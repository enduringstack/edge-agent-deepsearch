"""Re-bucket overlapping old weeks into contiguous windows.

  python restructure_weeks.py            # dry run: show where every entry would go
  python restructure_weeks.py --apply    # write the new archives, delete retired labels

Weeks 06-26 ~ 08-18 overlapped (8-day, 6-day, 4-day and 1-day windows) and 09-16 ~ 09-22
overlapped 09-22. Entries, hardware items and community items move to the week that
contains their date; anything dated outside the restructured span stays with the new
week that replaces its old one. Summaries of the rebuilt weeks must be rewritten after.
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from app import weeks as weeks_mod  # noqa: E402

NEW = {  # label -> (start, end)
    "2026-06-26": ("2026-06-26", "2026-07-02"),
    "2026-07-03": ("2026-07-03", "2026-07-09"),
    "2026-07-10": ("2026-07-10", "2026-07-16"),
    "2026-07-17": ("2026-07-17", "2026-07-23"),
    "2026-07-24": ("2026-07-24", "2026-07-30"),
    "2026-07-31": ("2026-07-31", "2026-08-06"),
    "2026-08-07": ("2026-08-07", "2026-08-13"),
    "2026-08-14": ("2026-08-14", "2026-08-18"),
    "2026-09-16": ("2026-09-16", "2026-09-21"),
}
OLD_TO_NEW = {"2026-06-26": "2026-06-26", "2026-07-02": "2026-07-03", "2026-07-10": "2026-07-10",
              "2026-07-17": "2026-07-17", "2026-07-25": "2026-07-24", "2026-07-31": "2026-07-31",
              "2026-08-01": "2026-07-31", "2026-08-05": "2026-07-31", "2026-08-07": "2026-08-07",
              "2026-08-12": "2026-08-14", "2026-09-16": "2026-09-16"}
RETIRED = sorted(set(OLD_TO_NEW) - set(NEW))
# The new week whose trending snapshot is reused (taken from the old week it mostly replaces).
TRENDING_FROM = {v: k for k, v in OLD_TO_NEW.items() if k in ("2026-06-26", "2026-07-02", "2026-07-10",
                 "2026-07-17", "2026-07-25", "2026-07-31", "2026-08-07", "2026-08-12", "2026-09-16")}


def home(day, old):
    for label, (s, e) in NEW.items():
        if s <= (day or "") <= e:
            return label
    return OLD_TO_NEW[old]


def main(apply):
    old = {l: weeks_mod.read_archive(l) for l in OLD_TO_NEW}
    papers, hw, comm = defaultdict(list), defaultdict(list), defaultdict(list)
    moves = Counter()
    for l, rec in old.items():
        for p in rec["papers"]:
            n = home(p.get("date"), l); papers[n].append(p); moves[(l, n)] += 1
        for it in (rec.get("hardware") or {}).get("items") or []:
            hw[home(it.get("date"), l)].append(it)
        for it in (rec.get("community") or {}).get("items") or []:
            comm[home(str(it.get("published_at", ""))[:10], l)].append(it)
    for (a, b), n in sorted(moves.items()):
        print(f"  {a} -> {b}: {n}")
    for l in NEW:
        print(f"{l} {NEW[l]}: {len(papers[l])} entries, {sum(p.get('recommendation') == '推荐' for p in papers[l])} rec, "
              f"{len(hw[l])} hardware, {len(comm[l])} community")
    if not apply:
        return 0
    for l, (s, e) in NEW.items():
        base = old.get(l) or old[TRENDING_FROM[l]]
        seen, ps = set(), []
        for p in papers[l]:
            if p["id"] not in seen:
                seen.add(p["id"]); ps.append(p)
        rec = {k: v for k, v in base.items() if k not in ("papers", "hardware", "community", "weekly")}
        rec.update({"label": l, "title": f"{s[5:]}~{e[5:]}", "range": {"start": s, "end": e}, "papers": ps,
                    "trending": old[TRENDING_FROM[l]].get("trending"),
                    "weekly": {"overview": "", "highlights": []}})
        hbase = dict((old.get(l) or old[TRENDING_FROM[l]]).get("hardware") or {})
        if hbase or hw[l]:
            hbase.update({"window": {"start": s, "end": e}, "items": hw[l]})
            rec["hardware"] = hbase
        cbase = dict((old.get(l) or old[TRENDING_FROM[l]]).get("community") or {})
        # The community validator wants a 7-day window ending inside the week.
        cstart = (date.fromisoformat(e) - timedelta(days=6)).isoformat()
        cbase.update({"window": {"start": cstart, "end": e}, "items": comm[l]})
        rec["community"] = cbase
        weeks_mod.archive_path(l).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    for l in RETIRED:
        weeks_mod.archive_path(l).unlink()
    cur = next(e["label"] for e in weeks_mod.read_manifest() if e.get("current"))
    weeks_mod.build_manifest(cur)
    print("[RESTRUCTURE] retired", RETIRED)
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
