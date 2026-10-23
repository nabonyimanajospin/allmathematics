import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { AuthForm } from "@/components/auth-form";
import { t } from "@/i18n";
import { getCurrentUser, safeNext } from "@/server/session";

export const metadata: Metadata = { title: t("nav.signIn") };

export default async function SignInPage({ searchParams }: { searchParams: Promise<{ next?: string; reset?: string }> }) {
  const params = await searchParams;
  const next = safeNext(params.next);
  if (await getCurrentUser()) redirect(next);
  return <AuthForm mode="signin" next={next} notice={params.reset === "1" ? t("auth.resetDone") : undefined} />;
}
