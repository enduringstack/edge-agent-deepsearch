"""usage: python set_trending_zh.py RUN_DIR ZH_JSON  (ZH_JSON: {"owner/repo": "中文描述"})"""
import json, sys
from pathlib import Path
p = Path(sys.argv[1]) / "github_trending_top20.json"
zh = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
items = json.loads(p.read_text(encoding="utf-8"))
missing = [x["repo"] for x in items if x["repo"] not in zh]
if missing:
    raise SystemExit(f"missing translations: {missing}")
for x in items:
    x["desc"] = zh[x["repo"]]
p.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{p}: {len(items)} descriptions set")
