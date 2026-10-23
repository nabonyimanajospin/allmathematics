export const SOLVER_OPERATIONS = ["auto", "derivative", "integral", "limit", "solve", "ode", "simplify", "expand", "factor", "vector"] as const;
export type SolverOperation = (typeof SOLVER_OPERATIONS)[number];

export interface SolverStepDto {
  title: string;
  /** KaTeX HTML rendered on the server; empty when the step has no formula. */
  html: string;
}

export interface SolverAccessDto {
  premium: boolean;
  used: number;
  limit: number | null;
  remaining: number | null;
}

export interface SolveResultDto {
  operation: string;
  questionHtml: string;
  answerHtml: string;
  answerText: string;
  steps: SolverStepDto[];
  notes: string[];
}

export interface SolveResponseDto {
  ok: boolean;
  solution?: SolveResultDto;
  code?: string;
  message?: string;
  access: SolverAccessDto;
}
