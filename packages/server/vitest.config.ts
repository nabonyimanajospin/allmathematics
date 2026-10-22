import { defineConfig } from "vitest/config";

export default defineConfig({
  test: { env: { SCRYPT_N: "1024" }, testTimeout: 30000, hookTimeout: 60000 },
});
