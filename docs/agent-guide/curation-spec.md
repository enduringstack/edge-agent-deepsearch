# 周报条目整理规范（主 agent 下发给整理子 agent）

> 每周正式 run 组装后，主 agent 按本规范把条目分批（每批约 30 条）派给整理子 agent；子 agent 输出逐条记录，主 agent 复核后用 `agent/curation_merge.py` 合并。历史周回填同样使用本规范（窗口换成该周窗口）。

周报：端侧 AI Agent 论文雷达，窗口以主 agent 在任务里给出的为准。你拿到一批已通过来源校验的条目（输入 JSON），任务是**逐条读来源**，写出读者可见的中文整理字段和评分建议。你只产出一个 JSON 文件，不改代码、网页、服务器，也不改输入文件。

## 必读（逐字读完再动手）
- `docs/agent-guide/output-contract.md` 的「单篇条目字段」「首页可读性要求」「推荐策展规则」
- `docs/agent-guide/research-prompt.md` 的硬约束 2、3、4、10、12、13、14、15、16
- `data/tags.yaml`（标签词表；方向/应用/硬件维必须命中词表，模型维可从词表选）

## 每条怎么读
- arXiv 条目：打开 `https://arxiv.org/abs/<id>` 读摘要和 Comments（看是否被顶会接收、是否开源）。凡是端侧相关度可能 ≥7、或你想建议推荐的条目，再打开全文 `https://arxiv.org/html/<id>`（没有 HTML 就读 PDF）核实：实验设备（手机型号/NPU/Jetson/PC…）、关键数字、作者机构。不要用 arXiv API（export.arxiv.org 正在限流），用网页。
- 官方动态（vendors）：打开 `paper_url` 读正文，核对页面内容与标题对得上（对不上就标 drop）。effects 只写正文给出的结果数字。
- GitHub 条目：打开 release / commit 页，读改动内容。
- 输入里的 `source_summary` 是原文摘要，可作为起点，但最终以你打开的页面为准。

## 输出字段（每条一个 object，以 id 为键）
```json
{
  "<id>": {
    "drop": false,
    "drop_reason": "",
    "abstract": "这是什么：1-2 句中文大白话，说清它解决什么问题",
    "effects": "有什么结果：只写原文报告的关键数字和对比对象；没有量化结果写“未报告”",
    "mechanism": "怎么做到的：1-2 句普通话解释核心方法",
    "score_relevance": 0,
    "score_contribution": 0,
    "score_reason": "直接显示给读者的中文：为什么是这个端侧相关度、贡献在哪里（2 句左右）",
    "tags": ["方向:…", "硬件:…"],
    "open_source": false,
    "edge_agent_scope": "手机 | PC | 其他端侧 | 非端侧Agent",
    "edge_agent_evidence": "仅当 scope 为手机/PC/其他端侧时写：哪个规划/记忆/工具/行动闭环运行在什么设备上（中文）",
    "venue": "arXiv 或 接收会议名（如 NeurIPS 2026）",
    "accepted_top_venue": false,
    "company": {"vendors": "", "evidence_url": "", "evidence_note": ""},
    "recommend": false,
    "title_zh": "",
    "recommendation_reason": ""
  }
}
```

### 字段规则
- **drop**：只有这些情况才 drop：完全无关（与 AI 推理/部署/端侧/Agent 运行时都无关）、关键词误匹配（如图论的 edge、生物学 spike）、纯 GUI 自动化 Agent 且无非 GUI 创新、页面内容与标题对不上、实际不在窗口内。普通但相关的量化/剪枝/缓存/benchmark/云端 serving **不 drop**，给低分保留。写清 drop_reason。
- **abstract/effects/mechanism**：中文，写给工程师看，避免论文腔；保留关键数字、模型名、设备名（英文专名可保留）。不得粘贴英文原文，不得以省略号截断，不得出现 `auto-converted`、`votes=`、`待核实`、`精修待补`、`自动初评`、`主 Agent`、`复核` 等流程词。effects 必须来自原文，不许推测。
- **score_relevance**（0-10）：明确端侧部署/真机评测 8-10；端侧技术栈或可直接迁移（量化、KV cache、投机解码、小模型、高效注意力、Agent 记忆/工具调用运行时等）4-7；只与云端宽泛相关 1-3。
- **score_contribution**（0-10）：创新度高 7-10；常见方法/工程整合 1-6。
- **tags**：1-8 个，必须取自 `data/tags.yaml`。`方向:端侧agent` 只在 edge_agent_scope 为手机/PC/其他端侧时使用。
- **edge_agent_scope**：真正端侧 Agent = 同时具备 Agent 闭环（规划/记忆/工具调用/环境交互/行动之一）**和**设备端执行证据（关键闭环至少部分实际运行在手机/PC/机器人/汽车/IoT 上；端云协同时终端承担时延敏感闭环）。手机/PC 只是云端 Agent 的入口、普通端侧推理/量化/缓存/检测、纯云端 Agent 训练基础设施，一律 `非端侧Agent`。凡判为 手机/PC/其他端侧，必须写 edge_agent_evidence，并且 score_relevance ≥ 8、recommend=true。
- **company**：只有在论文首页作者机构（arXiv HTML/PDF 署名或邮箱域名）明确出现公司时才填，例如 Google、Apple、Meta、Microsoft、NVIDIA、Qualcomm、Samsung、Huawei、MediaTek、Xiaomi、OPPO、vivo、Honor、Alibaba/Qwen、ByteDance、Tencent、Baidu、Kuaishou、Meituan、JD、Pinduoduo、NetEase、Intel、AMD、Arm、SK hynix 等。`vendors` 写公司英文名（多家用 `; ` 分隔），`evidence_url` 写 `https://arxiv.org/pdf/<id>`，`evidence_note` 写中文依据（如“PDF 首页作者 3、4 署名 Qualcomm AI Research”）。不许凭作者名、模型名、被研究的平台名推测；不确定就留空。作者注明“以个人身份”或只写“现就职于”的不算该公司的项目。
- **accepted_top_venue**：Comments 明确写被 NeurIPS/ICML/ICLR/MobiSys/SenSys/ASPLOS/ACL/CVPR/ICCV/EMNLP/AAAI/IJCAI/TPAMI/TNNLS/ToN（或同级：MICRO/ISCA/HPCA/EuroSys/OSDI/SOSP/MobiCom/DAC）接收时为 true，并把 venue 写成会议名+年份。Findings、Industry Track、Workshop、学生研讨会（SRW）一律不算顶会（`accepted_top_venue=false`，venue 照写，如“ACL 2026 Findings”）；ACM CCS、IEEE S&P 等安全四大按同级算。
- **recommend**：值得读者优先看的才 true（端侧真机结果扎实、方法有新意、或对端侧 Agent 有直接价值）。整批通常只有少数几条。recommend=true 时必须写：
  - `title_zh`：中文项目名，回答“它叫什么”，2 个以上中文字符，≤40 字，不能复制 abstract。
  - `recommendation_reason`：一句中文说明“为什么值得优先看”，要具体（关键发现/数字/对谁有用），不能复述标题或写评分流水账。

## 文风参考（上周已发布的推荐条目）
- title_zh：端侧多智能体推理系统 EdgeAgent
- abstract：多个智能体互相配合跑在自己电脑上时，内存带宽会被抢爆、工具调用又会让硬件时不时空转。这套系统专门为统一内存架构的端侧设备重排了这类负载。
- effects：在 Apple M4 芯片上实测，仅统一内存感知的执行方式就比批量投机解码快 1.29 倍；再加上面向智能体的调度后，在工具调用时延很高的场景下整体加速 1.77 倍。
- recommendation_reason：本周少见的把「多个智能体一起跑在个人电脑上」当成系统问题正面解决的工作：它指出统一内存上的总线争抢和工具调用停顿才是真瓶颈，并在 Apple M4 上实测拿到 1.77 倍加速。

## 交付
- 用 Python `json.dump(obj, f, ensure_ascii=False, indent=1)` 写到指定输出路径；输入里的每个 id 都必须有一条输出（drop 的也要有）。
- 写完运行自检（必须无输出错误）：
  ```
  cd C:/Users/guanjungao/Desktop/chenfuduo/reportweekly/repo && python -X utf8 agent/check_curation_batch.py <输入文件> <输出文件>
  ```
- 完成后只回复简短总结：drop 几条、建议推荐哪几条（id + 一句理由）、判为端侧 Agent 的有哪几条（id + 设备）、填了公司归属的有哪几条。
