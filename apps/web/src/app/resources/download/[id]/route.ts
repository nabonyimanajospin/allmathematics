import { createReadStream, statSync } from "node:fs";
import { extname, join } from "node:path";
import { Readable } from "node:stream";
import { isDownloadable } from "@allmaths/content-schema";
import { getResourceCatalog } from "@/server/resources";

const TYPES: Record<string, string> = {
  ".pdf": "application/pdf",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".png": "image/png",
  ".jpg": "image/jpeg",
};

/** Only a document of the catalogue whose permission is granted can be downloaded; nothing else on disk is reachable. */
export async function GET(_req: Request, ctx: { params: Promise<{ id: string }> }): Promise<Response> {
  const { id } = await ctx.params;
  const catalog = getResourceCatalog();
  const r = catalog.resources.find((x) => x.id === id);
  if (!r || !r.file || !isDownloadable(catalog, r)) return new Response("Not found", { status: 404 });
  const path = join(catalog.filesDir, r.file);
  const ext = extname(r.file).toLowerCase();
  const body = Readable.toWeb(createReadStream(path)) as unknown as ReadableStream;
  return new Response(body, {
    headers: {
      "Content-Type": TYPES[ext] ?? "application/octet-stream",
      "Content-Length": String(statSync(path).size),
      "Content-Disposition": `attachment; filename="${r.file}"`,
      "X-Content-Type-Options": "nosniff",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
