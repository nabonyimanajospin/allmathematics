"""Exercises of Course 2, Module 5: partial differential equations."""

from __future__ import annotations

import sympy as sp
from toolkit import eng, ex, exset, tex, write_exercises

BASE = "mvc/m05-pde"
U1 = f"{BASE}/u01-introduction-and-first-order"
U2 = f"{BASE}/u02-separation-of-variables"
U3 = f"{BASE}/u03-fourier-series"
R = sp.Rational
PI = sp.pi
x, y, t = sp.symbols("x y t", real=True)
FMT = "Type an expression in the variables of the question, such as `exp(-3*t)*sin(x)` or `5/(7*pi)`."


def zero(e) -> bool:
    return sp.simplify(e) == 0


def solution_item(id_: str, statement: str, u, vars_: list[str], hints: list[str], solution: str, check) -> dict:
    """An exercise whose answer is a function; `check(u)` must be zero (it proves the answer before it ships)."""
    assert zero(check(u)), f"{id_}: the answer does not satisfy its equation"
    return ex(id_, statement, "expression", eng(u), variables=vars_, hints=hints, solution=solution)


YES_NO = [{"text": "Yes", "value": "1"}, {"text": "No", "value": "2"}]
TYPES = [{"text": "Elliptic", "value": "1"}, {"text": "Parabolic", "value": "2"}, {"text": "Hyperbolic", "value": "3"}]


def l01() -> list[dict]:
    items = []
    for n, (eq, order) in enumerate(((r"u_t=u_{xxx}+u_x", 3), (r"u_{tt}=4u_{xx}", 2), (r"u_x+u_y=0", 1), (r"u_{xy}+u_{yyy}=x", 3)), 1):
        items.append(ex(f"pv-{n:02d}", rf"The order of ${eq}$.", "number", str(order), hints=["Find the highest derivative."], solution=rf"The highest derivative has order ${order}$."))
    items.append(ex("pv-05", r"Is the equation $u_{xx}+x\,u_{yy}=0$ linear?", "multiple_choice", "1", choices=YES_NO, correctIndex=0,
                    hints=["The coefficients may depend on the variables."], solution=r"$u$ and its derivatives appear to the first power and are not multiplied together: it is linear."))
    items.append(ex("pv-06", r"Is the equation $u_t+u\,u_x=0$ linear?", "multiple_choice", "2", choices=YES_NO, correctIndex=1,
                    hints=["Look at the term $u\\,u_x$."], solution=r"$u\,u_x$ is a product of the unknown with its derivative: the equation is not linear."))
    for n, (A, B, C, kind, eq) in enumerate(((1, 3, 2, 3, r"u_{xx}+3u_{xy}+2u_{yy}=0"), (1, 0, 1, 1, r"u_{xx}+u_{yy}=0"), (4, 4, 1, 2, r"4u_{xx}+4u_{xy}+u_{yy}=0")), 7):
        d = B * B - 4 * A * C
        items.append(ex(f"pv-{n:02d}", rf"The value of $B^2-4AC$ for ${eq}$.", "number", str(d), hints=[f"$A={A}$, $B={B}$, $C={C}$."],
                        solution=rf"$B^2-4AC={B*B}-{4*A*C}={d}$: the equation is {['', 'elliptic', 'parabolic', 'hyperbolic'][kind]}."))
    items.append(ex("pv-10", r"What type is the wave equation $u_{tt}=9u_{xx}$?", "multiple_choice", "3", choices=TYPES, correctIndex=2,
                    hints=["Write it as $u_{tt}-9u_{xx}=0$: $A=-9$ (for $x$), $C=1$."], solution=r"$B^2-4AC=0-4(-9)(1)=36>0$: hyperbolic."))
    items.append(ex("pv-11", r"What type is the heat equation $u_t=3u_{xx}$?", "multiple_choice", "2", choices=TYPES, correctIndex=1,
                    hints=["There is no term $u_{tt}$ nor $u_{xt}$."], solution=r"$A=3$ and $B=C=0$, so $B^2-4AC=0$: parabolic."))
    items.append(ex("pv-12", r"The number $k$ for which $u=e^{kt}\sin2x$ is a solution of $u_t=u_{xx}$.", "number", "-4", hints=["$u_t=ku$ and $u_{xx}=-4u$."],
                    solution=r"$u_t=k\,u$ and $u_{xx}=-4u$, so $k=-4$."))
    items.append(ex("pv-13", r"The number $k$ for which $u=e^{kt}\sin3x$ is a solution of $u_t=2u_{xx}$.", "number", "-18", hints=["$u_{xx}=-9u$."],
                    solution=r"$u_t=k\,u$ and $2u_{xx}=-18u$, so $k=-18$."))
    items.append(ex("pv-14", r"The positive number $k$ for which $u=\sin x\cos kt$ is a solution of $u_{tt}=4u_{xx}$.", "number", "2", hints=["$u_{tt}=-k^2u$ and $u_{xx}=-u$."],
                    solution=r"$-k^2u=-4u$, so $k^2=4$ and $k=2$."))
    items.append(ex("pv-15", r"The number $a$ for which $u=x^3+a\,xy^2$ is a solution of $u_{xx}+u_{yy}=0$.", "number", "-3", hints=["$u_{xx}=6x$."],
                    solution=r"$u_{xx}=6x$ and $u_{yy}=2ax$; $6x+2ax=0$ gives $a=-3$."))
    items.append(ex("pv-16", r"The general solution of $u_{xy}=0$ is $u=f(x)+h(y)$. If $u(x,0)=x^2$ and $u(0,y)=y^2$, find $u(2,3)$.", "number", "13",
                    hints=["Find $u(x,y)$ first."], solution=r"$f(x)+h(0)=x^2$ and $f(0)+h(y)=y^2$ give $u=x^2+y^2$ (the constants add up to $u(0,0)=0$), so $u(2,3)=4+9=13$."))
    return items


def l02() -> list[dict]:
    items = []
    cases = (
        (3, 2, x**2), (1, 2, x**3), (2, 1, sp.sin(x)), (1, 3, sp.exp(x)),
    )
    for n, (a, b, g) in enumerate(cases, 1):
        s = sp.Symbol("s")
        # u = f(b x - a y), f(b x) = g(x)  ->  f(s) = g(s / b)
        u = sp.simplify(g.subs(x, (b * x - a * y) / b))
        check = lambda w, a=a, b=b: a * sp.diff(w, x) + b * sp.diff(w, y)
        items.append(solution_item(f"ch-{n:02d}", rf"The solution of ${a}u_x+{b}u_y=0$ with $u(x,0)={tex(g)}$ (an expression in $x$ and $y$).", u, ["x", "y"],
                                   [rf"$u=f({b}x-{a}y)$; the condition at $y=0$ gives $f({b}x)={tex(g)}$."],
                                   rf"$u=f({b}x-{a}y)$ and $f({b}x)={tex(g)}$, so $f(s)={tex(g.subs(x, s/b))}$ and $u={tex(u)}$.", check))
    for n, (c, g) in enumerate(((3, 1 / (1 + x**2)), (2, sp.cos(x))), 5):
        u = g.subs(x, x - c * t)
        items.append(solution_item(f"ch-{n:02d}", rf"The solution of $u_t+{c}u_x=0$ with $u(x,0)={tex(g)}$ (an expression in $x$ and $t$).", u, ["x", "t"],
                                   [rf"The profile moves to the right at speed ${c}$."], rf"$u=f(x-{c}t)$ with $f={tex(g.subs(x, sp.Symbol('s')))}$, so $u={tex(u)}$.",
                                   lambda w, c=c: sp.diff(w, t) + c * sp.diff(w, x)))
    u = (y - x**2 / 2) ** 2
    items.append(solution_item("ch-07", r"The solution of $u_x+x\,u_y=0$ with $u(0,y)=y^2$.", u, ["x", "y"], ["The characteristics are $y-\\dfrac{x^2}{2}=C$."],
                               r"$u=f\left(y-\dfrac{x^2}2\right)$ and $f(y)=y^2$, so $u=\left(y-\dfrac{x^2}{2}\right)^2$.", lambda w: sp.diff(w, x) + x * sp.diff(w, y)))
    u = sp.sin(y - x**2)
    items.append(solution_item("ch-08", r"The solution of $u_x+2x\,u_y=0$ with $u(0,y)=\sin y$.", u, ["x", "y"], ["Solve $\\dfrac{dy}{dx}=2x$."],
                               r"The characteristics are $y-x^2=C$, so $u=f(y-x^2)$ with $f=\sin$: $u=\sin\left(y-x^2\right)$.", lambda w: sp.diff(w, x) + 2 * x * sp.diff(w, y)))
    u = y**3 * sp.exp(-3 * x)
    items.append(solution_item("ch-09", r"The solution of $u_x+y\,u_y=0$ with $u(0,y)=y^3$.", u, ["x", "y"], ["Solve $\\dfrac{dy}{dx}=y$: the invariant is $ye^{-x}$."],
                               r"The characteristics are $y=Ce^{x}$, that is $ye^{-x}=C$. So $u=f\left(ye^{-x}\right)$, and $u(0,y)=y^3$ gives $f(s)=s^3$: $u=\left(ye^{-x}\right)^3=y^3e^{-3x}$.", lambda w: sp.diff(w, x) + y * sp.diff(w, y)))
    u = sp.exp(y) * sp.cos(x - y)
    items.append(solution_item("ch-10", r"The solution of $u_x+u_y=u$ with $u(x,0)=\cos x$.", u, ["x", "y"], ["$u=e^{x}f(x-y)$."],
                               r"$u=e^{x}f(x-y)$ and $e^{x}f(x)=\cos x$ give $f(s)=e^{-s}\cos s$, so $u=e^{y}\cos(x-y)$.", lambda w: sp.diff(w, x) + sp.diff(w, y) - w))
    u = sp.exp(2 * y) * sp.sin(x - y)
    items.append(solution_item("ch-11", r"The solution of $u_x+u_y=2u$ with $u(x,0)=\sin x$.", u, ["x", "y"], ["$u=e^{2x}f(x-y)$."],
                               r"$u=e^{2x}f(x-y)$ and $e^{2x}f(x)=\sin x$ give $f(s)=e^{-2s}\sin s$, so $u=e^{2y}\sin(x-y)$.", lambda w: sp.diff(w, x) + sp.diff(w, y) - 2 * w))
    return items


def heat(L, k, modes):
    u = sum(b * sp.exp(-k * (n * PI / L) ** 2 * t) * sp.sin(n * PI * x / L) for n, b in modes)
    return u, sum(b * sp.sin(n * PI * x / L) for n, b in modes)


def l03() -> list[dict]:
    items = []
    cases = ((PI, 2, [(1, 3)]), (PI, 5, [(2, 1), (4, -2)]), (1, 2, [(1, 5), (3, 1)]), (2, 1, [(1, 4)]), (PI, 3, [(1, 1), (3, -4)]))
    for n, (L, k, modes) in enumerate(cases, 1):
        u, f = heat(L, k, modes)
        assert zero(sp.diff(u, t) - k * sp.diff(u, x, 2)) and zero(u.subs(x, 0)) and zero(u.subs(x, L))
        items.append(ex(f"he-{n:02d}", rf"A rod of length ${tex(L)}$ with $k={k}$ has its ends at $0$ and the initial temperature $f(x)={tex(f)}$. Find $u(x,t)$.", "expression", eng(u),
                        variables=["x", "t"], hints=[rf"The mode $n$ is multiplied by $e^{{-k(n\pi/L)^2t}}$."],
                        solution=rf"Each mode $\sin\dfrac{{n\pi x}}{{{tex(L)}}}$ is multiplied by $e^{{-{k}(n\pi/{tex(L)})^2t}}$, so $u={tex(u)}$."))
    items.append(ex("he-06", r"On a rod of length $\pi$ with $k=3$, the number $\mu$ such that the mode $n=2$ decays like $e^{-\mu t}$.", "number", "12", hints=["$\\mu=k\\left(\\dfrac{n\\pi}{L}\\right)^2$."], solution=r"$\mu=3\cdot2^2=12$."))
    items.append(ex("he-07", r"On a rod of length $1$ with $k=1$, the number $\mu$ such that the mode $n=1$ decays like $e^{-\mu t}$.", "expression", "pi^2", hints=["$L=1$."], solution=r"$\mu=\pi^2$."))
    items.append(ex("he-08", r"A rod of length $\pi$ with $k=1$ has the initial temperature $\sin x+\sin2x$. Which of the two terms of $u(x,t)$ is smaller at $t=1$: answer the exponent $\mu$ of the smaller one.", "number", "4",
                    hints=["The higher mode decays faster: compute its exponent."], solution=r"The modes decay like $e^{-t}$ and $e^{-4t}$; the second one is smaller, with exponent $4$."))
    return items


def wave(c, L, fmodes, gmodes):
    u = 0
    for n, a in fmodes:
        u += a * sp.cos(n * PI * c * t / L) * sp.sin(n * PI * x / L)
    for n, B in gmodes:
        u += B * L / (n * PI * c) * sp.sin(n * PI * c * t / L) * sp.sin(n * PI * x / L)
    return sp.simplify(u)


def l04() -> list[dict]:
    items = []
    cases = (
        (2, PI, [(1, 3)], [], r"a string with $c=2$, $L=\pi$, starting at rest with $f=3\sin x$"),
        (3, PI, [(2, 1)], [], r"a string with $c=3$, $L=\pi$, starting at rest with $f=\sin2x$"),
        (1, 1, [(1, 2)], [], r"a string with $c=1$, $L=1$, starting at rest with $f=2\sin\pi x$"),
        (1, PI, [], [(2, 1)], r"a string with $c=1$, $L=\pi$, starting flat with the velocity $g=\sin2x$"),
        (2, PI, [], [(3, 1)], r"a string with $c=2$, $L=\pi$, starting flat with the velocity $g=\sin3x$"),
    )
    for n, (c, L, fm, gm, text) in enumerate(cases, 1):
        u = wave(c, L, fm, gm)
        assert zero(sp.diff(u, t, 2) - c**2 * sp.diff(u, x, 2)) and zero(u.subs(x, 0)) and zero(sp.simplify(u.subs(x, L)))
        items.append(ex(f"wa-{n:02d}", rf"The displacement $u(x,t)$ of {text}, with fixed ends.", "expression", eng(u), variables=["x", "t"],
                        hints=[r"The angular frequency of the mode $n$ is $\omega_n=\dfrac{n\pi c}{L}$."], solution=rf"With $\omega_n=\dfrac{{n\pi c}}{{L}}$ the solution is $u={tex(u)}$."))
    dal = (
        (x**2, 0, r"u(x,0)=x^2,\ u_t(x,0)=0", x**2 + sp.Symbol("c") ** 2 * t**2, r"$\dfrac{(x-ct)^2+(x+ct)^2}2=x^2+c^2t^2$."),
        (0, sp.cos(x), r"u(x,0)=0,\ u_t(x,0)=\cos x\ (c=1)", sp.cos(x) * sp.sin(t), r"$\dfrac12\int_{x-t}^{x+t}\cos s\,ds=\dfrac12\left[\sin(x+t)-\sin(x-t)\right]=\cos x\sin t$."),
        (sp.sin(x), 0, r"u(x,0)=\sin x,\ u_t(x,0)=0\ (c=2)", sp.sin(x) * sp.cos(2 * t), r"$\dfrac{\sin(x-2t)+\sin(x+2t)}2=\sin x\cos2t$."),
        (0, 2 * x, r"u(x,0)=0,\ u_t(x,0)=2x\ (c=1)", 2 * x * t, r"$\dfrac12\int_{x-t}^{x+t}2s\,ds=(x+t)^2/2-(x-t)^2/2=2xt$."),
    )
    for n, (f, g, cond, u, sol) in enumerate(dal, 6):
        c = sp.Symbol("c")
        cc = 2 if "c=2" in cond else 1
        if n == 6:
            items.append(ex(f"wa-{n:02d}", rf"Solve $u_{{tt}}=c^2u_{{xx}}$ with ${cond}$ (an expression in $x$, $t$ and $c$).", "expression", "x^2+c^2*t^2", variables=["x", "t", "c"],
                            hints=["Use d'Alembert's formula."], solution=sol))
        else:
            assert zero(sp.diff(u, t, 2) - cc**2 * sp.diff(u, x, 2))
            items.append(ex(f"wa-{n:02d}", rf"Solve $u_{{tt}}=c^2u_{{xx}}$ with ${cond}$.", "expression", eng(u), variables=["x", "t"], hints=["Use d'Alembert's formula."], solution=sol))
    items.append(ex("wa-10", r"A string has $c=6$ and $L=3$. The angular frequency $\omega_2$ of its second mode.", "expression", "4*pi", hints=["$\\omega_n=\\dfrac{n\\pi c}{L}$."], solution=r"$\omega_2=\dfrac{2\pi\cdot6}3=4\pi$."))
    return items


def l05() -> list[dict]:
    items = []
    cases = ((PI, 1, [(1, 1)]), (PI, 1, [(2, 3)]), (1, 2, [(1, 2)]), (PI, 2, [(1, 1)]), (2, 1, [(1, 4)]))
    for n, (a, b, modes) in enumerate(cases, 1):
        u = sum(c * sp.sin(m * PI * x / a) * sp.sinh(m * PI * y / a) / sp.sinh(m * PI * b / a) for m, c in modes)
        f = sum(c * sp.sin(m * PI * x / a) for m, c in modes)
        assert zero(sp.diff(u, x, 2) + sp.diff(u, y, 2)) and zero(u.subs(x, 0)) and zero(sp.simplify(u.subs(x, a))) and zero(u.subs(y, 0)) and zero(sp.simplify(u.subs(y, b) - f))
        items.append(ex(f"la-{n:02d}", rf"On the rectangle $0\le x\le{tex(a)}$, $0\le y\le{b}$, solve $u_{{xx}}+u_{{yy}}=0$ with $u=0$ on three sides and $u(x,{b})={tex(f)}$.", "expression", eng(u), variables=["x", "y"],
                        hints=[r"The modes are $\sin\dfrac{n\pi x}{a}\sinh\dfrac{n\pi y}{a}$; divide by the value at the top."], solution=rf"$u={tex(u)}$."))
    items.append(ex("la-06", r"The number $k$ for which $u=x^3+k\,xy^2$ is a solution of $u_{xx}+u_{yy}=0$.", "number", "-3", hints=["$u_{xx}=6x$."], solution=r"$6x+2kx=0$ gives $k=-3$."))
    items.append(ex("la-07", r"The number $a$ for which $u=x^2+a\,y^2$ is a solution of $u_{xx}+u_{yy}=0$.", "number", "-1", hints=["$u_{xx}=2$ and $u_{yy}=2a$."], solution=r"$2+2a=0$, so $a=-1$."))
    items.append(ex("la-08", r"The positive number $a$ for which $u=e^{x}\cos ay$ is a solution of $u_{xx}+u_{yy}=0$.", "number", "1", hints=["$u_{xx}=u$ and $u_{yy}=-a^2u$."], solution=r"$1-a^2=0$, so $a=1$."))
    return items


def fourier(f, L, n):
    if isinstance(f, sp.Abs):  # even: integrate on (0, L) and double
        a = sp.simplify(2 * sp.integrate(x * sp.cos(n * PI * x / L), (x, 0, L)) / L)
        return a, sp.Integer(0)
    a = sp.simplify(sp.integrate(f * sp.cos(n * PI * x / L), (x, -L, L)) / L)
    b = sp.simplify(sp.integrate(f * sp.sin(n * PI * x / L), (x, -L, L)) / L)
    return a, b


def l06() -> list[dict]:
    items = []
    spec = (
        (x, PI, "x", "b", 1, "b_1", r"The function is odd, so $b_n=\dfrac{2}{\pi}\int_0^\pi x\sin nx\,dx=\dfrac{2(-1)^{n+1}}{n}$."),
        (x, PI, "x", "b", 2, "b_2", r"$b_n=\dfrac{2(-1)^{n+1}}{n}$."),
        (x, PI, "x", "b", 4, "b_4", r"$b_n=\dfrac{2(-1)^{n+1}}{n}$."),
        (x**2, PI, "x^2", "a", 1, "a_1", r"The function is even: $a_n=\dfrac{4(-1)^n}{n^2}$."),
        (x**2, PI, "x^2", "a", 3, "a_3", r"$a_n=\dfrac{4(-1)^n}{n^2}$."),
        (sp.Abs(x), PI, "|x|", "a", 3, "a_3", r"$a_n=\dfrac{2\left((-1)^n-1\right)}{\pi n^2}$, so $a_3=-\dfrac{4}{9\pi}$."),
        (x, 1, "x", "b", 1, "b_1", r"Here $L=1$: $b_n=\int_{-1}^{1}x\sin n\pi x\,dx=\dfrac{2(-1)^{n+1}}{n\pi}$."),
    )
    for k, (f, L, ftext, kind, n, name, sol) in enumerate(spec, 1):
        a, b = fourier(f, L, n)
        val = a if kind == "a" else b
        rng = r"]-\pi,\pi[" if L == PI else r"]-1,1["
        items.append(ex(f"fs-{k:02d}", rf"The coefficient ${name}$ of the Fourier series of $f(x)={ftext}$ on ${rng}$.", "expression", eng(val), hints=["Use the parity of $f$ to avoid half of the computation."], solution=sol))
    a0 = sp.simplify(sp.integrate(x**2, (x, -PI, PI)) / PI)
    items.append(ex("fs-08", r"The coefficient $a_0=\dfrac1\pi\int_{-\pi}^{\pi}f$ of $f(x)=x^2$ on $]-\pi,\pi[$.", "expression", eng(a0), hints=["Integrate $x^2$."], solution=rf"$a_0=\dfrac{{1}}{{\pi}}\cdot\dfrac{{2\pi^3}}{{3}}={tex(a0)}$."))
    sq = sp.Piecewise((-1, x < 0), (1, True))
    b3 = sp.simplify(sp.integrate(sp.sin(3 * x), (x, 0, PI)) * 2 / PI)
    items.append(ex("fs-09", r"The coefficient $b_3$ of the square wave $f=-1$ on $]-\pi,0[$, $f=1$ on $]0,\pi[$.", "expression", eng(b3), hints=["$f$ is odd: $b_n=\\dfrac2\\pi\\int_0^\\pi\\sin nx\\,dx$."], solution=rf"$b_3=\dfrac2\pi\cdot\dfrac{{2}}{{3}}={tex(b3)}$."))
    items.append(ex("fs-10", r"The function $f=0$ on $]-\pi,0[$ and $f=2$ on $]0,\pi[$ has a jump at $0$. The sum of its Fourier series at $x=0$.", "number", "1", hints=["Average the one-sided limits."], solution=r"$\dfrac{0+2}{2}=1$."))
    items.append(ex("fs-11", r"The sum of the Fourier series of $f(x)=x$ on $]-\pi,\pi[$ at $x=\pi$.", "number", "0", hints=["The left limit is $\\pi$ and the right limit (periodic extension) is $-\\pi$."], solution=r"$\dfrac{\pi+(-\pi)}{2}=0$."))
    items.append(ex("fs-12", r"What can you say about the Fourier series of the odd function $f(x)=x^2\sin x$ on $]-\pi,\pi[$?", "multiple_choice", "2",
                    choices=[{"text": "All the $b_n$ vanish", "value": "1"}, {"text": "All the $a_n$ vanish (including $a_0$)", "value": "2"}, {"text": "No coefficient vanishes", "value": "3"}], correctIndex=1,
                    hints=["Is $x^2\\sin x$ even or odd?"], solution=r"$x^2$ is even and $\sin x$ is odd, so $f$ is odd: only sines appear, all $a_n$ vanish."))
    return items


def l07() -> list[dict]:
    items = []
    spec = (
        (x * (PI - x), "x(\\pi-x)", 1), (x * (PI - x), "x(\\pi-x)", 2), (x * (PI - x), "x(\\pi-x)", 3),
        (x, "x", 2), (x, "x", 3), (sp.Integer(1), "1", 1), (sp.Integer(1), "1", 3), (PI - x, "\\pi-x", 3),
    )
    for k, (f, ftext, n) in enumerate(spec, 1):
        b = sp.simplify(2 / PI * sp.integrate(f * sp.sin(n * x), (x, 0, PI)))
        items.append(ex(f"fp-{k:02d}", rf"The coefficient $b_{n}$ of the sine series of $f(x)={ftext}$ on $]0,\pi[$.", "expression", eng(b),
                        hints=[r"$b_n=\dfrac2\pi\int_0^\pi f(x)\sin nx\,dx$."], solution=rf"$b_{n}=\dfrac{{2}}{{\pi}}\int_0^\pi {ftext}\sin {n}x\,dx={tex(b)}$."))
    items.append(ex("fp-09", r"A rod of length $\pi$ with $k=2$ has the initial temperature $x(\pi-x)$. In $u(x,t)$ the mode $n=3$ decays like $e^{-\mu t}$: find $\mu$.", "number", "18",
                    hints=["$\\mu=kn^2$ when $L=\\pi$."], solution=r"$\mu=2\cdot9=18$."))
    items.append(ex("fp-10", r"A string with $c=1$, $L=\pi$, at rest with the initial shape $x(\pi-x)$. The angular frequency of the mode $n=3$.", "number", "3",
                    hints=["$\\omega_n=\\dfrac{n\\pi c}{L}$."], solution=r"$\omega_3=3$."))
    return items


def build() -> None:
    write_exercises(f"{U1}/l01-vocabulary-and-classification", [exset("vocabulary", "Vocabulary, solutions and classification.", l01(), format=FMT)], "mvc_m05.py")
    write_exercises(f"{U1}/l02-method-of-characteristics", [exset("characteristics", "First-order equations and characteristics.", l02(), format=FMT)], "mvc_m05.py")
    write_exercises(f"{U2}/l01-the-heat-equation", [exset("heat", "The heat equation.", l03(), format=FMT)], "mvc_m05.py")
    write_exercises(f"{U2}/l02-the-wave-equation", [exset("wave", "The wave equation.", l04(), format=FMT)], "mvc_m05.py")
    write_exercises(f"{U2}/l03-laplace-equation-on-a-rectangle", [exset("laplace", "Laplace's equation.", l05(), format=FMT)], "mvc_m05.py")
    write_exercises(f"{U3}/l01-fourier-series", [exset("fourier", "Fourier series.", l06(), format=FMT)], "mvc_m05.py")
    write_exercises(f"{U3}/l02-fourier-series-and-the-pde", [exset("sine-series", "Sine series and the PDE.", l07(), format=FMT)], "mvc_m05.py")
