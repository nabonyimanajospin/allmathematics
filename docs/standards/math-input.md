# Typing mathematics

The learner types mathematics **as it is printed**, in one kind of field across the whole platform.

## 1. Today (current state)

- Lessons, exercises and unit tests: a visual math field (MathLive, `apps/web/src/components/lesson/math-field.tsx`): a fraction is typed with `/` and appears as a numerator over a denominator; powers and roots appear in place; a "Type as plain text instead" switch; a row of symbol buttons.
- Solver, grapher and triangle toolkit: plain text boxes (`x^2`, `sqrt(2)`, `pi`).
- The text sent to the math engine is the same plain text everywhere (`apps/web/src/lib/latex-input.ts` converts the visual field).

## 2. Target (Rule for new work)

1. **One component** for every place where mathematics is typed: lessons, exercises, tests, solver, grapher, triangle toolkit, (later) exams. Same behavior, same buttons, same messages.
2. **Visual by default, plain text available.** The learner sees `\dfrac{3}{4}`, `x^2`, `\sqrt{2}`, vectors, matrices as printed; a switch gives the plain-text box; the choice is remembered.
3. **Palettes by topic**, shown when the question needs them: fraction, power, root, absolute value, π, e, ∞, Greek letters, vector arrow, matrix, integral, sum, limit, inequality signs, set symbols, intervals, ± and the degree sign.
4. **Phone keyboard** with the same palettes; the field never sits under the phone keyboard.
5. **Live reading**: the field shows how the engine understood the input when it is ambiguous (for example `1/2x`), before the answer is sent.
6. **The same notation as the lessons** ([notation-and-naming.md](notation-and-naming.md)): what the learner types and what the lessons show look the same.
7. **Answer acceptance** (already a rule): any equivalent exact form is accepted; a decimal is refused with a friendly message unless an approximation is asked; the answer type (number, expression, point, vector, equation, interval, set, matrix) is shown before typing, with an example of the format that never contains the answer.
8. **Accessibility**: a label for every field, keyboard use, the typed mathematics read aloud by screen readers.
9. **Tests** for every form of input: unit tests of the conversion to engine text, browser tests of typing in each place.
