# User Guide

PulseBoard has three roles. What you can do depends on which one you have —
your administrator assigns this when creating your account.

| Role | Can view | Can edit |
|---|---|---|
| **Executive** | Portfolio summaries, drill-down into any project | Nothing — read-only by design |
| **Member** | Everything an executive sees | Only tasks assigned to them; can report new blockers |
| **Admin** (project manager) | Everything | Projects, tasks (any), blockers (including resolving), budget entries, users |

## Signing in

Go to your PulseBoard URL, enter your email and password, and sign in. If
you've forgotten your password, ask an admin to reset it via `POST
/api/users` (self-service password reset is not included in this initial
release — see [CONTRIBUTING.md](../CONTRIBUTING.md) if you'd like to add it).

## The dashboard

When you sign in, you land on the portfolio dashboard:

- **KPI strip** at the top: total projects, how many are active, at risk, or
  delayed, and the portfolio's overall budget burn.
- **Filter bar**: narrow the table below by stage or timeline health.
- **Top budget burn** chart: the ten projects consuming the largest share of
  their budget.
- **Timeline health** donut: how many projects are on track, at risk, or
  delayed across the whole portfolio.
- **Projects with open blockers**: a quick list of what's stuck and how
  severely.
- **Project table**: every project matching your filters. Click any row to
  drill down into its raw tasks, blockers, and budget entries.

The dashboard updates itself. If a teammate changes a task's status or an
admin resolves a blocker, you'll see it reflected within a second or two —
no need to refresh the page.

## For project managers (admins)

- **Create a project**: use the interactive API docs at `/docs` (Swagger UI)
  under `POST /api/projects`, or ask your team to build a "New Project" form
  in the frontend as a follow-up enhancement — the API already supports it.
- **Update a project's stage**: `PATCH /api/projects/{id}` with the new
  `stage`.
- **Record spend**: `POST /api/budget-entries` with a `label`, `amount`, and
  `incurred_on` date.
- **Resolve a blocker**: `PATCH /api/blockers/{id}` with `resolved: true`.
- **Add a teammate**: `POST /api/users` with their name, email, a temporary
  password, and their role.

## For team members

- Tasks assigned to you show up when you drill into a project. Update your
  own task's status with `PATCH /api/tasks/{id}` — you'll get a `403` if you
  try to edit someone else's task, which is expected: ask that task's
  assignee or your project manager instead.
- You can report a new blocker on any project you're working on
  (`POST /api/blockers`) but only an admin can mark it resolved, so the
  resolution reflects an actual decision, not just the reporter closing
  their own concern.

## For executives

Everything is read-only for you by design — you get the full picture without
any risk of accidentally changing a record you were just reviewing. Use the
dashboard filters and the drill-down view; there's nothing else to learn.

## Getting help

If something looks wrong (a project stuck in the wrong stage, a metric that
doesn't match your expectation), check the drill-down view first — it shows
every raw task, blocker, and budget entry behind the computed numbers. If it
still doesn't add up, that's worth reporting as a bug (see
[CONTRIBUTING.md](../CONTRIBUTING.md#reporting-bugs)).
