"""Regions of the plane or of space written as conditions, e.g. ``x^2+y^2<=4 and y>0``.

Used for domains of definition and sets of discontinuity. Two regions are equal when they agree at every
sample point. The samples include a dense grid of integers and half-integers, so boundary curves such as
``x^2+y^2=1`` or ``x+y=0`` are tested exactly, and a strict inequality is told apart from a non-strict one.

Grammar:  or  <  and  <  relation ( <, <=, >, >=, =, != )  with optional chains such as ``-1<=x<=1``.
Words: ``true``/``all`` (everywhere) and ``false``/``empty`` (nowhere). Parentheses group conditions.
"""

from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

from .errors import ParseError
from .latex_in import latex_to_text
from .parser import normalize, parse

EPS = 1e-9
MAX_LENGTH = 300

_TRUE = {"true", "all", "everywhere", "r2", "r^2", "plane", "space", "r3", "r^3", "anywhere", "any"}
_FALSE = {"false", "empty", "nowhere", "none", "∅", "empty set"}

_REL_ORDER = ("<=", ">=", "!=", "==", "<", ">", "=")


@dataclass
class Region:
    """A compiled condition: call it with a dict of variable values to get True or False."""

    variables: list[str]
    _fn: object

    def contains(self, point: dict[str, float]) -> bool:
        return bool(self._fn(point))  # type: ignore[operator]


def _prepare(text: str, fmt: str) -> str:
    if len(text) > MAX_LENGTH:
        raise ParseError("The condition is too long.", "too_long")
    if fmt == "auto":
        fmt = "latex" if ("\\" in text or "{" in text) else "text"
    if fmt == "latex":
        text = latex_to_text(text)
    text = normalize(text)
    for a, b in (("≤", "<="), ("≥", ">="), ("≠", "!="), ("∧", " and "), ("∨", " or "), ("&&", " and "), ("||", " or ")):
        text = text.replace(a, b)
    return text.strip()


def _depth_map(text: str) -> list[int]:
    depth, out = 0, []
    for ch in text:
        if ch in "([{":
            out.append(depth)
            depth += 1
        elif ch in ")]}":
            depth -= 1
            out.append(depth)
        else:
            out.append(depth)
        if depth < 0:
            raise ParseError("Unbalanced parentheses in the condition.", "unbalanced")
    if depth != 0:
        raise ParseError("Unbalanced parentheses in the condition.", "unbalanced")
    return out


def _split_words(text: str, words: tuple[str, ...], symbols: tuple[str, ...] = ()) -> list[str]:
    """Split at top level (outside parentheses) on the given whole words or symbols."""
    depth = _depth_map(text)
    pieces: list[str] = []
    start = 0
    i = 0
    low = text.lower()
    while i < len(text):
        if depth[i] == 0:
            hit = None
            for sym in symbols:
                if text.startswith(sym, i):
                    hit = sym
                    break
            if hit is None:
                for w in words:
                    if low.startswith(w, i) and (i == 0 or not low[i - 1].isalnum()) and (
                        i + len(w) == len(text) or not low[i + len(w)].isalnum()
                    ):
                        hit = w
                        break
            if hit:
                pieces.append(text[start:i])
                i += len(hit)
                start = i
                continue
        i += 1
    pieces.append(text[start:])
    return [p.strip() for p in pieces]


def _wrapped(text: str) -> bool:
    if not text or text[0] != "(" or text[-1] != ")":
        return False
    depth = _depth_map(text)
    return all(d > 0 for d in depth[1:-1]) if len(text) > 2 else True


def _has_logic_or_relation(text: str) -> bool:
    depth = _depth_map(text)
    for i, ch in enumerate(text):
        if depth[i] == 0 and ch in "<>=!":
            return True
    return len(_split_words(text, ("and", "or"), (";", ","))) > 1


class _Compiler:
    def __init__(self, allowed: set[str]) -> None:
        self.allowed = allowed
        self.used: set[str] = set()

    def expr(self, text: str) -> object:
        text = text.strip()
        if not text:
            raise ParseError("A condition is incomplete.", "empty")
        or_parts = _split_words(text, ("or",))
        if len(or_parts) > 1:
            subs = [self.expr(p) for p in or_parts]
            return lambda pt: any(f(pt) for f in subs)  # type: ignore[operator]
        and_parts = _split_words(text, ("and",), (";", ","))
        if len(and_parts) > 1:
            subs = [self.expr(p) for p in and_parts]
            return lambda pt: all(f(pt) for f in subs)  # type: ignore[operator]
        return self.atom(text)

    def atom(self, text: str) -> object:
        low = text.lower().replace(" ", "")
        if low in _TRUE or text.lower() in _TRUE:
            return lambda pt: True
        if low in _FALSE or text.lower() in _FALSE:
            return lambda pt: False
        if text.lower().startswith("not "):
            inner = self.expr(text[4:])
            return lambda pt: not inner(pt)  # type: ignore[operator]
        if _wrapped(text) and _has_logic_or_relation(text[1:-1]):
            return self.expr(text[1:-1])
        return self.relation(text)

    def relation(self, text: str) -> object:
        depth = _depth_map(text)
        ops: list[tuple[int, str]] = []
        i = 0
        while i < len(text):
            if depth[i] == 0 and text[i] in "<>=!":
                for op in _REL_ORDER:
                    if text.startswith(op, i):
                        ops.append((i, op))
                        i += len(op) - 1
                        break
                else:
                    raise ParseError("I do not understand this condition.", "bad_relation")
            i += 1
        if not ops:
            raise ParseError("Each condition needs a comparison such as <, <=, > , >= or =.", "no_relation")
        sides: list[object] = []
        start = 0
        for pos, op in ops:
            sides.append(self.side(text[start:pos]))
            start = pos + len(op)
        sides.append(self.side(text[start:]))
        funcs = [fn for fn, _ in sides]  # type: ignore[misc]
        checks = [op for _, op in ops]

        def evaluate(pt: dict[str, float]) -> bool:
            try:
                vals = [f(pt) for f in funcs]
            except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                return False
            for v in vals:
                if isinstance(v, complex):
                    if abs(v.imag) > EPS:
                        return False
                if v != v or v in (math.inf, -math.inf):
                    return False
            vals = [v.real if isinstance(v, complex) else v for v in vals]
            for (a, b), op in zip(itertools.pairwise(vals), checks, strict=True):
                d = a - b
                ok = {
                    "<": d < -EPS,
                    "<=": d <= EPS,
                    ">": d > EPS,
                    ">=": d >= -EPS,
                    "=": abs(d) <= EPS,
                    "==": abs(d) <= EPS,
                    "!=": abs(d) > EPS,
                }[op]
                if not ok:
                    return False
            return True

        return evaluate

    def side(self, text: str) -> tuple[object, None]:
        parsed = parse(text, fmt="text", variables=self.allowed)
        value = parsed.value
        if isinstance(value, sp.Tuple):
            raise ParseError("A condition compares numbers, not vectors.", "vector_in_condition")
        assert isinstance(value, sp.Expr)
        names = sorted(s.name for s in value.free_symbols)
        self.used.update(names)
        fn = sp.lambdify([sp.Symbol(n, real=True) for n in names], value, modules="math")

        def call(pt: dict[str, float]) -> float | complex:
            return fn(*[pt[n] for n in names])

        return call, None


def compile_region(text: str, variables: list[str], fmt: str = "auto") -> Region:
    """Compile a condition on the given coordinate variables. Raises ParseError for unusable input."""
    prepared = _prepare(text, fmt)
    if not prepared:
        raise ParseError("The answer is empty.", "empty")
    comp = _Compiler(set(variables))
    fn = comp.expr(prepared)
    return Region(sorted(comp.used | set()) or list(variables), fn)


def sample_points(variables: list[str], seed: int = 11) -> list[dict[str, float]]:
    """Grid of half-integers plus random rationals. Boundaries through lattice points are hit exactly."""
    rng = random.Random(seed)
    n = len(variables)
    if n == 0:
        return [{}]
    if n == 1:
        axis = [i / 4 for i in range(-24, 25)]
        pts = [{variables[0]: v} for v in axis]
    else:
        step, lim = (Fraction(1, 2), 4) if n == 2 else (Fraction(1, 2), 3)
        axis = [float(step * k) for k in range(int(-lim / step), int(lim / step) + 1)]
        pts = [dict(zip(variables, combo, strict=True)) for combo in itertools.product(axis, repeat=n)]
    extra = 400 if n == 2 else 600
    for _ in range(extra):
        pts.append({v: float(Fraction(rng.randint(-60, 60), rng.choice([4, 5, 7, 10]))) for v in variables})
    return pts


def regions_equal(key: Region, student: Region, variables: list[str]) -> tuple[bool, dict[str, float] | None]:
    """Compare two regions on the sample points of the given coordinate variables."""
    for pt in sample_points(variables):
        full = {v: pt.get(v, 0.0) for v in variables}
        if key.contains(full) != student.contains(full):
            return False, full
    return True, None

