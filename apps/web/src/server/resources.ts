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
