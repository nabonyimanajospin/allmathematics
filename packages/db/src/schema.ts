/**
 * Database schema (spec section 11). Every change goes through a migration (drizzle-kit generate).
 * Content tables (courses..sections) use the stable text ids of the content files (geo-m01-u01-l01).
 * `events` is append-only; `section_progress` and `progress` are derived from events on the server.
 */

import { sql } from "drizzle-orm";
import {
  bigint,
  boolean,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  primaryKey,
  real,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core";

export const ROLES = ["student", "instructor", "content_author", "reviewer", "admin"] as const;
export type Role = (typeof ROLES)[number];

export const roleEnum = pgEnum("role", ROLES);
export const contentStatusEnum = pgEnum("content_status", ["draft", "in_review", "verified", "published", "archived"]);
export const verbEnum = pgEnum("verb", [
  "started",
  "viewed",
  "completed",
  "attempted",
  "answered",
  "hinted",
  "revealed_solution",
  "passed",
  "failed",
  "bookmarked",
  "resumed",
]);
export const providerEnum = pgEnum("payment_provider", ["stripe", "flutterwave"]);

const createdAt = () => timestamp("created_at", { withTimezone: true }).notNull().defaultNow();

// --- identity -----------------------------------------------------------------------------------------
export const users = pgTable(
  "users",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    email: text("email").notNull(),
    name: text("name").notNull(),
    role: roleEnum("role").notNull().default("student"),
    locale: text("locale").notNull().default("en"),
    passwordHash: text("password_hash"),
    emailVerifiedAt: timestamp("email_verified_at", { withTimezone: true }),
    suspendedAt: timestamp("suspended_at", { withTimezone: true }),
    deletedAt: timestamp("deleted_at", { withTimezone: true }),
    createdAt: createdAt(),
  },
  (t) => [uniqueIndex("users_email_lower_idx").on(sql`lower(${t.email})`)],
);

export const sessions = pgTable(
  "sessions",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    /** SHA-256 of the session token; the token itself is only in the cookie. */
    tokenHash: text("token_hash").notNull().unique(),
    expiresAt: timestamp("expires_at", { withTimezone: true }).notNull(),
    createdAt: createdAt(),
    lastSeenAt: timestamp("last_seen_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index("sessions_user_idx").on(t.userId)],
);

// --- content ------------------------------------------------------------------------------------------
export const courses = pgTable("courses", {
  id: text("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  title: text("title").notNull(),
  description: text("description").notNull().default(""),
  order: integer("order").notNull(),
  /** Price in US cents; null = not for sale yet. */
  priceUsdCents: integer("price_usd_cents"),
  status: contentStatusEnum("status").notNull().default("draft"),
});

export const modules = pgTable(
  "modules",
  {
    id: text("id").primaryKey(),
    courseId: text("course_id")
      .notNull()
      .references(() => courses.id, { onDelete: "cascade" }),
    order: integer("order").notNull(),
    title: text("title").notNull(),
    description: text("description").notNull().default(""),
    free: boolean("free").notNull().default(false),
  },
  (t) => [index("modules_course_idx").on(t.courseId)],
);

export const units = pgTable(
  "units",
  {
    id: text("id").primaryKey(),
    moduleId: text("module_id")
      .notNull()
      .references(() => modules.id, { onDelete: "cascade" }),
    order: integer("order").notNull(),
    title: text("title").notNull(),
  },
  (t) => [index("units_module_idx").on(t.moduleId)],
);

export const lessons = pgTable(
  "lessons",
  {
    id: text("id").primaryKey(),
    unitId: text("unit_id")
      .notNull()
      .references(() => units.id, { onDelete: "cascade" }),
    order: integer("order").notNull(),
    title: text("title").notNull(),
    estMinutes: integer("est_minutes").notNull(),
    version: integer("version").notNull().default(1),
    status: contentStatusEnum("status").notNull().default("draft"),
    /** Hash of the lesson file; changes when the content changes. */
    contentHash: text("content_hash").notNull().default(""),
    /** Phase 2 components; before they exist the progress formula ignores their weight. */
    hasPractice: boolean("has_practice").notNull().default(false),
    hasQuiz: boolean("has_quiz").notNull().default(false),
  },
  (t) => [index("lessons_unit_idx").on(t.unitId)],
);

export const sections = pgTable(
  "sections",
  {
    id: text("id").primaryKey(),
    lessonId: text("lesson_id")
      .notNull()
      .references(() => lessons.id, { onDelete: "cascade" }),
    order: integer("order").notNull(),
    type: text("type").notNull(),
    /** Minimum active seconds; null means the default for the block type. */
    minSeconds: integer("min_seconds"),
    contentJson: jsonb("content_json").notNull(),
  },
  (t) => [index("sections_lesson_idx").on(t.lessonId, t.order)],
);

export const skills = pgTable("skills", {
  id: text("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  title: text("title").notNull(),
  moduleId: text("module_id").references(() => modules.id, { onDelete: "set null" }),
});

// --- problems and assessment --------------------------------------------------------------------------
export const problemTemplates = pgTable("problem_templates", {
  id: text("id").primaryKey(),
  lessonId: text("lesson_id").references(() => lessons.id, { onDelete: "cascade" }),
  difficulty: integer("difficulty").notNull(),
  specYaml: text("spec_yaml").notNull(),
  version: integer("version").notNull().default(1),
  status: contentStatusEnum("status").notNull().default("draft"),
});

export const templateSkills = pgTable(
  "template_skills",
  {
    templateId: text("template_id")
      .notNull()
      .references(() => problemTemplates.id, { onDelete: "cascade" }),
    skillId: text("skill_id")
      .notNull()
      .references(() => skills.id, { onDelete: "cascade" }),
  },
  (t) => [primaryKey({ columns: [t.templateId, t.skillId] })],
);

export const problemInstances = pgTable(
  "problem_instances",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    templateId: text("template_id")
      .notNull()
      .references(() => problemTemplates.id, { onDelete: "cascade" }),
    seed: bigint("seed", { mode: "bigint" }).notNull(),
    paramsJson: jsonb("params_json").notNull(),
    /** Server-side only. Never sent to the browser before submission. */
    answerJson: jsonb("answer_json").notNull(),
  },
  (t) => [uniqueIndex("problem_instances_seed_idx").on(t.templateId, t.seed)],
);

export const assessments = pgTable("assessments", {
  id: uuid("id").primaryKey().defaultRandom(),
  type: text("type").notNull(),
  scopeId: text("scope_id").notNull(),
  settingsJson: jsonb("settings_json").notNull().default({}),
});

export const attempts = pgTable(
  "attempts",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    assessmentId: uuid("assessment_id")
      .notNull()
      .references(() => assessments.id, { onDelete: "cascade" }),
    startedAt: timestamp("started_at", { withTimezone: true }).notNull().defaultNow(),
    submittedAt: timestamp("submitted_at", { withTimezone: true }),
    score: integer("score"),
    maxScore: integer("max_score"),
  },
  (t) => [index("attempts_user_idx").on(t.userId)],
);

export const responses = pgTable(
  "responses",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    attemptId: uuid("attempt_id")
      .notNull()
      .references(() => attempts.id, { onDelete: "cascade" }),
    instanceId: uuid("instance_id")
      .notNull()
      .references(() => problemInstances.id, { onDelete: "cascade" }),
    answerLatex: text("answer_latex").notNull(),
    correct: boolean("correct").notNull(),
    points: integer("points").notNull().default(0),
    hintsUsed: integer("hints_used").notNull().default(0),
    durationMs: integer("duration_ms").notNull().default(0),
  },
  (t) => [index("responses_attempt_idx").on(t.attemptId)],
);

// --- learning events and progress ---------------------------------------------------------------------
/** Append-only. `id` is the client-generated UUID, so a re-delivered event is stored once. */
export const events = pgTable(
  "events",
  {
    id: uuid("id").primaryKey(),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    verb: verbEnum("verb").notNull(),
    objectType: text("object_type").notNull(),
    objectId: text("object_id").notNull(),
    lessonId: text("lesson_id"),
    sectionId: text("section_id"),
    resultJson: jsonb("result_json"),
    ts: timestamp("ts", { withTimezone: true }).notNull().defaultNow(),
    clientTs: timestamp("client_ts", { withTimezone: true }),
    device: text("device"),
  },
  (t) => [index("events_user_lesson_idx").on(t.userId, t.lessonId, t.ts), index("events_user_ts_idx").on(t.userId, t.ts)],
);

/** Per section: how much credited active time, and when it was completed. */
export const sectionProgress = pgTable(
  "section_progress",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    sectionId: text("section_id")
      .notNull()
      .references(() => sections.id, { onDelete: "cascade" }),
    lessonId: text("lesson_id")
      .notNull()
      .references(() => lessons.id, { onDelete: "cascade" }),
    activeMs: integer("active_ms").notNull().default(0),
    /** Server time of the last `started` event for this section; bounds the credited duration. */
    openedAt: timestamp("opened_at", { withTimezone: true }),
    checkAnsweredCorrectly: boolean("check_answered_correctly").notNull().default(false),
    hintsUsed: integer("hints_used").notNull().default(0),
    completedAt: timestamp("completed_at", { withTimezone: true }),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [primaryKey({ columns: [t.userId, t.sectionId] }), index("section_progress_lesson_idx").on(t.userId, t.lessonId)],
);

/** Materialized progress as an exact fraction (num/den); `percent` is the whole-number display value. */
export const progress = pgTable(
  "progress",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    objectType: text("object_type").notNull(), // lesson | unit | module | course
    objectId: text("object_id").notNull(),
    num: bigint("num", { mode: "bigint" }).notNull(),
    den: bigint("den", { mode: "bigint" }).notNull(),
    percent: integer("percent").notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [primaryKey({ columns: [t.userId, t.objectType, t.objectId] })],
);

export const mastery = pgTable(
  "mastery",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    skillId: text("skill_id")
      .notNull()
      .references(() => skills.id, { onDelete: "cascade" }),
    value: real("value").notNull().default(0),
    level: text("level").notNull().default("not_started"),
    lastPracticedAt: timestamp("last_practiced_at", { withTimezone: true }),
  },
  (t) => [primaryKey({ columns: [t.userId, t.skillId] })],
);

// --- commerce -----------------------------------------------------------------------------------------
export const enrollments = pgTable(
  "enrollments",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    courseId: text("course_id")
      .notNull()
      .references(() => courses.id, { onDelete: "cascade" }),
    source: text("source").notNull(), // free | purchase | subscription | class | admin
    startedAt: timestamp("started_at", { withTimezone: true }).notNull().defaultNow(),
    expiresAt: timestamp("expires_at", { withTimezone: true }),
  },
  (t) => [primaryKey({ columns: [t.userId, t.courseId] })],
);

export const subscriptions = pgTable("subscriptions", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  provider: providerEnum("provider").notNull(),
  status: text("status").notNull(),
  plan: text("plan").notNull(),
  currentPeriodEnd: timestamp("current_period_end", { withTimezone: true }),
});

export const payments = pgTable("payments", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  provider: providerEnum("provider").notNull(),
  /** Minor units (cents for USD, whole francs for RWF). */
  amount: bigint("amount", { mode: "bigint" }).notNull(),
  currency: text("currency").notNull(),
  status: text("status").notNull(),
  providerRef: text("provider_ref").notNull(),
  createdAt: createdAt(),
}, (t) => [uniqueIndex("payments_provider_ref_idx").on(t.provider, t.providerRef)]);

// --- classes ------------------------------------------------------------------------------------------
export const classes = pgTable("classes", {
  id: uuid("id").primaryKey().defaultRandom(),
  instructorId: uuid("instructor_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  courseId: text("course_id")
    .notNull()
    .references(() => courses.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  joinCode: text("join_code").notNull().unique(),
});

export const classMembers = pgTable(
  "class_members",
  {
    classId: uuid("class_id")
      .notNull()
      .references(() => classes.id, { onDelete: "cascade" }),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
  },
  (t) => [primaryKey({ columns: [t.classId, t.userId] })],
);

export const assignments = pgTable("assignments", {
  id: uuid("id").primaryKey().defaultRandom(),
  classId: uuid("class_id")
    .notNull()
    .references(() => classes.id, { onDelete: "cascade" }),
  assessmentId: uuid("assessment_id").references(() => assessments.id, { onDelete: "cascade" }),
  lessonId: text("lesson_id").references(() => lessons.id, { onDelete: "cascade" }),
  dueAt: timestamp("due_at", { withTimezone: true }),
});

// --- community ----------------------------------------------------------------------------------------
export const forumThreads = pgTable("forum_threads", {
  id: uuid("id").primaryKey().defaultRandom(),
  lessonId: text("lesson_id")
    .notNull()
    .references(() => lessons.id, { onDelete: "cascade" }),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  body: text("body").notNull(),
  status: text("status").notNull().default("open"),
  createdAt: createdAt(),
});

export const forumPosts = pgTable("forum_posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  threadId: uuid("thread_id")
    .notNull()
    .references(() => forumThreads.id, { onDelete: "cascade" }),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  body: text("body").notNull(),
  isAccepted: boolean("is_accepted").notNull().default(false),
  isVerified: boolean("is_verified").notNull().default(false),
  createdAt: createdAt(),
});

export const notes = pgTable("notes", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  sectionId: text("section_id")
    .notNull()
    .references(() => sections.id, { onDelete: "cascade" }),
  body: text("body").notNull(),
});

export const bookmarks = pgTable(
  "bookmarks",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    sectionId: text("section_id")
      .notNull()
      .references(() => sections.id, { onDelete: "cascade" }),
  },
  (t) => [primaryKey({ columns: [t.userId, t.sectionId] })],
);

export const certificates = pgTable("certificates", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  courseId: text("course_id")
    .notNull()
    .references(() => courses.id, { onDelete: "cascade" }),
  issuedAt: timestamp("issued_at", { withTimezone: true }).notNull().defaultNow(),
  verifyCode: text("verify_code").notNull().unique(),
});

export const auditLog = pgTable("audit_log", {
  id: uuid("id").primaryKey().defaultRandom(),
  actorId: uuid("actor_id").references(() => users.id, { onDelete: "set null" }),
  action: text("action").notNull(),
  target: text("target"),
  ts: timestamp("ts", { withTimezone: true }).notNull().defaultNow(),
});
