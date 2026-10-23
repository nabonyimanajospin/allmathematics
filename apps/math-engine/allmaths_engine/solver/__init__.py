"""A rule-based solver (no AI): the request is read with a closed grammar, solved with SymPy, explained step by step and always checked.

    derivative / integral / definite integral / limit / equation / system / ordinary differential equation /
    simplify, expand, factor / dot, cross, norm, angle, projection and box product of vectors.
"""

from __future__ import annotations

import re

import sympy as sp

from ..errors import EngineError
from ..parser import _WORDS, _split_name, parse
from . import algebra, derivative, integral, limits, more_text, multivar_text, odes, vector_ops
from .types import Solution, SolverError

MAX_INPUT = 300
OPERATIONS = {"auto", "derivative", "integral", "limit", "solve", "ode", "simplify", "expand", "factor", "vector", "multivariable", "other"}


def _check_words(text: str) -> None:
    """Refuse anything that looks like an English word or a long run of letters: the reader would turn it into a product of variables."""
    known = set(_WORDS) | {"oo", "e", "pi"}
    for run in re.findall(r"[A-Za-z]+", text):
        if len(run) < 3 or run.lower() in known:
            continue
        tokens = [t.text for t in _split_name(run)]
        if all(len(t) == 1 for t in tokens):
            raise SolverError(
                f"I could not read “{run}”. Write products with a * (for example x*y*z) and functions with parentheses (for example sin(x)).",
                "unknown_word",
            )


def _value(text: str) -> object:
    _check_words(text)
    try:
        return parse(text.strip(), fmt="text").value
    except EngineError as exc:
        raise SolverError(f"I could not read “{text.strip()[:60]}”: {exc.message}", "parse") from None


def _expr(text: str) -> sp.Expr:
    v = _value(text)
    if isinstance(v, sp.Tuple):
        raise SolverError("I expected an expression here, not a list of numbers.", "parse")
    return v  # type: ignore[return-value]


def _pick_variable(expr: sp.Expr, wanted: str | None) -> sp.Symbol:
    if wanted:
        return sp.Symbol(wanted, real=True)
    free = sorted(expr.free_symbols, key=lambda s: s.name)
    if not free:
        return sp.Symbol("x", real=True)
    if len(free) == 1:
        return free[0]
    for pref in ("x", "t", "u", "y", "z"):
        for s in free:
            if s.name == pref:
                return s
    return free[0]


def _clean(raw: str) -> str:
    t = raw.strip().rstrip("?.")
    t = t.replace("∬", " double integral of ").replace("∭", " triple integral of ").replace("∇", " gradient of ").replace("∂", " partial ")
    t = t.replace("∫", " integral of ").replace("′", "'").replace("→", "->").replace("’", "'")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


_ORDER = {"first": 1, "second": 2, "third": 3}


def _derivative(low: str, text: str) -> Solution | None:
    m = re.match(r"^(?:find |compute |calculate |what is )?(?:the )?(first |second |third )?(?:derivative|differentiate|diff)\s*(?:of )?(.+?)(?:\s+(?:with respect to|wrt|w\.r\.t\.?)\s+([a-z]))?$", low)
    if m:
        order = _ORDER.get((m.group(1) or "first").strip(), 1)
        body = text[m.start(2):m.end(2)]
        expr = _expr(body)
        return derivative.differentiate(expr, _pick_variable(expr, m.group(3)), order)
    m = re.match(r"^d\s*/\s*d([a-z])\s*(.+)$", low)
    if m:
        expr = _expr(text[m.start(2):m.end(2)])
        return derivative.differentiate(expr, sp.Symbol(m.group(1), real=True))
    return None


def _integral(low: str, text: str) -> Solution | None:
    m = re.match(r"^(?:find |compute |calculate |evaluate )?(?:the )?(?:definite |indefinite )?(?:integral|integrate)\s*(?:of )?(.+?)(?:\s+from\s+(.+?)\s+to\s+(.+?))?(?:\s+d([a-z]))?$", low)
    if not m:
        return None
    body = text[m.start(1):m.end(1)]
    var = m.group(4)
    if var is None:
        mm = re.match(r"^(.*?)\s*d([a-z])$", body)
        if mm and not re.search(r"[a-z]\s*$", mm.group(1)):
            body, var = mm.group(1), mm.group(2)
    expr = _expr(body)
    x = _pick_variable(expr, var)
    if m.group(2) is not None:
        a, b = _expr(text[m.start(2):m.end(2)]), _expr(text[m.start(3):m.end(3)])
        return integral.definite(expr, x, a, b)
    return integral.indefinite(expr, x)


def _limit(low: str, text: str) -> Solution | None:
    m = re.match(r"^(?:find |compute |calculate |evaluate )?(?:the )?(?:limit|lim)\s+(?:as|when)\s+([a-z])\s*(?:->|to|approaches|tends to)\s*(\S+)\s+of\s+(.+)$", low)
    if m:
        body, var, target = text[m.start(3):m.end(3)], m.group(1), text[m.start(2):m.end(2)]
        return limits.limit(_expr(body), sp.Symbol(var, real=True), _expr(target.replace("infinity", "oo").replace("inf", "oo")), "")
    m = re.match(r"^(?:find |compute |calculate )?(?:the )?(?:limit|lim)\s*(?:of )?(.+?)\s+(?:as|when)\s+([a-z])\s*(?:->|to|approaches|tends to)\s*(.+?)$", low)
    if m:
        body, var, target = text[m.start(1):m.end(1)], m.group(2), text[m.start(3):m.end(3)]
    else:
        m = re.match(r"^(?:limit|lim)\s+([a-z])\s*(?:->|to)\s*(\S+)\s+(.+)$", low)
        if not m:
            return None
        var, target, body = m.group(1), text[m.start(2):m.end(2)], text[m.start(3):m.end(3)]
    direction = ""
    t = target.strip()
    if t.endswith("+") and len(t) > 1:
        direction, t = "+", t[:-1]
    elif t.endswith("-") and len(t) > 1:
        direction, t = "-", t[:-1]
    t = t.replace("infinity", "oo").replace("inf", "oo")
    expr = _expr(body)
    return limits.limit(expr, sp.Symbol(var, real=True), _expr(t), direction)


def _equations(text: str) -> list[tuple[sp.Expr, sp.Expr]]:
    body = re.sub(r"\s+for\s+[a-z]\s*$", "", re.sub(r"^solve\s*", "", text, flags=re.I), flags=re.I)
    parts = [p for p in re.split(r"\s*(?:;|,|\band\b)\s*", body) if "=" in p]
    eqs: list[tuple[sp.Expr, sp.Expr]] = []
    for p in parts:
        sides = p.split("=")
        if len(sides) != 2 or not sides[0].strip() or not sides[1].strip():
            raise SolverError("An equation needs one = sign with something on each side.", "parse")
        eqs.append((_expr(sides[0]), _expr(sides[1])))
    return eqs


def _ode(low: str, text: str) -> Solution | None:
    if not re.search(r"y'|dy\s*/\s*dx", low) or "=" not in low:
        return None
    t = re.sub(r"dy\s*/\s*dx", "y'", text, flags=re.I)
    conditions: list[tuple[sp.Expr, sp.Expr, int]] = []
    for m in re.finditer(r"y(')?\s*\(\s*([^()]+?)\s*\)\s*=\s*([^,;]+)", t):
        conditions.append((_expr(m.group(2)), _expr(m.group(3)), 1 if m.group(1) else 0))
    t = re.sub(r"[,;]?\s*y(')?\s*\(\s*[^()]+?\s*\)\s*=\s*[^,;]+", "", t)
    sides = t.split("=")
    if len(sides) != 2:
        return None
    lhs, rhs = _expr(sides[0]), _expr(sides[1])
    x = sp.Symbol("x", real=True)
    y, y1, y2 = sp.Symbol("y", real=True), sp.Symbol("y1", real=True), sp.Symbol("y2", real=True)
    return odes.solve_ode(lhs, rhs, x, y, y1, y2, conditions)


def _vector(low: str, text: str) -> Solution | None:
    if not re.search(r"\b(dot|cross|norm|magnitude|length|angle|projection|proj|box|triple)\b", low):
        return None
    tuples = re.findall(r"\(([^()]*,[^()]*)\)", text)
    vecs = [_value("(" + t + ")") for t in tuples]
    vecs = [v for v in vecs if isinstance(v, sp.Tuple)]
    if re.search(r"\bdot\b|scalar product|inner product", low) and len(vecs) == 2:
        return vector_ops.dot(vecs[0], vecs[1])
    if re.search(r"\bcross\b|vector product", low) and len(vecs) == 2:
        return vector_ops.cross(vecs[0], vecs[1])
    if re.search(r"\b(box|triple)\b", low) and len(vecs) == 3:
        return vector_ops.box(vecs[0], vecs[1], vecs[2])
    if re.search(r"\bangle\b", low) and len(vecs) == 2:
        return vector_ops.angle(vecs[0], vecs[1])
    if re.search(r"\b(projection|proj)\b", low) and len(vecs) == 2:
        return vector_ops.projection(vecs[0], vecs[1])
    if re.search(r"\b(norm|magnitude|length)\b", low) and len(vecs) == 1:
        return vector_ops.norm(vecs[0])
    raise SolverError("I could not match the vectors to the operation. Write the vectors like (1, 2, 3).", "vector_args")


def solve_text(raw: str, operation: str = "auto") -> Solution:
    if operation not in OPERATIONS:
        raise SolverError("Unknown operation.", "bad_operation")
    text = _clean(raw)
    if not text:
        raise SolverError("Type a problem to solve.", "empty")
    if len(text) > MAX_INPUT:
        raise SolverError("The problem is too long.", "too_long")
    low = text.lower()
    bars = re.fullmatch(r"\|\s*(\(.*\))\s*\|", text)
    if bars:
        text = "norm of " + bars.group(1)
        low = text.lower()

    if operation in ("auto", "multivariable"):
        r = multivar_text.read(low, text)
        if r:
            return r
        if operation == "multivariable":
            raise SolverError("I did not recognise this multivariable problem. Examples: “gradient of x^2*y”, “critical points of x^3-3*x*y+y^3”, “double integral of x*y over x from 0 to 1, y from 0 to x”.", "no_intent")
    if operation in ("auto", "other"):
        r = more_text.read(low, text)
        if r:
            return r
        if operation == "other":
            raise SolverError("I did not recognise this problem. Examples: “determinant of [[1,2],[3,4]]”, “solve x^2 - 4 > 0”, “tangent line to y = x^2 at x = 1”, “taylor series of sin(x) up to order 5”, “sum of k^2 for k from 1 to 10”.", "no_intent")
    if operation in ("auto", "derivative"):
        r = _derivative(low, text)
        if r:
            return r
        if operation == "derivative":
            expr = _expr(text)
            return derivative.differentiate(expr, _pick_variable(expr, None))
    if operation in ("auto", "integral"):
        r = _integral(low, text)
        if r:
            return r
        if operation == "integral":
            expr = _expr(text)
            return integral.indefinite(expr, _pick_variable(expr, None))
    if operation in ("auto", "limit"):
        r = _limit(low, text)
        if r:
            return r
    if operation in ("auto", "ode"):
        r = _ode(low, text)
        if r:
            return r
    if operation in ("auto", "vector"):
        r = _vector(low, text)
        if r:
            return r
    if operation in ("auto", "simplify", "expand", "factor"):
        m = re.match(r"^(simplify|expand|factor|factorise|factorize)\s*(?:the )?(?:expression )?(.+)$", low)
        if m and "=" not in m.group(2):
            kind = "factor" if m.group(1).startswith("factor") else m.group(1)
            return algebra.rewrite(_expr(text[m.start(2):m.end(2)]), kind)
        if operation in ("simplify", "expand", "factor"):
            return algebra.rewrite(_expr(text), operation)
    if operation in ("auto", "solve") and "=" in text:
        eqs = _equations(text)
        if len(eqs) == 1:
            lhs, rhs = eqs[0]
            m = re.search(r"\bfor\s+([a-z])\b", low)
            x = _pick_variable(lhs - rhs, m.group(1) if m else None)
            if len((lhs - rhs).free_symbols) > 1 and not m:
                raise SolverError("The equation has several unknowns: say which one to solve for, for example “solve for x”.", "ambiguous")
            return algebra.solve_equation(lhs, rhs, x)
        syms = sorted({s for l, r in eqs for s in (l - r).free_symbols}, key=lambda s: s.name)
        return algebra.solve_system(eqs, syms)
    if operation == "auto":
        v = _value(text)
        if isinstance(v, sp.Tuple):
            raise SolverError("Tell me what to do with these numbers, for example “norm of (3, 4)”.", "no_intent")
        return algebra.rewrite(v, "simplify")  # type: ignore[arg-type]
    raise SolverError("I could not understand the problem.", "no_intent")
