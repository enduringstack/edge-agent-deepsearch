# 开源大项目白名单

> github MCP 采集只盯本表项目 + 本周爆火新 agent 仓。非白名单小/个人仓一律不收。
> 采集规则：
> - **现有仓只提取「重大更新」**：版本号大版本发布（v1.27.0 / v0.24.0 这种）或重要 feature release。**每日 CI build（如 llama.cpp 的 b9823）、patch/小修、常规 commit 不算**，不提取。
> - **本周爆火 agent 仓**：created 在过去 7 天内 + agent 相关 + star 短时暴涨（爆火，主 agent 判断）。
> - release notes 必须从官方 release 页取，不许用二手解读。
> - github MCP 配置见 `docs/references/mcp-setup.md`（项目级 `.mcp.json`，需 `GITHUB_PERSONAL_ACCESS_TOKEN`）。

## 端侧/边缘推理引擎与端侧模型（22）
- llama.cpp — `github.com/ggml-org/llama.cpp`（GGUF 标准，CPU/Metal/CUDA/Vulkan）
- ExecuTorch (Meta) — `github.com/pytorch/executorch`（PyTorch 边缘部署）
- MLC-LLM — `github.com/mlc-ai/mlc-llm`（TVM 编译，跨平台含 WebGPU）
- ONNX Runtime (Microsoft) — `github.com/microsoft/onnxruntime`（工业标准，EP 最广）
- MNN (Alibaba) — `github.com/alibaba/MNN`（移动/嵌入式轻量）
- NCNN (Tencent) — `github.com/Tencent/ncnn`（移动端）
- MediaPipe (Google) — `github.com/google-ai-edge/mediapipe`（Gemma/Llama on Android/iOS）
- LiteRT (Google, ex-TF Lite) — `github.com/google-ai-edge/litert`（移动推理）
- LiteRT-LM (Google) — `github.com/google-ai-edge/LiteRT-LM`（端侧大模型运行时，Gemma / Gemini Nano 在 Android、iOS、Web 上的推理栈）
- Core ML Tools (Apple) — `github.com/apple/coremltools`（iOS 部署）
- MLX (Apple) — `github.com/ml-explore/mlx`（Apple Silicon）
- OpenVINO (Intel) — `github.com/openvinotoolkit/openvino`（边缘推理）
- PowerInfer (SJTU) — `github.com/Tiiny-AI/PowerInfer`（CPU+GPU 混合端侧大模型。原 `PowerInfer/PowerInfer` 组织路径已 404，项目迁至 Tiiny-AI）
- RKLLM (Rockchip) — `github.com/airockchip/rknn-llm`（瑞芯微 RK3588/RK3576 NPU 端侧 LLM 运行时）
- Ryzen AI Software (AMD) — `github.com/amd/RyzenAI-SW`（AMD 锐龙 AI PC 的 NPU 推理工具链与运行时；约 900 星）
- GenieX (Qualcomm，原 Nexa SDK) — `github.com/qualcomm/GenieX`（骁龙 Hexagon NPU 上跑 GGUF 等模型的端侧运行时；约 8500 星）
- HailoRT (Hailo) — `github.com/hailo-ai/hailort`（Hailo 边缘 AI 加速器运行时）
- DX-All-Suite (DEEPX) — `github.com/DEEPX-AI/dx-all-suite`（DEEPX NPU 的编译器与运行时套件）
- Cactus (Cactus Compute) — `github.com/cactus-compute/cactus`（手机端侧推理引擎；约 6200 星）
- MiniCPM (面壁/OpenBMB) — `github.com/OpenBMB/MiniCPM`（端侧大模型；约 1.2 万星）
- MiniCPM-V (面壁/OpenBMB) — `github.com/OpenBMB/MiniCPM-V`（端侧多模态大模型；约 2.7 万星）
- VoxCPM (面壁/OpenBMB) — `github.com/OpenBMB/VoxCPM`（端侧语音合成；约 4 万星）

> 2026-10-31 加入初创与芯片厂的端侧运行时：qualcomm/GenieX（Nexa AI 被高通收购后 nexa-sdk 迁入此仓）、hailo-ai/hailort、DEEPX-AI/dx-all-suite、cactus-compute/cactus、MemTensor/MemOS，按用户“初创公司也加入白名单”的要求。HailoRT 与 DX-All-Suite 星数不高，但都是厂商官方运行时，与 RKLLM、RyzenAI-SW 同类。未加：PrismML 的 llama.cpp fork（自动构建 tag）、needle 与 Bonsai-demo（不用 Releases）、om-ai-lab 各仓（Releases 停在 2025 年初）。

> 2026-10-31 加入 amd/RyzenAI-SW：AMD 锐龙 AI PC 的 NPU 推理栈只在这个仓发布版本（1.9.0 取消 NPU 上大模型的 4K/16K 上下文上限），amd.com 没有对应的带日期稿件。星数不到 1000，但它是厂商官方运行时，与 RKLLM 同类，用户同意加入。

> 2026-10-24 加入 LiteRT-LM：它是独立仓，白名单原来只有 `litert`，7–9 月 v0.14~v0.17 的重要版本（多 token 预测、Android 原生 CLI、NPU 音频加速）全部漏收，只能写进周报摘要。

> 2026-10-21 加入 OpenBMB 三仓：面壁是 24 家规范厂商之一，但官网新闻只链到微信公众号（不在白名单），端侧模型实际只在 GitHub/HF 发布，按旧规则永远进不了正式周报（1–5 月月度对账发现 VoxCPM 2、MiniCPM-V 4.6 等全部漏收）。AgentCPM（约 800 星）未达大项目标准，不加。

## Agent 应用
- nanobot (HKUDS) — `github.com/HKUDS/nanobot`（轻量开源 AI agent，工具/聊天/工作流；港大 HKUDS 实验室）
- MemOS (MemTensor) — `github.com/MemTensor/MemOS`（智能体记忆操作系统；约 1.2 万星。属于相邻 Agent 平台，是否端侧按每次发布内容判断）
- Orchard (Microsoft Research) — `github.com/microsoft/Orchard`（Agent 训练与 Kubernetes 环境基础设施；属于相邻 Agent 平台，不是端侧 Agent）
- Limioryn — `github.com/YINGLINGH/limioryn`（本周新仓快速获得 100+ stars；面向 ESP32/STM32/Linux SBC 的端云 Agent 框架，提供 Capability 工具、设备执行、ACK、对账与恢复闭环）

## 维护规则

> **仓址必须写具体路径。** RKLLM 一度只写「仓址以官方为准」，`REQUIRED_GITHUB_PROJECTS` 因此从不包含瑞芯微仓，
> 采集器连续两周扫不到它的真实 release（06-17 的 v1.3.0、09-29 的 v1.3.1）；PowerInfer 的组织路径失效后也静默
> 失联。**没有具体仓路径的条目等于不存在**——机器清单只认路径，人读文档里的描述性文字不参与任何过滤。
- 增删在本文档进行，不靠记忆。新项目要"业界认可大项目"（知名实验室/公司/高 star+影响力），个人小仓不收。
- 一个仓只在「最近 7 天有重大 release」时才进本周 run。
