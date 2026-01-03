#!/bin/bash

# Script to automatically update content counts in index.qmd

# Count Deep Learning chapters
DL_COUNT=$(grep -c "^\*\*\[Chapter" ML/deep-learning-book.qmd)

# Count MIT 18.06 lectures (including reflections)
MIT1806_COUNT=$(grep -c "^\*\*\[Lecture\|^\*\*\[Deep\|^\*\*\[From" Math/MIT18.06/lectures.qmd)

# Count MIT 18.065 lectures
MIT18065_COUNT=$(grep -c "^\*\*\[Lecture" Math/MIT18.065/lectures.qmd)

# Count EE 364A lectures and chapters
EE364A_COUNT=$(grep -c "^\*\*\[Lecture\|^\*\*\[Chapter" Math/EE364A/lectures.qmd)

echo "Content counts:"
echo "  Deep Learning: $DL_COUNT chapters"
echo "  MIT 18.06SC: $MIT1806_COUNT lectures"
echo "  MIT 18.065: $MIT18065_COUNT lectures"
echo "  Stanford EE 364A: $EE364A_COUNT lectures"

# Update index.qmd with the counts
sed -i.bak "s/Deep Learning Book <span class=\"section-count\">[0-9]* chapters/Deep Learning Book <span class=\"section-count\">$DL_COUNT chapters/" index.qmd

sed -i.bak "s/MIT 18.06SC Linear Algebra <span class=\"section-count\">[0-9]* lectures/MIT 18.06SC Linear Algebra <span class=\"section-count\">$MIT1806_COUNT lectures/" index.qmd

sed -i.bak "s/MIT 18.065: Linear Algebra Applications <span class=\"section-count\">[0-9]* lectures\{0,1\}/MIT 18.065: Linear Algebra Applications <span class=\"section-count\">$MIT18065_COUNT lectures/" index.qmd

sed -i.bak "s/Stanford EE 364A: Convex Optimization <span class=\"section-count\">[0-9]* lectures\{0,1\}/Stanford EE 364A: Convex Optimization <span class=\"section-count\">$EE364A_COUNT lectures/" index.qmd

# Remove backup file
rm index.qmd.bak

echo ""
echo "✅ Updated index.qmd with new counts!"
echo ""
echo "⚠️  REMINDER: Did you update the 'Latest 4' items on the homepage?"
echo "   If you added new content, manually edit index.qmd to:"
echo "   1. Replace the oldest item with the new item"
echo "   2. Keep the 4 most recent items visible (newest first)"
echo "   3. Then run: quarto render index.qmd"
echo ""
