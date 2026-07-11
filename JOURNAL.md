# JOURNAL — 26.SUM.B.6 pod portfolio

> Dated log of decisions and notes. Reverse-chronological; one paragraph max.

## 2026-07-11 — MySQL-backed timeline #decision

Week 4 calls for a public timeline (peewee + MySQL) added to the existing routes.
Kept the connection and the TimelinePost model directly in app/__init__.py
instead of splitting into a models.py: the assignment's own deliverable links
straight to that file, and grading expects the MySQL wiring to be visible
there. Local dev uses the exact myportfolio/mypassword credentials from the
assignment; the VPS gets its own generated password in a gitignored .env
instead, since that box sits on the open internet. Also added a MySQL service
container to CI, since the app now connects to a database at import time and
the smoke suite would otherwise fail on every PR.

## 2026-06-17 — CI + contributor onboarding #decision

Added a GitHub Actions workflow (ruff + a pytest smoke suite over every route)
so PRs are gated before teammates start pushing. The smoke test loops over all
`MEMBERS`, so a malformed entry fails CI instead of breaking the site. Wrote a
CONTRIBUTING guide whose first task is "add yourself to the fleet."

## 2026-06-17 — Built it as a team "fleet" #decision

Task 2 is a team project, so the site is a fleet: the pod is the landing page
and each teammate is a service with their own `/u/<handle>` page. Everything is
data — adding a member is one dict in `app/data.py` plus a photo, and the menu
bar + their page appear automatically. No template edits.

## 2026-06-17 — Kept the design a believable upgrade of the template #decision

Went minimalist on purpose: white canvas, one deep-blue accent (the template's
own blue, deepened), Inter, plain section names, and a slim MLH Fellowship
ribbon up top. The point was a tasteful, hand-crafted upgrade of the starter —
not an elaborate themed site.
