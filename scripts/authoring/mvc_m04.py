"""Exercises of Course 2, Module 4: ordinary differential equations (sheet parts A, B.I-III and the second-order part)."""

from __future__ import annotations

import random

import sympy as sp
from toolkit import P, eng, ex, exset, tex, write_exercises, x

BASE = "mvc/m04-ode"
U1 = f"{BASE}/u01-first-order"
U2 = f"{BASE}/u02-second-order"


# --- an independent audit of every explicit answer (the engine re-checks all answers when the content is verified) ------
def _sym(expr: sp.Expr, name: str) -> sp.Symbol:
    for s in expr.free_symbols:
        if s.name == name:
            return s
    return sp.Symbol(name, real=True)


def audit(equation: str, answer: str, params: dict[str, float] | None = None, sample: tuple[float, float] = (0.6, 1.9)) -> None:
    """For an explicit answer y = F(x, C...): F must satisfy the equation F(x, y, y1, y2) = 0 at random points."""
    lhs, rhs = answer.split("=", 1)
    if lhs.strip() != "y":
        return
    f = P(rhs)
    eq = P(equation)
    xs = _sym(f, "x")
    consts = [s for s in f.free_symbols if s.name not in {"x"} | set(params or {})]
    d1, d2 = sp.diff(f, xs), sp.diff(f, xs, 2)
    rng = random.Random(7)
    for _ in range(5):
        sub = {c: sp.Rational(rng.randint(1, 9), 4) for c in consts}
        sub.update({_sym(f, k): sp.Rational(v) for k, v in (params or {}).items()})
        sub[xs] = sp.Rational(rng.randint(int(sample[0] * 100), int(sample[1] * 100)), 100)
        mapping = {
            _sym(eq, "y"): f.subs(sub),
            _sym(eq, "y1"): d1.subs(sub),
            _sym(eq, "y2"): d2.subs(sub),
            _sym(eq, "x"): sub[xs],
        }
        for k, v in (params or {}).items():
            mapping[_sym(eq, k)] = sp.Rational(v)
        value = sp.N(eq.subs(mapping), 30)
        assert abs(value) < 1e-20, (equation, answer, value)


def sol(
    id: str,
    statement: str,
    equation: str,
    answer: str,
    solution: str,
    hints: list[str],
    *,
    sample: tuple[float, float] | None = None,
    conditions: list[tuple[str, str, int]] | None = None,
    params: dict[str, float] | None = None,
    order: int = 1,
    note: str | None = None,
) -> dict:
    ode: dict = {"order": order, "equation": equation}
    if sample:
        ode["sample"] = list(sample)
    if conditions:
        ode["conditions"] = [{"at": a, "value": v, "derivative": d} for a, v, d in conditions]
    if params:
        ode["parameters"] = list(params)
    audit(equation, answer, params, sample or (0.6, 1.9))
    extra: dict = {}
    if note:
        extra["note"] = note
    return ex(id, statement, "ode_solution", answer, solution=solution, hints=hints, ode=ode, **extra)


# --- lesson 1: vocabulary --------------------------------------------------------------------------------------------
def proving_items() -> list[dict]:
    items: list[dict] = []
    c1, c2, c3, c = sp.symbols("c1 c2 c3 c", real=True)

    def prove(id, y_tex, ode_tex, y_expr, residual, orders, hint, template):
        """Ask for the derivatives that the equation needs; the substitution is carried out in the solution.

        `template` is the left-hand side of the equation with @Y, @1, @2 standing for y and its derivatives."""
        derivs = [sp.simplify(sp.diff(y_expr, x, k)) for k in range(1, orders + 1)]
        assert sp.simplify(residual(y_expr)) == 0, id
        names = ["y'", "y''", "y'''"][:orders]
        lhs = template
        for token, value in {"@Y": tex(y_expr), **{f"@{k + 1}": tex(d) for k, d in enumerate(derivs)}}.items():
            lhs = lhs.replace(token, value)
        shown = ",\\quad ".join(f"{n}={tex(d)}" for n, d in zip(names, derivs))
        answer = "(" + ", ".join(eng(d) for d in derivs) + ")"
        if orders == 1:
            answer = eng(derivs[0])
        vars_ = ["x", *[s.name for s in sorted(y_expr.free_symbols - {x}, key=lambda s: s.name)]]
        return ex(
            id,
            f"Prove that ${y_tex}$ is a solution of ${ode_tex}$.",
            "vector" if orders > 1 else "expression",
            answer,
            variables=vars_,
            hints=[hint],
            solution=(
                f"Differentiate: ${shown}$. Substituting into the left-hand side of ${ode_tex}$ gives $${lhs}=0$$ "
                f"for every value of the constants, so $y$ is a solution. Enter the derivatives used in the substitution"
                + (" as a vector $(y',\\,y'')$." if orders == 2 else " as a vector $(y',\\,y'',\\,y''')$." if orders == 3 else ".")
            ),
        )

    e = sp.E
    items.append(prove(
        "sol-1", r"y=c_1e^{x}+c_2e^{2x}", r"y''-3y'+2y=0",
        c1 * e**x + c2 * e ** (2 * x), lambda y: sp.diff(y, x, 2) - 3 * sp.diff(y, x) + 2 * y, 2,
        "Differentiate twice, then collect the terms in $e^{x}$ and in $e^{2x}$ separately.",
        r"\left(@2\right)-3\left(@1\right)+2\left(@Y\right)",
    ))
    items.append(prove(
        "sol-2", r"y=ce^{-3x}", r"y'+3y=0",
        c * e ** (-3 * x), lambda y: sp.diff(y, x) + 3 * y, 1,
        "The derivative of $e^{-3x}$ is $-3e^{-3x}$.",
        r"\left(@1\right)+3\left(@Y\right)",
    ))
    items.append(prove(
        "sol-3", r"y=e^{x}(c_1\cos x+c_2\sin x)", r"y''-2y'+2y=0",
        e**x * (c1 * sp.cos(x) + c2 * sp.sin(x)), lambda y: sp.diff(y, x, 2) - 2 * sp.diff(y, x) + 2 * y, 2,
        "Use the product rule. The terms with $\\cos x$ and with $\\sin x$ cancel separately.",
        r"\left(@2\right)-2\left(@1\right)+2\left(@Y\right)",
    ))
    items.append(prove(
        "sol-4", r"y=(c_1+c_2x)e^{-2x}", r"y''+4y'+4y=0",
        (c1 + c2 * x) * e ** (-2 * x), lambda y: sp.diff(y, x, 2) + 4 * sp.diff(y, x) + 4 * y, 2,
        "Write $y=c_1e^{-2x}+c_2xe^{-2x}$ and differentiate each term.",
        r"\left(@2\right)+4\left(@1\right)+4\left(@Y\right)",
    ))

    # 7: implicit
    yy = sp.Symbol("y", real=True)
    g = yy**2 - x**2 - x * yy
    yp = sp.simplify(sp.idiff(g, yy, x))
    assert sp.simplify((x - 2 * yy) * yp + 2 * x + yy) == 0
    items.append(ex(
        "sol-5", r"Prove that $y^2-x^2-xy=c$ defines solutions of $(x-2y)y'+2x+y=0$.", "expression", eng(yp), variables=["x", "y"],
        hints=["Differentiate both sides with respect to $x$, treating $y$ as a function of $x$, then solve for $y'$."],
        solution=(
            r"Differentiate $y^2-x^2-xy=c$ with respect to $x$: $2yy'-2x-y-xy'=0$, so $(2y-x)\,y'=2x+y$ and $y'=\dfrac{2x+y}{2y-x}$. "
            r"Substituting into the equation: $(x-2y)\dfrac{2x+y}{2y-x}+2x+y=-(2x+y)+2x+y=0$."
        ),
        note="Printed as exercise 7 on the sheet. The printed sheet has no exercises 5 and 6 in this part, so the three that follow are numbered 6 and 7 here (printed 8 and 9).",
    ))

    # 8
    y8 = c1 * x + c2 / x + c3
    d8 = [sp.simplify(sp.diff(y8, x, k)) for k in (1, 2, 3)]
    assert sp.simplify(d8[2] + 3 / x * d8[1]) == 0
    items.append(ex(
        "sol-6", r"Prove that $y=c_1x+\dfrac{c_2}{x}+c_3$ is a solution of $y'''+\dfrac3x\,y''=0$.", "vector",
        "(" + ", ".join(eng(d) for d in d8) + ")", variables=["x", "c1", "c2", "c3"],
        hints=[r"Write $\dfrac{c_2}{x}=c_2x^{-1}$ and differentiate three times."],
        solution=(
            rf"$y'={tex(d8[0])}$, $y''={tex(d8[1])}$, $y'''={tex(d8[2])}$. Then $y'''+\dfrac3x\,y''=-\dfrac{{6c_2}}{{x^4}}+\dfrac3x\cdot\dfrac{{2c_2}}{{x^3}}=0$. "
            r"Enter the three derivatives as a vector."
        ),
    ))

    # 9
    a = sp.asin(x)
    y9 = c1 * e**a + c2 * e ** (-a)
    d9 = [sp.simplify(sp.diff(y9, x, k)) for k in (1, 2)]
    assert sp.simplify((1 - x**2) * d9[1] - x * d9[0] - y9) == 0
    items.append(ex(
        "sol-7", r"Prove that $y=c_1e^{\arcsin x}+c_2e^{-\arcsin x}$ is a solution of $(1-x^2)y''-xy'-y=0$.", "vector",
        "(" + ", ".join(eng(d) for d in d9) + ")", variables=["x", "c1", "c2"],
        hints=[r"$\dfrac{d}{dx}\arcsin x=\dfrac1{\sqrt{1-x^2}}$, so each exponential gains the factor $\pm\dfrac1{\sqrt{1-x^2}}$ when differentiated."],
        solution=(
            r"With $u=\arcsin x$, $u'=\dfrac1{\sqrt{1-x^2}}$, so $y'=\dfrac{c_1e^{u}-c_2e^{-u}}{\sqrt{1-x^2}}$. Differentiating again, "
            r"$y''=\dfrac{c_1e^{u}+c_2e^{-u}}{1-x^2}+\dfrac{x\,(c_1e^{u}-c_2e^{-u})}{(1-x^2)^{3/2}}$. "
            r"Then $(1-x^2)y''=y+xy'$, which is the equation. Enter $(y',y'')$."
        ),
        note="The printed sheet writes $y''$ without simplification; any equivalent form of the derivatives is accepted.",
    ))
    return items


def forming_items() -> list[dict]:
    def fam(id, family_tex, family, consts, order, answer, hint, solution, **extra):
        return ex(
            id, rf"Form the differential equation whose general solution is ${family_tex}$.", "ode_family", answer,
            ode={"order": order, "family": family, "constants": consts}, hints=[hint], solution=solution, **extra,
        )

    return [
        fam("form-1", r"y=cx^{2}-x", "y = c*x^2 - x", ["c"], 1, "x*y' = 2*y + x",
            "Differentiate once, solve for $c$ and substitute back into $y$.",
            r"$y'=2cx-1$, so $c=\dfrac{y'+1}{2x}$. Then $y=cx^2-x=\dfrac{x(y'+1)}{2}-x$, which gives $xy'=2y+x$."),
        fam("form-2", r"y=c_1x^{3}+c_2x+c_3", "y = c1*x^3 + c2*x + c3", ["c1", "c2", "c3"], 3, "x*y''' = y''",
            "Three constants need three derivatives. The derivatives $y''$ and $y'''$ contain $c_1$ only.",
            r"$y''=6c_1x$ and $y'''=6c_1$, so $xy'''=y''$."),
        fam("form-3", r"y=c_1e^{x}+c_2xe^{x}", "y = c1*e^x + c2*x*e^x", ["c1", "c2"], 2, "y'' - 2*y' + y = 0",
            "The root $1$ of the characteristic equation is double.",
            r"The characteristic equation has the double root $r=1$, that is $(r-1)^2=r^2-2r+1=0$. The equation is $y''-2y'+y=0$."),
        fam("form-4", r"y=c_1x^{3}+c_2x", "y = c1*x^3 + c2*x", ["c1", "c2"], 2, "x^2*y'' - 3*x*y' + 3*y = 0",
            "Differentiate twice, then eliminate $c_1$ and $c_2$ from the three equations for $y$, $y'$, $y''$.",
            r"$y'=3c_1x^2+c_2$ and $y''=6c_1x$. So $c_1=\dfrac{y''}{6x}$ and $c_2=y'-\dfrac{xy''}{2}$. "
            r"Substituting in $y=c_1x^3+c_2x$ gives $y=\dfrac{x^2y''}{6}+xy'-\dfrac{x^2y''}{2}=xy'-\dfrac{x^2y''}{3}$, that is $x^2y''-3xy'+3y=0$."),
        fam("form-5", r"x^{2}+y^{2}=c^{2}", "x^2 + y^2 = c^2", ["c"], 1, "x + y*y' = 0",
            "Differentiate both sides with respect to $x$; the constant disappears.",
            r"$2x+2yy'=0$, so $x+yy'=0$."),
        fam("form-6", r"y=c_1e^{x}+c_2xe^{x}+c_3e^{-x}", "y = c1*e^x + c2*x*e^x + c3*e^(-x)", ["c1", "c2", "c3"], 3,
            "y''' - y'' - y' + y = 0",
            "Read the roots of the characteristic equation from the exponents: $1$ (double) and $-1$.",
            r"The characteristic roots are $1,1,-1$, so $(r-1)^2(r+1)=r^3-r^2-r+1=0$ and the equation is $y'''-y''-y'+y=0$.",
            note="Printed as exercise 7 on the sheet (the sheet has no exercise 6 in this part)."),
        fam("form-7", r"y=c_1e^{x}+c_2xe^{-x}+c_3e^{-x}", "y = c1*e^x + c2*x*e^(-x) + c3*e^(-x)", ["c1", "c2", "c3"], 3,
            "y''' + y'' - y' - y = 0",
            "Read the roots from the exponents: $1$ and $-1$ (double).",
            r"The roots are $1,-1,-1$, so $(r-1)(r+1)^2=r^3+r^2-r-1=0$ and the equation is $y'''+y''-y'-y=0$.",
            note="Printed as exercise 8 on the sheet."),
    ]


def build_l01() -> None:
    write_exercises(
        f"{U1}/l01-solutions-and-equations",
        [
            exset("prove", "Show that the function is a solution. Enter the derivatives you need; the substitution is in the worked solution.",
                  proving_items(), format="For several derivatives type a vector, for example `(2*x, 2)`."),
            exset("form", "Eliminate the arbitrary constants to find the differential equation of lowest order.", forming_items(),
                  format="Type the equation, for example `y' = 3*y` or `y'' - y = 0`."),
        ],
        "mvc_m04.py",
    )


# --- lesson 2: separable ----------------------------------------------------------------------------------------------
def build_l02() -> None:
    items = [
        sol("sep-a", r"$\tan x\,\sin^2y\,dx+\cos x\,\cot y\,dy=0$", "tan(x)*sin(y)^2 + cos(x)*cot(y)*y1",
            "1/cos(x) = 1/(2*sin(y)^2) + C",
            r"Divide by $\cos x\,\sin^2y$: $\dfrac{\sin x}{\cos^2x}\,dx+\dfrac{\cos y}{\sin^3y}\,dy=0$. Integrate: "
            r"$\dfrac1{\cos x}-\dfrac1{2\sin^2y}=C$.",
            ["Divide by $\\cos x\\,\\sin^2y$ so that each side has one variable. Note that $\\tan x/\\cos x=\\sin x/\\cos^2x$."], sample=(0.3, 1.2)),
        sol("sep-b", r"$xy'-y=y^3$", "x*y1 - y - y^3", "y^2/(1+y^2) = C*x^2",
            r"$xy'=y(1+y^2)$, so $\dfrac{dy}{y(1+y^2)}=\dfrac{dx}x$. With $\dfrac1{y(1+y^2)}=\dfrac1y-\dfrac y{1+y^2}$: "
            r"$\ln|y|-\tfrac12\ln(1+y^2)=\ln|x|+c$, that is $\dfrac{y^2}{1+y^2}=Cx^2$. The constant solution $y=0$ is the case $C=0$.",
            ["Use the partial fractions $\\dfrac1{y(1+y^2)}=\\dfrac1y-\\dfrac y{1+y^2}$."]),
        sol("sep-c", r"$xyy'=1-x^3$", "x*y*y1 - (1 - x^3)", "y^2/2 = ln(abs(x)) - x^3/3 + C",
            r"$y\,dy=\left(\dfrac1x-x^2\right)dx$, so $\dfrac{y^2}2=\ln|x|-\dfrac{x^3}3+C$.",
            ["Write $y\\,dy=\\dfrac{1-x^3}{x}\\,dx$."]),
        sol("sep-d", r"$y-xy'=1+x^2y'$", "y - x*y1 - 1 - x^2*y1", "y = 1 + C*x/(x+1)",
            r"Collect $y'$: $y-1=(x^2+x)\,y'$, so $\dfrac{dy}{y-1}=\dfrac{dx}{x(x+1)}=\left(\dfrac1x-\dfrac1{x+1}\right)dx$. "
            r"Then $\ln|y-1|=\ln\left|\dfrac x{x+1}\right|+c$, and $y=1+C\dfrac{x}{x+1}$.",
            ["Collect all the terms with $y'$ on one side: $y-1=(x+x^2)\\,y'$."]),
        sol("sep-e", r"$y'\tan x=y$", "y1*tan(x) - y", "y = C*sin(x)",
            r"$\dfrac{dy}y=\cot x\,dx$, so $\ln|y|=\ln|\sin x|+c$ and $y=C\sin x$.",
            ["Divide by $y\\tan x$."], sample=(0.3, 1.2)),
        sol("sep-f", r"$3e^{x}\tan y\,dx+(1-e^{x})\sec^2y\,dy=0$", "3*e^x*tan(y) + (1 - e^x)*sec(y)^2*y1",
            "tan(y) = C*(1 - e^x)^3",
            r"Divide by $(1-e^x)\tan y$: $\dfrac{\sec^2y}{\tan y}\,dy=-\dfrac{3e^x}{1-e^x}\,dx$. Integrate: "
            r"$\ln|\tan y|=3\ln|1-e^x|+c$, so $\tan y=C(1-e^x)^3$.",
            ["Divide by $(1-e^x)\\tan y$. Note $\\dfrac{d}{dy}\\tan y=\\sec^2y$."], sample=(0.2, 1.2)),
    ]
    ivp = [
        sol("sep-g", r"$(1+e^{x})\,yy'=e^{x}$, $\ y(0)=1$", "(1 + e^x)*y*y1 - e^x", "y = sqrt(2*ln(1+e^x) - 2*ln(2) + 1)",
            r"$y\,dy=\dfrac{e^x}{1+e^x}\,dx$, so $\dfrac{y^2}2=\ln(1+e^x)+C$. From $y(0)=1$: $\dfrac12=\ln2+C$, so $C=\dfrac12-\ln2$ and "
            r"$y^2=2\ln(1+e^x)-2\ln2+1$. Since $y(0)=1>0$, take the positive root.",
            ["After integrating, use $y(0)=1$ to find $C$. Then decide the sign of the square root from $y(0)>0$."],
            conditions=[("0", "1", 0)]),
        sol("sep-h", r"$(xy^{2}+x)\,dx+(x^{2}y-y)\,dy=0$, $\ y(0)=1$", "(x*y^2 + x) + (x^2*y - y)*y1",
            "y = sqrt((1+x^2)/(1-x^2))",
            r"Factor: $x(y^2+1)\,dx+y(x^2-1)\,dy=0$, so $\dfrac{x\,dx}{x^2-1}+\dfrac{y\,dy}{y^2+1}=0$. Integrate: "
            r"$\tfrac12\ln|x^2-1|+\tfrac12\ln(y^2+1)=c$, so $(1-x^2)(1+y^2)=C$. $y(0)=1$ gives $C=2$, so $y^2=\dfrac2{1-x^2}-1=\dfrac{1+x^2}{1-x^2}$ "
            r"(positive root, since $y(0)=1$), for $|x|<1$.",
            ["Factor $x$ from the first bracket and $y$ from the second one, then separate."],
            sample=(0.1, 0.8), conditions=[("0", "1", 0)]),
    ]
    write_exercises(
        f"{U1}/l02-separable",
        [
            exset("separable", "Solve the differential equation. Give the general solution.", items,
                  format="Type the solution, for example `y = C*sin(x)` or an implicit relation such as `y^2 = x^3 + C`."),
            exset("separable-ivp", "Solve the initial-value problem.", ivp, format="Type $y$ as an explicit function of $x$."),
        ],
        "mvc_m04.py",
    )


# --- lesson 3: homogeneous and reducible ---------------------------------------------------------------------------------
def build_l03() -> None:
    hom = [
        sol("hom-a", r"$(y-x)\,dx+(y+x)\,dy=0$", "(y - x) + (y + x)*y1", "y^2 + 2*x*y - x^2 = C",
            r"The equation is homogeneous of degree $1$ (and also exact). With $y=vx$: $(vx-x)\,dx+(vx+x)(v\,dx+x\,dv)=0$, i.e. "
            r"$(v^2+2v-1)\,dx+x(v+1)\,dv=0$. Then $\dfrac{(v+1)\,dv}{v^2+2v-1}=-\dfrac{dx}x$, so $\tfrac12\ln|v^2+2v-1|=-\ln|x|+c$ and "
            r"$x^2(v^2+2v-1)=C$, that is $y^2+2xy-x^2=C$.",
            ["Put $y=vx$, so $dy=v\\,dx+x\\,dv$, and separate $v$ and $x$."]),
        sol("hom-b", r"$(x+y)\,dx+x\,dy=0$", "(x + y) + x*y1", "y = -x/2 + C/x",
            r"With $y=vx$: $(1+v)\,dx+(v\,dx+x\,dv)=0$, so $(1+2v)\,dx+x\,dv=0$ and $\dfrac{dv}{1+2v}=-\dfrac{dx}x$. "
            r"Then $\tfrac12\ln|1+2v|=-\ln|x|+c$, so $x^2(1+2v)=C$, that is $x^2+2xy=C$ and $y=-\dfrac x2+\dfrac C{2x}$ (the constant $\dfrac C2$ is renamed $C$).",
            ["Put $y=vx$. After separation the left side is $\\dfrac{dv}{1+2v}$."]),
        sol("hom-c", r"$(x+y)\,dx+(y-x)\,dy=0$", "(x + y) + (y - x)*y1", "atan(y/x) = ln(x^2+y^2)/2 + C",
            r"With $y=vx$: $(1+v)\,dx+(v-1)(v\,dx+x\,dv)=0$, so $(1+v^2)\,dx+x(v-1)\,dv=0$ and $\dfrac{(v-1)\,dv}{1+v^2}=-\dfrac{dx}x$. "
            r"Integrate: $\tfrac12\ln(1+v^2)-\arctan v=-\ln|x|+c$, so $\arctan\dfrac yx=\ln|x|+\tfrac12\ln\left(1+\dfrac{y^2}{x^2}\right)+C=\tfrac12\ln(x^2+y^2)+C$.",
            ["With $y=vx$ the equation becomes $(1+v^2)\\,dx+x(v-1)\\,dv=0$."], sample=(0.6, 1.9)),
        sol("hom-d", r"$x\,dy-y\,dx=\sqrt{x^{2}+y^{2}}\;dx$", "x*y1 - y - sqrt(x^2 + y^2)", "y + sqrt(x^2+y^2) = C*x^2",
            r"For $x>0$, $y'=\dfrac yx+\sqrt{1+\left(\dfrac yx\right)^2}$. With $y=vx$: $xv'=\sqrt{1+v^2}$, so $\dfrac{dv}{\sqrt{1+v^2}}=\dfrac{dx}x$ and "
            r"$\ln\left(v+\sqrt{1+v^2}\right)=\ln x+c$. Hence $v+\sqrt{1+v^2}=Cx$, i.e. $y+\sqrt{x^2+y^2}=Cx^2$.",
            ["For $x>0$ divide by $x$: $\\sqrt{x^2+y^2}=x\\sqrt{1+v^2}$. The integral $\\int\\dfrac{dv}{\\sqrt{1+v^2}}$ is $\\ln\\left(v+\\sqrt{1+v^2}\\right)$."],
            note=r"The sheet prints $\sqrt{x^2+y^2\,dx}$, with $dx$ under the root. It is read here as $\sqrt{x^2+y^2}\,dx$, the only reading that gives a differential equation."),
        sol("hom-e", r"$(8y+10x)\,dx+(5y+7x)\,dy=0$", "(8*y + 10*x) + (5*y + 7*x)*y1", "(x+y)^2*(2*x+y)^3 = C",
            r"With $y=vx$: $(8v+10)\,dx+(5v+7)(v\,dx+x\,dv)=0$, so $5(v+1)(v+2)\,dx+x(5v+7)\,dv=0$. "
            r"Partial fractions: $\dfrac{5v+7}{(v+1)(v+2)}=\dfrac2{v+1}+\dfrac3{v+2}$. Integrate: $2\ln|v+1|+3\ln|v+2|=-5\ln|x|+c$, so "
            r"$(v+1)^2(v+2)^3x^5=C$, that is $(x+y)^2(2x+y)^3=C$.",
            ["After $y=vx$ the factor $5v^2+15v+10$ appears; it factors as $5(v+1)(v+2)$."], sample=(0.6, 1.9)),
        sol("hom-f", r"$xy^{2}\,dy=(x^{3}+y^{3})\,dx$", "x*y^2*y1 - x^3 - y^3", "y^3 = 3*x^3*ln(x) + C*x^3",
            r"$y'=\dfrac{x^3+y^3}{xy^2}$. With $y=vx$: $v+xv'=\dfrac{1+v^3}{v^2}$, so $xv'=\dfrac1{v^2}$ and $v^2\,dv=\dfrac{dx}x$. "
            r"Then $\dfrac{v^3}3=\ln|x|+c$, so $y^3=3x^3\ln|x|+Cx^3$.",
            ["With $y=vx$, $xv'=\\dfrac{1+v^3}{v^2}-v=\\dfrac1{v^2}$."]),
    ]
    red = [
        sol("red-a", r"$(2x+y-4)\,dy+(x-2y+5)\,dx=0$", "(x - 2*y + 5) + (2*x + y - 4)*y1",
            "2*atan((y - 14/5)/(x - 3/5)) + ln((x - 3/5)^2 + (y - 14/5)^2)/2 = C",
            r"The lines $2x+y-4=0$ and $x-2y+5=0$ meet at $\left(\dfrac35,\dfrac{14}5\right)$. Put $X=x-\dfrac35$ and $Y=y-\dfrac{14}5$: "
            r"$(2X+Y)\,dY+(X-2Y)\,dX=0$, which is homogeneous. With $Y=vX$: $\dfrac{(2+v)\,dv}{1+v^2}=-\dfrac{dX}X$. Integrate: "
            r"$2\arctan v+\tfrac12\ln(1+v^2)=-\ln|X|+c$, that is $2\arctan\dfrac YX+\tfrac12\ln(X^2+Y^2)=C$.",
            ["Solve $2x+y=4$, $x-2y=-5$ for the intersection point, then shift the origin to it."], sample=(1.0, 2.5)),
        sol("red-b", r"$y'=\dfrac{1-3x-3y}{1+x+y}$", "y1*(1 + x + y) - (1 - 3*x - 3*y)", "3*x + y + 2*ln(abs(1 - x - y)) = C",
            r"The lines are parallel (the right side depends on $x+y$ only). Put $u=x+y$: $u'=1+\dfrac{1-3u}{1+u}=\dfrac{2(1-u)}{1+u}$, so "
            r"$\dfrac{1+u}{1-u}\,du=2\,dx$. Since $\dfrac{1+u}{1-u}=-1+\dfrac2{1-u}$: $-u-2\ln|1-u|=2x+c$. Substituting $u=x+y$: $3x+y+2\ln|1-x-y|=C$.",
            ["Put $u=x+y$, so $u'=1+y'$."], sample=(1.2, 2.0)),
        sol("red-c", r"$y'=\dfrac{x+2y+1}{2x+4y+3}$", "y1*(2*x + 4*y + 3) - (x + 2*y + 1)", "8*y - 4*x + ln(abs(4*x + 8*y + 5)) = C",
            r"The lines are parallel again. Put $u=x+2y$: $u'=1+2y'=1+\dfrac{2(u+1)}{2u+3}=\dfrac{4u+5}{2u+3}$, so "
            r"$\dfrac{2u+3}{4u+5}\,du=dx$. Since $\dfrac{2u+3}{4u+5}=\dfrac12+\dfrac1{2(4u+5)}$: $\dfrac u2+\dfrac18\ln|4u+5|=x+c$, that is "
            r"$4u+\ln|4u+5|=8x+C$. With $u=x+2y$: $8y-4x+\ln|4x+8y+5|=C$.",
            ["Put $u=x+2y$; then $2x+4y+3=2u+3$."]),
        sol("red-d", r"$(x+2y+1)\,dx-(2x+4y+3)\,dy=0$", "(x + 2*y + 1) - (2*x + 4*y + 3)*y1", "8*y - 4*x + ln(abs(4*x + 8*y + 5)) = C",
            r"Solving for $y'$ gives $y'=\dfrac{x+2y+1}{2x+4y+3}$, the equation of part (c). The solution is the same: $8y-4x+\ln|4x+8y+5|=C$.",
            ["Divide by $dx$ and compare with part (c)."],
            note="Parts (c) and (d) of the sheet are the same differential equation, written in two ways."),
    ]
    write_exercises(
        f"{U1}/l03-homogeneous",
        [
            exset("homogeneous", "Integrate the homogeneous equation.", hom,
                  format="Type the relation between $x$ and $y$, with an arbitrary constant $C$."),
            exset("reducible", "Reduce to a homogeneous or a separable equation and solve.", red,
                  format="Type the relation between $x$ and $y$, with an arbitrary constant $C$."),
        ],
        "mvc_m04.py",
    )


# --- lesson 4: linear -----------------------------------------------------------------------------------------------------
def build_l04() -> None:
    lin = [
        sol("lin-a", r"$y'-\dfrac{2y}{x+1}=(x+1)^3$", "y1 - 2*y/(x+1) - (x+1)^3", "y = (x+1)^4/2 + C*(x+1)^2",
            r"$P=-\dfrac2{x+1}$, so $\mu=e^{-2\ln|x+1|}=\dfrac1{(x+1)^2}$. Then $\left(\dfrac y{(x+1)^2}\right)'=x+1$, so "
            r"$\dfrac y{(x+1)^2}=\dfrac{(x+1)^2}2+C$ and $y=\dfrac{(x+1)^4}2+C(x+1)^2$.",
            ["The integrating factor is $\\mu=(x+1)^{-2}$."]),
        sol("lin-b", r"$y'-\dfrac yx=\dfrac{x+1}x$", "y1 - y/x - (x + 1)/x", "y = x*ln(abs(x)) - 1 + C*x",
            r"$\mu=e^{-\ln|x|}=\dfrac1x$ and $\left(\dfrac yx\right)'=\dfrac{x+1}{x^2}=\dfrac1x+\dfrac1{x^2}$. Integrate: $\dfrac yx=\ln|x|-\dfrac1x+C$, "
            r"so $y=x\ln|x|-1+Cx$.",
            ["Multiply by $\\mu=1/x$."]),
        sol("lin-c", r"$(x-x^{3})\,y'+(2x^{2}-1)\,y=x^{3}$", "(x - x^3)*y1 + (2*x^2 - 1)*y - x^3", "y = x + C*x*sqrt(1 - x^2)",
            r"Divide by $x(1-x^2)$: $P=\dfrac{2x^2-1}{x(1-x^2)}=-\dfrac1x+\dfrac1{2(1-x)}-\dfrac1{2(1+x)}$. For $0<x<1$ this gives "
            r"$\mu=\dfrac1{x\sqrt{1-x^2}}$. Then $(\mu y)'=\dfrac{x^2}{1-x^2}\cdot\dfrac1{x\sqrt{1-x^2}}=\dfrac x{(1-x^2)^{3/2}}$, so $\mu y=\dfrac1{\sqrt{1-x^2}}+C$ and "
            r"$y=x+Cx\sqrt{1-x^2}$.",
            ["Decompose $\\dfrac{2x^2-1}{x(1-x^2)}$ into partial fractions to integrate it."], sample=(0.2, 0.8)),
        sol("lin-d", r"$y'\cos x+y\sin x=-1$", "y1*cos(x) + y*sin(x) + 1", "y = -sin(x) + C*cos(x)",
            r"Divide by $\cos x$: $y'+\tan x\,y=-\sec x$, with $\mu=e^{\int\tan x\,dx}=\sec x$. Then $(y\sec x)'=-\sec^2x$, so $y\sec x=-\tan x+C$ and "
            r"$y=-\sin x+C\cos x$.",
            ["The integrating factor is $\\mu=\\sec x$."], sample=(0.2, 1.2)),
        sol("lin-e", r"$y'-\dfrac nx\,y=e^{x}x^{n}$, where $n$ is a constant", "y1 - n*y/x - e^x*x^n", "y = x^n*(e^x + C)",
            r"$\mu=e^{-n\ln x}=x^{-n}$, so $\left(x^{-n}y\right)'=e^x$ and $x^{-n}y=e^x+C$, that is $y=x^n(e^x+C)$.",
            ["Here $n$ is given; the integrating factor is $x^{-n}$."], params={"n": 1.5}),
        sol("lin-f", r"$y'+y=e^{-x}$", "y1 + y - e^(-x)", "y = (x + C)*e^(-x)",
            r"$\mu=e^x$ and $(e^xy)'=1$, so $e^xy=x+C$ and $y=(x+C)e^{-x}$.",
            ["Multiply by $e^x$: the right-hand side becomes $1$."]),
        sol("lin-g", r"$y'+\dfrac{1-2x}{x^{2}}\,y-1=0$", "y1 + (1 - 2*x)/x^2*y - 1", "y = x^2*(1 + C*e^(1/x))",
            r"$P=\dfrac1{x^2}-\dfrac2x$, so $\mu=e^{-1/x-2\ln x}=\dfrac{e^{-1/x}}{x^2}$. Then $(\mu y)'=\mu=\dfrac{e^{-1/x}}{x^2}$, and since $\dfrac d{dx}e^{-1/x}=\dfrac{e^{-1/x}}{x^2}$: "
            r"$\mu y=e^{-1/x}+C$. Hence $y=x^2\left(1+Ce^{1/x}\right)$.",
            ["Integrate $P$ term by term: $\\int\\dfrac{dx}{x^2}=-\\dfrac1x$."]),
    ]
    ivp = [
        sol("ivp-a", r"$y'-\dfrac y{1-x^{2}}-1-x=0$, $\ y(0)=0$", "y1 - y/(1 - x^2) - 1 - x",
            "y = sqrt((1+x)/(1-x))*(x*sqrt(1-x^2) + asin(x))/2",
            r"For $|x|<1$, $\mu=e^{-\int\frac{dx}{1-x^2}}=\sqrt{\dfrac{1-x}{1+x}}$. Then $(\mu y)'=\mu(1+x)=\sqrt{1-x^2}$, so "
            r"$\mu y=\dfrac12\left(x\sqrt{1-x^2}+\arcsin x\right)+C$. $y(0)=0$ gives $C=0$, so $y=\sqrt{\dfrac{1+x}{1-x}}\cdot\dfrac{x\sqrt{1-x^2}+\arcsin x}2$.",
            [r"$\int\dfrac{dx}{1-x^2}=\dfrac12\ln\dfrac{1+x}{1-x}$, and $\int\sqrt{1-x^2}\,dx=\dfrac12\left(x\sqrt{1-x^2}+\arcsin x\right)$."],
            sample=(0.1, 0.8), conditions=[("0", "0", 0)]),
        sol("ivp-b", r"$y'-y\tan x=\dfrac1{\cos x}$, $\ y(0)=0$", "y1 - y*tan(x) - 1/cos(x)", "y = x/cos(x)",
            r"$\mu=e^{-\int\tan x\,dx}=\cos x$, so $(y\cos x)'=1$ and $y\cos x=x+C$. $y(0)=0$ gives $C=0$, so $y=\dfrac x{\cos x}$.",
            ["The integrating factor is $\\cos x$."], sample=(0.2, 1.2), conditions=[("0", "0", 0)],
            note=r"The sheet writes $\operatorname{tg}x$ for $\tan x$."),
        sol("ivp-c", r"$xy'+y-e^{x}=0$, $\ y(1)=2$", "x*y1 + y - e^x", "y = (e^x + 2 - e)/x",
            r"The left side of $xy'+y=e^x$ is $(xy)'$, so $xy=e^x+C$. $y(1)=2$ gives $2=e+C$, so $C=2-e$ and $y=\dfrac{e^x+2-e}x$.",
            ["Notice that $xy'+y=(xy)'$."], sample=(0.6, 1.9), conditions=[("1", "2", 0)]),
        sol("ivp-d", r"$xy'+y-e^{x}=0$, $\ y(0)=1$", "x*y1 + y - e^x", "y = (e^x - 1)/x",
            r"As in (c), $xy=e^x+C$. At $x=0$ the left side is $0$, so $0=1+C$ and $C=-1$; then $y=\dfrac{e^x-1}x$, and "
            r"$\lim_{x\to0}\dfrac{e^x-1}x=1=y(0)$, as required. For any other $C$ the solution is unbounded at $x=0$.",
            ["Substitute $x=0$ into $xy=e^x+C$ before dividing by $x$."], sample=(0.3, 1.5), conditions=[("0", "1", 0)],
            note="The initial point is the point where the standard form $y'+\\dfrac yx=\\dfrac{e^x}x$ is undefined, so the usual formula does not apply; only $C=-1$ gives a solution that is finite at $0$."),
    ]
    write_exercises(
        f"{U1}/l04-linear",
        [
            exset("linear", "Solve the linear equation. Give the general solution.", lin, format="Type $y$ as a function of $x$ with an arbitrary constant $C$."),
            exset("linear-ivp", "Solve the initial-value problem.", ivp, format="Type $y$ as a function of $x$."),
        ],
        "mvc_m04.py",
    )


# --- lesson 5: Bernoulli ---------------------------------------------------------------------------------------------------
def build_l05() -> None:
    items = [
        sol("ber-a", r"$y'+xy=x^{3}y^{3}$", "y1 + x*y - x^3*y^3", "1/y^2 = x^2 + 1 + C*e^(x^2)",
            r"Divide by $y^3$ and put $z=y^{-2}$, $z'=-2y^{-3}y'$: $z'-2xz=-2x^3$. With $\mu=e^{-x^2}$: $\left(ze^{-x^2}\right)'=-2x^3e^{-x^2}$, so "
            r"$ze^{-x^2}=(x^2+1)e^{-x^2}+C$ and $\dfrac1{y^2}=x^2+1+Ce^{x^2}$. (The solution $y=0$ is lost when dividing by $y^3$.)",
            ["Put $z=y^{-2}$. Then $z'=-2y^{-3}y'$ and the equation becomes linear in $z$."]),
        sol("ber-b", r"$(1-x^{2})\,y'-xy-xy^{2}=0$", "(1 - x^2)*y1 - x*y - x*y^2", "1/y = C*sqrt(1 - x^2) - 1",
            r"Divide by $y^2$ and put $z=\dfrac1y$: $z'+\dfrac x{1-x^2}\,z=-\dfrac x{1-x^2}$. With $\mu=(1-x^2)^{-1/2}$: $\left(\dfrac z{\sqrt{1-x^2}}\right)'=-\dfrac x{(1-x^2)^{3/2}}$, "
            r"so $\dfrac z{\sqrt{1-x^2}}=-\dfrac1{\sqrt{1-x^2}}+C$ and $\dfrac1y=C\sqrt{1-x^2}-1$.",
            ["Put $z=1/y$, then $z'=-y'/y^2$."], sample=(0.1, 0.8)),
        sol("ber-c", r"$3y^{2}y'-y^{3}-x-1=0$", "3*y^2*y1 - y^3 - x - 1", "y^3 = C*e^x - x - 2",
            r"Put $z=y^3$, $z'=3y^2y'$: $z'-z=x+1$. A particular solution is $z_p=-x-2$ (substitute $Ax+B$), so $z=Ce^x-x-2$ and $y^3=Ce^x-x-2$.",
            ["Here $3y^2y'$ is exactly $z'$ for $z=y^3$."]),
        sol("ber-d", r"$(y\ln x-2)\,y\,dx=x\,dy$", "(y*ln(x) - 2)*y - x*y1", "1/y = ln(x)/2 + 1/4 + C*x^2",
            r"$xy'=y^2\ln x-2y$. Divide by $y^2$ and put $z=\dfrac1y$: $z'-\dfrac2x\,z=-\dfrac{\ln x}x$. With $\mu=x^{-2}$: $\left(\dfrac z{x^2}\right)'=-\dfrac{\ln x}{x^3}$, "
            r"and $\int-\dfrac{\ln x}{x^3}\,dx=\dfrac{\ln x}{2x^2}+\dfrac1{4x^2}$ (by parts). Hence $z=\dfrac{\ln x}2+\dfrac14+Cx^2$.",
            ["Put $z=1/y$. The integral of $\\ln x/x^3$ is done by parts."],
            note=r"The sheet writes $y\,\ell nx$ for $y\ln x$."),
        sol("ber-e", r"$y-y'\cos x=y^{2}\cos x\,(1-\sin x)$", "y - y1*cos(x) - y^2*cos(x)*(1 - sin(x))",
            "1/y = cos(x)*(sin(x) + C)/(1 + sin(x))",
            r"$y'=y\sec x-y^2(1-\sin x)$. Put $z=\dfrac1y$: $z'+\sec x\,z=1-\sin x$. With $\mu=\sec x+\tan x=\dfrac{1+\sin x}{\cos x}$: "
            r"$(\mu z)'=\dfrac{(1+\sin x)(1-\sin x)}{\cos x}=\cos x$, so $\mu z=\sin x+C$ and $\dfrac1y=\dfrac{\cos x\,(\sin x+C)}{1+\sin x}$.",
            ["Put $z=1/y$. The integrating factor of $z'+\\sec x\\,z$ is $\\sec x+\\tan x$."], sample=(0.2, 1.2)),
        sol("ber-f", r"$y'+\dfrac yx=-xy^{2}$", "y1 + y/x + x*y^2", "1/y = x^2 + C*x",
            r"Put $z=\dfrac1y$: $z'-\dfrac zx=x$. With $\mu=\dfrac1x$: $\left(\dfrac zx\right)'=1$, so $z=x(x+C)$ and $\dfrac1y=x^2+Cx$.",
            ["Put $z=1/y$; the equation becomes $z'-z/x=x$."]),
        sol("ber-g", r"$2xyy'-y^{2}+x=0$", "2*x*y*y1 - y^2 + x", "y^2 = x*(C - ln(abs(x)))",
            r"Put $z=y^2$, $z'=2yy'$: $xz'-z+x=0$, so $z'-\dfrac zx=-1$. With $\mu=\dfrac1x$: $\left(\dfrac zx\right)'=-\dfrac1x$, so $\dfrac zx=C-\ln|x|$ and $y^2=x(C-\ln|x|)$.",
            ["Here $2yy'=(y^2)'$, so put $z=y^2$ directly."]),
    ]
    write_exercises(
        f"{U1}/l05-bernoulli",
        [exset("bernoulli", "Integrate the Bernoulli equation.", items, format="Type the relation between $x$ and $y$, with an arbitrary constant $C$.")],
        "mvc_m04.py",
    )


# --- lesson 6: exact -------------------------------------------------------------------------------------------------------
def build_l06() -> None:
    items = [
        sol("exa-a", r"$(x+y)\,dx+(x+2y)\,dy=0$", "(x + y) + (x + 2*y)*y1", "x^2/2 + x*y + y^2 = C",
            r"$M_y=1=N_x$. $F=\int(x+y)\,dx=\dfrac{x^2}2+xy+g(y)$, and $F_y=x+g'(y)=x+2y$ gives $g=y^2$. So $\dfrac{x^2}2+xy+y^2=C$.",
            ["Check $\\dfrac{\\partial M}{\\partial y}=\\dfrac{\\partial N}{\\partial x}$ first."]),
        sol("exa-b", r"$(x^{2}+y^{2}+2x)\,dx+2xy\,dy=0$", "(x^2 + y^2 + 2*x) + 2*x*y*y1", "x^3/3 + x*y^2 + x^2 = C",
            r"$M_y=2y=N_x$. $F=\int M\,dx=\dfrac{x^3}3+xy^2+x^2+g(y)$ and $F_y=2xy+g'=2xy$ gives $g'=0$. So $\dfrac{x^3}3+xy^2+x^2=C$.",
            ["Integrate $M$ with respect to $x$ and compare $F_y$ with $N$."]),
        sol("exa-c", r"$(x^{2}+y)\,dx+(x-2y)\,dy=0$", "(x^2 + y) + (x - 2*y)*y1", "x^3/3 + x*y - y^2 = C",
            r"$M_y=1=N_x$. $F=\dfrac{x^3}3+xy+g(y)$, $F_y=x+g'=x-2y$ gives $g=-y^2$. So $\dfrac{x^3}3+xy-y^2=C$.",
            ["Integrate $M$ with respect to $x$, then find $g(y)$ from $F_y=N$."]),
        sol("exa-d", r"$(x^{3}-3xy^{2}+2)\,dx-(3x^{2}y-y^{2})\,dy=0$", "(x^3 - 3*x*y^2 + 2) - (3*x^2*y - y^2)*y1",
            "x^4/4 - 3*x^2*y^2/2 + 2*x + y^3/3 = C",
            r"$M_y=-6xy=N_x$. $F=\dfrac{x^4}4-\dfrac{3x^2y^2}2+2x+g(y)$ and $F_y=-3x^2y+g'=-3x^2y+y^2$ gives $g=\dfrac{y^3}3$. "
            r"So $\dfrac{x^4}4-\dfrac32x^2y^2+2x+\dfrac{y^3}3=C$.",
            ["Here $N=-(3x^2y-y^2)$; keep the minus sign when you compare $F_y$ with $N$."]),
        sol("exa-e", r"$(\sin xy+xy\cos xy)\,dx+x^{2}\cos xy\,dy=0$", "(sin(x*y) + x*y*cos(x*y)) + x^2*cos(x*y)*y1", "x*sin(x*y) = C",
            r"$M_y=2x\cos xy-x^2y\sin xy=N_x$. It is easier to integrate $N$ with respect to $y$: $F=\int x^2\cos xy\,dy=x\sin xy+h(x)$. "
            r"Then $F_x=\sin xy+xy\cos xy+h'=M$ gives $h'=0$. So $x\sin xy=C$.",
            ["Integrate $N$ with respect to $y$: $\\int x^2\\cos xy\\,dy=x\\sin xy$."]),
    ]
    write_exercises(
        f"{U1}/l06-exact",
        [exset("exact", "Check that the equation is exact and integrate it.", items, format="Type the relation $F(x,y)=C$.")],
        "mvc_m04.py",
    )


# --- unit 2, lesson 1: constant coefficients -----------------------------------------------------------------------------
def build_u2l1() -> None:
    gen = [
        sol("cc-a", r"$y''-5y'+6y=0$", "y2 - 5*y1 + 6*y", "y = C1*e^(2*x) + C2*e^(3*x)",
            r"$r^2-5r+6=(r-2)(r-3)=0$ gives $r=2,3$. So $y=C_1e^{2x}+C_2e^{3x}$.", ["Factor $r^2-5r+6$."], order=2),
        sol("cc-b", r"$y''-9y=0$", "y2 - 9*y", "y = C1*e^(3*x) + C2*e^(-3*x)",
            r"$r^2-9=0$ gives $r=\pm3$. So $y=C_1e^{3x}+C_2e^{-3x}$.", ["$r^2=9$."], order=2),
        sol("cc-c", r"$y''-y'=0$", "y2 - y1", "y = C1 + C2*e^x",
            r"$r^2-r=r(r-1)=0$ gives $r=0,1$. So $y=C_1+C_2e^{x}$.", ["One root is $0$; recall $e^{0x}=1$."], order=2),
        sol("cc-d", r"$y''-2y'+2y=0$", "y2 - 2*y1 + 2*y", "y = e^x*(C1*cos(x) + C2*sin(x))",
            r"$r^2-2r+2=0$ gives $r=1\pm i$, so $\alpha=1$, $\beta=1$ and $y=e^{x}(C_1\cos x+C_2\sin x)$.", ["The discriminant is negative."], order=2),
    ]
    ivp = [
        sol("cc-i", r"$y''-5y'+4y=0$, $\ y(0)=5$, $y'(0)=8$", "y2 - 5*y1 + 4*y", "y = 4*e^x + e^(4*x)",
            r"$r^2-5r+4=(r-1)(r-4)=0$: $y=C_1e^x+C_2e^{4x}$. $y(0)=C_1+C_2=5$ and $y'(0)=C_1+4C_2=8$ give $C_2=1$ and $C_1=4$. So $y=4e^x+e^{4x}$.",
            ["Two equations for $C_1$ and $C_2$: $C_1+C_2=5$ and $C_1+4C_2=8$."], order=2,
            conditions=[("0", "5", 0), ("0", "8", 1)]),
        sol("cc-j", r"$y''+3y'+2y=0$, $\ y(0)=1$, $y'(0)=-1$", "y2 + 3*y1 + 2*y", "y = e^(-x)",
            r"$r^2+3r+2=(r+1)(r+2)=0$: $y=C_1e^{-x}+C_2e^{-2x}$. $y(0)=C_1+C_2=1$ and $y'(0)=-C_1-2C_2=-1$ give $C_2=0$ and $C_1=1$. So $y=e^{-x}$.",
            ["Subtract the two equations for the constants."], order=2,
            conditions=[("0", "1", 0), ("0", "-1", 1)]),
        sol("cc-k", r"$y''+3y=0$, $\ y(0)=0$, $y(3)=0$", "y2 + 3*y", "y = 0",
            r"$r^2+3=0$ gives $r=\pm i\sqrt3$: $y=C_1\cos\sqrt3x+C_2\sin\sqrt3x$. $y(0)=0$ gives $C_1=0$. Then $y(3)=C_2\sin3\sqrt3=0$. "
            r"$\sin3\sqrt3=0$ would need $3\sqrt3=k\pi$ for an integer $k\ne0$, that is $\pi=\dfrac{3\sqrt3}k$, an algebraic number; but $\pi$ is transcendental. So $\sin3\sqrt3\ne0$ and $C_2=0$. "
            r"The only solution of this boundary-value problem is $y=0$.",
            ["Apply $y(0)=0$ first. For the second condition, ask whether $\\sin3\\sqrt3$ is zero."], order=2,
            conditions=[("0", "0", 0), ("3", "0", 0)],
            note="On the printed sheet this exercise is also labelled c. It is a boundary-value problem: the conditions are at two points, and the only solution is the trivial one."),
    ]
    write_exercises(
        f"{U2}/l01-constant-coefficients",
        [
            exset("general", "Find the general solution.", gen, format="Type $y$ as a function of $x$ with arbitrary constants `C1` and `C2`."),
            exset("conditions", "Solve with the given conditions.", ivp, format="Type $y$ as a function of $x$."),
        ],
        "mvc_m04.py",
    )


# --- unit 2, lesson 2: undetermined coefficients --------------------------------------------------------------------------
def build_u2l2() -> None:
    gen = [
        sol("uc-a", r"$y''-7y'+12y=-e^{4x}$", "y2 - 7*y1 + 12*y + e^(4*x)", "y = C1*e^(3*x) + C2*e^(4*x) - x*e^(4*x)",
            r"$r^2-7r+12=0$ gives $r=3,4$. The right side contains $e^{4x}$ with $4$ a root, so try $y_p=Axe^{4x}$: $y_p''-7y_p'+12y_p=A(2\cdot4-7)e^{4x}=Ae^{4x}$. "
            r"So $A=-1$ and $y=C_1e^{3x}+C_2e^{4x}-xe^{4x}$.",
            ["Resonance: $4$ is a root, so multiply the guess by $x$."], order=2),
        sol("uc-b", r"$y''-2y'=x^{2}-1$", "y2 - 2*y1 - x^2 + 1", "y = C1 + C2*e^(2*x) - x^3/6 - x^2/4 + x/4",
            r"$r^2-2r=0$ gives $r=0,2$, so $y_h=C_1+C_2e^{2x}$. A constant is a homogeneous solution, so a polynomial guess needs an extra factor $x$: "
            r"$y_p=Ax^3+Bx^2+Dx$. Then $y_p''-2y_p'=-6Ax^2+(6A-4B)x+(2B-2D)=x^2-1$ gives $A=-\dfrac16$, $B=-\dfrac14$, $D=\dfrac14$.",
            ["The polynomial $Ax^2+Bx+D$ is not enough, because the constant is a solution of the homogeneous equation. Try $x(Ax^2+Bx+D)$."], order=2),
        sol("uc-c", r"$y''-2y'=e^{2x}+5$", "y2 - 2*y1 - e^(2*x) - 5", "y = C1 + C2*e^(2*x) + x*e^(2*x)/2 - 5*x/2",
            r"$y_h=C_1+C_2e^{2x}$. Treat the two terms separately. For $e^{2x}$ ($2$ is a root): $y_1=Axe^{2x}$ gives $A(2\cdot2-2)e^{2x}=2Ae^{2x}$, so $A=\dfrac12$. "
            r"For $5$ ($0$ is a root): $y_2=Bx$ gives $-2B=5$, so $B=-\dfrac52$.",
            ["Both terms of the right side resonate with a root: use $Axe^{2x}$ and $Bx$."], order=2),
        sol("uc-g", r"$y''+2y'+y=e^{x}+e^{-x}$", "y2 + 2*y1 + y - e^x - e^(-x)", "y = (C1 + C2*x)*e^(-x) + e^x/4 + x^2*e^(-x)/2",
            r"$(r+1)^2=0$: $y_h=(C_1+C_2x)e^{-x}$. For $e^x$ ($1$ is not a root): $Ae^x$ gives $4Ae^x=e^x$, $A=\dfrac14$. "
            r"For $e^{-x}$ ($-1$ is a double root): $Bx^2e^{-x}$ gives $2Be^{-x}=e^{-x}$, $B=\dfrac12$.",
            ["For a double root the guess is multiplied by $x^2$."], order=2),
        sol("uc-h", r"$y''-2y'+10y=\sin3x+e^{x}$", "y2 - 2*y1 + 10*y - sin(3*x) - e^x",
            "y = e^x*(C1*cos(3*x) + C2*sin(3*x)) + (6*cos(3*x) + sin(3*x))/37 + e^x/9",
            r"$r^2-2r+10=0$ gives $r=1\pm3i$: $y_h=e^x(C_1\cos3x+C_2\sin3x)$. For $\sin3x$ ($3i$ is not a root): $A\cos3x+B\sin3x$ gives "
            r"$(A-6B)\cos3x+(6A+B)\sin3x=\sin3x$, so $A=\dfrac6{37}$ and $B=\dfrac1{37}$. For $e^x$: $De^x$ gives $9De^x=e^x$, so $D=\dfrac19$.",
            ["Use both $\\cos3x$ and $\\sin3x$ in the guess, even though the right side has only $\\sin3x$."], order=2),
        sol("uc-i", r"$y''-3y'=x+\cos x$", "y2 - 3*y1 - x - cos(x)", "y = C1 + C2*e^(3*x) - x^2/6 - x/9 - cos(x)/10 - 3*sin(x)/10",
            r"$y_h=C_1+C_2e^{3x}$. For $x$ ($0$ is a root): $Ax^2+Bx$ gives $2A-3B-6Ax=x$, so $A=-\dfrac16$ and $B=-\dfrac19$. "
            r"For $\cos x$: $D\cos x+E\sin x$ gives $(-D-3E)\cos x+(3D-E)\sin x=\cos x$, so $D=-\dfrac1{10}$ and $E=-\dfrac3{10}$.",
            ["For the term $x$, the polynomial guess must be multiplied by $x$."], order=2),
        sol("uc-j", r"$y''-2y'=e^{2x}$, $\ y(0)=\dfrac18$, $y'(0)=1$", "y2 - 2*y1 - e^(2*x)", "y = -1/8 + e^(2*x)/4 + x*e^(2*x)/2",
            r"General solution (as in part c): $y=C_1+C_2e^{2x}+\dfrac12xe^{2x}$. $y(0)=C_1+C_2=\dfrac18$. "
            r"$y'=2C_2e^{2x}+\dfrac12e^{2x}+xe^{2x}$, so $y'(0)=2C_2+\dfrac12=1$ and $C_2=\dfrac14$, $C_1=-\dfrac18$.",
            ["Find the general solution first, then apply both conditions."], order=2,
            conditions=[("0", "1/8", 0), ("0", "1", 1)]),
        sol("uc-k", r"$y''+4y=\sin x$, $\ y(0)=y'(0)=1$", "y2 + 4*y - sin(x)", "y = cos(2*x) + sin(2*x)/3 + sin(x)/3",
            r"$y_h=C_1\cos2x+C_2\sin2x$. Try $y_p=A\sin x$: $(-1+4)A\sin x=\sin x$, so $A=\dfrac13$. $y(0)=C_1=1$. "
            r"$y'=-2C_1\sin2x+2C_2\cos2x+\dfrac13\cos x$, so $y'(0)=2C_2+\dfrac13=1$ and $C_2=\dfrac13$.",
            ["Because the right side is $\\sin x$ and not $\\sin2x$, there is no resonance."], order=2,
            conditions=[("0", "1", 0), ("0", "1", 1)]),
    ]
    write_exercises(
        f"{U2}/l02-undetermined-coefficients",
        [exset("undetermined", "Solve with the method of undetermined coefficients.", gen,
               format="Type $y$ as a function of $x$, with `C1` and `C2` when the problem has no conditions.")],
        "mvc_m04.py",
    )


# --- unit 2, lesson 3: variation of parameters ---------------------------------------------------------------------------
def build_u2l3() -> None:
    items = [
        sol("var-a", r"$y''+y=\tan x$", "y2 + y - tan(x)", "y = C1*cos(x) + C2*sin(x) - cos(x)*ln(sec(x) + tan(x))",
            r"$y_1=\cos x$, $y_2=\sin x$, $W=1$. $u_1'=-\sin x\tan x=\cos x-\sec x$ and $u_2'=\sin x$, so $u_1=\sin x-\ln(\sec x+\tan x)$ and $u_2=-\cos x$. "
            r"Then $y_p=u_1\cos x+u_2\sin x=-\cos x\,\ln(\sec x+\tan x)$.",
            ["$W=1$. Use $\\int\\sec x\\,dx=\\ln(\\sec x+\\tan x)$."], order=2, sample=(0.2, 1.3)),
        sol("var-b", r"$y''+y=\cot x$", "y2 + y - cot(x)", "y = C1*cos(x) + C2*sin(x) + sin(x)*ln(tan(x/2))",
            r"$W=1$. $u_1'=-\sin x\cot x=-\cos x$, so $u_1=-\sin x$. $u_2'=\cos x\cot x=\dfrac{\cos^2x}{\sin x}=\csc x-\sin x$, so $u_2=\ln\tan\dfrac x2+\cos x$. "
            r"Then $y_p=-\sin x\cos x+\sin x\ln\tan\dfrac x2+\sin x\cos x=\sin x\,\ln\tan\dfrac x2$, for $0<x<\pi$.",
            ["$\\int\\csc x\\,dx=\\ln\\tan\\dfrac x2$."], order=2, sample=(0.4, 2.6),
            note=r"The sheet writes $\operatorname{cotg}x$ for $\cot x$."),
        sol("var-c", r"$y''+2y'+y=\dfrac{e^{-x}}x$", "y2 + 2*y1 + y - e^(-x)/x", "y = (C1 + C2*x)*e^(-x) + x*e^(-x)*ln(x)",
            r"$y_1=e^{-x}$, $y_2=xe^{-x}$, $W=e^{-2x}$. $u_1'=-\dfrac{xe^{-x}\cdot e^{-x}/x}{e^{-2x}}=-1$ and $u_2'=\dfrac{e^{-x}\cdot e^{-x}/x}{e^{-2x}}=\dfrac1x$, "
            r"so $u_1=-x$ and $u_2=\ln x$. Then $y_p=-xe^{-x}+xe^{-x}\ln x$; the term $-xe^{-x}$ belongs to $y_h$, so it is absorbed in $C_2$.",
            ["Compute $W$ first: $W=e^{-2x}$."], order=2),
        sol("var-d", r"$y''=-y+\sec x$", "y2 + y - sec(x)", "y = C1*cos(x) + C2*sin(x) + cos(x)*ln(cos(x)) + x*sin(x)",
            r"$W=1$. $u_1'=-\sin x\sec x=-\tan x$ and $u_2'=\cos x\sec x=1$, so $u_1=\ln\cos x$ and $u_2=x$. So $y_p=\cos x\ln\cos x+x\sin x$.",
            ["$u_1'=-\\tan x$, $u_2'=1$."], order=2, sample=(0.2, 1.3),
            note=r"The sheet prints $y''=y+\sec x$, that is $y''-y=\sec x$, whose solution needs $\int e^{\pm x}\sec x\,dx$, which is not elementary. "
                 r"The equation is read here as $y''=-y+\sec x$, i.e. $y''+y=\sec x$, as in the other exercises of this group."),
        sol("var-e", r"$y''+y=\csc x$", "y2 + y - 1/sin(x)", "y = C1*cos(x) + C2*sin(x) - x*cos(x) + sin(x)*ln(sin(x))",
            r"$W=1$. $u_1'=-\sin x\csc x=-1$ and $u_2'=\cos x\csc x=\cot x$, so $u_1=-x$ and $u_2=\ln\sin x$. So $y_p=-x\cos x+\sin x\ln\sin x$, for $0<x<\pi$.",
            ["$u_1'=-1$ and $u_2'=\\cot x$."], order=2, sample=(0.4, 2.6),
            note=r"The sheet writes $\operatorname{cosec}x$ for $\csc x$."),
        sol("var-f", r"$y''-2y=4x^{2}e^{2x}$", "y2 - 2*y - 4*x^2*e^(2*x)",
            "y = C1*e^(sqrt(2)*x) + C2*e^(-sqrt(2)*x) + e^(2*x)*(2*x^2 - 8*x + 14)",
            r"$r^2-2=0$ gives $r=\pm\sqrt2$, so $y_h=C_1e^{\sqrt2x}+C_2e^{-\sqrt2x}$. Variation of parameters leads to the integrals "
            r"$\int x^2e^{(2\mp\sqrt2)x}\,dx$, which are long. Because the right side is $e^{2x}$ times a polynomial and $2$ is not a root, a shortcut gives the same $y_p$: "
            r"$y_p=e^{2x}q(x)$ with $q=Ax^2+Bx+D$. Then $y_p''-2y_p=e^{2x}\left(q''+4q'+2q\right)=4x^2e^{2x}$, so $2A=4$, $8A+2B=0$, $2A+4B+2D=0$: $A=2$, $B=-8$, $D=14$.",
            ["Try $y_p=e^{2x}(Ax^2+Bx+D)$: the right side has this form."], order=2,
            note="Both methods give the same particular solution; here undetermined coefficients is shorter."),
    ]
    write_exercises(
        f"{U2}/l03-variation-of-parameters",
        [exset("variation", "Solve with variation of parameters.", items, format="Type $y$ as a function of $x$ with `C1` and `C2`.")],
        "mvc_m04.py",
    )


def build() -> None:
    build_l01()
    build_l02()
    build_l03()
    build_l04()
    build_l05()
    build_l06()
    build_u2l1()
    build_u2l2()
    build_u2l3()
