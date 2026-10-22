import { describe, expect, it } from "vitest";
import { buildPlot, compileExpr, PlotExpressionError, validatePlotConfig } from "../src";

describe("plot expressions", () => {
  it("evaluates with the usual precedence, powers and unary minus", () => {
    expect(compileExpr("1+2*3")()).toBe(7);
    expect(compileExpr("2^3^2")()).toBe(512);
    expect(compileExpr("-2^2")()).toBe(-4);
    expect(compileExpr("(1+2)*3-4/2")()).toBe(7);
    expect(compileExpr("3*(1+cos(t))", ["t"])(0)).toBe(6);
    expect(compileExpr("sin(pi/2)")()).toBeCloseTo(1, 12);
    expect(compileExpr("2^-1")()).toBe(0.5);
  });

  it("rejects unknown names, functions and characters instead of running anything", () => {
    expect(() => compileExpr("foo(1)")).toThrow(PlotExpressionError);
    expect(() => compileExpr("x+1")).toThrow(PlotExpressionError);
    expect(() => compileExpr("1+")).toThrow(PlotExpressionError);
    expect(() => compileExpr("alert(1);")).toThrow(PlotExpressionError);
    expect(() => compileExpr("constructor", ["t"])).toThrow(PlotExpressionError);
    expect(() => compileExpr("constructor(1)")).toThrow(PlotExpressionError);
    expect(() => compileExpr("toString")).toThrow(PlotExpressionError);
    expect(() => compileExpr("(1+2")).toThrow(PlotExpressionError);
  });
});

describe("plot sampling", () => {
  it("samples a cardioid and stays inside its bounds", () => {
    const plot = buildPlot({ mode: "polar", r: "3*(1+cos(t))", range: 8 });
    const pts = plot.curves[0]!.pieces.flat();
    expect(pts.length).toBeGreaterThan(1000);
    expect(Math.max(...pts.map((p) => p[0]))).toBeCloseTo(6, 2); // r = 6 at t = 0
  });

  it("breaks a curve at an asymptote", () => {
    const plot = buildPlot({ mode: "cartesian", f: "1/x", xmin: -4, xmax: 4, ymin: -4, ymax: 4 });
    expect(plot.curves[0]!.pieces.length).toBeGreaterThanOrEqual(2);
  });

  it("drops the points where the function is undefined (a lemniscate has gaps)", () => {
    const plot = buildPlot({ mode: "polar", r: "4*sqrt(cos(2*t))", range: 6 });
    // the lobe through the starting point is cut where the angle goes round: three pieces that join up
    expect(plot.curves[0]!.pieces.length).toBe(3);
  });

  it("reports mistakes in the configuration", () => {
    expect(validatePlotConfig({ mode: "polar", r: "3*(1+cos(t))" })).toBeNull();
    expect(validatePlotConfig({ mode: "polar", r: "3*(1+co(t))" })).toContain("Unknown function");
    expect(validatePlotConfig({ mode: "spiral", r: "t" })).toContain("mode");
    expect(validatePlotConfig({ mode: "cartesian", f: "sqrt(-1-x^2)" })).toContain("fewer than 20");
    expect(validatePlotConfig({ mode: "parametric", x: "cos(t)" })).toContain("at least one curve");
  });
});
