"""Authoring toolkit: compute exercise keys with SymPy and write them as YAML.

Run with the math engine's Python (it has SymPy and the engine package):

    apps/math-engine/.venv/Scripts/python scripts/authoring/build_all.py

Nothing here is typed by hand into the answer keys: functions are written once in the engine's input language
(`P("x^2*y")`), every derivative, integral, limit and solution is computed by SymPy, and several results are
cross-checked by a second method (numeric differentiation or quadrature) before they are written.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "math-engine"))

import mpmath as mp  # noqa: E402
import sympy as sp  # noqa: E402

from allmaths_engine.parser import parse  # noqa: E402

CONTENT = ROOT / "content"
x, y, z, t, u, v, r = (sp.Symbol(n, real=True) for n in "xyztuvr")


# --- expressions ---------------------------------------------------------------------------------------------
def P(text: str) -> sp.Expr:
    """Engine syntax -> SymPy (the same grammar students use, plus diff/integrate/limit)."""
    value = parse(text, fmt="text", trusted=True).value
    assert isinstance(value, sp.Expr), text
    return value


def eng(e: sp.Expr) -> str:
    """SymPy -> engine syntax (what the answer keys contain)."""
    s = str(e).replace("**", "^")
    s = s.replace("Abs(", "abs(").replace("log(", "ln(")
    s = re.sub(r"\bE\b", "e", s)
    s = s.replace("exp(", "exp(")
    return s


def simp(e: sp.Expr) -> sp.Expr:
    return sp.simplify(e)


def tex(e: sp.Expr, display: bool = False) -> str:
    """LaTeX of an expression, with the platform's conventions (ln, \\arctan, \\dfrac in display math)."""
    s = sp.latex(e, ln_notation=True, inv_trig_style="full", mul_symbol=None)
    s = s.replace("\\operatorname{", "\\operatorname{")
    return s.replace("\\frac", "\\dfrac") if display else s


def dtex(e: sp.Expr) -> str:
    return tex(e, True)


def m(latex: str) -> str:
    return f"${latex}$"


def mm(latex: str) -> str:
    return f"$${latex}$$"


# --- numeric cross-checks ---------------------------------------------------------------------------------
def numeric_partial(f: sp.Expr, var: sp.Symbol, point: dict[sp.Symbol, float]) -> float:
    """Central difference of f in `var` at `point` (an independent check of a symbolic derivative)."""
    mp.mp.dps = 30
    lam = sp.lambdify(list(point), f, modules="mpmath")
    keys = list(point)
    idx = keys.index(var)
    h = mp.mpf("1e-10")
    a = [mp.mpf(point[k]) for k in keys]
    b = list(a)
    a[idx] += h
    b[idx] -= h
    return float((lam(*a) - lam(*b)) / (2 * h))


def check_partial(f: sp.Expr, var: sp.Symbol, symbolic: sp.Expr, points: list[dict[sp.Symbol, float]]) -> None:
    for pt in points:
        try:
            expected = numeric_partial(f, var, pt)
            got = complex(sp.N(symbolic.subs(pt), 20))
        except (ValueError, ZeroDivisionError, TypeError):
            continue
        if abs(got.imag) > 1e-9 or abs(got.real - expected) > 1e-6 * (1 + abs(expected)):
            raise AssertionError(f"derivative mismatch for {f} wrt {var} at {pt}: symbolic {got}, numeric {expected}")


def numeric_double(f: sp.Expr, ya: float | sp.Expr, yb: float | sp.Expr, xa: float, xb: float) -> float:
    mp.mp.dps = 20
    fl = sp.lambdify((x, y), f, modules="mpmath")
    ya_f = sp.lambdify(x, ya, modules="mpmath") if isinstance(ya, sp.Expr) else (lambda _x, c=ya: c)
    yb_f = sp.lambdify(x, yb, modules="mpmath") if isinstance(yb, sp.Expr) else (lambda _x, c=yb: c)
    return float(mp.quad(lambda xv: mp.quad(lambda yv: fl(xv, yv), [ya_f(xv), yb_f(xv)]), [xa, xb]))


def same_number(a: sp.Expr, b: float, tol: float = 1e-8) -> bool:
    return abs(float(sp.N(a, 20)) - b) <= tol * (1 + abs(b))


# --- domains: independent audit ---------------------------------------------------------------------------
def defined_real(f: sp.Expr, point: dict[sp.Symbol, float]) -> bool:
    """Is f real and finite at the point? (used to audit domain keys)"""
    sub = {k: sp.Rational(v).limit_denominator(1000) for k, v in point.items()}
    # Every sub-expression must be real and finite: two complex terms can add up to a real number by accident.
    for node in sp.postorder_traversal(f):
        if node.is_Atom:
            continue
        try:
            val = sp.N(node.subs(sub), 25)
        except (ZeroDivisionError, TypeError, ValueError):
            return False
        if not val.is_number or val.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
            return False
        if abs(sp.im(val)) > 1e-12:
            return False
    return True


# --- YAML output -------------------------------------------------------------------------------------------
_PLAIN = re.compile(r"^[A-Za-z_][A-Za-z0-9_\-./ ]*$")  # starts with a letter: never read as a number


def _scalar(value: object, indent: int) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int | float):
        return repr(value)
    assert isinstance(value, str), value
    if "\n" in value or "\\" in value or value != value.strip() or ": " in value or "#" in value:
        pad = " " * (indent + 2)
        body = "\n".join((pad + line) if line else "" for line in value.split("\n"))
        return "|-\n" + body
    if _PLAIN.match(value) and value.lower() not in {"true", "false", "null", "yes", "no", "on", "off"}:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def emit(value: object, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if v is None:
                continue
            if isinstance(v, dict | list) and v:
                lines.append(f"{pad}{k}:\n{emit(v, indent + 2)}")
            elif isinstance(v, list) and not v:
                lines.append(f"{pad}{k}: []")
            elif isinstance(v, dict):
                lines.append(f"{pad}{k}: {{}}")
            else:
                lines.append(f"{pad}{k}: {_scalar(v, indent)}")
        return "\n".join(lines)
    if isinstance(value, list):
        if all(isinstance(i, int | float) and not isinstance(i, bool) for i in value) or (
            value and all(isinstance(i, str) and len(i) <= 3 and i.isalnum() for i in value)
        ):
            return f"{pad}[{', '.join(_scalar(i, 0) for i in value)}]"
        lines = []
        for item in value:
            if isinstance(item, dict | list):
                inner = emit(item, indent + 2)
                lines.append(f"{pad}- {inner.lstrip()}")
            else:
                lines.append(f"{pad}- {_scalar(item, indent)}")
        return "\n".join(lines)
    return f"{pad}{_scalar(value, indent)}"


def write_exercises(lesson_dir: str, sets: list[dict], script: str) -> Path:
    """Write content/<lesson_dir>/exercises.yaml."""
    path = CONTENT / lesson_dir / "exercises.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Generated by scripts/authoring/{script}. The answers are computed with SymPy.\n"
        "# Change the script and run build_all.py instead of editing this file by hand.\n"
    )
    path.write_text(header + emit(sets) + "\n", encoding="utf8", newline="\n")
    return path


# --- units -----------------------------------------------------------------------------------------------------------
# A length is given in lu, an area in squ and a volume in cu. Builders of geometry and integrals switch this on.
UNITS = False
_VOLUME = re.compile(r"\bvolume\b", re.I)
_AREA = re.compile(r"\barea\b", re.I)
_LENGTH = re.compile(r"\b(length|distance|perimeter|radius|height|altitude|circumference|circumradius|inradius)\b", re.I)


_SEGMENT_EQ = re.compile(r"(?<![A-Za-z\\{}_])([A-F]{2})((?:\^2)?)(?=\s*=)")


def segment_norms(text: str) -> str:
    """AB = 5 is written ||AB|| = 5 (the length of the vector AB), also in the texts of exercises."""
    if not UNITS or "$" not in text:
        return text
    parts = text.split("$")
    for i in range(1, len(parts), 2):
        parts[i] = _SEGMENT_EQ.sub(lambda m: "\\norm{\\overrightarrow{" + m.group(1) + "}}" + m.group(2), parts[i])
    return "$".join(parts)


def unit_note(statement: str, answer_type: str) -> str:
    """The statement of a question about a length, an area or a volume, with its unit."""
    if not UNITS or answer_type not in ("number", "expression") or " lu" in statement or " squ" in statement or " cu" in statement:
        return statement
    for pat, unit in ((_VOLUME, "cu"), (_AREA, "squ"), (_LENGTH, "lu")):
        if pat.search(statement):
            return statement.rstrip() + f" The unit is {unit}: give the number only."
    return statement


def with_units(fn):
    """Decorator for a `build` function: its exercises state the units of lengths, areas and volumes."""
    def run(*args, **kwargs):
        global UNITS
        UNITS = True
        try:
            return fn(*args, **kwargs)
        finally:
            UNITS = False
    run.__name__ = fn.__name__
    return run


# --- exercise constructors ---------------------------------------------------------------------------------
SOURCE = "MATH126 exercise sheet, T. Hakizimana"


def ex(
    id: str,
    statement: str,
    answer_type: str,
    answer: str,
    *,
    solution: str,
    hints: list[str] | None = None,
    **extra: object,
) -> dict:
    item: dict = {"id": id, "statement": segment_norms(unit_note(statement, answer_type)), "answerType": answer_type, "answer": answer}
    for key in ("variables", "coordinates", "constraint", "ode", "choices", "correctIndex"):
        if key in extra:
            item[key] = extra.pop(key)
    item["hints"] = [segment_norms(h) for h in (hints or [])]
    item["solution"] = segment_norms(solution)
    for key, val in extra.items():
        item[key] = val
    return _tidy(item)


_DISPLAY = re.compile(r"\$\$.*?\$\$", re.S)


def _tidy(item: dict) -> dict:
    """Use the display fraction inside $$...$$ in every text of an exercise."""
    bs = chr(92)

    def fix(text: str) -> str:
        return _DISPLAY.sub(lambda m: re.sub(re.escape(bs + "frac") + r"(?![a-z])", lambda _m: bs + "dfrac", m.group(0)), text)

    for key in ("statement", "solution", "note"):
        if isinstance(item.get(key), str):
            item[key] = fix(item[key])
    item["hints"] = [fix(h) for h in item.get("hints", [])]
    return item


def exset(id: str, task: str, items: list[dict], format: str | None = None, source: str = SOURCE) -> dict:
    out: dict = {"id": id, "task": task}
    if format:
        out["format"] = format
    out["source"] = source
    out["items"] = items
    return out


def exset_plain(id: str, task: str, items: list[dict], format: str | None = None) -> dict:
    """An exercise set that is not taken from the printed exercise sheet (no source line)."""
    out: dict = {"id": id, "task": task}
    if format:
        out["format"] = format
    out["items"] = items
    return out


def floor_sqrt(n: int) -> int:
    return math.isqrt(n)
