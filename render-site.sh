#!/bin/bash

# Helper script to render the site cleanly without errors
# This script cleans up stray HTML files before rendering

echo "🧹 Cleaning up stray HTML files in source directories..."

# Remove HTML files from source directories (they should only be in docs/)
find ML -maxdepth 1 -name "*.html" -delete 2>/dev/null
find Math -type f -name "*.html" ! -path "*/docs/*" -delete 2>/dev/null
find Algorithm -maxdepth 1 -name "*.html" -delete 2>/dev/null
rm -f index.html about.html index-backup.html 2>/dev/null

echo "✅ Cleanup complete"
echo ""
echo "🔨 Running quarto render..."

# Run the full site render
quarto render

# Store exit code
RENDER_EXIT_CODE=$?

echo ""
if [ $RENDER_EXIT_CODE -ne 0 ]; then
    echo "⚠️  Render completed with errors. Restoring images..."
else
    echo "✅ Render completed successfully. Restoring images..."
fi

# Restore images (always needed because Quarto deletes them during render)

# 1. Restore *_files directories (code-generated images from notebooks)
echo "   → Restoring *_files directories..."
cp -r ML/*_files docs/ML/ 2>/dev/null
# Handle nested subdirectories in Math/
find Math -name "*_files" -type d 2>/dev/null | while read dir; do
    # Get the relative path after "Math/"
    rel_path="${dir#Math/}"
    # Create parent directory in docs if needed
    mkdir -p "docs/Math/$(dirname "$rel_path")" 2>/dev/null
    # Copy the directory
    cp -r "$dir" "docs/Math/$(dirname "$rel_path")/" 2>/dev/null
done
cp -r Algorithm/*_files docs/Algorithm/ 2>/dev/null

# 2. Restore static PNG images
echo "   → Restoring static PNG images..."
cp ML/*.png docs/ML/ 2>/dev/null
cp Math/MIT18.06/*.png docs/Math/MIT18.06/ 2>/dev/null
cp Math/MIT18.065/*.png docs/Math/MIT18.065/ 2>/dev/null
cp Math/EE364A/*.png docs/Math/EE364A/ 2>/dev/null

# 3. Restore media/ and imgs/ directories
echo "   → Restoring media/ and imgs/ directories..."
mkdir -p docs/media docs/imgs 2>/dev/null
cp media/*.png docs/media/ 2>/dev/null
cp imgs/*.png docs/imgs/ 2>/dev/null

# 4. Move any HTML files that ended up in wrong places
find . -maxdepth 3 -name "*.html" ! -path "./docs/*" -type f -exec mv {} docs/ \; 2>/dev/null

echo "✅ Images restored and HTML files moved"

echo ""
echo "📊 Verifying output..."
echo "   HTML files in docs/: $(find docs -name "*.html" | wc -l | tr -d ' ')"
echo "   Image files in docs/: $(find docs -name "*.png" | wc -l | tr -d ' ')"
