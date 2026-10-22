"""Spec section 7.5 answer key (vector and geometry rows). These are fixed, verified facts.

Each answer is *computed* by the engine from the problem data, then checked against the exact value
printed in the specification.
"""

import pytest

from allmaths_engine.checker import check_answer, compute, values_equal


def computed(expr: str) -> str:
    text, _ = compute(expr)
    return text


def assert_equal(expr: str, expected: str) -> None:
    ok, method = values_equal(expr, expected)
    assert ok, f"{expr} != {expected} ({method}); engine says {computed(expr)}"


U, V, W = "(2,-1,3)", "(1,4,-2)", "(0,1,1)"


def test_row1_dot_product():
    assert_equal(f"dot({U},{V})", "-8")


def test_row1_cross_product():
    assert_equal(f"cross({U},{V})", "(-10,7,9)")


def test_row1_box_product():
    assert_equal(f"box({U},{V},{W})", "16")


def test_row1_cosine_of_angle():
    assert_equal(f"cos_angle({U},{V})", "-4*sqrt(6)/21")


def test_row2_distance_between_skew_lines():
    # (D1): (1,0,-1)+t(1,2,-1) ; (D2): (0,1,2)+s(2,-1,1)
    expr = "abs(dot((0,1,2)-(1,0,-1), cross((1,2,-1),(2,-1,1)))) / norm(cross((1,2,-1),(2,-1,1)))"
    assert_equal(expr, "19*sqrt(35)/35")


def test_row3_tetrahedron_volume_area_height():
    ab, ac, ad = "((3,1,0)-(1,0,2))", "((0,2,1)-(1,0,2))", "((2,-1,3)-(1,0,2))"
    volume = f"abs(box({ab},{ac},{ad}))/6"
    area = f"norm(cross({ab},{ac}))/2"
    assert_equal(volume, "2/3")
    assert_equal(area, "5*sqrt(2)/2")
    assert_equal(f"3*({volume})/({area})", "2*sqrt(2)/5")


def test_row4_triangle_area_by_cross_product():
    # A(-1,0), B(5,0), C(2,4): area K = 12
    assert_equal("abs(cross((5,0)-(-1,0),(2,4)-(-1,0)))/2", "12")


def test_row5_distance_point_to_line():
    # P(3,-1,2); line (1,1,0)+t(2,-1,2)
    expr = "norm(cross((3,-1,2)-(1,1,0),(2,-1,2)))/norm((2,-1,2))"
    assert_equal(expr, "2*sqrt(2)/3")


def test_row7_max_of_linear_form_on_sphere():
    # Cauchy-Schwarz: max of <(1,2,2),(x,y,z)> on |(x,y,z)|=3 is |(1,2,2)|*3 = 9, at (1,2,2)
    assert_equal("norm((1,2,2))*3", "9")
    assert_equal("(3/norm((1,2,2)))*(1,2,2)", "(1,2,2)")


@pytest.mark.parametrize(
    "student",
    ["-4*sqrt(6)/21", "-4\\sqrt{6}/21", "-\\frac{4\\sqrt{6}}{21}", "-8/(7*sqrt(6))", "-(4/21)*sqrt(6)"],
)
def test_row1_cosine_accepts_equivalent_forms(student):
    r = check_answer(answer_type="number", student=student, correct="-4*sqrt(6)/21")
    assert r.status == "correct", r


def test_row1_results_as_vectors_checker():
    r = check_answer(answer_type="vector", student="(-10, 7, 9)", correct="cross((2,-1,3),(1,4,-2))")
    assert r.status == "correct"


def test_wrong_variants_of_the_key_are_rejected():
    # A mistake that is easy to make must not be accepted.
    assert check_answer(answer_type="number", student="19*sqrt(35)/34", correct="19*sqrt(35)/35").status == "incorrect"
    assert check_answer(answer_type="number", student="2/3", correct="1/3").status == "incorrect"
    assert check_answer(answer_type="vector", student="(10,7,9)", correct="(-10,7,9)").status == "incorrect"
