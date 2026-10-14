import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

import collect_github_releases as cgr  # noqa: E402


class UnprovenScanTest(unittest.TestCase):
    def run_collector(self, tmp: Path, fetch) -> dict:
        cgr.UNPROVEN_RELEASE_SCANS.clear()
        manifest = tmp / "collection-manifest.json"
        with mock.patch.object(cgr, "fetch_json", fetch):
            cgr.main(["--today", "2026-05-14", "--manifest", str(manifest), "--out", str(tmp / "gh.json")])
        return json.loads(manifest.read_text(encoding="utf-8"))["sources"]["github"]

    def test_clean_rerun_clears_stale_unproven_list(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            refused = self.run_collector(tmp, lambda url, timeout=30: None)
            self.assertTrue(refused["release_scan_unproven"])
            clean = self.run_collector(tmp, lambda url, timeout=30: [])
            self.assertEqual(clean["release_scan_unproven"], [])


if __name__ == "__main__":
    unittest.main()
