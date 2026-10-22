"""Exercises of Course 2, Module 3: triple integrals and volumes (sheet parts B.III and B.IV)."""

from __future__ import annotations

import mpmath as mp
import sympy as sp
from toolkit import eng, ex, exset, same_number, tex, write_exercises, x, y, z

BASE = "mvc/m03-triple-integrals"
a, b, R = sp.symbols("a b R", positive=True)
rho, phi, th = sp.symbols("rho varphi theta", real=True)
mp.mp.dps = 15


def triple(f: sp.Expr, zr: tuple, yr: tuple, xr: tuple) -> sp.Expr:
    """∫_x ∫_y ∫_z f, innermost first; each range is (var, lo, hi)."""
    g = sp.integrate(f, zr)
    g = sp.integrate(sp.simplify(g), yr)
    return sp.simplify(sp.integrate(sp.simplify(g), xr))


def cartesian_items() -> list[dict]:
    items: list[dict] = []

    # 1: unit cube
    f = x**2 + y**2 + z**2
    val = triple(f, (z, 0, 1), (y, 0, 1), (x, 0, 1))
    assert val == 1
    items.append(ex(
        "tri-01", r"$\displaystyle\iiint_D(x^2+y^2+z^2)\,dx\,dy\,dz$, $\ D:\ 0\le x\le1,\ 0\le y\le1,\ 0\le z\le1$", "number", eng(val),
        hints=["Integrate each of the three terms separately: by symmetry they give the same value."],
        solution=(
            r"Each term gives the same integral: $\displaystyle\iiint x^2\,dV=\int_0^1x^2\,dx\cdot\int_0^1dy\cdot\int_0^1dz=\frac13$. "
            r"The same holds for $y^2$ and $z^2$, so the total is $3\cdot\dfrac13=1$."
        ),
        verify=[{"expr": "integrate(integrate(integrate(x^2+y^2+z^2, z, 0, 1), y, 0, 1), x, 0, 1)", "equals": "1"}],
    ))

    # 3: x, y in [0,1], 0 <= z <= sqrt(1 - x^2 - y^2): the part of the unit ball in the first octant
    val = sp.pi / 10
    # independent numeric check in spherical coordinates over the first octant of the unit ball
    num = float(mp.quad(lambda r_: r_**4, [0, 1]) * mp.quad(lambda p_: mp.sin(p_), [0, mp.pi / 2]) * (mp.pi / 2))
    assert same_number(val, num)
    items.append(ex(
        "tri-02", r"$\displaystyle\iiint_D(x^2+y^2+z^2)\,dx\,dy\,dz$, $\ D:\ 0\le x\le1,\ 0\le y\le1,\ 0\le z\le\sqrt{1-x^2-y^2}$", "expression", eng(val),
        hints=["For $z$ to be real we need $x^2+y^2\\le1$: the solid is one eighth of the unit ball. Use spherical coordinates."],
        solution=(
            r"The upper limit $\sqrt{1-x^2-y^2}$ is real only when $x^2+y^2\le1$, so $D$ is the part of the unit ball with $x,y,z\ge0$, that is one "
            r"eighth of the ball: $0\le\rho\le1$, $0\le\varphi\le\dfrac\pi2$, $0\le\theta\le\dfrac\pi2$." + "\n\n"
            r"$$\int_0^{\pi/2}\int_0^{\pi/2}\int_0^1\rho^2\cdot\rho^2\sin\varphi\,d\rho\,d\varphi\,d\theta=\frac15\cdot1\cdot\frac\pi2=\frac{\pi}{10}.$$"
        ),
        verify=[{"expr": "integrate(integrate(integrate(rho^4*sin(f), rho, 0, 1), f, 0, pi/2), t, 0, pi/2)", "equals": "pi/10"}],
    ))

    # 4: simplex
    f = x**2 + y**2 + z**2
    val = triple(f, (z, 0, 1 - x - y), (y, 0, 1 - x), (x, 0, 1))
    assert val == sp.Rational(1, 20)
    items.append(ex(
        "tri-03", r"$\displaystyle\iiint_D(x^2+y^2+z^2)\,dx\,dy\,dz$, $\ D:\ 0\le x\le1,\ 0\le y\le1-x,\ 0\le z\le1-x-y$", "number", eng(val),
        hints=["The solid is symmetric in $x$, $y$, $z$: compute $\\iiint x^2\\,dV$ and multiply by $3$."],
        solution=(
            r"The solid is the tetrahedron bounded by the coordinate planes and $x+y+z=1$, which is symmetric in $x$, $y$, $z$. So the integral is "
            r"$3\iiint x^2\,dV$. Now" + "\n\n"
            r"$$\iiint x^2\,dV=\int_0^1x^2\int_0^{1-x}(1-x-y)\,dy\,dx=\int_0^1x^2\cdot\frac{(1-x)^2}{2}\,dx=\frac12\left(\frac13-\frac12+\frac15\right)=\frac1{60}.$$" + "\n\n"
            r"The result is $3\cdot\dfrac1{60}=\dfrac1{20}$."
        ),
        verify=[{"expr": "integrate(integrate(integrate(x^2+y^2+z^2, z, 0, 1-x-y), y, 0, 1-x), x, 0, 1)", "equals": "1/20"}],
    ))

    # 5: xyz over the simplex
    val = triple(x * y * z, (z, 0, 1 - x - y), (y, 0, 1 - x), (x, 0, 1))
    assert val == sp.Rational(1, 720)
    num = float(mp.quad(lambda xv: mp.quad(lambda yv: xv * yv * (1 - xv - yv) ** 2 / 2, [0, 1 - xv]), [0, 1]))
    assert same_number(val, num)
    items.append(ex(
        "tri-04", r"$\displaystyle\iiint_Dxyz\,dx\,dy\,dz$, $\ D:\ 0\le x\le1,\ 0\le y\le1-x,\ 0\le z\le1-x-y$", "number", eng(val),
        hints=["Innermost: $\\int_0^{1-x-y}z\\,dz=\\dfrac{(1-x-y)^2}{2}$."],
        solution=(
            r"Innermost: $\displaystyle\int_0^{1-x-y}z\,dz=\frac{(1-x-y)^2}2$." + "\n\n"
            r"Middle: $\displaystyle\int_0^{1-x}\frac{xy(1-x-y)^2}{2}\,dy=\frac{x(1-x)^4}{24}$." + "\n\n"
            r"Outer: $\displaystyle\int_0^1\frac{x(1-x)^4}{24}\,dx=\frac1{24}\cdot\frac1{30}=\frac1{720}$."
        ),
        verify=[{"expr": "integrate(integrate(integrate(x*y*z, z, 0, 1-x-y), y, 0, 1-x), x, 0, 1)", "equals": "1/720"}],
    ))
    return items


def spherical_items() -> list[dict]:
    val = sp.simplify(sp.integrate(sp.integrate(sp.integrate((rho * sp.sin(phi) * sp.cos(th)) ** 2 * rho**2 * sp.sin(phi), (rho, 0, R)), (phi, 0, sp.pi)), (th, 0, 2 * sp.pi)))
    assert sp.simplify(val - 4 * sp.pi * R**5 / 15) == 0
    vol = sp.simplify(sp.integrate(sp.integrate(sp.integrate(rho**2 * sp.sin(phi), (rho, 0, a)), (phi, 0, sp.pi)), (th, 0, 2 * sp.pi)))
    assert sp.simplify(vol - 4 * sp.pi * a**3 / 3) == 0
    return [
        ex(
            "sph-01", r"$\displaystyle\iiint_Dx^2\,dx\,dy\,dz$, $\ D:\ x^2+y^2+z^2\le R^2$ (with $R>0$)", "expression", eng(val), variables=["R"],
            hints=["By symmetry $\\iiint x^2\\,dV=\\dfrac13\\iiint(x^2+y^2+z^2)\\,dV$. Use spherical coordinates for the last one."],
            solution=(
                r"By symmetry, $\iiint x^2\,dV=\iiint y^2\,dV=\iiint z^2\,dV$, so $\iiint x^2\,dV=\dfrac13\iiint(x^2+y^2+z^2)\,dV$. In spherical coordinates:" + "\n\n"
                r"$$\iiint\rho^2\,dV=\int_0^{2\pi}\int_0^\pi\int_0^R\rho^4\sin\varphi\,d\rho\,d\varphi\,d\theta=2\pi\cdot2\cdot\frac{R^5}{5}=\frac{4\pi R^5}{5}.$$" + "\n\n"
                r"Therefore $\iiint x^2\,dV=\dfrac13\cdot\dfrac{4\pi R^5}5=\dfrac{4\pi R^5}{15}$."
            ),
            verify=[{"expr": "integrate(integrate(integrate((rho*sin(f)*cos(t))^2*rho^2*sin(f), rho, 0, R), f, 0, pi), t, 0, 2*pi)",
                     "equals": "4*pi*R^5/15"}],
        ),
        ex(
            "sph-02", r"The volume of the sphere $x^2+y^2+z^2=a^2$ (that is, of the ball it bounds), with $a>0$.", "expression", eng(vol), variables=["a"],
            hints=["Use spherical coordinates: $V=\\iiint\\rho^2\\sin\\varphi\\,d\\rho\\,d\\varphi\\,d\\theta$."],
            solution=r"$$V=\int_0^{2\pi}\int_0^\pi\int_0^a\rho^2\sin\varphi\,d\rho\,d\varphi\,d\theta=2\pi\cdot2\cdot\frac{a^3}{3}=\frac{4\pi a^3}{3}.$$",
            verify=[{"expr": "integrate(integrate(integrate(rho^2*sin(f), rho, 0, a), f, 0, pi), t, 0, 2*pi)", "equals": "4*pi*a^3/3"}],
        ),
    ]


def volume_items() -> list[dict]:
    val = sp.integrate(sp.integrate(sp.integrate(1, (z, 0, a**2 - x**2)), (x, 0, a)), (y, 0, b))
    assert sp.simplify(val - sp.Rational(2, 3) * a**3 * b) == 0
    return [
        ex(
            "vol-01", r"The volume of the solid bounded by the surface $z=a^2-x^2$ and the planes $x=0$, $y=0$, $z=0$, $y=b$ (with $a,b>0$).", "expression",
            eng(sp.simplify(val)), variables=["a", "b"],
            hints=["The surface meets $z=0$ at $x=a$ (for $x\\ge0$). The solid lies over the rectangle $0\\le x\\le a$, $0\\le y\\le b$."],
            solution=(
                r"The surface $z=a^2-x^2$ is a parabolic cylinder; it meets the plane $z=0$ at $x=a$. The solid lies over the rectangle $0\le x\le a$, $0\le y\le b$, "
                r"with height $a^2-x^2$." + "\n\n"
                r"$$V=\int_0^b\int_0^a(a^2-x^2)\,dx\,dy=b\left[a^2x-\frac{x^3}{3}\right]_0^a=b\cdot\frac{2a^3}{3}=\frac{2a^3b}{3}.$$"
            ),
            verify=[{"expr": "integrate(integrate(a^2-x^2, x, 0, a), y, 0, b)", "equals": "2*a^3*b/3"}],
        ),
        ex(
            "vol-02", r"The volume of the tetrahedron bounded by the coordinate planes and the plane $x+y+z=1$.", "number", "1/6",
            hints=["Use the formula $\\dfrac{abc}{6}$ from the lesson with $a=b=c=1$, or integrate $1-x-y$ over the triangle."],
            solution=(
                r"The top surface is $z=1-x-y$ over the triangle $0\le y\le1-x$, $0\le x\le1$:" + "\n\n"
                r"$$V=\int_0^1\int_0^{1-x}(1-x-y)\,dy\,dx=\int_0^1\frac{(1-x)^2}{2}\,dx=\frac16.$$" + "\n\n"
                r"Check with geometry: $\dfrac13\cdot\text{base}\cdot\text{height}=\dfrac13\cdot\dfrac12\cdot1=\dfrac16$."
            ),
            verify=[{"expr": "integrate(integrate(1-x-y, y, 0, 1-x), x, 0, 1)", "equals": "1/6"}],
        ),
    ]


def build() -> None:
    write_exercises(
        f"{BASE}/u01-cartesian/l01-triple-integrals",
        [exset("triple", "Evaluate the following triple integrals.", cartesian_items(), format="Type an exact value such as `1/20` or `pi/10`.")],
        "mvc_m03.py",
    )
    write_exercises(
        f"{BASE}/u02-cylindrical-and-spherical/l01-cylindrical-and-spherical",
        [exset("spherical", "Use spherical coordinates.", spherical_items(), format="Type an exact expression, for example `4*pi*R^5/15`.")],
        "mvc_m03.py",
    )
    write_exercises(
        f"{BASE}/u03-volumes/l01-volumes",
        [exset("volumes", "Find the volume bounded by the given surfaces.", volume_items(), format="Type an exact expression, for example `2*a^3*b/3`.")],
        "mvc_m03.py",
    )
