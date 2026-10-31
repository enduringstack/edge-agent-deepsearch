# AGENTS.md — edge_agent 项目工作指引

> 本文件是 agent 在此项目工作的目录表和免疫系统。
> 仓库是唯一记录系统：流程、契约、教训都写进 repo，不靠对话记忆。

## 必读项目 Skill

新的 codeagent 进入本仓库后，先读取项目内 skill：

```text
.agents/skills/edge-agent-research-pipeline/SKILL.md
```

这个 skill 是本项目的工作入口，说明项目目标、主 agent / 子 agent 边界、research run 契约、校验发布命令和不可违反规则。后续维护时，`AGENTS.md` 和该 skill 必须保持一致。

## 项目一句话

端侧 AI Agent 论文雷达：主 code agent 调度调研子 agent 搜索最近一周端侧 agent 相关论文，主 agent 校验后把结构化结果发布到服务器，网页从服务器刷新最新论文列表。

## 架构边界

项目按两大模块解耦 + 能力层：

- **Agent 调研模块**（`agent/`）：research_run 校验库、validate CLI、publish 脚本。主 agent 调度子 agent 搜索论文，产出 `research_runs/*.json`，校验后发布。
- **网页 App 模块**（`app/`）：server HTTP 路由、storage SQLite、page 展示页、build 静态 fallback、gates 内容校验。接收发布结果并展示。
- **能力层**（`.agents/skills/` + `AGENTS.md`）：给 codeagent 的工作指引和 skill，新 codeagent 强入口。
- 服务器不搜索论文，只接收校验过的 research run；搜索由 agent 工具完成。

## 目录地图

两大模块解耦 + 能力层：

| 路径 | 用途 |
|---|---|
| `.agents/skills/edge-agent-research-pipeline/SKILL.md` | 【能力层】项目工作 skill，新 codeagent 优先读取 |
| `AGENTS.md` | 【能力层】agent 总指引（本文件） |
| `agent/` | 【模块1·调研 pipeline】research_run/validate/publish |
| `agent/research_run.py` | research run 校验库 |
| `agent/validate_research_run.py` | 发布前校验 CLI |
| `agent/publish_results.py` | POST 到服务器 |
| `app/` | 【模块2·网页/server】server/storage/page + 静态 fallback |
| `app/server.py` | HTTP 路由和服务器入口 |
| `app/storage.py` | SQLite 存储和 paper upsert/query |
| `app/page.py` | 服务器展示页 HTML shell |
| `app/community.py` | 社区雷达 7 日窗口、来源覆盖和条目契约校验 |
| `app/build.py` | 静态 fallback build（生成 site/index.html） |
| `app/gates/` | content/papers frontmatter 校验 gate |
| `app/frontmatter.schema.json` | frontmatter 字段 schema |
| `tests/` | 跨模块测试（test_research_pipeline, test_build） |
| `research_runs/` | 子 agent 产出的 run JSON，默认不提交 |
| `content/papers/` | 兼容旧静态 build 的本地 Markdown |
| `site/` | 静态 fallback 产物，不提交 |
| `data/` | index.json / vendors.yaml 共享数据 |
| `data/community_radar.json` | X/Bluesky/Reddit/HN/Mastodon/GitHub Discussions/Hugging Face/视频/厂商论坛的独立社区线索与覆盖证据 |
| `data/hardware_radar.json` | 本周硬件雷达（移动 SoC / PC 芯片 / NPU / 低功耗 / PIM / 内存 / 论文），契约见 `app/hardware.py` |
| `data/hardware-insights/` | 月度硬件洞察 markdown + `index.json`（页面 `hardware.html` 的月份切换） |
| `agent/hardware_week.py` | 硬件雷达合并去重写入（merge）、本周覆盖检查（check）、月报组装（month） |
| `docs/agent-guide/hardware-radar.md` | 硬件雷达/硬件洞察的子 agent 调研规范、契约和每周/每月步骤 |
| `docs/agent-guide/recall-audit.md` | 漏检对账：独立列本周大事并逐条对账的规范 |
| `app/recall.py` / `data/recall_audit.json` | 漏检对账契约与本周对账结果 |
| `data/collection_history.json` | 每周各来源采集条数，覆盖异常门的比较基线 |
| `docs/` | 文档（agent-guide / site / design-docs / plans / references） |
| `README.md` | 人类入口和常用命令 |
| `ARCHITECTURE.md` | 顶层架构和数据流 |

## 主 Agent 工作流

> 总览见 `docs/harness.md` 第 3 节每周调研主循环。本节是主 agent 每周硬步骤，和 harness 保持一致，不许跳步。

1. 读 `.agents/skills/edge-agent-research-pipeline/SKILL.md`、`docs/agent-guide/main-agent-workflow.md`、`docs/agent-guide/research-prompt.md`、`output-contract.md`、`validation-rules.md`。强入口，不许跳过。
2. 检查 `data/.last_run`：读上次调研时间戳，距本次 ≥7 天才跑；<7 天提示"本周已调研"并停止。防重复跑、防拿旧 run 充本周。
3. 发起调研子 agent。**prompt 必须注入 `docs/agent-guide/research-prompt.md` 全文 + 硬约束**（广检索边界、官方域名白名单、动态 7 天窗口、多标签 tags、source_tier、不凑数）。**不许主 agent 自写简化版 prompt**。
4. 子 agent 用 arXiv MCP + HF Daily Papers MCP + GitHub MCP + websearch 广搜集最近 7 个自然日的端侧 agent、端侧技术栈和有直接迁移价值的相邻工作 + 24 个规范厂商/模型实验室官方来源 + 开源大项目 release。普通量化、剪枝、缓存、benchmark 或云端 serving 只要仍与 AI 推理/部署技术栈相关就保留并低分，不因“不够推荐”提前删除；完全无关才丢。子 agent 只输出结构化候选和覆盖证据，不改代码、网页、服务器。
5. 四类来源完成后必须生成 `research_runs/collection-manifest.json`：HF 逐日覆盖；GitHub trending 与大项目 release 分别记录；厂商逐家记录成功访问的官方来源；arXiv 完成大类扫描并自然翻页到窗口外。候选文件完成后运行 `python agent/attest_candidates.py`，把四个文件的路径、条数、文件 SHA-256、逐候选记录指纹和原始 title+URL+来源日期稳定身份写入 manifest；每条 run 内容必须保留唯一的 `candidate_source` + `candidate_ref`，不得复用候选，且原标题/原文 URL/日期必须匹配该候选身份。少一类、少一天、某厂全不可达、条数/哈希/血缘不一致都不能组装、validate 或 publish。
6. 主 agent 保存为 `research_runs/run-YYYYMMDD-HHMMSS.json`，亲自完成最终筛选、评分、标签、中文整理、affiliation 核实和逐条`edge_agent_scope`分类。自动汇集必须保持`edge_agent_scope=待核实`且不得自动加`方向:端侧agent`。真正端侧 Agent 的关键闭环至少部分实际运行在设备端，凡确认属于手机/PC/其他端侧都必须推荐；手机最优先、PC第二、其他端侧仍完整收录并推荐。
7. 运行 `python agent/validate_research_run.py research_runs/<run_id>.json`：先校验 collection manifest，再校验内容结构、动态 7 天窗口、评分、标签、链接、arXiv date 和跨 run 去重。旧论文若仅因本周修订进入窗口，主 agent 必须对比旧版并填写中文 `arxiv_revision_note`；排版、勘误或摘要无实质变化的一律不收。校验失败自动拦。
8. validate 失败：修正或丢弃不合格条目，**不许凑数**。找不到官方 URL 就丢，大厂不足就少收。
9. publish 前主 agent 抽检 `source_tier=官方动态` 和 `source_tier=开源大项目` 条目：fetch 每个 URL，对比页面内容 vs 标题摘要。URL 能开 ≠ 内容对题，对不上就丢。
10. **独立采集社区雷达**：以运行日为末日检索最近 7 个自然日的 X、Bluesky、Reddit、Hacker News、Mastodon、GitHub Discussions、Hugging Face（Discussions/Models/Spaces）、YouTube / Bilibili 和厂商论坛，写 `data/community_radar.json`。九类来源逐一写 `found/no_match/limited/unavailable` + 中文说明；X 只用无需登录即可打开并核验日期的公开原帖，受限就写 `limited`，不得拿转述冒充原帖。视频只收官方频道或可回链一手项目的演示。社区条目只进“社区雷达”，不得直接进入正式 run；必须回链一手材料并重新满足正式来源契约后才可晋升。
10.5 **独立采集硬件雷达**：按 `docs/agent-guide/hardware-radar.md` 派 6 个硬件子 agent（高通 / Apple 与 Google / 其他 SoC 与 PC / 低功耗·存内计算·内存 / 顶会 / arXiv），prompt 注入该文档第 2–4 节全文；主 agent 抽检冲突数字、写本周 overview + takeaways，用 `python agent/hardware_week.py merge … --text …` 写 `data/hardware_radar.json`（自动与往周去重），`python agent/hardware_week.py check` 确认覆盖本周。每月第一次周调研时，再按该文档第 6 节写上个月的硬件洞察（`hardware_week.py month`）。
10.6 **漏检对账**：按 `docs/agent-guide/recall-audit.md` 派一个不看本周报的子 agent，从独立媒体、聚合站和社区热榜列出本周端侧 AI 大事；主 agent 逐条对账写 `data/recall_audit.json`（已收录 / 补收 / 不收）。补收的回到对应采集层走完整流程，每个补收都要查根因写进教训。`gate_release` 拦缺失、理由缺失和“声称已收录但页面没有”。
11. 运行 `python agent/publish_results.py research_runs/<run_id>.json --server <SERVER_URL>`（缺少页面源文件的机器先设 `EDGE_AUTO_DEPLOY=0`）。发布后运行 `python agent/record_collection_history.py` 记录本周各来源条数，供覆盖异常门做比较。
12. 服务器 upsert，`GET /api/papers` 刷新最新 run；`GET /api/community` 读取独立社区雷达。
13. 详情页展示短摘要 + tags + 原文链接。publish 后列表页、社区雷达和详情页立即可见。
14. 更新 `data/.last_run` 时间戳为本次调研时间。
15. 本周错误沉淀进 AGENTS + validation-rules + research-prompt，不靠对话记忆。
16. 跑 `python tests/test_research_pipeline.py`、`python tests/test_build.py`、`python app/gates/gate_all.py` 确认 harness 健康。

## 调研策略（核心）

这是让调研子 agent 在搜索时必须注意的策略：

- **分层调研系统**：调研分 4 层（MCP大量搜集 → 主agent筛选 → 主agent评分 → 自动发布），详见 `docs/harness.md` 分层调研系统设计。三个 MCP 数据源：arXiv MCP（全量搜）/ HF Daily Papers MCP（社区精选）/ GitHub MCP（开源动态，端侧优先）。主 agent 亲自筛选+评分，不全交给子 agent。不设硬数量目标，有多少合格收多少。

- **优先级（高→低）**：
  1. 大厂官方动态（Apple/Google/Microsoft/OpenAI/Anthropic/Meta/NVIDIA/Samsung/Huawei/Qualcomm/MediaTek/小米/OPPO/vivo/荣耀/Alibaba-Qwen/Mistral/面壁，官方博客/产品发布，`source_tier=官方动态`，命中官方域名，排序最前）
  2. **公司项目**（快手/字节/腾讯/百度/美团/京东/拼多多/网易等公司独立或主导的研究，arXiv 或顶会，affiliation 命中公司）。优先级非常高，排序仅低于大厂官方。
  3. **公司+学校合作顶会项目**（公司联合高校发表顶会）
  4. **学校顶会项目**（高校独立发表顶会顶刊）
- **学校项目门槛**：`学校顶会` 必须发表在顶会顶刊（NeurIPS/ICML/ICLR/MobiSys/SenSys/ASPLOS/ACL/CVPR/ICCV/EMNLP/AAAI/IJCAI/TPAMI/TNNLS/ToN）+ 任何正规大学（不再卡中美名校）。任何大学的 arXiv 预印本（非顶会但强相关）收为 `学校预印本`。公司项目 arXiv 或顶会均可。
- **广收录、推荐聚焦**：普通量化/剪枝、缓存、benchmark、通用 serving 只要与 AI 推理/部署或资源受限场景有直接迁移价值就收录；常见方法给较低贡献分，通常不推荐。不得用“创新一般”充当检索删除条件；只有完全无关、来源不可信、越窗、重复或链接不匹配才删除。
- **真正端侧 Agent 是最高优先级**：必须同时具备 Agent 闭环（规划/记忆/工具/环境交互/行动之一）和设备端执行证据。`edge_agent_scope`只能是`待核实`/`手机`/`PC`/`其他端侧`/`非端侧Agent`；发布不得残留`待核实`。手机、PC、其他端侧必须有中文`edge_agent_evidence`、`方向:端侧agent`、`score_relevance>=8`且全部`推荐`，排序手机 > PC > 其他端侧 > 普通推荐。普通端侧模型/量化/缓存/检测、手机仅作云端入口、Orchard 一类云端 Agent 训练基础设施都不算真正端侧 Agent。
- **评分口径**（2 维，搜集阶段可给初值，最终由主 agent 阅读来源后确认）：
  - `score_relevance`（0-10）：明确端侧部署 8-10；端侧技术栈或直接可迁移工作 4-7；仅宽泛云端关联 1-3；完全无关排除
  - `score_contribution`（0-10）：创新度高 7-10；常见方法/工程整合 1-6。低贡献仍可完整收录，但不自动推荐
  - `score` = 2 维之和（0-20），排序靠 `source_tier` 优先级 + `score`
- **source_tier**（来源 facet，替代旧 source_type + is_major_vendor_official）：`官方动态`（24 个规范厂商/模型实验室官方来源，含 NVIDIA，命中官方域名，排序最前）/ `开源大项目`（白名单大项目 release，github.com URL）/ `公司项目`（affiliation 有一手证据，vendors 必填）/ `学校顶会`（任何大学顶会顶刊）/ `学校预印本`（任何大学 arXiv 预印本，排序最低）
- **open_source**：bool facet（有开源仓库/数据集/模型 true），不打分，同等条件开源优先
- **vendors 字段**：公司项目必填公司名和 `affiliation_evidence_url`。证据 URL 只能是 arXiv PDF、OpenReview/Scholar 或权威论文出版页，`score_reason` 必须解释它如何支持 vendors；GitHub 仓库/release 不是作者机构证据，统一归 `开源大项目`。没有一手证据一律先标 `学校预印本`。
- **官方域名硬约束**：非论文条目必须命中官方域名（见 `docs/references/vendor-whitelist.md`），非官方博客、新闻、GitHub release、社媒、二手解读一律排除。
- **多标签 tags**：每条 1-8 个标签，格式 `维度:值`（4 维：方向/应用/硬件/模型，如 `方向:端侧agent`/`硬件:NPU`/`模型:Llama`），取自 `data/tags.yaml` 词表（人读版 `docs/references/tag-taxonomy.md`），多标签，一个工作可挂多个（如「端侧 VLM 量化部署」挂 `方向:端侧agent`+`方向:多模态`+`方向:量化`+`方向:编译部署`）。页面按 4 维 faceted 筛选展示，不是非此即彼。方向/应用/硬件为受控词表，模型为半自由。词表外标签先加进 `data/tags.yaml` 再用。
- **首页字段人类可读**：`abstract`/`effects`/`mechanism` 用中文短句给人看（这是什么/有什么结果/怎么做到的），详细技术分解放 wiki，不塞首页。
- **推荐是主 agent 的编辑判断**：自动脚本和搜集子 agent 只做完整收录，一律 `title_zh=""`、`recommendation=纳入`、`edge_agent_scope=待核实`；不得因为标题命中关键词自动晋升。主 agent 逐条读来源后决定普通推荐；真正端侧 Agent 是例外中的硬规则——确认后必须推荐。推荐卡按设备范围徽标 → 中文项目名 → 中文 `abstract` 介绍 → tags 关键词 → 推荐理由 → 小号英文原标题展示。
- **keywords 已并入 tags**：原 keywords 字段取消，统一用 `tags`（受控词表）。
- **MCP 配置**：arXiv MCP / HuggingFace Daily Papers MCP / GitHub MCP 已沉淀为项目级 `.mcp.json`，配置和工具用法见 `docs/references/mcp-setup.md`。调研 agent 搜集优先用 MCP（arXiv 全量搜 / HF 社区精选 / GitHub 大项目 release），websearch 补充搜大厂官网。
- **开源大项目白名单**：GitHub MCP 只收 `docs/references/big-projects-whitelist.md` 内业界认可大项目（vLLM/SGLang/llama.cpp/ExecuTorch/ADK/TensorRT 等），非白名单小仓不收。
- **社区雷达独立层**：社媒/论坛能补充真实设备体验、项目苗头和用户争议，但可信度不同于正式周报。社区条目固定使用中文名称、中文总结、价值判断、设备范围和核验状态；手机优先、PC 第二、其他端侧与通用技术仍列出。搜索/筛选只作用于该层，不改写正式 papers。

## 不可违反

- 服务器不负责搜索论文；搜索由 agent 使用自己的搜索、浏览、阅读工具完成。
- 大厂官方技术博客 / 官方产品发布可收录且排序最前（`source_tier=官方动态`），但必须命中官方域名；开源大项目 release 用 `source_tier=开源大项目` + github.com URL + 白名单（`docs/references/big-projects-whitelist.md`）。非官方博客、新闻、GitHub release、社媒、二手解读一律排除。
- 社媒和论坛链接只允许出现在 `data/community_radar.json`，不得作为正式周报 `paper_url`。社区条目写“已进入正式周报”时，正式条目仍必须使用回链后的一手 URL，而不是讨论链接。
- 时间窗口是当前日期过去 7 天，不允许用旧 `.last_run` 放行过期样例。
- arXiv 更新稿不能只凭 `updated` 日期进入周报：必须由主 agent 对比旧版，确认实验、方法、数据、代码或结论有实质变化并填写 `arxiv_revision_note`；仅改排版、作者信息或无实质内容变化必须丢弃。
- `research_runs/collection-manifest.json` 是发布硬门：四类来源、精确 7 个自然日、arXiv 分页自然终止、HF 逐日、GitHub release/trending 分离、24 个厂商/模型实验室逐厂成功来源证据、候选文件路径/条数/文件 SHA-256/逐记录指纹、run 条目血缘缺一不可。组装会把 manifest 与候选血缘嵌入 run，发布客户端和服务器都会复验。所有写 API 还必须使用服务端配置的 `EDGE_PUBLISH_TOKEN`，匿名原始 POST 不能绕过。`--allow-incomplete-coverage` 只用于本地历史恢复，正常周报禁止使用。
- 没有本周合格论文时显示空状态，不拿旧数据撑数量。
- 凑数禁令：本周大厂官方不足就少收，不拿学术充大厂，不拿不确定链接凑数。
- `paper_url` 必须和论文标题、摘要匹配。
- `effects` 必须来自论文原文；没有报告写 `未报告`。
- 发布前必须跑 `validate_research_run.py`。
- **发布前必须跑 `python app/gates/gate_all.py`（含 `gate_release.py`）**。`gate_release` 是机械门，作用在构建产物 `site/` + `data/`，拦：__PAPERS__ 契约、推荐中文项目名/摘要/理由缺失或含内部占位词、项目名复用介绍、非空周报 0 推荐、内链 404、热点复读论文列表、0 官方动态静默、社区九来源覆盖缺失、静态社区快照不一致、社媒链接污染正式周报、硬件雷达不是本周或月度硬件洞察超过 38 天未更新、漏检对账缺失或不实。**它 FAIL 就不许部署**——比 assertIn 子串测试强，子串测试测不出的功能回归它都能拦。
- `data/weekly_summary.json` 是**独立编辑产物**，不是 run 的派生字段。`highlights` 必须是编辑性新闻（厂商博客/动态/行业事件，带**外部 URL**，≥5 条），不许用 run 的 paper_id 切 top N 填充——那会让热点复读下面的论文列表。流程顺序：先采厂商动态（`官方动态`）→ 再写 weekly_summary（从新闻 + 判断）→ run 论文列表是另一层。
- **0 官方动态是流程告警，不是可接受结果**。research-prompt 和 collection manifest 强制查 24 个规范厂商/模型实验室来源。run 里 `官方动态` count==0 时，必须要么去补采，要么在 `data/weeks/<label>-no-vendor.md` 写明逐厂证据，不许静默接受 0。
- 修改完成前至少跑 `python tests/test_research_pipeline.py`、`python tests/test_build.py`、`python app/gates/gate_all.py`。

## 已知教训

- [2026-06-25] 非官方博客/产品发布冒充论文会污染页面 → 只允许大厂官方技术博客/官方产品发布（`source_tier=官方动态` + 官方域名），其余非论文一律排除；普通论文用 `source_tier=学校顶会/公司项目` + 权威论文链接。
- [2026-06-25] 2025 年旧样例被展示成当前周报 → 时间窗口必须按当前日期过去 7 天硬校验，不能靠旧 `.last_run` 放行。
- [2026-06-25] GitHub 静态页不是最终形态 → 最终展示由服务器 `GET /api/papers` 刷新；GitHub Pages 只保留 fallback。
- [2026-06-25] 子 agent 和页面职责混淆 → 子 agent 只产出 research run JSON，主 agent 校验并发布，服务器只接收和展示。
- [2026-06-25] 新 codeagent 只读散落文档容易漏流程 → 项目内 `.agents/skills/edge-agent-research-pipeline/SKILL.md` 是强入口，AGENTS 必须指向它。
- [2026-06-26] 主 agent 绕过 research-prompt.md 自写简化 prompt → 子 agent 没守标准 → 编造 404 链接。修复：发起子 agent 时 prompt 必须注入 research-prompt.md 全文，不许自写简化版。
- [2026-06-26] 本周大厂官方内容稀疏时凑数，拿不确定链接充数。修复：找不到官方 URL 就丢弃，大厂不足就少收，不凑数。
- [2026-06-26] 整理 agent 产出的 detail 含英文双引号会破坏 JSON 编码（方案 B 已停用整理 agent，不再产 detail，此条归档）。
- [2026-07-09] 周切换器上线后在线站点论文列表 0 篇、切换器跳错、热点链接 404、热点复读论文列表——四个功能回归全因「只验数据形状（assertIn 子串/count/测试绿）不验产品体验（不打开页面点链接、不跟上周对比）」。修复：加 `app/gates/gate_release.py` 机械门（契约/内链/编辑层/官方动态），FAIL 不许部署；发布前用 chrome-devtools 实点每类链接。
- [2026-07-09] `weekly_summary` 被当 run 派生字段（切 top N 论文填热点）→ 热点复读论文列表、无厂商新闻。根因：编辑层和采集层没分离。修复：weekly_summary 标为独立编辑产物，先采厂商动态再写热点，highlights 须 ≥5 外部 URL。
- [2026-07-09] 子 agent 报「0 官方动态」主 agent 直接信 → 厂商博客层根本没采。修复：0 官方动态必须配 `data/weeks/<label>-no-vendor.md` 逐厂证据，gate_release 拦。
- [2026-06-26] 调研 agent 标注 vendors/affiliation 只凭作者名推测，没附证据来源 → 用户质疑。修复：vendors/affiliation 标注必须有证据来源（OpenReview profile / Google Scholar / 论文 PDF 作者机构页），score_reason 里写明 affiliation 依据（如「Zhixiang Chi OpenReview profile 显示 Huawei Technologies Ltd，huawei.com 邮箱确认」），不许只凭名字猜。
- [2026-06-26] 整理 agent 等全部整理完才统一推送 → 页面长时间停在「整理中」（方案 B 已停用整理 agent，详情页改短摘要+标签+链接，无「整理中」状态，此条归档）。
- [2026-06-27] 6 维评分表演性太强（relevance 没口径、vendor 按出身加权、维度重叠、跨 run date 漂移）→ 改方案 B：2 维（relevance+contribution，0-20）+ source_tier facet + open_source bool + 多标签 tags。取消 6 段 detail 整理 agent（`detail-prompt.md` 删除）。新增 arXiv date 核对 + 跨 run 去重，根治「旧论文改日期充本周」。
- [2026-06-27] 强入口文档过时（SKILL/output-contract 写 7天/5维，代码当时是 14天/6维）→ 新 agent 照强入口跑必和 validate 冲突。修复：强入口全量同步到代码实际口径。
- [2026-06-27] MCP 配置只在用户级 opencode.json，Claude Code runtime 接不上 → 沉淀为项目级 `.mcp.json` + `docs/references/mcp-setup.md`，任何 agent 进来都能配。Windows 上 `command:"uvx"` 不走 shell PATH，用 `cmd /c uvx` 包一层。
- [2026-06-27] 14 天窗口太宽混入旧内容 → 改 7 天（一周）。硬数量目标（400-500/30-50/10-20）不切实际且诱导凑数 → 改"有多少合格收多少，列表轻量罗列可以多收"。开源大项目白名单不分主次 → 标注端侧推理/端侧agent（ADK/nanoagent）优先，vLLM/TensorRT 次要。query 写死不灵活 → 加自适应（返回少就放宽换词）。
- [2026-07-03] 部署后只 curl 解析数量 + 跑 tests 就宣布"验证通过"，结果 weekly 是自动糊的噪声（商业/传闻/药物 + 通用 why）质量回归没发现，chrome-devtools 残留标签导致只显 75 篇也没发现——是用户逼着 chromedev 验收才查出。修复：**每次 publish/deploy 后必做渲染验证**（见 harness.md §5 渲染验证）——chrome-devtools 加载线上页 ignoreCache 硬刷新，查 DOM 渲染（row 数/折叠/标签栏）+ **读内容质量**（weekly topic/why、论文摘要真的看不是数条数；weekly 手挑手写不许自动构建）+ console error。curl 对 ≠ 渲染对，tests 过 ≠ 页面好。chrome-devtools profile 锁不是借口，`taskkill //F //IM chrome.exe` 杀掉重连。
- [2026-07-03] 教训/工作流硬规则放 ~/.claude 本地记忆（换机器没了、别人看不到、不进 git）违反"仓库是唯一记录系统"原则 → 改：项目硬规则一律写进 repo（AGENTS 教训段 / harness 校验段 / SKILL），本地记忆只留个人偏好。
- [2026-07-15] 阶跃星辰发布全球首个 AI 智能体手机 STEPX Neo+智能体 OS（本周最大端侧新闻）漏掉 → 根因：把 vendor-research-guide 的厂商清单当穷举，清单只列 DeepSeek/Moonshot/Zhipu/Minimax/百川「等」，没主动扩阶跃星辰。修复：阶跃星辰补进 vendor-whitelist（stepfun.com 官方域名）+ vendor-research-guide 模型厂表 + OFFICIAL_SOURCE_DOMAINS；release-check 加厂商覆盖自检（中国头部模型厂含阶跃星辰，漏的写逐厂证据，不许只写「0」断言）。**vendor 清单是起步集不是穷举，遇到「等」要主动扩，模型厂亲自下场造端侧硬件是最对题信号。**
- [2026-07-15] github trending 区显示 07-03 旧仓（搁 12 天） → 根因：把「GitHub」当一个桶（只做了白名单 release 扫描），忘了 trending 是独立产物（`data/github_trending_top20.json` + 自己脚本 `collect_github_trending.py` + 自己 API `/api/trending`）。修复：gate_release 加 `check_trending_freshness`（mtime ≤7 天，>7 天 FAIL）；release-check 体验项加「trending 第一仓是本周的吗」人工确认。
- [2026-07-15] SNN 标签把 Ising 神经形态信道解码错标 → 根因：`auto_tags` 的 SNN 规则用裸 `neuromorphic` 当触发词，neuromorphic 是超集（Ising 机/事件硬件/memristor 不全是 SNN），裸 `spike-based`/`spiking neuron` 还可能是生物学放电。修复：SNN 规则只留 `spiking neural network`/`\bsnn\b`/`spikformer`/`spiking transformer`/`spiking neuron model`；validation-rules 加规则 21（标签触发词精度，不许伞词当唯一触发）；release-check 加「按非默认 tag 筛 2-3 篇看是否对题」人工抽检。**重蹈了 research-prompt §2 已警告的「关键字过匹配」反模式——加新方向时也要想 tag 规则精度，不只让 query 能搜到。**
- [2026-07-15] **共同根因**：执行了流程的字面（arXiv/HF/github-release/vendor 清单）没执行精神（端侧 AI 全景覆盖 + 内容语义自检）。gate_release 是结构性门（契约/内链/编辑层/官方动态≥1），拦不住语义缺口（漏厂商/trending 过期/标签太松）。修复：release-check 加「用户视角浏览」段（按 tag 筛看对题、trending 第一仓时效、官方动态扫漏大厂、highlights 链接是真实新闻非首页壳）。三次都是同一个病没真正吸收——跟 07-09「热点 404 测试不全面」同一教训：验证停在「数据形状对 + gate 绿 + 渲染 N 篇」，没像用户一样浏览内容语义。
- [2026-07-30] 论文/开源项目/公司项目 abstract 全英文——`output-contract.md` 明确要「大白话中文整理版，不搬原文」，但 `build_run_week.py` auto-convert 用 `first_sentence(summary)` 截 arxiv/HF **英文原文**首句，违反 spec（score_reason 自己写了「精修大白话待补」一直没补）。根因：auto-convert 是脚本不能翻译，LLM 翻译步骤缺失。修复：build_run_week 出 run JSON 后派 subagent 把英文 abstract 翻成中文大白话（1-2 句"这是什么"风格）写回 run JSON，再 validate/publish。**spec 要中文的，脚本做不到的，必须有 LLM 步骤兜底，不能留 TODO 不补。**
- [2026-07-30] github trending 每次要手动跑——gate_release `check_trending_freshness` 只拦过期不自动刷，`collect_github_trending.py` 靠主 agent 手动跑（gate FAIL 才补）。根因：trending 刷新不在刷新流程里。修复：`agent/refresh_trending.py`（collect + 转 top20 一步）作为**主 agent 每次周刷新的固定步骤**（build_run_week 后、翻译 subagent 前），`refresh_trending` 拿英文 desc → 翻译 subagent 把 trending desc + run abstract 翻中文。**不进 auto-deploy**（auto-deploy 的 refresh 会覆盖翻译 subagent 的中文 desc——refresh 拿英文 GitHub 描述，翻译要 LLM 在 refresh 之后）。gate 兜底（mtime>7d FAIL 提醒主 agent 补刷）。
- [2026-08-04] 推荐区把英文原标题当主信息，还把 `score_reason` 的 `auto-converted`/`votes=`/`待核实` 等流水线文字直接展示；同时 `build_run_week.py` 仅凭标题关键词自动推荐，导致弱相关内容挤进首屏。根因：完整收录和编辑推荐共用字段、页面层级反了、中文要求只有文档没有机械门。修复：推荐卡改为中文 `abstract` 主信息 + 中文 `recommendation_reason` + 小号原标题；自动汇集一律 `纳入`，只允许主 agent 阅读来源后晋升；validate 与 gate_release 双层拦英文摘要、缺失理由和内部占位词。**今后凡读者可见的内容契约，都必须同时落到 prompt、schema/存储、测试和真实构建 gate，不能只修页面或只写文档。**
- [2026-08-04] 中文摘要虽然解决了英文难读，但把“项目介绍”直接放到卡片第一视觉层，读者仍要读完一句话才知道条目叫什么。根因：数据里没有独立的中文项目名，页面只能拿 abstract 冒充标题。修复：新增 `title_zh` 全链路字段；推荐时由主 agent 编写简短中文名称，卡片固定按名称→介绍→关键词→理由→原标题展示；validate 与 gate_release 拦缺失、过长和直接复制 abstract。**名称和介绍是两个不同的内容契约，不能靠前端截句或同一字段兼任。**
- [2026-08-05] 广搜初筛把裸 `edge/embedded/deployed/energy/pruning/加速` 当端侧证据，既收进图结构、社会语境、音乐和云端 Mobile 用户等噪声，也因 AI 词表只认单数 LLM/agent 而漏掉 TinyML、ExecuTorch、端侧视觉/语音任务。修复：相关性改为“明确设备语境 + AI 模型/任务”或“明确推理优化技术栈”的组合证据；补复数、视觉、目标检测、语音识别、关键词唤醒等高频端侧词；每次改触发规则必须在 `tests/test_research_collection.py` 同时加正例和碰撞负例。**广搜追求召回，入库仍要语义证据；单个词既不能自动收录，也不能自动推荐。**
- [2026-08-05] 检索数量多但无法证明覆盖完整：arXiv 只取每个 query 前 100 条、多个采集脚本写死日期、厂商/HF/GitHub 候选靠临时执行，且“常见方法直接删”与“完整收录”冲突。修复：统一 `research_collection.py` 动态 7 日窗口和 `collection-manifest.json` 四来源覆盖门；arXiv 翻页；普通但相关内容低分保留；主 agent 只通过推荐层决定用户优先看什么；公司归属只认明确 affiliation 证据。**检索层追求覆盖，推荐层负责注意力，不能用提前删内容代替策展。**
- [2026-08-05] 覆盖清单若只写 `status=complete` 仍可能把抓取失败、分页截断或被清空的候选文件伪装成完整；只在发布 CLI 检查还可被直接 API 绕过。修复：arXiv 命中页数上限即失败；厂商逐家记录 `found/no_match/unreachable` 和成功官方来源；四候选文件必须做路径/条数/文件 SHA-256/逐记录指纹/稳定 title+URL+来源日期身份证明；每条 run 内容必须唯一命中候选且不能复用；manifest 与血缘嵌入 run 并由客户端、服务器复验；写 API 强制 `EDGE_PUBLISH_TOKEN`。公司项目另强制权威 `affiliation_evidence_url`，GitHub URL 不算机构证据，多 vendors（包括 `JD` 这类短名称）必须逐家解释，空分隔符不能算厂商；`candidate_source=github` 强制映射为 `开源大项目` 且 URL 命中大项目白名单，未知小仓不能伪装成学校/公司项目。**覆盖证据必须和实际候选、最终条目、受信发布者同时绑定，不能只相信采集器自报。**
- [2026-08-05] 为补漏加入 arXiv `lastUpdatedDate` 扫描后，旧论文仅改排版也会伪装成本周动态；Jetson-PI v1/v4 摘要和文件大小几乎不变，不能因 8 月 3 日更新时间重发。修复：`arxiv_date_basis=updated` 必须填写主 agent 比对旧版后的中文 `arxiv_revision_note`，说明实验、方法、数据、代码或结论的实质变化；缺失即 validate 拦截。**更新时间只负责召回，实质修订证据才允许进入本周。**
- [2026-08-05] 中文摘要已修好但详情页仍显示“自动初评/主 Agent 复核”，且 25 条摘要以省略号截断。根因：只把摘要当读者字段，遗漏了同样直接展示的 `score_reason`；翻译检查只数中文字符，没有检查句子完整性。修复：摘要翻译后必须拦截省略号结尾并回到原始摘要重写；`build_run_week.py` 生成读者可读评分依据，validate 与 `gate_release` 对所有条目的 `score_reason` 拦内部流程词，并配回归测试。**所有会在页面出现的字段都属于内容契约，不能只检查推荐卡主字段。**
- [2026-08-05] `方向:端侧agent`曾由`edge/mobile/agent`宽泛关键词自动生成，49 个标签条目里混入普通推理、检测、量化和云边系统，无法据此强制推荐。修复：新增经原文核实的`edge_agent_scope`+`edge_agent_evidence`；自动搜集只写`待核实`且不自动加端侧 Agent 标签，validate 和 gate 双层拦待核实、标签错配、漏推荐和低相关分。**真正端侧 Agent 必须有关键 Agent 闭环实际在设备端运行；手机优先、PC次之、其他设备仍全部推荐。**
- [2026-08-12] 厂商 sitemap 把旧产品页的 `lastmod` 和地区镜像伪装成本周新动态，自动采集一度产生 229 条噪声。修复：sitemap/搜索抓取时间只负责发现，正式候选日期必须回到具体官方直达页正文核验；旧页面模板更新、地区/语言重复页全部剔除。**官方域名正确不等于发布日期正确，URL、主题和正文日期三者都要对上。**
- [2026-08-12] 裸 `multi-agent system` 和摘要深处偶然出现的蒸馏/serving 再次把医疗表型、低功耗网络等无关工作带进入库。修复：相邻技术证据必须是标题或核心贡献；真正端侧 Agent 必须同时有设备语境与规划/记忆/工具/行动闭环，新增 ESP32/STM32/Linux SBC 正例和关键词碰撞负例。**广搜保召回，但正式入库仍看语义中心。**
- [2026-08-12] GitHub Trending 发现 Limioryn 等端侧 Agent 新仓，静态白名单会漏新方向，但直接接纳所有新仓又会把 0-star 个人演示当大项目。修复：未知新仓先留线索；主 agent 核对本周事件、影响力、代码和真实设备 ACK/对账/恢复闭环后，仅将通过审计的项目加入白名单并补测试。**白名单可演进，但每次晋升都必须有人工证据和机械回归。**
- [2026-08-13] 页面新增 HTTP 状态检查后，`build.py` 依赖两行精确代码形状的正则没有命中，GitHub Pages 仍请求不存在的 `/api/papers`，本地动态服务正常却导致线上“读取失败”。修复：页面运行时固定先读内联 `window.__PAPERS__`，不存在时才请求 API；静态构建不再重写 fetch 代码；页面测试、真实构建测试和 `gate_release` 同时检查这一契约。**静态/动态双运行模式必须由稳定的数据优先级契约保证，不能靠匹配实现细节的源码正则。**
- [2026-08-13] 正式来源扩展后仍看不到 X/论坛动态，是因为“可信正式收录”和“高召回社区发现”被塞进同一个来源门：放宽会污染周报，不放宽就永远缺社区声音。修复：新增独立 `data/community_radar.json` + `/api/community` + 页面“社区雷达”；九类来源逐项留下覆盖状态，X 公开索引受限时明确展示，不编造完整性；社区讨论回链一手材料前不得进入正式周报。`gate_release` 同时校验数据、静态快照、页面顺序和层间隔离。**来源可信度不同就拆层展示，不能靠降低正式周报标准换取消息量。**
- [2026-08-17] HF 日榜只识别 `arxiv.org/abs/` 链接，漏掉 `huggingface.co/papers/<id>` 形式的 SPIEval 手机助理评测、AutoPrune 视觉令牌剪枝和 Maglev 固定大小记忆。修复：两种链接统一提取规范 arXiv ID并跨源去重；手机助理、精确视觉令牌剪枝和循环记忆加入应收正例，同时保留碰撞负例。**跨源去重必须按稳定内容身份，不得把某个网站 URL 形状当唯一身份。**
- [2026-08-17] 内部流程词正则 `主\s*Agent` 把正常读者文案“自主Agent闭环”也拦掉。修复：validate 与 `gate_release` 同步改成排除“自主Agent”的语义边界，并各自增加“流程话术应拦 / 正常文案应放”回归测试。**内容门禁不能只测拒绝路径；任何新禁词都要有合法文本反例，避免越修越窄。**
- [2026-09-22] 回填 08-19~09-22 五周时，`recent-updates`（9 大类按 `lastUpdatedDate` 倒序扫描）在每个历史窗口都失败：arXiv legacy API 在 `start=10000` 直接返回 HTTP 500，9 类合起来的更新量早就超过一万行，加 `--max-pages` 不可能翻回一个月前的窗口。试图用 `lastUpdatedDate:[窗口]` 过滤同样无效——实测 arXiv **不认**这个字段的范围过滤，同样边界下它返回的结果集与 `submittedDate` 完全一致（totalResults 都是 1181，命中的是提交日在窗口内的论文）。修复：`recent-updates` 拆成 9 个单大类 sweep 分别翻页（单大类翻到 5 周前约 9000 行，在墙以内），`submitted` 类 sweep 改用 `submittedDate:[窗口]` 过滤直接框住范围不再深翻；新增 `--labels` 定向重试参数，让失败的 query 可以单独补跑并合并进已有候选集，不必丢掉整窗口重来；`curl_url` 重试 4→8 次、429 退避上限 300 秒，`queries_failed` 写入前去重。**API 的分页深度是硬上限，覆盖要靠把查询切小，不能靠翻得更深；而且"能用的过滤字段"必须实测，不能按文档想当然。**
- [2026-09-22] 同一批回填里，多窗口并行打 arXiv 直接触发持续 429，连 `start=0` 都被拒，浪费了两轮重试。修复：采集脚本按窗口串行跑，页大小从 1000 降到 500/200，失败后先冷却再重试。**并行采集提速的前提是对方扛得住；外部 API 是共享资源，串行 + 退避比并行 + 重试更快到终点。**
- [2026-09-22] Qualcomm OnQ/developer blog 模板关掉了日期显示（`showDate: ""`），正文里没有任何发布日，一度要在"丢弃真动态"和"拿 sitemap lastmod 凑数"之间二选一。修复：允许取该文章 URL 自己返回的 CMS 正文载荷（`<article-url>.model.json` 的 `pagePublishDate`，epoch 毫秒）并与 URL 路径 `/YYYY/MM/` 交叉印证，写进 `validation-rules.md` 第 26 条和 `vendor-research-guide.md`；整站 JS 壳、只拿得到标题、或 canonical 指向另一篇的仍然一律丢弃。**"正文日期"要防的是发现层时间戳，不是一手结构化数据；规则的意图比字面重要，但放宽必须写进 repo 而不是个案决定。**
- [2026-09-28] 厂商核验 agent 查到 vLLM v0.30.0、TensorRT v11.3、ollama v0.34.4 都在窗口内有正式 release，差点当成漏采补进白名单——根因是 `output-contract.md` 和 `research-prompt.md` 举例时写了「如 vLLM/SGLang/llama.cpp/ExecuTorch/ADK/TensorRT 等」，而 `big-projects-whitelist.md` 的实际清单刻意只有端侧/边缘推理引擎 + Agent 应用，从来没有这几个服务端 serving 栈。修复：两处举例改成与白名单一致，并明写「服务端 serving 栈不在边界内」。**文档举例和机器清单不一致时，agent 会信举例；举例必须从清单里取，不能随手写。**
- [2026-09-28] 社区雷达九类来源第一次全部 `found`。此前 X 长期只能记 `limited`（未登录拿不到原帖发布时间，又不许拿转述冒充），本周验证出可行办法：x.com 状态页未登录即可取到 `og:description` 正文和 `<meta property="article:published_time">` 精确 ISO 发布时间，足以满足「公开可打开 + 日期可核验」。同批还验证：Bluesky 用 `api.bsky.app`（不是 403 的 `public.api.bsky.app`）的 `searchPosts` 带 since/until；Reddit 用浏览器 UA 打 `/r/<sub>/top/.rss?t=week`（`.json` 与 old.reddit 仍 403，429 需退避重试）。**「检索受限」要区分是真受限还是没找对入口；记 `limited` 之前先把一手接口试完。**
- [2026-10-09] 硬件雷达/硬件洞察（2026-05~09 回填）一直靠一次性脚本手工补，周调研流程里没有这一步，下周起就会断更。修复：新增 `docs/agent-guide/hardware-radar.md`（6 路子 agent 规范 + 契约 + 每周/每月步骤）和 `agent/hardware_week.py`（merge 自动与往周归档去重、窗口外自动丢、check、month 组装）；`run_weekly.sh` 在 build 前强制 `hardware_week.py check`；`gate_release` 新增硬件雷达新鲜度和月报 38 天上限。回填中暴露的问题（多篇论文共用一个目录页 URL 被合并、同一新闻多源重复、子 agent 对同一数字结论相反、跨月重复收录）都写进该文档的已知教训。**新增编辑层时，产物、流程脚本、发布门三件事要一起落地，否则只是一次性的数据。**
- [2026-10-12] 本周 10-06~10-12 周报一次暴露四个“采集自报完整、实际漏或混”的问题。(1) arXiv 的 Systems and Control 论文现在挂在 `eess.SY`，`cat:cs.SY` 返回 0 行，`cs.SY-broad` 却照样记为 complete（同窗口 eess.SY 有 136 篇）。修复：`arxiv_curl_sweep.cat_query` 对 cs.SY 一律查 `(cat:cs.SY OR cat:eess.SY)`，含 recent-updates 与可达性探测，并加回归测试。**某个大类突然 0 条不是“本周没有”，先直接查 API 的 totalResults 确认分类没改名。** (2) GitHub Trending 解析器的 `<p[^>]*>` 会匹配到星标按钮里的 SVG `<path>`，描述被吞成 “Star owner / repo”，而且从不解析星数，真正上榜的端侧仓（BitNet、uzu、Llama-macOS、atomic-agent）全部排到末尾、Top20 只剩 1–5 星新仓。修复：解析总星数和本周新增星，Trending 页仓库须同时命中端侧推理栈词和 AI 词（`is_edge_trending`，带“web and mobile apps”“tinyhumansai”等碰撞负例），按本周新增星排序。(3) llama.cpp 每合一个 PR 就打一个 `bNNNNN` CI 构建 tag，本周 110 个全部被组装成“开源大项目”；白名单早写了“每日 CI build 不算”，但只存在于文档。修复：`build_run_week.is_daily_build` 机械过滤。(4) HF 日榜会把上周已发布的论文再推一遍（本周 3 条，其中 2 条差点作为推荐重发）；validate 只对“上一期”给 warning。修复：组装器按 arXiv/HF 统一身份与全部 `data/weeks/*.json` 去重。**文档里写了的规则，只要还能被脚本绕过，就等于没写。**
- [2026-10-12] 本地 `app/server.py` 收到 publish 后 10 秒会自动 build 并把 `site/` **整体替换**推到 gh-pages；本机没有调研笔记源文件时，这会把线上笔记页一起抹掉（本次因 origin 不带凭证才没推出去）。修复：新增 `EDGE_AUTO_DEPLOY=0` 开关；缺少任何页面源文件的机器发布时必须关掉自动部署，改为只把本次重建的页面（index、week/*、paper/*、hardware*）覆盖到 gh-pages。
- [2026-10-12] 微软 10-07 Windows 发布会的官方稿（MXC 执行容器正式版、Building Windows for hybrid intelligence）发在 `blogs.windows.com`，不在官方域名白名单，厂商子 agent 按规则只能漏掉本周 PC 端 Agent 最重要的一手来源。核实为微软官方 Windows 博客、`/feed/` 带 pubDate 后加入白名单（`vendor-whitelist.md` + `OFFICIAL_SOURCE_DOMAINS` + 采集入口 + 回归测试）。**子 agent 报告“官方稿在白名单外”时，主 agent 要当场核实并决定是否扩白名单，而不是默认放弃。**
- [2026-10-12] 追问“怎么保证不遗漏”时按日期盘点历史周，发现最大的漏洞不在任何单一来源：arXiv 周一晚上才公开周四下午到周日的投稿，而周报周一跑、下周窗口又已越过，**这几天的论文从上线起就永远进不了任何一周**（07-02、07-25、08-12、09-22、09-29、10-06 等周的窗口末尾都是 0 篇；仅 cs.LG 一个类 10-03~10-05 就有 647 篇投稿，最终只收了 1 条）。修复：(1) arXiv 按提交日收录允许回看窗口前 5 天（`ARXIV_CATCHUP_DAYS`），与所有往期去重，validate 同步放行并拦重复；(2) 覆盖异常门：大类 0 条、已公开工作日 0 篇、来源条数崩到中位数 30% 以下都拦组装；(3) 每周漏检对账：独立子 agent 列本周大事，主 agent 逐条对账，gate 拦。历史缺口用 `arxiv_curl_sweep.py --since/--until/--out` 补采后并入原周存档。**“每个来源都查过”不等于“没有漏”：要按输出的日期、类别分布反查覆盖，再用外部视角对账。**
- [2026-10-12] 第一次漏检对账（15 条独立来源列出的本周大事）：10 条已收录、3 条补收、2 条有理由不收。补收的根因：(1) AMD 新一代锐龙 AI Halo（10-12 美国时间发布）和 Janas 登上 HN（10-12 22:05 UTC）都发生在运行当天、晚于各路子 agent 的采集时间；(2) Perplexity 开源的端侧检索模型来自 24 家规范厂商之外，官方采集层天然覆盖不到，只能靠社区与对账发现。修复：对账子 agent 放在 build 前最后一步派出，并专门补扫运行当天；名单外公司的端侧发布以社区雷达承接（回链官方原文）。**名单是起步集，对账才是检验名单够不够的手段。**
- [2026-10-12] 这一周的整理跨过午夜，10-13 才发布。服务器端早有 `EDGE_TODAY` 覆盖“今天”，但社区雷达、漏检对账、`gate_release`、`gate_window`、validate 默认值和 `hardware_week.py` 都直接用 `date.today()`，晚一天发布会被判过期，build 还会把社区雷达写成空。修复：统一走 `app/clock.report_today()`（读 `EDGE_TODAY`），发布门加“隔天发布”回归测试。**同一个“今天”在一条流水线里必须只有一个来源。**

- [2026-10-20] 10-13~10-19 周报（10-20 发布）的四条新教训。(1) 漏检对账发现 Apple ML Research 10-15 的 MLX 多机分布式推理实测没进正式周报：厂商子 agent 读了 `machinelearning.apple.com/research` 第 1 页内嵌数据，却漏了这篇（硬件子 agent 收到了）。补收后加入候选 → attest → 重新组装。**同一官方源被两路子 agent 读到不同结果时，以并集为准，主 agent 组装前要拿硬件雷达里的官方 URL 反查正式 run。** (2) 阶跃终端 STEPX Neo 先行版（10-13 发布、10-16 首销）的官网 `stepx.com` 是无日期的 JS 产品页，满足不了正式来源的“正文日期”要求，只能进本周判断；`stepfun.com` 新闻列表窗口内也没有对应稿。**模型厂的终端子品牌另起域名时，要在 vendor-research-guide 记下它的发布入口，没有带日期的一手稿就明确放本周判断，不能静默漏掉。** (3) arXiv 周日提交的修订稿，abs 页显示“last revised 19 Oct”，接口 `updated` 却是 10-20，validate 以接口为准判越窗；本周因此逐条剔除 4 篇（AutoTailor、LeanTTA 等），留待下周按修订稿判断。**修订稿的日期以 arXiv 接口为准，整理时不要按 abs 页日期判断窗口。** (4) 一次部署命令在 `gate_all` FAIL 后仍继续推送（失败项是热门仓库 7 天新鲜度，内容没有回归）。**部署脚本必须 `set -e` 或用 `&&` 串起来，gate 失败立即停止，不能靠事后发现。**
- [2026-10-21] 1–5 月按月做漏检对账（每月一个不看周报的子 agent 列 34–37 件大事，再由对账 agent 逐条比对各周 papers/硬件/社区/周报摘要）：共 179 件，正式补收 16 条（用 `research_runs/backfill/add_items.py` 按发布时的内容规则校验后写回原周），另有 52 件只有媒体报道、没有合规一手来源，统一写进对应周周报摘要末尾的“另据媒体报道”段。漏收根因有四类：(1) 组装阶段的相关性预筛把大厂通用模型技术报告（阶跃 STEP3-VL、DeepSeek-OCR 2、腾讯 AngelSlim）提前滤掉了，这类报告对端侧多有直接价值，预筛需要对“公司 + 小模型/压缩/端侧部署”放宽；(2) Apple 的研讨会回顾发在 `machinelearning.apple.com/updates/`，厂商子 agent 只扫 `/research`，模板已补入口；(3) 面壁官网只链微信，端侧模型只发 GitHub/HF，已把 OpenBMB 的 MiniCPM / MiniCPM-V / VoxCPM 加入大项目白名单（AgentCPM 星数不够未加）；(4) 2026 年 3–4 月的“Claw”类手机/PC 系统级智能体（小米 miclaw、华为小艺 Claw、荣耀 YOYO Claw、OPPO 小布 Claw）几乎都没有官方域名上带日期的发布稿，只能进周报摘要。**手机厂商的系统级智能体是本项目最对题的内容，却恰好最难满足正式来源规则；遇到这类事件要主动找官方新闻中心或开发者文档的带日期页面，找不到就明确写进周报摘要，不能静默漏掉。** 另：`qwen.ai`（Qwen 官网）不在官方域名白名单，Qwen3.5 小模型因此只进了社区雷达，待核实其带日期页面后再决定是否加入（2026-10-24 已加入，同时加入 `amd.com`、`liquid.ai` 和大项目 `google-ai-edge/LiteRT-LM`）。
- [2026-10-22] 6 月底到 9 月中的旧周是按“发布日”而不是按连续 7 日窗口建档的，07-31/08-01/08-05 三周互相重叠，08-12 与 08-07 重叠，09-16 跨进 09-22，导致同一内容在多周重复、周页时间轴错乱。已用 `research_runs/backfill/restructure_weeks.py` 把 06-26~09-21 重排为首尾相接的周（08-14 为 5 天、09-16 为 6 天过渡周），papers/硬件/社区按日期重新分桶，受影响周的摘要全部重写，退役标签 07-02/07-25/08-01/08-05/08-12 在 gh-pages 上留跳转页。**新建周档案前先确认它的开始日正好是上一周结束日的次日；窗口一旦重叠，去重和周报摘要都会跟着出错。**
- [2026-10-23] 6 月（05-15~06-25）漏检对账：49 件，已收 28、补收 5、不收 16。补收的根因：(1) OpenBMB 仓库 10-21 才进大项目白名单，MiniCPM 5.0 release 当时只进了社区雷达；(2) 厂商采集没覆盖 `blogs.windows.com/windowsdeveloper`（Build 上的 Aion 1.0 端侧规划模型、MXC 智能体沙箱）和荣耀中文新闻中心 `honor.com/cn/news`（Agentic OS），两处应加进厂商入口；(3) 地平线 HoloMotion-1 的 arXiv 提交日在周末最后一天，被相邻周漏掉。只有媒体来源的 14 件（联想天禧 Claw、小艺 Claw 全量开放、荣耀 YOYO×微信 A2A、理想 M100 等）写入各周周报摘要。
- [2026-10-24] 7 月（06-26~07-30）漏检对账：50 件，已收 22、补收 4、不收 24。根因：(1) 三篇补收的 arXiv 都是公司技术报告（灵波 LingBot-VLA 2.0、腾讯 Hy-Embodied-VLM、阿里 OvisOCR2），标题不含端侧关键词，被组装预筛滤掉——与 1–5 月的“公司技术报告预筛过严”是同一问题；(2) 荣耀 07-18 WAIC 官网稿标题写的是 Robot Phone 预约，按关键词抓厂商新闻会漏；(3) 白名单缺口：`google-ai-edge/LiteRT-LM` 不在大项目白名单（只有 litert），`amd.com` 不在厂商白名单（AMD Advancing AI 硬件雷达也漏了），待用户决定是否加入；(4) 手机系统级智能体的生态动作（微信/支付宝 A2A、OPPO 小布 Next、小艺任务、努比亚 NaviX）仍只有媒体来源，已写入周报摘要。
- [2026-10-24] 8、9 月漏检对账（97 件，补收 11）与 1–5 月、零散周“未报告”补数字收尾。新根因：(1) 中国手机厂商的系统发布（荣耀 MagicOS 11 / Magic9、vivo OriginOS 7）都在白名单域名 honor.com / vivo.com.cn 的中文新闻页，厂商子 agent 没扫到——厂商入口要补中文新闻中心；oppo.com、华为官网的发布页常常没有日期，永远进不了正式周报；(2) 高通 OnQ 博客和新闻稿正文靠 JS 渲染，只读 HTML 会拿到空页，要读文章的 `.model.json`；(3) developer.meta.com、NVIDIA 开发者博客与 RTX AI Garage 系列、alibabacloud.com 博客（Qwen 发布）不在常规入口；(4) 白名单缺口：Liquid AI、AMD、IBM、科大讯飞、PrismML、LiteRT-LM、Ollama，8、9 月合计约 10 件有一手页面却因白名单不收。补数字方面：重新核对原文后约四成能补出具体数字，剩下的多是没有效果数据的厂商新闻稿；子 agent 容易把小型初创公司填成公司归属、把默认云端模型的 nanobot 判为端侧，合并前要统一纠正。
- [2026-10-24] **部分周的做法**（10-20~10-26 周在 10-24 周六先发布）：采集、社区雷达、硬件雷达、漏检对账仍按“今天往前 7 个自然日”（10-18~10-24）跑，因为校验器和门禁都要求窗口截至 today；内容上只收 10-20 起的条目（arXiv 回看补采例外），各 JSON 的 window 字段写 10-18~10-24、说明里注明“部分周”。周档案的标签和范围由周报摘要文字解析，所以 overview 要写“（10-20~10-26，部分周，数据截至 10-24）”，档案就会落在 10-20 周、range 10-20~10-26。**追加**：10-26 之后以 `--today 2026-10-26`（`EDGE_TODAY=2026-10-26`）重跑 `collect_live.sh 2026-10-20 2026-10-26`，窗口正好是 10-20~10-26；已发布的 10-20 周条目由组装器按已发布身份去重（当前周本身不排除时需先确认 `published_identities` 的处理），新增条目精选后与本次 `research_runs/backfill/2026-10-20/batches/out_*.json` 合并重新发布；arXiv 10-23、10-24 的投稿以及本次因当天又出新修订而暂缓的 2609.22818、2511.14102 要在追加时补判。另：同一天连续跑多步时，`pytest` 会清空 `site/`，门禁必须在 build 之后跑；命令链里不要用 `| tail` 吞掉门禁的退出码（要么 `set -o pipefail`，要么不接管道）。
- [2026-10-27] 10-20~10-26 周补齐（10-26 深夜以 today=10-26 重跑）：组装器排除当前周自身，已精选的 190 条直接复用 out_*.json，只精选新增 114 条；增量子 agent（厂商/社区/硬件/漏检）只追加 10-24~10-26 的内容。三个坑：(1) **部分周会多收修订稿**：部分周窗口是 10-18~10-24，修订日期为 10-18/19 的 arXiv 修订稿（含推荐第一的 HAFS）被收进来；全周窗口 10-20 起后它们出窗（修订稿不享受回看补采）。它们也不在 10-13 周（那时还没公开），所以用 `add_items.py 2026-10-13 … `（EDGE_TODAY=2026-10-19）补回上一周，网站不丢；以后部分周发布时就应把修订日期早于本周起始日的修订稿排除。(2) arXiv API 在多个子 agent 并发抓网页时触发 429，cs.AI 大类整体失败、coverage=incomplete；等接口恢复后单独重跑 `arxiv_curl_sweep.py` 即可，不要带着不完整的 manifest 组装。(3) `record_collection_history.py` 会把部分周也记一行，补齐后要删掉部分周那行（否则覆盖异常门的基线被重叠窗口污染）；改写该文件保持 indent=1、LF。
- [2026-10-30] 10-27~11-02 周部分周（today=10-30，窗口 10-24~10-30）：(1) 组装后先预筛再精选——修订日期早于本周起始日的修订稿、以及上期 run 里已评审未收的投稿（会因“未发布”重新出现）直接剔除，写进 `decisions.json` 的 `prefiltered`，精选只跑 `run-filtered.json`（211→180）；(2) arXiv 大扫描跑完前不启动会抓 arXiv 的硬件 arXiv 子 agent，本次没有 429；(3) 白名单缺口：Android 官方博客 `developer.android.com`（10-28 ML Kit 端侧智能体 API）原不在 OFFICIAL_SOURCE_DOMAINS，厂商子 agent 也没扫到；用户 10-30 同意加入，已补收为本周唯一的手机端侧 Agent。补收单条时**不要重跑 build_run_week**：当前周发布后，部分周窗口起点（10-24）早于周标签（10-27），组装器会把本周已发布条目当往期去重；应从首次组装的 run 加上新条目重建 `run-filtered.json`，并记得把重新签名的 collection-manifest 复制到 research_runs/ 再 publish；(4) 当前周不生成 `week/<label>.html`，部署后该页 404 是正常的；(5) MobiCom 2026 的 10-26 报告论文（ExoMem、mzCache）按报告日属上期，上期未收，只在本期硬件 section 作背景。追加时（11-02 后）要删掉部分周那行 collection_history，并补判 2603.10726（10-31 新修订）。

