# Curriculum structure

The same structure for every course and every level. A learner who has finished one lesson knows where everything is in every other lesson.

## 1. The hierarchy

**Rule (current):**

```text
Course  →  Module  →  Unit  →  Lesson  →  Section
```

| Level | What it is | Size | Ends with |
|---|---|---|---|
| Course | One subject, sold and followed as a whole (code `geo`, `mvc`, `stat`) | several modules | (later) a course certificate |
| Module | A major theme of the course | 3 to 6 units | (later) a module test |
| Unit | Closely related lessons | 3 to 8 lessons | the **unit test** (10 questions, pass mark 7) |
| Lesson | One study session | 30 to 60 minutes | its exercises |
| Section | One block of a lesson: a definition, a formula, an example, a question... | one idea | — |

**Proposed (to be confirmed at the owner's meeting with the lecturer):** the names of the levels may change (for example "chapter" instead of "unit"). Whatever names are chosen:

- the hierarchy has **at most five levels** and the **same levels everywhere**;
- a name is used for one level only, in the content, the interface and the documents;
- the change is made once, everywhere (content files, ids, interface texts, these documents), never module by module.

The **level of study** (`S`, `U1` ... `D`, see [vision-and-scope.md](vision-and-scope.md)) is a label of each course and module, not an extra level of the hierarchy.

## 2. Ids and file names (Rule)

- Ids are stable, lowercase and readable: `geo-m03-u02-l06` = course `geo`, module 3, unit 2, lesson 6. Two digits for each number (`m01`...`m99`).
- A new course gets a short code of 2 to 5 lowercase letters (`alg`, `lin`, `ana`, `pde`, `num`...), agreed once and never reused.
- Folders: `content/<course>/m<NN>-<slug>/u<NN>-<slug>/l<NN>-<slug>/lesson.yaml` (+ the generated `exercises.yaml`).
- Section ids inside a lesson are short and unique: `def-…`, `thm-…`, `formulas`, `ex-…`, `chk-…`, `fig-…`, `summary`. Exercise ids are unique in the lesson.
- An id is never changed once published (progress is stored by id). A lesson that moves keeps its id.

## 3. The lesson template (Proposed, the one order for every lesson)

Every lesson has the same parts **in this order**. A part may be absent when it has no content (for example no figure), but the order never changes.

| # | Part | Section type | Content |
|---|---|---|---|
| 1 | Header | (metadata) | title, level, estimated time, **prerequisites** (links to earlier lessons), **objectives** ("In this lesson you will…") |
| 2 | Introduction | `concept` | why the topic matters, the idea in plain words, a link to what the learner already knows |
| 3 | Definitions and notation | `definition` | each new term defined once, with its notation; "Other notations you may see" when textbooks differ |
| 4 | Results | `theorem` | properties and theorems, each with its proof (`U1` and above) or its justification (`S`), a "why" for the key step |
| 5 | Key formulas | `formula` | the formulas to remember, in one box; **always before the first question** of the lesson |
| 6 | Figures | `visual` | a figure for every geometric or graphical idea (2D or rotatable 3D, exact coordinates) |
| 7 | Worked examples | `example` | from simple to harder; each: problem, steps with the reason of each step, the **final answer** clearly marked, and the engine's verification |
| 8 | Quick checks | `check` | one short question after the example(s) of each main idea; answering it correctly opens what follows |
| 9 | Common mistakes | `concept` (titled "Common mistakes") | the errors learners usually make, and how to avoid them (encouraged from now on) |
| 10 | Summary | `summary` | the points to remember, in a few lines |
| 11 | Exercises | (exercise sets) | graded practice, at least 15 per lesson (section 5) |
| 12 | Final answers | (generated) | the list of final answers of the exercises (section 6) |

Notes:

- Parts 4 to 8 may repeat in cycles for a long lesson (definition → example → check, then the next idea), but **inside a cycle the order is the same**, and the key formulas still come before the first question.
- Numbering inside a lesson is uniform: *Definition 1, Theorem 1, Example 1, Exercise 1*, counted separately and shown in the titles (Proposed).
- The printable lesson sheet follows the same order.

## 4. Sections: one style for each type (Rule)

- **Definition**: one term, written in bold where it is defined, followed by its notation.
- **Theorem**: statement, then proof (or "Why it is true"), then where it is used.
- **Formula box**: formulas only, with one line saying when each one applies. No examples inside.
- **Worked example**: a complete problem statement, numbered steps, a reason ("why") for every step that is not obvious, the final answer on its own line, the verification by the engine (hidden from the learner, required for publication).
- **Quick check**: one question, exact answer, at least one hint, a short explanation shown after a correct answer.
- **Summary**: 3 to 6 short points, the key formulas repeated in their final form.

## 5. Exercises (Rule)

- At least **15 exercises per lesson**, in sets; each set has an instruction ("Find the domain of definition of each function.") and a format hint (how to type the answer).
- **Every exercise statement says what to do**, even when it is shown alone (in a unit test, on a printed sheet). The set instruction is shown with the question wherever the question appears.
- Graded difficulty inside a lesson: direct application first, then standard exam questions, then a few harder ones (Proposed: labels A, B, C).
- Each exercise has: hints that point to the method **without giving the result**, a worked solution, and a verified final answer.
- A hint never contains the final answer (checked automatically for the answer itself; reviewed by eye for the near-answer).
- Exercises taken from the owner's sheets and exams are kept complete; a printed error is corrected and the correction shown in a note.

## 6. Final answers of the exercises (Decision needed)

The owner wants a list of final answers at the end of each lesson, so that a learner can check that the result is right. The current rule says that **a correct answer is never sent to the browser before the learner has answered** (so that the progress means something).

Options:

1. **Final answer on request, per exercise (recommended):** after a first attempt, or at once with a "Show the final answer" button. Showing it is recorded; the exercise still counts only when the learner types a correct answer. The printed sheet has the list of final answers on its last page.
2. A full answer list at the end of the lesson, always visible: simplest, but the exercises would then count for nothing in the progress.
3. Final answers only on the printed sheet.

Unit tests and (later) certificate exams never show answers before submission, whatever is chosen.

## 7. Tests (Rule)

- **Quick checks** inside the lesson: unlimited attempts, hints, a short explanation.
- **Unit test**: 10 questions drawn from the exercises of the unit (at most 3 multiple choice), each with its instruction; pass mark 7; new questions at every attempt; worked solutions after submission. A unit counts 100% only after its test is passed.
- **Module test** and **course exam**: Target (spec section 8); designed with the certification.

## 8. Progress (Rule)

Lesson: two thirds for the sections read, one third for the exercises solved; unit: 80% lessons + 20% unit test; module and course: averages weighted by time. Public explanation: page `/how-progress-works`. Any change is made in `packages/core/src/progress.ts` and in that page at the same time.

## 9. Definition of done for a module (Rule)

A module is published only when:

1. Every lesson follows the template of section 3 and the notation of [notation-and-naming.md](notation-and-naming.md).
2. Every lesson has at least 15 exercises, each with instruction, hints, worked solution and verified final answer.
3. Every answer key and worked result is verified by the engine (`pnpm verify-content`: 0 errors).
4. Every unit has a unit test that can be drawn.
5. Figures exist for every geometric or graphical idea.
6. Theory at `U3` and above is reviewed and the reviewer recorded.
7. The solver solves the module's computational exercises (or the gaps are listed in the solver coverage report, see [solver.md](solver.md)).
8. The checks are green: types, lint, unit tests, engine tests, browser tests.
