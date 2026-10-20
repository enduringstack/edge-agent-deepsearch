# 硬件洞察：端侧 AI 芯片月报（2026-02-27 ~ 2026-03-26）

> **说明：** 本期为 2026-10 回填，规则同周报硬件雷达；TrendForce 3 月 23 日的手机存储报告被三个方向重复收录，只计一次，全月去重后 87 条。3 月素材检索时 WebSearch 额度已用完，华为、紫光展锐和国产存算方向主要靠官网直查，覆盖不足（见第 7 节口径说明）。
>
> **一句话结论：3 月是“硬件铺底、软件提速”的一个月。** Apple 三天内更新了从 iPhone 17e 到 M5 Max 的整条产品线，高通把 NPU 放进手表，SK 海力士 LPDDR6 完成开发验证，但没有新的手机旗舰 SoC。真正让端侧 LLM 变快的是软件：同一颗骁龙 8 至尊版第五代，自推测解码把 3B 模型从约 33 提到约 58 tok/s。英伟达把 RTX PC 和 DGX Spark 定位成跑常驻 Agent 的“Agent 电脑”；美光移动与客户端内存毛利率升到 79%，内存账单继续压着终端配置。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断与时间线；第 1–6 节依次为 高通 / Apple 与 Google / 其他 SoC 与 PC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选；第 7 节总结对端侧智能体的含义和 4 月观察清单。逐条动态见 02-27、03-06、03-13、03-20 四周首页的“硬件雷达”。

## 0. 总览：3 月的五个判断

**判断一：Apple 全线配上 GPU 矩阵单元，“AI 快 4 倍”说的是 prefill，decode 仍看带宽。**

| 发布 | 数字 | 口径 |
|---|---|---|
| [M5 Pro / M5 Max](https://www.apple.com/newsroom/2026/03/apple-debuts-m5-pro-and-m5-max-to-supercharge-the-most-demanding-pro-workflows/)（03-03） | 两颗 3nm 裸片封成一颗 SoC，每个 GPU 核带 Neural Accelerator；Pro 最高 64GB、307GB/s，Max 最高 128GB、614GB/s；LLM prefill 最高比 M4 Pro/Max 快 4 倍 | 官方 |
| [MacBook Air M5](https://www.apple.com/newsroom/2026/03/apple-introduces-the-new-macbook-air-with-m5/)（03-03） | 带宽 153GB/s（+28%）；AI 任务最高比 M4 版快 4 倍 | 官方 |
| [MacBook Neo](https://www.apple.com/newsroom/2026/03/say-hello-to-macbook-neo/)（03-04） | A18 Pro、固定 8GB、60GB/s，599 美元起；端侧 AI 滤镜比 8GB 的 Core Ultra 5 笔记本最高快 3 倍 | 官方（对比条件由 Apple 选定） |
| [iPad Air M4](https://www.apple.com/newsroom/2026/03/apple-introduces-the-new-ipad-air-powered-by-m4/)（03-02） | 内存 8GB → 12GB、120GB/s；同日 iPhone 17e 下放 A19，内存未公布 | 官方 |

M5 Max 的带宽只比 M4 Max 的 546GB/s 高约 12%。按“带宽 ÷ 每 token 读取字节数”推算，27B 稠密 4bit 模型 decode 上限约 38 tok/s，MacBook Neo 适合 3B 级 4bit 模型（上限约 30 tok/s）。Neural Engine 依旧不公布 TOPS，窗口内也没有带 tok/s 的第三方 M5 Pro/Max 实测。

**判断二：端侧 LLM 的提速来自软件，不来自新芯片。**

| 证据 | 数字 | 口径 |
|---|---|---|
| [AI Hub 0.48.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.48.0)（03-12） | Qwen3-4B w4a16、4K 上下文：8 至尊版第五代 29.03、X2 Elite 29.99、X Elite 14.79 tok/s | 官方 perf.yaml |
| [AI Hub 0.49.1](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.49.1)（03-24） | Llama 3.2 3B 自推测解码：8 至尊版第五代 32.65 → 57.79（1.77 倍），X Elite 2.28 倍，车规 SA8775P 1.54 倍 | 官方（短提示、长回答） |
| [MobileLLM-Flash](https://arxiv.org/abs/2603.15954)（03-16） | 1.4B W4A8，Galaxy S25 CPU 4 线程，1k 上下文解码 60.52 tok/s | 论文实测 |
| [Bielik 11B 推测解码](https://arxiv.org/abs/2604.16368)（03-22） | M2 Pro 基线 14.6–15.1 tok/s，只在结构化文本上最多快 1.7 倍 | 论文实测 |

带宽越紧的平台，推测解码收益越大；Bielik 则说明它不是必然加速，要看接受率。2 月月报问 Hexagon-MLIR 能否给出端到端 LLM 数据，3 月高通又补了 XNNPACK 接入 HVX（QD8 TransformerBlock 仅 1.1–3.5 倍），两条开源路径都还没有端到端 LLM 结果。

**判断三：带安全运行时的本地常驻 Agent 先在 PC 上成套，手机仍是端云混合。**

| 发布 | 数字 | 口径 |
|---|---|---|
| [NemoClaw](https://nvidianews.nvidia.com/news/nvidia-announces-nemoclaw)（03-16） | Nemotron 模型加开源 OpenShell 运行时，按策略管控工具、网络与隐私 | 官方 |
| [RTX AI Garage](https://blogs.nvidia.com/blog/rtx-ai-garage-gtc-2026-nemoclaw)（03-17） | Nemotron 3 Super 120B 总参 / 12B 激活；DGX Spark 128GB，称可跑 120B+ | 官方 |
| [Arc Pro B70](https://www.phoronix.com/news/Intel-Arc-Pro-B70-Announced)（03-25） | 32GB、608GB/s、367 INT8 TOPS、949 美元 | 媒体转述官方 |
| [Nexa 智能体上骁龙 X](https://www.qualcomm.com/developer/blog/2026/03/run-nexa-ai-agents-locally-on-snapdragon-pc-with-hexagon-npu)（03-19） | NPU 模型预算约 4B；X2 系列 NPU 最高 80 TOPS | 官方 |

DGX Spark 带宽 273GB/s，Nemotron 3 Super 以 NVFP4 每 token 读约 6GB，decode 上限约 45 tok/s，同规模稠密模型只有约 4.5 tok/s（推算）。手机侧，Pixel 上线 Gemini 多步任务 beta（官方），iOS 27 据报将让 App 内智能体接入 Siri（爆料）；报道称 PCC 平均利用率仅约 10%、新 Siri 将跑在 Google 数据中心（媒体）。

**判断四：带宽墙和持续性能成了实测焦点。**

| 证据 | 数字 | 口径 |
|---|---|---|
| [VLA 在 Orin/Thor 上](https://arxiv.org/abs/2603.02271)（03-01） | Thor 算力是 Orin 的 5 倍，端到端只快 1.4 倍；带宽 273 vs 203GB/s | 论文实测 |
| [四平台持续负载](https://arxiv.org/abs/2603.23640)（03-24） | 1.5B 4bit：iPhone 16 Pro 37.58 → 22.56 tok/s；S24 Ultra 9.93 tok/s，第 6 轮降频后终止；Hailo-10H 6.914 tok/s、270.5 mJ/token | 论文实测 |
| [Wear Elite](https://www.qualcomm.com/news/releases/2026/03/qualcomm-powers-the-rise-of-personal-ai-with-new-snapdragon-wear)（03-02） | 3nm、12 TOPS、称可跑 2B；16-bit LPDDR5-6400 下 2B INT4 上限约 12 tok/s | 官方 / 媒体 / 推算 |
| [SK 海力士 1c LPDDR6](https://news.skhynix.com/1c-lpddr6-development-2026/)（03-10） | 10.7Gbps 以上，比 LPDDR5X 快 33%，功耗降 20% 以上，下半年供货 | 官方 |

S24 Ultra 的实测只有带宽上限（约 85–95 tok/s，推算）的十分之一左右，先撞上的是软件路径和温控。ASPLOS 2026 的端侧论文也集中在少搬数据：[FlashMem](https://doi.org/10.1145/3779212.3790164) 在手机 GPU 上流式加载权重，几何平均比 LiteRT 快 1.7 倍；三星 PIM-SHERPA 让手机 LPDDR-PIM 免存两份权重（解码为仿真）。

**判断五：内存账单扩散到整机和代工，NPU 则下沉到 1 美元 MCU。**

| 信号 | 数字 | 口径 |
|---|---|---|
| [美光 FQ2](https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-results-second-quarter-fiscal-2026)（03-18） | 移动与客户端毛利率 79%（去年同期 15%）；FQ3 毛利率指引约 81% | 官方 |
| [SK 集团会长](https://www.electronicsweekly.com/news/business/memory-shortage-to-last-4-5-years-says-sk-boss-2026-03/)（03-16） | 晶圆缺口超过 20%，短缺或持续到 2030 年 | 媒体转述（官方稿无此句） |
| [TrendForce 笔记本](https://www.trendforce.com/presscenter/news/20260310-12959.html)（03-10） | DRAM+SSD 占 BOM 从约 15% 升到 30% 以上，内存与 CPU 合计占比约 45% → 约 58%，零售价或涨近 40% | 第三方预测 |
| [TI TinyEngine MCU](https://www.ti.com/about-ti/newsroom/news-releases/2026/2026-03-10-ti-expands-microcontroller-portfolio-and-software-ecosystem-to-enable-edge-ai-in-every-device.html)（03-10） | Cortex-M0+ 加 2.56 GOPS NPU，千片单价低于 1 美元 | 官方 |

2 月月报的判断是“内存成为端侧模型规模的上限”；3 月成本开始向整机和代工传导，美光移动与客户端业务的毛利率首次高过数据中心业务。低端方向相反，NPU 正进入 MCU 和无线芯片（NXP、Nordic、Synaptics），但各家只给相对倍数，没有可横向比较的 μJ/推理。

### 3 月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 03-01~02 | 联发科天玑 9500 驱动 AI 眼镜；iPhone 17e、iPad Air M4；Wear Elite；锐龙 AI 400 台式机；Nordic nRF92；爆料 Core AI、报道 PCC 利用率约 10% | Apple / 高通 / PC |
| 03-03~05 | M5 Pro/Max、MacBook Air M5、MacBook Neo；Pixel Drop 多步任务；ST HSP；Ambiq Atomiq | Apple / Google / 低功耗 |
| 03-06~09 | Orion 编程 ANE；Arduino VENTUNO Q、NEURA 合作；NXP i.MX 93W | 研究 / 机器人 |
| 03-10~12 | SK 海力士 LPDDR6；Embedded World（TI、BrainChip、Synaptics、DEEPX）；PIM-SHERPA；AI Hub 0.48.0；MLX 调优 M5；爆料 iPhone Fold 12GB | 内存 / MCU / 软件 |
| 03-16~17 | GTC：NemoClaw、Vera Rubin 与 Groq 3 LPU、HBM4E；SK 会长谈短缺；AXClaw Box；MobileLLM-Flash；LiteRT 2.1.3 | PC / 内存 / 软件 |
| 03-18~19 | 美光 FQ2；Nexa 智能体上骁龙 X；TrendForce 代工预测 | 内存 / PC / 产业 |
| 03-22~23 | ASPLOS 开幕；XNNPACK 接入 HVX；TrendForce 手机存储；Apple 宣布 WWDC26 | 研究 / 软件 / 存储 |
| 03-24 | AI Hub 0.49.1；TurboQuant；Arm AGI CPU；iOS 26.4 未含 Gemini 版 Siri；四平台持续负载实测 | 软件 / 产业 / 研究 |
| 03-25~26 | Arc Pro B70；ASPLOS（FlashMem、最佳论文 FlexiFlow、HNLPU、M2XFP）；爆料 Siri 智能体扩展 | PC / 研究 / Apple |

## 1. 高通：Wear Elite 首次带 NPU、自投机解码与 XNNPACK 接入 Hexagon

### 本月概览：可穿戴上 NPU，软件栈继续提速

2026-02-27 ~ 2026-03-26 这四周，高通依然没有发布新的手机或 PC SoC：手机旗舰要等 9 月骁龙峰会，6 Gen 5 / 4 Gen 5 等中低端平台也不在本窗口。本月的硬件主角是 3 月 2 日 MWC 上的 [Snapdragon Wear Elite](https://www.qualcomm.com/news/releases/2026/03/qualcomm-powers-the-rise-of-personal-ai-with-new-snapdragon-wear)。这是骁龙可穿戴产品线第一次集成 Hexagon NPU，官方给出 3nm、12 TOPS、可跑 20 亿参数模型。同一天高通还发布了 [X105 5G 调制解调器](https://www.qualcomm.com/news/releases/2026/03/qualcomm-announces-5g-advanced-leap-with-qualcomm-x105-5g-modem-)、[FastConnect 8800 与 Wi-Fi 8 产品线](https://www.qualcomm.com/news/releases/2026/03/qualcomm-debuts-ai-native-wifi-8-portfolio-unifying-client-and-n)，并展示了 [AI200 推理机架](https://www.qualcomm.com/news/onq/2026/03/ai-inference-that-scales-qualcomm-ai200-infrastructure-management-suite)。

软件栈是本月第二条主线，而且数字比硬件更硬。[AI Hub Models 0.48.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.48.0) 上架 Qwen3-4B，官方实测在骁龙 8 至尊版第五代上 4K 上下文约 29 tok/s。[0.49.1](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.49.1) 给 Llama 3.2 3B 加了自推测解码，同一平台从 32.65 提到 57.79 tok/s。开发者博客则宣布 [XNNPACK 接入 Hexagon HVX](https://www.qualcomm.com/developer/blog/2026/03/bringing-xnnpack-hexagon-npu)，让 LiteRT、ExecuTorch、ONNX Runtime 的默认 CPU 后端也能卸载到 NPU。第三条线是物理 AI：[Arduino VENTUNO Q](https://www.qualcomm.com/news/releases/2026/03/arduino-announces-arduino-ventuno-q----powered-by-qualcomm-drago)、[NEURA Robotics 合作](https://www.qualcomm.com/news/releases/2026/03/neura-robotics-and-qualcomm--enter-strategic-collaboration-to-ad)、[Wayve 智驾合作](https://www.qualcomm.com/news/releases/2026/03/qualcomm-and-wayve-advance-production-ready----end-to-end-ai-for) 在 3 月 9–10 日集中发布。

与往周的关系：相关各周（02-06、02-13、02-20、02-27）的周报硬件雷达此前都没有收录高通条目，因此本节不需要与已收条目合并。2 月月报已覆盖的 S26 Ultra 用的骁龙 8 至尊版第五代 for Galaxy、Hexagon-MLIR 开源、AI Hub 2 月更新和 2nm 骁龙爆料，这里只作为背景引用。

### 可穿戴：Wear Elite 把“个人 AI”放到手腕上

Wear Elite 的规格分散在几处官方来源。新闻稿写“支持十亿级参数模型”，[官方产品页](https://www.qualcomm.com/wearables/products/snapdragon-wear-elite-platform) 写得更具体：最高 12 TOPS、支持 2B 参数模型、3nm 工艺。对比上代 W5+ Gen 2，单核 CPU 最高 5 倍、GPU 最高 7 倍、日使用时间延长 30%，约 10 分钟可充到 50%（均为官方口径）。媒体补全了其余规格：[GSMArena](https://m.gsmarena.com/snapdragon_wear_elite_arrives_with_ondevice_ai_capabilities_performance_and_battery_gains-news-71793.php) 称 CPU 为 1 个 2.1GHz 主核加 4 个 1.9GHz 性能核；[CNX Software](https://www.cnx-software.com/2026/03/03/qualcomm-snapdragon-wear-elite-wearable-platform-offers-5g-redcap-wifi-6-bluetooth-6-0-built-in-ai-accelerator/) 列出 16-bit LPDDR5-6400 和 32GB eMMC。

“能跑 2B”需要打折理解。16-bit、6400 MT/s 的内存峰值带宽约 12.8 GB/s。2B 模型按 INT4 量化后权重约 1GB，decode 理论上限约 12 tok/s；INT8 约 6 tok/s（以上为推算，未计 KV cache）。因此更现实的分工是：手表上用 0.5B–1B 模型常驻做意图识别、语音唤醒和生活记录摘要，复杂规划交给手机。高通在 3 月底的 [OnQ 博客](https://www.qualcomm.com/news/onq/2026/03/snapdragon-wear-elite-platform) 里也是这么描述“Ecosystem of You”的：可穿戴提供连续上下文，手机和 PC 承担重任务。

连接是 Wear Elite 的另一半卖点。它集成了 5G RedCap、Micro-Power Wi-Fi、蓝牙 6.0、UWB、GNSS 和 NB-NTN 卫星消息，其中 Micro-Power Wi-Fi 明确面向“持续 AI 上下文同步”。Google Wear OS、Motorola（Project Maxwell 概念设备）和三星都在新闻稿中表态，三星确认下一代 Galaxy Watch 采用，首批设备预计“未来几个月”上市。同日发布的 [FastConnect 8800](https://www.qualcomm.com/news/onq/2026/03/fastconnect-8800-ai-ready-connectivity-4x4-wif-fi) 是首个 4×4 手机 Wi-Fi 系统，峰值 11.6 Gbps；[X105](https://www.qualcomm.com/news/releases/2026/03/qualcomm-announces-5g-advanced-leap-with-qualcomm-x105-5g-modem-) 下行峰值 14.8 Gbps，首个 6nm 射频收发器功耗最多降 30%，内置第五代 AI 处理器用“智能体式”流量分类，下半年出货。这些连接芯片决定了端云、端端协同智能体的时延下限。

### 软件栈：模型库、推测解码与开源后端

**AI Hub 模型库。** 0.48.0（3 月 12 日）是本月最有用的数据源。Qwen3-4B w4a16、4096 上下文的官方 [perf.yaml](https://raw.githubusercontent.com/qualcomm/ai-hub-models/v0.48.0/qai_hub_models/models/qwen3_4b/perf.yaml) 实测：8 至尊版第五代 QRD 29.0 tok/s，X2 Elite 30.0，Galaxy S25 25.4，X Elite 14.8，Dragonwing IQ-9075 13.0。X2 Elite 相比 X Elite 约翻倍，工业平台则落后手机旗舰一代以上。该版本还开始支持 LLM 多档上下文编译（512–4096），短对话可以用小上下文换取更低的首 token 时延。

0.49.1（3 月 24 日）新增 Llama-3.2-3B-Instruct-SSD，用单模型自推测解码，官方称输出与原模型逐字一致。同版本数据对比：8 至尊版第五代 32.65→57.79 tok/s（1.77 倍），X2 Elite 42.77→76.39（1.79 倍），X Elite 11.87→27.09（2.28 倍），车规 SA8775P 只有 1.54 倍。端侧解码受带宽限制，推测解码把每次读权重的开销摊到多个 token 上，带宽越紧的平台收益越大，这与数据一致。需要注意，官方测的是短提示、长回答，实际对话中的加速比会随接受率波动。

**XNNPACK 接入 Hexagon。** 3 月 23 日的博客由高通与 Google 工程师联合完成。测试机为 Galaxy S24（骁龙 8 Gen 3），CDSP 时钟 1.92GHz，相对标量基线：MobileNet 子图 8–9 倍，DepthwiseSeparable 约 10 倍，Attention 5–6 倍，纯 GEMM 微内核 50–90 倍，但类 LLM 形状的 GEMM 只有约 31.8 倍，QD8 TransformerBlock 仅 1.1–3.5 倍。FP16 尚未接入，VTCM 也还没用上。高通明说它不替代 QNN，只是“开源友好”的补充。结合 2 月开源的 Hexagon-MLIR，高通的开源 NPU 路径已有两条：面向新算子的编译器，以及面向现有框架的微内核后端。

**量化与 SDK。** [AIMET 2.26.0](https://github.com/qualcomm/aimet/releases/tag/2.26.0) 新增 int2 的 ONNX QDQ 导出和 Qwen3 MoE 原生支持，[2.27.0](https://github.com/qualcomm/aimet/releases/tag/2.27.0) 降低 QDQ 时延并让 SeqMSE 支持断点保存。int2 和 MoE 进入量化工具，预示端侧模型库下一步可能出现更低比特和稀疏激活的模型。第三方 SDK 方面，[NexaSDK for Linux](https://www.qualcomm.com/developer/blog/2026/03/qualcomm-nexa-ai-docker-bring-ai-to-iot-robotics-with-nexasdk-linux) 用 Docker 镜像直通 Dragonwing IQ9（50–100 dense TOPS）和 RB3 Gen 2（12 TOPS）的 NPU，IQ9 上已有 1.5B VLM 和 1.2B LLM。[Nexa 的 PC 博客](https://www.qualcomm.com/developer/blog/2026/03/run-nexa-ai-agents-locally-on-snapdragon-pc-with-hexagon-npu) 重申 X 系列 NPU 45 TOPS、X2 系列 80 TOPS，NPU 模型预算约 4B。[Snapdragon Game AI SDK](https://www.qualcomm.com/developer/blog/2026/03/snapdragon-game-ai-sdk-launch-on-device-ai-in-gaming) 以 UE5 插件形式提供端侧 ASR、量化 LLM 和 TTS，但没有任何时延或功耗数字。AI Hub Workbench 的 [3 月 2 日更新](https://workbench.aihub.qualcomm.com/docs/hub/release_notes.html) 弃用了 qnn_context_binary 目标，改由 compile-and-link API 生成。

### 物理 AI 与汽车：从开发板到整车

3 月 9 日的 VENTUNO Q 是继 UNO Q 之后 Arduino 的第二块高通平台开发板，算力大幅提升：Dragonwing IQ8 系列 NPU 最高 40 dense TOPS，16GB 内存，另配 STM32H5 跑 Zephyr 做实时电机控制，原生 CAN-FD 和 ROS 2，第二季度开售。同日上线的 [Dragonwing Robotics Hub](https://www.qualcomm.com/developer/blog/2026/03/what-qualcomm-dragonwing-robotics-hub-means-for-developers) 把人形、四足、AMR、LeRobot 遥操作等示例放进 Arduino Project Hub。NEURA 合作则面向整机，以 1 月发布的 IQ10 为“大脑”，加上实时控制的“神经系统”，形成混合关键性参考架构，但没有给出算力或时间表。

汽车方面，Wayve 的端到端 AI Driver 被预集成到 Snapdragon Ride 与高通 Active Safety 栈之上，覆盖脱手到脱眼，并探索 L4 Robotaxi。3 月 19 日的 [OnQ 博客](https://www.qualcomm.com/news/onq/2026/03/snapdragon-automotive-market-traction-and-scale) 重申 Q1 FY26 汽车收入 11 亿美元（同比 +15%），设计订单管线约 450 亿美元，这些是 2 月财报的数字，不是新增数据。工业侧，[Embedded World 博客](https://www.qualcomm.com/news/onq/2026/03/how-qualcomm-dragonwing-powers-industrial-edge-ai) 称 Dragonwing 覆盖 1 到 350 dense TOPS，Cloud AI 100 Ultra 单卡 150W 可跑 GPT-OSS 120B。MWC 上与 [西门子的工厂演示](https://www.qualcomm.com/news/releases/2026/03/qualcomm-brings-onpremises-industrial-ai-and-connectivity-to-a-s) 则在工控机的 Cloud AI 100 卡上本地运行故障诊断智能体。[Insight 安防平台博客](https://www.qualcomm.com/news/onq/2026/03/qualcomm-insight-platform-edge-ai-security) 提到 Q-7790 在执法记录仪上本地运行 LLM，但没有给出规格。

数据中心方面，AI200 机架内存 43TB，单卡演示 350B 模型、设计上限 1T。按本雷达的口径这些是容量数字，高通没有披露带宽，无法推算生成速度。资本层面，3 月 17 日高通 [上调季度股息并新增 200 亿美元回购授权](https://www.qualcomm.com/news/releases/2026/03/qualcomm-increases-quarterly-cash-dividend-and-announces-new--20)，与端侧 AI 无直接关系。

### 小结：本月的三个判断

第一，端侧 AI 正从手机向“个人设备群”扩散。Wear Elite 让手表第一次有了 12 TOPS 的 NPU，但约 12.8 GB/s 的带宽决定了它是“小模型常驻 + 手机协同”，不是独立运行大模型。第二，本月对端侧 LLM 体验提升最大的是软件，而不是芯片：同一颗 8 至尊版第五代，靠自推测解码把 3B 模型从约 33 tok/s 推到约 58 tok/s；Qwen3-4B 约 29–30 tok/s 已经是手机和 PC 的共同基线。第三，高通正在补开源和长尾生态的短板：XNNPACK 后端、Hexagon-MLIR、Docker 化的 NexaSDK 和 Arduino 开发板都在降低上 NPU 的门槛。不过这些开源路径目前仍以 CNN 和 1B 级模型为主，生产级 LLM 依旧依赖 QNN/Genie 闭源栈。

本月存疑点：Wear Elite 是否另有 eNPU 低功耗岛、CPU 的具体频率，只有媒体或检索摘要来源，官方未确认；Snapdragon Game AI SDK 和 NEURA、Wayve 两项合作都没有可核验的性能数字；本窗口没有核实到可信的 2nm 骁龙新爆料，也没有完成对高通 AI Research 新 arXiv 论文的检索（arXiv 检索被限流）。

## 2. Apple 与 Google：M5 Pro/Max、MacBook Neo 与 TurboQuant

### 总览：Apple 一周七款新品，Google 以软件推进为主

2026 年 2 月 27 日至 3 月 26 日这四周，Apple 与 Google 方向的硬件看点几乎都集中在 **Apple 3 月 2–4 日的连续发布**上。往周（2026-02-06、02-13、02-20、02-27 四周）的硬件雷达在本方向没有收录条目，本节内容全部来自本次回填，2 月的事件只作背景（见上月雷达）。

**Apple 三天发了五款带 AI 卖点的设备。** 3 月 2 日是 [iPhone 17e](https://www.apple.com/newsroom/2026/03/apple-introduces-iphone-17e/)（A19）和 [iPad Air](https://www.apple.com/newsroom/2026/03/apple-introduces-the-new-ipad-air-powered-by-m4/)（M4、12GB 内存）；3 月 3 日是 [M5 Pro / M5 Max](https://www.apple.com/newsroom/2026/03/apple-debuts-m5-pro-and-m5-max-to-supercharge-the-most-demanding-pro-workflows/) 及对应的 [MacBook Pro](https://www.apple.com/newsroom/2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/)、[MacBook Air M5](https://www.apple.com/newsroom/2026/03/apple-introduces-the-new-macbook-air-with-m5/)，以及不含 AI 芯片升级的 Studio Display 系列；3 月 4 日是 599 美元、用 A18 Pro 的 [MacBook Neo](https://www.apple.com/newsroom/2026/03/say-hello-to-macbook-neo/)。3 月 16 日另有搭载 H2 的 AirPods Max 2。这些新品的共同点是：**从 iPhone 入门机到 Max 级笔记本，全线都带有 GPU 内的 Neural Accelerator（矩阵单元）**，Apple 把它作为本代 AI 性能的主要来源。

**Google 一侧没有新芯片。** 3 月 3 日的 [Pixel Drop](https://blog.google/products-and-platforms/devices/pixel/march-2026-pixel-drop/) 把上月公布的 Gemini 多步任务带到 Pixel；3 月 17 日 [LiteRT 2.1.3](https://github.com/google-ai-edge/LiteRT/releases/tag/v2.1.3) 让联发科 NPU 支持覆盖所有适用 Android 版本；3 月 24 日 Google Research 发文介绍 [TurboQuant](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)，称可把 KV 缓存压到 3 bit 且几乎无损。Android 17 在 3 月 26 日进入 [Beta 3 平台稳定版](https://android-developers.googleblog.com/2026/03/the-third-beta-of-android-17.html)，但这一版没有新的 AI/NPU 接口。Gemma 4（含 E2B/E4B 端侧版本）直到 3 月 31 日才发布，在本窗口之外。

**爆料与报道集中在 Apple 的 AI 软件与云端。** Gurman 称 iOS 27 将用 [Core AI 取代 Core ML](https://9to5mac.com/2026/03/01/apple-replacing-core-ml-with-modernized-core-ai-framework-for-ios-27-at-wwdc/)，并为 Siri 加入 [第三方智能体扩展](https://9to5mac.com/2026/03/26/ios-27-apple-will-reportedly-let-claude-and-other-ai-chatbot-apps-integrate-with-siri/)；The Information 报道 [PCC 平均利用率只有约 10%](https://9to5mac.com/2026/03/02/some-apple-ai-servers-are-reportedly-sitting-unused-on-warehouse-shelves-due-to-low-apple-intelligence-usage/)，新 Siri 将跑在 Google 数据中心。Apple 官方在 3 月 23 日宣布 [WWDC26 于 6 月 8–12 日举行](https://www.apple.com/newsroom/2026/03/apples-worldwide-developers-conference-returns-the-week-of-june-8/)，并罕见地在新闻稿里预告「AI advancements」。

### Apple 芯片：Fusion Architecture 与 GPU 矩阵单元

**M5 Pro / M5 Max 是本月最重要的硬件。** 它们是 Apple 第一次让 Pro/Max 级芯片本身由两颗裸片组成：两颗第三代 3nm 裸片通过先进封装连成一颗 SoC，Apple 称之为 Fusion Architecture。官方口径的关键数字：

- CPU 18 核，其中 6 个 super core（原「性能核」改名）、12 个全新设计的性能核。Apple 的 Anand Shimpi 在接受 Mac & i 采访时说，新性能核是「完全定制的微架构」，与 super core 和能效核都不同（[9to5Mac 转述](https://9to5mac.com/2026/03/20/apple-explains-why-m5-chips-have-three-different-core-types-in-new-interview/)）。
- GPU 最高 20 核（Pro）/ 40 核（Max），每核一个 Neural Accelerator；GPU 峰值 AI 算力比上一代高 4 倍以上。
- 统一内存 M5 Pro 最高 64GB、307GB/s，M5 Max 最高 128GB、614GB/s。
- MacBook Pro 新闻稿称 LLM 提示词处理最高比 M4 Pro/Max 快 4 倍，并点名 LM Studio。

需要分清的是，**「4 倍」说的是算力密集的 prefill，不是 decode**。decode 主要受内存带宽限制：M5 Max 的 614GB/s 比 M4 Max 的 546GB/s（往期公开规格）只高约 12%。按「带宽 ÷ 每 token 读取字节」推算，M5 Max 跑 27B 稠密 4bit 模型（约 16GB 权重）decode 上限约 38 tok/s，70B 稠密 4bit 约 15–17 tok/s。MoE 模型每 token 只读激活参数，带宽上限高得多，128GB 内存才是装不装得下的门槛。第三方方面，[Tom's Hardware](https://www.tomshardware.com/laptops/macbooks/apple-macbook-pro-14-inch-m5-max-2026-review) 实测 Geekbench 6 单核 4338、多核 29430，混合续航 17 小时 58 分钟，用 LM Studio 跑 Gemma 3 27B 称「出 token 极快」，但没有给出 tok/s。

**MacBook Air M5** 把 2025 年 10 月首发的 M5 装进轻薄本：带宽 153GB/s（比 M4 高 28%），官方称 AI 任务比 M4 版快最高 4 倍，并第一次在 Air 的新闻稿里写「企业在本机跑 LLM」。推算 8B 稠密 4bit 模型 decode 上限约 34 tok/s。

**MacBook Neo** 是另一个方向：A18 Pro（6 核 CPU、5 核 GPU、16 核 Neural Engine）、固定 8GB 内存、60GB/s 带宽，599 美元起。官方称端侧 AI 负载（Photoshop 滤镜）比畅销的 Core Ultra 5 笔记本快最高 3 倍。8GB 内存意味着它只适合 3B 级本地模型和 Apple Intelligence 自带功能。TrendForce 预计 Neo 2026 年出货 400–500 万台（[9to5Mac 转述](https://9to5mac.com/2026/03/05/apple-could-sell-4-5m-macbook-neo-machines-this-year-says-trendforce/)），在全球笔记本出货预计下降 9.2% 的背景下逆势推入门款。

至此 Mac 的芯片阶梯是 A18 Pro（60GB/s）→ M5（153GB/s）→ M5 Pro（307GB/s）→ M5 Max（614GB/s），带宽相差约 10 倍。对端侧模型开发者来说，Apple 平台的「最低公分母」仍是 8GB 设备，而上限已到 128GB。

### Apple 移动端：A19 下放，内存与存储抬底线

**iPhone 17e** 用上与 iPhone 17 相同的 A19：6 核 CPU、4 核 GPU（带 Neural Accelerators）、16 核 Neural Engine。官方特意写 Neural Engine「为大型生成式模型优化」。内存容量 Apple 照例不公布。9to5Mac 汇总的 Geekbench 早期结果显示 Metal 约 31163，比 iPhone 16e 的 23895 高约 30%。起步存储 256GB，基带换成 C1X（官方称能耗比 iPhone 16 Pro 的基带低 30%）。

**iPad Air M4** 的关键变化是内存从 8GB 提到 12GB、带宽 120GB/s，官方直接把它与「更快地跑 AI 模型」挂钩。推算 8B 4bit 模型 decode 上限约 26 tok/s。

**存储底线同步上移。** 3 月 23 日 [TrendForce](https://www.trendforce.com/presscenter/news/20260323-12983.html) 预计 2026 年手机平均存储容量增长 4.8%，理由之一是 Apple、华为的端侧 AI 模型需要 40–60GB 系统存储作缓存（第三方口径，Apple 从未公布）。Apple 本月的新品正好印证这一点：iPhone 17e 256GB 起、MacBook Air 512GB 起、MacBook Pro 1TB 起，起价同时上调（[9to5Mac](https://9to5mac.com/2026/03/03/apple-macbook-price-increase-ram-same/)），但内存升级加价与上一代相同。

**爆料**：韩国 The Bell 称 iPhone Fold 将配 12GB LPDDR5X（三星供货），与 iPhone 17 Pro 相同（[9to5Mac 转述](https://9to5mac.com/2026/03/12/new-iphone-fold-details-include-rumored-ram-storage-and-pricing/)，低可信）。如果属实，Apple 高端机的内存仍停在 12GB，端侧模型规模的上限短期不会明显上移。Gurman 还称搭载 A18 的新款入门 iPad 仍按上半年发布推进，届时最便宜的 iPad 也将支持 Apple Intelligence。

### Apple 软件栈与云端：框架换代、Siri 开放、PCC 尴尬

**MLX 跟进很快。** M5 Pro/Max 3 月 11 日发售，[MLX 0.31.1](https://github.com/ml-explore/mlx/releases/tag/v0.31.1) 3 月 12 日就合入「initial tuning for M5 pro and max」。2 月 28 日的 0.31.0 改进了多机互联（JACCL）带宽，3 月 7 日 mlx-lm 0.31.0 为 Qwen 3.5 加入张量并行，方向都是把多台 Mac 拼起来跑单机装不下的模型。值得注意的是，这两个版本的大部分改动在 CUDA 后端，MLX 正在变成跨 Apple 与 NVIDIA 的框架。

**Core AI 爆料。** Gurman 称 Apple 将在 WWDC 用 Core AI 取代 Core ML，用途仍是帮助开发者集成外部模型（爆料，中等可信）。Core ML 是第三方模型调用 Neural Engine 的主要官方途径，而 M5 系列把 AI 算力重心放到了 GPU 矩阵单元，框架层如果重构，可能会统一 ANE 与 GPU 的调度（推断，待 WWDC 验证）。

**Siri 走向「智能体入口」。** Gurman 3 月 24 日称 Apple 在测试独立的 Siri App，3 月 26 日又称 iOS 27 将加入 Extensions，让已安装 App 中的智能体（如 Claude）与 Siri 协作，测试版里的原文是「Extensions allow agents from installed apps to work with Siri」。Gemini 驱动的新 Siri 没有赶上 3 月 24 日发布的 iOS 26.4，各方报道都指向 iOS 26.5。和上月 Google 公布的 AppFunctions 对照，两家都在把「系统助手 + App 智能体」做成平台接口，只是方向相反：Google 让 App 向智能体暴露本地函数，Apple 让 App 里的智能体接入 Siri。

**PCC 的尴尬。** The Information 报道 Private Cloud Compute 平均只用了约 10% 容量，部分服务器闲置；PCC 芯片据信是改造的 M2 Ultra，跑不动 Gemini 级模型，因此新 Siri 将由 Google 在其数据中心运行（媒体报道，中等可信）。这与上月 Apple 官方宣布休斯敦 AI 服务器提前出货形成反差。如果属实，Apple 平台的智能体将长期是**端侧模型负责本地理解和执行、合作方云端模型负责重推理**的混合形态，端侧芯片的角色是隐私敏感任务与低延迟交互，而不是独立承担前沿模型。

**产业链**：3 月 26 日 Apple 宣布[美国制造计划新增 Bosch、Cirrus Logic、TDK、Qnity](https://www.apple.com/newsroom/2026/03/apple-adds-new-partners-to-its-american-manufacturing-program/)，到 2030 年投入 4 亿美元；台积电华盛顿 Camas 工厂将为 Bosch 传感硬件生产 IC，GlobalFoundries 纽约 Malta 工厂为 Cirrus Logic 引入新工艺。涉及的是传感器与混合信号芯片，不是 SoC。

### Google：手机智能体落地、NPU 碎片化与 KV 压缩

**Pixel Drop 把多步任务推到自家机型。** 3 月 3 日的 Pixel Drop 中，Gemini 可以在后台操作 App 完成订菜、叫车（beta，部分 App），Pixel 10 系列另有查看/终止任务的界面；诈骗检测扩展到六个国家（Pixel 9 及以上）。页面没有提到 Gemini Nano、Tensor 或端侧处理，功能按 Pixel 9 / Pixel 10 分档，但未说明原因。结合上月公告，这类手机智能体目前是「云端规划 + 设备上执行操作」的混合形态。

**LiteRT 解决 NPU 碎片化。** LiteRT 2.1.3 允许把联发科 NPU 库打包进 App，使联发科 NPU 支持从仅 Android 15 扩展到所有适用版本；同时加入 Broadcom VideoCore GPU（树莓派一类设备）基础支持。LiteRT-LM 0.9.0 在窗口内走完 alpha03（3 月 6 日）、beta（3 月 13 日）和 rc（3 月 25 日），正式版 3 月 27 日发布，与 3 月 31 日的 Gemma 4 衔接。

**TurboQuant 对端侧的价值被低估。** 这项工作（ICLR 2026，论文 2025 年 4 月已上 arXiv）先随机旋转、再用极坐标量化（PolarQuant），最后用 1 bit 的 QJL 消除残差偏差，几乎不需要额外的量化常数。官方称 KV 缓存可压到 3 bit、无需训练且精度无损，长上下文测试中 KV 内存至少缩小 6 倍；8 倍加速是 H100 上的数据，没有端侧实测。推算：8B 级模型在 fp16 下每 token KV 约 128KB，32K 上下文约 4GB，压缩后可降到 0.7GB 以内，对 8–12GB 内存的手机和笔记本是决定性的差别。

**Android XR 眼镜仍在预热。** Google 在 MWC 提供了单目 AI 眼镜原型试用（[9to5Google](https://9to5google.com/2026/03/02/android-mwc-2026/)）；三星确认眼镜有眼睛高度的摄像头、需连接手机、2026 年上市；SamMobile 爆料 Galaxy Glasses 电池 245mAh，接近带屏的 Meta Ray-Ban Display（低可信）。电池规模决定了眼镜端只能做采集、显示和轻量推理，重计算在手机或云端。窗口内没有看到 Tensor G6 或 Pixel 11 芯片的可信新爆料。

### 口径与存疑

- **官方倍数都是「最高」口径。** M5 Pro/Max 的「prefill 快 4 倍」、MacBook Air 的「AI 任务快 4 倍」、MacBook Neo 的「端侧 AI 快 3 倍」都来自 Apple 1–2 月用预生产机做的内部测试，对比对象和负载由 Apple 选定。Neo 的对比对象是 8GB 内存的 Core Ultra 5 笔记本，负载是 Photoshop 滤镜，不是大模型。
- **Neural Engine 仍不公布 TOPS。** 本月所有新品都只写「16 核」「更快」，无法与高通、联发科、Intel 的 NPU 直接比较；Apple 宣传重点转向 GPU 矩阵单元，可能也与此有关。
- **iPhone 内存不公开。** iPhone 17e 的内存容量和带宽都没有官方数字，能跑多大的本地模型无法推算；iPhone Fold 12GB 只是爆料。
- **本节所有 tok/s 都是推算。** 推算用「带宽 ÷ 每 token 读取的权重字节」，忽略 KV 缓存读取、计算开销和带宽利用率，实际值会明显低于上限。窗口内没有找到带具体 tok/s 的第三方 M5 Pro/Max 实测。
- **PCC 与 Siri 相关内容全部是媒体报道或爆料**，Apple 未确认；The Information 原文付费，本节以 9to5Mac 转述为准。
- **TurboQuant 的论文早在 2025 年 4 月上了 arXiv**，本月收录依据是 Google Research 官方博客的发布日；8 倍加速来自 H100，不能直接套到手机上。
- **Google 方向本月没有硬件发布。** Pixel 10a（2 月 18 日）已在上月收录；Tensor G6 在窗口内没有新的可信爆料；Gemma 4 与 Gemini Nano 新版都在 3 月 31 日之后，留给下月。

### 小结：硬件底座已就位，等 6 月的软件

本月 Apple 完成了一轮几乎覆盖全线的硬件更新，三个信号最明确：

1. **AI 算力重心转向 GPU 矩阵单元。** 从 iPhone 17e 到 M5 Max 都带 Neural Accelerator，官方宣传的 AI 提升（prefill 4 倍、AI 任务 4 倍）都来自这里；Neural Engine 的 TOPS 依旧不公布。
2. **内存决定能跑多大的模型，而 Apple 的内存分层很陡。** 8GB（Neo）、12GB（iPad Air、传闻中的 iPhone Fold）、最高 128GB（M5 Max），带宽从 60GB/s 到 614GB/s。端侧智能体要按最低档设计，按最高档宣传。
3. **软件和云端是短板。** 新 Siri 未随 iOS 26.4 发布，PCC 利用率低且算力不足，Core AI、Siri 扩展、独立 Siri App 都要等 6 月 WWDC。

Google 一侧没有硬件，但 LiteRT 下放 NPU 支持、TurboQuant 压缩 KV 缓存、Pixel 上线手机智能体，都是在为 3 月 31 日的 Gemma 4 与 5 月 I/O 铺路。**下月要看**：Gemma 4 端侧版本在 Pixel 和 LiteRT-LM 上的实测数字，A18 入门 iPad 是否发布，以及 iOS 26.5 能否兑现 Gemini 版 Siri。

## 3. 其他 SoC 与 PC：NemoClaw 本地常驻 Agent、Arm 自研芯片与 Arc Pro B70

### 本月要点：新芯片少，"Agent 电脑"和内存账单成了主线

2 月 27 日到 3 月 26 日这四周，高通、苹果、谷歌以外的 SoC 与 PC 阵营没有发布新的旗舰手机 SoC。联发科在 MWC 上主推的仍是去年的天玑 9500，AMD 和英特尔做的是现有平台的扩展和补位。这个月真正有分量的变化在三处。第一，英伟达在 GTC 2026 把 RTX PC 和 DGX Spark 定位为跑常驻 Agent 的“Agent 电脑”，同时发布 NemoClaw 软件栈和一批百亿参数级的 MoE 开放模型。第二，Arm 和英伟达同月推出面向 Agent 的数据中心 CPU，“Agent 需要更多 CPU”成了行业共识。第三，TrendForce 连续发布报告，显示内存涨价已经从手机传导到笔记本、代工和存储配置，2026 年端侧设备的内存预算很难增加。

说明：窗口内各周（2026-02-06、02-13、02-20、02-27）的周度硬件雷达在本方向没有已收条目。2 月的背景（DRAM 合约价单季预测上调到 90–95%、全年手机产量预测 -10%、三星 2nm Exynos 2600 随 Galaxy S26 商用）见上月小节，本节只写 2 月 27 日以后的新变化。

### 移动 SoC：联发科把 AI 眼镜的算力放回手机

联发科的 MWC 新闻稿（[3 月 1 日](https://www.mediatek.com/press-room/mediatek-exemplifies-ai-and-connectivity-leadership-at-mwc-2026)）里没有新天玑，主角是用天玑 9500 NPU 驱动的 AI 眼镜：手机端运行支持文本、图像、语音、视频的全模态（Omni）大模型，眼镜只负责采集和显示。官方展台说明直接写着“Smartphone handles all compute enabling ultra-light weight glasses”。这条路线和“眼镜自带 NPU”不同：成本和功耗留在手机 SoC 上，眼镜可以做得更轻，代价是必须始终连着手机。OPPO 在 3 月 4 日联发科主题演讲上[同步宣布](https://www.oppo.com/en/newsroom/press/oppo-and-mediatek-mwc2026/)，Omni 是“业界首个端侧全模态模型”的技术预览；基于天玑 9500 的端侧翻译平均准确率比常规方案高 15%，将随 ColorOS 16 推送到 Find X9 系列。两家都没有公布 Omni 的参数量、精度和 tok/s，模型规模目前只能记为未披露。

同一份新闻稿里还有三件与端侧相关的硬件：3nm 车规级天玑 Auto 智能座舱平台（Arm v9.2 CPU、支持光追的 GPU、面向本地生成式语音助手的 NPU），带调制解调器级 AI 的 5G-Advanced 车载通信芯片，以及在台积电 2nm/3nm 上完成硅验证的 UCIe-Advanced die-to-die IP（最高 10 Tbps/mm）。联发科还提出“personal device cloud”，设想 AI Agent 通过 Wi-Fi 或 6G 在家庭和个人设备之间协同。它与 AI 眼镜方案的思路相同：把多个设备当作一台分布式的端侧 Agent 计算机。

小米方面，卢伟冰在 MWC 接受 CNBC 采访时表示，玄戒芯片“很可能”每年更新一代，并会用于海外市场机型（[9to5Google 转述](https://9to5google.com/2026/03/04/xiaomi-xring-chip-yearly-update/)）。和 2 月“年内芯片、OS、大模型合一”的表态相比，这次新增的是迭代节奏和出海计划，但下一代芯片的命名、工艺、NPU 规格都还没有官方信息。三星 Exynos、华为麒麟、紫光展锐、瑞芯微在窗口内都没有查到新芯片的一手发布。

### PC：台式机拿到 Copilot+ NPU，32GB 显存进入千元美元档

AMD 在 [3 月 2 日](https://www.amd.com/en/newsroom/press-releases/2026-3-2-amd-gives-consumers-and-businesses-more-ai-pc-opti.html)发布锐龙 AI 400 / AI PRO 400 台式机处理器（AM5），官方称是首个支持 Copilot+ 体验的台式机家族。12 个型号最高 8 核 16 线程、5.1 GHz，NPU 一律最高 50 TOPS，TDP 为 65W（G）和 35W（GE），2026 年第二季度由惠普、联想等出货。值得注意的是，台式机 NPU 标的是 50 TOPS，低于同系列移动版的 60 TOPS，官方没有解释原因。新闻稿也没有给出内存规格。按双通道 DDR5 估算（带宽为假设值，约 90 GB/s 量级），8B 模型 INT4 的 decode 上限约 20 tok/s（推算）。也就是说，台式机 NPU 解决的是常驻和 prefill 的能效，decode 速度仍然受内存带宽限制。

英特尔 3 月 25 日在 Pro 发布活动上推出 Arc Pro B70（[Phoronix](https://www.phoronix.com/news/Intel-Arc-Pro-B70-Announced)，[igor'sLAB 规格整理](https://www.igorslab.de/en/intel-launches-the-arc-pro-b70-with-32-gb-of-vram-for-949-big-battlemage-is-coming-first-for-ai-and-workstations/)），参数为 32 Xe 核、32GB GDDR6、608 GB/s、367 INT8 TOPS、230W，建议价 949 美元，当日开售；同场还发布了 Core Ultra Series 3 vPro 和 Xeon 600 工作站处理器。英特尔的宣传重点是“上下文窗口最多大 2.2 倍、多 Agent 响应最多快 6.2 倍”（厂商口径），卖的是容量和并发，而不是游戏性能。推算：27B 稠密模型 Q4 每 token 约读 15GB，单卡 decode 上限约 40 tok/s；120B 级 MoE 的 4bit 权重约 60GB，单卡放不下。另外，英特尔 3 月 9 日在 Embedded World 发布的 Core Series 2（P 核工业版）主打确定性实时控制，[官方稿](https://www.intel.com/content/www/us/en/newsroom/news/client-computing/intel-launches-core-series-2-processors-expands-edge-ai-portfolio.html)没有给 NPU/TOPS，只附带一套医疗边缘 AI 套件预览，与端侧大模型关系不大，所以没有单列条目。

### 英伟达 GTC：把 PC 变成“Agent 电脑”

本月 PC 端侧最重要的事件来自英伟达。[3 月 16 日发布的 NemoClaw](https://nvidianews.nvidia.com/news/nvidia-announces-nemoclaw) 是给 OpenClaw Agent 平台用的一键栈：安装 Nemotron 开放模型和新开源的 OpenShell 运行时。OpenShell 提供隔离沙箱，以及按策略控制数据、工具、网络访问的护栏，敏感请求留在本地，需要时再通过“隐私路由”调用云端前沿模型。官方列出的运行平台是 GeForce RTX PC/笔记本、RTX PRO 工作站、DGX Station 和 DGX Spark，理由是“常驻 Agent 需要专用本地算力”。端侧 Agent 原本最缺的是“敢在个人设备上长期运行”的安全底座，这次由 GPU 厂商直接补上了。

模型侧，[GTC RTX AI Garage 博客](https://blogs.nvidia.com/blog/rtx-ai-garage-gtc-2026-nemoclaw)列出可在 RTX PC 与 DGX Spark 上本地运行的模型：Nemotron 3 Super（120B 总参/12B 激活，PinchBench 85.6%）、Mistral Small 4（119B/6B 激活）、Qwen 3.5（27B/9B/4B，262K 上下文）、Nemotron 3 Nano 4B。本月本地化的两款百亿级模型都是 MoE，这一点很关键。DGX Spark 的[官方带宽是 273 GB/s](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)：Nemotron 3 Super 用 NVFP4 每 token 约读 6GB 激活权重，decode 上限约 45 tok/s；如果换成同样规模的稠密模型，上限只有约 4.5 tok/s（均为推算）。所以官方说的“128GB 可跑 120B+”只说明权重装得下，实际能不能用，要看激活参数。[MONOist](https://monoist.itmedia.co.jp/mn/articles/2603/19/news046.html) 报道同期软件更新支持最多 4 台 DGX Spark 互联（2 台直连、3 台环形、4 台经交换机 RoCE）；本次未打开英伟达 3 月的一手互联说明（详细的 2 台 256GB / 4 台 512GB 配置见其 6 月开发者博客），因此这一项按媒体口径记录。

### 数据中心：Agent 让 CPU 回到中心

GTC 同日，英伟达宣布 [Vera Rubin 平台七款芯片全面量产](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform)，并首次纳入 Groq 3 LPU。LPX 机架有 256 颗 LPU、128GB 片上 SRAM、640 TB/s 纵向带宽，与 NVL72 协同做 decode，官方称每兆瓦推理吞吐最高提升 35 倍。[Vera CPU](https://nvidianews.nvidia.com/news/nvidia-launches-vera-cpu-purpose-built-for-agentic-ai) 有 88 个自研 Olympus 核，第二代低功耗内存子系统改用 LPDDR5X，带宽 1.2 TB/s。一周后，Arm 推出[公司 35 年来第一款自己销售的芯片 Arm AGI CPU](https://newsroom.arm.com/news/arm-agi-cpu-launch)：最多 136 个 Neoverse V3 核、300W、12 通道 DDR5-8800（800GB/s 以上），Meta 是首要合作方兼共同开发方，官方称每机架性能是 x86 的 2 倍以上。两家的说法一致：Agent 的工具调用、沙箱、环境模拟和编排都是 CPU 负载，Arm 估计每 GW 数据中心所需 CPU 容量会增加到 4 倍以上。

对端侧有两点参考。其一，“SRAM/高带宽专用硬件负责 decode”的异构拆分已经进入商用平台，与端侧 SoC 中 NPU 负责 prefill、decode 受限于 LPDDR 带宽是同一个问题。其二，Arm 开始自己卖芯片，会改变它与联发科、三星、小米等手机 SoC 客户的关系；“Agent 需要更多 CPU”的判断，也同样适用于手机和 PC 上 CPU 与 NPU 的面积配比。

### 代工与内存：成本从 DRAM 扩散到整机

TrendForce 本月的几份报告可以连起来看。[3 月 10 日](https://www.trendforce.com/presscenter/news/20260310-12959.html)：以 900 美元主流笔记本建模，DRAM+SSD 占 BOM 从约 15% 升到 1Q26 的 30% 以上；英特尔入门 CPU 已涨价 15% 以上，2Q26 还要上调主流平台价格；内存与 CPU 合计占 BOM 从 45% 升到 58%，零售价可能要涨近 40%。[3 月 12 日](https://www.trendforce.com/presscenter/news/20260312-12965.html)：4Q25 前十大代工营收 463 亿美元，台积电以 3nm 手机 AP 拉高 ASP，份额 70.4%；三星代工靠 2nm 新品和 HBM4 逻辑 die 季增 6.7%，份额升到 7.1%。[3 月 19 日](https://www.trendforce.com/presscenter/news/20260319-12979.html)：2026 年代工营收预计增长 24.8% 至约 2188 亿美元，台积电 5/4nm 及以下全年满载并全面涨价，三星 5/4nm 也已涨价。[3 月 23 日](https://www.trendforce.com/presscenter/news/20260323-12983.html)：2026 年手机平均存储容量预计增长 4.8%，TrendForce 称端侧 AI 需要 40–60GB 系统存储作缓存，iPhone 17 起步 256GB，华为 Mate 80 推 512GB，主流安卓机 128GB 档可能在年底消失。另一份 [3 月 9 日报告](https://www.trendforce.com/presscenter/news/20260309-12956.html)重申 2026 年手机产量至少 -10%（约 11.35 亿部），属于 2 月预测的延续，不再单列。

上游原因在 GTC 上能看得很清楚：三星[展出 HBM4E（16Gbps、4.0 TB/s）并宣布已量产 SOCAMM2](https://news.samsung.com/global/samsung-unveils-hbm4e-showcasing-comprehensive-ai-solutions-nvidia-partnership-and-vision-at-nvidia-gtc-2026)，3 月 18 日又与 AMD [签署 MOU](https://news.samsung.com/global/samsung-and-amd-expand-strategic-collaboration-on-next-generation-ai-memory-solutions)，作为 MI455X 的 HBM4 主要供应商。英伟达 Vera 和三星 SOCAMM2 都把 LPDDR 带进服务器，于是手机 LPDDR5X 不仅要和 HBM 争晶圆，还要和服务器 LPDDR 争产能。

### 小结与判断

1. **端侧 Agent 的主战场本月在 PC，不在手机。** NemoClaw + OpenShell + 百亿级 MoE 开放模型 + 128GB 统一内存设备，让“本地常驻、带安全沙箱的 Agent”第一次成为可以买到的完整方案；手机侧本月只有联发科和 OPPO 的全模态模型预览，参数规模未公开。
2. **“能装下”和“能跑快”要分开看。** 本月厂商宣传的“120B+”“2.2 倍上下文”都是容量口径。按带宽推算，DGX Spark 能流畅跑的是激活 6–12B 的 MoE，32GB 的 Arc Pro B70 适合 27–32B 稠密模型，台式机锐龙 AI 400 在双通道 DDR5 下适合 8B 以下。
3. **内存与代工双涨，会压住 2026 年端侧硬件的升级幅度。** 笔记本 32GB 普及会推迟，中低端安卓机的内存配置难以提升；能把更大模型带到端侧的，主要是能消化成本的高端品牌和 MoE 这类“少读权重”的模型结构。
4. **待观察：** 联发科下一代旗舰与小米下一代玄戒的 NPU 规格；Arm 自己做芯片后与手机 SoC 客户关系的变化；DGX Spark 多机互联的官方口径和实测吞吐。

## 4. 低功耗、存内计算与内存：1 美元 NPU MCU、LPDDR6 验证与存算空窗

### 总览：NPU 下沉到 1 美元 MCU，内存成了最贵的端侧资源

本月窗口（02-27~03-26）同时赶上 MWC（3 月 2~5 日，巴塞罗那）、Embedded World（3 月 10~12 日，纽伦堡）和英伟达 GTC（3 月 16~19 日）。低功耗、存内计算与内存这个方向的新闻量明显多于 2 月。窗口内各周（02-27、03-06、03-13、03-20）的硬件雷达此前都没有这一方向的已收条目，本节以本月新收的 14 条为主；窗口外的材料只作背景，并单独标注。

本月可以归纳为四条主线：

1. **NPU 成为 MCU 和连接芯片的默认配置**：TI 把自研 TinyEngine NPU 放进千片单价不到 1 美元的 Cortex-M0+；ST 给超低功耗 STM32U3 加了 HSP 加速器；NXP、Nordic、Synaptics 把 NPU 和无线做进同一颗芯片或同一个封装。
2. **常开可穿戴继续往“更低电压、更专用的芯片”走**：Ambiq 把亚阈值平台搬到 12nm、最低 300mV；Alif 与 Brilliant Labs 合作为 AI 眼镜定制芯片；BrainChip 推出神经形态常开参考设计。
3. **边缘加速器拼的是渠道和形态**：DEEPX 借瑞萨、树莓派进欧洲；爱芯元智用 24 TOPS 级 SoC 做本地 OpenClaw 盒子。
4. **内存从“技术升级”变成“供给约束”**：SK 海力士 1c LPDDR6 完成开发验证；同月美光移动业务毛利率升到 79%，SK 集团会长称短缺可能持续到 2030 年；TrendForce 估计端侧 AI 要占 40~60GB 存储。

存内计算/PIM 本月没有找到窗口内的产品级发布，下文单独说明。

### 一、MCU 与连接芯片：NPU 不再是高端选项

**TI 把 NPU 推到最低端。** [TI 3 月 10 日发布](https://www.ti.com/about-ti/newsroom/news-releases/2026/2026-03-10-ti-expands-microcontroller-portfolio-and-software-ecosystem-to-enable-edge-ai-in-every-device.html)两个 MCU 系列，都集成自研 TinyEngine NPU。入门款 [MSPM0G5187](https://www.ti.com/product/MSPM0G5187) 是 80MHz 的 Cortex-M0+，只有 128KB 闪存和 32KB SRAM，NPU 在 80MHz 下为 2.56 GOPS，支持 2/4/8-bit 权重，千片单价低于 1 美元。官方称相比没有加速器的同类 MCU，单次推理延迟最多降 90 倍、能耗降 120 倍以上（厂商对比口径，没有绝对能耗数）。高端的 AM13Ex 是 250MHz 的 Cortex-M33，可在控制 4 台电机的同时跑自适应控制模型。结合上月 TI 宣布以 75 亿美元收购 Silicon Labs（窗口外背景），TI 的方向很清楚：NPU 要覆盖它的整个 MCU 产品线。

**ST 走的是另一条路：不加 NPU，加 DSP。** [ST 3 月 3 日的博客](https://blog.st.com/hardware-signal-processing-hsp/)介绍了 STM32U3B5/U3C5 上的新硬件单元 HSP。它本来为 FFT、FIR 设计，后来发现对神经网络也有效。按 ST 内部测试，256 点 FFT 比 Cortex-M33 快 13 倍，约为竞品 Cortex-M55（带 Helium）的 3 倍；KWS、图像分类、视觉唤醒模型比 M33 加 TFLite Micro 快 6~9 倍，部分 AI 应用能效翻倍。STM32U3 是 ST 最省电的近阈值系列，加上 HSP 后，电池设备不必外挂 DSP 就能做连续振动、音频分析。和上月车规 Stellar P3E 一样，ST 的思路是按场景选加速器，而不是所有芯片都放同一个 NPU。

**NPU 和无线开始合并。** [NXP i.MX 93W](https://finviz.com/news/333269/nxps-new-imx-93w-fuses-edge-compute-and-secure-wireless-connectivity-to-accelerate-physical-ai)（3 月 9 日）把双核 A55 加 1.8 eTOPS Ethos NPU 的 i.MX 93，与 Wi-Fi 6/BLE/802.15.4 三模无线芯片 IW610 做成一个 SiP，官方称可替代最多 60 颗分立器件。NPU 算力没有升级，卖点是省掉射频设计和认证。[Nordic nRF92](https://www.nordicsemi.com/Nordic-news/2026/03/Nordic-accelerates-cellular-IoT-leadership-with-major-new-product-releases-at-MWC-2026)（3 月 2 日）把 Axon NPU 放进 LTE-M/NB-IoT 加卫星 NTN 芯片，但没有公布任何算力和功耗数字，2027 年初才全面供货。[Synaptics SYN765x](https://www.edge-ai-vision.com/2026/03/synaptics-introduces-syn765x-an-industry-leading-ai-native-wi-fi-7-solution-for-integrated-iot-edge-applications/)（3 月 10 日）是带 NPU 和 DSP 的 Wi-Fi 7 单芯片，用 Wi-Fi 信道状态信息在本地做存在检测和动作跟踪；同日 Synaptics 与 Google 推出基于 Astra SL2610 的 Coral 开发板（1 TOPS Torq NPU 加 Google Coral NPU）。

这几条放在一起看：家居、工业、表计这类设备的端侧 AI，越来越多地会运行在“无线芯片里的 NPU”上，而不是单独的 AI 芯片上。对这类设备来说，在本地判断后少发一次包，省下的电往往比 NPU 本身的功耗还多。

### 二、常开可穿戴：更低电压、更定制

**Ambiq 把亚阈值做到 12nm。** [Ambiq 3 月 5 日公布](https://ambiq.com/news/ambiq-reveals-12nm-spot-platform-enabling-operation-down-to-300mv-for-atomiq/)Atomiq 的技术细节：SPOT 亚阈值平台首次用在 FinFET（台积电 N12e），超低功耗模式最低约 300mV，是公司历史上最低电压；集成 Arm Ethos-U85 NPU，官方称在 100MHz 的低压模式下仍有“每秒数百亿次运算”（没有给出精确 TOPS）。为此 Ambiq 重做了电源管理：用单电感多输出降压转换器，提供 6 路独立电压轨，负载从纳安到毫安。12nm 平台已经硅验证，但 Atomiq 要到 2027 年才量产。同日财报显示 Ambiq 2025 年营收 7,250 万美元，累计出货超过 2.9 亿台设备；3 月 11 日，其 AOT 编译器 heliaAOT 获 Embedded World 工具类奖，官方称内存占用比基于运行时的部署少 10 倍。

**AI 眼镜：MCU 路线开始定制硅。** [Alif 与 Brilliant Labs 3 月 11 日宣布](https://alifsemi.com/press-release/next-generation-ai-powered-smart-glasses/)共同定义下一代 AI 眼镜芯片。现款 Halo 眼镜几乎所有功能都由一颗 Balletto B1 MCU 承担（Cortex-M55 加 Ethos-U55，NPU 最高 46 GOPS，3.9mm×3.9mm 封装，见 [Alif 2025 年博客](https://alifsemi.com/powering-the-future-of-smart-glasses-how-alifs-balletto-b1-enables-halo-by-brilliant-labs/)，窗口外背景），端侧做实时翻译和 AI 记忆，续航最长 14 小时。与之对照，本月 MWC 上联发科、高通都在推手机级芯片做眼镜（由其他方向收录）。AI 眼镜正在分成两条路线：手机级 SoC 追求能力，MCU 级方案追求全天续航，把大模型交给手机和云端。

**神经形态常开方案。** [BrainChip AkidaTag](https://brainchip.com/newsfeed/brainchip-enables-the-next-generation-of-always-on-wearables-with-the-akidatag-reference-platform/)（3 月 10 日）用 AKD1500 神经形态协处理器做常开推理，Nordic nRF5340 负责蓝牙和应用，支持生命体征监测、异常检测、语音唤醒，并能在设备上做增量学习。5 月开放评估、三季度量产。和上月索喜与 Innatera 的雷达加神经形态方案一样，常开 AI 正在形成“亚毫瓦感知常开、主处理器按需唤醒”的两级结构。不过这一路线目前只有厂商口径，没有第三方功耗实测。

### 三、边缘加速器：从比 TOPS 到比生态

[DEEPX 在 Embedded World](https://deepx.ai/deepx-targets-the-european-market-at-embedded-world-2026-building-a-comprehensive-alliance-with-10-global-partners/) 发布量产的 DX-M1M M.2 模组（[产品页](https://deepx.ai/products/dx-m1/)：25 TOPS INT8，4GB LPDDR5，典型 5W，约 5 TOPS/W，按官方数字推算）。更重要的是渠道：瑞萨展出 3 款以上“瑞萨应用处理器加 DEEPX NPU”的工业板，树莓派生态首发 DX-M1 AI HAT，安富利 Silica 称在欧洲已找到 30 多家客户。DEEPX 1 月 CES 上把下一代 2nm DX-M2 定位为 5W 内跑 20B~100B 参数 MoE 模型（窗口外背景，未经验证，不收为本月条目）。

国内方面，[爱芯元智 3 月 16 日](https://www.axera-tech.com/zh-hans/news/3093.html)与无问芯穹宣布 AXClaw Box（帝王虾盒）：基于 OpenClaw 平台，本地用 VLM 和 ASR 处理音视频并脱敏，大模型对话按需调用云端 Kimi K2.5、MiniMax M2.5、GLM-5。同月 AX8850（八核 A55、24 TOPS NPU）先后出现在 [MWC 广和通家庭 CPE](https://www.axera-tech.com/zh-hans/news/3094.html) 和 [Embedded World 的 M5Stack AI Pyramid](https://www.axera-tech.com/zh-hans/news/3092.html)（8GB LPDDR4x）。这是本月最接近“端侧 Agent 硬件”的形态：本地模型负责感知和隐私，云端模型负责推理。8GB 内存最多装下约 7B INT4 权重（推算），所以它不是本地大模型盒子，而是端云协同的入口设备。

本月在 Hailo、Axelera 的官方新闻源里没有找到窗口内的新发布（Axelera 融资已在上月收录）。

### 四、内存：带宽在升，价格和供给决定上限

**带宽。** [SK 海力士 3 月 10 日](https://news.skhynix.com/1c-lpddr6-development-2026/)宣布 1c 工艺 16Gb LPDDR6 完成全球首个开发验证：基础速率 10.7Gbps 以上，比 LPDDR5X 快 33%，靠子通道结构和 DVFS 省电 20% 以上；上半年完成量产准备、下半年供货。官方只承诺 10.7Gbps，上月 ISSCC 论文展示的 14.4Gbps 还没有落到产品档位。按“带宽 ÷ 每 token 读取字节数”估算：如果手机用 96-bit LPDDR6 跑 10.7Gbps，峰值约 128GB/s，3B 参数 INT4 模型（约 1.5GB）的 decode 理论上限约 85 tok/s，比 64-bit LPDDR5X-9600（76.8GB/s）高约 1.7 倍（推算，实际位宽取决于 SoC）。SK 海力士在 [MWC 展台](https://news.skhynix.com/en/mwc-2026/)同时展出了 UFS 4.1（1TB）、uMCP 4.1 和 ZUFS 4.1。存储接口方面，JEDEC 在 2 月 26 日发布 UFS 5.0 标准（顺序读写约 10.8GB/s，窗口外一天，作背景）。

**价格与供给。** [美光 3 月 18 日财报](https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-results-second-quarter-fiscal-2026)：单季营收 238.6 亿美元，移动与客户端业务营收 77.1 亿美元、毛利率 79%（一年前为 15%），首次高于数据中心业务；下季度指引毛利率约 81%。[SK 集团会长崔泰源 3 月 16 日在 GTC 表示](https://www.electronicsweekly.com/news/business/memory-shortage-to-last-4-5-years-says-sk-boss-2026-03/)，HBM 消耗大量晶圆，晶圆供给落后需求 20% 以上，短缺可能持续到 2030 年（媒体转述，[SK 海力士官方稿](https://news.skhynix.com/en/gtc-2026-ai-partnership/)没有这句话）。TrendForce 3 月 3 日预计一季度 NAND 价格环比上涨 85~90%。

**容量。** [TrendForce 3 月 23 日](https://www.trendforce.com/presscenter/news/20260323-12983.html)预计 2026 年手机平均存储容量增长 4.8%，理由之一是端侧 AI 模型需要 40~60GB 系统存储作缓存；iPhone 17 起步容量升到 256GB，Mate 80 推广 512GB，128GB 可能在年底退出主流安卓机型。

三件事放在一起，含义很直接：手机内存的带宽会在下半年随 LPDDR6 上一个台阶，但每 GB 的价格在上涨，供给可能紧张好几年。端侧模型的规模将更多受内存成本限制，而不是带宽。低比特量化、KV 缓存压缩、按需加载这类软件手段的价值会继续上升。

### 五、存内计算/PIM：本月空窗

本月没有找到窗口内的存内计算/PIM 产品发布或融资。逐项核查的结果是：知存科技官网新闻在 2025-09 到 2026-04 之间没有更新；炬芯科技 3 月只有获奖类新闻（其存内计算 ATS3231 耳机方案发布于 3 月 31 日，在窗口外）；后摩智能官网无法访问；EnCharge、Sagence 等海外模拟存算公司的官网新闻源本次没有取到。ISSCC 2026（2 月）上的存内计算论文由顶会方向收录。这一方向的空窗主要是检索覆盖受限造成的（本次 Web 搜索额度用尽，中文媒体覆盖不足），不能据此判断 3 月没有国产存算动态。

### 六、口径与存疑

- **厂商倍数不能直接比较。** TI 的“延迟降 90 倍、能耗降 120 倍”以无加速器的同类 MCU 为基准；ST 的“6~9 倍”以 Cortex-M33 加 TFLite Micro 为基准；Ambiq 只说“数百亿次运算”。三家都没有给出同一模型下的绝对 μJ/推理，本月无法横向排名。
- **NXP 新闻稿的一手页面。** NXP 官网新闻页本次无法直接访问，正文取自 GlobeNewswire 分发稿的转载页（发布时间 3 月 9 日），并用 Edge AI and Vision Alliance 转载和マイナビ 3 月 18 日说明会报道交叉核对。
- **Synaptics SYN765x 的量产时间。** 新闻稿没有写送样和量产时间；另有资料称二季度送样、四季度量产，但本次未在一手页面核实，因此不写入条目。
- **SK 会长“2030 年”的说法。** 这句话只见于媒体转述，SK 海力士官方新闻稿没有出现，所以按媒体口径处理，置信度记为 medium。
- **内存带宽推算。** 文中 LPDDR6 的 128GB/s 和 85 tok/s 都基于假设的 96-bit 位宽和 3B INT4 模型，是理论上限，不是实测；实际 decode 还要扣掉 KV 缓存读取和调度开销。

### 小结

3 月这个方向的变化可以用一句话概括：**算力在往下走，内存在往上涨**。NPU 已经进入 1 美元级 MCU、蜂窝和 Wi-Fi 芯片，常开 AI 的芯片成本和功耗门槛都在快速下降；同时手机内存的价格、毛利率和供给预期都在朝不利于终端厂的方向变化。对端侧 AI 和智能体来说，近期更现实的形态是“很多颗便宜芯片上的小模型常开感知，加上手机或云端的大模型按需推理”，就像 AXClaw Box 和 Halo 眼镜那样，而不是把越来越大的模型硬塞进越来越贵的手机内存。下个月值得跟踪的是：LPDDR6 首批客户和速度档位、Atomiq 与 TinyEngine 的第三方能效实测，以及国产存算公司的产品动态。

## 5. 顶会论文：ASPLOS 2026 的手机 GPU 流式权重与 MX 格式

### 本月顶会总览：ASPLOS 2026 是唯一的主场

2026-02-27 至 03-26 这个窗口里，体系结构与系统方向真正召开的顶会只有一个：[ASPLOS 2026](https://www.asplos-conference.org/asplos2026/program/index.html)，3 月 22–26 日在匹兹堡举行（22–23 日为 workshop 和 tutorial，24–26 日为正会，共 167 篇论文，ACM 论文集 Vol.2 于 3 月 22 日上线）。会期核对结果：HPCA 2026（1 月 31 日–2 月 4 日，悉尼）和 HotMobile 2026（2 月 25–26 日，亚特兰大）都在窗口之前；EuroSys 2026（4 月 27–30 日）和 MLSys 2026（5 月 17–22 日）在窗口之后。前几周（02-06、02-13、02-20、02-27）的硬件雷达均没有收录顶会条目，所以本节的全部材料都来自 ASPLOS 2026。本节条目日期统一取论文在详细议程中所在 session 的报告日。

这届 ASPLOS 有几个直接对应端侧 AI 的信号。第一，大会单设 “Session 5B: On-Device & Edge AI”。第二，LLM 相关 session 占了议程的显著比例：serving、投机解码、KV cache、MoE、PIM、3DGS 都有专场。第三，[最佳论文](https://www.asplos-conference.org/asplos2026/awards/)颁给了一篇研究一次性柔性芯片的“极端边缘”论文，4 比特数据格式 M2XFP 也拿到荣誉提名。下面按主题拆开看，最后做小结。

### 端侧 LLM 推理系统：问题在内存，不在算力

本月和端侧推理最相关的三篇论文，处理的都是内存层次问题。

**测试时扩展搬到边缘。** Imperial College London 与微软研究院的 [FastTTS](https://doi.org/10.1145/3779212.3790161)（[arXiv](https://arxiv.org/abs/2509.00195)）把束搜索类测试时扩展做成 vLLM 插件，用投机束扩展、非对称多模型显存分配和前缀感知调度，让 1.5B/7B 生成器搭配 1.5B/7B 过程奖励模型在单张 RTX 4090 上逼近云端推理模型的准确率。论文口径下 goodput 平均提升 2.2 倍（最高 5.4 倍），延迟降低 38%–68%；在 8GB 的 RTX 3070 Ti 上仍有 1.4–1.6 倍提升。需要注意，它的“边缘”是消费级独显，不是手机 NPU。

**MoE 专家的混合精度卸载。** 上海交大与港中文的 [MoE-APEX](https://doi.org/10.1145/3779212.3790187) 把缓存未命中、重要性低的专家换成低精度版本加载，基于 llama.cpp 实现。ACM 正式版摘要称在多种边缘设备上 decode 提升 1.34–9.75 倍。它的前身预印本 [HOBBIT](https://arxiv.org/abs/2411.01433) 给出了更具体的设置：Jetson AGX Orin 上 Mixtral-8x7B（激活 14B）主精度 INT8、低精度专家 INT2，准确率损失不超过 1%。按 Orin 的 204.8GB/s 带宽推算，即使 Mixtral 全部驻留内存，INT8 decode 上限也只有约 14 tok/s。所以端侧跑 40B 级 MoE，体验上限仍由带宽决定，卸载策略只是在这个上限之下尽量少损失。同一会议上，上海交大的 [EARTH](https://doi.org/10.1145/3779212.3790155) 从硬件角度处理同一问题：把专家拆成高信息量基座和增量两部分，配合投机预取，相对已有方案最高加速 2.10 倍。

**手机 GPU 的权重流式加载。** 佐治亚大学的 [FlashMem](https://doi.org/10.1145/3779212.3790164)（[arXiv](https://arxiv.org/abs/2602.15379)）在 OnePlus 12（Adreno 750）、Pixel 8（Mali-G715）等手机上，用 2.5D 纹理内存按需流式加载权重，替代全量预载。11 个模型上内存降低 2.0–8.4 倍，加速 1.7–75 倍；几何平均相对 LiteRT 加速 1.7 倍、相对 ExecuTorch 加速 75 倍。不过测试的最大模型是 GPTNeo-2.7B，计时包含冷启动初始化，热启动场景下的优势会缩小。

同场 5B session 还有清华与微软研究院的 Neuralink（[arXiv](https://arxiv.org/abs/2410.19274)），在 OnePlus 12/Ace 3/Ace 2（骁龙 8 Gen 3/8 Gen 2/8+ Gen 1，UFS 4.0/3.1）上按神经元共激活关系重排闪存布局，端到端延迟平均提升 1.49 倍。这篇论文已于 2025 年 8 月收入 ASPLOS '25 Vol.3 论文集，本届只是会上报告，因此只作为背景，不算本月新条目。三篇合起来看，结论一致：手机上的 LLM 和多模态模型受限于 DRAM 容量、闪存 IOPS 和 GPU 缓存层次，而不是 TOPS。

### 端侧加速器与数据格式：4 比特格式与可编程稀疏

[M2XFP](https://doi.org/10.1145/3779212.3790185)（上海交大与华为计算产品线，[arXiv](https://arxiv.org/abs/2601.19213)）获最佳论文荣誉提名。它在 MXFP4 上为每 32 个元素附加 8 位元数据（每元素 0.25 位），有效精度约 4.5 比特。7B/8B 模型平均精度损失从 MXFP4 的 5.38%、NVFP4 的 2.52% 降到 1.58%，LLaMA3-70B 的困惑度从 4.84 降到 3.56（FP16 为 2.85）。硬件代价是 PE tile 面积比 MXFP4 多 4.0%，解码和量化单元合计只占 0.26% 面积。端侧 NPU 正在从 INT4 转向 FP4/MX 格式，这篇论文给出的结论是“多花 0.25 位元数据”比“换一种格式”更划算。按推算，7B 模型在 4.5 比特下权重约 3.9GB，若手机 LPDDR5X 带宽按约 77GB/s 计，decode 上限约 20 tok/s。

中科院计算所与睿芯集成的 [BitRed](https://doi.org/10.1145/3779212.3790132) 把位级稀疏加速拆成三条 RISC-V 自定义指令。TSMC 28nm 下面积 5.072mm²，功耗 458–550mW，相对 Bitlet 最高加速 9.4 倍，摘要称效率最高为 Jetson Orin 32GB 的 13.5 倍。它代表了用 ISA 扩展而不是固定数据通路来做边缘 AI 协处理器的路线，很适合 MCU 和 IoT SoC。

XR 方向，KAIST 与 Meta 的 [Neo](https://doi.org/10.1145/3779212.3790192)（[arXiv](https://arxiv.org/abs/2511.12930)）指出 3DGS 的瓶颈在排序带宽，于是复用上一帧的排序结果做增量更新。7nm 综合后面积 0.387mm²、功耗约 0.8W，在 51.2GB/s 的 LPDDR4 预算下 QHD 平均 99.3 FPS，相对 Orin AGX 提升 10 倍，DRAM 流量降低约 94%。上海交大的 [Nebula](https://doi.org/10.1145/3779212.3790190) 则走端云协同渲染路线，处理超大规模 3DGS 场景在 VR 中的带宽问题。纽约大学的 [Segment Only Where You Look](https://doi.org/10.1145/3779212.3790216) 利用注视行为，只在用户看的区域做分割，降低 AR 设备的算力需求。三篇论文都说明，AR/VR 眼镜的端侧 AI 正在按“注视点加时间复用”的思路做专用硬件。

### 存内计算与“权重即电路”：两种极端的去搬运方案

Session 4D 和 3A 有一批 PIM/CIM 论文。中科院计算所的 [Ouroboros](https://doi.org/10.1145/3779212.3790197)（[arXiv](https://arxiv.org/abs/2603.02737)）把 215mm×215mm 晶圆做成 54GB SRAM 数字 CIM，权重、激活和 KV 全部在片上。平均吞吐提升 4.1 倍、能效提升 4.2 倍，每 token 能耗相对 DGX A100 降低 84%、相对 Cerebras WSE-2 降低 66%。RPI 与 IBM 的 [STARC](https://doi.org/10.1145/3779212.3790226) 把 KV 按语义聚类后映射到 HBM-PIM 的连续行，相对逐 token 稀疏方法降低注意力延迟 19%–31%、能耗 19%–27%。上海交大的 [REPA](https://doi.org/10.1145/3779212.3790212) 用可重构 ReRAM PIM 同时承担 KV 卸载和计算，速度比 A100 快 1.5–6.5 倍。

最激进的是中科院计算所与寒武纪的 [HNLPU](https://doi.org/10.1145/3779212.3790169)（[arXiv](https://arxiv.org/abs/2508.16151)）：把 gpt-oss 120B 的 FP4 权重通过 Metal-Embedding 固化进金属层，70 层掩膜中 60 层可以复用，NRE 降到 5946 万至 1.235 亿美元。仿真结果为 249,960 tok/s、36 tok/J，分别是 H100 的 5,555 倍和 1,047 倍。这些都是数据中心方案，对端侧的参考在于方向：端侧 LPDDR 带宽长期只有几十到一百多 GB/s，PIM 和“权重固化”都是从根本上减少权重读取的路线。如果将来把 1B 级常驻模型固化进低功耗芯片，就可能出现“模型即芯片”的端侧产品（推断）。

### 低功耗、可靠性与极端边缘

最佳论文 [Lifetime-Aware Design for Item-Level Intelligence at the Extreme Edge](https://doi.org/10.1145/3779212.3790182)（哈佛、Pragmatic、Qamcom，[arXiv](https://arxiv.org/abs/2509.08193)）研究嵌入食品包装、医疗贴片的一次性柔性芯片。这类芯片只有 kHz 级频率和几千门规模，作者用全开源工具在柔性 PDK 上流片到 30.9kHz，FlexiBits RISC-V 核能效提升 2.65–3.50 倍，并指出不同应用寿命相差约 1000 倍，应按寿命权衡隐含碳和运行碳。

北大与 Georgia Tech 的 [CREATE](https://doi.org/10.1145/3779212.3790147)（[arXiv](https://arxiv.org/abs/2601.14140)）面向电池供电的具身智能体。它以 22nm、144 TOPS 的 INT8 脉动阵列为平台，通过电路、模型、应用三层容错设计实现低电压运行，计算能耗平均节省 40.6%，芯片级节省 29.5%–37.3%，估计续航提升 15%–30%。UCSD 的 [PrioriFI](https://doi.org/10.1145/3779212.3790204) 则用 Hessian 排序加速边缘神经网络的故障注入评估。这几篇论文都在说明，端侧芯片在降压省电时，必须先知道模型哪些位和哪些层出错是能容忍的。

### 通用处理器：苹果芯片上的内存模型实测

特拉维夫大学的 [Arm Weak Memory Consistency on Apple Silicon](https://doi.org/10.1145/3779212.3790129)（[PDF](https://www.cs.tau.ac.il/~mad/publications/asplos2026-TSO.pdf)）利用 M1/M4 为 Rosetta 准备的 TSO 模式做同硬件对比。49 个应用在 TSO 下慢速的调和平均只有 1.9%（排除离群项），较大的减速来自苹果实现上的瑕疵，且 M4 已修复 SIMD 问题。这对 Arm PC 上运行 x86 转译的 AI 应用来说是好消息，但与 NPU 推理本身关系不大。

### 小结：本月顶会对端侧 AI 的三点启示

第一，端侧推理的主要矛盾已经从算力转到内存层次。FlashMem、MoE-APEX、Neuralink、Neo 的收益都来自减少搬运和复用数据，而不是增加 TOPS。评估端侧芯片时，应优先看 LPDDR 带宽、闪存 IOPS 和片上缓存，再看 NPU 峰值算力。第二，4 比特浮点格式正在成为端侧 NPU 的竞争点。M2XFP 这类“格式加少量元数据”的方案只增加 4% 左右的 PE 面积，就能明显缩小与 FP16 的精度差距，且有华为参与，值得观察能否落地。第三，学术界开始系统研究端侧智能体：FastTTS 讨论边缘测试时扩展，CREATE 讨论具身智能体的低压可靠性，大会也单设了 On-Device & Edge AI session。

需要提醒的是，本月几乎所有数字都来自论文自报，且以模拟和综合为主（Neo、Ouroboros、HNLPU、M2XFP、CREATE 都没有流片），真机实测只有 FlashMem、Neuralink、FastTTS、Apple TSO 和柔性芯片流片几项。另外，MoE-APEX 和 BitRed 只拿到了 ACM 正式版摘要，设备细节引自前身预印本，置信度为中等。

## 6. arXiv 精选：持续负载实测、手机 PIM 与直接编程神经引擎

### 总览：从“能不能跑”转向“能不能一直跑”

2026-02-27 至 2026-03-26 这个窗口里，arXiv 上与端侧硬件和系统相关的论文，关注点明显变了。上个月讨论的核心是“权重和 KV cache 放在哪里”；这个月更多论文开始在真机上做**持续负载、散热、内存争用和安全隔离**的测试，回答一个更接近产品的问题：手机上的智能体能不能全天候运行。窗口覆盖的往周（2026-02-06、02-13、02-20、02-27 各周）硬件雷达 `hardware.items` 均为空，因此下文全部基于本次新收的 22 篇论文（按 arXiv v1 提交日计，分布在 03-01 至 03-26）。其中有 DAC 2026、DATE 2026、ISLPED 2026、MobiCom 2026、MLSys 2026、ACL 2026 录用稿，按规范以 v1 日期收录。

大致可以分为六类：
1. 手机与 PC 真机实测（持续负载、Apple ANE、统一内存上的推测解码）；
2. 厂商论文：三星 LPDDR-PIM、Meta MobileLLM-Flash、高通端侧推理模型；
3. 手机系统软件：异构调度、TrustZone 隔离、应用冷启动、算子生成；
4. 机器人与边缘模组：Jetson 上的 VLA；
5. 超低功耗与 MCU：调频、电源编排、MX 格式、端侧训练；
6. 存内计算与新型存储，以及对端侧有参考价值的数据中心架构。

本月论文给出的端侧模型规模集中在 0.6B–11B：手机上实测的最大是 7B 级（高通，未给 tok/s），PC 统一内存上是 11B（8-bit）。

### 一、真机实测：散热和调度开销才是真瓶颈

本月最值得读的实测是 [LLM Inference at the Edge](https://arxiv.org/abs/2603.23640)（03-24）。作者用同一个 4-bit Qwen2.5-1.5B 和固定的 258 token 提示词，在四个平台上各连续跑 20 轮：
- iPhone 16 Pro 前两轮均值 37.58 tok/s，第 8 轮起进入 Hot 状态，均值降到 22.56 tok/s，比峰值低 44.1%；
- Galaxy S24 Ultra（骁龙 8 Gen 3，走 Adreno GPU）前 5 轮只有 9.93 tok/s，第 6 轮 GPU 频率被温控压到 231 MHz，实验被迫终止；
- 树莓派 5 + Hailo-10H 只有 6.914 tok/s，但整机 1.87 W、270.5 mJ/token，19 轮吞吐变异系数仅 0.04%；
- RTX 4050 笔记本 131.7 tok/s，34.1 W，约 297.3 mJ/token。

按 [HeRo](https://arxiv.org/abs/2603.01661) 论文给出的骁龙 8 Gen 3 带宽 76.8 GB/s 推算，1.5B 4-bit 模型的解码上限约 85–95 tok/s，S24 Ultra 的实测只有约十分之一。可见 MLC-LLM GPU 路径的软件效率和温控远比 DRAM 带宽更早成为瓶颈（推算）。

第二篇是 [Orion](https://arxiv.org/abs/2603.06728)（03-06）。一位独立开发者绕过 CoreML，用私有 API 直接在 M4 Max 的神经引擎上做 LLM 推理和训练，整理出 20 条 ANE 约束，其中 14 条是首次记录。论文引用的第三方测量显示：
- 苹果标称的 38 TOPS 是 INT8 口径，ANE 实际会先反量化为 FP16，实测峰值约 19 TFLOPS；
- 每次 IOSurface 往返约 2.3 ms，所以 GPT-2 124M 在 ANE 上解码 170 tok/s，反而不如 CPU 的 283 tok/s。

它的价值在于：把苹果 NPU 的“适用区间”说清楚了，即大批量预填充、常驻小模型和 LoRA 热切换。

第三篇是 [Bielik 11B 推测解码](https://arxiv.org/abs/2604.16368)（03-22），测试机是 M2 Pro（200 GB/s）。8-bit 的 11B 目标模型基线为 14.6–15.1 tok/s，已达到带宽上限（约 18 tok/s，推算）的 80% 左右。跨家族草稿模型只在结构化文本上带来最多 1.7 倍加速，GPU 占用率始终约 28%。结论很直接：在统一内存设备上，“推测解码必然加速”不成立。

### 二、厂商论文：三星押 PIM，Meta 和高通押模型设计

三星 SAIT 与三星电子的 [PIM-SHERPA](https://arxiv.org/abs/2603.09216)（03-10）是本月唯一由存储厂商署名、在手机上验证的 PIM 系统论文。它指出 LPDDR5X-PIM 在手机上有两个冲突：
- 内存属性：解码时权重必须放在不可缓存区，否则请求会命中缓存、触发不了 PIM；预填充却需要缓存复用；
- 权重排布：主机友好排布与 PIM 排布不一致。

以往的解决办法是存两份权重，Llama 3.2 3B 就要多占 6 GB，手机放不下。PIM-SHERPA 用 DRAM 双缓冲和在线重排把内存占用降低约 48%，TTFT 与 FACIL 相当。测试平台是 Galaxy S24+（Exynos 2400，LPDDR5X 68.264 GB/s），解码阶段为 PIM 仿真。按带宽推算，3B BF16 模型在这颗芯片上的解码上限约 11 tok/s，这正是 PIM 想突破的地方。

Meta 的 [MobileLLM-Flash](https://arxiv.org/abs/2603.15954)（03-16）走另一条路：直接用 Galaxy S25（骁龙 8 Elite）上的 ExecuTorch 实测延迟来搜索模型结构。它不用任何自定义算子，产出 350M/650M/1.4B 三个模型。1.4B 版本在 4 个 CPU 线程、W4A8 下的表现：
- 1k 上下文解码 60.52 tok/s；
- TTFT 在 1k/2k/4k 上下文分别为 3.40/9.08/16.50 s。

数字也暴露了 CPU 路径在长上下文预填充上的短板。

高通 AI 研究院的 [Efficient Reasoning on the Edge](https://arxiv.org/abs/2603.16867)（03-17）在 Qwen2.5-7B 上把推理能力做成按需启用的 LoRA，用强化学习把推理 token 减少 2.4 倍；它还利用“解码受带宽限制、算力有余”的特点做多路并行生成，准确率最多提升约 10%。模型量化到 W4A16KV8 后，准确率仍在全精度的 2% 以内。遗憾的是正文没有给出测试 SoC 和 tok/s。按 7B×4-bit≈3.5 GB 估算，单流解码上限约 20 tok/s（推算）。

### 三、系统软件：手机智能体是一条多模型流水线

几篇论文共同指出：端侧智能体不是“一个 LLM”，而是多个模型和多个阶段组成的流水线。
- [HeRo](https://arxiv.org/abs/2603.01661)（北大，DAC 2026）在 Redmi K80（骁龙 8 Gen 3）和 OnePlus 13（骁龙 8 Elite）上调度智能体 RAG。它考虑加速器亲和性、形状敏感性和共享带宽争用，端到端延迟最多降低 10.94 倍。
- [FlexServe](https://arxiv.org/abs/2603.09046)（上海交大 IPADS）在 RK3588 上把 LLM 推理放进 TrustZone，让内存页和 NPU 能在受保护与不受保护模式间切换。TTFT 相对朴素方案平均快 10.05 倍，多模型智能体工作流最多快 24.3 倍。
- [AppFlow](https://arxiv.org/abs/2603.17259)（西工大，MobiCom 2026）处理的是 GB 级应用的冷启动问题：在 Pixel 8 上，86.6% 的 GB 级冷启动超过 1 秒。AppFlow 联合调度预载、回收和查杀，延迟降低 66.5%。
- [MobileKernelBench](https://arxiv.org/abs/2603.11935)（浙大/阿里 MNN）在小米 13 上测试大模型能否写手机算子。现有模型编译失败率超过 54%，多智能体系统 MoKA 把成功率提到 93.7%。
- 哈工大的 [HuoziIME](https://arxiv.org/abs/2604.14159) 是一个完整的端侧智能体产品原型：Qwen3-0.6B 量化后 485 MB，在天玑 9000 上解码 24–25 token/s，额外峰值内存 1.12 GB。

### 四、机器人与边缘模组：带宽墙比手机更早到来

Google 与普渡的 [VLA 剖析](https://arxiv.org/abs/2603.02271)（03-01）给出了本月最清楚的带宽证据：
- MolmoAct-7B 在 Jetson Orin 和 Thor 上，动作生成阶段最多占 75% 延迟；
- Thor 算力是 Orin 的 5 倍，延迟只改善 1.4 倍，与两者带宽比 273/203≈1.34 几乎一致。

[LiteVLA-Edge](https://arxiv.org/abs/2603.03380) 则把模型压到 SmolVLM-256M 级，用 llama.cpp 在 Jetson AGX Orin 上做到 150.5 ms（约 6.6 Hz），仍低于 10 Hz 的常用目标。同样在 Jetson 上，[SparseDVFS](https://arxiv.org/abs/2603.21908) 按算子稀疏度同时调 CPU、GPU 和内存控制器频率，在 Orin Nano 上平均能效提升 78.17%。

### 五、超低功耗与 MCU：精度格式与电源编排

- ETH 的 [VMXDOTP](https://arxiv.org/abs/2603.04979)（DATE 2026）为 RISC-V 向量扩展加入 MXFP8/MXFP4 点积指令。12nm、1 GHz 下 MXFP4 达到 250 GFLOPS、1,632 GFLOPS/W，面积开销 7.2%。
- 同组的 [TrainDeeploy](https://arxiv.org/abs/2603.09511) 在 8 核 RISC-V PULP 集群上完成 Transformer 的端侧 LoRA 微调，但模型只有 0.28M 参数。
- 南加大的 [PowerFlow-DNN](https://arxiv.org/abs/2603.23882)（ISLPED 2026 最佳论文提名）由编译器统一编排 40nm 加速器的电压轨和电源门控，能耗最多降低 48%。
- [HYPER-TINYPW](https://arxiv.org/abs/2603.24916)（MLSys 2026）用“加载时生成权重”压缩 MCU 模型，225 kB 即可达到 1.4 MB CNN 的精度。

### 六、存内计算、新型存储与数据中心参考

港大的 [忆阻器 LLM 研究](https://arxiv.org/abs/2603.13725)（DAC 2026）发现，模拟 CIM 的非理想性对多步推理的伤害大于简单任务，浅层冗余是最有效的免训练缓解手段。[HAVEN](https://arxiv.org/abs/2603.01175) 建模了封装内的高带宽闪存（HBF）：按每堆栈 460 GB/s 的假设，RAG 重排吞吐最多提升 20 倍。这是除 DRAM 之外的另一条“容量换带宽”路线。

数据中心方向有两篇对端侧有直接参考：
- [DUET](https://arxiv.org/abs/2603.15530) 把混合 Mamba 模型的预填充和解码交给不同封装，相对 B200 首 token 快 4 倍；
- 南加大的 [GDN FPGA 加速器](https://arxiv.org/abs/2603.05931) 把 2 MB 线性注意力状态常驻片上 BRAM，单 token 63 µs，能效最高为 H100 的 60 倍。

后者说明：端侧 NPU 的 SRAM 只要能装下 SSM 或线性注意力的状态，混合模型的长上下文解码就能绕开 KV cache 的增长。

此外，窗口内还有一些相关但未单独收录的工作：
- 在 RTX 3090 上模拟边缘显存约束的 MoE 卸载 [DyMoE](https://arxiv.org/abs/2603.19172)；
- ASPLOS 2026 的 [Ouroboros](https://arxiv.org/abs/2603.02737)（晶圆级 SRAM CIM）和 [ZipServ](https://arxiv.org/abs/2603.17435)（无损压缩推理）；
- 多 SSD 的 KV 卸载 [Swarm](https://arxiv.org/abs/2603.17803)；
- 在 M4 Pro 上用 MLX 把语音模型注意力替换为 O(n) 门控的 [LPA](https://arxiv.org/abs/2603.16922)；
- 利用端侧 VLM 动态分块做侧信道攻击的 [Shape and Substance](https://arxiv.org/abs/2603.25403)。

### 七、核对“能跑多大模型”：用带宽倒推上限

把本月论文里的实测数字与“内存带宽 ÷ 每 token 读取的权重字节数”对照（以下上限均为推算，不是论文数据）：
- 骁龙 8 Gen 3（76.8 GB/s）跑 1.5B 4-bit：上限约 85–95 tok/s。S24 Ultra 实测 9.93 tok/s，差距主要来自软件路径和温控。
- Exynos 2400（68.264 GB/s）跑 Llama 3.2 3B BF16（约 6 GB）：上限约 11 tok/s。这也是三星要用 PIM 把有效带宽提高数倍的原因。
- 骁龙 8 Elite CPU 跑 MobileLLM-Flash 1.4B 4-bit：实测 60.5 tok/s，相当于每秒读取约 42 GB 权重，约为 HeRo 论文所列骁龙 8 Elite 带宽（84.8 GB/s）的一半。
- M2 Pro（200 GB/s）跑 11B 8-bit：上限约 18 tok/s，实测约 15 tok/s，已达上限的八成。
- Jetson Orin（203 GB/s）和 Thor（273 GB/s）跑 7B BF16 VLA：上限分别约 14.5 和 19.5 tok/s。实测的 1.4 倍差距正好落在带宽比附近。

由此可见，厂商宣传的“能跑 7B、13B”大多只说明内存装得下。真正决定交互体验的是带宽，以及能否持续保持频率。对端侧智能体来说，0.6B–3B 的 4-bit 模型才是当前手机上可以全天候常驻的规模；7B 及以上更适合按需唤醒，或配合推理适配器、并行生成等手段，用额外的算力换回质量。

### 总结：三个判断

1. **持续性能比峰值更重要。** 本月唯一的跨平台持续负载实测显示，旗舰手机 GPU 跑 1.5B 模型几轮后就降频或被系统终止。端侧智能体的硬件指标应改为“持续 tok/s + J/token + 温度曲线”。
2. **NPU 的瓶颈在软件开放度和调度开销。** 苹果 ANE 的 2.3 ms 调度往返、高通方案缺少公开的 tok/s、HeRo 对异构调度的十倍收益，都说明 TOPS 数字与可用性能之间隔着一整层系统软件。
3. **带宽墙正在推动存储侧创新。** 三星 LPDDR-PIM、HBF、片上状态常驻、预填充与解码分离，这些路线都在回应同一个事实：Jetson Thor 算力翻 5 倍，延迟只快 1.4 倍。下一代端侧芯片的胜负手更可能是带宽和存内计算，而不是 TOPS。

存疑点：高通 Efficient Reasoning on the Edge 未披露测试 SoC 与吞吐；PIM-SHERPA 的解码性能来自 PIM 仿真；PowerFlow-DNN 摘要与正文的最优差距数字不一致；HYPER-TINYPW 为个人作者。以上均已在条目中标注。

## 7. 总结：对端侧智能体意味着什么，以及 4 月该看什么

**对端侧智能体的含义**

1. **硬件底座到位了，常驻模型仍是 3–4B。** Qwen3-4B w4a16 在手机和 Arm PC 上都是约 29–30 tok/s（官方），Nexa 给骁龙 X NPU 的模型预算约 4B，Wear Elite 能装下 2B，但带宽只够约 12 tok/s（推算）。7B 级模型在手机上只适合按需唤醒：高通 AI 研究院的 7B 推理模型没有给出 tok/s，按带宽推算单流上限约 20 tok/s。
2. **提速靠解码算法和 KV 管理，不靠 TOPS。** 自推测解码让 3B 模型快 1.77–2.28 倍（官方），TurboQuant 把 KV 缓存至少压缩 6 倍，FlashMem 用流式加载换内存。智能体多轮、长输出，这些手段比 NPU 峰值更直接；但 Bielik 实验提醒，推测解码的收益取决于接受率。
3. **全天候运行要同时看持续性能和隔离。** 旗舰手机 GPU 连续跑几轮就降频（iPhone 16 Pro -44.1%）或被终止（S24 Ultra），Hailo-10H 速度慢但 1.87W 下稳定（论文实测）。FlexServe 在 RK3588 上把 LLM 放进 TrustZone，多模型智能体工作流比朴素方案最多快 24.30 倍；NemoClaw 用 OpenShell 给常驻 Agent 加策略护栏。评估端侧智能体硬件，应改用“持续 tok/s + J/token + 安全隔离”。
4. **现实形态是“设备群 + 端云混合”。** 手表、眼镜负责感知（Wear Elite、Alif 方案的 Halo 眼镜、AkidaTag），手机负责模型（联发科眼镜方案把算力全放在天玑 9500），PC 负责本地 Agent（NemoClaw），重推理在云端（新 Siri 据报道跑在 Google 数据中心，AXClaw Box 调用云端大模型）。HeRo 在手机上调度智能体 RAG 把延迟最多降低 10.94 倍，说明多模型流水线的调度本身就是性能来源。

**留给 4 月的问题（结论已写在 4 月硬件洞察）**

- **端侧模型交付**：LiteRT-LM 0.9.0 正式版（3 月 27 日）与 3 月 31 日的 Gemma 4 之后，2–4B 模型在手机 NPU/GPU 上的官方实测。4 月月报的结论是端侧模型层在 4 月一次交齐。
- **推测解码的扩散**：能否从高通 AI Hub 进入更多官方端侧运行时，以及在手机上实际对话中的接受率。
- **内存账单**：TrendForce 对 2Q26 合约价的预测，4 月底高通、联发科、Apple 财报对内存约束的表述；LPDDR6 的首批客户和速度档位。
- **Apple 软件**：iOS 26.5 能否兑现 Gemini 版 Siri，WWDC 前 Core AI 的进一步消息，A18 入门 iPad 是否发布。
- **会议与国产**：EuroSys（4 月 27–30 日）的端侧系统论文；华为、紫光展锐和国产存算公司的补检。

> 口径说明：标“官方”的是厂商发布的数字，“论文”是论文自报（ASPLOS 的 Neo、Ouroboros、HNLPU、M2XFP、CREATE 都没有流片，PIM-SHERPA 的解码为仿真），“媒体”和“爆料”未经厂商确认，“推算”是本文按“带宽 ÷ 每 token 读取字节数”等公开参数算出的理论上限，实际值会更低。**检索覆盖：** 3 月素材检索时 WebSearch 额度已用完，华为麒麟、紫光展锐和国产存算（知存、后摩、苹芯、九天睿芯）只能靠官网直查：知存官网新闻在窗口内无更新，后摩官网无法访问，中文媒体覆盖不足，因此这些方向的“空窗”不能当作 3 月没有动态。高通 AI 研究院论文只核实到一篇（arXiv 检索被限流）；2 月月报关注的 Innatera 现场实测、DARTH-PUM 正式报告本月素材未覆盖。**3 月没有检索到新品的方向：** 高通、联发科、三星 Exynos、华为麒麟、紫光展锐、瑞芯微均无新手机 SoC；Google 无新芯片，Tensor G6 无可信新爆料；小米只有“玄戒很可能每年一代”的表态；Hailo、Axelera 无新发布；存内计算/PIM 无产品级发布或融资。**存疑项：** Wear Elite 是否有独立 eNPU、CPU 频率和内存规格只有媒体来源；Apple 的“4 倍”“3 倍”都是内部测试的最高值；PCC 利用率、新 Siri 部署、Core AI 和 Siri 扩展均为媒体或爆料；SK 会长“2030 年”只见于媒体转述；TrendForce 的 40–60GB 是缓存空间口径，不是单个模型大小；DGX Spark 多机互联为媒体口径；Synaptics SYN765x 量产时间未核实；MoE-APEX、BitRed 只拿到正式版摘要；PowerFlow-DNN 摘要与正文的最优差距数字不一致；Bielik、HuoziIME 的 arXiv 编号为 2604，但 v1 在 3 月，按 v1 日期收录；TurboQuant 论文 2025 年 4 月已上 arXiv，按官方博客发布日收录，8 倍加速为 H100 数据；Ouroboros 的 arXiv v1 为 3 月 3 日，按 ASPLOS 报告日收录。
