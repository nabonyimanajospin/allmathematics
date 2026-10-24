import Link from "next/link";
import { feedbackCounts } from "@allmaths/server";
import { buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";

const ITEMS = [
  { href: "/admin", key: "overview" },
  { href: "/admin/users", key: "users" },
  { href: "/admin/feedback", key: "feedback" },
  { href: "/admin/announcements", key: "announcements" },
  { href: "/admin/resources", key: "resources" },
  { href: "/admin/audit", key: "audit" },
] as const;

/** The menu of the administration pages; the number of new messages from learners is shown on Feedback. */
export async function AdminNav({ current }: { current: (typeof ITEMS)[number]["key"] }) {
  const { db } = await getServices();
  const fresh = (await feedbackCounts(db)).new;
  return (
    <nav aria-label="Administration" className="mb-6 flex flex-wrap gap-2">
      {ITEMS.map((i) => (
        <Link key={i.key} href={i.href} aria-current={i.key === current ? "page" : undefined} className={buttonClass(i.key === current ? "primary" : "secondary")}>
          {t(`admin.nav.${i.key}`)}
          {i.key === "feedback" && fresh > 0 ? <span className="ml-1 rounded-full bg-danger px-2 text-xs font-bold text-white">{fresh}</span> : null}
        </Link>
      ))}
    </nav>
  );
}
