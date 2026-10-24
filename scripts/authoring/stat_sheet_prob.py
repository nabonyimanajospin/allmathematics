"""Course 3 (stat): the probability part of the STAT8225 exercise sheet.

Probabilities are computed exactly with fractions. Questions about two events are answered from the four cells of a Venn diagram
(A and B, A only, B only, neither): the cells must be real probabilities (between 0 and 1, adding up to 1), which also checks that the data of
the exercise are consistent. Printed errors of the sheet are corrected and said in the `note` of the exercise."""

from __future__ import annotations

import itertools
import math
from fractions import Fraction

import sympy as sp
from stat_course import C, R, pr
from toolkit import ex, exset

SOURCE = "STAT8225 exercise sheet, T. Hakizimana"
SCRIPT = "stat_sheet_prob.py"
M1 = "stat/m01-probability"
FMT = "Type a fraction such as `5/11` (not a decimal). For a formula in a, b, c type for example `2*a-b+1`."
a_, b_, c_ = (sp.Symbol(s, real=True) for s in "abc")


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


def T(v: sp.Rational) -> str:
    return sp.latex(sp.Rational(v)).replace("\\frac", "\\dfrac")


# --- equally likely outcomes (sheet 1 to 8) ----------------------------------------------------------------------------------------------
def equally_likely_items() -> list[dict]:
    it: list[dict] = []
    heads = sum(1 for o in itertools.product("HT", repeat=3) if o.count("H") == 2)
    assert R(heads, 8) == R(3, 8)
    it.append(pr("eq-1", r"Three coins are tossed together. Find the probability that there are exactly $2$ heads.", R(3, 8),
                 r"There are $2^3=8$ equally likely outcomes. Exactly two heads: choose which $2$ of the $3$ coins show heads, $\dbinom32=3$ outcomes (HHT, HTH, THH). So the probability is $\dfrac38$.", ["List the $8$ outcomes or count with $\\dbinom32$."]))
    at_least = sum(1 for o in itertools.product("HT", repeat=2) if o.count("T") >= 1)
    at_most = sum(1 for o in itertools.product("HT", repeat=2) if o.count("T") <= 1)
    assert at_least == 3 and at_most == 3
    it.append(pr("eq-2a", r"A coin is tossed two times. Find the probability of getting at least one tail.", R(3, 4),
                 r"The $4$ outcomes HH, HT, TH, TT are equally likely. At least one tail: HT, TH, TT, that is $3$ outcomes. Or by the complement: $1-P(\text{no tail})=1-\dfrac14=\dfrac34$.", ["Use the complement: no tail at all."]))
    it.append(pr("eq-2b", r"A coin is tossed two times. Find the probability of getting at most one tail.", R(3, 4),
                 r"At most one tail means $0$ or $1$ tail: HH, HT, TH, $3$ outcomes among $4$. So $\dfrac34$ (the only excluded outcome is TT).", ["The excluded outcome is two tails."],
                 note="The sheet writes 'at least/most one tail'; both readings are asked, and both give $\\dfrac34$."))
    it.append(pr("eq-3", r"A card is drawn at random from an ordinary pack of $52$ cards. Find the chance that it is a court card (king, queen or jack).", R(12, 52),
                 r"There are $3$ court ranks with $4$ suits each: $12$ court cards among $52$. $\dfrac{12}{52}=\dfrac3{13}$.", ["$3$ ranks times $4$ suits."]))
    v = R(math.comb(8, 2), math.comb(52, 2))
    it.append(pr("eq-4a", r"Two cards are drawn at random from a well-shuffled pack of $52$. Find the probability that each of the two cards is a king or a queen.", v,
                 r"There are $\dbinom{52}2=1326$ equally likely pairs. There are $8$ kings and queens, and the favorable pairs are the pairs of two of them: $\dbinom82=28$. So $\dfrac{28}{1326}=\dfrac{14}{663}$.", ["Choose both cards among the $8$ kings and queens."],
                 note="The sheet's wording 'king or queen' is read as: each of the two cards is a king or a queen."))
    v = R(4 * 4, math.comb(52, 2))
    it.append(pr("eq-4b", r"Two cards are drawn at random from a well-shuffled pack of $52$. Find the probability that one is a king and the other a jack.", v,
                 r"Favorable pairs: one of the $4$ kings and one of the $4$ jacks, $4\cdot4=16$. Total pairs $\dbinom{52}2=1326$. So $\dfrac{16}{1326}=\dfrac8{663}$.", ["Choose the king, then the jack."]))
    v = R(math.comb(26, 4) * math.comb(26, 3), math.comb(52, 7))
    it.append(pr("eq-5", r"Seven cards are drawn at random from a pack of $52$. Find the probability that $4$ are red and $3$ are black.", v,
                 rf"The pack has $26$ red and $26$ black cards. Favorable hands: $4$ red among $26$ and $3$ black among $26$, $\dbinom{{26}}4\dbinom{{26}}3={math.comb(26, 4)}\cdot{math.comb(26, 3)}={math.comb(26, 4) * math.comb(26, 3)}$. All hands: $\dbinom{{52}}7={math.comb(52, 7)}$. The probability is $\dfrac{{{math.comb(26, 4) * math.comb(26, 3)}}}{{{math.comb(52, 7)}}}={T(v)}$ after simplifying.", ["Choose the red cards and the black cards separately."]))
    v = R(math.comb(4, 2) * math.comb(5, 2), math.comb(9, 4))
    it.append(pr("eq-6", r"Four persons are chosen at random from a group of $3$ men, $2$ women and $4$ children. Find the chance that exactly two of them are children.", v,
                 r"The group has $9$ people. Favorable choices: $2$ children among $4$, and the other $2$ among the $5$ adults, $\dbinom42\dbinom52=6\cdot10=60$. All choices: $\dbinom94=126$. So $\dfrac{60}{126}=\dfrac{10}{21}$.", ["The two non-children come from the $5$ adults."]))
    v = R(math.comb(3, 2) * 4 * 5, math.comb(12, 4))
    it.append(pr("eq-7", r"From $3$ engineers, $4$ doctors and $5$ lawyers a sub-committee of four is selected by lots. Find the probability that it consists of $2$ engineers, $1$ doctor and $1$ lawyer.", v,
                 r"Favorable: $\dbinom32\cdot\dbinom41\cdot\dbinom51=3\cdot4\cdot5=60$. All sub-committees: $\dbinom{12}4=495$. So $\dfrac{60}{495}=\dfrac4{33}$.", ["Multiply the choices in each group."]))
    # 8) the three drivers: A = 2B, B = 2C, A + B + C = 1
    pc = sp.Symbol("pc")
    sol = sp.solve(sp.Eq(4 * pc + 2 * pc + pc, 1), pc)[0]
    pa_, pb_, pc_ = 4 * sol, 2 * sol, sol
    assert pa_ + pb_ + pc_ == 1
    for name, val, txt in (("A", pa_, "A"), ("B", pb_, "B"), ("C", pc_, "C")):
        it.append(pr(f"eq-8{name.lower()}", rf"Three drivers $A,B,C$ are in a race. $A$ is twice as likely to win as $B$, and $B$ is twice as likely to win as $C$. Find the probability that ${txt}$ wins.", val,
                     r"Let $P(C)=p$. Then $P(B)=2p$ and $P(A)=2P(B)=4p$. Exactly one of them wins, so $4p+2p+p=1$, $7p=1$, $p=\dfrac17$. Hence $P(C)=\dfrac17$, $P(B)=\dfrac27$, $P(A)=\dfrac47$.", ["Call the smallest probability $p$ and express the others with it."]))
    # more practice of the same kind (dice and cards), computed by enumeration
    s7 = sum(1 for d in itertools.product(range(1, 7), repeat=2) if sum(d) == 7)
    it.append(pr("eq-9", r"Two fair dice are thrown. Find the probability that the sum is $7$.", R(s7, 36), r"The sum $7$ is obtained by $(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)$: $6$ outcomes among $36$. $\dfrac6{36}=\dfrac16$.", ["List the favorable outcomes."]))
    two_aces = R(math.comb(4, 2), math.comb(52, 2))
    it.append(pr("eq-10", r"Two cards are drawn from a pack of $52$. Find the probability that both are aces.", two_aces, r"$\dfrac{\binom42}{\binom{52}2}=\dfrac{6}{1326}=\dfrac1{221}$.", ["Choose $2$ of the $4$ aces."]))
    h3 = R(math.comb(13, 3) * 1, math.comb(52, 3)) * 4
    it.append(pr("eq-11", r"Three cards are drawn from a pack of $52$. Find the probability that all three are of the same suit.", h3, r"Choose the suit ($4$ ways) and $3$ cards of that suit ($\dbinom{13}3=286$): $\dfrac{4\cdot286}{\binom{52}3}=\dfrac{1144}{22100}=\dfrac{22}{425}$.", ["Choose the suit first."]))
    # calculation-based multiple choice
    it.append(mc("eq-m1", r"Two cards are drawn from a pack of $52$. What is the probability that both are hearts?", [r"$\dfrac1{16}$", r"$\dfrac{1}{17}$", r"$\dfrac{3}{51}$", r"$\dfrac{13}{52}$"], 1,
                 r"$\dfrac{\binom{13}2}{\binom{52}2}$.", r"$\dfrac{\binom{13}2}{\binom{52}2}=\dfrac{78}{1326}=\dfrac1{17}$. (The product $\dfrac{13}{52}\cdot\dfrac{12}{51}=\dfrac{1}{17}$ gives the same value.)"))
    it.append(mc("eq-m2", r"A fair die is thrown three times. What is the probability that no $6$ appears?", [r"$\dfrac12$", r"$\dfrac{125}{216}$", r"$\dfrac{5}{18}$", r"$\dfrac{25}{36}$"], 1,
                 r"The throws are independent.", r"$\left(\dfrac56\right)^3=\dfrac{125}{216}$."))
    return it


# --- rules for events (sheet 9 to 33) ----------------------------------------------------------------------------------------------------
class Venn:
    """The four cells of two events from P(A), P(B), P(A and B); each cell must be a probability."""

    def __init__(self, pa: Fraction | int | str, pb: Fraction | int | str, pab: Fraction | int | str) -> None:
        pa, pb, pab = Fraction(pa), Fraction(pb), Fraction(pab)
        self.ab, self.a_nb, self.na_b, self.na_nb = pab, pa - pab, pb - pab, 1 - pa - pb + pab
        assert all(0 <= v <= 1 for v in (self.ab, self.a_nb, self.na_b, self.na_nb)), "inconsistent data"
        assert self.ab + self.a_nb + self.na_b + self.na_nb == 1
        self.pa, self.pb = pa, pb

    def union(self) -> Fraction:
        return 1 - self.na_nb


def fr(v: Fraction) -> sp.Rational:
    return sp.Rational(v.numerator, v.denominator)


def two_event_item(id_: str, header: str, venn: Venn, queries: list[tuple[str, str, Fraction, str]]) -> list[dict]:
    """queries: (suffix, text of the event, value, explanation)."""
    out = []
    for suffix, what, value, why in queries:
        out.append(pr(f"{id_}{suffix}", rf"{header} Find ${what}$.", fr(value), why, ["Draw the four cells: $A\\cap B$, $A$ only, $B$ only, neither."]))
    return out


def rules_items() -> list[dict]:
    it: list[dict] = []
    # 9) the student
    pm, pms, pu = Fraction(2, 3), Fraction(14, 45), Fraction(4, 5)
    ps = pu - pm + pms
    assert ps == Fraction(4, 9)
    it.append(pr("ru-9", r"The probability that a student passes a mathematics test is $\dfrac23$ and the probability that the student passes both mathematics and statistics is $\dfrac{14}{45}$. The probability that the student passes at least one of the tests is $\dfrac45$. What is the probability that the student passes the statistics test?", fr(ps),
                 r"Addition rule: $P(M\cup S)=P(M)+P(S)-P(M\cap S)$. So $P(S)=P(M\cup S)-P(M)+P(M\cap S)=\dfrac45-\dfrac23+\dfrac{14}{45}=\dfrac{36-30+14}{45}=\dfrac{20}{45}=\dfrac49$.", ["Solve the addition rule for $P(S)$."]))
    # 9b) independent events: P(A or B) = 1 - P(not A)P(not B)
    pa, pb = Fraction(2, 5), Fraction(1, 3)
    v = 1 - (1 - pa) * (1 - pb)
    assert v == pa + pb - pa * pb
    it.append(pr("ru-9b", r"$A$ and $B$ are independent events with $P(A)=\dfrac25$ and $P(B)=\dfrac13$. Find $P(A\cup B)$ using $P(A\cup B)=1-P(\bar A)P(\bar B)$.", fr(v),
                 r"$P(\bar A)=1-\dfrac25=\dfrac35$ and $P(\bar B)=1-\dfrac13=\dfrac23$. So $P(A\cup B)=1-\dfrac35\cdot\dfrac23=1-\dfrac25=\dfrac35$. **Why the formula holds:** $A\cup B$ fails exactly when neither happens, $P(\overline{A\cup B})=P(\bar A\cap\bar B)=P(\bar A)P(\bar B)$ because the complements of independent events are independent.", ["The complement of 'A or B' is 'neither A nor B'."]))
    # 10)
    v = Venn(Fraction(1, 3), Fraction(3, 4), Fraction(1, 3) + Fraction(3, 4) - Fraction(11, 12))
    assert v.ab == Fraction(1, 6)
    head = r"$P(A)=\dfrac13$, $P(B)=\dfrac34$, $P(A\cup B)=\dfrac{11}{12}$."
    it.append(pr("ru-10a", rf"{head} Find $P(A\mid B)$.", fr(v.ab / v.pb),
                 r"First $P(A\cap B)=P(A)+P(B)-P(A\cup B)=\dfrac13+\dfrac34-\dfrac{11}{12}=\dfrac{4+9-11}{12}=\dfrac16$. Then $P(A\mid B)=\dfrac{P(A\cap B)}{P(B)}=\dfrac{1/6}{3/4}=\dfrac29$.", ["Find $P(A\\cap B)$ first."]))
    it.append(pr("ru-10b", rf"{head} Find $P(B\mid A)$.", fr(v.ab / v.pa),
                 r"$P(A\cap B)=\dfrac16$ (addition rule). $P(B\mid A)=\dfrac{P(A\cap B)}{P(A)}=\dfrac{1/6}{1/3}=\dfrac12$.", ["Divide $P(A\\cap B)$ by $P(A)$."]))
    # 11) relation between p, q, r such that the complements are mutually exclusive
    p, q, r = sp.symbols("p q r", positive=True)
    relation = sp.simplify(p * r / (1 - p + p * r))
    check = sp.simplify(p + p * r / q - p * r - 1)
    assert sp.simplify(check.subs(q, relation)) == 0
    it.append(ex("ru-11", r"$P(A)=p$, $P(A\mid B)=q$ and $P(B\mid A)=r$. Find $q$ in terms of $p$ and $r$ so that $\bar A$ and $\bar B$ are mutually exclusive, that is $P(\bar A\cap\bar B)=0$.", "expression", "p*r/(1-p+p*r)", variables=["p", "r"],
                 hints=[r"$\bar A\cap\bar B=\overline{A\cup B}$, so $P(A\cup B)=1$.", r"$P(A\cap B)=P(A)P(B\mid A)=pr$ and $P(B)=\dfrac{P(A\cap B)}{P(A\mid B)}$."],
                 solution=r"$P(\bar A\cap\bar B)=0$ means $P(A\cup B)=1$. We know $P(A\cap B)=P(A)P(B\mid A)=pr$, and $P(A\cap B)=P(B)\,q$, so $P(B)=\dfrac{pr}q$. Addition rule: $p+\dfrac{pr}{q}-pr=1$. Solve for $q$: $\dfrac{pr}q=1-p+pr$, so $q=\dfrac{pr}{1-p+pr}$. Check with $p=\dfrac12$, $r=\dfrac13$: $q=\dfrac{1/6}{1/2+1/6}=\dfrac14$, and then $P(B)=\dfrac{1/6}{1/4}=\dfrac23$, $P(A\cup B)=\dfrac12+\dfrac23-\dfrac16=1$."))
    # 12)
    pa12, pab12, pu12 = Fraction(2, 5), Fraction(1, 5), Fraction(7, 10)
    pb12 = pu12 - pa12 + pab12
    assert pb12 == Fraction(1, 2) and pa12 * pb12 == pab12
    it.append(pr("ru-12", r"$P(A)=0.4$, $P(B)=p$, $P(A\cup B)=0.7$ and $P(A\cap B)=0.2$. Find $p$. (Then check that $A$ and $B$ are independent.)", fr(pb12),
                 r"Addition rule: $0.7=0.4+p-0.2$, so $p=0.5$. Independence needs $P(A\cap B)=P(A)P(B)$: $0.4\cdot0.5=0.2$, which is the given $P(A\cap B)$. So for $p=\dfrac12$ the events are independent.", ["Use the addition rule."]))
    # 13)
    pu13, pi13, pna2 = Fraction(5, 6), Fraction(1, 3), Fraction(1, 2)
    pa2 = 1 - pna2
    pa1 = pu13 - pa2 + pi13
    assert pa1 == Fraction(2, 3) and pa1 * pa2 == pi13
    it.append(pr("ru-13", r"$P(A_1\cup A_2)=\dfrac56$, $P(A_1\cap A_2)=\dfrac13$ and $P(\bar A_2)=\dfrac12$. Find $P(A_1)$.", fr(pa1),
                 r"$P(A_2)=1-P(\bar A_2)=\dfrac12$. Addition rule: $P(A_1)=P(A_1\cup A_2)-P(A_2)+P(A_1\cap A_2)=\dfrac56-\dfrac12+\dfrac13=\dfrac{5-3+2}{6}=\dfrac23$. Then $P(A_1)P(A_2)=\dfrac23\cdot\dfrac12=\dfrac13=P(A_1\cap A_2)$: the events are independent, as the sheet asks to show.", ["Find $P(A_2)$ first."]))
    it.append(mc("ru-13b", r"With $P(A_1)=\dfrac23$, $P(A_2)=\dfrac12$ and $P(A_1\cap A_2)=\dfrac13$, are $A_1$ and $A_2$ independent?", ["Yes, because $P(A_1)P(A_2)=P(A_1\\cap A_2)$", "No, because $P(A_1)+P(A_2)\\ne1$", "No, because $P(A_1\\cap A_2)\\ne0$", "Yes, because $P(A_1\\cap A_2)=P(A_1)+P(A_2)$"], 0,
                 r"Compare $P(A_1\cap A_2)$ with $P(A_1)P(A_2)$.", r"$\dfrac23\cdot\dfrac12=\dfrac13$ equals $P(A_1\cap A_2)=\dfrac13$, which is the definition of independence."))
    # 14) mutually exclusive: P(A | A u B) = P(A) / (P(A)+P(B))
    pa14, pb14 = Fraction(1, 5), Fraction(3, 10)
    v14 = pa14 / (pa14 + pb14)
    it.append(pr("ru-14", r"$A$ and $B$ are mutually exclusive with $P(A)=\dfrac15$ and $P(B)=\dfrac3{10}$. Find $P(A\mid A\cup B)$.", fr(v14),
                 r"$A\cap(A\cup B)=A$, so $P(A\mid A\cup B)=\dfrac{P(A)}{P(A\cup B)}$. Mutually exclusive events: $P(A\cup B)=P(A)+P(B)=\dfrac15+\dfrac3{10}=\dfrac12$. So $\dfrac{1/5}{1/2}=\dfrac25$. In general this is the formula $\dfrac{P(A)}{P(A)+P(B)}$ that the sheet asks to prove.", ["For mutually exclusive events $P(A\\cup B)=P(A)+P(B)$."]))
    # 15) three events
    pabc = Fraction(1, 4) * 3 - Fraction(1, 8)
    it.append(pr("ru-15", r"$P(A)=P(B)=P(C)=\dfrac14$, $P(A\cap B)=P(C\cap B)=0$ and $P(A\cap C)=\dfrac18$. Find $P(A\cup B\cup C)$.", fr(pabc),
                 r"Inclusion–exclusion for three events: $P(A\cup B\cup C)=P(A)+P(B)+P(C)-P(A\cap B)-P(B\cap C)-P(A\cap C)+P(A\cap B\cap C)$. Since $P(A\cap B)=0$, also $P(A\cap B\cap C)=0$. So $\dfrac34-0-0-\dfrac18+0=\dfrac58$.", ["Inclusion–exclusion; the triple intersection is inside $A\\cap B$."]))
    # 16) in terms of a, b, c
    it.append(ex("ru-16a", r"$P(X)=a$, $P(Y)=b$ and $P(X\cap Y)=c$. Express $P(\bar X\cup Y)$ in terms of $a$, $b$, $c$.", "expression", "1-a+c", variables=["a", "b", "c"],
                 hints=[r"The complement of $\bar X\cup Y$ is $X\cap\bar Y$."], solution=r"$\overline{\bar X\cup Y}=X\cap\bar Y$ (De Morgan), and $P(X\cap\bar Y)=P(X)-P(X\cap Y)=a-c$. So $P(\bar X\cup Y)=1-(a-c)=1-a+c$."))
    it.append(ex("ru-16b", r"$P(X)=a$, $P(Y)=b$ and $P(X\cap Y)=c$. Express $P(\bar X\cup\bar Y)$ in terms of $a$, $b$, $c$.", "expression", "1-c", variables=["a", "b", "c"],
                 hints=[r"De Morgan: $\bar X\cup\bar Y=\overline{X\cap Y}$."], solution=r"By De Morgan's law $\bar X\cup\bar Y=\overline{X\cap Y}$, so the probability is $1-P(X\cap Y)=1-c$."))
    it.append(ex("ru-16c", r"$P(X)=a$, $P(Y)=b$ and $P(X\cap Y)=c$. Express $P(X\cap\bar Y)$ in terms of $a$, $b$, $c$.", "expression", "a-c", variables=["a", "b", "c"],
                 hints=[r"$X$ is the union of $X\cap Y$ and $X\cap\bar Y$ (mutually exclusive)."], solution=r"$X=(X\cap Y)\cup(X\cap\bar Y)$ and the two parts are mutually exclusive, so $a=c+P(X\cap\bar Y)$ and $P(X\cap\bar Y)=a-c$."))
    # 17) equally likely, exclusive and exhaustive A, B; P(C|A) = 0.2, P(C|B) = 0.3
    pca, pcb = Fraction(1, 5), Fraction(3, 10)
    pc = Fraction(1, 2) * pca + Fraction(1, 2) * pcb
    it.append(pr("ru-17a", r"$A$ and $B$ are equally likely, mutually exclusive and exhaustive events, and $P(C\mid A)=0.2$, $P(C\mid B)=0.3$. Find $P(A\mid C)$.", fr(Fraction(1, 2) * pca / pc),
                 r"Equally likely, exclusive and exhaustive: $P(A)=P(B)=\dfrac12$. Total probability: $P(C)=\dfrac12\cdot\dfrac15+\dfrac12\cdot\dfrac3{10}=\dfrac1{10}+\dfrac3{20}=\dfrac14$. Bayes: $P(A\mid C)=\dfrac{P(A)P(C\mid A)}{P(C)}=\dfrac{1/10}{1/4}=\dfrac25$.", ["First find $P(A)$, $P(B)$ and $P(C)$."],
                 note="The sheet prints $p(A\\mid B)$ and $p(B\\mid A)$, which are $0$ because $A$ and $B$ are mutually exclusive. The intended questions, given the data on $C$, are $P(A\\mid C)$ and $P(B\\mid C)$."))
    it.append(pr("ru-17b", r"$A$ and $B$ are equally likely, mutually exclusive and exhaustive events, and $P(C\mid A)=0.2$, $P(C\mid B)=0.3$. Find $P(B\mid C)$.", fr(Fraction(1, 2) * pcb / pc),
                 r"As in the previous question $P(C)=\dfrac14$, so $P(B\mid C)=\dfrac{\frac12\cdot\frac3{10}}{\frac14}=\dfrac{3/20}{1/4}=\dfrac35$. Check: $P(A\mid C)+P(B\mid C)=\dfrac25+\dfrac35=1$.", ["The two answers add up to $1$."]))
    # 18) independent, P(A or B) = 0.6, P(A) = 0.4
    pb18 = (Fraction(3, 5) - Fraction(2, 5)) / (1 - Fraction(2, 5))
    it.append(pr("ru-18", r"$A$ and $B$ are independent. The probability that $A$ or $B$ occurs is $0.6$, and $P(A)=0.4$. Determine $P(B)$.", fr(pb18),
                 r"Independence: $P(A\cup B)=P(A)+P(B)-P(A)P(B)=P(A)+P(B)\,(1-P(A))$. So $0.6=0.4+0.6\,P(B)$, $P(B)=\dfrac{0.2}{0.6}=\dfrac13$.", ["$P(A\\cap B)=P(A)P(B)$."]))
    # 19) three books
    x_, y_, z_ = Fraction(20, 100), Fraction(16, 100), Fraction(14, 100)
    xy, xz, yz, xyz = Fraction(8, 100), Fraction(5, 100), Fraction(4, 100), Fraction(2, 100)
    union = x_ + y_ + z_ - xy - xz - yz + xyz
    only_x, only_y, only_z = x_ - xy - xz + xyz, y_ - xy - yz + xyz, z_ - xz - yz + xyz
    exactly_one = only_x + only_y + only_z
    assert union == Fraction(35, 100) and exactly_one == Fraction(22, 100)
    stem = r"A survey shows: $20\%$ read $X$, $16\%$ read $Y$, $14\%$ read $Z$, $8\%$ read $X$ and $Y$, $5\%$ read $X$ and $Z$, $4\%$ read $Y$ and $Z$, and $2\%$ read all three. A man is chosen at random. Find the probability that"
    expl = r"Inclusion–exclusion: $P(X\cup Y\cup Z)=0.20+0.16+0.14-0.08-0.05-0.04+0.02=0.35$."
    it.append(pr("ru-19a", rf"{stem} he reads none of the books.", fr(1 - union), rf"{expl} None of the books is the complement: $1-0.35=0.65=\dfrac{{13}}{{20}}$.", ["Find the probability of reading at least one first."]))
    it.append(pr("ru-19b", rf"{stem} he reads exactly one of the books.", fr(exactly_one),
                 r"Only $X$: $0.20-0.08-0.05+0.02=0.09$. Only $Y$: $0.16-0.08-0.04+0.02=0.06$. Only $Z$: $0.14-0.05-0.04+0.02=0.07$. Add: $0.09+0.06+0.07=0.22=\dfrac{11}{50}$. (Each 'only' removes the overlaps with the other books, but the triple overlap was subtracted twice, so it is added back once.)", ["Compute 'only $X$', 'only $Y$', 'only $Z$' and add."]))
    it.append(pr("ru-19c", rf"{stem} he reads at least one of the books.", fr(union), rf"{expl} So $0.35=\dfrac7{{20}}$.", ["Inclusion–exclusion for three events."]))

    # 26) P(A)=0.4, P(A u B)=0.7, P(B)=p
    pm26 = Fraction(7, 10) - Fraction(2, 5)
    it.append(pr("ru-26a", r"$P(A)=0.4$, $P(A\cup B)=0.7$ and $P(B)=p$. For what value of $p$ are $A$ and $B$ mutually exclusive?", fr(pm26),
                 r"Mutually exclusive: $P(A\cup B)=P(A)+P(B)$, so $0.7=0.4+p$ and $p=0.3=\dfrac3{10}$.", ["For mutually exclusive events the probabilities add."]))
    pi26 = (Fraction(7, 10) - Fraction(2, 5)) / (1 - Fraction(2, 5))
    it.append(pr("ru-26b", r"$P(A)=0.4$, $P(A\cup B)=0.7$ and $P(B)=p$. For what value of $p$ are $A$ and $B$ independent?", fr(pi26),
                 r"Independent: $P(A\cap B)=0.4p$, so $0.7=0.4+p-0.4p=0.4+0.6p$ and $p=\dfrac{0.3}{0.6}=\dfrac12$.", ["$P(A\\cap B)=P(A)P(B)$."]))
    # 27) P(A)=1/4, P(B)=2/5, P(A u B)=1/2
    v = Venn(Fraction(1, 4), Fraction(2, 5), Fraction(1, 4) + Fraction(2, 5) - Fraction(1, 2))
    assert v.ab == Fraction(3, 20)
    h = r"$P(A)=\dfrac14$, $P(B)=\dfrac25$, $P(A\cup B)=\dfrac12$."
    base27 = r"$P(A\cap B)=\dfrac14+\dfrac25-\dfrac12=\dfrac{5+8-10}{20}=\dfrac3{20}$."
    qs = [
        ("a", r"P(A\cap B)", v.ab, base27),
        ("b", r"P(A\mid B)", v.ab / v.pb, base27 + r" So $P(A\mid B)=\dfrac{3/20}{2/5}=\dfrac38$."),
        ("c", r"P(B\mid A)", v.ab / v.pa, base27 + r" So $P(B\mid A)=\dfrac{3/20}{1/4}=\dfrac35$."),
        ("d", r"P(A\cap\bar B)", v.a_nb, base27 + r" $A$ is split into $A\cap B$ and $A\cap\bar B$: $P(A\cap\bar B)=\dfrac14-\dfrac3{20}=\dfrac1{10}$."),
        ("e", r"P(A\cup\bar B)", 1 - v.na_b, base27 + r" The complement of $A\cup\bar B$ is $\bar A\cap B$ (De Morgan), $P(\bar A\cap B)=\dfrac25-\dfrac3{20}=\dfrac14$. So $P(A\cup\bar B)=1-\dfrac14=\dfrac34$."),
        ("f", r"P(\bar A\cap\bar B)", v.na_nb, r"$\bar A\cap\bar B$ is the complement of $A\cup B$: $1-\dfrac12=\dfrac12$."),
    ]
    it += two_event_item("ru-27", h, v, qs)
    # 28) P(A)=1/2, P(B)=3/5, P(A n B)=1/3
    v = Venn(Fraction(1, 2), Fraction(3, 5), Fraction(1, 3))
    h = r"$P(A)=\dfrac12$, $P(B)=\dfrac35$, $P(A\cap B)=\dfrac13$."
    qs = [
        ("a", r"P(A\cup B)", v.union(), r"$P(A\cup B)=\dfrac12+\dfrac35-\dfrac13=\dfrac{15+18-10}{30}=\dfrac{23}{30}$."),
        ("b", r"P(\bar A\cap\bar B)", v.na_nb, r"$\bar A\cap\bar B$ is the complement of $A\cup B$. $P(A\cup B)=\dfrac{23}{30}$, so $1-\dfrac{23}{30}=\dfrac7{30}$."),
        ("c", r"P(\bar A\cup\bar B)", 1 - v.ab, r"By De Morgan $\bar A\cup\bar B=\overline{A\cap B}$, so $P=1-\dfrac13=\dfrac23$."),
        ("d", r"P(A\cap\bar B)", v.a_nb, r"$P(A\cap\bar B)=P(A)-P(A\cap B)=\dfrac12-\dfrac13=\dfrac16$."),
    ]
    it += two_event_item("ru-28", h, v, qs)
    # 29) independent P(A)=2/3, P(B)=3/5
    v = Venn(Fraction(2, 3), Fraction(3, 5), Fraction(2, 3) * Fraction(3, 5))
    h = r"$A$ and $B$ are independent, $P(A)=\dfrac23$, $P(B)=\dfrac35$."
    qs = [
        ("a", r"P(A\cup B)", v.union(), r"$P(A\cap B)=\dfrac23\cdot\dfrac35=\dfrac25$ (independence). $P(A\cup B)=\dfrac23+\dfrac35-\dfrac25=\dfrac{10+9-6}{15}=\dfrac{13}{15}$."),
        ("b", r"P(\bar A\mid B)", v.na_b / v.pb, r"If $A$ and $B$ are independent so are $\bar A$ and $B$, therefore $P(\bar A\mid B)=P(\bar A)=1-\dfrac23=\dfrac13$."),
        ("c", r"P(\bar A\cap B)", v.na_b, r"$P(\bar A\cap B)=P(\bar A)P(B)=\dfrac13\cdot\dfrac35=\dfrac15$."),
        ("d", r"P(\bar A\cap\bar B)", v.na_nb, r"$P(\bar A\cap\bar B)=P(\bar A)P(\bar B)=\dfrac13\cdot\dfrac25=\dfrac2{15}$."),
        ("e", r"P(\bar A\cup\bar B)", 1 - v.ab, r"$\bar A\cup\bar B=\overline{A\cap B}$, so $P=1-\dfrac25=\dfrac35$."),
    ]
    it += two_event_item("ru-29", h, v, qs)
    # 30) P(A n notB) = 1/3, P(A u B) = 2/3
    pb30 = Fraction(2, 3) - Fraction(1, 3)
    it.append(pr("ru-30a", r"$P(A\cap\bar B)=\dfrac13$ and $P(A\cup B)=\dfrac23$. Find $P(B)$.", fr(pb30),
                 r"$A\cup B$ is made of $A\cap\bar B$ and $B$ (they do not overlap): $P(A\cup B)=P(A\cap\bar B)+P(B)$. So $P(B)=\dfrac23-\dfrac13=\dfrac13$.", ["Split $A\\cup B$ into $A\\cap\\bar B$ and $B$."]))
    pa30 = Fraction(1, 3) + Fraction(1, 6)
    it.append(pr("ru-30b", r"$P(A\cap\bar B)=\dfrac13$, $P(A\cup B)=\dfrac23$ and $P(A\cap B)=\dfrac16$. Find $P(A)$.", fr(pa30),
                 r"$A=(A\cap B)\cup(A\cap\bar B)$ with no overlap: $P(A)=\dfrac16+\dfrac13=\dfrac12$.", ["Split $A$ into $A\\cap B$ and $A\\cap\\bar B$."]))
    # 31) P(A)=1/2, P(B)=3/8, P(A n B)=1/4
    v = Venn(Fraction(1, 2), Fraction(3, 8), Fraction(1, 4))
    h = r"$P(A)=\dfrac12$, $P(B)=\dfrac38$, $P(A\cap B)=\dfrac14$."
    qs = [
        ("a", r"P(A\cup B)", v.union(), r"$\dfrac12+\dfrac38-\dfrac14=\dfrac{4+3-2}{8}=\dfrac58$."),
        ("b", r"P(\bar B)", 1 - v.pb, r"$1-\dfrac38=\dfrac58$."),
        ("c", r"P(\bar A\cap\bar B)", v.na_nb, r"The complement of $A\cup B$: $1-\dfrac58=\dfrac38$."),
        ("d", r"P(\bar A\cup\bar B)", 1 - v.ab, r"$\overline{A\cap B}$: $1-\dfrac14=\dfrac34$."),
        ("e", r"P(\bar A\cap B)", v.na_b, r"$P(B)-P(A\cap B)=\dfrac38-\dfrac14=\dfrac18$."),
        ("f", r"P(B\mid\bar A)", v.na_b / (1 - v.pa), r"$P(B\mid\bar A)=\dfrac{P(\bar A\cap B)}{P(\bar A)}=\dfrac{1/8}{1/2}=\dfrac14$."),
    ]
    it += two_event_item("ru-31", h, v, qs)
    # 32) P(A u B)=3/4, P(A)=1/2, P(notB)=5/8
    v = Venn(Fraction(1, 2), Fraction(3, 8), Fraction(1, 2) + Fraction(3, 8) - Fraction(3, 4))
    h = r"$P(A\cup B)=\dfrac34$, $P(A)=\dfrac12$, $P(\bar B)=\dfrac58$ (so $P(B)=\dfrac38$)."
    qs = [
        ("a", r"P(A\cap B)", v.ab, r"$P(A\cap B)=P(A)+P(B)-P(A\cup B)=\dfrac12+\dfrac38-\dfrac34=\dfrac18$."),
        ("b", r"P(\bar A\cup B)", 1 - v.a_nb, r"The complement of $\bar A\cup B$ is $A\cap\bar B$. $P(A\cap\bar B)=\dfrac12-\dfrac18=\dfrac38$, so $P(\bar A\cup B)=1-\dfrac38=\dfrac58$."),
        ("c", r"P(\bar A\mid B)", v.na_b / v.pb, r"$P(\bar A\cap B)=P(B)-P(A\cap B)=\dfrac38-\dfrac18=\dfrac14$. $P(\bar A\mid B)=\dfrac{1/4}{3/8}=\dfrac23$."),
        ("d", r"P(A\mid\bar B)", v.a_nb / (1 - v.pb), r"$P(A\cap\bar B)=\dfrac38$ (see above). $P(A\mid\bar B)=\dfrac{3/8}{5/8}=\dfrac35$."),
        ("e", r"P(\bar A\cap B)", v.na_b, r"$P(\bar A\cap B)=P(B)-P(A\cap B)=\dfrac38-\dfrac18=\dfrac14$."),
    ]
    it += two_event_item("ru-32", h, v, qs)
    # 33) P(A n B)=1/4, P(A u B)=3/4, P(B)=1/3
    pa33 = Fraction(3, 4) + Fraction(1, 4) - Fraction(1, 3)
    v = Venn(pa33, Fraction(1, 3), Fraction(1, 4))
    h = r"$P(A\cap B)=\dfrac14$, $P(A\cup B)=\dfrac34$, $P(B)=\dfrac13$ (so $P(A)=\dfrac34+\dfrac14-\dfrac13=\dfrac23$)."
    qs = [
        ("a", r"P(A\cup\bar B)", 1 - v.na_b, r"The complement of $A\cup\bar B$ is $\bar A\cap B$, with $P(\bar A\cap B)=\dfrac13-\dfrac14=\dfrac1{12}$. So $P(A\cup\bar B)=1-\dfrac1{12}=\dfrac{11}{12}$."),
        ("b", r"P(A\cap\bar B)", v.a_nb, r"$P(A)-P(A\cap B)=\dfrac23-\dfrac14=\dfrac5{12}$."),
        ("c", r"P(A\mid\bar B)", v.a_nb / (1 - v.pb), r"$P(A\mid\bar B)=\dfrac{P(A\cap\bar B)}{P(\bar B)}=\dfrac{5/12}{2/3}=\dfrac58$."),
    ]
    it += two_event_item("ru-33", h, v, qs)
    # a calculation-based multiple choice
    it.append(mc("ru-m1", r"$P(A)=0.5$, $P(B)=0.4$ and $P(A\cup B)=0.7$. Which statement is true?", [r"$A$ and $B$ are mutually exclusive", r"$A$ and $B$ are independent", r"$A$ and $B$ are neither mutually exclusive nor independent", r"$A\subset B$"], 1,
                r"Find $P(A\cap B)$ first.", r"$P(A\cap B)=0.5+0.4-0.7=0.2$. Mutually exclusive would need $P(A\cap B)=0$; here it is $0.2$. Independent needs $P(A\cap B)=P(A)P(B)=0.5\cdot0.4=0.2$, which is true. So $A$ and $B$ are independent. ($A\subset B$ is impossible because $P(A)>P(B)$.)"))
    return it


# --- Bayes, total probability (sheet 20 to 25) -----------------------------------------------------------------------------------------------
def bayes_items() -> list[dict]:
    it: list[dict] = []
    # 20) three groups
    pw = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)]
    tot = sum(Fraction(1, 3) * v for v in pw)
    assert tot == Fraction(1, 2)
    head = r"Three groups of people: $G_1$ has $3$ men and $1$ woman, $G_2$ has $2$ men and $2$ women, $G_3$ has $1$ man and $3$ women. A group is chosen at random, then a person from it. The person is a woman."
    for i, v in enumerate(pw, 1):
        post = Fraction(1, 3) * v / tot
        it.append(pr(f"ba-20-{i}", rf"{head} Find the probability that she comes from $G_{i}$.", fr(post),
                     rf"Each group has probability $\dfrac13$. $P(\text{{woman}})=\dfrac13\left(\dfrac14+\dfrac24+\dfrac34\right)=\dfrac13\cdot\dfrac32=\dfrac12$. Bayes: $P(G_{i}\mid\text{{woman}})=\dfrac{{\frac13\cdot P(\text{{woman}}\mid G_{i})}}{{1/2}}=\dfrac{{\frac13\cdot{T(v)}}}{{1/2}}={T(post)}$.",
                     ["First find $P(\\text{woman})$ by total probability."],
                     note="The sheet says 'a committee is selected and a person is chosen'; we read it as: one of the three groups is chosen at random, then a person of that group."))
    # 21) bolts
    sh, de = [Fraction(25, 100), Fraction(35, 100), Fraction(40, 100)], [Fraction(5, 100), Fraction(4, 100), Fraction(2, 100)]
    pd = sum(s * d for s, d in zip(sh, de, strict=True))
    assert pd == Fraction(345, 10000)
    for name, s, d in zip("ABC", sh, de, strict=True):
        post = s * d / pd
        it.append(pr(f"ba-21-{name.lower()}", rf"In a bolt factory, machines A, B, C make $25\%$, $35\%$ and $40\%$ of the total, and $5\%$, $4\%$ and $2\%$ of their output is defective. A bolt is drawn at random and is defective. Find the probability that it was made by machine {name}.", fr(post),
                     rf"$P(D)=0.25\cdot0.05+0.35\cdot0.04+0.40\cdot0.02=0.0125+0.014+0.008=0.0345$. Bayes: $P({name}\mid D)=\dfrac{{{float(s)}\cdot{float(d)}}}{{0.0345}}=\dfrac{{{float(s * d)}}}{{0.0345}}={T(post)}$. The three answers $\dfrac{{25}}{{69}},\dfrac{{28}}{{69}},\dfrac{{16}}{{69}}$ add up to $1$.", ["Total probability first, then divide the machine's share of defective bolts."]))
    # 22) urns
    pwr = [R(1 * 3, math.comb(6, 2)), R(2 * 1, math.comb(4, 2)), R(4 * 3, math.comb(12, 2))]
    assert pwr == [R(1, 5), R(1, 3), R(2, 11)]
    tot22 = sum(R(1, 3) * v for v in pwr)
    for i, v in enumerate(pwr, 1):
        post = R(1, 3) * v / tot22
        roman = ("I", "II", "III")[i - 1]
        it.append(pr(f"ba-22-{i}", r"Urn I has $1$ white, $2$ black and $3$ red balls; urn II has $2$ white, $1$ black and $1$ red; urn III has $4$ white, $5$ black and $3$ red. One urn is chosen at random and two balls are drawn. They are one white and one red. " + rf"Find the probability that they come from urn {roman}.", post,
                     rf"Probability of one white and one red in each urn: I: $\dfrac{{1\cdot3}}{{\binom62}}=\dfrac15$; II: $\dfrac{{2\cdot1}}{{\binom42}}=\dfrac13$; III: $\dfrac{{4\cdot3}}{{\binom{{12}}2}}=\dfrac2{{11}}$. Each urn has probability $\dfrac13$, so $P(WR)=\dfrac13\left(\dfrac15+\dfrac13+\dfrac2{{11}}\right)=\dfrac{{118}}{{495}}$. Bayes: $P(\text{{urn {roman}}}\mid WR)=\dfrac{{\frac13\cdot{T(v)}}}{{118/495}}={T(post)}$.",
                     ["Count the ways to draw one white and one red ball in each urn."]))
    # 23) factories
    pf = [R(1, 2), R(1, 4), R(1, 4)]
    pdf = [R(2, 100), R(2, 100), R(4, 100)]
    v = sum(a * b for a, b in zip(pf, pdf, strict=True))
    it.append(pr("ba-23", r"A certain item is made by three factories A, B, C. A makes twice as many items as B, and B and C make the same number. $2\%$ of the items of A and B are defective, and $4\%$ of those of C. One item is chosen at random from the stockpile. What is the probability that it is defective?", v,
                 r"Let C make a share $s$; then B makes $s$ and A makes $2s$, so $2s+s+s=1$ and $s=\dfrac14$: A makes $\dfrac12$, B $\dfrac14$, C $\dfrac14$. $P(D)=\dfrac12\cdot0.02+\dfrac14\cdot0.02+\dfrac14\cdot0.04=0.01+0.005+0.01=0.025=\dfrac1{40}$.", ["Find the share of each factory first."]))
    # 24) boys and girls
    v = R(2, 3) * R(28, 100) + R(1, 3) * R(25, 100)
    it.append(pr("ba-24", r"Two-thirds of the students in a class are boys and the rest are girls. The probability that a girl gets a first class is $0.25$ and that a boy gets one is $0.28$. Find the probability that a student chosen at random gets first class marks.", v,
                 r"Law of total probability over boy/girl: $P(F)=P(\text{boy})P(F\mid\text{boy})+P(\text{girl})P(F\mid\text{girl})=\dfrac23\cdot0.28+\dfrac13\cdot0.25=\dfrac{14}{75}+\dfrac1{12}=\dfrac{56+25}{300}=\dfrac{81}{300}=\dfrac{27}{100}$.", ["Split into boys and girls."]))
    # exam Q4b: P(girl | first class)
    post = R(1, 3) * R(25, 100) / v
    it.append(pr("ba-24b", r"In the same class (two-thirds boys; $P(\text{first class}\mid\text{girl})=0.25$, $P(\text{first class}\mid\text{boy})=0.28$), a student is chosen at random and is found to have first class marks. What is the probability that she is a girl?", post,
                 r"$P(\text{girl}\mid F)=\dfrac{P(\text{girl})P(F\mid\text{girl})}{P(F)}=\dfrac{\frac13\cdot\frac14}{27/100}=\dfrac{1/12}{27/100}=\dfrac{100}{324}=\dfrac{25}{81}$.", ["Use $P(F)=\\dfrac{27}{100}$ from the previous question."]))
    # 25) three groups of children, one from each, 1 girl and 2 boys
    g = [R(3, 4), R(2, 4), R(1, 4)]
    total = sum((g[i] * (1 - g[(i + 1) % 3]) * (1 - g[(i + 2) % 3])) for i in range(3))
    assert total == R(13, 32)
    it.append(pr("ba-25", r"Three groups of children have respectively $3$ girls and $1$ boy; $2$ girls and $2$ boys; $1$ girl and $3$ boys. One child is chosen at random from each group. Find the probability that the three chosen children are $1$ girl and $2$ boys.", total,
                 r"The girl can come from the first, the second or the third group; these cases are mutually exclusive. Girl from group 1 only: $\dfrac34\cdot\dfrac24\cdot\dfrac34=\dfrac{18}{64}$. From group 2 only: $\dfrac14\cdot\dfrac24\cdot\dfrac34=\dfrac6{64}$. From group 3 only: $\dfrac14\cdot\dfrac24\cdot\dfrac14=\dfrac2{64}$. Add: $\dfrac{26}{64}=\dfrac{13}{32}$.", ["Choose which group gives the girl; the draws are independent."]))
    return it


def register() -> None:
    from toolkit import add_extra

    add_extra(f"{M1}/u02-probability/l04-equally-likely-outcomes", exset("sheet-equally-likely", "Probability with equally likely outcomes (exercise sheet).", equally_likely_items(), format=FMT, source=SOURCE), SCRIPT, orphan=True)
    add_extra(f"{M1}/u02-probability/l05-rules-for-events", exset("sheet-rules", "Rules for events: union, complement, conditional probability, independence (exercise sheet).", rules_items(), format=FMT, source=SOURCE), SCRIPT, orphan=True)
    add_extra(f"{M1}/u02-probability/l03-total-probability-and-bayes", exset("sheet-bayes", "Total probability and Bayes (exercise sheet).", bayes_items(), format=FMT, source=SOURCE), SCRIPT)


def build() -> None:
    pass
