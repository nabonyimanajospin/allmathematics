import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { listFormulas, savedSectionIds, setFormulaSaved } from "../src";
import { makeFixture, type Fixture } from "./helpers";

const LESSON = "geo-m01-u01-l01";

let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
});
afterAll(async () => {
  await f.h.close();
});

describe("formula sheet", () => {
  it("starts empty, saves a formula, remembers it for the lesson, and removes it", async () => {
    expect(await listFormulas(f.h.db, f.store, f.userId)).toEqual([]);
    await setFormulaSaved(f.h.db, f.store, f.userId, LESSON, "components-formula", true);
    await setFormulaSaved(f.h.db, f.store, f.userId, LESSON, "components-formula", true); // saving twice changes nothing
    const list = await listFormulas(f.h.db, f.store, f.userId);
    expect(list).toHaveLength(1);
    expect(list[0]).toMatchObject({ lessonId: LESSON, sectionId: "components-formula", kind: "formula", courseId: "geo" });
    expect(await savedSectionIds(f.h.db, f.store, f.userId, LESSON)).toEqual(["components-formula"]);
    await setFormulaSaved(f.h.db, f.store, f.userId, LESSON, "components-formula", false);
    expect(await listFormulas(f.h.db, f.store, f.userId)).toEqual([]);
  });

  it("a theorem can be saved, but not a question or an unknown section", async () => {
    await setFormulaSaved(f.h.db, f.store, f.userId, LESSON, "opposite-and-origin", true);
    expect((await listFormulas(f.h.db, f.store, f.userId)).map((x) => x.kind)).toEqual(["theorem"]);
    await expect(setFormulaSaved(f.h.db, f.store, f.userId, LESSON, "chk-components", true)).rejects.toMatchObject({ status: 404 });
    await expect(setFormulaSaved(f.h.db, f.store, f.userId, LESSON, "nothing", true)).rejects.toMatchObject({ status: 404 });
    await expect(setFormulaSaved(f.h.db, f.store, f.userId, "no-lesson", "x", true)).rejects.toMatchObject({ status: 404 });
  });

  it("each student has a sheet of their own", async () => {
    const other = await makeFixture();
    try {
      expect(await listFormulas(other.h.db, other.store, other.userId)).toEqual([]);
    } finally {
      await other.h.close();
    }
  });
});
