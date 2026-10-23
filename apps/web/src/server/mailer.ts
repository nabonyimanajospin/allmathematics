import { RESET_CODE_MINUTES } from "@allmaths/server";

/**
 * Sends the password reset code. With RESEND_API_KEY and MAIL_FROM set it uses Resend (spec section 4);
 * without them (development) the code is printed in the server console and nothing leaves the machine.
 */
export async function sendResetCode(to: string, name: string, code: string): Promise<void> {
  const key = process.env.RESEND_API_KEY;
  const from = process.env.MAIL_FROM;
  if (!key || !from) {
    if (process.env.NODE_ENV === "production") throw new Error("RESEND_API_KEY and MAIL_FROM are required to send e-mail in production");
    console.log(`[mail:dev] password reset code for ${to}: ${code} (valid ${RESET_CODE_MINUTES} minutes)`);
    return;
  }
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { authorization: `Bearer ${key}`, "content-type": "application/json" },
    body: JSON.stringify({
      from,
      to,
      subject: "Your Allmaths password reset code",
      text: `Hello ${name},\n\nYour password reset code is ${code}.\nIt is valid for ${RESET_CODE_MINUTES} minutes. If you did not ask for it, ignore this message; your password has not changed.\n\nAllmaths`,
    }),
  });
  if (!res.ok) throw new Error(`mail provider answered ${res.status}`);
}
