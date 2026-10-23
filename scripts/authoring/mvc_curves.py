"""Exercises of Course 2, Module 1, Unit 6: vector functions, velocity, acceleration and arc length (original exercises)."""

from __future__ import annotations

import sympy as sp
from toolkit import P, eng, ex, exset_plain, simp, t, tex, write_exercises


def vec_tex(v: list[sp.Expr]) -> str:
    return r"\left(" + r",\,".join(tex(c) for c in v) + r"\right)"


def vec_key(v: list[sp.Expr]) -> str:
    return "(" + ", ".join(eng(c) for c in v) + ")"


def kind_of(value: sp.Expr) -> str:
    return "number" if value.is_Rational else "expression"


def r_tex(comps: list[sp.Expr]) -> str:
    return r"\left(" + r",\ ".join(tex(c) for c in comps) + r"\right)"


def at(vec: list[sp.Expr], t0: sp.Expr) -> list[sp.Expr]:
    return [simp(c.subs(t, t0)) for c in vec]


def curve_items() -> list[list[dict]]:
    motion: list[dict] = []
    tangents: list[dict] = []
    lengths: list[dict] = []
    rules: list[dict] = []

    def rt(comps: list[str]) -> list[sp.Expr]:
        return [P(c) for c in comps]

    def velocity_item(i: str, comps: list[str], t0: sp.Expr, t0_tex: str) -> None:
        r = rt(comps)
        v = [sp.diff(c, t) for c in r]
        val = at(v, t0)
        motion.append(ex(
            f"mo-{i}a", rf"A point moves along $\vec r(t)={r_tex(r)}$. Find its velocity at $t={t0_tex}$.", "vector", vec_key(val),
            hints=[r"Differentiate each coordinate, then substitute $t$."],
            solution=rf"$\vec v(t)=\vec r\,'(t)={r_tex(v)}$, so $\vec v({t0_tex})={vec_tex(val)}$.",
        ))

    def accel_item(i: str, comps: list[str], t0: sp.Expr, t0_tex: str) -> None:
        r = rt(comps)
        a = [sp.diff(c, t, 2) for c in r]
        val = at(a, t0)
        motion.append(ex(
            f"mo-{i}b", rf"A point moves along $\vec r(t)={r_tex(r)}$. Find its acceleration at $t={t0_tex}$.", "vector", vec_key(val),
            hints=[r"Differentiate twice: $\vec a=\vec r\,''$."],
            solution=rf"$\vec r\,''(t)={r_tex(a)}$, so $\vec a({t0_tex})={vec_tex(val)}$.",
        ))

    def speed_item(i: str, comps: list[str], t0: sp.Expr, t0_tex: str) -> None:
        r = rt(comps)
        v = [sp.diff(c, t) for c in r]
        val = simp(sp.sqrt(sum(c**2 for c in at(v, t0))))
        motion.append(ex(
            f"mo-{i}c", rf"A point moves along $\vec r(t)={r_tex(r)}$. Find its speed at $t={t0_tex}$.", kind_of(val), eng(val),
            hints=[r"The speed is the length of the velocity vector."],
            solution=rf"$\vec v={r_tex(v)}$, which at $t={t0_tex}$ is ${vec_tex(at(v, t0))}$. Its length is ${tex(val)}$.",
        ))

    velocity_item("01", ["t^2", "t^3", "2*t"], sp.Integer(1), "1")
    velocity_item("02", ["ln(t)", "t", "t^2"], sp.Integer(1), "1")
    accel_item("01", ["cos(2*t)", "sin(2*t)"], sp.pi / 4, r"\dfrac\pi4")
    accel_item("02", ["t", "t^2", "t^3"], sp.Integer(2), "2")
    speed_item("01", ["exp(t)", "exp(-t)", "sqrt(2)*t"], sp.Integer(0), "0")
    speed_item("02", ["3*cos(t)", "3*sin(t)", "4*t"], sp.pi, r"\pi")
    speed_item("03", ["t^2", "2*t"], sp.Integer(1), "1")

    # a horizontal tangent: y'(t)=0 with x'(t)!=0
    sols = sp.solve(sp.diff(P("t^2"), t), t)
    assert sols == [0] and sp.diff(P("t^3-3*t"), t).subs(t, 0) != 0
    motion.append(ex(
        "mo-04", r"For which $t$ is the tangent to the curve $\vec r(t)=(t^3-3t,\ t^2)$ horizontal?", "number", "0",
        hints=[r"A horizontal tangent has velocity $(x',0)$ with $x'\ne0$."],
        solution=r"$\vec r\,'=(3t^2-3,\ 2t)$. The second coordinate is $0$ only for $t=0$, and there $x'=-3\ne0$.",
    ))

    def tangent_item(i: str, comps: list[str], t0: sp.Expr, t0_tex: str) -> None:
        r = rt(comps)
        v = at([sp.diff(c, t) for c in r], t0)
        tangents.append(ex(
            f"tg-{i}a", rf"Give a direction vector of the tangent line to $\vec r(t)={r_tex(r)}$ at $t={t0_tex}$.", "direction", vec_key(v),
            hints=[r"The tangent vector is $\vec r\,'(t_0)$."],
            solution=rf"$\vec r\,'(t)={r_tex([sp.diff(c, t) for c in r])}$, so $\vec r\,'({t0_tex})={vec_tex(v)}$. Any non-zero multiple is accepted.",
        ))
        pt = at(r, t0)
        tangents.append(ex(
            f"tg-{i}b", rf"Find the point of the curve $\vec r(t)={r_tex(r)}$ at $t={t0_tex}$.", "vector", vec_key(pt),
            hints=[r"Substitute the value of $t$ in each coordinate."],
            solution=rf"$\vec r({t0_tex})={vec_tex(pt)}$.",
        ))

    tangent_item("01", ["t", "exp(t)", "cos(t)"], sp.Integer(0), "0")
    tangent_item("02", ["2*t", "t^2", "t^3"], sp.Integer(2), "2")

    def length_item(i: str, comps: list[str], lo: sp.Expr, hi: sp.Expr, rng_tex: str) -> None:
        r = rt(comps)
        v = [sp.diff(c, t) for c in r]
        speed = simp(sp.sqrt(sum(c**2 for c in v)))
        val = simp(sp.integrate(speed, (t, lo, hi)))
        num = float(sp.Integral(speed, (t, lo, hi)).evalf(15))
        assert abs(float(val) - num) < 1e-9, (comps, val, num)
        lengths.append(ex(
            f"ln-{i}", rf"Find the length of the curve $\vec r(t)={r_tex(r)}$ for ${rng_tex}$. The unit is lu: give the number only.", kind_of(val), eng(val),
            hints=[r"$L=\int\norm{\vec r\,'(t)}\,dt$. Simplify the speed first."],
            solution=rf"$\vec r\,'={r_tex(v)}$ has length ${tex(speed)}$. Then $L=\int_{{{tex(lo)}}}^{{{tex(hi)}}}{tex(speed)}\,dt={tex(val)}$.",
        ))

    length_item("01", ["3*t", "4*t"], sp.Integer(0), sp.Integer(2), r"0\le t\le2")
    length_item("02", ["cos(t)", "sin(t)", "t"], sp.Integer(0), sp.pi, r"0\le t\le\pi")
    length_item("03", ["t^2", "t^3"], sp.Integer(0), sp.Integer(1), r"0\le t\le1")
    length_item("04", ["exp(t)*cos(t)", "exp(t)*sin(t)"], sp.Integer(0), sp.Integer(1), r"0\le t\le1")

    rules.append(ex(
        "rl-01", r"A point moves on a sphere centred at the origin. Which statement is true for its velocity $\vec v$ and position $\vec r$ at every time?",
        "multiple_choice", "2",
        choices=[
            {"text": r"$\vec v$ is parallel to $\vec r$", "value": "1"},
            {"text": r"$\vec v$ is perpendicular to $\vec r$", "value": "2"},
            {"text": r"$\vec v=\vec 0$", "value": "3"},
        ],
        correctIndex=1, hints=[r"Differentiate $\dotp{\vec r}{\vec r}=\text{constant}$."],
        solution=r"$\dotp{\vec r}{\vec r}$ is constant, so $2\dotp{\vec r}{\vec r\,'}=0$: the velocity is perpendicular to the position.",
    ))
    r1, s1 = [t, sp.Integer(1), sp.Integer(0)], [t**2, t, sp.Integer(1)]
    dot = sp.expand(sum(a * b for a, b in zip(r1, s1, strict=True)))
    val = simp(sp.diff(dot, t).subs(t, 1))
    rules.append(ex(
        "rl-02", r"Let $\vec r(t)=(t,\ 1,\ 0)$ and $\vec s(t)=(t^2,\ t,\ 1)$. Find $\dfrac{d}{dt}\dotp{\vec r}{\vec s}$ at $t=1$.", "number", eng(val),
        hints=[r"Either expand $\dotp{\vec r}{\vec s}$ and differentiate, or use the product rule."],
        solution=rf"$\dotp{{\vec r}}{{\vec s}}=t^3+t$, so the derivative is $3t^2+1={tex(val)}$ at $t=1$.",
    ))
    return [motion, tangents, lengths, rules]


def build() -> None:
    motion, tangents, lengths, rules = curve_items()
    write_exercises(
        "mvc/m01-derivatives/u06-space-curves/l01-vector-functions",
        [
            exset_plain("motion", "Velocity, acceleration and speed.", motion,
                        format="Type a vector like `(2, -1, 3)` or an exact value such as `sqrt(5)`."),
            exset_plain("tangent", "Tangent vectors and points of a curve.", tangents,
                        format="Type a vector like `(1, 2, 3)`; for a direction any non-zero multiple is accepted."),
            exset_plain("length", "The length of a curve.", lengths, format="Type an exact value such as `3*sqrt(2)*pi` or `(2*sqrt(5)-1)/3`."),
            exset_plain("rules", "Rules of differentiation.", rules, format="Type a number."),
        ],
        "mvc_curves.py",
    )
