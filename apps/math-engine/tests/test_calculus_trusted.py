"""diff / integrate / limit exist for trusted content only and are refused in student answers."""

import pytest

from allmaths_engine.checker import check_answer, values_equal


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("diff(x^2*y, x)", "2*x*y"),
        ("diff(x^3, x, 2)", "6*x"),
        ("integrate(x^2, x, 0, 1)", "1/3"),
        ("integrate(integrate(x*y, y, 0, 1), x, 0, 2)", "1"),
        ("limit(sin(x)/x, x, 0)", "1"),
        ("limit((1+1/x)^x, x, oo)", "e"),
        ("integrate(1/(1+x^2), x, 0, oo)", "pi/2"),
    ],
)
def test_trusted_calculus(expr, expected):
    assert values_equal(expr, expected)[0]


@pytest.mark.parametrize("student", ["diff(x^2, x)", "integrate(x, x, 0, 1)", "limit(x, x, 0)"])
def test_students_cannot_call_calculus_functions(student):
    r = check_answer(answer_type="expression", student=student, correct="x", variables=["x"])
    assert r.status == "invalid" and r.code == "not_allowed"


def test_wrong_use_is_an_error_not_a_crash():
    r = values_equal("1", "1")
    assert r[0]
    with pytest.raises(Exception):  # noqa: B017 - any EngineError is acceptable here
        values_equal("diff(x^2, 3)", "2*x")
