/** Errors that are safe to show to the user. `code` is stable for the UI and tests. */
export class AppError extends Error {
  constructor(
    public readonly code: string,
    public readonly status: number,
    message: string,
    options?: { cause?: unknown },
  ) {
    super(message, options);
    this.name = "AppError";
  }
}

export const Errors = {
  unauthorized: () => new AppError("unauthorized", 401, "Please sign in."),
  forbidden: () => new AppError("forbidden", 403, "You do not have access to this."),
  notFound: (what = "Not found") => new AppError("not_found", 404, what),
  badRequest: (message: string, code = "bad_request") => new AppError(code, 400, message),
  tooMany: (retryAfterMs: number) =>
    new AppError("rate_limited", 429, `Too many attempts. Try again in ${Math.ceil(retryAfterMs / 1000)} seconds.`),
  unavailable: (message = "The service is temporarily unavailable.", cause?: unknown) =>
    new AppError("unavailable", 503, message, { cause }),
};
