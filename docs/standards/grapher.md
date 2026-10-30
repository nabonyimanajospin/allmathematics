# The grapher

The lecturer's requirement: the grapher must work **like GeoGebra in 2D and 3D**, not as a list of curves. This document describes that target and the way to get there. (It is written from knowledge of how GeoGebra works; before building, a side-by-side session with GeoGebra Classic and GeoGebra 3D is recommended to agree on the details.) The current grapher is described in `docs/grapher.md`.

## 1. What makes GeoGebra what it is

1. **Objects, not drawings.** Every point, line, circle, polygon, function or slider is an object with a **name**, a **definition** and a **value**. A point built as "the midpoint of A and B" stays the midpoint when A moves.
2. **Two linked views.** The **Algebra view** lists every object with its definition and its exact value; the **Graphics view** draws them. Changing one changes the other.
3. **Free and dependent objects.** Free objects can be dragged; dependent objects follow (construction by dependencies). A point can also be bound to an object (a point on a circle moves only along it).
4. **Tools and commands are the same thing.** The construction tools (touch the picture) and the input bar commands (`Midpoint(A, B)`, `Intersect(c, d)`) create the same objects.
5. **Properties.** Each object has a color, a style, a label (name, value, both or none), can be hidden, fixed, traced.
6. **Undo, redo, delete with dependents, redefine.**

## 2. Target features (with priority)

**P1 — the construction core**

- An object model with dependencies (free, dependent, bound objects), names, definitions, values; recalculation when a free object moves.
- Algebra view: every object with its definition and its exact value (for example `M = Midpoint(A, B) = (2, 3/2)`), editable, with show/hide.
- Tools: Move; Point; Point on object; Intersection; Midpoint; Segment; Line; Ray; Vector; Polygon; Regular polygon; Circle (center–point, center–radius, three points); Perpendicular line; Parallel line; Perpendicular bisector; Angle bisector; Tangents; Angle; Distance or length; Area; Slope; Slider; Text.
- Commands in the input bar for the same constructions, with autocompletion and a short help for each command.
- Undo and redo; delete with a warning listing the dependent objects; rename; redefine.
- Snapping to the grid and to objects; two points never in the same place (already a rule).

**P2 — calculus and analysis in 2D**

- Functions with their exact roots, extrema, inflection points and intersections (the engine gives exact values when it can prove them; already done for roots and intersections).
- Tangent at a point, derivative graph, shaded integral with its exact value, Riemann sums.
- Transformations: reflection, rotation, translation, dilation.
- Locus and trace.
- Conics through five points, and their equations in canonical form.

**P3 — 3D like GeoGebra 3D**

- Points, vectors, segments, lines, planes (through three points, through a point with a normal), spheres (center–radius, center–point).
- Solids: prism, pyramid, tetrahedron, cube, cylinder, cone; their nets.
- Intersections: line–plane, plane–plane, plane–sphere (the circle), with exact values.
- Surfaces `z = f(x, y)` and parametric surfaces and curves (already there), cross-sections.
- Rotation of the view, the xy / xz / yz views, zoom to fit.

**For all priorities**

- Object properties: color, line style and thickness, point style, label, fill, layer, fixed, trace.
- View settings: axes, grid, equal scales, ranges; export as PNG and SVG; share by link (already there); print.
- Lessons: every figure of a lesson opens in the grapher ("Open in the grapher"), as a starting construction.
- Touch and keyboard use, screen reader names for objects, phone screens.
- Exact values everywhere they can be proved; an approximation is marked `≈`.

## 3. How to get there (Proposed)

The current grapher reads each line separately (functions, named points, segments, circles, polygons). The target needs a **construction graph**: a new core module (in `packages/core`) holding objects and their dependencies, with the existing readers reused for functions and curves. Steps:

1. The object model and the Algebra view (P1 core), with the existing tools rebuilt on it; tests of every construction.
2. The remaining P1 tools and commands; undo and redo.
3. P2, then P3, each with browser tests.

Each step keeps the grapher usable; nothing is removed before its replacement works.
