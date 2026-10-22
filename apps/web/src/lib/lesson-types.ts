/** Lesson as delivered to the browser: every text is pre-rendered HTML, no answer keys. */

/** A step of a worked example, with the optional explanation of how it was found. */
export interface RStep {
  html: string;
  whyHtml?: string;
}

export interface RBase {
  id: string;
  /** Active seconds that complete this section; null for questions (they need a correct answer). */
  requiredSeconds: number | null;
}

export type RSection =
  | (RBase & { type: "concept"; titleHtml?: string; bodyHtml: string; moreHtml?: string })
  | (RBase & { type: "definition"; termHtml: string; bodyHtml: string; moreHtml?: string })
  | (RBase & { type: "theorem"; nameHtml?: string; statementHtml: string; proofHtml?: string; moreHtml?: string })
  | (RBase & { type: "formula"; titleHtml: string; formulaHtml: string; noteHtml?: string })
  | (RBase & { type: "example"; titleHtml?: string; problemHtml: string; steps: RStep[]; answerHtml: string; moreHtml?: string })
  | (RBase & { type: "visual"; kind: "vector2d"; mode: string; titleHtml: string; captionHtml: string })
  | (RBase & {
      type: "check";
      promptHtml: string;
      answerType: AnswerKind;
      choicesHtml?: string[];
      hintCount: number;
    })
  | (RBase & { type: "summary"; pointsHtml: string[] });

export type AnswerKind =
  | "number"
  | "expression"
  | "vector"
  | "point"
  | "multiple_choice"
  | "region"
  | "equation"
  | "direction"
  | "points"
  | "ode_solution"
  | "ode_family";

export interface RExercise {
  id: string;
  statementHtml: string;
  answerType: AnswerKind;
  choicesHtml?: string[];
  hintCount: number;
  noteHtml?: string;
}

export interface RExerciseSet {
  id: string;
  taskHtml: string;
  formatHtml?: string;
  source?: string;
  items: RExercise[];
}

export interface RLesson {
  id: string;
  title: string;
  estMinutes: number;
  objectivesHtml: string[];
  sections: RSection[];
  exerciseSets: RExerciseSet[];
}

export interface LessonStateDto {
  completedSectionIds: string[];
  solvedExerciseIds: string[];
  hintsUsed: Record<string, number>;
  resumeSectionId: string;
  progress: {
    lesson: { exact: string; percent: number };
    unit: { exact: string; percent: number };
    module: { exact: string; percent: number };
    course: { exact: string; percent: number };
  };
}

export interface CheckResponseDto {
  status: "correct" | "incorrect" | "invalid";
  code: string;
  message: string;
  hintHtml?: string;
  studentLatexHtml?: string;
  parts?: boolean[];
  explanationHtml?: string;
  progress?: LessonStateDto["progress"];
}
