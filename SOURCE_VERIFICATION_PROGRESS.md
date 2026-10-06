# 当前数据进度

正式有效数量以 [范围审核报告](data/automation/textile_scope_report.json) 为准，目标为 3000 个经原文核验、去重的样品。首页与网页阅读表由同一正式主表生成，不将候选数量计入目标。

最新数据批次 [B361 / PR #166](https://github.com/PolyFT/textile-tga-database/pull/166) 真正新增 8 个样品／8 条 TG 记录；另有 59 个旧样品／64 条 TG 记录完成适用范围审核。这批没有旧数值修改或证据升级。发布后有效总数为 676 个样品／841 条 TG 记录；879 个历史样品仍待范围审核。

本次仓库整理只生成阅读表、合并说明和归档历史材料，新增有效样品为 0。科学审核、去重及测试标准保持不变。

后续按文献批次更新当前状态；详细证据放在审核记录中。发布前检查最新 main、写入租约及未合并 PR。并行任务只准备库外私有结果，统一发布由租约持有者完成，测试及 GitHub 审批通过后合并。

历史批次的完整报告与发布记录：[历史进度](docs/archive/source-verification-through-b361.md)、[历史机器记录](docs/archive/source-verification-through-b361.json)。当前 [处理队列](data/curation/source_review_queue.csv) 和 [写入租约](data/curation/source_verification_progress.json) 保持在原位置。

整理 [PR #167](https://github.com/PolyFT/textile-tga-database/pull/167) 已通过精确提交检查、全部 2283 项测试及两个保留工作流的合并后检查。233 份历史材料按原字节归档；远端完整网页表格、两份科学主表及报告已读回核对。新增样品、证据升级与科学数值改动均为 0。已释放本次写入租约。

阅读网页可下载 `index.html` 后用浏览器直接打开。在线 Pages 发布因当前令牌缺少相应写入权限暂未启用；不影响离线表格或科学核验。
