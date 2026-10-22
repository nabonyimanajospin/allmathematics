"""Exercises of Course 1, Module 1: norm, direction cosines and the products of vectors."""

from __future__ import annotations

import sympy as sp
from geo_m03 import cross, dot, item_num, item_pt, norm, pt3_eng, pt3_tex, rad, sub, vec3_tex
from toolkit import eng, ex, exset_plain as exset, tex, write_exercises

BASE = "geo/m01-vectors"
U1 = f"{BASE}/u01-vectors-and-algebra"
U2 = f"{BASE}/u02-products-of-vectors"
R = sp.Rational
FMT = "Type a vector as `(a, b, c)`, a number or an exact expression such as `sqrt(7)/4`."


def tuple3(v):
    return tuple(sp.sympify(c) for c in v)


def scale(v, k):
    return tuple(rad(sp.sympify(k) * c) for c in v)


def add(u, v):
    return tuple(rad(a + b) for a, b in zip(u, v, strict=True))


def vt(v) -> str:
    return vec3_tex(v)


def u1l4() -> list[dict]:
    items = []
    for n, v in enumerate(((2, -3, 6), (1, -2, 2), (4, 3, 12), (2, 2, 1), (0, 5, 12)), 1):
        items.append(item_num(f"nm-{n:02d}", rf"The norm of $\vec v={vt(v)}$.", norm(v),
                              rf"$\norm{{\vec v}}=\sqrt{{{tex(v[0]**2)}+{tex(v[1]**2)}+{tex(v[2]**2)}}}={tex(norm(v))}$.", ["Add the squares of the components and take the square root."]))
    for n, v in enumerate(((3, 4, 0), (2, -2, 1), (1, 2, 2)), 6):
        nv = norm(v)
        u = tuple(rad(c / nv) for c in v)
        items.append(item_pt(f"nm-{n:02d}", rf"The unit vector in the direction of $\vec v={vt(v)}$.", u,
                             rf"$\norm{{\vec v}}={tex(nv)}$, so $\hat v=\dfrac{{\vec v}}{{{tex(nv)}}}={vt(u)}$.", ["Divide $\\vec v$ by its norm."]))
    v, L = (2, -1, 2), 12
    w = tuple(rad(L * c / norm(v)) for c in v)
    items.append(item_pt("nm-09", rf"A vector of length ${L}$ in the direction of $\vec v={vt(v)}$.", w,
                         rf"$\norm{{\vec v}}=3$, so the vector is ${L}\,\hat v={vt(w)}$.", ["Multiply the unit vector by the length."]))
    v = (2, -3, 6)
    items.append(ex("nm-10", rf"The direction cosines $(\cos\alpha,\cos\beta,\cos\gamma)$ of $\vec v={vt(v)}$.", "vector", pt3_eng(tuple(rad(c / norm(v)) for c in v)),
                    hints=["Divide each component by the norm."], solution=r"$\norm{\vec v}=7$, so the direction cosines are $\dfrac27,-\dfrac37,\dfrac67$."))
    items.append(ex("nm-11", r"A vector has $\cos\alpha=\dfrac12$ and $\cos\beta=\dfrac12$, and its angle $\gamma$ with the $z$-axis is acute. Find $\cos\gamma$.", "expression", "sqrt(2)/2",
                    hints=["$\\cos^2\\alpha+\\cos^2\\beta+\\cos^2\\gamma=1$."], solution=r"$\cos^2\gamma=1-\dfrac14-\dfrac14=\dfrac12$, so $\cos\gamma=\dfrac{\sqrt2}2$ (positive, since $\gamma$ is acute)."))
    items.append(item_num("nm-12", r"The angle between the vector $(1,1,\sqrt2)$ and the $z$-axis.", sp.pi / 4,
                          r"$\norm{(1,1,\sqrt2)}=2$, so $\cos\gamma=\dfrac{\sqrt2}{2}$ and $\gamma=\dfrac\pi4$.", ["$\\cos\\gamma$ is the third component divided by the norm."]))
    return items


def u2l1() -> list[dict]:
    items = []
    pairs = (((1, -2, 3), (4, 5, 6)), ((2, 0, -1), (3, 5, 4)), ((1, 2, 2), (2, -1, 2)), ((3, -1, 2), (1, 4, 2)))
    for n, (u, v) in enumerate(pairs, 1):
        items.append(item_num(f"dp-{n:02d}", rf"$\dotp{{\vec u}}{{\vec v}}$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", dot(u, v),
                              rf"$\dotp{{\vec u}}{{\vec v}}={tex(u[0]*v[0])}+{par(u[1]*v[1])}+{par(u[2]*v[2])}={tex(dot(u, v))}$.", ["Multiply the matching components and add."]))
    for n, (u, v) in enumerate((((1, 2, 2), (2, -1, 2)), ((1, 1, 0), (0, 1, 1)), ((1, 0, 0), (1, 1, 0)), ((2, 1, -2), (1, 2, 2))), 5):
        c = rad(dot(u, v) / (norm(u) * norm(v)))
        items.append(item_num(f"dp-{n:02d}", rf"$\cos\theta$ for the angle between $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", c,
                              rf"$\dotp{{\vec u}}{{\vec v}}={tex(dot(u, v))}$, $\norm{{\vec u}}={tex(norm(u))}$, $\norm{{\vec v}}={tex(norm(v))}$, so $\cos\theta={tex(c)}$.", ["$\\cos\\theta=\\dfrac{\\dotp{\\vec u}{\\vec v}}{\\norm{\\vec u}\\norm{\\vec v}}$."]))
    items.append(ex("dp-09", r"The angle between $\vec u=(1,1,0)$ and $\vec v=(0,1,1)$.", "expression", "pi/3", hints=["Compute $\\cos\\theta$ first."],
                    solution=r"$\cos\theta=\dfrac{1}{\sqrt2\cdot\sqrt2}=\dfrac12$, so $\theta=\dfrac\pi3$."))
    items.append(ex("dp-10", r"For which $k$ are $(k,2,-1)$ and $(3,k,4)$ orthogonal?", "number", "4/5", hints=["The dot product must be $0$."], solution=r"$3k+2k-4=0$, so $k=\dfrac45$."))
    items.append(ex("dp-11", r"For which $k$ are $(1,k,2)$ and $(k,-3,1)$ orthogonal?", "number", "1", hints=["$k-3k+2=0$."], solution=r"$k+k\cdot(-3)+2\cdot1=0$ gives $-2k+2=0$, so $k=1$."))
    items.append(ex("dp-12", r"Find a vector of the plane orthogonal to $\vec u=(3,4)$ with norm $10$ (the one with positive first component).", "vector", "(8, -6)",
                    hints=["Swap the components and change one sign, then scale."], solution=r"A perpendicular vector is $(4,-3)$, of norm $5$; doubling it gives $(8,-6)$."))
    return items


def par(v) -> str:
    v = sp.sympify(v)
    return tex(v) if v.is_nonnegative else rf"\left({tex(v)}\right)"


def u2l2() -> list[dict]:
    items = []
    for n, (u, v) in enumerate((((3, 4, 5), (1, 2, 2)), ((2, -1, 2), (0, 3, 4)), ((4, 2, 0), (1, 1, 0)), ((1, 2, 3), (2, 2, 1))), 1):
        t = rad(dot(u, v) / dot(v, v))
        p = scale(v, t)
        items.append(item_pt(f"pr-{n:02d}", rf"The orthogonal projection of $\vec u={vt(u)}$ on $\vec v={vt(v)}$.", p,
                             rf"$\dotp{{\vec u}}{{\vec v}}={tex(dot(u,v))}$ and $\norm{{\vec v}}^2={tex(dot(v,v))}$, so the projection is ${tex(t)}\,\vec v={vt(p)}$.", ["$\\dfrac{\\dotp{\\vec u}{\\vec v}}{\\norm{\\vec v}^2}\\vec v$."]))
    for n, (u, v) in enumerate((((2, -1, 2), (0, 3, 4)), ((1, 5, 2), (2, -2, 1))), 5):
        c = rad(dot(u, v) / norm(v))
        items.append(item_num(f"pr-{n:02d}", rf"The scalar component of $\vec u={vt(u)}$ along $\vec v={vt(v)}$.", c,
                              rf"$\dfrac{{\dotp{{\vec u}}{{\vec v}}}}{{\norm{{\vec v}}}}$ with $\dotp{{\vec u}}{{\vec v}}={tex(dot(u,v))}$ and $\norm{{\vec v}}={tex(norm(v))}$ is ${tex(c)}$.", ["Divide the dot product by the norm of $\\vec v$."]))
    u, v = (3, 4, 5), (1, 2, 2)
    t = rad(dot(u, v) / dot(v, v))
    perp = tuple(rad(a - t * b) for a, b in zip(u, v, strict=True))
    items.append(item_pt("pr-07", rf"The part of $\vec u={vt(u)}$ orthogonal to $\vec v={vt(v)}$ (that is $\vec u$ minus its projection on $\vec v$).", perp,
                         rf"The projection is ${tex(t)}\vec v={vt(scale(v,t))}$, so the orthogonal part is ${vt(perp)}$.", ["Subtract the projection from $\\vec u$."]))
    u, v = (1, 2, 3), (3, -1, 2)
    items.append(item_num("pr-08", rf"The product $\norm{{\vec u}}\norm{{\vec v}}$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$ (the upper bound of Cauchy–Schwarz).", norm(u) * norm(v),
                          rf"$\sqrt{{14}}\cdot\sqrt{{14}}=14$; compare with $|\dotp{{\vec u}}{{\vec v}}|={tex(sp.Abs(dot(u,v)))}\le14$.", ["Compute the two norms."]))
    items.append(item_num("pr-09", r"For $\vec u=(3,4)$ and $\vec v=(5,12)$, the norm $\norm{\vec u+\vec v}$.", rad(sp.sqrt(8**2 + 16**2)),
                          r"$\vec u+\vec v=(8,16)$, with norm $\sqrt{64+256}=8\sqrt5$. It is at most $5+13=18$, by the triangle inequality.", ["Add the vectors first."]))
    return items


def u2l3() -> list[dict]:
    items = []
    pairs = (((1, 2, 3), (4, 5, 6)), ((2, -1, 3), (1, 4, -2)), ((0, 1, 2), (3, 0, 1)), ((1, 0, 0), (0, 1, 0)), ((3, -2, 1), (2, 5, -1)), ((1, 1, 1), (1, -1, 2)))
    for n, (u, v) in enumerate(pairs, 1):
        c = cross(u, v)
        items.append(item_pt(f"cp-{n:02d}", rf"$\crossp{{\vec u}}{{\vec v}}$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", c,
                             rf"The components are $\left({tex(u[1]*v[2])}-{par(u[2]*v[1])},\ {tex(u[2]*v[0])}-{par(u[0]*v[2])},\ {tex(u[0]*v[1])}-{par(u[1]*v[0])}\right)={vt(c)}$.",
                             ["Use the determinant with $\\vec i,\\vec j,\\vec k$ in the first row; check with a dot product."]))
    u, v = (1, 2, 3), (4, 5, 6)
    items.append(item_pt("cp-07", rf"$\crossp{{\vec v}}{{\vec u}}$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", cross(v, u),
                         rf"Swapping the factors changes the sign: $\crossp{{\vec v}}{{\vec u}}=-\crossp{{\vec u}}{{\vec v}}={vt(cross(v,u))}$.", ["Compare with the previous exercise."]))
    u, v = (2, -1, 3), (1, 4, -2)
    items.append(ex("cp-08", rf"A direction vector orthogonal to both $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", "direction", pt3_eng(cross(u, v)),
                    hints=["Use the cross product."], solution=rf"$\crossp{{\vec u}}{{\vec v}}={vt(cross(u,v))}$; every non-zero multiple of it is also orthogonal to both."))
    u, v = (2, -1, 3), (1, 4, -2)
    lhs = rad(norm(u) ** 2 * norm(v) ** 2 - dot(u, v) ** 2)
    items.append(item_num("cp-09", rf"$\norm{{\crossp{{\vec u}}{{\vec v}}}}^2$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$, using Lagrange's identity $\norm{{\vec u}}^2\norm{{\vec v}}^2-\dotp{{\vec u}}{{\vec v}}^2$.", lhs,
                          rf"$14\cdot21-(-8)^2=230$.", ["Compute $\\norm{\\vec u}^2$, $\\norm{\\vec v}^2$ and $\\dotp{\\vec u}{\\vec v}$."], answer_type="number"))
    return items


def u2l4() -> list[dict]:
    items = []
    for n, (u, v) in enumerate((((1, 2, 2), (2, 0, 1)), ((3, 0, 1), (1, 2, 0)), ((2, 1, 0), (0, 1, 3))), 1):
        c = cross(u, v)
        items.append(item_num(f"ar-{n:02d}", rf"The area of the parallelogram built on $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", norm(c),
                              rf"$\crossp{{\vec u}}{{\vec v}}={vt(c)}$, with norm ${tex(norm(c))}$.", ["The norm of the cross product."]))
    for n, (A, B, C) in enumerate((((1, 0, 2), (3, 1, 0), (2, 2, 3)), ((0, 0, 0), (3, 0, 0), (0, 4, 0)), ((1, 1, 1), (2, 3, 1), (4, 1, 2)), ((-1, 2, 0), (1, 1, 3), (0, 0, 1))), 4):
        c = cross(sub(A, B), sub(A, C))
        K = rad(norm(c) / 2)
        items.append(item_num(f"ar-{n:02d}", rf"The area of the triangle $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$.", K,
                              rf"$\crossp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}={vt(c)}$, so the area is $\dfrac12{tex(norm(c))}={tex(K)}$.", ["Half the norm of the cross product of two sides."]))
    for n, (P, d) in enumerate((((1, 2, 3), (1, 2, 2)), ((0, 1, 0), (1, 0, 0))), 8):
        c = cross(P, d)
        dist = rad(norm(c) / norm(d))
        items.append(item_num(f"ar-{n:02d}", rf"The distance from $P{pt3_tex(P)}$ to the line through the origin with direction ${vt(d)}$.", dist,
                              rf"$\crossp{{\overrightarrow{{OP}}}}{{\vec d}}={vt(c)}$, with norm ${tex(norm(c))}$, and $\norm{{\vec d}}={tex(norm(d))}$; the distance is ${tex(dist)}$.", ["$\\dfrac{\\norm{\\crossp{\\overrightarrow{AP}}{\\vec d}}}{\\norm{\\vec d}}$."]))
    items.append(item_num("ar-10", r"The height on the side $AB$ of the triangle $A(0,0,0)$, $B(4,0,0)$, $C(1,3,0)$.", R(3),
                          r"The area is $6$ and $AB=4$, so $h=\dfrac{2\cdot6}{4}=3$.", ["$h=\\dfrac{2K}{\\text{base}}$."], answer_type="number"))
    return items


def u2l5() -> list[dict]:
    items = []
    triples = (((1, 2, 3), (0, 1, 4), (5, 6, 0)), ((2, 0, 1), (1, 3, 2), (0, 1, 1)), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((3, 1, 2), (1, 2, 0), (2, 1, 1)))
    for n, (u, v, w) in enumerate(triples, 1):
        b = dot(cross(u, v), w)
        items.append(item_num(f"bx-{n:02d}", rf"$\boxp{{\vec u}}{{\vec v}}{{\vec w}}$ for $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$.", b,
                              rf"The determinant of the three rows is ${tex(b)}$.", ["Expand the determinant along the first row."], answer_type="number"))
    items.append(ex("bx-05", r"For which $k$ are $(1,2,k)$, $(2,1,0)$ and $(0,1,1)$ coplanar?", "number", "3/2", hints=["The determinant must be $0$."], solution=r"$1-4+2k=0$ gives $k=\dfrac32$."))
    items.append(ex("bx-06", r"For which $k$ are $(1,1,1)$, $(1,2,3)$ and $(1,4,k)$ coplanar?", "number", "7",
                    hints=["The determinant must be $0$."],
                    solution=r"The determinant is $1\cdot(2k-12)-1\cdot(k-3)+1\cdot(4-2)=k-7$, so $k=7$."))
    items.append(ex("bx-07", r"Is the triple $\vec u=(1,0,0)$, $\vec v=(0,0,1)$, $\vec w=(0,1,0)$ right-handed? Answer $1$ for yes, $0$ for no.", "number", "0",
                    hints=["Compute the sign of the box product."], solution=r"$\boxp{\vec i}{\vec k}{\vec j}=-1<0$: the triple is left-handed."))
    return items


def u2l6() -> list[dict]:
    items = []
    for n, (u, v, w) in enumerate((((2, 0, 0), (1, 3, 0), (0, 1, 4)), ((1, 2, 3), (3, 1, 2), (2, 4, 1)), ((1, 1, 0), (0, 1, 1), (1, 0, 1))), 1):
        b = dot(cross(u, v), w)
        items.append(item_num(f"vl-{n:02d}", rf"The volume of the parallelepiped built on ${vt(u)}$, ${vt(v)}$, ${vt(w)}$.", sp.Abs(b),
                              rf"The determinant is ${tex(b)}$; the volume is its absolute value ${tex(sp.Abs(b))}$.", ["The absolute value of the box product."], answer_type="number"))
    for n, (A, B, C, D) in enumerate((((1, 1, 1), (2, 3, 4), (4, 2, 3), (3, 5, 2)), ((0, 0, 0), (2, 0, 0), (0, 4, 0), (0, 0, 6)), ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))), 4):
        b = dot(cross(sub(A, B), sub(A, C)), sub(A, D))
        items.append(item_num(f"vl-{n:02d}", rf"The volume of the tetrahedron $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$, $D{pt3_tex(D)}$.", rad(sp.Abs(b) / 6),
                              rf"The box product of $\overrightarrow{{AB}},\overrightarrow{{AC}},\overrightarrow{{AD}}$ is ${tex(b)}$, so $V=\dfrac{{|{tex(b)}|}}{{6}}={tex(rad(sp.Abs(b)/6))}$.", ["One sixth of the absolute value of the box product."]))
    items.append(ex("vl-07", r"Are $A(0,0,0)$, $B(1,2,3)$, $C(2,1,0)$, $D(3,3,3)$ coplanar? Answer $1$ for yes, $0$ for no.", "number", "1",
                    hints=["Look at $\\overrightarrow{AB}+\\overrightarrow{AC}$."], solution=r"$\overrightarrow{AD}=\overrightarrow{AB}+\overrightarrow{AC}$, so the box product is $0$: the points are coplanar."))
    items.append(ex("vl-08", r"A tetrahedron has volume $12$ and the face $ABC$ has area $9$. Find the height from $D$.", "number", "4", hints=["$h=\\dfrac{3V}{S}$."], solution=r"$h=\dfrac{36}{9}=4$."))
    return items


def u2l7() -> list[dict]:
    items = []
    for n, (u, v, w) in enumerate((((1, 2, 3), (2, 0, 1), (1, 1, 0)), ((2, 1, 0), (1, 1, 1), (0, 2, 1)), ((1, 0, 2), (3, 1, 0), (1, 2, 1))), 1):
        res = cross(u, cross(v, w))
        a, b = dot(u, w), dot(u, v)
        items.append(item_pt(f"dc-{n:02d}", rf"$\crossp{{\vec u}}{{\crossp{{\vec v}}{{\vec w}}}}$ for $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$.", res,
                             rf"With the identity: ${tex(a)}\,\vec v-{par(b)}\,\vec w={vt(res)}$.", ["$\\vec v\\,\\dotp{\\vec u}{\\vec w}-\\vec w\\,\\dotp{\\vec u}{\\vec v}$."]))
    u, v, w = (1, 2, 3), (2, 0, 1), (1, 1, 0)
    other = cross(cross(u, v), w)
    items.append(item_pt("dc-04", rf"$\crossp{{\crossp{{\vec u}}{{\vec v}}}}{{\vec w}}$ for $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$.", other,
                         rf"$\crossp{{\vec u}}{{\vec v}}={vt(cross(u,v))}$; crossing with $\vec w$ gives ${vt(other)}$, which is different from $\crossp{{\vec u}}{{\crossp{{\vec v}}{{\vec w}}}}$.", ["Do the first cross product first."]))
    items.append(item_pt("dc-05", r"$\crossp{\vec i}{\crossp{\vec i}{\vec j}}$", (0, -1, 0), r"$\vec i\,\dotp{\vec i}{\vec j}-\vec j\,\dotp{\vec i}{\vec i}=-\vec j$.", ["Use the identity."]))
    return items


def build() -> None:
    write_exercises(f"{U1}/l04-norm-unit-vectors-direction-cosines", [exset("norms", "Norms, unit vectors and direction cosines.", u1l4(), format=FMT)], "geo_m01.py")
    write_exercises(f"{U2}/l01-dot-product", [exset("dot", "The dot product.", u2l1(), format=FMT)], "geo_m01.py")
    write_exercises(f"{U2}/l02-projection-and-inequalities", [exset("projection", "Projections and inequalities.", u2l2(), format=FMT)], "geo_m01.py")
    write_exercises(f"{U2}/l03-cross-product", [exset("cross", "The cross product.", u2l3(), format=FMT)], "geo_m01.py")
    write_exercises(f"{U2}/l04-areas", [exset("areas", "Areas and distances with the cross product.", u2l4(), format=FMT)], "geo_m01.py")
    write_exercises(f"{U2}/l05-box-product", [exset("box", "The box product.", u2l5(), format=FMT)], "geo_m01.py")
    write_exercises(f"{U2}/l06-volumes", [exset("volumes", "Volumes.", u2l6(), format=FMT)], "geo_m01.py")
    write_exercises(f"{U2}/l07-double-cross-product", [exset("double", "The double cross product.", u2l7(), format=FMT)], "geo_m01.py")
