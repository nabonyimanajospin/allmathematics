ALTER TYPE "public"."payment_provider" ADD VALUE 'manual';--> statement-breakpoint
CREATE TABLE "solver_requests" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"operation" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "solver_requests" ADD CONSTRAINT "solver_requests_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "solver_requests_user_idx" ON "solver_requests" USING btree ("user_id","created_at");