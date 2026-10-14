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

    def test_earlier_week_is_never_raided(self):
        self.write_later_week([hf("2605.04647", "2026-05-08")])
        self.assertFalse(backfill_week._reclaim_hf_pick(arxiv("2605.04647", "2026-05-09"), "2026-05-08"))


if __name__ == "__main__":
    unittest.main()
