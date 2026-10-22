/**
 * Notation lint (spec section 7.4, step 6). Works on LaTeX math strings and on engine answer expressions.
 * Errors block publication; warnings are shown to the author.
 */

export type LintSeverity = "error" | "warning";

export interface LintIssue {
  rule: string;
  severity: LintSeverity;
  message: string;
  /** The offending fragment (trimmed). */
  excerpt: string;
}

export const LINT_RULES = {
  dotCdot: "vector-dot-uses-cdot",
  crossTimes: "vector-cross-uses-times",
  plainLetterVector: "vector-without-arrow",
  boldVector: "vector-bold",
  rawAngle: "raw-angle-brackets",
  decimal: "decimal-in-math",
  unrationalized: "unrationalized-denominator",
  barNorm: "norm-with-bars",
  displayFrac: "display-frac-not-dfrac",
} as const;

export type LintRule = (typeof LINT_RULES)[keyof typeof LINT_RULES];

/** A token that denotes a vector in notation: \vec{..}, \overrightarrow{..}, \unit{..}, \hat{..}, \vecab{..}{..}. */
const VECTOR_TOKEN = String.raw`(?:\\vec\s*(?:\{[^{}]*\}|[A-Za-z])|\\overrightarrow\s*\{[^{}]*\}|\\unit\s*\{[^{}]*\}|\\hat\s*\{[^{}]*\}|\\vecab\s*\{[^{}]*\}\s*\{[^{}]*\}|\\zerovec)`;

const RE_CDOT = new RegExp(String.raw`${VECTOR_TOKEN}\s*\\cdot|\\cdot\s*${VECTOR_TOKEN}`);
const RE_TIMES = new RegExp(String.raw`${VECTOR_TOKEN}\s*\\times|\\times\s*${VECTOR_TOKEN}`);
const RE_BOLD = /\\(?:mathbf|boldsymbol|bm)\s*\{\s*[a-z]\s*\}/;
const RE_RAW_ANGLE = /\\(?:left)?\\?(?:langle|rangle)/;
const RE_DECIMAL = /(?<![\w.])\d+\.\d+(?!\w)/;
/** A radical of a plain number in a denominator, e.g. \frac{1}{\sqrt{2}}. A radical of an expression with letters is fine. */
const RE_UNRATIONALIZED_LATEX = /\\d?frac\s*\{[^{}]*\}\s*\{[^{}]*\\sqrt\s*\{[^{}a-zA-Z\\]*\}/;
const RE_BAR_NORM = /\\(?:left)?\\?(?:lvert|\|)\s*\\vec|\\vec\s*\{[^{}]*\}\s*\\(?:right)?\\?(?:rvert|\|)/;
/** Arguments of the product macros must be vectors or explicit coordinates. */
const PRODUCT_MACROS = ["dotp", "crossp", "boxp"] as const;

function extractArgs(src: string, start: number, count: number): string[] | null {
  const args: string[] = [];
  let i = start;
  for (let n = 0; n < count; n++) {
    while (i < src.length && /\s/.test(src[i] ?? "")) i++;
    if (src[i] !== "{") return null;
    let depth = 0;
    const from = i + 1;
    for (; i < src.length; i++) {
      const ch = src[i];
      if (ch === "{") depth++;
      else if (ch === "}") {
        depth--;
        if (depth === 0) break;
      }
    }
    if (depth !== 0) return null;
    args.push(src.slice(from, i));
    i++;
  }
  return args;
}

function looksLikeVector(arg: string): boolean {
  const a = arg.trim();
  if (a === "") return false;
  if (new RegExp(`^${VECTOR_TOKEN}`).test(a)) return true;
  if (/\\crossp|\\dotp|\\proj|\\comp|\\vec|\\overrightarrow|\\unit|\\hat|\\begin\{pmatrix\}/.test(a)) return true;
  // explicit coordinates such as (1,2,3) or \left(1,2\right), possibly with a scalar in front
  if (/(?:\\left)?\(.*,.*(?:\\right)?\)/.test(a)) return true;
  // a combination such as 2\vec u - \vec v already matched above; sums of tokens too.
  return false;
}

/**
 * Lint one LaTeX math fragment (without the surrounding $ delimiters).
 * `allowDecimal` is for the rare question that explicitly asks for an approximation.
 */
export function lintMath(latex: string, opts: { allowDecimal?: boolean; display?: boolean } = {}): LintIssue[] {
  const issues: LintIssue[] = [];
  const push = (rule: LintRule, severity: LintSeverity, message: string, excerpt: string) =>
    issues.push({ rule, severity, message, excerpt: excerpt.trim().slice(0, 80) });

  const cdot = RE_CDOT.exec(latex);
  if (cdot) push(LINT_RULES.dotCdot, "error", "Use \\dotp{u}{v} for the dot product, not \\cdot between vectors.", cdot[0]);

  const times = RE_TIMES.exec(latex);
  if (times)
    push(LINT_RULES.crossTimes, "error", "Use \\crossp{u}{v} for the cross product, not \\times between vectors.", times[0]);

  const bold = RE_BOLD.exec(latex);
  if (bold) push(LINT_RULES.boldVector, "error", "Vectors are written with an arrow (\\vec u), never in bold.", bold[0]);

  const angle = RE_RAW_ANGLE.exec(latex);
  if (angle) push(LINT_RULES.rawAngle, "error", "Use the notation macros (\\dotp, \\boxp) instead of raw angle brackets.", angle[0]);

  if (!opts.allowDecimal) {
    const dec = RE_DECIMAL.exec(latex);
    if (dec) push(LINT_RULES.decimal, "error", "No decimals: write an exact fraction, radical or multiple of \\pi.", dec[0]);
  }

  const unr = RE_UNRATIONALIZED_LATEX.exec(latex);
  if (unr) push(LINT_RULES.unrationalized, "error", "Rationalize the denominator (no radical in a denominator).", unr[0]);

  const bar = RE_BAR_NORM.exec(latex);
  if (bar) push(LINT_RULES.barNorm, "warning", "Write the norm with \\norm{\\vec u}.", bar[0]);

  // A small fraction is right inside an exponent or a subscript: only a fraction on the main line must be \dfrac.
  const mainLine = latex.replace(/[\^_]\{(?:[^{}]|\{[^{}]*\})*\}/g, "");
  if (opts.display && /\\frac\b/.test(mainLine)) {
    push(LINT_RULES.displayFrac, "warning", "Use \\dfrac in display math.", "\\frac");
  }

  for (const name of PRODUCT_MACROS) {
    const argc = name === "boxp" ? 3 : 2;
    const re = new RegExp(String.raw`\\${name}(?![A-Za-z])`, "g");
    for (let m = re.exec(latex); m; m = re.exec(latex)) {
      const args = extractArgs(latex, m.index + m[0].length, argc);
      if (!args) {
        push(LINT_RULES.plainLetterVector, "error", `\\${name} needs ${argc} arguments.`, latex.slice(m.index, m.index + 30));
        continue;
      }
      args.forEach((arg) => {
        if (!looksLikeVector(arg)) {
          push(
            LINT_RULES.plainLetterVector,
            "error",
            `The argument “${arg.trim()}” of \\${name} must be a vector with an arrow (\\vec ${arg.trim()}) or explicit coordinates.`,
            `\\${name}{${arg}}`,
          );
        }
      });
    }
  }
  return issues;
}

/** Lint an engine answer expression (ASCII syntax): no decimals, no unrationalized denominators. */
export function lintAnswerExpression(expr: string): LintIssue[] {
  const issues: LintIssue[] = [];
  const dec = RE_DECIMAL.exec(expr);
  if (dec)
    issues.push({ rule: LINT_RULES.decimal, severity: "error", message: "Answer keys must be exact (no decimals).", excerpt: dec[0] });
  if (/\/\s*(?:\d+\s*\*\s*)?sqrt\s*\(\s*[\d\s+\-*^]*\)/.test(expr)) {
    issues.push({
      rule: LINT_RULES.unrationalized,
      severity: "error",
      message: "Rationalize the denominator in the answer key (write sqrt(2)/2, not 1/sqrt(2)).",
      excerpt: expr.slice(0, 80),
    });
  }
  return issues;
}

export interface MathSegment {
  latex: string;
  display: boolean;
}

/**
 * Split text containing $...$ (inline) and $$...$$ (display) math into math segments.
 * A dollar sign that is not math is written \$ .
 */
export function extractMath(text: string): { segments: MathSegment[]; unbalanced: boolean } {
  const segments: MathSegment[] = [];
  let i = 0;
  while (i < text.length) {
    const ch = text[i];
    if (ch === "\\" && text[i + 1] === "$") {
      i += 2;
      continue;
    }
    if (ch !== "$") {
      i++;
      continue;
    }
    const display = text[i + 1] === "$";
    const open = display ? 2 : 1;
    let j = i + open;
    let found = -1;
    while (j < text.length) {
      if (text[j] === "\\") {
        j += 2;
        continue;
      }
      if (text[j] === "$" && (!display || text[j + 1] === "$")) {
        found = j;
        break;
      }
      j++;
    }
    if (found < 0) return { segments, unbalanced: true };
    segments.push({ latex: text.slice(i + open, found), display });
    i = found + open;
  }
  return { segments, unbalanced: false };
}

/** Lint every math segment of a text field. */
export function lintText(text: string, opts: { allowDecimal?: boolean } = {}): LintIssue[] {
  const { segments } = extractMath(text);
  return segments.flatMap((s) => lintMath(s.latex, { allowDecimal: opts.allowDecimal, display: s.display }));
}
