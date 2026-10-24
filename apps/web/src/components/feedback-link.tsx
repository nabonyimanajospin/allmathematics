"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { t } from "@/i18n";

/** A link in the footer to the feedback form; it carries the page the learner is on, so that a report names the lesson. */
export function FeedbackLink() {
  const path = usePathname();
  const href = path && !path.startsWith("/feedback") ? `/feedback?page=${encodeURIComponent(path)}` : "/feedback";
  return (
    <Link href={href} className="font-semibold text-accent underline underline-offset-2">
      {t("feedback.link")}
    </Link>
  );
}
