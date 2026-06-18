# Contributing — 26.SUM.B.6 pod portfolio

This is a **team portfolio** for our MLH × Meta Production Engineering pod. The
site is an ops console for a *fleet*: the pod is a cluster and each of us is a
service. The fleet overview lists everyone; each member gets their own page at
`/u/<handle>`.

New to the repo? Start with **"Add yourself to the fleet"** below — that's your
first PR and it gives you your own page.

## Dev setup

```bash
git clone https://github.com/Builder106/MLH-Meta-PE-Portfolio.git
cd MLH-Meta-PE-Portfolio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run
```

Open <http://127.0.0.1:5000>. (`FLASK_APP`/debug come from `.flaskenv`; needs
Python 3.12+.)

## Add yourself to the fleet

1. Open [`app/data.py`](app/data.py). Copy the `MEMBER_TEMPLATE` block at the
   bottom into the `MEMBERS` list.
2. Fill in your details. `handle` (lowercase-dashes) becomes your URL and your
   nav tab. `hobbies`, `education`, and `places` can start as `[]`.
3. Drop a **square** photo at `app/static/img/<your-handle>.jpg`.
4. `flask run` — you're on the fleet overview, you have a page at
   `/u/<your-handle>`, your hobbies show on `/ps_aux`, and the menu grew a tab.
   You changed zero templates.

## How the site is wired

- **All content is data.** `app/data.py` holds `POD` + a `MEMBERS` list. Routes
  in `app/__init__.py` render it through Jinja; templates have no hard-coded
  content.
- **The menu bar is dynamic** — built from `MEMBERS`, not hand-written. Add a
  member → a tab and a page appear automatically.
- **Reusable macros** (`app/templates/macros.html`: `deploy_row`,
  `provenance_card`, `process_card`) render repeating sections; pages just loop.

## Workflow

We practise the real GitHub flow — that's half the point of Week 1.

1. **Open an issue** (or claim one) for what you're doing.
2. **Branch** off `main`: `feat/<short-name>` (or `fix/`, `docs/`, `chore/`).
3. Commit, push, **open a PR** and link the issue (`Closes #12`).
4. **Get a teammate to review** before merging — every PR needs one approval.
   (This is also the "feedback from another fellow" the rubric wants.)
5. Squash-or-merge once it's green and approved.

Keep PRs small and focused — one feature/fix per PR.

## Guardrails

- **Content goes in `app/data.py`, not in templates.** If you're editing a
  `.html` file to change words, it probably belongs in `data.py`.
- **Keep the ops-console aesthetic** — terminal-dark, JetBrains Mono for data,
  the one operational-green accent. New colours/fonts should be a deliberate,
  discussed change, not a one-off.
- **Don't commit secrets.** `.env` is gitignored; use it for anything sensitive.
- Run the app locally before opening a PR — `/` and `/u/<your-handle>` should
  load without errors.

## Good first tasks

See the [issues labelled `good first issue`](https://github.com/Builder106/MLH-Meta-PE-Portfolio/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).
Typical starters: add yourself to the fleet, add a CI workflow, deploy the site
and wire the live URL into the README, or add your travel cities to the map.
