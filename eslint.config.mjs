import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "**/node_modules/**",
      "**/.next/**",
      "**/.next-e2e/**",
      "**/dist/**",
      "**/drizzle/**",
      "**/.data/**",
      "**/test-results/**",
      "**/playwright-report/**",
      "apps/math-engine/**",
      "**/next-env.d.ts",
      "**/*.mjs",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      // spec 5.4: TypeScript strict, no `any`
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "@typescript-eslint/consistent-type-imports": ["error", { fixStyle: "inline-type-imports" }],
      "no-console": ["warn", { allow: ["warn", "error", "log"] }],
    },
  },
);
