"""Course 1 (geo): exercises of the additions to the geometry course.

New lessons: cylindrical and spherical coordinates, the altitudes of a tetrahedron, the sphere (four points, parametric equations, area, volume),
tangent planes and normals of a sphere. Extra practice for the dot product in 2D and 3D, the parametric circle, the ellipse, the hyperbola and the
centers of a triangle. Every key is computed with SymPy; the geometry helpers are those of the other geometry builders."""

from __future__ import annotations

import sympy as sp
from geo_m02 import rad
from geo_m03 import (
    TA,
    TB,
    TC,
    TD,
    Tet,
    cross,
    dist3,
    dist_point_plane,
    dot,
    foot,
    item_num,
    item_plane,
    item_pt,
    norm,
    plane_through,
    pt3_eng,
    pt3_tex,
    sub,
)
from toolkit import add_extra, eng, ex, exset_plain, tex, with_units

SCRIPT = "geo_additions.py"
BASE = "geo"
FMT = "Type a point as `(x, y, z)`, an exact value such as `sqrt(7)/4`, or an equation with `=`."
R = sp.Rational
PI = sp.pi
x, y, z = sp.symbols("x y z", real=True)


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


def pt2_tex(p) -> str:
    return rf"\left({tex(p[0])},\,{tex(p[1])}\right)"


def pt2_eng(p) -> str:
    return f"({eng(p[0])}, {eng(p[1])})"


def item_pt2(id_: str, stmt: str, p, solution: str, hints: list[str]) -> dict:
    return ex(id_, stmt, "point", pt2_eng(p), solution=solution, hints=hints)


def angle01(v: sp.Expr) -> sp.Expr:
    """An angle of [0, 2pi) given as atan2 would return it."""
    v = sp.simplify(v)
    return sp.simplify(v + 2 * PI) if v.is_negative else v


# --- cylindrical and spherical coordinates --------------------------------------------------------------------------------------------------------
def cyl_sph_items() -> list[dict]:
    it: list[dict] = []
    # plane: polar and Cartesian
    p = (-1, 1)
    r_, t_ = rad(sp.sqrt(2)), angle01(sp.atan2(1, -1))
    assert t_ == 3 * PI / 4
    it.append(item_num("cs-p1", r"In polar coordinates, the point $(-1,1)$ has the distance $r$ equal to", r_, r"$r=\sqrt{(-1)^2+1^2}=\sqrt2$.", ["$r=\\sqrt{x^2+y^2}$."]))
    it.append(item_num("cs-p2", r"In polar coordinates, the point $(-1,1)$ has the angle $\theta\in[0,2\pi)$ equal to", t_, r"The point is in the second quadrant and $\tan\theta=-1$, so $\theta=\dfrac{3\pi}4$.", ["Find the quadrant first."]))
    q = (rad(4 * sp.cos(PI / 6)), rad(4 * sp.sin(PI / 6)))
    it.append(item_pt2("cs-p3", r"The Cartesian coordinates of the point with polar coordinates $\left(4,\dfrac\pi6\right)$.", q, r"$x=4\cos\dfrac\pi6=2\sqrt3$ and $y=4\sin\dfrac\pi6=2$.", ["$x=r\\cos\\theta$, $y=r\\sin\\theta$."]))
    # cylindrical from Cartesian
    pts = [(1, 1, 2), (0, 3, -1), (-2, 0, 5), (1, -sp.sqrt(3), 4)]
    for n, P in enumerate(pts, 1):
        r_ = rad(sp.sqrt(P[0] ** 2 + P[1] ** 2))
        t_ = angle01(sp.atan2(P[1], P[0]))
        it.append(item_num(f"cs-c{n}r", rf"The cylindrical coordinate $r$ of the point $P{pt3_tex(P)}$.", r_, rf"$r=\sqrt{{x^2+y^2}}={tex(r_)}$ (the distance from $P$ to the $z$-axis).", ["Use only $x$ and $y$."]))
        it.append(item_num(f"cs-c{n}t", rf"The cylindrical coordinate $\theta\in[0,2\pi)$ of the point $P{pt3_tex(P)}$.", t_, rf"The projection $({tex(P[0])},{tex(P[1])})$ is in the quadrant that gives $\theta={tex(t_)}$.", ["Look at the projection on the plane $xy$ and its quadrant."]))
    # Cartesian from cylindrical
    for n, (r_, t_, z_) in enumerate(((2, PI / 3, 5), (4, PI, 1), (3, PI / 2, -2)), 1):
        P = (rad(r_ * sp.cos(t_)), rad(r_ * sp.sin(t_)), z_)
        it.append(item_pt(f"cs-d{n}", rf"The Cartesian coordinates of the point with cylindrical coordinates $\left({tex(r_)},{tex(t_)},{z_}\right)$.", P,
                          rf"$x=r\cos\theta={tex(P[0])}$, $y=r\sin\theta={tex(P[1])}$, $z={z_}$.", ["$x=r\\cos\\theta$, $y=r\\sin\\theta$, $z$ is unchanged."]))
    # spherical from Cartesian
    for n, P in enumerate(((1, 2, 2), (1, 1, sp.sqrt(2)), (sp.sqrt(3), 1, 2)), 1):
        rho = rad(sp.sqrt(sum(c**2 for c in P)))
        phi = sp.simplify(sp.acos(rad(P[2] / rho)))
        th = angle01(sp.atan2(P[1], P[0]))
        it.append(item_num(f"cs-s{n}r", rf"The spherical coordinate $\rho$ of the point $P{pt3_tex(P)}$.", rho, rf"$\rho=\sqrt{{x^2+y^2+z^2}}={tex(rho)}$.", ["The distance from $P$ to the origin."]))
        it.append(item_num(f"cs-s{n}p", rf"The spherical coordinate $\varphi\in[0,\pi]$ of the point $P{pt3_tex(P)}$ (exact value).", phi,
                           rf"$\cos\varphi=\dfrac z\rho={tex(rad(P[2] / rho))}$ (with $z={tex(P[2])}$ and $\rho={tex(rho)}$), so $\varphi={tex(phi)}$.", ["$\\cos\\varphi=\\dfrac z\\rho$."]))
        if n > 1:
            it.append(item_num(f"cs-s{n}t", rf"The spherical coordinate $\theta$ of the point $P{pt3_tex(P)}$.", th, rf"$\theta$ is the polar angle of the projection $({tex(P[0])},{tex(P[1])})$: $\theta={tex(th)}$.", ["Use the projection on the plane $xy$."]))
    # Cartesian from spherical
    for n, (rho, ph, th) in enumerate(((4, PI / 3, PI / 6), (2, PI / 2, PI / 2), (6, PI / 6, PI / 4)), 1):
        P = (rad(rho * sp.sin(ph) * sp.cos(th)), rad(rho * sp.sin(ph) * sp.sin(th)), rad(rho * sp.cos(ph)))
        it.append(item_pt(f"cs-t{n}", rf"The Cartesian coordinates of the point with spherical coordinates $\left(\rho,\varphi,\theta\right)=\left({tex(rho)},{tex(ph)},{tex(th)}\right)$.", P,
                          rf"$x=\rho\sin\varphi\cos\theta={tex(P[0])}$, $y=\rho\sin\varphi\sin\theta={tex(P[1])}$, $z=\rho\cos\varphi={tex(P[2])}$.", ["$x=\\rho\\sin\\varphi\\cos\\theta$, $y=\\rho\\sin\\varphi\\sin\\theta$, $z=\\rho\\cos\\varphi$."]))
    # between the systems
    r_ = rad(4 * sp.sin(PI / 6))
    it.append(item_num("cs-b1", r"A point has spherical coordinates $\rho=4$, $\varphi=\dfrac\pi6$. Its cylindrical coordinate $r$ is", r_, r"$r=\rho\sin\varphi=4\cdot\dfrac12=2$.", ["$r=\\rho\\sin\\varphi$."]))
    it.append(item_num("cs-b2", r"A point has spherical coordinates $\rho=4$, $\varphi=\dfrac\pi6$. Its coordinate $z$ is", rad(4 * sp.cos(PI / 6)), r"$z=\rho\cos\varphi=4\cdot\dfrac{\sqrt3}2=2\sqrt3$.", ["$z=\\rho\\cos\\varphi$."]))
    it.append(item_num("cs-b3", r"A point has cylindrical coordinates $r=3$, $z=3$. Its spherical coordinate $\varphi$ is", PI / 4, r"$\tan\varphi=\dfrac rz=1$, so $\varphi=\dfrac\pi4$ (and $\rho=3\sqrt2$).", ["$\\tan\\varphi=\\dfrac rz$."]))
    # surfaces
    it.append(item_num("cs-e1", r"The sphere $x^2+y^2+z^2=16$ in spherical coordinates is $\rho=\,$?", sp.Integer(4), r"$x^2+y^2+z^2=\rho^2$, so $\rho^2=16$ and $\rho=4$.", ["The sum of the three squares is $\\rho^2$."]))
    it.append(item_num("cs-e2", r"The cone $z^2=3\left(x^2+y^2\right)$ with $z\ge0$ in spherical coordinates is $\varphi=\,$?", PI / 6, r"$\tan^2\varphi=\dfrac{x^2+y^2}{z^2}=\dfrac13$, so $\tan\varphi=\dfrac1{\sqrt3}$ and $\varphi=\dfrac\pi6$.", ["$\\tan\\varphi=\\dfrac rz$ with $r^2=x^2+y^2$."]))
    it.append(item_num("cs-e3", r"The cylinder $x^2+y^2=9$ in cylindrical coordinates is $r=\,$?", sp.Integer(3), r"$x^2+y^2=r^2=9$, so $r=3$.", ["$x^2+y^2=r^2$."]))
    it.append(mc("cs-m1", r"Which surface is $\varphi=\dfrac\pi3$ in spherical coordinates?", ["A sphere", "A cone around the $z$-axis", "A plane", "A cylinder"], 1,
                 r"All the points have the same angle with the $z$-axis.", r"The points that make a constant angle with the $z$-axis form a cone (a half cone, because $\varphi<\dfrac\pi2$)."))
    it.append(mc("cs-m2", r"Which surface is $\rho=5$ in spherical coordinates?", ["A cone", "A plane", "A sphere centered at the origin", "A cylinder"], 2,
                 r"$\rho$ is the distance to the origin.", r"All the points at distance $5$ from the origin form the sphere $x^2+y^2+z^2=25$."))
    return it


# --- the altitudes of a tetrahedron ---------------------------------------------------------------------------------------------------------------
def altitude_items() -> list[dict]:
    it: list[dict] = []
    tets = {"T1": Tet((0, 0, 0), (3, 0, 0), (0, 4, 0), (0, 0, 12)), "T2": TB, "T3": Tet((0, 0, 0), (6, 0, 0), (0, 6, 0), (0, 0, 6)), "T4": TA}

    def head(T: Tet) -> str:
        return ", ".join(rf"${n}{pt3_tex(T.V[n])}$" for n in Tet.NAMES)

    n = 0
    for name, T in tets.items():
        n += 1
        lab = f"The tetrahedron has the vertices {head(T)}. "
        it.append(item_num(f"al-{name}v", lab + r"Its volume (the unit is cu: give the number only) is", T.vol, rf"$V=\dfrac16\left|\boxp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}{{\overrightarrow{{AD}}}}\right|={tex(T.vol)}$.", ["The box product of three edges at $A$."]))
        for v in ("A", "D") if name != "T4" else ("A", "B"):
            f = T.opp[v]
            P = T.face_plane(f)
            h = T.height(v)
            t0, H = foot(T.V[v], P)
            it.append(item_num(f"al-{name}s{v}", lab + rf"The area of the face ${f}$ (unit squ: give the number only) is", T.face[f], rf"$S_{{{f}}}=\dfrac12\norm{{\crossp{{\overrightarrow{{{f[0]}{f[1]}}}}}{{\overrightarrow{{{f[0]}{f[2]}}}}}}}={tex(T.face[f])}$.", ["Half the length of a cross product of two edges of the face."]))
            it.append(item_num(f"al-{name}h{v}", lab + rf"The length of the altitude from ${v}$ (unit lu: give the number only) is", h, rf"$h_{v}=\dfrac{{3V}}{{S_{{{f}}}}}$ with $V={tex(T.vol)}$ and $S_{{{f}}}={tex(T.face[f])}$, so $h_{v}={tex(h)}$.", [r"$h=\dfrac{3V}{S}$ with the area of the opposite face."]))
            it.append(item_pt(f"al-{name}f{v}", lab + rf"The foot of the altitude from ${v}$ is", H,
                              rf"The face ${f}$ lies in the plane ${tex(sp.expand(P[0] * x + P[1] * y + P[2] * z + P[3]))}=0$. The altitude line is ${v}+t\,{pt3_tex(P[:3])}$, and it meets the plane for $t=-{tex(t0)}$: the foot is ${pt3_tex(H)}$.",
                              ["The altitude direction is the normal vector of the face; put the line in the plane of the face."]))
            assert abs(float(sp.N(dist3(T.V[v], H) - h))) < 1e-9
    it.append(item_pt("al-dir", r"The face $BCD$ of a tetrahedron lies in the plane $2x-y+2z=6$. A direction vector of the altitude from $A(1,1,1)$ is (with positive first coordinate)", (2, -1, 2),
                      r"The altitude is perpendicular to the plane, so it is parallel to the normal vector $(2,-1,2)$.", ["The normal vector of the plane."]))
    it.append(item_num("al-chk", r"A tetrahedron has volume $24$ cu and a face of area $18$ squ. The altitude to that face (unit lu: number only) is", sp.Integer(4), r"$h=\dfrac{3V}S=\dfrac{72}{18}=4$.", ["$V=\\dfrac13Sh$."]))
    it.append(mc("al-m1", r"In a tetrahedron the face $BCD$ has a larger area than the face $ABC$. Which altitude is longer?", ["The one from $A$ (to $BCD$)", "The one from $D$ (to $ABC$)", "They are equal", "It depends on the edges only"], 1,
                 r"$3V=h_AS_{BCD}=h_DS_{ABC}$.", r"Because $h_AS_{BCD}=h_DS_{ABC}=3V$, the larger face goes with the smaller altitude: $h_A<h_D$, so the altitude from $D$ is longer."))
    return it


# --- the sphere: four points, parametric equations, area and volume ----------------------------------------------------------------------------------------
def sphere_items() -> list[dict]:
    it: list[dict] = []
    m, nn, p, q = sp.symbols("m n p q")
    sets = {
        "S1": ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)),
        "S2": ((0, 0, 0), (4, 0, 0), (0, 4, 0), (0, 0, 4)),
        "S3": ((0, 0, 0), (4, 0, 0), (1, 3, 0), (2, 1, 5)),
        "S4": ((2, 0, 0), (0, 2, 0), (0, 0, 2), (-2, 0, 0)),
    }
    for name, pts in sets.items():
        eqs = [P[0] ** 2 + P[1] ** 2 + P[2] ** 2 + 2 * m * P[0] + 2 * nn * P[1] + 2 * p * P[2] + q for P in pts]
        sol = sp.solve(eqs, (m, nn, p, q), dict=True)[0]
        c = (rad(-sol[m]), rad(-sol[nn]), rad(-sol[p]))
        rho2 = rad(sol[m] ** 2 + sol[nn] ** 2 + sol[p] ** 2 - sol[q])
        rho = rad(sp.sqrt(rho2))
        assert all(rad(sum((P[i] - c[i]) ** 2 for i in range(3)) - rho2) == 0 for P in pts)
        head = "The sphere passes through " + ", ".join(rf"${'ABCD'[i]}{pt3_tex(P)}$" for i, P in enumerate(pts)) + ". "
        sol_txt = rf"Put the four points in $x^2+y^2+z^2+2mx+2ny+2pz+q=0$ and solve the four linear equations: $m={tex(sol[m])}$, $n={tex(sol[nn])}$, $p={tex(sol[p])}$, $q={tex(sol[q])}$. The center is $(-m,-n,-p)={pt3_tex(c)}$ and $\rho^2=m^2+n^2+p^2-q={tex(rho2)}$."
        it.append(item_num(f"sf-{name}q", head + r"In the general equation $x^2+y^2+z^2+2mx+2ny+2pz+q=0$ the value of $q$ is", sol[q], sol_txt, ["Four linear equations in $m$, $n$, $p$, $q$."]))
        it.append(item_pt(f"sf-{name}c", head + r"Its center is", c, sol_txt, ["The center is $(-m,-n,-p)$."]))
        it.append(item_num(f"sf-{name}r", head + r"Its radius is", rho, sol_txt, [r"$\rho^2=m^2+n^2+p^2-q$."]))
        it.append(item_num(f"sf-{name}a", head + r"Its surface area (unit squ: give the number only) is", rad(4 * PI * rho2), sol_txt + rf" The area is $4\pi\rho^2={tex(rad(4 * PI * rho2))}$.", [r"$4\pi\rho^2$."]))
        it.append(item_num(f"sf-{name}v", head + r"Its volume (unit cu: give the number only) is", rad(sp.Rational(4, 3) * PI * rho**3), sol_txt + rf" The volume is $\dfrac43\pi\rho^3={tex(rad(sp.Rational(4, 3) * PI * rho**3))}$.", [r"$\dfrac43\pi\rho^3$."]))
    # parametric equations
    for k, (c, rho, ph, th) in enumerate((((1, -2, 3), 5, PI / 2, 0), ((0, 0, 0), 3, PI / 3, PI / 2), ((2, 1, -1), 4, PI / 6, PI / 3)), 1):
        P = (rad(c[0] + rho * sp.sin(ph) * sp.cos(th)), rad(c[1] + rho * sp.sin(ph) * sp.sin(th)), rad(c[2] + rho * sp.cos(ph)))
        it.append(item_pt(f"sf-pp{k}", rf"The sphere has center ${pt3_tex(c)}$ and radius ${rho}$. Its point for $\varphi={tex(ph)}$, $\theta={tex(th)}$ in the parametric equations $x=p+\rho\sin\varphi\cos\theta$, $y=q+\rho\sin\varphi\sin\theta$, $z=r_0+\rho\cos\varphi$ is", P,
                          rf"$x={tex(P[0])}$, $y={tex(P[1])}$, $z={tex(P[2])}$.", ["Replace the center, $\\rho$ and the two angles."]))
    it.append(item_num("sf-av1", r"The volume of the sphere $x^2+y^2+z^2-2x+4y-6z-11=0$ (unit cu: number only) is", rad(sp.Rational(4, 3) * PI * 125), r"Completing the squares: $\rho^2=1+4+9+11=25$, $\rho=5$. $V=\dfrac43\pi\cdot125=\dfrac{500\pi}3$.", ["Find $\\rho$ first."]))
    it.append(item_num("sf-av2", r"The surface area of the sphere $x^2+y^2+z^2-6z=0$ (unit squ: number only) is", rad(4 * PI * 9), r"$x^2+y^2+(z-3)^2=9$: $\rho=3$ and the area is $4\pi\cdot9=36\pi$.", ["Complete the square in $z$."]))
    it.append(mc("sf-m1", r"In the parametric equations of a sphere, the curve obtained for a constant $\varphi=\dfrac\pi2$ is", ["A meridian", "The equator", "A pole", "A tangent line"], 1,
                 r"$z=r_0+\rho\cos\varphi$ is then constant.", r"For $\varphi=\dfrac\pi2$ we have $z=r_0$ and the point goes around the horizontal great circle: the equator."))
    return it


# --- tangent planes and normals of a sphere ---------------------------------------------------------------------------------------------------------
def tps_items() -> list[dict]:
    it: list[dict] = []
    cases = [((0, 0, 0), 9, (1, 2, 2)), ((0, 0, 0), 14, (1, 2, 3)), ((1, -2, 3), 49, (3, 1, 9)), ((2, 0, -1), 36, (2, 6, -1)), ((-1, 1, 2), 25, (2, 5, 2))]
    for k, (c, r2, P0) in enumerate(cases, 1):
        n = tuple(rad(P0[i] - c[i]) for i in range(3))
        assert sum(v * v for v in n) == r2
        pl = (n[0], n[1], n[2], -sum(n[i] * P0[i] for i in range(3)))
        from geo_m03 import plane_norm

        pl = plane_norm(*pl)
        head = rf"The sphere has center ${pt3_tex(c)}$ and $\rho^2={r2}$; $P_0{pt3_tex(P0)}$ is on it. "
        it.append(item_plane(f"tp-{k}t", head + r"The tangent plane at $P_0$ is", pl, rf"The radius vector is $\overrightarrow{{CP_0}}={pt3_tex(n)}$: it is the normal vector. The plane ${pt3_tex(n)}\cdot(X-P_0)=0$ is ${tex(sp.expand(pl[0] * x + pl[1] * y + pl[2] * z + pl[3]))}=0$.", ["The normal vector of the tangent plane is $\\overrightarrow{CP_0}$."]))
        it.append(item_pt(f"tp-{k}n", head + r"A direction vector of the normal line at $P_0$ (the line $CP_0$) is", n, rf"$\overrightarrow{{CP_0}}=P_0-C={pt3_tex(n)}$.", ["The normal line passes through the center."]))
    # parallel tangent planes
    for k, (nvec, rho) in enumerate((((2, -1, 2), 3), ((1, 2, 2), 2), ((3, 4, 0), 5)), 1):
        d = rad(rho * sp.sqrt(sum(v * v for v in nvec)))
        it.append(item_num(f"tp-p{k}", rf"The sphere $x^2+y^2+z^2={rho ** 2}$ has two tangent planes parallel to ${tex(sp.expand(nvec[0] * x + nvec[1] * y + nvec[2] * z))}=0$: they are ${tex(sp.expand(nvec[0] * x + nvec[1] * y + nvec[2] * z))}=\pm d$. The value $d>0$ is", d,
                           rf"The distance from the origin to the plane is $\dfrac{{|d|}}{{{tex(norm(nvec))}}}=\rho={rho}$, so $|d|={tex(d)}$.", [r"The distance from the center to the plane is $\rho$."]))
    # power and tangent length
    for k, (c, r2, P) in enumerate((((0, 0, 0), 9, (3, 0, 4)), ((1, 1, 1), 4, (1, 1, 6)), ((0, 0, 0), 25, (6, 8, 0))), 1):
        pw = rad(sum((P[i] - c[i]) ** 2 for i in range(3)) - r2)
        it.append(item_num(f"tp-w{k}", rf"The power of $P{pt3_tex(P)}$ with respect to the sphere with center ${pt3_tex(c)}$ and $\rho^2={r2}$ ($CP^2-\rho^2$) is", pw, rf"$CP^2={tex(rad(pw + r2))}$ and $\rho^2={r2}$, so the power is ${tex(pw)}$.", ["$CP^2-\\rho^2$."]))
        it.append(item_num(f"tp-l{k}", rf"The length of a tangent segment from $P{pt3_tex(P)}$ to the sphere with center ${pt3_tex(c)}$ and $\rho^2={r2}$ (unit lu: number only) is", rad(sp.sqrt(pw)), rf"The tangent length is $\sqrt{{\text{{power}}}}=\sqrt{{{tex(pw)}}}={tex(rad(sp.sqrt(pw)))}$ (right angle at the point of tangency).", ["Pythagoras in the triangle $CTP$."]))
    it.append(mc("tp-m1", r"The point $P(1,2,2)$ and the sphere $x^2+y^2+z^2=16$: the point is", ["Outside the sphere", "On the sphere", "Inside the sphere", "On the tangent plane at the origin"], 2,
                 r"Compare $CP^2$ with $\rho^2$.", r"$CP^2=1+4+4=9<16=\rho^2$: the power is negative, so $P$ is inside."))
    it.append(mc("tp-m2", r"The normal line to a sphere at a point $P_0$ of the sphere always passes through", ["The origin", "The center of the sphere", "The point $(1,1,1)$", "No fixed point"], 1,
                 r"It is the line of the radius.", r"The normal is perpendicular to the tangent plane at $P_0$, which is perpendicular to the radius, so the normal is the line $CP_0$ and passes through the center."))
    return it


# --- extra practice for existing lessons -----------------------------------------------------------------------------------------------------------------
def dot_items() -> list[dict]:
    it: list[dict] = []
    for n, (u, v) in enumerate((((3, 4), (-4, 3)), ((1, 2), (3, -5)), ((2, -1), (4, 8)), ((1, 1), (1, 0))), 1):
        d = u[0] * v[0] + u[1] * v[1]
        it.append(item_num(f"ad-dp{n}", rf"In the plane, $\dotp{{\vec u}}{{\vec v}}$ for $\vec u={pt2_tex(u)}$ and $\vec v={pt2_tex(v)}$ is", sp.Integer(d), rf"${u[0]}\cdot{v[0] if v[0] >= 0 else '(' + str(v[0]) + ')'}+{u[1] if u[1] >= 0 else '(' + str(u[1]) + ')'}\cdot{v[1] if v[1] >= 0 else '(' + str(v[1]) + ')'}={d}$.", ["Multiply the first components and the second components and add."]))
    for n, (u, v) in enumerate((((1, 1), (1, 0)), ((1, sp.sqrt(3)), (1, 0)), ((2, 2), (-1, 1))), 1):
        c = rad((u[0] * v[0] + u[1] * v[1]) / (sp.sqrt(u[0] ** 2 + u[1] ** 2) * sp.sqrt(v[0] ** 2 + v[1] ** 2)))
        th = sp.acos(c)
        it.append(item_num(f"ad-da{n}", rf"The angle between $\vec u={pt2_tex(u)}$ and $\vec v={pt2_tex(v)}$ in the plane is (an exact value)", th, rf"$\cos\theta=\dfrac{{\dotp{{\vec u}}{{\vec v}}}}{{\norm{{\vec u}}\norm{{\vec v}}}}={tex(c)}$, so $\theta={tex(th)}$.", ["Compute the cosine first."]))
    for n, (u, v) in enumerate((((1, 2, 3), (4, -1, 2)), ((2, -1, 0), (1, 2, 5)), ((1, 0, 1), (0, 1, 1))), 1):
        it.append(item_num(f"ad-ds{n}", rf"In space, $\dotp{{\vec u}}{{\vec v}}$ for $\vec u={pt3_tex(u)}$ and $\vec v={pt3_tex(v)}$ is", dot(u, v), rf"$\dotp{{\vec u}}{{\vec v}}={tex(dot(u, v))}$ (three products).", ["Three products."]))
    it.append(item_num("ad-dk", r"For which $k$ are $(k,3,-2)$ and $(2,1,4)$ perpendicular?", sp.Rational(5, 2), r"$2k+3-8=0$, so $k=\dfrac52$.", ["Set the dot product equal to $0$."]))
    return it


def circle_param_items() -> list[dict]:
    it: list[dict] = []
    for n, (p_, q_, r_) in enumerate(((4, -1, 2), (1, -2, 3), (0, 5, 4)), 1):
        gen = sp.expand((x - p_) ** 2 + (y - q_) ** 2 - r_**2)
        it.append(item_pt2(f"ad-cc{n}", rf"The center of the circle $x={p_}+{r_}\cos t$, $y={q_ if q_ >= 0 else '(' + str(q_) + ')'}+{r_}\sin t$ is", (p_, q_), rf"The constants are the coordinates of the center: ${pt2_tex((p_, q_))}$.", ["The constants in the parametric equations."]))
        it.append(ex(f"ad-ce{n}", rf"The analytic equation of the circle $x={p_}+{r_}\cos t$, $y={q_ if q_ >= 0 else '(' + str(q_) + ')'}+{r_}\sin t$ is", "equation", f"{eng(gen)}=0", coordinates=["x", "y"],
                     hints=["Eliminate $t$ with $\\cos^2t+\\sin^2t=1$ and expand."], solution=rf"$(x-{p_})^2+(y-{q_})^2={r_ ** 2}$, that is ${tex(gen)}=0$."))
    for n, (p_, q_, r_, t_) in enumerate(((0, 0, 3, 2 * PI / 3), (1, -2, 3, PI / 2)), 1):
        P = (rad(p_ + r_ * sp.cos(t_)), rad(q_ + r_ * sp.sin(t_)))
        it.append(item_pt2(f"ad-cp{n}", rf"The point of the circle with center ${pt2_tex((p_, q_))}$ and radius ${r_}$ for $t={tex(t_)}$ is", P, rf"$x={p_}+{r_}\cos t={tex(P[0])}$, $y={q_}+{r_}\sin t={tex(P[1])}$.", ["Replace $t$."]))
    it.append(item_num("ad-cr", r"The circle $x=3\cos t$, $y=3\sin t$ is at distance from the origin equal to", sp.Integer(3), r"$\sqrt{9\cos^2t+9\sin^2t}=3$ for every $t$.", ["Use $\\cos^2t+\\sin^2t=1$."]))
    return it


def ellipse_items() -> list[dict]:
    it: list[dict] = []
    for n, (a, b) in enumerate(((5, 3), (4, 2), (13, 5), (5, 4)), 1):
        c = rad(sp.sqrt(a * a - b * b))
        e = rad(c / a)
        lab = rf"For the ellipse $\dfrac{{x^2}}{{{a * a}}}+\dfrac{{y^2}}{{{b * b}}}=1$ "
        it.append(item_num(f"ad-el{n}a", lab + r"the area (unit squ: number only) is", rad(PI * a * b), rf"$\pi ab=\pi\cdot{a}\cdot{b}={tex(PI * a * b)}$.", ["$\\pi ab$."]))
        it.append(item_num(f"ad-el{n}l", lab + r"the length of the latus rectum is", rad(sp.Rational(2 * b * b, a)), rf"$\dfrac{{2b^2}}a=\dfrac{{{2 * b * b}}}{{{a}}}$.", ["$\\dfrac{2b^2}a$."]))
        it.append(item_num(f"ad-el{n}d", lab + r"the directrix $x=d$ with $d>0$ has $d=$", rad(sp.Rational(a * a) / c), rf"$d=\dfrac{{a^2}}c$ with $a^2={a * a}$ and $c={tex(c)}$, so $d={tex(rad(sp.Rational(a * a) / c))}$.", ["$\\dfrac{a^2}c$."]))
    t_ = PI / 3
    P = (rad(5 * sp.cos(t_)), rad(3 * sp.sin(t_)))
    it.append(item_pt2("ad-ep", r"The point of the ellipse $x=5\cos t$, $y=3\sin t$ for $t=\dfrac\pi3$ is", P, rf"$x=5\cos\dfrac\pi3={tex(P[0])}$, $y=3\sin\dfrac\pi3={tex(P[1])}$.", ["Replace $t$."]))
    it.append(item_num("ad-ef", r"On the ellipse $\dfrac{x^2}{25}+\dfrac{y^2}9=1$ the point with $x=\dfrac52$ has the focal radius $MF_1=a+ex$ equal to", sp.Integer(7), r"$e=\dfrac45$, so $MF_1=5+\dfrac45\cdot\dfrac52=7$.", ["$MF_1=a+ex$."]))
    it.append(item_num("ad-ee", r"The eccentricity of $9x^2+25y^2=225$ is", R(4, 5), r"$\dfrac{x^2}{25}+\dfrac{y^2}9=1$: $a=5$, $c=4$, $e=\dfrac45$.", ["Divide by $225$ first."]))
    return it


def hyperbola_items() -> list[dict]:
    it: list[dict] = []
    for n, (a, b) in enumerate(((3, 4), (4, 3), (5, 12), (1, 1)), 1):
        c = rad(sp.sqrt(a * a + b * b))
        lab = rf"For the hyperbola $\dfrac{{x^2}}{{{a * a}}}-\dfrac{{y^2}}{{{b * b}}}=1$ "
        it.append(item_num(f"ad-hy{n}e", lab + r"the eccentricity is", rad(c / a), rf"$c=\sqrt{{{a * a}+{b * b}}}={tex(c)}$ and $e=\dfrac ca={tex(rad(c / a))}$.", ["$c^2=a^2+b^2$."]))
        it.append(item_num(f"ad-hy{n}l", lab + r"the length of the latus rectum is", rad(sp.Rational(2 * b * b, a)), rf"$\dfrac{{2b^2}}a=\dfrac{{{2 * b * b}}}{{{a}}}$.", ["$\\dfrac{2b^2}a$."]))
        it.append(item_num(f"ad-hy{n}d", lab + r"the directrix $x=d$ with $d>0$ has $d=$", rad(sp.Rational(a * a) / c), rf"$d=\dfrac{{a^2}}c$ with $a^2={a * a}$ and $c={tex(c)}$, so $d={tex(rad(sp.Rational(a * a) / c))}$.", ["$\\dfrac{a^2}c$."]))
    it.append(item_num("ad-hs", r"The slope of the asymptote $y=mx$ ($m>0$) of $\dfrac{x^2}{9}-\dfrac{y^2}{16}=1$ is", R(4, 3), r"$m=\dfrac ba=\dfrac43$.", ["$m=\\dfrac ba$."]))
    it.append(item_num("ad-hf", r"On the right branch of $\dfrac{x^2}9-\dfrac{y^2}{16}=1$ the point with $x=5$ has the focal radius $MF_1=ex+a$ equal to", R(34, 3), r"$e=\dfrac53$, so $MF_1=\dfrac53\cdot5+3=\dfrac{34}3$.", ["$MF_1=ex+a$ on the right branch."]))
    it.append(item_num("ad-hr", r"The eccentricity of a rectangular hyperbola ($a=b$) is", sp.sqrt(2), r"$c=\sqrt{a^2+a^2}=a\sqrt2$, so $e=\sqrt2$.", ["$c^2=a^2+b^2$ with $b=a$."]))
    return it


def centers_items() -> list[dict]:
    it: list[dict] = []
    for n, (A, B, C) in enumerate((((0, 0), (14, 0), (5, 12)), ((0, 0), (6, 0), (0, 8)), ((0, 0), (4, 0), (0, 3))), 1):
        a = rad(sp.sqrt((B[0] - C[0]) ** 2 + (B[1] - C[1]) ** 2))
        b = rad(sp.sqrt((C[0] - A[0]) ** 2 + (C[1] - A[1]) ** 2))
        c = rad(sp.sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2))
        S = rad(sp.Abs((B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1])) / 2)
        s = (a + b + c) / 2
        I = (rad((a * A[0] + b * B[0] + c * C[0]) / (a + b + c)), rad((a * A[1] + b * B[1] + c * C[1]) / (a + b + c)))
        r = rad(S / s)
        Rr = rad(a * b * c / (4 * S))
        lab = rf"For the triangle $A{pt2_tex(A)}$, $B{pt2_tex(B)}$, $C{pt2_tex(C)}$ "
        it.append(item_pt2(f"ad-ci{n}", lab + r"the incenter $I=\dfrac{aA+bB+cC}{a+b+c}$ is", I, rf"$a=BC={tex(a)}$, $b=CA={tex(b)}$, $c=AB={tex(c)}$, so $I={pt2_tex(I)}$.", ["The weights are the opposite sides."]))
        it.append(item_num(f"ad-cr{n}", lab + r"the inradius $r=\dfrac Ss$ is", r, rf"$S={tex(S)}$ and $s={tex(rad(s))}$, so $r={tex(r)}$.", ["$r=S/s$."]))
        it.append(item_num(f"ad-cx{n}", lab + r"the circumradius $R=\dfrac{abc}{4S}$ is", Rr, rf"$R=\dfrac{{{tex(a)}\cdot{tex(b)}\cdot{tex(c)}}}{{4\cdot{tex(S)}}}={tex(Rr)}$.", ["$R=\\dfrac{abc}{4S}$."]))
    return it


# --- a complete study of a tetrahedron: edge and face, opposite edges, circumsphere -------------------------------------------------------------
def study_items() -> list[dict]:
    it: list[dict] = []
    m, nn, p, q = sp.symbols("m n p q")
    tets = {
        "n": ((-1, -3, 1), (5, 3, 8), (-1, -3, 5), (2, 1, 4)),
        "a": ((0, 0, 0), (3, 0, 0), (0, 4, 0), (0, 0, 12)),
        "b": ((0, 0, 0), (4, 0, 0), (0, 4, 0), (0, 0, 4)),
        "c": ((0, 0, 0), (2, 0, 0), (0, 2, 0), (1, 1, 2)),
    }
    for name, (A, B, C, D) in tets.items():
        Am, Bm, Cm, Dm = (sp.Matrix(P) for P in (A, B, C, D))
        AB, AC, AD, BC = Bm - Am, Cm - Am, Dm - Am, Cm - Bm
        N = AB.cross(AC)
        sin = rad(abs(N.dot(AD)) / (N.norm() * AD.norm()))
        cr = AD.cross(BC)
        box = sp.Matrix.hstack(AB, AD, BC).det()
        d = rad(abs(box) / cr.norm())
        head = "The tetrahedron has the vertices " + ", ".join(rf"${'ABCD'[i]}{pt3_tex(P)}$" for i, P in enumerate((A, B, C, D))) + ". "
        it.append(item_num(f"st-{name}s", head + r"The sine of the angle between the edge $AD$ and the face $ABC$ is", sin,
                           rf"$\vec N_{{ABC}}=\crossp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}={pt3_tex(tuple(N))}$ and $\overrightarrow{{AD}}={pt3_tex(tuple(AD))}$; $|\dotp{{\vec N}}{{\overrightarrow{{AD}}}}|={tex(abs(N.dot(AD)))}$, $\norm{{\vec N}}={tex(rad(N.norm()))}$, $\norm{{\overrightarrow{{AD}}}}={tex(rad(AD.norm()))}$, so $\sin\theta={tex(sin)}$.",
                           [r"$\sin\theta=\dfrac{|\dotp{\vec N}{\overrightarrow{AD}}|}{\norm{\vec N}\norm{\overrightarrow{AD}}}$."]))
        it.append(item_num(f"st-{name}d", head + r"The distance between the opposite edges $AD$ and $BC$ (unit lu: number only) is", d,
                           rf"$\overrightarrow{{AB}}={pt3_tex(tuple(AB))}$, $\overrightarrow{{AD}}={pt3_tex(tuple(AD))}$, $\overrightarrow{{BC}}={pt3_tex(tuple(BC))}$. The box product is ${tex(box)}$ and $\crossp{{\overrightarrow{{AD}}}}{{\overrightarrow{{BC}}}}={pt3_tex(tuple(cr))}$ has the length ${tex(rad(cr.norm()))}$, so $d={tex(d)}$.",
                           [r"$d=\dfrac{|\boxp{\overrightarrow{AB}}{\overrightarrow{AD}}{\overrightarrow{BC}}|}{\norm{\crossp{\overrightarrow{AD}}{\overrightarrow{BC}}}}$."]))
        eqs = [P[0] ** 2 + P[1] ** 2 + P[2] ** 2 + 2 * m * P[0] + 2 * nn * P[1] + 2 * p * P[2] + q for P in (A, B, C, D)]
        sol = sp.solve(eqs, (m, nn, p, q), dict=True)[0]
        c = (rad(-sol[m]), rad(-sol[nn]), rad(-sol[p]))
        rho2 = rad(sol[m] ** 2 + sol[nn] ** 2 + sol[p] ** 2 - sol[q])
        rho = rad(sp.sqrt(rho2))
        assert all(rad(sum((P[i] - c[i]) ** 2 for i in range(3)) - rho2) == 0 for P in (A, B, C, D))
        txt = rf"Solving the four linear equations: $m={tex(sol[m])}$, $n={tex(sol[nn])}$, $p={tex(sol[p])}$, $q={tex(sol[q])}$. The center is ${pt3_tex(c)}$ and $\rho^2={tex(rho2)}$."
        it.append(item_pt(f"st-{name}c", head + r"The center of the circumsphere is", c, txt, [r"The center is $(-m,-n,-p)$."]))
        it.append(item_num(f"st-{name}a", head + r"The area of the circumsphere (unit squ: number only) is", rad(4 * PI * rho2), txt + rf" The area is $4\pi\rho^2={tex(rad(4 * PI * rho2))}$.", [r"$4\pi\rho^2$."]))
        it.append(item_num(f"st-{name}v", head + r"The volume of the circumsphere (unit cu: number only) is", rad(sp.Rational(4, 3) * PI * rho**3), txt + rf" The volume is $\dfrac43\pi\rho^3={tex(rad(sp.Rational(4, 3) * PI * rho**3))}$.", [r"$\dfrac43\pi\rho^3$."]))
    it.append(mc("st-m1", r"The box product $\boxp{\overrightarrow{AB}}{\overrightarrow{AD}}{\overrightarrow{BC}}$ of two opposite edges of a tetrahedron is never $0$ because", ["The edges are perpendicular", "The four vertices are not in one plane", "The edges have the same length", "The edges are parallel"], 1,
                 r"The two opposite edges are not coplanar.", r"If the box product were $0$, the lines $AD$ and $BC$ would lie in one plane, and the four vertices would be coplanar: there would be no tetrahedron."))
    return it


def circ_det_items() -> list[dict]:
    it: list[dict] = []
    for n, P in enumerate((((-3, 2), (1, 5), (5, -7)), ((0, 0), (14, 0), (5, 12)), ((1, 1), (5, 1), (1, 4)), ((-2, 0), (4, 0), (0, 6))), 1):
        S = rad(sp.Matrix([[x_, y_, 1] for x_, y_ in P]).det() / 2)
        dx = sp.Matrix([[x_ * x_ + y_ * y_, y_, 1] for x_, y_ in P]).det()
        dy = sp.Matrix([[x_, x_ * x_ + y_ * y_, 1] for x_, y_ in P]).det()
        O = (rad(dx / (4 * S)), rad(dy / (4 * S)))
        assert len({rad((O[0] - x_) ** 2 + (O[1] - y_) ** 2) for x_, y_ in P}) == 1
        R2 = rad((O[0] - P[0][0]) ** 2 + (O[1] - P[0][1]) ** 2)
        head = rf"For the triangle $A{pt2_tex(P[0])}$, $B{pt2_tex(P[1])}$, $C{pt2_tex(P[2])}$ "
        sol = rf"The signed area is $S={tex(S)}$, so $4S={tex(4 * S)}$. The determinants are ${tex(dx)}$ and ${tex(dy)}$, so $O=\left(\dfrac{{{tex(dx)}}}{{{tex(4 * S)}}},\dfrac{{{tex(dy)}}}{{{tex(4 * S)}}}\right)={pt2_tex(O)}$."
        it.append(item_num(f"cd-{n}s", head + r"the signed area $S=\dfrac12\begin{vmatrix}x_1&y_1&1\\x_2&y_2&1\\x_3&y_3&1\end{vmatrix}$ is", S, rf"$S={tex(S)}$ (the sign shows the orientation of $A,B,C$).", ["Expand the determinant."]))
        it.append(item_num(f"cd-{n}x", head + r"the circumcenter coordinate $x_O$ (with the determinants and the signed $4S$) is", O[0], sol, [r"$x_O=\dfrac1{4S}\begin{vmatrix}x_i^2+y_i^2&y_i&1\end{vmatrix}$ (three rows)."]))
        it.append(item_num(f"cd-{n}y", head + r"the circumcenter coordinate $y_O$ is", O[1], sol, [r"$y_O=\dfrac1{4S}\begin{vmatrix}x_i&x_i^2+y_i^2&1\end{vmatrix}$ (three rows)."]))
        it.append(item_num(f"cd-{n}r", head + r"the circumradius $R$ (unit lu: number only) is", rad(sp.sqrt(R2)), sol + rf" Then $R^2=OA^2={tex(R2)}$ and $R={tex(rad(sp.sqrt(R2)))}$.", [r"$R=OA$."]))
    return it


@with_units
def register() -> None:
    sets = [
        ("m03-space/u01-points-lines-planes", "l06-cylindrical-and-spherical-coordinates", "add-coordinates", "Polar, cylindrical and spherical coordinates.", cyl_sph_items(), True),
        ("m03-space/u02-the-tetrahedron", "l05-altitudes-of-a-tetrahedron", "add-altitudes", "The altitudes of a tetrahedron: volume, face, height and foot.", altitude_items(), True),
        ("m03-space/u03-the-sphere", "l03-parametric-equations-area-and-volume-of-a-sphere", "add-sphere", "The sphere: four points, parametric equations, area and volume.", sphere_items(), True),
        ("m03-space/u03-the-sphere", "l04-tangent-planes-and-normals-of-a-sphere", "add-tps", "Tangent planes, normals and tangent lengths of a sphere.", tps_items(), True),
        ("m01-vectors/u02-products-of-vectors", "l01-dot-product", "add-dot-2d3d", "The dot product in the plane and in space.", dot_items(), False),
        ("m02-plane/u03-the-circle", "l01-equation-of-a-circle", "add-circle-param", "The parametric circle.", circle_param_items(), False),
        ("m02-plane/u05-conics-and-loci", "l02-the-ellipse", "add-ellipse", "The ellipse: area, latus rectum, directrices, parametric points.", ellipse_items(), False),
        ("m02-plane/u05-conics-and-loci", "l03-the-hyperbola", "add-hyperbola", "The hyperbola: eccentricity, latus rectum, directrices, asymptotes.", hyperbola_items(), False),
        ("m02-plane/u02-the-triangle", "l07-euler-line-and-complete-study", "add-centers", "The incenter and the radii of a triangle.", centers_items(), False),
        ("m03-space/u02-the-tetrahedron", "l06-complete-study-of-a-tetrahedron", "add-study", "Edge and face angle, distance between opposite edges, circumsphere.", study_items(), True),
        ("m02-plane/u02-the-triangle", "l05-perpendicular-bisectors-and-circumcenter", "add-circ-det", "The circumcenter with determinants.", circ_det_items(), False),
    ]
    for unit, lesson, sid, task, items, orphan in sets:
        for item in items:
            item["id"] = item["id"].lower()
        add_extra(f"{BASE}/{unit}/{lesson}", exset_plain(sid, task, items, format=FMT), SCRIPT, orphan=orphan)
    assert (TC, TD, cross, sub, dist_point_plane, plane_through, pt3_eng, sp.Integer(1)) is not None
