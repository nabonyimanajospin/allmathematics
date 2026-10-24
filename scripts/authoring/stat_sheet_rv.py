"""Course 3 (stat): random variables and special distributions of the STAT8225 exercise sheet, and the mid-summer exam.

Moments, skewness and kurtosis are computed exactly with SymPy from the probability mass function or the density, and the
distribution functions (binomial, Poisson, exponential, normal) are cross-checked numerically. Printed errors are corrected and said in the `note`
of the exercise; the questions that could not be read with certainty are left out."""

from __future__ import annotations

import math

import sympy as sp
from stat_course import C, R, pr
from toolkit import ex, exset

SOURCE = "STAT8225 exercise sheet, T. Hakizimana"
EXAM = "STAT8225 mid-summer exam 2025-2026 (3 July 2026), T. Hakizimana and V. N."
SCRIPT = "stat_sheet_rv.py"
M1 = "stat/m01-probability"
M2 = "stat/m02-random-variables"
t = sp.Symbol("t", real=True)
x = sp.Symbol("x", real=True)
E = sp.E
FMT = "Type a whole number, a fraction such as `7/19`, or an exact expression such as `exp(-5)` or `sqrt(7)/3`. Write the standard normal distribution function as `Phi(z)`. For a function of t type for example `(1+2*exp(t))/3`."


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


def L(v: sp.Expr) -> str:
    return sp.latex(v, ln_notation=True).replace("\\frac", "\\dfrac")


def expr_item(id_: str, stmt: str, value: sp.Expr, solution: str, hints: list[str], variables: list[str] | None = None, **kw: object) -> dict:
    v = sp.simplify(value)
    kind = "number" if v.is_Integer else "expression"
    from toolkit import eng

    return ex(id_, stmt, kind, eng(v), hints=hints, solution=solution, **({"variables": variables} if variables else {}), **kw)


# --- moments of a discrete variable ---------------------------------------------------------------------------------------------------
class Discrete:
    def __init__(self, pmf: dict[int, sp.Rational]) -> None:
        assert sum(pmf.values()) == 1, pmf
        self.pmf = pmf
        self.mean = sp.nsimplify(sum(k * p for k, p in pmf.items()))
        self.mu = lambda r: sp.nsimplify(sum((k - self.mean) ** r * p for k, p in pmf.items()))
        self.var = sp.simplify(self.mu(2))
        self.sd = sp.sqrt(self.var)
        self.skew = sp.simplify(self.mu(3) / self.sd**3)
        self.kurt = sp.simplify(self.mu(4) / self.sd**4)
        self.mgf = sum(p * sp.exp(k * t) for k, p in pmf.items())

    def table(self) -> str:
        return ", ".join(rf"$P(X={k})={L(p)}$" for k, p in self.pmf.items())

    def working(self) -> str:
        m = self.mean
        return (
            rf"Mean $E[X]=\sum xP(X=x)={L(m)}$. Central moments $\mu_r=E[(X-{L(m)})^r]$: $\mu_2={L(self.mu(2))}$, $\mu_3={L(self.mu(3))}$, $\mu_4={L(self.mu(4))}$. "
            rf"Variance $\sigma^2=\mu_2={L(self.var)}$, standard deviation $\sigma={L(self.sd)}$. Skewness $\gamma_1=\dfrac{{\mu_3}}{{\sigma^3}}={L(self.skew)}$. Kurtosis $\beta_2=\dfrac{{\mu_4}}{{\sigma^4}}={L(self.kurt)}$."
        )


def moment_items(tag: str, label: str, d: Discrete, median: int | None, mode: int) -> list[dict]:
    head = rf"The mass function of $X$ is {label} ({d.table()})."
    out = [
        expr_item(f"{tag}-mean", rf"{head} Find the mean $E[X]$ (a measure of location).", d.mean, d.working(), [r"$E[X]=\sum x\,P(X=x)$."]),
        expr_item(f"{tag}-var", rf"{head} Find the variance $\operatorname{{Var}}(X)$ (a measure of dispersion).", d.var, d.working(), [r"$\operatorname{Var}(X)=E[(X-\mu)^2]=E[X^2]-\mu^2$."]),
        expr_item(f"{tag}-sd", rf"{head} Find the standard deviation $\sigma$.", d.sd, d.working(), [r"$\sigma=\sqrt{\operatorname{Var}(X)}$."]),
        expr_item(f"{tag}-skew", rf"{head} Find the skewness $\gamma_1=\mu_3/\sigma^3$ (a measure of shape).", d.skew, d.working(), [r"First the central moment $\mu_3=E[(X-\mu)^3]$."]),
        expr_item(f"{tag}-kurt", rf"{head} Find the kurtosis $\beta_2=\mu_4/\sigma^4$ (a measure of shape).", d.kurt, d.working(), [r"First the central moment $\mu_4=E[(X-\mu)^4]$."]),
        pr(f"{tag}-mode", rf"{head} Find the mode (the most probable value).", mode, rf"The largest probability is ${L(max(d.pmf.values()))}$, at $x={mode}$.", ["Look for the largest probability."]),
    ]
    if median is not None:
        cum = 0
        rows = []
        for k, p in d.pmf.items():
            cum += p
            rows.append(rf"F({k})={L(cum)}")
        out.append(pr(f"{tag}-median", rf"{head} Find the median (the smallest value $x$ with $F(x)\ge\dfrac12$).", median, rf"The cumulative probabilities are ${', '.join(rows)}$. The first one that reaches $\dfrac12$ is at $x={median}$.", ["Add the probabilities from the smallest value upward."]))
    return out


def mgf_items(tag: str, label: str, d: Discrete) -> list[dict]:
    head = rf"The mass function of $X$ is {label}."
    mgf_text = " + ".join(rf"{L(p)}e^{{{k}t}}" for k, p in d.pmf.items())
    m1 = sp.diff(d.mgf, t).subs(t, 0)
    m2 = sp.diff(d.mgf, t, 2).subs(t, 0)
    assert sp.simplify(m1 - d.mean) == 0 and sp.simplify(m2 - d.mean**2 - d.var) == 0
    return [
        expr_item(f"{tag}-mgf", rf"{head} Find the moment generating function $M(t)=E\left[e^{{tX}}\right]$.", d.mgf,
                  rf"$M(t)=\sum_x e^{{tx}}P(X=x)={mgf_text}$. Check: $M(0)=\sum P(X=x)=1$.", [r"$M(t)=\sum_x e^{tx}P(X=x)$."], variables=["t"]),
        expr_item(f"{tag}-mgf1", rf"{head} Use $M(t)$ to find $E[X]=M'(0)$.", m1,
                  rf"$M'(t)=\sum_x x\,e^{{tx}}P(X=x)$, so $M'(0)=\sum xP(X=x)={L(m1)}$.", [r"Differentiate $M(t)$ and put $t=0$."]),
        expr_item(f"{tag}-mgf2", rf"{head} Use $M(t)$ to find $E[X^2]=M''(0)$.", m2,
                  rf"$M''(t)=\sum_x x^2e^{{tx}}P(X=x)$, so $M''(0)=\sum x^2P(X=x)={L(m2)}$. Then $\operatorname{{Var}}(X)=E[X^2]-E[X]^2={L(m2)}-\left({L(m1)}\right)^2={L(d.var)}$.", [r"$M''(0)=E[X^2]$."]),
    ]


def discrete_rv_items() -> list[dict]:
    out: list[dict] = []
    d1 = Discrete({2: R(1, 3), 3: R(1, 2), 5: R(1, 6)})
    d2 = Discrete({-1: R(1, 4), 0: R(1, 8), 1: R(1, 2), 2: R(1, 8)})
    d3 = Discrete({1: R(2, 5), 3: R(1, 10), 4: R(1, 5), 5: R(3, 10)})
    out += moment_items("rv-1i", r"$\left(2,\dfrac13\right),\left(3,\dfrac12\right),\left(5,\dfrac16\right)$", d1, 3, 3)
    out += moment_items("rv-1ii", r"$\left(-1,\dfrac14\right),\left(0,\dfrac18\right),\left(1,\dfrac12\right),\left(2,\dfrac18\right)$", d2, 1, 1)
    out += moment_items("rv-1iii", r"$(1,0.4),(3,0.1),(4,0.2),(5,0.3)$", d3, None, 1)
    out += mgf_items("rv-1i", r"$\left(2,\dfrac13\right),\left(3,\dfrac12\right),\left(5,\dfrac16\right)$", d1)
    # 2) f(x) = x/9, x in {2,3,4}
    d = Discrete({k: R(k, 9) for k in (2, 3, 4)})
    lab = r"$f(x)=\dfrac x9$ for $x\in\{2,3,4\}$"
    out += mgf_items("rv-2", lab, d)
    out += [
        expr_item("rv-2var", rf"The mass function of $X$ is {lab}. Find $\operatorname{{Var}}(X)$.", d.var, d.working(), [r"$E[X^2]-E[X]^2$."]),
        expr_item("rv-2skew", rf"The mass function of $X$ is {lab}. Find the skewness $\gamma_1$.", d.skew, d.working(), [r"$\mu_3/\sigma^3$."]),
    ]
    # 3) f(x) = a (x+1)^2, x in {0,1,2,3}
    a = sp.Symbol("a")
    sol_a = sp.solve(sp.Eq(sum(a * (k + 1) ** 2 for k in range(4)), 1), a)[0]
    assert sol_a == R(1, 30)
    out.append(pr("rv-3a", r"The mass function of $X$ is $f(x)=a(x+1)^2$ for $x\in\{0,1,2,3\}$. Find $a$.", sol_a,
                  r"The probabilities must add up to $1$: $a\left(1^2+2^2+3^2+4^2\right)=30a=1$, so $a=\dfrac1{30}$.", ["The sum of all probabilities is $1$."]))
    d = Discrete({k: R((k + 1) ** 2, 30) for k in range(4)})
    lab = r"$f(x)=\dfrac{(x+1)^2}{30}$ for $x\in\{0,1,2,3\}$"
    out += mgf_items("rv-3", lab, d)
    out.append(expr_item("rv-3skew", rf"The mass function of $X$ is {lab}. Find the skewness $\gamma_1$.", d.skew, d.working(), [r"$\mu_3/\sigma^3$."]))
    out.append(expr_item("rv-3kurt", rf"The mass function of $X$ is {lab}. Find the kurtosis $\beta_2$.", d.kurt, d.working(), [r"$\mu_4/\sigma^4$."]))
    # 4) f(x) = (1+|x-3|)/11, x in 1..5
    d = Discrete({k: R(1 + abs(k - 3), 11) for k in range(1, 6)})
    lab = r"$f(x)=\dfrac{1+|x-3|}{11}$ for $x\in\{1,2,3,4,5\}$"
    out += mgf_items("rv-4", lab, d)
    out.append(expr_item("rv-4skew", rf"The mass function of $X$ is {lab}. Find the skewness $\gamma_1$.", d.skew, d.working() + r" The mass function is symmetric about $3$, so the skewness is $0$.", [r"Is the mass function symmetric?"]))
    out.append(expr_item("rv-4kurt", rf"The mass function of $X$ is {lab}. Find the kurtosis $\beta_2$.", d.kurt, d.working(), [r"$\mu_4/\sigma^4$."]))
    # 5) 0.5a, 1.5a, a
    a = sp.Symbol("a")
    sol_a = sp.solve(sp.Eq(R(1, 2) * a + R(3, 2) * a + a, 1), a)[0]
    assert sol_a == R(1, 3)
    note5 = "The sheet prints $f(x)=0.5x,\\ 1.5x,\\ x$ for $x=0,1,2$ and asks for $a$; the letter $a$ is missing in print. We read $f(0)=0.5a$, $f(1)=1.5a$, $f(2)=a$ (otherwise $f(1)=1.5$ would exceed $1$)."
    out.append(pr("rv-5a", r"The mass function of $X$ is $f(0)=0.5a$, $f(1)=1.5a$, $f(2)=a$ and $f(x)=0$ elsewhere. Determine $a$.", sol_a,
                  r"The probabilities add up to $1$: $0.5a+1.5a+a=3a=1$, so $a=\dfrac13$. Then $f(0)=\dfrac16$, $f(1)=\dfrac12$, $f(2)=\dfrac13$.", ["The sum of the probabilities is $1$."], note=note5))
    d = Discrete({0: R(1, 6), 1: R(1, 2), 2: R(1, 3)})
    lab = r"$f(0)=\dfrac16$, $f(1)=\dfrac12$, $f(2)=\dfrac13$"
    out += [
        pr("rv-5b1", rf"The mass function of $X$ is {lab}. Find $P(X<2)$.", d.pmf[0] + d.pmf[1], r"$P(X<2)=P(X=0)+P(X=1)=\dfrac16+\dfrac12=\dfrac23$.", ["Add the probabilities of the values below $2$."]),
        pr("rv-5b2", rf"The mass function of $X$ is {lab}. Find $P(X\le2)$.", sp.Integer(1), r"All the values are at most $2$, so $P(X\le2)=1$.", ["Which values are above $2$?"]),
        pr("rv-5b3", rf"The mass function of $X$ is {lab}. Find $P(1\le X\le2)$.", d.pmf[1] + d.pmf[2], r"$P(1\le X\le2)=P(X=1)+P(X=2)=\dfrac12+\dfrac13=\dfrac56$.", ["Both endpoints are included."]),
    ]
    out += mgf_items("rv-5", lab, d)
    out.append(expr_item("rv-5var", rf"The mass function of $X$ is {lab}. Find $\operatorname{{Var}}(X)$.", d.var, d.working(), [r"$E[X^2]-E[X]^2$."]))
    out.append(expr_item("rv-5skew", rf"The mass function of $X$ is {lab}. Find the skewness $\gamma_1$.", d.skew, d.working(), [r"$\mu_3/\sigma^3$."]))
    out.append(mc("rv-m1", r"$X$ takes the values $0,1,2$ with probabilities $\dfrac16,\dfrac12,\dfrac13$. What is $E[X^2]$?", [r"$\dfrac76$", r"$\dfrac32$", r"$\dfrac{11}{6}$", r"$\dfrac{5}{3}$"], 2,
                 r"$E[X^2]=\sum x^2P(X=x)$.", r"$E[X^2]=0\cdot\dfrac16+1\cdot\dfrac12+4\cdot\dfrac13=\dfrac12+\dfrac43=\dfrac{11}6$. (Do not confuse it with $E[X]=\dfrac76$.)"))
    return out


# --- continuous variables (sheet 6 and 7) ------------------------------------------------------------------------------------------------
def continuous_rv_items() -> list[dict]:
    out: list[dict] = []
    a = sp.Symbol("a", positive=True)
    f = 2 * a * (10 - x)
    sol_a = sp.solve(sp.Eq(sp.integrate(f, (x, 0, 10)), 1), a)[0]
    assert sol_a == R(1, 100)
    g = sp.simplify(f.subs(a, sol_a))
    out.append(pr("co-6a", r"The density of $X$ is $f(x)=2a(10-x)$ for $0\le x\le10$ and $0$ elsewhere. Determine $a$.", sol_a,
                  r"The area under the density must be $1$: $\int_0^{10}2a(10-x)\,dx=2a\left[10x-\dfrac{x^2}2\right]_0^{10}=2a\cdot50=100a=1$, so $a=\dfrac1{100}$. The density is $f(x)=\dfrac{10-x}{50}$.", ["The integral of a density over its whole range is $1$."]))
    lab = r"$f(x)=\dfrac{10-x}{50}$ on $[0,10]$"
    p1 = sp.integrate(g, (x, 0, 2))
    p2 = sp.integrate(g, (x, 5, 10))
    p3 = sp.integrate(g, (x, 4, 8))
    out += [
        pr("co-6b1", rf"The density of $X$ is {lab}. Find $P(X<2)$.", p1, rf"$P(X<2)=\int_0^2\dfrac{{10-x}}{{50}}dx=\dfrac1{{50}}\left[10x-\dfrac{{x^2}}2\right]_0^2=\dfrac{{18}}{{50}}={L(p1)}$.", ["Integrate the density from $0$ to $2$."]),
        pr("co-6b2", rf"The density of $X$ is {lab}. Find $P(X>5)$.", p2, rf"$P(X>5)=\int_5^{{10}}\dfrac{{10-x}}{{50}}dx=\dfrac1{{50}}\left[10x-\dfrac{{x^2}}2\right]_5^{{10}}=\dfrac{{50-37.5}}{{50}}={L(p2)}$.", ["Integrate from $5$ to $10$."]),
        pr("co-6b3", rf"The density of $X$ is {lab}. Find $P(4\le X\le8)$.", p3, rf"$P(4\le X\le8)=\int_4^8\dfrac{{10-x}}{{50}}dx=\dfrac1{{50}}\left[10x-\dfrac{{x^2}}2\right]_4^8=\dfrac{{(80-32)-(40-8)}}{{50}}={L(p3)}$.", ["Integrate from $4$ to $8$."]),
    ]
    F = sp.simplify(sp.integrate(g.subs(x, sp.Symbol("s")), (sp.Symbol("s"), 0, x)))
    assert sp.simplify(F - (20 * x - x**2) / 100) == 0
    out.append(expr_item("co-6c", rf"The density of $X$ is {lab}. Find the cumulative function $F(x)$ for $0\le x\le10$.", F,
                         r"$F(x)=\int_0^x\dfrac{10-s}{50}\,ds=\dfrac1{50}\left[10s-\dfrac{s^2}2\right]_0^x=\dfrac{20x-x^2}{100}$. Check: $F(10)=\dfrac{200-100}{100}=1$.", [r"$F(x)=\int_0^xf(s)\,ds$."], variables=["x"]))
    out.append(pr("co-6c2", rf"The density of $X$ is {lab}. Find $F(6)$.", F.subs(x, 6), r"$F(6)=\dfrac{20\cdot6-36}{100}=\dfrac{84}{100}=\dfrac{21}{25}$.", ["Use $F(x)=\\dfrac{20x-x^2}{100}$."]))
    mean = sp.integrate(x * g, (x, 0, 10))
    ex2 = sp.integrate(x**2 * g, (x, 0, 10))
    var = sp.simplify(ex2 - mean**2)
    mu3 = sp.integrate((x - mean) ** 3 * g, (x, 0, 10))
    skew = sp.simplify(mu3 / var ** sp.Rational(3, 2))
    work = rf"$E[X]=\int_0^{{10}}x\,\dfrac{{10-x}}{{50}}dx={L(mean)}$. $E[X^2]={L(ex2)}$, so $\operatorname{{Var}}(X)=E[X^2]-E[X]^2={L(var)}$. Third central moment $\mu_3=\int(x-\mu)^3f(x)dx={L(sp.simplify(mu3))}$ and the skewness is $\gamma_1=\mu_3/\sigma^3={L(skew)}$."
    out += [
        expr_item("co-6d1", rf"The density of $X$ is {lab}. Find the mean $E[X]$.", mean, work, [r"$E[X]=\int xf(x)\,dx$."]),
        expr_item("co-6d2", rf"The density of $X$ is {lab}. Find the variance.", var, work, [r"$E[X^2]-E[X]^2$."]),
        expr_item("co-6d3", rf"The density of $X$ is {lab}. Find the skewness $\gamma_1$ (a positive value means a long tail on the right).", skew, work, [r"$\mu_3=\int(x-\mu)^3f(x)\,dx$."]),
    ]
    med = sp.solve(sp.Eq((20 * x - x**2) / 100, R(1, 2)), x)
    med = [m for m in med if 0 <= m <= 10][0]
    out.append(expr_item("co-6e", rf"The density of $X$ is {lab}. Find the median $m$, defined by $F(m)=\dfrac12$.", med,
                         rf"$F(m)=\dfrac{{20m-m^2}}{{100}}=\dfrac12$ gives $m^2-20m+50=0$, so $m=10\pm5\sqrt2$. Only $m=10-5\sqrt2$ lies in $[0,10]$.", [r"Solve $F(m)=\dfrac12$ and keep the root in $[0,10]$."]))
    # 7) k / x^2, x >= 400
    k = sp.Symbol("k", positive=True)
    xs = sp.Symbol("s", positive=True)
    sol_k = sp.solve(sp.Eq(sp.integrate(k / xs**2, (xs, 400, sp.oo)), 1), k)[0]
    assert sol_k == 400
    out.append(pr("co-7a", r"The density of $X$ is $f(x)=\dfrac k{x^2}$ for $x\ge400$ and $0$ elsewhere. Determine $k$.", sol_k,
                  r"$\int_{400}^{\infty}\dfrac k{x^2}dx=k\left[-\dfrac1x\right]_{400}^{\infty}=\dfrac k{400}=1$, so $k=400$.", ["The total area is $1$."]))
    lab7 = r"$f(x)=\dfrac{400}{x^2}$ for $x\ge400$"
    F7 = sp.simplify(sp.integrate(400 / xs**2, (xs, 400, x)))
    assert sp.simplify(F7 - (1 - 400 / x)) == 0
    out.append(expr_item("co-7b", rf"The density of $X$ is {lab7}. Find the cumulative function $F(x)$ for $x\ge400$.", F7, r"$F(x)=\int_{400}^x\dfrac{400}{s^2}ds=400\left[-\dfrac1s\right]_{400}^x=400\left(\dfrac1{400}-\dfrac1x\right)=1-\dfrac{400}x$.", [r"$F(x)=\int_{400}^xf(s)\,ds$."], variables=["x"]))
    out += [
        pr("co-7c1", rf"The density of $X$ is {lab7}. Find $P(X<500)$.", F7.subs(x, 500), r"$F(500)=1-\dfrac{400}{500}=\dfrac15$.", ["Use $F$."]),
        pr("co-7c2", rf"The density of $X$ is {lab7}. Find $P(X>600)$.", 1 - F7.subs(x, 600), r"$P(X>600)=1-F(600)=\dfrac{400}{600}=\dfrac23$.", ["The complement of $F$."]),
        pr("co-7c3", rf"The density of $X$ is {lab7}. Find $P(400\le X\le800)$.", F7.subs(x, 800), r"$F(800)-F(400)=\left(1-\dfrac12\right)-0=\dfrac12$.", ["$F(400)=0$."]),
        mc("co-7d", rf"The density of $X$ is {lab7}. What can be said about the mean $E[X]$?", ["$E[X]=400$", "$E[X]=800$", "$E[X]$ does not exist: the integral diverges", "$E[X]=1200$"], 2,
           r"$E[X]=\int_{400}^\infty x\cdot\dfrac{400}{x^2}\,dx$.", r"$E[X]=\int_{400}^{\infty}x\cdot\dfrac{400}{x^2}dx=400\int_{400}^{\infty}\dfrac{dx}x=400\left[\ln x\right]_{400}^{\infty}=\infty$. The integral diverges, so the mean (and therefore the variance and the skewness) does not exist. A density can be perfectly valid and still have no mean."),
        pr("co-7e", rf"The density of $X$ is {lab7}. Find the median $m$ with $F(m)=\dfrac12$.", sp.Integer(800), r"$1-\dfrac{400}m=\dfrac12$ gives $\dfrac{400}m=\dfrac12$, so $m=800$.", ["Solve $F(m)=\\dfrac12$."]),
    ]
    return out


# --- special distributions (sheet) -----------------------------------------------------------------------------------------------------------
def binomial_items() -> list[dict]:
    out: list[dict] = []
    n, p = sp.symbols("n p", positive=True)
    # 1) mean 6, sd sqrt 2
    q = 1 - sp.Rational(2, 3)
    pp, nn = sp.Rational(2, 3), 9
    assert nn * pp == 6 and nn * pp * (1 - pp) == 2
    sol1 = r"$np=6$ and $npq=\sigma^2=2$. Divide: $q=\dfrac{npq}{np}=\dfrac26=\dfrac13$, so $p=\dfrac23$ and $n=\dfrac6p=9$."
    out.append(pr("sp-1n", r"A binomial distribution has mean $6$ and standard deviation $\sqrt2$. Find $n$.", nn, sol1, [r"$\mathrm{mean}=np$, $\mathrm{variance}=npq$."]))
    out.append(pr("sp-1p", r"A binomial distribution has mean $6$ and standard deviation $\sqrt2$. Find $p$.", pp, sol1, [r"Divide the variance by the mean to get $q$."]))
    out.append(pr("sp-1a", r"A binomial distribution has mean $6$ and standard deviation $\sqrt2$ (so $n=9$, $p=\dfrac23$). Find the first term $P(X=0)$.", sp.Rational(1, 3) ** 9, r"$P(X=0)=q^9=\left(\dfrac13\right)^9=\dfrac1{19683}$.", ["$P(X=0)=q^n$."]))
    out.append(pr("sp-1b", r"A binomial distribution has $n=9$, $p=\dfrac23$. Find the second term $P(X=1)$.", 9 * sp.Rational(2, 3) * sp.Rational(1, 3) ** 8, r"$P(X=1)=\dbinom91p\,q^8=9\cdot\dfrac23\cdot\left(\dfrac13\right)^8=\dfrac{6}{3^8}=\dfrac2{2187}$.", [r"$\dbinom9 1pq^8$."]))
    mgf = ((1 + 2 * sp.exp(t)) / 3) ** 9
    out.append(expr_item("sp-1m", r"A binomial distribution has $n=9$ and $p=\dfrac23$. Find its moment generating function.", mgf, r"For a binomial distribution $M(t)=\left(q+pe^t\right)^n=\left(\dfrac13+\dfrac23e^t\right)^9=\left(\dfrac{1+2e^t}{3}\right)^9$.", [r"$M(t)=(q+pe^t)^n$."], variables=["t"]))
    # 2) four coins
    pr_ = lambda kk: sp.Rational(math.comb(4, kk), 16)
    out.append(pr("sp-2a", r"Four perfect coins are tossed simultaneously. What is the probability of getting at least $2$ heads?", sum(pr_(kk) for kk in (2, 3, 4)), r"$X\sim B\left(4,\dfrac12\right)$. $P(X\ge2)=1-P(0)-P(1)=1-\dfrac1{16}-\dfrac4{16}=\dfrac{11}{16}$.", ["Use the complement: $0$ or $1$ head."]))
    out.append(pr("sp-2b", r"Four perfect coins are tossed simultaneously. What is the probability of getting at most $2$ heads?", sum(pr_(kk) for kk in (0, 1, 2)), r"$P(X\le2)=\dfrac{1+4+6}{16}=\dfrac{11}{16}$.", ["Add the cases $0$, $1$, $2$."]))
    out.append(pr("sp-2c", r"Four perfect coins are tossed simultaneously. What is the probability of getting no heads?", pr_(0), r"$P(X=0)=\left(\dfrac12\right)^4=\dfrac1{16}$.", ["All four tails."]))
    # 3) n=6, 9 P(X=4) = P(X=2)
    sol = [pp_ for pp_ in (sp.Rational(1, 4),) if 9 * math.comb(6, 4) * pp_**4 * (1 - pp_) ** 2 == math.comb(6, 2) * pp_**2 * (1 - pp_) ** 4]
    assert sol == [sp.Rational(1, 4)]
    sol3 = r"$9\dbinom64p^4q^2=\dbinom62p^2q^4$. Both coefficients equal $15$; divide by $15p^2q^2$: $9p^2=q^2$, so $q=3p$ (positive numbers). With $p+q=1$: $4p=1$, $p=\dfrac14$."
    out.append(pr("sp-3p", r"$X$ is binomial with $n=6$ and satisfies $9P(X=4)=P(X=2)$. Find $p$.", sp.Rational(1, 4), sol3, [r"Write both probabilities with $p$ and $q$ and divide."]))
    out.append(pr("sp-3a", r"$X$ is binomial with $n=6$ and $9P(X=4)=P(X=2)$ (so $p=\dfrac14$). Find $P(X=2)$.", math.comb(6, 2) * sp.Rational(1, 16) * sp.Rational(3, 4) ** 4, r"$P(X=2)=\dbinom62\left(\dfrac14\right)^2\left(\dfrac34\right)^4=15\cdot\dfrac{81}{4096}=\dfrac{1215}{4096}$.", [r"$\dbinom62p^2q^4$."]))
    # 4) n=5, mean + variance = 1.8
    sol_p = [pp_ for pp_ in (sp.Rational(1, 5), sp.Rational(9, 5)) if 5 * pp_ + 5 * pp_ * (1 - pp_) == sp.Rational(9, 5)]
    assert sp.Rational(1, 5) in sol_p
    out.append(pr("sp-4", r"The sum of the mean and the variance of a binomial distribution with $5$ trials is $1.8$. Find $p$.", sp.Rational(1, 5),
                  r"$np+npq=5p+5p(1-p)=10p-5p^2=1.8$, so $5p^2-10p+1.8=0$, i.e. $p^2-2p+0.36=0$. Then $p=1\pm\sqrt{1-0.36}=1\pm0.8$. Only $p=0.2=\dfrac15$ is a probability. The distribution is $B\left(5,\dfrac15\right)$.", ["Write mean and variance with $p$ and solve the quadratic equation."]))
    # 5) mean 4, variance 3
    assert 16 * sp.Rational(1, 4) == 4 and 16 * sp.Rational(1, 4) * sp.Rational(3, 4) == 3
    sol5 = r"$np=4$ and $npq=3$, so $q=\dfrac34$, $p=\dfrac14$ and $n=\dfrac4p=16$."
    out.append(pr("sp-5n", r"A binomial distribution has mean $4$ and variance $3$. Find $n$.", 16, sol5, [r"Divide the variance by the mean."]))
    out.append(pr("sp-5a", r"A binomial distribution has mean $4$ and variance $3$ (so $n=16$, $p=\dfrac14$). Find the last term $P(X=16)$.", sp.Rational(1, 4) ** 16, r"$P(X=16)=p^{16}=\left(\dfrac14\right)^{16}=\dfrac1{4^{16}}$.", ["$P(X=n)=p^n$."]))
    out.append(pr("sp-5b", r"A binomial distribution has $n=16$ and $p=\dfrac14$. Find the second last term $P(X=15)$.", 16 * sp.Rational(1, 4) ** 15 * sp.Rational(3, 4), r"$P(X=15)=\dbinom{16}{15}p^{15}q=16\cdot\dfrac{3}{4^{16}}=\dfrac{48}{4^{16}}=\dfrac3{4^{14}}$.", [r"$\dbinom{16}{15}=16$."]))
    out.append(expr_item("sp-5m", r"A binomial distribution has $n=16$ and $p=\dfrac14$. Find its moment generating function.", ((3 + sp.exp(t)) / 4) ** 16, r"$M(t)=(q+pe^t)^n=\left(\dfrac34+\dfrac14e^t\right)^{16}=\left(\dfrac{3+e^t}{4}\right)^{16}$.", [r"$M(t)=(q+pe^t)^n$."], variables=["t"]))
    return out


def poisson_items() -> list[dict]:
    out: list[dict] = []
    lam = sp.Symbol("lambda", positive=True)
    pm = lambda kk, l: sp.exp(-l) * l**kk / sp.factorial(kk)
    # 7) P(1) + P(2) = P(0)
    s7 = sp.solve(sp.Eq(lam + lam**2 / 2, 1), lam)
    s7 = [v for v in s7 if v > 0][0]
    assert sp.simplify(s7 - (sp.sqrt(3) - 1)) == 0
    out.append(expr_item("po-7v", r"$X$ is Poisson with $P(X=1)+P(X=2)=P(X=0)$. Find the variance of $X$.", s7,
                         r"Divide by $e^{-\lambda}$: $\lambda+\dfrac{\lambda^2}2=1$, so $\lambda^2+2\lambda-2=0$ and $\lambda=-1\pm\sqrt3$. Only $\lambda=\sqrt3-1>0$ is possible. For a Poisson distribution variance $=\lambda=\sqrt3-1$.", [r"$P(X=k)=e^{-\lambda}\dfrac{\lambda^k}{k!}$; divide by $e^{-\lambda}$."]))
    out.append(expr_item("po-7m", r"$X$ is Poisson with $P(X=1)+P(X=2)=P(X=0)$, so $\lambda=\sqrt3-1$. Find the moment generating function.", sp.exp((sp.sqrt(3) - 1) * (sp.exp(t) - 1)),
                         r"For a Poisson distribution $M(t)=e^{\lambda(e^t-1)}=e^{(\sqrt3-1)(e^t-1)}$.", [r"$M(t)=e^{\lambda(e^t-1)}$."], variables=["t"]))
    # 8) P(1) = P(2), P(0)
    out.append(expr_item("po-8", r"$X$ is Poisson with $P(X=1)=P(X=2)$. Find $P(X=0)$.", sp.exp(-2), r"$e^{-\lambda}\lambda=e^{-\lambda}\dfrac{\lambda^2}2$ gives $\lambda=2$ (dividing by $\lambda\ne0$). Then $P(X=0)=e^{-2}$.", [r"Divide both sides by $e^{-\lambda}\lambda$."]))
    # 9) P(2) = 9P(4) + 90P(6)
    l9 = [v for v in sp.solve(sp.Eq(pm(2, lam), 9 * pm(4, lam) + 90 * pm(6, lam)), lam) if v > 0]
    assert l9 == [1]
    out.append(pr("po-9v", r"$X$ is Poisson with $P(X=2)=9P(X=4)+90P(X=6)$. Find the variance of $X$.", 1,
                  r"Divide by $e^{-\lambda}\lambda^2$: $\dfrac12=\dfrac{9\lambda^2}{24}+\dfrac{90\lambda^4}{720}=\dfrac{3\lambda^2}8+\dfrac{\lambda^4}8$. Multiply by $8$: $\lambda^4+3\lambda^2-4=0$, i.e. $(\lambda^2+4)(\lambda^2-1)=0$. So $\lambda=1$ and the variance is $1$.", [r"Divide by $e^{-\lambda}\lambda^2$ and set $u=\lambda^2$."]))
    out.append(expr_item("po-9m", r"$X$ is Poisson with $P(X=2)=9P(X=4)+90P(X=6)$, so $\lambda=1$. Find the moment generating function.", sp.exp(sp.exp(t) - 1), r"$M(t)=e^{\lambda(e^t-1)}=e^{e^t-1}$.", [r"$M(t)=e^{\lambda(e^t-1)}$."], variables=["t"]))
    # 10) P(2) = P(3)
    out.append(pr("po-10", r"The number of fatal accidents in a week has a Poisson distribution such that the probability of two fatal accidents is the same as that of three. Find the mean number of accidents.", 3,
                  r"$e^{-\lambda}\dfrac{\lambda^2}{2}=e^{-\lambda}\dfrac{\lambda^3}{6}$. Divide by $e^{-\lambda}\lambda^2$: $\dfrac12=\dfrac\lambda6$, so $\lambda=3$.", [r"Divide both sides by $e^{-\lambda}\lambda^2$."]))
    # 11) lambda = 3, 200 drivers
    out.append(expr_item("po-11a", r"The number of fatal accidents in a year of a taxi-driver follows a Poisson distribution with mean $3$. Out of $200$ drivers, find the expected number with no accident in a year.", 200 * sp.exp(-3), r"$P(X=0)=e^{-3}$, so among $200$ drivers about $200e^{-3}$ have no accident (about $10$).", [r"Multiply $P(X=0)$ by $200$."]))
    more5 = 1 - sum(pm(kk, 3) for kk in range(6))
    out.append(expr_item("po-11b", r"With the same Poisson distribution (mean $3$), find the expected number of drivers, out of $200$, with more than $5$ accidents in a year.", 200 * more5,
                         rf"$P(X>5)=1-\sum_{{k=0}}^5e^{{-3}}\dfrac{{3^k}}{{k!}}=1-e^{{-3}}\left(1+3+\dfrac92+\dfrac92+\dfrac{{27}}8+\dfrac{{81}}{{40}}\right)=1-{L(sp.simplify(sum(pm(kk, 3) for kk in range(6))))}$. Multiply by $200$.", [r"Use the complement: $0$ to $5$ accidents."]))
    out.append(mc("po-m1", r"A Poisson variable has $P(X=1)=P(X=2)$. What is its mean?", ["$1$", "$2$", "$\\dfrac12$", "$4$"], 1, r"$\dfrac{P(X=2)}{P(X=1)}=\dfrac\lambda2$.", r"$\dfrac{P(X=2)}{P(X=1)}=\dfrac{\lambda}{2}=1$, so $\lambda=2$."))
    return out


def exp_normal_items() -> list[dict]:
    out: list[dict] = []
    # 12) f(x) = k e^{-x/6}
    out.append(pr("ex-12k", r"The length of a phone call has the density $f(x)=ke^{-x/6}$ for $x>0$ (and $0$ otherwise). Find $k$.", sp.Rational(1, 6), r"$\int_0^{\infty}ke^{-x/6}dx=k\cdot6=1$, so $k=\dfrac16$ (an exponential distribution with mean $6$ minutes).", [r"$\int_0^\infty e^{-x/6}dx=6$."]))
    out.append(expr_item("ex-12a", r"The length of a call has the density $f(x)=\dfrac16e^{-x/6}$ for $x>0$. Find the probability that the person talks more than $8$ minutes.", sp.exp(-sp.Rational(8, 6)), r"$P(X>8)=\int_8^\infty\dfrac16e^{-x/6}dx=e^{-8/6}=e^{-4/3}$.", [r"$P(X>a)=e^{-a/6}$."]))
    out.append(expr_item("ex-12b", r"The length of a call has the density $f(x)=\dfrac16e^{-x/6}$ for $x>0$. Find the probability that the person talks less than $4$ minutes.", 1 - sp.exp(-sp.Rational(4, 6)), r"$P(X<4)=1-e^{-4/6}=1-e^{-2/3}$.", [r"$P(X<a)=1-e^{-a/6}$."]))
    out.append(expr_item("ex-12c", r"The length of a call has the density $f(x)=\dfrac16e^{-x/6}$ for $x>0$. Find the probability that the person talks between $5$ and $10$ minutes.", sp.exp(-sp.Rational(5, 6)) - sp.exp(-sp.Rational(10, 6)), r"$P(5<X<10)=P(X>5)-P(X>10)=e^{-5/6}-e^{-10/6}=e^{-5/6}-e^{-5/3}$.", [r"$P(X>5)-P(X>10)$."]))
    # 13) F(x) = 1 - e^{-8x}, hours
    out.append(expr_item("ex-13a", r"The waiting time $X$ in hours between two speeders has the distribution function $F(x)=1-e^{-8x}$ for $x>0$. Find the probability of waiting more than $12$ minutes.", sp.exp(-sp.Rational(8, 5)), r"$12$ minutes $=\dfrac15$ hour. $P(X>\tfrac15)=1-F\left(\tfrac15\right)=e^{-8/5}$.", [r"Convert the minutes to hours first."]))
    out.append(expr_item("ex-13b", r"The waiting time $X$ in hours between two speeders has the distribution function $F(x)=1-e^{-8x}$ for $x>0$. Find the probability of waiting less than $5$ minutes.", 1 - sp.exp(-sp.Rational(2, 3)), r"$5$ minutes $=\dfrac1{12}$ hour. $P(X<\tfrac1{12})=F\left(\tfrac1{12}\right)=1-e^{-8/12}=1-e^{-2/3}$.", [r"$5$ minutes is $\dfrac{5}{60}=\dfrac1{12}$ hour."]))
    # normal distribution
    PhiF = sp.Function("Phi")

    def Phi(z: sp.Expr) -> sp.Expr:
        return sp.Rational(1, 2) if z == 0 else PhiF(z)

    nt = r"$\Phi(z)=P(Z\le z)$ is the distribution function of the standard normal law (in the answer write `Phi(z)`; a table gives its values). $\Phi(-z)=1-\Phi(z)$."

    def normal(id_: str, stmt: str, value: sp.Expr, solution: str, hints: list[str]) -> dict:
        from allmaths_engine.parser import parse
        from toolkit import eng

        key = eng(value)
        as_erf = value.replace(PhiF, lambda z: (1 + sp.erf(z / sp.sqrt(2))) / 2)
        assert sp.simplify(parse(key, fmt="text", trusted=True).value - as_erf) == 0, key
        return ex(id_, stmt + r" Give the answer with $\Phi$.", "expression", key, hints=hints, solution=solution + " " + nt)

    out.append(pr("no-14z", r"Speeds of cars are normally distributed with mean $90$ km/h and standard deviation $10$ km/h. Find the standardized value $z$ of the speed $100$ km/h.", 1, r"$z=\dfrac{x-\mu}{\sigma}=\dfrac{100-90}{10}=1$.", [r"$z=\dfrac{x-\mu}\sigma$."]))
    out.append(normal("no-14", r"Speeds of cars are normally distributed with mean $90$ km/h and standard deviation $10$ km/h. Find the probability that a car picked at random travels at more than $100$ km/h.", 1 - Phi(1), r"$P(X>100)=P\left(Z>\dfrac{100-90}{10}\right)=P(Z>1)=1-\Phi(1)$.", [r"Standardize: $z=\dfrac{x-\mu}\sigma$."]))
    out.append(pr("no-15z", r"The life of an instrument is normal with mean $12$ months and standard deviation $2$ months. Find the standardized value of $7$ months.", -sp.Rational(5, 2), r"$z=\dfrac{7-12}{2}=-\dfrac52$.", [r"$z=\dfrac{x-\mu}\sigma$."]))
    out.append(normal("no-15a", r"The life of an instrument is normal with mean $12$ months and standard deviation $2$ months. Find the probability that it lasts less than $7$ months.", Phi(-sp.Rational(5, 2)), r"$P(X<7)=P\left(Z<\dfrac{7-12}{2}\right)=P\left(Z<-\dfrac52\right)=\Phi\left(-\dfrac52\right)$.", [r"Standardize."]))
    out.append(normal("no-15b", r"The life of an instrument is normal with mean $12$ months and standard deviation $2$ months. Find the probability that it lasts between $7$ and $12$ months.", Phi(0) - Phi(-sp.Rational(5, 2)), r"$P(7<X<12)=\Phi(0)-\Phi\left(-\dfrac52\right)=\dfrac12-\Phi\left(-\dfrac52\right)$, since $z=0$ for $x=12$ and $z=-\dfrac52$ for $x=7$.", [r"$P(a<X<b)=\Phi(z_b)-\Phi(z_a)$."]))
    out.append(normal("no-15c", r"The life of an instrument is normal with mean $12$ months and standard deviation $2$ months. Find the probability that it lasts at most $7$ months.", Phi(-sp.Rational(5, 2)), r"For a continuous variable $P(X\le7)=P(X<7)=\Phi\left(-\dfrac52\right)$ (a single value has probability $0$).", [r"For a continuous variable 'at most' and 'less than' are the same."]))
    out.append(normal("no-16a", r"The assembly time of a car is normal with mean $20$ hours and standard deviation $2$ hours. Find the probability that a car is assembled in less than $19.5$ hours.", Phi(-sp.Rational(1, 4)), r"$z=\dfrac{19.5-20}{2}=-\dfrac14$, so $P(X<19.5)=\Phi\left(-\dfrac14\right)$.", [r"Standardize $19.5$."]))
    out.append(normal("no-16b", r"The assembly time of a car is normal with mean $20$ hours and standard deviation $2$ hours. Find the probability that it is between $20$ and $22$ hours.", Phi(1) - Phi(0), r"$z=0$ for $20$ and $z=\dfrac{22-20}2=1$ for $22$: $P=\Phi(1)-\Phi(0)=\Phi(1)-\dfrac12$.", [r"Standardize both ends."]))
    out.append(normal("no-17a", r"Grades are approximately normal with mean $70$ and standard deviation $10$. Find the proportion of students who score higher than $80$.", 1 - Phi(1), r"$z=\dfrac{80-70}{10}=1$; $P(X>80)=1-\Phi(1)$.", [r"Standardize $80$."]))
    out.append(normal("no-17b", r"Grades are approximately normal with mean $70$ and standard deviation $10$. Find the proportion of students who pass, with a grade of at least $60$.", 1 - Phi(-1), r"$z=\dfrac{60-70}{10}=-1$; $P(X\ge60)=1-\Phi(-1)=\Phi(1)$ by symmetry.", [r"$P(X\ge a)=1-\Phi(z_a)$."]))
    out.append(normal("no-18a", r"Salaries are approximately normal with mean $\$50\,000$ and standard deviation $\$20\,000$. Find the proportion of people who earn less than $\$40\,000$.", Phi(-sp.Rational(1, 2)), r"$z=\dfrac{40\,000-50\,000}{20\,000}=-\dfrac12$; $P(X<40\,000)=\Phi\left(-\dfrac12\right)$.", [r"Standardize."]))
    out.append(normal("no-18b", r"Salaries are approximately normal with mean $\$50\,000$ and standard deviation $\$20\,000$. Find the proportion of people who earn between $\$45\,000$ and $\$65\,000$.", Phi(sp.Rational(3, 4)) - Phi(-sp.Rational(1, 4)), r"$z=\dfrac{45\,000-50\,000}{20\,000}=-\dfrac14$ and $z=\dfrac{65\,000-50\,000}{20\,000}=\dfrac34$. $P=\Phi\left(\dfrac34\right)-\Phi\left(-\dfrac14\right)$.", [r"Standardize both ends."]))
    out.append(normal("no-18c", r"Salaries are approximately normal with mean $\$50\,000$ and standard deviation $\$20\,000$. Find the proportion of people who earn more than $\$70\,000$.", 1 - Phi(1), r"$z=\dfrac{70\,000-50\,000}{20\,000}=1$; $P(X>70\,000)=1-\Phi(1)$.", [r"Standardize."]))
    out.append(mc("no-m1", r"$X$ is normal with mean $100$ and standard deviation $5$. Which value of $z$ corresponds to $x=92.5$?", ["$-1.5$", "$-2.5$", "$1.5$", "$-7.5$"], 0, r"$z=\dfrac{x-\mu}\sigma$.", r"$z=\dfrac{92.5-100}{5}=\dfrac{-7.5}{5}=-1.5$. (Dividing by the variance $25$ instead of the standard deviation $5$ would give $-0.3$.)"))
    return out


# --- the mid-summer exam ----------------------------------------------------------------------------------------------------------------------
def exam_items() -> list[dict]:
    out: list[dict] = []
    out.append(mc("sq-1a", r"**Q1 a(i).** The sample space of an experiment is", ["the set of all possible outcomes of the experiment", "the set of the favorable outcomes of an event", "the probability that the experiment succeeds", "the number of times the experiment is repeated"], 0, r"Think of tossing a die.", r"The **sample space** $S$ is the set of ALL possible outcomes. For a die, $S=\{1,2,3,4,5,6\}$. An event is a subset of $S$ (the favorable outcomes are just one event)."))
    out.append(mc("sq-1b", r"**Q1 a(ii).** Two events $A$ and $B$ are independent when", [r"$A\cap B=\varnothing$", r"$P(A\cap B)=P(A)P(B)$", r"$P(A\cup B)=P(A)+P(B)$", r"$P(A)+P(B)=1$"], 1, r"Independent is not the same as mutually exclusive.", r"Independent events: knowing that $B$ occurred does not change the probability of $A$, that is $P(A\mid B)=P(A)$, which is equivalent to $P(A\cap B)=P(A)P(B)$. The first choice describes mutually exclusive events."))
    out.append(mc("sq-1c", r"**Q1 b.** Which list contains the three axioms of probability?", [r"$P(A)\ge0$; $P(S)=1$; $P(A\cup B)=P(A)+P(B)$ for mutually exclusive $A,B$", r"$P(A)\le1$; $P(S)=0$; $P(A\cap B)=P(A)P(B)$", r"$P(A)>0$; $P(S)=1$; $P(A\cup B)=P(A)P(B)$", r"$P(A)\ge0$; $P(\varnothing)=1$; $P(A\cup B)=P(A)+P(B)$ always"], 0, r"Non-negativity, total probability $1$, additivity.", r"The axioms: (1) $P(A)\ge0$ for every event; (2) $P(S)=1$; (3) additivity: if $A$ and $B$ are mutually exclusive, $P(A\cup B)=P(A)+P(B)$ (and for a countable sequence of pairwise exclusive events). The other lists contain false statements (for example $P(\varnothing)=0$, not $1$)."))
    n2 = [m for m in range(3, 100) if 3 * math.comb(m, 3) == 10 * math.comb(m, 2)]
    assert n2 == [12]
    out.append(pr("sq-2a", r"**Q2 a.** Determine the value of $n$ in $3\dbinom n3=10\dbinom n2$.", 12,
                  r"$3\dbinom n3=\dfrac{3n(n-1)(n-2)}{6}=\dfrac{n(n-1)(n-2)}2$ and $10\dbinom n2=5n(n-1)$. Equal: $\dfrac{n(n-1)(n-2)}2=5n(n-1)$. Divide by $n(n-1)$ (not $0$ for $n\ge3$): $\dfrac{n-2}2=5$, so $n-2=10$ and $n=12$. Check: $3\cdot220=660=10\cdot66$.", [r"Write $\dbinom n3$ and $\dbinom n2$ as products and divide by $n(n-1)$."]))
    ct = sp.binomial(15, 5) * 3**10 * (-1) ** 5
    assert ct == -3003 * 59049
    out.append(pr("sq-2b", r"**Q2 b.** Find the constant term in the expansion of $\left(3x-\dfrac1{x^2}\right)^{15}$.", ct,
                  r"$T_{k+1}=\dbinom{15}k(3x)^{15-k}\left(-\dfrac1{x^2}\right)^k=\dbinom{15}k3^{15-k}(-1)^kx^{15-k-2k}=\dbinom{15}k3^{15-k}(-1)^kx^{15-3k}$. Constant: $15-3k=0$, $k=5$. $T_6=\dbinom{15}53^{10}(-1)^5=-3003\cdot59049=-177\,324\,147$ (the sign is negative because $k=5$ is odd).", [r"Set the power of $x$ in the general term equal to $0$."]))
    out.append(mc("sq-3a", r"**Q3 a.** $A$ and $B$ are independent. To show that $A$ and $\bar B$ are independent, we use", [r"$P(A\cap\bar B)=P(A)-P(A\cap B)=P(A)\,(1-P(B))=P(A)P(\bar B)$", r"$P(A\cap\bar B)=0$ because $\bar B$ is the opposite of $B$", r"$P(A\cap\bar B)=P(A)+P(\bar B)$", r"$P(\bar B)=P(B)$"], 0, r"Split $A$ into $A\cap B$ and $A\cap\bar B$.",
                 r"$A$ is the union of the disjoint events $A\cap B$ and $A\cap\bar B$, so $P(A\cap\bar B)=P(A)-P(A\cap B)$. By independence $P(A\cap B)=P(A)P(B)$, hence $P(A\cap\bar B)=P(A)-P(A)P(B)=P(A)(1-P(B))=P(A)P(\bar B)$. This is exactly the definition of independence of $A$ and $\bar B$."))
    out.append(pr("sq-3bi", r"**Q3 b(i).** $A$ and $B$ are independent with $P(A)=\dfrac23$ and $P(B)=\dfrac35$. Find $P(A\mid\bar B)$.", sp.Rational(2, 3), r"$A$ and $\bar B$ are independent (Q3 a), so $P(A\mid\bar B)=P(A)=\dfrac23$.", [r"Conditioning on an independent event does not change the probability."]))
    out.append(pr("sq-3bii", r"**Q3 b(ii).** $A$ and $B$ are independent with $P(A)=\dfrac23$ and $P(B)=\dfrac35$. Find $P(\bar A\cup\bar B)$.", 1 - sp.Rational(2, 3) * sp.Rational(3, 5), r"De Morgan: $\bar A\cup\bar B=\overline{A\cap B}$, so $P=1-P(A\cap B)=1-\dfrac23\cdot\dfrac35=1-\dfrac25=\dfrac35$.", [r"$\bar A\cup\bar B=\overline{A\cap B}$."]))
    ps = sp.Rational(8, 10) - sp.Rational(7, 10) + sp.Rational(2, 10)
    out.append(pr("sq-4a1", r"**Q4 a.** The probability that a student passes a mathematics test is $0.7$, that s/he passes both mathematics and statistics is $0.2$, and that s/he passes at least one test is $0.8$. Find the probability that s/he passes the statistics test.", ps, r"$P(S)=P(M\cup S)-P(M)+P(M\cap S)=0.8-0.7+0.2=0.3=\dfrac3{10}$.", [r"Addition rule."]))
    out.append(pr("sq-4a", r"**Q4 a.** The probability that a student passes a mathematics test is $0.7$, that s/he passes both mathematics and statistics is $0.2$, and that s/he passes at least one test is $0.8$. What is the probability that she fails the statistics test and passes mathematics?", sp.Rational(7, 10) - sp.Rational(2, 10),
                  r"We need $P(M\cap\bar S)$. The event $M$ is the union of $M\cap S$ and $M\cap\bar S$ (disjoint), so $P(M\cap\bar S)=P(M)-P(M\cap S)=0.7-0.2=0.5=\dfrac12$. (The value $P(S)=0.3$ and $P(M\cup S)=0.8$ were not even needed: the data are consistent, since $0.7+0.3-0.2=0.8$.)", [r"Split $M$ into 'passes statistics' and 'fails statistics'."]))
    out.append(pr("sq-4b", r"**Q4 b.** Two-thirds of the students in a class are boys, the rest are girls. The probability that a girl gets a first class is $0.25$ and that a boy gets one is $0.28$. A student is chosen at random and found to have the first class. What is the probability that she is a girl?", sp.Rational(25, 81),
                  r"Total probability: $P(F)=\dfrac23\cdot0.28+\dfrac13\cdot0.25=\dfrac{14}{75}+\dfrac1{12}=\dfrac{56+25}{300}=\dfrac{27}{100}$. Bayes: $P(\text{girl}\mid F)=\dfrac{\frac13\cdot0.25}{27/100}=\dfrac{1/12}{27/100}=\dfrac{100}{324}=\dfrac{25}{81}$.", [r"First $P(F)$ by total probability, then Bayes."]))
    return out


def register() -> None:
    from toolkit import add_extra

    ex1 = exset("sheet-discrete-moments", "Moments, shape and the moment generating function of a discrete variable (exercise sheet).", discrete_rv_items(), format=FMT, source=SOURCE)
    add_extra(f"{M2}/u01-discrete/l03-moments-skewness-and-the-mgf", ex1, SCRIPT, orphan=True)
    add_extra(f"{M2}/u02-continuous/l03-moments-and-shape-of-a-density", exset("sheet-continuous", "Densities, distribution functions and moments (exercise sheet).", continuous_rv_items(), format=FMT, source=SOURCE), SCRIPT, orphan=True)
    add_extra(f"{M2}/u01-discrete/l02-binomial-geometric-poisson", exset("sheet-binomial-dist", "Binomial distributions (exercise sheet).", binomial_items(), format=FMT, source=SOURCE), SCRIPT)
    add_extra(f"{M2}/u01-discrete/l02-binomial-geometric-poisson", exset("sheet-poisson", "Poisson distributions (exercise sheet).", poisson_items(), format=FMT, source=SOURCE), SCRIPT)
    add_extra(f"{M2}/u02-continuous/l02-uniform-exponential-normal", exset("sheet-exp-normal", "Exponential and normal distributions (exercise sheet).", exp_normal_items(), format=FMT, source=SOURCE), SCRIPT)
    add_extra(f"{M1}/u03-practice-exam/l01-mid-summer-exam-2025-2026", exset("exam", "The mid-summer exam STAT8225, solved question by question.", exam_items(), format=FMT, source=EXAM), SCRIPT, orphan=True)


def build() -> None:
    pass
