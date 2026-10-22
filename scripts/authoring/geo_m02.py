"""Exercises of Course 1, Module 2: geometry of the plane (the line, the triangle, the circle).

Every answer is computed with SymPy from the vertices, and each triangle is audited with an independent numeric check
(distances to the sides, equal distances to the vertices, the Euler relation, the lengths of the medians, altitudes and bisectors
from the coordinates). The solutions are written from the computed intermediate values.
"""

from __future__ import annotations

import math

import sympy as sp
from toolkit import eng, ex, exset_plain as exset, tex, write_exercises, x, y

BASE = "geo/m02-plane"
U1 = f"{BASE}/u01-coordinates-and-lines"
U2 = f"{BASE}/u02-the-triangle"
U3 = f"{BASE}/u03-the-circle"
R = sp.Rational
PI = sp.pi


def S(v) -> sp.Expr:
    return sp.nsimplify(v, rational=False) if isinstance(v, float) else sp.sympify(v)


def rad(e) -> sp.Expr:
    """A simplified exact value (radicals in the numerator)."""
    return sp.simplify(sp.radsimp(sp.simplify(e)))


# --- points, vectors, lines ----------------------------------------------------------------------------------
def pt_tex(p) -> str:
    return rf"\left({tex(p[0])},\,{tex(p[1])}\right)"


def pt_eng(p) -> str:
    return f"({eng(p[0])}, {eng(p[1])})"


def par(v) -> str:
    """A number inside a product: negative numbers get brackets."""
    v = sp.sympify(v)
    return tex(v) if v.is_nonnegative else rf"\left({tex(v)}\right)"


def vec(p, q):
    p, q = tuple(map(sp.sympify, p)), tuple(map(sp.sympify, q))
    return (rad(q[0] - p[0]), rad(q[1] - p[1]))


def dist(p, q) -> sp.Expr:
    p, q = tuple(map(sp.sympify, p)), tuple(map(sp.sympify, q))
    return rad(sp.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2))


def mid(p, q):
    p, q = tuple(map(sp.sympify, p)), tuple(map(sp.sympify, q))
    return (rad((p[0] + q[0]) / 2), rad((p[1] + q[1]) / 2))


def norm_line(a, b, c):
    a, b, c = map(sp.sympify, (a, b, c))
    """Integer coefficients with a positive first non-zero coefficient (when all are rational)."""
    a, b, c = (rad(v) for v in (a, b, c))
    if all(v.is_Rational for v in (a, b, c)):
        den = sp.ilcm(*[sp.fraction(v)[1] for v in (a, b, c)])
        a, b, c = (v * den for v in (a, b, c))
        g = math.gcd(*[int(v) for v in (a, b, c)])
        a, b, c = (v / g for v in (a, b, c))
    lead = a if a != 0 else b
    if lead.is_negative:
        a, b, c = -a, -b, -c
    return a, b, c


def line_normal(n, p):
    n, p = tuple(map(sp.sympify, n)), tuple(map(sp.sympify, p))
    return norm_line(n[0], n[1], -(n[0] * p[0] + n[1] * p[1]))


def line_through(p, q):
    d = vec(p, q)
    return line_normal((d[1], -d[0]), p)


def line_eng(L) -> str:
    return f"{eng(sp.expand(L[0] * x + L[1] * y + L[2]))}=0"


def line_tex(L) -> str:
    return f"{tex(sp.expand(L[0] * x + L[1] * y + L[2]))}=0"


def eval_line(L, p):
    L, p = tuple(map(sp.sympify, L)), tuple(map(sp.sympify, p))
    return rad(L[0] * p[0] + L[1] * p[1] + L[2])


def dist_point_line(p, L) -> sp.Expr:
    p, L = tuple(map(sp.sympify, p)), tuple(map(sp.sympify, L))
    return rad(sp.Abs(eval_line(L, p)) / sp.sqrt(L[0] ** 2 + L[1] ** 2))


def meet(L1, L2):
    L1, L2 = tuple(map(sp.sympify, L1)), tuple(map(sp.sympify, L2))
    D = L1[0] * L2[1] - L2[0] * L1[1]
    assert D != 0
    return (rad((L1[1] * L2[2] - L2[1] * L1[2]) / D), rad((L1[2] * L2[0] - L2[2] * L1[0]) / D))


def explicit_eng(L) -> str:
    return f"y={eng(sp.expand(-L[0] / L[1] * x - L[2] / L[1]))}"


def explicit_tex(L) -> str:
    return rf"y={tex(sp.expand(-L[0] / L[1] * x - L[2] / L[1]))}"


def normal_form(L):
    L = tuple(map(sp.sympify, L))
    """(cos a, sin a, p) of the normal form x cos a + y sin a - p = 0, with p >= 0."""
    a, b, c = L
    eps = -1 if c > 0 else 1
    n = sp.sqrt(a**2 + b**2)
    return rad(eps * a / n), rad(eps * b / n), rad(sp.Abs(c) / n)


# --- the triangle ----------------------------------------------------------------------------------------------
class Tri:
    def __init__(self, A, B, C):
        self.A, self.B, self.C = (tuple(S(v) for v in P) for P in (A, B, C))
        A, B, C = self.A, self.B, self.C
        self.a, self.b, self.c = dist(B, C), dist(C, A), dist(A, B)
        det = (B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1])
        assert det != 0, "collinear vertices"
        self.det, self.Ssigned, self.K = det, det / 2, abs(det) / 2
        self.per = rad(self.a + self.b + self.c)
        self.s = rad(self.per / 2)
        self.G = (rad((A[0] + B[0] + C[0]) / 3), rad((A[1] + B[1] + C[1]) / 3))
        X, Y = sp.symbols("X Y", real=True)
        sol = sp.solve(
            [(X - A[0]) ** 2 + (Y - A[1]) ** 2 - (X - B[0]) ** 2 - (Y - B[1]) ** 2,
             (X - A[0]) ** 2 + (Y - A[1]) ** 2 - (X - C[0]) ** 2 - (Y - C[1]) ** 2], [X, Y], dict=True)[0]
        self.O = (rad(sol[X]), rad(sol[Y]))
        self.H = (rad(A[0] + B[0] + C[0] - 2 * self.O[0]), rad(A[1] + B[1] + C[1] - 2 * self.O[1]))
        self.I = (rad((self.a * A[0] + self.b * B[0] + self.c * C[0]) / self.per),
                  rad((self.a * A[1] + self.b * B[1] + self.c * C[1]) / self.per))
        self.r = rad(self.K / self.s)
        self.Rc = rad(self.a * self.b * self.c / (4 * self.K))
        self.audit()

    # -- vertex helpers: 'A', 'B' or 'C' with the opposite side first -------------------------------------------
    def V(self, v):
        """(vertex, other1, other2, a_side, b_side, c_side) seen from vertex v: a is opposite v."""
        order = {"A": ("A", "B", "C"), "B": ("B", "C", "A"), "C": ("C", "A", "B")}[v]
        P, Q, Rr = (getattr(self, k) for k in order)
        opp = dist(Q, Rr)
        side_q = dist(Rr, P)  # the side opposite Q
        side_r = dist(P, Q)  # the side opposite R
        return P, Q, Rr, opp, side_q, side_r

    def median(self, v):
        P, Q, Rr, *_ = self.V(v)
        M = mid(Q, Rr)
        return M, line_through(P, M), dist(P, M)

    def altitude(self, v):
        P, Q, Rr, opp, *_ = self.V(v)
        L = line_normal(vec(Q, Rr), P)
        Lbase = line_through(Q, Rr)
        return meet(L, Lbase), L, rad(2 * self.K / opp)

    def bisector(self, v):
        P, Q, Rr, opp, bq, cr = self.V(v)
        # unit vectors along the sides PQ (length cr) and PR (length bq)
        w = (rad((Q[0] - P[0]) / cr + (Rr[0] - P[0]) / bq), rad((Q[1] - P[1]) / cr + (Rr[1] - P[1]) / bq))
        L = line_normal((w[1], -w[0]), P)
        D = (rad((bq * Q[0] + cr * Rr[0]) / (bq + cr)), rad((bq * Q[1] + cr * Rr[1]) / (bq + cr)))
        length = rad(sp.sqrt(bq * cr * ((bq + cr) ** 2 - opp**2)) / (bq + cr))
        return D, L, length

    def perp_bisector(self, v):
        """Perpendicular bisector of the side opposite v, and its length inside the triangle."""
        P, Q, Rr, opp, bq, cr = self.V(v)
        M = mid(Q, Rr)
        L = line_normal(vec(Q, Rr), M)
        nq, nr = {"A": ("B", "C"), "B": ("C", "A"), "C": ("A", "B")}[v]
        angQ, angR = self.angle_cos(nq), self.angle_cos(nr)
        if bq > cr:  # b > c: leaves through the side PR, length (a/2) tan R
            length = rad(opp / 2 * sp.sqrt(1 - angR**2) / angR)
        elif cr > bq:
            length = rad(opp / 2 * sp.sqrt(1 - angQ**2) / angQ)
        else:
            length = rad(2 * self.K / opp)
        return M, L, length

    def angle_cos(self, v):
        P, Q, Rr, opp, bq, cr = self.V(v)
        return rad((bq**2 + cr**2 - opp**2) / (2 * bq * cr))

    def excenter(self, v):
        P, Q, Rr, opp, bq, cr = self.V(v)
        den = -opp + bq + cr
        ctr = (rad((-opp * P[0] + bq * Q[0] + cr * Rr[0]) / den), rad((-opp * P[1] + bq * Q[1] + cr * Rr[1]) / den))
        return ctr, rad(self.K / (self.s - opp))

    def audit(self) -> None:
        A, B, C = self.A, self.B, self.C
        eps = 1e-9

        def num(e):
            return float(sp.N(e, 30))

        # circumcenter: equal distances to the vertices, and R
        for P in (A, B, C):
            assert abs(num(dist(self.O, P)) - num(self.Rc)) < eps
        # incenter: equal distances r to the three sides
        for P, Q in ((A, B), (B, C), (C, A)):
            assert abs(num(dist_point_line(self.I, line_through(P, Q))) - num(self.r)) < eps
        # orthocenter: on two altitudes; Euler relation HG = 2 GO
        for v in "ABC":
            _, L, _ = self.altitude(v)
            assert abs(num(eval_line(L, self.H))) < eps
        for i in (0, 1):
            assert abs(num(self.H[i] - self.G[i]) - 2 * num(self.G[i] - self.O[i])) < eps
        # medians, altitudes, bisectors: formulas against the coordinates
        for v in "ABC":
            P, Q, Rr, opp, bq, cr = self.V(v)
            M, Lm, lm = self.median(v)
            assert abs(num(lm) - num(sp.sqrt(2 * bq**2 + 2 * cr**2 - opp**2) / 2)) < eps
            assert abs(num(eval_line(Lm, self.G))) < eps
            F, La, ha = self.altitude(v)
            assert abs(num(dist(P, F)) - num(ha)) < eps
            D, Lb, lb = self.bisector(v)
            assert abs(num(dist(P, D)) - num(lb)) < eps
            assert abs(num(eval_line(Lb, self.I))) < eps
            M2, Lp, lp = self.perp_bisector(v)
            assert abs(num(eval_line(Lp, self.O))) < eps
            # the length inside the triangle: the bisector leaves through one of the two other sides
            exits = []
            for P2, Q2 in ((P, Q), (P, Rr)):
                side = line_through(P2, Q2)
                if side[0] * Lp[1] - Lp[0] * side[1] == 0:
                    continue
                e = meet(Lp, side)
                inside = all(min(num(P2[i]), num(Q2[i])) - eps <= num(e[i]) <= max(num(P2[i]), num(Q2[i])) + eps for i in (0, 1))
                if inside:
                    exits.append(num(dist(M2, e)))
            assert exits and all(abs(num(lp) - d) < 1e-7 for d in exits), (v, num(lp), exits)
        assert abs(num(self.K) - num(self.r * self.s)) < eps
        # incircle really touches, circumcircle really passes
        assert abs(num(self.K) - num(sp.sqrt(self.s * (self.s - self.a) * (self.s - self.b) * (self.s - self.c)))) < 1e-7


def P_expr(text: str) -> sp.Expr:
    return sp.sympify(text.replace("^", "**"))


def tri_tex(T: Tri) -> str:
    return rf"$A{pt_tex(T.A)}$, $B{pt_tex(T.B)}$, $C{pt_tex(T.C)}$"


TP = Tri((-3, 2), (1, 5), (5, -7))  # the triangle of the past paper
T1 = Tri((1, 2), (15, 2), (6, 14))  # sides 13, 14, 15
T2 = Tri((0, 0), (8, 0), (0, 6))  # right triangle 6, 8, 10
T3 = Tri((-1, 0), (5, 0), (2, 4))  # isosceles 5, 5, 6
T4 = Tri((-2, -1), (10, -1), (-2, 15))  # right triangle 12, 16, 20


# --- common item shapes -------------------------------------------------------------------------------------------
def num_item(id, statement, value, solution, hints, answer_type="expression", **kw):
    return ex(id, statement, answer_type, eng(value), solution=solution, hints=hints, **kw)


def pt_item(id, statement, p, solution, hints, **kw):
    return ex(id, statement, "vector", pt_eng(p), solution=solution, hints=hints, **kw)


def line_item(id, statement, L, solution, hints, **kw):
    return ex(id, statement, "equation", line_eng(L), coordinates=["x", "y"], solution=solution, hints=hints, **kw)


NXT = {"A": "B", "B": "C", "C": "A"}
PRV = {"A": "C", "B": "A", "C": "B"}


def poly_tex(D, E, F) -> str:
    return tex(x**2 + y**2 + D * x + E * y + F) + "=0"


def vec_tex(v) -> str:
    return rf"\left({tex(v[0])},\,{tex(v[1])}\right)"


PAPER_NOTE = (
    "This is the triangle of the past paper (vertices $A(-3,2)$, $B(1,5)$, $C(5,-7)$). The printed question gives $C$ with the signs "
    "mixed up; the worked solution on the paper uses $C(5,-7)$."
)


# ============================ UNIT 1: coordinates and the straight line =============================================
def u1l1() -> list[dict]:
    items: list[dict] = []

    def distance(n, P, Q):
        d = dist(P, Q)
        v = vec(P, Q)
        items.append(num_item(
            f"dd-{n:02d}", rf"The distance between $A{pt_tex(P)}$ and $B{pt_tex(Q)}$.", d,
            rf"$\overrightarrow{{AB}}={vec_tex(v)}$, so $AB=\sqrt{{{tex(v[0]**2)}+{tex(v[1]**2)}}}={tex(d)}$.",
            ["Subtract the coordinates to get $\\overrightarrow{AB}$, then use Pythagoras."]))

    distance(1, (3, -1), (-3, 7))
    distance(2, (1, 2), (-4, -10))
    distance(3, (1, 1), (4, 7))
    distance(4, (-5, 2), (7, -3))

    P, Q = (-6, 3), (2, 9)
    M = mid(P, Q)
    items.append(pt_item("dd-05", rf"The midpoint of the segment with ends $A{pt_tex(P)}$ and $B{pt_tex(Q)}$.", M,
                         rf"$M=\left(\dfrac{{{tex(P[0])}+{par(Q[0])}}}{{2}},\dfrac{{{tex(P[1])}+{par(Q[1])}}}{{2}}\right)={pt_tex(M)}$.",
                         ["Add the coordinates and divide by $2$."]))
    M, A = (2, -1), (5, 3)
    Bp = (2 * M[0] - A[0], 2 * M[1] - A[1])
    items.append(pt_item("dd-06", rf"The point $M{pt_tex(M)}$ is the midpoint of $AB$ and $A{pt_tex(A)}$. Find $B$.", Bp,
                         rf"From $M=\dfrac{{A+B}}2$ we get $B=2M-A=\left(2\cdot{tex(M[0])}-{par(A[0])},\,2\cdot{par(M[1])}-{tex(A[1])}\right)={pt_tex(Bp)}$.",
                         ["Solve $M=\\dfrac{A+B}{2}$ for $B$."]))

    def divide(n, A, B, m, k, external):
        kk = R(-m, k) if external else R(m, k)
        Pp = (rad((A[0] + kk * B[0]) / (1 + kk)), rad((A[1] + kk * B[1]) / (1 + kk)))
        kind = "outside the segment (external division)" if external else "on the segment (internal division)"
        items.append(pt_item(
            f"dd-{n:02d}", rf"The point $P$ of the line $AB$, {kind}, with $AP:PB={m}:{k}$, for $A{pt_tex(A)}$ and $B{pt_tex(B)}$.", Pp,
            rf"The number $k$ is ${tex(kk)}$, so $P=\dfrac{{A+kB}}{{1+k}}={pt_tex(Pp)}$.",
            ["Internal division has $k=\\dfrac mn$; external division has $k=-\\dfrac mn$. Then $P=\\dfrac{A+kB}{1+k}$."]))

    divide(7, (-1, 4), (9, -1), 2, 3, False)
    divide(8, (2, 1), (6, 5), 5, 2, True)
    A, B, Pp = (1, -1), (9, 3), (7, 2)
    kk = rad(sp.Integer(1) * (Pp[0] - A[0]) / (B[0] - Pp[0]))
    items.append(ex("dd-09", rf"The point $P{pt_tex(Pp)}$ is on the segment $AB$ with $A{pt_tex(A)}$ and $B{pt_tex(B)}$. Find the number $k=AP:PB$.",
                    "number", eng(kk), hints=["Compare the first coordinates: $\\overrightarrow{AP}$ and $\\overrightarrow{PB}$."],
                    solution=rf"$\overrightarrow{{AP}}={vec_tex(vec(A, Pp))}$ and $\overrightarrow{{PB}}={vec_tex(vec(Pp, B))}$; the first is ${tex(kk)}$ times the second, so $AP:PB={tex(kk)}:1$."))
    return items


def u1l2() -> list[dict]:
    items: list[dict] = []
    n = 0

    def forms(P, Q, label):
        nonlocal n
        d = vec(P, Q)
        L = line_through(P, Q)
        a, b, c = L
        cosa, sina, p = normal_form(L)
        pre = rf"the line through $A{pt_tex(P)}$ and $B{pt_tex(Q)}$"
        n += 1
        items.append(ex(f"eq-{n:02d}", rf"A direction vector of {pre}.", "direction", pt_eng(d),
                        hints=["Use $\\overrightarrow{AB}$."], solution=rf"$\overrightarrow{{AB}}={vec_tex(d)}$; any non-zero multiple is also a direction vector."))
        n += 1
        items.append(line_item(f"eq-{n:02d}", rf"The analytic implicit equation of {pre}.", L,
                               rf"A normal vector is $({tex(a)},\,{tex(b)})$, perpendicular to the direction ${vec_tex(d)}$. Through $A$: $${line_tex(L)}$$",
                               ["Turn the direction vector $(d_1,d_2)$ into the normal vector $(d_2,-d_1)$."]))
        if b != 0:
            n += 1
            items.append(ex(f"eq-{n:02d}", rf"The analytic explicit equation $y=mx+p$ of {pre}.", "equation", explicit_eng(L), coordinates=["x", "y"],
                            hints=["Solve the implicit equation for $y$."],
                            solution=rf"From ${line_tex(L)}$ we get ${explicit_tex(L)}$."))
        n += 1
        items.append(ex(f"eq-{n:02d}", rf"The numbers $(\cos\alpha,\ \sin\alpha)$ of the normal form $x\cos\alpha+y\sin\alpha-p=0$ of {pre}.", "vector",
                        pt_eng((cosa, sina)), variables=["x"],
                        hints=["Divide the implicit equation by $\\varepsilon\\sqrt{a^2+b^2}$ with $\\varepsilon=-1$ if $c>0$ and $\\varepsilon=1$ otherwise."],
                        solution=rf"The implicit equation is ${line_tex(L)}$ with $\sqrt{{a^2+b^2}}={tex(rad(sp.sqrt(a**2+b**2)))}$. After division, $\cos\alpha={tex(cosa)}$, $\sin\alpha={tex(sina)}$ and $p={tex(p)}$."))
        n += 1
        items.append(ex(f"eq-{n:02d}", rf"The distance $p$ from the origin to {pre}.", "expression", eng(p),
                        hints=["$p=\\dfrac{|c|}{\\sqrt{a^2+b^2}}$."],
                        solution=rf"The numerator is $|c|={tex(sp.Abs(c))}$ and the length of the normal is $\sqrt{{a^2+b^2}}={tex(rad(sp.sqrt(a**2 + b**2)))}$, so $p={tex(p)}$."))
        if a != 0 and b != 0 and c != 0:
            q1, q2 = rad(-c / a), rad(-c / b)
            n += 1
            items.append(ex(f"eq-{n:02d}", rf"The points where {pre} meets the two axes (first the $x$-axis).", "points",
                            f"({eng(q1)}, 0), (0, {eng(q2)})", hints=["Put $y=0$, then $x=0$, in the implicit equation."],
                            solution=rf"$y=0$ gives $x={tex(q1)}$ and $x=0$ gives $y={tex(q2)}$. The intercept form is $\dfrac{{x}}{{{tex(q1)}}}+\dfrac{{y}}{{{tex(q2)}}}=1$."))

    forms((1, 2), (4, 6), "L1")
    forms((-2, 5), (4, -1), "L2")

    def from_parametric(x0, y0, d1, d2):
        nonlocal n
        L = line_through((x0, y0), (x0 + d1, y0 + d2))
        n += 1
        items.append(line_item(f"eq-{n:02d}", rf"Write in implicit form the line $x={x0}{d1:+d}\lambda$, $y={y0}{d2:+d}\lambda$.", L,
                               rf"The direction vector is $({d1},{d2})$, so a normal vector is $({d2},{-d1})$. Through $({x0},{y0})$: ${line_tex(L)}$.",
                               ["The coefficients of $\\lambda$ form the direction vector."]))

    from_parametric(2, -1, 3, 2)
    from_parametric(-4, 0, 1, 5)
    # canonical form
    L = norm_line(5, 2, 1)
    n += 1
    items.append(line_item(f"eq-{n:02d}", r"Write in implicit form the line $\dfrac{x-1}{2}=\dfrac{y+3}{-5}$.", L,
                           r"Cross-multiply: $-5(x-1)=2(y+3)$, that is $-5x+5=2y+6$, so $5x+2y+1=0$.",
                           ["Multiply both sides by the denominators."]))
    n += 1
    P0, d = (1, -2), (3, 1)
    Pt = (P0[0] - 2 * d[0], P0[1] - 2 * d[1])
    items.append(pt_item(f"eq-{n:02d}", r"The point of the line $x=1+3\lambda$, $y=-2+\lambda$ for $\lambda=-2$.", Pt,
                         rf"$x=1+3\cdot(-2)={tex(Pt[0])}$ and $y=-2+(-2)={tex(Pt[1])}$.", ["Substitute $\\lambda=-2$."]))
    L = tuple(map(sp.sympify, (3, -5, 15)))
    q1, q2 = rad(-L[2] / L[0]), rad(-L[2] / L[1])
    n += 1
    items.append(ex(f"eq-{n:02d}", r"The points where the line $3x-5y+15=0$ meets the axes (first the $x$-axis).", "points",
                    f"({eng(q1)}, 0), (0, {eng(q2)})", hints=["Put $y=0$, then $x=0$."],
                    solution=rf"$y=0$: $x={tex(q1)}$. $x=0$: $y={tex(q2)}$. The intercept form is $\dfrac{{x}}{{{tex(q1)}}}+\dfrac{{y}}{{{tex(q2)}}}=1$."))
    return items


def u1l3() -> list[dict]:
    items: list[dict] = []

    def angle(n, L1, L2, t1, t2):
        L1, L2 = tuple(map(sp.sympify, L1)), tuple(map(sp.sympify, L2))
        n1, n2 = (L1[0], L1[1]), (L2[0], L2[1])
        dot = n1[0] * n2[0] + n1[1] * n2[1]
        cos = rad(sp.Abs(dot) / (sp.sqrt(n1[0] ** 2 + n1[1] ** 2) * sp.sqrt(n2[0] ** 2 + n2[1] ** 2)))
        items.append(num_item(
            f"an-{n:02d}", rf"$\cos\theta$ for the angle $\theta$ between the lines ${t1}$ and ${t2}$.", cos,
            rf"The normal vectors are ${vec_tex(n1)}$ and ${vec_tex(n2)}$, with $\dotp{{\vec n_1}}{{\vec n_2}}={tex(dot)}$. Then $\cos\theta=\dfrac{{|{tex(dot)}|}}{{\norm{{\vec n_1}}\,\norm{{\vec n_2}}}}={tex(cos)}$.",
            ["Use the normal vectors $(a,b)$ and the absolute value of the dot product."]))

    angle(1, (2, 1, 0), (1, -3, 0), "2x+y=0", "x-3y=0")
    angle(2, (3, -1, 0), (1, -2, 0), "3x-y=0", "x-2y=0")
    angle(3, (1, 1, -4), (1, -7, 3), "x+y-4=0", "x-7y+3=0")
    items.append(ex("an-04", r"The angle between the lines $y=2x+1$ and $y=-3x$.", "expression", "pi/4",
                    hints=["$\\tan\\theta=\\left|\\dfrac{m_2-m_1}{1+m_1m_2}\\right|$."],
                    solution=r"$m_1=2$ and $m_2=-3$, so $\tan\theta=\left|\dfrac{-3-2}{1+2\cdot(-3)}\right|=\left|\dfrac{-5}{-5}\right|=1$ and $\theta=\dfrac\pi4$."))
    items.append(ex("an-05", r"For which value of $k$ are the lines $kx+2y-1=0$ and $3x-y+4=0$ perpendicular?", "number", "2/3",
                    hints=["Perpendicular: $a_1a_2+b_1b_2=0$."],
                    solution=r"$3k+2\cdot(-1)=0$, so $k=\dfrac23$."))
    items.append(ex("an-06", r"For which value of $k$ are the lines $kx+2y-1=0$ and $3x-y+4=0$ parallel?", "number", "-6",
                    hints=["Parallel: $a_1b_2-a_2b_1=0$."],
                    solution=r"$k\cdot(-1)-3\cdot2=0$, so $k=-6$."))
    L0 = (4, -1, 1)
    Pp = (2, 3)
    par_l = line_normal((L0[0], L0[1]), Pp)
    perp_l = line_normal((L0[1], -L0[0]), Pp)
    items.append(line_item("an-07", rf"The line through $P{pt_tex(Pp)}$ parallel to ${line_tex(L0)}$.", par_l,
                           rf"A parallel line keeps the normal $(4,-1)$: ${line_tex(par_l)}$.", ["Keep the normal vector."]))
    items.append(line_item("an-08", rf"The line through $P{pt_tex(Pp)}$ perpendicular to ${line_tex(L0)}$.", perp_l,
                           rf"The normal of the perpendicular line is the direction vector of the given line, $({L0[1]*-1},{L0[0]})\parallel(1,4)$: ${line_tex(perp_l)}$.",
                           ["Use $(b,-a)$ as the new normal vector."]))
    items.append(line_item("an-09", r"The perpendicular to $5x-2y+3=0$ through the origin.", line_normal((2, 5), (0, 0)),
                           r"The normal of the perpendicular is $(2,5)$, and the line passes through $(0,0)$: $2x+5y=0$.", ["Swap the coefficients and change one sign."]))
    return items


def u1l4() -> list[dict]:
    items: list[dict] = []

    def point_line(n, p, L):
        p, L = tuple(map(sp.sympify, p)), tuple(map(sp.sympify, L))
        d = dist_point_line(p, L)
        items.append(num_item(
            f"ds-{n:02d}", rf"The distance from $P{pt_tex(p)}$ to the line ${line_tex(L)}$.", d,
            rf"The numerator is $|{tex(L[0])}\cdot{par(p[0])}+{par(L[1])}\cdot{par(p[1])}+{par(L[2])}|={tex(sp.Abs(eval_line(L, p)))}$ and the length of the normal is $\sqrt{{a^2+b^2}}={tex(rad(sp.sqrt(L[0]**2 + L[1]**2)))}$, so $d={tex(d)}$.",
            ["$d=\\dfrac{|ax_0+by_0+c|}{\\sqrt{a^2+b^2}}$."]))

    point_line(1, (2, 3), (3, -4, 5))
    point_line(2, (1, -2), (5, 12, -3))
    point_line(3, (0, 0), (1, 1, -4))
    point_line(4, (-3, 4), (2, -1, 7))

    def foot(n, p, L):
        p, L = tuple(map(sp.sympify, p)), tuple(map(sp.sympify, L))
        t = rad((L[0] * p[0] + L[1] * p[1] + L[2]) / (L[0] ** 2 + L[1] ** 2))
        H = (rad(p[0] - t * L[0]), rad(p[1] - t * L[1]))
        assert eval_line(L, H) == 0
        items.append(pt_item(f"ds-{n:02d}", rf"The foot of the perpendicular from $P{pt_tex(p)}$ to the line ${line_tex(L)}$.", H,
                             rf"$t=\dfrac{{ax_0+by_0+c}}{{a^2+b^2}}={tex(t)}$ and $H=P-t\,(a,b)={pt_tex(H)}$.",
                             ["$H=P-t\\,(a,b)$ with $t=\\dfrac{ax_0+by_0+c}{a^2+b^2}$."]))

    foot(5, (3, -1), (3, 4, -10))
    foot(6, (4, 5), (1, -1, 0))

    def parallel(n, L1, L2):
        L1, L2 = tuple(map(sp.sympify, L1)), tuple(map(sp.sympify, L2))
        k = rad(L2[0] / L1[0])
        d = rad(sp.Abs(L1[2] - L2[2] / k) / sp.sqrt(L1[0] ** 2 + L1[1] ** 2))
        items.append(num_item(
            f"ds-{n:02d}", rf"The distance between the parallel lines ${line_tex(L1)}$ and ${line_tex(L2)}$.", d,
            rf"Divide the second equation by ${tex(k)}$ so that the coefficients of $x$ and $y$ are the same as in the first: its constant term becomes ${tex(rad(L2[2]/k))}$. "
            rf"Then $d=\dfrac{{|c_1-c_2|}}{{\sqrt{{a^2+b^2}}}}={tex(d)}$.",
            ["Make the coefficients of $x$ and $y$ equal first."]))

    parallel(7, (3, 4, 1), (3, 4, -9))
    parallel(8, (2, -1, 3), (4, -2, -7))
    parallel(9, (1, 2, 5), (3, 6, 1))
    # distance from a vertex to the opposite side
    L = line_through((14, 0), (5, 12))
    items.append(num_item("ds-10", r"The distance from $A(0,0)$ to the line through $B(14,0)$ and $C(5,12)$.", dist_point_line((0, 0), L),
                          rf"The line $BC$ is ${line_tex(L)}$, so $d=\dfrac{{|{tex(L[2])}|}}{{{tex(rad(sp.sqrt(L[0]**2+L[1]**2)))}}}={tex(dist_point_line((0,0),L))}$.",
                          ["First write the equation of $BC$."]))
    return items


def u1l5() -> list[dict]:
    items: list[dict] = []

    def inter(n, L1, L2):
        L1, L2 = tuple(map(sp.sympify, L1)), tuple(map(sp.sympify, L2))
        p = meet(L1, L2)
        items.append(pt_item(f"in-{n:02d}", rf"The intersection of ${line_tex(L1)}$ and ${line_tex(L2)}$.", p,
                             rf"$D={tex(L1[0]*L2[1]-L2[0]*L1[1])}\neq0$, and solving gives $x={tex(p[0])}$, $y={tex(p[1])}$.",
                             ["Eliminate one variable, or use $D=a_1b_2-a_2b_1$."]))

    inter(1, (3, -1, -5), (1, 2, -4))
    inter(2, (2, 3, -7), (1, -1, -1))
    inter(3, (1, -2, 3), (3, 1, -5))
    inter(4, (5, 2, 1), (1, 3, -10))
    items.append(ex("in-05", r"For which value of $k$ are the lines $x+y-3=0$, $2x-y=0$ and $x+ky-9=0$ concurrent?", "number", "4",
                    hints=["Find the intersection of the first two lines."],
                    solution=r"The first two lines meet at $(1,2)$. The third passes through it when $1+2k-9=0$, so $k=4$."))
    items.append(ex("in-06", r"For which value of $k$ do the lines $2x-y+1=0$, $x+y-4=0$ and $3x+ky-9=0$ pass through one point?", "number", "2",
                    hints=["The first two lines meet at $(1,3)$."],
                    solution=r"Adding the first two equations gives $3x-3=0$, so they meet at $(1,3)$. The third line passes through it when $3+3k-9=0$, so $k=2$."))
    return items


# ============================ UNIT 2: the triangle ================================================================
def intro(T: Tri) -> str:
    return f"In the triangle {tri_tex(T)}, "


def u2l1() -> list[dict]:
    items: list[dict] = []
    for i, T in enumerate((T1, TP, T2), 1):
        A, B, C = T.A, T.B, T.C
        extra = {"note": PAPER_NOTE} if T is TP else {}
        items.append(num_item(
            f"tl1-p{i}", intro(T) + "find the perimeter.", T.per,
            rf"$a=BC={tex(T.a)}$, $b=CA={tex(T.b)}$, $c=AB={tex(T.c)}$. The perimeter is $a+b+c={tex(T.per)}$.",
            ["Find the three side lengths with the distance formula."], **extra))
        AB, AC = vec(A, B), vec(A, C)
        items.append(num_item(
            f"tl1-k{i}", intro(T) + "find the area.", T.K,
            rf"$\overrightarrow{{AB}}={vec_tex(AB)}$, $\overrightarrow{{AC}}={vec_tex(AC)}$, so $K=\dfrac12\left|{par(AB[0])}\cdot{par(AC[1])}-{par(AC[0])}\cdot{par(AB[1])}\right|={tex(T.K)}$.",
            ["Half of the absolute value of the determinant of $\\overrightarrow{AB}$ and $\\overrightarrow{AC}$."]))
        for v in "ABC":
            P, Q, Rr, opp, bq, cr = T.V(v)
            cosv = T.angle_cos(v)
            items.append(num_item(
                f"tl1-c{v.lower()}{i}", intro(T) + rf"find $\cos\hat {v}$.", cosv,
                rf"$\overrightarrow{{{v}{NXT[v]}}}={vec_tex(vec(P, Q))}$, $\overrightarrow{{{v}{PRV[v]}}}={vec_tex(vec(P, Rr))}$. "
                rf"The dot product is ${tex(rad(sum(vec(P,Q)[j]*vec(P,Rr)[j] for j in (0,1))))}$ and the norms are ${tex(rad(dist(P,Q)))}$ and ${tex(rad(dist(P,Rr)))}$, so $\cos\hat {v}={tex(cosv)}$.",
                ["Use the vectors from the vertex to the two other vertices."]))
    # sides forms of AB for the past paper triangle
    L = line_through(TP.A, TP.B)
    items.append(line_item("tl1-s1", intro(TP) + "find the analytic implicit equation of the side $AB$.", L,
                           rf"$\overrightarrow{{AB}}={vec_tex(vec(TP.A, TP.B))}$, a normal vector is $({tex(L[0])},{tex(L[1])})$, and the equation is ${line_tex(L)}$.",
                           ["Use $\\overrightarrow{AB}$ as the direction."], note=PAPER_NOTE))
    ca, sa, p = normal_form(L)
    items.append(ex("tl1-s2", intro(TP) + r"find $\cos\alpha$, $\sin\alpha$ of the normal form of the side $AB$.", "vector", pt_eng((ca, sa)), variables=["x"],
                    hints=["The implicit form is $3x-4y+17=0$."],
                    solution=rf"The implicit equation ${line_tex(L)}$ has $c=17>0$, so we divide by $-5$: $\cos\alpha={tex(ca)}$, $\sin\alpha={tex(sa)}$, $p={tex(p)}$.", note=PAPER_NOTE))
    q1, q2 = rad(-L[2] / L[0]), rad(-L[2] / L[1])
    items.append(ex("tl1-s3", intro(TP) + "find the points where the line $AB$ meets the axes (first the $x$-axis).", "points",
                    f"({eng(q1)}, 0), (0, {eng(q2)})", hints=["Put $y=0$, then $x=0$."],
                    solution=rf"$y=0$ gives $x={tex(q1)}$; $x=0$ gives $y={tex(q2)}$.", note=PAPER_NOTE))
    return items


def u2l2() -> list[dict]:
    items: list[dict] = []
    for i, (T, v) in enumerate(((T1, "A"), (T2, "B"), (TP, "A"), (T4, "C")), 1):
        P, Q, Rr, opp, bq, cr = T.V(v)
        M, L, length = T.median(v)
        extra = {"note": PAPER_NOTE} if T is TP else {}
        items.append(line_item(
            f"tl2-e{i}", intro(T) + rf"find an equation of the median from ${v}$.", L,
            rf"The midpoint of the opposite side is $M={pt_tex(M)}$ and $\overrightarrow{{{v}M}}={vec_tex(vec(P, M))}$. A normal vector gives the equation ${line_tex(L)}$.",
            ["The median joins the vertex to the midpoint of the opposite side."], **extra))
        items.append(num_item(
            f"tl2-l{i}", intro(T) + rf"find the length of the median from ${v}$.", length,
            rf"$m={tex(length)}$: with the formula, $\dfrac12\sqrt{{2b^2+2c^2-a^2}}=\dfrac12\sqrt{{2\cdot{tex(rad(bq**2))}+2\cdot{tex(rad(cr**2))}-{tex(rad(opp**2))}}}$.",
            ["$m_a=\\dfrac12\\sqrt{2b^2+2c^2-a^2}$, or the distance from the vertex to the midpoint."], **extra))
        items.append(pt_item(
            f"tl2-g{i}", intro(T) + "find the centroid $G$.", T.G,
            rf"$G=\dfrac{{A+B+C}}{{3}}=\left(\dfrac{{{tex(rad(T.A[0]+T.B[0]+T.C[0]))}}}{{3}},\dfrac{{{tex(rad(T.A[1]+T.B[1]+T.C[1]))}}}{{3}}\right)={pt_tex(T.G)}$.",
            ["Average the coordinates of the vertices."], **extra))
    items.append(num_item("tl2-x1", r"A triangle has sides $a=6$, $b=7$, $c=5$. Find the median $m_a$.", sp.sqrt(112) / 2,
                          r"$m_a=\dfrac12\sqrt{2\cdot49+2\cdot25-36}=\dfrac12\sqrt{112}=2\sqrt7$.", ["Use the formula with the sides."]))
    items.append(num_item("tl2-x2", r"A triangle has sides $a=10$, $b=10$, $c=12$. Find the median from the vertex $A$.", sp.sqrt(2 * 100 + 2 * 144 - 100) / 2,
                          r"$m_a=\dfrac12\sqrt{2\cdot100+2\cdot144-100}=\dfrac12\sqrt{388}=\sqrt{97}$.", ["Use the formula with the sides."]))
    return items


def u2l3() -> list[dict]:
    items: list[dict] = []
    for i, (T, v) in enumerate(((T1, "A"), (T2, "B"), (TP, "A"), (T3, "A")), 1):
        P, Q, Rr, opp, bq, cr = T.V(v)
        F, L, h = T.altitude(v)
        extra = {"note": PAPER_NOTE} if T is TP else {}
        items.append(line_item(
            f"tl3-e{i}", intro(T) + rf"find an equation of the altitude from ${v}$.", L,
            rf"The normal vector of the altitude is the vector of the opposite side, ${vec_tex(vec(Q, Rr))}$. Through ${v}$: ${line_tex(L)}$.",
            ["The altitude is perpendicular to the opposite side: that side's vector is the normal."], **extra))
        items.append(num_item(
            f"tl3-l{i}", intro(T) + rf"find the length of the altitude from ${v}$.", h,
            rf"$K={tex(T.K)}$ and the opposite side is $a={tex(opp)}$, so $h=\dfrac{{2K}}{{a}}={tex(h)}$.",
            ["$h_a=\\dfrac{2K}{a}$."], **extra))
        items.append(pt_item(
            f"tl3-h{i}", intro(T) + "find the orthocenter $H$.", T.H,
            rf"Two altitudes meet at $H={pt_tex(T.H)}$ (also $H=A+B+C-2O$ with $O={pt_tex(T.O)}$).",
            ["Intersect two altitudes."], **extra))
    items.append(pt_item("tl3-r1", r"A triangle has $A(0,0)$, $B(8,0)$ and $C(0,6)$. Find the orthocenter.", (0, 0),
                         r"The angle at $A$ is a right angle, so $H=A=(0,0)$.", ["The triangle is right-angled."]))
    return items


def u2l4() -> list[dict]:
    items: list[dict] = []
    for i, (T, v) in enumerate(((T1, "A"), (T2, "A"), (T3, "B"), (T4, "A")), 1):
        P, Q, Rr, opp, bq, cr = T.V(v)
        D, L, length = T.bisector(v)
        items.append(line_item(
            f"tl4-e{i}", intro(T) + rf"find an equation of the internal angle bisector from ${v}$.", L,
            rf"The foot on the opposite side is $D=\dfrac{{bQ+cR}}{{b+c}}={pt_tex(D)}$ and the bisector is the line ${v}D$: ${line_tex(L)}$.",
            ["The foot divides the opposite side in the ratio of the other two sides."]))
        items.append(num_item(
            f"tl4-l{i}", intro(T) + rf"find the length of the angle bisector from ${v}$.", length,
            rf"$l=\dfrac{{1}}{{b+c}}\sqrt{{bc\left[(b+c)^2-a^2\right]}}$ with $a={tex(opp)}$, $b={tex(bq)}$, $c={tex(cr)}$, which gives ${tex(length)}$.",
            ["Use $l_a=\\dfrac{1}{b+c}\\sqrt{bc\\left[(b+c)^2-a^2\\right]}$."]))
        items.append(pt_item(
            f"tl4-i{i}", intro(T) + "find the incenter $I$.", T.I,
            rf"$I=\dfrac{{aA+bB+cC}}{{a+b+c}}$ with $a={tex(T.a)}$, $b={tex(T.b)}$, $c={tex(T.c)}$: $I={pt_tex(T.I)}$.",
            ["Weight each vertex by the length of the opposite side."]))
    items.append(num_item("tl4-r1", r"Find the inradius $r$ of the triangle with sides $13$, $14$, $15$.", R(4),
                          r"$s=21$, $K=\sqrt{21\cdot8\cdot7\cdot6}=84$, so $r=\dfrac Ks=4$.", ["$r=\\dfrac{K}{s}$."]))
    items.append(num_item("tl4-r2", r"Find the inradius of the triangle $A(0,0)$, $B(4,0)$, $C(0,3)$.", R(1),
                          r"$K=6$ and $s=6$, so $r=1$.", ["$r=\\dfrac{K}{s}$."]))
    return items


def u2l5() -> list[dict]:
    items: list[dict] = []
    for i, (T, v) in enumerate(((T1, "A"), (T3, "B"), (TP, "A"), (T4, "A")), 1):
        P, Q, Rr, opp, bq, cr = T.V(v)
        M, L, length = T.perp_bisector(v)
        extra = {"note": PAPER_NOTE} if T is TP else {}
        items.append(line_item(
            f"tl5-e{i}", intro(T) + rf"find an equation of the perpendicular bisector of the side opposite ${v}$.", L,
            rf"The midpoint is $M={pt_tex(M)}$ and the normal vector is the vector of the side, ${vec_tex(vec(Q, Rr))}$: ${line_tex(L)}$.",
            ["Through the midpoint, with the side's vector as normal."], **extra))
        items.append(num_item(
            f"tl5-l{i}", intro(T) + rf"find the length of the part inside the triangle of the perpendicular bisector of the side opposite ${v}$.", length,
            rf"The sides next to ${v}$ are ${tex(bq)}$ and ${tex(cr)}$, so the bisector leaves through the longer-angle side, and the length is ${tex(length)}$.",
            ["Use $\\dfrac a2\\tan$ of the angle at the end of the shorter of the two other sides, or $h_a$ if they are equal."], **extra))
        items.append(pt_item(
            f"tl5-o{i}", intro(T) + "find the circumcenter $O$.", T.O,
            rf"The perpendicular bisectors meet at $O={pt_tex(T.O)}$.", ["Intersect two perpendicular bisectors."], **extra))
        items.append(num_item(
            f"tl5-r{i}", intro(T) + "find the circumradius $R$.", T.Rc,
            rf"$R=\dfrac{{abc}}{{4K}}=\dfrac{{{tex(rad(T.a*T.b*T.c))}}}{{4\cdot{tex(T.K)}}}={tex(T.Rc)}$.",
            ["$R=\\dfrac{abc}{4K}$."], **extra))
    return items


def u2l6() -> list[dict]:
    items: list[dict] = []
    for i, T in enumerate((T1, T3, T4, TP), 1):
        extra = {"note": PAPER_NOTE} if T is TP else {}
        r2 = rad(T.r**2)
        items.append(ex(f"tl6-i{i}", intro(T) + "write the analytic equation of the incircle.", "equation",
                        f"(x-({eng(T.I[0])}))^2+(y-({eng(T.I[1])}))^2={eng(r2)}", coordinates=["x", "y"],
                        hints=["Center $I$ and radius $r=\\dfrac Ks$."],
                        solution=rf"$I={pt_tex(T.I)}$ and $r={tex(T.r)}$, so $(x-{par(T.I[0])})^2+(y-{par(T.I[1])})^2={tex(r2)}$.", **extra))
        items.append(ex(f"tl6-c{i}", intro(T) + "write the analytic equation of the circumcircle.", "equation",
                        f"(x-({eng(T.O[0])}))^2+(y-({eng(T.O[1])}))^2={eng(rad(T.Rc**2))}", coordinates=["x", "y"],
                        hints=["Center $O$ and radius $R=\\dfrac{abc}{4K}$."],
                        solution=rf"$O={pt_tex(T.O)}$ and $R={tex(T.Rc)}$, so $(x-{par(T.O[0])})^2+(y-{par(T.O[1])})^2={tex(rad(T.Rc**2))}$.", **extra))
        items.append(ex(f"tl6-p{i}", intro(T) + "find the perimeter of the incircle.", "expression", eng(rad(2 * PI * T.r)),
                        hints=["$2\\pi r$."], solution=rf"$2\pi r=2\pi\cdot{tex(T.r)}={tex(rad(2*PI*T.r))}$.", **extra))
        items.append(ex(f"tl6-a{i}", intro(T) + "find the area of the circumcircle.", "expression", eng(rad(PI * T.Rc**2)),
                        hints=["$\\pi R^2$."], solution=rf"$\pi R^2=\pi\cdot{tex(rad(T.Rc**2))}={tex(rad(PI*T.Rc**2))}$.", **extra))
    items = [it for it in items if it["id"] not in ("tl6-i4", "tl6-p4")]
    ctr, ra = T1.excenter("A")
    items.append(pt_item("tl6-x1", intro(T1) + "find the excenter $I_a$ opposite $A$.", ctr,
                         rf"$I_a=\dfrac{{-aA+bB+cC}}{{-a+b+c}}={pt_tex(ctr)}$.", ["Change the sign of $a$ in the incenter formula."]))
    items.append(num_item("tl6-x2", intro(T1) + "find the exradius $r_a$.", ra,
                          rf"$r_a=\dfrac{{K}}{{s-a}}={tex(ra)}$.", ["$r_a=\\dfrac{K}{s-a}$."]))
    items.append(ex("tl6-x3", r"A circle has center $(2,-3)$ and radius $5$. Give the point of its parametric equation for $t=\dfrac\pi2$.", "vector", "(2, 2)",
                    variables=["x"], hints=["$x=2+5\\cos t$, $y=-3+5\\sin t$."],
                    solution=r"$x=2+5\cos\dfrac\pi2=2$ and $y=-3+5\sin\dfrac\pi2=2$."))
    return items


def u2l7() -> list[dict]:
    """The complete study of the triangle of the past paper (parts a to f), one question per item."""
    T = TP
    A, B, C = T.A, T.B, T.C
    items: list[dict] = []
    note = {"note": PAPER_NOTE}
    # Euler
    items.append(ex("st-01", intro(T) + r"compute $\overrightarrow{HG}$ and check that it equals $2\overrightarrow{GO}$. Enter $\overrightarrow{HG}$.", "vector",
                    pt_eng(vec(T.H, T.G)), variables=["x"], hints=["Find $H$, $G$, $O$ first."],
                    solution=rf"$H={pt_tex(T.H)}$, $G={pt_tex(T.G)}$, $O={pt_tex(T.O)}$. $\overrightarrow{{HG}}={vec_tex(vec(T.H,T.G))}$ and $2\overrightarrow{{GO}}={vec_tex(tuple(2*c for c in vec(T.G,T.O)))}$: equal.", **note))
    items.append(pt_item("st-02", intro(T) + "find the orthocenter $H$ from the Euler relation $H=3G-2O$.", T.H,
                         rf"$G={pt_tex(T.G)}$, $O={pt_tex(T.O)}$, so $H=3G-2O={pt_tex(T.H)}$.", ["Compute $G$ and $O$ first."], **note))
    # whole-triangle quantities
    M, Lm, lm = T.median("A")
    Fa, La, ha = T.altitude("A")
    D, Lb, lb = T.bisector("A")
    items.append(num_item("st-03", intro(T) + "find the ratio $\\dfrac{GM_a}{AM_a}$ of the centroid on the median from $A$ (a number).", R(1, 3),
                          r"The centroid divides the median $2:1$ from the vertex, so $GM_a=\dfrac13AM_a$.", ["The centroid is at two thirds from the vertex."], **note))
    # equal sums
    items.append(num_item("st-04", intro(T) + "find $h_a\\cdot a$ (the double area $2K$).", rad(2 * T.K),
                          rf"$h_a\cdot a=2K={tex(rad(2*T.K))}$.", ["$h_a=\\dfrac{2K}{a}$."], **note))
    items.append(ex("st-05", intro(T) + "write in implicit form the line through the circumcenter and the centroid (the Euler line).", "equation",
                    line_eng(line_through(T.O, T.G)), coordinates=["x", "y"], hints=["The Euler line passes through $O$, $G$ and $H$."],
                    solution=rf"The direction is $\overrightarrow{{OG}}={vec_tex(vec(T.O,T.G))}$, so the line is ${line_tex(line_through(T.O,T.G))}$; $H$ is on it.", **note))
    U = T1
    items.append(ex("st-06", intro(U) + "check that the incenter is at distance $r$ from the side $AB$: find this distance.", "expression", eng(U.r),
                    hints=["Use the point-line distance formula."],
                    solution=rf"The distance from $I={pt_tex(U.I)}$ to $AB:\ {line_tex(line_through(U.A, U.B))}$ is ${tex(dist_point_line(U.I, line_through(U.A, U.B)))}$, which equals $r={tex(U.r)}$."))
    items.append(num_item("st-07", intro(U) + "find the ratio $AI:ID_a$ of the incenter on the bisector from $A$, as a number.", rad((U.b + U.c) / U.a),
                          rf"$AI:ID_a=(b+c):a=\dfrac{{{tex(rad(U.b + U.c))}}}{{{tex(U.a)}}}={tex(rad((U.b + U.c) / U.a))}$.", ["$AI:ID_a=(b+c):a$."]))
    # the incenter and the bisector of the past-paper triangle, in the form the paper uses (denominators are not rationalized)
    a_, b_, c_ = T.a, T.b, T.c
    den = "(5+sqrt(145)+4*sqrt(10))"
    ix = f"(-12*sqrt(10)+sqrt(145)+25)/{den}"
    iy = f"(8*sqrt(10)+5*sqrt(145)-35)/{den}"
    assert abs(float(sp.N(P_expr(ix) - T.I[0], 20))) < 1e-12 and abs(float(sp.N(P_expr(iy) - T.I[1], 20))) < 1e-12
    items.append(ex("st-08", intro(T) + "find the incenter $I$ (leave the denominator as it is).", "vector", f"({ix}, {iy})",
                    hints=["$I=\\dfrac{aA+bB+cC}{a+b+c}$ with $a=BC=4\\sqrt{10}$, $b=CA=\\sqrt{145}$, $c=AB=5$."],
                    solution=(r"The sides are $a=4\sqrt{10}$, $b=\sqrt{145}$, $c=5$, so $a+b+c=5+\sqrt{145}+4\sqrt{10}$. "
                              r"$x_I=\dfrac{a\cdot(-3)+b\cdot1+c\cdot5}{a+b+c}=\dfrac{-12\sqrt{10}+\sqrt{145}+25}{5+\sqrt{145}+4\sqrt{10}}$ and "
                              r"$y_I=\dfrac{a\cdot2+b\cdot5+c\cdot(-7)}{a+b+c}=\dfrac{8\sqrt{10}+5\sqrt{145}-35}{5+\sqrt{145}+4\sqrt{10}}$."),
                    lintIgnore=["unrationalized-denominator"], **note))
    lb_key = "sqrt(7250+50*sqrt(145))/(5+sqrt(145))"
    assert abs(float(sp.N(P_expr(lb_key) - T.bisector("A")[2], 20))) < 1e-12
    items.append(ex("st-09", intro(T) + "find the length of the angle bisector from $A$ (leave the denominator as it is).", "expression", lb_key,
                    hints=["$l_a=\\dfrac{1}{b+c}\\sqrt{bc\\left[(b+c)^2-a^2\\right]}$."],
                    solution=(r"$bc=5\sqrt{145}$ and $(b+c)^2-a^2=145+10\sqrt{145}+25-160=10+10\sqrt{145}$, so $bc\left[(b+c)^2-a^2\right]=7250+50\sqrt{145}$. "
                              r"Hence $l_a=\dfrac{\sqrt{7250+50\sqrt{145}}}{5+\sqrt{145}}$."),
                    lintIgnore=["unrationalized-denominator"], **note))
    return items


# ============================ UNIT 3: the circle ====================================================================
def circle_gen(p, q, r2):
    D, E = -2 * p, -2 * q
    F = p**2 + q**2 - r2
    return D, E, F


def u3l1() -> list[dict]:
    items: list[dict] = []
    for n, (p, q, rr) in enumerate(((3, -2, 5), (-1, 2, 3), (R(1, 2), 2, 2), (0, 4, 1)), 1):
        D, E, F = circle_gen(p, q, rr**2)
        items.append(ex(f"ci-g{n}", rf"Find the center and the radius of the circle ${poly_tex(D, E, F)}$ "
                                    r"(enter the center first, then the radius).", "vector", f"({eng(p)}, {eng(q)}, {eng(rr)})", variables=["x"],
                        hints=["Complete the squares, or use $\\left(-\\dfrac D2,-\\dfrac E2\\right)$."],
                        solution=rf"The center is $\left({tex(p)},{tex(q)}\right)$ and $r^2=\dfrac{{D^2+E^2}}4-F={tex(rad(rr**2))}$, so $r={tex(rr)}$."))
    for n, (P1, P2) in enumerate((((1, 2), (5, 6)), ((-3, 0), (3, 8)), ((0, 0), (6, 0))), 1):
        M = mid(P1, P2)
        r2 = rad(((P2[0] - P1[0]) ** 2 + (P2[1] - P1[1]) ** 2) / sp.Integer(4))
        items.append(ex(f"ci-d{n}", rf"The circle with the segment from $A{pt_tex(P1)}$ to $B{pt_tex(P2)}$ as a diameter.", "equation",
                        f"(x-({eng(M[0])}))^2+(y-({eng(M[1])}))^2={eng(r2)}", coordinates=["x", "y"],
                        hints=["The center is the midpoint of the diameter."],
                        solution=rf"The center is $M={pt_tex(M)}$ and $r^2=\dfrac{{AB^2}}4={tex(r2)}$: $(x-{par(M[0])})^2+(y-{par(M[1])})^2={tex(r2)}$."))
    # three points
    for n, pts in enumerate((((0, 0), (6, 0), (0, 8)), ((1, 0), (0, 1), (-1, 0)), ((2, 1), (5, 4), (6, 1))), 1):
        X, Y = sp.symbols("X Y", real=True)
        Dv, Ev, Fv = sp.symbols("Dv Ev Fv")
        s = sp.solve([P[0] ** 2 + P[1] ** 2 + Dv * P[0] + Ev * P[1] + Fv for P in pts], [Dv, Ev, Fv], dict=True)[0]
        D, E, F = s[Dv], s[Ev], s[Fv]
        key = f"x^2+y^2+({eng(D)})*x+({eng(E)})*y+({eng(F)})=0"
        items.append(ex(f"ci-t{n}", r"The circle through the points " + ", ".join(f"${pt_tex(P)}$" for P in pts) + ".", "equation", key,
                        coordinates=["x", "y"], hints=["Substitute the three points into $x^2+y^2+Dx+Ey+F=0$."],
                        solution=rf"The three equations give $D={tex(D)}$, $E={tex(E)}$, $F={tex(F)}$: ${poly_tex(D, E, F)}$."))
    # circumcircle of a triangle through its vertices: area
    items.append(ex("ci-a1", r"The area enclosed by the circle $x^2+y^2-6x-8y=0$.", "expression", "25*pi",
                    hints=["Find the radius first."], solution=r"The center is $(3,4)$ and $r^2=9+16=25$, so the area is $\pi r^2=25\pi$."))
    items.append(ex("ci-a2", r"The circumference of the circle $x^2+y^2+2x-4y-4=0$.", "expression", "6*pi",
                    hints=["Complete the squares to find $r$."], solution=r"$(x+1)^2+(y-2)^2=9$, so $r=3$ and the circumference is $2\pi r=6\pi$."))
    return items


def u3l2() -> list[dict]:
    items: list[dict] = []

    def tangent_at(n, p, q, r, P0):
        assert (P0[0] - p) ** 2 + (P0[1] - q) ** 2 == r**2
        # (x0-p)(x-p)+(y0-q)(y-q)=r^2  ->  (x0-p)x + (y0-q)y - (x0-p)p - (y0-q)q - r^2 = 0
        L = norm_line(P0[0] - p, P0[1] - q, -(P0[0] - p) * p - (P0[1] - q) * q - r**2)
        assert dist_point_line((p, q), L) == r
        items.append(line_item(f"tg-{n:02d}", rf"The tangent to the circle $(x-{par(p)})^2+(y-{par(q)})^2={r**2}$ at the point $P_0{pt_tex(P0)}$.", L,
                               rf"The radius vector is $({tex(P0[0]-p)},{tex(P0[1]-q)})$, so the tangent is $({tex(P0[0]-p)})(x-{par(p)})+({tex(P0[1]-q)})(y-{par(q)})={r**2}$, that is ${line_tex(L)}$.",
                               ["The tangent is perpendicular to the radius at the point of contact."]))

    tangent_at(1, 1, -2, 5, (4, 2))
    tangent_at(2, 0, 0, 5, (3, 4))
    tangent_at(3, 0, 0, 13, (5, -12))
    tangent_at(4, 2, 1, 5, (6, 4))

    def power(n, p, q, r, P):
        pw = rad((P[0] - p) ** 2 + (P[1] - q) ** 2 - r**2)
        length = rad(sp.sqrt(pw))
        items.append(num_item(f"tg-{n:02d}", rf"The length of a tangent segment from $P{pt_tex(P)}$ to the circle with center $({p},{q})$ and radius ${r}$.", length,
                              rf"$\text{{pow}}(P)=CP^2-r^2={tex(pw)}$, so the length is $\sqrt{{{tex(pw)}}}={tex(length)}$.",
                              ["$\\sqrt{CP^2-r^2}$."]))

    power(5, 0, 0, 5, (5, 12))
    power(6, 1, 2, 3, (6, 14))
    power(7, 0, 0, 2, (4, 0))
    items.append(ex("tg-08", r"How many common points have the line $3x+4y-20=0$ and the circle $x^2+y^2=16$?", "number", "1",
                    hints=["Compare the distance from the center to the line with the radius."],
                    solution=r"The distance from the origin to the line is $\dfrac{20}{5}=4$, which equals the radius $4$: the line is tangent to the circle, so there is exactly one common point."))
    return items


def u3l3() -> list[dict]:
    items: list[dict] = []

    def radical(n, S1, S2):
        # circles given as (D, E, F): x^2+y^2+Dx+Ey+F=0
        L = norm_line(S1[0] - S2[0], S1[1] - S2[1], S1[2] - S2[2])
        items.append(line_item(f"tc-{n:02d}", rf"The radical axis of ${poly_tex(*S1)}$ and ${poly_tex(*S2)}$.", L,
                               rf"Subtract the equations: $({S1[0]-S2[0]})x+({S1[1]-S2[1]})y+({S1[2]-S2[2]})=0$, that is ${line_tex(L)}$.",
                               ["Subtract the two equations."]))

    radical(1, (0, 0, -9), (-4, -6, 9))
    radical(2, (0, 0, -25), (-12, 0, 11))
    radical(3, (-2, 4, -4), (4, -2, 1))
    items.append(pt_item("tc-04", r"The common point with positive $y$ of the circles $x^2+y^2=25$ and $(x-6)^2+y^2=25$.", (3, 4),
                         r"The radical axis is $x=3$; then $y^2=25-9=16$, so $y=4$.", ["Find the radical axis first."]))
    items.append(pt_item("tc-05", r"The common point with positive $y$ of $x^2+y^2=9$ and $(x-5)^2+y^2=16$.", (R(9, 5), R(12, 5)),
                         r"The radical axis is $x=\dfrac95$; then $y^2=9-\dfrac{81}{25}=\dfrac{144}{25}$ and $y=\dfrac{12}5$.", ["Subtract the equations."]))
    items.append(ex("tc-06", r"The circles $x^2+y^2=9$ and $(x-5)^2+y^2=16$ are orthogonal. Compute $d^2-r_1^2-r_2^2$.", "number", "0",
                    hints=["$d=5$, $r_1=3$, $r_2=4$."], solution=r"$25-9-16=0$, so the circles are orthogonal."))
    items.append(ex("tc-07", r"For which value of $d>0$ are two circles of radii $5$ and $12$ orthogonal? ($d$ = distance between the centers.)", "number", "13",
                    hints=["$d^2=r_1^2+r_2^2$."], solution=r"$d^2=25+144=169$, so $d=13$."))
    items.append(ex("tc-08", r"Two circles have radii $7$ and $3$ and their centers are $4$ apart. What is the position? Answer $1$ for externally tangent, $2$ for intersecting, $3$ for internally tangent.", "number", "3",
                    hints=["Compare $d$ with $r_1-r_2$."], solution=r"$d=4=7-3$: the circles are internally tangent."))
    return items


def build() -> None:
    write_exercises(f"{U1}/l01-distance-and-division", [exset("distance", "Distance, midpoint and division of a segment.", u1l1(),
                    format="Type a point as `(x, y)` and a number or an exact expression such as `sqrt(2)/3`.")], "geo_m02.py")
    write_exercises(f"{U1}/l02-eight-equations-of-a-line", [exset("equations", "Equations of a line.", u1l2(),
                    format="Type an equation with `=`, for example `x - 2*y + 5 = 0` (any non-zero multiple is accepted). A list of points: `(1, 0), (0, 3)`.")], "geo_m02.py")
    write_exercises(f"{U1}/l03-angle-between-lines", [exset("angles", "Angles, parallel and perpendicular lines.", u1l3(),
                    format="Type a number or an exact expression such as `pi/6` or `sqrt(3)/2`; type an equation with `=`.")], "geo_m02.py")
    write_exercises(f"{U1}/l04-distances", [exset("distances", "Distances from a point to a line, and between parallel lines.", u1l4(),
                    format="Type an exact value such as `7/5` or `3*sqrt(2)`; a point as `(x, y)`.")], "geo_m02.py")
    write_exercises(f"{U1}/l05-intersection-of-lines", [exset("intersections", "Intersections and concurrent lines.", u1l5(),
                    format="Type a point as `(x, y)` or a number.")], "geo_m02.py")
    write_exercises(f"{U2}/l01-vertices-sides-angles", [exset("sides", "Sides, perimeter, angles and area.", u2l1(),
                    format="Type an exact value; radicals as `sqrt(145)`. A point as `(x, y)`; a list of points as `(a, 0), (0, b)`.")], "geo_m02.py")
    write_exercises(f"{U2}/l02-medians-and-centroid", [exset("medians", "Medians and the centroid.", u2l2(),
                    format="Type an exact value or an equation with `=`; a point as `(x, y)`.")], "geo_m02.py")
    write_exercises(f"{U2}/l03-altitudes-and-orthocenter", [exset("altitudes", "Altitudes and the orthocenter.", u2l3(),
                    format="Type an exact value or an equation with `=`; a point as `(x, y)`.")], "geo_m02.py")
    write_exercises(f"{U2}/l04-angle-bisectors-and-incenter", [exset("bisectors", "Angle bisectors and the incenter.", u2l4(),
                    format="Type an exact value or an equation with `=`; a point as `(x, y)`.")], "geo_m02.py")
    write_exercises(f"{U2}/l05-perpendicular-bisectors-and-circumcenter", [exset("perpendicular-bisectors", "Perpendicular bisectors and the circumcenter.", u2l5(),
                    format="Type an exact value or an equation with `=`; a point as `(x, y)`.")], "geo_m02.py")
    write_exercises(f"{U2}/l06-incircle-circumcircle-excircles", [exset("circles", "The incircle, the circumcircle and the excircles.", u2l6(),
                    format="Type a circle as `(x-1)^2+(y-2)^2=9`, a perimeter or an area with `pi`.")], "geo_m02.py")
    write_exercises(f"{U2}/l07-euler-line-and-complete-study", [exset("study", "Checks on the triangle of the past paper.", u2l7(),
                    format="Type an exact value or an equation with `=`; a point or a vector as `(x, y)`.")], "geo_m02.py")
    write_exercises(f"{U3}/l01-equation-of-a-circle", [exset("circles", "Equations of circles.", u3l1(),
                    format="Type an equation with `=`; for the center and the radius type `(p, q, r)`.")], "geo_m02.py")
    write_exercises(f"{U3}/l02-tangents-and-power", [exset("tangents", "Tangents and the power of a point.", u3l2(),
                    format="Type an equation with `=` or an exact number.")], "geo_m02.py")
    write_exercises(f"{U3}/l03-two-circles", [exset("two-circles", "Two circles and the radical axis.", u3l3(),
                    format="Type an equation with `=`, a point as `(x, y)`, or a number.")], "geo_m02.py")
