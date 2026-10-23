"""Equations and systems with the method named at each step, solutions always checked by substituting them back; simplify, expand, factor."""

from __future__ import annotations

import sympy as sp

from .types import Solution, SolverError, Step, eng, tex


def _check_solutions(eq: sp.Expr, x: sp.Symbol, sols: list[sp.Expr]) -> None:
    for s in sols:
        residual = sp.simplify(eq.subs(x, s))
        if residual != 0 and abs(complex(sp.N(residual, 20))) > 1e-10:
            raise SolverError("I could not verify the solutions.", "unverified")


def solve_equation(lhs: sp.Expr, rhs: sp.Expr, x: sp.Symbol) -> Solution:
    eq = sp.expand(lhs - rhs)
    steps: list[Step] = []
    question = rf"{tex(lhs)}={tex(rhs)}"
    if rhs != 0:
        steps.append(Step("Move everything to one side.", rf"{tex(sp.expand(lhs - rhs))}=0"))
    try:
        poly = sp.Poly(eq, x)
    except sp.PolynomialError:
        poly = None
    if poly is not None and poly.degree() >= 1:
        deg = poly.degree()
        if deg == 1:
            a, b = poly.all_coeffs()
            steps.append(Step("A linear equation ax + b = 0: x = −b/a.", rf"a={tex(a)},\quad b={tex(b)}\ \Rightarrow\ {tex(x)}=-\dfrac{{{tex(b)}}}{{{tex(a)}}}"))
            sols = [sp.nsimplify(-b / a)]
        elif deg == 2:
            a, b, c = poly.all_coeffs()
            fac = sp.factor(eq)
            if fac.is_Mul and all(sp.degree(t, x) <= 1 for t in fac.args if t.has(x)) and len([t for t in fac.args if t.has(x)]) == 2:
                steps.append(Step("Factor the quadratic and set each factor to zero.", rf"{tex(fac)}=0"))
            disc = sp.simplify(b**2 - 4 * a * c)
            steps.append(Step("The discriminant tells how many real solutions there are: Δ = b² − 4ac.", rf"\Delta=\left({tex(b)}\right)^2-4\cdot\left({tex(a)}\right)\cdot\left({tex(c)}\right)={tex(disc)}"))
            sols = sp.solve(eq, x)
            if disc.is_negative:
                steps.append(Step("Δ is negative: there is no real solution (the solutions are complex).", ""))
                sols = [s for s in sols if sp.im(s) == 0]
            else:
                steps.append(Step("Quadratic formula.", rf"{tex(x)}=\dfrac{{-b\pm\sqrt{{\Delta}}}}{{2a}}=\dfrac{{{tex(-b)}\pm\sqrt{{{tex(disc)}}}}}{{{tex(2 * a)}}}"))
        else:
            fac = sp.factor(eq)
            steps.append(Step(f"A polynomial of degree {deg}: factor it and set each factor to zero.", rf"{tex(fac)}=0"))
            sols = [s for s in sp.solve(eq, x) if sp.im(s) == 0]
        sols = sorted({sp.simplify(s) for s in sols}, key=lambda s: float(sp.N(s)))
    else:
        raw = sp.solve(eq, x)
        sols = [sp.simplify(s) for s in raw if s.is_real is not False]
        try:
            sols = sorted(set(sols), key=lambda s: float(sp.N(s)))
        except (TypeError, ValueError):
            pass
        steps.append(Step("Solved with the algebra system (not a polynomial equation).", rf"{tex(x)}\in\left\{{{', '.join(tex(s) for s in sols)}\right\}}"))
    _check_solutions(eq, x, sols)
    steps.append(Step("The solutions:", ", ".join(rf"{tex(x)}={tex(s)}" for s in sols) if sols else r"\text{no real solution}"))
    steps.append(Step("Check: put each solution back in the original equation.", ", ".join(rf"{tex(lhs.subs(x, s))}={tex(rhs.subs(x, s))}" for s in sols[:4]) if sols else ""))
    return Solution(
        operation="solve",
        question_latex=question,
        answer_latex=", ".join(rf"{tex(x)}={tex(s)}" for s in sols) if sols else r"\text{no real solution}",
        answer_text=", ".join(f"{x}={eng(s)}" for s in sols) if sols else "no real solution",
        steps=steps,
        notes=["Every solution was checked by substituting it into the equation."],
    )


def solve_system(eqs: list[tuple[sp.Expr, sp.Expr]], syms: list[sp.Symbol]) -> Solution:
    if len(eqs) != len(syms) or not 2 <= len(syms) <= 3:
        raise SolverError("I can solve systems of 2 or 3 equations in as many unknowns.", "bad_system")
    exprs = [sp.expand(l - r) for l, r in eqs]
    steps = [Step("The system.", r"\begin{cases}" + r"\\".join(rf"{tex(l)}={tex(r)}" for l, r in eqs) + r"\end{cases}")]
    linear = all(sp.Poly(e, *syms).total_degree() <= 1 for e in exprs)
    if linear:
        a, b = sp.linear_eq_to_matrix(exprs, syms)
        steps.append(Step("All the equations are linear: write them as a matrix equation A·X = B.", rf"{tex(a)}\,{tex(sp.Matrix(syms))}={tex(b)}"))
        det = a.det()
        steps.append(Step("The determinant of A decides whether there is exactly one solution.", rf"\det A={tex(det)}"))
        if det == 0:
            sol = sp.solve(exprs, syms, dict=True)
            if not sol:
                steps.append(Step("The determinant is 0 and the equations contradict each other: no solution.", ""))
                return Solution("system", r"\text{system}", r"\text{no solution}", "no solution", steps, [])
            steps.append(Step("The determinant is 0: there are infinitely many solutions.", ""))
    sols = sp.solve(exprs, syms, dict=True)
    if not sols:
        raise SolverError("This system has no solution.", "no_solution")
    for s in sols:
        for e in exprs:
            if sp.simplify(e.subs(s)) != 0:
                raise SolverError("I could not verify the solution of the system.", "unverified")
    shown = sols[0]
    steps.append(Step("Eliminate the unknowns one at a time (substitution/elimination); the solution is:", ", ".join(rf"{tex(k)}={tex(v)}" for k, v in shown.items())))
    steps.append(Step("Check: put the solution in every equation.", ", ".join(rf"{tex(l.subs(shown))}={tex(r.subs(shown))}" for l, r in eqs)))
    return Solution(
        operation="system",
        question_latex=r"\begin{cases}" + r"\\".join(rf"{tex(l)}={tex(r)}" for l, r in eqs) + r"\end{cases}",
        answer_latex=", ".join(rf"{tex(k)}={tex(v)}" for k, v in shown.items()),
        answer_text=", ".join(f"{k}={eng(v)}" for k, v in shown.items()),
        steps=steps,
        notes=["The solution was checked in every equation."],
    )


def rewrite(f: sp.Expr, kind: str) -> Solution:
    """simplify, expand or factor, checked by comparing values at sample points."""
    result = {"simplify": sp.simplify, "expand": sp.expand, "factor": sp.factor}[kind](f)
    syms = sorted(f.free_symbols, key=lambda s: s.name)
    for k in range(3):
        sub = {s: sp.Rational(3 + k, 5 + 2 * k) + sp.Rational(i, 7) for i, s in enumerate(syms)}
        try:
            diff = complex(sp.N((f - result).subs(sub), 20))
        except (TypeError, ZeroDivisionError):
            continue
        if abs(diff) > 1e-9:
            raise SolverError("I could not verify that the two forms are equal.", "unverified")
    verb = {"simplify": "Simplify.", "expand": "Expand the products.", "factor": "Factor the expression."}[kind]
    return Solution(
        operation=kind,
        question_latex=tex(f),
        answer_latex=tex(result),
        answer_text=eng(result),
        steps=[Step(verb, rf"{tex(f)}={tex(result)}")],
        notes=["The two forms were compared at several values and agree."],
    )
