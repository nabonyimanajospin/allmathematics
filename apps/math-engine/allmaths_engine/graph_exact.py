"""Exact coordinates for the roots and intersections that the grapher finds numerically.

The browser finds candidates (x close to a zero of f, or of f - g). Here each candidate is made exact, or refused:

1. when SymPy can list every real solution of the equation, the solution closest to the candidate is used;
2. otherwise (sin(x) = 0 has infinitely many) the candidate is recognised as a rational multiple of pi, a radical or e, and the guess is
   accepted only if it satisfies the equation exactly (or to 1e-12 after the same substitution).

A candidate that cannot be made exact stays approximate in the browser; nothing is ever shown as exact without this check.
"""

from __future__ import annotations

import re
from typing import Any

import sympy as sp

from .errors import EngineError
from .parser import parse

MAX_CANDIDATES = 24
MAX_LINES = 24


def _real_x(expr: sp.Expr, params: dict[str, sp.Expr]) -> tuple[sp.Expr, sp.Symbol]:
    X = sp.Symbol("x", real=True)
    subs: dict[sp.Basic, sp.Basic] = {}
    for s in expr.free_symbols:
        if s.name == "x":
            subs[s] = X
        elif s.name in params:
            subs[s] = params[s.name]
    return expr.subs(subs), X


def _read(text: str, params: dict[str, sp.Expr]) -> tuple[sp.Expr, sp.Symbol]:
    if len(text) > 200 or not re.fullmatch(r"[A-Za-z0-9_+\-*/^(). ,]*", text):
        raise ValueError("bad expression")
    try:
        value = parse(text.strip(), fmt="text").value
    except EngineError as exc:
        raise ValueError(exc.message) from None
    if isinstance(value, sp.Tuple):
        raise ValueError("not an expression")
    expr, X = _real_x(value, params)
    leftover = expr.free_symbols - {X}
    if leftover:
        raise ValueError("unknown letters")
    return expr, X


def _exact_zero(h: sp.Expr, X: sp.Symbol, x0: float, cache: dict[sp.Expr, Any]) -> sp.Expr | None:
    if h not in cache:
        try:
            cache[h] = sp.solveset(h, X, domain=sp.S.Reals)
        except Exception:  # noqa: BLE001 - SymPy may fail on unusual equations; then we fall back to recognising the value
            cache[h] = None
    sols = cache[h]
    if isinstance(sols, sp.FiniteSet):
        best = None
        for s in sols:
            try:
                d = abs(float(s) - x0)
            except TypeError:
                continue
            if d < 1e-5 * max(1.0, abs(x0)) and (best is None or d < best[0]):
                best = (d, s)
        if best is not None:
            return sp.simplify(best[1])
    # recognise the value
    for guess in (
        sp.nsimplify(x0, [sp.pi], tolerance=1e-10, rational=False),
        sp.nsimplify(x0, [sp.E], tolerance=1e-10, rational=False),
        sp.nsimplify(x0, tolerance=1e-10, rational=False),
    ):
        try:
            if abs(float(guess) - x0) > 1e-7 * max(1.0, abs(x0)):
                continue
            residue = sp.simplify(h.subs(X, guess))
            if residue == 0:
                return sp.simplify(guess)
        except Exception:  # noqa: BLE001
            continue
    return None


def exact_points(payload: dict[str, Any]) -> dict[str, Any]:
    """payload: {"lines": {"1": "x^2-4"}, "params": {"a": "3/2"}, "candidates": [{"lines": [1] | [1, 2], "x": 2.0}]}"""
    params: dict[str, sp.Expr] = {}
    for name, val in (payload.get("params") or {}).items():
        if re.fullmatch(r"[a-z]", str(name)) and re.fullmatch(r"-?\d+(/\d+)?", str(val)):
            params[str(name)] = sp.Rational(str(val))
    lines: dict[int, sp.Expr] = {}
    X = sp.Symbol("x", real=True)
    for key, text in list((payload.get("lines") or {}).items())[:MAX_LINES]:
        try:
            lines[int(key)], X = _read(str(text), params)
        except (ValueError, TypeError):
            continue
    cache: dict[sp.Expr, Any] = {}
    out: list[dict[str, Any]] = []
    for cand in list(payload.get("candidates") or [])[:MAX_CANDIDATES]:
        try:
            ids = [int(i) for i in cand["lines"]]
            x0 = float(cand["x"])
            if not all(i in lines for i in ids) or len(ids) not in (1, 2):
                continue
            h = lines[ids[0]] if len(ids) == 1 else lines[ids[0]] - lines[ids[1]]
            xe = _exact_zero(sp.simplify(h), X, x0, cache)
            if xe is None:
                continue
            ye = sp.simplify(lines[ids[0]].subs(X, xe)) if len(ids) == 2 else sp.Integer(0)
            if len(ids) == 1:
                check = sp.simplify(lines[ids[0]].subs(X, xe))
                if check != 0:
                    continue
            if ye.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or not (xe.is_real is not False):
                continue
            out.append({"lines": ids, "x": float(xe), "x_latex": sp.latex(xe), "y_latex": sp.latex(ye), "x_text": str(xe), "y_text": str(ye)})
        except Exception:  # noqa: BLE001 - one bad candidate must not spoil the others
            continue
    return {"points": out}
