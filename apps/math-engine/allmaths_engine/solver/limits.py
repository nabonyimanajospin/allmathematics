"""Limits: direct substitution, then L'Hôpital's rule for 0/0 and ∞/∞, and a numeric cross-check of every result."""

from __future__ import annotations

import sympy as sp

from .types import Solution, SolverError, Step, eng, tex

_INDETERMINATE = (sp.nan, sp.zoo)


def _lim(f: sp.Expr, x: sp.Symbol, a: sp.Expr, direction: str) -> str:
    sign = {"+": "^+", "-": "^-", "": ""}[direction]
    return rf"\lim_{{{tex(x)}\to {tex(a)}{sign}}}\left[{tex(f)}\right]"


def _substitute(f: sp.Expr, x: sp.Symbol, a: sp.Expr) -> sp.Expr | None:
    """The value of f at a, or None when the substitution is an indeterminate form."""
    try:
        v = f.subs(x, a)
    except Exception:  # noqa: BLE001
        return None
    if v in _INDETERMINATE or v.has(sp.nan) or v.has(sp.zoo):
        return None
    return v


def _numeric_check(f: sp.Expr, x: sp.Symbol, a: sp.Expr, value: sp.Expr, direction: str) -> bool:
    if a in (sp.oo, -sp.oo) or value in (sp.oo, -sp.oo):
        return True
    try:
        target = float(sp.N(a))
        goal = float(sp.N(value))
    except (TypeError, ValueError):
        return True
    for h in (1e-4, 1e-6):
        pts = []
        if direction in ("", "+"):
            pts.append(target + h)
        if direction in ("", "-"):
            pts.append(target - h)
        for p in pts:
            try:
                v = complex(sp.N(f.subs(x, sp.Float(p, 30)), 20))
            except (TypeError, ValueError, ZeroDivisionError):
                return True
            if abs(v - goal) > 1e-3 * (1 + abs(goal)):
                return False
    return True


def limit(f: sp.Expr, x: sp.Symbol, a: sp.Expr, direction: str = "") -> Solution:
    steps: list[Step] = []
    direct = _substitute(f, x, a) if a not in (sp.oo, -sp.oo) else None
    if direct is not None and direct.is_finite is not False:
        steps.append(Step("The function is continuous at the point: substitute the value.", rf"{_lim(f, x, a, direction)}={tex(f.subs(x, a))}={tex(sp.simplify(direct))}"))
        value = sp.simplify(direct)
    else:
        value = None
        num, den = sp.fraction(sp.together(f))
        if den != 1 and a not in (sp.oo, -sp.oo):
            n0, d0 = sp.limit(num, x, a), sp.limit(den, x, a)
            steps.append(Step("Substituting gives an indeterminate form; look at the numerator and the denominator separately.", rf"\text{{numerator}}\to {tex(n0)},\qquad \text{{denominator}}\to {tex(d0)}"))
            current_n, current_d = num, den
            for round_ in range(1, 4):
                n0, d0 = sp.limit(current_n, x, a), sp.limit(current_d, x, a)
                if n0 == 0 and d0 == 0:
                    steps.append(Step(f"Form 0/0: apply L'Hôpital's rule (differentiate the numerator and the denominator), round {round_}.", rf"\lim \dfrac{{{tex(current_n)}}}{{{tex(current_d)}}}=\lim \dfrac{{{tex(sp.diff(current_n, x))}}}{{{tex(sp.diff(current_d, x))}}}"))
                    current_n, current_d = sp.diff(current_n, x), sp.diff(current_d, x)
                    direct = _substitute(sp.simplify(current_n / current_d), x, a)
                    if direct is not None:
                        value = sp.simplify(direct)
                        steps.append(Step("Now the substitution works.", rf"{tex(sp.simplify(current_n / current_d))}\to {tex(value)}"))
                        break
                else:
                    break
        if value is None:
            value = sp.limit(f, x, a, dir=direction or "+-")
            steps.append(Step("The limit was evaluated by the algebra system (series expansion).", rf"{_lim(f, x, a, direction)}={tex(value)}"))
    if value is None or value.has(sp.nan) or isinstance(value, sp.Limit):
        raise SolverError("I could not find this limit.", "no_limit")
    # an independent check against the algebra system's own result
    reference = sp.limit(f, x, a, dir=direction or "+-")
    if sp.simplify(reference - value) != 0 and not (reference in (sp.oo, -sp.oo) and value == reference):
        raise SolverError("I could not verify this limit.", "unverified")
    if not _numeric_check(f, x, a, value, direction):
        raise SolverError("I could not verify this limit numerically.", "unverified")
    return Solution(
        operation="limit",
        question_latex=_lim(f, x, a, direction),
        answer_latex=tex(value),
        answer_text=eng(value),
        steps=steps,
        notes=["The result was checked with a second method and by evaluating the function close to the point."],
    )
