"""Safe parser for student answers and content expressions.

No eval, no sympify of raw strings. A hand-written recursive-descent parser builds SymPy objects directly
from a closed grammar, with hard limits on input size, nesting depth and the size of numeric powers.

Grammar (precedence from low to high):
    expr    := term (('+' | '-') term)*
    term    := unary (('*' | '/' | implicit) unary)*       implicit multiplication: 2x, 2(x+1), (a)(b), 2sqrt(3)
    unary   := ('-' | '+') unary | power
    power   := atom ('^' signed_power)?                    right-associative, -x^2 = -(x^2)
    atom    := number | name | call | '(' expr (',' expr)* ')'

A parenthesised comma list is a vector/point and becomes a sympy Tuple.
A function without parentheses takes one atom (``sin x``); if more factors follow (``sin 2x``) the input is
rejected so that it is never silently misread.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

import sympy as sp

from . import vectors as vec
from .errors import ComplexityError, ParseError
from .latex_in import latex_to_text

MAX_TEXT_LENGTH = 500
MAX_DEPTH = 40
MAX_OPS = 400
MAX_BITS = 20_000

_SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻", "0123456789+-")
_UNICODE = {
    "−": "-", "–": "-", "—": "-", "×": "*", "·": "*", "⋅": "*", "÷": "/", "√": "sqrt", "π": "pi",
    "θ": "theta", "φ": "phi", "ρ": "rho", "α": "alpha", "β": "beta", "γ": "gamma", "λ": "lambda",
    "μ": "mu", "σ": "sigma", "ω": "omega", "⟨": "(", "⟩": ")", "〈": "(", "〉": ")",
    "’": "'", " ": " ",
}

CONSTANTS: dict[str, sp.Expr] = {"pi": sp.pi, "e": sp.E, "oo": sp.oo}

_UNARY: dict[str, Callable[[sp.Expr], sp.Expr]] = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot, "sec": sp.sec, "csc": sp.csc,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "arcsin": sp.asin, "arccos": sp.acos,
    "arctan": sp.atan, "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "ln": sp.log, "log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt, "abs": sp.Abs,
    # the distribution function of the standard normal law: Phi(z) = P(Z <= z)
    "Phi": lambda z: (1 + sp.erf(z / sp.sqrt(2))) / 2,
}
_GREEK = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta", "vartheta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "rho", "sigma", "tau", "phi", "varphi", "chi", "psi",
    "omega",
}
# Vector functions available to content expressions (e.g. cross(u, v)). Students may use them too.
_VECTOR_FUNCS: dict[str, Callable[..., object]] = {
    "dot": vec.dot, "cross": vec.cross, "norm": vec.norm, "box": vec.box, "proj": vec.proj,
    "comp": vec.comp, "cos_angle": vec.cos_angle, "unit": vec.unit,
}
# Calculus functions are for trusted content only (worked examples and answer keys), never for student input:
# an integral or a limit can take arbitrarily long to compute.
_CALCULUS = {"diff", "integrate", "limit"}
_WORDS = sorted(
    set(_UNARY) | set(_VECTOR_FUNCS) | set(CONSTANTS) | _GREEK | {"root"} | _CALCULUS, key=len, reverse=True
)

_TOKEN_RE = re.compile(
    r"""
    (?P<num>\d+\.\d*|\.\d+|\d+)
  | (?P<sym>[A-Za-z](?:\d+|'+))
  | (?P<name>[A-Za-z]+(?:_[A-Za-z0-9]+)?)
  | (?P<op>[-+*/^(),|])
  | (?P<ws>\s+)
    """,
    re.VERBOSE,
)


@dataclass
class Token:
    kind: str  # num | name | op | end
    text: str


@dataclass
class Parsed:
    """Result of parsing: the value plus facts about how it was written."""

    value: object  # sp.Expr or sp.Tuple
    has_decimal: bool = False
    names: set[str] = field(default_factory=set)


def normalize(text: str) -> str:
    text = text.replace("**", "^").translate(_SUPERSCRIPTS)
    for k, v in _UNICODE.items():
        text = text.replace(k, v if v.isalpha() is False else f" {v} ")
    return text


def tokenize(text: str) -> tuple[list[Token], bool]:
    tokens: list[Token] = []
    has_decimal = False
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if m is None:
            raise ParseError(f"I do not understand the character “{text[pos]}”.", "bad_character")
        pos = m.end()
        if m.lastgroup == "ws":
            continue
        if m.lastgroup == "num":
            if "." in m.group():
                has_decimal = True
            tokens.append(Token("num", m.group()))
        elif m.lastgroup == "sym":
            # x0, C1, y2 are one symbol; y' and y'' are the first and second derivative symbols y1 and y2
            word = m.group()
            tokens.append(Token("name", word[0] + str(word.count("'")) if "'" in word else word))
        elif m.lastgroup == "name":
            tokens.extend(_split_name(m.group()))
        else:
            tokens.append(Token("op", m.group()))
    tokens.append(Token("end", ""))
    return tokens, has_decimal


def _split_name(word: str) -> list[Token]:
    """Split a run of letters into known words and single letters, e.g. 'pix' -> pi, x ; 'xy' -> x, y."""
    if "_" in word:  # subscripted symbol such as C_1 or x_2 stays whole
        return [Token("name", word)]
    out: list[Token] = []
    i = 0
    while i < len(word):
        for w in _WORDS:
            if word.startswith(w, i):
                out.append(Token("name", w))
                i += len(w)
                break
        else:
            out.append(Token("name", word[i]))
            i += 1
    return out


class _Parser:
    def __init__(self, tokens: list[Token], variables: set[str] | None, trusted: bool = False) -> None:
        self.trusted = trusted
        self.t = tokens
        self.i = 0
        self.depth = 0
        self.bars = 0  # number of |...| absolute-value bars currently open
        self.variables = variables
        self.names: set[str] = set()

    # --- helpers -----------------------------------------------------------------------------
    @property
    def cur(self) -> Token:
        return self.t[self.i]

    def eat(self) -> Token:
        tok = self.t[self.i]
        self.i += 1
        return tok

    def accept(self, op: str) -> bool:
        if self.cur.kind == "op" and self.cur.text == op:
            self.i += 1
            return True
        return False

    def expect(self, op: str) -> None:
        if not self.accept(op):
            raise ParseError(f"Expected “{op}” in the answer.", "expected_symbol")

    def starts_atom(self) -> bool:
        c = self.cur
        if c.kind == "op" and c.text == "|":
            return self.bars == 0  # inside |...| a bar after an operand closes it
        return c.kind in {"num", "name"} or (c.kind == "op" and c.text == "(")

    def enter(self) -> None:
        self.depth += 1
        if self.depth > MAX_DEPTH:
            raise ComplexityError("The answer is nested too deeply.", "too_deep")

    def leave(self) -> None:
        self.depth -= 1

    # --- grammar -----------------------------------------------------------------------------
    def parse(self) -> object:
        if self.cur.kind == "end":
            raise ParseError("The answer is empty.", "empty")
        value = self.expr_or_tuple()
        if self.cur.kind != "end":
            raise ParseError("Part of the answer could not be understood.", "trailing_input")
        return value

    def expr_or_tuple(self) -> object:
        first = self.expr()
        if self.cur.kind == "op" and self.cur.text == ",":
            items = [first]
            while self.accept(","):
                items.append(self.expr())
            return self._tuple(items)
        return first

    @staticmethod
    def _tuple(items: list[object]) -> sp.Tuple:
        for it in items:
            if isinstance(it, sp.Tuple):
                raise ParseError("Nested vectors are not supported.", "nested_vector")
        return sp.Tuple(*items)

    def expr(self) -> object:
        self.enter()
        left = self.term()
        while self.cur.kind == "op" and self.cur.text in "+-":
            op = self.eat().text
            right = self.term()
            left = vec.add(left, right) if op == "+" else vec.sub(left, right)
        self.leave()
        return left

    def term(self) -> object:
        left = self.unary()
        while True:
            if self.cur.kind == "op" and self.cur.text in "*/":
                op = self.eat().text
                right = self.unary()
                left = vec.mul(left, right) if op == "*" else vec.div(left, right)
            elif self.starts_atom():
                if self.cur.kind == "num" and self.t[self.i - 1].kind == "num":
                    raise ParseError("Put an operator between the numbers, for example 2*3.", "adjacent_numbers")
                right = self.unary()
                left = vec.mul(left, right)
            else:
                return left

    def unary(self) -> object:
        if self.cur.kind == "op" and self.cur.text in "+-":
            op = self.eat().text
            self.enter()
            operand = self.unary()
            self.leave()
            return vec.neg(operand) if op == "-" else operand
        return self.power()

    def power(self) -> object:
        base = self.atom()
        if self.accept("^"):
            self.enter()
            exp = self.signed_power()
            self.leave()
            return self._pow(base, exp)
        return base

    def signed_power(self) -> object:
        if self.cur.kind == "op" and self.cur.text in "+-":
            op = self.eat().text
            inner = self.signed_power()
            return vec.neg(inner) if op == "-" else inner
        return self.power()

    @staticmethod
    def _pow(base: object, exp: object) -> sp.Expr:
        if isinstance(base, sp.Tuple) or isinstance(exp, sp.Tuple):
            raise ParseError("Powers of vectors are not defined.", "vector_power")
        assert isinstance(base, sp.Expr) and isinstance(exp, sp.Expr)
        if base.is_Number and exp.is_Number:
            if exp.is_Integer:
                if abs(int(exp)) > 5000:
                    raise ComplexityError("That power is too large to compute.", "too_large")
                bits = (abs(int(base.p)) if base.is_Rational else 2).bit_length() * abs(int(exp))
                if bits > MAX_BITS:
                    raise ComplexityError("That number is too large to compute.", "too_large")
            elif exp.is_Rational:
                # 2^(1/3) is fine; 123456789^(1/3) fine; but huge radicands are not
                if base.is_Rational and (abs(int(base.p)) > 10**12 or int(base.q) > 10**12):
                    raise ComplexityError("That number is too large to compute.", "too_large")
        return base**exp

    def atom(self) -> object:
        tok = self.cur
        if tok.kind == "num":
            self.eat()
            return sp.Rational(tok.text) if "." in tok.text else sp.Integer(tok.text)
        if tok.kind == "name":
            return self.name_or_call()
        if tok.kind == "op" and tok.text == "(":
            self.eat()
            self.enter()
            inner = self.expr_or_tuple()
            self.leave()
            self.expect(")")
            return inner
        if tok.kind == "op" and tok.text == "|":
            self.eat()
            self.enter()
            self.bars += 1
            inner = self.expr()
            self.bars -= 1
            self.leave()
            self.expect("|")
            if isinstance(inner, sp.Tuple):
                raise ParseError("Use norm(...) for the length of a vector.", "vector_in_bars")
            assert isinstance(inner, sp.Expr)
            return sp.Abs(inner)
        if tok.kind == "end":
            raise ParseError("The answer ends unexpectedly.", "unexpected_end")
        raise ParseError(f"Unexpected “{tok.text}” in the answer.", "unexpected_symbol")

    def name_or_call(self) -> object:
        name = self.eat().text
        if name in _CALCULUS:
            if not self.trusted:
                raise ParseError(f"“{name}” cannot be used in an answer.", "not_allowed")
            return self.call(name)
        if name in _UNARY or name in _VECTOR_FUNCS or name == "root":
            return self.call(name)
        if name in CONSTANTS:
            return CONSTANTS[name]
        return self.symbol(name)

    def symbol(self, name: str) -> sp.Symbol:
        if self.variables is not None and name not in self.variables:
            raise ParseError(f"The answer uses “{name}”, which is not part of this problem.", "unknown_name")
        self.names.add(name)
        return sp.Symbol(name, real=True)

    def call(self, name: str) -> object:
        if self.cur.kind == "op" and self.cur.text == "(":
            self.eat()
            self.enter()
            args = [self.expr()]
            while self.accept(","):
                args.append(self.expr())
            self.leave()
            self.expect(")")
        else:
            if name in _VECTOR_FUNCS or name == "root" or name in _CALCULUS:
                raise ParseError(f"“{name}” needs parentheses, like {name}(…).", "func_parens")
            arg = self.power()
            if self.starts_atom():
                raise ParseError(
                    f"Please put parentheses around the argument of {name}, for example {name}(2x).",
                    "func_parens",
                )
            args = [arg]
        return self.apply(name, args)

    @staticmethod
    def apply(name: str, args: list[object]) -> object:
        if name in _CALCULUS:
            return _calculus(name, args)
        if name == "root":
            if len(args) != 2 or not all(isinstance(a, sp.Expr) for a in args):
                raise ParseError("root(x, n) needs two numbers.", "bad_call")
            x, n = args
            assert isinstance(x, sp.Expr) and isinstance(n, sp.Expr)
            return _Parser._pow(x, 1 / n)
        if name in _UNARY:
            if len(args) != 1 or isinstance(args[0], sp.Tuple):
                raise ParseError(f"{name} takes exactly one number.", "bad_call")
            arg = args[0]
            assert isinstance(arg, sp.Expr)
            return _UNARY[name](arg)
        try:
            return _VECTOR_FUNCS[name](*args)
        except (TypeError, ValueError, vec.VectorError) as exc:
            raise ParseError(f"{name}(…) was used with the wrong arguments: {exc}", "bad_call") from exc


def _calculus(name: str, args: list[object]) -> object:
    """diff(f, x[, n]), integrate(f, x[, a, b]) and limit(f, x, a): evaluated exactly by SymPy."""
    if not args or not all(isinstance(a, sp.Expr) for a in args):
        raise ParseError(f"{name}(...) needs expressions, not vectors.", "bad_call")
    exprs = [a for a in args if isinstance(a, sp.Expr)]
    f = exprs[0]
    if len(exprs) < 2 or not isinstance(exprs[1], sp.Symbol):
        raise ParseError(f"{name}(f, x, ...) needs a variable as its second argument.", "bad_call")
    x = exprs[1]
    try:
        if name == "diff":
            n = int(exprs[2]) if len(exprs) > 2 else 1
            return sp.diff(f, x, n)
        if name == "integrate":
            if len(exprs) == 2:
                return sp.integrate(f, x)
            if len(exprs) == 4:
                return sp.simplify(sp.integrate(f, (x, exprs[2], exprs[3])))
            raise ParseError("integrate(f, x) or integrate(f, x, a, b).", "bad_call")
        if len(exprs) != 3:
            raise ParseError("limit(f, x, a).", "bad_call")
        return sp.limit(f, x, exprs[2])
    except (ValueError, NotImplementedError, TypeError) as exc:
        raise ParseError(f"{name}(...) could not be computed: {exc}", "bad_call") from exc


def parse(
    text: str,
    *,
    fmt: str = "auto",
    variables: set[str] | None = None,
    trusted: bool = False,
) -> Parsed:
    """Parse `text` (LaTeX or plain text) into a SymPy value.

    variables: allowed free symbol names; None allows any letter. Names like pi/e/sin are never variables.
    """
    if not isinstance(text, str):
        raise ParseError("The answer must be text.", "not_text")
    if len(text) > MAX_TEXT_LENGTH:
        raise ComplexityError("The answer is too long.", "too_long")
    if not text.strip():
        raise ParseError("The answer is empty.", "empty")
    if fmt == "auto":
        fmt = "latex" if ("\\" in text or "{" in text or "}" in text) else "text"
    if fmt == "latex":
        text = latex_to_text(text)
    elif fmt != "text":
        raise ParseError("Unknown input format.", "bad_format")
    text = normalize(text)
    tokens, has_decimal = tokenize(text)
    p = _Parser(tokens, variables, trusted)
    value = p.parse()
    if sp.count_ops(value) > MAX_OPS:
        raise ComplexityError("The answer is too complex.", "too_complex")
    return Parsed(value=value, has_decimal=has_decimal, names=p.names)
