"""Ordinary differential equations: the type of the equation, the method with its key steps, the solution checked by substitution."""

from __future__ import annotations

import sympy as sp

from .types import Solution, SolverError, Step, eng, tex

_NAMES = {
    "separable": "separable equation",
    "1st_linear": "linear equation of the first order",
    "Bernoulli": "Bernoulli equation",
    "1st_exact": "exact equation",
    "1st_homogeneous_coeff_best": "homogeneous equation (of degree 0)",
    "1st_homogeneous_coeff_subs_dep_div_indep": "homogeneous equation (of degree 0)",
    "1st_homogeneous_coeff_subs_indep_div_dep": "homogeneous equation (of degree 0)",
    "nth_linear_constant_coeff_homogeneous": "linear equation with constant coefficients (homogeneous)",
    "nth_linear_constant_coeff_undetermined_coefficients": "linear equation with constant coefficients (undetermined coefficients)",
    "nth_linear_constant_coeff_variation_of_parameters": "linear equation with constant coefficients (variation of parameters)",
}


def solve_ode(lhs: sp.Expr, rhs: sp.Expr, x: sp.Symbol, y: sp.Symbol, y1: sp.Symbol, y2: sp.Symbol, conditions: list[tuple[sp.Expr, sp.Expr, int]]) -> Solution:
    f = sp.Function("y")
    sub = {y2: f(x).diff(x, 2), y1: f(x).diff(x), y: f(x)}
    eq = sp.Eq(lhs.subs(sub), rhs.subs(sub))
    order = 2 if eq.has(f(x).diff(x, 2)) else 1
    try:
        hints = [h for h in sp.classify_ode(eq, f(x)) if h in _NAMES]
    except Exception:  # noqa: BLE001
        hints = []
    if not hints:
        raise SolverError("I do not recognise the type of this differential equation yet.", "ode_type")
    steps = [Step("Write the equation and find its type.", rf"{tex(eq.lhs)}={tex(eq.rhs)}"), Step(f"Type: {_NAMES[hints[0]]} (order {order}).", "")]

    kind = hints[0]
    if kind.startswith("nth_linear_constant_coeff") and order == 2:
        r = sp.Symbol("r")
        a2 = sp.simplify(sp.expand(eq.lhs - eq.rhs).coeff(f(x).diff(x, 2)))
        a1 = sp.simplify(sp.expand(eq.lhs - eq.rhs).coeff(f(x).diff(x)))
        a0 = sp.simplify(sp.expand(eq.lhs - eq.rhs).coeff(f(x)))
        char = a2 * r**2 + a1 * r + a0
        roots = sp.roots(sp.Poly(char, r))
        steps.append(Step("The homogeneous part: try y = e^(rx); this gives the characteristic equation.", rf"{tex(char)}=0"))
        steps.append(Step("Its roots decide the form of the solution.", ", ".join(rf"r={tex(k)}" + (rf"\ (\text{{double}})" if m == 2 else "") for k, m in roots.items())))
    elif kind == "1st_linear":
        steps.append(Step("Write it as y' + P(x)y = Q(x), multiply by the integrating factor μ = e^(∫P dx), and integrate (μy)' = μQ.", ""))
    elif kind == "separable":
        steps.append(Step("Separate the variables: put all y on one side and all x on the other, then integrate both sides.", ""))
    elif kind == "Bernoulli":
        steps.append(Step("Divide by yⁿ and substitute v = y^(1−n): the equation becomes linear in v.", ""))
    elif kind == "1st_exact":
        steps.append(Step("Check that M_y = N_x, find a potential Φ with Φ_x = M and Φ_y = N, and write Φ = C.", ""))

    solution = sp.dsolve(eq, f(x), hint=kind) if kind in _NAMES else sp.dsolve(eq, f(x))
    sols = solution if isinstance(solution, list) else [solution]
    for s in sols:
        ok, residual = sp.checkodesol(eq, s, f(x))
        if not ok:
            raise SolverError("I could not verify this solution of the differential equation.", "unverified")
    general = sols[0]
    steps.append(Step("The general solution:", tex(general)))
    final = general
    if conditions:
        consts = sorted([c for c in general.rhs.free_symbols if c.name.startswith("C")], key=lambda c: c.name)
        eqs = []
        for at, value, deriv in conditions:
            expr = general.rhs if deriv == 0 else sp.diff(general.rhs, x, deriv)
            eqs.append(sp.Eq(expr.subs(x, at), value))
        sol_c = sp.solve(eqs, consts, dict=True)
        if not sol_c:
            raise SolverError("The initial conditions cannot be met by this equation.", "no_solution")
        final = sp.Eq(general.lhs, sp.simplify(general.rhs.subs(sol_c[0])))
        steps.append(Step("Use the conditions to find the constants.", ", ".join(rf"{tex(c)}={tex(v)}" for c, v in sol_c[0].items())))
        ok, _ = sp.checkodesol(eq, final, f(x))
        if not ok:
            raise SolverError("I could not verify the particular solution.", "unverified")
        steps.append(Step("The solution of the initial value problem:", tex(final)))
    return Solution(
        operation="ode",
        question_latex=rf"{tex(eq.lhs)}={tex(eq.rhs)}",
        answer_latex=tex(final),
        answer_text=f"y = {eng(final.rhs)}",
        steps=steps,
        notes=["The solution was checked by substituting it into the differential equation. C1 and C2 are arbitrary constants."],
    )
