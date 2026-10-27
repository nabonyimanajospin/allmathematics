import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { solverAccess } from "@allmaths/server";
import { BackLink } from "@/components/back-link";
import { SolverHub } from "@/components/solver-hub";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { paymentConfig } from "@/server/payments-config";
import { freeSolvesPerDay } from "@/server/solver-config";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("solver.title") };
export const dynamic = "force-dynamic";

export default async function SolverPage({ searchParams }: { searchParams: Promise<{ paid?: string; mode?: string }> }) {
  const { paid, mode } = await searchParams;
  const triangle = mode === "triangle";
  const user = await getCurrentUser();
  if (!user) redirect(`/signin?next=${encodeURIComponent(triangle ? "/solver?mode=triangle" : "/solver")}`);
  const { db } = await getServices();
  const access = await solverAccess(db, user.id, freeSolvesPerDay());
  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <BackLink href="/dashboard">{t("lesson.back")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("solver.title")}</h1>
      <div className="mt-4">
        <SolverHub initialAccess={access} canPay={paymentConfig() !== null} justPaid={paid === "1"} initialMode={triangle ? "triangle" : "problem"} />
      </div>
    </div>
  );
}
