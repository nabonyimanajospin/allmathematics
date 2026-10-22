"""Exercises of Course 2, Module 1, Units 3 and 4: tangent planes, normal lines, local and constrained extrema
(sheet parts A.VIII and A.IX)."""

from __future__ import annotations

import math

import sympy as sp
from toolkit import P, check_partial, dtex, eng, ex, exset, simp, tex, write_exercises, x, y, z

BASE = "mvc/m01-derivatives"
a, b, c, x0, y0, z0 = (sp.Symbol(n, real=True) for n in ("a", "b", "c", "x0", "y0", "z0"))


def reduce_int(vec: list[sp.Expr]) -> list[sp.Expr]:
    """Divide an integer vector by the gcd of its entries (and keep the sign of the first non-zero entry)."""
    if all(v.is_Integer for v in vec):
        g = math.gcd(*[int(v) for v in vec])
        vec = [v / g for v in vec]
    return vec


# --- A.VIII tangent planes and normal lines -------------------------------------------------------------------------
def tangent_items() -> list[dict]:
    items: list[dict] = []

    def surface(n: int, name: str, latex: str, F: sp.Expr, point: tuple, graph: bool, pt_latex: str):
        grad = [sp.diff(F, s) for s in (x, y, z)]
        at = {x: point[0], y: point[1], z: point[2]}
        assert simp(F.subs(at)) == 0, f"the point is not on the surface {latex}"
        n_vec = reduce_int([simp(g.subs(at)) for g in grad])
        poly = sp.expand(sum(g.subs(at) * (s - p) for g, s, p in zip(grad, (x, y, z), point, strict=True)))
        if all(co.is_Rational for co in sp.Poly(poly, x, y, z).coeffs()):
            den = sp.ilcm(*[sp.fraction(co)[1] for co in sp.Poly(poly, x, y, z).coeffs()])
            poly = sp.expand(poly * den)
            g = math.gcd(*[int(co) for co in sp.Poly(poly, x, y, z).coeffs()])
            poly = sp.expand(poly / g)
        for s in (x, y, z):
            check_partial(F, s, sp.diff(F, s), [{x: 1.3, y: 0.7, z: 1.9}])
        key = f"{eng(poly)}=0"
        if graph:
            how = (
                rf"The surface is the graph $z=f(x,y)$ with $f=\,${tex(F + z)}$\,$, so $f_x={tex(simp(grad[0].subs(at)))}$ and "
                rf"$f_y={tex(simp(grad[1].subs(at)))}$ at the point. The tangent plane is "
                rf"$z-{tex(point[2])}=f_x\,(x-{tex(point[0])})+f_y\,(y-{tex(point[1])})$."
            )
        else:
            how = (
                rf"Take $F(x,y,z)={tex(F)}$. Then $(F_x,F_y,F_z)=\left({tex(grad[0])},\,{tex(grad[1])},\,{tex(grad[2])}\right)$, "
                rf"which at the point equals $\left({tex(simp(grad[0].subs(at)))},\,{tex(simp(grad[1].subs(at)))},\,{tex(simp(grad[2].subs(at)))}\right)$."
            )
        # a plain, readable plane equation
        plane_eq = rf"{tex(poly)}=0"
        sol_plane = (
            how + "\n\n"
            rf"The tangent plane is $${plane_eq}$$ (any non-zero multiple of this equation describes the same plane)."
        )
        items.append(ex(
            f"tan-{n:02d}a", rf"Tangent plane to {latex} at {pt_latex}.", "equation", key,
            coordinates=["x", "y", "z"], hints=[
                "Write the surface as $F(x,y,z)=0$ and compute $(F_x,F_y,F_z)$ at the point; they are the coefficients of the plane."],
            solution=sol_plane,
        ))
        dir_key = f"({', '.join(eng(v) for v in n_vec)})"
        line = (
            rf"$$\dfrac{{x-{tex(point[0])}}}{{{tex(n_vec[0])}}}=\dfrac{{y-{tex(point[1])}}}{{{tex(n_vec[1])}}}=\dfrac{{z-{tex(point[2])}}}{{{tex(n_vec[2])}}}.$$"
        )
        items.append(ex(
            f"tan-{n:02d}b", rf"Normal line to {latex} at {pt_latex}: give a direction vector $\vec n$ of the line.", "direction", dir_key,
            hints=["The normal line has the direction of $(F_x,F_y,F_z)$ at the point."],
            solution=(
                f"The normal line has the direction of the normal vector $(F_x,F_y,F_z)$ at the point, here "
                rf"$\vec n=\left({', '.join(tex(v) for v in n_vec)}\right)$ (or any non-zero multiple). The line through the point is" + "\n\n" + line
            ),
        ))

    surface(1, "z", r"the surface $z=3x^2+2y^2-11$", P("3*x^2+2*y^2-11-z"), (2, 1, 3), True, "$P(2,1,3)$")
    surface(2, "z", r"the surface $z=x^2+y^2$", P("x^2+y^2-z"), (1, -2, 5), True, "$P(1,-2,5)$")
    surface(3, "z", r"the surface $x^2+4y^2-4z^2-4=0$", P("x^2+4*y^2-4*z^2-4"), (2, 1, 1), False, "$P(2,1,1)$")
    surface(4, "z", r"the sphere $x^2+y^2+z^2=169$", P("x^2+y^2+z^2-169"), (3, 4, 12), False, "$P(3,4,12)$")

    # 5 and 6: general quadrics, point (x0, y0, z0) on the surface
    for n, sign, latex in ((5, 1, r"\dfrac{x^2}{a^2}+\dfrac{y^2}{b^2}+\dfrac{z^2}{c^2}=1"), (6, -1, r"\dfrac{x^2}{a^2}-\dfrac{y^2}{b^2}-\dfrac{z^2}{c^2}=1")):
        sy = sign
        key_plane = f"x*x0/a^2 {'+' if sy == 1 else '-'} y*y0/b^2 {'+' if sy == 1 else '-'} z*z0/c^2 - 1 = 0"
        kind = "ellipsoid" if n == 5 else "hyperboloid of two sheets"
        sgn = "+" if sy == 1 else "-"
        nv = f"(x0/a^2, {'' if sy == 1 else '-'}y0/b^2, {'' if sy == 1 else '-'}z0/c^2)"
        plane_tex = rf"\dfrac{{x_0\,x}}{{a^2}}{sgn}\dfrac{{y_0\,y}}{{b^2}}{sgn}\dfrac{{z_0\,z}}{{c^2}}=1"
        items.append(ex(
            f"tan-{n:02d}a", rf"Tangent plane to the {kind} ${latex}$ at a point $P(x_0,y_0,z_0)$ of the surface.", "equation", key_plane,
            coordinates=["x", "y", "z"], variables=["a", "b", "c", "x0", "y0", "z0"],
            hints=[
                "Take $F=\\dfrac{x^2}{a^2}\\pm\\dfrac{y^2}{b^2}\\pm\\dfrac{z^2}{c^2}-1$ and compute $F_x,F_y,F_z$ at $P$. At the end use the fact that $P$ lies on the surface to simplify the constant term."],
            solution=(
                rf"With $F=\dfrac{{x^2}}{{a^2}}{sgn}\dfrac{{y^2}}{{b^2}}{sgn}\dfrac{{z^2}}{{c^2}}-1$ we get "
                rf"$(F_x,F_y,F_z)=\left(\dfrac{{2x_0}}{{a^2}},\,{'' if sy == 1 else '-'}\dfrac{{2y_0}}{{b^2}},\,{'' if sy == 1 else '-'}\dfrac{{2z_0}}{{c^2}}\right)$ at $P$. "
                rf"The tangent plane is $F_x(x-x_0)+F_y(y-y_0)+F_z(z-z_0)=0$; dividing by $2$ gives" + "\n\n"
                rf"$$\dfrac{{x_0(x-x_0)}}{{a^2}}{sgn}\dfrac{{y_0(y-y_0)}}{{b^2}}{sgn}\dfrac{{z_0(z-z_0)}}{{c^2}}=0.$$" + "\n\n"
                rf"Because $P$ is on the surface, $\dfrac{{x_0^2}}{{a^2}}{sgn}\dfrac{{y_0^2}}{{b^2}}{sgn}\dfrac{{z_0^2}}{{c^2}}=1$, so the constant term equals $-1$ and the plane is" + "\n\n"
                rf"$${plane_tex}.$$"
            ),
        ))
        items.append(ex(
            f"tan-{n:02d}b", rf"Normal line to the same {kind} at $P(x_0,y_0,z_0)$: give a direction vector $\vec n$ of the line.", "direction", nv,
            variables=["a", "b", "c", "x0", "y0", "z0"],
            hints=["The direction is the coefficient vector of the tangent plane found in the previous exercise."],
            solution=(
                rf"The normal vector is the coefficient vector of the plane: $\vec n=\left(\dfrac{{x_0}}{{a^2}},\,{'' if sy == 1 else '-'}\dfrac{{y_0}}{{b^2}},\,{'' if sy == 1 else '-'}\dfrac{{z_0}}{{c^2}}\right)$. "
                "The normal line is the line through $P$ with this direction."
            ),
        ))
    return items


# --- A.IX extrema -------------------------------------------------------------------------------------------------
def pts_key(points: list[tuple]) -> str:
    return ", ".join("(" + ", ".join(eng(sp.nsimplify(c)) for c in p) + ")" for p in points)


def pts_tex(points: list[tuple]) -> str:
    return ",\\ ".join("(" + ",\\,".join(tex(sp.nsimplify(c)) for c in p) + ")" for p in points)


def local_extrema_items() -> list[dict]:
    items: list[dict] = []

    def analyse(f: sp.Expr):
        sols = sp.solve([sp.diff(f, x), sp.diff(f, y)], [x, y], dict=True)
        pts = [(s[x], s[y]) for s in sols if all(v.is_real for v in s.values())]
        info = []
        for px, py in pts:
            fxx, fyy, fxy = (sp.diff(f, *v).subs({x: px, y: py}) for v in ((x, x), (y, y), (x, y)))
            d = fxx * fyy - fxy**2
            kind = "min" if d > 0 and fxx > 0 else "max" if d > 0 and fxx < 0 else "saddle" if d < 0 else "unknown"
            info.append((px, py, fxx, fyy, fxy, d, kind, f.subs({x: px, y: py})))
        return pts, info

    # 1
    f1 = P("x^2+y^2-4*x+6*y+25")
    pts, info = analyse(f1)
    assert len(pts) == 1 and info[0][6] == "min"
    items.append(ex(
        "ext-01a", r"Find the critical points of $z=x^2+y^2-4x+6y+25$.", "points", pts_key(pts),
        hints=["Solve $z_x=0$ and $z_y=0$ together."],
        solution=rf"$z_x=2x-4=0$ gives $x=2$ and $z_y=2y+6=0$ gives $y=-3$. The only critical point is $({pts_tex(pts)[1:-1]})$.",
    ))
    d = info[0]
    items.append(ex(
        "ext-01b", r"Find the local minimum value of $z=x^2+y^2-4x+6y+25$.", "number", eng(d[7]),
        hints=["Classify $(2,-3)$ with $D=z_{xx}z_{yy}-z_{xy}^2$, then compute $z(2,-3)$."],
        solution=rf"$z_{{xx}}=2$, $z_{{yy}}=2$, $z_{{xy}}=0$, so $D=4>0$ and $z_{{xx}}>0$: a local minimum. Its value is $z(2,-3)=4+9-8-18+25={tex(d[7])}$. "
                 r"(Check: $z=(x-2)^2+(y+3)^2+12$, which is at least $12$.)",
    ))

    # 2
    f2 = P("x^3+y^3+3*x*y")
    pts, info = analyse(f2)
    assert {i[6] for i in info} == {"saddle", "max"}
    items.append(ex(
        "ext-02a", r"Find the critical points of $z=x^3+y^3+3xy$.", "points", pts_key([(p[0], p[1]) for p in info]),
        hints=["From $z_x=3x^2+3y=0$ get $y=-x^2$, then substitute in $z_y=3y^2+3x=0$."],
        solution=r"$z_x=3x^2+3y=0$ gives $y=-x^2$. Then $z_y=3y^2+3x=3x^4+3x=3x(x^3+1)=0$, so $x=0$ or $x=-1$. "
                 rf"The critical points are ${pts_tex([(p[0], p[1]) for p in info])}$.",
    ))
    mx = next(i for i in info if i[6] == "max")
    items.append(ex(
        "ext-02b", r"Find the local maximum value of $z=x^3+y^3+3xy$.", "number", eng(mx[7]),
        hints=["Compute $D=z_{xx}z_{yy}-z_{xy}^2$ at each critical point: $z_{xx}=6x$, $z_{yy}=6y$, $z_{xy}=3$."],
        solution=r"At $(-1,-1)$: $z_{xx}=-6$, $z_{yy}=-6$, $z_{xy}=3$, so $D=36-9=27>0$ and $z_{xx}<0$: a local maximum, with value $z(-1,-1)=-1-1+3="
                 rf"{tex(mx[7])}$. At $(0,0)$: $D=0-9<0$, a saddle point.",
    ))
    items.append(ex(
        "ext-02c", r"What kind of point is the critical point $(0,0)$ of $z=x^3+y^3+3xy$?", "multiple_choice", "3",
        choices=[{"text": "A local minimum", "value": "1"}, {"text": "A local maximum", "value": "2"},
                 {"text": "A saddle point", "value": "3"}, {"text": "The test does not decide", "value": "4"}],
        correctIndex=2, hints=["At $(0,0)$: $z_{xx}=0$, $z_{yy}=0$, $z_{xy}=3$."],
        solution=r"At $(0,0)$: $z_{xx}=0$, $z_{yy}=0$, $z_{xy}=3$, so $D=0\cdot0-9=-9<0$. A negative $D$ means a saddle point.",
    ))

    # 3 (corrected function)
    f3 = P("x^3+3*x*y^2-15*x-12*y")
    pts, info = analyse(f3)
    assert {(p[0], p[1]) for p in info} == {(1, 2), (2, 1), (-1, -2), (-2, -1)}
    note = (
        "The printed sheet has $x^2$ as the first term. With $x^2$ the critical points are the solutions of $3y^3-15y+4=0$, which are not "
        "exact numbers, so the problem is almost certainly $z=x^3+3xy^2-15x-12y$, the classical exercise. This corrected function is used here."
    )
    items.append(ex(
        "ext-03a", r"Find the critical points of $z=x^3+3xy^2-15x-12y$.", "points", pts_key([(p[0], p[1]) for p in info]),
        hints=["$z_x=3x^2+3y^2-15=0$ and $z_y=6xy-12=0$. The second equation gives $xy=2$."],
        solution=(
            r"$z_x=3x^2+3y^2-15=0$ gives $x^2+y^2=5$, and $z_y=6xy-12=0$ gives $xy=2$. Then $(x+y)^2=5+4=9$ and $(x-y)^2=5-4=1$, "
            r"so $x+y=\pm3$ and $x-y=\pm1$. The four solutions are " + rf"${pts_tex([(p[0], p[1]) for p in info])}$."
        ),
        note=note,
    ))
    mn = next(i for i in info if i[6] == "min")
    mx = next(i for i in info if i[6] == "max")
    items.append(ex(
        "ext-03b", r"Find the local minimum value of $z=x^3+3xy^2-15x-12y$.", "number", eng(mn[7]),
        hints=["Here $z_{xx}=6x$, $z_{yy}=6x$, $z_{xy}=6y$, so $D=36x^2-36y^2$."],
        solution=rf"$D=36(x^2-y^2)$. At $({tex(mn[0])},{tex(mn[1])})$ we get $D={tex(mn[5])}>0$ and $z_{{xx}}={tex(mn[2])}>0$: a local minimum, with value ${tex(mn[7])}$.",
    ))
    items.append(ex(
        "ext-03c", r"Find the local maximum value of $z=x^3+3xy^2-15x-12y$.", "number", eng(mx[7]),
        hints=["Look for the critical point with $D>0$ and $z_{xx}<0$."],
        solution=rf"At $({tex(mx[0])},{tex(mx[1])})$: $D={tex(mx[5])}>0$ and $z_{{xx}}={tex(mx[2])}<0$: a local maximum, with value ${tex(mx[7])}$.",
    ))
    items.append(ex(
        "ext-03d", r"What kind of point is the critical point $(1,2)$ of $z=x^3+3xy^2-15x-12y$?", "multiple_choice", "3",
        choices=[{"text": "A local minimum", "value": "1"}, {"text": "A local maximum", "value": "2"},
                 {"text": "A saddle point", "value": "3"}, {"text": "The test does not decide", "value": "4"}],
        correctIndex=2, hints=["Compute $D=36(x^2-y^2)$ at $(1,2)$."],
        solution=r"At $(1,2)$: $D=36(1-4)=-108<0$, so $(1,2)$ is a saddle point. The same happens at $(-1,-2)$.",
    ))
    return items


def constrained_items() -> list[dict]:
    items: list[dict] = []
    lam = sp.Symbol("lam", real=True)

    def lagrange(f: sp.Expr, g: sp.Expr):
        sols = sp.solve([sp.diff(f, x) - lam * sp.diff(g, x), sp.diff(f, y) - lam * sp.diff(g, y), g], [x, y, lam], dict=True)
        pts = [(simp(s[x]), simp(s[y])) for s in sols]
        return pts, [simp(f.subs({x: px, y: py})) for px, py in pts]

    # 4
    f, g = P("6-4*x-3*y"), P("x^2+y^2-1")
    pts, vals = lagrange(f, g)
    mx_i, mn_i = vals.index(max(vals)), vals.index(min(vals))
    assert vals[mx_i] == 11 and vals[mn_i] == 1
    th = [i / 200 * 2 * math.pi for i in range(200)]
    assert abs(max(6 - 4 * math.cos(q) - 3 * math.sin(q) for q in th) - 11) < 1e-3
    items.append(ex(
        "con-04a", r"Find the points where $z=6-4x-3y$ has its extreme values on the circle $x^2+y^2=1$.", "points", pts_key(pts),
        hints=["The system is $-4=2\\lambda x$, $-3=2\\lambda y$, $x^2+y^2=1$."],
        solution=(
            r"Take $g=x^2+y^2-1$. The system $-4=2\lambda x$, $-3=2\lambda y$ gives $x=-\dfrac{2}{\lambda}$ and $y=-\dfrac{3}{2\lambda}$, so $y=\dfrac34x$. "
            r"With $x^2+y^2=1$: $x^2\left(1+\dfrac9{16}\right)=1$, $x=\pm\dfrac45$. The points are " + rf"${pts_tex(pts)}$."
        ),
    ))
    items.append(ex("con-04b", r"Find the maximum value of $z=6-4x-3y$ on the circle $x^2+y^2=1$.", "number", eng(vals[mx_i]),
                    hints=["Compare the values of $z$ at the two points found above."],
                    solution=rf"$z\left({pts_tex([pts[mn_i]])[1:-1]}\right)={tex(vals[mn_i])}$ and $z\left({pts_tex([pts[mx_i]])[1:-1]}\right)={tex(vals[mx_i])}$. The larger value is the maximum: ${tex(vals[mx_i])}$."))
    items.append(ex("con-04c", r"Find the minimum value of $z=6-4x-3y$ on the circle $x^2+y^2=1$.", "number", eng(vals[mn_i]),
                    hints=["The smaller of the two values is the minimum."],
                    solution=rf"The smaller of the two values is the minimum: ${tex(vals[mn_i])}$."))

    # 5
    items.append(ex(
        "con-05a", r"Find the point where $z=xy$ has its extreme value on the line $x+y=1$.", "points", "(1/2, 1/2)",
        hints=["Substitute $y=1-x$ and maximize $x(1-x)$."],
        solution=r"With $y=1-x$: $z=x-x^2$, and $\dfrac{dz}{dx}=1-2x=0$ gives $x=\dfrac12$, $y=\dfrac12$. The point is $\left(\dfrac12,\dfrac12\right)$.",
    ))
    items.append(ex("con-05b", r"Find the maximum value of $z=xy$ on the line $x+y=1$.", "number", "1/4",
                    hints=["$z=x-x^2$ is a downward parabola."],
                    solution=r"$z=x-x^2$ has its maximum at $x=\dfrac12$, where $z=\dfrac12\cdot\dfrac12=\dfrac14$."))
    items.append(ex(
        "con-05c", r"Does $z=xy$ have a minimum value on the line $x+y=1$?", "multiple_choice", "2",
        choices=[{"text": "Yes, it has a minimum", "value": "1"}, {"text": "No, there is no minimum", "value": "2"}],
        correctIndex=1, hints=["The line is unbounded. What happens to $x-x^2$ when $x$ is very large?"],
        solution=r"On the line, $z=x-x^2$, which tends to $-\infty$ as $x\to\pm\infty$. The line is not bounded, so there is a maximum ($\dfrac14$) but no minimum.",
    ))

    # 6
    f, g = P("x+y"), P("x^2+y^2-5")
    pts, vals = lagrange(f, g)
    mx_i, mn_i = vals.index(max(vals)), vals.index(min(vals))
    assert simp(vals[mx_i] - sp.sqrt(10)) == 0
    items.append(ex(
        "con-06a", r"Find the points where $z=x+y$ has its extreme values on the circle $x^2+y^2=5$.", "points", pts_key(pts),
        hints=["The system $1=2\\lambda x$, $1=2\\lambda y$ shows that $x=y$."],
        solution=r"$1=2\lambda x$ and $1=2\lambda y$ give $x=y$. With $x^2+y^2=5$: $2x^2=5$, so $x=y=\pm\sqrt{\dfrac52}=\pm\dfrac{\sqrt{10}}2$. "
                 rf"The points are ${pts_tex(pts)}$.",
    ))
    items.append(ex("con-06b", r"Find the maximum value of $z=x+y$ on the circle $x^2+y^2=5$.", "number", eng(vals[mx_i]),
                    hints=["Add the two coordinates of each candidate point."],
                    solution=rf"At the point with positive coordinates $z=2\cdot\dfrac{{\sqrt{{10}}}}2=\sqrt{{10}}$. This is the maximum."))
    items.append(ex("con-06c", r"Find the minimum value of $z=x+y$ on the circle $x^2+y^2=5$.", "number", eng(vals[mn_i]),
                    hints=["Use the other candidate point."],
                    solution=rf"At the point with negative coordinates $z=-\sqrt{{10}}$. This is the minimum."))
    return items


def build() -> None:
    write_exercises(
        f"{BASE}/u03-tangent-planes/l01-tangent-plane-and-normal-line",
        [exset(
            "tangent", "Find the tangent plane and the normal line to each surface at the given point.", tangent_items(),
            format="Write the plane as an equation, for example `2*x + 4*y - z = 10`; any non-zero multiple of the equation is accepted. "
            "For the normal line, give a direction vector like `(2, 4, -1)`; any non-zero multiple is accepted.",
        )],
        "mvc_m01_u03_u04.py",
    )
    write_exercises(
        f"{BASE}/u04-optimization/l01-local-extrema",
        [exset("extrema", "Examine the following function for local extrema.", local_extrema_items(),
               format="For a list of points type `(a, b), (c, d)`. For a value type a number or an exact expression.")],
        "mvc_m01_u03_u04.py",
    )
    write_exercises(
        f"{BASE}/u04-optimization/l02-constrained-extrema",
        [exset("constrained", "Find the extreme values of each function under the given constraint (S/C).", constrained_items(),
               format="For a list of points type `(a, b), (c, d)`. For a value type a number or an exact expression such as `sqrt(10)`.")],
        "mvc_m01_u03_u04.py",
    )
