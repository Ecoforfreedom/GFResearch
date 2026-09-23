# Runtime Capabilities and Fallbacks

This is the execution adapter for all platforms. Apply the same evidence and formatting contract regardless of the model. Use only tools actually exposed by the host; do not invent tool names or assume a Codex installation.

## Capability check

Resolve the following internally at the start of a task. Report only a gap that affects the requested result; do not burden the user with a setup questionnaire.

| Capability | Full workflow | If unavailable |
| --- | --- | --- |
| Read skill files | Read the selected references relative to `SKILL.md` | Use the complete single-file instructions; embedded sections count as loaded references |
| Search and retrieve sources | Search, then open the original article or document and record its date and location | Work from supplied full texts; state the coverage date and that latest developments are unverified. Do not infer quotes from snippets or fabricate missing URLs |
| Maintain working evidence | Store candidate sentences, source locations, clusters, and consolidated claims in temporary files or workflow state | Keep equivalent structured working notes within the task context. These are evidence records, not a request to disclose hidden reasoning |
| Create DOCX | Use available document tools, or Python with `python-docx` | Deliver the finished source blocks as a Markdown draft and identify Word production as pending |
| Execute the validator | Run the bundled Python script on the actual output file | Manually check content and visible format; explicitly mark automated validation as not run |
| Render and inspect pages | Use the host renderer, Word, LibreOffice, or another available equivalent; view every page | Label visual review as pending; never treat a structural pass as a visual pass |
| Microsoft YaHei and Arial | Set the required font names in the DOCX and render with those fonts installed | Keep the required font declarations and report substitutions. Do not silently certify typography using substitute fonts |

Research with only user-supplied material is useful, but is not proof of current status. Continue useful work with the available material; ask for an essential missing source only when it prevents the requested research.

## Paths, dependencies, and tools

- Treat the skill directory, working directory, and output directory as separate locations. Resolve the skill directory once and use host-provided writable storage for outputs.
- Python scripts support Windows, macOS, and Linux. Use the available Python 3.10+ executable; it may be named `python`, `python3`, or `py`.
- `requirements.txt` declares the DOCX validator dependency. Install it only when the host permits dependency installation, preferably in a task-specific environment. Managed platforms may require an administrator or a prebuilt environment instead.
- Network retrieval, OCR, podcast transcription, DOCX generation, and page rendering are host capabilities, not functionality bundled in this skill.
- Do not require a missing companion skill. When the host provides a document skill, use it for its document mechanics while preserving this skill's editorial contract.
- A skill does not grant publishing, messaging, account access, or other external mutation permissions. Follow the user's actual task and the host's authorization rules.

## Markdown fallback

Use this only when a requested file cannot be produced in the current host, or when Markdown was requested. Complete the same evidence workflow and preserve source language, exact headlines, URLs, source count per question, and two or three distinct bullets per source.

```text
Original published headline
https://full-working-url
▪ **Evidence label:** A complete source-grounded evidence body.
▪ **Second label:** A distinct source-grounded evidence body.
```

The literal `▪` is appropriate in a text-only draft. When converting to Word, replace it with native square list numbering; do not retain a typed glyph plus a Word bullet. Markdown cannot enforce 14 pt type, fonts, pagination, or Word list properties. Keep the missing-capability note outside the research body and do not invent a download link.

## Handoff and workflow nodes

If research and document production run in different nodes, pass the complete source blocks and evidence records forward, not only a summary. Each source needs its exact headline, URL (or an explicit missing-link marker), publication date if available, language, and two or three labels with their evidence bodies. Preserve attribution and distinguish paraphrase from quotation. The document node applies `word-production.md`, runs the validator, and performs page review if its environment supports them.

Do not silently omit instructions because a platform truncates a prompt or file. Inject the full single-file edition as instructions or make it available for complete retrieval. Ordinary keyword-based knowledge-base retrieval can miss formatting and source rules and is not equivalent to loading the full skill.
