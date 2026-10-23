"""More practice for Course 2, Module 1 (functions of several variables, partial derivatives, tangent planes, extrema).

Every key is computed with SymPy from the data of the problem and cross-checked numerically."""

from __future__ import annotations

import math

import sympy as sp
from toolkit import P, add_extra, check_partial, defined_real, eng, ex, exset_plain, simp, t, tex, u, v, x, y, z

SCRIPT = "more_mvc_a.py"
M1 = "mvc/m01-derivatives"


def vec_key(pts: list[tuple]) -> str:
    return ", ".join("(" + ", ".join(eng(sp.nsimplify(c)) for c in p) + ")" for p in pts)


def vec_tex(pts: list[tuple]) -> str:
    return ",\\ ".join("(" + ",\\,".join(tex(sp.nsimplify(c)) for c in p) + ")" for p in pts)


def kind_of(value: sp.Expr) -> str:
    return "number" if value.is_Rational else "expression"


# --- domains ------------------------------------------------------------------------------------------------------------
def domain_items() -> list[dict]:
    spec = [
        ("mp-dom-1", r"z=\sqrt{xy}", "sqrt(x*y)", "x*y>=0",
         "The root needs $xy\\ge0$: $x$ and $y$ have the same sign, or one of them is $0$. The domain is the first and third quadrants with both axes.",
         "A square root needs a non-negative argument."),
        ("mp-dom-2", r"z=\ln\left(4-x^2-y^2\right)", "ln(4-x^2-y^2)", "x^2+y^2<4",
         "The logarithm needs a positive argument: $4-x^2-y^2>0$, that is $x^2+y^2<4$. The domain is the open disc of radius $2$; the circle is excluded.",
         "A logarithm needs a positive argument."),
        ("mp-dom-3", r"z=\dfrac{1}{\sqrt{x-y^2}}", "1/sqrt(x-y^2)", "x>y^2",
         "The root needs $x-y^2\\ge0$ and it is in the denominator, so $x-y^2\\ne0$: together $x>y^2$. The domain is the region to the right of the parabola $x=y^2$, without the parabola.",
         "Two conditions: the root is defined, and the denominator is not zero."),
        ("mp-dom-4", r"z=\sqrt{y-x^2}+\ln x", "sqrt(y-x^2)+ln(x)", "y>=x^2 and x>0",
         "The root needs $y\\ge x^2$ and the logarithm needs $x>0$, and both must hold. The domain is the part of the region above the parabola $y=x^2$ with $x>0$.",
         "Both terms must be defined at the same time."),
    ]
    items = []
    for id_, latex, fn, cond, sol, hint in spec:
        f = P(fn)
        py_cond = cond.replace("^", "**")
        for px in range(-6, 7):
            for py in range(-6, 7):
                pt = (px / 2, py / 2)
                holds = eval(py_cond, {"x": pt[0], "y": pt[1]})  # noqa: S307 - our own string
                assert holds == defined_real(f, {x: pt[0], y: pt[1]}), (fn, pt)
        items.append(ex(id_, f"${latex}$", "region", cond, coordinates=["x", "y"], hints=[hint], solution=sol))
    return items


# --- limits ----------------------------------------------------------------------------------------------------------------
def limit_items() -> list[dict]:
    items = []

    def approach(fn: str) -> list[float]:
        f = sp.lambdify((x, y), P(fn), "math")
        out = []
        for k in range(12):
            r = 1e-4
            out.append(f(r * math.cos(k), r * math.sin(k)))
        return out

    vals = approach("x^3/(x^2+y^2)")
    assert max(abs(w) for w in vals) < 2e-4
    items.append(ex(
        "mp-lim-1", r"$\displaystyle\lim_{(x,y)\to(0,0)}\frac{x^3}{x^2+y^2}$", "number", "0",
        hints=[r"Use $x^2\le x^2+y^2$ to bound the fraction by $|x|$ (or use polar coordinates)."],
        solution=r"$\left|\dfrac{x^3}{x^2+y^2}\right|=|x|\cdot\dfrac{x^2}{x^2+y^2}\le|x|\to0$, so the limit is $0$ (the squeeze theorem). In polar form it is $r\cos^3\theta\to0$.",
    ))
    vals = approach("sin(x^2+y^2)/(x^2+y^2)")
    assert max(abs(w - 1) for w in vals) < 1e-6
    items.append(ex(
        "mp-lim-2", r"$\displaystyle\lim_{(x,y)\to(0,0)}\frac{\sin\left(x^2+y^2\right)}{x^2+y^2}$", "number", "1",
        hints=[r"Put $w=x^2+y^2$. When $(x,y)\to(0,0)$, $w\to0^+$."],
        solution=r"With $w=x^2+y^2\to0$ the expression is $\dfrac{\sin w}{w}\to1$.",
    ))
    f = P("(x^2-y^2)/(x^2+y^2)")
    assert f.subs({x: sp.Rational(1, 1000), y: 0}) == 1 and f.subs({x: 0, y: sp.Rational(1, 1000)}) == -1
    items.append(ex(
        "mp-lim-3", r"$\displaystyle\lim_{(x,y)\to(0,0)}\frac{x^2-y^2}{x^2+y^2}$", "number", "@dne",
        hints=[r"Approach the origin along the $x$-axis and along the $y$-axis."],
        solution=r"Along the $x$-axis ($y=0$) the value is $\dfrac{x^2}{x^2}=1$; along the $y$-axis ($x=0$) it is $-1$. The two limits differ, so the limit **does not exist**.",
        note="Answer with `does not exist` when the limit does not exist.",
    ))
    return items


# --- chain rule ------------------------------------------------------------------------------------------------------------
def chain_items() -> list[dict]:
    items = []

    def numeric_check(composite: sp.Expr, var: sp.Symbol, at: dict) -> None:
        check_partial(composite, var, sp.diff(composite, var), [{k: float(val) for k, val in at.items()}])

    def one_param(i: str, name: str, fl: str, fn: str, sub_tex: str, subs: dict, t0: sp.Expr) -> None:
        f = P(fn)
        comp = f.subs(subs, simultaneous=True)
        numeric_check(comp, t, {t: t0})
        val = simp(sp.diff(comp, t).subs(t, t0))
        syms = [s for s in (x, y, z) if s in subs]
        parts = ", ".join(rf"{name}_{s.name}={tex(simp(sp.diff(f, s)))}" for s in syms)
        derivs = ", ".join(rf"{s.name}'={tex(sp.diff(subs[s], t))}" for s in syms)
        items.append(ex(
            f"mp-cha-{i}", rf"Let ${name}={fl}$ with {sub_tex}. Find $\dfrac{{d{name}}}{{dt}}$ at $t={tex(t0)}$.", kind_of(val), eng(val),
            hints=[rf"Use $\dfrac{{d{name}}}{{dt}}=" + " + ".join(rf"{name}_{s.name}\,{s.name}'" for s in syms) + "$."],
            solution=rf"The chain rule gives $\dfrac{{d{name}}}{{dt}}=" + " + ".join(rf"{name}_{s.name}\,{s.name}'" for s in syms)
            + rf"$ with ${parts}$ and ${derivs}$. At $t={tex(t0)}$ the value is ${tex(val)}$ (it can be checked by substituting first and differentiating in $t$).",
        ))

    one_param("1", "z", "x^2y", "x^2*y", r"$x=t^2$ and $y=t^3$", {x: t**2, y: t**3}, sp.Integer(1))
    one_param("2", "z", "e^{xy}", "exp(x*y)", r"$x=\cos t$ and $y=\sin t$", {x: sp.cos(t), y: sp.sin(t)}, sp.Integer(0))
    one_param("3", "z", r"\dfrac xy", "x/y", r"$x=e^t$ and $y=1+t^2$", {x: sp.exp(t), y: 1 + t**2}, sp.Integer(2))
    one_param("4", "w", "xyz", "x*y*z", r"$x=t$, $y=t^2$ and $z=t^3$", {x: t, y: t**2, z: t**3}, sp.Integer(1))

    def two_param(i: str, fl: str, fn: str, sub_tex: str, subs: dict, var: sp.Symbol, at: dict) -> None:
        f = P(fn)
        comp = f.subs(subs, simultaneous=True)
        numeric_check(comp, var, at)
        val = simp(sp.diff(comp, var).subs(at))
        where = ",\\ ".join(rf"{k.name}={tex(w)}" for k, w in at.items())
        items.append(ex(
            f"mp-cha-{i}", rf"Let $z={fl}$ with {sub_tex}. Find $\dfrac{{\partial z}}{{\partial {var.name}}}$ at ${where}$.", kind_of(val), eng(val),
            hints=[rf"$\dfrac{{\partial z}}{{\partial {var.name}}}=z_x\,\dfrac{{\partial x}}{{\partial {var.name}}}+z_y\,\dfrac{{\partial y}}{{\partial {var.name}}}$."],
            solution=rf"By the chain rule, $\dfrac{{\partial z}}{{\partial {var.name}}}=z_x\,x_{var.name}+z_y\,y_{var.name}$ with $z_x={tex(simp(sp.diff(f, x)))}$, $z_y={tex(simp(sp.diff(f, y)))}$, "
            rf"$x_{var.name}={tex(sp.diff(subs[x], var))}$ and $y_{var.name}={tex(sp.diff(subs[y], var))}$. At the point the result is ${tex(val)}$.",
        ))

    two_param("5", "x^2+y^2", "x^2+y^2", r"$x=u+v$ and $y=u-v$", {x: u + v, y: u - v}, u, {u: sp.Integer(1), v: sp.Integer(2)})
    two_param("6", "xy", "x*y", r"$x=u^2-v$ and $y=u+v^2$", {x: u**2 - v, y: u + v**2}, v, {u: sp.Integer(2), v: sp.Integer(1)})
    two_param("7", "e^{x-y}", "exp(x-y)", r"$x=uv$ and $y=u^2$", {x: u * v, y: u**2}, v, {u: sp.Integer(1), v: sp.Integer(1)})
    two_param("8", r"\ln\left(x^2+y^2\right)", "ln(x^2+y^2)", r"$x=u\cos v$ and $y=u\sin v$", {x: u * sp.cos(v), y: u * sp.sin(v)}, v,
              {u: sp.Integer(2), v: sp.Integer(1)})
    return items


# --- higher-order derivatives -----------------------------------------------------------------------------------------
def higher_items() -> list[dict]:
    items = []

    def second(i: str, fl: str, fn: str, order: str, at: tuple) -> None:
        f = P(fn)
        vars_ = [x if c == "x" else y for c in order]
        d = f
        for s in vars_:
            d = sp.diff(d, s)
        val = simp(d.subs({x: at[0], y: at[1]}))
        sub = {k: float(w) for k, w in zip((x, y), at, strict=True)}
        check_partial(sp.diff(f, *vars_[:-1]) if len(vars_) > 1 else f, vars_[-1], sp.diff(f, *vars_), [sub])
        name = "f_{" + "".join(order) + "}"
        items.append(ex(
            f"mp-hi-{i}", rf"Let $f(x,y)={fl}$. Find ${name}$ at $({tex(at[0])},{tex(at[1])})$.", kind_of(val), eng(val),
            hints=["Differentiate in the order of the subscripts, from left to right."],
            solution=rf"${name}={tex(simp(d))}$, which at the point equals ${tex(val)}$.",
        ))

    second("1", r"x^3y^2-2xy", "x^3*y^2-2*x*y", "xx", (1, 2))
    second("2", r"x^3y^2-2xy", "x^3*y^2-2*x*y", "xy", (1, 2))
    second("3", r"e^{xy}", "exp(x*y)", "yy", (1, 0))
    second("4", r"\ln\left(x^2+y^2\right)", "ln(x^2+y^2)", "xy", (1, 1))
    second("5", r"\dfrac{x}{y}", "x/y", "yx", (2, 1))
    second("6", r"x^2y^3", "x^2*y^3", "xyy", (1, 1))
    items.append(ex(
        "mp-hi-7", r"Which of these functions satisfies Laplace's equation $f_{xx}+f_{yy}=0$ everywhere?", "multiple_choice", "2",
        choices=[{"text": r"$x^2+y^2$", "value": "1"}, {"text": r"$x^2-y^2$", "value": "2"}, {"text": r"$x^2y$", "value": "3"}],
        correctIndex=1, hints=[r"Compute $f_{xx}+f_{yy}$ for each one."],
        solution=r"For $x^2-y^2$: $f_{xx}=2$ and $f_{yy}=-2$, so the sum is $0$. For $x^2+y^2$ it is $4$, and for $x^2y$ it is $2y$.",
    ))
    assert sp.diff(x**2 - y**2, x, 2) + sp.diff(x**2 - y**2, y, 2) == 0
    return items


# --- implicit differentiation ---------------------------------------------------------------------------------------------
def implicit_items() -> list[dict]:
    items = []

    def curve(i: str, fl: str, fn: str, at: tuple, at_tex: str) -> None:
        F = P(fn)
        assert simp(F.subs({x: at[0], y: at[1]})) == 0, fn
        dydx = simp(-sp.diff(F, x) / sp.diff(F, y))
        val = simp(dydx.subs({x: at[0], y: at[1]}))
        # independent check: solve numerically for y(x) near the point and differentiate
        h = 1e-6
        f_ = sp.lambdify((x, y), F, "math")

        def y_of(xv: float) -> float:
            yv = float(at[1])
            for _ in range(60):
                fy = float(sp.diff(F, y).subs({x: xv, y: yv}))
                yv -= f_(xv, yv) / fy
            return yv

        num = (y_of(float(at[0]) + h) - y_of(float(at[0]) - h)) / (2 * h)
        assert abs(num - float(val)) < 1e-5, (fn, num, val)
        items.append(ex(
            f"mp-imp-{i}a", rf"The equation ${fl}=0$ defines $y$ as a function of $x$ near the point {at_tex}. Find $\dfrac{{dy}}{{dx}}$ as an expression in $x$ and $y$.",
            "expression", eng(dydx), variables=["x", "y"],
            hints=[r"For $F(x,y)=0$: $\dfrac{dy}{dx}=-\dfrac{F_x}{F_y}$."],
            solution=rf"With $F={tex(F)}$ we get $F_x={tex(sp.diff(F, x))}$ and $F_y={tex(sp.diff(F, y))}$, so $\dfrac{{dy}}{{dx}}=-\dfrac{{F_x}}{{F_y}}={tex(dydx)}$.",
        ))
        items.append(ex(
            f"mp-imp-{i}b", rf"For the same equation ${fl}=0$, find the slope $\dfrac{{dy}}{{dx}}$ at the point {at_tex}.", kind_of(val), eng(val),
            hints=[r"Substitute the coordinates of the point in $-\dfrac{F_x}{F_y}$."],
            solution=rf"$\dfrac{{dy}}{{dx}}=-\dfrac{{F_x}}{{F_y}}={tex(dydx)}$, which at the point equals ${tex(val)}$.",
        ))

    curve("1", "x^2+y^2-25", "x^2+y^2-25", (3, 4), "$(3,4)$")
    curve("2", "x^3+y^3-6xy", "x^3+y^3-6*x*y", (3, 3), "$(3,3)$")
    curve("3", "x^2y+xy^2-6", "x^2*y+x*y^2-6", (1, 2), "$(1,2)$")
    curve("4", r"\sin x+\cos y-1", "sin(x)+cos(y)-1", (sp.pi / 2, sp.pi / 2), r"$\left(\dfrac\pi2,\dfrac\pi2\right)$")
    curve("5", r"xe^{y}+ye^{x}", "x*exp(y)+y*exp(x)", (0, 0), "$(0,0)$")
    return items


# --- tangent planes ----------------------------------------------------------------------------------------------------------
def tangent_plane_items() -> list[dict]:
    items = []

    def plane(i: str, fl: str, fn: str, at: tuple) -> None:
        f = P(fn)
        z0 = simp(f.subs({x: at[0], y: at[1]}))
        fx, fy = (simp(sp.diff(f, s).subs({x: at[0], y: at[1]})) for s in (x, y))
        poly = sp.expand((fx * (x - at[0]) + fy * (y - at[1]) - (z - z0)) * sp.ilcm(*[sp.fraction(c)[1] for c in (fx, fy, z0)]))
        items.append(ex(
            f"mp-tp-{i}", rf"Find the tangent plane to the surface $z={fl}$ at the point $({at[0]},{at[1]},{tex(z0)})$.", "equation", f"{eng(poly)}=0",
            coordinates=["x", "y", "z"],
            hints=[r"$z-z_0=f_x(x_0,y_0)(x-x_0)+f_y(x_0,y_0)(y-y_0)$."],
            solution=rf"$f_x={tex(simp(sp.diff(f, x)))}$ and $f_y={tex(simp(sp.diff(f, y)))}$ give $f_x={tex(fx)}$, $f_y={tex(fy)}$ at the point. "
            rf"So $z-{tex(z0)}={tex(fx)}(x-{at[0]})+{tex(fy)}(y-{at[1]})$, that is ${tex(poly)}=0$ (any non-zero multiple describes the same plane).",
        ))

    plane("1", "x^2+y^2", "x^2+y^2", (1, 2))
    plane("2", "xe^{y}", "x*exp(y)", (2, 0))
    plane("3", r"\sqrt{x^2+y^2}", "sqrt(x^2+y^2)", (3, 4))
    return items


# --- local extrema -------------------------------------------------------------------------------------------------------------
def extrema_items() -> list[dict]:
    items = []
    names = {"min": "a local minimum", "max": "a local maximum", "saddle": "a saddle point", "none": "the second-derivative test is inconclusive"}

    def classify(f: sp.Expr, p: tuple) -> str:
        sub = {x: p[0], y: p[1]}
        fxx, fyy, fxy = (sp.diff(f, *vs).subs(sub) for vs in ((x, x), (y, y), (x, y)))
        d = fxx * fyy - fxy**2
        if d > 0:
            return "min" if fxx > 0 else "max"
        return "saddle" if d < 0 else "none"

    def one(i: str, fl: str, fn: str, pick: int) -> None:
        f = P(fn)
        sols = sp.solve([sp.diff(f, x), sp.diff(f, y)], [x, y], dict=True)
        pts = sorted([(simp(s[x]), simp(s[y])) for s in sols if s[x].is_real and s[y].is_real], key=lambda p: (float(p[0]), float(p[1])))
        items.append(ex(
            f"mp-ext-{i}a", rf"Find all the critical points of $f(x,y)={fl}$.", "points", vec_key(pts),
            hints=[r"Solve $f_x=0$ and $f_y=0$ together."],
            solution=rf"$f_x={tex(sp.diff(f, x))}$ and $f_y={tex(sp.diff(f, y))}$. The system $f_x=f_y=0$ has the solutions ${vec_tex(pts)}$.",
        ))
        p = pts[pick]
        kind = classify(f, p)
        order = ["min", "max", "saddle", "none"]
        sub = {x: p[0], y: p[1]}
        fxx, fyy, fxy = (simp(sp.diff(f, *vs).subs(sub)) for vs in ((x, x), (y, y), (x, y)))
        items.append(ex(
            f"mp-ext-{i}b", rf"Classify the critical point $({tex(p[0])},{tex(p[1])})$ of $f(x,y)={fl}$.", "multiple_choice", str(order.index(kind) + 1),
            choices=[{"text": names[k].capitalize() if k != "none" else "The test is inconclusive", "value": str(n + 1)} for n, k in enumerate(order)],
            correctIndex=order.index(kind),
            hints=[r"Compute $D=f_{xx}f_{yy}-f_{xy}^2$ at the point."],
            solution=rf"At the point $f_{{xx}}={tex(fxx)}$, $f_{{yy}}={tex(fyy)}$ and $f_{{xy}}={tex(fxy)}$, so $D={tex(simp(fxx * fyy - fxy**2))}$. "
            + {"min": "$D>0$ and $f_{xx}>0$: a local minimum.", "max": "$D>0$ and $f_{xx}<0$: a local maximum.",
               "saddle": "$D<0$: a saddle point.", "none": "$D=0$: the test is inconclusive."}[kind],
        ))

    one("1", "x^3-3x+y^2", "x^3-3*x+y^2", 1)
    one("2", "x^2+xy+y^2-3x", "x^2+x*y+y^2-3*x", 0)
    one("3", "2x^3+y^3-6x-3y", "2*x^3+y^3-6*x-3*y", 0)
    return items


# --- constrained extrema --------------------------------------------------------------------------------------------------------
def constrained_items() -> list[dict]:
    items = []
    lam = sp.Symbol("lam", real=True)

    def one(i: str, fl: str, fn: str, gl: str, gn: str) -> None:
        f, g = P(fn), P(gn)
        sols = sp.solve([sp.diff(f, x) - lam * sp.diff(g, x), sp.diff(f, y) - lam * sp.diff(g, y), g], [x, y, lam], dict=True)
        vals = [simp(f.subs({x: s[x], y: s[y]})) for s in sols if s[x].is_real and s[y].is_real]
        vmax, vmin = max(vals, key=float), min(vals, key=float)
        # independent check: the constraint is a circle; sample it
        r = math.sqrt(float(sp.solve(g.subs(y, 0), x)[-1] ** 2))
        fl_ = sp.lambdify((x, y), f, "math")
        samples = [fl_(r * math.cos(k * 2 * math.pi / 20000), r * math.sin(k * 2 * math.pi / 20000)) for k in range(20000)]
        assert abs(max(samples) - float(vmax)) < 1e-3 and abs(min(samples) - float(vmin)) < 1e-3, (fn, vmax, vmin, max(samples), min(samples))
        sol = rf"With the multiplier $\lambda$: $\nabla f=\lambda\nabla g$ and ${gl}=0$. Solving the system gives the candidate values ${', '.join(tex(w) for w in sorted(set(vals), key=float))}$."
        items.append(ex(f"mp-con-{i}a", rf"Find the maximum value of $f(x,y)={fl}$ on the curve ${gl}=0$.", kind_of(vmax), eng(vmax),
                        hints=[r"Solve $f_x=\lambda g_x$, $f_y=\lambda g_y$ and $g=0$, then compare the values of $f$."], solution=sol + rf" The largest is ${tex(vmax)}$."))
        items.append(ex(f"mp-con-{i}b", rf"Find the minimum value of $f(x,y)={fl}$ on the curve ${gl}=0$.", kind_of(vmin), eng(vmin),
                        hints=[r"Solve $f_x=\lambda g_x$, $f_y=\lambda g_y$ and $g=0$, then compare the values of $f$."], solution=sol + rf" The smallest is ${tex(vmin)}$."))

    one("1", "xy", "x*y", "x^2+y^2-2", "x^2+y^2-2")
    one("2", "x+2y", "x+2*y", "x^2+y^2-5", "x^2+y^2-5")
    one("3", "x^2+2y^2", "x^2+2*y^2", "x^2+y^2-1", "x^2+y^2-1")
    return items


def register() -> None:
    add_extra(f"{M1}/u01-functions-of-several-variables/l01-domains",
              exset_plain("more-domains", "More practice: domains.", domain_items(),
                          format="Type the conditions, for example `x > 1 and y <= 2`, with `<=` and `>=`."), SCRIPT)
    add_extra(f"{M1}/u01-functions-of-several-variables/l02-limits-and-continuity",
              exset_plain("more-limits", "More practice: limits.", limit_items(), format="Type a number, or `does not exist`."), SCRIPT)
    add_extra(f"{M1}/u02-partial-differentiation/l02-chain-rule",
              exset_plain("more-chain", "More practice: the chain rule.", chain_items(), format="Type an exact value such as `7/4` or `e^3/10`."), SCRIPT)
    add_extra(f"{M1}/u02-partial-differentiation/l03-higher-order-derivatives",
              exset_plain("more-higher", "More practice: derivatives of higher order.", higher_items(), format="Type an exact value such as `5/3`."), SCRIPT)
    add_extra(f"{M1}/u02-partial-differentiation/l04-implicit-differentiation",
              exset_plain("more-implicit", "More practice: implicit differentiation.", implicit_items(),
                          format="Type an expression in `x` and `y` such as `x/(y+1)`, or a value such as `-2/3`."), SCRIPT)
    add_extra(f"{M1}/u03-tangent-planes/l01-tangent-plane-and-normal-line",
              exset_plain("more-planes", "More practice: tangent planes to a graph.", tangent_plane_items(),
                          format="Write the plane as an equation; any non-zero multiple is accepted."), SCRIPT)
    add_extra(f"{M1}/u04-optimization/l01-local-extrema",
              exset_plain("more-extrema", "More practice: critical points and their type.", extrema_items(),
                          format="For a list of points type `(a, b), (c, d)`."), SCRIPT)
    add_extra(f"{M1}/u04-optimization/l02-constrained-extrema",
              exset_plain("more-constrained", "More practice: Lagrange multipliers.", constrained_items(),
                          format="Type an exact value such as `sqrt(3)` or `7/2`."), SCRIPT)
