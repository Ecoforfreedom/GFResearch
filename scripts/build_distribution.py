#!/usr/bin/env python3
"""Build reproducible Claude/Bailian ZIPs and a self-contained instruction file."""

from __future__ import annotations

import argparse
import hashlib
import io
from pathlib import Path
import re
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
NAME = "gao-feng-research"
REFERENCES = (
    "references/runtime-capabilities.md",
    "references/research-modes.md",
    "references/source-blocks.md",
    "references/word-production.md",
)
# Explicit allowlist: never package .git, local credentials, work products, or dist.
PACKAGE_FILES = (
    "SKILL.md",
    *REFERENCES,
    "scripts/validate_gao_feng_research.py",
    "requirements.txt",
    "agents/openai.yaml",
    "examples/sample-output.docx",
)


def read_source(root: Path, relative: str) -> bytes:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"Missing required package file: {relative}")
    data = path.read_bytes()
    # Git may use CRLF on Windows. Normalizing text keeps packages reproducible.
    if path.suffix in {".md", ".py", ".txt", ".yaml"}:
        data = data.decode("utf-8-sig").replace("\r\n", "\n").encode("utf-8")
    return data


def without_frontmatter(text: str) -> str:
    parts = text.split("---\n", 2)
    if len(parts) != 3 or parts[0]:
        raise ValueError("SKILL.md must begin with YAML frontmatter")
    if not re.search(r"^name: gao-feng-research$", parts[1], re.MULTILINE):
        raise ValueError("Skill name must match the distribution folder")
    return parts[2].strip()


def portable_instructions(root: Path) -> bytes:
    sections = [
        "# Gao Feng Research — 完整单文件指令\n\n"
        "此文件由核心规范自动生成，供不能读取技能目录的 Agent 使用。"
        "请将全文作为工作流指令加载，并遵守所在平台的上层规则。\n\n"
        "下方已包含 SKILL、运行能力、研究模式、信源和 Word 规范。"
        "对这些 references 的读取要求由相应内嵌章节满足，无须另外访问仓库。"
        "根据任务选用相关模式；输出研究时不要复制这些操作说明。\n\n"
        "本文件不包含可执行脚本。需要自动检查 Word 时，使用完整技能包中的检查器；"
        "没有该能力时必须注明未运行检查，不能虚构完成状态。"
    ]
    documents = [("skill", without_frontmatter(read_source(root, "SKILL.md").decode("utf-8")))]
    documents += [(Path(path).stem, read_source(root, path).decode("utf-8").strip()) for path in REFERENCES]
    for anchor, text in documents:
        for path in REFERENCES:
            text = text.replace(f"]({path})", f"](#{Path(path).stem})")
        sections.append(f'<a id="{anchor}"></a>\n\n{text}')
    return ("\n\n---\n\n".join(sections) + "\n").encode("utf-8")


def zip_payload(root: Path, prefix: str) -> bytes:
    output = io.BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in PACKAGE_FILES:
            info = ZipInfo(prefix + relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, read_source(root, relative))
    return output.getvalue()


def artifacts(root: Path) -> dict[str, bytes]:
    # Validate the core entrypoint even if a caller only consumes the ZIPs.
    portable = portable_instructions(root)
    result = {
        f"{NAME}-claude.zip": zip_payload(root, f"{NAME}/"),
        f"{NAME}-bailian.zip": zip_payload(root, ""),
        "Gao-Feng-Research-Instructions.md": portable,
    }
    if len(result[f"{NAME}-bailian.zip"]) >= 10_000_000:
        raise ValueError("Bailian package must remain below 10 MB")
    result["SHA256SUMS.txt"] = "".join(
        f"{hashlib.sha256(data).hexdigest()}  {name}\n"
        for name, data in sorted(result.items())
    ).encode("ascii")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify checked-in artifacts without rewriting them")
    args = parser.parse_args()
    try:
        outputs = artifacts(ROOT)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    destination = ROOT / "dist"
    if args.check:
        stale = [name for name, data in outputs.items() if not (destination / name).is_file() or (destination / name).read_bytes() != data]
        if stale:
            print("Missing or stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"All {len(outputs)} distribution files match their sources.")
        return 0
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (destination / name).write_bytes(data)
        print(f"dist/{name} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
