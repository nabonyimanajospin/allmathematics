"""Exercises of Course 2, Module 2: double integrals, polar coordinates, Jacobian, areas (sheet part B.I and B.II)."""

from __future__ import annotations

import mpmath as mp
import sympy as sp
from toolkit import eng, ex, exset, numeric_double, same_number, tex, write_exercises, x, y, with_units

BASE = "mvc/m02-double-integrals"
a, b = sp.symbols("a b", positive=True)
th, rr = sp.symbols("theta r", real=True)
mp.mp.dps = 25


def iterated(f: sp.Expr, inner: tuple, outer: tuple) -> sp.Expr:
    """∫_outer ∫_inner f, exact. inner = (var, lo, hi), outer = (var, lo, hi)."""
    g = sp.integrate(f, inner)
    return sp.simplify(sp.integrate(sp.simplify(g), outer))


def dtex(e: sp.Expr) -> str:
    return tex(e, True)


# --- B.I double integrals ------------------------------------------------------------------------------------
def cartesian_items() -> list[dict]:
    items: list[dict] = []

    # 1: improper but convergent
    f = 1 / sp.sqrt((1 - x**2) * (1 - y**2))
    val = (sp.pi / 2) ** 2
    num = float(mp.quad(lambda xv: mp.quad(lambda yv: 1 / mp.sqrt((1 - xv**2) * (1 - yv**2)), [0, 1]), [0, 1]))
    assert same_number(val, num, 1e-6), (val, num)
    items.append(ex(
        "dbl-01", r"$\displaystyle\iint_D\frac{dx\,dy}{\sqrt{(1-x^2)(1-y^2)}}$, $\ D:\ 0\le x\le1,\ 0\le y\le1$", "expression", eng(sp.expand(val)),
        hints=["The integrand is a product of a function of $x$ and a function of $y$ over a rectangle."],
        solution=(
            r"Over a rectangle, a product of a function of $x$ and a function of $y$ integrates as a product:" + "\n\n"
            r"$$\iint_D=\int_0^1\frac{dx}{\sqrt{1-x^2}}\cdot\int_0^1\frac{dy}{\sqrt{1-y^2}}=\left(\arcsin x\Big|_0^1\right)^2=\left(\frac\pi2\right)^2=\frac{\pi^2}{4}.$$" + "\n\n"
            r"The integrand is unbounded near $x=1$ and $y=1$, but each factor is an integrable (improper) integral, so the double integral converges."
        ),
        verify=[{"expr": "integrate(1/sqrt(1-x^2), x, 0, 1)", "equals": "pi/2"}],
    ))

    # 2: diverges
    inner = sp.integrate(1 / (x**2 + y**2), (y, 0, x))
    assert sp.simplify(inner - sp.pi / (4 * x)) == 0
    items.append(ex(
        "dbl-02", r"$\displaystyle\iint_D\frac{dx\,dy}{x^2+y^2}$, $\ D:\ 0\le x\le2,\ 0\le y\le x$", "number", "@dne",
        hints=["Integrate in $y$ first, then look carefully at what is left in $x$ near $0$."],
        solution=(
            r"Inner integral: $\displaystyle\int_0^x\frac{dy}{x^2+y^2}=\frac1x\arctan\frac yx\Big|_0^x=\frac{\pi}{4x}$." + "\n\n"
            r"Outer integral: $\displaystyle\int_0^2\frac{\pi}{4x}\,dx=\frac\pi4\ln x\Big|_0^2$, which is infinite because $\ln x\to-\infty$ as $x\to0^+$." + "\n\n"
            "The integral **diverges**: it has no finite value. The integrand is not bounded near the origin, which is a corner of $D$."
        ),
        verify=[{"expr": "integrate(1/(x^2+y^2), y, 0, x)", "equals": "pi/(4*x)"}],
        note="This exercise has a trap: it looks like a routine iterated integral, but it does not converge. Answer with `diverges`.",
    ))

    # 3
    f = x**2 + y**2
    val = iterated(f, (y, x, sp.sqrt(x)), (x, 0, 1))
    assert same_number(val, numeric_double(f, x, sp.sqrt(x), 0, 1))
    inner_expr = sp.simplify(sp.integrate(f, (y, x, sp.sqrt(x))))
    items.append(ex(
        "dbl-03", r"$\displaystyle\iint_D(x^2+y^2)\,dx\,dy$, $\ D:\ 0\le x\le1,\ x\le y\le\sqrt x$", "number", eng(val),
        hints=["Integrate in $y$ from $x$ to $\\sqrt x$ first; the result is a function of $x$."],
        solution=(
            rf"Inner integral: $\displaystyle\int_x^{{\sqrt x}}(x^2+y^2)\,dy=\left[x^2y+\dfrac{{y^3}}{{3}}\right]_x^{{\sqrt x}}={tex(inner_expr)}$." + "\n\n"
            rf"Outer integral: $\displaystyle\int_0^1\left({tex(inner_expr)}\right)dx={tex(val)}$."
        ),
        verify=[{"expr": "integrate(integrate(x^2+y^2, y, x, sqrt(x)), x, 0, 1)", "equals": eng(val)}],
    ))

    # 6: region between y = 2 - x^2 and y = 2x - 1
    xs = sp.solve(sp.Eq(2 - x**2, 2 * x - 1), x)
    assert sorted(xs) == [-3, 1]
    f = x - y
    val = iterated(f, (y, 2 * x - 1, 2 - x**2), (x, -3, 1))
    assert same_number(val, numeric_double(f, 2 * x - 1, 2 - x**2, -3, 1))
    inner_expr = sp.expand(sp.integrate(f, (y, 2 * x - 1, 2 - x**2)))
    items.append(ex(
        "dbl-04", r"$\displaystyle\iint_D(x-y)\,dx\,dy$, $\ D$ bounded by $y=2-x^2$ and $y=2x-1$", "number", eng(val),
        hints=["Find where the parabola and the line meet. On the region, the parabola is above the line."],
        solution=(
            r"The curves meet where $2-x^2=2x-1$, that is $x^2+2x-3=0$, so $x=-3$ or $x=1$. Between them the parabola is above the line, so "
            r"$D:\ -3\le x\le1,\ 2x-1\le y\le2-x^2$." + "\n\n"
            rf"Inner integral: $\displaystyle\int_{{2x-1}}^{{2-x^2}}(x-y)\,dy={tex(inner_expr)}$." + "\n\n"
            rf"Outer integral: $\displaystyle\int_{{-3}}^{{1}}\left({tex(inner_expr)}\right)dx={tex(val)}$."
        ),
        verify=[{"expr": "integrate(integrate(x-y, y, 2*x-1, 2-x^2), x, -3, 1)", "equals": eng(val)}],
    ))

    # 7: sin(x+y), triangle x = 0, y = pi/2, y = x
    f = sp.sin(x + y)
    val = iterated(f, (y, x, sp.pi / 2), (x, 0, sp.pi / 2))
    assert same_number(val, numeric_double(f, x, sp.pi / 2, 0, float(sp.pi / 2)))
    inner_expr = sp.simplify(sp.integrate(f, (y, x, sp.pi / 2)))
    items.append(ex(
        "dbl-05", r"$\displaystyle\iint_D\sin(x+y)\,dx\,dy$, $\ D$ bounded by $x=0$, $y=\dfrac\pi2$, $y=x$", "number", eng(val),
        hints=["$D$ is the triangle with vertices $(0,0)$, $\\left(0,\\frac\\pi2\\right)$, $\\left(\\frac\\pi2,\\frac\\pi2\\right)$: $0\\le x\\le\\dfrac\\pi2$, $x\\le y\\le\\dfrac\\pi2$."],
        solution=(
            r"The region is the triangle $0\le x\le\dfrac\pi2$, $x\le y\le\dfrac\pi2$." + "\n\n"
            rf"Inner integral: $\displaystyle\int_x^{{\pi/2}}\sin(x+y)\,dy={tex(inner_expr)}$." + "\n\n"
            rf"Outer integral: $\displaystyle\int_0^{{\pi/2}}\left({tex(inner_expr)}\right)dx={tex(val)}$."
        ),
        verify=[{"expr": "integrate(integrate(sin(x+y), y, x, pi/2), x, 0, pi/2)", "equals": eng(val)}],
    ))

    # 8: x over the triangle A(2,3), B(7,2), C(4,5): area * x-coordinate of the centroid
    A, B, C = (2, 3), (7, 2), (4, 5)
    area = sp.Rational(abs((B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])), 2)
    val = area * sp.Rational(A[0] + B[0] + C[0], 3)
    # independent check by splitting into two integrals over x
    # lower boundary: A->B for x in [2,7]? B has the smallest y; use the three edges
    def edge(P, Q):
        return lambda xv: P[1] + (Q[1] - P[1]) * (xv - P[0]) / (Q[0] - P[0])

    ab, bc, ac = edge(A, B), edge(B, C), edge(A, C)
    num = float(mp.quad(lambda xv: xv * (ac(xv) - ab(xv)), [2, 4]) + mp.quad(lambda xv: xv * (bc(xv) - ab(xv)), [4, 7]))
    # the upper boundary is A->C for x in [2,4] and C->B for x in [4,7]; lower boundary is A->B
    assert same_number(val, num), (val, num)
    items.append(ex(
        "dbl-06", r"$\displaystyle\iint_D x\,dx\,dy$, $\ D$ the triangle $ABC$ with $A(2,3)$, $B(7,2)$, $C(4,5)$", "number", eng(val),
        hints=["For $f=x$, $\\iint_D x\\,dA=(\\text{area of }D)\\cdot(x\\text{-coordinate of the centroid})$. Or split $D$ at $x=4$."],
        solution=(
            r"Use the centroid: for $f=x$, $\iint_D x\,dA=\text{area}(D)\cdot\bar x$, where $\bar x$ is the $x$-coordinate of the centroid." + "\n\n"
            rf"Area: $\dfrac12\left|\crossp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}\right|$ with $\overrightarrow{{AB}}=(5,-1)$ and $\overrightarrow{{AC}}=(2,2)$ "
            rf"gives $\dfrac12|5\cdot2-(-1)\cdot2|={tex(area)}$. "
            rf"Centroid: $\bar x=\dfrac{{2+7+4}}3=\dfrac{{13}}3$. Therefore $\iint_Dx\,dA={tex(area)}\cdot\dfrac{{13}}3={tex(val)}$."
        ),
    ))
    return items


# --- B.I polar -------------------------------------------------------------------------------------------------
def polar_items() -> list[dict]:
    items: list[dict] = []

    # 4: ∫0^{2π} ∫_{a sinθ}^{a} r dr dθ
    val = sp.simplify(sp.integrate(sp.integrate(rr, (rr, a * sp.sin(th), a)), (th, 0, 2 * sp.pi)))
    assert sp.simplify(val - sp.pi * a**2 / 2) == 0
    items.append(ex(
        "pol-01", r"$\displaystyle\iint_Dr\,dr\,d\theta$, $\ D:\ 0\le\theta\le2\pi,\ a\sin\theta\le r\le a$ (with $a>0$)", "expression", eng(val),
        variables=["a"],
        hints=["Integrate in $r$ first: $\\int_{a\\sin\\theta}^{a}r\\,dr=\\dfrac{a^2-a^2\\sin^2\\theta}{2}$."],
        solution=(
            r"Inner integral: $\displaystyle\int_{a\sin\theta}^{a}r\,dr=\frac{a^2-a^2\sin^2\theta}{2}=\frac{a^2\cos^2\theta}{2}$." + "\n\n"
            r"Outer integral: $\displaystyle\int_0^{2\pi}\frac{a^2\cos^2\theta}{2}\,d\theta=\frac{a^2}{2}\cdot\pi=\frac{\pi a^2}{2}$, because $\int_0^{2\pi}\cos^2\theta\,d\theta=\pi$."
        ),
        verify=[{"expr": "integrate(integrate(r, r, a*sin(t), a), t, 0, 2*pi)", "equals": "pi*a^2/2"}],
    ))

    # 5: ∬ r^2 sin^2θ dr dθ, −π/2 ≤ θ ≤ π/2, 0 ≤ r ≤ 3 cos θ
    lit = sp.simplify(sp.integrate(sp.integrate(rr**2 * sp.sin(th) ** 2, (rr, 0, 3 * sp.cos(th))), (th, -sp.pi / 2, sp.pi / 2)))
    jac = sp.simplify(sp.integrate(sp.integrate(rr**3 * sp.sin(th) ** 2, (rr, 0, 3 * sp.cos(th))), (th, -sp.pi / 2, sp.pi / 2)))
    assert lit == sp.Rational(12, 5) and sp.simplify(jac - 81 * sp.pi / 64) == 0
    items.append(ex(
        "pol-02", r"$\displaystyle\iint_Dr^2\sin^2\theta\,dr\,d\theta$, $\ D:\ -\dfrac\pi2\le\theta\le\dfrac\pi2,\ 0\le r\le3\cos\theta$", "number", eng(lit),
        hints=["Integrate in $r$ first: $\\int_0^{3\\cos\\theta}r^2\\,dr=9\\cos^3\\theta$. Then use $\\sin^2\\theta\\cos^3\\theta=\\sin^2\\theta(1-\\sin^2\\theta)\\cos\\theta$."],
        solution=(
            r"Inner integral: $\displaystyle\int_0^{3\cos\theta}r^2\,dr=\frac{(3\cos\theta)^3}{3}=9\cos^3\theta$." + "\n\n"
            r"Outer integral: $\displaystyle9\int_{-\pi/2}^{\pi/2}\sin^2\theta\cos^3\theta\,d\theta$. With $s=\sin\theta$ and $ds=\cos\theta\,d\theta$, "
            r"$\cos^2\theta=1-s^2$, this is $9\int_{-1}^{1}s^2(1-s^2)\,ds=9\left(\dfrac23-\dfrac25\right)=\dfrac{12}{5}$."
        ),
        note=(
            "The integrand is taken exactly as printed, $r^2\\sin^2\\theta$ with $dr\\,d\\theta$. If the intended integral was "
            "$\\iint y^2\\,dA$ in polar coordinates, the area element $r\\,dr\\,d\\theta$ adds a factor $r$, and the value would be "
            "$\\dfrac{81\\pi}{64}$."
        ),
    ))

    # 9: ∬ sqrt(x²+y²) over the quarter disc x²+y² ≤ a², x, y ≥ 0
    val = sp.simplify(sp.integrate(sp.integrate(rr * rr, (rr, 0, a)), (th, 0, sp.pi / 2)))
    assert sp.simplify(val - sp.pi * a**3 / 6) == 0
    items.append(ex(
        "pol-03", r"$\displaystyle\iint_D\sqrt{x^2+y^2}\,dx\,dy$, $\ D:\ x^2+y^2\le a^2,\ x\ge0,\ y\ge0$ (with $a>0$)", "expression", eng(val),
        variables=["a"],
        hints=["Use polar coordinates: $0\\le r\\le a$, $0\\le\\theta\\le\\dfrac\\pi2$, $\\sqrt{x^2+y^2}=r$, $dA=r\\,dr\\,d\\theta$."],
        solution=(
            r"The region is a quarter of a disc: $0\le r\le a$, $0\le\theta\le\dfrac\pi2$. With $\sqrt{x^2+y^2}=r$ and $dx\,dy=r\,dr\,d\theta$:" + "\n\n"
            r"$$\int_0^{\pi/2}\int_0^{a}r\cdot r\,dr\,d\theta=\frac\pi2\cdot\frac{a^3}{3}=\frac{\pi a^3}{6}.$$"
        ),
        verify=[{"expr": "integrate(integrate(r*r, r, 0, a), t, 0, pi/2)", "equals": "pi*a^3/6"}],
    ))
    return items


def jacobian_items() -> list[dict]:
    u, v = sp.symbols("u v", real=True)
    f = u**3 * v**2
    val = sp.integrate(sp.integrate(f * sp.Rational(1, 2), (v, -1, 1)), (u, 1, 3))
    assert val == sp.Rational(20, 3)
    # independent audit in the original coordinates: the parallelogram with vertices (1,0), (2,1), (1,2), (0,1)
    num = float(
        mp.quad(
            lambda xv: mp.quad(lambda yv: (xv + yv) ** 3 * (xv - yv) ** 2, [abs(xv - 1), 2 - abs(xv - 1)]), [0, 1, 2]
        )
    )
    assert same_number(val, num), (val, num)
    return [ex(
        "jac-01", r"$\displaystyle\iint_D(x+y)^3(x-y)^2\,dx\,dy$, $\ D$ bounded by $x+y=1$, $x-y=1$, $x+y=3$, $x-y=-1$", "number", eng(val),
        hints=["Put $u=x+y$ and $v=x-y$. Then $D$ becomes a rectangle, and $dx\\,dy=\\dfrac12\\,du\\,dv$."],
        solution=(
            r"Let $u=x+y$ and $v=x-y$. The region is $1\le u\le3$ and $-1\le v\le1$, a rectangle. Since $x=\dfrac{u+v}2$ and $y=\dfrac{u-v}2$, "
            r"$\left|\dfrac{\partial(x,y)}{\partial(u,v)}\right|=\dfrac12$, so $dx\,dy=\dfrac12\,du\,dv$." + "\n\n"
            r"$$\iint_D=\frac12\int_1^3u^3\,du\int_{-1}^{1}v^2\,dv=\frac12\cdot\frac{81-1}{4}\cdot\frac23=\frac{20}{3}.$$"
        ),
        verify=[{"expr": "integrate(integrate(u^3*v^2/2, v, -1, 1), u, 1, 3)", "equals": "20/3"}],
    )]


# --- B.II areas ------------------------------------------------------------------------------------------------
def area_items() -> list[dict]:
    items: list[dict] = []

    def between_x(id_, latex, eqs_latex, lo_expr, hi_expr, y_lo, y_hi, hint, extra: str = ""):
        """Area with x between lo and hi (functions of y)."""
        val = sp.simplify(sp.integrate(sp.integrate(1, (x, lo_expr, hi_expr)), (y, y_lo, y_hi)))
        return val

    # 1: x = 4y - y^2 and x + y = 6   (right boundary x = 4y - y^2, left x = 6 - y, y in [2, 3])
    val = sp.integrate((4 * y - y**2) - (6 - y), (y, 2, 3))
    assert val == sp.Rational(1, 6)
    num = float(mp.quad(lambda yv: (4 * yv - yv**2) - (6 - yv), [2, 3]))
    assert same_number(val, num)
    items.append(ex(
        "are-01", r"The area bounded by $x=4y-y^2$ and $x+y=6$.", "number", eng(val),
        hints=["Find the intersections: $4y-y^2=6-y$. Then see which curve is to the right between them."],
        solution=(
            r"Intersections: $4y-y^2=6-y$ gives $y^2-5y+6=0$, so $y=2$ or $y=3$. For $2<y<3$ the parabola $x=4y-y^2$ is to the right of the line $x=6-y$ "
            r"(at $y=\tfrac52$ for example, $\tfrac{15}4>\tfrac72$). Integrate in $x$ first:" + "\n\n"
            r"$$A=\int_2^3\int_{6-y}^{4y-y^2}dx\,dy=\int_2^3(-y^2+5y-6)\,dy=\frac16.$$"
        ),
        verify=[{"expr": "integrate(integrate(1, x, 6-y, 4*y-y^2), y, 2, 3)", "equals": "1/6"}],
    ))

    # 2: x = y^2 - 2y and x + y = 0  -> y in [0,1], right x = -y, left x = y^2 - 2y
    val = sp.integrate(-y - (y**2 - 2 * y), (y, 0, 1))
    assert val == sp.Rational(1, 6)
    items.append(ex(
        "are-02", r"The area bounded by $x=y^2-2y$ and $x+y=0$.", "number", eng(val),
        hints=["The intersections satisfy $y^2-2y=-y$."],
        solution=(
            r"Intersections: $y^2-2y=-y$ gives $y^2-y=0$, so $y=0$ or $y=1$. For $0<y<1$ the line $x=-y$ is to the right of the parabola "
            r"(at $y=\tfrac12$: $-\tfrac12>-\tfrac34$). Then" + "\n\n"
            r"$$A=\int_0^1\big(-y-(y^2-2y)\big)\,dy=\int_0^1(y-y^2)\,dy=\frac12-\frac13=\frac16.$$"
        ),
        verify=[{"expr": "integrate(integrate(1, x, y^2-2*y, -y), y, 0, 1)", "equals": "1/6"}],
    ))

    # 3: y^2 = 4x and x^2 = 4y
    val = sp.integrate(2 * sp.sqrt(x) - x**2 / 4, (x, 0, 4))
    assert val == sp.Rational(16, 3)
    items.append(ex(
        "are-03", r"The area bounded by $y^2=4x$ and $x^2=4y$.", "number", eng(val),
        hints=["The curves meet at $(0,0)$ and $(4,4)$. Write them as $y=2\\sqrt x$ and $y=\\dfrac{x^2}{4}$."],
        solution=(
            r"The curves meet at $(0,0)$ and $(4,4)$. For $0<x<4$ the curve $y=2\sqrt x$ is above $y=\dfrac{x^2}{4}$. Then" + "\n\n"
            r"$$A=\int_0^4\left(2\sqrt x-\frac{x^2}{4}\right)dx=\left[\frac43x^{3/2}-\frac{x^3}{12}\right]_0^4=\frac{32}{3}-\frac{16}{3}=\frac{16}{3}.$$"
        ),
        verify=[{"expr": "integrate(integrate(1, y, x^2/4, 2*sqrt(x)), x, 0, 4)", "equals": "16/3"}],
    ))

    # 4: x = 4 - y^2 and x + 2y = 4
    val = sp.integrate((4 - y**2) - (4 - 2 * y), (y, 0, 2))
    assert val == sp.Rational(4, 3)
    items.append(ex(
        "are-04", r"The area bounded by $x=4-y^2$ and $x+2y=4$.", "number", eng(val),
        hints=["Intersections: $4-y^2=4-2y$. Integrate in $x$ first."],
        solution=(
            r"Intersections: $4-y^2=4-2y$ gives $y^2-2y=0$, so $y=0$ or $y=2$. For $0<y<2$ the parabola is to the right of the line "
            r"(at $y=1$: $3>2$). Then" + "\n\n"
            r"$$A=\int_0^2\big((4-y^2)-(4-2y)\big)\,dy=\int_0^2(2y-y^2)\,dy=4-\frac83=\frac43.$$"
        ),
        verify=[{"expr": "integrate(integrate(1, x, 4-2*y, 4-y^2), y, 0, 2)", "equals": "4/3"}],
        note="On the printed sheet this exercise is numbered 3 a second time; the numbering here continues from the previous exercise.",
    ))

    # 5: circle x^2 + y^2 = 4 (polar)
    val = sp.integrate(sp.integrate(rr, (rr, 0, 2)), (th, 0, 2 * sp.pi))
    assert val == 4 * sp.pi
    items.append(ex(
        "are-05", r"The area bounded by $x^2+y^2=4$.", "expression", eng(val),
        hints=["Use polar coordinates: $0\\le r\\le2$, $0\\le\\theta\\le2\\pi$."],
        solution=r"In polar coordinates the disc is $0\le r\le2$, $0\le\theta\le2\pi$: $A=\displaystyle\int_0^{2\pi}\int_0^2r\,dr\,d\theta=2\pi\cdot2=4\pi$. (This is $\pi R^2$ with $R=2$.)",
        verify=[{"expr": "integrate(integrate(r, r, 0, 2), t, 0, 2*pi)", "equals": "4*pi"}],
    ))

    # 6: ellipse x^2/a^2 + y^2/b^2 = 1, area pi a b (change of variables x = a r cos t, y = b r sin t, J = a b r)
    val = sp.integrate(sp.integrate(a * b * rr, (rr, 0, 1)), (th, 0, 2 * sp.pi))
    assert sp.simplify(val - sp.pi * a * b) == 0
    items.append(ex(
        "are-06", r"The area bounded by the ellipse $\dfrac{x^2}{a^2}+\dfrac{y^2}{b^2}=1$ (with $a,b>0$).", "expression", eng(val),
        variables=["a", "b"],
        hints=["Stretch the polar coordinates: $x=ar\\cos\\theta$, $y=br\\sin\\theta$. The Jacobian is $abr$."],
        solution=(
            r"Put $x=ar\cos\theta$ and $y=br\sin\theta$. The ellipse is $r=1$ and the disc is $0\le r\le1$, $0\le\theta\le2\pi$. "
            r"The Jacobian is $\left|\begin{matrix}a\cos\theta&-ar\sin\theta\\b\sin\theta&br\cos\theta\end{matrix}\right|=abr$. Then" + "\n\n"
            r"$$A=\int_0^{2\pi}\int_0^1abr\,dr\,d\theta=ab\cdot\frac12\cdot2\pi=\pi ab.$$"
        ),
        verify=[{"expr": "integrate(integrate(a*b*r, r, 0, 1), t, 0, 2*pi)", "equals": "pi*a*b"}],
        note="On the printed sheet this exercise is numbered 5; the numbering here continues from the previous exercise.",
    ))
    return items


@with_units
def build() -> None:
    write_exercises(
        f"{BASE}/u01-over-regions/l01-iterated-integrals",
        [exset("double-integrals", "Evaluate the following double integrals.", cartesian_items(),
               format="Type an exact value such as `2/9` or `pi/8`. If the integral does not converge, type `diverges`.")],
        "mvc_m02.py",
    )
    write_exercises(
        f"{BASE}/u02-polar-and-change-of-variables/l01-polar-coordinates",
        [exset("polar", "Evaluate the following double integrals in polar coordinates.", polar_items(),
               format="Type an exact expression such as `a^3/6`.")],
        "mvc_m02.py",
    )
    write_exercises(
        f"{BASE}/u02-polar-and-change-of-variables/l02-jacobian",
        [exset("jacobian", "Evaluate with a change of variables.", jacobian_items(), format="Type an exact value.")],
        "mvc_m02.py",
    )
    write_exercises(
        f"{BASE}/u03-applications/l01-area",
        [exset("areas", "Find the area bounded by the given curves.", area_items(), format="Type an exact value such as `5/6` or `pi*r^2`.")],
        "mvc_m02.py",
    )
