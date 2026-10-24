"""Course 3 (stat): practice questions of the same kinds as the mid-summer exam, with other numbers (not from the sheet)."""

from __future__ import annotations

import math

import sympy as sp
from stat_course import R, pr
from toolkit import add_extra, ex, exset_plain

SCRIPT = "stat_exam_practice.py"
M1 = "stat/m01-probability"
x = sp.Symbol("x", real=True)
FMT = "Type a whole number or a fraction such as `5/12` (not a decimal)."


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


def exam_practice_items() -> list[dict]:
    out: list[dict] = []
    for tag, a, b, n in (("1", 1, 4, 14), ("2", 2, 6, 11)):
        assert a * math.comb(n, 3) == b * math.comb(n, 2)
        lead = "" if a == 1 else str(a)
        out.append(
            pr(
                f"xp-n{tag}",
                rf"Determine $n$ in ${lead}\dbinom n3={b}\dbinom n2$.",
                n,
                rf"$\dbinom n3=\dfrac{{n(n-1)(n-2)}}6$ and $\dbinom n2=\dfrac{{n(n-1)}}2$. Divide the equation by $n(n-1)$ (it is not $0$): ${a}\cdot\dfrac{{n-2}}{{6}}={b}\cdot\dfrac12$, so $n-2={b * 3 // a}$ and $n={n}$.",
                [r"Write the coefficients as products and divide by $n(n-1)$."],
            )
        )
    for tag, a_part, b_part, n, label in (
        ("1", 2 * x, -1 / x**2, 12, r"\left(2x-\dfrac1{x^2}\right)^{12}"),
        ("2", x**2, -1 / (2 * x), 9, r"\left(x^2-\dfrac1{2x}\right)^{9}"),
    ):
        found = None
        for k in range(n + 1):
            term = sp.simplify(sp.binomial(n, k) * a_part ** (n - k) * b_part**k)
            if not term.has(x):
                found = (k, term)
                break
        assert found is not None
        k, term = found
        out.append(
            pr(
                f"xp-c{tag}",
                rf"Find the constant term in the expansion of ${label}$.",
                term,
                rf"The power of $x$ in the general term $T_{{k+1}}$ is $0$ for $k={k}$ (set the exponent equal to $0$ and solve). $T_{{{k + 1}}}=\dbinom{{{n}}}{{{k}}}a^{{{n - k}}}b^{{{k}}}={sp.latex(term).replace(chr(92) + 'frac', chr(92) + 'dfrac')}$.",
                [r"Collect the power of $x$ in the general term."],
            )
        )
    out.append(pr("xp-i1", r"$A$ and $B$ are independent with $P(A)=\dfrac35$ and $P(B)=\dfrac14$. Find $P(A\mid\bar B)$.", R(3, 5), r"$A$ and $\bar B$ are independent, so $P(A\mid\bar B)=P(A)=\dfrac35$.", [r"The complement of an independent event is still independent."]))
    out.append(pr("xp-i2", r"$A$ and $B$ are independent with $P(A)=\dfrac35$ and $P(B)=\dfrac14$. Find $P(\bar A\cup\bar B)$.", 1 - R(3, 20), r"$\bar A\cup\bar B=\overline{A\cap B}$ (De Morgan) and $P(A\cap B)=\dfrac35\cdot\dfrac14=\dfrac3{20}$, so $P=1-\dfrac3{20}=\dfrac{17}{20}$.", [r"De Morgan's law."]))
    out.append(
        pr(
            "xp-p1",
            r"A student passes mathematics with probability $0.6$, passes both mathematics and statistics with probability $0.25$, and passes at least one of them with probability $0.7$. What is the probability that she passes mathematics and fails statistics?",
            R(7, 20),
            r"$P(M\cap\bar S)=P(M)-P(M\cap S)=0.6-0.25=0.35=\dfrac7{20}$. (The event $M$ is split into 'passes statistics' and 'fails statistics'.)",
            [r"Split $M$ into passes and fails statistics."],
        )
    )
    pf = R(3, 5) * R(3, 10) + R(2, 5) * R(1, 5)
    out.append(
        pr(
            "xp-b1",
            r"Three-fifths of the students are boys. The probability of a first class is $0.3$ for a boy and $0.2$ for a girl. A student with a first class is chosen at random. What is the probability that she is a girl?",
            R(2, 5) * R(1, 5) / pf,
            r"$P(F)=\dfrac35\cdot\dfrac3{10}+\dfrac25\cdot\dfrac15=\dfrac9{50}+\dfrac4{50}=\dfrac{13}{50}$. Bayes: $P(\text{girl}\mid F)=\dfrac{\frac25\cdot\frac15}{13/50}=\dfrac{4/50}{13/50}=\dfrac4{13}$.",
            [r"Total probability first, then Bayes."],
        )
    )
    out.append(
        mc(
            "xp-m1",
            r"$P(A)=0.3$ and $P(B)=0.5$. If $A$ and $B$ are mutually exclusive, what is $P(A\cup B)$, and can they be independent?",
            [r"$0.8$, and they can be independent", r"$0.8$, and they cannot be independent", r"$0.65$, and they are independent", r"$0.15$, and they are mutually exclusive"],
            1,
            r"For mutually exclusive events $P(A\cap B)=0$.",
            r"Mutually exclusive: $P(A\cup B)=0.3+0.5=0.8$. Independent would need $P(A\cap B)=0.3\cdot0.5=0.15\ne0$. Two events of positive probability that cannot occur together are never independent.",
        )
    )
    return out


def register() -> None:
    add_extra(f"{M1}/u03-practice-exam/l01-mid-summer-exam-2025-2026", exset_plain("exam-practice", "More questions of the same kinds as the exam, with other numbers.", exam_practice_items(), format=FMT), SCRIPT, orphan=True)


def build() -> None:
    pass
