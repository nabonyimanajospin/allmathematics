import type { Metadata, Viewport } from "next";
import Script from "next/script";
import type { ReactNode } from "react";
import "katex/dist/katex.min.css";
import "./globals.css";
import { AnnouncementBar } from "@/components/announcement-bar";
import { FeedbackLink } from "@/components/feedback-link";
import { SiteHeader } from "@/components/site-header";
import { t } from "@/i18n";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = {
  title: { default: `${t("app.name")}: ${t("app.tagline")}`, template: `%s · ${t("app.name")}` },
  description: t("home.lead"),
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#ffffff",
};

/** Applies the saved theme before first paint so there is no flash of the wrong theme. Without a saved theme the page stays light. */
const themeScript = `try{var m=localStorage.getItem("allmaths-theme"),r=document.documentElement;if(m==="dark")r.setAttribute("data-theme",m);else if(m==="system")r.removeAttribute("data-theme")}catch(e){}`;

export default async function RootLayout({ children }: { children: ReactNode }) {
  const signedIn = (await getCurrentUser()) !== null;
  return (
    <html lang="en" data-theme="light" suppressHydrationWarning>
      <body className="min-h-dvh">
        <Script id="theme-init" strategy="beforeInteractive" dangerouslySetInnerHTML={{ __html: themeScript }} />
        <a href="#main" className="skip-link">
          {t("nav.skip")}
        </a>
        <SiteHeader />
        <AnnouncementBar />
        <main id="main" tabIndex={-1} className="outline-none">
          {children}
        </main>
        <footer className="mx-auto mt-16 max-w-5xl px-4 pb-10 text-sm text-muted">
          {t("footer.rights", { year: new Date().getFullYear() })}
          {signedIn ? (
            <>
              {" · "}
              <FeedbackLink />
            </>
          ) : null}
        </footer>
      </body>
    </html>
  );
}
