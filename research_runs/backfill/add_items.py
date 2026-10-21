"""Add recall-audit catches to an already archived week.

  python add_items.py LABEL items.json [--dry-run]

items.json is a list of fully curated entries in the run schema (same fields as a
curated run's papers). They are validated with the publish-time content rules
against the week's own window (EDGE_TODAY semantics: today = the week's last day),
without a collection manifest: recall catches come from the audit, not a sweep.
Anything already published in another week is refused, and detail pages are
rendered for the new entries.
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT))

import backfill_week  # noqa: E402
import research_run  # noqa: E402
from app import weeks as weeks_mod  # noqa: E402
from research_collection import content_identity, published_identities  # noqa: E402


def main(label: str, items_path: str, dry_run: bool) -> int:
    rec = weeks_mod.read_archive(label)
    end = date.fromisoformat(rec["range"]["end"])
    items = json.loads(Path(items_path).read_text(encoding="utf-8"))
    payload = {"run_id": f"recall-{label}", "generated_at": f"{end.isoformat()}T23:59:00+00:00", "papers": items}
    normalized = research_run.validate_payload(payload, today=end, skip_network=True)
    start = rec["range"]["start"]
    others = published_identities(exclude_label=None)
    added = []
    for paper in normalized["papers"]:
        if paper["date"] < start:
            raise SystemExit(f"{paper['id']}: date {paper['date']} is before the week {start}")
        week = others.get(content_identity(paper["paper_url"]))
        if week:
            raise SystemExit(f"{paper['id']}: already published in {week}")
        added.append(paper)
    print(f"[ADD] {label}: {len(added)} entr(ies) pass validation: {[p['id'] for p in added]}")
    if dry_run:
        return 0
    rec["papers"].extend(added)
    weeks_mod.archive_path(label).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    backfill_week._render_details(added)
    print(f"[ADD] {label}: now {len(rec['papers'])} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2], "--dry-run" in sys.argv))
