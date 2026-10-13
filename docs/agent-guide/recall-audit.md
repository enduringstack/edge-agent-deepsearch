# 漏检对账（每周）

> 采集层的 manifest 证明“查过哪些来源”，证明不了“这些来源漏了什么”。漏检对账是外部视角：由一个**不看本周报内容**的子 agent，从独立媒体、聚合站和社区热榜列出本周端侧 AI 的大事，再由主 agent 逐条和本周报对账。
> 产物：`data/recall_audit.json`，契约 `app/recall.py`，发布门 `gate_release.check_recall_audit`（缺文件、窗口不对、不足 10 条、“不收”没理由、声称已收录但页面里找不到——任一即 FAIL）。

## 1. 什么时候做

每周在正式 run、社区雷达、硬件雷达、本周判断都写完之后、build 之前。对账发现的漏项要回到对应采集层补收，再重新 build。

**运行当天的事件最容易漏**：各路子 agent 大多在运行日白天跑完，当天晚些时候的发布会和热帖（美国时间上午 = 北京时间晚上）进不来。2026-10-12 首次对账的 3 条补收里有 2 条发生在运行当天（AMD 新一代 Halo、Janas 登上 HN）。对账子 agent 应该在 build 前最后派出，并专门再扫一遍运行当天的发布与热榜。

## 2. 子 agent 任务（prompt 注入本节全文）

你只负责“列出本周大事”，**不要读本项目的周报、run 或任何 data 文件**——保持独立，才能发现漏项。

- 窗口：运行日向前含当日 7 个自然日。
- 范围：端侧 AI——手机/PC/汽车/机器人/IoT 上的模型、Agent、推理引擎、NPU 与 AI 芯片、端侧大模型发布与实测、端侧 AI 平台与安全、重要端侧论文与开源项目。云端大模型发布只有在对端侧有直接影响（如同时发布端侧版本）时才列。
- 至少查这些独立来源，并在 `method` 里写清实际查了哪些：
  - 中文：机器之心、量子位、36氪、IT之家、新智元
  - 英文：The Verge、9to5Google、9to5Mac、Android Authority、Tom's Hardware、Ars Technica、The Register、MarkTechPost
  - 社区热榜：Hacker News 首页（Algolia 按日期）、Reddit r/LocalLLaMA 周榜、GitHub Trending 周榜
  - 发布会/大会：窗口内召开的厂商发布会和技术大会
- 输出 15–25 条，按重要性排序；每条：`headline`（中文，一句话说清谁做了什么）、`url`（报道或原文直达）、`source`、`date`、`why`（中文，为什么算本周端侧大事）。只列真实打开过、日期在窗口内的事件。
- 写到 `research_runs/recall/events.json`。

## 3. 主 agent 对账

逐条判断并写入 `data/recall_audit.json`：

```json
{
  "window": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "method": "中文：子 agent 实际查了哪些独立来源",
  "items": [
    {"headline": "…", "url": "…", "source": "…", "date": "YYYY-MM-DD",
     "status": "已收录 | 补收 | 不收",
     "place": "正式周报 | 本周判断 | 社区雷达 | 硬件雷达",
     "match": "对应条目的 id 或 URL（status 为已收录/补收时必填）",
     "reason": "status 为不收时必填：中文理由"}
  ]
}
```

- **已收录**：本周报里已有，`match` 填该条目的 id（正式周报）或 URL（其他位置）。
- **补收**：漏了，回到对应层补上（正式条目必须找到官方/论文一手来源并走候选文件 → attest → 组装 → 校验；没有一手来源的放社区雷达或本周判断），补完再填 `match`。
- **不收**：确实不该收，写清理由（不是端侧、越窗、只有二手转述且无一手来源……）。
- 每一个“补收”都说明采集层有缺口：把根因写进 AGENTS.md 已知教训，能机械化的修进采集脚本或白名单。
