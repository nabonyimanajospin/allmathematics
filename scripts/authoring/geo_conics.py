"""Exercises of Course 1, Module 2, Unit 5: conics and loci."""

from __future__ import annotations

import sympy as sp
from toolkit import eng, ex, exset_plain as exset, tex, write_exercises

BASE = "geo/m02-plane/u05-conics-and-loci"
R = sp.Rational
FMT = "Type a point as `(a, b)`, an exact value such as `5/13` or `sqrt(7)/3`, an equation with `=`; for an angle you can type `theta`."


def conic_choices() -> list[dict]:
    return [{"text": "An ellipse", "value": "1"}, {"text": "A hyperbola", "value": "2"}, {"text": "A parabola", "value": "3"},
            {"text": "Two lines or a point or nothing", "value": "4"}]


def l01() -> list[dict]:
    items = []
    for n, k in enumerate((12, 20, 6, 28), 1):
        f = R(k, 4)
        items.append(ex(f"pa-{n:02d}", rf"The focus of the parabola $y^2={k}x$.", "vector", f"({eng(f)}, 0)", hints=["Write $y^2=2px$: the focus is $\\left(\\dfrac p2,0\\right)$."],
                        solution=rf"$2p={k}$, so $p={tex(R(k, 2))}$ and the focus is $\left({tex(f)},0\right)$."))
    items.append(ex("pa-05", r"The directrix of the parabola $y^2=-12x$.", "equation", "x=3", coordinates=["x", "y"], hints=["Here $2p=-12$: the parabola opens to the left."],
                    solution=r"The parabola $y^2=-2px$ with $p=6$ has the focus $(-3,0)$ and the directrix $x=3$."))
    items.append(ex("pa-06", r"The vertex of the parabola $y^2-4y-12x+28=0$.", "vector", "(2, 2)", hints=["Complete the square in $y$."],
                    solution=r"$(y-2)^2-4-12x+28=0$ gives $(y-2)^2=12(x-2)$: the vertex is $(2,2)$."))
    items.append(ex("pa-07", r"The focus of the parabola $x^2-6x-8y+25=0$.", "vector", "(3, 4)", hints=["Complete the square in $x$: the parabola opens upward."],
                    solution=r"$(x-3)^2=8y-16=8(y-2)$. Vertex $(3,2)$, $p=4$, so the focus is $2$ above the vertex: $(3,4)$."))
    items.append(ex("pa-08", r"The equation of the parabola with vertex at the origin and focus $(3,0)$.", "equation", "y^2=12*x", coordinates=["x", "y"], hints=["$\\dfrac p2=3$."],
                    solution=r"$p=6$, so $y^2=2px=12x$."))
    items.append(ex("pa-09", r"The distance from the point $(3,6)$ of $y^2=12x$ to the focus.", "number", "6", hints=["It equals the distance to the directrix $x=-3$."],
                    solution=r"The distance to the directrix is $3+3=6$, and it equals the distance to the focus $(3,0)$: $\sqrt{0+36}=6$."))
    items.append(ex("pa-10", r"The tangent to $y^2=12x$ at the point $(3,6)$.", "equation", "y=x+3", coordinates=["x", "y"], hints=["$yy_0=p(x+x_0)$ with $p=6$."],
                    solution=r"$6y=6(x+3)$, so $y=x+3$."))
    items.append(ex("pa-11", r"The tangent to $x^2=8y$ at the point $(4,2)$.", "equation", "y=x-2", coordinates=["x", "y"], hints=["Differentiate: the slope is $\\dfrac x4$."],
                    solution=r"The slope at $x=4$ is $1$, so $y-2=x-4$, that is $y=x-2$."))
    return items


def l02() -> list[dict]:
    items = []
    items.append(ex("el-01", r"The distance between the foci of $\dfrac{x^2}{100}+\dfrac{y^2}{36}=1$.", "number", "16", hints=["$c^2=a^2-b^2$."],
                    solution=r"$c^2=100-36=64$, so $c=8$ and the distance is $2c=16$."))
    items.append(ex("el-02", r"The eccentricity of $9x^2+25y^2=225$.", "expression", "4/5", hints=["Divide by $225$ first."],
                    solution=r"$\dfrac{x^2}{25}+\dfrac{y^2}9=1$, $c^2=16$, $e=\dfrac45$."))
    items.append(ex("el-03", r"The eccentricity of $4x^2+y^2=16$.", "expression", "sqrt(3)/2", hints=["Here the major axis is vertical: $a=4$ and $b=2$."],
                    solution=r"$\dfrac{x^2}{4}+\dfrac{y^2}{16}=1$, so $a=4$, $b=2$, $c^2=16-4=12$, $c=2\sqrt3$ and $e=\dfrac{2\sqrt3}{4}=\dfrac{\sqrt3}2$."))
    items.append(ex("el-04", r"The length of the latus rectum of $\dfrac{x^2}{25}+\dfrac{y^2}{9}=1$.", "expression", "18/5", hints=["The length is $\\dfrac{2b^2}a$."],
                    solution=r"$\dfrac{2\cdot9}{5}=\dfrac{18}5$."))
    items.append(ex("el-05", r"The equation of the ellipse with foci $(\pm3,0)$ and $a=5$.", "equation", "x^2/25+y^2/16=1", coordinates=["x", "y"], hints=["$b^2=a^2-c^2$."],
                    solution=r"$b^2=25-9=16$, so $\dfrac{x^2}{25}+\dfrac{y^2}{16}=1$."))
    items.append(ex("el-06", r"The equation of the ellipse with foci $(\pm4,0)$ and eccentricity $\dfrac45$.", "equation", "x^2/25+y^2/9=1", coordinates=["x", "y"], hints=["$a=\\dfrac ce$."],
                    solution=r"$a=4\cdot\dfrac54=5$ and $b^2=25-16=9$."))
    items.append(ex("el-07", r"The center of $4x^2+9y^2-16x+18y-11=0$.", "vector", "(2, -1)", hints=["Complete the squares in $x$ and in $y$."],
                    solution=r"$4(x-2)^2+9(y+1)^2=11+16+9=36$, so the center is $(2,-1)$ and the semi-axes are $3$ and $2$."))
    items.append(ex("el-08", r"For a point $M$ of $\dfrac{x^2}{25}+\dfrac{y^2}{9}=1$, the sum $MF_1+MF_2$ of the distances to the foci.", "number", "10", hints=["The sum is constant."],
                    solution=r"It is $2a=10$."))
    items.append(ex("el-09", r"The tangent to $\dfrac{x^2}{25}+\dfrac{y^2}{16}=1$ at $\left(3,\dfrac{16}5\right)$.", "equation", "3*x+5*y=25", coordinates=["x", "y"], hints=["$\\dfrac{xx_0}{a^2}+\\dfrac{yy_0}{b^2}=1$."],
                    solution=r"$\dfrac{3x}{25}+\dfrac{\frac{16}5y}{16}=\dfrac{3x}{25}+\dfrac y5=1$, so $3x+5y=25$."))
    items.append(ex("el-10", r"The tangent to $\dfrac{x^2}{20}+\dfrac{y^2}{5}=1$ at $(2,2)$.", "equation", "x+4*y=10", coordinates=["x", "y"], hints=["Check that the point is on the ellipse."],
                    solution=r"$\dfrac{2x}{20}+\dfrac{2y}5=1$ gives $x+4y=10$."))
    return items


def l03() -> list[dict]:
    items = []
    items.append(ex("hy-01", r"The eccentricity of $16x^2-9y^2=144$.", "expression", "5/3", hints=["$c^2=a^2+b^2$."],
                    solution=r"$\dfrac{x^2}9-\dfrac{y^2}{16}=1$, $c^2=25$, $e=\dfrac53$."))
    items.append(ex("hy-02", r"The positive slope of the asymptotes of $\dfrac{x^2}{36}-\dfrac{y^2}{64}=1$.", "expression", "4/3", hints=["$\\dfrac ba$."],
                    solution=r"$a=6$, $b=8$: the slope is $\dfrac86=\dfrac43$."))
    items.append(ex("hy-03", r"The value of $c$ for $\dfrac{x^2}{20}-\dfrac{y^2}5=1$.", "expression", "5", hints=["$c^2=a^2+b^2$."], solution=r"$c^2=20+5=25$."))
    items.append(ex("hy-04", r"The equation of the hyperbola with vertices $(\pm4,0)$ and foci $(\pm5,0)$.", "equation", "x^2/16-y^2/9=1", coordinates=["x", "y"], hints=["$b^2=c^2-a^2$."],
                    solution=r"$a=4$, $c=5$, $b^2=25-16=9$."))
    items.append(ex("hy-05", r"The eccentricity of $4x^2-y^2=16$.", "expression", "sqrt(5)", hints=["Divide by $16$."],
                    solution=r"$\dfrac{x^2}4-\dfrac{y^2}{16}=1$, $c^2=20$, $e=\dfrac{2\sqrt5}2=\sqrt5$."))
    items.append(ex("hy-06", r"The tangent to $\dfrac{x^2}9-\dfrac{y^2}{16}=1$ at $\left(5,\dfrac{16}3\right)$.", "equation", "5*x-3*y=9", coordinates=["x", "y"], hints=["$\\dfrac{xx_0}{a^2}-\\dfrac{yy_0}{b^2}=1$."],
                    solution=r"$\dfrac{5x}9-\dfrac y3=1$, so $5x-3y=9$."))
    items.append(ex("hy-07", r"The tangent to $\dfrac{x^2}4-\dfrac{y^2}5=1$ at $\left(3,\dfrac52\right)$.", "equation", "3*x-2*y=4", coordinates=["x", "y"], hints=["Check that the point is on the hyperbola."],
                    solution=r"$\dfrac{3x}4-\dfrac{\frac52y}5=\dfrac{3x}4-\dfrac y2=1$, so $3x-2y=4$."))
    items.append(ex("hy-08", r"The distance between the vertices of the rectangular hyperbola $xy=8$.", "number", "8", hints=["Rotate by $\\dfrac\\pi4$: $x'^2-y'^2=16$."],
                    solution=r"After the rotation $x'^2-y'^2=16$, so $a=4$ and the vertices are $8$ apart. (Directly: the vertices are $(2\sqrt2,2\sqrt2)$ and its opposite.)"))
    items.append(ex("hy-09", r"For a point $M$ of $\dfrac{x^2}9-\dfrac{y^2}{16}=1$, the value of $\left|MF_1-MF_2\right|$.", "number", "6", hints=["It is constant."], solution=r"It is $2a=6$."))
    return items


def l04() -> list[dict]:
    items = []
    th = ["theta"]
    items.append(ex("po-01", r"The eccentricity of $r=\dfrac{15}{5-3\cos\varphi}$.", "expression", "3/5", hints=["Divide the numerator and the denominator by $5$."],
                    solution=r"$r=\dfrac{3}{1-\frac35\cos\varphi}$, so $e=\dfrac35$."))
    items.append(ex("po-02", r"The eccentricity of $r=\dfrac{8}{2-4\cos\varphi}$.", "number", "2", hints=["Divide by $2$."], solution=r"$r=\dfrac{4}{1-2\cos\varphi}$, so $e=2$: a hyperbola."))
    items.append(ex("po-03", r"The distance from the focus to the directrix of $r=\dfrac{12}{4-4\cos\varphi}$.", "number", "3", hints=["Here $e=1$."],
                    solution=r"$r=\dfrac{3}{1-\cos\varphi}$, so $e=1$ and $ed=3$ gives $d=3$."))
    items.append(ex("po-04", r"The polar equation of the conic with a focus at the pole, eccentricity $\dfrac12$ and directrix $x=-6$ (answer $r$ as a function of theta).", "expression", "6/(2-cos(theta))", variables=th,
                    hints=["$ed=3$."], solution=r"$r=\dfrac{3}{1-\frac12\cos\theta}=\dfrac{6}{2-\cos\theta}$."))
    items.append(ex("po-05", r"The semi-latus rectum of $r=\dfrac{9}{5-4\cos\varphi}$.", "expression", "9/5", hints=["It is $r$ at $\\varphi=\\dfrac\\pi2$."],
                    solution=r"$r=\dfrac95$ for $\varphi=\dfrac\pi2$."))
    items.append(ex("po-06", r"The semi-major axis $a$ of the ellipse $r=\dfrac{9}{5-4\cos\varphi}$.", "number", "5", hints=["The vertices are at $\\varphi=0$ and $\\varphi=\\pi$."],
                    solution=r"$r(0)=9$ and $r(\pi)=1$, so $2a=10$ and $a=5$."))
    items.append(ex("po-07", r"The semi-transverse axis $a$ of the hyperbola $r=\dfrac{16}{3-5\cos\varphi}$.", "number", "3", hints=["Use $a=\\dfrac{\\ell}{e^2-1}$ with $\\ell=\\dfrac{16}3$ and $e=\\dfrac53$."],
                    solution=r"$a=\dfrac{16/3}{25/9-1}=\dfrac{16/3}{16/9}=3$."))
    items.append(ex("po-08", r"The Cartesian equation of $r=\dfrac{4}{1-\cos\theta}$ (in the letters $x,y$).", "equation", "y^2=8*x+16", coordinates=["x", "y"], hints=["$r-r\\cos\\theta=4$ gives $r=x+4$."],
                    solution=r"$r=x+4$, so $x^2+y^2=(x+4)^2$ and $y^2=8x+16$: a parabola with vertex $(-2,0)$."))
    return items


def l05() -> list[dict]:
    items = []
    for n, (text, A, B, C) in enumerate((("5x^2+4xy+2y^2-6=0", 5, 2, 2), ("x^2+6xy+y^2-8=0", 1, 3, 1), ("x^2-2xy+y^2-4x-4y=0", 1, -1, 1), ("3x^2+10xy+3y^2-8=0", 3, 5, 3)), 1):
        d = A * C - B * B
        items.append(ex(f"gs-{n:02d}", rf"The invariant $\delta=AC-B^2$ of ${text}$ (the cross term is $2Bxy$).", "number", str(d), hints=[f"Here $A={A}$, $B={B}$, $C={C}$."],
                        solution=rf"$\delta={A}\cdot{C}-({B})^2={d}$."))
    kinds = (("4x^2+9y^2-36=0", "1"), ("x^2+4xy+y^2-3=0", "2"), ("x^2-2xy+y^2-4x-4y=0", "3"))
    reasons = (r"$\delta=36>0$ and $\Delta S<0$: a real ellipse.", r"$\delta=1-4=-3<0$ and $\Delta\ne0$: a hyperbola.",
               r"$\delta=0$ and $\Delta=-16\ne0$: a parabola.")
    items.append(ex("gs-05", rf"What kind of curve is ${kinds[0][0]}$?", "multiple_choice", "1", choices=conic_choices(), correctIndex=0, hints=["Compute $\\delta$."], solution=reasons[0]))
    items.append(ex("gs-06", rf"What kind of curve is ${kinds[1][0]}$?", "multiple_choice", "2", choices=conic_choices(), correctIndex=1, hints=["Compute $\\delta$."], solution=reasons[1]))
    items.append(ex("gs-07", rf"What kind of curve is ${kinds[2][0]}$?", "multiple_choice", "3", choices=conic_choices(), correctIndex=2, hints=["Compute $\\delta$."], solution=reasons[2]))
    items.append(ex("gs-08", r"The rotation angle $\varphi\in\left]0,\dfrac\pi2\right[$ that removes the cross term of $x^2+6xy+y^2-8=0$.", "expression", "pi/4", hints=["$A=C$."],
                    solution=r"$A=C$, so $\varphi=\dfrac\pi4$."))
    items.append(ex("gs-09", r"After a rotation, $3x^2+2xy+3y^2-8=0$ becomes $\dfrac{x'^2}{p}+\dfrac{y'^2}{q}=1$ with $p<q$. Find $q$.", "number", "4", hints=["The new coefficients are the roots of $\\lambda^2-6\\lambda+8=0$."],
                    solution=r"The roots are $4$ and $2$: $4x'^2+2y'^2=8$, that is $\dfrac{x'^2}2+\dfrac{y'^2}4=1$. So $p=2$ and $q=4$."))
    items.append(ex("gs-10", r"After the rotation that removes the cross term of $7x^2+2xy+7y^2-24=0$, find the larger of the two new coefficients of $x'^2$ and $y'^2$.", "number", "8", hints=["The roots of $\\lambda^2-14\\lambda+48=0$."],
                    solution=r"$\delta=49-1=48$, $S=14$: $\lambda^2-14\lambda+48=0$ has roots $6$ and $8$. The equation becomes $6x'^2+8y'^2=24$."))
    return items


def l06() -> list[dict]:
    items = []
    items.append(ex("lo-01", r"The locus of the points $M$ with $MA=MB$, where $A(2,0)$ and $B(0,4)$.", "equation", "x-2*y=-3", coordinates=["x", "y"], hints=["Square the distances and expand."],
                    solution=r"$(x-2)^2+y^2=x^2+(y-4)^2$ gives $-4x+4=-8y+16$, so $x-2y=-3$."))
    items.append(ex("lo-02", r"The radius of the locus of the points $M$ with $MA^2+MB^2=50$, where $A(-3,0)$ and $B(3,0)$.", "number", "4", hints=["$MA^2+MB^2=2x^2+2y^2+18$."],
                    solution=r"$2x^2+2y^2+18=50$ gives $x^2+y^2=16$: radius $4$."))
    items.append(ex("lo-03", r"The center of the locus of the points $M$ with $MA=2\,MB$, where $A(0,0)$ and $B(3,0)$.", "vector", "(4, 0)", hints=["Square and complete the square."],
                    solution=r"$x^2+y^2=4\left((x-3)^2+y^2\right)$ gives $(x-4)^2+y^2=4$: center $(4,0)$, radius $2$."))
    items.append(ex("lo-04", r"The locus of the points $M$ equidistant from the point $F(0,2)$ and from the line $y=-2$.", "equation", "x^2=8*y", coordinates=["x", "y"], hints=["It is a parabola: $p=4$."],
                    solution=r"$x^2+(y-2)^2=(y+2)^2$ gives $x^2=8y$."))
    items.append(ex("lo-05", r"The sum of the distances from $M$ to $F_1(-4,0)$ and $F_2(4,0)$ is $10$. Find the locus.", "equation", "x^2/25+y^2/9=1", coordinates=["x", "y"], hints=["$2a=10$ and $c=4$."],
                    solution=r"$a=5$, $c=4$, $b^2=9$: $\dfrac{x^2}{25}+\dfrac{y^2}9=1$."))
    items.append(ex("lo-06", r"The absolute value of the difference of the distances from $M$ to $F_1(-5,0)$ and $F_2(5,0)$ is $6$. Find the locus.", "equation", "x^2/9-y^2/16=1", coordinates=["x", "y"], hints=["$2a=6$ and $c=5$."],
                    solution=r"$a=3$, $c=5$, $b^2=16$: $\dfrac{x^2}9-\dfrac{y^2}{16}=1$."))
    return items


def build() -> None:
    write_exercises(f"{BASE}/l01-the-parabola", [exset("parabola", "The parabola.", l01(), format=FMT)], "geo_conics.py")
    write_exercises(f"{BASE}/l02-the-ellipse", [exset("ellipse", "The ellipse.", l02(), format=FMT)], "geo_conics.py")
    write_exercises(f"{BASE}/l03-the-hyperbola", [exset("hyperbola", "The hyperbola.", l03(), format=FMT)], "geo_conics.py")
    write_exercises(f"{BASE}/l04-focus-directrix-and-polar-equation", [exset("polar-conics", "Conics in polar form.", l04(), format=FMT)], "geo_conics.py")
    write_exercises(f"{BASE}/l05-general-second-degree-equation", [exset("general", "The general second-degree equation.", l05(), format=FMT)], "geo_conics.py")
    write_exercises(f"{BASE}/l06-loci", [exset("loci", "Loci.", l06(), format=FMT)], "geo_conics.py")
