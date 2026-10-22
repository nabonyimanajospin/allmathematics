/** Typed HTTP client for the internal math engine. Used by the web backend and the content scripts. */

import { z } from "zod";

const checkResponse = z.object({
  status: z.enum(["correct", "incorrect", "invalid"]),
  code: z.string(),
  message: z.string(),
  student_latex: z.string().nullable().optional(),
  method: z.string().nullable().optional(),
  parts: z.array(z.boolean()).nullable().optional(),
  hint: z.string().nullable().optional(),
});
export type EngineCheckResponse = z.infer<typeof checkResponse>;

const verifyResponse = z.object({
  equal: z.boolean(),
  method: z.string().nullable().optional(),
  code: z.string().nullable().optional(),
  message: z.string().nullable().optional(),
});

const computeResponse = z.object({
  ok: z.boolean(),
  text: z.string().nullable().optional(),
  latex: z.string().nullable().optional(),
  code: z.string().nullable().optional(),
  message: z.string().nullable().optional(),
});

export interface EngineCheckRequest {
  answer_type:
    | "number"
    | "expression"
    | "vector"
    | "point"
    | "multiple_choice"
    | "auto"
    | "region"
    | "equation"
    | "direction"
    | "points"
    | "ode_solution"
    | "ode_family";
  student: string;
  correct: string;
  input_format?: "auto" | "latex" | "text";
  variables?: string[];
  allow_decimal?: boolean;
  sig_figs?: number;
  mistakes?: { expr: string; hint: string }[];
  coordinates?: string[];
  constraint?: { equation: string; solve_for: string; ranges?: Record<string, [number, number]>; substitutions?: Record<string, string> };
  ode?: {
    order: number;
    equation?: string;
    family?: string;
    constants?: string[];
    conditions?: { at: string; value: string; derivative?: number }[];
    sample?: [number, number];
    parameters?: string[];
  };
}

export class EngineUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EngineUnavailableError";
  }
}

export interface EngineClientOptions {
  url: string;
  token: string;
  timeoutMs?: number;
  fetchImpl?: typeof fetch;
  /** Extra attempts after a network error or HTTP 5xx. Default 2. */
  retries?: number;
  /** Base delay between attempts; attempt n waits n times this. Default 250 ms. */
  retryDelayMs?: number;
}

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

export function createEngineClient(opts: EngineClientOptions) {
  const base = opts.url.replace(/\/$/, "");
  const doFetch = opts.fetchImpl ?? fetch;
  const timeout = opts.timeoutMs ?? 12_000;
  const retries = opts.retries ?? 2;
  const retryDelayMs = opts.retryDelayMs ?? 250;

  /**
   * Engine calls are pure (same input, same answer), so a failed call is safely retried a few times:
   * a network hiccup or an engine restart must not show a student "answer checking is unavailable".
   * Client errors (4xx) are never retried.
   */
  async function post<T>(path: string, body: unknown, schema: z.ZodType<T>): Promise<T> {
    let lastError = "unknown error";
    for (let attempt = 0; attempt <= retries; attempt++) {
      if (attempt > 0) await sleep(retryDelayMs * attempt);
      let res: Response;
      try {
        res = await doFetch(`${base}${path}`, {
          method: "POST",
          headers: { "content-type": "application/json", "x-engine-token": opts.token },
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(timeout),
        });
      } catch (e) {
        lastError = `unreachable at ${base}: ${e instanceof Error ? e.message : String(e)}`;
        continue;
      }
      if (res.status >= 500) {
        lastError = `HTTP ${res.status} for ${path}`;
        continue;
      }
      if (!res.ok) throw new EngineUnavailableError(`Math engine returned HTTP ${res.status} for ${path}`);
      const parsed = schema.safeParse(await res.json().catch(() => null));
      if (!parsed.success) throw new EngineUnavailableError(`Math engine returned an unexpected response for ${path}`);
      return parsed.data;
    }
    throw new EngineUnavailableError(`Math engine ${lastError}`);
  }

  return {
    check: (req: EngineCheckRequest) => post("/v1/check", req, checkResponse),
    verify: (a: string, b: string) => post("/v1/verify", { a, b }, verifyResponse),
    compute: (expression: string) => post("/v1/compute", { expression }, computeResponse),
    async health(): Promise<boolean> {
      try {
        const res = await doFetch(`${base}/health`, { signal: AbortSignal.timeout(3000) });
        return res.ok;
      } catch {
        return false;
      }
    },
  };
}

export type EngineClient = ReturnType<typeof createEngineClient>;
