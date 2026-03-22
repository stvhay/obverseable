#!/usr/bin/env bash
# Hook: validates that when CHANGELOG.md has an ## Unreleased section,
# it also has a <!-- bump: TYPE --> comment.
#
# Intended to run as a Claude Code pre-commit hook.

set -euo pipefail

if ! [ -f CHANGELOG.md ]; then
    exit 0
fi

if grep -q "^## Unreleased" CHANGELOG.md; then
    if ! grep -qP '<!--\s*bump:\s*(patch|minor|major)\s*-->' CHANGELOG.md; then
        echo "Error: CHANGELOG.md has '## Unreleased' but missing '<!-- bump: TYPE -->' comment" >&2
        exit 1
    fi
fi

exit 0
