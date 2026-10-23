"""Exercises of Course 2, Module 2, Unit 1, Lesson 2: Riemann sums, properties of the double integral, mass, average value, centre of mass
(original exercises)."""

from __future__ import annotations

import sympy as sp
from toolkit import P, eng, ex, exset_plain, simp, tex, write_exercises, x, y

r, th = sp.symbols("r theta", positive=True)


def kind_of(value: sp.Expr) -> str:
    return "number" if value.is_Rational else "expression"


def dbl(f: sp.Expr, ylo: sp.Expr, yhi: sp.Expr, xlo: sp.Expr, xhi: sp.Expr) -> sp.Expr:
    return simp(sp.integrate(sp.integrate(f, (y, ylo, yhi)), (x, xlo, xhi)))


def riemann_items() -> list[dict]:
    items: list[dict] = []

    def midpoint(i: str, f: sp.Expr, ftex: str, xs: tuple, ys: tuple, m: int, n: int) -> None:
        dx, dy = sp.Rational(xs[1] - xs[0], m), sp.Rational(ys[1] - ys[0], n)
        pts = [(xs[0] + (a + sp.Rational(1, 2)) * dx, ys[0] + (b + sp.Rational(1, 2)) * dy) for a in range(m) for b in range(n)]
        vals = [simp(f.subs({x: p[0], y: p[1]})) for p in pts]
        total = simp(sum(vals) * dx * dy)
        items.append(ex(
            f"rs-{i}", rf"Compute the midpoint Riemann sum of $f(x,y)={ftex}$ over $[{xs[0]},{xs[1]}]\times[{ys[0]},{ys[1]}]$ with ${m}\times{n}$ equal rectangles (${m}$ in the $x$ direction, ${n}$ in the $y$ direction).",
            kind_of(total), eng(total),
            hints=[rf"Each rectangle has area $\Delta A={tex(dx * dy)}$. Evaluate $f$ at the centre of each rectangle and add."],
            solution=rf"The centres give the values ${', '.join(tex(v) for v in vals)}$; their sum is ${tex(sum(vals))}$, times $\Delta A={tex(dx * dy)}$ gives ${tex(total)}$.",
        ))

    midpoint("01", P("x*y"), "xy", (0, 4), (0, 2), 2, 2)
    midpoint("02", P("x^2+y"), "x^2+y", (0, 3), (0, 2), 3, 2)
    midpoint("03", P("4-x-y"), "4-x-y", (0, 2), (0, 2), 2, 2)

    corner = [P("x+2*y").subs({x: a, y: b}) for a in (0, 1) for b in (0, 1)]
    total = simp(sum(corner))
    items.append(ex(
        "rs-04", r"Compute the Riemann sum of $f(x,y)=x+2y$ over $[0,2]\times[0,2]$ with the four unit squares, taking the **lower left corner** of each square as the sample point.",
        kind_of(total), eng(total),
        hints=[r"The lower left corners are $(0,0)$, $(1,0)$, $(0,1)$, $(1,1)$ and each square has area $1$."],
        solution=rf"$f$ takes the values ${', '.join(tex(v) for v in corner)}$, so $S={tex(total)}$.",
    ))

    f = P("x^2+y^2")
    val = dbl(f, 0, 2, 0, 3)
    items.append(ex(
        "rs-05", r"Compute the exact value of $\displaystyle\iint_R(x^2+y^2)\,dA$ over $R=[0,3]\times[0,2]$.", kind_of(val), eng(val),
        hints=[r"Integrate first in $y$ from $0$ to $2$, then in $x$ from $0$ to $3$."],
        solution=rf"$\int_0^3\!\!\int_0^2(x^2+y^2)\,dy\,dx=\int_0^3\left(2x^2+\dfrac83\right)dx={tex(val)}$.",
    ))
    return items


def property_items() -> list[dict]:
    items: list[dict] = []
    items.append(ex(
        "pr-01", r"Over a region $D$: $\displaystyle\iint_Df\,dA=4$ and $\displaystyle\iint_Dg\,dA=-1$. Find $\displaystyle\iint_D(3f+2g)\,dA$.", "number", "10",
        hints=[r"Use linearity of the integral."],
        solution=r"$3\cdot4+2\cdot(-1)=10$.",
    ))
    items.append(ex(
        "pr-02", r"The region $D$ is split into two regions $D_1$, $D_2$ that do not overlap. If $\displaystyle\iint_Df\,dA=15$ and $\displaystyle\iint_{D_1}f\,dA=6$, find $\displaystyle\iint_{D_2}f\,dA$.",
        "number", "9", hints=[r"The integrals over $D_1$ and $D_2$ add up to the integral over $D$."],
        solution=r"$\iint_{D_2}f\,dA=15-6=9$.",
    ))
    items.append(ex(
        "pr-03", r"Use $\displaystyle\iint_D1\,dA$ to find the area of the triangle $D$ with vertices $(0,0)$, $(4,0)$, $(0,3)$. The unit is squ: give the number only.",
        "number", "6", hints=[r"The triangle is $0\le x\le4$, $0\le y\le3-\dfrac34x$."],
        solution=rf"$\int_0^4\!\!\int_0^{{3-3x/4}}1\,dy\,dx={tex(dbl(sp.Integer(1), 0, 3 - sp.Rational(3, 4) * x, 0, 4))}$, which is half of $4\cdot3$.",
    ))
    items.append(ex(
        "pr-04", r"On a region $D$ of area $5$ we know $1\le f(x,y)\le3$. Between which numbers is $\displaystyle\iint_Df\,dA$ certainly found?",
        "multiple_choice", "2",
        choices=[{"text": r"between $1$ and $3$", "value": "1"}, {"text": r"between $5$ and $15$", "value": "2"}, {"text": r"between $0$ and $5$", "value": "3"}],
        correctIndex=1, hints=[r"Compare $f$ with the constants $1$ and $3$ and use $\iint_Dc\,dA=c\cdot\text{area}$."],
        solution=r"Since $1\le f\le3$, $\iint_D1\,dA\le\iint_Df\,dA\le\iint_D3\,dA$, that is $5\le\iint_Df\,dA\le15$.",
    ))
    return items


def mass_items() -> list[dict]:
    items: list[dict] = []

    def mass(i: str, shape: str, rho: sp.Expr, rtex: str, bounds: tuple) -> None:
        val = dbl(rho, *bounds)
        items.append(ex(
            f"ms-{i}", rf"Find the mass of the plate {shape} with density $\rho(x,y)={rtex}$ (give the number only, in kg).", kind_of(val), eng(val),
            hints=[r"$M=\iint_D\rho\,dA$. Describe the region with inequalities first."],
            solution=rf"$M=\iint_D\rho\,dA={tex(val)}$.",
        ))

    mass("01", r"$[0,2]\times[0,1]$", P("x+y"), "x+y", (0, 1, 0, 2))
    mass("02", r"$0\le y\le x\le2$", P("y"), "y", (0, x, 0, 2))
    mass("03", r"between the curves $y=x^2$ and $y=x$ ($0\le x\le1$)", sp.Integer(1), "1", (x**2, x, 0, 1))
    disc = simp(sp.integrate(sp.integrate(r**2 * r, (r, 0, 2)), (th, 0, 2 * sp.pi)))
    assert disc == 8 * sp.pi
    items.append(ex(
        "ms-04", r"Find the mass of the disc $x^2+y^2\le4$ with density $\rho(x,y)=x^2+y^2$ (give the number only, in kg).", "expression", eng(disc),
        hints=[r"Use polar coordinates: $x^2+y^2=r^2$ and $dA=r\,dr\,d\theta$."],
        solution=r"$M=\displaystyle\int_0^{2\pi}\!\!\int_0^2r^2\cdot r\,dr\,d\theta=2\pi\cdot\dfrac{2^4}{4}=8\pi$.",
    ))
    return items


def average_items() -> list[dict]:
    items: list[dict] = []
    val = simp(dbl(P("x^2+y^2"), 0, 1, 0, 1) / 1)
    items.append(ex(
        "av-01", r"Find the average value of $f(x,y)=x^2+y^2$ over the square $[0,1]\times[0,1]$.", kind_of(val), eng(val),
        hints=[r"The area of the square is $1$."], solution=rf"$\iint f\,dA=\dfrac13+\dfrac13={tex(val)}$ and the area is $1$, so the average is ${tex(val)}$.",
    ))
    tri = dbl(P("x+y"), 0, 2 - x, 0, 2)
    avg = simp(tri / 2)
    items.append(ex(
        "av-02", r"Find the average value of $f(x,y)=x+y$ over the triangle with vertices $(0,0)$, $(2,0)$, $(0,2)$.", kind_of(avg), eng(avg),
        hints=[r"The area of the triangle is $2$. The region is $0\le x\le2$, $0\le y\le2-x$."],
        solution=rf"$\iint(x+y)\,dA={tex(tri)}$ and the area is $2$, so the average is ${tex(avg)}$.",
    ))
    trig = simp(sp.integrate(sp.integrate(sp.sin(x) * sp.cos(y), (y, 0, sp.pi / 2)), (x, 0, sp.pi)) / (sp.pi * (sp.pi / 2)))
    items.append(ex(
        "av-03", r"Find the average value of $f(x,y)=\sin x\cos y$ over the rectangle $0\le x\le\pi,\ 0\le y\le\dfrac\pi2$.", "expression", eng(trig),
        hints=[r"The double integral separates into $\int_0^\pi\sin x\,dx\cdot\int_0^{\pi/2}\cos y\,dy$. The area is $\dfrac{\pi^2}{2}$."],
        solution=rf"$\iint f\,dA=2\cdot1=2$ and the area is $\dfrac{{\pi^2}}{{2}}$, so the average is ${tex(trig)}$.",
    ))
    return items


def centre_items() -> list[dict]:
    items: list[dict] = []
    rho = P("x")
    m = dbl(rho, 0, 1, 0, 2)
    xb = simp(dbl(x * rho, 0, 1, 0, 2) / m)
    yb = simp(dbl(y * rho, 0, 1, 0, 2) / m)
    items.append(ex(
        "cm-01", r"A plate occupies $[0,2]\times[0,1]$ and has density $\rho(x,y)=x$. Find the $x$-coordinate $\bar x$ of its centre of mass.", kind_of(xb), eng(xb),
        hints=[r"$\bar x=\dfrac1M\iint x\rho\,dA$ with $M=\iint\rho\,dA$."],
        solution=rf"$M=\int_0^2\!\!\int_0^1x\,dy\,dx={tex(m)}$ and $\iint x\cdot x\,dA=\dfrac83$, so $\bar x={tex(xb)}$.",
    ))
    items.append(ex(
        "cm-02", r"For the same plate ($[0,2]\times[0,1]$, $\rho=x$) find the $y$-coordinate $\bar y$ of its centre of mass.", kind_of(yb), eng(yb),
        hints=[r"$\bar y=\dfrac1M\iint y\rho\,dA$."],
        solution=rf"$\iint y\cdot x\,dA=2\cdot\dfrac12=1$ and $M={tex(m)}$, so $\bar y={tex(yb)}$.",
    ))
    return items


def build() -> None:
    write_exercises(
        "mvc/m02-double-integrals/u01-over-regions/l02-riemann-sums-and-applications",
        [
            exset_plain("riemann", "Riemann sums.", riemann_items(), format="Type an exact value such as `7/2`."),
            exset_plain("properties", "Properties of the double integral.", property_items(), format="Type a number."),
            exset_plain("mass", "Mass of a plate.", mass_items(), format="Type an exact value such as `5/6` or `3*pi`."),
            exset_plain("average", "Average value.", average_items(), format="Type an exact value such as `7/9` or `3/pi^2`."),
            exset_plain("centre", "Centre of mass.", centre_items(), format="Type an exact value such as `9/8`."),
        ],
        "mvc_double.py",
    )
