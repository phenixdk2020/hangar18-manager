#!/usr/bin/env bash
set -euo pipefail

base_ref="${1:-origin/main}"

allowed='^(src/|tests/Architecture/|assets/site-builder-runtime\.(js|css)$|docs/(architecture-|ud-)[^/]+\.md$|\.github/workflows/architecture-foundation-qa\.yml$)'
changed="$(git diff --name-only "${base_ref}...HEAD")"

violations="$(printf '%s\n' "$changed" | grep -Ev "$allowed" || true)"

if [[ -n "$violations" ]]; then
  echo "Architecture isolation FAILED."
  echo "Existing v0.5.30 runtime files were changed during a non-invasive architecture phase:"
  printf '%s\n' "$violations"
  exit 1
fi

echo "Architecture isolation: PASS"
echo "Existing v0.5.30 runtime files remain untouched; passive Site Builder runtime assets are allowed but not enqueued."
