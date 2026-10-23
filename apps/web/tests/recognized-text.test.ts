import { describe, expect, it } from "vitest";
import { cleanRecognized } from "@/lib/recognized-text";

describe("cleanRecognized", () => {
  it("turns printed signs into the typed form", () => {
    expect(cleanRecognized("3 × x² ÷ 2 − 1")).toBe("3 * x² / 2 - 1");
    expect(cleanRecognized("√2 + π")).toBe("sqrt(2) + pi");
  });
  it("joins several lines with commas, so a system stays a system", () => {
    expect(cleanRecognized("x + y = 5\n\n x − y = 1 \r\n")).toBe("x + y = 5, x - y = 1");
  });
  it("returns an empty string when there is no text", () => {
    expect(cleanRecognized("  \n | \n")).toBe("");
  });
});
