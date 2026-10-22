/**
 * The version of a lesson that is sent to the browser. Secrets never leave the server (spec section 13):
 * answer keys, explanations, hint texts, common-mistake expressions and the correct choice are removed.
 * The browser learns only how many hints a check has; hint text is fetched one at a time (and counted).
 */

import type { Lesson, Section } from "./schema";

export interface ClientCheck {
  id: string;
  type: "check";
  prompt: string;
  answerType: "number" | "expression" | "vector" | "point" | "multiple_choice";
  choices?: { text: string }[];
  hintCount: number;
  minSeconds?: undefined;
}

export type ClientSection = Exclude<Section, { type: "check" }> | ClientCheck;

export interface ClientLesson {
  id: string;
  title: string;
  estMinutes: number;
  objectives: string[];
  sections: ClientSection[];
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

export function toClientLesson(lesson: Lesson): ClientLesson {
  return {
    id: lesson.id,
    title: lesson.title,
    estMinutes: lesson.estMinutes,
    objectives: lesson.objectives,
    sections: lesson.sections.map(toClientSection),
  };
}
