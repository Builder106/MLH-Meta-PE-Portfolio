"""Flask app for the pod portfolio.

The site is an ops console for a *fleet*: the pod is a cluster, each teammate is
a service. ``/`` lists the fleet, ``/u/<handle>`` is a service's detail page, and
``/ps_aux`` is the fleet-wide background-process (hobbies) view. All content comes
from ``app.data`` so templates stay logic-light, and the menu bar is generated
from ``MEMBERS`` — add a member and a tab + a page appear automatically.
"""
import hashlib
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, jsonify, abort
from peewee import CharField, DateTimeField, Model, MySQLDatabase, TextField
from playhouse.shortcuts import model_to_dict

from . import data

load_dotenv()

app = Flask(__name__)

db = MySQLDatabase(
    os.getenv("MYSQL_DATABASE"),
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
)


class TimelinePost(Model):
    """A post on the fleet's public timeline — school + career updates."""

    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        database = db


db.connect()
db.create_tables([TimelinePost])


def gravatar_url(email, size=64):
    """Gravatar's hash-of-email avatar convention; `d=identicon` covers posters
    without a registered Gravatar."""
    digest = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?s={size}&d=identicon"


app.jinja_env.globals["gravatar_url"] = gravatar_url


def serialize_post(post):
    payload = model_to_dict(post)
    payload["gravatar"] = gravatar_url(post.email)
    return payload


@app.context_processor
def inject_globals():
    """Build the dynamic nav (fleet + a tab per member + ps_aux) and expose the
    pod to every template. Active tab is resolved from the current endpoint."""
    nav = [{"label": "Team", "url": url_for("fleet"),
            "active": request.endpoint == "fleet"}]
    for m in data.MEMBERS:
        nav.append({
            "label": m["name"].split()[0],
            "url": url_for("member", handle=m["handle"]),
            "active": (request.endpoint == "member"
                       and request.view_args.get("handle") == m["handle"]),
        })
    nav.append({"label": "Hobbies", "url": url_for("hobbies"),
                "active": request.endpoint == "hobbies"})
    nav.append({"label": "Timeline", "url": url_for("timeline"),
                "active": request.endpoint == "timeline"})
    return {
        "nav": nav,
        "pod": data.POD,
        "now": datetime.now(timezone.utc),
        "site_url": os.getenv("URL", "localhost:5000"),
    }


@app.route("/")
def fleet():
    return render_template("fleet.html", title=f"{data.POD['name']} — team",
                           members=data.MEMBERS)


@app.route("/u/<handle>")
def member(handle):
    m = data.member_by_handle(handle)
    if m is None:
        abort(404)
    return render_template("member.html",
                           title=f"{m['name']} — {data.POD['name']}", member=m)


@app.route("/ps_aux")
def hobbies():
    return render_template("hobbies.html", title=f"Hobbies — {data.POD['name']}",
                           procs=data.all_hobbies())


@app.route("/timeline")
def timeline():
    posts = TimelinePost.select().order_by(TimelinePost.created_at.desc())
    return render_template("timeline.html",
                           title=f"Timeline — {data.POD['name']}", posts=posts)


@app.route("/api/timeline_post", methods=["POST"])
def create_timeline_post():
    payload = request.get_json(silent=True) or request.form
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    content = (payload.get("content") or "").strip()
    if not name or not email or not content:
        return jsonify(error="name, email, and content are all required"), 400
    post = TimelinePost.create(name=name, email=email, content=content)
    return jsonify(serialize_post(post)), 201


@app.route("/api/timeline_post", methods=["GET"])
def list_timeline_posts():
    posts = TimelinePost.select().order_by(TimelinePost.created_at.desc())
    return jsonify([serialize_post(p) for p in posts])


@app.route("/api/timeline_post/<int:post_id>", methods=["DELETE"])
def delete_timeline_post(post_id):
    post = TimelinePost.get_or_none(TimelinePost.id == post_id)
    if post is None:
        return jsonify(error="not found"), 404
    post.delete_instance()
    return jsonify(deleted=post_id)


@app.route("/healthz")
def healthz():
    """Liveness probe — because of course a fleet has one."""
    return jsonify(
        pod=data.POD["name"],
        status=data.POD["status"],
        region=data.POD["region"],
        cohort=data.POD["cohort"],
        services=[m["handle"] for m in data.MEMBERS],
        checks={"members": len(data.MEMBERS),
                "processes": len(data.all_hobbies())},
        ts=datetime.now(timezone.utc).isoformat(),
    )


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html", title="404 — no such service"), 404
