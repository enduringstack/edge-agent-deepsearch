#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh data/github_trending_top20.json in one step.

Runs collect_github_trending (fetches trending + search API → _github_trending.json)
then converts to the top20 file the page reads. The main agent runs this during
weekly collection before Chinese rewriting; deployment must not overwrite the
translated descriptions with fresh English text.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

parser = argparse.ArgumentParser(description="Refresh data/github_trending_top20.json.")
parser.add_argument("--today", help="Override collection date as YYYY-MM-DD")
parser.add_argument(
    "--no-collect",
    action="store_true",
    help="Convert the existing data/_github_trending.json instead of re-fetching. "
         "Use when rebuilding a past window, or when the collector already ran.",
)
args = parser.parse_args()

if not args.no_collect:
    import collect_github_trending  # noqa: E402

    collect_github_trending.main(["--today", args.today] if args.today else None)

src = ROOT / "data" / "_github_trending.json"
d = json.loads(src.read_text(encoding="utf-8"))
items = [x for x in d if x.get("source") == "search" and x.get("stars")]
items.sort(key=lambda x: x["stars"], reverse=True)
out = [
    {
        "rank": i + 1,
        "repo": x["repo"],
        "url": x["url"],
        "total": str(x["stars"]) + "★",
        "week": str(x["stars"]),
        "desc": x["desc"][:140],
    }
    for i, x in enumerate(items[:20])
]
dest = ROOT / "data" / "github_trending_top20.json"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[TRENDING] refreshed top20 -> {dest} · {len(out)} items, first: {out[0]['repo'] if out else 'NONE'}")
