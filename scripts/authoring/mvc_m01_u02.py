"""Exercises of Course 2, Module 1, Unit 2: partial derivatives, total differential, chain rule,
second-order derivatives and implicit differentiation (sheet parts A.IV to A.VII)."""

from __future__ import annotations

import sympy as sp
from toolkit import P, check_partial, dtex, eng, ex, exset, simp, t, tex, u, v, write_exercises, x, y, z, r

BASE = "mvc/m01-derivatives/u02-partial-differentiation"
PTS = [{x: 1.3, y: 0.7, z: 1.9}, {x: 2.1, y: 1.4, z: 0.8}, {x: 1.7, y: 0.9, z: 1.2}]


def vec(comps: list[sp.Expr]) -> str:
    return "(" + ", ".join(eng(c) for c in comps) + ")"


def pd(name: str, var: str) -> str:
    return rf"\pd{{{name}}}{{{var}}}"


# --- A.IV first-order partial derivatives -------------------------------------------------------------------
def first_order_items() -> list[dict]:
    spec = [
        ("par-01", "z", r"x^2+y^2-3xy", "x^2+y^2-3*x*y", "xy", "Differentiate term by term; in $\\pd zx$ the variable $y$ is a constant."),
        ("par-02", "z", r"x^y", "x^y", "xy",
         "In $\\pd zx$ the exponent $y$ is a constant (power rule). In $\\pd zy$ the base $x$ is a constant: $\\dfrac{d}{dy}a^y=a^y\\ln a$."),
        ("par-03", "z", r"\arctan\dfrac yx", "atan(y/x)", "xy",
         "Use $\\dfrac{d}{du}\\arctan u=\\dfrac1{1+u^2}$ with $u=\\dfrac yx$, then multiply by the derivative of $u$."),
        ("par-04", "z", r"e^{\sin\frac yx}", "e^(sin(y/x))", "xy",
         "Apply the chain rule twice: the exponential, then the sine, then $\\dfrac yx$."),
        ("par-05", "z", r"\ln\left(x+\sqrt{x^2+y^2}\right)", "ln(x+sqrt(x^2+y^2))", "xy",
         "$\\dfrac{d}{du}\\ln u=\\dfrac{u'}{u}$ with $u=x+\\sqrt{x^2+y^2}$."),
        ("par-06", "z", r"\dfrac{x-y}{x+y}", "(x-y)/(x+y)", "xy", "Use the quotient rule."),
        ("par-07", "z", r"\dfrac{x}{\sqrt{x^2+y^2}}", "x/sqrt(x^2+y^2)", "xy",
         "Write $z=x\\,(x^2+y^2)^{-1/2}$ and use the product rule in $x$."),
        ("par-08", "z", r"\arcsin\sqrt{\dfrac{x^2-y^2}{x^2+y^2}}", "asin(sqrt((x^2-y^2)/(x^2+y^2)))", "xy",
         "Chain rule with $\\dfrac{d}{du}\\arcsin u=\\dfrac1{\\sqrt{1-u^2}}$ and the square root. Work where $x>|y|$."),
        ("par-09", "u", r"(xy)^z", "(x*y)^z", "xyz",
         "Write $(xy)^z=e^{z\\ln(xy)}$, or use the power rule for $x$ and $y$ and the exponential rule for $z$."),
        ("par-10", "u", r"z^{xy}", "z^(x*y)", "xyz",
         "Write $z^{xy}=e^{xy\\ln z}$. For $\\pd uz$ use the power rule."),
        ("par-11", "u", r"xz\arctan\dfrac yz", "x*z*atan(y/z)", "xyz",
         "Product rule, and $\\dfrac{d}{dw}\\arctan w=\\dfrac1{1+w^2}$ with $w=\\dfrac yz$."),
        ("par-12", "u", r"x^2y+yz^2+x^2z+xyz", "x^2*y+y*z^2+x^2*z+x*y*z", "xyz", "Differentiate term by term."),
        ("par-13", "u", r"2y^2+z^2-xy-yz+2x", "2*y^2+z^2-x*y-y*z+2*x", "xyz", "Differentiate term by term."),
    ]
    items = []
    for id_, name, latex, fn, names, hint in spec:
        f = P(fn)
        syms = [sp.Symbol(c, real=True) for c in names]
        comps = [simp(sp.diff(f, s)) for s in syms]
        for s, c in zip(syms, comps, strict=True):
            check_partial(f, s, c, PTS)
        lines = "\n\n".join(rf"$${pd(name, s.name)}={dtex(c)}$$" for s, c in zip(syms, comps, strict=True))
        solution = (
            "Differentiate with respect to each variable in turn, treating the other variables as constants.\n\n"
            + lines
            + ("\n\nIn $\\pd zx$ and $\\pd zy$ the results are valid where the function is defined." if False else "")
        )
        items.append(
            ex(id_, f"${name}={latex}$", "vector", vec(comps), variables=list(names), hints=[hint], solution=solution,
               verify=[{"expr": f"diff({fn}, {s.name})", "equals": eng(c)} for s, c in zip(syms, comps, strict=True)])
        )
    return items


# --- A.IV total differential ------------------------------------------------------------------------------------
def differential_items() -> list[dict]:
    spec = [
        ("dif-01", "z", r"x^2y^2", "x^2*y^2", "xy", "Find $z_x$ and $z_y$; the coefficients of $dx$ and $dy$ are exactly these.", ""),
        ("dif-02", "z", r"\sin^2x+\cos^2y", "sin(x)^2+cos(y)^2", "xy", "$\\dfrac{d}{dx}\\sin^2x=2\\sin x\\cos x$.", ""),
        ("dif-03", "z", r"\ln\tan\dfrac yx", "ln(tan(y/x))", "xy", "Chain rule: $\\dfrac{d}{du}\\ln\\tan u=\\dfrac{1}{\\sin u\\cos u}$ with $u=\\dfrac yx$.", ""),
        ("dif-04", "z", r"yx^y", "y*x^y", "xy", "Product rule in $y$; the exponent $y$ also appears in $x^y$.", ""),
        ("dif-05", "z", r"\dfrac{x^2-y^2}{x^2+y^2}", "(x^2-y^2)/(x^2+y^2)", "xy", "Quotient rule.", ""),
        ("dif-06", "z", r"\arctan\dfrac yx+\arctan\dfrac xy", "atan(y/x)+atan(x/y)", "xy",
         "Compute $z_x$ and $z_y$ carefully, and compare the two arctangent terms.",
         "\n\nThis is not an accident: for $x,y>0$ we have $\\arctan\\dfrac yx+\\arctan\\dfrac xy=\\dfrac\\pi2$, so the function is constant "
         "on each quadrant, and a constant has differential $0$."),
        ("dif-07", "u", r"\dfrac{z}{\sqrt{x^2+y^2}}", "z/sqrt(x^2+y^2)", "xyz", "Treat $z$ as a constant when differentiating in $x$ and $y$.", ""),
        ("dif-08", "u", r"yxz", "y*x*z", "xyz", "Each partial derivative is the product of the other two variables.", ""),
    ]
    items = []
    for id_, name, latex, fn, names, hint, extra in spec:
        f = P(fn)
        syms = [sp.Symbol(c, real=True) for c in names]
        comps = [simp(sp.diff(f, s)) for s in syms]
        pts = [{x: 2.1, y: 1.0, z: 1.3}, {x: 1.6, y: 0.7, z: 0.9}] if id_ == "dif-03" else PTS
        for s, c in zip(syms, comps, strict=True):
            check_partial(f, s, c, pts)
        d = " + ".join(
            rf"\left({dtex(c)}\right)\,d{s.name}" if c != 0 else "0" for s, c in zip(syms, comps, strict=True)
        )
        if all(c == 0 for c in comps):
            d = "0"
        solution = (
            "The total differential is the sum of each partial derivative times the differential of its variable.\n\n"
            + "\n\n".join(rf"$${pd(name, s.name)}={dtex(c)}$$" for s, c in zip(syms, comps, strict=True))
            + f"\n\nTherefore $$d{name}={d}.$$"
            + extra
        )
        items.append(
            ex(id_, f"${name}={latex}$", "vector", vec(comps), variables=list(names), hints=[hint], solution=solution,
               verify=[{"expr": f"diff({fn}, {s.name})", "equals": eng(c)} for s, c in zip(syms, comps, strict=True)])
        )
    return items


# --- A.V chain rule ----------------------------------------------------------------------------------------------
def chain_items() -> list[dict]:
    items: list[dict] = []
    a, b = sp.symbols("a b", positive=True)

    def one_param(id_, name, latex_f, fn, subs_latex, subs, tpts, hint, note=None, params=None):
        """dz/dt for z = f(x,y[,z]) with x=x(t), ... ; subs: dict Symbol -> expr(t)."""
        f = P(fn)
        syms = [s for s in (x, y, z) if s in subs]
        composite = f.subs(subs)
        total = simp(sp.diff(composite, t))
        extra = params or {}
        check_partial(composite.subs(extra), t, total.subs(extra), [{t: tv} for tv in tpts])
        partials = {s: simp(sp.diff(f, s)) for s in syms}
        chain_terms = " + ".join(rf"{pd(name, s.name)}\,\dfrac{{d{s.name}}}{{dt}}" for s in syms)
        steps = (
            f"By the chain rule, $$\\dfrac{{d{name}}}{{dt}}={chain_terms}.$$\n\n"
            + "The ingredients are\n\n"
            + "\n\n".join(rf"$${pd(name, s.name)}={dtex(partials[s])},\qquad \dfrac{{d{s.name}}}{{dt}}={dtex(sp.diff(subs[s], t))}$$" for s in syms)
            + f"\n\nSubstituting $x,y,z$ by their expressions in $t$ and simplifying, $$\\dfrac{{d{name}}}{{dt}}={dtex(total)}.$$"
        )
        item_vars = ["t"] + [str(s) for s in total.free_symbols if s.name in ("a", "b")]
        out = ex(
            id_, rf"$\dfrac{{d{name}}}{{dt}}$ if ${name}={latex_f}$, where {subs_latex}",
            "expression" if total.free_symbols else "number", eng(total),
            variables=sorted(set(item_vars)), hints=[hint], solution=steps,
            verify=[{"expr": f"diff({eng(composite)}, t)", "equals": eng(total)}],
            **({"note": note} if note else {}),
        )
        items.append(out)

    one_param("cha-01", "z", r"\dfrac xy", "x/y", r"$x=e^t$, $y=\ln t$", {x: sp.exp(t), y: sp.log(t)}, [1.3, 2.2, 3.1],
              "Write $\\dfrac{dz}{dt}=z_x\\,x'+z_y\\,y'$ with $z_x=\\dfrac1y$ and $z_y=-\\dfrac{x}{y^2}$.")
    one_param("cha-02", "z", r"\ln\sin\dfrac{x}{\sqrt y}", "ln(sin(x/sqrt(y)))", r"$x=3t^2$, $y=\sqrt{t^2+1}$",
              {x: 3 * t**2, y: sp.sqrt(t**2 + 1)}, [0.31, 0.42, 0.5],
              "Chain rule on $\\ln\\sin u$ with $u=\\dfrac{x}{\\sqrt y}$: $\\dfrac{d}{du}\\ln\\sin u=\\cot u$.")
    one_param("cha-03", "z", r"x^y", "x^y", r"$x=\sin t$, $y=\cos t$", {x: sp.sin(t), y: sp.cos(t)}, [0.4, 0.9, 1.2],
              "$z_x=yx^{y-1}$ and $z_y=x^y\\ln x$. Then multiply by $\\cos t$ and $-\\sin t$.")
    one_param("cha-04", "u", r"xyz", "x*y*z", r"$x=t+1$, $y=\ln t$, $z=\tan t$",
              {x: t + 1, y: sp.log(t), z: sp.tan(t)}, [0.5, 0.8, 1.1],
              "Product rule through the chain rule: $u_x=yz$, $u_y=xz$, $u_z=xy$.",
              note="On the printed sheet the second condition is mixed with a fraction symbol. It is read here as $y=\\ln t$.")
    one_param("cha-05", "u", r"\dfrac{z}{\sqrt{x^2+y^2}}", "z/sqrt(x^2+y^2)", r"$x=a\cos t$, $y=a\sin t$, $z=b$",
              {x: a * sp.cos(t), y: a * sp.sin(t), z: b}, [0.4, 0.9, 1.2],
              "Simplify first: what is $x^2+y^2$ when $x=a\\cos t$ and $y=a\\sin t$?",
              note="The printed line also contains the letters $xyz$ after the fraction. They are read here as a typing slip, and $u=\\dfrac{z}{\\sqrt{x^2+y^2}}$.",
              params={a: 2, b: 3})

    # 6: z = arctan(x/y), x = u sin v, y = u cos v
    f = P("atan(x/y)")
    subs = {x: u * sp.sin(v), y: u * sp.cos(v)}
    comp = f.subs(subs)
    zu, zv = simp(sp.diff(comp, u)), simp(sp.diff(comp, v))
    check_partial(comp, u, zu, [{u: 1.3, v: 0.4}, {u: 2.2, v: 0.9}])
    check_partial(comp, v, zv, [{u: 1.3, v: 0.4}, {u: 2.2, v: 0.9}])
    items.append(ex(
        "cha-06", r"$\pd zu,\ \pd zv$ if $z=\arctan\dfrac xy$, where $x=u\sin v$, $y=u\cos v$", "vector", vec([zu, zv]),
        variables=["u", "v"],
        hints=["Use the chain rule with $z_x=\\dfrac{y}{x^2+y^2}$ and $z_y=-\\dfrac{x}{x^2+y^2}$, or simplify $\\dfrac xy$ first."],
        solution=(
            r"$z_x=\dfrac{y}{x^2+y^2}$ and $z_y=-\dfrac{x}{x^2+y^2}$, with $x_u=\sin v$, $x_v=u\cos v$, $y_u=\cos v$, $y_v=-u\sin v$. "
            r"Since $x^2+y^2=u^2$:" + "\n\n"
            r"$$\pd zu=\dfrac{u\cos v}{u^2}\sin v-\dfrac{u\sin v}{u^2}\cos v=0,$$" + "\n\n"
            r"$$\pd zv=\dfrac{u\cos v}{u^2}\,u\cos v+\dfrac{u\sin v}{u^2}\,u\sin v=\cos^2v+\sin^2v=1.$$" + "\n\n"
            r"Check by substitution: $\dfrac xy=\tan v$, so $z=\arctan(\tan v)=v$ for $|v|<\dfrac\pi2$, which gives $z_u=0$ and $z_v=1$."
        ),
    ))

    # 7: spherical coordinates, nine partial derivatives
    X, Y, Z = r * sp.sin(u) * sp.cos(v), r * sp.sin(u) * sp.sin(v), r * sp.cos(u)
    order = [(X, r), (Y, r), (Z, r), (X, u), (Y, u), (Z, u), (X, v), (Y, v), (Z, v)]
    comps = [simp(sp.diff(F, w)) for F, w in order]
    names = ["x", "y", "z"]
    rows = []
    for w in (r, u, v):
        for nm, F in zip(names, (X, Y, Z), strict=True):
            rows.append(rf"$\pd{{{nm}}}{{{w.name}}}={tex(simp(sp.diff(F, w)))}$")
    items.append(ex(
        "cha-07",
        r"$\pd xr,\ \pd yr,\ \pd zr,\ \pd xu,\ \pd yu,\ \pd zu,\ \pd xv,\ \pd yv,\ \pd zv$ if $x=r\sin u\cos v$, $y=r\sin u\sin v$, $z=r\cos u$",
        "vector", vec(comps), variables=["r", "u", "v"],
        hints=["Each of the nine derivatives is an ordinary derivative: the other two letters are constants."],
        solution=(
            "Differentiate each coordinate with respect to $r$, $u$ and $v$ in turn, treating the other two as constants:\n\n"
            + "\n\n".join(rows)
            + "\n\nThese nine numbers form the matrix of derivatives of spherical coordinates. Its determinant, $r^2\\sin u$ up to sign, "
            "is the factor you will meet in triple integrals."
        ),
        note=None,
    ))
    return items


# --- A.VI second-order derivatives ----------------------------------------------------------------------------
def second_order_items() -> list[dict]:
    spec = [
        ("sec-01", "z", r"x^2+y^2-3xy", "x^2+y^2-3*x*y", "xy"),
        ("sec-02", "z", r"x^y", "x^y", "xy"),
        ("sec-03", "z", r"\arctan\dfrac yx", "atan(y/x)", "xy"),
        ("sec-04", "z", r"\sin x\sin y\sin(x+y)", "sin(x)*sin(y)*sin(x+y)", "xy"),
        ("sec-05", "u", r"\sqrt{x^2+y^2+z^2}", "sqrt(x^2+y^2+z^2)", "xyz"),
        ("sec-06", "u", r"z^{xy}", "z^(x*y)", "xyz"),
        ("sec-07", "u", r"xz\arctan\dfrac yz", "x*z*atan(y/z)", "xyz"),
        ("sec-08", "u", r"x^2y+yz^2+x^2z+xyz", "x^2*y+y*z^2+x^2*z+x*y*z", "xyz"),
    ]
    items = []
    for id_, name, latex, fn, names in spec:
        f = P(fn)
        syms = [sp.Symbol(c, real=True) for c in names]
        if len(syms) == 2:
            pairs = [(syms[0], syms[0]), (syms[0], syms[1]), (syms[1], syms[1])]
            label = f"(z_{{xx}},\\ z_{{xy}},\\ z_{{yy}})"
        else:
            pairs = [(syms[0], syms[0]), (syms[1], syms[1]), (syms[2], syms[2]), (syms[0], syms[1]), (syms[0], syms[2]), (syms[1], syms[2])]
            label = "(u_{xx},\\ u_{yy},\\ u_{zz},\\ u_{xy},\\ u_{xz},\\ u_{yz})"
        comps = []
        lines = []
        for p, q in pairs:
            first = sp.diff(f, p)
            second = simp(sp.diff(first, q))
            # Schwarz: the other order must give the same function
            assert simp(sp.diff(sp.diff(f, q), p) - second) == 0, (id_, p, q)
            check_partial(first, q, second, PTS)
            comps.append(second)
            sub = f"{p.name}{q.name}"
            sub_label = f"{name}_{{{sub}}}"
            lines.append(rf"$${sub_label}={dtex(second)}$$")
        first_lines = "\n\n".join(
            rf"$${pd(name, s.name)}={dtex(simp(sp.diff(f, s)))}$$" for s in syms
        )
        solution = (
            "First compute the first-order partial derivatives:\n\n" + first_lines
            + "\n\nThen differentiate each of them again. The mixed derivatives do not depend on the order of differentiation (Schwarz's theorem), so one order is enough:\n\n"
            + "\n\n".join(lines)
        )
        items.append(
            ex(id_, f"${name}={latex}$", "vector", vec(comps), variables=list(names),
               hints=["Compute the first derivatives first, then differentiate each of them again."], solution=solution)
        )
    return items


# --- A.VII implicit differentiation -----------------------------------------------------------------------------
def implicit_items() -> list[dict]:
    items = []
    a, b = sp.symbols("a b", real=True)

    y1 = sp.Symbol("y1", real=True)

    def curve(id_, latex_eq, F, ranges, hint, notes=None):
        yp = simp(-sp.diff(F, x) / sp.diff(F, y))
        # second derivative: d/dx of y' with y = y(x); the compact form keeps y' as the symbol y1
        ypp = simp(sp.diff(yp, x) + sp.diff(yp, y) * y1)
        answer = vec([yp, ypp])
        names = ["x", "y", "y1"] + [s.name for s in (a, b) if s in F.free_symbols]
        solution = (
            rf"With $F(x,y)={tex(F)}$ we get $F_x={tex(simp(sp.diff(F, x)))}$ and $F_y={tex(simp(sp.diff(F, y)))}$." + "\n\n"
            rf"$$\dfrac{{dy}}{{dx}}=-\dfrac{{F_x}}{{F_y}}={dtex(yp)}.$$" + "\n\n"
            r"For the second derivative, differentiate $y'$ with respect to $x$. Since $y$ depends on $x$, the chain rule gives "
            r"$y''=\dfrac{\partial y'}{\partial x}+\dfrac{\partial y'}{\partial y}\,y'$, that is" + "\n\n"
            rf"$$\dfrac{{d^2y}}{{dx^2}}={dtex(ypp.subs(y1, sp.Symbol(chr(121) + chr(39), real=True)))}.$$" + "\n\n"
            r"Here $y'$ is the first derivative found above. You may leave $y'$ in the answer, or replace it by its formula: on the curve "
            r"both forms have the same values, and any such form is accepted."
        )
        out = ex(
            id_, rf"$\dfrac{{dy}}{{dx}}$ and $\dfrac{{d^2y}}{{dx^2}}$ if {latex_eq}", "vector", answer, variables=names,
            constraint={"equation": eng(F), "solveFor": "y", "ranges": ranges, "substitutions": {"y1": eng(yp)}},
            hints=[hint], solution=solution,
        )
        if notes:
            out["note"] = notes
        items.append(out)

    curve("imp-01", r"$y=1+y^x$", y - 1 - y**x, {"x": [0.2, 0.8]},
          "Write the equation as $F(x,y)=y-1-y^x=0$. The derivative of $y^x$ with respect to $y$ is $xy^{x-1}$, and with respect to $x$ it is $y^x\\ln y$.")
    curve("imp-02", r"$e^x\sin y+e^y\sin x=1$", sp.exp(x) * sp.sin(y) + sp.exp(y) * sp.sin(x) - 1, {"x": [0.1, 0.5]},
          "Take $F=e^x\\sin y+e^y\\sin x-1$ and use $y'=-\\dfrac{F_x}{F_y}$.")
    curve("imp-03", r"$\dfrac{x^2}{a^2}+\dfrac{y^2}{b^2}=1$", x**2 / a**2 + y**2 / b**2 - 1, {"x": [0.1, 0.5], "a": [1.0, 2.0], "b": [1.0, 2.0]},
          "For the ellipse $F_x=\\dfrac{2x}{a^2}$ and $F_y=\\dfrac{2y}{b^2}$.")

    def surface(id_, latex_eq, F, ranges, hint):
        zx = simp(-sp.diff(F, x) / sp.diff(F, z))
        zy = simp(-sp.diff(F, y) / sp.diff(F, z))
        solution = (
            rf"With $F(x,y,z)={tex(F)}$ we get $F_x={tex(simp(sp.diff(F, x)))}$, $F_y={tex(simp(sp.diff(F, y)))}$, $F_z={tex(simp(sp.diff(F, z)))}$." + "\n\n"
            rf"$$\pd zx=-\dfrac{{F_x}}{{F_z}}={dtex(zx)},\qquad \pd zy=-\dfrac{{F_y}}{{F_z}}={dtex(zy)}.$$"
        )
        items.append(ex(
            id_, rf"$\pd zx$ and $\pd zy$ if {latex_eq}", "vector", vec([zx, zy]), variables=["x", "y", "z"],
            constraint={"equation": eng(F), "solveFor": "z", "ranges": ranges}, hints=[hint], solution=solution,
        ))

    surface("imp-04", r"$x\cos y+y\cos z+z\cos x=1$", x * sp.cos(y) + y * sp.cos(z) + z * sp.cos(x) - 1, {"x": [0.1, 0.4], "y": [0.1, 0.4]},
            "Take $F=x\\cos y+y\\cos z+z\\cos x-1$ and compute $F_x$, $F_y$, $F_z$.")
    surface("imp-05", r"$x^2+y^2-z^2-xy=0$", x**2 + y**2 - z**2 - x * y, {"x": [0.5, 2.0], "y": [0.5, 2.0]},
            "Take $F=x^2+y^2-z^2-xy$; note that $F_z=-2z$.")
    return items


def build() -> None:
    first_format = (
        "Type the partial derivatives as a vector, in the order of the variables: `(derivative in x, derivative in y)`, "
        "and a third entry for $z$ when the function has three variables. For example `(2*x, 3*y)`."
    )
    write_exercises(
        f"{BASE}/l01-partial-derivatives",
        [
            exset("first-order", "Calculate the partial derivatives of the first order of each function.", first_order_items(), format=first_format),
            exset(
                "differentials", "Find the total differential of each function.", differential_items(),
                format="Write $dz=A\\,dx+B\\,dy$ and type the coefficients as a vector `(A, B)`. For a function $u$ of three variables type `(A, B, C)`.",
            ),
        ],
        "mvc_m01_u02.py",
    )
    write_exercises(
        f"{BASE}/l02-chain-rule",
        [exset("compound", "Find the derivatives of the following compound functions.", chain_items(),
               format="Type an expression in $t$ (or in $a$, $b$, $t$), or a vector of expressions when several derivatives are asked.")],
        "mvc_m01_u02.py",
    )
    write_exercises(
        f"{BASE}/l03-higher-order-derivatives",
        [exset(
            "second-order", "Calculate the partial derivatives of the second order of each function.", second_order_items(),
            format="For $z=f(x,y)$ type `(z_xx, z_xy, z_yy)`. For $u=f(x,y,z)$ type `(u_xx, u_yy, u_zz, u_xy, u_xz, u_yz)`, in this order.",
        )],
        "mvc_m01_u02.py",
    )
    write_exercises(
        f"{BASE}/l04-implicit-differentiation",
        [exset(
            "implicit", "Calculate the derivatives of the functions given implicitly.", implicit_items(),
            format="Type the derivatives as a vector in terms of the variables of the equation, for example `(y', y'')` written as `(expression, expression)`. "
            "An answer is accepted when it has the same values as the correct one on the curve (or surface). For a second derivative you may write the first derivative as `y'`.",
        )],
        "mvc_m01_u02.py",
    )
