"""Integrals with steps, from SymPy's rule-based integrator (a tree of rules), always verified by differentiating the result."""

from __future__ import annotations

import sympy as sp
from sympy.integrals import manualintegrate as mi

from .types import Solution, SolverError, Step, eng, tex

MAX_STEPS = 40


def _int(f: sp.Expr, x: sp.Symbol) -> str:
    return rf"\int {tex(f)}\,d{tex(x)}"


class _Narrator:
    def __init__(self, x: sp.Symbol) -> None:
        self.x = x
        self.steps: list[Step] = []

    def add(self, title: str, latex: str) -> None:
        if len(self.steps) >= MAX_STEPS:
            raise SolverError("This integral is too long to show step by step.", "too_long")
        self.steps.append(Step(title, latex))

    def walk(self, rule: object) -> None:
        x = self.x
        name = type(rule).__name__
        f = getattr(rule, "integrand", None)
        if name == "ConstantRule":
            self.add("The integral of a constant is the constant times the variable.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "PowerRule":
            self.add("Power rule: ∫xⁿ dx = xⁿ⁺¹/(n+1) for n ≠ −1.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "ExpRule":
            self.add("Exponential rule.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "ReciprocalRule":
            self.add("The integral of 1/x is ln|x|.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name in {"SinRule", "CosRule", "TrigRule", "Sec2Rule", "Csc2Rule", "SecTanRule", "CscCotRule", "SinhRule", "CoshRule", "HyperbolicRule"}:
            self.add("A standard integral of a trigonometric or hyperbolic function.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "ArctanRule":
            self.add("A standard integral that gives an arctangent.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "ArcsinRule":
            self.add("A standard integral that gives an arcsine.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "AddRule":
            self.add("Sum rule: integrate each term separately.", rf"{_int(f, x)}=" + "+".join(_int(s.integrand, x) for s in rule.substeps))  # type: ignore[attr-defined]
            for s in rule.substeps:  # type: ignore[attr-defined]
                self.walk(s)
        elif name == "ConstantTimesRule":
            self.add("Constant multiple rule: take the constant out of the integral.", rf"{_int(f, x)}={tex(rule.constant)}\cdot{_int(rule.other, x)}")  # type: ignore[attr-defined]
            self.walk(rule.substep)  # type: ignore[attr-defined]
        elif name == "URule":
            u, uf = rule.u_var, rule.u_func  # type: ignore[attr-defined]
            self.add("Substitution: let u be the inside part.", rf"u={tex(uf)},\qquad du={tex(sp.diff(uf, x))}\,d{tex(x)}")
            self.add("Rewrite the integral in terms of u.", rf"{_int(f, x)}=\int {tex(rule.substep.integrand)}\,d{tex(u)}")  # type: ignore[attr-defined]
            self.walk(rule.substep)  # type: ignore[attr-defined]
            self.add("Put x back in place of u.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "PartsRule":
            self.add("Integration by parts: ∫u dv = uv − ∫v du.", rf"u={tex(rule.u)},\qquad dv={tex(rule.dv)}\,d{tex(x)}")  # type: ignore[attr-defined]
            self.add("Find v and du.", rf"v={tex(rule.v_step.eval())},\qquad du={tex(sp.diff(rule.u, x))}\,d{tex(x)}")  # type: ignore[attr-defined]
            if rule.second_step is not None:  # type: ignore[attr-defined]
                self.add("The remaining integral is easier.", rf"\int v\,du=\int {tex(rule.second_step.integrand)}\,d{tex(x)}")  # type: ignore[attr-defined]
                self.walk(rule.second_step)  # type: ignore[attr-defined]
            self.add("Combine.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "CyclicPartsRule":
            self.add("Integrate by parts twice: the original integral appears again, and we solve for it.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]
        elif name == "RewriteRule":
            self.add("Rewrite the integrand in an equivalent form.", rf"{tex(f)}={tex(rule.rewritten)}")  # type: ignore[attr-defined]
            self.walk(rule.substep)  # type: ignore[attr-defined]
        elif name == "AlternativeRule":
            self.walk(rule.alternatives[0])  # type: ignore[attr-defined]
        elif name == "DontKnowRule":
            raise SolverError("I cannot find an elementary antiderivative for this integral.", "no_antiderivative")
        else:
            self.add("Apply the matching standard method.", rf"{_int(f, x)}={tex(rule.eval())}")  # type: ignore[attr-defined]


def _antiderivative(f: sp.Expr, x: sp.Symbol) -> tuple[sp.Expr, list[Step]]:
    try:
        rule = mi.integral_steps(f, x)
        narrator = _Narrator(x)
        narrator.walk(rule)
        result = rule.eval()  # type: ignore[attr-defined]
        steps = narrator.steps
    except SolverError:
        raise
    except Exception:  # noqa: BLE001 - the rule engine may fail on exotic input; fall back to the full integrator without steps
        result = sp.integrate(f, x)
        if result.has(sp.Integral):
            raise SolverError("I cannot find an elementary antiderivative for this integral.", "no_antiderivative") from None
        steps = [Step("Integrate.", rf"{_int(f, x)}={tex(result)}")]
    if isinstance(result, sp.Integral) or result.has(sp.Integral):
        raise SolverError("I cannot find an elementary antiderivative for this integral.", "no_antiderivative")
    if sp.simplify(sp.diff(result, x) - f) != 0:
        # compare numerically as a second chance (simplify can miss equal forms)
        pts = [sp.Rational(3, 10), sp.Rational(7, 10), sp.Rational(11, 10)]
        ok = all(abs(sp.N((sp.diff(result, x) - f).subs(x, p))) < 1e-9 for p in pts)
        if not ok:
            raise SolverError("I could not verify this integral.", "unverified")
    return result, steps


def indefinite(f: sp.Expr, x: sp.Symbol) -> Solution:
    result, steps = _antiderivative(f, x)
    steps.append(Step("Add the constant of integration.", rf"{tex(result)}+C"))
    return Solution(
        operation="integral",
        question_latex=_int(f, x),
        answer_latex=rf"{tex(result)}+C",
        answer_text=f"{eng(result)} + C",
        steps=steps,
        notes=["The result was checked by differentiating it: the derivative of the answer is the integrand."],
    )


def definite(f: sp.Expr, x: sp.Symbol, a: sp.Expr, b: sp.Expr) -> Solution:
    result, steps = _antiderivative(f, x)
    fb, fa = sp.simplify(result.subs(x, b)), sp.simplify(result.subs(x, a))
    value = sp.simplify(fb - fa)
    steps.append(Step("Evaluate the antiderivative at the limits (Fundamental Theorem of Calculus).", rf"\left[{tex(result)}\right]_{{{tex(a)}}}^{{{tex(b)}}}=\left({tex(fb)}\right)-\left({tex(fa)}\right)"))
    steps.append(Step("Simplify.", rf"{tex(value)}"))
    notes = ["The antiderivative was checked by differentiating it."]
    # numeric cross-check of the value
    try:
        numeric = sp.Integral(f, (x, a, b)).evalf(15)
        if abs(complex(sp.N(value, 15)) - complex(numeric)) > 1e-8 * (1 + abs(complex(numeric))):
            raise SolverError("I could not verify this definite integral.", "unverified")
        notes.append("The value was also checked by numerical integration.")
    except SolverError:
        raise
    except Exception:  # noqa: BLE001 - improper integrals may not evaluate numerically
        pass
    return Solution(
        operation="definite_integral",
        question_latex=rf"\int_{{{tex(a)}}}^{{{tex(b)}}} {tex(f)}\,d{tex(x)}",
        answer_latex=tex(value),
        answer_text=eng(value),
        steps=steps,
        notes=notes,
    )
