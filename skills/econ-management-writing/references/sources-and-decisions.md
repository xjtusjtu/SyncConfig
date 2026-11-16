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

## 8. 反模板化写作规范并入（2026-11-13 新增）

本次新增一份规范：[反模板化写作](anti-ai-style.md) 与一个只读扫描脚本 `scripts/check_ai_tells.py`，在 SKILL.md 的 description、§1、§2、§3、§5 接入。依据与取舍如下。

### 来源与版本

- 仓库：`brycewang-stanford/Auto-Empirical-Research-Skills`（公开 skills 集合）。实读与采用的具体条目：
  - `skills/33-Galaxy-Dawn-claude-scholar/skills/writing-anti-ai/`（SKILL.md、`references/patterns-chinese.md`、`patterns-english.md`、`phrases-to-cut.md`、中英文示例）；
  - `skills/35-bahayonghang-academic-writing-skills/skills/latex-thesis-zh/references/DEAI_GUIDE.md`、`FORBIDDEN_TERMS.md`；
  - `skills/47-conorbronsdon-avoid-ai-writing/SKILL.md`（P0/P1/P2 分级、上下文严格度矩阵、输出格式）；
  - `skills/49-voidborne-d-humanize-chinese/SKILL.md`（中文高/中/低危模式与学术专用检测维度）。
- 该仓库为 skill 集合再分发，各条目保留原作者与许可声明；本 skill 只取写作判断思路，**未复制其脚本、词库与长段正文**，模式清单为按经管论文场景重写的版本。
- 参考出处：`writing-anti-ai` 自述基于维基百科 “Signs of AI writing”；`avoid-ai-writing` 的分级与词表自述参考 `brandonwise/humanizer` 的词汇研究。这些是外部启发，不构成对成稿质量的独立验证。

### 采用

- **十类高风险写法**（空泛形容词、无证据绝对化、模糊量化、填充连接词、机械三段式、模板化段落、堆叠引用、元话语、空洞套话、格式噪声），每类给"为什么像模板 + 改法"。
- **起草前置**的工作顺序：先定可核查主张 → 再选句式 → 最后填连接词；骨架不清时逐句换词没有意义。
- **中英文替换参考表**，并明确"确有技术含义的术语不动""不得破坏术语一致性"。
- **分章节应用表**（摘要／引言／综述／理论／方法／结果／讨论／结论）。
- **P0/P1/P2 自检清单**：`scripts/check_ai_tells.py` 只报位置与类别，跳过代码块、公式、引用命令与参考文献表；输出 JSON，明确写出"不是质量分、不是作者身份判断、不是检测分数"。

### 不采用

- **"注入人味""注入灵魂"**（第一人称、情感、幽默、观点）：经管论文按目标期刊惯例写作，此处不采用。
- **口语化改写**与"降 AIGC 分数"的 best-of-N 流程：本 skill 不承诺任何检测分数，也不做面向检测器的优化。
- **词表硬配额**（如句长上限、每段句数、禁用词频率阈值、禁用括号）：与第 5 节"不新增固定句长、每段句数或机械配额"的既有立场冲突，只保留可核查的逐类判断。
- **段落首句必须中心句**的硬性要求：与"不强制所有段落都以结论开头"的现有规则冲突，以现有规则为准。
- **主动／被动语态配额与"保留作者声音"的强行改写**：不做语态比例控制。
- **`detect_cn.py` / `deai_check.py` 等检测脚本**：不引入第三方脚本与模型依赖；自写脚本只做词面扫描。
- **风险检查项"过度限定"**：与本 skill"正文少用防御性限定、局限集中"的既有规则相反，未纳入。

### 验证边界

- 新规范与新脚本均为写作判断与词面扫描，不由 `scripts/check_protected_fields.py` 验证，也没有独立代理前向测试、盲评或真实论文效果评估；不声称降低任何检测分数或优于候选 skill。
- 扫描器的命中率未经语料标注校准：同一措辞在作者笔下可能完全正当，逐条判断，不追求清零。

## 9. 反模板化写作规范扩充：humanizer 模式补充

本次在第 8 节基础上补入**结构层面的模板模式**与两道护栏。来源：`blader/humanizer`（MIT，69,325 stars，最近提交 2026-11-10，skill 版本 v4.0.0）。

### 来源与版本

- 仓库：`blader/humanizer`，MIT。skill 正文是单文件 `SKILL.md`（v4.0.0）：**26 条模式**分 A–F 六组——staging（铺垫而非陈述）、rhythm by rule（规则化节奏）、inflation（膨胀与借权威）、formatting by rule（格式装饰）、leftovers（对话与草稿残留）、wrong reader（写错了读者）；另有 `README.md`、`CHANGELOG.md`、`.claude-plugin/` 与 `.cursor-plugin/` 清单、`scripts/validate-package.py`，以及 `ISSUE_TEMPLATE/new-pattern.yml`（社区提交新模式的入口）。
- 该 skill 自述模式来源为**维基百科 "Signs of AI writing"**（WikiProject AI Cleanup 维护）。这与第 8 节引用的 `writing-anti-ai`、`brandonwise/humanizer` 同源——本 skill 的「去 AI 味」知识链在此收敛到同一个公共上游。
- 该仓库的词面研究型清单未逐条迁移：只取**模式维度与判断原则**，不取其词表配额与改写脚本。

### 采用

- **结构性模式 15 条**（[反模板化写作](anti-ai-style.md) §2.1 的 11–19、§2.2 的 20–25）：否定对比、单独成段收束、格言化表达、铺垫式开场、反驳无人异议、破折号当万能连接符、标题后重复首句、段落级三连、对话残留、赋予重大意义、含糊关联、浅层动名词短语、过度限定堆叠、回避简单动词、无主语句式。均按经管论文场景重写为中文识别信号与改法，未复制原文示例。
- **强／弱信号分级**（同文件 §2.3）：单条命中不作为证据；强信号出现一次即可动手，弱信号需同现（同一段落或小节内两个以上弱信号，或与任一强信号同现）。落到脚本的 `signal` 字段与 `manual_review_required` 首条。
- **何时不要动**（同文件 §6.1）：引文／书名／术语／专名内不动、2022-11-30 之前的文本不按 AI 痕迹处理、保留承载作者声音的细节、体裁的合法例外、作者样本与目标期刊风格优先。
- **事实保全核对**（同文件 §1 第 4 步）：改后逐项核对事实、名称、数字、日期、引文、排序与「两件事同时发生」类主张不得丢改——与既有 [证据与保护规则](evidence-and-integrity.md) 同向，写成流程的一步而非新规则。
- **改写而非打补丁**：不逐词替换，句子仍别扭时重写它所在的段落，句长要有变化。
- **脚本新增检测**：`scripts/check_ai_tells.py` 的 P1 增加 8 类（否定对比、格言化表达、铺垫式开场、反驳无人异议、赋予重大意义、含糊关联、浅层动名词短语、回避简单动词），P2 增加 1 类（无主语句式）与 5 项结构检测（单独成段收束、限定词堆叠、装饰性标题、破折号作连接符、标题后重复首句）；原 P2「否定排比」升级为 P1「否定对比」并合并「不是 X 而是 Y／不仅仅是 X 更是 Y／跨句拆分」三种构式。

### 不采用

- **「注入人味／注入灵魂」**（第一人称情绪、幽默、观点）：沿用第 8 节结论，经管论文按目标期刊惯例写作。
- **口语化改写**与面向检测器的 best-of-N 降分流程：不承诺任何检测分数。
- **词表硬配额**（句长上限、每段句数、禁用词频率阈值、禁用括号）：与既有「不新增固定句长或机械配额」的立场冲突。
- **「最终稿不得出现破折号」的绝对禁令**：该规则面向英文排版与个人化写作，中文期刊排版惯例不同；改为「密度按目标期刊与作者样本判断」，并保留 §2.1 #16 的判据式用法。
- **英文排版专属项**（直引号／弯引号、Title Case 标题）：不迁移。
- **「写文档而非写对象」**（本节将介绍…／下表比较了…）：中文论文中「如表 3 所示」「本节将介绍」属期刊体裁要求，机器识别必然误报，故不作为模式收录，只保留在人工判断层面。
- **段落级三连的自动检测**：拟人化判断成分高，只进清单（§2.1 #18），不进脚本。

### 验证边界

- 模式清单为人工改写，**未做检出率／误报率评测**；脚本的每条命中都需人工判断，词面命中不等于问题（§2.3、§6.1）。
- 本次只扩充规范与扫描脚本，未改动 SKILL.md 的其他条款；§16 自检清单已同步新增类别。
- 上游仍在迭代（2026-11-10 仍有提交），本 skill 只固定引用 v4.0.0 的模式集。
