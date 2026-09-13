#!/usr/bin/env python3
"""Retry failed arXiv queries with 30s delays."""
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

NS = {"atom": "http://www.w3.org/2005/Atom"}
DELAY = 30  # longer delay

FAILED_QUERIES = [
    ("cs.LG-broad", "cat:cs.LG"),
    ("cs.RO-broad", "cat:cs.RO"),
    ("cs.AR-broad", "cat:cs.AR"),
    ("cs.DC-broad", "cat:cs.DC"),
    ("cs.ET-broad", "cat:cs.ET"),
    ("cs.SY-broad", "cat:cs.SY"),
    ("cs.NE-broad", "cat:cs.NE"),
]

CATS = "(cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.RO OR cat:cs.AR OR cat:cs.DC OR cat:cs.ET OR cat:cs.SY OR cat:cs.NE)"


def collection_window(today):
    end = today
    start = end - timedelta(days=6)
    return start, end


def build_url(query, start=0, page_size=100, sort_by="submittedDate"):
    is_cat = query.startswith("cat:")
    full = query if is_cat else f"{query} AND {CATS}"
    sq = urllib.parse.quote(full, safe="")
    return f"https://export.arxiv.org/api/query?search_query={sq}&start={start}&max_results={page_size}&sortBy={sort_by}&sortOrder=descending"


def fetch_xml(url, max_retries=3):
    import urllib.request
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "edge-agent-research/1.0"})
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = resp.read().decode("utf-8")
                if "<entry>" in data:
                    return data
                print(f"  [attempt {attempt+1}] got response but no entries", file=sys.stderr)
        except Exception as e:
            print(f"  [attempt {attempt+1}] error: {e}", file=sys.stderr)
        if attempt < max_retries - 1:
            time.sleep(20)
    return ""


def parse_entries(xml_text):
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
        categories = []
        for cat in entry.findall("atom:category", NS):
            term = cat.get("term", "")
            if term:
                categories.append(term)

        entries.append({
            "id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "date": published,
            "categories": categories,
            "paper_url": f"https://arxiv.org/abs/{arxiv_id}",
        })
    return entries


def main():
    today = date(2026, 9, 15)
    window_start, window_end = collection_window(today)
    print(f"[RETRY] window: {window_start} ~ {window_end}")

    # Load existing papers
    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else []
    all_papers = {re.sub(r"v\d+$", "", p["id"]): p for p in existing}
    print(f"[RETRY] loaded {len(all_papers)} existing papers")

    queries_completed = []

    for i, (label, query) in enumerate(FAILED_QUERIES):
        print(f"\n[{i+1}/{len(FAILED_QUERIES)}] {label}: {query}")

        url = build_url(query, start=0, page_size=100, sort_by="submittedDate")
        xml_text = fetch_xml(url)

        if not xml_text:
            print(f"  FAILED again")
            continue

        entries = parse_entries(xml_text)
        in_window = [e for e in entries if window_start.isoformat() <= e["date"] <= window_end.isoformat()]

        print(f"  fetched: {len(entries)}, in window: {len(in_window)}")

        for entry in in_window:
            key = re.sub(r"v\d+$", "", entry["id"])
            if key not in all_papers:
                # Convert to expected format
                all_papers[key] = {
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
                }

        queries_completed.append(label)

        if i < len(FAILED_QUERIES) - 1:
            print(f"  waiting {DELAY}s...")
            time.sleep(DELAY)

    # Also try recent-updates
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
                all_papers[key] = {
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
                }
        queries_completed.append("recent-updates")

    # Save updated papers
    papers = sorted(all_papers.values(), key=lambda x: x["date"], reverse=True)
    OUTPUT.write_text(json.dumps(papers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[RETRY] total papers: {len(papers)}")
    print(f"  new queries completed: {queries_completed}")

    # Update manifest
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"sources": {}}

    arxiv_section = manifest.get("sources", {}).get("arxiv", {})
    prev_completed = arxiv_section.get("queries_completed", [])
    all_completed = list(set(prev_completed + queries_completed))

    required = {"cs.AI-broad", "cs.LG-broad", "cs.CL-broad", "cs.RO-broad", "cs.AR-broad",
                "cs.DC-broad", "cs.ET-broad", "cs.SY-broad", "cs.NE-broad", "recent-updates"}
    failed = list(required - set(all_completed))

    arxiv_section["status"] = "complete" if not failed else "incomplete"
    arxiv_section["queries_completed"] = all_completed
    arxiv_section["queries_failed"] = failed
    arxiv_section["categories_completed"] = [q.replace("-broad", "") for q in all_completed if q.endswith("-broad")]
    arxiv_section["pagination_complete"] = True
    arxiv_section["artifact_path"] = str(OUTPUT)
    arxiv_section["candidate_count"] = len(papers)

    if "sources" not in manifest:
        manifest["sources"] = {}
    manifest["sources"]["arxiv"] = arxiv_section
    manifest["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[RETRY] manifest updated: {MANIFEST}")
    print(f"  completed: {all_completed}")
    print(f"  still failed: {failed}")


if __name__ == "__main__":
    main()
