#!/usr/bin/env bash
set -euo pipefail

base_ref="${1:-origin/main}"
allowed='^(src/|tests/Architecture/|assets/(site-builder-runtime|interaction-runtime|ultimate-designer-admin|ultimate-designer-menu-admin|ultimate-designer-menu-pages|ultimate-designer-side-health|ultimate-designer-asset-admin|ultimate-designer-portability|ultimate-designer-permissions|ultimate-designer-ai|ultimate-designer-qa|ultimate-designer-conversion|ultimate-designer-layout-tools)\.(js|css)$|docs/(architecture-|ud-|v085-)[^/]+\.md$|docs/ultimate-designer-onboarding\.md$|docs/integration-backlog-after-ud120\.md$|\.github/workflows/architecture-foundation-qa\.yml$)'
changed="$(git diff --name-only "${base_ref}...HEAD")"
violations="$(printf '%s\n' "$changed" | grep -Ev "$allowed" || true)"
if [[ -n "$violations" ]]; then
  echo "Architecture isolation FAILED."
  echo "Existing legacy/public runtime files were changed during a non-invasive architecture phase:"
  printf '%s\n' "$violations"
  exit 1
fi
echo "Architecture isolation: PASS"
echo "Existing legacy/public runtime files remain untouched; extracted services, tests/docs and dedicated Ultimate Designer admin assets are allowed."
