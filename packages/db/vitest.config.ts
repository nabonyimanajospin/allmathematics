import { defineConfig } from "vitest/config";

// Opening the in-memory PostgreSQL (PGlite) and running the migrations takes several seconds on a busy machine.
export default defineConfig({
  test: { testTimeout: 30000, hookTimeout: 60000 },
});
