"""Exercises of Course 2, Module 1, Unit 4, Lesson 3: absolute extrema on closed bounded regions (original exercises).

Each extreme value is computed exactly (interior critical points, then every part of the boundary) and then checked
against a dense numerical search of the region, so a wrong candidate cannot slip through."""

from __future__ import annotations

import itertools
import math


import sympy as sp
from toolkit import P, eng, ex, exset_plain, simp, tex, write_exercises, x, y

lam = sp.Symbol("lam", real=True)
s = sp.Symbol("s", real=True)


def kind_of(value: sp.Expr) -> str:
    return "number" if value.is_Rational else "expression"


def feasible(pt: tuple, ineq: list) -> bool:
    return all(sp.simplify(c.subs({x: pt[0], y: pt[1]})) >= 0 for c in ineq)


def interior_critical(f: sp.Expr, ineq: list) -> list[tuple]:
    sols = sp.solve([sp.diff(f, x), sp.diff(f, y)], [x, y], dict=True)
    pts = [(simp(sol[x]), simp(sol[y])) for sol in sols if x in sol and y in sol]
    return [p for p in pts if all(c.is_real for c in p) and feasible(p, ineq)]


def segment_candidates(f: sp.Expr, p: tuple, q: tuple, ineq: list) -> list[tuple]:
    """End points and critical points of f on the segment pq."""
    pts = [p, q]
    sub = {x: p[0] + s * (q[0] - p[0]), y: p[1] + s * (q[1] - p[1])}
    g = sp.expand(f.subs(sub, simultaneous=True))
    for root in sp.solve(sp.diff(g, s), s):
        if root.is_real and 0 < root < 1:
            pts.append((simp(sub[x].subs(s, root)), simp(sub[y].subs(s, root))))
    return pts


def circle_candidates(f: sp.Expr, radius2: sp.Expr) -> list[tuple]:
    sols = sp.solve([sp.diff(f, x) - lam * 2 * x, sp.diff(f, y) - lam * 2 * y, x**2 + y**2 - radius2], [x, y, lam], dict=True)
    return [(simp(sol[x]), simp(sol[y])) for sol in sols if sol[x].is_real and sol[y].is_real]


def extrema(f: sp.Expr, ineq: list, candidates: list[tuple], box: tuple) -> tuple[sp.Expr, sp.Expr, tuple, tuple]:
    vals = [(simp(f.subs({x: p[0], y: p[1]})), p) for p in candidates]
    vmax, pmax = max(vals, key=lambda v: float(v[0]))
    vmin, pmin = min(vals, key=lambda v: float(v[0]))
    # independent check: dense grid over the bounding box restricted to the region
    fl = sp.lambdify((x, y), f, "math")
    cl = [sp.lambdify((x, y), c, "math") for c in ineq]
    n = 400
    lo = math.inf
    hi = -math.inf
    for i in range(n + 1):
        xv = box[0] + (box[1] - box[0]) * i / n
        for j in range(n + 1):
            yv = box[2] + (box[3] - box[2]) * j / n
            if all(c(xv, yv) >= -1e-12 for c in cl):
                v = fl(xv, yv)
                lo = min(lo, v)
                hi = max(hi, v)
    step = max(box[1] - box[0], box[3] - box[2]) / n
    tol = 12 * step * (1 + abs(float(vmax)) + abs(float(vmin)))
    assert abs(hi - float(vmax)) < tol, (f, float(vmax), hi)
    assert abs(lo - float(vmin)) < tol, (f, float(vmin), lo)
    return vmax, vmin, pmax, pmin


def rect_items() -> list[dict]:
    items: list[dict] = []

    def one(i: str, f: sp.Expr, ftex: str, a: int, b: int, c: int, d: int, how: str) -> None:
        ineq = [x - a, b - x, y - c, d - y]
        corners = list(itertools.product((a, b), (c, d)))
        cand = interior_critical(f, ineq) + corners
        cand += [p for (p0, p1) in [((a, c), (b, c)), ((b, c), (b, d)), ((b, d), (a, d)), ((a, d), (a, c))] for p in segment_candidates(f, p0, p1, ineq)]
        vmax, vmin, pmax, pmin = extrema(f, ineq, cand, (a, b, c, d))
        region = rf"the rectangle $ {a}\le x\le{b},\ {c}\le y\le{d}$".replace("$ ", "$")
        crit = interior_critical(f, ineq)
        crit_txt = (
            "The critical point inside the region is " + ",\\ ".join(rf"$({tex(p[0])},{tex(p[1])})$" for p in crit) + ". "
            if crit else "There is no critical point inside the region. "
        )
        sol = (
            crit_txt + "Checking the four edges and the corners gives the candidates; "
            rf"the largest value is ${tex(vmax)}$ at $({tex(pmax[0])},{tex(pmax[1])})$ and the smallest is ${tex(vmin)}$ at $({tex(pmin[0])},{tex(pmin[1])})$."
        )
        items.append(ex(
            f"ae-{i}a", rf"Find the absolute maximum value of $f(x,y)={ftex}$ on {region}.", kind_of(vmax), eng(vmax),
            hints=["Compare the value at the critical points inside with the extreme values on the four edges, corners included."], solution=sol))
        items.append(ex(
            f"ae-{i}b", rf"Find the absolute minimum value of $f(x,y)={ftex}$ on {region}.", kind_of(vmin), eng(vmin),
            hints=["Compare the value at the critical points inside with the extreme values on the four edges, corners included."], solution=sol))

    one("01", P("x*y-x-y"), "xy-x-y", 0, 2, 0, 3, "")
    one("02", P("x^2+y^2-4*x"), "x^2+y^2-4x", 0, 3, -1, 2, "")
    one("03", P("x^3-3*x+y^2"), "x^3-3x+y^2", -2, 2, -1, 1, "")
    one("04", P("x^2*y-y"), "x^2y-y", -1, 2, 0, 2, "")
    one("05", P("2*x+3*y"), "2x+3y", 0, 4, 0, 1, "")
    return items


def triangle_items() -> list[dict]:
    items: list[dict] = []
    ineq = [x, y, 2 - x - y]
    f = P("x^2-x*y+y^2-x-y")
    cand = interior_critical(f, ineq) + [(0, 0), (2, 0), (0, 2)]
    for p, q in (((0, 0), (2, 0)), ((2, 0), (0, 2)), ((0, 2), (0, 0))):
        cand += segment_candidates(f, p, q, ineq)
    vmax, vmin, pmax, pmin = extrema(f, ineq, cand, (0, 2, 0, 2))
    sol = (
        r"Inside: $f_x=2x-y-1=0$ and $f_y=-x+2y-1=0$ give $(1,1)$, which lies on the hypotenuse; so we check it with the edges. "
        rf"Comparing the candidates, the largest value is ${tex(vmax)}$ and the smallest is ${tex(vmin)}$."
    )
    stmt = r"on the triangle with vertices $(0,0)$, $(2,0)$ and $(0,2)$"
    items.append(ex("ae-t1a", rf"Find the absolute maximum value of $f(x,y)=x^2-xy+y^2-x-y$ {stmt}.", kind_of(vmax), eng(vmax),
                    hints=["The triangle is $x\\ge0,\\ y\\ge0,\\ x+y\\le2$. Check the three edges and the corners."], solution=sol))
    items.append(ex("ae-t1b", rf"Find the absolute minimum value of $f(x,y)=x^2-xy+y^2-x-y$ {stmt}.", kind_of(vmin), eng(vmin),
                    hints=["The triangle is $x\\ge0,\\ y\\ge0,\\ x+y\\le2$. Check the three edges and the corners."], solution=sol))
    return items


def disc_items() -> list[dict]:
    items: list[dict] = []

    def one(i: str, f: sp.Expr, ftex: str, r2: int, hint: str) -> None:
        ineq = [r2 - x**2 - y**2]
        cand = interior_critical(f, ineq) + circle_candidates(f, sp.Integer(r2))
        rad = sp.sqrt(r2)
        vmax, vmin, pmax, pmin = extrema(f, ineq, cand, (-float(rad), float(rad), -float(rad), float(rad)))
        sol = (
            rf"Inside the disc the critical point(s): {', '.join(rf'$({tex(p[0])},{tex(p[1])})$' for p in interior_critical(f, ineq)) or 'none'}. "
            rf"On the circle (Lagrange multipliers or the parametrization $x={tex(rad)}\cos\theta,\ y={tex(rad)}\sin\theta$) the extreme values are found at the candidate points. "
            rf"Comparing everything, the largest value is ${tex(vmax)}$ and the smallest is ${tex(vmin)}$."
        )
        stmt = rf"on the disc $x^2+y^2\le{r2}$"
        items.append(ex(f"ae-{i}a", rf"Find the absolute maximum value of $f(x,y)={ftex}$ {stmt}.", kind_of(vmax), eng(vmax), hints=[hint], solution=sol))
        items.append(ex(f"ae-{i}b", rf"Find the absolute minimum value of $f(x,y)={ftex}$ {stmt}.", kind_of(vmin), eng(vmin), hints=[hint], solution=sol))

    one("d1", P("x^2+2*y^2"), "x^2+2y^2", 1, "Check the critical point inside and the circle $x^2+y^2=1$.")
    one("d2", P("x-2*y"), "x-2y", 5, r"$\nabla f=(1,-2)$ never vanishes, so both extreme values are on the circle.")
    one("d3", P("x^2-y^2"), "x^2-y^2", 4, "Check the origin and the circle $x^2+y^2=4$.")
    one("d4", P("x^2+y^2-2*x"), "x^2+y^2-2x", 4, "Check the critical point $(1,0)$ and the circle.")
    return items


def concept_items() -> list[dict]:
    return [
        ex(
            "ae-c1", r"On which of these regions is a continuous function guaranteed to have an absolute maximum and an absolute minimum?",
            "multiple_choice", "2",
            choices=[
                {"text": r"the open disc $x^2+y^2<1$", "value": "1"},
                {"text": r"the closed square $0\le x\le1,\ 0\le y\le1$", "value": "2"},
                {"text": r"the half-plane $y\ge0$", "value": "3"},
                {"text": r"the whole plane", "value": "4"},
            ],
            correctIndex=1, hints=["The region must be closed (contain its boundary) and bounded."],
            solution=r"Only the closed square is both closed and bounded. The open disc is not closed, and the half-plane and the plane are not bounded.",
        ),
        ex(
            "ae-c2", r"The function $f(x,y)=x^2+y^2$ has no absolute maximum on which region?",
            "multiple_choice", "3",
            choices=[
                {"text": r"the closed disc $x^2+y^2\le9$", "value": "1"},
                {"text": r"the square $|x|\le2,\ |y|\le2$", "value": "2"},
                {"text": r"the half-plane $x\ge0$", "value": "3"},
            ],
            correctIndex=2, hints=["Is the region bounded?"],
            solution=r"On the half-plane, which is not bounded, $f$ grows without limit. On the closed disc and the closed square the extreme value theorem guarantees a maximum.",
        ),
    ]


def build() -> None:
    write_exercises(
        "mvc/m01-derivatives/u04-optimization/l03-absolute-extrema",
        [
            exset_plain("rectangles", "Absolute extreme values on a rectangle.", rect_items(),
                        format="Type an exact value such as `11/3`."),
            exset_plain("triangle", "Absolute extreme values on a triangle.", triangle_items(), format="Type an exact value such as `11/3`."),
            exset_plain("discs", "Absolute extreme values on a disc.", disc_items(), format="Type an exact value such as `sqrt(5)` or `7/2`."),
            exset_plain("concepts", "When do absolute extreme values exist?", concept_items()),
        ],
        "mvc_extrema.py",
    )
