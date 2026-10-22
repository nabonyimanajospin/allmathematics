import { handle, json } from "@/server/http";
import { requireUser } from "@/server/session";

export function GET(): Promise<Response> {
  return handle(async () => {
    const u = await requireUser();
    return json({ user: { name: u.name, email: u.email, role: u.role, locale: u.locale } });
  });
}
