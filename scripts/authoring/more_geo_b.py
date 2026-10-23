"""More practice for Course 1, Module 2, Units 1 to 3: lines, the triangle and the circle.

Every key is computed with SymPy from the data of the problem; the geometric facts are also checked with numeric distances."""

from __future__ import annotations

import sympy as sp
from geo_m02 import (
    Tri, dist, dist_point_line, eval_line, line_eng, line_item, line_normal, line_through, line_tex, mid, meet, norm_line, num_item, pt_eng, pt_item, pt_tex, rad, vec, vec_tex,
)
from toolkit import add_extra, eng, ex, exset_plain, tex, with_units, x, y

SCRIPT = "more_geo_b.py"
U1 = "geo/m02-plane/u01-coordinates-and-lines"
U2 = "geo/m02-plane/u02-the-triangle"
U3 = "geo/m02-plane/u03-the-circle"
FMT = "Type a point as `(a, b)`, a number or an exact value such as `5/13` or `sqrt(7)/3`, and a line or a circle as an equation with `=`."


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


def P2(p) -> str:
    return pt_tex(p)


# --- unit 1 ---------------------------------------------------------------------------------------------------------------------------
def distance_items() -> list[dict]:
    items = []
    for n, (p, q) in enumerate((((-2, 3), (4, -5)), ((1, 1), (4, 5)), ((-3, -1), (2, 11))), 1):
        d = dist(p, q)
        items.append(num_item(f"mp-di-{n}", rf"Find the distance between $P{P2(p)}$ and $Q{P2(q)}$. The unit is lu: give the number only.", d,
                              rf"$\overrightarrow{{PQ}}={vec_tex(vec(p, q))}$, so $PQ=\sqrt{{{tex((q[0]-p[0])**2)}+{tex((q[1]-p[1])**2)}}}={tex(d)}$.", ["Use $\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$."]))
    p, q = (-4, 7), (10, -3)
    m = mid(p, q)
    items.append(pt_item("mp-di-4", rf"Find the midpoint of $P{P2(p)}$ and $Q{P2(q)}$.", m, rf"The midpoint is $\left(\dfrac{{-4+10}}2,\dfrac{{7-3}}2\right)={P2(m)}$.", ["Average the coordinates."]))
    a, b = (-1, 2), (9, 7)
    pt = (rad(a[0] + sp.Rational(2, 5) * (b[0] - a[0])), rad(a[1] + sp.Rational(2, 5) * (b[1] - a[1])))
    items.append(pt_item("mp-di-5", rf"The point $P$ divides the segment $AB$ in the ratio $AP:PB=2:3$, with $A{P2(a)}$ and $B{P2(b)}$. Find $P$.", pt,
                         rf"$\overrightarrow{{AP}}=\dfrac25\overrightarrow{{AB}}$, so $P=A+\dfrac25{vec_tex(vec(a, b))}={P2(pt)}$.", ["$P$ is two fifths of the way from $A$ to $B$."]))
    A, B, C = (0, 0), (6, 0), (3, 4)
    per = rad(dist(A, B) + dist(B, C) + dist(C, A))
    items.append(num_item("mp-di-6", rf"Find the perimeter of the triangle $A{P2(A)}$, $B{P2(B)}$, $C{P2(C)}$. The unit is lu: give the number only.", per,
                          r"The sides are $AB=6$, $BC=\sqrt{9+16}=5$ and $CA=5$, so the perimeter is $16$.", ["Add the three side lengths."]))
    return items


def angle_items() -> list[dict]:
    items = []
    p, q = (1, 2), (4, 11)
    slope = sp.Rational(q[1] - p[1], q[0] - p[0])
    items.append(num_item("mp-an-1", rf"Find the slope of the line through $P{P2(p)}$ and $Q{P2(q)}$.", slope, rf"$m=\dfrac{{11-2}}{{4-1}}={tex(slope)}$.", ["$m=\\dfrac{y_2-y_1}{x_2-x_1}$."], answer_type="number"))
    m1, m2 = 1, 3
    t = sp.Rational(abs(m2 - m1), 1 + m1 * m2)
    items.append(num_item("mp-an-2", r"Find $\tan\theta$ for the acute angle $\theta$ between the lines $y=x$ and $y=3x$.", t, r"$\tan\theta=\left|\dfrac{m_2-m_1}{1+m_1m_2}\right|=\dfrac{2}{4}=\dfrac12$.", ["Use $\\tan\\theta=\\left|\\dfrac{m_2-m_1}{1+m_1m_2}\\right|$."], answer_type="number"))
    items.append(num_item("mp-an-3", r"Find the acute angle between the lines $x-y=0$ and $y=0$.", sp.pi / 4, r"The first line has slope $1$ and the second slope $0$, so $\tan\theta=1$ and $\theta=\dfrac\pi4$.", ["The second line is the $x$-axis."]))
    L, pt = (3, -1, 1), (2, 3)
    par = norm_line(L[0], L[1], -(L[0] * pt[0] + L[1] * pt[1]))
    items.append(line_item("mp-an-4", rf"Find the line through $P{P2(pt)}$ parallel to ${line_tex(L)}$.", par, r"Parallel lines have the same normal vector $(3,-1)$, so the line is $3(x-2)-(y-3)=0$.", ["Keep the normal vector $(a,b)$."]))
    L, pt = (2, 3, -5), (1, -2)
    perp = line_normal((3, -2), pt)
    assert eval_line(perp, pt) == 0
    items.append(line_item("mp-an-5", rf"Find the line through $P{P2(pt)}$ perpendicular to ${line_tex(L)}$.", perp, r"The normal vector of the given line, $(2,3)$, becomes the direction vector of the new line; its normal vector is $(3,-2)$.", ["Swap the coefficients and change one sign to get the normal vector."]))
    k = sp.Symbol("k")
    kval = sp.solve(k * 6 + 2 * (k - 1), k)[0]
    items.append(ex("mp-an-6", r"For which $k$ are the lines $kx+2y-1=0$ and $6x+(k-1)y+4=0$ perpendicular?", "number", eng(kval), hints=[r"The normal vectors must be orthogonal: $6k+2(k-1)=0$."],
                    solution=rf"$6k+2(k-1)=0$ gives $8k=2$, so $k={tex(kval)}$."))
    return items


def dpl_items() -> list[dict]:
    items = []
    L, p = (4, 3, -5), (3, -2)
    d = dist_point_line(p, L)
    items.append(num_item("mp-dl-1", rf"The distance from $P{P2(p)}$ to the line ${line_tex(L)}$. The unit is lu: give the number only.", d, r"The norm of the normal vector is $5$ (since $4^2+3^2=25$), so the distance is $\dfrac{|4\cdot3+3\cdot(-2)-5|}{5}=\dfrac15$.", ["$d=\\dfrac{|ax_0+by_0+c|}{\\sqrt{a^2+b^2}}$."]))
    L1, L2 = (3, 4, -10), (3, 4, 5)
    d = rad(sp.Abs(L1[2] - L2[2]) / sp.sqrt(L1[0] ** 2 + L1[1] ** 2))
    items.append(num_item("mp-dl-2", rf"The distance between the parallel lines ${line_tex(L1)}$ and ${line_tex(L2)}$. The unit is lu: give the number only.", d, r"The norm of the normal vector is $5$ (since $3^2+4^2=25$), so the distance is $\dfrac{|-10-5|}{5}=3$.", ["Use a point of one line, or the formula $\\dfrac{|c_1-c_2|}{\\sqrt{a^2+b^2}}$."]))
    L, p = (1, 1, -6), (1, 2)
    t = -eval_line(L, p) / (L[0] ** 2 + L[1] ** 2)
    foot = (rad(p[0] + t * L[0]), rad(p[1] + t * L[1]))
    assert eval_line(L, foot) == 0
    items.append(pt_item("mp-dl-3", rf"Find the foot of the perpendicular from $P{P2(p)}$ to the line ${line_tex(L)}$.", foot, r"The foot is $P-\dfrac{ax_0+by_0+c}{a^2+b^2}(a,b)$, and it lies on the line.", ["Move from $P$ along the normal vector until you reach the line."]))
    refl = (rad(p[0] + 2 * t * L[0]), rad(p[1] + 2 * t * L[1]))
    items.append(pt_item("mp-dl-4", rf"Find the reflection of $P{P2(p)}$ in the line ${line_tex(L)}$.", refl, rf"The foot of the perpendicular is ${P2(foot)}$, and it is the midpoint of $P$ and its reflection.", ["The foot is the midpoint of $P$ and its image."]))
    L = (5, -12, 26)
    d = dist_point_line((0, 0), L)
    items.append(num_item("mp-dl-5", rf"The distance from the origin to the line ${line_tex(L)}$. The unit is lu: give the number only.", d, r"The norm of the normal vector is $13$ (since $5^2+12^2=169$), so the distance is $\dfrac{26}{13}=2$.", ["Put $x_0=y_0=0$ in the formula."]))
    return items


def intersection_items() -> list[dict]:
    items = []
    pairs = (((2, 1, -7), (1, -1, -2)), ((3, -2, 0), (1, 1, -5)), ((1, 2, -4), (2, -1, -3)))
    for n, (L1, L2) in enumerate(pairs, 1):
        p = meet(L1, L2)
        assert eval_line(L1, p) == 0 and eval_line(L2, p) == 0
        items.append(pt_item(f"mp-in-{n}", rf"Find the intersection of ${line_tex(L1)}$ and ${line_tex(L2)}$.", p, rf"Solving the two equations together gives the point ${P2(p)}$, which satisfies both.", ["Solve the system of the two equations."]))
    k = sp.Symbol("k")
    L1, L2 = (1, 1, -4), (2, -1, -2)
    p = meet(L1, L2)
    kval = sp.solve(3 * p[0] + k * p[1] - 9, k)[0]
    items.append(ex("mp-in-4", rf"For which $k$ are the lines $x+y-4=0$, $2x-y-2=0$ and $3x+ky-9=0$ concurrent?", "number", eng(kval), hints=[r"Find the intersection of the first two lines, then put it in the third."],
                    solution=rf"The first two lines meet at ${P2(p)}$. Putting it in the third: $3\cdot2+k\cdot2-9=0$, so $k={tex(kval)}$."))
    L1, L2 = (1, -1, 0), (1, 1, -6)
    p = meet(L1, L2)
    kval = sp.solve(2 * p[0] + k * p[1] - 10, k)[0]
    items.append(ex("mp-in-5", r"For which $k$ are the lines $x-y=0$, $x+y-6=0$ and $2x+ky-10=0$ concurrent?", "number", eng(kval), hints=[r"The first two lines meet at $(3,3)$."],
                    solution=rf"They meet at $(3,3)$; then $6+3k-10=0$ gives $k={tex(kval)}$."))
    L1, L2, pt = (1, 1, -4), (2, -1, -2), (0, 0)
    lam = sp.Symbol("lam")
    eq = sp.expand((L1[0] * x + L1[1] * y + L1[2]) + lam * (L2[0] * x + L2[1] * y + L2[2]))
    lv = sp.solve(eq.subs({x: pt[0], y: pt[1]}), lam)[0]
    res = sp.expand(eq.subs(lam, lv))
    c = [res.coeff(x), res.coeff(y), res.subs({x: 0, y: 0})]
    L = norm_line(*c)
    items.append(line_item("mp-in-6", rf"Find the line through the origin and the intersection of ${line_tex(L1)}$ and ${line_tex(L2)}$.", L, r"Use the pencil $(x+y-4)+\lambda(2x-y-2)=0$ and choose $\lambda$ so that the origin satisfies it.", ["The lines through the intersection form the pencil $L_1+\\lambda L_2=0$."]))
    L1, L2, pt = (1, -1, 1), (1, 1, -5), (3, 0)
    eq = sp.expand((L1[0] * x + L1[1] * y + L1[2]) + lam * (L2[0] * x + L2[1] * y + L2[2]))
    lv = sp.solve(eq.subs({x: pt[0], y: pt[1]}), lam)[0]
    res = sp.expand(eq.subs(lam, lv))
    L = norm_line(res.coeff(x), res.coeff(y), res.subs({x: 0, y: 0}))
    assert eval_line(L, pt) == 0
    items.append(line_item("mp-in-7", rf"Find the line through $P{P2(pt)}$ and the intersection of ${line_tex(L1)}$ and ${line_tex(L2)}$.", L, r"Use the pencil $L_1+\lambda L_2=0$ and choose $\lambda$ so that $P$ satisfies it.", ["Substitute the coordinates of $P$ to find $\\lambda$."]))
    items.append(mc("mp-in-8", r"The lines $2x+4y-6=0$ and $x+2y-3=0$ are", ["parallel and different", "the same line", "perpendicular", "intersecting at one point"], 1, r"Compare the coefficients.", r"The first equation is twice the second: the two equations describe the same line."))
    items.append(mc("mp-in-9", r"The lines $2x+3y-1=0$ and $4x+6y+5=0$ are", ["parallel and different", "the same line", "perpendicular", "intersecting at one point"], 0, r"The coefficients of $x$ and $y$ are proportional.", r"$(4,6)=2(2,3)$ but the constants do not match ($5\ne2\cdot(-1)$): the lines are parallel and different, so they never meet."))
    return items


# --- unit 2 -----------------------------------------------------------------------------------------------------------------------------
def triangle_items() -> dict[str, list[dict]]:
    T = Tri((-2, 1), (6, 1), (2, 7))
    out = {"l02-medians-and-centroid": [], "l03-altitudes-and-orthocenter": [], "l04-angle-bisectors-and-incenter": [], "l07-euler-line-and-complete-study": []}
    stm = rf"the triangle $A{P2(T.A)}$, $B{P2(T.B)}$, $C{P2(T.C)}$"
    M, L, lm = T.median("A")
    out["l02-medians-and-centroid"].append(num_item("mp-tm-1", rf"In {stm}, find the length of the median from $A$. The unit is lu: give the number only.", lm,
                                                   rf"The midpoint of $BC$ is ${P2(M)}$, so $m_a=\norm{{\overrightarrow{{AM_a}}}}={tex(lm)}$.", ["The median joins $A$ to the midpoint of $BC$."]))
    F, La, ha = T.altitude("B")
    out["l03-altitudes-and-orthocenter"].append(pt_item("mp-ta-1", rf"In {stm}, find the orthocenter $H$.", T.H, rf"Two altitudes meet at ${P2(T.H)}$ (also $H=A+B+C-2O$ with $O={P2(T.O)}$).", ["Intersect two altitudes."]))
    out["l03-altitudes-and-orthocenter"].append(num_item("mp-ta-2", rf"In {stm}, find the length of the altitude from $B$. The unit is lu: give the number only.", ha, rf"$h_b=\dfrac{{2S}}{{b}}={tex(ha)}$ with $S={tex(T.K)}$.", ["Use $h=\\dfrac{2S}{\\text{side}}$."]))
    out["l04-angle-bisectors-and-incenter"].append(num_item("mp-tb-1", rf"In {stm}, find the inradius $r$. The unit is lu: give the number only.", T.r, rf"$S={tex(T.K)}$ and $s={tex(T.s)}$, so $r=\dfrac{{S}}{{s}}={tex(T.r)}$.", ["$r=\\dfrac{S}{s}$."]))
    e = out["l07-euler-line-and-complete-study"]
    e.append(pt_item("mp-te-1", rf"In {stm}, find the circumcenter $O$.", T.O, rf"$O$ is at equal distance from the three vertices: $O={P2(T.O)}$ and $R={tex(T.Rc)}$.", ["Intersect two perpendicular bisectors."]))
    e.append(num_item("mp-te-2", rf"In {stm}, find the circumradius $R$. The unit is lu: give the number only.", T.Rc, rf"$R=\dfrac{{abc}}{{4S}}={tex(T.Rc)}$.", ["$R=\\dfrac{abc}{4S}$."]))
    e.append(pt_item("mp-te-3", rf"In {stm}, find the centroid $G$.", T.G, rf"$G=\dfrac{{A+B+C}}3={P2(T.G)}$.", ["Average the vertices."]))
    e.append(num_item("mp-te-4", rf"In {stm}, find the distance $OH$ between the circumcenter and the orthocenter. The unit is lu: give the number only.", dist(T.O, T.H),
                      rf"$O={P2(T.O)}$ and $H={P2(T.H)}$, so $OH={tex(dist(T.O, T.H))}$; it is three times $OG$ (Euler line).", ["Find $O$ and $H$ first."]))
    assert rad(dist(T.O, T.H) - 3 * dist(T.O, T.G)) == 0
    if T.O != T.G:
        EL = line_through(T.O, T.G)
        assert eval_line(EL, T.H) == 0
        e.append(line_item("mp-te-5", rf"In {stm}, find the equation of the Euler line (through $O$, $G$ and $H$).", EL, rf"The line through $O={P2(T.O)}$ and $G={P2(T.G)}$ also contains $H$.", ["The Euler line passes through $O$ and $G$."]))
    e.append(num_item("mp-te-6", rf"In {stm}, find $OI^2$ where $I$ is the incenter, using Euler's relation $OI^2=R^2-2Rr$. The unit is squ: give the number only.", rad(T.Rc**2 - 2 * T.Rc * T.r),
                      rf"$R={tex(T.Rc)}$ and $r={tex(T.r)}$, so $OI^2=R^2-2Rr={tex(rad(T.Rc**2 - 2 * T.Rc * T.r))}$.", ["$OI^2=R^2-2Rr$."]))
    assert rad(dist(T.O, T.I) ** 2 - (T.Rc**2 - 2 * T.Rc * T.r)) == 0
    return out


# --- unit 3: the circle ------------------------------------------------------------------------------------------------------------------
def circle_poly(h, k, r2) -> sp.Expr:
    return sp.expand((x - h) ** 2 + (y - k) ** 2 - r2)


def circle_eq(h, k, r2) -> str:
    return f"{eng(circle_poly(h, k, r2))}=0"


def circle_tex(h, k, r2) -> str:
    return f"{tex(circle_poly(h, k, r2))}=0"


def circle_items() -> list[dict]:
    items = []
    h, k, r_ = 2, -3, 4
    items.append(ex("mp-ci-1", rf"Write the equation of the circle with center $\left({h},{k}\right)$ and radius ${r_}$ in the form $x^2+y^2+Dx+Ey+F=0$.", "equation", circle_eq(h, k, r_**2), coordinates=["x", "y"],
                    hints=[r"Start from $(x-h)^2+(y-k)^2=r^2$ and expand."], solution=rf"$(x-2)^2+(y+3)^2=16$ expands to ${circle_tex(h, k, r_**2)}$."))
    D, E, F = -6, 4, -12
    h2, k2 = sp.Rational(-D, 2), sp.Rational(-E, 2)
    r2 = h2**2 + k2**2 - F
    items.append(ex("mp-ci-2", rf"Find the center of the circle $x^2+y^2{D:+d}x{E:+d}y{F:+d}=0$.", "vector", pt_eng((h2, k2)), hints=[r"Complete the squares in $x$ and in $y$."],
                    solution=rf"$(x-3)^2+(y+2)^2={tex(r2)}$: the center is ${P2((h2, k2))}$ and the radius is ${tex(sp.sqrt(r2))}$."))
    items.append(num_item("mp-ci-3", rf"Find the radius of the circle $x^2+y^2{D:+d}x{E:+d}y{F:+d}=0$. The unit is lu: give the number only.", sp.sqrt(r2), rf"$r^2=h^2+k^2-F={tex(r2)}$, so $r={tex(sp.sqrt(r2))}$.", ["Complete the squares: $r^2=h^2+k^2-F$."]))
    A, B, C = (0, 0), (4, 0), (0, 6)
    sol_ = sp.solve([(a[0] ** 2 + a[1] ** 2) + sp.Symbol("D") * a[0] + sp.Symbol("E") * a[1] + sp.Symbol("F") for a in (A, B, C)], sp.symbols("D E F"), dict=True)[0]
    Dd, Ee, Ff = (sol_[sp.Symbol(c)] for c in "DEF")
    items.append(ex("mp-ci-4", rf"Find the equation of the circle through $A{P2(A)}$, $B{P2(B)}$ and $C{P2(C)}$.", "equation", f"{eng(sp.expand(x**2 + y**2 + Dd * x + Ee * y + Ff))}=0", coordinates=["x", "y"],
                    hints=[r"Put the three points in $x^2+y^2+Dx+Ey+F=0$ and solve for $D$, $E$, $F$."], solution=rf"The three conditions give $D={tex(Dd)}$, $E={tex(Ee)}$, $F={tex(Ff)}$."))
    return items


def tangent_items() -> list[dict]:
    items = []
    h, k, r2, pt = 1, 2, 25, (4, 6)
    assert (pt[0] - h) ** 2 + (pt[1] - k) ** 2 == r2
    n = (pt[0] - h, pt[1] - k)
    L = norm_line(n[0], n[1], -(n[0] * pt[0] + n[1] * pt[1]))
    items.append(line_item("mp-ct-1", rf"Find the tangent to the circle ${circle_tex(h, k, r2)}$ at the point $P{P2(pt)}$.", L, r"The tangent is perpendicular to the radius $\overrightarrow{CP}=(3,4)$.", ["Use the radius as the normal vector of the tangent."]))
    c, r_, pt = (0, 0), 5, (13, 0)
    t = sp.sqrt((pt[0] - c[0]) ** 2 + (pt[1] - c[1]) ** 2 - r_**2)
    items.append(num_item("mp-ct-2", rf"Find the length of the tangent segment from $P{P2(pt)}$ to the circle $x^2+y^2=25$. The unit is lu: give the number only.", t, r"$t^2=OP^2-r^2=169-25=144$, so $t=12$.", ["$t^2=d^2-r^2$."]))
    pw = pt[0] ** 2 + pt[1] ** 2 - 25
    items.append(num_item("mp-ct-3", rf"Find the power of $P{P2(pt)}$ with respect to the circle $x^2+y^2=25$.", pw, r"The power is $OP^2-r^2=144$.", ["Power $=d^2-r^2$."], answer_type="number"))
    L = (3, 4, -25)
    d = dist_point_line((0, 0), L)
    items.append(mc("mp-ct-4", rf"The line ${line_tex(L)}$ and the circle $x^2+y^2=25$:", ["do not meet", "are tangent", "meet at two points"], 1, r"Compare the distance from the center to the line with the radius.",
                    rf"The distance from $(0,0)$ to the line is $\dfrac{{25}}{{5}}={tex(d)}$, equal to the radius: the line is tangent."))
    L = (1, 1, -2)
    d = dist_point_line((0, 0), L)
    chord = rad(2 * sp.sqrt(25 - d**2))
    items.append(num_item("mp-ct-5", rf"Find the length of the chord cut from the circle $x^2+y^2=25$ by the line ${line_tex(L)}$. The unit is lu: give the number only.", chord,
                          rf"The distance from the center to the line is ${tex(d)}$, so the chord has length $2\sqrt{{25-{tex(d**2)}}}={tex(chord)}$.", ["Half the chord, the distance and the radius form a right triangle."]))
    sols = sp.solve([x**2 + y**2 - 25, x + y - 1], [x, y], dict=True)
    pts = sorted([(rad(s_[x]), rad(s_[y])) for s_ in sols], key=lambda p: float(p[0]))
    items.append(ex("mp-ct-6", r"Find the points where the line $x+y=1$ meets the circle $x^2+y^2=25$.", "points", ", ".join(pt_eng(p) for p in pts), hints=[r"Put $y=1-x$ in the circle."],
                    solution=rf"$x^2+(1-x)^2=25$ gives $x^2-x-12=0$, so $x=4$ or $x=-3$: the points are ${P2(pts[0])}$ and ${P2(pts[1])}$."))
    pt = (0, 10)
    items.append(ex("mp-ct-7", r"How many tangents can be drawn from the point $(0,10)$ to the circle $x^2+y^2=25$?", "number", "2", hints=[r"Is the point outside the circle?"],
                    solution=r"$0+100>25$: the point is outside, so there are two tangents."))
    assert pt is not None
    return items


def two_circles_items() -> list[dict]:
    items = []
    c1, c2 = (0, 0, 9), (6, 0, 4)
    rad_axis = sp.expand((circle_poly(*c1)) - (circle_poly(*c2)))
    coeffs = [rad_axis.coeff(x), rad_axis.coeff(y), rad_axis.subs({x: 0, y: 0})]
    L = norm_line(*coeffs)
    items.append(line_item("mp-tc-1", rf"Find the radical axis of the circles ${circle_tex(*c1)}$ and ${circle_tex(*c2)}$.", L, r"Subtract the two equations: the terms in $x^2$ and $y^2$ cancel and a line remains.", ["Subtract one equation from the other."]))
    d = rad(sp.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2))
    items.append(num_item("mp-tc-2", r"Find the distance between the centers of the circles $x^2+y^2=9$ and $(x-6)^2+y^2=4$. The unit is lu: give the number only.", d, r"The centers are $(0,0)$ and $(6,0)$: the distance is $6$.", ["Read the centers from the equations."]))
    cases = (
        ("(x-6)^2+y^2=4", 6, 3, 2, "external", 3),
        ("(x-1)^2+y^2=1", 1, 3, 1, "internal", 0),
        ("(x-5)^2+y^2=4", 5, 3, 2, "tangent externally", 2),
        ("x^2+y^2=1", 0, 3, 1, "one inside the other", 0),
    )
    names = ["They are separate (outside each other)", "They are tangent internally", "They are tangent externally", "One circle is inside the other without touching", "They intersect at two points"]

    def rel(dd: int, r1: int, r2: int) -> int:
        if dd > r1 + r2:
            return 0
        if dd == r1 + r2:
            return 2
        if dd < abs(r1 - r2):
            return 3
        if dd == abs(r1 - r2):
            return 1
        return 4

    for n, (eqn, dd, r1, r2, _, _) in enumerate(cases, 3):
        items.append(mc(f"mp-tc-{n}", rf"How are the circles $x^2+y^2=9$ and ${eqn.replace('^', '^')}$ placed? (the second has center at distance ${dd}$ and radius ${r2}$)", names, rel(dd, r1, r2),
                        r"Compare the distance between the centers with $r_1+r_2$ and $|r_1-r_2|$.", rf"$d={dd}$, $r_1+r_2={r1 + r2}$ and $|r_1-r_2|={abs(r1 - r2)}$: {names[rel(dd, r1, r2)].lower()}."))
    c1, c2 = (0, 0, 25), (7, 0, 25)
    ax = sp.expand(circle_poly(*c1) - circle_poly(*c2))
    xr = sp.solve(ax, x)[0]
    yv = sp.sqrt(25 - xr**2)
    chord = rad(2 * yv)
    items.append(num_item("mp-tc-7", r"Find the length of the common chord of the circles $x^2+y^2=25$ and $(x-7)^2+y^2=25$. The unit is lu: give the number only.", chord,
                          rf"The radical axis is $x={tex(xr)}$; there $y^2=25-{tex(xr**2)}$, so $y=\pm{tex(yv)}$ and the chord has length ${tex(chord)}$.", ["The common chord lies on the radical axis."]))
    pw1 = 9 + 0 - 9
    items.append(num_item("mp-tc-8", r"Find the power of the point $P(3,0)$ with respect to the circle $x^2+y^2=9$.", sp.Integer(pw1), r"The point is on the circle, so its power is $0$.", ["Power $=OP^2-r^2$."], answer_type="number"))
    items.append(ex("mp-tc-9", r"Is the point $(4,0)$ on the radical axis of $x^2+y^2=16$ and $(x-8)^2+y^2=16$?", "multiple_choice", "1", choices=[{"text": "Yes", "value": "1"}, {"text": "No", "value": "2"}], correctIndex=0,
                    hints=[r"Compute the power of the point with respect to each circle."], solution=r"The powers are $16-16=0$ and $16-16=0$: equal, so the point is on the radical axis."))
    return items


@with_units
def register() -> None:
    plain = [
        (U1, "l01-distance-and-division", "more-distance", "More practice: distance, midpoint and division.", distance_items()),
        (U1, "l03-angle-between-lines", "more-angles", "More practice: angles, parallel and perpendicular lines.", angle_items()),
        (U1, "l04-distances", "more-distance-line", "More practice: distance from a point to a line.", dpl_items()),
        (U1, "l05-intersection-of-lines", "more-intersections", "More practice: intersections, concurrent lines and pencils.", intersection_items()),
        (U3, "l01-equation-of-a-circle", "more-circles", "More practice: the equation of a circle.", circle_items()),
        (U3, "l02-tangents-and-power", "more-tangents", "More practice: tangents and the power of a point.", tangent_items()),
        (U3, "l03-two-circles", "more-two-circles", "More practice: two circles and the radical axis.", two_circles_items()),
    ]
    for unit, lesson, sid, task, items in plain:
        add_extra(f"{unit}/{lesson}", exset_plain(sid, task, items, format=FMT), SCRIPT)
    for lesson, items in triangle_items().items():
        add_extra(f"{U2}/{lesson}", exset_plain("more-triangle", "More practice: a new triangle.", items, format=FMT), SCRIPT)
