"""Self-check for a curation batch: python -X utf8 check_batch.py <input.json> <output.json>"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
import research_run  # noqa: E402

CJK = re.compile(r"[㐀-鿿]")
BANNED = re.compile(r"auto-converted|votes=|待核实|精修待补|自动初评|(?<!自)主\s*Agent|复核")
SCOPES = {"手机", "PC", "其他端侧", "非端侧Agent"}

inp = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
vocab = research_run.load_tag_vocab()
errors = []
for item in inp:
    pid = item["id"]
    o = out.get(pid)
    if o is None:
        errors.append(f"{pid}: missing")
        continue
    if o.get("drop"):
        if not o.get("drop_reason"):
            errors.append(f"{pid}: drop needs drop_reason")
        continue
    for f in ("abstract", "effects", "mechanism", "score_reason"):
        v = str(o.get(f) or "")
        if f == "effects" and v == "未报告":
            continue
        if len(CJK.findall(v)) < 8:
            errors.append(f"{pid}: {f} 需要可读中文")
        if BANNED.search(v):
            errors.append(f"{pid}: {f} 含流程词")
        if v.rstrip().endswith(("…", "...")):
            errors.append(f"{pid}: {f} 以省略号结尾")
    for f in ("score_relevance", "score_contribution"):
        if not isinstance(o.get(f), int) or not 0 <= o[f] <= 10:
            errors.append(f"{pid}: {f} 必须是 0-10 整数")
    tags = o.get("tags") or []
    if not 1 <= len(tags) <= 8:
        errors.append(f"{pid}: tags 需要 1-8 个")
    try:
        research_run.normalize_tags(tags, pid, vocab)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{pid}: tags {exc}")
    scope = o.get("edge_agent_scope")
    if scope not in SCOPES:
        errors.append(f"{pid}: edge_agent_scope 非法")
    elif scope != "非端侧Agent":
        if len(CJK.findall(o.get("edge_agent_evidence") or "")) < 8:
            errors.append(f"{pid}: 端侧 Agent 需要中文 edge_agent_evidence")
        if "方向:端侧agent" not in tags or (o.get("score_relevance") or 0) < 8 or not o.get("recommend"):
            errors.append(f"{pid}: 端侧 Agent 必须带 方向:端侧agent、相关度>=8 且 recommend")
    elif "方向:端侧agent" in tags:
        errors.append(f"{pid}: 非端侧Agent 不得使用 方向:端侧agent")
    if o.get("recommend"):
        tz = o.get("title_zh") or ""
        if len(CJK.findall(tz)) < 2 or len(tz) > 40:
            errors.append(f"{pid}: title_zh 需要 2+ 中文字、<=40 字")
        if len(CJK.findall(o.get("recommendation_reason") or "")) < 8:
            errors.append(f"{pid}: recommendation_reason 需要中文")
    comp = o.get("company") or {}
    if comp.get("vendors") and not str(comp.get("evidence_url", "")).startswith("https://arxiv.org/pdf/"):
        errors.append(f"{pid}: company 需要 arXiv PDF 证据 URL")
print("\n".join(errors) if errors else f"OK {len(inp)} items")
