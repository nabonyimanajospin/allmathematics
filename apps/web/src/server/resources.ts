import { resolve } from "node:path";
import { loadResources, type ResourceCatalog } from "@allmaths/content-schema";

/** The catalogue is small and read on each request, so a new file or a permission change shows up without a restart. */
export function getResourceCatalog(): ResourceCatalog {
  const root = resolve(process.cwd(), "..", "..");
  return loadResources(process.env.RESOURCES_DIR ?? resolve(root, "resources"));
}
