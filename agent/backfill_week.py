#!/usr/bin/env python3
"""Write a fully curated historical week into data/weeks/<label>.json.

The live pipeline publishes the current week to the server and lets app/build.py
archive it. A backfilled week must not become "current", so it is validated here
against its own window (EDGE_TODAY semantics: today = the week's last day) and
written straight to the archive, with its paper detail pages rendered into site/.

  python agent/backfill_week.py write --label 2026-05-08 --end 2026-05-14 \\
      --run run.json --weekly weekly.json --trending top20.json \\
      --community community.json [--hardware hardware.json]
  python agent/backfill_week.py set-hardware --label 2026-05-08 --hardware hw.json
  python agent/backfill_week.py set-community --label 2026-06-26 --community c.json
  python agent/backfill_week.py set-weekly --label 2026-06-26 --weekly weekly.json

Papers already published in another archived week are dropped (never two weeks).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT))

import research_run  # noqa: E402
from app import community, hardware  # noqa: E402
from app import weeks as weeks_mod  # noqa: E402
from research_collection import content_identity, published_identities  # noqa: E402

MIN_HIGHLIGHTS = 5


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _current_label() -> str | None:
    for entry in weeks_mod.read_manifest():
        if entry.get("current"):
            return entry["label"]
    return None


def _render_details(papers: list) -> None:
    from app.build import rewrite_detail  # noqa: E402
    from app.server import render_detail  # noqa: E402
    out = ROOT / "site" / "paper"
    out.mkdir(parents=True, exist_ok=True)
    for paper in papers:
        (out / f"{paper['id']}.html").write_text(rewrite_detail(render_detail(paper)), encoding="utf-8")


def check_weekly(weekly: dict, start: date, end: date) -> None:
    title = f"{start:%m-%d}~{end:%m-%d}"
    if title not in (weekly.get("overview") or ""):
        raise SystemExit(f"weekly overview must contain the window '{title}'")
    external = [h for h in weekly.get("highlights") or [] if str(h.get("url", "")).startswith("http")]
    if len(external) < MIN_HIGHLIGHTS:
        raise SystemExit(f"weekly needs >= {MIN_HIGHLIGHTS} external-URL highlights, has {len(external)}")


def check_hardware(block: dict, start: date, end: date) -> dict:
    block = hardware.validate_hardware(block)
    win = block["window"]
    if win["start"] < start.isoformat() or win["end"] > end.isoformat():
        raise SystemExit(f"hardware window {win} is outside the week {start}~{end}")
    return block


def cmd_write(args) -> int:
    start, end = date.fromisoformat(args.label), date.fromisoformat(args.end)
    run = _load(args.run)
    normalized = research_run.validate_payload(run, today=end, skip_network=True,
                                               require_collection_manifest=not args.no_manifest)
    others = published_identities(exclude_label=args.label)
    papers, dupes, reclaimed = [], [], []
    for paper in normalized["papers"]:
        week = others.get(content_identity(paper["paper_url"]))
        if week and _reclaim_hf_pick(paper, week):
            reclaimed.append((paper["id"], week))
            week = None
        (dupes if week else papers).append(paper if not week else (paper["id"], week))
    weekly = _load(args.weekly)
    check_weekly(weekly, start, end)
    # Highlight URLs are hand-written; one wrong slug ships a dead link. Flag any
    # that isn't an entry of this week so it gets copied from the curated run.
    listed = {p["paper_url"] for p in papers}
    for h in weekly.get("highlights") or []:
        if str(h.get("url", "")).startswith("http") and h["url"] not in listed:
            print(f"[BACKFILL] WARN highlight URL is not an entry of this week: {h['url']}")
    trending = _load(args.trending)
    trending = trending if isinstance(trending, dict) else {"items": trending}
    comm = community.validate_community(_load(args.community), today=end)
    hw = check_hardware(_load(args.hardware), start, end) if args.hardware else None
    meta = {"label": args.label, "title": f"{start:%m-%d}~{end:%m-%d}",
            "range": {"start": start.isoformat(), "end": end.isoformat()}}
    weeks_mod.write_archive(meta, papers, weekly, trending, comm, hw)
    weeks_mod.build_manifest(_current_label() or args.label)
    _render_details(papers)
    rec = sum(p.get("recommendation") == "推荐" for p in papers)
    print(f"[BACKFILL] {args.label}: {len(papers)} papers ({rec} recommended), "
          f"{len(comm['items'])} community, {len((hw or {}).get('items', []))} hardware; "
          f"dropped {len(dupes)} already in other weeks {dupes[:5]}; "
          f"reclaimed {len(reclaimed)} HF-dated picks from later weeks {reclaimed[:5]}")
    return 0


def _reclaim_hf_pick(paper: dict, label: str) -> bool:
    """Move an arXiv paper back from a later week that only holds its HF daily-pick copy.

    Hugging Face picks are dated by the day they were featured, often a week after
    arXiv submission. Live runs go forward, so the submission week's arXiv sweep
    claims the paper first; a backfill goes newest-first, so without this the later
    week's HF copy would win every time. Only an arxiv.org copy dated by submission
    reclaims, and only from a later week whose copy is the HF page.
    """
    rec = _reclaimable_from(paper, label)
    if rec is None:
        return False
    key = content_identity(paper["paper_url"])
    rec["papers"] = [p for p in rec["papers"] if content_identity(p["paper_url"]) != key]
    weeks_mod.archive_path(label).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def hf_pick_reclaimable(paper: dict, label: str) -> bool:
    """True when ``paper`` may take its HF-dated copy back from week ``label``.

    The assembler asks this before dropping an already-published entry, so the
    reclaim in ``write`` gets to see it.
    """
    return _reclaimable_from(paper, label) is not None


def _reclaimable_from(paper: dict, label: str) -> dict | None:
    """The later week's archive if it only holds ``paper`` as an HF pick it never featured."""
    if not str(paper.get("paper_url", "")).startswith("https://arxiv.org/abs/"):
        return None
    path = weeks_mod.archive_path(label)
    rec = json.loads(path.read_text(encoding="utf-8"))
    if rec["range"]["start"] <= paper["date"]:
        return None
    key = content_identity(paper["paper_url"])
    copies = [p for p in rec["papers"] if content_identity(p["paper_url"]) == key]
    if not copies or not all(str(p["paper_url"]).startswith("https://huggingface.co/papers/") for p in copies):
        return None
    # A week whose summary already features the paper keeps it: moving it would
    # leave that summary pointing at another week's item.
    featured = {content_identity(h.get("url", "")) for h in (rec.get("weekly") or {}).get("highlights") or []
                if str(h.get("url", "")).startswith("http")}
    if key in featured:
        return None
    return rec


def _update(label: str, key: str, block: dict) -> None:
    path = weeks_mod.archive_path(label)
    rec = json.loads(path.read_text(encoding="utf-8"))
    rec[key] = block
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_set_hardware(args) -> int:
    rec = weeks_mod.read_archive(args.label)
    start, end = date.fromisoformat(rec["range"]["start"]), date.fromisoformat(rec["range"]["end"])
    block = check_hardware(_load(args.hardware), start, end)
    _update(args.label, "hardware", block)
    print(f"[BACKFILL] {args.label}: hardware {len(block['items'])} items")
    return 0


def cmd_set_community(args) -> int:
    rec = weeks_mod.read_archive(args.label)
    start, end = date.fromisoformat(rec["range"]["start"]), date.fromisoformat(rec["range"]["end"])
    payload = _load(args.community)
    # Old-schema weeks overlap, so their radars use non-overlapping windows that can
    # end before the archive does; validate against the radar's own 7-day window.
    radar_end = date.fromisoformat((payload.get("window") or {}).get("end", end.isoformat()))
    if not start <= radar_end <= end:
        raise SystemExit(f"community window end {radar_end} is outside the week {start}~{end}")
    block = community.validate_community(payload, today=radar_end)
    _update(args.label, "community", block)
    print(f"[BACKFILL] {args.label}: community {len(block['items'])} items")
    return 0


def cmd_set_weekly(args) -> int:
    rec = weeks_mod.read_archive(args.label)
    start, end = date.fromisoformat(rec["range"]["start"]), date.fromisoformat(rec["range"]["end"])
    weekly = _load(args.weekly)
    check_weekly(weekly, start, end)
    listed = {p["paper_url"] for p in rec["papers"]}
    stray = [h["url"] for h in weekly.get("highlights") or []
             if str(h.get("url", "")).startswith("http") and h["url"] not in listed]
    if stray:
        raise SystemExit(f"highlight URLs are not entries of {args.label}: {stray}")
    _update(args.label, "weekly", weekly)
    print(f"[BACKFILL] {args.label}: weekly replaced, {len(weekly['highlights'])} highlights")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--label", required=True)
    w.add_argument("--end", required=True)
    w.add_argument("--run", required=True)
    w.add_argument("--weekly", required=True)
    w.add_argument("--trending", required=True)
    w.add_argument("--community", required=True)
    w.add_argument("--hardware")
    w.add_argument("--no-manifest", action="store_true", help="run without an embedded collection manifest")
    w.set_defaults(func=cmd_write)
    h = sub.add_parser("set-hardware")
    h.add_argument("--label", required=True)
    h.add_argument("--hardware", required=True)
    h.set_defaults(func=cmd_set_hardware)
    c = sub.add_parser("set-community")
    c.add_argument("--label", required=True)
    c.add_argument("--community", required=True)
    c.set_defaults(func=cmd_set_community)
    s = sub.add_parser("set-weekly")
    s.add_argument("--label", required=True)
    s.add_argument("--weekly", required=True)
    s.set_defaults(func=cmd_set_weekly)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
