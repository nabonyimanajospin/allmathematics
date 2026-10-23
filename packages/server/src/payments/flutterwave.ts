/**
 * Premium payments with Flutterwave (card and mobile money). Nothing is trusted from the browser or from the webhook body alone:
 *   1. the learner asks for a checkout; we store a pending payment with our own reference and send the learner to Flutterwave;
 *   2. Flutterwave calls our webhook; the call must carry our secret hash (verif-hash header);
 *   3. we then ask Flutterwave itself to confirm the transaction (status, reference, amount, currency) before granting Premium;
 *   4. the grant is idempotent: the same payment can never give Premium twice.
 *
 * It needs FLW_SECRET_KEY, FLW_SECRET_HASH and the price (PREMIUM_PRICE, PREMIUM_CURRENCY) in the environment. It has been tested with a
 * simulated Flutterwave only: test it against Flutterwave's test mode before taking real money.
 */

import { randomBytes, timingSafeEqual } from "node:crypto";
import { and, eq } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import { AppError, Errors } from "../errors";

const API = "https://api.flutterwave.com/v3";
export const PREMIUM_DAYS = 30;

export interface PaymentConfig {
  secretKey: string;
  secretHash: string;
  /** Amount in major units (for example 3000 for 3,000 RWF). */
  price: number;
  currency: string;
  redirectUrl: string;
}

type FetchLike = typeof fetch;

export function paymentConfigFromEnv(env: Record<string, string | undefined>, redirectUrl: string): PaymentConfig | null {
  const price = Number(env.PREMIUM_PRICE);
  if (!env.FLW_SECRET_KEY || !env.FLW_SECRET_HASH || !Number.isFinite(price) || price <= 0 || !env.PREMIUM_CURRENCY) return null;
  return { secretKey: env.FLW_SECRET_KEY, secretHash: env.FLW_SECRET_HASH, price, currency: env.PREMIUM_CURRENCY.toUpperCase(), redirectUrl };
}

/** Starts a payment: stores it as pending and returns the link where the learner pays. */
export async function createCheckout(
  db: AppDb,
  cfg: PaymentConfig,
  user: { id: string; email: string; name: string },
  fetchImpl: FetchLike = fetch,
): Promise<{ link: string; reference: string }> {
  const reference = `allmaths-${user.id.slice(0, 8)}-${randomBytes(6).toString("hex")}`;
  await db.insert(schema.payments).values({
    userId: user.id,
    provider: "flutterwave",
    amount: BigInt(Math.round(cfg.price)),
    currency: cfg.currency,
    status: "pending",
    providerRef: reference,
  });
  const res = await fetchImpl(`${API}/payments`, {
    method: "POST",
    headers: { authorization: `Bearer ${cfg.secretKey}`, "content-type": "application/json" },
    body: JSON.stringify({
      tx_ref: reference,
      amount: cfg.price,
      currency: cfg.currency,
      redirect_url: cfg.redirectUrl,
      payment_options: "card,mobilemoneyrwanda",
      customer: { email: user.email, name: user.name },
      customizations: { title: "Allmaths Premium", description: `${PREMIUM_DAYS} days of unlimited solving` },
    }),
  });
  const data = (await res.json().catch(() => null)) as { status?: string; data?: { link?: string } } | null;
  if (!res.ok || data?.status !== "success" || !data.data?.link) throw Errors.unavailable("Payments are temporarily unavailable. Please try again.");
  return { link: data.data.link, reference };
}

/** The webhook must carry our secret hash. Compared in constant time. */
export function isGenuineWebhook(headerValue: string | null, secretHash: string): boolean {
  if (!headerValue) return false;
  const a = Buffer.from(headerValue);
  const b = Buffer.from(secretHash);
  return a.length === b.length && timingSafeEqual(a, b);
}

interface VerifyData {
  status?: string;
  tx_ref?: string;
  amount?: number;
  currency?: string;
}

/**
 * Handles a webhook for `transactionId`: confirms the transaction with Flutterwave, checks that it is the payment we stored
 * (reference, amount, currency, successful) and grants Premium once. Returns true when Premium was granted by this call.
 */
export async function confirmPayment(db: AppDb, cfg: PaymentConfig, transactionId: number | string, fetchImpl: FetchLike = fetch, now = new Date()): Promise<boolean> {
  const res = await fetchImpl(`${API}/transactions/${encodeURIComponent(String(transactionId))}/verify`, { headers: { authorization: `Bearer ${cfg.secretKey}` } });
  const body = (await res.json().catch(() => null)) as { status?: string; data?: VerifyData } | null;
  const d = body?.data;
  if (!res.ok || body?.status !== "success" || !d?.tx_ref) throw new AppError("verify_failed", 502, "The payment could not be confirmed.");
  const [row] = await db
    .select()
    .from(schema.payments)
    .where(and(eq(schema.payments.provider, "flutterwave"), eq(schema.payments.providerRef, d.tx_ref)));
  if (!row) throw new AppError("unknown_payment", 404, "Unknown payment.");
  if (row.status === "successful") return false; // already processed: the webhook may be delivered several times
  const paidEnough = typeof d.amount === "number" && d.amount >= Number(row.amount);
  if (d.status !== "successful" || d.currency !== row.currency || !paidEnough) {
    await db.update(schema.payments).set({ status: "failed" }).where(eq(schema.payments.id, row.id));
    return false;
  }
  const claimed = await db
    .update(schema.payments)
    .set({ status: "successful" })
    .where(and(eq(schema.payments.id, row.id), eq(schema.payments.status, "pending")))
    .returning({ id: schema.payments.id });
  if (claimed.length === 0) return false; // another delivery got there first
  const end = new Date(now.getTime() + PREMIUM_DAYS * 86_400_000);
  await db.insert(schema.subscriptions).values({ userId: row.userId, provider: "flutterwave", status: "active", plan: "premium", currentPeriodEnd: end });
  return true;
}
