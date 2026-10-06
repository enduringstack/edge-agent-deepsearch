# 厂商调研方法总结（调研记忆）

> 本文件是调研 agent 的厂商检索记忆，基于 `vendor-whitelist.md`（官方域名白名单）扩展。
> **端侧重点关注厂商举例**：Apple、Google、NVIDIA。这只是举例，其余厂商同样要覆盖，不许只搜这三家。
> 规范官方来源：9 家设备厂商 + 10 家模型厂商（含 NVIDIA/StepFun）+ 5 家模型实验室补充来源；另查 8 家中国互联网公司研究项目。完整集合由 `agent/research_collection.py` 机械校验。
> 不可违反规则：非论文条目必须命中 `vendor-whitelist.md` 官方域名；公司项目按 arXiv affiliation + GitHub org 搜；不拿新闻、社媒、GitHub release、二手解读冒充官方。

## 通用检索方法

### arXiv affiliation 搜法（公司项目主力路径）

arXiv 自身搜索只匹配标题和摘要，不直接按作者 affiliation 过滤。抓公司项目的实操路径：

1. **websearch 全文匹配**：`site:arxiv.org "Kuaishou"` 加主题词（如 `mobile agent`），命中 affiliation 出现在正文 / 作者列表的论文。
2. **邮箱域名反查**：很多公司论文作者邮箱是公司域名（如 `@meituan.com`、`@vivo.com`），用 `"@meituan.com" arxiv` 这类查询能定位。
3. **Semantic Scholar / Google Scholar**：按 affiliation 字段过滤更准，配合主题词 `edge agent`、`on-device LLM`。
4. **GitHub org 论文链接**：公司研究 GitHub 仓库 README 常挂论文 PDF 和 arXiv 链接，是 affiliation 之外最可靠的一手来源。

### 官方动态识别（非论文条目硬约束）

- 只认 `vendor-whitelist.md` 列出的官方域名及其子域名。
- 官方技术博客 / 官方产品发布可收录，`source_tier=官方动态`，排序最前，必须命中官方域名。
- 新闻站、社媒、第三方解读、GitHub release notes、公众号搬运一律排除。

---

## 设备厂商（9 家）

| 厂商 | 官方动态来源 | websearch 关键词 | arXiv affiliation | GitHub / 重要页面 |
|---|---|---|---|---|
| Apple | `machinelearning.apple.com`（ML 研究博客）、`developer.apple.com`（Apple Intelligence / CoreAI 文档） | `"Apple Intelligence" on-device`、`site:machinelearning.apple.com`、`CoreAI`、`Apple Foundation Models` | `Apple` / `Apple Inc`（论文极少，主要靠官方博客） | `machinelearning.apple.com`、`developer.apple.com/machine-learning` |
| Samsung | `research.samsung.com/blog`、`research.samsung.com/artificial-intelligence`、`news.samsung.com` | `"Samsung Gauss"`、`"Galaxy AI" on-device`、`site:research.samsung.com` | `Samsung Research`、`Samsung AI Center (SAIC)`、`Samsung Electronics` | `research.samsung.com/blog`（AI 主题筛选） |
| Huawei | `developer.huawei.com/consumer/cn/hiai/`（HiAI Foundation）、`huaweicloud.com` Pangu 产品页、`huawei.com` | `"Huawei Pangu"`、`"HiAI"`、`"HarmonyOS AI"`、`site:developer.huawei.com` | `Huawei`、`Huawei Noah's Ark Lab`、`HiSilicon`、`海思` | `developer.huawei.com` HiAI、`huaweicloud.com` Pangu |
| Qualcomm | `aihub.qualcomm.com`（AI Hub 模型库）、`qualcomm.com/developer`、`developer.qualcomm.com`（技术博客） | `"Qualcomm AI Hub"`、`"Hexagon NPU"`、`site:aihub.qualcomm.com` | `Qualcomm AI Research`、`Qualcomm` | `github.com/qualcomm/ai-hub-models`、`aihub.qualcomm.com/models` |
| MediaTek | `neuropilot.mediatek.com`、`neuropilot-developer.mediatek.com`、`mediatek.com/technology/ai` | `"MediaTek NeuroPilot"`、`"MediaTek edge AI"`、`site:mediatek.com` | `MediaTek`（论文少，主要靠官方门户） | `neuropilot.mediatek.com`、`mediatek.com/technology/ai` |
| Xiaomi | `mimo.xiaomi.com`（MiMo 模型博客）、`mi.com/global/brand/ai/xiaomi-hyperai`（HyperAI） | `"Xiaomi MiMo"`、`"Xiaomi HyperAI"`、`"HyperVL"`、`site:mimo.xiaomi.com` | `Xiaomi`、`HyperAI Team, Xiaomi Corporation`、`Xiaomi AI Lab`、`小米` | `mimo.xiaomi.com/blog`（HyperVL 等端侧多模态论文挂此） |
| OPPO | `oppo.com`（AndesGPT 产品）、OPPO 开发者社区、`coloros.com` AI 板块 | `"OPPO AndesGPT"`、`"OPPO AI Center"`、`"ColorOS AI"`、`"安第斯大模型"` | `OPPO`、`OPPO Research Institute`、`OPPO AI Lab` | `oppo.com` AndesGPT、OPPO 开发者平台 |
| vivo | `developers.vivo.com/product/ai/bluelm`（蓝心大模型文档）、`vivo.com` | `"vivo BlueLM"`、`"蓝心大模型"`、`site:developers.vivo.com` | `vivo`、`vivo AI Lab`、`vivo AI 全球研究院` | `github.com/vivo-ai-lab/BlueLM`、`developers.vivo.com` BlueLM |
| Honor | `honor.com`（MagicOS AI、YOYO 智能体） | `"Honor MagicOS AI"`、`"Honor YOYO"`、`"荣耀端侧大模型"` | `Honor`、`荣耀`（论文极少，主要靠官方发布） | `honor.com` MagicOS、YOYO 智能体 |

> 设备厂商研究产出偏工程和官方发布，arXiv affiliation 命中率低于模型厂商。优先抓官方博客和产品发布，再补 affiliation 论文。

---

## 模型厂商（10 家，含 NVIDIA）

| 厂商 | 官方动态来源 | websearch 关键词 | arXiv affiliation | GitHub / 重要页面 |
|---|---|---|---|---|
| Google | `blog.google`、`ai.google.dev`、`developers.googleblog.com`（android-developers）、`developer.android.com/ai` | `"Gemini Nano"`、`"Google MediaPipe"`、`"Android AICore"`、`site:ai.google.dev on-device` | `Google`、`Google Research`、`Google DeepMind` | `ai.google.dev`、`developer.android.com/ai` |
| Microsoft | `techcommunity.microsoft.com`（Phi 博客）、`azure.microsoft.com/blog`、`microsoft.com/research` | `"Microsoft Phi-4"`、`"Phi-3-mini"`、`"Windows Copilot Runtime"`、`site:techcommunity.microsoft.com` | `Microsoft Research`、`Microsoft` | `techcommunity.microsoft.com`、`microsoft.com/research` |
| OpenAI | `openai.com/research`、`openai.com/blog` | `site:openai.com`、`"OpenAI" edge on-device`、`"OpenAI" function calling mobile` | `OpenAI` | `openai.com/research` |
| Anthropic | `anthropic.com/research`、`anthropic.com/news` | `site:anthropic.com`、`"Anthropic Haiku"`、`"Claude" edge deployment` | `Anthropic` | `anthropic.com/research` |
| Meta | `ai.meta.com`（博客 + 研究）、`about.fb.com` | `"Meta Llama" on-device`、`"Llama 3.2 1B 3B"`、`"Llama 4 Scout"`、`site:ai.meta.com` | `Meta AI`、`Meta FAIR`、`Fundamental AI Research` | `ai.meta.com/blog`、`github.com/meta-llama` |
| NVIDIA | `developer.nvidia.com/nim`、`blogs.nvidia.com`、`developer.nvidia.com/blog`（技术博客）、`build.nvidia.com` | `"NVIDIA NIM" on-device`、`"Project DIGITS"`、`"NVIDIA ACE"`、`site:blogs.nvidia.com` | `NVIDIA`、`NVIDIA Research` | `developer.nvidia.com/nim`、`build.nvidia.com`、`github.com/NVIDIA` |
| Mistral | `mistral.ai`（news / research）、`docs.mistral.ai` | `"Mistral Ministral"`、`"Ministral 3B 8B"`、`site:mistral.ai` | `Mistral AI` | `mistral.ai/news`、`github.com/mistralai` |
| 面壁智能 ModelBest | `modelbest.cn`、`modelbest.cn/en` | `"MiniCPM"`、`"面壁智能"`、`"MiniCPM-V"`、`site:modelbest.cn` | `ModelBest`、`面壁智能`、`OpenBMB` | `github.com/OpenBMB/MiniCPM`、`modelbest.cn` |
| 阶跃星辰 StepFun | `stepfun.com`（官网 JS 渲染，公告多在微信公众号，WebFetch 取不到深度页） | `"阶跃星辰"`、`"STEPX"`、`"Step 系列"`、`"印奇"`、`site:stepfun.com` | `StepFun`、`阶跃星辰` | `stepfun.com`、官方公众号（2026-07 发布全球首个 AI 智能体手机 STEPX Neo+智能体 OS） |
| Qwen（阿里云） | `qwenlm.github.io`、`alibabacloud.com` 博客 | `"Qwen2.5" on-device`、`"Qwen Mobile-Agent"`、`site:qwenlm.github.io` | `Alibaba`、`Alibaba Cloud`、`Qwen Team`、`阿里云` | `github.com/QwenLM`、`qwenlm.github.io` |

> 模型厂商 arXiv affiliation 命中率高，论文和官方技术报告都多。端侧关注小参数量变体（MiniCPM、Qwen 0.5B/1.5B/3B、Llama 1B/3B、Ministral 3B/8B、Phi-3-mini、Gemini Nano）。

## 模型实验室补充来源（5 家，强制检查）

| 厂商 | 官方来源 | 补查重点 |
|---|---|---|
| DeepSeek | `deepseek.com`、`api-docs.deepseek.com`、GitHub `deepseek-ai` | 新仓、重大 commit、推理内核、HF checkpoints；不能只查 arXiv |
| Moonshot/Kimi | `kimi.com`、`moonshot.cn` | 官方博客、模型发布、长上下文与本地部署动态 |
| Zhipu | `zhipuai.cn`、`bigmodel.cn` | GLM 小模型、Agent、端侧/工具调用更新 |
| MiniMax | `minimax.io` | 新模型、语音/多模态、小模型和推理部署 |
| Baichuan | `baichuan-ai.com` | 新模型、医疗以外的通用推理与端侧部署动态 |

这 5 家即使窗口内 0 命中也必须写入 `collection-manifest.json` 的 `vendors_checked`；0 是结果，不是跳过检查。

---

## 中国互联网公司研究项目（8 家）

> 这 8 家优先级仅低于大厂官方，`source_tier=公司项目`（排序低于官方动态和开源大项目）。多数没有独立官方研究门户，**主力靠 arXiv affiliation + GitHub org 搜法**。`vendors` 字段必填公司英文名，并在 `score_reason` 附 affiliation 证据来源。

| 公司 | 官方动态来源 | websearch 关键词 | arXiv affiliation | GitHub org / 重要项目 |
|---|---|---|---|---|
| 快手 Kuaishou | `kuaishou.com`（无独立研究门户，靠 arXiv + GitHub） | `"Kuaishou" arxiv`、`"快手" agent`、`"KwaiYii"` | `Kuaishou`、`Kuaishou Technology`、`Kwai`、`快手` | `github.com/kwai`（通用开源）、`github.com/Kwai-Kolors`（视觉生成 Kolors）、`github.com/KwaiKEG`（KwaiAgents、KwaiYii） |
| 字节 ByteDance | `seed.bytedance.com`（Seed 团队论文 + 研究）、`se-research.bytedance.com`（SE Lab） | `"ByteDance" arxiv`、`site:seed.bytedance.com`、`"字节跳动" agent` | `ByteDance`、`ByteDance Seed`、`字节跳动` | `github.com/bytedance`、`github.com/ByteDance-AI`；项目：Seed2.1、Trae Agent、MarsCode Agent |
| 腾讯 Tencent | `ailab.tencent.com`（AI Lab）、`ai.tencent.com` | `"Tencent AI Lab" arxiv`、`site:ailab.tencent.com`、`"腾讯" agent` | `Tencent`、`Tencent AI Lab`、`Tencent ARC Lab` | `github.com/tencent-ailab`、`github.com/TencentARC`、`github.com/Tencent`；项目：IP-Adapter、persona-hub、Hunyuan |
| 百度 Baidu | `ai.baidu.com`、`research.baidu.com`（Baidu Research） | `"Baidu" arxiv`、`site:ai.baidu.com`、`"百度" ERNIE agent` | `Baidu`、`Baidu Research`、`Institute of Deep Learning (IDL)` | `github.com/baidu`；项目：ERNIE、文心一言、PaddlePaddle |
| 美团 Meituan | 无独立研究门户，靠 arXiv affiliation + 邮箱域名 `@meituan.com` | `"Meituan" arxiv`、`"美团" agent 推荐` | `Meituan`（邮箱 `@meituan.com`） | `github.com/meituan`（工程为主，无突出研究 org）。研究多在推荐 / 检索 / 广告，端侧 agent 较少，按 affiliation 抓 |
| 京东 JD | 无独立研究门户，靠 arXiv affiliation | `"JD.com" arxiv`、`"京东" agent` | `JD.com`、`Jingdong`、`京东` | `github.com/jd-opensource`。研究多在推荐 / 供应链 / NLP |
| 拼多多 Pinduoduo | 无独立研究门户，靠 arXiv affiliation | `"Pinduoduo" arxiv`、`"PDD" arxiv`、`"拼多多" agent` | `Pinduoduo`、`PDD`、`拼多多` | 公开论文较少，搜索时放宽到 `PDD` / `Pinduoduo` 全文匹配 |
| 网易 Netease | 无独立研究门户，靠 arXiv affiliation | `"NetEase" arxiv`、`"网易" agent` | `NetEase`、`NetEase Games`、`网易` | `github.com/netease`、`github.com/netease-community`。研究多在游戏 AI / NLP / 音乐推荐 |

> 中国互联网公司公开论文未必聚焦端侧，但 affiliation 命中即算公司项目，优先级高于学校项目。抓到的论文若涉及 agent / 多模态 / 轻量化，即使不是手机端，也按公司项目收录并标 `vendors`。

---

## 发布日期核不到时怎么办

厂商官方页常见三种"日期不可见"，处理口径不同：

| 情况 | 典型站点 | 处理 |
|---|---|---|
| 模板关掉了日期显示，但文章自己的 CMS 载荷带发布日 | Qualcomm OnQ / developer blog（`showDate: ""`） | 取 `<article-url>.model.json` 的 `pagePublishDate`（epoch 毫秒），与 URL 路径 `/YYYY/MM/` 交叉印证后可用。这是一手正文数据 |
| 整站 JS 渲染，只拿得到标题；或 curl 返回的 canonical 指向另一篇 | qualcomm.com 部分页面、openai.com（403）、apple.com / samsung.com newsroom | **丢弃**。URL 能开 ≠ 内容对题，更 ≠ 日期可核 |
| sitemap `lastmod` 是本周，正文日期却是几个月前 | Anthropic、Mistral、MediaTek tek-talk、Honor 各地区镜像 | **丢弃**。`lastmod` 是发现层信号，常青页模板一动就刷新 |

### 历史窗口（回填）优先试这些入口

按实测有效性排序，`lastmod` 应当是最后手段：

| 入口 | 形式 | 实测 |
|---|---|---|
| **WordPress REST API** | `<blog>/wp-json/wp/v2/posts?after=…&before=…&per_page=100` | **最强**，按发布日精确过滤且带正文。`developer.nvidia.com/blog`、`blogs.nvidia.com`、`about.fb.com` 均可用。凡 WordPress 站先试这个 |
| **厂商自家全量 RSS** | `openai.com/news/rss.xml`（1247 条回溯到 2015）、`mistral.ai/rss.xml`（88 条回溯到 2023） | 对历史窗口是降维打击。注意区分「全量归档 feed」和「只给最近 N 条的 feed」 |
| **Blogger feed 带日期参数** | `…/feeds/posts/default?alt=rss&published-min=…&published-max=…` | `android-developers.googleblog.com` 可用 |
| **站点内嵌 JSON** | `machinelearning.apple.com/research?page=1..8` 内嵌 `"published"` | Apple 历史回填唯一可用入口（其 `rss.xml` 只有 10 条） |
| **全量 sitemap + 逐条核正文** | `blog.google/en-us/sitemap.xml`（11701 条）、`qualcomm.com/sitemap.xml` 按 URL 路径 grep `/YYYY/MM/` | lastmod 只做发现（可放宽±10 天），日期必须回正文或 `.model.json` 定 |

**本周（06-12~06-18 回填）新增实测**：

- `machinelearning.apple.com/research?page=N` 的 **`page` 参数是空操作** —— 1~8 页返回同一个 2.5MB 文档，内含全部 567 条 `published`（2017-07 ~ 2026-10）。取第 1 页即是全量，不必翻页
- `developer.apple.com/news/rss/news.rss` 是**可用的历史归档 feed**（147 条回溯到 2024-10），Apple 侧第二个入口
- **Microsoft 没有任何可用的历史归档入口**：techcommunity 两个 RSS 路径 404/空、`azure.microsoft.com/blog/feed` 10 条、`microsoft.com/research/feed` 10 条、`research.samsung.com/rss/blog` 404。回填窗口只能记 `no_match`，但这是「查不到」而非「确认没有」，性质与其他 `no_match` 不同
- `aihub.qualcomm.com/sitemap.xml` 有 18187 条 URL 但**完全没有 `<lastmod>`**，做不了时间发现
- `developers.vivo.com/sitemap.xml` 返回的是 Vue SPA 外壳 HTML 而非 XML，极易误判成「有 sitemap」
- `news.samsung.com/global/feed` 50 条但只回溯到 2026-08，属「只给最近 N 条」型

**06-05~06-11 回填新增实测**：

- **`anthropic.com/news` 内嵌 Sanity JSON 是 Anthropic 的全量归档索引**（269 组 `publishedOn`+`slug`，回溯到 2021-05）。`anthropic.com/rss.xml` 与 `/feed.xml` 均 404，此前只能靠 sitemap lastmod 记 `no_match`
- **`apple.com/newsroom/sitemap.xml`（2588 条）+ 逐条 JSON-LD `datePublished`**：sitemap 无 lastmod，但 URL 路径带 `/YYYY/MM/`，按月 grep 后逐条开正文定日。回填发布会周（WWDC 等）的关键入口
- **`mediatek.com/sitemap.xml`（4191 条带 lastmod）+ 文章页 JSON-LD** 可定日，**但 lastmod 实际是 `dateModified`**（实测一文 lastmod 06-10 / published 05-07），必须逐条回正文
- **Reddit 终于有历史入口**：`arctic-shift.photon-reddit.com/api/posts/search?subreddit=X&after=…&before=…` 匿名 200，返回带 `created_utc`/`score`/`selftext`/`permalink` 的 JSON。限制：每 sub 单次 100 条上限、翻页未跑通，是抽样不是穷举，条目 `verification` 应记「仅线索」
- **X 原帖回核**：UA 必须是 `curl/8.4.0` 才返回带 `article:published_time` 的 SSR 页（浏览器 UA 只得 JS 壳），且成功是概率性的、需 `sleep 4` 重试。可先用 snowflake 离线定时筛选——`(id>>22)+1288834974657` 毫秒即发布时间，与 meta 精确吻合，先筛进窗口再只对少数条做高成本回核
- **`news.samsung.com` 是 WordPress 但 `/wp-json/wp/v2/posts` 被 WAF 挡成 403** —— WP REST 这招对三星无效，别重试
- **`blog.mi.com` 是 catch-all 200 陷阱**：`/en/`、`/sitemap.xml`、`/feed/`、`/wp-json/wp/v2/posts` 全部返回同一个 42KB SPA 外壳，极易误记成 `found`
- **blog.google 的 lastmod 漂移远超 ±10 天**：实测有 lastmod 2026-06-10 / `datePublished` 2026-03-25（差 77 天）。发现窗放宽到 ±30 天仍可用，但 lastmod 绝不能当日期
- `honor.com/global/sitemap.xml` 可用（1794 条带 lastmod）但只反映近期重生成；`honor.com/sitemap.xml` 是 404。`oppo.com/sitemap.xml` 是按地区分的 sitemapindex，index 层 lastmod 全部同一天，拿不到逐条发布日

**05-29~06-04 回填新增实测**：

- **Samsung 终于有历史入口**：`news.samsung.com/global/<YYYY>/<MM>/`（含 `page/2/`）是**服务端渲染的月度归档**，
  再逐条开文章页取 JSON-LD `datePublished`。此前只有 `/global/feed`（50 条、回溯两个月）和被 WAF 挡成 403 的
  WP REST，连续数周只能记 no_match。注意 `news.samsung.com/global/wp-sitemap.xml` 存在（posts 分 4 片），
  但 `sitemap_index.xml` 是 404
- **Honor 有正文日期了**：`honor.com/global/news/` 列表页服务端渲染且带每条英文日期，文章页有 JSON-LD
  `datePublished`。此前只能用 sitemap lastmod，整批丢弃
- **ModelBest 首页内嵌 JSON 是全量索引**（title/intro/link/ISO 时间戳），能精确定位窗口内条目——但 link 全指向
  `mp.weixin.qq.com`，对本项目仍记 no_match。价值在于把「查不到」降级成「**确认有但域名不合规**」

**新增陷阱**：

- **Qualcomm `.model.json` 里有三个日期字段，只有一个是对的**：`publishDateTime`（如 "Jun 01, 2026 | 23:50"）
  和一堆整数 `publishDate` 都是**页内「相关文章」卡片的日期**，不是本文发布日（实测 dragonwing-iq10 的
  `pagePublishDate` 是 06-01、`publishDateTime` 却是 05-28）。只能用带引号的字符串字段
  `"pagePublishDate":"<ms>"`，且必须与 URL 路径年月交叉印证
- **blog.google 文章页的 JSON-LD 写作 `"datePublished": "`（冒号后有空格）**，无空格正则会全部匹配失败；
  用 `<meta property="article:published_time">` 更稳。另外 `blog.google/en-us/sitemap.xml` 里混有 `/authors/` 页，
  不过滤会污染候选池
- **`www.huawei.com/en/sitemap.xml` 和 `/en/news/<Y>/<M>` 是软 404**：返回 404 但带 199KB 正文，按响应体大小
  判断会误判成有数据
- **YouTube 频道 RSS 已整体 404**（多个有效频道 ID 验证，`?user=` 同样失效），从「只给 15 条」退化为完全不可用
- **GitHub Discussions 的 `ollama/ollama`、`google-ai-edge/LiteRT-LM`、`huggingface/transformers.js` 返回
  9 字节空响应**——这是入口级拒绝，不是「窗口内无帖」，应记为不可达而非 no_match
- `mediatek.com` 的 lastmod = dateModified 再次复现且偏差更大：Computex 2026 稿 lastmod `2026-07-15` /
  JSON-LD `2026-05-28`，差 48 天；大批 2022-2024 老稿集体刷成同一天

**05-22~05-28 回填新增实测**：

- **Microsoft 其实有历史归档入口**（推翻上一周「三路皆无、只能记查不到」的结论）：
  `microsoft.com/en-us/research/wp-json/wp/v2/posts?after=…&before=…&per_page=100` 可用——
  microsoft.com/research 是 WordPress。techcommunity 的搜索 API 仍 403
- **DeepSeek**：`deepseek.com/sitemap.xml` 是可枚举的全量 news 归档，每条 news 的 lastmod 就是发布日。
  DeepSeek 从「查不到」升级为可判「确认无」
- **Zhipu**：`zhipuai.cn/news` 服务端渲染带日期、25 条可枚举，同样可做「确认无」判定
- **Honor**：用 `/global/news/archive/`（全量 245 条）而不是 `/global/news/` 列表页，覆盖好得多
- **`mistral.ai/rss.xml` 现在 302 跳到 `/news/rss`**——直接取旧路径只得 24 字节 "Redirecting to"，必须 `curl -L`
- **`blog.google/en-us/sitemap.xml` 的小分区（`/security/`、`/waze/`、`/chromium/` 等约 300 条）不能漏**：
  实测唯一的 Chrome Enterprise AI agent 条目就在 `/security/` 下、路径只有 4 层，
  按「深度≥5 + 只看三大分区」过滤会整条漏掉

**两个会制造「假的 0 命中」的操作陷阱**：

- **blog.google 与 mediatek.com 会突发静默空响应**（curl 返回 000 或空体），并发 6~12 时成片失败，
  极易被误读成「该条无日期」。必须**串行 + 最多 3 次重试 + 对空值复跑**；实测复跑后 blog.google
  436 条里 390 条拿到 `published_time`（其余是本就无该 meta 的分区索引页），MediaTek 285 条全部拿到
- **Windows CRLF 陷阱**：Python `open(...,'w')` / `write_text` 默认会把 `
` 写成 `
`，
  URL 清单被 bash `read` 读进来时带着 `
`，curl 全部返回 000 —— 产生一次完全虚假的「0 命中」。
  管道里必须 `tr -d '
'`；写文件时用 `newline='
'` 显式指定，否则改一行 Markdown 也会变成全文件 diff

**05-15~05-21（Google I/O 周）回填新增实测**：

- **入口会腐坏，上周有效不等于本周有效**：**Zhipu 退化了**——`zhipuai.cn/news` 现在是 catch-all SPA 外壳
  （`/news`、`/news/`、`/devday` 返回同一个约 899KB 文档，内嵌 JSON 只剩模型卡 `updatedAt`），
  上一周记录的「服务端渲染 25 条可枚举」已不复现，本周只能退回「查不到」。
  **每周都要实测，别直接采信往期结论**
- **`developers.googleblog.com`**（注意它和 `blog.google`、`android-developers.googleblog.com` 是三个站，I/O 周三个都要查）：
  sitemap 的 lastmod 漂移大且方向不定（实测 lastmod 06-02 / 正文 04-14、lastmod 05-05 / 正文 04-30），
  但 **lastmod ≥ 发布日**，所以取 `lastmod >= 窗口月` 的条目回正文即可穷举
- **blog.google 的发现窗已验证够用**：除 lastmod 落在「发布月 +4 个月」内的条目外，额外兜底扫描
  前一个月与后四个月共 366 条，窗口内新增 0 条。串行 + 3 次重试下 447 条里 402 条拿到
  `published_time`，45 条无值全是分区索引页——没有假 0
- **`blog.google/sitemap.xml` 是 sitemapindex**，非 en-us 的分片全是 `/intl/<locale>/` 地区镜像；
  取 en-us 分片即英文全量（约 11700 条，含 `/security/` 等浅路径分区，**不要按路径深度过滤**）
- **Qualcomm 还有一段无日期路径**：`qualcomm.com/snapdragon/news/`（222 条，URL **不带** `/YYYY/MM/`），
  按「路径 grep /YYYY/MM/」会整段漏掉。这 222 条全部有 `.model.json` 的 `pagePublishDate`，
  应纳入常规扫描——但它们做不了 URL 年月交叉印证，收录前需另想印证手段
- **`techcommunity.microsoft.com` 的 RSS 现在返回 200/452KB**（此前 404/空），但只有最近 20 条，
  对历史窗口仍然无用——**别被 200 骗**
- **OPPO 的 sitemap lastmod 是模板重生成**（2020 年 Find X2 Pro 稿标成 2026-05-13），与 MediaTek 同类陷阱。
  `mi.com/global/discover/` 复现 catch-all 外壳（拼不存在的子路径同样返回 42KB）。
  `vivo.com/sitemap.xml`、`baichuan-ai.com/sitemap.xml`、`alibabacloud.com/blog/sitemap.xml` 均 404

**社区雷达侧的实测（同属历史窗口检索，记在一起便于查阅）**：

- **X 回核的 URL 形式必须完整**：`x.com/<handle>/status/<id>`。拼成 `x.com/<handle>/<id>` 只会拿到
  无 meta 的 JS 壳。形式写对后实测 24 次尝试 22 次拿到 `article:published_time`，
  这很可能才是之前记录的「概率性需重试」的真实成因。
  **判据用 `grep -a published_time` 命中与否，不要用响应体字节数**——壳的大小会随 X 前端版本漂移，
  字节数只能当快速初筛。`grep` 的 `-a` 不能省：响应体含二进制字节时 grep 会当成 binary file
  静默不输出，这本身就会制造一次假的「无 meta」
- **X 的纯图片/视频贴拿不到正文**：只有 `og:description` 那点文字可用，配图与视频内容不可复述。
  这个限制与回核成功率无关，高成功率也不改变它
- **Reddit 的限流响应是固定 54 字节**（`{"data":null,"error":"Timeout. Maybe slow down a bit"}`），
  可按字节数直接判限流并重试；**11 字节则是 sub 不存在**，两者含义完全不同
- **GitHub Discussions 的时间要按 `<relative-time>` 切块解析**：取每块里最后一个 discussions 链接，
  直接 `findall` 会让时间和标题错位
- **YouTube 频道 RSS 的覆盖窗约 6 周**（实测 5 个频道最早 published 落在约 6 周前），不是「最近两周」。
  对更早的窗口是结构性够不到，应记 `limited`

**无效 / 陷阱**（都实测过，别重复踩）：

- 「只给最近 N 条」的 feed 对历史窗口一律无用：`machinelearning.apple.com/rss.xml`(10)、`blog.google/rss/`(20)、`blogs.nvidia.com/feed/`(18)、`developer.nvidia.com/blog/feed/`(100，只回溯到 7 月)
- `developer.nvidia.com/blog/feed/?paged=12` 返回 200 且 782KB，但**整个文档没有一个 `<pubDate>`** —— 分页失效后的降级响应，极易误判成有数据
- `developers.googleblog.com/feeds/posts/default` 完全没有日期字段，`published-min` 被忽略（该站已非 Blogger）
- `ai.meta.com/*` 和 `meta.com/*` 对 curl 一律 **400**，浏览器 UA 也救不了 —— Meta 只能走 `about.fb.com`
- `blogs.nvidia.com/2026/06/` **404**，而 `developer.nvidia.com/blog/2026/06/` 可用 —— 同一公司两个博客归档形态不同，必须逐站实测
- `qwenlm.github.io/blog/index.xml` 最新只到 2025-09（博客已迁站）
- ModelBest 官网只做索引，文章正文托管在微信公众号（`mp.weixin.qq.com`），不命中官方域名白名单

---

sitemap 只用于**发现**，不用于**定日期**。一次回填里 176 条厂商 sitemap 命中最后只有 6 条经得起正文日期核验，这个比例是正常的，不是漏采。

---

## 与其他文档的关系

- `vendor-whitelist.md`：官方域名白名单和 affiliation 关键标识，是评分和收录的硬约束来源。本文件只补充检索方法，不重复定义白名单，不改它。
- `docs/agent-guide/research-prompt.md`：调研子 agent 的搜索提示词，发起子 agent 时注入全文。本文件被它引用，作为厂商检索方法展开。
- `docs/agent-guide/validation-rules.md`：收录和打分规则。本文件的优先级区间和 `vendors` 字段要求与它一致。
