"""The parser must never execute input and must bound the work it does."""

import pytest

from allmaths_engine.checker import check_answer
from allmaths_engine.errors import ComplexityError, ParseError
from allmaths_engine.parser import parse


@pytest.mark.parametrize(
    "evil",
    [
        "__import__('os').system('echo hacked')",
        "open('/etc/passwd')",
        "().__class__.__mro__",
        "x.__class__",
        "lambda: 1",
        "[c for c in ().__class__.__bases__]",
        "exec('1')",
        "1; import os",
    ],
)
def test_code_injection_is_rejected_not_executed(evil):
    r = check_answer(answer_type="expression", student=evil, correct="x", variables=["x"])
    assert r.status == "invalid"


@pytest.mark.parametrize("big", ["9^9^9^9", "2^(2^(2^20))", "10^100000", "(((((((((2)))))))))^99999"])
def test_huge_powers_are_refused_quickly(big):
    with pytest.raises((ComplexityError, ParseError)):
        parse(big)


def test_deep_nesting_is_refused():
    with pytest.raises((ComplexityError, ParseError)):
        parse("(" * 200 + "1" + ")" * 200)


def test_long_input_is_refused():
    with pytest.raises(ComplexityError):
        parse("1+" * 400 + "1")


def test_division_by_zero_is_a_parse_error():
    with pytest.raises(ParseError):
        parse("1/0")
    with pytest.raises(ParseError):
        parse("1/(2-2)")


def test_vector_misuse_is_refused():
    with pytest.raises(ParseError):
        parse("(1,2,3)*(4,5,6)")
    with pytest.raises(ParseError):
        parse("(1,2,3)+(1,2)")
    with pytest.raises(ParseError):
        parse("(1,2,3)^2")


def test_function_without_parentheses_is_never_silently_misread():
    with pytest.raises(ParseError):
        parse("sin 2x")


def test_precedence_and_unary_minus():
    assert str(parse("-2^2").value) == "-4"
    assert str(parse("2^-1").value) == "1/2"
    assert str(parse("2^3^2").value) == "512"
    assert str(parse("1/2x", variables={"x"}).value) == "x/2"


def test_latex_unsupported_commands_are_errors():
    with pytest.raises(ParseError):
        parse("\\foo{1}")
    with pytest.raises(ParseError):
        parse("\\frac{1}{")
