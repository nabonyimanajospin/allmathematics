/** Lesson as delivered to the browser: every text is pre-rendered HTML, no answer keys. */

export interface RBase {
  id: string;
  /** Active seconds that complete this section; null for questions (they need a correct answer). */
  requiredSeconds: number | null;
}

export type RSection =
  | (RBase & { type: "concept"; titleHtml?: string; bodyHtml: string })
  | (RBase & { type: "definition"; termHtml: string; bodyHtml: string })
  | (RBase & { type: "theorem"; nameHtml?: string; statementHtml: string; proofHtml?: string })
  | (RBase & { type: "formula"; titleHtml: string; formulaHtml: string; noteHtml?: string })
  | (RBase & { type: "example"; titleHtml?: string; problemHtml: string; stepsHtml: string[]; answerHtml: string })
  | (RBase & { type: "visual"; kind: "vector2d"; mode: string; titleHtml: string; captionHtml: string })
  | (RBase & {
      type: "check";
      promptHtml: string;
      answerType: "number" | "expression" | "vector" | "point" | "multiple_choice";
      choicesHtml?: string[];
      hintCount: number;
    })
  | (RBase & { type: "summary"; pointsHtml: string[] });

export interface RLesson {
  id: string;
  title: string;
  estMinutes: number;
  objectivesHtml: string[];
  sections: RSection[];
}

export interface LessonStateDto {
  completedSectionIds: string[];
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
