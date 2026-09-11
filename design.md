# Design Notes

Design decisions for Part 3a (Task Comments) and Part 3b (Activity Feed).

## Part 3a — Task Comments (implemented)

**What was built:** a chronological, append-only comment thread on each task, at
`GET/POST /api/tasks/<id>/comments`, with a thread UI in the task detail modal.

**Key decisions and why:**

- **Append-only enforced structurally, not by a rule.** The `Comment` model has no
  `updated_at` and no edit flag, and the API exposes only `GET` and `POST` on a single
  collection URL with no per-comment route. Any `PATCH`/`PUT`/`DELETE` therefore returns
  `405 Method Not Allowed`. Making "cannot edit or delete" a property of the schema and
  routing is stronger than enforcing it in view logic that a later change could bypass.

- **`author` is `on_delete=SET_NULL`, deliberately not `CASCADE`.** Comments are part of
  the engagement audit trail, so deleting a user must never erase what they wrote; such a
  comment serializes `author: null` but keeps its body and timestamp. This is intentionally
  the opposite of the `Task.created_by` CASCADE we found and flagged earlier, because the
  audit-trail requirement changes the right answer.

- **Authorization is checked on every request against the task's project membership.**
  Read requires membership (non-members get `403`, viewers may read). Posting requires the
  `admin` or `member` role (viewers get `403`), reusing the existing `_can_edit_tasks`
  helper so comments and tasks share one rule. Unauthenticated requests return `401`.

- **Author is always the authenticated user.** Any `authorId` in the request body is
  ignored, so the author field cannot be spoofed. Empty or whitespace-only bodies return
  `400` and create nothing.

- **Response shape matches the rest of the API:** wrapped `{"comments": [...]}`, nested
  `author {id, email, name}`, camelCase `createdAt`, ordered oldest-first so the thread
  reads top to bottom.

## Part 3b — Activity Feed (deferred, design only)

Not implemented due to time constraints; this records the intended design so it can be
picked up later. Scope per the brief: every meaningful change (task created, status
changed, assignee changed, comment added) leaves an audit record, and the project detail
page shows a chronological, member-only feed, most recent first.

**Planned shape:**

- **Model `Activity`:** `project` (FK, CASCADE), `actor` (FK to user, `SET_NULL` for the
  same audit-trail reason as comments), `action` (enum: `task_created`,
  `status_changed`, `assignee_changed`, `comment_added`), a nullable `task` reference, a
  small JSON `metadata` field (e.g. old/new status), and `created_at`. Index and default
  ordering on `(project, -created_at)` so the feed query is cheap and pre-sorted.
- **API:** `GET /api/projects/<id>/activity`, membership required (`403` for non-members,
  `401` unauthenticated), returning `{"activity": [...]}` most-recent-first. Write-only
  internally — activity rows are produced as a side effect of the operations above, never
  via a public write endpoint.
- **Where records are written:** at each mutation site (task create, task `PATCH` when
  status or assignee changes, comment create), emitting one `Activity` row describing who
  did what.

**Decision — if the activity write fails, the original change rolls back.**

We will wrap the mutation and its activity write together in `transaction.atomic()`, so a
failure to record the activity rolls back the underlying change. The brief states the audit
trail is part of the engagement and matters to project stakeholders, which makes a change
that silently went unrecorded worse than a change that failed loudly and can be retried.
If the audit trail were not important, the better choice would be the opposite: never block
the primary operation on audit capture, and instead log the failure so it can be
reconciled later — but that trade-off is wrong here given the stated importance of the
record.
