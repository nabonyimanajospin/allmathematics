import type { Role } from "@allmaths/db";
import { Errors } from "../errors";

/** Permissions are checked on the server for every request (spec section 13). */
export const PERMISSIONS = {
  "lesson:learn": ["student", "instructor", "content_author", "reviewer", "admin"],
  "class:manage": ["instructor", "admin"],
  "analytics:view": ["instructor", "admin"],
  "content:write": ["content_author", "admin"],
  "content:review": ["reviewer", "admin"],
  "users:manage": ["admin"],
  "audit:view": ["admin"],
} as const satisfies Record<string, readonly Role[]>;

export type Permission = keyof typeof PERMISSIONS;

export function can(role: Role, permission: Permission): boolean {
  return (PERMISSIONS[permission] as readonly Role[]).includes(role);
}

export function requirePermission(role: Role, permission: Permission): void {
  if (!can(role, permission)) throw Errors.forbidden();
}
