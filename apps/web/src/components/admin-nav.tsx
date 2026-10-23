import Link from "next/link";
import { buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";

const ITEMS = [
  { href: "/admin", key: "overview" },
  { href: "/admin/users", key: "users" },
  { href: "/admin/resources", key: "resources" },
] as const;

export function AdminNav({ current }: { current: (typeof ITEMS)[number]["key"] }) {
  return (
    <nav aria-label="Administration" className="mb-6 flex flex-wrap gap-2">
      {ITEMS.map((i) => (
        <Link key={i.key} href={i.href} aria-current={i.key === current ? "page" : undefined} className={buttonClass(i.key === current ? "primary" : "secondary")}>
          {t(`admin.nav.${i.key}`)}
        </Link>
      ))}
    </nav>
  );
}
