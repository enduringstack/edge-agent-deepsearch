#!/usr/bin/env python3
"""Enrich raw vendor collected data into candidates-vendor.json format.

Reads data/_vendors_collected.json (from collect_vendors.py) and produces
research_runs/candidates-vendor.json with abstracts, tags, and initial scoring.

For each vendor entry:
  1. Fetch the article page and extract first paragraph as abstract
  2. Auto-classify relevance (direct/adjacent/irrelevant)
  3. Generate initial tags based on keywords
  4. Set recommendation to "待审" for human review
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "_vendors_collected.json"
OUTPUT = ROOT / "research_runs" / "candidates-vendor.json"

UA = "Mozilla/5.0 (compatible; edge-agent-vendor-enricher/1.0)"


def fetch_page_text(url: str, timeout: int = 20) -> str:
    """Fetch a URL and return cleaned text (first 3000 chars)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # Strip HTML tags for a rough text extraction
        text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.S | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:3000]
    except Exception:
        return ""


def extract_abstract(text: str) -> str:
    """Extract a reasonable abstract from page text."""
    if not text:
        return ""
    # Take the first 2-3 sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    abstract = " ".join(sentences[:3]).strip()
    return abstract[:500] if abstract else text[:300]


# Keywords for auto-tagging
EDGE_KW = {
    "方向:端侧agent": [
        "on-device", "edge ai", "mobile ai", "npu", "embedded", "agent",
        "on device", "device-side", "smartphone", "wearable",
    ],
    "方向:高效推理": [
        "inference", "efficiency", "quantiz", "distill", "compress",
        "latency", "throughput", "accelerat", "speculative",
    ],
    "方向:模型架构": [
        "architecture", "transformer", "moe", "sparse", "attention",
        "foundation model", "language model",
    ],
    "方向:编译部署": [
        "deploy", "runtime", "compiler", "onnx", "tflite", "coreml",
        "executorch", "openvino", "litert",
    ],
    "方向:端云协同": [
        "cloud", "hybrid", "device-to-cloud", "offload", "federat",
    ],
    "方向:安全隐私": [
        "privacy", "security", "safety", "federated", "differential privacy",
    ],
    "方向:量化": [
        "quantiz", "int4", "int8", "fp8", "nvfp4", "w4a", "gptq", "awq",
    ],
    "方向:推理框架": [
        "llama.cpp", "vllm", "tensorrt", "triton", "serving", "framework",
    ],
}

# Keywords for relevance classification
DIRECT_RE = re.compile(
    r"on-device|on device|edge[- ](?:ai|inference|deploy|comput|device)|"
    r"mobile[- ](?:ai|llm|inference|deploy|device|agent)|"
    r"embedded[- ](?:ai|inference|system)|device[- ]side|"
    r"\bnpu\b|\bevks\b|hexagon|dragonwing|smartphone|wearable|smartwatch|"
    r"端侧|端上|边缘(?:设备|推理|计算)|设备端|离线运行",
    re.I,
)
AI_RE = re.compile(
    r"\bai\b|\bllms?\b|language model|foundation model|transformer|"
    r"neural network|generative|agent|inference|reasoning|"
    r"人工智能|语言模型|神经网络|生成式|推理|智能体",
    re.I,
)


def classify_relevance(title: str, abstract: str) -> str:
    text = title + " " + abstract
    if DIRECT_RE.search(text) and AI_RE.search(text):
        return "direct"
    if AI_RE.search(text):
        return "adjacent"
    return "irrelevant"


def auto_tags(title: str, abstract: str) -> list[str]:
    text = (title + " " + abstract).lower()
    tags = []
    for tag, keywords in EDGE_KW.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags[:5] or ["方向:高效推理"]


def enrich_vendor_entry(entry: dict) -> dict:
    vendor = entry.get("vendor", "")
    title = entry.get("title", "")
    url = entry.get("url", "")
    dt = entry.get("date", "")
    alive = entry.get("alive", True)

    # Fetch and extract abstract
    page_text = fetch_page_text(url) if alive else ""
    abstract = extract_abstract(page_text)

    # Classify relevance
    relevance = classify_relevance(title, abstract)

    # If completely irrelevant to AI/edge, skip
    if relevance == "irrelevant":
        return None

    # Generate tags
    tags = auto_tags(title, abstract)

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
        "venue": f"Official Blog",
        "alive": alive,
    }


def main() -> int:
    if not INPUT.exists():
        print(f"[ENRICH] ERROR: {INPUT} not found. Run collect_vendors.py first.")
        return 1

    raw = json.loads(INPUT.read_text(encoding="utf-8"))
    print(f"[ENRICH] loaded {len(raw)} vendor entries from {INPUT}")

    enriched = []
    skipped = 0
    for i, entry in enumerate(raw):
        vendor = entry.get("vendor", "?")
        title = entry.get("title", "?")[:50]
        print(f"  [{i+1}/{len(raw)}] {vendor}: {title}...")

        result = enrich_vendor_entry(entry)
        if result is None:
            skipped += 1
            print(f"    SKIP (irrelevant)")
            continue
        enriched.append(result)
        print(f"    OK: {result['tags'][:3]} rel={result['score_relevance']}")

    OUTPUT.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n[ENRICH] wrote {len(enriched)} candidates to {OUTPUT}")
    print(f"  skipped: {skipped} (irrelevant)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
