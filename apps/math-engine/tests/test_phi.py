"""The standard normal distribution function Phi(z) in answers."""

from allmaths_engine.checker import check_answer


def ok(student: str, correct: str) -> bool:
    return check_answer(answer_type="expression", student=student, correct=correct).status == "correct"


def test_equivalent_forms_of_a_normal_probability_are_accepted() -> None:
    assert ok("1-Phi(1)", "1 - Phi(1)")
    assert ok("Phi(-1)", "1 - Phi(1)")  # symmetry: Phi(-z) = 1 - Phi(z)
    assert ok("Phi(0)", "1/2")
    assert ok("Phi(1) - Phi(-1/4)", "Phi(1) + Phi(1/4) - 1")


def test_a_wrong_normal_probability_is_refused() -> None:
    assert not ok("Phi(1)", "1 - Phi(1)")
    assert not ok("Phi(2)", "Phi(1)")
