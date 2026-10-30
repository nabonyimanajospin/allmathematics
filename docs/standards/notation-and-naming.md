# Notation and naming

One notation for the whole platform, at every level. Notation is written with the macros of `packages/notation` wherever a macro exists, so that a convention can be changed in one place. This document extends section 6 of `MATH_PLATFORM_BUILD_SPEC.md`; where they differ, this document is the newer decision.

## 1. Exact values (Rule)

1. Answers and results are exact: `\dfrac{7}{2}`, not 3.5; `2\sqrt3`, not `\sqrt{12}`; π, e and `\ln 2` stay symbolic.
2. Fractions reduced, radicals simplified, denominators rationalized; display fractions with `\dfrac`, a fraction inside a fraction with `\tfrac`.
3. Angles in radians as exact multiples of π, or in exact degrees when the question uses degrees; a non-standard angle is written `\arccos(...)`.
4. A decimal appears only when the question asks for an approximation, and then the exact value is shown first, followed by `\approx`.
5. Decimal input from a learner is refused with a friendly message, unless the question asks for an approximation.

## 2. Numbers, sets and logic (Proposed)

| Concept | Notation | Notes |
|---|---|---|
| Number sets | `\mathbb N, \mathbb Z, \mathbb Q, \mathbb R, \mathbb C` | `\mathbb N` contains 0; `\mathbb N^*` without 0 |
| Intervals | `[a, b]`, `(a, b)`, `[a, b)`, `(-\infty, a]` | round bracket for an open end (not `]a, b[`) |
| Set of solutions | `S = \{2, 3\}`; empty set `\varnothing` | |
| Belongs, subset | `\in`, `\subseteq`, `\subset` (strict) | |
| Union, intersection, complement | `\cup`, `\cap`, `\overline{A}` or `A^c` | probability uses `A^c` (choose one per course and keep it) |
| Implication, equivalence | `\Rightarrow`, `\Leftrightarrow` | |
| For all, there exists | `\forall`, `\exists` | |
| Absolute value | `\lvert x \rvert` | |
| Integer part | `\lfloor x \rfloor`, `\lceil x \rceil` | |
| Approximately | `\approx` | only with a decimal that was asked for |

## 3. Functions and calculus (Rule where already used, Proposed otherwise)

| Concept | Notation |
|---|---|
| Function | `f : \mathbb R \to \mathbb R,\ x \mapsto f(x)`; domain `D_f` |
| Composition, inverse | `g \circ f`, `f^{-1}` (inverse function only, never `1/f`) |
| Natural logarithm, base b | `\ln x`, `\log_b x` (`\log` alone is never used) |
| Inverse trigonometric | `\arcsin, \arccos, \arctan` (never `\sin^{-1}`) |
| Limit | `\lim_{x \to a} f(x)`, one-sided `\lim_{x \to a^+}` |
| Derivative | `f'(x)`, `\dfrac{dy}{dx}`, higher `f''`, `f^{(n)}` |
| Partial derivative | `\dfrac{\partial f}{\partial x}` and `f_x`; mixed `\dfrac{\partial^2 f}{\partial x\,\partial y}` |
| Gradient, directional derivative | `\nabla f`, `D_{\vec u} f` |
| Hessian, Jacobian | `H_f`, `\dfrac{\partial(x,y)}{\partial(u,v)}` |
| Integrals | always with the differential and a thin space: `\int_a^b f(x)\,dx`, `\iint_D f\,dA`, `\iiint_E f\,dV`, `\oint_C` |
| Sequences and series | `(u_n)_{n \ge 0}`, `\sum_{n=1}^{\infty} a_n` |
| Differential equations | `y', y''`; constants `C_1, C_2`; initial conditions written explicitly `y(0) = 1` |

## 4. Vectors and geometry (Rule)

| Concept | Notation | Macro |
|---|---|---|
| Vector | `\vec u` (always an arrow; never bold, never plain) | `\vec{u}` |
| Vector between points | `\overrightarrow{AB}` | |
| Vector value | written as a **column** | the renderer turns `\overrightarrow{AB}=(3,4)` into a column |
| Point | capital letter, coordinates as a **row** `A(1, 2)` | |
| Norm (length) | `\norm{\vec u}`; a length of a segment is `\norm{\overrightarrow{BC}}`, never `BC` alone | `\norm{}` |
| Dot product | `\dotp{\vec u}{\vec v}`, shown ⟨u, v⟩ | `\dotp{}{}` |
| Cross product | `\crossp{\vec u}{\vec v}`, shown [u, v] (the course's convention; "other notations you may see: u × v" once per relevant lesson) | `\crossp{}{}` |
| Box (mixed) product | `\boxp{\vec u}{\vec v}{\vec w}`, shown ⟨u, v, w⟩ | `\boxp{}{}{}` |
| Lines, planes | `(D)`, `(\Delta)`; planes `(P)`, `\Pi` | |
| Vector equation of a line | a point plus λ times a column vector | |
| Parametric equations | `\begin{cases} ... \end{cases}` | |
| Distance | `d(A, B)`, `d(A, (D))`, `d(A, \Pi)` | |
| Triangle | sides `a, b, c` opposite `A, B, C`; semiperimeter `s`; **area `S`**; inradius `r`; circumradius `R`; centers `G` (centroid), `I` (incenter), `O` (circumcenter), `H` (orthocenter) | |
| Circle equations | **canonical** `(x-p)^2 + (y-q)^2 = \rho^2`; **analytic implicit** `x^2 + y^2 + Dx + Ey + F = 0`; parametric | |
| Units | lengths in **lu**, areas in **squ**, volumes in **cu** | geometry builders: `@with_units` |

## 5. Linear algebra (Proposed)

Matrices with capital letters `A, B` (not bold); entries `a_{ij}`; transpose `A^{T}`; inverse `A^{-1}`; determinant `\det A` (or `\lvert A \rvert` in a computation); identity `I_n`; rank `\operatorname{rank} A`; matrices shown with `\begin{pmatrix}`; eigenvalue `\lambda`, eigenvector `\vec v`.

## 6. Probability and statistics (Proposed)

`P(A)`, `P(A \mid B)`; random variables capital `X, Y`, values small `x`; `E(X)`, `\operatorname{Var}(X)`, `\sigma`; distributions `X \sim B(n, p)`, `\mathcal{P}(\lambda)`, `\mathcal{E}(\lambda)`, `\mathcal{N}(\mu, \sigma^2)`; standard normal function `\Phi(z)`; sample mean `\bar x`, sample variance `s^2`, correlation `r`; combinations `\binom{n}{k}`, arrangements `A_n^k` (one form per course, stated in the first lesson that uses it).

## 7. Language and naming (Rule)

- **Spelling: American English** (center, color, analyze). Today the content uses "center" 353 times and "centre" 26 times, and the interface has one "colour": the exceptions are corrected when the file is next touched, and new content uses American spelling only.
- **Titles in sentence case**: "Angle bisectors and the incenter", not "Angle Bisectors And The Incenter".
- **Exercise instructions** start with a verb in the imperative: Find, Compute, Show that, Prove that, Solve, Sketch, Determine. One verb for one kind of task across the platform ("Find" for a value, "Show that" for a given result, "Prove that" for a proof).
- **One name for one thing** in content, interface and documents: for example always "worked solution" (not "correction" or "answer explanation"), "unit test" (not "quiz" or "checkpoint"), "quick check", "final answer".
- **Short sentences**, no exclamation marks, no slang; the learner is addressed as "you".
- Interface texts live in `apps/web/src/i18n/en.json`; no text is written directly in the code.

## 8. Known inconsistencies to resolve (Decision needed)

| Topic | Today | Decision |
|---|---|---|
| Area of a triangle | the spec says `K` or `\mathcal A`; the lessons use `S` | **`S`** (as the lessons and the owner's notes); the spec is superseded |
| Circle equations | some lessons say "analytic (general) equation" for the expanded form | **canonical** and **analytic implicit**, as decided for the triangle toolkit; lessons updated when touched |
| Spelling | mostly American, some British | American (section 7) |
| Complement of an event | `\overline{A}` and `A^c` both appear | to choose with the lecturer |
| Hierarchy names | Course, Module, Unit, Lesson, Section | confirmed or changed at the owner's meeting (see [curriculum-structure.md](curriculum-structure.md)) |
