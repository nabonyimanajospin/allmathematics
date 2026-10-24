# Administration

The administrator's pages are under **Admin** in the header (only accounts with the role `admin` see them; for everybody else they do not exist).

## Making the first administrator

Put the e-mail of the owner in the server setting `ADMIN_EMAILS` (several e-mails are separated by commas) **before** starting the website, then **sign up** on the site with that e-mail.
That account is created as an administrator. Example (PowerShell):

```powershell
$env:ADMIN_EMAILS = "owner@example.com"
pnpm dev
```

With `pnpm seed` the demo administrator `admin@allmaths.test` exists too (development only). In production, sign up with your e-mail first, then remove or keep the setting:
it only decides the role of a **new** account; another administrator can be made later by an administrator in **Users** (change the role).

## What an administrator can do

| Page | What it is for |
|---|---|
| **Overview** | Number of accounts, new and active learners, suspended accounts, and for every course how many learners entered and how many completed it. A link downloads the list of accounts as CSV. |
| **Users** | Find an account by name or e-mail; reset its password (a temporary password is shown once and all sessions end); suspend or restore it; change its role; give or remove Premium. You cannot suspend or demote yourself. |
| **Feedback** | What learners wrote: problems, ideas, questions, mistakes in a lesson (with the page they were on). Filter by new, read or resolved; keep a private note; delete. The number of new messages is shown on the menu. |
| **Announcements** | A short message shown under the header to every signed-in learner (for example the date of a test) until you hide or delete it. |
| **Resources** | Upload and remove documents of a course. A learner sees only the documents of the course they follow. |
| **Audit log** | Everything an administrator did (resets, suspensions, role changes, uploads, feedback decisions, exports), newest first. |

## What a learner sees

- **Feedback** in the footer of every page (it remembers the page, so a report about a lesson names the lesson). A few messages per ten minutes.
- The announcements of the administrators under the header.
- Only the **Resources** of the course they follow.
