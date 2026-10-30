# The step-by-step solver

## 1. Principles (Rule)

1. **No AI.** The solver reads the problem with rules (a grammar plus the phrasing layer `allmaths_engine/solver/phrasing.py`), computes with SymPy, and explains with its own step builders. Nothing is guessed.
2. **Every answer is verified** by a second, independent computation (differentiate an antiderivative, substitute a solution, compare with SymPy's own result, check numerically at random points). An answer that cannot be verified is not shown.
3. **Refuse rather than guess.** When the problem cannot be read or solved, the solver says so, shows how to write the problem, and suggests the closest form it understands. A wrong answer is the worst possible outcome; an honest "not yet" is acceptable.
4. **Exact answers in the platform's notation** ([notation-and-naming.md](notation-and-naming.md)); steps written as in the lessons, each with a short reason.
5. **It says how it read the problem** when it rewrote the sentence ("I read 'derive sin x' as 'derivative of sin x'").
6. **Time limit** for every problem (worker processes in `solver_pool.py`); a problem that is too long to compute is refused with that reason.

## 2. What it solves today (current state)

Derivatives (with every rule shown), integrals (definite and indefinite), limits (with L'Hôpital), equations and systems, inequalities, ordinary differential equations (first order and linear constant coefficients), simplify / expand / factor, partial fractions, vectors (dot, cross, box, norm, angle, projection), matrices (determinant, inverse, eigenvalues, row reduction, products), multivariable calculus (partial derivatives, gradient, directional derivative, critical points, Lagrange multipliers, double, triple and line integrals), tangent lines and planes, Taylor series, sums, areas between curves; the triangle toolkit (a tab of the solver). See `docs/solver-and-premium.md` and `docs/triangle.md`.

## 3. Target coverage by level

The target is to solve **the computational questions of every module on the platform**, in the form in which they are written there, and the usual forms of the same questions in textbooks and exams.

| Level | Families to cover (Target) |
|---|---|
| `S` | arithmetic with fractions and radicals, algebraic expressions, linear and quadratic equations and inequalities, systems, functions (domain, variation, extremum), exponentials and logarithms, trigonometric equations, sequences (arithmetic, geometric), plane geometry computations, basic statistics |
| `U1`–`U2` | one- and several-variable calculus, series, vectors and analytic geometry (lines, planes, circles, spheres, conics, quadrics, the triangle and tetrahedron toolkits), linear algebra, ODEs (first order, linear, systems), complex numbers, probability distributions, descriptive and inferential statistics |
| `U3`–`U4` | Fourier series, Laplace transform, PDEs by separation of variables, numerical methods (with approximations when asked), complex analysis (residues, contour integrals), optimization, statistical tests |
| `M`, `D` | the computational parts of each module (transforms, special functions, eigenvalue problems, stochastic computations), decided module by module; proofs are out of scope for the solver |

## 4. How coverage is measured and grown (Rule)

1. **Coverage report.** Every exercise and worked example of the platform has a verified answer: it is the test set. A script feeds each one to the solver in its written form (the set instruction and the statement) and compares the solver's answer with the verified key. The report gives the percentage solved, by course, module and family, and the list of failures.
2. **Grow by family.** The largest family of failures is added next: reader rule, computation, steps, verification, tests. The coverage percentage must never go down (the report runs in the checks).
3. **Phrasing.** New ways of writing a problem are added to the phrasing layer with tests; the mathematics in the text is never changed.
4. **Every family ships with tests**: correct answers compared with independent computations, refused inputs, and the steps.
5. **New modules**: before a module is published, its computational exercises are run through the report; the gaps are listed in the module's definition of done ([curriculum-structure.md](curriculum-structure.md), section 9).

## 5. Input and output (Rule)

- The learner types in the same mathematical field as everywhere else ([math-input.md](math-input.md)), or in plain text; a picture of a printed problem is read on the device as a draft the learner checks.
- The answer is shown exactly, with the steps; the plain-text form of the answer is shown too (to be copied).
- The free plan has a daily limit; Premium has none (`docs/solver-and-premium.md`). The triangle toolkit and the graph tools are not counted against the limit.
