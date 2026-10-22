/**
 * Sliding-window rate limiter. In-memory implementation (one process). The interface is small on purpose:
 * Phase 5 swaps in a Redis-backed implementation without touching callers.
 */

export interface RateLimitResult {
  allowed: boolean;
  retryAfterMs: number;
}

export interface RateLimiter {
  hit(key: string, now?: number): RateLimitResult;
  reset(key: string): void;
}

export function createMemoryRateLimiter(limit: number, windowMs: number): RateLimiter {
  const hits = new Map<string, number[]>();
  let lastSweep = 0;

  function sweep(now: number): void {
    if (now - lastSweep < windowMs) return;
    lastSweep = now;
    for (const [k, v] of hits) {
      const fresh = v.filter((t) => now - t < windowMs);
      if (fresh.length === 0) hits.delete(k);
      else hits.set(k, fresh);
    }
  }

  return {
    hit(key, now = Date.now()) {
      sweep(now);
      const fresh = (hits.get(key) ?? []).filter((t) => now - t < windowMs);
      if (fresh.length >= limit) {
        hits.set(key, fresh);
        const oldest = fresh[0] ?? now;
        return { allowed: false, retryAfterMs: Math.max(0, windowMs - (now - oldest)) };
      }
      fresh.push(now);
      hits.set(key, fresh);
      return { allowed: true, retryAfterMs: 0 };
    },
    reset(key) {
      hits.delete(key);
    },
  };
}
