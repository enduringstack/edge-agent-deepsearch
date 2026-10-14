"""Render the 6 hardware-radar subagent prompts for one backfill month.
usage: python gen_hw_prompts.py TAG ITEM_START ITEM_END SECTION_START SECTION_END [CONTEXT_MD]
  -> prompts/hw-TAG/<direction>.txt ; outputs land in research_runs/backfill/hw-TAG/deep_*.json
New items are limited to ITEM_START..ITEM_END; section_md covers SECTION_START..SECTION_END
(the month report window). CONTEXT_MD: an existing month report the section may build on."""
import re, sys
from pathlib import Path
here = Path(__file__).resolve().parent
root = here.parents[1]
tag, i0, i1, s0, s1 = sys.argv[1:6]
ctx = sys.argv[6] if len(sys.argv) > 6 else ""
doc = (root / "docs/agent-guide/hardware-radar.md").read_text(encoding="utf-8")
m = re.search(r"(## 2\. 调研方向.*?)(?=\n## 5\. )", doc, re.S)
rules = m.group(1).strip()
dirs = [("deep_qualcomm.json", "1（高通）"), ("deep_apple.json", "2（Apple 与 Google）"),
        ("deep_soc.json", "3（其他 SoC、PC 与产业）"), ("deep_lowpower.json", "4（低功耗、存内计算与内存）"),
        ("deep_papers_venues.json", "5（顶会论文）"), ("deep_papers_arxiv.json", "6（arXiv）")]
out_dir = root / "research_runs/backfill" / f"hw-{tag}"
out_dir.mkdir(parents=True, exist_ok=True)
pdir = here / "prompts" / f"hw-{tag}"
pdir.mkdir(parents=True, exist_ok=True)
weeks = sorted(p.stem for p in (root / "data/weeks").glob("2026-*.json"))
for fname, name in dirs:
    text = f"""你是“端侧 AI 论文雷达”的**硬件雷达**调研子 agent，负责第 2 节表格里的方向 {name}，本次是**历史回填**（今天是 2026-10-13，窗口是过去的时间）。

## 本次任务
- `new_items`：只收真实发布日在 **{i0} ~ {i1}** 的条目（这段时间此前没有做过硬件雷达）。
- `section_md`：**必须写**，覆盖整个月报窗口 **{s0} ~ {s1}**，2500–5000 字，总-分-总，内联链接。窗口里 {i0}~{i1} 以外的时间段已有各周硬件雷达条目，见 `C:/Users/guanjungao/Desktop/chenfuduo/reportweekly/repo/data/weeks/<label>.json` 的 `hardware.items`（label 为该周起始日；相关周：{', '.join(w for w in weeks if s0[:7] in w or i0[:7] in w)}），写 section 时要把它们与你的新条目一起综合，但不要把那些已收条目再放进 new_items。{('已有该月旧版月报可作背景（只覆盖部分窗口，需扩写为全窗口）：`C:/Users/guanjungao/Desktop/chenfuduo/reportweekly/repo/' + ctx + '`。') if ctx else ''}
- 输出写到：`C:/Users/guanjungao/Desktop/chenfuduo/reportweekly/repo/research_runs/backfill/hw-{tag}/{fname}`（`json.dump(..., ensure_ascii=False, indent=1)`，写完重新加载自检：字段齐全、日期都在 {i0}~{i1}、URL 不重复）。
- 先用 ToolSearch 加载 `select:WebSearch,WebFetch`；也可用 Bash curl。预算约 80 次抓取/检索。arXiv 用网页（arxiv.org/abs、/html、/list），不要用 export.arxiv.org API（正在限流）。
- 完成后只回复简短总结：new_items 条数、最重要的 3 条（带关键数字）、section_md 字数、存疑点。

## 规范（摘自 docs/agent-guide/hardware-radar.md 第 2–4 节，全文）

{rules}
"""
    (pdir / fname.replace(".json", ".txt")).write_text(text, encoding="utf-8")
print(pdir)
