import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import type { ApiProjectDetail, Role } from "@/types";

// The Export-to-Airtable trigger lives on ProjectPage, gated by the same
// myRole check as comments (canExport = admin | member). These tests SHOULD
// FAIL red until that button + wiring exist.
import * as apiClient from "@/lib/api-client";
import ProjectPage from "@/pages/ProjectPage";

const PROJECT_ID = "p_1";
const ME = { id: "u_me", email: "me@taskboard.dev", name: "Me" };

vi.mock("@/lib/api-client", () => ({
  apiFetch: vi.fn(),
  getToken: () => "test-token",
  getStoredUser: () => ({ id: "u_me", email: "me@taskboard.dev", name: "Me" }),
}));

const apiFetch = apiClient.apiFetch as unknown as ReturnType<typeof vi.fn>;

function buildDetail(role: Role): ApiProjectDetail {
  const now = new Date().toISOString();
  return {
    id: PROJECT_ID,
    name: "Export Project",
    description: null,
    ownerId: ME.id,
    owner: ME,
    memberships: [{ id: "m_1", role, user: ME }],
    tasks: [
      {
        id: "t_1",
        projectId: PROJECT_ID,
        title: "First task",
        description: null,
        status: "todo",
        assigneeId: null,
        createdById: ME.id,
        position: 0,
        createdAt: now,
        updatedAt: now,
        assignee: null,
      },
    ],
    createdAt: now,
    updatedAt: now,
  };
}

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/projects/${PROJECT_ID}`]}>
        <Routes>
          <Route path="/projects/:id" element={<ProjectPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function mockDetail(role: Role) {
  apiFetch.mockImplementation((path: string) => {
    if (path === `/api/projects/${PROJECT_ID}`) {
      return Promise.resolve({ project: buildDetail(role) });
    }
    return Promise.reject(new Error(`unexpected path ${path}`));
  });
}

const exportButton = () =>
  screen.queryByRole("button", { name: /export to airtable/i });

describe("Export to Airtable button", () => {
  beforeEach(() => {
    apiFetch.mockReset();
  });

  // F1 — role gate
  it.each<[Role, boolean]>([
    ["admin", true],
    ["member", true],
    ["viewer", false],
  ])("role %s sees the export button: %s", async (role, visible) => {
    mockDetail(role);
    renderPage();
    await screen.findByText("Export Project");

    if (visible) {
      expect(exportButton()).toBeInTheDocument();
    } else {
      expect(exportButton()).toBeNull();
    }
  });

  // F2 — wiring: clicking calls the endpoint and shows the result
  it("clicking Export calls the endpoint and shows the result", async () => {
    apiFetch.mockImplementation((path: string, opts?: RequestInit) => {
      if (path === `/api/projects/${PROJECT_ID}` && opts?.method !== "POST") {
        return Promise.resolve({ project: buildDetail("admin") });
      }
      if (path === `/api/projects/${PROJECT_ID}/export`) {
        return Promise.resolve({ exported: 3, created: 3, updated: 0, failed: [] });
      }
      return Promise.reject(new Error(`unexpected path ${path}`));
    });
    renderPage();
    await screen.findByText("Export Project");

    const btn = await screen.findByRole("button", { name: /export to airtable/i });
    fireEvent.click(btn);

    await waitFor(() => {
      expect(apiFetch).toHaveBeenCalledWith(
        `/api/projects/${PROJECT_ID}/export`,
        expect.objectContaining({ method: "POST" }),
      );
    });
    expect(await screen.findByText(/exported 3 tasks/i)).toBeInTheDocument();
  });

  // F3 — partial failure surfaced; button re-enables
  it("shows a partial-failure message and re-enables the button", async () => {
    apiFetch.mockImplementation((path: string, opts?: RequestInit) => {
      if (path === `/api/projects/${PROJECT_ID}` && opts?.method !== "POST") {
        return Promise.resolve({ project: buildDetail("admin") });
      }
      if (path === `/api/projects/${PROJECT_ID}/export`) {
        return Promise.resolve({
          exported: 2,
          created: 2,
          updated: 0,
          failed: [{ taskId: "t_9", reason: "422 INVALID_VALUE_FOR_COLUMN" }],
          total: 3,
        });
      }
      return Promise.reject(new Error(`unexpected path ${path}`));
    });
    renderPage();
    await screen.findByText("Export Project");

    const btn = await screen.findByRole("button", { name: /export to airtable/i });
    fireEvent.click(btn);

    expect(await screen.findByText(/1 task failed/i)).toBeInTheDocument();
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: /export to airtable/i }),
      ).not.toBeDisabled(),
    );
  });

  // F4 — 503 when Airtable is not configured
  it("surfaces a 503 when Airtable is unconfigured", async () => {
    apiFetch.mockImplementation((path: string, opts?: RequestInit) => {
      if (path === `/api/projects/${PROJECT_ID}` && opts?.method !== "POST") {
        return Promise.resolve({ project: buildDetail("admin") });
      }
      if (path === `/api/projects/${PROJECT_ID}/export`) {
        return Promise.reject(new Error("airtable not configured"));
      }
      return Promise.reject(new Error(`unexpected path ${path}`));
    });
    renderPage();
    await screen.findByText("Export Project");

    const btn = await screen.findByRole("button", { name: /export to airtable/i });
    fireEvent.click(btn);

    expect(await screen.findByText(/airtable not configured/i)).toBeInTheDocument();
    // Per Q9 the button stays visible so the user can retry after fixing config.
    expect(
      screen.getByRole("button", { name: /export to airtable/i }),
    ).toBeInTheDocument();
  });
});
