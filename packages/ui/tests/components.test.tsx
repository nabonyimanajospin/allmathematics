import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Button, Field, ProgressBar, ProgressRing, Skeleton, buttonClass, cn } from "../src";

describe("ProgressBar", () => {
  it("exposes an accessible progressbar with a whole-number value", () => {
    const html = renderToStaticMarkup(<ProgressBar percent={42.9} label="Lesson progress" />);
    expect(html).toContain('role="progressbar"');
    expect(html).toContain('aria-valuenow="42"'); // rounded DOWN, never up
    expect(html).toContain('aria-label="Lesson progress"');
    expect(html).toContain("width:42%");
  });

  it("can draw small progress with a decimal while announcing a whole number, and never reaches 100 early", () => {
    const small = renderToStaticMarkup(<ProgressBar fractional percent={0.14} label="x" />);
    expect(small).toContain('aria-valuenow="0"');
    expect(small).toContain("width:0.1%");
    expect(renderToStaticMarkup(<ProgressBar fractional percent={99.99} label="x" />)).toContain("width:99.9%");
  });

  it("clamps to 0..100", () => {
    expect(renderToStaticMarkup(<ProgressBar percent={-5} label="x" />)).toContain('aria-valuenow="0"');
    expect(renderToStaticMarkup(<ProgressBar percent={250} label="x" />)).toContain('aria-valuenow="100"');
  });

  it("never shows 100 before it is reached", () => {
    expect(renderToStaticMarkup(<ProgressBar percent={99.99} label="x" />)).toContain('aria-valuenow="99"');
  });
});

describe("ProgressRing", () => {
  it("draws the arc proportionally and labels it", () => {
    const html = renderToStaticMarkup(<ProgressRing percent={25} label="Course" size={100} />);
    expect(html).toContain('aria-valuenow="25"');
    expect(html).toContain(">25%<");
    const r = (100 - Math.max(6, Math.round(100 / 11))) / 2;
    const c = 2 * Math.PI * r;
    expect(html).toContain(`stroke-dashoffset="${c * 0.75}"`);
  });
});

describe("Button", () => {
  it("defaults to type=button so it never submits a form by accident", () => {
    expect(renderToStaticMarkup(<Button>Go</Button>)).toContain('type="button"');
    expect(renderToStaticMarkup(<Button type="submit">Go</Button>)).toContain('type="submit"');
  });

  it("keeps labels on one line and a touch-friendly height", () => {
    const cls = buttonClass("primary");
    expect(cls).toContain("whitespace-nowrap");
    expect(cls).toContain("min-h-11");
  });
});

describe("Field", () => {
  it("links the label to the control and announces errors", () => {
    const html = renderToStaticMarkup(
      <Field label="E-mail" id="e" error="Required">
        <input id="e" />
      </Field>,
    );
    expect(html).toContain('for="e"');
    expect(html).toContain('role="alert"');
    expect(html).toContain("Required");
  });
});

describe("helpers", () => {
  it("cn joins only truthy parts", () => {
    expect(cn("a", false, null, undefined, "b")).toBe("a b");
  });
  it("Skeleton is hidden from assistive technology", () => {
    expect(renderToStaticMarkup(<Skeleton />)).toContain('aria-hidden="true"');
  });
});
