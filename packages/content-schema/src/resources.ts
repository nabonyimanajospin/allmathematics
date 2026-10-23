/**
 * The catalogue of downloadable documents (books, notes, exercise sheets) shown on the Resources page.
 * A document can be downloaded only if its permission is `granted` (spec section 12.2).
 */

import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml, stringify as stringifyYaml } from "yaml";
import { z } from "zod";

export const RESOURCE_KINDS = ["book", "notes", "exercises", "formulas", "syllabus"] as const;
export type ResourceKind = (typeof RESOURCE_KINDS)[number];

export const resourceSchema = z
  .object({
    id: z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*$/, "lower-case words separated by hyphens"),
    title: z.string().min(3).max(160),
    kind: z.enum(RESOURCE_KINDS),
    course: z.enum(["geo", "mvc", "stat"]),
    description: z.string().min(3).max(400),
    /** File name inside resources/files; required when the document can be downloaded. */
    file: z
      .string()
      .regex(/^[A-Za-z0-9][A-Za-z0-9._-]*$/, "a plain file name, no folders")
      .optional(),
    permission: z.enum(["granted", "pending"]),
    note: z.string().max(300).optional(),
  })
  .strict()
  .superRefine((r, ctx) => {
    if (r.permission === "granted" && !r.file) ctx.addIssue({ code: "custom", message: "A granted resource needs a `file`", path: ["file"] });
  });
export type Resource = z.infer<typeof resourceSchema>;

export interface ResourceCatalog {
  resources: Resource[];
  /** Absolute folder that holds the files. */
  filesDir: string;
  issues: string[];
}

/** Reads resources/resources.yaml. Problems are collected in `issues`, never thrown. */
export function loadResources(resourcesDir: string): ResourceCatalog {
  const filesDir = join(resourcesDir, "files");
  const issues: string[] = [];
  const path = join(resourcesDir, "resources.yaml");
  if (!existsSync(path)) return { resources: [], filesDir, issues };
  let raw: unknown;
  try {
    raw = parseYaml(readFileSync(path, "utf8"));
  } catch (e) {
    return { resources: [], filesDir, issues: [`resources.yaml: ${(e as Error).message}`] };
  }
  const parsed = z.array(resourceSchema).safeParse(raw ?? []);
  if (!parsed.success) {
    for (const i of parsed.error.issues) issues.push(`resources.yaml ${i.path.join(".")}: ${i.message}`);
    return { resources: [], filesDir, issues };
  }
  const seen = new Set<string>();
  for (const r of parsed.data) {
    if (seen.has(r.id)) issues.push(`resources.yaml: duplicate id ${r.id}`);
    seen.add(r.id);
    if (r.permission === "granted" && r.file && !existsSync(join(filesDir, r.file))) issues.push(`resources.yaml: the file of ${r.id} is missing (${r.file})`);
  }
  return { resources: parsed.data, filesDir, issues };
}

/** File types an administrator may upload, with the first bytes every genuine file of that type starts with. */
export const UPLOAD_TYPES: Record<string, readonly number[]> = {
  ".pdf": [0x25, 0x50, 0x44, 0x46, 0x2d],
  ".docx": [0x50, 0x4b, 0x03, 0x04],
  ".png": [0x89, 0x50, 0x4e, 0x47],
  ".jpg": [0xff, 0xd8, 0xff],
};
export const MAX_UPLOAD_BYTES = 50 * 1024 * 1024;

export class ResourceUploadError extends Error {
  constructor(
    public readonly code: "invalid" | "duplicate" | "type" | "too_large" | "not_found",
    message: string,
  ) {
    super(message);
  }
}

/** Keeps the comment block at the top of resources.yaml when the file is rewritten. */
function writeCatalog(resourcesDir: string, resources: Resource[]): void {
  const path = join(resourcesDir, "resources.yaml");
  const old = existsSync(path) ? readFileSync(path, "utf8") : "";
  const header = old.split(/\r?\n/).filter((l, i, all) => l.startsWith("#") && all.slice(0, i).every((p) => p.startsWith("#")));
  const body = resources.length > 0 ? stringifyYaml(resources, { lineWidth: 0 }) : "[]\n";
  writeFileSync(path, (header.length > 0 ? `${header.join("\n")}\n` : "") + body);
}

/**
 * Adds an uploaded document: checks the entry, the extension and the first bytes of the file, stores the file as
 * `<id><extension>` and lists it as granted (the administrator confirms the right to publish it).
 */
export function addResource(resourcesDir: string, entry: Omit<Resource, "file" | "permission">, original: string, bytes: Uint8Array): Resource {
  const ext = /\.[A-Za-z0-9]+$/.exec(original)?.[0].toLowerCase() ?? "";
  const magic = UPLOAD_TYPES[ext];
  if (!magic) throw new ResourceUploadError("type", "Upload a PDF, DOCX, PNG or JPG file.");
  if (bytes.length === 0) throw new ResourceUploadError("invalid", "The file is empty.");
  if (bytes.length > MAX_UPLOAD_BYTES) throw new ResourceUploadError("too_large", "The file is larger than 50 MB.");
  if (!magic.every((b, i) => bytes[i] === b)) throw new ResourceUploadError("type", "The content of the file does not match its extension.");
  const resource: Resource = { ...entry, file: `${entry.id}${ext}`, permission: "granted" };
  const parsed = resourceSchema.safeParse(resource);
  if (!parsed.success) throw new ResourceUploadError("invalid", parsed.error.issues[0]?.message ?? "Invalid document.");

  const catalog = loadResources(resourcesDir);
  if (catalog.issues.length > 0) throw new ResourceUploadError("invalid", "The catalogue has problems; fix them before uploading.");
  if (catalog.resources.some((r) => r.id === resource.id)) throw new ResourceUploadError("duplicate", "A document with this id already exists.");
  const target = join(catalog.filesDir, parsed.data.file!);
  if (existsSync(target)) throw new ResourceUploadError("duplicate", "A file with this name already exists.");
  mkdirSync(catalog.filesDir, { recursive: true });
  writeFileSync(target, bytes);
  writeCatalog(resourcesDir, [...catalog.resources, parsed.data]);
  return parsed.data;
}

/** Removes a document from the catalogue and deletes its file. */
export function removeResource(resourcesDir: string, id: string): void {
  const catalog = loadResources(resourcesDir);
  if (catalog.issues.length > 0) throw new ResourceUploadError("invalid", "The catalogue has problems; fix them before removing.");
  const r = catalog.resources.find((x) => x.id === id);
  if (!r) throw new ResourceUploadError("not_found", "Document not found.");
  writeCatalog(resourcesDir, catalog.resources.filter((x) => x.id !== id));
  if (r.file) rmSync(join(catalog.filesDir, r.file), { force: true });
}

/** True when the document may be offered for download right now. */
export function isDownloadable(catalog: ResourceCatalog, r: Resource): boolean {
  return r.permission === "granted" && !!r.file && existsSync(join(catalog.filesDir, r.file));
}
