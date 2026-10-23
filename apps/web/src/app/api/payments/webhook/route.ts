import { AppError, confirmPayment, isGenuineWebhook } from "@allmaths/server";
import { handle, json } from "@/server/http";
import { paymentConfig } from "@/server/payments-config";
import { getServices } from "@/server/runtime";

const MAX_BODY = 64 * 1024;

/**
 * Called by Flutterwave after a payment. It is not called from our own pages, so there is no same-origin check; instead the call must carry
 * our secret hash, and the payment is then confirmed with Flutterwave itself before anything is granted.
 */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    const cfg = paymentConfig();
    if (!cfg) throw new AppError("payments_off", 503, "Payments are not configured.");
    if (!isGenuineWebhook(req.headers.get("verif-hash"), cfg.secretHash)) throw new AppError("bad_signature", 401, "Unauthorized.");
    const text = await req.text();
    if (text.length > MAX_BODY) throw new AppError("too_large", 413, "Request too large.");
    let body: { event?: string; data?: { id?: number | string; status?: string } } | null = null;
    try {
      body = JSON.parse(text);
    } catch {
      throw new AppError("invalid_json", 400, "Invalid JSON.");
    }
    const id = body?.data?.id;
    if (body?.event === "charge.completed" && id !== undefined && body.data?.status === "successful") {
      const { db } = await getServices();
      await confirmPayment(db, cfg, id);
    }
    return json({ ok: true }); // always acknowledge, so Flutterwave does not retry what we deliberately ignored
  });
}
