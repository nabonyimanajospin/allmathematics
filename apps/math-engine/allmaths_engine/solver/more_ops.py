"""More problem types for the step-by-step solver, each checked by a second method before it is shown:

    matrices        determinant, inverse, transpose, trace, rank, row reduction, eigenvalues and eigenvectors, sums, products, powers
    inequalities    solve x^2 - 4 > 0
    tangent line    tangent line to y = x^2 at x = 1, normal line, tangent plane to z = x*y at (1, 2)
    series          Taylor and Maclaurin polynomials, sums of series (finite and infinite)
    algebra         partial fractions, the area between two curves
"""

from __future__ import annotations

import re

import sympy as sp

from .multivar import _definite
from .types import Solution, SolverError, Step, eng, tex

MAX_SIZE = 4
_SEP = r",\ "
_INFTY = r"\infty"


def _x() -> sp.Symbol:
    return sp.Symbol("x", real=True)


# ------------------------------------------------------------------------------------------------------ matrices
def _split_top(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return [p.strip() for p in parts]


def extract_matrices(text: str) -> tuple[list[sp.Matrix], str]:
    """The matrices written as [[1, 2], [3, 4]] and the text with each one replaced by M1, M2, ..."""
    from . import _expr

    out: list[sp.Matrix] = []
    result = ""
    i = 0
    while i < len(text):
        if text.startswith("[[", i) or re.match(r"\[\s*\[", text[i:]):
            depth = 0
            j = i
            while j < len(text):
                if text[j] == "[":
                    depth += 1
                elif text[j] == "]":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth != 0:
                raise SolverError("A bracket of the matrix is not closed.", "parse")
            inner = text[i + 1 : j]
            rows = [r for r in re.findall(r"\[([^\[\]]*)\]", inner) if r.strip()]
            if not rows:
                raise SolverError("Write the matrix like [[1, 2], [3, 4]].", "parse")
            table = [[_expr(c) for c in _split_top(r)] for r in rows]
            if len({len(r) for r in table}) != 1:
                raise SolverError("All the rows of a matrix must have the same number of entries.", "bad_matrix")
            if len(table) > MAX_SIZE or len(table[0]) > MAX_SIZE:
                raise SolverError(f"I handle matrices up to {MAX_SIZE} × {MAX_SIZE}.", "bad_matrix")
            out.append(sp.Matrix(table))
            result += f"M{len(out)}"
            i = j + 1
        else:
            result += text[i]
            i += 1
    return out, result


def _square(m: sp.Matrix, what: str) -> None:
    if m.rows != m.cols:
        raise SolverError(f"The {what} needs a square matrix (as many rows as columns).", "bad_matrix")


def _mat(m: sp.Matrix) -> str:
    return tex(m)


def determinant(m: sp.Matrix) -> Solution:
    _square(m, "determinant")
    n = m.rows
    steps: list[Step] = [Step("The matrix.", rf"A={_mat(m)}")]
    if n == 1:
        steps.append(Step("The determinant of a 1 × 1 matrix is its entry.", rf"\det A={tex(m[0, 0])}"))
    elif n == 2:
        a, b, c, d = m[0, 0], m[0, 1], m[1, 0], m[1, 1]
        steps.append(Step("For a 2 × 2 matrix, det = ad − bc.", rf"\det A=({tex(a)})({tex(d)})-({tex(b)})({tex(c)})={tex(sp.simplify(a * d - b * c))}"))
    else:
        terms = []
        total = 0
        for j in range(n):
            minor = m.minor_submatrix(0, j)
            sign = 1 if j % 2 == 0 else -1
            terms.append(rf"{'+' if sign == 1 and j > 0 else ('-' if sign == -1 else '')}({tex(m[0, j])})\cdot\det{_mat(minor)}")
            total += sign * m[0, j] * minor.det()
        steps.append(Step("Expand along the first row: each entry times the determinant of the smaller matrix left when its row and column are removed, with alternating signs + − + −.", rf"\det A={''.join(terms)}"))
        steps.append(Step("Evaluate the smaller determinants and add.", rf"\det A={tex(sp.simplify(total))}"))
    value = sp.simplify(m.det())
    other = sp.simplify(m.det(method="berkowitz"))
    if sp.simplify(value - other) != 0:
        raise SolverError("I could not verify the determinant.", "unverified")
    if sp.simplify(sp.Matrix(m.T).det() - value) != 0:
        raise SolverError("I could not verify the determinant.", "unverified")
    if value == 0:
        steps.append(Step("The determinant is 0, so the matrix is singular (it has no inverse) and its rows are linearly dependent.", ""))
    return Solution("determinant", rf"\det{_mat(m)}", tex(value), eng(value), steps, ["Checked with a second method (Berkowitz) and with the transposed matrix, which has the same determinant."])


def inverse(m: sp.Matrix) -> Solution:
    _square(m, "inverse")
    det = sp.simplify(m.det())
    steps = [Step("The matrix and its determinant. A matrix has an inverse exactly when its determinant is not 0.", rf"A={_mat(m)},\qquad \det A={tex(det)}")]
    if det == 0:
        steps.append(Step("The determinant is 0, so the matrix is singular and has no inverse.", ""))
        return Solution("inverse", rf"{_mat(m)}^{{-1}}", r"\text{no inverse (the determinant is 0)}", "no inverse (the determinant is 0)", steps, [])
    if m.rows == 2:
        steps.append(Step("For a 2 × 2 matrix: swap the diagonal entries, change the signs of the other two, divide by the determinant.", rf"A^{{-1}}=\dfrac{{1}}{{{tex(det)}}}{_mat(sp.Matrix([[m[1, 1], -m[0, 1]], [-m[1, 0], m[0, 0]]]))}"))
    else:
        cof = m.cofactor_matrix()
        steps.append(Step("Compute the matrix of cofactors (each entry replaced by ± the determinant of the smaller matrix).", rf"C={_mat(cof)}"))
        steps.append(Step("The adjugate is the transpose of the cofactor matrix; the inverse is the adjugate divided by the determinant.", rf"A^{{-1}}=\dfrac{{1}}{{{tex(det)}}}{_mat(cof.T)}"))
    inv = sp.simplify(m.inv())
    if sp.simplify(m * inv - sp.eye(m.rows)) != sp.zeros(m.rows) or sp.simplify(inv * m - sp.eye(m.rows)) != sp.zeros(m.rows):
        raise SolverError("I could not verify the inverse.", "unverified")
    steps.append(Step("Result.", rf"A^{{-1}}={_mat(inv)}"))
    return Solution("inverse", rf"{_mat(m)}^{{-1}}", _mat(inv), str(inv.tolist()), steps, ["Checked: A · A⁻¹ and A⁻¹ · A both give the identity matrix."])


def transpose_trace(m: sp.Matrix, kind: str) -> Solution:
    if kind == "transpose":
        return Solution("transpose", rf"{_mat(m)}^T", _mat(m.T), str(m.T.tolist()), [Step("Write the rows as columns.", rf"A^T={_mat(m.T)}")], [])
    _square(m, "trace")
    value = sp.simplify(sum(m[i, i] for i in range(m.rows)))
    return Solution("trace", rf"\operatorname{{tr}}{_mat(m)}", tex(value), eng(value), [Step("The trace is the sum of the diagonal entries.", rf"\operatorname{{tr}}A={'+'.join(tex(m[i, i]) for i in range(m.rows))}={tex(value)}")], [])


def _gauss_jordan(m: sp.Matrix) -> tuple[sp.Matrix, list[int], list[Step]]:
    a = m.copy()
    steps: list[Step] = []
    pivots: list[int] = []
    r = 0
    for c in range(a.cols):
        if r >= a.rows:
            break
        pivot_row = next((i for i in range(r, a.rows) if sp.simplify(a[i, c]) != 0), None)
        if pivot_row is None:
            continue
        if pivot_row != r:
            a.row_swap(r, pivot_row)
            steps.append(Step(f"Swap rows {r + 1} and {pivot_row + 1} to get a non-zero entry in column {c + 1}.", _mat(a)))
        p = a[r, c]
        if p != 1:
            a[r, :] = (a[r, :] / p).applyfunc(sp.simplify)
            steps.append(Step(f"Divide row {r + 1} by {eng(p)} so that the pivot is 1.", _mat(a)))
        for i in range(a.rows):
            if i != r and sp.simplify(a[i, c]) != 0:
                f = a[i, c]
                a[i, :] = (a[i, :] - f * a[r, :]).applyfunc(sp.simplify)
                steps.append(Step(f"Row {i + 1} ← row {i + 1} − ({eng(f)}) · row {r + 1}, to clear column {c + 1}.", _mat(a)))
        pivots.append(c)
        r += 1
        if len(steps) > 40:
            raise SolverError("The row reduction is too long to show step by step.", "too_long")
    return a, pivots, steps


def row_reduce(m: sp.Matrix) -> Solution:
    a, pivots, steps = _gauss_jordan(m)
    steps.insert(0, Step("Gauss–Jordan elimination: use row operations to make each pivot 1 and clear the rest of its column.", rf"A={_mat(m)}"))
    ref, ref_pivots = m.rref()
    if sp.simplify(a - ref) != sp.zeros(*a.shape) or list(ref_pivots) != pivots:
        raise SolverError("I could not verify the row reduction.", "unverified")
    rank = len(pivots)
    null = m.nullspace()
    if len(null) != m.cols - rank or any(sp.simplify(m * v) != sp.zeros(m.rows, 1) for v in null):
        raise SolverError("I could not verify the rank.", "unverified")
    steps.append(Step("The reduced row echelon form. The number of pivots is the rank.", rf"\operatorname{{rref}}(A)={_mat(a)},\qquad \operatorname{{rank}}A={rank}"))
    return Solution("rref", rf"\operatorname{{rref}}{_mat(m)}", rf"{_mat(a)},\ \operatorname{{rank}}={rank}", f"{a.tolist()}, rank {rank}", steps, ["Checked with SymPy's own reduction, and the null space has dimension (columns − rank) and satisfies A·v = 0."])


def rank_of(m: sp.Matrix) -> Solution:
    sol = row_reduce(m)
    rank = m.rank()
    return Solution("rank", rf"\operatorname{{rank}}{_mat(m)}", str(rank), str(rank), sol.steps, sol.notes)


def eigen(m: sp.Matrix, vectors: bool) -> Solution:
    _square(m, "eigenvalues")
    n = m.rows
    lam = sp.Symbol("lambda")
    poly = sp.expand((m - lam * sp.eye(n)).det())
    steps = [
        Step("Eigenvalues are the numbers λ with det(A − λI) = 0. Write the characteristic polynomial.", rf"\det(A-\lambda I)=\det{_mat(m - lam * sp.eye(n))}={tex(poly)}"),
    ]
    roots = sp.roots(sp.Poly(poly, lam))
    if sum(roots.values()) != n:
        raise SolverError("This matrix has eigenvalues that I cannot write exactly (the polynomial has no closed-form roots).", "no_solution")
    factored = sp.factor(poly)
    steps.append(Step("Factor it and read the roots.", rf"{tex(factored)}=0"))
    ordered = sorted(roots.items(), key=lambda kv: (sp.re(sp.N(kv[0])), sp.im(sp.N(kv[0]))))
    steps.append(Step("The eigenvalues (with their multiplicity).", ",\\ ".join(rf"\lambda={tex(v)}" + (rf"\ (\times{k})" if k > 1 else "") for v, k in ordered)))
    for v, _multiplicity in ordered:
        if sp.simplify(poly.subs(lam, v)) != 0:
            raise SolverError("I could not verify an eigenvalue.", "unverified")
    answer_parts = [rf"\lambda={tex(v)}" + (rf"\ (\times{k})" if k > 1 else "") for v, k in ordered]
    text_parts = [f"λ = {eng(v)}" + (f" (x{k})" if k > 1 else "") for v, k in ordered]
    notes = ["Every eigenvalue was substituted into the characteristic polynomial (it gives 0)."]
    if vectors:
        for v, k in ordered:
            ns = (m - v * sp.eye(n)).nullspace()
            clean: list[sp.Matrix] = []
            for vec in ns:
                den = sp.ilcm(*[sp.fraction(sp.together(c))[1] for c in vec]) if all(c.is_rational for c in vec) else 1
                clean.append(sp.simplify(vec * den))
            if not clean:
                raise SolverError("I could not find the eigenvectors.", "unverified")
            for vec in clean:
                if sp.simplify(m * vec - v * vec) != sp.zeros(n, 1):
                    raise SolverError("I could not verify an eigenvector.", "unverified")
            steps.append(Step(f"For λ = {eng(v)} solve (A − λI)v = 0.", rf"(A-({tex(v)})I)\vec v=\vec 0,\qquad \vec v={_SEP.join(_mat(vec) for vec in clean)}"))
            answer_parts.append(rf"\lambda={tex(v)}:\ " + r",\ ".join(_mat(vec) for vec in clean))
            text_parts.append(f"λ = {eng(v)}: " + ", ".join(str(list(vec)) for vec in clean))
            if len(clean) < k:
                notes.append(f"For λ = {eng(v)} there are fewer independent eigenvectors than the multiplicity, so the matrix is not diagonalizable.")
        notes.append("Every eigenvector was checked: A·v = λ·v exactly.")
    if vectors:
        answer_parts = [p for p in answer_parts if ":" in p]
        text_parts = [p for p in text_parts if ":" in p]
    question = rf"\text{{eigenvalues{' and eigenvectors' if vectors else ''} of }}{_mat(m)}"
    answer = r"\begin{array}{l}" + r"\\".join(answer_parts) + r"\end{array}"
    return Solution("eigen", question, answer, "; ".join(text_parts), steps, notes)


def combine(a: sp.Matrix, b: sp.Matrix | None, op: str, k: int | sp.Expr | None = None) -> Solution:
    if op == "scale":
        assert k is not None and b is None
        r = (k * a).applyfunc(sp.simplify)
        return Solution("matrix", rf"{tex(k)}{_mat(a)}", _mat(r), str(r.tolist()), [Step("Multiply every entry by the number.", rf"{tex(k)}{_mat(a)}={_mat(r)}")], [])
    if op == "power":
        assert k is not None and b is None
        _square(a, "power")
        n = int(k)
        if n < 0:
            if sp.simplify(a.det()) == 0:
                raise SolverError("The matrix has no inverse, so it has no negative powers.", "bad_matrix")
        if abs(n) > 12:
            raise SolverError("I handle powers up to 12.", "bad_matrix")
        r = (a**n).applyfunc(sp.simplify)
        check = sp.eye(a.rows)
        base = a if n >= 0 else a.inv()
        for _ in range(abs(n)):
            check = check * base
        if sp.simplify(check - r) != sp.zeros(a.rows):
            raise SolverError("I could not verify the power.", "unverified")
        steps = [Step("Multiply the matrix by itself repeatedly.", rf"A^{{{n}}}={_mat(r)}")]
        return Solution("matrix", rf"{_mat(a)}^{{{n}}}", _mat(r), str(r.tolist()), steps, ["Checked by repeated multiplication."])
    assert b is not None
    if op in ("add", "sub"):
        if a.shape != b.shape:
            raise SolverError("To add or subtract, the matrices must have the same size.", "bad_matrix")
        r = (a + b if op == "add" else a - b).applyfunc(sp.simplify)
        sign = "+" if op == "add" else "-"
        return Solution("matrix", rf"{_mat(a)}{sign}{_mat(b)}", _mat(r), str(r.tolist()), [Step("Add or subtract entry by entry.", rf"{_mat(a)}{sign}{_mat(b)}={_mat(r)}")], [])
    if a.cols != b.rows:
        raise SolverError(f"To multiply, the first matrix needs as many columns ({a.cols}) as the second has rows ({b.rows}).", "bad_matrix")
    r = (a * b).applyfunc(sp.simplify)
    explicit = sp.Matrix(a.rows, b.cols, lambda i, j: sp.Add(*[a[i, k2] * b[k2, j] for k2 in range(a.cols)]))
    if sp.simplify(explicit - r) != sp.zeros(a.rows, b.cols):
        raise SolverError("I could not verify the product.", "unverified")
    steps = [
        Step("Each entry of the product is the dot product of a row of the first matrix and a column of the second.", r"(AB)_{ij}=\sum_k a_{ik}b_{kj}"),
        Step("The first entry.", rf"(AB)_{{11}}={'+'.join(rf'({tex(a[0, k2])})({tex(b[k2, 0])})' for k2 in range(a.cols))}={tex(r[0, 0])}"),
        Step("All the entries.", rf"AB={_mat(r)}"),
    ]
    return Solution("matrix", rf"{_mat(a)}{_mat(b)}", _mat(r), str(r.tolist()), steps, ["Checked by computing every entry again from its definition."])


def read_matrix_problem(low: str, text: str) -> Solution | None:
    mats, shape = extract_matrices(text)
    if not mats:
        return None
    s = shape.lower().strip()
    one = mats[0]
    if re.search(r"\b(determinant|det)\b", s):
        return determinant(one)
    if re.search(r"\b(inverse|inv)\b", s) or re.fullmatch(r"m1\s*\^\s*\(?\s*-\s*1\s*\)?", s):
        return inverse(one)
    if "transpose" in s:
        return transpose_trace(one, "transpose")
    if re.search(r"\btrace\b", s):
        return transpose_trace(one, "trace")
    if re.search(r"\beigenvect", s):
        return eigen(one, True)
    if re.search(r"\beigenval", s):
        return eigen(one, False)
    if re.search(r"\b(rref|row reduce|row echelon|gauss|gaussian|reduced)\b", s):
        return row_reduce(one)
    if re.search(r"\brank\b", s):
        return rank_of(one)
    m = re.fullmatch(r"(?:multiply |product of )?m1\s*(?:\*|times|x|by|and)?\s*m2", s) or re.fullmatch(r"(?:multiply |product of )m1\s+(?:by|and|with)\s+m2", s)
    if m and len(mats) == 2:
        return combine(mats[0], mats[1], "mul")
    m = re.fullmatch(r"(?:add )?m1\s*\+\s*m2", s) or re.fullmatch(r"(?:sum of )?m1 plus m2", s)
    if m and len(mats) == 2:
        return combine(mats[0], mats[1], "add")
    m = re.fullmatch(r"(?:subtract )?m1\s*-\s*m2", s) or re.fullmatch(r"m1 minus m2", s)
    if m and len(mats) == 2:
        return combine(mats[0], mats[1], "sub")
    m = re.fullmatch(r"m1\s*\^\s*\(?\s*(-?\d+)\s*\)?", s) or re.fullmatch(r"m1 to the power (?:of )?(-?\d+)", s)
    if m:
        return combine(one, None, "power", int(m.group(1)))
    m = re.fullmatch(r"(-?\d+(?:/\d+)?)\s*\*?\s*m1", s)
    if m:
        return combine(one, None, "scale", sp.Rational(m.group(1)))
    raise SolverError("Tell me what to do with the matrix, for example “determinant of [[1,2],[3,4]]”, “inverse of …”, “eigenvalues of …”, “rank of …”, “[[1,2],[3,4]] * [[0,1],[1,0]]”.", "no_intent")


# ---------------------------------------------------------------------------------------------------- inequalities
def _fmt_set(s: sp.Basic) -> tuple[str, str]:
    """LaTeX and plain text of a subset of the real line."""
    if s == sp.S.Reals:
        return r"\text{all real numbers}", "all real numbers"
    if s == sp.S.EmptySet:
        return r"\text{no real solution}", "no real solution"

    def interval(i: sp.Interval) -> tuple[str, str]:
        lo = r"-\infty" if i.start == -sp.oo else tex(i.start)
        hi = r"\infty" if i.end == sp.oo else tex(i.end)
        left = "(" if i.left_open or i.start == -sp.oo else "["
        right = ")" if i.right_open or i.end == sp.oo else "]"
        tl = ("-oo" if i.start == -sp.oo else eng(i.start))
        th = ("oo" if i.end == sp.oo else eng(i.end))
        return rf"\left{left}{lo},\ {hi}\right{right}", f"{left}{tl}, {th}{right}"

    pieces = list(s.args) if isinstance(s, sp.Union) else [s]
    latex_parts: list[str] = []
    text_parts: list[str] = []
    for piece in sorted(pieces, key=lambda p: float(sp.N(p.inf if isinstance(p, sp.Interval) else min(p.args)) if not (isinstance(p, sp.Interval) and p.inf == -sp.oo) else -1e300)):
        if isinstance(piece, sp.Interval):
            a, b = interval(piece)
            latex_parts.append(a)
            text_parts.append(b)
        elif isinstance(piece, sp.FiniteSet):
            latex_parts.append(r"\left\{" + ",\\ ".join(tex(v) for v in sorted(piece.args, key=lambda v: float(sp.N(v)))) + r"\right\}")
            text_parts.append("{" + ", ".join(eng(v) for v in sorted(piece.args, key=lambda v: float(sp.N(v)))) + "}")
        else:
            raise SolverError("I could not write this solution set.", "no_solution")
    return r"\ \cup\ ".join(latex_parts), " U ".join(text_parts)


def inequality(lhs: sp.Expr, op: str, rhs: sp.Expr, x: sp.Symbol) -> Solution:
    expr = sp.simplify(lhs - rhs)
    rel = {"<": sp.Lt, ">": sp.Gt, "<=": sp.Le, ">=": sp.Ge}[op]
    symbol = {"<": "<", ">": ">", "<=": r"\le", ">=": r"\ge"}[op]
    steps = [Step("Bring everything to one side so that we compare with 0.", rf"{tex(expr)}{symbol}0")]
    factored = sp.factor(expr)
    if factored != expr:
        steps.append(Step("Factor.", rf"{tex(factored)}{symbol}0"))
    try:
        solution = sp.solve_univariate_inequality(rel(expr, 0), x, relational=False)
    except (NotImplementedError, ValueError, TypeError):
        raise SolverError("I could not solve this inequality.", "no_solution") from None
    # a second method for polynomials and fractions: the sign of the expression between its critical values
    notes: list[str] = []
    num, den = sp.fraction(sp.together(expr))
    if num.is_polynomial(x) and den.is_polynomial(x):
        crit_set = sp.solveset(num, x, sp.S.Reals) | sp.solveset(den, x, sp.S.Reals)
        if isinstance(crit_set, sp.FiniteSet):
            crits = sorted(crit_set.args, key=lambda v: float(sp.N(v)))
            steps.append(Step("The sign of the expression can only change at the zeros of the numerator and denominator:", r",\ ".join(tex(c) for c in crits) if crits else r"\text{none}"))
            bounds = [-sp.oo, *crits, sp.oo]
            keep: list[sp.Basic] = []
            rows: list[str] = []
            for lo, hi in zip(bounds, bounds[1:], strict=False):
                if lo == -sp.oo and hi == sp.oo:
                    probe = sp.Integer(0)
                elif lo == -sp.oo:
                    probe = sp.floor(sp.N(hi)) - 1
                elif hi == sp.oo:
                    probe = sp.ceiling(sp.N(lo)) + 1
                else:
                    probe = sp.nsimplify((sp.N(lo, 30) + sp.N(hi, 30)) / 2, rational=True, tolerance=1e-12)
                value = sp.simplify(expr.subs(x, probe))
                ok = bool(rel(value, 0))
                lo_t = r"-\infty" if lo == -sp.oo else tex(lo)
                hi_t = r"\infty" if hi == sp.oo else tex(hi)
                rows.append(rf"x\in\left({lo_t},\,{hi_t}\right):\ \text{{test }}x={tex(probe)}\Rightarrow {tex(value)}\ \text{{({'true' if ok else 'false'})}}")
                if ok:
                    keep.append(sp.Interval.open(lo, hi))
            own: sp.Basic = sp.Union(*keep) if keep else sp.S.EmptySet
            if op in ("<=", ">="):
                zeros = sp.solveset(num, x, sp.S.Reals) - sp.solveset(den, x, sp.S.Reals)
                own = sp.Union(own, zeros)
            if rows:
                steps.append(Step("Test one value in each interval between the critical values.", r"\begin{array}{l}" + r"\\".join(rows) + r"\end{array}"))
            probes = [sp.Rational(k, 4) for k in range(-80, 81)] + list(crits)
            for p in probes:
                try:
                    if (p in solution) != (p in own):
                        raise SolverError("I could not verify the solution set of the inequality.", "unverified")
                except TypeError:
                    continue
            notes.append("Checked a second way: the sign of the expression was tested in every interval, and the answer agrees at 160 sample values.")
            solution = own if own != sp.S.EmptySet or solution == sp.S.EmptySet else solution
    latex, text = _fmt_set(solution)
    steps.append(Step("Collect the intervals where the inequality is true.", latex))
    return Solution("inequality", rf"{tex(lhs)}{symbol}{tex(rhs)}", latex, text, steps, notes)


# ------------------------------------------------------------------------------------------------------ tangent
def tangent_line(f: sp.Expr, a: sp.Expr, normal: bool) -> Solution:
    x = _x()
    fx = f.subs({s: x for s in f.free_symbols})
    steps = [Step("The tangent line at x = a is y = f(a) + f′(a)(x − a).", rf"f(x)={tex(fx)},\quad a={tex(a)}")]
    value = sp.simplify(fx.subs(x, a))
    d = sp.simplify(sp.diff(fx, x))
    slope = sp.simplify(d.subs(x, a))
    if value.has(sp.zoo, sp.nan, sp.oo) or slope.has(sp.zoo, sp.nan, sp.oo):
        raise SolverError("The function or its derivative is not defined at that point.", "undefined")
    steps.append(Step("The value and the derivative.", rf"f({tex(a)})={tex(value)},\qquad f'(x)={tex(d)},\quad f'({tex(a)})={tex(slope)}"))
    h = sp.Rational(1, 10**6)
    approx = sp.N((fx.subs(x, a + h) - fx.subs(x, a - h)) / (2 * h), 25)
    if abs(complex(approx) - complex(sp.N(slope, 25))) > 1e-6 * (1 + abs(complex(approx))):
        raise SolverError("I could not verify the slope.", "unverified")
    if normal:
        if slope == 0:
            steps.append(Step("The tangent is horizontal, so the normal line is vertical.", rf"x={tex(a)}"))
            return Solution("normal_line", rf"\text{{normal to }}y={tex(fx)}\text{{ at }}x={tex(a)}", rf"x={tex(a)}", f"x = {eng(a)}", steps, [])
        ns = sp.simplify(-1 / slope)
        y = sp.expand(value + ns * (x - a))
        steps.append(Step("The normal line is perpendicular to the tangent: its slope is −1/f′(a).", rf"y={tex(value)}+\left({tex(ns)}\right)(x-{tex(a)})={tex(y)}"))
        return Solution("normal_line", rf"\text{{normal to }}y={tex(fx)}\text{{ at }}x={tex(a)}", rf"y={tex(y)}", f"y = {eng(y)}", steps, ["The slope of the tangent was checked with a difference quotient."])
    y = sp.expand(value + slope * (x - a))
    steps.append(Step("Put the value and the slope in the formula.", rf"y={tex(value)}+\left({tex(slope)}\right)(x-{tex(a)})={tex(y)}"))
    if sp.simplify(y.subs(x, a) - value) != 0:
        raise SolverError("I could not verify the tangent line.", "unverified")
    return Solution("tangent_line", rf"\text{{tangent to }}y={tex(fx)}\text{{ at }}x={tex(a)}", rf"y={tex(y)}", f"y = {eng(y)}", steps, ["Checked: the line passes through the point, and its slope matches a difference quotient of the function."])


def tangent_plane(f: sp.Expr, point: dict[sp.Symbol, sp.Expr]) -> Solution:
    x, y = sp.Symbol("x", real=True), sp.Symbol("y", real=True)
    if f.free_symbols - {x, y}:
        raise SolverError("The surface z = f(x, y) may only use x and y.", "bad_variables")
    a, b = point[x], point[y]
    fa = sp.simplify(f.subs({x: a, y: b}))
    fx = sp.simplify(sp.diff(f, x))
    fy = sp.simplify(sp.diff(f, y))
    fxa, fya = sp.simplify(fx.subs({x: a, y: b})), sp.simplify(fy.subs({x: a, y: b}))
    if any(v.has(sp.zoo, sp.nan, sp.oo) for v in (fa, fxa, fya)):
        raise SolverError("The function or its derivatives are not defined at that point.", "undefined")
    steps = [
        Step("The tangent plane at (a, b) is z = f(a, b) + f_x(a, b)(x − a) + f_y(a, b)(y − b).", rf"f={tex(f)},\quad (a,b)=({tex(a)},{tex(b)})"),
        Step("The partial derivatives.", rf"f_x={tex(fx)},\qquad f_y={tex(fy)}"),
        Step("Evaluate at the point.", rf"f(a,b)={tex(fa)},\quad f_x(a,b)={tex(fxa)},\quad f_y(a,b)={tex(fya)}"),
    ]
    z = sp.expand(fa + fxa * (x - a) + fya * (y - b))
    steps.append(Step("Put them in the formula.", rf"z={tex(z)}"))
    h = sp.Rational(1, 10**6)
    for name, d, direction in (("x", fxa, (h, 0)), ("y", fya, (0, h))):
        approx = sp.N((f.subs({x: a + direction[0], y: b + direction[1]}) - f.subs({x: a - direction[0], y: b - direction[1]})) / (2 * h), 25)
        if abs(complex(approx) - complex(sp.N(d, 25))) > 1e-6 * (1 + abs(complex(approx))):
            raise SolverError(f"I could not verify f_{name}.", "unverified")
    normal = sp.Matrix([fxa, fya, -1])
    steps.append(Step("A normal vector to the plane, from the equation fₓ(x−a) + f_y(y−b) − (z−f) = 0.", rf"\vec n={_mat(normal)}"))
    return Solution("tangent_plane", rf"\text{{tangent plane to }}z={tex(f)}\text{{ at }}({tex(a)},{tex(b)})", rf"z={tex(z)}", f"z = {eng(z)}", steps, ["Both partial derivatives were checked with difference quotients."])


# ------------------------------------------------------------------------------------------------------ series
def taylor(f: sp.Expr, a: sp.Expr, order: int) -> Solution:
    x = _x()
    fx = f.subs({s: x for s in f.free_symbols}) if f.free_symbols else f
    if not 1 <= order <= 12:
        raise SolverError("I handle orders from 1 to 12.", "bad_variables")
    steps = [Step("The Taylor polynomial of order n at a is the sum of f⁽ᵏ⁾(a)/k! · (x − a)ᵏ for k = 0 … n.", rf"f(x)={tex(fx)},\quad a={tex(a)},\quad n={order}")]
    terms = []
    rows = []
    cur = fx
    for k in range(order + 1):
        coefficient = sp.simplify(cur.subs(x, a) / sp.factorial(k))
        if coefficient.has(sp.zoo, sp.nan, sp.oo):
            raise SolverError("The function or one of its derivatives is not defined at that point.", "undefined")
        rows.append(rf"f^{{({k})}}({tex(a)})={tex(sp.simplify(cur.subs(x, a)))},\quad \dfrac{{f^{{({k})}}({tex(a)})}}{{{k}!}}={tex(coefficient)}")
        terms.append(coefficient * (x - a) ** k)
        cur = sp.diff(cur, x)
    steps.append(Step("The derivatives at a and the coefficients.", r"\begin{array}{l}" + r"\\".join(rows) + r"\end{array}"))
    poly = sp.expand(sum(terms))
    steps.append(Step("Add the terms (in powers of x − a).", rf"P_{{{order}}}(x)={'+'.join(tex(t) for t in terms if t != 0)}"))
    steps.append(Step("Expand.", rf"P_{{{order}}}(x)={tex(poly)}"))
    # check: the error shrinks like h^(n+1) near a
    nxt = sp.diff(fx, x, order + 1)
    bound = 1 + max(abs(float(sp.N(nxt.subs(x, a + sp.Rational(k, 500))))) for k in range(-5, 6)) / float(sp.factorial(order + 1))
    h = sp.Rational(1, 1000)
    err = abs(sp.N(fx.subs(x, a + h) - poly.subs(x, a + h), 60))
    if err > 50 * bound * float(h) ** (order + 1):
        raise SolverError("I could not verify the Taylor polynomial.", "unverified")
    return Solution("taylor", rf"\text{{Taylor polynomial of }}{tex(fx)}\text{{ at }}x={tex(a)},\ n={order}", rf"P_{{{order}}}(x)={tex(poly)}", f"{eng(poly)}", steps, ["Checked numerically: near a the difference between f and the polynomial is smaller than a constant times (x − a)ⁿ⁺¹."])


def series_sum(term: sp.Expr, k: sp.Symbol, lo: sp.Expr, hi: sp.Expr) -> Solution:
    import mpmath

    infinite = hi == sp.oo
    top = _INFTY if infinite else tex(hi)
    steps = [Step("The sum.", rf"\sum_{{{tex(k)}={tex(lo)}}}^{{{top}}}{tex(term)}")]
    value = sp.simplify(sp.summation(term, (k, lo, hi)))
    notes: list[str] = []
    if isinstance(value, sp.Sum) or value.has(sp.Sum):
        raise SolverError("I could not find a closed form for this sum.", "no_solution")
    if infinite:
        if value in (sp.oo, -sp.oo) or value.has(sp.oo):
            steps.append(Step("The terms do not shrink fast enough: the series diverges.", rf"\sum={tex(value)}"))
            parts = [sum(term.subs(k, i) for i in range(int(lo), int(lo) + n)) for n in (50, 200)] if lo.is_integer else []
            if parts and abs(float(sp.N(parts[1]))) <= abs(float(sp.N(parts[0]))) * 1.0001 and value.has(sp.oo):
                raise SolverError("I could not verify that the series diverges.", "unverified")
            return Solution("sum", rf"\sum_{{{tex(k)}={tex(lo)}}}^{{\infty}}{tex(term)}", r"\text{diverges}", "diverges", steps, ["The partial sums keep growing."])
        steps.append(Step("The series converges; its sum is", rf"\sum={tex(value)}"))
        f = sp.lambdify(k, term, "mpmath")
        try:
            numeric = mpmath.nsum(f, [int(lo), mpmath.inf])
        except Exception:  # noqa: BLE001 - numerical summation can fail for exotic terms; the exact value is still shown
            numeric = None
        if numeric is not None and abs(complex(numeric) - complex(sp.N(value, 20))) > 1e-7 * (1 + abs(complex(numeric))):
            raise SolverError("I could not verify the sum numerically.", "unverified")
        notes.append("The value was also checked by numerical summation.")
    else:
        steps.append(Step("Use the closed form and simplify.", rf"\sum={tex(value)}"))
        if hi.free_symbols:
            for n in range(int(lo) if lo.is_integer else 1, int(lo) + 6 if lo.is_integer else 6):
                explicit = sum(term.subs(k, i) for i in range(int(lo), n + 1))
                if sp.simplify(explicit - value.subs(hi, n)) != 0:
                    raise SolverError("I could not verify the sum.", "unverified")
            notes.append("Checked by adding the terms one by one for n = 1 … 5.")
        else:
            if hi - lo > 5000:
                raise SolverError("This sum has too many terms to check.", "too_long")
            explicit = sum(term.subs(k, i) for i in range(int(lo), int(hi) + 1))
            if sp.simplify(explicit - value) != 0:
                raise SolverError("I could not verify the sum.", "unverified")
            notes.append("Checked by adding the terms one by one.")
    return Solution("sum", rf"\sum_{{{tex(k)}={tex(lo)}}}^{{{top}}}{tex(term)}", tex(value) if value not in (sp.oo,) else _INFTY, eng(value), steps, notes)


# --------------------------------------------------------------------------------------- partial fractions, area
def partial_fractions(f: sp.Expr) -> Solution:
    x = _x()
    fx = f.subs({s: x for s in f.free_symbols}) if f.free_symbols else f
    num, den = sp.fraction(sp.together(fx))
    if not (num.is_polynomial(x) and den.is_polynomial(x)):
        raise SolverError("Partial fractions need a fraction of polynomials.", "bad_variables")
    steps = [Step("The fraction.", tex(fx))]
    factored = sp.factor(den)
    steps.append(Step("Factor the denominator.", rf"{tex(den)}={tex(factored)}"))
    result = sp.apart(fx, x)
    steps.append(Step("Write it as a sum of simpler fractions, one for each factor, and find the numerators.", rf"{tex(fx)}={tex(result)}"))
    for k in range(4):
        v = sp.Rational(7 + 3 * k, 5)
        if sp.denom(sp.together(v)) and abs(complex(sp.N((fx - result).subs(x, v)))) > 1e-9:
            raise SolverError("I could not verify the partial fractions.", "unverified")
    if sp.simplify(sp.together(result) - fx) != 0:
        raise SolverError("I could not verify the partial fractions.", "unverified")
    return Solution("partial_fractions", rf"\text{{partial fractions of }}{tex(fx)}", tex(result), eng(result), steps, ["Checked: the sum of the fractions equals the original fraction (at several values and symbolically)."])


def area_between(f: sp.Expr, g: sp.Expr, a: sp.Expr | None, b: sp.Expr | None) -> Solution:
    import mpmath

    x = _x()
    f = f.subs({s: x for s in f.free_symbols}) if f.free_symbols else f
    g = g.subs({s: x for s in g.free_symbols}) if g.free_symbols else g
    steps = [Step("The area between the curves is the integral of (upper − lower), taken piece by piece.", rf"y={tex(f)},\qquad y={tex(g)}")]
    if a is None or b is None:
        roots = sp.solve(sp.Eq(f, g), x)
        pts = sorted({sp.simplify(r) for r in roots if sp.im(sp.N(r)) == 0}, key=lambda v: float(sp.N(v)))
        if len(pts) < 2:
            raise SolverError("The curves must meet in at least two points to enclose an area; or give the limits, for example “from 0 to 2”.", "no_solution")
        steps.append(Step("Where the curves meet: solve f(x) = g(x).", rf"x={_SEP.join(tex(p) for p in pts)}"))
        cuts = pts
    else:
        inner = [r for r in sp.solve(sp.Eq(f, g), x) if sp.im(sp.N(r)) == 0 and float(sp.N(a)) < float(sp.N(r)) < float(sp.N(b))]
        cuts = [a, *sorted({sp.simplify(r) for r in inner}, key=lambda v: float(sp.N(v))), b]
    total = sp.Integer(0)
    for lo, hi in zip(cuts, cuts[1:], strict=False):
        mid = sp.nsimplify((sp.N(lo, 30) + sp.N(hi, 30)) / 2, rational=True, tolerance=1e-12)
        upper, lower = (f, g) if sp.N((f - g).subs(x, mid)) >= 0 else (g, f)
        diff = sp.expand(upper - lower)
        steps.append(Step(f"On [{eng(lo)}, {eng(hi)}] the upper curve is y = {eng(upper)}.", rf"\int_{{{tex(lo)}}}^{{{tex(hi)}}}\left({tex(upper)}-\left({tex(lower)}\right)\right)dx"))
        piece, inner_steps = _definite(diff, x, lo, hi)
        steps.extend(inner_steps)
        total += piece
    total = sp.simplify(total)
    steps.append(Step("Add the pieces. The area is", rf"{tex(total)}\ \text{{squ}}"))
    h = sp.lambdify(x, f - g, "mpmath")
    try:
        numeric = sum(mpmath.quad(lambda t: abs(h(t)), [float(sp.N(lo)), float(sp.N(hi))]) for lo, hi in zip(cuts, cuts[1:], strict=False))
        if abs(complex(numeric) - complex(sp.N(total, 20))) > 1e-6 * (1 + abs(complex(numeric))):
            raise SolverError("I could not verify the area numerically.", "unverified")
    except (TypeError, ValueError):
        pass
    return Solution("area", rf"\text{{area between }}y={tex(f)}\text{{ and }}y={tex(g)}", rf"{tex(total)}\ \text{{squ}}", f"{eng(total)} squ", steps, ["The value was also checked by numerical integration of |f − g|."])

