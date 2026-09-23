# Word Production and Quality Control

## Cross-platform execution

Apply these rules with the current host's document tools. Python 3.10+ and the dependency in `requirements.txt` are sufficient to run the bundled validator; creating and rendering a DOCX also require suitable tools in the host. Use `references/runtime-capabilities.md` for missing execution, rendering, font, or file-creation capabilities. A manual check or Markdown draft must not be described as a fully validated Word document.

## Document structure

Use a clean source-pack layout. A document may contain a descriptive title and date, followed by question headings or thematic section headings. Under each section, repeat:

```text
Original article headline
https://full-working-url
▪ Evidence label: Faithful source-based paraphrase with an optional “short continuous quotation anchor.”
▪ Second evidence label: Different paraphrased evidence or a permitted quotation.
▪ Optional third evidence label: A third materially different consolidated point when justified.
```

The content hierarchy is always:

```text
Document title and date, if needed
→ interview question or thematic section heading
→ original source headline
→ full clickable URL
→ first consolidated square-bullet evidence point
→ one or two additional consolidated evidence points from that source
→ next source headline
```

Every source block must contain exactly two or three evidence bullets. These are the final outputs of the private two-stage workflow in `source-blocks.md`, not raw sentence-level candidates.

Do not place a bullet before the question, section heading, source headline, or URL. Do not place the URL before the source headline.

Do not add a contents page, executive summary, methodology, conclusion, or interview suggestions unless requested.

## Typography

Apply the following to every paragraph and run, including titles, questions, headings, URLs, labels, and quotations:

- 14 pt throughout;
- Chinese/east Asian font: Microsoft YaHei;
- English/Latin font: Arial;
- document and section headings: black and bold;
- source headlines: black and bold;
- evidence label through the colon: bold;
- paraphrase and any short quotation after the colon: regular;
- URL: blue, underlined, and clickable.

Set both direct run fonts and the relevant OOXML `w:rFonts` values when necessary so Word and renderers agree.

## Bullets and indentation

- Headline: plain paragraph, no visible bullet, no `w:numPr`.
- URL: plain paragraph, no visible bullet, no `w:numPr`.
- Evidence: native Word list paragraph whose numbering glyph is exactly `▪`.
- Do not type a square or dot manually in a paragraph that also has Word numbering.
- Use a readable hanging indent and keep all evidence bullets aligned.

If the title or URL still shows a dot after editing, rebuild the document or the affected source block cleanly. Repeatedly clearing visible characters is not sufficient when hidden numbering remains.

## Pagination

Do not use `keepNext`, `keepLines`, or `pageBreakBefore`; these settings have produced small marks in the left margin in the target workflow. Insert an explicit page break in a standalone blank paragraph/run instead.

Keep a source headline, its URL, and the beginning of its first bullet on the same page when practical. Avoid:

- a headline alone at the bottom of a page;
- a URL separated from its headline;
- a single Chinese character or English word stranded on its own line;
- clipped hyperlinks, bullets, or quotations;
- blank pages created by stacked page breaks.

## Versioning and incremental work

- Never overwrite a previously delivered revision.
- Use a new filename such as `... v2.docx`, `... v3.docx`, and so on.
- When the user supplies one full article, change only that source block unless broader work is requested.
- Compare non-empty paragraphs before and after the edit to confirm unrelated content is unchanged.

## Validation and render gate

Run:

```text
python scripts/validate_gao_feng_research.py /path/to/research.docx
```

Run from the skill directory, or use the script's resolved absolute path. Quote paths containing spaces on every operating system.

Fix all reported errors, including any source with fewer than two or more than three evidence bullets. Manually verify that every verbatim quotation is one continuous source span. If it contains multiple sentences, confirm that they are adjacent in the original, appear in unchanged order, and omit no intervening sentence or material. Broader permission may change the allowable quotation length, but it does not permit joining non-contiguous passages.

Then render the final `.docx` to page images using the available document-rendering workflow and inspect every page at normal reading size. Check:

- no bullets before headlines or URLs;
- square bullets only before evidence;
- no left-margin black marks;
- correct 14 pt type and visible Chinese/English font behavior;
- bold labels ending at the colon;
- hyperlink wrapping;
- no overlaps, clipping, orphaned headings, awkward single-character lines, or blank pages;
- all pages reflect the latest revision rather than an older render.

After any correction, re-render and inspect again. Run the validator once more after the final edit.
