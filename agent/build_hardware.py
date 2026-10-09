#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the 硬件洞察 page: copy the monthly markdown reports into site/hardware/
and render site/hardware.html from app.hardware_page.HARDWARE_HTML.

Source layout: data/hardware-insights/index.json lists the months (newest
first) and each month's markdown file. The newest month is also published as
site/hardware/hardware-insight.md, which the page loads by default; older
months are reached through the page's month switcher (?m=YYYY-MM).

Re-run after editing data/hardware-insights/.
Override paths via HARDWARE_SRC_DIR and HARDWARE_SITE for tests.
"""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_SRC_DIR = ROOT / "data" / "hardware-insights"
DEFAULT_SITE = ROOT / "site"


def main() -> int:
    src = Path(os.environ.get("HARDWARE_SRC_DIR") or DEFAULT_SRC_DIR)
    site = Path(os.environ.get("HARDWARE_SITE") or DEFAULT_SITE)
    index_path = src / "index.json"
    if not index_path.exists():
        print(f"[HARDWARE] WARN index missing: {index_path}")
        return 1
    months = json.loads(index_path.read_text(encoding="utf-8"))
    if not months:
        print("[HARDWARE] WARN index.json lists no months")
        return 1
    out = site / "hardware"
    out.mkdir(parents=True, exist_ok=True)
    for entry in months:
        md = src / entry["file"]
        if not md.exists():
            print(f"[HARDWARE] WARN month file missing: {md}")
            return 1
        shutil.copy2(md, out / f"insight-{entry['month']}.md")
    shutil.copy2(src / months[0]["file"], out / "hardware-insight.md")
    (out / "index.json").write_text(json.dumps(
        [{"month": e["month"], "title": e["title"]} for e in months],
        ensure_ascii=False, indent=2), encoding="utf-8")
    from app.hardware_page import HARDWARE_HTML
    (site / "hardware.html").write_text(HARDWARE_HTML, encoding="utf-8")
    print(f"[HARDWARE] wrote site/hardware.html + {len(months)} month(s), latest {months[0]['month']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
