/**
 * Client-side learning telemetry (spec sections 9.1 and 9.4). Pure logic with injected clocks and storage,
 * so it is unit-tested without a browser. The server decides what counts; this only reports honestly.
 */

import type { EventInput } from "@allmaths/core";

export const IDLE_MS = 2 * 60 * 1000;
/** A tick longer than this is a sleeping laptop or a frozen tab, not reading time. */
const MAX_TICK_MS = 5000;

/** Accumulates active time per section: only while visible, and only if the student acted within IDLE_MS. */
export class ActivityTracker {
  private current: string | null = null;
  private lastTick: number;
  private lastInteraction: number;
  private visible = true;
  private pending = new Map<string, number>();
  private total = new Map<string, number>();

  constructor(
    now: number,
    private readonly idleMs = IDLE_MS,
  ) {
    this.lastTick = now;
    this.lastInteraction = now;
  }

  setVisible(visible: boolean, now: number): void {
    this.tick(now);
    this.visible = visible;
    this.lastTick = now;
  }

  interaction(now: number): void {
    this.tick(now);
    this.lastInteraction = now;
  }

  /** The section under the reading line changed. Returns true when it actually changed. */
  enter(sectionId: string | null, now: number): boolean {
    this.tick(now);
    if (sectionId === this.current) return false;
    this.current = sectionId;
    return true;
  }

  get active(): string | null {
    return this.current;
  }

  tick(now: number): void {
    const dt = Math.min(Math.max(0, now - this.lastTick), MAX_TICK_MS);
    this.lastTick = now;
    if (!this.current || !this.visible) return;
    if (now - this.lastInteraction > this.idleMs) return;
    this.pending.set(this.current, (this.pending.get(this.current) ?? 0) + dt);
    this.total.set(this.current, (this.total.get(this.current) ?? 0) + dt);
  }

  /** Active ms accumulated since the last drain, per section. */
  drain(): Map<string, number> {
    const out = this.pending;
    this.pending = new Map();
    return out;
  }

  /** Active ms in this page session (for the optimistic "section done" state). */
  totalMs(sectionId: string): number {
    return this.total.get(sectionId) ?? 0;
  }
}

// --- durable event queue --------------------------------------------------------------------------
export interface Storage2 {
  getItem(k: string): string | null;
  setItem(k: string, v: string): void;
  removeItem(k: string): void;
}

export type SendResult = "ok" | "retry" | "drop";

const MAX_QUEUE = 500;

/**
 * Events wait here until the server acknowledges them. Because every event has a client-generated UUID
 * the server stores each one once, so re-sending after a failure is always safe.
 */
export class EventQueue {
  private events: EventInput[] = [];
  private sending = false;

  constructor(
    private readonly key: string,
    private readonly storage: Storage2 | null,
    private readonly send: (batch: EventInput[]) => Promise<SendResult>,
    private readonly maxBatch = 50,
  ) {
    this.events = this.restore();
  }

  get size(): number {
    return this.events.length;
  }

  push(e: EventInput): void {
    this.events.push(e);
    if (this.events.length > MAX_QUEUE) this.events.splice(0, this.events.length - MAX_QUEUE);
    this.persist();
  }

  snapshot(): EventInput[] {
    return [...this.events];
  }

  /** Send everything queued, in batches. Stops at the first failure and keeps the rest. */
  async flush(): Promise<void> {
    if (this.sending) return;
    this.sending = true;
    try {
      while (this.events.length > 0) {
        const batch = this.events.slice(0, this.maxBatch);
        const r = await this.send(batch);
        if (r === "retry") return;
        const sent = new Set(batch.map((b) => b.eventId));
        this.events = this.events.filter((e) => !sent.has(e.eventId));
        this.persist();
      }
    } finally {
      this.sending = false;
    }
  }

  /** Remove events that the page already handed to the browser for delivery on exit. */
  acknowledge(ids: Set<string>): void {
    this.events = this.events.filter((e) => !ids.has(e.eventId));
    this.persist();
  }

  private persist(): void {
    try {
      if (this.events.length === 0) this.storage?.removeItem(this.key);
      else this.storage?.setItem(this.key, JSON.stringify(this.events));
    } catch {
      /* storage may be full or blocked; the in-memory queue still works */
    }
  }

  private restore(): EventInput[] {
    try {
      const raw = this.storage?.getItem(this.key);
      if (!raw) return [];
      const parsed: unknown = JSON.parse(raw);
      return Array.isArray(parsed) ? (parsed as EventInput[]).slice(-MAX_QUEUE) : [];
    } catch {
      return [];
    }
  }
}

export function queueKey(userId: string): string {
  return `allmaths:events:${userId}`;
}

export function deviceKind(width: number): "mobile" | "tablet" | "desktop" {
  return width < 640 ? "mobile" : width < 1024 ? "tablet" : "desktop";
}
