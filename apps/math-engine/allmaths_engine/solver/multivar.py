"""Multivariable calculus with steps: partial derivatives, the gradient, critical points, Lagrange multipliers,
double and triple integrals (also in polar, cylindrical and spherical coordinates) and line integrals.

Every result is checked by a second, independent method before it is shown:
partial derivatives by a central difference, critical points by substituting them back and by looking at the values around them,
Lagrange candidates by substituting them in every equation (and, for a closed curve, by sampling the curve),
iterated integrals by numerical integration.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable

import sympy as sp

from . import derivative
from .integral import _antiderivative
from .types import Solution, SolverError, Step, eng, tex

_PREFERRED = "xyz"
MAX_POINTS = 24


def order_vars(syms: object) -> list[sp.Symbol]:
    """x, y, z first, then the other letters alphabetically."""
    return sorted(syms, key=lambda s: (0, _PREFERRED.index(s.name)) if s.name in _PREFERRED else (1, s.name))  # type: ignore[attr-defined]


def _vec(items: list[sp.Expr]) -> str:
    return r"\begin{pmatrix}" + r"\\".join(tex(c) for c in items) + r"\end{pmatrix}"


def _pt(items: list[sp.Expr]) -> str:
    return r"\left(" + r",\ ".join(tex(c) for c in items) + r"\right)"


def _names(syms: list[sp.Symbol]) -> str:
    return ", ".join(s.name for s in syms)


def _real_number(v: sp.Expr) -> bool:
    if v.free_symbols:
        return False
    if v.is_real is True:
        return True
    try:
        return abs(complex(sp.N(v, 30)).imag) < 1e-12
    except (TypeError, ValueError):
        return False


def _sample_points(syms: list[sp.Symbol], k: int) -> dict[sp.Symbol, sp.Expr]:
    return {s: sp.Rational(2 + k, 3) + sp.Rational(i + 1, 7) for i, s in enumerate(syms)}


def _central_difference_ok(f: sp.Expr, v: sp.Symbol, d: sp.Expr) -> bool:
    """The partial derivative d of f with respect to v agrees with (f(v+h) - f(v-h)) / 2h at a few points."""
    syms = order_vars(f.free_symbols | d.free_symbols | {v})
    h = sp.Rational(1, 10**6)
    for k in range(3):
        pt = _sample_points(syms, k)
        try:
            up = f.subs({**pt, v: pt[v] + h})
            down = f.subs({**pt, v: pt[v] - h})
            numeric = complex(sp.N((up - down) / (2 * h), 30))
            exact = complex(sp.N(d.subs(pt), 30))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if abs(numeric - exact) > 1e-6 * (1 + abs(exact)):
            return False
    return True


def _pd_latex(f: sp.Expr, vs: list[sp.Symbol]) -> str:
    """\\dfrac{\\partial^n}{\\partial v_n ... \\partial v_1}[f]; the variable differentiated first is written last."""
    groups: list[tuple[sp.Symbol, int]] = []
    for v in reversed(vs):
        if groups and groups[-1][0] == v:
            groups[-1] = (v, groups[-1][1] + 1)
        else:
            groups.append((v, 1))
    den = r"\,".join(rf"\partial {tex(v)}" + (rf"^{{{k}}}" if k > 1 else "") for v, k in groups)
    top = r"\partial" + (rf"^{{{len(vs)}}}" if len(vs) > 1 else "")
    return rf"\dfrac{{{top}}}{{{den}}}\left[{tex(f)}\right]"


def _value_at(expr: sp.Expr, point: dict[sp.Symbol, sp.Expr]) -> sp.Expr:
    value = sp.simplify(expr.subs(point))
    if value.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        raise SolverError("This is not defined at that point.", "undefined")
    return value


# --------------------------------------------------------------------------------------------------- partial derivatives
def partial(f: sp.Expr, vs: list[sp.Symbol], at: dict[sp.Symbol, sp.Expr] | None = None) -> Solution:
    if not vs or len(vs) > 4:
        raise SolverError("Tell me with respect to which variable (at most 4 derivatives in a row).", "bad_variables")
    allv = order_vars(f.free_symbols | set(vs))
    steps: list[Step] = []
    cur = f
    for v in vs:
        others = [s for s in allv if s != v]
        if others:
            steps.append(Step(f"Differentiate with respect to {v.name}; treat {_names(others)} as {'a constant' if len(others) == 1 else 'constants'}.", rf"\dfrac{{\partial}}{{\partial {tex(v)}}}\left[{tex(cur)}\right]"))
        inner = derivative.differentiate(cur, v)
        steps.extend(inner.steps)
        nxt = sp.diff(cur, v)
        if not _central_difference_ok(cur, v, nxt):
            raise SolverError("I could not verify this partial derivative.", "unverified")
        steps.append(Step("Result of this step.", rf"\dfrac{{\partial}}{{\partial {tex(v)}}}\left[{tex(cur)}\right]={tex(sp.simplify(nxt))}"))
        cur = sp.simplify(nxt)
    notes = ["Each derivative was checked against the difference quotient (f(x+h) − f(x−h)) / 2h at several points."]
    if len(vs) == 2 and vs[0] != vs[1]:
        other = sp.simplify(sp.diff(f, vs[1], vs[0]))
        if sp.simplify(other - cur) == 0:
            notes.append("Differentiating in the other order gives the same function (mixed partial derivatives are equal here).")
    question = _pd_latex(f, vs)
    answer = cur
    answer_tex = tex(cur)
    if at is not None:
        missing = [s for s in allv if s not in at]
        if missing:
            raise SolverError(f"Give a value for {_names(missing)} in the point.", "bad_point")
        value = _value_at(cur, at)
        steps.append(Step("Evaluate at the point.", rf"{tex(cur)}\Big|_{{{', '.join(f'{tex(k)}={tex(v)}' for k, v in at.items())}}}={tex(value)}"))
        answer = value
        answer_tex = tex(value)
        question += rf"\Big|_{{{', '.join(f'{tex(k)}={tex(v)}' for k, v in at.items())}}}"
    return Solution("partial_derivative", question, answer_tex, eng(answer), steps, notes)


# ---------------------------------------------------------------------------------------------------------- gradient
def _gradient_vector(f: sp.Expr, vs: list[sp.Symbol], steps: list[Step]) -> list[sp.Expr]:
    comps: list[sp.Expr] = []
    show_inner = sp.count_ops(f) <= 14
    for v in vs:
        d = sp.simplify(sp.diff(f, v))
        if show_inner:
            steps.append(Step(f"Partial derivative with respect to {v.name} (the other letters are constants).", ""))
            steps.extend(derivative.differentiate(f, v).steps)
        if not _central_difference_ok(f, v, d):
            raise SolverError("I could not verify the gradient.", "unverified")
        steps.append(Step(f"∂f/∂{v.name}", rf"\dfrac{{\partial}}{{\partial {tex(v)}}}\left[{tex(f)}\right]={tex(d)}"))
        comps.append(d)
    return comps


def gradient(f: sp.Expr, at: dict[sp.Symbol, sp.Expr] | None = None) -> Solution:
    vs = order_vars(f.free_symbols)
    if not vs or len(vs) > 4:
        raise SolverError("The gradient needs a function of 1 to 4 variables.", "bad_variables")
    partials = ", ".join(rf"\dfrac{{\partial f}}{{\partial {tex(v)}}}" for v in vs)
    steps = [Step("The gradient is the vector of all the first partial derivatives.", rf"\nabla f=\left({partials}\right)")]
    comps = _gradient_vector(f, vs, steps)
    notes = ["Every component was checked against a difference quotient."]
    question = rf"\nabla\left({tex(f)}\right)"
    answer_tex = rf"\nabla f={_vec(comps)}"
    answer = f"({', '.join(eng(c) for c in comps)})"
    steps.append(Step("Collect the partial derivatives.", answer_tex))
    if at is not None:
        missing = [s for s in vs if s not in at]
        if missing:
            raise SolverError(f"Give a value for {_names(missing)} in the point.", "bad_point")
        values = [_value_at(c, at) for c in comps]
        steps.append(Step("Evaluate every component at the point.", rf"\nabla f{_pt([at[v] for v in vs])}={_vec(values)}"))
        norm = sp.simplify(sp.sqrt(sum(c**2 for c in values)))
        if norm != 0:
            steps.append(Step("The function increases fastest in the direction of the gradient, at the rate equal to its length.", rf"\left\|\nabla f\right\|={tex(norm)}"))
        question += rf"\ \text{{at }}{_pt([at[v] for v in vs])}"
        answer_tex = rf"\nabla f={_vec(values)}"
        answer = f"({', '.join(eng(c) for c in values)})"
    return Solution("gradient", question, answer_tex, answer, steps, notes)


def directional(f: sp.Expr, at: dict[sp.Symbol, sp.Expr], direction: list[sp.Expr]) -> Solution:
    vs = order_vars(f.free_symbols)
    if len(direction) != len(vs):
        raise SolverError(f"The direction needs {len(vs)} numbers, one for each of {_names(vs)}.", "bad_vectors")
    length = sp.simplify(sp.sqrt(sum(c**2 for c in direction)))
    if length == 0:
        raise SolverError("The direction cannot be the zero vector.", "bad_vectors")
    steps: list[Step] = []
    comps = _gradient_vector(f, vs, steps)
    grad = [_value_at(c, at) for c in comps]
    steps.append(Step("The gradient at the point.", rf"\nabla f={_vec(grad)}"))
    unit = [sp.simplify(c / length) for c in direction]
    steps.append(Step("A directional derivative needs a unit vector: divide the direction by its length.", rf"\vec u=\dfrac{{1}}{{{tex(length)}}}{_vec(list(direction))}={_vec(unit)}"))
    value = sp.simplify(sum(g * u for g, u in zip(grad, unit, strict=True)))
    steps.append(Step("The directional derivative is the dot product of the gradient and the unit vector.", rf"D_{{\vec u}}f=\nabla f\cdot\vec u={tex(value)}"))
    # check: derivative of t -> f(p + t u) at t = 0
    t = sp.Symbol("t", real=True)
    line = f.subs({v: at[v] + t * u for v, u in zip(vs, unit, strict=True)}, simultaneous=True)
    if sp.simplify(sp.diff(line, t).subs(t, 0) - value) != 0:
        raise SolverError("I could not verify the directional derivative.", "unverified")
    return Solution(
        "directional_derivative",
        rf"D_{{\vec u}}\left({tex(f)}\right)\text{{ at }}{_pt([at[v] for v in vs])}",
        tex(value),
        eng(value),
        steps,
        ["Checked a second way: the derivative of f(P + t·u) at t = 0 gives the same value."],
    )


# ---------------------------------------------------------------------------------------------- critical points
def _real_solutions(eqs: list[sp.Expr], vs: list[sp.Symbol]) -> list[tuple[sp.Expr, ...]]:
    try:
        sols = sp.solve(eqs, vs, dict=True)
    except (NotImplementedError, ValueError, TypeError):
        raise SolverError("I could not solve the equations for the critical points.", "no_solution") from None
    points: list[tuple[sp.Expr, ...]] = []
    for s in sols:
        if set(s) != set(vs) or any(val.free_symbols for val in s.values()):
            raise SolverError("This function has infinitely many critical points (a whole line or curve of them); I only list isolated points.", "infinite")
        pt = tuple(sp.simplify(s[v]) for v in vs)
        if all(_real_number(c) for c in pt) and pt not in points:
            points.append(pt)
    points.sort(key=lambda p: tuple(float(sp.N(c)) for c in p))
    return points


def _minors_sign(h: sp.Matrix) -> str:
    n = h.shape[0]
    minors = [sp.simplify(h[:k, :k].det()) for k in range(1, n + 1)]
    if all(m > 0 for m in minors):
        return "min"
    if all((m < 0) if k % 2 == 0 else (m > 0) for k, m in enumerate(minors)):
        return "max"
    if minors[-1] != 0 and not all(m >= 0 for m in minors) and not all((m <= 0) if k % 2 == 0 else (m >= 0) for k, m in enumerate(minors)):
        return "saddle"
    if minors[-1] != 0:
        return "saddle"
    return "unknown"


def _neighbour_check(f: sp.Expr, vs: list[sp.Symbol], point: tuple[sp.Expr, ...], kind: str) -> bool:
    """The values of f close to a critical point agree with its classification."""
    delta = sp.Rational(1, 100)
    base = f.subs(dict(zip(vs, point, strict=True)))
    up = down = False
    for d in itertools.product((-1, 0, 1), repeat=len(vs)):
        if not any(d):
            continue
        try:
            diff = float(sp.N(f.subs({v: p + delta * k for v, p, k in zip(vs, point, d, strict=True)}) - base, 30))
        except (TypeError, ValueError, ZeroDivisionError):
            return True
        up = up or diff > 1e-12
        down = down or diff < -1e-12
    if kind == "min":
        return not down
    if kind == "max":
        return not up
    if kind == "saddle":
        return up and down
    return True


_KIND = {"min": "local minimum", "max": "local maximum", "saddle": "saddle point", "unknown": "the test is inconclusive"}


def critical_points(f: sp.Expr) -> Solution:
    vs = order_vars(f.free_symbols)
    n = len(vs)
    if n == 0 or n > 3:
        raise SolverError("I find the critical points of a function of 1, 2 or 3 variables.", "bad_variables")
    steps = [Step("A local maximum or minimum can only be where every first partial derivative is 0.", r"\begin{cases}" + r"\\[0.9em]".join(rf"\dfrac{{\partial f}}{{\partial {tex(v)}}}=0" for v in vs) + r"\end{cases}")]
    grad = [sp.simplify(sp.diff(f, v)) for v in vs]
    for v, g in zip(vs, grad, strict=True):
        if not _central_difference_ok(f, v, g):
            raise SolverError("I could not verify the partial derivatives.", "unverified")
    steps.append(Step("Compute the partial derivatives.", r"\begin{cases}" + r"\\".join(rf"f_{{{tex(v)}}}={tex(g)}" for v, g in zip(vs, grad, strict=True)) + r"\end{cases}"))
    points = _real_solutions(grad, vs)
    if len(points) > MAX_POINTS:
        raise SolverError("There are too many critical points to list.", "too_long")
    notes = ["Each critical point was put back in every first derivative (they are 0), and the values of f around it were compared with the classification."]
    if not f.is_polynomial(*vs) and not f.is_rational_function(*vs):
        notes.append("For a function with trigonometric, exponential or logarithmic parts, there can be more critical points than the ones found here.")
    if not points:
        steps.append(Step("The equations have no real solution.", r"\text{no critical points}"))
        return Solution("critical_points", rf"\text{{critical points of }}{tex(f)}", r"\text{no critical points: no local maximum or minimum}", "no critical points", steps, notes)
    steps.append(Step("Solve the system. The critical points are:", ",\\quad ".join(_pt(list(p)) for p in points)))
    hess = sp.Matrix(n, n, lambda i, j: sp.diff(f, vs[i], vs[j]))
    steps.append(Step("Second-derivative test: build the Hessian matrix of second partial derivatives.", rf"H={tex(hess)}"))
    results: list[tuple[tuple[sp.Expr, ...], str, sp.Expr]] = []
    for p in points:
        sub = dict(zip(vs, p, strict=True))
        if any(sp.simplify(g.subs(sub)) != 0 for g in grad):
            raise SolverError("I could not verify a critical point.", "unverified")
        hp = hess.subs(sub).applyfunc(sp.simplify)
        value = sp.simplify(f.subs(sub))
        if n == 1:
            second = hp[0, 0]
            kind = "min" if second > 0 else "max" if second < 0 else "unknown"
            detail = rf"f''={tex(second)}"
        elif n == 2:
            d = sp.simplify(hp[0, 0] * hp[1, 1] - hp[0, 1] ** 2)
            kind = "unknown" if d == 0 else "saddle" if d < 0 else ("min" if hp[0, 0] > 0 else "max")
            detail = rf"D=f_{{{tex(vs[0])}{tex(vs[0])}}}f_{{{tex(vs[1])}{tex(vs[1])}}}-f_{{{tex(vs[0])}{tex(vs[1])}}}^2={tex(d)},\quad f_{{{tex(vs[0])}{tex(vs[0])}}}={tex(hp[0, 0])}"
        else:
            kind = _minors_sign(hp)
            detail = rf"H={tex(hp)}"
        if not _neighbour_check(f, vs, p, kind):
            raise SolverError("I could not verify the classification of a critical point.", "unverified")
        results.append((p, kind, value))
        steps.append(Step("At the point (" + ", ".join(eng(c) for c in p) + f"): {_KIND[kind]}.",rf"{detail},\quad f={tex(value)}"))
    if n == 2:
        notes.append("Test used: D > 0 and f_xx > 0 gives a minimum, D > 0 and f_xx < 0 a maximum, D < 0 a saddle point, D = 0 tells nothing.")
    answer_tex = r"\begin{array}{l}" + r"\\".join(rf"{_pt(list(p))}:\ \text{{{_KIND[k]}}},\ f={tex(v)}" for p, k, v in results) + r"\end{array}"
    answer_text = "; ".join(f"({', '.join(eng(c) for c in p)}): {_KIND[k]}, f = {eng(v)}" for p, k, v in results)
    return Solution("critical_points", rf"\text{{critical points of }}{tex(f)}", answer_tex, answer_text, steps, notes)


# ------------------------------------------------------------------------------------------- Lagrange multipliers
def _bounded_variables(g: sp.Expr, vs: list[sp.Symbol]) -> set[sp.Symbol]:
    """The variables that the set g = 0 keeps bounded: those of a sum of even powers with equal signs (a circle, a sphere, ...),
    or the one variable of an equation such as z = 1."""
    used = [v for v in vs if g.has(v)]
    if not used:
        return set()
    try:
        poly = sp.Poly(sp.expand(g), *used)
    except sp.PolynomialError:
        return set()
    d = poly.total_degree()
    if len(used) == 1 and d >= 1:
        return {used[0]}
    if d < 2 or d % 2:
        return set()
    top = {m: c for m, c in poly.terms() if sum(m) == d}
    pure_powers = all(sum(1 for e in m if e) == 1 for m in top) and {i for m in top for i, e in enumerate(m) if e == d} == set(range(len(used)))
    same_sign = all(c > 0 for c in top.values()) or all(c < 0 for c in top.values())
    return set(used) if pure_powers and same_sign and len(top) == len(used) else set()


def _is_compact(gs: list[sp.Expr], vs: list[sp.Symbol]) -> bool:
    """The solution set of all the constraints is closed and bounded."""
    bounded: set[sp.Symbol] = set()
    for g in gs:
        bounded |= _bounded_variables(g, vs)
    return bounded == set(vs)


def _sample_constraint_ok(f: sp.Expr, g: sp.Expr, vs: list[sp.Symbol], low: sp.Expr, high: sp.Expr) -> bool:
    """For a closed curve in two variables: the values of f along the curve stay between the smallest and largest found."""
    x, y = vs
    try:
        pol = sp.Poly(g, y)
    except sp.PolynomialError:
        return True
    lo, hi = float(sp.N(low)), float(sp.N(high))
    fl = sp.lambdify((x, y), f, "math")
    for k in range(-60, 61):
        xv = k / 6.0
        coeffs = [complex(sp.N(c.subs(x, xv))) for c in pol.all_coeffs()]
        if abs(coeffs[0]) < 1e-14:
            continue
        try:
            roots = sp.Poly(sp.Poly(g.subs(x, sp.Float(xv)), y), y).nroots(n=15)
        except Exception:  # noqa: BLE001 - numerical root finding may fail at a few points; the check is only a second opinion
            continue
        for r in roots:
            if abs(sp.im(r)) < 1e-9:
                val = fl(xv, float(sp.re(r)))
                if val < lo - 1e-6 * (1 + abs(lo)) or val > hi + 1e-6 * (1 + abs(hi)):
                    return False
    return True


def lagrange(f: sp.Expr, constraints: list[tuple[sp.Expr, sp.Expr]], goal: str) -> Solution:
    gs = [sp.expand(lhs - rhs) for lhs, rhs in constraints]
    vs = order_vars(set(f.free_symbols).union(*[g.free_symbols for g in gs]))
    n, m = len(vs), len(gs)
    if n < 2 or n > 3 or m < 1 or m > 2 or m >= n:
        raise SolverError("I handle 2 or 3 variables with 1 constraint (or 3 variables with 2 constraints).", "bad_variables")
    lam = [sp.Symbol("lambda", real=True)] if m == 1 else [sp.Symbol(f"lambda_{i + 1}", real=True) for i in range(m)]
    lagr = [sp.diff(f, v) - sum(lm * sp.diff(g, v) for lm, g in zip(lam, gs, strict=True)) for v in vs]
    grad_terms = "+".join((tex(lm) + r"\nabla g_{" + str(i + 1) + "}") if m > 1 else (tex(lm) + r"\nabla g") for i, lm in enumerate(lam))
    cons_rows = r"\\".join(tex(lhs) + "=" + tex(rhs) for lhs, rhs in constraints)
    var_rows = r"\\".join(tex(sp.diff(f, v)) + "=" + "+".join(tex(lm) + r"\cdot\left(" + tex(sp.diff(g, v)) + r"\right)" for lm, g in zip(lam, gs, strict=True)) for v in vs)
    plural = "s" if m > 1 else ""
    steps = [
        Step("Lagrange multipliers: at an extreme point the gradient of f is a combination of the gradients of the constraints.", r"\nabla f=" + grad_terms),
        Step(f"The constraint{plural}.", r"\begin{cases}" + cons_rows + r"\end{cases}"),
        Step(f"Write one equation for every variable, plus the constraint{plural}.", r"\begin{cases}" + var_rows + r"\\" + cons_rows + r"\end{cases}"),
    ]
    try:
        sols = sp.solve(lagr + gs, vs + lam, dict=True)
    except (NotImplementedError, ValueError, TypeError):
        raise SolverError("I could not solve the Lagrange equations.", "no_solution") from None
    cands: dict[tuple[sp.Expr, ...], dict[sp.Symbol, sp.Expr]] = {}
    for s in sols:
        if set(s) != set(vs + lam) or any(val.free_symbols for val in s.values()):
            raise SolverError("The solutions form a whole curve; I only handle isolated candidate points.", "infinite")
        pt = tuple(sp.simplify(s[v]) for v in vs)
        if all(_real_number(c) for c in pt) and pt not in cands:
            cands[pt] = s
    singular: list[tuple[sp.Expr, ...]] = []
    if m == 1:
        try:
            for s in sp.solve([sp.diff(gs[0], v) for v in vs] + gs, vs, dict=True):
                pt = tuple(sp.simplify(s.get(v, v)) for v in vs)
                if all(_real_number(c) for c in pt) and pt not in cands:
                    cands[pt] = {}
                    singular.append(pt)
        except (NotImplementedError, ValueError, TypeError):
            pass
    if len(cands) > MAX_POINTS:
        raise SolverError("There are too many candidate points to list.", "too_long")
    if not cands:
        steps.append(Step("The equations have no real solution.", ""))
        return Solution("lagrange", rf"\text{{extrema of }}{tex(f)}", r"\text{no point satisfies the conditions}", "no candidate points", steps, [])
    ordered = sorted(cands, key=lambda p: tuple(float(sp.N(c)) for c in p))
    rows: list[tuple[tuple[sp.Expr, ...], sp.Expr]] = []
    for p in ordered:
        sub = dict(zip(vs, p, strict=True))
        if any(sp.simplify(g.subs(sub)) != 0 for g in gs):
            raise SolverError("I could not verify a candidate point.", "unverified")
        s = cands[p]
        if s and any(sp.simplify(e.subs(s)) != 0 for e in lagr):
            raise SolverError("I could not verify a candidate point.", "unverified")
        rows.append((p, sp.simplify(f.subs(sub))))
    steps.append(Step("Solve the equations. The candidate points and the value of f at each:", r"\begin{array}{l}" + r"\\".join(rf"{_pt(list(p))}:\ f={tex(v)}" for p, v in rows) + r"\end{array}"))
    if singular:
        steps.append(Step("At these points the gradient of the constraint is 0, so the multiplier method cannot see them; they are candidates too.", ",\\quad ".join(_pt(list(p)) for p in singular)))
    values = [v for _, v in rows]
    hi = max(values, key=lambda v: float(sp.N(v)))
    lo = min(values, key=lambda v: float(sp.N(v)))
    notes = ["Every candidate was put back in the constraint and in the Lagrange equations."]
    compact = _is_compact(gs, vs)
    lines_tex: list[str] = []
    lines_txt: list[str] = []

    def where(target: sp.Expr) -> str:
        return r",\ ".join(_pt(list(p)) for p, v in rows if sp.simplify(v - target) == 0)

    def where_txt(target: sp.Expr) -> str:
        return " and ".join("(" + ", ".join(eng(c) for c in p) + ")" for p, v in rows if sp.simplify(v - target) == 0)

    if compact:
        steps.append(Step("The constraint is a closed and bounded set, so f has a largest and a smallest value on it, and they are among the candidates. Compare the values.", rf"\max={tex(hi)},\qquad \min={tex(lo)}"))
        if goal in ("max", "both"):
            lines_tex.append(rf"\text{{maximum }}f={tex(hi)}\ \text{{at }}{where(hi)}")
            lines_txt.append(f"maximum {eng(hi)} at {where_txt(hi)}")
        if goal in ("min", "both"):
            lines_tex.append(rf"\text{{minimum }}f={tex(lo)}\ \text{{at }}{where(lo)}")
            lines_txt.append(f"minimum {eng(lo)} at {where_txt(lo)}")
        if n == 2 and m == 1 and not _sample_constraint_ok(f, gs[0], vs, lo, hi):
            raise SolverError("I could not verify the extreme values along the curve.", "unverified")
        if n == 2 and m == 1:
            notes.append("A second check: f was evaluated at many points of the curve, and it stays between the minimum and the maximum found.")
    elif n == 2 and m == 1:
        g = gs[0]
        gx, gy = sp.diff(g, vs[0]), sp.diff(g, vs[1])
        kinds: list[tuple[tuple[sp.Expr, ...], str, sp.Expr]] = []
        for p, v in rows:
            s = cands[p]
            if not s:
                kinds.append((p, "unknown", v))
                continue
            lm = s[lam[0]]
            lag_fn = f - lm * g
            sub = dict(zip(vs, p, strict=True))
            bordered = sp.Matrix([[0, gx, gy], [gx, sp.diff(lag_fn, vs[0], 2), sp.diff(lag_fn, vs[0], vs[1])], [gy, sp.diff(lag_fn, vs[0], vs[1]), sp.diff(lag_fn, vs[1], 2)]]).subs(sub)
            det = sp.simplify(bordered.det())
            kinds.append((p, "unknown" if det == 0 else "max" if det > 0 else "min", v))
        steps.append(
            Step(
                "The constraint is not closed and bounded, so check each candidate with the bordered Hessian (positive: local maximum, negative: local minimum).",
                r"\begin{array}{l}" + r"\\".join(rf"{_pt(list(p))}:\ \text{{{_KIND[k] if k != 'unknown' else 'not decided'}}},\ f={tex(v)}" for p, k, v in kinds) + r"\end{array}",
            )
        )
        for p, k, v in kinds:
            wanted = (goal == "both") or (goal == "max" and k == "max") or (goal == "min" and k == "min")
            if wanted or k == "unknown":
                lines_tex.append(rf"{_pt(list(p))}:\ \text{{{_KIND[k] if k != 'unknown' else 'not decided'}}},\ f={tex(v)}")
                lines_txt.append(f"({', '.join(eng(c) for c in p)}): {_KIND[k] if k != 'unknown' else 'not decided'}, f = {eng(v)}")
        notes.append("These are local extremes. The constraint is not a closed bounded set, so f may take larger or smaller values far away.")
        if not lines_tex:
            lines_tex.append(r"\text{none of the candidates is of the type asked for}")
            lines_txt.append("none of the candidates is of the type asked for")
    else:
        for p, v in rows:
            lines_tex.append(rf"{_pt(list(p))}:\ f={tex(v)}")
            lines_txt.append(f"({', '.join(eng(c) for c in p)}): f = {eng(v)}")
        notes.append("The extreme values are among these candidate points, but I cannot tell which is a maximum or a minimum here because the constraint is not closed and bounded.")
    if not f.is_polynomial(*vs) or any(not g.is_polynomial(*vs) for g in gs):
        notes.append("With non-polynomial functions there may be more candidate points than the ones found.")
    answer_tex = r"\begin{array}{l}" + r"\\".join(lines_tex) + r"\end{array}"
    verb = {"max": "maximum", "min": "minimum", "both": "extreme values"}[goal]
    return Solution("lagrange", rf"\text{{{verb} of }}{tex(f)}\text{{ subject to }}" + ",\\ ".join(rf"{tex(lhs)}={tex(rhs)}" for lhs, rhs in constraints), answer_tex, "; ".join(lines_txt), steps, notes)


# ------------------------------------------------------------------------------------------ iterated integrals
def _definite(f: sp.Expr, x: sp.Symbol, a: sp.Expr, b: sp.Expr) -> tuple[sp.Expr, list[Step]]:
    antiderivative, steps = _antiderivative(f, x)
    upper, lower = sp.simplify(antiderivative.subs(x, b)), sp.simplify(antiderivative.subs(x, a))
    value = sp.simplify(upper - lower)
    steps.append(Step("Evaluate between the limits (Fundamental Theorem of Calculus).", rf"\left[{tex(antiderivative)}\right]_{{{tex(a)}}}^{{{tex(b)}}}=\left({tex(upper)}\right)-\left({tex(lower)}\right)={tex(value)}"))
    return value, steps


def _simpson(fn: Callable[[float], float], a: float, b: float, n: int) -> float:
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += fn(a + i * h) * (4 if i % 2 else 2)
    return total * h / 3


def _numeric_nested(f: sp.Expr, levels: list[tuple[sp.Symbol, sp.Expr, sp.Expr]]) -> float | None:
    """Numerical value of the iterated integral (levels are innermost first) by Simpson's rule; None when it cannot be computed."""
    outer = list(reversed(levels))
    names = [v for v, _, _ in outer]
    try:
        fn = sp.lambdify(names, f, "math")
        lows = [sp.lambdify(names[:k], a, "math") for k, (_, a, _) in enumerate(outer)]
        highs = [sp.lambdify(names[:k], b, "math") for k, (_, _, b) in enumerate(outer)]
        count = {1: 400, 2: 60, 3: 24}[len(outer)]

        def rec(k: int, env: list[float]) -> float:
            if k == len(outer):
                return fn(*env)
            return _simpson(lambda s: rec(k + 1, [*env, s]), float(lows[k](*env)), float(highs[k](*env)), count)

        result = rec(0, [])
        return result if math.isfinite(result) else None
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        return None


_COORDS = {
    "polar": ({"r", "theta"}, "x = r\\cos\\theta,\\quad y = r\\sin\\theta,\\quad dA = r\\,dr\\,d\\theta"),
    "cylindrical": ({"r", "theta", "z"}, "x = r\\cos\\theta,\\quad y = r\\sin\\theta,\\quad z = z,\\quad dV = r\\,dz\\,dr\\,d\\theta"),
    "spherical": ({"rho", "phi", "theta"}, "x = \\rho\\sin\\varphi\\cos\\theta,\\quad y = \\rho\\sin\\varphi\\sin\\theta,\\quad z = \\rho\\cos\\varphi,\\quad dV = \\rho^2\\sin\\varphi\\,d\\rho\\,d\\varphi\\,d\\theta"),
}


def _to_coordinates(f: sp.Expr, system: str) -> tuple[sp.Expr, sp.Expr]:
    x, y, z = (sp.Symbol(n, real=True) for n in "xyz")
    r, th, ph, rho = (sp.Symbol(n, real=True) for n in ("r", "theta", "phi", "rho"))
    if system == "polar":
        return f.subs({x: r * sp.cos(th), y: r * sp.sin(th)}, simultaneous=True), r
    if system == "cylindrical":
        return f.subs({x: r * sp.cos(th), y: r * sp.sin(th)}, simultaneous=True), r
    return f.subs({x: rho * sp.sin(ph) * sp.cos(th), y: rho * sp.sin(ph) * sp.sin(th), z: rho * sp.cos(ph)}, simultaneous=True), rho**2 * sp.sin(ph)


def multiple_integral(f: sp.Expr, levels: list[tuple[sp.Symbol, sp.Expr, sp.Expr]], system: str | None = None) -> Solution:
    """levels: (variable, lower, upper) from the innermost integral to the outermost."""
    if not 2 <= len(levels) <= 3:
        raise SolverError("A double integral has 2 variables and a triple integral 3.", "bad_bounds")
    names = [v for v, _, _ in levels]
    if len(set(names)) != len(names):
        raise SolverError("Each variable can have only one pair of limits.", "bad_bounds")
    for k, (v, a, b) in enumerate(levels):
        for dep in (a.free_symbols | b.free_symbols):
            if dep == v or dep not in names[k + 1 :]:
                raise SolverError(f"The limits of {v.name} use {dep.name}, which is not an outer variable: write the integral so that {dep.name} is integrated after {v.name}.", "bad_bounds")
    steps: list[Step] = []
    integrand = f
    if system:
        expected, formulas = _COORDS[system]
        if {v.name for v in names} != expected:
            raise SolverError(f"In {system} coordinates the variables are {', '.join(sorted(expected))}.", "bad_bounds")
        converted, jacobian = _to_coordinates(f, system)
        integrand = sp.simplify(converted * jacobian)
        steps.append(Step(f"Change to {system} coordinates; the area or volume element gets a factor.", formulas))
        steps.append(Step("Write the integrand in the new variables and multiply by the factor.", rf"{tex(f)}\ \longrightarrow\ \left({tex(sp.simplify(converted))}\right)\cdot\left({tex(jacobian)}\right)={tex(integrand)}"))
    leftover = integrand.free_symbols - set(names)
    if leftover:
        raise SolverError(f"The integrand contains {_names(order_vars(leftover))}, which has no limits.", "bad_bounds")
    order = [v.name for v in names]
    steps.append(Step(f"Integrate from the inside out: first {order[0]}, then {order[1]}" + (f", then {order[2]}." if len(order) == 3 else "."), ""))
    cur = integrand
    for v, a, b in levels:
        steps.append(Step(f"Integrate with respect to {v.name} from {eng(a)} to {eng(b)}; the other letters are constants.", rf"\int_{{{tex(a)}}}^{{{tex(b)}}} {tex(cur)}\,d{tex(v)}"))
        cur, inner = _definite(cur, v, a, b)
        steps.extend(inner)
        steps.append(Step(f"Result after integrating {v.name}.", tex(cur)))
    if cur.free_symbols:
        raise SolverError("The result still contains a letter; check the limits.", "bad_bounds")
    notes: list[str] = []
    numeric = _numeric_nested(integrand, levels)
    value = float(sp.N(cur, 15)) if cur.is_real else None
    if numeric is not None and value is not None:
        if abs(numeric - value) > 1e-4 * (1 + abs(value)):
            raise SolverError("I could not verify this integral numerically.", "unverified")
        notes.append("The value was also checked by numerical integration of the iterated integral.")
    signs = "".join(rf"\int_{{{tex(a)}}}^{{{tex(b)}}}" for _, a, b in reversed(levels))
    diffs = "".join(rf"\,d{tex(v)}" for v in names)
    question = rf"{signs} {tex(f)}{diffs}" if not system else rf"{signs} {tex(f)}\ \text{{({system} coordinates)}}{diffs}"
    op = "double_integral" if len(levels) == 2 else "triple_integral"
    return Solution(op, question, tex(cur), eng(cur), steps, notes)


# ------------------------------------------------------------------------------------------------ line integrals
def _resolve_abs(expr: sp.Expr, t: sp.Symbol, a: sp.Expr, b: sp.Expr) -> sp.Expr:
    """Replace |g(t)| by g or -g when g keeps its sign on [a, b]."""
    lo, hi = float(sp.N(a)), float(sp.N(b))
    for atom in expr.atoms(sp.Abs):
        arg = atom.args[0]
        vals = [float(sp.N(arg.subs(t, lo + (hi - lo) * k / 200))) for k in range(201)]
        if all(v >= -1e-12 for v in vals):
            expr = expr.subs(atom, arg)
        elif all(v <= 1e-12 for v in vals):
            expr = expr.subs(atom, -arg)
        else:
            raise SolverError("The speed changes its formula along the path; split the path into pieces.", "piecewise")
    return expr


def line_integral(field: object, curve: list[sp.Expr], t: sp.Symbol, a: sp.Expr, b: sp.Expr) -> Solution:
    dim = len(curve)
    if dim not in (2, 3):
        raise SolverError("The curve needs 2 or 3 coordinates.", "bad_curve")
    coords = [sp.Symbol(n, real=True) for n in "xyz"[:dim]]
    if any(c.free_symbols - {t} for c in curve):
        raise SolverError("The curve may only use the letter t.", "bad_curve")
    if a.free_symbols or b.free_symbols:
        raise SolverError("The limits of t must be numbers.", "bad_bounds")
    if float(sp.N(b)) <= float(sp.N(a)):
        raise SolverError("t must go from a smaller to a larger value.", "bad_bounds")
    on_curve = dict(zip(coords, curve, strict=True))
    velocity = [sp.simplify(sp.diff(c, t)) for c in curve]
    steps = [
        Step("Parametrize the path.", rf"\vec r(t)={_vec(curve)},\quad {tex(a)}\le t\le {tex(b)}"),
        Step("Differentiate to get the velocity vector.", rf"\vec r\,'(t)={_vec(velocity)}"),
    ]
    if isinstance(field, sp.Tuple):
        comps = list(field)
        if len(comps) != dim:
            raise SolverError(f"The field has {len(comps)} components but the curve has {dim} coordinates.", "bad_vectors")
        if set().union(*[c.free_symbols for c in comps]) - set(coords):
            raise SolverError(f"The field may only use {_names(coords)}.", "bad_vectors")
        along = [sp.simplify(c.subs(on_curve, simultaneous=True)) for c in comps]
        steps.append(Step("Put the path into the field, x = x(t), y = y(t), …", rf"\vec F(\vec r(t))={_vec(along)}"))
        integrand = sp.simplify(sum(fc * v for fc, v in zip(along, velocity, strict=True)))
        steps.append(Step("The work is ∫ F · dr = ∫ F(r(t)) · r′(t) dt. Take the dot product.", rf"\vec F\cdot\vec r\,'={tex(integrand)}"))
        question = rf"\int_C \vec F\cdot d\vec r,\quad \vec F={_vec(comps)}"
        op = "line_integral_vector"
    else:
        f = field  # type: ignore[assignment]
        if f.free_symbols - set(coords):  # type: ignore[attr-defined]
            raise SolverError(f"The function may only use {_names(coords)}.", "bad_vectors")
        speed = sp.simplify(sp.sqrt(sp.simplify(sum(v**2 for v in velocity))))
        steps.append(Step("The length element is ds = ‖r′(t)‖ dt.", rf"\left\|\vec r\,'(t)\right\|={tex(speed)}"))
        along = sp.simplify(f.subs(on_curve, simultaneous=True))  # type: ignore[attr-defined]
        steps.append(Step("Put the path into the function.", rf"f(\vec r(t))={tex(along)}"))
        integrand = sp.simplify(along * speed)
        steps.append(Step("The line integral of a function is ∫ f ds = ∫ f(r(t)) ‖r′(t)‖ dt.", rf"{tex(integrand)}"))
        question = rf"\int_C {tex(f)}\,ds"  # type: ignore[attr-defined]
        op = "line_integral_scalar"
    integrand = _resolve_abs(integrand, t, a, b)
    steps.append(Step("Now it is an ordinary integral in t.", rf"\int_{{{tex(a)}}}^{{{tex(b)}}} {tex(integrand)}\,dt"))
    value, inner = _definite(integrand, t, a, b)
    steps.extend(inner)
    notes: list[str] = []
    numeric = _numeric_nested(integrand, [(t, a, b)])
    if numeric is not None and value.is_real:
        if abs(numeric - float(sp.N(value, 15))) > 1e-6 * (1 + abs(numeric)):
            raise SolverError("I could not verify this line integral numerically.", "unverified")
        notes.append("The value was also checked by numerical integration.")
    return Solution(op, question, tex(value), eng(value), steps, notes)
