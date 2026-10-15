# 硬件洞察：端侧 AI 芯片月报（2026-01-01 ~ 2026-01-29）

> **说明：** 本期为 2026-10 回填。窗口内各周此前没有硬件雷达，条目全部来自回填时重新核实的一手页面、媒体报道和论文。1 月 30 日之后的事件（HPCA、ISSCC、Galaxy S26、各家 2 月财报）归入 2 月。
>
> **一句话结论：1 月是“CES 月”，也是“内存月”。** 新芯片集中在 PC 和边缘：骁龙 X2 Plus、锐龙 AI 400、酷睿 Ultra 3 同周发布，NPU 普遍在 50–80 TOPS，手机 SoC 只有天玑 9500s / 8500。真正的变量是内存：TrendForce 预计 1Q26 常规 DRAM 合约价环比涨 55–60%，Apple 在财报会上点名内存涨价会压低毛利。模型与软件侧，Apple 下一代基础模型改用 Gemini 打底，Google 让 LiteRT 接班 TFLite。研究侧都在减少数据搬运，但绝大多数是仿真。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断与时间线；第 1–6 节依次为 高通 / Apple 与 Google / 其他 SoC 与 PC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选；第 7 节是总结。逐条动态（含“能跑多大模型”和可展开的“技术细节”）见 01-02、01-09、01-16、01-23 四周首页的“硬件雷达”。

## 0. 总览：1 月的五个判断

**判断一：PC 的 NPU 到了 50–80 TOPS，分档开始看内存带宽。**

| 芯片（01-05 发布） | NPU | 内存 / 带宽 | 口径 |
|---|---|---|---|
| 骁龙 X2 Plus | 80 TOPS，与 X2 Elite 相同 | 152 GB/s；X2 Elite 高配 228 GB/s | 官方；带宽来自媒体整理 |
| 锐龙 AI 400 | 50 / 55 / 60 TOPS | 128-bit LPDDR5X，约 136–154 GB/s | 官方；带宽为推算 |
| 酷睿 Ultra 3（首款 18A） | 46–50 TOPS，平台合计最高 180 TOPS | LPDDR5X-9600，最大 96 GB | 官方 + 媒体规格表 |
| 按 152 GB/s 推算 | — | 8B INT4 decode 上限约 34 tok/s | 推算，实际约五到七成 |

本地大模型主力仍是 GPU；窗口内没有这三款芯片的第三方 LLM 实测。

**判断二：“能装下”和“能流畅跑”差一个数量级。**

| 平台 | 宣传口径 | 实际速度 | 口径 |
|---|---|---|---|
| 锐龙 AI Halo（128 GB） | 可跑 200B | 按约 256 GB/s，稠密 200B decode 约 2–3 tok/s | 官方容量 / 推算 |
| [Jetson T4000](https://developer.nvidia.com/blog/accelerate-ai-inference-for-edge-and-robotics-with-nvidia-jetson-t4000-and-nvidia-jetpack-7-1)（64 GB，273 GB/s） | Qwen3-30B-A3B 218 tok/s，Qwen3 32B 68 tok/s | 32B 稠密单流上限约 15–17 tok/s，68 应为并发吞吐 | 官方 / 推算 |
| [DEEPX DX-M2](https://deepx.ai/ces-2026-media-briefing-deepx-unveils-physical-ai-vision-roadmap/) | 5W 内跑 20B–100B | 按 153.6 GB/s，稠密 100B 约 3 tok/s | 路线图；带宽来自媒体 |
| Dragonwing Q-8750 | 77 TOPS 跑 11B | 未公布速度和精度 | 官方 |

**判断三：内存是最硬的外部约束，而且 1 月的预测偏保守。**

| 信号 | 数字 | 口径 |
|---|---|---|
| [TrendForce](https://www.trendforce.com/presscenter/news/20260105-12860.html)（01-05） | 1Q26 常规 DRAM 环比 +55–60%；2 月上修到 +90–95% | 研究机构 |
| TrendForce（01-15 / 01-26） | 2026 年手机产量预测下调到 -7%；1Q26 笔记本出货环比 -14.8% | 研究机构 |
| 韩媒（01-27） | 三星、SK 海力士向 Apple 要价 LPDDR 一季度涨 80%–100% | 爆料，未证实 |
| [Apple 财报](https://www.apple.com/newsroom/2026/01/apple-reports-first-quarter-results/)（01-29） | 下季度毛利率指引 48%–49%，已计入更大的内存影响 | 官方 + 媒体整理 |
| [美光](https://micron.gcs-web.com/node/49981)（01-17） | 18 亿美元买力积电铜锣厂，有意义的产出要到 2027 年下半年 | 官方 |

**判断四：端云分工重划，运行时比芯片更能决定端侧生态。** 01-12 的[联合声明](https://blog.google/company-news/inside-google/company-announcements/joint-statement-google-apple/)称下一代 Apple Foundation Models 基于 Gemini，Apple Intelligence 仍运行在设备与 PCC 上；爆料称新 Siri 模型 AFM v10 约 1.2 万亿参数、跑在 PCC。

| 发布 | 数字 | 口径 |
|---|---|---|
| [LiteRT](https://developers.googleblog.com/litert-the-universal-framework-for-on-device-ai/)（01-28） | GPU 平均比 TFLite 快 1.4 倍；Gemma 3 1B 在 S25 Ultra 上 NPU prefill 比 GPU 快 3 倍；NPU 量产名单只有联发科和高通 | 官方，只有相对倍数 |
| MLX 0.30.3 / 0.30.4（01-13 / 01-27） | M4 Max 上 Qwen3 4B mxfp4 约 141 tok/s；M5 神经加速器 Split-K GEMM 最高约 1.62 倍 | 开发者实测 |
| 高通 AI Hub（01-26） | QAIRT 2.42，上线 IQ9075（100 TOPS）真机 | 官方 |

**判断五：研究侧的共识是“少搬数据”，但几乎全停在仿真。**

| 研究 | 结果 | 口径 |
|---|---|---|
| [Patterson 等](https://arxiv.org/abs/2601.05047)（01-08） | 单条 LPDDR5-6400 约 51 GB/s；PIM 在移动端可能可行 | 论文 |
| [CD-PIM](https://arxiv.org/abs/2601.12298)（01-18） | iPhone 15 Pro 级配置下 LLaMA-1B 快 18.6 倍，新增 144 mW | 模拟 |
| [Platinum](https://arxiv.org/abs/2511.21910)（ASP-DAC） | 能耗比 T-MAC 低 15.0–20.9 倍；3.2 W 中 DRAM 占 53.5% | 综合 / 仿真 |
| [ROMA](https://arxiv.org/abs/2503.12988)（ASP-DAC） | 2-bit Llama3-8B 整模上片，但 7nm 503.7 mm²、33.1 W | 仿真 |
| [ZipMoE](https://arxiv.org/abs/2601.21198)（01-29） | Jetson AGX Orin 上 MoE 延迟最多降 72.77% | 真机实测 |

ASP-DAC 的 11 篇都没有流片实测。另外，端侧 AI 正外溢到车、机器人和可穿戴（IQ10 350 dense TOPS、零跑 D19、Arm 物理 AI 事业部、Ambiq Atomiq），见第 1、3、4 节。

### 1 月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 01-05 | CES：骁龙 X2 Plus、Dragonwing IQ10 / Q-8750、零跑 D19；锐龙 AI 400 / AI Halo；酷睿 Ultra 3；Jetson T4000；TrendForce 预计 DRAM +55–60% | PC / 边缘 / 内存 |
| 01-06 | Ambiq Atomiq、Nordic nRF54LM20B、DEEPX DX-M2、ASUS UGen300、恩智浦 eIQ Agentic；SK 海力士展 LPDDR6；高通 Chassis Agents | 低功耗 / 车载 |
| 01-07~09 | Rokid 双芯眼镜；爆料：高通与三星洽谈 2nm；Patterson 内存墙综述；Arm 物理 AI 事业部 | 眼镜 / 产业 / 研究 |
| 01-12 | Apple–Google 联合声明；DeepSeek Engram；Sherry 1.25 bit | Apple / 研究 |
| 01-13~15 | MLX 0.30.3；MedGemma 1.5、TranslateGemma；天玑 9500s / 8500；台积电财报；NanoSD | 模型 / 移动 SoC |
| 01-17~18 | 美光收购铜锣厂；CD-PIM | 内存 |
| 01-19~22 | ASP-DAC（香港）：BitROM、ROMA、Platinum、BitStopper 等；爆料 Siri 改为 Campos、AI 胸针；英特尔财报 | 研究 / Apple |
| 01-25~27 | 爆料 AFM v10 约 1.2 万亿；AI Hub 上线 IQ9075；MLX 0.30.4；vllm-mlx；爆料 Apple LPDDR 涨 80%–100% | Apple / 软件 / 内存 |
| 01-28~29 | LiteRT 接班 TFLite；Gemini Nano v3 确认源自 Gemma 3n；SK 海力士、三星、Apple 财报；Apple 收购 Q.ai；ZipMoE | Google / 内存 / 研究 |

## 1. 高通：CES 上 X2 Plus、IQ10 与 Dragonwing 全线铺开

### 总览：一月的高通是“CES 月”，主角不是手机

2026 年 1 月（1/1–1/29）高通几乎所有一手发布都集中在 CES 2026（1/6–1/9，拉斯维加斯）开幕前后的 1 月 5–8 日。和往年不同，这个月高通没有发布任何新手机 SoC：Snapdragon 8 Elite Gen 5 在 2025 年 9 月已发布，下一代 8 Elite Gen 6 要到 2026 年秋天。高通把 CES 的舞台给了四条“非手机”产品线：**主流价位 AI PC（Snapdragon X2 Plus）**、**人形机器人（Dragonwing IQ10）**、**端侧视觉 IoT（Dragonwing Q-8750 / Q-7790）**，以及**车端中央计算与车载 Agent**。CMO Don McGuire 在 [CES 总述博客](https://www.qualcomm.com/news/onq/2026/01/qualcomm-at-ces-2026) 里把主线概括为“下一个 UI 是你的 Agent”：Agent 在可穿戴、手机和 PC 上看、听、替你行动，并且依赖设备端 AI 处理来保证私密与常驻。

这一个月的共同点可以用一句话概括：**80 TOPS 级 NPU 正在变成“标配”，竞争焦点从峰值 TOPS 转向内存带宽、功能安全和工具链。** 下面按产品线展开。需要说明的是，本窗口此前没有做过硬件雷达，各周归档里没有已收的高通条目，本节内容全部来自本次回填核实过的一手页面和媒体报道。

### PC：X2 Plus 把 80 TOPS 下放到主流价位

1 月 5 日发布的 [Snapdragon X2 Plus](https://www.qualcomm.com/news/releases/2026/01/empowering-professionals-and-aspiring-creators--snapdragon-x2-pl) 是 X2 家族的第三档，排在 2025 年 9 月发布的 X2 Elite / X2 Elite Extreme 之下。官方口径有三条：第三代 Oryon CPU 单核性能比上一代 X Plus 快最多 35%、功耗低 43%；集成 80 TOPS Hexagon NPU；OEM 整机 2026 年上半年开售。[官方产品页](https://www.qualcomm.com/laptops/products/snapdragon-x2-plus) 列出两颗 SKU：X2P-64-100（10 核，34 MB 缓存，GPU 1.70 GHz）和 X2P-42-100（6 核，GPU 0.91 GHz）。[CNX Software](https://www.cnx-software.com/?p=163123) 补充了内存规格：128-bit LPDDR5X-9523，带宽 152 GB/s，最高 128 GB，CPU 单核最高 4.04 GHz。[SiliconANGLE](https://siliconangle.com/2026/01/05/qualcomm-debuts-new-chips-robots-windows-laptops/) 称该芯片采用台积电 3nm 性能优化版，官方新闻稿没有写制程。

最值得关注的是 **NPU 没有降档**：两款 X2 Plus 和 X2 Elite 一样都是 80 TOPS。对端侧 Agent 开发者来说，这意味着 Copilot+ 本地功能和第三方 NPU 应用可以按同一个能力基线设计，不必为低价机型另做一套。不过要看清瓶颈：decode 阶段每生成一个 token 都要把权重读一遍，152 GB/s 的带宽才是生成速度的上限。**推算**：8B INT4 模型（约 4.5 GB）decode 理论上限约 34 tok/s，14B INT4 约 19 tok/s，实际一般只有上限的 50–70%。所以 X2 Plus 的“甜点区”是 3–8B 的稠密模型，或激活参数很小的 MoE。X2 Elite 高配公开带宽是 228 GB/s（检索摘要，来自高通产品页对比），两档差距主要在带宽而不在 NPU。

形态方面，1 月 6 日的 [OnQ 博客](https://www.qualcomm.com/news/onq/2026/01/accelerating-the-future-of-desktop-pcs-snapdragon-x-series) 宣布首款骁龙一体机 ASUS AiO VM441QA(QC)。这台机器用的是第一代 Snapdragon X（45 TOPS），不是 X2。博客同时称 X2 系列 NPU 最高 85 TOPS，X2 Elite 功耗比上一代低最多 20%。窗口内没有找到 X2 Plus 的第三方 NPU 实测。此前 X2 Elite Extreme 的 Geekbench AI 约 8.8 万分，那是 2025 年由高通控制测试条件得出的数字，只能当背景参考。

### 机器人与 IoT：高通想做“机器人的大脑”和“摄像头里的 11B 模型”

1 月 5 日的 [机器人全栈发布](https://www.qualcomm.com/news/releases/2026/01/qualcomm-introduces-a-full-suite-of-robotics-technologies-power) 是本月最有新意的一条。高通推出一套通用机器人架构，把异构边缘计算、混合关键性系统、MLOps 和“采集-训练-部署”的 AI 数据飞轮打包在一起，旗舰芯片是 **Dragonwing IQ10**。新闻稿本身没有写算力，[IQ10 产品页](https://www.qualcomm.com/internet-of-things/products/iq10-series) 给出的规格是：最高 700 TOPS（括号注明 **350 dense TOPS @INT8**）、18 核 Oryon CPU、20 路以上摄像头、最高 SIL-3 安全岛，供货支持到 2038 年。SiliconANGLE 的现场报道也写的是 350 dense TOPS，“是 IQ9 的 3 倍以上”，并提到 IQ9 可跑 13B LLM。**口径提醒**：700 是含稀疏的峰值，横向比较应该用 350。合作方中，Figure 与高通“共同定义下一代计算架构”，Kuka 在洽谈，Booster、VinMotion 已经用 Dragonwing 系列做人形机器人，但新闻稿没有确认 Figure 的量产机型会采用 IQ10。架构明确支持 VLA / VLM 端到端模型，这让高通成为 NVIDIA Jetson Thor 之外第二个大厂级的端侧 VLA 平台。内存带宽未披露，所以暂时无法估算大模型的实时性。

同日的 [IE-IoT 发布](https://www.qualcomm.com/news/releases/2026/01/qualcomm-s-ie_iot-expansion-is-complete--edge-ai-unleashed-for-d) 宣布完成对 Augentix 的收购。加上此前的 Arduino、Edge Impulse、Focus.AI、Foundries.io，高通 18 个月内完成了 5 笔收购，拼出“芯片 + 工具链 + 开发者入口”的 IoT 全栈。两颗新芯片中：**Dragonwing Q-8750** 有 77 TOPS（支持 INT4/8/16、FP16），官方称可在端侧运行最多 **11B 参数 LLM**，支持 12 路物理摄像头和 3 个 48MP ISP；**Q-7790** 有 24 TOPS，主打 AV1 解码和双 4K60 显示。**口径冲突**：SiliconANGLE 把两颗芯片的 TOPS 写反了，并称 Q-7790 为 3nm 八核，这里以官方新闻稿为准。同一新闻稿还提到 Dragonwing AI On-Prem Appliance 完整集成 Edge Impulse，可离线推理“最大 120B 参数”的模型。按硬规则，这只说明内存装得下：稿件没写是稠密模型还是 MoE，也没写精度和速度。

这两条合在一起，高通的端侧 AI 版图从“手机 + PC”扩成了“摄像头/无人机里的 7–11B 模型 → 机器人里的 VLA → 现场一体机里的 120B 兜底”的分层级联。1 月 16 日的 [初创生态博客](https://www.qualcomm.com/news/onq/2026/01/edge-ai-trends-driving-startup-success-2025) 也说明了这一点：2025 年高通扶持的 60 多家初创公司大量使用 RB3 Gen 2、IQ9 做 SLAM、视觉巡检和边缘 Agent。

### 汽车：中央计算量产，车端 Agent 有了名字

汽车是本月发布最密集的方向。[CES 车载汇总稿](https://www.qualcomm.com/news/releases/2026/01/qualcomm-drives-the-future-of-mobility-with-strong-snapdragon-di) 给出的关键数字如下：Snapdragon Cockpit/Ride Elite 旗舰中央计算平台新增理想、零跑、极氪、长城、蔚来、奇瑞的合作，定点累计 10 个项目；舱驾一体的 Ride Flex 已在 8 个全球量产项目落地；Ride 平台有 20 个定点，出货近 100 万颗 SoC；截至 2025 年 6 月，带 AI 的座舱平台装车超过 7500 万辆。高通同时发布了首款车规 5G RedCap 调制解调器 A10。

最具体的落地案例是 [零跑 D19](https://www.qualcomm.com/news/releases/2026/01/leapmotor-and-qualcomm-debuts-world-s-first-automotive-central-c)：它是全球首款搭载双 SA8797P（Snapdragon Elite）中央计算机的量产车，一个控制器统一座舱、L2 辅助驾驶、车身和网关。官方称这套系统可以**同时运行座舱全模态大模型和驾驶 VLA 多模态模型**，支持最多 8 块屏和 13 路摄像头，但没有披露总算力和模型规模。Tier1 方面，[ZF ProAI](https://www.qualcomm.com/news/releases/2026/01/zf-and-qualcomm-collaborate-to-deliver-scalable-adas-solution-po) 改用 Snapdragon Ride，支持把感知、融合、决策做成单一端到端模型，顶配多板整机超过 1,500 TOPS。这个数字是 ZF 整机口径，不是单颗芯片。[现代摩比斯](https://www.qualcomm.com/news/releases/2026/01/hyundai-mobis-and-qualcomm-sign-comprehensive-agreement-to-colla)（1/7）与高通签 MOU，以 Ride Flex 开拓印度等新兴市场；[大众集团](https://www.qualcomm.com/news/releases/2026/01/volkswagen-group-and-qualcomm-sign-letter-of-intent-to-power-nex)（1/8）签署意向书，从 2027 年起由高通为大众-Rivian 区域架构供应信息娱乐 SoC。1 月 2 日新款丰田 RAV4 也宣布采用新一代 Snapdragon 座舱平台。

软件与 Agent 层有两条值得端侧 AI 读者关注。一是与 Google 的 [扩大合作](https://www.qualcomm.com/news/releases/2026/01/qualcomm-expands-decade-long-collaboration-with-google-for-autom)：Gemini Enterprise for Automotive 采用**端侧 + 云端模型混合架构**；Snapdragon 座舱路线图从 Android 17 起与 AAOS 对齐；高通推出跑在 Google Cloud Axion C4A 裸金属实例上的 Snapdragon vSoC 虚拟平台，[1 月 9 日博客](https://www.qualcomm.com/news/onq/2026/01/snapdragon-vsoc-aaos-sdv-google-cloud) 补充了细节。二是 1 月 6 日提出的 [Snapdragon Chassis Agents](https://www.qualcomm.com/news/onq/2026/01/from-software-defined-to-ai-defined-vehicle-snapdragon-chassis-agents)：高通把“AI 定义汽车”落到一个车端 Agent 框架上，用 agentic 框架加车端推理来编排车辆功能。博客没有给出模型规模、工具接口或延迟数字，现阶段更像命名和路线宣示。

### 软件栈：AI Hub 两周一版，IQ9 真机上云

[AI Hub Workbench 发布记录](https://workbench.aihub.qualcomm.com/docs/hub/release_notes.html) 显示本月有两个版本。1 月 6 日版本把 QAIRT 升到 2.41.0，模型页开始展示 I/O 规格和量化参数，同时移除 nnapi 等旧 TFLite 委托选项。1 月 26 日版本把默认 QAIRT 升到 2.42.0，上线 **Dragonwing IQ9075-AA（100 TOPS，Qualcomm Linux）真机**，lite-mp 混合精度敏感度分析改为考虑模型全部输出。IQ9 真机上云与 IQ10 的发布是配套的：机器人和工业开发者现在可以在公共平台上量化并 profile VLM/VLA，拿到可复现的真机数据。窗口内没有找到 GenieX 或 QAIRT 大版本的单独公告。开发者博客方面，1 月 21 日的 [UE5 博客](https://www.qualcomm.com/developer/blog/2026/01/run-unreal-engine-5-content-30fps-snapdragon-mobile) 介绍了在 8 Elite Gen 5 上以 30 fps 运行 UE 5.4 的 Nanite/Lumen 演示，属于图形方向，与端侧 AI 关系不大。

### 手机与产业：没有新品，只有代工传闻

手机 SoC 这个月是空窗。唯一的高通相关硬件新闻是代工：[科技新报](https://technews.tw/2026/01/08/qualcomm-has-confirmed-that-it-is-in-advanced-talks-with-samsung-regarding-2nm-process-manufacturing/)（1/8）、[SamMobile](https://www.sammobile.com/news/samsung-may-make-qualcomms-next-2nm-high-end-chip/)（1/7）和 [GSMArena](https://www.gsmarena.com/qualcomm_could_return_to_samsung_for_its_2nm_chip_production-news-71053.php)（1/10）都报道，安蒙在 CES 期间表示已与三星洽谈 2nm 代工、设计已完成。这是高通首次公开表示考虑把先进制程应用处理器交给三星，但具体芯片型号未确认，属于**媒体转述 + 爆料**。背景方面，2025 年 10–11 月 [GSMArena 转述的爆料](https://www.gsmarena.com/new_and_intriguing_details_about_the_snapdragon_8_elite_gen_6_leak-news-70159.php) 称 8 Elite Gen 6 将分标准版和 Pro 版，都用台积电 2nm，只有 Pro 版支持 LPDDR6。若三星 2nm 成为第二供应源，2026–2027 年旗舰 SoC 的成本和供给都会受影响。另据检索摘要，Axios 1 月 19 日报道安蒙称 AI 眼镜年出货约 1000 万副、一两年内可到 1 亿副，这是 CEO 预测，未能打开原文核实。窗口之外，2 月 4 日高通发布 FY26 Q1 财报，指引因内存短缺下调。这件事落在下一窗口，这里只作提示。

### 对端侧 Agent 开发者意味着什么

把本月的发布放到开发者视角下，可以得到三条比较实用的结论。**PC 端**：80 TOPS NPU 已经覆盖 X2 全系，Windows 上的本地 Agent 可以默认让 NPU 常驻一个 3–8B 的 INT4 模型，负责意图识别、工具选择和隐私数据处理，把长上下文推理留给云端或更高带宽的机器。**汽车端**：“车端模型 + 云端 Gemini”的分工写进了高通与 Google 的联合路线图，零跑 D19 又证明一辆车里两颗旗舰 SoC 可以同时跑座舱大模型和驾驶 VLA。车载 Agent 的工程重点会落在端云切换策略和混合关键性隔离上，而不是单纯堆模型。**机器人/IoT 端**：IQ9 真机进入 AI Hub、IQ10 公布 350 dense TOPS、Q-8750 标称能跑 11B，说明高通在给 VLA 和视觉 Agent 准备一条从原型（Arduino、Edge Impulse）到量产（Dragonwing、安全岛）的完整路径。不过这几颗芯片的内存带宽、功耗和实测 tok/s 都还没公开，开发者现在做选型时，只能把官方 TOPS 和“可跑多少 B”当作上限参考，不能当作体验承诺。

### 小结：三个判断

第一，**NPU 算力已经过剩，带宽和内存成为分档依据**。X2 Plus 与 X2 Elite 的 NPU 同为 80 TOPS，差别在 152 GB/s 和 228 GB/s 的带宽。端侧 LLM 的实际体验将越来越由内存子系统决定，这与 2 月初财报提到的内存短缺是同一个问题。第二，**高通的端侧 AI 叙事正在从“手机上的模型”变成“分层级联的 Agent 硬件”**：可穿戴和摄像头跑小模型，PC 和车跑 8–14B 级模型与 VLA，机器人跑 350 dense TOPS 的 VLA，现场一体机兜底 120B。CES 的四条产品线正好对应这几层。第三，**功能安全和工具链是新的护城河**：IQ10 的 SIL-3 安全岛、车端混合关键性、AI Hub 真机测评和 Edge Impulse/Arduino 的开发者渠道，是 NVIDIA 和联发科在机器人与 IoT 方向较难短期复制的部分。待跟踪的问题包括：IQ10 的内存带宽与量产时间、Q-8750 跑 11B 模型的实际 tok/s、X2 Plus 整机的第三方 NPU 实测，以及三星 2nm 是否真的拿到高通订单。

## 2. Apple 与 Google：Gemini 打底、LiteRT 接班与 MLX 迭代

### 总览：Apple 外采大模型，Google 把端侧运行时做成“通用底座”

2026 年 1 月（01-01~01-29）Apple 与 Google 方向没有发布新芯片，CES 上 Google 也只在拉斯维加斯 Sphere 上做了 [Android XR 的品牌宣传](https://blog.google/technology/xr-ar/android-xr-sphere-ces-2026/)，没有新硬件。这个月的主线是**端侧 AI 的分工被重新划定**。1 月 12 日两家发布[联合声明](https://blog.google/company-news/inside-google/company-announcements/joint-statement-google-apple/)：Apple 下一代 Apple Foundation Models 将基于 Gemini 的模型和云技术，但 Apple Intelligence“继续运行在 Apple 设备和 Private Cloud Compute 上”。同月 Google 的端侧动作集中在软件栈：1 月 28 日 [LiteRT 正式接班 TFLite](https://developers.googleblog.com/litert-the-universal-framework-for-on-device-ai/)，同日确认 ML Kit 里的 [Gemini Nano v3 是 Gemma 3n 的质量优化版](https://android-developers.googleblog.com/2026/01/how-automated-prompt-optimization.html)；模型侧开放了面向手机的 [TranslateGemma 4B](https://blog.google/innovation-and-ai/technology/developers-tools/translategemma/) 和可离线运行的 [MedGemma 1.5 4B](https://research.google/blog/next-generation-medical-image-interpretation-with-medgemma-15-and-medical-speech-to-text-with-medasr/)。Apple 的一手发布只有两版 MLX，更多信息来自爆料：Siri 聊天机器人 Campos、1.2 万亿参数的 AFM v10、AI 胸针，以及月末官宣的 Q.ai 收购和财报会上的内存涨价警告。

本月可以归纳为三个判断：

1. **“大模型在云、个人上下文在端”成为 Apple 的明确路线。** 爆料中的 AFM v10 约 1.2 万亿参数，按 int4 估算权重约 600GB，只能跑在 PCC（推算）；端侧仍是 Apple 2025 技术报告里约 3B 参数、2-bit 量化感知训练的小模型。端侧芯片的任务变成屏幕理解、个人数据检索和动作执行。
2. **Google 在端侧的优势是运行时，不是芯片。** LiteRT 的 NPU 量产名单里只有联发科和高通，Google 自家 Tensor 没有出现；Gemini Nano v3 通过 AICore 跑在多家 SoC 上。Google 的端侧影响力主要来自“模型 + 运行时 + 分发”这一层，而不是 Tensor 本身。
3. **内存成为端侧 AI 的成本瓶颈。** Apple 1 月 29 日财报会上 Cook 说内存对上季度毛利影响很小，但本季度会更大，之后价格还在“大幅上涨”。端侧大模型最吃 DRAM，涨价会把厂商推向低比特量化和端云分工。

### Apple：模型外采，端侧守住隐私链路

**Gemini 联合声明（01-12，官方）。** 声明只有三段，但信息量很大：合作是多年期的；对象是“下一代 Apple Foundation Models”；新模型将驱动包括“今年推出的更个性化 Siri”在内的功能；运行环境仍是设备 + PCC。金额没有披露，[Bloomberg](https://www.bloomberg.com/news/articles/2026-01-12/google-confirms-multiyear-ai-deal-to-power-apple-models-siri) 与此前媒体报道的约每年 10 亿美元属于媒体口径。对端侧硬件来说，关键在于 Apple 把前沿模型能力交给外部，而把芯片、PCC 和隐私推理链路留在自己手里。

**两条 Gurman 爆料勾勒出端云边界（01-21、01-25，爆料）。** 1 月 21 日 [Bloomberg](https://www.bloomberg.com/news/articles/2026-01-21/ios-27-apple-to-revamp-siri-as-built-in-iphone-mac-chatbot-to-fend-off-openai) 称 Siri 将在 iOS 27 改造成内置聊天机器人 Campos，有语音和文字两种模式，能感知屏幕、代用户改设置；双方还在“讨论直接托管在 Google 服务器上”（[Thurrott 转述](https://www.thurrott.com/a-i/331929/apple-will-reportedly-transform-siri-into-a-chatbot-later-this-year)）。1 月 25 日的 [Power On](https://www.bloomberg.com/news/newsletters/2026-01-25/inside-apple-s-ai-shake-up-ai-safari-and-plans-for-new-siri-in-ios-26-4-ios-27-mktqy7xb) 称 iOS 26.4 的个性化 Siri 将在 2 月下旬展示；[9to5Mac](https://9to5mac.com/2026/01/25/apple-siri-gemini-partnership-set-to-launch-next-month-ios-26-4/) 转述该模型内部叫 AFM v10，约 1.2 万亿参数、跑在 PCC，对比 Apple 现有约 1500 亿参数的云端模型；iOS 27 将用 AFM v11。两条爆料合在一起看：iOS 26.4 版走 PCC，iOS 27 版可能上 Google 云，这与 1 月 12 日声明中“设备 + PCC”的说法存在张力。需要注意，这个时间表后来落空了：[2 月 17 日的 iOS 26.4 测试版没有新 Siri](https://www.macrumors.com/2026/02/17/ios-26-4-no-new-siri-features/)（窗口外后续）。

**可穿戴与无声交互（01-21 爆料、01-29 官宣）。** [TechCrunch 转述 The Information](https://techcrunch.com/2026/01/21/not-to-be-outdone-by-openai-apple-is-reportedly-developing-an-ai-wearable/)：Apple 在研发 AirTag 大小的 AI 胸针，带两颗摄像头、三个麦克风，可能 2027 年推出、首发约 2000 万台，项目仍处早期。1 月 29 日 Apple 确认[收购 Q.ai](https://engadget.com/big-tech/apple-acquires-qai-for-a-reported-2-billion-190017949.html)，该公司做低语识别、嘈杂环境音频增强和“面部皮肤微动作”默念识别；估值约 16 亿美元（路透社消息源）到近 20 亿美元（金融时报）。表态来自负责芯片的 Johny Srouji，创始人 Aviad Maizels 曾把 PrimeSense 卖给 Apple，相关技术后来用于 Face ID。胸针和 Q.ai 放在一起看，Apple 在为“无屏、常开、低功耗”的个人 AI 设备准备传感器和交互技术，这类设备的大模型推理只能交给 iPhone 或云端（推断）。

**MLX 两版：FP4/FP8 与 M5 神经加速器（01-13、01-27，官方）。** [MLX v0.30.3](https://github.com/ml-explore/mlx/releases/tag/v0.30.3) 让 Metal 支持 nvfp4/mxfp8。PR 作者在 M4 Max 上用 Qwen3 4B 实测：mxfp4 生成约 141 tok/s，mxfp8 约 88 tok/s，prefill 各格式都在约 1570~1620 tok/s。4-bit 与 8-bit 的生成速度比约 1.6，接近字节数之比，说明 decode 受带宽限制（推算）。[MLX v0.30.4](https://github.com/ml-explore/mlx/releases/tag/v0.30.4) 加入面向长上下文的向量融合 GQA 注意力，以及给 M5 GPU 神经加速器（NAX）用的 [Split-K GEMM](https://github.com/ml-explore/mlx/pull/3018)：在 M5 上处理大 K 矩阵乘，bf16 最高约 1.62 倍（开发者实测）。[mlx-lm](https://github.com/ml-explore/mlx-lm/releases/tag/v0.30.5) 同月加入多种新模型和激活量化算子。Apple 在 1 月没有官方 ML 研究博客文章，ML Research 网站上的条目都是论文页，例如 1 月挂出的[分层记忆预训练](https://machinelearning.apple.com/research/hierarchical-memories)：160M 模型外挂从 4.6B 记忆库取出的 18M 记忆块，效果可比 2 倍以上参数的模型。这项工作的 arXiv 首版在 2025 年 10 月，这里只作为背景。它对端侧的启发是：长尾知识可以放进按需取用的记忆，常驻 DRAM 的只是小模型。

**财报会的内存警告（01-29，官方 + 媒体）。** [新闻稿](https://www.apple.com/newsroom/2026/01/apple-reports-first-quarter-results/)显示营收 1438 亿美元（+16%），活跃设备超过 25 亿台。据[媒体整理](https://finance.yahoo.com/news/apple-tops-q1-earnings-estimates-on-record-breaking-iphone-sales-213019517.html)，电话会上第二季度毛利率指引为 48%~49%，已计入更大的内存影响，Cook 还说之后内存价格继续大幅上涨。这是本月端侧 AI 硬件最直接的成本信号。

### Google：运行时、系统模型与小模型三层推进

**LiteRT 成为通用端侧框架（01-28，官方）。** 新 GPU 引擎 ML Drift 一套代码覆盖 OpenCL、OpenGL、Metal、WebGPU，支持 Android、iOS、macOS、Windows、Linux 和 Web，平均比 TFLite GPU delegate 快 1.4 倍，异步 + 零拷贝最高约 2 倍。NPU 方面，官方称最高比 CPU 快 100 倍、比 GPU 快 10 倍，并点名联发科（视频示例为天玑 9500）和高通（视频示例为骁龙 8 Elite Gen 5）。LLM 只给了定性结论：Gemma 3 1B 在 Galaxy S25 Ultra 上 CPU/GPU 均快于 llama.cpp，NPU prefill 再比 GPU 快 3 倍，没有绝对 tok/s，也没有功耗数据。同日的 [LiteRT 2.1.2](https://github.com/google-ai-edge/LiteRT/releases/tag/v2.1.2) 在 Python 包中加入 Linux（WebGPU）和 Mac（Metal）桌面 GPU。NPU 的优势集中在算力受限的 prefill，这对长 prompt、需要读大量上下文的端侧智能体最有用；decode 仍受内存带宽限制（推断）。LiteRT-LM v0.9.0-alpha 在 1 月 30 日发布，已在窗口之外。

**Gemini Nano v3 与提示优化（01-28，官方）。** Android 开发者博客首次明确：ML Kit GenAI API 在支持设备上使用 nano-v3，它是“质量优化版的 Gemma 3n”。由于 AICore 是共享系统服务，很难按应用挂 LoRA，Google 改为在 Vertex AI 上用 Gemini Pro/Flash 做自动提示优化（APO），主题分类 +5%、意图分类 +8.0%、网页翻译 BLEU +8.57%。系统级共享端侧模型（Android AICore、Apple Foundation Models 框架）成为主流后，应用侧的定制会从改权重转向“云端辅助的提示与评测”。1 月 16 日的 [FunctionGemma 微调指南](https://developers.googleblog.com/a-guide-to-fine-tuning-functiongemma/)（270M）则是另一条路：给开发者自有的超小模型做工具调用微调，但文中没有给出准确率和端侧速度。

**面向设备的专用小模型（01-13、01-15，官方）。** TranslateGemma 分 4B/12B/27B 三档，官方分别对应手机与边缘设备、消费级笔记本、单张 H100。[技术报告](https://arxiv.org/abs/2601.09012)给出 WMT24++ MetricX：4B 从 6.97 降到 5.32，12B 的 3.60 已优于 Gemma 3 27B 基线的 4.04。MedGemma 1.5 4B 官方称“小到可以离线运行”，MRI 分类从 51% 提到 65%；MedASR 在胸片口述上的词错率为 5.2%，Whisper large-v3 为 12.5%。按 int4 估算，4B 模型权重约 2GB；以 LPDDR5X-9600 64-bit 约 76.8GB/s 的带宽计，decode 理论上限约 38 tok/s（推算，官方未给端侧速度）。Google Research 1 月 22 日的[意图抽取博客](https://research.google/blog/small-models-big-results-achieving-superior-intent-extraction-through-decomposition/)（论文为 EMNLP 2025）也指向同一方向：把手机界面轨迹拆成逐屏摘要，再让小模型抽取用户意图，目标是“全部在设备上处理”。

**Tensor 与 XR：本月没有一手进展。** 窗口内没有 Tensor 新芯片的官方信息。Pixel 10a 沿用 Tensor G4 的说法最早出自 2025 年 9 月的爆料，不属于本月新闻；CES 上 Android XR 只有 Sphere 的品牌宣传，XREAL 的 Project Aura 只是入选 CES 2026 创新奖（Honoree），没有公布新规格。

### 能跑多大模型：本月数字核对

本月两家公布的数字口径差别很大，放在一起需要分开读：

- **官方实测、有绝对值的只有 MLX。** Qwen3 4B 在 M4 Max 上 4-bit 生成约 136~141 tok/s、8-bit 约 88 tok/s，来自 [PR #2946](https://github.com/ml-explore/mlx/pull/2946) 中开发者的测试，作者注明还没有做性能调优。这组数字最有价值的地方是两档精度之间的比例：权重字节数减半，生成速度提高约 1.6 倍，而 prefill 几乎不变。这再次说明在 Apple Silicon 上，decode 由内存带宽决定，prefill 由算力决定。
- **LiteRT 只给了相对倍数。** “GPU 比 TFLite 快 1.4 倍”“NPU 比 CPU 快 100 倍、比 GPU 快 10 倍”“NPU prefill 比 GPU 快 3 倍”都是官方口径，而且 100 倍、10 倍来自联发科和高通专题中的最佳个例，不是 LLM 的平均水平。Gemma 3 1B 是本文唯一点名的 LLM 实测模型，但只给了柱状对比，没有 tok/s。
- **模型发布只给“定位”，不给设备速度。** TranslateGemma 4B 写的是“为移动和边缘部署优化”，MedGemma 1.5 写的是“小到可以离线运行”，都没有量化版本、内存占用和 tok/s。本节对 4B 级模型的估算（int4 约 2GB 权重、手机 decode 理论上限约 38 tok/s）以及对 12B 模型的估算（int4 约 6GB、约 100GB/s 带宽的笔记本上 decode 上限约 16 tok/s）都属于推算，实际值通常只有理论上限的一半到七成。
- **Apple 的模型规模几乎全部来自爆料。** AFM v10 约 1.2 万亿参数、现有云端模型约 1500 亿参数，都出自 Gurman 的报道；Apple 官方只公开过 2025 年端侧模型约 3B、2-bit 量化感知训练这一档。即便 Apple 未来把 Gemini 蒸馏成端侧版本，按 iPhone 15 Pro 起的 8GB 内存门槛，留给模型的空间仍然只够 3B 左右的低比特模型（推算）。
- **Gemini Nano v3 只公开了血缘。** 官方只说它是“质量优化版的 Gemma 3n”，没有说明对应 E2B 还是 E4B，也没有给出量化精度。在 AICore 共享服务的架构下，所有应用共用同一份权重，这也是 Google 用提示优化代替 LoRA 的原因。

### 小结：端侧芯片的角色变了

1 月份两家都没有发布新芯片，但端侧 AI 的分工在这个月变得清楚：**前沿大模型放在云端或私有云**（AFM v10 跑在 PCC，Campos 可能托管在 Google 云），**端侧负责小模型和个人上下文**（约 3B 的 AFM 端侧模型、Gemma 3n 衍生的 Gemini Nano v3、4B 级专用模型），**运行时负责屏蔽硬件差异**（LiteRT 统一 CPU/GPU/NPU，MLX 跟进 FP4/FP8 和 M5 NAX）。对芯片厂商来说，竞争点从“能装下多大的模型”转向 prefill 算力、长上下文注意力的带宽效率，以及常开、低功耗的传感与交互（胸针、Q.ai）。内存涨价会强化这个趋势。

需要继续跟踪的存疑点：AFM v10 的 1.2 万亿参数和每年约 10 亿美元的金额都是爆料口径；Campos 托管在 Google 服务器的方案当时仍在谈判，与“设备 + PCC”的官方表述存在冲突；LiteRT 的 100 倍、10 倍是最佳个例，LLM 场景缺少绝对速度和能耗；Gemini Nano v3 的参数规模至今未披露。M5 Pro/Max MacBook Pro 和 iOS 26.4 Siri 的结果都在 2 月以后。

## 3. 其他 SoC 与 PC：AMD、英特尔、NVIDIA 同周换代，内存成变量

### 总览：CES定调，芯片在PC端，变量在内存

1月的“其他SoC、PC与产业”方向有两条主线。第一条是CES 2026（1月5日前后）：AMD、英特尔、NVIDIA同一天发布新一代AI PC、嵌入式和桌面AI平台。第二条是产业：台积电、三星、SK海力士、英特尔的季度财报，以及TrendForce的一组预测，共同指向“AI服务器吃掉内存和先进制程，端侧设备付更高的钱”。移动SoC相对安静，只有联发科1月15日发布的[天玑9500s与天玑8500](https://www.mediatek.com/press-room/mediatek-unveils-dimensity-9500s-and-dimensity-8500-to-propel-performance-gaming-and-efficiency-in-flagship-and-premium-smartphones)，以及关于小米玄戒O2的爆料。华为麒麟、紫光展锐、瑞芯微在本月检索中没有查到新品发布。

本月的三个判断：

1. **x86笔记本的NPU基线到了50 TOPS，但本地大模型的上限仍由内存带宽决定。** 锐龙AI 400的NPU为50–60 TOPS，酷睿Ultra 3的NPU为46–50 TOPS。两者主流配置都是128-bit LPDDR5X，带宽约136–154GB/s（推算），8B模型4-bit的decode上限约30 tok/s。
2. **“能跑多大模型”的竞争转到128GB统一内存的桌面/迷你主机。** AMD锐龙AI Halo称可跑200B参数，NVIDIA DGX Spark称100B、DGX Station称1T。三者都是容量口径；DGX Spark和Strix Halo级平台的带宽都只有约256–273GB/s，真正可用的是激活参数小的MoE模型。
3. **内存涨价是全年端侧AI最大的外部约束。** TrendForce在[1月5日](https://www.trendforce.com/presscenter/news/20260105-12860.html)预计1Q26常规DRAM环比上涨55–60%（2月又上调到90–95%）。同月它把2026年手机产量预测下调到-7%，并预计1Q26笔记本出货环比-14.8%。

### PC芯片：AMD、英特尔同日刷新

**AMD（官方口径）。** [CES发布稿](https://ir.amd.com/news-events/press-releases/detail/1270/amd-expands-ai-leadership-across-client-graphics-and-software-with-new-ryzen-ryzen-ai-400-series-and-rocm-announcements-at-ces-2026)给出锐龙AI 400/PRO 400共13个SKU。架构仍是Zen 5、XDNA 2 NPU和RDNA 3.5，最高12核。NPU分三档：HX 475为60 TOPS，HX 470为55 TOPS，其余全部50 TOPS；cTDP 15–54W。笔记本1Q26出货，台式机2Q26。

同场新增的锐龙AI Max+ 392（12核）和388（8核）都保留完整的40 CU Radeon 8060S，NPU为50 TOPS，cTDP 45–120W。面向开发者的锐龙AI Halo迷你主机最高128GB统一内存，脚注写明“200B参数需要128GB”，计划2Q26上市，价格未披露。ROCm 7.2同时覆盖Windows、Linux和锐龙AI 400，并集成进ComfyUI。

这一代是同架构刷新，增量在于NPU峰值从50提到60 TOPS，以及把“大GPU+大统一内存”下放到8核的388。

**英特尔（官方口径）。** [酷睿Ultra第3代（Panther Lake）](https://newsroom.intel.com/client-computing/ces-2026-intel-core-ultra-series-3-debut-first-built-on-intel-18a)是首款18A客户端芯片，但只有计算芯粒（CPU+NPU）用18A。按[StorageReview整理的规格表](https://www.storagereview.com/news/intel-core-ultra-series-3-arrives-at-ces-2026-as-intels-first-18a-based-client-platform)，14个SKU的NPU为46–50 TOPS。只有带“X”的X9/X7型号有12个Xe3 GPU核（约122 TOPS），平台合计最高180 TOPS。12 Xe核型号只支持LPDDR5X-9600、最大96GB。

产品1月6日开订、1月27日上市；边缘与嵌入式版本取得扩展温度和24×7认证，2Q26出货。英特尔称边缘场景LLM性能最高是竞品的1.9倍、VLA吞吐最高4.5倍，但未公布对比对象（[媒体报道](https://interestingengineering.com/ces-2026/intel-core-ultra-series-3-ai-pc-ces-2026)）。

两家对比：AI主力都在GPU而不是NPU。NPU适合常驻小模型和低功耗任务，本地大模型跑在GPU上，瓶颈是带宽。按X9 388H的154GB/s推算，96GB内存装得下4-bit的70B稠密模型，但decode上限只有约4 tok/s。本月窗口内没有查到Panther Lake或锐龙AI 400的第三方LLM实测；Phoronix的llama.cpp测试在2月初才发布。

**供给面。** 英特尔[1月22日财报](https://www.intc.com/news-events/press-releases/detail/1759/intel-reports-fourth-quarter-and-full-year-2025-financial)称18A已在亚利桑那和俄勒冈大批量生产，但CFO明确表示“一季度可用供给是最低点”。财报风险提示还写到，若拿不到外部客户，可能暂停14A。TrendForce[1月26日报告](https://www.trendforce.com/presscenter/news/20260126-12895.html)称英特尔低端CPU涨价、缺货持续到3月后，与财报口径一致。

### NVIDIA：桌面“个人超算”与机器人模组

NVIDIA这次没有发布新的PC芯片（N1X仍未发布），增量全在软件和Jetson。

- **DGX Spark/Station（官方口径）。** [NVIDIA博客](https://blogs.nvidia.com/blog/dgx-spark-and-station-open-source-frontier-models)称DGX Spark可本地跑100B参数模型。GB300的DGX Station有775GB相干内存，可跑1T参数模型，2026年春季由7家OEM上市。[开发者博客](https://developer.nvidia.com/blog/new-software-and-model-optimizations-supercharge-nvidia-dgx-spark)给出：两台Spark用200Gbps互联组成256GB，Qwen-235B用NVFP4加投机解码比FP8最高快2.6倍；llama.cpp在MoE上平均快35%。GB10由联发科与NVIDIA合作设计，获CES 2026创新奖（[联发科CES回顾](https://www.mediatek.com/tek-talk-blogs/ces-2026-recap)）。
- **RTX PC软件栈（官方口径）。** [开发者博客](https://developer.nvidia.com/blog/open-source-ai-tool-upgrades-speed-up-llm-and-diffusion-models-on-nvidia-rtx-pcs)称，过去4个月MoE模型的token生成吞吐在llama.cpp上提升35%、Ollama提升30%。改动包括GPU端采样和QKV并发CUDA流。ComfyUI上NVFP4平均提速3倍、省显存60%。同时推出Nemotron 3 Nano（总参32B、激活3.6B、1M上下文）。
- **Jetson T4000（官方口径）。** [T4000](https://developer.nvidia.com/blog/accelerate-ai-inference-for-edge-and-robotics-with-nvidia-jetson-t4000-and-nvidia-jetpack-7-1)规格为1,536核Blackwell、64GB、273GB/s、40–70W，FP4稀疏1,200 TFLOPS。官方表中Qwen3-30B-A3B为218 tok/s、Qwen3 32B为68 tok/s。按273GB/s推算，32B稠密模型4-bit的单流上限只有约15–17 tok/s，所以68 tok/s应是并发吞吐，博客没有写并发数。JetPack 7.1新增开源的TensorRT Edge-LLM C++ SDK。

### 嵌入式与IP：物理AI成为独立赛道

AMD同日发布[锐龙AI嵌入式P100/X100](https://ir.amd.com/news-events/press-releases/detail/1271/amd-introduces-ryzen-ai-embedded-processor-portfolio-powering-ai-driven-immersive-experiences-in-automotive-industrial-and-physical-ai)。首发6个4–6核SKU，NPU 30/50 TOPS，支持-40~105°C、AEC-Q100和最长10年供货。它用Xen虚拟化把HMI、实时控制和Android/Windows放在同一颗芯片上，目标是座舱和人形机器人。4–6核已送样，量产在第二季度；X100（最多16核）上半年采样，TOPS未公布。

Arm在CES期间从Edge部门拆出物理AI事业部，合并汽车与机器人，由Drew Henry负责（[SiliconANGLE援引路透](https://siliconangle.com/2026/01/07/chip-designer-arm-targets-robotics-new-physical-ai-business/)）。Arm的[CES回顾](https://newsroom.arm.com/blog/arm-ces-2026-takeaways)把车、机器人、PC、眼镜的共同需求概括为“AI要在本地运行”。

至此，AMD、英特尔、NVIDIA、Arm四家在同一周都把机器人和车载推理列为独立产品线。端侧AI的“第三终端”（手机、PC之后）开始有专门的芯片和IP。

### 移动SoC：联发科下放，国产自研只有爆料

- **联发科（官方口径）。** 天玑9500s为3nm，1×X925 3.73GHz+3×X4+4×A720，配Immortalis-G925。这套CPU组合与天玑9400+相同（推算），是把上代旗舰复用为次旗舰。天玑8500为4nm、8×A725全大核，Mali-G720性能+25%、功耗-20%，第8代NPU，支持主流LLM/MLLM和图像生成模型，内存LPDDR5X-9600。两款都没有公布TOPS和模型速度。推算：64-bit LPDDR5X-9600约77GB/s，3B模型4-bit的decode上限约45 tok/s。
- **小米（爆料，低可信度）。** [IT之家转财联社](https://www.ithome.com/0/914/432.htm)称，玄戒O2或继续用台积电N3P而非2nm，并推广到平板、汽车和PC，平板先行。消息来源未具名，小米未确认。
- **三星。** Exynos 2600于2025年12月发布（窗口外），本月只在[财报](https://news.samsungsemiconductor.com/global/samsung-electronics-announces-fourth-quarter-and-fy-2025-results/)中间接出现：代工“第一代2nm产品量产”，System LSI把“良率稳定”列为2026年目标。Galaxy S26将在1Q26主打智能体AI（2月发布，窗口外）。
- **华为、紫光展锐、瑞芯微。** 本月检索未发现新SoC发布：麒麟9030的TechInsights工艺分析在3月，展锐N9系列在5月，瑞芯微RK182X的模型适配进展在7–9月，均为窗口外。

### 代工与内存：AI服务器挤压端侧

- **台积电（官方口径）。** [4Q25营收](https://pr.tsmc.com/english/news/3281)337.3亿美元，毛利率62.3%；3nm占晶圆营收28%，7nm及以下合计77%。2026年资本开支520–560亿美元。媒体整理的法说会信息显示，智能手机占营收32%，HPC占55%；N2于4Q25量产，2026年将拉低毛利2–3个百分点（[Futurum](https://futurumgroup.com/insights/tsmc-q4-fy-2025-results-and-fy-2026-outlook-signal-ai-led-growth)）。
- **三星与SK海力士（官方口径）。** 三星4Q25营业利润20.1万亿韩元，其中DS部门16.4万亿，HBM4本季度出货。[SK海力士](https://news.skhynix.com/en/sk-hynix-announces-fy25-financial-results/)4Q25营业利润19.17万亿韩元，营业利润率58%；全年47.2万亿，超过三星全公司的43.6万亿。两家的发布稿都没有提移动LPDDR，扩产重点全部是HBM、SOCAMM2和服务器DRAM。
- **TrendForce（研究机构口径）。** 1月5日：1Q26常规DRAM环比+55–60%，LPDDR4X/5X持续供不应求。[1月15日](https://www.trendforce.com/presscenter/news/20260115-12880.html)：2026年手机产量从-2%下调到-7%。1月26日：笔记本1Q26环比-14.8%、全年-9.4%，笔记本DRAM环比涨80%以上。这些数字在2月被继续上调或下调，说明1月的预测普遍低估了涨价速度。

### 小结与观察清单

1月的硬件变化主要在PC和产业两端。PC侧，50 TOPS NPU成为x86全线标配，128GB统一内存的桌面机把“本地跑100B以上模型”变成可买到的产品，但带宽只有约150–270GB/s，决定了本地智能体实际用的是3B–8B稠密模型或激活参数5B以下的MoE。产业侧，先进制程和内存同时向AI服务器倾斜，手机和笔记本出货预测在一个月内连续下调，端侧AI的内存配置成为最大变量。

下月观察：

1. Galaxy S26（Exynos 2600/骁龙）的内存配置和端侧模型规模；
2. Panther Lake与锐龙AI 400的第三方LLM实测（tok/s、J/token）；
3. TrendForce对1Q26内存涨幅的修正，以及手机厂商是否降内存配置；
4. 锐龙AI Halo与DGX Station的定价；
5. 小米玄戒O2与NVIDIA N1X的正式消息。

## 4. 低功耗、存内计算与内存：亚阈值 NPU、DX-M2 路线图与 DRAM 涨价

### 总览：1 月是 CES 月，算力往下沉，内存往上涨

1 月（01-01~01-29）低功耗、存内计算与内存方向的信息几乎都集中在 CES 2026（1 月 6~9 日）那一周。这个窗口此前没有做过硬件雷达，各周的 `hardware.items` 都是空的，所以本节完全基于本次回填的 11 条新条目，加上少量检索到的背景材料。全月可以归纳为三条主线：

1. **常开芯片开始“带 NPU 出厂”**：Ambiq Atomiq 把 Ethos-U85 放进亚阈值平台，算力超过 200 GOPS；Nordic 第一颗带 Axon NPU 的蓝牙 SoC nRF54LM20B 开始送样；Rokid 的 AI 眼镜用“NXP RT600 常开 + 高通 AR1 按需唤醒”的双芯分工。
2. **边缘加速器开始拿“能跑多大 LLM”做卖点**：DEEPX 宣称 DX-M2 能在 5W 内跑最高 100B 参数的模型，ASUS 推出基于 Hailo-10H 的 U 盘式加速器，安霸 CV7 让安防相机芯片并行跑 VLM。但几家给出的内存带宽都在 17~154GB/s 这一档，真正的上限是内存，不是 TOPS。
3. **内存成为端侧 AI 最贵的部件**：TrendForce 预测 1Q26 DRAM 合约价环比上涨 55~60%（2 月又上修到 90~95%），韩媒爆料苹果 LPDDR 一季度涨 80%~100%，美光花 18 亿美元买现成洁净室，但新增产出要等到 2027 年下半年。

存内计算（CIM/PIM）是本月最冷清的子方向：国内外都没有新的量产产品发布，只有 SK 海力士在 CES 展台展示了几个原型。

### 一、常开 AI 与可穿戴：NPU 进入 MCU 和蓝牙芯片

**Ambiq Atomiq。** 1 月 6 日 [Ambiq 发布 Atomiq](https://ambiq.com/news/ambiq-unveils-atomiq-the-worlds-first-ultra-low-power-npu-soc-built-on-spot)，称这是第一颗基于 SPOT 亚阈值/近阈值平台的 NPU SoC。芯片集成 Arm Ethos-U85，官方口径端侧 AI 性能超过 200 GOPS，支持稀疏和权重即时解压，面向智能摄像头、AR 眼镜与可穿戴、工业边缘。发布稿没有给工艺、功耗、SRAM 容量和上市时间，只说 12nm SPOT 平台的细节要到 3 月 Embedded World 再公布。同稿还提到 Ambiq 累计供货超过 2.8 亿台设备，Bravechip 基于 Apollo330B Plus 的智能戒指方案能降本最多 85%（合作方口径）。按 200 GOPS 这个档位推算，它适合多语种语音识别、关键词唤醒和轻量视觉模型，不适合跑十亿参数级的语言模型。

**Nordic nRF54LM20B。** 同一天 [Nordic 发布 nRF54LM20B](https://www.nordicsemi.com/Nordic-news/2026/01/nRF54L-Series-SoC-with-NPU-and-Nordic-Edge-AI-Lab-make-on-device-intelligence-easily-accessible)。这是全球最大的低功耗蓝牙芯片供应商第一次在量产系列里集成 NPU（Axon，来自 2023 年收购的 Atlazo）。官方称它在关键词识别、声音分类和图像检测上比竞品快最多 7 倍、能效高最多 8 倍，但没有说明对比对象。芯片是 128MHz Cortex-M33 加 RISC-V 协处理器，配 2MB NVM 和 512KB RAM。配套的 Nordic Edge AI Lab 生成的 Neuton 模型通常小于 5KB。这个内存规模决定了它的定位是“传感器旁边的分类器”：耳机、戒指、手表外设可以在无线芯片上本地完成手势、唤醒和健康异常检测，让主 SoC 更多时间休眠。芯片已向部分客户送样，官方预计 Q2 初广泛开放开发。

**AI 眼镜的双芯分工。** 1 月 7 日 [Rokid 发布无屏眼镜 Rokid Ai Glasses Style](https://www.aap.com.au/aapreleases/cision20260106ae56965)：38.5 克，NXP RT600 负责常开低功耗任务，高通 AR1 负责 AI 和影像，官方称典型使用最长 12 小时、待机超过 24 小时，1 月 19 日全球上市，售价 299 美元起。大模型对话（ChatGPT、DeepSeek、千问）和 89 种语言翻译都走云端，眼镜本体不跑 LLM。同场的 Infinix AI 眼镜也采用 6nm 主处理器加独立影像芯片的双芯方案（媒体报道）。

把这三条放在一起看：眼镜和可穿戴的端侧 AI 不是在比谁能跑更大的模型，而是在比“常开感知”每小时耗多少电。Ambiq 和 Nordic 把常开芯片的 AI 能力抬了一档，眼镜厂商则用双芯架构把高功耗应用处理器的工作时间压到最短。目前三家都没有公布 µW 或 µJ/inference 这类可比数字，下一步要看量产后的实测。

### 二、边缘加速器：从 TOPS 转向“LLM 参数量”，但带宽说了算

**DEEPX DX-M2。** 1 月 6 日 [DEEPX 在 CES 媒体会上公布 DX-M2 路线图](https://deepx.ai/ces-2026-media-briefing-deepx-unveils-physical-ai-vision-roadmap/)：第二代处理器目标是在 5W 内推理 20B~100B 参数的 LLM（含 MoE）。官方稿没有给 TOPS 和工艺；[EE Times Japan 的 CES 现场报道](https://eetimes.itmedia.co.jp/ee/articles/2601/23/news067.html)补充了三星 2nm GAA、4 个 NPU 核、80 TOPS、LPDDR5X 153.6GB/s、20~30 tok/s 和 2026 年内量产（媒体口径）。按带宽推算：稠密 100B 模型 INT4 每 token 要读约 50GB，decode 上限只有约 3 tok/s；只有激活参数约 5B 的 MoE（INT4 约 2.5GB/token）才可能到 60 tok/s 级别。另外，100B INT4 权重需要约 50GB 内存，DX-M2 的内存容量没有公布。所以“100B”应理解为路线图目标，20~30 tok/s 也没有说明对应哪个模型。第一代 DX-M1（25 TOPS、1~5W）已在 50 多个项目部署，CES 上演示的 ResNet50 达到 958 fps。

**Hailo 与 ASUS UGen300。** [Hailo 的 CES 稿](https://hailo.ai/company-overview/newsroom/news/hailo-accelerates-edge-ai-adoption-across-consumer-and-commercial-markets-demonstrated-live-at-ces-2026/)没有发新芯片，重点是展示 Hailo-8、Hailo-10H 和 Hailo-15 的落地。其中 ASUS 当天发布的 UGen300 是第一款基于 Hailo-10H 的 USB 边缘 AI 加速器。[ASUS 规格页](https://www.asus.com/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/techspec/)写明 40 TOPS（INT4）/20 TOPS（INT8）、8GB LPDDR4 4266MT/s、典型功耗 2.5W。8GB 装得下 INT4 的 7B 模型，但 LPDDR4 位宽没有公布；如果按 32 位估算，带宽约 17GB/s，1.5B 模型 decode 上限约 20 tok/s，7B 模型约 4 tok/s（推算）。它的意义在于形态：没有大 NPU 的旧笔记本和工控机，插上一个 U 盘大小的外设就能离线跑小模型。

**安霸 CV7。** 1 月 5 日 [安霸发布 CV7](https://www.edge-ai-vision.com/2026/01/ambarella-launches-powerful-edge-ai-8k-vision-soc-with-industry-leading-ai-and-multi-sensor-perception-performance/)，这是它第一颗三星 4nm 芯片。官方称 AI 性能是 CV5 的 2.5 倍以上，功耗低 20%，可以同时运行 CNN、Transformer 和 VLM；DRAM 接口拓宽到 64 位，但没有给出带宽绝对值。安防和无人机芯片开始把 VLM 当标配，同时 8K 编解码和 AI 共用一组 DRAM，模型实际能用的带宽会低于理论值。

**软件侧。** 恩智浦在 CES 发布了 [eIQ Agentic AI Framework](https://convergedigest.com/nxp-unveils-eiq-agentic-ai-framework/)（媒体转述），在 i.MX 8/9 和 Ara 独立 NPU 上编排“感知—推理—控制”多步工作流，对齐 A2A 和 MCP 协议，并把提示注入防护和硬件信任根放进同一套方案。这是嵌入式芯片厂商第一次把“智能体运行时”作为工具链发布，没有给性能数字。

**横向对比（官方口径为主，带宽和 decode 上限为推算）：**

| 芯片/产品 | 定位 | 算力 | 内存 | 功耗 | 能跑多大模型 |
|---|---|---|---|---|---|
| Ambiq Atomiq | 亚阈值常开 SoC | >200 GOPS | 未披露 | 未披露 | 语音唤醒、多语种 ASR、轻量视觉 |
| Nordic nRF54LM20B | 蓝牙 SoC + NPU | 未披露 | 512KB RAM / 2MB NVM | 电池级 | KB 级分类模型（Neuton <5KB） |
| ASUS UGen300（Hailo-10H） | USB 加速器 | 40 TOPS INT4 | 8GB LPDDR4 | 2.5W 典型 | 1.5B 约 20 tok/s，7B 约 4 tok/s（推算，假设 32 位） |
| DEEPX DX-M2 | M.2/模组加速器 | 80 TOPS（媒体） | LPDDR5X 153.6GB/s（媒体） | <5W | 低激活 MoE 可达数十 tok/s，稠密 100B 约 3 tok/s（推算） |
| 安霸 CV7 | 视觉 SoC | CV5 的 2.5 倍以上 | 64 位 DRAM | 比上代低 20% | 可并行跑 VLM，规模未披露 |

这张表说明，同样叫“端侧 AI 芯片”，能力跨度有五六个数量级。从 KB 级分类器到数十亿参数的语言模型，中间的分界线不是 TOPS，而是片上 SRAM 和片外 DRAM 的容量与带宽。厂商宣传里常把“能装下”说成“能跑”，例如 DEEPX 的 100B 和 UGen300 的 8GB，读者应该先看内存再看算力。

### 三、内存：端侧 AI 最贵、也最缺的部件

**LPDDR6 仍在展示阶段。** [SK 海力士 CES 展台](https://news.skhynix.com/sk-hynix-showcases-next-generation-ai-memory-innovations-at-ces-2026/)把面向端侧 AI 的 LPDDR6 和 16 层 48GB HBM4、服务器用 SOCAMM2 放在一起展示，LPDDR6 只说速度和能效“显著提升”，没有数字。三星 LPDDR6（12nm、10.7Gbps、能效比 LPDDR5X 高约 21%）的规格在 2025 年 11 月就已公布，CES 上只是展示，本月没有新的数据。

**价格在失控。** 1 月 5 日 [TrendForce 预测](https://www.trendforce.com/presscenter/news/20260105-12860.html) 1Q26 常规 DRAM 合约价环比上涨 55~60%，NAND 上涨 33~38%，原因是原厂把先进制程和新产能转向服务器和 HBM。移动 DRAM 供应紧张、分配不均，eMMC/UFS 虽然需求弱，但因为减产仍然供不应求。1 月 22 日 TrendForce 又预测 [2026 年存储产值 5516 亿美元、2027 年 8427 亿美元](https://www.trendforce.com/presscenter/news/20260122-12893.html)。1 月 27 日，[韩媒爆料](https://www.trendforce.com/news/2026/01/27/news-samsung-may-raise-iphone-lpddr-prices-by-over-80-qoq-sk-hynix-reportedly-near-100-increase/)三星向苹果提出一季度 LPDDR 涨价 80% 以上、SK 海力士要价接近 100%，而且苹果这次只能签半年合同（爆料，未证实）。事后看，1 月的预测明显偏保守：TrendForce 2 月把 DRAM 涨幅上修到 90~95%，并预计 LPDDR4X/LPDDR5X 环比约涨 90%，与爆料区间吻合。

**扩产远水难救近火。** 1 月 17 日 [美光宣布以 18 亿美元收购力积电铜锣 P5 厂](https://micron.gcs-web.com/node/49981)，拿到 30 万平方英尺现成的 300mm 洁净室，但有意义的 DRAM 产出要到 2027 年下半年。同月美光还在纽约州巨型晶圆厂动工、在新加坡新建晶圆厂（媒体转述）。新增产能会优先给 HBM 和服务器（推断），手机 LPDDR 的缓解会更晚。

**对端侧 AI 的直接影响。** 端侧大模型最依赖的是内存容量：一个 INT4 的 3B 模型常驻就要约 1.5GB，7B 模型约 3.5~4GB，再加上 KV 缓存和系统本身的占用，旗舰机 12~16GB 内存才刚够用。TrendForce 在 1 月稿里已经提到，部分入门和中端笔记本为了压 BOM 开始降配。如果手机厂商也在中端机上停在 8GB，端侧 AI 功能会进一步向旗舰集中。对模型和系统侧来说，这会推高三类技术的价值：更低比特的量化、MoE 与按需加载（只把激活专家留在内存里），以及把权重放在 UFS 上流式读取的方案。这些方案本身又依赖 UFS 和 LPDDR 带宽，而本月这两类产品都没有新的量产数据。

### 四、存内计算：1 月无新品

本月没有检索到知存、苹芯、后摩、九天睿芯，以及 EnCharge、Mythic、Sagence 发布新的存算一体产品。九天睿芯在聚合平台上有一条 1 月 B+ 轮融资记录，但没有找到一手公告，不作为条目。产业侧唯一的展示是 SK 海力士在 CES 的 AI 系统演示区：基于 GDDR6-AiM 的 LLM 加速卡原型 AiMX、在 DRAM 单元内做简单运算的 CuD、把计算放进 CXL 内存的 CMM-Ax，都没有性能数字，也都不是手机形态。学术侧的存算论文集中在 2 月的 ISSCC 2026，不在本窗口内。

### 小结：端侧 AI 的瓶颈从算力转到了内存

1 月的硬件信号很一致：算力在往更小的芯片里下沉（200 GOPS 的亚阈值 MCU、带 NPU 的蓝牙 SoC、2.5W 的 USB 加速器），但每一家能跑多大模型，最后都由内存决定。MCU 受 512KB 级 SRAM 限制，加速器受 17~154GB/s 带宽和 8GB 级容量限制，手机则要面对 LPDDR 价格一个季度可能接近翻倍的现实。对端侧智能体来说，这意味着两件事。第一，短期内“常开小模型在本地、重推理在手机或云端”的分层架构不会改变，Rokid 的双芯眼镜和恩智浦的智能体调度框架都是这种思路。第二，2026 年真正能扩大端侧模型规模的，是 LPDDR6 量产、MoE 低激活模型和 PIM 落地，而本月这三件事都还停在展示或路线图阶段。需要继续跟踪的是：Ambiq 12nm SPOT 和 Nordic nRF54LM20B 的功耗实测（3 月 Embedded World）、DX-M2 的内存容量与量产时间，以及 LPDDR6 首发机型。

## 5. 顶会论文：ASP-DAC 2026 的 ROM 固化与三值查表

**判断：** 1 月是顶会的淡季。窗口（1/1–1/29）内真正召开、而且与端侧芯片对题的体系结构/设计自动化会议只有一个：1 月 19–22 日在香港举行的 [ASP-DAC 2026](https://www.aspdac.com/aspdac2026/)。HPCA、ISSCC 都要到 2 月才开。但 ASP-DAC 这一届的 LLM 硬件密度很高：一个专门的“近存/存内加速 LLM”场次（4B）、一个“超低精度与量化”场次（9F），再加上 MoE 卸载、稀疏注意力、MX 格式 NPU 等散落在各场的论文，几乎都在回答同一个问题：**decode 阶段每个 token 都要把权重和 KV 从 DRAM 读一遍，这部分搬运怎么省掉？** 本月收录的 11 篇给出了四类答案：把权重固化进 ROM（BitROM、ROMA）；用查表或按位提前终止减少计算和读取（Platinum、BitStopper）；把计算挪到 DRAM 旁边或 KV 正上方（BLADE、SpAct-NDP、M3DKV）；在内存受限的平台上把 MoE 专家按冷热分工（MoBiLE、台大的 CPU-GPU 协同）。需要先说明：这些数字绝大多数是综合或仿真结果，没有一篇是流片实测。

### 会期核对：哪些会落在 1 月窗口

| 会议 | 2026 会期 | 本期处理 |
|---|---|---|
| ASP-DAC | 1/19–22，香港（迪士尼乐园酒店） | 主收录来源，论文按宣讲场次日期标注 |
| AAAI-26 | 1/20–27，新加坡 EXPO（主会 1/22–25） | 偏算法，未检索到可核实的端侧硬件论文，本期不收 |
| HiPEAC 2026 | 1/26–28，克拉科夫 | 以 workshop 为主，未检索到可核实的端侧硬件论文 |
| HPCA / PPoPP / CGO（联合举办） | 1/31–2/4，悉尼 | 首日在窗口外，留给 2 月 |
| ISSCC | 2/15–19，旧金山 | 窗口外，留给 2 月 |
| HotMobile | 2/25–26，亚特兰大 | 窗口外 |

日期取法：会议论文一律按[ASP-DAC 2026 完整程序册](https://www.aspdac.com/aspdac2026/pdf/ASP-DAC_2026_Full_Program.pdf)上的宣讲场次日期标注（1/20、1/21 或 1/22）；IEEE 论文集在 1/19 开放下载。本窗口内各周（1/2、1/9、1/16、1/23、1/30）的硬件雷达此前都是空的，所以没有需要合并去重的往周条目，本节完全基于本期新收的论文。

### 一、主题演讲与圆桌：边缘 AI 与存算一体被放上主舞台

1 月 20 日的第二场主题演讲由杜克大学的陈怡然（Yiran Chen）主讲，题目是“Edge AI: Everything, Everywhere, All at Once”。他把边缘 AI 的难点概括为：多模态数据要处理得动，资源受限时要跑得稳，异构平台之间要协作得起来。1 月 21 日，港科大的谢源讲“从 3D、Chiplet 到 PIM/NDP”的历史脉络。1 月 22 日的压轴圆桌“AI Accelerators at a Crossroads”请到了[后摩智能](https://www.aspdac.com/aspdac2026/pdf/ASP-DAC_2026_Full_Program.pdf)的陈钢和知存科技的王绍迪。两家国产存算一体公司同台，加上 1 月 19 日的 CIM 设计方法学教程，以及“端侧 AI 用于移动与植入式医疗设备”的教程，可以看出存算一体与端侧部署已是这个 EDA 会议的主线之一。产业论文方面，vivo 在 6B 场次发表了 DNN 加速器“非均匀循环-存储映射”协同优化（ALMA）。这是本月唯一一篇手机厂商独立署名的论文，但目前只能看到标题，摘要和数字都没有公开，所以没有收录为条目。

### 二、权重固化：ROM 能放下多大的模型

**BitROM（1/21，4B 场次）**：庆应义塾大学的 [BitROM](https://arxiv.org/abs/2509.08542) 把 1.58-bit 三值权重写进 ROM，每个晶体管存 2 个权重，位密度 4,967 Kb/mm²，约为上一代数字 CiROM 的 10 倍；能效 20.8 TOPS/W。片上 13.5 MB 的 eDRAM 缓存早期 token 的 KV，序列长 128 时外部 DRAM 访问减少 43.6%。数字来自 65nm 后仿真。论文自己给出的 14nm 投影很关键：1B 模型的 ROM 要 16.71 cm²，eDRAM 还要 10.24 cm²。这说明“整模固化”目前只适合几十 M 级的常驻模型，1B 级还远放不进手机芯片。

**ROMA（1/22，9F 场次）**：上海交大、北大与微软亚研的 [ROMA](https://arxiv.org/abs/2503.12988) 把同样的思路放大到 QLoRA。片上 1.86 GB B-ROM 放基座，304 MB SRAM 放 LoRA 和 KV，可以整模装下 2-bit Llama3-8B 或 4-bit Llama3.2-3B。decode 峰值 24.1K/31.8K tok/s，KV 到 4K 时仍超过 1 万 tok/s，论文称比 RTX 4090 上的 TensorRT-LLM 平均快 70.5 倍。但它的面积是 503.7 mm²（7nm），功耗 33.1 W，本质上是一张固化了模型的加速卡。作为对照（推算）：一台 LPDDR5X 约 77 GB/s 的手机跑 2-bit 8B（约 2 GB 权重），batch=1 的 decode 上限约 38 tok/s。两者相差近三个数量级，差距几乎全部来自“权重不出片”。

两篇放在一起看，端侧的启示不是“把模型做进 ROM”，而是**基座长期不变、只更新 LoRA**的部署模式，可以倒推出存储层级：不变的部分放密度最高、不能改写的介质，变化的部分放 SRAM。

### 三、算得更少、读得更少：查表与按位提前终止

**Platinum（1/22，9F）**：杜克大学的 [Platinum](https://arxiv.org/abs/2511.21910) 是三值矩阵乘的查表 ASIC。28nm 下面积 0.955 mm²，吞吐 1534 GOP/s。在 BitNet b1.58-3B 上，它的 prefill 比微软 T-MAC（16 线程 M2 Pro）快 2.15 倍、能耗低 20.9 倍；decode 快 1.75 倍、能耗低 15.0 倍。值得注意的是它的功耗构成：3.2 W 中 DRAM 占 53.5%。计算单元做得再好，带宽仍然是天花板。按 1.6 bit/权重、64 GB/s 推算，3B 模型 batch=1 的 decode 上限约 100 tok/s。

**BitStopper（1/20，2A）**：清华的 [BitStopper](https://arxiv.org/abs/2512.06457) 处理长上下文注意力。它从 Key 的高位比特面开始逐位计算，判断出不重要的 token 就提前停算，把稀疏预测阶段并入正式计算。结果是比 SOFA 快 1.89 倍、能效高 2.1 倍，片外访存占总能耗的比例从 Sanger 的 67% 降到 38%（28nm 综合，703 mW）。论文还量化了一个容易被忽视的开销：在 4K 序列下，传统动态稀疏的预测阶段功耗是正式计算的 4.7 倍。

**MX 格式 NPU（1/21，4D）**：KU Leuven 的[可伸缩 MX 数据通路](https://arxiv.org/abs/2511.06313)（特邀论文）把 8×8 MX MAC 集成进 SNAX NPU，0.60 mm² 内支持 MXINT8 到 MXFP4，能效 657–4065 GOPS/W，并同时支持训练，目标是边缘持续学习。它与 1 月 21 日下午整场“精度可伸缩的边缘智能”特别会议（5B）呼应：端侧 NPU 的精度不再固定，而是按层、按任务切换。另一篇值得一提的是亚琛工大的 [ConfASR](https://doi.org/10.1109/ASP-DAC66049.2026.11420567)（1/20），一个 22nm、1.19 mm²、359 mW 的 Conformer 语音识别块，速度为实时所需的 900 多倍，适合作为耳机、眼镜上的常驻语音前端。

### 四、把计算挪到数据旁边：PIM、NDP 与 3D KV

4B 场次的四篇论文里，有三篇面向 DRAM 侧或存储内计算：
- [BLADE](https://doi.org/10.1109/ASP-DAC66049.2026.11420462)（上海交大）指出，DRAM-PIM 的瓶颈不只是算力，还有 bank 间通信和 V 缓存转置。它按序列长度动态调整 PIM 并行度，论文称比 GPU 基线快 105.7 倍、能效高 41.6 倍，但摘要没有给出基线型号，需要谨慎看待。
- [SpAct-NDP](https://doi.org/10.1109/ASP-DAC66049.2026.11420624)（上海交大、清华）把动态稀疏度超过 80% 的稀疏激活 FFN 交给近数据处理单元，在 RTX 3090 和 A100 上端到端提速 2.17 倍和 1.92 倍。PowerInfer 一类端侧推理依赖的正是稀疏激活，这为 LPDDR-PIM 提供了一个现成的负载。
- 同场的 BALANCE（东南大学）讨论闪存内计算 LLM 加速器的轻量 ECC。闪存内计算是继 HBF 之后另一条“用闪存当模型存储”的思路，但目前只能看到标题。

5A 场次的 [M3DKV](https://doi.org/10.1109/ASP-DAC66049.2026.11420572)（北大、清华）把 KV 放进后道堆叠的增益单元存储层，在其正下方的前道层完成注意力计算。片上带宽 0.29 TB/s/核，decode 比 GPU 快 97 倍。上下文变长之后，端侧瓶颈会从权重转向 KV，把 KV 存在计算单元正上方是一个新方向，不过单片 3D 离消费级量产还远。

### 五、内存不够时怎么跑 MoE

消费级平台跑 MoE 的共同困难是专家放不进显存，PCIe 又太慢。台大的 [CPU-GPU 协同推理](https://arxiv.org/abs/2512.16473)（1/20，3A）实测了一组很直观的数字：Mixtral 单个专家层在 GPU 上计算只要 0.25 ms，搬运却要 28.02 ms，而 24 线程 CPU 就地计算只需 7.34 ms。所以它把热专家缓存在 GPU 上，冷专家留在 CPU 上直接算。Mixtral 8x7B（88 GB）跑到 4.8 tok/s，能耗 51.1 J/token，是 Pre-gated MoE 的 30%。清华的 [MoBiLE](https://arxiv.org/abs/2510.12357)（1/21，6F）换了个角度：不重要的 token 只激活一半专家，在 RTX 4080 16GB 上提速 1.60–1.72 倍；代价是 OLMoE 的 GSM8K 掉了 6.7 个点。这两篇的测试平台都是台式机，但思路可以直接迁移到 AI PC 和统一内存设备：“每个 token 激活多少专家”“未命中的专家在哪里算”都可以作为运行时旋钮。

### 小结：1 月给 2 月定下的基调

1. **带宽是主问题，算力只是陪衬。** 本月几乎每篇论文的功耗拆分里，DRAM 都占一半以上（Platinum 为 53.5%，BitStopper 的对比方为 62–67%）。下一代端侧 NPU 的竞争点在于每个 token 读多少字节，而不是 TOPS。
2. **三条去搬运的路线各有硬伤。** ROM 固化的面积账算不过来；PIM/NDP 要解决 bank 间通信和数据布局；3D KV 的工艺还没准备好。短期最有可能进入手机的，是 LUT、MX 低精度、按位提前终止这类改动不大的 NPU 微架构增强。
3. **口径提醒。** 本月 11 篇全部为综合或仿真结果，无流片；M3DKV、ConfASR、SpAct-NDP、BLADE 只拿到摘要。2 月的 ISSCC（2/15–19）会有大量流片实测，届时可以对照本月的仿真结论。

## 6. arXiv 精选：内存墙、LPDDR 存内计算与端侧 MoE

### 总览：1 月 arXiv 的主线是“内存墙”，不是算力

2026 年 1 月（01-01~01-29）arXiv 上与端侧 AI 硬件相关的论文，几乎都在回答同一个问题：手机和 PC 上的 LLM decode 受 LPDDR 带宽和容量限制，算力并不缺，怎么办。往周硬件雷达在这段时间没有收录条目，本节以本次回填的 20 篇 arXiv 论文（v1 均在窗口内）为主，补充少量窗口内但未单列的论文作背景。整体看有四条路线：一是**改内存**（LPDDR-PIM、ReRAM/MRAM 混合内存、高带宽闪存）；二是**改数据流向**（MoE 专家放 SSD/近存，权重无损压缩，查表记忆放主机内存）；三是**改格式**（1.25 bit 三值、带元数据的 4 bit 微缩放）；四是**为新负载改 NPU**（扩散语言模型采样、智能体长上下文、3D 重建）。论文多为模拟评估，真机实测集中在 Jetson、Apple M4 Max 和骁龙 SM8750 三类平台，引用时需区分“论文实测”和“模拟/推算”。

### 定调：Patterson 把移动端也算进了内存问题

Google DeepMind 的 Xiaoyu Ma 与 David Patterson 在 [Challenges and Research Directions for LLM Inference Hardware](https://arxiv.org/abs/2601.05047)（01-08，IEEE Computer 录用）中指出，LLM 推理的主要难题是内存与互连，并列出四个方向：高带宽闪存（HBF）、近存计算（PNM）、3D 存储-逻辑堆叠和低延迟互连。论文表 3 的量级对比最值得端侧读者记住：一条 16 GB LPDDR5-6400 模组只有约 51 GB/s、3 W，而一个 HBF 堆栈约 512 GB、1638 GB/s。关于移动端，作者明确写道：数据中心里 PNM 优于 PIM，但手机模型更小、上下文更短、单用户 batch=1，PIM 的弱点不那么严重，“在移动设备上可能可行”。按 51 GB/s 推算，4-bit 7B 模型在单条 LPDDR5 上 decode 上限只有约 14 tok/s，这也解释了为什么本月大量论文都在做 LPDDR 端的近存/存内计算。

### 路线一：在 LPDDR 里面算（PIM/CIM）

- **CD-PIM**（[南京大学/中国移动研究院](https://arxiv.org/abs/2601.12298)，01-18，DATE 2026）：把每个 LPDDR5 bank 切成 4 个伪 bank 提升内部带宽，单批次比纯 GPU 平均快 11.42 倍、比 AttAcc 快 4.25 倍。在 iPhone 15 Pro 级配置（51.2 GB/s）下 LLaMA-1B 访存密集场景加速 18.6 倍，高于 Jetson 配置的 10.1 倍，说明带宽越紧的设备收益越大。新增计算单元在 TSMC 28nm 下每个 4.5 mW，总增功耗 144 mW，约占 die 面积 0.8%。同组的 [边缘 GPU-NDP MoE 调度](https://arxiv.org/abs/2601.03992)（01-07）把专家放进近存单元，端到端平均快 2.41 倍。两篇都是模拟结果。
- **QMC**（[UCSD](https://arxiv.org/abs/2601.14549)，01-21）走的是“换内存介质”：普通权重存 2–3 bit 多值 ReRAM，离群权重存 5 bit MRAM，以 Jetson AGX Orin 的 LPDDR5 体系为基线，能耗降 11.7 倍、延迟降 12.5 倍（摘要口径，正文为 10.98/12.48 倍），同样是模拟。
- **数字/随机 CIM 宏**：港科大 [DS-CIM](https://arxiv.org/abs/2601.06724)（01-10）用 OR 门做累加，宏级能效 3566.1 TOPS/W，并在 FP8 LLaMA-7B 上验证精度；东南大学/清华的 [CIM-Tuner](https://arxiv.org/abs/2601.18070)（01-26）开源了经硅验证的 SRAM-CIM 架构/映射联合探索工具，能效提升 1.58 倍；巴伊兰大学的 [PiC-BNN](https://arxiv.org/abs/2601.19920)（01-08）是本月少见的流片实测，65nm CAM 芯片能效 7.03 亿次推理/秒/瓦，但只能跑二值 MLP。窗口内另有 [RRAM CIM 混合精度编译](https://arxiv.org/abs/2601.21737)、[OpenACM 近似 CIM 编译器](https://arxiv.org/abs/2601.11292) 和 [PRIMAL 存内 LoRA 加速器](https://arxiv.org/abs/2601.13628)（对比 H100 能效 25 倍）等工作，说明 CIM 的研究重心正从单个宏转向编译器与系统映射。

### 路线二：让大模型“住”在慢内存里

MoE 让端侧模型参数越来越大，但每个 token 只激活一小部分，于是“容量”和“带宽”可以拆开对待。

- **ZipMoE**（[南京大学](https://arxiv.org/abs/2601.21198)，01-29，后被 ICML 2026 接收）在 Jetson AGX Orin 64GB/32GB 上实测：只对 BF16 指数位做无损压缩（ZSTD 压到 68%，接近约 66% 的熵界），配合缓存亲和调度，推理延迟最多降 72.77%、吞吐最多提高 6.76 倍，且不损失模型行为。
- **FlashMoE**（[论文](https://arxiv.org/abs/2601.17063)，01-22）把不活跃专家放到 PCIe 5.0 SSD（SK hynix P51，7.4 GB/s），并量化了瓶颈：一次 SSD 专家加载约 3 ms，而一次 FFN 只需 158 µs，专家加载占 decode 时间七成以上。它的 ML 缓存策略比 LRU/LFU 命中率最多高 51%，整体最高快 2.6 倍。
- **DeepSeek Engram**（[DeepSeek/北大](https://arxiv.org/abs/2601.07372)，01-12）从模型侧给出同一方向的答案：用确定性地址的 N-gram 查表做“条件记忆”，Engram-27B（26.7B 总参、3.8B 激活）在同参数同 FLOPs 下全面超过 MoE 基线（如 BBH +5.0、NIAH 84.2→97.0）。工程上，100B 参数的查表可放主机内存经 PCIe 预取，H800 上吞吐开销不超过 2.8%。论文本身面向数据中心，但“大容量慢内存存知识、快内存跑计算”的分层与端侧的 LPDDR+UFS 结构天然契合。

窗口外的背景：2025-12 提交、1 月才出现在 cs.AR 列表的 [CHIME](https://arxiv.org/abs/2601.19908)（M3D DRAM+RRAM chiplet，相对 Jetson Orin NX 能效最高 246 倍）属于同一思路，因 v1 不在窗口内未单列。

### 路线三：更少的位、更对齐的位

- **Sherry**（[香港城市大学/腾讯](https://arxiv.org/abs/2601.07892)，01-12）用 3:4 稀疏把三值权重压到 1.25 bit 且保持 2 的幂对齐。BitNet.cpp 框架下 3B 模型 45.55 tok/s、712 MB，比 2-bit I2_S（41.87 tok/s、874 MB）更快更小。按 iPhone 15 Pro 级 51.2 GB/s 推算，712 MB 权重的 decode 带宽上限约 72 tok/s（推算）。注意论文中 CPU 型号和模型规模的表述前后不一致。
- **M2XFP**（[上海交大/华为](https://arxiv.org/abs/2601.19213)，01-27，ASPLOS 2026）在 MXFP4 上加入少量元数据，精度损失比 MXFP4 少 70.63%、比 NVFP4 少 37.30%，加速器最高快 1.91 倍。窗口内的另一篇 [ICLR 2026 论文](https://arxiv.org/abs/2601.19026) 发现微缩放块越小精度反而可能越差，并提出 UE5M3 缩放格式。两者说明 4-bit 浮点格式之争还没有定论，端侧 NPU 选格式时需要留出余地。
- **Mugi**（[UCF/CMU](https://arxiv.org/abs/2601.10823)，01-15，ASPLOS 2026）把值级并行扩展到 softmax 等非线性运算和小批量 GEMM，非线性吞吐最高提升 45 倍，整体 LLM 能效提升 3.11 倍，适合端侧 batch=1 的负载。

### 路线四：新负载需要新 NPU

- **扩散语言模型**：[帝国理工/剑桥](https://arxiv.org/abs/2601.20706)（01-28）给出首个面向 dLLM 的 NPU。他们发现 LLaDA 等模型的采样阶段（归约、top-k）最多占延迟约 70%，以 GEMM 为中心的 NPU 处理不好。7nm 下 2048 位向量单元 2.93 mm²、1.52 W，采样比 RTX A6000 快 2.53 倍（v1 为模拟）。
- **边缘解码加速器**：华科 [SwiftKV](https://arxiv.org/abs/2601.10953)（01-16）在 Alveo U55C 上实测 LLaMA2-7B（W4A8）81.5 tok/s、2.41 token/J，约为 FlightLLM 的 2 倍能效，但依赖板载 HBM，换算到 LPDDR 端侧需按带宽打折。
- **3D/XR**：港科大 [VersaQ-3D](https://arxiv.org/abs/2601.20317)（01-28）为十亿参数级 VGGT 做 4-bit 量化和多精度加速器，比边缘 GPU 快 5.4–22.0 倍。
- **智能体负载**：[帝国理工/微软研究院](https://arxiv.org/abs/2601.22001)（01-29）用运算强度和容量足迹两个指标分析聊天、编码、网页与电脑操作四类智能体，结论是长上下文 KV Cache 让 decode 高度受内存约束，需要 prefill/decode 分离的异构硬件。这个判断同样适用于端侧智能体。

### 真机数据：Apple、高通、Jetson 各有一组

- **Apple M4 Max**：[vllm-mlx](https://arxiv.org/abs/2601.19139)（01-27）在 128 GB/546 GB/s 统一内存上测 4-bit 模型：Qwen3-8B 93.3 tok/s（llama.cpp 76.9），Qwen3-30B-A3B 109.7 tok/s，Qwen3-0.6B 525.5 tok/s。按带宽推算，8B 已达理论上限约 77%，30B-A3B 只到约 40%，MoE 路由效率仍有空间。Qwen3-VL-8B 多轮看图靠内容哈希缓存从 21.7 s 降到 0.78 s。
- **骁龙 SM8750 与 A17 Pro**：三星印度研究院的 [NanoSD](https://arxiv.org/abs/2601.09823)（01-14）在 Galaxy S25 Ultra 的 NPU 上把 SD1.5 蒸馏版跑到 12–41 ms（W8A16），SD1.5 原版在两家 NPU 上 FP32/INT16/INT8 都编译不出可执行文件。同一模型在 A17 Pro 上的排序与在骁龙上不同（130M 的 NanoSD 7 在 A17 Pro 上要 66 ms），说明模型应按 NPU 设计，参数少不等于跑得快。
- **嵌入式**：[ZeroDVFS](https://arxiv.org/abs/2601.08166)（01-13）在 Jetson TX2/Orin NX/RubikPi 上用 LLM 特征做零样本调频，能效提升 7.09 倍；[边缘 GPU 隔离研究](https://arxiv.org/abs/2601.07600) 在 Jetson Orin 上比较了 MPS、MIG 和 Green Contexts，后者可做低开销的细粒度 SM 分配，但没有内存隔离。

### 总结：对端侧 AI 的三点判断

1. **带宽仍是第一约束，PIM 有了权威背书。** Patterson 明确认为 PIM 在移动端可能可行，CD-PIM 等工作给出了百毫瓦级代价、数量级加速的模拟证据。LPDDR6 时代的 PIM 标准化值得持续跟踪，但目前还没有手机级真机数据。
2. **容量和带宽在分开发展。** ZipMoE、FlashMoE、Engram 都在把“很少访问的大块参数”放到更便宜、更慢的介质上（SSD、主机内存）。对手机来说，这意味着 UFS 与 LPDDR 之间的数据通路和缓存策略会变成影响体验的指标。
3. **NPU 设计要跟着负载变。** 扩散解码、智能体长上下文和 3D 感知都不是纯 GEMM 负载，下一代端侧 NPU 需要补上归约、非线性和多精度能力。另一方面，本月的硬数字大多来自模拟或 FPGA，真机实测只有 M4 Max、SM8750/A17 Pro 和 Jetson 三组，引用时应把这些口径区分清楚。

## 7. 总结：对端侧智能体意味着什么，以及 2 月该看什么

**对端侧智能体的含义**

1. **先看内存，再看 TOPS。** X2 Plus 与 X2 Elite 的 NPU 都是 80 TOPS，差别在 152 与 228 GB/s 的带宽。按带宽推算，主流 AI PC 上常驻智能体的甜点区是 3–8B INT4 稠密模型或低激活 MoE；“128 GB 能装下 200B”只说明容量。
2. **端云分工更明确。** Apple 把前沿模型交给 Gemini、跑在 PCC，端侧留约 3B 小模型和个人上下文；高通与 Google 的车载方案也是“车端模型 + 云端 Gemini”。工程重点是端云切换和工具调用。
3. **运行时决定能用哪颗 NPU。** LiteRT 的 NPU prefill 比 GPU 快 3 倍，对要读大量上下文的智能体最有用，decode 仍受带宽限制；系统级共享模型普及后，应用定制会从改权重转向提示优化。
4. **涨价会把高级端侧 AI 推向旗舰。** 中端机若停在 8 GB，只能跑 1–3B 常驻模型；低比特量化、MoE 按需加载和闪存流式读取（ZipMoE、FlashMoE、Engram）的价值会上升。
5. **常开感知与重推理分层。** Rokid 眼镜用 RT600 常开、AR1 按需唤醒，大模型走云端；Ambiq、Nordic 把 NPU 放进 MCU 和蓝牙芯片，指标是常开功耗而不是 TOPS。

**留给 2 月的问题**

- ISSCC（2/15–19）和 HPCA（1/31–2/4）的流片数据能否印证 1 月的仿真结论。
- Galaxy S26 的内存配置与端侧模型规模；酷睿 Ultra 3、锐龙 AI 400 的第三方 LLM 实测。
- 涨价传导：TrendForce 是否继续上修，高通 2 月 4 日 FY26 Q1 指引（素材提示因内存短缺下调）。
- iOS 26.4 个性化 Siri 能否如期展示（素材显示 2 月 17 日测试版没有新 Siri）。
- 待核实：IQ10、DX-M2 的内存容量与带宽，Q-8750 跑 11B 的实测速度，高通 2nm 是否交给三星。

> 口径说明：“官方”是厂商数字，“开发者实测”“媒体”为独立测试或报道，“爆料”未经确认（AFM v10 规模、Siri 托管 Google 云、Apple LPDDR 涨价、高通–三星 2nm、玄戒 O2 用 N3P），“推算”按公开带宽和模型大小计算，“模拟 / 仿真”为未流片结果。1 月没有新品的方向：高通、Apple、Google 无新手机芯片，Tensor 无一手进展；麒麟、展锐、瑞芯微无新 SoC；国内外存算一体公司无新产品，SK 海力士 PIM 方案只是展示原型；LPDDR6 无新数据。本期为 2026-10 回填。
