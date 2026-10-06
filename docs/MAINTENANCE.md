# 维护与追溯

首页只提供阅读入口。`index.html` 是 `data/tg_loi_textile_master.csv` 的确定性导出，默认展示常用字段，展开一行可查看完整阅读字段；它不替代完整事实、来源和证据字段。气氛、升温速率和残余质量温度随每条记录保留。原文缺失或有争议的字段不补填，阅读表中的备注保留限制与不确定性。

| 内容 | 位置 |
|---|---|
| 完整且通过城市材料范围审核的主表 | [`data/tg_loi_textile_master.csv`](../data/tg_loi_textile_master.csv) |
| 历史宽范围核验主表（包含范围待审样品） | [`data/tg_loi_master.csv`](../data/tg_loi_master.csv) |
| 原始批次事实输入，重建仍全部读取 | [`data/incoming/`](../data/incoming/) |
| 当前队列、问题、来源／范围证据与写入租约 | [`data/curation/`](../data/curation/) |
| 历史批次审核、字段暂缓和对应表 | [`data/curation/archive/`](../data/curation/archive/) |
| 当前科学校验及范围报告 | [`data/automation/`](../data/automation/) |
| 旧说明、完整历史进度和停止执行的联网工作流 | [`docs/archive/`](archive/) |
| 归档前后路径及逐文件 SHA-256 | [`归档清单`](../data/curation/archive/index.json) |

归档文件内容逐字保留。历史文档反映当时目标和路径；历史 500／2000 个目标与旧联网流程不再作为当前工作要求。当前目标始终按城市材料范围报告计算为 3000 个样品。历史宽范围校验报告的旧目标字段保留以兼容既有审核工具，不用于计算项目完成度。

## 本地采集与发布

使用只读文献索引定位 PDF／HTML 和补充材料，原生文本读取。缓存、脚本、未完成队列和断点在文献库外保存；不同 DOI 可并行抽取。每篇完整审核符合条件的样品，保留同一配方、形态、制备、洗涤和老化状态的对应证据。来源公开定位使用 DOI、页码、表号或图号，库内路径与全文保持私有。

不同测试条件保留为测试记录；真正新增样品、旧证据升级和旧样品范围复核分开计数。原文冲突、仅曲线估读、状态或条件对应不清的材料按证据规则暂缓，不进入阅读表。

发布前读取最新 main、`writer_lease` 和未合并 PR，不抢占有效租约。一个租约持有者负责合并、全字段去重／验证及 PR；其他任务只准备私有批次。确认证据和原件哈希、完整科学测试、精确提交的 GitHub 检查及远端结果后，保存断点并释放自己的租约。不要上传文献全文、私人批注或本地路径。

旧的定时 OpenAlex／网页检索和每 10 分钟联网抽取任务已归档。保留 PR／main 科学验证与 main 离线重建两个工作流，继续使用同一写入并发组；不改变 GitHub 的审批规则。

## 重建与验证

```sh
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
python scripts/validate_tg_loi.py
python scripts/textile_scope.py
```

最后一步从正式范围主表导出网页，同时刷新首页的有效样品及测试记录数。网页的 TG 特征温度与残余质量来自明确命名的正式字段；未定义温度的原文残余质量不会被补成固定温度指标。完整主表保留所有特殊指标和原文定义，阅读表是常用字段视图。

字段定义：[数据字段](../schema/scatter_ready.md)、[样品对应审核](../schema/pairing_review.md)、[无 DOI 来源身份](../schema/source_identity.md)。全部历史批次测试仍参与自动发现；归档只更新必要文件路径，不删除测试。

<!-- TG-LOI-SNAPSHOT:START -->
## Current TG–LOI evidence snapshot

- Legacy field-complete condition records: **2303** (not a scientific Grade-A count)
- Numeric TG–LOI candidate rows: **2622**, across **504 DOI**
- Field-complete, unflagged condition records awaiting evidence review: **382**
- Quarantined condition records: **34**; originals and reasons retained
- Malformed input CSV records quarantined separately: **1**
- Evidence-reviewed exact Grade-A conditions / sample states: **1978 / 1555**
- DOI cohort: **435 sources / 1970 conditions / 1547 states**
- Reviewed non-DOI cohort: **2 sources / 8 conditions / 8 states**
- Overall reviewed sources: **437**; source identity schema **1**
- Recorded publication types (disjoint Grade-A source identities): journal_article: **292**; conference_proceedings: **5**; author_preprint: **8**; unspecified: **132**; unrecognized: **0**; conflicting_metadata: **0**
- Sources explicitly marked `author_preprint` (without conflicting type metadata): **8 sources / 33 conditions / 23 states**
Publication types use explicit `publication_type` metadata on Grade-A candidate rows before deduplication; pending and quarantined rows cannot classify verified sources. Non-DOI `original_conference_proceedings` also identifies conference proceedings. Missing-only labels are `unspecified`; unknown labels are `unrecognized`; disagreeing nonempty labels are `conflicting_metadata`, excluded from the author-preprint subtotal. Blank labels do not contradict an explicit source-level type. DOI presence and Grade-A numerical review do not establish journal publication or peer review.
Unspecified or unrecognized publication types do not invalidate accepted numerical evidence. Zero explicitly marked author-preprint sources does not establish that no legacy source is a preprint.
New author-preprint rows should explicitly record `publication_type=author_preprint` and `source_version`. These reporting fields do not change source identities, fingerprints or the evidence gate.
A missing new review field means pending documentation, not that a legacy measurement is wrong.
Counts are generated together with `data/automation/validation_report.json`; do not edit by hand.
Snapshot SHA-256: `aee412b10f6b0e12c729227457b707173ddd4022836b0c01edaa0cdf95e40fb0`
<!-- TG-LOI-SNAPSHOT:END -->
