"""The step-by-step solver: results are compared with independent computations, and unreadable or hostile input is refused."""

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from allmaths_engine.main import app
from allmaths_engine.solver import solve_text
from allmaths_engine.solver.types import SolverError
from allmaths_engine.solver_pool import SolverPool, _slow_worker_for_tests

x = sp.Symbol("x", real=True)
client = TestClient(app)
H = {"X-Engine-Token": "test-token-123456"}


def titles(sol):
    return " ".join(s.title for s in sol.steps)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("derivative of x^2*sin(x)", 2 * x * sp.sin(x) + x**2 * sp.cos(x)),
        ("derivative of (x^2+1)/(x-3)", sp.diff((x**2 + 1) / (x - 3), x)),
        ("d/dx e^(3x)*cos(x)", sp.diff(sp.exp(3 * x) * sp.cos(x), x)),
        ("derivative of sqrt(x^2+1)", x / sp.sqrt(x**2 + 1)),
        ("second derivative of x^4-3x^2", 12 * x**2 - 6),
        ("derivative of ln(sin(x))", sp.cos(x) / sp.sin(x)),
    ],
)
def test_derivatives_are_right(text, expected):
    sol = solve_text(text)
    got = sp.sympify(sol.answer_text.replace("^", "**"), locals={"x": x})
    assert sp.simplify(got - expected) == 0


def test_derivative_names_the_rules_it_uses():
    assert "Product rule" in titles(solve_text("derivative of x^2*sin(x)"))
    assert "Quotient rule" in titles(solve_text("derivative of sin(x)/x"))
    assert "Chain rule" in titles(solve_text("derivative of sin(3x)"))


@pytest.mark.parametrize(
    ("text", "answer"),
    [("integrate x^2+3x from 0 to 2", "26/3"), ("integral of 1/(1+x^2) from 0 to 1", "pi/4"), ("integrate sqrt(1-x^2) from 0 to 1", "pi/4"), ("integral of x*e^x from 0 to 1", "1")],
)
def test_definite_integrals(text, answer):
    assert solve_text(text).answer_text == answer


def test_indefinite_integral_is_verified_by_differentiation():
    sol = solve_text("integral of x*cos(x)")
    anti = sp.sympify(sol.answer_text.replace(" + C", "").replace("^", "**"), locals={"x": x})
    assert sp.simplify(sp.diff(anti, x) - x * sp.cos(x)) == 0
    assert "Integration by parts" in titles(sol)


def test_no_antiderivative_is_reported_not_invented():
    with pytest.raises(SolverError):
        solve_text("integral of x^x")


def test_a_special_function_antiderivative_is_still_checked():
    sol = solve_text("integral of sin(x)/x")
    assert "Si" in sol.answer_text


@pytest.mark.parametrize(
    ("text", "answer"),
    [("limit of sin(x)/x as x->0", "1"), ("limit of (x^2-1)/(x-1) as x->1", "2"), ("limit of (1-cos(x))/x^2 as x->0", "1/2"), ("limit of (3x^2+1)/(x^2-5) as x->oo", "3")],
)
def test_limits(text, answer):
    assert solve_text(text).answer_text == answer


def test_equations_and_the_for_variable_guard():
    assert solve_text("solve x^2-5x+6=0").answer_text == "x=2, x=3"
    assert solve_text("2x+3=11").answer_text == "x=4"
    assert solve_text("x^2+1=0").answer_text == "no real solution"
    assert solve_text("solve x^2=2x for x").answer_text == "x=0, x=2"  # "for x" must not be read as a product of variables


def test_systems():
    assert solve_text("x+y=5, x-y=1").answer_text == "x=3, y=2"
    assert solve_text("2x+3y=7, x-y=1").answer_text == "x=2, y=1"


def test_differential_equations_are_checked_by_substitution():
    assert "C1" in solve_text("y' = x*y").answer_text
    assert solve_text("y'' + y = 0, y(0)=1, y'(0)=0").answer_text == "y = cos(x)"
    assert "characteristic equation" in titles(solve_text("y'' - 3y' + 2y = 0"))


def test_vectors():
    assert solve_text("dot (1,2,3),(4,5,6)").answer_text == "32"
    assert solve_text("cross of (1,0,0) and (0,1,0)").answer_text == "(0, 0, 1)"
    assert solve_text("norm of (3,4)").answer_text == "5"
    assert solve_text("angle between (1,0) and (1,1)").answer_text == "pi/4"


@pytest.mark.parametrize("text", ["hello world", "import os", "__import__('os')", "x*y*z+xyz", "open('f')", "", "1" * 400])
def test_nonsense_and_hostile_input_is_refused(text):
    with pytest.raises(SolverError):
        solve_text(text)


def test_api_requires_the_token_and_answers():
    body = {"input": "derivative of x^3", "operation": "auto"}
    assert client.post("/v1/solve", json=body).status_code == 401
    j = client.post("/v1/solve", json=body, headers=H).json()
    assert j["ok"] and j["solution"]["answer_text"] == "3*x^2" and j["solution"]["steps"]
    bad = client.post("/v1/solve", json={"input": "hello world"}, headers=H).json()
    assert not bad["ok"] and bad["code"] == "unknown_word"
    assert client.post("/v1/solve", json={"input": "x" * 301}, headers=H).status_code == 422


def test_a_stuck_worker_is_killed_and_the_pool_keeps_working():
    slow = SolverPool(workers=1, timeout=1.0, target=_slow_worker_for_tests)
    try:
        r = slow.run("anything", "auto")
        assert r["error"] == "timeout"
    finally:
        slow.close()
    fast = SolverPool(workers=1, timeout=30.0)
    try:
        assert fast.run("2+2", "auto")["solution"]["answer_text"] == "4"
        assert fast.run("derivative of x^2", "auto")["solution"]["answer_text"] == "2*x"
    finally:
        fast.close()
