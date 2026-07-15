"""Flask integration tests — exercise the timeline API end to end against
an isolated in-memory SQLite database (TESTING=true), not the app's own
MySQL connection.
"""
import os
os.environ.setdefault("TESTING", "true")

import unittest

from app import app as flask_app


class TestTimelineEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = flask_app.test_client()

    # TODO 1: creating a post
    def test_create_timeline_post(self):
        resp = self.client.post("/api/timeline_post", json={
            "name": "Grace Hopper",
            "email": "grace@example.com",
            "content": "Found the first bug.",
        })
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["name"], "Grace Hopper")
        self.client.delete(f"/api/timeline_post/{body['id']}")

    # TODO 2: listing posts
    def test_list_timeline_posts(self):
        created = self.client.post("/api/timeline_post", json={
            "name": "Grace Hopper", "email": "grace@example.com",
            "content": "Found the first bug.",
        }).get_json()

        resp = self.client.get("/api/timeline_post")

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(p["id"] == created["id"] for p in resp.get_json()))
        self.client.delete(f"/api/timeline_post/{created['id']}")

    # TODO 3: deleting a post
    # def test_delete_timeline_post(self):
    #     created = self.client.post("/api/timeline_post", json={
    #         "name": "Grace Hopper", "email": "grace@example.com",
    #         "content": "Found the first bug.",
    #     }).get_json()

    #     resp = self.client.delete(f"/api/timeline_post/{created['id']}")

    #     self.assertEqual(resp.status_code, 200)
    #     remaining = self.client.get("/api/timeline_post").get_json()
    #     self.assertFalse(any(p["id"] == created["id"] for p in remaining))

    # --- TDD: written before the app supported them, both drove a fix ---

    # def test_create_timeline_post_rejects_malformed_email(self):
    #     resp = self.client.post("/api/timeline_post", json={
    #         "name": "Ada Lovelace", "email": "not-an-email",
    #         "content": "Shipped the first program.",
    #     })
    #     self.assertEqual(resp.status_code, 400)

    # def test_get_single_timeline_post(self):
    #     created = self.client.post("/api/timeline_post", json={
    #         "name": "Ada Lovelace", "email": "ada@example.com",
    #         "content": "Shipped the first program.",
    #     }).get_json()

        # resp = self.client.get(f"/api/timeline_post/{created['id']}")

        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(resp.get_json()["id"], created["id"])
        # self.client.delete(f"/api/timeline_post/{created['id']}")

    # def test_get_single_timeline_post_404_for_missing_id(self):
    #     resp = self.client.get("/api/timeline_post/999999")
    #     self.assertEqual(resp.status_code, 404)

    # Added by Chloe from here

    def test_delete_timeline_post_404_for_missing_id(self):
        resp = self.client.delete("/api/timeline_post/999999")
        self.assertEqual(resp.status_code, 404)

    def test_create_timeline_post_missing_name(self):
        resp = self.client.post("/api/timeline_post", json={
            "email": "ada@example.com", "content": "Shipped the first program.",
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_timeline_post_missing_email(self):
        resp = self.client.post("/api/timeline_post", json={
            "name": "Ada Lovelace", "content": "Shipped the first program.",
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_timeline_post_missing_content(self):
        resp = self.client.post("/api/timeline_post", json={
            "name": "Ada Lovelace", "email": "ada@example.com",
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_timeline_post_whitespace_only_fields_rejected(self):
        resp = self.client.post("/api/timeline_post", json={
            "name": "   ", "email": "ada@example.com", "content": "Shipped the first program.",
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_timeline_post_accepts_local_static_image(self):
        created = self.client.post("/api/timeline_post", json={
            "name": "Ada Lovelace", "email": "ada@example.com",
            "content": "Shipped the first program.", "image": "/static/photos/ada.jpg",
        }).get_json()

        self.assertEqual(created["image"], "/static/photos/ada.jpg")
        self.client.delete(f"/api/timeline_post/{created['id']}")

    def test_create_timeline_post_accepts_form_encoded_body(self):
        resp = self.client.post("/api/timeline_post", data={
            "name": "Ada Lovelace", "email": "ada@example.com",
            "content": "Shipped the first program.",
        })
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["name"], "Ada Lovelace")
        self.client.delete(f"/api/timeline_post/{body['id']}")

    # def test_get_timeline_post_null_fields_round_trip(self):
    #     created = self.client.post("/api/timeline_post", json={
    #         "name": "Ada Lovelace", "email": "ada@example.com",
    #         "content": "Shipped the first program.",
    #     }).get_json()

        # resp = self.client.get(f"/api/timeline_post/{created['id']}")

        # body = resp.get_json()
        # self.assertIsNone(body["event_date"])
        # self.assertIsNone(body["image"])
        # self.client.delete(f"/api/timeline_post/{created['id']}")


if __name__ == "__main__":
    unittest.main()
