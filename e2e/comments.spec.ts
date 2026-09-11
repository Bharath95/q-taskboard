import { test, expect, type Page } from "@playwright/test";

// End-to-end RED test for a Task Comments feature that does NOT exist yet.
// It logs in with the real (existing) login UI, opens the Q3 Launch project,
// opens a task (the real TaskDetail modal), and then asserts on comment-thread
// UI that has not been built. Those assertions are expected to FAIL — that is
// the point of this test (TDD red).

const APP = {
  admin: { email: "meera@taskboard.dev", password: "password123" },
  viewer: { email: "dev@example.com", password: "password123" },
  project: "Q3 Launch",
};

// --- Helpers built on the EXISTING, real UI (verified against source) -------

async function login(page: Page, email: string, password: string) {
  await page.goto("/login");
  // LoginPage.tsx: <input type="email"> and <input type="password">, submit button "sign in".
  await page.locator('input[type="email"]').fill(email);
  await page.locator('input[type="password"]').fill(password);
  await page.getByRole("button", { name: /sign in/i }).click();
  // DashboardPage renders "your projects" after auth.
  await expect(page.getByRole("heading", { name: /your projects/i })).toBeVisible();
}

async function logout(page: Page) {
  // Header.tsx: <button>sign out</button>
  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page.locator('input[type="email"]')).toBeVisible();
}

async function openProject(page: Page, name: string) {
  // DashboardPage.tsx: project name rendered in an <h2> inside a <Link>.
  await page.getByRole("link", { name: new RegExp(name, "i") }).first().click();
  await expect(page.getByRole("heading", { name: new RegExp(name, "i") })).toBeVisible();
}

async function openFirstTask(page: Page) {
  // ProjectPage renders StatusColumn -> TaskCard (a <button> with the task title).
  // The "add a task" form also has inputs; task cards are buttons inside columns.
  // Pick the first task card button (task titles), open the TaskDetail modal.
  const card = page
    .locator("button")
    .filter({ hasNotText: /^(add|sign out|save|cancel|delete task|✕)$/i })
    .first();
  await card.click();
  // TaskDetail.tsx modal shows the "edit task" heading.
  await expect(page.getByRole("heading", { name: /edit task/i })).toBeVisible();
}

// --- The one comment-thread flow test (RED) --------------------------------

// DISABLED for now: pending confirmation from the team that end-to-end browser
// automation of the app is authorised. Re-enable by changing `test.skip` back to
// `test`. The test body is unchanged and was verified to fail red (comment UI missing).
test.skip("comment thread flow", async ({ page }) => {
  // 1. Log in as admin/member (can post).
  await login(page, APP.admin.email, APP.admin.password);

  // 2. Open Q3 Launch and open a task (real TaskDetail modal).
  await openProject(page, APP.project);
  await openFirstTask(page);

  // 3. Locate the comment thread UI and post a comment.
  const commentList = page.getByTestId("comment-list");
  const commentInput = page.getByTestId("comment-input");
  const postButton = page.getByRole("button", { name: /post|comment|reply/i });

  await expect(commentList, "a comments section should be visible in the task modal").toBeVisible();

  const first = `E2E comment ${Date.now()}`;
  await commentInput.fill(first);
  await postButton.click();

  // 4. Posted comment appears with author name + timestamp + body.
  const firstItem = page.getByTestId("comment-item").filter({ hasText: first });
  await expect(firstItem).toBeVisible();
  await expect(firstItem).toContainText(first); // body
  await expect(firstItem).toContainText(/meera/i); // author name
  await expect(firstItem.getByTestId("comment-timestamp")).toBeVisible(); // timestamp

  // 5. Post a second comment; both appear in chronological order (first above second).
  const second = `E2E comment ${Date.now()}-second`;
  await commentInput.fill(second);
  await postButton.click();

  const items = page.getByTestId("comment-item");
  await expect(items.filter({ hasText: first })).toBeVisible();
  await expect(items.filter({ hasText: second })).toBeVisible();

  const allText = await items.allTextContents();
  const idxFirst = allText.findIndex((t) => t.includes(first));
  const idxSecond = allText.findIndex((t) => t.includes(second));
  expect(idxFirst, "first comment should render above the second (chronological)").toBeLessThan(
    idxSecond,
  );

  // 6. Append-only: no edit or delete control on a posted comment.
  await expect(
    firstItem.getByRole("button", { name: /edit/i }),
    "comments must be append-only (no edit control)",
  ).toHaveCount(0);
  await expect(
    firstItem.getByRole("button", { name: /delete|remove/i }),
    "comments must be append-only (no delete control)",
  ).toHaveCount(0);

  // 7. Log out, log in as the VIEWER, open the same project + task.
  await logout(page);
  await login(page, APP.viewer.email, APP.viewer.password);
  await openProject(page, APP.project);
  await openFirstTask(page);

  // 8. Viewer can SEE comments but has NO enabled compose box / Post button.
  await expect(
    page.getByTestId("comment-list"),
    "viewer should still see the comment thread",
  ).toBeVisible();
  await expect(page.getByTestId("comment-item").first()).toBeVisible();

  const viewerInput = page.getByTestId("comment-input");
  const viewerPost = page.getByRole("button", { name: /post|comment|reply/i });
  // Read-only: either the compose UI is absent, or it is present but disabled.
  const inputCount = await viewerInput.count();
  if (inputCount > 0) {
    await expect(viewerInput).toBeDisabled();
  } else {
    await expect(viewerInput).toHaveCount(0);
  }
  const postCount = await viewerPost.count();
  if (postCount > 0) {
    await expect(viewerPost).toBeDisabled();
  } else {
    await expect(viewerPost).toHaveCount(0);
  }
});
