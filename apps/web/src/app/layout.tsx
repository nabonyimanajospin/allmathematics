import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "katex/dist/katex.min.css";
import "./globals.css";
import { SiteHeader } from "@/components/site-header";
import { t } from "@/i18n";

export const metadata: Metadata = {
  title: { default: `${t("app.name")}: ${t("app.tagline")}`, template: `%s · ${t("app.name")}` },
  description: t("home.lead"),
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fbfbf9" },
    { media: "(prefers-color-scheme: dark)", color: "#10151c" },
  ],
};

/** Applies the saved theme before first paint so there is no flash of the wrong theme. */
const themeScript = `try{var m=localStorage.getItem("allmaths-theme");if(m==="light"||m==="dark")document.documentElement.setAttribute("data-theme",m)}catch(e){}`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-dvh">
        <a href="#main" className="skip-link">
          {t("nav.skip")}
        </a>
        <SiteHeader />
        <main id="main" tabIndex={-1} className="outline-none">
          {children}
        </main>
        <footer className="mx-auto mt-16 max-w-5xl px-4 pb-10 text-sm text-muted">
          {t("footer.rights", { year: new Date().getFullYear() })}
        </footer>
      </body>
    </html>
  );
}
