"""Vector operations with the formula and the numbers shown (dot, cross, norm, angle, projection, box product)."""

from __future__ import annotations

import sympy as sp

from .types import Solution, SolverError, Step, eng, tex


def _vec(v: sp.Tuple) -> str:
    return r"\begin{pmatrix}" + r"\\".join(tex(c) for c in v) + r"\end{pmatrix}"


def _same_length(a: sp.Tuple, b: sp.Tuple) -> None:
    if len(a) != len(b) or len(a) not in (2, 3):
        raise SolverError("The two vectors must have the same number of coordinates (2 or 3).", "bad_vectors")


def dot(a: sp.Tuple, b: sp.Tuple) -> Solution:
    _same_length(a, b)
    terms = " + ".join(rf"\left({tex(x)}\right)\left({tex(y)}\right)" for x, y in zip(a, b, strict=True))
    value = sp.simplify(sum(x * y for x, y in zip(a, b, strict=True)))
    return Solution("dot", rf"\left\langle {_vec(a)},\,{_vec(b)}\right\rangle", tex(value), eng(value),
                    [Step("Multiply the matching coordinates and add.", terms), Step("Result.", tex(value))], [])


def cross(a: sp.Tuple, b: sp.Tuple) -> Solution:
    if len(a) != 3 or len(b) != 3:
        raise SolverError("The cross product needs two vectors with 3 coordinates.", "bad_vectors")
    c = sp.Matrix(a).cross(sp.Matrix(b))
    rows = [
        rf"\left({tex(a[1])}\right)\left({tex(b[2])}\right)-\left({tex(a[2])}\right)\left({tex(b[1])}\right)",
        rf"\left({tex(a[2])}\right)\left({tex(b[0])}\right)-\left({tex(a[0])}\right)\left({tex(b[2])}\right)",
        rf"\left({tex(a[0])}\right)\left({tex(b[1])}\right)-\left({tex(a[1])}\right)\left({tex(b[0])}\right)",
    ]
    result = sp.Tuple(*[sp.simplify(v) for v in c])
    checks = [sp.simplify(sum(x * y for x, y in zip(result, v, strict=True))) for v in (a, b)]
    if any(ch != 0 for ch in checks):
        raise SolverError("I could not verify the cross product.", "unverified")
    return Solution("cross", rf"\left[{_vec(a)},\,{_vec(b)}\right]", _vec(result), eng(result),
                    [Step("Use the determinant formula: each coordinate is a 2×2 determinant.", r"\begin{pmatrix}" + r"\\".join(rows) + r"\end{pmatrix}"), Step("Result.", _vec(result))],
                    ["The result is orthogonal to both vectors (checked with the dot product)."])


def norm(a: sp.Tuple) -> Solution:
    squares = " + ".join(rf"\left({tex(x)}\right)^2" for x in a)
    value = sp.simplify(sp.sqrt(sum(x**2 for x in a)))
    return Solution("norm", rf"\left\lVert {_vec(a)}\right\rVert", tex(value), eng(value), [Step("Square the coordinates, add, take the square root.", rf"\sqrt{{{squares}}}"), Step("Result.", tex(value))], [])


def angle(a: sp.Tuple, b: sp.Tuple) -> Solution:
    _same_length(a, b)
    d = sp.simplify(sum(x * y for x, y in zip(a, b, strict=True)))
    na, nb = sp.sqrt(sum(x**2 for x in a)), sp.sqrt(sum(x**2 for x in b))
    if na == 0 or nb == 0:
        raise SolverError("The angle with the zero vector is not defined.", "bad_vectors")
    c = sp.simplify(d / (na * nb))
    theta = sp.simplify(sp.acos(c))
    return Solution("angle", rf"\widehat{{\left({_vec(a)},\,{_vec(b)}\right)}}", tex(theta), eng(theta),
                    [Step("cos θ = ⟨u, v⟩ / (‖u‖ ‖v‖).", rf"\cos\theta=\dfrac{{{tex(d)}}}{{{tex(sp.simplify(na))}\cdot {tex(sp.simplify(nb))}}}={tex(c)}"), Step("The angle is the arccosine.", rf"\theta={tex(theta)}")], [])


def projection(a: sp.Tuple, b: sp.Tuple) -> Solution:
    _same_length(a, b)
    d = sp.simplify(sum(x * y for x, y in zip(a, b, strict=True)))
    nb2 = sp.simplify(sum(x**2 for x in b))
    if nb2 == 0:
        raise SolverError("You cannot project onto the zero vector.", "bad_vectors")
    p = sp.Tuple(*[sp.simplify(d / nb2 * c) for c in b])
    return Solution("projection", rf"\operatorname{{proj}}_{{{_vec(b)}}}{_vec(a)}", _vec(p), eng(p),
                    [Step("proj = ⟨u, v⟩ / ‖v‖² · v.", rf"\dfrac{{{tex(d)}}}{{{tex(nb2)}}}\,{_vec(b)}"), Step("Result.", _vec(p))], [])


def box(a: sp.Tuple, b: sp.Tuple, c: sp.Tuple) -> Solution:
    if not (len(a) == len(b) == len(c) == 3):
        raise SolverError("The box product needs three vectors with 3 coordinates.", "bad_vectors")
    m = sp.Matrix([list(a), list(b), list(c)])
    value = sp.simplify(m.det())
    return Solution("box", rf"\left\langle {_vec(a)},\,{_vec(b)},\,{_vec(c)}\right\rangle", tex(value), eng(value),
                    [Step("The box product is the determinant of the three vectors.", rf"\det{tex(m)}"), Step("Result.", tex(value))],
                    ["Its absolute value is the volume of the parallelepiped built on the three vectors."])
