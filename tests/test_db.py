import os
os.environ.setdefault("TESTING", "true")
import peewee

import unittest
from datetime import date, datetime

from app import TimelinePost, _ordered_posts

test_db = peewee.SqliteDatabase(":memory:")

class TestTimelinePost(unittest.TestCase):
    def setUp(self):
        self._ctx = test_db.bind_ctx([TimelinePost])
        self._ctx.__enter__()
        test_db.create_tables([TimelinePost])

    def tearDown(self):
        test_db.drop_tables([TimelinePost])
        self._ctx.__exit__(None, None, None)

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
