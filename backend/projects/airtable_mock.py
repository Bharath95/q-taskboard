"""In-memory test double for a pyairtable ``Table``.

Only ``batch_upsert`` is exercised by the export service, so that is the one
method modelled here. The double mirrors pyairtable 2.3.7 semantics closely
enough that the service's error-classification and retry code sees the real
types (``requests.HTTPError`` carrying a ``.response`` with a status code and
headers).

This module is genuine test scaffolding: it is meant to be fully working, not
a red stub.
"""

import copy

import requests


def http_error(status, headers=None):
    """Build the ``requests.HTTPError`` pyairtable raises for an HTTP failure.

    ``exc.response.status_code`` carries the status and ``exc.response.headers``
    carries any response headers (e.g. ``Retry-After`` on a 429), matching what
    pyairtable 2.3.x surfaces to callers.
    """
    response = requests.Response()
    response.status_code = status
    if headers:
        response.headers.update(headers)
    return requests.HTTPError(f"HTTP {status}", response=response)


class FakeAirtableTable:
    """Minimal stand-in for ``pyairtable.Table`` supporting ``batch_upsert``.

    Rows are stored in-memory keyed by their ``Task ID`` field. Every call is
    recorded in ``self.calls``. Failures can be scripted with ``fail_next`` and
    ``fail_for_task_id``.
    """

    def __init__(self):
        # Task ID -> {"id": recXXXX, "fields": {...}}
        self.store = {}
        # One entry per batch_upsert call: {"records", "key_fields", "typecast", "kw"}
        self.calls = []
        self._id_counter = 0
        self._fail_remaining = 0
        self._fail_exc = None
        self._fail_task_ids = {}  # task_id -> exc

    # -- scriptable failures -------------------------------------------------

    def fail_next(self, n, exc):
        """Raise ``exc`` on each of the next ``n`` calls to ``batch_upsert``."""
        self._fail_remaining = n
        self._fail_exc = exc

    def fail_for_task_id(self, task_id, exc):
        """Raise ``exc`` on any call whose records include ``task_id``."""
        self._fail_task_ids[str(task_id)] = exc

    def clear_failures(self):
        """Drop all scripted failures (used by recovery tests)."""
        self._fail_remaining = 0
        self._fail_exc = None
        self._fail_task_ids = {}

    # -- the modelled API ----------------------------------------------------

    def batch_upsert(self, records, key_fields, typecast=False, **kw):
        """Upsert ``records`` matching existing rows on ``key_fields``.

        Returns ``{"createdRecords": [...ids], "updatedRecords": [...ids],
        "records": [...]}``. Does not raise on batch size; the service already
        chunks to <= 10.
        """
        self.calls.append({
            "records": copy.deepcopy(records),
            "key_fields": list(key_fields),
            "typecast": typecast,
            "kw": kw,
        })

        # Transient-style failure: raise on the next n calls regardless of content.
        if self._fail_remaining > 0:
            self._fail_remaining -= 1
            raise self._fail_exc

        # Per-record failure: raise if any record carries a targeted Task ID.
        if self._fail_task_ids:
            for record in records:
                key = str(record["fields"].get("Task ID"))
                if key in self._fail_task_ids:
                    raise self._fail_task_ids[key]

        key_field = key_fields[0]
        created_ids = []
        updated_ids = []
        result_records = []

        for record in records:
            fields = dict(record["fields"])
            key = str(fields.get(key_field))
            if key in self.store:
                existing = self.store[key]
                existing["fields"].update(fields)
                updated_ids.append(existing["id"])
                result_records.append(copy.deepcopy(existing))
            else:
                self._id_counter += 1
                rec_id = f"rec{self._id_counter:014d}"
                row = {"id": rec_id, "fields": fields}
                self.store[key] = row
                created_ids.append(rec_id)
                result_records.append(copy.deepcopy(row))

        return {
            "createdRecords": created_ids,
            "updatedRecords": updated_ids,
            "records": result_records,
        }
