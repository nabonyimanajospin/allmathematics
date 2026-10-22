import { describe, expect, it } from "vitest";
import { latexToEngine } from "../src/lib/latex-input";

describe("latexToEngine", () => {
  it("reads a stacked fraction as an exact quotient", () => {
    expect(latexToEngine("\\frac{2}{3}")).toBe("(2)/(3)");
    expect(latexToEngine("2\\frac{x+1}{4}")).toBe("2(x+1)/(4)");
    expect(latexToEngine("\\frac{\\frac{1}{2}}{3}")).toBe("((1)/(2))/(3)");
  });

  it("reads roots, powers and pi", () => {
    expect(latexToEngine("2\\sqrt{3}")).toBe("2sqrt(3)");
    expect(latexToEngine("\\frac{\\sqrt{3}}{2}")).toBe("(sqrt(3))/(2)");
    expect(latexToEngine("x^{2}+y^2")).toBe("x^2+y^2");
    expect(latexToEngine("e^{-2t}")).toBe("e^(-2t)");
    expect(latexToEngine("\\frac{5\\pi}{6}")).toBe("(5pi)/(6)");
    expect(latexToEngine("\\sqrt[3]{x}")).toBe("(x)^(1/(3))");
  });

  it("reads degrees as exact multiples of pi", () => {
    expect(latexToEngine("60^{\\circ}")).toBe("60*(pi/180)");
    expect(latexToEngine("150^\\circ")).toBe("150*(pi/180)");
  });

  it("reads vectors, equations and regions", () => {
    expect(latexToEngine("(1,\\ -2,\\ 3)")).toBe("(1, -2, 3)");
    expect(latexToEngine("x+2y-z=0")).toBe("x+2y-z=0");
    expect(latexToEngine("x^2+y^2\\le4")).toBe("x^2+y^2<=4");
    expect(latexToEngine("x\\ge1\\text{ and }y\\ne0")).toBe("x>=1 and y!=0");
  });

  it("reads functions, constants with an index and derivatives", () => {
    expect(latexToEngine("\\sin(x)+\\ln(x)")).toBe("sin(x)+ln(x)");
    expect(latexToEngine("C_1e^{x}+C_{2}e^{2x}")).toBe("C1e^x+C2e^(2x)");
    expect(latexToEngine("xy'-2y=x")).toBe("xy'-2y=x");
    expect(latexToEngine("xy^{\\prime}-2y=x")).toBe("xy'-2y=x");
    expect(latexToEngine("\\left(1+x\\right)^{2}")).toBe("(1+x)^2");
  });
});
