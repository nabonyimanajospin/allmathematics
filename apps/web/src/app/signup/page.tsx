import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { AuthForm } from "@/components/auth-form";
import { t } from "@/i18n";
import { getCurrentUser, safeNext } from "@/server/session";

export const metadata: Metadata = { title: t("nav.signUp") };

export default async function SignUpPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const next = safeNext((await searchParams).next);
  if (await getCurrentUser()) redirect(next);
  return <AuthForm mode="signup" next={next} />;
}
