# 硬件洞察：端侧 AI 芯片月报（2026-03-27 ~ 2026-04-30）

> **说明：** 本期为 2026-10 回填，规则同周报硬件雷达；lowpower 与 arXiv 两个方向重复收录的 5 篇论文（NVLLM、EdgeCIM、SHIELD、BioTrain、AQPIM）只计一次。
>
> **一句话结论：4 月是“模型交齐、内存卡脖子”的一个月。** 窗口内没有新的手机旗舰 SoC，高通、Apple 都没有发布新芯片。端侧模型和运行时却一次交齐：Gemma 4 E2B/E4B 与 Gemini Nano 4 同源，LiteRT-LM 给出从手机到树莓派的整张实测表。决定能跑多快的仍是内存：QMX、三星量产模型和 CIM 流片芯片都显示 decode 受带宽限制；月底高通、联发科、Apple、恒玄的财报又把内存涨价写进了出货和成本。芯片增量集中在车载（联发科 C-X1、地平线星空）和 LPDDR6-PIM 标准化。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断与时间线；第 1–6 节依次为 高通 / Apple 与 Google / 其他 SoC 与 PC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选；第 7 节总结对端侧智能体的含义和 5 月观察清单。逐条动态见 03-27、04-03、04-10、04-17、04-24 五周首页的“硬件雷达”。

## 0. 总览：4 月的五个判断

**判断一：端侧模型层一次交齐，2B 级多模态模型在手机 GPU 上 decode 50+ tok/s。**

| 发布 | 数字 | 口径 |
|---|---|---|
| [Gemma 4](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)（04-02） | E2B 有效 2.3B、E4B 有效 4.5B，128K 上下文，文本/图像/音频；26B A4B 每 token 激活 3.8B；Apache 2.0 | 官方（模型卡） |
| [LiteRT-LM 端侧实测](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/) | E2B decode：S26 Ultra GPU 约 52、iPhone 17 Pro GPU 约 57、Dragonwing IQ8 NPU 31.7、树莓派 5 CPU 7.6 tok/s；部分设备内存 <1.5GB | 官方（手机数字取自模型卡当前版本） |
| [Gemini Nano 4 预览](https://android-developers.googleblog.com/2026/04/AI-Core-Developer-Preview.html) | 基于 E2B/E4B；比上一代“最高快 4 倍、最多省电 60%” | 官方（未注明对比条件） |
| [Android Studio 本地 Agent](https://android-developers.googleblog.com/2026/04/android-studio-supports-gemma-4-local.html) | E2B 8GB / E4B 12GB / 26B MoE 24GB 总内存，推荐 26B MoE | 官方 |

E2B 在智能体基准 Tau2 上只有 24.5%（E4B 42.2%，模型卡），手机上的多步规划仍偏弱。按 0.8GB 权重、60–85GB/s 带宽推算，E2B 的 decode 上限约 75–105 tok/s，实测利用了五到七成带宽。

**判断二：NPU 和矩阵单元只救 prefill，decode 由带宽决定。**

| 证据 | 数字 | 口径 |
|---|---|---|
| [QMX on llama.cpp](https://www.qualcomm.com/developer/blog/2026/04/llama-models-acceleration-on-cpu-qmx)（04-07） | Q8 TTFT 单线程最高 2.9 倍；decode 4 线程仅 1.05 倍；Q4 数字文中三处不一致 | 官方 |
| [三星 S24/S25 量产部署](https://arxiv.org/abs/2604.18655)（04-20） | 3B INT4 约 19 tok/s，DS2D 自投机后 35–45 tok/s，峰值内存约 2.46GB；1B 在 S24 上 41.32 tok/s | 论文实测（“已量产”为作者自述） |
| IQ8 NPU 对比树莓派 CPU | prefill 约 28 倍，decode 约 4 倍 | 按官方数字推算 |
| [EdgeFlow](https://arxiv.org/abs/2604.09083)（04-10） | 小米 15 Pro 上 8B 冷启动优化后仍 9.1s（7.4s 等闪存），EdgeFlow 最多降 4.07 倍 | 论文实测 |
| [手机 NPU 测试时扩展](https://arxiv.org/abs/2509.23324)（EuroSys，04-28） | 解码时矩阵单元闲置，改做并行采样；GEMM 最高 19.0 倍（算子级），OnePlus 12 解码 3B 约 4.3W | 论文 |

三星 3B INT4 的 19 tok/s 对应约 30GB/s 的有效权重读取（推算）。量产端侧模型仍停在 1B–3B，提速靠投机解码而不是更大的 NPU。

**判断三：内存涨价从预测变成财报里的实绩。**

| 信号 | 数字 | 口径 |
|---|---|---|
| [TrendForce 2Q26](https://www.trendforce.com/presscenter/news/20260331-12995.html)（03-31） | 常规 DRAM 合约价季涨 58–63%，NAND 70–75%，UFS/eMMC 缺口最紧；[笔记本出货](https://www.trendforce.com/presscenter/news/20260330-12992.html)下修至 -14.8% | 第三方预测 |
| [高通 FY26Q2](https://www.qualcomm.com/news/releases/2026/04/qualcomm-announces-second-quarter-fiscal-2026-results)（04-29） | 手机 60.24 亿美元（-13%）；Q3 指引 92–100 亿美元，明确计入内存约束 | 官方 |
| [联发科法说](https://www.mediatek.com/hubfs/MediaTek%20Assets/Pdfs/Quarterly%20Earnings%20Release/2026/Quarterly%20Earnings%20Release-2026Q1/%E8%AA%AA%E6%98%8E%E6%9C%83%E9%80%90%E5%AD%97%E7%A8%BF.pdf)（04-30） | 预计 2026 年全球手机出货下降约 15% | 官方 |
| [Apple 电话会](https://www.macrumors.com/2026/04/30/apple-q2-2026-earnings-call/)（04-30） | 6 月季度内存成本“显著上升”；Mac mini/Studio 因 AI 与智能体需求缺货 | 官方（媒体整理） |
| [恒玄一季报](http://static.cninfo.com.cn/finalpage/2026-04-30/1225258463.PDF) / [Jetson 停产](https://connecttech.com/ftp/pdf/Connect-Tech-Jetson-Lifecycle-Update-and-Planning.pdf) | 恒玄营收 -32.72%；四款 LPDDR4 Jetson 最后采购日 07-01 | 官方 / 合作伙伴转述 |

**判断四：存内计算进入 LPDDR 标准化，但量产的是百万参数模型，LLM 级仍以仿真为主。**

| 工作 | 数字 | 口径 |
|---|---|---|
| [JEDEC LPDDR6 预告](https://www.jedec.org/news/pressreleases/jedec%C2%AE-previews-lpddr6-roadmap-expanding-lpddr-data-centers-and-processing-memory)（04-22） | 新增 x6 子通道，远期 512GB；LPDDR6 PIM 标准“接近完成”，点名边缘推理 | 官方 |
| [炬芯](http://static.cninfo.com.cn/finalpage/2026-03-30/1225049465.PDF) / [安克 Thus](https://www.ifanr.com/1663362) | SRAM-CIM 6.4TOPS/W@INT8 放量；NOR Flash CIM 支持约 4M 参数 | 公司口径 / 媒体转述 |
| [CD-PIM](https://date26.date-conference.com/programme#TS34.6) / [AHASD](https://arxiv.org/abs/2604.25326) / [NVLLM](https://arxiv.org/abs/2604.25699) | LPDDR5-PIM 解码比纯 GPU 快 11.42 倍；PIM 起草 + NPU 验证吞吐 4.2 倍；3D NAND 内算 FFN，30B 比 A800 外存快 16.7–37.9 倍 | 仿真 |
| [RCW-CIM](https://arxiv.org/abs/2604.27384) / [VitaLLM](https://arxiv.org/abs/2604.27396) | 22nm 流片，Llama2-7B INT4 decode 26.87 tok/s；16nm 0.223mm²、65.97mW 跑 BitNet 3B 70.70 tok/s | 论文（VitaLLM 未计外存） |

RCW-CIM 的 26.87 tok/s 约需 94GB/s，已接近双路 DDR5-6400 的理论带宽（推算）：能效可以做上去，生成速度仍被外存卡住。

**判断五：芯片增量在车载和本地智能体平台，手机旗舰只有爆料。**

| 发布 | 数字 | 口径 |
|---|---|---|
| [联发科 C-X1](https://www.mediatek.com/press-room/mediatek-showcases-its-active-intelligent-cockpit-solution-ushering-the-industry-into-new-era-of-ai-defined-vehicles)（04-24） | 3nm，400 TOPS，集成 Blackwell GPU；“带宽需求降至 10%”无基线 | 官方 |
| [地平线星空](https://www.horizon.auto/news/partnership/447)（04-24） | 650 TOPS、273GB/s；7B INT4 decode 上限约 78 tok/s | 媒体口径 / 推算 |
| [Ollama 改用 MLX](https://ollama.com/blog/mlx)（03-30） | Qwen3.5-35B-A3B decode 58 → 112 tok/s，测试芯片未写 | 官方（量化格式前后不同） |
| [高通 OpenClaw 教程](https://www.qualcomm.com/developer/blog/2026/04/install-openclaw-hermes-agent-qualcomm-arduino-rubik-pi-snapdragon-pcs)（04-24） | 编排跑在 4GB 的 Arduino UNO Q，推理在云端或 X Elite PC | 官方 |
| [8 至尊版 Gen 6](https://www.gsmarena.com/even_more_details_about_the_snapdragon_8_elite_gen_6_leak-news-72380.php) / [麒麟 9030S](https://www.ithome.com/0/941/208.htm) | 标准版 2nm、LPDDR5X；麒麟 NPU 图像理解 +200%，无绝对规格 | 爆料 / 官方相对值 |

### 4 月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 03-27 | Galaxy S25 Ultra 8 模型能耗实测；ANVIL 骁龙 NPU 插帧 | 研究 |
| 03-30 | Ollama 0.19 改用 MLX；TrendForce 笔记本出货 -14.8%；炬芯年报；Everysight 眼镜用 Alif E7 | Apple / 内存 / 低功耗 |
| 03-31 | TrendForce：2Q26 DRAM 季涨 58–63% | 内存 |
| 04-02 | Gemma 4、Gemini Nano 4 预览、LiteRT-LM 实测、Android Studio 本地 Gemma 4 | Google |
| 04-07 | 高通 QMX 实测；OpenVINO 2026.1 接入 llama.cpp；AI Hub v0.50 | 软件 |
| 04-08 | 美光投资 SiMa.ai；SHIELD | 产业 / 研究 |
| 04-10 | 高通与 Snap 多年协议；博世 ADAS；EdgeFlow | XR / 车载 / 研究 |
| 04-14~16 | Genio Pro 5100；爆料 8 至尊版 Gen 6 标准版；台积电 Q1 | IoT / 爆料 / 代工 |
| 04-17 | Firebase 端云混合推理 API | Google |
| 04-20 | Pura 90 / 麒麟 9030S、MateBook 14（麒麟 X90）；Srouji 任首席硬件官；CPULLVM 开源；三星多 LoRA 部署、NPUMoE；DATE 2026 开幕 | 移动 SoC / 研究 |
| 04-22 | JEDEC LPDDR6 预告；TPU 8t/8i；Google 称下代 Apple 模型基于 Gemini；台积电技术论坛；安克 Thus；爆料 8 至尊版 Gen 6 或交三星代工 | 内存 / 产业 |
| 04-23 | 英特尔 Q1（客户端 +1%）；乐鑫 ESP-Claw；ParaRNN | PC / MCU / Apple |
| 04-24 | 北京车展：联发科 C-X1、地平线星空；高通 OpenClaw 教程；Galaxy Book6 Edge 泄露；BrainChip 季报 | 车载 / 智能体 |
| 04-27 | NVIDIA 因 LPDDR4 加速停产旧 Jetson | 内存 |
| 04-28 | EuroSys 正会（至 04-30）：手机 NPU 测试时扩展、viNPU；ST BrightSense；NVLLM、AHASD；AI Hub v0.52（Qwen2.5-VL-7B）；爆料 Tensor G6 | 研究 / 低功耗 |
| 04-29 | 高通 FY26Q2；TZ-LLM | 产业 / 研究 |
| 04-30 | Apple、联发科、三星 Q1；恒玄一季报；TrendForce：3nm 产能将超 5/4nm；RCW-CIM、VitaLLM；PRISM | 产业 / 研究 |

## 1. 高通：QMX 实测、AI Hub 迭代与“内存决定手机业务”

### 总览：4月的高通没有新芯片，重点是CPU矩阵扩展、Agent和内存压力

2026年3月27日至4月30日，高通没有发布任何手机、PC或XR新芯片，官方新闻稿里一颗新SoC都没有。这个月的增量来自四个方向。第一，开发者博客首次公开骁龙8至尊版Gen 5 CPU矩阵扩展QMX在llama.cpp上的实测（[04-07](https://www.qualcomm.com/developer/blog/2026/04/llama-models-acceleration-on-cpu-qmx)），这是本月最硬的一组端侧大模型数字。第二，软件栈继续向开源靠拢：AI Hub模型库连发三版、默认运行时升到QAIRT 2.45（[v0.51.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.51.0)），编译器换成开源的CPULLVM（[04-20](https://www.qualcomm.com/developer/blog/2026/04/announcing-an-open-source-llvm-toolchain-for-snapdragon-cpus-mcus)）。第三，高通在官方渠道正式押注开源个人Agent OpenClaw与Hermes（[04-22](https://www.qualcomm.com/news/onq/2026/04/openclaw-ai-agent-orchestration)、[04-24](https://www.qualcomm.com/developer/blog/2026/04/install-openclaw-hermes-agent-qualcomm-arduino-rubik-pi-snapdragon-pcs)）。第四，[FY26第二财季财报](https://www.qualcomm.com/news/releases/2026/04/qualcomm-announces-second-quarter-fiscal-2026-results)（04-29）把“内存供应约束与涨价”直接写进了业绩指引。

整体判断有三点。一是端侧大模型的瓶颈越来越明确地落在内存上：QMX实测显示decode几乎不随算力提升，财报显示内存涨价已经在压低手机出货，爆料中的下一代旗舰也把LPDDR6当作主要卖点。二是高通的Agent叙事在4月仍以“端侧编排、云端推理”为主，官方自己也承认全本地运行只是“可能”。三是高通的增长重心在汽车、IoT和数据中心，手机端侧AI的官方硬指标本月几乎是空白。

本月往前的背景：3月初MWC上高通发布了首个集成NPU的可穿戴平台[Snapdragon Wear Elite](https://www.qualcomm.com/news/onq/2026/03/snapdragon-wear-elite-platform)（3nm，官方称可支持最高约2B参数的端侧模型；3月31日OnQ再次阐述“Ecosystem of You”愿景）。3月9日发布的Arduino VENTUNO Q（媒体称40 TOPS，[GSMArena](https://www.gsmarena.com/arduino_ventuno_q_announced_with_powerful_cpu_and_gpu_40_tops_of_ai_performance_too-news-71872.php)），以及3月23日把XNNPACK移植到Hexagon HVX的[开发者文章](https://www.qualcomm.com/developer/blog/2026/03/bringing-xnnpack-hexagon-npu)，都早于本窗口，这里只作背景。

### 一、手机：QMX实测说明了什么，以及下一代旗舰的爆料

**QMX：CPU上的矩阵单元（04-07，官方实测）。** 骁龙8至尊版Gen 5的Oryon CPU集成了Qualcomm MX矩阵扩展，指令集兼容Arm SME，支持INT8和BF16，按tile执行GEMM/GEMV。高通在同一颗芯片上对比QMX与纯NEON，用llama.cpp + KleidiAI（开关GGML_KLEIDIAI_SME）测了Gemma 270M、Gemma 1B、Llama 1B、Gemma 4B、Llama 3B、Llama 8B共6个GGUF模型，prompt和生成长度均为128 token，CPU锁频（大核4394MHz、小核3953MHz）。

结果（官方口径）：Q8模型单线程首token时延（TTFT）最高缩短到1/2.9，4线程约1/2.0；decode单线程最高快约1.5倍，4线程只快1.05倍。Q4模型表格给出TTFT最高2.07倍（单线程）和1.77倍（4线程），decode约1.25倍和1.21倍。需要注意，同一篇文章的小结写Q4为1.52倍和约1.34倍，结论段又写1.5倍，三处不一致，引用时应以表格为准。文章没有给功耗，也没有在正文给出tok/s绝对值。

这组数据的价值在于它清楚划出了算力和带宽的分界。prefill是矩阵乘矩阵，算力受限，QMX收益最大；decode是矩阵乘向量，每生成一个token都要把全部权重读一遍，很快就受内存带宽限制，所以Q4模型的decode几乎不变。高通在文末自己列出的下一步也是decode侧的内存优化（权重打包、预取、cache友好布局）。推算来看，Llama 8B Q4权重约4.5–5GB，即使按50–70GB/s的可用带宽算，decode上限也只有10–15 tok/s左右（推算，带宽为假设值）。对Agent负载来说，工具调用和多轮上下文让prefill占比更高，QMX缩短首token等待是实打实的体验改进；但想让手机端生成更快，只能靠更高带宽或更激进的量化。

**骁龙8至尊版Gen 6爆料（04-15，爆料）。** 数码闲聊站在微博披露、[GSMArena转述](https://www.gsmarena.com/even_more_details_about_the_snapdragon_8_elite_gen_6_leak-news-72380.php)：标准版SM8950采用台积电2nm，新Oryon CPU为2+3+3、共享16MB L2，Adreno 845（6 slice、12MB图形缓存、6MB系统级缓存），支持LPDDR5X和UFS 5.0，相比Pro版削减了“部分缓存与外设规格”。窗口前一天（03-25）的[另一则爆料](https://www.gsmarena.com/snapdragon_8_elite_gen_6_8_elite_gen_6_pro_specifications_leak-news-72097.php)称Pro版SM8975配Adreno 850、18MB GMEM、8MB LLC，内存可选四通道24bit LPDDR6或四通道16bit LPDDR5X。NPU规格两次爆料都没有提。

如果属实，同代旗舰内部会按内存代际分层。推算：Pro版96bit LPDDR6按10.7Gbps计约128GB/s，标准版64bit LPDDR5X按同速率约85GB/s，8B INT4模型的decode上限分别约28和19 tok/s（推算，速率为假设）。结合QMX的结论，这可能比NPU的TOPS提升更直接地决定下一代旗舰的端侧生成速度。

**代工：可能回到三星（04-22，爆料）。** 韩国媒体报道、[GSMArena转述](https://www.gsmarena.com/qualcomms_snapdragon_8_elite_gen_6_might_be_made_by_samsung-news-72482.php)，安蒙访韩与三星讨论2nm代工，8至尊版Gen 6有可能部分交由三星制造，这会是2022年以来首次。它与“标准版用台积电2nm”的爆料并存，较可能的情况是双源代工，有待9月发布确认。

### 二、PC：X2系列进入铺货期，带宽决定本地模型上限

本月高通PC侧没有新芯片，X2 Plus（1月CES）和X2 Elite/Extreme（2025年9月）进入大规模铺货。4月30日高通官方的[Snapdragon Insiders文章](https://www.qualcomm.com/snapdragon/news/explore-the-lineup-of-new-next-gen-pcs-powered-by-snapdragon-x2-)汇总了华硕Zenbook A16（X2 Elite Extreme）、ProArt PZ14、惠普OmniBook Ultra、联想Yoga Slim 7x等新机。4月24日，德国零售商提前上架了[三星Galaxy Book6 Edge](https://www.gsmarena.com/samsung_galaxy_book6_edge_with_snapdragon_x2_elite_chip_leaks-news-72538.php)（零售商泄露、媒体整理）：X2E-88-100，18核，LPDDR5X 128bit、152GB/s，NPU 80 TOPS（INT8），整机16GB/512GB，售价2200欧元。

这款泄露机型给了一个具体的推算基准：152GB/s约为手机旗舰64bit LPDDR5X的1.8倍，8B INT4模型decode上限约34 tok/s、14B INT4约19 tok/s（推算）。但16GB内存扣掉系统占用后，只能放下约8–14B INT4的模型，30B级MoE即使激活参数小、总权重也装不下。也就是说，X2系列PC跑本地Agent的约束首先是内存容量，其次才是带宽和NPU。

高通OnQ文章还提到，Claude Cowork已可在骁龙X2 Elite Extreme笔记本上运行，用于把本地文件整理成幻灯片等多步任务。这类Agent的规划仍在云端模型上，PC端负责本地文件访问和执行。

### 三、Agent：OpenClaw上了官方渠道，但推理主要还在云端

4月22日的OnQ文章[《Intelligence everywhere》](https://www.qualcomm.com/news/onq/2026/04/openclaw-ai-agent-orchestration)是高通第一次在官方渠道系统讨论开源个人Agent。作者把OpenClaw部署在一块59美元的Arduino UNO Q上，用于每日新闻简报、邮件整理、物流跟踪，并称OpenClaw代表AI从“对话”转向“执行”。文章同时明确说，完全本地运行OpenClaw及其调用的模型“是可能的”，但多数配置是编排层跑在设备上、重推理交给云端模型。

两天后的[开发者教程](https://www.qualcomm.com/developer/blog/2026/04/install-openclaw-hermes-agent-qualcomm-arduino-rubik-pi-snapdragon-pcs)给出了硬件梯度：Arduino UNO Q（QRB2210，4GB内存、32GB存储，跑完整Debian，装完仍有10GB以上空间）作为常驻编排节点；Rubik Pi 3（Dragonwing QCS6490）应对更高负载；需要本地模型时，把LLM服务跑在骁龙X Elite笔记本上。教程强调用独立开发板做“硬件沙箱”，只给Agent受限凭据，与主力电脑的数据隔离。

这个月高通的Agent叙事因此可以概括为：常驻、编排和执行在端侧，大模型推理在PC或云端。它与财报里“AI Agent正在重塑我们所有平台的路线图”的表态一致，但距离“手机上全本地Agent闭环”还有明显距离。

### 四、软件栈与工具链：QAIRT 2.45、7B多模态与开源编译器

**AI Hub模型库（04-07 ~ 04-28，官方）。** [v0.50.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.50.0)新增Qwen3-4B-Instruct-2507；v0.50.1修复Llama 3.2 3B Instruct SSD（自投机解码）在Windows上的兼容性；[v0.51.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.51.0)把默认QAIRT升到2.45，Genie LLM运行时同步升级，Whisper、MeloTTS、Opus可导出到新的Voice AI运行时，同时移除ONNX Runtime GenAI运行时；[v0.52.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.52.0)新增Qwen2.5-VL-7B视觉语言模型（提供预编译资产）并为LLM/VLM加入Genie App脚本。三个版本把库里的生成式模型从3B文本推到7B图文，语音链路也有了独立运行时。不足之处是release notes没有给出tok/s、上下文长度和功耗。

**CPULLVM（04-20，官方）。** 高通用开源的CPULLVM取代闭源的Snapdragon LLVM Compiler，覆盖Arm/AArch64与RISC-V 32/64位的裸机、Zephyr和Linux，首版基于LLVM 22.1.0（3月17日发布），之后跟随上游3月和9月版本，所有新特性先进llvm.org。它和3月把XNNPACK移植到Hexagon HVX、4月在llama.cpp上启用QMX一起，构成高通“开源优先”的一条线：让第三方不经过专有SDK也能用上骁龙的CPU和NPU加速。

### 五、XR、可穿戴与车载

**Snap Specs（04-10，官方）。** 高通与Snap子公司Specs Inc.签署[多年战略协议](https://www.qualcomm.com/news/releases/2026/04/qualcomm-and-snap-expand-strategic-collaboration-to-advance-inte)，未来多代Specs独立透视AR眼镜都用骁龙XR平台，消费版2026年内上市。新闻稿没有给芯片型号、NPU算力和功耗。可穿戴侧本窗口唯一的端侧模型硬指标仍是3月发布的Wear Elite“最高约2B参数”。

**博世ADAS（04-10，官方）。** 博世基于骁龙座舱平台的车载计算机累计交付超过1000万台；双方[合作扩展到ADAS](https://www.qualcomm.com/news/releases/2026/04/bosch-and-qualcomm-expand-collaboration-to-strategic-adas-soluti)，新项目基于Snapdragon Ride，座舱和ADAS融合方案基于Ride Flex单芯片（最高ASIL-D），已在东亚拿到多个定点，首批车型2028年上路。财报中汽车收入13.26亿美元、同比增长38%，创季度新高。

### 六、财报与产业：内存写进了官方指引

FY26第二财季（截至3月29日）营收105.99亿美元，同比下降3%；QCT手机收入60.24亿美元，同比下降13%；汽车13.26亿美元（+38%），IoT 17.26亿美元（+9%）。第三财季指引为营收92–100亿美元、QCT 79–85亿美元，官方明确说明指引计入了“内存供应约束和相关涨价对多家手机OEM需求的影响”，并预计中国客户的手机收入在第三财季见底（[财报PDF](https://s204.q4cdn.com/645488518/files/doc_financials/2026/q2/FY2026-2nd-Quarter-Earnings-Release.pdf)）。CEO称与一家头部云厂商的定制数据中心芯片合作将于年内首批出货，4月30日高通另发通告称6月24日投资者日将介绍数据中心、物理AI、面向Agent负载的个人AI和6G。

对端侧AI来说，这是本月最值得记住的一条：本地大模型需要更大内存，而据媒体报道，内存厂正把产能转向数据中心用的HBM，手机用内存因此供应偏紧、价格上涨。OEM在中低端机型上压缩内存配置的动力变强，端侧大模型下放到中端机的节奏可能因此放慢（推断）。

### 七、高通AI研究院论文

本窗口内未能核实到以高通AI研究院为主的新arXiv论文。高通官网论文目录未更新到2026年，arXiv检索页在本次调研期间持续返回429限流，因此这部分留给arXiv方向的子agent补查，这里不做结论。

### 小结：4月对端侧智能体意味着什么

4月的高通没有新芯片，但给出了几条清楚的信号。其一，QMX实测证明CPU矩阵单元可以把首token时延缩短2–3倍，但decode被内存带宽卡住，这和财报里的内存压力、爆料中下一代旗舰的LPDDR6指向同一个结论：2026年端侧大模型的上限由内存容量和带宽决定，TOPS已经不是主要矛盾。其二，高通的Agent路线在4月是“端侧常驻编排 + 云端推理”，OpenClaw跑在4GB的Arduino板上，本地模型交给X系列PC；手机上的全本地Agent闭环，官方没有给出任何数字。其三，软件栈继续开源化（QAIRT 2.45、7B VLM、Voice AI运行时、CPULLVM、XNNPACK和llama.cpp路径），降低了第三方在骁龙上部署模型的门槛。

接下来值得关注：5月是否发布中端芯片并补上NPU数字；Wear Elite和Specs终端何时给出眼镜/手表端的实测；8至尊版Gen 6的LPDDR6和NPU规格能否得到官方确认；以及6月投资者日上“面向Agent负载的个人AI”具体指什么。

## 2. Apple 与 Google：Gemma 4 与 Gemini Nano 4、Ollama 改用 MLX

### 总览：Google 交了一整套端侧模型，Apple 的端侧 AI 体现在缺货的 Mac 上

在 2026-03-27 到 04-30 这段时间里，Apple 和 Google 在端侧 AI 上的分工很清楚。**Google 在 4 月 2 日一天之内发布了端侧需要的整套东西**：开放模型 [Gemma 4](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)、系统级模型 [Gemini Nano 4 预览](https://android-developers.googleblog.com/2026/04/AI-Core-Developer-Preview.html)、运行时 [LiteRT-LM 与 AI Edge Gallery 的 Agent Skills](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)，以及 [Android Studio 本地 Agent 编码](https://android-developers.googleblog.com/2026/04/android-studio-supports-gemma-4-local.html)。两周后又推出[端云混合推理 API](https://android-developers.googleblog.com/2026/04/Hybrid-inference-and-new-AI-models-are-coming-to-Android.html)。**Apple 本月没有发布新芯片或新端侧模型**，3 月初的 MacBook Neo、M5 MacBook Air 等新品都在窗口之前。Apple 本月的端侧 AI 动态主要有三类：[Ollama 改用 MLX](https://ollama.com/blog/mlx) 后 Mac 本地推理明显提速，[Apple 财报](https://www.macrumors.com/2026/04/30/apple-q2-2026-earnings-call/)承认 Mac mini 和 Mac Studio 因“AI 与智能体工具”需求缺货、内存成本将显著上升，以及 Google 在 Cloud Next 台上确认[下一代 Apple 基础模型基于 Gemini](https://9to5mac.com/2026/04/22/google-teases-gemini-powered-siri-upgrade-during-cloud-next-keynote/)。

本期回溯的 03-06、03-13、03-20、03-27 四周此前没有硬件雷达条目，以下内容全部来自本次回填的 13 条新条目和若干背景材料。全月可以归纳为三个判断：

1. **2B 级多模态模型在手机上 decode 进入 50 tok/s 档，内存压到 1.5GB 以内。** Gemma 4 E2B 在 Galaxy S26 Ultra GPU 上约 52 tok/s、iPhone 17 Pro GPU 约 57 tok/s，在高通 Dragonwing IQ8 NPU 上 31.7 tok/s，在树莓派 5 CPU 上 7.6 tok/s。
2. **系统模型与开放模型合流。** Gemini Nano 4 直接基于 Gemma 4 E2B/E4B，“为 Gemma 4 写的代码会自动在 Nano 4 设备上运行”。
3. **端侧 AI 需求开始反作用于硬件供给。** 本地跑 30B 级 MoE 的需求让 32–64GB 内存的 Mac 台式机缺货；同时内存涨价、台积电先进制程被 AI 芯片挤占，Apple 预计 6 月季度内存成本“显著上升”。

### 一、Gemma 4：端侧档位、能力与“有效参数”

[Gemma 4](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) 于 4 月 2 日发布（[Gemma 发布记录](https://ai.google.dev/gemma/docs/releases)写的是 3 月 31 日上线），共四个尺寸，许可证改为 Apache 2.0。根据[模型卡](https://ai.google.dev/gemma/docs/core/model_card_4)：

| 型号 | 参数 | 上下文 | 模态 | 定位 |
|---|---|---|---|---|
| E2B | 有效 2.3B（含嵌入 5.1B） | 128K | 文本/图像/音频 | 手机、IoT |
| E4B | 有效 4.5B（含嵌入 8B） | 128K | 文本/图像/音频 | 旗舰手机、PC |
| 26B A4B | 总 25.2B，激活 3.8B（128 选 8 专家 + 1 共享） | 256K | 文本/图像 | PC、工作站 |
| 31B | 30.7B 稠密 | 256K | 文本/图像 | 工作站、云 |

端侧两款的能力（模型卡，指令版）：E4B 的 MMLU Pro 69.4%、GPQA Diamond 58.6%、LiveCodeBench v6 52.0%；E2B 分别为 60.0%、43.4%、44.0%。智能体基准 Tau2 上 E4B 42.2%、E2B 只有 24.5%，说明 2B 级模型做多步工具调用仍然偏弱，端侧智能体的“规划”环节仍可能需要 E4B 或更大的模型。

“有效参数”是理解端侧占用的关键：E2B 含嵌入 5.1B，但逐层嵌入可以内存映射、不必常驻，所以实际常驻内存远小于 5B 参数对应的大小。Gemma 4 的 MTP 草稿模型权重于 4 月 16 日上线（[发布记录](https://ai.google.dev/gemma/docs/releases)），正式介绍和运行时支持在 5 月，归入 5 月月报。

### 二、端侧实测：LiteRT-LM 给出的一整张表

[Google AI Edge 博客](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)和 [LiteRT-LM 模型卡](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm)给出了本月最完整的端侧数字（Gemma 4 E2B，1024 prefill + 256 decode）：

| 设备 | 后端 | prefill tok/s | decode tok/s | 口径 |
|---|---|---|---|---|
| Galaxy S26 Ultra | GPU | 约 3,808 | 约 52 | 官方模型卡（当前版本） |
| Galaxy S26 Ultra | CPU | 约 557 | 约 47 | 官方模型卡 |
| iPhone 17 Pro | GPU | 约 2,878 | 约 57 | 官方模型卡 |
| 高通 Dragonwing IQ8 | NPU | 3,747 | 31.7 | 官方，4096 上下文 |
| 树莓派 5 | CPU | 133 | 7.6 | 官方博客 |
| MacBook Pro M4 Max | GPU | 约 7,835 | 约 160 | 官方模型卡 |

几个要点：

- **内存**：2/4/8bit 混合量化，纯文本权重最低约 0.8GB，约 1.12GB 嵌入参数走内存映射，官方称部分设备上内存占用低于 1.5GB。
- **NPU 的收益主要在 prefill**：IQ8 NPU 的 prefill 是树莓派 CPU 的约 28 倍，decode 只有约 4 倍。decode 受内存带宽限制，NPU 算力优势很难体现在出字速度上。
- **带宽推算（标为推算）**：每 token 读约 0.8GB 权重，旗舰手机 LPDDR5X 按 60–85GB/s 估，decode 上限约 75–105 tok/s；实测 52–57 tok/s，带宽利用率约五到七成。要再快，需要 MTP 一类投机解码（5 月落地）。
- **智能体**：AI Edge Gallery 新增 Agent Skills，官方称 2 个技能共 4,000 输入 token 不到 3 秒处理完（设备未注明），对应 prefill 超过 1,300 tok/s，这是端侧智能体读工具说明时的关键指标。
- 次日 [LiteRT-LM v0.10.1](https://github.com/google-ai-edge/LiteRT-LM/releases/tag/v0.10.1) 发布 Gemma 4 支持、Hugging Face 模型自动转换、基于 LiteRT 的 KV Cache 和投机解码。

存疑：手机端 GPU 数字来自模型卡当前版本，4 月初是否已经是这些数字无法确认；[树莓派官方实测](https://www.raspberrypi.com/news/mastering-edge-ai-on-raspberry-pi-with-litert-and-gemma/)在 8GB 版 Pi 5 上用 QAT 模型得到 prefill 99、decode 9 tok/s、峰值内存 1432MB，设置与 Google 的数字不同。

### 三、Android：Gemini Nano 4 与端云混合

[AICore 开发者预览](https://android-developers.googleblog.com/2026/04/AI-Core-Developer-Preview.html)让开发者提前测试 Gemini Nano 4。[9to5Google](https://9to5google.com/2026/04/02/gemini-nano-4-android/) 披露预览中有两档：Nano 4 Fast（基于 E2B）和 Nano 4 Full（基于 E4B），均标注“TPU”。官方口径是比上一代“最高快 4 倍、最多省电 60%”，E2B 比 E4B 快 3 倍；但没有说明对比对象和测试设备。预览支持 Google、联发科、高通三家的加速器，其他设备回落 CPU。工具调用、结构化输出、系统提示词和思考模式将在预览期内加入。[同日的 Android 博客](https://android-developers.googleblog.com/2026/04/gemma-4-new-standard-for-local-agentic-intelligence.html)称 Gemini Nano 已覆盖超过 1.4 亿台设备，Nano 4 将在今年晚些时候随新旗舰机发布。

4 月 17 日的[混合推理 API](https://android-developers.googleblog.com/2026/04/Hybrid-inference-and-new-AI-models-are-coming-to-Android.html)（实验性）用一个 Firebase 接口在端侧 Nano 和云端 Gemini 之间切换，提供“优先端侧”和“优先云端”两种模式。但端侧目前只支持单轮文本或单图输入，路由也只看“有没有 Nano、在不在线”。端侧负责低延迟和隐私，复杂任务交给云端，这是 Google 目前给开发者的现实方案。

PC 侧，[Android Studio](https://android-developers.googleblog.com/2026/04/android-studio-supports-gemma-4-local.html) 给出了本地 Agent 编码的内存门槛：E2B 8GB、E4B 12GB、26B MoE 24GB（总内存，含 IDE），并推荐最低配置机器用 26B MoE。原因是带宽：26B MoE 每 token 只读 3.8B 激活参数，按 4bit 约 2GB（推算），比 31B 稠密少读约 8 倍。

XR 方面，[Android XR 4 月更新](https://blog.google/products-and-platforms/platforms/android/android-xr-immersive-features-update-april-2026/)（04-07）为 Galaxy XR 带来实验性的自动空间化（把普通应用、视频转成 3D）和墙面固定应用等功能，但没有披露端侧模型或芯片信息。眼镜方面只有爆料：Samsung One UI 9 代码中出现带显示屏的 Android XR 眼镜代号 “Haean”（[9to5Google，04-24](https://9to5google.com/2026/04/24/samsungs-delayed-android-xr-glasses-the-ones-with-a-display-showed-up-in-one-ui-9/)）。

### 四、Apple：MLX 成为 Mac 本地推理的默认后端

[Ollama 0.19 预览](https://ollama.com/blog/mlx)（03-30）在 Apple Silicon 上改用 MLX 作为推理后端。在 Qwen3.5-35B-A3B 上，prefill 从 1154 提升到 1810 tok/s，decode 从 58 提升到 112 tok/s；换用 int4 后官方称可达 1851 / 134 tok/s。需要注意，前后版本的量化格式不同（Q4_K_M 对 NVFP4），所以这不是纯粹的后端对比。官方要求统一内存大于 32GB，并点名 M5 系列 GPU 内的神经加速器。**推算**：112 tok/s × 每 token 约 1.7–2GB，相当于约 190–220GB/s 的有效带宽，高于基础款 M5 的 153GB/s，测试机很可能是 M5 Pro 或 M5 Max（官方未写）。

[MLX v0.31.2](https://github.com/ml-explore/mlx/releases/tag/v0.31.2)（04-22）允许多个线程各自独立调用 MLX，配套 [mlx-lm v0.31.3](https://github.com/ml-explore/mlx-lm/releases/tag/v0.31.3) 加入线程本地生成流。这让一个本地服务可以同时跑多个会话或智能体。此后 MLX 到 7 月才有下一个版本。

Apple ML Research 本月有两篇文章。[ICLR 2026 页面](https://machinelearning.apple.com/research/iclr-2026)（04-22）列出展台演示：M5 Max MacBook Pro 在 Xcode 中用 MLX 完全本地运行量化的前沿编码模型，iPad Pro（M5）运行 SHARP 单图生成 3D 场景，均未给出速度数字。[ParaRNN](https://machinelearning.apple.com/research/large-scale-rnns)（04-23）介绍 ICLR 口头报告论文：用牛顿迭代 + 并行归约让非线性 RNN 沿序列并行训练，提速 665 倍，训练出约 7B 的 ParaGRU/ParaLSTM，困惑度 9.16–9.19，优于同规模 Transformer（9.55），略逊 Mamba2（8.62）。RNN 推理时每 token 耗时恒定、没有随上下文增长的 KV Cache，对长对话端侧智能体有吸引力，但文章没有给出端侧实测。

### 五、Apple：内存、制程与组织调整

[Apple 2026 财年二季度财报](https://www.apple.com/newsroom/2026/04/apple-reports-second-quarter-results/)（04-30）营收 1112 亿美元、同比增长 17%。[电话会](https://www.macrumors.com/2026/04/30/apple-q2-2026-earnings-call/)上有三条与端侧 AI 硬件直接相关：

- Cook 预计 6 月季度内存成本“显著上升”，此后影响持续加大；
- iPhone 供给受限“主要由” A19 系列所用先进制程的可得性造成，台积电同一制程同时供应 AI 芯片；
- Mac mini 和 Mac Studio “是出色的 AI 和智能体工具平台”，需求超预期，供需平衡需要数月。

4 月里缺货信号逐步加重：04-03 M3 Ultra Mac Studio 的 256GB 配置交期 4–5 个月（512GB 配置 3 月已下架，[9to5Mac](https://9to5mac.com/2026/04/03/mac-studio-delivery-4-5-months-out-for-top-ram-after-apple-dropped-512gb-option/)）；04-22 599 美元基础款 Mac mini 售罄。Bloomberg 爆料新一代 Mac Studio 可能推迟到 10 月（[经 9to5Mac，04-19](https://9to5mac.com/2026/04/19/new-mac-studio-may-not-arrive-until-october/)）。

组织上，Apple 芯片负责人 Johny Srouji 于 04-20 [升任首席硬件官](https://www.apple.com/newsroom/2026/04/johny-srouji-named-apples-chief-hardware-officer/)，同时统管硬件工程和硬件技术；次日 Apple 宣布 John Ternus 将于 9 月 1 日接任 CEO。芯片和整机由同一人负责后，内存、带宽和散热的取舍会更直接地服务于端侧模型。

模型侧，Google Cloud CEO Kurian 在 Cloud Next 上说，Google 作为“首选云服务商”与 Apple 合作开发“基于 Gemini 技术的下一代 Apple 基础模型”，用于今年晚些时候的个性化 Siri。Bloomberg 爆料的 iOS 27 Siri 能力包括单条指令处理多项请求、相机 Siri 模式。端侧和云端的分工本月没有一手信息。可穿戴方面只有爆料：Apple AI 眼镜在测试至少四种镜框（[04-12](https://9to5mac.com/2026/04/12/apple-exploring-four-different-styles-for-its-upcoming-smart-glasses-using-premium-materials/)），AR 眼镜目标 2028–2030 年（[04-27](https://9to5mac.com/2026/04/27/major-new-apple-products-get-fresh-updates-ar-glasses-and-ipad-fold/)），都没有芯片信息。

### 六、Google 芯片：云端 TPU 8 分家，Tensor G6 只有 CPU 爆料

[第八代 TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/)（04-22）首次分成训练用 8t 和推理用 8i。8i 每芯片配 288GB HBM 和 384MB 片上 SRAM（上一代 3 倍），ICI 带宽 19.2Tb/s，推理性价比提升 80%；两款芯片能效比均比 Ironwood 最高提升 2 倍。8i 用大 SRAM 把活跃工作集留在片上，和端侧 NPU 依赖片上缓存缓解带宽瓶颈是同一思路。04-29 Pichai 宣布 TPU 将卖给部分客户放进自有数据中心。

手机侧的 [Tensor G6 爆料](https://9to5google.com/2026/04/28/google-pixel-11-tensor-g6-cpu-gpu-leak/)（04-28，可信度低到中）只涉及 CPU 和 GPU：1×C1-Ultra 4.11GHz + 4×C1-Pro 3.38GHz + 2×C1-Pro 2.65GHz，GPU 为 PowerVR CXTP-48-1536，几乎不升级。决定 Gemini Nano 4 体验的 TPU 和内存配置都没有信息。

### 七、两家对比：同一个月，两种端侧路线

| 维度 | Google | Apple |
|---|---|---|
| 端侧模型 | Gemma 4 E2B/E4B 开放权重，Gemini Nano 4 同源（预览） | 本月无新端侧模型发布；下一代基础模型基于 Gemini（Google 口径） |
| 运行时 | LiteRT-LM v0.10.1、AI Edge Gallery Agent Skills、ML Kit Prompt API | MLX v0.31.2；第三方 Ollama 改用 MLX |
| 公开实测 | 手机 GPU decode 52–57 tok/s，IQ8 NPU 31.7 tok/s，树莓派 7.6 tok/s | 第三方：Mac 上 35B-A3B MoE decode 112 tok/s（芯片未写） |
| 芯片 | TPU 8t/8i（云端）；Tensor G6 仅爆料 | 无新芯片；首席硬件官由芯片负责人担任 |
| 内存信号 | AICore 预览未写门槛；Android Studio 本地编码 24GB | Mac mini/Studio 因 AI 需求缺货，内存成本将显著上升 |
| 端云分工 | 混合推理 API，端侧单轮、云端兜底 | Siri 依赖云端 Gemini，端侧分工未公开 |

从这张表看，Google 的优势在“可复现”：模型权重、运行时、测试设置和设备数字都公开，开发者可以按同一张表估算自己的设备能跑多快。Apple 的优势在“装机硬件”：统一内存和高带宽让 Mac 成为本地大模型最常用的平台之一，但 Apple 自己本月几乎没有公开端侧模型的数字，开发者看到的性能主要来自 Ollama、MLX 社区等第三方。对端侧智能体开发者来说，4 月的实用结论是：手机上用 2B–4B 级模型做感知、改写和简单工具调用，复杂规划交给 PC 上的 30B 级 MoE 或云端；而 PC 这一档的内存，正在变得又贵又难买。

### 结论：端侧智能体的软件已经就绪，瓶颈转到内存

这五周的材料指向同一个结论。**模型和运行时层面**，Google 已经给出了可量化的端侧方案：2B 级多模态模型在手机上 decode 50+ tok/s、内存低于 1.5GB，系统模型与开放权重同源，工具调用和思考模式在路线图上。**硬件层面的约束是内存而不是算力**：NPU 主要加速 prefill，decode 受带宽限制；本地 30B 级 MoE 需要 24–32GB 以上内存，而这一档的 Mac 正在缺货、内存正在涨价。**两家都把端云混合作为现实路线**：Google 提供了混合推理 API，Apple 的下一代 Siri 依赖云端 Gemini。

后续值得跟踪：Gemini Nano 4 正式版的内存门槛和工具调用何时开放；Tensor G6 的 TPU 规格；Apple 在 WWDC（6 月 8 日）是否公布新一代端侧基础模型的规模、量化方式以及与 Gemini 的关系；以及内存涨价是否会让 2026 年下半年的端侧 AI 设备降低内存配置。

## 3. 其他 SoC 与 PC：联发科与台积电看淡手机、车展上的大算力

### 总览：芯片发布少，产业约束多

2026-03-27 ~ 04-30 这段时间，“其他 SoC、PC 与产业”方向几乎没有手机旗舰芯片发布。最具体的增量来自三处：华为 4 月 20 日发布 Pura 90 系列，首发[麒麟 9030S](https://www.ithome.com/0/941/208.htm)；台积电在北美技术论坛公布 [A13、N2U 与车规 N2A](https://pr.tsmc.com/english/news/3302)；北京车展上，[联发科 C-X1](https://www.mediatek.com/press-room/mediatek-showcases-its-active-intelligent-cockpit-solution-ushering-the-industry-into-new-era-of-ai-defined-vehicles)（3nm、400 TOPS）和[地平线星空](https://www.horizon.auto/news/partnership/447)（650 TOPS）把“整车智能体”做成了芯片卖点。

更值得重视的是财报和研究机构给出的约束信号。联发科在 [4 月 30 日法说会](https://www.mediatek.com/hubfs/MediaTek%20Assets/Pdfs/Quarterly%20Earnings%20Release/2026/Quarterly%20Earnings%20Release-2026Q1/%E8%AA%AA%E6%98%8E%E6%9C%83%E9%80%90%E5%AD%97%E7%A8%BF.pdf)上预计今年全球智能手机出货下降约 15%，并明确说原因是“内存供给问题”。TrendForce 3 月底预计 [2Q26 DRAM 合约价环比再涨 58~63%](https://www.trendforce.com/presscenter/news/20260331-12995.html)，并把 [2026 年笔记本出货下修到 -14.8%](https://www.trendforce.com/presscenter/news/20260330-12992.html)。英特尔[客户端营收仅增 1%](https://www.intc.com/news-events/press-releases/detail/1767/intel-reports-first-quarter-2026-financial-results)，三星和台积电则因 AI 服务器需求创下纪录。

这个月可以用一句话概括：**端侧 AI 的硬件已经铺开，但成本被数据中心挤高，增长动力转到了汽车和机器人。**

| 日期 | 事件 | 关键数字 | 口径 |
|---|---|---|---|
| 03-30 | TrendForce 下修笔记本出货 | 2026 年 -14.8%（原 -9.2%） | 研究机构 |
| 03-31 | TrendForce 2Q26 内存合约价 | DRAM +58~63%，NAND +70~75% | 研究机构 |
| 04-07 | OpenVINO 2026.1 | llama.cpp 后端可调度英特尔 NPU（预览） | 官方 |
| 04-14 | 联发科 Genio Pro 5100 | 3nm，50+ TOPS，最高 7B LLM | 官方 |
| 04-16 | 台积电 Q1 | 3nm 占晶圆营收 25%，毛利率 66.2% | 官方 |
| 04-20 | 华为麒麟 9030S / MateBook 14 | NPU 图像理解 +200%；麒麟 X90 笔记本 24GB 起 | 官方经媒体 |
| 04-22 | 台积电技术论坛 | N2U 功耗 -8~10%，A13 面积 -6% | 官方 |
| 04-23 | 英特尔 Q1 | 客户端 77 亿美元，+1% | 官方 |
| 04-24 | 联发科 C-X1 / 地平线星空 | 400 TOPS / 650 TOPS、273 GB/s | 官方 / 媒体 |
| 04-30 | 联发科、三星 Q1 | 手机出货预计 -15%；三星二代 2nm 移动工艺 H2 爬坡 | 官方 |

### 一、手机 SoC：华为只公布 AI ISP 数字，联发科与三星押注 2nm

**华为麒麟 9030S。** Pura 90 Pro / Pro Max 首发麒麟 9030S，华为只给了相对数字：NPU 图像理解能力提升 200%，AI ISP 色彩引擎提升 43%，长焦视频清晰度提升 110%，整机性能提升 25%。制程、CPU 和 NPU 的绝对规格一律未披露。标准版没有在发布会上公布芯片，[IT之家从官网查到](https://www.ithome.com/0/941/280.htm)它用的是麒麟 9010S，同一代机型因此拆成两档芯片。全系内存从 12GB 起步，“超空间内存”宣称 12GB 能达到 16GB 的后台保活效果。华为这一代的 AI 投入集中在影像和视觉理解上，没有公布本地 LLM 的规模和速度。同场还发布了搭载麒麟 X90 的 [MateBook 14 鸿蒙版](https://www.ithome.com/0/941/273.htm)，内存 24GB 起步、最高 32GB，以大内存弥补鸿蒙 PC 的生态劣势。

**联发科：2nm 旗舰三季度末上市。** 法说会上，联发科确认首颗 2nm 旗舰 SoC 已拿下多个设计订单，搭载机型三季度末上市。一季度手机营收环比下降 17%，占比降到 49%，二季度还会继续下滑。CEO 被问到智能体是否需要更大的 NPU 时，回答这是从 AI 眼镜、手机、IoT、PC 到汽车的多平台问题：手机功耗预算约 8W，车载可到 40~80W，而且“智能体时代 CPU 正在复兴”。这与英特尔 CEO 把增长押在“智能体需要更多 CPU”上的说法一致。TrendForce [4 月 1 日的排名](https://www.trendforce.com/presscenter/news/20260401-12996.html)显示，联发科 2025 年营收 191 亿美元（+16%），其中天玑 9500 出货带动全年营收创新高。

**三星 Exynos：下半年争取旗舰订单。** [三星 Q1 财报](https://news.samsung.com/global/samsung-electronics-announces-first-quarter-2026-results)显示，System LSI 因 SoC 销量增加而改善，下半年目标是“拿下旗舰 SoC 设计订单”。代工部门计划下半年开始量产爬坡第二代 2nm 移动工艺，1.4nm 开发按计划推进。两条信息放在一起，指向 Exynos 2700 这一代，但机型归属只是媒体推测。

### 二、PC：AI PC 铺开了，出货却在收缩

英特尔一季度营收 136 亿美元（+7%），但客户端只有 77 亿美元（+1%），增长来自数据中心（+22%）和代工（+16%）。季度内英特尔推出酷睿 Ultra 200S Plus / 200HX Plus，并用酷睿 Series 3（原代号 Wildcat Lake）把 18A 带进主流价位。软件侧更值得关注的是 [OpenVINO 2026.1](https://github.com/openvinotoolkit/openvino/releases/tag/2026.1.0)：它预览了 llama.cpp 的 OpenVINO 后端，GGUF 模型因此可以直接调度英特尔 CPU、GPU 和 NPU，已验证的模型覆盖 1B~7B。此前 PC NPU 的最大问题是主流本地推理工具用不上，这一步补上了入口，不过目前仍是预览版。

需求端数字很直接。TrendForce 把 2026 年笔记本出货预测从 -9.2% 下修到 -14.8%，原因包括内存涨价、CPU 调价，以及先进制程和封装产能被 AI 计算优先占用。只有 Apple 预计逆势增长 7.7%，靠的是低价 MacBook Neo 和统一的内存配置。大内存本来是 AI PC 跑本地模型的前提，现在却成了最贵的部件。AMD 在本窗口内没有新的客户端芯片发布（锐龙 AI 400 扩展在 3 月 2 日，窗口外）；NVIDIA 的 Arm PC 芯片在 4 月仍停留在爆料阶段。

### 三、车载与机器人：带宽和功耗最宽裕的端侧

北京车展是这个月最集中的端侧 AI 芯片发布场合。

- **联发科 C-X1**：3nm，最高 400 TOPS，集成 NVIDIA Blackwell GPU 并支持 CUDA。官方称大模型解码优化把带宽需求降到 10%（未说明基线），MPS 让多模型调度吞吐最高提升 50%，还预告了 2nm 座舱芯片。
- **地平线星空 Starry**：[量子位](https://www.qbitai.com/2026/04/408031.html)报道其规格为 5nm 车规工艺、650 TOPS、内存带宽 273 GB/s，单芯片同时跑座舱和辅助驾驶，官方称单车硬件成本可降 1500~4000 元。按 273 GB/s 推算，7B INT4 模型的 decode 上限约 78 tok/s，14B 约 39 tok/s（推算，没有计入智驾并发）。650 TOPS 的算力远超带宽能支撑的大模型解码需求，带宽调度会是舱驾一芯的新瓶颈。
- **联发科 Genio Pro 5100**（04-14）：3nm，50+ TOPS，官方称可在本地运行最高 7B 的 LLM，支持 16 路摄像头和 ROS2，面向机器人与工业终端。

台积电的论坛也在呼应这条线：车规纳米片工艺 N2A 比 N3A 同功耗快 15~20%，N3A 今年量产；联发科也在法说会上表示要带汽车行业迁移到 2nm。

### 四、代工与内存：先进制程和内存都被 AI 服务器抢走

**台积电。** Q1 营收约 359 亿美元（+40.6%），毛利率 66.2%，3nm 占晶圆营收 25%。[媒体报道](https://apps.digitimes.com/topic/tsmc_1q26_earnings_call/a001711.html)称 2nm 已进入量产，全年资本开支 520~560 亿美元。技术论坛上，N2U 相对 N2P 只多出 3~4% 速度或 8~10% 功耗收益，A13 相对 A14 面积节省 6%，2nm 之后单代工艺红利已降到个位数。面向 AI 眼镜的 N16HV 让近眼显示芯片面积减少 40%、功耗降低超过 20%，是本月少有的直接作用于可穿戴续航的数字。

**3nm 拥挤。** TrendForce [4 月 30 日](https://www.trendforce.com/presscenter/news/20260430-13028.html)判断，3nm 产能年底将超过 5/4nm。由于高端手机和 PC 处理器尚未大规模转向 2nm，它们会在 3nm 上与 AI 加速器争产能。

**内存。** 3 月 31 日的预测是 DRAM 合约价环比再涨 58~63%、NAND 涨 70~75%，其中 eMMC/UFS 缺口最紧，手机品牌可能从二季度开始减产。三星 Q1 存储业务营收和利润都创新高，产能优先给了 HBM4、SOCAMM2 等 AI 产品。5 月 14 日 TrendForce 又给出 LPDDR5X +78~83% 的细分数字（已收入 5 月月报），可以看作这一轮涨价的延续。

### 五、能跑多大模型：本月数字的口径核对

这个月厂商给出的“模型规模”数字很少，而且口径各不相同，需要分开看：

- **Genio Pro 5100 的“最高 7B”** 是官方口径，但没有说明精度、内存容量和 tok/s。按 INT4 计算，7B 的权重约 3.5GB；如果配的是常见的 LPDDR5X 带宽，decode 上限大约在每秒数十 token（推算）。实际速度要等第三方实测。
- **地平线星空的 273 GB/s** 是本月唯一公开的内存带宽数字，可以直接拿来推算：7B INT4 约 78 tok/s，14B INT4 约 39 tok/s。不过这颗芯片要同时承担智驾感知，留给大模型的带宽会明显少于理论值。
- **联发科 C-X1 的“带宽需求降至 10%”** 没有给基线，可能来自投机解码、稀疏化或 KV cache 压缩。在拿到技术细节之前，不能把它换算成 10 倍速度。
- **华为麒麟 9030S 的“NPU 图像理解 +200%”** 没有说明测试模型和对比对象，只能看作厂商口径的相对数字。
- **OpenVINO 2026.1 的 1B~7B** 指的是“已验证可以跑”，不代表 NPU 路径更快；英特尔没有给 NPU 的 tok/s。

总的来说，本月没有一个能在手机或 PC 上与 5 月 Gemma 4、ExecuTorch 实测数字直接对比的新数据点。增量主要在平台能力和产业约束上，而不是可验证的推理性能。

### 背景：窗口前后的相关事件

- 3 月 24 日 Arm 在 Arm Everywhere 活动上发布首颗自研芯片 [AGI CPU](https://datacenterknowledge.com/data-center-chips/arm-enters-data-center-chip-fray-with-agi-cpu-for-ai-infrastructure)（数据中心，Meta 为首个客户），早于本窗口，标志 Arm 从 IP 授权转向卖芯片。4 月 28 日的 [Arm Performix](https://newsroom.arm.com/news/announcing-arm-performix) 是面向云端 Arm CPU 的免费性能分析工具，支持 MCP，和端侧关系不大。
- 紫光展锐、瑞芯微、小米玄戒在窗口内没有查到官方芯片发布。媒体报道展锐 4 月中旬披露了 IPO 辅导进展，瑞芯微 RK182X 协处理器早于窗口推出。

### 总结：对端侧智能体意味着什么

1. **成本先于算力成为约束。** 联发科、TrendForce、三星三方的口径一致：2026 年手机和 PC 出货收缩，根源是内存被 AI 服务器抢走，而不是端侧 AI 需求不足。端侧模型在短期内会继续向“更小、更省内存”的方向优化。
2. **增量平台转向汽车和机器人。** C-X1、星空和 Genio Pro 5100 都在本月把 400~650 TOPS、7B 级本地模型和“整车智能体”写进规格。这些平台的功耗预算比手机大 5~10 倍，最先跑起多模型并发的端侧智能体。
3. **工艺红利变薄，软件入口变得更重要。** N2U 只有个位数收益，所以端侧能效的提升更多要靠 NPU 软件栈和内存带宽。OpenVINO 接入 llama.cpp 正是这一思路。

下月观察：联发科 2nm 旗舰的具体 NPU 规格、Computex 上的 Arm PC 芯片、TrendForce 对 3Q26 手机内存价格的预测，以及华为麒麟 9030S 是否有第三方拆解。

## 4. 低功耗、存内计算与内存：LPDDR6 PIM 标准化与涨价传导

### 总览：4 月的主角是内存，不是 NPU

2026-03-27 ~ 04-30 这个窗口里，低功耗、存内计算与内存方向没有出现旗舰级新芯片，此前各周的硬件雷达在本方向也没有已收条目，本节完全基于本次回填的条目。综合来看，这五周可以概括为三句话：

1. **内存从“成本项”变成了端侧 AI 的硬约束**：TrendForce 预测 2Q26 常规 DRAM 合约价再涨 58–63%、NAND 涨 70–75%；可穿戴主控厂恒玄一季度营收同比下降 32.72%，财报直接把原因写成“上游存储芯片涨价”；NVIDIA 因 LPDDR4 供给与价格问题，加速停产四款旧 Jetson 模组。
2. **存内计算在两个层面同时推进**：标准层面，JEDEC 宣布 LPDDR6 PIM 标准“接近完成”；产品层面，炬芯的 SRAM 存算音频芯片出货攀升，安克自研的 NOR Flash 存算耳机芯片 Thus 即将量产。不过，量产的存算芯片跑的都是百万参数级小模型。
3. **常开感知的功耗优化，从 NPU 前移到传感器和协处理器**：ST 的新图像传感器做到“检测后再唤醒”，BrainChip 把神经形态芯片用到雷达识别上，ETH 系初创公司 Mosaic SoC 为 AR 眼镜做专用空间感知芯片。

### 一、内存：标准在扩张，供给在收紧

**标准侧。** 4 月 22 日 [JEDEC 预告 LPDDR6 下一版](https://www.jedec.org/news/pressreleases/jedec%C2%AE-previews-lpddr6-roadmap-expanding-lpddr-data-centers-and-processing-memory)，主要有三项内容：接口从 x16 改为非二进制的 x24，新增 x12、x6 子通道，让每个封装能堆更多 die；远期密度到 512GB；同时制定 LPDDR6 SOCAMM2 模组标准和 LPDDR6 PIM 标准。新版扩展的主要动机写明是“数据中心与加速计算”，PIM 则同时点名了“边缘推理”。JEDEC 4 月 7 日公布的 [5 月 Mobile/Client/Edge 论坛议程](https://www.jedec.org/news/pressreleases/jedec%C2%AE-announces-may-2026-forums-focused-next-generation-memory-ai-server-cloud)里专门有一场“LPDDR6-PIM 的上市之路”。速率方面，新闻稿没有给数字。[SK hynix 3 月 10 日](https://news.skhynix.com/en/1c-lpddr6-development-2026/)（早于本窗口，作背景）公布的 1c LPDDR6 速率超过 10.7Gbps，数据处理速度比 LPDDR5X 高 33%，功耗低 20% 以上，计划下半年供货。

**供给侧，数字很极端。** [TrendForce 3 月 31 日](https://www.trendforce.com/presscenter/news/20260331-12995.html)预测 2Q26 常规 DRAM 合约价环比上涨 58–63%，NAND 上涨 70–75%，其中 UFS/eMMC 的缺口在所有品类中最紧，因为它和企业级 SSD 共用产能、利润却更低。[4 月 7 日的报告](https://www.trendforce.com/presscenter/news/20260407-13001.html)显示，3 月 4Gb 以下的小容量 DDR4 月涨超过 20%，DDR3/DDR2 上涨 20–40%。这些小容量颗粒正是机顶盒、IoT 和边缘模组的常用料。

下游的反应在 4 月底集中出现：

- [恒玄科技一季报](http://static.cninfo.com.cn/finalpage/2026-04-30/1225258463.PDF)：营收 6.69 亿元，同比下降 32.72%，归母净利润下降 53.26%，原因写明是“上游存储芯片涨价、国补政策退坡”。恒玄是耳机、手表和 AI 眼镜主控的主要供应商之一，这是本窗口里内存涨价传导到可穿戴芯片最直接的一手证据。
- [Connect Tech 4 月 27 日通知](https://connecttech.com/ftp/pdf/Connect-Tech-Jetson-Lifecycle-Update-and-Planning.pdf)：NVIDIA 称 LPDDR4 模组“供给与价格日益受限”，因此加速 Jetson TX2 NX、TX2i、AGX Xavier、Xavier NX 的停产，最后采购日为 7 月 1 日。这是内存短缺第一次直接改写主流边缘 AI 模组的生命周期。
- [炬芯一季报](http://static.cninfo.com.cn/finalpage/2026-04-29/1225234095.PDF)：营收同比增长 23.74%，但为应对“关键原材料价格预期上行和产能风险”主动备货，经营现金流转为负数。
- [美光 4 月 8 日战略投资 SiMa.ai](https://sima.ai/press-release/sima-ai-strategic-investment-from-micron-to-scale-physical-ai/)，Modalix 平台集成美光 LPDDR5X。SiMa.ai CEO 的原话是“物理 AI 对内存的要求极高”。内存原厂入股下游边缘芯片公司，有锁定供给的意味（推断）。

**能跑多大模型，仍由带宽决定。** 以 3B 参数、INT4 量化为例，每生成一个 token 要读约 1.5GB 权重。手机常见的 64-bit LPDDR5X-8533 带宽约 68GB/s，decode 上限约 45 tok/s（推算，未计 KV 和激活读取）。LPDDR6 的单针速率提升有限，更大的变量是 PIM：如果把 GEMV 搬进内存，就不再需要每个 token 把权重搬一遍。

### 二、存内计算：标准化起步，量产的仍是小模型

**量产侧。** [炬芯 2025 年年报](http://static.cninfo.com.cn/finalpage/2026-03-30/1225049465.PDF)（3 月 30 日）给出了国内 SRAM-CIM 量产最完整的一组数据：营收 9.22 亿元，同比增长 41.50%；存内计算芯片 ATS323X、ATS362X 出货持续攀升，已用于无线麦克风、电竞耳机和 Party 音箱；NPU 单核 100GOPS，能效 6.4TOPS/W@INT8（公司口径）。第二代存内计算 IP 的目标是单核算力倍增并支持 Transformer。安克在 4 月 22 日的技术沟通会上（[爱范儿报道](https://www.ifanr.com/1663362)）披露了 Thus 芯片：基于 NOR Flash 做存算一体，原生支持约 400 万参数模型，内部测试的 AI 峰值算力是上一代旗舰耳机芯片的 150 倍，后来在 5 月 22 日随 Liberty 5 Pro 上市。两家的共同点是：存算一体已在毫瓦级音频 AI 上实现商业化，但模型规模在百万参数量级，和端侧 LLM 相差三到四个数量级。知存、后摩、苹芯、九天睿芯在窗口内没有找到可核实的新品发布。

**学术侧：目标转向 LLM decode，但都是仿真结果。**

| 工作 | v1 日期 | 介质 | 关键数字 | 口径 |
|---|---|---|---|---|
| [NVLLM（东南大学）](https://arxiv.org/abs/2604.25699) | 04-28 | 3D NAND 内算 FFN | 30B 模型，比 A800 外存推理快 16.7–37.9 倍，CMOS 面积开销 2.7% | 架构仿真，v2 注明 DAC 2026 |
| [EdgeCIM（KAUST/UCI）](https://arxiv.org/abs/2604.11512) | 04-13 | 65nm 数字 SRAM-CIM | 0.5B–4B 模型，INT4，平均 336 tok/s、173 tok/J | 仿真，片外按 16 通道 LPDDR5X 建模 |
| [AQPIM（东京科学大学）](https://arxiv.org/abs/2604.18137) | 04-20 | DRAM-PIM | 在 PIM 内对 KV 做乘积量化，比 SOTA PIM 快 3.4 倍 | HPCA 2026 |
| [SHIELD（NUS）](https://arxiv.org/abs/2604.07396) | 04-08 | 片上 eDRAM | 按 BF16 比特分段跳过刷新，刷新能耗降 35% | AICAS 2026 |

这几项工作的共同判断是：端侧 decode 受内存限制，计算要靠近权重。NVLLM 用闪存容量替代 DRAM，思路和 SanDisk/SK hynix 的 HBF 接近，但需要 NAND 和逻辑晶圆键合。EdgeCIM 的优势很大程度来自 16 通道内存的假设，手机通常只有 4 个 16-bit 通道，落地前需要重新评估。

### 三、常开 AI、MCU 与眼镜：功耗优化前移到传感器

- **传感器端**：[ST VD55G4/VD65G4](https://newsroom.st.com/media-center/press-item.html/p4772.html)（4 月 28 日）是本窗口最对题的低功耗新品。全局快门，在约 800×700、10fps 下功耗最高比传统方案低 10 倍；内置“检测后唤醒”模式，可直连 MCU，面向可穿戴和 AR/VR。这意味着常开视觉的大部分时间可以不唤醒 NPU。
- **神经形态**：[BrainChip 雷达参考平台](https://www.edge-ai-vision.com/2026/04/brainchip-unveils-radar-reference-platform-to-bridge-the-identification-gap-in-edge-ai/)（4 月 6 日）用 AKD1500 加旭化成雷达模块做微多普勒识别，没有给出功耗数字。[季报](https://announcements.asx.com.au/asxpdf/20260424/pdf/06ytg6cfvrv13j.pdf)显示 AKD1500 首批约 7 万颗，7 月交付；AKD2500 将采用台积电 12nm；单季客户现金流入只有 70 万美元。
- **眼镜**：[Alif 官方博客](https://alifsemi.com/edge-ai-meets-wearables-inside-everysight-maverick-smart-glasses-powered-by-alif-ensemble-e7/)披露 Everysight Maverick 用 Ensemble E7（双 M55、双 Ethos-U55、双 A32），显示开启续航 8 小时以上。[Mosaic SoC](https://www.sovereignmagazine.com/article/mosaic-soc-edge-ai-chip-ar-glasses) 拿到 380 万美元种子前融资，做 PULP 系 RISC-V 空间感知芯片（媒体口径，功耗为亚瓦级）。恒玄年报引用 IDC 数据：2026 年全球智能眼镜出货将超过 2,368.7 万台，其中端侧支持 AI 的占比超过 30%。
- **MCU 智能体**：[乐鑫 ESP-Claw](https://www.cnx-software.com/2026/04/23/espressif-systems-esp-claw-framework-builds-local-ai-agents-for-esp32-devices/)（4 月 23 日）让 ESP32-S3（8MB Flash + 8MB PSRAM）同时充当 MCP 服务端和客户端，在本地保存记忆、执行 Lua 规则，但大模型推理调用云端。本质上是让 MCU 成为智能体的执行端。
- **训练下沉**：[BioTrain](https://arxiv.org/abs/2604.13359) 在 GAP9 上以不到 50mW 的功耗、0.67MB 内存完成全网络微调（实测），可穿戴设备的个性化可以完全留在本地。
- **边缘加速器**：[DEEPX 与现代汽车集团 Robotics LAB](https://kyodonewsprwire.jp/release/202604217790)（4 月 21 日）围绕 DX-M2 合作开发机器人算力平台。新闻稿没有规格；CES 期间的媒体口径是约 80 TOPS、5W 以下、三星 2nm。Edge AI and Vision Alliance 4 月公布的年度产品奖中，SiMa.ai Modalix SoM 和 Expedera Origin Evolution NPU IP 获奖。

### 结语：下半年要盯的四件事

本窗口最重要的变化不在算力，而在内存。“装得下、读得动、买得到”取代 TOPS，成为端侧 AI 硬件的首要约束；存内计算则一边进入 LPDDR 标准化，一边在毫瓦级音频芯片上放量。接下来值得跟踪：

1. LPDDR6 PIM 标准的正式文本，以及是否有手机 SoC 宣布支持；
2. 内存涨价会不会让 AI 眼镜和可穿戴的出货节奏再推迟一个季度；
3. 炬芯二代 CIM 能否真正跑 Transformer，并给出 tok/s 级别的数据；
4. NAND 内计算或 HBF 能否从仿真走到原型。

**存疑点**：安克 Thus 的工艺和能效、DEEPX DX-M2 的规格与量产时间、Mosaic SoC 的功耗，都还没有一手数字；Jetson 停产的时间表来自合作伙伴转述，可能与 NVIDIA 生命周期页不一致。

## 5. 顶会论文：EuroSys 与 DATE 上的手机 NPU 与 TEE

**判断：** 3/27–4/30 这个窗口里没有 ISSCC、ISCA、MICRO 这类芯片或体系结构旗舰会议，端侧相关的论文集中在 4 月下旬的几场中型会议：[DATE 2026](https://date26.date-conference.com/programme)（维罗纳，4/20–22）、[EuroSys 2026](https://2026.eurosys.org/preliminary-program.html)（爱丁堡，4/27 研讨会，4/28–30 正会）、[ISPASS 2026](https://ispass.org/ispass2026/program.php)（首尔，4/26 教程，4/27–28 正会），以及电路方向的 [COOL Chips 29](https://www.coolchips.org/archive/2026/)（东京，4/15–17）和 CICC 2026（西雅图，4/19–22）。本月的信号很清楚：**端侧大模型研究的重心从「芯片能不能跑」转到了「手机已有的 NPU、内存和安全硬件怎么用足」。** EuroSys 上有三篇论文直接在商用手机 SoC 或开发板上做实测，主题分别是 NPU 闲置算力、TrustZone 保护模型、重排序器内存。DATE 上的存内/近存计算论文则大多以 LPDDR5、3D DRAM、MRAM 为载体，目标都是解码阶段的带宽墙。本节新收 11 条（EuroSys 4 条、DATE 7 条）。3/6–3/27 各周硬件雷达没有收录顶会条目，本节是这段时间顶会方向的首次汇总。

### 会期核对

| 会议 | 2026 会期 | 与端侧相关的看点 |
|---|---|---|
| COOL Chips 29 | 4/15–17，东京 | KAIST 低比特 LLM 存算加速器、EdgeCortix 与 SK hynix 主题演讲 |
| CICC 2026 | 4/19–22（含研讨会至 4/23），西雅图 | 4/21 第 15 场机器学习加速器专场、边缘系统安全论坛 |
| DATE 2026 | 4/20–22，维罗纳 | 端侧 LLM 的 PIM/近存、三值模型、极端边缘训练 |
| ISPASS 2026 | 4/26–28，首尔 | 边缘 CPU 小模型特征分析、1.58-bit 查表加速器 |
| EuroSys 2026 | 4/27–30，爱丁堡 | 手机 NPU、TrustZone、端侧检索、MCU 模型更新 |

窗口前后：ASPLOS 2026 会期为 3/22–26（据 2 月节会期核对），在窗口开始前结束，MLSys 2026 在 5/18–22（[官方日期页](https://mlsys.org/Conferences/2026/Dates)），ISCA、VLSI 在 6 月，都不在本窗口。日期取法：EuroSys 按官方程序里论文所在专场的日期，DATE 按程序页各技术专场的日期，均为宣讲日。

### 一、EuroSys：在真实手机硬件上找空间

EuroSys 今年专门设了「端侧与联邦学习」（4/28）和「边缘计算、IoT 与嵌入式 AI」（4/30）两个专场，最有分量的三篇都给出了真机数字。

**手机 NPU 的闲置算力。** 清华、中科大和微软亚洲研究院的 [Scaling LLM Test-Time Compute with Mobile NPU on Smartphones](https://arxiv.org/abs/2509.23324) 指出，手机 NPU 的矩阵单元按大 tile 设计，而 LLM 解码时 GEMM 退化为 GEMV，大部分矩阵算力闲置。作者把这部分算力用来并行采样，做 Best-of-N 和步级 beam search，让 1B–3B 模型逼近更大模型的准确率。为此他们直接给 Hexagon NPU 的 HVX/HMX 写内核：用对齐 HMX tile 的分组量化绕开 QNN 只支持逐通道量化的限制（论文举例：Llama3.2-1B 在 QNN W4A16 下 MATH500 只有 2.1 分，AWQ 分组量化为 15.9 分），用查表替代 Softmax 和反量化。论文报告混合精度 GEMM 最高提速 19.0 倍、Softmax 最高 2.2 倍，测试机为骁龙 8 Gen 2、8 Gen 3、8 Elite 三代 OnePlus 手机，OnePlus 12 解码 Qwen2.5-3B 时整机功耗约 4.3W。19 倍是算子级对比，不能直接读成端到端 tok/s。

**用 TrustZone 保护端侧模型。** 上海交大 IPADS 的 [TZ-LLM](https://arxiv.org/abs/2511.13717) 关心的是另一件事：模型权重部署到用户设备后很容易被提取。它把推理放进 TrustZone，并用两项设计控制代价。一是利用推理访存顺序确定的特点，边算边预取、解密参数；二是在 TEE 里只放最小的 NPU 数据面驱动，让 NPU 在两个世界之间分时共享。在 RK3588 开发板（16GB LPDDR4X）上，TZ-LLM 跑通了 8-bit Llama-3-8B，TTFT 比未优化的 TEE 基线低 76.1%–90.9%；与不做保护的方案相比，TTFT 仍多出 5.2%–28.3%，解码速度只慢 1.3%–4.9%。

**端侧检索与记忆组件。** 上海交大与华为的 [PRISM](https://arxiv.org/abs/2510.15620) 优化的是 RAG 和智能体记忆里常被忽视的一环：交叉编码重排序器。作者观察到 top-K 选择只需要相对排名，而排名在中间层就基本稳定，因此可以逐层剪掉落选候选，再配合层流式加载和嵌入表缓存。在 Apple M2 Mac mini 和 RTX 5070 笔记本上评测 0.6B–8B 重排序模型，微基准延迟最多降低 89.2%，峰值内存最多降低 91.3%；在三个真实应用里，延迟降低 11.6%–51.0%。

**其他值得记一笔的 EuroSys 论文。** 延世大学的 [viNPU](https://doi.org/10.1145/3767295.3803619) 优化手机 NPU 上的 ViT 推理。全文本次未能打开，作者履历称在 Galaxy S22/S25 上平均提速 11.5 倍，这个数字没有与论文核对，只能当线索。另有几篇只看到程序页标题、没有核对内容，不单列条目：UC Berkeley 的 Efficient ML Model Updates for Deeply Embedded Microcontrollers、乌普萨拉大学的 Neuro-C: Neural Inference Shaped by Hardware Limits、西安交大的稀疏激活 LLM 端侧联邦微调，以及中科院软件所面向电脑操作智能体的「LLM 友好 OS 接口」。

### 二、DATE：存内与近存计算瞄准解码带宽

DATE 2026 有一个专场直接叫「AI inference and learning at the edge」（TS04），存内计算和新型存储专场里也有多篇以端侧 LLM 为目标。共同点是：大多数是架构模拟或单元级评估，还没有流片实测。

**LPDDR5 存内计算。** 南京大学、鲁汶大学与中国移动研究院的 [CD-PIM](https://date26.date-conference.com/programme#TS34.6) 用分段全局位线把 LPDDR5 每个 bank 拆成 4 个伪 bank 来提升内部带宽，再让 GEMV 与 GEMM 交错执行。单 batch 下，它相比纯 GPU 基线平均提速 11.42 倍，相比现有 PIM 设计平均提速 4.25 倍。同一团队的 [MoE 调度框架](https://date26.date-conference.com/programme#TS01.7) 研究把 MoE 专家卸载到近数据处理单元，端到端延迟平均提速 2.41 倍。两篇合起来，可以看出国内团队在系统地做「LPDDR/NDP + MoE」的端侧路线。

**芯粒近存跑多模态模型。** UCSD 的 [CHIME](https://date26.date-conference.com/programme#TS35.4) 让单片 3D DRAM 芯粒负责注意力和 KV cache，RRAM 芯粒负责存权重。在 FastVLM 与 MobileVLM（0.6B–3B）上，它的能效为 116.5–266.5 token/J，对照的 Jetson Orin NX 为 0.7–1.1 token/J。需要注意，CHIME 一侧是模拟，Jetson 一侧是实机，两边口径不同。

**三值模型两条路。** UC Irvine 的 [T-SAR](https://date26.date-conference.com/programme#TS19.5) 走 CPU 路线：把 SIMD 寄存器堆改造成寄存器内查找表，只增加 1.4% 面积和 3.2% 功耗，能效最高达到 Jetson AGX Orin 的 2.5–4.9 倍。高丽大学的 [HINT](https://date26.date-conference.com/programme#TS35.7) 走存算路线：用 SRAM-MRAM 混合三值位单元提高密度，在 BitNet b1.58（700M）上能效最高提升 2.67 倍。

**极端边缘的训练与算子。** ETH Zurich 与博洛尼亚大学的 [TrainDeeploy](https://date26.date-conference.com/programme#TS04.3) 在 RISC-V 超低功耗 SoC 上首次端到端微调完整 Transformer（CCT，0.28M 参数），端侧 LoRA 让动态内存减少 23%。密歇根大学、布朗大学与 Google 的 [FLARE](https://date26.date-conference.com/programme#TS34.5) 用 ReLU 注意力加精简版 FIRE 位置编码替换 Softmax，在定制硬件上能耗比 Softmax 单元低 600 倍（单元级对比）。

DATE 上还有几篇不直接以端侧为目标、但值得留意的工作，只记标题：北大的 ACES 用芯粒架构加速智能体 LLM 负载，上海交大、清华与港科大的 Endor 用近存架构加速 LLM 推理，以及中科院计算所的 3D 混合键合 NPU 方案 3D-Flow。

### 三、电路与性能分析会议：只有标题级信息

以下会议本次只核对了程序和标题，没有拿到论文数字，因此不单列条目：

- **COOL Chips 29（4/15）：** KAIST Hoi-Jun Yoo 团队发表 MicroXPU，标题为 Energy-Efficient Low-bit LLM Accelerator with Microscaling Format-Tailored Digital Compute-in-Memory Macro，即面向 MX 微缩放格式的数字存算 LLM 加速器（见 [会议论文集目录](https://www.proceedings.com/content/086/086328webtoc.pdf)）。同批作者还有两篇 3D 高斯泼溅建图处理器（COOL-Splat 等）。主题演讲包括 EdgeCortix 的可编程动态神经加速器 DNA-X，以及 SK hynix 的「从云到端的 AI 内存子系统」。
- **CICC 2026（4/21 机器学习加速器专场）：** 港科大计算机体系结构组（作者含 F. Tu）的 D2CIM 是 28nm 数字存算宏，面向基于 FlashMLA 的 LLM 解码，标题给出 53.3 TFLOPS/W（见 [课题组论文列表](https://computer-arch.hkust.edu.hk/publication)）。
- **ISPASS 2026（4/27–28）：** 值得关注的有三篇。多伦多大学与富士通的 HeadSkip 分析小语言模型在边缘 CPU 上的表现；鲁汶大学 Verhelst 组的 1.58-bit LLM 查表加速器生成与探索获最佳论文提名；Harvard 与 Meta 的 The xPU-athalon 量化比较各类 AI 加速器。

### 小结

把这一个月的论文放在一起看，有三点判断：

1. **手机 NPU 的瓶颈在软件。** 测试时扩展那篇论文显示解码时矩阵单元大量闲置，viNPU 的线索显示 ViT 数据流还有数量级的优化空间，两者都需要绕开厂商闭源栈直接写内核。高通 Hexagon 成了学术界的默认实验平台。
2. **端侧 LLM 的系统问题已经扩展到安全、检索、记忆。** TZ-LLM 和 PRISM 说明，端侧智能体要落地，除了生成 tok/s，还要解决模型权重保护和检索组件的内存占用，而且这些问题已经能在 RK3588、M2 这类现成硬件上给出实测答案。
3. **存内/近存计算论文很多，但大多是模拟。** DATE 上 CD-PIM、CHIME、HINT 报出的十倍乃至百倍收益都来自模拟或单元级评估，与 2 月 ISSCC 的流片数字（μJ/token 级）不在同一可信度层级，阅读时要区分口径。

下一批可对照的流片数据要等 6 月的 VLSI 与 ISCA。

## 6. arXiv 精选：三星量产多 LoRA、NPUMoE 与冷启动

### 总览：四月 arXiv 端侧硬件论文的三条主线

2026-03-27 至 04-30 这段时间，arXiv 上与端侧 AI 硬件和系统相关的论文可以归为三条主线。第一，**手机和 Mac 上的真机数据变多了**：三星第一次披露了在 Galaxy S24/S25 的高通 NPU 上量产部署 1B/3B 模型的逐项延迟；复旦在小米 15 Pro 上拆解了 8B 模型的冷启动；还有一篇在 Galaxy S25 Ultra 上测了 8 个模型的能耗。第二，**瓶颈从算力转向“内存装不下、闪存读不快”**：冷启动受闪存带宽限制，长上下文受 KV 容量限制，解码受 DRAM 带宽限制，于是出现了在闪存里算 FFN、在 PIM 里压缩 KV、把 KV 直写 NVMe 等方案。第三，**专用芯片围绕“三值权重 + 存内计算”收敛**：阳明交大在 4 月 30 日同时放出 16nm 三值加速器和 22nm 数字 CIM 芯片，鲁汶大学给三值查表加速器做了统一的设计空间。

需要说明：此前各周的硬件雷达（03-06、03-13、03-20、03-27 四周）在 arXiv 方向都没有收录条目，所以本节内容全部来自本次回填，日期一律按 arXiv v1 提交日（UTC）计。部分论文的 v2 在 5~10 月更新，文中数字取自当前 HTML 版本，会单独注明。

### 一、手机：量产数字与冷启动

本月最有分量的一手数据来自三星。三星班加罗尔研究院和水原总部在 4 月 20 日提交的 [ACL 2026 论文](https://arxiv.org/abs/2604.18655) 中，给出了 LLaMA 结构多语言基础模型在 Galaxy S24（SM8650）和 S25（SM8750）高通 NPU 上的完整部署方案，并写明该方案“已在 Galaxy S25 系列真实部署”。具体数字如下：1B 模型在 S24 上逐 token 24.19ms，即 41.32 token/s；3B INT4 模型在 S25 Ultra 上不投机时约 19 token/s，用无草稿模型的自投机解码 DS2D 后升到 35~45 token/s，prefill 约 209ms，峰值内存约 2.46GB。工程上有两个值得借鉴的做法：一是 LoRA 权重作为计算图输入，一张冻结图服务多个任务，2 任务模型从 894MB 降到 686MB；二是把多头注意力拆成单头、把线性层改写成 1×1 卷积，以适配 NPU 的卷积核。这说明量产端侧模型的规模仍停在 1B~3B，提速主要靠解码算法。

复旦的 [EdgeFlow](https://arxiv.org/abs/2604.09083)（04-10）关注的是另一个常被忽略的体验问题：冷启动。在小米 15 Pro（骁龙 8 至尊版、16GB）上，llm.npu 跑 Llama3 8B 的冷启动最长 51.2s；物化计算图并让加载与计算重叠后仍要 9.1s，其中 7.4s 是等权重从闪存加载的流水线气泡。EdgeFlow 在 NPU 原生数据类型的约束下按通道重要性分配位宽，再用 SIMD 友好的打包格式把解包开销压到 0.65s 以内，冷启动 TTFT 较 llama.cpp、MNN、llm.npu 最多降 4.07 倍，解码速度不受影响。端侧智能体会被系统反复回收内存，冷启动时间直接决定“随叫随到”的体验。

能耗方面，那不勒斯大学和阿姆斯特丹自由大学在 03-27 提交的[实测论文](https://arxiv.org/abs/2603.26603)用 llama.cpp 在 Galaxy S25 Ultra 上测了 0.5B~9B 的 8 个模型，每组重复 30 次。结论有两条：一是重要性感知的 IQ4_XS 量化能降峰值内存，但不省电、也不提速，续航主要取决于模型架构；二是 MoE 模型 OLMoE-1B-7B 的能耗与 1B~2B 稠密模型同档。单次推理能耗方面，Gemma-2-9B 常超过 300J，Qwen2-0.5B 约 50J，作者推荐 Qwen2.5-3B 作为平衡点。

还有一篇是围绕 NPU 能力重新设计模型的例子：[ANVIL](https://arxiv.org/abs/2603.26835)（03-27）指出光流插帧模型 95% 的周期耗在内存受限算子上，1080p 下单个 grid_sample 就超过 33.3ms 的帧预算。它改为复用 H.264 解码器的运动矢量，在骁龙 8 Gen 3 上实现 1080p INT8 推理 12.8ms。

### 二、PC 与开发板：苹果 ANE 被重新发掘，低功耗 NPU 出现可比数据

苹果神经引擎长期被认为只适合静态 CNN。弗吉尼亚大学的 [NPUMoE](https://arxiv.org/abs/2604.18788)（04-20）把 MoE 大模型 prefill 中稠密、静态的部分卸载到 ANE，动态路由留在 CPU/GPU，再用离线校准的静态容量分档、分组执行专家和负载感知的图常驻来对付 ANE 的三个短板。在 M2 Max/M2 Ultra 上，PhiMoE 的 prefill 延迟降 1.32~5.55 倍、能效升 1.81~7.37 倍；Qwen3-30B-A3B 也能提速 1.19~3.86 倍，prefill 能耗约 52~137 mJ/token。它的局限也很明确：Core ML 在编译期就静态决定设备放置，decode 阶段仍不在 ANE 上。

同在 Mac 上，[Open-TQ-Metal](https://arxiv.org/abs/2604.16957)（04-18）用融合 int4 注意力，让 Llama 3.1 70B 在 128K 上下文下装进 64GB 的 M1 Max：KV 缓存从 40GB 降到 12.5GB，128K 注意力从 480ms 降到 9.9ms。作者自己也算了账：70B 4bit 权重约 39GB，按 400GB/s 带宽每 token 至少 98ms，所以端到端上限约 10 token/s。瓶颈从“KV 装不下”回到了“权重带宽”。

开发板方面，[Cloud to Edge](https://arxiv.org/abs/2604.24785)（v1 04-24，下列数字取自 08-03 的 v2）给出了少见的同口径对比。树莓派 5 加 Hailo-10H（40 TOPS INT4）后，1.5B 模型的能耗从 27~77 J/token 降到 0.88~5.51 J/token，吞吐升到 1.01~6.34 token/s。Jetson Orin Nano Super 的 GPU 最快，约 9~10 token/s，但功耗 12~13W。爱芯元智 AX630C 的 M5Stack 模块只有 38cm³、约 1.4W，能跑 2~3 token/s，按体积归一化最高。可见低功耗 NPU 已能支撑 1.5B 级离线助手，但速度距手机还差一个量级。

### 三、专用芯片：三值权重与存内计算

4 月 30 日，阳明交大张添烜团队一天放出两篇。[VitaLLM 期刊版](https://arxiv.org/abs/2604.27396)（IEEE TCAS-AI）用 TSMC 16nm 在 0.223mm²、65.97mW 下让 BitNet b1.58 3B 解码 70.70 token/s，品质因数 17.4 TOPS/mm²/W；同一设计的 ISCAS 2026 版在 5 月 1 日另行上传（0.214mm²、72.46 token/s），两版是同一工作的不同版本，本节不作两项成果重复计数。[RCW-CIM](https://arxiv.org/abs/2604.27384)（ISCAS 2026，与工研院合作）是 22nm 流片的数字存内计算芯片，100MHz 下 3.28 TOPS、42.3 TOPS/W；配双路 DDR5-6400 时，INT4 权重的 Llama2-7B 解码 26.87 token/s。按 7B INT4 约 3.5GB 推算，这已接近外存带宽上限。它的核心贡献是把 CIM 的权重写入与读-算重叠，因为 LLM 权重远大于宏容量，写入延迟会进入关键路径。

鲁汶大学 MICAS 的 [ISPASS 2026 论文](https://arxiv.org/abs/2604.25183) 为三值查表加速器做了开源生成器和经 16nm 综合校准的代价模型。结论有些反直觉：查表复用对 FP16 激活收益大，对小整型激活收益递减；优化后面积较乘法器基线小 2.2 倍。同组与斯坦福的[立场论文](https://arxiv.org/abs/2604.07935)则提醒，Mamba-3 为饱和云端 GPU 所做的改动，在边缘场景让延迟增加 28%（880M）到 48%（15M）。

仿真类工作中，KAUST 与 UC Irvine 的 [EdgeCIM](https://arxiv.org/abs/2604.11512) 以 65nm CIM 宏建模，在 1B~4B 小模型上平均达到 336 token/s、173 token/J，并声称在 LLaMA3.2-3B 上比高通 SA8255P 快 9.95 倍。不过这是仿真数字与实测平台的比较，口径不一致。新加坡国立大学的 [SHIELD](https://arxiv.org/abs/2604.07396)（AICAS 2026）按 BF16 位重要性给 eDRAM 分级刷新，刷新能耗降 35%。

### 四、内存层级：闪存、PIM 与 NVMe

本月有三篇工作试图把 KV 和权重放到 DRAM 之外。东南大学的 [NVLLM](https://arxiv.org/abs/2604.25699)（DAC 2026）用晶圆键合把计算流水线和 ECC 做进 3D NAND，FFN 权重在闪存内就地计算，注意力和 KV 留在 DRAM。仿真显示在最大 30B 模型上比 A800 外存推理快 16.7~37.9 倍，CMOS 面积开销 2.7%。计算所的 [AHASD](https://arxiv.org/abs/2604.25326)（DAC 2026）面向手机“单 NPU + LPDDR5-PIM”：PIM 跑草稿模型，NPU 做验证，任务级异步执行；吞吐和能效分别为纯 GPU 基线的 4.2 倍和 5.6 倍，硬件开销不到 DRAM 面积的 3%。东京科学大学的 [AQPIM](https://arxiv.org/abs/2604.18137)（HPCA 2026）在 PIM 内部用乘积量化压缩 KV，较最新 PIM 方案提速 3.4 倍。西江大学等的 [DUAL-BLADE](https://arxiv.org/abs/2604.26557)（ICDCS 2026）把 KV 绕过文件系统直写 NVMe 的连续 LBA，decode 延迟最多降 42.4%。剑桥等的 [MemExplorer](https://arxiv.org/abs/2604.16007) 虽然面向数据中心，但把 LPDDR6 和高带宽闪存（HBF）纳入同一套内存综合，对端侧 SoC 的选型也有参考价值。

### 五、可穿戴与安全

毫瓦级设备上，ETH/博洛尼亚的 [BioTrain](https://arxiv.org/abs/2604.13359) 在 GAP9 MCU 上以低于 50mW 的功耗完成全网络反向传播微调，内存从 5.4MB 压到 0.67MB。帝国理工、诺基亚贝尔实验室等的 [PhysioLite](https://arxiv.org/abs/2604.18067) 把 ECG/EMG 模型压到约 370KB，并部署到 MAX78000 和 Himax WE2 两款 μNPU。安全方面，帝国理工等的 [AgenTEE](https://arxiv.org/abs/2604.18231) 用 Arm CCA 机密虚拟机隔离端侧智能体的运行时、推理引擎和第三方应用，开销低于 5.15%。作者也坦言目前没有商用 CCA 硬件，实验只能在 OpenCCA 原型板上进行。

### 结语：对端侧智能体意味着什么

这个月的论文合起来给出了一个比较清晰的判断：**端侧大模型的约束已经从 NPU 的 TOPS 转到内存层级**。量产手机跑 3B INT4 约 20 token/s，靠投机解码翻倍；8B 模型的冷启动卡在闪存带宽上；Mac 跑 70B 长上下文卡在 400GB/s 的统一内存带宽上；专用芯片即使做到 40+ TOPS/W，解码速度也由外部 DDR 决定。由此出现了两条应对路线。一条是“少读”：三值权重、KV 量化、MoE 稀疏激活，Galaxy S25 Ultra 的实测也证明 MoE 是在手机上“容量换能耗”的现实选择。另一条是“就地算”：LPDDR-PIM 跑草稿模型、3D NAND 跑 FFN、CIM 跑 GEMV，但这条路线目前大多停留在仿真阶段，真正流片的只有 RCW-CIM 这类小规模芯片。对端侧智能体来说，近期能落地的是前者：1B~3B 模型 + 自投机解码 + 更快的冷启动；后者则决定更远期的手机能否常驻 10B 级模型。

需要存疑的地方有三点：EdgeCIM、AHASD、NVLLM、AQPIM 的倍数都来自仿真；Cloud to Edge 的数字来自 v2；三星“已量产部署”是作者自述，论文没有给出对应的具体产品功能名称。

## 7. 总结：对端侧智能体意味着什么，以及 5 月该看什么

**对端侧智能体的含义**

1. **模型够用了，内存决定谁能用。** Gemma 4 E2B 在旗舰手机 GPU 上 decode 50+ tok/s、内存低于 1.5GB（官方），三星在 S25 Ultra 上量产部署 3B INT4（论文），手机常驻 2–4B 模型已经有完整的开放工具链。瓶颈在内存：DRAM 季涨近六成（TrendForce 预测），高通、联发科、Apple、恒玄在财报里确认了出货或成本压力，中端机和可穿戴拿到端侧智能体的时间会往后推。
2. **提速靠解码算法和冷启动，不靠 TOPS。** QMX 和 IQ8 NPU 的数据都表明矩阵算力只缩短首 token，decode 由带宽决定；三星用自投机解码把 3B 从约 19 提到 35–45 tok/s，EdgeFlow 把 8B 冷启动最多缩短 4.07 倍。智能体要多轮、反复唤起，投机解码、闪存加载和 KV 管理是近期最有效的投入。
3. **端侧智能体的现实形态是“端侧编排 + 本地 PC 或云端推理”。** 高通把 OpenClaw 编排放在 4GB 的开发板上，乐鑫让 ESP32 成为 MCP 端点，Firebase 混合推理按规则在 Nano 与云端间切换，下一代 Siri 依赖云端 Gemini。全本地闭环目前只在 24GB 以上的 PC 和 Mac 上可行，而这一档的 Mac 正在缺货。
4. **安全、检索和隔离进入端侧系统议程。** TZ-LLM 在 RK3588 上用 TrustZone 保护 8B 模型且保留 NPU 加速，AgenTEE 用 Arm CCA 隔离智能体运行时（开销 <5.15%），PRISM 把端侧重排序器的峰值内存最多降 91.3%。智能体要保管凭据、调用第三方服务，这些组件和生成速度同样重要。

**留给 5 月的问题（结论已写在 5 月硬件洞察）**

- **投机解码能否进入官方端侧运行时**：Gemma 4 的 MTP 草稿模型权重 4 月 16 日已上线，LiteRT-LM 何时正式支持。
- **内存涨价是否继续扩大**：TrendForce 对 2Q26 手机 LPDDR 的细分预测，以及系统级端侧功能是否开始设内存门槛。
- **NPU 软件栈能否兑现**：ExecuTorch、llama.cpp 等开源栈在 Hexagon NPU 上的端到端数字；Gemini Nano 4 工具调用何时开放。
- **端侧智能体平台化**：联发科、紫光展锐等手机芯片厂商是否把常驻感知和跨应用执行做进 SoC 平台。
- **PIM 的下一步**：JEDEC 5 月 12 日论坛上“LPDDR6-PIM 的上市之路”，以及 MLSys（5/18–22）上的端侧 LLM 论文。

> 口径说明：标“官方”的是厂商发布的数字，“论文”是论文自报（DATE、AHASD、NVLLM、EdgeCIM、AQPIM 等多为仿真），“媒体”和“爆料”未经厂商确认，“推算”是本文按“带宽 ÷ 每 token 读取字节数”等公开参数计算的结果。4 月没有检索到新品的方向：高通、Apple 无新芯片，Apple 无新端侧模型；AMD 无新客户端芯片；紫光展锐、瑞芯微、小米玄戒无官方芯片发布；知存、后摩、苹芯、九天睿芯无可核实的新动态；窗口内没有 ISSCC、ISCA、MICRO 等旗舰会议，高通 AI 研究院新论文未能核实。存疑项：QMX 文中 Q4 加速倍数三处不一致；LiteRT-LM 手机 GPU 数字取自模型卡当前版本；Ollama 前后量化格式不同、测试芯片未写；三星“已量产部署”为作者自述；viNPU 数字来自作者履历；单板机实测论文的数字取自 v2；地平线星空规格为媒体口径；C-X1“带宽需求降至 10%”没有基线；Jetson 停产时间表为合作伙伴转述；8 至尊版 Gen 6“台积电 2nm”与“三星代工”两则爆料存在张力。
