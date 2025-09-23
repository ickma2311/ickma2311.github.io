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

1. Create the content file in the appropriate directory (`ML/` or `Algorithm/`)
2. Update the corresponding index.qmd file to include the new content
3. Add navigation entry to `_quarto.yml` if it should appear in the navbar dropdown
4. Use consistent frontmatter with `title` field

## Configuration Notes

- Output directory is set to `docs/` for GitHub Pages compatibility
- Theme: Cosmo with custom branding
- All pages include table of contents (`toc: true`)
- Site uses custom CSS from `styles.css`
- Jupyter notebooks are supported alongside Quarto markdown

## GitHub Pages Deployment

The site is automatically deployed from the `docs/` directory. After rendering, commit and push the `docs/` folder to trigger GitHub Pages rebuild.
- Author is Chao Ma