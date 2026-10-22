import pytest

from allmaths_engine.errors import ParseError
from allmaths_engine.region import compile_region, regions_equal


def same(a: str, b: str, vs=("x", "y")) -> bool:
    v = list(vs)
    return regions_equal(compile_region(a, v), compile_region(b, v), v)[0]


@pytest.mark.parametrize(
    "a,b",
    [
        ("x^2+y^2<=4", "4-x^2-y^2>=0"),
        ("x^2+y^2<=4", "x**2+y**2 <= 4"),
        ("x^2+y^2<=4", "x^2 <= 4 - y^2"),
        ("x+y>0", "y>-x"),
        ("x^2<=1 and y^2<=1", "-1<=x<=1 and -1<=y<=1"),
        ("x^2<=1 and y^2<=1", "abs(x)<=1 and abs(y)<=1"),
        ("x^2>=4 and y^2<=4", "(x<=-2 or x>=2) and -2<=y<=2"),
        ("x^2+y^2>0", "x!=0 or y!=0"),
        ("true", "x^2+y^2>=0"),
        ("x=y", "y=x"),
        ("x>=0; y>=0", "x>=0 and y>=0"),
    ],
)
def test_equal_regions(a, b):
    assert same(a, b), (a, b)


@pytest.mark.parametrize(
    "a,b",
    [
        ("x^2+y^2<=4", "x^2+y^2<4"),  # strict vs non-strict differ on the circle
        ("x^2+y^2<=4", "x^2+y^2<=5"),
        ("x+y>0", "x+y>=0"),
        ("x^2<=1 and y^2<=1", "x^2<=1 or y^2<=1"),
        ("x^2+y^2>0", "x^2+y^2>=0"),
        ("x=y", "x<=y"),
        ("x>=0 and y>=0", "x>=0"),
    ],
)
def test_different_regions(a, b):
    assert not same(a, b), (a, b)


def test_three_variables():
    assert same("x*y*z>0", "x*y*z>0 and true", ("x", "y", "z"))
    assert same("x^2+y^2+z^2=4", "4=x^2+y^2+z^2", ("x", "y", "z"))
    assert not same("x^2+y^2+z^2<=4", "x^2+y^2+z^2<=1", ("x", "y", "z"))
    assert same("x>=0 and y>=0 and z>=0", "x>=0; y>=0; z>=0", ("x", "y", "z"))


def test_domain_with_logarithm_and_root():
    assert same("x+y>0", "ln(x+y)>-1000")  # ln is only defined where x+y>0
    assert same("1-x^2>=0 and 1-y^2>=0", "sqrt(1-x^2)>=0 and sqrt(1-y^2)>=0")


def test_latex_input():
    assert same(r"x^2+y^2\le 4", "x^2+y^2<=4")
    assert same(r"x^{2}\ge 4", "x^2>=4")
    assert same(r"x\neq y", "x!=y")


@pytest.mark.parametrize("bad", ["", "x+y", "x^2+y^2<=", "x<=1 and", "(x<=1", "z>0"])
def test_unusable_input(bad):
    with pytest.raises(ParseError):
        compile_region(bad, ["x", "y"])
