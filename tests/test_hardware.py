#!/usr/bin/env python3
"""Hardware radar: contract validation, static inlining round-trip, insight page build."""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import build, hardware, weeks
from app.hardware_page import HARDWARE_HTML
from app.page import INDEX_HTML


def _item(**over):
    item = {
        "date": "2026-09-25", "vendor": "Qualcomm", "category": "移动SoC",
        "title": "Flagship SoC", "title_zh": "新旗舰移动平台",
        "url": "https://www.qualcomm.com/news/releases/flagship",
        "source_type": "官方", "summary_zh": "高通发布新一代旗舰移动平台。",
        "whats_new_zh": ["NPU 性能提升。"], "key_specs": {"npu": "Hexagon", "gpu": ""},
        "edge_ai_impact_zh": "端侧大模型解码更快。", "evidence_urls": [], "confidence": "high",
    }
    item.update(over)
    return item


def _payload(*items):
    return {"window": {"start": "2026-09-22", "end": "2026-09-28"},
            "overview": "本周硬件综述。", "items": list(items) or [_item()]}


class ValidateHardwareTest(unittest.TestCase):
    def test_accepts_good_payload_and_drops_empty_specs(self):
        out = hardware.validate_hardware(_payload())
        self.assertEqual(out["items"][0]["key_specs"], {"npu": "Hexagon"})

    def test_sorts_by_category_then_trust_then_newest(self):
        out = hardware.validate_hardware(_payload(
            _item(category="存内计算/PIM", url="https://a.example/1"),
            _item(date="2026-09-23", url="https://a.example/2"),
            _item(date="2026-09-27", url="https://a.example/3"),
            _item(date="2026-09-28", url="https://a.example/4", confidence="low"),
        ))
        self.assertEqual([i["url"][-1] for i in out["items"]], ["3", "2", "4", "1"])

    def test_rejects_bad_fields(self):
        cases = {
            "date": _item(date="2026-10-30"),
            "category": _item(category="手机"),
            "source_type": _item(source_type="博客"),
            "url": _item(url="ftp://x"),
            "title_zh": _item(title_zh="English only"),
            "whats_new_zh": _item(whats_new_zh=["english"]),
            "key_specs": _item(key_specs={"price": "1"}),
            "confidence": _item(confidence="sure"),
        }
        for field, item in cases.items():
            with self.subTest(field=field):
                with self.assertRaises(hardware.HardwareValidationError) as ctx:
                    hardware.validate_hardware(_payload(item))
                self.assertIn(field, str(ctx.exception))

    def test_accepts_deep_fields_and_takeaways(self):
        payload = _payload(_item(
            model_capacity_zh="官方口径：30B MoE（约 3B 激活），32K 上下文。",
            deep_dive_zh=[{"heading": "NPU 微架构", "points": ["新增 Element Accelerator。"]}]))
        payload["takeaways_zh"] = ["内存子系统成为竞争焦点。"]
        out = hardware.validate_hardware(payload)
        self.assertEqual(out["takeaways_zh"], ["内存子系统成为竞争焦点。"])
        self.assertEqual(out["items"][0]["deep_dive_zh"][0]["heading"], "NPU 微架构")

    def test_rejects_bad_deep_fields(self):
        cases = {
            "deep_dive_zh": _item(deep_dive_zh=[{"heading": "NPU", "points": ["x"]}]),
            "model_capacity_zh": _item(model_capacity_zh="30B"),
            "venue": _item(category="学术研究", source_type="论文"),
        }
        for field, item in cases.items():
            with self.subTest(field=field):
                with self.assertRaises(hardware.HardwareValidationError) as ctx:
                    hardware.validate_hardware(_payload(item))
                self.assertIn(field, str(ctx.exception))
        bad = _payload()
        bad["takeaways_zh"] = ["english"]
        with self.assertRaises(hardware.HardwareValidationError):
            hardware.validate_hardware(bad)

    def test_page_renders_deep_fields(self):
        for marker in ("能跑多大模型", "技术细节", "本周结论", "hw-takeaways", "item.venue"):
            self.assertIn(marker, INDEX_HTML)

    def test_rejects_duplicate_urls(self):
        with self.assertRaises(hardware.HardwareValidationError):
            hardware.validate_hardware(_payload(_item(), _item()))

    def test_missing_file_loads_empty(self):
        self.assertEqual(hardware.load_hardware(ROOT / "nope.json")["items"], [])


class InlineRoundTripTest(unittest.TestCase):
    def test_render_page_inlines_and_extract_recovers_hardware(self):
        payload = hardware.validate_hardware(_payload())
        html = build.render_page(
            INDEX_HTML, [], {"overview": "", "highlights": []}, {"items": []}, [],
            week_label=None, weeks_base="", runtime=False,
            community={"coverage": [], "items": []}, hardware=payload)
        self.assertIn("let data=window.__HARDWARE__||null;", html)
        extracted = weeks.extract_payloads_from_html(html)
        self.assertEqual(extracted["hardware"], payload)
        self.assertEqual(extracted["community"], {"coverage": [], "items": []})

    def test_page_places_hardware_between_weekly_and_library(self):
        self.assertLess(INDEX_HTML.find('id="weekly"'), INDEX_HTML.find('id="hardware"'))
        self.assertLess(INDEX_HTML.find('id="hardware"'), INDEX_HTML.find('id="all-research"'))
        self.assertIn('href="hardware.html"', INDEX_HTML)

    def test_static_week_pages_rewrite_hardware_nav(self):
        html = build.render_page(
            INDEX_HTML, [], {}, {}, [], week_label="2026-09-22", weeks_base="../",
            runtime=False)
        self.assertIn('href="../hardware.html"', html)


class BuildHardwarePageTest(unittest.TestCase):
    def test_shell_points_at_hardware_markdown(self):
        self.assertIn("hardware/hardware-insight.md", HARDWARE_HTML)
        self.assertIn("硬件洞察", HARDWARE_HTML)
        self.assertNotIn("WAIC-insight.md", HARDWARE_HTML)

    def test_build_writes_html_and_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "hw.md"
            src.write_text("# t\n## 1. A\n", encoding="utf-8")
            site = Path(tmp) / "site"
            os.environ["HARDWARE_SRC"], os.environ["HARDWARE_SITE"] = str(src), str(site)
            self.addCleanup(os.environ.pop, "HARDWARE_SRC", None)
            self.addCleanup(os.environ.pop, "HARDWARE_SITE", None)
            spec = importlib.util.spec_from_file_location(
                "build_hardware", ROOT / "agent" / "build_hardware.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.assertEqual(mod.main(), 0)
            self.assertTrue((site / "hardware.html").exists())
            self.assertTrue((site / "hardware" / "hardware-insight.md").exists())


class CommittedDataTest(unittest.TestCase):
    def test_committed_hardware_data_passes_contract(self):
        current = ROOT / "data" / "hardware_radar.json"
        if current.exists():
            hardware.load_hardware(current)
        for p in sorted((ROOT / "data" / "weeks").glob("*.json")):
            if p.name == "manifest.json":
                continue
            block = json.loads(p.read_text(encoding="utf-8")).get("hardware")
            if block and block.get("items"):
                with self.subTest(week=p.name):
                    hardware.validate_hardware(block)


if __name__ == "__main__":
    unittest.main()
