#!/usr/bin/env bash
# Hook: validates that CHANGELOG.md has an ## Unreleased section and
# a <!-- bump: TYPE --> comment when source files have been modified.
#
# Intended to run as a Claude Code pre-commit hook.

set -euo pipefail

# Check if any source files are staged (exclude docs/config)
STAGED=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)

if [ -z "$STAGED" ]; then
    exit 0
fi

# Check if only non-source files changed
SOURCE_CHANGED=false
for file in $STAGED; do
    case "$file" in
        *.md|*.yml|*.yaml|.gitignore|.project-init|LICENSE) ;;
        *) SOURCE_CHANGED=true; break ;;
    esac
done

if [ "$SOURCE_CHANGED" = false ]; then
    exit 0
fi

# Validate CHANGELOG.md
if ! [ -f CHANGELOG.md ]; then
    echo "Warning: CHANGELOG.md not found" >&2
    exit 0
fi

if ! grep -q "^## Unreleased" CHANGELOG.md; then
    echo "Error: CHANGELOG.md missing '## Unreleased' section for source changes" >&2
    exit 1
fi

if ! grep -qP '<!--\s*bump:\s*(patch|minor|major)\s*-->' CHANGELOG.md; then
    echo "Error: CHANGELOG.md missing '<!-- bump: TYPE -->' comment" >&2
    exit 1
fi

exit 0
