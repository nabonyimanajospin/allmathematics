"""Multivariable solver: partial derivatives, gradient, extrema, Lagrange multipliers, iterated and line integrals.

Every expected value below was worked out by hand (the working is in the comment) and is also what SymPy gives.
"""

import pytest

from allmaths_engine.solver import solve_text
from allmaths_engine.solver.types import SolverError


def answer(text: str) -> str:
    return solve_text(text).answer_text


# --- partial derivatives --------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "problem, expected",
    [
        ("partial derivative of x^2*y wrt x", "2*x*y"),
        ("partial derivative of x^2*y^3 wrt x, y", "6*x*y^2"),  # f_xy = 2x * 3y^2
        ("second partial derivative of sin(x*y) wrt x", "-y^2*sin(x*y)"),
        ("partial derivative of x^2*y + y^3 wrt y at (1, 2)", "13"),  # x^2 + 3y^2 = 1 + 12
        ("∂ x*e^y wrt y", "x*exp(y)"),
    ],
)
def test_partial_derivatives(problem: str, expected: str) -> None:
    assert answer(problem) == expected


def test_mixed_partials_are_reported_equal() -> None:
    sol = solve_text("partial derivative of x^2*y^3 wrt x, y")
    assert any("other order" in n for n in sol.notes)


def test_partial_derivative_is_undefined_where_the_function_is_not() -> None:
    with pytest.raises(SolverError) as exc:
        solve_text("partial derivative of 1/x wrt x at (0)")
    assert exc.value.code == "undefined"


# --- gradient and directional derivative ---------------------------------------------------------------------------
def test_gradient_and_its_value() -> None:
    assert answer("gradient of x^2*y + z") == "(2*x*y, x^2, 1)"
    assert answer("gradient of x^2*y + z at (1,2,3)") == "(4, 1, 1)"  # (2xy, x^2, 1)
    assert answer("∇(x^2 + y^2) at x = 3, y = 4") == "(6, 8)"


def test_directional_derivative() -> None:
    # grad(xy) = (y, x) = (2, 1) at (1, 2); u = (3, 4)/5; 6/5 + 4/5 = 2
    assert answer("directional derivative of x*y at (1,2) in the direction (3,4)") == "2"


def test_gradient_needs_a_variable() -> None:
    with pytest.raises(SolverError) as exc:
        solve_text("gradient of 5")
    assert exc.value.code == "bad_variables"


# --- critical points ------------------------------------------------------------------------------------------------
def test_saddle_and_minimum() -> None:
    # f = x^3 - 3xy + y^3: gradient (3x^2 - 3y, 3y^2 - 3x) = 0 at (0,0) and (1,1)
    # (0,0): D = 0*0 - 9 < 0 saddle;  (1,1): D = 36 - 9 > 0 and f_xx = 6 > 0, f = -1
    assert answer("critical points of x^3 - 3*x*y + y^3") == "(0, 0): saddle point, f = 0; (1, 1): local minimum, f = -1"


def test_maximum_and_one_variable() -> None:
    assert answer("find the critical points of 4 - x^2 - y^2") == "(0, 0): local maximum, f = 4"
    assert answer("local extrema of x^3 - 3*x") == "(-1, ): local maximum, f = 2; (1, ): local minimum, f = -2".replace("(-1, )", "(-1)").replace("(1, )", "(1)")


def test_no_critical_points_and_infinitely_many() -> None:
    assert answer("critical points of x + y") == "no critical points"
    with pytest.raises(SolverError) as exc:
        solve_text("critical points of (x - y)^2")
    assert exc.value.code == "infinite"


def test_inconclusive_second_derivative_test_is_said_honestly() -> None:
    # f = x^4 + y^4 has its minimum at the origin, but D = 0 there, so the test tells nothing
    assert "inconclusive" in answer("critical points of x^4 + y^4")


# --- Lagrange multipliers ------------------------------------------------------------------------------------------
def test_lagrange_on_a_circle_is_absolute() -> None:
    # x + y on x^2 + y^2 = 1: maximum sqrt(2) at (sqrt2/2, sqrt2/2), minimum -sqrt(2) at the opposite point
    assert answer("maximize x + y subject to x^2 + y^2 = 1") == "maximum sqrt(2) at (sqrt(2)/2, sqrt(2)/2)"
    assert answer("minimize x + y subject to x^2 + y^2 = 1") == "minimum -sqrt(2) at (-sqrt(2)/2, -sqrt(2)/2)"
    both = answer("extrema of x^2 + 2*y^2 subject to x^2 + y^2 = 1")
    assert both == "maximum 2 at (0, -1) and (0, 1); minimum 1 at (-1, 0) and (1, 0)"


def test_lagrange_on_a_line_is_only_local() -> None:
    sol = solve_text("maximize x*y subject to x + y = 10")
    assert sol.answer_text == "(5, 5): local maximum, f = 25"
    assert any("local" in n for n in sol.notes)


def test_lagrange_in_three_variables() -> None:
    # x + y + z on the sphere of radius 1: maximum sqrt(3) where x = y = z = sqrt(3)/3
    assert answer("maximize x + y + z subject to x^2 + y^2 + z^2 = 1") == "maximum sqrt(3) at (sqrt(3)/3, sqrt(3)/3, sqrt(3)/3)"


def test_lagrange_with_two_constraints() -> None:
    # x + y + z on the plane z = 1 and the circle x^2 + y^2 = 1 is x + y + 1: maximum 1 + sqrt(2)
    assert answer("maximize x + y + z subject to z = 1 and x^2 + y^2 = 1") == "maximum 1 + sqrt(2) at (sqrt(2)/2, sqrt(2)/2, 1)"


# --- double and triple integrals -----------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "problem, expected",
    [
        ("double integral of x*y over x from 0 to 1, y from 0 to x", "1/8"),  # int_0^1 x * x^2/2 dx
        ("double integral of x*y dy dx over x from 0 to 1, y from 0 to x", "1/8"),
        ("double integral of x + y over x from 0 to 1, y from 0 to 2", "3"),  # 2*1/2 + 1*2
        ("∬ x*y over 0 <= x <= 2, 0 <= y <= 3", "9"),  # (4/2) * (9/2)
        ("triple integral of x + y + z over x from 0 to 1, y from 0 to 1, z from 0 to 1", "3/2"),
        ("triple integral of 1 over x from 0 to 1, y from 0 to 1 - x, z from 0 to 1 - x - y", "1/6"),  # tetrahedron
        ("double integral of x^2 + y^2 in polar coordinates over r from 0 to 2, theta from 0 to 2*pi", "8*pi"),  # 2pi * 2^4/4
        ("triple integral of z in cylindrical coordinates over r from 0 to 1, theta from 0 to 2*pi, z from 0 to 1", "pi/2"),
        ("triple integral of 1 in spherical coordinates over rho from 0 to 1, phi from 0 to pi, theta from 0 to 2*pi", "4*pi/3"),
        ("triple integral of x^2 + y^2 + z^2 in spherical coordinates over rho from 0 to 1, phi from 0 to pi, theta from 0 to 2*pi", "4*pi/5"),
    ],
)
def test_iterated_integrals(problem: str, expected: str) -> None:
    sol = solve_text(problem)
    assert sol.answer_text == expected
    assert any("numerical" in n for n in sol.notes)


def test_integration_order_is_worked_out_from_the_limits() -> None:
    # y depends on x, so y is integrated first even when the limits are written the other way round
    a = answer("double integral of x*y over y from 0 to x, x from 0 to 1")
    assert a == "1/8"


def test_wrong_limits_are_refused() -> None:
    for bad in (
        "double integral of x*y over x from 0 to y, y from 0 to x",  # each limit uses the other variable
        "double integral of x*y dx dy over x from 0 to 1, y from 0 to x",  # dy must be inside: y's limits use x
        "double integral of x*y over x from 0 to 1",  # one pair of limits
        "double integral of x*y*z over x from 0 to 1, y from 0 to 1",  # z has no limits
    ):
        with pytest.raises(SolverError) as exc:
            solve_text(bad)
        assert exc.value.code in ("bad_bounds", "parse"), bad


# --- line integrals ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "problem, expected",
    [
        ("line integral of (-y, x) along (cos(t), sin(t)) for t from 0 to 2*pi", "2*pi"),  # sin^2 + cos^2 = 1
        ("work done by (y, x) along (t, t^2) for t from 0 to 1", "1"),  # F = grad(xy), ends (0,0) and (1,1)
        ("line integral of x^2 + y^2 along (2*t, 2*t) for t from 0 to 1", "16*sqrt(2)/3"),  # 8t^2 * 2sqrt2
        ("line integral of x*y along (t, t^2) for t from 0 to 1", "1/120 + 5*sqrt(5)/24"),
        ("line integral of 1 along (3*cos(t), 3*sin(t)) for t from 0 to 2*pi", "6*pi"),  # circumference
        ("line integral of (1, 2, 3) along (t, t, t) for t from 0 to 1", "6"),
        ("line integral of x + y along (t, 1 - t) with t in [0, 1]", "sqrt(2)"),  # 1 * |(1,-1)|
    ],
)
def test_line_integrals(problem: str, expected: str) -> None:
    assert answer(problem) == expected


def test_line_integral_checks_the_dimensions() -> None:
    with pytest.raises(SolverError) as exc:
        solve_text("line integral of (y, x, z) along (t, t) for t from 0 to 1")
    assert exc.value.code == "bad_vectors"


def test_the_multivariable_operation_explains_what_it_accepts() -> None:
    with pytest.raises(SolverError) as exc:
        solve_text("hello there", "multivariable")
    assert exc.value.code in ("no_intent", "unknown_word", "parse")


def test_existing_problems_still_work() -> None:
    assert answer("derivative of x^2*sin(x)") == "x*(x*cos(x) + 2*sin(x))"
    assert answer("integral of x*e^x from 0 to 1") == "1"


@pytest.mark.parametrize(
    "problem",
    [
        "partial derivative of x^2*y wrt x at (1, 2)",
        "gradient of x^2*y + z at (1,2,3)",
        "directional derivative of x*y at (1,2) in the direction (3,4)",
        "critical points of x^3 - 3*x*y + y^3",
        "maximize x*y subject to x + y = 10",
        "extrema of x^2 + 2*y^2 subject to x^2 + y^2 = 1",
        "double integral of x^2 + y^2 in polar coordinates over r from 0 to 2, theta from 0 to 2*pi",
        "triple integral of 1 in spherical coordinates over rho from 0 to 1, phi from 0 to pi, theta from 0 to 2*pi",
        "line integral of (-y, x) along (cos(t), sin(t)) for t from 0 to 2*pi",
    ],
)
def test_step_titles_are_plain_text(problem: str) -> None:
    for step in solve_text(problem).steps:
        assert "\\" not in step.title, step.title
