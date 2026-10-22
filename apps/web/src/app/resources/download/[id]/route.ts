import { createReadStream, statSync } from "node:fs";
import { extname, join } from "node:path";
import { Readable } from "node:stream";
import { isDownloadable } from "@allmaths/content-schema";
import { getResourceCatalog } from "@/server/resources";
import { getCurrentUser } from "@/server/session";

const TYPES: Record<string, string> = {
  ".pdf": "application/pdf",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".png": "image/png",
  ".jpg": "image/jpeg",
};

/** Only a signed-in student can download, and only a document of the catalogue whose permission is granted; nothing else on disk is reachable. */
export async function GET(req: Request, ctx: { params: Promise<{ id: string }> }): Promise<Response> {
  if (!(await getCurrentUser())) return new Response("Please sign in to download resources.", { status: 401, headers: { "Cache-Control": "no-store" } });
  const { id } = await ctx.params;
  const catalog = getResourceCatalog();
  const r = catalog.resources.find((x) => x.id === id);
  if (!r || !r.file || !isDownloadable(catalog, r)) return new Response("Not found", { status: 404 });
  const path = join(catalog.filesDir, r.file);
  const ext = extname(r.file).toLowerCase();
  const inline = new URL(req.url).searchParams.get("inline") === "1" && ext === ".pdf";
  const body = Readable.toWeb(createReadStream(path)) as unknown as ReadableStream;
  return new Response(body, {
    headers: {
      "Content-Type": TYPES[ext] ?? "application/octet-stream",
      "Content-Length": String(statSync(path).size),
      "Content-Disposition": `${inline ? "inline" : "attachment"}; filename="${r.file}"`,
      "X-Content-Type-Options": "nosniff",
      "Cache-Control": "private, max-age=3600",
    },
  });
}
