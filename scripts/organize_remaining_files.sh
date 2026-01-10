#!/bin/bash
# organize_remaining_files.sh
# Moves misplaced scripts and docs into scripts/ and docs/ directories.
# Safe to delete after use.

set -e

# Move scripts (top-level .sh and .py files except main entry points)
for f in *.sh *.py; do
  if [[ -f "$f" && ! "$f" =~ ^(start_all_fixed.sh|start_all.sh|run_tests.sh|README.md|.*_README.md|.*_GUIDE.md|.*_DOCUMENTATION.md)$ ]]; then
    echo "Moving $f to scripts/"
    mv "$f" scripts/
  fi
done

# Move markdown docs (top-level .md files except README.md)
for f in *.md; do
  if [[ -f "$f" && "$f" != "README.md" ]]; then
    echo "Moving $f to docs/"
    mv "$f" docs/
  fi
done

echo "Organization complete. Review scripts/ and docs/ for results."
