"""Canonical LaTeX rendering of exact values (spec section 6.4: display fractions with \\dfrac)."""

from __future__ import annotations

import sympy as sp

from .vectors import clean


def expr_to_latex(x: sp.Expr) -> str:
    text = sp.latex(clean(x) if not x.free_symbols else x, fold_short_frac=False, mul_symbol=None)
    return text.replace("\\frac", "\\dfrac")


def value_to_latex(value: object) -> str:
    if isinstance(value, sp.Tuple):
        return "\\left(" + ", ".join(expr_to_latex(c) for c in value) + "\\right)"
    assert isinstance(value, sp.Expr)
    return expr_to_latex(value)
