/** What learners send to the administrators (feedback), the announcements shown to learners, and the audit log. */

import { and, count, desc, eq, isNull } from "drizzle-orm";
import { FEEDBACK_CATEGORIES, FEEDBACK_STATUSES, schema, type AppDb, type FeedbackCategory, type FeedbackStatus } from "@allmaths/db";
import { Errors } from "../errors";

export const FEEDBACK_MAX = 2000;

export interface FeedbackInput {
  category: string;
  message: string;
  page?: string | null;
}

/** Stores a message from a learner. Returns its id. */
export async function submitFeedback(db: AppDb, userId: string, input: FeedbackInput): Promise<string> {
  const category = FEEDBACK_CATEGORIES.find((c) => c === input.category);
  if (!category) throw Errors.badRequest("Choose what your message is about.", "invalid_category");
  const message = input.message.trim();
  if (message.length < 5) throw Errors.badRequest("Write a few words so that we can understand you.", "message_too_short");
  if (message.length > FEEDBACK_MAX) throw Errors.badRequest(`Please keep your message under ${FEEDBACK_MAX} characters.`, "message_too_long");
  const page = input.page && /^\/[A-Za-z0-9\-_/.]{0,198}$/.test(input.page) ? input.page : null;
  const [row] = await db.insert(schema.feedback).values({ userId, category, message, page }).returning({ id: schema.feedback.id });
  if (!row) throw new Error("insert returned no row");
  return row.id;
}

export interface FeedbackRow {
  id: string;
  category: FeedbackCategory;
  message: string;
  page: string | null;
  status: FeedbackStatus;
  adminNote: string | null;
  createdAt: Date;
  userName: string | null;
  userEmail: string | null;
}

export async function listFeedback(db: AppDb, opts: { status?: FeedbackStatus; limit?: number } = {}): Promise<FeedbackRow[]> {
  const rows = await db
    .select({
      id: schema.feedback.id,
      category: schema.feedback.category,
      message: schema.feedback.message,
      page: schema.feedback.page,
      status: schema.feedback.status,
      adminNote: schema.feedback.adminNote,
      createdAt: schema.feedback.createdAt,
      userName: schema.users.name,
      userEmail: schema.users.email,
    })
    .from(schema.feedback)
    .leftJoin(schema.users, eq(schema.users.id, schema.feedback.userId))
    .where(opts.status ? eq(schema.feedback.status, opts.status) : undefined)
    .orderBy(desc(schema.feedback.createdAt))
    .limit(Math.min(opts.limit ?? 100, 300));
  return rows.map((r) => ({
    ...r,
    category: (FEEDBACK_CATEGORIES.find((c) => c === r.category) ?? "other") as FeedbackCategory,
    status: (FEEDBACK_STATUSES.find((s) => s === r.status) ?? "new") as FeedbackStatus,
  }));
}

export async function feedbackCounts(db: AppDb): Promise<Record<FeedbackStatus, number>> {
  const rows = await db.select({ status: schema.feedback.status, n: count() }).from(schema.feedback).groupBy(schema.feedback.status);
  const out: Record<FeedbackStatus, number> = { new: 0, read: 0, resolved: 0 };
  for (const r of rows) if ((FEEDBACK_STATUSES as readonly string[]).includes(r.status)) out[r.status as FeedbackStatus] = r.n;
  return out;
}

async function audit(db: AppDb, actorId: string, action: string, target: string): Promise<void> {
  await db.insert(schema.auditLog).values({ actorId, action, target });
}

export async function setFeedbackStatus(db: AppDb, actorId: string, id: string, status: string, note?: string | null): Promise<void> {
  const next = FEEDBACK_STATUSES.find((s) => s === status);
  if (!next) throw Errors.badRequest("Unknown status.", "invalid_status");
  const adminNote = note === undefined ? undefined : note === null || note.trim() === "" ? null : note.trim().slice(0, 1000);
  const updated = await db
    .update(schema.feedback)
    .set({ status: next, updatedAt: new Date(), ...(adminNote !== undefined ? { adminNote } : {}) })
    .where(eq(schema.feedback.id, id))
    .returning({ id: schema.feedback.id });
  if (updated.length === 0) throw Errors.notFound("Message not found");
  await audit(db, actorId, `feedback.${next}`, id);
}

export async function deleteFeedback(db: AppDb, actorId: string, id: string): Promise<void> {
  const removed = await db.delete(schema.feedback).where(eq(schema.feedback.id, id)).returning({ id: schema.feedback.id });
  if (removed.length === 0) throw Errors.notFound("Message not found");
  await audit(db, actorId, "feedback.delete", id);
}

// --- announcements -------------------------------------------------------------------------------------------------
export interface AnnouncementRow {
  id: string;
  message: string;
  active: boolean;
  createdAt: Date;
}

export async function listAnnouncements(db: AppDb, opts: { onlyActive?: boolean } = {}): Promise<AnnouncementRow[]> {
  return db
    .select({ id: schema.announcements.id, message: schema.announcements.message, active: schema.announcements.active, createdAt: schema.announcements.createdAt })
    .from(schema.announcements)
    .where(opts.onlyActive ? eq(schema.announcements.active, true) : undefined)
    .orderBy(desc(schema.announcements.createdAt))
    .limit(50);
}

export async function createAnnouncement(db: AppDb, actorId: string, message: string): Promise<string> {
  const text = message.trim();
  if (text.length < 3 || text.length > 500) throw Errors.badRequest("An announcement is 3 to 500 characters.", "invalid_message");
  const [row] = await db.insert(schema.announcements).values({ authorId: actorId, message: text }).returning({ id: schema.announcements.id });
  if (!row) throw new Error("insert returned no row");
  await audit(db, actorId, "announcement.create", row.id);
  return row.id;
}

export async function setAnnouncementActive(db: AppDb, actorId: string, id: string, active: boolean): Promise<void> {
  const updated = await db.update(schema.announcements).set({ active }).where(eq(schema.announcements.id, id)).returning({ id: schema.announcements.id });
  if (updated.length === 0) throw Errors.notFound("Announcement not found");
  await audit(db, actorId, active ? "announcement.show" : "announcement.hide", id);
}

export async function deleteAnnouncement(db: AppDb, actorId: string, id: string): Promise<void> {
  const removed = await db.delete(schema.announcements).where(eq(schema.announcements.id, id)).returning({ id: schema.announcements.id });
  if (removed.length === 0) throw Errors.notFound("Announcement not found");
  await audit(db, actorId, "announcement.delete", id);
}

// --- audit log -----------------------------------------------------------------------------------------------------
export interface AuditRow {
  id: string;
  action: string;
  target: string | null;
  at: Date;
  actorEmail: string | null;
}

export async function listAudit(db: AppDb, limit = 200): Promise<AuditRow[]> {
  return db
    .select({ id: schema.auditLog.id, action: schema.auditLog.action, target: schema.auditLog.target, at: schema.auditLog.ts, actorEmail: schema.users.email })
    .from(schema.auditLog)
    .leftJoin(schema.users, eq(schema.users.id, schema.auditLog.actorId))
    .orderBy(desc(schema.auditLog.ts))
    .limit(Math.min(limit, 500));
}

/** The accounts as CSV (name, e-mail, role, created, status) for a report. A cell that starts with = + - or @ gets a leading quote so that a spreadsheet does not run it. */
export async function usersCsv(db: AppDb): Promise<string> {
  const rows = await db
    .select({ name: schema.users.name, email: schema.users.email, role: schema.users.role, createdAt: schema.users.createdAt, suspendedAt: schema.users.suspendedAt })
    .from(schema.users)
    .where(and(isNull(schema.users.deletedAt)))
    .orderBy(desc(schema.users.createdAt));
  const cell = (v: string): string => {
    const safe = /^[=+\-@\t\r]/.test(v) ? "'" + v : v;
    return `"${safe.replaceAll('"', '""')}"`;
  };
  const lines = ["name,email,role,created,status", ...rows.map((r) => [cell(r.name), cell(r.email), cell(r.role), cell(r.createdAt.toISOString().slice(0, 10)), cell(r.suspendedAt ? "suspended" : "active")].join(","))];
  return lines.join("\r\n") + "\r\n";
}
