import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { addResource, isDownloadable, loadResources, removeResource } from "../src";

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

  describe("upload by an administrator", () => {
    const entry = { id: "notes-unit4", title: "Lecture notes, Unit 4", kind: "notes" as const, course: "mvc" as const, description: "Unit 4 notes" };
    const pdf = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34]);
    const header = "# Catalogue header\n# second line\n";

    it("stores the file, lists it as granted and keeps the header comment", () => {
      const dir = setup(header + item("  file: a.pdf\n  permission: granted\n"), ["a.pdf"]);
      const added = addResource(dir, entry, "Unit 4.PDF", pdf);
      expect(added.file).toBe("notes-unit4.pdf");
      const c = loadResources(dir);
      expect(c.issues).toEqual([]);
      expect(c.resources.map((r) => r.id)).toEqual(["a-book", "notes-unit4"]);
      expect(isDownloadable(c, c.resources[1]!)).toBe(true);
      expect(readFileSync(join(dir, "resources.yaml"), "utf8").startsWith(header)).toBe(true);
    });

    it("refuses a wrong type, a file whose content does not match, an empty file and a duplicate id", () => {
      const dir = setup(item("  file: a.pdf\n  permission: granted\n"), ["a.pdf"]);
      expect(() => addResource(dir, entry, "run.exe", pdf)).toThrow(/PDF, DOCX/);
      expect(() => addResource(dir, entry, "x.pdf", new Uint8Array([1, 2, 3, 4, 5]))).toThrow(/does not match/);
      expect(() => addResource(dir, entry, "x.pdf", new Uint8Array())).toThrow(/empty/);
      expect(() => addResource(dir, { ...entry, id: "a-book" }, "x.pdf", pdf)).toThrow(/already exists/);
      expect(() => addResource(dir, { ...entry, id: "../evil" }, "x.pdf", pdf)).toThrow();
      expect(loadResources(dir).resources).toHaveLength(1);
    });

    it("removes the entry and its file", () => {
      const dir = setup(header + item("  file: a.pdf\n  permission: granted\n"), ["a.pdf"]);
      addResource(dir, entry, "x.pdf", pdf);
      removeResource(dir, "notes-unit4");
      expect(loadResources(dir).resources.map((r) => r.id)).toEqual(["a-book"]);
      expect(existsSync(join(dir, "files", "notes-unit4.pdf"))).toBe(false);
      expect(() => removeResource(dir, "notes-unit4")).toThrow(/not found/);
    });
  });

  it("rejects a file name that leaves the folder", () => {
    expect(loadResources(setup(item("  file: ../secret.pdf\n  permission: granted\n"))).issues.length).toBeGreaterThan(0);
  });
});
