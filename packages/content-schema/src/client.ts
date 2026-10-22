/**
 * The version of a lesson that is sent to the browser. Secrets never leave the server (spec section 13):
 * answer keys, explanations, hint texts, solutions, common-mistake expressions and the correct choice are removed.
 * The browser learns only how many hints a question has; hint text is fetched one at a time (and counted).
 */

import type { AnswerType, CheckSpec, Exercise, Lesson, Section } from "./schema";

export interface ClientCheck {
  id: string;
  type: "check";
  prompt: string;
  answerType: AnswerType;
  choices?: { text: string }[];
  hintCount: number;
  minSeconds?: undefined;
}

export type ClientSection = Exclude<Section, { type: "check" }> | ClientCheck;

export interface ClientExercise {
  id: string;
  statement: string;
  answerType: AnswerType;
  choices?: { text: string }[];
  hintCount: number;
  note?: string;
}

export interface ClientExerciseSet {
  id: string;
  task: string;
  format?: string;
  source?: string;
  items: ClientExercise[];
}

export interface ClientLesson {
  id: string;
  title: string;
  estMinutes: number;
  objectives: string[];
  sections: ClientSection[];
  exerciseSets: ClientExerciseSet[];
}

export function toClientSection(s: Section): ClientSection {
  if (s.type !== "check") return s;
  const client: ClientCheck = {
    id: s.id,
    type: "check",
    prompt: s.prompt,
    answerType: s.answerType,
    hintCount: s.hints.length,
  };
  if (s.choices) client.choices = s.choices.map((c) => ({ text: c.text }));
  return client;
}

export function toClientExercise(e: Exercise): ClientExercise {
  const client: ClientExercise = {
    id: e.id,
    statement: e.statement,
    answerType: e.answerType,
    hintCount: e.hints.length,
  };
  if (e.choices) client.choices = e.choices.map((c) => ({ text: c.text }));
  if (e.note) client.note = e.note;
  return client;
}

export function toClientLesson(lesson: Lesson): ClientLesson {
  return {
    id: lesson.id,
    title: lesson.title,
    estMinutes: lesson.estMinutes,
    objectives: lesson.objectives,
    sections: lesson.sections.map(toClientSection),
    exerciseSets: lesson.exerciseSets.map((set) => ({
      id: set.id,
      task: set.task,
      ...(set.format ? { format: set.format } : {}),
      ...(set.source ? { source: set.source } : {}),
      items: set.items.map(toClientExercise),
    })),
  };
}

/** Every exercise of a lesson, in order. */
export function allExercises(lesson: Lesson): Exercise[] {
  return lesson.exerciseSets.flatMap((s) => s.items);
}

/** The body of a request to the math engine for one answer (server side only). */
export interface EngineRequestBody {
  answer_type: AnswerType;
  student: string;
  correct: string;
  input_format?: "auto" | "latex" | "text";
  variables?: string[];
  coordinates?: string[];
  allow_decimal?: boolean;
  mistakes?: { expr: string; hint: string }[];
  constraint?: { equation: string; solve_for: string; ranges?: Record<string, [number, number]> };
  ode?: {
    order: number;
    equation?: string;
    family?: string;
    constants?: string[];
    conditions?: { at: string; value: string; derivative?: number }[];
    sample?: [number, number];
  };
}

/**
 * Build the engine request for a question (a check or an exercise). `student` is the answer to test;
 * pass the model answer to verify that the key checks itself.
 */
export function toEngineRequest(q: CheckSpec & { allowDecimal?: boolean | undefined }, student: string, format: "auto" | "text" = "auto"): EngineRequestBody {
  if (q.answerType === "multiple_choice") {
    return { answer_type: "multiple_choice", student, correct: String(q.correctIndex ?? -1) };
  }
  const body: EngineRequestBody = { answer_type: q.answerType, student, correct: q.answer, input_format: format };
  if (q.variables) body.variables = q.variables;
  if (q.coordinates) body.coordinates = q.coordinates;
  if (q.allowDecimal) body.allow_decimal = true;
  if (q.mistakes) body.mistakes = q.mistakes;
  if (q.constraint) {
    body.constraint = {
      equation: q.constraint.equation,
      solve_for: q.constraint.solveFor,
      ...(q.constraint.ranges ? { ranges: q.constraint.ranges as Record<string, [number, number]> } : {}),
    };
  }
  if (q.ode) {
    body.ode = {
      order: q.ode.order,
      ...(q.ode.equation ? { equation: q.ode.equation } : {}),
      ...(q.ode.family ? { family: q.ode.family } : {}),
      ...(q.ode.constants ? { constants: q.ode.constants } : {}),
      ...(q.ode.conditions
        ? { conditions: q.ode.conditions.map((c) => ({ at: c.at, value: c.value, ...(c.derivative ? { derivative: c.derivative } : {}) })) }
        : {}),
      ...(q.ode.sample ? { sample: q.ode.sample } : {}),
    };
  }
  return body;
}
