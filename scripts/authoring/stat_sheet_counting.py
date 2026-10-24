"""Course 3 (stat): the counting part of the STAT8225 exercise sheet (permutations, combinations, the binomial formula).

Every key is computed with SymPy and cross-checked by brute force (itertools) where the numbers are small. Printed errors of the sheet are
corrected and said in the `note` of the exercise."""

from __future__ import annotations

import itertools
import math

import sympy as sp
from stat_course import C, F, R, pr
from toolkit import ex, exset

SOURCE = "STAT8225 exercise sheet, T. Hakizimana"
SCRIPT = "stat_sheet_counting.py"
M1 = "stat/m01-probability"
n_ = sp.Symbol("n", integer=True, positive=True)
x, y, b, c, k = (sp.Symbol(s, real=True) for s in ("x", "y", "b", "c", "k"))
FMT = "Type a whole number, a fraction, or an expression such as `2*x^3`. Use `n` for the unknown number of sides."


def P(n: int, r: int) -> int:
    return math.perm(n, r)


def mc(id_: str, stmt: str, options: list[str], correct: int, hint: str, solution: str) -> dict:
    return ex(id_, stmt, "multiple_choice", str(correct + 1), choices=[{"text": o, "value": str(i + 1)} for i, o in enumerate(options)], correctIndex=correct, hints=[hint], solution=solution)


# --- lesson l03: permutations, combinations and equations in n ---------------------------------------------------------------------------
def solve_n(expr: sp.Expr, lo: int = 1, hi: int = 200) -> list[int]:
    """The integers n in [lo, hi] for which expr(n) == 0 (exact), found by testing, so that no solution can be missed or invented."""
    return [m for m in range(lo, hi + 1) if sp.simplify(expr.subs(n_, m)) == 0]


def perm_comb_items() -> list[dict]:
    it: list[dict] = []
    # direct values
    for i, (a, r_) in enumerate(((8, 3), (10, 4), (12, 2)), 1):
        v = P(a, r_)
        assert v == len(list(itertools.permutations(range(a), r_))) if a <= 8 else True
        it.append(pr(f"pc-p{i}", rf"Compute ${{}}_{{{a}}}P_{{{r_}}}$, the number of arrangements of {r_} objects taken from {a}.", v,
                     rf"${{}}_{{{a}}}P_{{{r_}}}=\dfrac{{{a}!}}{{{a - r_}!}}={'\\cdot'.join(str(a - j) for j in range(r_))}={v}$.",
                     [r"${}_nP_r=n(n-1)\cdots(n-r+1)$: $r$ factors, starting at $n$."]))
    for i, (a, r_) in enumerate(((9, 4), (15, 3), (20, 2)), 1):
        v = C(a, r_)
        it.append(pr(f"pc-c{i}", rf"Compute $\dbinom{{{a}}}{{{r_}}}$.", v, rf"$\dbinom{{{a}}}{{{r_}}}=\dfrac{{{a}!}}{{{r_}!\,{a - r_}!}}={v}$.", [r"$\dbinom nr=\dfrac{n!}{r!\,(n-r)!}$."]))

    # 1 ii) 56P(n+6) : 54P(n+3) = 3088 : 1, printed; the ratio 30800 : 1 is what gives an integer n
    def ratio_ii(m: int, target: int) -> bool:
        return sp.Rational(P(56, m + 6), P(54, m + 3)) == target

    sol = [m for m in range(1, 49) if ratio_ii(m, 30800)]
    assert sol == [41] and not any(ratio_ii(m, 3088) for m in range(1, 49))
    it.append(pr("pc-1ii", r"Find $n$ if ${}_{56}P_{n+6}:{}_{54}P_{n+3}=30800:1$.", 41,
                 r"Write the two arrangements with factorials: ${}_{56}P_{n+6}=\dfrac{56!}{(50-n)!}$ and ${}_{54}P_{n+3}=\dfrac{54!}{(51-n)!}$. Their ratio is $\dfrac{56!}{54!}\cdot\dfrac{(51-n)!}{(50-n)!}=56\cdot55\cdot(51-n)=3080\,(51-n)$. Set it equal to $30800$: $51-n=10$, so $n=41$. Check: $n+6=47\le56$ and $n+3=44\le54$, so both arrangements exist.",
                 [r"$\dfrac{56!}{54!}=56\cdot55$.", r"$\dfrac{(51-n)!}{(50-n)!}=51-n$."],
                 note="The sheet prints the ratio as $3088:1$. With $3088:1$ there is no whole number $n$ (the equation $3080(51-n)=3088$ has no integer solution); the zeros were lost in printing and the intended ratio is $30800:1$."))

    # 1 iii) C(n+2,8) : (n-2)P4 = 57:16
    def ratio_iii(m: int) -> bool:
        return m >= 8 and m - 2 >= 4 and sp.Rational(math.comb(m + 2, 8), P(m - 2, 4)) == sp.Rational(57, 16)

    sol3 = [m for m in range(1, 200) if ratio_iii(m)]
    if sol3:
        v = sol3[0]
        it.append(pr("pc-1iii", r"Find $n$ if $\dbinom{n+2}{8}:{}_{n-2}P_4=57:16$.", v,
                     rf"$\dbinom{{n+2}}{{8}}=\dfrac{{(n+2)!}}{{8!\,(n-6)!}}$ and ${{}}_{{n-2}}P_4=(n-2)(n-3)(n-4)(n-5)$. The ratio simplifies and the equation gives $n={v}$.", ["Write both sides with factorials and cancel."]))

    # 1 iv) 2 C(n,3) = 20/3 C(n,2)
    s4 = solve_n(2 * sp.binomial(n_, 3) - sp.Rational(20, 3) * sp.binomial(n_, 2), 3)
    assert s4 == [12], s4
    it.append(pr("pc-1iv", r"Find $n$ if $2\dbinom n3=\dfrac{20}3\dbinom n2$.", 12,
                 r"$\dbinom n3=\dfrac{n(n-1)(n-2)}{6}$ and $\dbinom n2=\dfrac{n(n-1)}{2}$. The equation becomes $\dfrac{n(n-1)(n-2)}{3}=\dfrac{10\,n(n-1)}{3}$. Divide both sides by $\dfrac{n(n-1)}{3}$ (it is not $0$ for $n\ge3$): $n-2=10$, so $n=12$.",
                 [r"Write the binomial coefficients as products and divide by $n(n-1)$."]))

    # 1 v) C(28,2n) : C(24,2n-4) = 225 : 11
    def ratio_v(m: int) -> bool:
        return 2 * m <= 28 and 2 * m - 4 >= 0 and sp.Rational(math.comb(28, 2 * m), math.comb(24, 2 * m - 4)) == sp.Rational(225, 11)

    sol5 = [m for m in range(1, 15) if ratio_v(m)]
    assert sol5, "no integer n for 1 v)"
    v5 = sol5[0]
    it.append(pr("pc-1v", r"Find $n$ if $\dbinom{28}{2n}:\dbinom{24}{2n-4}=225:11$.", v5,
                 rf"With $m=2n$: $\dbinom{{28}}{{m}}=\dfrac{{28!}}{{m!\,(28-m)!}}$ and $\dbinom{{24}}{{m-4}}=\dfrac{{24!}}{{(m-4)!\,(28-m)!}}$. The ratio is $\dfrac{{28\cdot27\cdot26\cdot25}}{{m(m-1)(m-2)(m-3)}}=\dfrac{{225}}{{11}}$, so $m(m-1)(m-2)(m-3)=\dfrac{{11\cdot491400}}{{225}}={11 * 491400 // 225}$, which holds for $m={2 * v5}$. So $n={v5}$.",
                 [r"The factor $(28-m)!$ cancels in the quotient.", r"$\dfrac{28!}{24!}=28\cdot27\cdot26\cdot25$."]))

    # 1 vi) C(n, n-4) = 70
    s6 = solve_n(sp.binomial(n_, n_ - 4) - 70, 4, 60)
    assert s6 == [8], s6
    it.append(pr("pc-1vi", r"Find $n$ if $\dbinom{n}{n-4}=70$.", 8,
                 r"$\dbinom n{n-4}=\dbinom n4$ (choosing which $4$ objects to leave out). So $\dfrac{n(n-1)(n-2)(n-3)}{24}=70$, i.e. $n(n-1)(n-2)(n-3)=1680=8\cdot7\cdot6\cdot5$, hence $n=8$.",
                 [r"Use $\dbinom nr=\dbinom n{n-r}$."]))

    # 2) the system
    sols = [(xx, yy) for yy in range(1, 30) for xx in range(1, yy + 1) if P(yy, xx) == (P(yy, xx + 1) if xx + 1 <= yy else None) and math.comb(yy, xx) == math.comb(yy, xx - 1)]
    assert sols == [(2, 3)], sols
    sys_text = r"$\begin{cases}{}_yP_x={}_yP_{x+1}\\[2pt]\dbinom yx=\dbinom y{x-1}\end{cases}$"
    sol_sys = r"First equation: $\dfrac{y!}{(y-x)!}=\dfrac{y!}{(y-x-1)!}$, so $(y-x)!=(y-x-1)!$, which is true only when $y-x=1$. Second equation: $\dbinom yx=\dbinom y{x-1}$ means $x+(x-1)=y$ (two coefficients of $\dbinom y\cdot$ are equal only when the lower numbers add up to $y$), so $y=2x-1$. Then $x+1=2x-1$ gives $x=2$ and $y=3$. Check: ${}_3P_2=6={}_3P_3$ and $\dbinom32=3=\dbinom31$."
    it.append(pr("pc-2x", rf"Solve the system {sys_text} Find $x$.", 2, sol_sys, [r"$(y-x)!=(y-x-1)!$ only when $y-x=1$.", r"$\dbinom ya=\dbinom yb$ with $a\ne b$ needs $a+b=y$."]))
    it.append(pr("pc-2y", rf"Solve the system {sys_text} Find $y$.", 3, sol_sys, [r"First find $x$."]))

    # 8) NUMBER, 4-letter words
    v = P(6, 4)
    assert v == len(list(itertools.permutations("NUMBER", 4)))
    it.append(pr("pc-8", r"How many different $4$-letter words, with or without meaning, can be formed from the letters of the word NUMBER?", v,
                 r"NUMBER has $6$ different letters. A $4$-letter word is an arrangement of $4$ of them, with the order mattering: ${}_6P_4=6\cdot5\cdot4\cdot3=360$.", ["The letters are all different; the order matters."]))
    # 9) PROBABILITY, STATISTICS
    v = F(11) / (F(2) * F(2))
    it.append(pr("pc-9a", r"How many different arrangements are there of the letters of the word PROBABILITY?", v,
                 r"PROBABILITY has $11$ letters; B appears twice and I twice, all the others once. Divide $11!$ by $2!\,2!$: $\dfrac{39\,916\,800}{4}=9\,979\,200$.", ["Divide by the factorial of each repeated letter."]))
    v = F(10) / (F(3) * F(3) * F(2))
    it.append(pr("pc-9b", r"How many different arrangements are there of the letters of the word STATISTICS?", v,
                 r"STATISTICS has $10$ letters: S three times, T three times, I twice, A and C once each. $\dfrac{10!}{3!\,3!\,2!}=\dfrac{3\,628\,800}{72}=50\,400$.", ["Count each letter: S, T, A, I, C."]))
    # 10) 6 persons
    it.append(pr("pc-10a", r"In how many ways can $6$ persons be arranged in a line?", F(6), r"$6!=720$.", ["Arrangements of all the persons."]))
    it.append(pr("pc-10b", r"In how many ways can $6$ persons be arranged in a circle (only the order around the circle counts, a rotation is the same arrangement)?", F(5),
                 r"Fix one person: the other $5$ can be arranged in $5!=120$ ways. Equivalently $\dfrac{6!}{6}=120$, because each circular arrangement appears $6$ times in the line count (one for each rotation).", ["Fix one person to remove the rotations."]))
    # 11) 4 brothers and 3 sisters
    together = F(5) * F(3)
    it.append(pr("pc-11a", r"A family of $4$ brothers and $3$ sisters is arranged in a row for a photograph. In how many ways can they be seated if all the sisters sit together?", together,
                 r"Glue the $3$ sisters into one block. Now there are $4$ brothers and $1$ block: $5!=120$ arrangements. Inside the block the sisters can be ordered in $3!=6$ ways. Total $120\cdot6=720$.", ["Treat the sisters as one block, then arrange the block inside."]))
    it.append(pr("pc-11b", r"The same family: in how many ways can they be seated if the sisters are not all together?", F(7) - together,
                 r"All arrangements: $7!=5040$. Those with the sisters together: $720$ (previous question). So $5040-720=4320$.", ["Subtract the arrangements where the sisters are together."]))
    # 12) triangles of a hexagon
    it.append(pr("pc-12", r"How many triangles can be formed by joining the vertices of a hexagon?", C(6, 3), r"A triangle is a choice of $3$ vertices out of $6$ (no three vertices of a hexagon are on a line): $\dbinom63=20$.", ["A triangle is a set of three vertices."]))
    # 13) diagonals
    diag = n_ * (n_ - 3) / 2
    for m in range(4, 12):
        assert diag.subs(n_, m) == math.comb(m, 2) - m
    it.append(ex("pc-13", r"How many diagonals has a polygon with $n$ sides? Give a formula in $n$.", "expression", "n*(n-3)/2", variables=["n"],
                 hints=[r"Count all the segments joining two vertices, then remove the $n$ sides."],
                 solution=r"Two vertices determine a segment: $\dbinom n2=\dfrac{n(n-1)}2$ segments. Among them $n$ are sides of the polygon. The diagonals are the others: $\dfrac{n(n-1)}2-n=\dfrac{n(n-1)-2n}{2}=\dfrac{n(n-3)}2$. Check with the hexagon: $\dfrac{6\cdot3}2=9$."))
    # 14) selections of books
    it.append(pr("pc-14a", r"How many different selections of $4$ books can be made from $10$ different books if two particular books are always selected?", C(8, 2),
                 r"The two particular books are in. We still choose $2$ books among the other $8$: $\dbinom82=28$.", ["Only the remaining places need choosing."]))
    it.append(pr("pc-14b", r"How many different selections of $4$ books can be made from $10$ different books if two particular books are never selected?", C(8, 4),
                 r"The two particular books are out: choose $4$ books among the other $8$: $\dbinom84=70$.", ["Remove the two books first."]))
    # 16) committee
    it.append(pr("pc-16a", r"In how many ways can a committee of $4$ people be chosen from a panel of $10$ if a certain person must be on the committee?", C(9, 3),
                 r"That person is in. Choose the other $3$ members among the remaining $9$ people: $\dbinom93=84$.", ["Choose the remaining places."]))
    it.append(pr("pc-16b", r"In how many ways can a committee of $4$ people be chosen from a panel of $10$ if a certain person must not be on the committee?", C(9, 4),
                 r"That person is out. Choose $4$ among the other $9$: $\dbinom94=126$.", ["Remove that person first."]))
    # a calculation multiple-choice question: the value of n must be worked out
    it.append(mc("pc-m1", r"Which value of $n$ satisfies $\dbinom n2=45$?", ["$8$", "$9$", "$10$", "$11$"], 2, r"$\dbinom n2=\dfrac{n(n-1)}{2}$.",
                 r"$\dfrac{n(n-1)}2=45$ gives $n(n-1)=90=10\cdot9$, so $n=10$. (For $n=9$ we get $36$, for $n=11$ we get $55$.)"))
    it.append(mc("pc-m2", r"In how many ways can $5$ people sit in a row if two of them, Ann and Ben, must not sit next to each other?", ["$48$", "$72$", "$96$", "$120$"], 1,
                 r"Count all arrangements, then subtract those where Ann and Ben are together.", r"All arrangements: $5!=120$. With Ann and Ben together: $4!\cdot2=48$. So $120-48=72$."))
    return it


# --- lesson l04: the general term, the middle term and the constant term ---------------------------------------------------------------------
def term(a_part: sp.Expr, b_part: sp.Expr, n: int, kk: int) -> sp.Expr:
    return sp.expand(sp.binomial(n, kk) * a_part ** (n - kk) * b_part**kk)


def general_term_items() -> list[dict]:
    it: list[dict] = []
    # 3) the identities, as the numerical values they predict
    v = sp.binomial(10, 5)
    assert v == sum(sp.binomial(5, i) ** 2 for i in range(6))
    it.append(pr("gt-3i", r"The identity $\dbinom{2n}{n}=\dbinom n0^2+\dbinom n1^2+\cdots+\dbinom nn^2$ is true for every $n$. Use it with $n=5$ to find $\displaystyle\sum_{k=0}^{5}\dbinom5k^2$.", v,
                 r"The sum equals $\dbinom{2n}{n}=\dbinom{10}5=252$. **Why the identity holds:** compare the coefficient of $x^n$ in $(1+x)^{2n}=(1+x)^n(1+x)^n$. On the left it is $\dbinom{2n}n$. On the right, multiply $\sum\dbinom nj x^j$ by $\sum\dbinom nk x^k$: the terms with $j+k=n$ give $\sum_k\dbinom n{n-k}\dbinom nk=\sum_k\dbinom nk^2$.", ["Compare the coefficient of $x^n$ in $(1+x)^n(1+x)^n$."]))
    v = 3**4
    assert v == sum(2**i * sp.binomial(4, i) for i in range(5))
    it.append(pr("gt-3ii", r"The identity $3^n=\dbinom n0+2\dbinom n1+4\dbinom n2+\cdots+2^n\dbinom nn$ holds for every $n$. Use it to find $\displaystyle\sum_{k=0}^{4}2^k\dbinom4k$.", v,
                 r"The sum is $3^4=81$. **Proof of the identity:** the binomial theorem with $a=1$, $b=2$ gives $(1+2)^n=\sum_k\dbinom nk1^{n-k}2^k=\sum_k2^k\dbinom nk$.", ["Binomial theorem with $a=1$ and $b=2$."]))
    v = 4**3
    assert v == sum(3**i * sp.binomial(3, i) for i in range(4))
    it.append(pr("gt-3iii", r"The identity $4^n=\dbinom n0+3\dbinom n1+9\dbinom n2+\cdots+3^n\dbinom nn$ holds for every $n$. Use it to find $\displaystyle\sum_{k=0}^{3}3^k\dbinom3k$.", v,
                 r"The sum is $4^3=64$. **Proof:** the binomial theorem with $a=1$, $b=3$ gives $(1+3)^n=\sum_k3^k\dbinom nk$.", ["Binomial theorem with $a=1$ and $b=3$."]))
    v = 4**5
    assert v == sum(3**i * sp.binomial(5, i) for i in range(6)) == sum(sp.binomial(5, i) for i in range(6)) ** 2
    it.append(pr("gt-3iv", r"The identity $\displaystyle\sum_{k=0}^n3^k\dbinom nk=\left[\sum_{k=0}^n\dbinom nk\right]^2$ holds for every $n$. For $n=5$ find the value of both sides.", v,
                 r"The left side is $4^5=1024$ (binomial theorem with $a=1$, $b=3$). The bracket on the right is $2^5=32$ (binomial theorem with $a=b=1$) and $32^2=1024$. In general $4^n=(2^n)^2$, which is the identity.", ["The left side is $(1+3)^n$, the bracket is $(1+1)^n$."]))

    # 4) the middle term
    cases4 = [
        ("pi", 3 * x - sp.Rational(2, 3) * x**2, 8, 4, r"\left(3x-\dfrac{2}{3}x^2\right)^{8}", "one"),
        ("pii", x - 2 * y, 13, 6, r"(x-2y)^{13}", "two"),
        ("piii", x / b + b / x, 16, 8, r"\left(\dfrac xb+\dfrac bx\right)^{16}", "one"),
        ("piv", 3 * x - 2 / x**2, 17, 8, r"\left(3x-\dfrac{2}{x^2}\right)^{17}", "two"),
    ]
    for tag, base, n, kk, tex_, kind in cases4:
        parts = base.as_ordered_terms()
        a_part, b_part = parts[0], parts[1]
        if tag == "pi":
            a_part, b_part = 3 * x, -sp.Rational(2, 3) * x**2
        elif tag == "pii":
            a_part, b_part = x, -2 * y
        elif tag == "piii":
            a_part, b_part = x / b, b / x
        else:
            a_part, b_part = 3 * x, -2 / x**2
        assert sp.expand(a_part + b_part - base) == 0
        if kind == "one":
            t5 = sp.simplify(term(a_part, b_part, n, kk))
            ord_ = kk + 1
            vars_ = sorted({s.name for s in t5.free_symbols})
            it.append(ex(f"gt-4{tag}", rf"Find the middle term in the expansion of ${tex_}$.", "expression", str(t5).replace("**", "^"), variables=vars_,
                         hints=[rf"There are ${n + 1}$ terms, so the middle one is the term number ${ord_}$.", r"The general term is $T_{k+1}=\dbinom nk a^{n-k}b^k$."],
                         solution=rf"The expansion has ${n}+1={n + 1}$ terms, so the middle term is the ${ord_}$th, $T_{{{ord_}}}$, with $k={kk}$. With $a={sp.latex(a_part)}$ and $b={sp.latex(b_part)}$: $T_{{{ord_}}}=\dbinom{{{n}}}{{{kk}}}a^{{{n - kk}}}b^{{{kk}}}={sp.latex(t5)}$."))
        else:
            for which, kk2 in (("first", kk), ("second", kk + 1)):
                tt = sp.simplify(term(a_part, b_part, n, kk2))
                vars_ = sorted({s.name for s in tt.free_symbols})
                it.append(ex(f"gt-4{tag}-{which}", rf"The expansion of ${tex_}$ has two middle terms. Find the {which} one.", "expression", str(tt).replace("**", "^"), variables=vars_,
                             hints=[rf"$n={n}$ is odd: there are ${n + 1}$ terms, and the two middle ones are the terms number ${n // 2 + 1}$ and ${n // 2 + 2}$.", r"$T_{k+1}=\dbinom nk a^{n-k}b^k$."],
                             solution=rf"With $n={n}$ (odd) there are ${n + 1}$ terms and two middle terms: the ${n // 2 + 1}$th and the ${n // 2 + 2}$th. The {which} one has $k={kk2}$: $T_{{{kk2 + 1}}}=\dbinom{{{n}}}{{{kk2}}}a^{{{n - kk2}}}b^{{{kk2}}}={sp.latex(tt)}$."))
    # v) (1+x)^2n, vi) (1+1/(2x))^2n, vii) (x-1/x)^2n : the middle term is the term number n+1, k = n; checked for n = 4
    for tag, base, a_part, b_part, tex_, closed in (
        ("pv", 1 + x, sp.Integer(1), x, r"(1+x)^{2n}", "C(2n,n) x^n"),
        ("pvi", 1 + 1 / (2 * x), sp.Integer(1), 1 / (2 * x), r"\left(1+\dfrac1{2x}\right)^{2n}", "C(2n,n) / (2x)^n"),
        ("pvii", x - 1 / x, x, -1 / x, r"\left(x-\dfrac1x\right)^{2n}", "(-1)^n C(2n,n)"),
    ):
        nn = 3
        tm = sp.simplify(term(a_part, b_part, 2 * nn, nn))
        it.append(ex(f"gt-4{tag}", rf"Find the middle term in the expansion of ${tex_}$ for $n=3$ (so the power is $6$).", "expression", str(tm).replace("**", "^"), variables=["x"],
                     hints=[r"The power is $6$: there are $7$ terms, the middle one is the fourth ($k=3$).", r"In general the middle term of a power $2n$ is the term number $n+1$, with $k=n$."],
                     solution=rf"With power $2n=6$ there are $7$ terms; the middle one is $T_4$ ($k=3$): $T_4=\dbinom63a^3b^3={sp.latex(tm)}$. In general the power $2n$ has $2n+1$ terms and the middle one is $T_{{n+1}}=\dbinom{{2n}}n a^nb^n$."))
    # 5) the constant term
    def const_term(a_part: sp.Expr, b_part: sp.Expr, n: int) -> tuple[int, sp.Expr] | None:
        for kk in range(n + 1):
            tt = sp.simplify(term(a_part, b_part, n, kk))
            if not tt.has(x):
                return kk, tt
        return None

    r1 = const_term(2 * x**2, 1 / x, 12)
    assert r1 == (8, 7920), r1
    it.append(pr("gt-5i", r"Find the constant term in the expansion of $\left(2x^2+\dfrac1x\right)^{12}$.", 7920,
                 r"$T_{k+1}=\dbinom{12}k(2x^2)^{12-k}\left(\dfrac1x\right)^k=\dbinom{12}k2^{12-k}x^{24-2k-k}=\dbinom{12}k2^{12-k}x^{24-3k}$. The term is constant when $24-3k=0$, i.e. $k=8$. Then $T_9=\dbinom{12}82^4=495\cdot16=7920$.", [r"Find the power of $x$ in the general term and set it equal to $0$."]))
    r2 = const_term(sp.Rational(4, 3) * x**2, -sp.Rational(3, 2) / x, 9)
    assert r2 == (6, 2268), r2
    it.append(pr("gt-5ii", r"Find the constant term in the expansion of $\left(\dfrac{4x^2}3-\dfrac3{2x}\right)^{9}$.", 2268,
                 r"$T_{k+1}=\dbinom9k\left(\dfrac{4x^2}3\right)^{9-k}\left(-\dfrac3{2x}\right)^k$ has the power $x^{2(9-k)-k}=x^{18-3k}$. Constant when $k=6$: $T_7=\dbinom96\left(\dfrac43\right)^3\left(-\dfrac32\right)^6=84\cdot\dfrac{64}{27}\cdot\dfrac{729}{64}=84\cdot27=2268$.", [r"The power of $x$ is $2(9-k)-k$."]))
    assert const_term(9 * x, -b / (c * x**2), 17) is None
    it.append(mc("gt-5iii", r"Does the expansion of $\left(9x-\dfrac{b}{cx^2}\right)^{17}$ have a constant term?", ["Yes, for $k=5$", "Yes, for $k=6$", "No, there is no constant term", "Yes, for $k=17$"], 2,
                 r"The general term has $x^{(17-k)-2k}=x^{17-3k}$.", r"The power of $x$ in $T_{k+1}$ is $(17-k)-2k=17-3k$. It is $0$ only if $3k=17$, but $17$ is not a multiple of $3$, so no whole number $k$ works: the expansion has no constant term."))
    # a similar one, to practise the method
    r3 = const_term(x**2, 2 / x, 9)
    assert r3 is not None
    it.append(pr("gt-5x", r"Find the constant term in the expansion of $\left(x^2+\dfrac2x\right)^{9}$.", r3[1],
                 rf"$T_{{k+1}}=\dbinom9kx^{{2(9-k)}}\left(\dfrac2x\right)^k=\dbinom9k2^kx^{{18-3k}}$. Constant when $k=6$: $T_7=\dbinom96\cdot2^6=84\cdot64={r3[1]}$.", ["The power of $x$ is $2(9-k)-k$."]))
    # 6) ratio of coefficients
    r_ = [rr for rr in range(1, 21) if sp.Rational(math.comb(20, rr - 1), math.comb(20, rr)) == sp.Rational(1, 6)]
    assert r_ == [3], r_
    it.append(pr("gt-6", r"In the expansion of $(1+x)^{20}$ the coefficients of the $r$th and the $(r+1)$th terms are in the ratio $1:6$. Find $r$.", 3,
                 r"The $r$th term has the coefficient $\dbinom{20}{r-1}$ and the $(r+1)$th term $\dbinom{20}r$. Their ratio is $\dfrac{\binom{20}{r-1}}{\binom{20}r}=\dfrac{r}{21-r}$ (because $\dbinom{20}{r}=\dbinom{20}{r-1}\cdot\dfrac{21-r}{r}$). Set $\dfrac r{21-r}=\dfrac16$: $6r=21-r$, so $r=3$.",
                 [r"$\dbinom{20}r=\dbinom{20}{r-1}\cdot\dfrac{20-(r-1)}{r}$."]))
    # 7) arithmetic progression
    n7 = [nn for nn in range(6, 80) if 2 * math.comb(nn, 5) == math.comb(nn, 4) + math.comb(nn, 6)]
    assert n7 == [7, 14], n7
    sol7 = (r"The coefficients of the $5$th, $6$th and $7$th terms are $\dbinom n4$, $\dbinom n5$, $\dbinom n6$. They are in arithmetic progression when $2\dbinom n5=\dbinom n4+\dbinom n6$. Divide by $\dbinom n4$: $\dbinom n5=\dbinom n4\cdot\dfrac{n-4}5$ and $\dbinom n6=\dbinom n4\cdot\dfrac{(n-4)(n-5)}{30}$. So $\dfrac{2(n-4)}5=1+\dfrac{(n-4)(n-5)}{30}$, i.e. $12(n-4)=30+(n-4)(n-5)$, which gives $n^2-21n+98=0=(n-7)(n-14)$. Hence $n=7$ or $n=14$.")
    it.append(pr("gt-7a", r"The coefficients of the $5$th, $6$th and $7$th terms in the expansion of $(1+x)^n$ are in arithmetic progression. Find the smaller possible value of $n$.", 7, sol7, [r"Arithmetic progression: the middle term is the average of the others."]))
    it.append(pr("gt-7b", r"The coefficients of the $5$th, $6$th and $7$th terms in the expansion of $(1+x)^n$ are in arithmetic progression. Find the larger possible value of $n$.", 14, sol7, [r"The equation in $n$ has two solutions."]))
    return it


def register() -> None:
    from toolkit import add_extra

    add_extra(f"{M1}/u01-counting/l03-permutations-and-combinations-in-n", exset("sheet-counting", "Permutations, combinations and arrangements (exercise sheet).", perm_comb_items(), format=FMT, source=SOURCE), SCRIPT, orphan=True)
    add_extra(f"{M1}/u01-counting/l04-general-term-middle-and-constant-terms", exset("sheet-binomial", "The binomial formula: identities, middle terms, constant terms (exercise sheet).", general_term_items(), format=FMT, source=SOURCE), SCRIPT, orphan=True)


def build() -> None:
    pass
