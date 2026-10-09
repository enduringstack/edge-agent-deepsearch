#!/usr/bin/env python3
"""Tests for agent/hardware_week.py — weekly merge, freshness check, monthly insight."""
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agent"))

import hardware_week as hw  # noqa: E402
from app import hardware  # noqa: E402

TODAY = date.today()
START = TODAY - timedelta(days=6)


def _item(url, day=None, **extra):
    return {
        "date": (day or TODAY).isoformat(), "vendor": "Qualcomm", "category": "移动SoC",
        "title": "Chip", "title_zh": "新芯片", "url": url, "source_type": "官方",
        "summary_zh": "发布新芯片。", "whats_new_zh": ["NPU 更快。", "English only"],
        "key_specs": {"npu": "Hexagon", "bogus": "x"}, "edge_ai_impact_zh": "端侧更快。",
        "evidence_urls": [], "confidence": "high",
        "model_capacity_zh": "能跑多大的模型：3B 模型 INT4，45 tok/s。",
        "deep_dive_zh": [{"heading": "NPU 微架构", "points": ["矩阵单元翻倍。"]}],
        **extra,
    }


class HardwareWeekTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self._saved = (hw.WEEKS, hw.INSIGHTS, hw.RADAR)
        hw.WEEKS = self.root / "weeks"
        hw.INSIGHTS = self.root / "hardware-insights"
        hw.RADAR = self.root / "hardware_radar.json"
        hw.WEEKS.mkdir()
        self.addCleanup(self._restore)

    def _restore(self):
        hw.WEEKS, hw.INSIGHTS, hw.RADAR = self._saved

    def _agent_file(self, name, items):
        p = self.root / name
        p.write_text(json.dumps({"topic": name, "new_items": items}, ensure_ascii=False), encoding="utf-8")
        return p

    def _archive(self, label, start, end, urls):
        block = {"window": {"start": start.isoformat(), "end": end.isoformat()},
                 "items": [{"url": u} for u in urls]}
        (hw.WEEKS / f"{label}.json").write_text(json.dumps({"hardware": block}), encoding="utf-8")

    def test_normalise_cleans_fields(self):
        it = hw.normalise(_item("https://a.com/x"))
        self.assertEqual(it["whats_new_zh"], ["NPU 更快。"])
        self.assertEqual(it["key_specs"], {"npu": "Hexagon"})
        self.assertEqual(it["model_capacity_zh"], "3B 模型 INT4，45 tok/s。")

    def test_arxiv_variants_dedupe_and_fold_details(self):
        a = self._agent_file("a.json", [_item("https://arxiv.org/abs/2610.01234", category="学术研究")])
        b = self._agent_file("b.json", [_item(
            "https://arxiv.org/pdf/2610.01234v2", category="学术研究",
            deep_dive_zh=[{"heading": "能效与实测", "points": ["0.5W。"]}], venue="ISCA 2026")])
        items, report = hw.merge([a, b], START, TODAY)
        self.assertEqual(len(items), 1)
        self.assertEqual(report["in_batch_dupes"], 1)
        self.assertEqual([d["heading"] for d in items[0]["deep_dive_zh"]], ["NPU 微架构", "能效与实测"])
        self.assertEqual(items[0]["venue"], "arXiv")  # first source's venue default is kept

    def test_drops_items_already_in_older_weeks_but_not_this_week(self):
        old = START - timedelta(days=7)
        self._archive("old", old, old + timedelta(days=6), ["https://a.com/old"])
        self._archive("this", START, TODAY, ["https://a.com/rerun"])
        f = self._agent_file("a.json", [_item("https://a.com/old/"), _item("https://a.com/rerun")])
        items, report = hw.merge([f], START, TODAY)
        self.assertEqual([i["url"] for i in items], ["https://a.com/rerun"])
        self.assertEqual(report["archived_dupes"], [("https://a.com/old/", "old")])

    def test_window_filter_and_same_news_fold(self):
        f = self._agent_file("a.json", [
            _item("https://vendor.com/launch"),
            _item("https://media.com/launch-story"),
            _item("https://a.com/early", day=START - timedelta(days=1)),
        ])
        items, report = hw.merge([f], START, TODAY, dupes={"https://media.com/launch": "https://vendor.com/launch"})
        self.assertEqual([i["url"] for i in items], ["https://vendor.com/launch"])
        self.assertIn("https://media.com/launch-story", items[0]["evidence_urls"])
        self.assertEqual(len(report["outside"]), 1)

    def test_merge_cli_writes_valid_radar(self):
        f = self._agent_file("a.json", [_item("https://vendor.com/launch")])
        text = self.root / "text.json"
        text.write_text(json.dumps({"overview": "本周综述。", "takeaways": ["结论一。"]}, ensure_ascii=False),
                        encoding="utf-8")
        out = self.root / "radar.json"
        rc = hw.main(["merge", str(f), "--text", str(text), "--out", str(out)])
        self.assertEqual(rc, 0)
        block = hardware.load_hardware(out)
        self.assertEqual(block["takeaways_zh"], ["结论一。"])
        self.assertEqual(hw.main(["check", "--path", str(out)]), 0)

    def test_check_fails_on_last_weeks_radar(self):
        old = TODAY - timedelta(days=10)
        out = self.root / "radar.json"
        out.write_text(json.dumps({
            "window": {"start": (old - timedelta(days=6)).isoformat(), "end": old.isoformat()},
            "overview": "上周综述。", "items": []}, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(hw.main(["check", "--path", str(out)]), 1)

    def test_month_assembles_parts_and_sorts_index(self):
        hw.INSIGHTS.mkdir()
        (hw.INSIGHTS / "index.json").write_text(json.dumps(
            [{"month": "2026-09", "title": "2026-09-02 ~ 2026-10-07", "file": "2026-09.md"}]), encoding="utf-8")
        head = self.root / "head.md"
        head.write_text("# 硬件洞察：10 月\n\n## 0. 总览\n\n判断。", encoding="utf-8")
        deep = self.root / "deep_qualcomm.json"
        deep.write_text(json.dumps({"section_md": "高通本月判断。"}, ensure_ascii=False), encoding="utf-8")
        tail = self.root / "tail.md"
        tail.write_text("## 7. 总结\n\n收尾。", encoding="utf-8")
        rc = hw.main(["month", "--month", "2026-10", "--title", "2026-10-08 ~ 2026-11-04",
                      "--head", str(head), "--part", f"{deep}::高通：新旗舰", "--tail", str(tail)])
        self.assertEqual(rc, 0)
        md = (hw.INSIGHTS / "2026-10.md").read_text(encoding="utf-8")
        self.assertIn("## 1. 高通：新旗舰\n\n高通本月判断。", md)
        self.assertTrue(md.endswith("收尾。\n"))
        index = json.loads((hw.INSIGHTS / "index.json").read_text(encoding="utf-8"))
        self.assertEqual([e["month"] for e in index], ["2026-10", "2026-09"])

    def test_month_rejects_bad_title(self):
        self.assertEqual(hw.main(["month", "--month", "2026-10", "--title", "十月", "--file", "x.md"]), 1)


class FreshnessTest(unittest.TestCase):
    def test_insight_age(self):
        fresh = [{"month": "m", "title": f"2026-01-01 ~ {(TODAY - timedelta(days=5)).isoformat()}"}]
        hardware.check_insight_fresh(fresh, TODAY)
        stale = [{"month": "m", "title": f"2026-01-01 ~ {(TODAY - timedelta(days=60)).isoformat()}"}]
        with self.assertRaises(hardware.HardwareValidationError):
            hardware.check_insight_fresh(stale, TODAY)
        with self.assertRaises(hardware.HardwareValidationError):
            hardware.check_insight_fresh([], TODAY)


if __name__ == "__main__":
    unittest.main()
