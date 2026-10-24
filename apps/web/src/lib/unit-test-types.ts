import type { AnswerKind } from "./lesson-types";

/** A question of a unit test as the browser sees it: no answer key, no hints. */
export interface TestQuestionDto {
  index: number;
  promptHtml: string;
  answerType: AnswerKind;
  /** For a multiple-choice question: the choices (the answer sent back is the number of the chosen one, from 0). */
  choicesHtml?: string[];
}

export interface StartedTestDto {
  attemptId: string;
  unitId: string;
  passScore: number;
  questions: TestQuestionDto[];
}

/** Shown after the attempt is submitted: the worked solutions are allowed now. */
export interface TestResultDto {
  score: number;
  total: number;
  passScore: number;
  passed: boolean;
  results: { index: number; correct: boolean; solutionHtml: string }[];
}
