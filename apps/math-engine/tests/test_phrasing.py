"""The solver reads natural phrasing: "derive sin x", "please integrate x^2", "roots of x^2-4", a misspelled verb."""

import pytest
import sympy as sp

from allmaths_engine.solver import phrasing, solve_text
from allmaths_engine.solver.types import SolverError

x = sp.Symbol("x", real=True)


def answer_of(text: str) -> str:
    return solve_text(text).answer_text.replace(" ", "")


@pytest.mark.parametrize(
    ("said", "canonical"),
    [
        ("derive sin x", "derivative of sin x"),
        ("Derive sin x", "derivative of sin x"),
        ("differentiate x^3", "derivative of x^3"),
        ("find the derivative of x^3", "find the derivative of x^3"),  # already in the grammar: not touched
        ("please differentiate x^3 with respect to x", "derivative of x^3 with respect to x"),
        ("can you derive x^2*sin(x)", "derivative of x^2*sin(x)"),
        ("take the derivative of e^(2x)", "take the derivative of e^(2x)"),
        ("I want to integrate x^2 from 0 to 1", "integral of x^2 from 0 to 1"),
        ("antiderivative of cos x", "integral of cos x"),
        ("find the primitive of 1/x", "integral of 1/x"),
        ("roots of x^2-4", "solve x^2-4 = 0"),
        ("find the zeros of x^2-5x+6", "solve x^2-5x+6 = 0"),
        ("the solutions of x^2=9", "solve x^2=9"),
        ("grad of x^2*y", "gradient of x^2*y"),
        ("det of [[1,2],[3,4]]", "determinant of [[1,2],[3,4]]"),
        ("dervative of x^3", "derivative of x^3"),
        ("intergral of x", "integral of x"),
        ("simplfy x+x", "simplify x+x"),
        ("derivitive of x^2", "derivative of x^2"),
    ],
)
def test_the_sentence_is_rewritten_for_the_grammar(said, canonical):
    assert phrasing.normalize(said) == canonical


@pytest.mark.parametrize("sentence", ["solve x^2-4=0", "derivative of x^2", "factorial 5", "x^2+3x", "sin(x)^2+cos(x)^2", "(1,2,3)", "norm of (3, 4)", "expand (x+1)^2"])
def test_a_sentence_that_is_already_fine_is_left_alone(sentence):
    assert phrasing.normalize(sentence) == sentence


def test_the_mathematics_is_never_changed():
    assert phrasing.normalize("derive diff(x)") == "derivative of diff(x)"
    assert phrasing.normalize("det of [[det,2],[3,4]]").endswith("[[det,2],[3,4]]")


@pytest.mark.parametrize(
    ("said", "expected"),
    [
        ("derive sin x", sp.cos(x)),
        ("differentiate x^3", 3 * x**2),
        ("dervative of x^3", 3 * x**2),
        ("can you derive x^2*sin(x)", 2 * x * sp.sin(x) + x**2 * sp.cos(x)),
    ],
)
def test_derivatives_said_in_other_words_give_the_same_answer(said, expected):
    sol = solve_text(said)
    assert sol.operation == "derivative"
    assert sp.simplify(sp.sympify(sol.answer_text.replace("^", "**"), locals={"x": x}) - expected) == 0


def test_the_solver_says_how_it_read_the_problem():
    sol = solve_text("derive sin x")
    assert sol.notes[0] == "I read “derive sin x” as “derivative of sin x”."
    assert solve_text("derivative of sin x").notes == [] or not solve_text("derivative of sin x").notes[0].startswith("I read")


def test_integrals_and_equations_said_in_other_words():
    assert answer_of("integrate x^2 from 0 to 1") == "1/3"
    assert "sin(x)" in answer_of("antiderivative of cos x")
    assert "x**2" in answer_of("intergral of 2*x").replace("^", "**")
    roots = solve_text("roots of x^2-4").answer_text
    assert "-2" in roots and "2" in roots
    assert answer_of("det of [[1,2],[3,4]]") == "-2"


def test_an_unreadable_verb_gets_a_suggestion():
    with pytest.raises(SolverError) as e:
        solve_text("dervatv of x")
    assert e.value.code == "unknown_word"
    assert "Did you mean “derivative”" in e.value.message


def test_a_chosen_operation_is_never_rewritten():
    """With an operation picked in the list the text is taken as it is, as before."""
    sol = solve_text("x^3", "derivative")
    assert sol.operation == "derivative"
    assert not any(n.startswith("I read") for n in sol.notes)
