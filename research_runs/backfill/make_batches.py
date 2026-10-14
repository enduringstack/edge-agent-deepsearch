"""Curation input batches from an assembled backfill run (ids match the run).
usage: python make_batches.py RUN_DIR RUN_JSON BATCH_SIZE [--only-new]
Writes RUN_DIR/batches/input_N.json; curated outputs go to RUN_DIR/batches/out_N.json."""
import glob, json, re, sys
from pathlib import Path
d = Path(sys.argv[1]); run = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")); size = int(sys.argv[3])
ld = lambda n: json.loads((d / n).read_text(encoding="utf-8")) if (d / n).exists() else []
summ = {}
for c in ld("arxiv_candidates.json"):
    summ["https://arxiv.org/abs/" + re.sub(r"v\d+$", "", str(c.get("id")))] = c.get("abstract") or c.get("summary") or ""
for c in ld("candidates-vendor.json"):
    summ[c["url"]] = (c.get("summary") or "") + ("\n[采集备注] " + c["edge_note"] if c.get("edge_note") else "")
for c in ld("candidates-github.json"):
    summ[c["release_url"]] = c.get("summary") or ""
for c in ld("candidates-hf.json"):
    for k in ("url", "paper_url"):
        if c.get(k): summ.setdefault(c[k], c.get("summary") or c.get("abstract") or "")
out = d / "batches"; out.mkdir(exist_ok=True)
done = set()
if "--only-new" in sys.argv:
    for f in glob.glob(str(out / "out_*.json")):
        done |= set(json.loads(Path(f).read_text(encoding="utf-8")))
items = [{**p, "source_summary": summ.get(p["paper_url"], "")} for p in run["papers"] if p["id"] not in done]
items.sort(key=lambda p: (p.get("candidate_source") not in ("vendors", "github"), p["id"]))
start = len(glob.glob(str(out / "input_*.json")))
n = 0
for i in range(0, len(items), size):
    n += 1
    (out / f"input_{start + n}.json").write_text(json.dumps(items[i:i+size], ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(items)} items -> batches input_{start+1}..input_{start+n}; missing summary: {sum(not x['source_summary'] for x in items)}")
