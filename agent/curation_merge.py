#!/usr/bin/env python3
"""Merge curation-subagent records into an assembled run.

Curation subagents (research_runs/curation/CURATION_SPEC.md) return one record per
paper id. This applies them to the run: reader-facing Chinese fields, scores,
tags, edge-agent scope, recommendation copy, and company attribution — keeping
the collection lineage so the result still validates against its manifest.

  python agent/curation_merge.py --run run.json --curated out_*.json \\
      [--decisions decisions.json] --out curated.json

decisions.json (main-agent editorial calls):
  {"force_drop": {"<id>": "中文理由"}, "not_edge_agent": ["<id>"],
   "reason_overrides": {"<id>": "推荐理由"}}
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

# Recognisable companies only. Small or secondary affiliations stay in the school
# tiers: "公司项目" is for research a known company leads.
COMPANIES = {
    "Google", "Apple", "Meta", "Microsoft", "NVIDIA", "Qualcomm", "Samsung", "Huawei", "MediaTek",
    "Xiaomi", "OPPO", "vivo", "Honor", "Alibaba", "ByteDance", "Tencent", "Baidu", "Kuaishou",
    "Meituan", "JD", "Pinduoduo", "NetEase", "Intel", "AMD", "Arm", "Amazon", "IBM", "Adobe",
    "Waymo", "Toyota Research Institute", "Xiaohongshu", "eBay", "NEC", "Midea",
    "Black Sesame Technologies", "d-Matrix", "SK hynix",
    "Anthropic", "OpenAI", "Mistral", "DeepSeek", "Moonshot", "Zhipu", "MiniMax", "Baichuan",
    "StepFun", "ModelBest", "Workday", "Ant Group", "Yandex", "Ericsson", "Shopify", "Salesforce",
    "Toshiba", "HP", "Panasonic", "iFLYTEK", "China Unicom", "China Mobile", "Nokia",
    "Changan Automobile", "ZTE", "Volkswagen", "Honda", "Cohere", "Scania", "PwC",
    "Lenovo", "LG", "Red Hat", "Hewlett Packard Enterprise", "AT&T", "Zoom", "Li Auto",
    "Rockwell Automation", "Qihoo 360", "Hitachi", "China Telecom", "Ping An", "Toyota", "Cisco", "Houmo AI", "Infineon", "NTT", "Snowflake", "Siemens", "Airbus", "Preferred Networks", "PayPal", "NIO", "BMW", "Fujitsu", "GlobalFoundries",
}
EDGE_SCOPES = ("手机", "PC", "其他端侧")
EDITABLE = ("abstract", "effects", "mechanism", "score_reason", "tags", "edge_agent_scope", "edge_agent_evidence")


def canonical_company(name: str) -> str:
    """'Microsoft Research Cambridge' -> 'Microsoft'; unknown or small firms -> ''."""
    name = (name or "").strip()
    for company in sorted(COMPANIES, key=len, reverse=True):
        if name == company or name.startswith(company + " ") or name.startswith(company + "（"):
            return company
    return ""


def apply_curation(paper: dict, cur: dict, *, keep_lineage: bool = True,
                   not_edge_agent: bool = False) -> dict | None:
    """Return the curated paper, or None when the curation record drops it."""
    if cur.get("drop"):
        return None
    q = {k: v for k, v in paper.items() if k not in ("source_summary", "categories")}
    for f in EDITABLE:
        q[f] = cur[f]
    q["score_relevance"], q["score_contribution"] = cur["score_relevance"], cur["score_contribution"]
    q["score"] = q["score_relevance"] + q["score_contribution"]
    q["open_source"] = bool(cur.get("open_source"))
    if cur.get("arxiv_revision_note"):
        q["arxiv_revision_note"] = cur["arxiv_revision_note"]
    if not_edge_agent:
        q["edge_agent_scope"], q["edge_agent_evidence"] = "非端侧Agent", ""
        q["tags"] = [t for t in q["tags"] if t != "方向:端侧agent"]
    research = paper.get("candidate_source", "arxiv") in ("arxiv", "huggingface", "")
    if research:
        if cur.get("venue"):
            q["venue"] = cur["venue"]
        comp = cur.get("company") or {}
        names = [canonical_company(n) for n in re.split(r"[;,]", comp.get("vendors") or "")]
        names = list(dict.fromkeys(n for n in names if n))
        if names and str(comp.get("evidence_url", "")).startswith("https://arxiv.org/pdf/"):
            q["source_tier"], q["vendors"] = "公司项目", "; ".join(names)
            q["affiliation_evidence_url"] = comp["evidence_url"]
            note = (comp.get("evidence_note") or "").strip().rstrip("。")
            q["score_reason"] = (q["score_reason"].rstrip() + f" 作者机构依据：arXiv PDF 首页署名 {', '.join(names)}"
                                 + (f"（{note}）" if note else "") + "。")
        else:
            q["vendors"], q["affiliation_evidence_url"] = "", ""
            q["source_tier"] = "学校顶会" if cur.get("accepted_top_venue") else "学校预印本"
    rec = bool(cur.get("recommend")) or q["edge_agent_scope"] in EDGE_SCOPES
    q["recommendation"] = "推荐" if rec else "纳入"
    q["title_zh"] = cur.get("title_zh", "") if rec else ""
    q["recommendation_reason"] = cur.get("recommendation_reason", "") if rec else ""
    if not keep_lineage:
        q.pop("candidate_source", None)
        q.pop("candidate_ref", None)
    return q


def merge_run(run: dict, curated: dict, decisions: dict | None = None) -> tuple[dict, list, list]:
    decisions = decisions or {}
    force_drop = decisions.get("force_drop") or {}
    not_edge = set(decisions.get("not_edge_agent") or [])
    overrides = decisions.get("reason_overrides") or {}
    out, dropped, missing = [], [], []
    for paper in run["papers"]:
        pid = paper["id"]
        cur = curated.get(pid)
        if cur is None:
            missing.append(pid)
            continue
        if pid in force_drop:
            dropped.append((pid, force_drop[pid]))
            continue
        q = apply_curation(paper, cur, not_edge_agent=pid in not_edge)
        if q is None:
            dropped.append((pid, cur.get("drop_reason", "")))
            continue
        if pid in overrides and q["recommendation"] == "推荐":
            q["recommendation_reason"] = overrides[pid]
        out.append(q)
    return {**run, "papers": out}, dropped, missing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--curated", nargs="+", required=True)
    ap.add_argument("--decisions")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    run = json.loads(Path(args.run).read_text(encoding="utf-8"))
    curated = {}
    for f in args.curated:
        curated.update(json.loads(Path(f).read_text(encoding="utf-8")))
    decisions = json.loads(Path(args.decisions).read_text(encoding="utf-8")) if args.decisions else {}
    merged, dropped, missing = merge_run(run, curated, decisions)
    if missing:
        print(f"[MERGE] curation missing for {len(missing)} paper(s): {missing[:8]}")
        return 1
    Path(args.out).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    papers = merged["papers"]
    print(f"[MERGE] kept {len(papers)}, dropped {len(dropped)} -> {args.out}")
    print("  tiers:", dict(Counter(p["source_tier"] for p in papers)))
    print("  recommended:", sum(p["recommendation"] == "推荐" for p in papers),
          "| edge agents:", dict(Counter(p["edge_agent_scope"] for p in papers if p["edge_agent_scope"] in EDGE_SCOPES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
