import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { solverAccess } from "@allmaths/server";
import { BackLink } from "@/components/back-link";
import { SolverClient } from "@/components/solver-client";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { freeSolvesPerDay } from "@/server/solver-config";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("solver.title") };
export const dynamic = "force-dynamic";

export default async function SolverPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/solver");
  const { db } = await getServices();
  const access = await solverAccess(db, user.id, freeSolvesPerDay());
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <BackLink href="/dashboard">{t("lesson.back")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("solver.title")}</h1>
      <div className="mt-4">
        <SolverClient initialAccess={access} />
      </div>
    </div>
  );
}
