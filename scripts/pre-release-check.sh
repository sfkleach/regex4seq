#!/usr/bin/env bash
# Run from the repository root. Optional argument: expected version (e.g. from a git tag).
set -euo pipefail

expected_version="${1:-}"

# `|| true` keeps grep's empty-result exit code from tripping `set -e` before
# we get a chance to print a useful error message.
heading=$(grep -m1 '^## \[[0-9]\+\.[0-9]\+\.[0-9]\+\]' CHANGELOG.md || true)
if [ -z "$heading" ]; then
  echo "No versioned entry found in CHANGELOG.md - top entry must be [X.Y.Z] not Unreleased"
  exit 1
fi

if ! echo "$heading" | grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
  echo "CHANGELOG top entry must include a date (YYYY-MM-DD)"
  echo "Found: $heading"
  exit 1
fi

changelog_version=$(echo "$heading" | grep -oE '\[[0-9]+\.[0-9]+\.[0-9]+\]' | tr -d '[]' || true)
if [ -z "$changelog_version" ]; then
  echo "Could not extract version from CHANGELOG heading: $heading"
  exit 1
fi

pyproject_line=$(grep -m1 '^version = ' pyproject.toml || true)
if [ -z "$pyproject_line" ]; then
  echo "No 'version = ' line found in pyproject.toml"
  exit 1
fi

pyproject_version=$(echo "$pyproject_line" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || true)
if [ -z "$pyproject_version" ]; then
  echo "Could not extract version from pyproject.toml line: $pyproject_line"
  exit 1
fi

if [ "$changelog_version" != "$pyproject_version" ]; then
  echo "CHANGELOG version [$changelog_version] does not match pyproject.toml version [$pyproject_version]"
  exit 1
fi

if [ -n "$expected_version" ] && [ "$changelog_version" != "$expected_version" ]; then
  echo "Version [$changelog_version] does not match expected version [$expected_version]"
  exit 1
fi

echo "Version checks passed: $changelog_version"
