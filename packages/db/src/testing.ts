import { resolve } from "node:path";
import { openDb, type DbHandle } from "./index";

export const migrationsFolder = resolve(import.meta.dirname, "..", "drizzle");

/** A fresh, migrated, in-memory PostgreSQL for one test file. */
export function openTestDb(): Promise<DbHandle> {
  return openDb({ migrationsFolder });
}
