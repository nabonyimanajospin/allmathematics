"""Equality of two expressions on a curve or surface given implicitly by F = 0.

Implicit derivatives can be written in many equivalent ways that differ as formulas but agree on the curve
(for example ``dy/dx = -x/y`` and ``dy/dx = -x/sqrt(1-x^2)`` on the circle). To judge such answers fairly the two
expressions are compared at points that really lie on the curve.
"""

from __future__ import annotations

import random

import mpmath as mp
import sympy as sp
from mpmath.libmp import NoConvergence

mp.mp.dps = 40

_GUESSES = [sp.Rational(1, 2), sp.Integer(1), sp.Integer(2), sp.Integer(-1), sp.Integer(3), sp.Rational(-1, 2), sp.Integer(5)]


def _symbol(name: str) -> sp.Symbol:
    return sp.Symbol(name, real=True)


def curve_points(
    equation: sp.Expr,
    dependent: str,
    ranges: dict[str, tuple[float, float]],
    count: int = 16,
    seed: int = 3,
) -> list[dict[sp.Symbol, sp.Expr]]:
    """Points (as exact-ish Float assignments) with F = 0, found by solving for the dependent variable."""
    rng = random.Random(seed)
    dep = _symbol(dependent)
    others = sorted((equation.free_symbols - {dep}), key=lambda s: s.name)
    found: list[dict[sp.Symbol, sp.Expr]] = []
    attempts = 0
    while len(found) < count and attempts < count * 12:
        attempts += 1
        pt: dict[sp.Symbol, sp.Expr] = {}
        for s in others:
            lo, hi = ranges.get(s.name, (0.5, 2.5))
            pt[s] = sp.Rational(round(rng.uniform(lo, hi) * 100), 100)
        f = equation.subs(pt)
        for guess in _GUESSES + [sp.Float(rng.uniform(0.2, 3.0))]:
            try:
                root = sp.nsolve(f, dep, guess, tol=1e-30, maxsteps=60, prec=40)
            except (ValueError, ZeroDivisionError, TypeError, NoConvergence):
                continue
            if root.is_real and abs(sp.N(f.subs(dep, root), 40)) < 1e-25:
                found.append({**pt, dep: root})
                break
    return found


def equal_on_curve(
    a: sp.Expr,
    b: sp.Expr,
    equation: sp.Expr,
    dependent: str,
    ranges: dict[str, tuple[float, float]] | None = None,
) -> bool | None:
    """True/False when decided; None when too few points of the curve could be found."""
    pts = curve_points(equation, dependent, ranges or {})
    if len(pts) < 5:
        return None
    decided = 0
    for pt in pts:
        try:
            va = sp.N(a.subs(pt), 30)
            vb = sp.N(b.subs(pt), 30)
        except (ZeroDivisionError, TypeError, ValueError):
            continue
        if not (va.is_number and vb.is_number) or va.has(sp.nan, sp.zoo, sp.oo) or vb.has(sp.nan, sp.zoo, sp.oo):
            continue
        decided += 1
        if abs(va - vb) > sp.Float("1e-18") * (1 + abs(va)):
            return False
    return True if decided >= 5 else None
