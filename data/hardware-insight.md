# 硬件洞察：端侧 AI 芯片月报（2026-09-02 ~ 2026-10-07）

> 一句话结论：**端侧 AI 硬件的竞争焦点已经从“NPU 峰值 TOPS”转向“内存子系统”**，包括带宽、容量、封装散热和近存/存内计算。这个月 Apple、高通、联发科三家旗舰同时进入 2nm，但三家都不再把 TOPS 当主卖点，改讲 prefill 速度、每瓦 token、能跑多大的 MoE 模型。与此同时，DRAM 涨价正在压缩手机能给大模型的内存预算。这两股力量叠加，决定了 2027 年端侧智能体的形态：手机跑 10–30B 稀疏模型，PC、车机和机器人跑更大模型，可穿戴设备负责感知并把推理交给手机。

本页是每周“硬件雷达”的月度汇总。逐条动态（含原文链接、规格、可信度）见各周首页的 **硬件雷达** 模块。标注“媒体”或“传闻”的数字未经厂商官方确认。

## 1. 本月旗舰 SoC 一览

| 芯片 | 首发 | 工艺 | CPU | AI 单元 | 内存 | 本代最关键的变化 |
|---|---|---|---|---|---|---|
| Apple A20 Pro | 09-09 iPhone 18 Pro / Duo | TSMC N2（TechInsights 确认） | 6 核（2P+4E），单核 GB6 约 4,720（泄露） | 双 16 核 Neural Engine，AI 算力 ×2；CPU/GPU 内嵌 Neural Accelerator | 96-bit LPDDR5X，带宽 +50% | PoP → WMCM 并排封装，持续性能 +40%；裸片约 98.2mm²，与上代相当 |
| 骁龙 8 超级至尊版 Gen 6（SM8975） | 09-22 小米 18 Pro Max | 2nm（媒体称 TSMC N2P） | 2×5.0GHz + 6×4.0GHz Oryon | Hexagon 新增 Element Accelerator，INT2–FP16；Adreno 首次带矩阵核心；NPU +35% | LPDDR6，约 127GB/s | 目标 30B MoE、32K 上下文；Offset PoP 散热 |
| 骁龙 8 至尊版 Gen 6（SM8950） | 09-22 | 2nm | 同上 | NPU +14%，GPU 无矩阵核心 | LPDDR5X，84.8GB/s | 首次拆成两档，AI 资源向高价档集中 |
| 天玑 9600 Pro | 09-15 vivo X500 Pro / Find X10 Pro Max | TSMC 2nm | 2×C2-Ultra 4.55GHz + 6×C2-Pro | NPU 1090（LLM）+ 常驻低功耗 NPU；INT4 ×2，prefill +51%，每瓦 token +55% | LPDDR6 + UFS 5.0 | 首个 LPDDR6 + UFS 5.0 组合；最高 30B 模型 |
| 天玑 9600M | 09-15 Find X10 | 3nm 级 | C1 系列，支持 SME2 | NPU 990 + **存内计算（CIM）超低功耗 NPU** | LPDDR5X-10667 | 存内计算进入量产手机 SoC |
| 麒麟 9050 Pro | 09-07 Mate XT2 / 10-01 Mate 90 | 约 7nm 级 DUV（Bernstein 估计） | 支持超线程 | 同性能下 NPU 功耗 -66%（官方口径） | — | LogicFolding：晶体管密度约 155→238 MTr/mm²，die 间带宽 125TB/s；Mate 90 端侧跑 30B MoE |
| 玄戒 O3 | 09-07 小米 18 Fold | TSMC 3nm | 10 核（2×C1-Ultra 4.35GHz…，媒体） | NPU 200 TOPS（较 O1 +45%） | 长鑫 LPDDR6-10667，约 113.8GB/s | 首款国产 LPDDR6 手机 |
| Exynos 2700（传） | 10-02 据报量产 | Samsung SF2P | 2×C2-Ultra + 8×C2-Pro（爆料） | — | LPDDR6（爆料） | 三星 2nm 第二代，仍未经官方确认 |

**读表要点：**

- **2nm 不等于更大的芯片。** A20 Pro 的裸片面积几乎没变，新增的晶体管几乎全部给了 NPU 和 GPU。
- **LPDDR6 是本代真正的分水岭。** 高通、联发科、小米都只在最高档型号上用 LPDDR6；苹果仍用 LPDDR5X，靠加宽位宽和改封装换来 +50% 带宽。
- **Arm C2 + SME2 成了安卓旗舰的公共底座。** 9600 Pro、Exynos 2700 和 Arm CSS for Mobile 2 都基于它，CPU 侧的 AI 加速差异会缩小，竞争转到 NPU 和内存上。

## 2. 高通：新东西都集中在“喂数据”

骁龙峰会（09-22~24）的改动几乎都围绕内存瓶颈：

- **Hexagon NPU 重构**（09-10 预披露）：
  - 新增专门加速 Transformer 的 Element Accelerator，配置为 12 标量 + 8 向量 + 1 张量 + 1 element。
  - 共享内存 +50%，减少对 DRAM 的访问。
  - 新增 INT2，支持 INT2/INT4/INT8/INT16/FP8/FP16 全谱精度。
  - INT4 prefill 最高 +50%，并强化了 KV Cache 和投机解码。
  - 官方能力目标写的是“30B 参数 MoE（约 3B 激活）+ 32K 上下文”，而不是 TOPS。
- **GPU 首次加入矩阵核心**：Adreno 成为第二个 AI 引擎，GPU 性能 +44%。
- **LPDDR6（约 127GB/s，上代 84.8GB/s）+ Offset PoP**：把 DRAM 从逻辑 die 正上方挪开，官方称峰值性能可维持的时间翻倍。
- **HBC 近存计算**（The Elec 等报道，中等可信）：
  - 结构：多层 LPDDR 经 TSV 堆叠在 XPU 计算 die 上。
  - 高通口径：同功耗下带宽与 token 效率是 HBM 的 6 倍。
  - 分工：三星和 SK 海力士负责堆叠，台积电负责封装，计划下放到骁龙。
  - 如果 MWC 2027 落地，将是主流移动 SoC 厂商第一次把近存计算产品化。
- **分布式智能体硬件**：
  - 耳机：畅听 Elite Gen 2 的 eNPU 达到 128 GOPS（上代两倍），并加入微功耗 Wi-Fi 6E，耳机可以绕过手机直连云端智能体。
  - 眼镜：AR1 眼镜跑 2B 参数的 1-bit 多模态模型，权重内存从 1.66GB 降到 0.43GB。
  - 胸针：基于 Wear Elite 的 AI 胸针参考设计。
- **补齐软件生态**：骁龙 X2 获得官方 Linux 支持（NPU/GPU 驱动上游化），收购 MoveIt 维护方 PickNik，Modular Mojo 登陆骁龙。
- **产品策略**：旗舰首次拆成两档，LPDDR6、GPU 矩阵核心和大共享内存只给超级至尊版。端侧大模型能力会先集中在高价机型上。

## 3. Apple：带宽、封装和“内存门槛”

- **A20 Pro**：
  - 首颗量产 2nm 手机 SoC。
  - 双 16 核 Neural Engine，AI 算力 ×2；GPU 7 核，+40%；CPU 和 GPU 都嵌入 Neural Accelerator，形成“NPU 常驻低功耗推理 + GPU 矩阵跑开发者大模型”的双路线。
  - 封装从 PoP 改为 WMCM：内存移出散热路径、直贴均热板（面积为上代 3 倍）。带宽 +50%、持续性能 +40% 是端侧 LLM 解码最实在的提升。
- **M6（09-22 开售 Mac mini）**：首颗 2nm M 芯片，与 A20 Pro 同代同构；GPU 每核带 Neural Accelerator，带宽 170GB/s。M5 Ultra 由四个裸片组成，内存最高 512GB、带宽 1.2TB/s。
- **iOS 27 / AFM 3 Core Advanced**：
  - 约 20B 参数的稀疏模型，每次请求只激活 1–4B 参数。
  - 完整权重放在 NAND 闪存，专家按需载入内存。这是“闪存当内存扩展”的量产实践。
  - 只开放给内存 ≥12GB 的设备，**内存容量第一次成为系统功能门槛**。
- **垂直整合仍在过渡**：C2 基带比 C1X 功耗低 15% 并补上 mmWave，但拆解显示 iPhone 18 Pro Max 仍用高通 X80。S11 加入 Secure Exclave，在隔离的硬件区内处理音频。
- **与安卓阵营的差异**：Apple 不公布 TOPS，比拼的是带宽、散热封装和系统级智能体框架（Core AI）。单核性能仍领先骁龙参考机约 8%。

## 4. 联发科、Arm、三星与国产自研

- **联发科天玑 9600 Pro**：率先量产台积电 2nm。两颗 NPU 分工：NPU 1090 跑 LLM，常驻 NPU 跑感知。宣传指标改为 prefill 和每瓦 token，并加入硬件 KV Cache 压缩与 MoE 推理。次旗舰 9600M 把**存内计算 NPU** 带进量产手机 SoC。Counterpoint 数据显示，Q2 手机 AP 出货份额联发科 31% 仍居第一。
- **Arm CSS for Mobile 2**（09-08）：
  - C2-Ultra 的 AI 性能最高是 C1-Ultra 的 1.7 倍，同性能功耗最多 -38%。
  - 集群内 SME2 单元增加到两个，官方称 SLM 加速 70%。
  - Mali G2-Ultra NX 首次在 GPU 内加入神经加速器。
  - Arm AI Portal 可以通过 MCP 被编码智能体调用。
- **三星**：Exynos 2700 据报在 SF2P 上量产，规格均来自爆料。Exynos Q2 份额升到 9%，为历史新高。三星 2nm 良率传闻为 60–70%，高通订单可能推迟到 2027 年。
- **华为**：麒麟 9050 Pro 在受限工艺下靠 LogicFolding（逻辑折叠式 3D 集成）提高密度和带宽，Mate 90 全系使用麒麟芯片。Bernstein 估计其多核性能落后 A20 Pro 约 30%，与苹果的差距缩小到约三年。
- **小米**：玄戒 O3 采用台积电 3nm、NPU 200 TOPS，搭配长鑫 LPDDR6，走“自研 SoC + 国产内存 + MiMo 模型”的整合路线。

## 5. PC：统一内存容量取代 NPU TOPS 门槛

- **NVIDIA RTX Spark（N1X）**：10-07 开放预订，10-16 出货。最高 20 核 CPU、6144 核 GPU、128GB 统一内存、1 PFLOPS FP4。微软 Surface Laptop Ultra 同步推出，并带来面向本地智能体的 Execution Containers 安全隔离和智能体 Entra 身份。
- **AMD Ryzen AI Max PRO 400**：统一内存最高 192GB，AMD 称 4-bit 下可跑 300B+ 模型。Perplexity 的本地智能体可在 Ryzen AI Max 上运行，本地任务不消耗云端额度。
- **Intel Panther Lake（18A，NPU 50 TOPS）**：首发 Googlebook。高通 X2 Plus（NPU 80 TOPS）进入新 Surface。
- **趋势**：Copilot+ 定下的“40 TOPS NPU”门槛已经失去区分度，PC 端智能体的分水岭变成了内存容量、内存带宽和本地/云端混合调度。

## 6. 内存与存内计算：为什么带宽是第一瓶颈

解码阶段每生成一个 token 都要把全部权重读一遍，计算强度极低。粗略估算：

$$\text{tokens/s 上限} \approx \frac{\text{内存带宽}}{\text{每 token 读取的权重字节数}}$$

以 7–8B 的 INT4 模型为例，权重约 4GB：

- 在约 85GB/s 的 LPDDR5X 上，上限只有约 20 token/s。
- 换到约 127GB/s 的 LPDDR6，上限约 30 token/s。
- MoE 每个 token 只读激活的专家，例如 30B 模型只激活约 3B，这正是高通、联发科和 Apple 都选择稀疏模型的原因。

本月三条路线同时推进：

1. **更快的内存**：
   - 三星 16GB LPDDR6 完成骁龙验证：10.7Gbps、114GB/s，能效 +21%。
   - 长鑫 LPDDR6 量产，首发小米 18 Fold。
   - 美光 1γ LPDDR6 开始向物理 AI 客户送样，SOCAMM 收入环比翻倍。
2. **把带宽搬进内存（PIM/近存）**：
   - 三星在 Hot Chips（08-26，窗口前）公布 LPDDR5X-PIM 数据：Llama 3.1 8B 运行时间从 12.3 秒降到 5.4 秒；4nm GAIA 有望在 2027 年成为首款量产 PIM 芯片；JEDEC LPDDR6-PIM 规范接近定稿。
   - SK 海力士把 AiM 定位为“快速 Decode 层”，并提出 SALT-KV，把 KV Cache 分到 HBM/DRAM/SSD 三层。
   - 高通 HBC 走 LPDDR + TSV 堆叠路线。
   - 联发科 9600M 内置 CIM NPU。
3. **少读数据**：
   - 1-bit 和 INT2 量化：高通 AR1 眼镜、新 Hexagon。
   - 稀疏 MoE 和闪存专家卸载：Apple AFM 3。
   - KV Cache 压缩：天玑 9600 Pro 硬件化。
   - 学术侧：伯克利的闪存存内计算 LLM 把 KV 写入流量降低 15 倍。

**PIM 商业化现状**：独立存算公司仍处于融资和小批量交付阶段：

- 融资：Euclyd A 轮超过 2 亿欧元，三星参与领投；地瓜机器人完成 4 亿美元 C 轮。
- 国内交付：据报后摩 M50 已量产（低可信）。“十五五”电子信息制造业规划首次点名存算一体。

但 SoC 大厂（联发科 CIM NPU、高通 HBC、三星 PIM）正在把近存能力做进自家芯片，独立 PIM 公司的空间被挤压，出路更可能在 AI PC、边缘服务器和车载。

**最大变量是涨价**：

- TrendForce 预计 4Q26 DRAM 合约价再涨 10–15%，NAND 再涨 15–20%。
- 高端机 12GB 成为主流、16GB 减少，中端机回落到 8GB。
- 传闻 Galaxy S27 将提价并可能不用 LPDDR6。

结果是在手机端，量化和 KV 压缩比堆模型参数更重要。

## 7. 低功耗、可穿戴与眼镜

- **MCU 级 AI**：英飞凌 PSOC Edge（Cortex-M55 + Ethos-U55）以约 20–65mW 本地运行 6M–32M 参数的语音转写模型，资源占用 ROM 约 4.4MB、RAM 不到 3MB。BrainChip AKD1500 进入量产爬坡，AKD2500 计划 12 月流片。Microchip 完成收购 Hailo。Ambarella X7 是 2–5W 的 M.2 协处理器，用于改造存量设备。
- **眼镜的两种架构**：
  - **分体计算**：Meta VR Glasses 的口袋计算盒内是骁龙 Reality Elite（48 TOPS）和 12GB 内存。
  - **轻眼镜 + 手机/云端**：Ray-Ban Meta Gen 3 和 Audio 款、千问 N1。
  - 高通 AR1 跑 1-bit 2B 多模态模型，说明眼镜本机也能承担一部分推理。
- **耳机和手表**：高通 eNPU 128 GOPS 加微功耗 Wi-Fi；Apple S11 的 Secure Exclave 把隐私敏感的音频处理放进隔离硬件。可穿戴设备正在成为智能体的“常驻感知端”。

## 8. 机器人与车载：国产平台进入 500–700 TOPS

- **地平线**：征程系列累计量产超过 1500 万颗，上半年自主品牌 ADAS 芯片份额首次过半；征程 6P（560 TOPS）获京东 L4 无人配送车定点，车规 SoC 开始复用到物流和机器人场景。
- **爱芯元智 M97**：5nm、720 TOPS、等效带宽 460GB/s。
- **海光 CPU1000**：C86 架构的端侧处理器，规格尚未公开。
- **地瓜机器人**：完成 4 亿美元 C 轮，旭日芯片出货超过 800 万片。
- **高通**：收购 PickNik，从 VLA 模型一路打通到运动规划和实时控制。
- **英伟达**：本月没有新的 Jetson 硬件（Orin Nano 2 在 08-25 发布，窗口之前）。国产平台已经进入可以直接对标 Jetson Thor 的算力区间。

## 9. 产业格局

- **份额**（Counterpoint，Q2'26 手机 AP）：联发科 31%、高通 23%、苹果 19%、展锐 13%（受内存危机冲击）、三星 9%（历史新高）、海思 5%。
- **代工**：台积电 N2 已承接 A20 Pro、M6、天玑 9600 Pro 和骁龙 Gen 6。三星 SF2/SF2P 良率传闻为 60–70%，Exynos 2700 据报已量产。
- **整机**：TrendForce 预计 2026 年手机产量 10.7 亿部，同比 -14%；内存成本推高售价、压缩配置。
- **专利与授权**：高通与华为签署交叉许可（10-05），高通诉 Arm 案同日开庭，Arm 的授权模式仍是安卓阵营的变量。

## 10. 对端侧智能体意味着什么，以及接下来盯什么

**含义**

1. **手机侧的目标模型变成 10–30B 稀疏 MoE。** 能否跑得动，取决于内存容量（≥12GB 的门槛）、带宽（LPDDR6）和闪存卸载，而不是 TOPS。
2. **芯片开始为智能体专门设计。** 常驻感知 NPU、硬件 KV Cache 压缩、GPU 矩阵核心、OS 级隔离（Secure Exclave、Execution Containers）都是例子。端侧智能体的“常驻、长上下文、多工具”负载会直接塑造下一代 SoC。
3. **分布式端侧智能体成形。** 耳机、手表和眼镜负责感知，手机 NPU 负责推理，PC、车机和机器人承接大模型，云端兜底。
4. **NPU 后端越来越碎片化。** Hexagon、NPU 1090、ANE、麒麟 NPU、CIM NPU 各不相同，Arm AI Portal、LiteRT、MLX/Core AI 这类跨平台层更有价值。

**下月观察清单**

- 骁龙 8 超级至尊版 Gen 6 和天玑 9600 Pro 量产机的实测：端侧 LLM 的 prefill 和 decode tokens/s，以及持续性能。
- JEDEC LPDDR6-PIM 规范何时发布；三星 GAIA 的量产时间表。
- 高通 HBC 在移动端的具体形态（MWC 2027 前的消息）。
- M6 MacBook Pro / iMac（传 10 月），以及 RTX Spark PC 上市后的本地智能体实测。
- 4Q DRAM 涨价向 2027 年春季旗舰内存配置的传导。
- MICRO 2026 的 PIM/CIM 论文，以及端侧 LLM 的硬件协同设计工作。

## 附：窗口边缘条目（未计入周报模块）

- 08-26：三星在 Hot Chips 披露 LPDDR5X-PIM，GAIA 或成首款量产 PIM 商用芯片（[TrendForce](https://www.trendforce.com/news/2026/08/26/news-samsungs-4nm-gaia-could-mark-first-pim-commercialization-in-ai-pcs-mass-production-as-early-as-2027/)）。
- 09-01：佐治亚理工提出面向边缘的块扩散 LLM 硬件，与宽 I/O LPDDR 协同设计（[arXiv 2609.01084](https://arxiv.org/abs/2609.01084)）。
- 10-07：微软 Surface Laptop Ultra（RTX Spark）开启预订（[Windows Blog](https://blogs.windows.com/devices/2026/10/07/pre-order-our-most-powerful-surface-devices-ever/)）；RTX Spark PC 全面预订，10-16 出货。

> 来源说明：每条动态都在各周“硬件雷达”中附有原文链接、来源类型（官方/媒体/论文）和可信度。部分厂商官网拒绝抓取，相关条目以多家媒体交叉印证，并标为中等可信。爆料和传闻标为“待进一步核实”。
