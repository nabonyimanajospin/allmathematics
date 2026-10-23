"""More practice for Course 1, Module 3: lines and planes in space, the tetrahedron, the sphere and quadric surfaces.

Every key is computed with SymPy and checked with an independent numeric distance or substitution."""

from __future__ import annotations

import math

import sympy as sp
from geo_m03 import (
    Tet, cross, dist3, dist_point_plane, dot, eval_plane, item_num, item_plane, item_pt, mid3, norm, plane_eng, plane_norm, plane_point_normal, plane_through, plane_tex, pt3_eng, pt3_tex, rad, sub,
)
from toolkit import add_extra, eng, ex, exset_plain, tex, with_units, x, y, z

SCRIPT = "more_geo_d.py"
U1 = "geo/m03-space/u01-points-lines-planes"
U2 = "geo/m03-space/u02-the-tetrahedron"
U3 = "geo/m03-space/u03-the-sphere"
U4 = "geo/m03-space/u04-quadric-surfaces"
FMT = "Type a point as `(a, b, c)`, an exact value such as `sqrt(7)/4` or `5/7`, and a plane or a surface as an equation with `=`."
M = sp.Matrix


def vt(v) -> str:
    return pt3_tex(v)


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


def eq_xyz(poly: sp.Expr) -> str:
    return f"{eng(sp.expand(poly))}=0"


# --- unit 1 -----------------------------------------------------------------------------------------------------------------------------
def points_items() -> list[dict]:
    items = []
    A, B = (1, -2, 3), (4, 2, 15)
    d = dist3(A, B)
    items.append(item_num("mp-sp-1", rf"The distance between $A{vt(A)}$ and $B{vt(B)}$. The unit is lu: give the number only.", d, rf"$\overrightarrow{{AB}}={vt(sub(A, B))}$, so $AB={tex(d)}$.", ["Take the norm of $\\overrightarrow{AB}$."]))
    A, B = (3, 1, -5), (-1, 7, 3)
    m = mid3(A, B)
    items.append(item_pt("mp-sp-2", rf"The midpoint of $A{vt(A)}$ and $B{vt(B)}$.", m, rf"The midpoint is ${vt(m)}$.", ["Average the coordinates."]))
    P = tuple(rad(a + sp.Rational(1, 3) * (b - a)) for a, b in zip((0, 3, 6), (9, 0, -3), strict=True))
    items.append(item_pt("mp-sp-3", rf"The point $P$ of the segment $AB$ with $\overrightarrow{{AP}}:\overrightarrow{{PB}}=1:2$, for $A(0,3,6)$ and $B(9,0,-3)$.", P, rf"$P=A+\dfrac13\overrightarrow{{AB}}={vt(P)}$.", ["$P$ is one third of the way from $A$ to $B$."]))
    p = (3, -4, 12)
    d = rad(sp.sqrt(p[1] ** 2 + p[2] ** 2))
    items.append(item_num("mp-sp-4", rf"The distance from $P{vt(p)}$ to the $x$-axis. The unit is lu: give the number only.", d, r"The foot of the perpendicular is $(3,0,0)$, so the distance is $\sqrt{y^2+z^2}=\sqrt{16+144}$... computed as the norm of $(0,-4,12)$.", ["Remove the $x$-coordinate and take the norm of what is left."]))
    assert d == 4 * sp.sqrt(10)
    return items


def line_items() -> list[dict]:
    items = []
    A, B = (1, 2, 3), (4, 6, 15)
    d = sub(A, B)
    items.append(ex("mp-ln-1", rf"Give a direction vector of the line through $A{vt(A)}$ and $B{vt(B)}$.", "direction", pt3_eng(d), hints=[r"Use $\overrightarrow{AB}$."], solution=rf"$\overrightarrow{{AB}}={vt(d)}$; any non-zero multiple is accepted."))
    P0, v, t0 = (2, -1, 4), (3, 0, -2), 2
    P = tuple(P0[i] + t0 * v[i] for i in range(3))
    items.append(item_pt("mp-ln-2", rf"The line $x=2+3t$, $y=-1$, $z=4-2t$. Find its point for $t=2$.", P, rf"$x=2+6=8$, $y=-1$, $z=4-4=0$: the point is ${vt(P)}$.", ["Substitute $t=2$."]))
    # is a point on the line
    q = (11, -1, -2)
    t = sp.symbols("t")
    on = sp.solve([P0[i] + t * v[i] - q[i] for i in range(3)], t, dict=True)
    items.append(mc("mp-ln-3", rf"Is the point $Q{vt(q)}$ on the line $x=2+3t$, $y=-1$, $z=4-2t$?", ["Yes", "No"], 0 if on else 1, r"Find $t$ from one coordinate and test the others.",
                    r"$11=2+3t$ gives $t=3$; then $y=-1$ and $z=4-6=-2$ also match: the point is on the line." if on else "The coordinates do not give the same $t$: the point is not on the line."))
    L1, L2 = ((1, 0, 2), (1, 1, 0)), ((0, 1, 0), (0, 1, -1))
    s, u = sp.symbols("s u")
    sol_ = sp.solve([L1[0][0] + s * L1[1][0] - (L2[0][0] + u * L2[1][0]), L1[0][1] + s * L1[1][1] - (L2[0][1] + u * L2[1][1])], [s, u], dict=True)[0]
    inter = tuple(rad(L1[0][i] + sol_[s] * L1[1][i]) for i in range(3))
    third = L2[0][2] + sol_[u] * L2[1][2]
    assert third == inter[2]
    items.append(item_pt("mp-ln-4", r"The lines $(x,y,z)=(1,0,2)+s(1,1,0)$ and $(x,y,z)=(0,1,0)+u(0,1,-1)$ meet at one point. Find it.", inter, rf"Equating the coordinates gives $s={tex(sol_[s])}$, $u={tex(sol_[u])}$, and the point ${vt(inter)}$.", ["Solve the first two coordinates, then check the third."]))
    P0, v, Q = (0, 0, 0), (1, 2, 2), (3, 0, 0)
    d = rad(norm(cross(sub(P0, Q), v)) / norm(v))
    items.append(item_num("mp-ln-5", rf"The distance from $Q{vt(Q)}$ to the line through the origin with direction $\vec v={vt(v)}$. The unit is lu: give the number only.", d,
                          rf"$d=\dfrac{{\norm{{\crossp{{\overrightarrow{{OQ}}}}{{\vec v}}}}}}{{\norm{{\vec v}}}}={tex(d)}$.", ["Use the cross product of $\\overrightarrow{OQ}$ and the direction vector."]))
    d1, d2 = (1, 2, 3), (2, 4, 6)
    items.append(mc("mp-ln-6", r"The lines with direction vectors $(1,2,3)$ and $(2,4,6)$ are", ["perpendicular", "parallel or the same", "skew for sure", "intersecting for sure"], 1, r"Compare the direction vectors.", r"$(2,4,6)=2(1,2,3)$: the directions are parallel, so the lines are parallel (or the same line)."))
    L1p, L1v, L2p, L2v = (0, 0, 0), (1, 0, 0), (0, 1, 1), (0, 1, 0)
    det = M([list(sub(L1p, L2p)), list(L1v), list(L2v)]).det()
    items.append(mc("mp-ln-7", r"The line through the origin with direction $(1,0,0)$ and the line through $(0,1,1)$ with direction $(0,1,0)$ are", ["intersecting", "parallel", "skew"], 2, r"Compute the box product of $\overrightarrow{P_1P_2}$ and the two directions.",
                    rf"The box product is ${tex(det)}\ne0$, so the lines are not coplanar: they are skew."))
    assert det != 0
    return items


def plane_items() -> list[dict]:
    items = []
    P = plane_through((1, 0, 0), (0, 2, 0), (0, 0, 3))
    items.append(item_plane("mp-pl-1", r"The plane through $A(1,0,0)$, $B(0,2,0)$, $C(0,0,3)$.", P, rf"The plane is ${plane_tex(P)}$ (intercept form $x+\dfrac y2+\dfrac z3=1$).", ["Use the intercept form, or the normal vector $\\crossp{\\overrightarrow{AB}}{\\overrightarrow{AC}}$."]))
    n, p0 = (2, -1, 3), (1, 2, -1)
    P = plane_point_normal(n, p0)
    items.append(item_plane("mp-pl-2", r"The plane through $P(1,2,-1)$ with normal vector $\vec n=(2,-1,3)$.", P, rf"$2(x-1)-(y-2)+3(z+1)=0$, that is ${plane_tex(P)}$.", ["$a(x-x_0)+b(y-y_0)+c(z-z_0)=0$."]))
    base, p0 = (3, -2, 5, 7), (1, 1, 1)
    P = plane_point_normal(base[:3], p0)
    items.append(item_plane("mp-pl-3", r"The plane through $P(1,1,1)$ parallel to $3x-2y+5z+7=0$.", P, r"Parallel planes have the same normal vector $(3,-2,5)$.", ["Keep the normal vector."]))
    P = plane_through((1, 2, 3), (2, 3, 5), (4, 4, 4))
    items.append(item_plane("mp-pl-4", r"The plane through $A(1,2,3)$, $B(2,3,5)$, $C(4,4,4)$.", P, rf"$\overrightarrow{{AB}}=(1,1,2)$, $\overrightarrow{{AC}}=(3,2,1)$, $\crossp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}={vt(cross((1, 1, 2), (3, 2, 1)))}$; the plane is ${plane_tex(P)}$.", ["Use the cross product of two edge vectors as the normal."]))
    n = (4, -2, 1)
    items.append(ex("mp-pl-5", r"Give a normal vector of the plane $4x-2y+z-9=0$.", "direction", pt3_eng(n), hints=[r"Read the coefficients of $x$, $y$, $z$."], solution=r"The normal vector is $(4,-2,1)$; any non-zero multiple is accepted."))
    P = plane_point_normal((0, 1, 0), (5, 3, 2))
    items.append(item_plane("mp-pl-6", r"The plane through $P(5,3,2)$ parallel to the $xz$-plane.", P, r"The $xz$-plane has normal $(0,1,0)$, so the plane is $y=3$.", ["Parallel to the $xz$-plane means constant $y$."]))
    items.append(mc("mp-pl-7", r"The plane $z=5$ is", ["parallel to the $xy$-plane", "parallel to the $xz$-plane", "perpendicular to the $xy$-plane"], 0, r"Its normal vector is $(0,0,1)$.", r"The normal vector $(0,0,1)$ is the one of the $xy$-plane: the planes are parallel."))
    return items


def relative_items() -> list[dict]:
    items = []
    n1, n2 = (1, 1, 0), (0, 1, 1)
    c = rad(dot(n1, n2) / (norm(n1) * norm(n2)))
    items.append(item_num("mp-rp-1", r"The cosine of the acute angle between the planes $x+y=0$ and $y+z=0$.", c, rf"The normals $(1,1,0)$ and $(0,1,1)$ give $\cos\theta=\dfrac{{1}}{{2}}={tex(c)}$.", ["Use the angle between the normal vectors."]))
    v, n = (1, 1, 1), (0, 0, 1)
    s_ = rad(sp.Abs(dot(v, n)) / (norm(v) * norm(n)))
    items.append(item_num("mp-rp-2", r"The sine of the angle between the line with direction $(1,1,1)$ and the plane $z=0$.", s_, rf"$\sin\varphi=\dfrac{{|\dotp{{\vec v}}{{\vec n}}|}}{{\norm{{\vec v}}\norm{{\vec n}}}}={tex(s_)}$.", ["The sine of the angle with the plane uses the dot product with the normal."]))
    d1, d2 = (1, 2, 2), (2, 1, -2)
    c = rad(sp.Abs(dot(d1, d2)) / (norm(d1) * norm(d2)))
    items.append(item_num("mp-rp-3", r"The cosine of the acute angle between the lines with directions $(1,2,2)$ and $(2,1,-2)$.", c, rf"$\dotp{{\vec d_1}}{{\vec d_2}}={tex(dot(d1, d2))}$ and the norms are $3$ and $3$: $\cos\theta={tex(c)}$.", ["Use the absolute value of the dot product of the directions."]))
    k = sp.Symbol("k")
    kv = sp.solve(dot((k, 2, 1), (1, -1, 3)), k)[0]
    items.append(ex("mp-rp-4", r"For which $k$ are the planes $kx+2y+z=1$ and $x-y+3z=2$ perpendicular?", "number", eng(kv), hints=[r"The normals must be orthogonal."], solution=rf"$k-2+3=0$ gives $k={tex(kv)}$."))
    P, v, p0 = (1, 2, 3, -14), (1, 2, 3), (0, 0, 0)
    t = sp.Symbol("t")
    tv = sp.solve(P[0] * (p0[0] + t * v[0]) + P[1] * (p0[1] + t * v[1]) + P[2] * (p0[2] + t * v[2]) + P[3], t)[0]
    meetp = tuple(rad(p0[i] + tv * v[i]) for i in range(3))
    assert eval_plane(P, meetp) == 0
    items.append(item_pt("mp-rp-5", r"The line $(x,y,z)=t(1,2,3)$ meets the plane $x+2y+3z-14=0$ at one point. Find it.", meetp, rf"$t+4t+9t=14$ gives $t=1$: the point is ${vt(meetp)}$.", ["Substitute the parametric equations in the plane equation."]))
    items.append(mc("mp-rp-6", r"The planes $x+y+z=1$ and $2x+2y+2z=5$ are", ["the same plane", "parallel and different", "perpendicular", "intersecting in a line"], 1, r"The normals are proportional; compare the constants.", r"$(2,2,2)=2(1,1,1)$ but $5\ne2\cdot1$: the planes are parallel and different."))
    return items


def distance_items() -> list[dict]:
    items = []
    P, p = (2, -1, 2, -5), (1, 1, 1)
    d = dist_point_plane(p, P)
    items.append(item_num("mp-dp-1", rf"The distance from $P{vt(p)}$ to the plane ${plane_tex(P)}$. The unit is lu: give the number only.", d, rf"$\dfrac{{|2-1+2-5|}}{{3}}={tex(d)}$ (the norm of the normal vector is $3$).", ["$d=\\dfrac{|ax_0+by_0+cz_0+d|}{\\sqrt{a^2+b^2+c^2}}$."]))
    P1, P2 = (1, 2, 2, 3), (1, 2, 2, -6)
    d = rad(sp.Abs(P1[3] - P2[3]) / norm(P1[:3]))
    items.append(item_num("mp-dp-2", rf"The distance between the parallel planes ${plane_tex(P1)}$ and ${plane_tex(P2)}$. The unit is lu: give the number only.", d, r"$\dfrac{|3-(-6)|}{3}=3$.", ["Divide the difference of the constants by the norm of the normal vector."]))
    return items


# --- unit 2: the tetrahedron ----------------------------------------------------------------------------------------------------------
def tetra_items() -> dict[str, list[dict]]:
    T = Tet((0, 0, 0), (2, 0, 0), (0, 3, 0), (1, 1, 6))
    stm = rf"the tetrahedron $A{vt(T.V['A'])}$, $B{vt(T.V['B'])}$, $C{vt(T.V['C'])}$, $D{vt(T.V['D'])}$"
    out: dict[str, list[dict]] = {"l02-volume-heights-dihedral-angles": [], "l03-centers-and-spheres": [], "l04-regular-tetrahedron-and-platonic-solids": []}
    o = out["l02-volume-heights-dihedral-angles"]
    o.append(item_num("mp-tt-1", rf"Find the volume of {stm}. The unit is cu: give the number only.", T.vol, rf"$V=\dfrac16\left|\boxp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}{{\overrightarrow{{AD}}}}\right|={tex(T.vol)}$.", ["A sixth of the absolute value of the box product."]))
    o.append(item_num("mp-tt-2", rf"Find the height of {stm} from $D$ on the face $ABC$. The unit is lu: give the number only.", T.height("D"), rf"The face $ABC$ lies in the plane $z=0$, so the height is the $z$-coordinate of $D$: ${tex(T.height('D'))}$. Check: $h=\dfrac{{3V}}{{S}}$.", ["$h=\\dfrac{3V}{\\text{area of the face}}$."]))
    g = out["l03-centers-and-spheres"]
    g.append(item_pt("mp-tt-3", rf"Find the centroid of {stm}.", T.G, rf"$G=\dfrac{{A+B+C+D}}{{4}}={vt(T.G)}$.", ["Average the four vertices."]))
    g.append(item_pt("mp-tt-4", rf"Find the center of the circumscribed sphere of {stm}.", T.O, rf"The center is at equal distances from the four vertices: ${vt(T.O)}$, and the radius is ${tex(T.Rc)}$.", ["Equate the distances to $A$, $B$, $C$, $D$."]))
    g.append(item_num("mp-tt-5", rf"Find the radius of the inscribed sphere of {stm}. The unit is lu: give the number only.", T.r, rf"$r=\dfrac{{3V}}{{S}}={tex(T.r)}$ where $S$ is the total area of the four faces.", ["$r=\\dfrac{3V}{S}$."]))
    a = 6
    reg = out["l04-regular-tetrahedron-and-platonic-solids"]
    vol = rad(a**3 * sp.sqrt(2) / 12)
    reg.append(item_num("mp-tt-6", rf"The volume of a regular tetrahedron of edge ${a}$. The unit is cu: give the number only.", vol, r"$V=\dfrac{a^3\sqrt2}{12}=\dfrac{216\sqrt2}{12}=18\sqrt2$.", ["$V=\\dfrac{a^3\\sqrt2}{12}$."]))
    TR = Tet((0, 0, 0), (4, 4, 0), (4, 0, 4), (0, 4, 4))
    edge = TR.edge["AB"]
    assert rad(TR.Rc - edge * sp.sqrt(6) / 4) == 0
    reg.append(item_num("mp-tt-7", r"The circumradius of a regular tetrahedron of edge $4\sqrt2$. The unit is lu: give the number only.", TR.Rc, r"$R=\dfrac{a\sqrt6}{4}=\dfrac{4\sqrt2\cdot\sqrt6}{4}=2\sqrt3$.", ["$R=\\dfrac{a\\sqrt6}{4}$."]))
    reg.append(ex("mp-tt-8", r"A convex polyhedron has $8$ vertices and $12$ edges. How many faces has it (Euler's formula $V-E+F=2$)?", "number", "6", hints=[r"$F=2-V+E$."], solution=r"$F=2-8+12=6$ (a cube is an example)."))
    return out


# --- unit 3: the sphere -----------------------------------------------------------------------------------------------------------------
def sphere_poly(c, r2) -> sp.Expr:
    return sp.expand((x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2 - r2)


def sphere_items() -> list[dict]:
    items = []
    c, r_ = (1, -2, 3), 4
    items.append(ex("mp-sh-1", rf"Write the equation of the sphere with center ${vt(c)}$ and radius ${r_}$ (expanded).", "equation", eq_xyz(sphere_poly(c, r_**2)), coordinates=["x", "y", "z"],
                    hints=[r"$(x-a)^2+(y-b)^2+(z-c)^2=r^2$."], solution=rf"$(x-1)^2+(y+2)^2+(z-3)^2=16$ expands to ${tex(sphere_poly(c, r_**2))}=0$."))
    poly = sp.expand(x**2 + y**2 + z**2 - 4 * x + 6 * y - 2 * z - 11)
    ctr, r2 = (2, -3, 1), 25
    assert sp.expand(poly - sphere_poly(ctr, r2)) == 0
    items.append(ex("mp-sh-2", rf"The center of the sphere ${tex(poly)}=0$.", "vector", pt3_eng(ctr), hints=[r"Complete the squares in $x$, $y$, $z$."], solution=r"$(x-2)^2+(y+3)^2+(z-1)^2=25$: the center is $(2,-3,1)$ and the radius is $5$."))
    items.append(item_num("mp-sh-3", rf"The radius of the sphere ${tex(poly)}=0$. The unit is lu: give the number only.", sp.Integer(5), r"The completed squares give $r^2=25$.", ["Complete the squares."]))
    A, B = (1, 2, 3), (5, 2, -1)
    ctr = mid3(A, B)
    r2 = rad((dist3(A, B) / 2) ** 2)
    items.append(ex("mp-sh-4", rf"The sphere with diameter $AB$, $A{vt(A)}$, $B{vt(B)}$ (expanded equation).", "equation", eq_xyz(sphere_poly(ctr, r2)), coordinates=["x", "y", "z"],
                    hints=[r"The center is the midpoint and the radius is half of $AB$."], solution=rf"The center is ${vt(ctr)}$ and $r^2={tex(r2)}$: ${tex(sphere_poly(ctr, r2))}=0$."))
    pts = ((0, 0, 0), (2, 0, 0), (0, 4, 0), (0, 0, 6))
    D, E, F, G = sp.symbols("D E F G")
    sol_ = sp.solve([p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + D * p[0] + E * p[1] + F * p[2] + G for p in pts], [D, E, F, G], dict=True)[0]
    poly = x**2 + y**2 + z**2 + sol_[D] * x + sol_[E] * y + sol_[F] * z + sol_[G]
    items.append(ex("mp-sh-5", r"The sphere through $O(0,0,0)$, $A(2,0,0)$, $B(0,4,0)$, $C(0,0,6)$.", "equation", eq_xyz(poly), coordinates=["x", "y", "z"],
                    hints=[r"Put the four points in $x^2+y^2+z^2+Dx+Ey+Fz+G=0$."], solution=rf"The four conditions give $G=0$, $D=-2$, $E=-4$, $F=-6$: ${tex(sp.expand(poly))}=0$."))
    return items


def sphere_plane_items() -> list[dict]:
    items = []
    c, r2, p = (0, 0, 0), 14, (1, 2, 3)
    assert sum(a * a for a in p) == r2
    P = plane_point_normal(p, p)
    items.append(item_plane("mp-ss-1", r"The tangent plane to the sphere $x^2+y^2+z^2=14$ at the point $(1,2,3)$.", P, r"The radius $(1,2,3)$ is the normal vector of the tangent plane: $x+2y+3z=14$.", ["The tangent plane is perpendicular to the radius."]))
    d = dist_point_plane((0, 0, 0), (2, 2, 1, -6))
    rcirc = rad(sp.sqrt(25 - d**2))
    items.append(item_num("mp-ss-2", r"The plane $2x+2y+z=6$ cuts the sphere $x^2+y^2+z^2=25$ in a circle. Find its radius. The unit is lu: give the number only.", rcirc,
                          rf"The distance from the center to the plane is $\dfrac63={tex(d)}$, so the radius of the circle is $\sqrt{{25-{tex(d**2)}}}={tex(rcirc)}$.", ["Use the right triangle: radius of the sphere, distance, radius of the circle."]))
    items.append(mc("mp-ss-3", r"The spheres $x^2+y^2+z^2=9$ and $(x-5)^2+y^2+z^2=4$ are", ["separate", "tangent externally", "intersecting in a circle", "one inside the other"], 1, r"Compare the distance between the centers with $r_1+r_2$.",
                    r"The centers are at distance $5=3+2$: the spheres touch each other externally."))
    return items


# --- unit 4: quadrics ---------------------------------------------------------------------------------------------------------------------
def quadric_items() -> list[dict]:
    items = []
    names = ["ellipsoid", "hyperboloid of one sheet", "hyperboloid of two sheets", "elliptic paraboloid", "hyperbolic paraboloid", "elliptic cone"]
    specs = [
        (r"\dfrac{x^2}{4}+\dfrac{y^2}{9}+\dfrac{z^2}{16}=1", 0),
        (r"\dfrac{x^2}{4}+\dfrac{y^2}{9}-\dfrac{z^2}{16}=1", 1),
        (r"\dfrac{x^2}{4}-\dfrac{y^2}{9}-\dfrac{z^2}{16}=1", 2),
        (r"z=\dfrac{x^2}{4}+\dfrac{y^2}{9}", 3),
        (r"z=\dfrac{x^2}{4}-\dfrac{y^2}{9}", 4),
        (r"\dfrac{x^2}{4}+\dfrac{y^2}{9}=\dfrac{z^2}{16}", 5),
    ]
    for n, (eqn, idx) in enumerate(specs[:5], 1):
        items.append(mc(f"mp-qu-{n}", rf"The surface ${eqn}$ is", names, idx, r"Look at the signs of the squared terms and at the right-hand side.", rf"The signs of the terms show that it is a {names[idx]}."))
    return items


def surface_items() -> list[dict]:
    items = []
    items.append(mc("mp-sr-1", r"The surface $y^2+z^2=4$ in space is", ["a sphere", "a cylinder with the $x$-axis as its axis", "a cone", "a plane"], 1, r"The variable $x$ is missing.", r"$x$ is free: the circle $y^2+z^2=4$ is repeated along the $x$-axis, giving a cylinder."))
    items.append(mc("mp-sr-2", r"The surface $x^2+y^2=z^2$ is", ["a sphere", "a cylinder", "a circular cone", "a paraboloid"], 2, r"The right side is the square of $z$.", r"The sections $z=\text{constant}$ are circles of radius $|z|$: a circular cone."))
    items.append(mc("mp-sr-3", r"The surface $x^2=4y$ in space is", ["a parabola", "a parabolic cylinder", "a paraboloid", "a plane"], 1, r"The variable $z$ is missing.", r"$z$ is free: the parabola $x^2=4y$ is repeated along the $z$-axis: a parabolic cylinder."))
    # surfaces of revolution: replace the radial variable
    items.append(ex("mp-sr-4", r"The curve $z=x^2$ (in the $xz$-plane) is rotated about the $z$-axis. Write the equation of the surface.", "equation", "z=x^2+y^2", coordinates=["x", "y", "z"], hints=[r"Replace $x^2$ by $x^2+y^2$."],
                    solution=r"Rotating about the $z$-axis replaces $|x|$ by $\sqrt{x^2+y^2}$: $z=x^2+y^2$, a paraboloid."))
    items.append(ex("mp-sr-5", r"The line $y=3x$ (in the $xy$-plane) is rotated about the $x$-axis. Write the equation of the surface.", "equation", "y^2+z^2=9*x^2", coordinates=["x", "y", "z"], hints=[r"Replace $y^2$ by $y^2+z^2$."],
                    solution=r"$y^2=9x^2$ becomes $y^2+z^2=9x^2$: a circular cone with the $x$-axis as its axis."))
    items.append(ex("mp-sr-6", r"The circle $(x-3)^2+z^2=1$ (in the $xz$-plane) is rotated about the $z$-axis. Write the equation of the surface (a torus), in the form $\left(\sqrt{x^2+y^2}-3\right)^2+z^2=1$.", "equation", "(sqrt(x^2+y^2)-3)^2+z^2=1", coordinates=["x", "y", "z"],
                    hints=[r"Replace $x$ by $\sqrt{x^2+y^2}$."], solution=r"Rotating about the $z$-axis replaces $x$ by $\sqrt{x^2+y^2}$ (the distance to the axis): $\left(\sqrt{x^2+y^2}-3\right)^2+z^2=1$."))
    return items


@with_units
def register() -> None:
    plain = [
        (U1, "l01-points-in-space", "more-points", "More practice: points in space.", points_items()),
        (U1, "l02-the-line-in-space", "more-lines", "More practice: the line in space.", line_items()),
        (U1, "l03-the-plane", "more-planes", "More practice: the plane.", plane_items()),
        (U1, "l04-relative-positions-and-angles", "more-angles", "More practice: relative positions and angles.", relative_items()),
        (U1, "l05-distances-and-projections", "more-distances", "More practice: distances.", distance_items()),
        (U3, "l01-equation-of-a-sphere", "more-spheres", "More practice: the equation of a sphere.", sphere_items()),
        (U3, "l02-sphere-plane-line-and-two-spheres", "more-sections", "More practice: tangent planes and sections.", sphere_plane_items()),
        (U4, "l01-the-canonical-quadrics", "more-quadrics", "More practice: quadric surfaces.", quadric_items()),
        (U4, "l02-cylinders-cones-and-surfaces-of-revolution", "more-revolution", "More practice: cylinders, cones and revolution.", surface_items()),
    ]
    for unit, lesson, sid, task, items in plain:
        add_extra(f"{unit}/{lesson}", exset_plain(sid, task, items, format=FMT), SCRIPT)
    for lesson, items in tetra_items().items():
        add_extra(f"{U2}/{lesson}", exset_plain("more-tetrahedron", "More practice: a new tetrahedron.", items, format=FMT), SCRIPT)
    assert math is not None and plane_eng is not None and plane_norm is not None
