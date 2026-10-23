"""Exercises of the lessons added to Course 2 after the first release (gradient, linear approximation, space curves,
the double integral as a limit of sums, absolute extrema). Original exercises, not taken from the printed sheet."""

from __future__ import annotations

import math

import sympy as sp
from toolkit import P, eng, ex, exset_plain, simp, tex, write_exercises, x, y, z

BASE = "mvc/m01-derivatives"


def vec_tex(v: list[sp.Expr]) -> str:
    return r"\left(" + r",\,".join(tex(c) for c in v) + r"\right)"


def vec_key(v: list[sp.Expr]) -> str:
    return "(" + ", ".join(eng(c) for c in v) + ")"


def unit(v: list[sp.Expr]) -> list[sp.Expr]:
    n = sp.sqrt(sum(c**2 for c in v))
    return [simp(c / n) for c in v]


def kind_of(value: sp.Expr) -> str:
    return "number" if value.is_Rational else "expression"


# --- gradient and directional derivative -----------------------------------------------------------------------------
def gradient_items() -> list[list[dict]]:
    grads: list[dict] = []
    dirs: list[dict] = []
    steep: list[dict] = []
    level: list[dict] = []

    def grad_item(i: str, f: sp.Expr, ftex: str, vars_: list, pt: list, pt_tex: str) -> None:
        g = [simp(sp.diff(f, v).subs(dict(zip(vars_, pt, strict=True)))) for v in vars_]
        names = ",".join(str(v) for v in vars_)
        parts = r",\ ".join(rf"f_{{{v}}}={tex(sp.diff(f, v))}" for v in vars_)
        grads.append(ex(
            f"gr-{i}", rf"Find the gradient $\nabla f$ of $f({names})={ftex}$ at the point {pt_tex}.", "vector", vec_key(g),
            hints=[rf"Compute each partial derivative first, then substitute the coordinates of the point."],
            solution=rf"The partial derivatives are ${parts}$. At the point they give $\nabla f={vec_tex(g)}$.",
            verify=[{"expr": f"diff({eng(f)}, {vars_[0]})", "equals": eng(sp.diff(f, vars_[0]))}],
        ))

    grad_item("01", P("x^3-3*x*y+y^2"), "x^3-3xy+y^2", [x, y], [1, 2], "$(1,2)$")
    grad_item("02", P("exp(x)*sin(y)"), r"e^{x}\sin y", [x, y], [sp.log(2), sp.pi / 6], r"$\left(\ln 2,\dfrac\pi6\right)$")
    grad_item("03", P("ln(x^2+y^2)"), r"\ln\left(x^2+y^2\right)", [x, y], [1, 2], "$(1,2)$")
    grad_item("04", P("x/y"), r"\dfrac{x}{y}", [x, y], [3, 3], "$(3,3)$")
    grad_item("05", P("x*y*z"), "xyz", [x, y, z], [1, 2, 3], "$(1,2,3)$")
    grad_item("06", P("x^2+y^2+z^2"), "x^2+y^2+z^2", [x, y, z], [1, -2, 2], "$(1,-2,2)$")

    def dir_item(i: str, f: sp.Expr, ftex: str, vars_: list, pt: list, pt_tex: str, v: list, how: str) -> None:
        sub = dict(zip(vars_, pt, strict=True))
        g = [simp(sp.diff(f, s).subs(sub)) for s in vars_]
        n = simp(sp.sqrt(sum(c**2 for c in v)))
        u = unit(v)
        val = simp(sum(a * b for a, b in zip(g, u, strict=True)))
        names = ",".join(str(s) for s in vars_)
        dirs.append(ex(
            f"dd-{i}", rf"Find the directional derivative of $f({names})={ftex}$ at {pt_tex} {how}", kind_of(val), eng(val),
            hints=[r"Use $\dirder{u}{f}=\dotp{\nabla f}{\vec u}$ with a **unit** vector $\vec u$: divide the direction by its length first."],
            solution=(
                rf"$\nabla f={vec_tex(g)}$ at the point. The direction vector has length ${tex(n)}$, so $\vec u={vec_tex(u)}$. "
                rf"Then $\dirder{{u}}{{f}}=\dotp{{{vec_tex(g)}}}{{{vec_tex(u)}}}={tex(val)}$."
            ),
        ))

    dir_item("01", P("x*y^2"), "xy^2", [x, y], [2, 1], "$(2,1)$", [1, -1], r"in the direction of $\vec v=(1,-1)$.")
    dir_item("02", P("x^2-y^2"), "x^2-y^2", [x, y], [2, 1], "$(2,1)$", [3, 4], r"in the direction of $\vec v=(3,4)$.")
    dir_item("03", P("exp(x*y)"), "e^{xy}", [x, y], [1, 0], "$(1,0)$", [1, 1], r"in the direction of $\vec v=(1,1)$.")
    dir_item("04", P("sqrt(x^2+y^2)"), r"\sqrt{x^2+y^2}", [x, y], [3, 4], "$(3,4)$", [1, 2], r"in the direction of $\vec v=(1,2)$.")
    dir_item("05", P("x^2+y*z"), "x^2+yz", [x, y, z], [1, 2, 1], "$(1,2,1)$", [2, 1, 2], r"in the direction of $\vec v=(2,1,2)$.")
    dir_item("06", P("x*y"), "xy", [x, y], [1, 1], "$P(1,1)$", [3, 4], r"in the direction from $P$ towards $Q(4,5)$.")

    # an angle: unit vector (cos 60, sin 60)
    f = P("x^2+y^2")
    g = [2, 2]
    val = simp(g[0] * sp.Rational(1, 2) + g[1] * sp.sqrt(3) / 2)
    dirs.append(ex(
        "dd-07", r"Find the directional derivative of $f(x,y)=x^2+y^2$ at $(1,1)$ in the direction that makes the angle $\dfrac\pi3$ with the positive $x$-axis.",
        "expression", eng(val),
        hints=[r"The unit vector at the angle $\theta$ with the $x$-axis is $(\cos\theta,\ \sin\theta)$."],
        solution=(
            r"The unit vector is $\vec u=\left(\cos\dfrac\pi3,\ \sin\dfrac\pi3\right)=\left(\dfrac12,\dfrac{\sqrt3}{2}\right)$ and $\nabla f(1,1)=(2,2)$. "
            r"So $\dirder{u}{f}=2\cdot\dfrac12+2\cdot\dfrac{\sqrt3}{2}=1+\sqrt3$."
        ),
    ))
    assert val == 1 + sp.sqrt(3) and f is not None

    def steep_value(i: str, f: sp.Expr, ftex: str, pt: list, pt_tex: str) -> None:
        g = [simp(sp.diff(f, s).subs({x: pt[0], y: pt[1]})) for s in (x, y)]
        n = simp(sp.sqrt(sum(c**2 for c in g)))
        steep.append(ex(
            f"st-{i}a", rf"What is the greatest rate of change of $f(x,y)={ftex}$ at {pt_tex}?", kind_of(n), eng(n),
            hints=[r"The greatest rate of change is $\norm{\nabla f}$."],
            solution=rf"$\nabla f={vec_tex(g)}$ at the point, so the greatest rate is $\norm{{\nabla f}}={tex(n)}$.",
        ))
        u = unit(g)
        steep.append(ex(
            f"st-{i}b", rf"In which direction does $f(x,y)={ftex}$ increase fastest at {pt_tex}? Give the unit vector.", "vector", vec_key(u),
            hints=[r"The direction of fastest increase is $\nabla f$. Divide it by its length."],
            solution=rf"$\nabla f={vec_tex(g)}$ has length ${tex(sp.sqrt(sum(c**2 for c in g)))}$, so the unit vector is ${vec_tex(u)}$.",
        ))

    steep_value("01", P("x^2+3*y^2"), "x^2+3y^2", [1, 1], "$(1,1)$")
    steep_value("02", P("x*y"), "xy", [2, 3], "$(2,3)$")

    g = [-1, 2]
    u = unit([-c for c in [2, -4]])
    steep.append(ex(
        "st-03", r"In which direction does $f(x,y)=x^2+y^2$ decrease fastest at $(1,-2)$? Give the unit vector.", "vector", vec_key(u),
        hints=[r"The fastest decrease is in the direction of $-\nabla f$."],
        solution=rf"$\nabla f(1,-2)=(2,-4)$, so $-\nabla f=(-2,4)$ with length $2\sqrt5$. The unit vector is ${vec_tex(u)}$.",
    ))
    assert u == unit(g)
    steep.append(ex(
        "st-04", r"At a point $P$ the gradient is $\nabla f(P)=(3,-4)$. What is the smallest value that a directional derivative $\dirder{u}{f}(P)$ can take?",
        "multiple_choice", "3",
        choices=[{"text": "$-1$", "value": "1"}, {"text": "$-3$", "value": "2"}, {"text": "$-5$", "value": "3"}, {"text": "$-7$", "value": "4"}],
        correctIndex=2, hints=[r"The smallest value is $-\norm{\nabla f(P)}$."],
        solution=r"$\norm{\nabla f(P)}=\sqrt{9+16}=5$, and the directional derivative is smallest, $-5$, in the direction of $-\nabla f(P)$.",
    ))
    steep.append(ex(
        "st-05", r"At $(1,2)$, give a direction $\vec u$ along which $f(x,y)=x^2+y^2$ does not change to first order, that is $\dirder{u}{f}=0$.",
        "direction", "(2, -1)",
        hints=[r"The directional derivative is $0$ when $\vec u$ is perpendicular to $\nabla f=(2,4)$."],
        solution=r"$\nabla f(1,2)=(2,4)$. A vector $(a,b)$ perpendicular to it satisfies $2a+4b=0$, for example $(2,-1)$. Any non-zero multiple is accepted.",
    ))

    def level_item(i: str, f: sp.Expr, ftex: str, c: sp.Expr, pt: tuple) -> None:
        assert simp(f.subs({x: pt[0], y: pt[1]}) - c) == 0
        g = [simp(sp.diff(f, s).subs({x: pt[0], y: pt[1]})) for s in (x, y)]
        poly = sp.expand(g[0] * (x - pt[0]) + g[1] * (y - pt[1]))
        coeffs = [int(co) for co in sp.Poly(poly, x, y).coeffs()]
        gcd = math.gcd(*coeffs)
        poly = sp.expand(poly / gcd)
        level.append(ex(
            f"lv-{i}", rf"Write the tangent line to the curve ${ftex}={tex(c)}$ at the point $({pt[0]},{pt[1]})$.", "equation", f"{eng(poly)}=0",
            coordinates=["x", "y"],
            hints=[rf"Take $f={ftex}$: its gradient is perpendicular to the curve, so it is a normal vector of the tangent line."],
            solution=rf"$\nabla f={vec_tex(g)}$ at the point, so the tangent line is ${tex(g[0])}(x-{pt[0]})+{tex(g[1])}(y-{pt[1]})=0$, that is ${tex(poly)}=0$.",
        ))

    level_item("01", P("x^2+y^2"), "x^2+y^2", sp.Integer(25), (3, 4))
    level_item("02", P("x^2-y^2"), "x^2-y^2", sp.Integer(3), (2, 1))
    level_item("03", P("x*y^2"), "xy^2", sp.Integer(18), (2, 3))
    g = [4, 6]
    level.append(ex(
        "lv-04", r"Give a normal vector of the curve $x^2+3y^2=7$ at the point $(2,1)$.", "direction", "(2, 3)",
        hints=[r"A normal vector of a level curve is the gradient."],
        solution=rf"For $f=x^2+3y^2$, $\nabla f=(2x,6y)=(4,6)$ at $(2,1)$. Dividing by $2$ gives $(2,3)$; any non-zero multiple is accepted.",
    ))
    assert g[0] * 3 == g[1] * 2

    return [grads, dirs, steep, level]


def build_gradient() -> None:
    grads, dirs, steep, level = gradient_items()
    write_exercises(
        f"{BASE}/u05-gradient/l01-gradient-and-directional-derivative",
        [
            exset_plain("gradient", "Compute the gradient at the given point.", grads,
                        format="Type the vector like `(3, -1)`; use exact values such as `sqrt(3)` and `pi`."),
            exset_plain("directional", "Compute the directional derivative.", dirs,
                        format="Type an exact value such as `4*sqrt(2)` or `16/5`."),
            exset_plain("steepest", "Fastest increase and decrease.", steep,
                        format="A unit vector is typed like `(sqrt(5)/5, 2*sqrt(5)/5)`; a direction like `(1, 3)`, any non-zero multiple is accepted."),
            exset_plain("level", "Level curves and tangent lines.", level,
                        format="Write the line as an equation, for example `3*x + 4*y = 25`; any non-zero multiple of the equation is accepted."),
        ],
        "mvc_new.py",
    )


# --- linear approximation, differential, errors --------------------------------------------------------------------------
def approximation_items() -> list[list[dict]]:
    approx: list[dict] = []
    errors: list[dict] = []
    diffs: list[dict] = []

    def approx_item(i: str, f: sp.Expr, ftex: str, base: tuple, dx: sp.Rational, dy: sp.Rational) -> None:
        sub = {x: base[0], y: base[1]}
        f0 = simp(f.subs(sub))
        fx, fy = (simp(sp.diff(f, s).subs(sub)) for s in (x, y))
        value = simp(f0 + fx * dx + fy * dy)
        target = (base[0] + dx, base[1] + dy)
        exact = float(f.subs({x: target[0], y: target[1]}))
        assert abs(float(value) - exact) < 0.02 * (1 + abs(exact)), (ftex, value, exact)  # the estimate is close to the true value
        approx.append(ex(
            f"la-{i}", rf"Use the linear approximation of $f(x,y)={ftex}$ at $({base[0]},{base[1]})$ to estimate $f\left({tex(target[0])},\ {tex(target[1])}\right)$.",
            kind_of(value), eng(value),
            hints=[rf"Compute $f$, $f_x$ and $f_y$ at $({base[0]},{base[1]})$, then use $\Delta x={tex(dx)}$ and $\Delta y={tex(dy)}$."],
            solution=(
                rf"$f({base[0]},{base[1]})={tex(f0)}$, $f_x={tex(fx)}$, $f_y={tex(fy)}$ at the base point. With $\Delta x={tex(dx)}$, $\Delta y={tex(dy)}$: "
                rf"$f\approx{tex(f0)}+{tex(fx)}\cdot{tex(dx)}+{tex(fy)}\cdot{tex(dy)}={tex(value)}$."
            ),
        ))

    approx_item("01", P("x*y^2"), "xy^2", (1, 2), sp.Rational(1, 10), sp.Rational(-1, 20))
    approx_item("02", P("sqrt(x^2+y^2)"), r"\sqrt{x^2+y^2}", (3, 4), sp.Rational(1, 50), sp.Rational(-1, 100))
    approx_item("03", P("x^2*y"), "x^2y", (2, 1), sp.Rational(1, 20), sp.Rational(1, 10))
    approx_item("04", P("x/y"), r"\dfrac{x}{y}", (4, 2), sp.Rational(1, 10), sp.Rational(-1, 20))
    approx_item("05", P("sqrt(x*y)"), r"\sqrt{xy}", (4, 9), sp.Rational(1, 10), sp.Rational(-1, 5))
    approx_item("06", P("exp(x)*cos(y)"), r"e^{x}\cos y", (0, 0), sp.Rational(1, 10), sp.Rational(1, 5))

    f = P("x^2*y")
    lin = simp(f.subs({x: 1, y: 1}) + sp.diff(f, x).subs({x: 1, y: 1}) * (x - 1) + sp.diff(f, y).subs({x: 1, y: 1}) * (y - 1))
    approx.append(ex(
        "la-07", r"Write the linearization $L(x,y)$ of $f(x,y)=x^2y$ at the point $(1,1)$, as an expression in $x$ and $y$.", "expression", eng(sp.expand(lin)),
        hints=[r"$L(x,y)=f(1,1)+f_x(1,1)(x-1)+f_y(1,1)(y-1)$."],
        solution=r"$f(1,1)=1$, $f_x=2xy=2$ and $f_y=x^2=1$ at $(1,1)$. So $L=1+2(x-1)+(y-1)=2x+y-2$.",
    ))
    assert sp.expand(lin) == 2 * x + y - 2

    def error_item(i: str, stmt: str, expr: sp.Expr, vars_: list, vals: list, errs: list, unit: str, sol: str) -> None:
        sub = dict(zip(vars_, vals, strict=True))
        total = simp(sum(abs(sp.diff(expr, v).subs(sub)) * e for v, e in zip(vars_, errs, strict=True)))
        errors.append(ex(f"er-{i}", stmt, kind_of(total), eng(total), hints=[r"Use $dQ=\sum \dfrac{\partial Q}{\partial x_i}\,dx_i$ and add the absolute values."], solution=sol.replace("{total}", tex(total))))

    r_, h_, a_, b_ = sp.symbols("r h a b", positive=True)
    error_item(
        "01",
        r"A rectangle has sides $x=10$ lu and $y=20$ lu, each measured with an error of at most $\dfrac1{10}$ lu. Estimate the largest error of its area $A=xy$ (in squ).",
        x * y, [x, y], [10, 20], [sp.Rational(1, 10)] * 2, "squ",
        r"$dA=y\,dx+x\,dy$, so $|dA|\le20\cdot\dfrac1{10}+10\cdot\dfrac1{10}={total}$.",
    )
    error_item(
        "02",
        r"The radius and height of a cylinder are $r=5$ lu and $h=10$ lu, each with an error of at most $\dfrac1{100}$ lu. Estimate the largest error of the volume $V=\pi r^2h$ (in cu).",
        sp.pi * r_**2 * h_, [r_, h_], [5, 10], [sp.Rational(1, 100)] * 2, "cu",
        r"$dV=2\pi rh\,dr+\pi r^2\,dh$, so $|dV|\le100\pi\cdot\dfrac1{100}+25\pi\cdot\dfrac1{100}={total}$.",
    )
    error_item(
        "03",
        r"The legs of a right triangle are $a=6$ lu and $b=8$ lu, each with an error of at most $\dfrac1{20}$ lu. Estimate the largest error of the hypotenuse $c=\sqrt{a^2+b^2}$ (in lu).",
        sp.sqrt(a_**2 + b_**2), [a_, b_], [6, 8], [sp.Rational(1, 20)] * 2, "lu",
        r"$dc=\dfrac{a}{c}\,da+\dfrac{b}{c}\,db$ with $c=10$, so $|dc|\le\dfrac{6}{10}\cdot\dfrac1{20}+\dfrac{8}{10}\cdot\dfrac1{20}={total}$.",
    )
    error_item(
        "04",
        r"The sides of a box are $x=2$ lu, $y=3$ lu and $z=4$ lu, each with an error of at most $\dfrac1{50}$ lu. Estimate the largest error of its volume $V=xyz$ (in cu).",
        x * y * z, [x, y, z], [2, 3, 4], [sp.Rational(1, 50)] * 3, "cu",
        r"$dV=yz\,dx+xz\,dy+xy\,dz$, so $|dV|\le\left(12+8+6\right)\cdot\dfrac1{50}={total}$.",
    )

    # the differential
    def diff_item(i: str, f: sp.Expr, ftex: str, base: tuple, dx: sp.Rational, dy: sp.Rational) -> None:
        sub = {x: base[0], y: base[1]}
        fx, fy = (simp(sp.diff(f, s).subs(sub)) for s in (x, y))
        value = simp(fx * dx + fy * dy)
        diffs.append(ex(
            f"df-{i}", rf"Let $f(x,y)={ftex}$. Compute the differential $df=f_x\,dx+f_y\,dy$ at $({base[0]},{base[1]})$ for $dx={tex(dx)}$ and $dy={tex(dy)}$.",
            kind_of(value), eng(value),
            hints=[r"Evaluate $f_x$ and $f_y$ at the point, then multiply by $dx$ and $dy$."],
            solution=rf"$f_x={tex(fx)}$ and $f_y={tex(fy)}$ at the point, so $df={tex(fx)}\cdot{tex(dx)}+{tex(fy)}\cdot{tex(dy)}={tex(value)}$.",
        ))

    diff_item("01", P("x^2*y^3"), "x^2y^3", (1, 2), sp.Rational(1, 10), sp.Rational(-1, 20))
    diff_item("02", P("ln(x^2+y^2)"), r"\ln\left(x^2+y^2\right)", (1, 1), sp.Rational(1, 10), sp.Rational(1, 20))
    diffs.append(ex(
        "df-03", r"Which statement guarantees that $f(x,y)$ is differentiable at a point?", "multiple_choice", "2",
        choices=[
            {"text": r"$f_x$ and $f_y$ exist at the point", "value": "1"},
            {"text": r"$f_x$ and $f_y$ exist near the point and are continuous at it", "value": "2"},
            {"text": r"$f$ is defined at the point", "value": "3"},
        ],
        correctIndex=1, hints=[r"Having partial derivatives alone is not enough: the graph might have no tangent plane."],
        solution=r"Continuous partial derivatives near the point imply differentiability. The existence of $f_x$ and $f_y$ at the point alone does not.",
    ))
    # relative error of a product: dA/A = dx/x + dy/y
    q = sp.Rational(1, 1)
    rel = simp(sp.diff(sp.log(x * y), x) * x * q + sp.diff(sp.log(x * y), y) * y * q)
    assert rel == 2
    diffs.append(ex(
        "df-04", r"The sides $x$ and $y$ of a rectangle are each measured with a relative error of at most $1\%$. Estimate the largest relative error of the area $A=xy$, in percent (give the number only).",
        "number", "2",
        hints=[r"Take the logarithm: $\ln A=\ln x+\ln y$, so $\dfrac{dA}{A}=\dfrac{dx}{x}+\dfrac{dy}{y}$."],
        solution=r"$\dfrac{dA}{A}=\dfrac{dx}{x}+\dfrac{dy}{y}$, so the relative errors add: $1\%+1\%=2\%$.",
    ))
    return [approx, errors, diffs]


def build_approximation() -> None:
    approx, errors, diffs = approximation_items()
    write_exercises(
        f"{BASE}/u02-partial-differentiation/l05-linear-approximation",
        [
            exset_plain("approximation", "Estimate with the linear approximation.", approx,
                        format="Type an exact fraction such as `7/3`, or an exact expression."),
            exset_plain("errors", "Estimate the largest error of a computed quantity (the unit is in the statement; give the number only).", errors,
                        format="Type an exact value such as `7/10` or `2*pi`."),
            exset_plain("differentials", "The differential.", diffs, format="Type an exact value such as `3/8`."),
        ],
        "mvc_new.py",
    )


def build() -> None:
    build_gradient()
    build_approximation()
