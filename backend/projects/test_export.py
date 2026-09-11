"""Part 3c — Airtable export tests (groups A-E).

RED by design: the export feature is not implemented. HTTP tests go through
``POST /api/projects/<id>/export`` (still a stub) and service-level retry tests
call ``projects.airtable_export.export_project_tasks`` directly (still raises
``NotImplementedError``). No real Airtable call is ever made: the table factory
is patched with ``FakeAirtableTable`` and ``time.sleep`` is patched/injected.

Test style follows projects/test_comments.py (pytest + APIClient, Bearer token
from POST /api/auth/login, member_client helper).
"""

import pytest
import requests

from rest_framework.test import APIClient

from users.models import User
from projects.models import Project, Membership, Task
from projects import airtable_export
from projects.airtable_export import (
    export_project_tasks,
    get_table,
    BATCH_SIZE,
    MAX_ATTEMPTS,
    BACKOFF_BASE_SECONDS,
    AirtableNotConfigured,
    AirtableAuthError,
)
from projects.airtable_mock import FakeAirtableTable, http_error


pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# Helpers / fixtures
# --------------------------------------------------------------------------- #

def make_user(email, name="Test User"):
    return User.objects.create_user(email=email, name=name, password="password123")


def authed_client(user):
    client = APIClient()
    resp = client.post(
        "/api/auth/login",
        {"email": user.email, "password": "password123"},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['token']}")
    return client


def member_client(project, email, role):
    user = make_user(email, name=f"{role.title()} User")
    Membership.objects.create(user=user, project=project, role=role)
    return user, authed_client(user)


def make_task(project, owner, title="A task", **kwargs):
    return Task.objects.create(project=project, title=title, created_by=owner, **kwargs)


def export_url(project_id):
    return f"/api/projects/{project_id}/export"


def expected_backoff(attempt_index):
    """Backoff delay before retry number ``attempt_index`` (0-based).

    Read from the module constant so the test tracks the implementation's
    exponential schedule rather than hard-coding seconds.
    """
    return BACKOFF_BASE_SECONDS * (2 ** attempt_index)


@pytest.fixture
def owner(db):
    return make_user("owner@taskboard.dev", name="Olive Owner")


@pytest.fixture
def project(owner):
    project = Project.objects.create(name="Export Project", owner=owner)
    Membership.objects.create(user=owner, project=project, role="admin")
    return project


@pytest.fixture(autouse=True)
def _airtable_settings(settings):
    """Configure Airtable so the config check passes for every test except B8."""
    settings.AIRTABLE_API_KEY = "test-key"
    settings.AIRTABLE_BASE_ID = "appTEST00000000"
    settings.AIRTABLE_TABLE_NAME = "Tasks"


@pytest.fixture
def fake_export(monkeypatch):
    """Patch the table factory with a FakeAirtableTable and silence sleep.

    HTTP tests use this so the endpoint (once wired) upserts into the fake and
    never touches the network.
    """
    fake = FakeAirtableTable()
    monkeypatch.setattr(airtable_export, "get_table", lambda: fake)
    monkeypatch.setattr(airtable_export.time, "sleep", lambda *a, **k: None)
    return fake


# --------------------------------------------------------------------------- #
# A. Authorization
# --------------------------------------------------------------------------- #

class TestAuthorization:
    @pytest.mark.parametrize("role,expected", [
        ("admin", 200),
        ("member", 200),
        ("viewer", 403),
        ("non_member", 403),
    ])
    def test_export_role_gate(self, project, owner, fake_export, role, expected):
        make_task(project, owner)

        if role == "non_member":
            client = authed_client(make_user("nobody@taskboard.dev"))
        elif role == "admin":
            client = authed_client(owner)
        else:
            _, client = member_client(project, f"{role}@taskboard.dev", role)

        resp = client.post(export_url(project.id))
        assert resp.status_code == expected
        if expected == 403:
            assert fake_export.calls == []

    def test_unauthenticated_gets_401(self, project, owner, fake_export):
        make_task(project, owner)
        resp = APIClient().post(export_url(project.id))
        assert resp.status_code == 401
        assert fake_export.calls == []


# --------------------------------------------------------------------------- #
# B. Core export
# --------------------------------------------------------------------------- #

class TestCoreExport:
    def test_exports_all_tasks_in_project(self, project, owner, fake_export):
        tasks = [make_task(project, owner, title=f"T{i}") for i in range(3)]
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        assert resp.data["created"] == 3
        assert len(fake_export.store) == 3
        assert set(fake_export.store.keys()) == {str(t.id) for t in tasks}

    def test_field_mapping(self, project, owner, fake_export):
        assignee = make_user("dev@taskboard.dev", name="Dev Person")
        Membership.objects.create(user=assignee, project=project, role="member")
        task = make_task(
            project, owner,
            title="Wire the widget",
            description="do the thing",
            status="in_progress",
            assignee=assignee,
            position=4,
        )
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        fields = fake_export.store[str(task.id)]["fields"]
        assert fields == {
            "Task ID": str(task.id),
            "Title": "Wire the widget",
            "Description": "do the thing",
            "Status": "in_progress",
            "Assignee": "dev@taskboard.dev",
            "Project": project.name,
            "Project ID": str(project.id),
            "Position": 4,
        }

    def test_unassigned_task_maps_assignee_empty(self, project, owner, fake_export):
        task = make_task(project, owner, assignee=None)
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        assert fake_export.store[str(task.id)]["fields"]["Assignee"] == ""

    def test_response_counts_and_invariants(self, project, owner, fake_export):
        for i in range(4):
            make_task(project, owner, title=f"T{i}")
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        body = resp.data
        assert body["created"] == 4
        assert body["updated"] == 0
        assert body["failed"] == []
        assert body["exported"] == body["created"] + body["updated"]
        assert body["total"] == body["exported"] + len(body["failed"]) == 4

    def test_empty_project_exports_zero(self, project, owner, fake_export):
        client = authed_client(owner)
        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        assert resp.data["exported"] == 0
        assert fake_export.calls == []  # no batch_upsert on an empty project

    def test_only_this_projects_tasks_exported(self, owner, fake_export):
        project_a = Project.objects.create(name="Project A", owner=owner)
        Membership.objects.create(user=owner, project=project_a, role="admin")
        project_b = Project.objects.create(name="Project B", owner=owner)
        Membership.objects.create(user=owner, project=project_b, role="admin")

        a_tasks = [make_task(project_a, owner, title=f"A{i}") for i in range(2)]
        b_tasks = [make_task(project_b, owner, title=f"B{i}") for i in range(2)]

        # Preload a fake row for one of B's tasks; it must stay untouched.
        fake_export.store[str(b_tasks[0].id)] = {
            "id": "recPRELOADED000",
            "fields": {"Task ID": str(b_tasks[0].id), "Title": "untouched"},
        }

        client = authed_client(owner)
        resp = client.post(export_url(project_a.id))
        assert resp.status_code == 200

        upserted = {r["fields"]["Task ID"]
                    for call in fake_export.calls for r in call["records"]}
        assert upserted == {str(t.id) for t in a_tasks}
        for r in (r for call in fake_export.calls for r in call["records"]):
            assert r["fields"]["Project ID"] == str(project_a.id)
        assert fake_export.store[str(b_tasks[0].id)]["fields"]["Title"] == "untouched"

    def test_large_export_batches_not_per_task(self, project, owner, fake_export):
        Task.objects.bulk_create(
            Task(project=project, title=f"T{i}", created_by=owner, position=i)
            for i in range(1000)
        )
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        assert resp.data["exported"] == 1000
        assert len(fake_export.calls) == 1000 // BATCH_SIZE  # 100 chunks of 10
        assert all(len(call["records"]) <= BATCH_SIZE for call in fake_export.calls)

    def test_missing_airtable_config_returns_503(self, project, owner, settings):
        # No fake patch here: the real get_table must see empty config and 503.
        settings.AIRTABLE_API_KEY = ""
        make_task(project, owner)
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 503
        assert resp.data == {"error": "airtable not configured"}


# --------------------------------------------------------------------------- #
# C. Idempotency
# --------------------------------------------------------------------------- #

class TestIdempotency:
    def test_second_run_does_not_duplicate(self, project, owner, fake_export):
        for i in range(3):
            make_task(project, owner, title=f"T{i}")
        client = authed_client(owner)

        client.post(export_url(project.id))
        client.post(export_url(project.id))
        assert len(fake_export.store) == 3

    def test_second_run_reports_updated_not_created(self, project, owner, fake_export):
        for i in range(3):
            make_task(project, owner, title=f"T{i}")
        client = authed_client(owner)

        first = client.post(export_url(project.id))
        assert first.data["created"] == 3
        assert first.data["updated"] == 0

        second = client.post(export_url(project.id))
        assert second.data["created"] == 0
        assert second.data["updated"] == 3
        assert second.data["exported"] == 3

    def test_changed_task_updates_same_row(self, project, owner, fake_export):
        task = make_task(project, owner, title="original", status="todo")
        client = authed_client(owner)

        client.post(export_url(project.id))
        rec_id = fake_export.store[str(task.id)]["id"]

        task.title = "changed"
        task.status = "done"
        task.save()
        resp = client.post(export_url(project.id))

        row = fake_export.store[str(task.id)]
        assert row["fields"]["Title"] == "changed"
        assert row["fields"]["Status"] == "done"
        assert row["id"] == rec_id  # same Airtable record
        assert resp.data["updated"] >= 1

    def test_mixed_create_and_update(self, project, owner, fake_export):
        make_task(project, owner, title="T0")
        make_task(project, owner, title="T1")
        client = authed_client(owner)
        client.post(export_url(project.id))

        make_task(project, owner, title="T2")
        resp = client.post(export_url(project.id))
        assert resp.data["created"] == 1
        assert resp.data["updated"] == 2
        assert len(fake_export.store) == 3

    def test_failed_record_recovers_on_next_run(self, project, owner, fake_export):
        make_task(project, owner, title="T0")
        make_task(project, owner, title="T1")
        t3 = make_task(project, owner, title="T2")
        fake_export.fail_for_task_id(t3.id, http_error(422))
        client = authed_client(owner)

        first = client.post(export_url(project.id))
        assert first.status_code == 200
        assert [f["taskId"] for f in first.data["failed"]] == [str(t3.id)]
        assert len(fake_export.store) == 2

        fake_export.clear_failures()
        second = client.post(export_url(project.id))
        assert second.data["failed"] == []
        assert str(t3.id) in fake_export.store

    def test_reexport_after_local_delete(self, project, owner, fake_export):
        tasks = [make_task(project, owner, title=f"T{i}") for i in range(3)]
        client = authed_client(owner)
        client.post(export_url(project.id))

        deleted_id = str(tasks[0].id)
        tasks[0].delete()

        fake_export.calls.clear()
        resp = client.post(export_url(project.id))
        assert resp.status_code == 200

        upserted = {r["fields"]["Task ID"]
                    for call in fake_export.calls for r in call["records"]}
        assert upserted == {str(tasks[1].id), str(tasks[2].id)}
        # Orphan row for the locally-deleted task stays in place (out of scope).
        assert deleted_id in fake_export.store


# --------------------------------------------------------------------------- #
# D. Partial failure resilience
# --------------------------------------------------------------------------- #

class TestPartialFailure:
    def test_single_permanent_failure_does_not_abort(self, project, owner, fake_export):
        tasks = [make_task(project, owner, title=f"T{i}") for i in range(5)]
        t3 = tasks[2]
        fake_export.fail_for_task_id(t3.id, http_error(422))
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        assert resp.data["exported"] == 4
        assert len(resp.data["failed"]) == 1
        failure = resp.data["failed"][0]
        assert failure["taskId"] == str(t3.id)
        assert "422" in failure["reason"]
        assert len(fake_export.store) == 4
        assert resp.data["total"] == resp.data["exported"] + len(resp.data["failed"]) == 5

    def test_failed_chunk_falls_back_to_single_records(self, project, owner, fake_export):
        tasks = [make_task(project, owner, title=f"T{i}") for i in range(BATCH_SIZE)]
        poisoned = tasks[5]
        fake_export.fail_for_task_id(poisoned.id, http_error(422))
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        # One chunk call (fails) + one single-record call per task.
        single_calls = [c for c in fake_export.calls if len(c["records"]) == 1]
        assert len(single_calls) == BATCH_SIZE
        assert resp.data["exported"] == BATCH_SIZE - 1
        assert [f["taskId"] for f in resp.data["failed"]] == [str(poisoned.id)]

    def test_all_records_fail_still_returns_200(self, project, owner, fake_export):
        tasks = [make_task(project, owner, title=f"T{i}") for i in range(3)]
        for t in tasks:
            fake_export.fail_for_task_id(t.id, http_error(422))
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 200
        assert resp.data["exported"] == 0
        assert len(resp.data["failed"]) == 3
        assert all(f["reason"] for f in resp.data["failed"])
        assert resp.data["total"] == 3

    def test_airtable_auth_error_returns_502(self, project, owner, fake_export):
        make_task(project, owner)
        fake_export.fail_next(1, http_error(401))
        client = authed_client(owner)

        resp = client.post(export_url(project.id))
        assert resp.status_code == 502
        assert "error" in resp.data
        assert fake_export.store == {}
        assert "failed" not in resp.data  # aborted, not a per-record report


# --------------------------------------------------------------------------- #
# E. Retry behaviour (service-level; sleep injected as a recorder)
# --------------------------------------------------------------------------- #

class TestRetry:
    @pytest.mark.parametrize("exc", [
        http_error(429),
        http_error(500),
        http_error(502),
        http_error(503),
        http_error(504),
        requests.Timeout("timeout"),
        requests.ConnectionError("conn reset"),
    ])
    def test_transient_is_retried_then_succeeds(self, project, owner, exc):
        n = 3
        for i in range(n):
            make_task(project, owner, title=f"T{i}")
        fake = FakeAirtableTable()
        fake.fail_next(1, exc)
        sleeps = []

        result = export_project_tasks(project, table=fake, sleep=sleeps.append)

        assert result["exported"] == n
        assert result["failed"] == []
        assert len(fake.calls) == 2  # first fails, retry succeeds
        assert len(sleeps) == 1

    @pytest.mark.parametrize("status", [400, 404, 422])
    def test_permanent_is_not_retried_and_reported(self, project, owner, status):
        task = make_task(project, owner)
        fake = FakeAirtableTable()
        fake.fail_for_task_id(task.id, http_error(status))
        sleeps = []

        result = export_project_tasks(project, table=fake, sleep=sleeps.append)

        assert len(fake.calls) == 1  # single task, single chunk, no retry
        assert sleeps == []
        assert [f["taskId"] for f in result["failed"]] == [str(task.id)]

    def test_retries_are_bounded(self, project, owner):
        task = make_task(project, owner)
        fake = FakeAirtableTable()
        fake.fail_next(99, http_error(503))
        sleeps = []

        result = export_project_tasks(project, table=fake, sleep=sleeps.append)

        assert len(fake.calls) == MAX_ATTEMPTS
        assert len(sleeps) == MAX_ATTEMPTS - 1
        assert [f["taskId"] for f in result["failed"]] == [str(task.id)]
        assert "503" in result["failed"][0]["reason"]

    def test_backoff_delays_grow(self, project, owner):
        make_task(project, owner)
        fake = FakeAirtableTable()
        fake.fail_next(2, http_error(503))
        sleeps = []

        export_project_tasks(project, table=fake, sleep=sleeps.append)

        assert sleeps == [expected_backoff(0), expected_backoff(1)]

    def test_429_honours_retry_after(self, project, owner):
        make_task(project, owner)
        fake = FakeAirtableTable()
        fake.fail_next(1, http_error(429, headers={"Retry-After": "3"}))
        sleeps = []

        export_project_tasks(project, table=fake, sleep=sleeps.append)

        assert sleeps[0] == 3

    def test_429_without_retry_after_uses_backoff(self, project, owner):
        make_task(project, owner)
        fake = FakeAirtableTable()
        fake.fail_next(1, http_error(429))
        sleeps = []

        export_project_tasks(project, table=fake, sleep=sleeps.append)

        assert sleeps[0] == expected_backoff(0)
        assert sleeps[0] != 0
