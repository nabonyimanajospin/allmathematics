import Link from "next/link";
import { can } from "@allmaths/server";
import { Logo, buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";
import { getCurrentUser } from "@/server/session";
import { SignOutButton } from "./sign-out-button";
import { ThemeToggle } from "./theme-toggle";

export async function SiteHeader() {
  const user = await getCurrentUser();
  return (
    <header className="sticky top-0 z-40 h-[var(--header-h)] border-b border-line bg-bg/90 backdrop-blur">
      <div className="mx-auto flex h-full max-w-5xl items-center justify-between gap-3 px-4">
        <Link href={user ? "/dashboard" : "/"} className="rounded-md" aria-label={t("app.name")}>
          <Logo name={t("app.name")} />
        </Link>
        <nav aria-label="Main" className="flex items-center gap-1.5">
          <ThemeToggle />
          {user ? (
            <>
              <span className="hidden sm:block">
                <Link href="/dashboard" className={buttonClass("ghost")}>
                  {t("nav.dashboard")}
                </Link>
              </span>
              <span className="hidden sm:block">
                <Link href="/formulas" className={buttonClass("ghost")}>
                  {t("nav.formulas")}
                </Link>
              </span>
              <Link href="/resources" className={buttonClass("ghost")}>
                {t("nav.resources")}
              </Link>
              {can(user.role, "users:manage") ? (
                <Link href="/admin" className={buttonClass("ghost")}>
                  {t("nav.admin")}
                </Link>
              ) : null}
              <SignOutButton />
            </>
          ) : (
            <>
              <Link href="/signin" className={buttonClass("ghost")}>
                {t("nav.signIn")}
              </Link>
              <span className="hidden sm:block">
                <Link href="/signup" className={buttonClass("primary")}>
                  {t("nav.signUp")}
                </Link>
              </span>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
