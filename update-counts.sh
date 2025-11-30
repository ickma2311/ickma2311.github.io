#!/bin/bash

# Script to automatically update content counts in index.qmd

# Count Deep Learning chapters
DL_COUNT=$(grep -c "^\*\*\[Chapter" ML/deep-learning-book.qmd)

# Count MIT 18.06 lectures (including reflections)
MIT1806_COUNT=$(grep -c "^\*\*\[Lecture\|^\*\*\[Deep\|^\*\*\[From" Math/MIT18.06/lectures.qmd)

# Count MIT 18.065 lectures
MIT18065_COUNT=$(grep -c "^\*\*\[Lecture" Math/MIT18.065/lectures.qmd)

echo "Content counts:"
echo "  Deep Learning: $DL_COUNT chapters"
echo "  MIT 18.06SC: $MIT1806_COUNT lectures"
echo "  MIT 18.065: $MIT18065_COUNT lectures"

# Update index.qmd with the counts
sed -i.bak "s/Deep Learning Book <span class=\"section-count\">[0-9]* chapters/Deep Learning Book <span class=\"section-count\">$DL_COUNT chapters/" index.qmd

sed -i.bak "s/MIT 18.06SC Linear Algebra <span class=\"section-count\">[0-9]* lectures/MIT 18.06SC Linear Algebra <span class=\"section-count\">$MIT1806_COUNT lectures/" index.qmd

sed -i.bak "s/MIT 18.065 Matrix Methods <span class=\"section-count\">[0-9]* lectures/MIT 18.065 Matrix Methods <span class=\"section-count\">$MIT18065_COUNT lectures/" index.qmd

# Remove backup file
rm index.qmd.bak

echo ""
echo "Updated index.qmd with new counts!"
