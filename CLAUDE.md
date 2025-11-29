# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Quarto-based technical blog hosted on GitHub Pages (ickma2311.github.io). The site covers machine learning, algorithms, and technical tutorials with a focus on mathematical foundations and practical implementations.

## Common Commands

### Development Workflow
- `quarto render` - Build the entire website (outputs to `docs/` directory)
- `quarto preview` - Start local development server with live reload
- `quarto render <file.qmd>` - Render a specific document
- `quarto check` - Verify Quarto installation and project setup

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
2. Update the corresponding index.qmd file to include the new content
3. Add navigation entry to `_quarto.yml` if it should appear in the navbar dropdown
4. Use consistent frontmatter with `title` field
5. **Set publication date**: Always use the current date from the system for the `date` field in frontmatter
   - Get current date with: `date +"%Y-%m-%d"` (format: YYYY-MM-DD)
   - Example: `date: "2025-10-26"`
6. **Important**: After adding new navbar items, run `quarto render` (full site render) to update the navbar on ALL existing pages. Individual file renders only update that specific page.

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

**ALWAYS verify locally before pushing to prevent broken images on production:**

1. **Run full render**: `quarto render` (not individual file renders)

2. **CRITICAL: Restore ALL deleted images after full render**

   Full site renders delete images from multiple locations. You MUST restore them:

   ```bash
   # 1. Restore *_files/ directories (code-generated matplotlib/plotly figures)
   cp -r ML/*_files docs/ML/ 2>/dev/null
   cp -r Math/*_files docs/Math/ 2>/dev/null
   cp -r Algorithm/*_files docs/Algorithm/ 2>/dev/null

   # 2. Restore static images in ML/ and Math/
   cp ML/*.png docs/ML/ 2>/dev/null
   cp Math/MIT18.06/*.png docs/Math/MIT18.06/ 2>/dev/null

   # 3. Restore media/ directory images (referenced with ../media/image.png)
   mkdir -p docs/media
   cp media/*.png docs/media/ 2>/dev/null

   # 4. Restore imgs/ directory images (referenced with ../imgs/image.png)
   mkdir -p docs/imgs
   cp imgs/*.png docs/imgs/ 2>/dev/null

   # 5. Move any HTML files that failed to move
   find ML -maxdepth 1 -name "*.html" -exec mv {} docs/ML/ \; 2>/dev/null
   find Math/MIT18.06 -maxdepth 1 -name "*.html" -exec mv {} docs/Math/MIT18.06/ \; 2>/dev/null
   find Algorithm -maxdepth 1 -name "*.html" -exec mv {} docs/Algorithm/ \; 2>/dev/null

   # 6. Move index files
   mv Algorithm/index.html docs/Algorithm/ 2>/dev/null
   mv Math/index.html docs/Math/ 2>/dev/null
   mv index-backup.html docs/ 2>/dev/null
   ```

3. **Check git status**: `git status` - verify all image files are staged
   - Look for `docs/**/*_files/figure-html/*.png` files (code-generated)
   - Look for `docs/media/*.png` files (media directory)
   - Look for `docs/imgs/*.png` files (imgs directory)
   - Look for `docs/ML/*.png` and `docs/Math/MIT18.06/*.png` files (static images)

4. **Local preview**: Open `docs/` HTML files in browser to verify images load
   - Check pages with Jupyter notebooks (e.g., `mit1806-lecture1-geometry.html`)
   - Check pages with media references (e.g., `dropout.html`)
   - Verify matplotlib/plotly figures appear correctly

5. **Commit ALL generated files**: Don't commit `.html` without their images

6. **Only then push**: `git push`

**Why this matters**: GitHub Pages serves from the `docs/` directory. Quarto's full render deletes images from docs/ but keeps them in source directories. If images aren't copied back to docs/, the HTML will reference missing files, causing broken images on production even though they work locally.

**Image locations that get deleted:**
- `docs/**/*_files/` - Code-generated figures from Python/matplotlib
- `docs/media/` - Shared media referenced with `../media/`
- `docs/imgs/` - Shared images referenced with `../imgs/`
- `docs/ML/*.png` - Static chapter images
- `docs/Math/MIT18.06/*.png` - Static lecture images

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