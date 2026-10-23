"""More practice for Course 1, Module 2, Units 4 and 5: polar coordinates, change of axes, conics and loci.

Conics are built from their parameters; every property is computed exactly and checked with the defining distance property."""

from __future__ import annotations

import math

import sympy as sp
from toolkit import add_extra, eng, ex, exset_plain, simp, tex, with_units, x, y

SCRIPT = "more_geo_c.py"
U4 = "geo/m02-plane/u04-polar-coordinates-and-curves"
U5 = "geo/m02-plane/u05-conics-and-loci"
FMT = "Type a point as `(a, b)`, an exact value such as `5/13` or `sqrt(7)/3`, an equation with `=`, and a list of points as `(a, b), (c, d)`."
th, rr = sp.symbols("theta r", real=True)
R = sp.Rational


def pe(p) -> str:
    return "(" + ", ".join(eng(c) for c in p) + ")"


def pt(p) -> str:
    return r"\left(" + r",\,".join(tex(c) for c in p) + r"\right)"


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


def normalize(poly: sp.Expr) -> sp.Expr:
    """Integer coefficients without a common factor and a positive leading coefficient."""
    poly = sp.expand(poly)
    p = sp.Poly(poly, x, y)
    den = sp.ilcm(*[sp.fraction(c)[1] for c in p.coeffs()])
    p = sp.Poly(sp.expand(poly * den), x, y)
    g = sp.igcd(*[int(c) for c in p.coeffs()])
    poly = sp.expand(poly * den / g)
    lead = sp.Poly(poly, x, y).coeffs()[0]
    return -poly if lead < 0 else poly


def eq_of(poly: sp.Expr) -> str:
    return f"{eng(normalize(poly))}=0"


def eq_tex(poly: sp.Expr) -> str:
    return f"{tex(normalize(poly))}=0"


# --- unit 4 ---------------------------------------------------------------------------------------------------------------------------------
def polar_equation_items() -> list[dict]:
    items = []

    def to_polar(i: str, cart: sp.Expr, rexpr: sp.Expr, cart_tex: str, hint: str) -> None:
        sub = sp.simplify(cart.subs({x: rr * sp.cos(th), y: rr * sp.sin(th)}))
        resid = sp.simplify(sub.subs(rr, rexpr))
        assert resid == 0, (cart, rexpr, resid)
        items.append(ex(f"mp-pe-{i}", rf"Write the curve ${cart_tex}$ in polar form $r=\dots$ (an expression in theta).", "expression", eng(rexpr), variables=["theta"], hints=[hint],
                        solution=rf"With $x=r\cos\theta$ and $y=r\sin\theta$, the equation becomes $r={tex(rexpr)}$."))

    to_polar("1", x**2 + y**2 - 10 * x, 10 * sp.cos(th), "x^2+y^2=10x", r"Use $x^2+y^2=r^2$ and $x=r\cos\theta$, then divide by $r$.")
    to_polar("2", x**2 + y**2 + 6 * y, -6 * sp.sin(th), "x^2+y^2+6y=0", r"Use $x^2+y^2=r^2$ and $y=r\sin\theta$, then divide by $r$.")
    to_polar("3", 2 * x + 3 * y - 6, 6 / (2 * sp.cos(th) + 3 * sp.sin(th)), "2x+3y=6", r"Put $x=r\cos\theta$, $y=r\sin\theta$ and solve for $r$.")

    def to_cart(i: str, rexpr: sp.Expr, rtex: str, cart: sp.Expr) -> None:
        # points of the Cartesian curve must satisfy the polar equation: check on sample angles
        for tv in (0.3, 0.9, 1.4, 2.1, 2.9):
            rv = float(rexpr.subs(th, tv))
            xv, yv = rv * math.cos(tv), rv * math.sin(tv)
            assert abs(float(cart.subs({x: xv, y: yv}))) < 1e-9, (rtex, tv)
        items.append(ex(f"mp-pe-{i}", rf"Write the curve $r={rtex}$ as a Cartesian equation.", "equation", eq_of(cart), coordinates=["x", "y"],
                        hints=[r"Multiply by $r$ (or $\cos\theta$) to make $x=r\cos\theta$ and $y=r\sin\theta$ appear."],
                        solution=rf"The Cartesian equation is ${eq_tex(cart)}$ (any non-zero multiple is accepted)."))

    to_cart("4", 4 * sp.cos(th) + 4 * sp.sin(th), r"4\cos\theta+4\sin\theta", x**2 + y**2 - 4 * x - 4 * y)
    to_cart("5", 3 / sp.sin(th), r"\dfrac{3}{\sin\theta}", y - 3)
    to_cart("6", 2 / (sp.cos(th) + sp.sin(th)), r"\dfrac{2}{\cos\theta+\sin\theta}", x + y - 2)
    return items


def polar_curve_items() -> list[dict]:
    return [ex("mp-pk-1", r"The number of petals of the rose $r=4\cos6\theta$.", "number", "12", hints=["Odd $n$: $n$ petals. Even $n$: $2n$ petals."], solution=r"The coefficient $6$ is even, so the rose has $2\cdot6=12$ petals.")]


def axes_items() -> list[dict]:
    items = []
    for n, (p, o) in enumerate((((7, 2), (3, -1)), ((-2, 5), (1, 1))), 1):
        new = (p[0] - o[0], p[1] - o[1])
        items.append(ex(f"mp-ax-{n}", rf"After moving the origin to $O'{pt(o)}$, find the new coordinates of $M{pt(p)}$.", "vector", pe(new), hints=[r"$x'=x-a$, $y'=y-b$."],
                        solution=rf"$x'={p[0]}-({o[0]})={new[0]}$ and $y'={p[1]}-({o[1]})={new[1]}$."))

    def translate(i: str, f: sp.Expr, o: tuple, ftex: str) -> None:
        X, Y = sp.symbols("X Y", real=True)
        g = sp.expand(f.subs({x: X + o[0], y: Y + o[1]}, simultaneous=True)).subs({X: x, Y: y}, simultaneous=True)
        items.append(ex(f"mp-ax-{i}", rf"The curve ${ftex}=0$ is described in axes with the new origin $O'{pt(o)}$. Write its equation in the new coordinates (using the letters $x$ and $y$).", "equation", eq_of(g), coordinates=["x", "y"],
                        hints=[r"Replace $x$ by $x+a$ and $y$ by $y+b$ and expand."], solution=rf"Substituting $x\to x+{o[0]}$, $y\to y+{o[1]}$ gives ${eq_tex(g)}$."))

    translate("3", x**2 + y**2 - 6 * x + 2 * y + 6, (3, -1), "x^2+y^2-6x+2y+6")
    translate("4", y**2 - 4 * y - 8 * x + 20, (2, 2), "y^2-4y-8x+20")
    for n, (p, ang, ang_tex) in enumerate((((1, 1), sp.pi / 4, r"\dfrac\pi4"), ((4, 0), sp.pi / 3, r"\dfrac\pi3")), 5):
        X = simp(p[0] * sp.cos(ang) + p[1] * sp.sin(ang))
        Y = simp(-p[0] * sp.sin(ang) + p[1] * sp.cos(ang))
        items.append(ex(f"mp-ax-{n}", rf"The axes are rotated by ${ang_tex}$. Find the new coordinates of $M{pt(p)}$.", "vector", pe((X, Y)),
                        hints=[r"$x'=x\cos\varphi+y\sin\varphi$ and $y'=-x\sin\varphi+y\cos\varphi$."], solution=rf"$x'={tex(X)}$ and $y'={tex(Y)}$."))
    # rotation of an equation by pi/4
    Xs, Ys = sp.symbols("X Y", real=True)
    c, s_ = sp.sqrt(2) / 2, sp.sqrt(2) / 2
    sub = {x: Xs * c - Ys * s_, y: Xs * s_ + Ys * c}
    f1 = sp.expand(sp.simplify((x**2 + 4 * x * y + y**2 - 6).subs(sub, simultaneous=True)))
    assert sp.expand(f1 - (3 * Xs**2 - Ys**2 - 6)) == 0
    items.append(ex("mp-ax-7", r"The axes are rotated by $\dfrac\pi4$. Write $x^2+4xy+y^2=6$ in the new coordinates (using the letters $x$ and $y$).", "equation", "3*x^2-y^2=6", coordinates=["x", "y"],
                    hints=[r"Replace $x$ and $y$ by $\dfrac{\sqrt2}2(x'-y')$ and $\dfrac{\sqrt2}2(x'+y')$."], solution=r"$x^2+y^2=x'^2+y'^2$ and $4xy=2\left(x'^2-y'^2\right)$, so the equation is $3x'^2-y'^2=6$."))
    f2 = sp.expand(sp.simplify((2 * x * y - 1).subs(sub, simultaneous=True)))
    assert sp.expand(f2 - (Xs**2 - Ys**2 - 1)) == 0
    items.append(ex("mp-ax-8", r"The axes are rotated by $\dfrac\pi4$. Write $2xy=1$ in the new coordinates (using the letters $x$ and $y$).", "equation", "x^2-y^2=1", coordinates=["x", "y"],
                    hints=[r"$2xy=x'^2-y'^2$ after the rotation."], solution=r"$2xy=x'^2-y'^2$, so the equation is $x'^2-y'^2=1$: a hyperbola."))
    return items


# --- unit 5: conics -------------------------------------------------------------------------------------------------------------------------
def parabola_items() -> list[dict]:
    items = []
    h, k, p = 1, -2, 3  # (y-k)^2 = 4p (x-h): opens to the right
    f = (y - k) ** 2 - 4 * p * (x - h)
    gen = sp.expand(f)
    vertex, focus = (h, k), (h + p, k)
    # defining property at a sample point
    ty = 5
    tx = h + (ty - k) ** 2 / (4 * p)
    assert abs(math.hypot(tx - focus[0], ty - focus[1]) - abs(tx - (h - p))) < 1e-9
    items.append(ex("mp-pa-1", rf"The vertex of the parabola ${tex(gen)}=0$.", "vector", pe(vertex), hints=[r"Complete the square in $y$."],
                    solution=rf"${tex(gen)}=0$ gives $(y+2)^2=12(x-1)$: the vertex is $(1,-2)$."))
    items.append(ex("mp-pa-2", rf"The focus of the parabola ${tex(gen)}=0$.", "vector", pe(focus), hints=[r"Write it as $(y-k)^2=4p(x-h)$: the focus is $p$ to the right of the vertex."],
                    solution=r"$(y+2)^2=12(x-1)$ gives $4p=12$, so $p=3$ and the focus is $(1+3,-2)=(4,-2)$."))
    items.append(ex("mp-pa-3", rf"The directrix of the parabola ${tex(gen)}=0$.", "equation", f"x={h - p}", coordinates=["x", "y"], hints=[r"The directrix is $p$ to the left of the vertex."],
                    solution=r"The vertex is at $x=1$ and $p=3$, so the directrix is $x=1-3=-2$."))
    F, d = (0, 2), -2  # focus (0,2), directrix y=-2  ->  x^2 = 8y
    cond = sp.expand(x**2 + (y - 2) ** 2 - (y + 2) ** 2)
    assert normalize(cond) == normalize(x**2 - 8 * y)
    items.append(ex("mp-pa-4", r"Find the equation of the parabola with focus $(0,2)$ and directrix $y=-2$.", "equation", "x^2=8*y", coordinates=["x", "y"], hints=[r"A point $(x,y)$ is at equal distances from the focus and the directrix."],
                    solution=r"$x^2+(y-2)^2=(y+2)^2$ gives $x^2=8y$."))
    assert d == -2 and F == (0, 2)
    return items


def ellipse_items() -> list[dict]:
    items = []
    h, k, a, b = 2, -1, 3, 2
    poly = normalize(b**2 * (x - h) ** 2 + a**2 * (y - k) ** 2 - a**2 * b**2)
    c = sp.sqrt(a**2 - b**2)
    foci = [(h - c, k), (h + c, k)]
    # the defining property: sum of distances 2a at a sample point
    t0 = 0.7
    px, py = h + a * math.cos(t0), k + b * math.sin(t0)
    assert abs(sum(math.hypot(px - f[0], py - f[1]) for f in foci_f(foci)) - 2 * a) < 1e-9
    items.append(ex("mp-el-1", rf"The center of the ellipse ${tex(poly)}=0$.", "vector", pe((h, k)), hints=[r"Complete the squares in $x$ and in $y$."],
                    solution=rf"${tex(poly)}=0$ becomes $\dfrac{{(x-2)^2}}{{9}}+\dfrac{{(y+1)^2}}{{4}}=1$: the center is $(2,-1)$."))
    items.append(ex("mp-el-2", rf"The foci of the ellipse ${tex(poly)}=0$ (give the two points).", "points", ", ".join(pe(f) for f in foci), hints=[r"$c^2=a^2-b^2$, on the major axis."],
                    solution=rf"$a^2=9$, $b^2=4$, so $c=\sqrt5$. The major axis is horizontal: the foci are ${pt(foci[0])}$ and ${pt(foci[1])}$."))
    e = simp(c / a)
    items.append(ex("mp-el-3", rf"The eccentricity of the ellipse ${tex(poly)}=0$.", "expression", eng(e), hints=[r"$e=\dfrac ca$."], solution=rf"$e=\dfrac{{\sqrt5}}{{3}}={tex(e)}$."))
    items.append(ex("mp-el-4", rf"The length of the minor axis of the ellipse ${tex(poly)}=0$. The unit is lu: give the number only.", "number", str(2 * b), hints=[r"The minor axis is $2b$."], solution=r"$b^2=4$, so the minor axis has length $2b=4$."))
    foc, s_ = (3, 0), 10  # foci (+-3, 0), sum 10 -> a=5, b=4
    a2 = s_ // 2
    b2 = sp.sqrt(a2**2 - foc[0] ** 2)
    items.append(ex("mp-el-5", r"Find the equation of the ellipse whose points have distances to $(-3,0)$ and $(3,0)$ adding up to $10$.", "equation", "x^2/25+y^2/16=1", coordinates=["x", "y"],
                    hints=[r"$2a=10$ and $c=3$, so $b^2=a^2-c^2$."], solution=r"$a=5$, $c=3$, $b^2=25-9=16$: $\dfrac{x^2}{25}+\dfrac{y^2}{16}=1$."))
    assert b2 == 4
    return items


def foci_f(foci):
    return [(float(f[0]), float(f[1])) for f in foci]


def hyperbola_items() -> list[dict]:
    items = []
    h, k, a, b = 1, 2, 3, 4
    poly = normalize(b**2 * (x - h) ** 2 - a**2 * (y - k) ** 2 - a**2 * b**2)
    c = sp.sqrt(a**2 + b**2)
    verts = [(h - a, k), (h + a, k)]
    foci = [(h - c, k), (h + c, k)]
    t0 = 0.8
    px, py = h + a * math.cosh(t0), k + b * math.sinh(t0)
    assert abs(abs(math.hypot(px - foci[0][0], py - foci[0][1]) - math.hypot(px - foci[1][0], py - foci[1][1])) - 2 * a) < 1e-9
    items.append(ex("mp-hy-1", rf"The center of the hyperbola ${tex(poly)}=0$.", "vector", pe((h, k)), hints=[r"Complete the squares in $x$ and in $y$."],
                    solution=r"The equation becomes $\dfrac{(x-1)^2}{9}-\dfrac{(y-2)^2}{16}=1$: the center is $(1,2)$."))
    items.append(ex("mp-hy-2", rf"The vertices of the hyperbola ${tex(poly)}=0$ (give the two points).", "points", ", ".join(pe(v) for v in verts), hints=[r"The vertices are $a$ to the left and to the right of the center."],
                    solution=r"$a^2=9$, so $a=3$: the vertices are $(-2,2)$ and $(4,2)$."))
    items.append(ex("mp-hy-3", rf"The foci of the hyperbola ${tex(poly)}=0$ (give the two points).", "points", ", ".join(pe(f) for f in foci), hints=[r"$c^2=a^2+b^2$."],
                    solution=r"$c^2=9+16=25$, so $c=5$: the foci are $(-4,2)$ and $(6,2)$."))
    items.append(ex("mp-hy-4", rf"The eccentricity of the hyperbola ${tex(poly)}=0$.", "expression", eng(sp.Rational(5, 3)), hints=[r"$e=\dfrac ca$."], solution=r"$e=\dfrac53$."))
    asym = normalize((y - k) - sp.Rational(b, a) * (x - h))
    items.append(ex("mp-hy-5", rf"An asymptote of the hyperbola ${tex(poly)}=0$ with positive slope.", "equation", eq_of(asym), coordinates=["x", "y"], hints=[r"The asymptotes are $y-k=\pm\dfrac ba(x-h)$."],
                    solution=rf"The slopes are $\pm\dfrac43$; the one with positive slope is $y-2=\dfrac43(x-1)$, that is ${eq_tex(asym)}$."))
    items.append(ex("mp-hy-6", r"Find the equation of the hyperbola with foci $(\pm5,0)$ whose points have distances to the foci differing by $6$.", "equation", "x^2/9-y^2/16=1", coordinates=["x", "y"],
                    hints=[r"$2a=6$ and $c=5$, so $b^2=c^2-a^2$."], solution=r"$a=3$, $c=5$, $b^2=25-9=16$: $\dfrac{x^2}{9}-\dfrac{y^2}{16}=1$."))
    return items


def focus_directrix_items() -> list[dict]:
    items = []
    for n, (e, name, idx) in enumerate(((R(1, 2), "an ellipse", 0), (R(3, 2), "a hyperbola", 1), (1, "a parabola", 2)), 1):
        items.append(mc(f"mp-fd-{n}", rf"A conic has eccentricity $e={tex(sp.Rational(e))}$. It is", ["an ellipse", "a hyperbola", "a parabola"], idx, r"Compare $e$ with $1$.",
                        rf"$e<1$ ellipse, $e=1$ parabola, $e>1$ hyperbola: here it is {name}."))
    e0, p0 = 2, 3  # r = e p / (1 + e cos(theta)) = 6/(1+2cos)
    items.append(ex("mp-fd-4", r"A conic has the polar equation $r=\dfrac{6}{1+2\cos\theta}$. Find its eccentricity.", "number", "2", hints=[r"Compare with $r=\dfrac{ep}{1+e\cos\theta}$."], solution=r"The coefficient of $\cos\theta$ in the denominator is $e=2$."))
    items.append(ex("mp-fd-5", r"A conic has the polar equation $r=\dfrac{6}{1+2\cos\theta}$. Find the distance $p$ from the focus to the directrix.", "number", "3", hints=[r"$ep=6$."], solution=r"$ep=6$ and $e=2$, so $p=3$."))
    # Cartesian equation of the conic r = 4/(1+cos theta) (parabola): r + x = 4 -> y^2 = 8(2 - x)... computed
    cart = sp.expand((4 - x) ** 2 - (x**2 + y**2))
    assert normalize(cart) == normalize(y**2 + 8 * x - 16)
    items.append(ex("mp-fd-6", r"Write the conic $r=\dfrac{4}{1+\cos\theta}$ as a Cartesian equation.", "equation", "y^2+8*x=16", coordinates=["x", "y"], hints=[r"Multiply by the denominator: $r+r\cos\theta=4$, so $r=4-x$; square."],
                    solution=r"$r+x=4$ gives $r=4-x$; squaring, $x^2+y^2=(4-x)^2$, that is $y^2+8x=16$."))
    items.append(ex("mp-fd-7", r"A point moves so that its distance to the point $(2,0)$ is half of its distance to the line $x=8$. Its eccentricity is", "expression", "1/2", hints=[r"The ratio of the distances is the eccentricity."], solution=r"$e=\dfrac{\text{distance to the focus}}{\text{distance to the directrix}}=\dfrac12$: an ellipse."))
    return items


def general_items() -> list[dict]:
    items = []
    for n, ((A, B, C), idx, name) in enumerate((((1, 0, 4), 0, "an ellipse"), ((1, 2, 1), 2, "a parabola"), ((1, 4, 1), 1, "a hyperbola")), 1):
        disc = B * B - 4 * A * C
        kinds = ["an ellipse", "a hyperbola", "a parabola"]
        correct = 0 if disc < 0 else (2 if disc == 0 else 1)
        eq = f"{'' if A == 1 else A}x^2{'+' + str(B) + 'xy' if B else ''}+{C}y^2+x-y-5=0".replace("+-", "-")
        items.append(mc(f"mp-gs-{n}", rf"The equation ${eq}$ (a general second-degree equation, if it has points) represents", kinds, correct, r"Compute $B^2-4AC$.",
                        rf"$A={A}$, $B={B}$, $C={C}$: $B^2-4AC={disc}$, so the curve is {kinds[correct]}."))
    # rotation angle: tan 2 theta = B/(A-C)
    items.append(ex("mp-gs-4", r"The term $xy$ of $x^2+2\sqrt3\,xy+3y^2-8=0$ is removed by rotating the axes through an acute angle $\theta$. Find $\theta$.", "expression", "pi/3", hints=[r"$\tan2\theta=\dfrac{B}{A-C}$."],
                    solution=r"$\tan2\theta=\dfrac{2\sqrt3}{1-3}=-\sqrt3$, so $2\theta=\dfrac{2\pi}{3}$ and $\theta=\dfrac\pi3$ (acute)."))
    th_ = sp.atan(2) / 2
    items.append(ex("mp-gs-5", r"For $x^2+xy+y^2=3$, $A=C$: the axes must be rotated by what angle to remove the $xy$ term?", "expression", "pi/4", hints=[r"When $A=C$, $\tan2\theta$ is infinite."],
                    solution=r"$A-C=0$ gives $2\theta=\dfrac\pi2$, so $\theta=\dfrac\pi4$."))
    assert th_ is not None
    return items


def loci_items() -> list[dict]:
    items = []

    def locus(i: str, stmt: str, cond: sp.Expr, expected: sp.Expr, sol: str, hint: str, samples) -> None:
        e = sp.expand(cond)
        if expected is None:
            expected = e
        assert normalize(e) == normalize(expected), (normalize(e), normalize(expected))
        for sx in samples:
            for sy in sp.solve(expected.subs(x, sx), y):
                if sy.is_real:
                    assert abs(float(cond.subs({x: sx, y: sy}))) < 1e-9
        items.append(ex(f"mp-lo-{i}", stmt, "equation", eq_of(expected), coordinates=["x", "y"], hints=[hint], solution=sol + rf" The equation is ${eq_tex(expected)}$."))

    d = lambda p, q: (x - p[0]) ** 2 + (y - p[1]) ** 2  # noqa: E731
    locus("1", r"Find the locus of the points equidistant from $A(1,2)$ and $B(5,4)$.", d((1, 2), (0, 0)) - d((5, 4), (0, 0)), None, r"$PA^2=PB^2$ gives $-2x-4y+5=-10x-8y+41$.",
          r"Write $PA^2=PB^2$ and expand.", (0, 1, 3))
    locus("2", r"Find the locus of the points at equal distances from the point $(0,3)$ and the line $y=-3$.", x**2 + (y - 3) ** 2 - (y + 3) ** 2, x**2 - 12 * y, r"The distance to the focus equals the distance to the directrix: $x^2+(y-3)^2=(y+3)^2$.",
          r"A point $(x,y)$ is at distance $|y+3|$ from the line.", (0, 1, 2, 4))
    locus("3", r"Find the locus of the points whose distances to $(\pm3,0)$ add up to $10$.", 16 * x**2 + 25 * y**2 - 400, 16 * x**2 + 25 * y**2 - 400, r"This is an ellipse with $2a=10$ and $c=3$, so $b^2=16$.",
          r"It is an ellipse with foci $(\pm3,0)$ and $2a=10$.", (0, 1, 3))
    locus("4", r"Find the locus of the points whose distances to $(\pm5,0)$ differ by $6$ (in absolute value).", 16 * x**2 - 9 * y**2 - 144, 16 * x**2 - 9 * y**2 - 144, r"This is a hyperbola with $2a=6$ and $c=5$, so $b^2=16$.",
          r"It is a hyperbola with foci $(\pm5,0)$ and $2a=6$.", (3, 4, 5))
    # Apollonius: PA = 2 PB with A(0,0), B(3,0)
    cond = x**2 + y**2 - 4 * ((x - 3) ** 2 + y**2)
    exp = x**2 + y**2 - 8 * x + 12
    locus("5", r"Find the locus of the points $P$ with $PA=2\,PB$, where $A(0,0)$ and $B(3,0)$.", cond * 1, -3 * exp, r"$PA^2=4PB^2$ gives $x^2+y^2=4\left[(x-3)^2+y^2\right]$; this is a circle (of Apollonius).", r"Square both sides.", (2, 3, 4))
    # midpoints of segments from (4,0) to the circle x^2+y^2=4: circle center (2,0) radius 1
    exp = (x - 2) ** 2 + y**2 - 1
    for tv in (0.3, 1.1, 2.0, 3.5):
        q = (2 * math.cos(tv), 2 * math.sin(tv))
        m = ((4 + q[0]) / 2, (0 + q[1]) / 2)
        assert abs(float(exp.subs({x: m[0], y: m[1]}))) < 1e-9
    items.append(ex("mp-lo-6", r"Find the locus of the midpoints of the segments joining $A(4,0)$ to the points of the circle $x^2+y^2=4$.", "equation", eq_of(exp), coordinates=["x", "y"],
                    hints=[r"If $Q(u,v)$ is on the circle, the midpoint is $x=\dfrac{4+u}{2}$, $y=\dfrac v2$."], solution=r"With $u=2x-4$ and $v=2y$ in $u^2+v^2=4$: $(2x-4)^2+4y^2=4$, that is $(x-2)^2+y^2=1$."))
    # PA^2 + PB^2 = 20, A(-2,0), B(2,0): x^2+y^2=6
    cond = (x + 2) ** 2 + y**2 + (x - 2) ** 2 + y**2 - 20
    assert normalize(cond) == normalize(x**2 + y**2 - 6)
    items.append(ex("mp-lo-7", r"Find the locus of the points $P$ with $PA^2+PB^2=20$, where $A(-2,0)$ and $B(2,0)$.", "equation", eq_of(x**2 + y**2 - 6), coordinates=["x", "y"],
                    hints=[r"Expand both squares."], solution=r"$(x+2)^2+y^2+(x-2)^2+y^2=20$ gives $2x^2+2y^2+8=20$, so $x^2+y^2=6$."))
    items.append(mc("mp-lo-8", r"The points at distance $3$ from the line $3x+4y=0$ form", ["one line", "two parallel lines", "a circle", "a parabola"], 1, r"The distance to the line is $\dfrac{|3x+4y|}{5}$.",
                    r"$\dfrac{|3x+4y|}{5}=3$ gives $3x+4y=15$ or $3x+4y=-15$: two parallel lines."))
    items.append(mc("mp-lo-9", r"The points whose distances to two fixed points have a constant ratio different from $1$ form", ["a line", "a circle", "a parabola", "a hyperbola"], 1, r"Square the condition: the $x^2$ and $y^2$ terms stay equal.",
                    r"This is the circle of Apollonius. (When the ratio is $1$, the locus is the perpendicular bisector, a line.)"))
    return items


@with_units
def register() -> None:
    sets = [
        (U4, "l02-lines-and-circles-in-polar-form", "more-polar-equations", "More practice: equations in polar form.", polar_equation_items()),
        (U4, "l03-polar-curves", "more-curves", "More practice: polar curves.", polar_curve_items()),
        (U4, "l04-change-of-axes", "more-axes", "More practice: change of axes.", axes_items()),
        (U5, "l01-the-parabola", "more-parabola", "More practice: the parabola.", parabola_items()),
        (U5, "l02-the-ellipse", "more-ellipse", "More practice: the ellipse.", ellipse_items()),
        (U5, "l03-the-hyperbola", "more-hyperbola", "More practice: the hyperbola.", hyperbola_items()),
        (U5, "l04-focus-directrix-and-polar-equation", "more-focus", "More practice: focus, directrix and eccentricity.", focus_directrix_items()),
        (U5, "l05-general-second-degree-equation", "more-general", "More practice: the general second-degree equation.", general_items()),
        (U5, "l06-loci", "more-loci", "More practice: loci.", loci_items()),
    ]
    for unit, lesson, sid, task, items in sets:
        add_extra(f"{unit}/{lesson}", exset_plain(sid, task, items, format=FMT), SCRIPT)
