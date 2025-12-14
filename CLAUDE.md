# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Quarto-based technical blog hosted on GitHub Pages (ickma2311.github.io). The site covers machine learning, algorithms, and technical tutorials with a focus on mathematical foundations and practical implementations.

## Common Commands

### Development Workflow
- `./publish.sh` - **RECOMMENDED**: Safe publishing script that handles everything automatically
  - Backs up critical files before render
  - Runs full site render
  - Restores ALL images and assets
  - Verifies no files were lost
  - Shows changes for review
- `quarto preview` - Start local development server with live reload
- `quarto render <file.qmd>` - Render a specific document (navbar won't update on other pages)
- `quarto check` - Verify Quarto installation and project setup

### CRITICAL: Publishing New Content
**ALWAYS use `./publish.sh` instead of `quarto render` or `./render-site.sh`**

The `publish.sh` script prevents these common problems:
1. Images getting deleted (backs up and restores automatically)
2. Homepage/about page disappearing (backs up critical files)
3. Navbar not updating (runs full site render)
4. Duplicate HTML files in wrong locations (cleans up automatically)

### Content Management
- Create new ML content in `ML/` directory
- Create new algorithm content in `Algorithm/` directory
- Update navigation by editing `_quarto.yml` navbar section
- Add new content to respective index.qmd files for discoverability

## Project Structure

```
├── _quarto.yml          # Main configuration file
├── docs/                # Generated output (GitHub Pages source)
├── index.qmd            # Homepage
├── about.qmd            # About page
├── ML/                  # Machine Learning content
│   ├── index.qmd        # ML topics overview
│   ├── *.qmd            # ML articles
│   └── *.ipynb          # Jupyter notebooks
├── Algorithm/           # Algorithm content
│   ├── index.qmd        # Algorithm topics overview
│   └── *.qmd            # Algorithm articles
├── imgs/                # Image assets
├── media/               # Media files
└── styles.css           # Custom CSS styles
```

## Content Organization

The site uses a hierarchical navigation structure defined in `_quarto.yml`:
- Two main sections: "ML" and "Algorithm"
- Each section has an index page that serves as a directory
- Content is categorized by topic (e.g., "NumPy Fundamentals", "Clustering Algorithms")

### Adding New Content

1. Create the content file in the appropriate directory (`ML/` or `Math/` or `Algorithm/`)
2. **Add to list page**: Update the corresponding list page (e.g., `ML/deep-learning-book.qmd`, `Math/MIT18.06/lectures.qmd`)
3. **Update homepage automatically**: Run `./update-counts.sh` to update section counts on homepage
4. Add navigation entry to `_quarto.yml` if it should appear in the navbar dropdown
5. Use consistent frontmatter with `title` field
6. **Set publication date**: Always use the current date from the system for the `date` field in frontmatter
   - Get current date with: `date +"%Y-%m-%d"` (format: YYYY-MM-DD)
   - Example: `date: "2025-10-26"`
7. **Important**: After adding new navbar items, run `quarto render` (full site render) to update the navbar on ALL existing pages. Individual file renders only update that specific page.

### Maintaining the Homepage

The homepage (`index.qmd`) shows the **latest 4 items** from each section with a count badge.

**CRITICAL: When adding new content, you MUST:**

1. **Add the new item to the appropriate list page:**
   - Deep Learning: `ML/deep-learning-book.qmd`
   - MIT 18.06SC: `Math/MIT18.06/lectures.qmd`
   - MIT 18.065: `Math/MIT18.065/lectures.qmd`

2. **Update the homepage manually** by editing `index.qmd`:
   - Replace the oldest item in the "Latest 4" with the new item
   - Keep the 4 most recent items visible
   - Order: newest first (top), oldest last (bottom)

3. **Update section counts automatically:**
   ```bash
   ./update-counts.sh
   ```
   This script automatically counts items in list pages and updates the count badges in `index.qmd`.

4. **Render and verify:**
   ```bash
   quarto render index.qmd
   ```

**Example workflow when adding Chapter 9.8:**
```bash
# 1. Create the new content file
vim ML/chapter-9-8.qmd

# 2. Add to list page
vim ML/deep-learning-book.qmd  # Add Chapter 9.8 entry

# 3. Update homepage
vim index.qmd  # Replace Chapter 9.4 with 9.8, keep 9.7, 9.6, and 9.5

# 4. Update counts automatically
./update-counts.sh

# 5. Render
quarto render index.qmd
```

**Warning**: The homepage will NOT automatically update when you add new content. You must manually update `index.qmd` to show the latest 4 items.

## Configuration Notes

- Output directory is set to `docs/` for GitHub Pages compatibility
- Theme: Cosmo with custom branding
- All pages include table of contents (`toc: true`)
- Site uses custom CSS from `styles.css`
- Jupyter notebooks are supported alongside Quarto markdown

## GitHub Pages Deployment

The site is automatically deployed from the `docs/` directory. After rendering, commit and push the `docs/` folder to trigger GitHub Pages rebuild.
- Author is Chao Ma
- GitHub Pages URL: https://ickma2311.github.io/

### Pre-Push Checklist (CRITICAL)

**The `./publish.sh` script handles everything automatically. Just follow these steps:**

1. **Run the publish script**:
   ```bash
   ./publish.sh
   ```

   The script automatically:
   - Backs up critical files (index.html, about.html, reflection images)
   - Runs full site render
   - Restores ALL images from all locations
   - Fixes misplaced HTML files
   - Removes duplicates
   - Verifies nothing was lost

2. **Review the output**: The script shows file counts before/after and lists any errors

3. **Check git status**: `git status` to see what changed

4. **Local preview**: Open `docs/index.html` in browser to verify

5. **Commit and push**:
   ```bash
   git add -A
   git commit -m "Add new content"
   git push
   ```

**Why this matters**: GitHub Pages serves from `docs/`. Quarto's render recreates `docs/` and deletes images. The publish script ensures all images are restored before you commit.

### Post-Deployment Cleanup

After successfully pushing changes to GitHub:

1. **Archive source images**: Move original images from Downloads to the banana folder for organization
   ```bash
   mv ~/Downloads/<image-name>.png ~/Documents/banana/
   ```
   Example: `mv ~/Downloads/seq2seq.png ~/Documents/banana/`

2. **Verify deployment**: Check GitHub Pages to ensure the site deployed successfully and images load correctly

## LinkedIn Post Guidelines

### Emoji Usage
When drafting LinkedIn posts for blog content, use these emojis:
- **Deep Learning topics**: ∇ (delta/nabla symbol) - represents gradients and optimization
- **Linear Algebra topics**: 📐 (triangle/ruler) - represents geometric and matrix concepts

### Writing Process
1. **Identify the key insight**: Focus on the main conceptual connection or "aha moment" from the blog post
2. **Use "connecting the dots" tone**: Emphasize how concepts link together (e.g., "how linear algebra connects to machine learning")
3. **Structure (Knowledge Card Format)**:
   - Start with emoji and chapter reference (e.g., "∇ **Deep Learning Book (Chapter 8.1)**" or "📐 **MIT 18.06SC Linear Algebra (Lecture 19)**")
   - Clear statement or equation (e.g., "Learning ≠ Optimization")
   - 2-4 bullet points (🔹) with key insights
   - Philosophical closing line (💡)
   - Link to full blog post (📖)
   - Source attribution at the end (e.g., "My notes on Deep Learning (Ian Goodfellow) Chapter X.X" or "My notes on MIT 18.06SC Linear Algebra - Lecture XX")
4. **Keep it concise**: Aim for clarity over comprehensiveness - use knowledge card format for quick, digestible insights
5. **Course naming**:
   - Always use "MIT 18.06SC" (not just "MIT 18.06") for linear algebra posts
   - Use full course titles to maintain consistency
6. **Include relevant hashtags**: #MachineLearning #LinearAlgebra #DeepLearning