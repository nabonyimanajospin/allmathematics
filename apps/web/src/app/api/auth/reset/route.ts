import { z } from "zod";
import { completePasswordReset } from "@allmaths/server";
import { assertSameOrigin, clientIp, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";

export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const { db, limits } = await getServices();
    enforce(limits.resetVerify, clientIp(req));
    const body = await readJson(req, z.unknown());
    await completePasswordReset(db, body);
    return json({ ok: true });
  });
}
