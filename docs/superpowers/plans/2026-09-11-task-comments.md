# Task Comments (Part 3a) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every task a chronological, append-only comment thread that project members can post to and viewers can only read.

**Architecture:** A new `Comment` model (child of `Task`, author is a `User`) exposed through one DRF `APIView` at `/api/tasks/<id>/comments` supporting only GET (list) and POST (create). Append-only is enforced structurally: no update/delete route exists and the model has no mutable fields. The React `TaskDetail` modal gains a comment thread that hides the compose box from viewers.

**Tech Stack:** Django 5, Django REST Framework, PostgreSQL, SimpleJWT; React 18 + TypeScript + TanStack Query; pytest-django and Playwright for tests.

**Spec:** Part 3a requirements — comments listed chronologically showing author/body/time; members post, viewers read-only; append-only (no edit/delete); authorization enforced correctly.

## Global Constraints

- Roles are `admin | member | viewer` on `Membership.role`; "can post" = `admin` or `member` (reuse `_can_edit_tasks`).
- Read access requires membership on the task's project (non-members get 403); viewers may read.
- Response bodies are JSON, wrapped (`{"comments": [...]}`, `{"comment": {...}}`), timestamps camelCase `createdAt`, author nested `{id, email, name}`.
- All new DB tables use a UUID primary key and an explicit `db_table`, matching existing models.
- Tests are written first and must fail before implementation. The red tests already exist: `backend/projects/test_comments.py` and `e2e/comments.spec.ts`.

---

## Data model

Table `comments`:

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | `default=uuid4`, not editable |
| `task_id` | FK → `tasks.id` | `on_delete=CASCADE`, `related_name='comments'` |
| `author_id` | FK → `users.id` | `on_delete=SET_NULL`, `null=True`, `related_name='comments'` |
| `body` | TEXT | required, non-blank (validated in the view) |
| `created_at` | timestamptz | `auto_now_add=True` |

- **No `updated_at`, no edit flag.** The absence of mutable fields is the append-only guarantee at the schema level.
- **`author` is `SET_NULL`, deliberately not `CASCADE`.** Comments are an audit trail; removing a user must not erase what they wrote. A comment with a deleted author serializes `author: null`. (This is the opposite of the `Task.created_by` CASCADE bug found earlier, on purpose.)
- **`task` is `CASCADE`.** A comment cannot outlive its task.
- `Meta.ordering = ['created_at']` so every query is chronological by default; `Meta.indexes = [Index(fields=['task', 'created_at'])]` for thread fetches.

## API contract

### `GET /api/tasks/<uuid:task_id>/comments`
- 401 if unauthenticated.
- 404 if the task does not exist.
- 403 if the caller has no membership on the task's project.
- 200 for any member (viewers included):
  ```json
  { "comments": [
    { "id": "uuid", "body": "text", "author": { "id": "uuid", "email": "a@b.dev", "name": "A B" }, "createdAt": "2026-09-11T12:00:00Z" }
  ] }
  ```
  Oldest first. `author` may be `null` if the author was deleted.

### `POST /api/tasks/<uuid:task_id>/comments`
- 401 if unauthenticated.
- 404 if the task does not exist.
- 403 if the caller is not a member, or is a `viewer`.
- 400 if `body` is missing, not a string, or whitespace-only. Nothing is created.
- Author is always `request.user`; any `authorId`/`author` in the payload is ignored.
- 201:
  ```json
  { "comment": { "id": "uuid", "body": "text", "author": { "id": "uuid", "email": "a@b.dev", "name": "A B" }, "createdAt": "2026-09-11T12:00:00Z" } }
  ```

### Append-only enforcement
- No `PATCH`, `PUT`, or `DELETE` handler on the comments endpoint, so DRF returns **405 Method Not Allowed**. There is no per-comment URL at all.

---

## File Structure

- Create `backend/projects/` model + migration for `Comment` (modify `models.py`, new migration file).
- Modify `backend/projects/serializers.py` — add `CommentSerializer`.
- Modify `backend/projects/views.py` — add `CommentListCreateView`.
- Modify `backend/projects/urls.py` — add the comments route.
- Modify `frontend/src/types/index.ts` — add `ApiComment`.
- Modify `frontend/src/components/TaskDetail.tsx` — comment thread + compose box.
- Modify `frontend/src/pages/ProjectPage.tsx` — compute `canComment` and pass it to `TaskDetail`.
- Tests already present: `backend/projects/test_comments.py`, `e2e/comments.spec.ts`.

---

### Task 1: Comment model and migration

**Files:**
- Modify: `backend/projects/models.py`
- Create: `backend/projects/migrations/0002_comment.py` (via makemigrations)

**Interfaces:**
- Produces: `Comment` model with fields `id, task (FK Task, related_name='comments'), author (FK User, SET_NULL, null=True, related_name='comments'), body (TextField), created_at`; `Meta.db_table='comments'`, `ordering=['created_at']`, index on `('task','created_at')`.

- [ ] **Step 1: Write the failing test** (model behavior)

```python
# backend/projects/test_comments_model.py
import pytest
from users.models import User
from projects.models import Project, Task, Comment

@pytest.mark.django_db
def test_comment_belongs_to_task_and_author_and_orders_by_created():
    u = User.objects.create_user(email='a@b.dev', name='A', password='password123')
    p = Project.objects.create(name='P', owner=u)
    t = Task.objects.create(project=p, title='T', created_by=u)
    c1 = Comment.objects.create(task=t, author=u, body='first')
    c2 = Comment.objects.create(task=t, author=u, body='second')
    assert list(t.comments.values_list('body', flat=True)) == ['first', 'second']
    assert c1.created_at <= c2.created_at

@pytest.mark.django_db
def test_deleting_author_keeps_comment_with_null_author():
    u = User.objects.create_user(email='a@b.dev', name='A', password='password123')
    p = Project.objects.create(name='P', owner=u)
    t = Task.objects.create(project=p, title='T', created_by=u)
    keeper = User.objects.create_user(email='k@b.dev', name='K', password='password123')
    c = Comment.objects.create(task=t, author=keeper, body='kept')
    keeper.delete()
    c.refresh_from_db()
    assert c.author_id is None
    assert c.body == 'kept'
```

- [ ] **Step 2: Run to verify it fails**

Run: `docker compose exec -T backend python -m pytest projects/test_comments_model.py -v`
Expected: FAIL — `ImportError: cannot import name 'Comment'`.

- [ ] **Step 3: Implement the model**

```python
# append to backend/projects/models.py
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [models.Index(fields=['task', 'created_at'])]
```

- [ ] **Step 4: Make and apply the migration, then run tests**

Run:
```bash
docker compose exec -T backend python manage.py makemigrations projects
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python -m pytest projects/test_comments_model.py -v
```
Expected: migration `0002_comment` created and applied; both tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/projects/models.py backend/projects/migrations/0002_comment.py backend/projects/test_comments_model.py
git commit -m "feat: add Comment model for task comment threads"
```

---

### Task 2: Comment serializer, view, and route (backend API)

**Files:**
- Modify: `backend/projects/serializers.py`
- Modify: `backend/projects/views.py`
- Modify: `backend/projects/urls.py`
- Test (already red): `backend/projects/test_comments.py`

**Interfaces:**
- Consumes: `Comment` model (Task 1); helpers `_get_membership(user, project_id)`, `_can_edit_tasks(role)` in `views.py`.
- Produces: `CommentSerializer` (fields `id, body, author (UserSerializer, read_only), createdAt (source=created_at)`); `CommentListCreateView` with `get`/`post`; route `path('tasks/<uuid:task_id>/comments', CommentListCreateView.as_view())`.

- [ ] **Step 1: Confirm the pre-written tests are red**

Run: `docker compose exec -T backend python -m pytest projects/test_comments.py -v`
Expected: the read/post/role/validation tests FAIL (route returns 404). 405/404-only assertions may already pass.

- [ ] **Step 2: Add the serializer**

```python
# backend/projects/serializers.py
from .models import Project, Membership, Task, Comment  # extend existing import

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'createdAt']
```

- [ ] **Step 3: Add the view**

```python
# backend/projects/views.py
from .models import Project, Membership, Task, Comment  # extend existing import
from .serializers import ProjectDetailSerializer, TaskSerializer, CommentSerializer  # extend

class CommentListCreateView(APIView):
    def _task_or_none(self, task_id):
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_id):
        task = self._task_or_none(task_id)
        if task is None:
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        membership = _get_membership(request.user, task.project_id)
        if not membership:
            return Response({'error': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)
        comments = task.comments.select_related('author').order_by('created_at')
        return Response({'comments': CommentSerializer(comments, many=True).data})

    def post(self, request, task_id):
        task = self._task_or_none(task_id)
        if task is None:
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        membership = _get_membership(request.user, task.project_id)
        if not membership:
            return Response({'error': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if not _can_edit_tasks(membership.role):
            return Response({'error': 'viewers cannot post comments'}, status=status.HTTP_403_FORBIDDEN)
        body = request.data.get('body')
        if not isinstance(body, str) or not body.strip():
            return Response({'error': 'comment body is required'}, status=status.HTTP_400_BAD_REQUEST)
        comment = Comment.objects.create(task=task, author=request.user, body=body.strip())
        data = CommentSerializer(Comment.objects.select_related('author').get(id=comment.id)).data
        return Response({'comment': data}, status=status.HTTP_201_CREATED)
```

- [ ] **Step 4: Add the route**

```python
# backend/projects/urls.py
from .views import (
    ProjectListCreateView, ProjectDetailView, TaskListCreateView,
    TaskDetailView, ExportView, MemberAddView, CommentListCreateView,
)
# add to urlpatterns:
path('tasks/<uuid:task_id>/comments', CommentListCreateView.as_view()),
```

- [ ] **Step 5: Run the comment API tests and the full suite**

Run:
```bash
docker compose exec -T backend python -m pytest projects/test_comments.py -v
docker compose exec -T backend python -m pytest -q
```
Expected: all `test_comments.py` tests PASS; full suite green. If `test_unauthenticated_request_is_rejected` sees 403 instead of 401, confirm SimpleJWT's actual code for a missing token and align the test to DRF's real behavior (do not weaken the auth).

- [ ] **Step 6: Commit**

```bash
git add backend/projects/serializers.py backend/projects/views.py backend/projects/urls.py
git commit -m "feat: add task comments list/create API (members post, viewers read-only, append-only)"
```

---

### Task 3: Comment thread UI in TaskDetail (frontend + E2E)

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/components/TaskDetail.tsx`
- Modify: `frontend/src/pages/ProjectPage.tsx`
- Test (already red): `e2e/comments.spec.ts`

**Interfaces:**
- Consumes: `apiFetch`, `getStoredUser` from `@/lib/api-client`; `GET/POST /api/tasks/:id/comments` (Task 2).
- Produces: `ApiComment` type; a comment thread rendered in `TaskDetail` with these exact test hooks the E2E targets — `data-testid="comment-list"`, `data-testid="comment-item"` per comment, `data-testid="comment-input"` on the textarea, `data-testid="comment-timestamp"` on each comment's time element, and a submit button whose accessible name matches `/post|comment/i`. Each item shows author name and `createdAt`. Compose box renders only when `canComment` is true.

- [ ] **Step 1: Add the type**

```typescript
// frontend/src/types/index.ts
export type ApiComment = {
  id: string;
  body: string;
  author: ApiUser | null;
  createdAt: string;
};
```

- [ ] **Step 2: Compute canComment and pass it down**

```tsx
// frontend/src/pages/ProjectPage.tsx
import { apiFetch, getToken, getStoredUser } from "@/lib/api-client";
// after `const project = data?.project;`
const me = getStoredUser();
const myRole = project?.memberships.find((m) => m.user.id === me?.id)?.role;
const canComment = myRole === "admin" || myRole === "member";
// in the TaskDetail usage, add:  canComment={canComment}
```

- [ ] **Step 3: Render the thread in TaskDetail**

Add `canComment: boolean` to `Props`. Inside the modal body add:

```tsx
const { data: commentsData } = useQuery({
  queryKey: ["task", task.id, "comments"],
  queryFn: () => apiFetch<{ comments: ApiComment[] }>(`/api/tasks/${task.id}/comments`),
});
const [commentBody, setCommentBody] = useState("");
const postComment = useMutation({
  mutationFn: (body: string) =>
    apiFetch<{ comment: ApiComment }>(`/api/tasks/${task.id}/comments`, {
      method: "POST",
      body: JSON.stringify({ body }),
    }),
  onSuccess: () => {
    setCommentBody("");
    queryClient.invalidateQueries({ queryKey: ["task", task.id, "comments"] });
  },
});
```

```tsx
<section className="mt-6">
  <h3 className="text-sm font-medium mb-2">Comments</h3>
  <ul data-testid="comment-list" className="space-y-2">
    {(commentsData?.comments ?? []).map((c) => (
      <li key={c.id} data-testid="comment-item" className="text-sm border border-border rounded p-2">
        <div className="flex justify-between text-xs text-muted">
          <span>{c.author?.name ?? "unknown"}</span>
          <time data-testid="comment-timestamp" dateTime={c.createdAt}>{new Date(c.createdAt).toLocaleString()}</time>
        </div>
        <p className="mt-1 whitespace-pre-wrap">{c.body}</p>
      </li>
    ))}
  </ul>
  {canComment && (
    <form
      className="mt-3 flex gap-2"
      onSubmit={(e) => {
        e.preventDefault();
        if (!commentBody.trim()) return;
        postComment.mutate(commentBody.trim());
      }}
    >
      <textarea
        data-testid="comment-input"
        value={commentBody}
        onChange={(e) => setCommentBody(e.target.value)}
        placeholder="add a comment"
        className="flex-1 rounded-md bg-bg border border-border px-3 py-2 text-sm"
      />
      <button type="submit" disabled={postComment.isPending}
        className="bg-accent text-white text-sm font-medium rounded-md px-4 disabled:opacity-50">
        Post comment
      </button>
    </form>
  )}
</section>
```

No edit or delete control is rendered on a comment item — append-only in the UI.

- [ ] **Step 4: Run the frontend unit tests, then the E2E**

Run:
```bash
docker compose exec -T frontend npm test -- --run
cd e2e && npx playwright test --reporter=list
```
Expected: existing vitest suite still green; `comment thread flow` E2E PASSES end to end (member posts two comments in order, no edit/delete control, viewer sees comments with no compose box).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/components/TaskDetail.tsx frontend/src/pages/ProjectPage.tsx
git commit -m "feat: task comment thread UI with viewer read-only gating"
```

---

## Self-review

- **Chronological listing:** Task 1 `Meta.ordering` + Task 2 `order_by('created_at')` + Task 3 render order. Covered.
- **Author/body/time shown:** `CommentSerializer` fields + Task 3 item markup. Covered.
- **Members post, viewers read:** Task 2 `_can_edit_tasks` gate (403) + Task 3 `canComment`. Covered by `test_role_can_or_cannot_post` and the E2E viewer step.
- **Append-only:** no mutable fields (Task 1), no update/delete route → 405 (Task 2), no edit/delete UI (Task 3). Covered by `test_comment_cannot_be_edited/deleted`.
- **Authorization correct:** 401/403/404 paths in Task 2. Covered by the non-member and unauthenticated tests.
- **Type consistency:** `createdAt`, `author {id,email,name}`, wrapped `{comments}`/`{comment}` used identically in serializer, tests, and frontend type.
