#!/usr/bin/env python3
"""Validate the structural rules of a Gao Feng research Word document."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


VISIBLE_BULLETS = ("▪", "■", "•", "·", "●", "◼", "□")
PAGINATION_PROPS = ("keepNext", "keepLines", "pageBreakBefore")
URL_RE = re.compile(r"https?://\S+")


def text_of(paragraph) -> str:
    return paragraph.text.replace("\v", "\n")


def is_url(text: str) -> bool:
    return bool(URL_RE.fullmatch(text.strip()))


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", text))


def style_map(document) -> dict:
    return {style.style_id: style.element for style in document.styles}


def style_chain(styles: dict, style) -> list:
    if style is None:
        return []
    based_on = style.find(qn("w:basedOn"))
    inherited = []
    if based_on is not None:
        inherited = style_chain(styles, styles.get(based_on.get(qn("w:val"))))
    return inherited + [style.find(qn("w:rPr"))]


def effective_run_props(document, styles: dict, paragraph_el, run_el) -> dict:
    defaults = document.styles.element.xpath("./w:docDefaults/w:rPrDefault/w:rPr")
    paragraph_style_node = paragraph_el.find("./" + qn("w:pPr") + "/" + qn("w:pStyle"))
    if paragraph_style_node is not None:
        paragraph_style = styles.get(paragraph_style_node.get(qn("w:val")))
    else:
        paragraph_style = next(
            (
                style
                for style in styles.values()
                if style.get(qn("w:type")) == "paragraph" and style.get(qn("w:default")) == "1"
            ),
            None,
        )

    props = list(defaults) + style_chain(styles, paragraph_style)
    direct = run_el.find(qn("w:rPr"))
    run_style_node = direct.find(qn("w:rStyle")) if direct is not None else None
    if run_style_node is not None:
        props += style_chain(styles, styles.get(run_style_node.get(qn("w:val"))))
    props.append(direct)

    result = {
        "ascii": None,
        "hAnsi": None,
        "eastAsia": None,
        "sz": None,
        "szCs": None,
        "bold": False,
        "color": None,
        "underline": None,
        "run_style": run_style_node.get(qn("w:val")) if run_style_node is not None else None,
    }
    for prop in props:
        if prop is None:
            continue
        fonts = prop.find(qn("w:rFonts"))
        if fonts is not None:
            for key in ("ascii", "hAnsi", "eastAsia"):
                value = fonts.get(qn("w:" + key))
                if value is not None:
                    result[key] = value
        for key in ("sz", "szCs"):
            value = prop.find(qn("w:" + key))
            if value is not None:
                result[key] = value.get(qn("w:val"))
        bold = prop.find(qn("w:b"))
        if bold is not None:
            result["bold"] = bold.get(qn("w:val"), "1") not in ("0", "false", "off")
        color = prop.find(qn("w:color"))
        if color is not None and color.get(qn("w:val")):
            result["color"] = color.get(qn("w:val")).upper()
        underline = prop.find(qn("w:u"))
        if underline is not None:
            result["underline"] = underline.get(qn("w:val"), "single")

    if result["eastAsia"] == "微软雅黑":
        result["eastAsia"] = "Microsoft YaHei"
    return result


def numbered_glyph(document, paragraph) -> str | None:
    num_nodes = paragraph._p.xpath("./w:pPr/w:numPr/w:numId")
    if not num_nodes:
        return None
    num_id = num_nodes[0].get(qn("w:val"))
    numbering = document.part.numbering_part.element
    abstract_nodes = numbering.xpath(f'./w:num[@w:numId="{num_id}"]/w:abstractNumId')
    if not abstract_nodes:
        return None
    abstract_id = abstract_nodes[0].get(qn("w:val"))
    glyph_nodes = numbering.xpath(
        f'./w:abstractNum[@w:abstractNumId="{abstract_id}"]/w:lvl[@w:ilvl="0"]/w:lvlText'
    )
    return glyph_nodes[0].get(qn("w:val")) if glyph_nodes else None


def split_label_excerpt(text: str) -> tuple[str, str] | None:
    positions = [position for position in (text.find("："), text.find(":")) if position >= 0]
    if not positions:
        return None
    position = min(positions)
    return text[:position].strip(), text[position + 1 :].strip()


def label_is_bold(document, styles: dict, paragraph, label_end: int) -> bool:
    consumed = 0
    saw_label_text = False
    for run_el in paragraph._p.xpath(".//w:r[w:t]"):
        run_text = "".join(node.text or "" for node in run_el.findall(qn("w:t")))
        relevant = run_text[: max(0, label_end - consumed)]
        if relevant.strip():
            saw_label_text = True
            if not effective_run_props(document, styles, paragraph._p, run_el)["bold"]:
                return False
        consumed += len(run_text)
        if consumed >= label_end:
            break
    return saw_label_text


def excerpt_has_regular_text(document, styles: dict, paragraph, label_end: int) -> bool:
    consumed = 0
    for run_el in paragraph._p.xpath(".//w:r[w:t]"):
        run_text = "".join(node.text or "" for node in run_el.findall(qn("w:t")))
        start = max(0, label_end - consumed)
        relevant = run_text[start:]
        if relevant.strip() and not effective_run_props(document, styles, paragraph._p, run_el)["bold"]:
            return True
        consumed += len(run_text)
    return False


def validate(path: Path) -> dict:
    document = Document(path)
    paragraphs = document.paragraphs
    styles = style_map(document)
    errors: list[dict] = []
    warnings: list[dict] = []
    labels: list[str] = []
    evidence_bodies: list[str] = []
    urls: list[str] = []
    source_titles: dict[int, str] = {}
    bullet_count = 0

    expected_font = {
        "ascii": "Arial",
        "hAnsi": "Arial",
        "eastAsia": "Microsoft YaHei",
        "sz": "28",
        "szCs": "28",
    }

    for index, paragraph in enumerate(paragraphs):
        text = text_of(paragraph).strip()
        if not text:
            continue
        has_numbering = bool(paragraph._p.xpath("./w:pPr/w:numPr"))

        for prop in PAGINATION_PROPS:
            if paragraph._p.xpath(f"./w:pPr/w:{prop}"):
                errors.append({"paragraph": index, "type": f"forbidden_{prop}", "text": text[:160]})

        if "原文：" in text or "原文:" in text or "Original text:" in text:
            errors.append({"paragraph": index, "type": "forbidden_original_text_label", "text": text[:160]})

        for run_index, run_el in enumerate(paragraph._p.xpath(".//w:r[w:t]")):
            props = effective_run_props(document, styles, paragraph._p, run_el)
            actual = {key: props[key] for key in expected_font}
            if actual != expected_font:
                run_text = "".join(node.text or "" for node in run_el.findall(qn("w:t")))
                errors.append(
                    {
                        "paragraph": index,
                        "run": run_index,
                        "type": "font_or_size_mismatch",
                        "expected": expected_font,
                        "actual": actual,
                        "text": run_text[:80],
                    }
                )

        if has_numbering:
            bullet_count += 1
            if text.startswith(VISIBLE_BULLETS):
                errors.append({"paragraph": index, "type": "typed_bullet_plus_numbering", "text": text[:160]})
            glyph = numbered_glyph(document, paragraph)
            if glyph != "▪":
                errors.append({"paragraph": index, "type": "non_square_numbering", "glyph": glyph, "text": text[:160]})

            parts = split_label_excerpt(text)
            if parts is None:
                errors.append({"paragraph": index, "type": "missing_label_colon", "text": text[:180]})
            else:
                label, excerpt = parts
                labels.append(label)
                evidence_bodies.append(excerpt)
                colon_end = min(position for position in (text.find("："), text.find(":")) if position >= 0) + 1
                if not label_is_bold(document, styles, paragraph, colon_end):
                    errors.append({"paragraph": index, "type": "label_not_bold", "label": label})
                if not excerpt_has_regular_text(document, styles, paragraph, colon_end):
                    errors.append({"paragraph": index, "type": "excerpt_not_regular_weight", "label": label})
                if not excerpt:
                    errors.append({"paragraph": index, "type": "empty_evidence_body", "label": label})

        if is_url(text):
            urls.append(text)
            if has_numbering or text.startswith(VISIBLE_BULLETS):
                errors.append({"paragraph": index, "type": "url_has_bullet", "text": text})
            hyperlink_runs = paragraph._p.xpath(".//w:hyperlink//w:r[w:t]")
            if not hyperlink_runs:
                errors.append({"paragraph": index, "type": "url_not_hyperlinked", "text": text})
            else:
                decorated = False
                for run_el in hyperlink_runs:
                    props = effective_run_props(document, styles, paragraph._p, run_el)
                    if props["run_style"] == "Hyperlink" or (
                        props["color"] in ("0000FF", "0563C1") and props["underline"] not in (None, "none", "0")
                    ):
                        decorated = True
                if not decorated:
                    errors.append({"paragraph": index, "type": "url_not_blue_and_underlined", "text": text})

            previous = index - 1
            while previous >= 0 and not text_of(paragraphs[previous]).strip():
                previous -= 1
            if previous < 0:
                errors.append({"paragraph": index, "type": "missing_source_headline", "text": text})
            else:
                title = paragraphs[previous]
                title_text = text_of(title).strip()
                source_titles[index] = title_text
                if title._p.xpath("./w:pPr/w:numPr") or title_text.startswith(VISIBLE_BULLETS):
                    errors.append({"paragraph": previous, "type": "headline_has_bullet", "text": title_text[:180]})
                title_runs = title._p.xpath(".//w:r[w:t]")
                if not title_runs or not all(
                    effective_run_props(document, styles, title._p, run_el)["bold"] for run_el in title_runs
                ):
                    errors.append({"paragraph": previous, "type": "headline_not_bold", "text": title_text[:180]})

            evidence_indices = []
            cursor = index + 1
            while cursor < len(paragraphs):
                following_text = text_of(paragraphs[cursor]).strip()
                if not following_text:
                    cursor += 1
                    continue
                if paragraphs[cursor]._p.xpath("./w:pPr/w:numPr"):
                    evidence_indices.append(cursor)
                    cursor += 1
                    continue
                break
            if not evidence_indices:
                errors.append({"paragraph": index, "type": "source_has_no_evidence_bullets", "text": text})
            else:
                if len(evidence_indices) < 2:
                    errors.append({"paragraph": index, "type": "source_has_fewer_than_two_evidence_bullets", "count": len(evidence_indices), "text": text})
                elif len(evidence_indices) > 3:
                    errors.append({"paragraph": index, "type": "source_has_more_than_three_evidence_bullets", "count": len(evidence_indices), "text": text})

            if evidence_indices and previous >= 0:
                title_is_chinese = has_cjk(text_of(paragraphs[previous]))
                for evidence_index in evidence_indices:
                    evidence_parts = split_label_excerpt(text_of(paragraphs[evidence_index]).strip())
                    if evidence_parts:
                        label_is_chinese = has_cjk(evidence_parts[0])
                        if title_is_chinese != label_is_chinese:
                            errors.append(
                                {
                                    "paragraph": evidence_index,
                                    "type": "label_language_does_not_match_source_headline",
                                    "headline": text_of(paragraphs[previous]).strip()[:160],
                                    "label": evidence_parts[0],
                                }
                            )

    duplicate_labels = [value for value, count in Counter(labels).items() if count > 1]
    duplicate_bodies = [value for value, count in Counter(evidence_bodies).items() if count > 1]
    duplicate_urls = [value for value, count in Counter(urls).items() if count > 1]
    if duplicate_labels:
        errors.append({"type": "duplicate_evidence_labels", "values": duplicate_labels})
    if duplicate_bodies:
        errors.append({"type": "duplicate_evidence_bodies", "values": duplicate_bodies})
    if duplicate_urls:
        warnings.append({"type": "duplicate_source_urls_review_for_conceptual_repetition", "values": duplicate_urls})
    if not urls:
        errors.append({"type": "no_source_urls"})
    if not bullet_count:
        errors.append({"type": "no_evidence_bullets"})

    return {
        "document": str(path),
        "source_count": len(urls),
        "evidence_bullet_count": bullet_count,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
        "manual_review_required": [
            "Exact headline, URL, publication date, and quotation fidelity",
            "A sentence-level intermediate pool was created for every retained source, targeting at least six useful candidates for a substantial article",
            "Candidates were grouped into exactly two or three coherent evidence clusters before final drafting",
            "Each final source bullet is the second-pass consolidation of one cluster rather than a raw candidate sentence",
            "Ordinary-source candidates were merged as paraphrase, not concatenated quotations",
            "Every verbatim quotation is one continuous span from a single source location",
            "Every multi-sentence quotation contains adjacent source sentences in original order with no omitted intervening sentence or material",
            "Ellipses, line breaks, or separate bullets were not used to join non-contiguous quotations",
            "Any longer verbatim combination is supported by ownership, permission, public-domain status, or a clear open license",
            "Quoted text remains within the applicable cumulative limit for each source",
            "Conceptual de-duplication and source quality",
            "Whether evidence answers each interview question",
            "At least one Chinese source per question when interview-led",
            "Rendered layout of every page",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path, help="Gao Feng research .docx file")
    parser.add_argument("--json-out", type=Path, help="Optional path for the JSON report")
    args = parser.parse_args()
    if not args.docx.is_file():
        parser.error(f"File not found: {args.docx}")
    report = validate(args.docx)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
