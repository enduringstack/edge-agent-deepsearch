# 硬件洞察：端侧 AI 芯片月报（2026-08-02 ~ 2026-09-01）

> **一句话结论：8 月是“发布前夜”，也是“带宽月”。** 手机旗舰（骁龙、天玑、麒麟、A20）都压到 9 月发布，8 月真正落地的芯片是 Apple M6 / M5 Ultra、谷歌 Tensor G6、小米玄戒三芯、NVIDIA Jetson Orin Nano 2 和 Intel Wildcat Lake。但这个月给出了端侧 AI 硬件最重要的一组“带宽证据”：三星 LPDDR5X-PIM 首次实测 8B 模型、小米 O100 用晶圆键合 DRAM 做到 1.22TB/s、d-Matrix 用 pJ/bit 算清数据搬运的能耗，Hot Chips 2026 几乎每个与端侧相关的演讲都在讲内存。9 月各家“30B MoE 上手机”的口径，就是建立在这一组证据之上。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断和芯片对照；第 1–6 节分厂商、分方向展开（高通 / Apple / 其他 SoC 与 PC / 低功耗、存内计算与内存 / Hot Chips 与顶会论文 / arXiv 精选）；第 7 节是对端侧智能体的含义和观察清单。逐条动态（含“能跑多大模型”和可展开的“技术细节”）见 8 月各周首页的“硬件雷达”。

## 0. 总览：8 月的五个判断

**判断一：带宽墙有了产品级的解法，从三个尺度同时推进。**

| 尺度 | 方案 | 关键数字 | 状态 |
|---|---|---|---|
| 内存颗粒内 | 三星 LPDDR5X-PIM：每个 bank 一个 MAC 块 | 内部带宽 614GB/s，为外部的 8 倍；Llama-3.1-8B 从 27.0 提到 81.3 tok/s（约 3 倍） | 首个落点为 AI PC（GAIA，最早 2027 年），手机要等 LPDDR6-PIM |
| 芯片封装 | 小米玄戒 O100：6nm 逻辑晶圆键合 2 层 DRAM | 1.22TB/s，约为手机 LPDDR5X 的 16 倍；官方称 MiMo 3B 达 330 tok/s（媒体实测样机约 295） | 2027 年商用，容量与功耗待验证 |
| 数据中心参照 | d-Matrix Raptor 3D DRAM | 0.37 pJ/bit，对比约 2.4 pJ/bit | 2026 年底流片 |

三者给出同一个结论：解码的成本主要在搬运数据，而不是计算。

**判断二：Apple 把桌面本地推理推进到“数千亿参数”区间，但只公布 prefill 数据。**

- **M6**：首颗 2nm 芯片，双 16 核 NE，GPU 每核带 Neural Accelerator，带宽 170GB/s，属于“prefill 快、decode 一般”。
- **M5 Ultra**：四裸片，512GB，1.2TB/s，官方称可本地运行数千亿参数的 LLM；Thunderbolt 5 RDMA 集群最多 4 台。
- **官方基准**：只有 LM Studio 的 prefill 倍数（M6 是 M4 的 4.8 倍），没有解码速度。

**判断三：手机旗舰进入“先爆料、后发布”的节奏，软件栈提前就位。**

- 骁龙 Gen 6 分两档的轮廓在 8 月已经清晰：高档 LPDDR6 + 18MB GMEM，标准档 LPDDR5X + 12MB（爆料）。
- 高通 GenieX 一个月发了 4 个版本，提前把多 HTP、MTP 投机解码和 26B-A4B MoE 放进测试矩阵。
- 谷歌 Tensor G6 只给相对值：TPU +50%，端侧任务快 3.5 倍；Gemini Nano 的规模未披露。

**判断四：入门级端侧设备的“AI 底线”被重新定义，由内存决定，而不是 NPU。**

- Intel Wildcat Lake：NPU 只有 17 TOPS，内存位宽减半（64-bit LPDDR5X），面向 15W 入门本，达不到 Copilot+ 门槛。
- NVIDIA Jetson Orin Nano 2：78 TOPS、8GB；地瓜 RDK S100P：128 TOPS、24GB、76.8GB/s。

这一档设备能跑多大的模型，基本由 8–24GB 内存和 60–120GB/s 带宽决定。

**判断五：学术界的重心从“能装下”转向“装下之后能不能用”。**

| 方向 | 代表工作 | 关键结果 |
|---|---|---|
| MoE 外存分页 | FreeToken | 8GB 笔记本 GPU 跑 35B MoE 达 39.3 tok/s |
| MoE 外存分页 | S2-MoE | Jetson 跑 GPT-OSS-120B |
| 投机解码硬件化 | EdgeXpert（MICRO 2026） | 1.52W |
| NPU 与 PIM 共处 | PFM（MICRO 2026） | 吞吐最高 2.32 倍 |
| FP4 格式改进 | AdaMX、HBQ | 块级自适应缩放 |
| 手机真实使用条件 | mzCache、提示词能耗 | prompt token 能耗是生成 token 的 3–6 倍 |

但手机 NPU 上的真机结果本月很少，存内/近存论文仍然全部是仿真。

### 8 月发布的芯片对照

| 芯片 | 日期 | 工艺 | AI 单元 | 内存 | 能跑多大模型（口径） |
|---|---|---|---|---|---|
| Apple M6 | 08-25 | 2nm | 双 16 核 NE + GPU Neural Accelerator | 最高 32GB，170GB/s | 未给解码速度；27B 4-bit 实用上限（第三方，9 月实测） |
| Apple M5 Ultra | 08-25 | 四裸片 UltraFusion | 32 核 NE，80 核 GPU | 512GB，1.2TB/s | “数千亿参数”（官方） |
| 谷歌 Tensor G6 | 08-12 | TSMC 3nm | TPU +50% | 未披露 | 未披露（Gemini Nano） |
| 小米玄戒 O3 | 08-24 | TSMC 3nm | NPU 200 TOPS（A8W4）+ 3.13 TFLOPS 向量 | LPDDR6，113.8GB/s | MiMo 3B prefill +40%、decode +45%（官方） |
| 小米玄戒 O100 | 08-24 | 6nm + 2 层 DRAM 晶圆键合 | 14 核 NPU（prefill 用环形网络，decode 用全互联） | 1.22TB/s | MiMo 3B 330 tok/s（官方），约 295（媒体实测） |
| NVIDIA Jetson Orin Nano 2 | 08-25 | — | 78 TOPS | 8GB | 推理为 Orin Nano Super 的 2 倍（官方） |
| Intel Wildcat Lake | 08-24 | Intel 18A | NPU 15–17 TOPS，平台约 40 TOPS | 64-bit LPDDR5X-7467，最高 48GB | 未披露；带宽约 60GB/s（推算） |

## 1. 高通：打基础，不发布

**判断**：8 月是高通的发布前窗口期，没有新芯片正式发布，Hot Chips 2026（8 月 23 至 25 日）的公开议程中也没有检索到高通的报告。但这个月的信息量不小：一是官方预热“双 8 Elite”，加上三轮爆料（安兔兔、命名、Geekbench），提前给出了 9 月旗舰的分档轮廓；二是软件栈密集更新，GenieX 一个月发了 4 个版本，把多 HTP、MTP 投机解码和 26B-A4B MoE 放进了测试矩阵，Modular 开源 Mojo；三是 HBC 近存计算、主权 AI PC 和两位数涨价，从数据中心和成本两端说明了“内存墙”正在成为高通的主线问题。

### 一、旗舰发布前的信息：从爆料到官方预热

| 日期 | 事件 | 关键数字 | 口径 |
|---|---|---|---|
| 8/14 至 8/15 | SM8975 安兔兔截图 | 总分 4,835,412；CPU 1,368,930；GPU 1,854,826（Adreno 850） | 爆料，安兔兔称后台查不到（[nokiamob](https://nokiamob.net/2026/08/14/snapdragon-8-elite-gen-6-pro-early-antutu-benchmark-explained/)、[gazlog](https://gazlog.jp/entry/snapdragon8e-g6-pro-antutu-benchmark-leak/)） |
| 8/19 | 官方 X 预热“Dual 8 Elites / Twice the options” | 9 月 22 日发布两颗 8 Elite | 官方（[ETV Bharat](https://www.etvbharat.com/en/technology/qualcomm-snapdragon-dual-8-elite-snapdragon-summit-2026-snapdragon-8-elite-gen-6-pro-enn26082007922)、[SamMobile](https://www.sammobile.com/news/galaxy-s27-snapdragon-chip-teased-as-qualcomm-confirms-two-new-flagships/)） |
| 8/25 | 命名爆料：Pro 改为 Extreme | 2×5.01GHz + 3 + 3，台积电 2nm | 爆料（[Android Authority](https://androidauthority.com/snapdragon-8-elite-extreme-gen-6-leak-3702629)） |
| 8/26 | vivo V2606A Geekbench 6.7.1 | 单核 3,434 / 多核 9,334（Gen 5 零售均值 3,631 / 10,940） | 跑分库（[gazlog](https://gazlog.jp/entry/snapdragon-8-elite-extreme-g6-geekbench6-benchmark/)） |

把 8 月的爆料和 9 月的官方规格对照，可以得到以下几点：

- **分档方式在 8 月已经基本明确**。爆料称 Pro 版为 Adreno 850 + 18MB GMEM + LPDDR6，标准版为 Adreno 845 + 12MB GMEM + LPDDR5X。9 月官方实际的分档也集中在内存带宽（LPDDR6 127.2GB/s 对 LPDDR5X 84.8GB/s）、NPU 共享内存（+50% 仅 Extreme）和 GPU Neural Fusion 上，与 8 月爆料基本吻合。
- **“Matrix ALU + AI Frame Fusion”提前曝光**。8 月的安兔兔爆料附带提到 Pro 版 GPU 会加入矩阵 ALU 和 AI 插帧，9 月落地为“Adreno 首次加入 AI 矩阵核心 + Neural Fusion”。这说明高通的 AI 算力开始从 Hexagon 向 GPU 外溢，但矩阵核心的数量和 TFLOPS 至今未披露。
- **5GHz 的代价**。8 月 26 日的开发机多核比上代零售机还低 15%，而 9 月官方参考机多核为 12,686。两者差约 36%，说明早期固件和功耗墙对 5GHz 设计的影响很大，也解释了官方为什么在 9 月强调 Offset PoP 和导热块。需要注意，簇配置存在口径冲突：爆料和 Geekbench 记录都是 3×3.74 + 3×4.03 + 2×5.01GHz，官方简介则写 2×5.0 + 6×4.0GHz。
- **NPU 在 8 月完全没有泄露**。所有爆料都没有提到 Hexagon 的 TOPS 或结构。Element Accelerator、共享内存 +50%、30B MoE 都是 9 月 22 日才首次公开。高通对 NPU 的信息管控明显比 CPU 和 GPU 严格。

### 二、软件栈：GenieX 8 月四连发，为 MoE 和投机解码铺路

[GenieX](https://github.com/qualcomm/GenieX/releases) 是高通开源的端侧生成式 AI 运行时（QAIRT 与 llama.cpp 双后端）。8 月共发布 4 个版本，9 月报告覆盖的是之后的 v0.7 和 v0.8：

| 版本（日期） | NPU/HTP 相关 | 模型/功能 |
|---|---|---|
| v0.3.19（8/7） | 所有设备重新获取 HTP 会话 | InternVL 3.5 走 QAIRT |
| v0.3.20（8/13） | 修复 HTP 会话频繁重建导致的 MTP 失败；MTP prefill 只为最后一个 token 计算 logits | CPU/GPU/NPU 三端 QDC 矩阵；FIM 接口 |
| v0.4.0（8/13） | Android SM8850 加入 QDC 矩阵 | `geniex model list` 接入 AI Hub 目录 |
| [v0.5.0（8/22）](https://github.com/qualcomm/GenieX/releases/tag/v0.5.0) | 显式多 HTP 设备列表作为计算单元；VLM 编码器固定在 HTP；Microsoft 签名 HTP catalog | gemma-4-26B-A4B-it QAT GGUF 进入 bench；MTP 投机解码；VLM KV 前缀复用 |

几点技术判断：

- **MoE 先进入测试，再进入发布会**。26B 总参数、约 4B 激活的 Gemma 4 MoE 在 8 月 22 日就进入了 bench 矩阵，一个月后官方提出“30B MoE（约 3B 激活）+ 32K 上下文”，两者规模接近。端侧 MoE 的核心问题是权重总量远大于激活量：按 4-bit 估算，26B 权重约 13GB 量级（本文推算），需要靠大内存或从闪存按需加载专家来解决（9 月 The Elec 称专家权重放在 UFS 5.0 上按需加载）。
- **HTP 会话开销是痛点**。连续两个版本都在修 HTP 会话重新获取和频繁重建的问题，说明投机解码（草稿模型和目标模型交替）以及 VLM（编码器和语言模型交替）在 NPU 上切换上下文的成本不低。这也解释了为什么 v0.5.0 把视觉编码器固定在 HTP 上，9 月 v0.8.0 又进一步拆分成独立会话。
- **多 HTP 主要面向 PC 和 IoT**。“显式设备列表作为一个计算单元”针对的是多 NPU 板卡和多核 HTP。9 月 v0.7.0 打开了 QAIRT HTP multicore，可以看出高通在为 X2 和 QCS 平台上的大模型做横向扩展。
- 所有版本的发布说明都**没有给出 tokens/s 或功耗**。prefill/decode 速度指标要到 9 月 v0.7.1 才加入服务端响应。

另外，高通 7 月 29 日完成收购的 Modular 在 8 月 11 日发布 Mojo 1.0，8 月 18 日以 Apache 2.0 [开源 Mojo 编译器](https://runtimewire.com/article/chris-lattner-open-sources-mojo-qualcomm-modular)。新后端包括 Cloud AI 100 Ultra 和 Dragonfly，**没有提到 Hexagon**。目前端侧仍是 QAIRT、Genie、GenieX 体系，Mojo 能否覆盖 Hexagon，是高通能否用一套语言贯通端到云的关键看点。

### 三、内存墙：从 HBC 到涨价

- **HBC 近存计算**：8 月 26 日德意志银行会议上，Durga Malladi 称首代数据中心芯片“back in the lab, looking good”，2027 年出货的 HBC“第一代预计没有问题”，内存厂商的态度是主动寻求更紧密的合作（[TIKR 转述](https://www.tikr.com/blog/qualcomm-stock-is-up-15-in-a-month-the-data-center-story-is-why-it-can-keep-going)，二手）。HBC 延续的是 AI200（每卡 768GB LPDDR）和 AI250（近存计算）的路线，用 LPDDR 的容量和近存算力替代 HBM。这与手机端“共享内存 +50%、LPDDR6、MoE 专家放在闪存”是同一个问题在不同尺度上的解法。
- **两位数涨价**：9 月 1 日以后出货的芯片涨价“两位数”，Amon 称是转嫁供应商成本，背景是 DRAM 和存储涨价（[MacRumors](https://www.macrumors.com/2026/08/31/qualcomm-chip-price-increase/)）。端侧大模型需要 16 至 24GB 内存，SoC 和内存同时涨价，意味着“能跑 30B MoE”的机型会集中在 Extreme 档的超高端机上，标准版机型更可能停留在小参数稠密模型。

### 四、PC：Horizon Ultra，主权 AI 的端侧形态

8 月 31 日，高通与 HUMAIN 在 LEAP 2026 发布 [Horizon Ultra AI PC](https://www.qualcomm.com/news/releases/2026/08/qualcomm-and-humain-unveil-horizon-ultra-ai-pc-at-leap-2026--bri)（[TelecomTV 全文](https://www.telecomtv.com/content/digital-platforms-services/qualcomm-and-humain-unveil-horizon-ultra-ai-pc-at-leap-2026-bringing-ai-directly-to-the-device-56150/)）：

| 项目 | 内容 | 口径 |
|---|---|---|
| SoC | Snapdragon X2 Elite，18 核 Oryon + Adreno + Hexagon | 官方 |
| NPU | 80 TOPS | 媒体转述（Reuters 系） |
| 续航 | 最长 22 小时 | HUMAIN 高管接受 AGBI 采访 |
| 系统 | Windows，2027 年换成 HUMAIN OS | 官方 |
| 模型 | 未披露 | — |
| 上市 | 9 月 20 日起企业销售（AlFalak） | 官方 |

这款产品的意义不在芯片本身：HUMAIN 同时是高通 AI200 机架的首个客户，高通借此在同一个客户身上打通了数据中心推理和端侧 AI PC 两条线。官方稿只提到“CPU、GPU、NPU 异构 + 云端延伸”，没有给出端侧模型规模，因此不宜把 X2 平台“30B、20 万上下文”的口径直接套用到这台机器上。

### 五、各项能跑多大的模型（8 月可确认信息）

| 对象 | 模型规模 | 精度 | 速度/功耗 | 口径 |
|---|---|---|---|---|
| 8 Elite Gen 6 / Extreme（8 月） | 未披露 | 未披露 | 未披露 | 爆料中无 NPU 信息 |
| GenieX v0.5.0 测试矩阵 | Gemma 4 E2B/E4B；InternVL 3.5；Gemma-4-26B-A4B | QAT GGUF（4-bit 级） | 未披露 | 官方开源仓库 |
| Horizon Ultra（X2 Elite） | 未披露 | 未披露 | 22 小时续航（媒体转述） | 官方稿未给出 |

### 小结

8 月高通在端侧 AI 上的动作主要是“打基础，不发布”：硬件分档在爆料中已经明确，NPU 新特性被严格保密到 9 月；软件上 GenieX 提前把 MoE、MTP 投机解码和多 HTP 做进运行时；战略上，HBC、主权 AI PC 和涨价都指向同一个约束，即内存容量、带宽和成本。我们的判断是，高通 2026 至 2027 年端侧 AI 竞争力的上限更多取决于每 GB 内存能支撑多大的模型，而不是 NPU 的 TOPS。值得跟踪的三个问题是：Hexagon 是否进入 Mojo/MAX 后端；GenieX 何时公布 MoE 的实测 tokens/s；标准版 8 Elite Gen 6 机型最终配 12GB 还是 16GB 内存。

（检索说明：Hot Chips 2026 公开议程中未检索到高通报告；FQ3 财报为 7 月 29 日，不在本窗口；8 月未检索到 Snapdragon 7/6/4 系、Wear、XR、Ride/Cockpit、Dragonwing 新品发布，Amazon 数据中心合作为 9 月 8 日，均不计入。）

## 2. Apple：M6 看并发，M5 Ultra 看容量

8 月的 Apple 只有一件主事：**8 月 25 日 M6 与 M5 Ultra 同日发布**。M6 是 Apple 第一颗 2nm 芯片，也是第一颗采用“双 16 核 Neural Engine”的芯片；M5 Ultra 用四裸片 UltraFusion 把单机统一内存带宽推到 1.2TB/s，官方首次明确说可以本地运行“数千亿参数”的 LLM。两颗芯片指向同一个方向：端侧 AI 算力的增量从 GPU 矩阵单元扩展到 NE 并发，桌面端则继续用容量和带宽换取能放下的模型规模。iOS 27 beta、MLX 的两个版本和 A20 Pro 的爆料都是这条主线的配套。

### 一、M5 → M6 → M5 Ultra：规格对比

| 项目 | M5（2025.10） | **M6（2026.08）** | **M5 Ultra（2026.08）** |
|---|---|---|---|
| 工艺 | 第三代 3nm | **2nm**（Apple 首颗） | 未单独披露（2×M5 Max） |
| 封装 | 单裸片 | 单裸片 | **四裸片 UltraFusion**，裸片间 >4.4TB/s |
| CPU | 10 核（4P+6E） | 12 核（**2 super**+4P+6E），多线程为 M5 的 1.2 倍 | 36 核（12 super+24P），对 M3 Ultra：单线程 1.25 倍 / 多线程 1.3 倍 |
| GPU | 10 核，每核带 Neural Accelerator | 12 核，AI 峰值比 M5 高近 30% | 80 核，AI 峰值为 M3 Ultra 的 4.5 倍 |
| Neural Engine | 16 核 | **双 16 核**，峰值最高 2 倍，可同时调用 | 32 核 |
| 内存上限 | 32GB | 32GB | **512GB** |
| 带宽 | 153GB/s | 170GB/s（+10%） | **1.2TB/s**（比 M3 Ultra 高 50%） |
| 官方 LLM 口径 | GPU AI 峰值为 M4 的 4 倍以上 | LM Studio prefill 为 M4 的 4.8 倍 | LM Studio prefill 为 M3 Ultra 的 4 倍；可运行“数千亿参数” |

来源：[M6 / M5 Ultra 新闻稿](https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/)、[Mac mini 新闻稿](https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/)、[Mac Studio 新闻稿](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/)、[M5 新闻稿](https://www.apple.com/newsroom/2025/10/apple-unleashes-m5-the-next-big-leap-in-ai-performance-for-apple-silicon/)。所有 TOPS 和 Neural Accelerator 的 FP16/INT8 吞吐，Apple 均**未披露**。

### 二、M6：2nm 上的三处改动

**1. CPU 改为三级核心。** M6 第一次在基础款 M 芯片上使用 super / performance / efficiency 三级，2+4+6=12 核，比 M5 多 2 核，多线程 +20%。Apple 只说“全球最快单线程”，没有给出单线程倍数。对 LLM 来说，CPU 主要承担 tokenizer、采样、工具调用等串行部分，这次升级对主干推理影响很小。

**2. NE 改为双实例。** “双 16 核”是两个独立的 16 核 NE，不是一个更宽的引擎。新闻稿特意写明“系统框架可以同时使用两个引擎”，因此 2 倍峰值更可能在多模型、多请求并发时兑现，比如 Siri AI、相机、输入法同时推理。单模型能否切分到两个引擎，Apple 没有说明（推断）。值得注意的是，M6 的 NE 核数（32）已经等于 M5 Ultra。

**3. GPU 增量放缓。** M4→M5 的 GPU AI 峰值提升超过 4 倍，M5→M6 只有“近 30%”，与 GPU 核数从 10 增到 12（+20%）加上频率提升基本吻合。官方给出 LM Studio prompt processing 为 M4 的 4.8 倍，但这测的是 prefill。M6 带宽只从 153 提高到 170GB/s，所以**解码速度的代际提升只有约 10%**（屋顶线推断）。手机端的 A20 Pro 把位宽从 64-bit 加到 96-bit，桌面基础款 M6 没有跟进，这是本代 M6 最明显的短板。

### 三、M5 Ultra：四裸片与 512GB

M5 Ultra 由两颗双裸片 M5 Max 通过新一代 UltraFusion 拼接而成，裸片间带宽超过 4.4TB/s，连接密度提高 6 倍以上。规格基本是 M5 Max 的两倍：M5 Max 为 18 核 CPU、40 核 GPU、614GB/s，M5 Ultra 为 36 核、80 核、1.2TB/s。这是 Ultra 第一次每个 GPU 核都带 Neural Accelerator，所以 [Mac Studio 新闻稿](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/) 中 LM Studio prefill 达到 M3 Ultra 的 4 倍、文生图 4.3 倍。按带宽比推算，解码只会快约 1.47 倍（1.2TB/s ÷ 819GB/s，推断）。

另一个变化是**集群**。Mac Studio 最多有 6 个 Thunderbolt 5（120Gb/s）端口，通过 RDMA 把多台机器的内存组成共享池，官方称 4 台集群的分布式推理最高为单机的 3 倍。单口约 15GB/s，只有片内带宽的约 1/80，因此集群更适合 pipeline 或 expert 并行，用来放下更大的模型，而不是加速小模型（推断）。512GB 配置延后到 10 月下旬出货；M5 Ultra 起价 5,499 美元，M6 Mac mini 起价 899 美元。

### 四、能跑多大的模型

Apple 唯一的官方模型规模口径是 M5 Ultra 可以运行“**数千亿参数**”（hundreds of billions of parameters）的 LLM。下表按“权重 = 参数 × bit/8，解码上限 ≈ 带宽 ÷ 每 token 读取的字节数”估算，均为**估算**，不代表 Apple 口径：

| 机型 | 内存 / 带宽 | 4-bit 稠密上限（估） | 典型负载与解码上限（估） |
|---|---|---|---|
| Mac mini M6 | 32GB / 170GB/s | 约 27–32B | 8B 4-bit 约 38 tok/s；27B 4-bit 约 11 tok/s |
| Mac mini M5 Pro | 64GB / 307GB/s | 约 70B | 70B 4-bit 约 7.7 tok/s；30B-A3B MoE >100 tok/s |
| Mac Studio M5 Max | 128GB / 614GB/s | 约 120B+ | 120B 级 MoE（激活约 5B）可常驻 |
| Mac Studio M5 Ultra | 512GB / 1.2TB/s | 约 0.7–0.9T | 671B 级 MoE（激活 37B，约 20GB/token）约 60 tok/s；70B 稠密约 30 tok/s |
| 4× M5 Ultra（RDMA） | 约 2TB | 约 3T | 官方只给出“3 倍提速” |

可以看出，M6 的定位是 8B–14B 级模型的常驻推理盒子；百 B 级以上的模型要靠 M5 Max / Ultra 的容量。这类模型最好选激活参数小的 MoE，因为同等显存占用下，稠密模型的解码要慢一个数量级。对照 Apple 自家模型，端侧 [AFM 3](https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models) Core Advanced 约 20B 总参、激活 1–4B，用闪存分层把总参数放在 NAND 上。Mac 和手机走的是同一条“总参大、激活小”的路线，区别在于 Mac 能把全部权重常驻 DRAM。

### 五、软件与爆料：iOS 27 beta、MLX、A20 Pro

- **iOS 27 beta 5/6**：[beta 5](https://9to5mac.com/2026/08/10/heres-whats-new-with-ios-27-beta-5/)（8 月 10 日）重启了 Siri AI 的索引，Siri 增强语音新增英式英语；[beta 6](https://9to5mac.com/2026/08/17/ios-27-beta-6/)（8 月 17 日，24A5418b）以稳定性为主，Camera App 新增 Siri 模式。Siri AI 基于新一代 Apple Foundation Models，端侧和 PCC 的分工未披露。
- **MLX**：[v0.32.1](https://github.com/ml-explore/mlx/releases/tag/v0.32.1)（8 月 18 日）和 [v0.32.2](https://github.com/ml-explore/mlx/releases/tag/v0.32.2)（8 月 25 日）集中优化 NAX（GPU Neural Accelerator）路径，包括 attention 循环展开、head_dim 256 融合 attention、量化 MoE matmul、M5 Max 上的 NVFP4 QMV；解码侧让 gqa-8 attention 的 K/V 只读一次；分布式侧为 JACCL 增加多 ring 和 scatter reduce。这些改动与新 Mac 的“prefill + 集群”卖点一一对应。
- **A20 Pro 爆料**：【爆料】MacRumors 8 月 17 日引述定焦数码，称性能 +18%、能效 +30%，这组数字与 TSMC N2 的工艺口径接近，可能是推算出来的；AppleInsider 8 月 7 日引述 Ice Universe，称 NE 面积明显变大。M6 发布后，A20 Pro 采用双 NE 已经可以推断。8 月没有检索到新的一手 N2 / WMCM 供应链报道，相关报道集中在 [2026 年 1 月](https://www.trendforce.com/news/2026/01/20/news-tsmc-reportedly-expands-wmcm-packaging-for-apple-capacity-may-more-than-double-by-2027/)和 [2 月](https://www.trendforce.com/news/2026/02/02/news-tsmc-2nm-reportedly-tight-amid-mobile-hpc-demand-nvidia-may-be-first-to-adopt-1-6nm-in-2028/)的 TrendForce。
- **论文**：8 月窗口内没有检索到 Apple 署名的端侧推理论文。第三方 [GreenBench](https://arxiv.org/abs/2608.28667)（arXiv，8 月 24 日）在 M4 Pro 上测得 Llama 3.2 3B 为 175 tok/s、Qwen 2.5 7B 为 59 tok/s，整机功耗 8–12W；但论文给出的“封装 0.47W”明显偏低，引用时要谨慎。

### 六、工程解读：这一代的取舍

**第一，为什么 M6 不加内存位宽。** 手机端 A20 Pro 要在 12GB 内存里运行激活 1–4B 的系统模型，解码速度直接决定 Siri AI 的交互体验，所以加宽总线的收益很高。桌面基础款 M6 的主要用户是办公和轻创作，本地大模型的重度用户本来就会选 Pro / Max。M6 把预算花在 2nm、多 2 个 CPU 核、多 2 个 GPU 核和一个 NE 实例上，更符合它的产品定位。代价是：M6 Mac mini 跑同一个 8B 模型，解码速度相比 M5 几乎不变，体验上的提升主要在首 token 延迟和长 prompt 处理上。

**第二，为什么 NE 和 GPU 两条路线并存。** GPU Neural Accelerator 面向开发者：MLX、llama.cpp、LM Studio 都跑在 Metal 上，算子可以自定义，适合大 batch 的 prefill 和各种新模型结构。NE 面向系统：Core AI 和 Foundation Models 框架负责调度，单位功耗算力更高，适合 Siri、相机、输入法等常驻任务。双 NE 的意义在于让多个系统模型同时常驻、互不抢占，而不是让第三方的单个大模型跑得更快。对第三方开发者来说，短期内在 Mac 上优化的重点仍然是 GPU 路径。

**第三，为什么 Ultra 不提高容量上限。** M5 Ultra 的 512GB 与 M3 Ultra 持平。在 LPDDR5X 供给紧张的 2026 年，Apple 选择用 Thunderbolt 5 RDMA 集群来突破单机容量，而不是把单机推到 1TB。这也解释了为什么 Mac Studio 新闻稿第一次把“分布式推理提速 3 倍”写成卖点，而 MLX 在 8 月连续加强 JACCL。

**第四，官方基准的边界。** Apple 在三份新闻稿中给出的 LLM 数字全部是 LM Studio 的 prompt processing 倍数，测试在 7 月用预量产机完成，模型、量化和上下文长度都没有公布。这类数字适合判断 GPU 矩阵单元的代际进步，但不能用来推算对话时的解码速度。工程评估时，建议同时记录 TTFT、prefill tok/s、decode tok/s 和整机功耗，再用带宽屋顶线检查结果是否合理。

### 小结

8 月 Apple 的芯片发布可以概括为：**基础款看并发，旗舰看容量**。M6 用 2nm 和双 NE 为系统级多模型并发做准备，但 170GB/s 的带宽限制了解码速度，属于“prefill 快、decode 一般”的产品；M5 Ultra 用四裸片 UltraFusion 把 512GB 和 1.2TB/s 放进单机，再用 Thunderbolt 5 RDMA 把边界扩展到多机，桌面本地推理正式进入数千亿参数 MoE 的区间。官方基准仍然只给 prefill 倍数，不给解码速度、TOPS 和模型细节，工程选型还要等 9 月之后的实测，并按带宽屋顶线自行校验。

## 3. 谷歌、小米、NVIDIA 与 PC：绕开 TOPS，正面解决带宽

8 月是非高通、非苹果阵营的“发布前夜”：联发科、华为、三星的旗舰均推迟到 9 月，真正落地的芯片新闻集中在三件事——谷歌 [Tensor G6](https://blog.google/products-and-platforms/devices/pixel/google-pixel-11-pro-xl/)（8 月 12 日）、小米玄戒三芯（8 月 24 日）、NVIDIA [Jetson Orin Nano 2](https://nvidianews.nvidia.com/news/nvidia-announces-jetson-orin-nano-2-robotics-computer-to-redefine-entry-level-edge-ai)（8 月 25 日），PC 侧则是 Hot Chips 上的 [Wildcat Lake](https://www.servethehome.com/intel-core-series-3-wildcat-lake-cpu-at-hot-chips-2026/)。共同信号是：**厂商开始绕开 TOPS，正面解决 decode 的内存带宽问题**——小米直接把 DRAM 堆到 NPU 上，NVIDIA 把 2 倍推理归功于带宽和 Tensor Core 利用率，谷歌只谈端到端“快 3.5 倍”。

### 一、谷歌 Tensor G6：只给相对值的“协同设计”

[官方博客](https://blog.google/products-and-platforms/devices/pixel/google-pixel-11-pro-xl/)给出的硬数字只有四个：TPU 算力 +50%、端侧 AI 任务最高快 3.5 倍且能耗最多降为 1/3.5、网页浏览 +25%、App 启动 +15%，全部为预量产机内部数据。工艺经 Google 硬件副总裁向 CNA 确认为改良版 TSMC 3nm（[HelenTech](https://helentech.jp/news-tensor-g6-pixeltsmc-3nm-confirmed/)），而非传闻的 2nm。

值得注意的是**峰值 +50% 与端到端 3.5 倍之间的缺口**：这部分增益只能来自模型侧（新版 Gemini Nano 与 DeepMind 联合设计）、编译器与内存通路，而非 MAC 数量。代价是可比性极差——[xenospectrum](https://xenospectrum.com/en/pixel-11-tensor-g6-tpu-compute-on-device-ai/)指出，Google 没公布模型名、输入长度和逐任务数据，G5 时代的“TPU +60%”与 G6 的“+50%”测量对象也不同，不能连乘。开发者侧，Tensor ML SDK 已于 5 月进入 Beta，可经 LiteRT 把 PyTorch/TFLite 模型放到 TPU，不支持的算子回退 CPU/GPU。

从工程角度看，“快 3.5 倍”的脚注写的是“预量产机、Wi-Fi 下播放 YouTube 时的内部数据平均值”，测的是通知摘要、语音转写这类短输入、短输出任务。这类任务的耗时主要在首 token 之前的 prefill 和模型加载，峰值算力 +50% 加上更小更新的 Nano 模型，就足以解释大部分提升；但对长上下文、长输出的 Agent 任务，决定速度的是带宽，而 Google 官方博客对带宽只字未提（个别媒体称“带宽翻倍”，仅单一来源）。内存方面，Google 在 DRAM 涨价背景下强调“优化 DRAM 使用方式”，媒体整理的 RAM 配置为 12GB/16GB，说明谷歌并不打算像联发科、华为那样追逐 30B 级端侧模型，而是维持“端侧 Nano 处理隐私和低延迟任务、云端 Gemini 处理跨 App Agent”的分工，并用 Private AI Compute 把云端部分包装为“近似端侧”的隐私保证。

### 二、小米玄戒三芯：从“堆 TOPS”转向“堆带宽”

8 月 24 日的玄戒技术沟通会一次发布 O3、O100、D100 三颗芯片和两台原型机（[IT之家](https://www.ithome.com/0/993/683.htm)、[爱范儿](https://ifanr.com/1676441)）。

**玄戒 O3**：3nm、240 亿晶体管（+26%）、133mm²；2×C1-Ultra 4.35GHz + 4×C1-Premium + 4×C1-Pro 十核全大核，双 SME2；NPU 200 TOPS（A8W4 口径）+ 3.13 TFLOPS 向量；GPU 内 8 个 NX 单元另有 36 TOPS。真正的亮点在存储子系统：首款 LPDDR6 手机 SoC（4×24-bit，113.8GB/s，较 O1 +48%），约 60MB 缓存加 28MB NPU 近存，动态访存时延 177ns（A19 Pro 211ns、O1 384ns，官方对比）。硬件霍夫曼无损压缩在权重读取路径上再省 30% 带宽。MiMo 3B 上首词 +40%、推理 +45%、功耗 -26%。

**玄戒 O100** 是本月最激进的设计：6nm 逻辑与 2 层 AI 专用 DRAM 做晶圆级混合键合（间距 1.4µm、258 万节点），带宽 1.22TB/s，约为 O3 的 10.7 倍（[RITS 推算](https://rits.shanghai.nyu.edu/ai/xiaomi-ai-cube-three-chip-prototype/)）。14 核 NPU 的片上网络按阶段切换：Prefill 用 Ring，Decode 用 All-to-All。官方口径最高 330 tokens/s，O3+O100 原型机实测最高约 295 tokens/s（媒体）。但原型机砍掉摄像模组、上主动风冷（散热 10W），堆叠 DRAM 容量未披露，进入量产手机仍有距离，官方称明年商用。

**玄戒 D100 / AI Cube**：3nm、20 核 CPU、16 核 NPU、最高 160GB 统一内存，已本地部署 200B 参数模型；AI Cube 三芯协同，150W 持续功耗，本地 120B + 3B 双模型做快慢系统切换。这是把“手机快系统 + 本地大模型慢系统”做成自家硅片组合的首个样机。

几点技术解读。其一，**A8W4 口径**：200 TOPS 是 INT8 激活乘 INT4 权重的吞吐，权重位宽减半让同样的 MAC 阵列吞吐翻倍，因此与竞品 INT8 TOPS 不能直接比较；它也说明小米的 NPU 是围绕“低比特权重 + 8-bit 激活”的 LLM 推理量身定做，而不是传统 CNN 加速器。其二，**时延比带宽更说明问题**：动态访存时延从 O1 的 384ns 降到 177ns，降幅超过一半，对 decode 阶段“小批量、随机性较强”的权重与 KV 读取比峰值带宽更敏感。其三，**O100 的双网络设计**直接对应 LLM 的两阶段：Prefill 是大矩阵乘、计算密集，Ring 网络适合把激活在核间流水传递；Decode 是矩阵向量乘、访存密集，All-to-All 让 14 个核各自直取本地堆叠 DRAM，避免环形网络的跳数延迟。其四，**28,672 条数据线**是 O3 的 96-bit LPDDR6 接口的约 300 倍，用低频宽接口换取带宽与每比特能耗，这与 HBM 的思路相同，只是做到了手机可容纳的 6nm + 晶圆键合方案上。

| 项目 | 玄戒 O1（2025） | 玄戒 O3 | 玄戒 O100 |
|---|---|---|---|
| 工艺 | 3nm | 3nm，133mm²，240 亿晶体管 | 6nm + WoW 3D 堆叠 DRAM |
| CPU | 十核 | 2×C1-Ultra + 4×C1-Premium + 4×C1-Pro，双 SME2 | — |
| NPU | — | 200 TOPS（A8W4）+ 3.13 TFLOPS 向量 | 14 核，TOPS 未披露 |
| 内存带宽 | 约 77GB/s（由 +48% 反推） | LPDDR6 113.8GB/s | 1.22TB/s |
| 动态访存时延 | 384ns | 177ns | — |
| LLM 口径 | — | MiMo 3B：Prefill +40%、Decode +45% | 最高 330 tok/s（原型机实测约 295） |

### 三、NVIDIA Jetson Orin Nano 2：TOPS +16%，推理 ×2

[官方新闻稿](https://nvidianews.nvidia.com/news/nvidia-announces-jetson-orin-nano-2-robotics-computer-to-redefine-entry-level-edge-ai)给出 78 TOPS、8GB、8 核 Arm CPU，推理为 Orin Nano Super 的 2 倍，15W 模式同性能功耗 -40%，2027 上半年供货。合作伙伴 [Premio](https://premioinc.com/blogs/blog/what-is-nvidia-jetson-orin-nano-2) 列出 1536 CUDA 核、LPDDR5X 120GB/s（上代 102.4GB/s），未经官方核实。TOPS 只比上代 67 TOPS 高 16%，带宽也只高约 17%，2 倍推理的剩余部分官方只归因于“改进的 Tensor Core”，是否引入新的低精度格式未披露。8GB 容量把它限定在 2-4B 级 VLM/VLA，这正是 Gemma 4、Qwen 3 小尺寸模型的甜区。

对机器人开发者而言，Orin Nano 2 的意义在于“同尺寸、同 260-pin 接口”的平滑升级：现有载板和散热设计可直接复用，软件栈沿用 JetPack，这是高通、瑞芯微等竞争者短期难以复制的生态壁垒（官方称 Jetson 开发者超 300 万）。但它的局限同样明显：8GB 内存要同时容纳视觉编码器、语言模型、动作头与 KV cache，实际跑 VLA 时可用于 LLM 部分的往往只有 2-3B；而 2027 上半年才供货，意味着今年下半年的入门级机器人仍停留在 Orin Nano Super 上。Deepu Talla 说“中小型前沿模型已达到去年最大模型的精度”，这句话正是 NVIDIA 押注 8GB 档位的理由——赌模型变小的速度快于机器人对能力的需求。

### 四、PC：Wildcat Lake 把 AI PC 推到 15W 入门本

Intel 在 [Hot Chips 2026](https://hotchips.org/program/conference/) 上详解 Core Series 3（Wildcat Lake）：18A 计算 die + 外部工艺平台 die，用有机 MCP 而非 Foveros，UCIe 跑 8 GT/s 以免去重传和 FEC；显示流量在 die 间缓冲，让链路进入低功耗态。规格上（[cnx-software](https://www.cnx-software.com/2026/04/17/intel-core-series-3-wildcat-lake-processor-family-launched-for-entry-level-laptops-and-edge-ai-systems?amp=1)）：2P + 4LPE、2 个 Xe3 核（GPU 21 TOPS）、NPU 15-17 TOPS、单通道 LPDDR5X-7467 最高 48GB、PBP 15W。NPU 不足 40 TOPS，因此不满足 Copilot+ 门槛。

Wildcat Lake 的设计取舍很有代表性：NPU 引擎被缩减而不是取消，GPU 去掉光追却保留 XMX 矩阵单元，内存总线变窄以压低整机成本。这说明 Intel 认为入门笔记本的 AI 负载是视频会议特效、本地语音转写、图像分类这类常驻小模型，而不是本地 LLM。封装上，有机 UCIe 的 bump pitch 约 110µm（先进封装约 36µm），Intel 选择把速率压在 8 GT/s，用更多 lane 换取无需重传和 FEC 的低误码链路，省掉了纠错逻辑的面积和时延；约 29% 的计算 die 可通过降级 SKU 回收，则是 18A 早期良率下控制成本的现实手段。对端侧 AI 的启示是：在低端平台上，单个加速器都很小，NPU、iGPU、CPU 之间的协同调度比任何一个引擎的峰值更重要。

| 平台（8 月节点） | AI 算力 | 内存 / 带宽 | 功耗 | 定位 |
|---|---|---|---|---|
| Intel Wildcat Lake（Core 7 360） | NPU 17 + GPU 21 TOPS | 单通道 LPDDR5X-7467，最高 48GB | 15W / 35W | 入门 AI PC、边缘 |
| Intel Panther Lake（背景） | NPU 5 约 50 TOPS，平台 180 TOPS | LPDDR5X 最高 9.6GT/s | — | 主流 Copilot+ |
| Jetson Orin Nano 2 | 78 TOPS | 8GB，约 120GB/s（Premio） | 15W 模式 | 入门机器人 |
| 玄戒 D100 | 16 核 NPU，TOPS 未披露 | 最高 160GB 统一内存 | 未披露 | 智驾 / AI Cube |

8 月 AMD、联发科、华为、三星、Arm 均无新芯片发布：天玑 9600 系列、麒麟 9050 Pro、Exynos 2700 die shot、Arm C2 均在 9 月披露（见 9 月报告）；三星本月的端侧亮点在存储侧——Hot Chips 的 LPDDR5X-PIM 与 TrendForce 报道的 4nm GAIA PIM 芯片（见 PIM 部分）。

### 五、模型容量对照

| 芯片 | 宣称模型 | 精度 | 内存 / 带宽 | tokens/s（口径） | 来源 |
|---|---|---|---|---|---|
| Tensor G6 | 最新 Gemini Nano（版本未披露） | 未披露 | 12/16GB（媒体），带宽未披露 | 未披露；任务快 3.5 倍 | [Google](https://blog.google/products-and-platforms/devices/pixel/google-pixel-11-pro-xl/) |
| 玄戒 O3 | MiMo 3B（最大规模未披露） | A8W4；定制量化 + 霍夫曼压缩 | 113.8GB/s | 未披露；Prefill +40%、Decode +45% | [IT之家](https://www.ithome.com/0/993/683.htm) |
| 玄戒 O100 | MiMo（报道为 3B） | 未披露 | 1.22TB/s，容量未披露 | 最高 330（官方）；约 295（原型机，媒体） | [爱范儿](https://ifanr.com/1676441) |
| 玄戒 D100 / AI Cube | 200B / 120B + 3B | 未披露 | 最高 160GB | 未披露 | [RITS](https://rits.shanghai.nyu.edu/ai/xiaomi-ai-cube-three-chip-prototype/) |
| Jetson Orin Nano 2 | Gemma 4、Qwen 3、Nemotron、Cosmos（尺寸未披露） | 未披露（Premio 标 INT8） | 8GB，约 120GB/s | 未披露；推理 2× Orin Nano Super | [NVIDIA](https://nvidianews.nvidia.com/news/nvidia-announces-jetson-orin-nano-2-robotics-computer-to-redefine-entry-level-edge-ai) |
| Wildcat Lake | 未披露 | INT8（NPU 5） | 最高 48GB，单通道 | 未披露 | [cnx-software](https://www.cnx-software.com/2026/04/17/intel-core-series-3-wildcat-lake-processor-family-launched-for-entry-level-laptops-and-edge-ai-systems?amp=1) |

用带宽做一个粗略的上限换算（本文推算，未计 KV 与效率损失）：decode 速度上限 ≈ 带宽 ÷ 每 token 读取字节。O3 跑约 2.6bit 的 MiMo 3B 约 1GB/token，上限约 100 tok/s；O100 的 330 tok/s 意味着每 token 读取不超过约 3.7GB；Orin Nano 2 跑 INT4 的 4B 模型（约 2GB）上限约 60 tok/s；Wildcat Lake 若单通道按 64-bit 计约 60GB/s，同一模型上限约 30 tok/s。可见对 decode 而言，O100 的 10 倍带宽比任何一家的 TOPS 提升都更有分量。

### 小结

8 月的三条主线各自回答了一个问题：谷歌回答“端到端体验能否不靠 TOPS 提升”（能，但不给可比数据）；小米回答“手机带宽墙怎么破”（LPDDR6 + 权重压缩是短期解，3D 堆叠 DRAM 的 O100 是长期解，但功耗、容量与量产仍待验证）；NVIDIA 与 Intel 回答“入门级边缘设备的 AI 底线在哪”（8GB/约 120GB/s 的机器人模组，15-17 TOPS 的 15W 笔记本）。9 月天玑 9600 Pro、麒麟 9050 Pro 的“30B MoE”口径，正是建立在本月小米所展示的同一逻辑之上：**带宽和每 token 字节数，而不是 TOPS，决定端侧大模型的可用速度。**

## 4. 低功耗、存内计算与内存：把计算挪到离 DRAM 更近的地方

8月低功耗AI硬件只有一个主题：**把计算挪到离DRAM更近的地方**。Hot Chips 2026（8月23–25日）把“内存”放在了几乎和GPU同等的位置：三星首次给出LPDDR5X-PIM的8B模型实测，d-Matrix用pJ/bit算清了3D DRAM的能耗账，XCENA把注意力计算下放到CXL内存卡。同一周小米发布玄戒O100，用晶圆键合在手机级芯片上做到1.22TB/s。内存价格方面，TrendForce的8月数据显示涨幅在收窄，但价格没有回落，端侧的RAM预算仍然受限。需要说明的是，本月可穿戴和眼镜方向没有经确认的新芯片发布，MCU NPU也没有新品，这一层的硬数字只有Ambiq的财报。

### 一、内存价格：涨幅收敛，不回头

| 指标 | 数值 | 口径/来源 |
|---|---|---|
| 3Q26移动DRAM合约价 | 环比+8–13%（2Q26 LPDDR5X为+78–83%） | [TrendForce 8/3](https://www.trendforce.com/research/download/RP260803NC) |
| 三星3Q26涨幅 | 中个位数；SK海力士、长鑫涨幅更大 | 同上 |
| 买方库存 | 12–14周；4Q26涨幅继续收敛，不回落 | 同上 |
| 2Q26前五大NAND营收 | 688.7亿美元，环比+77%，美光升至第三 | [TrendForce 8/18](https://www.trendforce.com/presscenter/news/20260818-13186.html) |
| 3Q26 NAND合约价 | +10–15%（7月口径）；手机/PC需求疲弱 | 同上 |

这些数字对端侧AI的含义是：2Q26的暴涨已经计入BOM，3Q26在此基础上还要再涨约一成。按9月分析的口径，8GB机型只能常驻3–4B INT4模型，12GB约7–8B（推算）。美光在2Q26主动减少对手机品牌的供货（[TrendForce移动DRAM排名](https://www.trendforce.com/research/download/RP260827LM)），原厂产能继续流向HBM和服务器，2027年旗舰机的RAM容量更多取决于成本谈判，而不是技术需要。所以本月各种“少搬字节”的硬件方案都值得关注。

### 二、PIM与近存：四种做法，一张表

| 方案 | 计算放在哪 | 加速什么 | 关键数字（口径） | 模型（口径） |
|---|---|---|---|---|
| [三星LPDDR5X-PIM](https://www.servethehome.com/samsung-lpddr5x-pim-at-hot-chips-2026/) | 标准LPDDR5X每bank一个MAC块 | Decode GEMV | 内部614 vs 外部76.8GB/s；2.4 TOPS/封装（4bit权重） | Llama-3.1-8B W4A8：27.0→81.3 t/s（官方） |
| [小米玄戒O100](https://equalocean.com/news/2026082522135) | 6nm NPU晶圆+2层DRAM晶圆WoW混合键合 | 完整Decode（NPU执行） | 1.22TB/s；1.4μm间距、258万键合点 | MiMo 3B最高330 t/s（官方） |
| [d-Matrix Raptor](https://servethehome.com/d-matrix-raptor-3d-dram-accelerator-for-generative-inference-at-hot-chips-2026) | N4逻辑die F2F叠在3D DRAM上 | Decode（Prefill交给GPU） | ~100TB/s、32GB/卡；0.37pJ/bit | 72卡跑Kimi K3 1M上下文（目标） |
| [XCENA MX1](https://www.servethehome.com/xcena-mx1-cxl-computational-memory-device-at-hot-chips-2026/) | CXL卡上3072个RISC-V核贴近DDR5 | 注意力/KV、向量检索 | 268.8GB/s本地 vs 64GB/s主机链路；40W | 70B INT8@100K：5.50→17.7 t/s |
| [SK海力士/闪迪 HBF](https://www.trendforce.com/news/2026/08/04/sk-hynix-sandisk-debut-hbf-standard-to-challenge-ai-memory-bottlenecks-with-google-tenstorrent-support/) | NAND堆叠，经UCIe直连 | 只读权重层 | ≤512GB，0.4–3.0TB/s | 数据中心，2027年商用 |
| [谦合益邦](https://news.pedaily.cn/202608/567713.shtml) | 4层3D DRAM堆叠存算 | 云端 | B轮超20亿元；带宽“提升一个数量级”（厂商） | 未披露 |

**第一层区别：PIM改的是内存，近存改的是封装。** 三星保留JEDEC 561-ball封装，可以直接替换LPDDR5X，用Address Align Mode兼容现有内存控制器；但只有GEMV在bank里算，注意力、softmax和采样仍回到主机。O100和Raptor则是把整颗计算die键合在DRAM上，所有算子都能用到近存带宽，代价是容量受键合DRAM层数限制，而且必须定制封装。XCENA处在两者之间：用CXL的内存语义把KV Cache和注意力放到卡上，GEMM仍交给GPU。

**第二层区别：能耗账。** d-Matrix给了一组可以复算的数字：片上SRAM约50fJ/bit，2.5D HBM4约2.5–5pJ/bit，垂直3D I/O约0.3–0.4pJ/bit。按100TB/s算，0.37pJ/bit对应约296W，2.4pJ/bit对应约1.92kW。手机上的LPDDR同样主要花在I/O和PHY上，这也是O100在不提TOPS的情况下只强调带宽的原因。

### 三、几个数字的可复算性

- **三星为什么是3倍而不是8倍。** 内部带宽是外部的8倍，但吞吐只提升3.01倍，总时长只缩短2.28倍。原因是Prefill、注意力和采样仍在主机执行，PIM模式切换和激活广播也有开销（Amdahl定律）。三星此前的仿真称矩阵运算最高6.2倍（[TrendForce转述](https://www.trendforce.com/news/2026/08/26/news-samsungs-4nm-gaia-could-mark-first-pim-commercialization-in-ai-pcs-mass-production-as-early-as-2027/)），实测大约只拿到一半。另一个值得注意的细节：8B INT4权重约4GB，27 t/s意味着每秒约108GB，已经超过单封装x64的76.8GB/s，因此测试平台可能不止一个封装（推算，三星未披露）。上下文只有320 token，长上下文时KV读取会进一步稀释收益。
- **软件代价。** [Chips and Cheese](https://chipsandcheese.com/hot-chips-2026-samsungs-processing)列出了一系列限制：PIM与非PIM访问不能重叠；隔离PIM区域需要独占通道；三星建议使用不可缓存映射；带副作用的读会与预取和推测执行冲突；抢占时要保存每个bank的寄存器。所以首个落地场景更可能是三星自己掌控驱动的AI PC加速器GAIA（4nm，原型已交联想、HP，最早2027年量产，属媒体爆料），手机要等LPDDR6-PIM标准。
- **O100的16倍。** 1.22TB/s ÷ 76.8GB/s（LPDDR5X-9600 x64）≈ 15.9，和官方说的“16倍”吻合；相对LPDDR6-10667 x96（约114GB/s）约为10.7倍。MiMo 3B跑到330 t/s：如果是INT4，每token约1.5GB，需要约0.5TB/s；如果是INT8，每token约3GB，需要约1TB/s，接近带宽的80%（推算）。O100的DRAM容量、TOPS和功耗都没有披露，这是判断它能否承载7–8B模型的关键缺口。
- **XCENA为什么有效。** MX1本地DDR5为268.8GB/s，主机链路只有64GB/s/方向。长上下文Decode的主要开销是KV读取，在卡上就地完成注意力，可以把这4倍的带宽差转化为3.35倍吞吐和3.84倍能效（70B INT8，100K上下文，厂商口径）。

### 四、功耗档位与8月新增数据点

| 功耗档 | 8月新数据点（口径） | 能跑什么 | 约束 |
|---|---|---|---|
| μW–mW（常开） | [Ambiq](https://ambiq.com/news/ambiq-reports-second-quarter-2026-financial-results/) Q2营收3,390万美元（+89.7%），全年指引约1.35亿美元 | 唤醒词、VAD、健康传感（10K–1M参数） | 片上SRAM；靠compressionKIT压缩（称最多20倍，厂商口径） |
| 手机级加速器（功耗未披露） | 小米O100：1.22TB/s | MiMo 3B 330 t/s | 键合DRAM容量未知；2027年商用 |
| ~10–25W（机器人开发板） | [地瓜RDK S100P](https://www.cnx-software.com/2026/08/31/d-robotics-rdk-s100p-a-128-tops-alternative-to-nvidia-jetson-orin-nx-16gb-with-cortex-a78ae-r52-cores/)：128 TOPS、24GB、76.8GB/s、899美元 | 8B INT4约17 t/s上限；3B约40 t/s（推算） | 96bit LPDDR5带宽低于Orin NX（约102GB/s） |
| 车规外挂AI | [BOS Eagle-N](https://www.bos-semi.com/post/bos-semiconductors-presents-chiplet-based-ai-accelerator-eagle-n-at-hot-chips-2026)：250 INT8 dense TOPS/chiplet，可扩展至2000+ | Transformer感知、DMS、生成式AI（未给参数量） | 内存与功耗未披露 |
| 40W板卡（数据中心） | XCENA MX1：芯片40W、板卡90W | 70B INT8长上下文注意力卸载 | 主机链路64GB/s |
| 背景（窗口外） | [Jetson T3000/T2000](https://www.igorslab.de/en/nvidia-jetson-t3000-t2000-blackwell-modules-ai-robots/)（7/15）：865/400 FP4 TFLOPS，T3000为32GB、273GB/s，2027Q1上市 | Cosmos 3 Edge 4B世界模型 | 仍是273GB/s带宽墙 |

### 五、超低功耗与MCU：本月是空档

8月没有检索到ST、NXP、Infineon、Renesas的MCU NPU新品，Syntiant、BrainChip也没有新的产品发布。唯一有数字的是Ambiq：Q2营收同比接近翻倍，GAAP毛利率提升490bp，公司称行业供应紧张限制了增长。它的增长来自SPOT亚阈值工艺和软件（heliaCORE、compressionKIT、heliaPROFILER），而不是加大NPU。这与9月分析的判断一致：0.1–1 TOPS这一档稳定可用的是千万参数级ASR和视觉，十亿参数级LLM还停留在演示阶段。整合方面，Microchip收购Hailo是7月24日宣布的（[evertiq](https://evertiq.com/design/2026-07-29-microchip-technology-signs-definitive-agreement-to-acquire-hailo)），8月只有进展报道，预计9月底完成交割。Hot Chips海报中有几项低功耗学术工作，包括面向可穿戴的RISC-V CGRA（HiVec，A*STAR/NUS）、KAIST的低功耗实时视觉语言导航处理器、Harvard的20-chiplet端侧小模型SiP（Pistil）和Berkeley的Intel 16双芯片多模态平台（Gemmelos），但都没有公开数字（[程序表](https://hc2026.hotchips.org/)）。

### 六、车与机器人：从卖芯片到卖IP，从TOPS到带宽

- **地平线**（[HKEX中报](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0831/2026083101009.pdf)）：收入20.55亿元（+32.9%），毛利率约66%；征程出货221.8万片，仅+12.1%，授权与服务收入11.29亿元（+52.7%），已超过产品收入。征程6B首发量产，征程7预计2027年发布。
- **爱芯元智**（[中报](https://m.rccaijing.com/news-7493186720872724302.html)）：收入4.02亿元（+181.8%），研发5.16亿元（+81%），研发支出高于收入；智驾与边缘推理业务占比14.1%。M97的“等效460GB/s”仍没有给出定义。
- **地瓜S100P**用24GB、128 TOPS和899美元对标Orin NX 16GB，但96bit LPDDR5的带宽偏低。它适合“大容量放模型、小激活参数推理”的机器人小脑和中脑场景。
- **BOS Eagle-N**在Hot Chips的主要观点是：车规AI的竞争力取决于数据在内存与计算之间搬运的效率，而不是TOPS。这和本月存储方向的主线一致。
- 背景：Tesla AI5于4月流片（[TechNode](https://technode.com/2026/04/16/tesla-completes-ai5-chip-tape-out-to-be-manufactured-by-tsmc-and-samsung/)），AI6据报由三星2nm在德州代工、同die面积性能约为AI5的2倍（[Korea Herald](https://www.koreaherald.com/article/10718955)），本月没有经确认的新进展。

### 七、眼镜与可穿戴：没有新硅

本月没有检索到Meta、Google/三星、Rokid、阿里夸克、小米等眼镜的新芯片发布。三星Galaxy Glasses确认将在11月推出，芯片传闻为骁龙AR1，属于爆料（[Android Authority](https://androidauthority.com/samsung-smart-glasses-launch-date-3717873)）。眼镜方向的硬件节奏要看9月的Meta Connect（见9月报告）。由于检索预算用尽，本节可能有遗漏。

### 八、对端侧选型的含义

- **评估加速器时，先问三个数**：外部和近存带宽（GB/s）、可用容量（GB）、每token读取字节数，然后再看TOPS。用“带宽÷每token字节数”可以快速核对厂商给的tokens/s。本月三星的81.3 t/s和小米的330 t/s都能这样核对，也都暴露出口径缺口：三星的测试封装数、小米的精度与容量都没有披露。
- **PIM对软件栈的要求高于对硬件的要求**：要拿到三星PIM的收益，需要内核把权重按bank感知方式布局，运行时要处理PIM与非PIM访问互斥，量化格式要对齐PIM的15种精度组合。像k-quants这类按块混合精度的格式不能直接映射。手机厂商如果在2027–2028年考虑LPDDR6-PIM，现在就应该评估推理框架能否把GEMV单独切出来。
- **闪存层要提前规划**：HBF说明业界正在把“只读权重放闪存”做成标准。端侧对应的是UFS 5.0加MoE专家卸载，但NAND同样在涨价。对中端机，比追加容量更实际的做法是提高专家缓存命中率，并配合投机解码减少随机读取。
- **机器人平台的选择**：S100P（24GB/76.8GB/s）适合装下较大的模型、以较低频率推理；需要7–8B VLM骨干并保持10Hz以上控制频率的场景，带宽仍然要到200GB/s以上（S600、J6P、Thor这一档）。

### 小结

1. **8月的关键词是“带宽/W”**：三星PIM（内部8倍、端到端3倍）、小米O100（1.22TB/s，约为LPDDR5X的16倍）、d-Matrix（0.37 vs 2.4pJ/bit）从三个尺度得出同一个结论，Decode的成本主要在搬运数据。
2. **PIM和近存会长期并存**：PIM兼容标准、容易替换，但只加速GEMV并需要OS配合，最早2027年通过AI PC（GAIA）落地；混合键合近存带宽高一个数量级，但容量和成本受限，O100要到2027年商用才能检验。
3. **内存价格涨幅收窄，但价格本身没有回落**：3Q26移动DRAM仍涨8–13%、NAND涨10–15%，端侧模型预算继续被限制在3–8B INT4，这反过来提高了低比特量化、MoE卸载和近存方案的价值。
4. **低功耗层本月是空档**：MCU NPU与眼镜芯片没有新品；车与机器人方向的增长正从卖芯片转向卖IP（地平线），从堆TOPS转向补带宽（Eagle-N、S100P）。

## 5. Hot Chips 2026 与顶会论文

**判断：** Hot Chips 2026（8/23–25，Stanford）几乎是一届“数据中心大会”，真正面向端侧的正式演讲只有 Intel Wildcat Lake、三星 LPDDR5X-PIM 与两场车载（Waymo、BOS）。但贯穿全场的主线对端侧同样成立：**决定推理体验的是数据在内存与计算之间搬得多快，而不是峰值 TOPS**。三星把 MAC 放进 LPDDR bank、Waymo 把整个模型编译进 64 MB SRAM、NVIDIA 用全 SRAM 的 Groq LPU 接管 decode，是同一思路在三种功耗档位上的落地；同月上 arXiv 的 MICRO 2026 论文（PFM、NOVA、EdgeXpert、HBQ）则在补软硬件协同的空缺。

> 口径说明：Hot Chips 条目按演讲内容标为“官方”，数字多经 [ServeTheHome](https://www.servethehome.com/) 现场博客与 [SemiWiki](https://semiwiki.com/semiconductor-manufacturers/intel/372653-intel-wildcat-lake-right-sizing-silicon-without-sinking-performance/) 转述胶片；论文数字均为作者自报（仿真或 ASIC 综合结果）。完整议程见 [官方程序](https://hc2026.hotchips.org/program/)。

### 一、Hot Chips 2026：端侧相关演讲总览

| 主题 | 演讲 | 关键数字（官方口径） | 对端侧的含义 |
|---|---|---|---|
| AI PC / 客户端 | [Intel Core Series 3 “Wildcat Lake”](https://www.servethehome.com/intel-core-series-3-wildcat-lake-cpu-at-hot-chips-2026/) | 18A 计算 die；NPU 1 tile/17 TOPS，GPU 20 TOPS，平台 40 TOPS；64-bit LPDDR5X-7467 | AI PC 下探入门价位，内存位宽减半是本地 LLM 的硬伤 |
| 存内计算 | [Samsung LPDDR5X-PIM](https://www.servethehome.com/samsung-lpddr5x-pim-at-hot-chips-2026/) | 16 个 bank 级 PIM 块；内部 614 GB/s（8×）；Llama-3.1-8B 81.3 vs 27.0 tokens/s | 首个产品级 LPDDR PIM，直击 decode 带宽墙 |
| 近存计算 | [XCENA MX1（与三星联合）](https://chipsandcheese.com/p/hot-chips-2026-xcena-and-samsungs) | Samsung 4nm；3,072 个 RISC-V 核；~3 TFLOPS；芯片 40 W | 服务器产品，其分层内存思路可借鉴 |
| 车载 | [Waymo 传感器融合处理器](https://servethehome.com/waymo-sensor-fusion-processor-at-hot-chips-2026/) | N5、208 mm²、<75 W；160 TOPS INT8 / 80 TFLOPS FP16；64 MB SRAM | 为一个模型定制的确定性数据流 NPU |
| 车载 | [BOS Eagle-N](https://www.bos-semi.com/post/bos-semiconductors-presents-chiplet-based-ai-accelerator-eagle-n-at-hot-chips-2026) | chiplet 扩展、NPU 虚拟化；工艺/TOPS 本次未披露 | 车载 SoC 走向 chiplet 组合 |
| Physical AI | [AMD Versal Premium Gen2](https://servethehome.com/amd-versal-premium-gen2-at-hot-chips-2026/) | 7.6K DSP；封装内 LPDDR5X 省约 60% 面积；PQC | 安全与确定性控制环成为硬件需求 |
| 参考 | [NVIDIA Groq 3 LPU](https://www.servethehome.com/nvidias-groq-3-lpu-accelerators-for-heterogeneous-ai-compute-at-hot-chips-2026/) | 每架 256 LPU / 128 GB SRAM / 40 PB/s；Gemma 4 31B 11,000 tokens/s | prefill/decode 异构解耦的样板 |

### 二、AI PC：Wildcat Lake 的“减法”

Wildcat Lake 是本届唯一的客户端 CPU 演讲。它从 Panther Lake U 衍生，保留工艺节点与主要 die 划分，几乎所有资源都砍一半左右：P 核 4→2、L3 12→6 MB、GPU 4→2 个 Xe 核（40→20 TOPS）、**NPU 3 tile/53 TOPS → 1 tile/17 TOPS**，内存从 128-bit LPDDR5X-9600 降到 64-bit LPDDR5X-7467，计算 die 面积因此缩小 38%。封装放弃 Foveros，改为有机 MCP（50×25 mm → 35×25 mm），UCIe 的 bump pitch 从 36 µm 放宽到 110 µm，链路限速 8 GT/s，省掉重传与 FEC；多级链路状态让空闲功耗最多降 8×。Intel 对 Core 7 150U 宣称 AI 性能 2.7×、处理器功耗低 64%（[SemiWiki 转述官方胶片](https://semiwiki.com/semiconductor-manufacturers/intel/372653-intel-wildcat-lake-right-sizing-silicon-without-sinking-performance/)），已有 70+ 个设计订单（[STH](https://www.servethehome.com/intel-core-series-3-wildcat-lake-cpu-at-hot-chips-2026/)）。

对端侧的读法：17 TOPS 的 NPU 不满足 Copilot+ PC 的 40 TOPS 门槛，定位是常驻小模型与 POS、机器人这类边缘设备；而 64-bit 内存让带宽较 Panther Lake U 少一半以上，7–8B 级本地 LLM 的 decode 会明显变慢。**同一价位上，PIM 恰好补的就是这块短板。**

### 三、存储与内存：LPDDR 里开始“算”了

三星的 [LPDDR5X-PIM](https://www.servethehome.com/samsung-lpddr5x-pim-at-hot-chips-2026/) 是本届对端侧意义最大的演讲：

- **架构**：16 个 bank 各有一个 PIM 块，内含 MAC 树，ALU 支持 FP/INT，共 15 种精度组合；SINT4 权重下每封装 2.4 TOPS，FP8 约 1.2 TFLOPS。x64 9600 Mbps 下 PIM 内部带宽 614 GB/s，是常规接口 76.8 GB/s 的 8×。
- **兼容性**：Address Align Mode 把 DRAM 地址映射成 MAC 指令，普通内存控制器即可驱动，封装为 JEDEC 标准 561-ball；运算由 WRPB 写激活、PIMX_RD 读权重、PIMX_WR 写部分和组成。
- **实测**（三星官方初步测试，自家边缘 AI SoC）：Llama-3.1-8B（W4A8，320 token）81.3 vs 27.0 tokens/s（3.01×）。**功耗、面积开销未披露。**
- **落地**：据 [TrendForce](https://www.trendforce.com/news/2026/08/26/news-samsungs-4nm-gaia-could-mark-first-pim-commercialization-in-ai-pcs-mass-production-as-early-as-2027/) 援引韩媒，System LSI 的 4nm AI PC 加速器 GAIA 将首个集成 LPDDR5X-PIM，原型已交 Lenovo、HP，最早 2027 年量产；LPDDR6-PIM 的 JEDEC 规范接近定稿。[韩国中央日报](https://www.koreajoongangdaily.com/business/samsung-bets-on-pim-while-sk-hynix-keeps-eye-on-hbm/12846274)则强调三星把它定位为手机/平板推理内存，而 SK hynix 仍押注 HBM。

同场的 [XCENA MX1](https://chipsandcheese.com/p/hot-chips-2026-xcena-and-samsungs) 走另一条路：在 CXL 卡上放 3,072 个 1.1 GHz RISC-V 核和 24 个向量引擎，挂 2 TB DDR5，还能把 SSD 当字节寻址内存（DRAM 以 64 KB 页缓存）。它面向服务器（芯片 40 W），但“SSD→DRAM 页缓存 + pinned prefix”的分层思路与端侧闪存卸载、KV 分层同构。Memory 教程中，d-Matrix 把 TSMC 4nm 计算 die 以 36 µm pitch 面对面键合在定制 DRAM 上，每卡 100 TB/s（[Tom's Hardware 标题口径](https://www.tomshardware.com/tech-industry/semiconductors/d-matrix-stacks-its-ai-accelerator-directly-on-custom-dram-for-100-tbs-per-card)），代表 3D DRAM 的更远期方向。

### 四、车载与 Physical AI：确定性比峰值重要

[Waymo 传感器融合处理器](https://servethehome.com/waymo-sensor-fusion-processor-at-hot-chips-2026/)是 Waymo 首次公开自研芯片细节：N5、208 mm²、<75 W，carTPU 阵列 16 个 PE（控制 PE 为带向量扩展的双核 RISC-V），160 TOPS INT8 / 80 TFLOPS FP16，64 MB 片上 SRAM + 封装内 LPDDR5X 273 GB/s。它只运行基础模型栈中的传感器融合编码器，驾驶 VLM 不在其上。软件上，AOT 编译把整模型做成 mega-kernel 切进 SRAM，静态形状、无缓存无分支，以“首像素到 embedding”的低 batch 延迟为指标；相机 ISP、去马赛克、编解码都自研，YUV 金字塔只落后传感器读出几百行。Waymo 称该芯片已在第六代车辆的运营车队中运行；端到端毫秒数未披露。

[BOS Eagle-N](https://www.bos-semi.com/post/bos-semiconductors-presents-chiplet-based-ai-accelerator-eagle-n-at-hot-chips-2026) 强调 chiplet 按车型扩展、NPU 虚拟化，以及以数据搬运为中心的 NPU（共享内存、NoC、专用搬运处理器）。官方稿未给 TOPS；此前合作方口径为 250 TOPS dense、基于 Tenstorrent Tensix。[AMD Versal Premium Gen2](https://servethehome.com/amd-versal-premium-gen2-at-hot-chips-2026/) 则把 Physical AI 的需求具体化：约 10 µs 的控制环、10–40 ms 的反应窗口，加上内联内存加密、PCIe IDE、后量子密码；内存从 HBM 改为封装内 LPDDR5X。

海报区还有几项端侧工作：UC Berkeley 的 Gemmelos（Intel 16 双芯片多模态边缘 AI 平台，据社交媒体消息获最佳学生海报亚军）、KAIST 带 3D 空间推理的低功耗视觉-语言导航处理器、A\*STAR/NUS 面向可穿戴的 HiVec CGRA，以及 KU Leuven/TU Delft 的 ETHEREAL 事件相机 GNN 处理器（详见下文）。

### 模型容量与吞吐对照（仅列有公开数字的项）

| 平台 | 模型 / 精度 | 吞吐或延迟 | 口径 |
|---|---|---|---|
| 三星边缘 SoC + LPDDR5X-PIM | Llama-3.1-8B，W4A8，320 token | 81.3 tokens/s（常规 LPDDR5X 为 27.0） | 官方初步测试 |
| NVIDIA LPX 机架（256 LPU） | Gemma 4 31B | 11,000 tokens/s（整架） | 官方，含第三方基准 |
| Waymo 传感器融合芯片 | 传感器融合编码器（参数量未披露） | 未披露毫秒数 | 官方 |
| Intel Wildcat Lake | 未给出模型 | 平台 40 TOPS；对 Core 7 150U AI 性能 2.7× | 官方 |
| EdgeXpert（28nm 综合） | Qwen3-30B-A3B 等 MoE | 延迟最多 −56.3% | 论文 |
| Block-Diffusion 加速（建模） | 1.5B / 7B block-diffusion LLM | 延迟 2.88× / 4.44× | 论文仿真 |

这张表反映出一个事实：除三星外，本届几乎没有厂商给出端侧 LLM 的 tokens/s。客户端芯片依旧只报 TOPS，车载芯片只报“实测加速比”的定性说法，可比较的实测数据仍主要来自学术论文和存储厂商。对做选型的工程师来说，有两点值得注意：第一，三星 3.01× 的提升是在同一颗 SoC 上换内存得到的，说明这台 8B 模型的瓶颈几乎完全在带宽；第二，按 Wildcat Lake 64-bit LPDDR5X-7467 的位宽和速率推算，峰值带宽约 60 GB/s（推算值，非官方），低于三星测试用的常规 LPDDR5X 接口（76.8 GB/s），8B 级模型在这类入门 AI PC 上很难达到可用的交互速度。

### 五、顶会论文（arXiv 首发于 8 月）

**PIM / 近存**

| 论文 | 会议 | 核心机制 | 关键结果 |
|---|---|---|---|
| [PFM](https://arxiv.org/abs/2608.06989)（计算所） | MICRO'26 | NPU-PIM 双视图内存，物理布局与逻辑视图解耦 | 吞吐最高 2.32× |
| [NOVA](https://arxiv.org/abs/2608.22613)（KAIST） | MICRO'26 | 4F² VCT DRAM + 外围 die/base die 两层近存 | 对 GPU 吞吐 4.5×、能效 5×，面积 +3.9% |
| [DRAM-PIM-GPU 设计原则](https://arxiv.org/abs/2608.04169) | SOCC'26 | 计入静态功耗的系统评估 | 只算动态功耗会把 tokens/s/W 高估最多 3.85× |
| [ReVolt](https://arxiv.org/abs/2608.08496) | ESWEEK'26 | LSTM 预测 PDN，动态调整 OU 大小 | 无跌落违例，EDP 平均 −76× |

PFM 回答的正是 LPDDR5X-PIM 进入 SoC 后的问题：prefill/decode 相变与 MoE 路由会让同一张量的最优执行设备在运行时变化，静态映射浪费带宽。SOCC 论文则提醒：三星没披露的功耗恰恰关键，batch=1 场景下 DRAM 刷新与漏电可能主导能效。

**端侧 LLM / MoE 与低比特**

- [EdgeXpert](https://arxiv.org/abs/2608.05303)（KAIST，MICRO'26 Distinguished Paper 专场）：解决 MoE 与投机解码的不兼容——prefill 阶段做 prompt 级专家复用，decode 阶段按深度合并专家、只取显著通道；Samsung 28nm @800 MHz，延迟最多 −56.3%、能耗最多 −44.1%。
- [APEX](https://arxiv.org/abs/2608.11688)（CODES'26）：在 attention 前预测专家并按置信度预取，重叠准确率 >99%，延迟最多 −26%、EDP 最多 −41%；纯运行时方案，可直接用在现有 SoC 上。
- [HBQ](https://arxiv.org/abs/2609.00450)（MICRO'26）：大块 + 尾数二级缩放，W4A5 达到 W4A16 精度且面积小于 NVFP4；28nm ASIC 的面积/能效比 SOTA 仅权重量化高 2.3×/4.6×。
- [UnionSparse](https://arxiv.org/abs/2608.09291)（ESWEEK/TCAD）：W4A4 下稀疏元数据成为瓶颈，提出 PMR 指标，比 SpInfer 快 1.43×、比 cuBLAS 快 3.46×。
- [mzCache](https://arxiv.org/abs/2609.01338)（MobiCom'26）：手机多任务时 OS 会回收 LLM 权重与 KV，利用统一内存让 GPU 推理与 CPU 恢复并发，TTFT 降 2.1–5.5×（llama.cpp/Android）。

**具身智能与感知**

- [Deltoris](https://arxiv.org/abs/2608.04428)（MICRO'26）：diffusion VLA 需要 50–200 Hz 控制频率；只计算相邻输入差分中的比特，再用投机推理摊薄片外访存，比移动 GPU 快最多 34.2×。
- [DeGS](https://arxiv.org/abs/2608.02099)（MICRO'26）：把 3DGS 渲染拆成解析→重组→混合三级，28nm，对 GSCore 等吞吐 2.36–7.25×，1024 PE 时利用率仍 >80%。
- [ETHEREAL](https://arxiv.org/abs/2608.17787)（Hot Chips 海报，投 JSSC）：首颗事件驱动 GNN 芯片，VGA 事件流每次推理 25.6 µs / 1.6 µJ（实测）。
- [Block-Diffusion LLM 边缘加速](https://arxiv.org/abs/2609.01084)（arXiv）：宽 I/O LPDDR + 低秩/INT8 KV + 低比特 FFN delta，在建模的 Jetson 级平台上 7B 模型延迟 4.44×、能耗 3.96×，精度损失 <1 个百分点。

### 小结

1. **端侧的带宽墙已有产品级解法。** LPDDR5X-PIM 在 8B 模型上实现 3×，GAIA 可能在 2027 年把它带进 AI PC；手机大概率要等 LPDDR6-PIM。待验证的是功耗，以及 NPU 与 PIM 之间的数据布局与调度（PFM 方向）。
2. **AI PC 下探靠“减法 + 封装”。** Wildcat Lake 用有机 MCP + 低速 UCIe 降成本，NPU 保留但缩到 17 TOPS，内存位宽减半；低端 AI PC 的本地 LLM 能力将由内存而非 NPU 决定。
3. **车载与机器人芯片转向“为模型定制的确定性数据流”。** Waymo 把整模型编进 SRAM，Groq LPU 用静态调度跑 decode，学界的 Deltoris/EdgeXpert 用比特稀疏与投机执行减少访存，思路一致。
4. **低比特格式的竞争从“几 bit”转到“怎么缩放”。** HBQ 证明块量化的块大小与二级缩放决定面积与精度，UnionSparse 证明低比特之后稀疏元数据成了新瓶颈；下一代手机 NPU 的数值格式选择（MX、NVFP4 或自定义块浮点）值得持续跟踪。
5. **信息缺口**：本节未系统覆盖 ISLPED 2026 等其他 8 月会议（本轮检索额度用尽）；Tom's Hardware 对 HBF、d-Matrix 的全文未能读取，相关数字仅取标题口径。

## 6. 8 月 arXiv 端侧硬件论文精选

8 月（2026-08-02 ~ 09-01）arXiv 上的端侧 LLM 硬件与系统论文，主线仍是**MoE + 外存分页**，但重点从“能不能装下”转到“装下之后速度能不能用”。真机结果多数来自 Jetson、消费级 PC GPU 和 Apple Silicon，手机 NPU 上的实测反而少。手机方向本月最值得看的是系统层工作：OS 回收内存后模型多快能恢复、提示词怎样改变能耗。硬件侧有两个亮点，一是 FP4 微缩放格式的改进（AdaMX，22nm 综合 + P&R），二是 KAIST 的近存架构 NOVA（MICRO 2026）。本月没有新的流片实测，存内/近存论文全部是仿真或综合结果，下文逐条标明口径。

（本节不重复 EdgeXpert、NPU-PIM 双视图内存、Deltoris 和块扩散 LLM 加速器这 4 篇种子论文。）

### 一、MoE 外存分页：从“能装下”到“能用”

- [FreeToken](https://arxiv.org/abs/2608.16157)（UC Berkeley / UT Austin 等）是本月真机结果最强的一篇。它不固定卸载策略，而是把专家驻留、CPU–GPU 执行、agent 状态复用和内存管理放在一起，按机器实际资源动态映射。论文报告：RTX 5090 上 Qwen3.6-35B 跑 77–83 tok/s，DeepSeek-V4-Flash 284B 跑 22–25 tok/s（约为最佳基线的 1.5–2.3×）；8 GB RTX 4060 笔记本上 35B 模型跑到 39.3 tok/s；单张工作站 GPU 上 GLM-5.2 753B 跑 14.9 tok/s，llama.cpp 为 7.3 tok/s。这是 PC 平台的结果，结论是主机 DRAM 和 PCIe 带宽决定上限，对“AI PC 该配多大内存”有直接参考价值。
- [S2-MoE](https://arxiv.org/abs/2608.15018)（北京大学，李萌组）把投机解码和 MoE 放在一起考虑。按路由感知动态扩展投机长度、复用已加载专家做验证，在 llama.cpp 上实现，Jetson Orin 系列上加速 1.3–5.3×（平均约 2.0×）。Orin NX 16 GB 上 GPT-OSS-120B 从 0.95 提到 1.44–2.45 tok/s，OLMoE 从 2.30 提到 12.08 tok/s。
- [NeuroPrefetcher](https://arxiv.org/abs/2608.22643)（Kennesaw State，ICPP 2026）针对稠密模型的“模型大于内存”场景。它观察到相邻 token 间 82–85% 的活跃神经元保持不变，于是只从 NVMe 预取增量行。Jetson AGX Orin + 990 PRO、14 GiB 预算下，Mistral-7B FP16 跑 3.22 tok/s，llama.cpp 为 0.34 tok/s（7.9–12.0×）。论文还报告，在同一设置下 20 个推理框架中有 12 个生成前就失败。
- [APEX](https://arxiv.org/abs/2608.11688)（UW–Madison，Ogras 组）在 attention 之前用轻量预取路由器预测专家，并按置信度决定多取几个，重叠准确率 >99%。这是**仿真结果**（TSMC 28nm RTL 综合 + 周期级协同仿真，Jetson Orin/Thor 级平台）：Granite-3B 11.41 ms/token，比 ProMoE 低 26%；在 32 GB/s 手机级带宽下延迟仍低 14–42%。
- 两篇“校准型”工作：[Cacheable by Design?](https://arxiv.org/abs/2608.18261) 在 RTX 3070 8 GB + PCIe3 NVMe 上实测 Qwen3-235B Q4 只有 0.44 tok/s，与 2.4 GB/s SSD 带宽模型一致；13.4% 的 LRU 专家缓存能命中 66% 请求；训练路由局部性可以让 miss 降 60%，但通不过 ≤1% 困惑度门槛（预注册的负结果）。[RotaryQuant](https://arxiv.org/abs/2608.08081)（Cognizant）在 M4 Max 上让 Nemotron-H 120B 的峰值内存降到 17.2 GB、跑 14.85 tok/s，但作者自己的消融显示，3-bit KV 让 Gemma4 从 109.8 掉到 20.6 tok/s，触发专家换出后约 1 tok/s，属于“用速度换装得下”。
- [SAEM](https://arxiv.org/abs/2608.21614)（NUS，Tulika Mitra 组）发现思维链推理的同一阶段内，专家激活一致性达 89.3%，据此做阶段感知缓存，平均 1.33×。不过实验平台是 A100 + Xeon 模拟受限内存，不是端侧设备。

判断：PC 和 Jetson 上，百亿到千亿级 MoE 已经能跑到可交互的速度（十几到几十 tok/s），前提是有低比特格式和足够的主机内存。纯闪存分页的速度仍然在个位数 tok/s，与上月手机上的结论一致：**预测准确率和读放大**才是瓶颈。

### 二、手机系统：多任务、投机草稿与 CPU 低比特

- [mzCache](https://arxiv.org/abs/2609.01338)（首尔大学 / UC Berkeley，MobiCom '26）是本月最“手机原生”的一篇。它关注 Android 在多任务下回收 LLM 内存（权重 + KV）之后的恢复速度。做法是把 LLM 内存切成细粒度共享缓冲区以便部分回收，再利用统一内存让 GPU 先算、CPU 同时恢复。在 Galaxy S25+ 和 OnePlus 12（12 GB LPDDR5X，UFS 4.0）上，TTFT 比从存储重载快 2.1–5.5×；全量被回收时，比 Android 自身换页快 2.5–3.0×（S25+）到 9.2–25.9×（OnePlus 12）。45 分钟真实多任务测试中，基线每轮都被 LMK 杀掉，mzCache 存活。代价是峰值功耗 19.2 W 对 14.6 W，但总能耗更低。模型只有 Qwen3-0.6B / EXAONE-1.2B，只用 GPU。
- [MemSpec](https://arxiv.org/abs/2608.10362)（庆北大学，LCTES '26）指出，边缘设备上投机解码的问题不在“选哪个草稿模型”，而在“选中的草稿是否在内存里”。Jetson Orin Nano 8 GB 只能同时放 2 个草稿模型，MemSpec 用预测器主动管理驻留集，吞吐比静态草稿高 58.8%，比 bandit 自适应高 40.7%，达到 oracle 的 95–97%。论文只给相对值，绝对 tok/s 未披露。
- [Llama-Mobile](https://arxiv.org/abs/2608.21134)（Graphcore Research / Arm）提出约 2.7 bit/参数的 S3D8 格式（INT8 激活），把 Llama 3.2 11B Vision 从 21.3 GB 压到 3.7 GB。VQA 平均分 0.661，bf16 为 0.744。Pixel 8a 的 CPU 上解码 3.8 tok/s（INT8 版本放不下）；Graviton4 上 36.8 tok/s，INT8 为 26.4 tok/s。这说明中端手机已能跑 11B 多模态模型，但 CPU 解码仍受带宽限制。
- [ANE 权重编码](https://arxiv.org/abs/2608.22110)（独立研究者）是一个方法论提醒。在 M1 的 Core ML 路径上，fp16 小模型 331 个算子中 0 个落到 ANE，整体在 CPU 上跑；int8 / 三值版本 335 个中 324 个落到 ANE，延迟 1.458 → 0.770 / 0.638 ms。也就是说，部分“量化加速”其实是**执行单元换了**。模型只有 28M–51M，置信度中等。

### 三、实测与能耗：Jetson 三代对比、提示词能耗

- [Hydra](https://arxiv.org/abs/2608.25053)（Northeastern 等，IISWC 2026）用同一套 schema 测了 AGX Xavier → Orin → Thor 三代、13 个 1.2–8.5B 模型、5 种格式，公开约 10.7 万条逐 prompt 记录。Q4_K_M 下 7–8B 模型解码：Thor 35–44 tok/s，Orin 22–28，Xavier 13–16。Qwen2.5-7B Q4 每 token 能耗 Orin 1867 mJ，Thor 1493 mJ：Thor 功耗更高，但每 token 能耗更低。另一个反直觉结果是 6-bit 格式的功耗常常高于 8-bit。
- [提示词与能耗](https://arxiv.org/abs/2609.01798)（Georgia State / 丰田北美）在 Pixel 8 Pro / Pixel 7 上用 MLC-LLM 跑了 7,620 次实验。每 token 预填充能耗是解码的 3–6×；措辞变化（如 CoT）主要通过增加 token 数影响能耗；认知负载高的任务会把 Qwen2.5-1.5B 的每 token 解码能耗推到 1.29×。注意 CPU/GPU 被锁在低频，绝对值偏低。
- [GreenBench](https://arxiv.org/abs/2608.28667) 在 M4 Pro 48 GB 上用 Ollama 测 3–9B 模型（Llama 3.2 3B 175.9 tok/s，Gemma 2 9B 42 tok/s）。但它报告的 0.47 W 封装功耗不合理，系统功耗是估算值，**只建议引用吞吐数据**。

### 四、低比特数据通路：FP4 与三值

- [AdaMX](https://arxiv.org/abs/2608.03867)（Brown / Michigan / Google）是本月最值得 NPU 设计者看的一篇。MXFP4 精度损失大，原因是每个块的元素格式和精度恢复方案固定。AdaMX 把闲置的共享指数位改作元数据，按块选择恢复方案、按操作数选择表示，等效位宽不变。精度上，常识推理和 MMLU 分别收回 MXFP4 损失的 83% 和 82%（对 NVFP4 为 43% / 27%）。硬件是 **22nm FD-SOI 综合 + P&R**（500 MHz / 0.8 V，未流片）：阵列面积 2.16 vs 2.10 mm²，功耗 482 vs 466 mW，峰值 8.19 TOPS、17.1 TOPS/W；系统能耗最多 +1.1%，在 4.25 bit/元素工作点反而降 2.9–5.2%。
- [三值 LLM 统一查表](https://arxiv.org/abs/2608.03229)（深圳 LuxiTech / 港科大 / 华科）把运行时 K/V 存成多平面有符号数位，让 attention 和三值投影共用一套 LUT 引擎。TSMC 40nm 综合加周期级仿真：编码器只增加 LUT 核 2.2–3.9% 的面积（另建一套 attention 阵列要 +64.5–254.4%），片外访存降 40.5%（BitNet-2B）到 57.3%（OPT-2.7B）。
- [Ankhdjet](https://arxiv.org/abs/2608.26206)（独立研究者）是开源版本的“权重写进掩膜”（对标 Taalas HC1）。它把 BitNet b1.58 检查点编译成 SKY130 上 compute-in-ROM 的通孔掩膜，DRC/LVS 两次签核为零，已投 TinyTapeout 班车，硅片预计 2027 年。130nm 下每个权重 2.21 µm²，装不下实用模型，更多是方法学价值。

### 五、存内/近存/存内闪存（全部为仿真或建模）

- [NOVA](https://arxiv.org/abs/2608.22613)（KAIST，MICRO 2026）针对 GQA + SSM + MoE 混合模型，把 4F² 垂直沟道（VCT）DRAM + peri-over-cell 结构（同面积约 2× 密度）和两级 NMP 结合。Ramulator2 周期级仿真 + 14nm 综合：相对 H100 平均吞吐 4.5×，端到端延迟降 69.8%；面积开销 +3.94%（5.55 mm²）。面向数据中心 HBM，但“按算术强度分层”的思路可以借鉴到 LPDDR-PIM。
- [IBM DRAM-PIM-GPU 设计原则](https://arxiv.org/abs/2608.04169)（IBM Research Zurich，SOCC 2026）给端侧 PIM 泼了冷水：只算动态功耗会把 tokens/s/W 高估最多 3.85×，静态功耗（漏电、刷新、GPU 空闲）占系统 66–69%；batch=1 时 PIM 只能和 GPU 打平，改进负载映射最多再提 5.6%。这与 Samsung LPDDR5X-PIM 的商用叙事形成对照，值得一起读。
- [NITRO](https://arxiv.org/abs/2608.11920)（西江大学，DATE 2026 扩展版）指出 NAND 存内计算的瓶颈是把激活写回 TLC，而不是读权重；改用 DRAM 缓冲激活后单项收益 4.07×。论文的 287× 等倍数是相对较弱的基线，也没有精度评估，参考价值有限。
- [事件驱动稀疏 LM](https://arxiv.org/abs/2608.30439)（Aarhus / UCSC / Harvard，MCSoC 2026）在线性注意力模型上诱导激活稀疏，乘加减少最多 76%。在 Loihi 2 实测稠密基线之上**建模推算**：prefill 3.5×、生成 5.4×；对比 Jetson 上同级 transformer，吞吐最高 37×、功耗低 16×。模型只有 370M–2.7B，可看作常驻 AI 的上限参考。

### 汇总表

| 论文 | 机构 | 发表 | 平台/口径 | 关键数字 |
|---|---|---|---|---|
| [FreeToken](https://arxiv.org/abs/2608.16157) | UC Berkeley / UT Austin | arXiv | 真机：RTX 4060 笔记本 ~ RTX PRO 6000 | 284B 22–25 tok/s（5090）；753B 14.9 tok/s |
| [S2-MoE](https://arxiv.org/abs/2608.15018) | 北京大学 | arXiv | 真机：Jetson Orin NX/AGX | 平均约 2.0×，最高 5.3× |
| [NeuroPrefetcher](https://arxiv.org/abs/2608.22643) | Kennesaw State | ICPP 2026 | 真机：AGX Orin + NVMe | 7.9–12.0× 对 llama.cpp |
| [APEX](https://arxiv.org/abs/2608.11688) | UW–Madison | arXiv | 仿真：28nm 综合 | 重叠 >99%，延迟 −26% |
| [Cacheable by Design?](https://arxiv.org/abs/2608.18261) | U. Cumberlands | arXiv | 真机：RTX 3070 + NVMe | 235B 0.44 tok/s；miss −60% 但精度不过关 |
| [RotaryQuant](https://arxiv.org/abs/2608.08081) | Cognizant | arXiv | 真机：M4 Max | 120B @ 17.2 GB，14.85 tok/s |
| [SAEM](https://arxiv.org/abs/2608.21614) | NUS | DAC 2026 扩展 | A100 模拟受限内存 | 1.33× 平均 |
| [mzCache](https://arxiv.org/abs/2609.01338) | 首尔大学 / UC Berkeley | MobiCom '26 | 真机：Galaxy S25+、OnePlus 12 | TTFT 2.1–5.5×；对 Android 换页最高 25.9× |
| [MemSpec](https://arxiv.org/abs/2608.10362) | 庆北大学 | LCTES '26 | 真机：Orin Nano 8 GB | 吞吐 +40.7–58.8% |
| [Llama-Mobile](https://arxiv.org/abs/2608.21134) | Graphcore / Arm | arXiv | 真机：Pixel 8a CPU | 11B VLM 3.7 GB，3.8 tok/s |
| [ANE 权重编码](https://arxiv.org/abs/2608.22110) | 独立研究者 | arXiv | 真机：M1 / M3 | int8 落 ANE，延迟 1.9× |
| [Hydra](https://arxiv.org/abs/2608.25053) | Northeastern 等 | IISWC 2026 | 真机：Xavier / Orin / Thor | 7–8B Q4：Thor 35–44 tok/s |
| [提示词能耗](https://arxiv.org/abs/2609.01798) | Georgia State / 丰田北美 | arXiv | 真机：Pixel 8 Pro / 7 | prefill 每 token 能耗为 decode 的 3–6× |
| [GreenBench](https://arxiv.org/abs/2608.28667) | PCCOE / Red Hat | arXiv | 真机：M4 Pro（功耗口径存疑） | 3B 175.9 tok/s |
| [AdaMX](https://arxiv.org/abs/2608.03867) | Brown / Michigan / Google | arXiv | 22nm 综合 + P&R | 收回 MXFP4 损失 82–83%，17.1 TOPS/W |
| [三值 LUT + 数位 KV](https://arxiv.org/abs/2608.03229) | LuxiTech / 港科大 / 华科 | arXiv | 40nm 综合 + 仿真 | 访存 −40.5–57.3% |
| [Ankhdjet](https://arxiv.org/abs/2608.26206) | 独立研究者 | arXiv | SKY130 签核，已投片 | 0.98–1.73 pJ/权重（仿真） |
| [NOVA](https://arxiv.org/abs/2608.22613) | KAIST | MICRO 2026 | 仿真 + 14nm 综合 | 对 H100 4.5× 吞吐 |
| [IBM PIM 原则](https://arxiv.org/abs/2608.04169) | IBM Research Zurich | SOCC 2026 | 系统仿真 | 只算动态功耗高估 3.85× |
| [NITRO](https://arxiv.org/abs/2608.11920) | 西江大学 | DATE 2026 扩展 | 仿真 | DRAM 激活缓冲 4.07× |
| [事件驱动 LM](https://arxiv.org/abs/2608.30439) | Aarhus / UCSC / Harvard | MCSoC 2026 | Loihi 2 建模 | 生成 5.4×；对 Jetson 功耗低 16× |

### 端侧“能跑多大模型”：本月论文实测口径汇总

| 设备 | 模型 / 精度 | 速度 / 能耗 | 来源 |
|---|---|---|---|
| RTX 4060 笔记本 8 GB | 35B MoE（Qwen3.6 系） | 39.3 tok/s | FreeToken |
| RTX 5090 台式机 | DeepSeek-V4-Flash 284B | 22–25 tok/s | FreeToken |
| 单张工作站 GPU | GLM-5.2 753B | 14.9 tok/s（llama.cpp 7.3） | FreeToken |
| Jetson Orin NX 16 GB | GPT-OSS-120B | 1.44–2.45 tok/s（基线 0.95） | S2-MoE |
| Jetson AGX Orin，14 GiB 预算 | Mistral-7B FP16（超出内存） | 3.22 tok/s（llama.cpp 0.34） | NeuroPrefetcher |
| Jetson AGX Thor / Orin / Xavier | 7–8B，Q4_K_M | 35–44 / 22–28 / 13–16 tok/s；Qwen2.5-7B 1493 / 1867 mJ/token（Thor / Orin） | Hydra |
| RTX 3070 8 GB + NVMe | Qwen3-235B Q4（134 GB） | 0.44 tok/s | Cacheable by Design? |
| Apple M4 Max（模拟 16–32 GB 预算） | Nemotron-H 120B，混合 2/4/8-bit + 3-bit KV | 14.85 tok/s @ 17.2 GB 峰值 | RotaryQuant |
| Pixel 8a（CPU） | Llama 3.2 11B Vision，约 2.7-bit | 3.8 tok/s，3.7 GB | Llama-Mobile |
| Galaxy S25+ / OnePlus 12（GPU） | Qwen3-0.6B / EXAONE-1.2B，8k–32k 上下文 | 被回收后 TTFT 快 2.1–5.5× | mzCache |
| Pixel 8 Pro（锁低频） | Gemma-2-2B / LLaMA-3.2-1B | 约 8.5 / 15.5 tok/s，约 0.71 / 0.41 J/token（由论文附表推算） | 提示词能耗 |

从表里看，同样是“百亿参数级”，PC 独显上能到几十 tok/s，Jetson 和纯闪存分页只有 1–3 tok/s，手机 CPU 上 11B 多模态约 4 tok/s。决定差距的主要是**可用带宽层级**（显存 / 主机 DRAM / PCIe / NVMe / UFS），其次才是算力。

### 小结

1. **MoE 外存分页在 PC 上已经实用，在手机上还不行**。FreeToken 在 8 GB 笔记本 GPU 上跑 35B MoE 达 39 tok/s；手机侧本月没有超过上月 BigMoMo / EStream 的新结果。手机要追上，靠的是更大的 LPDDR、UFS 4.x/5.0 带宽，以及路由预测。
2. **手机系统研究开始关注“真实使用条件”**。mzCache 研究被 OS 回收后的恢复，MemSpec 研究草稿模型能否常驻，提示词论文研究 token 数与每 token 能耗：端侧 LLM 的体验指标正在从峰值 tok/s 转向冷启动、恢复时间和 J/任务。
3. **FP4 格式还有改进空间**。AdaMX 用零额外位宽收回 MXFP4 八成以上的精度损失，面积和功耗只增加约 3%；下一代 NPU 的 FP4 数据通路很可能出现类似的块级自适应。
4. **存内/近存继续停留在仿真阶段，而且有反证**。IBM 的结论是 batch=1 时 PIM 只和 GPU 打平、静态功耗占 2/3，这对 LPDDR-PIM 进手机提出了实际问题；本月的存内/近存论文仍然没有流片实测。

## 7. 总结：对端侧智能体意味着什么，以及 9 月该看什么

**对端侧智能体的含义**

1. **评估端侧芯片，先看 GB/s 和 GB，再看 TOPS。** 8 月从 PIM、晶圆键合 DRAM 到 Wildcat Lake 的“减法”，都说明解码速度由带宽决定，能装下多大的模型由容量决定。NPU 峰值算力主要影响 prefill。
2. **手机端的带宽墙有了时间表。** 近期靠 LPDDR6 和权重压缩：玄戒 O3 平均约 2.6 bit，9 月旗舰普遍采用 LPDDR6。中期看 LPDDR6-PIM 标准化。远期看 3D 堆叠或晶圆键合 DRAM（O100、高通 HBC，均指向 2027 年）。
3. **内存成本是同样重要的约束。** DRAM 涨幅虽在收窄，价格没有回落，高通也已涨价。端侧模型预算短期内仍会被限制在 3–8B INT4，这让低比特量化、MoE 卸载和近存方案更有价值。
4. **运行时和软件栈会决定“30B 上手机”能否兑现。** GenieX 的 MTP 和多 HTP、MLX 的 Neural Accelerator 内核、mzCache 的内存回收恢复都说明：同样的硬件，运行时设计不同，可用性可能差一个数量级。
5. **低功耗层（MCU、眼镜）本月是空档。** 机器人和车载则在从“卖 TOPS”转向“补带宽”：S100P 有 24GB 内存，Eagle-N 用 chiplet 设计。

**留给 9 月的问题（结论已写在 9 月硬件洞察）**

- 骁龙 Gen 6 两档的最终规格：已在 9 月 22 日公布，超级至尊版使用 LPDDR6 并新增 Element Accelerator。
- A20 Pro 的 Neural Engine 和内存：已在 9 月 9 日公布，双 16 核 NE、12GB、带宽 +50%。
- 天玑 9600 Pro、麒麟 9050 Pro、Exynos 2700：均在 9 月发布或曝光，“30B MoE”成为旗舰新口径。
- 仍待验证：三星 GAIA 的量产、LPDDR6-PIM 标准、小米 O100 与高通 HBC 的商用时间。

> 口径说明：标“官方”的是厂商发布的数字，“媒体实测”和“第三方实测”是独立测试，“爆料”未经确认，“推算”或“估算”是本文按公开参数计算的结果。本月部分方向（ISLPED 2026、MCU NPU、眼镜芯片）因检索额度用尽，覆盖可能不完整，已在对应小节注明。
