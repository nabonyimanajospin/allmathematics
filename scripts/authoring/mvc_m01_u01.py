"""Exercises of Course 2, Module 1, Unit 1 (domains, limits, continuity), sheet part A.I to A.III."""

from __future__ import annotations

import mpmath as mp
import sympy as sp
from toolkit import ex, exset, P, defined_real, write_exercises, x, y, z

from allmaths_engine.region import compile_region, sample_points  # noqa: E402

REGION_FORMAT = (
    "Type the conditions on the variables, for example `x > 0 and y <= 2`. Use `<=` and `>=` for ≤ and ≥, "
    "and the words `and` / `or` to combine conditions. The words true (all points) and false (no point) are accepted."
)


def audit_domain(fn: str, key: str, coords: list[str], *, invert: bool = False) -> None:
    """The key region must equal the set where the formula gives a real number (or its complement)."""
    f = P(fn)
    region = compile_region(key, coords, "text")
    syms = {c: sp.Symbol(c, real=True) for c in coords}
    for pt in sample_points(coords):
        defined = defined_real(f, {syms[c]: pt[c] for c in coords})
        inside = region.contains(pt)
        if (inside == defined) == invert:
            raise AssertionError(f"domain key {key!r} disagrees with {fn!r} at {pt}: defined={defined}, in key={inside}")


# --- A.I domains -----------------------------------------------------------------------------------------------
def domain_items() -> list[dict]:
    spec = [
        ("dom-01", r"z=\sqrt{4-x^2-y^2}", "sqrt(4-x^2-y^2)", "x^2+y^2<=4", ["x", "y"],
         "A square root needs a non-negative argument.",
         r"The square root needs a non-negative argument: $4-x^2-y^2\ge0$, that is $x^2+y^2\le4$. "
         "The domain is the closed disc of radius $2$ centred at the origin; the circle itself is included.", None),
        ("dom-02", r"z=\ln(x+y)", "ln(x+y)", "x+y>0", ["x", "y"],
         "A logarithm needs a positive argument.",
         r"The logarithm needs a positive argument: $x+y>0$, that is $y>-x$. "
         "The domain is the open half-plane above the line $y=-x$; the line itself is excluded.", None),
        ("dom-03", r"z=\arctan\dfrac{1}{x^2+y^2}", "atan(1/(x^2+y^2))", "x^2+y^2>0", ["x", "y"],
         "The arctangent accepts every real number. What can still go wrong?",
         r"The arctangent accepts every real number, so only the denominator matters: $x^2+y^2\neq0$. "
         "Since $x^2+y^2\\ge0$ always, this means $x^2+y^2>0$. The domain is the whole plane except the origin.", None),
        ("dom-04", r"z=\sqrt{1-x^2}+\sqrt{1-y^2}", "sqrt(1-x^2)+sqrt(1-y^2)", "x^2<=1 and y^2<=1", ["x", "y"],
         "Both roots need a non-negative argument, and both conditions must hold together.",
         r"Both roots need non-negative arguments: $1-x^2\ge0$ and $1-y^2\ge0$, so $-1\le x\le1$ and $-1\le y\le1$. "
         r"The domain is the closed square with vertices $(\pm1,\pm1)$.", None),
        ("dom-05", r"z=\sqrt{x^2-4}+\sqrt{4-y^2}", "sqrt(x^2-4)+sqrt(4-y^2)", "x^2>=4 and y^2<=4", ["x", "y"],
         "Solve each root condition separately, then combine them with “and”.",
         r"$x^2-4\ge0$ gives $x\le-2$ or $x\ge2$. $4-y^2\ge0$ gives $-2\le y\le2$. The domain consists of the points "
         r"with $|x|\ge2$ and $|y|\le2$: two closed vertical-bounded strips, one on each side of the $y$-axis.", None),
        ("dom-06", r"z=\arctan\dfrac{x-y}{1+x^2y^2}", "atan((x-y)/(1+x^2*y^2))", "true", ["x", "y"],
         "Can the denominator $1+x^2y^2$ ever be zero?",
         r"The denominator is $1+x^2y^2\ge1$, so it is never zero, and the arctangent accepts every real number. "
         "The domain is the whole plane.", None),
        ("dom-07", r"u=\sqrt{1-x^2-y^2-z^2}", "sqrt(1-x^2-y^2-z^2)", "x^2+y^2+z^2<=1", ["x", "y", "z"],
         "The argument of the root must not be negative; this time there are three variables.",
         r"The root needs $1-x^2-y^2-z^2\ge0$, that is $x^2+y^2+z^2\le1$. The domain is the closed ball of radius $1$ "
         "centred at the origin.", None),
        ("dom-08", r"w=\ln(xyz)", "ln(x*y*z)", "x*y*z>0", ["x", "y", "z"],
         "The product $xyz$ must be positive. How many of the three numbers can be negative?",
         r"The logarithm needs $xyz>0$. A product of three numbers is positive when all three are positive, or when exactly "
         "two are negative. The domain is made of four of the eight octants.",
         "The sheet prints this function as $z=\\ln(xyz)$. The output is called $w$ here because $z$ is also a variable."),
        ("dom-09", r"w=\sqrt x+\sqrt y+\sqrt z", "sqrt(x)+sqrt(y)+sqrt(z)", "x>=0 and y>=0 and z>=0", ["x", "y", "z"],
         "Each of the three roots gives its own condition.",
         r"Each root needs a non-negative argument: $x\ge0$, $y\ge0$, $z\ge0$. The domain is the first octant, "
         "including the three coordinate planes.",
         "The sheet prints this function as $z=\\sqrt x+\\sqrt y+\\sqrt z$. The output is called $w$ here because $z$ is also a variable."),
        ("dom-10", r"w=\arcsin x+\arcsin y+\arcsin z", "asin(x)+asin(y)+asin(z)", "x^2<=1 and y^2<=1 and z^2<=1", ["x", "y", "z"],
         r"The arcsine is defined for arguments between $-1$ and $1$.",
         r"Each arcsine needs its argument in $[-1,1]$: $-1\le x\le1$, $-1\le y\le1$, $-1\le z\le1$. The domain is the "
         "closed cube of edge $2$ centred at the origin.", None),
        ("dom-11", r"w=\sqrt{x^2+y^2+z^2-4}+\sqrt{4-x^2-y^2-z^2}", "sqrt(x^2+y^2+z^2-4)+sqrt(4-x^2-y^2-z^2)",
         "x^2+y^2+z^2=4", ["x", "y", "z"],
         "Write both conditions with $s=x^2+y^2+z^2$ and see what they say together.",
         r"The first root needs $x^2+y^2+z^2\ge4$ and the second needs $x^2+y^2+z^2\le4$. Both hold only when "
         "$x^2+y^2+z^2=4$. The domain is the sphere of radius $2$ (its surface only, not the inside).", None),
    ]
    items = []
    for id_, latex, fn, key, coords, hint, solution, note in spec:
        audit_domain(fn, key, coords)
        items.append(
            ex(id_, f"${latex}$", "region", key, coordinates=coords, hints=[hint], solution=solution,
               **({"note": note} if note else {}))
        )
    return items


# --- A.III discontinuities -------------------------------------------------------------------------------------
def discontinuity_items() -> list[dict]:
    spec = [
        ("dis-01", r"z=\sqrt{9-x^2-y^2}", "sqrt(9-x^2-y^2)", "x^2+y^2>9",
         r"$\sqrt{9-x^2-y^2}$ is a composition of continuous functions, so it is continuous at every point where it is defined, "
         r"the disc $x^2+y^2\le9$. It is not defined at the points with $x^2+y^2>9$: these are the points of discontinuity."),
        ("dis-02", r"z=\ln\sqrt{x^2+y^2}", "ln(sqrt(x^2+y^2))", "x=0 and y=0",
         r"The logarithm needs $\sqrt{x^2+y^2}>0$, that is $(x,y)\neq(0,0)$. Everywhere else the function is continuous. "
         "The only point of discontinuity is the origin."),
        ("dis-03", r"z=\dfrac{1}{(x-y)^2}", "1/(x-y)^2", "x=y",
         r"A quotient is continuous where its denominator is not zero. $(x-y)^2=0$ on the line $y=x$, where the function "
         "is not defined. The points of discontinuity form the line $y=x$."),
        ("dis-04", r"z=\dfrac{1}{\sqrt{1-x^2-y^2}}", "1/sqrt(1-x^2-y^2)", "x^2+y^2>=1",
         r"The function is defined, and continuous, where $1-x^2-y^2>0$, the open unit disc. It is not defined where "
         r"$x^2+y^2\ge1$: on the unit circle (zero denominator) and outside it (negative radicand)."),
        ("dis-05", r"z=\dfrac{1}{\sqrt{1-x^2}+\sqrt{1-y^2}}", "1/(sqrt(1-x^2)+sqrt(1-y^2))",
         "x^2>1 or y^2>1 or (x^2=1 and y^2=1)",
         r"The roots need $|x|\le1$ and $|y|\le1$, so the function is undefined outside the closed square. Inside the square "
         r"the denominator is $\ge0$ and it is zero only if both roots are zero, that is $x^2=1$ and $y^2=1$: the four corners "
         r"$(\pm1,\pm1)$. The points of discontinuity are the points outside the square and the four corners."),
        ("dis-06", r"z=\dfrac{2}{1-x^2-y^2}", "2/(1-x^2-y^2)", "x^2+y^2=1",
         r"The denominator is zero when $x^2+y^2=1$. The function is a quotient of polynomials, hence continuous everywhere else. "
         "The points of discontinuity form the unit circle."),
    ]
    items = []
    for id_, latex, fn, key, solution in spec:
        audit_domain(fn, key, ["x", "y"], invert=True)
        items.append(
            ex(id_, f"${latex}$", "region", key, coordinates=["x", "y"],
               hints=["A formula is continuous wherever it is defined. Find where it is not defined."], solution=solution)
        )
    return items


# --- A.II limits ------------------------------------------------------------------------------------------------
def _along(f: sp.Expr, path, s: float) -> float:
    """f along a path (x(s), y(s)) at parameter s."""
    mp.mp.dps = 40
    fx, fy = path(mp.mpf(s))
    return float(sp.lambdify((x, y), f, modules="mpmath")(fx, fy))


def audit_limit(fn: str, paths, expected: float | None) -> None:
    """Numbers along several paths: all close to `expected`, or at least two clearly different values."""
    f = P(fn)
    vals = [_along(f, p, 1e-9) for p in paths]
    if expected is None:
        if max(vals) - min(vals) < 1e-3:
            raise AssertionError(f"{fn}: the paths agree ({vals}) but the key says the limit does not exist")
    else:
        for v in vals:
            if abs(v - expected) > 1e-4:
                raise AssertionError(f"{fn}: a path gives {v}, the key says {expected}")


def limit_items() -> list[dict]:
    items = []
    audit_limit("sin(x*y)/x", [lambda s: (s, 2 + s), lambda s: (s, 2), lambda s: (s * s, 2 - s), lambda s: (-s, 2 + s)], 2)
    items.append(ex(
        "lim-01", r"\displaystyle\lim_{(x,y)\to(0,2)}\frac{\sin xy}{x}".join(["$", "$"]), "number", "2",
        hints=[r"Write $\dfrac{\sin xy}{x}=y\cdot\dfrac{\sin xy}{xy}$ and use $\dfrac{\sin u}{u}\to1$."],
        solution=r"$\dfrac{\sin xy}{x}=y\cdot\dfrac{\sin xy}{xy}$. As $(x,y)\to(0,2)$ we have $u=xy\to0$, so $\dfrac{\sin u}{u}\to1$, "
                 r"and $y\to2$. The limit is $2\cdot1=2$.",
        verify=[{"expr": "limit(sin(x*2)/x, x, 0)", "equals": "2"}],
    ))
    items.append(ex(
        "lim-02", r"\displaystyle\lim_{(x,y)\to(\infty,k)}\left(1+\frac yx\right)^x".join(["$", "$"]), "expression", "e^k",
        variables=["k"],
        hints=[r"Write $\left(1+\dfrac yx\right)^x=\left[\left(1+\dfrac yx\right)^{x/y}\right]^{y}$ and recall $\left(1+\dfrac1n\right)^n\to e$."],
        solution=r"With $n=\dfrac xy$ we get $\left(1+\dfrac yx\right)^x=\left[\left(1+\dfrac1n\right)^n\right]^y$. "
                 r"As $x\to\infty$ with $y\to k$ (and $k\neq0$), $n\to\infty$ and $\left(1+\dfrac1n\right)^n\to e$, while $y\to k$. "
                 r"The limit is $e^k$. For $k=0$ the expression equals $1=e^0$ as well.",
        verify=[{"expr": "limit((1+k/x)^x, x, oo)", "equals": "e^k"}],
    ))
    items.append(ex(
        "lim-03", r"\displaystyle\lim_{(x,y)\to(\infty,\infty)}\frac{x+y}{x^2+y^2}".join(["$", "$"]), "number", "0",
        hints=[r"For $x,y>0$ compare $x+y$ with $2\max(x,y)$ and $x^2+y^2$ with $\max(x,y)^2$."],
        solution=r"Take $x,y>0$ and let $M=\max(x,y)$. Then $x+y\le2M$ and $x^2+y^2\ge M^2$, so "
                 r"$0<\dfrac{x+y}{x^2+y^2}\le\dfrac{2}{M}\to0$. By the squeeze principle the limit is $0$.",
        verify=[{"expr": "limit((x+x)/(x^2+x^2), x, oo)", "equals": "0"}],
    ))
    audit_limit("x/(x+y)", [lambda s: (s, 0 * s + 1e-30), lambda s: (0 * s + 1e-30, s), lambda s: (s, s)], None)
    items.append(ex(
        "lim-04", r"\displaystyle\lim_{(x,y)\to(0,0)}\frac{x}{x+y}".join(["$", "$"]), "number", "@dne",
        hints=["Try the path $y=0$, then the path $x=0$."],
        solution=r"Along $y=0$ (with $x\neq0$): $\dfrac{x}{x+0}=1$, so the values tend to $1$. Along $x=0$ (with $y\neq0$): "
                 r"$\dfrac{0}{y}=0$, so the values tend to $0$. Two paths give two different numbers, so the limit does not exist.",
        note=None,
    ))
    audit_limit("(x^2-y^2)/(x^2+y^2)", [lambda s: (s, 1e-30 * s), lambda s: (1e-30 * s, s)], None)
    items.append(ex(
        "lim-05", r"\displaystyle\lim_{(x,y)\to(0,0)}\frac{x^2-y^2}{x^2+y^2}".join(["$", "$"]), "number", "@dne",
        hints=["Compare the values along the $x$-axis and along the $y$-axis."],
        solution=r"Along the $x$-axis ($y=0$): $\dfrac{x^2}{x^2}=1$. Along the $y$-axis ($x=0$): $\dfrac{-y^2}{y^2}=-1$. "
                 "The two paths give $1$ and $-1$, so the limit does not exist.",
    ))
    audit_limit("(x^2+y^2)*sin(1/(x*y))", [lambda s: (s, s), lambda s: (s, 2 * s), lambda s: (s, s * s + s)], 0)
    items.append(ex(
        "lim-06", r"\displaystyle\lim_{(x,y)\to(0,0)}(x^2+y^2)\sin\frac1{xy}".join(["$", "$"]), "number", "0",
        hints=[r"The sine is always between $-1$ and $1$. Use the squeeze principle."],
        solution=r"Because $\left|\sin\dfrac1{xy}\right|\le1$, we have $\left|(x^2+y^2)\sin\dfrac1{xy}\right|\le x^2+y^2$. "
                 "The bound $x^2+y^2$ tends to $0$, so by the squeeze principle the limit is $0$. "
                 "(The function is not defined on the axes, but the limit is taken over the points where it is defined.)",
    ))
    return items


def build() -> None:
    write_exercises(
        "mvc/m01-derivatives/u01-functions-of-several-variables/l01-domains",
        [exset("domains", "Find the domain of definition of each function.", domain_items(), format=REGION_FORMAT)],
        "mvc_m01_u01.py",
    )
    write_exercises(
        "mvc/m01-derivatives/u01-functions-of-several-variables/l02-limits-and-continuity",
        [
            exset(
                "limits", "Evaluate each limit, or show that it does not exist.", limit_items(),
                format="Type a number or an exact expression. If the limit does not exist, type `DNE` or `does not exist`.",
            ),
            exset(
                "discontinuities",
                "Find the set of points of the plane at which the function is not continuous. "
                "Count the points where the formula is not defined.",
                discontinuity_items(), format=REGION_FORMAT,
            ),
        ],
        "mvc_m01_u01.py",
    )
