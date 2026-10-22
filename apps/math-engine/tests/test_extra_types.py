"""New answer types, tested with problems taken from the MATH126 exercise sheet."""

import pytest

from allmaths_engine.checker import Constraint, Mistake, check_answer
from allmaths_engine.ode import Condition, OdeSpec


def chk(answer_type, student, correct, **kw):
    return check_answer(answer_type=answer_type, student=student, correct=correct, **kw)


# --- regions (domains and discontinuity sets) -----------------------------------------------------------
@pytest.mark.parametrize(
    "student",
    ["x^2+y^2<=4", "4-x^2-y^2>=0", "x**2 + y**2 <= 4", "x^2<=4-y^2"],
)
def test_domain_of_sqrt(student):
    assert chk("region", student, "x^2+y^2<=4", coordinates=["x", "y"]).status == "correct"


def test_domain_boundary_hint():
    r = chk("region", "x^2+y^2<4", "x^2+y^2<=4", coordinates=["x", "y"])
    assert r.status == "incorrect" and r.code == "boundary"


def test_domain_wrong_and_invalid():
    assert chk("region", "x^2+y^2<=9", "x^2+y^2<=4", coordinates=["x", "y"]).code == "wrong"
    assert chk("region", "x^2+y^2", "x^2+y^2<=4", coordinates=["x", "y"]).status == "invalid"
    assert chk("region", "x^2+y^2<=4+t", "x^2+y^2<=4", coordinates=["x", "y"]).code == "unknown_name"


def test_domain_square_and_logic():
    assert chk("region", "-1<=x<=1 and -1<=y<=1", "x^2<=1 and y^2<=1", coordinates=["x", "y"]).status == "correct"
    assert chk("region", "|x|<=1 and |y|<=1", "x^2<=1 and y^2<=1", coordinates=["x", "y"]).status == "correct"


def test_domain_3d():
    assert chk("region", "x*y*z>0", "x*y*z>0", coordinates=["x", "y", "z"]).status == "correct"
    assert chk("region", "x^2+y^2+z^2=4", "x^2+y^2+z^2=4", coordinates=["x", "y", "z"]).status == "correct"


def test_region_known_mistake():
    r = chk("region", "x+y>=0", "x+y>0", coordinates=["x", "y"], mistakes=[Mistake("x+y>=0", "ln needs a positive argument")])
    assert r.code == "known_mistake" and "positive" in r.hint


def test_region_decimal_refused():
    assert chk("region", "x^2+y^2<=4.0", "x^2+y^2<=4", coordinates=["x", "y"]).code == "decimal_not_allowed"


# --- limits that do not exist, integrals that diverge ----------------------------------------------------
@pytest.mark.parametrize("s", ["DNE", "does not exist", "The limit does not exist", "d.n.e.", "diverges"])
def test_nonexistent_keyword(s):
    assert chk("number", s, "@dne").status == "correct"


def test_nonexistent_wrong_answers():
    assert chk("number", "0", "@dne").status == "incorrect"
    assert chk("number", "", "@dne").status == "invalid"
    assert chk("number", "DNE", "0").status == "invalid"  # a number key never accepts words


# --- equations up to a constant factor -------------------------------------------------------------------
def test_tangent_plane_equivalent_forms():
    key = "x + 2*y - z = 0"
    for s in ["z = x + 2y", "x+2y-z=0", "2z = 2x + 4y", "-x-2y+z=0", "x + 2y = z"]:
        assert chk("equation", s, key, coordinates=["x", "y", "z"]).status == "correct", s


def test_tangent_plane_wrong():
    key = "x + 2*y - z = 0"
    assert chk("equation", "z = x + y", key, coordinates=["x", "y", "z"]).code == "wrong"
    assert chk("equation", "x + 2y - z = 1", key, coordinates=["x", "y", "z"]).code == "wrong"


def test_equation_needs_equals_sign():
    assert chk("equation", "x+2y-z", "x+2*y-z=0", coordinates=["x", "y", "z"]).code == "not_an_equation"


def test_tangent_plane_to_ellipsoid_with_parameters():
    key = "x*x0/a^2 + y*y0/b^2 + z*z0/c^2 = 1"
    r = chk("equation", "(x0 x)/a^2 + (y0 y)/b^2 + (z0 z)/c^2 = 1", key, coordinates=["x", "y", "z"])
    assert r.status == "correct"
    r = chk("equation", "x0 x/a^2 + y0 y/b^2 - z0 z/c^2 = 1", key, coordinates=["x", "y", "z"])
    assert r.status == "incorrect"


def test_circle_equation():
    assert chk("equation", "(x-2)^2+(y-3/2)^2=9/4", "x^2-4*x+y^2-3*y+4 = 0", coordinates=["x", "y"]).status == "correct"


def test_equation_latex():
    r = chk("equation", r"z=x+2y", "x+2*y-z=0", coordinates=["x", "y", "z"])
    assert r.status == "correct"


# --- directions ------------------------------------------------------------------------------------------
def test_normal_direction_any_multiple():
    for s in ["(6, 8, -1)", "(12,16,-2)", "(-6,-8,1)", "(3, 4, -1/2)"]:
        assert chk("direction", s, "(6,8,-1)").status == "correct", s
    assert chk("direction", "(6,8,1)", "(6,8,-1)").status == "incorrect"
    assert chk("direction", "(0,0,0)", "(6,8,-1)").status == "incorrect"
    assert chk("direction", "(1,2)", "(6,8,-1)").code == "wrong_dimension"


# --- sets of points --------------------------------------------------------------------------------------
def test_point_sets_unordered():
    key = "(0,0), (-1,-1)"
    for s in ["(-1,-1), (0,0)", "{(0,0); (-1,-1)}", "(0, 0) and (-1, -1)", "(0,0),(-2/2,-1)"]:
        assert chk("points", s, key).status == "correct", s


def test_point_sets_wrong():
    key = "(0,0), (-1,-1)"
    r = chk("points", "(0,0)", key)
    assert r.status == "incorrect" and r.code == "missing"
    r = chk("points", "(0,0), (1,1)", key)
    assert r.status == "incorrect" and r.code == "wrong"
    assert chk("points", "(0,0), (0,0)", key).status == "incorrect"


def test_no_points():
    assert chk("points", "none", "none").status == "correct"
    assert chk("points", "(0,0)", "none").status == "incorrect"


# --- expressions on a curve ------------------------------------------------------------------------------
def test_implicit_derivative_on_circle():
    c = Constraint("x^2+y^2-1", "y", {"x": (0.1, 0.8)})
    assert chk("expression", "-x/y", "-x/y", variables=["x", "y"], constraint=c).status == "correct"
    assert chk("expression", "-x/sqrt(1-x^2)", "-x/y", variables=["x", "y"], constraint=c).status == "correct"
    assert chk("expression", "-y/x", "-x/y", variables=["x", "y"], constraint=c).status == "incorrect"


def test_implicit_vector_answer_on_curve():
    c = Constraint("x^2/4+y^2/9-1", "y", {"x": (0.2, 1.5)})
    key = "(-9*x/(4*y), -81/(16*y^3))"
    r = chk("vector", "(-9x/(4y), -81/(16 y^3))", key, variables=["x", "y"], constraint=c)
    assert r.status == "correct"


# --- differential equations: solutions -------------------------------------------------------------------
def spec(order, equation, conditions=None, sample=(0.6, 1.9)):
    return OdeSpec(order=order, equation=equation, conditions=conditions or [], sample=sample)


def ode_sol(student, s, **kw):
    return chk("ode_solution", student, "unused", ode=s, **kw)


def test_separable_explicit_and_implicit():
    # x y y' = 1 - x^3 ... solution: y^2/2 = ln|x| - x^3/3 + C   (equation: x*y*y1 - (1 - x^3) = 0)
    s = spec(1, "x*y*y1 - (1 - x^3)")
    assert ode_sol("y^2/2 = ln|x| - x^3/3 + C", s).status == "correct"
    assert ode_sol("y^2 = 2 ln(x) - 2x^3/3 + C", s).status == "correct"
    assert ode_sol("3 y^2 - 6 ln(x) + 2 x^3 = C", s).status == "correct"
    assert ode_sol("y = sqrt(2 ln(x) - 2x^3/3 + C)", s).status == "correct"
    assert ode_sol("y^2/2 = ln|x| - x^3/3", s).code == "no_constant"
    assert ode_sol("y^2/2 = ln|x| + x^3/3 + C", s).code == "not_a_solution"


def test_linear_first_order():
    s = spec(1, "y1 - 2*y/(x+1) - (x+1)^3")
    assert ode_sol("y = (x+1)^2 ((x+1)^2/2 + C)", s).status == "correct"
    assert ode_sol("y = (x+1)^4/2 + C (x+1)^2", s).status == "correct"
    assert ode_sol("y = (x+1)^4/2", s).code == "no_constant"


def test_second_order_general_solution():
    s = spec(2, "y2 - 5*y1 + 6*y")
    assert ode_sol("y = C1 e^{2x} + C2 e^{3x}", s).status == "correct"
    assert ode_sol("y = A e^(2x) + B e^(3x)", s).status == "correct"
    assert ode_sol("y = C1 e^(2x)", s).code == "no_constant" or ode_sol("y = C1 e^(2x)", s).code == "not_general"
    assert ode_sol("y = C1 e^(2x) + C2 e^(2x)", s).code in {"dependent_constants", "not_a_solution", "not_general"}
    assert ode_sol("y = C1 e^(2x) + C2 e^(4x)", s).code == "not_a_solution"


def test_second_order_resonance():
    # y'' + 4y = sin 2x  ->  y = C1 cos 2x + C2 sin 2x - x cos(2x)/4
    s = spec(2, "y2 + 4*y - sin(2*x)")
    assert ode_sol("y = C1 cos(2x) + C2 sin(2x) - (x/4) cos(2x)", s).status == "correct"
    assert ode_sol("y = C1 cos(2x) + C2 sin(2x) + (x/4) cos(2x)", s).status == "incorrect"


def test_initial_value_problem():
    # y' - y/(1-x^2) - 1 - x = 0 ... use a simpler, verifiable IVP: (1+e^x) y y' = e^x, y(0)=1
    s = spec(1, "(1+e^x)*y*y1 - e^x", [Condition("0", "1")])
    assert ode_sol("y^2 = 2 ln(1+e^x) - 2 ln(2) + 1", s).status == "correct"
    assert ode_sol("y = sqrt(2 ln((1+e^x)/2) + 1)", s).status == "correct"
    assert ode_sol("y^2 = 2 ln(1+e^x) + C", s).code == "constant_left"
    assert ode_sol("y^2 = 2 ln(1+e^x)", s).code == "condition_not_met"


def test_second_order_ivp_with_derivative_condition():
    s = spec(2, "y2 - 5*y1 + 4*y", [Condition("0", "5"), Condition("0", "8", 1)])
    assert ode_sol("y = 4 e^x + e^(4x)", s).status == "correct"
    assert ode_sol("y = 3 e^x + 2 e^(4x)", s).code == "condition_not_met"


def test_boundary_value_problem_with_only_trivial_solution():
    s = spec(2, "y2 + 3*y", [Condition("0", "0"), Condition("3", "0")], sample=(0.3, 2.5))
    assert ode_sol("y = 0", s).status == "correct"
    assert ode_sol("y = sin(sqrt(3) x)", s).code == "condition_not_met"


def test_solution_input_errors():
    s = spec(1, "y1 - y")
    assert ode_sol("e^x C", s).code == "not_an_equation"
    assert ode_sol("y' = C e^x", s).code == "derivative_in_solution"
    assert ode_sol("y = C e^x +", s).status == "invalid"


# --- differential equations: forming the equation --------------------------------------------------------
def fam(order, family, constants, sample=(0.6, 1.9)):
    return OdeSpec(order=order, family=family, constants=constants, sample=sample)


def ode_fam(student, f, **kw):
    return chk("ode_family", student, "unused", ode=f, **kw)


def test_form_equation_first_order():
    f = fam(1, "y = c*x^2 - x", ["c"])
    for s in ["x y' - 2y = x", "x y' = 2y + x", "y' = (2y + x)/x", "2y - x y' + x = 0", "y' x - 2 y - x = 0"]:
        assert ode_fam(s, f).status == "correct", s
    assert ode_fam("y' = 2y", f).code == "family_not_solution"


def test_form_equation_rejects_constants_and_wrong_order():
    f = fam(1, "y = c*x^2 - x", ["c"])
    assert ode_fam("y' = 2 c x - 1", f).code == "constants_left"
    assert ode_fam("y'' = 2 c", f).code in {"constants_left", "order_too_high"}
    g = fam(2, "y = c1*x^3 + c2*x", ["c1", "c2"])
    assert ode_fam("x^2 y'' - 3 x y' + 3 y = 0", g).status == "correct"
    assert ode_fam("x y' - y = 0", g).code in {"order_too_low", "family_not_solution"}


def test_form_equation_third_order_and_implicit_family():
    f = fam(3, "y = c1*e^x + c2*x*e^x + c3*e^(-x)", ["c1", "c2", "c3"])
    assert ode_fam("y''' - y'' - y' + y = 0", f).status == "correct"
    h = fam(1, "x^2 + y^2 = c^2", ["c"])
    assert ode_fam("x + y y' = 0", h).status == "correct"
    assert ode_fam("y' = -x/y", h).status == "correct"
    assert ode_fam("y' = x/y", h).code == "family_not_solution"


def test_form_equation_leibniz_notation():
    f = fam(1, "y = c*x^2 - x", ["c"])
    assert ode_fam("x dy/dx - 2y = x", f).status == "correct"
    assert ode_fam(r"x\frac{dy}{dx} - 2y = x", f).status == "correct"
    assert ode_fam(r"x y^{\prime} - 2y = x", f).status == "correct"


def test_ode_types_need_specification():
    assert chk("ode_solution", "y = C e^x", "unused").code == "bad_spec"


def test_second_derivative_may_use_y_prime():
    # x^2 + y^2 = 25:  y' = -x/y   and   y'' = -(x^2+y^2)/y^3 = -25/y^3
    c = Constraint("x^2+y^2-25", "y", {"x": (0.5, 3.0)}, {"y1": "-x/y"})
    key = "(-x/y, -25/y^3)"
    for s in ["(-x/y, -25/y^3)", "(-x/y, -(y - x y')/y^2)", "(-x/y, (-y - x*(-x/y))/y^2)", "(-x/y, -(x^2+y^2)/y^3)"]:
        r = chk("vector", s, key, variables=["x", "y", "y1"], constraint=c)
        assert r.status == "correct", s
    assert chk("vector", "(-x/y, -1/y^3)", key, variables=["x", "y", "y1"], constraint=c).status == "incorrect"
