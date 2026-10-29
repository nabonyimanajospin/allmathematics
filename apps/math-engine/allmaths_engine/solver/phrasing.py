"""Reads the way a learner naturally asks and rewrites it into the closed grammar of the solver.

"derive sin x", "please integrate x^2 from 0 to 1", "roots of x^2-4", "can you find the grad of x^2*y", "dervative of x^3" or "intergral of x"
all become the sentence the solver already understands ("derivative of sin x", "integral of x^2 from 0 to 1", "solve x^2-4 = 0", ...).
Only the first words of the sentence are rewritten; the mathematics itself is never touched. The solver tells the learner how it read the problem.
"""

from __future__ import annotations

import difflib
import re

from ..parser import _WORDS

# the words that may come before the verb: "find the", "please take the", "can you", "I want to", ...
_POLITE = re.compile(
    r"^(?:(?:please|pls|kindly)[,\s]+)?"
    r"(?:(?:can|could|would|will) you\s+(?:please\s+)?|i (?:want|need|would like) (?:you )?to\s+|help me\s+(?:to\s+)?|how (?:do i|can i|to)\s+|show me\s+(?:how to\s+)?|let'?s\s+)?",
    re.IGNORECASE,
)
_LEAD = r"(?:(?:find|compute|calculate|determine|take|get|evaluate|work out|give me)\s+)?(?:the\s+)?"

# (what the learner writes, what the solver reads); the rest of the sentence follows unchanged
_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(rf"^{_LEAD}(?:derive|derivate|deriv|differentiate|differentiation|differenciate|diff)\b(?:\s+of)?\s+", re.IGNORECASE), "derivative of "),
    (re.compile(rf"^{_LEAD}(?:antiderivative|anti-derivative|primitive|integrate|integration)\b(?:\s+of)?\s+", re.IGNORECASE), "integral of "),
    (re.compile(rf"^{_LEAD}grad\b(?:\s+of)?\s+", re.IGNORECASE), "gradient of "),
    (re.compile(rf"^{_LEAD}det\b(?:\s+of)?\s+", re.IGNORECASE), "determinant of "),
    (re.compile(rf"^{_LEAD}inv\b(?:\s+of)?\s+", re.IGNORECASE), "inverse of "),
]
_ROOTS = re.compile(rf"^{_LEAD}(?:roots|zeros|zeroes|solutions)\s+of\s+(.+)$", re.IGNORECASE)

# the verbs of the grammar, for a misspelled first word ("dervative", "intergral", "simplfy")
VERBS = ("derivative", "differentiate", "integral", "integrate", "limit", "simplify", "expand", "factor", "solve", "gradient", "determinant", "inverse", "eigenvalues", "tangent", "taylor")
_FIRST_WORD = re.compile(r"^([A-Za-z]{5,})\b", re.DOTALL)
CUTOFF = 0.85


def suggest(word: str, cutoff: float = 0.6) -> str | None:
    """The verb that a misspelled word is closest to, or None."""
    close = difflib.get_close_matches(word.lower(), VERBS, n=1, cutoff=cutoff)
    return close[0] if close else None


def _fix_first_word(text: str) -> str:
    m = _FIRST_WORD.match(text)
    if not m:
        return text
    word = m.group(1).lower()
    if word in VERBS or word in _WORDS:
        return text
    fixed = suggest(word, CUTOFF)
    return fixed + text[m.end(1) :] if fixed else text


def normalize(text: str) -> str:
    """The problem rewritten for the solver; the text itself when there is nothing to rewrite."""
    out = _POLITE.sub("", text.strip(), count=1)
    out = _fix_first_word(out)
    for pattern, replacement in _RULES:
        if pattern.match(out):
            out = replacement + pattern.sub("", out, count=1)
            break
    m = _ROOTS.match(out)
    if m:
        body = m.group(1).strip()
        out = f"solve {body}" if "=" in body else f"solve {body} = 0"
    return out.strip() or text
