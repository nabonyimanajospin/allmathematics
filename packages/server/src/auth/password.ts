/** Password hashing with scrypt (Node built-in, no native build). Parameters are stored in the hash. */

import { randomBytes, scrypt, timingSafeEqual, type ScryptOptions } from "node:crypto";

const KEYLEN = 64;
const DEFAULT_N = 32768; // 2^15, about 100 ms on a modern CPU
const R = 8;
const P = 1;

function scryptAsync(password: string, salt: Buffer, keylen: number, opts: ScryptOptions): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    scrypt(password.normalize("NFKC"), salt, keylen, opts, (err, key) => (err ? reject(err) : resolve(key)));
  });
}

function costN(): number {
  const fromEnv = Number(process.env.SCRYPT_N);
  return Number.isInteger(fromEnv) && fromEnv >= 1024 && (fromEnv & (fromEnv - 1)) === 0 ? fromEnv : DEFAULT_N;
}

function maxmem(n: number): number {
  return 128 * n * R * 2 + 1024 * 1024;
}

export async function hashPassword(password: string): Promise<string> {
  const n = costN();
  const salt = randomBytes(16);
  const key = await scryptAsync(password, salt, KEYLEN, { N: n, r: R, p: P, maxmem: maxmem(n) });
  return `scrypt$${n}$${R}$${P}$${salt.toString("base64")}$${key.toString("base64")}`;
}

export async function verifyPassword(password: string, stored: string): Promise<boolean> {
  const parts = stored.split("$");
  if (parts.length !== 6 || parts[0] !== "scrypt") return false;
  const [, nStr, rStr, pStr, saltB64, keyB64] = parts as [string, string, string, string, string, string];
  const n = Number(nStr);
  const r = Number(rStr);
  const p = Number(pStr);
  const validParams =
    [n, r, p].every((v) => Number.isInteger(v) && v >= 1) && n >= 2 && (n & (n - 1)) === 0 && n <= 1 << 20 && r <= 32 && p <= 16;
  if (!validParams) return false;
  const expected = Buffer.from(keyB64, "base64");
  if (expected.length < 16 || expected.length > 128) return false;
  try {
    const actual = await scryptAsync(password, Buffer.from(saltB64, "base64"), expected.length, {
      N: n,
      r,
      p,
      maxmem: 128 * n * r * 2 + 1024 * 1024,
    });
    return actual.length === expected.length && timingSafeEqual(actual, expected);
  } catch {
    return false;
  }
}

let dummy: Promise<string> | undefined;
/** A valid hash of a random password, used to spend the same time when the e-mail is unknown. */
export function dummyHash(): Promise<string> {
  dummy ??= hashPassword(randomBytes(12).toString("hex"));
  return dummy;
}
