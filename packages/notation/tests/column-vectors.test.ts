import { describe, expect, it } from "vitest";
import { columnVectors } from "../src";

const col = (...p: string[]) => `\\begin{pmatrix}${p.join("\\\\")}\\end{pmatrix}`;

describe("columnVectors", () => {
  it("writes the value of a vector as a column", () => {
    expect(columnVectors("\\overrightarrow{AB}=(3,4)")).toBe(`\\overrightarrow{AB}=${col("3", "4")}`);
    expect(columnVectors("\\vec u+\\vec v=(1,\\,-2,\\,5)")).toBe(`\\vec u+\\vec v=${col("1", "-2", "5")}`);
    expect(columnVectors("\\overrightarrow{AB}=(1-(-2),\\,-1-3)=(3,-4)")).toBe(`\\overrightarrow{AB}=${col("1-(-2)", "-1-3")}=${col("3", "-4")}`);
  });

  it("handles \\left( \\right) and several vectors in one line", () => {
    expect(columnVectors("\\overrightarrow{AB}=\\left(x_B-x_A,\\; y_B-y_A\\right)")).toBe(`\\overrightarrow{AB}=${col("x_B-x_A", "y_B-y_A")}`);
    expect(columnVectors("\\overrightarrow{AB}=(3,4)\\text{ and }\\overrightarrow{BA}=(-3,-4)")).toBe(
      `\\overrightarrow{AB}=${col("3", "4")}\\text{ and }\\overrightarrow{BA}=${col("-3", "-4")}`,
    );
    expect(columnVectors("\\nabla f=(2x,2y)")).toBe(`\\nabla f=${col("2x", "2y")}`);
  });

  it("writes a direction vector after a parameter as a column", () => {
    expect(columnVectors("\\overrightarrow{OP}=(1,2,3)+\\lambda(3,4,12)")).toBe(`\\overrightarrow{OP}=${col("1", "2", "3")}+\\lambda${col("3", "4", "12")}`);
  });

  it("leaves points, scalars and groups as they are", () => {
    expect(columnVectors("A(1,2)")).toBe("A(1,2)");
    expect(columnVectors("P=(1,2)")).toBe("P=(1,2)");
    expect(columnVectors("A(1,2),\\ B=(4,6)")).toBe("A(1,2),\\ B=(4,6)");
    expect(columnVectors("\\overrightarrow{AB}=3(x+1)")).toBe("\\overrightarrow{AB}=3(x+1)");
    expect(columnVectors("\\overrightarrow{AB}=(3,4),\\ B=(4,6)")).toBe(`\\overrightarrow{AB}=${col("3", "4")},\\ B=(4,6)`);
    expect(columnVectors("\\dotp{\\vec u}{\\vec v}=(1+2)")).toBe("\\dotp{\\vec u}{\\vec v}=(1+2)");
  });
});
