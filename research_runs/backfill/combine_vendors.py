"""Combine vendors_A.json + vendors_B.json into candidates-vendor.json and the
manifest's vendors coverage.  usage: python combine_vendors.py RUN_DIR END"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent"))
from research_collection import REQUIRED_VENDOR_SOURCES, update_source_coverage
d = Path(sys.argv[1]); end = sys.argv[2]
cands, checks, seen = [], {}, set()
for name in ("vendors_A.json", "vendors_B.json"):
    blob = json.loads((d / name).read_text(encoding="utf-8"))
    for c in blob["candidates"]:
        if c["url"] in seen:
            continue
        seen.add(c["url"]); cands.append(c)
    checks.update(blob["vendor_checks"])
bad = []
for v in sorted(REQUIRED_VENDOR_SOURCES):
    ch = checks.get(v)
    if not ch or ch.get("status") not in ("found", "no_match") or not ch.get("sources_succeeded"):
        bad.append(v)
        continue
    ch["candidate_count"] = sum(c["vendor"] == v for c in cands)
    if ch["status"] == "found" and not ch["candidate_count"]:
        bad.append(v + "(found but 0)")
if bad:
    raise SystemExit(f"vendor checks incomplete: {bad}")
(d / "candidates-vendor.json").write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")
update_source_coverage(d / "collection-manifest.json", "vendors", {
    "status": "complete", "candidate_count": len(cands),
    "vendors_checked": sorted(REQUIRED_VENDOR_SOURCES), "vendor_checks": checks,
    "method": "historical-window official sources by vendor subagents (vendor-research-guide.md); collect_vendors.py discovery layer only",
}, today=end)
print(f"[VENDORS] {len(cands)} candidates; found: {sorted(v for v,c in checks.items() if c['status']=='found')}")
