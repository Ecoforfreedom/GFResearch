# Gao Feng Research Skill

高风信源型研究工作流，可用于 Codex、Claude Code、Claude 自定义 Skills、阿里云百炼，以及能加载完整指令的其他 Agent 平台。

用于访谈准备、公司与 IPO 动态、PPT 构思、展会观后感。核心格式保持为：**引用文章原标题 → 完整链接 → 每个信源 2–3 个方块要点**。研究规范共用一份，工具由所在平台提供。

## 选择你的使用方式

| 使用环境 | 入口 | 操作 |
| --- | --- | --- |
| Claude 网页端 / 支持自定义 Skills 的客户端 | [下载 Claude 技能包](https://raw.githubusercontent.com/Ecoforfreedom/GFResearch/main/dist/gao-feng-research-claude.zip) | 在 Skills 上传入口上传此 ZIP 并启用；包内含 `gao-feng-research/` 文件夹 |
| Claude Code | 下方安装命令 | 将完整仓库放到 `~/.claude/skills/gao-feng-research`，调用 `/gao-feng-research` |
| 阿里云百炼自定义 Skill / Agent Studio Skill | [下载百炼技能包](https://raw.githubusercontent.com/Ecoforfreedom/GFResearch/main/dist/gao-feng-research-bailian.zip) | 使用此根目录直接包含 `SKILL.md` 的 ZIP 上传，并添加到目标智能体 |
| Codex | 下方安装命令 | 将完整仓库放到 `~/.agents/skills/gao-feng-research`，调用 `$gao-feng-research` |
| Dify、扣子等提供 Agent 指令或完整文件读取入口的平台 | [打开完整单文件指令](dist/Gao-Feng-Research-Instructions.md) · [下载原始文件](https://raw.githubusercontent.com/Ecoforfreedom/GFResearch/main/dist/Gao-Feng-Research-Instructions.md) | 将全文放入 Agent 指令，或让 Agent 完整读取该文件；再配置搜索、网页正文读取和文件输出工具 |

两种 ZIP 结构不同，请按平台选择；GitHub 的 **Code → Download ZIP** 是仓库源码包，不是上述平台上传包。其他原生支持 Agent Skills 的平台可以使用完整技能文件夹，具体上传结构按该平台要求。

## 安装到 Claude Code 或 Codex

只需选择正在使用的平台。目标目录已存在时，先检查已有内容；不要直接覆盖已有自定义版本。

Claude Code，macOS / Linux：

```bash
git clone https://github.com/Ecoforfreedom/GFResearch.git ~/.claude/skills/gao-feng-research
```

Claude Code，Windows PowerShell：

```powershell
git clone https://github.com/Ecoforfreedom/GFResearch.git "$env:USERPROFILE\.claude\skills\gao-feng-research"
```

Codex，macOS / Linux：

```bash
git clone https://github.com/Ecoforfreedom/GFResearch.git ~/.agents/skills/gao-feng-research
```

Codex，Windows PowerShell：

```powershell
git clone https://github.com/Ecoforfreedom/GFResearch.git "$env:USERPROFILE\.agents\skills\gao-feng-research"
```

也可下载仓库，解压后把文件夹命名为 `gao-feng-research`，放到对应目录。已有 `.codex/skills/gao-feng-research` 安装且仍可识别的用户可以保留原位置，避免同时安装两个同名副本。项目内共享可使用 `.claude/skills/gao-feng-research` 或 `.agents/skills/gao-feng-research`。

## 调用示例

```text
按 Gao Feng Research 做一个森马 AI 转型 research，供服装企业会见准备使用。
要具体案例、实施方式和量化结果，加入第三方报告；每个信源 2–3 个不重复的点。
```

Claude Code 可以在需求前加 `/gao-feng-research`；Codex 可以加 `$gao-feng-research`。其他平台在启用 Skill 或加载完整指令后使用上述自然语言即可。

## 规范与调用顺序

```text
SKILL.md
→ 首次运行检查 runtime-capabilities.md
→ 理解任务和附件
→ research-modes.md：选择访谈、公司动态、观后感、PPT 或增量更新模式
→ source-blocks.md：查阅信源与建立句子级证据池
→ 将候选材料聚合为每个信源 2–3 个证据簇
→ 二次整合与跨信源去重
→ word-production.md：制作 Word
→ 结构检查 → 逐页视觉检查 → 修订交付
```

内容充足的文章先提取至少 6 个句子级候选，再聚合成 2–3 个最终要点。候选证据与整合记录属于工作材料，默认不加入交付文档。直接引文必须连续；转述与引文明确区分，引用长度遵守适用的权利和平台规则。

最终文档只使用中英文信源。原标题和链接前没有 bullet；证据使用原生方块 `▪`。中文微软雅黑、英文 Arial、全文 14 pt；冒号前标签加粗，后面的证据正文保持常规字重，网址完整、蓝色、下划线且可点击。访谈提纲默认每问两个强信源，至少一个中文。除非另有要求，不加 summary、结论或访谈切口。

## 工具能力与降级

生成 Word 的平台需要文档工具或代码运行能力。运行检查器需要 Python 3.10+ 与 `python-docx`；在允许安装依赖的环境中，从技能目录执行：

```bash
python -m pip install -r requirements.txt
python scripts/validate_gao_feng_research.py /path/to/research.docx
```

根据环境可改用 `python3` 或 `py`。检查器验证文件结构，不代替事实核验或逐页检查。字体和渲染工具由运行环境提供。

没有 Word 输出能力时，Agent 应交付相同内容结构的 Markdown 草稿，并说明待排版；没有联网能力时，只能基于提供的材料开展研究并注明时效边界。任何平台都不得把未执行的搜索、校验或渲染说成已通过。

## 仓库维护与发布包

```text
SKILL.md                              共用核心入口
references/                           模式、信源、Word、运行能力规范
agents/openai.yaml                    可选 Codex 界面元数据
adapters/platform-guide.md            平台安装和接入说明
requirements.txt                      Word 检查器依赖
scripts/validate_gao_feng_research.py   现有 Word 检查器
scripts/build_distribution.py          由同一套规范生成分发文件
dist/                                 两种上传 ZIP、完整单文件指令与校验值
examples/sample-output.docx            既有格式样张
tests/test_distribution.py             分发结构与完整性检查
```

修改核心或引用规范后重新生成分发文件，避免几个平台的规则不同步：

```bash
python scripts/build_distribution.py
python scripts/build_distribution.py --check
python -m unittest discover -s tests
```

单文件版自动内嵌核心及全部研究规范，不需要 Agent 再访问仓库读取其他指令。Word 检查器作为可执行文件只在 ZIP 和仓库中提供；单文件版会说明相关能力缺失时如何处理。

平台入口依据官方文档核对于 2026-09-23。链接和具体区别见 [平台接入指南](adapters/platform-guide.md)。
