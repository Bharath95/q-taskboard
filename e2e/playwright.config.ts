import { defineConfig, devices } from "@playwright/test";

// Isolated E2E config. The app is already running via Docker:
//   frontend http://localhost:3000, backend http://localhost:8000.
// No webServer here — we run against the already-up app.
export default defineConfig({
  testDir: ".",
  fullyParallel: false,
  forbidOnly: false,
  retries: 0,
  workers: 1,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:3000",
    headless: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
