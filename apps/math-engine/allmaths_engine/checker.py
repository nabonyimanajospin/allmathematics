"""Mathematical answer checking (spec section 7.2).

Answers are compared by meaning, not by text: 2/sqrt(2) equals sqrt(2). All work is exact.
A result has one of three statuses:
  correct    the answer is mathematically equivalent to the key
  incorrect  a valid answer that is wrong (counts as an attempt)
  invalid    not a usable answer (syntax error, decimal where exact is required, wrong kind of value);
             the student is asked to fix it and the attempt is NOT counted
"""

from __future__ import annotations

import math
import random
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal, TypeVar

import sympy as sp

from .errors import ComplexityError, EngineError
from .parser import Parsed, parse
from .render import value_to_latex

AnswerType = Literal[
    "number", "expression", "vector", "point", "multiple_choice", "auto",
    "region", "equation", "direction", "points", "ode_solution", "ode_family",
]
EXTRA_TYPES = {"region", "equation", "direction", "points", "ode_solution", "ode_family"}
Status = Literal["correct", "incorrect", "invalid"]

CHECK_TIMEOUT_SECONDS = 8.0
NUMERIC_POINTS = 20
_RNG_SEED = 20261021
_T = TypeVar("_T")

DECIMAL_MESSAGE = (
    "Please enter an exact value (a fraction, a radical such as 2√3, or a multiple of π), not a decimal."
)


@dataclass
class Mistake:
    expr: str
    hint: str


@dataclass
class Constraint:
    """Expressions are compared on the curve or surface `equation` = 0, solving for `dependent`."""

    equation: str
    dependent: str
    ranges: dict[str, tuple[float, float]] = field(default_factory=dict)
    #: symbols to replace before comparing, e.g. {"y1": "(2*y-x^2)/(y^2-2*x)"} so that answers may use y'
    substitutions: dict[str, str] = field(default_factory=dict)


@dataclass
class CheckResult:
    status: Status
    code: str
    message: str
    student_latex: str | None = None
    method: str | None = None
    parts: list[bool] | None = None
    hint: str | None = None
    extra: dict[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------------------------------------
def run_limited(fn: Callable[[], _T], seconds: float = CHECK_TIMEOUT_SECONDS) -> _T:
    """Run fn with a wall-clock limit. The worker thread cannot be killed, so the web layer must also
    rate-limit; process isolation is planned for Phase 2 (see docs/engine-hardening.md)."""
    box: dict[str, object] = {}

    def target() -> None:
        try:
            box["value"] = fn()
        except BaseException as exc:  # noqa: BLE001 - re-raised in caller
            box["error"] = exc

    th = threading.Thread(target=target, daemon=True)
    th.start()
    th.join(seconds)
    if th.is_alive():
        raise ComplexityError("That answer took too long to check. Try a simpler form.", "timeout")
    if "error" in box:
        raise box["error"]  # type: ignore[misc]
    return box["value"]  # type: ignore[return-value]


def _sample_points(symbols: list[sp.Symbol], n: int) -> list[dict[sp.Symbol, sp.Expr]]:
    rng = random.Random(_RNG_SEED)
    pts = []
    for _ in range(n):
        pt = {}
        for s in symbols:
            num = rng.choice([v for v in range(-12, 13) if v != 0])
            den = rng.choice([1, 2, 3, 4, 5])
            pt[s] = sp.Rational(num, den)
        pts.append(pt)
    return pts


def _finite(v: sp.Expr) -> bool:
    return v.is_number and v.is_finite is not False and v not in (sp.nan, sp.zoo, sp.oo, -sp.oo)


def numeric_test(a: sp.Expr, b: sp.Expr, points: int = NUMERIC_POINTS) -> tuple[bool, int]:
    """Compare a and b at deterministic pseudo-random rational points.
    Returns (no_disagreement, number_of_valid_points)."""
    symbols = sorted((a.free_symbols | b.free_symbols), key=lambda s: s.name)
    valid = 0
    for pt in _sample_points(symbols, points):
        try:
            va, vb = sp.N(a.subs(pt), 30), sp.N(b.subs(pt), 30)
        except (ZeroDivisionError, TypeError, ValueError):
            continue
        if not (_finite(va) and _finite(vb)):
            continue
        valid += 1
        if abs(va - vb) > sp.Float("1e-15") * (1 + abs(va)):
            return False, valid
    return True, valid


def exprs_equivalent(a: sp.Expr, b: sp.Expr) -> tuple[bool, str]:
    """Exact equivalence. Returns (equal, method) with method in exact | symbolic | numeric."""
    d = a - b
    if d == 0:
        return True, "exact"
    if not d.free_symbols:
        if sp.simplify(d) == 0:
            return True, "symbolic"
        v = sp.N(d, 120)
        # A difference below 1e-80 at 120 digits is zero for every algebraic constant a student can type.
        if v.is_number and abs(v) < sp.Float("1e-80"):
            return True, "numeric"
        return False, "symbolic"
    symbolic_zero = sp.simplify(d) == 0
    agree, valid = numeric_test(a, b)
    if symbolic_zero:
        return (agree, "symbolic") if agree else (False, "inconsistent")
    if agree and valid >= (3 * NUMERIC_POINTS) // 4:
        return True, "numeric"
    return False, "symbolic"


# --------------------------------------------------------------------------------------------------
def _round_window(correct: sp.Expr, sig_figs: int) -> sp.Float:
    c = abs(sp.N(correct, 50))
    if c == 0:
        return sp.Float(0)
    exponent = math.floor(math.log10(float(c)))
    return sp.Float(5) * sp.Float(10) ** (exponent - sig_figs)


def _approx_equal(student: sp.Expr, correct: sp.Expr, sig_figs: int) -> bool:
    s, c = sp.N(student, 50), sp.N(correct, 50)
    return bool(abs(s - c) <= _round_window(correct, sig_figs) * sp.Float("1.000000001"))


def _vec_from_ijk(expr: sp.Expr, dim: int) -> sp.Tuple | None:
    i, j, k = (sp.Symbol(n, real=True) for n in "ijk")
    basis = [i, j, k][:dim]
    expr = sp.expand(expr)
    coeffs = [expr.coeff(b) for b in basis]
    rest = sp.expand(expr - sum((c * b for c, b in zip(coeffs, basis, strict=False)), sp.Integer(0)))
    if rest != 0 or any(c.free_symbols & set([i, j, k]) for c in coeffs):
        return None
    return sp.Tuple(*coeffs)


def _declared_symbols(variables: list[str] | None, correct: Parsed) -> set[str]:
    return set(variables or []) | set(correct.names)


def _kind_of(value: object) -> str:
    if isinstance(value, sp.Tuple):
        return "vector"
    assert isinstance(value, sp.Expr)
    return "number" if not value.free_symbols else "expression"


def check_answer(
    *,
    answer_type: AnswerType,
    student: str,
    correct: str,
    input_format: str = "auto",
    variables: list[str] | None = None,
    allow_decimal: bool = False,
    sig_figs: int | None = None,
    mistakes: list[Mistake] | None = None,
    coordinates: list[str] | None = None,
    constraint: Constraint | None = None,
    ode: object | None = None,
) -> CheckResult:
    try:
        return run_limited(
            lambda: _check(
                answer_type, student, correct, input_format, variables, allow_decimal, sig_figs, mistakes or [],
                coordinates, constraint, ode,
            )
        )
    except EngineError as exc:
        return CheckResult("invalid", exc.code, exc.message)


def _check(
    answer_type: AnswerType,
    student_raw: str,
    correct_raw: str,
    fmt: str,
    variables: list[str] | None,
    allow_decimal: bool,
    sig_figs: int | None,
    mistakes: list[Mistake],
    coordinates: list[str] | None = None,
    constraint: Constraint | None = None,
    ode: object | None = None,
) -> CheckResult:
    if answer_type == "multiple_choice":
        return _check_choice(student_raw, correct_raw)
    if answer_type in EXTRA_TYPES:
        from . import extra_types  # local import: extra_types builds on this module

        return extra_types.check_extra(
            answer_type, student_raw, correct_raw, fmt, variables, coordinates, mistakes, allow_decimal, ode
        )
    if correct_raw.strip() == "@dne":
        return _check_nonexistent(student_raw, answer_type)

    key = parse(correct_raw, fmt="text", trusted=True)  # the key is trusted text written by authors
    if key.has_decimal:
        raise EngineError("The answer key contains a decimal. Keys must be exact.", "decimal_in_key")
    kind = _kind_of(key.value)
    if answer_type == "auto":
        answer_type = kind  # type: ignore[assignment]
    if answer_type == "point":
        answer_type = "vector"
    if answer_type != kind:
        raise EngineError(f"The answer key is a {kind} but the problem type is {answer_type}.", "key_type_mismatch")

    allowed = _declared_symbols(variables, key)
    if answer_type == "vector":
        allowed |= {"i", "j", "k"}
    stu = parse(student_raw, fmt=fmt, variables=allowed)

    if stu.has_decimal and not allow_decimal:
        return CheckResult("invalid", "decimal_not_allowed", DECIMAL_MESSAGE)

    value = stu.value
    if answer_type == "vector":
        assert isinstance(key.value, sp.Tuple)
        if isinstance(value, sp.Expr) and (stu.names & {"i", "j", "k"}):
            converted = _vec_from_ijk(value, len(key.value))
            if converted is None:
                return CheckResult("invalid", "bad_vector", "Write the vector as (a, b, c) or a i + b j + c k.")
            value = converted
        if not isinstance(value, sp.Tuple):
            return CheckResult("invalid", "expected_vector", "A vector such as (1, 2, 3) is expected here.")
        if len(value) != len(key.value):
            return CheckResult(
                "invalid", "wrong_dimension", f"A vector with {len(key.value)} components is expected here."
            )
        return _check_vector(value, key.value, stu, mistakes, variables, allow_decimal, sig_figs, constraint)

    if isinstance(value, sp.Tuple):
        return CheckResult("invalid", "expected_scalar", "A single value is expected here, not a vector.")
    assert isinstance(value, sp.Expr) and isinstance(key.value, sp.Expr)

    if answer_type == "number" and value.free_symbols:
        names = ", ".join(sorted(s.name for s in value.free_symbols))
        msg = f"A number is expected here, but your answer contains {names}."
        return CheckResult("invalid", "expected_number", msg)

    latex = value_to_latex(value)
    ok, method = _scalar_equal(value, key.value, stu.has_decimal, sig_figs, constraint)
    if ok:
        return CheckResult("correct", "ok", "Correct.", latex, method)
    return _incorrect_scalar(value, key.value, latex, mistakes, allowed)


def _scalar_equal(
    value: sp.Expr,
    key: sp.Expr,
    decimal_used: bool,
    sig_figs: int | None,
    constraint: Constraint | None = None,
) -> tuple[bool, str]:
    if decimal_used:
        sf = sig_figs or 3
        return _approx_equal(value, key, sf), "approximation"
    ok, method = exprs_equivalent(value, key)
    if ok or constraint is None:
        return ok, method
    from .curves import equal_on_curve  # local import keeps the module light
    from .equations import equation_poly

    on_curve = equal_on_curve(
        value, key, equation_poly(constraint.equation, "text"), constraint.dependent, constraint.ranges,
        constraint.substitutions,
    )
    return (True, "on-curve") if on_curve else (False, method)


def _incorrect_scalar(
    value: sp.Expr, key: sp.Expr, latex: str, mistakes: list[Mistake], allowed: set[str]
) -> CheckResult:
    for m in mistakes:
        try:
            mk = parse(m.expr, fmt="text", variables=allowed)
        except EngineError:
            continue
        if isinstance(mk.value, sp.Expr) and exprs_equivalent(value, mk.value)[0]:
            return CheckResult("incorrect", "known_mistake", "Not correct yet.", latex, hint=m.hint)
    if key != 0 and exprs_equivalent(value, -key)[0]:
        return CheckResult("incorrect", "sign_error", "Not correct yet.", latex, hint="Check the sign of your answer.")
    return CheckResult("incorrect", "wrong", "Not correct yet.", latex)


def _check_vector(
    value: sp.Tuple,
    key: sp.Tuple,
    stu: Parsed,
    mistakes: list[Mistake],
    variables: list[str] | None,
    allow_decimal: bool,
    sig_figs: int | None,
    constraint: Constraint | None = None,
) -> CheckResult:
    latex = value_to_latex(value)
    parts: list[bool] = []
    method = "exact"
    for sv, kv in zip(value, key, strict=False):
        ok, m = _scalar_equal(sv, kv, stu.has_decimal, sig_figs, constraint)
        parts.append(ok)
        if ok and m in ("numeric", "approximation"):
            method = m
    if all(parts):
        return CheckResult("correct", "ok", "Correct.", latex, method, parts)
    allowed = set(variables or []) | {n for c in key for n in (s.name for s in c.free_symbols)}
    for m in mistakes:
        try:
            mk = parse(m.expr, fmt="text", variables=allowed)
        except EngineError:
            continue
        if isinstance(mk.value, sp.Tuple) and len(mk.value) == len(value):
            if all(exprs_equivalent(a, b)[0] for a, b in zip(value, mk.value, strict=False)):
                return CheckResult("incorrect", "known_mistake", "Not correct yet.", latex, parts=parts, hint=m.hint)
    if all(exprs_equivalent(a, -b)[0] for a, b in zip(value, key, strict=False)) and any(c != 0 for c in key):
        return CheckResult(
            "incorrect", "sign_error", "Not correct yet.", latex, parts=parts,
            hint="Check the direction (sign) of your vector.",
        )
    return CheckResult("incorrect", "wrong", "Not correct yet.", latex, parts=parts)


_NONEXISTENT = {
    "dne", "d.n.e.", "d.n.e", "does not exist", "doesnt exist", "doesn't exist", "no limit", "does not converge",
    "diverges", "divergent", "diverge", "the integral diverges", "limit does not exist", "infinite", "infinity",
    "oo", "∞", "none", "undefined", "not exist", "nonexistent", "non-existent", "@dne",
}


_NONEXISTENT_PHRASES = (
    "dne", "d.n.e", "does not exist", "doesnt exist", "doesn't exist", "no limit", "not exist", "does not converge",
    "diverge", "undefined", "nonexistent", "non-existent", "infinite", "infinity",
)


def _check_nonexistent(student: str, answer_type: str) -> CheckResult:
    """The key is “does not exist” (a limit that fails, an integral that diverges). Written words are accepted."""
    cleaned = " ".join(student.strip().lower().replace("’", "'").split())
    if not cleaned:
        return CheckResult("invalid", "empty", "The answer is empty.")
    exact = cleaned in _NONEXISTENT
    phrase = not any(ch.isdigit() for ch in cleaned) and any(p in cleaned for p in _NONEXISTENT_PHRASES)
    if exact or phrase:
        return CheckResult("correct", "ok", "Correct.", method="keyword")
    return CheckResult(
        "incorrect", "wrong", "Not correct yet.",
        hint="Check whether a finite value is really reached, whatever way you approach.",
    )


def _check_choice(student: str, correct: str) -> CheckResult:
    try:
        s, c = int(student.strip()), int(correct.strip())
    except ValueError:
        return CheckResult("invalid", "bad_choice", "Choose one of the options.")
    if s == c:
        return CheckResult("correct", "ok", "Correct.", method="choice")
    return CheckResult("incorrect", "wrong", "Not correct yet.", method="choice")


# --------------------------------------------------------------------------------------------------
def compute(expression: str) -> tuple[str, str]:
    """Evaluate a trusted content expression, e.g. cross((1,2,3),(4,5,6)). Returns (canonical text, latex)."""

    def work() -> tuple[str, str]:
        p = parse(expression, fmt="text", trusted=True)
        return str(p.value), value_to_latex(p.value)

    return run_limited(work)


def values_equal(expr_a: str, expr_b: str) -> tuple[bool, str]:
    """Used by content verification: do two trusted expressions denote the same exact value?"""

    def work() -> tuple[bool, str]:
        a, b = parse(expr_a, fmt="text", trusted=True), parse(expr_b, fmt="text", trusted=True)
        if a.has_decimal or b.has_decimal:
            raise EngineError("Content values must be exact (no decimals).", "decimal_in_content")
        va, vb = a.value, b.value
        if isinstance(va, sp.Tuple) != isinstance(vb, sp.Tuple):
            return False, "type"
        if isinstance(va, sp.Tuple):
            assert isinstance(vb, sp.Tuple)
            if len(va) != len(vb):
                return False, "dimension"
            results = [exprs_equivalent(x, y) for x, y in zip(va, vb, strict=False)]
            return all(r[0] for r in results), "vector"
        assert isinstance(va, sp.Expr) and isinstance(vb, sp.Expr)
        return exprs_equivalent(va, vb)

    return run_limited(work)
