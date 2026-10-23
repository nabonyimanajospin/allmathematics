"""Derivatives with the rule used at every step (sum, constant multiple, product, quotient, power, chain, exponential)."""

from __future__ import annotations

import sympy as sp

from .types import Solution, SolverError, Step, eng, tex

# derivative of f(u) with respect to u, for the elementary functions
_OUTER: dict[type, tuple[str, object]] = {
    sp.sin: ("sine", lambda u: sp.cos(u)),
    sp.cos: ("cosine", lambda u: -sp.sin(u)),
    sp.tan: ("tangent", lambda u: 1 / sp.cos(u) ** 2),
    sp.cot: ("cotangent", lambda u: -1 / sp.sin(u) ** 2),
    sp.exp: ("exponential", lambda u: sp.exp(u)),
    sp.log: ("natural logarithm", lambda u: 1 / u),
    sp.atan: ("arctangent", lambda u: 1 / (1 + u**2)),
    sp.asin: ("arcsine", lambda u: 1 / sp.sqrt(1 - u**2)),
    sp.acos: ("arccosine", lambda u: -1 / sp.sqrt(1 - u**2)),
    sp.sinh: ("hyperbolic sine", lambda u: sp.cosh(u)),
    sp.cosh: ("hyperbolic cosine", lambda u: sp.sinh(u)),
    sp.tanh: ("hyperbolic tangent", lambda u: 1 / sp.cosh(u) ** 2),
}

MAX_STEPS = 60


def _d(f: sp.Expr, x: sp.Symbol) -> str:
    return rf"\dfrac{{d}}{{d{tex(x)}}}\left[{tex(f)}\right]"


class _Stepper:
    def __init__(self, x: sp.Symbol) -> None:
        self.x = x
        self.steps: list[Step] = []

    def add(self, title: str, latex: str) -> None:
        if len(self.steps) >= MAX_STEPS:
            raise SolverError("This derivative is too long to show step by step.", "too_long")
        self.steps.append(Step(title, latex))

    def diff(self, f: sp.Expr) -> sp.Expr:
        x = self.x
        if not f.has(x):
            self.add("The derivative of a constant is 0.", rf"{_d(f, x)}=0")
            return sp.Integer(0)
        if f == x:
            self.add("The derivative of the variable itself is 1.", rf"{_d(f, x)}=1")
            return sp.Integer(1)

        if f.is_Add:
            terms = list(f.args)
            self.add("Sum rule: differentiate each term separately.", rf"{_d(f, x)}=" + "+".join(_d(t, x) for t in terms))
            parts = [self.diff(t) for t in terms]
            total = sp.Add(*parts)
            self.add("Add the derivatives of the terms.", rf"{_d(f, x)}={tex(total)}")
            return total

        if f.is_Mul:
            const, rest = f.as_independent(x)
            if const != 1:
                self.add("Constant multiple rule: a constant factor stays in front.", rf"{_d(f, x)}={tex(const)}\cdot{_d(rest, x)}")
                return const * self.diff(rest)
            num, den = sp.fraction(f)
            if den.has(x) and not num == 1 and (den.is_Pow is False or den.exp.is_Integer):
                return self.quotient(f, num, den)
            args = list(f.args)
            u, v = args[0], sp.Mul(*args[1:])
            self.add("Product rule: (uv)' = u'v + uv'.", rf"u={tex(u)},\quad v={tex(v)}")
            du, dv = self.diff(u), self.diff(v)
            res = du * v + u * dv
            self.add("Put the pieces in the product rule.", rf"{_d(f, x)}={tex(du)}\cdot\left({tex(v)}\right)+\left({tex(u)}\right)\cdot\left({tex(dv)}\right)")
            return res

        if f.is_Pow:
            base, ex = f.args
            if not ex.has(x):
                if base == x:
                    self.add("Power rule: d/dx[xⁿ] = n·xⁿ⁻¹.", rf"{_d(f, x)}={tex(ex * x ** (ex - 1))}")
                    return ex * x ** (ex - 1)
                self.add("Power rule with the chain rule: d/dx[uⁿ] = n·uⁿ⁻¹·u'.", rf"u={tex(base)},\quad n={tex(ex)}")
                du = self.diff(base)
                self.add("Put the pieces together.", rf"{_d(f, x)}={tex(ex)}\left({tex(base)}\right)^{{{tex(ex - 1)}}}\cdot\left({tex(du)}\right)")
                return ex * base ** (ex - 1) * du
            if not base.has(x):
                if base == sp.E:
                    self.add("Exponential rule with the chain rule: d/dx[eᵘ] = eᵘ·u'.", rf"u={tex(ex)}")
                    du = self.diff(ex)
                    return sp.exp(ex) * du
                self.add("Exponential rule with the chain rule: d/dx[aᵘ] = aᵘ·ln a·u'.", rf"a={tex(base)},\quad u={tex(ex)}")
                du = self.diff(ex)
                self.add("Put the pieces together.", rf"{_d(f, x)}={tex(f)}\cdot\ln\left({tex(base)}\right)\cdot\left({tex(du)}\right)")
                return f * sp.log(base) * du
            self.add("Both the base and the exponent contain the variable: write f = e^(g·ln u) and differentiate.", rf"{tex(f)}=e^{{{tex(ex)}\ln\left({tex(base)}\right)}}")
            res = sp.diff(f, x)
            self.add("Result of the logarithmic differentiation.", rf"{_d(f, x)}={tex(res)}")
            return res

        if f.func in _OUTER and len(f.args) == 1:
            name, outer = _OUTER[f.func]
            u = f.args[0]
            deriv = outer(u)  # type: ignore[operator]
            if u == x:
                self.add(f"Derivative of the {name} function.", rf"{_d(f, x)}={tex(deriv)}")
                return deriv
            self.add(f"Chain rule: differentiate the {name} function, then multiply by the derivative of the inside.", rf"u={tex(u)},\quad \dfrac{{d}}{{du}}\left[{tex(f.func(sp.Symbol('u')))}\right]={tex(outer(sp.Symbol('u')))}")  # type: ignore[operator]
            du = self.diff(u)
            self.add("Multiply the outer derivative (with u put back) by u'.", rf"{_d(f, x)}={tex(deriv)}\cdot\left({tex(du)}\right)")
            return deriv * du

        if f.func == sp.Abs:
            res = sp.diff(f, x)
            self.add("Derivative of the absolute value (for u ≠ 0).", rf"{_d(f, x)}={tex(res)}")
            return res
        raise SolverError("I do not know a rule for this function yet.", "unsupported")

    def quotient(self, f: sp.Expr, num: sp.Expr, den: sp.Expr) -> sp.Expr:
        self.add("Quotient rule: (u/v)' = (u'v − uv')/v².", rf"u={tex(num)},\quad v={tex(den)}")
        du, dv = self.diff(num), self.diff(den)
        self.add("Put the pieces in the quotient rule.", rf"{_d(f, self.x)}=\dfrac{{\left({tex(du)}\right)\left({tex(den)}\right)-\left({tex(num)}\right)\left({tex(dv)}\right)}}{{\left({tex(den)}\right)^2}}")
        return (du * den - num * dv) / den**2


def differentiate(f: sp.Expr, x: sp.Symbol, order: int = 1) -> Solution:
    """The derivative of f with respect to x, with its steps; the result is checked against SymPy's own derivative."""
    steps: list[Step] = []
    current = f
    for k in range(order):
        st = _Stepper(x)
        raw = st.diff(current)
        simplified = sp.simplify(raw)
        reference = sp.diff(current, x)
        if sp.simplify(simplified - reference) != 0:
            # the step engine and SymPy disagree: never show a doubtful result
            raise SolverError("I could not verify this derivative step by step.", "unverified")
        if order > 1:
            steps.append(Step(f"Derivative number {k + 1}.", rf"\dfrac{{d}}{{d{tex(x)}}}\left[{tex(current)}\right]"))
        steps.extend(st.steps)
        steps.append(Step("Simplify.", rf"{tex(simplified)}"))
        current = simplified
    sym = rf"\dfrac{{d^{{{order}}}}}{{d{tex(x)}^{{{order}}}}}" if order > 1 else rf"\dfrac{{d}}{{d{tex(x)}}}"
    return Solution(
        operation="derivative",
        question_latex=rf"{sym}\left[{tex(f)}\right]",
        answer_latex=tex(current),
        answer_text=eng(current),
        steps=steps,
        notes=["The result was checked by differentiating with an independent method."],
    )
