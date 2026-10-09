# 硬件洞察：端侧 AI 芯片月报（2026-05-15 ~ 2026-05-28）

> **说明：** 本站的周报数据从 2026-05-15 开始，所以 5 月只覆盖下半月两周；5 月上旬的动态（如 5 月 7 日的骁龙 6 Gen 5 / 4 Gen 5、Tensor G6 爆料）只在分节中作为背景出现。5 月 29 日起的 Computex 归入 6 月。
>
> **一句话结论：5 月下半月是“软件月”和“祛魅月”。** 没有旗舰芯片发布，最具体的端侧数字来自软件栈：Google LiteRT-LM 上 Gemma 4 E2B 在手机 GPU 上 decode 52–56 tok/s，Meta ExecuTorch 在 Hexagon NPU 上把 Llama 3.2 1B 的 prefill 做到约 2,900 tok/s。同时，多篇独立实测指出，在通用框架上手机 NPU 的 decode 只快 5–20%，prefill 甚至可能慢于 CPU。芯片侧的增量在中端（天玑 8550 的 LLM Booster）和眼镜（Android XR、安凯微、Coral NPU）。
>
> **阅读结构（总-分-总）**：第 0 节是半月判断；第 1–6 节分厂商、分方向展开（高通 / Apple 与 Google / 其他 SoC 与 PC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选）；第 7 节是对端侧智能体的含义和观察清单。逐条动态（含“能跑多大模型”和可展开的“技术细节”）见 05-15、05-22 两周首页的“硬件雷达”。

## 0. 总览：5 月下半月的五个判断

**判断一：2B 级端侧模型的 decode 进入 50 tok/s 档，跨平台运行时成熟。**

| 平台 | 模型 | decode / prefill | 口径 |
|---|---|---|---|
| Galaxy S26 Ultra GPU（LiteRT-LM） | Gemma 4 E2B | decode 52 tok/s（MTP 最多再快 2.2 倍） | Google 官方 |
| iPhone 17 Pro GPU（LiteRT-LM） | Gemma 4 E2B | decode 56 tok/s | Google 官方 |
| M4 Max WebGPU（LiteRT-LM） | Gemma 4 E2B | decode 最高 76 tok/s | Google 官方 |
| Galaxy S25（8 Elite，4 线程 CPU） | MobileMoE-S | decode 138.1 tok/s | Meta 论文 |
| iPhone 16 Pro（A18 Pro，2 线程） | MobileMoE-S | decode 204.6 tok/s | Meta 论文 |

**判断二：NPU 的真实收益由软件栈决定，而不是 TOPS。**

| 研究 | 平台 | 结果 |
|---|---|---|
| ExecuTorch（MLSys） | Galaxy S25 Ultra Hexagon NPU，Llama 3.2 1B（A16W4） | prefill 2813–2977 tok/s，llama.cpp NPU 路径为 330–374 tok/s |
| Quant.npu（arXiv） | 骁龙 8 Elite，Qwen2.5-3B（W4A8） | prefill 970 tok/s（ExecuTorch 808） |
| NPU 并不总是更快（arXiv，莱顿） | 骁龙 8 Gen 3，llama.cpp | prefill NPU 比 CPU 慢 1.27–1.62 倍；decode 端到端只快 1.05–1.20 倍 |
| CORE（MLSys，上海交大） | Pixel 7 | 联合调 CPU/GPU/内存频率，TPOT 降 27.8–39.6%，每 token 能耗不增加 |

**判断三：“12GB 内存”成为高级端侧 AI 的共同门槛。** Android 的 Gemini Intelligence 要求旗舰芯片 + 至少 12GB 内存 + Gemini Nano v3 以上；三周后的 WWDC26 上，Apple 的 20B 稀疏端侧模型同样以 12GB 为门槛（见 6 月）。Chrome 的 Prompt API 则要求 4GB 以上显存或 16GB 内存。

**判断四：手机跑 8B–14B 的路线是“闪存 + MoE + 投机解码”。**

| 研究 | 做法 | 结果 |
|---|---|---|
| Lever（清华） | 目标模型放闪存，投机解码批量验证 | 比直接从闪存读取快 2.93 倍；单次验证 I/O 占 78–93% |
| ReMoE（北航 / 华为，ICML 2026） | 微调路由提升专家复用 | Jetson Orin NX 上 decode 提速 1.77–1.99 倍 |
| NASiC（北大，DAC 2026） | 3D NAND 内做 MoE 存内计算 | 架构级评估：性能 4–114.8 倍 |
| MobileMoE / Dense2MoE | 小参数 MoE 模型家族 | 激活参数少、decode 快 |

**判断五：芯片增量在中端和眼镜。** 天玑 8550 给中端加上 LLM Booster（INT4、投机解码、Gemini Nano V3），但不再公布 TOPS；Android XR 音频眼镜今秋上市；安凯微眼镜芯片 0.5–8 TOPS、单次拍照低至 0.08mAh；Google 开源 Coral NPU 的首块开发板 1 TOPS 可跑 Gemma 3 270M。眼镜的指标正在从 TOPS 转向“每次拍照 / 每次唤醒耗多少电”。

### 5 月下半月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 05-15 | Gemini Intelligence 硬件门槛：旗舰芯片 + 12GB；联发科更新天玑主流芯片 | Google / 移动 SoC |
| 05-16 | 清华 Lever：手机闪存驻留 8B–14B 投机解码 | 研究 |
| 05-17 | 爆料：独立 Siri App、Gemini 版 Siri 跑在 PCC | Apple |
| 05-18 | LiteRT-LM v0.12（CLI 支持 NPU）；卢伟冰确认玄戒年内迭代 | 软件 / 移动 SoC |
| 05-18~22 | MLSys 2026：ExecuTorch、CORE、IntAttention、Kitty 等 | 研究 |
| 05-19 | Google I/O：LiteRT-LM 数据、Chrome Prompt API、Android XR 眼镜、Coralboard；Mythic 收购 Videantis；AI Hub 上架 Pi0.5 | Google / 低功耗 |
| 05-21 | 高通与 Stellantis 扩大合作，aiMotive 拟并入高通；小米 17 Max | 车载 |
| 05-25 | 华为“韬定律”与双层逻辑折叠；荣耀 600 Pro、OPPO Reno16 Pro；N1X 泄露 | 移动 SoC / PC |
| 05-26 | MobileMoE、ReMoE、Dense2MoE；Android I/O AI 汇总（Nano 4 预览） | 研究 / 软件 |
| 05-27 | 天玑 8550 发布；安凯微 AI 眼镜芯片 | 移动 SoC / 眼镜 |
| 05-28 | 爆料：Apple 用 Gemini 蒸馏端侧模型；三星代工 × Cadence 物理 AI chiplet | Apple / 代工 |

## 1. 高通：车载与工具链，没有新芯片

5月15日至28日是高通的“发布空窗期”：5月7日的骁龙6 Gen 5/4 Gen 5已经发完，Computex（6月1日主题演讲）和Investor Day（6月24日）都还没到。窗口内没有新的手机或PC芯片，真正有分量的是两件“软”事：一是5月21日Stellantis把ADAS软件栈也交给高通，并拟把aiMotive并入高通；二是开发者侧的工具链更新，包括AI Hub上架Pi0.5机器人VLA模型、X2 Elite NPU本地Agent，以及面向带宽优化的Adreno tile memory扩展。整体判断：高通在这两周的重心是车载全栈化和开发者生态，芯片硬指标留到了6月及之后。

### 一、车载：从“卖SoC”到“SoC+ADAS软件+仿真”

[Stellantis与高通扩大合作](https://www.qualcomm.com/news/releases/2026/05/stellantis-and-qualcomm-expand-partnership-to-adopt----snapdrago)（5月21日）是窗口内唯一的官方新闻稿。要点如下：

| 维度 | 官方口径 | 未披露 |
|---|---|---|
| 覆盖域 | 座舱、连接、ADAS统一采用Snapdragon Digital Chassis SoC | 具体SoC型号（Ride Elite/Ride Flex/Cockpit Elite均未点名） |
| ADAS软件 | Snapdragon Ride Pilot，从主动安全/法规功能扩展到L2+脱手驾驶 | 传感器配置、TOPS |
| 平台集成 | 与STLA Brain电子电气/软件平台集成 | 首发车型、年份 |
| 规模 | Ride Pilot可赋能“数百万辆”Stellantis车辆 | 金额、出货量 |
| 法律性质 | non-binding award，需后续正式协议、尽调与监管审批 | — |
| 附带交易 | 非约束性LOI：aiMotive拟加入高通 | 价格、结构、时间 |

和此前“14个品牌用Digital Chassis、2024年Maserati首发”的老协议相比，本次的增量在ADAS软件层，同时通过aiMotive补上了仿真与自动驾驶算法团队（见[Robotics & Automation News](https://roboticsandautomationnews.com/2026/05/22/stellantis-expands-qualcomm-partnership-for-ai-powered-vehicle-platforms/101840/)、[Digitimes](https://www.digitimes.com/news/a20260525PR202/stellantis-qualcomm-snapdragon-vehicle-adas.html)转述）。这让高通在欧洲传统车企面前，可以直接对标英伟达DRIVE和Mobileye的整套交付模式。需要提醒的是，授标和LOI都是非约束性的，短期确定性有限。

窗口外的背景有两条。5月29日的OnQ文章《[China Speed](https://www.qualcomm.com/news/onq/2026/05/china-speed-automotive-ai-innovation)》提到理想Li9、零跑D19/D99等量产车搭载Snapdragon Elite级平台，并称联合开发能把开发周期压缩到传统流程的近一半。6月的无锡汽车峰会上，媒体称Ride Flex（8775）已获9款车型定点，8797平台“有效算力最高2000 TOPS”（[媒体口径](https://english.news18a.com/news/english_264309.html)，型号命名与SA8775P体系不一致，需以官方为准）。由此可见，高通在中国主推舱驾一体单芯片，在欧洲则先以“分域统一+软件栈”切入。

### 二、XR/可穿戴：Google I/O上的Android XR眼镜

Google I/O 2026（5月19日开幕）展示了[Gemini版Android XR眼镜](https://www.phonebunch.com/news/google-i-o-2026-android-xr-platform-intelligent-eyewear-samsung_9460.html)，分音频眼镜和显示眼镜两类，音频眼镜2026年秋季先上市。媒体称Android XR由Google、三星与高通联合开发，但I/O期间没有点名眼镜芯片。直到9月骁龙峰会，Google才确认这批眼镜采用[Snapdragon AR1](https://the-gadgeteer.com/2026/09/23/snapdragon-summit-2026-qualcomm-puts-ai-agents-on-smart-glasses/)。架构上，Gemini依赖配对手机的连接实现AI功能，眼镜端负责相机、音频、唤醒等低功耗常驻任务。这再次说明，眼镜品类的端侧AI重点是常驻感知和ISP能效，而不是在眼镜上跑大模型。

### 三、软件栈与工具链：VLA、本地Agent与带宽

| 日期 | 内容 | 关键技术点 | 性能数据 |
|---|---|---|---|
| 5-19 | [AI Hub Models v0.54.0](https://github.com/qualcomm/ai-hub-models/releases?page=2) | 新增Pi0.5 VLA；新增Dragonwing Q-7790/Q-8750/IQ-X5121/IQ-X7181与SA8255P/SA8650P设备指标 | release note未给 |
| 5-26 | [LLMWare本地Agent](https://www.qualcomm.com/developer/blog/2026/05/local-agentic-ai-with-llmware-on-pcs-with-snapdragon-x-series) | Windows ML + ORT GenAI + QNN EP，X2 Elite NPU为主 | 未披露 |
| 5-27 | [Tile Memory Heap](https://www.qualcomm.com/developer/blog/2026/05/high-performance-memory-extension-optimize-memory) | VK_QCOM_tile_memory_heap把片上tile内存暴露为Vulkan heap | 未给百分比 |

**Pi0.5（VLA）**：[AI Hub模型页](https://aihub.qualcomm.com/models/pi05)显示该模型拆为vision_encoder、token_emb、backbone、action_expert四个子图，backbone用w4a16，视觉编码器和动作专家用w8a16。输入为3路相机、224×224，输出50步action chunk。页面在X2 Elite CRD NPU上默认展示的一组组件指标为2.05 ms、489 inf/s、39 MB，但没有标明对应哪个组件，完整控制回路延迟未披露。这是高通首次把通用机器人基础模型放进官方预优化库，和CES发布、Computex升级的Dragonwing IQ10机器人参考设计（[Computex报道](https://the-gadgeteer.com/2026/06/01/qualcomm-computex-snapdragon-c-dragonwing-iq10-robotics/)）是一条路线。

**本地Agent**：LLMWare这篇博文的价值在“栈”而不在“数”。ISV通过微软的Windows ML/Foundry Local标准路径调用Hexagon NPU，不再直接面对QNN。算力背景方面，X2 Elite的Hexagon NPU官方口径为80 TOPS（INT8），比初代X Elite的45 TOPS提升约78%（[Windows Central](https://www.windowscentral.com/hardware/qualcomm/qualcomm-announces-snapdragon-x2-plus-ces-2026)）。博文没有模型名称、量化精度和tokens/s，只能算方案演示。

**Tile Memory Heap**：扩展号548，2025年已进入Vulkan规范（[proposal](https://docs.vulkan.org/features/latest/features/proposals/VK_QCOM_tile_memory_heap.html)），本次博文是使用指南。它允许render和compute pass在一次提交批次内共享片上tile内存，减少LPDDR往返。对端侧来说，GPU上的神经渲染和小网络后处理同样受带宽约束，这类显式片上内存API值得关注。Google 2025年公布的LiteRT QNN加速器数据（72个模型中64个可完全下放NPU，8 Elite Gen 5上56+个模型低于5 ms，LLM路径为int8权重+int16激活，见[Google Developers Blog](https://developers.googleblog.com/unlocking-peak-performance-on-qualcomm-npu-with-litert/)）说明，NPU以外的GPU路径同样需要带宽层面的优化。

### 四、终端与爆料：窗口内的“存量”

- **终端**：[小米17 Max](https://91mobiles.com/hub/xiaomi-17-max-china-launch-confirmed-may-21st)于5月21日发布，搭载Snapdragon 8 Elite Gen 5和8000mAh电池，起售价4299元（媒体口径），没有新的端侧AI规格披露。窗口内骁龙旗舰新机的卖点集中在续航和影像。
- **背景（窗口前）**：5月7日的[骁龙6 Gen 5/4 Gen 5](https://www.qualcomm.com/news/releases/2026/05/qualcomm-unveils-two-new-snapdragon-mobile-platforms--delivering)为4nm，官方称应用启动快20%–43%、卡顿减少18%–25%（[IT之家](https://www.ithome.com/0/947/192.htm)），终端在2026下半年上市，AI不是主要卖点。
- **爆料（窗口前，仅作背景）**：Digital Chat Station在3月爆料8 Elite Gen 6分为SM8950/SM8975两款，均为TSMC 2nm，CPU为2+3+3，Pro版Adreno 850配18MB GMEM、支持LPDDR6/UFS 5.0，标准版Adreno 845配12MB GMEM、LPDDR5X（[Gizmochina](https://www.gizmochina.com/2026/03/25/snapdragon-8-elite-gen-6-8-elite-gen-6-pro-specs-leak/)）。另有爆料称GPU增至6个slice（[tbreak](https://tbreak.com/snapdragon-8-elite-gen-6-gpu-slices/)）。5月12日有爆料称Pro版单颗成本超过300美元（[AndroidHeadlines](https://androidheadlines.com/2026/05/snapdragon-8-elite-gen-6-pro-price-leak-ultra-flagships.html)）。以上均为爆料，NPU规格完全没有泄露；正式规格以9月骁龙峰会为准。窗口内未发现关于X3或8 Elite Gen 6的新可信爆料。
- **窗口外紧邻事件**：Dragonwing MBM715/MBM415（4nm，MBM715带Hexagon生成式AI引擎、LPDDR5x-4200、Wi-Fi 7 5.8Gbps）据报道于“5月底”发布，但确切日期无法核实，媒体报道集中在6月8–9日（[CNX](https://www.cnx-software.com/2026/06/08/qualcomm-dragonwing-mobile-broadband-multimedia-mbm-mbm715-and-mbm-415-socs-combine-5g-wi-fi-multimedia-and-edge-ai/)、[Wi-Fi NOW](https://wifinowglobal.com/news-blog/qualcomms-new-dragonwing-mbm-silicon-solution-combines-interactive-multimedia-with-top-tier-wi-fi-5g-connectivity-and-on-device-ai/)），本期不计入。ASUS Ascent QN10（X2 Elite 18核、80 TOPS INT8、最高32GB LPDDR5X）于6月2日Build期间发布（[ASUS](https://www.asus.com/us/business/resources/news/computex-2026-ascent-qn10/)），也不计入。

### 小结

这两周高通没有发布新芯片，可记录的变化集中在三处。（1）车载由SoC供应商升级为“SoC+Ride Pilot软件+aiMotive仿真”的全栈方案，但授标和LOI都非约束性。（2）机器人VLA进入AI Hub官方模型库，采用w4a16主干和w8a16动作专家的混合精度。（3）PC本地Agent通过Windows ML标准栈调用Hexagon NPU。需要注意，窗口内几乎所有官方材料都没有给出tokens/s、TOPS或功耗等硬数字，真正的硬件指标要看6月Computex（Snapdragon C、IQ10升级、Dragonfly）和9月第六代骁龙8至尊版。

## 2. Apple 与 Google：I/O 给出端侧实测，Apple 只有爆料

**判断：** 5 月下半月是“WWDC 前夜 + Google I/O”的窗口期。Google 一方给出了本月最扎实的端侧数字——Gemma 4 E2B 在旗舰手机 GPU 上 52~56 tok/s、MTP 再提速最高 2.2 倍、iOS 上仅约 607 MB 常驻内存——并把 LiteRT-LM 从 Android 推向 iOS、Web 与 Intel NPU；Apple 一方则几乎没有一手发布（Apple ML Research 博客在 4 月 23 日 ParaRNN 之后直到 6 月 8 日才更新，MLX 在 4 月 22 日 v0.31.2 后至 7 月才有新版），信息主要来自 Gurman 与 The Information 的爆料，核心是“端侧蒸馏 Gemini + 云端借力 Google/Nvidia”。

### 一、Google I/O 2026：端侧 LLM 进入“50 tok/s + 跨平台”阶段

I/O 当天（5 月 19 日）Google 在 [LiteRT-LM 技术博客](https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/) 中给出了官方口径的 decode 吞吐：

| 设备 / 后端 | 模型 | Decode（无 MTP） | 备注 |
|---|---|---|---|
| Galaxy S26 Ultra / OpenCL GPU | Gemma 4 E2B | 52 tok/s | MTP 最高 2.2x |
| iPhone 17 Pro / Metal GPU | Gemma 4 E2B | 56 tok/s | 开源 Swift API |
| MacBook Pro M4 Max / WebGPU | Gemma 4 E2B | 最高 76 tok/s | LiteRT-LM.js |
| Apple 移动端 CPU | Gemma 4 E2B | 未披露 | 物理内存约 607 MB |

几个值得工程师关注的机制：

- **MTP 投机解码**：drafter 与主模型跑在同一加速器上、共享 KV Cache，避免 CPU↔GPU/NPU 间搬运；Gemma 官方[发布记录](https://ai.google.dev/gemma/docs/releases)显示 MTP 权重已于 4 月 16 日随 E2B/E4B/31B/26B A4B 发布，I/O 是把它工程化进 runtime。
- **内存压缩**：E2B 文件约 2.58 GB，但 Per-Layer Embedding 不常驻、图像/音频编码器按需加载，加上 XNNPACK weight caching，使 iOS CPU 物理占用降到约 607 MB——这解释了 Google 为何敢把 Gemma 4 推向 8 GB 内存的 iPhone。
- **带宽决定 decode**：同一模型在 M4 Max（高带宽统一内存）上 76 tok/s，高于手机 GPU 的 52~56 tok/s，与“decode 受内存带宽约束”的经验一致。量化位宽 Google 未披露。

前一天发布的 [LiteRT-LM v0.12.0](https://github.com/google-ai-edge/LiteRT-LM/releases/tag/v0.12.0) 让 CLI 在 Linux/macOS/Windows 上支持 NPU，并通过 `--backend=npu` 接入 **Intel OpenVINO NPU**，同时修复了一个把 prefill 限制在 50% 的 GPU bug。此前 LiteRT 的 NPU 支持以 Qualcomm、MediaTek 手机 NPU 为主（AOT 与端上编译两种方式）。至此 LiteRT-LM 已覆盖手机 NPU、AI PC NPU、Apple GPU 与浏览器 WebGPU 四类后端。

### 二、Android：Nano 4、门槛与 Agent 平台

- **Gemini Nano 4**：4 月 2 日已[预发布](https://developer.android.com/blog/posts/gemma-4-the-new-standard-for-local-agentic-intelligence-on-android)，基于 Gemma 4（AICore 预览提供 E2B 与 E4B），官方称较上一代最高快 4 倍、省电最高 60%，Nano 已覆盖 1.4 亿台以上设备。I/O 上 [Android 开发者博客汇总](https://android-developers.googleblog.com/2026/05/android-ai-intelligence-system.html)（5 月 26 日）确认 Nano 4 仍处 AICore Developer Preview，“今年晚些时候”随旗舰机发布，具体参数、tok/s、机型未披露。
- **Prompt API 新能力**：Prefix Caching（跨请求复用共享前缀的中间状态，即 KV Cache 复用，直接压缩 Agent 场景下长 system prompt 的 prefill）与即将推出的 Structured Output API。
- **端云混合**：Firebase AI Logic 提供 PREFER_ON_DEVICE / PREFER_CLOUD / ONLY_ON_DEVICE / ONLY_CLOUD 四种路由；ADK for Android 支持端云多 Agent；AppFunctions 让 App 成为端上 MCP Server。
- **硬件门槛**：5 月 15 日 [9to5Google](https://9to5google.com/2026/05/15/gemini-intelligence-android-spec-requirements/) 披露 Gemini Intelligence 需要“旗舰芯片”、**≥12 GB RAM**、Gemini Nano v3+，以及 5 次系统升级、6 年安全更新。Pixel 10、Galaxy S26、OnePlus 15 等满足；Pixel 9、Galaxy Z Fold7、Xiaomi 15 仍为 Nano v2。

| 维度 | Gemini Intelligence（Android） | 说明 |
|---|---|---|
| 内存 | ≥12 GB | 官方脚注 |
| 芯片 | “flagship chip” | 未给出清单/TOPS |
| 模型 | Gemini Nano v3 或以上 | 以 Prompt API 支持为准 |
| 软件 | 5 次 OS 升级 + 6 年安全更新 | 另有崩溃率等质量指标 |

另据 5 月 4 日 Mystic Leaks 爆料（[9to5Google](https://9to5google.com/2026/05/04/google-pixel-11-specs-cameras-tensor-g6-leak/)，窗口前，仅作背景）：Tensor G6 采用 TSMC 2nm、1+4+2 Arm C1 CPU、新 TPU 与新 GXP ISP，但 TPU 性能未披露。

### 三、浏览器与眼镜：两种新的端侧载体

- **Chrome**：[I/O Chrome 汇总](https://developer.chrome.com/blog/chrome-at-io26)宣布 Prompt API 在 Chrome 148 稳定（多模态输入、JSON Schema/正则约束输出），并发布 **Gemma 197M** 专家模型承担 Summarizer 等任务型 API。[Prompt API 文档](https://developer.chrome.com/docs/ai/prompt-api)给出的硬件门槛是：GPU 显存 >4 GB，或 16 GB RAM + 4 核 CPU，存储 ≥22 GB 空闲，暂不支持移动端。这是典型的大小模型分层：Gemini Nano 负责通用，197M 级模型下沉到低配设备。
- **Android XR 眼镜**：[Google 官方](https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/)宣布与 Samsung、Qualcomm 共建，音频眼镜今秋先发，显示款随后，同时支持 Android 与 iOS。官方未公布芯片；媒体爆料首款 Samsung 眼镜采用 Snapdragon AR1、约 50 g、155 mAh（[Smartprix](https://www.smartprix.com/bytes/samsung-galaxy-glasses-release-date-price-android-xr-features-specs-everything-else-we-know/)，爆料）。架构上，眼镜负责传感/唤醒/ISP，推理主要落在手机或云端。

### 四、Apple：无一手发布，爆料指向“蒸馏 + 外部算力”

| 日期 | 来源 | 内容 | 口径 |
|---|---|---|---|
| 05-17 | Gurman / [9to5Mac](https://9to5mac.com/2026/05/17/apple-launching-new-siri-app-next-month-with-auto-deleting-chat-history/) | 独立 Siri App、beta 标签，Gemini Siri 跑在 Apple PCC | 爆料 |
| 05-23 | MacRumors / [TechTimes](https://www.techtimes.com/articles/317080/20260525/apple-registers-genai-subdomain-ahead-wwdc-siri-overhaul-finally-arrives-ios-27.htm) | genai.apple.com 子域名出现 | 媒体 |
| 05-28 | The Information / [9to5Mac](https://9to5mac.com/2026/05/28/new-details-on-apple-google-ai-deal-revealed-including-nvidia-chips-report/) | 用 Gemini 蒸馏端侧小模型；完整 Gemini 为“数万亿参数”，部分 Siri 请求跑在 Google Cloud 的 Nvidia 机密计算上；考虑收购 Liquid AI | 爆料 |

技术上值得注意的两点：

1. **端侧模型改走蒸馏路线**。此前 Apple 的端侧 Foundation Model 在 ANE 上采用 palettization，平均低于 4 bit/weight（[Apple 技术报告](https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025)，背景）。如果新端侧模型由 Gemini 蒸馏而来，参数规模和量化方式未必大变，但质量上限将取决于 teacher。
2. **自研服务器芯片暂时撑不住万亿参数**。Gurman 1 月称 PCC 上的定制 Gemini 约 1.2 万亿参数；Kuo 1 月称 Apple 自研 AI 服务器芯片 2H26 量产、自建数据中心 2027 年运营；Baltra 早前报道为 TSMC N3P、与 Broadcom 合作网络。5 月 28 日的报道说明，在 Baltra 落地前，Apple 需要借 Google Cloud + Nvidia confidential compute 补算力，“PCC”品牌将覆盖非 Apple 硬件。

Apple ML Research 博客在本窗口内无新文章（4 月 23 日 ParaRNN → 6 月 8 日第三代 Foundation Models），CVPR 2026 参会页（5 月 28 日）仅为论文列表；MLX 本窗口无 release。M5 Neural Accelerator 的 MLX 支持（M5 带宽 153 GB/s，较 M4 的 120 GB/s 提升，TTFT 提升 19~27%）是 2025 年 11 月的旧闻，此处仅作背景。

**范围说明**：Microsoft Build 2026 在 6 月 2~3 日举行（Windows ML 2.0、Foundry Local 等），WWDC26 在 6 月 8 日，均不属于本窗口。

### 小结

- **Google** 在 I/O 上把端侧 LLM 的竞争点从“能不能跑”推进到“多快、多省内存、几个平台”：2B 级有效参数模型 50+ tok/s 已是旗舰手机 GPU 的基线，MTP 与 Prefix Caching 分别攻 decode 与 prefill，12 GB RAM 成为 Android 高端 AI 的硬门槛。
- **Apple** 在 WWDC 前保持沉默，爆料显示其“端侧 + 自有 PCC”架构正在变成“蒸馏端侧模型 + PCC + Google/Nvidia 云”的混合体，自研 Baltra 服务器芯片的时间表因此更受关注。
- 需要跟进：Nano 4 的实际参数、量化方式与 NPU tok/s（随 Pixel 11 / Galaxy Z Fold8 发布）；Gemma 197M 的细节；WWDC26 第三代 Apple Foundation Models 的端侧规格（6 月已覆盖）。

## 3. 联发科、华为、小米与 PC：中端下放 LLM 加速

5 月下半月（5/15–5/28）高通、苹果、谷歌之外的端侧芯片新闻，大致是“中端下放 + 工艺另辟蹊径 + PC 预热”三条线。联发科把 LLM Booster、投机解码、INT4 混合精度这些旗舰手段搬进天玑 8550，荣耀、OPPO 同周首发。华为在 ISCAS 2026 公开“韬(τ)定律/逻辑折叠”，想在受限工艺上把密度和能效拿回来。NVIDIA N1X 的爆料在 Computex 前集中出现，Arm PC 的焦点从 TOPS 转向统一内存容量与带宽。整个月的背景是内存涨价：手机厂商只能在“端侧 AI 要 12GB 以上内存”和“BOM 被 DRAM 吃掉”之间取舍。

### 一、联发科：天玑 8550 把 LLM 加速下放到中端

联发科 [5 月 15 日官方博客](https://www.mediatek.com/tek-talk-blogs/mainstream-to-premium-smartphones-get-a-fresh-set-of-mediatek-dimensity-chipsets)汇总了一批新天玑。主流的 6000/7000 系讲的是能效：6500/6360 在 20 个场景下能效最高提升 19%，7300e 的 Modem 能效提升 21%。真正围绕生成式 AI 的只有 8550。媒体在 [5 月 27–28 日](https://mezha.ua/en/news/mediatek-dimensity-8550-311713/)报道了它的完整规格：

| 项目 | 天玑 8550 | 天玑 8500（2026.1） |
|---|---|---|
| 工艺 | TSMC 4nm N4P | 同 |
| CPU | 8×A725：1×3.4 + 3×3.2 + 4×2.2GHz，6MB L3 + 5MB SLC | 同 |
| GPU | Mali-G720 MC8 | 同 |
| NPU | NPU 880 + **LLM Booster**（TOPS 未披露） | NPU 880 |
| AI 特性 | Gemini Nano V3、DiT、INT4 混合精度、投机解码、NeuroPilot 硬件压缩 | — |
| 内存 | LPDDR5X-9600、UFS 4.0 MCQ | 同 |

几点判断：
- **差异全部在 NPU 软件栈上。** [Notebookcheck 用 Reno16 Pro 实测](https://www.notebookcheck.net/New-chipset-brings-on-device-AI-to-Galaxy-S26-alternative.1382370.0.html)，CPU、GPU 相对上一代 SoC 机型都没有提升（媒体实测）。“能不能跑 Gemini Nano V3”现在取决于 Google 的认证和整机内存，媒体称需要 ≥12GB RAM。
- **带宽仍是 LLM 解码的硬约束。** LPDDR5X-9600 按 64-bit 推算峰值约 76.8GB/s（按规格推算，非官方）。投机解码和 INT4 都是在不加带宽的前提下提高 tok/s 的办法，所以联发科这次没有宣传 TOPS，宣传的是这些手段。
- **首发机型。** [荣耀 600 Pro 国行版](https://www.fonearena.com/blog/483611/honor-600-price-specifications-honor-600-pro-china.html)（5/25 发布）把海外版的 Snapdragon 8 Elite 换成“天玑 8550 Elite”。[OPPO Reno16 Pro](https://www.money.it/oppo-reno-16-e-reno-16-pro-ufficiale-il-lancio-ecco-i-nuovi-smartphone-con-intelligenza-artificiale)（5/25）加了实体 AI 键，一键笔记和 AI Mind Space 都从这里进入。两款机器都是 12GB 起步。

PC 侧，联发科 [5 月 19 日](https://www.mediatek.com/tek-talk-blogs/signal-65-investigates-the-architectural-advantage-of-the-mediatek-kompanio-ultra-910)转述了 Signal65 对 Kompanio Ultra 910 的测试。这颗芯片是 NPU 890、**50 TOPS**，配 11 核 Immortalis-G925。电池供电时性能只掉 6%，x86 Chromebook 掉 42%（厂商转述的第三方结论）。它的 TOPS 和 Intel Panther Lake NPU 5（官方 50 TOPS）、AMD Strix Point（50 TOPS）同档，是 Googlebook 形态的主力 Arm SoC。

财务方面，联发科 4 月 30 日的 Q1 法说会是背景信息：手机营收同比 −15%，管理层预计全年智能手机出货下滑约 15%，并把 AI ASIC 年营收目标上调到约 20 亿美元（[Futurum](https://futurumgroup.com/insights/mediatek-q1-fy-2026-earnings-driven-by-ai-asic-ramp-visibility/)、[Focus Taiwan](https://focustaiwan.tw:443/sci-tech/202604300022)）。所以中端芯片做“同硅片 + AI 软件升级”，是成本压力下的理性选择。

### 二、华为：韬(τ)定律与双层逻辑折叠

5 月 25 日，何庭波在上海 [IEEE ISCAS 2026 主旨演讲](https://www.huawei.com/cn/news/2026/5/ieee-iscas-tau-scaling)中提出“韬(τ)定律”，核心是用“时间缩微”取代几何缩微。下表把官方口径和媒体转述分开列：

| 层级 | 手段 | 官方/媒体口径 |
|---|---|---|
| 器件 | 降低晶体管与互连的 R、寄生 C | 官方 |
| 电路 | **逻辑折叠 LogicFolding**，由单层扩展到双层 | 官方；[IT之家](https://www.ithome.com/0/954/745.htm)转述“单层→双层” |
| 芯片 | 软件-架构-芯片协同，细粒度控制指令流和数据流 | 官方 |
| 系统 | 灵衢总线，跨超节点统一内存编址 | 官方 |
| 结果 | 同器件节点下密度 +55%、能效 +41% | 媒体转述论文摘要，官方新闻稿无数字 |
| 结果 | 约 238 MTr/mm²，性能核 +41%，频率 +12.7% | [Huawei Central](https://www.huaweicentral.com/huawei-kirin-2026-chip/) 转述，可信度中 |

官方给出的确定信息有三条：六年设计量产 381 款芯片；今年秋季的麒麟芯片首次完整采用逻辑折叠；预测 2031 年高端芯片密度达到等效 1.4nm。对端侧 AI 来说，同节点 55% 的密度增益如果兑现，可以用来放更大的 NPU MAC 阵列或片上 SRAM，这是缓解 LLM 解码带宽瓶颈最直接的办法。目前这些数字还没有第三方验证。

### 三、小米玄戒：迭代确认，规格仍是爆料

据[观察者网 5 月 18 日报道](https://www.guancha.cn/economy/2026_05_18_817486.shtml)，卢伟冰 5 月 16 日在直播中确认，小米今年“一定”推出玄戒迭代芯片，由一款旗舰首发。他同时否认“跳过 O2 直接叫 O3”，并说网传规格的可信度不高。爆料方面，这颗芯片仍用 TSMC 3nm（N3P），约 8 月上市（[Notebookcheck](https://www.notebookcheck.net/Upcoming-Xiaomi-XRing-O2-chipset-to-miss-out-on-2nm-process.1207362.0.html)）。参照基线是玄戒 O1：N3E 工艺，190 亿晶体管，6 核 NPU，44 TOPS。

### 四、PC：N1X 爆料密集，统一内存成焦点

[HotHardware 5 月 25 日](https://hothardware.com/news/lenovo-leak-points-nvidia-n1x-laptop-chip-ahead-computex)汇总了几条泄露：联想门户里出现 Legion 7 N1X 条目；Dell 16 OLED 搭载 N1X“ES2”工程样；闲鱼出现 N1 + 128GB 的工程主板。黄仁勋对台媒表示，这颗芯片与联发科共同设计。VideoCardz 的爆料表（[igor'sLAB](https://www.igorslab.de/en/nvidia-n1-n1x-windows-on-arm-chips-notebooks/) 转述）如下：

| 型号 | CPU | GPU | 功耗 | 内存上限 |
|---|---|---|---|---|
| N1X 675 | 20 核 (10+10) | 48 SM / 6144 CUDA | 45–80W | 128GB LPDDR5X |
| N1X 650 | 18 核 (9+9) | 40 SM / 5120 CUDA | 45–80W | 128GB LPDDR5X |
| N1 | 12 核 / 10 核 | 20 / 16 SM | 18–45W | 64GB LPDDR5X |

以上均为爆料，NPU TOPS 未披露。如果它沿用 GB10（DGX Spark：128GB、273GB/s）的统一内存设计，Arm 笔记本第一次有容量装下 70B 级 INT4 模型（容量推算）。不过 tok/s 主要由带宽决定。正式发布在 Computex（6 月期已覆盖）。

Intel 方面，Nova Lake 的 NPU 6 被爆料为约 74 TOPS（桌面版），Intel 未确认（[Guru3D](https://www.guru3d.com/story/intel-nova-lake-desktop-cpu-could-offer-tops-npu-for-local-ai/)）。AMD 的 Gorgon Point（55+ TOPS）和 Medusa（爆料 100 TOPS）仍停留在路线图阶段，窗口期内没有官方新品。

### 五、内存与份额：端侧 AI 的成本天花板

- **DRAM 涨价。** [TrendForce](https://www.trendforce.com/price/dram/mobileDram_contract) 4 月底到 5 月初预测 2Q26 手机 DRAM 合约价大涨：LPDDR4X +70–75%，LPDDR5X +78–83%。最终价格在 5 月下旬敲定；Samsung 一步到位调价，SK hynix 分步上调。内存在 BOM 中的占比已从 10–15% 升到 30–40%，高端机向 12GB 收敛，中端机回落到 8GB。这直接限制了端侧模型的可用内存。
- **SoC 份额。** Counterpoint 的 Q1 2026 数据：联发科 32%（后修订为 33%），同比从 38% 下滑；紫光展锐升至 14%（[Counterpoint](https://www.counterpointresearch.com/en/insights/global-smartphone-apsoc-market-share-quarterly)）。原因是内存短缺对入门和主流机的冲击最大。
- **LPDDR6。** SK hynix 的 1c LPDDR6 目标速率 14.4Gbps（比 LPDDR5X 的 10.7Gbps 高 33%），计划下半年量产（[TweakTown](https://tweaktown.com/news/112910/sk-hynix-will-start-lpddr6-mass-production-in-2026-for-xiaomi-smartphones/index.html)）。窗口期内没有量产新闻。

### 小结

这两周没有出现新的旗舰级 NPU，但方向很清楚。第一，端侧 LLM 的竞争从 TOPS 转到了软件手段（投机解码、INT4、LLM Booster）和内存容量，天玑 8550 就是“同硅片、换 AI 栈”的样本。第二，华为用逻辑折叠在受限工艺上找密度和能效，秋季麒麟会是第一个检验点。第三，PC 侧 N1X 把统一内存容量推到了 128GB 量级，接下来要看实际带宽和 Windows on Arm 的 NPU 软件生态。内存涨价是所有这些路线共同的成本上限。

## 4. 低功耗、存内计算与内存：眼镜与 MCU 进入 Transformer 时代

**判断**：5月15日~28日这两周，低功耗AI与存算一体领域没有出现“新一代旗舰芯片”式的发布（Embedded Vision Summit 5月11~13日、IMW 2026 5月10~13日都在窗口前），但有三条值得工程师记住的主线：**(1) 存算一体厂商开始“补数字短板、做完整系统”**——Mythic收购Videantis；**(2) 开源RISC-V NPU + 小模型下沉到1 TOPS级常开设备**——Google×Synaptics Coralboard跑Gemma 3 270M；**(3) AI眼镜进入主流生态，眼镜芯片的竞争点是“拍一张照片花多少电”而非TOPS**——Google I/O音频眼镜与国内安凯微、恒玄、炬芯的产品矩阵。存储侧本期无重大发布，LPDDR6/UFS 5.0/HBF的关键节点分别落在3月和6~8月。

### 一、存内计算：从“宏”走向“系统”

| 厂商 | 路线 | 关键口径 | 本期动态 |
|---|---|---|---|
| Mythic | 模拟CIM（Flash阵列） | 120 TOPS/W（含内存搬运，官方2025-12口径）；历史M1076为25 TOPS | 5月19日收购Videantis（金额未披露）[链接](https://www.edge-ai-vision.com/2026/05/mythic-acquires-videantis-to-build-the-worlds-most-energy-efficient-ai-compute-platform/) |
| 炬芯 ATS362X | SRAM CIM NPU（可穿戴音频） | 132 GOPS@500MHz；6.4 TOPS/W INT8，稀疏19.2 TOPS/W | 产业综述引用 [链接](https://www.36kr.com/p/3816031662382597) |
| Axelera Europa | 数字CIM（D-IMC） | 629 TOPS INT8，8个第二代AI核，64GB内存 | 官方称2026上半年出货（背景） |
| EnCharge AI | 模拟CIM（SRAM电容） | 宣称能效约20倍于数字芯片（媒体口径） | 2025-05发布EN100，本期无新动态 |

**Mythic + Videantis** 是本期最重要的存算新闻。模拟CIM最大的工程痛点是：矩阵乘以外的算子（前后处理、Softmax、LayerNorm、视频编解码、传统CV）无法在阵列里完成，必须回到数字域，系统能效被“阿姆达尔定律”拖累。Videantis的v-MP6000UDX是VLIW+SIMD同构多核阵列，可同时跑深度学习、传统视觉与视频编解码，累计出货超2500万颗、进入欧洲前三大车企的AEB摄像头。Mythic官方仍只给“比GPU高100倍”“能耗1%”的定性口径，**本次未披露任何新的TOPS/W、精度或模型规模**——这需要等首颗混合芯片的数据。

**国产SRAM-CIM已进入量产级消费芯片**：炬芯ATS362X的数字值得注意——6.4 TOPS/W（INT8）在MCU级NPU中属于高水平，稀疏后3倍提升到19.2 TOPS/W；但需注意，学术界数字SRAM-CIM宏已报道到数百TOPS/W（如ISSCC 2026的16nm 444.21 TOPS/W宏），宏级与芯片级、稀疏与稠密、1-bit归一与INT8之间不可直接比较。窗口前的IMW 2026（鲁汶）专门开设了“基于忆阻器的CiM神经网络加速”教程，说明非易失CIM仍是存储器社区的热点。

### 二、MCU/常开NPU：Transformer开始进入1 TOPS档

**Google×Synaptics Coralboard**（5月19日，Google I/O）把Google开源的Coral NPU第一次以开发板形态交给开发者：Astra SL2619双核@2GHz、2GB DDR4、Torq NPU子系统1 TOPS且“支持CNN与Transformer”，Gemma 3 270M有硬件加速支持 [来源](https://www.edge-ai-vision.com/2026/05/google-research-and-synaptics-partner-to-showcase-immersive-edge-ai-experiences-powered-by-the-coralboard-at-google-i-o-2026/)。Coral NPU IP本身的设计目标是256 MACs/cycle、512 GOPS、约6mW（22nm，Google与VeriSilicon对频率口径分别为1GHz/800MHz）[来源](https://developers.google.com/coral/guides/intro-coralNPU)。其意义在于：**RISC-V RVV 1.0向量单元+外积矩阵单元**的组合可以在NPU内完成Attention相关算子，而传统Ethos-U55类NPU主要面向CNN。

MCU级NPU的横向坐标（均为厂商/第三方汇总口径，测试方法不同）：

| 器件 | NPU | 算力口径 |
|---|---|---|
| ST STM32N6 | Neural-ART | 600 GOPS@1GHz |
| Renesas RA8P1 | Ethos-U55 | 256 GOPS |
| Infineon PSOC Edge E84 | Ethos-U55 | 约0.3 TOPS |
| NXP MCX N94x | eIQ Neutron | 约5 GOPS级 |
| Nordic nRF54LM20B | Axon（收购Atlazo） | 对比CPU快15倍、能效高8倍 |
| TI MSPM0G5187 / AM13Ex | TinyEngine | embedded world 2026发布 |
| 炬芯 ATS362X | SRAM-CIM | 132 GOPS，6.4 TOPS/W |
| Synaptics Coralboard | Torq（Coral NPU） | 1 TOPS，支持Transformer |

正如[选型指南](https://www.utmel.com/blog/categories/microcontrollers/mcu-with-built-in-npu-how-to-pick-an-edge-ai-microcontroller-in-2026)所提醒，同一个Ethos-U55在不同厂商口径下差异巨大，评估时应看目标模型的实测延迟与每次推理能耗（µJ/inference），而非标称TOPS。

### 三、AI眼镜/可穿戴：指标从TOPS转向“mAh/次”

- **Google I/O音频眼镜**（5月19日）：Samsung做硬件、Gentle Monster与Warby Parker设计，带摄像头、无显示，今秋上市，可配iPhone；媒体称芯片来自Qualcomm但未披露型号 [VR.org](https://vr.org/articles/google-io-2026-xr-recap)。从可配iPhone、手机侧Android Halo来看，Gemini主推理仍在手机/云端。
- **安凯微**（集微峰会，5月27~29日）：“孔明”视觉SoC 0.5~8 TOPS，AnyCloud39AV200方案单次拍照低至0.08mAh、冷启动150ms [来源](https://news.10jqka.com.cn/20260530/c677097052.shtml)。
- **产业综述**（5月19日）：Qualcomm骁龙可穿戴平台至尊版（3月发布，3nm，Hexagon NPU+eNPU）端侧最高2B参数、首token 0.2s、最高10 tokens/s；瑞芯微RK182X支持3B/7B、RK1860 >40 TOPS支持13B；恒玄6nm自研眼镜SoC，BES6000上半年送样 [36氪](https://www.36kr.com/p/3816031662382597)。
- **成本**：带显示眼镜光学近一半、主控两到三成 [同花顺](https://news.10jqka.com.cn/20260527/c676993825.shtml)。

工程含义：当单次拍照能耗被压到0.08mAh量级（厂商口径），拍照本身不再是续航主因，**常开语音唤醒（mW级以下）与无线回传**才是剩余大头——这也是Syntiant NDP、Nordic Axon等亚mW~mW级常开推理芯片的位置。

### 四、边缘加速器与系统

- **SiMa.ai × Emerson**（5月26日）：MLSoC进入Emerson加固IPC（-40~70°C），面向油气泄漏、火炬监测、气隙核电/水务 [新闻稿](https://finviz.com/news/356977/emerson-and-simaai-deliver-physical-ai-intelligence-to-the-industrial-edge)。背景：Modalix为6nm、50 TOPS（BF16/INT8/INT16）、<10W、128-bit LPDDR5-6400，可2/4芯级联至100/200 TOPS [产品简报](https://sima.ai/wp-content/uploads/2025/09/SiMa_MLSoC_Modalix_Product-Brief_09-09-25.pdf)。
- **DeepX DX-M2**（背景，CES 2026口径）：80 TOPS@<5W、LPDDR5X 153.6GB/s，宣称可跑最高100B参数LLM，计划Samsung 2nm；5月29日韩媒报道其将在Computex宣布量产合作，已不在本期窗口。
- **Samsung Foundry × Cadence**（5月28日）：SF5A车规工艺上的物理AI chiplet原型，AI chiplet可平铺扩展TOPS，但未披露数字与互连 [来源](https://www.edge-ai-vision.com/2026/05/samsung-foundry-and-cadence-accelerating-chiplet-solutions-for-physical-ai/)。
- **ADI收购Empower**（5月19日，15亿美元现金）：IVR+硅电容的垂直供电，先服务数据中心，对高功率边缘SoC的瞬态供电有参考意义 [来源](https://www.edge-ai-vision.com/2026/05/analog-devices-to-acquire-empower-semiconductor-expanding-its-next-generation-high-density-power-portfolio-for-the-ai-era/)。

### 五、内存与存储：窗口内无大发布，节奏梳理

| 技术 | 关键数字 | 时间点 |
|---|---|---|
| SK hynix LPDDR6（1c） | 16Gb，≥10.7Gbps，速度+33%、能效+20%（对LPDDR5X），下半年量产 | 3月发布 [TrendForce](https://www.trendforce.com/news/2026/03/10/news-sk-hynix-develops-1c-lpddr6-dram-with-33-speed-gain-20-power-savings-ships-in-2h26/) |
| Samsung LPDDR6 | 12nm级，初始10.7Gbps，下半年目标 | 媒体口径 |
| HBF（高带宽闪存） | 2月25日OCP工作组启动；8月FMS发布规范：单堆栈最高512GB、0.4~3.0TB/s、UCIe | 不在本期 |
| UFS 5.0 | Samsung 10.8GB/s（6月）；Kioxia 512GB/1TB样品（7月） | 不在本期 |
| LPDDR5X-PIM | Samsung Hot Chips 2026披露：Llama 3.1 8B 5.4s vs 12.3s | 8月，不在本期 |

对端侧LLM而言，decode阶段带宽决定tokens/s：LPDDR5X-8533 64-bit约68GB/s，LPDDR6 10.7Gbps在同等位宽下约提升33%；而PIM/HBF分别从“减少搬运”和“扩大容量”两端绕开带宽墙。Micron 5月1日的机器人内存博客给出人形机器人16~128GB LPDDR5/5X、1~4TB NVMe的配置口径，可作为端侧VLA内存需求参考。

### 六、窗口前后的相关背景（不计入本期条目）

- **Embedded Vision Summit 2026**（5月11~13日，圣克拉拉）：90场报告、四个分会场，主题集中在物理AI、从原型到量产、处理器选型与模型优化；Micron讲“具身智能的内存”，Lattice讲“远端边缘的高效视觉”，Aion Silicon讲RISC-V从数据中心到边缘的算力架构 [项目公告](https://embeddedvisionsummit.com/?p=28013)。下一届将提前到2027年2月2~4日在旧金山举办。
- **FotoNation × SEMIFIVE**（5月11日）：TriSilica多模态感知AI芯片（音频、毫米波、光谱、红外、RGB融合）选用Samsung 8LPU，首颗TS-210计划年底上MPW，强调“大容量键合内存”，TOPS未披露。
- **Renesas收购Irida Labs**（5月14日）：把PerCV.ai视觉软件并入RA MCU/RZ MPU与Renesas 365云开发平台，说明MCU厂商的竞争正从NPU硬件转向“模型+工具链+参考应用”的交付能力。
- **Ambiq Q1财报**（5月12日）：净销售额同比增长59.3%，并披露12nm SPOT平台将用于下一代Atomiq SoC——亚阈值/近阈值低功耗路线首次迈向12nm先进节点。
- **Synaptics Astra SR80**（3月10日发布，5月18日博客转载）：Cortex-M33 + 自研NPU + HiFi 5 DSP的常开音频AI MCU，面向AI耳机、会议设备，算力与功耗数字未公开。

### 七、给工程师的评估建议

1. **算力口径统一到“目标模型实测”**：MCU级NPU的GOPS/TOPS差异往往来自频率、稀疏、位宽与是否计入内存搬运；建议以“目标网络单次推理延迟 + µJ/inference + 峰值SRAM占用”三项作为对比基准。
2. **存算一体看“系统能效”而非“宏能效”**：宏级数百TOPS/W到芯片级个位数~百位数TOPS/W之间，差距来自ADC/DAC、外围数字逻辑、片外搬运；Mythic补数字处理器、炬芯ATS362X报告芯片级6.4 TOPS/W，都应放在这一框架下理解。
3. **Transformer支持是新分水岭**：Coral/Torq这类可在NPU内处理Attention的设计，比只覆盖卷积的NPU更适合跑Gemma 270M这类小语言模型；选型时需确认Softmax、LayerNorm、GELU等算子是否回退CPU。
4. **可穿戴看事件驱动能耗**：AI眼镜/耳机应关注常开唤醒功耗、单次拍照能耗与冷启动时间、无线回传能耗，三者共同决定续航，单看NPU TOPS意义有限。
5. **内存决定LLM上限**：协处理器方案（RK182X/RK1860、DeepX DX-M2）的可运行模型规模由独立内存容量与带宽决定；明年LPDDR6与LPDDR5X-PIM量产后，端侧7B~13B模型的tokens/s会出现阶跃。

### 小结

本期的信号是“系统化”而非“堆TOPS”：存算一体公司通过并购补齐数字处理（Mythic），开源RISC-V NPU把Transformer推理带到1 TOPS/毫瓦级（Coral），AI眼镜芯片用单次拍照能耗与冷启动时间来定义竞争力（安凯微），国产可穿戴SoC已把SRAM-CIM做进量产（炬芯ATS362X，6.4 TOPS/W INT8）。需要警惕的是：本期多数公告**没有披露TOPS/W、精度或可运行模型规模**（Mythic、SiMa×Emerson、Google音频眼镜芯片均为“未披露”），真正可比较的数据要等Computex（5月31日起）、VLSI 2026（6月）与Hot Chips 2026（8月）。

## 5. 顶会论文：MLSys 2026 的端侧推理

5 月下半月的顶会论文几乎全部来自 [MLSys 2026](https://mlsys.org/Conferences/2026)（5 月 18–22 日，Bellevue）。与往年“数据中心服务系统”一统天下不同，今年端侧议题明显上桌：Meta 的 [ExecuTorch](https://proceedings.mlsys.org/paper_files/paper/2026/hash/236f915dd02af4f11927f67330b21d4b-Abstract-Conference.html) 进入 Best Paper Session 并获最佳工业论文，周四专门有 “Efficient ML” 场次讨论手机 DVFS 与全整数 attention，周五 NVIDIA 工业轨讲“小显存跑 235B MoE”。我们的判断是：**端侧 AI 的瓶颈已从“算子跑得快不快”转向“系统层是否协同”——NPU 图覆盖率、跨 CPU/GPU/DDR 的调频、KV Cache 与 softmax 等“非 GEMM”路径，成为新的性能杠杆。**

### 会期核对：哪些会落在窗口内

| 会议 | 2026 日期 | 是否在 5/15–5/28 窗口 |
|---|---|---|
| MLSys 2026 | 5 月 18–22 日，Bellevue | 是（主体） |
| ISCAS 2026 | 5 月 24–27 日，上海 | 是 |
| FCCM 2026 | 5 月 13–16 日，Atlanta | 部分重叠，未检索到可确认的端侧 LLM 论文 |
| CICC 2026 | 4 月 19–22 日，Seattle | 否 |
| ISPASS 2026 | 4 月 26–28 日，首尔 | 否（KU Leuven 1.58bit LUT 加速器获最佳论文，仅作背景） |

论文日期按 [MLSys 官方日程](https://mlsys.org/virtual/2026/calendar)中的宣讲场次标注。从场次安排看，端侧相关论文分布在四天里：周二（5/19）Best Paper Session 有 ExecuTorch 与 LEANN；周三（5/20）“LLM Serving 3”集中讨论 KV Cache（SkipKV、Kitty），“Model Compression”场有 HyperTinyPW、ScaleSearch、Shannonic；周四（5/21）“Efficient ML”场由 Vijay Janapa Reddi 主持，收录 IntAttention 与 CORE，工业轨则有华为 ProfInfer 与 Groq SHIP；周五（5/22）工业轨“Compilers/HW”收录 NVIDIA 客户端推理与 SambaNova 数据流论文。

### 本期论文速览

| 日期 | 论文 | 机构 | 方向 | 平台 |
|---|---|---|---|---|
| 5/19 | ExecuTorch | Meta | 端侧部署框架 | S25 Ultra / Pixel 9 Pro XL / iPhone 15 Pro / Pico 2 |
| 5/19 | LEANN | UC Berkeley 等 | 端侧 RAG 索引 | RTX 4090、M1 Mac |
| 5/20 | Kitty | Together AI 等 | 2bit KV 量化 | A100/H100 |
| 5/20 | SkipKV | Intel Labs 等 | 推理模型 KV 压缩 | 未强调端侧 |
| 5/20 | Locality-Aware Beam | 台湾大学 | 消费级 GPU TTC | RTX 4090 |
| 5/20 | HyperTinyPW | 独立研究者 | MCU 压缩 | MCU |
| 5/20 | ScaleSearch | Cornell/Together AI | NVFP4 缩放 | GPU |
| 5/20 | Shannonic | 多伦多大学 | 无损张量压缩 | 端云协同 |
| 5/21 | IntAttention | 南科大 | 全整数 attention | RK3588S2、Apple M2 |
| 5/21 | CORE | 上海交大/Purdue | 手机 DVFS | Pixel 7 / 7 Pro |
| 5/21 | ProfInfer | 华为 | 端侧推理剖析 | Orange Pi 5 Ultra |
| 5/21 | SHIP | Groq | SRAM 推理集群 | 数据中心 |
| 5/22 | pipelined sharding | NVIDIA | 客户端显存受限推理 | RTX 5090 等 |
| 5/22 | 归因稀疏激活 | 匹兹堡大学 | 稀疏激活 | H100 |
| 5/22 | Dataflow Is All You Need | SambaNova | 数据流解码 | SN40 RDU |
| 5/24–27 | 脉冲 Transformer 加速器 | 西湖大学 | 具身智能芯片 | 未披露 |

可以看到，真正在手机/嵌入式实机上测量的论文只有 ExecuTorch、CORE、IntAttention、ProfInfer 四篇，其余多以 GPU 为平台、以端侧为动机。这本身就是一个信号：学术界获取手机 NPU 的可编程接口仍然困难，CORE 甚至需要 root 并拆机直连电源才能拿到 0.2 ms 精度的功耗曲线。

### 一、端侧部署框架：NPU 的“图覆盖率”决定实际吞吐

ExecuTorch 论文给出了少见的同机横评（Galaxy S25 Ultra / Snapdragon 8 Elite，框架版本截至 2026-03-31）：

| 模型（4bit 权重） | 后端 | Prefill tok/s | Decode tok/s |
|---|---|---|---|
| Llama 3.2 1B | ET QNN（Hexagon NPU） | 2813–2977 | 46.5–46.6 |
| Llama 3.2 1B | 高通 QAIRT（NPU） | 2278–2392 | 52.0–52.7 |
| Llama 3.2 1B | llama.cpp（NPU 路径） | 330–374 | 23.6–25.6 |
| Llama 3.2 1B | ET XNNPACK（CPU，GS32） | 525–529 | 65.9–67.1 |
| Phi-4 Mini 3.8B | ET QNN（NPU） | 1161–1229 | 18.1–19.6 |

几点工程结论：(1) NPU 的优势集中在 prefill（比 CPU 高约 5 倍），decode 仍受带宽限制，甚至不如 CPU；(2) ExecuTorch 用 group-wise 量化 prefill 更快、decode 略慢于高通 per-channel 的 QAIRT，说明量化粒度会直接影响 NPU 的 decode 带宽效率；(3) 论文明确指出 LiteRT 与 ONNX Runtime 的 NPU EP 只“认领”少量节点，大部分仍回落 CPU——**端侧 NPU 的竞争正在变成编译器与算子覆盖率的竞争**。在 MCU 端，ExecuTorch 运行时本体仅 13–26 KiB，在 Pico 2 上 INT8 模型总 RAM 约 11 KiB，覆盖 0.01–800 W 的功耗区间（官方口径）。

### 二、SoC 级能效：DVFS 协同与全整数 attention

上海交大与 Purdue 的 [CORE](https://proceedings.mlsys.org/paper_files/paper/2026/hash/136b9a13861308c8948cd308ccd02658-Abstract-Conference.html) 用 Monsoon 电源在 Pixel 7（Tensor G2 + Mali-G710 MP7）上实测，揭示了一个被忽视的事实：即便是 GPU 推理，llama.cpp 的 OpenCL 运行时也要 CPU 持续派发 kernel（Mali 硬件队列只有 2 个在途条目），而 Android 的 CPU/GPU/内存 governor 各自决策。结果是默认策略比最优频点组合延迟高 23.0–40.4% 或能耗高 5.0–16.6%；CORE 在不增加能耗的前提下把 TPOT 降低 27.8–39.6%。这对 SoC 厂商的启示是：**LLM 需要专属的“跨 IP 调频档位”**，而不是沿用为图形负载调参的 governor。

南科大的 [IntAttention](https://proceedings.mlsys.org/paper_files/paper/2026/hash/ea5ffdf7da91256ecd2770f9fd2dade9-Abstract-Conference.html) 则量化了“GEMM 量化后的下一个瓶颈”：INT8 GEMM 后，softmax 相关路径占 attention 时间 57–65%。其 IndexSoftmax 用 32 项 UINT8 查找表（32 B）实现全整数 softmax，在 RK3588S2 上较 FP16 加速 2.1–3.7×、能耗降至 39.18%，在 Apple M2 上加速 2.4–2.8×。对缺少高吞吐 FP 单元的低功耗 NPU/DSP，这类全整数数据流比“加大 FP16 单元”更划算。

### 三、内存墙：KV Cache、显存与存储

| 论文 | 对象 | 关键数字 |
|---|---|---|
| [Kitty](https://proceedings.mlsys.org/paper_files/paper/2026/hash/e4d8d1b5120be349d3fff8878650cf45-Abstract-Conference.html) | 2bit KV + 12.5–25% 通道 INT4 | KV 内存约降 8×，吞吐 2.1–4.1× |
| [SkipKV](https://proceedings.mlsys.org/paper_files/paper/2026/hash/45c1f6a8cbf2da59ebf2c802b4f742cd-Abstract-Conference.html) | 推理模型句级 KV 驱逐 | 精度最高 +26.7%，生成长度最多缩短 1.6×，吞吐 1.7× |
| [Locality-Aware Beam](https://proceedings.mlsys.org/paper_files/paper/2026/hash/c74b624843218d9b6713fcf299d6d5e4-Abstract-Conference.html) | RTX 4090 上 TTC beam search | KV 传输减少 >95%，加速 3.39–9.72× |
| [NVIDIA pipelined sharding](https://proceedings.mlsys.org/paper_files/paper/2026/hash/7cd265ae802235b8d5778a4a96ff22dd-Abstract-Conference.html) | 客户端显存受限推理 | 2G 显存跑 Qwen3-235B 达 7.7 TPS；TPS 最高 30× |
| [LEANN](https://proceedings.mlsys.org/paper_files/paper/2026/hash/e27ea0cd50b798ff8942caf9203f0992-Abstract-Conference.html) | 个人设备 RAG 索引 | 索引最多缩小 50×，约为原数据 5% |
| [Shannonic](https://proceedings.mlsys.org/paper_files/paper/2026/hash/96f39c8de84678cb2a908cd52bfd7819-Abstract-Conference.html) | 张量无损压缩 | 状态仅 530 B，距香农极限 1% 以内 |

NVIDIA 的工作最值得 AI PC 关注：它把显存优先级定为 attention > KV > FFN > 输出，MoE 专家主要留在系统内存由 CPU 计算——Qwen3-235B-A22B（Q2_K，77 GB）只用约 5% 体积的显存（4G）即可在 16K 上下文跑出 6.7 TPS。这与统一内存 SoC 上的“专家卸载”是同一问题的两种形态。推理模型的普及让 KV 取代权重成为新的内存大户，Kitty 和 SkipKV 分别从“每个 KV 更小”和“少存 KV、少生成 token”两个方向下手。

具体到端侧：匹兹堡大学论文指出多数手机只有 6–8 GB 共享内存，旗舰机（如 ExecuTorch 测试用的 S25 Ultra）也仅 16 GiB；权重经 4bit 量化后已大幅压缩，而推理模型动辄生成数千 token 的思维链（Kitty 评测生成到 8192 token），KV 随之线性增长。Kitty 的结论是“只给 12.5%–25% 的 Key 通道保留 INT4，其余 2bit”即可基本回到 FP16 精度，而且通过把混合精度页拆成两个统一 2bit 张量，避免了不规则访存——这种布局对端侧 NPU 的 DMA 同样友好。SkipKV 则提醒，token 级驱逐会让模型“反复复核”，反而生成更长的序列，在端侧意味着更多能耗；按句子粒度删除冗余推理才能同时减少 KV 和生成长度。台湾大学的 beam 调度工作把测试时计算（TTC）引入消费级硬件的讨论：多条 beam 共享前缀，只要按局部性分组调度，KV 传输量可减少 95% 以上。

华为的 [ProfInfer](https://proceedings.mlsys.org/paper_files/paper/2026/hash/03dbc11a22e79cd38bea53cf518c2371-Abstract-Conference.html) 从另一个角度补位：用 eBPF 对 llama.cpp 做非侵入式算子级剖析，运行时开销低于 5%，可以直接看到逐算子的内存带宽占用，判断负载是访存受限还是计算受限。对正在把推理引擎移植到自研 NPU 的厂商来说，这种工具比单一的 tok/s 数字更有用。

### 四、低比特格式与稀疏

[ScaleSearch](https://proceedings.mlsys.org/paper_files/paper/2026/hash/633b0e871a48d542280c3ad03928e60d-Abstract-Conference.html) 指出微缩放格式按块最大值取 scale 并非最优，利用 FP8 scale 的尾数位搜索可把 NVFP4 量化误差降低 27%，Qwen3-8B PTQ 在 MATH500 上最多提升 15 分——随着端侧 NPU 引入 FP4/MX 格式，这是零硬件成本的精度红利。匹兹堡大学的[归因稀疏激活](https://proceedings.mlsys.org/paper_files/paper/2026/hash/29591f355702c3f4436991335784b503-Abstract-Conference.html)以手机 6–8 GB 内存为动机，在 70% 稀疏度下精度损失 <5%、内存 -40%（H100 实测，端侧数据未披露）。MCU 端，[HyperTinyPW](https://proceedings.mlsys.org/paper_files/paper/2026/hash/2d04d97593c8c33d415337f408ed0e1b-Abstract-Conference.html) 用“存生成器不存权重”让 225 kB 模型接近 1.4 MB CNN 的效果。

### 五、数据中心架构的端侧参照

[Groq SHIP](https://proceedings.mlsys.org/paper_files/paper/2026/hash/9c20f16b05f5e5e70fa07e2a4364b80e-Abstract-Conference.html) 首次系统披露纯 SRAM 推理集群（每日数千亿 token，作者现署名 NVIDIA）；[SambaNova](https://proceedings.mlsys.org/paper_files/paper/2026/hash/f502981cbe221d857ad409450a7917c3-Abstract-Conference.html) 称 GPU 解码只用到约 21% 可用带宽，而 SN40 RDU 可达屋顶线 75% 以上。两者共同指向：decode 的瓶颈在“带宽利用率与调度开销”，与 ExecuTorch 中 NPU decode 不如 CPU 的现象同源。ISCAS 2026 上，西湖大学的[脉冲 Transformer 加速器](https://cenbrain.westlake.edu.cn/info/1017/1663.htm)面向具身智能，能效最高提升 10.9×（工艺与功耗未披露）。

### 六、对芯片与终端厂商的启示

**其一，NPU 指标需要从“峰值 TOPS”转向“端到端图覆盖”。** ExecuTorch 的横评中，同一颗 Hexagon NPU 在不同框架下 prefill 相差约 8 倍，差距主要来自有多少节点真正被下发到 NPU。芯片厂商若只提供闭源 SDK 而缺乏 PyTorch 原生的 delegate，开发者很可能在 CPU 上“默默回落”。MediaTek、Samsung Exynos、NXP 等后端仍处于开发中（论文口径），意味着 Android 阵营的 NPU 软件生态在 2026 年中仍明显不均衡。

**其二，decode 阶段仍是带宽与调度问题。** NPU 上 1B 模型 decode 约 46 tok/s，甚至低于 CPU 的 66 tok/s；CORE 证明 GPU 推理同样被 CPU 派发与频点协同拖累；SambaNova 则在数据中心给出“GPU 只用到约 21% 带宽”的佐证。下一代端侧 NPU 需要更强的自主调度能力（片上循环、命令队列深度）与更高的 DDR 利用率，而不是单纯堆 MAC。

**其三，低比特格式向注意力与 KV 延伸。** IntAttention 用 32 B 查找表替代浮点指数，Kitty 把 KV 推到 2bit，ScaleSearch 优化 NVFP4 缩放因子——这些都意味着 NPU 需要在 softmax、反量化、混合精度 KV 读取上提供专门的数据通路，否则“量化后的非 GEMM 部分”会吞掉量化收益。

**其四，存储与内存分层成为一等公民。** NVIDIA 的显存优先级策略、LEANN 的“以算换存”、Shannonic 的 530 B 状态熵编码，都把端侧问题从“算得动”转为“放得下、搬得动”。对统一内存的手机与 AI PC，这类分层放置策略可以直接迁移到 NPU 本地 SRAM 与 DDR 之间。

### 小结

1. **软件栈决定 NPU 实际价值**：同一颗 Hexagon，不同框架 prefill 相差约 8 倍。
2. **非 GEMM 路径成为新瓶颈**：softmax（57–65%）、CPU 调度、DVFS 协同都在吃掉量化带来的收益。
3. **KV Cache 是推理模型时代的内存主角**：2bit KV、句级驱逐、局部性调度与显存分层放置是端侧长上下文的必修课。
4. 窗口内 CICC、ISPASS、ICLR 已提前结束，FCCM 仅部分重叠；6 月的 ISCA/VLSI/MobiSys 将提供更多芯片级数据。

## 6. 5 月下半月 arXiv 端侧硬件论文精选

5 月下半月（5/15–5/28）的 arXiv 端侧 AI 硬件论文有一个很清晰的主线：**端侧 LLM 的瓶颈正在从「算力够不够」转向「字节从哪里来、搬得动不动」**。一方面，多篇论文在真实手机上证明 Hexagon NPU 并非处处更快、更省电；另一方面，MoE 与「闪存当内存」成为把 8B~14B 甚至更大模型塞进 12~16GB 手机的主流路径，从软件路由（ReMoE）、投机解码（Lever）、模型结构（MobileMoE、Dense2MoE）一直延伸到 3D NAND 存内计算（NASiC）。

### 一、手机 NPU：真实测量开始「祛魅」

莱顿大学的 [When NPUs Are Not Always Faster](https://arxiv.org/abs/2605.27435) 是本期最值得硬件架构师读的一篇。作者在 Snapdragon 8 Gen 3（Hexagon v75，HTP 含 HVX/HMX）、16GB 内存的 Android 15 手机上，用 llama.cpp（b7588）跑 Llama-3.2-3B、Llama-3.1-8B、Qwen3-4B/8B（Q4_0），并用 OPMASK 方法把 NPU 路径拆成通信、量化、计算三部分：

| 阶段 | NPU 算子级 | 端到端 | 备注 |
|---|---|---|---|
| 预填充 | MUL_MAT 比 6 核 CPU 慢 1.27~1.62× | CPU 最多快 1.6× | 通信占 NPU 时间 0.2%~3.2% |
| 解码 | MUL_MAT 快 1.55~1.67× | 仅快 1.05~1.20× | 通信占 9.9%~13.0% |
| 能耗 | — | 全卸载耗电 +22%/+32%/+51% | 约 321/641/1281 token 提示 |

轻量算子在 NPU 上的调用时间是计算时间的 8~22 倍，FLASH_ATTN_EXT 等回退到 CPU 后还比原生 CPU 慢 1~1.5 倍。需要注意：这是**开源 llama.cpp Hexagon 后端**下的结论，并不等于 QNN/厂商私有栈的上限，但它清楚地指出了 NPU 的三处短板——调度开销、算子覆盖与解码数据通路。

与之形成对照的是 [Quant.npu](https://arxiv.org/abs/2605.20295)：它从量化格式入手迎合 NPU 约束（整数、静态、粗粒度）。论文给出 Hexagon 上 W4A8 per-tensor 比 W4A16 per-block 快约 20% 的观察，并在 SM8650 上相对 ExecuTorch-W4A16 最多提速 15.1%。附录在 SM8750（Snapdragon 8 Elite）上给出了少见的完整表格：Qwen2.5-3B 预填充 969.72 tok/s（ExecuTorch 808.10），SmolLM2-1.7B 达 1612.78 tok/s，峰值内存从 2216 MB 降到 1876 MB；**但解码速度与基线完全相同**（3B 约 21~29 tok/s），再次说明解码受带宽而非 NPU 格式限制。两篇合读的结论是：NPU 的价值主要在预填充，且前提是软件栈与量化格式真正贴合硬件。

背景上，2024 年的 [PowerInfer-2](https://arxiv.org/pdf/2406.06282) 与 [llm.npu](https://arxiv.org/html/2407.05858v2) 曾报告 NPU 预填充可达 1000 tok/s 级别；本期论文把这一结论细化为「只在合适的栈与格式下成立」。

### 二、闪存当内存：投机解码与路由改造

当模型超过手机 DRAM，权重只能留在 UFS。清华的 [Lever](https://arxiv.org/abs/2605.16786) 量化了这个代价：OnePlus 12 上 Qwen3-14B 一次验证 2108.3 ms，其中闪存 I/O 占 1967.1 ms（93.3%）。Lever 让小 draft 模型常驻 DRAM、闪存中的目标模型一次验证多个 token，并在 CPU-NPU 上做混合执行，在 OnePlus 12 与两款 Snapdragon 8 Elite 荣耀机型上实现几何平均 2.93 倍于闪存自回归、1.50 倍于链式投机解码的加速。但绝对速度仍然很低：Qwen3-8B 全闪存驻留时约 1.75 tok/s，全部驻留 DRAM 时约 3.40 tok/s。

北航与华为的 [ReMoE](https://arxiv.org/abs/2605.27081)（ICML 2026）则从模型侧下手：微调路由使其偏向近期专家，专家复用提升 26%，在 Jetson Orin NX 16GB + NVMe SSD 的 llama.cpp 上 TPOT 降低 43.6%~49.8%（1.77~1.99 倍解码加速）。它与 Lever 共同说明：**端侧大模型的关键硬件指标是 UFS/SSD 随机读带宽与 DRAM 容量，而非 NPU TOPS**。

### 三、MoE 成为端侧模型形态的新默认

Meta 的 [MobileMoE](https://arxiv.org/abs/2605.27358) 给出端侧 MoE 缩放律（中等稀疏 + 细粒度专家 + 共享专家），并在 Galaxy S25 与 iPhone 16 Pro 的 CPU（ExecuTorch+XNNPACK，INT4 权重/INT8 动态激活）上实测：

| 模型 | INT4 权重 | 14 项均分 | S25 解码 tok/s（256 / 8k） | iPhone 16 Pro 解码 tok/s（256 / 8k） |
|---|---|---|---|---|
| MobileLLM-Pro（稠密） | 0.55 GB | 45.5% | 61.3 / 10.6 | 61.0 / 10.6 |
| MobileMoE-S | 0.68 GB | 44.0% | 138.1 / 25.8 | 204.6 / 32.2 |
| MobileMoE-M | 1.48 GB | 52.5% | 83.6 / 15.4 | 106.8 / 17.2 |
| MobileMoE-L | 2.75 GB | 57.8% | 53.4 / 8.9 | 59.4 / 10.8 |

港中文（深圳）与理想汽车的 [Dense2MoE](https://arxiv.org/abs/2605.26496) 则把稠密模型剪掉冗余注意力、把 MLP 升级为专家，在 Jetson Thor-U 上把总时延从 307.5 ms 降到 271.0 ms，并强调车载统一内存需与传感器融合、规划共享 LPDDR，因此专家数需要硬件感知地控制（3.32 GB→5.31 GB 的扩展几乎无精度收益）。

硬件侧最激进的是北大的 [NASiC](https://arxiv.org/abs/2605.23294)（DAC 2026）：直接在 3D NAND 中用 CAM 掩码完成「选专家 + 算专家」，架构级评估显示性能 4~114.8 倍、能效 3.9~70 倍于既有设计。它与 Lever/ReMoE 是同一问题的软硬两端解法。

### 四、能耗测量与新型存储：口径决定结论

[The Energy Blind Spot](https://arxiv.org/abs/2605.27599) 审计了 GB10 架构的 ASUS Ascent GX10：除 NVML 的 GPU 瞬时功率外没有任何 CPU/电源轨能耗遥测，进程级能耗归因无法像 x86 RAPL 那样实现。对端侧 AI 的「J/token」评测而言，这是一个容易被忽略的方法学风险。[Memory-Bound but Not Bandwidth-Limited](https://arxiv.org/abs/2605.30571) 则在 batch-1 解码上测得 L4 达到内存下限约 81%、H100 只有约 27%，且 L4 上 bnb-nf4 / AWQ+Marlin 量化路径几乎拿不到理论 4 倍收益（62.32→59.36/45.24 ms/step），只有调优的 GPTQ+ExLlamaV2 达到 17.36 ms/step——「量化省带宽」必须由内核兑现。

存内计算方向，[FCDC](https://arxiv.org/abs/2605.28208) 以 HZO 铁电电容做非易失电荷域注意力，仿真显示每 token 能耗对单用户 GPU 低 18~35 倍，但对优化服务基线仅 1.4~4.7 倍，作者也坦承 MAC 能效只与开关电容 SRAM CIM 持平，收益来自非易失与 KV Cache 常驻（属纯仿真，置信度低）。

### 五、更宽的端侧形态：浏览器、GUI 智能体、IoT 集群与安全

- [LlamaWeb](https://arxiv.org/abs/2605.20706)：llama.cpp 的 WebGPU 后端，16 台设备/8 家厂商评估，内存少 29%~33%、解码吞吐高 45%~69%；Apple M3 上 Llama 3.2 1B 解码 89.9% 时间在 GEMV。
- [MobileExplorer](https://arxiv.org/abs/2605.26546)：Galaxy S24 上 2B VLM（MAI-UI-2B，Q8）单步约 40 秒，通过并行 UI 探索把步数与时延降 23%——端侧 VLM agent 离流畅仍远。
- [CATS](https://arxiv.org/abs/2605.15694)：16 颗 nRF52840（Cortex-M4）经 BLE 物理层协同运行 14M 参数 ViT，为单设备容量的 14 倍。
- [LLMForge](https://arxiv.org/abs/2605.17653)：硬件感知 NAS，ring 边缘加速器上能效版每 token 能耗 −40%、时延版 TTFT/TPOT −43%。
- [Speed Kills](https://arxiv.org/abs/2605.17707)：7 种边缘 AI 加速器中 6 种存在混淆代理攻击，影响 128+ SoC、1 亿+ 设备（CVE-2025-66425）。

另有两篇同期上传、已被 ISCA 2026 接收的预印本值得一提（会议本身在 6 月覆盖）：KAIST 的 [Cassandra](https://arxiv.org/abs/2605.26558) 用剪枝 + 尾数截断构造免训练自投机 draft，最高 2.41 倍于 BF16；[EVA](https://arxiv.org/abs/2605.24144) 把向量量化解码的 GEMV 变为 GEMM，相对查表架构最高 11.17 倍提速、7.17 倍能效。

### 六、端侧模型容量速查（均为论文实测口径）

| 论文 | 平台 | 模型 / 精度 | 关键数字 |
|---|---|---|---|
| Quant.npu | Snapdragon 8 Elite（SM8750）NPU | Qwen2.5-3B W4A8 | 预填充 969.72 tok/s，解码 21.06 tok/s，峰值内存 1876 MB |
| Quant.npu | 同上 | SmolLM2-1.7B W4A8 | 预填充 1612.78 tok/s，解码 37.00 tok/s，峰值内存 994 MB |
| MobileMoE | Galaxy S25 CPU | MobileMoE-S（家族最小档）INT4 | 解码 138.1 tok/s（256 上下文） |
| MobileMoE | iPhone 16 Pro CPU | MobileMoE-S INT4 | 解码 204.6 tok/s（256 上下文） |
| Lever | OnePlus 12（8 Gen 3）+ UFS 4.0 | Qwen3-8B，闪存驻留 | 解码约 1.75 tok/s（全闪存）/ 3.40 tok/s（全 DRAM） |
| ReMoE | Jetson Orin NX 16GB + NVMe | 细粒度 MoE（llama.cpp） | TPOT −43.6%~49.8% |
| MobileExplorer | Galaxy S24 12GB | MAI-UI-2B VLM Q8 | 单步约 40 s |
| Dense2MoE | Jetson Thor-U | Dense2MoE 转换模型 | 总时延 307.5→271.0 ms |

从表中可以读出一个直观的分界：**1.7B~3B 稠密模型在旗舰手机 NPU 上已能做到千级 tok/s 预填充、二三十 tok/s 解码**，属于可交互区间；**家族最小档的 MoE（MobileMoE-S，INT4 权重 0.68 GB） 在手机 CPU 上即可破百 tok/s**；而一旦模型超过 DRAM、需要从闪存流式读取（8B~14B），解码立刻跌到个位数 tok/s，即使投机解码也只能把它拉到「能用但不流畅」。VLM 智能体更是以「秒/步」计。换句话说，端侧体验的天花板目前由 DRAM 容量和闪存带宽共同决定，NPU 峰值算力并不是主要约束。

### 小结

本期论文共同指向三点：其一，**NPU 的优势集中在预填充**，且依赖静态整数量化与低调度开销，开源栈下解码收益仅 5%~20%、甚至更耗电；其二，**端侧大模型 = MoE + 闪存分层**，UFS/SSD 带宽、DRAM 容量与专家局部性成为新的关键指标，软硬协同从路由微调延伸到 3D NAND 存内计算；其三，**测量口径决定结论**——平台能耗遥测缺失、量化内核未兑现带宽节省，都会让 tok/s 与 J/token 对比失真。对芯片厂商而言，下一代手机 SoC 的竞争点可能不是 NPU TOPS，而是 NPU 调用开销、闪存带宽与能耗可观测性。

## 7. 总结：对端侧智能体意味着什么，以及 6 月该看什么

**对端侧智能体的含义**

1. **先选对运行时，再谈芯片。** 同一颗 Hexagon NPU，ExecuTorch 与 llama.cpp NPU 路径的 prefill 相差 7.5–9 倍；在通用框架上，NPU 的 decode 只快 5–20%。智能体要多轮生成，短期最有效的投入是图覆盖率、量化格式（W4A8 / A16W4）和 DVFS 协同（CORE 让 TPOT 降约三到四成）。
2. **12GB 是新的分水岭。** Google 和 Apple 在三周内先后把 12GB 内存定为高级端侧 AI 的门槛；8GB 设备只能跑 1–3B 常驻模型，更大的模型要靠闪存分页和 MoE。
3. **小参数 MoE 与闪存驻留会成为常态。** MobileMoE、ReMoE、Lever 都说明：激活参数决定 decode 速度，总参数决定内存和闪存 I/O，后者需要 UFS 4.x/5.0 级带宽。
4. **眼镜是新的低功耗战场。** 眼镜芯片 0.5–8 TOPS，只做感知和唤醒，大模型在手机或云端；评价指标正在变成“每次拍照 / 每次唤醒的耗电”。

**留给 6 月的问题（结论已写在 6 月硬件洞察）**

- PC 的统一内存竞赛：Computex 上 RTX Spark（N1X，128GB / 300GB/s）和 Ryzen AI Max PRO 400（192GB）正式发布。
- Apple 的端侧模型路线：WWDC26 公布 AFM 3，20B 稀疏端侧模型把权重放闪存，并以 12GB 为门槛，印证了 5 月“Gemini 蒸馏 + 外部算力”的爆料方向。
- 存内计算与 PIM：VLSI 2026 上联发科 3nm 存内计算 NPU、台积电 2nm 存内计算编译器，ISCA 上 PIM 进入手机 LPDDR。

> 口径说明：标“官方”的是厂商发布的数字，“媒体实测”和“第三方实测”是独立测试，“爆料”未经确认，“推算”或“估算”是本文按公开参数计算的结果。5 月下半月部分方向没有检索到新品：高通、Apple 都没有新芯片；三星 Exynos、紫光展锐、AMD、Intel、Arm，以及 Hailo、DeepX、知存、苹芯、后摩等在窗口内没有可核实的新动态；内存侧的 LPDDR6、UFS 5.0、HBF 新闻分别在 3 月、6–7 月、8 月，只作背景。
