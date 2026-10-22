# Math Learning Platform: Full Build Specification

**Working name:** Allmaths
**Document type:** Master instructions for an AI coding agent (Claude Code)
**Version:** 1.2, October 2026 (adds the Course → Module → Unit → Lesson hierarchy, conics, polyhedra and PDE; Phase 1 decisions recorded in `docs/architecture.md`)

---

## 0. How to Use This Document

This file is the single source of truth for building the platform. Give it to Claude Code at the start of the project and keep it in the repository root.

### 0.1 The prompt to give Claude Code first

Copy this exactly as your first message to Claude Code, with this file in the project folder:

```text
Read MATH_PLATFORM_BUILD_SPEC.md completely before writing any code.
It is the full specification for a university-level mathematics learning
platform. Do not try to build everything at once.

1. Summarize the specification back to me in under 40 lines so I can
   confirm you understood it.
2. Create CLAUDE.md from Section 17 of the spec.
3. Propose the repository structure (Section 5.3) and wait for my approval.
4. Then build Phase 1 only (Section 16). Write tests for everything.
   Stop at the end of Phase 1 and show me how to run and check it.

Rules you must follow throughout:
- Mathematical correctness is the top priority. Every answer, worked
  example and solution must be verified by the math engine (Section 7).
- All values are exact: fractions, radicals and π. Never decimals unless
  a question explicitly asks for a decimal approximation.
- Follow the notation standard in Section 6 exactly.
- Never mark a phase complete until its acceptance criteria pass.
```

### 0.2 Prompts for the following phases

At the start of each later phase, send:

```text
Re-read MATH_PLATFORM_BUILD_SPEC.md and CLAUDE.md. Build Phase N
(Section 16). Before coding, list the tasks you will do and the acceptance
criteria you will test against. Stop at the end of the phase.
```

### 0.3 Working rules for you, the owner

- Build in phases. One phase at a time, tested, then the next.
- Review every phase yourself: click through it as a student would.
- Keep this file updated. If you change a rule, change it here first, then tell Claude Code.
- Never publish content that has not passed the verification pipeline (Section 7.4).

---

## 1. Product Vision

A complete online learning platform for university mathematics, comparable in structure and quality to Coursera, edX, Cisco NetAcad and Khan Academy, specialized for:

1. **Geometry**: vectors and analytic geometry of the plane and of space (Course 1)
2. **Multivariable Calculus and Differential Equations**: derivatives, double and triple integrals, ODE, PDE (Course 2)
3. Later: **Probability and Statistics** (Course 3)

Content is organized as Course → Module → Unit → Lesson (Section 2.1).

The platform must:

- Teach from the very first concept up to full university exam level, in a fixed, logical order.
- Track exactly where every student is: every section read, every problem attempted, every answer, every minute.
- Show progress that moves continuously as the student works, not only at the end of a lesson.
- Generate unlimited practice through parameterized problems with exact answers.
- Check answers mathematically (equivalent forms accepted), not by string matching.
- Be beautiful, calm and engaging: professional animations, interactive 2D/3D graphics, no clutter.
- Earn money through subscriptions and course purchases, with local payment methods.
- Be reliable: tested, monitored, backed up, secure.

### 1.1 Target users

| Role | Description |
|---|---|
| **Student** | University students (first and second year), exam candidates, self-learners |
| **Instructor** | Lecturers or tutors who create classes, assign work and view class analytics |
| **Content author** | Writes and edits lessons and problems; content goes through review |
| **Reviewer** | Mathematically checks content before publication |
| **Admin** | Manages users, payments, courses, settings and reports |

---

## 2. Curriculum: Exact Order and Scope

### 2.1 Hierarchy

```text
Course  →  Module  →  Unit  →  Lesson  →  Section (block)
```

- **Course**: a sellable product (Section 4). Has a code used in ids: `geo`, `mvc`, `stat`.
- **Module**: a major theme of a course. Has a module test.
- **Unit**: a group of closely related lessons inside a module. Has a unit checkpoint quiz (optional, ungraded toward the certificate).
- **Lesson**: 20–40 minutes of study. Has sections, practice problems and a graded quiz. Four difficulty tiers (Section 8.2).

Ids are stable and human-readable: `geo-m01-u01-l01` (course, module, unit, lesson). Order inside every level is fixed. A lesson is only listed under one unit.

### 2.2 Course 1: Geometry (code `geo`)

Vectors, then plane geometry, then space geometry. Everything in Course 2 depends on it.

#### Module 1: Vectors (free)

**Unit 1: Vectors and their algebra**

1. Points, coordinates, the vector \(\overrightarrow{AB}\), equality of vectors, free vectors
2. Operations: addition (triangle and parallelogram rules), scalar multiplication, linear combinations
3. Collinear vectors; linear dependence and independence; bases of \(\mathbb{R}^2\) and \(\mathbb{R}^3\)
4. Norm \(\|\vec u\|\), unit vectors \(\hat u\), direction cosines

**Unit 2: Products of vectors**

1. Dot (scalar) product \(\langle \vec u, \vec v\rangle\): definition, properties, angle, orthogonality
2. Orthogonal projection, components, the Cauchy–Schwarz and triangle inequalities
3. Cross (vector) product \([\vec u, \vec v]\): definition by determinant, properties, right-hand rule
4. Area of a parallelogram and of a triangle
5. Box (mixed, scalar triple) product \(\langle \vec u, \vec v, \vec w\rangle\): volume, orientation, coplanarity
6. Volume of a parallelepiped and of a tetrahedron
7. Double cross product: \([\vec u, [\vec v, \vec w]] = \vec v\langle\vec u,\vec w\rangle - \vec w\langle\vec u,\vec v\rangle\)

#### Module 2: Geometry of the plane (2D)

**Unit 1: Coordinates and the straight line**

1. Cartesian coordinates, distance formula, midpoint, section formula (internal and external division)
2. Polar coordinates \((r, \theta)\), principal value, multiple representations of one point; conversion polar ↔ Cartesian with quadrant handling
3. Conversion of curves: lines, circles, cardioids, roses, lemniscates, spirals; distance between two points in polar form; area \(\tfrac12\int r^2\,d\theta\) (preview, completed in Course 2)
4. Change of axes: translation and rotation
5. The straight line: all forms (vector, parametric, Cartesian, slope-intercept, intercept, normal form)
6. Angle between two lines; parallel and perpendicular conditions
7. Distance point–point, point–line, line–line (parallel lines)
8. Intersection of lines; concurrent lines; pencils of lines

**Unit 2: The triangle**

1. Perimeter, area (determinant and Heron), centroid, orthocenter
2. Incircle: incenter, inradius \(r = \tfrac{K}{s}\), equation of the incircle; excircles
3. Circumcircle: circumcenter, circumradius \(R = \tfrac{abc}{4K}\), equation of the circumcircle

**Unit 3: The circle and conics**

1. Circle: standard and general equations, circle through three points, circumference and area
2. Line–circle position; tangent at a point; tangents from an external point; power of a point
3. Two circles: relative position, radical axis, orthogonal circles
4. Loci problems
5. Second-order curves (conics): parabola, ellipse, hyperbola; canonical equations, foci, eccentricity, tangents
6. General second-degree equation: classification and reduction to canonical form

#### Module 3: Geometry of space (3D)

**Unit 1: Points, lines and planes**

1. Points and distance in space; midpoint; division
2. The line in space: vector, parametric and symmetric equations
3. The plane: point–normal, general, parametric, intercept forms; plane through three points
4. Relative positions: line–line (parallel, intersecting, skew), line–plane, plane–plane
5. Angles: line–line, line–plane, plane–plane
6. Distances: point–plane, point–line, between parallel planes, between skew lines; common perpendicular
7. Projections of points and lines onto planes; symmetric points

**Unit 2: The tetrahedron and polyhedra**

1. The tetrahedron: volume, face areas, total surface area, heights, centroid
2. The regular tetrahedron and the other Platonic solids: faces, edges, vertices, Euler's formula, volume, surface area
3. Prisms and pyramids: volume and surface area, section by a plane

**Unit 3: The sphere and quadric surfaces**

1. The sphere: equation, center and radius from the general form, surface area and volume
2. Sphere–plane: tangent plane, intersection circle (center and radius); sphere–line; two spheres
3. Quadric surfaces: ellipsoid, paraboloids, hyperboloids, cones, cylinders; canonical equations and traces

### 2.3 Course 2: Multivariable Calculus and Differential Equations (code `mvc`)

Prerequisite: Course 1, Modules 1–3 (or a passed placement test).

#### Module 1: Derivatives of several variables

**Unit 1: Functions of several variables**

1. Functions of two and three variables: domain, range, graphs, level curves and level surfaces
2. Limits and continuity in two variables; path tests for non-existence

**Unit 2: Partial differentiation**

1. Partial derivatives (2 and 3 variables), geometric meaning
2. Higher-order partial derivatives; Schwarz/Clairaut theorem
3. Differentiability, total differential \(df\), linear approximation and error estimation
4. Chain rule (all cases), tree diagrams, implicit differentiation

**Unit 3: Gradient and tangent planes**

1. Gradient \(\nabla f\), directional derivative \(D_{\vec u}f\), steepest ascent
2. **Tangent plane to a surface (TpS)** and **normal line to a surface (NpS)**, for \(F(x,y,z)=0\) and for \(z=f(x,y)\)
3. Taylor polynomial of order 2 in two variables

**Unit 4: Optimization**

1. Critical points; Hessian; second derivative test; saddle points
2. Absolute extrema on closed bounded regions
3. Constrained optimization: Lagrange multipliers (one and two constraints)
4. Applications: optimization in geometry, economics and physics

#### Module 2: Double integrals

**Unit 1: Double integrals over regions**

1. Double integrals over rectangles; Fubini's theorem
2. Double integrals over general regions (type I and type II); sketching regions
3. Changing the order of integration

**Unit 2: Polar coordinates and change of variables**

1. Double integrals in polar coordinates
2. General change of variables in the plane; the Jacobian

**Unit 3: Applications of double integrals**

1. Area and volume
2. Mass, center of mass, moments of inertia, average value
3. Surface area of a graph \(z=f(x,y)\)

#### Module 3: Triple integrals

**Unit 1: Triple integrals in Cartesian coordinates**

1. Triple integrals over boxes and general solids; describing a solid by inequalities
2. Iterated triple integrals and changing the order of integration

**Unit 2: Cylindrical and spherical coordinates**

1. Triple integrals in cylindrical coordinates
2. Triple integrals in spherical coordinates
3. Choosing the best coordinate system

**Unit 3: Change of variables and applications**

1. General change of variables in space; the Jacobian determinant
2. Applications: volume, mass, centroid and moments of solids

#### Module 4: Ordinary differential equations (ODE)

**Unit 1: First-order equations**

1. Vocabulary: order, degree, linear vs non-linear, solution, general and particular solution, IVP
2. Separable equations
3. Homogeneous equations \(y' = F(y/x)\)
4. Linear equations, integrating factor
5. Exact equations and integrating factors for non-exact equations
6. Bernoulli equations
7. Applications: growth and decay, Newton's cooling, mixing, RC circuits

**Unit 2: Second-order equations**

1. Linear homogeneous with constant coefficients (3 cases)
2. Non-homogeneous: undetermined coefficients (including resonance)
3. Non-homogeneous: variation of parameters
4. Cauchy–Euler equations

**Unit 3: Applications, systems and Laplace transforms**

1. Applications: spring–mass systems, RLC circuits
2. Introduction to systems of linear differential equations
3. Laplace transform method (advanced)

#### Module 5: Partial differential equations (PDE) (advanced; written last)

**Unit 1: Introduction and first-order PDE**

1. Vocabulary: order, linearity, classification, solutions and boundary conditions
2. First-order linear PDE: method of characteristics

**Unit 2: Separation of variables**

1. The heat equation on a rod
2. The wave equation (vibrating string)
3. Laplace's equation on a rectangle

**Unit 3: Fourier series**

1. Fourier series: coefficients, even and odd functions, convergence
2. Fourier series in the solution of the heat and wave equations

### 2.4 Course 3 (later phase): Probability and Statistics (code `stat`)

Counting, probability axioms, conditional probability and Bayes, random variables, discrete and continuous distributions, expectation and variance, joint distributions, central limit theorem, estimation, confidence intervals, hypothesis testing, regression. Same platform features apply. Its modules and units are defined when Phase 6 starts.

### 2.5 Reference material

The owner's lecture notes and textbooks (folder "Multivariable Calculus and Differential Equations" on the owner's Desktop) are **reference only**: they set the level, order and style (university syllabus MATH8213). All platform content must be **original** (Section 12.2, copyright rule).

---

## 3. Feature Specification

### 3.1 Student features

- **Account**: sign up (email, Google), email verification, password reset, profile, preferred language.
- **Course catalog**: courses, modules, units, lessons, prerequisites, duration estimates, price.
- **Learning path**: fixed order with optional "test out" quizzes to skip mastered lessons.
- **Lesson player** (Section 3.3).
- **Practice center**: unlimited generated problems per skill, filtered by topic and difficulty.
- **Assessments**: lesson quizzes, module tests, timed mock exams, final exam.
- **Hints**: up to three progressive hints per problem; using hints is tracked and reduces points.
- **Step-by-step solutions**: revealed after an attempt or after giving up.
- **Mistake notebook**: every wrongly answered problem saved automatically for review.
- **Spaced review**: missed skills come back after 1, 3, 7 and 21 days.
- **Bookmarks and personal notes** on any lesson section.
- **Q&A forum per lesson**: ask questions, answers from instructors and other students, upvotes, "accepted answer", math rendering in posts.
- **Dashboard** (Section 9.5).
- **Certificates**: PDF, unique ID, public verification page, QR code.
- **Streaks and goals**: daily goal in minutes, streak counter. Keep it professional, not childish.
- **Offline-friendly**: lesson text cached for poor connections.

### 3.2 Instructor features

- Create classes with join codes; enroll students.
- Assign lessons, quizzes and exams with due dates.
- Class gradebook: per student, per lesson, per skill.
- Analytics: hardest problems, common wrong answers, time on task, students at risk.
- Export grades as CSV and Excel.
- Answer forum questions; mark answers as verified.

### 3.3 Lesson player

Each lesson is a sequence of **sections**. Each section is one of these blocks:

| Block | Purpose |
|---|---|
| `concept` | Short explanation with math, max ~250 words |
| `definition` | Formal definition box |
| `theorem` | Theorem box, optional proof (collapsible) |
| `formula` | Key formula box, "add to formula sheet" button |
| `example` | Worked example, revealed step by step |
| `visual` | Interactive 2D/3D graph (Section 10.3) |
| `check` | One quick question that must be answered to continue |
| `practice` | Set of generated problems |
| `summary` | Key points of the lesson |
| `quiz` | Graded lesson quiz |

Rules:

- A progress bar at the top of the lesson moves as each section is completed.
- A section counts as completed when the student scrolls through it and stays at least a minimum time (configurable, default 20 seconds for concept blocks), or answers its `check`.
- The student can always go back. Forward navigation may be locked behind `check` blocks (configurable per course).
- "Resume where I left off" returns to the exact section.

### 3.4 Admin features

- Users, roles and permissions; suspend and delete accounts (GDPR-style data export and deletion).
- Courses, pricing, coupons, free trials.
- Content workflow: draft → in review → verified → published → archived, with version history.
- Payment and subscription reports, refunds.
- Platform health dashboard.
- Audit log of all admin actions.

---

## 4. Monetization

- **Free tier**: Geometry, Module 1 (Vectors) completely free; the first unit of every other module free.
- **Subscription**: monthly and yearly, all courses.
- **Single course purchase**: lifetime access to one course.
- **Exam prep packs**: timed mock exams with full solutions, sold separately.
- **Institution licenses**: universities buy seats for a class.
- **Payments**: Stripe (cards) and mobile money (MTN MoMo, Airtel Money via Flutterwave or a similar aggregator). Prices shown in local currency (RWF) and USD.
- Webhooks update access immediately after payment; failed payments retry; receipts are emailed.
- Never store card numbers. All payment data stays with the provider.

---

## 5. Architecture

### 5.1 Technology stack (recommended)

| Layer | Choice |
|---|---|
| Frontend | Next.js (App Router), React, TypeScript (strict) |
| Styling | Tailwind CSS with a design-token file |
| Animation | Framer Motion; respects `prefers-reduced-motion` |
| Math rendering | KaTeX (server-side rendering where possible) |
| Math input | MathLive (visual math keyboard for answers) |
| 2D graphs | JSXGraph or Mafs |
| 3D graphs | Three.js via React Three Fiber |
| Backend API | Next.js route handlers, or a separate Node service for heavy jobs |
| Math engine | Python service with SymPy (FastAPI), Section 7 |
| Database | PostgreSQL (with Prisma or Drizzle ORM) |
| Cache / queues | Redis (sessions, rate limits, background jobs) |
| Auth | Auth.js or Clerk; role-based access control |
| Payments | Stripe + Flutterwave |
| Files | S3-compatible object storage (images, certificate PDFs) |
| Email | Resend or Postmark |
| Search | PostgreSQL full-text search (later: Meilisearch) |
| Testing | Vitest, Playwright (end-to-end), Pytest (math engine) |
| Monitoring | Sentry (errors), uptime monitoring, structured logs |
| Deployment | Vercel (web) + Railway/Fly.io/Render (math engine, database), or one VPS with Docker |
| CI/CD | GitHub Actions: lint, type-check, tests, content verification, deploy |

### 5.2 System diagram

```text
 Browser (Next.js app)
   │  lessons, answers, progress events
   ▼
 Web/API layer (Next.js) ──── Auth ──── Payments (Stripe / Flutterwave webhooks)
   │            │
   │            └── Redis (sessions, queues, rate limits)
   ▼
 PostgreSQL (users, content, attempts, events, progress)
   ▲
   │  verify answers, generate problems, check content
 Math Engine (Python + SymPy, internal only, never public)
```

### 5.3 Repository structure (monorepo)

```text
/apps
  /web              Next.js app (student, instructor, admin)
  /math-engine      FastAPI + SymPy service
/packages
  /ui               Shared components, design tokens, animations
  /notation         Notation rules and LaTeX macros (Section 6)
  /content-schema   Zod schemas for lessons and problems; content loader and verification
  /core             Pure logic shared by browser and server: exact progress formulas, event schema, engine client
  /server           Business rules: auth, sessions, content sync, events, progress, checks
  /db               Database schema and migrations
/content
  /geo                         Course 1: Geometry
    course.yaml
    /m01-vectors
      module.yaml
      /u01-vectors-and-algebra
        unit.yaml
        /l01-points-and-vectors
          lesson.yaml
          problems.yaml
  /mvc                         Course 2: Multivariable Calculus and DE
/scripts            verify-content, seed, import tools
/docs               Architecture decisions, runbooks
CLAUDE.md
MATH_PLATFORM_BUILD_SPEC.md
```

### 5.4 Engineering principles

- TypeScript strict mode; no `any`.
- Every database change through a migration.
- All input validated (Zod on the web side, Pydantic in the math engine).
- Business rules in one place (services), not scattered in UI components.
- Idempotent event ingestion (duplicate events never double-count progress).
- Feature flags for unfinished features.
- Accessibility: WCAG 2.1 AA; keyboard navigation; screen-reader text for math (KaTeX/MathML).
- Internationalization ready: English first; French and Kinyarwanda later. No hard-coded UI strings.

---

## 6. Mathematical Notation Standard (mandatory)

All notation is defined once in `/packages/notation` as LaTeX macros. Content authors and the AI must use the macros, never raw ad-hoc notation. This allows a notation change in one place.

### 6.1 Vectors

| Concept | Required notation | LaTeX macro |
|---|---|---|
| Vector | \(\vec u,\ \vec v,\ \vec w\) (arrow on top, always) | `\vec{u}` |
| Vector between points | \(\overrightarrow{AB}\) | `\overrightarrow{AB}` |
| Components | \(\vec u = (u_1, u_2, u_3)\) or column form | |
| Basis vectors | \(\vec i,\ \vec j,\ \vec k\) | `\vec{i}` |
| Zero vector | \(\vec 0\) | `\vec{0}` |
| Norm (length) | \(\|\vec u\|\) | `\norm{\vec u}` |
| Unit vector | \(\hat u = \dfrac{\vec u}{\|\vec u\|}\) | `\unit{u}` |
| **Dot product** | \(\langle \vec u, \vec v\rangle\) | `\dotp{\vec u}{\vec v}` |
| **Cross product** | \([\vec u, \vec v]\) | `\crossp{\vec u}{\vec v}` |
| **Box product** | \(\langle \vec u, \vec v, \vec w\rangle\) | `\boxp{\vec u}{\vec v}{\vec w}` |
| Angle between vectors | \(\widehat{(\vec u, \vec v)}\) or \(\theta\) | |
| Projection | \(\operatorname{proj}_{\vec v}\vec u\) | `\proj{\vec v}{\vec u}` |

Never write a vector as plain `u` or bold `u` in student-facing content.

> Note for Claude Code: \([\vec u,\vec v]\) for the cross product and \(\langle\vec u,\vec v,\vec w\rangle\) for the box product are this course's convention. Many textbooks use \(\vec u\times\vec v\) and \([\vec u,\vec v,\vec w]\) instead. Implement the macros so the convention can be switched globally, and show a small "other notations you may see" note once in each relevant lesson.

### 6.2 Geometry

- Points: capital letters \(A, B, C\); coordinates \(A(x_A, y_A, z_A)\).
- Lines: \((D)\), \((\Delta)\) or \(\ell\); planes: \((P)\), \(\Pi\).
- Distance: \(d(A, B)\), \(d(A, (D))\), \(d(A, \Pi)\).
- Triangle sides \(a, b, c\) opposite \(A, B, C\); semi-perimeter \(s\); area \(K\) (or \(\mathcal A\)); inradius \(r\); circumradius \(R\); incenter \(I\); circumcenter \(O\); centroid \(G\).

### 6.3 Calculus and differential equations

- Partial derivatives: \(\dfrac{\partial f}{\partial x}\) and \(f_x\); mixed \(\dfrac{\partial^2 f}{\partial x\,\partial y}\).
- Gradient \(\nabla f\); directional derivative \(D_{\vec u} f\); Hessian \(H_f\); Jacobian \(\dfrac{\partial(x,y)}{\partial(u,v)}\).
- Integrals always show the differential: \(\iint_D f\,dA\), \(\iiint_E f\,dV\), with limits on iterated integrals.
- ODEs: \(y',\ y''\) or \(\dfrac{dy}{dx}\); constants \(C_1, C_2\); IVP conditions written explicitly.

### 6.4 Exact values rule (critical)

1. **No decimals.** Answers are exact: \(\tfrac{7}{2}\), not 3.5; \(\tfrac{19\sqrt{35}}{35}\), not 3.211.
2. Fractions fully reduced; use `\dfrac` in display.
3. Radicals simplified (\(2\sqrt3\), not \(\sqrt{12}\)); denominators rationalized.
4. Keep \(\pi\), \(e\), \(\ln 2\) symbolic.
5. Angles in radians as exact multiples of \(\pi\) (\(\tfrac{\pi}{3}\)), or exact degrees when the question uses degrees. When an angle is not a standard angle, write \(\theta = \arccos\left(-\tfrac{4\sqrt6}{21}\right)\).
6. A decimal appears **only** when a question explicitly asks for an approximation ("to 3 significant figures"), and then the exact value is shown first.
7. Students may type answers in any equivalent exact form; the engine accepts them (Section 7.2). Decimal input is rejected with a friendly message asking for an exact value, unless the question asks for an approximation.

---

## 7. Math Engine and Correctness Guarantee

This is the most important part of the system. The goal is **zero mathematical errors**.

### 7.1 Responsibilities

The math engine (Python + SymPy, internal API) does four jobs:

1. **Verify content**: recompute every answer, example and solution step in the content files.
2. **Check student answers**: decide whether a student's input is mathematically equivalent to the correct answer.
3. **Generate problems**: create random instances of parameterized problem templates with exact answers.
4. **Render**: return canonical LaTeX for answers and steps.

### 7.2 Answer checking rules

| Answer type | Check method |
|---|---|
| Number | Exact symbolic equality: `simplify(student - correct) == 0` |
| Expression | Symbolic simplification, plus random numeric testing at 20 points as a second check |
| Vector / point | Component-wise exact equality |
| Equation (line, plane, circle, sphere) | Equivalent up to a non-zero constant multiple (for line/plane) or expanded equality (for circles and spheres) |
| Set of points / solutions | Unordered set comparison |
| ODE general solution | Substitute into the equation **and** check the number of independent constants; accept any equivalent form (e.g. \(C_1\cos 3x + C_2\sin 3x\) and \(A\sin(3x+\varphi)\)) |
| Interval / inequality | Normalized set comparison |
| Multiple choice | Index comparison |
| Multi-part | Each part checked separately; partial credit |

Feedback must recognize **common mistakes** (configured per problem): sign errors, forgetting the \(r\) in polar \(dA\), wrong quadrant in \(\theta\), forgetting the \(\tfrac16\) for a tetrahedron, etc. Each common mistake has a specific hint.

### 7.3 Parameterized problem templates

Every problem is a template, not a fixed question:

```yaml
id: geo-m03-u01-l06-skew-lines-distance
skill: distance-between-skew-lines
difficulty: 3          # 1 to 4, Section 8.2
params:
  P1: random_int_vector(-3, 3)
  d1: random_int_vector(-3, 3, nonzero=true)
  P2: random_int_vector(-3, 3)
  d2: random_int_vector(-3, 3, nonzero=true)
constraints:
  - cross(d1, d2) != 0                       # not parallel
  - dot(P2 - P1, cross(d1, d2)) != 0          # truly skew, not intersecting
statement: >
  Find the distance between the lines
  (D_1): \vec r = {P1} + t{d1} and (D_2): \vec r = {P2} + s{d2}.
answer: abs(dot(P2 - P1, cross(d1, d2))) / norm(cross(d1, d2))
answer_type: number
solution_steps:
  - "Compute [\\vec d_1, \\vec d_2] = {cross(d1, d2)}"
  - "Compute \\overrightarrow{P_1P_2} = {P2 - P1}"
  - "d = \\dfrac{|\\langle \\overrightarrow{P_1P_2}, [\\vec d_1, \\vec d_2]\\rangle|}{\\|[\\vec d_1, \\vec d_2]\\|} = {answer}"
common_mistakes:
  - expr: dot(P2 - P1, cross(d1, d2)) / norm(cross(d1, d2))
    hint: "A distance is never negative. Did you forget the absolute value?"
hints:
  - "The common perpendicular has direction [\\vec d_1, \\vec d_2]."
  - "Project \\overrightarrow{P_1P_2} onto that direction."
```

Rules:

- Constraints prevent degenerate cases (parallel lines, zero vectors, division by zero).
- The generator rejects instances whose answers are "ugly" beyond a configured complexity, unless the template allows it.
- Each generated instance is stored with its seed, so any attempt can be reproduced exactly.

### 7.4 Content verification pipeline

Run automatically in CI on every content change, and nothing is published unless it passes:

1. Schema validation of every lesson and problem file.
2. Every template generates 200 instances; every instance is solved and checked; constraints never violated.
3. Every worked example's stated result is recomputed by SymPy and must match.
4. Every multiple-choice question: exactly one option equals the answer; distractors are all different from the answer and from each other.
5. Every LaTeX string compiles in KaTeX.
6. Notation lint: flags `\cdot` between vectors, `\times` between vectors, plain-letter vectors, decimals in answers, unrationalized denominators.
7. Human review: a reviewer must approve before status becomes `published`.

### 7.5 Answer key examples (for testing the engine)

These are verified and must be used as engine unit tests:

| # | Problem | Exact answer |
|---|---|---|
| 1 | \(\vec u=(2,-1,3),\ \vec v=(1,4,-2),\ \vec w=(0,1,1)\). Find \(\langle\vec u,\vec v\rangle\), \([\vec u,\vec v]\), \(\langle\vec u,\vec v,\vec w\rangle\), \(\cos\theta\). | \(-8\); \((-10, 7, 9)\); \(16\); \(\cos\theta = -\tfrac{4\sqrt6}{21}\) |
| 2 | Distance between \((D_1): (1,0,-1)+t(1,2,-1)\) and \((D_2): (0,1,2)+s(2,-1,1)\) | \(\tfrac{19\sqrt{35}}{35}\) |
| 3 | Tetrahedron \(A(1,0,2), B(3,1,0), C(0,2,1), D(2,-1,3)\): volume, area of \(ABC\), height from \(D\) | \(V=\tfrac23\); \(\tfrac{5\sqrt2}{2}\); \(h=\tfrac{2\sqrt2}{5}\) |
| 4 | Triangle \(A(-1,0), B(5,0), C(2,4)\): area, incircle, circumcircle | \(K=12\); \((x-2)^2+(y-\tfrac32)^2=\tfrac94\); \((x-2)^2+(y-\tfrac78)^2=\tfrac{625}{64}\) |
| 5 | Distance from \(P(3,-1,2)\) to the line \((1,1,0)+t(2,-1,2)\) | \(\tfrac{2\sqrt2}{3}\) |
| 6 | Classify critical points of \(f=x^3-3x+y^3-12y\) | min at \((1,2)\), \(f=-18\); max at \((-1,-2)\), \(f=18\); saddles at \((1,-2)\) and \((-1,2)\) |
| 7 | Max of \(x+2y+2z\) on \(x^2+y^2+z^2=9\) | \(9\) at \((1,2,2)\) |
| 8 | \(z = xe^y\) at \((2,0,2)\): TpS and NpS | TpS: \(z = x + 2y\); NpS: \(\tfrac{x-2}{1}=\tfrac{y}{2}=\tfrac{z-2}{-1}\) |
| 9 | \(\displaystyle\int_0^1\!\!\int_{\sqrt y}^1 \sqrt{x^3+1}\,dx\,dy\) (reverse the order) | \(\tfrac{4\sqrt2-2}{9}\) |
| 10 | Volume inside \(\rho \le 2\) and above the cone \(\varphi=\tfrac{\pi}{3}\) | \(\tfrac{8\pi}{3}\) |
| 11 | Area inside the cardioid \(r = 1+\cos\theta\) | \(\tfrac{3\pi}{2}\) |
| 12 | \(y'' + 4y = \sin 2x\) (resonance) | \(y = C_1\cos2x + C_2\sin2x - \tfrac{x}{4}\cos 2x\) |
| 13 | \((2xy+3)\,dx + (x^2-1)\,dy = 0\) | exact; \(x^2y + 3x - y = C\) |

---

## 8. Assessment System

### 8.1 Assessment types

| Type | Where | Graded | Settings |
|---|---|---|---|
| Check question | Inside lesson | No (must answer) | Unlimited tries |
| Practice set | Lesson / practice center | Mastery only | Unlimited, generated |
| Lesson quiz | End of lesson | Yes | 5–8 questions, pass 70%, retakes get new instances |
| Module test | End of module | Yes | 15–25 questions, 60–90 min, pass 70%, 3 attempts |
| Mock exam | Exam prep | Yes | Full university-style paper, timed, worked solutions after |
| Final exam | End of course | Yes | Timed, proctoring-light (tab-switch logging), certificate requirement |

### 8.2 Difficulty tiers

Every lesson has problems in all four tiers. Quizzes and tests must include tiers 3 and 4.

| Tier | Name | Example (Geometry, Module 3) |
|---|---|---|
| 1 | Foundation | Write the equation of the plane with normal \(\vec n=(1,2,-1)\) through \(A(0,1,2)\) |
| 2 | Standard | Distance from a point to a plane |
| 3 | University | Distance between skew lines and the equation of their common perpendicular |
| 4 | Exam / challenge | Find the sphere tangent to two given planes with center on a given line; multi-step, several concepts |

### 8.3 Question formats

Multiple choice, multiple select, exact numeric input, expression input (MathLive keyboard), vector/point input, equation input, matching, ordering steps of a proof, drag points on a graph, multi-part problems with partial credit, and written solutions (uploaded photo or typed) graded by instructors.

### 8.4 Scoring

- Points per question set by difficulty: tier 1 = 1, tier 2 = 2, tier 3 = 3, tier 4 = 5.
- Hints reduce the points of that question by 25% each (minimum 25% of points).
- Partial credit for multi-part questions.
- Best score is recorded; all attempts are kept.
- Timed exams auto-submit at the end of time; work in progress autosaves every 10 seconds.

---

## 9. Progress Tracking and Analytics

The platform must know at every moment exactly what each student has done. Progress must **move continuously**: after every section, every problem and every quiz.

### 9.1 Event tracking

Every learning action is recorded as an event (inspired by the xAPI standard):

```text
event_id (UUID, generated on client, used for deduplication)
user_id, course_id, module_id, unit_id, lesson_id, section_id, problem_instance_id
verb: started | viewed | completed | attempted | answered | hinted |
      revealed_solution | passed | failed | bookmarked | resumed
result: { correct, score, max_score, answer_latex, duration_ms }
timestamp (server time), client_timestamp, device
```

Events are sent in batches every few seconds and on page exit (`navigator.sendBeacon`). They are stored permanently.

### 9.2 Progress formulas

All percentages are computed on the server from events, never trusted from the client.

**Section progress** \(\in \{0, 1\}\): completed when viewed for the minimum time or its check is answered.

**Lesson progress**
\[
P_{\text{lesson}} = 0.40\cdot\frac{\text{sections completed}}{\text{total sections}} + 0.20\cdot\frac{\text{practice problems solved (max 10)}}{10} + 0.40\cdot\mathbb 1[\text{quiz passed}]
\]

**Unit progress** is the time-weighted average of its lessons' progress (weights = estimated lesson minutes).

**Module progress**
\[
P_{\text{module}} = 0.80\cdot\frac{\sum_u w_u\,P_u}{\sum_u w_u} + 0.20\cdot\mathbb 1[\text{module test passed}]
\]
where \(w_u\) is the sum of the estimated minutes of the lessons of unit \(u\).

**Course progress** is the time-weighted average of module progress (weights = estimated minutes of the module).

All results are exact rational numbers computed in integer arithmetic and displayed as whole percentages (rounded down), so 100% is shown only when everything is truly complete.

**Components a lesson does not have yet.** The lesson formula is applied to the components the lesson actually has. A lesson without a practice set or quiz (all Phase 1 lessons) drops those weights, so reading and answering everything gives 100%. When Phase 2 adds them, the full formula applies.

**Time credit.** The browser reports active seconds per section, but the server credits at most the real time elapsed on its own clock since the section was opened or last credited, so the same time can never be credited twice. Only `started`, `viewed`, `resumed` and `bookmarked` are accepted from the browser; answers, hints and passes are recorded by the server.

The UI updates the progress ring and bars immediately (optimistic update), then reconciles with the server value.

### 9.3 Skill mastery

Each problem template is tagged with one or more skills (e.g. `cross-product-compute`, `tps-implicit-surface`). For each student and skill, a mastery value \(m \in [0,1]\) is updated after every attempt using Bayesian Knowledge Tracing (or a simpler Elo-style rating as a first version):

- Mastery levels: Not started (no attempts), Familiar (\(m \ge 0.4\)), Proficient (\(m \ge 0.7\)), Mastered (\(m \ge 0.9\) and two correct answers on different days).
- Skills drop one level if not practiced for 30 days (shown as "Review due").

### 9.4 Time tracking

Active time only: time counts while the tab is visible and the student interacted in the last 2 minutes. Shown per lesson, unit, module and course, and per day.

### 9.5 Student dashboard

- Course progress ring with percentage (exact, updating live).
- "Continue" card: exact next section.
- Module timeline with status (Not started / In progress / Completed / Mastered).
- Skill map: all skills colored by mastery level.
- Weekly activity chart (minutes per day), streak, goal.
- Scores: quiz and test history with dates and best scores.
- Weak areas: three skills with lowest mastery, with "Practice now" buttons.
- Upcoming deadlines (from instructors).
- Certificates earned.

### 9.6 Instructor and admin analytics

- Class progress heat map (students × lessons).
- Item analysis per problem: % correct, average time, most common wrong answers, discrimination index.
- At-risk students: inactive 7+ days or below 50% on recent quizzes.
- Funnel: started → completed per lesson (find where students quit).
- Revenue: subscriptions, churn, conversions from free to paid.

---

## 10. User Experience and Visual Design

### 10.1 Principles

- Calm, professional, academic, modern. Not childish. Comparable to Brilliant, Coursera and Khan Academy.
- One idea per screen section. Plenty of white space. Math is large and readable.
- Light and dark themes.
- Mobile-first: most students in the region study on phones.

### 10.2 Motion and loading

- Skeleton loaders on every page that fetches data (no blank screens, no spinners longer than necessary).
- Page transitions: short fades/slides (150–250 ms).
- Worked examples reveal step by step with a subtle fade-up.
- Progress bars and rings animate smoothly when they change.
- Correct answer: brief green check animation; wrong: gentle shake and red outline, then the hint.
- Lesson/module completion: a short, tasteful celebration (no confetti storms).
- All motion disabled when the user prefers reduced motion.

### 10.3 Interactive visualizations (required)

| Lesson | Visualization |
|---|---|
| Vectors | 3D vectors you can drag; live \(\langle\vec u,\vec v\rangle\), \([\vec u,\vec v]\), angle |
| Cross product | 3D parallelogram with the cross product vector and its area |
| Box product | 3D parallelepiped and tetrahedron with live volume |
| Polar coordinates | Point and curve plotter; drag \(r\) and \(\theta\) |
| Triangle | Drag vertices; incircle, circumcircle, centroid update live with exact coordinates where possible |
| Lines/planes in space | Rotate scene; see skew lines and their common perpendicular |
| Sphere | Sphere cut by a plane; intersection circle |
| Partial derivatives | Surface with slices \(x=x_0\) and \(y=y_0\) and their tangent lines |
| TpS and NpS | Surface with tangent plane and normal line at a draggable point |
| Optimization | Contour plot with critical points; Lagrange: level curves tangent to the constraint |
| Double/triple integrals | Region builder; Riemann boxes filling a volume |
| ODEs | Slope fields, solution curves through clicked initial points; spring animation |

### 10.4 Downloads and printing

- Every lesson: "Download lesson as PDF" (generated server-side with full math).
- Formula sheet per module and for the whole course, as PDF.
- Problem sets as PDF, with a separate answers PDF.
- Certificates as PDF.
- Instructors: export gradebooks as CSV/Excel.

---

## 11. Data Model (core tables)

```text
users(id, email, name, role, locale, created_at, ...)
courses(id, slug, title, price, status)
modules(id, course_id, order, title)
units(id, module_id, order, title)
sessions(id, user_id, token_hash, expires_at, last_seen_at)            -- hashed tokens only
section_progress(user_id, section_id, lesson_id, active_ms, opened_at, check_answered_correctly, hints_used, completed_at)
lessons(id, unit_id, order, title, est_minutes, version, status)
sections(id, lesson_id, order, type, content_json)
skills(id, slug, title, module_id)   -- skills belong to a module; templates link to skills
problem_templates(id, lesson_id, difficulty, spec_yaml, version, status)
template_skills(template_id, skill_id)
problem_instances(id, template_id, seed, params_json, answer_json)
assessments(id, type, scope_id, settings_json)
attempts(id, user_id, assessment_id, started_at, submitted_at, score, max_score)
responses(id, attempt_id, instance_id, answer_latex, correct, points, hints_used, duration_ms)
events(id, user_id, verb, object_type, object_id, result_json, ts)   -- append-only
progress(user_id, object_type, object_id, value, updated_at)          -- materialized
mastery(user_id, skill_id, value, level, last_practiced_at)
enrollments(user_id, course_id, source, started_at, expires_at)
subscriptions(id, user_id, provider, status, plan, current_period_end)
payments(id, user_id, provider, amount, currency, status, provider_ref)
classes(id, instructor_id, course_id, join_code)
class_members(class_id, user_id)
assignments(id, class_id, assessment_id, due_at)
forum_threads(id, lesson_id, user_id, title, body, status)
forum_posts(id, thread_id, user_id, body, is_accepted, is_verified)
notes(id, user_id, section_id, body)
bookmarks(user_id, section_id)
certificates(id, user_id, course_id, issued_at, verify_code)
audit_log(id, actor_id, action, target, ts)
```

---

## 12. Content Authoring and Using Your Own Documents

### 12.1 Authoring format

Lessons are YAML files (`lesson.yaml`) with typed blocks, validated by strict Zod schemas; text fields hold Markdown with `$inline$` and `$$display$$` math written with the notation macros (changed from MDX in v1.2: stricter validation, no executable content). Problems are YAML templates (Section 7.3). An admin web editor with live preview will come in a later phase; before that, content lives in the repository.

### 12.2 Importing course notes and past papers

Build an import tool:

1. Upload PDF or images of notes or past papers.
2. Extract text and math (OCR with math support, e.g. Mathpix API or a vision model).
3. Convert each question into a problem template draft with difficulty and skill tags.
4. The math engine solves and verifies each one; failures are flagged.
5. A human reviewer approves before publishing.

**Copyright rule:** Do not publish copyrighted textbooks or a university's past papers on a paid platform without written permission. Use them as a guide to level and style, and create **original** problems of the same type. The importer must have a "source / permission" field, and items marked "reference only" can never be published.

---

## 13. Security and Privacy

- HTTPS everywhere; secure, HTTP-only cookies; CSRF protection.
- Passwords hashed (argon2 or bcrypt) if not using a hosted auth provider.
- Role-based access checked on the server for every request.
- Rate limiting on login, answer submission and the math engine.
- The math engine is never public; it accepts requests only from the backend.
- Correct answers are never sent to the browser before submission.
- Input sanitization; math input parsed by a safe parser (no `eval`, no `sympify` on raw untrusted strings without a restricted parser).
- Daily encrypted database backups; restore tested monthly.
- Privacy policy, terms of service, data export and account deletion.
- Payment webhooks verified by signature.

---

## 14. Testing and Quality

| Level | Requirement |
|---|---|
| Math engine | 100% of answer types unit-tested; Section 7.5 table as fixed tests; property tests on generators |
| Content | Section 7.4 pipeline in CI; failing content blocks deployment |
| Backend | Unit tests for progress formulas, scoring, mastery, payments, permissions |
| Frontend | Component tests for quiz, answer input, progress UI |
| End-to-end | Playwright: sign up → lesson → quiz → progress updates → pay → certificate |
| Performance | Lesson page interactive in under 2.5 s on a mid-range phone on 3G |
| Accessibility | Automated axe checks plus manual keyboard test |

Definition of done for any feature: code + tests + passes CI + documented + reviewed in the browser.

---

## 15. Operations

- Environments: local, staging, production.
- Seed script that creates demo users (student, instructor, admin) and demo content.
- Error monitoring and alerts; uptime checks on web and math engine.
- Logs without personal data.
- Runbooks in `/docs` for: deploy, rollback, restore backup, rotate secrets.

---

## 16. Build Phases and Acceptance Criteria

Build strictly in this order. Each phase ends with a working, tested product.

### Phase 1: Foundation

- Monorepo, TypeScript strict, linting, CI.
- Database schema and migrations (Section 11, core tables).
- Auth with roles (student, instructor, admin).
- Design system: tokens, light/dark, typography, KaTeX, notation macros (Section 6).
- Math engine service with answer checking for numbers, expressions and vectors.
- Content schema and loader; Geometry, Module 1, Unit 1, Lessons 1–3 written as real content.
- (Moved to Phase 2: MathLive visual keyboard. Phase 1 answers use a text field with a symbol bar; the engine already parses MathLive's LaTeX. Moved to Phase 5: e-mail verification, password reset, Google sign-in.)
- Lesson player with sections and section-level completion.
- Event tracking and live lesson progress.

**Acceptance:** A new student signs up, opens Lesson 1, and the progress bar increases after each section; refreshing the page keeps the exact progress; all notation follows Section 6; engine tests from Section 7.5 (vector rows) pass.

### Phase 2: Assessment and Tracking

- Problem templates and generator; all answer types; common-mistake feedback; hints; solutions.
- Lesson quizzes, module tests with timer and autosave.
- Progress formulas (Section 9.2), mastery (9.3), time tracking (9.4).
- Student dashboard (9.5).
- Content verification pipeline (7.4) in CI.
- Geometry, Modules 1–2 complete.

**Acceptance:** Every percentage on the dashboard equals the formula in Section 9.2 (unit-tested); retaking a quiz gives new numbers; a wrong but equivalent-form answer (e.g. \(\tfrac{2}{\sqrt2}\) for \(\sqrt2\)) is marked correct; decimal answers are refused with a helpful message.

### Phase 3: Content Completion and Visuals

- Geometry Module 3 and Course 2 (Modules 1–5) complete, all four difficulty tiers, at least 15 templates per lesson.
- Interactive visualizations (Section 10.3).
- Animations and loading states (10.2).
- PDF downloads (10.4).

**Acceptance:** All Section 7.5 problems exist as templates and pass; every lesson has at least one visualization or justified reason not to; Lighthouse performance ≥ 85 on mobile.

### Phase 4: Community and Instructors

- Forum per lesson, notes, bookmarks, mistake notebook, spaced review.
- Instructor classes, assignments, gradebook, analytics, exports.

### Phase 5: Monetization and Launch

- Pricing, free tier, Stripe and mobile money, coupons, receipts.
- Certificates with public verification.
- Mock exams and final exam.
- Legal pages, backups, monitoring, staging → production launch.

### Phase 6: Growth

- Admin content editor with review workflow.
- Document/past-paper importer (Section 12.2).
- Probability and Statistics course.
- French and Kinyarwanda interfaces.
- Optional AI tutor that explains steps, with every mathematical claim checked by the math engine before display.

---

## 17. CLAUDE.md (create this file in the repository root)

```markdown
# CLAUDE.md

## Project
University-level math learning platform (vectors, analytic geometry,
multivariable calculus, differential equations). Full spec:
MATH_PLATFORM_BUILD_SPEC.md. Read it before any large change.

## Non-negotiable rules
1. Mathematical correctness first. Every answer is verified by the math
   engine (apps/math-engine). Never hard-code an answer you did not verify.
2. Exact values only: fractions, simplified radicals, symbolic π and e.
   No decimals unless the question explicitly asks for an approximation.
3. Notation from packages/notation only:
   vectors \vec{u}; dot \dotp{\vec u}{\vec v} -> <u,v>;
   cross \crossp{\vec u}{\vec v} -> [u,v];
   box \boxp{\vec u}{\vec v}{\vec w} -> <u,v,w>.
4. Progress and scores are computed on the server from events.
5. Correct answers are never sent to the client before submission.
6. Every feature ships with tests. CI must be green.

## Commands
(fill in as the project grows: dev, test, verify-content, seed, deploy)

## Conventions
- TypeScript strict, no any. Zod for validation.
- Database changes only via migrations.
- UI strings through i18n.
- Respect prefers-reduced-motion.

## Current phase
Phase 1 (update this line at the start of each phase)
```

---

## 18. Final Checklist Before Launch

- [ ] All modules of Courses 1 and 2 published, each lesson with 4 difficulty tiers
- [ ] Content verification pipeline green
- [ ] Progress updates live on every section, problem and quiz
- [ ] Dashboard numbers match server formulas
- [ ] Notation audit passed (vectors with arrows, \(\langle\cdot,\cdot\rangle\), \([\cdot,\cdot]\), \(\langle\cdot,\cdot,\cdot\rangle\))
- [ ] No decimals in any answer key
- [ ] Payments tested in test mode with cards and mobile money
- [ ] Certificates verifiable online
- [ ] Backups restored successfully once
- [ ] Mobile tested on low-end Android phone
- [ ] Privacy policy and terms published
- [ ] Permission recorded for any third-party material

---

*End of specification.*
