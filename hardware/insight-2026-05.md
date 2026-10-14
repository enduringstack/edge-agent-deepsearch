# 硬件洞察：端侧 AI 芯片月报（2026-05-01 ~ 2026-05-28）

> **说明：** 本期在 2026-10 回填 05-01~05-14 两周后，由“下半月版”扩写为全月版。5 月 29 日起的 Computex 归入 6 月。
>
> **一句话结论：5 月是“软件月”和“内存月”。** 没有旗舰芯片发布，最具体的端侧数字来自软件栈：Gemma 4 的 MTP 草稿模型与 LiteRT-LM v0.11 让投机解码进入官方端侧运行时，Gemma 4 E2B 在手机 GPU 上 decode 52–56 tok/s，Meta ExecuTorch 在 Hexagon NPU 上把 Llama 3.2 1B 的 prefill 做到约 2,900 tok/s。同时内存成了硬约束：TrendForce 预计 2Q26 手机 LPDDR5X 合约价上涨 78–83%，而 Google 的 Gemini Intelligence 把 12GB 内存定为门槛。芯片侧的增量在平台能力（联发科天玑智能体化引擎 2.0）、中端（骁龙 6/4 Gen 5、天玑 8550）和眼镜。
>
> **阅读结构（总-分-总）**：第 0 节是全月判断与时间线；第 1–6 节分厂商、分方向展开（高通 / Apple 与 Google / 其他 SoC 与 PC / 低功耗、存内计算与内存 / 顶会论文 / arXiv 精选）；第 7 节是对端侧智能体的含义和观察清单。逐条动态（含“能跑多大模型”和可展开的“技术细节”）见 05-01、05-08、05-15、05-22 四周首页的“硬件雷达”。

## 0. 总览：5 月的六个判断

**判断一：投机解码进入官方端侧运行时，2B 级模型 decode 进入 50 tok/s 档。**

| 平台 / 发布 | 模型 | 数字 | 口径 |
|---|---|---|---|
| Gemma 4 MTP 草稿模型（05-05） | Gemma 4 全系 | 最高约 3 倍提速、质量不变；Apple Silicon 上 26B MoE 在 batch 4~8 约 2.2 倍 | Google 官方 |
| LiteRT-LM v0.11（05-07） | Gemma 4 + MTP | 移动 GPU decode 提速超过 2 倍；CLI 原生支持 Windows | Google 官方 |
| Galaxy S26 Ultra / iPhone 17 Pro GPU（LiteRT-LM） | Gemma 4 E2B | decode 52 / 56 tok/s | Google 官方 |
| Galaxy S25（8 Elite，4 线程 CPU） | MobileMoE-S | decode 138.1 tok/s | Meta 论文 |

**判断二：NPU 的真实收益由软件栈决定，而不是 TOPS。**

| 研究 | 平台 | 结果 |
|---|---|---|
| ExecuTorch（MLSys） | Galaxy S25 Ultra Hexagon NPU，Llama 3.2 1B（A16W4） | prefill 2813–2977 tok/s，llama.cpp NPU 路径为 330–374 tok/s |
| 手机 NPU 去噪（arXiv，05-05） | 天玑 9500 / 骁龙 8 Elite | 全高清一帧 34.0 / 46.1 ms；只用 NPU 原生算子时比 GPU 快最多 3.88 倍 |
| NPU 并不总是更快（arXiv，莱顿） | 骁龙 8 Gen 3，llama.cpp | prefill NPU 比 CPU 慢 1.27–1.62 倍；decode 只快 1.05–1.20 倍 |
| CoReDiT（高通 AI 研究院，05-13） | 骁龙 8 Elite NPU | 扩散模型令牌剪枝，逐块提速最高 1.72 倍 |

**判断三：内存是 5 月端侧 AI 最硬的约束。** TrendForce（05-14）预计 2Q26 LPDDR4X 合约价至少涨 70–75%、LPDDR5X 涨 78–83%，高端机主流回到 12GB、中端回到 8GB；同月 Google 的 Gemini Intelligence 要求旗舰芯片 + 至少 12GB 内存，联发科高管在 MDDC 上直言端侧 AI 的瓶颈已是内存和带宽而不是算力。按约 25GB/s 带宽推算，骁龙 6/4 Gen 5 这类中端芯片跑 3B INT4 模型 decode 上限约 15 tok/s（推算）。

**判断四：端侧智能体从应用层下沉到平台。** 联发科天玑智能体化引擎 2.0（05-13）把常驻感知放在超能效 NPU 上并支持跨应用执行，官方称常驻轻载模型功耗降 42%、端侧大模型部署耗时最多省 90%；紫光展锐（05-07）发布端边 AI 平台 N9 与 UniClaw 智能体；NVIDIA（05-13）推荐 Hermes Agent 配 Qwen 3.6 在 RTX PC 与 DGX Spark 上常驻本地运行。研究侧，MobiSys 的 Agent-X 在 M4 Pro Mac mini 上把本地智能体端到端提速 1.61 倍。

**判断五：手机跑大模型的路线是“闪存 + MoE + 投机解码”，硬件研究围绕“少搬数据”。**

| 研究 | 做法 | 结果 |
|---|---|---|
| DECO（清华，05-11） | 稀疏 MoE 只激活约 20% 专家 | Jetson AGX Orin 上 decode 44.24 vs 15.09 tok/s（2.93 倍） |
| CATS（UF，05-11） | 闪存流式加载权重时的级联自投机解码 | Jetson 上最高 5.08 倍，不额外占内存 |
| 港科大 ReRAM 堆叠芯片（ISSCC，arXiv 05-10） | 55nm 逻辑 + 4 层 ReRAM，25.6GB/s | LLaMA2-7B decode 17.82 tok/s、123 mJ/token |
| Lever（清华，05-16） | 目标模型放闪存，投机解码批量验证 | 比直接从闪存读取快 2.93 倍 |

**判断六：芯片增量在中端、低功耗和眼镜。** 骁龙 6 Gen 5 / 4 Gen 5（05-07）和天玑 8550（05-27）把 AI 能力下放到中端但都不公布 TOPS；16nm 三值加速器 VitaLLM 以 0.214mm² 跑 BitNet 3B 72 tok/s（片外带宽未计入）；Ambiq 一季度超八成出货在跑 AI 算法；Android XR 音频眼镜、安凯微眼镜芯片、Halo AI 眼镜（单颗 Alif B1）说明眼镜的指标正在从 TOPS 转向“每次唤醒耗多少电”。

### 5 月关键事件时间线

| 日期 | 事件 | 类别 |
|---|---|---|
| 05-01 | VitaLLM 三值加速器、亚阈值 SRAM 存算宏（arXiv） | 研究 |
| 05-04 | 爆料：Tensor G6 与 Pixel 11 内存配置 | Google |
| 05-05 | Gemma 4 MTP 草稿模型；AI Hub 3B 自投机模型支持 8K；TechInsights 拆解 Exynos 2600（首款 2nm 手机 SoC） | 软件 / 移动 SoC |
| 05-06 | NSDI：Remembrall 端侧持续学习 | 研究 |
| 05-07 | 骁龙 6 Gen 5 / 4 Gen 5；LiteRT-LM v0.11；紫光展锐 N9；瑞萨完成收购 Irida Labs | 移动 SoC / 软件 |
| 05-08 | 报道：Apple 与 Intel 达成初步代工协议；高通 Dragonwing 开发者生态 | 产业 |
| 05-10 | 港科大 ReRAM 堆叠 LLM 芯片（ISSCC 论文 arXiv 版） | 研究 |
| 05-11 | Agent-X、DECO、CATS（arXiv）；嵌入式视觉峰会 | 研究 |
| 05-12 | Android Show：Gemini Intelligence、Googlebook；Ambiq 财报；SenSys 2026 开幕 | Google / 低功耗 |
| 05-13 | 联发科 MDDC 2026：天玑智能体化引擎 2.0；NVIDIA Hermes 本地智能体；CoReDiT | 移动 SoC / PC |
| 05-14 | TrendForce：LPDDR5X 季涨 78–83%；FCCM / RTAS 论文 | 内存 / 研究 |
| 05-15 | Gemini Intelligence 硬件门槛：旗舰芯片 + 12GB；联发科更新天玑主流芯片 | Google / 移动 SoC |
| 05-18~22 | MLSys 2026：ExecuTorch、CORE、IntAttention、Kitty 等 | 研究 |
| 05-19 | Google I/O：LiteRT-LM 数据、Chrome Prompt API、Android XR 眼镜、Coralboard；Mythic 收购 Videantis | Google / 低功耗 |
| 05-21 | 高通与 Stellantis 扩大合作，aiMotive 拟并入高通 | 车载 |
| 05-25 | 华为“韬定律”与双层逻辑折叠；N1X 泄露 | 移动 SoC / PC |
| 05-27 | 天玑 8550 发布；安凯微 AI 眼镜芯片 | 移动 SoC / 眼镜 |
| 05-28 | 爆料：Apple 用 Gemini 蒸馏端侧模型；高通 Snapdragon C 官方稿 | Apple / PC |

## 1. 高通：中端芯片与工具链，没有旗舰新品

### 总览：高通5月是“软件月”，芯片硬指标留给6月

2026年5月1日至28日，高通没有发布任何旗舰或PC新芯片。官方芯片发布只有两次：5月7日面向中低端手机的[骁龙6 Gen 5与骁龙4 Gen 5](https://www.qualcomm.com/news/releases/2026/05/qualcomm-unveils-two-new-snapdragon-mobile-platforms--delivering)，以及5月28日面向300美元入门笔记本的[Snapdragon C](https://www.qualcomm.com/news/releases/2026/05/introducing-snapdragon-c--designed-to-revolutionize-entry-tier-l)，两者都没有公布NPU算力。真正密集的是软件栈与生态：AI Hub模型库连发两个版本（3B自投机模型上下文扩到8K、上架Pi0.5机器人VLA），首个公开的ONNX Runtime插件执行提供程序，X2 Elite NPU上的本地Agent方案，以及Vulkan的tile内存扩展。车载侧，Stellantis在5月21日把ADAS软件也交给高通，并拟将aiMotive并入高通。

整体判断有三点。第一，高通5月的增量集中在“让开发者更容易用上Hexagon NPU”，而不是更高的TOPS。第二，中低端芯片的AI叙事明显落后于同月联发科天玑8550/7500的“LLM加速下放”。第三，官方材料几乎都缺少tokens/s、TTFT和功耗这类硬数字，月内最具体的骁龙NPU端侧数字反而来自第三方论文和Google、Meta的运行时。

### 一、手机：中低端只讲体验，旗舰只有爆料

**骁龙6 Gen 5 / 4 Gen 5（5月7日，官方）。** 新闻稿给出的都是体验数字：6 Gen 5应用启动快20%、卡顿少18%、GPU提升最高21%；4 Gen 5应用启动快43%、卡顿少25%、GPU提升最高77%，4系首次支持90FPS游戏。[产品页](https://www.qualcomm.com/smartphones/products/6-series/snapdragon-6-gen-5-mobile-platform)补充CPU最高2.6GHz、能效提升8%。制程与内存来自[IT之家](https://www.ithome.com/0/947/192.htm)（媒体口径）：两款均为4nm；6 Gen 5为4×2.6GHz+4×2.0GHz，最高16GB LPDDR4X-4200或LPDDR5-6400；4 Gen 5为LPDDR4X-4267。AI部分官方只写了“AI拍照/夜视”，Hexagon代际和TOPS均未披露。另需注意，新闻稿写Adaptive Performance Engine 4.0，产品页写5.0，两处官方口径不一致。

能跑多大的模型，只能推算：6 Gen 5配LPDDR5-6400（2×16bit）时峰值带宽约25.6GB/s，3B模型INT4权重约1.5–1.7GB，decode理论上限约15 tok/s；若OEM选LPDDR4X，带宽约17GB/s，上限再降三分之一。对照同月Google [Gemini Intelligence的门槛](https://9to5google.com/2026/05/15/gemini-intelligence-android-spec-requirements/)（旗舰芯片+至少12GB内存+Gemini Nano v3），6系机型实际进不了高级端侧AI那一档。

**终端。** 5月21日[小米17 Max](https://91mobiles.com/hub/xiaomi-17-max-china-launch-confirmed-may-21st)搭载第五代骁龙8至尊版和8000mAh电池，没有新的端侧AI规格。窗口内骁龙旗舰新机的卖点仍是续航与影像。

**爆料：第六代8至尊版Pro成本超300美元（5月12日，低可信）。** [Android Headlines](https://androidheadlines.com/2026/05/snapdragon-8-elite-gen-6-pro-price-leak-ultra-flagships.html)转述爆料人@yabhishekhd：SM8975单颗成本超过300美元，估计最高330美元，高于第五代约280美元；台积电N2P，Pro版支持LPDDR6与UFS 5.0，标准版SM8950为LPDDR5X+Adreno 845。这与3月Digital Chat Station关于双版本、18MB与12MB GMEM的[爆料](https://www.gizmochina.com/2026/03/25/snapdragon-8-elite-gen-6-8-elite-gen-6-pro-specs-leak/)一致，但NPU规格仍完全空白。若属实，LPDDR6带来的带宽红利会先被最贵的一档机型吃掉。正式规格要到9月骁龙峰会。

### 二、PC：入门平台与“标准栈”调用NPU

**Snapdragon C（5月28日，官方）。** 官方新闻稿的`pagePublishDate`为5月28日（此前周报依媒体报道记为6月1日Computex）。定位是300美元起的入门笔记本，OEM为宏碁、惠普、联想，“集成NPU”但未披露TOPS、制程与内存规格，终端年内上市。它的意义在于把Windows on Arm的NPU带到最低价位，但没有算力数字就无法判断能否满足Copilot+ PC的40 TOPS门槛。

**ONNX Runtime插件EP（5月20日，官方）。** 高通在[开发者博客](https://www.qualcomm.com/developer/blog/2026/05/qualcomm-launches-the-first-onnx-runtime-plugin-execution-provider)宣布首个公开的ORT插件执行提供程序，并开源EP代码。插件EP以动态库形式加载，和ORT核心解耦，高通可以按月推送算子覆盖与性能优化，不必等ORT季度版本，覆盖Android、Windows和Linux。

**LLMWare本地Agent（5月26日，官方）。** [博客](https://www.qualcomm.com/developer/blog/2026/05/local-agentic-ai-with-llmware-on-pcs-with-snapdragon-x-series)演示在X2 Elite NPU上通过Windows ML + ORT GenAI + QNN EP跑本地Agent工作流，但没有模型名称、精度和tokens/s。X2 Elite的NPU官方口径为80 TOPS（INT8）。两篇博客合起来看，高通正把ISV从直接调用QNN转向微软标准栈，NPU的价值越来越取决于ORT/Windows ML的算子覆盖率。

### 三、车载、机器人与IoT：全栈化

**Stellantis（5月21日，官方）。** [新闻稿](https://www.qualcomm.com/news/releases/2026/05/stellantis-and-qualcomm-expand-partnership-to-adopt----snapdrago)称Stellantis在座舱、连接和ADAS上统一采用Snapdragon Digital Chassis，Snapdragon Ride Pilot从主动安全扩展到L2+脱手驾驶，并与STLA Brain集成，可赋能“数百万辆”车；同时签署非约束性意向书，拟将aiMotive并入高通。具体SoC型号、TOPS、首发车型均未披露，且授标与意向书都非约束性。背景是4月10日Bosch与高通把合作扩展到ADAS（Bosch已交付超1000万台骁龙座舱计算机），4月29日财报显示QCT汽车营收创纪录，汽车+IoT合计同比增长20%。

**Dragonwing开发者生态（5月8日，官方）。** [博客](https://www.qualcomm.com/developer/blog/2026/05/edge-ai-prototype-deployment-qualcomm-dragonwing-developer-ecosystem)把Arduino（UNO Q/VENTUNO Q原型板）、AI Hub（模型）、Edge Impulse（训练与容器化，支持VLM级联）、Arduino App Lab（应用组装）和Foundries.io（Yocto、SBOM、OTA回滚）串成一条官方链路。同期的[UNO Q博客](https://www.qualcomm.com/developer/blog/2026/05/the-arduino-uno-q-board--unpack-the-dual-brain-power-for-next-ge)介绍该板的“双脑”架构：Dragonwing QRB2210跑Debian，STM32U585跑Zephyr做实时控制，内存2GB/4GB，只适合视觉小模型而非LLM。

**AI Hub上架Pi0.5（5月19日，官方）。** [v0.54.0](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.54.0)新增Pi0.5视觉-语言-动作模型，并在设备列表中加入Dragonwing Q-7790、Q-8750、IQ-X5121、IQ-X7181与SA8255P/SA8650P。模型拆为视觉编码器、token嵌入、主干和动作专家四个子图，主干w4a16、其余w8a16，完整控制回路延迟未披露。这是高通首次把通用机器人基础模型放进官方预优化库。

**Dragonwing MBM（5月20日，OnQ）。** [OnQ文章](https://www.qualcomm.com/news/onq/2026/05/qualcomm-dragonwing-mbm-family-announcement)发布面向“互动宽带”终端的MBM7/MBM4系列（MBM715、MBM415）：5G Sub-6、Wi-Fi 7（320MHz、4K QAM）、蓝牙6.0、三12-bit ISP最高200MP、LPDDR4x/LPDDR5x，MBM7系列“集成AI”但未给TOPS。旧版月报认为该产品发布日无法核实，现据OnQ正文载荷确认为5月20日。

### 四、软件栈与工具链：上下文、精度与带宽

- **AI Hub Models v0.53.1（5月5日）**：[release](https://github.com/qualcomm/ai-hub-models/releases/tag/v0.53.1)称Llama 3.2 3B Instruct SSD（自投机解码，主干w4a16）通过把LM head拆成独立context binary，上下文从4K扩到最高8K；新增头部姿态SixDRepNet和激光雷达分割RangeNet++。[模型页](https://aihub.qualcomm.com/models/llama_v3_2_3b_instruct_ssd)列出手机、PC、IoT、车载四类终端，但未给tok/s。8K上下文对端侧Agent装下工具描述和多轮历史是实用下限。
- **QAIRT 2.47.0（5月版）**：官方[修订历史](https://docs.qualcomm.com/doc/80-63442-10/topic/general_revision_history.html)标注为2026年5月，构建号为2.47.0.260601，未计入新条目。HTP新增W2FP16a（Conv/FC/MatMul）与W4FP16a块量化、Int16 Hadamard变换；Genie新增线性注意力支持并在Windows上启用GPU引擎；LPAI后端支持Hexagon模拟器。2-bit权重块量化与线性注意力意味着高通在为更大的端侧模型和长上下文做准备。
- **Tile Memory Heap（5月27日）**：[博客](https://www.qualcomm.com/developer/blog/2026/05/high-performance-memory-extension-optimize-memory)介绍VK_QCOM_tile_memory_heap，让render与compute pass在一次提交内共享片上tile内存，减少LPDDR往返，但未给收益百分比。

### 五、XR与可穿戴

Google I/O（5月19日）展示的[Android XR眼镜](https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/)分音频款和显示款，音频款今秋先上市，由Google、三星与高通联合开发，但I/O上未点名芯片。到9月骁龙峰会才确认采用Snapdragon AR1。眼镜端负责相机、音频和唤醒等常驻任务，大模型推理依赖配对手机。4月10日高通与Snap签署多年协议，为未来几代Specs提供Snapdragon XR平台，加上5月的Android XR，高通在眼镜芯片上同时绑定了Google与Snap两大平台。

### 六、高通AI研究院论文

5月13日提交的[CoReDiT](https://arxiv.org/abs/2605.14191)（论文页注明CVPR workshop）用线性复杂度的空间一致性分数跳过潜空间里的冗余token，再用邻近token重建，让张量形状保持规则。在PixArt-α与MagicDrive-V2上自注意力FLOPs最多减少55%，云端GPU提速1.33倍，**骁龙8 Elite NPU逐块提速最高1.72倍**；基线在超过1600分辨率时于NPU上OOM，说明端侧图像生成先撞上的是内存。同日同组还提交了[MAPLE](https://arxiv.org/abs/2605.14201)，在VLA潜空间里做多智能体闭环强化学习，用于端到端自动驾驶（Bench2Drive），偏训练方法，和车载产品线呼应。月内第三方论文中，ExecuTorch（MLSys）在Galaxy S25 Ultra的Hexagon NPU上把Llama 3.2 1B的prefill做到2,813–2,977 tok/s；莱顿大学则发现骁龙8 Gen 3上llama.cpp的NPU路径prefill反而比CPU慢1.27–1.62倍。可见骁龙NPU的实际收益高度依赖软件栈。

### 小结：5月对端侧智能体意味着什么

1. **算力没有新数字，栈在变厚。** 5月高通能确认的端侧新能力是：3B模型8K上下文、ORT插件EP按月更新、QAIRT加入2-bit块量化与线性注意力、Windows ML标准路径调用X2 Elite NPU。这些都在降低端侧Agent的部署成本，而不是抬高上限。
2. **分层更清晰。** 8系（及爆料中的Gen 6 Pro）承担生成式AI，6/4系和Snapdragon C只保证“有NPU”，没有给出能跑多大模型的口径；中低端端侧大模型将受LPDDR4X/LPDDR5带宽约束。
3. **物理AI是第二主线。** 车载从SoC走向“SoC+Ride Pilot+aiMotive”，机器人有Pi0.5进入AI Hub、Dragonwing工具链整合，但都缺少闭环延迟和功耗数据。

6月要看的是：Computex上Snapdragon C和X2系列的NPU规格、Dragonwing IQ10机器人平台，以及6月24日投资者日上的数据中心与物理AI路线；9月骁龙峰会才会揭晓第六代8至尊版的NPU与LPDDR6实际规格。

## 2. Apple 与 Google：MTP 与 I/O 给出端侧实测，Apple 只有供应链与爆料

### 总览：Google 用数字说话，Apple 只有爆料和供应链

整个 5 月（05-01~05-28），Apple 和 Google 在端侧 AI 上走了两条截然不同的路线。**Google 把端侧大模型做成了可量化的工程**：5 月 5 日发布 [Gemma 4 多 token 预测（MTP）草稿模型](https://blog.google/innovation-and-ai/technology/developers-tools/multi-token-prediction-gemma-4/)，5 月 7 日 [LiteRT-LM v0.11.0](https://github.com/google-ai-edge/LiteRT-LM/releases/tag/v0.11.0) 把 MTP 接入端侧，5 月 12 日 Android Show 推出 Gemini Intelligence 和 Googlebook，5 月 19 日 I/O 上给出 Gemma 4 E2B 在旗舰手机 GPU 上 52~56 tok/s 的官方数据。**Apple 在 WWDC（6 月 8 日）前几乎没有一手发布**：Apple ML Research 博客 5 月只有论文条目，MLX 从 4 月 22 日 v0.31.2 到 7 月都没有新版本。外界看到的 Apple 主要来自供应链和爆料：Intel 代工、Mac Studio 大内存配置下架、带摄像头的 AirPods、Gemini 蒸馏端侧模型。

本月可以归纳为三个判断：

1. **投机解码成为端侧 LLM 的标配。** MTP 从 Gemma 权重（4 月 16 日）到运行时（5 月 7 日）再到 I/O 的官方数字（5 月 19 日，最高 2.2 倍），一个月内走完了落地流程。手机 decode 受内存带宽限制，MTP 用一次读权重校验多个 token，是目前少数能越过带宽上限的手段。
2. **“12GB 内存”成为高级端侧 AI 的门槛，而内存正在涨价。** Gemini Intelligence 要求至少 12GB 内存；Tensor G6 爆料中基础款 Pixel 11 却出现 8GB 版本；Apple 下架了 M3 Ultra Mac Studio 的 256GB 选项，只剩 96GB。端侧 AI 的需求和内存供应在同一个月里相互挤压。
3. **端云混合是两家的共同现实。** Google 的 Gemini Intelligence 同时依赖端侧 Private Compute Core 和云端 Private AI Compute；Apple 的新 Siri 据报道由 Gemini 驱动，部分请求要上 Google 云。纯端侧智能体在 2026 年 5 月还不是任何一家的主路线。

### 一、Gemma 4 MTP：从权重到端侧运行时（05-05 ~ 05-07）

Gemma 官方[发布记录](https://ai.google.dev/gemma/docs/releases)显示 MTP 权重早在 4 月 16 日就已上线，5 月 5 日的 Keyword 博客是面向开发者的正式介绍。官方口径：

| 场景 | 加速 | 口径 |
|---|---|---|
| Gemma 4 全系（最好情况） | 最高约 3 倍，质量不下降 | 官方，未注明对应的模型和硬件 |
| 26B MoE @ Apple Silicon，batch=1 | 收益受限（MoE 路由问题） | 官方定性 |
| 26B MoE @ Apple Silicon，batch 4~8 | 约 2.2 倍 | 官方 |
| 移动 GPU（LiteRT-LM v0.11.0） | 超过 2 倍 | 官方 release note |
| 移动 GPU / 移动 CPU（LiteRT-LM 文档） | 最高 2.2 倍 / 最高 1.5 倍 | 官方文档当前版本 |

机制上有两点值得注意。其一，草稿模型**复用主模型的激活并共享 KV Cache**，不重复做 prefill，这对内存紧张的手机很关键。其二，Google 承认端侧 E2B/E4B 的瓶颈在**最后的 logit 计算**（大词表投影），并在 embedder 中加入聚类技术缓解；这说明 2B 级模型压到极致后，瓶颈已经从 Transformer 主体转移到词表层。

LiteRT-LM 文档还给出一条实用的取舍：GPU 上建议所有任务都开启 MTP；但 E2B 在 CPU 上做自由生成时可能反而变慢，只在改写、摘要、代码这类可预测输出上开启，原因是草稿接受率低。同版本还让 LiteRT-LM CLI 原生支持 Windows（CPU/GPU），[AI Edge Gallery 1.0.13](https://github.com/google-ai-edge/gallery/releases/tag/1.0.13) 在 Android/iOS 上加入“投机解码”开关。

**带宽推算（标为推算）**：LiteRT-LM 文档当前版本中 E2B 文件为 2.58 GB。若每个 token 读取约 1~1.5 GB 权重（量化位宽官方未披露），旗舰手机几十 GB/s 的 LPDDR5X 对应的 decode 上限是几十 tok/s，与 S26 Ultra GPU 52 tok/s、iPhone 17 Pro GPU 56 tok/s 同一量级。同一张表里 MacBook Pro M4 GPU 达到 160 tok/s，也符合“带宽越高 decode 越快”。要在手机上越过这个量级，靠的是 MTP（一次读权重多出 token）和 MoE（少读权重）。

### 二、Android Show（05-12）：Gemini Intelligence 与 Googlebook

5 月 12 日，Google 在 I/O 前一周的 [Android Show](https://blog.google/products-and-platforms/platforms/android/android-show-io-edition-2026/) 上发布两件事：

- **[Gemini Intelligence](https://blog.google/products-and-platforms/platforms/android/gemini-intelligence/)**：把跨应用多步自动化、Personal Intelligence 自动填充、Gboard 语音输入“Rambler”和生成式小组件统一成一个品牌。多步自动化以 Galaxy S26 和 Pixel 10 为调优机型，今夏首发最新的 Galaxy 和 Pixel，年内扩展到手表、汽车、眼镜和笔记本。官方博客**没有写任何芯片和内存要求**；三天后（05-15），[9to5Google 从落地页脚注](https://9to5google.com/2026/05/15/gemini-intelligence-android-spec-requirements/)中发现门槛是“旗舰芯片 + 至少 12GB 内存 + Gemini Nano v3 以上”。同日的[安全博客](https://blog.google/security/android-gemini-intelligence-security-privacy/)说明了架构：主动功能使用端侧 Private Compute Core、云端 Private AI Compute 和受保护 KVM；智能体执行需要按应用授权、购买前确认，并有提示注入防护。这是端云混合架构，而不是纯端侧。
- **[Googlebook](https://blog.google/products-and-platforms/platforms/android/meet-googlebook/)**：以 Gemini 为核心的新笔记本品类，首批 OEM 为 Acer、ASUS、Dell、HP、Lenovo，今秋上市。官方没有给出 NPU 和内存规格；Google 副总裁 John Maletis 对 [ChannelNews](https://www.channelnews.com.au/googlebook-laptops-to-launch-with-intel-qualcomm-and-mediatek-chips/) 表示从第一天起就与 Intel、Qualcomm、MediaTek 合作。结合 LiteRT-LM 同月先后加入 Windows 原生支持（05-07）和 Intel OpenVINO NPU 后端（05-18 的 v0.12.0），Google 的端侧栈正在为 PC NPU 做准备。

此外，媒体报道 Gemini Intelligence 将随 Galaxy Z Fold8/Flip8 首发商用，三星首款 Android XR 眼镜也传将在 7 月 22 日的发布会亮相（[9to5Google](https://9to5google.com/2026/05/12/samsung-galaxy-glasses-watch-9-launch-date-report/)，媒体转述首尔经济日报）。5 月 6 日的一则报道提醒了端侧模型的“存储成本”：Chrome 在后台下载约 4GB 的 Gemini Nano 权重（[9to5Google](https://9to5google.com/2026/05/06/google-chrome-4gb-storage-ai-details/)）；Chrome [官方文档](https://developer.chrome.com/docs/ai/understand-built-in-model-management)说明会用着色器测试 GPU 性能，在约 4B 和约 2B 两个变体之间选择，磁盘空间不足时自动删除。Android AICore 在 Nano 升级时也会新旧两版并存最多 3 天（[9to5Google 05-02](https://9to5google.com/2026/05/02/android-aicore-storage/)）。

### 三、Google I/O（05-19 ~ 05-26）：端侧 50 tok/s 档与跨平台

I/O 的端侧数字在 05-15、05-22 两周的硬件雷达中已有详细条目，这里只做综合：

| 设备 / 后端 | 模型 | Decode（不含 MTP） | 口径 |
|---|---|---|---|
| Galaxy S26 Ultra / GPU | Gemma 4 E2B | 52 tok/s | Google 官方 |
| iPhone 17 Pro / Metal GPU | Gemma 4 E2B | 56 tok/s | Google 官方 |
| MacBook Pro M4 Max / WebGPU | Gemma 4 E2B | 最高 76 tok/s | Google 官方 |
| iPhone 17 Pro / CPU | Gemma 4 E2B | 内存约 607 MB | Google 官方 |

- [LiteRT-LM 技术博客](https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/)把 MTP 的官方上限定为 2.2 倍，并开源 Swift API 和 WebGPU JS API；E2B 的 Per-Layer Embedding 不常驻内存、编码器按需加载，把 iOS CPU 上的物理内存压到约 607 MB。
- [LiteRT-LM v0.12.0](https://github.com/google-ai-edge/LiteRT-LM/releases/tag/v0.12.0)（05-18）让 CLI 支持 NPU，接入 Intel OpenVINO NPU。
- [Chrome I/O 汇总](https://developer.chrome.com/blog/chrome-at-io26)：Prompt API 在 Chrome 148 进入稳定版，并发布 Gemma 197M 专家模型承担任务型 API。
- [Android XR](https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/)：与三星、高通共建，音频眼镜今秋先发，兼容 iOS；官方未公布芯片。Google Research 与 Synaptics 在 I/O 展示 [Coralboard](https://www.edge-ai-vision.com/2026/05/google-research-and-synaptics-partner-to-showcase-immersive-edge-ai-experiences-powered-by-the-coralboard-at-google-i-o-2026/)（1 TOPS 级 Coral NPU）。
- [Android I/O AI 汇总](https://android-developers.googleblog.com/2026/05/android-ai-intelligence-system.html)（05-26）：Gemini Nano 4 仍处于 AICore 开发者预览，Prompt API 加入前缀缓存（直接压缩智能体长 system prompt 的 prefill）；Firebase AI Logic 提供 PREFER_ON_DEVICE 等四种端云路由。

### 四、Tensor G6：TPU 仍是空白

5 月 4 日，Mystic Leaks 发布 Pixel 11 大规模泄露（[9to5Google](https://9to5google.com/2026/05/04/google-pixel-11-specs-cameras-tensor-g6-leak/)，爆料）：Tensor G6 采用 1+4+2 的 Arm C1 CPU（Android Authority 检索摘要给出 4.11/3.38/2.65GHz，比 G5 少 1 核），GPU 是 PowerVR CXTP-48-1536（媒体称是 2021 年的设计），有新 TPU 和新 GXP ISP，基带换成联发科 M90。**TPU 算力完全没有披露**；TSMC 2nm 只见于部分媒体，9to5Google 原文没有写。更值得注意的是内存：基础款 Pixel 11 为 8GB/12GB，Pro 系列为 12GB/16GB。如果属实，8GB 版本将达不到 Gemini Intelligence 的 12GB 门槛。Google 自家旗舰内部也会出现“能不能跑高级端侧 AI”的分层。

### 五、Apple：供应链、内存和爆料

**一手发布几乎为零。** Apple ML Research 博客 5 月上架的条目中，与端侧系统相关的只有几篇论文：[SpecMD](https://machinelearning.apple.com/research/specmd-expert-prefetching)（ICML，MoE 专家预取；Least-Stale 淘汰策略比 LRU 冲突缺失最多少 85 倍，在 OLMoE 上仅用 0.6 GB 缓存就让 TTFT 最多降 34.7%）、[Stochastic KV Routing](https://machinelearning.apple.com/research/stochastic-kv-routing)（沿深度方向跨层共享 KV Cache）、[EpiCache](https://machinelearning.apple.com/research/epicache)（ICML，长对话 KV Cache 4~6 倍压缩下接近全缓存精度，延迟最多降 2.4 倍，峰值内存最多降 3.7 倍）。这三篇的 arXiv 首发都早于 5 月（2602.03921、2604.22782、2509.17396），所以只作背景。5 月 19 日 Apple 预告了一批由 Apple Intelligence 驱动的[辅助功能](https://www.apple.com/newsroom/2026/05/apple-unveils-new-accessibility-features-and-updates-with-apple-intelligence/)，媒体称视频字幕将用端侧语音识别生成，年内上线。5 月 11 日 ML Research 发布了隐私保护机器学习研讨会回顾（[9to5Mac](https://9to5mac.com/2026/05/11/apple-shares-recordings-and-research-from-recent-privacy-focused-ai-and-ml-workshop/)），与硬件无关。

**供应链与内存。** 5 月 5 日 Bloomberg 报道 Apple 评估 Intel 和三星产线（[9to5Mac](https://9to5mac.com/2026/05/04/report-apple-considers-intel-and-samsung-to-diversify-chip-manufacturing-away-from-tsmc/)），原因之一是“适合本地跑 AI 模型的 Mac”需求超出预期。5 月 8 日 WSJ 称双方已达成[初步代工协议](https://9to5mac.com/2026/05/08/apple-and-intel-have-reached-a-deal-to-produce-future-chips-report/)。5 月 14 日郭明錤称 Intel 已开始初步生产低端或旧款芯片，TSMC 仍保有超过 90% 的份额（[9to5Mac](https://9to5mac.com/2026/05/14/intel-is-now-making-iphone-chips-for-apple-per-report/)）。同样在 5 月 5 日，M3 Ultra Mac Studio 的 [256GB 选项被下架](https://9to5mac.com/2026/05/05/apples-most-powerful-mac-studio-loses-its-last-remaining-ram-upgrade-option/)（512GB 已在 3 月下架），只剩 96GB。按容量推算，96GB 放得下约 70B 的 8bit 模型或约 150B 的 4bit 模型，而在单机本地跑数百 B 参数 MoE 的档位已经消失。本地 AI 的需求在这里第一次以缺货的形式出现。

**爆料：端侧蒸馏、外部算力和新形态。**

| 日期 | 内容 | 口径 |
|---|---|---|
| 05-05 | iOS 27 “Extensions”：用户可为 Siri、写作工具等选择 Gemini、Claude 等第三方模型（[9to5Mac](https://9to5mac.com/2026/05/05/ios-27-will-let-you-choose-between-gemini-claude-and-more-for-ai-features-report/)） | Bloomberg 爆料 |
| 05-07 | 带摄像头的 AirPods 进入 DVT，左右各一颗低分辨率摄像头作为 Siri 的“眼睛”，视觉数据上云时亮 LED（[9to5Mac](https://9to5mac.com/2026/05/07/apple-hits-milestone-in-development-of-airpods-with-cameras-report/)） | Bloomberg 爆料 |
| 05-12 | iOS 27 重建 Siri，加入系统级“Search or Ask”手势和对话模式（[9to5Mac](https://9to5mac.com/2026/05/12/ios-27s-completely-rebuilt-siri-will-include-a-new-system-wide-search-gesture-report/)） | Bloomberg 爆料 |
| 05-17 | 独立 Siri App，Gemini 版 Siri 跑在 PCC（[9to5Mac](https://9to5mac.com/2026/05/17/apple-launching-new-siri-app-next-month-with-auto-deleting-chat-history/)） | 爆料 |
| 05-25 | genai.apple.com 子域名出现（[TechTimes](https://www.techtimes.com/articles/317080/20260525/apple-registers-genai-subdomain-ahead-wwdc-siri-overhaul-finally-arrives-ios-27.htm)） | 媒体 |
| 05-28 | 用 Gemini 蒸馏端侧小模型；部分 Siri 请求跑在 Google 云的 Nvidia 机密计算上（[9to5Mac](https://9to5mac.com/2026/05/28/new-details-on-apple-google-ai-deal-revealed-including-nvidia-chips-report/)） | The Information 爆料 |

把这些拼起来，Apple 的架构正从“端侧模型 + 自有 PCC”变成“蒸馏端侧模型 + PCC + 第三方云 + 第三方模型扩展”。AirPods 摄像头的设计（低分辨率采集、上云理解）也说明，Apple 的可穿戴 AI 并不打算在耳机里做重推理。

### 小结

- **Google**：5 月形成了“权重（MTP）→ 运行时（LiteRT-LM v0.11/v0.12）→ 平台（Gemini Intelligence、Googlebook、Chrome、Android XR）→ 官方实测（I/O）”的完整链条。2B 级模型在旗舰手机 GPU 上 50+ tok/s 已是基线，MTP 和前缀缓存分别优化 decode 和 prefill。短板在于 Tensor 自家 TPU 没有公开的端侧 LLM 数字，官方数据都来自 GPU 和 CPU。
- **Apple**：一手信息几乎为零，可以确认的变化在供应链（Intel 初步代工）和内存（Mac Studio 大内存配置下架）；关于端侧模型的判断全部来自爆料，需要等 WWDC26 的第三代 Foundation Models 验证。
- **共同趋势**：内存容量成为端侧 AI 的真正门槛（12GB 门槛、8GB SKU、96GB Mac Studio），端云混合是两家都接受的现实。
- **存疑与待跟进**：MTP“最高 3 倍”未注明硬件；LiteRT-LM 表格为文档当前版本，不一定是 5 月当时的数字；Tensor G6 的 2nm 和频率来自单一爆料源；Googlebook 在 5 月没有任何 NPU 规格。

## 3. 联发科、紫光展锐、华为与 PC：智能体平台与内存涨价

5 月（5/1–5/28）高通、苹果、谷歌之外的端侧芯片动态，可以用一句话概括：**算力不再是瓶颈，内存才是。** 上半月，联发科在 MDDC 2026 上公开说“端侧 AI 的主要瓶颈是内存和带宽”；TrendForce 同日发布报告，手机 LPDDR5X 合约价一个季度上涨 78–83%。下半月的产品都在回应这个约束：天玑 8550 不加硬件，只换 AI 软件栈；华为用“逻辑折叠”在受限工艺上找回密度；NVIDIA 和 AMD 的 PC 路线都在堆统一内存容量。月底的 Computex（5/29 起）归入 6 月。

### 一、联发科：上半月讲 Agent 平台，下半月讲中端下放

**MDDC 2026（5/13）。** 联发科在[天玑开发者大会](https://www.mediatek.com/zh-cn/press-room/mediatek-held-dimensity-developer-conference-2026-mddc2026)发布了天玑 AI 智能体化引擎 2.0 和 AI 开发套件 3.0，并展示了与 OPPO、小米、传音合作的系统原生 Claw。硬件基础是旗舰平台的“超性能 + 超能效”双 NPU：重负载交给大 NPU，常驻感知交给 eNPU。官方给出的数字如下：

| 工具 | 官方口径 |
|---|---|
| eNPU 开发工具包 | 常驻轻载模型功耗 −42% |
| Low Bit 压缩工具包 | 同等质量下压缩率最多 +58% |
| 天玑 AI Partner | 端侧 LLM 移植耗时最多 −90% |
| LVM 可视化部署 | 部署与调优效率 +50% |

更值得注意的是会后群访（[IT之家](https://www.ithome.com/0/951/028.htm)）。高管直言手机算力已能满足大部分应用，内存占用和带宽才是主要瓶颈；内存涨价会让行业“更理性地思考端云边界”。他们还认为，Agent 框架把 Harness 和大模型分开以后，手机可以先用 CPU 跑记忆、场景感知这部分，所以未来的天玑平台会更重视 CPU 与 NPU 的协同调度。这等于承认，下一代手机 Agent 的体验差异主要来自常驻低功耗 NPU、低比特压缩和调度，而不是峰值 TOPS。

**中端下放（5/15–5/28）。** [5 月 15 日的官方博客](https://www.mediatek.com/tek-talk-blogs/mainstream-to-premium-smartphones-get-a-fresh-set-of-mediatek-dimensity-chipsets)更新了一批主流天玑芯片。月底发布的天玑 8550 与 8500 硬件相同（4nm、8×A725、Mali-G720 MC8、LPDDR5X-9600），区别是 NPU 880 加上了 **LLM Booster**、INT4 混合精度和投机解码，并支持 Gemini Nano V3（[Tecnoblog](https://tecnoblog.net/noticias/mediatek-revela-chip-dimensity-8550-para-levar-ia-local-a-celulares-mais-baratos/)）。[荣耀 600 Pro 国行版](https://www.fonearena.com/blog/483611/honor-600-price-specifications-honor-600-pro-china.html)和 [OPPO Reno16 Pro](https://www.money.it/oppo-reno-16-e-reno-16-pro-ufficiale-il-lancio-ecco-i-nuovi-smartphone-con-intelligenza-artificiale)（均为 5/25 发布）首发，两款都是 12GB 起步。LPDDR5X-9600 按 64-bit 总线推算，峰值约 76.8GB/s，3B 级 INT4 模型的 decode 上限约为每秒几十 token（推算）。投机解码和 INT4 是在不增加带宽的前提下提高 tok/s 的手段，这和 MDDC 上“瓶颈在带宽”的说法一致。

PC 侧，联发科在 [5 月 19 日](https://www.mediatek.com/tek-talk-blogs/signal-65-investigates-the-architectural-advantage-of-the-mediatek-kompanio-ultra-910)转述了 Signal65 对 Kompanio Ultra 910（NPU 890，50 TOPS）的测试：电池供电时性能只下降 6%（厂商转述的第三方结论）。5 月 26 日，Arm 发布了与 Google 合作的 [AI 原生 Googlebook](https://newsroom.arm.com/blog/arm-google-ai-native-googlebooks)，Arm 版 Chromebook/Googlebook 成了联发科 PC 线的主战场。

### 二、紫光展锐与三星：4nm 端边平台与 2nm 封装取舍

**紫光展锐（5/7）。** 在新紫光集团创新峰会上，展锐发布了端边 AI 芯片平台 **N9 系列**（4nm、Armv9.2 CPU，覆盖手机、平板、座舱、边缘网关）、Agentic AI 技术方案和 UniClaw 智能体（[C114](https://m.c114.com.cn/w16-1309933.html)）。NPU 算力和内存规格都没有公开，所以还判断不了它能跑多大的模型。和联发科同一周推出 “Claw” 类系统 Agent，说明中低端 SoC 厂商也开始把 Agent 当作平台卖点。另据 [Counterpoint](https://www.counterpointresearch.com/en/insights/global-smartphone-apsoc-market-share-quarterly)，展锐 Q1 份额升到 14%；联发科从 38% 降到 32%（后修订为 33%），主要原因是内存短缺冲击了入门和主流机型。

**三星。** 第三方机构 TechInsights 在 [5 月 5 日的分析](https://www.techinsights.com/blog/samsung-exynos-2600-brings-2nm-smartphones)中确认，Exynos 2600 采用 SF2 GAA 工艺，是首款上市的 2nm 手机 SoC，并且放弃了以往的单片裸片布局。5 月 14 日，[SamMobile 援引 SisaJournal](https://www.sammobile.com/?p=16658774) 爆料：Exynos 2700 可能放弃 FOWLP 封装来提高良率，改用 SoC 与 DRAM 并排的封装、两者都加散热块（HPB）。传闻规格为 SF2P、10 核 CPU、RDNA 5 GPU、LPDDR6、UFS 5.0（以上均为爆料，可信度低）。LPDDR6 如果按 14.4Gbps、64-bit 计算，峰值约 115GB/s，比 LPDDR5X-10.7Gbps 高三成多（推算）。这是下一代旗舰端侧 LLM tok/s 最直接的提升来源。5 月 28 日，[三星代工与 Cadence](https://www.edge-ai-vision.com/2026/05/samsung-foundry-and-cadence-accelerating-chiplet-solutions-for-physical-ai/) 宣布在 SF5A 上做面向物理 AI 的 Chiplet，代工方也在用封装和 Chiplet 换成本与良率。

### 三、华为与小米：工艺受限下的两条路

**华为（5/25）。** 何庭波在 [IEEE ISCAS 2026](https://www.huawei.com/cn/news/2026/5/ieee-iscas-tau-scaling) 上提出“韬(τ)定律”，即用时间缩微代替几何缩微。官方确认的信息有三条：秋季的麒麟芯片首次采用逻辑折叠（LogicFolding）；六年来设计并量产 381 款芯片；预计 2031 年高端芯片密度达到等效 1.4nm。具体增益只见于媒体转述，[IT之家](https://www.ithome.com/0/954/745.htm)等报道的口径是密度约 +53.5%（另有转述为 +55%）、P 核能效 +41%、峰值频率 +12.7%、首次超过 3GHz，官方新闻稿中没有这些数字。背景是 4 月 20 日 Pura 90 Pro 系列首发的麒麟 9030S，以及 TechInsights 确认的 SMIC N+3（7nm 级的演进）。如果密度增益兑现，最直接的用途是更大的 NPU 阵列和片上 SRAM，用来缓解带宽瓶颈。目前这些数字还没有第三方验证。

**小米。** 据[观察者网](https://www.guancha.cn/economy/2026_05_18_817486.shtml)报道，卢伟冰 5 月 16 日确认玄戒今年“一定”会迭代，并由旗舰首发。他同时否认了“跳过 O2 直接叫 O3”的说法，并称网传规格可信度不高。参照基线是玄戒 O1：N3E 工艺、190 亿晶体管、NPU 44 TOPS，出货已超过百万颗。5 月 21 日的[小米 17 Max](https://91mobiles.com/hub/xiaomi-17-max-china-launch-confirmed-may-21st) 仍然采用骁龙 8 至尊版 Gen5，自研芯片还没进入主力机型。

### 四、PC：本地 Agent 定义了内存门槛

**NVIDIA（5/13）。** RTX AI Garage 的[博客](https://blogs.nvidia.com/blog/rtx-ai-garage-hermes-agent-dgx-spark/)推荐 Nous Research 的 Hermes Agent 搭配 Qwen 3.6 在本地常驻。按厂商口径，Qwen 3.6 35B 约需 20GB 内存，DGX Spark（128GB 统一内存）可以全天运行 120B MoE；NVFP4 加 MTP 草稿模型最多提速 3 倍。按带宽推算，27B 稠密模型 4bit 每个 token 约读取 13.5GB 权重，在约 273GB/s 的 GB10 上 decode 上限约 20 tok/s。所以“30B 级本地 Agent”在统一内存机器上装得下，但跑得并不快。5 月 25 日，[HotHardware](https://hothardware.com/news/lenovo-leak-points-nvidia-n1x-laptop-chip-ahead-computex) 汇总了联想 Legion 7 N1X、Dell N1X 工程样等泄露信息（爆料），N1X 被传最高支持 128GB LPDDR5X。正式发布（RTX Spark）在 5 月 31 日，归入 6 月。

**AMD / Intel。** [AMD Q1 财报](https://www.amd.com/en/newsroom/press-releases/2026-5-5-amd-reports-first-quarter-2026-financial-results.html)（5/5）显示，客户端营收 29 亿美元，同比 +26%；本季度新增锐龙 AI PRO 400 和 Ryzen AI Embedded P100，但没有新 NPU 架构。192GB 统一内存的 Halo 平台要到 6 月才发布。Intel 在窗口内没有可核实的端侧 NPU 新品，Nova Lake NPU 6 仍停留在爆料阶段。

### 五、产业：内存与代工把成本推高

- **内存。** [TrendForce（5/14）](https://www.trendforce.com/presscenter/news/20260514-13044.html)：2Q26 LPDDR4X 合约价涨至少 70–75%，LPDDR5X 涨 78–83%；三星一步调价，SK hynix 分步调价。高端机回到 12GB 主流、16GB 占比下降，中端回到 8GB。品牌会减产，并“更多依赖云端”。12GB 恰好也是 Gemini Intelligence 的门槛。
- **IP。** [Arm FY26 Q4](https://www.sec.gov/Archives/edgar/data/0001973239/000197323926000062/exhibit992fye26q431-marx26.htm)（5/6）营收 14.9 亿美元（+20%），版税 6.71 亿美元（+11%），增长主要来自 v9/CSS 更高的单芯片费率和数据中心，手机出货本身偏弱。
- **代工。** [台积电 4 月营收](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000213/tsm-revenue20260508.htm)（5/8）为 4107.3 亿新台币（同比 +17.5%），增长主要来自 AI 加速器，手机 2nm 芯片要到下半年才放量。[TrendForce（5/7）](https://www.trendforce.com/presscenter/news/20260507-13036.html)称 8 英寸成熟制程将涨价，端侧 MCU 和电源芯片的成本也会受影响。
- **眼镜与边缘。** 根据[半导体产业纵横的梳理](https://www.36kr.com/p/3816031662382597)和[安凯微在集微峰会上的披露](https://news.10jqka.com.cn/20260530/c677097052.shtml)，国产 AI 眼镜主控芯片集中出现（详见第 4 节）。工业侧有 [SiMa.ai MLSoC 集成进 Emerson 工业 PC](https://finviz.com/news/356977/emerson-and-simaai-deliver-physical-ai-intelligence-to-the-industrial-edge)。

### 小结

5 月这一方向的三条主线都指向内存。第一，**手机 SoC 的差异从 TOPS 转向软件栈和常驻 NPU**：联发科双 NPU + eNPU 工具链、天玑 8550 的 LLM Booster、展锐 N9 + UniClaw，都在同一块硅片上靠软件和调度换体验。第二，**工艺受限的厂商在用电路和封装找回密度**：华为逻辑折叠、三星 2nm 非单片设计与并排封装，最终都是为了更大的 NPU、片上 SRAM 或更高的 DRAM 带宽。第三，**PC 端本地 Agent 把门槛定在约 20GB 以上内存、30B 级模型**，NVIDIA、AMD 都转向 128–192GB 统一内存，但 decode 速度仍然受约 270GB/s 级带宽限制（推算）。

成本是这一切的上限：LPDDR5X 一个季度涨约八成，高端手机停在 12GB。6 月要看的是：Computex 上 RTX Spark/N1X 与锐龙 AI Max PRO 400 的实测带宽与 tok/s；LPDDR6 手机首发时间；秋季麒麟的逻辑折叠能否得到第三方验证；以及联发科、展锐的系统级 Agent 是否在量产机上真正常驻运行。

## 4. 低功耗、存内计算与内存：眼镜与 MCU 进入 Transformer 时代

### 总览：5 月是“系统化”而不是“堆 TOPS”

整个 5 月（05-01~05-28），低功耗、存内计算与内存方向没有出现旗舰级新芯片。Embedded Vision Summit（5 月 11~13 日）、Google I/O（5 月 19 日）和集微峰会（5 月 27~29 日）是三个信息集中点，但能比较的硬数字主要来自学术原型和少数厂商口径。综合四周的条目，可以归纳为四条主线：

1. **存算一体从“宏”走向“系统”**：Mythic 收购 Videantis 补齐数字处理；学术侧出现 1181 TOPS/W 的亚阈值 SRAM 存算宏、3D NAND 内的 MoE 计算（NASiC）和商用 NAND 内位运算（MCFlash）。
2. **常开 AI 成为 MCU 出货的主力用途**：Ambiq 称超过 80% 的出货在跑 AI；Coral NPU 首块开发板把 Transformer 带到 1 TOPS 档；瑞萨通过收购 Irida Labs 补齐视觉软件。
3. **眼镜芯片的指标从 TOPS 变成“每次事件耗多少电”**：安凯微单次拍照 0.08mAh，Brilliant Labs Halo 用一颗 Alif MCU 做常开感知，Android XR 音频眼镜把推理放在手机上。
4. **内存是端侧 LLM 的真正上限，且供给在收紧**：VitaLLM 证明计算可以压到 59mW，但每 token 仍需从片外读约 0.6GB 权重；同时原厂把产能转向 HBM 与 1c DRAM，MLC NAND 现货价较去年底涨超 3 倍。

### 一、存内计算：产业补短板，学术刷能效

**产业侧。** 5 月 19 日 [Mythic 收购 Videantis](https://www.edge-ai-vision.com/2026/05/mythic-acquires-videantis-to-build-the-worlds-most-energy-efficient-ai-compute-platform/) 是本月唯一的存算一体并购。模拟 CIM 阵列只擅长矩阵乘，Softmax、LayerNorm、前后处理和视频编解码都要回到数字域。Videantis 的 VLIW+SIMD 多核正好补上这一块，但 Mythic 本次没有给出新的 TOPS/W 或模型规模。国内方面，[36 氪的产业综述](https://www.36kr.com/p/3816031662382597)（5 月 19 日）把炬芯 ATS362X 作为 SRAM-CIM 量产的样本：132 GOPS@500MHz，INT8 能效 6.4 TOPS/W，稀疏后 19.2 TOPS/W（厂商口径）。知存科技在 5 月 27 日对外披露，过去三年研发投入超过 15 亿元、流片超过 10 款，2026 年研发预算将超过过去三年总和（公司自报，见[中国日报网](https://cn.chinadaily.com.cn/a/202605/27/WS6a16be13a310942cc49aea46.html)）。后摩、苹芯、九天睿芯在窗口内没有可核实的新品发布。

**学术侧，数字差几个数量级，必须看口径。**

| 工作 | 日期 | 类型 | 关键数字 | 口径 |
|---|---|---|---|---|
| [亚阈值 SRAM-CIM（阳明交大，TCAS-I）](https://arxiv.org/abs/2605.00319) | 05-01 | 宏级流片，28nm | 1181.42 TOPS/W，7.24 TOPS/mm²，KWS 93.64% | 单时间步、高稀疏、宏级 |
| [MCFlash（科罗拉多州立）](https://arxiv.org/abs/2605.05119) | 05-06 | 商用 3D NAND 内位运算 | >10 亿次无错误；10k P/E 后 BER<0.015% | 真实芯片实测 |
| [NASiC（北大，DAC 2026）](https://arxiv.org/abs/2605.23294) | 05-22 周 | 3D NAND 存内 MoE | 架构级性能 4–114.8 倍 | 仿真 |
| [FCDC（铁电电容电荷域注意力）](https://arxiv.org/abs/2605.28208) | 05-27 | 非易失电荷域注意力 | 见原文 | 仿真/器件级 |
| 炬芯 ATS362X | 背景 | 量产 SRAM-CIM | 6.4 TOPS/W（INT8） | 芯片级、厂商口径 |

从 1181 TOPS/W 的宏到 6.4 TOPS/W 的芯片，差距来自 ADC/DAC、外围数字逻辑、片外搬运和稠密/稀疏口径。评估存算芯片时应看“目标网络在整芯片上的 µJ/inference”，而不是宏级峰值。5 月 30 日三星在 arXiv 公开的 [LP5X-PIM Sim](https://arxiv.org/abs/2606.00636)（GEMV 最高 6.2 倍加速，在窗口外，仅作背景）说明，手机内存里的 PIM 正在从论文走向产品；JEDEC 在 4 月 22 日也[预告](https://www.jedec.org/news/pressreleases/jedec%C2%AE-previews-lpddr6-roadmap-expanding-lpddr-data-centers-and-processing-memory)了 LPDDR6 PIM 标准即将完成。

### 二、MCU 与常开 NPU：出货靠 AI，竞争靠软件

- **Ambiq**（5 月 12 日，[Q1 财报](https://ambiq.com/news/ambiq-reports-first-quarter-2026-financial-results/)）：营收同比 +59.3%，超过 80% 的出货单元运行 AI 算法，前三大客户占比从 86% 降到约 71%，预计个人设备以外的营收今年翻倍。12nm SPOT 可在 300mV 下工作，按 3 月发布稿，Atomiq 集成 Ethos-U85，2027 年量产。亚阈值路线首次进入 FinFET 节点。
- **Ceva**（5 月 11 日，[Q1 财报](https://www.sec.gov/Archives/edgar/data/0001173489/000143774926015998/ex_960108.htm)）：AI 占授权收入超过 20%，季度签约 14 份。版税持平而授权增长 18%，说明一批集成第三方小 NPU 的芯片仍在设计期。
- **瑞萨**（5 月 7 日，[完成收购 Irida Labs](https://renesas.com/en/about/newsroom/renesas-completes-acquisition-irida-labs-expand-vision-ai-software-capabilities-and-accelerates)）：PerCV.ai 并入瑞萨 365 云平台，面向 RA MCU / RZ MPU。MCU 厂商的竞争从 NPU 硬件转向“模型+工具链+参考应用”。
- **Google × Synaptics Coralboard**（5 月 19 日，[I/O 展示](https://www.edge-ai-vision.com/2026/05/google-research-and-synaptics-partner-to-showcase-immersive-edge-ai-experiences-powered-by-the-coralboard-at-google-i-o-2026/)）：Astra SL2619，Torq NPU 子系统 1 TOPS，支持 CNN 与 Transformer，Gemma 3 270M 有硬件加速。Coral NPU IP 的设计目标是 512 GOPS、约 6mW 量级（[Google 文档](https://developers.google.com/coral/guides/intro-coralNPU)）。
- **Synaptics Astra SR80**（3 月发布，5 月 18 日[博客转载](https://www.edge-ai-vision.com/2026/05/the-new-baseline-for-human-centric-devices-starts-with-always-on-edge-ai-audio-introducing-the-synaptics-astra-sr80-series/)）：Cortex-M33 + 自研 NPU + HiFi 5 DSP，面向常开音频，算力与功耗未公开。
- 学术侧，MLSys 上的 [HyperTinyPW](https://proceedings.mlsys.org/paper_files/paper/2026/hash/2d04d97593c8c33d415337f408ed0e1b-Abstract-Conference.html) 用生成式权重压缩把更大的网络塞进 MCU；[CATS](https://arxiv.org/abs/2605.15694) 让 16 颗 nRF52840 协同跑 Transformer。这两项说明 MCU 端 Transformer 的瓶颈首先是 SRAM 容量。

横向看，Ethos-U55 级 MCU 的算力约 0.1~0.3 TOPS，STM32N6 为 600 GOPS，Coralboard 为 1 TOPS。同一 IP 在不同厂商口径下差异很大，应以目标模型的延迟、µJ/inference 和峰值 SRAM 占用作为比较基准。

### 三、AI 眼镜与可穿戴：从 TOPS 转向“每次事件的电量”

| 方案 | 日期 | 端侧做什么 | 关键数字 | 口径 |
|---|---|---|---|---|
| [Brilliant Labs Halo / Alif Balletto B1](https://www.eejournal.com/article/aiar-glasses-that-remember-where-you-left-your-keys/) | 05-14 | 音频活动检测；模型在手机 NPU 上，只有 embedding 上云 | 3.9mm×3.9mm 单芯片，349 美元 | 媒体 |
| [Android XR 音频眼镜](https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/) | 05-19 | 相机、音频、唤醒；Gemini 在手机/云端 | 今秋上市，兼容 iOS；芯片 9 月才确认为 AR1 | 官方 |
| [安凯微“孔明”](https://news.10jqka.com.cn/20260530/c677097052.shtml) | 05-27 | 视觉 SoC | 0.5~8 TOPS；单次拍照低至 0.08mAh，冷启动 150ms | 厂商口径 |
| [FotoNation TriSilica](https://www.edge-ai-vision.com/2026/05/fotonation-and-semifive-announce-strategic-collaboration-for-turnkey-development-of-trisilica-perceptual-ai-chip-family-using-samsung-foundry/) | 05-11 | 五模态感知融合 + 神经 ISP | 三星 8LPU，TS-210 年底 MPW；键合内存 | 官方，无性能数据 |
| 骁龙可穿戴平台至尊版（背景） | 3 月 | 端侧最高 2B 参数 | 首 token 0.2s，最高 10 tok/s | 媒体转述 |

同花顺 5 月 27 日的[产业报道](https://news.10jqka.com.cn/20260527/c676993825.shtml)指出，带显示的眼镜里光学成本占近一半，主控占两到三成；恒玄 6nm 的 BES6100 计划下半年送样（媒体口径）。工程上的含义是：单次拍照能耗被压到 0.08mAh 量级后，续航的大头变成常开语音唤醒和无线回传，这正是 Alif、Syntiant、Nordic Axon 这类亚 mW~mW 级常开推理芯片的位置。6 月 3 日酷芯微 ARS45 给出“6 TOPS / 300mW”（见 6 月），是眼镜主控首次把功耗写进标题。

### 四、边缘加速器与系统

- **VitaLLM**（5 月 1 日，[arXiv](https://arxiv.org/abs/2605.00320)，阳明交大，ISCAS 2026）：16nm 原型跑 BitNet b1.58 3B，decode 72.46 tok/s，面积 0.214mm²，功耗 59.12mW。**推算**：3B 三值权重约 0.6GB，片上只有 120KB，72 tok/s 需要约 43GB/s 片外带宽，接近 LPDDR5X 64-bit 的上限，59mW 不含 DRAM 功耗。计算已经不是瓶颈，内存才是。
- **DSPE**（5 月 9 日，[DAC 2026](https://arxiv.org/abs/2605.08615)）：28nm，122~345mW，POSIT8 下 109.4 TFLOPS/W，但缺少端到端的 tok/s。
- **SiMa.ai × Emerson**（5 月 26 日，[新闻稿](https://finviz.com/news/356977/emerson-and-simaai-deliver-physical-ai-intelligence-to-the-industrial-edge)）：MLSoC 进入 -40~70°C 的加固工业 PC。Modalix 为 6nm、50 TOPS、<10W（[产品简报](https://sima.ai/wp-content/uploads/2025/09/SiMa_MLSoC_Modalix_Product-Brief_09-09-25.pdf)）。
- **三星代工 × Cadence**（5 月 28 日，[物理 AI chiplet](https://www.edge-ai-vision.com/2026/05/samsung-foundry-and-cadence-accelerating-chiplet-solutions-for-physical-ai/)）：SF5A 车规工艺上的可平铺 AI chiplet，数字未披露。
- **ADI 15 亿美元收购 Empower**（5 月 19 日，[来源](https://www.edge-ai-vision.com/2026/05/analog-devices-to-acquire-empower-semiconductor-expanding-its-next-generation-high-density-power-portfolio-for-the-ai-era/)）：垂直供电 IVR，对高功率边缘 SoC 的瞬态供电有参考价值。
- 背景：NXP Ara240 DNPU 的 M.2 卡（Gateworks GW16168，40 eTOPS、16GB LPDDR4，[NXP 博客](https://www.nxp.com/company/about-nxp/smarter-world-blog/BL-NXP-GATEWORKS-INDUSTRIAL-EDGE-AI) 4 月 17 日）；DeepX 在 5 月 21 日与 Ultralytics 结盟，量产合作在 Computex 前后公布。

### 五、内存与存储：供给收紧，下一代节点在下半年

| 技术/事件 | 关键数字 | 时间 | 口径 |
|---|---|---|---|
| SK hynix 1c LPDDR6 | 16Gb，速度 +33%，功耗 -20%（对 LPDDR5X） | 3 月发布，下半年供货（[TrendForce](https://www.trendforce.com/news/2026/03/10/news-sk-hynix-develops-1c-lpddr6-dram-with-33-speed-gain-20-power-savings-ships-in-2h26/)） | 官方转述 |
| JEDEC LPDDR6 路线图 | PIM 标准接近完成，SOCAMM2 在制定 | 4 月 22 日 | 官方 |
| Sandisk HBF | NAND 硅片 2026 年底，带控制器的系统方案 2027 年初到年中 | 4 月 30 日财报会，TrendForce 5 月 5 日[报道](https://www.trendforce.com/news/2026/05/05/news-sandisk-long-term-deals-gain-scale-over-one-third-of-fy27-bits-reportedly-locked-50-in-sight-hbf-advances/) | 管理层口径 |
| 铠侠/Sandisk MSA-CBA | QLC 多堆叠键合，目标 1000+ 层；VLSI 2026 发表 | TrendForce 5 月 4 日[报道](https://www.trendforce.com/news/2026/05/04/news-kioxia-sandisk-to-demonstrate-qlc-nand-using-multi-stacked-cell-architecture-targeting-1000-layers/) | 媒体 |
| [MLC NAND 现货价](https://www.trendforce.com/news/2026/05/13/news-mlc-nand-spot-prices-reportedly-triple-since-late-2025-as-samsung-kioxia-exit-supply/) | 64Gb 涨超 300%；2026 年 MLC 产能 -41.7% | 05-13 | 媒体/TrendForce |
| UFS 5.0 / LPDDR5X-PIM | 三星 10.8GB/s（6 月）；Hot Chips 披露 PIM（8 月） | 窗口外 | — |

两点判断。第一，decode 速度由带宽决定：LPDDR5X-8533 64-bit 约 68GB/s，LPDDR6 在同位宽下约提升 33%。VitaLLM、[Lever](https://arxiv.org/abs/2605.16786)（闪存驻留 8B~14B 投机解码）和 NASiC 实际都在绕这堵墙。第二，原厂把产能转向 HBM、1c DRAM 和高层数 NAND：三星把华城 Line 12 的 2D NAND 产线转产 1c DRAM，MLC 现货价较去年底涨超 3 倍。这让工业、IoT 和可穿戴设备的小容量存储成本被动上升，也让“片上大 SRAM / 键合内存”（TriSilica）和“闪存内计算”更有商业动机。

### 小结与观察清单

5 月的信号是系统化：存算公司用并购补数字处理，MCU 厂商靠软件和 AI 出货增长，眼镜芯片用单次事件能耗定义竞争力，而端侧 LLM 的上限越来越清楚地落在内存带宽和容量上。需要警惕的是，本月多数产业公告（Mythic、FotoNation、SiMa×Emerson、Android XR 眼镜芯片、Halo）都**没有披露 TOPS/W、精度或可运行的模型规模**；能比较的硬数字几乎都来自学术原型，而且多为宏级或芯片级口径。

后续观察：(1) Computex（5 月 31 日起）上 DeepX、Kneron、Axelera Europa 的量产数据；(2) VLSI 2026（6 月）铠侠/Sandisk 多堆叠 NAND 与存算宏；(3) LPDDR6 首批终端与 JEDEC LPDDR6-PIM 标准落地；(4) Atomiq、TS-210、BES6100 等常开芯片的实测功耗；(5) 三星 LPDDR5X-PIM 在 Hot Chips 上的完整数据。

## 5. 顶会论文：NSDI、SenSys 与 MLSys 的端侧系统

**判断：** 5 月的顶会论文分成两段。上旬（5/4–5/16）是嵌入式与系统会议扎堆的“小模型周”：[NSDI 2026](https://www.usenix.org/conference/nsdi26)（5/4–6）、CPS-IoT Week 中的 [SenSys 2026](https://sensys.acm.org/2026/) 与 [RTAS 2026](https://2026.rtas.org/program/)（5/11–14），以及 [FCCM 2026](https://www.fccm.org/fccm-26-program/)（5/13–16）。下旬（5/18–22）是 [MLSys 2026](https://mlsys.org/Conferences/2026)，端侧 LLM 第一次在这个会上成规模出现。两段放在一起，最清楚的结论是：**端侧 AI 的瓶颈已经从“峰值算力”转到“调度、内存层级和散热”**。被拿出来讨论的变量是 DVFS 与解码策略的联合控制、KV 上下文的换入换出、SSD 和闪存作为内存扩展层，以及 μNPU 的算子覆盖；更大的 TOPS 很少被当作答案。

### 会期核对：哪些会落在 5 月窗口

| 会议 | 2026 会期 | 与端侧相关的看点 |
|---|---|---|
| NSDI | 5/4–6，Renton | 152 篇论文里端侧相关的很少，主要是 SoC GPU 上的视频分析 |
| ICASSP | 5/4–8，巴塞罗那 | 未检索到可核实的端侧硬件论文，本期不收 |
| SenSys（CPS-IoT Week） | 5/11–14，圣马洛 | 5/12 设“On-Device AI & Efficient Inference”专场；会议全称已改为“嵌入式人工智能与感知系统” |
| RTAS（CPS-IoT Week） | 5/12–14 | 5/14 设“ML Inference and Acceleration”场次 |
| FCCM | 5/13–16，亚特兰大 | 5/14 设“AI Inference”场次 |
| MLSys | 5/18–22，Bellevue | ExecuTorch、CORE、IntAttention 等端侧论文 |
| ISCAS | 5/24–27，上海 | 西湖大学脉冲 Transformer 加速器 |

ISCA、VLSI 研讨会和 MobiSys（6/21–25，剑桥）都在 6 月，AICAS 在 9 月，HotOS 今年没有举办。论文日期一律按宣讲场次所在日期标注。

### 一、上旬：嵌入式会议上的端侧 LLM（5/4–5/14）

**能效：解码策略也成了调频旋钮。** 西北大学的 [PELM](https://doi.org/10.1145/3774906.3802783)（SenSys，5/12）观察到，在 Jetson AGX Orin 上跑 LLaMA-8B，“20 层 + 0.6 GHz”和“32 层 + 高频”都能达到约 10 tok/s，所以降模型深度和降频率可以互相替代。它把自投机解码和可变验证深度加入 DVFS 的动作空间，用 branch-DQN 每 100 ms 做一次决策。论文口径的结果是最高加速 23.1%、能耗最多降低 52.4%，测试平台为 AGX Orin（64 GB，15–60 W）和 Orin Nano（8 GB，7–15 W）。它和下旬 MLSys 上交大的 [CORE](https://proceedings.mlsys.org/paper_files/paper/2026/hash/136b9a13861308c8948cd308ccd02658-Abstract-Conference.html)（Pixel 7 上 CPU/GPU/DDR 联合调频，TPOT 降低 27.8–39.6%）正好互补：CORE 只调硬件频点，PELM 同时调解码策略。两篇放在一起看，无风扇终端上的热余量应该成为推理运行时的输入。

**内存：KV 上下文与存储层被当成操作系统资源来管理。** 北大、北邮与清华 AIR 的[端侧 LLMaaS 上下文管理](https://doi.org/10.1145/3774906.3800479)（SenSys，5/12）把端侧模型当成多个 App 共享的系统服务，按块压缩、换出和重算 KV。该团队 2024 年技术报告的口径是，切换时延最多降低两个数量级，测试平台包括小米 14；正式版的数字我们没能核对。DGIST 的 [ZeroSwap](https://2026.rtas.org/program/#zeroswap)（RTAS 最佳论文，5/14）把 SSD 当作 GPU 内存的扩展，用于实时多 DNN 推理。据媒体转述，超出 GPU 内存时平均时延只增加 3.6%。普林斯顿的 [Remembrall](https://www.usenix.org/conference/nsdi26/presentation/ramanujam)（NSDI，5/6）则从另一面说明问题：Jetson Nano 和骁龙 450 这类 SoC 是算力受限、内存相对富余，在内存里常驻一个基座模型、只做少样本特化，就能把重训练开销降低 2.8–10 倍，中位精度提升 18.1–45.1%。

**数据通路：瓶颈常常在模型之外。** 港科大的 [MMEdge](https://doi.org/10.1145/3774906.3800485) 把传感器采集和编码流水化，在无人机测试平台（Jetson Orin Nano）上把端到端时延降低 75.83%。上交大与字节跳动的 [AutoFeature](https://doi.org/10.1145/3774906.3800493) 处理的是从 App 日志提取特征这一步，在 5 个线上服务中把端侧模型执行时延降低 1.33–4.53 倍。对眼镜和个性化智能体来说，“等数据”和“备数据”的时间可能比 NPU 推理本身还长。

**可穿戴：μNPU 能跑的仍是几百 KB 的卷积模型。** [PhysioLite](https://doi.org/10.1145/3774906.3802787)（SenSys 短文，5/13）把心电/肌电基础模型改写成约 370 KB 的 INT8 卷积网络。它在 MAX78000 和 Himax WE2 上的端到端时延为 10–20 ms，相对 WE2 纯 CPU 执行快 5–6 倍；推理功耗分别为 33.4 mW 和 103.8 mW，而 WE2 的空闲功耗高达 88.6 mW。μNPU 不支持动态注意力，这是基础模型下放到手表一类设备的硬门槛。同一届 SenSys 上，代尔夫特与诺基亚贝尔实验室的无电池可穿戴设备 Cheetah 获最佳论文提名，作者称充电 6 秒即可工作一整天（[TU Delft 记录](https://repository.tudelft.nl/record/uuid:8759fe9e-8acd-4ff2-8361-eaeae314edc9)）。

**FPGA：查表正在替代乘加。** FCCM 的 AI Inference 场次（5/14）有两篇值得关注。UCLA 与微软研究院的 [LUT-LLM](https://arxiv.org/abs/2511.06174) 在 AMD V80 上用向量量化查表跑 Qwen3 1.7B，论文口径是速度为 GPU 的 1.10–3.29 倍、能效为 GPU 的 3.05–6.60 倍。港城大的 [ViM-Q](https://arxiv.org/abs/2605.01935) 在 ZCU102 上运行 Vision Mamba，相比 RTX 3090 能效提升 59.8 倍。两者和 MLSys 上 IntAttention 的 32 B 查表 softmax 思路一致：用片上存储换算力，对 SRAM 大但功耗受限的端侧 NPU 有直接参考价值。

### 二、下旬：MLSys 把端侧 LLM 推上主会（5/18–5/22）

下旬的细节见各周雷达，这里只列结论。Meta 的 [ExecuTorch](https://proceedings.mlsys.org/paper_files/paper/2026/hash/236f915dd02af4f11927f67330b21d4b-Abstract-Conference.html)（最佳论文场次，5/19）在 Galaxy S25 Ultra 的 Hexagon NPU 上，把 Llama 3.2 1B 的 prefill 做到 2813–2977 tok/s，llama.cpp 的 NPU 路径只有 330–374 tok/s；但 NPU 的 decode（约 46 tok/s）反而低于 CPU（约 66 tok/s），说明图覆盖率和带宽比 TOPS 更关键。南科大的 [IntAttention](https://proceedings.mlsys.org/paper_files/paper/2026/hash/ea5ffdf7da91256ecd2770f9fd2dade9-Abstract-Conference.html) 发现，INT8 GEMM 之后 softmax 路径占 attention 时间的 57–65%，改用整数实现后在 RK3588S2 上加速 2.1–3.7 倍。NVIDIA 的[客户端显存受限推理](https://proceedings.mlsys.org/paper_files/paper/2026/hash/7cd265ae802235b8d5778a4a96ff22dd-Abstract-Conference.html)在小显存上跑 Qwen3-235B，达到 6.7–7.7 TPS。KV 方向有 [Kitty](https://proceedings.mlsys.org/paper_files/paper/2026/hash/e4d8d1b5120be349d3fff8878650cf45-Abstract-Conference.html)（2bit）和 [SkipKV](https://proceedings.mlsys.org/paper_files/paper/2026/hash/45c1f6a8cbf2da59ebf2c802b4f742cd-Abstract-Conference.html)（按句驱逐）。此外还有两篇已被录用、本月以预印本形式出现的论文：北航与华为的 [ReMoE](https://arxiv.org/abs/2605.27081)（ICML 2026，Jetson Orin NX 上 decode 提速 1.77–1.99 倍）和北大的 [NASiC](https://arxiv.org/abs/2605.23294)（DAC 2026，在 3D NAND 内做 MoE 存内计算）。ISCAS 上，西湖大学的[脉冲 Transformer 加速器](https://cenbrain.westlake.edu.cn/info/1017/1663.htm)面向具身智能，能效最多提升 10.9 倍，工艺与功耗未披露。

### 三、全月归纳：三条主线

| 主线 | 上旬证据 | 下旬证据 |
|---|---|---|
| 调度与散热决定能效 | PELM（能耗 -52.4%） | CORE（TPOT -27.8~39.6%） |
| 内存层级成为一等公民 | LLMaaS 上下文管理、ZeroSwap、Remembrall | NVIDIA 客户端推理、Kitty、ReMoE、NASiC |
| 非 GEMM / 查表数据通路 | LUT-LLM、ViM-Q、PhysioLite | IntAttention、ExecuTorch 的图覆盖率 |

需要说明口径：上旬的实测平台几乎都是 Jetson、MCU 和 FPGA，真正在手机上测量的只有技术报告里的小米 14 和 AutoFeature 的线上服务。手机 NPU 的一手实测仍然集中在下旬 MLSys 的 ExecuTorch 和 CORE。我们的判断是，到 6 月的 ISCA、VLSI 和 MobiSys，学术界会给出更多芯片级与手机级数据；短期内对终端厂商最可落地的，是 PELM、CORE 这类“调频 + 解码”联合策略，以及按 OS 分页思路管理 KV 与闪存的方案。

## 6. 5 月 arXiv 端侧硬件论文精选

### 总览：五月 arXiv 端侧硬件论文的三条主线

2026 年 5 月（05-01 ~ 05-28）arXiv 上与端侧 AI 硬件和系统相关的论文，可以归为三条主线。第一，**“NPU 祛魅”**：手机 NPU 对卷积类模型优势明显，但跑 LLM 时，收益取决于算子覆盖、调度开销和量化格式，而不是 TOPS。第二，**“内存装不下”成为主约束**：投机解码、MoE、闪存驻留和 KV 量化都在为 8~16GB 的 DRAM 重新设计。第三，**端侧智能体开始被当作独立负载来测量**：KAIST 的 Agent-X 和 Brave 的 AgentStop 第一次把智能体的时延构成和能耗算清楚。芯片侧，5 月上旬有两颗 LLM 加速器上了 arXiv，分别是港科大 ISSCC 2026 的 ReRAM 堆叠芯片和阳明交大 0.214mm² 的三值加速器；下旬则有北大的 3D NAND 存内 MoE 和铁电电荷域注意力，两者都是架构或仿真级工作。

下文的日期均为 arXiv v1 提交日。05-15 之后的论文已在各周“硬件雷达”收录，这里只做综合，数字沿用当时的核验结果。

### 一、专用芯片：LLM 加速器从 prefill 转向 decode

本月最硬的芯片数据来自港科大。他们把 ISSCC 2026 第 31.1 篇论文（2 月 18 日报告）的全文在 5 月 10 日放上 [arXiv](https://arxiv.org/abs/2605.09375)。芯片在 55nm 逻辑裸片上用 2048 个面对面凸点堆叠了 4 颗 ReRAM 裸片，在 100MHz 下提供 25.6GB/s 带宽和 8MB 容量；4 芯片系统可扩到 32MB / 102.4GB/s，足以放下草稿模型的全部码本。它的判断很明确：在边缘加速器上，投机解码的时延仍由权重外存访问主导，其中 60% 以上来自目标模型。因此它用局部旋转单元实现 W4A8 无离群量化，同时用 ReRAM 近存放草稿模型，再用自适应并行投机解码提高带宽利用率。整体实测 14.08~135.69 token/s，比 BF16 投机解码快 4.46~7.17 倍、省能 3.74~4.85 倍。在统一补上 LPDDR3 的公平对比下，LLaMA2-7B 在 MT-Bench 上解码 17.82 token/s、123.41 mJ/token。作者特别指出，多数前作（C-Transformer、Slim-Llama 等）只优化 prefill，而真正的瓶颈在 decode。

阳明交大的 [VitaLLM](https://arxiv.org/abs/2605.00320)（ISCAS 2026）走的是另一个极端：面向 BitNet b1.58 三值模型，用无乘法器的 TINT 核加上复用 Booth 数据通路的 BoothFlex 核。16nm 原型在 1GHz/0.8V 下只有 0.214mm²、120KB 片上存储、59.12mW，BitNet b1.58 3B 解码 72.46 token/s。按我们的推算，3B 三值权重约 0.6GB，72 token/s 意味着片外每秒要读 40GB 以上，而论文没有给出 DRAM 带宽，因此这个数字更像“核心算力上限”，而非系统实测。

[DSPE](https://arxiv.org/abs/2605.08615)（DAC 2026）面向 DeepSeek 推理定制了 DA-Posit 格式，28nm、8.23mm² 下宣称 109.4 TFLOPS/W（POSIT8，0.6V/200MHz）。但它基于综合与布局布线评估，也没有给出 token/s，参考价值低于前两者。下旬的北大 [NASiC](https://arxiv.org/abs/2605.23294)（DAC 2026）在 3D NAND 内完成“选专家 + 算专家”，架构级评估性能为前作的 4~114.8 倍。[FCDC](https://arxiv.org/abs/2605.28208) 用 HZO 铁电电容做非易失电荷域注意力，纯仿真下对优化后的服务基线只有 1.4~4.7 倍能耗优势。另外，科罗拉多州立大学的 [MCFlash](https://arxiv.org/abs/2605.05119) 证明，在美光 64 层与 176 层商用 3D NAND 上，只用标准用户态指令就能无差错地执行 AND/OR/XNOR/NOT 位运算。它暂时没有 AI 负载，但与 NASiC 一起说明“在闪存里算”正从概念走向可部署。

### 二、手机 NPU：同一颗 NPU，视觉快 3.9 倍，LLM 却可能更慢

维尔茨堡大学为 Mobile AI 2026 挑战赛设计的[去噪网络](https://arxiv.org/abs/2605.03680)只用 3×3 卷积、ReLU 和最近邻上采样等 NPU 原生算子。1.96M 参数、Full HD 输入下，天玑 9500 NPU 耗时 34.0ms，骁龙 8 Elite NPU 耗时 46.1ms，而移动 GPU 平均 132.0ms，NPU 快 2.86~3.88 倍。作者称之为“推理反转”。

LLM 的情况相反。莱顿大学的 [When NPUs Are Not Always Faster](https://arxiv.org/abs/2605.27435) 在骁龙 8 Gen 3 上用 llama.cpp 测得：prefill 阶段 NPU 的 MUL_MAT 比 6 核 CPU 慢 1.27~1.62 倍，decode 端到端只快 1.05~1.20 倍，全量卸载到 NPU 后电池消耗反而增加 22~51%。[Quant.npu](https://arxiv.org/abs/2605.20295) 则从量化格式入手：在骁龙 8 Elite 上，Qwen2.5-3B（W4A8）prefill 达到 969.72 tok/s，ExecuTorch 为 808.10 tok/s，但 decode 与基线相同。MLSys 的 [ExecuTorch](https://proceedings.mlsys.org/paper_files/paper/2026/hash/236f915dd02af4f11927f67330b21d4b-Abstract-Conference.html)（arXiv 版 2605.08195）在 Hexagon NPU 上把 Llama 3.2 1B 的 prefill 做到约 2,900 tok/s。三者合读的结论是：NPU 的价值主要在 prefill，前提是图能整体落在 NPU 上；decode 受带宽限制，NPU 帮不上太多。

### 三、PC 与 Mac：统一内存决定能跑多大

巴赫切谢希尔大学的 [Silicon Showdown](https://arxiv.org/abs/2605.00519) 是本月最直接的消费级硬件对比。显存放得下时，RTX 5090 最快：Llama-3.3-70B（IQ3_XXS）46.5 tok/s，Qwen3-Next-80B-A3B（Q2_K_XL）76.1 tok/s。一旦用 Q4_K_M 并卸载 25~28% 到 CPU，速度就跌到 2.3~4.7 tok/s。Apple 统一内存可以原生跑 4bit：M3 Ultra（819GB/s）上 Llama-3.3-70B 为 13.1 tok/s，接近“带宽 ÷ 约 35~40GB 权重”推算出的 20 tok/s 上限；M4 Pro 跑 80B-A3B MoE 达 52.3 tok/s。论文称 M3 Ultra 的 tokens/J 最高是 RTX 5090 的 23 倍，但没有给出测试条件，只能当作方向性结论。

在 Mac 上做软件优化也有收获。Illumina 作者的 [int4 KV Cache](https://arxiv.org/abs/2605.05699) 在 M1 上让 Gemma-3 1B 的解码比 fp16 快 0.9~8.2%，原因是统一内存带宽是瓶颈，量化省下的读取量超过了反量化开销。Mindbeam 的 [Litespark](https://arxiv.org/abs/2605.06485) 用 SDOT/VNNI 点积指令跑 BitNet 2B，在 M5 Max 上达到 39.92 tok/s，A18 Pro 上 19.60 tok/s，内存不到 1GB。不过它的倍数是相对未优化的 PyTorch。另一项研究观察到 [Apple MPS 解码延迟的非单调突变](https://arxiv.org/abs/2605.08913)：在某些解码长度区间延迟最高跳升 21 倍，提醒端侧基准测试不能只取单点。下旬的 [LlamaWeb](https://arxiv.org/abs/2605.20706) 把 llama.cpp 搬到 WebGPU，在 16 台设备上内存少 29~33%、解码吞吐高 45~69%。[Memory-Bound but Not Bandwidth-Limited](https://arxiv.org/abs/2605.30571) 则提醒，batch-1 解码常常连带宽都跑不满，“量化省带宽”必须由内核真正兑现。

### 四、内存墙：投机解码、MoE 与闪存驻留

佛罗里达大学的 [CATS](https://arxiv.org/abs/2605.11186) 指出，传统投机解码假设内存能同时放下两个模型，这在 16GB 级的 Jetson 上不成立。它改用自投机解码，峰值内存等于目标模型本身：在 Vicuna-7B 2/6/8GB 预算下提速 2.82~3.16 倍，最高 5.08 倍。清华的 [DECO](https://arxiv.org/abs/2605.10933) 只激活约 20% 路由专家，就在相同总参数下追平稠密模型；在 Jetson AGX Orin 上解码 44.24 tok/s，稠密基线为 15.09 tok/s，快 2.93 倍。

下旬的工作继续沿这条线推进。清华的 [Lever](https://arxiv.org/abs/2605.16786) 把 8B~14B 目标模型放在手机闪存里：OnePlus 12 上 Qwen3-14B 一次验证耗时 2108.3ms，其中闪存 I/O 占 93.3%；投机批量验证后几何平均提速 2.93 倍，但 Qwen3-8B 全闪存驻留时仍只有约 1.75 tok/s。北航/华为的 [ReMoE](https://arxiv.org/abs/2605.27081) 微调路由以提高专家复用，在 Orin NX 上解码提速 1.77~1.99 倍。Meta 的 [MobileMoE](https://arxiv.org/abs/2605.27358) 在 Galaxy S25 和 iPhone 16 Pro 的 CPU 上分别做到 138.1 和 204.6 tok/s。港中文（深圳）/理想汽车的 [Dense2MoE](https://arxiv.org/abs/2605.26496) 则在 Jetson Thor-U 上把时延从 307.5ms 降到 271.0ms。合起来看，端侧大模型的关键硬件指标正变成 **DRAM 容量、UFS 随机读带宽，以及 NPU 对动态稀疏的支持**。

### 五、端侧智能体：第一次被当作独立负载测量

KAIST 的 [Agent-X](https://arxiv.org/abs/2605.10380)（MobiSys 2026）在 M4 Pro Mac mini 上剖析了 TinyAgent-7B：每个任务平均 35.4 秒，decode 占 68.7%。它通过改写提示词提高前缀缓存命中（不可缓存 token 从 1,711 降到 519），再用不需要草稿 LLM 的投机解码，最终端到端提速 1.61 倍。Brave 的 [AgentStop](https://arxiv.org/abs/2605.15206) 在 M1 Max 上跑 Qwen3-Coder-30B-A3B：GPU 功率反复超过 40W，温度接近 95°C，失败的 SWE-Bench 任务平均耗 3004.6 mWh，是成功任务的两倍。提前终止可以省下 15~20% 的浪费能耗。[Agentic Performance at the Edge](https://arxiv.org/abs/2605.10384)（MobiSys AutoEdge 研讨会）发现，8B 以下模型的智能体质量并不随参数量单调变化，选模型和设计工具流程同样重要。下旬，港科大/上交的 [MobileExplorer](https://arxiv.org/abs/2605.26546) 在 Galaxy S24 上测得 2B VLM GUI 智能体单步约 40 秒。

生产落地方面，淘天的 [RecGPT-Mobile](https://arxiv.org/abs/2605.04726) 把 Qwen3-0.6B 量化模型部署到淘宝手机端，上千万用户的 A/B 实验中 GMV 平均提升 2.5%。不过论文没有给出任何硬件指标。

### 六、MCU、单板机与安全

代尔夫特理工的[多 MCU 切分推理](https://arxiv.org/abs/2605.09357)让 3~8 颗 Teensy 4.1（Cortex-M7、1MB RAM）协同跑通 MobileNetV2，但单次推理要 43~57 秒，其中通信占大头。这与 05-15 RWTH 的 [CATS](https://arxiv.org/abs/2605.15694)（16 颗 nRF52840 经 BLE 协同跑 14M ViT）属于同一路线。塔尔图大学在[树莓派上评测 25 个模型](https://arxiv.org/abs/2605.03111)：Pi 4 上 Granite4 Tiny 7B 为 2.5 tok/s、0.90 tok/J（功耗为估算值）。这给出了无 NPU 的 ARM 单板机的现实下限。下旬的 [LLMForge](https://arxiv.org/abs/2605.17653) 做边缘硬件感知的结构搜索；Purdue 的 [Speed Kills](https://arxiv.org/abs/2605.17707) 发现 7 种边缘 AI 加速器中有 6 种存在混淆代理漏洞，涉及 128 款以上 SoC。

### 速查：本月 arXiv 端侧实测数字（论文口径）

| 平台 | 负载 | 结果 | 来源 |
|---|---|---|---|
| 港科大 55nm + ReRAM 堆叠（4 芯片） | LLaMA2-7B W4A8 | 17.82 tok/s，123.41 mJ/token | ISSCC 31.1 |
| VitaLLM 16nm，59mW | BitNet b1.58 3B | 72.46 tok/s 解码 | ISCAS 2026 |
| 天玑 9500 / 骁龙 8 Elite NPU | 1.96M 去噪，Full HD | 34.0 / 46.1 ms | Würzburg |
| Jetson AGX Orin | DECO 稀疏 MoE | 44.24 tok/s（稠密 15.09） | 清华 |
| M3 Ultra / RTX 5090 | Llama-3.3-70B | 13.1（4bit）/ 46.5（IQ3）tok/s | Silicon Showdown |
| M5 Max / A18 Pro CPU | BitNet 2B | 39.92 / 19.60 tok/s | Litespark |
| M4 Pro Mac mini | TinyAgent-7B 智能体 | 35.4s/任务，Agent-X 后快 1.61 倍 | KAIST |
| Raspberry Pi 4 | Granite4 Tiny 7B Q4 | 2.5 tok/s，0.90 tok/J（估算） | Tartu |

### 小结

五月的 arXiv 论文给端侧芯片设计者传达了一致的信号：**decode 阶段受带宽限制，容量受 DRAM 限制，而 TOPS 是最不紧的约束**。港科大的 ReRAM 堆叠芯片和 VitaLLM 都把优化重点放在 decode 与外存访问上；手机侧的研究证明，NPU 的收益由软件栈和算子覆盖决定；Mac/PC 侧的数据说明，本地能跑多大模型由统一内存容量决定，这也为月底 Computex 上的 RTX Spark 和 Ryzen AI Max 埋下了伏笔。端侧智能体在本月首次被量化：decode 占时延近七成，失败轨迹最耗电。下一代端侧 SoC 的竞争点因此更可能落在内存容量与带宽、近存/存内计算、动态稀疏支持和前缀缓存上，而不是峰值算力。存疑之处：多篇论文存在口径不一致（Silicon Showdown 的 23 倍能效、VitaLLM 未给外存带宽、DSPE 未流片、树莓派功耗为估算值），引用时应带上口径说明。

## 7. 总结：对端侧智能体意味着什么，以及 6 月该看什么

**对端侧智能体的含义**

1. **先选对运行时，再谈芯片。** 同一颗 Hexagon NPU，ExecuTorch 与 llama.cpp NPU 路径的 prefill 相差 7.5–9 倍；投机解码（Gemma 4 MTP、LiteRT-LM v0.11）在 5 月成为官方运行时的标配。智能体要多轮生成，短期最有效的投入是图覆盖率、量化格式和投机解码。
2. **内存决定谁能用上端侧智能体。** 12GB 门槛遇上 LPDDR5X 季涨近八成，中端机很可能被挡在高级端侧 AI 功能之外；8GB 设备只能跑 1–3B 常驻模型，更大的模型要靠闪存分页和 MoE。
3. **平台化开始了。** 联发科把常驻感知和跨应用执行做进 SoC 平台、Google 推出 AppFunctions 与 Gemini Intelligence、NVIDIA 推本地常驻智能体，5 月是端侧智能体从“应用 demo”走向“平台能力”的起点。
4. **眼镜与 MCU 是新的低功耗战场。** 眼镜芯片只做感知和唤醒，大模型在手机或云端；评价指标变成“每次拍照 / 每次唤醒的耗电”。

**留给 6 月的问题（结论已写在 6 月硬件洞察）**

- PC 的统一内存竞赛：Computex 上 RTX Spark（N1X，128GB / 300GB/s）和 Ryzen AI Max PRO 400（192GB）正式发布。
- Apple 的端侧模型路线：WWDC26 公布 AFM 3，20B 稀疏端侧模型把权重放闪存，并以 12GB 为门槛。
- 存内计算与 PIM：VLSI 2026 上联发科 3nm 存内计算 NPU、台积电 2nm 存内计算编译器，ISCA 上 PIM 进入手机 LPDDR。

> 口径说明：标“官方”的是厂商发布的数字，“媒体实测”和“第三方实测”是独立测试，“爆料”未经确认，“推算”或“估算”是本文按公开参数计算的结果。5 月没有检索到新品的方向：高通、Apple 都没有旗舰新芯片；Intel、瑞芯微、Hailo、DeepX、知存、苹芯、后摩等在窗口内没有可核实的新动态；内存侧的 LPDDR6、UFS 5.0、HBF 节点分别在 3 月、6–8 月，只作背景。本期上半月部分为 2026-10 回填，检索依据与周报同一套规则。
