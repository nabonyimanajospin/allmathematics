"""Answers that are equations, directions or sets of points.

equation   two equations are the same when one is a non-zero constant multiple of the other
           (tangent planes, normal lines, circles, ...): ``x+2y-z=0`` and ``z=x+2y`` are equal.
direction  a vector is accepted when it is a non-zero multiple of the key (normal vectors).
points     an unordered set of points, written ``(0,0), (1,-1)`` or ``{(0,0); (1,-1)}``.
"""

from __future__ import annotations

import random

import sympy as sp

from .errors import ParseError
from .latex_in import latex_to_text
from .parser import normalize, parse

_NO_POINTS = {"none", "no point", "no points", "empty", "∅", "no critical point", "no critical points", "{}"}


def to_text(text: str, fmt: str = "auto") -> str:
    if fmt == "auto":
        fmt = "latex" if ("\\" in text or "{" in text) else "text"
    if fmt == "latex":
        text = latex_to_text(text)
    return normalize(text)


def _depth0_equals(text: str) -> list[int]:
    depth = 0
    out = []
    for i, ch in enumerate(text):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "=" and depth == 0:
            prev = text[i - 1] if i else ""
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if prev not in "<>!=" and nxt != "=":
                out.append(i)
    return out


def split_equation(text: str, fmt: str = "auto", variables: set[str] | None = None) -> tuple[sp.Expr, sp.Expr]:
    """Parse ``left = right`` into two expressions."""
    prepared = to_text(text, fmt)
    cuts = _depth0_equals(prepared)
    if len(cuts) != 1:
        raise ParseError("Write an equation with exactly one “=” sign.", "not_an_equation")
    left, right = prepared[: cuts[0]], prepared[cuts[0] + 1 :]
    pair: list[sp.Expr] = []
    for side in (left, right):
        value = parse(side, fmt="text", variables=variables).value
        if isinstance(value, sp.Tuple):
            raise ParseError("An equation compares numbers, not vectors.", "vector_in_equation")
        assert isinstance(value, sp.Expr)
        pair.append(value)
    return pair[0], pair[1]


def equation_poly(text: str, fmt: str = "auto", variables: set[str] | None = None) -> sp.Expr:
    """`left - right`. A key written without “=” means “expression = 0”."""
    prepared = to_text(text, fmt)
    if not _depth0_equals(prepared):
        value = parse(prepared, fmt="text", variables=variables).value
        assert isinstance(value, sp.Expr)
        return value
    left, right = split_equation(text, fmt, variables)
    return left - right


def equations_equivalent(student: sp.Expr, key: sp.Expr, coordinates: set[str]) -> bool:
    """True when student = λ·key for a non-zero constant λ (constant in the coordinates)."""
    if sp.simplify(student) == 0:
        return False
    if sp.simplify(key) == 0:
        return False
    ratio = sp.cancel(sp.together(student / key))
    coord_syms = {s for s in ratio.free_symbols if s.name in coordinates}
    if not coord_syms and ratio != 0:
        return True
    # numeric fallback: the ratio must be the same non-zero number at many random points
    rng = random.Random(7)
    symbols = sorted(student.free_symbols | key.free_symbols, key=lambda s: s.name)
    seen: sp.Expr | None = None
    valid = 0
    for _ in range(14):
        pt = {s: sp.Rational(rng.randint(-9, 9), rng.randint(1, 5)) for s in symbols}
        k = key.subs(pt)
        s = student.subs(pt)
        if k == 0:
            if s != 0:
                return False
            continue
        r = sp.nsimplify(s / k) if s != 0 else sp.Integer(0)
        if r == 0:
            return False
        if seen is None:
            seen = r
        elif sp.simplify(r - seen) != 0:
            return False
        valid += 1
    return valid >= 6


def directions_equivalent(student: sp.Tuple, key: sp.Tuple) -> bool:
    """student = λ·key with λ ≠ 0 (both non-zero vectors)."""
    if len(student) != len(key):
        return False
    if all(sp.simplify(c) == 0 for c in student) or all(sp.simplify(c) == 0 for c in key):
        return False
    for i in range(len(key)):
        for j in range(i + 1, len(key)):
            if sp.simplify(student[i] * key[j] - student[j] * key[i]) != 0:
                return False
    return True


def parse_points(text: str, fmt: str = "auto", variables: set[str] | None = None) -> list[sp.Tuple]:
    # braces here mean "a set", not LaTeX grouping: only a backslash switches to LaTeX
    mode = fmt if fmt != "auto" else ("latex" if "\\" in text else "text")
    prepared = to_text(text.replace("{", " ").replace("}", " ") if mode == "text" else text, mode).strip()
    if prepared.lower() in _NO_POINTS:
        return []
    points: list[sp.Tuple] = []
    depth = 0
    start = -1
    for i, ch in enumerate(prepared):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ParseError("Unbalanced parentheses.", "unbalanced")
            if depth == 0:
                value = parse(prepared[start : i + 1], fmt="text", variables=variables).value
                if not isinstance(value, sp.Tuple):
                    raise ParseError("Write each point with a comma, like (1, 2).", "bad_point")
                points.append(value)
    if depth != 0:
        raise ParseError("Unbalanced parentheses.", "unbalanced")
    if not points:
        raise ParseError("Write the points like (1, 2), (3, 4), or “none”.", "no_points")
    return points


def point_sets_equal(student: list[sp.Tuple], key: list[sp.Tuple]) -> tuple[bool, int]:
    """Unordered equality. Returns (equal, number of student points that match some key point)."""
    from .checker import exprs_equivalent  # local import: checker imports this module

    def same(p: sp.Tuple, q: sp.Tuple) -> bool:
        return len(p) == len(q) and all(exprs_equivalent(a, b)[0] for a, b in zip(p, q, strict=True))

    unused = list(range(len(key)))
    matched = 0
    for sp_ in student:
        for idx in unused:
            if same(sp_, key[idx]):
                unused.remove(idx)
                matched += 1
                break
    return (matched == len(student) == len(key)), matched
