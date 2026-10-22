import { statSync } from "node:fs";
import { extname, join } from "node:path";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { isDownloadable } from "@allmaths/content-schema";
import { buttonClass } from "@allmaths/ui";
import { t, type MessageKey } from "@/i18n";
import { getResourceCatalog } from "@/server/resources";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("resources.title") };
export const dynamic = "force-dynamic";

function sizeLabel(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** A page of our own around the document, so the student can read it and go back to the list. */
export default async function ResourceViewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await getCurrentUser();
  if (!user) redirect(`/signin?next=/resources/view/${id}`);
  const catalog = getResourceCatalog();
  const r = catalog.resources.find((x) => x.id === id);
  if (!r || !r.file || !isDownloadable(catalog, r)) notFound();
  const ext = extname(r.file).slice(1).toUpperCase();
  const size = sizeLabel(statSync(join(catalog.filesDir, r.file)).size);
  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <Link href="/resources" className={buttonClass("secondary")}>
        ← {t("resources.back")}
      </Link>
      <div className="mt-5 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted">
            {t(`resources.kind.${r.kind}` as MessageKey)} · {ext} · {size}
          </p>
          <h1 className="mt-1 text-2xl font-extrabold tracking-tight">{r.title}</h1>
          <p className="mt-2 max-w-2xl text-muted">{r.description}</p>
        </div>
        <a href={`/resources/download/${r.id}`} download className={buttonClass("primary")}>
          {t("resources.download")}
        </a>
      </div>
      {ext === "PDF" ? (
        <iframe
          title={r.title}
          src={`/resources/download/${r.id}?inline=1`}
          className="mt-6 h-[80vh] w-full rounded-[var(--radius)] border border-line bg-surface"
        />
      ) : (
        <p className="mt-6 rounded-[var(--radius)] border border-line bg-surface-2 p-4 text-muted">{t("resources.noPreview")}</p>
      )}
    </div>
  );
}
