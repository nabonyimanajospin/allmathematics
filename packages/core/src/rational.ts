/** Exact rational numbers on bigint. Progress is never computed with floating point (spec section 9.2). */

export interface Frac {
  readonly num: bigint;
  readonly den: bigint; // always > 0
}

function gcd(a: bigint, b: bigint): bigint {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y !== 0n) {
    [x, y] = [y, x % y];
  }
  return x;
}

export function frac(num: bigint | number, den: bigint | number = 1n): Frac {
  let n = BigInt(num);
  let d = BigInt(den);
  if (d === 0n) throw new RangeError("Denominator must not be zero");
  if (d < 0n) {
    n = -n;
    d = -d;
  }
  const g = gcd(n, d);
  return g > 1n ? { num: n / g, den: d / g } : { num: n, den: d };
}

export const ZERO: Frac = frac(0);
export const ONE: Frac = frac(1);

export function add(a: Frac, b: Frac): Frac {
  return frac(a.num * b.den + b.num * a.den, a.den * b.den);
}

export function mul(a: Frac, b: Frac): Frac {
  return frac(a.num * b.num, a.den * b.den);
}

export function div(a: Frac, b: Frac): Frac {
  if (b.num === 0n) throw new RangeError("Division by zero");
  return frac(a.num * b.den, a.den * b.num);
}

export function eq(a: Frac, b: Frac): boolean {
  return a.num === b.num && a.den === b.den;
}

export function lte(a: Frac, b: Frac): boolean {
  return a.num * b.den <= b.num * a.den;
}

export function min(a: Frac, b: Frac): Frac {
  return lte(a, b) ? a : b;
}

/** Whole percentage, rounded DOWN, clamped to 0..100. 100 is returned only when the value is exactly 1. */
export function percentFloor(a: Frac): number {
  if (a.num <= 0n) return 0;
  if (a.num >= a.den) return 100;
  return Number((a.num * 100n) / a.den);
}

export function toString(a: Frac): string {
  return a.den === 1n ? a.num.toString() : `${a.num}/${a.den}`;
}

export function parse(text: string): Frac {
  const m = /^(-?\d+)(?:\/(\d+))?$/.exec(text);
  if (!m) throw new RangeError(`Not a fraction: ${text}`);
  return frac(BigInt(m[1] ?? "0"), BigInt(m[2] ?? "1"));
}
