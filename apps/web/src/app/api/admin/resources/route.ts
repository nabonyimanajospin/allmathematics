import { z } from "zod";
import { addResource, MAX_UPLOAD_BYTES, RESOURCE_KINDS, ResourceUploadError } from "@allmaths/content-schema";
import { schema } from "@allmaths/db";
import { AppError, Errors, requirePermission } from "@allmaths/server";
import { assertSameOrigin, handle, json } from "@/server/http";
import { resourcesDir } from "@/server/resources";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const fields = z.object({
  id: z.string().trim(),
  title: z.string().trim(),
  kind: z.enum(RESOURCE_KINDS),
  course: z.enum(["geo", "mvc", "stat"]),
  description: z.string().trim(),
  confirm: z.literal("yes", { error: "Confirm that we may publish this file." }),
});

/** An administrator uploads a document; it appears on the Resources page for every signed-in learner. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    requirePermission(user.role, "resources:manage");
    const length = Number(req.headers.get("content-length") ?? "0");
    if (length > MAX_UPLOAD_BYTES + 64 * 1024) throw new AppError("too_large", 413, "The file is larger than 50 MB.");
    const form = await req.formData();
    const file = form.get("file");
    if (!(file instanceof File)) throw Errors.badRequest("Choose a file to upload.", "invalid_input");
    const parsed = fields.safeParse(Object.fromEntries([...form.entries()].filter(([, v]) => typeof v === "string")));
    if (!parsed.success) throw Errors.badRequest(parsed.error.issues[0]?.message ?? "Invalid input.", "invalid_input");
    const { id, title, kind, course, description } = parsed.data;
    const entry = { id, title, kind, course, description };
    try {
      const added = addResource(resourcesDir(), entry, file.name, new Uint8Array(await file.arrayBuffer()));
      const { db } = await getServices();
      await db.insert(schema.auditLog).values({ actorId: user.id, action: "resource.upload", target: added.id });
      return json({ ok: true, id: added.id }, 201);
    } catch (e) {
      if (e instanceof ResourceUploadError) throw new AppError(`upload_${e.code}`, e.code === "duplicate" ? 409 : e.code === "too_large" ? 413 : 400, e.message);
      throw e;
    }
  });
}
