"""More practice for Course 3 (Probability and Statistics): counting, probability, random variables, data and regression.

Probabilities are computed exactly and cross-checked by enumerating the outcomes where that is possible."""

from __future__ import annotations

import itertools
from fractions import Fraction

import sympy as sp
from stat_course import C, F, R, fit, pr
from toolkit import add_extra, eng, ex, exset_plain, tex, x

SCRIPT = "more_stat.py"
M1 = "stat/m01-probability"
M2 = "stat/m02-random-variables"
M3 = "stat/m03-data-and-regression"
FMT = "Type a whole number, a fraction such as `7/19`, or an exact expression such as `exp(-5)` or `sqrt(7)/3`."
e = sp.E


def fr(p: Fraction) -> sp.Rational:
    return sp.Rational(p.numerator, p.denominator)


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


# --- counting ------------------------------------------------------------------------------------------------------------------------------
def counting_items() -> list[dict]:
    it = []
    v = C(8, 3) * C(6, 2)
    assert v == len(list(itertools.combinations(range(8), 3))) * len(list(itertools.combinations(range(6), 2)))
    it.append(pr("mp-co-1", r"A team of $3$ boys is chosen from $8$ and a team of $2$ girls from $6$. In how many ways can the two teams be chosen?", v, r"$\dbinom83\cdot\dbinom62=56\cdot15=840$.", ["Multiply the two independent choices."]))
    v = 26**3 * 10**4
    it.append(pr("mp-co-2", r"A code has $3$ letters (of $26$) followed by $4$ digits. How many codes are possible?", v, r"$26^3\cdot10^4=175\,760\,000$.", ["Multiplication principle: each position is chosen independently."]))
    v = 2**10
    assert v == len(list(itertools.product((0, 1), repeat=10)))
    it.append(pr("mp-co-3", r"How many subsets has a set of $10$ elements (including the empty set)?", v, r"Each element is in or out: $2^{10}=1024$.", ["Two choices for each element."]))
    v = F(6)
    it.append(pr("mp-co-4", r"In how many ways can $6$ different books be arranged on a shelf?", v, r"$6!=720$.", ["Arrangements of all the objects."]))
    v = C(9, 4) - C(5, 4)
    it.append(pr("mp-co-5", r"A committee of $4$ is chosen from $4$ doctors and $5$ nurses. In how many ways does it contain at least one doctor?", v, r"All committees: $\dbinom94=126$. With no doctor: $\dbinom54=5$. So $121$.", ["Count the complement: no doctor."]))
    return it


def binomial_theorem_items() -> list[dict]:
    it = []
    for n, (w, ms) in enumerate((("MISSISSIPPI", (4, 4, 2, 1)), ("BANANA", (3, 2, 1)), ("COMMITTEE", (2, 2, 2, 1, 1, 1))), 1):
        v = F(len(w)) / sp.prod([F(m) for m in ms])
        assert len(w) == sum(ms)
        it.append(pr(f"mp-bt-{n}", rf"The number of different arrangements of the letters of the word {w}.", v, rf"{len(w)} letters with multiplicities ${', '.join(map(str, ms))}$: $\dfrac{{{len(w)}!}}{{{'!'.join(map(str, ms))}!}}={v}$.", ["Divide by the factorial of each multiplicity."]))
    for n, (a, b, p, k) in enumerate(((2, 1, 6, 3), (1, -3, 5, 2), (3, 2, 4, 2)), 4):
        coeff = sp.Poly(sp.expand((a * x + b) ** p), x).coeff_monomial(x**k)
        it.append(pr(f"mp-bt-{n}", rf"The coefficient of $x^{k}$ in $({tex(a * x + b)})^{p}$.", coeff, rf"The coefficient is $\dbinom{p}{k}{a}^{k}({b})^{p - k}={coeff}$ (binomial theorem).", [r"$\dbinom nk(ax)^k b^{n-k}$."]))
    return it


# --- probability -----------------------------------------------------------------------------------------------------------------------------
def sample_space_items() -> list[dict]:
    it = []
    dice = list(itertools.product(range(1, 7), repeat=2))
    p = Fraction(sum(1 for a, b in dice if a + b == 7), 36)
    it.append(pr("mp-sa-1", r"Two fair dice are thrown. The probability that the sum is $7$.", fr(p), r"The outcomes $(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)$: $\dfrac6{36}=\dfrac16$.", ["List the favorable outcomes."]))
    p = Fraction(sum(1 for a, b in dice if a == b), 36)
    it.append(pr("mp-sa-2", r"Two fair dice are thrown. The probability that both show the same number.", fr(p), r"$6$ outcomes among $36$: $\dfrac16$.", ["Count the pairs $(k,k)$."]))
    p = Fraction(sum(1 for a, b in dice if max(a, b) <= 4), 36)
    it.append(pr("mp-sa-3", r"Two fair dice are thrown. The probability that both show at most $4$.", fr(p), r"$4\cdot4=16$ outcomes among $36$: $\dfrac49$.", ["Each die has $4$ favorable faces."]))
    p = Fraction(sum(1 for t in itertools.product((0, 1), repeat=5) if sum(t) == 2), 32)
    it.append(pr("mp-sa-4", r"A fair coin is tossed $5$ times. The probability of exactly $2$ heads.", fr(p), r"$\dfrac{\binom52}{2^5}=\dfrac{10}{32}=\dfrac5{16}$.", ["Choose the positions of the heads."]))
    p = Fraction(C(13, 2), C(52, 2))
    it.append(pr("mp-sa-5", r"Two cards are drawn together from a deck of $52$. The probability that both are hearts.", fr(p), r"$\dfrac{\binom{13}2}{\binom{52}2}=\dfrac{78}{1326}=\dfrac1{17}$.", ["Count pairs."]))
    it.append(pr("mp-sa-6", r"$P(A)=\dfrac12$, $P(B)=\dfrac25$ and $A$, $B$ are mutually exclusive. Find $P(A\cup B)$.", R(9, 10), r"For exclusive events $P(A\cup B)=\dfrac12+\dfrac25=\dfrac9{10}$.", ["Exclusive events: add."]))
    return it


def conditional_items() -> list[dict]:
    it = []
    p = R(5, 12) * R(4, 11)
    it.append(pr("mp-cn-1", r"A box has $5$ white and $7$ black balls. Two are drawn without replacement. The probability that both are white.", p, r"$\dfrac5{12}\cdot\dfrac4{11}=\dfrac{5}{33}$.", ["After one white ball, $4$ white remain among $11$."]))
    p = R(7, 12) * R(5, 11)
    it.append(pr("mp-cn-2", r"In the same box, the probability that the first ball is black and the second is white.", p, r"$\dfrac7{12}\cdot\dfrac5{11}=\dfrac{35}{132}$.", ["Multiplication rule."]))
    p = R(3, 20) / R(2, 5)
    it.append(pr("mp-cn-3", r"$P(A\cap B)=\dfrac3{20}$ and $P(B)=\dfrac25$. Find $P(A\mid B)$.", p, r"$\dfrac{3/20}{2/5}=\dfrac38$.", ["$P(A\\mid B)=\\dfrac{P(A\\cap B)}{P(B)}$."]))
    dice = list(itertools.product(range(1, 7), repeat=2))
    b = [d for d in dice if d[0] + d[1] >= 10]
    a = [d for d in b if d[0] == 6]
    p = Fraction(len(a), len(b))
    it.append(pr("mp-cn-4", r"Two dice are thrown and the sum is at least $10$. The probability that the first die shows $6$.", fr(p), r"The favorable pairs for the sum are $(4,6),(5,5),(6,4),(5,6),(6,5),(6,6)$; three have a first die equal to $6$: $\dfrac36=\dfrac12$.", ["Restrict to the outcomes with a sum of at least $10$."]))
    it.append(mc("mp-cn-5", r"$P(A)=\dfrac14$, $P(B)=\dfrac13$ and $P(A\cap B)=\dfrac1{12}$. Are $A$ and $B$ independent?", ["Yes", "No"], 0, r"Compare $P(A\cap B)$ with $P(A)P(B)$.", r"$\dfrac14\cdot\dfrac13=\dfrac1{12}=P(A\cap B)$: independent."))
    it.append(mc("mp-cn-6", r"$P(A)=\dfrac12$, $P(B)=\dfrac12$ and $P(A\cap B)=\dfrac3{10}$. Are $A$ and $B$ independent?", ["Yes", "No"], 1, r"Compare $P(A\cap B)$ with $P(A)P(B)$.", r"$\dfrac14\ne\dfrac3{10}$: not independent."))
    p = R(1, 2) * R(1, 2) * R(1, 2)
    it.append(pr("mp-cn-7", r"A fair coin is tossed three times. The probability of three heads.", p, r"The tosses are independent: $\left(\dfrac12\right)^3=\dfrac18$.", ["Independent events: multiply."]))
    p = 1 - R(5, 6) ** 2
    it.append(pr("mp-cn-8", r"A fair die is thrown twice. The probability of at least one six.", p, r"$1-\left(\dfrac56\right)^2=\dfrac{11}{36}$.", ["Use the complement: no six at all."]))
    return it


def bayes_items() -> list[dict]:
    it = []
    scenarios = [
        ("Two boxes: box 1 has $3$ red and $1$ blue ball, box 2 has $1$ red and $3$ blue. A box is chosen at random and a ball is drawn", [R(1, 2), R(1, 2)], [R(3, 4), R(1, 4)], "the ball is red", "it came from box 1", 1),
        ("A factory has three lines making $50\\%$, $30\\%$ and $20\\%$ of the items, with defect rates $2\\%$, $3\\%$ and $5\\%$. An item is picked", [R(1, 2), R(3, 10), R(1, 5)], [R(2, 100), R(3, 100), R(5, 100)], "the item is defective", "it comes from line 3", 3),
        ("In a town $1\\%$ of the people have a condition. A test is positive for $90\\%$ of the sick and for $5\\%$ of the healthy. A person is tested", [R(1, 100), R(99, 100)], [R(9, 10), R(5, 100)], "the test is positive", "the person is sick", 1),
        ("A student comes to class by bus ($40\\%$), by bike ($35\\%$) or on foot ($25\\%$), and is late with probability $10\\%$, $4\\%$ and $2\\%$", [R(2, 5), R(7, 20), R(1, 4)], [R(1, 10), R(4, 100), R(2, 100)], "the student is late", "the student came by bus", 1),
        ("A message is sent by two senders: sender 1 ($70\\%$ of the messages) writes spam with probability $\\dfrac1{10}$, sender 2 ($30\\%$) with probability $\\dfrac12$", [R(7, 10), R(3, 10)], [R(1, 10), R(1, 2)], "a message is spam", "it came from sender 2", 2),
    ]
    for n, (setup, priors, likes, event, given, idx) in enumerate(scenarios, 1):
        assert sum(priors) == 1
        total = sum(p * q for p, q in zip(priors, likes, strict=True))
        post = priors[idx - 1] * likes[idx - 1] / total
        # cross-check by counting in a population of 1,000,000
        pop = 1_000_000
        count_total = sum(int(p * pop) * q for p, q in zip(priors, likes, strict=True))
        count_i = int(priors[idx - 1] * pop) * likes[idx - 1]
        assert sp.Rational(count_i) / sp.Rational(count_total) == post
        terms = " + ".join(rf"{tex(p)}\cdot{tex(q)}" for p, q in zip(priors, likes, strict=True))
        it.append(pr(f"mp-ba-{n}a", rf"{setup}. The probability that {event}.", total, rf"Total probability: $P={terms}={tex(total)}$.", ["Add the cases: probability of the cause times probability of the event."]))
        it.append(pr(f"mp-ba-{n}b", rf"{setup}. Given that {event}, the probability that {given}.", post, rf"Bayes' theorem: $\dfrac{{{tex(priors[idx - 1])}\cdot{tex(likes[idx - 1])}}}{{{tex(total)}}}={tex(post)}$.", ["$P(\\text{cause}\\mid\\text{event})=\\dfrac{P(\\text{cause})P(\\text{event}\\mid\\text{cause})}{P(\\text{event})}$."]))
    return it


# --- random variables ----------------------------------------------------------------------------------------------------------------------
def pmf_items() -> list[dict]:
    it = []

    def table(pmf: dict) -> str:
        return ", ".join(rf"${k}$ with probability ${tex(p)}$" for k, p in pmf.items())

    def stats(pmf: dict):
        mean = sum(k * p for k, p in pmf.items())
        return mean, sum(k**2 * p for k, p in pmf.items()) - mean**2

    pm1 = {1: R(1, 5), 2: R(1, 5), 3: R(3, 10), 4: R(3, 10)}
    pm2 = {-1: R(1, 4), 0: R(1, 2), 2: R(1, 4)}
    for n, (pm, what) in enumerate(((pm1, 0), (pm1, 1), (pm2, 0), (pm2, 1)), 1):
        assert sum(pm.values()) == 1
        mean, var = stats(pm)
        label = "$E[X]$" if what == 0 else r"$\operatorname{Var}(X)$"
        val = mean if what == 0 else var
        it.append(pr(f"mp-ev-{n}", rf"$X$ takes the values {table(pm)}. Find {label}.", val, rf"$E[X]={tex(mean)}$ and $\operatorname{{Var}}(X)=E[X^2]-E[X]^2={tex(var)}$.", ["$E[X]=\\sum x_ip_i$ and $\\operatorname{Var}=E[X^2]-E[X]^2$."]))
    heads = sum(Fraction(k) * Fraction(C(6, k), 64) for k in range(7))
    it.append(pr("mp-ev-5", r"A fair coin is tossed $6$ times. The expected number of heads.", fr(heads), r"$E[X]=np=6\cdot\dfrac12=3$.", ["Linearity of the expectation."]))
    it.append(pr("mp-ev-6", r"$E[X]=2$ and $\operatorname{Var}(X)=3$. Find $\operatorname{Var}(3X+1)$.", 27, r"$\operatorname{Var}(3X+1)=3^2\cdot3=27$ (the constant does not change the variance).", ["$\\operatorname{Var}(aX+b)=a^2\\operatorname{Var}(X)$."]))
    return it


def distribution_items() -> list[dict]:
    it = []
    p = C(8, 3) * R(1, 4) ** 3 * R(3, 4) ** 5
    it.append(pr("mp-bg-1", r"$X\sim\mathrm B\left(8,\dfrac14\right)$. Find $P(X=3)$.", p, r"$\dbinom83\left(\dfrac14\right)^3\left(\dfrac34\right)^5=56\cdot\dfrac{243}{65536}=\dfrac{1701}{8192}$.", ["$\\dbinom nkp^k(1-p)^{n-k}$."]))
    it.append(pr("mp-bg-2", r"$X\sim\mathrm B\left(20,\dfrac15\right)$. Find $E[X]$.", 4, r"$np=4$.", ["$np$."]))
    it.append(pr("mp-bg-3", r"$X\sim\mathrm B\left(20,\dfrac15\right)$. Find $\operatorname{Var}(X)$.", R(16, 5), r"$np(1-p)=20\cdot\dfrac15\cdot\dfrac45=\dfrac{16}5$.", ["$npq$."]))
    it.append(pr("mp-bg-4", r"Trials succeed with probability $\dfrac13$. The probability that the first success is at trial $3$.", R(2, 3) ** 2 * R(1, 3), r"$\left(\dfrac23\right)^2\dfrac13=\dfrac4{27}$.", ["Two failures, then a success."]))
    it.append(pr("mp-bg-5", r"$X$ is Poisson with mean $3$. Find $P(X=0)$.", e**-3, r"$e^{-3}$.", ["$e^{-\\lambda}\\dfrac{\\lambda^k}{k!}$."], kind="expression"))
    it.append(pr("mp-bg-6", r"$X$ is Poisson with mean $2$. Find $P(X\le2)$.", 5 * e**-2, r"$e^{-2}\left(1+2+2\right)=5e^{-2}$.", ["Add the cases $0$, $1$ and $2$."], kind="expression"))
    return it


def density_items() -> list[dict]:
    it = []

    def dens(i: str, ftxt: str, f_expr: sp.Expr, lo, hi, probs) -> None:
        total = sp.integrate(f_expr, (x, lo, hi))
        assert sp.simplify(total - 1) == 0, (ftxt, total)
        mean = sp.simplify(sp.integrate(x * f_expr, (x, lo, hi)))
        var = sp.simplify(sp.integrate(x**2 * f_expr, (x, lo, hi)) - mean**2)
        pa, pb = probs
        pr_ = sp.simplify(sp.integrate(f_expr, (x, pa, pb)))
        it.append(pr(f"mp-dn-{i}a", rf"$X$ has the density $f(x)={ftxt}$ on $[{lo},{hi}]$ (and $0$ elsewhere). Find $E[X]$.", mean, rf"$E[X]=\int_{{{lo}}}^{{{hi}}}xf(x)\,dx={tex(mean)}$.", ["$\\int xf(x)\\,dx$."]))
        it.append(pr(f"mp-dn-{i}b", rf"$X$ has the density $f(x)={ftxt}$ on $[{lo},{hi}]$ (and $0$ elsewhere). Find $P({tex(pa)}<X<{tex(pb)})$.", pr_, rf"$\int_{{{tex(pa)}}}^{{{tex(pb)}}}f(x)\,dx={tex(pr_)}$.", ["Integrate the density between the two values."]))
        it.append(pr(f"mp-dn-{i}c", rf"$X$ has the density $f(x)={ftxt}$ on $[{lo},{hi}]$ (and $0$ elsewhere). Find $\operatorname{{Var}}(X)$.", var, rf"$E[X^2]-E[X]^2={tex(var)}$.", ["$E[X^2]-E[X]^2$."]))

    dens("1", r"\dfrac{3x^2}{8}", 3 * x**2 / 8, 0, 2, (sp.Integer(1), sp.Integer(2)))
    dens("2", r"2x", 2 * x, 0, 1, (sp.Rational(1, 2), sp.Integer(1)))
    dens("3", r"\dfrac{x}{2}", x / 2, 0, 2, (sp.Integer(1), sp.Integer(2)))
    return it


def continuous_items() -> list[dict]:
    it = []
    it.append(pr("mp-un-1", r"$X$ is uniform on $[2,10]$. Find $P(X>7)$.", R(3, 8), r"$\dfrac{10-7}{10-2}=\dfrac38$.", ["Ratio of lengths."]))
    it.append(pr("mp-un-2", r"$X$ is uniform on $[2,10]$. Find $E[X]$.", 6, r"The midpoint of the interval: $\dfrac{2+10}2=6$.", ["$\\dfrac{a+b}{2}$."]))
    it.append(pr("mp-un-3", r"$T$ is exponential with rate $\dfrac12$. Find $P(T>4)$.", e**-2, r"$e^{-\lambda t}=e^{-\frac12\cdot4}=e^{-2}$.", ["$e^{-\\lambda t}$."]))
    it.append(pr("mp-un-4", r"$T$ is exponential with rate $\dfrac12$. Find $E[T]$.", 2, r"$\dfrac1\lambda=2$.", ["Reciprocal of the rate."]))
    it.append(pr("mp-un-5", r"$X\sim\mathrm N(50,16)$. The standardized value of $x=58$.", 2, r"$\sigma=4$, so $z=\dfrac{58-50}4=2$.", ["$\\sigma=\\sqrt{16}$."]))
    it.append(pr("mp-un-6", r"$X\sim\mathrm N(50,16)$. Find the value $x$ whose standardized value is $z=-\dfrac32$.", 44, r"$x=\mu+z\sigma=50-\dfrac32\cdot4=44$.", ["$x=\\mu+z\\sigma$."]))
    it.append(pr("mp-un-7", r"A lamp lasts an exponential time with mean $100$ hours. The probability that it lasts more than $100$ hours.", e**-1, r"The rate is $\dfrac1{100}$, so $P(T>100)=e^{-1}$.", ["The rate is the reciprocal of the mean."]))
    return it


# --- data and regression ----------------------------------------------------------------------------------------------------------------------
def data_items() -> list[dict]:
    it = []
    data = [2, 3, 5, 8, 12]
    m = R(sum(data), len(data))
    s2 = sum((v - m) ** 2 for v in data) / (len(data) - 1)
    it.append(pr("mp-ds-1", r"The mean of $2,3,5,8,12$.", m, r"$\dfrac{30}{5}=6$.", ["Add and divide by the number of values."]))
    it.append(pr("mp-ds-2", r"The sample variance of $2,3,5,8,12$.", s2, rf"The sum of the squared deviations is ${tex(s2 * 4)}$; divided by $4$: ${tex(s2)}$.", ["Divide by $n-1$."]))
    data2 = [4, 7, 7, 9, 10, 13]
    med = R(7 + 9, 2)
    it.append(pr("mp-ds-3", r"The median of $4,7,7,9,10,13$.", med, r"With six values the median is the average of the third and the fourth: $\dfrac{7+9}2=8$.", ["Average the two middle values."]))
    it.append(pr("mp-ds-4", r"The mode of $4,7,7,9,10,13$.", 7, r"The value $7$ appears twice, more than any other.", ["The most frequent value."]))
    assert sorted(data2)[2:4] == [7, 9]
    return it


def regression_items() -> list[dict]:
    it = []
    pts = ((1, 1), (2, 3), (3, 4), (4, 6))
    xb, yb, sxx, sxy, syy, m, q = fit(pts)
    txt = ", ".join(f"({a},{b})" for a, b in pts)
    it.append(pr("mp-lr-1", rf"The slope $m$ of the least-squares line through ${txt}$.", m, rf"$\bar x={tex(xb)}$, $\bar y={tex(yb)}$, $S_{{xx}}={tex(sxx)}$, $S_{{xy}}={tex(sxy)}$, so $m={tex(m)}$.", ["$m=\\dfrac{S_{xy}}{S_{xx}}$."]))
    it.append(pr("mp-lr-2", rf"The intercept $q$ of the least-squares line through ${txt}$.", q, rf"$q=\bar y-m\bar x={tex(q)}$.", ["$q=\\bar y-m\\bar x$."]))
    it.append(pr("mp-lr-3", rf"The least-squares line through ${txt}$ predicts which value at $x=5$?", m * 5 + q, rf"$y={tex(m)}x+\left({tex(q)}\right)$, so $y(5)={tex(m * 5 + q)}$.", ["Use $y=mx+q$."]))
    it.append(pr("mp-lr-4", rf"The correlation coefficient of ${txt}$ (a simplified expression).", sxy / sp.sqrt(sxx * syy), rf"$r=\dfrac{{S_{{xy}}}}{{\sqrt{{S_{{xx}}S_{{yy}}}}}}={tex(sp.simplify(sxy / sp.sqrt(sxx * syy)))}$.", ["$r=\\dfrac{S_{xy}}{\\sqrt{S_{xx}S_{yy}}}$."], kind="expression"))
    return it


def register() -> None:
    sets = [
        (M1, "u01-counting/l01-counting-principles", "more-counting", "More practice: counting.", counting_items()),
        (M1, "u01-counting/l02-repetitions-and-the-binomial-theorem", "more-binomial-theorem", "More practice: repetitions and the binomial theorem.", binomial_theorem_items()),
        (M1, "u02-probability/l01-sample-spaces-and-axioms", "more-sample-spaces", "More practice: probabilities of events.", sample_space_items()),
        (M1, "u02-probability/l02-conditional-probability-and-independence", "more-conditional", "More practice: conditional probability.", conditional_items()),
        (M1, "u02-probability/l03-total-probability-and-bayes", "more-bayes", "More practice: total probability and Bayes.", bayes_items()),
        (M2, "u01-discrete/l01-expectation-and-variance", "more-expectation", "More practice: expectation and variance.", pmf_items()),
        (M2, "u01-discrete/l02-binomial-geometric-poisson", "more-distributions", "More practice: binomial, geometric and Poisson.", distribution_items()),
        (M2, "u02-continuous/l01-density-and-distribution-function", "more-densities", "More practice: densities.", density_items()),
        (M2, "u02-continuous/l02-uniform-exponential-normal", "more-continuous", "More practice: uniform, exponential and normal.", continuous_items()),
        (M3, "u01-data/l01-describing-data", "more-data", "More practice: describing data.", data_items()),
        (M3, "u01-data/l02-least-squares-line", "more-regression", "More practice: least squares.", regression_items()),
    ]
    for base, lesson, sid, task, items in sets:
        add_extra(f"{base}/{lesson}", exset_plain(sid, task, items, format=FMT), SCRIPT)
    assert eng is not None
