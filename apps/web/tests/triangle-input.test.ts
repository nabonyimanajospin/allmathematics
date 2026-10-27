import { describe, expect, it } from "vitest";
import { findTriangleVertices } from "../src/lib/triangle-input";

describe("findTriangleVertices", () => {
  it("reads three labelled points of a triangle", () => {
    expect(findTriangleVertices("triangle A(1,2), B(3,4), C(5,0)")).toEqual([["1", "2"], ["3", "4"], ["5", "0"]]);
  });

  it("reads points in a sentence, with negative numbers, fractions and decimals", () => {
    expect(findTriangleVertices("Find the area of the triangle with vertices (-3, 2), (1/2, 5) and (5, -0.5)")).toEqual([["-3", "2"], ["1/2", "5"], ["5", "-0.5"]]);
  });

  it("accepts three points labelled A, B and C even without the word triangle", () => {
    expect(findTriangleVertices("A(0,0) B(4,0) C(0,3)")).toEqual([["0", "0"], ["4", "0"], ["0", "3"]]);
    expect(findTriangleVertices("A = (0,0), B = (4,0), C = (0,3)")).toHaveLength(3);
  });

  it("does not take other problems for a triangle", () => {
    expect(findTriangleVertices("gradient of x^2*y + z at (1,2,3)")).toBeNull();
    expect(findTriangleVertices("distance between (1,2) and (3,4)")).toBeNull();
    expect(findTriangleVertices("derivative of x^2*sin(x)")).toBeNull();
    expect(findTriangleVertices("the points (1,2), (3,4), (5,6) lie on a line")).toBeNull();
  });

  it("needs three complete points", () => {
    expect(findTriangleVertices("triangle A(1,2), B(3,4)")).toBeNull();
    expect(findTriangleVertices("triangle A(1,2), B(3,4), C(5")).toBeNull();
  });
});
