/**
 * Process-wide services: database, content store, math engine client, rate limiters.
 * Created once per server process (kept on globalThis so dev hot reloads reuse them).
 */

import { resolve } from "node:path";
import { createEngineClient, type EngineClient } from "@allmaths/core";
import { openDb, type DbHandle } from "@allmaths/db";
import {
  createMemoryRateLimiter,
  createReloadingStore,
  syncContent,
  type ContentStore,
  type RateLimiter,
} from "@allmaths/server";

export interface Services {
  db: DbHandle["db"];
  store: ContentStore;
  engine: EngineClient;
  limits: {
    signIn: RateLimiter;
    signInPerEmail: RateLimiter;
    signUp: RateLimiter;
    check: RateLimiter;
    hint: RateLimiter;
    events: RateLimiter;
    resetRequest: RateLimiter;
    resetRequestPerEmail: RateLimiter;
    resetVerify: RateLimiter;
    unitTest: RateLimiter;
    solver: RateLimiter;
    feedback: RateLimiter;
  };
}

interface Runtime {
  handle: DbHandle;
  getStore: () => ContentStore;
  engine: EngineClient;
  limits: Services["limits"];
  synced?: ContentStore;
  syncing?: Promise<void>;
}

const globalKey = Symbol.for("allmaths.runtime");
type Holder = typeof globalThis & { [globalKey]?: Promise<Runtime> };

function env(name: string): string | undefined {
  const v = process.env[name];
  return v && v.length > 0 ? v : undefined;
}

async function createRuntime(): Promise<Runtime> {
  const isProd = process.env.NODE_ENV === "production";
  const databaseUrl = env("DATABASE_URL");
  const engineToken = env("MATH_ENGINE_TOKEN") ?? "dev-engine-token";
  if (isProd && !databaseUrl) throw new Error("DATABASE_URL is required in production");
  if (isProd && engineToken === "dev-engine-token") throw new Error("MATH_ENGINE_TOKEN must be set in production");
  if (isProd && env("RATE_LIMIT_MULTIPLIER")) throw new Error("RATE_LIMIT_MULTIPLIER is for tests only");

  const root = resolve(process.cwd(), "..", "..");
  const handle = await openDb({
    url: databaseUrl,
    dataDir: databaseUrl ? undefined : (env("PGLITE_DIR") ?? resolve(root, ".data", "pglite")),
    migrationsFolder: env("MIGRATIONS_DIR") ?? resolve(root, "packages", "db", "drizzle"),
  });
  const getStore = createReloadingStore(env("CONTENT_DIR") ?? resolve(root, "content"), !isProd);
  const engine = createEngineClient({
    url: env("MATH_ENGINE_URL") ?? "http://127.0.0.1:8001",
    token: engineToken,
  });
  const MIN = 60_000;
  // Only for automated tests, which sign up many users from one address. Never set in production.
  const mult = Number(env("RATE_LIMIT_MULTIPLIER") ?? 1);
  const scale = (n: number): number => (Number.isFinite(mult) && mult >= 1 ? Math.round(n * mult) : n);
  return {
    handle,
    getStore,
    engine,
    limits: {
      signIn: createMemoryRateLimiter(scale(10), MIN),
      signInPerEmail: createMemoryRateLimiter(scale(6), 5 * MIN),
      signUp: createMemoryRateLimiter(scale(6), 10 * MIN),
      check: createMemoryRateLimiter(scale(90), MIN),
      hint: createMemoryRateLimiter(scale(40), MIN),
      events: createMemoryRateLimiter(scale(240), MIN),
      resetRequest: createMemoryRateLimiter(scale(10), 10 * MIN),
      resetRequestPerEmail: createMemoryRateLimiter(scale(3), 10 * MIN),
      resetVerify: createMemoryRateLimiter(scale(20), 10 * MIN),
      unitTest: createMemoryRateLimiter(scale(30), 60 * MIN),
      solver: createMemoryRateLimiter(scale(20), MIN),
      feedback: createMemoryRateLimiter(scale(5), 10 * MIN),
    },
  };
}

export async function getServices(): Promise<Services> {
  const holder = globalThis as Holder;
  if (!holder[globalKey]) {
    const starting = createRuntime();
    holder[globalKey] = starting;
    // a failed start (database down, bad config) must not be cached: the next request tries again
    starting.catch(() => {
      if (holder[globalKey] === starting) holder[globalKey] = undefined;
    });
  }
  const rt = await holder[globalKey];
  const store = rt.getStore();
  if (rt.synced !== store) {
    rt.syncing ??= syncContent(rt.handle.db, store)
      .then(() => {
        rt.synced = store;
      })
      .finally(() => {
        rt.syncing = undefined;
      });
    await rt.syncing;
  }
  return { db: rt.handle.db, store, engine: rt.engine, limits: rt.limits };
}
