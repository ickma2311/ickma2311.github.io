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

# Count Calculus notes
CALCULUS_COUNT=$(grep -c "^\*\*\[" Math/Calculus/index.qmd)

# Count Probability notes
PROBABILITY_COUNT=$(grep -c "^\*\*\[" Math/Probability/index.qmd)

# Count Information Theory notes
INFO_THEORY_COUNT=$(grep -c "^\*\*\[" Math/InformationTheory/index.qmd)

# Count all Math items
MATH_COUNT=$((MIT1806_COUNT + MIT18065_COUNT + EE364A_COUNT + CALCULUS_COUNT + PROBABILITY_COUNT + INFO_THEORY_COUNT))

# Count Deep Learning papers
DL_PAPERS_COUNT=$(grep -c "^\*\*\[" ML/papers/index.qmd)

# Count RL notes
RL_COUNT=$(grep -c "^\*\*\[" ML/RL/index.qmd)

# Count JAX notes
JAX_COUNT=$(grep -c "^\*\*\[" ML/JAX/index.qmd)

# Count ML HW-SW codesign notes
HWSW_COUNT=$(grep -c "^\*\*\[" ML/HW-SW-codesign/index.qmd)

echo "Content counts:"
echo "  Deep Learning: $DL_COUNT chapters"
echo "  Math: $MATH_COUNT items"
echo "    Probability: $PROBABILITY_COUNT notes"
echo "    Information Theory: $INFO_THEORY_COUNT notes"
echo "    Calculus: $CALCULUS_COUNT notes"
echo "    MIT 18.06SC: $MIT1806_COUNT lectures"
echo "    MIT 18.065: $MIT18065_COUNT lectures"
echo "    Stanford EE 364A: $EE364A_COUNT lectures"
echo "  Deep Learning Papers: $DL_PAPERS_COUNT notes"
echo "  JAX: $JAX_COUNT notes"
echo "  RL: $RL_COUNT notes"
echo "  ML HW-SW Codesign: $HWSW_COUNT notes"

# Update index.qmd with the counts
sed -i.bak "s/Goodfellow Deep Learning Book <span class=\"section-count\">[0-9]* chapters/Goodfellow Deep Learning Book <span class=\"section-count\">$DL_COUNT chapters/" index.qmd

sed -i.bak "s/Math <span class=\"section-count\">[0-9]* item[s]\\{0,1\\}/Math <span class=\\\"section-count\\\">$MATH_COUNT item$( [ $MATH_COUNT -eq 1 ] && echo '' || echo 's' )/" index.qmd

sed -i.bak "s/Papers in Deep Learning <span class=\"section-count\">[0-9]* note[s]\\{0,1\\}/Papers in Deep Learning <span class=\\\"section-count\\\">$DL_PAPERS_COUNT note$( [ $DL_PAPERS_COUNT -eq 1 ] && echo '' || echo 's' )/" index.qmd

sed -i.bak "s/JAX <span class=\"section-count\">[0-9]* note[s]\\{0,1\\}/JAX <span class=\\\"section-count\\\">$JAX_COUNT note$( [ $JAX_COUNT -eq 1 ] && echo '' || echo 's' )/" index.qmd

sed -i.bak "s/RL <span class=\"section-count\">[0-9]* note[s]\\{0,1\\}/RL <span class=\\\"section-count\\\">$RL_COUNT note$( [ $RL_COUNT -eq 1 ] && echo '' || echo 's' )/" index.qmd

sed -i.bak "s/ML HW-SW Codesign <span class=\"section-count\">[0-9]* note[s]\\{0,1\\}/ML HW-SW Codesign <span class=\\\"section-count\\\">$HWSW_COUNT note$( [ $HWSW_COUNT -eq 1 ] && echo '' || echo 's' )/" index.qmd

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
