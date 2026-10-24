import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.E2E_PORT ?? 3000);
const ENGINE_PORT = Number(process.env.E2E_ENGINE_PORT ?? 8001);
const engineToken = process.env.MATH_ENGINE_TOKEN ?? "dev-engine-token";

export default defineConfig({
  testDir: "./e2e",
  timeout: 120_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  use: { baseURL: `http://localhost:${PORT}`, trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "phone", use: { ...devices["Pixel 5"] } },
  ],
  // Reuses servers that are already running (local development); starts them otherwise (CI).
  webServer: [
    {
      command: `python -m uvicorn allmaths_engine.main:app --host 127.0.0.1 --port ${ENGINE_PORT}`,
      cwd: "../math-engine",
      url: `http://127.0.0.1:${ENGINE_PORT}/health`,
      reuseExistingServer: true,
      env: { ENGINE_TOKEN: engineToken },
      timeout: 60_000,
    },
    {
      command: `pnpm exec next dev -p ${PORT}`,
      url: `http://localhost:${PORT}`,
      reuseExistingServer: true,
      env: { MATH_ENGINE_TOKEN: engineToken, MATH_ENGINE_URL: `http://127.0.0.1:${ENGINE_PORT}`, RATE_LIMIT_MULTIPLIER: "100", ADMIN_EMAILS: "e2e-admin@example.com" },
      // the first request compiles the app and loads all the lessons, which takes a while on a cold start
      timeout: 300_000,
    },
  ],
});
