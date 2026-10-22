import { Skeleton } from "@allmaths/ui";

export default function Loading() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-8" aria-busy="true">
      <Skeleton className="h-9 w-56" />
      <Skeleton className="mt-6 h-28 w-full" />
      <Skeleton className="mt-10 h-8 w-64" />
      <Skeleton className="mt-4 h-40 w-full" />
    </div>
  );
}
