/**
 * Development seed (spec section 15): loads the content into the database and creates demo users.
 *   pnpm seed
 * Uses DATABASE_URL if set, otherwise the embedded PGlite database in .data/pglite.
 * Refuses to run in production: the demo passwords are public.
 */
import { resolve } from "node:path";
import { openDb } from "@allmaths/db";
import { loadStore, syncContent, upsertUserWithRole } from "@allmaths/server";

if (process.env.NODE_ENV === "production") {
  console.error("Refusing to seed demo users in production.");
  process.exit(1);
}

const root = resolve(import.meta.dirname, "..");
const url = process.env.DATABASE_URL || undefined;
const handle = await openDb({
  url,
  dataDir: url ? undefined : (process.env.PGLITE_DIR ?? resolve(root, ".data", "pglite")),
  migrationsFolder: resolve(root, "packages", "db", "drizzle"),
});

const store = loadStore(resolve(root, "content"));
const counts = await syncContent(handle.db, store);
console.log(`Content synced: ${counts.lessons} lessons, ${counts.sections} sections.`);

const demo = [
  { email: "student@allmaths.test", name: "Demo Student", role: "student" },
  { email: "instructor@allmaths.test", name: "Demo Instructor", role: "instructor" },
  { email: "admin@allmaths.test", name: "Demo Admin", role: "admin" },
] as const;
for (const u of demo) {
  await upsertUserWithRole(handle.db, { ...u, password: "demo-password-123" });
  console.log(`  ${u.role.padEnd(10)} ${u.email}  /  demo-password-123`);
}
await handle.close();
