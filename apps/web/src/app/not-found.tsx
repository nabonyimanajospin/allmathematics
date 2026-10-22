import Link from "next/link";
import { buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center">
      <h1 className="text-3xl font-extrabold">{t("errors.notFoundTitle")}</h1>
      <p className="mt-3 text-muted">{t("errors.notFound")}</p>
      <Link href="/" className={buttonClass("primary", "mt-8")}>
        {t("errors.back")}
      </Link>
    </div>
  );
}
