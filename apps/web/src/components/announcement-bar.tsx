import { listAnnouncements, type AnnouncementRow } from "@allmaths/server";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

/** The active announcements of the administrators, shown under the header to every signed-in user. A failure here never breaks the page. */
export async function AnnouncementBar() {
  const user = await getCurrentUser();
  if (!user) return null;
  let rows: AnnouncementRow[] = [];
  try {
    const { db } = await getServices();
    rows = await listAnnouncements(db, { onlyActive: true });
  } catch {
    return null;
  }
  if (rows.length === 0) return null;
  return (
    <section aria-label={t("announcements.label")} className="border-b border-line bg-accent-soft">
      <ul className="mx-auto grid max-w-5xl gap-1 px-4 py-2 text-sm font-medium">
        {rows.slice(0, 3).map((r) => (
          <li key={r.id} className="whitespace-pre-wrap break-words">
            <span aria-hidden="true">📢 </span>
            {r.message}
          </li>
        ))}
      </ul>
    </section>
  );
}
