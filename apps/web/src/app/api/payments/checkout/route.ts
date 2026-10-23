import { AppError, createCheckout, hasPremium } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json } from "@/server/http";
import { paymentConfig } from "@/server/payments-config";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

/** Starts a Premium payment and returns the address where the learner pays. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const cfg = paymentConfig();
    if (!cfg) throw new AppError("payments_off", 503, "Payments are not available yet. Ask your administrator to activate Premium.");
    const { db, limits } = await getServices();
    enforce(limits.unitTest, user.id);
    if (await hasPremium(db, user.id)) throw new AppError("already_premium", 409, "You already have Premium.");
    const { link } = await createCheckout(db, cfg, { id: user.id, email: user.email, name: user.name });
    return json({ link });
  });
}
