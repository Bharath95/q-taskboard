"""Sanity checks for the FakeAirtableTable test double.

These SHOULD PASS: the double is complete scaffolding, not a red stub.
"""

import pytest
import requests

from projects.airtable_mock import FakeAirtableTable, http_error


def _record(task_id, **fields):
    return {"fields": {"Task ID": str(task_id), **fields}}


def test_upsert_creates_then_updates_same_key():
    fake = FakeAirtableTable()

    first = fake.batch_upsert([_record("t1", Title="A")], key_fields=["Task ID"])
    assert len(first["createdRecords"]) == 1
    assert first["updatedRecords"] == []
    assert len(fake.store) == 1
    rec_id = first["createdRecords"][0]

    second = fake.batch_upsert([_record("t1", Title="B")], key_fields=["Task ID"])
    assert second["createdRecords"] == []
    assert second["updatedRecords"] == [rec_id]  # same record id reused
    assert len(fake.store) == 1  # no duplicate row
    assert fake.store["t1"]["fields"]["Title"] == "B"  # value updated
    assert len(fake.calls) == 2


def test_fail_next_raises_then_recovers():
    fake = FakeAirtableTable()
    fake.fail_next(1, http_error(503))

    with pytest.raises(requests.HTTPError):
        fake.batch_upsert([_record("t1")], key_fields=["Task ID"])
    # The failed call is still recorded and nothing was stored.
    assert len(fake.calls) == 1
    assert fake.store == {}

    result = fake.batch_upsert([_record("t1")], key_fields=["Task ID"])
    assert len(result["createdRecords"]) == 1
    assert len(fake.calls) == 2


def test_fail_for_task_id_targets_the_right_record():
    fake = FakeAirtableTable()
    fake.fail_for_task_id("bad", http_error(422))

    # A batch that does not include the poisoned id succeeds.
    ok = fake.batch_upsert([_record("good")], key_fields=["Task ID"])
    assert len(ok["createdRecords"]) == 1

    # Any batch that includes it raises, every time.
    with pytest.raises(requests.HTTPError):
        fake.batch_upsert([_record("good2"), _record("bad")], key_fields=["Task ID"])
    with pytest.raises(requests.HTTPError):
        fake.batch_upsert([_record("bad")], key_fields=["Task ID"])


def test_http_error_carries_status_and_headers():
    exc = http_error(429, headers={"Retry-After": "3"})
    assert isinstance(exc, requests.HTTPError)
    assert exc.response.status_code == 429
    assert exc.response.headers["Retry-After"] == "3"

    plain = http_error(500)
    assert plain.response.status_code == 500


def test_clear_failures_recovers_targeted_record():
    fake = FakeAirtableTable()
    fake.fail_for_task_id("t3", http_error(422))
    with pytest.raises(requests.HTTPError):
        fake.batch_upsert([_record("t3")], key_fields=["Task ID"])

    fake.clear_failures()
    result = fake.batch_upsert([_record("t3")], key_fields=["Task ID"])
    assert len(result["createdRecords"]) == 1
