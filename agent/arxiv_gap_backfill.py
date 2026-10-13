#!/usr/bin/env python3
"""Backfill arXiv papers a published week never collected (e.g. the Monday-run
weekend gap) into that week's archive.

  1. collect:  python agent/arxiv_curl_sweep.py --since D1 --until D2 --out gap.json
  2. draft:    python agent/arxiv_gap_backfill.py draft --candidates gap.json --out drafts.json
               -> keeps relevant papers (same classifier as the weekly assembler) that are
                  not already in any archived week, in curation-input form
  3. curate:   subagents per research_runs/curation/CURATION_SPEC.md -> out_*.json
  4. apply:    python agent/arxiv_gap_backfill.py apply --week LABEL --drafts drafts.json
                   --curated out_a.json out_b.json ... [--extend-end D]
               -> validates every paper against that week's window and appends it to
                  data/weeks/<LABEL>.json (no paper ever lands in two weeks)

Detail pages for the added papers are written by `apply` into site/paper/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT))

import build_run_week  # noqa: E402
import research_run  # noqa: E402
from research_collection import content_identity, published_identities  # noqa: E402

WEEKS = ROOT / "data" / "weeks"
# Recognisable companies only; small or secondary affiliations stay in the school tiers.
COMPANIES = {
    "Google", "Apple", "Meta", "Microsoft", "NVIDIA", "Qualcomm", "Samsung", "Huawei", "MediaTek",
    "Xiaomi", "OPPO", "vivo", "Honor", "Alibaba", "ByteDance", "Tencent", "Baidu", "Kuaishou",
    "Meituan", "JD", "Pinduoduo", "NetEase", "Intel", "AMD", "Arm", "Amazon", "IBM", "Adobe",
    "Waymo", "Toyota Research Institute", "Xiaohongshu", "eBay", "NEC", "Midea",
    "Black Sesame Technologies", "d-Matrix", "SK hynix",
    "Anthropic", "OpenAI", "Mistral", "DeepSeek", "Moonshot", "Zhipu", "MiniMax", "Baichuan",
    "StepFun", "ModelBest", "Workday", "Ant Group", "Yandex", "Ericsson", "Shopify", "Salesforce", "Toshiba", "HP", "Panasonic", "iFLYTEK", "China Unicom", "China Mobile", "Nokia", "Changan Automobile", "ZTE", "Volkswagen", "Honda", "Cohere", "Scania", "PwC",
}
EDGE_SCOPES = ("手机", "PC", "其他端侧")

def canonical_company(name: str) -> str:
    """'Microsoft Research Cambridge' -> 'Microsoft'; unknown or small firms -> ''."""
    name = (name or "").strip()
    for company in sorted(COMPANIES, key=len, reverse=True):
        if name == company or name.startswith(company + " ") or name.startswith(company + "（"):
            return company
    return ""



def cmd_draft(args) -> int:
    cands = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    published = published_identities()
    drafts, seen = [], set()
    skipped_published = 0
    for c in cands:
        p = build_run_week.convert_arxiv(c)
        if not p:
            continue
        key = content_identity(p["paper_url"])
        if key in published:
            skipped_published += 1
            continue
        if key in seen:
            continue
        seen.add(key)
        drafts.append({
            **p,
            "source_summary": c.get("abstract") or c.get("summary") or "",
            "categories": c.get("categories"),
        })
    Path(args.out).write_text(json.dumps(drafts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[GAP] {len(cands)} candidates -> {len(drafts)} relevant drafts "
          f"({skipped_published} already published) -> {args.out}")
    return 0


def apply_curation(draft: dict, cur: dict) -> dict | None:
    """Turn a draft plus its curation record into a publishable paper, or None if dropped."""
    if cur.get("drop"):
        return None
    q = {k: v for k, v in draft.items() if k not in ("source_summary", "categories")}
    for f in ("abstract", "effects", "mechanism", "score_reason", "tags", "edge_agent_scope", "edge_agent_evidence"):
        q[f] = cur[f]
    q["score_relevance"], q["score_contribution"] = cur["score_relevance"], cur["score_contribution"]
    q["score"] = q["score_relevance"] + q["score_contribution"]
    q["open_source"] = bool(cur.get("open_source"))
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
    # archived papers carry no collection lineage
    q.pop("candidate_source", None)
    q.pop("candidate_ref", None)
    return q


def cmd_apply(args) -> int:
    label = args.week
    path = WEEKS / f"{label}.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    drafts = {d["id"]: d for d in json.loads(Path(args.drafts).read_text(encoding="utf-8"))}
    cur = {}
    for f in args.curated:
        cur.update(json.loads(Path(f).read_text(encoding="utf-8")))
    missing = [pid for pid in drafts if pid not in cur]
    if missing:
        print(f"[GAP] curation missing for {len(missing)} draft(s): {missing[:5]}")
        return 1
    if args.extend_end:
        rec["range"]["end"] = args.extend_end
        rec["title"] = f"{rec['range']['start'][5:]}~{args.extend_end[5:]}"
    end = date.fromisoformat(rec["range"]["end"])
    start = date.fromisoformat(rec["range"]["start"])
    vocab = research_run.load_tag_vocab()
    published = published_identities()
    existing_ids = {p["id"] for p in rec["papers"]}
    added, dropped = [], 0
    for pid, draft in drafts.items():
        paper = apply_curation(draft, cur[pid])
        if paper is None:
            dropped += 1
            continue
        if content_identity(paper["paper_url"]) in published or pid in existing_ids:
            continue  # published meanwhile; never let a paper land in two weeks
        day = date.fromisoformat(paper["date"])
        if not start <= day <= end:
            print(f"[GAP] {pid}: {day} outside week {start}~{end}, skipped")
            continue
        normalized = research_run.normalize_paper(paper, end, set(), vocab, skip_network=True)
        added.append({**paper, **{k: normalized[k] for k in ("tags",)}})
    rec["papers"].extend(added)
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.extend_end:
        manifest_path = WEEKS / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest:
            if entry["label"] == label:
                entry["range"]["end"], entry["title"] = rec["range"]["end"], rec["title"]
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    from app.build import rewrite_detail  # noqa: E402
    from app.server import render_detail  # noqa: E402
    out_dir = ROOT / "site" / "paper"
    out_dir.mkdir(parents=True, exist_ok=True)
    for paper in added:
        (out_dir / f"{paper['id']}.html").write_text(rewrite_detail(render_detail(paper)), encoding="utf-8")
    print(f"[GAP] {label}: +{len(added)} papers ({dropped} dropped in curation, "
          f"{sum(p['recommendation'] == '推荐' for p in added)} recommended); detail pages written")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draft")
    d.add_argument("--candidates", required=True)
    d.add_argument("--out", required=True)
    d.set_defaults(func=cmd_draft)
    a = sub.add_parser("apply")
    a.add_argument("--week", required=True)
    a.add_argument("--drafts", required=True)
    a.add_argument("--curated", nargs="+", required=True)
    a.add_argument("--extend-end", help="move the week's range end (for a day no week covered)")
    a.set_defaults(func=cmd_apply)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
