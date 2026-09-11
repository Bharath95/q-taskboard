# q-taskboard

## Running with Docker

- Use `docker compose` (v2 plugin syntax). The README's `docker-compose` hyphenated form is not installed here.
- Start: `docker compose up --build -d`, then `docker compose exec backend python manage.py migrate` and `... seed`.
- Seed is idempotent-ish for dev: creates 5 users, 3 projects, 8 memberships, 12 tasks. Password for all users is `password123`.
- Frontend: http://localhost:3000, backend: http://localhost:8000, Postgres on host port 5432.

## API gotchas

- Login (`POST /api/auth/login`) returns `{"user": {...}, "token": "..."}`. The JWT key is `token`, not `access`.
- `GET /api/projects` returns `{"projects": [...]}`, not a bare list.
- DB table names are `users`, `projects`, `memberships`, `tasks` (custom `db_table`), not Django defaults like `users_user`.

## Logging

- `TERMINAL_LOG.md` at repo root holds the captured shell output for the setup session. Append new sessions rather than overwriting.

## Terminal logging (mandatory)

- Every shell command run in this repo, by the main agent or any subagent, must be appended to `TERMINAL_LOG.md` at the repo root.
- Format: `$ <command>` on its own line, then the full stdout/stderr, then `[exit <code>]` and a blank line. Keep it inside the single ```text fence at the end of the file.
- Use this wrapper for each command so nothing is missed:
  `run(){ { echo "\$ $*"; eval "$@"; echo "[exit $?]"; echo; } 2>&1 | tee -a TERMINAL_LOG.md; }`
- Subagents write to the same file. Each subagent prefixes its first entry with `# subagent: <name> — <task>` so its output is attributable.
- Never log secrets. Do not `cat .env` or print API keys into the log. Truncate tokens.
- Never overwrite or truncate `TERMINAL_LOG.md`. Append only.
- Failed commands stay in the log. Do not delete them; retry after them.

## Context management

- When context usage reaches 55%, compact before continuing. This applies to the main agent and every subagent.
- Before compacting, make sure `TERMINAL_LOG.md` and `CLAUDE.md` are up to date so nothing is lost.

## Model and subagent policy

- The main agent runs on Fable and acts as orchestrator: plan, delegate, review, and integrate.
- Delegate implementation, research, and test runs to Opus subagents (`model: "opus"`) to save tokens. Give each subagent a narrow, self-contained task with the logging rules above.
- If an Opus subagent fails, stalls, or runs longer than expected, spawn a Fable agent (`model: "fable"`) to resolve that specific issue directly instead of retrying Opus.
- Subagents report results back concisely. The orchestrator verifies claims (run the command, read the output) before treating a task as done.
