"""Database tests — verify TimelinePost read/write against the app's
in-memory SQLite database (TESTING=true), independent of MySQL.

Note: don't follow Peewee's testing docs literally here and bind
TimelinePost to a second, throwaway SqliteDatabase — Model.bind() mutates
the model class globally, so it leaks across test modules in the same
process and breaks test_app.py/test_smoke.py, which expect TimelinePost
still bound to the app's own db. Clearing rows between tests on the
existing db avoids that.
"""
import os
os.environ.setdefault("TESTING", "true")

import unittest
from datetime import date, datetime

from app import TimelinePost, _ordered_posts


class TestTimelinePost(unittest.TestCase):
    def setUp(self):
        TimelinePost.delete().execute()

    def test_create_and_retrieve_post(self):
        TimelinePost.create(
            name="Ada Lovelace",
            email="ada@example.com",
            content="Shipped the first program.",
            event_date=date(1843, 12, 10),
        )
        post = TimelinePost.get(TimelinePost.email == "ada@example.com")
        self.assertEqual(post.name, "Ada Lovelace")
        self.assertEqual(post.content, "Shipped the first program.")
        self.assertEqual(post.event_date, date(1843, 12, 10))

    def test_list_timeline_posts(self):
        # TODO: create a couple of TimelinePost rows, then confirm listing
        # them returns everything. See app/__init__.py's _ordered_posts() /
        # TimelinePost.select() for how the app itself lists posts.
        TimelinePost.create(name="Ada Lovelace", email="ada@example.com", content="first")
        TimelinePost.create(name="Grace Hopper", email="grace@example.com", content="second")

        posts = list(TimelinePost.select())

        self.assertEqual(len(posts), 2)
        self.assertEqual({p.name for p in posts}, {"Ada Lovelace", "Grace Hopper"})

    
    # Add by Chloe from here

    def test_ordered_posts_sorts_by_event_date_desc(self):
        TimelinePost.create(name="A", email="a@example.com", content="a", event_date=date(2024, 1, 1))
        TimelinePost.create(name="B", email="b@example.com", content="b", event_date=date(2024, 6, 1))
        TimelinePost.create(name="C", email="c@example.com", content="c", event_date=date(2024, 3, 1))

        ordered = _ordered_posts()

        self.assertEqual([p.name for p in ordered], ["B", "C", "A"])

    def test_ordered_posts_falls_back_to_created_at_when_event_date_missing(self):
        TimelinePost.create(name="Older", email="o@example.com", content="o",
                            created_at=datetime(2024, 1, 1))
        TimelinePost.create(name="Newer", email="n@example.com", content="n",
                            created_at=datetime(2024, 6, 1))

        ordered = _ordered_posts()

        self.assertEqual([p.name for p in ordered], ["Newer", "Older"])

    def test_ordered_posts_mixes_event_date_and_created_at_fallback(self):
        TimelinePost.create(name="Backfilled", email="b@example.com", content="b",
                            event_date=date(2024, 1, 1))
        TimelinePost.create(name="Undated", email="u@example.com", content="u",
                            created_at=datetime(2024, 5, 1))

        ordered = _ordered_posts()

        self.assertEqual([p.name for p in ordered], ["Undated", "Backfilled"])


if __name__ == "__main__":
    unittest.main()
