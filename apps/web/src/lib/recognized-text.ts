/** Turns what a text reader returns into the typed form the solver understands. */
export function cleanRecognized(raw: string): string {
  return raw
    .replace(/[×·✕]/g, "*")
    .replace(/[÷]/g, "/")
    .replace(/[−–—]/g, "-")
    .replace(/[“”"]/g, "")
    .replace(/√\s*(\d+|[a-z])/g, "sqrt($1)")
    .replace(/√/g, "sqrt")
    .replace(/π/g, "pi")
    .replace(/[|]/g, "")
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l !== "")
    .join(", ")
    .replace(/\s+/g, " ")
    .trim();
}
