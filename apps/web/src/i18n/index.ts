import en from "./en.json";

/**
 * No hard-coded UI strings (spec section 5.4). English is the only locale for now; French and
 * Kinyarwanda are added by adding a file with the same keys and a locale switch here.
 */
type Messages = typeof en;

type Leaves<T, P extends string = ""> = {
  [K in keyof T & string]: T[K] extends string ? `${P}${K}` : Leaves<T[K], `${P}${K}.`>;
}[keyof T & string];

export type MessageKey = Leaves<Messages>;

const catalogs: Record<string, Messages> = { en };

export function t(key: MessageKey, vars?: Record<string, string | number>, locale = "en"): string {
  const catalog = catalogs[locale] ?? en;
  let value: unknown = catalog;
  for (const part of key.split(".")) {
    value = (value as Record<string, unknown> | undefined)?.[part];
  }
  let text = typeof value === "string" ? value : key;
  if (vars) for (const [k, v] of Object.entries(vars)) text = text.replaceAll(`{${k}}`, String(v));
  return text;
}
