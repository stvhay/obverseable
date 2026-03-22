#!/usr/bin/env python3
"""Version management for Obverseable.

Reads the current version from pyproject.toml and computes the next version
based on the bump type specified in CHANGELOG.md.

Usage:
    python3 compute_version.py              # Print current version
    python3 compute_version.py --check      # Validate changelog has bump comment
    python3 compute_version.py --ci         # Print next version from changelog bump type
    python3 compute_version.py --ci --update # Bump version in pyproject.toml and rewrite changelog
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    print("Error: Python 3.11+ required (tomllib)", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"

BUMP_COMMENT_RE = re.compile(r"<!--\s*bump:\s*(patch|minor|major)\s*-->")
UNRELEASED_RE = re.compile(r"^## Unreleased", re.MULTILINE)
VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)


def read_version() -> str:
    """Read version from pyproject.toml."""
    if not PYPROJECT.exists():
        return "0.0.0"
    with open(PYPROJECT, "rb") as f:
        data = tomllib.load(f)
    return data.get("project", {}).get("version", "0.0.0")


def read_bump_type() -> str | None:
    """Read bump type from <!-- bump: TYPE --> comment in CHANGELOG.md."""
    if not CHANGELOG.exists():
        return None
    text = CHANGELOG.read_text()
    match = BUMP_COMMENT_RE.search(text)
    return match.group(1) if match else None


def compute_next_version(current: str, bump: str) -> str:
    """Compute the next version given a bump type."""
    parts = current.split(".")
    if len(parts) != 3:
        print(f"Error: version '{current}' is not semver", file=sys.stderr)
        sys.exit(1)
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    if bump == "major":
        return f"{major + 1}.0.0"
    elif bump == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def update_pyproject(new_version: str) -> None:
    """Update version in pyproject.toml using regex replacement."""
    if not PYPROJECT.exists():
        print("Error: pyproject.toml not found", file=sys.stderr)
        sys.exit(1)
    text = PYPROJECT.read_text()
    new_text, count = VERSION_RE.subn(f'version = "{new_version}"', text)
    if count == 0:
        print("Error: could not find version field in pyproject.toml", file=sys.stderr)
        sys.exit(1)
    PYPROJECT.write_text(new_text)


def update_changelog(new_version: str) -> None:
    """Rewrite '## Unreleased' to '## vX.Y.Z' in CHANGELOG.md."""
    text = CHANGELOG.read_text()
    from datetime import datetime, timezone

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_text = UNRELEASED_RE.sub(f"## v{new_version} ({date_str})", text, count=1)
    CHANGELOG.write_text(new_text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute or bump project version")
    parser.add_argument("--ci", action="store_true", help="Compute next version from changelog bump type")
    parser.add_argument("--update", action="store_true", help="Write new version to pyproject.toml and changelog")
    parser.add_argument("--check", action="store_true", help="Validate changelog has bump comment")
    args = parser.parse_args()

    current = read_version()

    if args.check:
        bump = read_bump_type()
        if not bump:
            print("Error: CHANGELOG.md missing <!-- bump: TYPE --> comment", file=sys.stderr)
            sys.exit(1)
        if not UNRELEASED_RE.search(CHANGELOG.read_text()):
            print("Error: CHANGELOG.md missing ## Unreleased section", file=sys.stderr)
            sys.exit(1)
        print(f"OK: bump type is '{bump}', current version is {current}")
        sys.exit(0)

    if args.ci:
        bump = read_bump_type()
        if not bump:
            print("Error: no bump type found in CHANGELOG.md", file=sys.stderr)
            sys.exit(1)
        next_version = compute_next_version(current, bump)
        if args.update:
            update_pyproject(next_version)
            update_changelog(next_version)
            print(f"Updated: {current} -> {next_version}")
        else:
            print(next_version)
    else:
        print(current)


if __name__ == "__main__":
    main()
