# Part 3c — Airtable Export: Test-Case Plan (for review)

Status: IMPLEMENTED. These cases are written and passing (42 backend export cases plus the frontend export-button cases); the live export against the real base was verified idempotent. Decisions from the review round are folded in (batch_upsert, synchronous, no queue).

## 1. Context and assumptions

### Stack clarification
- Backend is Django 5 + DRF. Real Airtable calls go through `pyairtable` (installed **2.3.7**, pinned `>=2.3,<3.0`). The brief's mention of the npm `airtable` package and `src/lib/airtable-mock.ts` comes from a stale PDF and does not apply.
- The endpoint already exists as a stub: `POST /api/projects/<uuid:project_id>/export` → `ExportView` in `backend/projects/views.py`. It already enforces membership + `_can_edit_tasks(role)` and returns `{'exported': 0, ...}`.
- Config comes from `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME` (default `Tasks`).
- `backend/projects/airtable_mock.py` does not exist yet. Creating it is part of 3c (see "Test double").

### Endpoint contract

Request: `POST /api/projects/{project_id}/export`, empty body, Bearer token.

Success (HTTP 200), also returned when some records failed:

```json
{
  "exported": 12,
  "created": 9,
  "updated": 3,
  "failed": [ { "taskId": "0f1c...", "reason": "422 INVALID_VALUE_FOR_COLUMN" } ],
  "total": 13
}
```

- Invariants: `exported == created + updated`; `total == exported + len(failed)`; `total` equals the number of tasks in the project.
- HTTP 200 with a non-empty `failed` list = partial success.
- Non-200 only for: `401` (unauthenticated), `403` (viewer/non-member), `503` (missing Airtable config), or `502` (an Airtable **auth** error such as 401/403 from the API, meaning no work could proceed).
- Error shape: `{"error": "<message>"}`.

### Idempotency and export algorithm (what the tests assume)

Uses `pyairtable`'s server-side upsert; there is **no read-then-write lookup**, so two concurrent exports cannot both insert duplicates.

1. Auth check (already in stub). Load all tasks for the project (`select_related('assignee','created_by')`).
2. Build one record per task: `{"fields": {<mapping>}}`, including `Task ID = str(task.id)`.
3. Chunk the records into groups of **10** at the service level (`BATCH_SIZE = 10`). We own chunking deliberately, so a failure is isolated to at most 10 records and call counts are deterministic; each `batch_upsert` call therefore receives ≤10 records (never exceeding what pyairtable would send per request anyway).
4. For each chunk, call `table.batch_upsert(chunk, key_fields=["Task ID"], typecast=True)` wrapped in the retry loop. Accumulate `created += len(result["createdRecords"])`, `updated += len(result["updatedRecords"])`.
5. Failure handling per chunk:
   - **Transient** error → retried with backoff (see policy).
   - **Per-record permanent** error (400/404/422) → fall back to upserting that chunk's records one at a time (`batch_upsert([record], ...)`), so only the genuinely bad record lands in `failed`; the rest of the chunk still exports.
   - **Auth** error (401/403 from Airtable) → abort the whole export with `502`; this is a credentials/permission problem, not a per-record one.
6. Return the aggregated counts.

Verified `batch_upsert` signature (pyairtable 2.3.7):
`batch_upsert(records, key_fields, replace=False, typecast=False, return_fields_by_field_id=False) -> UpsertResultDict` where the result carries `createdRecords`, `updatedRecords`, and `records`.

### Field mapping (Task → Airtable `Tasks` row)

The base's `Tasks` table has exactly these fields; any other name returns `422 UNKNOWN_FIELD_NAME`.

| Airtable field | Source | Notes |
|---|---|---|
| `Task ID` | `str(task.id)` | Idempotency key (`key_fields`). |
| `Title` | `task.title` | Primary field. |
| `Description` | `task.description or ""` | |
| `Status` | `task.status` | Raw code (`todo`/`in_progress`/`review`/`done`) with `typecast=True`. |
| `Assignee` | `task.assignee.email` or `""` | Plain text. |
| `Project` | `project.name` | |
| `Project ID` | `str(project.id)` | Lets one base hold many projects. |
| `Position` | `task.position` | Number. |

### Injectable client (testability)
- Export logic lives in `export_project_tasks(project, table=None, sleep=time.sleep)` in a new `backend/projects/airtable_export.py`. When `table is None` it builds a real client via a `get_table()` factory (`Api(key, retry_strategy=False).table(base, name)`), so our own retry loop owns retries and call counts stay exact.
- The only method the service calls on the client is `batch_upsert(records, key_fields=..., typecast=...)`. Both `pyairtable.Table` and the double satisfy that.
- HTTP tests patch the factory (`monkeypatch.setattr('projects.airtable_export.get_table', lambda: fake)`) so they never touch the network. `sleep` is injected as a recorder so backoff is asserted without real waiting.

### Test double: `FakeAirtableTable` (built as part of 3c)
- In-memory store keyed by `Task ID` → fields; generates `recXXXX` ids on create.
- `batch_upsert(records, key_fields, typecast=False, **kw)`: matches on `key_fields`, updates matches and creates the rest, returns `{"createdRecords": [...], "updatedRecords": [...], "records": [...]}`. Records every call in `self.calls`. It mirrors `pyairtable` and does **not** raise on batch size (the service already sends ≤10).
- Scriptable failures: `fail_next(n, exc)` raises `exc` on the next `n` calls; `fail_for_task_id(task_id, exc)` raises whenever a call's records include that Task ID (per-record failure tests).
- Errors are raised as `requests.HTTPError` with `exc.response.status_code` set, matching what pyairtable 2.3.x surfaces, so the classification code sees the real type.

### Retry / error classification under test
- **Transient (retry, bounded):** HTTP 429, 500, 502, 503, 504, plus `requests.ConnectionError` / `requests.Timeout`. Exponential backoff honouring `Retry-After` on 429; `MAX_ATTEMPTS` total attempts (tests read the constant).
- **Per-record permanent (no retry, → `failed`):** HTTP 400, 404, 422.
- **Auth (no retry, → 502 abort):** HTTP 401, 403.

---

## 2. Test cases

Test style follows `backend/projects/test_comments.py`: pytest + `APIClient`, Bearer token from `POST /api/auth/login`, helper `member_client(project, email, role)`. Files: `backend/projects/test_export.py` (HTTP + service) and `backend/projects/test_airtable_mock.py` (double sanity checks). Every HTTP test patches the table factory with a `FakeAirtableTable`.

### A. Authorization (2 cases)

| # | Test name | Intent | Exercise / assert |
|---|---|---|---|
| A1 | `test_export_role_gate` (parametrized) | Server-side auth, not just UI. | Parametrize role→status: `admin→200, member→200, viewer→403, non_member→403`. On every 403 assert `fake.calls == []` (no Airtable call). |
| A2 | `test_unauthenticated_gets_401` | Missing token rejected. | POST with no credentials; assert 401 and no Airtable call. |

### B. Core export (8 cases)

| # | Test name | Intent | Exercise / assert |
|---|---|---|---|
| B1 | `test_exports_all_tasks_in_project` | Every task is pushed. | 3 tasks; POST; assert `created == 3`, store has 3 rows, set of `Task ID`s equals the task ids. |
| B2 | `test_field_mapping` | Row fields match the mapping. | One fully-populated task; assert the stored record's fields exactly (`Task ID`, `Title`, `Status`, `Assignee` email, `Project ID`, `Position`, ...). |
| B3 | `test_unassigned_task_maps_assignee_empty` | Null assignee does not crash. | Task with `assignee=None`; assert `Assignee == ""` and export succeeds. |
| B4 | `test_response_counts_and_invariants` | Counts consistent. | 4 tasks; assert `created == 4`, `updated == 0`, `failed == []`, `exported == created + updated`, `total == exported + len(failed) == 4`. |
| B5 | `test_empty_project_exports_zero` | No tasks is a graceful no-op. | 0 tasks; assert 200, `exported == 0`, and **no** `batch_upsert` call. |
| B6 | `test_only_this_projects_tasks_exported` | Scope is one project (replaces the old formula-string assertion with observable behavior). | Two projects, 2 tasks each, plus a preloaded fake row for a project-B task; export A; assert only A's Task IDs were upserted, every upserted row's `Project ID == A.id`, and B's preloaded row is unchanged. |
| B7 | `test_large_export_batches_not_per_task` | Batches, no per-task calls. | 1000 tasks; assert `batch_upsert` was called exactly 100 times (chunks of 10), each call ≤10 records, `exported == 1000`. |
| B8 | `test_missing_airtable_config_returns_503` | Unconfigured fails clearly, before any work. | Unset `AIRTABLE_API_KEY`; POST; assert 503 `{"error": "airtable not configured"}` and no `batch_upsert` call. |

### C. Idempotency (6 cases)

| # | Test name | Intent | Exercise / assert |
|---|---|---|---|
| C1 | `test_second_run_does_not_duplicate` | Re-run upserts, not inserts. | POST twice with 3 tasks (fake retains state); assert store still has 3 rows, each Task ID once. |
| C2 | `test_second_run_reports_updated_not_created` | Created vs updated split. | Run 1: `created == 3, updated == 0`. Run 2: `created == 0, updated == 3`, `exported == 3`. |
| C3 | `test_changed_task_updates_same_row` | Edits propagate to the same row. | Export; change a task's title+status; export; assert that Task ID's row has the new values, the same `rec` id, and `updated >= 1`. |
| C4 | `test_mixed_create_and_update` | New + existing in one run. | Export 2 tasks; add a 3rd; export; assert `created == 1, updated == 2`, store has 3 rows. |
| C5 | `test_failed_record_recovers_on_next_run` | Failures are not permanently stuck. | Run 1 with `fail_for_task_id(t3, 422)` → `t3` in `failed`, 2 rows stored. Clear the failure; run 2; assert `t3` is now created and `failed == []`. |
| C6 | `test_reexport_after_local_delete` | Deleted-locally task does not break re-export; orphan row left in place. | Export 3 tasks; delete one task locally; export; assert 200, only the 2 remaining Task IDs upserted, and the deleted task's row is **still present** in the store (orphan cleanup is out of scope) with no error. |

### D. Partial failure resilience (4 cases)

| # | Test name | Intent | Exercise / assert |
|---|---|---|---|
| D1 | `test_single_permanent_failure_does_not_abort` | One bad record, others succeed. | 5 tasks; `fail_for_task_id(t3, 422)`; assert 200, `exported == 4`, `failed == [{taskId: t3, reason ~ "422"}]`, store has 4 rows, `total == exported + len(failed) == 5`. |
| D2 | `test_failed_chunk_falls_back_to_single_records` | Blast radius bounded to the bad record. | 10 tasks in one chunk, one poisoned (422); assert the chunk `batch_upsert` fails, then 10 single-record `batch_upsert` calls follow; 9 succeed, 1 in `failed`. |
| D3 | `test_all_records_fail_still_returns_200` | Total failure reported, not a 500. | All tasks poisoned with 422; assert 200, `exported == 0`, `len(failed) == n`, each has a non-empty `reason`, `total == n`. |
| D4 | `test_airtable_auth_error_returns_502` | Bad credentials abort, not partial. | First `batch_upsert` raises `401`; assert 502 `{"error": ...}`, no records stored, no per-record `failed` report. |

### E. Retry behaviour (6 cases; service-level, `sleep` injected as a recorder)

| # | Test name | Intent | Exercise / assert |
|---|---|---|---|
| E1 | `test_transient_is_retried_then_succeeds` (parametrized) | Transient errors retry. | Parametrize over `429, 500, 502, 503, 504, requests.Timeout, requests.ConnectionError`: `fail_next(1, exc)`; assert `batch_upsert` called twice, `exported == n`, `failed == []`, `sleep` called once. |
| E2 | `test_permanent_is_not_retried_and_reported` (parametrized) | Validation errors do not retry. | Parametrize over `400, 404, 422`: `fail_for_task_id(t, exc)`; assert exactly one call for that record, `sleep` never called, `t` in `failed`. |
| E3 | `test_retries_are_bounded` | Never loops forever. | `fail_next(99, 503)`; assert exactly `MAX_ATTEMPTS` attempts, then the record in `failed` with reason mentioning 503; `sleep` called `MAX_ATTEMPTS - 1` times. |
| E4 | `test_backoff_delays_grow` | Backoff is exponential. | `fail_next(2, 503)`; assert recorded sleeps equal the module's computed backoff sequence (read from constants, not hard-coded). |
| E5 | `test_429_honours_retry_after` | Uses the server's hint. | 429 with `Retry-After: 3`; assert `sleep` called with `3`. |
| E6 | `test_429_without_retry_after_uses_backoff` | Falls back when no hint. | 429 with no `Retry-After` header; assert `sleep` called with the computed backoff delay (not 0). |

### F. Frontend trigger (4 cases; Vitest + Testing Library)

| # | Test name | Intent | Exercise / assert |
|---|---|---|---|
| F1 | `Export button role gate` (parametrized) | Members see it, viewers don't. | Render with current-user role `admin`/`member` → button "Export to Airtable" present; role `viewer` → `queryByRole('button', {name: /export/i})` is null. |
| F2 | `clicking Export calls the endpoint and shows result` | Wiring. | Mock `POST /api/projects/{id}/export` → `{exported: 3, created: 3, updated: 0, failed: []}`; click; assert the call and that "Exported 3 tasks" appears. |
| F3 | `Export shows partial-failure message` | Surfaces failures. | Mock response with `failed: [{...}]`; assert a "1 task failed" message and the button re-enables. |
| F4 | `Export surfaces a 503 when unconfigured` | Server says unavailable. | Mock 503 `{"error": "airtable not configured"}`; assert the error is shown (button stays visible, per Q9). |

Note: the button derives from the same `myRole` check already in `ProjectPage.tsx` (a `canExport = admin|member`, mirroring `canComment`) to avoid drift.

---

## 3. Real-integration verification (manual, not automated)

One-off check after implementation, run by a human:

1. Ensure `.env` has real `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME=Tasks` and the base's `Tasks` table has the mapped fields.
2. Log in as an admin, create a project with 3–5 tasks (one unassigned), call the endpoint once.
3. Confirm the response counts (`created == n`).
4. Read the rows back (Airtable MCP `list_records_for_table` or the Airtable UI); confirm one row per task with matching `Task ID` and `Title`.
5. Edit one task, export again; confirm `updated == n, created == 0` and the base row count is unchanged (idempotency).
6. Record the outcome in `TERMINAL_LOG.md`, never the API key.

Why manual, not CI: the real API is rate-limited (5 req/s per base), needs a secret that must not reach CI logs, writes persist in a shared base, and network latency makes results non-deterministic. All logic paths are covered deterministically by the fake; the manual run only proves credentials, field names, and `pyairtable` wiring.

---

## 4. Decisions (confirmed in review)

- **Q1 Response shape:** `{exported, created, updated, failed:[{taskId, reason}], total}`; the stub's `tasks` list is dropped (too large at 1000 tasks).
- **Q2 Store Airtable record id on Task:** No. `batch_upsert` keyed on `Task ID` needs no stored id and no lookup.
- **Q3 Sync vs async:** Synchronous, no queue/Celery/threads (user-confirmed). ~1000 tasks in one request.
- **Q4 Status field:** Send raw codes with `typecast=True`.
- **Q5 Who retries:** Own bounded loop; `Api(..., retry_strategy=False)` disables pyairtable's.
- **Q6 Update all vs changed:** Update every existing row each run (deterministic; no `Updated At` optimisation).
- **Q7 Partial-failure status:** 200 with a `failed` list.
- **Q8 Deleted-task orphans:** Out of scope; a re-export after a local delete succeeds and leaves the stale row in place (C6).
- **Q9 Missing config:** 503 `airtable not configured`; the frontend surfaces it rather than hiding the button.

Remaining to confirm at implementation time: the base's `Status` single-select choices must equal the four raw codes (or `typecast=True` must be allowed to create them); pin B2's expected `Status` value accordingly.
