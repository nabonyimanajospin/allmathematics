import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { eq } from "drizzle-orm";
import { schema } from "@allmaths/db";
import { confirmPayment, createCheckout, isGenuineWebhook, paymentConfigFromEnv, type PaymentConfig } from "../src/payments/flutterwave";
import { hasPremium } from "../src/solver/plan";
import { makeFixture, type Fixture } from "./helpers";

const cfg: PaymentConfig = { secretKey: "FLWSECK_TEST-key", secretHash: "my-secret-hash", price: 3000, currency: "RWF", redirectUrl: "https://example.org/solver" };
let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
});
afterAll(async () => {
  await f.h.close();
});

const json = (data: unknown, ok = true) => ({ ok, status: ok ? 200 : 500, json: async () => data }) as Response;

describe("Premium payments (simulated Flutterwave)", () => {
  it("is off unless every setting is present", () => {
    expect(paymentConfigFromEnv({}, "x")).toBeNull();
    expect(paymentConfigFromEnv({ FLW_SECRET_KEY: "k", FLW_SECRET_HASH: "h", PREMIUM_PRICE: "3000", PREMIUM_CURRENCY: "rwf" }, "x")).toMatchObject({ price: 3000, currency: "RWF" });
    expect(paymentConfigFromEnv({ FLW_SECRET_KEY: "k", FLW_SECRET_HASH: "h", PREMIUM_PRICE: "free", PREMIUM_CURRENCY: "RWF" }, "x")).toBeNull();
  });

  it("only a webhook with our secret hash is accepted", () => {
    expect(isGenuineWebhook("my-secret-hash", cfg.secretHash)).toBe(true);
    expect(isGenuineWebhook("my-secret-hasH", cfg.secretHash)).toBe(false);
    expect(isGenuineWebhook("short", cfg.secretHash)).toBe(false);
    expect(isGenuineWebhook(null, cfg.secretHash)).toBe(false);
  });

  it("a checkout stores a pending payment and sends the amount and our reference to the provider", async () => {
    let sent: { url: string; body: Record<string, unknown>; auth: string } | null = null;
    const fake = (async (url: string, init: RequestInit) => {
      sent = { url, body: JSON.parse(String(init.body)), auth: String((init.headers as Record<string, string>).authorization) };
      return json({ status: "success", data: { link: "https://checkout.example/pay/123" } });
    }) as unknown as typeof fetch;
    const r = await createCheckout(f.h.db, cfg, { id: f.userId, email: "t@example.com", name: "T" }, fake);
    expect(r.link).toBe("https://checkout.example/pay/123");
    expect(sent!.url).toContain("/payments");
    expect(sent!.auth).toBe("Bearer FLWSECK_TEST-key");
    expect(sent!.body).toMatchObject({ tx_ref: r.reference, amount: 3000, currency: "RWF" });
    const [row] = await f.h.db.select().from(schema.payments).where(eq(schema.payments.providerRef, r.reference));
    expect(row).toMatchObject({ status: "pending", currency: "RWF", userId: f.userId });
  });

  it("a verified successful payment grants Premium once, even if the webhook is delivered twice", async () => {
    const ref = (await createCheckout(f.h.db, cfg, { id: f.userId, email: "t@example.com", name: "T" }, (async () => json({ status: "success", data: { link: "https://x" } })) as unknown as typeof fetch)).reference;
    const verify = (async () => json({ status: "success", data: { status: "successful", tx_ref: ref, amount: 3000, currency: "RWF" } })) as unknown as typeof fetch;
    expect(await hasPremium(f.h.db, f.userId)).toBe(false);
    expect(await confirmPayment(f.h.db, cfg, 111, verify)).toBe(true);
    expect(await hasPremium(f.h.db, f.userId)).toBe(true);
    expect(await confirmPayment(f.h.db, cfg, 111, verify)).toBe(false);
    const subs = await f.h.db.select().from(schema.subscriptions).where(eq(schema.subscriptions.userId, f.userId));
    expect(subs).toHaveLength(1);
  });

  it("a wrong amount, wrong currency or failed status never grants Premium", async () => {
    const [u] = await f.h.db.insert(schema.users).values({ email: "cheat@example.com", name: "Cheat" }).returning();
    for (const bad of [{ status: "successful", amount: 100, currency: "RWF" }, { status: "successful", amount: 3000, currency: "USD" }, { status: "failed", amount: 3000, currency: "RWF" }]) {
      const ref = (await createCheckout(f.h.db, cfg, { id: u!.id, email: "cheat@example.com", name: "Cheat" }, (async () => json({ status: "success", data: { link: "https://x" } })) as unknown as typeof fetch)).reference;
      const verify = (async () => json({ status: "success", data: { ...bad, tx_ref: ref } })) as unknown as typeof fetch;
      expect(await confirmPayment(f.h.db, cfg, 222, verify)).toBe(false);
    }
    expect(await hasPremium(f.h.db, u!.id)).toBe(false);
  });

  it("an unknown reference or a provider that cannot confirm is refused", async () => {
    const unknownRef = (async () => json({ status: "success", data: { status: "successful", tx_ref: "someone-elses", amount: 3000, currency: "RWF" } })) as unknown as typeof fetch;
    await expect(confirmPayment(f.h.db, cfg, 1, unknownRef)).rejects.toMatchObject({ code: "unknown_payment" });
    const down = (async () => json({}, false)) as unknown as typeof fetch;
    await expect(confirmPayment(f.h.db, cfg, 1, down)).rejects.toMatchObject({ code: "verify_failed" });
  });
});
