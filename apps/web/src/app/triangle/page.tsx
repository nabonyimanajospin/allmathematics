import { redirect } from "next/navigation";

/** The triangle toolkit lives in the Solver (the tab "A triangle (three vertices)"); this address keeps old links working. */
export default function TrianglePage(): never {
  redirect("/solver?mode=triangle");
}
