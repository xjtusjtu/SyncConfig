# 来源、审读范围与设计取舍

审读日期：2026-10-09（第 1～5 节）、2026-11-08（第 6 节）。下列判断基于实际获取的仓库正文，不是星数、README 宣传或效果证明。分支会变化，复核请使用所列 commit。

本 skill 的中文规范、例子和检查器独立撰写，没有复制第三方脚本或大段正文。借鉴的是工作思路，并保留下列来源供核对；不将候选 skill 自报的语料规模或测试成绩当作已独立验证的效果。

## 1. 学科写作候选

### hanlulong/econ-writing-skill

- 版本：`f2bf7a22c5e3b37921a5e6c73bd1fb380a5e00e8`。
- 实读：[入口](https://github.com/hanlulong/econ-writing-skill/blob/f2bf7a22c5e3b37921a5e6c73bd1fb380a5e00e8/skills/econ-write/SKILL.md)、同目录 `review-checklist.md`；抽读 `examples/before-after.md` 开头的摘要、引言和文献改写示例。
- 可借鉴：按章节任务组织写作；尽早交代问题与回答；解释结果的实质意义。
- 不采用：摘要一律 150 词上限、文献综述一律不单列、讨论每一个表内数字、固定贡献数量，以及把写作评分映射为顶刊准备度。
- 示例风险：改写示例加入原段落没有提供的设计与数字。即便视为教学演示，也不能成为真实稿件“润色”的默认行为。
- 许可证文件：MIT，Copyright (c) 2026 Lu Han。

### Silas1929/econ-writing

- 版本：`ba636f282fc80b12dbed623752b76c1513cd73ea`。
- 实读：[入口](https://github.com/Silas1929/econ-writing/blob/ba636f282fc80b12dbed623752b76c1513cd73ea/SKILL.md)、`references/paragraph-composition.md`、`references/tone-register.md`。
- 可借鉴：区分创作、润色与只诊断；保留技术术语；重视引用归属、删装饰性冗余而不删信息。
- 需调整：它明确只管经济学行文，不负责研究内容或设计；段落长度与禁止路标的规则不应泛化。引用可以随受支持的论断一起合法重排，而非绝不能移动字符。
- 许可证文件：MIT，Copyright (c) 2026 Slias。

### linkingoscar/econ-management-paper-polish

- 版本：`da924b433eb7ebf7c57d014dcd476735dcb8e0a5`。
- 实读：[入口](https://github.com/linkingoscar/econ-management-paper-polish/blob/da924b433eb7ebf7c57d014dcd476735dcb8e0a5/SKILL.md)；`references/v3/02-writing-style.md`、`06-argument-structure.md`、`05-methods-identification.md`、`writing-examples.md`；中英文经济学／管理学四份 style 文件、`subfields-management.md`；`scripts/verify_bounded_patch.py`、`check_numeric_consistency.py`。
- 可借鉴：按研究范式选择规范；构念—机制—边界与问题—识别—量级两种路线；轻量修改不要求大型审计工作区；脚本明确自己的检查上限。
- 需调整：对当前四类任务只保留必要工作流，不引入其完整文献／语料／集成系统。脚本与全部依赖没有在本次完成端到端验证；阅读实现不等于实际验证整个框架。
- 许可证文件：MIT，Copyright (c) 2026 econ-management-paper-polish contributors。

## 2. 对照候选

### felixschrimpff/academic-writing-skill

- 版本：`86ea3ee3f8b936490c5edbbe4506117a508ca407`。
- 实读：[入口](https://github.com/felixschrimpff/academic-writing-skill/blob/86ea3ee3f8b936490c5edbbe4506117a508ca407/SKILL.md)、`references/revision-checklist.md`、`references/corpus-and-method.md`。
- 可借鉴：先修结构与论断强度，再修句子；主动检查删改过度。
- 不采用：语料六类领域不包含管理学／经济学，不能据此给经管论文设词频或语态配额；入口也明确破折号禁令是某用户偏好，不是语料结论。
- 没有独立复现其语料采集、标注和效果测试。
- 许可证文件：MIT，Copyright (c) 2026 Felix Schrimpff。

### Chen-ShiRui/claude-academic-skills

- 版本：`7ed6377f0efb6a38951b48ef03b19d996e454b1f`。
- 实读：[research-writing-skill 入口](https://github.com/Chen-ShiRui/claude-academic-skills/blob/7ed6377f0efb6a38951b48ef03b19d996e454b1f/research-writing-skill/SKILL.md) 及 `references/paper-writing/section_rhetorical_moves/introduction.md`。
- 可借鉴：区别原材料、作者确认内容、推断与建议；中国用户可用的输入与输出习惯。
- 不采用：配套引言规范偏系统／网络论文，其命名新抽象、加粗贡献清单和评估指标模板不适合直接覆盖经管稿件。
- 许可证文件：MIT，Copyright (c) 2026 [zLanqing]。

## 3. 官方材料核对

- [Management Science 投稿指南](https://pubsonline.informs.org/page/mnsc/submission-guidelines)：2026-10-09 页面所示摘要为至多 250 词，说明候选中的 150 词不能当通用期刊硬规则；该刊范围也包括规范性与描述性的决策研究。
- [AMJ 官方投稿说明](https://www.aom.org/publications/journals/publishing-with-aom/author-and-reviewer-resources/author-resources/submitting-to-journal/)：强调对既有管理与组织文献的理论增量，也承认多种贡献路径，不能只用一套计量模板判断。

以上是本次核对时的页面信息，不是永久不变的约束；实际期刊适配时需重新核对。只有此处列明的材料被审读，未阅读的配套文件和其引用来源不视为已验证。

## 4. 本地实现与验证边界

本 skill 将四个使用场景分开，并补充“扩写增加何类内容、需要什么依据”的决策规范。词面检查脚本只作为辅助；不以通过测试证明写作效果。

检查器与结构回归测试放在项目 `tmp/scripts/test_writing_skill.py`，测试输出放在 `tmp/output/writing_skill_audit/`。没有独立代理前向测试、盲评或真实论文效果评估，不声称优于候选或保证发表。

## 5. 写作约定文件与读者视角表达（2026-11-02 新增）

本次新增两份规范：[写作约定文件](manuscript-conventions.md) 与 [读者视角表达](reader-facing-expression.md)，并在 SKILL.md 及各章节、局部、全局、证据规范中接入。依据与取舍如下。

- **项目写作约定文件**：要求论文项目根部存在 `WRITING_CONVENTIONS.md`，集中存放确定性写法（术语、变量与测量、方法与步骤、样本口径、表图引用、符号）。论文遵循约定，不遵循代码工程实现；变量名、列名、函数名、模块名、脚本名不得进正文。约定文件缺失时只报告、不自动创建（用户确认，2026-11-02）；本 skill 仅提供空白模板 `templates/WRITING_CONVENTIONS.md`。
- **读者视角表达**：默认读者是不了解本研究技术背景的审稿人；步骤按「为什么做—给什么输入—怎样处理—得到什么输出」展开；新术语首次出现先以普通语言释义；不堆叠连续抽象名词；不以大量括号和防御性限定推进正文；专业术语保留但须说明其在本研究中的具体作用。
- **不采纳**：不新增固定句长、每段句数或「禁用括号」的机械配额；不要求每个句子都写成四段式（四段式仅针对方法／流程类步骤叙述）；不改变现有「局限集中放在最后部分」的规则（用户确认以现有规则为准，仅强化正文少用括号与防御性限定）。
- **命名不区分内部／外部名称**：统一裁决标准是读者能否快速理解其指代及在研究中承担的作用，而非名称来源。
- **验证边界**：两份新规范为写作判断，不由 `scripts/check_protected_fields.py` 验证；该脚本仍只做词面清单差异。

## 6. 学术志 skills 并入（2026-11-08 新增）

本次新增四份规范：[文献综述](literature-review.md)、[标题、摘要与关键词](title-abstract-keywords.md)、[中文期刊规范](zh-journal-conventions.md)、[英文期刊规范](en-journal-conventions.md)。来源与取舍如下。

### 来源与版本

- 仓库：`yipng05-max/-skills`（学术志公开 skills 仓库）。本地副本：`C:\Users\Xiaobu\Desktop\-skills-main`。
- 该副本**不是 git clone**（无 `.git`），无法给 commit。版本参照：文件时间 2026-04-15，`CHANGELOG.md` 最新条目 2026-04-09。
- 仓库共 37 个 skill 目录（含一个裸 `.skill` 文件与两个协调器），逐个读过 description，写作相关者细读正文。
- 许可：MIT License, Copyright (c) 2026 一平博士 / 学术志。

### 采用

- **`literature-review-writer`**：结构模式（漏斗型／理论驱动型／争论型）、综合式与串珠式的对比、四类综合技术、批判性评价三层面、研究空白识别方式、引文密度经验值、顶刊综述与博士论文综述的差异表。
- **`paper-title-abstract-keywords`**：标题四角度、摘要三结构、关键词两策略的多方案交付机制，以及 C刊／SSCI 在篇幅（字 vs 词）、结构偏好与关键词策略上的语言差异。

### 不采用

- **WebSearch 自动检索 + `literature-verifier` 强制核查流程**：本 skill 定位明写“不替代系统文献检索”（见 frontmatter description），且引用归属已有规则（[证据、引用与实质修改](evidence-and-integrity.md) 第 3 节）。仅并入写作知识；文献检索与真实性核查仍由外部流程或作者负责。
- **`generate_docx.py` 与 Word 生成**：本 skill 不替代排版。排版规格仅以文字记在[英文期刊规范](en-journal-conventions.md) 第 8 节，并显式注明不生成文件。
- **`ta-research-AFP` / `ta-research-AFP-auto` 12 检查点协调器**：它们是全流程编排器，会调用上述被剔除的检索与核查能力，且面向 TA 定性研究。
- **三步硬停止交互**：原 skill 要求标题→摘要→关键词逐轮强制确认；本 skill 改为默认一次交付多方案（与 SKILL.md “不要为了开始修改而逐项询问完整问卷”一致），仅用户明确要求时逐轮。

### 未收录的其余 35 个及理由

- **非写作阶段工具（按用户判定排除）**：`argument-auditor` 是成稿后的论证逻辑审查，`counterfactual-reasoning` 是分析阶段的结论压力测试，均不属写作环节。
- **定性社会学导向**：`introduction-writer`、`ta-framework-builder/-writer`、`ta-methods-writer`、`ta-findings-writer`、`ta-discussion-writer`、`thematic-analysis`、`grounded-coding`、`analytic-memo`、`memo-coach`、`negative-case-finder`、`design-coherence-check`、`concept-clarifier`、`theory-fit-assessment`、`problematization`、`conceptual-framework-builder` —— 均以社会学与质性方法为默认场景，与本 skill 的定量与识别导向框架不兼容。
- **排版与评阅**：`paper-formatter`（按范文排版）、`paper-reviewer`、`feishu-paper-reviewer`（依赖飞书）。
- **检索、数据与元工具**：`cnki-advanced-search`、`foreign-literature-search`、`cjournal-analyzer`、`literature-verifier`、`pdf-bib-import`、`paper-analyzer`、`text-to-excel`、`skill-installer`、`top-journals-methods-scout`。
- **非学术场景**：`strategy-maker`（企业战略制定）。
- **学位论文专用**：`phd-literature-review`（约两万字、百科式覆盖，与期刊综述的选文策略相反）。

### 验证边界

四份新规范均为写作判断，不由 `scripts/check_protected_fields.py` 验证。篇幅数字（摘要 250～350 字 / 150～200 words）标为经验值，两份语言规范均要求期刊适配时核对该刊最新投稿须知；未对 AMJ、ASQ、SMJ、MISQ、OS、JCR、JMR 逐一核对官方 author guidelines，不将本文件当作投稿要求。

## 7. K-Dense scientific-agent-skills 并入（2026-11-08 新增）

本次新增两份规范：[表格与图形](tables-and-figures.md)、[期刊政策记录](journal-policy-record.md)，并在 [证据、引用与实质修改](evidence-and-integrity.md)（新增第 6、7 节）、[全局修改](global-editing.md)（G2 新增跳节审计）、[标题、摘要与关键词](title-abstract-keywords.md)（新增镜像与同一分析集规则）以及 SKILL.md 的 description、§2 与 §5 接入。

### 来源与版本

- 仓库：K-Dense `scientific-agent-skills`（arXiv:2609.00065）。本地副本：`C:\Users\Xiaobu\Desktop\scientific-agent-skills-main`。
- 该副本**不是 git clone**（无 `.git` 目录），无法给 commit。版本参照：`README.md` 标 Version 2.72.0，文件时间 2026-11-02。
- 仓库共 177 个 skill，按 README 的分类目录与 description 逐个筛选，仅细读与写作相关的 3 个（`scientific-writing`、`venue-templates`、`research-grants`）及 `peer-review` 的参考文件。
- 许可：MIT（`LICENSE.md`）。

### 采用

- **`scientific-writing/references/writing_principles.md`**：分析类型三分标注（确认性／探索性／描述性）、post hoc 不得改写为预设、数字与单位清单、零与缺失的五种含义不得混用，以及“不为流畅度改精度或加强论断”的否定规则。
- **`scientific-writing/references/imrad_structure.md`**：仅取其“跳节一致性审计”内核（目标↔结局↔结果↔结论；方法↔结果；摘要↔正文↔表图；注册↔稿件；引用↔参考文献表），**不引入 IMRaD 章节命名**——章节结构仍由 [学科与章节规范](discipline-and-sections.md) 的六类范式与章节任务表决定。
- **`scientific-writing/references/figures_tables.md`**：正文／表／图的形式选择、不得三处重复、表格与图形核查清单、题注自足要求、不得据截图重造数据。
- **`scientific-writing/references/journal_policies.md`**：带日期的政策快照清单、初投与生产阶段分开、不猜测缺失政策。
- **`venue-templates/references/venue_writing_styles.md`**：“不设句长／引文密度／近期文献占比／图表数量配额”的立场，以及“we observed”类证据语言的区别；后者已存在于本 skill 的 [局部修改](local-editing.md)，仅作交叉印证。

### 不采用

- **IMRaD 作为章节模板**：经管论文不用 IMRaD，与现有六类范式表冲突。
- **生物医学报告规范整套**（CONSORT 2025、PRISMA 2020、STROBE、STARD、TRIPOD+AI、CARE、ARRIVE 2.0、SQUIRE 2.0、ICMJE、CRediT）：不适用于经管；且[第 3 节](#3-官方材料核对)已确立“期刊规则须现查”的立场。
- **证据 ID 注册表与 claim marker 机制**（`[claim:C001] [evidence:E001]`、五份 JSON/CSV 模板）：粒度与本 skill 不符，且要求维护独立注册表，不适合以改稿为主的场景。
- **8 个 Python 审计脚本**（`audit_claims.py`、`check_consistency.py` 等）：沿用本 skill 不带脚本的定位；`check_protected_fields.py` 仍只做词面清单差异。
- **回应审稿意见与改投适配**：`venue-templates/references/reviewer_expectations.md` 的 rebuttal 契约与五段式应答、以及改投适配 6 步，本次按用户范围决定不纳入（回复信严格说不属 paper 写作）。
- **基金写作**：`research-grants/references/writing_principles.md` 的叙事与说服框架面向基金申请，非期刊论文体裁。

### 明确一项阴性结论：本仓库无社会学 skill

这是纯自然科学／生物医学库，“社会学的 skill 按内容判断是否纳入”在本仓库**无对象可判**。核查方式：全库搜 `sociolog`，唯一命中是 `paper-lookup/references/semantic-scholar.md` 中的学科枚举列表（`Sociology`、`Business`、`Economics` 与 `Art`、`History` 并列），不是 skill；`qualitative research` 仅作为 SRQR/COREQ 报告规范的条目名出现。此结论供日后复核，避免误判为漏检。

### 未收录的其余 skill 与理由

- **文献检索**：`literature-review`、`citation-management`、`paper-lookup`、`research-lookup`、`paperzilla`、`bgpt-paper-search`、`paperclip`、`open-notebook`、`pyzotero`——用户明确排除（与第 6 节立场一致）。
- **研究方法**：`statistical-analysis`、`statsmodels`、`statistical-power`、`experimental-design`、`scikit-learn`、`scikit-survival`、`shap`、`uncertainty-and-units`、`exploratory-data-analysis` 及全部科学计算包——用户明确排除。
- **出图与演示**：`scientific-visualization`、`scientific-schematics`、`infographics`、`generate-image`、`scientific-slides`、`latex-posters`、`pptx-posters`、`markdown-mermaid-writing`——呈现与出图，非写作。
- **审稿与评级**：`peer-review`、`scholar-evaluation`、`scientific-critical-thinking`——评审他人工作，非写作；仅 `peer-review` 的 `common_issues.md` 被参阅以校核主张—证据对齐的表述。
- **构思与分析**：`hypothesis-generation`、`scientific-brainstorming`、`what-if-oracle`、`consciousness-council`、`dhdna-profiler`、`hypogenic`、`arbor`——构思与决策，非写作。
- **非期刊论文体裁**：`research-grants`、`market-research-reports`、`clinical-reports`、`treatment-plans`、`clinical-decision-support`、`protocolsio-integration`。
- **文档处理与基础设施**：`liteparse`、`markitdown`、`datalad`、`modal`、`get-available-resources`、`autoskill`、`pi-agent` 等——工具链。
- **`venue-templates` 本体**：仅取两份 reference 的知识，不取 LaTeX 骨架与模板脚本。

### 验证边界

两份新规范为写作判断，不由 `scripts/check_protected_fields.py` 验证。源仓库的 U.S. ／生物医学期刊体例未逐一核对，不将 `journals_formatting.md` 的具体数字当经管期刊要求；`journal-policy-record.md` 本身即要求核对官方须知并记录访问日期，而非提供任何上限值。
