# 来源、审读范围与设计取舍

审读日期：2026-10-09。下列判断基于实际获取的仓库正文，不是星数、README 宣传或效果证明。分支会变化，复核请使用所列 commit。

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
