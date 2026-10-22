/**
 * Converts what the student typed in the math field (LaTeX) into the plain text the math engine reads.
 * A fraction \frac{2}{3} becomes (2)/(3); the engine then treats it as an exact value.
 */

const FUNCTIONS = new Set(["sin", "cos", "tan", "cot", "sec", "csc", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh", "ln", "log", "exp"]);

const SYMBOLS: Record<string, string> = {
  pi: "pi",
  theta: "theta",
  varphi: "phi",
  phi: "phi",
  alpha: "alpha",
  beta: "beta",
  lambda: "lambda",
  cdot: "*",
  times: "*",
  le: "<=",
  leq: "<=",
  ge: ">=",
  geq: ">=",
  ne: "!=",
  neq: "!=",
  prime: "'",
  exponentialE: "e",
  ",": " ",
  ";": " ",
  ":": " ",
  "!": "",
  " ": " ",
  placeholder: "",
  left: "",
  right: "",
  mathrm: "",
  mathit: "",
};

class Reader {
  private i = 0;
  constructor(private readonly s: string) {}

  done(): boolean {
    return this.i >= this.s.length;
  }

  /** Text up to the end, or up to the `}` that closes the current group. */
  convert(untilBrace: boolean): string {
    let out = "";
    while (!this.done()) {
      const c = this.s[this.i]!;
      if (c === "}" && untilBrace) {
        this.i++;
        return out;
      }
      if (c === "\\") out += this.command();
      else if (c === "{") {
        this.i++;
        out += this.convert(true);
      } else if (c === "^") {
        this.i++;
        const exp = this.argument();
        out += /^\(?'+\)?$/.test(exp) ? exp.replace(/[()]/g, "") : "^" + exp;
      } else if (c === "_") {
        this.i++;
        out += this.argument(true);
      } else {
        out += c;
        this.i++;
      }
    }
    return out;
  }

  private skipSpaces(): void {
    while (this.s[this.i] === " ") this.i++;
  }

  /** One argument: a `{group}` or a single character or command. */
  private raw(): string {
    this.skipSpaces();
    if (this.s[this.i] === "{") {
      this.i++;
      return this.convert(true);
    }
    if (this.s[this.i] === "\\") return this.command();
    const ch = this.s[this.i] ?? "";
    this.i++;
    return ch;
  }

  private argument(subscript = false): string {
    const inner = this.raw();
    if (subscript) return inner; // C_1 is read as C1
    return inner.length === 1 || /^[0-9]+$/.test(inner) ? inner : `(${inner})`;
  }

  private command(): string {
    this.i++; // the backslash
    let name = "";
    const first = this.s[this.i] ?? "";
    if (/[A-Za-z]/.test(first)) {
      while (/[A-Za-z]/.test(this.s[this.i] ?? "")) name += this.s[this.i++];
    } else {
      name = first;
      this.i++;
    }
    if (name === "frac" || name === "dfrac" || name === "tfrac") {
      const a = this.raw();
      const b = this.raw();
      return `(${a})/(${b})`;
    }
    if (name === "sqrt") {
      this.skipSpaces();
      if (this.s[this.i] === "[") {
        const end = this.s.indexOf("]", this.i);
        const n = this.s.slice(this.i + 1, end);
        this.i = end + 1;
        return `(${this.raw()})^(1/(${n}))`;
      }
      return `sqrt(${this.raw()})`;
    }
    if (name === "text" || name === "operatorname" || name === "mathrm") {
      const inner = this.raw();
      return inner === "and" || inner === "or" ? ` ${inner} ` : inner;
    }
    if (name === "left" || name === "right") {
      this.skipSpaces();
      if (this.s[this.i] === ".") {
        this.i++;
        return "";
      }
      return "";
    }
    if (FUNCTIONS.has(name)) return name;
    if (name in SYMBOLS) return SYMBOLS[name]!;
    if (name === "{" || name === "}") return name === "{" ? "(" : ")";
    return "";
  }
}

export function latexToEngine(latex: string): string {
  const out = new Reader(latex).convert(false);
  return out.replace(/\s+/g, " ").trim();
}
