# Vision and scope

## What Allmaths is

A mathematics learning platform where a learner can study **alone**, from the first idea to the exam, with the same quality as a good university course: clear notes, worked examples, exercises with hints and worked solutions, tests, a step-by-step solver, a grapher, and progress that is measured honestly. It must be able to compete with the international platforms, and it must be **simple to use**.

## Levels covered (Rule)

The platform is built to hold about **100 modules**, from secondary school to doctorate:

| Level code | Level | Examples of content |
|---|---|---|
| `S` | Secondary school | numbers, algebra, equations, functions, trigonometry, plane geometry, sequences, introductory calculus, statistics |
| `U1`, `U2` | First and second year of university | calculus of one and several variables, linear algebra, vectors and analytic geometry, ordinary differential equations, probability, statistics |
| `U3`, `U4` | Third and fourth year | real and complex analysis, partial differential equations, numerical methods, abstract algebra, topology, mathematical statistics, optimization |
| `M` | Master's | functional analysis, measure theory, advanced PDE, stochastic processes, advanced statistics, specialized courses |
| `D` | Doctorate | research-level topics chosen with the lecturers |

What exists today: Geometry (vectors, plane, space), Multivariable Calculus and Differential Equations, Probability and Statistics: 109 lessons, levels `U1` to `U2`.

## Principles that are never traded away (Rule)

1. **Correct mathematics first.** Every answer key, every worked result and every solver answer is computed and checked by the math engine. Nothing is hard-coded without verification.
2. **Exact values.** Fractions, simplified radicals, π, e. A decimal only when the question asks for an approximation.
3. **One notation, one structure, one style** for the whole platform ([notation-and-naming.md](notation-and-naming.md), [curriculum-structure.md](curriculum-structure.md)). A learner who knows one lesson knows how every lesson works.
4. **No AI in the answers.** The solver, the answer checking and the grapher are rule-based and verified; nothing is guessed. When the platform cannot do something, it says so clearly.
5. **Honest progress.** Percentages are computed on the server from what the learner did, exactly, and explained publicly.
6. **Self-study first.** Everything must be understandable without a teacher: prerequisites linked, every step explained, every exercise with hints, a worked solution and its final answer.
7. **Simple and professional.** Few, clear pages; no clutter; accessible on a phone with a slow connection.
8. **Every feature ships with tests**, and the checks are green before anything is published.

## How correctness is ensured at higher levels (Rule)

The math engine (SymPy) proves computations: derivatives, integrals, limits, equations, matrices, series, exact values, probabilities. It does **not** prove theorems. Therefore:

- Computational content (answers, worked examples, exercises with a value as answer) is verified by the engine, as today.
- Proofs, definitions and theory at `U3` and above are **reviewed by a qualified person** (the lecturer or a reviewer named on the team page) before publication. Each such lesson records its reviewer in its metadata (Proposed: a `reviewedBy` field).
- Exercises whose answer is a proof are marked as such; they have a model proof and a self-check list instead of an automatic check.
- Doctoral content is written with the lecturers; the platform provides the structure, the notation, the computation checks and the tools, not the research judgement.

## What comes later (Target)

- **Certification**: certificates for modules or courses, with question pools, identity checks and exam rules. Not designed yet; nothing in the current work may make it harder (for example: keep every attempt and score on the server, keep tests drawn from verified pools).
- More languages for the interface (the text system is ready: `apps/web/src/i18n`).
- Instructors and classes, as in the original specification (section 3.2).
