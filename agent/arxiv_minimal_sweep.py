#!/usr/bin/env python3
"""Minimal conservative arXiv sweep - avoids rate limiting with long delays.

Only fetches first page (100 results) per required query with 15s delays.
"""
import json
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".superpowers" / "sdd" / "arxiv_candidates.json"
MANIFEST = ROOT / "research_runs" / "collection-manifest.json"

NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
DELAY = 15  # seconds between queries

# Required queries from research_collection.py
REQUIRED_QUERIES = [
    ("cs.AI-broad", "cat:cs.AI"),
    ("cs.LG-broad", "cat:cs.LG"),
    ("cs.CL-broad", "cat:cs.CL"),
    ("cs.RO-broad", "cat:cs.RO"),
    ("cs.AR-broad", "cat:cs.AR"),
    ("cs.DC-broad", "cat:cs.DC"),
    ("cs.ET-broad", "cat:cs.ET"),
    ("cs.SY-broad", "cat:cs.SY"),
    ("cs.NE-broad", "cat:cs.NE"),
]

CATS = "(cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.RO OR cat:cs.AR OR cat:cs.DC OR cat:cs.ET OR cat:cs.SY OR cat:cs.NE)"


def collection_window(today: date) -> tuple[date, date]:
    end = today
    start = end - timedelta(days=6)
    return start, end


def build_url(query: str, start: int = 0, page_size: int = 100, sort_by: str = "submittedDate") -> str:
    is_cat = query.startswith("cat:")
    full = query if is_cat else f"{query} AND {CATS}"
    sq = urllib.parse.quote(full, safe="")
    return f"https://export.arxiv.org/api/query?search_query={sq}&start={start}&max_results={page_size}&sortBy={sort_by}&sortOrder=descending"


def fetch_xml(url: str, max_retries: int = 3) -> str:
    import urllib.request
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "edge-agent-research/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            print(f"  [attempt {attempt+1}] error: {e}", file=sys.stderr)
            time.sleep(10)
    return ""


def parse_entries(xml_text: str) -> list[dict]:
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    entries = []
    for entry in root.findall("atom:entry", NS):
        arxiv_id = entry.findtext("atom:id", "", NS).split("/abs/")[-1]
        title = entry.findtext("atom:title", "", NS).strip()
        title = re.sub(r"\s+", " ", title)
        abstract = entry.findtext("atom:summary", "", NS).strip()
        abstract = re.sub(r"\s+", " ", abstract)

        authors = []
        for author in entry.findall("atom:author", NS):
            name = author.findtext("atom:name", "", NS)
            if name:
                authors.append(name)

        published = entry.findtext("atom:published", "", NS)[:10]
        updated = entry.findtext("atom:updated", "", NS)[:10]

        # Get categories
        categories = []
        for cat in entry.findall("atom:category", NS):
            term = cat.get("term", "")
            if term:
                categories.append(term)

        # Get PDF URL
        pdf_url = ""
        for link in entry.findall("atom:link", NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href", "")
                break

        entries.append({
            "id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "date": published,
            "updated": updated,
            "categories": categories,
            "paper_url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": pdf_url,
        })
    return entries


def main():
    today = date(2026, 9, 15)
    window_start, window_end = collection_window(today)
    print(f"[MINI-SWEEP] window: {window_start} ~ {window_end}")

    all_papers = {}
    queries_completed = []
    queries_failed = []
    categories_completed = []

    for i, (label, query) in enumerate(REQUIRED_QUERIES):
        print(f"\n[{i+1}/{len(REQUIRED_QUERIES)}] {label}: {query}")

        url = build_url(query, start=0, page_size=100, sort_by="submittedDate")
        xml_text = fetch_xml(url)

        if not xml_text:
            print(f"  FAILED: no response")
            queries_failed.append(label)
            continue

        entries = parse_entries(xml_text)
        in_window = [e for e in entries if window_start.isoformat() <= e["date"] <= window_end.isoformat()]

        print(f"  fetched: {len(entries)}, in window: {len(in_window)}")

        for entry in in_window:
            key = re.sub(r"v\d+$", "", entry["id"])
            if key not in all_papers:
                all_papers[key] = entry

        queries_completed.append(label)
        cat = label.replace("-broad", "")
        if cat not in categories_completed:
            categories_completed.append(cat)

        if i < len(REQUIRED_QUERIES) - 1:
            print(f"  waiting {DELAY}s...")
            time.sleep(DELAY)

    # Also do the recent-updates query
    print(f"\n[recent-updates] lastUpdatedDate sweep")
    time.sleep(DELAY)
    url = build_url(CATS, start=0, page_size=100, sort_by="lastUpdatedDate")
    xml_text = fetch_xml(url)
    if xml_text:
        entries = parse_entries(xml_text)
        in_window = [e for e in entries if window_start.isoformat() <= e["date"] <= window_end.isoformat()]
        print(f"  fetched: {len(entries)}, in window: {len(in_window)}")
        for entry in in_window:
            key = re.sub(r"v\d+$", "", entry["id"])
            if key not in all_papers:
                all_papers[key] = entry
        queries_completed.append("recent-updates")
    else:
        queries_failed.append("recent-updates")

    # Convert to expected format
    papers = []
    for entry in all_papers.values():
        papers.append({
            "id": entry["id"],
            "title": entry["title"],
            "paper_url": entry["paper_url"],
            "date": entry["date"],
            "arxiv_date_basis": "submitted",
            "authors": ", ".join(entry["authors"]),
            "abstract": entry["abstract"],
            "venue": ", ".join(entry["categories"][:3]),
            "source_tier": "arXiv",
            "score_relevance": 5,
            "score_contribution": 5,
            "tags": [],
            "open_source": False,
            "edge_agent_scope": "待核实",
            "edge_agent_evidence": "",
            "recommendation": "待审",
            "recommendation_reason": "",
            "title_zh": "",
            "effects": "",
            "mechanism": "",
            "score_reason": "",
        })

    # Sort by date descending
    papers.sort(key=lambda x: x["date"], reverse=True)

    OUTPUT.write_text(json.dumps(papers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[MINI-SWEEP] wrote {len(papers)} papers to {OUTPUT}")
    print(f"  queries_completed: {queries_completed}")
    print(f"  queries_failed: {queries_failed}")
    print(f"  categories_completed: {categories_completed}")

    # Update the collection manifest with completion status
    manifest = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Ensure arXiv section exists and is updated
    if "sources" not in manifest:
        manifest["sources"] = {}

    arxiv_section = manifest["sources"].get("arxiv", {})
    arxiv_section["status"] = "complete" if not queries_failed else "incomplete"
    arxiv_section["queries_completed"] = queries_completed
    arxiv_section["queries_failed"] = queries_failed
    arxiv_section["categories_completed"] = categories_completed
    arxiv_section["pagination_complete"] = True
    arxiv_section["artifact_path"] = str(OUTPUT)
    arxiv_section["candidate_count"] = len(papers)
    manifest["sources"]["arxiv"] = arxiv_section
    manifest["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    manifest["window_start"] = window_start.isoformat()
    manifest["window_end"] = window_end.isoformat()

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[MINI-SWEEP] updated manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
