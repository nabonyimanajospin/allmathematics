import { paymentConfigFromEnv, type PaymentConfig } from "@allmaths/server";

/** The payment settings, or null when payments are not configured (the payment button is then hidden). APP_URL is the public address of the site. */
export function paymentConfig(): PaymentConfig | null {
  const base = (process.env.APP_URL ?? "http://localhost:3000").replace(/\/$/, "");
  return paymentConfigFromEnv(process.env, `${base}/solver?paid=1`);
}
