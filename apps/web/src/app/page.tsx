import Link from "next/link";
import { Card, buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export default async function HomePage() {
  const [user, { store }] = await Promise.all([getCurrentUser(), getServices()]);
  const features = [
    { title: t("home.feature1Title"), text: t("home.feature1Text") },
    { title: t("home.feature2Title"), text: t("home.feature2Text") },
    { title: t("home.feature3Title"), text: t("home.feature3Text") },
  ];
  return (
    <div className="mx-auto max-w-5xl px-4">
      <section className="py-14 sm:py-20">
        <h1 className="max-w-3xl text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">{t("home.title")}</h1>
        <p className="mt-5 max-w-2xl text-lg text-muted">{t("home.lead")}</p>
        <div className="mt-8 flex flex-wrap items-center gap-4">
          <Link href={user ? "/dashboard" : "/signup"} className={buttonClass("primary", "px-6 text-base")}>
            {user ? t("home.ctaSignedIn") : t("home.cta")}
          </Link>
          <p className="text-sm font-medium text-success">{t("home.free")}</p>
        </div>
      </section>

      <section aria-labelledby="features" className="grid gap-4 sm:grid-cols-3">
        <h2 id="features" className="sr-only">
          {t("app.name")}
        </h2>
        {features.map((f) => (
          <Card key={f.title}>
            <h3 className="text-lg font-bold">{f.title}</h3>
            <p className="mt-2 text-muted">{f.text}</p>
          </Card>
        ))}
      </section>

      <section aria-labelledby="courses" className="mt-14">
        <h2 id="courses" className="text-2xl font-bold tracking-tight">
          {t("home.courses")}
        </h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          {store.courses.map((c) => (
            <Card key={c.meta.id}>
              <h3 className="text-xl font-bold">{c.meta.title}</h3>
              <p className="mt-2 text-muted">{c.meta.description}</p>
              <ul className="mt-4 grid gap-1 text-sm">
                {c.modules.map((m) => (
                  <li key={m.meta.id} className="flex items-center justify-between gap-3 border-t border-line pt-1.5">
                    <span>
                      {t("dashboard.module")} {m.meta.order}: {m.meta.title}
                    </span>
                    {m.meta.free ? (
                      <span className="rounded-full bg-success-soft px-2 py-0.5 text-xs font-semibold text-success">{t("dashboard.free")}</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
