"""The triangle toolkit: exact results for a triangle given by its three vertices."""

import math

import pytest
import sympy as sp
from fastapi.testclient import TestClient
from sympy.parsing.sympy_parser import implicit_multiplication_application, parse_expr, standard_transformations

from allmaths_engine.main import app
from allmaths_engine.triangle import TriangleError, analyze, implicit_coefficients, parse_coordinate

x, y = sp.symbols("x y", real=True)
TRANSFORMS = standard_transformations + (implicit_multiplication_application,)
TOKEN = {"X-Engine-Token": "test-token-123456"}


def expr(latex: str) -> sp.Expr:
    """Reads back the LaTeX produced by the engine (fractions, radicals, implicit products) so that the tests can check the mathematics."""
    text = latex.replace(r"\left(", "(").replace(r"\right)", ")").replace(r"\,", " ")
    text = text.replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac").replace(r"\pi", "pi")

    def group(t: str, i: int) -> tuple[str, int]:
        """The text between the braces that open at t[i], and the position after the closing brace."""
        assert t[i] == "{", t[i:]
        depth, j = 0, i
        while True:
            depth += {"{": 1, "}": -1}.get(t[j], 0)
            j += 1
            if depth == 0:
                return t[i + 1 : j - 1], j

    def convert(t: str) -> str:
        out, i = "", 0
        while i < len(t):
            if t.startswith(r"\frac", i):
                num, j = group(t, i + 5)
                den, k = group(t, j)
                out += f"(({convert(num)})/({convert(den)}))"
                i = k
            elif t.startswith(r"\sqrt", i):
                inner, k = group(t, i + 5)
                out += f"sqrt({convert(inner)})"
                i = k
            else:
                out += {"{": "(", "}": ")"}.get(t[i], t[i])
                i += 1
        return out

    return parse_expr(convert(text), transformations=TRANSFORMS, local_dict={"x": x, "y": y})


def point(latex: str) -> tuple[sp.Expr, sp.Expr]:
    inner = latex.removeprefix(r"\left(").removesuffix(r"\right)")
    first, second = inner.split(r",\,")
    return expr(first), expr(second)


def lhs(latex: str) -> sp.Expr:
    left, right = latex.split("=")
    return expr(left) - expr(right)


_CACHE: dict[str, dict] = {}


def run(pts: list[list[str]]) -> dict:
    """The analysis of a triangle, computed once for the whole test module."""
    key = repr(pts)
    if key not in _CACHE:
        _CACHE[key] = analyze(pts)
    return _CACHE[key]


RIGHT = [["-2", "2"], ["-2", "-1"], ["2", "2"]]  # the 3-4-5 triangle
NOTES = [["-3", "2"], ["1", "5"], ["5", "-7"]]  # the triangle of the course notes
SCALENE = [["0", "0"], ["4", "1"], ["1", "3"]]  # three different radicals as sides
COURSE = [["0", "0"], ["14", "0"], ["5", "12"]]  # the running triangle of the lessons


def test_the_345_triangle_has_every_value_exact():
    r = run(RIGHT)
    assert [r["sides"][k]["length"] for k in "abc"] == ["5", "4", "3"]
    assert r["longest"] == ["BC"] and r["shortest"] == ["AB"]
    assert r["perimeter"] == "12" and r["area"] == "6" and r["semiperimeter"] == "6"
    assert r["kind"] == {"by_sides": "scalene", "by_angles": "right"}
    assert r["angles"]["A"]["degrees"] == "90^\\circ"
    assert r["angles"]["B"]["cos"] == r"\dfrac{3}{5}"
    assert point(r["centers"]["G"]) == (sp.Rational(-2, 3), 1)
    assert point(r["centers"]["I"]) == (-1, 1)
    assert point(r["centers"]["O"]) == (0, sp.Rational(1, 2))
    assert point(r["centers"]["H"]) == (-2, 2)  # the orthocenter of a right triangle is the vertex of the right angle
    assert r["radii"] == {"r": "1", "R": r"\dfrac{5}{2}"}
    assert r["circles"]["incircle"]["area"] == r"\pi"
    assert r["circles"]["circumcircle"]["perimeter"] == r"5 \pi"


def test_the_triangle_of_the_notes():
    r = run(NOTES)
    assert r["area"] == "30"
    assert point(r["centers"]["O"]) == (sp.Rational(5, 2), sp.Rational(-7, 6))
    assert r["radii"]["R"] == r"\dfrac{5 \sqrt{58}}{6}"
    assert r["sides"]["a"]["length"] == r"4 \sqrt{10}"


def test_decimals_are_read_as_exact_fractions():
    assert parse_coordinate("0.5") == sp.Rational(1, 2)
    assert parse_coordinate("-7/6") == sp.Rational(-7, 6)
    assert parse_coordinate(" 3 ") == 3
    assert run([["0", "0"], ["1/2", "0"], ["0", "0.25"]])["area"] == r"\dfrac{1}{16}"


@pytest.mark.parametrize("bad", ["1e3", "sqrt(2)", "pi", "1/0x", "", "--1", "7/"])
def test_a_coordinate_must_be_a_number(bad):
    with pytest.raises(TriangleError) as e:
        parse_coordinate(bad)
    assert e.value.code == "bad_coordinate"


def test_numbers_that_are_too_large_are_refused():
    with pytest.raises(TriangleError) as e:
        parse_coordinate("123456")
    assert e.value.code == "coordinate_range"
    with pytest.raises(TriangleError):
        parse_coordinate("1/1001")


def test_collinear_and_repeated_points_are_refused():
    with pytest.raises(TriangleError) as e:
        analyze([["0", "0"], ["1", "1"], ["3", "3"]])
    assert e.value.code == "collinear"
    with pytest.raises(TriangleError) as e:
        analyze([["0", "0"], ["1", "1"], ["0", "0"]])
    assert e.value.code == "same_points"
    with pytest.raises(TriangleError) as e:
        analyze([["0", "0"], ["1", "1"]])
    assert e.value.code == "three_points"


@pytest.mark.parametrize("pts", [RIGHT, NOTES, SCALENE, COURSE, [["0", "0"], ["2", "0"], ["1", "1.5"]]])
def test_the_classical_relations_hold(pts):
    """HG = 2 GO (the Euler line), OI^2 = R^2 - 2Rr (Euler's formula), checked on the drawing coordinates."""
    r = run(pts)
    fp = r["figure"]["points"]
    centroid, orthocenter, circumcenter, incenter = (sp.Matrix(fp[k]) for k in "GHOI")
    assert (orthocenter - centroid - 2 * (centroid - circumcenter)).norm() < 1e-4
    big_r = r["figure"]["circumcircle"]["r"]
    small_r = r["figure"]["incircle"]["r"]
    assert abs((circumcenter - incenter).norm() ** 2 - (big_r**2 - 2 * big_r * small_r)) < 1e-4


@pytest.mark.parametrize("pts", [RIGHT, NOTES, SCALENE])
def test_every_line_passes_through_its_two_points_in_every_form(pts):
    r = run(pts)
    assert len(r["lines"]) == 15  # 3 sides, 3 perpendicular bisectors, 3 medians, 3 altitudes, 3 bisectors
    for ln in r["lines"]:
        p, q = point(ln["from_point"]), point(ln["to_point"])
        for form in ("implicit", "explicit"):
            e = lhs(ln["forms"][form])
            for u in (p, q):
                assert abs(sp.N(e.subs({x: u[0], y: u[1]}), 30)) < 1e-12, (ln["id"], form)
        # the normal (Hesse) form: the coefficients of x and y have the sum of squares 1 and the constant term is not positive
        n = lhs(ln["forms"]["normal"])
        a, b, c = sp.diff(n, x), sp.diff(n, y), n.subs({x: 0, y: 0})
        assert abs(sp.N(a**2 + b**2 - 1, 30)) < 1e-12 and sp.N(c) <= 1e-12, ln["id"]
        assert abs(sp.N(n.subs({x: p[0], y: p[1]}), 30)) < 1e-12, ln["id"]


def test_lengths_of_the_lines():
    got = {ln["id"]: ln["length"] for ln in run(RIGHT)["lines"]}
    assert got["side-BC"] == "5"
    assert got["median-A"] == r"\dfrac{5}{2}"  # the median of the right angle is half of the hypotenuse
    assert got["altitude-B"] == "3" and got["altitude-C"] == "4"
    assert got["altitude-A"] == r"\dfrac{12}{5}"
    assert got["bisector-C"] == r"\dfrac{4 \sqrt{10}}{3}"
    assert got["perpbisector-CA"] == r"\dfrac{3}{2}"


def test_the_eight_forms_of_a_line_are_clean():
    lines = {ln["id"]: ln["forms"] for ln in run(RIGHT)["lines"]}
    vertical = lines["side-AB"]  # x = -2
    assert vertical["symmetric"] == "x=-2" and vertical["implicit"] == "x+2=0"
    assert vertical["intercept"] is None  # a line parallel to an axis has no intercept form
    side = lines["side-BC"]
    assert side["implicit"] == "3x-4y+2=0"
    assert side["explicit"] == r"y=\dfrac{3}{4}x+\dfrac{1}{2}"
    assert side["polar"] == r"r\left(3\cos\theta-4\sin\theta\right)+2=0"
    # no "0x", no "+-" and no decimal point in any result
    text = (repr(run(NOTES)["lines"]) + repr(run(NOTES)["circles"])).replace("[0.7em]", "")  # the row spacing of a column vector is layout, not a result
    assert "+-" not in text and "." not in text and " 0x" not in text and "+0y" not in text


def test_implicit_coefficients_are_whole_numbers_without_common_factor():
    a, b, c = implicit_coefficients((sp.Rational(1, 2), 0), (sp.Rational(1, 3), sp.Rational(2, 3)))
    assert (a, b, c) == (2, -1, -1)
    assert math.gcd(math.gcd(int(a), int(b)), int(c)) == 1


def test_an_isosceles_right_triangle():
    r = run([["0", "0"], ["4", "0"], ["0", "4"]])
    assert r["kind"] == {"by_sides": "isosceles", "by_angles": "right"}
    assert r["euler"] is not None


def test_the_circles_and_excircles():
    r = run(COURSE)
    assert r["circles"]["incircle"]["analytic"] == r"\left(x-6\right)^{2}+\left(y-4\right)^{2}=16"
    cc = r["circles"]["circumcircle"]
    assert point(cc["center"]) == (7, sp.Rational(33, 8)) and cc["radius"] == r"\dfrac{65}{8}"
    assert cc["parametric"].startswith(r"\begin{cases}x=7+\dfrac{65}{8}\cos t")
    assert set(r["excircles"]) == {"A", "B", "C"}


def test_the_endpoint_needs_the_token_and_answers_with_the_analysis():
    client = TestClient(app)
    body = {"points": RIGHT}
    assert client.post("/v1/geometry/triangle", json=body).status_code == 401
    ok = client.post("/v1/geometry/triangle", json=body, headers=TOKEN).json()
    assert ok["ok"] is True and ok["data"]["area"] == "6"
    bad = client.post("/v1/geometry/triangle", json={"points": [["0", "0"], ["1", "1"], ["2", "2"]]}, headers=TOKEN).json()
    assert bad["ok"] is False and bad["code"] == "collinear"
    assert client.post("/v1/geometry/triangle", json={"points": [["0", "0"]]}, headers=TOKEN).status_code == 422
