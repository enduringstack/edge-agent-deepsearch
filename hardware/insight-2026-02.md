# 硬件洞察：端侧 AI 芯片月报（2026-01-30 ~ 2026-02-26）

> **说明：** 本期为 2026-10 回填，规则同周报硬件雷达；3 月 2 日起的 MWC 归入 3 月。
>
> **一句话结论：2 月是“内存月”，也是“ISSCC 月”。** 窗口内没有新的旗舰 SoC 家族，唯一的新芯片商用节点是 Galaxy S26 上的骁龙 8 至尊版第五代 for Galaxy 和 2nm Exynos 2600。决定端侧 AI 走向的是内存：1Q26 手机 LPDDR 合约价预计单季涨约 90%，高通把“内存可得性”写进指引，S26 停在 12GB。ISSCC 上 LPDDR6 跑到 14.4Gbps，端侧 LLM 芯片改按 μJ/token 比较。软件侧，高通开源 Hexagon-MLIR，Android 推出 AppFunctions 并由系统仲裁 NPU。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断与时间线；第 1–6 节依次为 高通 / Apple 与 Google / 其他 SoC 与 PC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选；第 7 节总结对端侧智能体的含义和 3 月观察清单。逐条动态见 01-30、02-06、02-13、02-20 四周首页的“硬件雷达”。

## 0. 总览：2 月的六个判断

**判断一：内存从成本项变成了端侧模型规模的上限。**

| 信号 | 数字 | 口径 |
|---|---|---|
| [TrendForce 1Q26 预测上调](https://www.trendforce.com/presscenter/news/20260202-12911.html)（02-02） | 标准 DRAM 季涨 55–60% → 90–95%；LPDDR4X/5X 约 +90%，史上最大单季涨幅 | 第三方预测 |
| [TrendForce 手机产量](https://www.trendforce.com/presscenter/news/20260211-12922.html)（02-11） | 2026 年 -10%；8GB+256GB 合约价同比约 +200%，占 BOM 30–40% | 第三方预测 |
| [高通 Q1 FY26](https://www.qualcomm.com/news/releases/2026/02/qualcomm-announces-first-quarter-fiscal-2026-results)（02-04） | Q2 营收指引 102–110 亿美元，手机约 60 亿；出货“100% 由内存可得性决定” | 官方（财报会） |
| [Apple 采购 LPDDR5X](https://www.mactrast.com/2026/02/apple-reportedly-agrees-to-pay-double-for-samsung-memory-chips-while-it-works-to-keep-iphone-18-prices-flat/)（02-26） | 12GB 颗粒约 30 → 70 美元 | 媒体（单一韩媒信源） |
| [Galaxy S26](https://news.samsung.com/global/samsung-unveils-galaxy-s26-series-the-most-intuitive-galaxy-ai-phone-yet) / [Pixel 10a](https://store.google.com/us/magazine/meet-google-pixel-10a?hl=en-US) | S26 全系 12GB 起，16GB 仅 Ultra 1TB 版；Pixel 10a 沿用 Tensor G4 + 8GB | 官方 |

联发科 CEO 在 ISSCC 称内存约占 XPU 物料成本 50%（[TrendForce 转述](https://www.trendforce.com/news/2026/02/25/news-mediatek-ceo-flags-memory-as-one-of-xpu-bottlenecks-now-making-up-50-of-costs/)）。12GB 扣除系统占用后，旗舰现实的常驻模型是 3–4B INT4（推算）。

**判断二：带宽在升级，容量被价格压住，闪存被重新定位为权重层。**

| 部件 | 数字 | 口径 |
|---|---|---|
| [SK 海力士 LPDDR6](https://doi.org/10.1109/isscc49663.2026.11409121) | 16Gb，1.025V 下 14.4Gbps/pin；能效比 LPDDR5 高 20% 以上 | 论文（ISSCC） |
| [三星 LPDDR6](https://doi.org/10.1109/isscc49663.2026.11409018) | 12.8Gbps，带宽比 LPDDR5X 高 33.3%，每比特能耗低 21%；另有 2nm PHY 14.4Gbps | 论文（ISSCC） |
| [铠侠 UFS 5.0 样品](https://americas.kioxia.com/en-us/business/news/2026/ssd-20260223-1.html) | 双通道有效读写约 10.8GB/s，512GB/1TB | 官方 |
| [HBF 标准化](https://www.sandisk.com/company/newsroom/press-releases/2026/2026-02-25-sandisk-and-sk-hynix-begin-global-standardization-of-next-generation-memory-solution-high-bandwidth-flash-hbf) | 闪迪与 SK 海力士在 OCP 成立工作组，未给规格 | 官方 |
| 8B INT4 decode 上限 | LPDDR5X（约 85GB/s）约 21 tok/s；LPDDR6（假设约 154GB/s）约 38 tok/s | 推算 |

另有[爆料](https://www.notebookcheck.com/Xiaomi-18-erstmals-nicht-mit-bestem-2nm-Snapdragon-Chip-Leaker-mit-Details-zum-Snapdragon-8-Elite-Gen-6-Duo.1224191.0.html)称 2nm 骁龙 8 第六代仅 Pro 版支持 LPDDR6（高通未确认）。

**判断三：端侧智能体写进了量产旗舰的卖点，但架构仍是端云混合。**

| 发布 | 端侧相关事实 | 口径 |
|---|---|---|
| [骁龙 8 至尊版第五代 for Galaxy](https://www.qualcomm.com/news/releases/2026/02/qualcomm-unveils-the-snapdragon-8-elite-gen-5-for-galaxy--drivin) | NPU +39%、CPU 最高 +19%、GPU +24%（对比 S25 Ultra）；TOPS 未披露 | 三星官方 |
| Exynos 2600 | 首颗 2nm GAA 手机 SoC；NPU 生成式 AI 性能比 Exynos 2500 高 113% | 三星官方 |
| [AppFunctions / UI 自动化](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html) | 函数本地执行；规划由 Gemini 3 系列模型承担 | Google 官方 |
| [诈骗检测](https://blog.google/products-and-platforms/platforms/android/samsung-unpacked-2026/) | “analysis happens entirely on your device”；模型规模未披露 | Google 官方 |
| [新 Siri](https://9to5mac.com/2026/02/11/apple-reportedly-pushing-back-gemini-powered-siri-features-beyond-ios-26-4/) | 个人数据与 App 内操作可能推迟到 iOS 26.5 / 27 | 爆料（彭博） |

按第三方规格库约 84.8GB/s 推算，S26 Ultra 上 3B / 7B INT4 的 decode 上限约 50 / 22 tok/s。

**判断四：ISSCC 把端侧 LLM 芯片的计量单位换成了 μJ/token。**

| 芯片（ISSCC 2026） | 关键数字 | 备注 |
|---|---|---|
| [KAIST SoulMate](https://doi.org/10.1109/isscc49663.2026.11409048) | 28nm，片上 RAG+LoRA；推理 26.3 / 微调 56.8 μJ/token；9.8–180.5mW | 模型未披露 |
| [KAIST Tri-Oracle](https://doi.org/10.1109/isscc49663.2026.11408987) | VLM，17.78 μJ/token，合并 68% 冗余 token | 模型未披露 |
| [东南大学](https://doi.org/10.1109/isscc49663.2026.11409212) / [SMoLPU](https://doi.org/10.1109/isscc49663.2026.11409285) | 旋转量化 LLM 51.6 μJ/token；MoE + 投机解码 122.1 μJ/token | 模型未披露 |
| [港科大 ReRAM 堆叠](https://doi.org/10.1109/isscc49663.2026.11409211) | LLaMA2-7B 17.82 tok/s、123.41 mJ/token | 4 芯片，含 LPDDR3 外存访问 |
| [清华](https://doi.org/10.1109/isscc49663.2026.11408953) | 105–685 μs/token | 口径存疑 |

各篇的模型、精度和是否计入外存都不同，不能横向排名；计入外存后，7B 模型每 token 能耗会升到百毫焦量级（港科大）。

**判断五：软件栈和非主流硬件在不加内存的前提下挤性能。**

| 工作 | 数字 | 口径 |
|---|---|---|
| [Hexagon-MLIR 开源](https://www.qualcomm.com/developer/blog/2026/02/build-faster-on-hexagon-npu-tritor-pytorch-with-hexagon-mlir-open-source) | Triton/PyTorch 直编 Hexagon；GELU fp16 向量化 63.9 倍 | 论文（kernel 级，无端到端 LLM） |
| [MLX 0.30.6](https://github.com/ml-explore/mlx/releases/tag/v0.30.6) | 4×M3 Ultra 跑 123B：prefill 303 tok/s；decode 几乎不变 | PR 实测 |
| [Hummingbird+](https://doi.org/10.1145/3748173.3779189) | Qwen3-30B-A3B 4bit decode >18 tok/s，BOM <150 美元 | 论文（带宽未披露） |
| [NanoFLUX](https://arxiv.org/abs/2602.06879) | 约 2.4B 文生图，骁龙 8 Elite NPU 端到端约 2.5 秒 | 论文实测（月内唯一手机 NPU 数据） |

**判断六：NPU 成为 MCU 和连接芯片的标配，常开感知下探到亚毫瓦。**

| 信号 | 数字 | 口径 |
|---|---|---|
| [Arm Flexible Access](https://newsroom.arm.com/blog/arm-flexible-access-broadens-scope-to-help-companies-build-silicon-faster) | 纳入 Ethos-U85，年费 8.5 万美元、不限流片 | 官方 |
| [ST Stellar P3E](https://newsroom.st.com/media-center/press-item.html/p4749.html) | 首款带 NPU 的车规 MCU，推理能效最高为 MCU 内核 30 倍，2026Q4 量产 | 官方 |
| [Ceva](https://www.ceva-ip.com/press/ceva-highlights-breakthrough-year-for-ai-licensing-and-physical-ai-adoption-in-2025/) / [TI](https://news.silabs.com/2026-02-04-Texas-Instruments-to-acquire-Silicon-Labs) | Ceva 2025 年签 10 份 NPU 授权；TI 以约 75 亿美元收购 Silicon Labs | 官方 |
| [索喜 + Innatera](https://www.innatera.com/newsroom/socionext-and-innatera-introduce-integrated-60-ghz-fmcw-radar-and-neuromorphic-edge-ai-for-human-presence-detection/) | 雷达人体存在检测 <1mW、准确率 >99% | 官方（测试集未公布） |

### 2 月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 02-02 | TrendForce 上调 1Q26 DRAM 涨幅；Arm 纳入 Ethos-U85；HPCA 正会开幕 | 内存 / 研究 |
| 02-03 | Xcode 26.3 接入 MCP 智能体 | Apple |
| 02-04 | 高通 Q1 FY26 财报；联发科法说；TI 宣布收购 Silicon Labs | 产业 |
| 02-06 | 高通开源 Hexagon-MLIR；MLX 0.30.6；NanoFLUX | 软件 / 研究 |
| 02-10 | ST Stellar P3E；爱芯元智港股上市 | MCU / 产业 |
| 02-11 | TrendForce：手机产量 -10%；爆料：骁龙 8 第六代仅 Pro 版支持 LPDDR6、新 Siri 推迟 | 内存 / 爆料 |
| 02-12 | 三星首批商用 HBM4 出货 | 内存 |
| 02-15~19 | ISSCC 2026：LPDDR6、GB10、MADiC、第 31 场端侧 LLM 芯片；02-17 AI Hub 加入 QAIRT 2.43，爆料 Apple 三款 AI 可穿戴 | 研究 / 内存 |
| 02-18 | Pixel 10a（Tensor G4 + 8GB）；高通印度 AI 基金 | Google / 产业 |
| 02-23 | 铠侠 UFS 5.0 送样；OpenVINO 2026.0；索喜 + Innatera | 存储 / 软件 |
| 02-24 | Apple 休斯敦 AI 服务器提前出货；Axelera 融资超 2.5 亿美元；FPGA 2026 上 Hummingbird+ 跑 30B MoE | 产业 / 研究 |
| 02-25 | Galaxy Unpacked：S26、骁龙 8 至尊版第五代 for Galaxy、Exynos 2600、AppFunctions、端侧诈骗检测；HBF 标准化 | 移动 SoC / Google |
| 02-26 | Android 17 Beta 2 NPU 访问声明；报道：Apple 接受 LPDDR5X 价格翻倍；TrendForce 4Q25 DRAM 营收 +29.4% | Google / 内存 |

## 1. 高通：S26 专供版、Hexagon-MLIR 开源与“内存决定出货”

### 本月概览：旗舰交付、编译栈开源与“内存荒”

2026-01-30 ~ 2026-02-26 这四周，高通没有发布新的 SoC 家族：新品集中在 1 月 CES 和 3 月初的 MWC，2nm 新旗舰要等 9 月骁龙峰会。这段时间的主线可以概括为三件事。第一是交付：2 月 25 日 Galaxy Unpacked 上，[骁龙 8 至尊版第五代 for Galaxy](https://www.qualcomm.com/news/releases/2026/02/qualcomm-unveils-the-snapdragon-8-elite-gen-5-for-galaxy--drivin) 随 Galaxy S26 Ultra 全球上市。三星官方给出 NPU +39%、CPU 最高 +19%、GPU +24% 的提升，“端侧智能体”第一次成为三星旗舰的核心卖点。第二是软件栈：高通开源了 Hexagon NPU 编译栈 [Hexagon-MLIR](https://www.qualcomm.com/developer/blog/2026/02/build-faster-on-hexagon-npu-tritor-pytorch-with-hexagon-mlir-open-source)，[AI Hub Workbench](https://workbench.aihub.qualcomm.com/docs/hub/release_notes.html) 和 [AI Hub Models](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.47.0) 则在多图权重共享、QAIRT 2.43 和 X2 Elite 性能数据上连续更新。第三是供给侧的坏消息：2 月 4 日的 [Q1 FY26 财报](https://www.qualcomm.com/news/releases/2026/02/qualcomm-announces-first-quarter-fiscal-2026-results) 营收创纪录，但高通明确表示，存储厂把产能转向 HBM 导致手机 DRAM 短缺，Q2 手机芯片收入指引降到约 60 亿美元。

本窗口与往周的关系：这几周的周报此前都没有硬件雷达条目，因此这里没有需要与往周合并的高通条目。1 月 CES 的 X2 Plus、IQ10 机器人等发布早于窗口，只作为背景。

### 旗舰手机：Galaxy S26 Ultra 把“端侧智能体”写进卖点

高通 2 月 25 日的新闻稿措辞克制，只说这是为 Galaxy S26 系列“专门定制”的平台，采用第 3 代 Oryon CPU、Adreno GPU 和 Hexagon NPU，全球版 S26 Ultra 全部使用，S26+ 和 S26 只在部分地区使用；三星规格表显示其余地区为 Exynos 2600。具体数字来自三星：[三星新闻稿](https://news.samsung.com/global/samsung-unveils-galaxy-s26-series-the-most-intuitive-galaxy-ai-phone-yet) 写明 CPU 最高 +19%、NPU +39%、GPU +24%，对比的是上一代 S25 Ultra 的 for Galaxy 版（官方口径）；[次日的回顾稿](https://news.samsung.com/global/galaxy-unpacked-2026-highlights-from-galaxy-unpacked-the-beginning-of-truly-agentic-ai) 称这是三星“联合开发的定制 AP”，并配了“迄今最大的均热板”。高通自己的[产品页](https://www.qualcomm.com/smartphones/products/8-series/snapdragon-8-elite-gen-5)对标准版给出的是 NPU +37%、CPU +20%、GPU +23%，最高频率 4.74 GHz，并注明还有 4.6 GHz 和 7 核版本。两组百分比的对比基线不同，不能相减得出“定制版多快 2%”这样的结论。媒体普遍把 4.74 GHz 归给 Galaxy 版，这属于 Geekbench 记录和爆料口径。

对端侧 AI 更有意义的是功能层面。高通新闻稿描述了 Now Nudge 这类“及时给出建议、在后台替用户执行动作”的体验，三星则把 Personal Data Engine 定位为端侧的个性化与情境引擎。三星同时说明 Now Brief 等功能仍需联网和三星账号，所以 S26 的 Galaxy AI 是端云混合，不是纯端侧。内存方面，S26 Ultra 只有 1TB 版是 16GB，其余为 12GB。按第三方规格库列出的约 84.8 GB/s 峰值带宽推算（非官方）：3B 稠密模型 INT4 的 decode 上限约 50 tok/s，7B INT4 约 22 tok/s。再扣掉系统和常驻应用占用的内存，12GB 机型更现实的常驻规模是 3–4B。第三方实测方面，[Notebookcheck](https://www.notebookcheck.org/Samsung-Galaxy-S26-Ultra-protagoniza-las-pruebas-practicas-de-CPU-y-GPU-antes-de-su-debut-oficial.1233129.0.html) 记录 S26 Ultra 的 Geekbench 6 单核 3648、多核 10898，认为在同芯片机型里属于中游。

高通在 2 月 4 日的[财报会](https://s204.q4cdn.com/645488518/files/doc_events/2026/Feb/04/Q1FY26-Earnings-Call-Transcript_2-5-26_Final.pdf)上预计，三星新一代高端家族中骁龙份额约 75%，与此前预期一致；同时把字节跳动基于骁龙 8 至尊版的手机称为“首款智能体 AI 手机”。把这两点和 S26 的宣传放在一起看，2026 年上半年手机端智能体已经进入量产旗舰，高通的叙事也从“NPU 有多少 TOPS”转向“能替用户在后台做事”。

### 软件栈：Hexagon-MLIR 开源，AI Hub 收敛到权重共享

本月对开发者最有价值的是 2 月 6 日发布的 Hexagon-MLIR 早期开发者预览版。它能把 Triton kernel 和 PyTorch 模型（经 Torch-MLIR）直接编译成 Hexagon NPU 可执行文件，已在 v73、v75、v79 三代 NPU 上测试，支持算子融合、按 TCM 分块、HVX 多线程、双缓冲、向量化和 HexKL 矩阵乘，代码在 [qualcomm/hexagon-mlir](https://github.com/qualcomm/hexagon-mlir)。2 月 23 日，25 位高通作者提交了配套论文 [arXiv:2602.19762](https://arxiv.org/abs/2602.19762)，提出把任意长的算子链融合成“mega-kernel”，让中间结果留在 TCM 里，以缓解算子库方案反复读写 DDR 的带宽瓶颈。论文给出的 kernel 级向量化加速为：GELU fp16 63.9 倍、RMSNorm fp16 46.5 倍、Flash Attention fp32 4.7 倍；多线程在 512K 元素时比单线程快 3.95 倍，但 16K 以下反而更慢。这些是论文口径的 kernel 数据，没有端到端 LLM 的 tok/s，也没写测试用的具体 SoC。博客也坦言，性能数据会随项目推进再公布。它的意义在于，高通第一次给社区提供一条不依赖 QNN 算子覆盖的 NPU 路径：新的注意力变体、量化 kernel、MoE 路由都可以先用 Triton 写出来跑在 Hexagon 上。不过论文也列出了明显短板：softmax、前缀和、TopK 这类无法用单个 `linalg.generic` 表达的算子还需要额外的控制流支持；1M 元素时 TCM 和 DMA 队列压力会让加速比回落；fp16 运算一旦被内部提升为 fp32，性能也会下降。也就是说，它现在更适合研究者做算子实验，还不能替代 QAIRT 承担量产部署。

AI Hub 这边是两次工程收敛。[Workbench](https://workbench.aihub.qualcomm.com/docs/hub/release_notes.html) 2 月 2 日新增 `submit_compile_and_link_jobs()`，把多个模型编译并链接成一个权重共享的 QNN context binary，正好对应端侧 LLM 的 prefill/decode 多图部署；同时 beta 支持 `.pt2` 输入（需 PyTorch 2.8.0）。2 月 17 日加入 QAIRT 2.43.1（默认仍为 2.42.0），ONNX Runtime 升级到 1.24.1，新增 SC8480XP Windows 设备，并移除编译到 QNN Model Library 的目标。与之配套，微软 [ONNX Runtime 1.24.1](https://github.com/microsoft/onnxruntime/releases/tag/v1.24.1) 的 QNN EP 升级到 QNN SDK 2.42，新增 RMSNorm、GatherND、STFT 等算子；2 月 19 日的 [1.24.2](https://github.com/microsoft/onnxruntime/releases/tag/v1.24.2) 又为 v81 及以上的 HTP 启用了 64 位 UDMA 模式。这些第三方运行时的跟进，让 Windows on Snapdragon 上走 ONNX 路线的开发者也能用上新版 QNN 的算子。模型库方面，[v0.46.1](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.46.1)（2 月 13 日）把全部模型改成带元数据的 zip 包发布到 Hugging Face，LLM 统一编译为 QAIRT 2.42 的 context binary，并新增 Dragonwing IQ-9075 EVK 的性能数据；[v0.47.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.47.0)（2 月 25 日）为所有适用模型补上骁龙 X2 Elite 的性能数据，新增 EdgeTAM、ACT（机器人模仿学习策略）、MeloTTS-EN 和 MaskRCNN，同时因精度验证暂时下架 Qwen2.5-1.5B-Instruct。看得出高通开始用扩展提示集做 LLM 的精度回归。

开发者生态的其他动态：2 月 9 日的[韩国端侧 AI 黑客松回顾](https://www.qualcomm.com/developer/blog/2026/02/on-device-ai-developers-korea)展示了在骁龙 X 系列 Copilot+ PC 上本地运行 Qwen2.5-7B-Instruct、Nomic 嵌入和 EasyOCR 的邮件代理与文件助手。这类 PC 端智能体样例说明，7B 级模型在 PC 内存条件下已经是开发者的默认选择。

### 财报：营收创纪录，但 HBM 挤占手机 DRAM

[Q1 FY26 财报](https://s204.q4cdn.com/645488518/files/doc_financials/2026/q1/FY2026-1st-Quarter-Earnings-Release.pdf)：营收 122.5 亿美元（同比 +5%），QCT 106.1 亿美元；手机 78.2 亿美元（+3%）和汽车 11.0 亿美元（+15%）都创纪录，IoT 16.9 亿美元（+9%）。转折出现在指引：Q2 营收 102–110 亿美元，QCT 88–94 亿美元，财报会上给出的手机收入约 60 亿美元。[官方演示稿](https://s204.q4cdn.com/645488518/files/doc_financials/2026/q1/FY2026-1st-Quarter-Earnings-Presentation_2-4-26_final_distributed.pdf)专门用一页解释“内存行业动态对指引的影响”：AI 数据中心对存储的需求造成手机 OEM 的内存供给和价格不确定，多家中国 OEM 削减了生产计划和渠道库存；内存短缺与涨价“很可能决定全年手机行业的规模”。安蒙在问答中说得更直接：Q2 的出货“100% 由内存可得性决定”，因为 HBM 被优先保障，消费电子可得的 DRAM 同比下降。有分析师在会上引用存储厂“只能满足 50%–70% 需求、短缺持续到 2028 年”的说法，并追问中国客户是否会导入长鑫存储（这是分析师口径，不是高通口径）。

这对端侧 AI 是一个容易被忽视的约束：端侧模型能否常驻，取决于 DRAM 容量和带宽，而不只是 NPU 算力。内存涨价会让 OEM 在中端机上更难配到 12–16GB，“端侧大模型下沉”的节奏可能因此放慢（推算）。同一场财报会还披露：40 多款个人 AI 设备在量产或开发中；高通与全球 9 家最大云公司中的 7 家合作；今年目标商用约 150 款骁龙 X PC；X2 Plus 的 Hexagon NPU 推理速度据称是竞品 NPU 的 5.7 倍、竞品 GPU 的 3.4 倍（官方口径）。数据中心方面，已完成 Alphawave 收购、收购 Ventana（RISC-V），AI250 采用新内存架构，预计 2027 年开始贡献收入。

### 产业与组织：印度基金、供应链换帅

2 月 18 日，高通在新德里 India AI Impact Summit 期间宣布[最高 1.5 亿美元的印度战略 AI 基金](https://www.qualcomm.com/news/releases/2026/02/qualcomm-commits-up-to--150-million-for-strategic-ai-venture-fun)，重点投资汽车、IoT、机器人和手机方向的 AI；高通自 2007 年起已在印度投资 40 多家公司。同期[媒体报道](https://www.businesstoday.in/amp/technology/news/story/india-ai-impact-summit-2026-hybrid-ai-deployment-model-is-way-to-power-indias-sovereign-ai-ambitions-says-qualcomms-sahil-arora-516260-2026-02-16)中，高通印度高管把“端侧加云”的混合 AI 描述为印度主权 AI 的落地路径；另有报道称本土模型公司 Sarvam 与高通、HMD 合作，把小模型优化到现有手机芯片上离线运行（媒体口径，未见高通官方稿）。2 月 26 日，高通任命英特尔代工服务前负责人 [Kevin O'Buckley](https://www.qualcomm.com/news/releases/2026/02/qualcomm-appoints-kevin-o-buckley-as-executive-vice-president--g) 为执行副总裁，统管制造工程、代工、供应链与采购，3 月 2 日生效。在内存和先进制程同时紧张的背景下，这次任命针对的是交付能力。2 月 24 日的 OnQ 文章《[Physical AI 与 6G](https://www.qualcomm.com/news/onq/2026/02/physical-ai-6g-robotics)》则以 IQ10 人形机器人、AMR 和巡检无人机组成的“持续学习机队”为例，描述端侧 AI 与 6G 协同的机器人路线，属于愿景阐述，没有新的硬件规格。

### 爆料：2nm 第六代旗舰可能按 LPDDR6 分档

2 月 11 日，[Notebookcheck 转述 Digital Chat Station 的爆料](https://www.notebookcheck.com/Xiaomi-18-erstmals-nicht-mit-bestem-2nm-Snapdragon-Chip-Leaker-mit-Details-zum-Snapdragon-8-Elite-Gen-6-Duo.1224191.0.html)：下一代旗舰分为 SM8950（标准版）和 SM8975（Pro 版），均采用台积电 2nm；只有 Pro 版支持 LPDDR6，并配完整 GPU 和缓存，价格“非常贵”，小米 18 标准版可能用不上 Pro。可信度为中等，高通没有确认。如果属实，同代旗舰的端侧 LLM 体验会第一次按内存标准分档。decode 速度基本由带宽决定，所以“Pro 机型 tok/s 明显更高”几乎是必然结果（推算）。这与财报中的内存荒是同一个问题的两面：内存正在取代 NPU TOPS，成为端侧 AI 的分档依据。

### 窗口外背景（1 月）

本窗口的很多动态都承接 1 月 CES：高通 1 月 5 日发布了面向商用 PC 的 [Snapdragon X2 Plus](https://www.qualcomm.com/news/releases/2026/01/empowering-professionals-and-aspiring-creators--snapdragon-x2-pl) 和[全套机器人技术与 Dragonwing IQ10](https://www.qualcomm.com/news/releases/2026/01/qualcomm-introduces-a-full-suite-of-robotics-technologies-power)，并宣布 [IE-IoT 产品线扩展完成](https://www.qualcomm.com/news/releases/2026/01/qualcomm-s-ie_iot-expansion-is-complete--edge-ai-unleashed-for-d)。本月 AI Hub Models 加入 X2 Elite 数据和 ACT 机器人策略，可以看作 CES 硬件的软件跟进。窗口结束后几天（3 月 2 日起的 MWC），高通发布了 Snapdragon Wear Elite 等可穿戴平台，这些留到 3 月统计。

### 小结与看点

总结这四周：硬件上，骁龙 8 至尊版第五代 for Galaxy 把约 40% 的 NPU 提升和“后台代办”式端侧智能体带进了年度出货量最大的安卓旗舰之一；软件上，Hexagon-MLIR 开源和 AI Hub 的权重共享 context binary，降低了新算子和多图 LLM 上 NPU 的门槛；产业上，HBM 挤占手机 DRAM 已被高通写进官方指引，加上 LPDDR6 可能只给 Pro 版的爆料，内存正在成为 2026 年端侧 AI 最硬的约束。接下来值得关注：Hexagon-MLIR 能否给出端到端 LLM 的数据；QAIRT 2.43 之后 AI Hub 的 LLM 指标何时从 2.37/2.42 更新；内存短缺是否迫使 OEM 在中端机上削减内存，进而影响端侧模型的下沉节奏。

## 2. Apple 与 Google：MLX 多机互联、AppFunctions 与 Android 17 的 NPU 声明

### 总览：Google 把智能体接进系统，Apple 在推迟与扩产之间

2026 年 1 月 30 日至 2 月 26 日这四周，Apple 与 Google 都没有发布新的旗舰芯片，**端侧 AI 的看点集中在系统软件和产业链**。往周（2026-01-02、01-09、01-16、01-23、01-30 五周）的硬件雷达在本方向没有收录条目，本节内容全部来自本次回填，1 月下旬的事件仅作背景。

**Google 一侧密集落地**。2 月 13 日发布 [Android 17 Beta 1](https://android-developers.googleblog.com/2026/02/the-first-beta-of-android-17.html)，18 日发布沿用 Tensor G4 的 [Pixel 10a](https://store.google.com/us/magazine/meet-google-pixel-10a?hl=en-US)。25 日三星 Unpacked 当天，Google 连发三篇：[“Intelligent OS”](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html)公布 AppFunctions 与 UI 自动化两条智能体接入路线；[Gemini 多步任务 beta](https://blog.google/innovation-and-ai/products/gemini-app/android-multi-step-tasks/)；Galaxy S26 内置[端侧 Gemini 诈骗检测](https://blog.google/products-and-platforms/platforms/android/samsung-unpacked-2026/)。26 日的 [Android 17 Beta 2](https://android-developers.googleblog.com/2026/02/the-second-beta-of-android-17.html) 要求直接访问 NPU 的 App 必须声明，同日 [AI Edge Gallery 1.0.10](https://github.com/google-ai-edge/gallery/releases/tag/1.0.10) 加入 270M 函数调用模型和应用内跑分。

**Apple 一侧以基础设施和爆料为主**。官方动作有三项：2 月 3 日 [Xcode 26.3](https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/) 通过 MCP 接入编程智能体；MLX 在 2 月 3 日和 6 日连发 [0.30.5](https://github.com/ml-explore/mlx/releases/tag/v0.30.5) 和 [0.30.6](https://github.com/ml-explore/mlx/releases/tag/v0.30.6)，多机互联带宽大幅提升；2 月 24 日宣布休斯敦 [AI 服务器提前出货](https://www.apple.com/newsroom/2026/02/apple-accelerates-us-manufacturing-with-mac-mini-production/)。媒体面则是 Gemini 版 Siri [推迟出 iOS 26.4](https://9to5mac.com/2026/02/11/apple-reportedly-pushing-back-gemini-powered-siri-features-beyond-ios-26-4/)、[三款 AI 可穿戴](https://9to5mac.com/2026/02/17/apple-accelerating-work-on-three-new-ai-wearables-per-report/)、[A20/M6 用 N2](https://www.macrumors.com/2026/02/03/apple-seemingly-avoiding-latest-chip-tech/) 和 [12GB LPDDR5X 价格翻倍](https://www.mactrast.com/2026/02/apple-reportedly-agrees-to-pay-double-for-samsung-memory-chips-while-it-works-to-keep-iphone-18-prices-flat/)。Apple ML Research 博客本月只有论文条目，没有 highlight 长文。

本月可以归纳为三个判断：

1. **手机智能体的接口开始标准化。** Android 的 AppFunctions 被官方类比为“端侧版 MCP”，Xcode 26.3 用 MCP 开放 IDE 能力。两家都在让智能体调用结构化的本地函数，而不是只靠读屏点按。
2. **NPU 和内存成为需要分配的资源。** Android 17 把 NPU 当作要声明、可被系统调度的共享资源；同月移动 DRAM 价格据报翻倍，Pixel 10a 维持 8GB。端侧 AI 的约束正从“有没有 NPU”转向“谁来用、内存够不够”。
3. **端云混合是现实，纯端侧智能体仍未出现。** Gemini 多步任务由 Gemini 3 系列模型完成规划，执行在手机上的虚拟窗口；Apple 新 Siri 卡在个人数据与 App 操作的可靠性上，同时在扩充自有 AI 服务器。

### 一、Android 的智能体接口：AppFunctions、UI 自动化与 NPU 声明（02-25 ~ 02-26）

Android 开发者博客 2 月 25 日的 [“The Intelligent OS”](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html)（作者为 Android 开发产品副总裁 Matthew McCullough）把智能体接入 App 分成两条路线：

| 路线 | 做法 | 运行位置 | 首发 |
|---|---|---|---|
| AppFunctions | App 用 Jetpack 库声明“自描述函数”，智能体按自然语言发现并调用 | 官方原话“an on-device solution”，函数本地执行 | Galaxy S26 已支持，OneUI 8.5+ 三星设备即将支持 |
| UI 自动化框架 | 开发者“zero code”，Gemini 在后台虚拟窗口直接操作 App | 执行在手机上；规划由 Gemini 3 系列模型承担（Unpacked 稿口径） | Galaxy S26、部分 Pixel 10 早期预览；美国、韩国；外卖、生鲜、网约车 |

第一个公开案例是三星相册：在 Galaxy S26 上让 Gemini“找我家猫的照片”，结果直接出现在 Gemini 中。日历、笔记、任务类 App 也已能在多家厂商设备上被 Gemini 自动化。官方把 AppFunctions 类比为云端 MCP 服务器的端侧版本。这意味着智能体调用 App 的方式会和服务端工具调用越来越接近，**手机 App 正在变成智能体的本地工具集**。

需要注意口径：Google 没有说明 Gemini 的理解与规划是否有端侧模型参与，[blog.google 的 Unpacked 稿](https://blog.google/products-and-platforms/platforms/android/samsung-unpacked-2026/)明确写的是“Gemini 3 series models are doing the heavy lifting”。所以这是“云端规划、端侧执行”的混合智能体。同一篇稿件里另有一项完全端侧的能力：Galaxy S26 的三星电话 App 集成 Google 诈骗检测，“using our on-device Gemini model”实时分析通话，“analysis happens entirely on your device”，音频不录不存不上传。一台手机上，长链路规划在云端，常驻、隐私敏感的推理在端侧，分工很清楚。

第二天的 [Android 17 Beta 2](https://android-developers.googleblog.com/2026/02/the-second-beta-of-android-17.html) 加入了一个容易被忽略但影响深远的变化：**面向 Android 17 的 App 若要直接访问 NPU，必须声明 `FEATURE_NEURAL_PROCESSING_UNIT`**，否则可能被阻止访问。范围包括 LiteRT NPU 委托、芯片厂商 SDK 和“已弃用”的 NNAPI。系统模型（Gemini Nano、诈骗检测）、智能体与第三方 App 同时争用 NPU 后，资源仲裁从芯片驱动层上移到了 OS 层。文章没有说明优先级怎么分配，也没有说明未声明的 App 是失败还是回退到 CPU/GPU，这是后续 Beta 需要跟踪的点。Beta 1（2 月 13 日）则主要是无锁 MessageQueue、分代 GC 等性能改动，没有 AI 相关条目；平台稳定版目标为 3 月。

同一天（2 月 26 日）的 [AI Edge Gallery 1.0.10](https://github.com/google-ai-edge/gallery/releases/tag/1.0.10) 补上了“动作层”：新增基于 [FunctionGemma](https://ai.google.dev/gemma/docs/releases) 270M 微调的 Mobile Actions 模型，把自然语言映射为手机操作；同时加入应用内 benchmark 页面，可以在真机上直接测模型速度。release note 没有附任何跑分结果。另外，[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM/releases) 在 1 月 30 日和 2 月 12 日先后打了 v0.9.0-alpha、alpha02 两个预发布标签，均无实质更新说明。LiteRT 正式进入生产栈的官方稿发于 1 月 28 日，在窗口之外，这里只作背景。

### 二、Pixel 10a 与 Tensor 路线：中端机退回上一代芯片（02-18 ~ 02-19）

2 月 18 日发布的 Pixel 10a 是本月 Google 唯一的新硬件。[官方规格页](https://store.google.com/us/product/pixel_10a_specs?hl=en-US)写明：Tensor G4 + Titan M2，128GB/256GB 两档都是 8GB RAM，Google AI 一栏列有 Gemini Nano。[9to5Google 上手稿](https://9to5google.com/2026/02/18/google-pixel-10a-announcement-hands-on/)给出售价 499/599 美元、3 月 5 日开售，并指出这是 **A 系列第一次没有用当代旗舰同一代芯片**，Google 给的理由是可负担性。

对端侧 AI 来说，8GB 是关键约束。Google 没有披露 Gemini Nano 在 10a 上的版本和速度。参考 5 月 Gemini Intelligence 设定的 12GB 门槛（见往月硬件雷达），10a 大概率拿不到最高级别的端侧能力（推算）。官方介绍把 Gemini Live、Nano Banana 等云端功能和 Gemini Nano 端侧功能放在一起宣传，读者需要自己区分哪些在本地跑。

Tensor 下一代只有零星爆料。2 月 19 日 [9to5Google](https://9to5google.com/2026/02/19/googles-tensor-g6-rumored-to-be-paired-with-new-titan-m3-security-coprocessor/) 援引 Mystic Leaks 称 Tensor G6 将搭配代号“Google Epic”的 Titan M3（固件“longjing”），工艺和 CPU/GPU/TPU 都未提及（爆料，low）。2 月 20 日，美国检方起诉三人涉嫌窃取 Pixel Tensor 相关商业机密，共 14 项重罪指控（[9to5Google 转述彭博](https://9to5google.com/2026/02/20/stealing-tensor-pixel-trade-secrets-ex-google-employees/)），被窃内容未公开。产业面，[Counterpoint 2 月初预测](https://9to5google.com/2026/02/02/google-pixel-expected-to-see-strongest-growth-in-2026-report-says/) 2026 年 Tensor 出货增长从略高于 13% 上调到接近 19%，而整体手机 SoC 出货将下降约 7%，原因是内存短缺和成本上涨。

### 三、Apple 的软件栈：MLX 多机互联与 Xcode 智能体（02-03 ~ 02-12）

MLX 本月最值得看的是 [PR #3094](https://github.com/ml-explore/mlx/pull/3094)（随 v0.30.6 于 2 月 6 日发布）。JACCL 是 MLX 基于 Thunderbolt RDMA 的分布式通信后端，这次更新在 macOS 26.3 及以上用大缓冲区修复了带宽，并新增 ring 拓扑，支持任意多台 Mac 串联。MLX 团队给出的 4 台 M3 Ultra 实测（2048 token 提示词，生成 128 token，batch=1）：

| 模型 | 阶段 | 1 台 | 4 台（更新前） | 4 台（更新后最好） |
|---|---|---|---|---|
| Devstral 2 123B 4-bit | prefill | 91.5 tok/s | 135 | 303（ring，+124%） |
| Devstral 2 123B 4-bit | decode | 9.0 tok/s | 24.5 | 26.2（mesh，+6.9%） |
| GLM 4.7 358B 6-bit | prefill | 265 tok/s | 309 | 719（ring，+133%） |
| GLM 4.7 358B 6-bit | decode | 16.9 tok/s | 27.4 | 27.7（mesh，+1.1%） |

prefill 是算力瓶颈，多机能接近线性扩展。decode 每个 token 都要跨机同步，被互联时延卡住，这次更新几乎没有帮助。用带宽估算单机 decode 上限（推算）：Devstral 2 是 123B 稠密模型，4-bit 每 token 读约 62GB，M3 Ultra 819GB/s（Apple 规格页），上限约 13 tok/s，实测 9.0 tok/s 约为上限的七成。PR 作者还提到，batch=8 时 MoE 在 4 台上的加速比从 1.6 倍提升到 2.6 倍。社区在 [issue #3162](https://github.com/ml-explore/mlx/issues/3162) 报告 macOS 26.3 的 RDMA 驱动每台设备约有 100 个内存注册区上限，可能限制扩展规模（未经 Apple 确认）。

另一条线索在手机端：[0.30.5](https://github.com/ml-explore/mlx/releases/tag/v0.30.5) 修复了 iPhone 上 NAX（GPU 神经加速器矩阵路径）的判定条件和溢出问题，[mlx-swift 0.30.6](https://github.com/ml-explore/mlx-swift/releases/tag/0.30.6)（2 月 10 日）专门修复 iPhone 16 Pro 上 NAX 被误检。这说明 MLX 正在把 M5 的 GPU 神经加速器优化同步到 A19 手机。配套的 mlx-lm [0.30.6](https://github.com/ml-explore/mlx-lm/releases/tag/v0.30.6)、[0.30.7](https://github.com/ml-explore/mlx-lm/releases/tag/v0.30.7) 跟进了 Kimi-K2.5、DeepSeek V3.2 等新模型。

[Xcode 26.3](https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/)（2 月 3 日 RC）原生支持 Claude Agent 和 Codex，并通过 MCP 开放 Xcode 能力：智能体能查文档、改项目设置、编译修复、截取 Previews 自检。模型在云端，编译和预览在本机。它与 AppFunctions 的思路一致，都是把本地能力暴露给智能体。

Apple ML Research 本月的[论文列表](https://machinelearning.apple.com/research)中，与端侧相关的有 2 月 17 日上架的 [Ferret-UI Lite](https://machinelearning.apple.com/research/ferret-ui)（3B 端侧 GUI 智能体）和 2 月 23 日的 [Learning to Evict from Key-Value Cache](https://machinelearning.apple.com/research/evict)。前者的 arXiv 首版早于本窗口，按规则只作背景，论文由 arXiv 方向收录。

### 四、Apple 的产业与爆料：Siri 推迟、AI 服务器、可穿戴与 2nm（02-03 ~ 02-26）

**Siri 推迟（爆料，medium）**。2 月 11 日彭博 Gurman 报道（[9to5Mac](https://9to5mac.com/2026/02/11/apple-reportedly-pushing-back-gemini-powered-siri-features-beyond-ios-26-4/)），Gemini 驱动的新 Siri 将从 iOS 26.4 拆分到 iOS 26.5（5 月）和 iOS 27（9 月）。最可能推迟的是“读取个人数据”和“语音控制 App 内操作”。[GSMArena](https://www.gsmarena.com/gurman_apples_new_siri_delayed_again_will_not_be_included_in_ios_264-news-71525.php) 转述的内测问题包括响应慢、复杂问题处理差，以及意外转交 ChatGPT 而不是用 Apple 自己的模型。推迟的恰好是记忆和工具调用这两项智能体能力，与 Google 同月推出多步任务 beta 形成对照。Apple 否认这是“推迟”。背景：1 月底 Apple 收购以色列“无声语音”初创公司 Q.ai（[媒体报道](https://www.privacyguides.org/news/2026/01/30/apple-acquires-q-ai-startup-for-silent-voice-input/)，金额约 16 亿美元，未经 Apple 披露），日期在窗口外。

**AI 服务器提前出货（官方）**。2 月 24 日的[新闻稿](https://www.apple.com/newsroom/2026/02/apple-accelerates-us-manufacturing-with-mac-mini-production/)中，库克称休斯敦的先进 AI 服务器“ahead of schedule”出货，并将扩产。Apple 预计 2026 年从台积电亚利桑那采购“well over 100 million”颗先进芯片。按 [2025 年 2 月官方稿](https://www.apple.com/newsroom/2025/02/apple-will-spend-more-than-500-billion-usd-in-the-us-over-the-next-four-years/)，休斯敦工厂用于生产 Apple Intelligence 服务器；[PCC](https://security.apple.com/blog/private-cloud-compute/) 使用 Apple 芯片。也就是说，在 Siri 部分依赖 Google 模型的同时，Apple 自有云这一半仍在加速建设。

**三款 AI 可穿戴（爆料，medium）**。2 月 17 日彭博报道（[9to5Mac](https://9to5mac.com/2026/02/17/apple-accelerating-work-on-three-new-ai-wearables-per-report/)）：一是无显示屏的眼镜，配两颗摄像头，其中一颗专用于“计算机视觉”；二是 AirTag 大小的吊坠，两颗摄像头、三个麦克风，“主要依赖 iPhone 处理”；三是带摄像头的 AirPods，最早 2026 年推出。芯片和功耗都没有披露。共同点是：可穿戴端负责常开感知，iPhone 负责算力。

**2nm 与内存（报道，medium）**。[MacRumors](https://www.macrumors.com/2026/02/03/apple-seemingly-avoiding-latest-chip-tech/) 援引台媒称 A20 和 M6 用台积电 N2，而不是同功耗快约 5% 的 N2P；高通、联发科预计用 N2P。[MacTrast](https://www.mactrast.com/2026/02/apple-reportedly-agrees-to-pay-double-for-samsung-memory-chips-while-it-works-to-keep-iphone-18-prices-flat/) 转述韩媒 Dealsite 称，Apple 接受三星 12GB LPDDR5X 从约 30 美元涨到约 70 美元，原因是 SK 海力士和美光把产能转向 HBM。云端 AI 抢走内存产能，直接推高端侧 AI 的硬件成本。

### 结语：本月的端侧 AI 主线是“接口与资源”，不是“算力”

这四周没有新的 TOPS 数字，也没有新的端侧模型规模数字。但三件事会影响后面半年：

- **智能体接口**：Android AppFunctions、UI 自动化和 Xcode MCP 让“本地函数 + 智能体”成为两大平台的正式接口。下一步要看 Android 17 正式版的开放范围，以及 Apple 在 WWDC 上的回应。
- **资源仲裁**：NPU 访问需要声明，DRAM 价格翻倍，中端机停在 8GB。端侧模型要在“共享 NPU + 有限内存”的条件下运行，低比特量化、MoE 稀疏和 KV cache 压缩的重要性继续上升。
- **端云分工**：Google 用 Gemini 3 在云端规划、在手机上执行；Apple 一边推迟 Siri，一边扩建 AI 服务器。2026 年 2 月，两家的手机智能体都还是混合架构。端侧真正独立承担的仍是诈骗检测这类常驻、隐私敏感、模型较小的任务。

存疑与待跟踪：Gemini 多步任务的规划是否有端侧模型参与（官方未说明）；Pixel 10a 上 Gemini Nano 的版本与能力（未披露）；Siri 推迟与可穿戴均为单一信源爆料；内存涨价数字来自单一韩国媒体。

## 3. 其他 SoC 与 PC：Galaxy S26 与 Exynos 2600、财报季里的内存账

### 本月要点：内存成了端侧 AI 的第一约束

1 月 30 日到 2 月 26 日这四周，除高通、苹果、谷歌以外的 SoC 与 PC 阵营几乎没有发布新芯片：联发科在 1 月 15 日发完天玑 9500s/8500 后，到 3 月 MWC 前没有新的天玑发布；英特尔 Panther Lake、AMD 锐龙 AI 400 都是 CES 的产物；华为麒麟、小米玄戒、紫光展锐、瑞芯微在窗口内也没有查到新芯片发布。这个月真正的主线在供应链：内存价格以创纪录的速度上涨，正在决定 2026 年手机和 PC 能配多大内存，也就决定了端侧能跑多大的模型。本月唯一的新 SoC 商用节点，是三星 2nm Exynos 2600 随 Galaxy S26 上市。

先看数字。TrendForce 2 月 2 日[把 1Q26 标准 DRAM 合约价预测从季涨 55–60% 上调到 90–95%](https://www.trendforce.com/presscenter/news/20260202-12911.html)，手机用 LPDDR4X、LPDDR5X 预计季涨约 90%，PC DRAM 季涨超过 100%，都是历史最大单季涨幅（第三方预测口径）。2 月 11 日的报告进一步[把 2026 年全球手机产量预测下调为同比 -10%，约 11.35 亿部](https://www.trendforce.com/presscenter/news/20260211-12922.html)，悲观情形 -15% 以上；主流 8GB+256GB 内存组合的合约价同比上涨近 200%，内存占整机 BOM 的比例从 10–15% 升到 30–40%。端侧 AI 过去两年的主要升级路径是“加内存、上更大的模型”，这条路在 2026 年上半年被成本卡住了。

### 移动 SoC：Exynos 2600 上市，12GB 成为旗舰上限

三星 2 月 25 日在旧金山发布 [Galaxy S26 系列](https://news.samsung.com/global/samsung-unveils-galaxy-s26-series-the-most-intuitive-galaxy-ai-phone-yet)。官方规格表写明，S26 和 S26+ 按设备与市场搭载 Snapdragon 8 Elite Gen 5 for Galaxy 或 Exynos 2600，S26 Ultra 只有 Snapdragon 版。也就是说，Exynos 2600 第一次进入量产旗舰，但仍没有拿回 Ultra。按[三星半导体产品页](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2600/)的官方口径，Exynos 2600 是业界首个 2nm GAA 手机 SoC，10 核 CPU 为 1 个 C1-Ultra 加 9 个 C1-Pro，支持 Armv9.3 与 SME2；NPU 的生成式 AI 性能比 Exynos 2500 高 113%（未给 TOPS），Xclipse 960 GPU 计算性能翻倍，并首次用 Heat Path Block 封装把热阻降低最高 16%。它还官方支持 ExecuTorch，PyTorch 模型可以直接部署到 Exynos 设备上，这对开发者生态是实质进展。

S26 全系起步 12GB 内存，只有 Ultra 的 1TB 版配 16GB，内存容量没有随 AI 功能继续增加。按 [TrendForce 转述 Chosun 的报道](https://www.trendforce.com/news/2026/02/23/news-samsung-reportedly-lifts-galaxy-s26-ultra-1tb-20-on-memory-costs-entry-model-up-5-8/)，韩国 S26 Ultra 1TB 版较上代涨价约 20%，256GB 版涨 5.8%（媒体口径）。软件侧，三星把 Bixby 重做为“对话式设备 Agent”，并在系统层集成 Gemini 与 Perplexity，可在后台完成跨应用多步任务；不过发布稿没有区分哪些 Agent 能力在本地运行。按推算，12GB 内存扣除系统和常驻应用后，留给端侧模型的空间约 3–4GB，对应 INT4 量化的 3–7B 级稠密模型；三星没有披露 LPDDR 带宽，若按 60–77GB/s 的假设估算，7B INT4 的 decode 理论上限约 17–22 tok/s。2026 年旗舰端侧模型大概率停留在这个量级，Agent 能力更多依赖端云混合。

联发科没有新芯片，但 2 月 4 日的 [4Q25 法说会逐字稿](https://www.mediatek.com/hubfs/MediaTek%20Assets/Pdfs/Quarterly%20Earnings%20Release/2025/Quarterly%20Earnings%20Release-2025Q4/%E8%AA%AA%E6%98%8E%E6%9C%83%E9%80%90%E5%AD%97%E7%A8%BF.pdf)给出了几个硬数字：2025 年手机业务首次超过 100 亿美元，其中旗舰 SoC 贡献 30 亿美元；4Q25 手机营收季增 18%，靠天玑 9500 与 8500 放量；公司已完成台积电 2nm 流片。CEO 蔡力行同时表示，内存和 BOM 成本上涨会压低 2026 年手机需求，1Q26 手机营收将明显季减。他在问答中判断 Agentic AI 会融入手机，手机本身会提供足够的生成式与 Agent 能力。联发科的增长重心正在转向数据中心 ASIC，公司“有信心”2026 年这部分营收超过 10 亿美元。2 月中旬蔡力行在 [ISSCC 2026 发表主题演讲](https://www.mediatek.com/tek-talk-blogs/mediatek-ceo-rick-tsai-presents-keynote-speech-at-isscc-2026)，[据 TrendForce 转述](https://www.trendforce.com/news/2026/02/25/news-mediatek-ceo-flags-memory-as-one-of-xpu-bottlenecks-now-making-up-50-of-costs/)，他指出内存已占 XPU 物料成本约 50%，推理会带动更多高密度 DDR 使用，存内计算与近存计算是值得探索的方向。端侧 SoC 厂商的 CEO 也把内存列为首要瓶颈，这和手机端的涨价是同一件事的两面。

国产 SoC 方面，窗口内没有查到麒麟、玄戒、展锐、瑞芯微的新芯片。小米释放了方向性信号：[TrendForce 转述南华早报](https://www.trendforce.com/news/2026/02/25/news-xiaomi-doubles-down-on-chips-trademark-filing-reportedly-signals-potential-memory-entry/)称，雷军表示今年要把自研芯片、自研 OS 和自研大模型整合进同一设备，并在未来五年投入 2000 亿元研发核心技术（媒体转述）。同期，中小品牌受到的冲击已经很明显，[魅族被报道将于 3 月退出手机业务](https://www.trendforce.com/news/2026/02/26/news-meizu-reportedly-eyes-march-smartphone-exit-after-scrapping-launch-amid-memory-costs-surge/)，其高管此前承认内存涨价导致新机取消（媒体转述）。

### PC 与 IP：财报很好，新品真空，软件栈在补课

AMD 2 月 3 日[公布 4Q25 财报](https://ir.amd.com/news-events/press-releases/detail/1276/amd-reports-fourth-quarter-and-full-year-2025-financial-results)，客户端营收创纪录 31 亿美元，同比增长 34%，全年 106 亿美元、增长 51%，说明锐龙在 AI PC 换机周期中继续拿份额。财报回顾的 CES 产品线中，锐龙 AI Max+ 与锐龙 AI Halo 开发者平台面向本地大模型开发。1 月 26 日发布的 Ryzen AI Software 1.7（窗口前，背景）已把 NPU 上下文扩到 16K，并预览了 GPT-OSS-20B 与 Gemma-3-4B 的 NPU 版本。

英伟达 2 月 25 日的 [FY26Q4 财报](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000019/q4fy26pr.htm)中，“游戏与 AI PC”营收 37 亿美元，同比 +47%、环比 -13%；专业可视化同比 +159%，新发布的 RTX PRO 5000 72GB 明确面向“更大模型与 Agent 工作流”，DGX Spark 扩大全球供货。官方称 RTX AI 让主流 AI PC 框架的 LLM 推理最高提速 35%。另一面是一条低可信度爆料：[TrendForce 转述 The Information](https://www.trendforce.com/news/2026/02/06/news-nvidia-reportedly-plans-no-new-gaming-gpu-in-2026-amid-memory-tightness-first-time-in-30-years/) 称英伟达 2026 年可能不推新游戏 GPU，好把显存配额让给 AI 加速器（英伟达回应称继续出货全部 GeForce 产品）。如果属实，桌面端侧推理在 2026 年会更依赖 DGX Spark、锐龙 AI Max+ 这类统一内存机器和 Mac。

英特尔本月最值得看的是软件。2 月 23 日的 [OpenVINO 2026.0](https://github.com/openvinotoolkit/openvino/releases/tag/2026.0.0) 让 GenAI 在 NPU 上支持投机解码，新增 MiniCPM-o-2.6、Qwen2.5-1.5B-Instruct 等 NPU 模型。NNCF 增加了面向 MoE 3D MatMul 的 INT4 数据感知压缩；预览功能里，NPU 编译器直接随插件发布，可以预编译或在设备端编译，不再等 OEM 驱动更新。Panther Lake 的 NPU 硬件在 CES 已经发布，这一版补的是“NPU 能不能真正跑起本地小模型 Agent”的软件短板。不过官方列出的 NPU 端 LLM 仍只有 0.5–1.5B 级，GPT-OSS-20B 走的是 CPU/GPU。

Arm 2 月 4 日的 [FY26Q3 财报](https://newsroom.arm.com/news/arm-q3-fye26-results)显示营收 12.42 亿美元，同比 +26%，版税 7.37 亿美元创纪录。本季新签两份面向边缘 AI 平板和手机的 CSS 授权，CSS 授权累计 21 份、覆盖 12 家公司，前四大 Android 手机厂商都在出货 CSS 设备。CPU 子系统在走向标准化，手机 SoC 的差异化正在转移到 NPU、内存子系统和软件栈。低功耗一端，Arm 2 月 2 日把 [Ethos-U85 NPU 纳入 Flexible Access](https://newsroom.arm.com/blog/arm-flexible-access-broadens-scope-to-help-companies-build-silicon-faster)，官方口径是性能为前代 4 倍、支持 Transformer，配合 Armv9 边缘 AI 平台可在端侧运行超过 10 亿参数的模型；年费统一为 8.5 万美元、不限流片次数，做常开 AI 芯片的门槛进一步降低。车端，[Tensor 与 Arm 合作的个人 Robocar](https://newsroom.arm.com/news/arm-and-tensor-partnership) 每台集成 433 个 Arm 核，其中 Cortex-X 明确用于“Agent 化座舱”，是物理 AI 端侧化的一个极端样本。

### 代工与内存：数据中心的需求在挤占端侧

台积电 2 月 10 日[董事会核准约 449.62 亿美元资本预算](https://pr.tsmc.com/english/news/3287)，首项用途是先进制程产能；同日公布的 [1 月营收](https://pr.tsmc.com/english/news/3284)为 4012.6 亿新台币，年增 36.8%。[据 TrendForce 转述台媒](https://www.trendforce.com/news/2026/02/02/news-tsmc-2nm-reportedly-tight-amid-mobile-hpc-demand-nvidia-may-be-first-to-adopt-1-6nm-in-2028/)，2nm 产能已被订满，2026 年 2nm 客户主要是苹果与高通，苹果拿到首批产能的一半以上（媒体转述）。今年下半年旗舰手机 SoC 的工艺升级因此会集中在少数头部厂商。

内存侧，三星 2 月 12 日[宣布 HBM4 量产出货](https://news.samsung.com/global/samsung-ships-industry-first-commercial-hbm4)，称为业界首家：引脚速率 11.7Gbps、可上探 13Gbps，单堆栈带宽 3.3TB/s，采用 1c DRAM 加 4nm base die，并预计 2026 年 HBM 销售额是 2025 年的 3 倍以上。TrendForce 次日[预计三家原厂都在 2Q26 完成英伟达 HBM4 验证](https://www.trendforce.com/presscenter/news/20260213-12929.html)。2 月 26 日的统计显示 [4Q25 DRAM 产业营收 535.8 亿美元，季增 29.4%](https://www.trendforce.com/presscenter/news/20260226-12937.html)，三星以 36% 份额重回第一。TrendForce 还预测 [2026 年内存产值 5516 亿美元，超过晶圆代工（2187 亿美元）的两倍](https://www.trendforce.com/presscenter/news/20260209-12917.html)，这一轮周期由价格不敏感的 CSP 主导。对端侧来说，这意味着手机和 PC 在 DRAM 配额上排在 CSP 后面，LPDDR5X 还要和服务器一起抢。

### 小结与观察

这个月的硬件信号可以归结为三点。第一，端侧 AI 的约束从“NPU 算力够不够”转向“内存能不能配得起”。LPDDR 一个季度涨约 90%，S26 停在 12GB，TrendForce 下调手机产量，联发科和 AMD 都在财报里提示内存成本。2026 年上半年端侧模型规模大概率不会跳升，主战场在 3–8B 级量化模型和更高效的推理软件。第二，软件栈正在补位：OpenVINO 的 NPU 投机解码与免驱动编译、ExecuTorch 进入 Exynos、Ryzen AI 1.7 的 NPU 长上下文，都是在不加内存的前提下挤出更多端侧能力。第三，系统级 Agent 形态开始落到量产设备上，例如三星的设备 Agent、Tensor 的 Agent 化座舱，以及小米“芯片 + OS + 大模型合一”的表态；但目前公开材料都没有说明本地与云端的分工比例，需要后续实测验证。

存疑点：Exynos 2600 的 NPU TOPS、LPDDR 类型与带宽，三星均未披露；英伟达停推游戏 GPU 属爆料；小米存储商标与 2nm 产能分配均来自媒体转述。下月需要跟踪 MWC 2026（3 月 2–5 日）上联发科、AMD 的新品，以及 1Q26 中国手机品牌 LPDDR 合约价的最终谈判结果。

## 4. 低功耗、存内计算与内存：LPDDR6、UFS 5.0 与 HBF

### 总览：2 月的主角是内存，而不是新芯片

本月窗口（01-30~02-26）里，低功耗、存内计算与内存方向没有出现旗舰级新芯片。Embedded World（3 月 10~12 日）和 MWC（3 月 2 日起）都在窗口之后，MCU 和可穿戴厂商把新品留到了 3 月。往周（01-02~01-30）的硬件雷达在这一方向没有已收条目，本节以本月新收的 12 条为主，窗口外的材料只作背景并单独标注。

本月可以归纳为四条主线：

1. **内存成为端侧 AI 的硬约束，而且越来越贵**：TrendForce 2 月 2 日把一季度 LPDDR4X/LPDDR5X 合约价预测上调到环比约 +90%；同月 ISSCC 上 SK 海力士和三星把 LPDDR6 推到 14.4/12.8Gbps；铠侠送样 UFS 5.0；闪迪与 SK 海力士启动 HBF 标准化。
2. **NPU 正在变成 MCU 和连接芯片的标配**：ST 把 Neural-ART 放进车规 MCU，Ceva 一年签 10 份 NPU 授权，TI 以 75 亿美元收购 Silicon Labs。
3. **常开 AI 走向“亚毫瓦感知 + 按需唤醒”的两级架构**：索喜与 Innatera 的雷达加神经形态方案是典型例子。
4. **边缘加速器进入资本兑现期**：Axelera 融资超 2.5 亿美元，爱芯元智港股上市；NXP 透露数百 TOPS 级 NPU 在研。

### 一、内存：带宽在涨，价格涨得更快

**价格。** [TrendForce 2 月 2 日的预测](https://www.trendforce.com/presscenter/news/20260202-12911.html)把一季度常规 DRAM 合约价涨幅从 55~60% 上调到 90~95%，NAND 从 33~38% 上调到 55~60%。手机用 LPDDR4X 和 LPDDR5X 预计都涨约 90%，是历史最大单季涨幅（第三方预测口径）。原因是 AI 数据中心抢产能，原厂还把部分 NAND 产线转去做 DRAM。TrendForce 6 月回看称一季度实际涨了约 93~98%（窗口外，供参照）。这一点已经传导到芯片厂：[恒玄科技 2025 年业绩快报](https://www.cls.cn/detail/2295089)显示四季度归母净利润同比减少近五成，公司把原因之一归于存储涨价。对端侧大模型来说，内存成本单季近乎翻倍，中端机型更可能压缩 RAM，常驻模型的规模会被直接限制。

**带宽。** ISSCC 2026（2 月 15~19 日，旧金山）上两家 DRAM 原厂都发表了 16Gb LPDDR6 论文（[TweakTown 会前预告](https://www.tweaktown.com/news/110149/sk-hynix-shows-off-16gb-lpddr6-at-14-4gbps-while-samsung-sends-lpddr6x-samples-to-qualcomm/index.html)；细节见[36 氪转载的论文解读](https://www.36kr.com/p/3856607395959810)）：

| 项目 | SK 海力士 | 三星 |
|---|---|---|
| 工艺 | 1c（第六代 10nm 级） | 10nm 级（节点未说明），面积 44.5mm² |
| 速率/电压 | 14.4Gbps @1.025V | 12.8Gbps @0.97V（JEDEC 最低电压点） |
| 能效 | 较 LPDDR5 提升超 20% | 较 LPDDR5X 每比特能耗 -21%，读功耗 -27% |
| 带宽 | 单通道实测峰值 38.4GB/s | 较 LPDDR5X +33.3% |

两家的取向不同：海力士冲 JEDEC 上限，另设节能模式；三星把最高速率放在最低电压点，主攻待机和读写电流。两家的能效基准不一样，不能直接比较。用“带宽 ÷ 每 token 读取字节数”推算：假设手机配 4 个 x24 通道（约 154GB/s），3B INT4 模型的 decode 上限约 100tok/s，8B INT4 约 38tok/s；LPDDR5X-10667 64-bit（约 85GB/s）下分别约 57 和 21tok/s（推算，整机通道数尚无产品披露）。此外 The Bell 报道三星已向高通提供 LPDDR6X 早期样品，计划 2027 年下半年商用（爆料）。

**闪存。** [铠侠 2 月 23 日宣布送样 UFS 5.0](https://americas.kioxia.com/en-us/business/news/2026/ssd-20260223-1.html)：M-PHY 6.0 单通道理论 46.6Gb/s，双通道有效读写约 10.8GB/s，512GB 样品 2 月 24 日出货，1TB 样品 3 月起。官方直接把卖点写成“带端侧 AI 功能的高端手机”。按 10.8GB/s 推算，载入 4GB 的 8B INT4 模型约需 0.4 秒，但流式读取权重仍比 LPDDR5X 慢一个数量级，只适合低频访问的专家或权重。

**HBF。** [闪迪与 SK 海力士 2 月 25 日启动 HBF 标准化](https://www.sandisk.com/company/newsroom/press-releases/2026/2026-02-25-sandisk-and-sk-hynix-begin-global-standardization-of-next-generation-memory-solution-high-bandwidth-flash-hbf)，在 OCP 下成立工作组。新闻稿没有给规格；[IEEE Spectrum 7 月报道](https://spectrum.ieee.org/high-bandwidth-flash)的第一代口径为每堆栈 16 颗 NAND、512GB、读带宽 1.6TB/s（窗口外）。HBF 面向数据中心，但它和 UFS 5.0 讲的是同一件事：推理权重以读为主，可以下沉到闪存层，DRAM 只放热数据。

### 二、MCU 与 NPU IP：NPU 成为标配

- **ST Stellar P3E（2 月 10 日）**：[首款带 NPU 的车规 MCU](https://newsroom.st.com/media-center/press-item.html/p4749.html)。6 个 500MHz Cortex-R52+，Neural-ART NPU 与 STM32N6 同源，但针对时序数据做了调整；19.5MB 相变存储器 xMemory 可存双镜像 OTA。官方称推理能效最高为 MCU 内核的 30 倍，[ST 博客](https://blog.st.com/stellar-p3e/)口径为推理性能提升 20~30 倍，2026Q4 量产。TOPS 和功耗均未披露。
- **Ceva（2 月 17 日）**：[2025 年签 10 份 NeuPro NPU 授权](https://www.ceva-ip.com/press/ceva-highlights-breakthrough-year-for-ai-licensing-and-physical-ai-adoption-in-2025/)，AI 占授权收入超 20%，其中有一家头部 PC OEM，以及 Microchip 的全系列授权；六家客户预计 2026 年底前回片。NPU 正以 IP 形式进入蓝牙、Wi-Fi、MCU 等大出货芯片。
- **TI 收购 Silicon Labs（2 月 4 日）**：[每股 231 美元、企业价值约 75 亿美元](https://news.silabs.com/2026-02-04-Texas-Instruments-to-acquire-Silicon-Labs)，预计 2027 年上半年交割。新闻稿只谈无线连接和自有晶圆厂，没有提 AI。但 TI 在 3 月 10 日（窗口外）发布了带 TinyEngine NPU 的 MCU，两条线未来合并的可能性很大。
- **背景（窗口外）**：Nordic 带 Axon NPU 的 nRF54LM20B 在 1 月发布、3 月宣布供货；Ambiq Atomiq（Ethos-U85）1 月公布；高通 Snapdragon Wear Elite 在 3 月 MWC 发布，带独立的常开 eNPU。这些说明 2 月的空档只是因为厂商把新品集中留到了展会季。

### 三、常开感知：亚毫瓦做第一级唤醒

[索喜与 Innatera 2 月 23 日的联合方案](https://www.innatera.com/newsroom/socionext-and-innatera-introduce-integrated-60-ghz-fmcw-radar-and-neuromorphic-edge-ai-for-human-presence-detection/)用 60GHz FMCW 雷达加脉冲神经处理器做人体存在检测。官方称准确率超过 99%，可以识别静止的人，功耗低于 1mW，让摄像头和射频模块在确认有人前保持休眠，续航提升 3~6 倍。测试集、误报率以及亚毫瓦是否包含雷达前端都没有公布，需要等 3 月展会的演示。

眼镜方向本月没有新主控发布。[恒玄业绩快报](https://www.cls.cn/detail/2295089)显示营收约 35.25 亿元、归母净利润约 5.88 亿元，BES2800 系列已用于智能眼镜；媒体引述的公开资料称其旗舰芯片独家供应 Meta Ray-Ban。这说明主流 AI 眼镜仍以毫瓦级可穿戴 SoC 做主控，大模型推理放在手机或云端。

### 四、边缘加速器：资本兑现与路线上移

- **Axelera AI（2 月 24 日）**：[融资超 2.5 亿美元](https://bits-chips.com/article/axelera-ai-raises-over-250m-on-global-commercial-growth/)（路透报道为 2.5 亿美元），累计超 4.5 亿美元，已向第 500 家客户出货；第二代 Europa 的 INT8 算力为 629TOPS，PCIe 卡计划上半年出货。官方未披露内存带宽，无法推算 LLM decode 上限。
- **爱芯元智（2 月 10 日）**：[港交所上市](https://www.cls.cn/detail/2286129)，发行价 28.2 港元，净筹约 28 亿港元，首日市值约 165.75 亿港元。截至 2025 年 9 月累计 SoC 交付超 1.65 亿颗，但边缘推理专用的 8850 系列 2024 年出货仅 10 万颗量级，经调整净亏损仍在扩大。
- **NXP（2 月 12 日东京媒体会）**：据 [MONOist 报道](https://monoist.itmedia.co.jp/mn/articles/2602/16/news056.html)，Kinara Ara-2 约 40TOPS@6W，现场在 Ara-2 上运行 8B VLM（Llama3-LLaVA-NeXT-8B）做决策，再由 Qwen2.5-Coder-1.5B 生成控制代码。NXP 还透露以 Kinara 技术开发目标数百 TOPS 的 eIQ Neutron GT NPU（在研，无时间表）。按 8B INT4 每 token 约读 4GB 推算，没有足够带宽的话 decode 只有个位数到十余 tok/s（推算，Ara-2 的内存带宽本报道未披露）。
- **未见窗口内一手动态**：Hailo、DEEPX（DX-M2 时间表在 1 月 CES 与 4 月报道之间说法不一）、EnCharge、SiMa.ai 在窗口内都没有可核实的新品或融资发布。

### 五、存内计算：学术热、产业静

ISSCC 2026 的存内计算专场和面向端侧 LLM 的加速器论文，由顶会方向另行梳理。从本方向看，宏级数字仍在刷新，例如 [OpenAlex 收录的 16nm 1Mb 全数字 SRAM 存算宏](https://api.openalex.org/works/doi:10.1109%2FISSCC49663.2026.11409250)（台湾清华大学等，444.21TOPS/W，混合 SNN-CNN，论文口径）。但宏级 TOPS/W 和系统级能效差几个数量级，不能拿来和产品比较。

产业侧，国产存算公司本月几乎没有新动作：知存、后摩、苹芯、九天睿芯在窗口内没有可核实的新品发布。微纳核芯 1 月完成兆易创新参与的 B2 轮战略融资，用于 3D 存算一体 LPU（具体日期未核实，未收为条目）。存算一体在端侧落地，目前仍主要靠炬芯这类把 SRAM-CIM NPU 做进音频 SoC 的厂商，而非独立存算芯片。

### 结语：端侧 AI 的瓶颈从算力移到了内存

把本月 12 条放在一起看：NPU 的算力在 MCU、IP 和边缘卡上都在快速普及，真正卡住端侧大模型的是内存。带宽靠 LPDDR6 提升 30%~50%，容量却被涨价压住；闪存（UFS 5.0、HBF）因此被重新定位为权重层。由此看三个后续观察点：

1. **3 月展会季**：TI、Nordic、Ambiq、高通可穿戴平台的 NPU MCU 要用 µJ/inference 和实际模型说话，而不只是 TOPS。
2. **手机内存配置**：二季度如果移动 DRAM 继续大涨，12GB 机型会成为端侧模型规模的现实上限，闪存卸载和 2~4bit 量化的需求会更迫切。
3. **两级常开架构**：亚毫瓦感知芯片加上按需唤醒的 NPU/大模型，是电池设备跑智能体的可行路径。Innatera 这类方案能否在展会实测中站住，决定它能否从演示走向量产。

## 5. 顶会论文：ISSCC 2026 把端侧 LLM 芯片带进 μJ/token

**判断：** 2 月（1/30–2/26）的顶会论文集中在两个时间点。月初是悉尼的 [HPCA 2026](https://conf.researchr.org/home/hpca-2026)，与 CGO、PPoPP 同址（1/31–2/4，正会 2/2–2/4）。月中是旧金山的 [ISSCC 2026](https://submissions.mirasmart.com/ISSCC2026/PDF/ISSCC2026AdvanceProgram.pdf)（2/15–2/19），月底还有 [FPGA 2026](https://www.isfpga.org/program/)（2/22–2/24）。本月最重要的信号来自 ISSCC：**端侧 LLM 芯片的比较单位已经从 TOPS/W 换成了 μJ/token 和 token/s**，第 31 场 AI 加速器专场 9 篇论文里有 8 篇以 LLM、VLM、状态空间语言模型或生成模型为对象。同时，LPDDR6 颗粒和 PHY 集中亮相，FPGA 2026 出现了用 150 美元级板卡跑 30B MoE 模型的工作。三条线指向同一个结论：端侧大模型的瓶颈是内存带宽和每 token 能耗，2026 年的芯片设计都在围绕这两点做文章。本期共收 23 条，往周（1/2–1/30）硬件雷达没有顶会条目，本节为窗口内首次汇总。

### 会期核对

| 会议 | 2026 会期 | 与端侧相关的看点 |
|---|---|---|
| HPCA / CGO / PPoPP | 1/31–2/4，悉尼（正会 2/2–2/4） | 流式视频 LLM、3DGS 上 NPU、单卡游戏 + LLM、端侧编译器内存优化 |
| ISSCC | 2/15–2/19，旧金山（论文 2/16–2/18） | LLM/VLM 芯片、LPDDR6、MCU NPU、常开视觉 |
| FPGA | 2/22–2/24，Seaside（论文 2/23–2/24） | 低成本 FPGA 跑 30B MoE、三值 LLM |

ASPLOS（3/22–26）、MLSys（5 月）、ISCA 与 VLSI（6 月）都不在窗口内。日期一律按论文宣讲场次所在日标注：ISSCC 按高级程序（Advance Program）的场次时间，HPCA/CGO 按 researchr 日程。

### 一、ISSCC：端侧 LLM 芯片按 μJ/token 比较

第 31 场（2/18）是本月端侧 LLM 硬件最密集的一场，各篇的思路可以分成三类。

**个性化与学习上片。** KAIST 的 [SoulMate](https://doi.org/10.1109/isscc49663.2026.11409048) 在 28nm 上同时做 RAG 和 LoRA 微调，论文口径功耗 9.8–180.5 mW，推理 26.3 μJ/token、微调 56.8 μJ/token，被选为 Highlight Paper。KAIST 3 月的新闻稿补充了 216.4 ms 的响应时间，并称计划 2027 年前后商用，但没有公开模型规模。同样把 LoRA 放上芯片的还有西北大学的[智能眼镜神经接口 SoC](https://doi.org/10.1109/isscc49663.2026.11409094)，它用 LoRA 把可训练参数减少 54–77%。这两篇说明，“在设备上越用越懂用户”已经有了硅片级实现。

**近存与投机解码。** 港科大的 [ReRAM-on-logic 加速器](https://doi.org/10.1109/isscc49663.2026.11409211)把 4 片 ReRAM（8 MB、25.6 GB/s）堆叠在 55nm 逻辑晶粒上，配合并行投机解码，吞吐 14.08–135.69 token/s。arXiv 全文给出的端到端数字更有参考价值：LLaMA2-7B 在 4 芯片系统加 LPDDR3 外存的条件下解码 17.82 token/s、123.41 mJ/token。清华的 [28nm 投机解码处理器](https://doi.org/10.1109/isscc49663.2026.11408953)标称 105–685 μs/token、加速 10.29 倍。按此折算超过 1,000 token/s，远高于同场其他芯片，测试条件尚不清楚，本期标为存疑。KAIST 的 [SMoLPU](https://doi.org/10.1109/isscc49663.2026.11409285)（2/17）把 MoE 专家调度和投机解码结合，做到 122.1 μJ/token。

**低比特与冗余削减。** 东南大学的 [51.6 μJ/token 加速器](https://doi.org/10.1109/isscc49663.2026.11409212)和 KAIST 的 Revolver 都在处理旋转量化的硬件开销：前者把片上旋转功耗降低 62.3%，每 token 能耗比 SOTA 低 32.6%。KAIST 的 [Tri-Oracle](https://doi.org/10.1109/isscc49663.2026.11408987) 面向 VLM，合并 68% 的冗余视觉 token、跳过流式注意力头，外存访问减少 57%，能耗 17.78 μJ/token。

需要说明的是，这些 μJ/token 数字的模型、精度和是否计入外存访问各不相同，大多数摘要也没有给出模型规模，**不能直接横向排名**。从港科大的全文可以看到，一旦计入外存访问，7B 模型的每 token 能耗就升到百毫焦量级。

### 二、产业论文：从 MCU 到桌面

ISSCC 第 17 场“Highlighted Chip Releases for AI”（2/17）只有 4 篇论文，覆盖了从 MCU 到桌面的跨度。[意法 STM32N6](https://doi.org/10.1109/isscc49663.2026.11409013) 首次以论文公开 Neural-ART NPU 的 16nm FinFET 实现，产品资料口径为 600 GOPS、3 TOPS/W。[Mobilint](https://doi.org/10.1109/isscc49663.2026.11409083) 用同一套 NPU 架构做了本地服务器芯片 ARIES（公司口径 80 TOPS）和端侧 SoC REGULUS（10 TOPS、<3 W），并现场演示了多模态模型。[NVIDIA GB10](https://doi.org/10.1109/isscc49663.2026.11409351) 给出了 DGX Spark 双晶粒的论文版本：3nm、20 核 Arm v9.2、Blackwell iGPU、FP4 1 PFLOPS。按媒体口径的 273 GB/s 推算，70B 稠密 4bit 模型的解码上限只有约 7.8 token/s，再次说明容量和带宽是两回事。微软 MAIA 是数据中心芯片，不在本栏范围。

常开感知方面，NVIDIA Research 的 [ALPhA-Vision](https://doi.org/10.1109/isscc49663.2026.11409322) 在 4.6 mW 下以 60 fps 做人脸检测，延迟 787 μs，全程不访问外部内存。南科大的[全模拟视觉 SoC](https://doi.org/10.1109/isscc49663.2026.11409209)（2/16）去掉了传感器到推理之间的模数转换，系统能效 346 TOPS/W（MAC 阵列口径为 8,791 TOPS/W，引用时要区分）。联发科在 2/16 的处理器专场发表了 3nm、0.338 mm² 的扩散模型加速器 [MADiC](https://doi.org/10.1109/isscc49663.2026.11409294)，能效 17.4 TOPS/W，面向端侧生成式修图。同日，联发科 CEO 蔡力行做了大会开场主题演讲。

### 三、内存：LPDDR6 颗粒与 PHY 同时亮相，近存给出另一条路

2/17 的第 15 场（存储）有两篇 LPDDR6。[SK 海力士](https://doi.org/10.1109/isscc49663.2026.11409121)的 1c nm 16Gb 颗粒在 1.025 V 下达到 14.4 Gb/s/pin，功耗效率比 LPDDR5 高 20% 以上，并新增带电源门控的效率模式。TrendForce 引述称该颗粒 2026 年下半年出货。[三星](https://doi.org/10.1109/isscc49663.2026.11409018)的 12.8 Gb/s 颗粒比 LPDDR5X 带宽高 33.3%、能效高 21.0%，2/18 又发表了 [2nm 全数字 LPDDR6 PHY](https://doi.org/10.1109/isscc49663.2026.11409321)（14.4 Gb/s/pin）。同一场还有 MediaTek 的 2nm、350 mV 单电源轨 SRAM，面向 CPU/GPU/NPU 缓存。对端侧 LLM 来说，解码 token/s 大体与带宽成正比。以 96 DQ、14.4 Gb/s 为假设推算，峰值约 173 GB/s，8B 模型 4bit 的解码上限约 43 token/s，这就是下一代旗舰手机的大致天花板。

另一条路是近存。复旦等单位的 [3D 双 DRAM 单逻辑近存芯片](https://doi.org/10.1109/isscc49663.2026.11409184)（2/18）带宽密度 12.77 GB/s/mm²、访存能耗 0.67 pJ/b，GEMM 时间最多降低 98%，西安紫光国芯参与其中。它与港科大的 ReRAM 堆叠一起说明，国内团队正在用 3D 集成绕开 LPDDR 接口的带宽和能耗限制。

### 四、HPCA / CGO：端侧系统问题

HPCA 上与端侧直接相关的论文集中在多模态和空间计算。KAIST 的 [V-Rex](https://doi.org/10.1109/hpca68181.2026.11408603)（2/3）处理流式视频 LLM 的 KV cache 膨胀问题，免训练的动态 KV 检索加上一个只占 2% 面积的检索引擎，相对 Jetson AGX Orin 加速 1.9–19.7 倍，实现 3.9–8.3 FPS。上海交大的 [Splatonic](https://doi.org/10.1109/hpca68181.2026.11408505) 用稀疏像素采样让 3DGS-SLAM 在现成 GPU 上端到端提速 14.6 倍，专用架构相对移动 GPU 最高快 274.9 倍。同校的 [ORANGE](https://doi.org/10.1109/hpca68181.2026.11408575) 把 3DGS 混合改写为矩阵乘，在通用 NPU 上运行，比 Xavier NX GPU 快 15.5 倍。PC 方向，[LEGO](https://doi.org/10.1109/hpca68181.2026.11408477)（2/4）让一张 RTX 4090 同时渲染游戏、跑 LLM 角色控制，空余算力利用率提升 28.6%。CGO 上延世大学的 [OKO](https://doi.org/10.1109/cgo68049.2026.11395230) 在编译器层把端侧推理峰值内存平均降低 59%。此外，KAIST 的“The Cost of Dynamic Reasoning”从数据中心视角量化了智能体多轮推理的成本，是云端研究，只作背景参考。

### 五、FPGA：低成本板卡跑 30B MoE

FPGA 2026 第六场（2/24）有两篇值得关注的工作。中科院自动化所的 [Hummingbird+](https://doi.org/10.1145/3748173.3779189) 用入门级 Zynq UltraScale+ 自制 PCB，配 24 GB 内存，量产 BOM 预计低于 150 美元，跑 GPTQ 4bit 的 Qwen3-30B-A3B，解码超过 18 token/s，预填充超过 50 token/s。按激活约 3B 参数推算，每 token 需读约 1.5–1.7 GB，18 token/s 对应约 30 GB/s 等效带宽，但摘要没有给出板卡带宽，是否依赖专家缓存还待全文核实。UC Irvine 的 [TeLLMe](https://doi.org/10.1145/3748173.3779191) 在 5 W 功耗下以 1.58bit 三值权重解码，最高 25 token/s，首 token 时间 0.45–0.96 s。两篇都说明，**MoE 加大容量低价内存，或者三值量化加查表计算，能让 FPGA 这类非主流硬件跑起实用规模的 LLM**。

### 小结与存疑

1. 衡量单位变了：本月 ISSCC 的 LLM 芯片普遍按 μJ/token、token/s 报告，个性化（RAG+LoRA）和投机解码已有芯片实现。但各论文的口径不统一，引用时必须注明模型、精度以及是否计入外存访问。
2. 带宽仍是主线：LPDDR6（12.8–14.4 Gb/s）、3D 近存和 ReRAM 堆叠在同一个月集中出现，说明业界已有共识：端侧大模型提速主要靠内存，而不是靠 TOPS。
3. MoE 改变了“能跑多大模型”的算法：Hummingbird+ 用 30B 总参数、约 3B 激活参数达到 18 token/s，提醒读者评估端侧容量时要分开看总参数和激活参数。
4. 存疑：清华投机解码处理器的 μs/token 口径偏乐观；Mobilint、STM32N6 的 TOPS 数字来自公司或媒体资料，不是论文实测；Hummingbird+ 的带宽来源未披露。

## 6. arXiv 精选：手机 NPU 实测、ROM 固化与 MX 格式 NPU

### 总览：内存墙成为端侧论文的共同主题

2026-01-30 至 2026-02-26 这四周，arXiv 上与端侧硬件和系统相关的论文明显向一个问题集中：**模型权重和 KV 缓存放在哪里，怎么搬**。本窗口内往周硬件雷达没有已收录条目（2026-01-02 至 2026-01-30 各周 `hardware.items` 均为空），下文全部基于本次新收的 26 篇论文。按 arXiv v1 提交日计，它们分布在 02-02 到 02-26。大致可分为五类：

1. 厂商或厂商参与的端侧 NPU 与工具链：高通、三星、华为、意法半导体（ST）、恩智浦（NXP）、理想汽车；
2. 手机和 PC 上的真机实测；
3. 面向 LLM 的 NPU 与加速器架构；
4. 存内计算（CIM/PIM）；
5. MCU 与 IoT 级的极低功耗推理。

整体看，论文给出的“能跑多大模型”基本停在 0.3B–16B 之间，真机实测仍以 GPU/统一内存设备为主。直接报告手机 NPU 实测数字的只有三星 NanoFLUX（骁龙 8 Elite）一篇。

### 一、厂商动作：编译入口开放与低精度格式之争

本月最重要的厂商论文是高通的 [Hexagon-MLIR](https://arxiv.org/abs/2602.19762)（02-23）。高通团队把基于 MLIR 的 Hexagon NPU 编译栈开源（[代码仓库](https://github.com/qualcomm/hexagon-mlir)），Triton 内核和 PyTorch 子图可以直接编译成 NPU 二进制。思路是把多个算子融合成“巨型内核”，让数据尽量留在 TCM 紧耦合内存里，不再按库函数逐个往返 DDR。论文给出的都是算子级实测：
- GELU 用 HVX 向量化后，float16 提速 63.9 倍；
- 多线程在 512K 元素时提速 3.95 倍。

论文没有披露测试 SoC 型号，也没有端到端 LLM 的 tok/s。所以它的意义在于“开放”，不在性能：新注意力结构和 MoE 路由算子不必等 QAIRT 官方适配，开发者可以自己写 Triton 内核。

三星有两篇。三星研究院与三星电子的 [TriGen](https://arxiv.org/abs/2602.12962)（02-13）是端侧 LLM NPU 架构，做了三件事：
- 用 MX 微缩放 8-bit 格式做运算；
- 用查找表替代 softmax、SiLU 等非线性专用硬件；
- 在有限 SRAM 下用编译期搜索压低 DRAM 流量。

相对基线 NPU，TriGen 平均提速 2.73 倍，内存传输少 52%，代表模型是 Llama-3.2-3B。三星剑桥 AI 中心的 [NanoFLUX](https://arxiv.org/abs/2602.06879)（02-06）把 FLUX.1-Schnell 压缩到约 2.4B，在 Galaxy S25 Ultra（骁龙 8 Elite Hexagon NPU）上端到端约 2.5 秒生成一张 512×512 图像。这是本窗口唯一一组手机 NPU 实测数字。

华为团队（通讯作者为海思邮箱）发布了 [HiFloat4](https://arxiv.org/abs/2602.11287)（02-11）块浮点格式：64 个 4-bit 元素共享 32 bit 三级缩放元数据，平均每值 4.5 bit。论文称它在 LLaMA、Qwen、DeepSeek-V3.1 等模型上的平均精度高于 NVIDIA 的 NVFP4。4-bit 格式之争已经从数据中心延伸到端侧 NPU，量化模型怎么发布将受芯片格式影响。

其余几家：
- **ST 与米兰理工**：把数字存内计算单元嵌入 RISC-V 向量流水线（[02-02](https://arxiv.org/abs/2602.01827)），ResNet-50 峰值 137 GOP/s；
- **NXP 与德累斯顿工业大学**：用编译器代价模型把投机解码切分到 Cortex-A CPU 和 Mali GPU 上（[02-08](https://arxiv.org/abs/2602.08060)），最高提速 1.68 倍；
- **理想汽车与中科院自动化所**：在 Jetson Orin 上评测 1,942 个候选架构，提出[硬件协同设计缩放律](https://arxiv.org/abs/2602.10377)（02-10）。同等延迟下，其架构的 WikiText-2 困惑度比 Qwen2.5-0.5B 低 19.42%。车企已经在“先定芯片、再反推模型结构”。

### 二、手机与 PC 真机：瓶颈从算力转向容量

手机侧有三篇值得注意。
- **[Mobile-O](https://arxiv.org/abs/2602.20161)**（MBZUAI，02-23）：1.6B 参数的理解+生成统一模型，在 iPhone 17 Pro 上约 3 秒生成一张 512×512 图像，GenEval 74%。
- **[FlashMem](https://arxiv.org/abs/2602.15379)**（佐治亚大学，02-17）：不在推理前预载全部权重，改为按需把权重流式送入手机 GPU 的纹理内存。在 OnePlus 12/11、小米 6、Pixel 8 上，内存降低 2.0–8.4 倍，提速 1.7–75 倍，还能跑起其他框架装不下的 2.7B 模型。
- **[MeSP](https://arxiv.org/abs/2602.13069)**（OptAI，ACL 2026，02-13）：把端侧 LoRA 微调的峰值内存从 361 MB 压到 136 MB（Qwen2.5-0.5B），梯度与原方法完全一致。

三篇的共同前提是：手机上 6–12 GB 的 LPDDR 被所有应用共享，内存装不下比算力不够更常见。

PC 侧的焦点是 MoE 和长上下文。
- **[DALI](https://arxiv.org/abs/2602.03495)**（中科院自动化所等，02-03）：在 RTX 3090/4090 级本地 PC 上动态把专家分给 CPU 或 GPU。prefill 比 llama.cpp 平均快 7.62 倍，decode 快 3.97 倍。论文指出，Mixtral-8×7B 在已有方案中 PCIe 传输占推理时间六成以上。按推算，Mixtral 每 token 激活约 13B 参数，4-bit 约 6.5 GB；如果全部经 PCIe 4.0 的 32 GB/s 搬运，上限只有约 5 tok/s，所以“CPU 就地算一部分专家”是必然选择。
- **[HillInfer](https://arxiv.org/abs/2602.18750)**（中国科大等，02-21）：把 token 重要性评估卸载到三星 SmartSSD 的板载 FPGA，最高提速 8.56 倍。注意它的“AI PC”测试平台是 Xeon 加 RTX 4090 的台式机。
- **[持久化 Q4 KV 缓存](https://arxiv.org/abs/2603.04428)**（02-17，单作者）：在 24 GB 的 M4 Pro（273 GB/s）上，把每个智能体的 KV 以 4-bit 格式落盘、需要时直接恢复，多智能体切换的 TTFT 最多降低 136 倍。按推算，273 GB/s 统一内存跑 FP16 8B 模型（约 16 GB 权重）的 decode 上限约 17 tok/s，而论文报告 Llama 8B“FP16 权重”可达 39–55 tok/s，口径存疑，引用时以 TTFT 加速比为准。

这三篇共同说明：在 PC 端，SSD 正在变成 KV 缓存的第二层内存，“统一内存 + 高速 NVMe”是本地智能体的关键硬件组合。

评测方法上，[RooflineBench](https://arxiv.org/abs/2602.11506)（02-12）在 M1 Pro、RTX 3070/3090/4090、Jetson Orin Nano Super、树莓派 5 上实测屋顶线，发现两点：
- 模型越深，运算强度越低；
- MLA 注意力在带宽受限设备上更占优。

### 三、NPU 与加速器架构：从堆 TOPS 到少搬数据

本月的学术 NPU 论文几乎都在减少数据搬运。
- **[3D-Flow](https://arxiv.org/abs/2602.11016)**（中科院计算所，DATE 2026，02-11）：实测发现，片外流量被压下来之后，长序列负载里片上 SRAM 访问占能耗六成以上。于是用混合键合把 PE 垂直堆叠，层间寄存器直连。与 2D/3D 设计相比能耗降 46–93%，提速 1.4–7.6 倍。
- **[Voltra](https://arxiv.org/abs/2602.11357)**（KU Leuven，ISCAS 2026，02-11）：16nm 流片芯片，实测 1.60 TOPS/W、1.25 TOPS/mm²，主打不同负载下的高利用率。
- **[D-Legion](https://arxiv.org/abs/2602.06252)**（爱丁堡大学，02-05）：面向 BitNet 的众核脉动阵列，注意力延迟最多降 8.2 倍。
- **[TOM](https://arxiv.org/abs/2602.20662)**（微软研究院、上海交大等，02-24）：最激进的方案。它把三值化的 BitNet-2B 权重直接综合进 7nm 片上 ROM，存储密度 15.0 MB/mm²，并保留 SRAM 存放可微调的 QLoRA 适配器。芯片面积 56.9 mm²，功耗 5.33 W，峰值 3,306 token/s（仿真）。按推算，每 token 约 1.6 mJ。代价是模型固化在芯片里，只适合机器人这类“单模型、要毫秒级动作 token”的场景。

数据中心侧的参考是哈佛的 [RPU](https://arxiv.org/abs/2602.18568)（HPCA 2026，02-20）。它认为推理模型输出长、运算强度低，瓶颈在带宽，所以用“容量优化型 HBM”拿容量换每 bit 能耗。同 TDP 下运行 Llama3-405B，延迟比 H100 最多低 45.3 倍（仿真）。“带宽优先、容量让位”的取向与端侧 LPDDR6 和 PIM 的方向一致。

### 四、存内计算：从矩阵乘协处理器到 MoE 与通用计算

存内计算论文本月有三个方向。

**格式。** 一篇 28nm FP8 数字 CIM（[02-05](https://arxiv.org/abs/2602.05743)，IEEE TVLSI 已接收）支持全部 FP8 变体，E5M7 下 20.4 TFLOPS/W。UCLA 的 [MXFormer](https://arxiv.org/abs/2602.12480)（02-12）用电荷陷阱晶体管实现 MXFP4 模拟存内计算，全部权重常驻片上，ViT-B/16 单芯片 41,269 FPS。

**MoE。** 弗吉尼亚大学的 [MoE 存内计算](https://arxiv.org/abs/2602.10254)（ISCAS 2026，02-10）利用专家稀疏激活，让多个交叉阵列共享外围电路，面积效率提升 2.2 倍；门控输出缓存把能效提升 10.1 倍。

**通用化。** UIUC 与桑迪亚国家实验室的 [DARTH-PUM](https://arxiv.org/abs/2602.16075)（ASPLOS 2026，02-17）把模拟 MVM 和数字布尔运算放进同一阵列，让归一化、激活这类非矩阵运算也不必离开内存。

这些工作多数仍是仿真或电路级评估，离可买到的端侧产品还远。但 MoE 与 PIM 的结合、FP8/MX 格式的原生支持，与端侧模型的实际演进方向是吻合的。

### 五、极低功耗：MCU 与 IoT 级推理

最底层的设备也在吃进更大的模型。
- **[TinyVLM](https://arxiv.org/abs/2603.00136)**（02-24，单作者）：只用 285 KB RAM 和 892 KB flash，就在 STM32H7 上以 26 FPS 做零样本视觉识别；在带 CNN 加速器的 MAX78000 上超过 1,000 FPS。
- **[分布式提示缓存](https://arxiv.org/abs/2602.22812)**（庆应大学，EuroMLSys'26，02-26）：让多台树莓派 Zero 2W（512 MB）共享 Gemma-3 270M 的 KV 状态，TTFT 降 93%。
- **[SwapLess](https://arxiv.org/abs/2602.17808)**（02-19）：针对 Edge TPU 仅 8 MB 片上 SRAM，在线调整 CPU/TPU 切分点，多租户延迟降 77.4%。

在这个层级，“片上 SRAM 有多少”直接决定能跑什么。

### 六、能跑多大模型：按带宽推算的上限

本月论文给出的模型规模，需要放回具体硬件的内存带宽里核对。下面的推算都用“带宽 ÷ 每 token 读取字节数”估计 decode 上限，标为推算，不代表论文实测。

**iPhone 17 Pro。** 据[持久化 KV 论文](https://arxiv.org/abs/2603.04428)的设备表，它有 12 GB 内存、约 77 GB/s 带宽。
- 3B 模型按 4-bit 算约 1.5 GB 权重，decode 上限约 50 tok/s；
- 8B 模型 4-bit 约 4 GB，上限约 19 tok/s，而且还要和系统及其他应用共用 12 GB 内存。

所以 Mobile-O（1.6B）、NanoFLUX（约 2.4B）这类 2B 上下的模型，是当前旗舰手机上兼顾质量与速度的合理区间。

**M4 Pro。** 273 GB/s 统一内存。
- Gemma 3 12B 按 4-bit 约 6–7 GB 权重，decode 上限约 40 tok/s；
- 换成 FP16 约 24 GB，24 GB 机型已经装不下。

这也是该论文选择把 KV 量化到 4-bit 再落盘的原因：在内存只够 3 个 FP16 智能体的前提下，Q4 能多放 4 倍上下文。

**PC 上的 MoE。** 瓶颈不在显存带宽（RTX 4090 约 1,000 GB/s），而在 PCIe（约 32 GB/s）。专家能留在显存时速度很快；一旦要跨 PCIe 搬运，速度就跌一个数量级以上。这解释了 DALI 和 HillInfer 都把重点放在“减少跨总线搬运”，而不是加快 GPU 计算。

**固化权重芯片。** TOM 把 BitNet-2B 固化进片上 ROM，绕开了片外带宽限制，所以能达到千 token/s 级别。代价是模型容量被芯片面积锁死：56.9 mm² 里约 500 MB ROM，大约只够放 2B 级的三值模型。

**MCU。** 片上 SRAM 与 flash 以 KB 到 MB 计。TinyVLM 的 285 KB RAM 与 Edge TPU 的 8 MB SRAM 说明，这一层只适合视觉编码器和百 M 级以下的模型；LLM 级任务要靠多设备协作（如分布式提示缓存）或上行到手机。

### 七、值得后续跟踪的线索

- **Hexagon-MLIR 的演进。** 论文自称“进行中”。后续如果出现端到端 LLM 的 tok/s、对新一代 Hexagon 的支持，或与 QAIRT/Genie 的性能对比，就能判断开源路径能否替代官方算子库。
- **三星的端侧 NPU。** TriGen 的 MX 低精度与 LUT 非线性方案会不会出现在 Exynos 后续 NPU 上，目前没有官方证据，只能作为技术方向观察。
- **HiFloat4 的落地。** 需要看华为昇腾或麒麟的官方材料里是否出现 HiF4 支持，以及端侧模型是否以该格式发布。
- **计算型存储进入 AI PC。** HillInfer 用的是数据中心型 SmartSSD。消费级 PC 上能否出现带近存计算的 SSD，要看存储厂商在 HBF 等新介质上的产品节奏。
- **固化权重芯片的商业化。** TOM 一类“模型即芯片”的路线，在机器人和可穿戴领域是否会有初创公司跟进，值得持续观察。

### 结语：本月的三个判断

**一，端侧 AI 的主要矛盾已经从 TOPS 转到内存层级。** 手机端靠权重流式加载和微调省内存，PC 端靠 SSD 和计算型存储托住 KV 与 MoE 专家，芯片端靠 3D 堆叠、ROM 固化和存内计算减少搬运。

**二，厂商开始把底层能力开放给研究社区。** 高通开源 Hexagon-MLIR，三星、华为把 NPU 和低精度格式写成论文，理想汽车、NXP、ST 把车端和 MCU 场景的方法论公开。端侧 NPU 的编程门槛正在降低。

**三，真机数据仍然稀缺。** 本窗口直接给出手机 NPU 实测的只有 NanoFLUX，LLM 的 tok/s 与 J/token 在手机 NPU 上几乎没有公开报告；多数加速器数字是仿真值。读者看到“X 倍加速”时，应先确认对比基线和测试平台。

## 7. 总结：对端侧智能体意味着什么，以及 3 月该看什么

**对端侧智能体的含义**

1. **先算内存，再谈模型。** 2 月最硬的约束不是 NPU，而是 DRAM 的价格和可得性：LPDDR 单季涨约 90%（TrendForce 预测），旗舰停在 12GB，Pixel 10a 留在 8GB。端侧智能体的常驻模型在 2026 年上半年大概率停在 3–4B INT4（推算）。更大的模型要靠 MoE、闪存分页（UFS 5.0、FlashMem）和 KV 落盘（M4 Pro 上 Q4 KV 复用让 TTFT 最多降 136 倍，论文实测）。
2. **接口比模型先标准化。** Android AppFunctions 被官方类比为端侧版 MCP，Xcode 26.3 用 MCP 开放本地工具，三星把 Bixby 改成设备 Agent。智能体从读屏点按转向调用结构化的本地函数，这决定了手机智能体的可靠性上限；规划仍主要在云端（Gemini 3），完全在端侧的是诈骗检测这类常驻、隐私敏感的小任务。
3. **NPU 变成共享资源。** Android 17 要求直接访问 NPU 的 App 必须声明，系统模型、智能体和第三方 App 同时争用 NPU，仲裁上移到 OS 层；Hexagon-MLIR 开源和 OpenVINO 的 NPU 投机解码，则让开发者能更快把新算子和小模型放上 NPU。
4. **芯片研究在为“少搬数据”和“片上个性化”铺路。** ISSCC 上的 RAG+LoRA 片上个性化、近存与 ReRAM 堆叠、投机解码硬件，以及 μJ/token 计量，都对应智能体多轮、长输出、个性化的负载特征。亚毫瓦的常开感知（Innatera、ALPhA-Vision）加按需唤醒大模型的两级架构，是电池设备跑智能体的现实路径。

**留给 3 月的问题**

- **MWC（3 月 2–5 日）**：高通可穿戴平台（含独立常开 eNPU 的 Snapdragon Wear Elite）、联发科与 AMD 是否有新品；新机的内存配置是否因涨价下调。
- **Embedded World（3 月 10–12 日）**：Innatera 亚毫瓦雷达方案的现场实测；TI 带 NPU 的 MCU、Nordic nRF54LM20B 供货，看 MCU NPU 能否用 μJ/inference 和实际模型说话。
- **ASPLOS（3 月 22–26 日）**：DARTH-PUM 等存内计算与端侧系统论文的正式报告。
- **内存价格**：中国手机品牌 1Q26 LPDDR 合约谈判的结果；SK 海力士 LPDDR6 量产准备的进度；2Q26 涨幅是否继续扩大。
- **软件栈**：Android 17 平台稳定版（目标 3 月）对 NPU 优先级的具体规则；Hexagon-MLIR 能否给出端到端 LLM 数据；新 Siri 在 iOS 26.4 中的实际范围。

> 口径说明：标“官方”的是厂商发布的数字，“论文”是论文自报（多数为仿真或特定测试条件），“媒体”和“爆料”未经厂商确认，“推算”是本文按“带宽 ÷ 每 token 读取字节数”等公开参数计算的结果。2 月没有检索到新品的方向：Apple、Google 无新旗舰芯片；联发科、华为麒麟、小米玄戒、紫光展锐、瑞芯微在窗口内无新芯片；Intel、AMD 无新 PC 硬件（新品都在 1 月 CES）；Hailo、DEEPX、EnCharge、SiMa.ai 无可核实的新品或融资；知存、后摩、苹芯、九天睿芯无可核实的新动态。存疑项：清华投机解码处理器的 μs/token 口径、Hummingbird+ 的板卡带宽、M4 Pro KV 论文中“FP16 权重 39–55 tok/s”超出带宽上限、Apple LPDDR5X 价格为单一韩媒信源。
