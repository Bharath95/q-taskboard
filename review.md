# Code Review — Backend Bugs

Top findings from a security-focused review of the Django backend, ranked by severity.

## 1. SQL injection in task search

- **File / line:** `backend/projects/views.py:113`
- **Category:** Security
- **Severity:** Critical

**Description:** The `?q=` search parameter is interpolated into a raw SQL string using f-strings and executed directly via `cursor.execute`. Any authenticated project member can close the quote and append arbitrary SQL (e.g. `?q=%25' OR 1=1 --`), reading every task across all projects regardless of membership. Because psycopg2 allows multiple statements, this extends to writes and DDL against the whole database.

**Recommended fix:** Replace the raw query with the ORM: `Task.objects.filter(project_id=project_id).filter(Q(title__icontains=q) | Q(description__icontains=q))` serialized through `TaskSerializer`. At minimum, pass values as parameters to `cursor.execute` instead of formatting them into the string.

## 2. Task update has no authorization check

- **File / line:** `backend/projects/views.py:164`
- **Category:** Security
- **Severity:** Critical

**Description:** `TaskDetailView.patch` loads the task by ID and saves changes without calling `_get_membership` or `_can_edit_tasks`. Any logged-in user, including non-members and viewers, can rename, reassign, or change the status of any task in any project if they know its UUID. The sibling `delete` method performs both checks, so this is an omission.

**Recommended fix:** Mirror the `delete` method: load the task with `select_related('project')`, resolve membership on `task.project_id`, and return 403 for non-members and for the viewer role before applying any changes.

## 3. DEBUG on by default with wildcard ALLOWED_HOSTS

- **File / line:** `backend/taskboard/settings.py:8`
- **Category:** Security
- **Severity:** High

**Description:** `DEBUG` defaults to true unless the environment variable is explicitly set, and `ALLOWED_HOSTS` is `['*']`. Several code paths raise unhandled exceptions on malformed input, so an attacker can trigger Django's debug page and read the full traceback, settings, database credentials, and the secret key. The wildcard host list also enables host-header poisoning.

**Recommended fix:** Default `DEBUG` to false (`os.environ.get('DEBUG', 'false')`) and read `ALLOWED_HOSTS` from an environment variable with a restrictive default such as localhost.

## 4. Hardcoded fallback secret key signs JWTs

- **File / line:** `backend/taskboard/settings.py:7`
- **Category:** Security
- **Severity:** High

**Description:** `SECRET_KEY` falls back to the public literal `'dev-secret-change-me-in-production'`, and SimpleJWT signs access tokens with `SECRET_KEY` because no `SIGNING_KEY` is configured. Any deployment that forgets to set `DJANGO_SECRET_KEY` lets an attacker forge a valid token for any user UUID. The docker-compose file ships an equally public value.

**Recommended fix:** Raise `django.core.exceptions.ImproperlyConfigured` when `DJANGO_SECRET_KEY` is unset instead of falling back to a literal, and generate a unique key per environment.

---

## Bug 1 — Reproduction (SQL injection in task search)

Single copy-paste command. It logs in as `meera@taskboard.dev`, picks a project, fires the injection payload `x%') OR 1=1 --` into the `?q=` search, and reports whether tasks leaked from other projects. Use the **same command before and after the fix**.

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"meera@taskboard.dev","password":"password123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])') && PID=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/projects | python3 -c 'import sys,json;print(json.load(sys.stdin)["projects"][0]["id"])') && curl -s -G -H "Authorization: Bearer $TOKEN" --data-urlencode "q=x%') OR 1=1 --" "http://localhost:8000/api/projects/$PID/tasks" | python3 -c 'import sys,json;t=json.load(sys.stdin)["tasks"];p=set(x["project_id"] for x in t);print("SQLi returned",len(t),"tasks across",len(p),"projects ->","VULNERABLE (leaked other projects)" if len(p)>1 else "scoped to 1 project")'
```

**Output before fix (vulnerable):**

```
SQLi returned 12 tasks across 2 projects -> VULNERABLE (leaked other projects)
```

**Expected output after fix:** the payload is treated as a literal search string, so it matches nothing and stays within the queried project.

```
SQLi returned 0 tasks across 0 projects -> scoped to 1 project
```
