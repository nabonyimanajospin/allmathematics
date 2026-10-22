/**
 * Notation standard (spec section 6). Every mathematical notation used on the platform is defined here
 * once, as KaTeX / LaTeX macros. Content uses the macros, never ad-hoc notation, so a change of
 * convention is a change of this file only.
 *
 * Course convention (default):  dot ⟨u, v⟩   cross [u, v]   box ⟨u, v, w⟩
 * Standard convention (switch): dot u · v    cross u × v    box [u, v, w]
 */

export type NotationStyle = "course" | "standard";

export type MacroMap = Readonly<Record<string, string>>;

/** Macros that do not depend on the convention. */
const common: MacroMap = {
  // Number sets
  "\\R": "\\mathbb{R}",
  "\\N": "\\mathbb{N}",
  "\\Z": "\\mathbb{Z}",
  "\\Q": "\\mathbb{Q}",
  "\\C": "\\mathbb{C}",
  // Vectors
  "\\norm": "\\left\\lVert #1\\right\\rVert",
  "\\unit": "\\hat{#1}",
  "\\proj": "\\operatorname{proj}_{#1}#2",
  "\\comp": "\\operatorname{comp}_{#1}#2",
  "\\vecab": "\\overrightarrow{#1#2}",
  "\\zerovec": "\\vec{0}",
  "\\basis": "\\vec{#1}",
  "\\angbetween": "\\widehat{(#1,\\,#2)}",
  // Geometry
  "\\dist": "d\\left(#1,\\,#2\\right)",
  "\\area": "\\mathcal{A}",
  // Calculus
  "\\pd": "\\dfrac{\\partial #1}{\\partial #2}",
  "\\pdd": "\\dfrac{\\partial^{2} #1}{\\partial #2\\,\\partial #3}",
  "\\grad": "\\nabla",
  "\\dd": "\\,\\mathrm{d}",
  "\\Hess": "H_{#1}",
  "\\jac": "\\dfrac{\\partial(#1)}{\\partial(#2)}",
  "\\dirder": "D_{\\vec{#1}}#2",
};

const course: MacroMap = {
  "\\dotp": "\\left\\langle #1,\\,#2\\right\\rangle",
  "\\crossp": "\\left[#1,\\,#2\\right]",
  "\\boxp": "\\left\\langle #1,\\,#2,\\,#3\\right\\rangle",
};

const standard: MacroMap = {
  "\\dotp": "#1\\cdot #2",
  "\\crossp": "#1\\times #2",
  "\\boxp": "\\left[#1,\\,#2,\\,#3\\right]",
};

export function getMacros(style: NotationStyle = "course"): Record<string, string> {
  return { ...common, ...(style === "course" ? course : standard) };
}

/** Names of every macro defined (without backslash). Used by the lint to know what is allowed. */
export const macroNames: readonly string[] = Object.keys(getMacros()).map((m) => m.slice(1));

/** LaTeX preamble with the same macros, for server-side PDF generation (spec section 10.4). */
export function latexPreamble(style: NotationStyle = "course"): string {
  const defs: Record<string, [number, string]> = {
    R: [0, "\\mathbb{R}"],
    N: [0, "\\mathbb{N}"],
    Z: [0, "\\mathbb{Z}"],
    Q: [0, "\\mathbb{Q}"],
    C: [0, "\\mathbb{C}"],
  };
  const lines = Object.entries(getMacros(style)).map(([name, body]) => {
    const argc = Math.max(0, ...Array.from(body.matchAll(/#(\d)/g), (m) => Number(m[1])));
    const key = name.slice(1);
    const known = defs[key];
    const count = known ? known[0] : argc;
    return `\\newcommand{${name}}${count > 0 ? `[${count}]` : ""}{${body}}`;
  });
  return lines.join("\n");
}
