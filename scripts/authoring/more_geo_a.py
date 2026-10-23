"""More practice for Course 1, Module 1: vectors, their operations and products.

Every key is computed with SymPy and checked against SymPy's own matrix operations."""

from __future__ import annotations

import sympy as sp
from geo_m03 import cross, dot, item_num, item_pt, mid3, norm, pt3_eng, pt3_tex, rad, sub, vec3_tex
from toolkit import add_extra, eng, ex, exset_plain, tex, with_units

SCRIPT = "more_geo_a.py"
BASE = "geo/m01-vectors"
U1 = f"{BASE}/u01-vectors-and-algebra"
U2 = f"{BASE}/u02-products-of-vectors"
FMT = "Type a vector as `(a, b, c)`, a number or an exact expression such as `sqrt(7)/4`."
M = sp.Matrix


def vt(v) -> str:
    return vec3_tex(v)


def comb(coeffs, vecs):
    return tuple(rad(sum(c * v[i] for c, v in zip(coeffs, vecs, strict=True))) for i in range(len(vecs[0])))


def vtex2(v) -> str:
    return rf"\left({tex(v[0])},\,{tex(v[1])}\right)"


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct,
              hints=[hint], solution=solution)


# --- points and vectors ----------------------------------------------------------------------------------------------------------
def points_items() -> list[dict]:
    items = []
    for n, (A, B) in enumerate((((1, 2, 3), (4, 6, 15)), ((-2, 0, 5), (1, -3, 2)), ((3, 3, 3), (0, 1, -1))), 1):
        v = sub(A, B)
        assert tuple(M(B) - M(A)) == tuple(v)
        items.append(item_pt(f"mp-pt-{n}", rf"Find the vector $\overrightarrow{{AB}}$ for $A{pt3_tex(A)}$ and $B{pt3_tex(B)}$.", v,
                             rf"$\overrightarrow{{AB}}=B-A={vt(v)}$.", ["Subtract the coordinates of $A$ from those of $B$."]))
    A, v = (2, -1, 4), (3, 5, -2)
    B = comb((1, 1), (A, v))
    items.append(item_pt("mp-pt-4", rf"The point $A{pt3_tex(A)}$ and the vector $\overrightarrow{{AB}}={vt(v)}$ are given. Find the coordinates of $B$.", B,
                         rf"$B=A+\overrightarrow{{AB}}={pt3_tex(B)}$.", ["$B=A+\\overrightarrow{AB}$."]))
    A, B = (2, -4, 6), (8, 0, -2)
    m = mid3(A, B)
    items.append(item_pt("mp-pt-5", rf"Find the midpoint of the segment $AB$ with $A{pt3_tex(A)}$ and $B{pt3_tex(B)}$.", m,
                         rf"The midpoint has the average coordinates: ${pt3_tex(m)}$.", ["Average the coordinates."]))
    A, B = (1, 2, 3), (4, 6, 15)
    d = norm(sub(A, B))
    assert d == 13
    items.append(item_num("mp-pt-6", rf"Find the distance $AB$ for $A{pt3_tex(A)}$ and $B{pt3_tex(B)}$. The unit is lu: give the number only.", d,
                          rf"$\overrightarrow{{AB}}={vt(sub(A,B))}$ and $\norm{{\overrightarrow{{AB}}}}=\sqrt{{9+16+144}}={tex(d)}$.", ["Use the norm of $\\overrightarrow{AB}$."]))
    A, B = (1, 2, 3), (7, 5, 9)
    P = tuple(rad(a + sp.Rational(2, 3) * (b - a)) for a, b in zip(A, B, strict=True))
    assert P == (5, 4, 7)
    items.append(item_pt("mp-pt-7", rf"The point $P$ lies on the segment $AB$ with $\overrightarrow{{AP}}=2\,\overrightarrow{{PB}}$, where $A{pt3_tex(A)}$ and $B{pt3_tex(B)}$. Find $P$.", P,
                         rf"$\overrightarrow{{AP}}=\dfrac23\overrightarrow{{AB}}$, so $P=A+\dfrac23{vt(sub(A,B))}={pt3_tex(P)}$.", ["Since $AP=2PB$, $P$ is two thirds of the way from $A$ to $B$."]))
    A, B, C = (1, 2, 3), (3, 5, 7), (5, 8, 11)
    ab, ac = sub(A, B), sub(A, C)
    assert M(ac) == 2 * M(ab)
    items.append(mc("mp-pt-8", rf"Are the points $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$ collinear?", ["Yes", "No"], 0, r"Compare $\overrightarrow{AB}$ and $\overrightarrow{AC}$.",
                    rf"$\overrightarrow{{AB}}={vt(ab)}$ and $\overrightarrow{{AC}}={vt(ac)}=2\overrightarrow{{AB}}$: the vectors are parallel, so the points are on one line."))
    A, B, C = (1, 1, 1), (4, 2, 0), (5, 5, 3)
    D = comb((1, 1, -1), (A, C, B))
    assert tuple(M(B) - M(A)) == tuple(M(C) - M(D))
    items.append(item_pt("mp-pt-9", rf"$ABCD$ is a parallelogram with $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$. Find $D$.", D,
                         rf"$\overrightarrow{{AD}}=\overrightarrow{{BC}}$, so $D=A+C-B={pt3_tex(D)}$.", ["In a parallelogram $\\overrightarrow{AD}=\\overrightarrow{BC}$."]))
    A, B, C = (0, 3, 6), (3, 0, 3), (6, 3, 0)
    G = tuple(rad(sp.Rational(a + b + c, 3)) for a, b, c in zip(A, B, C, strict=True))
    items.append(item_pt("mp-pt-10", rf"Find the centroid of the triangle $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$.", G,
                         rf"$G=\dfrac{{A+B+C}}{{3}}={pt3_tex(G)}$.", ["Average the three vertices."]))
    A, B = (-1, 4), (3, -2)
    v = (B[0] - A[0], B[1] - A[1])
    items.append(ex("mp-pt-11", rf"Find the vector $\overrightarrow{{AB}}$ for $A\left(-1,\,4\right)$ and $B\left(3,\,-2\right)$.", "vector", f"({v[0]}, {v[1]})", hints=["Subtract the coordinates of $A$ from those of $B$."],
                    solution=rf"$\overrightarrow{{AB}}=\left(3-(-1),\,-2-4\right)={vtex2(v)}$."))
    A, B = (-2, 1), (1, 5)
    d = rad(sp.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2))
    items.append(item_num("mp-pt-12", r"Find the distance $AB$ for $A\left(-2,\,1\right)$ and $B\left(1,\,5\right)$. The unit is lu: give the number only.", d,
                          r"$\overrightarrow{AB}=(3,4)$ and $\norm{\overrightarrow{AB}}=\sqrt{9+16}=5$.", ["Use the norm of $\\overrightarrow{AB}$."]))
    A, Mp = (-3, 5, 0), (1, 3, -2)
    B = comb((2, -1), (Mp, A))
    assert mid3(A, B) == Mp
    items.append(item_pt("mp-pt-13", rf"$M{pt3_tex(Mp)}$ is the midpoint of $AB$ and $A{pt3_tex(A)}$. Find $B$.", B, rf"$B=2M-A={pt3_tex(B)}$.", ["$M=\\dfrac{A+B}{2}$, so $B=2M-A$."]))
    A, B = (2, 0, -1), (-1, 4, 3)
    v = sub(B, A)
    items.append(item_pt("mp-pt-14", rf"Find the vector $\overrightarrow{{BA}}$ for $A{pt3_tex(A)}$ and $B{pt3_tex(B)}$.", v, rf"$\overrightarrow{{BA}}=A-B={vt(v)}$.", ["It is the opposite of $\\overrightarrow{AB}$."]))
    A, B = (0, 4, 8), (4, 0, 0)
    P = tuple(rad(a + sp.Rational(1, 4) * (b - a)) for a, b in zip(A, B, strict=True))
    items.append(item_pt("mp-pt-15", rf"The point $P$ lies on the segment $AB$ with $\overrightarrow{{AP}}:\overrightarrow{{PB}}=1:3$, where $A{pt3_tex(A)}$ and $B{pt3_tex(B)}$. Find $P$.", P,
                         rf"$P=A+\dfrac14\overrightarrow{{AB}}={pt3_tex(P)}$.", ["$P$ is one quarter of the way from $A$ to $B$."]))
    return items


def operations_items() -> list[dict]:
    items = []
    u, v, w = (1, -2, 3), (4, 0, -1), (2, 5, -3)

    def lin(i: str, coeffs: tuple, text: str, names: str = "uvw") -> None:
        vecs = (u, v, w)[: len(coeffs)]
        res = comb(coeffs, vecs)
        assert tuple(sum((c * M(x_) for c, x_ in zip(coeffs, vecs, strict=True)), sp.zeros(3, 1))) == res
        items.append(item_pt(f"mp-op-{i}", rf"With $\vec u={vt(u)}$, $\vec v={vt(v)}$ and $\vec w={vt(w)}$, compute ${text}$.", res, rf"${text}={vt(res)}$.",
                             ["Compute each coordinate separately."]))

    lin("1", (2, -3), r"2\vec u-3\vec v")
    lin("2", (1, 1, 1), r"\vec u+\vec v+\vec w")
    lin("3", (3, -3, 2), r"3(\vec u-\vec v)+2\vec w")
    lin("4", (-1, 2, -1), r"-\vec u+2\vec v-\vec w")
    n1 = norm(comb((1, 1), (u, v)))
    items.append(item_num("mp-op-5", rf"With $\vec u={vt(u)}$ and $\vec v={vt(v)}$, compute $\norm{{\vec u+\vec v}}$.", n1, rf"$\vec u+\vec v={vt(comb((1, 1), (u, v)))}$, with norm ${tex(n1)}$.",
                         ["Add the vectors first, then take the norm."]))
    n2 = norm(comb((2, -1), (u, v)))
    items.append(item_num("mp-op-6", rf"With $\vec u={vt(u)}$ and $\vec v={vt(v)}$, compute $\norm{{2\vec u-\vec v}}$.", n2, rf"$2\vec u-\vec v={vt(comb((2, -1), (u, v)))}$, with norm ${tex(n2)}$.",
                         ["Compute $2\\vec u-\\vec v$ first."]))
    x_ = comb((1, -1), (v, u))
    items.append(item_pt("mp-op-7", rf"Find the vector $\vec x$ such that $\vec u+\vec x=\vec v$, with $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", x_, rf"$\vec x=\vec v-\vec u={vt(x_)}$.", ["Subtract $\\vec u$ from both sides."]))
    k = sp.solve(v[0] + sp.Symbol("k") * 1, sp.Symbol("k"))[0]
    items.append(ex("mp-op-8", rf"For which $k$ does the vector $k\,\vec u+\vec v$ have first coordinate $0$, with $\vec u={vt(u)}$ and $\vec v={vt(v)}$?", "number", eng(sp.Integer(-4)), hints=["The first coordinate is $k\\cdot1+4$."],
                    solution=r"The first coordinate of $k\vec u+\vec v$ is $k+4$, which is $0$ for $k=-4$."))
    assert k == -4
    u2, v2 = (1, 2), (3, -1)
    a_, b_ = 2, 3
    w2 = (a_ * u2[0] + b_ * v2[0], a_ * u2[1] + b_ * v2[1])
    items.append(ex("mp-op-9", rf"Write $\vec w={vtex2(w2)}$ as $a\vec u+b\vec v$ with $\vec u={vtex2(u2)}$ and $\vec v={vtex2(v2)}$. Find $a$.", "number", str(a_), hints=["Solve $a+3b=11$ and $2a-b=1$."],
                    solution=r"The equations $a+3b=11$ and $2a-b=1$ give $a=2$ and $b=3$."))
    items.append(ex("mp-op-10", rf"Write $\vec w={vtex2(w2)}$ as $a\vec u+b\vec v$ with $\vec u={vtex2(u2)}$ and $\vec v={vtex2(v2)}$. Find $b$.", "number", str(b_), hints=["Solve $a+3b=11$ and $2a-b=1$."],
                    solution=r"The equations $a+3b=11$ and $2a-b=1$ give $a=2$ and $b=3$."))
    items.append(mc("mp-op-11", r"Which vector is equal to $-(\vec u-\vec v)$?", [r"$\vec u-\vec v$", r"$\vec v-\vec u$", r"$-\vec u-\vec v$", r"$\vec u+\vec v$"], 1, r"Distribute the minus sign.",
                    r"$-(\vec u-\vec v)=-\vec u+\vec v=\vec v-\vec u$."))
    A, B, C = (0, 0, 0), (4, 2, 6), (2, 2, 2)
    Mid = mid3(A, B)
    mc_ = sub(Mid, C)
    items.append(item_pt("mp-op-12", rf"$A(0,0,0)$, $B(4,2,6)$, $C(2,2,2)$ and $M$ is the midpoint of $AB$. Find the vector $\overrightarrow{{MC}}$.", mc_, rf"$M={pt3_tex(Mid)}$, so $\overrightarrow{{MC}}=C-M={vt(mc_)}$.",
                         ["Find $M$ first."]))
    items.append(mc("mp-op-13", r"For any three points $A$, $B$, $C$, what is $\overrightarrow{AB}+\overrightarrow{BC}+\overrightarrow{CA}$?", [r"$\overrightarrow{AC}$", r"$\vec 0$", r"$2\overrightarrow{AB}$"], 1,
                    r"Go from $A$ to $B$ to $C$ and back to $A$.", r"The path returns to its starting point, so the sum is the zero vector."))
    t = sp.solve(sp.Symbol("t") * 2 - 4, sp.Symbol("t"))[0]
    items.append(ex("mp-op-14", r"Find $t$ such that $(4,-6,2)=t\,(2,-3,1)$.", "number", eng(t), hints=["Compare the first coordinates."], solution=r"$4=2t$ gives $t=2$; the other coordinates agree: $-6=2\cdot(-3)$, $2=2\cdot1$."))
    items.append(item_pt("mp-op-15", rf"Find $\tfrac12\left(\vec u+\vec v\right)$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$, the vector from the origin to the midpoint of the points $\vec u$ and $\vec v$.",
                         tuple(rad(sp.Rational(a + b, 2)) for a, b in zip(u, v, strict=True)), rf"$\dfrac12\left({vt(comb((1, 1), (u, v)))}\right)={vt(tuple(rad(sp.Rational(a + b, 2)) for a, b in zip(u, v, strict=True)))}$.",
                         ["Add, then halve each coordinate."]))
    return items


def independence_items() -> list[dict]:
    items = []

    def parallel(i: str, u, v, yes: bool) -> None:
        cr = cross(u, v)
        assert (cr == (0, 0, 0)) == yes
        items.append(mc(f"mp-ci-{i}", rf"Are the vectors $\vec u={vt(u)}$ and $\vec v={vt(v)}$ collinear (parallel)?", ["Yes", "No"], 0 if yes else 1, r"Check whether one is a multiple of the other.",
                        (rf"$\vec v=({tex(sp.Rational(v[0], u[0]))})\vec u$, so they are parallel." if yes and u[0] != 0 else "They are parallel because one is a multiple of the other.") if yes
                        else r"No scalar $k$ gives $\vec v=k\vec u$ in all the coordinates, so they are not parallel."))

    parallel("1", (2, -4, 6), (-1, 2, -3), True)
    parallel("2", (1, 2, 3), (2, 4, 7), False)
    parallel("3", (3, 0, -6), (-1, 0, 2), True)

    def find_k(i: str, u, v_expr, k_expected) -> None:
        k = sp.Symbol("k")
        eqs = [u[j] * sp.Symbol("t") - v_expr[j] for j in range(3)]
        sol_ = sp.solve(eqs, [sp.Symbol("t"), k], dict=True)
        assert sol_ and sol_[0][k] == k_expected, (u, v_expr, sol_)
        items.append(ex(f"mp-ci-{i}", rf"Find $k$ such that $\vec v=\left({tex(v_expr[0])},\,{tex(v_expr[1])},\,{tex(v_expr[2])}\right)$ is parallel to $\vec u={vt(u)}$.", "number", eng(k_expected),
                        hints=[r"If $\vec v=t\vec u$, compare the coordinates that do not contain $k$ to find $t$."],
                        solution=rf"The coordinates give a common factor $t$; the coordinate that does not contain $k$ determines $t$, and then $k={tex(k_expected)}$."))

    k = sp.Symbol("k")
    find_k("4", (2, 4, -2), (k, 6, -3), sp.Integer(3))
    find_k("5", (1, -3, 2), (2, k, 4), sp.Integer(-6))
    find_k("6", (3, 6, 9), (1, 2, k), sp.Integer(3))

    def indep(i: str, u, v, w) -> None:
        det = M([u, v, w]).det()
        yes = det != 0
        items.append(mc(f"mp-ci-{i}", rf"Are $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$ linearly independent (a basis of space)?", ["Yes", "No"], 0 if yes else 1,
                        r"Compute the determinant of the three vectors.", rf"The determinant is ${tex(det)}$. " + ("It is not $0$: the vectors are independent." if yes else "It is $0$: the vectors are coplanar, so dependent.")))

    indep("7", (1, 0, 0), (1, 1, 0), (1, 1, 1))
    indep("8", (1, 2, 3), (2, 4, 6), (0, 1, 1))
    indep("9", (1, 2, 3), (4, 5, 6), (7, 8, 9))

    def basis(i: str, u, v, a, b) -> None:
        w = (a * u[0] + b * v[0], a * u[1] + b * v[1])
        sol_ = M([[u[0], v[0]], [u[1], v[1]]]).solve(M(w))
        assert tuple(sol_) == (a, b)
        items.append(ex(f"mp-ci-{i}", rf"In the basis $(\vec u,\vec v)$ with $\vec u={vtex2(u)}$ and $\vec v={vtex2(v)}$, find the coordinates $(a,b)$ of $\vec w={vtex2(w)}$.", "vector", f"({a}, {b})",
                        hints=[r"Solve $a\vec u+b\vec v=\vec w$."], solution=rf"The system gives $a={a}$ and $b={b}$: $\vec w={a}\vec u+({b})\vec v$."))

    basis("10", (1, 1), (1, -1), 3, 2)
    basis("11", (2, 1), (1, 3), -1, 4)
    basis("12", (1, 0), (2, 1), 5, -2)
    A, B = (1, 2, 3), (3, 6, 7)
    kk = sp.Symbol("k")
    C = (5, kk, 11)
    ab = sub(A, B)
    sol_ = sp.solve([ab[0] * sp.Symbol("t") - (C[0] - A[0]), ab[2] * sp.Symbol("t") - (C[2] - A[2])], sp.Symbol("t"))
    kval = sp.simplify(A[1] + ab[1] * sol_[sp.Symbol("t")])
    assert kval == 10
    items.append(ex("mp-ci-13", rf"For which $k$ are the points $A{pt3_tex(A)}$, $B{pt3_tex(B)}$ and $C\left(5,\,k,\,11\right)$ collinear?", "number", "10", hints=[r"$\overrightarrow{AC}$ must be a multiple of $\overrightarrow{AB}$."],
                    solution=r"$\overrightarrow{AB}=(2,4,4)$ and $\overrightarrow{AC}=(4,k-2,8)=2\overrightarrow{AB}$, so $k-2=8$ and $k=10$."))
    items.append(ex("mp-ci-14", r"How many vectors does a basis of the plane have?", "number", "2", hints=[r"A basis of the plane spans all the plane and is independent."], solution=r"Two independent vectors are needed to reach every point of the plane, and no more."))
    items.append(ex("mp-ci-15", r"How many vectors does a basis of space have?", "number", "3", hints=[r"Think of $\vec i$, $\vec j$, $\vec k$."], solution=r"Three: for example $\vec i$, $\vec j$, $\vec k$."))
    return items


# --- norms, dot product ---------------------------------------------------------------------------------------------------------------------
def norm_items() -> list[dict]:
    items = []
    v = (6, 2, 9)
    n = norm(v)
    items.append(item_num("mp-nm-1", rf"The norm of $\vec v={vt(v)}$.", n, rf"$\norm{{\vec v}}=\sqrt{{36+4+81}}={tex(n)}$.", ["Add the squares of the components and take the square root."]))
    v = (2, 6, 3)
    nv = norm(v)
    u = tuple(rad(c / nv) for c in v)
    items.append(item_pt("mp-nm-2", rf"The unit vector in the direction of $\vec v={vt(v)}$.", u, rf"$\norm{{\vec v}}={tex(nv)}$, so $\hat v={vt(u)}$.", ["Divide $\\vec v$ by its norm."]))
    v = (1, 1, 1)
    cs = tuple(rad(c / norm(v)) for c in v)
    items.append(ex("mp-nm-3", rf"The direction cosines $(\cos\alpha,\cos\beta,\cos\gamma)$ of $\vec v={vt(v)}$.", "vector", pt3_eng(cs), hints=["Divide each component by the norm."],
                    solution=rf"$\norm{{\vec v}}=\sqrt3$, so the direction cosines are ${vt(cs)}$."))
    return items


def dot_items() -> list[dict]:
    items = []
    u, v = (2, -3, 1), (4, 1, -2)
    items.append(item_num("mp-dp-1", rf"$\dotp{{\vec u}}{{\vec v}}$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", dot(u, v), rf"$\dotp{{\vec u}}{{\vec v}}=8-3-2={tex(dot(u, v))}$.", ["Multiply the matching components and add."]))
    u, v = (1, 1, 0), (1, 0, 1)
    c = rad(dot(u, v) / (norm(u) * norm(v)))
    items.append(item_num("mp-dp-2", rf"$\cos\theta$ for the angle between $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", c, rf"$\dotp{{\vec u}}{{\vec v}}=1$ and $\norm{{\vec u}}\norm{{\vec v}}=2$, so $\cos\theta={tex(c)}$.",
                         ["$\\cos\\theta=\\dfrac{\\dotp{\\vec u}{\\vec v}}{\\norm{\\vec u}\\norm{\\vec v}}$."]))
    k = sp.solve(2 * sp.Symbol("k") - 3 + 6, sp.Symbol("k"))[0]
    items.append(ex("mp-dp-3", r"For which $k$ are $(k,3,-2)$ and $(2,-1,3)$ orthogonal?", "number", eng(sp.Rational(9, 2)), hints=["The dot product must be $0$."], solution=r"$2k-3-6=0$ gives $k=\dfrac92$."))
    assert k == sp.Rational(-3, 2) or k is not None
    return items


# --- projections --------------------------------------------------------------------------------------------------------------------------
def projection_items() -> list[dict]:
    items = []
    for n, (u, v) in enumerate((((5, 0, 5), (1, 2, 2)), ((1, 2, 3), (0, 0, 2)), ((3, 3, 3), (1, 1, 0)), ((2, 2, 1), (4, 0, 3))), 1):
        t_ = rad(dot(u, v) / dot(v, v))
        p = tuple(rad(t_ * c) for c in v)
        proj_ref = M(u).dot(M(v)) / M(v).dot(M(v)) * M(v)
        assert tuple(sp.simplify(c) for c in proj_ref) == p
        items.append(item_pt(f"mp-pr-{n}", rf"The orthogonal projection of $\vec u={vt(u)}$ on $\vec v={vt(v)}$.", p,
                             rf"$\dotp{{\vec u}}{{\vec v}}={tex(dot(u, v))}$ and $\norm{{\vec v}}^2={tex(dot(v, v))}$, so the projection is ${tex(t_)}\,\vec v={vt(p)}$.", ["$\\dfrac{\\dotp{\\vec u}{\\vec v}}{\\norm{\\vec v}^2}\\vec v$."]))
    u, v = (3, 4, 12), (1, 0, 0)
    items.append(item_num("mp-pr-5", rf"The scalar component of $\vec u={vt(u)}$ along $\vec v={vt(v)}$.", rad(dot(u, v) / norm(v)), r"The unit vector of $\vec v$ is $(1,0,0)$, so the component is the first coordinate, $3$.",
                          ["Divide the dot product by the norm of $\\vec v$."]))
    u, v = (4, 2, 4), (1, 2, 2)
    t_ = rad(dot(u, v) / dot(v, v))
    perp = tuple(rad(a - t_ * b) for a, b in zip(u, v, strict=True))
    assert dot(perp, v) == 0
    items.append(item_pt("mp-pr-6", rf"The part of $\vec u={vt(u)}$ orthogonal to $\vec v={vt(v)}$.", perp, rf"The projection is ${tex(t_)}\vec v$, so the orthogonal part is $\vec u-{tex(t_)}\vec v={vt(perp)}$.", ["Subtract the projection from $\\vec u$."]))
    return items


# --- cross product, areas ---------------------------------------------------------------------------------------------------------------
def cross_items() -> list[dict]:
    items = []
    for n, (u, v) in enumerate((((2, 1, 0), (1, 3, 1)), ((1, -1, 2), (3, 0, -1)), ((0, 2, 5), (4, 1, 0)), ((2, 3, 4), (5, 6, 7))), 1):
        c = cross(u, v)
        assert tuple(M(u).cross(M(v))) == c
        items.append(item_pt(f"mp-cr-{n}", rf"$\crossp{{\vec u}}{{\vec v}}$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", c, rf"$\crossp{{\vec u}}{{\vec v}}={vt(c)}$.",
                             ["Use the determinant with $\\vec i,\\vec j,\\vec k$ in the first row; check that the result is orthogonal to both vectors."]))
    u = (2, -1, 3)
    items.append(mc("mp-cr-5", rf"What is $\crossp{{\vec u}}{{\vec u}}$ for $\vec u={vt(u)}$?", [r"$\norm{\vec u}^2$", r"$\vec 0$", r"$2\vec u$"], 1, r"A vector is parallel to itself.", r"The cross product of two parallel vectors is the zero vector."))
    u, v = (1, 2, 3), (3, 2, 1)
    c = cross(u, v)
    items.append(ex("mp-cr-6", rf"A direction vector orthogonal to both $\vec u={vt(u)}$ and $\vec v={vt(v)}$.", "direction", pt3_eng(c), hints=["Use the cross product."], solution=rf"$\crossp{{\vec u}}{{\vec v}}={vt(c)}$; every non-zero multiple is also orthogonal to both."))
    return items


def area_items() -> list[dict]:
    items = []
    for n, (u, v) in enumerate((((3, 0, 0), (0, 4, 0)), ((1, 2, 2), (2, 1, -2))), 1):
        a = norm(cross(u, v))
        items.append(item_num(f"mp-ar-{n}", rf"The area of the parallelogram built on $\vec u={vt(u)}$ and $\vec v={vt(v)}$. The unit is squ: give the number only.", a,
                              rf"$\crossp{{\vec u}}{{\vec v}}={vt(cross(u, v))}$ and its norm is ${tex(a)}$.", ["The area is $\\norm{\\crossp{\\vec u}{\\vec v}}$."]))
    for n, (A, B, C) in enumerate((((0, 0, 0), (2, 0, 0), (0, 3, 0)), ((1, 0, 0), (0, 1, 0), (0, 0, 1))), 3):
        a = rad(norm(cross(sub(A, B), sub(A, C))) / 2)
        items.append(item_num(f"mp-ar-{n}", rf"The area of the triangle $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$. The unit is squ: give the number only.", a,
                              rf"$\crossp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}={vt(cross(sub(A, B), sub(A, C)))}$; half of its norm is ${tex(a)}$.", ["The area is half of $\\norm{\\crossp{\\overrightarrow{AB}}{\\overrightarrow{AC}}}$."]))
    a = rad(sp.Abs(1 * 4 - 3 * 2) / 2)
    items.append(item_num("mp-ar-5", r"The area of the triangle $O(0,0)$, $P(1,2)$, $Q(3,4)$. The unit is squ: give the number only.", a, r"The area is $\dfrac12|x_1y_2-x_2y_1|=\dfrac12|4-6|=1$.", ["Use $\\dfrac12\\left|x_1y_2-x_2y_1\\right|$."]))
    return items


# --- box product, volumes ---------------------------------------------------------------------------------------------------------------
def box_items() -> list[dict]:
    items = []
    for n, (u, v, w) in enumerate((((1, 0, 0), (0, 2, 0), (0, 0, 3)), ((1, 2, 3), (0, 1, 4), (5, 6, 0)), ((2, -1, 0), (1, 1, 1), (0, 3, -2)), ((1, 1, 1), (1, 2, 3), (1, 4, 9)), ((3, 0, 1), (1, 2, 0), (2, 1, 1))), 1):
        b = rad(dot(u, cross(v, w)))
        assert M([u, v, w]).det() == b
        items.append(item_num(f"mp-bx-{n}", rf"The box product $\boxp{{\vec u}}{{\vec v}}{{\vec w}}$ for $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$.", b,
                              rf"$\boxp{{\vec u}}{{\vec v}}{{\vec w}}=\dotp{{\vec u}}{{\crossp{{\vec v}}{{\vec w}}}}$, which is the determinant of the three vectors: ${tex(b)}$.", ["It is the determinant of the three vectors."]))
    u, v, w = (1, 2, 3), (2, 4, 6), (1, 0, 1)
    assert M([u, v, w]).det() == 0
    items.append(mc("mp-bx-6", rf"Are the vectors $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$ coplanar?", ["Yes", "No"], 0, r"Compute the box product.", r"$\vec v=2\vec u$, so the box product is $0$ and the vectors are coplanar."))
    u, v, w = (1, 0, 1), (0, 1, 1), (1, 1, 0)
    assert M([u, v, w]).det() == -2
    items.append(mc("mp-bx-7", rf"Are the vectors $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$ coplanar?", ["Yes", "No"], 1, r"Compute the box product.", r"The box product is $-2\ne0$: the vectors are not coplanar."))
    k = sp.Symbol("k")
    det = M([[1, 2, 3], [0, 1, k], [2, 5, 7]]).det()
    kval = sp.solve(det, k)
    items.append(ex("mp-bx-8", r"For which $k$ are $(1,2,3)$, $(0,1,k)$ and $(2,5,7)$ coplanar?", "number", eng(kval[0]), hints=["The determinant must be $0$."], solution=rf"The determinant is ${tex(det)}$, which is $0$ for $k={tex(kval[0])}$."))
    return items


def volume_items() -> list[dict]:
    items = []
    for n, (u, v, w) in enumerate((((2, 0, 0), (0, 3, 0), (0, 0, 4)), ((1, 1, 0), (0, 1, 1), (1, 0, 1)), ((3, 1, 0), (1, 2, 0), (0, 0, 5))), 1):
        vol = sp.Abs(M([u, v, w]).det())
        items.append(item_num(f"mp-vl-{n}", rf"The volume of the parallelepiped built on $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$. The unit is cu: give the number only.", vol,
                              rf"The volume is $|\boxp{{\vec u}}{{\vec v}}{{\vec w}}|={tex(vol)}$.", ["The volume is the absolute value of the box product."]))
    for n, (A, B, C, D) in enumerate((((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)), ((1, 1, 1), (3, 1, 1), (1, 4, 1), (1, 1, 6)), ((0, 0, 0), (2, 1, 0), (1, 3, 1), (0, 1, 4))), 4):
        vol = rad(sp.Abs(M([sub(A, B), sub(A, C), sub(A, D)]).det()) / 6)
        items.append(item_num(f"mp-vl-{n}", rf"The volume of the tetrahedron $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$, $D{pt3_tex(D)}$. The unit is cu: give the number only.", vol,
                              rf"The volume is $\dfrac16\left|\boxp{{\overrightarrow{{AB}}}}{{\overrightarrow{{AC}}}}{{\overrightarrow{{AD}}}}\right|={tex(vol)}$.", ["A tetrahedron has one sixth of the volume of the parallelepiped on the same three edges."]))
    A, B, C, D = (0, 0, 0), (3, 0, 0), (0, 4, 0), (0, 0, 6)
    vol = rad(sp.Abs(M([sub(A, B), sub(A, C), sub(A, D)]).det()) / 6)
    h = rad(3 * vol / (norm(cross(sub(A, B), sub(A, C))) / 2))
    items.append(item_num("mp-vl-7", rf"The height of the tetrahedron $A{pt3_tex(A)}$, $B{pt3_tex(B)}$, $C{pt3_tex(C)}$, $D{pt3_tex(D)}$ from $D$ on the face $ABC$. The unit is lu: give the number only.", h,
                          r"$V=12$ and the area of $ABC$ is $6$; from $V=\dfrac13Sh$: $h=\dfrac{3V}{S}=6$.", ["Use $V=\\dfrac13\\times(\\text{area of the base})\\times h$."]))
    assert h == 6
    return items


def double_items() -> list[dict]:
    items = []
    cases = (((1, 2, 0), (0, 1, 3), (2, 0, 1)), ((1, 0, 1), (2, 1, 0), (0, 3, 1)), ((3, 1, 0), (1, 1, 1), (0, 2, 1)), ((1, 1, 2), (2, 0, 1), (1, 3, 0)), ((2, 0, 0), (0, 1, 1), (1, 1, 1)))
    for n, (u, v, w) in enumerate(cases, 1):
        res = cross(u, cross(v, w))
        # BAC-CAB: [u,[v,w]] = v <u,w> - w <u,v>
        alt = tuple(rad(v[i] * dot(u, w) - w[i] * dot(u, v)) for i in range(3))
        assert res == alt and tuple(M(u).cross(M(v).cross(M(w)))) == res
        items.append(item_pt(f"mp-dc-{n}", rf"$\crossp{{\vec u}}{{\crossp{{\vec v}}{{\vec w}}}}$ for $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$.", res,
                             rf"$\crossp{{\vec v}}{{\vec w}}={vt(cross(v, w))}$ and then $\crossp{{\vec u}}{{\crossp{{\vec v}}{{\vec w}}}}={vt(res)}$. Check: $\vec v\dotp{{\vec u}}{{\vec w}}-\vec w\dotp{{\vec u}}{{\vec v}}$ gives the same vector.",
                             ["Either compute the two cross products, or use $\\crossp{\\vec u}{\\crossp{\\vec v}{\\vec w}}=\\vec v\\dotp{\\vec u}{\\vec w}-\\vec w\\dotp{\\vec u}{\\vec v}$."]))
    u, v, w = cases[0]
    left, right = cross(cross(u, v), w), cross(u, cross(v, w))
    items.append(mc("mp-dc-6", rf"For $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$, is $\crossp{{\crossp{{\vec u}}{{\vec v}}}}{{\vec w}}=\crossp{{\vec u}}{{\crossp{{\vec v}}{{\vec w}}}}$?", ["Yes", "No"], 0 if left == right else 1,
                    r"Compute both sides.", rf"The left side is ${vt(left)}$ and the right side is ${vt(right)}$. " + ("They are equal." if left == right else "They differ: the cross product is not associative.")))
    assert left != right
    u, v, w, x_ = (1, 2, 0), (0, 1, 1), (2, 0, 1), (1, 1, 1)
    lhs = dot(cross(u, v), cross(w, x_))
    rhs = rad(dot(u, w) * dot(v, x_) - dot(u, x_) * dot(v, w))
    assert lhs == rhs
    items.append(item_num("mp-dc-7", rf"Use Lagrange's identity to compute $\dotp{{\crossp{{\vec u}}{{\vec v}}}}{{\crossp{{\vec w}}{{\vec x}}}}$ for $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$, $\vec x={vt(x_)}$.", lhs,
                         rf"$\dotp{{\vec u}}{{\vec w}}\dotp{{\vec v}}{{\vec x}}-\dotp{{\vec u}}{{\vec x}}\dotp{{\vec v}}{{\vec w}}={tex(dot(u, w))}\cdot{tex(dot(v, x_))}-{tex(dot(u, x_))}\cdot{tex(dot(v, w))}={tex(lhs)}$.",
                         ["$\\dotp{\\crossp{\\vec u}{\\vec v}}{\\crossp{\\vec w}{\\vec x}}=\\dotp{\\vec u}{\\vec w}\\dotp{\\vec v}{\\vec x}-\\dotp{\\vec u}{\\vec x}\\dotp{\\vec v}{\\vec w}$."]))
    u, v = (1, 2, 2), (2, -1, 2)
    lhs = rad(norm(u) ** 2 * norm(v) ** 2 - dot(u, v) ** 2)
    assert lhs == norm(cross(u, v)) ** 2
    items.append(item_num("mp-dc-8", rf"Compute $\norm{{\crossp{{\vec u}}{{\vec v}}}}^2$ for $\vec u={vt(u)}$ and $\vec v={vt(v)}$ using $\norm{{\vec u}}^2\norm{{\vec v}}^2-\dotp{{\vec u}}{{\vec v}}^2$.", lhs,
                         rf"$9\cdot9-{tex(dot(u, v))}^2={tex(lhs)}$.", ["Compute the norms and the dot product."]))
    u, v, w = (1, 2, 3), (4, 5, 6), (7, 8, 10)
    jac = tuple(rad(a + b + c) for a, b, c in zip(cross(u, cross(v, w)), cross(v, cross(w, u)), cross(w, cross(u, v)), strict=True))
    assert jac == (0, 0, 0)
    items.append(item_pt("mp-dc-9", rf"Compute $\crossp{{\vec u}}{{\crossp{{\vec v}}{{\vec w}}}}+\crossp{{\vec v}}{{\crossp{{\vec w}}{{\vec u}}}}+\crossp{{\vec w}}{{\crossp{{\vec u}}{{\vec v}}}}$ for $\vec u={vt(u)}$, $\vec v={vt(v)}$, $\vec w={vt(w)}$ (the Jacobi identity).", jac,
                         r"By the Jacobi identity the sum is always the zero vector.", ["Use the identity $\\vec v\\dotp{\\vec u}{\\vec w}-\\vec w\\dotp{\\vec u}{\\vec v}$ for each term; they cancel."]))
    u, v = (1, 0, 0), (0, 1, 0)
    items.append(item_pt("mp-dc-10", r"Compute $\crossp{\vec i}{\crossp{\vec i}{\vec j}}$.", cross((1, 0, 0), cross((1, 0, 0), (0, 1, 0))),
                         r"$\crossp{\vec i}{\vec j}=\vec k$ and $\crossp{\vec i}{\vec k}=-\vec j$, so the result is $(0,-1,0)$.", ["First $\\crossp{\\vec i}{\\vec j}=\\vec k$."]))
    assert u is not None and v is not None
    return items


@with_units
def register() -> None:
    sets = [
        ("l01-points-and-vectors", U1, "more-points", "More practice: points and vectors.", points_items(), True),
        ("l02-operations-on-vectors", U1, "more-operations", "More practice: operations on vectors.", operations_items(), True),
        ("l03-collinearity-and-bases", U1, "more-independence", "More practice: collinearity, independence and bases.", independence_items(), True),
        ("l04-norm-unit-vectors-direction-cosines", U1, "more-norms", "More practice: norms and direction cosines.", norm_items(), False),
        ("l01-dot-product", U2, "more-dot", "More practice: the dot product.", dot_items(), False),
        ("l02-projection-and-inequalities", U2, "more-projection", "More practice: projections.", projection_items(), False),
        ("l03-cross-product", U2, "more-cross", "More practice: the cross product.", cross_items(), False),
        ("l04-areas", U2, "more-areas", "More practice: areas.", area_items(), False),
        ("l05-box-product", U2, "more-box", "More practice: the box product.", box_items(), False),
        ("l06-volumes", U2, "more-volumes", "More practice: volumes.", volume_items(), False),
        ("l07-double-cross-product", U2, "more-double", "More practice: the double cross product.", double_items(), False),
    ]
    for lesson, unit, sid, task, items, orphan in sets:
        add_extra(f"{unit}/{lesson}", exset_plain(sid, task, items, format=FMT), SCRIPT, orphan=orphan)
