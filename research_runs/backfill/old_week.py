"""Re-curate an already-published old-schema week with the current curation spec.

  python old_week.py export LABEL [--all]   -> research_runs/backfill/old-LABEL/{run.json,batches/input_N.json}
  python old_week.py apply LABEL            -> rewrites data/weeks/LABEL.json from batches/out_*.json

Old weeks (06-26 ~ 07-31) predate edge-agent scope and recommendation copy, and some
were auto-converted with English stub abstracts and keyword-guessed companies. Only
items without an edge_agent_scope are exported (``--all`` exports every item). Sources
and dates were verified when the week was published and are kept as-is; a curated drop
removes the item unless the week's summary features it.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT))

import backfill_week  # noqa: E402
from curation_merge import merge_run  # noqa: E402
from app import weeks as weeks_mod  # noqa: E402

SOURCES = {"arxiv": "arxiv", "vendor": "vendors", "github": "github", "hf": "huggingface"}


def run_dir(label):
    return Path(__file__).resolve().parent / f"old-{label}"


def export(label, everything):
    rec = weeks_mod.read_archive(label)
    papers = [{**p, "candidate_source": SOURCES.get(p["id"].split("-")[0], "arxiv")}
              for p in rec["papers"] if everything or "edge_agent_scope" not in p]
    d = run_dir(label)
    d.mkdir(exist_ok=True)
    (d / "run.json").write_text(json.dumps({"papers": papers}, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(Path(__file__).with_name("make_batches.py")), str(d), str(d / "run.json"), "34"],
                   check=True)


def apply(label):
    d = run_dir(label)
    run = json.loads((d / "run.json").read_text(encoding="utf-8"))
    curated = {}
    for f in sorted((d / "batches").glob("out_*.json")):
        curated.update(json.loads(f.read_text(encoding="utf-8")))
    rec = weeks_mod.read_archive(label)
    featured = {h.get("url") for h in (rec.get("weekly") or {}).get("highlights") or []}
    keep = {p["id"] for p in run["papers"] if p["paper_url"] in featured and curated.get(p["id"], {}).get("drop")}
    # A featured item the curator dropped stays as published: its record carries no
    # rewritten fields, and removing it would orphan the week's summary.
    run = {**run, "papers": [p for p in run["papers"] if p["id"] not in keep]}
    merged, dropped, missing = merge_run(run, curated)
    if missing:
        raise SystemExit(f"curation missing for {len(missing)}: {missing[:8]}")
    new = {p["id"]: {k: v for k, v in p.items() if k not in ("candidate_source", "candidate_ref")}
           for p in merged["papers"]}
    # Old GitHub entries carry keyword-guessed companies; a repo is not affiliation
    # evidence, so they file under 开源大项目 like every new-schema week.
    for pid, q in new.items():
        if pid.startswith("github-"):
            q["vendors"], q["source_tier"] = "", "开源大项目"
    gone = {pid for pid, _ in dropped}
    out = []
    for p in rec["papers"]:
        if p["id"] in gone:
            continue
        out.append({**p, **new[p["id"]]} if p["id"] in new else p)
    rec["papers"] = out
    weeks_mod.archive_path(label).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    backfill_week._render_details([p for p in out if p["id"] in new])
    rec_n = sum(p.get("recommendation") == "推荐" for p in out)
    print(f"[OLD-WEEK] {label}: {len(new)} re-curated, {len(gone)} dropped {sorted(gone)[:6]}, "
          f"kept featured as published {sorted(keep)}; now {len(out)} items, {rec_n} recommended")


if __name__ == "__main__":
    cmd, label = sys.argv[1], sys.argv[2]
    export(label, "--all" in sys.argv) if cmd == "export" else apply(label)
