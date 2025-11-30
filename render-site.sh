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

# Check if render succeeded
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Render completed with errors. Restoring images..."

    # Restore deleted images from git (images only, not HTML files)
    git checkout docs/**/*.png docs/**/*.jpg docs/**/*.gif docs/**/*.svg 2>/dev/null

    # Move any HTML files that ended up in wrong places
    find . -maxdepth 3 -name "*.html" ! -path "./docs/*" -type f -exec mv {} docs/ \; 2>/dev/null

    echo "✅ Images restored and HTML files moved"
else
    echo ""
    echo "✅ Render completed successfully!"
fi

echo ""
echo "📊 Verifying output..."
echo "   HTML files in docs/: $(find docs -name "*.html" | wc -l | tr -d ' ')"
echo "   Image files in docs/: $(find docs -name "*.png" | wc -l | tr -d ' ')"
