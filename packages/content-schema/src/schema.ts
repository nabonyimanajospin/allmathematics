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

export const ANSWER_TYPES = ["number", "expression", "vector", "point", "multiple_choice"] as const;
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

const check = z.strictObject({
  ...blockBase,
  type: z.literal("check"),
  prompt: text,
  answerType: z.enum(ANSWER_TYPES),
  /** The key in the engine language. Never sent to the browser. */
  answer: z.string().min(1).max(300),
  /** Symbols allowed in the student's answer besides those in the key. */
  variables: z.array(z.string().regex(/^[A-Za-z](?:_[A-Za-z0-9]+)?$/)).max(6).optional(),
  choices: z.array(choiceSchema).min(3).max(6).optional(),
  correctIndex: z.number().int().min(0).max(5).optional(),
  hints: z.array(text).max(3).default([]),
  explanation: text,
  mistakes: z.array(mistakeSchema).max(6).optional(),
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
  })
  .superRefine((lesson, ctx) => {
    const seen = new Set<string>();
    lesson.sections.forEach((s, i) => {
      if (seen.has(s.id)) {
        ctx.addIssue({ code: "custom", path: ["sections", i, "id"], message: `Duplicate section id “${s.id}”` });
      }
      seen.add(s.id);
    });
    lesson.sections.forEach((s, i) => {
      if (s.type !== "check") return;
      if (s.answerType === "multiple_choice") {
        if (!s.choices || s.correctIndex === undefined) {
          ctx.addIssue({
            code: "custom",
            path: ["sections", i],
            message: "A multiple-choice check needs `choices` and `correctIndex`",
          });
        } else if (s.correctIndex >= s.choices.length) {
          ctx.addIssue({ code: "custom", path: ["sections", i, "correctIndex"], message: "correctIndex is out of range" });
        }
      } else if (s.choices || s.correctIndex !== undefined) {
        ctx.addIssue({
          code: "custom",
          path: ["sections", i],
          message: "`choices` and `correctIndex` are only for multiple-choice checks",
        });
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
