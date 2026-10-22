import pytest

from allmaths_engine.checker import Mistake, check_answer


def chk(student, correct, answer_type="number", **kw):
    return check_answer(answer_type=answer_type, student=student, correct=correct, **kw)


# --- numbers ---------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "student", ["sqrt(2)", "2/sqrt(2)", "\\frac{2}{\\sqrt{2}}", "sqrt(8)/2", "\\sqrt{2}", "2^(1/2)"]
)
def test_equivalent_exact_forms_are_correct(student):
    assert chk(student, "sqrt(2)").status == "correct"


@pytest.mark.parametrize("student", ["7/2", "14/4", "\\frac{7}{2}", "\\dfrac{7}{2}", "3+1/2", "35/10"])
def test_fractions_equivalent(student):
    assert chk(student, "7/2").status == "correct"


def test_pi_multiples():
    assert chk("\\frac{\\pi}{3}", "pi/3").status == "correct"
    assert chk("2pi/6", "pi/3").status == "correct"
    assert chk("π/3", "pi/3").status == "correct"


def test_wrong_number_is_incorrect_not_invalid():
    r = chk("3", "7/2")
    assert r.status == "incorrect" and r.code == "wrong"


def test_sign_error_gets_specific_hint():
    r = chk("-7/2", "7/2")
    assert r.status == "incorrect" and r.code == "sign_error" and "sign" in r.hint.lower()


def test_decimal_is_refused_with_friendly_message():
    r = chk("3.5", "7/2")
    assert r.status == "invalid" and r.code == "decimal_not_allowed"
    assert "exact" in r.message.lower()


def test_decimal_refused_even_inside_expression():
    assert chk("1.5+2", "7/2").status == "invalid"


def test_decimal_allowed_for_approximation_questions():
    assert chk("3.21", "19*sqrt(35)/35", allow_decimal=True, sig_figs=3).status == "correct"
    assert chk("3.22", "19*sqrt(35)/35", allow_decimal=True, sig_figs=3).status == "incorrect"


def test_exact_still_accepted_when_decimals_allowed():
    assert chk("19*sqrt(35)/35", "19*sqrt(35)/35", allow_decimal=True, sig_figs=3).status == "correct"


def test_number_question_rejects_symbols():
    r = chk("x+1", "3", variables=["x"])
    assert r.status == "invalid" and r.code == "expected_number"


def test_vector_given_for_number_is_invalid():
    assert chk("(1,2)", "3").code == "expected_scalar"


def test_unknown_name_is_invalid():
    r = chk("2*y", "2*x", answer_type="expression")
    assert r.status == "invalid" and r.code == "unknown_name"


def test_known_mistake_hint():
    r = chk("-19/sqrt(35)", "19/sqrt(35)", mistakes=[Mistake("-19/sqrt(35)", "A distance is never negative.")])
    assert r.status == "incorrect" and r.code == "known_mistake" and "never negative" in r.hint


@pytest.mark.parametrize("s", ["", "   ", "2+", "((1)", "1 2", "@@", "sin 2x"])
def test_empty_and_garbage_are_invalid(s):
    r = chk(s, "2")
    assert r.status == "invalid", (s, r)


# --- expressions -----------------------------------------------------------------------------------
@pytest.mark.parametrize("student", ["2x+2", "2(x+1)", "x+1+x+1", "\\left(x+1\\right)\\cdot2", "2*x+2*1"])
def test_expression_equivalence(student):
    assert chk(student, "2*x+2", answer_type="expression").status == "correct"


def test_expression_trig_identity():
    assert chk("1-sin(x)^2", "cos(x)^2", answer_type="expression").status == "correct"


def test_expression_not_equivalent():
    assert chk("2x+3", "2*x+2", answer_type="expression").status == "incorrect"


def test_expression_sqrt_of_square_is_not_x():
    assert chk("sqrt(x^2)", "x", answer_type="expression").status == "incorrect"


def test_expression_exponential_forms():
    assert chk("e^{2x}", "exp(2*x)", answer_type="expression").status == "correct"


def test_expression_difference_of_squares():
    assert chk("(x-1)(x+1)", "x^2-1", answer_type="expression").status == "correct"


def test_expression_near_miss_is_wrong():
    assert chk("x^2-1+0.0000001", "x^2-1", answer_type="expression").status == "invalid"  # decimal
    assert chk("x^2-1+1/10000000", "x^2-1", answer_type="expression").status == "incorrect"


# --- vectors ---------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "student",
    [
        "(-10,7,9)",
        "(-10, 7, 9)",
        "\\left(-10,7,9\\right)",
        "\\begin{pmatrix}-10\\\\7\\\\9\\end{pmatrix}",
        "-10i+7j+9k",
        "-10\\vec{i}+7\\vec{j}+9\\vec{k}",
        "\\langle -10, 7, 9\\rangle",
        "(-20/2, 7, 18/2)",
    ],
)
def test_vector_forms(student):
    assert chk(student, "(-10,7,9)", answer_type="vector").status == "correct", student


def test_vector_partial_credit_parts():
    r = chk("(-10,7,8)", "(-10,7,9)", answer_type="vector")
    assert r.status == "incorrect" and r.parts == [True, True, False]


def test_vector_wrong_dimension_invalid():
    assert chk("(1,2)", "(1,2,3)", answer_type="vector").code == "wrong_dimension"


def test_vector_scalar_given_invalid():
    assert chk("5", "(1,2,3)", answer_type="vector").code == "expected_vector"


def test_vector_sign_error():
    assert chk("(10,-7,-9)", "(-10,7,9)", answer_type="vector").code == "sign_error"


def test_vector_decimal_refused():
    assert chk("(-10.0,7,9)", "(-10,7,9)", answer_type="vector").code == "decimal_not_allowed"


def test_point_is_vector():
    assert chk("(1, 2)", "(1,2)", answer_type="point").status == "correct"


def test_vector_with_radicals():
    assert chk("(1/sqrt(2), 1/sqrt(2))", "(sqrt(2)/2, sqrt(2)/2)", answer_type="vector").status == "correct"


def test_vector_with_parameter():
    assert chk("(1+t, 2t)", "(t+1, 2*t)", answer_type="vector", variables=["t"]).status == "correct"


# --- choices ---------------------------------------------------------------------------------------
def test_multiple_choice():
    assert chk("2", "2", answer_type="multiple_choice").status == "correct"
    assert chk("1", "2", answer_type="multiple_choice").status == "incorrect"
    assert chk("two", "2", answer_type="multiple_choice").status == "invalid"


# --- key validation --------------------------------------------------------------------------------
def test_key_with_decimal_is_rejected():
    r = chk("2", "2.5")
    assert r.status == "invalid" and r.code == "decimal_in_key"


def test_key_type_mismatch():
    assert chk("1", "(1,2)", answer_type="number").code == "key_type_mismatch"
