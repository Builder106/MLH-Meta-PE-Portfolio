"""Flask app for an individual portfolio.

The site is an ops console for one person: ``/`` is the profile — status
header, ``whoami``, ``deploy.log``, build provenance, edge network — and
``/ps_aux`` is the background-process (hobbies) view. All content comes from
``app.data.PROFILE`` so templates stay logic-light.
"""
import itertools
import os
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, jsonify

from peewee import CharField, DateField, DateTimeField, Model, MySQLDatabase, SqliteDatabase, TextField, fn
from playhouse.migrate import MySQLMigrator, migrate
from playhouse.shortcuts import model_to_dict

from . import data

load_dotenv()

app = Flask(__name__)

# Tests set TESTING=true so the suite runs against an isolated in-memory
# SQLite database instead of requiring a real MySQL instance.
TESTING = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    db = SqliteDatabase(":memory:")
else:
    db = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class TimelinePost(Model):
    """A post on the public timeline — school + career updates.

    ``event_date`` is when the update actually happened, distinct from
    ``created_at`` (when the row was inserted) — the two diverge whenever a
    post is backfilled instead of written the day of.
    """

    name = CharField()
    email = CharField()
    content = TextField()
    event_date = DateField(null=True)
    image = CharField(null=True, max_length=500)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        database = db


db.connect()
db.create_tables([TimelinePost])
if not TESTING:
    # SQLite gets the event_date/image columns for free since the in-memory
    # database is always created fresh from the current Model definition —
    # only the long-lived MySQL database needs a migration path.
    existing_columns = {c.name for c in db.get_columns(TimelinePost._meta.table_name)}
    migrator = MySQLMigrator(db)
    if "event_date" not in existing_columns:
        migrate(migrator.add_column(TimelinePost._meta.table_name, "event_date", TimelinePost.event_date))
    if "image" not in existing_columns:
        migrate(migrator.add_column(TimelinePost._meta.table_name, "image", TimelinePost.image))
if not TESTING:
    db.close()
# When TESTING, leave the in-memory SQLite connection open — closing it
# would wipe every row created since the database only lives as long as
# its connection does.


@app.before_request
def _db_connect():
    db.connect(reuse_if_open=True)


@app.teardown_request
def _db_close(exc):
    # Keep the in-memory SQLite connection open for the life of the test
    # process; closing it deletes the database.
    if TESTING:
        return
    if not db.is_closed():
        db.close()


def serialize_post(post):
    payload = model_to_dict(post)
    payload["event_date"] = post.event_date.isoformat() if post.event_date else None
    return payload


def display_date(post):
    """The date a post is grouped/labeled by: the real event date if given,
    otherwise the day it was posted."""
    return post.event_date or post.created_at.date()


@app.context_processor
def inject_globals():
    """Expose the profile and a fixed nav to every template."""
    nav = [
        {"label": "Home", "url": url_for("home"), "active": request.endpoint == "home"},
        {"label": "Hobbies", "url": url_for("hobbies"), "active": request.endpoint == "hobbies"},
        {"label": "Timeline", "url": url_for("timeline"), "active": request.endpoint == "timeline"},
    ]
    return {
        "nav": nav,
        "profile": data.PROFILE,
        "now": datetime.now(timezone.utc),
        "site_url": os.getenv("URL", "localhost:5000"),
    }


@app.route("/")
def home():
    return render_template("home.html", title=f"{data.PROFILE['name']} — {data.PROFILE['role']}",
                           profile=data.PROFILE)


@app.route("/ps_aux")
def hobbies():
    return render_template("hobbies.html", title=f"Hobbies — {data.PROFILE['name']}",
                           procs=data.PROFILE["hobbies"])


def _ordered_posts():
    """Posts ordered by their real-world date (event_date, falling back to the
    day they were posted), newest first."""
    order = fn.COALESCE(TimelinePost.event_date, fn.DATE(TimelinePost.created_at))
    return list(TimelinePost.select().order_by(order.desc(), TimelinePost.created_at.desc()))


@app.route("/timeline")
def timeline():
    posts = _ordered_posts()
    for i, post in enumerate(posts):
        post.month_label = display_date(post).strftime("%B %Y")
        post.day_label = display_date(post).strftime("%b %d")
        post.is_latest = i == 0
    groups = [{"label": label, "posts": list(group)}
              for label, group in itertools.groupby(posts, key=lambda p: p.month_label)]
    return render_template("timeline.html",
                           title=f"Timeline — {data.PROFILE['name']}", groups=groups)


@app.route("/api/timeline_post", methods=["POST"])
def create_timeline_post():
    payload = request.get_json(silent=True) or request.form
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    content = (payload.get("content") or "").strip()
    event_date_raw = (payload.get("event_date") or "").strip()
    image = (payload.get("image") or "").strip()
    if not name or not email or not content:
        return jsonify(error="name, email, and content are all required"), 400
    if not EMAIL_RE.match(email):
        return jsonify(error="email must be a valid email address"), 400
    event_date = None
    if event_date_raw:
        try:
            event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()
        except ValueError:
            return jsonify(error="event_date must be YYYY-MM-DD"), 400
    if image and not image.startswith(("http://", "https://", "/static/")):
        return jsonify(error="image must be an http(s) URL"), 400
    post = TimelinePost.create(name=name, email=email, content=content,
                               event_date=event_date, image=image or None)
    return jsonify(serialize_post(post)), 201


@app.route("/api/timeline_post", methods=["GET"])
def list_timeline_posts():
    return jsonify([serialize_post(p) for p in _ordered_posts()])


@app.route("/api/timeline_post/<int:post_id>", methods=["GET"])
def get_timeline_post(post_id):
    post = TimelinePost.get_or_none(TimelinePost.id == post_id)
    if post is None:
        return jsonify(error="not found"), 404
    return jsonify(serialize_post(post))


@app.route("/api/timeline_post/<int:post_id>", methods=["DELETE"])
def delete_timeline_post(post_id):
    post = TimelinePost.get_or_none(TimelinePost.id == post_id)
    if post is None:
        return jsonify(error="not found"), 404
    post.delete_instance()
    return jsonify(deleted=post_id)


@app.route("/healthz")
def healthz():
    """Liveness probe — because of course a service has one."""
    return jsonify(
        service=data.PROFILE["handle"],
        status=data.PROFILE["status"],
        region=data.PROFILE["region"],
        cohort=data.PROFILE["cohort"],
        checks={"processes": len(data.PROFILE["hobbies"])},
        ts=datetime.now(timezone.utc).isoformat(),
    )


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html", title="404 — no such service"), 404