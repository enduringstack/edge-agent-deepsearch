#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify vendor article publication dates by fetching actual page content.

Solves the <lastmod> fabrication problem: sitemap dates reflect page modification
times, not publication dates. This script fetches each candidate page and extracts
the real publication date from structured markup (JSON-LD, meta tags, <time>).

Only entries with verified dates in the collection window are kept.

Input:  data/_vendors_collected.json
Output: data/_vendors_verified.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "_vendors_collected.json"
OUTPUT = ROOT / "data" / "_vendors_verified.json"

UA = "Mozilla/5.0 (compatible; edge-agent-date-verifier/1.0)"
WORKERS = 10
TIMEOUT = 12

sys.path.insert(0, str(ROOT / "agent"))
from research_collection import collection_window, parse_collection_date


def fetch_html(url: str) -> str:
    """Fetch a URL and return HTML text."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read(65536).decode("utf-8", errors="replace")
    except Exception as e:
        return ""


def parse_date_str(s: str) -> datetime | None:
    """Parse various date string formats into datetime."""
    if not s:
        return None
    s = s.strip()
    # Remove trailing timezone offset like +00:00 -> +0000
    s = re.sub(r'(\+|-)(\d{2}):(\d{2})$', r'\1\2\3', s)

    for fmt in (
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%B %d, %Y',     # "September 10, 2026"
        '%b %d, %Y',     # "Sep 10, 2026"
        '%d %B %Y',      # "10 September 2026"
        '%d %b %Y',      # "10 Sep 2026"
    ):
        try:
            d = datetime.strptime(s, fmt)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # Fallback: extract YYYY-MM-DD pattern
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        try:
            return datetime(int(m[1]), int(m[2]), int(m[3]), tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def extract_date_from_jsonld(html: str) -> str | None:
    """Extract datePublished from JSON-LD structured data."""
    for m in re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S
    ):
        try:
            data = json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            continue

        # Handle single object or list of objects
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            # Check @graph wrapper
            if "@graph" in item:
                graph_items = item["@graph"]
                if isinstance(graph_items, list):
                    items.extend(graph_items)
                continue

            # Look for datePublished
            for key in ("datePublished", "dateCreated", "datePosted"):
                val = item.get(key)
                if val and isinstance(val, str):
                    dt = parse_date_str(val)
                    if dt:
                        return dt.strftime("%Y-%m-%d")
    return None


def extract_date_from_meta(html: str) -> str | None:
    """Extract publication date from meta tags."""
    meta_patterns = [
        # Open Graph
        (r'<meta[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        (r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']', re.I),
        # Standard meta
        (r'<meta[^>]*name=["\']publish_date["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        (r'<meta[^>]*name=["\']publish-date["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        (r'<meta[^>]*name=["\']publication_date["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        (r'<meta[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        (r'<meta[^>]*name=["\']DC\.date["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        (r'<meta[^>]*name=["\']DC\.date\.issued["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        (r'<meta[^>]*itemprop=["\']datePublished["\'][^>]*content=["\']([^"\']+)["\']', re.I),
        # Reversed attribute order
        (r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']publish_date["\']', re.I),
        (r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']date["\']', re.I),
        (r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*itemprop=["\']datePublished["\']', re.I),
    ]
    for pattern, flags in meta_patterns:
        m = re.search(pattern, html, flags)
        if m:
            dt = parse_date_str(m.group(1))
            if dt:
                return dt.strftime("%Y-%m-%d")
    return None


def extract_date_from_time(html: str) -> str | None:
    """Extract date from <time> elements with datetime attribute."""
    # <time datetime="2026-09-10" pubdate> or <time datetime="2026-09-10" itemprop="datePublished">
    for m in re.finditer(
        r'<time[^>]*datetime=["\']([^"\']+)["\'][^>]*(?:pubdate|itemprop=["\']datePublished["\'])',
        html, re.I
    ):
        dt = parse_date_str(m.group(1))
        if dt:
            return dt.strftime("%Y-%m-%d")
    # Also try reverse attribute order
    for m in re.finditer(
        r'<time[^>]*(?:pubdate|itemprop=["\']datePublished["\'])[^>]*datetime=["\']([^"\']+)["\']',
        html, re.I
    ):
        dt = parse_date_str(m.group(1))
        if dt:
            return dt.strftime("%Y-%m-%d")
    # Any <time> with a date-like datetime attribute
    for m in re.finditer(r'<time[^>]*datetime=["\']([^"\']+)["\']', html, re.I):
        dt = parse_date_str(m.group(1))
        if dt:
            return dt.strftime("%Y-%m-%d")
    return None


def extract_date_from_text(html: str) -> str | None:
    """Fallback: extract date from visible text patterns."""
    # Remove HTML tags for text search
    text = re.sub(r'<[^>]+>', ' ', html)

    patterns = [
        # "Published on September 10, 2026"
        r'(?:published|posted|released)\s+(?:on\s+)?(\w+ \d{1,2},?\s+\d{4})',
        # "September 10, 2026"
        r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
        # "Sep 10, 2026"
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4})',
        # "10 September 2026"
        r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            dt = parse_date_str(m.group(1))
            if dt:
                return dt.strftime("%Y-%m-%d")
    return None


def extract_date_from_html(html: str) -> str | None:
    """Extract real publication date from HTML, trying multiple strategies."""
    if not html:
        return None
    # Strategy 1: JSON-LD (most reliable)
    d = extract_date_from_jsonld(html)
    if d:
        return d
    # Strategy 2: Meta tags
    d = extract_date_from_meta(html)
    if d:
        return d
    # Strategy 3: <time> elements
    d = extract_date_from_time(html)
    if d:
        return d
    # Strategy 4: Text patterns (least reliable)
    d = extract_date_from_text(html)
    if d:
        return d
    return None


def verify_entry(
    entry: dict, window_start: str, window_end: str
) -> dict | None:
    """Fetch page, extract real date, verify it's in the collection window."""
    url = entry.get("url", "")
    if not url:
        return None

    html = fetch_html(url)
    if not html:
        return None

    real_date = extract_date_from_html(html)
    if not real_date:
        return None

    # Check if date falls in window
    if window_start <= real_date <= window_end:
        # Update the entry with verified date
        result = dict(entry)
        result["date"] = real_date
        result["date_verified"] = True
        return result
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify vendor article dates from page content.")
    parser.add_argument("--today", help="Override collection date as YYYY-MM-DD")
    args = parser.parse_args(argv)

    if not INPUT.exists():
        print(f"[VERIFY] ERROR: {INPUT} not found. Run collect_vendors.py first.", file=sys.stderr)
        return 1

    run_date = parse_collection_date(args.today)
    window_start, window_end, _ = collection_window(run_date)
    ws = window_start.strftime("%Y-%m-%d")
    we = window_end.strftime("%Y-%m-%d")

    raw = json.loads(INPUT.read_text(encoding="utf-8"))
    print(f"[VERIFY] loaded {len(raw)} candidates, window={ws}..{we}")

    verified = []
    dropped = 0
    no_date = 0
    out_of_window = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {
            pool.submit(verify_entry, e, ws, we): e
            for e in raw
        }
        for future in as_completed(futures):
            entry = futures[future]
            try:
                result = future.result()
                if result:
                    verified.append(result)
                else:
                    dropped += 1
            except Exception:
                dropped += 1

    # Sort by date descending
    verified.sort(key=lambda x: x.get("date", ""), reverse=True)

    OUTPUT.write_text(
        json.dumps(verified, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Summary
    from collections import Counter
    vendors = Counter(e["vendor"] for e in verified)
    print(f"\n[VERIFY] kept {len(verified)} verified entries, dropped {dropped}")
    print(f"[VERIFY] wrote to {OUTPUT}")
    print(f"  by vendor:")
    for v, c in vendors.most_common():
        print(f"    {v}: {c}")
    if verified:
        print(f"\n  verified entries:")
        for e in verified:
            print(f"    [{e['date']}] {e['vendor']:10} {e['title'][:50]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
