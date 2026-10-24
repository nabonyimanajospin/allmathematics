import { requirePermission, usersCsv } from "@allmaths/server";
import { schema } from "@allmaths/db";
import { handle } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

/** The list of accounts as a CSV file, for a report. Administrators only; the export is written to the audit log. */
export function GET(): Promise<Response> {
  return handle(async () => {
    const actor = await requireUser();
    requirePermission(actor.role, "users:manage");
    const { db } = await getServices();
    await db.insert(schema.auditLog).values({ actorId: actor.id, action: "users.export", target: null });
    return new Response(await usersCsv(db), {
      headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": 'attachment; filename="allmaths-users.csv"', "Cache-Control": "no-store" },
    });
  });
}
