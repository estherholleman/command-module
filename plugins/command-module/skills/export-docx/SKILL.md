---
name: export-docx
description: "Convert a markdown document to DOCX, with a proofing reminder before export. Use when a document needs to be shared as a Word file."
argument-hint: "[markdown file path]"
---

# Export DOCX

Convert a markdown document to DOCX format for external sharing. Checks for writing style review before exporting and discovers repo-specific conversion scripts.

## Phase 1: Identify the Document

**If a file path is provided in arguments:** Verify it exists and is a markdown file.

**If no path is provided:** Ask which document to export using the platform's question tool (AskUserQuestion in Claude Code, request_user_input in Codex, ask_user in Gemini).

## Phase 2: Proofing Check

Before converting, check whether this document has been through writing style review.

Look for a findings file matching the document name (e.g., `[document-name]-proof-findings.md` in the same directory or a sibling directory). Also check git log for recent commits mentioning "proof" and this file.

**If no evidence of proofing found:**

> This document hasn't been through `/proof` yet. Since it's about to leave as a deliverable, consider running `/proof [file path]` first to catch AI-typical writing patterns.
>
> 1. Run `/proof` now (recommended)
> 2. Skip and export anyway

Wait for the user's choice before proceeding. If they choose to run proof, stop and let them invoke it separately. Resume export-docx after proofing is complete.

**If proofing evidence exists:** Proceed directly to Phase 3.

## Phase 3: Discover Conversion Script

Search the current repository for a markdown-to-docx conversion script. Check these locations in order:

1. `scripts/md_to_docx.py`
2. `scripts/export_docx.py`
3. `scripts/convert_docx.py`
4. `scripts/to_docx.py`
5. Any Python file in `scripts/` containing "docx" in its name

Also check if the script has dependencies that need to be installed (look for `python-docx`, `docx`, or `pandoc` imports).

### If a repo-specific script is found

Read the first 30 lines to understand its usage (docstring, argparse setup). Run it with the appropriate arguments.

Typical invocation pattern:
```bash
python3 scripts/md_to_docx.py [input.md] -o [output.docx]
```

Adapt arguments based on the script's actual interface (read its argparse or usage string).

### If no repo-specific script is found

Check if `pandoc` is available:

```bash
pandoc --version
```

If pandoc is available, convert using:
```bash
pandoc [input.md] -o [output.docx] --from markdown --to docx
```

If neither a script nor pandoc is available, inform the user and suggest installing pandoc:

> No conversion script found in this repo and pandoc is not installed.
> Options:
> 1. Install pandoc: `brew install pandoc` (macOS) or `apt install pandoc` (Linux)
> 2. Create a repo-specific conversion script at `scripts/md_to_docx.py`

## Phase 4: Report

After successful conversion, report:

- Output file path and size
- Any warnings from the conversion process
- Suggest next steps if relevant (e.g., "open in Word to verify formatting")
