import Link from "next/link";

/** A clear way back, always to a fixed place so it works after a reload or from a shared link. */
export function BackLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link href={href} className="mb-4 inline-flex min-h-11 items-center gap-1 rounded-md text-sm font-semibold text-accent hover:underline">
      <span aria-hidden="true">←</span> {children}
    </Link>
  );
}
