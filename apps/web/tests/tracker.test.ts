import { describe, expect, it } from "vitest";
import type { EventInput } from "@allmaths/core";
import { ActivityTracker, EventQueue, IDLE_MS, queueKey, type SendResult, type Storage2 } from "../src/lib/tracker";

describe("ActivityTracker (spec 9.4: visible tab, interaction within 2 minutes)", () => {
  it("counts time only for the section under the reading line", () => {
    const t = new ActivityTracker(0);
    t.enter("a", 0);
    for (let s = 1; s <= 4; s++) t.tick(s * 1000);
    t.enter("b", 4000);
    for (let s = 5; s <= 7; s++) t.tick(s * 1000);
    const d = t.drain();
    expect(d.get("a")).toBe(4000);
    expect(d.get("b")).toBe(3000);
  });

  it("does not count while the tab is hidden", () => {
    const t = new ActivityTracker(0);
    t.enter("a", 0);
    t.tick(2000);
    t.setVisible(false, 2000);
    t.tick(4000);
    t.tick(6000);
    t.setVisible(true, 6000);
    t.tick(7000);
    expect(t.drain().get("a")).toBe(3000);
  });

  it("stops counting after 2 minutes without interaction and resumes on interaction", () => {
    const t = new ActivityTracker(0);
    t.enter("a", 0);
    for (let s = 1; s <= 130; s++) t.tick(s * 1000);
    // 120 s of counted time (the 120 ticks up to the idle limit), then nothing
    expect(t.totalMs("a")).toBe(IDLE_MS);
    t.interaction(131_000);
    t.tick(132_000);
    expect(t.totalMs("a")).toBe(IDLE_MS + 1000);
  });

  it("ignores huge gaps (sleep, frozen tab)", () => {
    const t = new ActivityTracker(0);
    t.enter("a", 0);
    t.interaction(10_000_000 - 1);
    t.tick(10_000_000);
    expect(t.totalMs("a")).toBeLessThanOrEqual(5000);
  });

  it("counts nothing with no active section", () => {
    const t = new ActivityTracker(0);
    t.tick(3000);
    expect(t.drain().size).toBe(0);
    expect(t.enter(null, 3000)).toBe(false);
  });

  it("drain resets the pending amounts but not the session total", () => {
    const t = new ActivityTracker(0);
    t.enter("a", 0);
    t.tick(2000);
    expect(t.drain().get("a")).toBe(2000);
    expect(t.drain().size).toBe(0);
    expect(t.totalMs("a")).toBe(2000);
  });
});

const ev = (n: number): EventInput => ({
  eventId: `00000000-0000-4000-8000-${String(n).padStart(12, "0")}`,
  verb: "viewed",
  lessonId: "geo-m01-u01-l01",
  clientTimestamp: n,
});

function memoryStorage(): Storage2 & { data: Map<string, string> } {
  const data = new Map<string, string>();
  return {
    data,
    getItem: (k) => data.get(k) ?? null,
    setItem: (k, v) => void data.set(k, v),
    removeItem: (k) => void data.delete(k),
  };
}

describe("EventQueue", () => {
  it("sends in batches and empties on success", async () => {
    const sent: number[] = [];
    const q = new EventQueue("k", null, async (b) => (sent.push(b.length), "ok"), 3);
    for (let i = 0; i < 7; i++) q.push(ev(i));
    await q.flush();
    expect(sent).toEqual([3, 3, 1]);
    expect(q.size).toBe(0);
  });

  it("keeps events when the network fails and re-sends the same ids later", async () => {
    let result: SendResult = "retry";
    const seen: string[][] = [];
    const q = new EventQueue("k", null, async (b) => (seen.push(b.map((e) => e.eventId)), result));
    q.push(ev(1));
    q.push(ev(2));
    await q.flush();
    expect(q.size).toBe(2);
    result = "ok";
    await q.flush();
    expect(q.size).toBe(0);
    expect(seen[1]).toEqual(seen[0]);
  });

  it("drops a batch the server rejected as invalid (no infinite retry)", async () => {
    const q = new EventQueue("k", null, async () => "drop");
    q.push(ev(1));
    await q.flush();
    expect(q.size).toBe(0);
  });

  it("survives a page reload through storage", async () => {
    const storage = memoryStorage();
    const q1 = new EventQueue(queueKey("u1"), storage, async () => "retry");
    q1.push(ev(1));
    q1.push(ev(2));
    const q2 = new EventQueue(queueKey("u1"), storage, async () => "ok");
    expect(q2.size).toBe(2);
    await q2.flush();
    expect(q2.size).toBe(0);
    expect(storage.data.size).toBe(0);
  });

  it("never mixes queues of different users", () => {
    const storage = memoryStorage();
    new EventQueue(queueKey("u1"), storage, async () => "retry").push(ev(1));
    expect(new EventQueue(queueKey("u2"), storage, async () => "ok").size).toBe(0);
  });

  it("tolerates corrupt storage and a failing storage", () => {
    const storage = memoryStorage();
    storage.setItem("k", "{not json");
    expect(new EventQueue("k", storage, async () => "ok").size).toBe(0);
    const broken: Storage2 = {
      getItem: () => {
        throw new Error("blocked");
      },
      setItem: () => {
        throw new Error("full");
      },
      removeItem: () => undefined,
    };
    const q = new EventQueue("k", broken, async () => "ok");
    q.push(ev(1));
    expect(q.size).toBe(1);
  });

  it("does not run two flushes at once", async () => {
    let calls = 0;
    const q = new EventQueue("k", null, async () => {
      calls++;
      await new Promise((r) => setTimeout(r, 20));
      return "ok";
    });
    q.push(ev(1));
    await Promise.all([q.flush(), q.flush()]);
    expect(calls).toBe(1);
  });

  it("acknowledge removes events handed to sendBeacon", () => {
    const q = new EventQueue("k", null, async () => "ok");
    q.push(ev(1));
    q.push(ev(2));
    q.acknowledge(new Set([ev(1).eventId]));
    expect(q.snapshot().map((e) => e.clientTimestamp)).toEqual([2]);
  });
});
