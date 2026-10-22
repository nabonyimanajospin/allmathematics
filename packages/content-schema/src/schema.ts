/**
 * Zod schemas for course content (spec sections 3.3, 7.3, 12.1).
 * Lessons are YAML files; text fields hold Markdown with $inline$ and $$display$$ math written with the
 * notation macros (packages/notation). All objects are strict: a misspelled key is an error, not ignored.
 */

import { z } from "zod";

export const STATUSES = ["draft", "in_review", "verified", "published", "archived"] as const;
export type ContentStatus = (typeof STATUSES)[number];

export const slug = z
  .string()
  .min(2)
  .max(60)
  .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Use lowercase letters, digits and hyphens");

const text = z.string().min(1).max(6000);
const shortText = z.string().min(1).max(300);

/** Keys common to every block. */
const blockBase = {
  id: slug,
  /** Override the minimum active seconds that complete this block. */
  minSeconds: z.number().int().min(1).max(600).optional(),
  /** Lint rule ids that are deliberately allowed in this block (rare, reviewed). */
  lintIgnore: z.array(z.string()).max(5).optional(),
  /** The block deliberately contains decimals (an approximation question). */
  allowDecimal: z.boolean().optional(),
};

export const ANSWER_TYPES = [
  "number",
  "expression",
  "vector",
  "point",
  "multiple_choice",
  "region",
  "equation",
  "direction",
  "points",
  "ode_solution",
  "ode_family",
] as const;
export type AnswerType = (typeof ANSWER_TYPES)[number];

export const mistakeSchema = z.strictObject({
  expr: z.string().min(1).max(200),
  hint: z.string().min(1).max(300),
});

const verifySchema = z.strictObject({
  /** Expression in the engine language, e.g. cross((2,-1,3),(1,4,-2)). */
  expr: z.string().min(1).max(400),
  /** The exact value the lesson states, in the engine language, e.g. (-10,7,9). */
  equals: z.string().min(1).max(200),
  note: shortText.optional(),
});
export type VerifyEntry = z.infer<typeof verifySchema>;

const concept = z.strictObject({
  ...blockBase,
  type: z.literal("concept"),
  title: shortText.optional(),
  body: text,
});

const definition = z.strictObject({
  ...blockBase,
  type: z.literal("definition"),
  term: shortText,
  body: text,
});

const theorem = z.strictObject({
  ...blockBase,
  type: z.literal("theorem"),
  name: shortText.optional(),
  statement: text,
  proof: text.optional(),
});

const formula = z.strictObject({
  ...blockBase,
  type: z.literal("formula"),
  title: shortText,
  /** Display LaTeX without $ delimiters. */
  formula: z.string().min(1).max(600),
  note: text.optional(),
});

const example = z.strictObject({
  ...blockBase,
  type: z.literal("example"),
  title: shortText.optional(),
  problem: text,
  steps: z.array(text).min(1).max(12),
  answer: text,
  /** Every stated result is recomputed by the math engine (spec 7.4, step 3). */
  verify: z.array(verifySchema).min(1).max(12),
});

const visual = z.strictObject({
  ...blockBase,
  type: z.literal("visual"),
  kind: z.enum(["vector2d"]),
  title: shortText,
  caption: text,
  config: z.record(z.string(), z.union([z.number(), z.string(), z.boolean()])).optional(),
});

const choiceSchema = z.strictObject({
  text: shortText,
  /** The option's value in the engine language; used to prove exactly one option is right. */
  value: z.string().min(1).max(200),
});

/** Settings for the answer types that need more than a key (spec section 7.2). */
const rangesSchema = z.record(z.string(), z.tuple([z.number(), z.number()]));

const constraintSchema = z.strictObject({
  /** The curve or surface F = 0 on which implicit derivatives are compared. */
  equation: z.string().min(1).max(200),
  solveFor: z.string().regex(/^[A-Za-z]$/),
  ranges: rangesSchema.optional(),
  /** Symbols replaced before comparing, e.g. { y1: "(2*y-x^2)/(y^2-2*x)" } so that answers may use y'. */
  substitutions: z.record(z.string(), z.string()).optional(),
});

const conditionSchema = z.strictObject({
  at: z.string().min(1).max(40),
  value: z.string().min(1).max(40),
  derivative: z.number().int().min(0).max(2).optional(),
});

const odeSchema = z.strictObject({
  order: z.number().int().min(1).max(3),
  /** For `ode_solution`: the equation F(x, y, y1, y2) = 0 that the answer must satisfy (y1 is y', y2 is y''). */
  equation: z.string().min(1).max(300).optional(),
  /** For `ode_family`: the general solution, y = f(x, c...) or F(x, y, c) = 0. */
  family: z.string().min(1).max(300).optional(),
  constants: z.array(z.string().regex(/^[A-Za-z][0-9]?$/)).max(4).optional(),
  conditions: z.array(conditionSchema).max(3).optional(),
  /** Interval of x where the answer is tested numerically. */
  sample: z.tuple([z.number(), z.number()]).optional(),
});

const answerSpec = {
  answerType: z.enum(ANSWER_TYPES),
  /** The key in the engine language. For ODE and region types it is a model answer that checks itself. Never sent to the browser. */
  answer: z.string().min(1).max(450),
  variables: z.array(z.string().regex(/^[A-Za-z](?:_[A-Za-z0-9]+|[0-9])?$/)).max(8).optional(),
  /** Coordinate variables of a region or an equation, e.g. ["x", "y", "z"]. */
  coordinates: z.array(z.string().regex(/^[A-Za-z]$/)).min(1).max(4).optional(),
  constraint: constraintSchema.optional(),
  ode: odeSchema.optional(),
  choices: z.array(choiceSchema).min(2).max(6).optional(),
  correctIndex: z.number().int().min(0).max(5).optional(),
  hints: z.array(text).max(3).default([]),
  mistakes: z.array(mistakeSchema).max(6).optional(),
};

const check = z.strictObject({
  ...blockBase,
  type: z.literal("check"),
  prompt: text,
  ...answerSpec,
  explanation: text,
});

const practice = z.strictObject({
  ...blockBase,
  type: z.literal("practice"),
  skill: slug,
});

const summary = z.strictObject({
  ...blockBase,
  type: z.literal("summary"),
  points: z.array(text).min(2).max(10),
});

export const sectionSchema = z.discriminatedUnion("type", [
  concept,
  definition,
  theorem,
  formula,
  example,
  visual,
  check,
  practice,
  summary,
]);
export type Section = z.infer<typeof sectionSchema>;
export type SectionType = Section["type"];
export type CheckSection = Extract<Section, { type: "check" }>;
export type ExampleSection = Extract<Section, { type: "example" }>;


/** Rules that tie the answer type to the fields it needs. Returns a message, or null when the spec is consistent. */
function answerSpecProblem(s: {
  answerType: (typeof ANSWER_TYPES)[number];
  choices?: unknown[] | undefined;
  correctIndex?: number | undefined;
  ode?: z.infer<typeof odeSchema> | undefined;
}): string | null {
  if (s.answerType === "multiple_choice") {
    if (!s.choices || s.correctIndex === undefined) return "A multiple-choice question needs `choices` and `correctIndex`";
    if (s.correctIndex >= s.choices.length) return "correctIndex is out of range";
  } else if (s.choices || s.correctIndex !== undefined) {
    return "`choices` and `correctIndex` are only for multiple-choice questions";
  }
  if (s.answerType === "ode_solution" && !s.ode?.equation) return "An ode_solution question needs `ode.equation`";
  if (s.answerType === "ode_family") {
    if (!s.ode?.family) return "An ode_family question needs `ode.family`";
    if ((s.ode.constants?.length ?? 0) !== s.ode.order) return "`ode.constants` must list exactly `ode.order` constants";
  }
  if (s.answerType !== "ode_solution" && s.answerType !== "ode_family" && s.ode) return "`ode` is only for differential-equation questions";
  return null;
}

export type CheckSpec = Pick<
  z.infer<typeof check>,
  "answerType" | "answer" | "variables" | "coordinates" | "constraint" | "ode" | "choices" | "correctIndex" | "hints" | "mistakes"
>;

/** One exercise: a statement to work on, a key, hints and a worked solution shown after an attempt. */
export const exerciseSchema = z.strictObject({
  id: slug,
  /** The function, equation or region to work on (Markdown with math). The set's `task` says what to do. */
  statement: text,
  ...answerSpec,
  /** Worked solution (Markdown with math). Required: every exercise is explained. */
  solution: text,
  /** Optional independent recomputation of the key by the engine, e.g. diff(f, x) equals the stated derivative. */
  verify: z.array(verifySchema).max(6).optional(),
  /** A remark for the student, e.g. a correction to the printed exercise. */
  note: text.optional(),
  allowDecimal: z.boolean().optional(),
  lintIgnore: z.array(z.string()).max(5).optional(),
});
export type Exercise = z.infer<typeof exerciseSchema>;

export const exerciseSetSchema = z.strictObject({
  id: slug,
  /** Instruction shared by the items, e.g. "Find the domain of definition of each function." */
  task: text,
  /** How to type the answer, e.g. "Write the conditions, like x^2 + y^2 <= 4". */
  format: text.optional(),
  /** Where the exercises come from (kept for the permission record, spec section 12.2). */
  source: shortText.optional(),
  items: z.array(exerciseSchema).min(1).max(20),
});
export type ExerciseSet = z.infer<typeof exerciseSetSchema>;

export const lessonIdPattern = /^[a-z]{3,5}-m\d{2}-u\d{2}-l\d{2}$/;
export const unitIdPattern = /^[a-z]{3,5}-m\d{2}-u\d{2}$/;
export const moduleIdPattern = /^[a-z]{3,5}-m\d{2}$/;

const status = z.enum(STATUSES);

export const lessonSchema = z
  .strictObject({
    id: z.string().regex(lessonIdPattern),
    title: shortText,
    estMinutes: z.number().int().min(5).max(90),
    version: z.number().int().min(1),
    status,
    skills: z.array(slug).min(1).max(6),
    objectives: z.array(shortText).min(1).max(6),
    sections: z.array(sectionSchema).min(3).max(40),
    exerciseSets: z.array(exerciseSetSchema).max(8).default([]),
  })
  .superRefine((lesson, ctx) => {
    const seen = new Set<string>();
    lesson.sections.forEach((s, i) => {
      if (seen.has(s.id)) {
        ctx.addIssue({ code: "custom", path: ["sections", i, "id"], message: `Duplicate section id “${s.id}”` });
      }
      seen.add(s.id);
    });
    const exerciseIds = new Set<string>();
    lesson.exerciseSets.forEach((set, si) => {
      set.items.forEach((item, ii) => {
        const path = ["exerciseSets", si, "items", ii];
        if (exerciseIds.has(item.id) || seen.has(item.id)) {
          ctx.addIssue({ code: "custom", path: [...path, "id"], message: `Duplicate id “${item.id}”` });
        }
        exerciseIds.add(item.id);
        const problem = answerSpecProblem(item);
        if (problem) ctx.addIssue({ code: "custom", path, message: problem });
      });
    });
    lesson.sections.forEach((s, i) => {
      if (s.type === "check") {
        const problem = answerSpecProblem(s);
        if (problem) ctx.addIssue({ code: "custom", path: ["sections", i], message: problem });
      }
    });
  });
export type Lesson = z.infer<typeof lessonSchema>;

export const courseSchema = z.strictObject({
  id: z.string().regex(/^[a-z]{3,5}$/),
  title: shortText,
  description: text,
  status,
  order: z.number().int().min(1),
});
export type CourseMeta = z.infer<typeof courseSchema>;

export const moduleSchema = z.strictObject({
  id: z.string().regex(moduleIdPattern),
  title: shortText,
  description: text,
  order: z.number().int().min(1),
  /** Free tier (spec section 4). */
  free: z.boolean().default(false),
});
export type ModuleMeta = z.infer<typeof moduleSchema>;

export const unitSchema = z.strictObject({
  id: z.string().regex(unitIdPattern),
  title: shortText,
  order: z.number().int().min(1),
});
export type UnitMeta = z.infer<typeof unitSchema>;
