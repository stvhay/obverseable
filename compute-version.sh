#!/usr/bin/env bash
# Thin wrapper around compute_version.py
# Usage:
#   ./compute-version.sh [--ci] [--update] [--check]
#
# Requires Python 3.11+ (for tomllib)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check Python availability
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but not found" >&2
    exit 1
fi

# Check Python version (need 3.11+ for tomllib)
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    echo "Error: Python 3.11+ required (found $PYTHON_VERSION)" >&2
    exit 1
fi

exec python3 "$SCRIPT_DIR/compute_version.py" "$@"
