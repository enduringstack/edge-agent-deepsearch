"""Keep every item in exactly one archived week.

  python dedupe_weeks.py            # report duplicates and the copy that would be kept
  python dedupe_weeks.py --apply    # drop the other copies from data/weeks/*.json

Old-schema weeks overlap (07-31 ~ 08-03, 08-01 ~ 08-07, 08-05) and predate the
published-identity check, so the same paper landed in several weeks. The kept copy is,
in order: the one a week's summary features; a recommended one; the earliest dated;
the earliest week. A paper featured by two summaries keeps one copy by the same order; the
weeks that lose a featured entry are listed so their summaries get rewritten.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT))

from app import weeks as weeks_mod  # noqa: E402
from research_collection import content_identity  # noqa: E402


def main(apply: bool) -> int:
    weeks = {}
    for path in sorted(weeks_mod.WEEKS_DIR.glob("2026-*.json")):
        weeks[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    copies = defaultdict(list)
    for label, rec in weeks.items():
        featured = {content_identity(h.get("url", "")) for h in (rec.get("weekly") or {}).get("highlights") or []}
        for p in rec["papers"]:
            key = content_identity(p["paper_url"])
            copies[key].append((label, p, key in featured))
    drop = defaultdict(set)
    conflicts = []
    for key, cs in copies.items():
        if len(cs) < 2:
            continue
        keep = min(cs, key=lambda c: (not c[2], c[1].get("recommendation") != "推荐", c[1]["date"], c[0]))
        lost = [c[0] for c in cs if c[2] and c is not keep]
        if lost:
            conflicts.append((key, lost))
        for label, p, _ in cs:
            if (label, p["id"]) != (keep[0], keep[1]["id"]):
                drop[label].add(p["id"])
        print(f"{key}: keep {keep[0]} ({keep[1]['date']}); drop {[c[0] for c in cs if c is not keep]}")
    for key, labels in conflicts:
        print(f"[REWRITE SUMMARY] {labels} lose featured {key}")
    print(f"[DEDUPE] {sum(map(len, drop.values()))} copies to drop across {len(drop)} weeks; "
          f"{len(conflicts)} featured in two summaries")
    if apply:
        for label, ids in drop.items():
            rec = weeks[label]
            rec["papers"] = [p for p in rec["papers"] if p["id"] not in ids]
            weeks_mod.archive_path(label).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  {label}: -{len(ids)} -> {len(rec['papers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
