import { assertSameOrigin, handle, json } from "@/server/http";
import { endSession } from "@/server/session";

export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    await endSession();
    return json({ ok: true });
  });
}
