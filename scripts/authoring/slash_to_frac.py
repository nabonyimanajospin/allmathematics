"""Show every fraction with a horizontal bar: in the math of lessons and exercises, `a/b` becomes `\\dfrac{a}{b}`.

Only text between dollar signs is changed (engine input such as answers is never touched). Fractions inside
superscripts and subscripts use `\\frac`, everything else `\\dfrac`. The script is idempotent: run it after any build.
"""

from __future__ import annotations

import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BS = chr(92)

_ATOM = (
    r"(?:\\[A-Za-z]+(?:\{[^{}]*\})?"  # \pi, \sqrt{2}
    r"|\([^()]*\)"  # (x - y)
    r"|[A-Za-z0-9]+'*(?:_\{[^{}]*\}|_[A-Za-z0-9])?(?:\^\{[^{}]*\}|\^[A-Za-z0-9])?)"  # x, 12, y', c_2, y^2, x^{3}
)
_SLASH = re.compile(rf"(?<![\\A-Za-z0-9'_^])(?P<n>{_ATOM})\s*/\s*(?P<d>{_ATOM})")
_FUNCTIONS = re.compile(r"^\\(?:sin|cos|tan|cot|sec|csc|ln|log|exp|arcsin|arccos|arctan)$")
_SCRIPT = re.compile(r"(?P<head>[\^_])\{(?P<body>[^{}]*)\}")
_MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]*?\$", re.S)


def _strip(atom: str) -> str:
    return atom[1:-1] if atom.startswith("(") and atom.endswith(")") else atom


def _fraction(command: str):
    def repl(m: re.Match[str]) -> str:
        if _FUNCTIONS.match(m.group("n")) or _FUNCTIONS.match(m.group("d")):
            return m.group(0)  # a function name is not a numerator or a denominator: fix by hand
        return f"{command}{{{_strip(m.group('n'))}}}{{{_strip(m.group('d'))}}}"

    return repl


def convert_math(math: str) -> str:
    if "/" not in math:
        return math
    # superscripts and subscripts first (with the small fraction), including nested slash fractions like 1/(1-n)
    math = _SCRIPT.sub(lambda m: f"{m.group('head')}{{{_SLASH.sub(_fraction(BS + 'frac'), m.group('body'))}}}", math)
    return _SLASH.sub(_fraction(BS + "dfrac"), math)


_QUOTED = re.compile(r'^(?P<head>\s*(?:-\s+|[A-Za-z]+:\s+)?")(?P<body>.*)(?P<tail>"\s*)$')


def _plain(chunk: str) -> str:
    return _MATH.sub(lambda m: convert_math(m.group(0)), chunk)


def convert_text(text: str) -> str:
    """Plain and block scalars are converted as they are; a double-quoted YAML line writes every backslash twice."""
    out: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            out.extend(_plain("\n".join(buffer)).split("\n"))
            buffer.clear()

    for line in text.split("\n"):
        quoted = _QUOTED.match(line)
        if quoted and "$" in line:
            flush()
            body = _plain(quoted.group("body").replace(BS + BS, BS))
            out.append(quoted.group("head") + body.replace(BS, BS + BS) + quoted.group("tail"))
        else:
            buffer.append(line)
    flush()
    return "\n".join(out)


def run() -> int:
    changed = 0
    for pattern in ("lesson.yaml", "exercises.yaml"):
        for path in glob.glob(str(ROOT / "content" / "**" / pattern), recursive=True):
            text = Path(path).read_text(encoding="utf8")
            fixed = convert_text(text)
            if fixed != text:
                Path(path).write_text(fixed, encoding="utf8", newline="\n")
                changed += 1
    return changed


if __name__ == "__main__":
    print("files changed:", run())
