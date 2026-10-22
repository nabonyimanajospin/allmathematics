import { defineConfig } from "vitest/config";

// The real-content tests compile every formula of every lesson with KaTeX.
export default defineConfig({
  test: { testTimeout: 60000, hookTimeout: 60000 },
});
