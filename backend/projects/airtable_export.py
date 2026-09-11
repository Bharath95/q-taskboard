"""Airtable export service (Part 3c).

Pushes a project's tasks to the Airtable ``Tasks`` table via server-side
``batch_upsert`` keyed on ``Task ID``, so re-running never duplicates rows. The
service owns chunking (``BATCH_SIZE``) and retries (``MAX_ATTEMPTS``) so unit
tests see exact call counts; pyairtable's own retry is disabled in
``get_table``. No real network call is made in tests: an injected ``table`` (the
in-memory ``FakeAirtableTable``) and ``sleep`` recorder stand in.
"""

from dataclasses import dataclass, field

import time  # noqa: F401  (tests patch projects.airtable_export.time.sleep)

import requests

from django.conf import settings

from .models import Task

# How many records go in one batch_upsert call. We own chunking so a failure is
# isolated to at most this many records and call counts stay deterministic.
BATCH_SIZE = 10

# Total attempts (initial + retries) for a transient failure on one chunk.
MAX_ATTEMPTS = 3

# Base for exponential backoff between retries, in seconds.
BACKOFF_BASE_SECONDS = 0.5

KEY_FIELDS = ["Task ID"]

TRANSIENT_STATUSES = frozenset({429, 500, 502, 503, 504})
PERMANENT_STATUSES = frozenset({400, 404, 422})
AUTH_STATUSES = frozenset({401, 403})


class AirtableNotConfigured(Exception):
    """Raised when Airtable credentials/base are not configured."""


class AirtableAuthError(Exception):
    """Raised when Airtable rejects our credentials (401/403 from the API)."""


@dataclass
class ExportResult:
    created: int = 0
    updated: int = 0
    failed: list = field(default_factory=list)  # [{'taskId': str, 'reason': str}]

    @property
    def exported(self):
        return self.created + self.updated

    @property
    def total(self):
        return self.exported + len(self.failed)

    def as_dict(self):
        return {
            "exported": self.exported,
            "created": self.created,
            "updated": self.updated,
            "failed": list(self.failed),
            "total": self.total,
        }


def task_to_fields(task, project):
    return {
        "Task ID": str(task.id),
        "Title": task.title,
        "Description": task.description or "",
        "Status": task.status,
        "Assignee": task.assignee.email if task.assignee else "",
        "Project": project.name,
        "Project ID": str(project.id),
        "Position": task.position,
    }


def task_to_record(task, project):
    """batch_upsert wants {'fields': {...}} per record."""
    return {"fields": task_to_fields(task, project)}


def get_table():
    """Build a real pyairtable table client from Django settings.

    Raises ``AirtableNotConfigured`` when the API key or base id is empty.
    pyairtable's own retry is disabled so our service owns retries and unit-test
    call counts stay exact.
    """
    api_key = getattr(settings, "AIRTABLE_API_KEY", "") or ""
    base_id = getattr(settings, "AIRTABLE_BASE_ID", "") or ""
    table_name = getattr(settings, "AIRTABLE_TABLE_NAME", "") or "Tasks"

    if not api_key or not base_id:
        raise AirtableNotConfigured("airtable not configured")

    from pyairtable import Api

    api = Api(api_key, retry_strategy=False, timeout=(5, 30))
    return api.table(base_id, table_name)


def _classify(exc):
    """Return ('transient' | 'permanent' | 'auth', retry_after_seconds_or_None)."""
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return "transient", None
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        code = exc.response.status_code
        if code in AUTH_STATUSES:
            return "auth", None
        if code in TRANSIENT_STATUSES:
            retry_after = exc.response.headers.get("Retry-After") if code == 429 else None
            delay = float(retry_after) if retry_after and retry_after.isdigit() else None
            return "transient", delay
        return "permanent", None
    return "permanent", None


def _backoff(attempt):
    return BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)  # 0.5, 1.0, ...


def _reason(exc):
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return f"{exc.response.status_code} {exc}"[:300]
    return f"{type(exc).__name__}: {exc}"[:300]


def _call_with_retry(fn, sleep):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fn()
        except Exception as exc:
            kind, retry_after = _classify(exc)
            if kind == "auth":
                raise AirtableAuthError(_reason(exc)) from exc
            if kind == "permanent" or attempt == MAX_ATTEMPTS:
                raise
            sleep(retry_after if retry_after is not None else _backoff(attempt))


def _upsert(table, payloads, sleep):
    return _call_with_retry(
        lambda: table.batch_upsert(payloads, key_fields=KEY_FIELDS, typecast=True),
        sleep,
    )


def _add_counts(result, res):
    result.created += len(res["createdRecords"])
    result.updated += len(res["updatedRecords"])


def _add_failure(result, task, exc):
    result.failed.append({"taskId": str(task.id), "reason": _reason(exc)})


def _chunks(items, size=BATCH_SIZE):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def _upsert_chunk_with_fallback(table, chunk, result, sleep):
    """chunk: list of (task, payload), len <= BATCH_SIZE. Implements D10 and D13."""
    try:
        _add_counts(result, _upsert(table, [p for _, p in chunk], sleep))
        return
    except AirtableAuthError:
        raise  # abort the whole export
    except Exception as exc:
        kind, _ = _classify(exc)
        if kind == "transient" or len(chunk) == 1:
            # Retries exhausted (transient) or already isolated: report as-is.
            for task, _ in chunk:
                _add_failure(result, task, exc)
            return
    # Permanent error on a chunk of >1: isolate the bad record(s).
    for task, payload in chunk:
        try:
            _add_counts(result, _upsert(table, [payload], sleep))
        except AirtableAuthError:
            raise
        except Exception as exc:
            _add_failure(result, task, exc)


def export_project_tasks(project, table=None, sleep=None):
    """Export all of ``project``'s tasks to Airtable via ``batch_upsert``.

    When ``table`` is None a real client is built via ``get_table`` (raising
    ``AirtableNotConfigured`` before any DB work). ``sleep`` defaults to
    ``time.sleep`` and is injectable so backoff is asserted without real waiting.
    Raises ``AirtableNotConfigured`` or ``AirtableAuthError`` only.
    """
    if sleep is None:
        sleep = time.sleep
    if table is None:
        table = get_table()

    tasks = list(
        Task.objects.filter(project=project)
        .select_related("assignee")
        .order_by("created_at", "id")
    )
    result = ExportResult()
    records = [(t, task_to_record(t, project)) for t in tasks]
    for chunk in _chunks(records):
        _upsert_chunk_with_fallback(table, chunk, result, sleep)
    return result.as_dict()
