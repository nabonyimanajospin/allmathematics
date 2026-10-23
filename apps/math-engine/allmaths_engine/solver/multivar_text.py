"""Reads multivariable problems written in words and hands them to `multivar`.

    partial derivative of x^2*y wrt x [at (1, 2)]        gradient of x^2 + y^2 [at (1, 2)]
    directional derivative of x*y at (1, 2) in the direction (3, 4)
    critical points of x^3 - 3*x*y + y^3                  maximize x*y subject to x + y = 10
    double integral of x*y over x from 0 to 1, y from 0 to x
    triple integral of x + y + z over x from 0 to 1, y from 0 to 1, z from 0 to 1
    double integral of x^2 + y^2 in polar coordinates over r from 0 to 2, theta from 0 to 2*pi
    line integral of (-y, x) along (cos(t), sin(t)) for t from 0 to 2*pi
    line integral of x*y along (t, t^2) for t from 0 to 1
"""

from __future__ import annotations

import re

import sympy as sp

from . import multivar
from .types import Solution, SolverError

_VAR = r"(?:theta|phi|rho|[a-z])"
_NUMBER_WORDS = {"first": 1, "second": 2, "third": 3}


def _split_top(text: str, seps: str = ",;") -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch in seps and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return [p.strip() for p in parts if p.strip()]


def _balanced(text: str, start: int) -> int:
    """Index just after the parenthesis that closes the one at `start`."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    raise SolverError("A bracket is not closed.", "parse")


def _point(at_text: str, syms: list[sp.Symbol]) -> dict[sp.Symbol, sp.Expr]:
    """'(1, 2)' (in the order x, y, z) or 'x = 1, y = 2'."""
    from . import _expr, _value

    t = at_text.strip().rstrip(".")
    if "=" in t:
        out: dict[sp.Symbol, sp.Expr] = {}
        for part in re.split(r"\s*(?:,|;|\band\b)\s*", t):
            m = re.match(rf"^({_VAR})\s*=\s*(.+)$", part.strip(), flags=re.I)
            if not m:
                raise SolverError("Write the point like (1, 2) or x = 1, y = 2.", "bad_point")
            out[sp.Symbol(m.group(1).lower(), real=True)] = _expr(m.group(2))
        return out
    v = _value(t)
    if not isinstance(v, sp.Tuple) and len(syms) == 1:
        return {syms[0]: v}  # type: ignore[dict-item]
    if not isinstance(v, sp.Tuple):
        raise SolverError("Write the point like (1, 2).", "bad_point")
    if len(v) != len(syms):
        raise SolverError(f"The point needs {len(syms)} numbers, one for each of {', '.join(s.name for s in syms)}.", "bad_point")
    return dict(zip(syms, v, strict=True))


def _function(text: str) -> sp.Expr:
    from . import _expr

    body = re.sub(r"^\s*(?:f|g|h)\s*(?:\([a-z, ]*\))?\s*=\s*", "", text.strip(), flags=re.I)
    return _expr(body)


def _partial(low: str, text: str) -> Solution | None:
    m = re.match(
        r"^(?:find |compute |calculate |what is )?(?:the )?(first |second |third )?(?:order )?partial(?: derivatives?)?\s*(?:of )?(.+?)\s+(?:with respect to|wrt|w\.r\.t\.?)\s+(.+?)(?:\s+at\s+(.+))?$",
        low,
    )
    if not m:
        return None
    f = _function(text[m.start(2) : m.end(2)])
    names = re.findall(rf"\b{_VAR}\b", m.group(3))
    names = [n for n in names if n not in ("and", "then")]
    if not names:
        raise SolverError("Say with respect to which variable, for example “wrt x”.", "parse")
    if "twice" in m.group(3):
        names.append(names[-1])
    order = _NUMBER_WORDS.get((m.group(1) or "").strip())
    if order and len(names) == 1:
        names = names * order
    vs = [sp.Symbol(n, real=True) for n in names]
    at = None
    if m.group(4):
        at = _point(text[m.start(4) : m.end(4)], multivar.order_vars(f.free_symbols | set(vs)))
    return multivar.partial(f, vs, at)


def _gradient(low: str, text: str) -> Solution | None:
    m = re.match(r"^(?:find |compute |calculate )?(?:the )?directional derivative\s*(?:of )?(.+?)\s+at\s+(.+?)\s+(?:in|along|toward|towards)\s+(?:the )?(?:direction )?(?:of )?(\(.+\))$", low)
    if m:
        from . import _value

        f = _function(text[m.start(1) : m.end(1)])
        vs = multivar.order_vars(f.free_symbols)
        at = _point(text[m.start(2) : m.end(2)], vs)
        d = _value(text[m.start(3) : m.end(3)])
        if not isinstance(d, sp.Tuple):
            raise SolverError("Write the direction like (3, 4).", "bad_vectors")
        return multivar.directional(f, at, list(d))
    m = re.match(r"^(?:find |compute |calculate )?(?:the )?(?:gradient|grad|nabla)\s*(?:vector )?(?:of )?(.+?)(?:\s+at\s+(.+))?$", low)
    if not m:
        return None
    f = _function(text[m.start(1) : m.end(1)])
    at = _point(text[m.start(2) : m.end(2)], multivar.order_vars(f.free_symbols)) if m.group(2) else None
    return multivar.gradient(f, at)


def _extrema(low: str, text: str) -> Solution | None:
    from . import _equations

    m = re.match(
        r"^(?:find |compute |determine )?(?:the )?(maximi[sz]e|minimi[sz]e|maximum|minimum|extrema|extreme values?|optimi[sz]e|max|min|maxima and minima)\s*(?:value )?(?:of )?(.+?)\s+(?:subject to|under the constraint|given that|with the constraint|constraint|such that|on the (?:curve|surface|circle|sphere|line|plane|ellipse))\s+(.+)$",
        low,
    )
    if m:
        word = m.group(1)
        goal = "max" if word.startswith(("maxim", "max")) and "and" not in word else "min" if word.startswith(("minim", "min")) and "and" not in word else "both"
        f = _function(text[m.start(2) : m.end(2)])
        cons = _equations(text[m.start(3) : m.end(3)])
        if not cons:
            raise SolverError("The constraint needs an = sign, for example x + y = 10.", "parse")
        return multivar.lagrange(f, cons, goal)
    m = re.match(
        r"^(?:find |compute |classify |determine )?(?:all |the )*(?:critical points|stationary points|local extrema|local maxima and minima|local max(?:ima)? and min(?:ima)?|relative extrema|extrema|extreme values|maxima and minima|saddle points|maximi[sz]e|minimi[sz]e|optimi[sz]e)\s*(?:and classify them )?(?:of |for )?(.+)$",
        low,
    )
    if m:
        return multivar.critical_points(_function(text[m.start(1) : m.end(1)]))
    return None


def _bounds(part: str) -> tuple[sp.Symbol, sp.Expr, sp.Expr]:
    from . import _expr

    m = re.match(rf"^({_VAR})\s+(?:from|=|in)\s+\[?\s*(.+?)\s+to\s+(.+?)\s*\]?$", part.strip(), flags=re.I)
    if m:
        return sp.Symbol(m.group(1).lower(), real=True), _expr(m.group(2)), _expr(m.group(3))
    m = re.match(rf"^(.+?)\s*(?:<=|≤)\s*({_VAR})\s*(?:<=|≤)\s*(.+)$", part.strip(), flags=re.I)
    if m:
        return sp.Symbol(m.group(2).lower(), real=True), _expr(m.group(1)), _expr(m.group(3))
    raise SolverError(f"I could not read the limits “{part.strip()[:40]}”. Write them like x from 0 to 1.", "parse")


def _multiple(low: str, text: str) -> Solution | None:
    from . import _expr

    system = None
    cm = re.search(r"\s*\bin (polar|cylindrical|spherical) coordinates\b", low)
    if cm:
        system = cm.group(1)
        text = text[: cm.start()] + text[cm.end() :]
        low = low[: cm.start()] + low[cm.end() :]
    m = re.match(r"^(?:find |compute |evaluate |calculate )?(?:the )?(double|triple|iterated)\s+integral\s*(?:of )?(.+?)\s+(?:over|for|where|with limits|with|on|in the region)\s+(.+)$", low)
    if not m:
        return None
    body = text[m.start(2) : m.end(2)].strip()
    parts = [p for p in re.split(r"\s*(?:,|;|\band\b)\s*", text[m.start(3) : m.end(3)]) if p.strip()]
    bounds = [_bounds(p) for p in parts]
    names = [b[0] for b in bounds]
    given: list[sp.Symbol] | None = None
    dm = re.match(rf"^(.*?)\s*\*?\s*((?:d{_VAR}\s*\*?\s*)+)$", body, flags=re.I)
    if dm:
        ds = [sp.Symbol(x.lower(), real=True) for x in re.findall(rf"d({_VAR})", dm.group(2), flags=re.I)]
        if sorted(s.name for s in ds) == sorted(s.name for s in names):
            body, given = dm.group(1), ds
    f = _expr(body)
    if given is not None:
        ordered = [next(b for b in bounds if b[0] == s) for s in given]
    else:
        remaining = list(bounds)
        outer_first: list[tuple[sp.Symbol, sp.Expr, sp.Expr]] = []
        chosen: set[sp.Symbol] = set()
        while remaining:
            ready = [b for b in remaining if ((b[1].free_symbols | b[2].free_symbols) & set(names)) <= chosen]
            if not ready:
                raise SolverError("The limits depend on each other in a circle. A limit can use only variables that are integrated after it.", "bad_bounds")
            pick = ready[0]
            outer_first.append(pick)
            chosen.add(pick[0])
            remaining.remove(pick)
        ordered = list(reversed(outer_first))
    kind = m.group(1)
    if kind == "double" and len(ordered) != 2:
        raise SolverError("A double integral needs limits for exactly 2 variables.", "bad_bounds")
    if kind == "triple" and len(ordered) != 3:
        raise SolverError("A triple integral needs limits for exactly 3 variables.", "bad_bounds")
    return multivar.multiple_integral(f, ordered, system)


def _line(low: str, text: str) -> Solution | None:
    from . import _expr, _value

    m = re.match(r"^(?:find |compute |evaluate |calculate )?(?:the )?(?:line integral|work done|work)\s*(?:of|by)?\s*(?:the )?(?:vector field |field |function )?(.+?)\s+(?:along|over|on|around)\s+(?:the )?(?:curve |path )?", low)
    if not m:
        return None
    field_text = re.sub(r"^\s*[A-Za-z]\s*=\s*", "", text[m.start(1) : m.end(1)])
    rest = text[m.end() :]
    rest = re.sub(r"^\s*[a-z]\s*\(\s*t\s*\)\s*=\s*", "", rest, flags=re.I)
    if not rest.startswith("("):
        raise SolverError("Write the path as (x(t), y(t)), for example (cos(t), sin(t)).", "parse")
    end = _balanced(rest, 0)
    curve = _value(rest[:end])
    if not isinstance(curve, sp.Tuple):
        raise SolverError("Write the path as (x(t), y(t)).", "parse")
    tail = rest[end:].strip().lstrip(",;").strip()
    tail = re.sub(r"^(?:for|with|where)\s+", "", tail, flags=re.I)
    t = sp.Symbol("t", real=True)
    rm = re.match(r"^t\s*(?:from|=|in|:)?\s*\[?\s*(.+?)\s*(?:\bto\b|,)\s*(.+?)\s*\]?$", tail, flags=re.I)
    if rm:
        a, b = _expr(rm.group(1)), _expr(rm.group(2))
    else:
        rm = re.match(r"^(.+?)\s*(?:<=|≤)\s*t\s*(?:<=|≤)\s*(.+)$", tail, flags=re.I)
        if not rm:
            raise SolverError("Say the range of t, for example t from 0 to 1.", "parse")
        a, b = _expr(rm.group(1)), _expr(rm.group(2))
    field = _value(field_text)
    return multivar.line_integral(field, list(curve), t, a, b)


def read(low: str, text: str) -> Solution | None:
    """The solution of a multivariable problem, or None when the text is not one."""
    for reader in (_partial, _gradient, _multiple, _line, _extrema):
        r = reader(low, text)
        if r:
            return r
    return None
