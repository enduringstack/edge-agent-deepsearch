#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build special event report pages.

Copies event markdown files from data/events/ into site/events/ and renders:
  - site/events.html          (hub page listing all events)
  - site/events/<slug>.html   (individual event detail pages)

Usage:
    python agent/build_event.py

Override paths via EVENTS_SRC (the data/events dir) and EVENTS_SITE (the site/ dir).
"""
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_SRC = ROOT / "data" / "events"
DEFAULT_SITE = ROOT / "site"


def main() -> int:
    src = Path(os.environ.get("EVENTS_SRC") or DEFAULT_SRC)
    site = Path(os.environ.get("EVENTS_SITE") or DEFAULT_SITE)

    if not src.exists():
        print(f"[EVENTS] WARN source dir missing: {src}")
        return 1

    site.mkdir(parents=True, exist_ok=True)
    (site / "events").mkdir(parents=True, exist_ok=True)

    from app.event_page import EVENTS_HUB_HTML, render_event_page

    # Write hub page
    (site / "events.html").write_text(EVENTS_HUB_HTML, encoding="utf-8")

    # Find all .md files in data/events/ and render detail pages
    md_files = sorted(src.glob("*.md"))
    count = 0
    for md_file in md_files:
        slug = md_file.stem
        # Copy markdown to site/events/ for client-side fetch
        shutil.copy2(md_file, site / "events" / f"{slug}.md")
        # Render HTML shell
        html = render_event_page(slug)
        (site / "events" / f"{slug}.html").write_text(html, encoding="utf-8")
        count += 1
        print(f"[EVENTS] wrote site/events/{slug}.html + {slug}.md")

    print(f"[EVENTS] hub: site/events.html ({count} event report(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
