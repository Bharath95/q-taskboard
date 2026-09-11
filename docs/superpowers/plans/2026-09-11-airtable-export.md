# Airtable Export (Part 3c) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** DESIGN, revised 2026-09-11 to match the approved test plan `docs/3c-airtable-export-test-plan.md`, which is the source of truth for test names and behaviour. All decisions below are locked (server-side `batch_upsert` keyed on `Task ID`, service-level chunks of 10, synchronous, own retry loop, response shape, 503 on missing config, 502 on an Airtable auth error). IMPLEMENTED and green; the built code is the source of truth where it diverges from snippets below (the service returns a plain dict, the test double keys its in-memory store by Task ID, and the frontend test file is `frontend/src/tests/ExportButton.test.tsx`).

**Goal:** Let an admin or member push every task in a project to the Airtable `Tasks` table with one click, so that re-running never duplicates rows, one bad record never sinks the export, and the caller gets an honest per-record report.

**Architecture:** The existing stub `ExportView` (`POST /api/projects/<uuid:project_id>/export`) keeps its auth checks and delegates to a new pure service, `export_project_tasks(project, table=None, sleep=None)` in `backend/projects/airtable_export.py`. The service maps tasks to `{"fields": {...}}` records, splits them into chunks of `BATCH_SIZE = 10`, and for each chunk calls `table.batch_upsert(chunk, key_fields=["Task ID"], typecast=True)` inside a bounded retry loop. Airtable matches on `Task ID` server-side, so there is no read-then-write window and no record id to store. `created`/`updated` counts are accumulated from each call's `createdRecords`/`updatedRecords`. A chunk that fails with a per-record permanent error is re-sent one record at a time so only the genuinely bad ones land in `failed`; an Airtable auth error aborts the export with 502. A new in-memory `FakeAirtableTable` (`backend/projects/airtable_mock.py`) implements `batch_upsert` so unit tests never touch the network. The React project page gains an "Export to Airtable" button for admins/members that shows the counts.

**Tech Stack:** Django 5, Django REST Framework, `pyairtable` 2.3.x (installed 2.3.7, pinned `>=2.3,<3.0`; `batch_upsert` exists since 1.5), `requests` (transitive); React 18 + TypeScript + TanStack Query; pytest-django and Vitest + Testing Library for tests.

**Spec:** Part 3c requirements — bulk export of a project's tasks to Airtable via the existing endpoint; idempotent re-runs (no duplicate rows); partial-failure resilience with per-record error reporting; retry transient errors with backoff; authorization enforced server-side; a UI trigger. Test cases live in `docs/3c-airtable-export-test-plan.md`; this plan uses the same test names, response shape and behaviour so those tests pass.

## Global Constraints

- Roles are `admin | member | viewer`; "can export" = `admin` or `member` (reuse `_can_edit_tasks`). Non-members get 403, unauthenticated 401 (DRF default `IsAuthenticated` + SimpleJWT).
- Airtable config comes from env: `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME` (default `Tasks`). Never log or return the key. Never print `.env`.
- The real base (`TaskBoard`, base id in `AIRTABLE_BASE_ID`) has table `Tasks` with exactly these fields: `Title` (primary), `Task ID`, `Project`, `Project ID`, `Status` (single select: `todo`, `in_progress`, `review`, `done`), `Assignee`, `Description`, `Position`. Sending any other field name returns 422 `UNKNOWN_FIELD_NAME`, so the mapping sends only these eight.
- `Task ID` (the Task UUID as text) is the upsert key (`fieldsToMergeOn`). Task UUIDs are globally unique, so the match needs no project scoping. Nothing about Airtable is stored on the `Task` model. No migration in this part.
- Chunking is owned by the service: `BATCH_SIZE = 10`, one `batch_upsert` call per chunk. This isolates a failure to at most 10 records and makes call counts deterministic (1000 tasks = exactly 100 calls). pyairtable would also chunk at 10 internally, so each call is exactly one HTTP request. Airtable rejects a whole request when any record in it is invalid, so a failed chunk has written nothing.
- Airtable's rate limit is 5 requests/second per base; a synchronous export of ~1000 tasks is ~100 requests, ~20–30 s, and is accepted (no queue, no threads).
- Unit tests never touch the network: the service takes an injected `table` and an injected `sleep`; HTTP tests patch the table factory.
- Error bodies follow the repo convention `{"error": "<message>"}`.
- Tests are written first and must fail before implementation (red → green per task). Run backend tests with `docker compose exec -T backend python -m pytest ...`, frontend with `docker compose exec -T frontend npm test -- --run`.

---

## Design decisions

| # | Decision | Chosen | Alternative considered | Status |
|---|---|---|---|---|
| D1 | Response shape | `{exported, created, updated, failed: [{taskId, reason}], total}`. `exported = created + updated`, `total = exported + len(failed)` = number of tasks in the project. The stub's `tasks` list is dropped. | Keep `tasks` list. | Locked |
| D2 | Idempotency mechanism | Server-side upsert: `table.batch_upsert(chunk, key_fields=['Task ID'], typecast=True)` per chunk. Airtable matches existing rows on `Task ID` inside the request, so two concurrent exports cannot both "see no row yet" and create duplicates. `Task ID` is a globally unique UUID, so the match needs no project scoping. Counts come from `createdRecords` / `updatedRecords` in the return value. No `all()` lookup, no `airtable_record_id` column. | Manual lookup + split into create/update calls (TOCTOU race, extra requests); or a `Task.airtable_record_id` column (migration, goes stale). | Locked |
| D3 | Sync vs async | Synchronous; the request blocks until every chunk is done. | 202 + job id with Celery/thread. | Locked |
| D4 | Who retries | Our own loop (`MAX_ATTEMPTS = 3`, backoff 0.5 s → 1 s, honour `Retry-After` on 429). The real `Api` is built with `retry_strategy=False` so pyairtable's urllib3 retries do not hide calls from our tests. A retry re-sends the same chunk; that is duplicate-safe because the upsert keys on `Task ID`. | pyairtable's `retry_strategy`. | Locked |
| D5 | Partial-failure status | HTTP 200 with a non-empty `failed` list. Non-200 only for 401/403 (caller), 404 (project missing), 503 (not configured), and 502 (Airtable answered 401/403: bad credentials or no base access, so no work can proceed). There is no read-before-write step, so no other 5xx arises from the service. | 207 Multi-Status. | Locked |
| D6 | Field set | Send only the eight fields that exist in the base (see mapping). `Created By`, `Created At`, `Updated At` are not sent; the base has no such fields and they would 422 every record. | Add those fields to the base, then extend the mapping. | Locked |
| D7 | `Status` field | Send the raw value (`todo` …); the base's single-select choices match. `typecast=True` on the upsert so a renamed/added choice is created rather than rejected. | `typecast=False`; or send human labels. | Locked |
| D8 | Unconfigured Airtable | 503 `{"error": "airtable not configured"}` before any DB or network work. | 500. | Locked |
| D9 | Update strategy | Every task is included in every run; Airtable decides created vs updated. Unchanged tasks count as `updated`. | Skip unchanged tasks (needs an `Updated At` field in the base). | Locked |
| D10 | Fallback scope | Failure isolation is per chunk of 10. If a chunk fails with a **per-record permanent** error (400/404/422) after one attempt, the service re-sends **that chunk's records** one at a time (`batch_upsert([record], ...)`); only the bad ones land in `failed`. A chunk that exhausts **transient** retries is reported failed as a whole, with no single-record fallback (the problem is Airtable, not a record). A chunk of exactly one record skips the fallback (it is already isolated). Cost is bounded by 10 extra calls per bad chunk, only in the failure case. | Fallback over the whole export (N extra calls). | Locked |
| D11 | Tasks deleted locally | Out of scope to delete Airtable rows. A re-export after a local delete must succeed and leave the stale row untouched: the deleted task is simply absent from the upsert payload, so Airtable never sees it. Tested explicitly (C6). | Orphan-row cleanup step. | Locked |
| D12 | Empty assignee/description | Send `""` (clears a previously set value on update). | `None` or omit the key (omitting leaves stale values on update). | Locked |
| D13 | Airtable auth error | 401/403 **from Airtable** (as opposed to from our own auth) is never retried and is not a per-record problem. The service raises `AirtableAuthError`; the view returns 502 `{"error": "airtable authentication failed"}`. Chunks already applied before the error stay applied (harmless: the next run matches them on `Task ID`). | Report every task as `failed` with a 200. | Locked |

---

## Data model

No schema change. The service reads:

| Model | Fields used |
|---|---|
| `Project` | `id`, `name` |
| `Task` | `id`, `title`, `description`, `status`, `assignee` (→ `email`), `position` |

Tasks are loaded with `Task.objects.filter(project=project).select_related('assignee').order_by('created_at', 'id')` so the payload order, the chunk contents, and the `failed` order are deterministic.

### Field mapping (Task → Airtable `Tasks` row)

| Airtable field | Airtable type | Source | Notes |
|---|---|---|---|
| `Task ID` | single line text | `str(task.id)` | Upsert key (`key_fields`). Never changes for a task. |
| `Title` | single line text (primary) | `task.title` | |
| `Description` | long text | `task.description or ""` | |
| `Status` | single select | `task.status` | Raw value; `typecast=True` (D7). |
| `Assignee` | single line text | `task.assignee.email if task.assignee else ""` | Email, not a linked record or collaborator, so the base needs no user table. |
| `Project` | single line text | `project.name` | Human-readable. |
| `Project ID` | single line text | `str(project.id)` | Lets one base hold many projects. |
| `Position` | number | `task.position` | Integer. |

```python
# backend/projects/airtable_export.py
def task_to_fields(task, project) -> dict:
    return {
        'Task ID': str(task.id),
        'Title': task.title,
        'Description': task.description or '',
        'Status': task.status,
        'Assignee': task.assignee.email if task.assignee else '',
        'Project': project.name,
        'Project ID': str(project.id),
        'Position': task.position,
    }

def task_to_record(task, project) -> dict:
    """batch_upsert wants {'fields': {...}} per record."""
    return {'fields': task_to_fields(task, project)}
```

### Settings

```python
# backend/taskboard/settings.py (append)
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY', '')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', '')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'Tasks')
```

Tests override with pytest-django's `settings` fixture (`settings.AIRTABLE_API_KEY = ''`), which satisfies test B8 without touching the process environment.

---

## API contract

### `POST /api/projects/<uuid:project_id>/export`

Request: empty body, `Authorization: Bearer <token>`.

- 401 if unauthenticated (DRF default).
- 403 `{"error": "forbidden"}` if the caller has no membership on the project.
- 403 `{"error": "only admins and members can export"}` for viewers.
- 404 `{"error": "not found"}` if the project does not exist (membership already implies existence; kept for symmetry).
- 503 `{"error": "airtable not configured"}` if `AIRTABLE_API_KEY` or `AIRTABLE_BASE_ID` is blank. Checked before loading tasks; no Airtable call is made.
- 502 `{"error": "airtable authentication failed"}` if Airtable answers 401 or 403 to any `batch_upsert` (D13). No per-record report is returned.
- 200 otherwise, including partial or total per-record failure:

```json
{
  "exported": 12,
  "created": 9,
  "updated": 3,
  "failed": [
    { "taskId": "0f1c…", "reason": "422 Client Error: Unprocessable Entity … {'type': 'UNKNOWN_FIELD_NAME', …}" }
  ],
  "total": 13
}
```

`failed` is ordered by task order. `reason` is a short human-readable string (status code + message, truncated to 300 chars) and never contains the API key.

Authorization is server-side only. The frontend hides the button for viewers as a convenience; test A1 proves a forced request still gets 403.

### Service contract

```python
# backend/projects/airtable_export.py
BATCH_SIZE = 10             # records per batch_upsert call (== Airtable's per-request max)
MAX_ATTEMPTS = 3            # 1 initial + 2 retries, per batch_upsert call
BACKOFF_BASE_SECONDS = 0.5  # delays: 0.5, 1.0
KEY_FIELDS = ['Task ID']
TRANSIENT_STATUSES = frozenset({429, 500, 502, 503, 504})
PERMANENT_STATUSES = frozenset({400, 404, 422})   # per-record; anything else unknown is treated the same
AUTH_STATUSES = frozenset({401, 403})             # abort the export

class AirtableNotConfigured(Exception): ...
class AirtableAuthError(Exception): ...            # str(exc) is the reason, never the key

@dataclass
class ExportResult:
    created: int = 0
    updated: int = 0
    failed: list[dict] = field(default_factory=list)   # [{'taskId': str, 'reason': str}]

    @property
    def exported(self) -> int: return self.created + self.updated
    @property
    def total(self) -> int: return self.exported + len(self.failed)
    def as_dict(self) -> dict:
        return {'exported': self.exported, 'created': self.created, 'updated': self.updated,
                'failed': list(self.failed), 'total': self.total}

def get_table():
    """Factory for the real client. Patched in tests. Raises AirtableNotConfigured."""

def export_project_tasks(project, table=None, sleep=None) -> ExportResult:
    """table=None -> get_table(); sleep=None -> time.sleep (resolved at call time so tests can patch it).
    Raises AirtableNotConfigured or AirtableAuthError only."""
```

Client protocol: the service calls exactly **one** method on the table, satisfied by `pyairtable.Table` and `FakeAirtableTable`. Signature verified on installed pyairtable 2.3.7:

```python
def batch_upsert(
    self,
    records: Iterable[Dict[str, Any]],      # each {'fields': {...}} (or {'id': 'rec…', 'fields': {...}})
    key_fields: List[str],                  # fieldsToMergeOn, e.g. ['Task ID']
    replace: bool = False,
    typecast: bool = False,
    return_fields_by_field_id: bool = False,
) -> UpsertResultDict:                      # {'createdRecords': [rec ids], 'updatedRecords': [rec ids], 'records': [RecordDict]}
```

Behaviour of the real method that the design depends on (read from the installed source):
- Before any network call it raises `ValueError` if a record lacks a key field (cannot happen here; `Task ID` is always set).
- It sends `PATCH` requests with `performUpsert.fieldsToMergeOn = key_fields`, chunking at 10 internally. Because the service already sends ≤10 records per call, every call is exactly one HTTP request, and a raised exception means that request wrote nothing.

The service calls it exactly as: `table.batch_upsert(chunk, key_fields=KEY_FIELDS, typecast=True)`.

### Export algorithm (exact)

1. `table = table if table is not None else get_table()` — raises `AirtableNotConfigured` first, before any DB work.
2. Load tasks (ordered, `select_related('assignee')`). If empty, return `ExportResult()` without calling Airtable.
3. `records = [(task, task_to_record(task, project)) for task in tasks]`.
4. For each `chunk` of `BATCH_SIZE` records, in order: `_upsert_chunk_with_fallback(table, chunk, result, sleep)`. An `AirtableAuthError` propagates out immediately (D13).
5. Return `result`.

```python
def _chunks(items, size=BATCH_SIZE):
    for start in range(0, len(items), size):
        yield items[start:start + size]

def _upsert(table, payloads, sleep):
    return _call_with_retry(lambda: table.batch_upsert(payloads, key_fields=KEY_FIELDS, typecast=True), sleep)

def _add_counts(result, res):
    result.created += len(res['createdRecords'])
    result.updated += len(res['updatedRecords'])

def _add_failure(result, task, exc):
    result.failed.append({'taskId': str(task.id), 'reason': _reason(exc)})

def _upsert_chunk_with_fallback(table, chunk, result, sleep):
    """chunk: list of (task, payload), len <= BATCH_SIZE. Implements D10 and D13."""
    try:
        _add_counts(result, _upsert(table, [p for _, p in chunk], sleep))
        return
    except AirtableAuthError:
        raise                                            # abort the whole export
    except Exception as exc:
        kind, _ = _classify(exc)
        if kind == 'transient' or len(chunk) == 1:       # retries exhausted, or already isolated
            for task, _ in chunk:
                _add_failure(result, task, exc)
            return
    for task, payload in chunk:                          # permanent: isolate the bad record(s)
        try:
            _add_counts(result, _upsert(table, [payload], sleep))
        except AirtableAuthError:
            raise
        except Exception as exc:
            _add_failure(result, task, exc)

def export_project_tasks(project, table=None, sleep=None):
    sleep = sleep or time.sleep
    table = table if table is not None else get_table()
    tasks = list(Task.objects.filter(project=project).select_related('assignee').order_by('created_at', 'id'))
    result = ExportResult()
    for chunk in _chunks([(t, task_to_record(t, project)) for t in tasks]):
        _upsert_chunk_with_fallback(table, chunk, result, sleep)
    return result
```

Worked example, D2 in the test plan: 10 tasks, one poisoned with 422. `batch_upsert` is called once with 10 records (fails, nothing written), then 10 times with 1 record each; 9 succeed, 1 lands in `failed`. Total 11 calls, no sleeps.

Worked example, B7: 1000 tasks, all good: exactly 100 calls of 10 records; `created == 1000`.

Worked example, 23 tasks, poison in the third chunk: calls of 10, 10, 3 (fails), then 1, 1, 1. `created == 22`, `failed` has 1 entry, `exported == 22`, `total == 23`, no duplicates, no skew in the created/updated split.

Worked example, E3: 1 task, Airtable answers 503 forever: 3 calls (`MAX_ATTEMPTS`), 2 sleeps, the task lands in `failed` with a reason mentioning 503. No fallback because the failure is transient.

Worked example, D4: 12 tasks, the first call answers 401: 1 call, no sleeps, `AirtableAuthError` propagates, the view returns 502, nothing was written.

### Error classification and retry

```python
def _classify(exc) -> tuple[str, float | None]:
    """Returns ('transient' | 'permanent' | 'auth', retry_after_seconds_or_None)."""
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return 'transient', None
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        code = exc.response.status_code
        if code in AUTH_STATUSES:
            return 'auth', None
        if code in TRANSIENT_STATUSES:
            retry_after = exc.response.headers.get('Retry-After') if code == 429 else None
            return 'transient', (float(retry_after) if retry_after and retry_after.isdigit() else None)
        return 'permanent', None          # 400/404/422 and any other status
    return 'permanent', None              # unknown exception types (incl. ValueError) are not retried

def _backoff(attempt) -> float:
    return BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)     # 0.5, 1.0, ...

def _call_with_retry(fn, sleep):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fn()
        except Exception as exc:
            kind, retry_after = _classify(exc)
            if kind == 'auth':
                raise AirtableAuthError(_reason(exc)) from exc
            if kind == 'permanent' or attempt == MAX_ATTEMPTS:
                raise
            sleep(retry_after if retry_after is not None else _backoff(attempt))

def _reason(exc) -> str:
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return f'{exc.response.status_code} {exc}'[:300]
    return f'{type(exc).__name__}: {exc}'[:300]
```

How pyairtable errors reach this code: `pyairtable` 2.3.x calls `response.raise_for_status()` in `Api._process_response` and re-raises the same `requests.HTTPError` with Airtable's `error` JSON appended to `exc.args`, so `exc.response.status_code` and `.headers` are available. Network failures surface as `requests.ConnectionError` / `requests.Timeout`. No pyairtable-specific exception class needs importing. The fake raises the same types.

Behaviour matrix (matches test groups D and E; "calls" = `batch_upsert` calls for one chunk):

| Failure | Calls | Sleeps | Outcome |
|---|---|---|---|
| 429 then OK | 2 | 1 (`Retry-After` if present, else 0.5) | success |
| 500/502/503/504 then OK | 2 | 1 (0.5) | success |
| `requests.Timeout` / `requests.ConnectionError` then OK | 2 | 1 (0.5) | success; the re-sent chunk is matched on `Task ID`, no duplicates |
| 503 forever | `MAX_ATTEMPTS` = 3 | 2 (0.5, 1.0) | every record of the chunk in `failed`, reason mentions 503; **no** single-record fallback |
| 400/404/422, chunk of 1 | 1 | 0 | the record in `failed` (no fallback needed) |
| 400/404/422, chunk of k > 1 | 1 + k | 0 | bad record(s) in `failed`, the rest exported |
| 401/403 from Airtable | 1 | 0 | `AirtableAuthError` → HTTP 502, export aborted |

### Real client

```python
# backend/projects/airtable_export.py
from django.conf import settings
from pyairtable import Api

def get_table():
    key, base, name = settings.AIRTABLE_API_KEY, settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_NAME
    if not key or not base:
        raise AirtableNotConfigured()
    api = Api(key, retry_strategy=False, timeout=(5, 30))   # we own retries (D4)
    return api.table(base, name)
```

`pyairtable.Table` already exposes `batch_upsert` with the signature above, so no wrapper class is needed; "thin client" = this factory plus the one-method protocol.

### Test double

```python
# backend/projects/airtable_mock.py  (new file; test-only, never imported by production code)
import itertools


class FakeAirtableTable:
    """In-memory stand-in for pyairtable.Table, exposing only batch_upsert.

    Matches on key_fields like Airtable, updates matches, creates the rest, and returns
    createdRecords/updatedRecords/records. A scripted failure raises before anything in that
    call is applied (Airtable rejects a whole request). It does NOT enforce a batch size: the
    service is responsible for sending <= 10 records per call and B7 asserts that.
    """

    def __init__(self, rows=None):
        self.rows = {}                 # rec id -> fields dict (insertion ordered)
        self.calls = []                # one entry per batch_upsert call: list of records passed
        self._ids = itertools.count(1)
        self._fail_next = []           # exceptions raised on the next N calls
        self._fail_for_task = {}       # Task ID -> exception raised when a call contains it
        for fields in rows or []:
            self._insert(fields)

    # -- scripting -------------------------------------------------------
    def fail_next(self, n, exc):
        """Raise exc on the next n calls, then behave normally."""
        self._fail_next.extend([exc] * n)

    def fail_for_task_id(self, task_id, exc):
        """Raise exc whenever a call's records include this Task ID."""
        self._fail_for_task[task_id] = exc

    def clear_failures(self):
        """Forget every scripted failure (used by C5 to let a record recover)."""
        self._fail_next.clear()
        self._fail_for_task.clear()

    # -- protocol ---------------------------------------------------------
    def batch_upsert(self, records, key_fields, replace=False, typecast=False, return_fields_by_field_id=False):
        records = list(records)
        self.calls.append(records)
        for record in records:                       # same pre-check as pyairtable
            missing = set(key_fields) - set(record.get('fields', {}))
            if 'id' not in record and missing:
                raise ValueError(f'missing key fields {missing!r}')
        self._maybe_fail(records)                    # whole call fails, nothing applied
        result = {'createdRecords': [], 'updatedRecords': [], 'records': []}
        for record in records:
            rid = record.get('id') or self._match(record['fields'], key_fields)
            if rid is None:
                rid = self._insert(record['fields'])
                result['createdRecords'].append(rid)
            else:
                if replace:
                    self.rows[rid] = dict(record['fields'])
                else:
                    self.rows[rid].update(record['fields'])
                result['updatedRecords'].append(rid)
            result['records'].append(self._record_dict(rid))
        return result

    # -- helpers -----------------------------------------------------------
    def _match(self, fields, key_fields):
        for rid, stored in self.rows.items():
            if all(stored.get(k) == fields.get(k) for k in key_fields):
                return rid
        return None

    def _insert(self, fields):
        rid = f'rec{next(self._ids):014d}'
        self.rows[rid] = dict(fields)
        return rid

    def _record_dict(self, rid):
        return {'id': rid, 'createdTime': '2026-09-11T00:00:00.000Z', 'fields': dict(self.rows[rid])}

    def _maybe_fail(self, records):
        if self._fail_next:
            raise self._fail_next.pop(0)
        for record in records:
            exc = self._fail_for_task.get(record.get('fields', {}).get('Task ID'))
            if exc:
                raise exc

    def task_ids(self):
        return [f.get('Task ID') for f in self.rows.values()]


def http_error(status, message='', headers=None):
    """Build the requests.HTTPError pyairtable raises, with .response.status_code and headers."""
    import requests
    response = requests.Response()
    response.status_code = status
    response.headers.update(headers or {})
    response._content = message.encode() or b'{"error": {"type": "TEST", "message": "scripted failure"}}'
    return requests.HTTPError(f'{status} Error: scripted', response=response)
```

One observability channel: `fake.calls` (how many times the service called `batch_upsert` and with how many records each time). Chunking, retry and fallback tests all assert on `calls`; state tests assert on `rows` / `task_ids()`.

---

## File Structure

- Create `backend/projects/airtable_mock.py` — `FakeAirtableTable`, `http_error` helper (test double).
- Create `backend/projects/test_airtable_mock.py` — sanity tests for the double.
- Create `backend/projects/airtable_export.py` — constants, `AirtableNotConfigured`, `AirtableAuthError`, `ExportResult`, `task_to_fields`, `task_to_record`, `get_table`, `_chunks`, `_classify`, `_backoff`, `_call_with_retry`, `_reason`, `_upsert`, `_upsert_chunk_with_fallback`, `export_project_tasks`.
- Create `backend/projects/test_export.py` — service + HTTP tests (groups A–E of the test plan).
- Modify `backend/taskboard/settings.py` — three `AIRTABLE_*` settings.
- Modify `backend/projects/views.py` — `ExportView.post` delegates to the service and maps `AirtableNotConfigured` to 503 and `AirtableAuthError` to 502.
- Modify `frontend/src/types/index.ts` — `ApiExportResult`.
- Modify `frontend/src/pages/ProjectPage.tsx` — `canExport`, export mutation, button, result line.
- Create `frontend/src/tests/ProjectPage.test.tsx` — F1–F4.
- Modify `README.md` — one paragraph on the export behaviour and the manual verification; `CLAUDE.md` already carries the gotchas (field set, `retry_strategy=False`, chunking, 502).

---

### Task 1: `FakeAirtableTable` test double

**Files:**
- Create: `backend/projects/airtable_mock.py`
- Create: `backend/projects/test_airtable_mock.py`

**Interfaces:**
- Produces: `FakeAirtableTable(rows=None)` with `batch_upsert(records, key_fields, replace=False, typecast=False, return_fields_by_field_id=False)`, `calls`, `rows`, `task_ids()`, `fail_next(n, exc)`, `fail_for_task_id(task_id, exc)`, `clear_failures()`; module helper `http_error(status, message='', headers=None)`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/projects/test_airtable_mock.py
import pytest
import requests
from projects.airtable_mock import FakeAirtableTable, http_error


def rec(task_id, **fields):
    return {'fields': {'Task ID': task_id, **fields}}


def test_upsert_creates_then_updates_on_key_match():
    fake = FakeAirtableTable()
    first = fake.batch_upsert([rec('t1', Title='A')], key_fields=['Task ID'], typecast=True)
    second = fake.batch_upsert([rec('t1', Title='B')], key_fields=['Task ID'], typecast=True)
    assert len(first['createdRecords']) == 1 and first['updatedRecords'] == []
    assert second['createdRecords'] == [] and second['updatedRecords'] == first['createdRecords']
    assert len(fake.rows) == 1 and next(iter(fake.rows.values()))['Title'] == 'B'
    assert len(fake.calls) == 2 and fake.calls[1] == [rec('t1', Title='B')]


def test_result_records_carry_ids_and_fields():
    fake = FakeAirtableTable()
    res = fake.batch_upsert([rec('t1', Title='A')], key_fields=['Task ID'])
    assert res['records'][0]['id'] == res['createdRecords'][0]
    assert res['records'][0]['fields'] == {'Task ID': 't1', 'Title': 'A'}


def test_does_not_enforce_batch_size():
    fake = FakeAirtableTable()
    res = fake.batch_upsert([rec(str(i)) for i in range(23)], key_fields=['Task ID'])
    assert len(res['createdRecords']) == 23 and len(fake.calls) == 1


def test_missing_key_field_raises_value_error_before_applying():
    fake = FakeAirtableTable()
    with pytest.raises(ValueError):
        fake.batch_upsert([{'fields': {'Title': 'no key'}}], key_fields=['Task ID'])
    assert fake.rows == {}


def test_fail_next_raises_on_next_calls_without_applying_then_recovers():
    fake = FakeAirtableTable()
    fake.fail_next(2, http_error(503))
    for _ in range(2):
        with pytest.raises(requests.HTTPError) as info:
            fake.batch_upsert([rec('x')], key_fields=['Task ID'])
        assert info.value.response.status_code == 503
    assert fake.rows == {}
    fake.batch_upsert([rec('x')], key_fields=['Task ID'])
    assert len(fake.calls) == 3 and len(fake.rows) == 1


def test_fail_for_task_id_rejects_whole_call_until_cleared():
    fake = FakeAirtableTable()
    fake.fail_for_task_id('bad', http_error(422))
    with pytest.raises(requests.HTTPError):
        fake.batch_upsert([rec('good'), rec('bad')], key_fields=['Task ID'])
    assert fake.rows == {}                                  # nothing in that call was applied
    fake.batch_upsert([rec('good')], key_fields=['Task ID'])
    assert fake.task_ids() == ['good']
    fake.clear_failures()
    fake.batch_upsert([rec('bad')], key_fields=['Task ID'])
    assert sorted(fake.task_ids()) == ['bad', 'good']


def test_preloaded_rows_are_matched_not_duplicated():
    fake = FakeAirtableTable(rows=[{'Task ID': 'pre', 'Title': 'keep'}])
    res = fake.batch_upsert([rec('pre', Title='new')], key_fields=['Task ID'])
    assert res['createdRecords'] == [] and len(res['updatedRecords']) == 1 and len(fake.rows) == 1


def test_http_error_exposes_status_and_headers():
    exc = http_error(429, headers={'Retry-After': '3'})
    assert exc.response.status_code == 429 and exc.response.headers['Retry-After'] == '3'
```

- [ ] **Step 2: Run to verify it fails**

Run: `docker compose exec -T backend python -m pytest projects/test_airtable_mock.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'projects.airtable_mock'`.

- [ ] **Step 3: Implement the double** — the `FakeAirtableTable` and `http_error` code from the "Test double" section above, verbatim.

- [ ] **Step 4: Run to verify it passes**

Run: `docker compose exec -T backend python -m pytest projects/test_airtable_mock.py -v`
Expected: 8 PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/projects/airtable_mock.py backend/projects/test_airtable_mock.py
git commit -m "test: add FakeAirtableTable double implementing pyairtable batch_upsert"
```

---

### Task 2: Service skeleton — mapping, config check, chunked `batch_upsert`, counts from the result

**Files:**
- Create: `backend/projects/airtable_export.py`
- Create: `backend/projects/test_export.py` (service-level portion)
- Modify: `backend/taskboard/settings.py`

**Interfaces:**
- Consumes: `Task`, `Project`; `FakeAirtableTable` (Task 1).
- Produces: `task_to_fields`, `task_to_record`, `ExportResult`, `AirtableNotConfigured`, `get_table()`, `_chunks`, `export_project_tasks(project, table=None, sleep=None)` (happy path only; retries in Task 4, fallback in Task 5). Constants `BATCH_SIZE`, `KEY_FIELDS`, `MAX_ATTEMPTS`, `BACKOFF_BASE_SECONDS`.

- [ ] **Step 1: Write the failing tests** (B1–B3, B5–B7 at the service level, plus the config check; B4 and B8 are asserted over HTTP in Task 6)

```python
# backend/projects/test_export.py
import pytest
from users.models import User
from projects.models import Project, Membership, Task
from projects.airtable_mock import FakeAirtableTable, http_error
from projects import airtable_export
from projects.airtable_export import export_project_tasks, AirtableNotConfigured, KEY_FIELDS, BATCH_SIZE


@pytest.fixture
def owner(db):
    return User.objects.create_user(email='owner@taskboard.dev', name='Olive Owner', password='password123')

@pytest.fixture
def project(owner):
    p = Project.objects.create(name='Export Project', owner=owner)
    Membership.objects.create(user=owner, project=p, role='admin')
    return p

def make_tasks(project, owner, n, **kw):
    return [Task.objects.create(project=project, title=f'Task {i}', created_by=owner, position=i, **kw) for i in range(n)]

def no_sleep(_seconds):
    pass


@pytest.mark.django_db
class TestServiceHappyPath:
    def test_exports_all_tasks_in_project(self, project, owner):                       # B1
        tasks = make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert (result.created, result.updated, result.exported, result.total) == (3, 0, 3, 3)
        assert set(fake.task_ids()) == {str(t.id) for t in tasks}

    def test_upsert_is_keyed_on_task_id_with_typecast(self, project, owner):
        make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        assert len(fake.calls) == 1 and len(fake.calls[0]) == 3
        assert KEY_FIELDS == ['Task ID'] and BATCH_SIZE == 10

    def test_field_mapping(self, project, owner):                                       # B2
        t = Task.objects.create(project=project, title='Map me', description='desc', status='review',
                                assignee=owner, created_by=owner, position=7)
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        assert fake.calls[0][0] == {'fields': {
            'Task ID': str(t.id), 'Title': 'Map me', 'Description': 'desc', 'Status': 'review',
            'Assignee': 'owner@taskboard.dev', 'Project': 'Export Project',
            'Project ID': str(project.id), 'Position': 7,
        }}
        assert next(iter(fake.rows.values())) == fake.calls[0][0]['fields']

    def test_unassigned_task_maps_assignee_empty(self, project, owner):                 # B3
        make_tasks(project, owner, 1)
        fake = FakeAirtableTable()
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert result.failed == [] and fake.calls[0][0]['fields']['Assignee'] == ''

    def test_empty_project_exports_zero(self, project):                                 # B5
        fake = FakeAirtableTable()
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert result.as_dict() == {'exported': 0, 'created': 0, 'updated': 0, 'failed': [], 'total': 0}
        assert fake.calls == []

    def test_only_this_projects_tasks_exported(self, project, owner):                   # B6
        other = Project.objects.create(name='Other', owner=owner)
        make_tasks(project, owner, 2)
        foreign = make_tasks(other, owner, 2)
        fake = FakeAirtableTable(rows=[{'Task ID': str(foreign[0].id), 'Project ID': str(other.id), 'Title': 'keep'}])
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        upserted = {r['fields']['Task ID'] for call in fake.calls for r in call}
        assert upserted == {str(t.id) for t in Task.objects.filter(project=project)}
        assert all(r['fields']['Project ID'] == str(project.id) for call in fake.calls for r in call)
        assert result.created == 2 and len(fake.rows) == 3
        assert [r for r in fake.rows.values() if r['Task ID'] == str(foreign[0].id)][0]['Title'] == 'keep'

    def test_large_export_batches_not_per_task(self, project, owner):                   # B7
        Task.objects.bulk_create([Task(project=project, title=f'T{i}', created_by=owner, position=i) for i in range(1000)])
        fake = FakeAirtableTable()
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert len(fake.calls) == 100                              # chunks of BATCH_SIZE, not per task
        assert all(len(c) <= BATCH_SIZE for c in fake.calls)
        assert result.exported == 1000 and len(fake.rows) == 1000

    def test_chunk_boundaries_are_exact(self, project, owner):
        make_tasks(project, owner, 23)
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        assert [len(c) for c in fake.calls] == [10, 10, 3]

    def test_missing_config_raises(self, project, settings):
        settings.AIRTABLE_API_KEY = ''
        with pytest.raises(AirtableNotConfigured):
            export_project_tasks(project)          # table=None -> get_table() -> config check
```

- [ ] **Step 2: Run to verify it fails**

Run: `docker compose exec -T backend python -m pytest projects/test_export.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'projects.airtable_export'`.

- [ ] **Step 3: Add settings and implement the service skeleton**

Append the three `AIRTABLE_*` settings to `backend/taskboard/settings.py` (see Data model). Then create `airtable_export.py` with the constants, `AirtableNotConfigured`, `ExportResult`, `task_to_fields`, `task_to_record`, `get_table`, `_chunks`, and this first version of the pipeline (no retry, no fallback yet):

```python
import time
from dataclasses import dataclass, field
from .models import Task

def export_project_tasks(project, table=None, sleep=None):
    sleep = sleep or time.sleep
    table = table if table is not None else get_table()
    tasks = list(Task.objects.filter(project=project).select_related('assignee').order_by('created_at', 'id'))
    result = ExportResult()
    for chunk in _chunks([task_to_record(t, project) for t in tasks]):
        res = table.batch_upsert(chunk, key_fields=KEY_FIELDS, typecast=True)
        result.created += len(res['createdRecords'])
        result.updated += len(res['updatedRecords'])
    return result
```

- [ ] **Step 4: Run to verify it passes**

Run: `docker compose exec -T backend python -m pytest projects/test_export.py projects/test_airtable_mock.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/projects/airtable_export.py backend/projects/test_export.py backend/taskboard/settings.py
git commit -m "feat: Airtable export service upserting tasks in chunks of 10 keyed on Task ID"
```

---

### Task 3: Idempotency via `batch_upsert` — re-run, update, mixed, stale-row guards

**Files:**
- Modify: `backend/projects/test_export.py`

**Interfaces:**
- No new production code expected. These tests pin the behaviour the upsert design promises (C1–C4, C6 and D11) so a future refactor to a different mechanism cannot silently regress them. C5 needs the failure path and lives in Task 5.

- [ ] **Step 1: Write the tests**

```python
@pytest.mark.django_db
class TestIdempotency:
    def test_second_run_does_not_duplicate(self, project, owner):                       # C1
        make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        export_project_tasks(project, table=fake, sleep=no_sleep)
        assert len(fake.rows) == 3 and len(set(fake.task_ids())) == 3

    def test_second_run_reports_updated_not_created(self, project, owner):              # C2
        make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        first = export_project_tasks(project, table=fake, sleep=no_sleep)
        second = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert (first.created, first.updated) == (3, 0)
        assert (second.created, second.updated, second.exported) == (0, 3, 3)

    def test_changed_task_updates_same_row(self, project, owner):                       # C3
        t = make_tasks(project, owner, 1)[0]
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        rid = next(iter(fake.rows))
        t.title, t.status = 'Renamed', 'done'; t.save()
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert result.updated >= 1 and list(fake.rows) == [rid]
        assert fake.rows[rid]['Title'] == 'Renamed' and fake.rows[rid]['Status'] == 'done'

    def test_mixed_create_and_update(self, project, owner):                             # C4
        make_tasks(project, owner, 2)
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        make_tasks(project, owner, 1)
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert (result.created, result.updated) == (1, 2) and len(fake.rows) == 3

    def test_reexport_after_local_delete(self, project, owner):                         # C6
        tasks = make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        tasks[0].delete()
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert result.as_dict() == {'exported': 2, 'created': 0, 'updated': 2, 'failed': [], 'total': 2}
        assert {r['fields']['Task ID'] for r in fake.calls[-1]} == {str(t.id) for t in tasks[1:]}
        assert len(fake.rows) == 3 and str(tasks[0].id) in fake.task_ids()   # stale row untouched (D11)
```

- [ ] **Step 2: Run**

Run: `docker compose exec -T backend python -m pytest projects/test_export.py -k Idempotency -v`
Expected: all PASS with no production change (the upsert gives idempotency for free). If any fails, the Task 2 implementation is wrong; fix it before continuing.

- [ ] **Step 3: Commit**

```bash
git add backend/projects/test_export.py
git commit -m "test: pin idempotent re-export and stale-row behaviour of Airtable batch_upsert export"
```

---

### Task 4: Error classification, bounded retry with backoff, auth abort

**Files:**
- Modify: `backend/projects/airtable_export.py`
- Modify: `backend/projects/test_export.py`

**Interfaces:**
- Produces: `AirtableAuthError`, `_classify(exc)`, `_backoff(attempt)`, `_call_with_retry(fn, sleep)`, `_reason(exc)`, `_upsert(table, payloads, sleep)`; constants `TRANSIENT_STATUSES`, `PERMANENT_STATUSES`, `AUTH_STATUSES`. Every `batch_upsert` call goes through `_call_with_retry`. Until Task 5, a chunk that still fails after the policy marks every task in it as failed (no single-record fallback yet); an auth error propagates as `AirtableAuthError`.

- [ ] **Step 1: Write the failing tests** (E1–E6 plus the service-level half of D4)

```python
import requests
from projects.airtable_export import MAX_ATTEMPTS, BACKOFF_BASE_SECONDS, AirtableAuthError


class SleepRecorder:
    def __init__(self): self.calls = []
    def __call__(self, seconds): self.calls.append(seconds)


TRANSIENT = [http_error(429), http_error(500), http_error(502), http_error(503), http_error(504),
             requests.Timeout('slow'), requests.ConnectionError('down')]


@pytest.mark.django_db
class TestRetry:
    @pytest.mark.parametrize('exc', TRANSIENT, ids=lambda e: getattr(getattr(e, 'response', None), 'status_code', type(e).__name__))
    def test_transient_is_retried_then_succeeds(self, project, owner, exc):             # E1
        make_tasks(project, owner, 2)
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_next(1, exc)
        result = export_project_tasks(project, table=fake, sleep=sleep)
        assert len(fake.calls) == 2 and len(sleep.calls) == 1
        assert result.exported == 2 and result.failed == []
        assert len(fake.rows) == 2 and len(set(fake.task_ids())) == 2      # re-sent chunk matched on Task ID

    @pytest.mark.parametrize('status', [400, 404, 422])
    def test_permanent_is_not_retried_and_reported(self, project, owner, status):       # E2
        t = make_tasks(project, owner, 1)[0]
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_for_task_id(str(t.id), http_error(status))
        result = export_project_tasks(project, table=fake, sleep=sleep)
        assert len(fake.calls) == 1 and sleep.calls == []                  # exactly one call for that record
        assert result.failed[0]['taskId'] == str(t.id) and str(status) in result.failed[0]['reason']

    def test_retries_are_bounded(self, project, owner):                                 # E3
        t = make_tasks(project, owner, 1)[0]
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_next(99, http_error(503))                              # every attempt fails
        result = export_project_tasks(project, table=fake, sleep=sleep)
        assert len(fake.calls) == MAX_ATTEMPTS                             # no fallback for transient exhaustion
        assert len(sleep.calls) == MAX_ATTEMPTS - 1
        assert result.failed[0]['taskId'] == str(t.id) and '503' in result.failed[0]['reason']
        assert result.exported == 0 and result.total == 1

    def test_backoff_delays_grow(self, project, owner):                                 # E4
        make_tasks(project, owner, 1)
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_next(2, http_error(503))
        export_project_tasks(project, table=fake, sleep=sleep)
        assert sleep.calls == [airtable_export._backoff(1), airtable_export._backoff(2)]
        assert sleep.calls == [BACKOFF_BASE_SECONDS, BACKOFF_BASE_SECONDS * 2]

    def test_429_honours_retry_after(self, project, owner):                             # E5
        make_tasks(project, owner, 1)
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_next(1, http_error(429, headers={'Retry-After': '3'}))
        export_project_tasks(project, table=fake, sleep=sleep)
        assert sleep.calls == [3.0]

    def test_429_without_retry_after_uses_backoff(self, project, owner):                # E6
        make_tasks(project, owner, 1)
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_next(1, http_error(429))
        export_project_tasks(project, table=fake, sleep=sleep)
        assert sleep.calls == [airtable_export._backoff(1)] and sleep.calls[0] > 0

    @pytest.mark.parametrize('status', [401, 403])
    def test_auth_error_aborts_without_retry(self, project, owner, status):             # D4, service half
        make_tasks(project, owner, 12)                                     # two chunks
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_next(1, http_error(status))
        with pytest.raises(AirtableAuthError) as info:
            export_project_tasks(project, table=fake, sleep=sleep)
        assert len(fake.calls) == 1 and sleep.calls == [] and fake.rows == {}
        assert str(status) in str(info.value)
```

- [ ] **Step 2: Run to verify it fails**

Run: `docker compose exec -T backend python -m pytest projects/test_export.py -k "Retry" -v`
Expected: FAIL — `ImportError` for `MAX_ATTEMPTS` / `AirtableAuthError` until they exist; then transient tests raise `requests.HTTPError` out of the service.

- [ ] **Step 3: Implement classification and retry** — `AirtableAuthError`, `_classify`, `_backoff`, `_call_with_retry`, `_reason`, `_upsert` from the "Error classification and retry" section. In `export_project_tasks`, call `_upsert(table, chunk_payloads, sleep)` per chunk inside `try/except AirtableAuthError: raise` / `except Exception as exc:` and, for now, append `{'taskId', 'reason'}` for every task in the chunk when it fails.

- [ ] **Step 4: Run to verify it passes**

Run: `docker compose exec -T backend python -m pytest projects/ -v`
Expected: all PASS. Sanity: `grep -n 'retry_strategy=False' backend/projects/airtable_export.py` returns the `get_table` line.

- [ ] **Step 5: Commit**

```bash
git add backend/projects/airtable_export.py backend/projects/test_export.py
git commit -m "feat: classify Airtable errors, retry transient ones with bounded backoff, abort on auth errors"
```

---

### Task 5: Partial-failure resilience — single-record fallback for a permanently failed chunk

**Files:**
- Modify: `backend/projects/airtable_export.py`
- Modify: `backend/projects/test_export.py`

**Interfaces:**
- Produces: `_upsert_chunk_with_fallback(table, chunk, result, sleep)` implementing D10 and D13; `export_project_tasks` calls it per chunk.

- [ ] **Step 1: Write the failing tests** (D1–D3 at the service level, plus C5)

```python
@pytest.mark.django_db
class TestPartialFailure:
    def test_single_permanent_failure_does_not_abort(self, project, owner):             # D1
        tasks = make_tasks(project, owner, 5)
        fake = FakeAirtableTable()
        fake.fail_for_task_id(str(tasks[2].id), http_error(422))
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert result.exported == 4 and len(fake.rows) == 4 and result.total == 5
        assert [f['taskId'] for f in result.failed] == [str(tasks[2].id)]
        assert '422' in result.failed[0]['reason']

    def test_failed_chunk_falls_back_to_single_records(self, project, owner):           # D2
        tasks = make_tasks(project, owner, 10)
        fake = FakeAirtableTable()
        fake.fail_for_task_id(str(tasks[4].id), http_error(422))
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert [len(c) for c in fake.calls] == [10] + [1] * 10             # chunk fails, then 10 singles
        assert result.created == 9 and len(result.failed) == 1

    def test_fallback_is_scoped_to_the_failed_chunk(self, project, owner):
        tasks = make_tasks(project, owner, 23)
        fake = FakeAirtableTable()
        fake.fail_for_task_id(str(tasks[22].id), http_error(422))        # third chunk (3 records) fails
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert [len(c) for c in fake.calls] == [10, 10, 3, 1, 1, 1]
        assert len(fake.rows) == 22 and len(set(fake.task_ids())) == 22
        assert (result.created, result.updated, result.exported, result.total) == (22, 0, 22, 23)
        assert result.failed[0]['taskId'] == str(tasks[22].id)

    def test_failure_on_update_path_reported(self, project, owner):
        tasks = make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        export_project_tasks(project, table=fake, sleep=no_sleep)
        fake.fail_for_task_id(str(tasks[0].id), http_error(422))
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert result.updated == 2 and result.failed[0]['taskId'] == str(tasks[0].id)

    def test_all_records_fail_still_returns_report(self, project, owner):               # D3, service half
        tasks = make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        for t in tasks:
            fake.fail_for_task_id(str(t.id), http_error(422))
        result = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert result.exported == 0 and len(result.failed) == 3 and result.total == 3
        assert all(f['reason'] for f in result.failed)

    def test_transient_exhaustion_reports_whole_chunk_without_fallback(self, project, owner):
        make_tasks(project, owner, 4)
        fake, sleep = FakeAirtableTable(), SleepRecorder()
        fake.fail_next(99, http_error(503))
        result = export_project_tasks(project, table=fake, sleep=sleep)
        assert [len(c) for c in fake.calls] == [4] * MAX_ATTEMPTS           # no single-record calls
        assert len(result.failed) == 4 and result.exported == 0

    def test_auth_error_during_fallback_still_aborts(self, project, owner):
        tasks = make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        fake.fail_for_task_id(str(tasks[1].id), http_error(422))         # chunk fails permanently (checked first)
        fake.fail_for_task_id(str(tasks[2].id), http_error(401))         # ... then the third single call is 401
        with pytest.raises(AirtableAuthError):
            export_project_tasks(project, table=fake, sleep=no_sleep)
        assert [len(c) for c in fake.calls] == [3, 1, 1, 1]

    def test_failed_record_recovers_on_next_run(self, project, owner):                  # C5
        tasks = make_tasks(project, owner, 3)
        fake = FakeAirtableTable()
        fake.fail_for_task_id(str(tasks[2].id), http_error(422))
        first = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert [f['taskId'] for f in first.failed] == [str(tasks[2].id)] and len(fake.rows) == 2
        fake.clear_failures()
        second = export_project_tasks(project, table=fake, sleep=no_sleep)
        assert second.failed == [] and (second.created, second.updated) == (1, 2)
        assert str(tasks[2].id) in fake.task_ids() and len(fake.rows) == 3
```

- [ ] **Step 2: Run to verify it fails**

Run: `docker compose exec -T backend python -m pytest projects/test_export.py -k "PartialFailure" -v`
Expected: FAIL — D1 reports 5 failures and `exported == 0`; D2 shows `calls == [10]`; C5's first run has 3 failures and 0 rows.

- [ ] **Step 3: Implement `_upsert_chunk_with_fallback`** from the "Export algorithm" section and call it from `export_project_tasks` for each chunk.

- [ ] **Step 4: Run to verify it passes**

Run: `docker compose exec -T backend python -m pytest projects/ -v`
Expected: all export, mock, and comment tests PASS. `TestRetry` must pass unchanged (E2 stays at one call because a chunk of one skips the fallback; E3 stays at `MAX_ATTEMPTS` because transient exhaustion has no fallback).

- [ ] **Step 5: Commit**

```bash
git add backend/projects/airtable_export.py backend/projects/test_export.py
git commit -m "feat: isolate bad records with single-record upsert fallback per failed chunk"
```

---

### Task 6: Wire `ExportView` — response shape, 503/502 mapping, HTTP tests

**Files:**
- Modify: `backend/projects/views.py`
- Modify: `backend/projects/test_export.py` (HTTP portion)

**Interfaces:**
- Consumes: `export_project_tasks`, `AirtableNotConfigured`, `AirtableAuthError`, `_get_membership`, `_can_edit_tasks`.
- Produces: `ExportView.post` returning `result.as_dict()` (200), 503 `airtable not configured`, or 502 `airtable authentication failed`. The `tasks` list is removed from the response (D1).

- [ ] **Step 1: Write the failing tests** (A1, A2, B4, B8, D3 and D4 over HTTP, response-shape guard)

```python
from rest_framework.test import APIClient
from projects.test_comments import authed_client, member_client, make_user   # reuse helpers


@pytest.fixture
def fake_airtable(monkeypatch):
    fake = FakeAirtableTable()
    monkeypatch.setattr(airtable_export, 'get_table', lambda: fake)
    monkeypatch.setattr(airtable_export.time, 'sleep', no_sleep)   # service resolves time.sleep lazily
    return fake

def export_url(project_id):
    return f'/api/projects/{project_id}/export'


@pytest.mark.django_db
class TestExportEndpoint:
    @pytest.mark.parametrize('role,expected', [('admin', 200), ('member', 200), ('viewer', 403), ('non_member', 403)])
    def test_export_role_gate(self, project, owner, fake_airtable, role, expected):     # A1
        make_tasks(project, owner, 1)
        if role == 'non_member':
            client = authed_client(make_user('stranger@taskboard.dev'))
        else:
            _, client = member_client(project, f'{role}@taskboard.dev', role)
        res = client.post(export_url(project.id))
        assert res.status_code == expected
        if expected == 403:
            assert 'error' in res.data and fake_airtable.calls == []
        else:
            assert res.data['exported'] == 1 and len(fake_airtable.calls) == 1

    def test_unauthenticated_gets_401(self, project, fake_airtable):                   # A2
        res = APIClient().post(export_url(project.id))
        assert res.status_code == 401 and fake_airtable.calls == []

    def test_response_counts_and_invariants(self, project, owner, fake_airtable):      # B4
        make_tasks(project, owner, 4)
        res = authed_client(owner).post(export_url(project.id))
        assert res.status_code == 200
        assert res.data == {'exported': 4, 'created': 4, 'updated': 0, 'failed': [], 'total': 4}
        assert res.data['exported'] == res.data['created'] + res.data['updated']
        assert res.data['total'] == res.data['exported'] + len(res.data['failed']) == 4

    def test_missing_airtable_config_returns_503(self, project, owner, settings):      # B8
        settings.AIRTABLE_API_KEY = ''
        res = authed_client(owner).post(export_url(project.id))
        assert res.status_code == 503 and res.data == {'error': 'airtable not configured'}

    def test_partial_failure_is_200_with_failed_list(self, project, owner, fake_airtable):
        tasks = make_tasks(project, owner, 3)
        fake_airtable.fail_for_task_id(str(tasks[1].id), http_error(422))
        res = authed_client(owner).post(export_url(project.id))
        assert res.status_code == 200
        assert res.data['exported'] == 2 and res.data['failed'][0]['taskId'] == str(tasks[1].id)

    def test_all_records_fail_still_returns_200(self, project, owner, fake_airtable):  # D3
        tasks = make_tasks(project, owner, 3)
        for t in tasks:
            fake_airtable.fail_for_task_id(str(t.id), http_error(422))
        res = authed_client(owner).post(export_url(project.id))
        assert res.status_code == 200 and res.data['exported'] == 0
        assert len(res.data['failed']) == 3 and all(f['reason'] for f in res.data['failed'])
        assert res.data['total'] == 3

    def test_airtable_auth_error_returns_502(self, project, owner, fake_airtable):     # D4
        make_tasks(project, owner, 3)
        fake_airtable.fail_next(1, http_error(401))
        res = authed_client(owner).post(export_url(project.id))
        assert res.status_code == 502 and res.data == {'error': 'airtable authentication failed'}
        assert fake_airtable.rows == {} and 'failed' not in res.data

    def test_response_has_no_tasks_list(self, project, owner, fake_airtable):
        res = authed_client(owner).post(export_url(project.id))
        assert set(res.data) == {'exported', 'created', 'updated', 'failed', 'total'}
```

- [ ] **Step 2: Run to verify it fails**

Run: `docker compose exec -T backend python -m pytest projects/test_export.py -k Endpoint -v`
Expected: A1 admin/member cases FAIL (stub returns `{'exported': 0, 'tasks': [...]}`, no Airtable call); B4, B8, D3, D4 and the no-tasks-list test FAIL; A1 viewer/non-member and A2 already PASS.

- [ ] **Step 3: Rewrite `ExportView.post`**

```python
# backend/projects/views.py
from .airtable_export import export_project_tasks, AirtableNotConfigured, AirtableAuthError

class ExportView(APIView):
    def post(self, request, project_id):
        membership = _get_membership(request.user, project_id)
        if not membership:
            return Response({'error': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if not _can_edit_tasks(membership.role):
            return Response({'error': 'only admins and members can export'}, status=status.HTTP_403_FORBIDDEN)
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            result = export_project_tasks(project)
        except AirtableNotConfigured:
            return Response({'error': 'airtable not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except AirtableAuthError:
            return Response({'error': 'airtable authentication failed'}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(result.as_dict())
```

`TaskSerializer` is still imported for other views; nothing else in the file changes. The 502 body deliberately omits Airtable's message so nothing about the credentials leaks.

- [ ] **Step 4: Run the export tests and the full backend suite**

Run:
```bash
docker compose exec -T backend python -m pytest projects/test_export.py -v
docker compose exec -T backend python -m pytest -q
```
Expected: all PASS. The suite must not sleep for real (total runtime stays in seconds).

- [ ] **Step 5: Commit**

```bash
git add backend/projects/views.py backend/projects/test_export.py
git commit -m "feat: POST /api/projects/:id/export upserts tasks to Airtable and reports counts and failures"
```

---

### Task 7: "Export to Airtable" button on the project page

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/pages/ProjectPage.tsx`
- Create: `frontend/src/tests/ProjectPage.test.tsx`

**Interfaces:**
- Consumes: `apiFetch`, `getStoredUser` from `@/lib/api-client`; `POST /api/projects/:id/export` (Task 6).
- Produces: `ApiExportResult` type; `canExport` derived from the same `myRole` as `canComment`; a button with accessible name "Export to Airtable" rendered only when `canExport`; a `data-testid="export-result"` line after a run; a `role="alert"` line on request error.

- [ ] **Step 1: Write the failing tests** (F1–F4)

```tsx
// frontend/src/tests/ProjectPage.test.tsx
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProjectPage from "@/pages/ProjectPage";
import type { ApiProjectDetail, Role } from "@/types";

const apiFetch = vi.fn();
vi.mock("@/lib/api-client", () => ({
  apiFetch: (...args: unknown[]) => apiFetch(...args),
  getToken: () => "token",
  getStoredUser: () => ({ id: "u_me", email: "me@taskboard.dev", name: "Me" }),
  clearSession: () => {},
}));

function projectWithRole(role: Role): ApiProjectDetail {
  return {
    id: "p_1", name: "P", description: null, ownerId: "u_me",
    owner: { id: "u_me", email: "me@taskboard.dev", name: "Me" },
    memberships: [{ id: "m_1", role, user: { id: "u_me", email: "me@taskboard.dev", name: "Me" } }],
    tasks: [], createdAt: "", updatedAt: "",
  };
}

function renderPage(role: Role, exportResponse: unknown = { exported: 3, created: 3, updated: 0, failed: [], total: 3 }) {
  apiFetch.mockImplementation((path: string) =>
    path.endsWith("/export") ? Promise.resolve(exportResponse) : Promise.resolve({ project: projectWithRole(role) }),
  );
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={["/projects/p_1"]}>
        <Routes><Route path="/projects/:id" element={<ProjectPage />} /></Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => apiFetch.mockReset());

describe("ProjectPage export button", () => {
  it("shows Export button for member", async () => {
    renderPage("member");
    expect(await screen.findByRole("button", { name: /export to airtable/i })).toBeInTheDocument();
  });

  it("hides Export button for viewer", async () => {
    renderPage("viewer");
    await screen.findByText("P");
    expect(screen.queryByRole("button", { name: /export/i })).toBeNull();
  });

  it("calls the export endpoint and shows the summary", async () => {
    renderPage("admin");
    fireEvent.click(await screen.findByRole("button", { name: /export to airtable/i }));
    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith("/api/projects/p_1/export", expect.objectContaining({ method: "POST" })),
    );
    expect(await screen.findByTestId("export-result")).toHaveTextContent("Exported 3 tasks");
  });

  it("shows partial-failure count and re-enables the button", async () => {
    renderPage("admin", { exported: 2, created: 2, updated: 0, failed: [{ taskId: "t", reason: "422" }], total: 3 });
    const button = await screen.findByRole("button", { name: /export to airtable/i });
    fireEvent.click(button);
    expect(await screen.findByTestId("export-result")).toHaveTextContent("1 task failed");
    expect(button).not.toBeDisabled();
  });

  it("surfaces a 503 when Airtable is not configured and keeps the button", async () => {   // F4
    apiFetch.mockImplementation((path: string) =>
      path.endsWith("/export")
        ? Promise.reject(new Error("airtable not configured"))
        : Promise.resolve({ project: projectWithRole("admin") }),
    );
    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter initialEntries={["/projects/p_1"]}>
          <Routes><Route path="/projects/:id" element={<ProjectPage />} /></Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );
    const button = await screen.findByRole("button", { name: /export to airtable/i });
    fireEvent.click(button);
    expect(await screen.findByRole("alert")).toHaveTextContent("airtable not configured");
    expect(screen.getByRole("button", { name: /export to airtable/i })).not.toBeDisabled();
  });
});
```

F4 relies on `apiFetch` rejecting with the server's `error` message on a non-2xx response (its existing behaviour); a 502 `airtable authentication failed` surfaces the same way.

Check `frontend/vitest.config.ts` includes `src/tests/**` with `jsdom` (it does for the existing tests).

- [ ] **Step 2: Run to verify it fails**

Run: `docker compose exec -T frontend npm test -- --run src/tests/ProjectPage.test.tsx`
Expected: FAIL — no button named "Export to Airtable"; no element with test id `export-result`.

- [ ] **Step 3: Implement the type and the button**

```typescript
// frontend/src/types/index.ts
export type ApiExportResult = {
  exported: number;
  created: number;
  updated: number;
  failed: { taskId: string; reason: string }[];
  total: number;
};
```

```tsx
// frontend/src/pages/ProjectPage.tsx — near canComment
const isEditor = myRole === "admin" || myRole === "member";
const canComment = isEditor;
const canExport = isEditor;

const [exportResult, setExportResult] = useState<ApiExportResult | null>(null);
const [exportError, setExportError] = useState<string | null>(null);
const exportTasks = useMutation({
  mutationFn: () => apiFetch<ApiExportResult>(`/api/projects/${id}/export`, { method: "POST" }),
  onMutate: () => { setExportError(null); setExportResult(null); },
  onSuccess: (res) => setExportResult(res),
  onError: (err) => setExportError(err instanceof Error ? err.message : "export failed"),
});
```

```tsx
// in the header row (the flex container that holds <h1>), right-hand side:
{canExport && (
  <div className="text-right">
    <button
      type="button"
      onClick={() => exportTasks.mutate()}
      disabled={exportTasks.isPending}
      className="bg-surface border border-border hover:border-accent text-sm font-medium rounded-md px-4 py-2 disabled:opacity-50"
    >
      {exportTasks.isPending ? "Exporting…" : "Export to Airtable"}
    </button>
    {exportResult && (
      <p data-testid="export-result" className="text-xs text-muted mt-2">
        Exported {exportResult.exported} tasks ({exportResult.created} created, {exportResult.updated} updated)
        {exportResult.failed.length > 0 &&
          ` · ${exportResult.failed.length} task${exportResult.failed.length === 1 ? "" : "s"} failed`}
      </p>
    )}
    {exportError && (
      <p role="alert" className="text-xs text-red-400 mt-2">{exportError}</p>
    )}
  </div>
)}
```

A 503 from the server surfaces as the alert "airtable not configured" through `apiFetch`'s existing error handling; no extra UI state is needed.

- [ ] **Step 4: Run the frontend tests and a type check**

Run:
```bash
docker compose exec -T frontend npm test -- --run
docker compose exec -T frontend npx tsc --noEmit
```
Expected: all Vitest suites PASS; no `src/` type errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/pages/ProjectPage.tsx frontend/src/tests/ProjectPage.test.tsx
git commit -m "feat: Export to Airtable button for admins and members with result summary"
```

---

### Task 8: Manual real-integration verification and docs

**Files:**
- Modify: `README.md` (Airtable Export section)
- Append: `TERMINAL_LOG.md` (the run, never the key)

This is the only step that touches the real base. It is deliberately manual and not part of CI: the real API is rate-limited (5 req/s per base), needs a secret that must not enter the repo or CI logs, writes persist in a shared base (tests would need cleanup and would collide when run concurrently), and network latency makes results non-deterministic. Every logic path is already covered deterministically by `FakeAirtableTable`; this run only proves credentials, field names, the single-select choices, and the pyairtable `batch_upsert` wiring (including that `performUpsert` on `Task ID` really matches).

- [ ] **Step 1: Confirm config without printing secrets**

Run: `docker compose exec -T backend python -c "from django.conf import settings; print(bool(settings.AIRTABLE_API_KEY), settings.AIRTABLE_BASE_ID[:3], settings.AIRTABLE_TABLE_NAME)"`
Expected: `True app Tasks`.

- [ ] **Step 2: First export**

Log in as an admin in the UI, open a project with 3–5 tasks (include one unassigned and one with a description), click "Export to Airtable". Expected: summary reads `Exported N tasks (N created, 0 updated)`.

- [ ] **Step 3: Read back through the Airtable MCP**

Use `list_records_for_table` on the `Tasks` table filtered by `{Project ID}='<project uuid>'`. Expected: exactly N rows, `Task ID` values equal the task UUIDs, `Status` shows the select choice, `Assignee` shows the email or is blank.

- [ ] **Step 4: Idempotency re-run**

Edit one task's title in the UI, click export again. Expected: `Exported N tasks (0 created, N updated)`; the MCP read-back still shows N rows for the project and the edited title. Then delete one task locally and export once more: expected `Exported N-1 tasks (0 created, N-1 updated)` and the base still has N rows (D11).

- [ ] **Step 5: Document**

Add to `README.md` under "Airtable Export (Part 3c)": the response shape, the idempotency rule (server-side upsert on `Task ID`), the chunking (10 records per `batch_upsert` call), the retry policy (3 attempts, 0.5 s / 1 s, honours `Retry-After`), the single-record fallback for a permanently failed chunk, the 503 (unconfigured) and 502 (Airtable auth error) cases, the "deleted locally leaves the row" rule, and the sentence on why the real run is manual. Append the verification outcome to `TERMINAL_LOG.md`.

Run: `git add README.md TERMINAL_LOG.md && git commit -m "docs: Airtable export behaviour and manual verification record"`

---

## Self-review

- **Bulk export of all tasks:** Task 2 loads every task and sends them through `batch_upsert` in chunks of `BATCH_SIZE = 10` (`test_exports_all_tasks_in_project`, `test_large_export_batches_not_per_task`: 1000 tasks = 100 calls, `test_only_this_projects_tasks_exported`). Covered.
- **Idempotent re-runs, race-free:** D2 server-side upsert keyed on `Task ID`; no lookup, no stored record id (`TestIdempotency`, C1–C4, C6). Concurrent exports cannot both "see no row" because matching happens inside Airtable's request. Covered.
- **Deleted locally:** absent from the payload, so the stale row is untouched and the run succeeds (`test_reexport_after_local_delete`). Covered.
- **Partial-failure resilience:** Task 5 single-record fallback scoped to the permanently failed chunk, per-record `failed` entries, 200 on partial or total failure (`test_single_permanent_failure_does_not_abort`, `test_failed_chunk_falls_back_to_single_records`, `test_all_records_fail_still_returns_200`, `test_failed_record_recovers_on_next_run`). Covered.
- **Transient retry with backoff:** Task 4 `_classify` + `_call_with_retry`, `MAX_ATTEMPTS`, `Retry-After`, 504 and network errors included (`test_transient_is_retried_then_succeeds`, `test_retries_are_bounded`, `test_backoff_delays_grow`, `test_429_honours_retry_after`, `test_429_without_retry_after_uses_backoff`); pyairtable's own retries disabled so counts are exact; a retried chunk is duplicate-safe by `Task ID`. A chunk that exhausts retries is reported failed with no fallback. Covered.
- **Auth error from Airtable:** 401/403 → `AirtableAuthError` → HTTP 502, no retry, no per-record report (`test_auth_error_aborts_without_retry`, `test_airtable_auth_error_returns_502`). Covered.
- **Authorization server-side:** stub's `_get_membership` + `_can_edit_tasks` kept; `test_export_role_gate` and `test_unauthenticated_gets_401` over HTTP in Task 6; viewer hiding in the UI is convenience only. Covered.
- **Unconfigured:** 503 before any work (`test_missing_airtable_config_returns_503`). Covered.
- **Deterministic chunking:** `_chunks` with `BATCH_SIZE`; `test_chunk_boundaries_are_exact` (10/10/3) and B7 assert every call is ≤10 records. The fake never enforces the size, so the assertion is on the service, not the double.
- **No network in unit tests:** every service test injects `FakeAirtableTable` and a recorder `sleep`; HTTP tests patch `get_table` and `time.sleep`. The only real call is the manual run in Task 8.
- **Test-plan alignment:** test names, response shape, 503, 502 on auth, retry constants (3 attempts, 0.5/1.0), the three-way error classification (transient / per-record permanent 400-404-422 / auth 401-403), `""` for empty assignee, the eight-field mapping, and the fallback call pattern (1 × 10 then 10 × 1) match `docs/3c-airtable-export-test-plan.md`. Deliberate placement: B1–B3, B5–B7, C1–C6, D1–D3 and E1–E6 run at the service level with the plan's names (so they go red → green before the view exists); A1, A2, B4, B8, D3 and D4 are also asserted over HTTP in Task 6.
- **Type consistency:** `ApiExportResult` in the frontend mirrors `ExportResult.as_dict()` key for key (`exported, created, updated, failed[{taskId, reason}], total`).
