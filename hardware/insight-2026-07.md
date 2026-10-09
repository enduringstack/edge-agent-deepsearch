# 硬件洞察：端侧 AI 芯片月报（2026-07-02 ~ 2026-08-01）

> **一句话结论：7 月是“成本月”和“验证月”。** 手机芯片没有新品（高通、苹果、联发科、华为、小米的旗舰都在 8–9 月发布），真正有分量的是两类信息。一是财报揭示的成本约束：内存厂商利润几乎全部来自 HBM，DRAM 继续涨价，高通和联发科的手机收入都下降约 20%。二是研究和实测给出的瓶颈定位：手机 NPU 擅长 prefill、不擅长 decode，端侧 VLM 的能耗主要花在生成上，MoE 外存分页取决于存储带宽。WAIC 2026 上国产存算一体、近存和具身芯片集中亮相，“10W 跑千亿模型”这类口径需要按带宽逐一核实。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断；第 1–6 节分厂商、分方向展开（高通 / Apple / 其他 SoC、PC 与 WAIC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选）；第 7 节是对端侧智能体的含义和观察清单。逐条动态（含“能跑多大模型”和可展开的“技术细节”）见 7 月各周首页的“硬件雷达”。

## 0. 总览：7 月的五个判断

**判断一：端侧 AI 的瓶颈被实测定位在 decode。** 四组独立测量给出一致结论：

| 平台 | 研究 | 关键结果 |
|---|---|---|
| 骁龙手机（8 Gen3 至 SM8850） | 清华 / 北交大 | NPU prefill 达 1463.7 tok/s，decode 却是 CPU 最快；调整休眠和调频参数可省约 54.8% 能耗（推算） |
| Jetson / 手机 VLM | 多篇 | decode 占能耗 86–97%，剪掉全部视觉 token 最多省 10% |
| Apple M5 | BaseRT | GPU Neural Accelerator 主要加速 prefill（最高为 llama.cpp 的 6.4 倍） |
| AMD AI PC | HeteroMosaic | iGPU+NPU 协同几乎只提升 prefill，decode 只有 0.98–1.13 倍 |

结论是：NPU 的 TOPS 决定 prefill，decode 由带宽、动态形状支持和调度决定。

**判断二：成本成为端侧 AI 的头号约束。**

| 方面 | 数据 |
|---|---|
| 内存价格 | TrendForce 预计 3Q26 DRAM 再涨 13–18% |
| 内存厂商 | 三星半导体贡献 99.7% 利润，SK 海力士营业利润率 76%；三星 CFO 称 2027 年供给更紧 |
| 手机芯片厂商 | 高通手机收入 -20%，联发科手机业务 -20%，两家都开始提价 |
| Apple | 称存储涨价是“百年一遇的洪水” |
| 台积电 | N2 只贡献 3% 营收，爬坡期就要拉低毛利率 3–4 个百分点 |

手机端内存容量短期很难增长，模型规模只能靠量化、MoE 和存储分层。

**判断三：“百亿级模型进设备”有了一批数据点，但速度要按带宽核实。**

| 设备 | 模型 | 速度（口径） |
|---|---|---|
| iPhone 17 Pro | 1-bit 稠密 Bonsai 27B（3.9GB） | 11 tok/s（PrismML） |
| M5 Max | 同上 | 87 tok/s（PrismML） |
| 骁龙手机 NPU | DraftExpert，DeepSeek-V2-Lite | 15.47 tok/s（论文） |
| 后摩 M50 联想整机（30W） | 122B | 50 tok/s（厂商）；按 153.6GB/s 反推，只可能是激活约 10B 的 MoE |

**判断四：存储分层是 Apple 和高通共同的方向。**

| 厂商 | 动向 |
|---|---|
| Apple | ICML 论文：专家缓存（SpecMD）、KV 预算（EpiCache）、FFN 外存化（MemoryLLM）；9 月 AFM 3 的“闪存存专家”路线已在这里埋下伏笔 |
| 高通 | HBC 近存 Gen 1 流片，2027 年年中出产品 |
| 存储 | 铠侠 UFS 5.0 样品读取达 10GB/s，SK 海力士和长鑫的 LPDDR6 下半年量产 |

**判断五：WAIC 上国产端侧芯片集中落地，但口径透明度不足。**

| 方向 | 产品 |
|---|---|
| 存算一体 | 后摩 M50（160 TOPS / 10W） |
| 3D 近存 | 东方算芯 DF1000（6.4TB/s） |
| 具身控制器 | 爱芯元智 1500 TOPS、蔚来神玑 800 TOPS |
| 协处理器 | 瑞芯微 RK1828（2B–7B 模型） |
| AI 眼镜 | 十余家、799–4599 元 |

普遍问题是不公布带宽、模型和实测 tokens/s；眼镜都没有披露端侧大模型。

### 7 月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 07-04~09 | Apple 在 ICML 2026 发布端侧推理论文（SpecMD、EpiCache、MemoryLLM 等） | 研究 |
| 07-06 | 清华 / 北交大实测：手机 NPU 的 decode 不如 CPU | 研究 |
| 07-14 | PrismML 1-bit Bonsai 27B：iPhone 11 tok/s | 模型 |
| 07-15 | NVIDIA Jetson T3000/T2000；网信办首批 7 款手机端侧生成式 AI 备案 | 机器人 / 监管 |
| 07-16 | 台积电 Q2：N2 占 3%，手机占 22% | 财报 |
| 07-17~20 | WAIC 2026：后摩 M50、RK1828、爱芯 1500 TOPS、AI 眼镜 | 展会 |
| 07-22 | 三星 Unpacked：Fold8 用骁龙，Flip8 用 Exynos 2600（2nm） | 终端 |
| 07-24 | Microchip 宣布收购 Hailo | 产业 |
| 07-29 | 高通 FQ3 财报，HBC Gen 1 流片，完成收购 Modular，签下宝马；SK 海力士 Q2；铠侠 UFS 5.0 | 财报 / 存储 |
| 07-30 | 三星 Q2、Apple Q3 财报 | 财报 |
| 07-31 | 联发科 Q2：Q3 推 2nm Agentic AI 旗舰 | 财报 |

## 1. 高通：硬件静默，基础设施先行

**判断**：7 月高通没有发布新芯片，Snapdragon 7/6/4、Wear、XR、Dragonwing、Ride/Cockpit、X2 均未检索到新 SKU（6 Gen 5 / 4 Gen 5 是 5 月，Reality Elite 和 START 是 6 月，均为背景）。这个月的主线有三条：一是 [FQ3 财报](https://www.qualcomm.com/news/releases/2026/07/qualcomm-announces-third-quarter-fiscal-2026-results) 显示，内存涨价让手机收入同比下降 20%，汽车收入同比增长 61%，同时宣布 HBC Gen 1 流片；二是同一天完成 [Modular 收购](https://www.qualcomm.com/news/releases/2026/07/qualcomm-completes-acquisition-of-modular)，拿下宝马座舱和智驾的十年主算力合同；三是端侧软件栈（GenieX、AI Hub）和 WAIC 演讲把“2B 至 3B 常驻模型 + 智能体 token 量级增长”讲清楚了。9 月旗舰的爆料也在月底开始出现。

### 一、7 月事件一览

| 日期 | 事件 | 类别 | 关键数字 | 口径 |
|---|---|---|---|---|
| 7/2 至 7/31 | [GenieX](https://github.com/qualcomm/GenieX/releases) v0.3.14 至 v0.3.18 | 软件栈 | Gemma 4 E2B/E4B 通过 QAIRT 上 HTP；默认使用 NPU | 官方 |
| 7/3 至 7/15 | [AI Hub Models](https://github.com/quic/ai-hub-models/releases) v0.57.1 至 v0.58.0 | 软件栈 | GR00T-N1.5 四组件上 NPU；Qwen3-VL-8B | 官方 |
| 7/18 至 7/19 | WAIC 2026 徐晧演讲（[爱范儿](https://www.ifanr.com/1672429)、[澎湃](https://m.thepaper.cn/newsDetail_forward_33613484)） | 产业 | 手机 NPU 跑 2B 至 3B；座舱跑 10B 以上；token 需求每阶段约 10 倍 | 官方演讲 |
| 7/21 | [Whispp × X Elite](https://www.3blmedia.com/news/how-whispp-and-qualcomm-brought-voice-reconstruction-ai-snapdragon-x-elite) | PC | NPU 时延 48 至 50ms；续航 310 对 130 分钟 | 厂商试点 |
| 7/22 | [三星 Unpacked](https://www.qualcomm.com/news/releases/2026/07/qualcomm-and-samsung-expand-collaboration-with-snapdragon-poweri)：Fold8 系列、Watch9、眼镜 | 移动 / 可穿戴 | 8 Elite Gen 5 for Galaxy；Wear Elite；AR1 Gen 1 | 官方 |
| 7/23 至 7/25 | SM8850-1-AB 爆料（[Tech Outlook](https://www.thetechoutlook.com/tech-whispers/new-snapdragon-8-elite-gen-5-sm8850-1-ab-version-tipped-to-launch-in-h2-2026/)） | 移动 | GB6 约 3,600 / 11,300；约 4,000 元价位 | 爆料 |
| 7/26 至 7/27 | Gen 6 Pro die 爆料（[TechTimes](https://www.techtimes.com/articles/321683/20260727/snapdragon-8-elite-gen-6-pro-exclusive-die-size-lpddr6-first-ai-frame-fusion-detailed.htm)） | 移动 | 约 134mm²；LPDDR6 14.4Gbps；2 个 Matrix ALU | 爆料 |
| 7/29 | FQ3 财报，HBC Gen 1 流片 | 产业 / 数据中心 | 营收 99.47 亿美元；汽车 +61% | 官方 |
| 7/29 | Modular 交割 | 软件栈 | Lattner 出任 EVP | 官方 |
| 7/29 | [BMW](https://www.qualcomm.com/news/releases/2026/07/qualcomm-named-bmw-group-s-lead-compute-silicon-provider-for-dig) 座舱和智驾主算力供应商 | 车载 | 覆盖“下一个十年” | 官方 |

### 二、FQ3 财报：内存墙首先体现在财务上

| 分部（百万美元） | FQ3 FY26 | FQ3 FY25 | 同比 | FQ4 指引 |
|---|---|---|---|---|
| QCT 手机 | 5,086 | 6,328 | -20% | 约 5,200 |
| QCT 汽车 | 1,588 | 984 | +61% | 同比约 +60% |
| QCT IoT | 1,830 | 1,681 | +9% | 同比约持平 |
| QCT 合计 | 8,504 | 8,993 | -5% | 8,400 至 9,000 |
| 总营收 | 9,947 | 10,365 | -4% | 9,700 至 10,500 |

数据来自[财报 PDF](https://s204.q4cdn.com/645488518/files/doc_financials/2026/q3/FY2026-3rd-Quarter-Earnings-Release.pdf)和[电话会实录](https://s204.q4cdn.com/645488518/files/doc_financials/2026/q3/Q3FY26_Earnings_Call-Transcript_7-30-26_FINAL.pdf)。对端侧芯片来说，有几点值得注意：

- **手机下滑是内存造成的，不是需求本身**。CFO 的说法是“industry-wide memory dynamics”；Amon 称，即使高通提价两位数，与内存 BOM 的涨幅相比也“很小”，OEM 甚至会改用上一代芯片。端侧大模型需要大内存，内存涨价相当于直接抬高了“能跑多大模型”的门槛。
- **IoT 内部分化**。FQ4 中平板等消费品受内存拖累，工业、网络和机器人保持两位数增长；工业 design-win 管道超过 70 亿美元，FY26 已锁定超过 35 亿美元。
- **HBC Gen 1 流片**。HBC 把计算直接集成到高密度内存旁，未来几个季度展示硅片，2027 年中推出首款方案。本次电话会没有单独提到 AI200/AI250，改用“基于 HBC 的加速器”的说法。数据中心目标为 FY27 50 亿美元、FY29 150 亿美元。
- **端侧表态**：中国大型 OEM 正在准备端侧 agent 和 orchestrator，Amon 称已看到“agentic smartphone cycle”的早期迹象；PC 侧提到 GoogleBooks（搭载 Gemini Intelligence）的 design-win 份额领先，以及与 Microsoft 合作的 [Project Solara](https://www.tomshardware.com/tech-industry/artificial-intelligence/microsoft-unveils-project-solara-ai-a-chip-to-cloud-platform-built-to-power-a-new-generation-of-agent-first-enterprise-devices-hardware-designed-to-run-ai-agents-instead-of-traditional-apps)（6 月 Build 发布，高通负责便携和穿戴形态）。X2 的份额数字未披露。
- **苹果份额加速下滑**：由于供应约束，新 iPhone 中高通基带的份额将“明显低于”此前估计的 20%。管理层希望 FY27 非手机业务的增量能够完全抵消 FY26 的苹果收入；非手机业务增速预计从 FY26 的 24% 提升到 FY27 的 60% 以上，FY27 非手机收入占 QCT 的比重超过一半。
- **毛利率**：提价会逐步生效，CFO 称基础业务毛利率预计回到 48% 至 50% 区间；数据中心早期收入以定制芯片为主，利润率明显较低，会拖累 QCT 加权毛利率 1.5 至 2 个百分点（电话会原话）。对端侧来说，这意味着 9 月以后的旗舰 SoC 单价会明显上升，8 月宣布的两位数涨价见 8 月报告。

### 三、终端落地：三星 Unpacked 与模型能力梯度

7 月 22 日 Unpacked 上，Fold8 Ultra 和 Fold8 使用 Snapdragon 8 Elite Gen 5 for Galaxy。[三星官方页](https://www.samsung.com/sg/mobile/mobile-phone-buying-guide/galaxy-z-fold8-ultra-release-date-specs/)只写了“tuned with an upgraded NPU, GPU and CPU”，没有百分比。[91mobiles](https://www.91mobiles.com/samsung-galaxy-z-fold-8-ultra-price-in-india) 列出的频率是 2×4.74GHz + 6×3.62GHz（媒体口径）。Flip8 在欧洲和亚洲大部分地区使用 Exynos 2600。Galaxy Watch9 和 Watch Ultra2 是 [Wear Elite](https://9to5google.com/2026/03/01/qualcomm-snapdragon-wear-elite/) 首批落地的旗舰手表，Intelligent Eyewear 使用 AR1 Gen 1，预计秋季上市。电话会称三星旗舰约 70% 使用骁龙。

| 平台（7 月落地或提及） | NPU | 能跑的模型（口径） | 速度 | 来源 |
|---|---|---|---|---|
| 8 Elite Gen 5 for Galaxy（Fold8） | Hexagon，TOPS 未披露 | 未披露；WAIC 称手机跑 2B 至 3B | 未披露 | 官方 / 官方演讲 |
| Wear Elite（Watch9） | Hexagon + eNPU | 最高 2B | 约 10 tok/s | 媒体转述官方（3 月） |
| AR1 Gen 1（眼镜） | Hexagon | 未披露；第三方 1-bit 1.7B | 15.36 tok/s | [第三方](https://alphasignal.ai/news/prismml-runs-bonsai-1-7b-on-smart-glasses-at-2x-the-speed) |
| 座舱芯片（未点名） | 未披露 | 10B 以上 | 未披露 | WAIC 演讲 |
| X Elite（Whispp） | 45 TOPS | 语音重建（规模未披露） | 48 至 50ms 每步 | 厂商试点 |

在 16GB 内存封顶、内存价格高企的情况下，按 4-bit 估算，手机上真正能常驻的 LLM 大约在 2B 至 4B 量级（本文推算），与 WAIC 上“2B 至 3B”的口径一致。9 月 Gen 6 的“30B MoE（约 3B 激活）”本质上是在保持约 3B 激活参数不变的前提下，靠闪存流式加载专家来扩大总参数量（见 9 月报告）。

Wear Elite 值得单独说明。它是高通第一颗带 Hexagon NPU 的手表芯片，采用两级 NPU 设计：主 NPU 负责 2B 级生成式任务，eNPU 常驻处理关键词检测、活动识别和降噪。这与手机上“Sensing Hub Micro NPU + 主 Hexagon”的分层思路相同，只是把功耗台阶再往下移了一级。CPU 首次采用 1+4 大小核，单核性能约为 W5+ Gen 2 的 5 倍（媒体转述官方）。从 Watch9 开始，手表上的模型可以在本地生成摘要和回复，不必每次都回传手机，但三星没有公布实际搭载的模型规模和续航影响。

### 四、汽车与工业：BMW 十年合同与机器人模型

7 月 29 日，高通宣布成为宝马下一代数字座舱和 ADAS/AD 的 lead compute silicon provider，覆盖“下一个十年”的车型项目，供货范围包括 Snapdragon Cockpit、Ride、Elite 汽车平台以及专用 AI 加速器（[BMWBlog](https://www.bmwblog.com/2026/07/29/qualcomm-bmw-chip-deal-digital-cockpit-adas/)）。此前的合作成果是 2025 年 11 月随 Neue Klasse iX3 量产的 Snapdragon Ride Pilot。

- **舱驾由同一供应商提供**：过去座舱和智驾芯片常由不同厂商供货；这次统一交给高通，为舱驾融合以及座舱 LLM 和智驾 VLA 共享算力、内存池提供了前提。“专用 AI 加速器”说明 SoC 内置 NPU 已不足以承载下一代车端模型，但型号和 TOPS 都未披露。
- **车端模型规模**：WAIC 演讲称座舱芯片可稳定运行 10B 以上参数的模型，是手机 2B 至 3B 的 3 至 5 倍；车端功耗预算和内存容量都更宽松，因此成为高通端侧大模型的上限场景。
- **工业和机器人**：电话会称工业 design-win 管道超过 70 亿美元，FY29 工业、网络和机器人收入目标为 80 亿美元；渠道客户超过 3.8 万家，加上 Arduino 和 Edge Impulse 覆盖 3,000 万以上用户。AI Hub 在 7 月 9 日把 GR00T-N1.5 放到 Dragonwing IQ-9075 上，正是这条业务线在软件上的体现。

### 五、WAIC 2026：智能体时代的端侧架构

徐晧在 7 月 18 日荣耀分论坛和 7 月 19 日端侧 AI 论坛上的要点（[IT之家](https://www.ithome.com/0/978/832.htm)）：

- **token 需求逐级放大**：单轮对话、多轮对话、agent 调度，每个阶段所需的 token 处理量约增加 10 倍（万级、十万级、百万级）。因此需要端云协同：端侧小模型处理隐私和实时任务，云端负责深度推理和规划。
- **三类单元分工**：新 CPU 负责规划和控制；Sensing Hub 以低功耗持续感知，构建个人知识图谱；Hexagon NPU 中有面向长上下文、张量/矩阵和图像的加速单元，跑 2B 至 3B 模型（面壁 MiniCPM 2B/3B 流畅运行）。
- **解读**：“长上下文加速”的提法比 9 月 Element Accelerator（KV Cache 和动作循环加速）早了两个月；百万级 token 的 agent 负载在端侧主要受 prefill 和 KV Cache 带宽约束，这也解释了 9 月为什么主打“共享内存 +50%”而不是 TOPS。本届 WAIC 没有检索到高通发布新芯片，展台细节也未检索到。

### 六、软件栈：GenieX 与 AI Hub 为 8 月和 9 月铺路

| 版本 | 日期 | 与 NPU 相关的变化 |
|---|---|---|
| GenieX v0.3.14 | 7/2 | Hexagon toolchain v0.7，修复 HTP v75 被误编译的问题 |
| AI Hub v0.57.1 | 7/3 | Qwen3-4B-2507 支持 GenieX；IQ-8275 上的 Qwen3-8B 和 Qwen3-VL-4B |
| AI Hub v0.57.3 | 7/9 | GR00T-N1.5（ViT / LLM / projector / DiT）上 NPU，含 IQ-9075 数据 |
| AI Hub v0.58.0 | 7/15 | Qwen3-VL-8B、Qwen3-1.7B（SpinQuant），QAIRT 2.45 |
| GenieX v0.3.16 | 7/20 | 默认使用 NPU；Hexagon SDK 6.6；QAIRT sliding window；prefill 按 padded 长度统计 |
| GenieX v0.3.17 | 7/24 | 自动识别 IQ-8275 和 X2 Plus；Windows 免证书 HTP catalog |
| GenieX v0.3.18 | 7/31 | Gemma 4 E2B/E4B 通过 QAIRT 上 HTP；投机解码扩展到所有模型 |

技术要点有三条。第一，**机器人 VLA 上 NPU**：GR00T-N1.5 被拆成四个 context binary 分别编译，扩散动作头（DiT）也放在 Hexagon 上跑，与电话会中“工业和机器人 design-win”的业务线对应，但模型页没有公开时延和内存。第二，**口径变化**：从 v0.3.16 开始，prefill 速率按 padded 长度统计，跨版本比较 tok/s 时需要注意。第三，**解码优化**：7 月先把投机解码扩展到所有模型，8 月再加入 MTP 和 26B-A4B MoE（见 8 月报告）。7 月所有 release notes 都**没有给出 tokens/s**。PC 侧唯一可量化的数据来自 7 月 21 日的 Whispp 试点：实时语音重建放在 X Elite NPU 上时，每步时延约 48 至 50ms，续航约 310 分钟，是 CPU（约 130 分钟）的约 2.4 倍，且 CPU 路径有明显的时延尖峰。这说明常驻、低时延的语音类负载放在 NPU 上，价值主要在续航和稳定性，而不是峰值速度。Modular（Mojo/MAX）交割后，官方定位是“硬件无关、覆盖数据中心与边缘”，但尚未提到 Hexagon 后端。

### 七、爆料：9 月旗舰的轮廓

| 项目 | 7 月爆料（SM8975） | 9 月官方（见 9 月报告） |
|---|---|---|
| 工艺 / die | N2P，约 134mm²（Gen 5 为 126.2mm²） | 2nm（N2P） |
| GPU | Adreno 850，18MB GMEM，2 个 Matrix ALU | 首次加入 AI 矩阵核心 |
| 内存 | LPDDR6 14.4Gbps/pin | LPDDR6 10.6Gbps，127.2GB/s |
| NPU | 未泄露 | Element Accelerator，共享内存 +50% |

从 3nm 换到 N2P 后，die 面积反而增加约 6%，说明新增的晶体管主要用在缓存（LLC 8MB、GMEM 18MB）和 GPU 矩阵单元上。文章的成本模型估算 N2P 晶圆约 3.3 万美元（3nm 约 2 万美元），每颗良品 die 约 84 美元，LPDDR6 比 LPDDR5X 贵约 20%。这些都是第三方模型，但与 7 月 29 日电话会上的提价口径方向一致。7 月 24 日另有爆料称小米 18 Pro Max 首发 Pro 版。值得注意的是，所有 7 月爆料都没有涉及 Hexagon NPU，NPU 的新特性被保密到 9 月 22 日。爆料的 LPDDR6 14.4Gbps 按 96bit 位宽算，峰值约 172.8GB/s；9 月官方实际为 10.6Gbps、127.2GB/s，说明爆料偏乐观（本文推算）。

此外，7 月 23 日至 25 日有爆料称 SM8850-1-AB 将作为第四款 Gen 5 变体推出（GB6 约 3,600 / 11,300，约 4,000 元价位），8 月以“V 系列”名义上线，唯一已知差异是 HPM 从 18MB 降到 12MB，NPU 不变（[Beebom](https://gadgets.beebom.com/news/qualcomm-introduces-snapdragon-8-elite-gen-5-v-series-with-key-gaming-upgrade)）。在内存涨价的背景下，砍 GPU 缓存、保留 NPU 是把旗舰 NPU 下放到中端机型的较便宜办法。

### 小结

7 月的高通可以概括为“硬件静默，基础设施先行”。财务上，内存涨价使手机收入下降 20%，被迫提价；汽车（+61%、BMW 十年合同）和工业机器人成为新的增长来源。技术上，云端的 HBC 流片和端侧的“2B 至 3B 常驻 + 长上下文加速”说的是同一件事：端侧 AI 的瓶颈正在从 TOPS 转向内存容量、带宽和成本。软件上，GenieX 和 AI Hub 已经把 Gemma 4、Qwen3-VL-8B、GR00T-N1.5 放上 Hexagon，Modular 则提供了打通端云软件栈的可能。需要提醒的是，7 月所有官方材料都没有给出 tokens/s、TOPS 或功耗的绝对值，die 尺寸和 LPDDR6 速率等信息都属于爆料，其中 LPDDR6 速率已被 9 月官方数据证明偏乐观。

（检索说明：7 月未检索到 Snapdragon 7/6/4 系、Wear、XR、Dragonwing、Ride/Cockpit 或 X2 的新 SKU 发布；7 月未检索到 OnQ 上关于 Hexagon 或 Sensing Hub 的技术长文；WAIC 展台细节未检索到。）

## 2. Apple：没有新芯片的“软件月”

7 月的 Apple **没有发布任何芯片或硬件**。M6、M5 Ultra 在 8 月 25 日发布，A20 Pro 在 9 月发布，7 月处在两者之前的空档。本月真正有信息量的是三件事：ICML 2026 上一批关于“权重和 KV 如何在 DRAM 与闪存之间搬运”的论文；iOS 27 从 beta 3 到公测版的 Siri AI 推进，以及由此暴露出的机型分层；还有一份外部数据——PrismML 的 1-bit 稠密 27B 模型在 iPhone 17 Pro 上跑到 11 tok/s。7 月 30 日的财报则从供给侧给出两条约束：存储涨价和先进制程紧张。

### 一、本月 Apple 相关事件一览

| 日期 | 事件 | 口径 | 与端侧 AI 的关系 |
|---|---|---|---|
| 07-04 | [Apple at ICML 2026](https://machinelearning.apple.com/updates/apple-at-icml-2026) 参会页 | 官方 | 约 25 篇主会论文，其中至少 6 篇与端侧推理效率直接相关 |
| 07-06 | [iOS 27 dev beta 3](https://9to5mac.com/2026/07/06/heres-whats-new-with-ios-27-beta-3/)（24A5380h） | 媒体 | Apple Intelligence 资产重新下载，语音滑块限 12GB 机型 |
| 07-07 | [MLX v0.32.0](https://github.com/ml-explore/mlx/releases/tag/v0.32.0) | 官方 | iOS 默认 Metal，修复 NAX 量化 GEMM，新增 qmv_wide |
| 07-09 | [Apple 与 PrismML 接触](https://www.macrumors.com/2026/07/09/apple-prismml-larger-on-device-ai-models/) | 爆料（The Information） | 评估在 iPhone 上运行稠密 27B 模型 |
| 07-13 / 07-23 | [OS 27 公测版 1](https://www.macworld.com/article/3190070/the-os-27-public-betas-are-out-now-with-siri-ai-platform-improvements-and-more.html) / 公测版 2 | 媒体 | Siri AI 首次面向公众，仅英语，欧盟暂缺 |
| 07-14 | [Bonsai 27B 开源](https://prismml.com/news/prismml-releases-bonsai-27b) | 第三方官方 | 1-bit 3.9GB，iPhone 17 Pro 上 11 tok/s |
| 07-16 | [TSMC Q2 财报](https://pr.tsmc.com/english/news/3326) | 官方 | N2 占晶圆收入 3%，Q3 进入“陡峭爬坡” |
| 07-20 | [iOS 27 dev beta 4](https://9to5mac.com/2026/07/20/heres-whats-new-with-ios-27-beta-4/) | 媒体 | 有媒体称 Siri AI 覆盖 iPhone 15 Pro 及以上 |
| 07-30 | [Q3 FY26 财报](https://www.apple.com/newsroom/2026/07/apple-reports-third-quarter-results/) | 官方 | 端侧 + PCC；存储涨价是“100-year flood”；先进制程受限 |

硬件方面，本月只有传闻：[iLounge](https://www.ilounge.com/news/apple/apple-to-only-make-base-m6-chip-before-moving-to-m7) 汇总称 M6 只出基础款，M7 提前到 2027 年初。其中“M5 Ultra 最早 2027 年”一条已被 8 月的发布推翻，整体可信度低。关于 A20 Pro 的 WMCM 封装，本月没有找到新的一手报道。

### 二、ICML 2026：Apple 的端侧推理研究集中在“分层存储”

把 Apple 本月在 ICML 上与效率相关的论文放在一起，可以看出一条清晰的主线：**模型总参数放不进 DRAM，那就决定好什么放 DRAM、什么放闪存、什么时候搬运**。这与 [AFM 3](https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models) Core Advanced 的官方架构一致：20B 总参、激活 1–4B，共享专家常驻 DRAM，路由专家从 NAND 按需载入。

| 论文 | 解决的问题 | 关键数字（论文口径） | 对应的端侧瓶颈 |
|---|---|---|---|
| [SpecMD](https://machinelearning.apple.com/research/specmd-expert-prefetching) | MoE 专家缓存与预取 | Least-Stale 冲突缺失比 LRU 少最多 85 倍；命中率 >88%；缓存约 0.6GB；OLMoE 上 TTFT 最多 -34.7% | 路由专家换入换出 |
| [EpiCache](https://machinelearning.apple.com/research/epicache) | 长期对话的 KV 预算 | 4–6 倍压缩接近全缓存精度；准确率最多 +30%；延迟 -2.4 倍；峰值内存 -3.7 倍 | 多轮对话中 KV 线性增长 |
| [Learning to Evict](https://machinelearning.apple.com/research/evict) | 学习式 KV 淘汰 | 每个 head 一个 RL agent；RULER 测到 128K；零样本迁移 | 固定 KV 预算下的长上下文质量 |
| [MemoryLLM](https://machinelearning.apple.com/research/memoryllm) | FFN 外存化 | FFN 变成 token 级查表，可在显存与存储之间搬运；数字未披露 | DRAM 容量 |
| [RCD](https://machinelearning.apple.com/research/residual-context-diffusion) | 扩散 LM 浪费的计算 | +5–10 点准确率；同精度下步数最多 -4–5 倍；转换约需 1B tokens | 解码受带宽限制 |
| [Unmasking Policy](https://machinelearning.apple.com/research/unmasking)（Oral） | 扩散 LM 每步解开哪些 token | 单层 Transformer 策略，全扩散生成下优于启发式 | 同上 |

几点判断：

- **SpecMD 的结论支撑了 AFM 3“按 prompt 路由”的选择。** 论文发现 MoE 专家访问不满足时间局部性，LRU/LFU 会出现大量冲突缺失。在手机上，未命中意味着从 NAND 读取，代价比 GPU 显存场景高得多。与其逐 token 换专家，不如在 prefill 时一次选定，这是合理的工程折中（推断）。
- **KV 管理开始和权重管理同等重要。** Siri AI 主打个人上下文与多轮对话，EpiCache 的分块 prefill 可以把峰值内存压住，这对 8GB 机型尤其关键。两篇 KV 论文都已开源代码（[ml-epicache](https://github.com/apple/ml-epicache)、[ml-learning-to-evict](https://github.com/apple/ml-learning-to-evict)）。
- **扩散 LM 是绕开带宽墙的候选路线。** 自回归解码速度约等于“带宽 ÷ 每 token 读取的权重字节数”；扩散 LM 一次权重读取可以产出多个 token，再把步数减少 4–5 倍，就能把手机上闲置的 NE/GPU 算力用起来。不过目前没有任何证据显示它已进入 Apple 产品。
- 需要说明的是，这些论文的 arXiv 首版大多在 2025-09 至 2026-02 之间，7 月是正式发表；实验硬件在摘要中均未披露，没有 iPhone 或 Mac 上的实测数据。

### 三、iOS 27 beta 3/4 与公测：Siri AI 的机型分层

| 层级 | 机型（媒体口径） | 内存 | 可用能力 | 推测的模型 |
|---|---|---|---|---|
| 基线 | iPhone 15 Pro/Pro Max、iPhone 16 全系 | 8GB | Siri AI 对话、个人上下文、跨 App 操作 | AFM 3 Core（3B）+ PCC（推断） |
| 高阶 | iPhone 17 Pro/Pro Max、iPhone Air | 12GB | 另有表现力语音（Pace/Expressivity）、系统级听写 | AFM 3 Core Advanced（[MacRumors 转述](https://www.macrumors.com/2026/07/09/apple-prismml-larger-on-device-ai-models/)） |

- **模型以独立资产分发。** beta 2→3 之间，部分设备重新下载了 Apple Intelligence 资产，期间新 Siri 不可用（[9to5Mac](https://9to5mac.com/2026/07/06/heres-whats-new-with-ios-27-beta-3/)）。可见端侧权重和适配器仍在频繁迭代，而且可以不随系统镜像一起更新。
- **端云分工未披露。** 公测报道只说 Siri AI“结合端侧 Foundation Models 与 Private Cloud Compute”（[eWeek](https://www.eweek.com/news/apple-ios-27-public-beta-siri-ai-2026/)）。仅英语、欧盟缺席、部分用户需要候补，说明 PCC 容量和合规是放量的约束。
- **体验仍有毛刺。** [PhoneArena](https://www.phonearena.com/news/siri-ai-gets-better-with-latest-beta-update_id182128) 称 beta 4 已支持免唤醒追问，但偶尔会在用户说完前截断，或完全没有响应。TidBITS 作者实测，计时器启动需要 5–6 秒（[TidBITS](https://tidbits.com/2026/07/31/apples-q3-2026-earnings-record-revenue-and-marketing-to-the-street/)）。
- 另有两点存疑：beta 3 的发布日期，9to5Mac 记为 7 月 6 日，Macworld 记为 7 月 3 日；9to5Mac 给出的 beta 4 build 号 23G71 与 24A 序列不连续。

### 四、MLX 0.32 与 PrismML：12GB 手机上的稠密 27B

[MLX v0.32.0](https://github.com/ml-explore/mlx/releases/tag/v0.32.0)（7 月 7 日）是本月唯一的 MLX 版本，与端侧相关的改动有四项：iOS 默认启用 Metal 后端；修复 M5 GPU Neural Accelerator（NAX）路径上 qmm 的 int16 溢出和 MoE 用的 gather_qmm；新增小 batch 量化 matvec 内核 qmv_wide；SDPA 支持 192/128 非对称 head dim（MLA 类结构）。发布页没有性能数字。

PrismML 的 Bonsai 27B 正是跑在修改版 MLX 上。把它与 Apple 自家路线对比，可以量化“端侧能跑多大模型”：

| 项目 | AFM 3 Core Advanced（Apple 官方） | Bonsai 27B 1-bit（PrismML 官方） | Bonsai 27B 三值 |
|---|---|---|---|
| 结构 | 20B MoE，激活 1–4B | 27B 稠密，全激活 | 27B 稠密 |
| 位宽 | 未披露 | 约 1.125 bit（媒体口径） | 1.58 bit（另有 1.71 bit 的说法） |
| 权重占用 | 未披露（路由专家放 NAND） | 3.9GB | 5.9GB |
| iPhone 17 Pro 速度 | 未披露 | 11 tok/s | 未披露 |
| M5 Max 速度 | — | 87 tok/s | 58 tok/s |
| 质量 | 未披露 | 官方称 >90% 全精度；社区 98 题测试 82.9% 对 94.2% | 官方称 >95% |

- **瓶颈仍是带宽。** 每 token 读取 3.9GB，11 tok/s 对应约 43GB/s 有效带宽；M5 Max 87 tok/s 对应约 340GB/s（均为推算）。速度与位宽基本成反比，与 NE/GPU 算力关系不大。
- **散热和续航同样是约束。** 媒体转述白皮书称，约 5 分钟后出现轻微降频，每 1% 电量约生成 672 tokens；4K 上下文时运行内存约 5.9GB，约占 12GB 的一半（[The Decoder](https://the-decoder.com/bonsai-27b-is-a-full-open-reasoning-model-that-fits-on-an-iphone/)）。
- **Apple 为何在意。** 按 The Information 的报道，Apple 评估的是速度、能效与性能，动机是把更多功能从 PCC 移到端侧。不过这只是探索性接触，没有产品承诺。

**用同一把尺子估算端侧能跑多大模型。** 解码速度上限约等于“有效带宽 ÷ 每 token 读取的权重字节数”。以 Bonsai 在 iPhone 17 Pro 上实测出的约 43GB/s 有效带宽为基准（推算），可以粗略比较几种方案：

| 方案 | 每 token 读取量 | 按 43GB/s 推算的上限 | 备注 |
|---|---|---|---|
| AFM 3 Core，3B 稠密，按 4-bit 计 | 约 1.5GB | 约 28 tok/s | Apple 未披露位宽，属估算 |
| AFM 3 Core Advanced，激活 4B，按 4-bit 计 | 约 2GB | 约 21 tok/s | 若专家未命中，还要从 NAND 读取，实际更低 |
| AFM 3 Core Advanced，激活 1B，按 4-bit 计 | 约 0.5GB | 约 86 tok/s | 激活下限场景 |
| Bonsai 27B，1-bit | 3.9GB | 11 tok/s（实测） | 第三方官方口径 |

这张表说明两点。第一，在同一代手机上，“稀疏 + 4-bit”和“稠密 + 1-bit”的速度处在同一量级，差别主要在质量和闪存访问模式。第二，在带宽不变的前提下，ICML 上的扩散解码和专家预取研究，是继续提速的少数手段之一。表中 AFM 3 的数字全部是假设位宽下的推算，Apple 没有公布任何端侧 tok/s。

### 五、财报与供应链：存储涨价和 N2 产能

- **财报（官方）。** Q3 FY26 营收 US$1094 亿（+16%），Mac US$104 亿（+29%）。Cook 的原话包括：模型“running on-device and on servers using private cloud compute”；“we use some third-party cloud, and we do our own data centers”；存储价格是“100-year flood”，并且还会涨；Mac 供应受限“主要由 SoC 所用先进制程的可用性导致”，9 月季度影响将显著增加（[纪要](https://www.webull.com/news/15364638775387136)）。Q4 指引为营收 +9–11%、毛利率 47–48%（媒体口径）。
- **TSMC（官方）。** Q2 N2 首次单列，占晶圆收入 3%，Q3 迎来“steep ramp-up”（[TSMC](https://pr.tsmc.com/english/news/3326)），与 A20 Pro 和 M6 的量产窗口吻合。
- **Mac 作为本地 AI 平台。** Cook 在开场发言中提到，有企业“部署 Mac Studio 集群在本地运行前沿级模型”；纪要摘要还提到 Disney 创意团队用 Mac 做端侧 AI，以降低云端 token 成本、保护 IP。Mac 营收 +29% 主要由 MacBook Pro 与 MacBook Neo 拉动，Apple 没有把增长直接归因于 AI。
- **AI 投入的口径。** Cook 表示 AI 支出“增长了相当多”，并且不仅计入 OpEx，也计入 COGS 等科目；同时确认 Apple 使用部分第三方云，也有自建数据中心。PCC 的规模、芯片构成和 capex 数字均未披露。他还提到会为 Siri AI 重度用户推出更高的 iCloud+ 档位，侧面说明个人上下文相关的存储和云端负载会随使用量增长。
- **推论。** DRAM 涨价加上 N2 产能有限，端侧 AI 的提升路线只能是“容量不加、位宽和算力加”。9 月 A20 Pro 维持 12GB、改用 96-bit 位宽，正是这一路线的体现（见后续月份报告）。

### 小结

7 月是 Apple 端侧 AI 的“软件月”。研究侧，ICML 论文把注意力放在专家缓存、KV 预算、FFN 外存化和扩散解码上，目标都是在 12GB 级内存和约 100GB/s 级带宽下塞进更大的模型、吐出更多 token。产品侧，Siri AI 在公测中形成了 8GB/12GB 两级机型分层，端云分工仍然不透明。外部的 Bonsai 27B 证明，稠密 27B 已能装进 iPhone，但只有 11 tok/s，而且会降频，带宽与散热依旧是天花板。财报中的存储涨价与先进制程紧张，则解释了接下来 M6/A20 Pro 为什么选择加位宽、加 NE 并发，而不是加内存容量。

## 3. 联发科、三星、谷歌、PC 与 WAIC：财报月加展会月

7 月是非高通、非苹果阵营的“财报月 + 展会月”，不是新品月：联发科、华为、小米的新一代手机 SoC 都放在 9 月前后，本月真正落地的芯片只有三星 Galaxy Z Flip8 搭载的 Exynos 2600（2025 年 12 月已发布的 2nm GAA 芯片首次进入折叠屏）。真正有信息量的是三份财报：[台积电](https://anysilicon.com/news/tsmc-q2-2026-earnings-ai-demand-drives-revenue-as-2nm-begins-to-scale/)手机营收占比降到 22%、N2 首次贡献 3% 晶圆营收；[联发科](https://www.mediatek.com/hubfs/MediaTek%20Assets/Pdfs/Quarterly%20Earnings%20Release/2026/Quarterly%20Earnings%20Release-2026Q2/Prepared%20remarks.pdf)手机业务同比下滑 20%，同时预告第三季度推出 2nm“Agentic AI”旗舰 SoC；[Arm](https://newsroom.arm.com/news/arm-q1-fye27-results)版税同比增长 22%，但增量主要来自数据中心。结论是：**存储涨价压缩了手机 BOM，端侧 AI 的增量被挤向两头**。一头是旗舰手机 SoC，另一头是 PC 和边缘盒子这类“大内存端侧”，后者在 WAIC 上第一次给出了“122B 模型、50 tokens/s、30W 整机”这样的绝对数字。

### 一、财报：手机变成“被挤压的端侧”

| 公司（日期） | 关键数字（官方口径） | 与端侧 AI 相关的表述 |
|---|---|---|
| 台积电 Q2（7/16） | 营收 402.0 亿美元，环比 +12.0%；HPC 占 66%，手机占 22%（Q1 为 26%）；N2 占晶圆营收 3%，3nm 占 30% | Q3 指引 446～458 亿美元；N2 爬坡预计拉低毛利率 3～4 个百分点（[AnySilicon](https://anysilicon.com/news/tsmc-q2-2026-earnings-ai-demand-drives-revenue-as-2nm-begins-to-scale/)） |
| Intel Q2（7/23） | 营收 161 亿美元，同比 +25%；客户端部门改名 CCPG（客户端计算与物理 AI），营收 89 亿美元，同比 +13% | 部分 Core Ultra Series 3（Panther Lake）进入 18A 大规模量产；超过 130 家客户采用或测试 Series 3 做边缘 AI 和机器人；通稿未提 Nova Lake 和 AI PC（[Intel](https://www.intc.com/news-events/press-releases/detail/1776/intel-reports-second-quarter-2026-financial-results)） |
| Arm FQ1 FY27（7/29） | 营收 12.89 亿美元，同比 +22%；版税 7.15 亿美元，同比 +22% | 数据中心版税同比翻倍以上；版税费率提升来自 Armv9 和 CSS；RTX Spark 是“首个基于 Arm CSS 的 Agentic PC 平台”（[Arm](https://newsroom.arm.com/news/arm-q1-fye27-results)） |
| 三星电子 Q2（7/30） | 营收 171.5 万亿韩元，营业利润 89.5 万亿韩元（DS 部门 89.2 万亿） | System LSI 受旗舰淡季和中国手机需求疲软影响；拿下下一代旗舰 SoC 订单；Foundry 下半年量产第二代 2nm 手机产品（[Samsung](https://news.samsung.com/my/samsung-electronics-announces-second-quarter-2026-results)） |
| 联发科 Q2（7/31） | 营收 1,522 亿新台币；手机环比 -14%、同比 -20%，占营收 41%；智慧边缘平台同比 +26%，占 53% | 全年手机出货预计下滑约 15%；Q3 推出 2nm 旗舰 SoC，主打 Agentic AI；入门级产品提供“内存使用效率”技术；RTX Spark 年底旺季上市 |

几个值得工程侧注意的点：

- **台积电手机占比下降不等于手机芯片萎缩**。HPC 环比 +20%，手机环比 -4%，主要是分母在变大。N2 第一次出现在营收结构里（3%），时间点与联发科、苹果、高通的 2nm 旗舰同时进入量产吻合。毛利率被拉低 3～4 个百分点，说明 N2 初期晶圆成本很高，这部分成本最终会落到 9 月旗舰机的 BOM 上。
- **联发科第一次在财报里把“手机端侧 AI”的卖点从 TOPS 换成了 Agentic AI**，并把“入门机的内存使用效率”列为卖点。在 DRAM 涨价背景下，这实际是在说：中低端机不会为端侧大模型多配内存，端侧 LLM 的普及节奏会放慢，资源集中到旗舰。
- **Arm 的增长重心明显偏向云端**。官方新闻稿完全没有给出手机数字；媒体（Motley Fool 转述）称版税增长展望下调的原因是“手机内存价格”。对端侧而言，Lumex/SME2 的版税红利已经计入基数，不再是增长弹性的来源。

### 二、三星 Unpacked（7/22）：Exynos 2600 首进折叠屏，AI 卖点仍是云端 Agent

[三星官方首发稿](https://news.samsung.com/global/galaxy-unpacked-july-2026-a-first-look-at-galaxy-z-fold8-ultra-galaxy-z-fold8-and-galaxy-z-flip8)确认，Z Fold8 Ultra 和 Z Fold8 搭载“Snapdragon 8 Elite Gen 5 for Galaxy”。Z Flip8 的芯片在[德国规格页](https://news.samsung.com/de/samsung-galaxy-z-fold8-ultra-fold8-und-flip8-fur-jeden-lifestyle-ein-faltbares-gerat)写的是 Exynos 2600；媒体报道称美国版仍用骁龙。官方 AI 演示（Gemini Notebook、用 Gemini 从照片订酒店、Now Brief 上 FlexWindow）都没有说明哪些在端侧运行，NPU 数字也一个没给。

| 项目 | Exynos 2500（Flip7） | Exynos 2600（Flip8） | 口径 |
|---|---|---|---|
| 工艺 | 3nm GAA | 2nm GAA（SF2） | 官方 / [TechInsights](https://techinsights.com/blog/samsung-exynos-2600-2nm-sf2-process-analysis) |
| CPU | 10 核 | 10 核：1×C1-Ultra + 3 + 6，Armv9.3 + SME2，性能 +39% | [官方](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2600/) |
| NPU | — | 生成式 AI 性能 +113%（芯片级）；整机宣传 +41%（对比 Flip7） | 官方芯片页 / 越南媒体转述 |
| 散热 | — | Heat Path Block，热阻 -16% | 官方 |
| 内存 | 12GB | 12GB（LPDDR 规格未披露） | 媒体 |
| 媒体实测 | — | 安兔兔约 318.8 万；Asphalt 约 113 FPS，约 10 分钟后降频 | [Di Động Việt](https://didongviet.vn/dchannel/danh-gia-hieu-nang-samsung-galaxy-z-flip8/) |

+113% 和 +41% 并不矛盾，前者是芯片级生成式 AI 指标，后者是整机对比口径。两者的测试模型和精度都未披露。真正的约束是 12GB 内存：扣掉系统和常驻应用后，留给端侧模型的空间大致只够 3～4B 的 INT4 模型（推算）。所以 Flip8 的 Galaxy AI 仍是“端侧小模型 + 云端 Gemini”的分工，[edaily](https://en.edaily.co.kr/news/eda202607235631) 也把这次发布称为 System LSI 竞争力的“试金石”。

### 三、谷歌：7 月只有软件栈动作

Tensor G6 放在 8 月，7 月谷歌在端侧只有一件事：7 月 9 日发布 [LiteRT.js](https://developers.googleblog.com/litertjs-googles-high-performance-web-ai-inference/)，把原生 LiteRT 运行时通过 WebAssembly 带进浏览器。它有三条后端：CPU 走 XNNPACK（多线程 + relaxed SIMD），GPU 走 ML Drift/WebGPU，NPU 走 WebNN（Chrome/Edge 实验性，评测时经 CoreML 调用 Apple NPU）。官方称在经典 CV 和音频模型上，CPU 和 GPU 推理都比其他 Web 运行时快最多 3 倍；WebGPU/WebNN 比纯 CPU 快 5～60 倍，测试设备为 M4 MacBook Pro。LLM 不在 LiteRT.js 本体，而是由单独的 LiteRT-LM.js 负责。意义在于，“同一份 .tflite 模型跑遍 Android、iOS、Web、AI PC”的路线又补上了浏览器这一块，但 Web 端 NPU 依赖 WebNN，短期内仍是实验特性。

### 四、PC：RTX Spark 驱动落地，Intel 18A 放量

- **NVIDIA RTX Spark（原 N1X）**：6 月 Computex 已发布，规格为 20 核 Arm CPU（10×X925 + 10×A725）、6,144 CUDA 核 Blackwell GPU、128GB LPDDR5X、约 300GB/s、FP4 约 1 PFLOPS（媒体转述）。7 月 18 日，[IT 之家](https://www.ithome.com/0/978/599.htm)报道 Windows 11 Arm64 原生驱动 616.00 上线，驱动中出现两档 N1X 配置（6,144 和 5,120 核），以及一个使用 DLA 设备 ID 的“NVIDIA NPU”条目。联发科在财报中确认产品“年底旺季上市”。
- **Intel**：Panther Lake 部分型号在 18A 进入大规模量产，18A-P 进入风险量产；Nova Lake 在财报中没有出现。
- **AMD / 微软**：本窗口内没有新的端侧 NPU 产品或 Copilot+ 平台公告。

### 五、WAIC 2026（7/17–20）：边缘侧第一次给出绝对 tokens/s

| 厂商（日期） | 产品 | 官方/媒体给出的数字 | 能跑多大模型 |
|---|---|---|---|
| 后摩智能（7/19 报道） | M50 存算一体芯片 | 160 TOPS @10W | 30B～120B；联想 AI 主机 P7：122B、50 tokens/s、整机 30W；长城 N90 Pro 笔记本：35B、30 tokens/s（[钜亨](https://hao.cnyes.com/post/259837)） |
| 瑞芯微（7/17–18） | RK35xx + RK1828 协处理器 | Gemma4 首 token 最低 169.93ms | 2B～7B；下一代协处理器 Q3 发布（[news18a](https://english.news18a.com/news/english_276742.html)） |
| 爱芯元智（7/20） | 元曦 A 系列推理卡 / 具身大脑控制器 | 超 1000 TOPS / 1500 TOPS，带宽约为“行业领先产品的 2 倍” | 未披露（[IT 之家](https://www.ithome.com/0/978/841.htm)） |
| 阶跃星辰（7/13） | STEPX Neo 手机 + Step Edge 端侧模型族 | 硬件规格未披露 | 未披露（[新华网](https://www.news.cn/digital/20260714/8354f82874ee4741ad1fd9ef716112ef/c.html)） |
| 荣耀 × 阿里（7/18） | Robot Phone + 千问手机 Agent 方案 | 1,000+ 场景评测、200+ 工具 | 端/云划分未披露（[中证网](https://www.cs.com.cn/ssgs/01/2026/07/19/detail_2026071910025313.html)） |

后摩的数字最值得推敲。30W 整机跑 122B 模型达到 50 tokens/s，如果是稠密模型，INT4 权重约 61GB，每秒需要读约 3TB，远超任何端侧内存带宽。因此几乎可以肯定是**激活参数在 10B 左右的 MoE 模型**（模型名未披露，属于推断）。这与[RTX Spark](https://tomshardware.com/tech-industry/computex-2026-day-zero-wrap-up-nvidia-launches-rtx-spark-superchip-assault-on-laptop-and-desktop-markets-intel-readies-xeon-6)“128GB 跑 120B”的叙事一致：**端侧大模型的容量看总参数，速度看激活参数 × 带宽**。

另外，7 月 15 日网信办公示了首批 7 款手机[端侧生成式 AI 服务备案](https://stock.10jqka.com.cn/20260715/c678203208.shtml)，包括 Apple 智能、华为小艺、OPPO AndesGPT、vivo 蓝心端侧、小米澎湃 AI、三星盖乐世 AI、努比亚豆包，荣耀不在首批名单。这为国内手机端侧模型的上线扫清了合规障碍。

### 六、模型容量对照（7 月窗口内可核实的口径）

| 平台 | 内存 / 带宽 | 能跑多大模型 | 口径 |
|---|---|---|---|
| Galaxy Z Flip8（Exynos 2600） | 12GB / 未披露 | 未披露；推算 INT4 3～4B 级 | 推算 |
| RTX Spark | 128GB / 约 300GB/s | 约 120B（媒体）；稠密 70B INT4 理论 decode 上限约 8 tokens/s | 媒体 + 推算 |
| 后摩 M50 整机（联想 P7） | 未披露 | 122B、50 tokens/s、30W | 厂商 / 媒体 |
| 后摩 M50 笔记本（长城 N90 Pro） | 未披露 | 35B、30 tokens/s | 厂商 / 媒体 |
| 瑞芯微 RK1828 协处理器 | 未披露 | 2B～7B，Gemma4 首 token 169.93ms | 厂商 |

### 七、未发生的事

- 联发科、华为、小米本月都没有发布手机 SoC。联发科的 2nm 旗舰定在 Q3；华为 HDC 2026 在 6 月 12–14 日（窗口外），麒麟“逻辑折叠”数据来自 5 月论文；小米新一代玄戒在 8 月财报会上才确认“即将发布”。
- 紫光展锐本月没有新芯片公告，最近一次是 5 月发布的 4nm N9 端边 AI 平台。
- 华为在 WAIC 展出昇腾 950 超节点（1,024 颗 NPU、FP4 2 EFLOPS），属于数据中心产品，不计入端侧。

### 八、对端侧 AI 工程的含义

1. **内存配置会比 NPU 算力更早成为瓶颈。** 联发科管理层预计全年手机出货下滑约 15%，并把入门机的卖点改成“内存使用效率”。三星 Q2 通稿也说零部件成本上升和消费疲软会延续到下半年。可以预期，2026 下半年中端机的内存不会增加，部分机型可能缩减。面向中端机的端侧模型应按 8～12GB 内存预算设计：权重 INT4 甚至更低、KV Cache 压缩、按需加载。不要指望硬件来兜底。
2. **“TOPS → Agentic AI”的叙事切换已进入财报。** 联发科用“规划、推理、执行、自我修正”来描述算力需求，Arm 把 RTX Spark 称为“Agentic PC 平台”，Intel 把客户端部门改名为“客户端计算与物理 AI”。这三家都没有给出端侧 Agent 的量化指标（任务成功率、单任务能耗、端云调用比例）。评估供应商方案时，应主动索要这些数据，而不是只看 TOPS。
3. **大内存端侧的单位成本正在被验证。** 后摩 M50 在 10W 芯片功耗下给出 160 TOPS，联想 P7 整机 30W 跑 122B、50 tokens/s；RTX Spark 用 128GB LPDDR5X、约 300GB/s 做 Windows 本地推理。两者都依赖 MoE 的“大总参、小激活”。对需要本地私有化知识库或长上下文 Agent 的场景，这类“端侧服务器”可能比旗舰手机更早落地。但两者都还没有独立第三方的 tokens/J 实测，现阶段应视为厂商口径。
4. **软件栈继续向“一次转换、多端部署”收敛。** LiteRT.js 补上浏览器端，加上此前的 LiteRT-LM（Android、iOS、WebGPU）和 OpenVINO 后端，谷歌已覆盖手机、PC、Web 三类目标。Exynos 2600 官方强调支持 ExecuTorch，瑞芯微用 RKNN3 适配 Gemma4/Qwen3.5。模型侧的主流选择也越来越集中，Gemma 4 和 Qwen 3.5 成为各家芯片首发适配的事实标准。

### 小结

7 月的主线不是新芯片，而是**成本**。台积电 N2 刚贡献 3% 营收就要拉低毛利率 3～4 个百分点，存储涨价让联发科手机业务同比少了 20%，Arm 的增量转向数据中心。端侧 AI 因此分成两条路：手机端（Exynos 2600、9 月的天玑和麒麟）继续在 12～16GB 内存里做“小模型 + 云端 Agent”；PC 和边缘盒子（RTX Spark、后摩 M50）用数十 GB 到 128GB 的内存加 MoE，第一次把百亿级模型的 tokens/s 写进了宣传稿。下个月看 Tensor G6 和小米玄戒能否给出绝对值。

## 4. 低功耗、存内计算与内存：内存越来越贵，大家都在少读字节

7月的低功耗AI硬件可以概括为两点：**内存越来越贵，各家都在想办法少读字节。** 三星和SK海力士Q2利润创纪录，DRAM价格在2Q26暴涨之后，3Q26仍要再涨13–18%。WAIC 2026上，存算一体（后摩M50）、3D近存（东方算芯DF1000）和具身大脑芯片（爱芯1500 TOPS、神玑800 TOPS）集中亮相。NVIDIA用Jetson T3000把Thor的容量和功耗砍半，但保留了273GB/s带宽。眼镜和MCU这一层在7月没有新硅片，变化主要在资本层面：Microchip收购Hailo，Syntiant递表上市，BrainChip首批AKD1500到货。

### 一、内存：涨幅收敛，但端侧拿不到更多容量

| 指标 | 数值 | 口径/来源 |
|---|---|---|
| 2Q26移动DRAM合约价 | LPDDR5X ≥+78–83%，LPDDR4X ≥+70–75% | [TrendForce 5月](https://wantrich.chinatimes.com/news/20260515900291-420101) |
| 3Q26 DRAM / NAND合约价 | +13–18% / +10–15%（eMMC/UFS涨幅较小） | [TrendForce 7/3](https://iconnect007.com/article/150656/ai-server-demand-keeps-memory-prices-up-in-3q26-but-gains-moderate/150653/pcb) |
| 供需缺口 | DRAM缺口从1–2%继续扩大；NAND要到2H27才转宽松 | [TrendForce 7/30（IT之家）](https://www.ithome.com/0/983/762.htm) |
| 三星Q2 | DS部门营业利润89.2万亿韩元，占全公司99.7%；DRAM ASP +40%中段，NAND +60%高段 | [Digital Today](https://www.digitaltoday.co.kr/en/view/87308/samsung-electronics-chip-unit-makes-up-99-7-percent-of-company-operating-profit) |
| 三星展望 | HBM4在Q3环比增长3倍以上；CFO称2027年供给比2026年更紧 | [Blocks & Files](https://blocksandfiles.com/flash/2026/07/31/for-samsung-hbm-is-the-gift-that-keeps-on-giving/5281709) |
| SK海力士Q2 | 营收79.3万亿、营业利润60.5万亿韩元（利润率76%，低于预期）；HBM4量产出货；约10家客户签订长约 | [Xenospectrum](https://xenospectrum.com/en/sk-hynix-q2-hbm-lta/) |

这些数字反映的是**利润流向**。三星整机部门（DX）营收环比下降9%，内存部门却拿走了几乎全部利润。SK海力士也承认，内存紧缺导致手机和PC销量阶段性回落。TrendForce 5月预计12GB会成为高端机主流，16GB机型占比回落。按这个容量推算，扣除系统占用后，手机能常驻的模型约为7–8B INT4，或者30B级MoE中的热专家子集。2027年供给会更紧，旗舰机RAM容量大概率停在12–16GB，端侧模型的规模将主要由内存成本决定，而不是由NPU算力决定。

**LPDDR6和UFS 5.0：带宽在上升，但离量产机还有距离。** SK海力士1c LPDDR6计划2H26量产，[据报首供小米](https://www.ithome.com/0/982/326.htm)，厂商称速度提升33%、功耗降低20%以上。[长鑫LPDDR6](https://www.yicai.com/news/103301625.html)接近验证尾声，设计速率12800Mbps，与SoC搭配时以10667Mbps起步，采用1295-ball POP封装。按96bit位宽计算，10667Mbps约对应113.8GB/s，12800Mbps约对应136.5GB/s（已扣除LPDDR6的256/288元数据开销），8B INT4的Decode上限分别约为25和30 t/s（推算）。[铠侠UFS 5.0](https://www.kioxia.com/en-jp/business/news/2026/20260729-2.html)7月29日进入商用样品阶段，读10GB/s、写9.0GB/s，年底量产。即使如此，闪存带宽仍比LPDDR6低一个数量级：30B-A3B INT4每个token激活约1.65GB，如果全部从闪存读取，上限只有约6 t/s。所以闪存只适合存放冷专家，热专家必须常驻DRAM。

**粗算一下BOM账。** 把2Q26 LPDDR5X涨幅（+78–83%）与7月TrendForce给出的3Q26 DRAM整体涨幅（+13–18%）连乘，LPDDR5X到3Q26约为1Q26的2.0–2.2倍（推算；两个数字口径不同，8月TrendForce单列的移动DRAM涨幅为+8–13%，按此口径约1.9–2.1倍）。也就是说，同样的12GB，半年内成本翻了一倍左右，这部分增量要由整机厂消化。对端侧AI的影响是：手机厂很难为了跑更大的本地模型再加4GB RAM，只能在现有容量里优化，例如把KV Cache量化到INT8/INT4、用滑动窗口限制上下文、MoE只常驻热专家、让模型与系统共享权重页。这也是7月各家硬件方案都在强调“每token字节数”而不是TOPS的原因。

### 二、存算与近存：WAIC上的三种做法

| 方案 | 计算放在哪 | 关键数字（口径） | 模型（口径） | 瓶颈 |
|---|---|---|---|---|
| [后摩M50](https://finance.eastmoney.com/a/202607193811732690.html) | 存算IPU（天璇），权重放外部内存 | 160 TOPS INT8@10W；最大48GB、153.6GB/s（2025年口径）；2026年2月量产 | 联想P7整机30W，122B@50 t/s；长城N90 Pro 35B@30 t/s（厂商/媒体） | 外部153.6GB/s带宽 |
| [东方算芯DF1000](https://xenospectrum.com/dfsx-df1000-3d-dram-14nm/) | 14nm逻辑与DRAM 3D混合键合，亚μm间距 | 6.4TB/s；BF16 520 TFLOPS；Scale-up 900GB/s；容量和TDP未披露 | 未披露 | 键合良率（两层90%×90%=81%为假设）、容量 |
| [瑞芯微RK182X](https://m.gelonghui.com/news/5268125) | 协处理器，集成3D堆叠DRAM | 20 TOPS（代理商口径）；WAIC展示车载、机器人、NAS等方案；2H26放量 | 3B/7B（券商转述），0.5–8B（代理商） | 小容量，只适合小模型 |
| [爱芯具身大脑控制器](https://stock.10jqka.com.cn/20260720/c678288587.shtml) | 未披露 | 1500 TOPS；带宽“约为行业领先的2倍” | 兼容VLA与世界模型 | 规格未披露，无法评估 |

**第一，存算一体解决的是“算得省”，不解决“读得快”。** M50的160 TOPS@10W约合16 TOPS/W（INT8峰值），但LLM权重仍放在外部内存里，解码速度取决于153.6GB/s的带宽。拿厂商数字反推：联想P7跑122B模型达到50 t/s，意味着每个token最多读约3GB。这只有一种解释可行：模型是激活约10B的MoE，并且平均量化到约2.4bit以下；否则就是用了多颗M50或投机解码（推算，厂商未披露模型和位宽）。长城N90 Pro跑35B模型30 t/s，对应每个token不超过5GB，与30B级MoE（激活约3B）的特征一致。换句话说，**存算芯片能跑“千亿参数”，靠的是MoE的稀疏激活和低比特量化，而不是存算本身。** 虎嗅专访中后摩CEO的说法也比较克制：token成本“理论上可以降一个数量级，目前做不到10倍，但几倍可以争取”。

**第二，3D近存在中国已从论文进入产品。** DF1000用14nm逻辑die加混合键合做到6.4TB/s，带宽是H200的1.33倍，用成熟制程换带宽。这条路线与8月小米O100、d-Matrix Raptor相同。但容量和TDP都未披露，6.4TB/s能支撑多大的模型无法判断。DF2000（4Q26）计划做到15TB/s，DF3000（4Q27）计划做到20TB/s。

**第三，名单里有缺席者。** 知存、苹芯、九天睿芯在7月没有检索到新品发布。知存5月披露三年研发投入超15亿元，并预计2027年LLM芯片将占其出货量的80%（[同花顺](https://news.10jqka.com.cn/20260527/c677022517.shtml)），但面向LLM的产品尚未公开规格。

### 三、按功耗档位看：7月新品能跑多大的模型

| 功耗档 | 7月相关产品 | 算力/内存 | 能跑什么（口径） |
|---|---|---|---|
| μW–mW常开 | Syntiant NDP（[S-1](https://www.sec.gov/Archives/edgar/data/0001718728/000119312526296426/ck0001718728-20260706.htm)）、BrainChip AKD1500（[首批2000颗](https://www.fool.com.au/2026/07/27/brainchip-posts-q2-cash-chips-hit-commercial-production/)） | 毫瓦/亚毫瓦；片上存储 | 唤醒词、VAD、事件检测，不跑LLM |
| 百mW级眼镜 | [WAIC眼镜](https://www.bjnews.com.cn/detail/1784469956169987.html)：千问S1（AR1+协处理器，51g，续航7h）、讯飞（40g）、李未可（26g） | 芯片多数未披露 | 本地LLM均未披露，大模型走手机或云 |
| 2–5W | [Hailo-10H](https://hailo.ai/products/ai-accelerators/hailo-10h-ai-accelerator/)（并入Microchip） | 40 TOPS INT4@2.5W；LPDDR4/4X | 推算1–3B INT4 |
| ~10W | 后摩M50 | 160 TOPS；48GB/153.6GB/s | 30–120B（厂商），依赖MoE |
| 40–70W | [Jetson T2000/T3000](https://blogs.nvidia.com/blog/2026/07/15/jetson-thor-robotics-edge-ai-agent/) | 400/865 FP4 TFLOPS；16GB / 32GB、273GB/s | T3000：8B INT4上限约60 t/s，可装约50B INT4（推算） |
| 机器人域控 | [地瓜S600](https://damodev.csdn.net/6a5a1ef610ee7a33f28e84d6.html) 560 TOPS；[神玑NX9031U](https://cnevpost.com/2026/07/17/nio-shenji-showcases-chips-waic-2026/) 800 TOPS；爱芯1500 TOPS | 内存多未披露 | S600：Qwen3-VL-8B、Pi0，操作模型约10 FPS |

这张表最值得注意的是Jetson T3000：它的FP4算力只有T5000的42%，内存只有1/4，**带宽却没降，仍是273GB/s**。NVIDIA同时推出Jetson agent skills，自动做内存优化：UBTech等客户从AGX Orin 64GB降到32GB（最多省15GB），SandStar从16GB降到8GB。在DRAM涨价时，“少用8–15GB内存”可以直接折算成BOM节省。国产机器人芯片的TOPS数字已经很高（560–1500），但大多不公布带宽和容量。S600操作模型约10 FPS，说明VLA的瓶颈仍在内存，而不在TOPS。

**产业格局方面**，[Microchip收购Hailo](https://ir.microchip.com/news-events/press-releases/detail/1406/microchip-technology-signs-definitive-agreement-to-acquire-hailo)（客户100+、开发者1万+，条款未披露，称对财务“无重大影响”），加上此前NXP收购Kinara，2–5W的独立NPU正在被MCU/MPU厂商并入自己的产品组合。Syntiant的S-1显示，公司业务已与2024年底收购的Knowles MEMS麦克风深度绑定（SiSonic在2025年出货超10亿颗），2025年净亏损6090万美元，2026Q1营收6450万美元。BrainChip首轮产量从约7万颗下调到约6万颗。纯μW级AI芯片仍然很难独立支撑一家公司。ST、NXP、Infineon、Renesas在7月都没有检索到MCU NPU新品。

### 四、眼镜与具身：两头的约束正好相反

**眼镜受电池限制。** 千问S1用287mAh双电池（可热插拔）实现综合续航7小时（[IT之家](https://www.ithome.com/0/937/763.htm)、[新京报](https://www.bjnews.com.cn/detail/1784469956169987.html)），按常见3.8V电芯估算，总能量约2.2Wh，平均功耗只有约300mW（推算）。AR1这一级的SoC在相机、编码和显示上已经用掉大部分预算，留给本地LLM的余量几乎为零。因此WAIC上十余家眼镜厂商都**没有公布本地模型参数**，千问、讯飞、Rokid的大模型能力全部在手机或云端。眼镜的差异化集中在麦克风阵列和降噪（讯飞5气导+1骨导+唇动识别）、重量（14.9–51g）和价格（799–4599元）。Rokid强调“双芯片双系统独立运行”和“端边云协同算力拆分”，这正说明眼镜本地只负责常驻和前处理。在Meta财报中，AI眼镜是Reality Labs Q2营收增长16%（至4.31亿美元）的主要来源，但这个营收规模说明眼镜专用芯片仍缺乏规模经济。

**具身芯片受带宽限制。** 机器人对功耗相对宽容（40–130W），但VLA需要同时满足视觉骨干的带宽和动作头的低延迟。7月新品的TOPS数字都很高：地瓜S600 560 TOPS、神玑NX9031U 800 TOPS（5nm车规，[CnEVPost](https://cnevpost.com/2026/07/17/nio-shenji-showcases-chips-waic-2026/)）、爱芯1500 TOPS，但几乎都没有公布内存带宽。能拿来核算的只有NVIDIA：T3000以273GB/s跑8B INT4的VLM骨干，Decode上限约60 t/s（推算）。S600公开的“操作模型约10 FPS”与此量级相符。车企芯片（神玑）把智驾SoC降一档用于机器人，地瓜把单SoC做成“大脑+小脑+MCU”合一，爱芯则拆成“控制器+AX8910视觉芯片”，三种方案的共同点是在数据路径上减少一次跨芯片搬运。Tesla AI5在7月财报中没有新的公开数字（二手报道称2027年中量产，可信度低），本节不纳入比较。

### 小结

7月的信号很一致。**内存方面**：原厂利润几乎全部来自HBM和服务器，DRAM价格在3Q26继续上涨，CFO称2027年会更紧，端侧RAM容量难以增长。**硬件方面**：存算（M50）、3D近存（DF1000）、3D堆叠DRAM协处理器（RK182X），以及“砍容量、保带宽”的Jetson T3000，都在想办法降低每个token需要读取的字节数。**模型方面**：能在10W跑“百亿到千亿参数”，前提是MoE稀疏激活和低比特量化，厂商tokens/s数字需要按带宽反推核实。眼镜与MCU层7月没有新硅片，资本在整合，而8月Hot Chips的三星LPDDR5X-PIM和小米O100会把“近存”推进到手机级别。

## 5. 顶会论文：decode 决定体验与能耗

**判断：** 7 月窗口内的顶会/预印本信号非常集中——端侧 AI 硬件研究正在从“把 TOPS 做大”转向“把 decode 做省”：多篇独立测量（手机 NPU、Jetson VLM、M5 GPU、AMD AI PC）一致发现**prefill 靠矩阵算力、decode 靠带宽**，NPU 在 decode 上普遍不占优；与此同时，MICRO 2026（10/31–11/4，雅典）录用论文在 7 月集中上 arXiv，PIM/近存、细粒度 DVFS、低比特格式与存储可靠性成为主线。本月窗口内 [ICML 2026](https://icml.cc/Conferences/2026)（7/6–11，首尔）与 [DAC 2026](https://ieee-ceda.org/post/announcement/dac-2026-call-contributions)（7/26–29，Long Beach）召开，但与端侧硬件直接相关的成果以 MICRO/ICCAD 录用论文为主。

换句话说，本月的学术界和工业界都在回答同一个问题：在带宽固定的统一内存上，如何让每个比特只搬一次、每个引擎只做自己擅长的事。

> 说明：日期均为 arXiv v1 真实发布日期；Hot Chips 2026（8/23–25）与 MICRO 正式会议属于后续月份内容，此处不重复。

### 会议背景

- **ICML 2026**（7/6–11，首尔 COEX）：主会以算法为主，与端侧硬件直接相关的成果主要出现在 workshop，例如 ETRI 的小型 VLM 量化工作；高效推理方向的主会论文大多不涉及具体芯片，本节不单独展开。
- **DAC 2026**（7/26–29，首次移师 Long Beach）：窗口内 arXiv 上与端侧 AI 硬件相关的 DAC 论文较少，本节收录 Notre Dame 的 p-MEM；DAC 的 EDA×LLM 方向（如 LLM 生成 RTL）不在本节讨论范围内。
- **MICRO 2026 / ICCAD 2026**：录用通知后，作者在 7 月集中把论文上传到 arXiv，构成本月的主体。MICRO 程序中还有更多 PIM/低比特相关论文，于 8–9 月陆续公开，留到后续月份介绍。
- **工业界**：本月有 AMD（UEP、HeteroMosaic）、SK hynix（StreamDQ、NELSSA）、华为（HiFA4、Sparse by Command）、阿里（CODA）、Google（NeuScale 合作）、长江存储（HEMERA）参与的论文；高通、三星、Meta 在窗口内未见直接相关的端侧硬件论文（Meta 的 [Triton for MTIA](https://arxiv.org/abs/2608.00325) 属于数据中心编程模型，不展开）。

### Top Picks

| 日期 | 论文 | 会议 | 机构 | 关键数字 |
|---|---|---|---|---|
| 07-06 | [Is Your NPU Ready for LLMs?](https://arxiv.org/abs/2607.05475) | arXiv | 清华、北交大 | NPU prefill 1464 tok/s，decode 仅约 23 tok/s；CPU decode 更快 |
| 07-14 | [HeteroMosaic](https://arxiv.org/abs/2607.12839) | MICRO'26 | UIUC、AMD | iGPU+NPU 协同比 llama.cpp 快 2.05×，能耗 −45.3% |
| 07-16 | [CODA](https://arxiv.org/abs/2607.14908) | MICRO'26 | 北大、阿里 | 视频扩散缓存近存化 1.80×/1.74× 能效 |
| 07-17 | [eNPU](https://arxiv.org/abs/2607.16473) | MICRO'26 | UIUC | 组件级 DVFS 能耗 −25.8~35.2%，面积 +3.45% |
| 07-21 | [BaseRT](https://arxiv.org/abs/2607.19438) | arXiv | Base Compute | M5 Pro prefill 比 llama.cpp 6.4×；35B-A3B decode 110.7 tok/s |
| 07-21 | [UEP](https://arxiv.org/abs/2607.19623) | MICRO'26 | AMD | ECC 节省 37.5–62.5%，BF16 读能耗 −17% |
| 07-24 | [Sparse by Command](https://arxiv.org/abs/2607.22038) | MICRO'26 | 港科大、华为诺亚 | FLOPs −66~76%，延迟 2.1–2.4× |
| 07-28 | [DOPS](https://arxiv.org/abs/2607.25498) | MICRO'26 | 北大（推断） | NPU+PIM 动态调度 1.20–2.23× |
| 07-29 | [NELSSA](https://arxiv.org/abs/2607.26633) | MICRO'26 | SK hynix、KAIST | GPU+PNM decode 5.5×、P99 15× |

### 一、测量研究：decode 不是 NPU 的主场

- **手机 NPU 的 phase split（清华/北交大）**：在小米 14/15/17、OnePlus 15（SM8650→SM8850，Hexagon V75→V81）上，Qwen2.5-1.5B W4 的 NPU prefill 由 GENIE 跑到 1213–1464 tokens/s，而 decode 仅约 23 tokens/s；同机 CPU llama.cpp 的 decode 约 52–56 tokens/s。同为 QNN 后端，GENIE 与 MNN 的 prefill 差 1.7×，llama.cpp 的 NPU 后端只有约 110 tokens/s——**框架差异在 NPU 上被放大到 10×**。线程、NPU 休眠延迟与 CPU 轮询的配置不当最多浪费 40% 能耗。[arXiv](https://arxiv.org/abs/2607.05475)
- **端侧 VLM 能耗（UPenn 等，ACM MM'26）**：平均功率几乎是模型常数（<5% 波动），每个输出 token 的耗时是输入 token 的 11–39×；删掉全部视觉 token 最多省 10%，控制输出长度最多省 97%。[arXiv](https://arxiv.org/abs/2607.09520)
- **小型 VLM 分组件量化（ETRI，ICML'26 Workshop）**：Jetson Orin 上 INT4 LLM 主干省显存却让 token 生成**变慢**（反量化开销），MoE 主干比稠密主干更抗 INT4 噪声。[arXiv](https://arxiv.org/abs/2607.08029)
- **手机 NPU 峰值电流（UC Berkeley/Sony）**：Xperia 1 VI（骁龙 8 Gen 3）上，编译器激进融合形成 superlayer，低电量时触发 PMIC 降频；插入 barrier 后峰值电流 3.12 A→1.94 A，延迟仅 +3.76%，DVFS 裕量约 +173 mV。[arXiv](https://arxiv.org/abs/2607.16555)

**解读：** 四项独立研究在不同平台得出一致结论——prefill 是算力问题、decode 是带宽与调度问题。这直接支撑了 HeteroMosaic 的结果：其 decode 归一化 TPS 仅 0.98–1.13×，收益几乎全部来自 prefill。下一代手机 NPU 若想接管 decode，需要动态形状支持与更低的 kernel 启动开销，而不是更高的峰值 TOPS。

从硬件设计角度，还有两点值得注意。第一，**框架是被低估的变量**：同一颗 Hexagon V81、同一个 QNN 后端，GENIE 与 llama.cpp 的 NPU prefill 相差一个数量级，说明厂商闭源算子库（如 MatMul 实现与 layout 转换）本身就是竞争力。这对联发科、苹果等平台的启示是，NPU SDK 的算子覆盖与图编译质量，可能比再加一倍 MAC 阵列更能改善用户体感。第二，**峰值功率开始成为约束**：Sony/Berkeley 的工作说明，编译器为了减少访存而做的激进融合，会把电流集中在极短的时间窗内释放。电池老化或低电量时，PMIC 的保护性降频会让延迟抖动明显变大。今后手机 NPU 编译器的代价模型除了延迟和 DRAM 流量，还需要加入 PAPR/di/dt 这一项。

### 二、异构调度：把 iGPU、NPU、PIM 当一个系统

| 工作 | 平台 | 方法 | 收益 |
|---|---|---|---|
| [HeteroMosaic](https://arxiv.org/abs/2607.12839)（MICRO'26） | Ryzen AI 7 350 / HX 370 / Max+ 395 | 异构 roofline + 因果 micro-batch | 比 llama.cpp 2.05×，能耗 −45.3% |
| [BaseRT](https://arxiv.org/abs/2607.19438) | Apple M5 Pro 48GB | GEMM 走每核 Neural Accelerator，decode 走专用 kernel | prefill 对 llama.cpp 6.4×、对 MLX 3.9× |
| [DOPS](https://arxiv.org/abs/2607.25498)（MICRO'26） | Ascend 910B + AiM GDDR6-PIM | 动态算子放置 + 权重布局仲裁 | 1.20–2.23×，再 +1.28–1.33× |
| [CODA](https://arxiv.org/abs/2607.14908)（MICRO'26） | RTX 4090 + DIMM-NMP | 缓存算子近存化 + CFG 交错 | 1.80× / 1.74× 能效 |

BaseRT 给出了本月最直观的“端侧能跑多大模型”数据：M5 Pro 上 Qwen3.6-35B-A3B Q4 decode 110.7 tokens/s，Qwen3-30B-A3B Q4 105.1 tokens/s，而稠密 Qwen3.6-27B Q4 只有 18.1 tokens/s——**MoE 的小激活参数比稠密模型更适合带宽受限的端侧**（厂商自测，非同行评审）。DOPS 则指出 NPU 分形布局（ZZ/NZ/ZN）与 PIM bank 对齐布局之间存在冲突，这会是 LPDDR-PIM 进入手机 SoC 后软件栈必须解决的问题。

这四项工作的共同点是：**不再假设“整模型放某个设备”**，而是在算子、micro-batch 乃至权重块粒度上做放置。HeteroMosaic 的异构 roofline 给出了一个简单的判据：iGPU 越弱，NPU 协同的理论上界越高（AI 7 350 约 3×，Max+ 395 只有约 1.25×）。这意味着在 Wildcat Lake、天玑中端这类 GPU 规模有限的芯片上，异构调度的边际收益反而最大。BaseRT 的做法则相反：苹果把矩阵单元直接放进 GPU 核内，从而绕开“GPU 与 ANE 之间搬数据”的开销。这两条路线（独立 NPU + 精细调度，或 GPU 内嵌矩阵单元）孰优孰劣，取决于统一内存带宽与驱动栈的成熟度。CODA 的“edge”指带 24 GB 独显的工作站，与手机差距较大，但它揭示的问题在手机上同样存在：生成式视频的跨步缓存远大于片上存储，缓存路径属于带宽密集型，适合交给内存侧计算。

### 三、低比特与 CPU 路径

- **PolyQ（UCI，ICCAD'26）**：逐通道 {2,3,4,8,16} bit 分配，编译期把通道聚成同比特块；3 bit 预算下 PPL 改善 2.4–32.1%，重排流量 −70.8%，能耗/token 开销 <2%，覆盖工作站、笔记本和手机三类 CPU。[arXiv](https://arxiv.org/abs/2607.14618)
- **ExaGEMM（UCI，ICCAD'26）**：只新增寄存器内 select/feed 机制，即可在 SIMD 上做 LUT 低比特 GEMM；比纯软件快 13.29×，候选空间剪枝 99.2%。[arXiv](https://arxiv.org/abs/2607.14622)
- **HiFA4（华为）**：QKᵀ 与 PV 都用昇腾 HIF4 4-bit Cube GEMM，Qwen3-8B 的 MMLU 回退减少 57%；延迟收益（−35.4%）为模型推算，尚未上板。[arXiv](https://arxiv.org/abs/2607.04302)

**解读：** 低比特方向在 7 月呈现“两头走”的态势。一头是 **CPU 回退路径**：UCI 的 PolyQ 与 ExaGEMM 分别从编译器和 ISA 两侧，把 2–4 bit 的混合精度做到 CPU 上可预测地执行。这类工作的现实意义在于，新模型发布后，NPU 往往需要数周到数月才能完成算子适配，CPU 是首日可用的后端。另一头是 **attention 的 4-bit 化**：权重 4-bit 已经普及，而 QKᵀ/PV 这两个随上下文增长的 GEMM 仍多用 FP16/BF16；HiFA4 指出，“归一化因子与 PV 所用精度不一致”会带来系统性偏差，这一结论对任何 FP4/INT4 attention 实现都适用。与此相对，ETRI 在 Jetson 上的实测提醒我们：没有原生低比特 MAC 时，INT4 反而更慢。

### 四、内存、PIM 与可靠性

- **SK hynix 两连发**：[StreamDQ](https://arxiv.org/abs/2607.08993) 在 HBM base die 中做内联反量化（每个 DQB 0.127 mm²/0.355 W @12nm，GEMM 7.08×）；[NELSSA](https://arxiv.org/abs/2607.26633)（MICRO'26，与 KAIST 合作）用真实 CXL-PNM 设备承接长上下文稀疏 attention，decode 5.5×、P99 15×。两篇都是数据中心场景，但“内存侧做格式转换 / 长 KV 交给近存”的分工可直接映射到 LPDDR-PIM。
- **AMD 不等差错保护（MICRO'26）**：FP16/BF16/FP32 分别有 6/4/15 个低位可不保护，ECC 节省 37.5–62.5%，非关键分区降压后 BF16 读能耗 −17%。[arXiv](https://arxiv.org/abs/2607.19623)
- **模拟 CIM 上的 KV（北航/港大等）**：sink token 与最近 token 放数字路径，噪声下 PPL 从 33.91 降到 11.95（干净基线 11.06）。[arXiv](https://arxiv.org/abs/2607.29076)
- **HEMERA（北大/长江存储，ICCAD'26）**：Mamba-2 SSD 改写为流式递归，DCIM + 3D NAND；能效达 A100 的 12.2–27.0×，但计算 die 为 113.96 mm²/18.02 W，离手机功耗预算仍远。[arXiv](https://arxiv.org/abs/2607.22022)
- **p-MEM（Notre Dame 等，DAC'26）**：内存直接按 μ/σ 采样，>1000 GSa/s/mm²，为端侧不确定性估计提供硬件原语。[arXiv](https://arxiv.org/abs/2607.02465)

**解读：** 7 月是存储厂商论文最密集的一个月。SK hynix 的两篇工作分别对应 PIM 的两种商业形态：一种是改 base die、对主机透明的“custom HBM”，另一种是挂在 CXL 上、需要软件显式调度的 PNM 设备。AMD 的 UEP 工作则从另一个角度切入，主张“比特并不同等重要”，用可靠性裕量换取 SRAM 能效。对端侧而言，LPDDR 的 ECC 与低压运行同样可以按数据类型分级。模拟 CIM 上 KV 保护的研究说明，CIM 要从静态权重扩展到动态 KV，就必须做 token 级的精度分级；而 HEMERA 这类 NAND + CIM 方案在能效上的数字很亮眼，但面积与功耗规模更接近边缘服务器，而非手机。

### 五、NPU 微架构与具身负载

- **eNPU（UIUC，MICRO'26）**：把 NPU 流水线拆成组件级 V/f 域，ISA 支持亚微秒 DVFS，能耗 −25.8~35.2%（TPUv4 参照，面积 +3.45%）。同组 [NeuScale](https://arxiv.org/abs/2607.16488)（UIUC + Google）研究多代异构 NPU 池的自动扩缩容。[arXiv](https://arxiv.org/abs/2607.16473)
- **Sparse by Command（港科大/华为诺亚，MICRO'26）**：任务指令驱动 tile 级掩码，并下沉到 ISA；在 CARLA 驾驶任务上，FPGA 原型延迟 9.12→3.74–4.44 ms，能耗 263→108–128 mJ。[arXiv](https://arxiv.org/abs/2607.22038)

**解读：** eNPU 与 Sparse by Command 都把**软件已知的信息下沉到 ISA**：前者让编译器在指令中直接设置各组件的 V/f，后者让任务指令携带 tile 掩码。这种“编译期/任务期决策，硬件零开销执行”的模式，非常适合端侧 NPU：decode 阶段脉动阵列利用率低而内存接口繁忙，可以单独给阵列降压；VLA/具身模型一个主干服务多条指令，可以按指令关掉大部分通道。代价是电压域、电源轨和 ISA 兼容性带来的面积与验证成本，在手机 SoC 上需要谨慎权衡。

### 小结

1. **decode 决定体验与能耗**：手机、Jetson、M5、AI PC 四类平台的独立数据一致表明，NPU 的价值目前集中在 prefill，decode 需要带宽、动态形状支持与调度上的改进。
2. **内存厂商深度入场**：SK hynix（StreamDQ、NELSSA）、AMD（UEP）、长江存储（HEMERA）均在 7 月发表工作，“在内存侧做计算或格式转换”正从学术走向产品路线。
3. **对产品的含义**：手机/PC 厂商短期内最划算的投入是软件，包括 prefill-NPU/decode-CPU（或 GPU）的阶段拆分、框架算子质量，以及考虑峰值电流的编译策略，这几项可以在现有芯片上直接带来 1.5–2× 的体验改善。中期看，在 LPDDR 侧做反量化或 attention 的 PIM 方案，以及组件级 DVFS，有望把 decode 能效再提升一个台阶；MoE 的“大总参、小激活”则会持续推高端侧对内存容量的需求。
4. **局限**：本月多数结果来自仿真或云侧平台，真正在手机 SoC 上流片或实测的工作仍少；DAC/ICML 主会中与端侧硬件直接相关、且 arXiv v1 落在窗口内的论文不多，这一部分**信息有限**。

## 6. 7 月 arXiv 端侧硬件论文精选

7 月（2026-07-02 ~ 08-01）arXiv 上的端侧 LLM 硬件与系统论文，真机结果明显多于上月。共同的结论是：**端侧 NPU 的短板在 decode，不在 TOPS。** 手机侧在骁龙 8 Elite Gen5（SM8850）上同时出现了“NPU decode 打不过 CPU”的系统测量，以及 0.9B VLM 跑到 98 tok/s 的工程样例。Mac 侧，M5 的 GPU 内 Neural Accelerator 第一次被第三方运行时跑满。加速器侧本月没有新的流片实测：KV 压缩、4-bit 旋转量化、LUT GEMM、模拟 CIM 都是综合或仿真结果，下文逐条标明口径。

（本节不重复 HeteroMosaic，另有专题。部分论文 arXiv 编号为 2609.*，但摘要页显示 v1 提交于 7 月，按 v1 日期计入本月。）

### 一、手机 NPU 真机：prefill 归 NPU，decode 归 CPU

- [Is Your NPU Ready for LLMs?](https://arxiv.org/abs/2607.05475)（清华大学王继良组 / 北京交通大学）是本月最值得读的手机实测。测试覆盖 4 台 16 GB 骁龙手机（SM8650/V75、SM8750/V79、SM8850/V81）和 llama.cpp、MNN、GENIE、MLLM、MLC-LLM 五个框架，并用基于 Qualcomm Power Telemetry 的 PowerBench 把能耗拆到 CPU/GPU/NPU。
  - 框架差距很大。OnePlus 15 上跑 Qwen2.5-1.5B 的 NPU prefill，GENIE 1463.7 tok/s，MNN 700.9 tok/s，llama.cpp 只有 115.1 tok/s；到了 decode，三者几乎持平（23.0 vs 22.8 tok/s）。
  - NPU decode 速度由图的上下文长度决定。上下文从 16 增到 4096，Llama-3.2-1B 从 61.6 降到 47.0 tok/s。CPU 反而是 decode 最快的后端（约 20–70 tok/s）。
  - host 侧有很大的调参空间。RPC 轮询改为 20µs、NPU 休眠延迟改为 65535µs、CPU 锁最低频后，prefill/decode 能耗估算分别降 53.6%/54.8%。代价是 decode 吞吐降 13.4%。
- [StepX-Edge](https://arxiv.org/abs/2607.22708)（StepX Team）是本月唯一一个“模型 + 部署”都在手机 NPU 上闭环的工作。0.9B UI-VLM 全程用标准 full attention，方便适配主流 NPU 算子；部署采用 ViT W8A16、LLM W4A16+KV8。骁龙 8 Gen5 实测 TTFT 0.84 s、prefill 4200 tok/s、decode 98 tok/s、峰值内存 1.4 GB。功耗未披露。
- [DraftExpert](https://arxiv.org/abs/2607.24434) 把 MoE 路由专家放在 Flash 上，按需加载到手机 NPU（Xiaomi MIX Flip 2，Hexagon HTP v81）。每层常驻一个自蒸馏的 draft expert 做自投机解码。DeepSeek-V2-Lite Q4_0 从 10.18 提升到 15.47 tok/s，Moonlight-16B-A3B 从 8.50 提升到 13.69 tok/s，接受率 84–87%，预取命中率 86–88%。这是本月唯一在手机 NPU 上实测 16B 级 MoE 的论文。注意：作者把 SM8850 机型写成“Snapdragon 8 Elite”，且机构未披露。
- [HybridInfer](https://arxiv.org/abs/2609.30270)（独立研究者）给出了少见的负面真机数据。Galaxy S25+（骁龙 8 Elite）用 MLC-LLM/OpenCL 跑 Llama 3.2 3B q4，冷机 14–24 tok/s，热降频后 4–13 tok/s。连续 4–12 次查询后 GPU 运行时崩溃或卡死，40 条长提示中 22 条卡住超过 240 s。作者据此用热余量做端-边-云路由，单次查询从纯端侧的 28–30 s 降到 9.0 s。

把这四篇放在一起看，SM8850 这一代手机的 LLM 能力大致可以这样描述：

- **prefill**：靠 Hexagon NPU 能做到每秒上千 token，但前提是用 QNN/GENIE 这类厂商栈并整图下沉；开源 NPU 路径（llama.cpp）落后约一个数量级。
- **decode**：仍受 LPDDR 带宽和静态图开销限制。1–2B 模型的 NPU decode 为 20–60 tok/s；只有像 StepX-Edge 这样把模型压到 0.9B、W4A16+KV8，并为 NPU 定制算子的方案，才能接近 100 tok/s。
- **长时运行**：热与运行时稳定性是现实约束。HybridInfer 的崩溃数据说明，厂商宣传的峰值 tok/s 不等于可持续速度。

对 SoC 厂商而言，下一代 NPU 的竞争点很可能是 decode 路径（动态 shape、KV 读取、host 唤醒开销），而不是峰值 TOPS。

### 二、能耗与 DVFS：真正的成本是“说多少”

- [Seeing is Free, Speaking is Not](https://arxiv.org/abs/2607.09520)（Imperial / UPenn / 小红书等，ACM MM 2026）在 Jetson Orin NX 和 RTX 3070 Laptop 上测了 5 个 1B–4B VLM。
  - 平均功率是模型固有常数，随输入变化不到 5%；Orin NX 上约 14–15 W。
  - 每个输出 token 的耗时是输入 token 的 11–39 倍，decode 占能耗的 86–97%。
  - 删掉全部视觉 token 最多只省 10% 能耗，控制输出长度最多可省 97%。这直接质疑了“视觉 token 剪枝 = 省电”的主流假设。
- [The Battery Price of edge AI](https://arxiv.org/abs/2609.11940)（Greenspector）在 Pixel 8（Tensor G3）和 iPhone 14（A15）上测了 18 种 1B–4B 配置（Q2/Q4/Q6）。
  - 量化位宽与每 token 能耗不是单调关系，Q4 是能耗甜点。
  - 端侧推理平均比批处理服务器推理能效低约 3 倍。
  - 本地推理的环境影响 88–90% 来自手机隐含碳（摘要口径）。
- [DVFSLM](https://arxiv.org/abs/2609.13153)（香港城市大学李振江组）在 Jetson Orin 上联合调节 GPU 与 EMC（内存控制器）频率。每 token 能耗比内置 governor 低最多 12.4%，比 GearDVFS 低最多 8.4%，QoS 最多改善 93.12%。它说明 decode 能效的关键旋钮是内存频率。
- [eNPU](https://arxiv.org/abs/2607.16473)（UIUC Jian Huang 组，MICRO 2026）把 NPU 拆成多个部件级 V/f 域，并扩展 ISA 实现亚微秒级 DVFS。在 TPUv4 级模拟上，LLM 服务能耗降 25.8%–35.2%，面积开销 3.45%。这是数据中心 NPU 的工作，但“按算子瓶颈分部件调频”同样适用于手机 NPU 的 decode。口径为 RTL + 校准模拟器。

### 三、Mac 与 AI PC：M5 Neural Accelerator 与 XDNA

- [BaseRT](https://arxiv.org/abs/2607.19438)（Base Compute）用 Metal 4 tensor API 手写 GEMM/flash-attention kernel，把 prefill 交给 M5 GPU 每个核心内的 Neural Accelerator。M5 Pro 48 GB 上，prefill 最高为 llama.cpp 的 6.4×、MLX 的 3.9×，decode 最高 1.75×/1.33×。Qwen3.6-35B-A3B Q4 decode 约 110 tok/s。能耗未披露；作者是该运行时的发布方，存在利益相关。
- [FusionML](https://arxiv.org/abs/2607.22785)（独立作者）发现 MLX 的 lazy graph 会把跨 CPU/GPU 流的工作串行化：同一个行切分 matmul 从 1.38× 变成 0.66×。修复后在 M1–M4 共 5 颗芯片上，prefill 提速 1.15–1.38×，Qwen2.5-7B 的 TTFT 快 1.18–1.25×。decode 没有收益，因为共享带宽才是上限。
- [STEEL](https://arxiv.org/abs/2607.09385)（AMD RAD / ETH / Bologna，IEEE COINS 2026）是首个面向 XDNA 的开源 FlashAttention，针对 causal mask 做了稀疏感知的流水放置。Ryzen AI 9 HX 370 上 attention 能耗比 CPU 低 9.17×、比 iGPU 低 1.75×，XDNA 1 上比此前最佳快 9.6×。只覆盖 prefill attention 算子。
- [ATSInfer](https://arxiv.org/abs/2607.10183)（南京大学李武军组）把 CPU-GPU 卸载粒度从层/专家细化到张量。在 RTX 3060 6 GB 笔记本和 RTX 4090 上，prefill 最高提速 1.94×、decode 最高 3.29×，最大跑到 Qwen3.5-122B-A10B 和 GPT-OSS-120B。
- [Lossless but Not Free](https://arxiv.org/abs/2607.17283)（UCSD）在 M3 级 Mac 上实测投机解码。最佳配置 K=6 时为 1.61×，但 5 种配置中 3 种反而变慢，原因是量化 Metal 后端把“并行验证”实际串行执行了。

### 四、外存分页：带宽墙下预测不等于加速

[Budgeting Bytes](https://arxiv.org/abs/2609.04238)（独立作者，workshop 草稿）是本月最“冷水”的结果。8 GB RK3588 + eMMC 跑 Qwen3-30B-A3B 4-bit（18 GB），decode 被 eMMC 带宽封顶，连完美预测的 oracle 预取也无效，因为瓶颈是每 token 的字节量。路由可预测性达 91.2%，但只有在快速层能缓存大部分模型时才能转化为速度。量化到 Q2_K 放进 M4 16 GB 统一内存后，速度为 11.5 tok/s（22×）。这与 DraftExpert 在 UFS 手机上取得的正收益形成对照：**外存分页能否成立，取决于 Flash 带宽与激活参数量的比例。**

### 五、加速器、KV 压缩与存内计算（均为综合/仿真口径）

| 论文 | 机构 / venue | 关键结果 | 口径 |
|---|---|---|---|
| [HiKV](https://arxiv.org/abs/2607.22389) | KU Leuven Verhelst 组 / TCAS-I | token 级 + 元素级两级 KV 压缩，attention 最高提速 7.95×、能耗降 80–90%；面积 2.059 mm²，额外硬件占 8.64% 面积 | TSMC 16nm post-layout |
| [GyRot](https://arxiv.org/abs/2607.27694) | KAIST Hoi-Jun Yoo 组 / HPCA 2026 | 粗旋转 + 细分组的全整数 4-bit，相比基线提速 3.4×、能效提升 3.6×；前作 [LightRot](https://arxiv.org/abs/2607.27704) 27.4 TOPS/W | Samsung 28nm 综合 |
| [MxGLUT](https://arxiv.org/abs/2607.01607) | 澳门大学 | LUT 统一执行 FP8-INT4 与 FP8-FP8，0.492 TFLOPS/mm²、11.58 TFLOPS/W | UMC 28nm 综合 |
| [模拟 CIM 上的 KV 保护](https://arxiv.org/abs/2607.29076) | 北航 / 港大等 | sink token + 最近窗口走数字路径，PPL 33.91→11.95（无噪声 11.06），编程行利用率 23.1%→91.2% | 实测标定的噪声仿真 |
| [DOPS](https://arxiv.org/abs/2607.25498) | 北京大学 / MICRO 2026 | NPU+PIM 动态算子调度，比 PD 分离快 1.20–2.23×，加权重布局再快 1.28–1.33× | 模拟（Ascend 910B + AiM） |
| [PolyQ](https://arxiv.org/abs/2607.14618) | UC Irvine / ICCAD 2026 | 2/3/4/8/16 bit 按通道混合分配，3 bit 下 PPL 改善 2.4–32.1%，能耗/token 仅比 LUT 后端高 <2% | 3 颗 x86 CPU 实测 |
| [解码芯片经济学](https://arxiv.org/abs/2607.13068) | ByteFuture / Texas State | Skymizer HTX-301（28nm + DDR5）4U 约 2.8 万美元跑 DeepSeek-R1 671B，每用户 20.3 tok/s | 厂商资料 + 成本模型 |

这一组的共同方向，是在 decode 中减少需要搬运的字节，而不是增加算力：KV 两级稀疏读取、4-bit 全整数反量化、大容量低带宽 DDR、存内算 KV。HiKV 的“外存访问再降 1.82–4.87×”和 HTX-301 的“少算力多容量”是同一个逻辑。

### 本月论文汇总

| 日期(v1) | 论文 | 平台 | 类型 |
|---|---|---|---|
| 07-02 | MxGLUT | UMC 28nm | 综合 |
| 07-06 | Is Your NPU Ready | 骁龙 8 Gen3/Elite/8 Gen5 手机 | 真机 |
| 07-08 | DVFSLM | Jetson Orin | 真机 |
| 07-10 | Seeing is Free | Orin NX / RTX 3070 | 真机 |
| 07-10 | Battery Price | Pixel 8 / iPhone 14 | 真机 |
| 07-10 | STEEL | Ryzen AI 9 HX 370 XDNA | 真机 |
| 07-10 | 解码芯片经济学 | Skymizer HTX-301 | 分析 |
| 07-11 | ATSInfer | RTX 3060 笔记本 / 4090 | 真机 |
| 07-14 | HybridInfer | Galaxy S25+ | 真机 |
| 07-16 | PolyQ | 9950X / 7840U / N250 | 真机 |
| 07-17 | eNPU | TPUv4 级 | 模拟 |
| 07-19 | 投机解码实测 | M3 Mac | 真机 |
| 07-20 | StepX-Edge | 骁龙 8 Gen5 | 真机 |
| 07-21 | BaseRT | M5 Pro | 真机 |
| 07-24 | FusionML | M1–M4 | 真机 |
| 07-24 | HiKV | TSMC 16nm | post-layout |
| 07-27 | DraftExpert | Hexagon v81 手机 / 4090 | 真机 |
| 07-28 | DOPS | NPU + PIM | 模拟 |
| 07-29 | Budgeting Bytes | RK3588 / M4 | 真机 |
| 07-30 | GyRot | Samsung 28nm | 综合 |
| 07-31 | CIM KV 保护 | 模拟 CIM | 仿真 |

### 能跑多大的模型（真机口径）

| 平台 | 模型 / 精度 | 速度 | 来源 |
|---|---|---|---|
| 骁龙 8 Gen5（SM8850）手机 | StepX-Edge 0.9B，W4A16+KV8 | decode 98 tok/s，prefill 4200 tok/s，1.4 GB | [StepX-Edge](https://arxiv.org/abs/2607.22708) |
| OnePlus 15（SM8850）NPU | Qwen2.5-1.5B，GENIE | prefill 1463.7 tok/s，decode 23.0 tok/s | [Is Your NPU Ready](https://arxiv.org/abs/2607.05475) |
| Xiaomi MIX Flip 2 NPU + Flash | DeepSeek-V2-Lite 16B-A2.4B，Q4_0 | 15.47 tok/s | [DraftExpert](https://arxiv.org/abs/2607.24434) |
| Galaxy S25+（骁龙 8 Elite）GPU | Llama 3.2 3B，q4 | 冷机 14–24，热降频后 4–13 tok/s | [HybridInfer](https://arxiv.org/abs/2609.30270) |
| M5 Pro 48 GB | Qwen3.6-35B-A3B，Q4 | decode 约 110 tok/s | [BaseRT](https://arxiv.org/abs/2607.19438) |
| M4 16 GB | Qwen3-30B-A3B，Q2_K | 11.5 tok/s | [Budgeting Bytes](https://arxiv.org/abs/2609.04238) |
| RK3588 8 GB + eMMC | Qwen3-30B-A3B，4-bit | 被 eMMC 带宽封顶（具体值未披露） | 同上 |
| RTX 4090 + 主机内存 | Qwen3.5-122B-A10B / GPT-OSS-120B | 相对 llama.cpp decode 最高 3.29×（绝对值未披露） | [ATSInfer](https://arxiv.org/abs/2607.10183) |

### 小结

7 月的论文把端侧 LLM 的瓶颈定位得更清楚了：手机 NPU 擅长 prefill，decode 受静态图、host 调度和 LPDDR 带宽限制，默认 DVFS 和休眠参数可能浪费一半能耗。模型侧最有效的省电手段是控制输出长度，而不是剪视觉 token。对 SoC 设计的启示有三点：NPU 需要动态 shape 和小 kernel 友好的 decode 路径；内存控制器频率应与 NPU 协同调度；MoE 外存分页依赖 UFS 带宽，eMMC 级存储上无效。加速器方向（KV 压缩、4-bit 旋转、LUT GEMM、模拟 CIM）本月仍停留在综合和仿真阶段，需要等待流片验证。

## 7. 总结：对端侧智能体意味着什么，以及 8 月该看什么

**对端侧智能体的含义**

1. **体验瓶颈在 decode 和软件栈。** 智能体要多轮生成、频繁调用工具，decode 的速度和能耗直接决定体验和续航。短期最划算的投入是软件：prefill 交给 NPU、decode 交给 CPU/GPU 的阶段拆分，调度与调频（DVFS）协同，控制输出长度。在现有芯片上就能拿到 1.5–2 倍的改善。
2. **内存成本决定模型规模的上限。** 手机内存在 2026–2027 年难以增长，“大总参、小激活”的 MoE 加 1–2 bit 量化和闪存专家分页，是在 12–16GB 内跑十亿到百亿级模型的唯一现实路径；前提是 UFS 4.x/5.0 级的存储带宽。
3. **分层部署成为共识。** 7 月的手机仍以“2B–3B 常驻 + 云端 Agent”为主（高通 WAIC 口径），眼镜只做感知，PC、边缘盒子和车机承担百亿级以上模型。
4. **对厂商口径保持怀疑。** 存算一体、具身芯片和眼镜普遍不公布带宽和实测 tokens/s，“千亿模型”宣传要看是不是 MoE、激活多少参数、什么精度、多大上下文。用带宽除以每 token 读取字节数，就能做第一轮核实。

**留给 8 月的问题（结论已写在 8 月硬件洞察）**

- 近存能否进入手机级芯片：8 月小米玄戒 O100（晶圆键合 DRAM，1.22TB/s）和三星 LPDDR5X-PIM（Hot Chips）给出了第一批证据。
- Apple 新芯片的方向：8 月 25 日 M6 和 M5 Ultra 发布，走的是双 NE、加带宽、不加容量的路线。
- 高通、联发科 2nm 旗舰的规格：8 月爆料成形，9 月正式发布，“30B MoE 上手机”成为新口径。

> 口径说明：标“官方”的是厂商发布的数字，“媒体实测”和“第三方实测”是独立测试，“爆料”未经确认，“推算”或“估算”是本文按公开参数计算的结果。7 月部分方向没有检索到新品或技术长文，已在对应小节注明，包括高通低端 SoC 和 OnQ 技术文、Apple 硬件、知存/苹芯/九天睿芯、MCU NPU、ICML/DAC 主会的端侧硬件论文。
