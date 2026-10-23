import { removeResource, ResourceUploadError } from "@allmaths/content-schema";
import { schema } from "@allmaths/db";
import { AppError, requirePermission } from "@allmaths/server";
import { assertSameOrigin, handle, json } from "@/server/http";
import { resourcesDir } from "@/server/resources";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

/** An administrator removes a document and its file. */
export function DELETE(req: Request, ctx: { params: Promise<{ id: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    requirePermission(user.role, "resources:manage");
    const { id } = await ctx.params;
    try {
      removeResource(resourcesDir(), id);
    } catch (e) {
      if (e instanceof ResourceUploadError) throw new AppError(`upload_${e.code}`, e.code === "not_found" ? 404 : 400, e.message);
      throw e;
    }
    const { db } = await getServices();
    await db.insert(schema.auditLog).values({ actorId: user.id, action: "resource.remove", target: id });
    return json({ ok: true });
  });
}
