"""Checking differential-equation answers by substitution (spec section 7.2).

Two kinds of answer:

ode_solution  the student gives a solution (explicit ``y = ...`` or implicit ``F(x,y) = C``).
              It is accepted when substituting it into the equation gives 0 at many points, when it has
              the right number of independent arbitrary constants (or none, for an initial-value problem),
              and when it meets the initial or boundary conditions. Any equivalent form is accepted.
ode_family    the student gives a differential equation whose general solution is a given family
              (``y = c x^2 - x``, or implicit ``x^2 + y^2 = c^2``): the family must satisfy the student's equation,
              the equation must not contain the constants, and its order must equal the number of constants.

Notation: ``y'`` is the symbol ``y1``, ``y''`` is ``y2``, ``y'''`` is ``y3``; ``dy/dx`` is accepted as well.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

import mpmath as mp
import sympy as sp
from mpmath.libmp import NoConvergence

from .equations import split_equation, to_text
from .errors import ParseError
from .parser import parse

mp.mp.dps = 40

X = sp.Symbol("x", real=True)
Y = sp.Symbol("y", real=True)
DERIVS = [Y] + [sp.Symbol(f"y{k}", real=True) for k in range(1, 5)]
_RESERVED = {"x", "y", "y1", "y2", "y3", "y4"}
TOL = sp.Float("1e-20")
MAX_ORDER = 3


@dataclass
class Condition:
    """y^(derivative)(at) = value, with `at` and `value` written in engine syntax."""

    at: str
    value: str
    derivative: int = 0


@dataclass
class OdeSpec:
    order: int
    equation: str | None = None  # for ode_solution: "F(x,y,y1,y2) = 0" (or without "=")
    family: str | None = None  # for ode_family: "y = c*x^2 - x" or "x^2 + y^2 = c^2"
    constants: list[str] = field(default_factory=list)
    conditions: list[Condition] = field(default_factory=list)
    sample: tuple[float, float] = (0.6, 1.9)


@dataclass
class OdeResult:
    status: str  # correct | incorrect | invalid
    code: str
    message: str


def _ok() -> OdeResult:
    return OdeResult("correct", "ok", "Correct.")


def _bad(code: str, message: str) -> OdeResult:
    return OdeResult("incorrect", code, message)


def _invalid(code: str, message: str) -> OdeResult:
    return OdeResult("invalid", code, message)


# dy/dx, d2y/dx2, d^2y/dx^2, also with the extra parentheses that the LaTeX converter adds around fractions
_LEIBNIZ = re.compile(r"\(*\s*d(?:\^?\(?(?P<n>[23])\)?)?\s*y\s*\)*\s*/\s*\(*\s*dx(?:\^?\(?[23]\)?)?\s*\)*")


def _leibniz(text: str) -> str:
    """Accept dy/dx and d2y/dx2 as well as y' and y''."""
    return _LEIBNIZ.sub(lambda m: " y" + "'" * int(m.group("n") or 1) + " ", text)


def _prepare(text: str, fmt: str) -> str:
    prepared = to_text(text, fmt)
    prepared = _leibniz(prepared)
    return prepared


def _parse_equation(text: str, fmt: str) -> tuple[sp.Expr, sp.Expr]:
    return split_equation(_prepare(text, fmt), "text", None)


def _constants_of(expr: sp.Expr) -> list[sp.Symbol]:
    return sorted((s for s in expr.free_symbols if s.name not in _RESERVED), key=lambda s: s.name)


def _order_of(expr: sp.Expr) -> int:
    top = 0
    for k, s in enumerate(DERIVS):
        if k and s in expr.free_symbols:
            top = k
    return top


def _numeric(expr: sp.Expr, sub: dict[sp.Symbol, object]) -> sp.Expr | None:
    try:
        value = sp.N(expr.subs(sub), 35)
    except (ZeroDivisionError, TypeError, ValueError, OverflowError):
        return None
    if not value.is_number or value.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
        return None
    if value.has(sp.I):
        re_, im_ = value.as_real_imag()
        if abs(im_) > sp.Float("1e-25"):
            return None
        return sp.Float(re_)
    return value


def _is_zero(value: sp.Expr, scale: sp.Expr) -> bool:
    return abs(value) <= TOL * (1 + abs(scale))


def _derivatives(f: sp.Expr, order: int) -> list[sp.Expr]:
    out = [f]
    for _ in range(order):
        out.append(sp.diff(out[-1], X))
    return out


def _explicit_form(left: sp.Expr, right: sp.Expr) -> sp.Expr | None:
    """If the equation is y = f(x, ...) or f(x, ...) = y return f."""
    if left == Y and Y not in right.free_symbols:
        return right
    if right == Y and Y not in left.free_symbols:
        return left
    return None


def _random_constants(consts: list[sp.Symbol], rng: random.Random) -> dict[sp.Symbol, object]:
    return {c: sp.Rational(rng.randint(3, 19), rng.randint(2, 7)) for c in consts}


def _sample_xs(spec: OdeSpec, n: int, rng: random.Random) -> list[sp.Rational]:
    lo, hi = spec.sample
    return [sp.Rational(round(rng.uniform(lo, hi) * 1000), 1000) for _ in range(n)]


def _implicit_points(
    g: sp.Expr, consts: list[sp.Symbol], spec: OdeSpec, rng: random.Random, count: int
) -> list[tuple[dict[sp.Symbol, object], sp.Expr]]:
    """Points (substitution, y) on the curve g(x, y, constants) = 0."""
    guesses = [sp.Rational(1, 2), sp.Integer(1), sp.Integer(2), sp.Rational(3, 2), sp.Integer(-1), sp.Integer(4)]
    out: list[tuple[dict[sp.Symbol, object], sp.Expr]] = []
    tries = 0
    while len(out) < count and tries < count * 15:
        tries += 1
        sub = _random_constants(consts, rng)
        x0 = _sample_xs(spec, 1, rng)[0]
        sub[X] = x0
        f = g.subs(sub)
        for guess in guesses + [sp.Float(rng.uniform(0.3, 3))]:
            try:
                root = sp.nsolve(f, Y, guess, tol=1e-30, maxsteps=60, prec=40)
            except (ValueError, ZeroDivisionError, TypeError, NoConvergence):
                continue
            if root.is_real and abs(sp.N(f.subs(Y, root), 40)) < 1e-25:
                out.append(({**sub, Y: root}, root))
                break
    return out


def _implicit_derivatives(g: sp.Expr, order: int) -> list[sp.Expr]:
    """y', y'', ... of the curve g(x, y) = 0 as expressions in x, y (and constants)."""
    return [sp.idiff(g, Y, X, n) for n in range(1, order + 1)]


def _residual_points(spec: OdeSpec, ode: sp.Expr, left: sp.Expr, right: sp.Expr, rng: random.Random):
    """Yield (sub, residual, scale) at sample points of the student's solution."""
    explicit = _explicit_form(left, right)
    order = spec.order
    if explicit is not None:
        f = explicit
        consts = _constants_of(f)
        derivs = _derivatives(f, order)
        for _ in range(30):
            sub = _random_constants(consts, rng)
            sub[X] = _sample_xs(spec, 1, rng)[0]
            vals = [_numeric(d, sub) for d in derivs]
            if any(v is None for v in vals):
                continue
            mapping = {DERIVS[k]: vals[k] for k in range(order + 1)}
            res = _numeric(ode.subs(mapping), {X: sub[X]})
            if res is None:
                continue
            yield sub, res, sum(abs(v) for v in vals)
        return
    g = left - right
    consts = _constants_of(g)
    ders = _implicit_derivatives(g, order)
    for sub, y0 in _implicit_points(g, consts, spec, rng, 16):
        vals = [_numeric(d, sub) for d in ders]
        if any(v is None for v in vals):
            continue
        mapping = {DERIVS[0]: y0, **{DERIVS[k + 1]: vals[k] for k in range(order)}}
        res = _numeric(ode.subs(mapping), {X: sub[X]})
        if res is None:
            continue
        yield sub, res, sum(abs(v) for v in vals) + abs(y0)


def _jacobian_rank(f: sp.Expr, consts: list[sp.Symbol], spec: OdeSpec, rng: random.Random) -> int:
    rows = []
    base = _random_constants(consts, rng)
    for x0 in _sample_xs(spec, len(consts) + 4, rng):
        row = []
        for c in consts:
            v = _numeric(sp.diff(f, c), {**base, X: x0})
            if v is None:
                break
            row.append(mp.mpf(str(sp.re(v))))
        else:
            rows.append(row)
    if len(rows) < len(consts):
        return len(consts)  # cannot decide; do not penalise
    sv = mp.svd_r(mp.matrix(rows), compute_uv=False)
    top = max(sv) if len(sv) else mp.mpf(0)
    if top == 0:
        return 0
    return sum(1 for s in sv if s > mp.mpf("1e-12") * top)


def check_solution(student: str, spec: OdeSpec, fmt: str = "auto") -> OdeResult:
    """Is the student's answer a solution (general, or particular when conditions are given)?"""
    if spec.equation is None or not 1 <= spec.order <= MAX_ORDER:
        raise ParseError("The problem is not configured correctly.", "bad_spec")
    rng = random.Random(5)
    ode_left, ode_right = split_equation(spec.equation, "text", None) if "=" in spec.equation else (
        parse(spec.equation, fmt="text").value,
        sp.Integer(0),
    )
    ode = sp.sympify(ode_left) - sp.sympify(ode_right)

    try:
        left, right = _parse_equation(student, fmt)
    except ParseError as exc:
        if exc.code == "not_an_equation":
            return _invalid("not_an_equation", "Write your solution as an equation, like y = … or F(x, y) = C.")
        raise
    names = {s.name for s in left.free_symbols | right.free_symbols}
    if names & {"y1", "y2", "y3", "y4"}:
        return _invalid("derivative_in_solution", "A solution must not contain y′ or y″. Solve the equation first.")
    explicit = _explicit_form(left, right)
    g = left - right
    consts = _constants_of(explicit if explicit is not None else g)
    particular = bool(spec.conditions)

    if explicit is None and spec.order > 1 and not particular and Y not in g.free_symbols:
        return _invalid("no_y", "Your equation does not contain y.")
    if X not in g.free_symbols and Y not in g.free_symbols:
        return _invalid("no_variables", "Your answer does not contain x or y.")

    if particular and consts:
        names_ = ", ".join(c.name for c in consts)
        return _bad("constant_left", f"This problem gives conditions, so the answer must be one particular solution without {names_}.")
    if not particular:
        if not consts:
            return _bad("no_constant", f"A general solution of an equation of order {spec.order} has {spec.order} arbitrary constant(s). Yours has none.")
        if len(consts) > spec.order:
            return _bad("too_many_constants", f"An equation of order {spec.order} has {spec.order} independent constant(s); yours has {len(consts)}.")

    residuals = list(_residual_points(spec, ode, left, right, rng))
    if len(residuals) < 6:
        return _invalid("cannot_evaluate", "I could not evaluate your answer at enough points. Check that it is defined for x between "
                        f"{spec.sample[0]} and {spec.sample[1]}.")
    for _sub, res, scale in residuals:
        if not _is_zero(res, scale):
            return _bad("not_a_solution", "Substitute your answer into the equation: it does not satisfy it.")

    if not particular and consts:
        rank = _jacobian_rank(explicit, consts, spec, rng) if explicit is not None else len(consts)
        if rank < spec.order:
            if len(consts) < spec.order:
                return _bad("not_general", f"This is a solution, but not the general one: it needs {spec.order} independent arbitrary constants.")
            return _bad("dependent_constants", "Some of your constants are not independent (they can be merged into fewer constants).")

    for cond in spec.conditions:
        ok = _check_condition(cond, explicit, g, spec)
        if not ok:
            return _bad("condition_not_met", "Your solution satisfies the equation but not the given condition.")
    return _ok()


def _check_condition(cond: Condition, explicit: sp.Expr | None, g: sp.Expr, spec: OdeSpec) -> bool:
    at = sp.sympify(parse(cond.at, fmt="text").value)
    target = sp.sympify(parse(cond.value, fmt="text").value)
    if explicit is not None:
        d = sp.diff(explicit, X, cond.derivative) if cond.derivative else explicit
        value = d.subs(X, at)
        return bool(sp.simplify(value - target) == 0 or abs(sp.N(value - target, 30)) < sp.Float("1e-25"))
    if cond.derivative == 0:
        residue = g.subs({X: at, Y: target})
        return bool(sp.simplify(residue) == 0 or abs(sp.N(residue, 30)) < sp.Float("1e-25"))
    # implicit and a derivative condition: use the implicit derivative at the point (y = value of y at `at`
    # is not available here), so only first-order IVPs are supported for implicit answers.
    return False


def check_family(student: str, spec: OdeSpec, fmt: str = "auto") -> OdeResult:
    """Does the student's differential equation have the given family as its general solution?"""
    if spec.family is None or not 1 <= spec.order <= MAX_ORDER:
        raise ParseError("The problem is not configured correctly.", "bad_spec")
    rng = random.Random(9)
    const_syms = [sp.Symbol(c, real=True) for c in spec.constants]
    fam_left, fam_right = split_equation(spec.family, "text", None) if "=" in spec.family else (
        Y,
        parse(spec.family, fmt="text").value,
    )

    try:
        s_left, s_right = _parse_equation(student, fmt)
    except ParseError as exc:
        if exc.code == "not_an_equation":
            return _invalid("not_an_equation", "Write a differential equation with an “=” sign, using y′, y″ …")
        raise
    ode = s_left - s_right
    if sp.simplify(ode) == 0:
        return _invalid("trivial", "That equation says nothing (0 = 0).")
    leftover = {s.name for s in ode.free_symbols} - _RESERVED
    if leftover:
        return _bad("constants_left", "Your equation still contains the constant(s) "
                    f"{', '.join(sorted(leftover))}. Eliminate the arbitrary constants.")
    top = _order_of(ode)
    if top < spec.order:
        return _bad("order_too_low", f"The general solution has {spec.order} arbitrary constant(s), so the equation has order {spec.order}.")
    if top > spec.order:
        return _bad("order_too_high", f"Eliminate the constants with the lowest order possible: the equation should have order {spec.order}.")

    sub_spec = OdeSpec(order=spec.order, sample=spec.sample)
    explicit = _explicit_form(fam_left, fam_right)
    count = 0
    if explicit is not None:
        derivs = _derivatives(explicit, spec.order)
        for _ in range(30):
            sub = _random_constants(const_syms, rng)
            x0 = _sample_xs(sub_spec, 1, rng)[0]
            sub[X] = x0
            vals = [_numeric(d, sub) for d in derivs]
            if any(v is None for v in vals):
                continue
            mapping = {DERIVS[k]: vals[k] for k in range(spec.order + 1)}
            res = _numeric(ode.subs(mapping), {X: x0})
            if res is None:
                continue
            count += 1
            if not _is_zero(res, sum(abs(v) for v in vals)):
                return _bad("family_not_solution", "The general solution does not satisfy your equation.")
    else:
        g = fam_left - fam_right
        ders = _implicit_derivatives(g, spec.order)
        for sub, y0 in _implicit_points(g, const_syms, sub_spec, rng, 18):
            vals = [_numeric(d, sub) for d in ders]
            if any(v is None for v in vals):
                continue
            mapping = {DERIVS[0]: y0, **{DERIVS[k + 1]: vals[k] for k in range(spec.order)}}
            res = _numeric(ode.subs(mapping), {X: sub[X]})
            if res is None:
                continue
            count += 1
            if not _is_zero(res, sum(abs(v) for v in vals) + abs(y0)):
                return _bad("family_not_solution", "The general solution does not satisfy your equation.")
    if count < 6:
        return _invalid("cannot_evaluate", "I could not test your equation at enough points.")
    # the equation must really involve the highest derivative (not a multiple of a lower-order relation)
    if sp.simplify(sp.diff(ode, DERIVS[spec.order])) == 0:
        return _bad("order_too_low", "Your equation does not involve the highest derivative.")
    return _ok()
