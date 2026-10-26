"""Exact analysis of a triangle given by the coordinates of its three vertices.

Everything is computed with SymPy on exact numbers (integers, fractions, radicals, pi): never a float, except the
plain drawing coordinates of ``figure``, which the browser uses to draw and never shows as results.
All the results are LaTeX strings in the notation of the platform (fractions as \\dfrac, vectors as columns).
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

import sympy as sp

from .errors import EngineError

X, Y = sp.symbols("x y", real=True)
NUMBER = re.compile(r"^[+-]?(\d+(\.\d+)?|\.\d+)(/\d+)?$")
MAX_COORD = 10_000
MAX_DENOMINATOR = 1_000


class TriangleError(EngineError):
    code = "triangle"


def parse_coordinate(text: str) -> sp.Rational:
    """A whole number, a fraction such as -7/6 or a finite decimal such as 0.5 (read as the exact fraction 1/2)."""
    t = text.strip().replace(" ", "")
    if not NUMBER.match(t):
        raise TriangleError("A coordinate must be a whole number, a fraction such as 7/6, or a decimal such as 0.5.", "bad_coordinate")
    value = sp.Rational(t)
    if abs(value) > MAX_COORD or value.q > MAX_DENOMINATOR:
        raise TriangleError("The coordinates are too large or too complicated: use numbers up to 10000 with a denominator up to 1000.", "coordinate_range")
    return value


# --- LaTeX ---------------------------------------------------------------------------------------------------------------------------------------------------
def has_nested_radical(e: sp.Expr) -> bool:
    """A radical of a sum, such as sqrt(2*sqrt(3)+5), which cannot be written with plain radicals only."""
    return any(isinstance(p.base, sp.Add) and p.exp.is_Rational and not p.exp.is_Integer for p in e.atoms(sp.Pow))


@lru_cache(maxsize=8192)
def _simp(e: sp.Expr) -> sp.Expr:
    if e.is_Rational or not e.free_symbols and e.is_Atom:
        return e
    # sums and products of radicals: rationalise the denominators and expand (about a hundred times faster than simplify, same result)
    out = sp.expand(sp.radsimp(sp.together(e)))
    return sp.simplify(out) if has_nested_radical(out) else out


def simp(e: Any) -> sp.Expr:
    """The canonical exact form of a number: simplified radicals and rationalised denominators (cached: the same values come back many times)."""
    return _simp(sp.sympify(e))


@lru_cache(maxsize=8192)
def _tx(e: sp.Expr) -> str:
    text = sp.latex(e, fold_short_frac=False, mul_symbol=None).replace("\\frac", "\\dfrac")
    return text.replace("\\operatorname{acos}", "\\arccos").replace("\\operatorname{asin}", "\\arcsin")


def tx(e: Any) -> str:
    """LaTeX of an exact value, with fractions as \\dfrac (spec section 6.4)."""
    return _tx(simp(e))


def small(latex: str) -> str:
    """Fractions inside a fraction are drawn in the smaller style."""
    return latex.replace("\\dfrac", "\\tfrac")


def pt(p: tuple[sp.Expr, sp.Expr]) -> str:
    return rf"\left({tx(p[0])},\,{tx(p[1])}\right)"


def col(u: tuple[sp.Expr, sp.Expr]) -> str:
    return rf"\begin{{pmatrix}}{tx(u[0])}\\[0.7em]{tx(u[1])}\end{{pmatrix}}"


def lin_comb(terms: list[tuple[Any, str]]) -> str:
    """A sum such as ``4x-3y+2``: zero terms are left out, a coefficient 1 is not written, signs are joined to the operators."""
    out = ""
    for coef, symbol in terms:
        c = simp(coef)
        if c == 0:
            continue
        negative = bool(c.is_number and c.is_real and sp.N(c) < 0)
        body = simp(-c) if negative else c
        if symbol and body == 1:
            text = symbol
        else:
            text = tx(body)
            if isinstance(body, sp.Add):
                text = rf"\left({text}\right)"
            text += symbol
        out += ("-" if negative else ("+" if out else "")) + text
    return out or "0"


def add(p: tuple[sp.Expr, sp.Expr], q: tuple[sp.Expr, sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
    return (p[0] + q[0], p[1] + q[1])


def sub(p: tuple[sp.Expr, sp.Expr], q: tuple[sp.Expr, sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
    return (p[0] - q[0], p[1] - q[1])


def scale(k: sp.Expr, p: tuple[sp.Expr, sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
    return (k * p[0], k * p[1])


def dist(p: tuple[sp.Expr, sp.Expr], q: tuple[sp.Expr, sp.Expr]) -> sp.Expr:
    return simp(sp.sqrt(sp.expand((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)))


def ptsimp(p: tuple[sp.Expr, sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
    return (simp(p[0]), simp(p[1]))


# --- lines ----------------------------------------------------------------------------------------------------------------------------------------------------
def primitive_direction(d: tuple[sp.Expr, sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
    """A rational direction becomes the smallest whole-number vector with the same sense; anything else is only simplified."""
    d = ptsimp(d)
    if d[0].is_Rational and d[1].is_Rational:
        m = sp.ilcm(d[0].q, d[1].q)
        a, b = int(d[0] * m), int(d[1] * m)
        g = sp.igcd(a, b) or 1
        return (sp.Integer(a // g), sp.Integer(b // g))
    return d


def common_denominator(*values: sp.Expr) -> sp.Integer:
    """The smallest whole number that clears every rational coefficient in expressions such as 59/12 + 5*sqrt(145)/12."""
    denominators = [1]
    for v in values:
        for coefficient in sp.expand(v).as_coefficients_dict().values():
            if coefficient.is_Rational:
                denominators.append(int(coefficient.q))
    return sp.Integer(sp.ilcm(*denominators))


def normalized_coefficients(a: sp.Expr, b: sp.Expr, c: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """ax+by+c=0 with whole-number coefficients without common factor when they are rational, the first one of a, b positive."""
    a, b, c = simp(a), simp(b), simp(c)
    if all(v.is_Rational for v in (a, b, c)):
        m = sp.ilcm(a.q, b.q, c.q)
        ia, ib, ic = int(a * m), int(b * m), int(c * m)
        g = sp.igcd(sp.igcd(ia, ib), ic) or 1
        a, b, c = sp.Integer(ia // g), sp.Integer(ib // g), sp.Integer(ic // g)
    else:
        # radicals: the first coefficient becomes 1, then the rational denominators are cleared (12x + (59 + 5*sqrt(145))y - ... = 0)
        lead = a if a != 0 else b
        a, b, c = simp(a / lead), simp(b / lead), simp(c / lead)
        m = common_denominator(a, b, c)
        a, b, c = simp(a * m), simp(b * m), simp(c * m)
    first = a if a != 0 else b
    if sp.N(first) < 0:
        a, b, c = -a, -b, -c
    return a, b, c


def implicit_coefficients(p: tuple[sp.Expr, sp.Expr], direction: tuple[sp.Expr, sp.Expr]) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """(a, b, c) of ax+by+c=0 for the line through p with the given direction: d2(x-p1)-d1(y-p2)=0."""
    d = primitive_direction(direction)
    p = ptsimp(p)
    return normalized_coefficients(d[1], -d[0], d[0] * p[1] - d[1] * p[0])


def line_forms(p: tuple[sp.Expr, sp.Expr], direction: tuple[sp.Expr, sp.Expr]) -> dict[str, str | None]:
    """The eight equations of the line through p with the given direction (the lesson 'The eight equations of a straight line')."""
    p = ptsimp(p)
    d = primitive_direction(direction)
    a, b, c = implicit_coefficients(p, d)
    lam = r"\lambda"
    forms: dict[str, str | None] = {}
    forms["vector"] = rf"{col((X, Y))}={col(p)}+{lam}{col(d)}"
    rows = []
    for name, base, comp in (("x", p[0], d[0]), ("y", p[1], d[1])):
        rows.append(rf"{name}={lin_comb([(base, ''), (comp, lam)])}")
    forms["parametric"] = r"\begin{cases}" + r"\\".join(rows) + r"\end{cases}"
    if d[0] == 0:
        forms["symmetric"] = rf"x={tx(p[0])}"
    elif d[1] == 0:
        forms["symmetric"] = rf"y={tx(p[1])}"
    else:
        # a fraction inside the numerator or the denominator of a fraction is drawn smaller (\tfrac)
        num_x, num_y = small(lin_comb([(1, "x"), (-p[0], "")])), small(lin_comb([(1, "y"), (-p[1], "")]))
        forms["symmetric"] = rf"\dfrac{{{num_x}}}{{{small(tx(d[0]))}}}=\dfrac{{{num_y}}}{{{small(tx(d[1]))}}}"
    forms["implicit"] = rf"{lin_comb([(a, 'x'), (b, 'y'), (c, '')])}=0"
    if b == 0:
        forms["explicit"] = rf"x={tx(-c / a)}"
    else:
        forms["explicit"] = rf"y={lin_comb([(-a / b, 'x'), (-c / b, '')])}"
    norm_squared = simp(sp.expand(a**2 + b**2))
    n = simp(sp.sqrt(norm_squared))
    eps = -1 if sp.N(c) > 0 else 1  # the constant term of the normal form is minus the distance of the line from the origin: not positive
    if has_nested_radical(n):
        # e.g. an angle bisector: the length of the normal vector is a radical of a radical, so keep the division visible
        forms["normal"] = rf"\dfrac{{{lin_comb([(eps * a, 'x'), (eps * b, 'y'), (eps * c, '')])}}}{{\sqrt{{{tx(norm_squared)}}}}}=0"
    else:
        forms["normal"] = rf"{lin_comb([(eps * a / n, 'x'), (eps * b / n, 'y'), (eps * c / n, '')])}=0"
    trig = lin_comb([(a, r"\cos\theta"), (b, r"\sin\theta")])
    forms["polar"] = rf"r{trig}" if a == 0 or b == 0 else rf"r\left({trig}\right)"
    if c != 0:
        constant = lin_comb([(c, "")])  # signed, and in brackets when it is a sum such as -74 + 25*sqrt(10)
        forms["polar"] += constant if constant.startswith("-") else f"+{constant}"
    forms["polar"] += "=0"
    forms["intercept"] = rf"\dfrac{{x}}{{{small(tx(-c / a))}}}+\dfrac{{y}}{{{small(tx(-c / b))}}}=1" if a != 0 and b != 0 and c != 0 else None
    return forms


def line_through(p: tuple[sp.Expr, sp.Expr], q: tuple[sp.Expr, sp.Expr]) -> dict[str, str | None]:
    return line_forms(p, sub(q, p))


def chord_in_triangle(p: tuple[sp.Expr, sp.Expr], d: tuple[sp.Expr, sp.Expr], verts: list[tuple[sp.Expr, sp.Expr]]) -> tuple[tuple[sp.Expr, sp.Expr], tuple[sp.Expr, sp.Expr]]:
    """The two points where the line meets the boundary of the triangle."""
    found: list[tuple[sp.Expr, sp.Expr]] = []
    for i in range(3):
        u, v = verts[i], verts[(i + 1) % 3]
        e = sub(v, u)
        det = simp(e[0] * d[1] - e[1] * d[0])
        if det == 0:
            continue
        w = sub(u, p)
        # p + t*d = u + s*e: a cross product with d gives the parameter s of the point on the side
        s = simp((w[1] * d[0] - w[0] * d[1]) / det)
        if sp.N(s) < -1e-12 or sp.N(s) > 1 + 1e-12:
            continue
        q = ptsimp(add(u, scale(s, e)))
        if not any(simp(q[0] - r[0]) == 0 and simp(q[1] - r[1]) == 0 for r in found):
            found.append(q)
    if len(found) < 2:
        raise TriangleError("The line does not cross the triangle.", "no_chord")
    best = max(((i, j) for i in range(len(found)) for j in range(i + 1, len(found))), key=lambda ij: float(sp.N(dist(found[ij[0]], found[ij[1]]))))
    return found[best[0]], found[best[1]]


# --- circles ----------------------------------------------------------------------------------------------------------------------------------------------
def square_term(var: str, c: sp.Expr) -> str:
    c = simp(c)
    if c == 0:
        return rf"{var}^{{2}}"
    return rf"\left({lin_comb([(1, var), (-c, '')])}\right)^{{2}}"


def circle_forms(center: tuple[sp.Expr, sp.Expr], radius: sp.Expr) -> dict[str, str]:
    center = ptsimp(center)
    radius = simp(radius)
    r2 = simp(radius**2)
    p, q = center
    # the pieces are built first: a backslash is not allowed inside an f-string expression before Python 3.12
    x_sq, y_sq = "x^{2}", "y^{2}"
    cos_t, sin_t = r"\cos t", r"\sin t"
    general = lin_comb([(1, x_sq), (1, y_sq), (-2 * p, "x"), (-2 * q, "y"), (p**2 + q**2 - r2, "")])
    x_of_t, y_of_t = lin_comb([(p, ""), (radius, cos_t)]), lin_comb([(q, ""), (radius, sin_t)])
    return {
        "center": pt(center),
        "radius": tx(radius),
        "analytic": f"{square_term('x', p)}+{square_term('y', q)}={tx(r2)}",
        "general": f"{general}=0",
        "parametric": r"\begin{cases}x=" + x_of_t + r"\\y=" + y_of_t + r"\end{cases},\ t\in[0,2\pi)",
        "perimeter": tx(2 * sp.pi * radius),
        "area": tx(sp.pi * r2),
    }


def angle_info(cos_value: sp.Expr) -> dict[str, str | None]:
    cos_value = simp(cos_value)
    angle = sp.acos(cos_value)
    ratio = simp(angle / sp.pi)
    return {"cos": tx(cos_value), "angle": tx(angle), "degrees": rf"{tx(ratio * 180)}^\circ" if ratio.is_Rational else None}


# --- the triangle ------------------------------------------------------------------------------------------------------------------------------------------
def analyze(raw: list[list[str]]) -> dict[str, Any]:
    if len(raw) != 3 or any(len(p) != 2 for p in raw):
        raise TriangleError("Give the three vertices, each with an x and a y.", "three_points")
    P = [(parse_coordinate(p[0]), parse_coordinate(p[1])) for p in raw]
    A, B, C = P
    if len(set(P)) < 3:
        raise TriangleError("The three vertices must be different points.", "same_points")
    twice_signed = (B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1])
    if twice_signed == 0:
        raise TriangleError("The three points are on one straight line: they do not make a triangle.", "collinear")
    names = ["A", "B", "C"]
    # sides: a = BC, b = CA, c = AB
    a, b, c = dist(B, C), dist(C, A), dist(A, B)
    sq = {"a": sp.expand((B[0] - C[0]) ** 2 + (B[1] - C[1]) ** 2), "b": sp.expand((C[0] - A[0]) ** 2 + (C[1] - A[1]) ** 2), "c": sp.expand((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2)}
    side_names = {"a": "BC", "b": "CA", "c": "AB"}
    side_len = {"a": a, "b": b, "c": c}
    area = simp(sp.Abs(twice_signed) / 2)
    perimeter = simp(a + b + c)
    s = simp(perimeter / 2)
    r_in = simp(area / s)
    R_circ = simp(a * b * c / (4 * area))

    biggest = max(sq.values())
    smallest = min(sq.values())
    longest = [side_names[k] for k in "abc" if sq[k] == biggest]
    shortest = [side_names[k] for k in "abc" if sq[k] == smallest]
    equal_pairs = sum(1 for i, j in ((0, 1), (0, 2), (1, 2)) if sq["abc"[i]] == sq["abc"[j]])
    by_sides = "equilateral" if equal_pairs == 3 else ("isosceles" if equal_pairs >= 1 else "scalene")
    others = sum(sq.values()) - biggest  # the sum of the squares of the two shorter sides, compared with the longest (converse of Pythagoras)
    by_angles = "right" if biggest == others else ("acute" if biggest < others else "obtuse")

    G = ptsimp(scale(sp.Rational(1, 3), add(add(A, B), C)))
    incenter = ptsimp(scale(1 / (a + b + c), add(add(scale(a, A), scale(b, B)), scale(c, C))))
    den = 2 * (A[0] * (B[1] - C[1]) + B[0] * (C[1] - A[1]) + C[0] * (A[1] - B[1]))
    o2 = {k: P[i][0] ** 2 + P[i][1] ** 2 for i, k in enumerate(names)}
    circumcenter = ptsimp((
        (o2["A"] * (B[1] - C[1]) + o2["B"] * (C[1] - A[1]) + o2["C"] * (A[1] - B[1])) / den,
        (o2["A"] * (C[0] - B[0]) + o2["B"] * (A[0] - C[0]) + o2["C"] * (B[0] - A[0])) / den,
    ))
    H = ptsimp(sub(add(add(A, B), C), scale(2, circumcenter)))
    N = ptsimp(scale(sp.Rational(1, 2), add(circumcenter, H)))

    angles = {
        "A": angle_info((sq["b"] + sq["c"] - sq["a"]) / (2 * b * c)),
        "B": angle_info((sq["a"] + sq["c"] - sq["b"]) / (2 * a * c)),
        "C": angle_info((sq["a"] + sq["b"] - sq["c"]) / (2 * a * b)),
    }

    lines: list[dict[str, Any]] = []

    def add_line(group: str, label: str, forms: dict[str, str | None], length: sp.Expr, ends: tuple[tuple[sp.Expr, sp.Expr], tuple[sp.Expr, sp.Expr]], extra: dict[str, str] | None = None) -> None:
        lines.append({"id": f"{group}-{label}", "group": group, "label": label, "length": tx(length), "from_point": pt(ends[0]), "to_point": pt(ends[1]), "forms": forms, "extra": extra or {}})

    # the sides and their perpendicular bisectors
    for k, (u, v, label) in {"a": (B, C, "BC"), "b": (C, A, "CA"), "c": (A, B, "AB")}.items():
        add_line("side", label, line_through(u, v), side_len[k], (u, v))
    for _, (u, v, label) in {"a": (B, C, "BC"), "b": (C, A, "CA"), "c": (A, B, "AB")}.items():
        mid = ptsimp(scale(sp.Rational(1, 2), add(u, v)))
        e = sub(v, u)
        direction = (-e[1], e[0])
        p1, p2 = chord_in_triangle(mid, direction, [A, B, C])
        add_line("perpbisector", label, line_forms(mid, direction), dist(p1, p2), (p1, p2), {"midpoint": pt(mid)})
    # the medians, altitudes and bisectors of the vertices
    for name, V, U, W, opp in (("A", A, B, C, "a"), ("B", B, C, A, "b"), ("C", C, A, B, "c")):
        opposite = {"a": a, "b": b, "c": c}[opp]
        mid = ptsimp(scale(sp.Rational(1, 2), add(U, W)))
        add_line("median", name, line_through(V, mid), dist(V, mid), (V, mid), {"foot": pt(mid)})
        e = sub(W, U)
        t = simp(((V[0] - U[0]) * e[0] + (V[1] - U[1]) * e[1]) / (e[0] ** 2 + e[1] ** 2))
        foot = ptsimp(add(U, scale(t, e)))
        add_line("altitude", name, line_forms(V, (-e[1], e[0])), simp(2 * area / opposite), (V, foot), {"foot": pt(foot)})
        # the bisector from V meets the opposite side UW at (|VW|*U + |VU|*W)/(|VW|+|VU|)
        lenVU, lenVW = dist(V, U), dist(V, W)
        d_foot = ptsimp(scale(1 / (lenVU + lenVW), add(scale(lenVW, U), scale(lenVU, W))))
        add_line("bisector", name, line_through(V, d_foot), dist(V, d_foot), (V, d_foot), {"foot": pt(d_foot)})

    euler = None if simp(circumcenter[0] - H[0]) == 0 and simp(circumcenter[1] - H[1]) == 0 else line_through(circumcenter, H)

    excircles = {}
    for name, (sign_a, sign_b, sign_c, rad_s) in {"A": (-1, 1, 1, s - a), "B": (1, -1, 1, s - b), "C": (1, 1, -1, s - c)}.items():
        w = sign_a * a + sign_b * b + sign_c * c
        center = ptsimp(scale(1 / w, add(add(scale(sign_a * a, A), scale(sign_b * b, B)), scale(sign_c * c, C))))
        excircles[name] = {"center": pt(center), "radius": tx(area / rad_s)}

    # drawing coordinates only (plain numbers for the browser)
    f = lambda p: [round(float(sp.N(p[0])), 6), round(float(sp.N(p[1])), 6)]  # noqa: E731
    xs = [float(sp.N(v)) for v in (A[0], B[0], C[0], circumcenter[0] - R_circ, circumcenter[0] + R_circ)]
    ys = [float(sp.N(v)) for v in (A[1], B[1], C[1], circumcenter[1] - R_circ, circumcenter[1] + R_circ)]
    pad = 0.08 * max(max(xs) - min(xs), max(ys) - min(ys))
    figure = {
        "view": [round(min(xs) - pad, 3), round(max(xs) + pad, 3), round(min(ys) - pad, 3), round(max(ys) + pad, 3)],
        "points": {"A": f(A), "B": f(B), "C": f(C), "G": f(G), "I": f(incenter), "O": f(circumcenter), "H": f(H)},
        "incircle": {"center": f(incenter), "r": round(float(sp.N(r_in)), 6)},
        "circumcircle": {"center": f(circumcenter), "r": round(float(sp.N(R_circ)), 6)},
    }

    return {
        "vertices": {"A": pt(A), "B": pt(B), "C": pt(C)},
        "sides": {k: {"name": side_names[k], "length": tx(side_len[k])} for k in "abc"},
        "longest": longest,
        "shortest": shortest,
        "perimeter": tx(perimeter),
        "semiperimeter": tx(s),
        "area": tx(area),
        "kind": {"by_sides": by_sides, "by_angles": by_angles},
        "angles": angles,
        "centers": {"G": pt(G), "I": pt(incenter), "O": pt(circumcenter), "H": pt(H), "N": pt(N)},
        "radii": {"r": tx(r_in), "R": tx(R_circ)},
        "euler": euler,
        "circles": {
            "incircle": circle_forms(incenter, r_in),
            "circumcircle": circle_forms(circumcenter, R_circ),
            "ninepoint": circle_forms(N, R_circ / 2),
        },
        "excircles": excircles,
        "lines": lines,
        "figure": figure,
    }
