# 硬件洞察：端侧 AI 芯片月报（2026-09-02 ~ 2026-10-07）

> **一句话结论：端侧 AI 硬件的竞争焦点已经从“NPU 峰值 TOPS”全面转向“内存子系统”。** 内存子系统包括带宽、容量、片上共享内存、封装散热、闪存分层，以及近存和存内计算。本月 Apple、高通、联发科三家旗舰同时进入 2nm，但没有一家公布 NPU 的 TOPS，也没有一家公布端侧 LLM 的绝对 tokens/s。它们改讲“能装下多大的 MoE”、prefill 快多少、每瓦 token 多少。与此同时，DRAM 涨价正在压缩手机能给大模型的内存预算。
>
> **阅读结构（总-分-总）**：第 0 节是全月的五个判断和旗舰对照表；第 1–7 节分厂商、分方向展开技术细节，包括低功耗/常驻 NPU、能跑多大的模型、内存带宽推算、顶会与 arXiv 论文；第 8 节回到对端侧智能体的含义和下月观察清单。每周首页的“硬件雷达”模块里，每条动态都有“能跑多大模型”和可展开的“技术细节”。

## 0. 总览：本月五个判断

**判断一：模型能多大看容量，解码能多快看带宽，TOPS 主要影响 prefill。** 解码阶段每生成一个 token，都要把激活的权重和 KV Cache 读一遍：

$$\text{decode tokens/s 上限} \approx \frac{\text{有效内存带宽}}{\text{每 token 读取字节数}}$$

本月各家的改进都落在这个公式的分子或分母上：

| 厂商 | 改进 | 作用在 |
|---|---|---|
| Apple A20 Pro | 内存仍为 12GB，位宽从 64-bit 加到 96-bit，带宽 +50% | 分子 |
| 高通 | 改用 LPDDR6（约 114–127GB/s），NPU 共享内存 +50% | 分子 |
| 小米玄戒 O3 | 权重平均约 2.6 bit，带宽占用降约 30% | 分母 |
| 联发科 | KV Cache 硬件压缩 | 分母 |

GPU 矩阵单元（Apple Neural Accelerator、Adreno 矩阵核心）主要缩短首 token 时间（TTFT）。Apple 的 MLX 实测里，M5 的 TTFT 比 M4 快 3.3–4 倍，解码只快 19–27%，正好是两者带宽的比例。

**判断二：“手机能跑 30B”是容量口径，不是速度口径。** 高通超级至尊版和联发科 9600 Pro 都宣称支持 30B MoE（约 3B 激活），华为在 Mate 90 上运行盘古 30B-A2B，Apple 的 AFM 3 Core Advanced 约 20B、每次激活 1–4B。这些模型能放进手机，靠的是专家权重放在闪存、按需载入，而不是常驻内存。各家都没给出 tokens/s，可参考的数字如下：

| 来源 | 设备 / 模型 | 速度 |
|---|---|---|
| 推算 | LPDDR6、3B 激活、INT4 | 理论上限约 76–85 tok/s |
| 第三方实测 | iPhone 17 Pro Max，27B 1-bit | 约 11 tok/s |
| 论文 | Snapdragon 手机，最大 80B 总参 MoE（BigMoMo） | 已能运行 |
| 论文 | iPhone 朴素分页，35B MoE | 只有 2–3 tok/s |

同一个模型，运行时设计不同，速度可以差 10 倍。

**判断三：低功耗端形成了一条按功耗分级的“模型梯度”。**

| 功耗档 | 设备 / 芯片 | 能跑的模型 | 速度 |
|---|---|---|---|
| 毫瓦级 MCU | 英飞凌 PSOC Edge | 6M–32M 参数语音转写，20–65mW | — |
| 常驻层 | 高通 Sensing Hub 双 Micro NPU | 最高 200M 参数 | — |
| 常驻层 | 联发科 CIM 常驻 NPU | 对焦追踪、场景识别等轻量模型 | — |
| 耳机 | 高通 eNPU | 128 GOPS，跑 ANC 和语音小模型 | — |
| 手表 | Wear Elite | 最高 2B | 约 10 tok/s |
| 眼镜 | AR1 | 2B VLM（1-bit） | 15.36 tok/s |
| 手机主 NPU | 旗舰 SoC | 3B 稠密到 30B MoE | 见判断二 |

真正 7×24 小时常开的只有前两档（百万到两亿参数），大模型都是按需唤醒。所有厂商都没有公布常驻功耗的绝对值，这是评估“常驻智能体”续航的最大信息缺口。

**判断四：存内计算从论文走向产品和标准，但要区分两种路线。**

- **DRAM-PIM 加速解码**：
  - 三星 LPDDR5X-PIM 在 Hot Chips 2026 公布：PIM 内部带宽 614GB/s，是外部的 8 倍；Llama-3.1-8B 从 27.0 提到 81.3 tok/s，端到端约 3 倍。LPDDR6-PIM 正在走 JEDEC 标准化。
  - 高通 HBC 近存堆叠计划下放到骁龙。
  - MICRO 2026 有三个 PIM/近存专场。
- **SRAM 存算（CIM）提升能效（TOPS/W）和 prefill，解决不了解码的带宽墙**：
  - 天玑 9600M 的 CIM NPU 用于常驻任务。
  - Axelera 和后摩跑大模型时，速度仍受外部 LPDDR 带宽限制。

**判断五：软件栈落后于硬件宣传。** 高通的 GenieX 目前只在 llama.cpp 路径支持 MoE 和投机解码，NPU（QAIRT）路径还不支持。本月多篇 arXiv 论文（EStream、TierKV、KV 复用等）都在处理同一个矛盾：NPU 只能执行静态图，而 MoE 路由、KV 复用是动态负载。在这些问题解决之前，“30B 上手机”更像是能力上限，而不是开发者能直接调用的能力。

### 本月旗舰 SoC 对照（已按深挖结果修订）

| 芯片 | 工艺 | AI 单元（本代真正新增的部分） | 内存 | 能跑多大模型（口径） |
|---|---|---|---|---|
| Apple A20 Pro | TSMC N2，裸片约 98.2mm² | 双 16 核 NE（两个独立实例，单模型实测约 +50%）；GPU 每核带 Neural Accelerator | 12GB（Xcode 口径），96-bit LPDDR5X，约 115GB/s（媒体推算） | AFM 3 Core Advanced 约 20B、激活 1–4B（官方）；第三方 27B 1-bit 约 11 tok/s（上代机型） |
| 骁龙 8 超级至尊版 Gen 6 | 2nm（N2P） | 新增 Element Accelerator，共享内存 +50%（INT2 上代已有）；Adreno 矩阵核心 | LPDDR6，114–127GB/s，最高 24GB | 30B MoE（约 3B 激活）、32K 上下文（官方）；tok/s 未披露 |
| 骁龙 8 至尊版 Gen 6 | 2nm | NPU +14%；矩阵核心和 LPDDR6 存在官方与媒体口径冲突 | 媒体称 LPDDR5X 84.8GB/s | 未单独披露 |
| 天玑 9600 Pro | TSMC 2nm | NPU 1090（INT4 算力为上代 2 倍）+ 第二代常驻高效 NPU；KV Cache 硬件压缩 | LPDDR6 + UFS 5.0 | 最高 30B MoE（官方）；prefill +51%，生成 +40% |
| 天玑 9600M | 3nm 级 | NPU 990 + CIM 存内计算常驻 NPU（沿用天玑 9500 首代设计，当时官方称比常规 NPU 功耗低 42%） | LPDDR5X-10667 | 4B 级（官方列出 Gemini Nano 4、Qwen 3.5 Omni 4B） |
| 麒麟 9050 Pro | 约 7nm 级 DUV（Bernstein 估计） | LogicFolding 面对面双 die；NPU 实测约 68 TOPS INT8（极客湾） | 未披露 | 盘古 30B-A2B（官方）；tok/s 未披露 |
| 玄戒 O3 | TSMC 3nm | NPU 200 TOPS；5 值量化 + Huffman 压缩，平均约 2.6 bit/权重 | LPDDR6，4×24bit，113.8GB/s | 未披露（“330 tok/s”属于 O100 加速器，不是 O3） |
| Exynos 2700（爆料） | SF2P | 2×C2-Ultra + 8×C2-Pro | LPDDR6（爆料） | 未披露 |

## 1. 高通：算力够了，喂不饱

**判断**：本月高通的端侧AI主线可以概括为“算力够了，喂不饱”。第六代骁龙8超级至尊版没有公布TOPS，而是用“30B MoE（约3B激活）+ 32K上下文 + 共享内存+50% + LPDDR6”来定义AI能力；低功耗侧，从手机Sensing Hub的200M参数Micro NPU，到耳机128 GOPS的eNPU、手表2B模型和眼镜1-bit VLM，形成了一条按功耗分级的模型梯度。更远的HBC近存计算，则是高通对内存墙给出的长期答案。

### 一、Hexagon NPU：变化集中在“喂数据”上

对照两代官方产品简介（[Gen 6 Extreme](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-8-Elite-Extreme-Gen-6-Product-Brief.pdf) / [Gen 5](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-8-Elite-Gen-5-product-brief.pdf)）可以看出，真正新增的只有两项：**Element Accelerator** 和 **共享内存+50%**。Direct Link、Micro Tile Inferencing、64位内存虚拟化和INT2至FP16混合精度，上代都已具备。

| 项目 | 8 Elite Gen 5 | 8 Elite Gen 6 | 8 Elite Extreme Gen 6 |
|---|---|---|---|
| 配置 | 12标量 + 8向量 + 1 accelerator | 12标量 + 8向量 + 1 tensor + 1 element | 同左 |
| 共享内存 | 基线 | 未标注 | +50%（绝对值未披露） |
| 精度 | INT2/4/8/16、FP8/16 | 同左 | 同左 |
| NPU性能 / AI每瓦 | +37% / +16%（对比8 Elite） | +14% / +20% | +35% / +33% |
| TOPS | 未披露 | 未披露 | 未披露 |
| 工艺 | 3nm | 2nm（N2P） | 2nm（N2P） |

Element Accelerator的官方定位是“快速动作循环与KV Cache加速”（[Computerworld](https://www.computerworld.com/article/4220719/qualcomms-next-snapdragon-mobile-chip-comes-into-focus-with-on-device-ai.html)）。INT4模型prefill最高+50%（[Digital Today](https://www.digitaltoday.co.kr/en/view/107233/snapdragon-summit-2026-smartphones-can-run-30-billion-parameter-ai-models)转述部分模型最高+80%），投机解码也有增强，但tokens/s绝对值未公布。MoE的实现方式是专家权重存放在UFS 5.0闪存中按需加载，高频专家常驻缓存（[The Elec](https://www.thelec.net/news/articleView.html?idxno=13884)）。需要注意，30B MoE和+50%共享内存只出现在超级至尊版的材料中。

### 二、CPU / GPU / 内存与封装

- **CPU**：2×5.0GHz + 6×4.0GHz Oryon，16MB Flex Cache；官方称“带硬件AI加速”，但未说明SME细节。
- **GPU**：Adreno首次加入AI矩阵核心（数量和TFLOPS未披露），驱动Neural Fusion超分和插帧；18MB HPM。媒体普遍称矩阵核心是超级至尊版独有，但[标准版官方简介](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-8-Elite-Gen-6-Product-Brief.pdf)同样写着“Adreno GPU with matrix cores”，属于口径冲突。
- **内存**：[ServeTheHome](https://www.servethehome.com/qualcomm-unveils-snapdragon-8-elite-gen-6-and-elite-extreme-gen-6-next-gen-flagship-mobile-chips/)给出LPDDR6 4×24bit@10.6Gbps = 127.2GB/s，标准版LPDDR5X为84.8GB/s；[三星](https://view.asiae.co.kr/en/article/2026092310181884005)的16GB LPDDR6（10.7Gbps）口径是114GB/s。两者的差异，按LPDDR6每个288bit burst中只有256bit是数据来推算，正好吻合（本文推算）。
- **封装**：Offset PoP把DRAM从SoC正上方移到侧面，并加导热块，官方称峰值持续时间翻倍。
- **分档的含义**：两档CPU频率和缓存完全相同，差异集中在AI相关资源上，包括NPU共享内存、内存带宽、GPU Neural Fusion，以及NPU提升幅度（+35%对比+14%）。IDC称两档价差约100美元。也就是说，高通把“端侧大模型”当作溢价点来卖，开发者需要按两档分别准备模型规格，例如超级至尊版跑30B MoE，标准版退回到更小的稠密模型或更短的上下文。

### 三、各平台能跑多大的模型

| 平台 | AI单元算力 | 内存/带宽 | 官方模型能力 | 速度 | 口径 |
|---|---|---|---|---|---|
| 8 Elite Extreme Gen 6（手机） | 未披露TOPS | 最高24GB；LPDDR6约114至127GB/s | 30B MoE（约3B激活），32K上下文，从闪存加载 | 未披露；prefill +50% | 官方 |
| 8 Elite Gen 5（上代） | 未披露 | LPDDR5x 5300MHz，24GB | 32K上下文 | 约220 tok/s（[媒体转述](https://www.sammyfans.com/2025/09/25/snapdragon-8-elite-gen-5-specs/)，模型未说明） | 官方 |
| Sensing Hub Micro NPU ×2 | +85%性能、+20%能效 | 未披露 | 最高200M参数（Personal Scribe） | 未披露 | 官方，经[HotHardware](https://hothardware.com/news/snapdragon-8-elite-extreme-gen-6-release)转述 |
| X2 Elite / Plus（PC） | 80 TOPS INT8（部分SKU 85） | 152/228GB/s，最高128GB | 最高30B、20万上下文 | 第一代的2倍 | 官方（[ITdaily](https://itdaily.com/news/workplace/qualcomm-snapdragon-x2-elite-agentic-pc/)、[The Register](https://www.theregister.com/2025/09/25/qualcomm_details_x2_elite)） |
| Reality Elite（XR） | 48 TOPS | 未披露 | 未披露（有西语媒体称3B） | 未披露 | 官方，[6月发布](https://9to5google.com/2026/06/16/snapdragon-reality-elite/) |
| AR1 Gen 1（眼镜） | 未披露TOPS | 4GB系统 | 2B VLM（1.7B 1-bit + 0.3B 4-bit） | 15.36 tok/s（4-bit基线为7.44） | 厂商实测，[AlphaSignal](https://alphasignal.ai/news/prismml-runs-bonsai-1-7b-on-smart-glasses-at-2x-the-speed) |
| AR1+ Gen 1（眼镜） | 未披露 | 未披露 | Llama 3.2 1B端侧演示 | 未披露 | 官方演示，[2025 AWE](https://9to5google.com/2025/06/10/snapdragon-ar1-gen-1/) |
| Wear Elite（手表/胸针） | NPU未披露 + eNPU | 未披露 | 最高2B | 约10 tok/s，首token约0.2s | 官方，[9to5Google](https://9to5google.com/2026/03/01/qualcomm-snapdragon-wear-elite/) |
| Sound Elite Gen 2（耳机） | eNPU 128 GOPS | 未披露 | 未披露（ANC、语音、声景等小模型） | 不适用 | 官方，[audioXpress](https://audioxpress.com/news/qualcomm-snapdragon-sound-elite-gen-integrates-ai-and-wi-fi-for-next-generation-hearables) |
| Dragonwing Q-2390（IoT） | 1.1 TOPS | 2×16bit LPDDR4x | 未披露（适合CNN视觉） | 不适用 | [CNX](https://www.cnx-software.com/2026/09/01/qualcomm-introduces-dragonwing-q-2390-and-iq-2390-for-consumer-and-industrial-aiot-applications/) |

带宽约束的推算（非官方）：30B MoE在INT4下权重约15GB；每个token读取3B激活参数，约1.5GB。按127GB/s计算，decode理论上限约85 tok/s，按114GB/s约76 tok/s，实际还要扣除KV Cache读取和专家换入的开销。由此也能看出，片上共享内存+50%和专家缓存命中率，比TOPS更能决定实际速度。

### 四、低功耗 / 常驻 AI

高通的常驻AI分为四级，各级之间是协作关系：

1. **手机Sensing Hub**：双Micro NPU（音频、语音、传感器）+ 双Always-Sensing ISP（两路常开摄像头），支持最高200M参数的模型，用于运行Personal Scribe。它持续从短信、邮件、日程和对话中抽取信息，在本地构建个人知识图谱。Gen 5已有这一结构（Micro NPU支持INT4/8/16），Gen 6性能+85%、能效+20%。功耗绝对值和GOPS未披露。
2. **耳机eNPU**：256 MAC/周期@250MHz = 128 GOPS，是S7 Gen 1的2倍；芯片还包括M55 + 2×HiFi 5 + HiFi 3。微功耗Wi-Fi 6E的待机电流为0.6mA（S7 Gen 1为1.0mA，仿真值）。负责ANC、语音检测和声学场景识别，并决定何时把请求交给云端。
3. **手表Wear Elite eNPU**：负责KWS、活动识别、降噪等常驻任务；主NPU负责2B级的生成式任务。
4. **眼镜AR1/AR1+**：依靠1-bit权重（±1，每128个共享一个FP16 scale），借助内部QNN 1-bit kernel在Hexagon上执行，把2B级VLM放进4GB系统。

“有多少是真正常开的？”从公开资料看，真正7×24小时常驻的只有第1级的Micro NPU和Always-Sensing ISP，以及耳机和手表的eNPU，模型规模在百万级到2亿参数之间。主Hexagon NPU上的30B MoE和手表上的2B模型都是按需唤醒的。高通的思路是由小模型持续采集上下文、写入知识图谱，再由大模型在被唤醒时读取。这种分层的目的是压低常驻功耗，但高通至今没有公布任何一级的常驻功耗绝对值，这是评估“常驻智能体”续航代价时最大的信息缺口。

### 五、HBC 近存计算

[The Elec](https://www.thelec.net/news/articleView.html?idxno=14133)报道：多层LPDDR经TSV堆叠在XPU计算die上，三星和SK海力士负责DRAM堆叠，台积电负责封装。高通的口径（数据中心语境）是同功耗下带宽和token效率为HBM的6倍。手机版的容量、带宽和时间表都未披露，[IDC](https://www.idc.com/resource-center/blog/snapdragon-summit-2026-qualcomms-bid-to-be-the-silicon-behind-every-agent-on-every-device/)称细节将在MWC 2027公布。

### 六、软件栈

[GenieX](https://geniex.aihub.qualcomm.com/en/get-started/what-is-geniex)（Genie的社区版，开发者预览）在窗口期内迭代到v0.8.0：QAIRT路径从v0.7.0起支持HTP多核，v0.7.1加入prefill和decode的tok/s指标。MoE模型（gemma-4-26B-A4B）和MTP投机解码目前只在llama.cpp路径可用，QAIRT路径会忽略投机解码设置，release中也没有提到LoRA。也就是说，Gen 6硬件宣传的“30B MoE + 增强投机解码”，在NPU工具链上还需要等待对应的QAIRT和Genie版本。另外，X2的官方Linux支持（Debian在2026年底，Ubuntu在2027年上半年）会把NPU开发扩展到Linux。

### 小结

高通这一代的端侧AI竞争力主要来自内存子系统：片上共享内存、LPDDR6、闪存专家流式加载，以及远期的HBC。峰值TOPS不再是主要卖点，因此高通干脆不公布。低功耗侧则形成了从200M（Sensing Hub）到2B（手表、眼镜）再到30B MoE（手机）的模型梯度。需要警惕三点：一是tokens/s、TOPS和功耗至今没有官方绝对值，也没有独立实测；二是标准版和超级至尊版在矩阵核心、LPDDR6上的口径存在冲突；三是NPU工具链对MoE和投机解码的支持落后于硬件宣传。第四季度首批机型的实测，将检验“30B MoE上手机”究竟是可用能力，还是只能用来演示。

## 2. Apple：容量不变，带宽 +50%，AI 算力分两路翻倍

本月 Apple 芯片的技术主线可以概括为：**容量不变、带宽 +50%、AI 算力分两路翻倍**。A20 Pro 和 M6 同代进入 TSMC N2，Neural Engine 都从单个 16 核改为“双 16 核”，GPU 每核都带 Neural Accelerator。手机端内存仍是 12GB，但位宽从 64-bit 加宽到 96-bit，封装改为 WMCM 并排式。这些改动的共同目标是让 1–4B 激活参数级的端侧模型解码更快、持续性能更高，而不是让手机装下更大的模型。真正决定“能跑多大模型”的，仍然是内存容量和 Apple 的闪存分层 MoE 设计。

### 一、A18 Pro → A19 Pro → A20 Pro：代际规格

| 项目 | A18 Pro（2024） | A19 Pro（2025） | A20 Pro（2026） |
|---|---|---|---|
| 工艺 | 3nm | 3nm | TSMC N2（GAA），裸片约 98.2mm²（[TechInsights](https://www.techinsights.com/blog/apple-a20-pro-tsmc-2nm-processor-analysis)） |
| CPU | 6 核 | 6 核 | 6 核（2P+4E），官方称集成 Neural Accelerators |
| GPU | 6 核 | 6 核，每核加入 Neural Accelerator | 7 核，每核带 Neural Accelerator，官方最高 +40% |
| Neural Engine | 16 核，35 TOPS（[媒体转述](https://techcrunch.com/2024/09/09/apple-announces-its-new-a18-iphone-chip/)） | 16 核，约 35 TOPS 量级 | **双 16 核（32 核）**，官方称 2 倍算力，TOPS 未披露 |
| Geekbench AI NPU（单/半/量化） | 4,575 / 32,910 / 45,348 | 5,111 / 36,772 / 50,411 | 7,002 / 55,720 / 75,810（[IT之家/凤凰网](https://tech.ifeng.com/c/8wNVMWU93D8)） |
| 内存 | — | 12GB，64-bit LPDDR5X | 12GB（[Xcode 口径](https://www.macrumors.com/2026/09/10/iphone-18-pro-max-battery-capacities-ram/)），96-bit LPDDR5X，带宽 +50% |
| 封装 / 散热 | PoP | PoP + 均热板（持续性能 +40%） | WMCM 并排封装，SoC 直贴 3 倍面积均热板，持续性能再 +40% |

几个关键点：

- **“双 16 核”是两个 NE 实例，不是一个更宽的 NE。** [M6 新闻稿](https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/)明确写到系统框架可以同时使用两个引擎。Geekbench AI 的量化分只提高约 50%，没有达到 2 倍，说明单模型未必能切到两个引擎上。2 倍更可能在 Siri、相机、输入法等多模型并发时兑现（推断）。Macworld 实测 NE 也是“快 40% 以上”（[评测](https://www.macworld.com/article/3242385/iphone-18-pro-review-the-best-boring-gets.html)）。
- **GPU Neural Accelerator 负责 prefill。** 这条路线始于 A19 Pro 和 M5。Apple 称 [M5](https://www.apple.com/newsroom/2025/10/apple-unleashes-m5-the-next-big-leap-in-ai-performance-for-apple-silicon/) 的 GPU 峰值 AI 算力是 M4 的 4 倍以上。Apple 的 [MLX 实测](https://machinelearning.apple.com/research/exploring-llms-mlx-m5)显示，M5 的 TTFT 比 M4 快 3.3–4.1 倍，但解码只快 19–27%，基本就是 153 对 120GB/s 的带宽比例。Apple 没有公开 Neural Accelerator 的 FP16/INT8 吞吐。
- **带宽推算。** 96-bit × 9600MT/s = 115.2GB/s（媒体给出的数字）。Apple 只说 +50%，没有公布绝对值。发布前 [iPhone-Mania](https://iphone-mania.jp/iphone18-603246/) 按 8533MT/s 估算为约 102GB/s。
- **CPU 的 Neural Accelerators 仍是黑盒。** Apple 只说 6 核 CPU“集成 Neural Accelerators”，没有披露它是不是类似 AMX/SME 的矩阵扩展，也没有公布精度和吞吐。实测 CPU 单核 +26%、多核 +28–30%（Macworld），主要有利于 tokenizer、调度、工具调用等串行逻辑，对 LLM 主干推理的帮助有限。
- **封装是本代最“M 系列化”的一步。** DRAM 移出 SoC 的散热路径，持续性能 +40%（[官方](https://www.apple.com/newsroom/2026/09/apple-debuts-iphone-18-pro-and-iphone-18-pro-max/)）。折叠机型 [iPhone Duo](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/) 只有 +35%，说明长时间推理受机身散热的约束很明显。

### 二、M5 → M6 / M5 Ultra：桌面端的 AI 规格

| 芯片 | 工艺 | GPU（每核带 Neural Accelerator） | NE | 内存上限 | 带宽 |
|---|---|---|---|---|---|
| M5 | 第三代 3nm | 10 核，GPU AI 峰值为 M4 的 4 倍以上 | 16 核 | 32GB | 153GB/s |
| M5 Pro / Max | 第三代 3nm，双裸片 Fusion | 20 / 40 核 | 16 核 | 64 / 128GB | 307 / 614GB/s（[官方](https://www.apple.com.cn/newsroom/2026/03/apple-debuts-m5-pro-and-m5-max-to-supercharge-the-most-demanding-pro-workflows/)） |
| **M6** | 2nm | 12 核，比 M5 高近 30% | **双 16 核** | 32GB | 170GB/s（实测 STREAM 143–145） |
| **M5 Ultra** | 未公布，四裸片 UltraFusion（>4.4TB/s） | 80 核，为 M3 Ultra 的 4.5 倍 | 32 核 | **512GB** | **1.2TB/s** |

从桌面端的数据可以看出，Apple 这两年 AI 算力的增量主要来自 GPU：从 M4 到 M5，GPU 峰值 AI 算力提高 4 倍以上，而 NE 只是“更快”；到了 M6，NE 才第一次翻倍。原因在于，Mac 上的主流本地推理工具（MLX、llama.cpp、LM Studio）几乎都跑在 GPU 上，NE 主要服务系统级的 Apple Intelligence 和 Core AI。实测也印证了这一点：M6 的 prefill 比 M4 快 3.5 倍，解码只快 1.5 倍；M5 Ultra 相比 M3 Ultra，解码快 30–40%，图像生成快 2–3 倍。对买 Mac 做本地推理的用户来说，“内存带宽决定解码速度，GPU Neural Accelerator 决定首 token 和 prefill，内存容量决定能放下多大的模型”这三条规律基本成立。

M6 和 A20 Pro 是同一代同构设计，双 NE 加 GPU 矩阵单元的组合便于同一模型在 Mac 和 iPhone 之间迁移。M5 Ultra 的 512GB 统一内存按 4-bit 估算，可以装下约 0.7–0.9T 参数的权重（扣除系统和 KV Cache 后的估算）；512GB 配置 10 月下旬才出货。Thunderbolt 5 加 RDMA 集群，官方称分布式推理最高提速 3 倍（[官方](https://www.apple.com/newsroom/2026/09/the-new-mac-mini-and-mac-studio-are-available-today/)）。

### 三、能跑多大的模型：官方模型与第三方实测

**Apple 自家模型**（[AFM 3 技术博客](https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models)）：

| 模型 | 部署位置 | 参数 | 结构 / 压缩 | 设备门槛 |
|---|---|---|---|---|
| AFM 3 Core | 端侧 | 3B 稠密 | QAT（位宽未披露） | Apple Intelligence 设备 |
| AFM 3 Core Advanced | 端侧 | 约 20B 总参，**激活 1–4B** | IFP 剪枝稀疏；按 prompt 路由；共享专家常驻 DRAM，路由专家从 NAND 按需载入；原生多模态 | iPhone 17 Pro/Air/18 Pro/Duo；≥12GB 的 M4 iPad / M3 Mac；Vision Pro（M5） |
| AFM 3 Cloud / Cloud Pro | PCC | 未披露 | Cloud Pro 针对 NVIDIA GPU 优化 | 有每日用量上限 |
| 对照：AFM 2025 端侧 | 端侧 | 约 3B | 2-bit QAT、embedding 4-bit、KV 8-bit；KV 共享使 KV 内存 -37.5%（[2025 报告](https://machinelearning.apple.com/research/apple-foundation-models-2025-updates)） | — |

Core Advanced 最有意思的设计是**按 prompt 而不是按 token 路由**。Apple 明确说明，NAND 到 DRAM 的带宽撑不住逐 token 换专家，所以由一个轻量稠密块在 prefill 阶段一次选定专家，生成过程中周期性重选。这实际上是用“闪存作为第二级权重存储”的方式，在 12GB 手机上运行 20B 模型。Apple 没有公布上下文长度和 tokens/s。

**第三方实测**（均为媒体或开发者口径）：

| 设备 | 模型 | 结果 |
|---|---|---|
| iPhone 17 Pro Max | Bonsai 27B 1-bit（3.9GB） | 约 11 tok/s（[PrismML](https://mezha.ua/en/news/prismml-bonsai-27b-iphone-313253/)） |
| iPhone 18 Pro | 同上 | 约为 17 Pro 的 2 倍，没有绝对值（[开发者自述](https://zamin.uz/en/technology/221932-27-billion-parameter-ai-launched-on-iphone-18-pro-smartphone.html)） |
| M6 Mac mini 32GB | 27B 4-bit / 9B 4-bit | 8–9.7 tok/s（用 MTP 为 16–19）；26.9 tok/s，prefill 742 tok/s（[汇总](https://www.starryhope.com/minipcs/mac-mini-m6-vs-m5-pro-local-ai/)） |
| M5 Max | Bonsai 27B 1-bit | 87 tok/s（[PrismML](https://9to5mac.com/?p=1060851)） |
| M5 Ultra 256GB | Qwen 27B 4-bit / Qwen3.5-122B-A10B | 约 55 / 约 80 tok/s，TTFT 约 0.5 秒（[BGR](https://www.bgr.com/2264114/mac-studio-m5-ultra-review/)） |

**屋顶线校验**：解码速度上限约等于带宽除以每 token 读取的权重字节数。27B 4-bit 约 13.5GB，M6 按实测 144GB/s 算上限约 10.7 tok/s，实测 8–9.7 tok/s；M5 Ultra 上限约 89 tok/s，实测 55 tok/s。在 A20 Pro 上，假设 Core Advanced 激活 4B、按 4-bit 算约 2GB，上限约 57 tok/s；按 2-bit 算约 1GB，上限约 115 tok/s（Apple 未公布 AFM 3 的位宽，属估算）。结论是：**手机端模型规模的上限由 12GB 容量决定（单模型约 6GB 预算），速度由约 115GB/s 带宽决定，NE 和 GPU 的算力主要决定 prefill 和 TTFT。**

开发路径上，iOS 27 用 [Core AI](https://developer.apple.com/core-ai/) 接替 Core ML：Swift API、AOT 编译、按硬件自动特化，在 CPU、GPU、NE 之间调度，并可以把自定义语言模型接入 Foundation Models 框架。Mac 端 MLX 从 macOS 26.2 起可以调用 GPU Neural Accelerator。

### 四、为什么容量没涨：工程取舍

把规格和模型放在一起看，可以得出 Apple 本代的设计逻辑。第一，LPDDR5X 的容量和成本在 2026 年都很紧张，12GB 已经能放下 Core Advanced 的共享专家、常驻的系统模型和 App 工作集。再往上加容量，边际收益不如加位宽：加位宽能让所有端侧模型都变快，加容量只对少数更大的模型有用。第二，Apple 选择把模型的“总参数”放在 NAND、“激活参数”放在 DRAM，这和高通、联发科依靠 16GB/24GB 大内存常驻 7B–13B 稠密模型的思路不同。代价是专家切换只能按 prompt 进行，长对话中话题漂移时需要周期性重选专家并重新载入，首 token 延迟会受闪存读取速度影响。Apple 没有公布这部分开销，开发者应该实测。第三，双 NE 和 GPU 矩阵单元这两条算力路径，分别对应“系统常驻、多模型并发、低功耗”和“开发者模型、大 batch prefill、MLX/Metal 生态”。前者由 Core AI 和系统框架自动调度，后者给第三方留出了更可控的高吞吐通道。第四，持续性能比峰值更重要。agent 会连续多轮调用模型和工具，手机必须长时间维持推理功耗，WMCM 加直贴均热板就是为这种负载准备的。iPhone Duo 只有 +35% 也提醒我们：同一颗芯片放进不同机身，可持续的端侧 AI 吞吐可能差出一个档次。

对第三方开发者来说，比较务实的选型是：在 iPhone 17 Pro 及以上（12GB）上，单模型预算按约 6GB 计算，4-bit 下大约是 7B–9B 稠密模型，或者用 1-bit/三值量化跑 20B–30B 模型；如果追求低延迟交互，优先选择激活参数在 3B 以内的 MoE 或稠密小模型，并利用 GPU Neural Accelerator 缩短 prefill。在 Mac 上，M6 的 16–32GB 适合 8B–27B 级模型，M5 Max 的 128GB 和 M5 Ultra 的 512GB 则进入百 B 到数百 B 参数的 MoE 区间，这时应优先选择激活参数小的大 MoE 模型，而不是同等显存占用的稠密模型。

### 五、低功耗与常驻 AI：表—耳—机—云分层

- **Apple Watch（S11）**：官方只说是“最强可穿戴芯片”，核数、工艺和 TOPS 都未披露。新增 **Secure Exclave**，原始音频在硬件隔离区处理后立即删除（[官方](https://www.apple.com/newsroom/2026/09/introducing-apple-watch-series-12-with-the-all-new-health-sensing-system/)）。爆料称 S11 为 2 核 CPU、4 核 NE（LLC +50%）、RAM 从 2GB 增至 4GB（[科技新报](https://technews.tw/?p=1615944)）。对照：S9（2023）首次配 4 核 NE，Siri 可以在本地处理（[TechCrunch](https://techcrunch.com/2023/09/12/the-apple-watch-series-9-features-a-new-chip-the-s9)）。
- **分工**：Sound Recognition 在表上运行，不需要 iPhone；Live Rewind 和 Siri Recap 需要 iPhone 16+ 上的模型以及 PCC（[Siri AI 新闻稿](https://www.apple.com/newsroom/2026/09/siri-ai-a-profoundly-more-capable-and-personal-assistant-is-here/)）。
- **AirPods 5**：H 系列芯片型号未披露。耳机端只做 ANC（降噪量 +50%）和头部手势识别；Live Translation 在 iPhone 上完成（[Apple 2025](https://www.apple.com/ie/newsroom/2025/11/live-translation-on-airpods-expands-to-the-eu/)）。
- **为什么这样分层**：手表和耳机受电池与散热限制，只负责常开感知，比如声学事件检测、心率采样、头部手势识别。它们需要的是极低的待机功耗和隐私隔离，而不是大模型算力。Secure Exclave 的意义在于，把“常开麦克风”这一隐私风险最高的环节放进硬件隔离区，输出给上层的只有文本或事件。真正的语言理解和生成交给 iPhone 上的 AFM，再由 PCC 兜底复杂请求。这种分层也决定了：手表上的 Siri AI 体验，很大程度上取决于配对 iPhone 的芯片代际和网络状况。
- **C2 / N1**：C2 能耗比 C1X 低 15%，新增 mmWave；N1 没有公布功耗。TechInsights 拆解发现 iPhone 18 Pro Max 仍用高通 X80（[拆解](https://www.techinsights.com/blog/iphone-18-pro-max-unboxing)）。基带功耗降低，直接降低端云 agent 常驻联网的能耗底噪。

### 小结

Apple 这一代没有追 TOPS 数字，而是在“带宽、封装散热、双 NE 并发、GPU 矩阵单元”四个方面同时改进，再用闪存分层的 20B 稀疏模型绕开了 12GB 的容量墙。工程上值得关注的有三点：其一，双 NE 的 2 倍要在多模型并发中兑现，单模型约 1.5 倍；其二，解码速度基本贴着带宽屋顶线，投机解码（MTP）是下一步的主要软件手段；其三，可穿戴设备坚持“隔离感知前端 + 手机推理 + PCC 兜底”的三层架构，手表内存翻倍、NE 缓存加大，都是在为常开音频智能铺路。

## 3. 联发科、Arm、三星、谷歌、华为、小米与 PC

本期非高通、非苹果阵营的端侧AI芯片出现明显分化。手机厂商的宣传重点已从“NPU多少TOPS”转向能跑多大的MoE模型、prefill和decode各快多少、KV与权重怎么压缩；PC阵营则直接比统一内存容量（128GB对192GB）和带宽（约300GB/s）。但几乎所有厂商都没有公布绝对tokens/s，“30B”“300B”这类数字应理解为容量上限，不是可用速度。

### 一、联发科：双NPU + KV压缩，30B MoE成为旗舰新口径

[天玑9600 Pro](https://www.mediatek.com/press-room/mediatek-dimensity-9600-pro-sets-new-standard-for-flagship-smartphone-chips)（台积电2nm，Arm C2核）把AI拆成两颗NPU：

- **NPU 1090**：INT4算力为[天玑9500 NPU 990](https://www.nasdaq.com/press-release/mediatek-dimensity-9500-unleashes-best-class-performance-ai-experiences-and-power)的2倍（NPU 990峰值约100 TOPS，为[Counterpoint](https://counterpointresearch.com/cn/insights/mediatek-dimensity-9500-powering-powering-next-gen-smartphones)口径）。官方数据为LLM prefill+51%、token生成+40%、每瓦token+55%。[heise](https://www.heise.de/en/news/Mediatek-Dimensity-9600-Pro-2nm-processor-with-All-Big-Core-CPU-and-two-NPUs-11452796.html)指出，+40%是“调度引擎3.0 + AI Compute Fusion”的系统级结果，并非NPU单独贡献。
- **KV-cache硬件压缩引擎**（[gsmarena](https://www.gsmarena.com/the_dimensity_9600_pro_is_a_2nm_chip_with_arm_c2_cores_and_malig2_ultra_nx_gpu-news-74619.php)）：用来降低长上下文时KV占用的容量和decode带宽，压缩比和是否有损均**未披露**。
- **Super Efficient NPU 2.0**：常驻AI功耗-40%。第一代（天玑9500）采用**存内计算（CIM）**，面向对焦追踪等持续运行的轻量模型，官方称比常规NPU省电42%（[MediaTek](https://www.mediatek.com/dimensity-9500)）。2.0代是否仍为CIM**未披露**。

[天玑9600M](https://www.mediatek.com/products/smartphones/dimensity-9600m)沿用NPU 990加CIM超低功耗NPU，官方点名支持Gemini Nano 4和Qwen 3.5 Omni 4B。由此，vivo X500和OPPO Find X10系列的端侧模型大致分成两档：Pro版约30B MoE，标准版约4B。

| 项目 | 天玑9500（2025） | 天玑9600M | 天玑9600 Pro |
|---|---|---|---|
| 工艺 | 3nm | 3nm级 | 2nm |
| 大NPU | NPU 990（约100 TOPS，Counterpoint） | NPU 990 | NPU 1090（INT4算力×2，TOPS未披露） |
| 常驻NPU | 第一代CIM，比常规NPU省电42% | CIM NPU | SE-NPU 2.0，常驻功耗-40% |
| 模型口径 | 3B LLM，128K上下文，BitNet 1.58-bit | Gemini Nano 4 / Qwen3.5 Omni 4B | 最高30B（含MoE） |
| 关键新特性 | 端侧LoRA训练 | — | 硬件KV压缩、MoE |
| 内存 | LPDDR5X | LPDDR5X-10667 | LPDDR6（同频有效带宽+33%）/ LPDDR5X |

### 二、Arm CSS for Mobile 2：CPU里放两个SME2，GPU里加INT8矩阵单元

[C2集群](https://newsroom.arm.com/blog/arm-css-for-mobile-2-and-c2-cpu-cluster)每簇两个SME2单元（较上一代配置翻倍）。SME2位于核外，由各核共享，相当于集群级矩阵协处理器。官方称最新SLM提速70%，C2-Ultra的AI性能为C1-Ultra的1.7倍。每单元每周期MAC数、SVL位宽均**未披露**（Lumex代首批为512-bit SVL，见[xpu.pub](https://xpu.pub/2025/09/09/arm-lumex/)）。[Chips and Cheese](https://chipsandcheese.com/p/arms-c2-ultra-g2-ultra-nx-and-css)的分析可以给宣传降降温：C2-Ultra峰值IPC仅+7%，扣除频率后平均IPC约+3.2%。

G2-Ultra NX的**NX单元**每个着色器核最高1024 INT8 MAC/clk（或512 INT16），可运行在执行引擎2倍频率，**不支持FP8/BF16**，单核面积因此增加约21%。它主要服务神经图形（NSS超分、NFRU插帧），不适合承担LLM主力推理。Arm本身不给模型规模口径，CPU路径的价值在于不依赖各家私有NPU SDK，通过KleidiAI自动启用SME2，并借[AI Portal](https://newsroom.arm.com/news/arm-unveils-arm-ai-portal)分发模型（Qwen3-TTS在vivo X300上单线程提速超过4倍）。

从系统分工看，C2平台形成了三层AI算力：SME2负责低延迟、小批量的矩阵运算（如SLM的首token、ASR和TTS），GPU的NX单元负责INT8神经图形，SoC厂商自研的NPU负责大模型的prefill和decode。值得注意的是，天玑9600 Pro与玄戒O3都同时用上了这三层，而Exynos 2700据爆料采用2×C2-Ultra + 8×C2-Pro全大核布局，说明2027年Android旗舰的CPU侧AI基线会统一到“双SME2”。对开发者来说，SME2经KleidiAI接入llama.cpp、ExecuTorch和LiteRT后无需改代码即可受益，是跨芯片最省事的加速路径；但它的绝对算力远不如NPU，更适合作为调度兜底和低延迟通路。

### 三、华为与小米：芯片和自家模型一起设计

**麒麟9050 Pro / LogicFolding**：根据极客湾拆解（[KOCPC转述](https://en.kocpc.com.tw/archives/25948)），两颗die面对面混合键合。上层主die放CPU执行单元和NPU，下层副die放L1/L2缓存、I/O和PLL；die间有500万信号键合点，带宽125TB/s（[官方](https://www.prnewswire.com/news-releases/huawei-launches-the-huawei-mate-90-series-equipped-with-the-flagship-tau-chipset-across-the-entire-series-302895853.html)），关键路径时延-30%。238 MTr/mm²是两层叠加后的投影密度，不能与单层工艺密度直接比较。NPU为达芬奇架构，极客湾测得INT8约68 TOPS（媒体实测）；论文口径为等性能下NPU功耗-66%。Mate 90 Pro Max端侧运行**盘古30B-A2B**（激活2B），tokens/s、量化方式、上下文长度均**未披露**，唯一的速度数据是“3B模型prefill为上代3倍”。

**玄戒O3**：Tensor算力200 TOPS（精度口径不一），Vector算力3.13 TFLOPS；与MiMo团队联合做了**5值量化+霍夫曼压缩**，平均权重位宽约2.6 bit，内存带宽占用降低约30%。MiMo-3B上Prefill+40%、Decode+45%、功耗-26%（[智源社区转述官方](https://hub.baai.ac.cn/view/57441)）。LPDDR6为4×24-bit，113.8GB/s。广为流传的“330 tokens/s”属于**玄戒O100**，不是O3。

### 四、三星与谷歌：只给相对数字

- **Exynos 2600**（[官方](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2600)）：NPU与2500同为32K MAC，生成式AI性能+113%，增益来自架构而不是MAC数量。
- **Exynos 2700（爆料）**：SF2P工艺，2×C2-Ultra + 8×C2-Pro，24MB SLC，NPU面积很大但未量化，据报有4个LPDDR6 PHY（[SamMobile](https://sammobile.com/news/galaxy-s27-exynos-2700-chip-design-leaks)、[helentech](https://helentech.jp/news-exynos-2700-die-shot-leak-90856/)）。
- **Tensor G6**（8月12日，背景）：TPU算力+50%，端侧任务最高快3.5倍、省能3.5倍（[Google](https://blog.google/products-and-platforms/devices/pixel/google-pixel-11-pro-xl/)）；Gemini Nano的版本、参数量和上下文长度均**未披露**。

### 五、PC：容量决定能装多大，带宽决定跑多快

| 平台 | AI算力口径 | 统一内存 / 带宽 | 功耗 |
|---|---|---|---|
| NVIDIA N1X（RTX Spark） | 1 PFLOPS FP4（稀疏，理论值） | 最高128GB，256-bit LPDDR5X-9400，约300.8GB/s | 笔记本45-80W，台式140W |
| AMD Ryzen AI Max+ PRO 495 | XDNA 2 NPU 55 TOPS（大模型主要跑在GPU） | 最高192GB（160GB可作显存），LPDDR5X-8533，约273GB/s | 45-120W |
| Intel Panther Lake | NPU 5约50 TOPS，平台合计180 TOPS | LPDDR5(X)最高9.6GT/s | — |
| Copilot+门槛 | NPU 40+ TOPS | 16GB / 256GB | — |

Panther Lake的NPU 5把NCE从6个减为3个、每个MAC阵列翻倍，并新增FP8（BF8/HF8），TOPS/mm²提升约40%（[tbreak](https://tbreak.com/intel-panther-lake-ai-pc-architecture/)、[Igor's Lab](https://www.igorslab.de/en/panther-lake-and-the-integration-of-ki-graphics-and-image-processing-an-overview-of-intels-new-architectural-strategy/)）。不过50 TOPS只满足[Copilot+门槛](https://support.microsoft.com/help/5039678)，本地大模型的竞争已经不在NPU上。N1X与Strix Halo系的带宽同属约300GB/s一档，decode速度上限相近，差别主要在容量和软件栈：N1X有CUDA与MXC，AMD有192GB和x86兼容。

两家的软件生态差异同样关键。微软在Surface Laptop Ultra上演示的MAI Code 1.1 Flash（137B，3-bit量化，建议128GB内存）是“本地编码Agent”的样板：prefill在64K上下文下为923.5 tok/s，决定读入大型代码库所需的时间；decode约60 tok/s，决定生成代码的速度。AMD给出的128K上下文下36 tok/s输出、446 tok/s输入虽然没写模型名，但同样把长上下文作为主测场景，可见两家都把“读完整个代码库后再行动”的Agent当作本地大模型的主要负载。需要提醒的是，N1X的1 PFLOPS是稀疏FP4理论值，对prefill有帮助，对受带宽限制的decode几乎没有帮助。

### 六、模型容量对照表

| 芯片 | 宣称最大模型 | 精度 | 上下文 | 激活参数 | tokens/s（口径） | 来源 |
|---|---|---|---|---|---|---|
| 天玑9600 Pro | 30B（含MoE） | INT4（FP8未披露） | 未披露 | 未披露 | 未披露；相对值：生成+40%、prefill+51% | [官方](https://www.mediatek.com/press-room/mediatek-dimensity-9600-pro-sets-new-standard-for-flagship-smartphone-chips) |
| 天玑9600M | Gemini Nano 4 / Qwen3.5 Omni 4B | 未披露 | 未披露（9500口径为3B@128K） | — | 未披露 | [官方](https://www.mediatek.com/products/smartphones/dimensity-9600m) |
| 麒麟9050 Pro | 盘古30B-A2B（全模态MoE） | 未披露 | 未披露 | 2B | 未披露；3B模型prefill为上代3倍 | [官方](https://www.prnewswire.com/news-releases/huawei-launches-the-huawei-mate-90-series-equipped-with-the-flagship-tau-chipset-across-the-entire-series-302895853.html) / [拆解](https://en.kocpc.com.tw/archives/25948) |
| 玄戒O3 | 未披露（测试模型MiMo-3B） | 5值量化，约2.6 bit | 未披露 | — | 未披露；Prefill+40%、Decode+45% | [官方转述](https://hub.baai.ac.cn/view/57441) |
| Arm C2（CPU） | 未披露（定位SLM） | INT8/BF16等 | — | — | 未披露；SLM+70% | [Arm](https://newsroom.arm.com/news/arm-css-for-mobile-2-agentic-ai-mobile-graphics) |
| Tensor G6 | Gemini Nano（版本未披露） | 未披露 | 未披露 | — | 未披露；任务快3.5倍 | [Google](https://blog.google/products-and-platforms/devices/pixel/google-pixel-11-pro-xl/) |
| Exynos 2600/2700 | 未披露 | 未披露 | 未披露 | — | 未披露 | [Samsung](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2600) |
| N1X 128GB | 120B@1M上下文（NVIDIA）；137B / 284B（微软）；200B（Dell） | FP4，2-3 bit | 最高1M | — | MAI Code 1.1 Flash（137B）decode约63→39 tok/s（2K→256K，含投机解码，图表估读）；prefill 923.5 tok/s@64K | [StorageReview](https://www.storagereview.com/news/nvidia-rtx-spark-pre-orders-n1x-laptop-desktop-tdp-mxc-dgx-station-for-windows) |
| Ryzen AI Max PRO 400（192GB） | 300B+ | 4-bit | — | — | 未写模型名：输出36 tok/s、输入446 tok/s@128K | [AMD](https://www.amd.com/en/blogs/2026/how-amd-ryzen-ai-max-pro-400-series-processors-bring-local-agentic-ai-to-business-customers.html) |
| Ryzen AI Max+ 300（128GB） | 200B | 4-bit | — | — | 未披露 | [AMD](https://newsroom.amd.com/press-kits/press-kit-agentic-pcs) |
| Panther Lake | 未披露 | FP8/INT8 | — | — | 未披露 | [tbreak](https://tbreak.com/intel-panther-lake-ai-pc-architecture/) |

参考：同为GB10架构的DGX Spark上，llama.cpp实测gpt-oss-120b生成58.7 tok/s（[llama.cpp](https://github.com/ggml-org/llama.cpp/discussions/16578)），可视为N1X decode速度的大致上限。

### 七、工程视角：怎么读这些“能跑多大”的口径

**第一，容量上限不等于可用速度。** LLM decode每生成一个token，都要把全部激活权重从DRAM读一遍，所以速度上限约等于“内存带宽 ÷ 每token读取字节数”。以AMD的300B为例：如果是稠密模型，4-bit下每个token要读约150GB，在约273GB/s的带宽下，每秒连两个token都生成不了（本文推算）。因此300B在工程上只对MoE有意义，例如激活参数在数十亿到两百亿级的模型。手机同理：盘古30B-A2B每步只读2B激活参数，INT4下约1GB，在约100GB/s级的LPDDR带宽上理论可达数十tok/s；但30B总权重仍要放得下，INT4下约15GB，对16GB内存的手机非常紧张（均为本文推算，不是厂商口径）。

**第二，压缩发生在三个层面。** 权重压缩：小米5值量化把平均位宽压到约2.6 bit，直接减少decode每步读取的字节数。KV压缩：联发科做成了硬件引擎，长上下文Agent的KV cache随上下文线性增长，到数万token时常常比激活权重还大。投机解码：微软在N1X上测MAI Code 1.1 Flash时用了DFlash2投机解码，所以约63 tok/s不是“裸”decode速度，跨平台比较时必须注意。

**第三，常驻NPU是Agent的“感官”，不是“大脑”。** 联发科的CIM NPU和华为、小米的低功耗通路，目标都是在mW级功耗下持续运行唤醒、场景识别、对焦追踪等小模型，再在需要时唤醒大NPU。厂商普遍不公布常驻NPU的绝对功耗和TOPS，只给“-40%”“-42%”这类相对值，而且基准各不相同，目前无法横向比较。

**第四，各家仍不公布TOPS和tokens/s，这本身就说明了问题。** 联发科、谷歌、华为都不给1090/TPU/达芬奇的TOPS；本期涉及的厂商也都没有公布端侧LLM的绝对tokens/s。原因之一是不同精度（INT4/FP8/A8W4）、稀疏与否、是否含投机解码，都会让数字相差数倍。下季度第三方用统一模型（如Qwen3.5 4B或gpt-oss系列）实测，比继续看发布会口径更有价值。

### 小结

手机侧，“30B MoE”已成为旗舰的新口径（联发科、华为），能做到这一点靠的是**低激活比例 + 权重/KV压缩 + LPDDR6**，而不是单纯堆TOPS。小米压权重，联发科压KV，华为用3D堆叠扩大NPU面积。三家都没有公布绝对tokens/s，第三方实测会是下一阶段最关键的验证数据。PC侧，N1X与Ryzen AI Max的带宽同在约300GB/s一档，竞争点变成容量（128GB对192GB）和软件栈（CUDA/MXC对x86/ROCm）；NPU TOPS只剩满足Copilot+门槛的作用。

## 4. 低功耗、存内计算与内存：每个 token 要搬多少字节

本月低功耗AI硬件的主线很清楚：**端侧大模型的瓶颈已经从TOPS转移到“每生成一个token要搬多少字节”**。三星在Hot Chips公开LPDDR5X-PIM（内部带宽为外部的8倍，8B模型吞吐约3倍），SK海力士把AiM定位为“快速Decode”层，高通宣布把HBC近存堆叠带进骁龙，LPDDR6随小米18 Fold、骁龙8 Elite Extreme Gen 6开始商用，这几件事说的都是带宽。另一端，几十mW的MCU已经能跑数千万参数的离线语音转写，2–10W的独立加速器能跑7B–30B模型，但DRAM涨价正在压缩终端内存容量。

### 一、为什么Decode是带宽问题：一组可复算的上限

自回归解码每生成1个token，要把全部（MoE则是激活部分）权重和当前上下文的KV Cache各读一遍，计算强度只有约1–2 FLOP/Byte，因此**tokens/s上限 ≈ 有效内存带宽 ÷ 每token读取字节数**。以Llama-3.1-8B为例：INT4权重约4GB；KV Cache每token为2×32层×8个KV头×128维×2字节≈128KB，4K上下文约0.5GB，合计每token约4.5GB。30B-A3B类MoE（激活约3.3B）INT4权重约1.65GB，加4K上下文KV约0.4GB，合计约2GB（以下均为推算，实际利用率通常为理论值的60–80%）。

| 内存配置 | 有效带宽 | 8B INT4上限 | 30B-A3B INT4上限 | 来源/算法 |
|---|---|---|---|---|
| LPDDR5X-8533，64bit | 68.3 GB/s | ~15 t/s | ~33 t/s | 8.533×64÷8 |
| LPDDR5X-10667，64bit | 85.3 GB/s | ~19 t/s | ~42 t/s | 10.667×64÷8 |
| LPDDR5X-10667，96bit（“6通道”） | ~128 GB/s（原始） | ~28 t/s | ~62 t/s | [美光已出货6通道1γ LPDDR5X](https://www.sec.gov/Archives/edgar/data/0000723125/000072312526000018/a2026q4ex991-pressrelease.htm)，按16bit/通道推算 |
| LPDDR6-10667，96bit | 113.8 GB/s | ~25 t/s | ~55 t/s | [三星114GB/s](https://view.asiae.co.kr/en/article/2026092310181884005)、玄戒O3 113.8GB/s |
| LPDDR6-14400，96bit | 153.6 GB/s | ~34 t/s | ~75 t/s | JEDEC上限 |
| LPDDR5X-9600-PIM（单封装内部） | 614 GB/s | 仅GEMV部分加速 | — | [Chips and Cheese](https://chipsandcheese.com/hot-chips-2026-samsungs-processing) |
| Jetson Thor，256bit LPDDR5X | 273 GB/s | ~60 t/s | 70B INT4约7 t/s | 第三方规格页 |

两点需要说明。其一，LPDDR6每通道24bit（2个12bit子通道），BL24时每子通道一次突发288bit，其中256bit是数据，32bit是元数据/链路ECC/DBI，**有效载荷约88.9%**（[Power Systems Design](https://www.powersystemsdesign.com/articles/lpddr6-bandwidth-math-what-you-gain-what-you-pay-what-you-measure/22/23664)）；10.667Gbps×96bit×256/288÷8≈113.8GB/s，与三星、玄戒O3公布的数字吻合。所以“LPDDR6同频比LPDDR5X高33%”是拿96bit和64bit系统比较，同位宽同频下LPDDR6反而略低，真正的增益来自14.4Gbps的频率上限和子通道并行。其二，**容量决定能不能装下，带宽决定能跑多快**：16GB手机扣除系统后常驻8B INT4已经偏紧；30B总参数的MoE需要把冷门专家放在闪存。UFS 5.0（JESD220H，2月发布）基于M-PHY 6.0 HS-G6，两lane顺序读写最高10.8GB/s（[EE Asia](https://www.eetasia.com/jedec-releases-updates-to-ufs-and-memory-interface-standards/)）。若每token需从闪存补读0.5GB专家权重，仅闪存一项就把上限压到约20 t/s，随机读时更低（推算），因此专家缓存命中率比峰值带宽更重要。

### 二、LPDDR6：功耗、可靠性与渗透节奏

- **功耗**：DVFS分DVFSH/DVFSL等档位，动态能效模式在低带宽时只开一个子通道。三星称能效比LPDDR5X最高+21%，SK海力士称功耗-20%以上，长鑫称-20%（均为厂商口径）。
- **PRAC**：每行带激活计数位，主机和DRAM同时跟踪，超阈值时DRAM拉ALERT，主机插入RFM缓解行锤（[Cadence](https://community.cadence.com/cadence_blogs_8/b/fv/posts/lpddr6-next-generation-lpddr-device-standard-and-how-it-differs-from-lpddr5)）。这对长时间满带宽解码的LLM负载是可靠性底线，代价是少量带宽损失（缓解窗口）。
- **路线**：JEDEC 4月预告下一版将增加x12/x6子通道模式、容量到512GB，并制定LPDDR6 SOCAMM2，LPDDR6-PIM“接近完成”（[TrendForce](https://www.trendforce.com/news/2026/04/24/news-jedec-previews-lpddr6-enhancements-develops-socamm2-standard-for-ai-memory/)）。服务器侧，美光SOCAMM2已送样192GB/9.6Gbps，SOCAMM营收环比翻倍；PC侧，LPCAMM2让可插拔LPDDR5X进入笔记本。
- **渗透**：Omdia预测LPDDR6在LPDDR出货中的占比2027年仅3%、2028年9%、2030年39%；美光的1γ LPDDR6先送样物理AI客户，手机端用6通道LPDDR5X过渡；另有传闻称Galaxy S27 Ultra可能因成本放弃LPDDR6（未证实）。

### 三、PIM/CIM：谁把算力放在哪里

| 方案 | 计算位置 | 加速阶段 | 关键数字（口径） | 模型规模 |
|---|---|---|---|---|
| [三星LPDDR5X-PIM](https://chipsandcheese.com/hot-chips-2026-samsungs-processing) | DRAM每bank一个MAC块 | Decode GEMV | 内部614 vs 外部76.8GB/s；~2.4 INT8 TOPS/封装 | Llama 3.1 8B：吞吐27→81.3（官方） |
| 三星HBM-PIM（2021） | HBM底部4层die，每bank（对）一个FP16 PCU | GEMV | 300MHz，32 PCU/die；能耗-70%（官方） | HPC/推理 |
| [SK海力士GDDR6-AiM/AiMX](https://news.skhynix.com/en/ai-infra-summit-2026/) | 每bank一个PU，1GHz | Decode | 1 TFLOPS/8Gb die（ISSCC'22）；AiMX 32GB | OPT-13B、Llama 3 70B演示 |
| d-Matrix Raptor | 4nm逻辑die面对面键合定制DRAM | Decode（Prefill交给Vera Rubin） | >100TB/s/卡，0.37pJ/bit vs HBM4 2–3pJ/bit；32GB/卡 | 数据中心，2027Q4 |
| 高通HBC | LPDDR经TSV堆叠在XPU上 | Decode | 同功耗带宽为HBM的6倍（厂商口径） | 移动端参数未披露 |
| [Axelera Europa](https://convergedigest.com/axelera-launches-europa-aipu-with-629-tops/) | 数字SRAM存内计算（D-IMC） | 视觉全流程；LLM受LPDDR5限制 | 629 TOPS INT8，45W TDP，200GB/s | Qwen3-32B 11 t/s（厂商） |
| [后摩M50](https://finance.eastmoney.com/a/202607193811732690.html) | 数字SRAM存算（bit-serial） | Prefill+Decode | 160 TOPS@10W，153.6GB/s，≤48GB | 7/8B 25+ t/s；P7整机称122B 50 t/s |
| EnCharge EN100 | 模拟电容存内计算 | Prefill为主 | 200+ TOPS@8.25W（M.2），16nm | M.2卡32GB/68GB/s（eeJournal口径） |
| 知存WTM2101 | 模拟NOR Flash存算 | KWS/降噪 | ~50 Gops，μA–mA级 | 2–3个语音小模型并行 |

这张表要读出三层意思。**第一，“存内计算”分两类**：DRAM-PIM（三星、SK海力士）把MAC放进DRAM bank，用的是bank级并行带来的内部带宽，只适合GEMV，正好对应Decode；SRAM-CIM（Axelera、后摩、EnCharge、知存）提升的是片上MAC能效（TOPS/W），但LLM权重放不进片上SRAM，**解码速度仍由外部LPDDR带宽决定**。Europa的128MB SRAM、200GB/s跑Qwen3-32B只有11 t/s，后摩M50的25+ t/s与153.6GB/s推算的8B INT4上限（约34 t/s）一致，都说明了这一点。**第二，PIM的收益受Amdahl定律限制**：内部带宽8倍，端到端只有约3倍，因为注意力、softmax、采样和模式切换仍在主机上；GEMV化的设计对投机解码、MoE随机专家访问也不友好。**第三，“千亿模型塞进口袋”靠的是MoE加大容量**：联想P7的50 t/s在约150GB/s级带宽下意味着每token只读约3GB，1220亿参数只能是激活参数约5B的MoE（推算），存算一体在这里主要贡献了Prefill的能效。

### 四、功耗档位 vs 能跑的模型

| 功耗档 | 代表芯片（口径） | 典型可跑模型 | 关键约束 |
|---|---|---|---|
| μW–1mW（常开） | Syntiant NDP250 30 GOPS；Ambiq Apollo510（M55，较M4级能效30倍）；知存WTM2101；BrainBoard 1500关机37μW | 唤醒词、VAD、声学事件、传感器异常检测（10K–1M参数） | 片上SRAM/Flash百KB–MB；NDP250官方未列Transformer |
| 10–300mW（MCU/耳机/手表） | [PSOC Edge E84](https://www.elektormagazine.com/articles/elektor-at-embedded-world-north-america-day-update)（Ethos-U55约102 GOPS推算，20–65mW）；STM32N6 600 GOPS、4.2MB SRAM；AKD1500 800 GOPS/<300mW；骁龙畅听Elite Gen 2 eNPU 128 GOPS；Ethos-U85最高4 TOPS（2048 MAC@1GHz） | 6M–32M参数离线ASR；YOLO级视觉；TinyLlama 15M（U85 512 MAC FPGA演示）；A320+U85官方称可跑>1B | 片上SRAM 1–5MB，权重需外部Flash XIP |
| 0.3–1W（眼镜） | 骁龙AR1 Gen 1（Ray-Ban Display：2GB RAM，960mWh电池） | 2B 1-bit VLM（约0.25GB权重，推算）；亿级INT4模型 | 电池与热；大模型对话走手机/云 |
| 2–5W（M.2加速卡） | [Hailo-10H](https://hailo.ai/products/ai-accelerators/hailo-10h-ai-accelerator/) 40 TOPS INT4/2.5W；Ambarella X7 2–5W | 1–2B LLM/VLM；Llama2-7B约10 t/s（Hailo早期官方） | LPDDR4X/LPDDR5带宽；主机链路仅PCIe Gen3 x1 |
| ~10W（AI PC/边缘盒） | 后摩M50 160 TOPS/10W；EnCharge EN100 200+ TOPS/8.25W | 7–8B 25+ t/s；35B约30 t/s（整机）；MoE百亿级 | 48GB/153.6GB/s级内存 |
| 30–50W（边缘服务器） | Axelera Europa 45W；联想P7整机30W；Ambarella N1 <50W | Qwen3-32B 11 t/s；Llama2-13B 25 t/s（N1）；122B MoE（P7） | 200GB/s级LPDDR5 |
| 40–130W（机器人/车） | Jetson Thor 2070 FP4 TFLOPS、128GB、273GB/s；征程6P/旭日S600 560 TOPS、~205GB/s；爱芯M97 720 TOPS、等效460GB/s | VLA：GR00T N1.7 NVFP4 125→39.9ms、25Hz（NVIDIA教程）；S600跑Pi0、Qwen3-VL-8B，约10FPS | 控制频率≥10Hz；动作头算力+VLM带宽 |

### 五、超低功耗层：MCU NPU 的真实边界

MCU级NPU的上限首先取决于片上存储，而不是算力。英飞凌PSOC Edge E84的Cortex-M55子系统有5MB SRAM，另有M33子系统1MB SRAM和512KB超低功耗RRAM；Ethos-U55为128 MAC、400MHz，按每MAC 2次运算推算峰值约102 GOPS。本月演示的DEEPCRAFT语音转文字模型为6M到32M参数，最小配置约4.4MB ROM、不到3MB RAM，有效功耗20–65mW。6M参数INT8约6MB，32M参数约32MB，因此大模型档必须依赖外部Flash/PSRAM以XIP方式取权重，这时外部总线带宽又成为新的瓶颈（推算）。常开部分由M33+NNLite承担VAD和唤醒，命中后才拉起M55+U55，所以电池设备的平均功耗远低于上述有效功耗。

Arm Ethos-U85把MAC规模扩到128–2048个（1GHz时最高4 TOPS），并原生支持MATMUL等Transformer算子，不再需要回退到CPU；但Arm公开的演示只是512 MAC FPGA在32MHz下跑15M参数的TinyLlama2，配320KB SRAM。Arm高管自己也说，4 TOPS的U85跑TinyLlama能达到“阅读速度”，真正的问题是内存。ST的STM32N6（Neural-ART 600 GOPS、4.2MB SRAM）、BrainChip AKD1500（800 GOPS、1MB片上存储、<300mW）、高通畅听Elite Gen 2（eNPU 128 GOPS，Wi-Fi空闲电流目标从1.0mA降到0.6mA）的算力都在0.1–1 TOPS之间，能稳定跑的是关键词、降噪、声学事件、YOLO级视觉和千万参数级ASR，**十亿参数级LLM在这一档仍是演示，不是产品**。这一档也在被整合：Microchip完成收购Hailo，BrainChip以99–149美元的开发卡打市场，英飞凌、ST把NPU直接做进MCU。可以预期，未来两年的格局会是“MCU内NPU负责常开，2–5W加速卡负责生成式”的两级结构。

### 六、内存涨价如何改写RAM配置

TrendForce称2Q26 LPDDR5X均价环比上涨78–83%，4Q26常规DRAM合约价仍会再涨10–15%，NAND涨15–20%；高端机以12GB为主流，16GB减少，中端机回到8GB。按扣除系统和常驻应用后的可用空间估算：8GB机型约剩2–3GB，只能常驻3–4B INT4模型；12GB机型可以放7–8B INT4，但KV Cache空间紧张；16GB才能较从容地跑8B加长上下文（推算）。这意味着2027年的端侧模型规划不能默认“内存随代际翻倍”，厂商会更依赖低比特量化、MoE专家闪存卸载和投机解码。安霸也在财报中把内存成本上涨列为风险因素，说明这一压力已经传导到边缘AI芯片公司。

### 七、可穿戴与机器人：两个极端的同一个问题

眼镜侧，Ray-Ban Display拆解显示为AR1 Gen 1+2GB RAM+32GB存储，电池仅960mWh（[Android Authority](https://www.androidauthority.com/meta-ray-ban-display-teardown-ifixit-3605921)），平均功耗只能在几百mW。高通与PrismML演示的2B 1-bit VLM，“速度为4-bit的2倍以上、内存为1/4”，本质也是用更少的字节换带宽。Meta新的VR Glasses则把骁龙Reality Elite、12GB内存、电池全部放进300克计算盒，换取手机级功耗预算；千问N1、Ray-Ban Meta Gen 3都没有公开芯片。机器人侧，旭日S600与征程6P同为4核BPU Nash+256bit LPDDR5(X)约205GB/s，S600的560 TOPS是1/2稀疏下的有效值；VLA的视觉语言骨干（7–8B）受带宽约束，动作扩散头受算力约束，因此Thor以2070 FP4 TFLOPS+273GB/s配NVFP4量化才把GR00T N1.7压到40ms。爱芯M97公布的“等效460GB/s”是本月车端最高的带宽口径，但“等效”的定义尚未披露。

### 小结

1. **评价端侧AI芯片，先看GB/s和GB，再看TOPS**：Decode上限≈带宽÷每token字节数，LPDDR6（96bit、10.7Gbps约114GB/s）把8B INT4的理论上限从约19提到约25 t/s，14.4Gbps才到约34 t/s。
2. **PIM的落地顺序是AI PC（2027年GAIA）→LPDDR6-PIM标准→手机**；它只加速GEMV，端到端收益约3倍，并需要OS、内存分配器和量化格式的配合。
3. **SRAM存算提升的是TOPS/W和Prefill，不解决LLM的带宽墙**；“百亿/千亿模型”宣传要看是否为MoE、激活参数多少、精度和上下文。
4. **DRAM涨价是最大的反向变量**：中端机回到8GB，端侧模型预算被压到3–4B INT4，1-bit量化、专家闪存卸载（UFS 5.0）和近存/存内计算的价值因此上升。

## 5. 顶会与业界论文：Hot Chips / MICRO / ISSCC / ISCA

**判断：** 2026 年下半年的顶会信号非常一致——端侧 LLM 的主战场已从“NPU 峰值 TOPS”转向“内存”：一是把计算塞进 LPDDR/闪存/ReRAM（PIM/CIM），二是用低比特格式与稀疏减少要搬的比特，三是在 iGPU/NPU/CPU 与 Agent 工作流之间做系统级调度。Hot Chips 2026 上三星 [LPDDR5X-PIM](https://www.servethehome.com/samsung-lpddr5x-pim-at-hot-chips-2026/) 的产品化，与 [MICRO 2026 程序](https://microarch.org/micro59/program/)中整整三个 PIM/近存专场、一个低比特专场、一个 VLA 专场，构成了产业与学术的同频共振。

> 说明：MICRO 2026 于 10/31–11/4 在雅典召开，本节论文多在 7–9 月上 arXiv；Hot Chips（8/23–25）、ISSCC/ISCA/DAC 条目属于窗口前**背景**，日期按真实发表时间标注。

### PIM / 近存：LPDDR 里开始“算”了

- **Samsung LPDDR5X-PIM（Hot Chips 2026，官方）**：16 个 bank 内置 PIM 块，PIM 内部带宽 614 GB/s，是常规 x64 LPDDR5X（76.8 GB/s）的 8×；支持 15 种精度组合，SINT4 权重 2.4 TOPS / FP8 约 1.2 TFLOPS 每封装。三星官方初步测试在自家边缘 AI SoC 上跑 Llama-3.1-8B（W4A8、320 token），81.3 vs 27.0 tokens/s（3.01×）。Address Align Mode 让常规内存控制器即可驱动，封装为 JEDEC 标准 561-ball，可直接替换；LPDDR6-PIM 正走向 JEDEC 标准。功耗/能效**未披露**。[STH 实况](https://www.servethehome.com/samsung-lpddr5x-pim-at-hot-chips-2026/)、[Tom's Hardware](https://www.tomshardware.com/pc-components/dram/hot-chips-2026-samsung-makes-lpddr5x-smart-with-logic-unit-in-memory-lpddr5x-pim-is-3-01x-faster-than-lpddr5x-in-ai-inference-with-8x-the-bandwidth)
- **PFM（ICT, MICRO'26）**：指出 NPU-PIM 统一内存“张量固定归属”假设在 prefill/decode 相变与 MoE 路由下失效，提出物理布局与逻辑视图解耦的双视图内存，吞吐最高 2.32×。这正是 LPDDR5X-PIM 进 SoC 后要解决的问题。[arXiv](https://arxiv.org/abs/2608.06989)
- **P3-LLM（ISCA'26）**：低精度 PIM 计算单元 + 混合数值格式量化 + 算子融合，平均比 HBM-PIM 快 4.9×、比 Pimba 快 3.4×，为“PIM 里放多高精度”给出依据。[arXiv](https://arxiv.org/abs/2511.06838)
- **CD-PIM（南大/中国移动，DATE'26）**：分段全局位线把 bank 拆成 4 个伪 bank，单 batch 比 GPU-only 快 11.42×、比 SOTA PIM 快 4.25×。[arXiv](https://arxiv.org/abs/2601.12298)
- **闪存/NAND 计算**：伯克利 [LLM Inference in a Flash!](https://arxiv.org/abs/2609.16161) 用 W8A8 全整数 + 32K 原子字典稀疏编码 KV，KV 动态流量降 15×，建模 CIM-SSD 在 256K 上下文下比 NPU+DDR5 延迟快 4.4×、能耗省 6.75×；北大 [NASiC](https://arxiv.org/abs/2605.23294)（DAC'26）用 CAM 掩码在 3D NAND 中单周期完成专家选择与计算，同组 MICRO'26 还有 NFC（3D NAND Flash-CIM 端侧 MoE）。SK hynix 的 C3（通用 DRAM 协同计算）也在 MICRO 程序中，细节待论文公开。

**解读：** 三星方案的关键不是 8× 内部带宽本身，而是“无需改内存控制器、可直接替换”的工程选择——这意味着手机/PC 厂商可以先在现有 SoC 上通过驱动和 SDK 接入，而学术界的 CD-PIM 等需要改动 DRAM 阵列位线，量产门槛更高。另一方面，三星演示只用了 320 token 短上下文，decode 中 attention 与 KV Cache 的读取并不在 PIM 内完成，长上下文、多轮 Agent 场景下的收益会被稀释；PFM、P3-LLM 讨论的正是“哪些算子放 PIM、哪些留在 NPU、同一份权重如何被两边共享”的问题。可以预期，下一阶段 SoC 厂商的竞争点会落在 PIM 感知的编译器与运行时上，而不仅是 NPU 的 TOPS。

### 低比特与稀疏：格式之争从 INT4 走向“块缩放变体”

- **MiX（Cornell Tech, MICRO'26）**：每元素私有指数、组共享尾数，解决 MX/NVFP4 的“微缩放坍塌”；4.5-bit 精度≥NVFP4，面积效率 +25%，对 Focus 快 2.3–4.5×。[arXiv](https://arxiv.org/abs/2609.19683)
- **MICRO'26 低比特专场**还有 HBQ（Cornell）、FlexPosit（UVA）、W4A4 micro-block（ICT）、SkewQ（华科），以及 LUT 专场的 TNT（MSRA，超低比特 + 原生 KV 计算）、FLUTE（中科院自动化所）——LUT 化与块缩放是两条并行主线。[程序](https://microarch.org/micro59/program/)
- **Deltoris（SJTU/ICT, MICRO'26）**：VLA 需 50–200 Hz 控制频率，用相邻帧差分 + 比特级稀疏 + 跨控制步投机推理，对移动 GPU 最高 34.2×。[arXiv](https://arxiv.org/abs/2608.04428)

**解读：** 端侧 NPU 过去几代以 INT8/INT4 为主，MICRO'26 的信号是：块缩放浮点（NVFP4/MXFP4）及其变体会下沉到端侧，而它们的离群值问题需要格式层面的修补（MiX 的私有指数、HBQ 的分层缩放）。对芯片设计者而言，这意味着 MAC 阵列需要同时支持多种块格式与 LUT 查表路径，数据通路复杂度上升；对模型厂商而言，量化方案将越来越与具体 NPU 格式绑定。

### KV Cache 与长上下文

- 伯克利字典式 KV（见上）把 KV 写入变成稀疏系数，解决闪存写寿命问题。
- Georgia Tech [块扩散 LLM 端侧加速](https://arxiv.org/abs/2609.01084)：BRQ-KV 用低秩 + INT8 残差、按 query 选精度的前缀缓存，配合 WIFiV-LPDDR 精度标记读；7B 模型延迟 4.44×、能耗 3.96×，掉点 <1pp。
- MICRO'26 还有 Duke 的 Gossamer（推理模型恒定预算 KV 压缩）、KAIST MemLLM（存储内预计算 KV 的 RAG），显示“推理模型的长输出 KV”成为新目标。

**解读：** 端侧长上下文的瓶颈正在从“权重带宽”转为“KV 带宽 + KV 容量”，尤其是推理模型动辄数千 token 的思考过程。学术界的共同做法是把 KV 表示为低秩/字典/低比特残差，从而既省带宽又适配非易失介质；但这些方案都改变了 attention 的数值路径，需要 NPU 原生支持稀疏系数或低秩乘法，短期更可能先在专用 IP 或 PIM 侧落地。

### NPU / 编译与异构调度

- **HeteroMosaic（UIUC/AMD, MICRO'26）**：异构 roofline + 因果 micro-batch，在 Ryzen AI 上让 iGPU 与 NPU 同时跑同一 LLM，比 llama.cpp 快 2.05×、能耗降 45.3%；iGPU 越弱（AI 7 350）理论收益越大（约 3×）。[arXiv](https://arxiv.org/abs/2607.12839)
- **Intel Wildcat Lake（Hot Chips 2026，官方）**：18A 计算 die + 有机 MCP/UCIe 8 GT/s，NPU 引擎数、GPU、内存位宽均比 Panther Lake 缩减，主打成本；NPU TOPS 演讲报道中**未披露**。[STH](https://www.servethehome.com/intel-core-series-3-wildcat-lake-cpu-at-hot-chips-2026/)
- UIUC 同组还有“NPU 空间细粒度 DVFS”“异构 NPU 自动伸缩”（MICRO'26 Distinguished/2A 场），说明 NPU 内部功耗管理开始被当作架构问题研究。

### 端侧系统与 Agent 调度

- **EdgeAgent（中山大学/中国移动）**：Apple M4 统一内存上零拷贝张量并行 + 按可预测性分配 draft 预算 + 工具调用期间挂起 agent，整体 1.77×。[arXiv](https://arxiv.org/abs/2610.03394)
- **PELM（SenSys'26）**：在 DVFS 外加入投机解码与可变验证深度，最高提速 23.1%、能耗降 52.4%，面向无风扇设备的热约束。[arXiv](https://arxiv.org/abs/2609.09662)
- **边缘连续体测量（WIMS'26）**：Jetson AGX Orin 能耗更低但延迟高于 GPU 服务器；计入流式 token 下发后 Pareto 最优点会改变。[arXiv](https://arxiv.org/abs/2609.08307)

**解读：** 三篇工作都说明，端侧 LLM 的实际性能越来越取决于运行时：多引擎争用同一条 LPDDR 总线时，盲目并行反而变慢（EdgeAgent 的 UMA 争用、HeteroMosaic 的内存争用建模）；在无风扇设备上，持续性能由热约束决定（PELM）。这对手机厂商的启示是，NPU 驱动、OS 调度器与推理框架需要共享一份“带宽/热预算”视图，而不是各自为政。

### 电路级与低功耗芯片

- **EdgeXpert（KAIST, MICRO'26 Distinguished 场）**：MoE + 投机解码首次兼容，Samsung 28nm 综合 9.3 mm²、1.52 W、13.1 TOPS（A8W4），配 LPDDR4X 16 GB/s 即可在 Qwen3-30B-A3B 上满足 TTFT<450 ms、TPOT<50 ms，延迟最多降 56.3%。[arXiv](https://arxiv.org/abs/2608.05303)
- **HKUST ReRAM-on-Logic（ISSCC'26 31.1，流片）**：55nm 面对面堆叠，14.08–135.69 tokens/s，LLaMA2-7B 17.82 tokens/s @123.41 mJ/token。[arXiv](https://arxiv.org/abs/2605.09375)
- **清华 28nm 投机解码处理器（ISSCC'26）**：105–685 µs/token，10.29× 加速。[DOI](https://doi.org/10.1109/ISSCC49663.2026.11408953)
- Hot Chips 2026 海报中还有 Harvard/Lockheed 的 **Pistil**（16nm、20 chiplet 2.5D SiP 分布式 SLM 推理，同时入选 MICRO'26 Distinguished 场）、KAIST 低功耗实时 VLN 处理器、伯克利 Intel 16 双芯片多模态边缘平台 Gemmelos。[海报列表](https://hc2026.hotchips.org/program/posters/)

### Top Picks

| 工作 | 会议 | 机构 | 核心机制 | 关键数字 |
|---|---|---|---|---|
| LPDDR5X-PIM | Hot Chips 2026 | Samsung | bank 内 PIM，15 种精度 | 614 GB/s 内部带宽（8×）；Llama-3.1-8B 3.01× tokens/s |
| EdgeXpert | MICRO 2026 | KAIST | MoE+投机解码专家复用/合并 | 1.52 W、9.3 mm²；延迟 −56.3%、能耗 −44.1% |
| HeteroMosaic | MICRO 2026 | UIUC/AMD | iGPU+NPU 因果 micro-batch | 对 llama.cpp 2.05×，能耗 −45.3% |
| PFM | MICRO 2026 | 中科院计算所 | NPU-PIM 双视图内存 | 吞吐最高 2.32× |
| MiX | MICRO 2026 | Cornell Tech | 私有指数/共享尾数 4.5-bit | 面积效率 +25%，对 Focus 2.3–4.5× |
| LLM in a Flash | arXiv（9/14） | UC Berkeley | 全整数 + 字典 KV | KV 流量 −15×；256K 下 4.4× 延迟 |
| 块扩散 LLM 加速 | arXiv（9/1） | Georgia Tech | BRQ-KV + DAT-FFN + 宽 I/O LPDDR | 7B 延迟 4.44×、能耗 3.96× |
| ReRAM-on-Logic | ISSCC 2026 | HKUST | 堆叠 PNM + 并行投机解码 | 14.08–135.69 tokens/s |
| P3-LLM | ISCA 2026 | Cornell 等 | 低精度 PIM + 混合格式 | 对 HBM-PIM 4.9× |
| Deltoris | MICRO 2026 | SJTU/ICT | 时域比特稀疏 VLA | 对移动 GPU 34.2× |

### 小结

1. **PIM 从论文走向 JEDEC**：三星 LPDDR5X-PIM 产品化 + LPDDR6-PIM 标准化，学术界随即转向“SoC 如何用好 PIM”（PFM、P3-LLM、CD-PIM）；未来 1–2 年手机/AI PC 的 decode 带宽可能不再由 LPDDR 外部接口决定。需要注意：三星尚未披露功耗，学术结果多为仿真。
2. **容量墙接替带宽墙**：MoE 与长输出推理模型让“放得下”比“搬得快”更重要，3D NAND/闪存/ReRAM CIM（NASiC、NFC、LLM in a Flash、HKUST 堆叠）是主要解法，KV 压缩开始针对写寿命设计。
3. **投机解码硬件化**：EdgeXpert、HKUST、清华 ISSCC、CrossSpec、Deltoris 都把 draft/verify 写进数据通路，这对 NPU 指令集与调度器提出了新需求。
4. **系统层收益不亚于芯片层**：HeteroMosaic、EdgeAgent、PELM 只靠调度就拿到 1.3–2× 性能或 50% 级节能，提示端侧 Agent 的瓶颈正转向多引擎协同、热约束与工具停顿。

## 6. 本月 arXiv 端侧硬件论文精选

本月（2026-09-02 ~ 10-07）arXiv 上端侧 LLM 硬件/系统方向的论文明显转向两件事：一是**用闪存（UFS/SSD）和 MoE 稀疏性突破手机 DRAM 容量墙**，已有工作在 Snapdragon 手机上跑到 80B 总参 MoE；二是**让静态图 NPU 适配动态负载**（MoE 路由、KV 复用、线性注意力），多篇来自上交、北大、阿里、AMD 的论文用实机 Hexagon/XDNA/昇腾给出数据。与此同时，热、能耗、统一内存带宽争用这些“持续运行”问题开始有专门的测量研究。存内/近存方向仍以仿真和建模为主，本月没有看到新的流片结果。

### 一、手机上的 MoE：闪存当仓库，NPU 当执行器

- [EStream](https://arxiv.org/abs/2609.06551)（上交/中国电信）解决 MoE **预填充**：用一张编译好的专家图服务所有专家，调用时再绑定 token 与权重地址，专家池放在 UFS 4.1 里，经固定大小的 NPU arena 分页换入。在 Snapdragon 8 Elite Gen 5（Hexagon v81）上，TTFT 加速 2.25–27.57×，峰值内存降 1.19–12.29×，能效几何平均提升 4.08×；Qwen3-30B-A3B 达到 43.59–72.18 tokens/J，可扩展到 46.7B 的 Mixtral-8x7B。
- [BigMoMo](https://arxiv.org/abs/2609.14643)（北大）解决 MoE **解码**：借投机解码的多 token 验证窗口让一次专家搬运服务多个 token，并按共加载模式重排闪存布局、热专家直接放进 VTCM。在三代 OnePlus 手机上平均快 4.83×（对按需卸载）、1.82×（对最佳投机 MoE 基线），最大跑到 Qwen3-Next-80B-A3B。
- [LeanStream](https://arxiv.org/abs/2609.03079)（GMU/摩根大通，MobiCom '26）面向稠密 7B + 激活稀疏，只在 DRAM 放 20% 权重时，Jetson AGX Orin 上 Mistral-7B / Llama2-7B / Qwen2.5-7B 跑到 16.4 / 18.3 / 19.8 tok/s。
- 两项“校准型”工作值得参考：[Paging the Experts](https://arxiv.org/abs/2609.29032) 在 iPhone 17 Pro Max 上用闪存跑 Qwen3.6-35B-A3B，进程占用只有 1.9–2.7 GiB，但冷启动解码仅 2.2–3.2 tok/s，512 token 运行的逻辑读约 320 GB；[Edge0](https://arxiv.org/abs/2609.18063)（AutoArk）训练 prerouter 预测下一层路由，在 24 GB Mac mini M4 Pro 上以 20.4 tok/s、2.9 GiB 跑同一个 35B MoE，全驻留的 mlx-lm 只有 3.9 tok/s、占 18.2 GiB。

判断：“大总参、小激活”的 MoE 加上 UFS 4.x 已经是端侧扩容的主要路线。瓶颈从算力转到**闪存读放大和预测准确率**，因此模型与系统协同（预测路由、投机窗口）比单纯改缓存策略更有效。

### 二、静态图 NPU 遇上动态负载：KV 复用、长上下文与新注意力

- [KV Cache Reuse on Mobile NPUs](https://arxiv.org/abs/2609.34727)（上交/阿里，EuroSys '27）把选择性 KV 重算做进 ExecuTorch 的 HTP 静态图，并用闪存做分层 KV 存储。在 Meizu 21 / Xiaomi 15 Pro / Honor Magic 8 三代 Hexagon（V75/V79/V81）上，TTFT 降 32–81%。Xiaomi 15 Pro 上平均功耗基本不变（6.34 W vs 6.68 W），所以预填充能耗随之降 52–77%。这篇直接对应端侧 Agent 里反复出现的 skill 描述、记忆和检索片段。
- [TierKV](https://arxiv.org/abs/2609.21172)（UGA/北大/WD，EuroSys '27）把 KV 分成精确、低秩、闪存三层，在 OnePlus 12 的 6.8 GB 稳定内存预算下，Gemma4 E2B 上下文从 50k 扩到 128k，预填充最高 17.6×。
- [HA-NPU](https://arxiv.org/abs/2609.32114)（北大/北邮）指出 Qwen3.5 等混合线性注意力模型在边缘 NPU 上的预填充瓶颈在数据流本身，在 Ascend 310P/310B 上 LA 内核最高快 35.95×、端到端快 2.03×。这提示手机 NPU 编译器也要为 GDN/KDA 这类递推状态做专门优化。
- [OmniTide](https://arxiv.org/abs/2609.34653) 处理流式全模态的 KV 膨胀（MiniCPM-o-4.5 处理 375 秒视频时 KV 近 80K token、约 23 GiB），在 M2 Pro 上实现 12.72× 内核加速。

### 三、NPU 编程与低比特数据通路

- [AMD XDNA FlashAttention](https://arxiv.org/abs/2609.21264) 是厂商一手经验：在 Ryzen AI 9 HX 370（XDNA 2）上，融合注意力达到 3.62 TFLOP/s（GEMM 口径），是 IRON 流式设计的 2 倍；≥2K token 时能效是同芯片 iGPU 的 5.3–7.2 倍。核心结论是用每一级存储的 ridge point 判断还要不要继续融合：XDNA 1 上同样的融合几乎没有收益。
- [BitNet on CGLA](https://arxiv.org/abs/2609.27453)（NAIST）用一条通用的有符号 int4 MAC 指令承载三值权重，按 28 nm/840 MHz 折算为 0.390 ns/乘积，但端到端只有 2.52 tokens/s。可编程方案的可行性有了，性能还远不够。

### 四、持续运行：热、能耗与统一内存争用

- [PELM](https://arxiv.org/abs/2609.09662)（Northwestern，SenSys '26）把投机解码和早退深度加进 DVFS 的动作空间，在 Jetson Orin 上最高节能 52.4%。
- [ThermE](https://arxiv.org/abs/2610.00267) 把 CPU/GPU/RAM 共享的热余量当作可调度资源，在 65 °C 环境下 TTFT 降 40.55%，SLO 违约率从 12.30% 降到 5.70%。
- [iPhone 17 Pro 微调 3B](https://arxiv.org/abs/2610.06325)（Saarland）：SmolLM3-3B 4-bit LoRA 训练约 0.04 J/token，405 条记录的用户耗电 47%。持续训练会把吞吐降到约一半；作者还修复了 MLX 中从未被调度的量化反向内核，训练提速 1.47×。
- [PhaseGate](https://arxiv.org/abs/2610.04537)（KAIST）测得 M4 上 4 个并发 CPU 检索会让 p95 解码时延上升 60–61%，预填充只上升 5.7–6.9%。解码对带宽干扰极敏感，因此端侧 RAG 必须按阶段调度。
- 已收录的 [EdgeAgent](https://arxiv.org/abs/2610.03394)（ASPLOS '27）在 M4 上同时用 SME2 CPU 与 GPU，多 Agent 场景加速 1.77×；[边缘连续体实测](https://arxiv.org/abs/2609.08307) 确认 Jetson AGX Orin 的能耗低于 T4 服务器。

### 五、存内/近存与新型存储接口（仿真为主）

- [LLM Inference in a Flash!](https://arxiv.org/abs/2609.16161)（Berkeley）在闪存 CIM 上做全整数 W8A8 和字典式 KV 压缩，KV 流量降 15×；按分析模型，长上下文时延/能耗收益为 4.4×/6.8×。
- [NVM KV 量化](https://arxiv.org/abs/2609.05764)（Notre Dame，ICCAD '26）让量化格式迁就读出电路，KV 读能耗降 3.1–3.6×，元数据从约 25% 降到约 3%。
- [时域模拟 Softmax](https://arxiv.org/abs/2609.04266)（22nm FDSOI 后仿）做到 25.5 pJ/元素、242.97 ns。
- [块扩散 LLM + WIFiV-LPDDR](https://arxiv.org/abs/2609.01084)（Georgia Tech，v1 为 09-01，略早于窗口）在 Jetson 级平台的建模中，能耗降 3.79–3.96×。

### 汇总表

| 论文 | 机构 | 硬件平台 | 关键结果 |
|---|---|---|---|
| [EStream](https://arxiv.org/abs/2609.06551) | 上交/中国电信 | Snapdragon 8 Elite Gen 5，Hexagon v81，UFS 4.1（实机） | MoE 预填充 TTFT 2.25–27.57×，内存 ↓1.19–12.29×，最大 46.7B |
| [BigMoMo](https://arxiv.org/abs/2609.14643) | 北大 | 三代 Snapdragon OnePlus（实机） | 解码 4.83× / 1.82×，最大 80B MoE |
| [KV Reuse on NPU](https://arxiv.org/abs/2609.34727) | 上交/阿里 | Hexagon V75/V79/V81（实机） | TTFT ↓32–81%，预填充能耗 ↓52–77% |
| [TierKV](https://arxiv.org/abs/2609.21172) | UGA/北大/WD | SD 8 Gen 3/8 Gen 2/Tensor G3（实机） | 预填充 17.6×，Gemma4 E2B 128k 上下文 |
| [HA-NPU](https://arxiv.org/abs/2609.32114) | 北大/北邮 | Ascend 310P/310B（实机） | LA 内核 35.95×，端到端 2.03× |
| [XDNA FlashAttention](https://arxiv.org/abs/2609.21264) | AMD/ETH/Cornell | Ryzen AI 9 HX 370（实机） | 3.62 TFLOP/s，能效 5.3–7.2× iGPU |
| [LeanStream](https://arxiv.org/abs/2609.03079) | GMU/摩根大通 | Jetson AGX Orin、OnePlus 13（实机） | 7B 16.4–19.8 tok/s（20% 权重驻留） |
| [Edge0](https://arxiv.org/abs/2609.18063) | AutoArk | Mac mini M4 Pro 24GB（实机） | 35B MoE 20.4 tok/s @ 2.9 GiB |
| [Paging the Experts](https://arxiv.org/abs/2609.29032) | 独立研究者 | iPhone 17 Pro Max（实机） | 35B MoE 约 1.8–3.2 tok/s，占用 1.9–2.7 GiB |
| [iPhone 微调 3B](https://arxiv.org/abs/2610.06325) | Saarland | iPhone 17 Pro（实机） | 0.04 J/token，MLX 反向修复 1.47× |
| [PELM](https://arxiv.org/abs/2609.09662) | Northwestern | Jetson AGX Orin / Orin Nano（实机） | 能耗 ↓52.4%，速度 +23.1% |
| [ThermE](https://arxiv.org/abs/2610.00267) | 港理工/南科大 | Jetson AGX Orin 64GB（实机） | TTFT ↓40.55%，违约率 5.70% |
| [PhaseGate](https://arxiv.org/abs/2610.04537) | KAIST | Apple M4/M2（实机） | 检索吞吐 2.0×，p95 ≤1.25× |
| [OmniTide](https://arxiv.org/abs/2609.34653) | 北大/北邮 | Apple M2 Pro、RTX 4090（实机） | 内核 12.72×，+18.0 pt |
| [NVM KV 量化](https://arxiv.org/abs/2609.05764) | Notre Dame | RRAM 片上 NVM（仿真） | KV 读能耗 ↓3.1–3.6× |
| [CIM Softmax](https://arxiv.org/abs/2609.04266) | UW-Madison/ORNL | GF 22nm FDSOI（后仿） | 25.5 pJ/元素 |
| [BitNet on CGLA](https://arxiv.org/abs/2609.27453) | NAIST | Versal FPGA → 28nm 折算 | 2.52 tok/s |
| [LLM in a Flash!](https://arxiv.org/abs/2609.16161) | UC Berkeley | Flash CIM（建模） | KV 流量 ↓15×，长上下文 4.4×/6.8× |

### 端侧“能跑多大模型”：本月论文实测口径汇总

下表只列论文中明确给出的设备、模型与指标，口径不同（预填充 tokens/J、解码 tok/s、训练 J/token），不能横向直接比较；“未披露”表示摘要或正文摘录中没有给出绝对值，只给了相对加速。

| 设备 / SoC | 模型（总参/激活，精度） | 指标 | 来源 |
|---|---|---|---|
| OnePlus（SD 8 Elite Gen 5，15.1 GiB） | Qwen3-30B-A3B，Q4_0 专家 | 预填充 43.59→72.18 tokens/J（1K→4K） | EStream |
| OnePlus（SD 8 Elite Gen 5） | Mixtral-8x7B（46.7B），Q4_0 | 预填充 23.41→35.76 tokens/J | EStream |
| OnePlus 15（SD 8 Elite Gen 5，16 GB） | Qwen3-Next-80B-A3B，Q4_0 + 草稿模型 | 8B–80B 各规模 TPOT 均最低，绝对值未披露（四模型平均对最佳投机基线 1.82×） | BigMoMo |
| Xiaomi 15 Pro（SD 8 Elite，Hexagon V79） | Qwen3-4B，INT4 | 预填充约 6.3 W，能耗 ↓52–77% | KV Reuse |
| OnePlus 12（SD 8 Gen 3，6.8 GB 预算） | Gemma4 E2B / Llama-3.2-1B | 最长上下文 128k / 72k（解码 ≥1 tok/s 约束） | TierKV |
| Jetson AGX Orin + SSD | Mistral-7B / Llama2-7B / Qwen2.5-7B | 16.4 / 18.3 / 19.8 tok/s（20% 权重驻留） | LeanStream |
| iPhone 17 Pro Max | Qwen3.6-35B-A3B，量化 | 冷启动 2.2–3.2 tok/s，持续 1.8–2.1 tok/s | Paging the Experts |
| Mac mini M4 Pro 24 GB | Qwen3.6-35B-A3B，int4（19.5 GB） | 20.4 tok/s @ 2.9 GiB | Edge0 |
| Apple M4 32 GB | Llama-3.1-8B / R1-Distill-Llama-8B，FP16 | 相对 1.77×（绝对值未披露） | EdgeAgent |
| iPhone 17 Pro（A19 Pro） | SmolLM3-3B，4-bit LoRA 训练 | 0.04 J/训练 token，满电约 130 万 token | iPhone 微调 |

从表里看，手机上 30B 级 MoE 的预填充（EStream）和解码（BigMoMo）都已有实机结果，但解码绝对速度普遍没有公开或偏低。Apple 平台上，同样的 35B MoE 因调度方式不同，速度从 2 tok/s（iPhone 朴素分页）到 20 tok/s（M4 Pro 预测流式）都有，差距约 10 倍。这说明现阶段判断端侧 SoC“能跑多大模型”时，运行时设计的影响不比 DRAM 容量小。

### 小结

1. **容量墙的解法已经从“压模型”转到“分页 + 预测”**。手机上 30B–80B MoE 已能跑起来，但实际速度差别很大：好的系统靠投机/预测把闪存读批量化；朴素分页在 iPhone 上只有 2–3 tok/s。UFS 带宽和 NPU 本地存储（VTCM/arena）因此成为 SoC 的关键指标。
2. **NPU 软件栈是当前的主要瓶颈**。MoE 路由、非前缀 KV 复用、线性注意力都与静态图冲突，本月最好的结果都来自“运行时绑定 + 编译期固定”的折中设计。厂商 SDK 需要原生支持这些模式。
3. **持续性能和能耗要按“任务”计量**。热降频可以让吞吐减半，统一内存争用可以让解码 p95 上升 60%。评估端侧芯片时，应在恒温、长时间、多任务条件下测 J/token 和持续 tok/s，只看峰值 TOPS 不够。
4. **存内/近存方向仍停在仿真**。量化格式与存储接口协同设计（NVM 读出、精度标签 LPDDR、闪存字典 KV）是值得跟踪的方向，但本月没有新的流片证据。

## 7. 产业格局：份额、代工与整机

- **份额**（Counterpoint，Q2'26 手机 AP）：联发科 31%、高通 23%、苹果 19%、展锐 13%（受内存危机冲击）、三星 9%（历史新高）、海思 5%。
- **代工**：台积电 N2 已承接 A20 Pro、M6、天玑 9600 Pro 和骁龙 Gen 6。三星 SF2/SF2P 良率传闻为 60–70%，Exynos 2700 据报已量产。
- **整机**：TrendForce 预计 2026 年手机产量 10.7 亿部，同比 -14%；内存成本推高售价、压缩配置。
- **专利与授权**：高通与华为签署交叉许可（10-05），高通诉 Arm 案同日开庭，Arm 的授权模式仍是安卓阵营的变量。

## 8. 总结：对端侧智能体意味着什么，以及接下来盯什么

**对端侧智能体的含义**

1. **手机端的目标模型变成 10–30B 稀疏 MoE。** 能否用起来取决于三件事：
   - 容量：12GB 是门槛，单模型预算大约 6GB。
   - 带宽：LPDDR6、位宽和片上共享内存。
   - 运行时：闪存专家分页、预测预取、投机解码。

   TOPS 的影响排在这三者之后。选模型时，优先选激活参数在 3B 以内的 MoE，或 1–2 bit 的稠密模型。
2. **芯片开始为智能体专门设计。** 例子包括：
   - 常驻感知 NPU：Sensing Hub、CIM NPU。
   - KV Cache 硬件压缩和 Element Accelerator。
   - GPU 矩阵单元，用来缩短 prefill。
   - 隐私隔离：Secure Exclave、Execution Containers。

   多轮工具调用需要长时间维持推理功耗，所以 WMCM、Offset PoP 这类散热封装同样重要。iPhone Duo 的持续性能只有 +35%，说明同一颗芯片放进不同机身，持续吞吐可能差一个档次。
3. **分布式端侧智能体成形。** 分层如下：
   - 耳机、手表、眼镜：常驻感知，模型在百万到 20 亿参数之间。
   - 手机：主推理，3B 稠密到 30B MoE。
   - PC：统一内存 128–192GB，能跑 100B 级以上的 MoE。
   - 车和机器人：500–700 TOPS 级平台。
   - 云端兜底：PCC、Cloud Pro 等。
4. **NPU 后端更碎片化，跨平台运行时更有价值。** Hexagon、NPU 1090、ANE、达芬奇、CIM NPU、XDNA 各不相同；静态图与动态负载的矛盾要靠运行时解决，例如 Core AI、QAIRT/GenieX、LiteRT、Arm KleidiAI。
5. **成本是反向变量。** DRAM 第四季度继续涨价，中端机回落到 8GB，只能跑 3–4B INT4 模型。极低比特量化、闪存卸载、近存和存内计算的商业价值因此上升。

**下月观察清单**

- 首批量产机（小米 18 Pro Max、vivo X500 Pro、Find X10、Mate 90、iPhone 18 Pro）的第三方统一测试：用同一模型测 prefill 和 decode 的 tok/s、J/token 和持续性能。这是验证“30B 上手机”的关键数据。
- 骁龙 8 至尊版 Gen 6 标准版到底有没有矩阵核心和 LPDDR6：拆解和实机会给出答案。
- 高通 GenieX 和 QAIRT 何时在 NPU 路径支持 MoE 与投机解码；Apple Core AI 的第三方模型性能。
- JEDEC LPDDR6-PIM 标准何时发布；三星 GAIA 的量产时间表；高通 HBC 移动版的细节（MWC 2027）。
- MICRO 2026（10/31–11/4，雅典）的正式报告：EdgeXpert、HeteroMosaic、PFM、MiX、Deltoris 等。
- M6 MacBook Pro / iMac（传 10 月）；RTX Spark 上市后的本地智能体实测。

## 附：窗口边缘条目（未计入周报模块）

- 08-12：Google Tensor G6 / Pixel 11（背景，详见第 3 节）。
- 08-24 / 08-25：Hot Chips 2026 的 Intel Wildcat Lake 和三星 LPDDR5X-PIM 报告（背景，详见第 4、5 节）。
- 09-01：佐治亚理工的块扩散 LLM 边缘硬件（[arXiv 2609.01084](https://arxiv.org/abs/2609.01084)，比窗口早一天）。
- 10-07：微软 Surface Laptop Ultra（RTX Spark）开启预订（[Windows Blog](https://blogs.windows.com/devices/2026/10/07/pre-order-our-most-powerful-surface-devices-ever/)）；RTX Spark PC 全面预订，10-16 出货。

> 口径说明：标“官方”的是厂商发布的数字，“媒体实测”和“第三方实测”是独立测试，“爆料”未经确认，“推算”或“估算”是本文按公开参数计算的结果。部分厂商官网无法抓取，相关条目以多家媒体交叉印证，并标为中等可信。
