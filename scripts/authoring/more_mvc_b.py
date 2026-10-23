"""More practice for Course 2, Modules 2 and 3: double and triple integrals, polar, cylindrical and spherical coordinates,
the Jacobian, areas and volumes. Keys are computed exactly with SymPy and every integral is cross-checked by a numerical grid sum."""

from __future__ import annotations

import math

import sympy as sp
from toolkit import P, add_extra, eng, ex, exset_plain, simp, tex, x, y, z

SCRIPT = "more_mvc_b.py"
M2 = "mvc/m02-double-integrals"
M3 = "mvc/m03-triple-integrals"
r, th, ph, rho = sp.symbols("r theta varphi rho", positive=True)
uu, vv = sp.symbols("u v", real=True)


def kind_of(value: sp.Expr) -> str:
    return "number" if value.is_Rational else "expression"


def num_ok(exact: sp.Expr, approx: float, tol: float = 0.02) -> None:
    assert abs(float(exact) - approx) <= tol * (1 + abs(approx)), (exact, float(exact), approx)


def grid2(f, inside, box: tuple, n: int = 600) -> float:
    """Midpoint grid sum of f over the part of the box where inside(x, y) holds."""
    ax, bx, ay, by = box
    dx, dy = (bx - ax) / n, (by - ay) / n
    total = 0.0
    for i in range(n):
        xv = ax + (i + 0.5) * dx
        for j in range(n):
            yv = ay + (j + 0.5) * dy
            if inside(xv, yv):
                total += f(xv, yv)
    return total * dx * dy


def grid3(f, inside, box: tuple, n: int = 60) -> float:
    ax, bx, ay, by, az, bz = box
    dx, dy, dz = (bx - ax) / n, (by - ay) / n, (bz - az) / n
    total = 0.0
    for i in range(n):
        xv = ax + (i + 0.5) * dx
        for j in range(n):
            yv = ay + (j + 0.5) * dy
            for k in range(n):
                zv = az + (k + 0.5) * dz
                if inside(xv, yv, zv):
                    total += f(xv, yv, zv)
    return total * dx * dy * dz


def lam2(e: sp.Expr):
    return sp.lambdify((x, y), e, "math")


def lam3(e: sp.Expr):
    return sp.lambdify((x, y, z), e, "math")


# --- double integrals: rectangles, regions, order of integration --------------------------------------------------------------
def iterated_items() -> list[dict]:
    items = []

    def rect(i: str, fl: str, fn: str, xs: tuple, ys: tuple, xs_tex: str, ys_tex: str) -> None:
        f = P(fn)
        val = simp(sp.integrate(sp.integrate(f, (y, ys[0], ys[1])), (x, xs[0], xs[1])))
        fl_ = lam2(f)
        num_ok(val, grid2(fl_, lambda a, b: True, (float(xs[0]), float(xs[1]), float(ys[0]), float(ys[1])), 400))
        items.append(ex(
            f"mp-it-{i}", rf"$\displaystyle\iint_R{fl}\,dA$ over the rectangle $R:\ {xs_tex},\ {ys_tex}$.", kind_of(val), eng(val),
            hints=[r"Integrate first in $y$ (treat $x$ as a constant), then in $x$."],
            solution=rf"$\displaystyle\int_{{{tex(xs[0])}}}^{{{tex(xs[1])}}}\int_{{{tex(ys[0])}}}^{{{tex(ys[1])}}}{fl}\,dy\,dx={tex(val)}$.",
        ))

    rect("1", "xy^2", "x*y^2", (0, 2), (1, 3), r"0\le x\le2", r"1\le y\le3")
    rect("2", "(2x+3y)", "2*x+3*y", (0, 1), (0, 2), r"0\le x\le1", r"0\le y\le2")
    rect("3", r"x\cos y", "x*cos(y)", (0, 2), (0, sp.pi / 2), r"0\le x\le2", r"0\le y\le\dfrac\pi2")

    def type1(i: str, fl: str, fn: str, xlo, xhi, ylo, yhi, desc: str) -> None:
        f = P(fn)
        val = simp(sp.integrate(sp.integrate(f, (y, ylo, yhi)), (x, xlo, xhi)))
        fl_ = lam2(f)
        lo, hi = lam2(ylo) if False else None, None
        ylo_f = sp.lambdify(x, ylo, "math")
        yhi_f = sp.lambdify(x, yhi, "math")
        num_ok(val, grid2(fl_, lambda a, b: ylo_f(a) <= b <= yhi_f(a), (float(xlo), float(xhi), float(sp.minimum(ylo, x, sp.Interval(xlo, xhi))), float(sp.maximum(yhi, x, sp.Interval(xlo, xhi)))), 500))
        inner = simp(sp.integrate(f, (y, ylo, yhi)))
        items.append(ex(
            f"mp-it-{i}", rf"$\displaystyle\iint_D{fl}\,dA$, where $D:\ {desc}$.", kind_of(val), eng(val),
            hints=[r"Integrate in $y$ first, between the lower and the upper curve; the result is a function of $x$."],
            solution=rf"Inner integral: $\displaystyle\int_{{{tex(ylo)}}}^{{{tex(yhi)}}}{fl}\,dy={tex(inner)}$. Outer integral: $\displaystyle\int_{{{tex(xlo)}}}^{{{tex(xhi)}}}\left({tex(inner)}\right)dx={tex(val)}$.",
        ))

    type1("4", "xy", "x*y", sp.Integer(0), sp.Integer(1), x**2, x, r"0\le x\le1,\ x^2\le y\le x")
    type1("5", "(x+y)", "x+y", sp.Integer(0), sp.Integer(2), sp.Integer(0), x, r"0\le x\le2,\ 0\le y\le x")
    type1("6", r"\left(x^2+y\right)", "x^2+y", sp.Integer(0), sp.Integer(1), sp.Integer(0), sp.sqrt(x), r"0\le x\le1,\ 0\le y\le\sqrt x")

    # Type II: integrate in x first
    f = P("exp(y^2)")
    val = simp(sp.integrate(sp.integrate(f, (x, 0, y)), (y, 0, 1)))
    num_ok(val, grid2(lam2(f), lambda a, b: 0 <= a <= b, (0, 1, 0, 1), 500))
    items.append(ex(
        "mp-it-7", r"$\displaystyle\iint_De^{y^2}\,dA$, where $D:\ 0\le y\le1,\ 0\le x\le y$.", "expression", eng(val),
        hints=[r"The region is described with $y$ as the outer variable: integrate in $x$ first."],
        solution=r"$\displaystyle\int_0^1\!\!\int_0^ye^{y^2}\,dx\,dy=\int_0^1ye^{y^2}\,dy=\left[\dfrac12e^{y^2}\right]_0^1=\dfrac{e-1}{2}$.",
    ))

    # change the order of integration
    f = sp.sin(y**2)
    val = simp(sp.integrate(sp.integrate(f, (y, x, 1)), (x, 0, 1)))
    swapped = simp(sp.integrate(sp.integrate(f, (x, 0, y)), (y, 0, 1)))
    assert simp(val - swapped) == 0
    num_ok(val, grid2(lam2(f), lambda a, b: a <= b, (0, 1, 0, 1), 500))
    items.append(ex(
        "mp-it-8", r"Evaluate $\displaystyle\int_0^1\!\!\int_x^1\sin\left(y^2\right)dy\,dx$ by changing the order of integration.", "expression", eng(val),
        hints=[r"The region is $0\le x\le y\le1$. Integrate in $x$ first: $x$ runs from $0$ to $y$."],
        solution=r"$\displaystyle\int_0^1\!\!\int_0^y\sin\left(y^2\right)dx\,dy=\int_0^1y\sin\left(y^2\right)dy=\left[-\dfrac12\cos\left(y^2\right)\right]_0^1=\dfrac{1-\cos1}{2}$.",
    ))
    items.append(ex(
        "mp-it-9", r"The integral $\displaystyle\int_0^1\!\!\int_x^1\sin\left(y^2\right)dy\,dx$ cannot be done in the given order. Why does changing the order help?",
        "multiple_choice", "1",
        choices=[
            {"text": r"The inner integral $\int\sin(y^2)\,dy$ has no elementary antiderivative, but after the swap the inner variable is $x$ and $\sin(y^2)$ is constant in $x$", "value": "1"},
            {"text": r"Changing the order changes the value of the integral", "value": "2"},
            {"text": r"The region of integration becomes a rectangle", "value": "3"},
        ],
        correctIndex=0, hints=[r"Sketch the triangle $0\le x\le y\le1$ and describe it in the other order."],
        solution=r"The triangle can be described as $0\le y\le1$, $0\le x\le y$. Then the inner integral is in $x$, and $\sin(y^2)$ is a constant for it. The value of the integral does not change.",
    ))
    return items


# --- polar coordinates ------------------------------------------------------------------------------------------------------------
def polar_items() -> list[dict]:
    items = []

    def polar(i: str, stmt: str, integrand_r: sp.Expr, rlo, rhi, tlo, thi, cart: sp.Expr, inside, box: tuple, hint: str, extra: str = "") -> None:
        val = simp(sp.integrate(sp.integrate(integrand_r * r, (r, rlo, rhi)), (th, tlo, thi)))
        num_ok(val, grid2(lam2(cart), inside, box, 700))
        items.append(ex(
            f"mp-po-{i}", stmt, kind_of(val), eng(val), hints=[hint],
            solution=rf"In polar coordinates $dA=r\,dr\,d\theta$. {extra}$\displaystyle\int_{{{tex(tlo)}}}^{{{tex(thi)}}}\!\int_{{{tex(rlo)}}}^{{{tex(rhi)}}}{tex(integrand_r)}\,r\,dr\,d\theta={tex(val)}$.",
        ))

    disc = lambda R: (lambda a, b: a * a + b * b <= R * R)  # noqa: E731
    polar("1", r"$\displaystyle\iint_D\left(x^2+y^2\right)dA$, where $D$ is the disc $x^2+y^2\le4$.", r**2, 0, 2, 0, 2 * sp.pi, P("x^2+y^2"), disc(2), (-2, 2, -2, 2),
          r"Put $x^2+y^2=r^2$.", "Here $x^2+y^2=r^2$. ")
    polar("2", r"$\displaystyle\iint_De^{-(x^2+y^2)}dA$, where $D$ is the disc $x^2+y^2\le1$.", sp.exp(-r**2), 0, 1, 0, 2 * sp.pi, P("exp(-(x^2+y^2))"), disc(1), (-1, 1, -1, 1),
          r"The integrand is $e^{-r^2}$ and $\int re^{-r^2}dr=-\dfrac12e^{-r^2}$.")
    polar("3", r"$\displaystyle\iint_D\sqrt{x^2+y^2}\,dA$, where $D$ is the annulus $1\le x^2+y^2\le4$.", r, 1, 2, 0, 2 * sp.pi, P("sqrt(x^2+y^2)"),
          lambda a, b: 1 <= a * a + b * b <= 4, (-2, 2, -2, 2), r"The annulus is $1\le r\le2$, $0\le\theta\le2\pi$.")
    polar("4", r"$\displaystyle\iint_Dx\,dA$, where $D$ is the half-disc $x^2+y^2\le4,\ x\ge0$.", r * sp.cos(th), 0, 2, -sp.pi / 2, sp.pi / 2, P("x"),
          lambda a, b: a >= 0 and a * a + b * b <= 4, (0, 2, -2, 2), r"The half-disc is $0\le r\le2$, $-\dfrac\pi2\le\theta\le\dfrac\pi2$, and $x=r\cos\theta$.")
    polar("5", r"$\displaystyle\iint_Dy\,dA$, where $D$ is the quarter of the disc $x^2+y^2\le9$ in the first quadrant.", r * sp.sin(th), 0, 3, 0, sp.pi / 2, P("y"),
          lambda a, b: a >= 0 and b >= 0 and a * a + b * b <= 9, (0, 3, 0, 3), r"The quarter-disc is $0\le r\le3$, $0\le\theta\le\dfrac\pi2$, and $y=r\sin\theta$.")
    polar("6", r"$\displaystyle\iint_D\dfrac{dA}{1+x^2+y^2}$, where $D$ is the disc $x^2+y^2\le1$.", 1 / (1 + r**2), 0, 1, 0, 2 * sp.pi, P("1/(1+x^2+y^2)"), disc(1), (-1, 1, -1, 1),
          r"$\int\dfrac{r}{1+r^2}dr=\dfrac12\ln\left(1+r^2\right)$.")
    polar("7", r"Evaluate $\displaystyle\int_0^1\!\!\int_0^{\sqrt{1-x^2}}\left(x^2+y^2\right)dy\,dx$ by changing to polar coordinates.", r**2, 0, 1, 0, sp.pi / 2, P("x^2+y^2"),
          lambda a, b: a >= 0 and b >= 0 and a * a + b * b <= 1, (0, 1, 0, 1), r"The region is the quarter-disc $x\ge0$, $y\ge0$, $x^2+y^2\le1$.", "The region is the quarter of the unit disc. ")
    polar("8", r"Find the area of the sector $0\le\theta\le\dfrac\pi3$, $0\le r\le2$ (the unit is squ: give the number only).", sp.Integer(1), 0, 2, 0, sp.pi / 3, sp.Integer(1) + 0 * x,
          lambda a, b: a * a + b * b <= 4 and b >= 0 and b <= a * math.sqrt(3), (0, 2, 0, 2 * math.sin(math.pi / 3)), r"Area $=\iint1\,dA$.")

    # areas of curves given in polar form
    def area(i: str, stmt: str, rexpr: sp.Expr, tlo, thi, cart_inside, box, hint: str) -> None:
        val = simp(sp.integrate(rexpr**2 / 2, (th, tlo, thi)))
        num_ok(val, grid2(lambda a, b: 1.0, cart_inside, box, 700))
        items.append(ex(f"mp-po-{i}", stmt, kind_of(val), eng(val), hints=[hint],
                        solution=rf"$A=\dfrac12\displaystyle\int_{{{tex(tlo)}}}^{{{tex(thi)}}}r^2\,d\theta=\dfrac12\int_{{{tex(tlo)}}}^{{{tex(thi)}}}\left({tex(rexpr)}\right)^2d\theta={tex(val)}$."))

    def cardioid(a, b):
        rr_ = math.hypot(a, b)
        ang = math.atan2(b, a)
        return rr_ <= 1 + math.cos(ang)

    area("9", r"Find the area enclosed by the cardioid $r=1+\cos\theta$ (the unit is squ: give the number only).", 1 + sp.cos(th), 0, 2 * sp.pi, cardioid, (-1, 2, -1.5, 1.5),
         r"$A=\dfrac12\int r^2\,d\theta$.")
    area("10", r"Find the area enclosed by the circle $r=2\cos\theta$ (the unit is squ: give the number only).", 2 * sp.cos(th), -sp.pi / 2, sp.pi / 2,
         lambda a, b: (a - 1) ** 2 + b * b <= 1, (0, 2, -1, 1), r"The circle is traced once for $-\dfrac\pi2\le\theta\le\dfrac\pi2$.")

    val = simp(sp.integrate(sp.integrate((r**2) * r, (r, 0, 1)), (th, 0, 2 * sp.pi)))
    items.append(ex(
        "mp-po-11", r"Find the volume of the solid under the paraboloid $z=x^2+y^2$ and above the unit disc $x^2+y^2\le1$ (the unit is cu: give the number only).",
        "expression", eng(val), hints=[r"$V=\iint_D\left(x^2+y^2\right)dA$ in polar coordinates."],
        solution=r"$V=\displaystyle\int_0^{2\pi}\!\!\int_0^1r^2\cdot r\,dr\,d\theta=2\pi\cdot\dfrac14=\dfrac\pi2$.",
    ))
    assert val == sp.pi / 2
    items.append(ex(
        "mp-po-12", r"Which description of the disc $x^2+y^2\le9$ in polar coordinates is correct?", "multiple_choice", "3",
        choices=[
            {"text": r"$0\le r\le9,\ 0\le\theta\le\pi$", "value": "1"},
            {"text": r"$0\le r\le9,\ 0\le\theta\le2\pi$", "value": "2"},
            {"text": r"$0\le r\le3,\ 0\le\theta\le2\pi$", "value": "3"},
        ],
        correctIndex=2, hints=[r"$x^2+y^2=r^2$."],
        solution=r"$x^2+y^2\le9$ means $r^2\le9$, so $0\le r\le3$; the whole disc needs $0\le\theta\le2\pi$.",
    ))
    return items


# --- Jacobian -------------------------------------------------------------------------------------------------------------------------
def jacobian_items() -> list[dict]:
    items = []

    def jac(i: str, xs: str, ys: str, xe: sp.Expr, ye: sp.Expr) -> sp.Expr:
        j = simp(sp.Matrix([[sp.diff(xe, uu), sp.diff(xe, vv)], [sp.diff(ye, uu), sp.diff(ye, vv)]]).det())
        h = 1e-6
        at = {uu: 1.3, vv: 0.7}
        fxy = sp.lambdify((uu, vv), [xe, ye], "math")

        def d(k: int, var: int) -> float:
            p = [1.3, 0.7]
            q = list(p)
            p[var] += h
            q[var] -= h
            return (fxy(*p)[k] - fxy(*q)[k]) / (2 * h)

        num = d(0, 0) * d(1, 1) - d(0, 1) * d(1, 0)
        assert abs(num - float(j.subs(at))) < 1e-5, (xs, ys, num, j)
        items.append(ex(
            f"mp-ja-{i}", rf"Find the Jacobian $\dfrac{{\partial(x,y)}}{{\partial(u,v)}}$ of the change of variables $x={xs}$, $y={ys}$.", "expression", eng(j), variables=["u", "v"],
            hints=[r"$\dfrac{\partial(x,y)}{\partial(u,v)}=x_uy_v-x_vy_u$."],
            solution=rf"$x_u={tex(sp.diff(xe, uu))}$, $x_v={tex(sp.diff(xe, vv))}$, $y_u={tex(sp.diff(ye, uu))}$, $y_v={tex(sp.diff(ye, vv))}$, so the Jacobian is $x_uy_v-x_vy_u={tex(j)}$.",
        ))
        return j

    jac("1", "u+v", "u-v", uu + vv, uu - vv)
    jac("2", r"u\cos v", r"u\sin v", uu * sp.cos(vv), uu * sp.sin(vv))
    jac("3", "2u+3v", "u-v", 2 * uu + 3 * vv, uu - vv)
    jac("4", "e^{u}\\cos v", "e^{u}\\sin v", sp.exp(uu) * sp.cos(vv), sp.exp(uu) * sp.sin(vv))
    jac("5", "u^2-v^2", "2uv", uu**2 - vv**2, 2 * uu * vv)
    jac("6", "uv", "u+v", uu * vv, uu + vv)

    def at_point(i: str, xs: str, ys: str, xe: sp.Expr, ye: sp.Expr, p: tuple) -> None:
        j = simp(sp.Matrix([[sp.diff(xe, uu), sp.diff(xe, vv)], [sp.diff(ye, uu), sp.diff(ye, vv)]]).det())
        val = simp(j.subs({uu: p[0], vv: p[1]}))
        items.append(ex(
            f"mp-ja-{i}", rf"For $x={xs}$, $y={ys}$, find the value of $\dfrac{{\partial(x,y)}}{{\partial(u,v)}}$ at $(u,v)=({p[0]},{p[1]})$.", kind_of(val), eng(val),
            hints=[r"Compute the Jacobian as an expression first, then substitute."],
            solution=rf"The Jacobian is ${tex(j)}$, which at $({p[0]},{p[1]})$ equals ${tex(val)}$.",
        ))

    at_point("7", "u^2-v^2", "2uv", uu**2 - vv**2, 2 * uu * vv, (1, 2))
    at_point("8", "uv", "u+v", uu * vv, uu + vv, (3, 1))
    at_point("9", r"u\cos v", r"u\sin v", uu * sp.cos(vv), uu * sp.sin(vv), (4, sp.pi / 3))

    # the area of an ellipse
    a_, b_ = 3, 2
    val = simp(sp.integrate(sp.integrate(a_ * b_, (uu, 0, 1)) * 1, (vv, 0, 2 * sp.pi)) * 0 + sp.integrate(sp.integrate(a_ * b_ * uu, (uu, 0, 1)), (vv, 0, 2 * sp.pi)))
    assert val == 6 * sp.pi
    items.append(ex(
        "mp-ja-10", r"Use the substitution $x=3u\cos v$, $y=2u\sin v$ to find the area of the ellipse $\dfrac{x^2}{9}+\dfrac{y^2}{4}\le1$ (the unit is squ: give the number only).",
        "expression", "6*pi", hints=[r"The ellipse becomes $0\le u\le1$, $0\le v\le2\pi$, and $dA=\left|\dfrac{\partial(x,y)}{\partial(u,v)}\right|du\,dv$."],
        solution=r"$\dfrac{\partial(x,y)}{\partial(u,v)}=3\cos v\cdot2u\cos v-(-3u\sin v)\cdot2\sin v=6u$. Then $A=\displaystyle\int_0^{2\pi}\!\!\int_0^16u\,du\,dv=6\pi$.",
    ))
    # a linear substitution on a parallelogram
    val = simp(sp.integrate(sp.integrate(uu * sp.Rational(1, 2), (uu, 0, 2)), (vv, 0, 2)))
    f = lam2(P("x+y"))
    num_ok(val, grid2(f, lambda a, b: 0 <= a + b <= 2 and 0 <= a - b <= 2, (0, 2, -1, 1), 700))
    items.append(ex(
        "mp-ja-11", r"Let $D$ be the square with vertices $(0,0)$, $(1,1)$, $(2,0)$, $(1,-1)$. Use $u=x+y$, $v=x-y$ to compute $\displaystyle\iint_D(x+y)\,dA$.", kind_of(val), eng(val),
        hints=[r"In the new variables $D$ is $0\le u\le2$, $0\le v\le2$. Solve for $x=\dfrac{u+v}{2}$, $y=\dfrac{u-v}{2}$ and find $|J|$."],
        solution=r"$x=\dfrac{u+v}{2}$, $y=\dfrac{u-v}{2}$ give $\dfrac{\partial(x,y)}{\partial(u,v)}=-\dfrac12$, so $dA=\dfrac12\,du\,dv$ and $\displaystyle\iint_D(x+y)\,dA=\int_0^2\!\!\int_0^2u\cdot\dfrac12\,du\,dv=2$.",
    ))
    # polar Jacobian meaning
    items.append(ex(
        "mp-ja-12", r"In the change of variables $x=r\cos\theta$, $y=r\sin\theta$ the area element is $dA=\left|\dfrac{\partial(x,y)}{\partial(r,\theta)}\right|dr\,d\theta$. What is the factor?",
        "multiple_choice", "2",
        choices=[{"text": "$1$", "value": "1"}, {"text": "$r$", "value": "2"}, {"text": r"$r^2$", "value": "3"}],
        correctIndex=1, hints=[r"Compute $x_ry_\theta-x_\theta y_r$."],
        solution=r"$x_ry_\theta-x_\theta y_r=\cos\theta\cdot r\cos\theta-(-r\sin\theta)\sin\theta=r$.",
    ))
    items.append(ex(
        "mp-ja-13", r"A change of variables has Jacobian $\dfrac{\partial(x,y)}{\partial(u,v)}=-3$ everywhere. A region of area $5$ in the $uv$-plane is mapped to a region of what area in the $xy$-plane?",
        "number", "15", hints=[r"Areas are multiplied by $|J|$."], solution=r"The area is multiplied by $|J|=3$: $5\cdot3=15$.",
    ))
    items.append(ex(
        "mp-ja-14", r"For $x=u+2v$, $y=3u+v$, find the Jacobian $\dfrac{\partial(x,y)}{\partial(u,v)}$.", "number", "-5",
        hints=[r"$x_uy_v-x_vy_u=1\cdot1-2\cdot3$."], solution=r"$x_u=1$, $x_v=2$, $y_u=3$, $y_v=1$, so $J=1\cdot1-2\cdot3=-5$.",
    ))
    assert sp.Matrix([[1, 2], [3, 1]]).det() == -5
    return items


# --- areas between curves --------------------------------------------------------------------------------------------------------------
def area_items() -> list[dict]:
    items = []

    def area(i: str, stmt: str, top: sp.Expr, bottom: sp.Expr, xlo, xhi, how: str) -> None:
        val = simp(sp.integrate(top - bottom, (x, xlo, xhi)))
        tf, bf = sp.lambdify(x, top, "math"), sp.lambdify(x, bottom, "math")
        n = 20000
        approx = sum((tf(float(xlo) + (k + 0.5) * (float(xhi) - float(xlo)) / n) - bf(float(xlo) + (k + 0.5) * (float(xhi) - float(xlo)) / n)) for k in range(n)) * (float(xhi) - float(xlo)) / n
        num_ok(val, approx, 1e-4)
        items.append(ex(
            f"mp-ar-{i}", stmt + " The unit is squ: give the number only.", kind_of(val), eng(val),
            hints=[r"Sketch the region, find where the curves meet, and integrate (upper curve) $-$ (lower curve)."],
            solution=rf"{how} $A=\displaystyle\int_{{{tex(xlo)}}}^{{{tex(xhi)}}}\left({tex(top)}-\left({tex(bottom)}\right)\right)dx={tex(val)}$.",
        ))

    area("1", r"Find the area of the region between $y=x^2$ and $y=x+2$.", x + 2, x**2, -1, 2, r"They meet where $x^2=x+2$, at $x=-1$ and $x=2$.")
    area("2", r"Find the area of the region between $y=x^3$ and $y=x$ for $0\le x\le1$.", x, x**3, 0, 1, r"On $[0,1]$ the line is above the cubic.")
    area("3", r"Find the area of the region bounded by $y=e^x$, $y=1$ and $x=1$.", sp.exp(x), sp.Integer(1), 0, 1, r"The curve $y=e^x$ meets $y=1$ at $x=0$.")
    area("4", r"Find the area of the region bounded by $y=\ln x$, the $x$-axis and the line $x=e$.", sp.log(x), sp.Integer(0), 1, sp.E, r"The curve meets the $x$-axis at $x=1$.")
    area("5", r"Find the area of the region bounded by $y=4-x^2$ and the $x$-axis.", 4 - x**2, sp.Integer(0), -2, 2, r"The parabola meets the axis at $x=\pm2$.")
    area("6", r"Find the area of the region between $y=x^2$ and $y=2-x^2$.", 2 - x**2, x**2, -1, 1, r"They meet where $x^2=2-x^2$, at $x=\pm1$.")
    area("7", r"Find the area of the region between $y=\sqrt x$ and $y=x^2$.", sp.sqrt(x), x**2, 0, 1, r"They meet at $x=0$ and $x=1$.")
    area("8", r"Find the area of the region between $y=\sin x$ and $y=\cos x$ for $0\le x\le\dfrac\pi4$.", sp.cos(x), sp.sin(x), 0, sp.pi / 4, r"On this interval cosine is above sine.")
    # with respect to y: x = y^2 and x = y + 2
    val = simp(sp.integrate((y + 2) - y**2, (y, -1, 2)))
    assert val == sp.Rational(9, 2)
    items.append(ex(
        "mp-ar-9", r"Find the area of the region bounded by $x=y^2$ and $x=y+2$. The unit is squ: give the number only.", "number", "9/2",
        hints=[r"Integrate with respect to $y$: the curves meet where $y^2=y+2$."],
        solution=r"They meet at $y=-1$ and $y=2$. On this interval the line $x=y+2$ is to the right of the parabola, so $A=\displaystyle\int_{-1}^{2}\left(y+2-y^2\right)dy=\dfrac92$.",
    ))
    return items


# --- triple integrals ----------------------------------------------------------------------------------------------------------------------
def triple_items() -> list[dict]:
    items = []

    def box(i: str, stmt: str, fn: str, xs: tuple, ys: tuple, zs: tuple) -> None:
        f = P(fn)
        val = simp(sp.integrate(f, (z, zs[0], zs[1]), (y, ys[0], ys[1]), (x, xs[0], xs[1])))
        num_ok(val, grid3(lam3(f), lambda a, b, c: True, (float(xs[0]), float(xs[1]), float(ys[0]), float(ys[1]), float(zs[0]), float(zs[1])), 40))
        items.append(ex(
            f"mp-tr-{i}", stmt, kind_of(val), eng(val), hints=[r"Over a box the limits are constants: integrate one variable at a time."],
            solution=rf"$\displaystyle\iiint f\,dV=\int_{{{tex(xs[0])}}}^{{{tex(xs[1])}}}\!\int_{{{tex(ys[0])}}}^{{{tex(ys[1])}}}\!\int_{{{tex(zs[0])}}}^{{{tex(zs[1])}}}f\,dz\,dy\,dx={tex(val)}$.",
        ))

    box("1", r"$\displaystyle\iiint_Dxyz\,dV$ over the box $0\le x\le1,\ 0\le y\le2,\ 0\le z\le3$.", "x*y*z", (0, 1), (0, 2), (0, 3))
    box("2", r"$\displaystyle\iiint_D(x+y+z)\,dV$ over the cube $[0,1]^3$.", "x+y+z", (0, 1), (0, 1), (0, 1))
    box("3", r"$\displaystyle\iiint_De^{x+y+z}\,dV$ over the cube $[0,1]^3$.", "exp(x+y+z)", (0, 1), (0, 1), (0, 1))

    def simplex(i: str, stmt: str, fn: str) -> None:
        f = P(fn)
        val = simp(sp.integrate(f, (z, 0, 1 - x - y), (y, 0, 1 - x), (x, 0, 1)))
        num_ok(val, grid3(lam3(f), lambda a, b, c: a + b + c <= 1, (0, 1, 0, 1, 0, 1), 50))
        items.append(ex(
            f"mp-tr-{i}", stmt, kind_of(val), eng(val), hints=[r"The solid is $0\le x\le1$, $0\le y\le1-x$, $0\le z\le1-x-y$."],
            solution=rf"$\displaystyle\int_0^1\!\!\int_0^{{1-x}}\!\!\int_0^{{1-x-y}}f\,dz\,dy\,dx={tex(val)}$.",
        ))

    simplex("4", r"$\displaystyle\iiint_D(x+2y)\,dV$, where $D$ is the tetrahedron bounded by the coordinate planes and $x+y+z=1$.", "x+2*y")
    simplex("5", r"$\displaystyle\iiint_D(x+y+z)\,dV$, where $D$ is the tetrahedron bounded by the coordinate planes and $x+y+z=1$.", "x+y+z")

    def vol(i: str, stmt: str, zhi: sp.Expr, ylo, yhi, xlo, xhi, inside, bx: tuple) -> None:
        val = simp(sp.integrate(1, (z, 0, zhi), (y, ylo, yhi), (x, xlo, xhi)))
        num_ok(val, grid3(lambda a, b, c: 1.0, inside, bx, 50))
        items.append(ex(
            f"mp-tr-{i}", stmt + " The unit is cu: give the number only.", kind_of(val), eng(val), hints=[r"The volume is $\iiint_D1\,dV$."],
            solution=rf"$V=\displaystyle\int_{{{tex(xlo)}}}^{{{tex(xhi)}}}\!\int_{{{tex(ylo)}}}^{{{tex(yhi)}}}\!\int_0^{{{tex(zhi)}}}dz\,dy\,dx={tex(val)}$.",
        ))

    vol("6", r"Find the volume of the tetrahedron bounded by the coordinate planes and $\dfrac x2+\dfrac y3+\dfrac z4=1$.", 4 * (1 - x / 2 - y / 3), sp.Integer(0), 3 * (1 - x / 2), sp.Integer(0), sp.Integer(2),
        lambda a, b, c: a / 2 + b / 3 + c / 4 <= 1, (0, 2, 0, 3, 0, 4))
    vol("7", r"Find the volume of the solid in the first octant bounded by the coordinate planes and $2x+y+z=2$.", 2 - 2 * x - y, sp.Integer(0), 2 - 2 * x, sp.Integer(0), sp.Integer(1),
        lambda a, b, c: 2 * a + b + c <= 2, (0, 1, 0, 2, 0, 2))
    vol("8", r"Find the volume of the solid under the plane $z=4-x-y$ and above the square $0\le x\le1,\ 0\le y\le1$.", 4 - x - y, sp.Integer(0), sp.Integer(1), sp.Integer(0), sp.Integer(1),
        lambda a, b, c: c <= 4 - a - b, (0, 1, 0, 1, 0, 4))

    f = P("y")
    val = simp(sp.integrate(f, (z, 0, x * y), (y, 0, x), (x, 0, 1)))
    num_ok(val, grid3(lam3(f), lambda a, b, c: b <= a and c <= a * b, (0, 1, 0, 1, 0, 1), 50))
    items.append(ex(
        "mp-tr-9", r"$\displaystyle\iiint_Dy\,dV$, where $D:\ 0\le x\le1,\ 0\le y\le x,\ 0\le z\le xy$.", kind_of(val), eng(val),
        hints=[r"Integrate in $z$ first: the upper limit $xy$ depends on $x$ and $y$."],
        solution=r"$\displaystyle\int_0^1\!\!\int_0^x\!\!\int_0^{xy}y\,dz\,dy\,dx=\int_0^1\!\!\int_0^xxy^2\,dy\,dx=\int_0^1\dfrac{x^4}{3}\,dx=\dfrac1{15}$.",
    ))
    items.append(ex(
        "mp-tr-10", r"In how many different orders can a triple integral $\iiint f\,dx\,dy\,dz$ over a box be written as an iterated integral?", "multiple_choice", "3",
        choices=[{"text": "3", "value": "1"}, {"text": "4", "value": "2"}, {"text": "6", "value": "3"}, {"text": "9", "value": "4"}],
        correctIndex=2, hints=[r"Count the ways to order the three variables."], solution=r"The three variables can be ordered in $3!=6$ ways, and over a box all of them give the same value.",
    ))
    f = P("x+y+z")
    val = simp(sp.integrate(f, (z, 0, 1 - x - y), (y, 0, 1 - x), (x, 0, 1)))
    items.append(ex(
        "mp-tr-11", r"A solid tetrahedron $D$ (bounded by the coordinate planes and $x+y+z=1$) has density $\rho(x,y,z)=x+y+z$. Find its mass (give the number only, in kg).",
        kind_of(val), eng(val), hints=[r"$M=\iiint_D\rho\,dV$."], solution=rf"$M=\displaystyle\iiint_D(x+y+z)\,dV={tex(val)}$.",
    ))
    return items


# --- cylindrical and spherical coordinates ------------------------------------------------------------------------------------------------
def coordinate_items() -> list[dict]:
    items = []

    def cyl(i: str, stmt: str, integrand: sp.Expr, rlim, zlim, tlim, cart: sp.Expr, inside, bx: tuple, hint: str) -> None:
        val = simp(sp.integrate(integrand * r, (z, zlim[0], zlim[1]), (r, rlim[0], rlim[1]), (th, tlim[0], tlim[1])))
        num_ok(val, grid3(lam3(cart), inside, bx, 50))
        items.append(ex(
            f"mp-cs-{i}", stmt, kind_of(val), eng(val), hints=[hint],
            solution=rf"In cylindrical coordinates $dV=r\,dz\,dr\,d\theta$, and the integral is ${tex(val)}$.",
        ))

    cyl("1", r"Find the volume of the solid cylinder $x^2+y^2\le4$, $0\le z\le5$. The unit is cu: give the number only.", sp.Integer(1), (0, 2), (0, 5), (0, 2 * sp.pi), sp.Integer(1) + 0 * x,
        lambda a, b, c: a * a + b * b <= 4, (-2, 2, -2, 2, 0, 5), r"Use $0\le r\le2$, $0\le\theta\le2\pi$, $0\le z\le5$.")
    cyl("2", r"Find the volume of the solid between the paraboloid $z=x^2+y^2$ and the plane $z=4$. The unit is cu: give the number only.", sp.Integer(1), (0, 2), (r**2, 4), (0, 2 * sp.pi),
        sp.Integer(1) + 0 * x, lambda a, b, c: c >= a * a + b * b and c <= 4, (-2, 2, -2, 2, 0, 4), r"For a fixed $r$, $z$ runs from $r^2$ to $4$.")
    cyl("3", r"Find the volume of the cone $\sqrt{x^2+y^2}\le z\le3$. The unit is cu: give the number only.", sp.Integer(1), (0, 3), (r, 3), (0, 2 * sp.pi), sp.Integer(1) + 0 * x,
        lambda a, b, c: math.hypot(a, b) <= c <= 3, (-3, 3, -3, 3, 0, 3), r"The cone is $r\le z\le3$.")
    cyl("4", r"$\displaystyle\iiint_Dz\,dV$, where $D$ lies between $z=x^2+y^2$ and $z=4$.", z, (0, 2), (r**2, 4), (0, 2 * sp.pi), z,
        lambda a, b, c: c >= a * a + b * b and c <= 4, (-2, 2, -2, 2, 0, 4), r"Integrate $z$ from $r^2$ to $4$ first.")

    def sph(i: str, stmt: str, integrand: sp.Expr, rlim, plim, tlim, cart: sp.Expr, inside, bx: tuple, hint: str) -> None:
        val = simp(sp.integrate(integrand * rho**2 * sp.sin(ph), (rho, rlim[0], rlim[1]), (ph, plim[0], plim[1]), (th, tlim[0], tlim[1])))
        num_ok(val, grid3(lam3(cart), inside, bx, 50))
        items.append(ex(
            f"mp-cs-{i}", stmt, kind_of(val), eng(val), hints=[hint],
            solution=rf"In spherical coordinates $dV=\rho^2\sin\varphi\,d\rho\,d\varphi\,d\theta$, and the integral is ${tex(val)}$.",
        ))

    ball = lambda R: (lambda a, b, c: a * a + b * b + c * c <= R * R)  # noqa: E731
    sph("5", r"Find the volume of the ball $x^2+y^2+z^2\le9$. The unit is cu: give the number only.", sp.Integer(1), (0, 3), (0, sp.pi), (0, 2 * sp.pi), sp.Integer(1) + 0 * x, ball(3),
        (-3, 3, -3, 3, -3, 3), r"$0\le\rho\le3$, $0\le\varphi\le\pi$, $0\le\theta\le2\pi$.")
    sph("6", r"$\displaystyle\iiint_Dz\,dV$, where $D$ is the upper half of the unit ball ($x^2+y^2+z^2\le1$, $z\ge0$).", rho * sp.cos(ph), (0, 1), (0, sp.pi / 2), (0, 2 * sp.pi), z,
        lambda a, b, c: c >= 0 and a * a + b * b + c * c <= 1, (-1, 1, -1, 1, 0, 1), r"$z=\rho\cos\varphi$ and $0\le\varphi\le\dfrac\pi2$.")
    sph("7", r"$\displaystyle\iiint_D\left(x^2+y^2+z^2\right)dV$, where $D$ is the ball of radius $2$.", rho**2, (0, 2), (0, sp.pi), (0, 2 * sp.pi), P("x^2+y^2+z^2"), ball(2),
        (-2, 2, -2, 2, -2, 2), r"$x^2+y^2+z^2=\rho^2$.")
    sph("8", r"$\displaystyle\iiint_Dx^2\,dV$, where $D$ is the unit ball.", (rho * sp.sin(ph) * sp.cos(th)) ** 2, (0, 1), (0, sp.pi), (0, 2 * sp.pi), P("x^2"), ball(1),
        (-1, 1, -1, 1, -1, 1), r"$x=\rho\sin\varphi\cos\theta$.")
    sph("9", r"Find the mass of the unit ball whose density at each point is its distance from the origin (give the number only, in kg).", rho, (0, 1), (0, sp.pi), (0, 2 * sp.pi),
        P("sqrt(x^2+y^2+z^2)"), ball(1), (-1, 1, -1, 1, -1, 1), r"The density is $\rho$.")
    sph("10", r"Find the volume of the part of the unit ball inside the cone $z\ge\sqrt{x^2+y^2}$ (the 'ice-cream cone'). The unit is cu: give the number only.", sp.Integer(1), (0, 1), (0, sp.pi / 4), (0, 2 * sp.pi),
        sp.Integer(1) + 0 * x, lambda a, b, c: a * a + b * b + c * c <= 1 and c >= math.hypot(a, b), (-1, 1, -1, 1, 0, 1), r"The cone is $0\le\varphi\le\dfrac\pi4$.")

    # conversions
    items.append(ex(
        "mp-cs-11", r"Convert the point $(1,1,2)$ from rectangular to cylindrical coordinates $(r,\theta,z)$ with $r>0$ and $0\le\theta<2\pi$.", "vector", "(sqrt(2), pi/4, 2)",
        hints=[r"$r=\sqrt{x^2+y^2}$ and $\tan\theta=\dfrac yx$."], solution=r"$r=\sqrt{1+1}=\sqrt2$, $\theta=\dfrac\pi4$ (first quadrant), $z=2$.",
    ))
    items.append(ex(
        "mp-cs-12", r"Convert the point $(1,1,\sqrt2)$ to spherical coordinates $(\rho,\varphi,\theta)$ with $\rho>0$, $0\le\varphi\le\pi$, $0\le\theta<2\pi$.", "vector", "(2, pi/4, pi/4)",
        hints=[r"$\rho=\sqrt{x^2+y^2+z^2}$, $\cos\varphi=\dfrac z\rho$, $\tan\theta=\dfrac yx$."], solution=r"$\rho=\sqrt{1+1+2}=2$, $\cos\varphi=\dfrac{\sqrt2}{2}$ so $\varphi=\dfrac\pi4$, and $\theta=\dfrac\pi4$.",
    ))
    pt = [simp(2 * sp.sin(sp.pi / 2) * sp.cos(sp.pi / 3)), simp(2 * sp.sin(sp.pi / 2) * sp.sin(sp.pi / 3)), simp(2 * sp.cos(sp.pi / 2))]
    items.append(ex(
        "mp-cs-13", r"Convert the spherical point $(\rho,\varphi,\theta)=\left(2,\dfrac\pi2,\dfrac\pi3\right)$ to rectangular coordinates.", "vector", "(" + ", ".join(eng(c) for c in pt) + ")",
        hints=[r"$x=\rho\sin\varphi\cos\theta$, $y=\rho\sin\varphi\sin\theta$, $z=\rho\cos\varphi$."],
        solution=rf"$x=2\cdot1\cdot\dfrac12=1$, $y=2\cdot1\cdot\dfrac{{\sqrt3}}{{2}}=\sqrt3$, $z=2\cos\dfrac\pi2=0$: the point is $\left({', '.join(tex(c) for c in pt)}\right)$.",
    ))
    return items


# --- volumes --------------------------------------------------------------------------------------------------------------------------------
def volume_items() -> list[dict]:
    items = []

    def vol(i: str, stmt: str, val: sp.Expr, how: str, hint: str, check: float | None = None) -> None:
        if check is not None:
            num_ok(val, check)
        items.append(ex(f"mp-vo-{i}", stmt + " The unit is cu: give the number only.", kind_of(val), eng(val), hints=[hint], solution=how.replace("{V}", tex(val))))

    rr_ = r
    v1 = simp(sp.integrate((4 - r**2) * r, (r, 0, 2), (th, 0, 2 * sp.pi)))
    vol("1", r"Find the volume under the paraboloid $z=4-x^2-y^2$ and above the $xy$-plane.", v1, r"The paraboloid meets $z=0$ on $r=2$: $V=\displaystyle\int_0^{2\pi}\!\!\int_0^2(4-r^2)\,r\,dr\,d\theta={V}$.",
        r"Use polar coordinates over the disc $r\le2$.", grid3(lambda a, b, c: 1.0, lambda a, b, c: 0 <= c <= 4 - a * a - b * b, (-2, 2, -2, 2, 0, 4), 50))
    v2 = simp(sp.integrate((8 - 2 * r**2) * r, (r, 0, 2), (th, 0, 2 * sp.pi)))
    vol("2", r"Find the volume of the solid between the paraboloids $z=x^2+y^2$ and $z=8-x^2-y^2$.", v2,
        r"They meet where $r^2=8-r^2$, that is $r=2$. $V=\displaystyle\int_0^{2\pi}\!\!\int_0^2\left(8-2r^2\right)r\,dr\,d\theta={V}$.", r"Subtract the lower surface from the upper one over the disc where they meet.",
        grid3(lambda a, b, c: 1.0, lambda a, b, c: a * a + b * b <= c <= 8 - a * a - b * b, (-2, 2, -2, 2, 0, 8), 50))
    v3 = simp(sp.integrate(2 * sp.sqrt(4 - r**2) * r, (r, 0, 1), (th, 0, 2 * sp.pi)))
    vol("3", r"Find the volume of the part of the ball $x^2+y^2+z^2\le4$ inside the cylinder $x^2+y^2\le1$.", v3,
        r"For each $r\le1$, $z$ runs from $-\sqrt{4-r^2}$ to $\sqrt{4-r^2}$: $V=\displaystyle\int_0^{2\pi}\!\!\int_0^12\sqrt{4-r^2}\,r\,dr\,d\theta={V}$.", r"Use cylindrical coordinates.",
        grid3(lambda a, b, c: 1.0, lambda a, b, c: a * a + b * b <= 1 and a * a + b * b + c * c <= 4, (-1, 1, -1, 1, -2, 2), 50))
    v4 = simp(sp.integrate(1, (z, 0, (6 - x - 2 * y) / 3), (y, 0, (6 - x) / 2), (x, 0, 6)))
    vol("4", r"Find the volume of the tetrahedron bounded by the coordinate planes and $x+2y+3z=6$.", v4, r"$V=\displaystyle\int_0^6\!\!\int_0^{(6-x)/2}\dfrac{6-x-2y}{3}\,dy\,dx={V}$.",
        r"The base is the triangle $x+2y\le6$ in the $xy$-plane.", grid3(lambda a, b, c: 1.0, lambda a, b, c: a + 2 * b + 3 * c <= 6, (0, 6, 0, 3, 0, 2), 50))
    v5 = simp(sp.integrate(x + y, (y, 0, x), (x, 0, 1)))
    vol("5", r"Find the volume under the plane $z=x+y$ above the triangle $0\le y\le x\le1$.", v5, r"$V=\displaystyle\int_0^1\!\!\int_0^x(x+y)\,dy\,dx={V}$.", r"The base triangle is $0\le x\le1$, $0\le y\le x$.",
        grid3(lambda a, b, c: 1.0, lambda a, b, c: b <= a and 0 <= c <= a + b, (0, 1, 0, 1, 0, 2), 50))
    v6 = simp(sp.integrate(sp.integrate(y, (y, 0, sp.sqrt(x))), (x, 0, 1)))
    vol("6", r"Find the volume under the surface $z=y$ above the region $0\le x\le1$, $0\le y\le\sqrt x$.", v6, r"$V=\displaystyle\int_0^1\!\!\int_0^{\sqrt x}y\,dy\,dx={V}$.", r"Integrate $z=y$ over the base region.",
        grid3(lambda a, b, c: 1.0, lambda a, b, c: b <= math.sqrt(a) and 0 <= c <= b, (0, 1, 0, 1, 0, 1), 50))
    v7 = simp(sp.integrate(sp.sin(ph) * rho**2, (rho, 0, 1), (ph, 0, sp.pi / 4), (th, 0, 2 * sp.pi)))
    vol("7", r"Find the volume of the solid above the cone $z=\sqrt{x^2+y^2}$ and inside the unit sphere.", v7, r"In spherical coordinates the solid is $0\le\rho\le1$, $0\le\varphi\le\dfrac\pi4$: $V={V}$.",
        r"The cone is $\varphi=\dfrac\pi4$.", grid3(lambda a, b, c: 1.0, lambda a, b, c: a * a + b * b + c * c <= 1 and c >= math.hypot(a, b), (-1, 1, -1, 1, 0, 1), 50))
    v8 = simp(sp.Rational(4, 3) * sp.pi * 2 * 3 * 1)
    vol("8", r"Find the volume of the ellipsoid $\dfrac{x^2}{4}+\dfrac{y^2}{9}+z^2\le1$.", v8,
        r"With $x=2u$, $y=3v$, $z=w$ the ellipsoid becomes the unit ball and $dV=6\,du\,dv\,dw$: $V=6\cdot\dfrac{4\pi}{3}={V}$.", r"Use the substitution $x=2u$, $y=3v$, $z=w$ (Jacobian $6$).",
        grid3(lambda a, b, c: 1.0, lambda a, b, c: a * a / 4 + b * b / 9 + c * c <= 1, (-2, 2, -3, 3, -1, 1), 50))
    v9 = simp(sp.integrate(sp.integrate(1 - y**2, (y, -1, 1)) * 3, (x, 0, 1)) / 1)
    v9 = simp(3 * sp.integrate(1 - y**2, (y, -1, 1)))
    vol("9", r"Find the volume of the solid $0\le x\le3$, $0\le z\le1-y^2$, $-1\le y\le1$.", v9, r"$V=3\displaystyle\int_{-1}^{1}\left(1-y^2\right)dy={V}$.", r"The cross-section does not depend on $x$.",
        grid3(lambda a, b, c: 1.0, lambda a, b, c: 0 <= c <= 1 - b * b, (0, 3, -1, 1, 0, 1), 50))
    v10 = simp(sp.integrate(sp.integrate((2 * r * sp.cos(th) - r**2) * r, (r, 0, 2 * sp.cos(th))), (th, -sp.pi / 2, sp.pi / 2)))
    vol("10", r"Find the volume of the solid between the paraboloid $z=x^2+y^2$ and the plane $z=2x$.", v10,
        r"They meet above the circle $x^2+y^2=2x$, that is $r=2\cos\theta$. $V=\displaystyle\int_{-\pi/2}^{\pi/2}\!\!\int_0^{2\cos\theta}\left(2r\cos\theta-r^2\right)r\,dr\,d\theta={V}$.",
        r"The plane is above the paraboloid over the disc $(x-1)^2+y^2\le1$.", grid2(lambda a, b: max(0.0, 2 * a - a * a - b * b), lambda a, b: True, (0, 2, -1, 1), 800))
    v11 = simp(sp.integrate((5 + r * sp.cos(th)) * r, (r, 0, 2), (th, 0, 2 * sp.pi)))
    vol("11", r"Find the volume of the solid inside the cylinder $x^2+y^2\le4$ between the planes $z=0$ and $z=5+x$.", v11,
        r"$V=\displaystyle\int_0^{2\pi}\!\!\int_0^2(5+r\cos\theta)\,r\,dr\,d\theta={V}$ (the term with $\cos\theta$ integrates to $0$).", r"Use polar coordinates for the base disc.",
        grid3(lambda a, b, c: 1.0, lambda a, b, c: a * a + b * b <= 4 and 0 <= c <= 5 + a, (-2, 2, -2, 2, 0, 7), 50))
    v12 = simp(sp.integrate(sp.integrate(sp.integrate(r, (z, 0, 4 * (1 - r / 3))), (r, 0, 3)), (th, 0, 2 * sp.pi)))
    vol("12", r"Find the volume of the cone with base radius $3$ and height $4$.", v12, r"With the apex up: $0\le z\le4\left(1-\dfrac r3\right)$, so $V=\displaystyle\int_0^{2\pi}\!\!\int_0^3 4\left(1-\dfrac r3\right)r\,dr\,d\theta={V}$ $\left(=\dfrac13\pi r^2h\right)$.",
        r"Use cylindrical coordinates, or the formula $\dfrac13\pi r^2h$ to check.", grid3(lambda a, b, c: 1.0, lambda a, b, c: 0 <= c <= 4 * (1 - math.hypot(a, b) / 3), (-3, 3, -3, 3, 0, 4), 50))
    items.append(ex(
        "mp-vo-13", r"Which coordinate system is the most convenient for the volume of the part of a ball above a cone with the same vertex at its centre?", "multiple_choice", "3",
        choices=[{"text": "Rectangular", "value": "1"}, {"text": "Cylindrical", "value": "2"}, {"text": "Spherical", "value": "3"}],
        correctIndex=2, hints=[r"Both the ball and the cone are very simple in $\rho$ and $\varphi$."],
        solution=r"In spherical coordinates the ball is $\rho\le R$ and the cone is $\varphi\le\alpha$, so the limits are constants.",
    ))
    assert rr_ is r
    return items


def register() -> None:
    f1 = "Type an exact value such as `7/6` or `e-1`."
    add_extra(f"{M2}/u01-over-regions/l01-iterated-integrals", exset_plain("more-iterated", "More practice: iterated integrals.", iterated_items(), format=f1), SCRIPT)
    add_extra(f"{M2}/u02-polar-and-change-of-variables/l01-polar-coordinates", exset_plain("more-polar", "More practice: polar coordinates.", polar_items(), format="Type an exact value such as `3*pi/4`."), SCRIPT)
    add_extra(f"{M2}/u02-polar-and-change-of-variables/l02-jacobian",
              exset_plain("more-jacobian", "More practice: the Jacobian.", jacobian_items(), format="Type an expression in u and v, or an exact value such as `-7`."), SCRIPT)
    add_extra(f"{M2}/u03-applications/l01-area", exset_plain("more-area", "More practice: areas between curves.", area_items(), format="Type an exact value such as `11/6` or `e-2`."), SCRIPT)
    add_extra(f"{M3}/u01-cartesian/l01-triple-integrals", exset_plain("more-triple", "More practice: triple integrals.", triple_items(), format="Type an exact value such as `7/8`."), SCRIPT)
    add_extra(f"{M3}/u02-cylindrical-and-spherical/l01-cylindrical-and-spherical",
              exset_plain("more-coordinates", "More practice: cylindrical and spherical coordinates.", coordinate_items(),
                          format="Type an exact value such as `3*pi/5`, or a triple such as `(2, pi/6, 1)`."), SCRIPT)
    add_extra(f"{M3}/u03-volumes/l01-volumes", exset_plain("more-volumes", "More practice: volumes.", volume_items(), format="Type an exact value such as `7*pi/6`."), SCRIPT)
