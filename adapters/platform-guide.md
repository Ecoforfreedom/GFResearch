# 平台接入指南

核对日期：2026-09-23。以下说明区分已核对的文件规范、本地完成的检查与仍需在目标平台执行的实际验收。

## 一份规范，三种接入方式

1. **原生技能目录**：Claude Code、Codex 及其他遵循 Agent Skills 的环境，加载 `SKILL.md` 和相对路径资源。技能目录命名为 `gao-feng-research`。
2. **上传技能包**：Claude 与百炼使用同一内容、不同 ZIP 外层结构。上传后仍需在目标账号启用，并确认可用工具。
3. **完整指令模式**：不能读取技能目录的平台使用 `dist/Gao-Feng-Research-Instructions.md`。把全文放入指令上下文，或明确要求完整读取该文件；不要仅存入按需召回的知识库。

这些接入方式只定义如何加载工作流。搜索、文件读写、代码执行和渲染仍由平台提供。`references/runtime-capabilities.md` 规定对应的降级和完成状态。

## Claude Code

个人安装目录为 `~/.claude/skills/gao-feng-research`，项目共享目录为 `.claude/skills/gao-feng-research`。目录中直接包含 `SKILL.md`，调用 `/gao-feng-research` 后附具体需求。无须把全文复制进 `CLAUDE.md`，也不依赖 Codex 的 `agents/openai.yaml`。依据：[Claude Code Skills](https://code.claude.com/docs/en/skills)。

## Claude 自定义 Skills

使用 `dist/gao-feng-research-claude.zip`，在账号的 Skills 上传入口启用。包结构如下：

```text
gao-feng-research-claude.zip
└── gao-feng-research/
    ├── SKILL.md
    ├── references/
    ├── scripts/validate_gao_feng_research.py
    └── requirements.txt
```

其他随包资源省略显示。该 ZIP 带技能名外层目录，符合 Claude 的自定义技能打包说明。当前账号是否显示上传入口、允许代码与文件生成，需要在该账号确认。依据：[创建自定义 Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)。

## 阿里云百炼 / Agent Studio

使用 `dist/gao-feng-research-bailian.zip`，在 Skill 管理的自定义技能上传入口提交，然后将技能添加至目标智能体。此包根目录直接包含 `SKILL.md`，与 Claude 包不同：

```text
gao-feng-research-bailian.zip
├── SKILL.md
├── references/
├── scripts/validate_gao_feng_research.py
└── requirements.txt
```

官方自定义 Skill 文档要求 ZIP 根部有 `SKILL.md`，并规定包体不超过 10 MB。生成器按此结构打包；平台审核及线上执行尚需在目标账号验证。依据：[百炼 Skill](https://help.aliyun.com/zh/model-studio/introduction-to-skill)、[Agent Studio 技能](https://help.aliyun.com/zh/model-studio/managed-agents-skill)。

## Codex

当前文档所列用户级目录为 `~/.agents/skills/gao-feng-research`，项目级目录为 `.agents/skills/gao-feng-research`。使用 `$gao-feng-research` 或自然语言触发。`agents/openai.yaml` 只用于 Codex 界面与调用配置；保留它不会给其他平台增加运行依赖。依据：[OpenAI 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills)。

## Dify、扣子与其他 Agent 平台

这是通用指令接入方案，不是这些平台的专有应用导入文件。若平台提供原生 Skill 上传，应先核对其当期规范；若只有指令、知识或工作流入口，可按以下方式接入：

1. 将完整单文件版放入 Agent 指令。字段长度不足时，通过可完整读取的文件或上下文注入方式加载；不要让平台静默截断。
2. 给 Agent 配置搜索和原网页正文获取能力，确保能核对标题、日期、链接和句子所在位置。
3. 有代码或文档服务时，接入文件生成，再以实际输出文件运行结构检查和页面检查。无文件能力时按规范输出 Markdown 草稿。
4. 多节点流程应显式传递研究任务、完整信源块及证据记录。渲染节点接收文件本身，输出真实的下载地址和检查状态。

Dify 的 Agent 节点提供自然语言 Instructions 和可配置工具，可作为上述指令接入方式的具体例子。不同版本节点的文件传递与变量长度限制应按实际文档核对。依据：[Dify Agent 节点](https://docs.dify.ai/en/cloud/use-dify/nodes/agent)。扣子及其他平台在本仓库中仅提供通用接入思路，未声明已完成专有导入或线上测试。

## 验收方法

用同一个测试任务检查每个目标平台：

```text
请按 Gao Feng Research 研究森马的 AI 转型。
先检索近期材料，选两个能支持具体业务机制和量化结果的强信源。
每个信源保留 2–3 个不同要点，原标题和完整链接独立成行。
完成证据池和二次整合，生成 Word；说明实际完成了哪些检查。
```

核对加载成功、信源真实且时效正确、每源 2–3 点、引用与转述分明、没有重复、标题/链接无 bullet。如果生成 Word，还需检查原生方块 bullet、字体、14 pt、实际结构报告与逐页查看记录。

当前完成的是分发包结构、规范内嵌完整性、依赖声明和既有 Word 样张的本地检查。此测试任务是目标平台验收清单，不能据此宣称已在所有平台跑通。

Agent Skills 的通用结构依据：[开放规范](https://agentskills.io/specification)。
