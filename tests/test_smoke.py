"""Smoke tests — boot the app and assert every route serves.

These run in CI on every PR. The per-member check means that if a teammate adds
a malformed entry to MEMBERS, their page 500s and CI fails before merge.
"""
import app as application


def client():
    return application.app.test_client()


def test_core_routes_ok():
    c = client()
    for path in ("/", "/ps_aux", "/healthz", "/timeline"):
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


def test_timeline_post_create_and_list():
    c = client()
    created = c.post("/api/timeline_post", json={
        "name": "CI Runner", "email": "ci@example.com", "content": "smoke test post",
    })
    assert created.status_code == 201, created.get_data(as_text=True)
    post_id = created.get_json()["id"]

    listed = c.get("/api/timeline_post").get_json()
    assert any(p["id"] == post_id for p in listed)

    assert c.delete(f"/api/timeline_post/{post_id}").status_code == 200


def test_timeline_post_requires_fields():
    resp = client().post("/api/timeline_post", json={"name": "Missing Fields"})
    assert resp.status_code == 400
