# 当前数据进度

正式有效数量以[范围审核报告](data/automation/textile_scope_report.json)为准，目标3000个原文核验、去重的样品。候选、暂缓和范围待审记录不计入目标。

[B406 / PR #172](https://github.com/PolyFT/textile-tga-database/pull/172) 已合并并完成远端核验：真正新增10个样品／13条TG记录，来自4篇本地原文；0个旧样品范围升级、0个旧证据升级、0个旧数值修改。正式有效总数为817个样品／1008条TG／151篇来源。成品纺织品576个／732条TG，纤维74个／74条TG，可制纤聚合物及复合材料167个／202条TG。

本批PA6、SLS加工PA12、半芳香聚酰胺和PA11保持配方、形态和初始处理状态对应。PA6两个气氛保留6条TG记录，只计3个样品；PA12 LOI来自补充材料图中直接印出的原生文字数值，不由柱高或曲线估读。判据未明确的最大温度和PA11初始温度保留原值与around约值注记，不补填Tmax、T5、T10或Tonset；残余质量没有对应温度时不采用程序终温。

HTN只采用实验TG，不混用计算曲线或锥形量热残留。PA11 S3与S7仅采用明确的氮气700℃残余质量；空气条件、温度不明的S5、旧对照来源未解决的S1继续暂缓。PLA资料完整可读，但TG／LOI成型状态未闭合，不新增配对。误差统计定义及测试重复次数未报告时保持未知。

当前证据：[B406审核](data/curation/archive/20261006/source_review_manifest_b406.json)、[来源队列](data/curation/source_review_queue.csv)、[租约](data/curation/source_verification_progress.json)。历史报告见[历史进度](docs/archive/source-verification-through-b361.md)及[批次归档](data/curation/archive/)。

下载index.html可离线浏览。继续只读本地文献库、原生文本读取、分篇并行与单写入发布；不公开全文、私密材料或本地路径。

全部2348项测试、精确提交检查及两个保留工作流的合并后检查通过。远端18个公共变更文件逐字核对，其余831个已有文件保持原提交内容；原件哈希未变，已释放本批自己的写入租约。
