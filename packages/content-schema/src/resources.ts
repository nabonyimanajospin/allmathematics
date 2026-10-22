/**
 * The catalogue of downloadable documents (books, notes, exercise sheets) shown on the Resources page.
 * A document can be downloaded only if its permission is `granted` (spec section 12.2).
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
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

/** True when the document may be offered for download right now. */
export function isDownloadable(catalog: ResourceCatalog, r: Resource): boolean {
  return r.permission === "granted" && !!r.file && existsSync(join(catalog.filesDir, r.file));
}
