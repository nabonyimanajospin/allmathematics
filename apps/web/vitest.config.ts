import { defineConfig } from "vitest/config";
import { resolve } from "node:path";

export default defineConfig({
  resolve: { alias: { "@": resolve(import.meta.dirname, "src") } },
  test: { include: ["tests/**/*.test.ts"], environment: "node", env: { SCRYPT_N: "1024" }, testTimeout: 30000, hookTimeout: 60000 },
});
