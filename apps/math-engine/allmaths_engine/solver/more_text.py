"""Reads the problems of `more_ops` written in words.

    determinant of [[1,2],[3,4]]     inverse of [[2,0],[0,4]]     eigenvalues of [[2,1],[1,2]]     [[1,2],[3,4]] * [[0,1],[1,0]]
    solve x^2 - 4 > 0                tangent line to y = x^2 at x = 1     tangent plane to z = x*y at (1, 2)
    taylor series of sin(x) at 0 up to order 5     maclaurin series of e^x     sum of k^2 for k from 1 to 10
    partial fractions of 1/(x^2-1)   area between y = x and y = x^2     area under y = x^2 from 0 to 1
"""

from __future__ import annotations

import re

import sympy as sp

from . import more_ops
from .types import Solution, SolverError

_INF = {"infinity": "oo", "inf": "oo", "∞": "oo", "+infinity": "oo", "+inf": "oo"}


def _num(text: str) -> sp.Expr:
    from . import _expr

    t = text.strip().lower()
    return _expr(_INF.get(t, t))


def _fn(text: str) -> sp.Expr:
    from . import _expr

    body = re.sub(r"^\s*(?:y|f\s*\(\s*x\s*\)|g\s*\(\s*x\s*\))\s*=\s*", "", text.strip(), flags=re.I)
    return _expr(body)


def _matrix(low: str, text: str) -> Solution | None:
    if "[" not in text:
        return None
    return more_ops.read_matrix_problem(low, text)


def _inequality(low: str, text: str) -> Solution | None:
    from . import _expr, _pick_variable

    body = re.sub(r"^\s*(?:solve|find all x such that|find|for which x is)\s*(?:the inequality )?", "", text, flags=re.I)
    body = re.sub(r"\s+for\s+[a-z]\s*$", "", body, flags=re.I)
    if "->" in body or "→" in body:
        return None  # a limit such as lim x->0 is not an inequality
    m = re.match(r"^(.+?)\s*(<=|>=|≤|≥|<|>)\s*(.+)$", body)
    if not m or re.search(r"[<>≤≥=]", m.group(3)):
        return None
    op = {"≤": "<=", "≥": ">="}.get(m.group(2), m.group(2))
    lhs, rhs = _expr(m.group(1)), _expr(m.group(3))
    x = _pick_variable(lhs - rhs, None)
    if len((lhs - rhs).free_symbols) > 1:
        raise SolverError("An inequality with several letters is not supported: use one unknown.", "ambiguous")
    return more_ops.inequality(lhs, op, rhs, x)


def _tangent(low: str, text: str) -> Solution | None:
    from . import _expr, _value

    m = re.match(r"^(?:find |compute |give )?(?:the )?(tangent|normal)\s*(?:line|plane)?\s*(?:to|of|at|for)\s+(.+?)\s+at\s+(.+)$", low)
    if not m:
        return None
    kind = m.group(1)
    body = text[m.start(2) : m.end(2)]
    at = text[m.start(3) : m.end(3)]
    if re.match(r"^\s*z\s*=", body, flags=re.I) or ("plane" in low and kind == "tangent"):
        f = _expr(re.sub(r"^\s*z\s*=\s*", "", body, flags=re.I))
        x, y = sp.Symbol("x", real=True), sp.Symbol("y", real=True)
        if "=" in at:
            point: dict[sp.Symbol, sp.Expr] = {}
            for part in re.split(r"\s*(?:,|;|\band\b)\s*", at):
                mm = re.match(r"^([xy])\s*=\s*(.+)$", part.strip(), flags=re.I)
                if not mm:
                    raise SolverError("Write the point like (1, 2) or x = 1, y = 2.", "bad_point")
                point[sp.Symbol(mm.group(1).lower(), real=True)] = _expr(mm.group(2))
        else:
            v = _value(at)
            if not isinstance(v, sp.Tuple) or len(v) != 2:
                raise SolverError("Write the point like (1, 2).", "bad_point")
            point = {x: v[0], y: v[1]}
        if x not in point or y not in point:
            raise SolverError("Give both x and y of the point.", "bad_point")
        return more_ops.tangent_plane(f, point)
    f = _fn(body)
    a = _num(re.sub(r"^\s*x\s*=\s*", "", at.strip(), flags=re.I))
    return more_ops.tangent_line(f, a, kind == "normal")


def _taylor(low: str, text: str) -> Solution | None:
    m = re.match(r"^(?:find |compute |give )?(?:the )?(taylor|maclaurin)\b(?:\s+(?:series|polynomial|expansion))?\s*(?:of |for )?(.+)$", low)
    if not m:
        return None
    rest = text[m.start(2) : m.end(2)]
    order = 5
    om = re.search(r"[,;]?\s*(?:up to |to |of |until )?(?:order|degree)\s*(\d+)|[,;]?\s*(?:up to |with )?n\s*=\s*(\d+)", rest, flags=re.I)
    if om:
        order = int(om.group(1) or om.group(2))
        rest = rest[: om.start()] + rest[om.end() :]
    center: sp.Expr = sp.Integer(0)
    cm = re.search(r"[,;]?\s*(?:about|around|at|centered at|centred at)\s+(?:x\s*=\s*)?([^,;]+?)\s*$", rest, flags=re.I)
    if cm and m.group(1) == "taylor":
        center = _num(cm.group(1))
        rest = rest[: cm.start()]
    elif cm:
        rest = rest[: cm.start()]
    return more_ops.taylor(_fn(rest), center, order)


def _sum(low: str, text: str) -> Solution | None:
    from . import _expr

    m = re.match(r"^(?:find |compute |evaluate |calculate )?(?:the )?(?:sum|series|summation)\s*(?:of )?(.+?)\s+(?:for |where |with )?([a-z])\s*(?:from|=)\s*(\S+)\s+(?:to|until|up to)\s+(\S+)$", low)
    if not m:
        return None
    term = _expr(text[m.start(1) : m.end(1)])
    k = sp.Symbol(m.group(2), real=True)
    lo = _num(text[m.start(3) : m.end(3)])
    hi = _num(text[m.start(4) : m.end(4)])
    if lo == sp.oo or lo.free_symbols:
        raise SolverError("The first value of the index must be a number.", "bad_bounds")
    return more_ops.series_sum(term, k, lo, hi)


def _partial_fractions(low: str, text: str) -> Solution | None:
    m = re.match(r"^(?:find |compute |give )?(?:the )?(?:partial fractions?|partial fraction decomposition)\s*(?:of |for )?(.+)$", low) or re.match(r"^(?:decompose|split)\s+(.+?)\s+(?:into|in)\s+partial fractions?$", low)
    if not m:
        return None
    return more_ops.partial_fractions(_fn(text[m.start(1) : m.end(1)]))


def _area(low: str, text: str) -> Solution | None:
    m = re.match(r"^(?:find |compute |calculate )?(?:the )?area\s+(?:between|enclosed by|bounded by)\s+(?:the curves? )?(.+?)\s+and\s+(.+?)(?:\s+(?:from|between|for)\s+(?:x\s*=\s*)?(.+?)\s+(?:to|and)\s+(?:x\s*=\s*)?(.+?))?$", low)
    if m:
        a = _num(text[m.start(3) : m.end(3)]) if m.group(3) else None
        b = _num(text[m.start(4) : m.end(4)]) if m.group(4) else None
        return more_ops.area_between(_fn(text[m.start(1) : m.end(1)]), _fn(text[m.start(2) : m.end(2)]), a, b)
    m = re.match(r"^(?:find |compute |calculate )?(?:the )?area\s+under\s+(?:the curve )?(.+?)\s+(?:from|between)\s+(?:x\s*=\s*)?(.+?)\s+(?:to|and)\s+(?:x\s*=\s*)?(.+)$", low)
    if m:
        return more_ops.area_between(_fn(text[m.start(1) : m.end(1)]), sp.Integer(0), _num(text[m.start(2) : m.end(2)]), _num(text[m.start(3) : m.end(3)]))
    return None


def read(low: str, text: str) -> Solution | None:
    for reader in (_matrix, _tangent, _taylor, _sum, _partial_fractions, _area, _inequality):
        r = reader(low, text)
        if r:
            return r
    return None
