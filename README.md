# Gao Feng Research Skill

A reusable Codex skill for source-driven interview research, company and IPO updates, PPT ideation, and event-observation research. It produces Chinese- and English-language source packs in the established Gao Feng title-link-square-bullet Word format.

这是一个可直接安装的 Codex Research Skill，用于访谈准备、公司与 IPO 动态、PPT 构思以及展会观后感等资料研究。

## 核心工作流

每个保留的信源都必须经过两级中间加工，不能从文章直接跳到最终 bullet：

```text
原始文章
→ 句子级候选证据池
→ 2–3 个证据簇
→ 每个 source 最终 2–3 个高信息密度 bullet
```

- 内容充足的文章原则上先提取至少 6 个句子级候选。
- 候选句按共同观点聚合，例如 `S1–S3 → C1`、`S4–S6 → C2`。
- 每个证据簇二次整合为一个最终大 bullet。
- 最终每个 source 必须有 2–3 个不同且不重复的 bullet。
- 任何直接引文必须来自原文中的一个连续位置；多句引文必须前后相邻、顺序不变，中间不能跳句。
- 不相邻的材料只能综合转述或拆成不同证据点，不能用省略号拼成连续引文。

## 最终输出格式

```text
Original published headline
https://full-working-url
▪ Bold insight label: Consolidated evidence body.
▪ Bold second insight label: A different consolidated point.
▪ Optional third insight label: A third materially different point.
```

- 原标题和网址前不加 bullet。
- 只有证据段使用原生方块 bullet `▪`。
- 中文使用微软雅黑，英文和拉丁字符使用 Arial，全文 14 号字。
- 冒号前的提炼标签加粗，冒号后的证据正文使用常规字重。
- URL 必须显示完整地址，并保持蓝色、下划线和可点击状态。

## 安装

### 方法一：Git clone

Windows PowerShell：

```powershell
git clone https://github.com/Ecoforfreedom/gao-feng-research-skill.git "$env:USERPROFILE\.codex\skills\gao-feng-research"
```

macOS 或 Linux：

```bash
git clone https://github.com/Ecoforfreedom/gao-feng-research-skill.git ~/.codex/skills/gao-feng-research
```

### 方法二：下载 ZIP

在 GitHub 仓库页面选择 **Code → Download ZIP**，解压后将文件夹放到：

```text
~/.codex/skills/gao-feng-research
```

确保 `SKILL.md` 位于该目录根部，然后重新启动或刷新 Codex。

## 使用

可以直接调用：

```text
$gao-feng-research
```

也可以自然语言触发，例如：

- “按照 Gao Feng Research 格式做一个访谈 research。”
- “整理这家公司最新动态，每个信源保留 2–3 个大点。”
- “做一个展会观后感 research，重点找个人博客和 podcast。”

## 目录

```text
SKILL.md
agents/openai.yaml
references/research-modes.md
references/source-blocks.md
references/word-production.md
scripts/validate_gao_feng_research.py
examples/sample-output.docx
```

## Word 文档检查

生成 `.docx` 后运行：

```powershell
python scripts/validate_gao_feng_research.py "D:\path\research.docx"
```

检查器会验证 source 数量、每个 source 的 2–3 个 evidence bullet、标题与链接的 bullet 状态、方块 bullet、字体字号、链接格式、标签加粗和重复内容等结构要求。引文连续性、事实准确性、来源质量和内容洞见仍需人工复核。

## 示例

[`examples/sample-output.docx`](examples/sample-output.docx) 展示一个经过“6 个句子级候选 → 2 个证据簇 → 2 个最终大 bullet”流程生成的 Word 样张。
