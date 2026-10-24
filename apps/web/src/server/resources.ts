import { resolve } from "node:path";
import { loadResources, type ResourceCatalog } from "@allmaths/content-schema";

/** Folder with resources.yaml and files/. RESOURCES_DIR must point to a writable, persistent disk in production (uploads are stored there). */
export function resourcesDir(): string {
  const root = resolve(process.cwd(), "..", "..");
  return process.env.RESOURCES_DIR ?? resolve(root, "resources");
}

/** The catalogue is small and read on each request, so a new file or a permission change shows up without a restart. */
export function getResourceCatalog(): ResourceCatalog {
  return loadResources(resourcesDir());
}

/**
 * The course whose documents this user may see: a student sees only the documents of the course they follow, so a learner of Probability
 * does not get the documents of Calculus. Staff (any other role) see all courses. Returns "all", a course id, or null when a student has not chosen a course.
 */
export async function resourceScope(user: { id: string; role: string }): Promise<"all" | string | null> {
  if (user.role !== "student") return "all";
  const { getServices } = await import("./runtime");
  const { getEnrolledCourseId } = await import("@allmaths/server");
  const { db } = await getServices();
  return getEnrolledCourseId(db, user.id);
}
