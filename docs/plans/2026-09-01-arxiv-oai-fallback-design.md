# arXiv OAI-PMH 备用覆盖设计

## 背景与选择

历史补采期间，arXiv Query API 在退避重试后仍持续返回 429/空响应，而官方 OAI-PMH `ListRecords` 可稳定返回同一时间范围的完整元数据。候选方案包括伪造 Query API 最低页数、等待限流解除、或让验证器识别官方 OAI 传输。前两种分别破坏审计真实性或让周报发布依赖不可控等待，因此选择第三种。

## 契约

Query API 路径保持原契约：十个 required sweep 全部完成，`pages_fetched` 至少覆盖每个 sweep 的首个响应页。OAI 路径必须显式写 `collection_transport=official-oai-pmh`，完整列出九个规范学科，记录真实响应页数，并在 resumption token 自然结束后写 `pagination_complete=true`。两条路径都必须生成候选文件哈希、逐记录指纹和稳定身份血缘。

OAI 的 datestamp/metadata 日期可能代表更新事件，不作为最终发布日期权威。候选进入 run 后仍由既有 arXiv API 校验 submitted/updated；首投越窗或更新稿缺少实质版本证据时删除。测试覆盖 Query API 旧契约不变、完整 OAI 证明可通过、OAI 缺学科被拒绝。这样既保留严格覆盖门槛，也避免把传输实现细节错误地当成覆盖本身。
