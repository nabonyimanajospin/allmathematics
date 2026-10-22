/**
 * Database access. Production and CI use PostgreSQL (DATABASE_URL). Local development and tests can use
 * PGlite, a real PostgreSQL running inside Node, so nothing needs to be installed (no Docker).
 */

import { mkdirSync } from "node:fs";
import { PGlite } from "@electric-sql/pglite";
import type { PgDatabase, PgQueryResultHKT } from "drizzle-orm/pg-core";
import { drizzle as drizzlePglite } from "drizzle-orm/pglite";
import { migrate as migratePglite } from "drizzle-orm/pglite/migrator";
import { drizzle as drizzlePg } from "drizzle-orm/node-postgres";
import { migrate as migratePg } from "drizzle-orm/node-postgres/migrator";
import pg from "pg";
import * as schema from "./schema";

export * as schema from "./schema";
export type { Role } from "./schema";
export { ROLES } from "./schema";

export type AppDb = PgDatabase<PgQueryResultHKT, typeof schema>;

export interface DbHandle {
  db: AppDb;
  kind: "postgres" | "pglite";
  close(): Promise<void>;
}

export interface OpenOptions {
  /** PostgreSQL connection string. If empty, PGlite is used. */
  url?: string | undefined;
  /** PGlite data directory; omitted = in-memory (tests). */
  dataDir?: string | undefined;
  /** Folder with the SQL migrations. */
  migrationsFolder: string;
  /** Run pending migrations on open. */
  migrate?: boolean;
}

export async function openDb(opts: OpenOptions): Promise<DbHandle> {
  const run = opts.migrate ?? true;
  if (opts.url) {
    const pool = new pg.Pool({ connectionString: opts.url, max: 10 });
    const db = drizzlePg(pool, { schema });
    if (run) await migratePg(db, { migrationsFolder: opts.migrationsFolder });
    return { db, kind: "postgres", close: () => pool.end() };
  }
  if (opts.dataDir) mkdirSync(opts.dataDir, { recursive: true });
  const client = opts.dataDir ? new PGlite(opts.dataDir) : new PGlite();
  const db = drizzlePglite(client, { schema });
  if (run) await migratePglite(db, { migrationsFolder: opts.migrationsFolder });
  return { db, kind: "pglite", close: () => client.close() };
}
