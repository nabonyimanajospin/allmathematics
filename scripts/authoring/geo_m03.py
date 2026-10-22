"""Exercises of Course 1, Module 3: geometry of space (points, lines, planes, the tetrahedron, the sphere).

Every answer is computed with SymPy. Each tetrahedron is audited with independent checks: the volume by two methods, the
circumcenter at equal distances from the four vertices, the incenter at distance r from the four face planes, the medians.
"""

from __future__ import annotations

import math

import sympy as sp
from geo_m02 import PAPER_NOTE as _unused  # noqa: F401  (keeps the import order of the two modules explicit)
from geo_m02 import rad
from toolkit import eng, ex, exset_plain as exset, tex, write_exercises, x, y, z, with_units

BASE = "geo/m03-space"
U1 = f"{BASE}/u01-points-lines-planes"
U2 = f"{BASE}/u02-the-tetrahedron"
U3 = f"{BASE}/u03-the-sphere"
R = sp.Rational
PI = sp.pi


# --- vectors in space ------------------------------------------------------------------------------------------
def S3(p):
    return tuple(sp.sympify(v) for v in p)


def sub(p, q):
    p, q = S3(p), S3(q)
    return tuple(rad(q[i] - p[i]) for i in range(3))


def dot(u, v):
    u, v = S3(u), S3(v)
    return rad(sum(u[i] * v[i] for i in range(3)))


def cross(u, v):
    u, v = S3(u), S3(v)
    return (rad(u[1] * v[2] - u[2] * v[1]), rad(u[2] * v[0] - u[0] * v[2]), rad(u[0] * v[1] - u[1] * v[0]))


def norm(u):
    return rad(sp.sqrt(dot(u, u)))


def dist3(p, q):
    return norm(sub(p, q))


def mid3(p, q):
    p, q = S3(p), S3(q)
    return tuple(rad((p[i] + q[i]) / 2) for i in range(3))


def add_scaled(p, t, n):
    p, n = S3(p), S3(n)
    return tuple(rad(p[i] + sp.sympify(t) * n[i]) for i in range(3))


def pt3_tex(p) -> str:
    return rf"\left({tex(p[0])},\,{tex(p[1])},\,{tex(p[2])}\right)"


def pt3_eng(p) -> str:
    return f"({eng(p[0])}, {eng(p[1])}, {eng(p[2])})"


def par(v) -> str:
    v = sp.sympify(v)
    return tex(v) if v.is_nonnegative else rf"\left({tex(v)}\right)"


def plane_norm(a, b, c, d):
    a, b, c, d = (rad(v) for v in (a, b, c, d))
    if all(v.is_Rational for v in (a, b, c, d)):
        den = sp.ilcm(*[sp.fraction(v)[1] for v in (a, b, c, d)])
        a, b, c, d = (v * den for v in (a, b, c, d))
        g = math.gcd(*[int(v) for v in (a, b, c, d)])
        a, b, c, d = (v / g for v in (a, b, c, d))
    lead = next(v for v in (a, b, c) if v != 0)
    if lead.is_negative:
        a, b, c, d = -a, -b, -c, -d
    return a, b, c, d


def plane_point_normal(n, p):
    n, p = S3(n), S3(p)
    return plane_norm(n[0], n[1], n[2], -dot(n, p))


def plane_through(p, q, r):
    return plane_point_normal(cross(sub(p, q), sub(p, r)), p)


def plane_eng(P) -> str:
    return f"{eng(sp.expand(P[0] * x + P[1] * y + P[2] * z + P[3]))}=0"


def plane_tex(P) -> str:
    return f"{tex(sp.expand(P[0] * x + P[1] * y + P[2] * z + P[3]))}=0"


def eval_plane(P, p):
    P, p = S3(P), S3(p)
    return rad(P[0] * p[0] + P[1] * p[1] + P[2] * p[2] + P[3])


def dist_point_plane(p, P) -> sp.Expr:
    return rad(sp.Abs(eval_plane(P, p)) / sp.sqrt(P[0] ** 2 + P[1] ** 2 + P[2] ** 2))


def foot(p, P):
    t = rad(eval_plane(P, p) / (P[0] ** 2 + P[1] ** 2 + P[2] ** 2))
    return t, add_scaled(p, -t, P[:3])


def sphere_eng(c, r2) -> str:
    return f"(x-({eng(c[0])}))^2+(y-({eng(c[1])}))^2+(z-({eng(c[2])}))^2={eng(r2)}"


def vec3_tex(v) -> str:
    return pt3_tex(v)


# --- the tetrahedron ---------------------------------------------------------------------------------------------
class Tet:
    NAMES = "ABCD"

    def __init__(self, A, B, C, D):
        self.V = {n: S3(p) for n, p in zip(self.NAMES, (A, B, C, D), strict=True)}
        a, b, c, d = (self.V[n] for n in self.NAMES)
        self.box = rad(dot(sub(a, b), cross(sub(a, c), sub(a, d))))
        assert self.box != 0, "coplanar vertices"
        self.vol = rad(sp.Abs(self.box) / 6)
        self.edge = {e: dist3(self.V[e[0]], self.V[e[1]]) for e in ("AB", "AC", "AD", "BC", "BD", "CD")}
        self.face = {"BCD": None, "ACD": None, "ABD": None, "ABC": None}
        for f in self.face:
            p, q, r = (self.V[ch] for ch in f)
            self.face[f] = rad(norm(cross(sub(p, q), sub(p, r))) / 2)
        self.opp = {"A": "BCD", "B": "ACD", "C": "ABD", "D": "ABC"}
        self.S = rad(sum(self.face.values()))
        self.G = tuple(rad(sum(self.V[n][i] for n in self.NAMES) / 4) for i in range(3))
        X = sp.symbols("X Y Z", real=True)
        eqs = [sum((X[i] - a[i]) ** 2 for i in range(3)) - sum((X[i] - self.V[n][i]) ** 2 for i in range(3)) for n in "BCD"]
        sol = sp.solve(eqs, X, dict=True)[0]
        self.O = tuple(rad(sol[X[i]]) for i in range(3))
        self.Rc = dist3(self.O, a)
        self.r = rad(3 * self.vol / self.S)
        self.I = tuple(rad(sum(self.face[self.opp[n]] * self.V[n][i] for n in self.NAMES) / self.S) for i in range(3))
        self.audit()

    def height(self, v) -> sp.Expr:
        return rad(3 * self.vol / self.face[self.opp[v]])

    def face_plane(self, f):
        p, q, r = (self.V[ch] for ch in f)
        return plane_through(p, q, r)

    def dihedral_cos(self, e1, e2="CD"):
        """cos of the interior dihedral angle along the edge e1[0]e1[1] between the faces with the third vertices given."""
        raise NotImplementedError

    def dihedral(self, edge: str, c: str, d: str) -> sp.Expr:
        p, q = self.V[edge[0]], self.V[edge[1]]
        n1 = cross(sub(p, q), sub(p, self.V[c]))
        n2 = cross(sub(p, q), sub(p, self.V[d]))
        return rad(dot(n1, n2) / (norm(n1) * norm(n2)))

    def audit(self) -> None:
        def num(e):
            return float(sp.N(e, 30))

        eps = 1e-9
        for v in self.NAMES:
            h = self.height(v)
            P = self.face_plane(self.opp[v])
            assert abs(num(dist_point_plane(self.V[v], P)) - num(h)) < eps
        for v in self.NAMES:
            assert abs(num(dist3(self.O, self.V[v])) - num(self.Rc)) < eps
        for f in self.face:
            assert abs(num(dist_point_plane(self.I, self.face_plane(f))) - num(self.r)) < eps
        # the medians divide 3:1
        for v in self.NAMES:
            others = [self.V[n] for n in self.NAMES if n != v]
            ga = tuple(rad(sum(o[i] for o in others) / 3) for i in range(3))
            assert all(abs(num(self.G[i] - (self.V[v][i] + 3 * ga[i]) / 4)) < eps for i in range(3))
        # the interior dihedral angle: sin formula
        a_len = self.edge["AB"]
        sin = rad(3 * self.vol * a_len / (2 * self.face["ABC"] * self.face["ABD"]))
        assert abs(num(sin**2 + self.dihedral("AB", "C", "D") ** 2) - 1) < 1e-9


def tet_tex(T: Tet) -> str:
    return ", ".join(rf"${n}{pt3_tex(T.V[n])}$" for n in Tet.NAMES)


TA = Tet((0, 0, 0), (4, 0, 0), (1, 3, 0), (2, 1, 5))  # the running example
TB = Tet((0, 0, 0), (2, 0, 0), (0, 4, 0), (0, 0, 6))  # corner tetrahedron, rational insphere
TC = Tet((2, -1, 1), (5, 5, 4), (3, 2, -1), (4, 1, 3))
TD = Tet((0, 0, 0), (2, 2, 0), (2, 0, 2), (0, 2, 2))  # regular, edge 2*sqrt(2)


def item_num(id, statement, value, solution, hints, answer_type="expression", **kw):
    return ex(id, statement, answer_type, eng(value), solution=solution, hints=hints, **kw)


def item_pt(id, statement, p, solution, hints, **kw):
    return ex(id, statement, "vector", pt3_eng(p), solution=solution, hints=hints, **kw)


def item_plane(id, statement, P, solution, hints, **kw):
    return ex(id, statement, "equation", plane_eng(P), coordinates=["x", "y", "z"], solution=solution, hints=hints, **kw)


# ============================ UNIT 1 =================================================================================
def u1l1() -> list[dict]:
    items = []
    for n, (P, Q) in enumerate((((1, 2, 3), (4, 6, 15)), ((-1, 2, 0), (3, -2, 2)), ((2, -3, 5), (-4, 1, 8)), ((0, 0, 0), (1, 1, 1))), 1):
        d = dist3(P, Q)
        v = sub(P, Q)
        items.append(item_num(f"ps-{n:02d}", rf"The distance between $A{pt3_tex(P)}$ and $B{pt3_tex(Q)}$.", d,
                              rf"$\overrightarrow{{AB}}={vec3_tex(v)}$, so $AB=\sqrt{{{tex(v[0]**2)}+{tex(v[1]**2)}+{tex(v[2]**2)}}}={tex(d)}$.",
                              ["Subtract the coordinates and use Pythagoras with three terms."]))
    P, Q = (3, 4, 12), (0, 0, 0)
    items.append(ex("ps-05", r"The direction cosines $(\cos\alpha,\cos\beta,\cos\gamma)$ of the vector $\overrightarrow{OA}$ with $A(3,4,12)$.", "vector",
                    "(3/13, 4/13, 12/13)", hints=["Divide the components by the length $13$."],
                    solution=r"$OA=\sqrt{9+16+144}=13$, so the direction cosines are $\dfrac3{13},\dfrac4{13},\dfrac{12}{13}$."))
    for n, (P, Q) in enumerate((((2, -4, 6), (-2, 0, 2)), ((1, 1, 1), (4, 7, -2))), 6):
        M = mid3(P, Q)
        items.append(item_pt(f"ps-{n:02d}", rf"The midpoint of the segment $A{pt3_tex(P)}$, $B{pt3_tex(Q)}$.", M,
                             rf"The midpoint is $\dfrac{{A+B}}{{2}}={pt3_tex(M)}$.", ["Average the coordinates."]))

    def divide(n, A, B, m, k, external):
        kk = R(-m, k) if external else R(m, k)
        Pp = tuple(rad((A[i] + kk * B[i]) / (1 + kk)) for i in range(3))
        kind = "outside the segment" if external else "on the segment"
        items.append(item_pt(f"ps-{n:02d}", rf"The point $P$ of the line $AB$, {kind}, with $AP:PB={m}:{k}$, for $A{pt3_tex(A)}$ and $B{pt3_tex(B)}$.", Pp,
                             rf"$k={tex(kk)}$, so $P=\dfrac{{A+kB}}{{1+k}}={pt3_tex(Pp)}$.", ["$P=\\dfrac{A+kB}{1+k}$ with $k=\\pm\\dfrac mn$."]))

    divide(8, (1, 2, 3), (4, 6, 15), 2, 1, False)
    divide(9, (0, 0, 0), (8, 4, -12), 1, 3, False)
    divide(10, (1, 0, 2), (3, 4, 6), 3, 2, True)
    M = (2, 3, -1)
    A = (5, 3, 3)
    B = tuple(2 * M[i] - A[i] for i in range(3))
    items.append(item_pt("ps-11", rf"$M{pt3_tex(M)}$ is the midpoint of $AB$ and $A{pt3_tex(A)}$. Find $B$.", B,
                         rf"$B=2M-A={pt3_tex(B)}$.", ["Solve $M=\\dfrac{A+B}{2}$ for $B$."]))
    return items


def u1l2() -> list[dict]:
    items = []
    n = 0

    def direction(P, Q):
        nonlocal n
        n += 1
        d = sub(P, Q)
        items.append(ex(f"ln-{n:02d}", rf"A direction vector of the line through $A{pt3_tex(P)}$ and $B{pt3_tex(Q)}$.", "direction", pt3_eng(d),
                        hints=["Use $\\overrightarrow{AB}$."], solution=rf"$\overrightarrow{{AB}}={vec3_tex(d)}$, and every non-zero multiple of it is also a direction vector."))

    direction((1, 2, 3), (4, 6, 15))
    direction((-1, 0, 2), (3, 2, -2))

    def from_planes(p1, p2):
        nonlocal n
        n += 1
        d = cross(p1[:3], p2[:3])
        items.append(ex(f"ln-{n:02d}", rf"A direction vector of the line ${plane_tex(p1)}$, ${plane_tex(p2)}$ (two planes).", "direction", pt3_eng(d),
                        hints=["The direction is the cross product of the normal vectors."],
                        solution=rf"The normals are ${vec3_tex(p1[:3])}$ and ${vec3_tex(p2[:3])}$, and their cross product is ${vec3_tex(d)}$."))

    from_planes((1, 1, 1, -3), (1, -1, 2, 0))
    from_planes((2, -1, 0, 4), (0, 1, 3, -6))
    for P0, d, lam in (((1, -2, 4), (3, 1, -2), -2), ((0, 5, -1), (2, -1, 4), 3)):
        n += 1
        Pt = add_scaled(P0, lam, d)
        items.append(item_pt(f"ln-{n:02d}", rf"The point of the line $\overrightarrow{{OP}}={pt3_tex(P0)}+\lambda{pt3_tex(d)}$ for $\lambda={lam}$.", Pt,
                             rf"Substitute $\lambda={lam}$: ${pt3_tex(Pt)}$.", ["Substitute the value of $\\lambda$ in each coordinate."]))
    # point on a line? parameter value
    n += 1
    items.append(ex(f"ln-{n:02d}", r"For which value of $\lambda$ does the line $\begin{cases}x=1+2\lambda\\ y=-3+\lambda\\ z=4-3\lambda\end{cases}$ pass through $(7,0,-5)$?", "number", "3",
                    hints=["Solve the first equation for $\\lambda$ and check the others."],
                    solution=r"$1+2\lambda=7$ gives $\lambda=3$; then $y=-3+3=0$ and $z=4-9=-5$: the point is on the line."))
    n += 1
    items.append(ex(f"ln-{n:02d}", r"Is the point $(3,1,1)$ on the line through $A(1,0,2)$ and $B(5,2,0)$? Answer $1$ for yes, $0$ for no.", "number", "1",
                    hints=["Find $\\lambda$ from the first coordinate."],
                    solution=r"$\overrightarrow{AB}=(4,2,-2)$ and $\overrightarrow{AP}=(2,1,-1)=\dfrac12\overrightarrow{AB}$: the point is on the line (for $\lambda=\dfrac12$)."))
    return items


def u1l3() -> list[dict]:
    items = []
    n = 0
    for P, Q, Rr in (((1, 0, 2), (3, 1, 0), (2, 2, 3)), ((1, 0, 0), (0, 2, 0), (0, 0, 3)), ((0, 1, 1), (2, 3, 0), (1, 0, 4))):
        n += 1
        L = plane_through(P, Q, Rr)
        nv = cross(sub(P, Q), sub(P, Rr))
        items.append(item_plane(f"pl-{n:02d}", rf"The plane through $A{pt3_tex(P)}$, $B{pt3_tex(Q)}$, $C{pt3_tex(Rr)}$.", L,
                                rf"$\overrightarrow{{AB}}={vec3_tex(sub(P,Q))}$ and $\overrightarrow{{AC}}={vec3_tex(sub(P,Rr))}$; the cross product is ${vec3_tex(nv)}$. The plane is ${plane_tex(L)}$.",
                                ["The normal vector is the cross product of $\\overrightarrow{AB}$ and $\\overrightarrow{AC}$."]))
    for nvec, P in (((2, -1, 3), (1, 1, 1)), ((1, 0, -2), (4, 5, 6))):
        n += 1
        L = plane_point_normal(nvec, P)
        items.append(item_plane(f"pl-{n:02d}", rf"The plane through $A{pt3_tex(P)}$ with normal vector ${vec3_tex(nvec)}$.", L,
                                rf"${vec3_tex(nvec)}\cdot(x-{par(P[0])},y-{par(P[1])},z-{par(P[2])})=0$, that is ${plane_tex(L)}$.",
                                ["Use $a(x-x_0)+b(y-y_0)+c(z-z_0)=0$."]))
    n += 1
    L0 = (2, -3, 6, 5)
    Pp = (1, 2, -1)
    L = plane_point_normal(L0[:3], Pp)
    items.append(item_plane(f"pl-{n:02d}", rf"The plane through $P{pt3_tex(Pp)}$ parallel to ${plane_tex(L0)}$.", L,
                            rf"A parallel plane keeps the normal ${vec3_tex(L0[:3])}$: ${plane_tex(L)}$.", ["Keep the normal vector."]))
    n += 1
    items.append(ex(f"pl-{n:02d}", r"The points where the plane $3x+2y+z-6=0$ meets the three axes.", "points", "(2, 0, 0), (0, 3, 0), (0, 0, 6)",
                    hints=["Put two coordinates equal to $0$ each time."], solution=r"$y=z=0$: $x=2$; $x=z=0$: $y=3$; $x=y=0$: $z=6$."))
    n += 1
    P = (2, -2, 1, -9)
    p = rad(9 / norm(P[:3]))
    items.append(item_num(f"pl-{n:02d}", rf"The distance $p$ from the origin to the plane ${plane_tex(P)}$.", p,
                          rf"The normal has length ${tex(norm(P[:3]))}$, so $p=\dfrac{{|d|}}{{{tex(norm(P[:3]))}}}={tex(p)}$.", ["$p=\\dfrac{|d|}{\\sqrt{a^2+b^2+c^2}}$."]))
    return items


def u1l4() -> list[dict]:
    items = []
    n = 0

    def position(A, u, B, v, label):
        nonlocal n
        n += 1
        c = cross(u, v)
        box = dot(sub(A, B), c)
        if c == (0, 0, 0):
            code = 2
            why = r"the directions are collinear, so the lines are parallel (code $2$)."
        elif box == 0:
            code = 1
            why = rf"the box product is $0$ and the directions are not collinear: the lines intersect (code $1$)."
        else:
            code = 3
            why = rf"the box product is ${tex(box)}\neq0$: the lines are skew (code $3$)."
        items.append(ex(f"rp-{n:02d}", rf"The line through $A{pt3_tex(A)}$ with direction ${vec3_tex(u)}$ and the line through $B{pt3_tex(B)}$ with direction ${vec3_tex(v)}$. "
                                      r"Answer $1$ if they intersect, $2$ if they are parallel (or equal), $3$ if they are skew.", "number", str(code),
                        hints=["Compute the cross product of the directions, then the box product with $\\overrightarrow{AB}$."],
                        solution=rf"The cross product of the directions is ${vec3_tex(c)}$ and $\boxp{{\overrightarrow{{AB}}}}{{\vec u}}{{\vec v}}={tex(box)}$: {why}"))

    position((0, 0, 0), (1, 1, 0), (2, 0, 0), (-1, 1, 0), "a")
    position((0, 0, 0), (1, 1, 0), (0, 0, 1), (1, -1, 0), "b")
    position((1, 2, 3), (2, 4, 6), (0, 0, 1), (1, 2, 3), "c")
    position((1, 0, 1), (1, 2, -1), (0, 3, 2), (3, 1, 0), "d")

    def angle_lines(u, v):
        nonlocal n
        n += 1
        c = rad(sp.Abs(dot(u, v)) / (norm(u) * norm(v)))
        items.append(item_num(f"rp-{n:02d}", rf"$\cos\theta$ for the angle between the lines of directions ${vec3_tex(u)}$ and ${vec3_tex(v)}$.", c,
                              rf"$\dotp{{\vec u}}{{\vec v}}={tex(dot(u,v))}$, $\norm{{\vec u}}={tex(norm(u))}$, $\norm{{\vec v}}={tex(norm(v))}$, so $\cos\theta={tex(c)}$.",
                              ["Use the absolute value of the dot product."]))

    angle_lines((1, 2, 2), (2, -1, 2))
    angle_lines((1, 1, 0), (0, 1, 1))
    n += 1
    d, nv = (1, 2, 2), (0, 0, 1)
    s = rad(sp.Abs(dot(d, nv)) / (norm(d) * norm(nv)))
    items.append(item_num(f"rp-{n:02d}", r"$\sin\varphi$ for the angle $\varphi$ between the line of direction $(1,2,2)$ and the plane $z=0$.", s,
                          rf"$\sin\varphi=\dfrac{{|\dotp{{\vec d}}{{\vec n}}|}}{{\norm{{\vec d}}\norm{{\vec n}}}}={tex(s)}$.", ["Use the normal vector $(0,0,1)$."]))
    n += 1
    n1, n2 = (1, 1, 1), (1, -1, 0)
    c = rad(sp.Abs(dot(n1, n2)) / (norm(n1) * norm(n2)))
    items.append(item_num(f"rp-{n:02d}", r"$\cos\psi$ for the angle between the planes $x+y+z=1$ and $x-y=0$.", c,
                          r"The normals are $(1,1,1)$ and $(1,-1,0)$, and their dot product is $0$, so $\cos\psi=0$: the planes are perpendicular.", ["Use the normal vectors."]))
    # intersection of line and plane
    n += 1
    P0, d = (1, 2, 3), (1, -1, 2)
    Pl = (2, 1, -1, 1)
    lam = rad(-eval_plane(Pl, P0) / dot(Pl[:3], d))
    Pt = add_scaled(P0, lam, d)
    items.append(item_pt(f"rp-{n:02d}", rf"The point where the line $\overrightarrow{{OP}}={pt3_tex(P0)}+\lambda{pt3_tex(d)}$ meets the plane ${plane_tex(Pl)}$.", Pt,
                         rf"Substitute the line in the plane: ${tex(eval_plane(Pl, P0))}+\lambda\cdot{tex(dot(Pl[:3], d))}=0$ gives $\lambda={tex(lam)}$, and the point is ${pt3_tex(Pt)}$.",
                         ["Replace $x,y,z$ in the equation of the plane by the parametric equations."]))
    return items


def u1l5() -> list[dict]:
    items = []
    n = 0

    def point_plane(P, Pl):
        nonlocal n
        n += 1
        d = dist_point_plane(P, Pl)
        items.append(item_num(f"dt-{n:02d}", rf"The distance from $P{pt3_tex(P)}$ to the plane ${plane_tex(Pl)}$.", d,
                              rf"The numerator is $|{tex(eval_plane(Pl,P))}|$ and the length of the normal is ${tex(norm(Pl[:3]))}$, so $d={tex(d)}$.",
                              ["$d=\\dfrac{|ax_0+by_0+cz_0+d|}{\\sqrt{a^2+b^2+c^2}}$."]))

    point_plane((1, 2, 3), (2, -1, 2, -1))
    point_plane((2, 1, -1), (1, 2, -2, -3))
    point_plane((0, 0, 0), (3, 4, 12, -26))
    point_plane((4, -1, 2), (1, 1, 1, 2))
    for P, Pl in (((1, 2, 3), (2, -1, 2, -1)), ((3, 0, -2), (1, 2, 2, -5))):
        n += 1
        t, H = foot(P, Pl)
        items.append(item_pt(f"dt-{n:02d}", rf"The foot of the perpendicular from $P{pt3_tex(P)}$ to the plane ${plane_tex(Pl)}$.", H,
                             rf"$t={tex(t)}$, so $H=P-t\,(a,b,c)={pt3_tex(H)}$.", ["$H=P-t\\,(a,b,c)$ with $t=\\dfrac{ax_0+by_0+cz_0+d}{a^2+b^2+c^2}$."]))
        n += 1
        Pp = add_scaled(P, -2 * t, Pl[:3])
        items.append(item_pt(f"dt-{n:02d}", rf"The point symmetric to $P{pt3_tex(P)}$ with respect to the plane ${plane_tex(Pl)}$.", Pp,
                             rf"$P'=P-2t\,(a,b,c)={pt3_tex(Pp)}$ with $t={tex(t)}$.", ["Go twice as far as the foot."]))
    n += 1
    A, d, P = (0, 0, 0), (1, 2, 2), (1, 2, 3)
    c = cross(sub(A, P), d)
    dd = rad(norm(c) / norm(d))
    items.append(item_num(f"dt-{n:02d}", rf"The distance from $P{pt3_tex(P)}$ to the line through the origin with direction ${vec3_tex(d)}$.", dd,
                          rf"The cross product of $\overrightarrow{{AP}}$ and $\vec d$ is ${vec3_tex(c)}$, with norm ${tex(norm(c))}$; $\norm{{\vec d}}={tex(norm(d))}$, so $\delta={tex(dd)}$.",
                          ["$\\delta=\\dfrac{\\norm{\\crossp{\\overrightarrow{AP}}{\\vec d}}}{\\norm{\\vec d}}$, with the cross product."]))
    for A, u, B, v in (((0, 0, 0), (1, 1, 0), (0, 0, 1), (1, -1, 0)), ((0, 0, 0), (1, 0, 0), (0, 0, 5), (0, 1, 0)), ((1, 0, 0), (0, 1, 1), (0, 2, 1), (1, 0, 2))):
        n += 1
        c = cross(u, v)
        box = dot(sub(A, B), c)
        dd = rad(sp.Abs(box) / norm(c))
        items.append(item_num(f"dt-{n:02d}", rf"The distance between the skew lines through $A{pt3_tex(A)}$ (direction ${vec3_tex(u)}$) and $B{pt3_tex(B)}$ (direction ${vec3_tex(v)}$).", dd,
                              rf"The box product is ${tex(box)}$ and the cross product of the directions is ${vec3_tex(c)}$, with norm ${tex(norm(c))}$, so $\delta={tex(dd)}$.",
                              ["$\\delta=\\dfrac{|\\boxp{\\overrightarrow{AB}}{\\vec u}{\\vec v}|}{\\norm{\\crossp{\\vec u}{\\vec v}}}$."]))
    n += 1
    P1, P2 = (2, -1, 2, 3), (2, -1, 2, -6)
    dd = rad(sp.Abs(P1[3] - P2[3]) / norm(P1[:3]))
    items.append(item_num(f"dt-{n:02d}", rf"The distance between the parallel planes ${plane_tex(P1)}$ and ${plane_tex(P2)}$.", dd,
                          rf"$d=\dfrac{{|c_1-c_2|}}{{{tex(norm(P1[:3]))}}}={tex(dd)}$.", ["The coefficients of $x,y,z$ are already equal."]))
    return items


# ============================ UNIT 2: the tetrahedron ===============================================================
def tin(T: Tet) -> str:
    return f"For the tetrahedron {tet_tex(T)}: "


def u2l1() -> list[dict]:
    items = []
    for i, T in enumerate((TA, TC, TB), 1):
        for e in ("AB", "CD"):
            items.append(item_num(f"te-e{e.lower()}{i}", tin(T) + rf"find the edge ${e}$.", T.edge[e],
                                  rf"$\overrightarrow{{{e}}}={vec3_tex(sub(T.V[e[0]], T.V[e[1]]))}$, so ${e}={tex(T.edge[e])}$.", ["The norm of the vector between the two vertices."]))
        for f in ("ABC", "BCD"):
            p, q, r = (T.V[c] for c in f)
            cr = cross(sub(p, q), sub(p, r))
            items.append(item_num(f"te-s{f.lower()}{i}", tin(T) + rf"find the area of the face ${f}$.", T.face[f],
                                  rf"The cross product of two edges is ${vec3_tex(cr)}$, with norm ${tex(norm(cr))}$; the area is half of it: ${tex(T.face[f])}$.", ["Half the norm of a cross product."]))
        p, q, r = T.V["A"], T.V["B"], T.V["C"]
        cosa = rad(dot(sub(p, q), sub(p, r)) / (norm(sub(p, q)) * norm(sub(p, r))))
        items.append(item_num(f"te-c{i}", tin(T) + r"find $\cos\hat A$ in the face $ABC$.", cosa,
                              rf"$\dotp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}={tex(dot(sub(p,q),sub(p,r)))}$ and the product of the norms is ${tex(rad(norm(sub(p,q))*norm(sub(p,r))))}$, so $\cos\hat A={tex(cosa)}$.",
                              ["The angle between $\\overrightarrow{AB}$ and $\\overrightarrow{AC}$."]))
    items.append(item_num("te-p1", tin(TA) + "find the perimeter of the face $ABC$.", rad(TA.edge["AB"] + TA.edge["AC"] + TA.edge["BC"]),
                          rf"$AB+AC+BC={tex(TA.edge['AB'])}+{tex(TA.edge['AC'])}+{tex(TA.edge['BC'])}$.", ["Add the three edges of the face."]))
    items.append(item_num("te-t1", tin(TB) + "find the total surface area.", TB.S,
                          rf"The faces have the areas ${tex(TB.face['ABC'])}$, ${tex(TB.face['ABD'])}$, ${tex(TB.face['ACD'])}$, ${tex(TB.face['BCD'])}$; their sum is ${tex(TB.S)}$.", ["Add the four face areas."]))
    return items


def u2l2() -> list[dict]:
    items = []
    for i, T in enumerate((TA, TC, TB), 1):
        a, b, c, d = (T.V[k] for k in "ABCD")
        items.append(item_num(f"tv-v{i}", tin(T) + "find the volume.", T.vol,
                              rf"The box product of $\overrightarrow{{AB}}$, $\overrightarrow{{AC}}$, $\overrightarrow{{AD}}$ is ${tex(T.box)}$, so $V=\dfrac{{|{tex(T.box)}|}}{{6}}={tex(T.vol)}$.", ["$V=\\dfrac16|\\boxp{\\overrightarrow{AB}}{\\overrightarrow{AC}}{\\overrightarrow{AD}}|$."]))
        items.append(item_num(f"tv-h{i}", tin(T) + "find the height from $D$.", T.height("D"),
                              rf"$h_D=\dfrac{{3V}}{{S_{{ABC}}}}=\dfrac{{3\cdot{tex(T.vol)}}}{{{tex(T.face['ABC'])}}}={tex(T.height('D'))}$.", ["$h_D=\\dfrac{3V}{S_{ABC}}$."]))
        P = T.face_plane("ABC")
        items.append(item_plane(f"tv-p{i}", tin(T) + "find the equation of the plane of the face $ABC$.", P,
                                rf"The normal is the cross product of $\overrightarrow{{AB}}$ and $\overrightarrow{{AC}}$; the plane is ${plane_tex(P)}$.", ["Plane through three points."]))
        cosd = T.dihedral("AB", "C", "D")
        items.append(item_num(f"tv-d{i}", tin(T) + r"find $\cos\varphi$, where $\varphi$ is the dihedral angle along $AB$ between the faces $ABC$ and $ABD$.", cosd,
                              rf"The normals are the cross products of $\overrightarrow{{AB}}$ with $\overrightarrow{{AC}}$ and $\overrightarrow{{AD}}$; $\cos\varphi={tex(cosd)}$.", ["Use the two normals."]))
    items.append(item_num("tv-x1", r"A tetrahedron has volume $V=15$ and the face $ABC$ has area $9$. Find the height from $D$.", R(5),
                          r"$h_D=\dfrac{3V}{S_{ABC}}=\dfrac{45}{9}=5$.", ["$h=\\dfrac{3V}{S}$."], answer_type="number"))
    return items


def u2l3() -> list[dict]:
    items = []
    for i, T in enumerate((TA, TC, TB), 1):
        items.append(item_pt(f"tc-g{i}", tin(T) + "find the centroid $G$.", T.G,
                             rf"$G=\dfrac{{A+B+C+D}}{{4}}={pt3_tex(T.G)}$.", ["Average the four vertices."]))
        ga = tuple(rad(sum(T.V[n][k] for n in "BCD") / 3) for k in range(3))
        items.append(item_num(f"tc-m{i}", tin(T) + "find the length of the median from $A$ (to the centroid of $BCD$).", dist3(T.V["A"], ga),
                              rf"The centroid of $BCD$ is ${pt3_tex(ga)}$, and the distance from $A$ to it is ${tex(dist3(T.V['A'], ga))}$.", ["The median ends at the centroid of the opposite face."]))
    items.append(item_pt("tc-o1", tin(TA) + "find the center of the circumsphere.", TA.O,
                         rf"The center is equidistant from the four vertices; solving gives ${pt3_tex(TA.O)}$.", ["Solve $2\\dotp{\\overrightarrow{AX}}{\\overrightarrow{AO}}=AX^2$ for $X=B,C,D$."]))
    items.append(item_num("tc-r1", tin(TA) + "find the radius of the circumsphere.", TA.Rc, rf"$R=OA={tex(TA.Rc)}$.", ["$R=OA$."]))
    items.append(ex("tc-s1", tin(TA) + "write the equation of the circumsphere.", "equation", sphere_eng(TA.O, rad(TA.Rc**2)), coordinates=["x", "y", "z"],
                    hints=["Center $O$ and radius $R$."],
                    solution=rf"$(x-{par(TA.O[0])})^2+(y-{par(TA.O[1])})^2+(z-{par(TA.O[2])})^2={tex(rad(TA.Rc**2))}$."))
    items.append(item_pt("tc-o2", tin(TC) + "find the center of the circumsphere.", TC.O, rf"The center is ${pt3_tex(TC.O)}$.", ["Solve three linear equations."]))
    items.append(item_num("tc-r2", tin(TB) + "find the radius $r$ of the insphere.", TB.r,
                          rf"$V={tex(TB.vol)}$ and $S={tex(TB.S)}$, so $r=\dfrac{{3V}}{{S}}={tex(TB.r)}$.", ["$r=\\dfrac{3V}{S}$."]))
    items.append(item_pt("tc-i1", tin(TB) + "find the center of the insphere.", TB.I,
                         rf"$I=\dfrac{{S_AA+S_BB+S_CC+S_DD}}{{S}}={pt3_tex(TB.I)}$.", ["Weight each vertex by the area of the opposite face."]))
    return items


def u2l4() -> list[dict]:
    items = []
    for n, a in enumerate((2, 6, 3, 12), 1):
        a = sp.Integer(a)
        items.append(item_num(f"rg-v{n}", rf"The volume of the regular tetrahedron of edge $a={a}$.", rad(sp.sqrt(2) / 12 * a**3),
                              rf"$V=\dfrac{{\sqrt2}}{{12}}a^3={tex(rad(sp.sqrt(2)/12*a**3))}$.", ["$V=\\dfrac{\\sqrt2}{12}a^3$."]))
    for n, a in enumerate((6, 4), 1):
        a = sp.Integer(a)
        items.append(item_num(f"rg-h{n}", rf"The height of the regular tetrahedron of edge $a={a}$.", rad(sp.sqrt(6) / 3 * a),
                              rf"$h=\dfrac{{\sqrt6}}{{3}}a={tex(rad(sp.sqrt(6)/3*a))}$.", ["$h=\\dfrac{\\sqrt6}{3}a$."]))
        items.append(item_num(f"rg-r{n}", rf"The circumradius of the regular tetrahedron of edge $a={a}$.", rad(sp.sqrt(6) / 4 * a),
                              rf"$R=\dfrac{{\sqrt6}}{{4}}a={tex(rad(sp.sqrt(6)/4*a))}$.", ["$R=\\dfrac{\\sqrt6}{4}a$."]))
    items.append(item_num("rg-s1", r"The total surface area of the regular tetrahedron of edge $a=5$.", rad(sp.sqrt(3) * 25),
                          r"$S=\sqrt3\,a^2=25\sqrt3$.", ["Four equilateral triangles of side $a$."]))
    items.append(item_pt("rg-c1", r"The tetrahedron with vertices $(0,0,0)$, $(2,2,0)$, $(2,0,2)$, $(0,2,2)$ is regular. Find its centroid.", TD.G,
                         r"$G=\dfrac{(4,4,4)}{4}=(1,1,1)$.", ["Average the vertices."]))
    items.append(item_num("rg-e1", r"A convex polyhedron has $8$ vertices and $6$ faces. How many edges has it?", R(12),
                          r"$V-E+F=2$ gives $8-E+6=2$, so $E=12$ (the cube).", ["Euler's formula."], answer_type="number"))
    items.append(item_num("rg-e2", r"A convex polyhedron has $20$ vertices and $12$ faces. How many edges has it?", R(30),
                          r"$20-E+12=2$, so $E=30$ (the dodecahedron).", ["Euler's formula."], answer_type="number"))
    return items


# ============================ UNIT 3: the sphere =====================================================================
def u3l1() -> list[dict]:
    items = []
    n = 0
    for (p, q, rr0, rho) in (((1, -2, 3), None, None, 5), ((2, -1, -2), None, None, 2), ((0, 1, 0), None, None, 3)):
        n += 1
        c = p
        D, E, F = -2 * c[0], -2 * c[1], -2 * c[2]
        G = c[0] ** 2 + c[1] ** 2 + c[2] ** 2 - rho**2
        poly = tex(x**2 + y**2 + z**2 + D * x + E * y + F * z + G) + "=0"
        items.append(ex(f"sp-{n:02d}", rf"The center and the radius of the sphere ${poly}$ (center first, then the radius).", "vector",
                        f"({eng(c[0])}, {eng(c[1])}, {eng(c[2])}, {eng(rho)})", hints=["Complete the squares in $x$, $y$ and $z$."],
                        solution=rf"The center is $\left(-\dfrac D2,-\dfrac E2,-\dfrac F2\right)={pt3_tex(c)}$ and $\rho^2=\dfrac{{D^2+E^2+F^2}}{{4}}-G={tex(rho**2)}$, so $\rho={tex(rho)}$."))
    for P, Q in (((1, 2, 3), (5, 6, 7)), ((0, 0, 0), (4, 0, 6))):
        n += 1
        M = mid3(P, Q)
        r2 = rad(dist3(P, Q) ** 2 / 4)
        items.append(ex(f"sp-{n:02d}", rf"The sphere with the segment from $A{pt3_tex(P)}$ to $B{pt3_tex(Q)}$ as a diameter.", "equation", sphere_eng(M, r2),
                        coordinates=["x", "y", "z"], hints=["The center is the midpoint."],
                        solution=rf"The center is ${pt3_tex(M)}$ and $\rho^2=\dfrac{{AB^2}}{{4}}={tex(r2)}$."))
    for pts in (((0, 0, 0), (4, 0, 0), (1, 3, 0), (2, 1, 5)), ((0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2)), ((1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0))):
        n += 1
        Dv, Ev, Fv, Gv = sp.symbols("Dv Ev Fv Gv")
        sol = sp.solve([sum(c**2 for c in P) + Dv * P[0] + Ev * P[1] + Fv * P[2] + Gv for P in pts], [Dv, Ev, Fv, Gv], dict=True)[0]
        D, E, F, G = (sol[k] for k in (Dv, Ev, Fv, Gv))
        key = f"x^2+y^2+z^2+({eng(D)})*x+({eng(E)})*y+({eng(F)})*z+({eng(G)})=0"
        items.append(ex(f"sp-{n:02d}", r"The sphere through the four points " + ", ".join(f"${pt3_tex(P)}$" for P in pts) + ".", "equation", key,
                        coordinates=["x", "y", "z"], hints=["Substitute the four points in $x^2+y^2+z^2+Dx+Ey+Fz+G=0$."],
                        solution=rf"The four linear equations give $D={tex(D)}$, $E={tex(E)}$, $F={tex(F)}$, $G={tex(G)}$: ${tex(x**2+y**2+z**2+D*x+E*y+F*z+G)}=0$."))
    n += 1
    items.append(ex(f"sp-{n:02d}", r"The surface area of the sphere $x^2+y^2+z^2-2x+4y-6z-11=0$.", "expression", "100*pi",
                    hints=["Find the radius first."], solution=r"The radius is $5$, so $S=4\pi\cdot25=100\pi$."))
    n += 1
    items.append(ex(f"sp-{n:02d}", r"The volume of the sphere $x^2+y^2+z^2-6x-8y=0$.", "expression", "500*pi/3",
                    hints=["Find the radius first."], solution=r"$(x-3)^2+(y-4)^2+z^2=25$, so $\rho=5$ and $V=\dfrac43\pi\cdot125=\dfrac{500\pi}3$."))
    return items


def u3l2() -> list[dict]:
    items = []
    n = 0
    for c, rho, Pl in (((0, 0, 0), 5, (2, -2, 1, -9)), ((1, 1, 1), 3, (0, 0, 1, -2)), ((0, 0, 0), 13, (3, 4, 12, -26 * 3))):
        n += 1
        d = dist_point_plane(c, Pl)
        rc = rad(sp.sqrt(rho**2 - d**2))
        items.append(item_num(f"sq-{n:02d}", rf"The radius of the circle in which the plane ${plane_tex(Pl)}$ cuts the sphere of center ${pt3_tex(c)}$ and radius ${rho}$.", rc,
                              rf"The distance from the center to the plane is ${tex(d)}$, so the radius is $\sqrt{{{rho**2}-{tex(d**2)}}}={tex(rc)}$.", ["Pythagoras: $\\sqrt{\\rho^2-\\delta^2}$."]))
        n += 1
        t, H = foot(c, Pl)
        items.append(item_pt(f"sq-{n:02d}", rf"The center of that circle (plane ${plane_tex(Pl)}$, sphere of center ${pt3_tex(c)}$).", H,
                             rf"It is the foot of the perpendicular from the center of the sphere: ${pt3_tex(H)}$.", ["The foot of the perpendicular."]))
    for c, rho, P0 in (((0, 0, 0), 3, (1, 2, 2)), ((1, -2, 3), 7, (3, 1, 9)), ((0, 0, 0), 13, (3, 4, 12))):
        n += 1
        nv = sub(c, P0)
        Pl = plane_point_normal(nv, P0)
        assert dist_point_plane(c, Pl) == rho
        items.append(item_plane(f"sq-{n:02d}", rf"The tangent plane to the sphere of center ${pt3_tex(c)}$ and radius ${rho}$ at $P_0{pt3_tex(P0)}$.", Pl,
                                rf"The radius vector is ${vec3_tex(nv)}$, the normal of the tangent plane: ${plane_tex(Pl)}$.", ["The tangent plane is perpendicular to the radius."]))
    for S1, S2 in (((0, 0, 0, -9), (-4, -6, -12, 9)), ((0, 0, 0, -25), (-12, 0, 0, 11))):
        n += 1
        Pl = plane_norm(S1[0] - S2[0], S1[1] - S2[1], S1[2] - S2[2], S1[3] - S2[3])
        poly1 = tex(x**2 + y**2 + z**2 + S1[0] * x + S1[1] * y + S1[2] * z + S1[3]) + "=0"
        poly2 = tex(x**2 + y**2 + z**2 + S2[0] * x + S2[1] * y + S2[2] * z + S2[3]) + "=0"
        items.append(item_plane(f"sq-{n:02d}", rf"The radical plane of ${poly1}$ and ${poly2}$.", Pl,
                                rf"Subtract the equations: ${plane_tex(Pl)}$.", ["Subtract the two equations."]))
    n += 1
    items.append(ex(f"sq-{n:02d}", r"Two spheres have radii $7$ and $3$ and their centers are $10$ apart. Position: $1$ separate, $2$ externally tangent, $3$ meeting in a circle, $4$ internally tangent.", "number", "2",
                    hints=["Compare $d$ with $\\rho_1+\\rho_2$."], solution=r"$d=10=7+3$: the spheres are externally tangent."))
    return items


@with_units
def build() -> None:
    f = "Type a point as `(x, y, z)`, an equation with `=`, or an exact value."
    write_exercises(f"{U1}/l01-points-in-space", [exset("points", "Points in space.", u1l1(), format=f)], "geo_m03.py")
    write_exercises(f"{U1}/l02-the-line-in-space", [exset("lines", "Lines in space.", u1l2(), format=f)], "geo_m03.py")
    write_exercises(f"{U1}/l03-the-plane", [exset("planes", "Planes.", u1l3(), format=f)], "geo_m03.py")
    write_exercises(f"{U1}/l04-relative-positions-and-angles", [exset("positions", "Relative positions and angles.", u1l4(), format=f)], "geo_m03.py")
    write_exercises(f"{U1}/l05-distances-and-projections", [exset("distances", "Distances and projections.", u1l5(), format=f)], "geo_m03.py")
    write_exercises(f"{U2}/l01-vertices-edges-faces", [exset("faces", "Edges, faces and angles of a tetrahedron.", u2l1(), format=f)], "geo_m03.py")
    write_exercises(f"{U2}/l02-volume-heights-dihedral-angles", [exset("volume", "Volume, heights and dihedral angles.", u2l2(), format=f)], "geo_m03.py")
    write_exercises(f"{U2}/l03-centers-and-spheres", [exset("centers", "Centroid, circumsphere and insphere.", u2l3(), format=f)], "geo_m03.py")
    write_exercises(f"{U2}/l04-regular-tetrahedron-and-platonic-solids", [exset("regular", "The regular tetrahedron and Euler's formula.", u2l4(), format=f)], "geo_m03.py")
    write_exercises(f"{U3}/l01-equation-of-a-sphere", [exset("spheres", "Equations of spheres.", u3l1(), format=f)], "geo_m03.py")
    write_exercises(f"{U3}/l02-sphere-plane-line-and-two-spheres", [exset("sections", "Planes, tangent planes and two spheres.", u3l2(), format=f)], "geo_m03.py")
