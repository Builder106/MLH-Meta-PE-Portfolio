"""Smoke tests — boot the app and assert every route serves.

These run in CI on every PR. The per-member check means that if a teammate adds
a malformed entry to MEMBERS, their page 500s and CI fails before merge.
"""
import app as application


def client():
    return application.app.test_client()


def test_core_routes_ok():
    c = client()
    for path in ("/", "/ps_aux", "/healthz"):
        assert c.get(path).status_code == 200, path


def test_every_member_page_ok():
    c = client()
    for m in application.data.MEMBERS:
        assert c.get(f"/u/{m['handle']}").status_code == 200, m["handle"]


def test_unknown_member_404():
    assert client().get("/u/does-not-exist").status_code == 404


def test_healthz_counts_members():
    payload = client().get("/healthz").get_json()
    assert payload["checks"]["members"] == len(application.data.MEMBERS)
