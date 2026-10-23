import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { ForgotForm } from "@/components/forgot-form";
import { t } from "@/i18n";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("auth.forgotTitle") };

export default async function ForgotPasswordPage() {
  if (await getCurrentUser()) redirect("/dashboard");
  return <ForgotForm />;
}
