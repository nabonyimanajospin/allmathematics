"""Exact vector algebra on SymPy values.

A vector is a ``sympy.Tuple`` of expressions; a scalar is a ``sympy.Expr``. Every function is exact:
results contain integers, rationals, radicals and symbols, never floats.
Convention (spec section 6.1): dot = ⟨u, v⟩, cross = [u, v], box = ⟨u, v, w⟩.
"""

from __future__ import annotations

import sympy as sp

from .errors import ParseError

Value = sp.Expr | sp.Tuple


class VectorError(ParseError):
    """Invalid operation on vectors (dimension mismatch, zero vector, wrong type)."""

    code = "vector_op"


def _is_vec(x: object) -> bool:
    return isinstance(x, sp.Tuple)


def _require_vec(x: object, name: str = "argument") -> sp.Tuple:
    if not isinstance(x, sp.Tuple):
        raise VectorError(f"{name} must be a vector such as (1, 2, 3).")
    return x


def _same_dim(u: sp.Tuple, v: sp.Tuple) -> None:
    if len(u) != len(v):
        raise VectorError(f"The vectors have different dimensions ({len(u)} and {len(v)}).")


def _scalar(x: object) -> sp.Expr:
    if isinstance(x, sp.Tuple) or not isinstance(x, sp.Expr):
        raise VectorError("A number was expected here, but a vector was given.")
    return x


def clean(x: sp.Expr) -> sp.Expr:
    """Canonical exact form: radicals simplified, denominators rationalised."""
    return sp.radsimp(sp.simplify(x))


# --- arithmetic used by the parser ----------------------------------------------------------------
def add(a: object, b: object) -> object:
    if _is_vec(a) or _is_vec(b):
        u, v = _require_vec(a, "Both sides of +"), _require_vec(b, "Both sides of +")
        _same_dim(u, v)
        return sp.Tuple(*[x + y for x, y in zip(u, v, strict=False)])
    return _scalar(a) + _scalar(b)


def neg(a: object) -> object:
    if _is_vec(a):
        return sp.Tuple(*[-x for x in _require_vec(a)])
    return -_scalar(a)


def sub(a: object, b: object) -> object:
    return add(a, neg(b))


def mul(a: object, b: object) -> object:
    if _is_vec(a) and _is_vec(b):
        raise VectorError("Two vectors cannot be multiplied with “*”. Use dot(u, v) or cross(u, v).")
    if _is_vec(a):
        k = _scalar(b)
        return sp.Tuple(*[x * k for x in _require_vec(a)])
    if _is_vec(b):
        k = _scalar(a)
        return sp.Tuple(*[x * k for x in _require_vec(b)])
    return _scalar(a) * _scalar(b)


def div(a: object, b: object) -> object:
    if _is_vec(b):
        raise VectorError("Division by a vector is not defined.")
    d = _scalar(b)
    if d == 0:
        raise VectorError("Division by zero.", "division_by_zero")
    if _is_vec(a):
        return sp.Tuple(*[x / d for x in _require_vec(a)])
    return _scalar(a) / d


# --- named functions ------------------------------------------------------------------------------
def dot(u: object, v: object) -> sp.Expr:
    a, b = _require_vec(u, "dot: first argument"), _require_vec(v, "dot: second argument")
    _same_dim(a, b)
    return sp.expand(sum((x * y for x, y in zip(a, b, strict=False)), sp.Integer(0)))


def cross(u: object, v: object) -> object:
    """3D cross product [u, v]. For two plane vectors returns the scalar z-component."""
    a, b = _require_vec(u, "cross: first argument"), _require_vec(v, "cross: second argument")
    _same_dim(a, b)
    if len(a) == 3:
        return sp.Tuple(
            sp.expand(a[1] * b[2] - a[2] * b[1]),
            sp.expand(a[2] * b[0] - a[0] * b[2]),
            sp.expand(a[0] * b[1] - a[1] * b[0]),
        )
    if len(a) == 2:
        return sp.expand(a[0] * b[1] - a[1] * b[0])
    raise VectorError("cross is defined for vectors in the plane or in space.")


def norm(u: object) -> sp.Expr:
    a = _require_vec(u, "norm: argument")
    return clean(sp.sqrt(sum((x**2 for x in a), sp.Integer(0))))


def box(u: object, v: object, w: object) -> sp.Expr:
    """Box (scalar triple) product ⟨u, v, w⟩ = ⟨u, [v, w]⟩."""
    a, b, c = (_require_vec(x, "box: argument") for x in (u, v, w))
    if not (len(a) == len(b) == len(c) == 3):
        raise VectorError("box is defined for three vectors in space.")
    return dot(a, cross(b, c))


def unit(u: object) -> sp.Tuple:
    a = _require_vec(u, "unit: argument")
    n = norm(a)
    if n == 0:
        raise VectorError("The zero vector has no direction.", "zero_vector")
    return sp.Tuple(*[clean(x / n) for x in a])


def cos_angle(u: object, v: object) -> sp.Expr:
    a, b = _require_vec(u, "cos_angle: first argument"), _require_vec(v, "cos_angle: second argument")
    na, nb = norm(a), norm(b)
    if na == 0 or nb == 0:
        raise VectorError("The angle with the zero vector is undefined.", "zero_vector")
    return clean(dot(a, b) / (na * nb))


def comp(u: object, v: object) -> sp.Expr:
    """Scalar component of u along v: ⟨u, v⟩ / ‖v‖."""
    a, b = _require_vec(u, "comp: first argument"), _require_vec(v, "comp: second argument")
    nb = norm(b)
    if nb == 0:
        raise VectorError("Cannot project onto the zero vector.", "zero_vector")
    return clean(dot(a, b) / nb)


def proj(u: object, v: object) -> sp.Tuple:
    """Orthogonal projection of u onto v: (⟨u, v⟩ / ⟨v, v⟩) v."""
    a, b = _require_vec(u, "proj: first argument"), _require_vec(v, "proj: second argument")
    vv = dot(b, b)
    if vv == 0:
        raise VectorError("Cannot project onto the zero vector.", "zero_vector")
    k = dot(a, b) / vv
    return sp.Tuple(*[clean(k * x) for x in b])
