#!/bin/bash

# =============================================================================
# publish.sh - Safe publishing script for ickma.dev
# =============================================================================
# This script safely publishes new content by:
# 1. Backing up critical files before render
# 2. Running full site render
# 3. Restoring all images and assets
# 4. Verifying no files were lost
# 5. Showing what changed for review
# =============================================================================

set -e  # Exit on error

echo "========================================"
echo "  ickma.dev Publishing Script"
echo "========================================"
echo ""

# -----------------------------------------------------------------------------
# Step 1: Backup critical files
# -----------------------------------------------------------------------------
echo "📦 Step 1: Backing up critical files..."

BACKUP_DIR=".backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup index.html and about.html (MUST exist in root docs/)
cp docs/index.html "$BACKUP_DIR/" 2>/dev/null || echo "   ⚠️  docs/index.html not found"
cp docs/about.html "$BACKUP_DIR/" 2>/dev/null || echo "   ⚠️  docs/about.html not found"
cp docs/index-backup.html "$BACKUP_DIR/" 2>/dev/null || true

# Backup reflection images (often get deleted)
if [ -d "docs/Math/reflections" ]; then
    mkdir -p "$BACKUP_DIR/Math/reflections"
    cp docs/Math/reflections/*.png "$BACKUP_DIR/Math/reflections/" 2>/dev/null || true
    cp docs/Math/reflections/*.mp4 "$BACKUP_DIR/Math/reflections/" 2>/dev/null || true
fi

# Count files before render
HTML_BEFORE=$(find docs -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
PNG_BEFORE=$(find docs -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
echo "   Before render: $HTML_BEFORE HTML, $PNG_BEFORE PNG"
echo "   Backup saved to: $BACKUP_DIR"
echo ""

# -----------------------------------------------------------------------------
# Step 2: Clean stray HTML files from source directories
# -----------------------------------------------------------------------------
echo "🧹 Step 2: Cleaning stray HTML files from source..."

find ML -maxdepth 1 -name "*.html" -delete 2>/dev/null || true
find Math -type f -name "*.html" ! -path "*/docs/*" -delete 2>/dev/null || true
find Algorithm -maxdepth 1 -name "*.html" -delete 2>/dev/null || true
rm -f index.html about.html index-backup.html 2>/dev/null || true

echo "   ✅ Source directories cleaned"
echo ""

# -----------------------------------------------------------------------------
# Step 3: Run quarto render
# -----------------------------------------------------------------------------
echo "🔨 Step 3: Running quarto render..."
echo ""

quarto render || true  # Continue even if there are errors

echo ""

# -----------------------------------------------------------------------------
# Step 4: Restore ALL images
# -----------------------------------------------------------------------------
echo "🖼️  Step 4: Restoring images..."

# 4a. Restore *_files directories (notebook-generated images)
echo "   → Restoring *_files directories..."
cp -r ML/*_files docs/ML/ 2>/dev/null || true

# Handle nested Math subdirectories
for dir in Math/MIT18.06 Math/MIT18.065 Math/EE364A Math/reflections; do
    if [ -d "$dir" ]; then
        find "$dir" -name "*_files" -type d 2>/dev/null | while read files_dir; do
            target_dir="docs/$dir"
            mkdir -p "$target_dir" 2>/dev/null
            cp -r "$files_dir" "$target_dir/" 2>/dev/null || true
        done
    fi
done

cp -r Algorithm/*_files docs/Algorithm/ 2>/dev/null || true

# 4b. Restore static PNG images in each directory
echo "   → Restoring static PNG images..."
cp ML/*.png docs/ML/ 2>/dev/null || true
mkdir -p docs/ML/papers docs/Math/Calculus docs/Theory-to-Repro 2>/dev/null || true
cp ML/papers/*.png docs/ML/papers/ 2>/dev/null || true
cp ML/papers/*.jpg docs/ML/papers/ 2>/dev/null || true
cp Math/MIT18.06/*.png docs/Math/MIT18.06/ 2>/dev/null || true
cp Math/MIT18.065/*.png docs/Math/MIT18.065/ 2>/dev/null || true
cp Math/EE364A/*.png docs/Math/EE364A/ 2>/dev/null || true
cp Math/Calculus/*.png docs/Math/Calculus/ 2>/dev/null || true
cp Math/reflections/*.png docs/Math/reflections/ 2>/dev/null || true
cp Math/reflections/*.mp4 docs/Math/reflections/ 2>/dev/null || true
cp Theory-to-Repro/*.png docs/Theory-to-Repro/ 2>/dev/null || true
cp Theory-to-Repro/*.jpg docs/Theory-to-Repro/ 2>/dev/null || true

# 4c. Restore media/ and imgs/ directories
echo "   → Restoring media/ and imgs/..."
mkdir -p docs/media docs/imgs 2>/dev/null
cp media/*.png docs/media/ 2>/dev/null || true
cp media/*.jpg docs/media/ 2>/dev/null || true
cp imgs/*.png docs/imgs/ 2>/dev/null || true
cp imgs/*.jpg docs/imgs/ 2>/dev/null || true

# 4d. Restore backed up files if they're missing
echo "   → Checking critical files..."
if [ ! -f "docs/index.html" ] && [ -f "$BACKUP_DIR/index.html" ]; then
    cp "$BACKUP_DIR/index.html" docs/
    echo "   ⚠️  Restored index.html from backup"
fi
if [ ! -f "docs/about.html" ] && [ -f "$BACKUP_DIR/about.html" ]; then
    cp "$BACKUP_DIR/about.html" docs/
    echo "   ⚠️  Restored about.html from backup"
fi

# Restore reflection images if deleted
if [ -d "$BACKUP_DIR/Math/reflections" ]; then
    mkdir -p docs/Math/reflections
    cp "$BACKUP_DIR/Math/reflections"/* docs/Math/reflections/ 2>/dev/null || true
fi

echo ""

# -----------------------------------------------------------------------------
# Step 5: Fix misplaced HTML files
# -----------------------------------------------------------------------------
echo "🔧 Step 5: Fixing misplaced HTML files..."

# Move HTML files from source to correct docs/ subdirectory
# IMPORTANT: Do NOT move to root docs/ - move to correct subdirectory

for src_dir in ML Math/MIT18.06 Math/MIT18.065 Math/EE364A Math/reflections Algorithm; do
    if [ -d "$src_dir" ]; then
        find "$src_dir" -maxdepth 1 -name "*.html" -type f 2>/dev/null | while read html_file; do
            filename=$(basename "$html_file")
            target_dir="docs/$src_dir"
            mkdir -p "$target_dir"
            mv "$html_file" "$target_dir/" 2>/dev/null || true
            echo "   Moved: $html_file → $target_dir/"
        done
    fi
done

# Remove any duplicate HTML files in root docs/ (except index.html, about.html, index-backup.html)
echo "   → Removing duplicates from root docs/..."
DUPLICATES_REMOVED=0
for html_file in docs/*.html; do
    filename=$(basename "$html_file")
    # Keep only these files in root docs/
    if [[ "$filename" != "index.html" && "$filename" != "about.html" && "$filename" != "index-backup.html" ]]; then
        # Check if this file exists in a subdirectory
        if find docs -mindepth 2 -name "$filename" -type f | grep -q .; then
            rm "$html_file" 2>/dev/null || true
            ((DUPLICATES_REMOVED++)) || true
        fi
    fi
done
echo "   Removed $DUPLICATES_REMOVED duplicate files from root docs/"
echo ""

# -----------------------------------------------------------------------------
# Step 6: Verify output
# -----------------------------------------------------------------------------
echo "✅ Step 6: Verifying output..."

HTML_AFTER=$(find docs -name "*.html" | wc -l | tr -d ' ')
PNG_AFTER=$(find docs -name "*.png" | wc -l | tr -d ' ')

echo ""
echo "   📊 File counts:"
echo "      HTML: $HTML_BEFORE → $HTML_AFTER"
echo "      PNG:  $PNG_BEFORE → $PNG_AFTER"
echo ""

# Check critical files exist
ERRORS=0

if [ ! -f "docs/index.html" ]; then
    echo "   ❌ MISSING: docs/index.html"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -f "docs/about.html" ]; then
    echo "   ❌ MISSING: docs/about.html"
    ERRORS=$((ERRORS + 1))
fi

# Check for reflection images
if [ -d "Math/reflections" ] && [ -f "Math/reflections/first-order.png" ]; then
    if [ ! -f "docs/Math/reflections/first-order.png" ]; then
        echo "   ❌ MISSING: docs/Math/reflections/first-order.png"
        ERRORS=$((ERRORS + 1))
    fi
fi

if [ $ERRORS -eq 0 ]; then
    echo "   ✅ All critical files present"
else
    echo ""
    echo "   ⚠️  $ERRORS critical files missing!"
    echo "   Run: git checkout HEAD -- docs/ to restore from last commit"
fi

echo ""

# -----------------------------------------------------------------------------
# Step 7: Show git status for review
# -----------------------------------------------------------------------------
echo "📋 Step 7: Changes ready for review..."
echo ""
echo "   Run 'git status' to see changes"
echo "   Run 'git diff --stat' to see summary"
echo ""

# Cleanup old backups (keep last 5)
ls -dt .backup_* 2>/dev/null | tail -n +6 | xargs rm -rf 2>/dev/null || true

echo "========================================"
echo "  Publishing complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Check locally: open docs/index.html"
echo "  3. Commit: git add -A && git commit -m 'Add new content'"
echo "  4. Push: git push"
echo ""
