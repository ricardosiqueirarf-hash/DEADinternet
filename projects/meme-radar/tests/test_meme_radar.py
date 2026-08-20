#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "meme_radar.py"
SPEC = importlib.util.spec_from_file_location("meme_radar", MODULE_PATH)
assert SPEC and SPEC.loader
meme_radar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(meme_radar)


class MemeRadarTests(unittest.TestCase):
    def candidate(self, **overrides):
        values = {
            "source": "reddit",
            "source_id": "t3_abc",
            "title": "Piada ácida de teste",
            "url": "https://example.com/post?utm_source=reddit",
            "permalink": "https://www.reddit.com/r/test/comments/abc",
            "community": "test",
            "author": "autor",
            "created_utc": 1_700_000_000.0,
            "score": 100,
            "comments": 20,
            "upvote_ratio": 0.9,
            "is_nsfw": False,
            "is_video": False,
            "ranking_score": 10.0,
        }
        values.update(overrides)
        return meme_radar.Candidate(**values)

    def test_text_and_url_are_normalized(self):
        self.assertEqual(meme_radar.normalize_text("  Comédia ÁCIDA!!! "), "comedia acida")
        self.assertEqual(
            meme_radar.canonical_url("HTTPS://EXAMPLE.COM/post/?utm_source=x&a=1#fim"),
            "https://example.com/post?a=1",
        )

    def test_duplicate_keeps_stronger_candidate(self):
        weaker = self.candidate(source_id="t3_1", ranking_score=8.0)
        stronger = self.candidate(source_id="t3_2", ranking_score=12.0)
        selected = meme_radar.deduplicate([weaker, stronger])
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].source_id, "t3_2")

    def test_rank_rewards_metrics_and_freshness(self):
        now = 1_700_000_000.0
        strong = self.candidate(created_utc=now - 3600, score=1000, comments=200, upvote_ratio=0.95)
        weak = self.candidate(created_utc=now - 7 * 24 * 3600, score=10, comments=1, upvote_ratio=0.5)
        self.assertGreater(
            meme_radar.rank_candidate(strong, now=now),
            meme_radar.rank_candidate(weak, now=now),
        )

    def test_parser_rejects_nsfw_by_default(self):
        payload = {
            "data": {
                "children": [
                    {
                        "data": {
                            "name": "t3_safe",
                            "title": "Seguro",
                            "url": "https://example.com/safe",
                            "permalink": "/r/test/safe",
                            "subreddit": "test",
                            "author": "a",
                            "created_utc": 1_700_000_000,
                            "score": 10,
                            "num_comments": 2,
                            "upvote_ratio": 0.8,
                            "over_18": False,
                        }
                    },
                    {
                        "data": {
                            "name": "t3_nsfw",
                            "title": "Adulto",
                            "url": "https://example.com/nsfw",
                            "permalink": "/r/test/nsfw",
                            "subreddit": "test",
                            "author": "b",
                            "created_utc": 1_700_000_000,
                            "score": 20,
                            "num_comments": 3,
                            "upvote_ratio": 0.9,
                            "over_18": True,
                        }
                    },
                ]
            }
        }
        parsed = meme_radar.parse_reddit_listing(payload, now=1_700_000_100)
        self.assertEqual([item.source_id for item in parsed], ["t3_safe"])

    def test_report_is_written_atomically(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            meme_radar.write_report(output, [self.candidate()], {"project": "Meme Radar"})
            self.assertTrue(output.is_file())
            self.assertFalse(output.with_suffix(".json.tmp").exists())
            self.assertIn('"project": "Meme Radar"', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
