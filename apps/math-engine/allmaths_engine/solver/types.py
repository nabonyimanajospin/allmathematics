"""Shared types of the step-by-step solver."""

from __future__ import annotations

from dataclasses import dataclass, field

import sympy as sp


@dataclass
class Step:
    """One line of a worked solution: a short explanation (plain text) and the mathematics (LaTeX, shown on its own line)."""

    title: str
    latex: str = ""


@dataclass
class Solution:
    operation: str
    question_latex: str
    answer_latex: str
    answer_text: str
    steps: list[Step] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class SolverError(ValueError):
    """The request cannot be solved; the message is safe to show to the learner."""

    def __init__(self, message: str, code: str = "cannot_solve") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


def tex(e: object) -> str:
    """LaTeX of a SymPy object with display fractions, as everywhere else on the platform."""
    text = sp.latex(e, fold_short_frac=False, mul_symbol=None, ln_notation=True)
    return text.replace("\\frac", "\\dfrac")


def eng(e: object) -> str:
    """Plain text of an exact value (the form a learner would type)."""
    return str(e).replace("**", "^").replace("log(", "ln(")
