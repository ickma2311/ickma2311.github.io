---
name: blog-write-social
description: Draft or revise technical blog content in this repo (Quarto .qmd), check for math/syntax/spelling/equation errors, improve readability, and generate LinkedIn knowledge-card plus single-tweet Twitter posts for new blog entries.
---

# Blog Write Social

## Overview
Use this skill to turn notes into polished QMD posts, catch technical errors, smooth readability, and produce LinkedIn/Twitter copy for new blog entries.

## Inputs to Collect
- Source content: Notion URL or pasted notes
- Target section: ML / Algorithm / Math
- Title + desired depth/length
- Images to include and their local paths
- Link to the published post (for social). Default base URL: https://ickma2311.github.io/

## Workflow

### 1) Draft or Revise the Post (QMD)
- If a Notion URL is provided and Notion MCP tools are available, fetch the content. Otherwise, ask for the notes directly.
- Create or edit the QMD with frontmatter `title` and `date` (use `date +"%Y-%m-%d"`).
- Preserve equations, code blocks, and notation. Do not change meaning.
- Add short intros/transitions where sections jump abruptly.
- If images are provided, place them in the requested local folder and use correct relative paths.

### 1b) Project Integration (Required)
- Update the relevant list page (e.g., `ML/deep-learning-book.qmd`, `Math/MIT18.065/lectures.qmd`).
- Update homepage “Latest 4” in `index.qmd` (newest first) and keep count badges in sync via `./update-counts.sh`.
- Add the new post to the navbar in `_quarto.yml`.
- Render via `./publish.sh` to refresh all pages and restore assets.
- Verify the rendered HTML includes the new content (grep the output file).

### 2) Error Check (Technical + Syntax)
- Validate math signs, denominators, conditions, and dimensions.
- Check equation references, LaTeX syntax, spelling, and grammar.
- List fixes clearly; apply edits only if asked.

### 3) Readability Pass
- Add 1-2 intuition sentences where the notes are too terse.
- Keep at least one concrete example if present in the notes.
- Tighten long sentences; improve flow with transitions.

### 4) Social Posts
- LinkedIn: follow the knowledge-card format and emoji rules in `references/social-posts.md`.
- Twitter: single tweet with the key insight + link (see `references/social-posts.md`).

## References
- `references/blog-quality-checklist.md`
- `references/social-posts.md`
