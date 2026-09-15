#!/usr/bin/env python3
"""Fast parallel vendor enrichment.

Fetches page titles concurrently (20 workers, 8s timeout each),
generates tags from URL path + vendor, classifies relevance.
Produces research_runs/candidates-vendor.json.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "_vendors_verified.json"
OUTPUT = ROOT / "research_runs" / "candidates-vendor.json"

UA = "Mozilla/5.0 (compatible; edge-agent-vendor-enricher/1.0)"
WORKERS = 20
TIMEOUT = 8


def fetch_title(url: str) -> str:
    """Fetch a URL and extract <title> tag only."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            # Read only first 8KB to find <title>
            raw = resp.read(8192).decode("utf-8", errors="replace")
        m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
        if m:
            title = re.sub(r"\s+", " ", m.group(1)).strip()
            # Remove common suffixes
            for suffix in [" | NVIDIA", " - Anthropic", " | OpenAI", " - Google", " | Qualcomm"]:
                title = title.replace(suffix, "").strip()
            return title
    except Exception:
        pass
    # Fallback: derive title from URL path
    from urllib.parse import urlparse
    p = urlparse(url)
    path_parts = [s for s in p.path.split("/") if s and s != ""]
    if path_parts:
        return f"{p.hostname}: {' / '.join(path_parts[:3])}"
    return p.hostname or url


def url_to_title_fallback(url: str) -> str:
    """Derive a rough title from URL path when fetch fails."""
    from urllib.parse import urlparse
    p = urlparse(url)
    path_parts = [s for s in p.path.split("/") if s and s != ""]
    if path_parts:
        return f"{p.hostname}: {' / '.join(path_parts[:3])}"
    return p.hostname or url


# Keywords for auto-tagging from URL + title
EDGE_KW = {
    "方向:端侧agent": [
        "on-device", "edge", "mobile", "npu", "agent", "device",
        "smartphone", "wearable", "embedded", "ondevice",
    ],
    "方向:高效推理": [
        "inference", "efficiency", "quantiz", "distill", "compress",
        "latency", "throughput", "accelerat", "speculative", "fast",
        "optim", "speed", "perf",
    ],
    "方向:模型架构": [
        "architecture", "transformer", "moe", "sparse", "attention",
        "foundation", "language-model", "llm", "model",
    ],
    "方向:编译部署": [
        "deploy", "runtime", "compiler", "onnx", "tflite", "coreml",
        "executorch", "openvino", "litert", "tensorrt", "triton",
    ],
    "方向:端云协同": [
        "cloud", "hybrid", "offload", "federat", "server",
    ],
    "方向:安全隐私": [
        "privacy", "security", "safety", "federated", "guard",
        "red-team", "alignment",
    ],
    "方向:量化": [
        "quantiz", "int4", "int8", "fp8", "nvfp4", "w4a", "gptq", "awq",
        "bit", "compress",
    ],
    "方向:推理框架": [
        "llama.cpp", "vllm", "tensorrt", "triton", "serving",
        "framework", "engine",
    ],
}

# Direct edge AI relevance patterns
DIRECT_RE = re.compile(
    r"on-device|ondevice|edge[- ]?(?:ai|inference|deploy|comput|device)|"
    r"mobile[- ]?(?:ai|llm|inference|deploy|device|agent)|"
    r"embedded[- ]?(?:ai|inference)|device[- ]?side|"
    r"\bnpu\b|\bevks\b|hexagon|dragonwing|smartphone|wearable|"
    r"端侧|端上|边缘|设备端|离线",
    re.I,
)
AI_RE = re.compile(
    r"\bai\b|\bllm|language.model|foundation.model|transformer|"
    r"neural|generative|agent|inference|reasoning|model",
    re.I,
)


def classify(url: str, title: str, vendor: str) -> str:
    text = f"{vendor} {title} {url}"
    if DIRECT_RE.search(text) and AI_RE.search(text):
        return "direct"
    if AI_RE.search(text):
        return "adjacent"
    return "irrelevant"


def auto_tags(url: str, title: str, vendor: str) -> list[str]:
    text = f"{vendor} {title} {url}".lower()
    tags = []
    for tag, keywords in EDGE_KW.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags[:5] or ["方向:高效推理"]


# URL patterns to skip (product pages, docs, login, etc.)
SKIP_PATTERNS = re.compile(
    r"/login|/signup|/pricing|/careers|/jobs|/contact|"
    r"/docs/|/api/|/reference|/changelog|/status|"
    r"\.(?:png|jpg|pdf|zip|tar|gz)$",
    re.I,
)


def enrich_entry(entry: dict) -> dict | None:
    """Enrich a single vendor entry. Returns None to skip."""
    vendor = entry.get("vendor", "")
    url = entry.get("url", "")
    dt = entry.get("date", "")
    alive = entry.get("alive", True)

    if not alive:
        return None
    if SKIP_PATTERNS.search(url):
        return None

    # Fetch title (or derive from URL)
    title = fetch_title(url)
    if not title or title == url:
        title = url_to_title_fallback(url)

    # Classify relevance
    relevance = classify(url, title, vendor)
    if relevance == "irrelevant":
        return None

    # Generate tags
    tags = auto_tags(url, title, vendor)

    # Build abstract from title + vendor context
    abstract = f"{vendor} published: {title}"

    # Initial scoring
    rel_score = 9 if relevance == "direct" else 5
    contrib_score = 5

    return {
        "vendor": vendor,
        "title": title,
        "paper_url": url,
        "url": url,
        "date": dt,
        "source_tier": "官方动态",
        "abstract": abstract,
        "vendors": vendor,
        "tags": tags,
        "open_source": False,
        "edge_agent_scope": "待核实",
        "edge_agent_evidence": "",
        "recommendation": "待审",
        "recommendation_reason": "",
        "title_zh": "",
        "effects": "",
        "mechanism": "",
        "score_reason": "",
        "score_relevance": rel_score,
        "score_contribution": contrib_score,
        "authors": vendor,
        "venue": "Official Blog",
        "alive": alive,
    }


def main() -> int:
    if not INPUT.exists():
        print(f"[ENRICH] ERROR: {INPUT} not found. Run collect_vendors.py first.")
        return 1

    raw = json.loads(INPUT.read_text(encoding="utf-8"))
    print(f"[ENRICH] loaded {len(raw)} vendor entries, enriching with {WORKERS} workers...")

    enriched = []
    skipped = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(enrich_entry, e): i for i, e in enumerate(raw)}
        for future in as_completed(futures):
            try:
                result = future.result()
                if result is None:
                    skipped += 1
                else:
                    enriched.append(result)
            except Exception:
                skipped += 1

    # Sort by date descending
    enriched.sort(key=lambda x: x.get("date", ""), reverse=True)

    OUTPUT.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Summary
    from collections import Counter
    vendors = Counter(e["vendors"] for e in enriched)
    print(f"\n[ENRICH] wrote {len(enriched)} candidates to {OUTPUT}")
    print(f"  skipped: {skipped} (irrelevant/error/skip-pattern)")
    print(f"  by vendor:")
    for v, c in vendors.most_common():
        print(f"    {v}: {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
