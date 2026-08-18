#!/usr/bin/env bash
set -euo pipefail

base_ref="${1:-origin/main}"

allowed='^(src/|tests/Architecture/|docs/architecture-migration\.md$|\.github/workflows/architecture-foundation-qa\.yml$)'
changed="$(git diff --name-only "${base_ref}...HEAD")"

violations="$(printf '%s\n' "$changed" | grep -Ev "$allowed" || true)"

if [[ -n "$violations" ]]; then
  echo "Architecture foundation isolation FAILED."
  echo "Existing v0.5.30 runtime files were changed during the non-invasive foundation phase:"
  printf '%s\n' "$violations"
  exit 1
fi

echo "Architecture foundation isolation: PASS"
echo "Existing v0.5.30 runtime files remain untouched."
