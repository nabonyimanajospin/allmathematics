CREATE TABLE "unit_test_attempts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"unit_id" text NOT NULL,
	"questions" jsonb NOT NULL,
	"answers" jsonb,
	"score" integer,
	"passed" boolean DEFAULT false NOT NULL,
	"started_at" timestamp with time zone DEFAULT now() NOT NULL,
	"submitted_at" timestamp with time zone
);
--> statement-breakpoint
ALTER TABLE "unit_test_attempts" ADD CONSTRAINT "unit_test_attempts_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "unit_test_attempts_user_unit_idx" ON "unit_test_attempts" USING btree ("user_id","unit_id");