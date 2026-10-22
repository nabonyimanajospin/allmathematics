import { Skeleton } from "@allmaths/ui";

export default function Loading() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8" aria-busy="true">
      <Skeleton className="h-3 w-full" />
      <Skeleton className="mt-10 h-10 w-3/4" />
      <Skeleton className="mt-6 h-24 w-full" />
      <Skeleton className="mt-8 h-6 w-full" />
      <Skeleton className="mt-3 h-6 w-11/12" />
      <Skeleton className="mt-3 h-6 w-9/12" />
    </div>
  );
}
