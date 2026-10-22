"""Exercises of Course 3 (stat): counting, probability, random variables, data and regression."""

from __future__ import annotations

import re

import sympy as sp
from toolkit import eng, ex, exset, tex, write_exercises

R = sp.Rational
C = sp.binomial
F = sp.factorial
e = sp.E
FMT = "Type a whole number, a fraction such as `3/11`, or an exact expression such as `exp(-3)` or `sqrt(5)/3`."
M1 = "stat/m01-probability"
M2 = "stat/m02-random-variables"
M3 = "stat/m03-data-and-regression"


def pr(id_: str, statement: str, answer, solution: str, hints: list[str], kind: str | None = None, **kw) -> dict:
    a = sp.nsimplify(answer) if not isinstance(answer, sp.Basic) else answer
    kind = kind or ("number" if a.is_Integer else "expression")
    return ex(id_, statement, kind, eng(a), hints=hints, solution=solution, **kw)


def l01_1() -> list[dict]:
    it = []
    for n, (a, b) in enumerate(((9, 3), (12, 5), (7, 2), (10, 5)), 1):
        v = C(a, b)
        it.append(pr(f"cp-{n:02d}", rf"The number of ways to choose ${b}$ objects from ${a}$ different objects, without regard to order.", v,
                     rf"$\dbinom{{{a}}}{{{b}}}={v}$.", ["The order does not matter."]))
    for n, (a, b) in enumerate(((7, 4), (10, 2)), 5):
        v = F(a) / F(a - b)
        it.append(pr(f"cp-{n:02d}", rf"The number of ways to choose and line up ${b}$ of ${a}$ different people (the order matters).", v,
                     rf"$A({a},{b})=\dfrac{{{a}!}}{{{a-b}!}}={v}$.", ["Arrangements: $\\dfrac{n!}{(n-k)!}$."]))
    it.append(pr("cp-07", r"A committee of $3$ is chosen from $4$ women and $6$ men. In how many ways does it contain at least one woman?", C(10, 3) - C(6, 3),
                 r"All committees: $\dbinom{10}3=120$. Without any woman: $\dbinom63=20$. So $120-20=100$.", ["Count the complement: no woman."]))
    it.append(pr("cp-08", r"In how many ways can $5$ people sit in a row if two of them insist on sitting next to each other?", 48,
                 r"Treat the pair as one block: $4!$ arrangements of $4$ units, and $2!$ orders inside the block: $24\cdot2=48$.", ["Glue the two people together."]))
    it.append(pr("cp-09", r"How many $3$-digit numbers have three different digits?", 648, r"$9\cdot9\cdot8=648$: the first digit cannot be $0$.", ["The first digit has $9$ choices."]))
    it.append(pr("cp-10", r"At a meeting of $12$ people everybody shakes hands with everybody else once. How many handshakes?", C(12, 2),
                 r"Each handshake is a pair of people: $\dbinom{12}2=66$.", ["A handshake is an unordered pair."]))
    return it


def l01_2() -> list[dict]:
    it = []
    for n, (w, ms) in enumerate((("STATISTICS", (3, 3, 2, 1, 1)), ("LETTER", (2, 2, 1, 1)), ("ALGEBRA", (2, 1, 1, 1, 1, 1))), 1):
        v = F(len(w)) / sp.prod([F(m) for m in ms])
        mult = ", ".join(str(m) for m in ms)
        it.append(pr(f"rb-{n:02d}", rf"The number of different arrangements of the letters of the word {w}.", v,
                     rf"{len(w)} letters with multiplicities ${mult}$: $\dfrac{{{len(w)}!}}{{{'!'.join(str(m) for m in ms)}!}}={v}$.", ["Divide by the factorial of each multiplicity."]))
    it.append(pr("rb-04", r"The number of binary strings of length $8$ with exactly three ones.", C(8, 3), r"Choose the positions of the ones: $\dbinom83=56$.", ["Choose the positions."]))
    x = sp.Symbol("x")
    for n, (expr, k) in enumerate(((x + 2, 2), (3 * x - 1, 3), (1 + x, 4)), 5):
        pw = {5: 5, 6: 5, 7: 7}[n]
        coeff = sp.Poly(sp.expand(expr**pw), x).coeff_monomial(x**k)
        it.append(pr(f"rb-{n:02d}", rf"The coefficient of $x^{k}$ in $({tex(expr)})^{pw}$.", coeff, rf"The coefficient is ${coeff}$ (binomial theorem).", ["$\\dbinom nk a^{n-k}b^k$."]))
    it.append(pr("rb-08", r"The sum of the coefficients of $(2x-1)^6$.", 1, r"Put $x=1$: $(2-1)^6=1$.", ["Put $x=1$."]))
    it.append(pr("rb-09", r"The value of $\dbinom{10}0+\dbinom{10}1+\cdots+\dbinom{10}{10}$.", 1024, r"The sum is $2^{10}=1024$.", ["Binomial theorem with $a=b=1$."]))
    return it


def l02_1() -> list[dict]:
    it = []
    it.append(pr("sa-01", r"Two fair dice are thrown. The probability that the sum is $9$.", R(4, 36), r"The outcomes $(3,6),(4,5),(5,4),(6,3)$: $\dfrac4{36}=\dfrac19$.", ["List the favorable outcomes."]))
    it.append(pr("sa-02", r"Two fair dice are thrown. The probability that both show an even number.", R(1, 4), r"$3\cdot3=9$ outcomes among $36$: $\dfrac14$.", ["Each die has $3$ even faces."]))
    it.append(pr("sa-03", r"Two fair dice are thrown. The probability that the sum is at least $10$.", R(6, 36), r"Sum $10$: $3$ outcomes; $11$: $2$; $12$: $1$. Total $6$ among $36$: $\dfrac16$.", ["Count the sums $10$, $11$, $12$."]))
    it.append(pr("sa-04", r"Three fair dice are thrown. The probability that no six appears.", R(125, 216), r"$\left(\dfrac56\right)^3=\dfrac{125}{216}$.", ["Independent dice."]))
    it.append(pr("sa-05", r"Four fair coins are tossed. The probability of at least one head.", R(15, 16), r"$1-\dfrac1{16}=\dfrac{15}{16}$.", ["Use the complement."]))
    it.append(pr("sa-06", r"$P(A)=\dfrac13$, $P(B)=\dfrac14$ and $P(A\cap B)=\dfrac1{12}$. Find $P(A\cup B)$.", R(1, 2), r"$\dfrac13+\dfrac14-\dfrac1{12}=\dfrac{4+3-1}{12}=\dfrac12$.", ["Addition rule."]))
    it.append(pr("sa-07", r"A card is drawn from a deck of $52$. The probability that it is red or an ace.", R(28, 52), r"$\dfrac{26+4-2}{52}=\dfrac{28}{52}=\dfrac7{13}$.", ["The two red aces are counted twice."]))
    it.append(pr("sa-08", r"A bag has $5$ red and $3$ blue balls. Two are drawn together. The probability that both are red.", R(10, 28), r"$\dfrac{\binom52}{\binom82}=\dfrac{10}{28}=\dfrac5{14}$.", ["Count pairs."]))
    it.append(pr("sa-09", r"In the same bag, the probability that exactly one of the two balls is red.", R(15, 28), r"$\dfrac{5\cdot3}{\binom82}=\dfrac{15}{28}$.", ["One red and one blue."]))
    return it


def l02_2() -> list[dict]:
    it = []
    it.append(pr("cn-01", r"Three cards are drawn without replacement from a deck of $52$. The probability that all three are aces.", R(4, 52) * R(3, 51) * R(2, 50),
                 r"$\dfrac4{52}\cdot\dfrac3{51}\cdot\dfrac2{50}=\dfrac1{5525}$.", ["Multiplication rule for three events."]))
    it.append(pr("cn-02", r"An urn has $4$ red and $6$ blue balls. Two are drawn without replacement. The probability that both are red.", R(4, 10) * R(3, 9),
                 r"$\dfrac4{10}\cdot\dfrac39=\dfrac2{15}$.", ["After one red ball, $3$ red remain among $9$."]))
    it.append(pr("cn-03", r"$P(A\cap B)=\dfrac1{10}$ and $P(B)=\dfrac14$. Find $P(A\mid B)$.", R(2, 5), r"$\dfrac{1/10}{1/4}=\dfrac25$.", ["Definition of conditional probability."]))
    it.append(pr("cn-04", r"A fair die shows an even number. The probability that it is at least $4$.", R(2, 3), r"The even results are $2,4,6$; two of them are at least $4$.", ["Restrict to the even results."]))
    it.append(pr("cn-05", r"Two dice are thrown and the first shows $3$. The probability that the sum is $8$.", R(1, 6), r"The second die must show $5$: probability $\dfrac16$.", ["Only the second die is still random."]))
    it.append(ex("cn-06", r"Events $A$, $B$ have $P(A)=\dfrac12$, $P(B)=\dfrac13$, $P(A\cap B)=\dfrac16$. Are they independent?", "multiple_choice", "1",
                 choices=[{"text": "Yes", "value": "1"}, {"text": "No", "value": "2"}], correctIndex=0, hints=["Compare $P(A\\cap B)$ with $P(A)P(B)$."], solution=r"$\dfrac12\cdot\dfrac13=\dfrac16=P(A\cap B)$: independent."))
    it.append(ex("cn-07", r"Events $A$, $B$ have $P(A)=\dfrac12$, $P(B)=\dfrac12$, $P(A\cap B)=\dfrac15$. Are they independent?", "multiple_choice", "2",
                 choices=[{"text": "Yes", "value": "1"}, {"text": "No", "value": "2"}], correctIndex=1, hints=["Compare $P(A\\cap B)$ with $P(A)P(B)$."], solution=r"$P(A)P(B)=\dfrac14\ne\dfrac15$: not independent."))
    return it


def l02_3() -> list[dict]:
    it = []
    it.append(pr("ba-01", r"Urn A has $2$ red and $3$ blue balls; urn B has $4$ red and $1$ blue. An urn is chosen at random and a ball is drawn. The probability that it is red.", R(1, 2) * R(2, 5) + R(1, 2) * R(4, 5),
                 r"$\dfrac12\cdot\dfrac25+\dfrac12\cdot\dfrac45=\dfrac35$.", ["Total probability."]))
    it.append(pr("ba-02", r"In the same experiment, the ball is red. The probability that it came from urn B.", R(2, 3), r"$\dfrac{\frac12\cdot\frac45}{\frac35}=\dfrac{2/5}{3/5}=\dfrac23$.", ["Bayes' theorem."]))
    d = R(1, 2) * R(1, 10) + R(1, 3) * R(1, 20) + R(1, 6) * R(1, 5)
    it.append(pr("ba-03", r"Machines $M_1$, $M_2$, $M_3$ make $\dfrac12$, $\dfrac13$, $\dfrac16$ of the items, with defect rates $\dfrac1{10}$, $\dfrac1{20}$, $\dfrac15$. The probability that an item is defective.", d,
                 r"$\dfrac1{20}+\dfrac1{60}+\dfrac1{30}=\dfrac{3+1+2}{60}=\dfrac1{10}$.", ["Add the three cases."]))
    it.append(pr("ba-04", r"In the same factory, a defective item is found. The probability that it was made by $M_3$.", (R(1, 6) * R(1, 5)) / d, r"$\dfrac{1/30}{1/10}=\dfrac13$.", ["Bayes' theorem."]))
    pos = R(1, 50) * R(4, 5) + R(49, 50) * R(1, 10)
    it.append(pr("ba-05", r"One person in $50$ has a disease; a test is positive for $\dfrac45$ of the sick and for $\dfrac1{10}$ of the healthy. The probability that a person with a positive test is sick.",
                 (R(1, 50) * R(4, 5)) / pos, r"$P(+)=\dfrac{8}{500}+\dfrac{49}{500}=\dfrac{57}{500}$ and $P(\text{sick}\mid+)=\dfrac{8}{57}$.", ["Compute $P(+)$ first."]))
    return it


def pmf_item(id_: str, pmf: dict, what: str) -> dict:
    mean = sum(k * p for k, p in pmf.items())
    var = sum(k**2 * p for k, p in pmf.items()) - mean**2
    table = ", ".join(rf"${tex(sp.Integer(k))}$ with probability ${tex(p)}$" for k, p in pmf.items())
    assert sum(pmf.values()) == 1
    if what == "mean":
        return pr(id_, rf"$X$ takes the values {table}. Find $E[X]$.", mean, rf"$E[X]=\sum x_ip(x_i)={tex(mean)}$.", ["Weighted average of the values."])
    return pr(id_, rf"$X$ takes the values {table}. Find $\operatorname{{Var}}(X)$.", var, rf"$E[X]={tex(mean)}$ and $\operatorname{{Var}}(X)=E[X^2]-E[X]^2={tex(var)}$.", ["$E[X^2]-E[X]^2$."])


def l03_1() -> list[dict]:
    it = []
    it.append(pmf_item("ev-01", {0: R(1, 2), 1: R(1, 4), 4: R(1, 4)}, "mean"))
    it.append(pmf_item("ev-02", {0: R(1, 8), 1: R(3, 8), 2: R(3, 8), 3: R(1, 8)}, "mean"))
    it.append(pmf_item("ev-03", {0: R(1, 8), 1: R(3, 8), 2: R(3, 8), 3: R(1, 8)}, "var"))
    it.append(pmf_item("ev-04", {1: R(1, 2), 2: R(1, 3), 6: R(1, 6)}, "var"))
    it.append(pr("ev-05", r"In a game you win $5$ with probability $\dfrac16$ and lose $1$ otherwise. The expected gain.", R(5, 6) - R(5, 6), r"$5\cdot\dfrac16-1\cdot\dfrac56=0$: a fair game.", ["Weighted average of the gains."]))
    it.append(pr("ev-06", r"$E[X]=3$ and $\operatorname{Var}(X)=2$. Find $\operatorname{Var}(5-4X)$.", 32, r"$(-4)^2\cdot2=32$.", ["$\\operatorname{Var}(aX+b)=a^2\\operatorname{Var}(X)$."]))
    it.append(pr("ev-07", r"$E[X]=3$. Find $E[5-4X]$.", -7, r"$5-12=-7$.", ["Linearity."]))
    it.append(pr("ev-08", r"The expected value of the sum of two fair dice.", 7, r"$\dfrac72+\dfrac72=7$.", ["$E[X+Y]=E[X]+E[Y]$."]))
    it.append(pr("ev-09", r"The variance of the sum of two independent fair dice.", R(35, 6), r"$\dfrac{35}{12}+\dfrac{35}{12}=\dfrac{35}{6}$.", ["For independent variables, variances add."]))
    return it


def l03_2() -> list[dict]:
    it = []
    p = sp.Rational
    it.append(pr("bg-01", r"$X\sim\mathrm B\left(6,\dfrac12\right)$. Find $P(X=3)$.", C(6, 3) * p(1, 2) ** 6, r"$\dbinom63\left(\dfrac12\right)^6=\dfrac{20}{64}=\dfrac5{16}$.", ["$\\dbinom nkp^k(1-p)^{n-k}$."]))
    it.append(pr("bg-02", r"$X\sim\mathrm B\left(4,\dfrac13\right)$. Find $P(X=2)$.", C(4, 2) * p(1, 3) ** 2 * p(2, 3) ** 2, r"$6\cdot\dfrac19\cdot\dfrac49=\dfrac{24}{81}=\dfrac8{27}$.", ["$q=\\dfrac23$."]))
    it.append(pr("bg-03", r"$X\sim\mathrm B\left(10,\dfrac12\right)$. Find $P(X\ge9)$.", (C(10, 9) + C(10, 10)) * p(1, 2) ** 10, r"$\dfrac{10+1}{1024}=\dfrac{11}{1024}$.", ["Add $P(X=9)$ and $P(X=10)$."]))
    it.append(pr("bg-04", r"$X\sim\mathrm B\left(12,\dfrac14\right)$. Find $E[X]$.", 3, r"$np=3$.", ["$np$."]))
    it.append(pr("bg-05", r"A fair coin is tossed until a head appears. The probability that this takes exactly $4$ tosses.", p(1, 16), r"$\left(\dfrac12\right)^3\dfrac12=\dfrac1{16}$.", ["Geometric distribution."]))
    it.append(pr("bg-06", r"Trials succeed with probability $\dfrac15$. The expected number of trials up to the first success.", 5, r"$\dfrac1p=5$.", ["$\\dfrac1p$."]))
    lam = sp.Symbol("l")
    it.append(pr("bg-07", r"$X$ is Poisson with mean $1$. Find $P(X=0)$.", e ** -1, r"$e^{-1}$.", ["$e^{-\\lambda}\\dfrac{\\lambda^k}{k!}$."], kind="expression"))
    it.append(pr("bg-08", r"$X$ is Poisson with mean $4$. Find $P(X\le1)$.", 5 * e ** -4, r"$e^{-4}(1+4)=5e^{-4}$.", ["Add the cases $0$ and $1$."], kind="expression"))
    it.append(pr("bg-09", r"$X$ is Poisson with mean $2$. Find $P(X=3)$.", 4 * e**-2 / 3, r"$e^{-2}\dfrac{8}{6}=\dfrac43e^{-2}$.", ["$\\dfrac{2^3}{3!}$."], kind="expression"))
    return it


def l04_1() -> list[dict]:
    x = sp.Symbol("x")
    it = []
    c = R(1, 9)
    it.append(pr("dn-01", r"Find $c$ so that $f(x)=c\,x^2$ on $[0,3]$ (and $0$ elsewhere) is a density.", c, r"$\int_0^3cx^2dx=9c=1$, so $c=\dfrac19$.", ["The total area is $1$."]))
    it.append(pr("dn-02", r"$f(x)=\dfrac{x^2}{9}$ on $[0,3]$. Find $P(X>1)$.", 1 - R(1, 27), r"$1-\int_0^1\dfrac{x^2}9dx=1-\dfrac1{27}=\dfrac{26}{27}$.", ["Use the complement."]))
    it.append(pr("dn-03", r"$f(x)=\dfrac{x^2}{9}$ on $[0,3]$. Find $E[X]$.", sp.integrate(x * x**2 / 9, (x, 0, 3)), r"$\int_0^3\dfrac{x^3}{9}dx=\dfrac94$.", ["$\\int xf(x)\\,dx$."]))
    it.append(pr("dn-04", r"$f(x)=6x(1-x)$ on $[0,1]$. Find $E[X]$.", R(1, 2), r"$\int_0^16x^2(1-x)dx=6\left(\dfrac13-\dfrac14\right)=\dfrac12$.", ["The density is symmetric about $\\dfrac12$."]))
    it.append(pr("dn-05", r"$f(x)=6x(1-x)$ on $[0,1]$. Find $\operatorname{Var}(X)$.", R(1, 20), r"$E[X^2]=6\left(\dfrac14-\dfrac15\right)=\dfrac3{10}$ and $\operatorname{Var}=\dfrac3{10}-\dfrac14=\dfrac1{20}$.", ["$E[X^2]-E[X]^2$."]))
    it.append(pr("dn-06", r"$f(x)=\dfrac{x^2}{9}$ on $[0,3]$. The distribution function $F(2)$.", R(8, 27), r"$F(2)=\int_0^2\dfrac{x^2}9dx=\dfrac{8}{27}$.", ["Integrate from $0$ to $2$."]))
    return it


def l04_2() -> list[dict]:
    it = []
    it.append(pr("un-01", r"$X$ is uniform on $[3,9]$. Find $P(X<5)$.", R(1, 3), r"$\dfrac{5-3}{9-3}=\dfrac13$.", ["Ratio of lengths."]))
    it.append(pr("un-02", r"$X$ is uniform on $[3,9]$. Find $\operatorname{Var}(X)$.", 3, r"$\dfrac{(9-3)^2}{12}=3$.", ["$\\dfrac{(b-a)^2}{12}$."]))
    it.append(pr("un-03", r"$T$ is exponential with rate $2$. Find $P(T>1)$.", e**-2, r"$e^{-2}$.", ["$e^{-\\lambda t}$."]))
    it.append(pr("un-04", r"$T$ is exponential with rate $2$. Find $E[T]$.", R(1, 2), r"$\dfrac1\lambda=\dfrac12$.", ["Reciprocal of the rate."]))
    it.append(pr("un-05", r"$T$ is exponential with rate $2$. Find $P(1<T<2)$.", e**-2 - e**-4, r"$e^{-2}-e^{-4}$.", ["$P(T>1)-P(T>2)$."]))
    it.append(pr("un-06", r"$X\sim\mathrm N(100,25)$. The standardized value of $x=110$.", 2, r"$\sigma=5$ and $z=\dfrac{110-100}{5}=2$.", ["$\\sigma=\\sqrt{25}$."]))
    it.append(pr("un-07", r"$X\sim\mathrm N(100,25)$. The standardized value of $x=95$.", -1, r"$z=\dfrac{95-100}{5}=-1$.", ["Below the mean: negative."]))
    it.append(pr("un-08", r"$X\sim\mathrm N(100,25)$. Find $P(X\le100)$.", R(1, 2), r"The mean divides the area in two equal halves.", ["Symmetry."]))
    return it


def l05_1() -> list[dict]:
    it = []
    for n, data in enumerate(([3, 5, 7, 9, 16], [1, 2, 2, 3, 7], [4, 8, 9, 10, 14]), 1):
        m = R(sum(data), len(data))
        s2 = sum((v - m) ** 2 for v in data) / (len(data) - 1)
        med = sorted(data)[len(data) // 2]
        txt = ",".join(str(v) for v in data)
        it.append(pr(f"ds-{n:02d}a", rf"The mean of ${txt}$.", m, rf"$\dfrac{{{sum(data)}}}{{{len(data)}}}={tex(m)}$.", ["Add and divide by the number of values."]))
        it.append(pr(f"ds-{n:02d}b", rf"The median of ${txt}$.", med, rf"The middle value of the ordered data is ${med}$.", ["Order the data."]))
        it.append(pr(f"ds-{n:02d}c", rf"The sample variance of ${txt}$.", s2, rf"The sum of squared deviations is ${tex(s2 * (len(data) - 1))}$; divided by ${len(data)-1}$ it gives ${tex(s2)}$.", ["Divide by $n-1$."]))
    it.append(pr("ds-04", r"The population variance of $2,4,4,6,9$.", R(28, 5), r"$\dfrac{9+1+1+1+16}{5}=\dfrac{28}5$.", ["Divide by $n$."]))
    it.append(pr("ds-05", r"The sample standard deviation of $2,4,4,6,9$.", sp.sqrt(7), r"$s^2=\dfrac{28}4=7$, so $s=\sqrt7$.", ["Square root of the sample variance."], kind="expression"))
    return it


def fit(pts):
    n = len(pts)
    xb = R(sum(p[0] for p in pts), n)
    yb = R(sum(p[1] for p in pts), n)
    sxx = sum((p[0] - xb) ** 2 for p in pts)
    sxy = sum((p[0] - xb) * (p[1] - yb) for p in pts)
    syy = sum((p[1] - yb) ** 2 for p in pts)
    m = sxy / sxx
    return xb, yb, sxx, sxy, syy, m, yb - m * xb


def l05_2() -> list[dict]:
    it = []
    for n, pts in enumerate((((1, 3), (2, 5), (3, 7)), ((0, 1), (1, 3), (2, 4)), ((1, 6), (2, 4), (3, 3), (5, 1)), ((1, 2), (2, 3), (3, 5), (4, 6))), 1):
        xb, yb, sxx, sxy, syy, m, q = fit(pts)
        txt = ", ".join(f"({a},{b})" for a, b in pts)
        it.append(pr(f"lr-{n:02d}a", rf"The slope $m$ of the least-squares line through ${txt}$.", m, rf"$\bar x={tex(xb)}$, $\bar y={tex(yb)}$, $S_{{xx}}={tex(sxx)}$, $S_{{xy}}={tex(sxy)}$, so $m={tex(m)}$.", ["$m=\\dfrac{S_{xy}}{S_{xx}}$."]))
        it.append(pr(f"lr-{n:02d}b", rf"The intercept $q$ of the least-squares line through ${txt}$.", q, rf"$q=\bar y-m\bar x={tex(q)}$.", ["$q=\\bar y-m\\bar x$."]))
    it.append(pr("lr-05", r"The correlation coefficient of $(1,3),(2,5),(3,7)$, which lie on a line.", 1, r"The points are exactly on the line $y=2x+1$ with positive slope, so $r=1$.", ["The points are aligned."]))
    xb, yb, sxx, sxy, syy, m, q = fit(((1, 2), (2, 3), (3, 5), (4, 6)))
    it.append(pr("lr-06", r"The least-squares line of $(1,2),(2,3),(3,5),(4,6)$ predicts which value of $y$ at $x=5$?", m * 5 + q, r"$y=\dfrac75x+\dfrac12$, so $y(5)=7+\dfrac12=\dfrac{15}{2}$.", ["Use $y=mx+q$."]))
    it.append(pr("lr-07", r"The correlation coefficient of $(1,2),(2,3),(3,5),(4,6)$ (a simplified radical).", sxy / sp.sqrt(sxx * syy), r"$r=\dfrac{7}{\sqrt{5\cdot10}}=\dfrac{7\sqrt2}{10}$.", ["$r=\\dfrac{S_{xy}}{\\sqrt{S_{xx}S_{yy}}}$."], kind="expression"))
    return it


def build() -> None:
    f = lambda title, items: [exset(re.sub(r"[^a-z]", "", title.split()[0].lower()), title, items, format=FMT)]
    write_exercises(f"{M1}/u01-counting/l01-counting-principles", f("Counting principles.", l01_1()), "stat_course.py")
    write_exercises(f"{M1}/u01-counting/l02-repetitions-and-the-binomial-theorem", f("Repetitions and the binomial theorem.", l01_2()), "stat_course.py")
    write_exercises(f"{M1}/u02-probability/l01-sample-spaces-and-axioms", f("Probabilities of events.", l02_1()), "stat_course.py")
    write_exercises(f"{M1}/u02-probability/l02-conditional-probability-and-independence", f("Conditional probability.", l02_2()), "stat_course.py")
    write_exercises(f"{M1}/u02-probability/l03-total-probability-and-bayes", f("Total probability and Bayes.", l02_3()), "stat_course.py")
    write_exercises(f"{M2}/u01-discrete/l01-expectation-and-variance", f("Expectation and variance.", l03_1()), "stat_course.py")
    write_exercises(f"{M2}/u01-discrete/l02-binomial-geometric-poisson", f("Binomial, geometric and Poisson.", l03_2()), "stat_course.py")
    write_exercises(f"{M2}/u02-continuous/l01-density-and-distribution-function", f("Densities.", l04_1()), "stat_course.py")
    write_exercises(f"{M2}/u02-continuous/l02-uniform-exponential-normal", f("Uniform, exponential and normal.", l04_2()), "stat_course.py")
    write_exercises(f"{M3}/u01-data/l01-describing-data", f("Describing data.", l05_1()), "stat_course.py")
    write_exercises(f"{M3}/u01-data/l02-least-squares-line", f("Least squares.", l05_2()), "stat_course.py")
