# 当前数据进度

正式有效数量以 [范围审核报告](data/automation/textile_scope_report.json) 为准，目标为3000个原文核验、去重的样品。网页与首页由正式主表生成；候选、暂缓及范围待审样品不计入目标。

[B384 / PR #170](https://github.com/PolyFT/textile-tga-database/pull/170) 已合并并完成远端核验：真正新增8个样品／8条TG记录，来自3篇本地原文；0个旧样品范围升级、0个旧证据升级、0个旧数值修改。正式有效总数为780个样品／965条TG。成品纺织品558个／711条TG，纤维65个／65条TG，可制纤聚合物及复合材料157个／189条TG。旧报告的成品小计已排除纤维，此分类纠正不增加科学样品。

原文定义有歧义的最大温度及温度未明确的残余质量保留为原始注记，不填入Tmax或固定温度残炭。测试条件不重复计独立样品，形态、洗涤或老化状态不混配。

当前证据：[B384审核](data/curation/archive/20261006/source_review_manifest_b384.json)、[来源队列](data/curation/source_review_queue.csv)、[租约](data/curation/source_verification_progress.json)。历史报告见[历史进度](docs/archive/source-verification-through-b361.md)及[批次归档](data/curation/archive/)。

下载index.html后可离线浏览；在线Pages尚待仓库设置启用。继续只读本地文献库、原生文本读取、分篇并行和单写入发布；不公开全文、私密材料或本地路径。

全部2311项测试、精确提交检查及两个保留工作流的合并后检查通过。远端18个公共变更文件逐字核对，所有其他历史科学和归档文件保持原提交内容；原件哈希未变，已释放本批自己的写入租约。
