import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT))

import backfill_week  # noqa: E402


def arxiv(aid, day):
    return {"id": f"arxiv-{aid}", "paper_url": f"https://arxiv.org/abs/{aid}", "date": day}


def hf(aid, day):
    return {"id": f"arxiv-{aid}", "paper_url": f"https://huggingface.co/papers/{aid}", "date": day}


class ReclaimHfPickTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "2026-05-08.json"
        patcher = mock.patch.object(backfill_week.weeks_mod, "archive_path", lambda label: self.path)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def write_later_week(self, papers):
        self.path.write_text(json.dumps({"range": {"start": "2026-05-08", "end": "2026-05-14"},
                                         "papers": papers}), encoding="utf-8")

    def later_ids(self):
        return [p["id"] for p in json.loads(self.path.read_text(encoding="utf-8"))["papers"]]

    def test_submission_dated_arxiv_copy_reclaims_hf_pick(self):
        self.write_later_week([hf("2605.04647", "2026-05-08"), arxiv("2605.09999", "2026-05-09")])
        self.assertTrue(backfill_week._reclaim_hf_pick(arxiv("2605.04647", "2026-05-06"), "2026-05-08"))
        self.assertEqual(self.later_ids(), ["arxiv-2605.09999"])

    def test_arxiv_copy_in_later_week_is_never_taken(self):
        self.write_later_week([arxiv("2605.04647", "2026-05-08")])
        self.assertFalse(backfill_week._reclaim_hf_pick(arxiv("2605.04647", "2026-05-06"), "2026-05-08"))
        self.assertEqual(self.later_ids(), ["arxiv-2605.04647"])

    def test_hf_copy_does_not_reclaim(self):
        self.write_later_week([hf("2605.04647", "2026-05-08")])
        self.assertFalse(backfill_week._reclaim_hf_pick(hf("2605.04647", "2026-05-06"), "2026-05-08"))

    def test_paper_featured_in_later_weekly_stays_there(self):
        self.write_later_week([hf("2605.04647", "2026-05-08")])
        rec = json.loads(self.path.read_text(encoding="utf-8"))
        rec["weekly"] = {"highlights": [{"url": "https://huggingface.co/papers/2605.04647"}]}
        self.path.write_text(json.dumps(rec), encoding="utf-8")
        self.assertFalse(backfill_week.hf_pick_reclaimable(arxiv("2605.04647", "2026-05-06"), "2026-05-08"))
        self.assertFalse(backfill_week._reclaim_hf_pick(arxiv("2605.04647", "2026-05-06"), "2026-05-08"))
        self.assertEqual(self.later_ids(), ["arxiv-2605.04647"])

    def test_earlier_week_is_never_raided(self):
        self.write_later_week([hf("2605.04647", "2026-05-08")])
        self.assertFalse(backfill_week._reclaim_hf_pick(arxiv("2605.04647", "2026-05-09"), "2026-05-08"))


class SetCommunityWindowTest(unittest.TestCase):
    """Old-schema weeks overlap, so their radars may end before the archive does."""

    def run_set(self, radar_end):
        archive = {"range": {"start": "2026-06-26", "end": "2026-07-03"}}
        payload = {"window": {"start": "2026-06-26", "end": radar_end}, "coverage": [], "items": []}
        seen = {}
        with mock.patch.object(backfill_week.weeks_mod, "read_archive", lambda label: archive),              mock.patch.object(backfill_week, "_load", lambda path: payload),              mock.patch.object(backfill_week, "_update", lambda *a: None),              mock.patch.object(backfill_week.community, "validate_community",
                               lambda p, today: seen.setdefault("today", today) and {"items": []}):
            backfill_week.cmd_set_community(mock.Mock(label="2026-06-26", community="c.json"))
        return seen["today"].isoformat()

    def test_validates_against_radar_window_end(self):
        self.assertEqual(self.run_set("2026-07-02"), "2026-07-02")

    def test_radar_ending_after_the_week_is_refused(self):
        with self.assertRaises(SystemExit):
            self.run_set("2026-07-04")


if __name__ == "__main__":
    unittest.main()
