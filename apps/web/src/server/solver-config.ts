/** The free plan's daily limit of solves (SOLVER_FREE_PER_DAY, default 5). */
export function freeSolvesPerDay(): number {
  const n = Number(process.env.SOLVER_FREE_PER_DAY ?? 5);
  return Number.isInteger(n) && n >= 0 ? n : 5;
}
