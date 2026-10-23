"""More practice for Course 2, Module 5: partial differential equations and Fourier series.

Every answer that is a function is checked against its equation and its boundary conditions before it ships."""

from __future__ import annotations

import sympy as sp
from mvc_m05 import FMT, PI, heat, solution_item, wave, zero
from toolkit import add_extra, eng, ex, exset_plain, simp, t, tex, x, y

SCRIPT = "more_mvc_d.py"
M5 = "mvc/m05-pde"
U1 = f"{M5}/u01-introduction-and-first-order"
U2 = f"{M5}/u02-separation-of-variables"
U3 = f"{M5}/u03-fourier-series"
xs, ys, ts = sp.symbols("x y t", real=True)


def characteristic_items() -> list[dict]:
    items = []
    s = sp.Symbol("s")
    # a u_x + b u_y = 0, u(x, 0) = g(x):  u = g((b x - a y) / b)
    a, b, g = 5, 2, xs**2 + 1
    u = sp.expand(g.subs(xs, (b * xs - a * ys) / b))
    items.append(solution_item("mp-ch-1", rf"The solution of ${a}u_x+{b}u_y=0$ with $u(x,0)={tex(g)}$ (an expression in $x$ and $y$).", u, ["x", "y"],
                               [rf"$u=f({b}x-{a}y)$; the condition at $y=0$ gives $f({b}x)={tex(g)}$."],
                               rf"$u=f({b}x-{a}y)$ and $f({b}x)={tex(g)}$, so $f(s)={tex(g.subs(xs, s / b))}$ and $u={tex(u)}$.",
                               lambda w: a * sp.diff(w, xs) + b * sp.diff(w, ys)))
    c = 4
    u = sp.sin(xs - c * ts)
    items.append(solution_item("mp-ch-2", rf"The solution of $u_t+{c}u_x=0$ with $u(x,0)=\sin x$ (an expression in $x$ and $t$).", u, ["x", "t"],
                               [r"The profile moves to the right at speed $4$."], rf"$u=f(x-{c}t)$ with $f=\sin$, so $u=\sin(x-{c}t)$.",
                               lambda w: sp.diff(w, ts) + c * sp.diff(w, xs)))
    u = sp.exp(ys - xs**3)
    items.append(solution_item("mp-ch-3", r"The solution of $u_x+3x^2\,u_y=0$ with $u(0,y)=e^{y}$.", u, ["x", "y"], [r"Solve $\dfrac{dy}{dx}=3x^2$: the characteristics are $y-x^3=C$."],
                               r"The characteristics are $y-x^3=C$, so $u=f\left(y-x^3\right)$; $u(0,y)=e^y$ gives $f=\exp$. Hence $u=e^{y-x^3}$.",
                               lambda w: sp.diff(w, xs) + 3 * xs**2 * sp.diff(w, ys)))
    u = sp.exp(-ys) * sp.cos(xs - ys)
    items.append(solution_item("mp-ch-4", r"The solution of $u_x+u_y=-u$ with $u(x,0)=\cos x$.", u, ["x", "y"], [r"$u=e^{-x}f(x-y)$."],
                               r"$u=e^{-x}f(x-y)$ and $e^{-x}f(x)=\cos x$ give $f(s)=e^{s}\cos s$, so $u=e^{-y}\cos(x-y)$.",
                               lambda w: sp.diff(w, xs) + sp.diff(w, ys) + w))
    return items


def heat_items() -> list[dict]:
    items = []
    cases = ((PI, 1, [(1, 2), (2, 3)]), (PI, 4, [(3, 1)]), (2, 3, [(1, 1), (2, -2)]), (1, 1, [(2, 5)]))
    for n, (L, k, modes) in enumerate(cases, 1):
        u, f = heat(L, k, modes)
        assert zero(sp.diff(u, ts) - k * sp.diff(u, xs, 2)) and zero(u.subs(xs, 0)) and zero(sp.simplify(u.subs(xs, L)))
        items.append(ex(f"mp-he-{n}", rf"A rod of length ${tex(L)}$ with $k={k}$ has its ends at $0$ and the initial temperature $f(x)={tex(f)}$. Find $u(x,t)$.", "expression", eng(u),
                        variables=["x", "t"], hints=[rf"The mode $n$ is multiplied by $e^{{-k(n\pi/L)^2t}}$."],
                        solution=rf"Each mode $\sin\dfrac{{n\pi x}}{{{tex(L)}}}$ is multiplied by $e^{{-{k}(n\pi/{tex(L)})^2t}}$, so $u={tex(u)}$."))
    mu = simp(4 * (3 * PI / PI) ** 2)
    items.append(ex("mp-he-5", r"On a rod of length $\pi$ with $k=4$, the number $\mu$ such that the mode $n=3$ decays like $e^{-\mu t}$.", "number", eng(mu), hints=[r"$\mu=k\left(\dfrac{n\pi}{L}\right)^2$."],
                    solution=rf"$\mu=4\cdot3^2={tex(mu)}$."))
    mu = simp(3 * (PI / 2) ** 2)
    items.append(ex("mp-he-6", r"On a rod of length $2$ with $k=3$, the number $\mu$ such that the mode $n=1$ decays like $e^{-\mu t}$.", "expression", eng(mu), hints=[r"$\mu=k\left(\dfrac{n\pi}{L}\right)^2$ with $L=2$."],
                    solution=rf"$\mu=3\cdot\dfrac{{\pi^2}}{{4}}={tex(mu)}$."))
    items.append(ex(
        "mp-he-7", r"A rod with both ends kept at temperature $0$ is heated and then left alone. What happens to its temperature $u(x,t)$ as $t\to\infty$?", "multiple_choice", "2",
        choices=[{"text": "It stays equal to the initial temperature", "value": "1"}, {"text": r"It tends to $0$ everywhere", "value": "2"}, {"text": "It becomes constant and positive", "value": "3"}],
        correctIndex=1, hints=[r"Every mode contains a factor $e^{-\mu_nt}$ with $\mu_n>0$."], solution=r"Every term of the solution has a factor $e^{-\mu_nt}\to0$, so the rod cools to the temperature $0$ of its ends.",
    ))
    return items


def wave_items() -> list[dict]:
    items = []
    cases = (
        (1, PI, [(3, 1)], [], r"a string with $c=1$, $L=\pi$, starting at rest with $f=\sin3x$"),
        (3, PI, [(1, 2), (2, 1)], [], r"a string with $c=3$, $L=\pi$, starting at rest with $f=2\sin x+\sin2x$"),
        (2, 1, [], [(1, 1)], r"a string with $c=2$, $L=1$, starting flat with the velocity $g=\sin\pi x$"),
    )
    for n, (c, L, fm, gm, text) in enumerate(cases, 1):
        u = wave(c, L, fm, gm)
        assert zero(sp.diff(u, ts, 2) - c**2 * sp.diff(u, xs, 2)) and zero(u.subs(xs, 0)) and zero(sp.simplify(u.subs(xs, L)))
        items.append(ex(f"mp-wa-{n}", rf"The displacement $u(x,t)$ of {text}, with fixed ends.", "expression", eng(u), variables=["x", "t"],
                        hints=[r"The angular frequency of the mode $n$ is $\omega_n=\dfrac{n\pi c}{L}$."], solution=rf"With $\omega_n=\dfrac{{n\pi c}}{{L}}$ the solution is $u={tex(u)}$."))
    u = sp.sin(xs) * sp.cos(3 * ts)
    assert zero(sp.diff(u, ts, 2) - 9 * sp.diff(u, xs, 2))
    items.append(ex("mp-wa-4", r"Solve $u_{tt}=c^2u_{xx}$ with $c=3$, $u(x,0)=\sin x$ and $u_t(x,0)=0$.", "expression", eng(u), variables=["x", "t"], hints=["Use d'Alembert's formula."],
                    solution=r"$\dfrac{\sin(x-3t)+\sin(x+3t)}{2}=\sin x\cos3t$."))
    w = simp(3 * PI * 2 / 4)
    items.append(ex("mp-wa-5", r"A string has $c=2$ and $L=4$. The angular frequency $\omega_3$ of its third mode.", "expression", eng(w), hints=[r"$\omega_n=\dfrac{n\pi c}{L}$."],
                    solution=rf"$\omega_3=\dfrac{{3\pi\cdot2}}{{4}}={tex(w)}$."))
    return items


def laplace_items() -> list[dict]:
    items = []
    cases = ((PI, 2, [(1, 3)]), (PI, 1, [(1, 1), (3, 2)]), (2, 1, [(2, 1)]), (1, 3, [(1, 5)]))
    for n, (a, b, modes) in enumerate(cases, 1):
        u = sum(c * sp.sin(m * PI * xs / a) * sp.sinh(m * PI * ys / a) / sp.sinh(m * PI * b / a) for m, c in modes)
        f = sum(c * sp.sin(m * PI * xs / a) for m, c in modes)
        assert zero(sp.diff(u, xs, 2) + sp.diff(u, ys, 2)) and zero(u.subs(xs, 0)) and zero(sp.simplify(u.subs(xs, a))) and zero(u.subs(ys, 0)) and zero(sp.simplify(u.subs(ys, b) - f))
        items.append(ex(f"mp-la-{n}", rf"On the rectangle $0\le x\le{tex(a)}$, $0\le y\le{b}$, solve $u_{{xx}}+u_{{yy}}=0$ with $u=0$ on three sides and $u(x,{b})={tex(f)}$.", "expression", eng(u),
                        variables=["x", "y"], hints=[r"The modes are $\sin\dfrac{n\pi x}{a}\sinh\dfrac{n\pi y}{a}$; divide by the value at the top."], solution=rf"$u={tex(u)}$."))
    # harmonic functions
    for k, (f, name, harmonic) in enumerate(((xs**2 - ys**2, "x^2-y^2", True), (sp.exp(xs) * sp.sin(ys), r"e^{x}\sin y", True), (xs**2 + ys**2, "x^2+y^2", False)), 5):
        lap = simp(sp.diff(f, xs, 2) + sp.diff(f, ys, 2))
        assert (lap == 0) == harmonic
        items.append(ex(f"mp-la-{k}", rf"Does $u={name}$ satisfy Laplace's equation $u_{{xx}}+u_{{yy}}=0$?", "multiple_choice", "1" if harmonic else "2",
                        choices=[{"text": "Yes", "value": "1"}, {"text": "No", "value": "2"}], correctIndex=0 if harmonic else 1, hints=[r"Compute $u_{xx}+u_{yy}$."],
                        solution=rf"$u_{{xx}}+u_{{yy}}={tex(lap)}$" + (", so it does." if harmonic else ", which is not $0$, so it does not.")))
    k_ = sp.Symbol("k")
    kval = sp.solve(sp.diff(xs**3 + k_ * xs * ys**2, xs, 2) + sp.diff(xs**3 + k_ * xs * ys**2, ys, 2), k_)
    assert kval == [-3]
    items.append(ex("mp-la-8", r"The number $k$ for which $u=x^3+kxy^2$ satisfies Laplace's equation $u_{xx}+u_{yy}=0$ for all $(x,y)$.", "number", "-3",
                    hints=[r"$u_{xx}=6x$ and $u_{yy}=2kx$."], solution=r"$6x+2kx=0$ for all $x$ gives $k=-3$."))
    return items


def fourier_items() -> list[dict]:
    items = []
    val = simp(2 * sp.integrate(xs * sp.cos(xs), (xs, 0, PI)) / PI)
    assert val == simp(-4 / PI)
    items.append(ex("mp-fs-1", r"The coefficient $a_1$ of the Fourier series of $f(x)=|x|$ on $]-\pi,\pi[$.", "expression", eng(val), hints=["The function is even: $a_n=\\dfrac2\\pi\\int_0^\\pi x\\cos nx\\,dx$."],
                    solution=rf"$a_1=\dfrac2\pi\int_0^\pi x\cos x\,dx=\dfrac{{2}}{{\pi}}\cdot(-2)={tex(val)}$."))
    b1 = simp(sp.integrate(xs**3 * sp.sin(xs), (xs, -PI, PI)) / PI)
    items.append(ex("mp-fs-2", r"The coefficient $b_1$ of the Fourier series of $f(x)=x^3$ on $]-\pi,\pi[$.", "expression", eng(b1), hints=["The function is odd: $b_n=\\dfrac2\\pi\\int_0^\\pi x^3\\sin nx\\,dx$. Integrate by parts three times."],
                    solution=rf"$b_1=\dfrac2\pi\int_0^\pi x^3\sin x\,dx={tex(b1)}$."))
    a0 = simp(2 * sp.integrate(xs, (xs, 0, PI)) / PI)
    items.append(ex("mp-fs-3", r"The coefficient $a_0=\dfrac1\pi\int_{-\pi}^{\pi}f$ of $f(x)=|x|$ on $]-\pi,\pi[$.", "expression", eng(a0), hints=["The function is even."], solution=rf"$a_0=\dfrac2\pi\int_0^\pi x\,dx={tex(a0)}$."))
    return items


def sine_series_items() -> list[dict]:
    items = []
    for k, (f, ftext, n) in enumerate(((xs**2, "x^2", 1), (xs**2, "x^2", 2), (xs * (PI - xs), "x(\\pi-x)", 5), (sp.Integer(2), "2", 2), (PI - xs, "\\pi-x", 1)), 1):
        b = simp(2 / PI * sp.integrate(f * sp.sin(n * xs), (xs, 0, PI)))
        items.append(ex(f"mp-fp-{k}", rf"The coefficient $b_{n}$ of the sine series of $f(x)={ftext}$ on $]0,\pi[$.", "expression", eng(b), hints=[r"$b_n=\dfrac2\pi\int_0^\pi f(x)\sin nx\,dx$."],
                        solution=rf"$b_{n}=\dfrac{{2}}{{\pi}}\int_0^\pi {ftext}\sin {n}x\,dx={tex(b)}$."))
    return items


def register() -> None:
    add_extra(f"{U1}/l02-method-of-characteristics", exset_plain("more-characteristics", "More practice: characteristics.", characteristic_items(), format=FMT), SCRIPT)
    add_extra(f"{U2}/l01-the-heat-equation", exset_plain("more-heat", "More practice: the heat equation.", heat_items(), format=FMT), SCRIPT)
    add_extra(f"{U2}/l02-the-wave-equation", exset_plain("more-wave", "More practice: the wave equation.", wave_items(), format=FMT), SCRIPT)
    add_extra(f"{U2}/l03-laplace-equation-on-a-rectangle", exset_plain("more-laplace", "More practice: Laplace's equation.", laplace_items(), format=FMT), SCRIPT)
    add_extra(f"{U3}/l01-fourier-series", exset_plain("more-fourier", "More practice: Fourier coefficients.", fourier_items(), format=FMT), SCRIPT)
    add_extra(f"{U3}/l02-fourier-series-and-the-pde", exset_plain("more-sine", "More practice: sine series.", sine_series_items(), format=FMT), SCRIPT)
    assert t is not None and x is not None and y is not None
