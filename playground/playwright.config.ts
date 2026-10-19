import { defineConfig, devices } from "@playwright/test";

// Tests the production build: the Pyodide worker is bundled differently in dev.
export default defineConfig({
  testDir: "./tests/e2e",
  // First boot downloads Python, pandas and pydantic from jsDelivr and PyPI.
  timeout: 180_000,
  expect: { timeout: 120_000 },
  fullyParallel: false,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:10012", trace: "retain-on-failure" },
  webServer: {
    command: "vp build && vp preview --host 127.0.0.1 --port 10012 --strictPort",
    url: "http://127.0.0.1:10012",
    reuseExistingServer: false,
    timeout: 120_000,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-chromium", use: { ...devices["Pixel 7"] } },
  ],
});
