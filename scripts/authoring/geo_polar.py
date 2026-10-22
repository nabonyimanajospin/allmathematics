"""Exercises of Course 1, Module 2, Unit 4: polar coordinates, polar curves and the change of axes."""

from __future__ import annotations

import sympy as sp
from toolkit import eng, ex, exset_plain as exset, tex, write_exercises, x, y

BASE = "geo/m02-plane/u04-polar-coordinates-and-curves"
R = sp.Rational
PI = sp.pi
th = sp.Symbol("theta", real=True)
FMT = "Type a point as `(a, b)`, an exact value such as `5*pi/6` or `sqrt(3)/2`; an equation with `=`; for an angle you can type `theta`."


def simp(e) -> sp.Expr:
    return sp.simplify(sp.radsimp(sp.simplify(e)))


def to_cart(r, t):
    return (simp(r * sp.cos(t)), simp(r * sp.sin(t)))


def to_polar(px, py):
    r = simp(sp.sqrt(px**2 + py**2))
    t = sp.atan2(py, px)  # principal value in (-pi, pi]
    return r, simp(t)


def pt_tex(p) -> str:
    return rf"\left({tex(p[0])},\,{tex(p[1])}\right)"


def pt_eng(p) -> str:
    return f"({eng(p[0])}, {eng(p[1])})"


def u4l1() -> list[dict]:
    items = []
    for n, (r, t) in enumerate(((4, 5 * PI / 6), (6, -PI / 3), (2, 3 * PI / 4), (10, PI / 2), (3, 7 * PI / 6)), 1):
        c = to_cart(r, t)
        items.append(ex(f"pc-{n:02d}", rf"The Cartesian coordinates of the point $P\left({r},{tex(t)}\right)$.", "vector", pt_eng(c),
                        hints=["$x=r\\cos\\theta$ and $y=r\\sin\\theta$."],
                        solution=rf"$x={r}\cos\left({tex(t)}\right)={tex(c[0])}$ and $y={r}\sin\left({tex(t)}\right)={tex(c[1])}$."))
    for n, (px, py) in enumerate(((-5, -5), (-sp.sqrt(3), 3), (3, -3), (0, -5), (-4, 0), (sp.sqrt(3), 1)), 6):
        r, t = to_polar(px, py)
        items.append(ex(f"pc-{n:02d}", rf"The polar coordinates $(r,\theta)$, with $r>0$ and $\theta\in]-\pi,\pi]$, of the point $({tex(px)},{tex(py)})$.", "vector", pt_eng((r, t)),
                        hints=["Find the quadrant first: the angle must be in it."],
                        solution=rf"$r=\sqrt{{{tex(px**2)}+{tex(py**2)}}}={tex(r)}$. The point is {'on an axis' if px == 0 or py == 0 else 'in the ' + ('first' if px > 0 and py > 0 else 'second' if px < 0 < py else 'third' if px < 0 and py < 0 else 'fourth') + ' quadrant'}, so $\\theta={tex(t)}$."))
    # distance (assignment, question 3)
    items.append(ex("pc-12", r"The length of the segment $AB$ with $A\left(8,-\dfrac{2\pi}3\right)$ and $B\left(6,\dfrac\pi3\right)$.", "number", "14",
                    hints=["$\\theta_2-\\theta_1=\\pi$: the points are on opposite sides of the pole."],
                    solution=r"$AB^2=64+36-2\cdot8\cdot6\cos\pi=196$, so $AB=14$."))
    items.append(ex("pc-13", r"The polar coordinates of the midpoint of $AB$, with $A\left(8,-\dfrac{2\pi}3\right)$ and $B\left(6,\dfrac\pi3\right)$ (with $r>0$).", "vector", "(1, -2*pi/3)",
                    hints=["The points are on one line through the pole."],
                    solution=r"The midpoint is $7$ from $A$ on the line $AB$, which passes through $O$, so it is at distance $8-7=1$ from $O$ on the side of $A$: $\left(1,-\dfrac{2\pi}3\right)$."))
    items.append(ex("pc-14", r"The length of the segment $AB$ with $A\left(12,\dfrac{4\pi}9\right)$ and $B\left(12,\dfrac{4\pi}9\right)$ (as printed on the assignment).", "number", "0",
                    hints=["Compare the two points."], solution=r"The two points are the same, so the length is $0$ and the midpoint is the point itself, $\left(12,\dfrac{4\pi}9\right)$.",
                    note="On the printed assignment the two endpoints of the second segment are written with the same coordinates; the exercise is solved as printed (the length is $0$). If one of the angles was meant to be different, use the formula $\\sqrt{r_1^2+r_2^2-2r_1r_2\\cos(\\theta_2-\\theta_1)}$ with the intended values."))
    items.append(ex("pc-15", r"The distance between $P\left(2,\dfrac\pi2\right)$ and $Q\left(2,\dfrac{\pi}{6}\right)$.", "expression", "sqrt(8-4*sqrt(3))" if False else eng(simp(sp.sqrt(8 - 8 * sp.cos(PI / 3)))),
                    hints=["$\\theta_2-\\theta_1=-\\dfrac\\pi3$."], solution=r"$PQ^2=4+4-8\cos\dfrac\pi3=4$, so $PQ=2$."))
    return items


def u4l2() -> list[dict]:
    items = []
    cart = (
        (x**2 + y**2 - 8 * y, 8 * sp.sin(th), "x^2+y^2=8y"),
        (x**2 + y**2 - 6 * x, 6 * sp.cos(th), "x^2+y^2-6x=0"),
        (x - 4, 4 / sp.cos(th), "x=4"),
        (y + 2, -2 / sp.sin(th), "y=-2"),
        (x**2 + y**2 - 16, sp.Integer(4), "x^2+y^2=16"),
    )
    for n, (_poly, rt, text) in enumerate(cart, 1):
        items.append(ex(f"pe-{n:02d}", rf"The polar equation $r=\dots$ of the curve ${text.replace('^', '^').replace('*', '')}$ (answer with $r$ as a function of theta).", "expression", eng(rt),
                        variables=["theta"], hints=["Substitute $x=r\\cos\\theta$, $y=r\\sin\\theta$ and simplify."],
                        solution=rf"After the substitution and a division by $r$ (or $\cos\theta$, $\sin\theta$) we get $r={tex(rt)}$."))
    polar_to_cart = (
        ("r=6\\sin\\theta", "x^2+(y-3)^2=9"),
        ("r=8\\cos\\theta", "(x-4)^2+y^2=16"),
        ("r=-4\\sin\\theta", "x^2+(y+2)^2=4"),
    )
    for n, (rtext, eq) in enumerate(polar_to_cart, 6):
        items.append(ex(f"pe-{n:02d}", rf"The Cartesian equation of the curve ${rtext}$.", "equation", eq, coordinates=["x", "y"],
                        hints=["Multiply both sides by $r$, then use $r^2=x^2+y^2$."],
                        solution=rf"Multiplying by $r$ gives $x^2+y^2=\dots$; completing the square gives ${eq.replace('^2', '^2')}$."))
    items.append(ex("pe-09", r"The Cartesian equation of the line $r\cos\left(\theta-\dfrac\pi3\right)=2$.", "equation", "x+sqrt(3)*y=4", coordinates=["x", "y"],
                    hints=["$\\cos(\\theta-\\alpha)=\\cos\\theta\\cos\\alpha+\\sin\\theta\\sin\\alpha$."],
                    solution=r"$r\left(\dfrac12\cos\theta+\dfrac{\sqrt3}2\sin\theta\right)=2$ gives $\dfrac x2+\dfrac{\sqrt3}2y=2$, that is $x+\sqrt3y=4$."))
    return items


def u4l3() -> list[dict]:
    items = []
    for n, (text, count) in enumerate((("r=5\\cos3\\theta", 3), ("r=6\\sin2\\theta", 4), ("r=2\\cos4\\theta", 8), ("r=3\\sin5\\theta", 5)), 1):
        items.append(ex(f"pk-{n:02d}", rf"The number of petals of the rose ${text}$.", "number", str(count), hints=["Odd $n$: $n$ petals. Even $n$: $2n$ petals."],
                        solution=rf"The coefficient of $\theta$ is {'odd' if count % 2 else 'even'}, so the rose has ${count}$ petals."))
    for n, (a, trig) in enumerate(((4, "1-\\sin\\theta"), (2, "1+\\cos\\theta"), (5, "1+\\sin\\theta")), 5):
        items.append(ex(f"pk-{n:02d}", rf"The largest value of $r$ on the cardioid $r={a}({trig})$.", "number", str(2 * a), hints=["The bracket is largest when the trigonometric term is $\\pm1$."],
                        solution=rf"The bracket takes values between $0$ and $2$, so the largest $r$ is ${2*a}$."))
    items.append(ex("pk-08", r"The value of $r$ on $r=3(1+\cos\theta)$ for $\theta=\dfrac{2\pi}3$.", "number", "3/2", hints=["$\\cos\\dfrac{2\\pi}3=-\\dfrac12$."], solution=r"$3\left(1-\dfrac12\right)=\dfrac32$."))
    for n, (a, kind) in enumerate(((2, "card"), (4, "card")), 9):
        area = sp.Rational(3, 2) * PI * a**2
        items.append(ex(f"pk-{n:02d}", rf"The area enclosed by the cardioid $r={a}(1+\cos\theta)$.", "expression", eng(area), hints=["$A=\\dfrac12\\int_0^{2\\pi}r^2\\,d\\theta$."],
                        solution=rf"$A=\dfrac12\int_0^{{2\pi}}{a**2}(1+\cos\theta)^2\,d\theta={a**2}\cdot\dfrac{{3\pi}}{{2}}={tex(area)}$."))
    items.append(ex("pk-11", r"The area enclosed by the rose $r=5\sin2\theta$.", "expression", "25*pi/2", hints=["$\\sin^22\\theta=\\dfrac{1-\\cos4\\theta}{2}$."],
                    solution=r"$A=\dfrac12\int_0^{2\pi}25\sin^22\theta\,d\theta=\dfrac{25}2\cdot\pi=\dfrac{25\pi}2$."))
    items.append(ex("pk-12", r"The area enclosed by the three-petal rose $r=4\cos3\theta$.", "expression", "8*pi", hints=["$\\int_0^{2\\pi}\\cos^23\\theta\\,d\\theta=\\pi$."],
                    solution=r"$A=\dfrac12\cdot16\cdot\pi=8\pi$."))
    items.append(ex("pk-13", r"The area enclosed by both loops of the lemniscate $r^2=16\cos2\theta$.", "number", "16", hints=["Use the loop for $-\\dfrac\\pi4\\le\\theta\\le\\dfrac\\pi4$ and double it."],
                    solution=r"One loop: $\dfrac12\int_{-\pi/4}^{\pi/4}16\cos2\theta\,d\theta=8\cdot1=8$. Two loops: $16$."))
    items.append(ex("pk-14", r"The area swept by the spiral $r=\dfrac\theta8$ for $0\le\theta\le2\pi$.", "expression", "pi^3/48", hints=["$A=\\dfrac12\\int_0^{2\\pi}\\dfrac{\\theta^2}{64}\\,d\\theta$."],
                    solution=r"$A=\dfrac1{128}\cdot\dfrac{(2\pi)^3}{3}=\dfrac{8\pi^3}{384}=\dfrac{\pi^3}{48}$."))
    return items


def u4l4() -> list[dict]:
    items = []
    items.append(ex("ca-01", r"After moving the origin to $O'(2,-1)$, the new coordinates of $M(5,3)$.", "vector", "(3, 4)", hints=["$x'=x-a$, $y'=y-b$."], solution=r"$x'=5-2=3$, $y'=3+1=4$."))
    items.append(ex("ca-02", r"After moving the origin to $O'(-3,4)$, the new coordinates of $M(1,1)$.", "vector", "(4, -3)", hints=["Subtract the coordinates of the new origin."], solution=r"$x'=1+3=4$, $y'=1-4=-3$."))
    items.append(ex("ca-03", r"The equation of $x^2+y^2-4x+6y-12=0$ after moving the origin to its center (write it as $x'^2+y'^2=\dots$ with the letters $x$ and $y$).", "equation", "x^2+y^2=25", coordinates=["x", "y"],
                    hints=["Complete the squares: the center is $(2,-3)$."], solution=r"$(x-2)^2+(y+3)^2=12+4+9=25$, so with $x'=x-2$ and $y'=y+3$ the equation is $x'^2+y'^2=25$."))
    items.append(ex("ca-04", r"The axes are rotated by $\dfrac\pi2$. The new coordinates of $M(3,4)$.", "vector", "(4, -3)", hints=["$x'=x\\cos\\varphi+y\\sin\\varphi$, $y'=-x\\sin\\varphi+y\\cos\\varphi$."], solution=r"$x'=4$, $y'=-3$."))
    items.append(ex("ca-05", r"The axes are rotated by $\dfrac\pi6$. The new coordinates of $M(2,0)$.", "vector", "(sqrt(3), -1)", hints=["$\\cos\\dfrac\\pi6=\\dfrac{\\sqrt3}2$, $\\sin\\dfrac\\pi6=\\dfrac12$."],
                    solution=r"$x'=2\cdot\dfrac{\sqrt3}2=\sqrt3$, $y'=-2\cdot\dfrac12=-1$."))
    items.append(ex("ca-06", r"The equation of $x^2-y^2=8$ after a rotation of the axes by $\dfrac\pi4$ (in the letters $x$ and $y$ for the new coordinates).", "equation", "x*y=-4", coordinates=["x", "y"],
                    hints=["$x=\\dfrac{\\sqrt2}{2}(x'-y')$ and $y=\\dfrac{\\sqrt2}{2}(x'+y')$."],
                    solution=r"$x^2-y^2=\dfrac12\left[(x'-y')^2-(x'+y')^2\right]=-2x'y'$, so $-2x'y'=8$, that is $x'y'=-4$."))
    items.append(ex("ca-07", r"The equation of $xy=1$ after a rotation of the axes by $\dfrac\pi4$ (written as $x^2-y^2=\dots$ in the new letters $x,y$).", "equation", "x^2-y^2=2", coordinates=["x", "y"],
                    hints=["Replace $x$ and $y$ by the rotation formulas."], solution=r"$xy=\dfrac12(x'^2-y'^2)=1$, so $x'^2-y'^2=2$."))
    return items


def build() -> None:
    write_exercises(f"{BASE}/l01-polar-coordinates", [exset("polar", "Polar coordinates.", u4l1(), format=FMT)], "geo_polar.py")
    write_exercises(f"{BASE}/l02-lines-and-circles-in-polar-form", [exset("polar-equations", "Equations in polar form.", u4l2(), format=FMT)], "geo_polar.py")
    write_exercises(f"{BASE}/l03-polar-curves", [exset("curves", "Polar curves and their areas.", u4l3(), format=FMT)], "geo_polar.py")
    write_exercises(f"{BASE}/l04-change-of-axes", [exset("axes", "Change of axes.", u4l4(), format=FMT)], "geo_polar.py")
