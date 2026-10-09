#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the 硬件洞察 page: copy the curated markdown into site/hardware/ and
render site/hardware.html from app.hardware_page.HARDWARE_HTML.

Re-run after editing data/hardware-insight.md.
Override paths via HARDWARE_SRC (the .md) and HARDWARE_SITE (the site/ dir) for tests.
"""
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_SRC = ROOT / "data" / "hardware-insight.md"
DEFAULT_SITE = ROOT / "site"


def main() -> int:
    src = Path(os.environ.get("HARDWARE_SRC") or DEFAULT_SRC)
    site = Path(os.environ.get("HARDWARE_SITE") or DEFAULT_SITE)
    if not src.exists():
        print(f"[HARDWARE] WARN source missing: {src}")
        return 1
    (site / "hardware").mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, site / "hardware" / "hardware-insight.md")
    from app.hardware_page import HARDWARE_HTML
    (site / "hardware.html").write_text(HARDWARE_HTML, encoding="utf-8")
    print(f"[HARDWARE] wrote site/hardware.html + site/hardware/hardware-insight.md (src {src.stat().st_size}B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
