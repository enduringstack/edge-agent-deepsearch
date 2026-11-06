# 硬件洞察：端侧 AI 芯片月报（2026-10-08 ~ 2026-11-02）

> **一句话结论：10 月没有新的旗舰手机 SoC，端侧 AI 的进展全部发生在“芯片之外”——运行时、系统接口、整机内存和存储层级；同时 DRAM 涨价和出货下滑，正在把大内存的本地智能体设备压回高端。** 9 月三款 2nm 旗舰发布后，本月厂商讲的不再是 TOPS，而是“装得下多大的模型、智能体循环在哪里跑、每 token 要读多少字节”。
>
> **阅读结构（总-分-总）**：第 0 节是全月四个判断、对照表和时间线；第 1–6 节按方向展开（高通、Apple 与 Google、其他 SoC/PC/产业、低功耗与内存、顶会、arXiv）；第 7 节回到对端侧智能体的含义和 11 月观察清单。每周首页“硬件雷达”模块的每条动态都有“能跑多大模型”和可展开的技术细节。

## 0. 总览：本月四个判断

**判断一：软件栈在补硬件宣传的课，但新旗舰仍然没有端侧实测。** 9 月月报的判断五是“软件栈落后于硬件宣传”，10 月三家都在补：

| 厂商 | 本月软件栈动作 | 还缺什么 |
|---|---|---|
| 高通 | GenieX 从 0.8.1 预发布迭代到 0.10：工具调用、Decisions API、并行工具调用、投机解码（Eaglet/MTP）、Dragonwing IQ9 双 NPU 切分；AI Hub 上线 8 Elite Gen 6 真机 | 官方提速数字；8EG6/8EE6 零售机的 LLM tok/s（第三方反而先出了发热传闻和约 11% IPC 倒退） |
| Google | ML Drift 开源 → LiteRT Tensor API → Play 服务版 LiteRT → 10-28 ML Kit 端侧智能体 API（规划在设备上，Gemini Nano 4） | Nano 4 参数量与 tok/s 没有一手数字；能跑 Nano 4 的机型只有 7 款；Play 服务版 NPU 支持“开发中” |
| Apple | MLX 分布式后端（mlx-lm 0.32、MLX Swift 0.33）；Siri AI 拆成“本机 + 户主手机 + 私有云”三层，国行版“自研模型 + 千问” | 国行版本机/云端分流比例；M6 第三方 decode 实测 |

论文侧把高通 Hexagon 的真实瓶颈摸得比厂商更清楚：HMX→HVX 回落、softmax 受 HVX 限制、8 MiB VTCM、温控降频、decode 时 NPU 空闲。同一颗芯片换运行时，decode 速度最多差约 1.7 倍、待机功耗差 3 倍以上（论文实测）。**选设备要看目标运行时下的实测，不能看规格表。**

**判断二：PC 和 Mac 的竞争维度变成“统一内存容量 × 带宽 × 能否多机互连”。**

| 平台 | 内存 / 带宽 | 本月关键数字（口径） |
|---|---|---|
| Apple M5 Ultra（多机） | 单机 decode 接近带宽上限 | 4 台张量并行跑 816B-A42B MoE（NVFP4，约 493GB）36.73 tok/s（官方，ML Research）；27B BF16 带宽利用率约 89%（推算） |
| Apple M6（MacBook Pro / iMac） | 16–32GB，最高 170GB/s（M5 为 153GB/s） | 提升集中在 prefill；8B 4-bit decode 上限约 38 tok/s（推算） |
| NVIDIA RTX Spark 笔记本 | 大统一内存 | 10-16 全球开售；首批评测 8B 约 49 tok/s（媒体实测）；10-28 加智能体资源调度 |
| AMD 锐龙 AI Halo | 192GB | 整机 7299 美元（媒体口径） |
| IDC“智能体电脑”门槛 | 32GB + 135GB/s | 中国 2030 年 2080 万台（IDC 预测） |

**判断三：从常开 MCU 到手机，瓶颈统一到“内存”——读多少字节、从哪一层读、成本多高。**

- **常开级芯片开始写“生成式”**：BrainChip Sequora 标称最高 3B 参数；Coral NPU 32 位架构完工并进入 Synaptics SR200；Ceva 新 NeuPro 从 Nano 档起支持分页 KV 缓存和 MoE。全部只有架构目标值，没有功耗或 tok/s 实测。
- **论文侧的统一口径**：投机解码在 Mac 和手机 NPU 上都没有净收益；稳定见效的是减少读取字节（KV 剪枝、低比特、嵌入表压缩）。Tandem 在骁龙 8 Elite 上把 Qwen3.5-4B 的文本步降到 1.38 s、每步 10.1 J、待机 0.22 W（论文实测）。
- **新的容量层进入推理关键路径**：SSD 常驻 + DRAM 缓存（PC），铁电 NOR、HBF 挂在 LPDDR6 上（手机，仍是仿真）；美光 vEIM（2TB/s）、HBF 标准（SK 海力士称明年 1 月定稿）、CXL 内存池写进存储厂路线图。
- **存内计算新增的是钱和流片，不是性能数据**：后摩、九天睿芯、亿铸、微纳核芯四家国产存算公司都转向 3D 近存/HBF 堆叠；TetraMem 12nm RRAM 存算 SoC 流片。量产都在 2027 年以后。

**判断四：成本是反向变量，大内存本地智能体短期只属于高端。**

| 指标 | 数字 | 来源口径 |
|---|---|---|
| Q3 全球手机出货 | 同比 -22% | IDC |
| Q3 全球 PC 出货 | 同比 -20.1%（Counterpoint 为 -21%） | IDC / Counterpoint，口径不同 |
| Q3 手机 SoC 出货 | 同比 -21% | Counterpoint |
| Q4 DRAM 合约价 | 环比约 +20% | TrendForce 新闻栏目转引 |
| 联发科 Q3 | 手机 -17%，智能边缘平台 +63%，AI ASIC Q4 单季目标约 25 亿美元 | 公司法说会 |
| 树莓派 16GB 版 | 涨价 80 美元 | 官方 |

芯片厂的增长都来自数据中心，手机和 PC 的内存预算被压缩；TrendForce 预计品牌会减少内存来守价格。

### 关键事件时间线

| 日期 | 事件 |
|---|---|
| 10-08 | Google 开源端侧 GPU 推理引擎 ML Drift；IDC 公布 Q3 PC 出货 -20.1% |
| 10-12 | AMD 锐龙 AI Halo（192GB）；AI Hub 模型库 v0.64 与 GenieX 预发布 |
| 10-13 | Apple HomeView、HomePod mini 2、Apple TV 4K；华为麒麟沟通会（9050 逻辑折叠量产）；高通诉 Arm 案陪审团认定 Arm 违约 |
| 10-14 | BrainChip Sequora（3B）；IDC：Q3 手机出货 -22%；后摩公布 2D/3D CIM 路线 |
| 10-15 | Apple ML Research：4 台 M5 Ultra 跑 816B MoE；RTX Spark 评测解禁 |
| 10-16 | RTX Spark 笔记本全球开售；GenieX 0.9 正式版（工具调用、Decisions API） |
| 10-19~22 | PACT 2026（存内计算 LLM 专场）；LiteRT Tensor API |
| 10-20 | Coral NPU 32 位架构完工，Synaptics SR200 同日发布；美光边缘推理内存路线图（10-21） |
| 10-23 | 九天睿芯融资（SRAM + HBF 存算）；Pura 90 Plus 开订，首发麒麟 9025 |
| 10-26~30 | MobiCom 2026（NPUGen、LeanStream、AppFlow 等） |
| 10-27 | M6 MacBook Pro / iMac；TetraMem RRAM 存算 SoC 流片 |
| 10-28 | ML Kit 端侧智能体 API（Nano 4）；GenieX 0.10；Ceva 新 NeuPro；触屏 OLED MacBook Pro（M5 Max）；SK 海力士 Q3（HBF 入长期战略）；微纳核芯超 10 亿元 C2 轮 |
| 10-30 | 联发科 Q3 法说会；Counterpoint：Q3 手机 SoC 出货 -21% |
| 10-31 | 国行 Apple 智能定档（11-04 测试、12 月上线）；MICRO 2026 开幕 |
| 11-02 | MICRO 主会首日（EdgeXpert、HeteroMosaic）；树莓派 16GB 版涨价 |

## 1. 高通：工具链补课，新旗舰缺实测

### 本月结论：没有新芯片，高通把月度精力花在“让 NPU 真能用”上

10-08 到 11-02 这近四周，高通没有发布任何新 SoC。第六代骁龙8至尊版（8EG6，SM8950）和超级至尊版（8EE6，SM8975）是 9 月骁龙峰会发布的，本月处在“工具链接入、零售机上市、口碑发酵”的阶段。官方动态几乎全部落在软件栈上。端侧大模型运行时 GenieX 从 v0.8.1 预发布一路迭代到 v0.10.0，把工具调用、Decisions API、并行工具调用、投机解码和双 NPU 切分接进了 Hexagon 路径。AI Hub 在云端编译服务里上线了两颗新旗舰的真机，模型库和应用跟进到 QAIRT 2.50。PC 侧补齐了原生 Python、x64 移植智能体和 SME 编译器。

硬件层面最有信息量的反而是负面消息：三星验证阶段传出 8EE6 过热（高通否认），极客湾零售机横评测出 IPC 倒退约 11%，同时 Exynos 2700 的内部跑分爆料频出。8EG6 的 NPU 至今没有公开的官方或第三方 tok/s。本月能引用的骁龙 NPU 实测仍来自上一代 8 Elite / 8 Elite Gen 5，主要出自论文和社区模型卡。

研究侧，高通 AI Research 本月发了四篇对端侧有直接价值的论文（投机解码选层、NPU 移植智能体、可穿戴 ASR 压缩、W4A4 量化），第三方又发了至少六篇以骁龙 Hexagon 为实验平台的系统论文。它们合起来把 Hexagon 的几个具体瓶颈摆到了台面上：HMX 与 HVX 的分工、softmax 走向量单元、VTCM 容量和单图映射上限。一句话概括本月：**骁龙的端侧 AI 瓶颈已经从“算力够不够”转到“运行时和工具链会不会用”。**

### 一、旗舰芯片：8EG6 / 8EE6 进入零售，NPU 数据缺位，口碑先受压

**工具链先行接入。** 按 [AI Hub Workbench 发布说明](https://workbench.aihub.qualcomm.com/docs/hub/release_notes.html)（官方，已核），10-12 版上线了 SM8950 和 SM8975 真机，QAIRT 升到 2.51.0，并为 v81 及以后的 DSP 启用 HTP 精度补偿。10-21 的 [AI Hub Models v0.65.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.65.0) 把两颗新芯片加进官网性能页，同时撤下 Galaxy S24。10-28 的[上游 Linux 博客](https://www.qualcomm.com/developer/blog/2026/10/same-day-snapdragon-8-elite-gen-6-upstream-linux-support)回顾了芯片发布后 24 小时内提交到 LKML 的补丁，也第一次在官方文档里写出部分规格（官方口径）：GPU 分别为 Adreno 850 和 Adreno 845，存储为 UFS 4.1，Compute DSP 和 Audio DSP 都进了上游，另提供可启动的 Debian 13 镜像。Compute DSP 进上游以后，Linux 设备才能通过 FastRPC 调用 Hexagon，机器人和工业终端可以更早用上旗舰 SoC。

但这些发布都没有给出新旗舰的 LLM 数字。9 月的官方口径是“8EE6 可在端侧跑 30B MoE（约 3B 激活）”，按 LPDDR6 约 114–127 GB/s 推算，decode 上限约 76–85 tok/s。到本月底，这个口径既没有官方 tok/s，也没有第三方实测。

**过热与 IPC：口碑先于数据。**
- 10-16，[9to5Google](https://9to5google.com/2026/10/16/samsung-galaxy-s27-snapdragon-overheating-report/) 等转述首尔经济日报的爆料：三星测试发现 8EE6 在长时间重负载下过热，Galaxy S27 Ultra 可能改用 Exynos 2700。高通对 9to5Google 的声明是“Recent reporting about thermal issues related to Snapdragon 8 Elite Extreme Gen 6 is inaccurate”（已打开原文核实）。
- 10-25，[朝鲜日报](https://biz.chosun.com/it-science/ict/2026/10/25/LYNO7ACPWRECDA5UDZRHHMLA6E/)爆料：Exynos 2700 内部测试的 Geekbench 6.5 多核约 13000 分，比 8EE6（约 11000 分）高约 20%，GPU 峰值也高约 20%。NPU 数据未披露。
- 10-30，IceUniverse 又称欧版 [S27 Ultra 仍未见 Exynos](https://www.sammyfans.com/2026/10/30/samsung-galaxy-s27-ultra-could-remain-snapdragon-exclusive/)，方向与前两条相反。

三条都是爆料，可信度中低，且互相矛盾。

10-27，极客湾发布零售机横评，以下数字引自[电脑王阿达的转述](https://www.kocpc.com.tw/archives/700857)（第三方实测，二手转述）。8EE6 的 IPC 比上代倒退近 11%。L2 TLB 延迟从 13.4 ns 升到 20 ns，约 1 MB 就需要查页表。《原神》60 帧功耗 3.7 W，A20 Pro 为 3.1 W。工程机上没有测出退步，后续固件可能改变结果，横评也没有测 NPU。下面是推算：LLM decode 要连续扫过 GB 级权重，TLB 覆盖变小对 CPU 侧推理不利；NPU 路径是否受影响没有数据，不能直接外推。过热传闻、IPC 倒退和 Exynos 回归三件事叠在一起，让“2nm 旗舰的持续负载能效”成了本月骁龙最大的问号，而端侧 Agent 恰恰是持续负载场景。

**市场与终端。** [Counterpoint](https://www.counterpointresearch.com/en/insights/smartphone-oems-shift-focus-to-profitability-as-soc-shipments-fall-21-percent-yoy)（第三方口径）统计，Q3 全球手机 SoC 出货同比下降 21%，高通与联发科、紫光展锐一起承压，全年预计下降 20%；Q4 的高端出货靠三颗 2nm 旗舰拉动。终端只有零星爆料：[一加可能首发“SM8845 Pro”](https://www.androidauthority.com/oneplus-turbo-snapdragon-8-gen-5-pro-3725410/)（低可信），摩托罗拉 Signature 27 宣布将在印度发布，据媒体报道搭载 8EE6。

**本月能用的骁龙 NPU 实测仍在上一代。** 下面几组数字可以当作 8EG6 实测出来之前的基线：
- [LG U+ ixi-sLM](https://arxiv.org/abs/2610.19382)（论文口径）：1.2B 模型压到 803 MiB，在 Galaxy S25 Ultra NPU 上预填充 3558 tok/s、解码 55.8 tok/s。推算有效带宽约 45 GB/s，约为该代 LPDDR5X 理论值的一半。
- 社区模型卡（第三方实测，来源为 litert-community）：[Nemotron-3.5-Bolt-E4B](https://huggingface.co/litert-community/NVIDIA-Nemotron-3.5-Bolt-E4B) 在 Galaxy S26（8 Elite Gen 5，SM8850）NPU 上预填充 742 tok/s、解码 12.2 tok/s，GPU 解码反而更快，为 15.2 tok/s；[d1-Omni-2B](https://huggingface.co/litert-community/d1-Omni-2B-LiteRT) 决策图单次调用 67 ms；[parakeet-ultra](https://huggingface.co/litert-community/parakeet-ultra) 语音识别 115 倍实时。

推算：若 E4B 按约 4B 有效参数、4-bit 计，每 token 约读 2 GB，按约 85 GB/s 估算，decode 上限约 40 tok/s。实测 12.2 tok/s 只到上限的三成左右，说明 NPU 的 decode 路径还没有触到带宽墙，运行时还有空间。NPU 文件的实际精度未披露，这个估算只作量级参考。

### 二、软件栈：GenieX 一月三版，Hexagon 变成兼容 OpenAI 接口的本地 Agent 服务端

本月高通最密集、也最对题的动作是 [GenieX](https://github.com/qualcomm/GenieX/releases)。迭代脉络如下（均为官方 release notes）：

- **v0.8.1 预发布（10-06~10-09）**：alpha.3 把 QAIRT 插件升到 2.50，这是 LLM 路径对齐 2.50 的第一步。
- **[v0.9.0](https://github.com/qualcomm/GenieX/releases/tag/v0.9.0)（10-16，转正式版）**：
  - QAIRT 后端支持工具调用；服务端新增 OpenAI 风格的 Decisions API 和结构化决策；推理内容和正文分开输出。
  - 修复 Dragonwing IQ9/IQ8 上 HTP 的 FastRPC 映射失败；加载时预热，让 HTP 映射不再计入首 token 延迟。
  - GPT-OSS 的专家层不再固定在 CPU 上；多模态投影器默认放到独立的 HTP 会话。
  - 之后 v0.9.1 和 v0.9.3 两三天一版。
- **[v0.10.0](https://github.com/qualcomm/GenieX/releases/tag/v0.10.0)（10-28，已核）**：
  - PR #1600 在 Dragonwing IQ9 上把 llama.cpp 的 HTP 后端按行切分到两颗 NPU；
  - PR #1580 让 QAIRT 插件支持 Qwen3-8B-Eaglet；
  - PR #1603 加入并行工具调用控制（破坏性变更）；
  - 新增 /health 和 Prometheus /metrics 端点；
  - Windows on Snapdragon 改用微软签名的 HTP catalog，不再需要手动导入证书。
- **[v0.10.1-rc.1](https://github.com/qualcomm/GenieX/releases/tag/v0.10.1-rc.1)（10-29）**：HTP 上的 MTP 解码与 llama.cpp 对齐。

这条线值得和 9 月对照着看。9 月月报指出，MoE 和 MTP 投机解码当时只在 llama.cpp 路径可用，QAIRT 路径会忽略投机解码设置，工具链落后于“30B MoE + 增强投机解码”的硬件宣传。本月 GenieX 补上了其中两块：GPT-OSS 专家层上 NPU，以及 Eaglet/MTP 投机解码上 HTP。缺口在缩小，但官方仍没有给任何提速数字。另一个变化是 Agent 接口的位置：工具调用、Decisions API、并行工具调用和监控端点都放在服务端，说明高通想把 GenieX 做成一个跑在 NPU 上、兼容 OpenAI 接口、可监控的本地推理服务，让手机、PC 和 Dragonwing 边缘盒都能当 Agent 后端。

**AI Hub 的配套更新。**
- [Models v0.64.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.64.0)（10-12）：维护性更新，移除旧的 `python -m` 导出入口。
- v0.65.0（10-21）：GenAI 运行时从 QAIRT 2.45 升到 2.50；新增 LFM2.5-1.2B-Instruct、V-JEPA-2 和一批离线 TTS/翻译模型；导出改用 torch.export（最低 PyTorch 2.9），属于破坏性变更；Gemma-4-E4B 只保留 q4_0 版本，说明 4B 级多模态模型的官方推荐路径转向 llama.cpp/GGUF。
- Workbench 10-27 版：新增 Projects / Teams / Organizations，AIMET-ONNX 升到 2.42.0，开始往企业协作方向走。

需要注意版本节奏：云端编译已到 2.51，端侧运行时和模型库在 2.50，两者差一个版本。

**社区反馈揭示“NPU 可用性”缺口**（以下均为个人自测，仅作线索）。
- [Open NPU](https://www.reddit.com/r/LocalLLM/comments/1xftovg/i_made_an_opensource_app_to_run_llms_on_the/) 作者发现，Surface Laptop 7（X Plus）上 Ollama、LM Studio 默默跑在 CPU 上。改走 NPU 后，Qwen3-4B 约 14 tok/s，LFM2.5-8B-A1B 约 31 tok/s，首字时延最多快约 18 倍。但高通预编译包在他的驱动上只能加载约 1.7B 以下的模型。
- 300 英镑的骁龙 X 迷你主机只能用 CPU，跑 35B-A3B 约 24.5 tok/s。
- 安卓开发者[求助](https://www.reddit.com/r/androiddev/comments/1xg7mxm/getting_a_model_to_genuinely_run_on_the_hexagon/)：在 V73 上让模型真正跑在 NPU 上很难，QNN EP 不接受动态形状，V75 的编译产物在 V73 上不能用。
- 10-28 的 [GenieX 介绍帖](https://www.reddit.com/r/LocalLLaMA/comments/1xhob18/ggufs_on_snapdragon_hexagon_npu_using_geniex/)把“无需测试签名驱动”当成最大卖点。

这几条正好说明，GenieX 本月要解决的就是第三方应用“用不上 NPU”的问题。

### 三、PC 与开发者生态：Windows on Snapdragon 补底座，AI PC 叙事从 TOPS 转向系统

- **原生 Python**（10-14，[官方博客](https://www.qualcomm.com/developer/blog/2026/10/native-python-windows-on-snapdragon-stronger-foundation-for-developers-ai-workflows)）：从 Python 3.15 起，Windows on Snapdragon 成为 CPython 的 Tier 2 目标。下载量前 1000 的包中有 95% 已有原生 wheel 或不需要 wheel，但 OpenCV、PyArrow、gRPC、JAXlib 仍缺原生 wheel。
- **WoS Porter**（10-20，[官方](https://www.qualcomm.com/developer/blog/2026/10/port-windows-projects-to-windows-on-snapdragon-with-agentic-ai)）：用 Copilot、Claude Code、Codex 插件形态的编码智能体，分 8 个阶段完成 x64 到 Arm64 的移植和 NEON 优化。官方实测 CRC32C 提速约 5.2 倍，SQLite 只有 1.07 倍。
- **[Adreno Vulkan/OpenCL 零拷贝](https://www.qualcomm.com/developer/blog/2026/10/how-to-share-vulkan-opencl-workloads-android-adreno-gpus)**（10-22）：面向在 GPU 上做 ML 后处理的手机应用，最优路径依赖高通私有扩展，没有给性能数字。
- **[Ripple](https://www.qualcomm.com/developer/blog/2026/10/ripple-llvm-aarch64-sve-sme-kernel-implementation)**（10-29，官方自测）：用开源 LLVM 的 SPMD 接口写 SME 内核。FP32 GEMV（对应 decode）与手写 SME 核相差不到 5%，代码约 17 行，对应汇编约 1200 行；INT8 GEMM 大矩阵相差约 1–2%。这给 Armv9 CPU 跑 LLM 矩阵运算提供了 NPU 之外的第二条路径，也呼应了 9 月 8EG6“CPU 带硬件 AI 加速”却没交代 SME 细节的空白。不过高通没有说明自家 Oryon 是否实现了 SME，示例按 512-bit 流式向量长度编写。

**渠道与定位。**
- 10-27，高通与 Anduril 发布美制加固笔记本 [BlueChip](https://www.qualcomm.com/news/releases/2026/10/anduril-and-qualcomm-unveil-bluechip-to-rebuild-american-compute)：官方只写了“骁龙 X 系列”，没有给型号和 NPU 规格；BOM 中美国及盟国供应商占采购成本 90% 以上，2027 年开始接单。离线推理在国防场景是刚需。
- 10-30 [Counterpoint 访谈](https://counterpointresearch.com/en/insights/counterpoint-conversations-snapdragon-x-series-ai-pcs-agentic-ai-googlebook-linux)（媒体转述厂商观点）：高通讲 AI PC 时不再突出峰值 NPU TOPS，改为强调 CPU、GPU、NPU、内存带宽和软件的整体，并把 X2 定位为常驻后台的低功耗 AI 负载；Googlebook 用的是第一代 X Elite；X2 的 Linux 支持由 Debian 在年内先行，Ubuntu 2027 年初跟进。
- 10-20 [IDC](https://www.ithome.com/1/015/221.htm)（第三方口径）：智能体电脑的门槛是至少 32 GB 内存、135 GB/s 带宽，30B 级模型是参考基准，并把 X2 Elite/Plus 列为代表平台。X2 Elite 官方带宽为 152/228 GB/s，跨过了门槛。推算：在 228 GB/s 下，激活约 3B 的 30B MoE 理论上限约 150 tok/s，稠密 30B 4-bit 约 15 tok/s。

另外，高通旗下 Modular 在 10-22 发布 [MAX 26.7](https://max.modular.com/releases/v26.7/)，全文仍没有提到骁龙或 Hexagon。收购完成约 3 个月，编译器栈还没有和端侧硬件打通的迹象。

### 四、研究：高通 AI Research 与第三方论文一起摸清 Hexagon 的边界

**高通 AI Research 本月四篇（论文口径）。**
- [ELSI](https://arxiv.org/abs/2610.12939)（10-09）：给 EAGLE3 类草稿头选目标模型的隐状态层。只取 1 层就能持平 EAGLE3 默认的 3 层，草稿头更小、额外访存更少。实验全部在 H100 上完成。
- [AIPC](https://arxiv.org/abs/2610.34890)（10-26）：让带“技能”的 LLM 智能体把 PyTorch 项目移植到 QCS9075 的 HTP 上。Whisper-Small 带技能时 7 次中 6 次达标（对照组 0/6），YOLO-Worldv2 端到端 2.79 倍（对照组 1.60 倍）。论文顺带公开了几条部署硬限制：VTCM 为 8 MiB，MeloTTS 解码器需要 11.16 MiB 而超限；Qwen3-0.6B 单图约 1.50 GiB 触及映射上限，需要拆图。
- [Depth through Recurrence](https://arxiv.org/abs/2610.37833)（10-27）：把 ASR 编码器换成循环调用的共享块。108.9M 编码器压到 14.2M，仍恢复 97.4% 的精度，目标是手表和眼镜。能耗只在 Apple M4 Pro 上测（单共享块时 DRAM 能耗降 1.46 倍），没有骁龙可穿戴实测。
- [HZ-PTQ](https://arxiv.org/abs/2610.40345)（10-29）：W4A4KV4 逐通道设置下，Llama 3.2 1B 困惑度 16.05（FlatQuant 17.23），Qwen3 8B 为 10.43。逐通道 W4A4 最贴合 NPU 的整数单元，但论文没有 Hexagon 真机数据。

四篇分别对应投机解码、部署自动化、可穿戴常驻语音和低比特量化，都直接服务于 9 月提出的“30B MoE + 增强投机解码”和“200M 到 2B 的低功耗梯度”。共同短板是没有一篇给出 8EG6 真机数字。

**第三方在骁龙上的实测（论文口径）。**
- [手机 NPU 做 LoRA 训练](https://arxiv.org/abs/2610.24816)（10-17）：在 OnePlus 15（Hexagon V81）等机型上，Llama-3.2-3B 训练 72.9 tokens/s，能耗 0.2275 J/token，约为 CPU 方案的 32%。
- [Tandem](https://arxiv.org/abs/2610.26660)（10-19）：发现混合线性注意力模型（Qwen3.5-4B）为保留回滚状态，会从 HMX 退到 HVX 逐 token 计算，预填充多出 614 ms。修复后每步延迟降 16–30%，待机功耗从 0.76 W 降到 0.22 W。
- [边缘 NPU 的 VLM 测量](https://arxiv.org/abs/2610.40039)（10-29，中南大学 / 微软研究院）：在 Hexagon v73、v79 上发现 softmax 主导注意力开销且受 HVX 限制；线性注意力因张量重排在真实 NPU 上跑输；持续推理会触发热降频。
- [NPUGen](https://dl.acm.org/doi/10.1145/3795866.3844480)（MobiCom 2026）：让 decode 期间闲置的 NPU 重算 KV，代替从存储换入。
- [CrossInfer](https://arxiv.org/abs/2610.35309)：在 QCS6490 等三个平台上，让 CPU、GPU、NPU 共享 VLM 上下文，吞吐超过最强单引擎基线。

这些工作合起来给出了一张 Hexagon 的“问题清单”：
- HMX 矩阵单元快，但递推状态、softmax 和张量重排会掉到 HVX 向量单元；
- VTCM 和单图映射容量限制模型切分方式；
- 持续负载会热降频；
- decode 期间 NPU 常常闲置。

这份清单比任何 TOPS 数字都更能说明骁龙 NPU 跑 Agent 的真实上限。

### 五、边缘、XR、可穿戴与车载：Dragonwing 和 Reality Elite 开始落到产品

- **家庭网关当 Agent 宿主。** 10-12 Network X 前夕，高通发布 [AI 原生宽带平台](https://www.qualcomm.com/news/releases/2026/10/qualcomm-unveils-ai-native-broadband-innovations-across-fiber--w)（官方口径）：
  - FWA Gen 6 Elite 集成 X105 5G Modem-RF 和 NPU，下行峰值 14.8 Gbps；
  - gFiber 与 Gemtek 推出首款基于 NPro A8 Elite 的 Wi-Fi 8 网关，内置 Hexagon NPU，演示了语音意图式家长控制；
  - Dragonwing SAM 端云协同框架，官方称已有超过 1000 万台网关运行 SAM agent。

  各平台的 NPU 算力和模型规模都未披露。10-30 的 OnQ 文章只是对 FWA 平台的勘误（6Rx 改为 8Rx），不是新品。
- **XR。** 10-28 Google 与 XREAL 推出 [XREAL AURA](https://developer.android.com/blog/posts/build-it-your-way-a-next-era-of-android-development#xreal-aura)，计算盒用 Snapdragon Reality Elite（48 TOPS，高通 6 月口径），12 GB 版售价 1099 美元（媒体口径），11 月中旬起发货。这是 Reality Elite 的第一款消费产品，但 Gemini 是否在端侧运行，官方没有说明。
- **可穿戴。** 10-16 OnQ 发布 [1.2 万人调研](https://www.qualcomm.com/news/onq/2026/10/personal-ai-wearables-consumer-survey)：近 60% 的可穿戴用户每周使用 AI，约 70% 对语音驱动的个性化 Agent 感兴趣。这是厂商自办调研，只能当营销口径看。
- **机器人与车载。** 10-26 [Counterpoint](https://www.counterpointresearch.com/en/insights/nvidia-leads-humanoid-robot-ai-accelerator-market)（第三方口径）称，高通以能效和更低 BOM 切入人形机器人加速器市场，合作方包括 Figure AI、Booster 等，但出货量明显落后 NVIDIA。10-20 高通宣布 [V2X 统一地区标准](https://www.qualcomm.com/news/releases/2026/10/qualcomm-to-unite-regional-v2x-standards-under-global-v2x-soluti)，新增日本 760 MHz 支持，与 NPU 无关。
- **6G。** 10-21 OnQ [文章](https://www.qualcomm.com/news/onq/2026/10/designing-6g-to-adapt-to-ai-demand)提出：随着推理变快，通信时延在首 token 时延中的占比会上升，要在终端用 AI 识别 Agent 的突发流量，并动态调整 QoS。

### 六、产业：“100B 手机”、Arm 案与裁员

- **100B 手机。** 10-10 前后，安蒙在播客中称有前沿 AI 公司要求 2028 年手机能本地跑至少 100B 参数的模型（[媒体转述](https://tech.yahoo.com/ai/apple-intelligence/articles/qcom-ceo-cristiano-amon-says-105424604.html)）。这是客户需求信号，不是路线图。推算：100B 稠密模型 INT4 约 50 GB，远超今天手机最高 24 GB 的内存；按 LPDDR6 约 127 GB/s，稠密模型 decode 上限约 2.5 tok/s，激活 3B 的 MoE 上限约 85 tok/s。现实路径只能是大总参、小激活的 MoE，加闪存专家流式加载。本月 NPUGen、LeanStream 等闪存与 KV 方向的论文正是在补这一块。
- **Arm 案。** 10-13，美国特拉华州陪审团认定 Arm 违反架构授权协议，但只判赔 2 美元（[高通声明](https://www.qualcomm.com/news/releases/2026/10/qualcomm-statement-on-trial-verdict-win)），这对 Oryon 自研 CPU 路线是利好。10-16 高通与传音续签专利授权至 2031 年。
- **裁员。** 10-20 路透独家报道（[The Star 转载](https://www.thestar.com.my/tech/tech-news/2026/10/20/exclusive-qualcomm-to-cut-jobs-worldwide-in-performance-focused-layoffs-internal-memo-shows)），高通将在全球按绩效裁员，人数未披露，并预计 2027 财年大部分芯片收入来自非手机业务。

### 判断与下月观察

本月有三个判断。

第一，高通在端侧 AI 上的投入重心明确转到软件栈。GenieX 一个月从预发布走到 v0.10，Agent 接口（工具调用、决策、并行调用、监控）和 NPU 能力（MoE 专家上 HTP、投机解码、双 NPU 切分）同步推进。9 月“工具链落后于硬件宣传”的缺口在收窄，但还没有官方提速数字可以验证。

第二，8EG6 / 8EE6 的端侧 AI 能力仍是“只有口径、没有实测”。零售机首批第三方数据集中在 CPU IPC 和功耗，而且偏负面；过热传闻又与 Exynos 2700 回归的爆料绑在一起。旗舰的持续负载能效会直接决定长时 Agent 的体验，这是骁龙下一阶段最需要用数据回应的问题。

第三，Hexagon 的真实瓶颈正被第三方论文系统地揭示出来，包括 HVX 回退、softmax、VTCM、热降频和 decode 期 NPU 闲置。同一颗芯片换一个运行时，解码速度可以差 1.7 倍，待机功耗可以差 3 倍以上。端侧选型和评测应以“目标运行时 + 目标芯片”的实测为准，不能只看芯片规格。

下月观察：
- 11-04 发布的 FY26 第四季度财报（已在本窗口之后）里，手机、PC、IoT 和汽车的收入结构，以及裁员范围是否波及 Hexagon 和端侧软件团队；
- 8EG6 / 8EE6 机型上的首批第三方 NPU 与 LLM 实测，尤其是 30B MoE 能否在零售机上以可用速度跑起来；
- GenieX 是否公布 Eaglet/MTP 和双 NPU 切分的提速数字；
- Galaxy S27 的芯片分配是否尘埃落定；
- XREAL AURA 上市后，Reality Elite 的端侧模型实测。

## 2. Apple 与 Google：端侧 AI 拼内存与系统接口

10 月（10-08 ~ 11-02）Apple 与 Google 都没有发布新的旗舰手机芯片，但两家都把端侧 AI 从“芯片规格”推进到了“部署形态”。Apple 的主线是**容量与分层**：月中 ML Research 公布 M5 Ultra 和多机 RDMA 的官方 tok/s，月底 M6 进入 1999 美元的 MacBook Pro 和 iMac，M5 Max 机型的新闻稿直接写了“在本机跑编码智能体”；同时 Siri AI 被拆成三层，家居设备做常开入口，户主手机提供个人上下文，Private Cloud Compute 兜底，国行版则换成“自研模型 + 千问”。Google 的主线是**系统化**：一个月里先后开源 GPU 引擎 ML Drift、发布 LiteRT Tensor API、把 ML Drift 放进 Play 服务，10-28 又推出基于 Gemini Nano 4 的 ML Kit 端侧智能体 API；最底层，Coral NPU 32 位架构完工，Synaptics 首颗商用芯片同日发布。本月两家的共同变化是：卖点从 TOPS 转向“装得下多大的模型、智能体循环在哪里跑”，而决定上限的仍是内存容量和带宽。Tensor G6 和 Gemini Nano 4 本月都没有新的官方参数或 tok/s。

### Mac：官方 tok/s、多机互连与 M6 换代

本月 Apple 端侧数字最硬的一篇是 10-15 Apple ML Research 的 [MLX 多机分布式推理实测](https://machinelearning.apple.com/research/mlx-distributed-inference)（官方口径）。M5 Ultra 内存带宽 1.2 TB/s（M3 Ultra 为 819 GB/s），最高 512GB 统一内存，峰值功耗约 300W。单机 decode：Qwen 3.8 27B BF16 从 M3 Ultra 的 12.46 tok/s 提到 19.69 tok/s，Mistral Medium 3.5 128B FP8 从 4.95 提到 7.70；4 台张量并行分别到 50.89 和 23.37 tok/s。单机放不下的 Muse Spark Open 816B-A42B（NVFP4，约 493GB）用 4 台张量并行跑到 36.73 tok/s。按“带宽 ÷ 每 token 读取字节”推算，27B BF16 每 token 约读 54GB，上限约 22 tok/s，实测带宽利用率约 89%；128B FP8 上限约 9.4 tok/s，利用率约 82%（推算）。单机已接近带宽天花板，而 816B MoE 的多机 decode 远低于按带宽算的上限，瓶颈转到 Thunderbolt 5 RDMA 互连：65K 上下文下每条链路从 1 根线加到 2 根，TTFT 从约 50.5 秒降到 40.6 秒。

软件栈全月跟进：[mlx-lm v0.32.0](https://github.com/ml-explore/mlx-lm/releases/tag/v0.32.0)（10-15）在模型发布当周就支持 816B NVFP4 MoE 和 2-bit Hadamard 旋转量化，[MLX v0.32.4](https://github.com/ml-explore/mlx/releases/tag/v0.32.4) 为 M5 之前的芯片优化了 SDPA 内存；10-27 的 [mlx-swift 0.33.0](https://github.com/ml-explore/mlx-swift/releases/tag/0.33.0) 启用 JACCL 分布式后端，原生 Swift 应用不经 Python 也能做多机推理。月初 Apple 的 [Minions](https://arxiv.org/abs/2610.12970)（10-09，arXiv）介绍了内部用闲置 Mac 组建批量推理云的做法，不过只给出“GPU 排队从数小时降到分钟级”这类定性结论，没有 tok/s 和设备数量。第三方方面，MacPaw 的[复测论文](https://arxiv.org/abs/2610.31479)（10-22，arXiv）提醒，服务器上的优化不能照搬到 Mac：KV 剪枝在 Qwen3-4B 上端到端加速 1.61–1.75 倍（同条件 RTX 4090 只有 0.98 倍），但 6 种投机解码在 MLX 单请求下全部没有净收益，M3 Ultra 4-bit 下 DFlash 甚至把 decode 从 156.7 拉低到 60.0 tok/s（论文实测）。

产品端，月初的爆料基本兑现。Gurman 10-09 称[10-27 前后发布 M6 Mac 与触屏 MacBook](https://www.gsmarena.com/gurman_apple_to_announce_its_touchscreen_macbook_on_october_27-news-74969.php)，Apple 10-19 [确认 10-28 洛杉矶活动](https://www.macrumors.com/2026/10/19/apple-pro-and-tell/)；实际是 10-27 发新闻稿、10-28 办媒体体验。[14 英寸 MacBook Pro（M6）](https://www.apple.com/newsroom/2026/10/apple-introduces-the-new-14-inch-macbook-pro-with-m6/)和 [iMac（M6）](https://www.apple.com/newsroom/2026/10/apple-unveils-new-imac-with-m6/)给出的官方对比数字为：双 16 核 Neural Engine 比 M5 快最高 1.9 倍，LLM 首 token 比 M5 MacBook Pro 快 1.3 倍、比 M1 快 13 倍，LLM prompt processing 比 M5 快最高 25%；iMac 在 LM Studio 中的 prompt processing 比 M4 快最高 5 倍。这些都是 Apple 内部测试，没有给出模型、量化方式和上下文长度。内存为 16GB 起、最高 32GB，带宽最高 170GB/s，只比 M5 的 153GB/s 高约 10%。所以 M6 的提升集中在 prefill，decode 变化不大：8B 4-bit 的 decode 上限约 38 tok/s，14B 约 21 tok/s，32GB 实际可放的稠密模型约 27B–32B（均为推算）。

10-28 的 [PROLED XDR MacBook Pro](https://www.apple.com/newsroom/2026/10/apple-unveils-groundbreaking-macbook-pro-with-proled-xdr-display/) 印证了“跳过 M6 Pro/Max”的爆料，芯片仍是 3 月的 M5 Pro/Max（最高 128GB，Max 为 614GB/s），增量在触控 OLED、灵动岛（Siri AI 入口）和更轻的机身，官方称持续性能与上代相同。新闻稿第一次把“用端侧 LLM 运行编码智能体”和“在设备上运行数千亿参数 LLM”写成卖点。后者只说明 128GB 装得下低比特 MoE：70B 稠密 4-bit 的 decode 上限约 16 tok/s，激活约 5B 的百亿级 MoE 才能达到百 tok/s 量级（推算）。Gurman 关于 [M7 Pro/Max 要到 2027 年底、M7 Ultra 到 2028 年上半年](https://www.macrumors.com/2026/10/15/macbook-pro-m7-late-2027/)的说法仍是爆料。照此看，到 2027 年底前，高端 Mac 本地推理能力的提升主要靠 M5 Ultra 加多机互连，而不是新一代芯片。

### iPhone 与 iPad：A20 Pro 按档位切 Neural Engine

10-23 开售的 iPhone Duo 在首销前有一组[媒体实测](https://www.tomsguide.com/phones/iphones/iphone-duo-full-benchmarks-the-worlds-fastest-foldable-but-how-does-it-stack-up-to-iphone-18-pro)（Tom's Guide）：Geekbench 6 为 4,722/12,708，与 iPhone 18 Pro（4,735/12,800）差距不到 1.5%，说明 A20 Pro 放进折叠机身后短时性能几乎不降频。Geekbench AI 1.7 量化分为 69,438（Core ML），略低于 Galaxy Z Fold 8 系列的 71,715–72,242（TFLite QNN）。两边后端不同，3–4% 的差距只能作参考。Pixel 11 Pro Fold（Tensor G6）的 CPU 分约为 Duo 的 57%，Geekbench AI 一栏原文数据异常，不能用来判断 Tensor G6 的 NPU 水平。内存约 12GB（据 Geekbench 记录推断，Apple 未确认）。按约 115GB/s 带宽推算，4-bit 8B 模型 decode 上限约 29 tok/s。

10-26 的 [iPad mini](https://www.apple.com/newsroom/2026/10/apple-gives-ipad-mini-its-biggest-update-ever/) 换上 2nm A20 Pro，官方称 AI 性能最高为上一代 4.5 倍、统一内存带宽提升 2 倍以上，每个 GPU 核心带神经加速器。按 [Apple 规格页](https://www.apple.com/ipad-mini/specs/)，只有 512GB 版是 6 核 CPU + 双 16 核 Neural Engine，128/256GB 版是 5 核 CPU + 单 16 核。同一型号的 NPU 规模相差一倍，这是 Apple 第一次按存储档位切分端侧 AI 算力。10-30 的 [Geekbench 成绩](https://www.gsmarena.com/the_new_oled_ipad_mini_runs_geekbench_here_are_the_results-news-75276.php)（第三方跑分）显示：5 核版单核 3879、多核 9870，内存 12GB（Xcode 读数，规格页未写）。开发者规划端侧模型的延迟和功耗时，应该按单 16 核这一档来算。NPU TOPS 和绝对带宽官方都没有公布，所以 iPad mini 的 decode 上限暂时无法推算。

### Siri AI 的分层部署：家居入口、国行混合与云端用量上限

10-13 的家居发布把 Siri AI 推到常开设备上：[HomeView](https://www.apple.com/newsroom/2026/10/meet-apple-homeview-a-new-way-to-enjoy-entertainment-and-manage-the-home/) 用 A18，[Apple TV 4K](https://www.apple.com/newsroom/2026/10/apple-unveils-the-new-apple-tv-4k/) 用 A19（官方称 CPU 最多快 50%、GPU 最多 2 倍），[HomePod mini 2](https://www.apple.com/newsroom/2026/10/apple-announces-the-next-generation-of-homepod-mini/) 用手表级 S10。芯片分配与 10-11 的[爆料](https://9to5mac.com/2026/10/11/apple-homeview-home-hub-four-colors-november/)一致。官方写法统一为：请求“可在设备端处理，也可走 Private Cloud Compute”，摄像头和麦克风数据在 Secure Exclaves 中隔离，个人上下文依赖户主那台 12GB 内存的 iPhone/iPad。内存、Neural Engine 规格和本地/云端分流比例都没有披露。从兼容范围也能看出一些信息：Siri AI 向下支持第 2 代 Apple TV 4K，但[第一代 HomePod mini 被排除](https://www.macrumors.com/2026/10/14/apple-home-devices-siri-ai/)。主体推理并不依赖本机 NE，但最小的设备仍然有硬件门槛。

10-31 Apple 中国官网发布[国行 Apple 智能定档](https://www.apple.com.cn/newsroom/2026/10/apple-intelligence-features-are-coming-to-users-in-china/)：11-04 进入开发者测试版，12 月随 iOS 27.3 正式上线，首批只支持 iPhone。[官网机型表](https://www.apple.com.cn/apple-intelligence/)中最低的芯片是 A17 Pro。功能基于 Apple 自研生成式模型，Siri、写作工具和视觉智能可以接入千问；WWDC 2026 的 Siri AI 这次不在范围内。新闻稿没有提 PCC，也没有说明哪些请求在本机完成。

11-02 的 Apple 第四财季财报（[MacRumors 整理](https://macrumors.com/2026/11/02/apple-4q-2026-earnings)，官方财报口径）补上了“云那一层”的账。Siri AI 的服务器端推理成本计入服务成本，部分硬件收入会在设备生命周期内递延；Siri AI 等服务器端功能会设用量上限，以后可付费扩容；端侧与云端的使用比例 Apple 不披露，称“还很早期”。同一份财报里，Mac 营收 108 亿美元、同比增 24%，CFO 称内存价格“前所未有”，预计 12 月季度 Mac 和 iPad 供货主要受内存约束，涨价会持续到下一季度以后。也就是说，Apple 一边在宣传 128GB“本机跑数千亿参数”，一边承认内存正是供货瓶颈。把能在本地做的请求留在本地，现在也是 Apple 控制云端成本的手段。

### Google 端侧推理栈：一个月走完“引擎 → 建模 → 系统下发”

Google 本月的软件动作前后衔接得很紧。10-08 开源的 [ML Drift](https://developers.googleblog.com/ml-drift-next-gen-gpu-aiml-inference-at-the-edge/) 是一套四后端 GPU 引擎（OpenCL/Metal/WebGPU/OpenGL ES）。官方口径：Gemma 基准下内存开销比其他框架最多低 12%，YouTube Shorts 帧延迟最多降 40%，Chrome 中的 Gemini Nano 已在上面量产。LLM 的 tok/s 只出现在图表里，正文没有给数值。10-19 的 [LiteRT Tensor API](https://developers.googleblog.com/native-model-authoring-for-edge-with-litert-tensor-api/) 允许用 C++ 逐算子建图，内置 SDPA、RMSNorm、KV cache 更新等 LLM 复合算子，权重可以直接从 safetensors 加载。官方示例 SAM 2.1 在 MacBook Pro Metal 上比 MLX 快约 1.5 倍，WebGPU 版经 agent 自动优化后从不到 10 FPS 提到 30 FPS 以上。10-28 的 [Play 服务版 LiteRT](https://developers.googleblog.com/smaller-apps-and-faster-gpu-inference-with-litert-in-google-play-services/) 换上 ML Drift，官方称 GPU 推理约为旧 delegate 的 1.4 倍，应用约小 8MB，每天超过一万亿次推理；旧 GPU delegate 弃用，NNAPI 从 2027 年开始移除，而 Play 服务版的 NPU 支持“开发中”。10-30 的 [LiteRT-LM v0.19.0](https://github.com/google-ai-edge/LiteRT-LM/releases/tag/v0.19.0) 把约束解码的 logit masking 放到 GPU 上并兼容 MTP，新增 Qwen3-ASR、Kokoro、Qwen3-TTS，C API 升到 1.0.0。

外围工具也在补齐。10-20 Google AI Edge 与 Arm 发文，介绍用 [Model Explorer 可视化 Ethos-U85 的 NPU 委托](https://developers.googleblog.com/bringing-visual-graph-debugging-to-custom-edge-compilers-with-model-explorer/)，可以直接看出哪些算子没被委托、哪个节点最耗周期，但性能数据来自 FVP 模拟器，没有真机加速比。社区方面，litert-community 上传的 [Qwen3.8-27B 混合 INT4](https://huggingface.co/litert-community/Qwen3.8-27B) 在 M4 Max GPU 上 decode 18.2 tok/s（第三方实测，仅作参考），说明 LiteRT-LM 已能承载 27B 级模型，但只在桌面级机器上跑得动。学术侧的 [OPTIC](https://arxiv.org/abs/2610.31309)（10-22，arXiv）把 Gemma 4 E4B 的逐层嵌入（PLE，占 35.2% 参数）压缩约 100 倍，仍保留 97.8% 性能，常驻存储从 5.64GB 降到 56.4MB（论文实测，RTX 4090）。PLE 正是 Gemma/Nano 端侧模型节省 DRAM 的关键设计，这类工作对手机内存有直接意义。

整体看，Google 的打法是把运行时从“每个应用自带”变成“系统统一下发”，并主动对标 Apple 平台：Metal 是一等后端，基准直接拿 MLX 比。GPU 路径已经统一，NPU 路径仍是最明显的缺口。

### Android 端侧智能体与 XR：接口成形，设备门槛很高

10-28 的 [Android Dev Summit 主文](https://developer.android.com/blog/posts/build-it-your-way-a-next-era-of-android-development)是本月 Google 方向对端侧智能体最重要的一条。ML Kit Agentic API（alpha）中的 AgentRunner 在 AICore 内完成“观察-推理-调用工具-评估”循环，按[官方文档](https://developers.google.com/ml-kit/genai/agent/android)，规划完全在设备上进行，提示数据不出设备；maxTurns 默认 10，用来限制失控循环和耗电。同批发布的还有端侧 Embeddings、语音翻译、21 种语言 TTS（alpha），Prompt API 的 Function Calling 预览，以及进入 beta 的 AppFunctions。至此，记忆、工具、语音输入输出都有了官方端侧接口。代价也很明显：ML Kit 文档单列的最新一代设备只有 Pixel 11 全系和三星 Z Flip8/Fold8/Fold8 Ultra 共 7 款（媒体称即 Nano 4 设备），Nano 4 的参数量和 tok/s 官方没有公布。媒体称 Nano 4 基于 Gemma 4 E2B/E4B，这一点本月没有一手页面可以核实。

同一篇文章还宣布了 Android XR 首款光学透视眼镜 XREAL AURA，Jetpack XR 核心库转为稳定版。据 [Road to VR](https://roadtovr.com/?p=233285)（媒体口径），AURA 采用分体架构，计算盒是 Snapdragon Reality Elite（最高 48 TOPS，12/16GB），眼镜重量不到 95 克，售价 1099/1299 美元，11 月中旬发货；AURA 上的 Gemini 有多少在端侧运行，官方没有说明。PC 方面，Counterpoint [访谈](https://counterpointresearch.com/en/insights/counterpoint-conversations-snapdragon-x-series-ai-pcs-agentic-ai-googlebook-linux)称 Googlebook 用的是第一代骁龙 X Elite，分析师归因于多年的工程周期。Google 的端侧智能体目前仍主要落在旗舰手机上，眼镜和笔记本更多是端云混合的入口。

### 最底层：Coral NPU 从开源设计走到商用芯片

10-14 Google Research 年度展示会先由媒体转述了“二代边缘芯片省电 40%”（[首尔经济](https://en.sedaily.com/international/2026/10/15/google-unveils-edge-ai-chip-using-40-percent-less-power-for)，二手口径），10-20 的[官方稿](https://developers.googleblog.com/unifying-edge-ai-how-coral-npus-open-standard-brings-portable-energy-viable-intelligence-from-model-to-silicon/)给出了完整信息。Coral NPU 32 位架构四个里程碑全部完成：M4 矩阵单元基于 RISC-V VME，外积引擎每周期 256 MAC，可配置到最高 1 TOPS，推理平均功耗目标 10 mW；RTL 开源，基于 IREE/MLIR 的 Coral Compiler v1.0 同步发布，芯原负责设计实现与验证。Synaptics 同日发布 [Astra SR200](https://www.synaptics.com/company/news/synaptics-astra-sr200-series-multimodal-edge-ai-processors)（厂商口径）：200/300/400 GOPS 三档，Cortex-M85 + M52，最多 8MB SRAM，另配可扩到数百 MB 的封装内定制 DRAM。

两处数字需要标口径。第一，256 MAC/周期等于每周期 512 次运算，达到 1 TOPS 约需 2 GHz，MCU 级频率达不到，所以“1 TOPS”和“10 mW”不一定是同一配置（推算）。第二，月中二手转述的“平均功耗低于 6 mW”“M3 可跑 Gemma 3 270M”，在官方稿中都没有出现，官方只说可以跑“Gemma 一类紧凑 Transformer”。按 4-bit 计，270M 级权重约 135MB，放不进 8MB SRAM，必须放到定制 DRAM，而 DRAM 带宽未披露，无法估算 decode 速度。Coral 的价值不在峰值：它是目前少见的同时具备开源 RTL、开源编译器和商用芯片的端侧 NPU，在 Google 的端云级联里负责毫瓦级常开感知。

### 判断与 11 月观察

本月 Apple 和 Google 走的是两条路线。Apple 靠统一内存的容量（最高 512GB/128GB）和多机互连，把“本机跑大模型、跑编码智能体”放在 Mac 上卖，手机和家居设备则按“本机 + 户主手机 + PCC”分层；财报显示，云端推理成本和内存涨价正在反过来推动这种分层。Google 则把智能体循环放进系统服务（AICore + ML Kit），把推理运行时放进 Play 服务，覆盖面和接口完整度领先，但能运行 Nano 4 的设备只有 7 款，NPU 路径也还没有统一。两家的共同瓶颈都是内存：M6 带宽只提升约 10%，iPad mini 用 NPU 档位区分 SKU，Apple 预计 12 月季度 Mac/iPad 供货受内存约束，PLE 压缩这类研究的价值也在节省 DRAM。

11 月要看的几件事：(1) M6 MacBook Pro/iMac 与 M5 Max PROLED 机型 11-06 发货后的第三方 MLX/llama.cpp tok/s，尤其是 M6 的 decode 是否真的只比 M5 快约 10%；(2) 11-04 国行 iOS 27.3 测试版中，Apple 自研模型与千问的本机/云端分流实测；(3) Gemini Nano 4 是否公布参数量和能效，以及 Play 服务版 LiteRT 何时支持 NPU、NNAPI 退场后各家 SoC 如何接入；(4) HomeView、Apple TV 4K 11-13 上市后的拆解（内存与 NE 规格）；(5) Synaptics SR200 的 DRAM 带宽和小模型实测。

## 3. 其他 SoC 与 PC：内存成为端侧硬约束

### 本月结论：算力在加，内存在抢，出货在缩

10-08~11-02 这一个月，“其他 SoC、PC 与产业”方向没有出现新一代旗舰手机 SoC。9 月三款 2nm 旗舰（苹果 A20、天玑 9600 Pro、骁龙 8 Elite Gen 6）发布后，本月进入落地和财报阶段，主线可以归纳为三条。

第一，PC 端出现了真正“为本地大模型设计”的整机。NVIDIA RTX Spark 笔记本从 10-07 开订，10-15 评测解禁，10-16 全球开售，10-28 补上了智能体资源调度。AMD 锐龙 AI Halo 把内存加到 192GB。IDC 给“智能体电脑”定了 32GB 内存、135GB/s 带宽的门槛。PC 的评价标准已经从 NPU TOPS 转向统一内存容量、带宽，以及 MoE 模型和智能体软件栈。

第二，产业端，AI 数据中心正在吸走内存和先进产能。三星 Q3 营业利润 107.4 万亿韩元，SK 海力士营业利润率 80%，韩国 10 月芯片出口同比增长 259%（均为官方口径）。同一时期，IDC 统计 Q3 全球手机出货同比降 22%，PC 出货同比降 20.1%；Counterpoint 统计手机 SoC 出货同比降 21%。

第三，芯片厂的增长重心在偏离手机。联发科手机业务同比降 17%，智能边缘平台同比增 63%，AI ASIC 收入 Q4 单季目标 25 亿美元。英特尔的增长几乎全部来自数据中心和代工。

合起来看，端侧 AI 硬件在高端继续加速，普及却被内存成本卡住。

### 一、PC：大统一内存平台从发布走到在售

**RTX Spark 的完整一个月。** 10-07 微软 Surface 与 NVIDIA 开订 RTX Spark 笔记本，起价 2599 美元。10-16 NVIDIA [宣布全球开售](https://nvidianews.nvidia.com/news/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs)，首批 9 款机型，覆盖华硕、戴尔、惠普、联想、微软、微星（官方口径）。芯片是单片 Blackwell RTX GPU 加 Grace CPU，CPU 与联发科合作设计；统一内存最高 128GB，FP4 算力最高 1 PFLOPS（官方口径）。

10-15 评测解禁后，[Windows Central](https://www.windowscentral.com/hardware/nvidia/rtx-spark-review-benchmarks-2026) 用 Procyon 测得 Llama 3.1 8B 为 49.44 tok/s（首 token 0.40 秒），Llama 2 13B 为 27.44 tok/s；CPU 单核 Cinebench 2026 为 558 分，低于骁龙 X2 Elite Extreme 的 662 分（媒体实测）。[HotHardware](https://hothardware.com/reviews/nvidia-rtx-spark-platform-review) 测得整机峰值约 138W，按续航计的能效排在末段（媒体实测）。按媒体报道的约 300GB/s 带宽推算，8B INT4 的 decode 上限约 66 tok/s，实测达到上限的约 75%，说明这颗芯片主要受带宽限制（推算）。

10-21 GTC 柏林上，NVIDIA 把本地 AI 硬件整理成三层（[官方博文](https://blogs.nvidia.com/blog/local-ai-gtc-rtx-dgx-spark-station-sync/)）：RTX Spark 笔记本给个人；DGX Spark 新增 64GB 版，10-23 开售，NVIDIA Sync 支持最多 8 台组成集群、合计 1TB 统一内存；DGX Station 有 748GB 一致性内存（均为官方口径）。配套模型几乎全是“大总参、小激活”：Nemotron 3.5 Bolt 74B-A9B（24GB 包体）、Recursive Flint 40B-A2.5B（AI 生成的内核在 RTX Spark 上提速 55%），以及最低 4GB 内存的 Nemotron Bolt E4B。10-28 的 [RTX AI Garage](https://blogs.nvidia.com/blog/local-ai-rtx-spark-laptops-updates-models-agents-games/) 确认六家 OEM 在售、128GB 版已到货，并在 NVIDIA App 加入“前台应用 vs 后台智能体”的 GPU 分配开关。这是 PC 厂商第一次把常驻智能体和前台应用争抢算力的问题，做成用户可见的系统设置。

推算口径下的结论是：稠密 70B 的 4-bit 模型在约 300GB/s 带宽下 decode 上限只有约 8 tok/s，稠密 120B 约 5 tok/s；74B-A9B 每 token 只读约 4.5GB，上限约 60–65 tok/s。“可跑 120B”只说明内存装得下，实际可用的是 MoE（推算）。

**AMD 与 x86 阵营。** 10-12 AMD 发布新一代[锐龙 AI Halo 开发者平台](https://www.ithome.com/1/012/104.htm)，基于锐龙 AI Max+ PRO 495，最高 192GB LPDDR5X-8533，其中 160GB 可作共享显存；Linux 版 7299.99 美元，初代 128GB 版起价 3999 美元（官方口径）。厂商称可本地运行 300B 以上模型。按 256-bit LPDDR5X-8533 约 273GB/s 推算，4-bit 稠密 70B 的 decode 上限约 7 tok/s，这条路线同样要靠 MoE。

10-20，AMD 与英特尔[宣布合并 PyTorch 的 x86 CPU 优化](https://newsroom.amd.com/news/amd-intel-collaborate-simplify-ai-development-on-x86-cpus-pytorch/)：ZenDNN 并入 oneDNN，oneDNN 成为 PyTorch 在 x86 上的默认加速库，双方还合作新的矩阵指令集 ACE（官方口径，未给时间表和性能数字）。同期 IIIT Hyderabad 与 AMD 在 PACT 2026 发表 [AIEHalide](https://pact2026.github.io/program/papers/pact26-final56.pdf)，用 Halide 直接编译到 XDNA 2 NPU，int8 GEMM 达 25.46 TOPS，为峰值的 62%（论文实测）。

**低价路线的第三方证据。** [PC Watch](https://pc.watch.impress.co.jp/docs/column/ubuntu/2150896.html) 10-26 在 12GB 显存的 Intel Arc B580 加 64GB DDR5 的普通台式机上，用针对 Intel GPU 优化的 XeStrata 跑 Qwen3.8-Flash-Next（IQ3_S、64K 上下文），得到 31.1 tok/s；原版 Strata 只有 10.9 tok/s（第三方实测）。社区项目[解除 RTX 20–40 张量核半速限制](https://videocardz.com/newz/modders-unlock-hidden-ai-performance-on-nvidia-rtx-20-30-and-40-series-gpus-with-up-to-2x-tensor-throughput)，RTX 4090 FP16 张量峰值从 165.6 提到 331.6 TFLOPS，但 LLM 只有预填充提速 14–36%，生成速度基本不变（社区实测，有损坏硬件的风险）。两件事指向同一个结论：消费级 PC 跑大模型，瓶颈在内存和专家调度，不在峰值算力。

**门槛与爆料。** [IDC](https://www.ithome.com/1/015/221.htm) 预测中国智能体电脑出货将从 2026 年 77 万台增至 2030 年 2080 万台，门槛是 32GB 内存加 135GB/s 带宽，高阶负载要 64GB 加 250GB/s，并以 30B 级模型为参考。按 135GB/s 推算，30B 稠密 4-bit 的 decode 上限约 9 tok/s，激活约 3B 的 MoE 约 90 tok/s，所以这个门槛实际上默认了 MoE 路线（推算）。后续产品只有爆料：DigiTimes 称入门级 12 英寸 Surface 在重新评估处理器，传闻中的 AMD Arm 芯片 Sound Wave 为 3nm、5–10W、6 核（[IT之家](https://www.ithome.com/1/015/311.htm)，爆料）；英特尔 Nova Lake-HX 旗舰据称 28 核，计算模块用台积电 N2P（[IT之家](https://www.ithome.com/1/015/986.htm)，爆料）。两条爆料都没有 NPU 规格。

### 二、手机 SoC：新品空窗期，竞争转向工艺和持续性能

**华为麒麟。** 10-13 华为开了时隔六年的[麒麟技术沟通会](https://www.ithome.com/1/012/327.htm)。据[第一财经](https://finance.sina.com.cn/roll/2026-10-13/doc-inivafqm8091935.shtml)转述的官方数字，麒麟 9050 系列是首款量产的“逻辑折叠”芯片，晶体管密度提升 53.5%；9050 Pro 的 CPU 大核能效提升 41%，NPU 算力提升 140%；混合键合间距 1.5μm，2027 年计划缩到 1μm（媒体转述官方）。网传的“逻辑在上、SRAM 在下、层间带宽约 125TB/s”只来自博主解读，官方没有给。

随后，10-23 华为开订 Pura 90 Plus，展机确认首发麒麟 9025（[IT之家](https://www.ithome.com/1/016/862.htm)）；10-28 [正式发布](https://www.gizchina.com/huawei/huawei-pura-90-plus-launches-with-kirin-9025-and-5700mah-battery)，官方称整体性能提升 19%（HuaweiCentral 写作“最高 +20%”），12GB 内存起步，售价 5499 元起。博主爆料称 9025 是 9020 提频到 2.6GHz 的版本。工艺和 NPU 规格至今未披露，华为也没有公布任何端侧模型规模或 tok/s。“不靠制程靠堆叠”是本月手机 SoC 唯一新的技术路线信号，但它对端侧大模型的实际收益还无法量化。

**三星 Exynos 2700 与 S27 Ultra 换芯的拉锯。** 这是本月消息反转最多的事件，三条都是爆料：
- 10-16，首尔经济日报称第六代骁龙 8 超级至尊版在长时间重负载下超出三星的温度上限，S27 Ultra 可能改用 SF2P 2nm 的 Exynos 2700（[Droid Life 转述](https://www.droid-life.com/2026/10/16/galaxy-s27-ultra-samsung-considers-switch-to-exynos/)）。
- 10-25，[朝鲜日报](https://biz.chosun.com/it-science/ict/2026/10/25/LYNO7ACPWRECDA5UDZRHHMLA6E/)称 Exynos 2700 内部测试 Geekbench 6.5 多核约 13000 分，比骁龙 8 Elite Extreme Gen 6 的约 11000 分高约 20%。
- 10-30，IceUniverse 又称欧洲版 S27 Ultra 看不到 Exynos 迹象，可能继续全系骁龙（[Sammy Fans 转述](https://www.sammyfans.com/2026/10/30/samsung-galaxy-s27-ultra-could-remain-snapdragon-exclusive/)）；高通也否认过热（[Android Authority](https://www.androidauthority.com/qualcomm-deny-snapdragon-8-elite-gen-6-heating-issues-3724807/)）。

三星 10-29 的[正式财报](https://news.samsung.com/global/samsung-electronics-announces-third-quarter-2026-results)只确认了三点：System LSI 的 Q3 增长来自下半年新机型 SoC 和图像传感器；2027 年要扩大旗舰 SoC 销售；代工 Q4 的驱动力之一是“4nm NPU 量产爬坡”，客户未披露。Exynos 2700 的 NPU 规格、功耗和能效至今没有任何来源。不论换芯结果如何，这场争论说明，长时间负载下的温度墙已经成为旗舰 SoC 的选型指标。对需要长时间 decode 的端侧智能体来说，持续性能比峰值跑分更重要。

**联发科、小米、瑞芯微、紫光展锐。** 本月联发科没有发布新的手机 SoC。天玑 9600 Pro 在 10-13 吉隆坡 Tech Day 上由 vivo 确认用于 X500 系列（检索摘要所见的单一二手媒体来源，待核实）。小米玄戒 O3 已在 8 月的沟通会发布，窗口内没有新动作。瑞芯微 10-15 发布前三季度[业绩预告](https://www.cnfin.com/yw-lb/detail/20261015/4481392_1.html)：营收约 44.47 亿元，同比增 41.56%，净利润 13.1–13.5 亿元；Q3 因 PCB 物料短缺，部分订单延后；RK182X 端侧大模型协处理器 Q4 放量，RK3668 即将投产，RK3688 随后（公司口径，经新华财经报道）。这是本方向少有的增长样本，增长来自机器人、车载和机器视觉等 AIoT 端侧，不来自手机。紫光展锐窗口内没有新芯片发布，只出现在下文 Counterpoint 的“承压”名单里。

### 三、联发科：营收创新高，但增长不在手机

联发科这个月的三条消息合起来，是本月最清楚的“重心迁移”样本。
- 10-08 月营收公布后，媒体加总的 Q3 营收为 1680.57 亿新台币，同比增长 18.27%，高于指引上限（[媒体报道](https://www.smbom.com/news/54336)）。
- 10-15 彭博报道[字节跳动洽购联发科数据中心 ASIC](https://www.bloomberg.com/news/articles/2026-10-15/bytedance-in-talks-to-secure-mediatek-ai-chips-for-data-centers)，两家公司都未确认。
- 10-30 [Q3 法说会](https://www.ithome.com/1/020/400.htm)公布：毛利率 46.3%，Q4 营收指引 2101–2218 亿新台币，环比增长 25%–32%。首款 AI 加速器 ASIC 9 月起出货，CEO 蔡力行称有信心实现 **Q4 单季** 25 亿美元的相关营收（此前指引为“略高于 20 亿美元”）；2027 年冲击约 160 亿美元区间的上限，约占 AI ASIC 市场的 20%；第二家 ASIC 客户已确认，不是中国公司，2028 年量产（均为公司口径，经 IT之家、[BigGo](https://finance.biggo.com/news/TW_2454.TW_2026-10-30) 转述）。

分部数据：手机占营收 37%，同比下降 17%；智能边缘平台占 58%，同比增长 63%，来自 5G 数据机、AI 平板、AI PC、车载等新项目；首款 2nm 天玑 9600 Pro 带动的旗舰段好于手机整体（BigGo 转述）。

另外两处可以看到联发科在端侧的延伸。一是为 RTX Spark 合作设计 CPU。二是 3nm 工业 SoC Genio Pro 5100 被广州 Harvest Praxis 用作机器人“大小脑合一”平台（[新闻稿](https://www.digitaljournal.com/pr/news/newsfile/dual-brains-one-chip-harvest-1493004329.html)），计划 2027 年 1 月量产。新闻稿写 NPU 106 TOPS，联发科[产品页](https://www.mediatek.com/products/iot/genio-iot/genio-pro-5100)写的是 50+ TOPS，口径不一致，需要厂商澄清。

### 四、代工与内存：数据中心吸走产能

**台积电。** 10-08 公布 9 月营收 5118.6 亿新台币，同比增长 54.6%（[官方](https://pr.tsmc.com/english/news/3343)）。10-15 公布 [Q3 财报](https://pr.tsmc.com/english/news/3346)：营收 466.7 亿美元，高于 446–458 亿美元的指引；毛利率 66.4%；2nm 占晶圆收入的比例从上季度的 3% 升到 8%；Q4 指引 523–543 亿美元，CFO 称由 2nm 陡峭爬坡支撑（官方口径）。媒体转述的平台结构是 HPC 占 68%，智能手机从去年同期的 30% 降到 21%，魏哲家提醒消费类市场受零部件涨价影响。Apple 10-20 [宣布](https://www.apple.com/newsroom/2026/10/apple-announces-american-manufacturing-program-partners-for-latest-iphone-lineup/)台积电亚利桑那厂 2026 年为其生产超过 1 亿颗芯片（官方口径，未说明节点）。

**三星与 SK 海力士。** 三星 10-08 [初步业绩](https://news.samsungsemiconductor.com/global/?p=4050)的营业利润约 107.4 万亿韩元，10-29 正式财报确认营收 195.3 万亿韩元，其中 DS 部门营业利润 106.5 万亿韩元，手机与网络部门亏损 0.6 万亿韩元（官方口径）。三星还首次把 QLC SSD 需求和“个人 AI 智能体服务”的扩张联系起来。[SK 海力士 Q3](https://news.skhynix.com/en/q3-2026-business-results-1/) 营收 104.6 万亿韩元，营业利润 83.3 万亿韩元，利润率 80%；14 家大客户的长约覆盖 2027–2028 年过半产能；公司预计供不应求持续到 2030 年，并计划扩大 AI 服务器用 LPDDR5 SOCAMM 的销售（官方口径）。这意味着手机用的 LPDDR 产能也在被服务器分走。11-01 韩国产业通商资源部公布 10 月半导体出口 564 亿美元，同比增长 259%（官方初步数据，[韩联社经 Korea Times](https://www.koreatimes.co.kr/economy/20261101/koreas-monthly-exports-hit-1153-bil-in-oct-on-record-chip-sales)）。

**价格与路线图。** TrendForce 新闻栏目汇总韩台媒体与机构的观点，Q4 DRAM 合约价预计环比再涨约 20%，低于 Q2 的约 80% 和 Q3 的约 40%（[TrendForce News](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand-tight-supply-support-outlook/)；这是转引，不是 TrendForce 自己的预测）。美光 10-21 的[技术路线图](https://s25.q4cdn.com/621799436/files/doc_downloads/2026/10/MU-TP-Webinar.pdf)给出两项目标：LPDDR6 功耗比 LPDDR5 改善 35% 以上；面向边缘推理的 vEIM 首代规格为 2TB/s、每比特能耗低于 1pJ。按满带宽算，vEIM 接口功耗约 16W，更可能先用在机器人、车载和 AI PC，进不了手机（推算）。

长鑫 10-30 业绩交流会披露，4F² 第六代平台已完成工程样片验证（[IT之家](https://www.ithome.com/1/020/599.htm)）；11-01 又披露上半年 LPDDR 收入占营收 52.02%，LPDDR6 在第五代平台上规划（[IT之家](https://www.ithome.com/1/020/832.htm)，媒体转述公司）。工艺侧，三星代工提交 IEDM 的 [8LPU+](https://www.ithome.com/1/015/638.htm) 不用 EUV，性能提升 12%、功耗降低 15%，并用 ULL-SRAM 降低待机漏电，面向边缘 AI 和车载（论文摘要口径）。英特尔 10-29 [Q3 财报](https://www.intc.com/news-events/press-releases/detail/1786/intel-reports-third-quarter-2026-financial-results)：营收 165 亿美元，同比增长 21%；但客户端与物理 AI 事业部同比下降 5%，数据中心增长 78%，代工增长 58%。CFO 称 PC 放缓至少持续到 2027 年上半年；以色列 Fab 28 停产约两周（官方口径及 [IT之家](https://www.ithome.com/1/020/385.htm) 转述的电话会内容）。

**“内存该给谁”被公开说出来。** Sam Altman 在播客里说，PC 里的 DRAM 只有约 5% 的时间在用，内存紧缺时放在云端才能做到最高利用率，“相当糟糕”（[Notebookcheck 转引](https://www.notebookcheck.net/Quite-terrible-Sam-Altman-says-PCs-waste-the-world-s-limited-DRAM-supply.1438393.0.html)，原话未逐字核对）；10-31 他在龙仁会见三星高管。终端侧的直接结果当月就能看到：11-02 [树莓派](https://www.raspberrypi.com/news/price-rises-for-some-16gb-raspberry-pi-products/)把 Pi 5 16GB 上调 80 美元至 385 美元，原因是 16GB DRAM 缺少替代货源（官方口径）。

### 五、需求侧：手机和 PC 出货一起创下纪录跌幅

- **PC。** IDC 10-08 统计 Q3 全球 PC 出货 [6270 万台](https://www.idc.com/?p=121750)，同比降 20.1%；Counterpoint 10-21 统计为 [5700 万台](https://www.counterpointresearch.com/en/insights/global-pc-shipments-plunge-21-percent-in-q3-2026)，同比降 21%，并预计 Q4 再降 27%。两家口径不同，绝对值相差约 570 万台，方向一致。Apple 和华硕跌幅最小。
- **手机。** IDC 10-14 统计 Q3 手机出货 [2.553 亿部](https://www.idc.com/resource-center/press-releases/smartphone-shipments-decline-3q26/)，同比降 22%，是有记录以来最大的单季跌幅；手机内存成本比去年上涨约 350%，复苏最早要到 2028 年。Counterpoint 10-30 统计 Q3 手机 [SoC 出货](https://www.counterpointresearch.com/en/insights/smartphone-oems-shift-focus-to-profitability-as-soc-shipments-fall-21-percent-yoy)同比降 21%，全年预计降 20%、2027 年再降 3%–4%；手机内存价格 Q3 环比又涨 5%–10%，部分入门机开始用回收内存。苹果和三星相对稳定，紫光展锐、联发科、高通承压。
- **成本结构。** TrendForce 10-08 称，CPU、DRAM 和 SSD 已占一台 900 美元主流笔电 BOM 的约 68%，品牌可能减少内存容量来控制成本（[TrendForce](https://www.trendforce.com/presscenter/news/20261008-13264.html)）；10-29 又称主要笔记本 ODM 预计 Q4 订单同比降 10%–15%（[TrendForce](https://www.trendforce.com/presscenter/news/20261029-13284.html)）。

这和第一节构成直接矛盾：IDC 要求智能体电脑至少 32GB 内存，TrendForce 却预计品牌会“减内存保价格”。短期内，大内存端侧 AI 设备只会集中在 2000 美元以上的高端机型。

### 六、IP、授权与规则

- **Arm 与高通诉讼。** 10-13，特拉华州陪审团认定 Arm 违反与高通的架构授权协议，但只判 2 美元名义赔偿（[Arm 声明](https://newsroom.arm.com/news/arm-qualcomm-legal-dispute)）。真正影响骁龙手机和 PC 芯片成本的，是法官后续对“五年免付授权费”和下一代授权善意谈判的裁决，本月还没有结果。
- **Arm 的眼镜判断。** Arm 10-30 在[可穿戴博客](https://newsroom.arm.com/blog/ai-wearables-smart-glasses-arm)中估计约 99% 的智能眼镜基于 Arm，提出“眼镜感知、手机或云推理”的分层架构（官方估计）。
- **NPU IP 与国产边端芯片。** Ceva 10-28 发布[新一代 NeuPro](https://www.ceva-ip.com/press/ceva-unveils-next-generation-neupro-npu-portfolio-and-announces-expansion-into-ai-infrastructure/)，从常开的 Nano 到数据中心的 Ultra 共用一套架构，官方称单位面积吞吐最高提升 2 倍，支持 FP4、分页 KV 缓存和 MoE，2027 年 Q2 正式供货。爱芯元智 10-13 发布 [AX8860](https://finance.sina.com.cn/tech/digi/2026-10-13/doc-inivasef8111871.shtml)：6nm、256 TOPS、最高 128GB LPDDR5X、273GB/s。厂商称 Qwen 27B 的 decode 比 DGX Spark 快约 30%，但两者带宽同级，按 FP4 推算 decode 上限都只有约 20 tok/s，需要第三方实测确认。
- **算力口径。** 地平线余凯 10-30 [公开批评](https://www.ithome.com/1/020/358.htm)“等效算力”虚标到稠密算力的 6–7 倍，征程 6P 按 NV 口径为 560 TOPS，按等效口径为 1960 TOPS。这对比较手机和 PC 的 NPU 同样适用：先换算到稠密 INT8 口径，再结合带宽看。
- **监管。** 美国 FCC 10-22 首次按芯片级规则[禁售两款含海思 AI 视觉 SoC 的设备](https://www.tomshardware.com/tech-industry/cyber-security/fcc-bans-first-two-devices-from-the-us-under-new-chip-level-rule-huawei-subsidiary-chip-boasts-face-detection-algorithm)。从此端侧 AI 芯片的原产地会直接影响整机能否出海。
- **机器人算力。** Counterpoint 预测人形机器人 AI 加速器累计出货 2030 年超过 100 万颗，2026–2030 年复合增速 144%，NVIDIA 领先，高通、英特尔拿到设计订单（[Counterpoint](https://www.counterpointresearch.com/en/insights/nvidia-leads-humanoid-robot-ai-accelerator-market)，第三方预测）。

### 判断与下月观察

本月的变化可以概括为一句话：端侧 AI 硬件的约束从“算力够不够”变成了“内存给不给”。证据有三层：PC 新平台的卖点是 128–192GB 统一内存；手机 SoC 的竞争点是工艺堆叠和温度墙；产业数据则显示 DRAM 和先进产能正在优先流向数据中心。

由此做三个判断：
1. 本地智能体会先在 2000 美元以上的大内存 PC 和 2nm 旗舰手机上普及，中低端设备的内存配置 2027 年可能停滞甚至倒退。
2. 在 135–300GB/s 带宽的设备上，大总参、小激活的 MoE 加 4-bit 以下量化是唯一可用的大模型形态，“可跑 xxxB”这类容量宣传应一律换算成激活参数和 decode 上限来看。
3. 联发科、英特尔、三星的增长都来自数据中心，端侧 SoC 的研发投入未来可能更多复用数据中心 IP（如联发科的 CPU 合作、三星的 4nm NPU 代工），而不是单独为手机投入。

11 月需要关注的事件：
- 高通、AMD、Arm 预计 11 月上旬的财报，看它们对 AI PC 和手机端侧需求的判断；
- Arm 与高通案的法官裁决；
- S27 Ultra 最终用哪颗芯片，以及 Exynos 2700 的 NPU 规格；
- 麒麟 9025 的第三方拆解与工艺判断；
- 瑞芯微新一代协处理器是否如期发布；
- RTX Spark 的续航与长时间负载散热实测（10 月解禁时没有这部分数据）；
- 三星 8LPU+ 在 12 月 IEDM 的正式报告。

## 4. 低功耗与内存：生成式下沉，瓶颈转向内存

### 本月结论：常开芯片开始写“生成式”，端侧大模型的瓶颈转到内存

10-08 到 11-02 这段时间，低功耗与内存方向没有出现手机级的新大芯片，但有三条变化贯穿全月。**第一，常开级芯片开始把生成式模型写进规格。** BrainChip Sequora 标称最高支持 3B 参数，Google 的 Coral NPU 32 位架构完工并装进 Synaptics 的 MCU，Ceva 新一代 NeuPro 从常开的 Nano 档起就支持分页 KV 缓存和 MoE。不过这些产品都还没有功耗或 tok/s 实测。**第二，存内计算从论文走到流片和融资。** 后摩、九天睿芯、亿铸、微纳核芯四家国产存算公司在一个月里集中公布路线或融资，TetraMem 的 12nm RRAM 存算 SoC 完成流片。四家押的方向相同，都是靠近存堆叠缓解解码阶段的带宽问题。**第三，端侧大模型的约束从算力转到内存的容量、带宽和价格。** 存储厂把 HBF、CXL 和“边缘推理内存”写进路线图；与此同时 DRAM 合约价继续上涨，手机 SoC 出货同比下降 21%，树莓派 16GB 版涨价 80 美元，LPDDR6 能否进入 2027 年旗舰手机也还没有定论。

### 一、MCU 与常开 NPU：Coral 开放标准落地，生成式模型进入毫瓦级规格

本月最完整的一条线是 Google 与 Synaptics 合作的芯片。10-14，Google Research 在研究展示活动上预告了新一代 Astra，[韩媒报道](https://en.sedaily.com/international/2026/10/15/google-unveils-edge-ai-chip-using-40-percent-less-power-for)称其能耗比现有边缘 AI 产品低 40%，产品会进入 Google 自家设备。10-20 正式发布时，Google 在[开发者博客](https://developers.googleblog.com/unifying-edge-ai-how-coral-npus-open-standard-brings-portable-energy-viable-intelligence-from-model-to-silicon/)宣布 Coral NPU 的 32 位架构全部完成（官方口径）：新增的矩阵单元每周期执行 256 个 MAC，可配置到最高 1 TOPS，平均推理功耗目标 10 mW；基于 IREE/MLIR 的编译器发布 v1.0，完整 RTL 开源。同日 Synaptics 发布 [Astra SR200](https://www.synaptics.com/company/news/synaptics-astra-sr200-series-multimodal-edge-ai-processors)，SR210、SR230、SR250 的算力分别为 200、300、400 GOPS，CPU 采用 Cortex-M85 与 Cortex-M52 组合。片上 SRAM 最多 8 MB，封装内的定制 DRAM 可扩展到数百 MB，官方称这部分 DRAM 的功耗约为常规系统 DRAM 的三分之一。这两则发布要分清口径。预告阶段二手转述的“平均功耗低于 6 mW”没有出现在正式稿里。10 mW 是架构的设计目标；SR200 用的是含向量核的第二代 IP，新的矩阵单元是否已经进入 SR200，官方没有说明。另外，256 MAC 每周期要达到 1 TOPS 需要约 2 GHz（推算），MCU 的频率到不了，所以“最高 1 TOPS”应该对应更大的阵列配置。SR200 的实际意义在于内存：MCU 封装第一次有了几百 MB 的空间放权重。按 256 MB 计算，扣掉运行时后，INT4 大约能放 3 亿到 4 亿参数（推算），适合小型 Transformer、语音前端和视觉，跑不了 B 级 LLM。

BrainChip 本月连发三次。10-14 的 [Sequora Core IP](https://brainchip.com/press/brainchip-launches-sequora-edge-ai-that-doesnt-just-recognize-it-understands-and-responds/) 官方标称支持数百万到 30 亿参数的模型，架构基于 SSM，片上存储只有约 189 KB，外存接口为 512-bit AXI。SSM 没有随上下文增长的 KV 缓存，这对常开语音设备是关键优点。不过 3B 模型按 4-bit 存储也有约 1.5 GB，必须放在外部 DRAM；接 x32 LPDDR5X（约 34 GB/s）时，decode 上限约 20 tok/s（推算）。10-22 的 [AKD1500 SPI](https://brainchip.com/press/brainchip-unveils-akd1500-spi-chip-bringing-neuromorphic-ai-to-everyday-edge-devices/) 把神经形态协处理器做成 SPI 外挂件，面向不想换主控的存量 MCU 产品；按 6 月官方规格，串行模式功耗低于 200 mW。10-29 又推出了[树莓派 5 开发套件](https://brainchip.com/press/brainchip-launches-akd1500-raspberry-pi-5-kit-giving-developers-a-direct-path-from-prototype-to-production/)。三次发布分别覆盖生成、感知和开发入口，但都没有第三方能效数据。

10-28，Ceva 发布新一代 [NeuPro](https://www.ceva-ip.com/press/ceva-unveils-next-generation-neupro-npu-portfolio-and-announces-expansion-into-ai-infrastructure/)，分 Nano、Prime、Max、Ultra 四档，共用一套架构，支持 FP4/FP8、分页 KV 缓存、MoE 和线性注意力。官方只给了相对上一代的数字：单位面积吞吐最高提升 2 倍，能效提升 50%；没有公布 TOPS，2027 年 Q2 才正式供货。连 IP 厂商都把 LLM 推理特性做到最低一档，说明 NPU IP 的规格表已经默认要跑生成式负载。工艺方面，三星 10-20 披露的 [8LPU+](https://www.ithome.com/1/015/638.htm) 不使用 EUV，论文摘要口径为相比 8LPU 功耗降低 15%，并用超低漏电 SRAM 降低待机漏电。这类成熟节点会是常开芯片的主要制造平台。

学术实测方面，本月数据很多，但它们说明的是同一件事：常开任务已经能在 MCU 上跑，但功耗还要靠细节逐项省。[ESP32-P4](https://arxiv.org/abs/2610.38739) 在没有 NPU 的情况下，用 2/4-bit 混合量化实时跑通了 6570 万参数的流式语音识别：1.28 秒的音频块 0.90 秒处理完，权重从 71 MB 压到 26.65 MB，但论文没有测能耗。高通 AI Research 的[块循环 ASR](https://arxiv.org/abs/2610.37833) 把 1.089 亿参数的编码器压到 1420 万参数，仍保留 97.4% 的精度，在 M4 Pro 上每次推理的 DRAM 能耗从 32.11 mJ 降到 21.98 mJ。[SpikeDuet](https://arxiv.org/abs/2610.24677) 在 EFR32MG24 上让 CPU 和矩阵单元协同跑 SNN，能耗降低 11%–34%。[预测编码脉冲唤醒词](https://arxiv.org/abs/2610.41381)把 SRAM 读取减少 33.87%。代尔夫特的 [InstMeter](https://dl.acm.org/doi/10.1145/3795866.3796672) 按时钟周期预测 MCU 推理能耗，误差比 SOTA 低 3 倍。以上都是论文实测或仿真口径。

### 二、眼镜与家居设备：分层算力成为默认设计

本月可穿戴和家居的发布集中，硬件结构也开始趋同：设备端放一颗低功耗感知芯片，复杂推理交给手机、计算盒或云端。千问 10-13 发布 [AI 眼镜 N1 和 N1 Pro](https://www.stdaily.com/web/gdxw/2026-10/13/content_595525.html)，采用“三芯异构”平台，加一颗“行业首发”的低功耗感知芯片和自研的端侧视觉模型，用于全天候感知。芯片型号没有公开。N1 续航 9 小时，N1 Pro 为 8 小时，靠可换镜腿电池补续航。10-27 的 Rokid Glasses 2 采用恒玄 BES2800BP 加骁龙 AR 平台的双芯方案，电池 263 mAh（[凤凰网科技](https://tech.ifeng.com/c/8xZ9WGXV1uU)）；平台是 AR1 还是 AR1+，媒体说法不一。10-28 开售的 [XREAL AURA](https://developer.android.com/blog/posts/build-it-your-way-a-next-era-of-android-development#xreal-aura) 由眼镜端的 X1S 协处理器负责显示和传感，计算盒使用骁龙 Reality Elite（最高 48 TOPS，媒体口径），配 12 GB 或 16 GB 内存。三款产品的共同点是常开感知放在眼镜端，大模型放在别处。Arm 10-30 的[官方博客](https://newsroom.arm.com/blog/ai-wearables-smart-glasses-arm)把这种结构称为“眼镜—手机—云”的混合分工，并估计约 99% 的智能眼镜基于 Arm，举的例子是 Everysight 在 Alif E4（Ethos-U85）上本地做眼动追踪。学术侧，新泽西理工的 [ActiveSight](https://dl.acm.org/doi/10.1145/3795866.3844451) 用常开音频唤醒视觉，平均功耗 453 mW，比持续视频流低 3 倍（论文实测）。

需求侧也有数据支持。TrendForce 预测 2026 年 AR 眼镜出货 131 万副，同比增长 111.1%（[TrendForce](https://www.trendforce.com/presscenter/news/20261015-13273.html)）。高通对 1.2 万名用户的[调研](https://www.qualcomm.com/news/onq/2026/10/personal-ai-wearables-consumer-survey)显示，超过 70% 的智能眼镜用户经常使用 AI。这是厂商自办调研的口径。Apple 10-13 的家居发布则体现了另一种思路：[HomePod mini 2](https://www.apple.com/newsroom/2026/10/apple-announces-the-next-generation-of-homepod-mini/) 从 S5 换成手表级的 S10，[HomeView](https://www.apple.com/newsroom/2026/10/meet-apple-homeview-a-new-way-to-enjoy-entertainment-and-manage-the-home/) 用 A18；Siri AI 请求可以在设备端处理，也可以交给 PCC，但哪些在本地运行、本机内存多大，Apple 都没有披露。芯原 10-29 的 [GLTiny](https://www.verisilicon.com/en/PressRelease/GLTiny) 给手表和眼镜精简了 3D 图形驱动，同样没有数字。

### 三、边缘加速器：从融资阶段进入订单和工具链阶段

爱芯元智 10-13 发布的 [AX8860](https://finance.sina.com.cn/tech/digi/2026-10-13/doc-inivasef8111871.shtml) 是本月国产边端芯片里最大的一款：6nm，256 TOPS（原生 FP4，不含稀疏），最高 128 GB LPDDR5X，带宽 273 GB/s，模组额定 40 W。厂商称在 Qwen 27B 上比 DGX Spark 的 decode 快约 30%。不过两者带宽属于同一档，27B 稠密模型按 FP4 计算的 decode 上限约 20 tok/s（推算），领先幅度应主要来自量化格式和软件栈，需要第三方实测确认。

韩国 DEEPX 本月形成了完整的商业链条。10-08 三星证券和三星创投注资约 147 亿韩元（[媒体援引公司声明](https://finance.biggo.com/news/d79b39e1-8ede-47f6-9497-1648e78725a5)）。10-18 [报道](https://view.asiae.co.kr/en/article/2026101612505185012)称其与台湾 Aetina 签订三年量产供货协议，DX-M1 良率约 90%，首年 77 张订单约 1300 万美元；下一代 DX-M2 改用三星 2nm，目标芯片级功耗 5 W 跑生成式模型。10-22 又在 ITS 世界大会上[展示](https://www.mt.co.kr/future/2026/10/22/2026102211003132310) 1–5 W 的交通视频分析方案（以上均为媒体口径）。欧洲的 Axelera 10-08 发布 [Voyager SDK 1.9](https://community.axelera.ai/product-updates/voyager-sdk-1-9-axscript-models-faster-pipelines-and-python-recipes-1622)，第一次以 AxScript 方式提供 11 个 LLM（0.35B–10B）和 7 个 VLM，但官方性能数字只覆盖视觉管线，没有任何 LLM 的 tok/s。高通 10-12 在 Network X 上发布的[宽带网关平台](https://www.qualcomm.com/news/releases/2026/10/qualcomm-unveils-ai-native-broadband-innovations-across-fiber--w)内置 Hexagon NPU，在网关本地跑意图式网络智能体，NPU 算力未披露。Hailo 本月没有查到窗口内的新品。

### 四、存内计算：国产厂商集中融资，RRAM 推进到 12nm

10-14，后摩智能在北京[公布 2D 和 3D CIM 两条路线](https://www.163.com/dy/article/L99ST9PT0514R9OJ.html)，都以 SRAM-CIM 为基础。3D CIM 用先进封装把逻辑层和存储层叠在一起提升带宽，优化目标是 Token/$ 和 Token/W；M50 量产不到一年，已获 150 多个产品定点（公司口径）。10-23 起的一周里，国产存算融资明显密集。[九天睿芯](https://www.thepaper.cn/newsDetail_forward_34315136)完成新一轮融资，累计融资约 10 亿元，路线是 SRAM 存算与 HBF 垂直堆叠，工程验证平台跑 DeepSeek-V4 单卡 decode 约 20 TPS（公司口径，未披露精度和功耗）。[亿铸科技](https://m.rccaijing.com/news-7520326598232045392.html)宣布完成超 10 亿元融资，路线是以 3D DRAM 为核心的全数字存算。10-28，[微纳核芯](https://news.pedaily.cn/202610/570997.shtml)完成超 10 亿元 C2 轮，3D-CIM 的三颗芯片已投片，计划 2027 年初送样（媒体报道）。需要更正一处周报说法：上一期把这几笔概括为“三笔 10 亿元级融资”，其实九天睿芯的 10 亿元是累计金额，单轮在 10 亿元以上的是亿铸和微纳核芯。四家公司的共同点是都不在 SRAM 平面上继续扩，而是转向 3D：近存 DRAM 或 HBF 堆叠。这和存储厂的路线方向一致。

海外方面，TetraMem 10-27 宣布 [MLX300 完成流片](https://via.ritzau.dk/pressemeddelelse/15250306/tetramem-advances-analog-in-memory-computing-with-tapeout-of-new-12nm-ai-soc?publisherId=90456)，称其为首款 12nm 多值 RRAM 模拟存算 SoC。片上最多存放 6400 万个 INT4 参数，约 32 MB（推算），不需要外部 DRAM。能效目标为 50–80 TOPS/W 以上，这是目标值。这个容量够跑唤醒词、语音增强和小视觉模型，离 1B 级 LLM 还差一个多数量级。三星 10-12 在 OCP 上把 [LPDDR5X-PIM](https://semiconductor.samsung.com/events/ocp-2026/) 放进“边缘 AI 加速器”演示：有效带宽最高为标准 LPDDR5X 的 8 倍，但 Llama 3.1 8B 的实测执行时间只缩短到 1/2.2（官方口径）。实测收益远低于带宽倍数，说明 PIM 的瓶颈已经转到软件映射和非 GEMV 算子上。学术侧，佐治亚理工的 [p-DCIM](https://arxiv.org/abs/2610.37033) 已在 28nm 流片，宏功耗 0.41 mW，用存算伊辛退火替代 LLM 重排来挑选 RAG 证据，每次查询总能耗降低 67%；[GUMPIM](https://arxiv.org/abs/2610.23406) 让 CPU 页和 PIM 页共存，端到端提速 2.3 倍；PACT 2026 也设了 [PIM 大模型专场](https://pact2026.github.io/program#session2-pim)。

### 五、内存层级：HBF、CXL 和“边缘推理内存”进入路线图

本月存储厂的口径高度一致：热数据靠近计算，冷 KV 和权重下沉到更便宜的大容量层。SK 海力士 10-16 的 [OCP 回顾](https://news.skhynix.com/en/ocp-global-summit-2026/)展示了第二代 CMM-DDR5（256 GB，CXL 3.2，80 GB/s）和 CMM-Ax 存内计算。10-14 起的 SEDEX 上，SK 海力士称 HBF 带宽约为 HBM4 的一半、单封装容量超过 10 倍，标准计划 2027 年 1 月定稿（[媒体报道](https://www.techtimes.com/articles/329022/20261014/samsung-chases-faster-hbm4-sk-hynix-goes-taller-koreas-ai-memory-war-begins.htm)）。10-28 的 [Q3 财报](https://news.skhynix.com/en/q3-2026-business-results-1/)第一次把 HBF 写进中长期 NAND 战略，但全文没有提到移动端。三星 10-29 的 [zHBM 文章](https://news.samsungsemiconductor.com/global/part-2-zhbm-next-generation-memory-for-the-data-movement-era)介绍了把内存直接堆在处理器上的方案，没有给任何数字。

和端侧最相关的是美光。10-21 的[技术研讨会材料](https://s25.q4cdn.com/621799436/files/doc_downloads/2026/10/MU-TP-Webinar.pdf)首次公开 vEIM（垂直边缘推理内存）：首代规格 2 TB/s，每比特能耗低于 1 pJ，路线图到 2030 年（目标值）。按带宽除以每 token 读取字节数推算，8B INT4 模型的 decode 上限约 500 tok/s；但按 1 pJ/bit 计算，跑满 2 TB/s 时接口功耗约 16 W，手机放不下，更适合机器人、车载和 AI PC。同一份材料确认 LPDDR6 的功耗比 LPDDR5 改善超过 35%（目标值），并且美光不走 4F² 路线。

学术界在手机这一档也给出了具体方案。北大与中科院微电子所的 [NORmal](https://arxiv.org/abs/2610.40000) 实测了 3D 铁电 NOR 阵列，把它当作普通 rank 挂到未改动的 LPDDR6 总线上，用来常驻 200B 级 MoE 规划模型。论文给出的带宽账很清楚：4-bit 下每 token 要读 1.5–8.5 GB，走 UFS 时 decode 上限只有 1.3–7.2 tok/s，走 LPDDR6 时为 18–102 tok/s。仿真结果比 UFS 卸载快 8.9–28 倍。KAIST 的 [MemLLM](https://arxiv.org/abs/2610.22579) 在 SSD 内部执行端侧 RAG 的注意力计算，平均提速约 4 倍，功耗控制在 3 W 以内。[LeanStream](https://dl.acm.org/doi/10.1145/3795866.3844470) 在 OnePlus 13 和 Jetson 上做闪存流式推理，内存占用降低 4.8–7.5 倍。[Gandalf](https://arxiv.org/abs/2610.30791) 在把 KV 卸载到 SSD 时让闪存寿命平均延长 7.3 倍。HBFSim 估算 HBF 寿命为 2.0–6.9 年（[MBZUAI](https://arxiv.org/abs/2610.23503)）。这些结果说明写入寿命已经成为闪存层级的第一约束。以上均为论文仿真或实测口径。

### 六、LPDDR6 与内存周期：成本制约端侧规格

成本信号贯穿全月。TrendForce 新闻栏目 10-20 [转引](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand-tight-supply-support-outlook/)韩台机构的看法，Q4 DRAM 合约价预计环比再涨约 20%。注意这是对他方观点的汇总，不是 TrendForce 自己的预测。Counterpoint 的数据显示 Q3 手机 SoC 出货同比下降 21%，手机内存价格 Q3 环比上涨 5%–10%（[第三方口径](https://www.counterpointresearch.com/en/insights/smartphone-oems-shift-focus-to-profitability-as-soc-shipments-fall-21-percent-yoy)）。三星 Q3 半导体部门营业利润 106.5 万亿韩元，手机业务却亏损 0.6 万亿韩元（[官方](https://news.samsung.com/global/samsung-electronics-announces-third-quarter-2026-results)）。韩国 10 月芯片出口同比增长 259%（[韩联社](https://www.koreatimes.co.kr/economy/20261101/koreas-monthly-exports-hit-1153-bil-in-oct-on-record-chip-sales)）。树莓派 11-02 宣布 [16GB 版涨价 80 美元](https://www.raspberrypi.com/news/price-rises-for-some-16gb-raspberry-pi-products/)，涨到 385 美元。Altman 甚至公开说，PC 里的 DRAM 只有约 5% 的时间在用，应该优先给数据中心（[媒体转述](https://www.notebookcheck.net/Quite-terrible-Sam-Altman-says-PCs-waste-the-world-s-limited-DRAM-supply.1438393.0.html)）。

在这种背景下，LPDDR6 进手机的节奏变得不确定。10-19 的[爆料](https://nokiamob.net/2026/10/19/galaxy-s27-could-launch-in-earlier-than-expected-as-samsung-races-to-production/)称，三星只考虑在 S27 Pro 和 Ultra 上用 LPDDR6 加 UFS 5.0，而且尚未定案（可信度低）。按 LPDDR6-10.7Gbps、64-bit 计算，峰值带宽约 85 GB/s，只比 LPDDR5X-9600 的约 77 GB/s 高一成左右（推算），所以端侧能拿到的带宽红利有限。国产方面，长鑫 10-30 在业绩交流会上披露 4F² 第六代平台已完成工程样片验证，但首个目标市场是服务器（[IT之家](https://www.ithome.com/1/020/599.htm)）。11-01 的[交流会记录](https://www.ithome.com/1/020/832.htm)显示，上半年 LPDDR 占长鑫营收 52.02%，LPDDR6 将在第五代平台上升级（媒体转述）。

### 判断与 11 月观察

本月最重要的判断是：**端侧 AI 硬件的主矛盾已经从 TOPS 转到每 token 读多少字节、从哪一层读、读的成本多高。** 常开层面，Coral、Sequora、NeuPro 都把生成式模型写进了低功耗规格，但目前只有架构目标值，没有功耗和 tok/s 实测，因此短期内眼镜、家居设备仍会采用“设备端感知 + 手机或云端生成”的分层结构。存算层面，国产厂商在一个月里集中把路线押到 3D 近存和 HBF 堆叠，TetraMem 推到 12nm RRAM，但这些产品要到 2027 年才送样或供货，本月新增的是资本和流片，不是性能数据。内存层面，HBF、vEIM、铁电 NOR 等新层级开始成形，但多数先面向服务器、机器人和车载；手机端的近期变量是 LPDDR6 的成本，而不是新存储形态。

11 月重点关注：SR200 和 Coralboard SR 的开售时间与整芯片功耗；Ceva 在新竹、上海研讨会上是否公布 NeuPro 的具体 TOPS；三星 AI 眼镜的芯片方案；JEDEC HBF 标准的进展；首批 LPDDR6 手机能否落地，以及 Q4 合约价的实际涨幅；IEDM（12 月）前各家公布的存算与 3D DRAM 论文摘要。

## 5. 顶会：端侧大模型瓶颈全面转向内存

10 月（10-08 ~ 11-02）的顶会素材集中在三个会：芝加哥的 [PACT 2026](https://pact2026.github.io/program)（10-19 workshop，10-20~10-22 正式报告）、奥斯汀的 [ACM MobiCom 2026](https://sigmobile.org/mobicom/2026/program.html)（10-26~10-29 主会，10-30 workshop），以及 10-31 在雅典开幕的 [MICRO 2026](https://microarch.org/micro59/program/index.php)。MICRO 10-31、11-01 两天是 workshop 和 tutorial，主会第一天是 11-02，正好是本月窗口的最后一天；11-03、11-04 的两天论文归 11 月。月初的 VLSI-SoC 2026（10-11~10-14）有边缘 AI 可靠性专场，SEC 2026、UbiComp/ISWC 2026 也在 10 月中旬召开，但都没有找到可核实数字的端侧芯片或系统论文。日期取法：PACT 首周按会议首日 10-19 记，后来补全文的按报告日记；MobiCom、MICRO 一律按报告日记。

本月结论：**三个会讲的是同一件事——端侧大模型的瓶颈是内存，不是算力。** PACT 的重点是把计算放进 LPDDR（三星 PIM 两篇），MobiCom 的重点是让操作系统和推理框架管好 KV 缓存、闪存权重和 MoE 专家，MICRO 首日则出现了把 MoE 专家放进 3D NAND 计算、用 chiplet 堆带宽的专用边缘芯片。和上月 ESWEEK 偏嵌入式实测相比，10 月的论文更接近手机和 PC：有 Galaxy S24+、OnePlus 13、Pixel 7/8 的真机数据，也有 Ryzen AI 两代 NPU 的实测。

### 内存侧计算：从 LPDDR-PIM 到 3D NAND 存内计算

PACT 的 PIM 专场有 4 篇，都做 LLM 推理。三星的两篇可以合起来看。[PIM-SHERPA](https://arxiv.org/abs/2603.09216)（三星 SAIT / 三星电子 / 延世）解决“权重放哪”：手机上 prefill 要求权重在可缓存区、用主机布局，decode 走 PIM 又要求在不可缓存区、用 PIM 布局，以前只能存两份。Llama 3.2 3B 的 BF16 权重约 6.4 GB，再存一份手机放不下；论文实测 Galaxy S24+ 能设成不可缓存的连续区只有约 1 GB。它用 DRAM 双缓冲和在线 swizzle 只留一份权重，内存节省约 47.8%–49.7%（论文口径；prefill 是 S24+ 真机测，PIM 部分为仿真）。[PDiMC](https://pact2026.github.io/program/papers/pact26-final87.pdf)（三星电子）解决“命令怎么发”：PIM 命令经 DFI MUX 直接送到 PHY，绕开内存控制器重排，GEMV 比软件控制 PIM 快最多 68%，混跑时 LLM 吞吐最高为无 PIM 基线的 2.8 倍（论文口径）。同专场 ETRI/KAIST 的 [Pascal 混合 PIM](https://pact2026.github.io/program/papers/pact26-paper109.pdf) 面向长序列 KV 过滤，比稠密 PIM 平均快 5.3 倍。

为什么手机需要这条路线，可以用带宽算一下（推算）：S24+ 的 LPDDR5X-8533 峰值约 68 GB/s，3B 模型 BF16 每个 token 要读约 6.4 GB 权重，decode 上限约 10 tok/s；int8 也只有 20 tok/s 左右。

MICRO 首日（11-02）的 Session 1B “3D-Stacked & PIM Architectures for LLM/MoE Serving” 把这条线往下推了一层。北京大学集成电路学院的 **NFC**（3D NAND Flash-CIM Centric Architecture for On-Device MoE LLM Inference）把端侧 MoE 的专家放进 3D NAND 做存内计算，首尔大学的 **HyPIM** 用统一 PIM 架构跑 Mamba-Transformer 混合模型，北大与西安紫光国芯、后摩智能合作的 **ATLAS** 是一个经过流片芯片校准的 3D-DRAM LLM 加速器全栈模拟器（[arXiv 预印本](https://arxiv.org/abs/2604.08044)称模拟误差 ≤8.57%，对标 H200，偏数据中心）。NFC、HyPIM 截至 11-02 没有找到公开全文，只能确认题目和作者（[MICRO 节目单](https://microarch.org/micro59/program/index.php)）。同一场还有微软亚洲研究院的 **TNT**：用查表（LUT）统一计算超低比特权重和 KV，延续 T-MAC、LUT Tensor Core 一脉。

一个月看下来，内存侧计算的讨论对象从“LPDDR 里加乘法器”扩到了“闪存里算专家”。前者三星已经在解决系统落地问题，后者还停留在架构论文阶段。

### 手机 LLM 的内存墙：MobiCom 给出的系统软件解法

MobiCom 本届开幕第一场就是 “On-Device LLMs and Mobile AI Agents”，10-27 下午的 Session 8 排了 18 篇闪电报告。本月收录的 11 篇里有 6 篇直接处理内存：

- **以算换存**：香港城市大学的 [NPUGen](https://dl.acm.org/doi/10.1145/3795866.3844480) 观察到 decode 期间手机 NPU 基本闲置，于是 KV 缓存放不下时不从存储换入，而是让 NPU 做一次类 prefill 前向重新算出 KV，并做成可被前台抢占的后台服务。论文在高通 SoC 手机上实测，但摘要没给倍数和具体 SoC 型号。
- **闪存流式**：George Mason 大学与摩根大通的 [LeanStream](https://dl.acm.org/doi/10.1145/3795866.3844470) 把权重放在闪存、按激活稀疏性按需加载。在 Jetson AGX Orin/Xavier 和 OnePlus 13（骁龙 8 Elite + UFS 4）上跑 7B 模型，达到以往最佳吞吐时内存降 4.8–7.5 倍，吞吐再提 1.6–2.1 倍（论文实测）。论文也指出手机 UFS 带宽低于 NVMe，内存预算一降，手机更早被 I/O 卡住。
- **OS 层回收**：西北工业大学的 [AppFlow](https://dl.acm.org/doi/10.1145/3795866.3796690) 实测 86.6% 的 GB 级应用冷启动超过 1 s，在 Pixel 7/8 上统一调度预加载、回收和查杀，冷启动延迟降 66.5%（如 2 s→690 ms）。同主题 10-26 的 [ExoMem](https://dl.acm.org/doi/10.1145/3795866.3844471)（64 GB Jetson 稳定跑 72B 级模型）和 [mzCache](https://dl.acm.org/doi/10.1145/3795866.3844495)（TTFT 比存储卸载降 2.1–5.5 倍）周报未单独收录，这里作背景。
- **MoE 专家搬运**：有 4 位华为作者的 [CFMoE](https://dl.acm.org/doi/10.1145/3795866.3844455) 认为训练时的负载均衡让专家路由缺乏局部性，从路由、微调、引擎三层一起改，平均内存降 32.9%；山东大学等的 [CRISP](https://dl.acm.org/doi/10.1145/3795866.3844472) 在 Mixtral-8x7B、DeepSeek-MoE-16B 上同等内存吞吐最高提 2.1 倍，精度损失不超过 3.6%（均为论文口径）。

把 PACT 和 MobiCom 放在一起看：硬件路线（PIM、闪存存内计算）和系统软件路线（KV 重算、闪存流式、OS 回收）在处理同一个问题。短期内能在手机上落地的是后者，因为它不需要新的内存颗粒。

### 异构 SoC：把已有的 NPU 和 iGPU 用满

PC 方向本月有两篇基于 AMD Ryzen AI 的实测，一篇在 PACT，一篇在 MICRO。

[AIEHalide](https://pact2026.github.io/program/papers/pact26-final56.pdf)（IIIT Hyderabad / AMD，PACT 10-21）让同一份 Halide 源码编译到两代 XDNA NPU：int8 GEMM 在 XDNA 上 5.42 TOPS，在 XDNA 2 上 25.46 TOPS（峰值 40.96 TOPS 的 62%），代码量比手写 IRON 少 2.8 倍（论文实测）。但手调实现在 XDNA 2 上能到 93% 峰值，bf16 利用率只有约 38%。论文给出 XDNA 2 的 DRAM 带宽约 40 GB/s，按此推算 int8 的 3B 模型 decode 上限约 13 tok/s。

[HeteroMosaic](https://arxiv.org/abs/2607.12839)（UIUC / AMD，MICRO 11-02，Session 2A）回答的是“NPU 和 iGPU 能不能一起用”。它先用异构 roofline 判断何时值得把 iGPU 和 NPU 合用，再把推理拆成保持依赖的微批，按实测 trace 联合优化调度和设备分配，考虑内存争用、DVFS 和 NPU 运行时开销。在 Ryzen AI 7 350、Ryzen AI 9 HX 370、Ryzen AI Max+ 395 三个平台上评估，balanced 平台相对单用 iGPU 最高 1.73 倍、相对单用 NPU 1.78 倍、相对 llama.cpp 2.05 倍，能耗最多降 45.3%（论文实测）。

手机侧对应的工作是 PACT 上延世大学与三星电子的 [异构 SoC 大模型调度](https://pact2026.github.io/program/papers/pact26-final195.pdf)：针对 NPU 内 TE、VE 共享片上 SRAM 的结构，用动态规划调度，平均比列表调度快 1.16 倍。MobiCom 上中山大学的 [nn-Live](https://dl.acm.org/doi/10.1145/3795866.3844468) 用每核硬件计数器预测 big.LITTLE 手机 SoC 上多模型并发的延迟。CPU 矩阵单元方向，PACT 的 [HiNa-MoE](https://arxiv.org/abs/2610.05123)（国防科大）在 Intel AMX 上跑 MoE 专家，端到端最高 2.09 倍；MICRO 首日 Session 2B 还有一篇专讲 Arm SME 外积的软件预取（HSPref），对 SME2 手机 CPU 有参考意义，但尚无全文。

这一组论文的共同结论是：PC 和手机 SoC 的 TOPS 已经不缺，缺的是编译器、调度器和对 NPU 运行时开销的建模。

### 专用边缘芯片：MICRO 首日的两篇“Distinguished Papers”

MICRO 11-02 下午的 Session 3C（Distinguished Papers II）有两篇直接面向边缘 LLM 的芯片设计：

- [EdgeXpert](https://arxiv.org/abs/2608.05303)（KAIST Hoi-Jun Yoo 组）要解决投机解码和 MoE 叠加时的冲突：投机解码一步生成多个候选 token，每个 token 选的专家不同，合起来要读的权重反而更多。它在 prefill 阶段改成按 prompt 共享一组专家，在 decode 阶段把同深度候选 token 的专家合并、只加载显著通道再做计算校准。三星 28 nm、800 MHz 综合结果，相比已有工作延迟最多降 56.3%、能耗降 44.1%，精度接近基线（论文口径，综合而非流片）。
- **Pistil**（哈佛 Brooks/Wei 组，与洛克希德·马丁合作）是一个 20 个 chiplet 的 2.5D 封装系统，用解耦流水线在多 chiplet 间维持内存带宽，跑分布式小语言模型推理。[Hot Chips 2026 海报](https://hc2026.hotchips.org/program/posters/)写明是 16 nm 加速器，MICRO 论文全文暂未公开，性能数字未披露。

再加上 PACT 的 [SLGS](https://pact2026.github.io/program/papers/pact26-final39.pdf)（延世，Meta 作者参与）：给 GPU 加一个 2.118 mm²、688 mW 的 3DGS 渲染尾段，相对 Jetson Orin NX 上的原版 3DGS 平均加速 12.43 倍（前端真机、尾段周期级仿真）。专用单元都很小，目标都是在带宽或功耗受限的设备上省掉一类数据搬运。

### 可穿戴、MCU 与 XR：眼镜靠分级唤醒和手机协同

MobiCom 上新泽西理工的 [ActiveSight](https://dl.acm.org/doi/10.1145/3795866.3844451) 是本月唯一自己做加速器并上真眼镜的论文：低功耗音频前端常开触发，需要时才启动 CLIP 检测器；FPGA 加速器 PL 侧能效 44.3 GOPS/W，平均功耗 453 mW，比持续视频流低 3 倍，真实眼镜命中率 88.5%。453 mW 对眼镜电池仍偏高，量产需要 ASIC。美国东北大学的 [智能眼镜首次实测](https://dl.acm.org/doi/10.1145/3795866.3844477) 主张把手机当眼镜的边缘服务器。MICRO 主会第一个主旨报告（11-02，UIUC 的 Sarita Adve）题为“从眼镜到数据中心”，讲的也是把沉浸式智能分摊到穿戴设备、附近设备、边缘和云。

MCU 方向，代尔夫特的 [InstMeter](https://dl.acm.org/doi/10.1145/3795866.3796672) 按时钟周期预测 MCU 推理能耗和延迟，误差比 SOTA 低 3 倍和 6.5 倍，覆盖 Cortex-M4/M7/M33 和 ESP32-C3。月初 [VLSI-SoC 2026](https://vlsi-soc.com/program.html#day2-edge-ai) 的边缘 AI 专场讲的是 SRAM 存内计算阵列的缺陷测试和功能安全，说明 CIM 的讨论在从能效转向可测性和量产。

### 判断与 11 月观察

三个判断：

1. **端侧 LLM 的硬件研究已经整体转向内存。** PACT、MobiCom、MICRO 三个会合计二十多篇对题论文，大多数在处理 KV 缓存、权重存放、专家搬运或带宽，真正“加 TOPS”的只有 EdgeXpert 这类专用芯片，而它的收益同样来自减少外部访存。
2. **手机上最先落地的是系统软件，不是新内存。** LPDDR-PIM 有三星在推，但 PIM-SHERPA 的 PIM 部分仍是仿真；NPUGen、LeanStream、AppFlow 都是现有手机上能做的事。7B 模型放进闪存后，UFS 带宽会成为下一道墙。
3. **PC 异构调度有了第一批可比数字。** 同在 Ryzen AI 上，AIEHalide 证明 NPU 可以用编译器而非手写用到 60% 左右的峰值，HeteroMosaic 证明 NPU 加 iGPU 合用比 llama.cpp 快 2 倍左右。下一步要看厂商运行时（Ryzen AI SW、OpenVINO、QNN）是否吸收这类调度。

11 月要看：MICRO 11-03、11-04 两天的剩余论文（尤其是 NFC、TNT、HyPIM、Pistil 的全文数字）；11-08~11-12 的 ICCAD 2026，已知有雅典国立技术大学的 [降压容错 DNN 加速器](https://arxiv.org/abs/2610.33824)（2 nm 评估，节能 39%，论文口径）；PACT 论文集上线 ACM DL 后核对 PIM 专场的最终数字；以及 2027 年 2 月 ISSCC 的论文名单是否提前公布。

## 6. arXiv：智能体能耗账与内存瓶颈

### 本月结论：端侧论文开始算“智能体的能耗账”，内存成了核心约束

10 月 8 日至 11 月 2 日，arXiv 上端侧硬件和系统方向的论文有一个明显转向。9 月以前，这类论文多在回答“某个模型在某块芯片上能跑多快”；本月，越来越多的论文在算一个智能体完整工作循环的成本：每一步多少秒、每一步多少焦耳、待机多少瓦、连续跑几分钟后会不会降频。真机证据集中在高通 Hexagon NPU 上，主要来自 Tandem、手机 NPU LoRA 训练、LG U+ ixi-sLM、三星 HyCo 和中南大学与微软亚洲研究院的边缘 NPU 实测。主线有三条。第一，手机 NPU 已经能承担 2B–4B 级智能体的推理，部分场景还能做训练，但瓶颈从矩阵算力转到了 softmax、布局变换、温控和待机功耗。第二，投机解码这类服务器上的成熟加速在 Mac 和手机 NPU 上接连失效，“每 token 读多少字节”成了端侧优化的统一口径。第三，SSD、HBF、PIM、铁电 NOR 这些容量层开始被设计成推理关键路径的一部分，目标是在手机或个人电脑上常驻 30B 到 200B 级模型。下文数字除特别注明外，均为论文作者自测或仿真口径；标“推算”的是按带宽和每 token 读取字节数估算的结果。

### 手机 NPU：智能体能跑起来，账算到了焦耳和待机功耗

本月手机端最扎实的一组数据来自 FIU、NEC 美国实验室等机构的两篇论文。[Tandem](https://arxiv.org/abs/2610.26660)（10-19）以真实 GUI 智能体轨迹为负载，在 llama.cpp 的 Hexagon 后端上做了三件事：在请求分叉点保存线性注意力状态，让 prefill 留在 HMX 矩阵单元上，在任务间隙释放 NPU 电源投票。在 OnePlus 13T（骁龙 8 Elite）上，Qwen3.5-4B Q4_K_M 的文本步从 1.96 s 降到 1.38 s，每步高于待机的能耗从 15.1 J 降到 10.1 J，模型常驻时的待机功耗从 0.76 W 降到 0.22 W；在 OnePlus 15（8 Elite Gen 5）上文本步为 1.21 s。同一团队的[手机 NPU 一阶 LoRA 训练](https://arxiv.org/abs/2610.24816)（10-17）把 NPU 推理接口改造成能算输入梯度的接口，Qwen3.5-4B 的夜间个性化约 8 小时完成，能耗 0.2275 J/token，约为优化后 CPU 训练器的三分之一；同形状前向 HMX 为 4.65 TFLOPS，CPU 只有 0.178 TFLOPS。

商用落地方面，[LG U+ 的 ixi-sLM](https://arxiv.org/abs/2610.19382)（10-14）是本月唯一的“百万级用户生产系统”。它以 EXAONE 4.0 1.2B 为底座，压到 803 MiB。在 Galaxy S25 Ultra 的 NPU 上 prefill 为 3,558 tok/s、decode 为 55.8 tok/s，每通电话耗电从 CPU 的 7.79 mAh 降到 1.79 mAh。NPU 的节电集中在 prefill（约 17 倍），decode 只省约 2 倍，这符合 decode 受带宽限制的常识。三星研究院的 [HyCo](https://arxiv.org/abs/2610.21436)（10-15）把云端 Gemma 4 26B-A4B 的 MTP 头量化后放到 Galaxy S26 Ultra 的 Hexagon v81 上起草，云端 GPU 每 token 时间减少 38.6%，用户侧送达 35.0 tok/s。这是本月唯一一篇把手机 NPU 设计成云端大模型协处理器的论文。

月末，中南大学与微软亚洲研究院的[边缘 NPU VLM 实测](https://arxiv.org/abs/2610.40039)（10-29）给这条线算了一笔清醒的账。我们打开原文核对：在 Hexagon v73、v79 和 RK3588 三块 NPU 上，Qwen3.5-2B 平均 prefill 729 tok/s、decode 16.7 tok/s。但在 OnePlus 13T 上用高通 GenieX 运行 Wi-Fi 导航任务，单轮最长 37.4 s，五轮共 146.4 s；512 帧视频摘要在开始解码前就要 97.6 s。原因有三：softmax 由 HVX 向量单元执行，HMX 只能等待；GDN 线性注意力占 Qwen3.5-2B prefill 的 54.5%–61.7%，理论上的复杂度优势被张量重排开销抵消；持续推理还会触发温控降频。把 Tandem 和这篇放在一起看，4B 级模型做文本步大约 1.2–1.4 s/步，带截图的多模态步就要数秒到数十秒。目前手机 GUI 智能体的体验上限由非矩阵算子和散热决定，而不是 TOPS。

软件生态也有进展。高通自己的 [AIPC](https://arxiv.org/abs/2610.34890)（10-26）用带技能的 LLM 智能体，把 7 个 PyTorch 项目自动搬上 QCS9075 的 HTP。论文顺带记录了 NPU 部署的硬约束：MeloTTS 解码器 11.16 MiB，超出 8 MiB VTCM；Qwen3-0.6B 单图约 1.50 GiB，超出单图映射上限，必须拆图。威斯康星、Meta 和 CMU 的 [CrossInfer](https://arxiv.org/abs/2610.35309)（10-26）让 CPU、GPU、NPU 轮流接着生成同一段视频对话。跨引擎 KV 导入使首 token 延迟比重算低 4.6 倍；作者还发现 batch=1 decode 在 M4 Max 上 GPU 最快，在 RK3588 上 CPU 最快。月初还有一批 10-08~10-12 投稿：[HeteroVDiff](https://arxiv.org/abs/2610.16244) 在 Galaxy S25 上让 NPU 与 GPU 共享一份 INT8 权重生成视频，权重内存省 48%；[SchemaWeaver](https://arxiv.org/abs/2610.17436) 把手机工具调用改成并行解码，时延最多降低 3.9 倍。窗口最后几天（10-31 提交）的 [BitLLM](https://arxiv.org/abs/2611.00547) 在手机 GPU 上把 W4A8 的类型转换移出计算热路径，平均比 llama.cpp、MNN-LLM、LiteRT-LM、MLC-LLM 快 1.47–1.78 倍，长上下文每 token 能耗最多降 88.9%（作者自测，已核摘要）。手机 GPU 路线仍有很大的软件余量。

### 投机解码在端侧失灵：减少读取字节才是正道

本月最值得写进判断的变化是投机解码在端侧“失灵”。MacPaw 的 [Apple Silicon 复测](https://arxiv.org/abs/2610.31479)（10-22）在 M2 到 M4 Pro 等四台 Mac 上测了 6 种投机解码，MLX 单请求下没有一种有端到端净收益。在 M3 Ultra 上，DFlash 每轮平均接受 2.57 个 token，decode 却从 156.7 降到 60.0 tok/s。相反，KV 剪枝在 Mac 上让 Qwen3-4B 提速 1.61–1.75 倍，在 RTX 4090 上只有 0.98 倍。Tandem 也测到，在 Hexagon NPU 上开投机解码后文本步反而升到 2.55 s，原因是循环状态快照拖慢 prefill，验证内核随草稿数的扩展也差。

成功的案例都没有增加权重读取量。港理工的 [BitMTP](https://arxiv.org/abs/2610.28500)（10-20，NeurIPS 2026，PolyU-OPPO 联合中心资助）让 1.58/2-bit 主干自己做多 token 起草，在 Jetson Orin NX 上把 BitNet 从 19.35 提到 61.76 tok/s（3.2 倍），倍数还高于 H20。HyCo 把起草移到手机、验证留在云端，等于把两边的字节账拆开了。ReClan 的 [MoE 投机解码模型](https://arxiv.org/abs/2610.34440)（10-25）把这条经验写成公式：步时间 = 请求字节 ÷ 有效带宽 + 固定开销，专家去重读取只在每次验证约 5–8 个 token 时才划算，并在 llama.cpp Metal、MLX-LM 和 CUDA 上验证。NVIDIA 与 Texas Tech 的 [Token 能耗定律](https://arxiv.org/abs/2610.28576)（10-20）从能耗一侧给出同样的框架：J/token 是“活跃字节”和“decode 时间”的仿射组合，在 GH200/GB300 上误差不超过 3.73%。端侧 batch=1 无法摊薄权重读取，所以 J/token 基本由每 token 读多少字节决定（推算）。高通的 [ELSI 选层](https://arxiv.org/abs/2610.12939)（10-09）让 EAGLE3 只用 1 层隐状态就持平默认的 3 层，但实验全部在 H100 上完成，能否迁移到 NPU 要打问号。

德州农工有两篇论文提醒，“省字节”也不等于“省电”。[10-23 的论文](https://arxiv.org/abs/2610.32417)在 A100 + llama.cpp 上跑 29 个带自动判分的智能体任务，4-bit 每 token 更省，但每完成一个任务的能耗最高可达 8-bit 的 3.5 倍。[10-30 的论文](https://arxiv.org/abs/2610.41672)换成 vLLM 多并发：四并发时 W4A16 每个验证通过的任务能耗比 W8A8 高约 49%（Qwen3.5-9B 为 48.4 vs 32.6 kJ），KV 缓存紧张时结论又会反转。测试平台都是数据中心 GPU，数值不能直接搬到手机，但“按任务而不是按 token 算能耗”这个口径适用于端侧智能体。

### PC 与统一内存：本地智能体的规模被显存和内存限住

Meta 的 [Muse Glimmer 30B 技术报告](https://arxiv.org/abs/2610.24628)（10-17）把“32GB 显存”写成了首要架构约束。团队比较了 1:8 和 1:16 两种 MoE，最终因稠密配置训练计算效率高 2–2.5 倍而选择稠密 30B，并用 3 局部 + 1 全局滑窗和 2 个 KV 头压缩 KV。4bit 方案分 24GB（Q4KM）和 32GB（EvoPress）两档，准确率比 BF16 低 0.1–0.9 个百分点。报告没有给 tok/s。按 RTX 5090 约 1.8 TB/s 带宽、每 token 读取约 18 GB 推算，decode 上限约在 100 tok/s 量级（推算）。上海交大 IPADS 的 [UMA 内存共享实测](https://arxiv.org/abs/2610.13125)（10-09，EuroSys 2027）覆盖 Lunar Lake、Arrow Lake、Raptor Lake 和 Jetson AGX Orin，总结出页大小、非缓存内存和单向一致性的规律。在 llama.cpp 运行 GLM-4.7-Flash 的智能体负载上，单请求延迟降低 9.0%–15.9%，模型加载时间在 Arrow Lake 上从 10.40 s 降到 5.06 s。Apple 的 [Minions](https://arxiv.org/abs/2610.12970)（10-09）把员工闲置 Mac 的 GPU 汇成批量推理池，但只有定性数据。

小显存和小内存方向：[SparPR](https://arxiv.org/abs/2610.18140) 在 8GB 笔记本 RTX 3070 Ti 上把 OPT-6.7B 的 4k prompt 时延降低 63%；[16MB 冻结词表](https://arxiv.org/abs/2610.22428) 让约 270M 级三值模型只占 46 MB，在笔记本 CPU 上达到 615–740 tok/s；UIUC 的[三值模型 CPU 解码](https://arxiv.org/abs/2610.28620)发现线程有 20%–48% 的时间在同步点等待，改成列切分后提速 1.5–2.1 倍。另一个新出现的方向是：查表多、计算少的参数正在占据端侧内存预算的大头。[OPTIC](https://arxiv.org/abs/2610.31309) 把 Gemma 4 E4B 的逐层嵌入（占参数 35.2%）从 5.64 GB 压到 56.4 MB，保留 97.8% 的性能；[低比特 n-gram 嵌入](https://arxiv.org/abs/2610.31646)让表内存省 47%–55%。KV 一侧，圣母大学的 [GAAC](https://arxiv.org/abs/2610.38210) 利用 BF16 指数位冗余做无损压缩，在 Apple M4 上让 64K 上下文的解码注意力快 1.02–1.25 倍，可以和有损方案叠加。

### 容量层进入推理路径：SSD、HBF、PIM 和铁电 NOR

本月有八篇以上论文讨论“权重和 KV 放在哪种介质上”，密度明显高于 9 月。KAIST 的 [MemLLM](https://arxiv.org/abs/2610.22579)（MICRO 2026）给 SSD 的每个 NAND 通道配一个加速器，在盘内直接对预计算 KV 做注意力，以 Jetson Orin 为主机，端侧 RAG 平均提速 4.06 倍，功耗限定在 3 W SSD 控制器预算内（模拟 + 实测混合）。[HBFSim](https://arxiv.org/abs/2610.23503) 的结论是权重适合放在 HBF，频繁写入的 KV 应留在 HBM。[GUMPIM](https://arxiv.org/abs/2610.23406) 让 CPU 页与 PIM 页零拷贝共存，端到端快 2.3 倍。首尔大学的 [DuoPD](https://arxiv.org/abs/2610.26131) 把整段 decode 交给 HBM 逻辑层，吞吐最高提升 2.23 倍。中旬的服务器论文开始关注闪存磨损：[Gandalf](https://arxiv.org/abs/2610.30791)（有三星半导体作者）按注意力类型决定哪些 KV 写入 SSD，使 SSD 寿命平均延长 7.3 倍；华为参与的 [SARIA](https://arxiv.org/abs/2610.31169) 让多轮智能体的 SSD 写入减少 57%–59%。智能体 KV 频繁写闪存会磨损介质，这对手机 UFS 同样成立。UESTC 的 [WorldPager](https://arxiv.org/abs/2610.35529) 把 int4 KV 分到 GPU、DRAM 和 NVMe 三层，在单张 RTX 4090 + 32 GB 内存上连续生成 37.5 分钟交互视频，零卡顿。

月末的 [NORmal](https://arxiv.org/abs/2610.40000)（10-29，北大、中科院微电子所）把这条线推到手机。它把已流片实测、感测时间小于 7.5 ns 的 3D 铁电 NOR 当作普通 rank 挂到未改动的 LPDDR6 总线上。论文自己的推算是：4-bit 下 3B–17B 激活参数每 token 读 1.5–8.5 GB，UFS（10.8 GB/s）卸载的 decode 上限只有 1.3–7.2 tok/s，满速 LPDDR6（153.6 GB/s）可达 18–102 tok/s。服务级仿真中，NORmal 比 UFS 卸载快 8.9–28 倍；在 256K token 以上的长会话中比 HBF 快 2.8–6.3 倍，短会话仍比 HBF 慢（只有 HBF 的 58%–91%）。200B 级结果全部来自仿真，FeNOR 量产成熟度无数据。11 月 2 日提交的 [PagedMoE](https://arxiv.org/abs/2611.03173)（已核摘要）给出 PC 侧对照：Qwen3.5-397B-A17B 的专家常驻 SSD、DRAM 缓存 24 GiB，平均 2.5 bit 动态精度下实测 8.89 tok/s，是统一 4-bit 的 1.56 倍。用 NORmal 的口径换算，17B 激活参数在 2.5 bit 下每 token 约读 5.3 GB（推算），单靠 SSD 根本达不到 8.89 tok/s，这个速度主要靠 DRAM 专家缓存命中。“大 MoE 上端侧”的胜负手是缓存命中率，不是闪存带宽。

### 加速器与数据格式：块缩放、三值和非矩阵单元

本月加速器论文的共同关键词是块缩放格式和超低比特。[MFSA](https://arxiv.org/abs/2610.19645)（ICCD 2026）在 TSMC 28nm 上让 16×16 阵列同时支持 MX 和 NVFP4，FP4 峰值 4 TOPS，MX 带来的增量面积减少 64.2%。KU Leuven 的[块缩放格式探索](https://arxiv.org/abs/2610.26083)（ASP-DAC 2027）推荐 UE5M3，以 +0.06% 面积把困惑度退化最多降低 25.3%。[BS-Spec](https://arxiv.org/abs/2610.22877) 从同一份块浮点权重只读高位做草稿，最高提速 1.9 倍。三值方向，浙大的 [SPARTA](https://arxiv.org/abs/2610.34824)（10-26）指出 1.58-bit 之后长上下文瓶颈转到 KV 流量，两级稀疏注意力把 KV 流量降低 4.1–4.8 倍；28nm 综合加周期级仿真下，吞吐是 Jetson AGX Orin 的 3.9 倍，能效是 8.3 倍。同校的 [DynaTE](https://arxiv.org/abs/2610.11284)（10-08）面向扩散 LLM，相对 Orin 快 2.55 倍，能效高 6.07 倍（综合 + 仿真）。其余方向：[FIGFLEX](https://arxiv.org/abs/2610.30480) 的 FP-INT 通路吞吐随位宽下降而提升；BSC 在长向量 RISC-V 上[重构 FlashAttention](https://arxiv.org/abs/2610.29489)，周期减少 1.84–2.08 倍；ICCAD 的[降压运行加速器](https://arxiv.org/abs/2610.33824)在 2nm 评估下节能 39%，精度损失小于 1%。

存内计算方面，佐治亚理工的 [p-DCIM](https://arxiv.org/abs/2610.37033) 是一颗已流片的 28nm 存内伊辛机，面积 0.16 mm²、功耗 0.41 mW，把 RAG 证据挑选改写成 QUBO 求解，每次查询总能耗降低 67%；IIT Indore 的 [SLICE-CiM](https://arxiv.org/abs/2610.37601) 只改外围控制，就把能效从 31.35 提到 454.91 TOPS/W，但这是 65nm 综合仿真结果。结合前面的手机实测，本月收录的加速器论文仍集中在矩阵数据通路和格式上，几乎没有针对 softmax、布局变换这类向量侧瓶颈做硬件设计，这是本月最明显的错位。

### 机器人与 VLA：延迟取决于动作生成方式

机器人方向本月从“能不能机载”走到了“为什么慢”。NUS 的 [VLA-HWBench](https://arxiv.org/abs/2610.34717)（10-26）在 Jetson AGX Thor 和 Ryzen AI Max+ PRO 395 上实测 18 个开源 VLA。未优化时延迟从 77 ms 到 6.3 s（Thor）不等，参数量的对数最多只能解释 15% 的延迟方差，决定因素是动作生成方式：少步数流匹配能跟上控制频率，逐 token 解码跟不上。[FlashRT-PAI](https://arxiv.org/abs/2610.24349) 在 Thor 上比官方编译路径快 1.3–3.7 倍，内核已被 LeRobot 采纳；[TRIAGE](https://arxiv.org/abs/2610.34519) 在 AGX Orin 上用 token 复用加剪枝，把 prefill 延迟最多降低 48%。国产机器人计算平台也有了真机数据：[RTPolicy](https://arxiv.org/abs/2610.41625)（10-30，含地瓜机器人作者）在 RDK S600 上 INT16 为 30.35 ms（32.9 Hz），同板 π0.5 只有 3.0 Hz。量化方面，KAIST 的 [SACQ](https://arxiv.org/abs/2610.41408) 把 GR00T N1.7 压到 1.5 bit、1.175 GB，LIBERO 成功率 93.85%（BF16 为 94.10%），但没有边缘设备实测速度。大模型机载方面，斯坦福、伯克利与 NVIDIA 的 [BT-Agent](https://arxiv.org/abs/2610.13862) 在 Spot 的 Jetson Thor 上运行 9B NVFP4 模型；按 273 GB/s 带宽、每 token 约 5 GB 推算，decode 上限约 50 tok/s（推算）。[OpenFlyV2](https://arxiv.org/abs/2610.39287) 在 Orin NX 上以 10 Hz 运行约 1B 的无人机 VLA，[OrbitWeaver](https://arxiv.org/abs/2610.29183) 在两颗低轨卫星上用检查点让 VLM 推理在断电重启后续跑，连续运行 72 小时。

### 常开层、MCU 与可穿戴：语音入口下沉到通用 MCU

常开层本月有两个清晰的信号。一是语音识别进入无 NPU 的 MCU。Lokutor 的 [Oído](https://arxiv.org/abs/2610.13447)（10-09）在 5 美元的 ESP32-S3 上运行 13M 参数 Conformer，LibriSpeech test-clean WER 3.70%，错误比乐鑫 MultiNet7 少 2.3–2.8 倍，但单核实时率 1.97，还达不到实时。[ESP32-P4 流式 ASR](https://arxiv.org/abs/2610.38739)（10-28）把 65.7M 参数模型压到 26.65 MB，用 0.90 s 处理 1.28 s 音频，已经快于实时，作者没有测能耗。高通的[块循环 ASR](https://arxiv.org/abs/2610.37833)（10-27）把 108.9M 编码器折成 14.2M 并恢复 97.4% 精度，但只在 Apple M4 Pro 上测了 DRAM 能耗（降 1.46 倍），没有骁龙可穿戴平台的实测。

二是端侧推理在亚瓦级设备上同样受内存限制。11 月 2 日提交的 [TinyML 内存墙基准](https://arxiv.org/abs/2611.03392)（已核摘要）在 10 款商用设备上实测：Sony IMX500 的传感器内 DSP 每次推理 0.13–0.35 mJ，比 STM32N6 低 1.3–3 倍；四款带 NPU 的器件延迟与权重加激活字节数的相关系数 r ≥ 0.98，与 MAC 数无关。“按字节而非 MAC 算成本”的结论从手机一直成立到 MCU。其他常开层工作：ETH 的 [SIXPPAC](https://arxiv.org/abs/2610.26552) 用 12nm、0.765 mm² 芯片做到 4.18 nJ/inference；[SpikeDuet](https://arxiv.org/abs/2610.24677) 在 EFR32MG24 上让 CPU 与矩阵向量单元协同跑 SNN；港大的 [StickFigure](https://arxiv.org/abs/2610.34130) 在 STM32H753 上只输出骨架，p95 延迟 0.107 s；[PULSE](https://arxiv.org/abs/2610.28081) 在 nRF54L15 上一次本地适应约 43 mJ；GN 的 [FPGA 语音增强](https://arxiv.org/abs/2610.35144)通过结构化稀疏把每帧动态能耗从 83 降到 33 µJ；Sivy 与剑桥的[预测编码唤醒词](https://arxiv.org/abs/2610.41381)让 SRAM 读取减少 33.87%。

### 判断与 11 月观察

本月 arXiv 方向可以归纳为三点判断。第一，手机 NPU 的竞争点正从峰值 TOPS 转向运行时能力：状态复用、待机功耗、能否训练、能否与云端分工，以及向量单元和散热能否撑住多模态智能体的连续推理。4B 级文本步 1.2–1.4 s 已可用，多模态步数秒到数十秒还不可用。第二，在端侧，“每 token 读多少字节”同时决定速度和能耗。服务器上的加速技巧必须在目标设备上重测；能稳定生效的是减少字节的方法（KV 剪枝、低比特、嵌入压缩、无损 KV），会增加读取量的投机解码在 Mac 和手机 NPU 上失效。第三，容量层已进入推理关键路径。PC 侧以“SSD 常驻 + DRAM 缓存”为主（PagedMoE、WorldPager），手机侧开始出现 LPDDR6 挂新型非易失介质（NORmal）和 HBF 两条路线之争，但都还停留在仿真。

11 月值得观察的点：骁龙 8 Elite Gen 5、天玑新平台是否出现针对 softmax 和布局变换的第三方真机复测；NORmal、HBF 这类路线有没有厂商（三星、SK 海力士、长江存储）作者参与的后续工作；11 月 3 日提交、窗口外一天的 [HyPAIC](https://arxiv.org/abs/2611.04144)（个人 AI 电脑用 HBF 跑万亿参数 MoE，仿真）会归入 11 月，是 PC 侧 HBF 的第一篇系统设计；还有高通 AIPC、GenieX 这条“智能体帮开发者上 NPU”的线是否扩展到骁龙手机平台。

## 7. 总结：对端侧智能体意味着什么，以及 11 月盯什么

**对端侧智能体的含义**

1. **智能体循环开始被拆到不同设备和不同层。** Apple 把 Siri AI 拆成“家居设备常开入口 + 户主手机个人上下文 + 私有云兜底”；Google 的 ML Kit 智能体 API 把规划放在设备上、生成可回落云端；Qualcomm 的 GenieX 把工具调用和决策直接接进 NPU 路径。开发者面对的不再是“一个模型跑在一颗 NPU 上”，而是“一个智能体循环跨几层运行”。
2. **评估端侧智能体要算“每步秒数、每步焦耳、待机瓦数”。** 本月论文第一次系统给出这些数字：4B 级文本步约 1.2–1.4 s 已可用，带截图的多模态步要数秒到数十秒，仍不可用；常驻待机功耗可以从 0.76 W 降到 0.22 W。只看 tok/s 会高估多模态 GUI 智能体的可用性。
3. **大模型上设备靠的是“大总参、小激活”的 MoE 加低比特和分层存储。** 在 135–300GB/s 带宽的设备上，这是唯一能实际跑起来的路线；NVIDIA、Apple、Meta 本月配套的本地模型几乎都是这一类。
4. **内存成本决定普及速度。** DRAM 合约价继续上涨、手机与 PC 出货创纪录下滑，中端设备的内存预算被压缩。极低比特量化、闪存卸载、近存/存内计算的商业价值因此上升，但真正量产要到 2027 年。

**11 月观察清单**

- 高通（11-04）、AMD、Arm 财报对端侧 AI 需求的判断；Arm 与高通案的法官裁决。
- 8 Elite Gen 6 / 8 Elite Extreme Gen 6 零售机的第三方 NPU 与 LLM 实测，尤其是 30B MoE 的可用速度；Galaxy S27 芯片分配是否定案。
- M6 MacBook Pro / iMac 与 M5 Max 机型的第三方 MLX/llama.cpp tok/s，验证 M6 decode 只比 M5 快约 10% 的推算。
- 国行 iOS 27.3 测试版中自研模型与千问的本机/云端分流；Gemini Nano 4 的参数量与能效；Play 服务版 LiteRT 的 NPU 支持。
- GenieX 是否公布 Eaglet/MTP 和双 NPU 切分的提速数字。
- MICRO 11-03、11-04 的剩余论文全文数字；ICCAD 2026（11-08~11-12）；IEDM（12 月）前的存算与 3D DRAM 论文摘要。
- Synaptics SR200、Coralboard SR 的整芯片功耗与小模型实测；JEDEC HBF 标准进展；首批 LPDDR6 手机与 Q4 合约价实际涨幅。

> 口径说明：标“官方”的是厂商发布的数字，“媒体实测”和“第三方实测”是独立测试，“爆料”未经确认，“推算”是本文按带宽与每 token 读取字节数等公开参数计算的结果；论文数字除特别注明外均为作者自测或仿真。本月没有新的旗舰手机 SoC 发布；小米玄戒、紫光展锐、Hailo、知存、苹芯本月未查到新品。Tensor G6、Gemini Nano 4 本月没有新的官方参数。MICRO 2026 只计主会首日（11-02），11-03 之后的论文归 11 月。
