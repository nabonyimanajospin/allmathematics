"""Convert the LaTeX subset produced by MathLive (and typed by students) into the engine's text syntax.

This is a small, explicit translator, not a general LaTeX parser. Anything it does not recognise raises
ParseError, so unknown input is never silently misread.
"""

from __future__ import annotations

import re

from .errors import ParseError

# Commands whose argument is simply passed through (decoration, not meaning).
_PASS_THROUGH = {
    "vec", "hat", "mathbf", "mathrm", "mathit", "boldsymbol", "text", "mathbb", "overrightarrow",
    "displaystyle", "textstyle",
}
_SPACES = {",", ";", ":", "!", " ", "quad", "qquad", "enspace", "thinspace"}
_GREEK = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta", "vartheta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "rho", "sigma", "tau", "phi", "varphi", "chi",
    "psi", "omega",
}
_FUNCTIONS = {
    "sin", "cos", "tan", "cot", "sec", "csc", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
    "ln", "exp", "log",
}
_TOKEN = re.compile(r"\\[A-Za-z]+|\\.|[{}\[\]]|[^\\{}\[\]]", re.DOTALL)

MAX_LATEX_LENGTH = 400


def _matrix_to_tuple(m: re.Match[str]) -> str:
    body = m.group(2)
    rows = [r for r in re.split(r"\\\\", body) if r.strip()]
    cells: list[str] = []
    for row in rows:
        cells.extend(c.strip() for c in row.split("&") if c.strip())
    if not cells:
        raise ParseError("The vector is empty.", "empty_vector")
    return "(" + ",".join(cells) + ")"


def latex_to_text(src: str) -> str:
    if len(src) > MAX_LATEX_LENGTH:
        raise ParseError("The answer is too long.", "too_long")
    src = re.sub(r"\\begin\{([pbv]?matrix)\}(.*?)\\end\{\1\}", _matrix_to_tuple, src, flags=re.DOTALL)
    tokens = _TOKEN.findall(src)
    out, pos = _convert(tokens, 0, closing=None)
    if pos != len(tokens):
        raise ParseError("Unbalanced braces in the answer.", "unbalanced")
    return out


def _read_group(tokens: list[str], i: int) -> tuple[str, int]:
    """Read one argument: either {...} or a single token. Returns (converted text, next index)."""
    while i < len(tokens) and tokens[i].isspace():
        i += 1
    if i >= len(tokens):
        raise ParseError("A part of the answer is missing an argument.", "missing_argument")
    if tokens[i] == "{":
        text, j = _convert(tokens, i + 1, closing="}")
        return text, j
    text, j = _convert_one(tokens, i)
    return text, j


def _convert(tokens: list[str], i: int, closing: str | None) -> tuple[str, int]:
    """Convert until the matching closing brace (consumed) or end of input."""
    parts: list[str] = []
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if closing is not None and t == closing:
            return "(" + "".join(parts) + ")" if closing == "}" else "".join(parts), i + 1
        if t == "}":
            raise ParseError("Unbalanced braces in the answer.", "unbalanced")
        piece, i = _convert_one(tokens, i)
        parts.append(piece)
    if closing is not None:
        raise ParseError("Unbalanced braces in the answer.", "unbalanced")
    return "".join(parts), i


def _convert_one(tokens: list[str], i: int) -> tuple[str, int]:
    t = tokens[i]
    n = len(tokens)
    if t == "{":
        text, j = _convert(tokens, i + 1, closing="}")
        return text, j
    if t == "^":
        # exponent: ^{...} or ^x ; degree sign handled separately
        j = i + 1
        while j < n and tokens[j].isspace():
            j += 1
        if j < n and tokens[j] == "\\circ":
            return "*(pi/180)", j + 1
        if j < n and tokens[j] == "{" and j + 1 < n and tokens[j + 1] == "\\circ":
            if j + 2 < n and tokens[j + 2] == "}":
                return "*(pi/180)", j + 3
        arg, j = _read_group(tokens, i + 1)
        if not arg.startswith("("):
            arg = "(" + arg + ")"
        return "^" + arg, j
    if t == "_":
        arg, j = _read_group(tokens, i + 1)
        arg = arg.strip("()")
        if not re.fullmatch(r"[A-Za-z0-9]+", arg):
            raise ParseError("Subscripts may only contain letters and digits.", "bad_subscript")
        return "_" + arg, j
    if t.startswith("\\"):
        cmd = t[1:]
        if cmd in {"frac", "dfrac", "tfrac"}:
            a, j = _read_group(tokens, i + 1)
            b, j = _read_group(tokens, j)
            return f"(({a})/({b}))", j
        if cmd == "sqrt":
            j = i + 1
            if j < n and tokens[j] == "[":
                k = j + 1
                idx = []
                while k < n and tokens[k] != "]":
                    idx.append(tokens[k])
                    k += 1
                if k >= n:
                    raise ParseError("Unbalanced bracket in a root.", "unbalanced")
                a, j = _read_group(tokens, k + 1)
                return f"(({a})^(1/({''.join(idx)})))", j
            a, j = _read_group(tokens, j)
            return f"sqrt({a})", j
        if cmd == "left" or cmd == "right":
            if i + 1 >= n:
                raise ParseError("A delimiter is missing.", "missing_argument")
            d = tokens[i + 1]
            if d in {"(", ")", "[", "]"}:
                return d, i + 2
            if d == "|":
                return ("abs(" if cmd == "left" else ")"), i + 2
            if d == "\\langle":
                return "(", i + 2
            if d == "\\rangle":
                return ")", i + 2
            if d == ".":
                return "", i + 2
            raise ParseError("Unsupported delimiter in the answer.", "unsupported")
        if cmd == "lvert":
            return "abs(", i + 1
        if cmd == "rvert":
            return ")", i + 1
        if cmd == "langle":
            return "(", i + 1
        if cmd == "rangle":
            return ")", i + 1
        if cmd in {"cdot", "times", "ast"}:
            return "*", i + 1
        if cmd == "div":
            return "/", i + 1
        if cmd == "pi":
            return " pi ", i + 1
        if cmd in _GREEK:
            return f" {cmd} ", i + 1
        if cmd in _FUNCTIONS:
            return f" {cmd} ", i + 1
        if cmd == "operatorname":
            a, j = _read_group(tokens, i + 1)
            return f" {a.strip('()')} ", j
        if cmd in _PASS_THROUGH:
            a, j = _read_group(tokens, i + 1)
            return a.strip("()") if re.fullmatch(r"\([A-Za-z0-9_]+\)", a) else a, j
        if cmd in _SPACES:
            return " ", i + 1
        if cmd == "\\":
            return " ", i + 1
        if cmd in {"le", "ge", "neq", "infty", "sum", "int", "lim", "partial", "nabla"}:
            raise ParseError(f"The symbol \\{cmd} cannot be used in this kind of answer.", "unsupported")
        raise ParseError(f"I do not understand \\{cmd} in the answer.", "unsupported")
    if t in "[]":
        return t, i + 1
    return t, i + 1
