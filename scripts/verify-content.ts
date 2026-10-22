/**
 * Content verification pipeline (spec 7.4). Exit code 0 only if every check passes.
 *   pnpm verify-content                 static checks + math engine checks
 *   pnpm verify-content -- --static     static checks only (no engine needed)
 * Environment: MATH_ENGINE_URL (default http://127.0.0.1:8001), MATH_ENGINE_TOKEN.
 */
import { resolve } from "node:path";
import { createEngineClient } from "@allmaths/core";
import {
  allLessons,
  loadContent,
  verifyLessonStatic,
  verifyLessonWithEngine,
  type ContentIssue,
} from "@allmaths/content-schema";

const contentDir = resolve(import.meta.dirname, "..", "content");
const staticOnly = process.argv.includes("--static");

async function main(): Promise<number> {
  const tree = loadContent(contentDir);
  const issues: ContentIssue[] = [...tree.issues];
  const lessons = allLessons(tree);
  console.log(`Loaded ${tree.courses.length} course(s), ${lessons.length} lesson(s) from ${contentDir}`);

  for (const l of lessons) issues.push(...verifyLessonStatic(l.meta, l.file));

  if (!staticOnly) {
    const engine = createEngineClient({
      url: process.env.MATH_ENGINE_URL ?? "http://127.0.0.1:8001",
      token: process.env.MATH_ENGINE_TOKEN ?? "dev-engine-token",
    });
    if (!(await engine.health())) {
      console.error("The math engine is not reachable. Start it (see docs/running.md) or use --static.");
      return 2;
    }
    for (const l of lessons) issues.push(...(await verifyLessonWithEngine(l.meta, l.file, engine)));
  }

  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");
  for (const i of issues) {
    console.log(`${i.severity === "error" ? "ERROR  " : "warning"} ${i.file}\n        ${i.message}`);
  }
  console.log(`\n${lessons.length} lesson(s): ${errors.length} error(s), ${warnings.length} warning(s)${staticOnly ? " (static only)" : ""}`);
  return errors.length === 0 ? 0 : 1;
}

main().then(
  (code) => process.exit(code),
  (e) => {
    console.error(e);
    process.exit(2);
  },
);
