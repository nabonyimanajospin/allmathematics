"""More practice for Course 2, Module 4: ordinary differential equations.

Each equation is built as a SymPy expression; the statement (LaTeX) and the residual given to the engine come from the same
expression, the solution is computed (integrating factors, dsolve, potentials) and then verified by substitution."""

from __future__ import annotations

import sympy as sp
from mvc_m04 import sol
from toolkit import P, add_extra, eng, ex, exset_plain, tex

SCRIPT = "more_mvc_c.py"
U1 = "mvc/m04-ode/u01-first-order"
U2 = "mvc/m04-ode/u02-second-order"

x = sp.Symbol("x", positive=True)
Y = sp.Symbol("y")
D1 = sp.Symbol("y'")
D2 = sp.Symbol("y''")
C, C1, C2 = sp.symbols("C C1 C2")


def residual(e: sp.Expr) -> str:
    return eng(e).replace("y''", "y2").replace("y'", "y1")


def otex(e: sp.Expr) -> str:
    """LaTeX that keeps the order in which the terms were written (y'' before y' before y)."""
    s = sp.latex(e, ln_notation=True, inv_trig_style="full", mul_symbol=None, order="none")
    return s


def ordered(*terms: sp.Expr) -> sp.Expr:
    return sp.Add(*[t for t in terms if t != 0], evaluate=False)


def stmt(lhs: sp.Expr, rhs: sp.Expr, cond: str = "") -> str:
    return f"${otex(lhs)}={otex(rhs)}${cond}"


def check_implicit(relation: sp.Expr, eqn: sp.Expr, label: str) -> None:
    """relation = F(x, y) (the constant C already isolated): F_x + F_y y' must vanish when y' solves the equation."""
    yf = sp.Function("yf")
    F = relation.subs(Y, yf(x))
    ode = eqn.subs({D2: sp.diff(yf(x), x, 2), D1: sp.diff(yf(x), x), Y: yf(x)})
    dy = sp.solve(sp.diff(F, x), sp.diff(yf(x), x))
    assert dy, label
    resid = sp.simplify(ode.subs(sp.diff(yf(x), x), dy[0]))
    assert resid == 0, (label, resid)


# --- separable ------------------------------------------------------------------------------------------------------------------
def separable_items() -> list[dict]:
    items = []

    def one(i: str, lhs, rhs, answer: str, solution: str, hint: str, cond: tuple | None = None, tex_cond: str = "", sample=None) -> None:
        eqn = lhs - rhs
        conditions = [(cond[0], cond[1], 0)] if cond else None
        items.append(sol(f"mp-sep-{i}", stmt(lhs, rhs, tex_cond), residual(eqn), answer, solution, [hint], conditions=conditions, sample=sample))

    one("1", D1, x * Y, "y = C*e^(x^2/2)", r"$\dfrac{dy}{y}=x\,dx$ gives $\ln|y|=\dfrac{x^2}2+c$, so $y=Ce^{x^2/2}$.", r"Write $y'=\dfrac{dy}{dx}$ and separate: $\dfrac{dy}{y}=x\,dx$.")
    one("2", D1, x * Y**2, "y = -2/(x^2 + C)", r"$\dfrac{dy}{y^2}=x\,dx$ gives $-\dfrac1y=\dfrac{x^2}2+c$, so $y=-\dfrac{2}{x^2+C}$ (with $C=2c$).", r"Separate: $\dfrac{dy}{y^2}=x\,dx$.", sample=(0.6, 1.9))
    one("3", D1, sp.exp(x - Y), "y = ln(e^x + C)", r"$e^{y}\,dy=e^{x}\,dx$ gives $e^y=e^x+C$, so $y=\ln(e^x+C)$.", r"$e^{x-y}=e^xe^{-y}$: multiply by $e^y$.", sample=(0.6, 1.9))
    one("4", x * D1, Y * sp.log(Y), "y = e^(C*x)", r"$\dfrac{dy}{y\ln y}=\dfrac{dx}{x}$ gives $\ln|\ln y|=\ln|x|+c$, so $\ln y=Cx$ and $y=e^{Cx}$.", r"$\int\dfrac{dy}{y\ln y}=\ln|\ln y|$.", sample=(0.6, 1.9))
    one("5", D1, 2 * x * Y, "y = 3*e^(x^2)", r"$\dfrac{dy}y=2x\,dx$ gives $y=Ce^{x^2}$. $y(0)=3$ gives $C=3$.", r"First find the general solution, then use $y(0)=3$.",
        cond=("0", "3"), tex_cond=r", $\ y(0)=3$")
    one("6", x * D1, Y, "y = 2*x", r"$\dfrac{dy}{y}=\dfrac{dx}{x}$ gives $y=Cx$. $y(1)=2$ gives $C=2$.", r"Separate the variables; then $y(1)=2$ fixes the constant.",
        cond=("1", "2"), tex_cond=r", $\ y(1)=2$", sample=(0.6, 1.9))
    one("7", D1, -Y**2, "y = 1/(x + 1)", r"$\dfrac{dy}{y^2}=-dx$ gives $-\dfrac1y=-x+c$, so $y=\dfrac{1}{x+C}$. $y(0)=1$ gives $C=1$.", r"$\int y^{-2}dy=-y^{-1}$.",
        cond=("0", "1"), tex_cond=r", $\ y(0)=1$", sample=(0.0, 1.9))
    return items


# --- homogeneous ---------------------------------------------------------------------------------------------------------------
def homogeneous_items() -> list[dict]:
    items = []
    v = sp.Symbol("v")

    def one(i: str, lhs, rhs, answer: str, rel: sp.Expr | None, solution: str, hint: str, cond=None, tex_cond: str = "", sample=None) -> None:
        eqn = lhs - rhs
        if rel is not None:
            check_implicit(rel, eqn, i)
        items.append(sol(f"mp-hom-{i}", stmt(lhs, rhs, tex_cond), residual(eqn), answer, solution, [hint], sample=sample, conditions=[(cond[0], cond[1], 0)] if cond else None))

    one("1", x * D1, x + Y, "y = x*ln(x) + C*x", None, r"Put $y=vx$: $xv'+v=1+v$, so $v'=\dfrac1x$ and $v=\ln x+C$. Hence $y=x\ln x+Cx$.", r"Put $y=vx$, so $y'=v+xv'$.", sample=(0.6, 1.9))
    one("2", D1, Y / x + sp.tan(Y / x), "sin(y/x) = C*x", sp.sin(Y / x) / x,
        r"Put $y=vx$: $xv'=\tan v$, so $\cot v\,dv=\dfrac{dx}{x}$ and $\ln|\sin v|=\ln|x|+c$. Hence $\sin\dfrac yx=Cx$.", r"With $y=vx$ the equation becomes $xv'=\tan v$.")
    one("3", D1, (x**2 + Y**2) / (2 * x * Y), "y^2 = x^2 + C*x", (Y**2 - x**2) / x,
        r"Put $y=vx$: $xv'=\dfrac{1-v^2}{2v}$, so $\dfrac{2v\,dv}{1-v^2}=\dfrac{dx}x$ and $-\ln|1-v^2|=\ln|x|+c$. Hence $x\left(1-v^2\right)=C'$, that is $y^2=x^2+Cx$.", r"Put $y=vx$ and separate $v$ from $x$.")
    one("4", D1, Y / x + (Y / x) ** 2, "y = -x/(ln(x) + C)", None, r"Put $y=vx$: $xv'=v^2$, so $-\dfrac1v=\ln x+C$ and $y=vx=-\dfrac{x}{\ln x+C}$.", r"With $y=vx$: $xv'=v^2$.", sample=(1.2, 1.9))
    one("5", x * D1, x + Y, "y = x*ln(x) + 2*x", None, r"As in part 1, $y=x\ln x+Cx$. $y(1)=2$ gives $C=2$.", r"First find the general solution, then use $y(1)=2$.",
        cond=("1", "2"), tex_cond=r", $\ y(1)=2$", sample=(0.6, 1.9))
    assert v is not None
    return items


# --- linear first order ---------------------------------------------------------------------------------------------------------
def linear_items() -> list[dict]:
    items = []

    def one(i: str, p: sp.Expr, q: sp.Expr, cond=None, tex_cond: str = "", sample=None) -> None:
        mu = sp.simplify(sp.exp(sp.integrate(p, x)))
        general = sp.simplify((sp.integrate(sp.simplify(mu * q), x) + C) / mu)
        if cond:
            c = sp.solve(general.subs(x, sp.Rational(cond[0])) - sp.Rational(cond[1]), C)[0]
            general = sp.simplify(general.subs(C, c))
        lhs, rhs = ordered(D1, p * Y), q
        eqn = lhs - rhs
        ans = f"y = {eng(general)}"
        items.append(sol(
            f"mp-lin-{i}", stmt(lhs, rhs, tex_cond), residual(eqn), ans,
            rf"The integrating factor is $\mu=e^{{\int P\,dx}}={tex(mu)}$. Then $(\mu y)'=\mu Q={tex(sp.simplify(mu * q))}$, and integrating gives $y={tex(general)}$.",
            [r"Find $\mu=e^{\int P\,dx}$ and multiply the equation by it."], sample=sample, conditions=[(cond[0], cond[1], 0)] if cond else None))

    one("1", sp.Integer(2), sp.exp(-x), sample=(0.2, 1.9))
    one("2", -1 / x, x**2, sample=(0.6, 1.9))
    one("3", 2 / x, x, sample=(0.6, 1.9))
    one("4", sp.Integer(1), x, cond=("0", "1"), tex_cond=r", $\ y(0)=1$", sample=(0.0, 1.9))
    return items


# --- Bernoulli ---------------------------------------------------------------------------------------------------------------------
def bernoulli_items() -> list[dict]:
    items = []

    def one(i: str, p: sp.Expr, q: sp.Expr, n: int, sample=(0.6, 1.9)) -> None:
        v = sp.Symbol("v")
        # v = y^(1-n):  v' + (1-n) P v = (1-n) Q
        pp, qq = (1 - n) * p, (1 - n) * q
        mu = sp.simplify(sp.exp(sp.integrate(pp, x)))
        vgen = sp.simplify((sp.integrate(sp.simplify(mu * qq), x) + C) / mu)
        lhs, rhs = ordered(D1, p * Y), q * Y**n
        eqn = lhs - rhs
        relation = Y ** (1 - n) - vgen  # = 0 for the solution; isolate C
        c_expr = sp.solve(sp.Eq(Y ** (1 - n), vgen), C)[0]
        check_implicit(c_expr, eqn, f"bern-{i}")
        left = "1/y" if n == 2 else f"y^{1 - n}"
        ans = f"{left} = {eng(vgen)}"
        items.append(sol(
            f"mp-ber-{i}", stmt(lhs, rhs), residual(eqn), ans,
            rf"Put $v=y^{{{1 - n}}}$. Dividing the equation by $y^{{{n}}}$ and using $v'=({1 - n})y^{{{-n}}}y'$ gives the linear equation ${otex(ordered(sp.Symbol(chr(118) + chr(39)), pp * sp.Symbol('v')))}={otex(qq)}$, with integrating factor $\mu={tex(mu)}$. Its solution is $v={tex(vgen)}$, that is ${tex(Y ** (1 - n))}={tex(vgen)}$.",
            [rf"Divide by $y^{{{n}}}$ and put $v=y^{{{1 - n}}}$: the equation becomes linear in $v$."], sample=sample))
        assert relation is not None and v is not None

    one("1", 1 / x, x, 2)
    one("2", sp.Integer(2), sp.Integer(1), 3)
    one("3", -1 / x, 1 / x, 2)
    one("4", sp.Integer(1), sp.exp(x), 2, sample=(0.2, 1.4))
    one("5", 2 / x, x**2, 2)
    one("6", sp.Integer(1), x, 2, sample=(0.2, 1.4))
    one("7", 1 / x, sp.Integer(1), 3)
    one("8", -2 * x, 2 * x, 2, sample=(0.2, 1.4))
    return items


# --- exact ---------------------------------------------------------------------------------------------------------------------------
def exact_items() -> list[dict]:
    items = []
    y_ = sp.Symbol("y_")

    def potential(i: str, phi: sp.Expr, cond=None, tex_cond: str = "") -> None:
        m = sp.simplify(sp.diff(phi, x))
        n = sp.simplify(sp.diff(phi, Y))
        eqn = m + n * D1
        assert sp.simplify(sp.diff(m, Y) - sp.diff(n, x)) == 0
        check_implicit(phi, eqn, f"exact-{i}")
        if cond:
            const = sp.simplify(phi.subs({x: sp.Rational(cond[0]), Y: sp.Rational(cond[1])}))
            ans = f"{eng(phi)} = {eng(const)}"
        else:
            ans = f"{eng(phi)} = C"
        items.append(sol(
            f"mp-exa-{i}", f"$\\left({otex(m)}\\right)dx+\\left({otex(n)}\\right)dy=0${tex_cond}", residual(eqn), ans,
            rf"$M_y={tex(sp.diff(m, Y))}=N_x$, so the equation is exact. From $\Phi_x=M$: $\Phi={tex(phi)}+g(y)$, and $\Phi_y=N$ gives $g'=0$. The solution is ${tex(phi)}=" + (tex(const) if cond else "C") + "$.",
            [r"Check $M_y=N_x$, then integrate $M$ in $x$ and match $N$."], conditions=[(cond[0], str(cond[1]) if False else cond[2], 0)] if cond else None))

    potential("1", x**2 * Y + Y**3)
    potential("2", x * Y + sp.exp(x))
    potential("3", x**3 + 3 * x * Y**2)
    potential("4", x**2 * Y + x * Y**2)
    potential("5", sp.sin(x) * Y + Y**2)
    potential("6", sp.exp(x) * Y + x**2)
    potential("7", x**2 + x * Y + Y**2, cond=("1", "1", "1"), tex_cond=r", $\ y(1)=1$")
    # is the equation exact?
    for k, (m, n) in enumerate([(2 * x * Y + 1, x**2 + 3), (Y * sp.exp(x), x * sp.exp(x)), (2 * x + Y, x + 3 * Y)], start=8):
        exact = sp.simplify(sp.diff(m, Y) - sp.diff(n, x)) == 0
        items.append(ex(
            f"mp-exa-{k}", rf"Is the equation $\left({otex(m)}\right)dx+\left({otex(n)}\right)dy=0$ exact?", "multiple_choice", "1" if exact else "2",
            choices=[{"text": "Yes, it is exact", "value": "1"}, {"text": "No, it is not exact", "value": "2"}], correctIndex=0 if exact else 1,
            hints=[r"Compare $M_y$ and $N_x$."],
            solution=rf"$M_y={tex(sp.diff(m, Y))}$ and $N_x={tex(sp.diff(n, x))}$. " + ("They are equal, so the equation is exact." if exact else "They are different, so the equation is not exact."),
        ))
    assert y_ is not None
    return items


# --- second order, constant coefficients ---------------------------------------------------------------------------------------------
def const_items() -> list[dict]:
    items = []
    f = sp.Function("f")

    def one(i: str, a: int, b: int, c: int, ics=None) -> None:
        lhs = ordered(D2, a * D1, b * Y)
        eqn = lhs - 0
        eq = sp.Eq(f(x).diff(x, 2) + a * f(x).diff(x) + b * f(x), 0)
        sol_ = sp.dsolve(eq, f(x), ics=ics) if ics else sp.dsolve(eq, f(x))
        ans = sp.simplify(sol_.rhs)
        roots = sp.roots(sp.Poly(sp.Symbol("r") ** 2 + a * sp.Symbol("r") + b, sp.Symbol("r")))
        text = (
            rf"The characteristic equation $r^2+({a})r+({b})=0$ has the roots ${', '.join(tex(r_) for r_ in roots)}$"
            + (rf", so $y={tex(ans)}$." if not ics else rf". The general solution fitted to the conditions is $y={tex(ans)}$.")
        )
        cond_tex = ""
        conditions = None
        if ics:
            (k0, v0), (k1, v1) = ics.items()
            cond_tex = rf", $\ y(0)={tex(v0)}$, $y'(0)={tex(v1)}$"
            conditions = [("0", str(v0), 0), ("0", str(v1), 1)]
        items.append(sol(f"mp-cc-{i}", stmt(lhs, sp.Integer(0), cond_tex), residual(eqn), f"y = {eng(ans)}", text, [r"Solve the characteristic equation $r^2+ar+b=0$."],
                         order=2, conditions=conditions))
        assert c == 0

    one("1", -3, 2, 0)
    one("2", 4, 4, 0)
    one("3", 0, 4, 0)
    one("4", 2, 5, 0)
    one("5", 0, -4, 0, ics={f(0): 1, f(x).diff(x).subs(x, 0): 2})
    one("6", 6, 9, 0, ics={f(0): 1, f(x).diff(x).subs(x, 0): 0})
    one("7", 1, -6, 0, ics={f(0): 0, f(x).diff(x).subs(x, 0): 5})
    one("8", 0, 9, 0, ics={f(0): 2, f(x).diff(x).subs(x, 0): 3})
    return items


# --- undetermined coefficients ------------------------------------------------------------------------------------------------------
def undetermined_items() -> list[dict]:
    items = []
    f = sp.Function("f")

    def one(i: str, a: int, b: int, g: sp.Expr, guess: str) -> None:
        lhs = ordered(D2, a * D1, b * Y)
        eqn = lhs - g
        eq = sp.Eq(f(x).diff(x, 2) + a * f(x).diff(x) + b * f(x), g)
        s = sp.simplify(sp.dsolve(eq, f(x)).rhs)
        items.append(sol(
            f"mp-uc-{i}", stmt(lhs, g), residual(eqn), f"y = {eng(s)}",
            rf"The homogeneous equation has $r^2+({a})r+({b})=0$. For the right-hand side ${tex(g)}$ try {guess}. Solving for the coefficients gives $y={tex(s)}$.",
            [r"General solution $=$ homogeneous solution $+$ a particular solution found with the right guess."], order=2))

    one("1", -3, 2, sp.exp(3 * x), r"$y_p=Ae^{3x}$ ($3$ is not a root)")
    one("2", 0, 1, x**2, r"$y_p=Ax^2+Bx+D$")
    one("3", 0, 4, sp.sin(x), r"$y_p=A\cos x+B\sin x$")
    one("4", 0, -1, sp.exp(x), r"$y_p=Axe^{x}$ ($1$ is a root, so multiply by $x$)")
    one("5", 2, 1, sp.exp(-x), r"$y_p=Ax^2e^{-x}$ ($-1$ is a double root, so multiply by $x^2$)")
    one("6", -2, 0, x, r"$y_p=x(Ax+B)$ ($0$ is a root, so multiply by $x$)")
    one("7", 0, 9, sp.cos(3 * x), r"$y_p=x(A\cos3x+B\sin3x)$ ($\pm3i$ are roots, so multiply by $x$)")
    return items


# --- variation of parameters ---------------------------------------------------------------------------------------------------------
def variation_items() -> list[dict]:
    items = []
    f = sp.Function("f")

    def one(i: str, a: int, b: int, g: sp.Expr, y1: sp.Expr, y2: sp.Expr, sample: tuple) -> None:
        lhs = ordered(D2, a * D1, b * Y)
        eqn = lhs - g
        wr = sp.simplify(y1 * sp.diff(y2, x) - y2 * sp.diff(y1, x))
        u1p = sp.simplify(-y2 * g / wr)
        u2p = sp.simplify(y1 * g / wr)
        u1, u2 = sp.integrate(u1p, x), sp.integrate(u2p, x)
        yp = sp.simplify(u1 * y1 + u2 * y2)
        eq = sp.Eq(f(x).diff(x, 2) + a * f(x).diff(x) + b * f(x), g)
        s = sp.simplify(sp.dsolve(eq, f(x)).rhs)
        items.append(sol(
            f"mp-vp-{i}", stmt(lhs, g), residual(eqn), f"y = {eng(s)}",
            rf"Homogeneous solutions $y_1={tex(y1)}$, $y_2={tex(y2)}$ with Wronskian $W={tex(wr)}$. Then $u_1'=-\dfrac{{y_2g}}{{W}}={tex(u1p)}$ and $u_2'=\dfrac{{y_1g}}{{W}}={tex(u2p)}$, so "
            rf"$u_1={tex(u1)}$, $u_2={tex(u2)}$ (constants of integration go into $C_1,C_2$), $y_p=u_1y_1+u_2y_2={tex(yp)}$ and $y=C_1y_1+C_2y_2+y_p={tex(s)}$.",
            [r"Compute the Wronskian $W=y_1y_2'-y_2y_1'$ and $u_1'=-\dfrac{y_2g}{W}$, $u_2'=\dfrac{y_1g}{W}$."], order=2, sample=sample))

    one("1", 0, 1, 1 / sp.cos(x), sp.cos(x), sp.sin(x), (0.2, 1.2))
    one("2", -2, 1, sp.exp(x) / x, sp.exp(x), x * sp.exp(x), (0.6, 1.9))
    one("3", 0, 1, 1 / sp.sin(x), sp.cos(x), sp.sin(x), (0.3, 2.8))
    one("4", 0, 4, 1 / sp.cos(2 * x), sp.cos(2 * x), sp.sin(2 * x), (0.1, 0.7))
    one("5", 2, 1, sp.exp(-x) / x, sp.exp(-x), x * sp.exp(-x), (0.6, 1.9))
    one("6", -2, 1, sp.exp(x) * sp.log(x), sp.exp(x), x * sp.exp(x), (0.6, 1.9))
    one("7", 0, 1, sp.tan(x) ** 0 * x, sp.cos(x), sp.sin(x), (0.2, 1.9))
    one("8", -3, 2, sp.exp(2 * x) / (sp.exp(2 * x) + 1) * 0 + sp.exp(3 * x), sp.exp(x), sp.exp(2 * x), (0.2, 1.4))
    one("9", 0, 9, 1 / sp.sin(3 * x), sp.cos(3 * x), sp.sin(3 * x), (0.2, 1.0))
    return items


def first_lesson_item() -> list[dict]:
    f = Y * 0
    assert f == 0
    return [ex(
        "mp-voc-1", r"What are the order and the degree of $\left(y''\right)^2+3y'-y=x$?", "multiple_choice", "3",
        choices=[{"text": "order 1, degree 2", "value": "1"}, {"text": "order 1, degree 1", "value": "2"}, {"text": "order 2, degree 2", "value": "3"}, {"text": "order 2, degree 1", "value": "4"}],
        correctIndex=2, hints=[r"The order is the highest derivative; the degree is the power of that derivative."],
        solution=r"The highest derivative is $y''$, so the order is $2$; it appears squared, so the degree is $2$.",
    )]


def register() -> None:
    fmt_rel = "Type the solution with an arbitrary constant `C`, for example `y = C*e^x` or `x^2 + y^2 = C`."
    add_extra(f"{U1}/l01-solutions-and-equations", exset_plain("more-vocabulary", "More practice: order and degree.", first_lesson_item()), SCRIPT)
    add_extra(f"{U1}/l02-separable", exset_plain("more-separable", "More practice: separable equations.", separable_items(), format=fmt_rel), SCRIPT)
    add_extra(f"{U1}/l03-homogeneous", exset_plain("more-homogeneous", "More practice: homogeneous equations.", homogeneous_items(), format=fmt_rel), SCRIPT)
    add_extra(f"{U1}/l04-linear", exset_plain("more-linear", "More practice: linear equations of the first order.", linear_items(), format=fmt_rel), SCRIPT)
    add_extra(f"{U1}/l05-bernoulli", exset_plain("more-bernoulli", "More practice: Bernoulli equations.", bernoulli_items(), format=fmt_rel), SCRIPT)
    add_extra(f"{U1}/l06-exact", exset_plain("more-exact", "More practice: exact equations.", exact_items(), format=fmt_rel), SCRIPT)
    add_extra(f"{U2}/l01-constant-coefficients", exset_plain("more-constant", "More practice: constant coefficients.", const_items(),
                                                              format="Type the general solution with constants `C1` and `C2`, for example `y = C1*e^x + C2*e^(-x)`."), SCRIPT)
    add_extra(f"{U2}/l02-undetermined-coefficients", exset_plain("more-undetermined", "More practice: undetermined coefficients.", undetermined_items(),
                                                                  format="Type the general solution with `C1` and `C2`."), SCRIPT)
    add_extra(f"{U2}/l03-variation-of-parameters", exset_plain("more-variation", "More practice: variation of parameters.", variation_items(),
                                                                format="Type the general solution with `C1` and `C2`."), SCRIPT)
