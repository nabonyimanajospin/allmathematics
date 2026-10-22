/**
 * Vectors are written as columns, points as rows. A coordinate list such as (3,4) is a vector when it is the value of a
 * vector expression in the same clause of a formula: \overrightarrow{AB}=(3,4), \vec u+\vec v=(1,2,3), \nabla f=(2x,2y).
 * A point such as A(1,2) or P=(1,2) is left as it is. Applied to every formula just before it is typeset.
 */

const VECTOR_MACROS = ["\\overrightarrow", "\\vec", "\\crossp", "\\nabla"];
const CLAUSE_BREAKS = ["\\text", "\\quad", "\\qquad", "\\;", "\\!"];

function isVectorMacroAt(s: string, i: number): boolean {
  return VECTOR_MACROS.some((m) => s.startsWith(m, i) && !/[A-Za-z]/.test(s[i + m.length] ?? ""));
}

/** Index of the parenthesis that closes the one opened at `open` (a plain "(" or "\left("), or -1. */
function matching(s: string, open: number): number {
  let depth = 0;
  for (let i = open; i < s.length; i++) {
    if (s[i] === "(") depth++;
    else if (s[i] === ")") {
      depth--;
      if (depth === 0) return i;
    } else if (s[i] === "{") {
      // skip a group: its commas and parentheses are not ours
      let g = 0;
      for (; i < s.length; i++) {
        if (s[i] === "{") g++;
        else if (s[i] === "}") {
          g--;
          if (g === 0) break;
        }
      }
    }
  }
  return -1;
}

/** The top-level parts of "a, b, c" (commas inside parentheses or braces do not split). */
function splitParts(inner: string): string[] {
  const parts: string[] = [];
  let depth = 0;
  let start = 0;
  for (let i = 0; i < inner.length; i++) {
    const c = inner[i];
    if (c === "(" || c === "{") depth++;
    else if (c === ")" || c === "}") depth--;
    else if (c === "," && depth === 0 && inner[i - 1] !== "\\") {
      parts.push(inner.slice(start, i));
      start = i + 1;
    }
  }
  parts.push(inner.slice(start));
  return parts;
}

const clean = (p: string): string => p.replace(/^(\s|\\[,;:! ])+|(\s|\\[,;:! ])+$/g, "");

export function columnVectors(src: string): string {
  let out = "";
  let clauseHasVector = false;
  let depth = 0;
  let i = 0;
  while (i < src.length) {
    if (isVectorMacroAt(src, i)) clauseHasVector = true;

    const brk = CLAUSE_BREAKS.find((b) => src.startsWith(b, i));
    if (brk && depth === 0) clauseHasVector = false;

    const c = src[i]!;
    const isLeft = src.startsWith("\\left(", i);
    if (c === "(" || isLeft) {
      const open = isLeft ? i + 5 : i;
      const close = matching(src, open);
      if (close > 0) {
        // for \left( the closing is \right)
        const end = isLeft ? close - "\\right".length : close;
        const inner = src.slice(open + 1, isLeft ? end : close);
        const parts = splitParts(inner);
        const before = out.replace(/(\s|\\[ ,;:!])+$/, "");
        if (clauseHasVector && (parts.length === 2 || parts.length === 3) && parts.every((p) => clean(p) !== "") && /(=|\+|-|\\lambda|\\mu)$/.test(before)) {
          out += "\\begin{pmatrix}" + parts.map(clean).join("\\\\") + "\\end{pmatrix}";
          i = close + 1;
          continue;
        }
      }
    }
    if (c === "(") depth++;
    if (c === ")") depth = Math.max(0, depth - 1);
    if ((c === "," && src[i - 1] !== "\\") || c === ";") if (depth === 0) clauseHasVector = false;
    out += c;
    i++;
  }
  return out;
}
