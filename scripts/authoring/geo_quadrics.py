"""Exercises of Course 1, Module 3, Unit 4: quadric surfaces."""

from __future__ import annotations

from toolkit import ex, exset, write_exercises

BASE = "geo/m03-space/u04-quadric-surfaces"
FMT = "Type a point as `(x, y, z)`, an equation with `=`, or an exact value such as `4*pi/3` or `sqrt(7)`."

KINDS = [
    {"text": "An ellipsoid", "value": "1"},
    {"text": "A hyperboloid of one sheet", "value": "2"},
    {"text": "A hyperboloid of two sheets", "value": "3"},
    {"text": "An elliptic paraboloid", "value": "4"},
    {"text": "A hyperbolic paraboloid", "value": "5"},
    {"text": "A cone", "value": "6"},

]
CYL = [{"text": "An ellipsoid", "value": "1"}, {"text": "A cone", "value": "2"}, {"text": "An elliptic paraboloid", "value": "3"}, {"text": "An elliptic cylinder", "value": "4"}]


def l01() -> list[dict]:
    items = []
    items.append(ex("qs-01", r"The volume of the solid bounded by $4x^2+9y^2+36z^2=36$.", "expression", "8*pi", hints=["Divide by $36$ to find the semi-axes."],
                    solution=r"$\dfrac{x^2}9+\dfrac{y^2}4+z^2=1$: $a=3$, $b=2$, $c=1$, so $V=\dfrac43\pi\cdot6=8\pi$."))
    items.append(ex("qs-02", r"The volume of the solid bounded by $2x^2+3y^2+6z^2=6$.", "expression", "4*sqrt(6)*pi/3", hints=["The semi-axes are $\\sqrt3$, $\\sqrt2$, $1$."],
                    solution=r"$\dfrac{x^2}3+\dfrac{y^2}2+z^2=1$, so $V=\dfrac43\pi\sqrt3\sqrt2=\dfrac{4\sqrt6\,\pi}{3}$."))
    items.append(ex("qs-03", r"The length of the longest semi-axis of $\dfrac{x^2}{16}+\dfrac{y^2}9+\dfrac{z^2}{4}=1$.", "number", "4", hints=["Take the square root of each denominator."], solution=r"The semi-axes are $4$, $3$, $2$."))
    items.append(ex("qs-04", r"The radius of the trace of $x^2+y^2-z^2=1$ in the plane $z=2$.", "expression", "sqrt(5)", hints=["Put $z=2$."], solution=r"$x^2+y^2=1+4=5$, a circle of radius $\sqrt5$."))
    items.append(ex("qs-05", r"The radius of the trace of $z=x^2+y^2$ in the plane $z=9$.", "number", "3", hints=["Put $z=9$."], solution=r"$x^2+y^2=9$, a circle of radius $3$."))
    items.append(ex("qs-06", r"The smallest value of $z$ on the upper sheet of $z^2-x^2-y^2=1$.", "number", "1", hints=["$x^2+y^2=z^2-1\\ge0$."],
                    solution=r"A sum of squares is not negative, so $z^2\ge1$. The upper sheet has $z\ge1$."))
    items.append(ex("qs-07", r"The value of $z$ at the point of the saddle $z=x^2-y^2$ above $(2,1)$.", "number", "3", hints=["Replace $x=2$, $y=1$."], solution=r"$z=4-1=3$."))
    items.append(ex("qs-08", r"What kind of surface is $\dfrac{x^2}{4}+\dfrac{y^2}{9}-\dfrac{z^2}{16}=1$?", "multiple_choice", "2", choices=KINDS, correctIndex=1,
                    hints=["Count the signs: two positive and one negative, equal to $1$."], solution=r"Two positive squares and one negative equal to $1$: a hyperboloid of one sheet."))
    items.append(ex("qs-09", r"What kind of surface is $\dfrac{z^2}{4}-\dfrac{x^2}{9}-\dfrac{y^2}{16}=1$?", "multiple_choice", "3", choices=KINDS, correctIndex=2,
                    hints=["One positive and two negative squares equal to $1$."], solution=r"One positive and two negative squares equal to $1$: two sheets."))
    items.append(ex("qs-10", r"What kind of surface is $x^2+y^2=z^2$?", "multiple_choice", "6", choices=KINDS, correctIndex=5,
                    hints=["The equation is homogeneous."], solution=r"The traces $z=k$ are circles of radius $\lvert k\rvert$, and the trace $z=0$ is one point: a cone."))
    return items


def l02() -> list[dict]:
    items = []
    items.append(ex("cy-01", r"The center of the ellipsoid $x^2+4y^2+z^2-2x+8y-2z-2=0$.", "vector", "(1, -1, 1)", hints=["Complete the squares."],
                    solution=r"$(x-1)^2+4(y+1)^2+(z-1)^2=8$: the center is $(1,-1,1)$."))
    items.append(ex("cy-02", r"The center of the ellipsoid $9x^2+y^2+9z^2-18x+4y+18z+13=0$.", "vector", "(1, -2, -1)", hints=["Factor $9$ from the terms in $x$ and in $z$."],
                    solution=r"$9(x-1)^2+(y+2)^2+9(z+1)^2=9$: the center is $(1,-2,-1)$."))
    items.append(ex("cy-03", r"The surface obtained by rotating the parabola $y=x^2$ of the plane $xy$ about the $y$-axis (equation $y=\dots$).", "equation", "y=x^2+z^2", coordinates=["x", "y", "z"],
                    hints=["Replace $x^2$ by $x^2+z^2$."], solution=r"$y=x^2+z^2$."))
    items.append(ex("cy-04", r"The surface obtained by rotating $z^2=4x$ of the plane $xz$ about the $x$-axis.", "equation", "y^2+z^2=4*x", coordinates=["x", "y", "z"],
                    hints=["Replace $z^2$ by $y^2+z^2$."], solution=r"$y^2+z^2=4x$."))
    items.append(ex("cy-05", r"The surface obtained by rotating the line $z=2x$ of the plane $xz$ about the $z$-axis.", "equation", "z^2=4*x^2+4*y^2", coordinates=["x", "y", "z"],
                    hints=["Square first, then replace $x^2$ by $x^2+y^2$."], solution=r"$z^2=4x^2$ becomes $z^2=4\left(x^2+y^2\right)$."))
    items.append(ex("cy-06", r"The radius of the circular cylinder $y^2+z^2=25$.", "number", "5", hints=["The variable $x$ is missing."], solution=r"The sections $x=k$ are circles of radius $5$."))
    items.append(ex("cy-07", r"The radius of the circle in which the cone $x^2+y^2=z^2$ meets the plane $z=3$.", "number", "3", hints=["Put $z=3$."], solution=r"$x^2+y^2=9$."))
    items.append(ex("cy-08", r"What kind of surface is $\dfrac{x^2}{4}+\dfrac{y^2}{9}=1$ in space?", "multiple_choice", "4", choices=CYL, correctIndex=3,
                    hints=["The variable $z$ is missing."], solution=r"For every $z$ the point $(x,y)$ stays on the same ellipse: an elliptic cylinder."))
    items.append(ex("cy-09", r"What kind of surface is $z=x^2+y^2$?", "multiple_choice", "4", choices=KINDS, correctIndex=3,
                    hints=["The traces $z=k$ are circles."], solution=r"It is the paraboloid of revolution, a case of the elliptic paraboloid."))
    return items


def build() -> None:
    write_exercises(f"{BASE}/l01-the-canonical-quadrics", [exset("quadrics", "The canonical quadrics.", l01(), format=FMT)], "geo_quadrics.py")
    write_exercises(f"{BASE}/l02-cylinders-cones-and-surfaces-of-revolution", [exset("cylinders", "Cylinders, cones and surfaces of revolution.", l02(), format=FMT)], "geo_quadrics.py")
