# JOURNAL — Olayinka Vaughan's portfolio

> Dated log of decisions and notes. Reverse-chronological; one paragraph max.

## 2026-07-20 — Containerized the app with Docker Compose #decision

Week 6 asks for a Dockerfile plus dev/prod `docker-compose.yml` variants:
`myportfolio` (gunicorn, matching how the VPS already serves it) alongside a
`mysql`/mariadb service on a named volume, so timeline data survives `compose
down`. Added a `.dockerignore` too — `.gitignore` only keeps files out of git,
not out of the Docker build context, so without it `COPY . .` would have
baked the local `.env` (real DB credentials) directly into the image layer.
`requirements.txt` was also missing `gunicorn`: it had been installed ad hoc
into the VPS venv for the systemd deploy back in Week 4 but never pinned,
which the Dockerfile build would otherwise have failed on.

## 2026-07-11 — Corrected the team/fleet framing — this is an individual portfolio #decision

Every fellow does their own portfolio; there's no pod-shared repo. The
06-17 decision to build this as a multi-teammate "fleet" (`MEMBERS` list,
`/u/<handle>` per-person routing, a CONTRIBUTING guide centered on "add
yourself to the fleet" and teammate PR review) was wrong from the start —
built on an assumption that was never checked against how the fellowship
actually runs. Collapsed `MEMBERS` down to a single `PROFILE` dict, `/` now
renders the profile directly instead of a list-of-one, dropped the `/u/<handle>`
route and the `member`/`fleet` template pair (merged into `home.html`), and
rewrote `README.md`/`CONTRIBUTING.md` to describe a solo repo. Kept the
ops-console visual metaphor (`deploy.log`, `whoami`, `ps_aux`, edge network)
since that part was never actually about having teammates — it just made
personal experience/education/hobbies read as systems primitives.

## 2026-07-11 — Connection-per-request instead of connect-once-at-boot #incident

Caught before it bit anyone in production, but worth writing down: the
timeline feature originally opened one MySQL connection at import time and
kept it for the process's whole life. MySQL's `wait_timeout` closes idle
connections after 8 hours by default, and peewee doesn't notice server-side
closes, so the first `/timeline` or `/api/timeline_post` request after any
quiet stretch that long would have thrown `OperationalError: MySQL server
has gone away`, and kept failing on every request after that until the
process restarted. Gunicorn's `Restart=always` would not have helped, since
the process itself never crashes. Switched to peewee's own recommended
Flask pattern instead: connect in `before_request`, close in
`teardown_request`.

## 2026-07-11 — Timeline deployed to the VPS #milestone

Installed `mysql-server` 8.0 on the CentOS Stream 9 box (the AppStream module
had it), then ran the equivalent of `mysql_secure_installation` by hand:
scoped the app's grant to `myportfoliodb.*` instead of the `*.*` the
assignment uses for local dev, dropped any anonymous accounts, and set a
generated root password instead of leaving root passwordless on a box that's
open to the internet. `redeploy-site.sh` handled the rest without changes.
`curl-test.sh` passes against the live server.

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
