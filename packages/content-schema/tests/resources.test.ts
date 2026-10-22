import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { isDownloadable, loadResources } from "../src";

function setup(yaml: string, files: string[] = []): string {
  const dir = mkdtempSync(join(tmpdir(), "res-"));
  mkdirSync(join(dir, "files"));
  writeFileSync(join(dir, "resources.yaml"), yaml);
  for (const f of files) writeFileSync(join(dir, "files", f), "x");
  return dir;
}
const item = (extra: string) => `- id: a-book\n  title: A book\n  kind: book\n  course: mvc\n  description: Something\n${extra}`;

describe("resources catalogue", () => {
  it("the real catalogue is valid and every granted file exists", () => {
    const c = loadResources(resolve(import.meta.dirname, "..", "..", "..", "resources"));
    expect(c.issues).toEqual([]);
    expect(c.resources.length).toBeGreaterThan(0);
  });

  it("offers a document only when permission is granted and the file exists", () => {
    const ok = loadResources(setup(item("  file: a.pdf\n  permission: granted\n"), ["a.pdf"]));
    expect(ok.issues).toEqual([]);
    expect(isDownloadable(ok, ok.resources[0]!)).toBe(true);
    const pending = loadResources(setup(item("  file: a.pdf\n  permission: pending\n"), ["a.pdf"]));
    expect(isDownloadable(pending, pending.resources[0]!)).toBe(false);
  });

  it("reports a granted document whose file is missing, and a granted one without a file", () => {
    expect(loadResources(setup(item("  file: a.pdf\n  permission: granted\n"))).issues.join()).toMatch(/missing/);
    expect(loadResources(setup(item("  permission: granted\n"))).issues.join()).toMatch(/needs a `file`/);
  });

  it("rejects a file name that leaves the folder", () => {
    expect(loadResources(setup(item("  file: ../secret.pdf\n  permission: granted\n"))).issues.length).toBeGreaterThan(0);
  });
});
