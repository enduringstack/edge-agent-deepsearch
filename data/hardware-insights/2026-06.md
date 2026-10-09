# 硬件洞察：端侧 AI 芯片月报（2026-05-29 ~ 2026-07-01）

> **一句话结论：6 月是“容量月”和“会议月”。** 没有手机旗舰 SoC 发布，信息集中在三处。第一是 PC：Computex 上 NVIDIA/联发科 RTX Spark、AMD Ryzen AI Max PRO 400 把 128–192GB 统一内存带进笔记本，竞争维度从 NPU TOPS 转向“内存容量 × 带宽 × 软件栈”。第二是 Apple WWDC26：端侧模型从 3B 稠密扩展到“20B 总参、每次激活 1–4B”的稀疏模型，权重放闪存，首次以 12GB 内存为门槛。第三是 VLSI、MobiSys、ISCA 三大会议：存内计算进入 2–3nm 和可穿戴 NPU，PIM 开始从 HBM 走向手机 LPDDR，NPU 的短板被一再定位在 decode 和软件开销。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断；第 1–6 节分厂商、分方向展开（高通 / Apple / 其他 SoC 与 PC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选）；第 7 节是对端侧智能体的含义和观察清单。逐条动态（含“能跑多大模型”和可展开的“技术细节”）见 6 月各周首页的“硬件雷达”。

## 0. 总览：6 月的五个判断

**判断一：PC 端侧 AI 改由“统一内存 + GPU”承载，NPU 退为常驻引擎。**

| 平台 | 内存 / 带宽 | AI 算力 | 厂商口径的模型规模 |
|---|---|---|---|
| NVIDIA / 联发科 RTX Spark（N1X，3nm） | 最高 128GB，300GB/s | 1 PFLOP FP4（GPU） | 120B、1M token 上下文（未给 tokens/s） |
| AMD Ryzen AI Max PRO 400 | 最高 192GB（160GB 可作显存） | NPU 55 TOPS + Radeon 8065S | 300B+（4-bit） |
| Intel Arc G3（18A 掌机） | 最高 96GB LPDDR5X | NPU 46 TOPS，GPU 90/113 TOPS | 未披露 |
| 高通 X2 Elite（ASUS QN10 迷你机） | 32GB | NPU 80 TOPS（INT8） | 未披露 |
| 高通 Snapdragon C（约 300 美元笔记本） | 25.6GB/s（8 月手册口径） | 不满足 Copilot+ 40 TOPS 门槛 | 未披露 |

按带宽核算：300GB/s 跑 4-bit 70B 稠密模型，decode 理论上限只有约 7–8 tok/s（推算）。“能跑 120B / 300B”说的是容量，可用速度要靠激活参数少的 MoE。

**判断二：Apple 把端侧模型的上限从 DRAM 推向闪存。**

| 项目 | WWDC26 口径 |
|---|---|
| 端侧模型 | AFM 3 Core（约 3B 稠密）+ AFM 3 Core Advanced（20B 总参，每请求激活 1–4B） |
| 存放方式 | 全量权重在闪存，按请求把激活部分载入 DRAM（每个 prompt 一次，而非每个 token） |
| 门槛 | 至少 12GB 内存：iPhone Air / 17 Pro、M4 iPad、M3 及以上 Mac、M5 Vision Pro |
| 上下文 | 端侧 8192（此前 4096）；开发者可用的 PCC 模型 32K |
| 软件栈 | Core AI 接替 Core ML；Metal 张量新增 FP8 / MX / INT2；GPU Neural Accelerator 定位为 prefill 引擎 |
| 未披露 | 量化位宽、DRAM 占用、tokens/s（完整技术报告“夏季稍后”） |

**判断三：独立实测一致——NPU 赢在 prefill，decode 只有小幅收益。**

| 平台 | 研究 | prefill | decode |
|---|---|---|---|
| 骁龙 X Elite Hexagon | 全流程端侧 RAG（Qwen3-4B） | NPU 787 tok/s，约为 CPU 18 倍 | NPU 14.2 tok/s，约为 CPU 1.7 倍 |
| 骁龙 8 Elite（SM8750） | VLM 分阶段表征（FastVLM-0.5B） | 197 vs CPU 121 tok/s | 113 vs CPU 96 tok/s |
| AMD XDNA2 | TileFuse（Llama3-8B W4A16） | NPU 比 iGPU 快 2 倍 | NPU 弱于 iGPU |
| Apple M1 ANE | 逆向论文 | 约 12 FP16 TFLOP/s | DRAM 85GB/s；小调用约 98% 是软件开销 |

**判断四：存内计算和近存在 6 月同时走向“产品化”。**

| 方向 | 代表 | 关键数字 |
|---|---|---|
| 可穿戴数字 CIM | 联发科 3nm TinyNPU（VLSI） | 峰值 1.47 TOPS，0.06–134.36 µJ/token |
| CIM 编译器 IP | 台积电 2nm DCIM 编译器（VLSI） | 234.4 TOPS/W，511.9 TOPS/mm² |
| 手机 LPDDR-PIM | JEDEC LPDDR6-PIM；COSM、P3-LLM（ISCA） | 标准核心功能基本定稿；PIM 吞吐最高 +2.8 倍 |
| 近存（数据中心，对端侧有参考） | 高通 HBC（投资者日） | 官方称每瓦带宽为 HBM 的 6 倍 |
| 边缘加速器 | Axelera Europa | 629 TOPS（INT8，数字 CIM） |

**判断五：内存成本继续压缩端侧预算，存储带宽成为新变量。** TrendForce 6 月把 2026 年手机产量预测下调到 -16.2%（2 月为 -10%），主因是内存涨价；三星 UFS 5.0（读 10.8GB/s）Q4 量产，美光 1γ LPDDR5X 放量。Apple 的闪存存权重路线和 MoE 专家分页都要依赖这一代存储带宽。

### 6 月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 05-29 | 联发科天玑 7500（首个 Arm C1 中端芯） | 移动 SoC |
| 05-31~06-02 | Computex：RTX Spark、DGX Station for Windows、Ryzen AI Max PRO 400、Arc G3、Snapdragon C、Dragonwing IQ10 | PC / 机器人 |
| 06-03 | CVPR 2026：Apple 14 篇论文与 EDGE 研讨会，高通 MuLo-SD / ReHyAt | 研究 |
| 06-05 | JEDEC：LPDDR6-PIM 核心功能基本定稿 | 内存 |
| 06-08 | WWDC26：AFM 3、20B 稀疏端侧模型、Core AI、PCC on Google Cloud | Apple |
| 06-09 | TrendForce：2026 手机产量或降 16.2% | 产业 |
| 06-10 | 高通无锡汽车峰会：座舱端侧 10B 多模态模型 | 车载 |
| 06-12 | 华为 HDC 2026：HarmonyOS 7 Beta、智能体框架 2.0 | 软件 |
| 06-14~18 | VLSI 2026：联发科 TinyNPU、台积电 2nm DCIM、µAgent 等 | 研究 |
| 06-16~17 | AWE：Snapdragon Reality Elite（48 TOPS，3B @ 45 tok/s）、START 眼镜方案、Snap Specs | XR / 眼镜 |
| 06-21~25 | MobiSys 2026：ShadowNPU、Vec-LUT、KVSwap 等 | 研究 |
| 06-23 | 三星 UFS 5.0（10.8GB/s） | 存储 |
| 06-24 | 高通投资者日：FY29 非手机 400 亿美元、Dragonfly/HBC、收购 Modular；美光 FQ3 | 产业 |
| 06-25 | 爆料：M6 仅基础款，2nm、约 200GB/s | Apple |
| 06-27 | 高通 GenieX（原 NexaSDK）开源 | 软件 |
| 06-29~07-01 | ISCA 2026：COSM、P3-LLM、Cassandra、EVA、SMoE 等 | 研究 |

## 1. 高通：没有新手机芯片，NPU 向所有形态扩展

**判断：** 2026 年 6 月高通没有发布新的手机 SoC，也没有公开新的 Hexagon 微架构细节。这个月的主线是**把“端侧 NPU”扩展到所有形态，并把软件栈补齐**。Computex 上推出 [Snapdragon C](https://the-gadgeteer.com/2026/06/01/qualcomm-computex-snapdragon-c-dragonwing-iq10-robotics/)（向下）、[Dragonwing IQ10](https://www.semiaccurate.com/2026/06/01/qualcomm-releases-the-dragonwing-iq10-rrd-robotics-platform/)（机器人），AWE 上推出 [Reality Elite](https://roadtovr.com/qualcomm-snapdragon-reality-elite-compact-headsets-glasses/) 和 [START](https://www.techtimes.com/articles/318634/20260619/qualcomm-launches-snapdragon-start-speed-ai-smart-glasses-market.htm)（XR/眼镜），投资者日亮出 Dragonfly（数据中心），同期还有 GenieX 开源、收购 Modular、扩大与 Hugging Face 的合作。本月最硬的端侧模型数字有两条：**Reality Elite 以 45 tok/s 运行 3B 模型**，以及**汽车座舱本地运行 10B 多模态模型**。

### 一、Computex：智能体叙事与 token 经济学

Amon 的主题演讲（[STH 实录](https://www.servethehome.com/qualcomm-computex-2026-live-coverage/)）没有给出新的 TOPS，而是给出一套 token 账：智能体每个任务需要 1 万到 100 万以上 token，两代之内需求增长 100 倍以上；端云分工的演示得到相同结果，**token 少 30%，成本低 4 倍**。这为端侧 NPU 提供了经济学论据。Amon 还强调智能体编排需要强 CPU，说明高通后续 SoC 会继续加码 Oryon。[Moor Insights](https://moorinsightsstrategy.com/research-notes/qualcomm-expands-snapdragons-pc-reach-teases-investor-day-news-at-computex-2026/) 转述了“从 2 mW 可穿戴到 200 kW 机柜”的算力连续体口径。

### 二、PC：两端拉开

| 平台 | CPU | NPU | 内存/带宽 | 定位 |
|---|---|---|---|---|
| Snapdragon C | 8 核 Kryo（1×3.0+3×2.6+4×2.0 GHz，8 月披露） | 官方未披露（媒体约 12 TOPS） | ≤16GB，32-bit，25.6 GB/s（8 月披露） | ~300 美元，非 Copilot+ |
| X2 Elite X2E-88-100（[ASUS QN10](https://www.cnx-software.com/2026/06/02/asus-ascent-qn10-mini-pc-is-powered-by-qualcomm-snapdragon-x2-elite-18-core-armv9-processor/)） | 18 核 Oryon，最高 4.7 GHz | 80 TOPS INT8 | 16/32GB LPDDR5X-8533 | 1,349.99 美元迷你台式机 |

Snapdragon C 是高通首条非 X 品牌的 PC 芯片。6 月发布时只公布了“Kryo CPU + 集成 NPU、不满足 Copilot+”。工艺（6nm）、GPU 和内存规格要到 8 月的[产品手册](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-C-Platform-Product-Brief.pdf)才补齐。按 25.6 GB/s 粗算，INT4 的 3B 模型解码上限约 17 tok/s（估算），所以它不是本地大模型平台。另一端，X2 Elite 的 Hexagon 从上一代 45 TOPS 提升到 80 TOPS，官方披露标量和向量吞吐各 +143%、矩阵 +78%、总线带宽 +127%（背景资料，见 [Signal65](https://signal65.com/research/snapdragon-x2-elite-and-x2-elite-extreme-raising-the-bar-for-ai-pcs/)）。FP8/INT2 等精度支持至今没有官方说明，记为未披露。

### 三、XR 与眼镜：首次公布 LLM 吞吐

[Reality Elite](https://roadtovr.com/qualcomm-snapdragon-reality-elite-compact-headsets-glasses/) 是本月技术含量最高的芯片：

| 项目 | XR2+ Gen 2 | Reality Elite（官方口径） |
|---|---|---|
| CPU | — | 6 核 Kryo（4P+2E），2.9 GHz，+30% |
| GPU | — | +60%，12MB 高速显存 |
| NPU | — | 48 TOPS，+160%，另有独立音频 NPU |
| 端侧 LLM | 未公布 | **3B @ 45 tok/s**（[TechCrunch](https://techcrunch.com/2026/06/16/qualcomm-wants-to-be-the-chip-inside-whatever-replaces-your-smartphone-and-it-just-announced-two-products-toward-that-end/)） |
| 显示 | 4.3K/眼 | 4.4K×4.4K/眼 @90Hz |
| 摄像头 | — | 12 路（2×12MP@90 + 10×720p@120） |
| 能效 | — | 同负载续航 +20%，满载温度低 12°C |

独立音频 NPU 用来做常驻唤醒，把低功耗常驻感知从主 NPU 里拆了出来。3B@45 tok/s 的精度没有明说；如果是 INT4，约需 68 GB/s 有效带宽（估算）。[START](https://www.techtimes.com/articles/318634/20260619/qualcomm-launches-snapdragon-start-speed-ai-smart-glasses-market.htm) 则是商业模式上的创新：基于 AR1+ 模组，提供音频+摄像头、单目 LCoS、双目 microLED 三种白牌参考设计，ODM 为 Pegatron 和 Jorjin，高通以约 1,000 万美元入股 Inspecs。Amon 称在研可穿戴设计超过 40 款。同场 [Snap Specs](https://tomsguide.com/computing/smart-glasses/snap-specs-are-official-and-theyre-a-bold-mash-up-of-ray-ban-metas-and-apple-vision-pro-with-an-eye-watering-price) 在镜框内用两颗骁龙（系统 + CV）分工，售价 2,195 美元。

### 四、机器人与汽车：端侧最大的模型

[Dragonwing IQ10](https://the-gadgeteer.com/2026/06/01/qualcomm-computex-snapdragon-c-dragonwing-iq10-robotics/) 采用 18 核 Oryon、64GB 封装内 LPDDR5x（带 ECC），接 12 路 GMSL2 和 8 路 CAN-FD。官方算力 700 TOPS，但 SemiAccurate 指出这是 CPU+GPU+NPU 的合计值。6 月开放早期客户，9 月全球供货。[无锡汽车峰会](https://autonews.gasgoo.com/articles/news/cockpit-driving-fusion-qualcomm-unveils-another-major-move-2064710943249113089)上，8775 舱驾一体已量产（9 个定点），8797 支持 40 路以上摄像头和端到端 Transformer，至尊版平台总有效算力最高 2,000 TOPS。**座舱可在本地运行 100 亿参数多模态大模型**，比手机和 XR 端高一个数量级；高通同时发起“Claw”车载智能体生态。轻舟智航在 SA8650P 上演示了[城市 NOA](https://roboticsandautomationnews.com/2026/06/12/qcraft-demonstrates-urban-noa-on-qualcomms-latest-snapdragon-ride-chip-targets-2026-global-mass-production/102512/)。

| 场景 | 平台 | 官方端侧模型规模 |
|---|---|---|
| XR | Reality Elite | 3B @ 45 tok/s |
| 汽车座舱 | 至尊版 8397 等 | 10B 多模态（tok/s 未披露） |
| 机器人 | IQ10 | 未披露（64GB 内存） |
| 入门 PC | Snapdragon C | 未披露 |

### 五、软件栈：本月真正的增量

- **GenieX**（原 NexaSDK，来自收购的 Nexa AI）：[开发者预览](https://www.qualcomm.com/developer/blog/2026/06/geniex-developer-preview)以 BSD-3 开源。llama.cpp 路径可以把任意 GGUF 模型跑到 Hexagon HTP 上（推荐 Q4_0）；qairt 路径使用 AI Hub 预编译包，只跑 NPU。它提供 OpenAI 兼容的本地服务，6 月下旬的版本加入微软签名的 HTP catalog 和 MXFP4 识别。
- **AI Hub**（[release notes](https://workbench.aihub.qualcomm.com/docs/hub/release_notes.html)）：6 月 9 日上线 Galaxy S26（SM8850-AD）真机；6 月 22 日加入 QAIRT 2.47，ONNX Runtime 1.26 + QNN EP 2.2，弃用 TorchScript、转向 .pt2。
- **Modular 收购与 Hugging Face**：投资者日同日公布。前者带来跨加速器编译栈（Mojo/MAX，7 月 29 日交割）；后者把 300 多万个模型接入 Snapdragon、Dragonwing、Dragonfly 全线平台，并共同开发混合编排的 HF Agent。
- **研究**：CVPR 2026（6 月 3-7 日）上，Qualcomm AI Research 的 [MuLo-SD](https://arxiv.org/abs/2601.05149)（图像自回归投机解码，最高快 5 倍）和 [ReHyAt](https://arxiv.org/abs/2601.04342)（视频 DiT 混合线性注意力，显存恒定，约 160 GPU 小时蒸馏）都瞄准端侧生成的带宽和显存瓶颈，但两篇都没有给出 Snapdragon 实测。

### 六、投资者日与数据中心（对端侧的参考）

[投资者日](https://futurumgroup.com/insights/qualcomms-investor-day-2026-agentic-and-ai-inference-to-drive-2x-revenue-growth-by-2030/)给出的 FY29 目标：非手机 QCT 400 亿美元，其中汽车 100 亿美元，IoT 超过 140 亿美元（工业/机器人 80 亿 + PC/XR 60 亿）；手机降到 QCT 的约 1/3。[Dragonfly](https://www.storagereview.com/news/qualcomm-unveils-dragonfly-data-center-roadmap-c1000-cpu-ai300-accelerator-and-modular-acquisition) 的 HBC 近存计算（AI250 单卡 133 TB/s，是 AI200 的 18 倍）和端侧 NPU 面对的是同一个问题：解码阶段受内存带宽限制。

### 爆料说明

经检索，没有找到 6 月发布的可核实的 Snapdragon 8 Elite Gen 6 新爆料。2nm、2+3+3 Oryon、Adreno 845/850 和 Pro 版 LPDDR6 等信息出自 3-4 月 Digital Chat Station 的**爆料**，“Extreme”命名和 5 GHz Geekbench 爆料则集中在 8 月；正式产品已于 9 月骁龙峰会发布，不属于本期。

### 小结

6 月的高通更像是在做生态和形态上的铺垫：芯片端唯一的新 NPU 数字来自 XR（48 TOPS，3B@45 tok/s），最大的端侧模型出现在汽车（10B），PC 端则用 Snapdragon C 主动放弃 Copilot+ 换取价格。真正的变化在软件侧：GenieX 让 GGUF 直通 Hexagon，Modular 和 Hugging Face 补上编译器和模型分发。这些都在为 9 月的 8 Elite Gen 6 和“agent-ready”换机周期做准备。值得跟踪的未知项包括：Hexagon 是否支持 FP8/INT2、Reality Elite 的精度和功耗，以及 GenieX 的实测 tok/s。

## 2. Apple：WWDC26 的端侧架构换代

**判断：** 2026 年 6 月的 WWDC26 是 Apple 端侧 AI 的一次「架构换代」：端侧模型从单一 3B 稠密模型扩展为 3B 稠密 + 20B 稀疏两档，后者把全部权重放在 NAND flash、每次只把 1–4B 参数搬进 DRAM，并以 12GB 内存作为硬门槛；软件栈上 Core AI 接替 Core ML，Metal 张量引入 FP8/MX/INT2，M5/A19 GPU 的 Neural Accelerator 被正式定位为 prefill 引擎。与此同时，最强的 AFM 3 Cloud Pro 跑在 Google Cloud 的 NVIDIA Blackwell 上，说明 Apple 自研服务器芯片尚未接手云端主力。

### 一、AFM 3：五个模型、两档端侧

[Apple ML Research 6 月 8 日博客](https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models) 公布第三代 Apple Foundation Models，官方称与 Google 合作定制，预训练在最新一代云 TPU 上扩展，后训练为 SFT + 多阶段 RL，并用 QAT 压缩；Apple [安全博客](https://security.apple.com/blog/expanding-pcc/) 则写明采用了 Gemini 家族背后的技术。

| 模型 | 部署 | 规模/架构（官方） | 优化目标硬件 |
|---|---|---|---|
| AFM 3 Core | 端侧 | ≈3B 稠密 | Apple silicon |
| AFM 3 Core Advanced | 端侧 | 20B 总参，稀疏，每请求激活 1–4B，原生多模态 | 最强 Apple silicon（≥12GB） |
| AFM 3 Cloud | PCC | 升级版 PT-MoE，参数未披露 | Apple silicon |
| ADM 3 Cloud (Image) | PCC | 扩散图像生成/编辑，带专用 adapter | Apple silicon |
| AFM 3 Cloud Pro | PCC（Google Cloud） | 未披露 | NVIDIA GPU |

官方人评：AFM 3 Core 对 2025 基线 45.6% vs 23.3%；AFM 3 Cloud 对 2025 AFM Server 64.7% vs 8.7%；AFM 3 Core Advanced 在 1B 激活档的 TTS MOS 为 4.15/4.24（旧 TTS 3.87/3.82），听写整体质量偏好 44.7% vs 17.6%。**量化位宽、内存占用、tokens/s 全部未披露**，Apple 表示完整技术报告「今夏晚些时候」发布。

作为对照，[2025 版报告](https://machinelearning.apple.com/research/apple-foundation-models-2025-updates) 的 3B 端侧模型为 5:3 两段结构、后段复用前段 KV cache（KV 内存 -37.5%）、解码器 2 bpw QAT、embedding 4 bit、KV cache 8 bit、LoRA adapter rank 32、视觉编码器 300M ViTDet-L；云端 PT-MoE 采用 3.56 bpw ASTC 压缩。

### 二、AFM 3 Core Advanced：把 20B 塞进手机的方法

核心是 Apple 2025 年 ICML 论文 [Instruction-Following Pruning](https://machinelearning.apple.com/research/pruning-large-language)（该文把 9B 模型按指令裁剪为 3B 激活，数学/代码比 3B 稠密高 5–8 分、接近 9B）。AFM 3 Core Advanced 的工程化要点（官方）：

- **权重在 flash，热点在 DRAM**：全量 20B 存 NAND，大比例 shared experts 常驻，routed experts 按需换入。
- **按 prompt 路由而非按 token**：因为 NAND→DRAM 带宽不足以逐 token 换专家；一个轻量稠密块在 prefill 选定专家集，生成中周期性重选。
- **激活规模按用例预设**：1B（语音/听写）到 4B，不同难度请求可增量加载。

设备门槛（[Siri AI 新闻稿](https://www.apple.com/newsroom/2026/06/apple-introduces-siri-ai-a-profoundly-more-capable-and-personal-assistant/)）：

| 平台 | 支持 20B 端侧模型 | 说明 |
|---|---|---|
| iPhone | iPhone Air、17 Pro/Pro Max（A19 Pro） | iPhone 16 Pro 等 8GB 机型排除 |
| iPad | M4 及以后且 ≥12GB | M4 iPad Pro 256/512GB（8GB）不支持（[macitynet](https://www.macitynet.it/afm-3-core-advanced-apple-12-gb-ram/)） |
| Mac | M3 及以后且 ≥12GB | 实际多为 16GB 起（[Mac Fan](https://macfan.book.mynavi.jp/article/109355/)） |
| Vision Pro | M5 版 | — |

12GB 是整机门槛而非模型占用：DRAM 需同时容纳 OS、App、被路由权重、共享专家、中间激活和随长度增长的 KV cache（媒体分析）。上下文方面，[会话 319](https://developer.apple.com/videos/play/wwdc2026/319/) 给出端侧 OS 26.0 为 4096、OS 27.0 新设备为 8192 tokens，PCC 模型 32768 tokens。

### 三、软件栈：Core AI 接替 Core ML

[Core AI](https://developer.apple.com/videos/play/wwdc2026/324/) 是面向生成式模型的新运行时：统一调度 CPU/GPU/Neural Engine，内存安全 Swift API、零拷贝、有状态执行（KV cache 作为 state 原地更新）、AOT 编译 + 设备特化缓存；会话以本地 70B 参数 LLM agent 为例。[InfoQ](https://www.infoq.com/news/2026/06/apple-core-ai-wwdc/) 称其覆盖约 3B 视觉模型到 70B 推理 LLM。Core ML 保留，定位传统 ML。

[会话 325](https://developer.apple.com/videos/play/wwdc2026/325/) 的 coreai-opt 支持 **int4 / int8 / FP4 / FP8** 权重压缩（PTQ 或 QAT），以 850M 参数 SAM3 为例：FP32 >3GB → int4 per-channel 约 430MB；对占 96% 参数的编码器用 4-bit palettization，而占 4% 的检测头保持高精度即可恢复质量；复用图像 embedding 使第二次推理快 76%。新 Core AI Debugger 以 PSNR 逐算子对比定位量化误差。

[会话 330](https://developer.apple.com/videos/play/wwdc2026/330/) 的 Metal 张量在 OS 27 新增 FP4/FP8（E4M3）、**INT2**、E8M0 块缩放（32×1）与 MX 格式，matmul2d 可直接消费量化输入；TensorOps 在 M5/A19 GPU 上自动调用每个 shader core 内的 **Neural Accelerator**，官方定位是「LLM prefill 等稠密计算」。

Foundation Models 框架（[会话 241](https://developer.apple.com/videos/play/wwdc2026/241/)）新增图像输入、LanguageModel 协议（可接 Claude/Gemini 及开源 CoreAILanguageModel/MLXLanguageModel）、Python SDK 与 fm CLI；PCC 模型对 <200 万首次下载的 App 免费。

### 四、MLX 与 M5 Neural Accelerator：prefill 与 decode 的分工

[会话 232](https://developer.apple.com/videos/play/wwdc2026/232/)：M5 GPU Neural Accelerator 使矩阵乘比 M4 快 **4×**，几乎等比转化为 MLX prefill 加速；agent 会话以输入 token 为主，因此收益明显。decode 仍受带宽约束——M5 基础款带宽 153GB/s，而 6 月 25 日 [Bloomberg/MacRumors 爆料](https://www.macrumors.com/2026/06/25/m6-macbook-pro-2026/) 的 M6 为约 200GB/s。[会话 233](https://developer.apple.com/videos/play/wwdc2026/233/) 则给出 Mac 集群数据：4 台 M3 Ultra 经 Thunderbolt 5 RDMA 互联，Qwen 3.6 27B 推理近 3×，1T 参数 Kimi 2.6（8-bit ≈1TB）四机可跑，Qwen 3.5 9B 微调 ~180 → ~600 tok/s。

| 维度 | M4 | M5 | M6（爆料） |
|---|---|---|---|
| 工艺 | 3nm | 3nm | TSMC N2（2nm），WMCM 封装 |
| GPU 矩阵乘 | 基准 | 4×（Neural Accelerator，官方） | 测试 12 核 GPU，「为 AI 优化」 |
| 内存带宽（基础款） | 未在本文来源核实 | 153GB/s | 约 200GB/s |

第三方研究也在本窗口给出 Apple 芯片的独立画像：[ANE 逆向论文](https://arxiv.org/abs/2606.22283)（6/21）实测 M1 ANE 峰值约 12 FP16 TFLOP/s、DRAM 85GB/s、拐点 ~141 FLOP/byte，小图调用约 190µs 且 98% 为软件/固件开销，M5 上四种压缩权重都能流式解码（带宽受限层 1.6–1.8× FP16 速度）；[BaseRT](https://arxiv.org/abs/2607.00501)（7/1）原生 Metal 运行时 decode 最高为 llama.cpp 的 1.56×、MLX 的 1.35×。这两项说明：ANE 擅长大块稠密卷积/矩阵（能效高 GPU 9×），但细粒度 LLM decode 受调度开销拖累，GPU 路线仍有优化余量。

### 五、云端：PCC 走出 Apple 数据中心

[Apple 安全博客](https://security.apple.com/blog/expanding-pcc/) 与 [Google Cloud 博客](https://cloud.google.com/blog/products/identity-security/powering-the-next-era-of-confidential-ai)（6/11）确认：PCC 首次部署到第三方数据中心，栈为 NVIDIA Blackwell 机密计算 + Intel TDX + Google Titan，软件证明至少基于两家独立厂商信任根，Google Cloud PCC 硬件记入可验证 append-only 账本。GPU 型号、规模未披露。Ivan Krstić 在 6 月 23–24 日 Confidential Computing Summit 进一步介绍（内容仅见媒体转述）。背景上，Apple 自研 AI 服务器芯片 Baltra 此前由郭明錤预计 2026 下半年量产（[TechSpot](https://www.techspot.com/news/110918-apple-could-unveil-house-ai-server-chips-later.html)），7 月中旬又有延期报道（窗口外）——本月 PCC 外包给 Blackwell 与此一致。

### 六、其他芯片爆料

- **M6（6/25，爆料）**：只做基础款，取消 M6 Pro/Max，高端跳到 2027 年 M7 Pro/Max/Ultra。
- **C2 基带（6/25–6/30，爆料）**：Tata Electronics 约 630GB 泄露文件显示 iPhone 18 Pro 美版仍用高通 SDX80M 等器件，非美版推测改用 C2，且 C2 据称不支持 mmWave（[AppleInsider](https://appleinsider.com/articles/26/06/30/iphone-18-pro-leaks-qualcomm-or-apple-c2-model-a20-details-camera-upgrades)、[heise](https://www.heise.de/en/news/Leak-Apple-uses-different-modems-for-iPhone-18-Pro-11352747.html)）。
- 学术侧，Apple 在 [CVPR 2026](https://machinelearning.apple.com/updates/apple-at-cvpr-2026) 发表 14 篇论文（STARFlow-V、AToken、VSAS-Bench 等），并在 EDGE（高效与端侧生成）研讨会做特邀报告，但页面未公开端侧效率数字。

### 七、对端侧芯片与系统设计的启示

1. **存储层级成为模型容量的一部分。** 过去端侧模型容量被 DRAM 卡死：8GB 手机在扣除系统与应用后，能留给模型的空间大约只够一个 2–4 bit 的 3B 模型。AFM 3 Core Advanced 把「总参数」与「驻留参数」解耦，模型上限改由 NAND 容量决定，而 DRAM 只需容纳 1–4B 激活参数加 KV cache。这对 SoC 与存储控制器提出新要求：NAND 顺序读带宽、读延迟和功耗会直接决定换专家的代价，UFS/NVMe 规格从此进入 AI 性能讨论。Apple 选择按 prompt 而不是按 token 路由，本身就说明当前 NAND 带宽还远不足以支撑逐 token 换入。
2. **12GB 是新的及格线。** 苹果用官方门槛把 8GB 设备挡在 20B 模型之外，也就默认了未来旗舰机的内存基线会继续上移。安卓阵营若要跟进同类稀疏模型，内存配置与 flash 带宽要同步升级。
3. **prefill 与 decode 分开优化。** M5/A19 的 GPU Neural Accelerator 提供 4 倍矩阵乘能力，主要缩短首 token 延迟；decode 是带宽受限的阶段，靠的是 M6 那样的带宽提升，以及 INT2/FP4/MX 这类更低比特的权重格式。Apple 把 INT2 和 MX 写进 Metal 张量规范，说明更激进的权重压缩正在成为官方路线。前两代端侧模型已经用 2 bpw QAT，AFM 3 大概率沿用甚至进一步压缩，但官方尚未确认。
4. **ANE 的定位在变化。** 独立逆向研究显示，ANE 在大块卷积和矩阵运算上能效突出，但小图调度开销高达百微秒级，不适合细粒度的动态算子。Core AI 统一调度 CPU、GPU 和 ANE，开源的 CoreAILanguageModel 又明确在 ANE 上运行本地模型，可以推断 Apple 正在用编译器和运行时（AOT 特化、状态化 KV cache、算子融合）来降低 ANE 的调度代价。实际效果要等第三方测出 tokens/s 才能判断。
5. **端云边界由开发者决定。** 端侧上下文 8K、PCC 32K，加上 LanguageModel 协议可以接入第三方云模型，端云路由不再只由系统决定，开发者也能控制。端侧芯片需要承担的是低延迟、离线和隐私数据处理，长上下文与深度推理交给云端。这种分工与高通、联发科「全量端侧」的宣传口径不同，值得在后续月份对比观察。

### 小结

Apple 本月给出的答案是「容量靠 flash、速度靠 prefill 加速器、复杂度交给云」：20B 稀疏模型以按 prompt 路由绕开 NAND 带宽瓶颈，12GB 内存成为新的端侧大模型分水岭；Core AI + coreai-opt + Metal 张量把 FP4/FP8/MX/INT2 纳入官方工具链，M5/A19 的 GPU Neural Accelerator 承担 prefill，而 decode 的带宽瓶颈留给 M6 的约 200GB/s 来解决。最大的信息缺口仍是 AFM 3 端侧模型的 bit 宽、DRAM 实占和 tokens/s——需等待 Apple 后续技术报告。

## 3. 联发科、NVIDIA、AMD、Intel 与产业：Computex 上的“容量竞赛”

**本月判断：** 6 月的主线不在手机，而在 PC。NVIDIA 与联发科联合打造的 RTX Spark（N1X）在 Computex 前夜正式亮相，把“128GB 统一内存 + 300GB/s + 1 PFLOP FP4 + 原生 CUDA”带进 14mm 厚的 Windows on Arm 笔记本，端侧 AI 的竞争维度正式从“NPU TOPS”转向“统一内存容量 × 带宽 × 软件栈”。AMD 用 192GB 的 Ryzen AI Max PRO 400 正面回应，Intel 则以 18A 量产与 Arc G3 掌机守住 x86 基本盘；手机侧只有天玑 7500、华为 nova 16 等中端迭代，同时内存涨价正在压缩端侧模型可用的 DRAM。

### 一、RTX Spark：Arm PC 的第二极，以 GPU 而非 NPU 承载 AI

[NVIDIA 官方页面](https://www.nvidia.com/en-gb/geforce/news/computex-2026-nvidia-geforce-rtx-announcements/)给出的核心口径是：20 核 Grace CPU + 6,144 CUDA 核 Blackwell RTX GPU（第五代 Tensor Core，支持 FP4），NVLink-C2C 互连，最高 128GB 统一内存、“up to 1 petaflop” AI 算力，今年秋季由 ASUS/Dell/HP/Lenovo/Surface/MSI 首发。[StorageReview](https://www.storagereview.com/news/nvidia-computex-2026-keynote-the-rtx-spark-pc-family-dgx-station-and-physical-ai) 与 [TechNews](https://finance.technews.tw/2026/06/02/nvidia-and-mediatek-unveil-rtx-spark-super-chip/) 补充了演讲细节：TSMC 3nm、两颗 chiplet、700 亿晶体管、LPDDR5X 300GB/s、C2C 600GB/s，功耗“个位数瓦到约 80W”，并称可运行 120B 模型、1M token 上下文。

| 平台 | CPU | AI 加速 | 统一内存 | 带宽 | 厂商模型口径 |
|---|---|---|---|---|---|
| NVIDIA RTX Spark | 20 核 Grace（Arm） | Blackwell 6,144 CUDA，1 PFLOP FP4；NPU 未披露 | 16–128GB LPDDR5X | 300GB/s | 120B，1M 上下文 |
| AMD Ryzen AI Max+ PRO 495 | 16 核 Zen 5 | 40 CU iGPU + NPU 55 TOPS | 最高 192GB（160GB 可作显存） | 未披露 | 300B+（4-bit） |
| Intel Arc G3 Extreme | 14 核（2P+8E+4LP-E） | Xe3 12 核 113 TOPS + NPU 46 TOPS | 最高 96GB LPDDR5X-8533 | 未披露 | 未披露 |
| NVIDIA DGX Station (Windows) | 72 核 Grace | Blackwell Ultra 20 PFLOPS FP4 | 748GB 一致性内存 | 未披露 | 万亿参数级 |

值得工程师注意的几点：

- **AI 主力是 Tensor Core 而非 NPU。** NVIDIA 与微软都没有公布独立 NPU 的 TOPS（[IT Brief](https://itbrief.com.au/story/microsoft-nvidia-launch-rtx-spark-windows-ai-pc-lineup) 只说它会归入 Copilot+ PC），1 PFLOP 是 FP4 Tensor Core 口径。这与 Snapdragon X、Panther Lake 等以 NPU 为常驻 AI 核心的路线完全不同：常驻低功耗 AI 能力如何实现，目前是未知数。
- **带宽决定解码速度。** 按 300GB/s 粗算（非实测），40GB 级的 70B INT4 稠密模型解码上限约 7 token/s；120B 的说法更适合激活参数只有数 B 的 MoE 模型。所以“能装下”不等于“跑得快”。
- **软件栈同时到位。** NVIDIA 宣布 llama.cpp 提速 2 倍、vLLM 提速 2.6 倍，Nemotron 3 Nano 30B 当场开放（Ultra 约 550B 总参/55B 激活，[DigitalApplied](https://www.digitalapplied.com/blog/nvidia-gtc-taipei-computex-2026-keynote-first-take)）；OpenShell 为每个 Agent 提供独立沙箱，微软则为该芯片适配了 MPTF 与调度器。
- **待验证。** StorageReview 转述称重度 AI 或游戏负载下电池只能撑 45–60 分钟；TDP、核心划分（传闻 10P+10E）、N1 小芯片（爆料：10/12 核、2,048/2,560 CUDA）都还没有独立评测。

联发科原定 6 月 3 日的 CEO 主题演讲被取消，[6 月 28 日的官方博客](https://www.mediatek.com/tek-talk-blogs/highlights-from-mediateks-computex-2026-keynote)只做了概括性回顾。联发科具体负责哪些模块仍未公开，但它借此首次以主 SoC 合作方身份进入 Windows 旗舰笔记本。

### 二、x86 阵营：AMD 拼容量，Intel 拼 18A 与掌机

**AMD**（本届没有主题演讲）的看点是 [Ryzen AI Max PRO 400](https://www.igorslab.de/en/amd-computex-2026-x3d-anniversary-am5-2029-rx-9070-gre-global-ai-pivot/)：

- 旗舰 Max+ PRO 495 为 16C/32T、Radeon 8065S 40 CU、NPU 55 TOPS，统一内存最高 192GB，AMD 称其为“首款能跑 300B+ LLM 的 x86 客户端处理器”（4-bit、160GB 显存口径）。
- 配套的 Ryzen AI Halo 开发平台 6 月开放预订，3,999 美元起，跑 ROCm + LM Studio/ComfyUI。
- NPU 仍停留在 XDNA 2 的 50–60 TOPS 档。大模型实际跑在 iGPU 上，和 RTX Spark 一样，“NPU TOPS”已经不是高端 AI PC 的决定性指标。

**Intel** 6 月 2 日的主题演讲以平台和制造为主（[SemiconAlpha](https://semiconalpha.substack.com/p/intel-computex-2026-keynote-key-takeaways)）：

- 18A 进入全面量产，Core Ultra Series 3 拿下 300+ 款设计，Core Series 3 有 70+ 款。
- 新品 [Arc G3/G3 Extreme](https://www.igorslab.de/en/intel-arc-g-series-panther-lake-handheld-processor-label/) 是 Panther Lake 的掌机版：14 核、Xe3 10/12 核（90/113 TOPS）、NPU 46 TOPS（笔记本版 NPU 5 为 50 TOPS）、LPDDR5X-8533 最高 96GB、cTDP 8–35W。
- Perplexity 演示了在 Core Ultra Series 3 本地处理机密文件、云端执行其余任务的混合 Agent 流程。
- Nova Lake 的 NPU 6 本月没有官方数字，此前爆料约 74 TOPS INT8。

### 三、Arm 与移动 SoC：本月以中端迭代为主

[Arm CEO Rene Haas 6 月 2 日的演讲](https://technews.tw/?p=1565258)聚焦 Agentic PC 与 RTX Spark，提出 Agent 负载需要“同功耗下 4 倍 CPU 核数”，但没有发布新的移动 IP，Lumex（C1 + Mali G1 + SME2，2025 年 9 月）仍是现役平台。

联发科 5 月 29 日发布的[天玑 7500](https://gsmarena.com/mediatek_unveils_dimensity_7500_with_arm_c1_cpu_faster_npu-news-73040.php)把 C1 Pro/C1 Nano 下放到 7 系：

- 4nm 工艺，4×2.6GHz + 4×2.0GHz，Mali-G625 MC2。
- NPU 850 只说“升级”，没有给 TOPS；内存仍是 LPDDR5-6400。
- 端侧 AI 用例限于实时转写/TTS、通知摘要。

华为方面：

- 6 月 1 日发布 [nova 16 系列](https://www.ithome.com/0/958/319.htm)，多数报道称全系麒麟 9010S，华为口径整机性能 +10%。麒麟 NPU 参数依旧不披露。
- 6 月 12 日 [HDC 2026](https://www.huawei.com/cn/news/2026/6/harmonyos7-hdc) 启动 HarmonyOS 7 Beta：智能体框架 2.0（复杂任务成功率 >90%）、开放 20+ 系统级 AI 能力与 GUI 操控，小艺接入 200+ 感知数据，并开源 openPangu 2.0，但端侧模型参数量同样未披露。

小米玄戒 O2、Google Tensor G6（爆料：1+4+2 七核、C1 Ultra 4.11GHz、TPU 代号 Santafe）、Exynos 2700（传闻 SF2P、LPDDR6）本月都没有官方发布，只能视为爆料。作为背景，第三方 die-shot 分析给出 Exynos 2600 NPU 的数据为 32K MAC、8MB scratchpad、约 59 TOPS（媒体口径）。

### 四、产业：内存成本正在吞噬端侧 AI 的内存预算

[TrendForce 6 月 9 日](https://www.trendforce.com/presscenter/news/20260609-13087.html)预测 2026 年全球手机产量约 10.51 亿部（-16.2%），1Q26 为 2.84 亿部（-1.7%）。其 [5 月报告](https://www.trendforce.com/presscenter/news/20260514-13044.html)预计 2Q26 LPDDR5X 合约价环比上涨 78–83%，此前还指出高端机 12GB 成为主流、中端回落到 8GB。对端侧 LLM 来说，DRAM 容量本来就是硬约束，现在叠加成本压力，OEM 更可能选择 3B 级以下的常驻模型或端云混合，而不是继续加大本地模型。

晶圆端，基于 TSMC 技术论坛的[分析](https://borecraft.com/2026/06/10/tsmc-is-ramping-2nm-at-five-fab-phases-in-year-one/)称 N2 首年有五个厂区阶段同步爬坡，年底产能约 9 万片/月（估计值、口径偏软，可信度低），为下半年的 2nm 手机旗舰供货。SK hynix 的 LPDDR6 量产仍指向下半年。

### 五、端侧模型容量对照：厂商口径 vs. 带宽现实

本月几家厂商给出的“能跑多大模型”口径差异很大，需要拆开看：

| 设备/平台 | 厂商口径 | 口径前提 | 我们的解读（非实测） |
|---|---|---|---|
| RTX Spark | 120B 参数、1M token 上下文 | 未说明精度与是否 MoE | 128GB 装得下 4-bit 的 120B 级 MoE；稠密 70B INT4 约 40GB，受 300GB/s 带宽限制，解码理论上限仅个位数 token/s |
| Ryzen AI Max PRO 400 | 300B+ LLM | 4-bit 量化、160GB 分给 GPU | 容量上限最高，但带宽未在本次材料中披露，速度无法评估 |
| DGX Station for Windows | 万亿参数级 | 748GB 一致性内存、20 PFLOPS FP4 | 定位桌边研发机，不属于移动端侧 |
| Jetson AGX Thor T5000 | 运行 Isaac GR00T / Cosmos 3 Edge | 128GB、2,070 FP4 TFLOPS、40–130W | 机器人端的 VLA/世界模型可以在本体上完整推理 |
| Nemotron 3 Nano | 30B，吞吐为前代 Nano 的 4 倍 | NVIDIA 官方 | 典型的 RTX 笔记本/RTX Spark 本地 Agent 尺寸 |
| 天玑 7500 / 麒麟 9010S | 未披露 | — | 中端手机仍以语音、摘要类小模型为主 |

由此可以得到三个工程判断：

1. **容量和速度要分开看。** 统一内存决定“能不能装下”，内存带宽决定“每秒能吐几个 token”。厂商普遍只报前者，本月没有一家给出端侧 tokens/s 实测，秋季的首批评测必须补上这一项。
2. **MoE 是 PC 端大模型的实际形态。** 120B、300B+ 这类口径，只有在激活参数远小于总参数的 MoE 模型上才有可用的交互速度。NVIDIA 同场开放的 Nemotron 3 Ultra（约 550B 总参/55B 激活）也是 hybrid MoE，说明模型侧在配合这一硬件趋势。
3. **常驻低功耗 AI 仍要靠 NPU。** GPU 的 FP4 算力适合突发的大模型推理，但系统级 Agent（如 HarmonyOS 7 的 200+ 项感知数据、Windows Copilot+ 的常驻功能）需要毫瓦到瓦级的常开能力。RTX Spark 没有公布 NPU 指标，这是它和 Panther Lake、Ryzen AI 路线之间最大的不确定性。

### 小结

- **PC 端侧 AI 进入“统一内存竞赛”。** RTX Spark 128GB/300GB/s、Ryzen AI Max PRO 400 192GB、DGX Station 748GB，NPU TOPS 在高端已退居次要；接下来要看的实测指标是 tokens/s 和电池续航，而不是峰值 TOPS。
- **移动端 6 月是空窗期。** 只有中端 C1 下放和麒麟迭代，真正的旗舰（天玑 9600、骁龙 8 Elite Gen 6、A20）集中在 9 月。
- **内存价格是最大的外部变量。** LPDRAM 涨价可能让 2026 年手机端侧模型的“可用内存”不增反降，这会推动 INT4/更低比特量化、MoE 与端云协同加速落地。

## 4. 低功耗、存内计算与内存：把数据搬运从功耗账本里拿掉

**总判断**：5月底至6月底这一个月，端侧低功耗AI硬件的主线不是"更大的TOPS"，而是**把数据搬运从功耗账本里拿掉**——学术界在VLSI 2026上集中展示数字/浮点存内计算（DCIM/FP-CIM）进入2nm与可穿戴NPU，产业界则在存储侧推进LPDDR6-PIM标准、UFS 5.0与LPDDR5X新密度。同时，AWE 2026把"AI眼镜"推到台前，常开（always-on）子任务正在从通用NPU剥离到专用ASIC。

### 一、VLSI 2026：存内计算从"宏"走向"产品化IP"与可穿戴NPU

[VLSI 2026](https://www.proceedings.com/content/086/086455webtoc.pdf)（6月14-18日，檀香山）主题为"Advancing the AI Frontier through VLSI Innovation"，投稿首次超过1000篇、录用251篇，中国内地入选33篇（[OFweek](https://ee.ofweek.com/2026-06/ART-8320315-8440-30690062.html)，媒体口径）。与端侧低功耗AI相关的代表性论文如下：

| 论文 | 机构 | 工艺 | 关键指标（论文/标题口径） | 端侧意义 |
|---|---|---|---|---|
| TinyNPU（C21.1） | 联发科 | 3nm | DCIM，512×8b MAC，256KB，1.47 TOPS，0.06-134.36 µJ/token，眼镜续航最长10天 | 可穿戴常开推理岛 |
| DCIM编译器（C8.1） | 台积电 | 2nm | 234.4 TOPS/W，511.9 TOPS/mm²，≤0.38V | CIM宏编译器化 |
| HCNP | Kyuho J. Lee组 | 未披露 | 70.2 TOPS/W，CIM+NPU混合 | XR头显CNN/Transformer |
| µAgent | Stanford/TSMC | 7nm | 404.3 mJ/Action，4-bit混合格式 | 端侧智能体 |
| 推理LLM加速器 | 北京大学 | 未披露 | 122.2 µJ/token，两级KV压缩 | 推理模型KV瓶颈 |
| FP8 CIM宏 | 华中科技大学 | 40nm | 24.85-80.59 TFLOPS/W | 端侧Transformer浮点CIM |
| 浮点CIM宏 | 尹首一/涂锋斌等 | 28nm | 44.15 TFLOPS/W，ASIL-D | 车规CIM |
| Event-Gaze | Georgia Tech | 28nm | 12.88mW，441µs | XR眼动常开 |

几点技术判断：

1. **DCIM进入先进制程并"编译器化"**。台积电2nm DCIM编译器达到234.4 TOPS/W、511.9 TOPS/mm²（[Mynavi](https://news.mynavi.jp/techplus/article/vlsi2026-8/)），对比其VLSI 2025上3nm编译器124.6 TOPS/W@0.5V（[VLSI 2025程序](https://archive.vlsisymposium.org/25web/wp-content/uploads/VLSI2025_Advanceprogram0611.pdf)），一代约1.9倍。编译器化意味着CIM宏将像SRAM宏一样交付给SoC客户。
2. **联发科TinyNPU首次把"常开推理"做成独立指标**。以µJ/token而非TOPS衡量，512个MAC、256KB片上存储、裸片约0.25mm²，说明可穿戴上的"小语言模型常开"是一个与手机NPU完全不同的设计点：容量极小、全片上、权重驻留。
3. **浮点CIM成熟**。华科40nm FP8 CIM（24.85-80.59 TFLOPS/W，较后对齐方案最高6.66倍，[集微网](https://www.laoyaoba.com/n/1054389)）与28nm ASIL-D浮点CIM并列出现，表明CIM正在解决Transformer激活离群值问题，且国产团队可在成熟制程上做出有竞争力的结果。
4. **能效指标正在"上移"**：TOPS/W → µJ/token（TinyNPU、北大）→ mJ/Action（µAgent）。这反映端侧负载已从单次分类变成多token生成与多步智能体推理，评价体系必须包含访存与KV Cache。

### 二、存储与内存：PIM标准化、UFS 5.0与新密度LPDDR5X

- **LPDDR6-PIM接近定稿**：据[EE Times Japan](https://eetimes.itmedia.co.jp/ee/articles/2606/05/news079.html)（6月5日），JEDEC JC-42.6副主席表示LPDDR6-PIM"大部分核心功能已定义、正在审查细节"；LPDDR6引入x6子通道与非二进制接口，容量目标512GB，并制定LPDDR6 SOCAMM2标准。作为背景，三星8月在Hot Chips公布的LPDDR5X-PIM（窗口外）在Llama-3.1-8B上吞吐从27.0提升到81.3 tokens/s（厂商口径），说明PIM对decode这种GEMV/带宽受限负载收益最大。
- **UFS 5.0**：[三星](https://news.samsung.com/global/samsung-unveils-industrys-fastest-ufs-5-0-solution-for-next-gen-on-device-ai-applications)6月23日发布，顺序读/写10.8/9.5GB/s，能效较UFS 4.1提升40%以上，封装缩小16.7%，Q4量产。对端侧AI的意义在于多模型热切换与大模型冷启动。
- **LPDDR5X仍是2026主力**：[美光FQ3财报](https://www.sec.gov/Archives/edgar/data/723125/000072312526000013/a2026q3ex991-pressrelease.htm)（6月24日）称1γ 16Gb LPDDR5X已在头部手机OEM大批量爬坡、24Gb送样；[Computex](https://finance.yahoo.com/sectors/technology/articles/micron-powers-ai-everywhere-computex-220000858.html)上展示LPCAMM2 9,600MT/s（128-bit，理论约153.6GB/s，推算）以及4600 SSD 1秒内载入13B Llama 2。
- **3D DRAM**：VLSI上SAIMEMORY 9层晶圆堆叠内存（1.125GB/芯片、0.25 Tb/s/mm²、约13.7K TSV），三星16层VS-DRAM与SK海力士4F² VG DRAM，均指向"更高带宽密度、更低每bit能耗"的端侧/近存方案。

| 存储 | 厂商/组织 | 关键数字 | 状态 |
|---|---|---|---|
| UFS 5.0 | 三星 | 10.8/9.5 GB/s，≤1TB，能效+40% | Q4 2026量产 |
| LPDDR5X 1γ | 美光 | 16Gb量产爬坡，24Gb送样 | 6月财报 |
| LPCAMM2 | 美光 | 9,600MT/s，128-bit | 展示 |
| LPDDR6-PIM | JEDEC | 核心功能基本定稿 | 标准制定中 |

### 三、边缘加速器：数字存内计算走向数百TOPS

[Axelera与晶心](https://www.andestech.com/en/2026/06/01/axelera-ai-and-andes-technology-partner-to-power-next-generation-europa-ai-platform-with-high-performance-risc-v-ax65-cores/)6月1日宣布Europa集成AX65 RISC-V主控（13级、4发射乱序，可跑Linux）。Europa峰值629 TOPS，推理由D-IMC（数字存内计算）核承担约99%，正向首批客户送样（正式发布在9月）。对比上一代Metis 214 TOPS、约15 TOPS/W（媒体口径），D-IMC已从"学术宏"走到数百TOPS级边缘产品。BrainChip则以AKD1500（INT4峰值800 GOPS、典型100-200mW，产品简介口径）推出射频信号识别参考平台，平台级功耗<1W。

### 四、可穿戴与AI眼镜：常开任务专用化

- [高通Snapdragon Reality Elite](https://9to5google.com/2026/06/16/snapdragon-reality-elite/)：Hexagon NPU 48 TOPS（+160% vs XR2+ Gen 2），同负载续航+20%、温度最多低12°C；轻量AI眼镜则通过Snapdragon START交钥匙模组推进。模型规模与内存配置未披露。
- [Ganzin EPU2](https://aijourn.com/ganzin-showcases-aurora-ecosystem-at-awe-2026-to-accelerate-eye-tracking-ai-glasses-adoption/)：眼动专用ASIC，功耗约为NPU方案1/4，最高120Hz；学术侧Event-Gaze以12.88mW实现事件相机眼动。
- [酷芯微ARS45](https://www.eet-china.com/news/202606031229.html)：等效6 TOPS NPU（INT8/INT16），0.65-1V DVFS，标题口径300mW。
- MCU侧：[Ambiq heliaCORE](https://s206.q4cdn.com/849744944/files/doc_news/Ambiq-Launches-heliaCORE-for-Real-World-Edge-AI-Deployment-2026.pdf)补齐200+算子，验证963个算子实例（约MLPerf Tiny的12倍）；Ambiq同日以78美元/股增发募资1.56亿美元。Syntiant收购Orosound与AudioSourceRE强化音频前端算法。本窗口内ST、NXP、瑞萨、英飞凌、Nordic未检索到新的NPU MCU发布（最近一批集中在3月Embedded World）。

### 小结

本月最值得记住的三条：其一，**DCIM已进入2nm且编译器化**（台积电234.4 TOPS/W），而联发科TinyNPU用µJ/token定义了可穿戴常开推理；其二，**LPDDR6-PIM标准核心功能基本定稿**，端侧PIM即将从私有方案走向JEDEC通用接口，decode带宽瓶颈有望在内存内部缓解；其三，**AI眼镜芯片呈"三层分工"**——48 TOPS级XR旗舰（puck/头显）、数TOPS级眼镜SoC、mW级眼动/音频专用ASIC。需要注意，本月多数产业数据为厂商口径，模型规模与tokens/s普遍未披露；PIM的实际收益要等8月Hot Chips及后续量产验证。

## 5. 顶会论文：VLSI、MobiSys、ISCA 集中在 decode 与 PIM

6 月是体系结构与移动系统的“顶会月”：[VLSI Symposium 2026](https://news.mynavi.jp/techplus/article/vlsi2026-1/)（6/14-18，檀香山）、[MobiSys 2026](https://www.sigmobile.org/mobisys/2026/awards/)（6/21-25，剑桥）和 [ISCA 2026](https://iscaconf.org/isca2026/program/)（6/27-7/1，罗利）集中召开。总体判断：**端侧 LLM 的研究重心已经从“能不能跑”转到“decode 带宽墙 + 内存容量墙 + 与前台 App 共存”这三件事上**——ISCA 上出现了大批面向边缘/手机的 PIM、LUT 低比特计算和 KV Cache 压缩论文，MobiSys 则集中在“让 NPU 真正接管整张图”和 KV/前缀复用。（MLSys 2026 于 5/18-22 召开、DAC 2026 不在 6 月，均不计入本月条目。）

### 一、PIM/近存计算：从 HBM 走向手机 LPDDR

ISCA 2026 第 1A、2B、3B、4A、10C 等多个 session 都和存内/近存计算有关，其中直接面向手机/边缘的有三篇：

| 论文 | 机构 | 目标场景 | 关键结果（作者口径） |
|---|---|---|---|
| [COSM](https://arxiv.org/abs/2606.30553) | 上海交大等 | 手机 PIM 与 CPU 共享 DRAM | PIM 吞吐最高 2.8x，CPU 损失 <2.0% |
| [P3-LLM](https://arxiv.org/abs/2511.06838v3) | Cornell / KU Leuven / Stanford | 端侧 NPU + DRAM-PIM | vs HBM-PIM 4.9x、vs Ecco 2.0x、vs Pimba 3.4x |
| DIAMoND | 北京大学 | 端侧 MoE，in-NAND + near-DRAM | 未披露 |

- **COSM 解决的是落地问题而不是峰值问题**：手机不可能为 PIM 单独配一组 DRAM，App 与 LLM 必须共享 bank。COSM 修改 DRAM 命令集让 PIM 命令可被 CPU 请求抢占，在控制器里加两条 PIM 专用队列，并用 idleness-aware 调度把 PIM 命令塞进 CPU 访存空隙。这与三星推进 LPDDR-PIM 的方向高度契合——如果 LP-PIM 进入旗舰手机，内存控制器的调度改造是绕不开的配套。
- **P3-LLM 的结论是“PIM 侧别堆 FP16”**：DRAM 工艺下高精度运算单元面积和功耗都贵，作者为权重、激活和 KV Cache 分配混合数值格式，在 PIM 中只放轻量低精度单元，等面积下提升吞吐，再用算子融合消除反量化开销。
- **DIAMoND / SHyLA / Raptor 代表“垂直堆叠”路线**：DIAMoND 把 MoE 专家放进 NAND 内计算；清华的 SHyLA 做 3D 堆叠 NVM-DRAM 混合；d-Matrix 的 [Raptor](https://servethehome.com/d-matrix-raptor-3d-dram-accelerator-for-generative-inference-at-hot-chips-2026) 在 7 月 1 日报告了早期硅：3D DRAM 与 TSMC N4 逻辑 die 面对面键合、取消内存 PHY，每卡 32GB、>100 TB/s，接口能耗实测约 0.376 pJ/bit（[媒体](https://hwbusters.com/news/d-matrix-raptor-drops-the-memory-phy-32gb-at-100-tb-s-against-hbm4s-192gb-at-18/)对比 HBM4 约 2-3 pJ/bit）。Raptor 是数据中心产品，吞吐倍数也来自建模，但“DRAM 与逻辑垂直键合”恰好是 VLSI 2026 上 SAIMEMORY/Intel 3D 高带宽 DRAM（约 0.25 Tb/s/mm²）、三星 16 层垂直堆叠 DRAM 等论文的共同方向，对未来手机 SoC 的带宽墙有参考价值。

### 二、低比特计算：LUT 化成为共识

ISCA Session 3A 同时出现 [OASIS](https://arxiv.org/pdf/2507.23035)（Duke）和 Omni-LUT（NYCU），MobiSys 最佳论文提名 [Vec-LUT](https://arxiv.org/abs/2512.06443)（清华 AIR）也是查表路线，软硬件两端形成呼应：

| 工作 | 层级 | 核心机制 | 结果 |
|---|---|---|---|
| OASIS | 加速器 | 笛卡尔积 LUT，权重/激活双侧非均匀量化，Orizuru top-k 异常值引擎 | LUT 尺寸 -64x、并行度 +1024x；vs FIGLUT 3.00x 速度、1.44x 能效；精度较 FP16 平均降 1.98% |
| Omni-LUT | 加速器 | LUT GEMM + 硬件感知 KV Cache 量化 | 未披露 |
| [EVA](https://arxiv.org/abs/2605.24144) | 加速器 | 向量量化：输入×码本点积，GEMV→GEMM，结构化查表消除 bank 冲突 | 最高 11.17x 速度、7.17x 能效（vs SOTA 查表架构） |
| Vec-LUT | 边缘 CPU 软件 | 跨 token 共享向量 LUT + cache 感知流式查表 | 5 设备×3 模型最高 4.2x，已并入 llama.cpp |

工程含义：端侧 NPU 支持 sub-4bit 的方式不一定是“加更窄的 MAC”，而可以是**查表单元 + 码本缓存**。EVA 把 decode 的 GEMV 改写成 GEMM 尤其值得手机 NPU 团队关注——decode 阶段 MAC 阵列利用率长期偏低，换一种数据通路可同时缓解带宽和利用率。

### 三、Decode 与推理模型：推测解码进入硬件

KAIST 的 [Cassandra](https://arxiv.org/abs/2605.26558) 面向“推理模型在端侧”这一新问题：长思维链让 decode 成为主导开销。它不训练独立草稿模型，而是对权重和 KV Cache 做剪枝 + 尾数截断得到“自身低精度视图”作草稿，全精度并行验证保证无损；再配一个可嵌入商用 GPU/NPU 的格式编解码模块。结果：相对 BF16 最高 2.41x；Llama 3 8B @ RTX 4090 同内存预算下生成 token 数是 Eagle-3 的 1.81x。同一方向上，MobiSys 的 [Agent-X](https://www.emergentmind.com/papers/2605.10380)（KAIST Minsoo Rhu 组）用 n-gram 推测解码 + prompt 重构匹配前缀缓存，在端侧 Agent 负载上端到端 1.61x、无精度损失。

### 四、NPU 接管全图：MobiSys 的系统视角

- [ShadowNPU](https://arxiv.org/abs/2508.16703)（北大/北邮）直面一个工程顽疾：attention 因量化敏感从 NPU 回退到 CPU/GPU。它用稀疏注意力只精算少量 token，并把“挑 token”的开销藏在 NPU 的 pilot 计算里，配合计算图分桶和 head 级 NPU-CPU/GPU 流水线。[MobiSys 公开评审](https://www.sigmobile.org/mobisys/2026/accepted_papers/)记录其在 Hexagon NPU 上最高 4.5x 端到端加速、7.7x 能耗降低、0.4pp 精度损失。
- [KVSwap](https://arxiv.org/abs/2511.11907v2)（Leeds）把完整 KV Cache 下沉到闪存，内存只存紧凑 K 表示做预测与预取，适配统一内存 + 低 IO 带宽的端侧特征。
- VLMCache 做端侧 VLM 的 KV 前缀复用；BUPT/字节跳动的 TurboInfer 与 MLSys 的 CORE 一样，说明**持续负载下的 DVFS 与热管理**已成为端侧 LLM 的独立研究课题。
- 边缘视觉方面，首尔大学 Ouroboros 在 Jetson Orin 上以运动感知 ViT 实现最高 87.0% 计算削减、2.61x 加速、64.5% 节能。

### 五、MoE 上端：容量墙的两种解法

南京大学 [SMoE](https://arxiv.org/pdf/2508.18983) 用“相似专家替换”提高 GPU 专家命中率（Qwen2-57B-A14B @ A6000 达 71%，预取专家数 3→1），并刻意避开依赖 AMX/AVX-512 的 kTransformers 路线以适配边缘 CPU；北大 DIAMoND 则从硬件侧把专家放进 NAND 内计算。ISCA 还有上交大 STEP（时空专家预取）等 MoE 论文，说明 MoE 端侧化已成为体系结构界的热点。

### 小结

本月顶会给端侧 AI 硬件的信号很清晰：**（1）带宽墙**——PIM 正从 HBM 走向 LPDDR，研究焦点转为与 CPU 共享内存的调度（COSM）和低精度 PIM 单元（P3-LLM）；**（2）低比特**——LUT/向量量化取代“更窄 MAC”成为 sub-4bit 主线（OASIS、EVA、Vec-LUT）；**（3）decode 加速**——推测解码开始配专用硬件（Cassandra）；**（4）系统层**——让 NPU 不回退（ShadowNPU）、把 KV 下沉到闪存（KVSwap）。VLSI 2026 本身公开的端侧 AI 芯片细节有限（[EE Times Japan](https://eetimes.itmedia.co.jp/ee/articles/2605/08/news043.html) 报道共 1,041 篇投稿、录用 237 篇），更多亮点在 3D DRAM 堆叠，这与 Raptor 共同指向下一代内存层级。需注意：Omni-LUT、DIAMoND、DynoPipe、TurboInfer 等论文目前仅有程序表或标题信息，数字未披露；ShadowNPU、Ouroboros 的数字来自会议公开评审摘要，均待全文核实。

## 6. 6 月 arXiv 端侧硬件论文精选

6月（2026-05-29 ~ 07-01）arXiv上的端侧硬件论文有一个很清晰的共同结论：**NPU的价值集中在预填充、编码器和视觉前端，自回归解码仍然被内存带宽和调度开销卡住**。高通Hexagon、AMD XDNA2、Apple ANE三条路线的独立实测都指向这一点；与此同时，研究重心正从“能不能跑”转向“跑得多省电、多凉快”，DVFS、内存频率和温控开始成为一等公民。

### 背景：为什么6月的论文集中在“分阶段”

LLM推理分为预填充（一次性处理整段提示，矩阵乘为主，计算受限）与解码（逐token生成，矩阵-向量乘为主，带宽受限）两个阶段。端侧SoC的NPU标称算力已从骁龙8 Gen 3的45 TOPS涨到8 Elite Gen 5的89.4 TOPS（[llada.cpp论文表格口径](https://arxiv.org/abs/2606.13740)），但手机/PC的LPDDR带宽增长远慢于算力。于是“哪个阶段放哪个处理器”成了本月几乎所有实测论文的主线：它们不再只报一个端到端tok/s，而是把预填充、解码、编码器、冷启动、温度分开测。这种测量范式本身就是6月最值得关注的变化。

### 一、NPU实测：预填充大幅领先，解码只有小幅收益

本月最有参考价值的是三篇真机实测，覆盖PC与手机两类高通平台和AMD AI PC：

| 论文 | 平台 | 模型 | 预填充（NPU vs 基线） | 解码（NPU vs 基线） | 能耗/热 |
|---|---|---|---|---|---|
| [端侧RAG on X Elite](https://arxiv.org/abs/2606.11257) | Snapdragon X Elite，Hexagon 45 TOPS | Qwen3-4B | 786.66 vs CPU 43.36 tok/s（18.1×） | 14.19 vs 8.17 tok/s（1.7×） | 单查询约315 J vs 1,251 J |
| [Phase Matters](https://arxiv.org/abs/2606.27906) | Snapdragon 8 Elite（SM8750） | FastVLM-0.5B | 197.4 vs 120.6 tok/s（1.64×） | 113.1 vs 95.5 tok/s（1.18×） | 能耗低2.52×，稳态温度低10.47 °C |
| [TileFuse](https://arxiv.org/abs/2606.11357) | Ryzen AI 7 350 / HX 370（XDNA2） | Llama3-8B W4A16 | 2K上下文4.13 s vs iGPU 8.25 s（2.0×） | 论文称NPU不如iGPU | 能耗降64.6% / 52.8% |

三者的模式高度一致：预填充是计算密集型，NPU的INT8/INT4矩阵算力可以兑现10倍级优势；解码每token要把全部权重读一遍，瓶颈在LPDDR带宽（AMD两平台名义约128 GB/s），NPU与CPU/GPU共享同一条内存通道，收益只剩1.2–1.7倍甚至落后。X Elite那篇还给出一个容易被忽视的事实：三端整机平均功耗几乎都在32–33 W，**NPU的节能几乎完全来自“更快完成”**，而非更低的瞬时功耗。

同时要注意几处“坑”：Hexagon静态图迫使RAG分块从2,500字符缩到1,000字符，FinDER压力测试中NPU实质回答率仅9.2%（CPU 44.2%）；SM8750上NPU执行器初始化就要536 ms，冷启动纯NPU管线26.8 s，热态才2.08 s——常驻场景必须保持执行器热态。另外，X Elite论文贡献列表里“能耗降19.2倍”与结果表的4.0倍不一致，引用请以4.0倍为准。

### 二、Apple Silicon：ANE被“拆开”，GPU路径被重新榨干

6月出现了一批针对苹果芯片的逆向和底层优化工作：

- [Apple Neural Engine手册](https://arxiv.org/abs/2606.22283)（302页）基于M1/M5实测与固件反编译给出ANE的roofline：M1上fp16计算顶约12 TFLOP/s（饱和大矩阵乘约4.8），DRAM顶85 GB/s，ridge点141 FLOP/byte，**2 MB片上工作集是硬阈值**；单次dispatch下限约0.23 ms，而一个Transformer层每token要发40–50次dispatch。作者结论很直接：“ANE跑编码器，不跑解码器”。它还揭示M1基础版HAL只读出4个架构核心（宣传为16核），M5为16核；int8仿射权重在M1上会展开成fp16（省存储不省带宽），A14/M2起才原生流式。
- [ANEForge](https://arxiv.org/abs/2606.17090)把这条直接路径做成Python包：58个融合算子，小程序单次约90 µs（接近约70 µs下限），还能在ANE上跑反向与优化器更新。
- [Rigel](https://arxiv.org/abs/2606.12765)在M4 Max上证明Metal 4.1的fp8 matmul2d是模拟实现，吞吐只有fp16的0.94倍，且没有专用矩阵通路——在M4上fp8只是省内存的手段。
- [BaseRT](https://arxiv.org/abs/2607.00501)用原生Metal在M4 Pro（273 GB/s）上把Qwen3-0.6B解码做到464.5 tok/s（llama.cpp 297.4），Qwen3-30B-A3B Q4解码84.1 tok/s、预填充738 tok/s；值得注意的是对手uzu借助ANE在多数预填充配置上领先。
- [M1 AMX预填充GEMM](https://arxiv.org/abs/2606.25426)则显示CPU旁的矩阵协处理器仍有余量：填满第二个AMX块+权重预打包，让llama.cpp预填充从291升到420 tokens/s（1.44×，逐位一致）。

合在一起看，苹果平台的分工已被第三方实测清楚刻画：**预填充/编码器→ANE（或AMX），解码→GPU+统一内存带宽**。

### 三、新解码范式与常驻语音：把动态计算改造成NPU友好的形状

[llada.cpp](https://arxiv.org/abs/2606.13740)（清华/北航）是首个面向手机Hexagon NPU的扩散语言模型推理框架：在OnePlus Ace5 Pro（8 Elite，16 GB）上，LLaDA-8B单步去噪128 token从CPU 14.76 s降到NPU 1.53 s，加上多块推测解码与交换优化内存运行时后，128 token GSM8K任务从2996 s降到16.1 s，相对同尺寸自回归Llama-3-8B最高快3.9倍。扩散式并行去噪把“解码”变成了稠密矩阵运算，天然契合NPU，是绕开解码带宽墙的一条值得跟踪的路线。论文同时记录了三代骁龙NPU的INT8算力口径：8 Gen 3 45 TOPS、8 Elite 65.25 TOPS、8 Elite Gen 5 89.4 TOPS。

[NPUsper](https://arxiv.org/abs/2607.01108)把Whisper的自回归解码按K步编译成分块图（受控展开），在Galaxy S25上平均功耗仅0.46 W（基线2.94–4.05 W），TTFT最多降33.2倍，代价是WER比最佳基线高约3个百分点。这说明“常驻语音”类负载可以在NPU上做到亚瓦级。

### 四、MoE上端：总参数决定成本，专家卸载靠预取

[UNB的实证研究](https://arxiv.org/abs/2606.21428)在Jetson Orin Nano 8 GB上发现，OLMoE-1B-7B（1.3B激活）比同激活量的Llama-3.2-1B慢约31%、每token能耗0.96 J vs 0.45 J，峰值内存8.01 GiB顶到上限——**在带宽受限设备上成本跟总参数走，不跟激活参数走**。[SpecPrefetch](https://arxiv.org/abs/2607.24787)则针对把专家放到存储上的方案，用轻量适配器预测下一层专家并异步预取，在8 Elite设备上解码吞吐最多提升约20%（Slow UFS设置），但绝对值只有约4 tok/s（DeepSeek-VL2-Tiny），说明闪存卸载MoE离实用仍有距离。

### 五、能耗与温控成为一等公民

- [EnerInfer](https://arxiv.org/abs/2606.23001)（华为/TUM/上交）指出峰值频率下手机外壳约100 s就超42 °C；适度降低NPU与DDR频率，在5 tok/s体验目标下高端手机tokens/J提升50–65%，热约束下多产出27.9% token。
- [Jetson调速器](https://arxiv.org/abs/2606.16106)证明不感知内存时钟（EMC）的DVFS在紧截止期会漏掉25–28%周期，感知后≤0.9%。
- [Keyword Matters](https://arxiv.org/abs/2607.22568)在Pixel 9a上测得提示关键词可使解码能耗相差-18.5%到+26.5%。

三者共同说明：端侧LLM的续航与体感不只由TOPS决定，**内存频率、温度轨迹和输出长度**同样是可调变量。

### 六、PIM与超低功耗芯片

存内计算方向本月以仿真为主：[PALUTE](https://arxiv.org/abs/2606.08891)（UCSD/EPFL，ISLPED 2026）在768层单片3D DRAM里做LUT查表，Qwen3-4B W4A4仿真1,264 TPS@0.16 W，但其面积效率低于CHIME/FIGLUT，且摘要“对FIGLUT能效1.6×”与表格不符；[RH+](https://arxiv.org/abs/2606.05511)指出HBM3-PIM上GEMV受行周期nRC（为nCCDAB的10–11倍）支配，仅改步长即获8–12倍加速。硅实测方面，ETH/博洛尼亚的[CHIMERA](https://arxiv.org/abs/2606.02358) AI-MCU（22 nm FDX，3.19 mm²）在0.6 V下3.1 TOPS/W，550 MHz时896 GOPS@600 mW，可作为可穿戴Transformer推理的参考设计点。

### 七、异构调度与机器人

Intel参与的[BIDENT](https://arxiv.org/abs/2606.05271)在Lunar Lake上把算子级CPU/GPU/NPU映射建成最短路问题，并发场景比朴素多PU放置快2.28倍、能耗平均降48.2%；[vla.cpp](https://arxiv.org/abs/2606.08094)让三值权重BitVLA在8 GB Orin Nano上完成200/200个LIBERO-Object回合，三值tensor-core核提速4.0–4.6倍。

### 八、本月论文中的“能跑多大模型”速查

| 平台 | 模型（精度） | 实测 | 来源 |
|---|---|---|---|
| M4 Pro 24 GB | Qwen3-30B-A3B（Q4） | 解码84.1 tok/s，预填充738 tok/s | [BaseRT](https://arxiv.org/abs/2607.00501)（作者自测） |
| Ryzen AI 7 350 | Llama3-8B（W4A16） | 1K上下文预填充501.9 tok/s | [TileFuse](https://arxiv.org/abs/2606.11357) |
| 8 Elite手机16 GB | LLaDA-8B（Q4_0，扩散LLM） | 128 token任务16.1 s | [llada.cpp](https://arxiv.org/abs/2606.13740) |
| X Elite笔记本64 GB | Qwen3-4B + 嵌入 + 重排 | 解码14.19 tok/s，TTFT 1.30 s | [端侧RAG](https://arxiv.org/abs/2606.11257) |
| Jetson Orin Nano 8 GB | OLMoE-1B-7B（Q4_K_M） | 22.9 tok/s，0.96 J/token，内存8.01 GiB触顶 | [MoE实证](https://arxiv.org/abs/2606.21428) |
| 8 Elite手机 | FastVLM-0.5B（W4A8混合） | 预填充197.4 / 解码113.1 tok/s | [Phase Matters](https://arxiv.org/abs/2606.27906) |
| Galaxy S25 | Whisper base | 平均功耗0.46 W；large版OOM | [NPUsper](https://arxiv.org/abs/2607.01108) |

可以看到，手机端实测的主流仍是0.5B–4B稠密模型，8B级只有在扩散LLM或NPU专门适配下才出现；30B级MoE目前只在24 GB以上统一内存的Mac上跑得顺。

### 小结

6月论文给端侧AI硬件画出了相当一致的图景：**NPU已能在预填充、编码器、语音这类计算密集或可静态化的负载上带来10–40倍加速和数倍节能，但自回归解码仍是带宽问题**。对芯片厂商，下一步的关键不是继续堆TOPS，而是提升LPDDR带宽、降低NPU dispatch/初始化开销、放宽静态图限制；对软件栈，扩散解码、分块展开、算子级异构调度和频率/温控协同是正在成形的方向。需要提醒的是，多篇论文存在摘要与正文口径不一致（X Elite RAG、PALUTE、EnerInfer），引用具体倍数时应以正文表格为准。

## 7. 总结：对端侧智能体意味着什么，以及 7 月该看什么

**对端侧智能体的含义**

1. **模型规模的上限由“内存层级”决定，而不只是 DRAM。** Apple 的 20B 稀疏模型（闪存存全量、按请求载入 1–4B）、MoE 专家分页（SpecPrefetch、SMoE）和 KV 卸载到闪存（KVSwap）是同一条路线：手机 DRAM 在 2026–2027 年难以增长，更大的模型要靠闪存带宽（UFS 5.0 约 10GB/s）和激活参数少的结构。
2. **NPU 的价值在 prefill、编码器和常驻小模型，decode 仍由带宽和软件决定。** 6 月的真机实测在 Hexagon、XDNA2、ANE 三条路线上给出一致结论；最划算的优化是让 NPU 接管整张图、减少调用和冷启动开销，并协同调 NPU 与 DDR 频率（EnerInfer 在手机上提升 tokens/J 50–65%）。
3. **分层部署更清晰。** 眼镜和 XR 端只跑感知和 3B 以下模型（Reality Elite 3B @ 45 tok/s 是目前公开的最高口径），手机常驻 3B、按需调用稀疏 20B，PC 与车机承担 10B–100B 级模型，最大的模型（Apple PCC、Cloud Pro）仍在云端 GPU 上。
4. **对厂商口径保持怀疑。** “可跑 120B / 300B / 1T”通常只说明内存装得下；要看是否 MoE、激活多少参数、什么精度、多大上下文。用带宽除以每 token 读取字节数，就能做第一轮核实。

**留给 7 月的问题（结论已写在 7 月硬件洞察）**

- decode 瓶颈能否在软件层缓解：7 月清华/北交大在 4 款骁龙手机上实测 NPU decode 不如 CPU，“prefill 归 NPU、decode 归 CPU”成为实测结论。
- 内存涨价对芯片厂的影响：7 月财报显示高通、联发科手机收入都降约 20%，内存厂利润几乎全部来自 HBM。
- 存内计算和近存能否落地：7 月 WAIC 上后摩 M50、东方算芯 DF1000 等国产存算/近存芯片集中亮相，高通 HBC Gen 1 流片。

> 口径说明：标“官方”的是厂商发布的数字，“媒体实测”和“第三方实测”是独立测试，“爆料”未经确认，“推算”或“估算”是本文按公开参数计算的结果。6 月部分方向没有检索到新品：高通和 Apple 都没有新的手机 SoC，ST、NXP、Renesas、Hailo、DeepX、知存、苹芯、后摩等在窗口内没有可核实的新动态；VLSI 和 MobiSys 的部分论文只有标题或评审摘要，已在对应条目标为“未披露”。
