# 硬件雷达与硬件洞察（每周 + 每月）

> 本文件约束「硬件雷达」（每周首页板块，数据 `data/hardware_radar.json`）和「硬件洞察」（月报页 `hardware.html`，数据 `data/hardware-insights/`）的调研与发布。
> 派硬件调研子 agent 时，**prompt 必须注入本文件第 2–4 节全文**，不许主 agent 自写简化版。
> 契约代码：`app/hardware.py`；工具：`agent/hardware_week.py`；发布门：`app/gates/gate_release.py::check_hardware_radar`。

## 1. 节奏

| 产物 | 时间窗 | 何时做 | 门 |
|---|---|---|---|
| 硬件雷达（周） | 与周报相同：运行日向前含当日 7 个自然日 | 每次周调研，和社区雷达同一阶段 | `hardware_radar.json` 的窗口必须与本周 7 日窗口有交集，否则 gate FAIL |
| 硬件洞察（月） | 接上一期月报结束日的次日，到本月最后一个周报窗口结束 | 每月第一次周调研时，写上个月 | 最新一期月报结束日距今超过 38 天，gate FAIL |

硬件雷达是独立编辑层，和正式 run 分开：不走 candidate attestation，也不进 `__PAPERS__`；但每条仍要有可打开、日期可核验的来源和可读中文。

## 2. 调研方向（6 个子 agent 并行，一路一个）

| # | 方向 | 输出文件 | 必查 |
|---|---|---|---|
| 1 | 高通 | `deep_qualcomm.json` | 新 SoC（8/7/6/4 系、X 系列 PC、XR/可穿戴、Dragonwing、车载），Hexagon NPU 细节，AI Hub / GenieX / QAIRT 更新，OnQ 技术文章，高通 AI Research 论文，可信爆料 |
| 2 | Apple 与 Google | `deep_apple.json` | Apple 芯片与端侧模型（ML Research 博客、MLX、Core AI/Core ML、PCC），Google Tensor、Gemini Nano / Gemma 端侧数字、LiteRT、Android XR，可信爆料 |
| 3 | 其他 SoC、PC 与产业 | `deep_soc.json` | 联发科、三星 Exynos、华为麒麟、小米玄戒、紫光展锐、瑞芯微；NVIDIA/AMD/Intel/Arm 的 PC 与 IP；代工与内存产业（台积电、三星、TrendForce） |
| 4 | 低功耗、存内计算与内存 | `deep_lowpower.json` | MCU/常开 NPU、眼镜与可穿戴芯片、边缘加速器（Hailo、DeepX、Axelera…）、PIM/CIM 产品与国产存算（知存、苹芯、后摩、九天睿芯），LPDDR6 / UFS / HBF / CXL |
| 5 | 顶会论文 | `deep_papers_venues.json` | 窗口内召开的会议：ISSCC、ISCA、MICRO、HPCA、ASPLOS、DAC、VLSI、Hot Chips、MLSys、MobiSys、MobiCom 等，先核对会期再收 |
| 6 | arXiv | `deep_papers_arxiv.json` | v1 提交日在窗口内的端侧硬件/系统论文，优先真机实测（tok/s、J/token、模型规模） |

清单是起步集，不是穷举；本周有别家发布对题的端侧硬件，必须主动扩进来。

## 3. 子 agent 输出契约

每个子 agent 写一个 UTF-8 JSON：

```json
{
  "topic": "高通",
  "new_items": [ {条目}, ... ],
  "section_md": "（仅月报时需要）该方向的中文 markdown 小节，2500–5000 字，### 小标题，总-分-总，内联链接；不要以 ## 开头"
}
```

条目字段（`app/hardware.py` 校验）：

| 字段 | 要求 |
|---|---|
| `date` | 真实发布日（YYYY-MM-DD），必须在窗口内；更早的材料只能写进 `section_md` 当背景 |
| `vendor` / `title` / `url` | 原始名称、原标题、一手 URL；同一 URL 不能给两条，一页多条时加 `#短标识` 区分 |
| `category` | `移动SoC` / `PC芯片` / `NPU/AI加速器` / `低功耗/可穿戴/IoT` / `存内计算/PIM` / `存储与内存` / `车载/机器人` / `数据中心(对端侧有参考)` / `软件栈/工具链` / `产业动态` / `学术研究` |
| `source_type` | `官方` / `媒体` / `论文` |
| `title_zh` | ≤30 字中文名 |
| `summary_zh` | 2–4 句中文 |
| `whats_new_zh` | 带数字的新变化，逐条中文 |
| `key_specs` | 只允许 `process` `cpu` `gpu` `npu` `memory` `power` `other` |
| `model_capacity_zh` | 能跑多大的模型：参数量、精度、上下文、激活参数、tok/s，标明口径；不适用就省略 |
| `deep_dive_zh` | 3–6 个 `{heading（中文）, points[]}`，如 NPU 微架构、低功耗/常驻 AI、内存与带宽、能效与实测；每点都要具体 |
| `edge_ai_impact_zh` | 1–3 句：对端侧 AI / 智能体意味着什么 |
| `evidence_urls` | 其他佐证链接 |
| `confidence` | `high` / `medium` / `low` |
| `venue` `affiliation` `authors` | 论文必填 `venue`（如 `ISCA 2026` / `arXiv`），并写机构、前 3 位作者 |

## 4. 硬规则

1. **不编造。** 每个数字、URL、日期、模型规模、TOPS、跑分都必须来自实际打开过的页面或看到的检索摘要；厂商没公布就写「未披露」。
2. **标口径。** 正文里明确区分：官方口径 / 媒体实测 / 第三方实测 / 爆料 / 推算。爆料只能用 `confidence=low` 或 `medium`，标题或要点里写「爆料」。
3. **核对“能跑多大模型”。** 厂商说“可跑 120B”通常只说明内存装得下。用「带宽 ÷ 每 token 读取字节数」估 decode 上限，并标为推算；要看是否 MoE、激活多少参数、什么精度。
4. **日期按真实发布日。** arXiv 以 v1 提交日为准（编号月份可能晚于 v1）；会议论文以报告日或会议首日为准，并说明取法。
5. **不重复。** 已在往周收录的事件不再收；新增的是同一事件的后续（如“完成收购” vs “宣布收购”）可以收，但要写清增量。
6. **子 agent 只产 JSON**，不改代码、网页、服务器；用 Python `json.dump(ensure_ascii=False)` 写文件，并重新加载自检。

## 5. 主 agent：每周步骤

1. 在 `research_runs/hardware/` 下准备工作目录（不提交），按第 2 节派 6 个子 agent，prompt 注入本文件第 2–4 节全文和本周窗口。
2. 合并并去重（同批 URL/arXiv 变体自动合并，与所有往周归档自动去重，窗口外自动丢弃）：
   ```bash
   python agent/hardware_week.py merge research_runs/hardware/deep_*.json --dry-run
   ```
   看报告：同一新闻被不同 URL 收了两次的，写进 `dupes.json`（`{"重复条目 URL 前缀": "保留条目 URL 前缀"}`）后加 `--dupes dupes.json`；确认要丢的加 `--drop <URL 前缀>`。
3. **抽检**：子 agent 之间说法冲突的数字（如一个说“3B @ 45 tok/s”、另一个说找不到）由主 agent 亲自打开来源核实，再改条目。
4. 写本周总述 `research_runs/hardware/weekly_text.json`：`{"overview": "……", "takeaways": ["……"]}`。overview 是总（本周最重要的 3–6 件事，带关键数字），takeaways 是 2–4 条判断，不复述条目。
5. 写入并检查：
   ```bash
   python agent/hardware_week.py merge research_runs/hardware/deep_*.json --text research_runs/hardware/weekly_text.json [--dupes …]
   python agent/hardware_week.py check
   ```
6. 之后照常 build：`app/build.py` 会把 `data/hardware_radar.json` 归档进本周 `data/weeks/<label>.json` 并内联到首页；`gate_release` 校验契约、新鲜度和静态快照一致。

## 6. 主 agent：每月步骤（硬件洞察）

1. 时间窗：上一期 `data/hardware-insights/index.json` 最新条目结束日的次日 → 本月最后一个周报窗口的结束日。
2. 素材：窗口内各周 `data/weeks/<label>.json` 的 `hardware` 条目；不够深的方向，按第 2 节重新派子 agent 写 `section_md`（新条目可补进对应周）。
3. 结构（总-分-总）：
   - `head.md`：`# 硬件洞察：端侧 AI 芯片月报（起 ~ 止）`、一句话结论、阅读结构、`## 0. 总览`（3–5 个判断，每个配表格）、关键事件时间线。
   - 6 个分节：取各子 agent 的 `section_md`，由脚本加 `## N. 标题`。
   - `tail.md`：`## 7. 总结`（对端侧智能体的含义 + 下月观察清单）和口径说明（含哪些方向本月没有新品）。
4. 组装并更新索引：
   ```bash
   python agent/hardware_week.py month --month 2026-10 --title "2026-10-08 ~ 2026-11-04" \
     --head head.md --tail tail.md \
     --part "deep_qualcomm.json::高通：……" --part "deep_apple.json::Apple 与 Google：……" \
     --part "deep_soc.json::……" --part "deep_lowpower.json::……" \
     --part "deep_papers_venues.json::顶会论文：……" --part "deep_papers_arxiv.json::arXiv 精选"
   ```
5. `python agent/build_hardware.py` 生成 `site/hardware.html` 和 `site/hardware/`；页面右上角月份切换会自动多出这一期。

## 7. 已知教训

- [2026-10] 子 agent 给多篇论文共用一个会议目录页 URL，去重时被合并成一条 → 一页多条必须加 `#短标识`。
- [2026-10] 同一事件被两个子 agent 从不同媒体收录（如 AWE 上的 Reality Elite）→ merge 报告后用 `--dupes` 合并，不能靠肉眼漏过。
- [2026-10] 子 agent 之间对同一数字结论相反（一个写“3B @ 45 tok/s 官方口径”，另一个说来源里没有）→ 主 agent 亲自打开来源，查到 TechCrunch 转述高通原话后改为“官方口径（TechCrunch 转述）”。
- [2026-10] 往月已收的事件在新一月又被收（d-Matrix Raptor 8 月 Hot Chips 已收，6 月 ISCA 又收）→ `merge` 现在自动与所有往周归档去重。
- [2026-10] arXiv 编号是 2609.* 但 v1 是 7 月提交 → 以摘要页 v1 日期为准，不按编号月份。
