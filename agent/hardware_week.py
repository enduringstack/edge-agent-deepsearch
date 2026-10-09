#!/usr/bin/env python3
"""Weekly 硬件雷达 + monthly 硬件洞察 helper for the main agent.

Research subagents (see docs/agent-guide/hardware-radar.md) each write one
JSON file ``{"topic", "new_items": [...], "section_md"}``. This script does the
mechanical part around them:

  merge  combine subagent files -> dedupe (within the batch and against every
         archived week) -> drop out-of-window items -> attach the main agent's
         overview/takeaways -> validate -> write data/hardware_radar.json
  check  validate data/hardware_radar.json and require it to cover this week
  month  assemble a monthly 硬件洞察 markdown (head + subagent sections + tail)
         into data/hardware-insights/YYYY-MM.md and update index.json

Usage:
  python agent/hardware_week.py merge research_runs/hardware/deep_*.json \\
      --text research_runs/hardware/weekly_text.json [--start D --end D] [--dry-run]
  python agent/hardware_week.py check
  python agent/hardware_week.py month --month 2026-10 --title "2026-10-08 ~ 2026-11-04" \\
      --head head.md --part "deep_qualcomm.json::高通：…" --part extra.md::标题 --tail tail.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import hardware  # noqa: E402

DATA = ROOT / "data"
RADAR = DATA / "hardware_radar.json"
WEEKS = DATA / "weeks"
INSIGHTS = DATA / "hardware-insights"
CJK = re.compile(r"[㐀-鿿]")
FIELDS = ("date", "vendor", "category", "title", "title_zh", "url", "source_type", "summary_zh",
          "whats_new_zh", "key_specs", "edge_ai_impact_zh", "evidence_urls", "confidence",
          "venue", "affiliation", "authors", "model_capacity_zh", "deep_dive_zh")
MAX_DEEP_BLOCKS = 7
MAX_EVIDENCE = 5


def url_key(url: str) -> str:
    """Identity for dedupe: arXiv abs/pdf/html collapse to one id; else the URL sans trailing /."""
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", url or "")
    return f"arxiv:{m.group(1)}" if m else (url or "").rstrip("/")


def _clean_deep(blocks) -> list:
    out = []
    for b in blocks or []:
        if isinstance(b, dict) and CJK.search(b.get("heading") or ""):
            pts = [p.strip() for p in b.get("points") or [] if isinstance(p, str) and p.strip()]
            if pts:
                out.append({"heading": b["heading"].strip(), "points": pts})
    return out


def _clean_capacity(text) -> str:
    text = re.sub(r"^(能跑多大的模型|对端侧模型容量的影响)[^：:]*[：:]\s*", "", (text or "").strip())
    if not text or text.startswith("不适用") or text in ("未披露", "未披露。") or not CJK.search(text):
        return ""
    return text


def _absorb(item: dict, src: dict) -> None:
    """Fold a duplicate's capacity, deep-dive blocks, evidence and paper meta into ``item``."""
    cap = _clean_capacity(src.get("model_capacity_zh"))
    if cap and not item.get("model_capacity_zh"):
        item["model_capacity_zh"] = cap
    blocks = list(item.get("deep_dive_zh") or [])
    have = {d["heading"] for d in blocks}
    for d in _clean_deep(src.get("deep_dive_zh")):
        if d["heading"] not in have and len(blocks) < MAX_DEEP_BLOCKS:
            blocks.append(d)
            have.add(d["heading"])
    item["deep_dive_zh"] = blocks
    evidence = list(item.get("evidence_urls") or [])
    extra = (src.get("extra_evidence_urls") or []) + (src.get("evidence_urls") or [])
    if src.get("url") and src["url"] != item["url"]:
        extra = [src["url"]] + extra
    for u in extra:
        if isinstance(u, str) and u.startswith("http") and u != item["url"] and u not in evidence:
            evidence.append(u)
    item["evidence_urls"] = evidence[:MAX_EVIDENCE]
    for k in ("venue", "affiliation", "authors"):
        if src.get(k) and not item.get(k):
            item[k] = src[k]


def normalise(raw: dict) -> dict:
    item = {f: raw[f] for f in FIELDS if f in raw}
    item["key_specs"] = {k: v for k, v in (item.get("key_specs") or {}).items()
                         if isinstance(v, str) and v and k in hardware.SPEC_KEYS}
    item["whats_new_zh"] = [x for x in item.get("whats_new_zh") or [] if isinstance(x, str) and CJK.search(x)]
    item["evidence_urls"] = []
    item["deep_dive_zh"] = []
    item.pop("model_capacity_zh", None)
    _absorb(item, {**raw, "url": item.get("url")})
    if item.get("category") == "学术研究":
        item.setdefault("venue", "arXiv")
        if item.get("source_type") not in ("论文", "官方"):
            item["source_type"] = "论文"
    return item


def archived_keys(start: date, end: date) -> dict:
    """url_key -> week label for every archived hardware item outside [start, end]."""
    seen = {}
    for p in sorted(WEEKS.glob("*.json")):
        if p.name == "manifest.json":
            continue
        block = (json.loads(p.read_text(encoding="utf-8")) or {}).get("hardware") or {}
        win = block.get("window") or {}
        try:
            overlaps = date.fromisoformat(win["start"]) <= end and date.fromisoformat(win["end"]) >= start
        except (KeyError, TypeError, ValueError):
            overlaps = False
        if overlaps:  # the archive of this same week: a re-run must not dedupe against itself
            continue
        for it in block.get("items") or []:
            seen.setdefault(url_key(it.get("url")), p.stem)
    return seen


def merge(paths, start: date, end: date, *, dupes=None, drop=()) -> tuple:
    """Return (items, report) after normalising, deduping and window-filtering."""
    items, by_key = [], {}
    report = {"in_batch_dupes": 0, "archived_dupes": [], "outside": [], "dropped": []}
    for path in paths:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        raws = payload.get("new_items") or payload.get("items") or []
        for raw in raws:
            if not isinstance(raw, dict) or not raw.get("url"):
                continue
            key = url_key(raw["url"])
            if key in by_key:
                _absorb(by_key[key], raw)
                report["in_batch_dupes"] += 1
                continue
            it = normalise(raw)
            by_key[key] = it
            items.append(it)
    for dup, canon in (dupes or {}).items():  # main-agent decided: same news, different URLs
        d = next((i for i in items if i["url"].startswith(dup)), None)
        c = next((i for i in items if i["url"].startswith(canon)), None)
        if d and c and d is not c:
            _absorb(c, d)
            items.remove(d)
            report["in_batch_dupes"] += 1
    kept = []
    archived = archived_keys(start, end)
    for it in items:
        if any(it["url"].startswith(p) for p in drop):
            report["dropped"].append(it["url"])
        elif url_key(it["url"]) in archived:
            report["archived_dupes"].append((it["url"], archived[url_key(it["url"])]))
        elif not (start.isoformat() <= str(it.get("date", "")) <= end.isoformat()):
            report["outside"].append((it.get("date"), it.get("title_zh")))
        else:
            kept.append(it)
    return kept, report


def cmd_merge(args) -> int:
    today = date.today()
    start = date.fromisoformat(args.start) if args.start else today - timedelta(days=hardware.WEEK_DAYS - 1)
    end = date.fromisoformat(args.end) if args.end else today
    dupes = json.loads(Path(args.dupes).read_text(encoding="utf-8")) if args.dupes else {}
    items, report = merge(args.inputs, start, end, dupes=dupes, drop=args.drop or ())
    print(f"[HW] window {start}~{end}: {len(items)} item(s); "
          f"batch dupes folded {report['in_batch_dupes']}, "
          f"already in archived weeks {len(report['archived_dupes'])}, "
          f"outside window {len(report['outside'])}, dropped {len(report['dropped'])}")
    for url, label in report["archived_dupes"]:
        print(f"  archived in {label}: {url}")
    for d, t in report["outside"]:
        print(f"  outside window: {d} {t}")
    counts = {}
    for it in items:
        counts[it["category"]] = counts.get(it["category"], 0) + 1
    print("  by category:", ", ".join(f"{k} {v}" for k, v in counts.items()))
    print("  with model capacity:", sum(1 for i in items if i.get("model_capacity_zh")),
          "| with deep dive:", sum(1 for i in items if i.get("deep_dive_zh")))

    payload = {"window": {"start": start.isoformat(), "end": end.isoformat()}, "items": items}
    if args.text:
        text = json.loads(Path(args.text).read_text(encoding="utf-8"))
        payload["overview"] = text.get("overview", "")
        payload["takeaways_zh"] = text.get("takeaways") or text.get("takeaways_zh") or []
    else:
        payload["overview"] = "（主 agent 待写本周综述）"
        payload["takeaways_zh"] = []
    try:
        block = hardware.validate_hardware(payload)
    except hardware.HardwareValidationError as exc:
        print(f"[HW] INVALID: {exc}")
        return 1
    if args.dry_run or not args.text:
        print("[HW] dry run — pass --text <overview/takeaways json> to write", args.out)
        return 0
    Path(args.out).write_text(json.dumps(block, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[HW] wrote {args.out}")
    return 0


def cmd_check(args) -> int:
    try:
        block = hardware.load_hardware(Path(args.path))
        hardware.check_fresh(block, date.today())
    except hardware.HardwareValidationError as exc:
        print(f"[HW] FAIL: {exc}")
        return 1
    win = block["window"]
    print(f"[HW] OK: {args.path} {win['start']}~{win['end']}, {len(block['items'])} item(s)")
    return 0


def _part_text(spec: str) -> tuple:
    path, _, heading = spec.partition("::")
    p = Path(path)
    body = json.loads(p.read_text(encoding="utf-8"))["section_md"] if p.suffix == ".json" \
        else p.read_text(encoding="utf-8")
    return heading.strip(), body.strip()


def cmd_month(args) -> int:
    if not re.fullmatch(r"\d{4}-\d{2}", args.month):
        print("[HW] --month must be YYYY-MM")
        return 1
    entry = {"month": args.month, "title": args.title, "file": f"{args.month}.md"}
    try:
        hardware.insight_end(entry)
    except hardware.HardwareValidationError as exc:
        print(f"[HW] {exc}")
        return 1
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8").strip() + "\n"
    else:
        parts = [Path(args.head).read_text(encoding="utf-8").strip()] if args.head else []
        for n, spec in enumerate(args.part or [], 1):
            heading, body = _part_text(spec)
            parts.append(f"## {n}. {heading}\n\n{body}" if heading else body)
        if args.tail:
            parts.append(Path(args.tail).read_text(encoding="utf-8").strip())
        text = "\n\n".join(parts) + "\n"
    if not text.lstrip().startswith("# "):
        print("[HW] monthly insight must start with a '# ' title line")
        return 1
    INSIGHTS.mkdir(parents=True, exist_ok=True)
    (INSIGHTS / entry["file"]).write_text(text, encoding="utf-8")
    index_path = INSIGHTS / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    index = [e for e in index if e.get("month") != args.month] + [entry]
    index.sort(key=lambda e: e["month"], reverse=True)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[HW] wrote {INSIGHTS / entry['file']} ({len(text)} chars); index has {len(index)} month(s)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge", help="merge subagent files into data/hardware_radar.json")
    m.add_argument("inputs", nargs="+")
    m.add_argument("--start", help="window start (default: today-6)")
    m.add_argument("--end", help="window end (default: today)")
    m.add_argument("--text", help='JSON {"overview": "...", "takeaways": [...]} written by the main agent')
    m.add_argument("--dupes", help='JSON {"dup url prefix": "canonical url prefix"} to fold same-news items')
    m.add_argument("--drop", action="append", help="url prefix to drop (repeatable)")
    m.add_argument("--out", default=str(RADAR))
    m.add_argument("--dry-run", action="store_true")
    m.set_defaults(func=cmd_merge)
    c = sub.add_parser("check", help="validate data/hardware_radar.json covers this week")
    c.add_argument("--path", default=str(RADAR))
    c.set_defaults(func=cmd_check)
    mo = sub.add_parser("month", help="assemble a monthly 硬件洞察 and update the index")
    mo.add_argument("--month", required=True)
    mo.add_argument("--title", required=True, help="'YYYY-MM-DD ~ YYYY-MM-DD'")
    mo.add_argument("--file", help="a finished markdown file (instead of head/part/tail)")
    mo.add_argument("--head")
    mo.add_argument("--part", action="append", help="'deep_x.json::小节标题' or 'x.md::小节标题'")
    mo.add_argument("--tail")
    mo.set_defaults(func=cmd_month)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
