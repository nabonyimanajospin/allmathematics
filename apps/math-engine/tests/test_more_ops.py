"""Matrices, inequalities, tangent lines, series, partial fractions and areas. Expected values are worked out by hand in the comments."""

import pytest

from allmaths_engine.solver import solve_text
from allmaths_engine.solver.types import SolverError


def answer(text: str) -> str:
    return solve_text(text).answer_text


@pytest.mark.parametrize(
    "problem, expected",
    [
        ("determinant of [[1,2],[3,4]]", "-2"),  # 1*4 - 2*3
        ("det [[2,1,0],[1,3,1],[0,1,4]]", "18"),  # 2*(12-1) - 1*(4-0) + 0
        ("inverse of [[2,1],[5,3]]", "[[3, -1], [-5, 2]]"),  # det 1
        ("inverse of [[1,2],[2,4]]", "no inverse (the determinant is 0)"),
        ("transpose of [[1,2,3],[4,5,6]]", "[[1, 4], [2, 5], [3, 6]]"),
        ("trace of [[1,2],[3,4]]", "5"),
        ("rank of [[1,2,3],[2,4,6],[1,0,1]]", "2"),  # row 2 = 2 * row 1
        ("[[1,2],[3,4]] * [[0,1],[1,0]]", "[[2, 1], [4, 3]]"),  # swaps the columns
        ("multiply [[1,0],[0,2]] by [[3],[4]]", "[[3], [8]]"),
        ("[[1,2],[3,4]] + [[1,1],[1,1]]", "[[2, 3], [4, 5]]"),
        ("[[1,2],[3,4]] - [[1,1],[1,1]]", "[[0, 1], [2, 3]]"),
        ("[[1,1],[0,1]]^5", "[[1, 5], [0, 1]]"),
        ("[[2,0],[0,2]]^-1", "[[1/2, 0], [0, 1/2]]"),
        ("3*[[1,2],[3,4]]", "[[3, 6], [9, 12]]"),
        ("eigenvalues of [[2,1],[1,2]]", "λ = 1; λ = 3"),  # trace 4, det 3
        ("eigenvalues and eigenvectors of [[4,1],[2,3]]", "λ = 2: [-1, 2]; λ = 5: [1, 1]"),  # trace 7, det 10
    ],
)
def test_matrices(problem: str, expected: str) -> None:
    assert answer(problem) == expected


def test_row_reduction_shows_each_operation() -> None:
    sol = solve_text("row reduce [[1,2,3],[4,5,6],[7,8,10]]")  # determinant -3, so it reduces to the identity
    assert sol.answer_text == "[[1, 0, 0], [0, 1, 0], [0, 0, 1]], rank 3"
    assert len(sol.steps) >= 6


def test_a_repeated_eigenvalue_without_enough_eigenvectors_is_noted() -> None:
    sol = solve_text("eigenvectors of [[1,1],[0,1]]")
    assert any("not diagonalizable" in n for n in sol.notes)


@pytest.mark.parametrize(
    "problem, code",
    [
        ("determinant of [[1,2,3],[4,5,6]]", "bad_matrix"),
        ("[[1,2],[3,4]] * [[1,2,3]]", "bad_matrix"),
        ("[[1,2],[3,4]] + [[1,2,3],[4,5,6]]", "bad_matrix"),
        ("determinant of [[1,2],[3]]", "bad_matrix"),
        ("[[1,2],[3,4]]", "no_intent"),
    ],
)
def test_matrix_mistakes_are_explained(problem: str, code: str) -> None:
    with pytest.raises(SolverError) as exc:
        solve_text(problem)
    assert exc.value.code == code


@pytest.mark.parametrize(
    "problem, expected",
    [
        ("solve x^2 - 4 > 0", "(-oo, -2) U (2, oo)"),
        ("solve x^2 - 4 >= 0", "(-oo, -2] U [2, oo)"),
        ("x^2 - 4 < 0", "(-2, 2)"),
        ("solve (x-1)/(x+2) > 0", "(-oo, -2) U (1, oo)"),  # the denominator is never allowed to be 0
        ("solve x^2 + 1 < 0", "no real solution"),
        ("solve x^2 >= 0", "all real numbers"),
        ("solve 2x - 3 <= 5", "(-oo, 4]"),
        ("solve (x-1)*(x-3) <= 0", "[1, 3]"),
    ],
)
def test_inequalities(problem: str, expected: str) -> None:
    assert answer(problem) == expected


@pytest.mark.parametrize(
    "problem, expected",
    [
        ("tangent line to y = x^3 at x = 2", "y = 12*x - 16"),  # f(2) = 8, f'(2) = 12
        ("tangent line to x^2 at x = 1", "y = 2*x - 1"),
        ("normal line to y = x^2 at x = 1", "y = 3/2 - x/2"),  # slope -1/2 through (1, 1)
        ("tangent plane to z = x^2 + y^2 at (1, 2)", "z = 2*x + 4*y - 5"),  # f = 5, f_x = 2, f_y = 4
        ("tangent plane to z = x*y at x = 2, y = 3", "z = 3*x + 2*y - 6"),  # f = 6, f_x = 3, f_y = 2
    ],
)
def test_tangents(problem: str, expected: str) -> None:
    assert answer(problem) == expected


def test_tangent_where_the_function_is_not_defined() -> None:
    with pytest.raises(SolverError) as exc:
        solve_text("tangent line to y = 1/x at x = 0")
    assert exc.value.code == "undefined"


@pytest.mark.parametrize(
    "problem, expected",
    [
        ("taylor series of sin(x) at 0 order 5", "x^5/120 - x^3/6 + x"),
        ("maclaurin series of e^x up to order 4", "x^4/24 + x^3/6 + x^2/2 + x + 1"),
        ("taylor series of ln(x) at 1 order 3", "x^3/3 - 3*x^2/2 + 3*x - 11/6"),  # (x-1) - (x-1)^2/2 + (x-1)^3/3
        ("maclaurin series of cos(x) order 4", "x^4/24 - x^2/2 + 1"),
    ],
)
def test_taylor(problem: str, expected: str) -> None:
    assert answer(problem) == expected


@pytest.mark.parametrize(
    "problem, expected",
    [
        ("sum of k^2 for k from 1 to 10", "385"),  # 10*11*21/6
        ("sum of k for k from 1 to n", "n*(n + 1)/2"),
        ("sum of 1/n^2 for n from 1 to infinity", "pi^2/6"),
        ("sum of (1/2)^k for k from 0 to infinity", "2"),
        ("sum of 1/k for k from 1 to infinity", "diverges"),
        ("sum of 2*k + 1 for k from 0 to 9", "100"),  # the first ten odd numbers
    ],
)
def test_sums(problem: str, expected: str) -> None:
    assert answer(problem) == expected


def test_partial_fractions() -> None:
    a = answer("partial fractions of (3x+5)/((x-1)(x+2))")  # 8/3 at x=1, 1/3 at x=-2
    assert "8/(3*(x - 1))" in a and "1/(3*(x + 2))" in a
    assert "1/(2*(x - 1))" in answer("partial fractions of 1/(x^2-1)")


@pytest.mark.parametrize(
    "problem, expected",
    [
        ("area between y = x and y = x^2", "1/6 squ"),
        ("area under y = x^2 from 0 to 3", "9 squ"),
        ("area between y = sin(x) and y = 0 from 0 to 2*pi", "4 squ"),  # |sin| over a full period
        ("area between y = x^2 and y = 2 - x^2", "8/3 squ"),  # meet at x = ±1: int (2 - 2x^2) = 8/3
    ],
)
def test_areas(problem: str, expected: str) -> None:
    assert answer(problem) == expected


def test_other_phrasings_and_old_problems_still_work() -> None:
    assert answer("limit as x approaches infinity of (1+1/x)^x") == "e"
    assert answer("lim x->0 sin(3x)/x") == "3"
    assert answer("|(3,4)|") == "5"
    assert answer("derivative of x^2*sin(x)") == "x*(x*cos(x) + 2*sin(x))"
    assert answer("solve x^2 - 5x + 6 = 0") == "x=2, x=3"


def test_the_other_operation_explains_what_it_accepts() -> None:
    with pytest.raises(SolverError) as exc:
        solve_text("hello there", "other")
    assert exc.value.code in ("no_intent", "unknown_word", "parse")


@pytest.mark.parametrize(
    "problem",
    [
        "determinant of [[2,1,0],[1,3,1],[0,1,4]]",
        "inverse of [[2,1],[5,3]]",
        "eigenvalues and eigenvectors of [[4,1],[2,3]]",
        "row reduce [[1,2,3],[4,5,6],[7,8,10]]",
        "solve (x-1)/(x+2) > 0",
        "tangent line to y = x^3 at x = 2",
        "tangent plane to z = x^2 + y^2 at (1, 2)",
        "taylor series of ln(x) at 1 order 3",
        "sum of 1/n^2 for n from 1 to infinity",
        "partial fractions of (3x+5)/((x-1)(x+2))",
        "area between y = x and y = x^2",
    ],
)
def test_step_titles_are_plain_text(problem: str) -> None:
    for step in solve_text(problem).steps:
        assert "\\" not in step.title, step.title
