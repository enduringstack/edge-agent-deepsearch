#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect HuggingFace Daily Papers for the seven-date window.

One request per window date against ``/api/daily_papers?date=YYYY-MM-DD`` so the
coverage manifest can record every date actually checked (validation requires the
dates_checked set to equal the window exactly). No keyword filtering here — the
assembler and the main agent do relevance work; this step only proves coverage.

Output: research_runs/candidates-hf.json
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from research_collection import (
    collection_window,
    parse_collection_date,
    update_source_coverage,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_runs" / "candidates-hf.json"
API = "https://huggingface.co/api/daily_papers?date={day}"
UA = "Mozilla/5.0 (edge-agent-research/1.0)"


def fetch_day(day: str, retries: int = 3):
    url = API.format(day=day)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"huggingface daily_papers failed for {day}: {exc}") from exc
            time.sleep(3 * (attempt + 1))
    return []


def to_candidate(entry: dict, day: str) -> dict | None:
    paper = entry.get("paper") or {}
    aid = str(paper.get("id") or "").strip()
    title = (paper.get("title") or entry.get("title") or "").strip()
    if not title:
        return None
    summary = (paper.get("summary") or "").strip()
    authors = [a.get("name", "") for a in (paper.get("authors") or []) if a.get("name")]
    paper_url = f"https://arxiv.org/abs/{aid}" if aid else (entry.get("url") or "")
    if not paper_url:
        return None
    return {
        "id": aid or title[:60],
        "title": title,
        "paper_url": paper_url,
        "date": day,
        "abstract": summary,
        "authors": authors,
        "upvotes": paper.get("upvotes"),
        "hf_page": f"https://huggingface.co/papers/{aid}" if aid else "",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Collect HF Daily Papers for the weekly window.")
    parser.add_argument("--today", help="Override collection date as YYYY-MM-DD")
    parser.add_argument("--manifest", default=str(ROOT / "research_runs" / "collection-manifest.json"))
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)
    run_date = parse_collection_date(args.today)
    start, end, dates = collection_window(run_date)

    seen_identity: set[tuple[str, str]] = set()
    cands: list[dict] = []
    checked: list[str] = []
    for d in dates:
        day = d.isoformat()
        rows = fetch_day(day)
        checked.append(day)
        for entry in rows or []:
            c = to_candidate(entry, day)
            if not c:
                continue
            key = (c["title"].lower(), c["paper_url"])
            if key in seen_identity:
                continue
            seen_identity.add(key)
            cands.append(c)
        print(f"[HF] {day}: {len(rows or [])} papers (total {len(cands)})")
        time.sleep(1)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")
    update_source_coverage(
        args.manifest,
        "huggingface",
        {"status": "complete", "dates_checked": checked, "candidate_count": len(cands)},
        today=run_date,
    )
    print(f"==> {len(cands)} HF candidates in {start}..{end} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
