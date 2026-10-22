"""Answer types beyond numbers, expressions and vectors: regions, equations, directions, point sets and
differential-equation answers. Dispatched from checker.check_answer."""

from __future__ import annotations

import re

import sympy as sp

from . import ode as ode_mod
from .checker import CheckResult, Mistake
from .equations import (
    _depth0_equals,
    directions_equivalent,
    equation_poly,
    equations_equivalent,
    parse_points,
    point_sets_equal,
    to_text,
)
from .errors import EngineError, ParseError
from .parser import parse
from .region import Region, compile_region, regions_equal, sample_points

_DECIMAL = re.compile(r"(?<![\w.])(?:\d+\.\d+|\.\d+)")
DECIMAL_MESSAGE = (
    "Please enter an exact value (a fraction, a radical such as 2√3, or a multiple of π), not a decimal."
)
WRONG = "Not correct yet."


def check_extra(
    answer_type: str,
    student: str,
    correct: str,
    fmt: str,
    variables: list[str] | None,
    coordinates: list[str] | None,
    mistakes: list[Mistake],
    allow_decimal: bool,
    ode: object | None,
) -> CheckResult:
    prepared = to_text(student, fmt) if student.strip() else ""
    if not prepared:
        return CheckResult("invalid", "empty", "The answer is empty.")
    if not allow_decimal and _DECIMAL.search(prepared):
        return CheckResult("invalid", "decimal_not_allowed", DECIMAL_MESSAGE)
    coords = list(coordinates or ["x", "y"])
    if answer_type == "region":
        return _region(student, correct, fmt, coords, mistakes)
    if answer_type == "equation":
        return _equation(student, correct, fmt, coords, variables, mistakes)
    if answer_type == "direction":
        return _direction(student, correct, fmt, variables, mistakes)
    if answer_type == "points":
        return _points(student, correct, fmt, variables)
    if answer_type in ("ode_solution", "ode_family"):
        return _ode(answer_type, student, fmt, ode)
    raise EngineError(f"Unknown answer type {answer_type}.", "bad_type")


# --- regions ---------------------------------------------------------------------------------------------
def _on_boundary(region: Region, pt: dict[str, float]) -> bool:
    here = region.contains(pt)
    for v in pt:
        for d in (-1e-3, 1e-3):
            q = dict(pt)
            q[v] = pt[v] + d
            if region.contains(q) != here:
                return True
    return False


def _region(student: str, correct: str, fmt: str, coords: list[str], mistakes: list[Mistake]) -> CheckResult:
    key = compile_region(correct, coords, "text")
    stu = compile_region(student, coords, fmt)
    same, witness = regions_equal(key, stu, coords)
    if same:
        return CheckResult("correct", "ok", "Correct.", method="sampling")
    for m in mistakes:
        try:
            wrong = compile_region(m.expr, coords, "text")
        except EngineError:
            continue
        if regions_equal(wrong, stu, coords)[0]:
            return CheckResult("incorrect", "known_mistake", WRONG, hint=m.hint)
    if witness is not None and _on_boundary(key, witness):
        return CheckResult(
            "incorrect", "boundary", WRONG,
            hint="Look at the boundary: check whether it belongs to the set (≤ or <, ≥ or >).",
        )
    return CheckResult("incorrect", "wrong", WRONG)


# --- equations -------------------------------------------------------------------------------------------
def _equation(
    student: str, correct: str, fmt: str, coords: list[str], variables: list[str] | None, mistakes: list[Mistake]
) -> CheckResult:
    key_poly = equation_poly(correct, "text")
    allowed = {s.name for s in key_poly.free_symbols} | set(coords) | set(variables or [])
    if len(_depth0_equals(to_text(student, fmt))) != 1:
        return CheckResult("invalid", "not_an_equation", "Write an equation with an “=” sign, like x + 2y − z = 0.")
    stu_poly = equation_poly(student, fmt, allowed)
    coord_set = set(coords)
    if equations_equivalent(stu_poly, key_poly, coord_set):
        return CheckResult("correct", "ok", "Correct.", method="proportional")
    for m in mistakes:
        try:
            wrong = equation_poly(m.expr, "text", allowed)
        except EngineError:
            continue
        if equations_equivalent(stu_poly, wrong, coord_set):
            return CheckResult("incorrect", "known_mistake", WRONG, hint=m.hint)
    return CheckResult("incorrect", "wrong", WRONG)


# --- directions ------------------------------------------------------------------------------------------
def _direction(
    student: str, correct: str, fmt: str, variables: list[str] | None, mistakes: list[Mistake]
) -> CheckResult:
    key = parse(correct, fmt="text").value
    if not isinstance(key, sp.Tuple):
        raise EngineError("A direction key must be a vector.", "key_type_mismatch")
    allowed = {s.name for c in key for s in c.free_symbols} | set(variables or [])
    stu = parse(student, fmt=fmt, variables=allowed).value
    if not isinstance(stu, sp.Tuple):
        return CheckResult("invalid", "expected_vector", "Give a vector such as (1, 2, −1).")
    if len(stu) != len(key):
        return CheckResult("invalid", "wrong_dimension", f"A vector with {len(key)} components is expected here.")
    if directions_equivalent(stu, key):
        return CheckResult("correct", "ok", "Correct.", method="parallel")
    for m in mistakes:
        try:
            wrong = parse(m.expr, fmt="text", variables=allowed).value
        except EngineError:
            continue
        if isinstance(wrong, sp.Tuple) and directions_equivalent(stu, wrong):
            return CheckResult("incorrect", "known_mistake", WRONG, hint=m.hint)
    return CheckResult("incorrect", "wrong", WRONG)


# --- sets of points --------------------------------------------------------------------------------------
def _points(student: str, correct: str, fmt: str, variables: list[str] | None) -> CheckResult:
    key = parse_points(correct, "text")
    allowed = {s.name for p in key for c in p for s in c.free_symbols} | set(variables or [])
    stu = parse_points(student, fmt, allowed)
    same, matched = point_sets_equal(stu, key)
    if same:
        return CheckResult("correct", "ok", "Correct.", method="set")
    if matched < len(stu):
        return CheckResult("incorrect", "wrong", WRONG, hint="At least one of the points you gave is not correct.")
    return CheckResult("incorrect", "missing", WRONG, hint="Every point you gave is right, but some points are missing.")


# --- differential equations -----------------------------------------------------------------------------
def _ode(answer_type: str, student: str, fmt: str, spec: object | None) -> CheckResult:
    if not isinstance(spec, ode_mod.OdeSpec):
        raise EngineError("This problem has no differential-equation specification.", "bad_spec")
    try:
        result = (
            ode_mod.check_solution(student, spec, fmt)
            if answer_type == "ode_solution"
            else ode_mod.check_family(student, spec, fmt)
        )
    except ParseError as exc:
        return CheckResult("invalid", exc.code, exc.message)
    if result.status == "correct":
        return CheckResult("correct", "ok", "Correct.", method="substitution")
    if result.status == "invalid":
        return CheckResult("invalid", result.code, result.message)
    return CheckResult("incorrect", result.code, WRONG, hint=result.message)


__all__ = ["check_extra", "sample_points"]
