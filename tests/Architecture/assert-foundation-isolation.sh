#!/usr/bin/env bash
set -euo pipefail

base_ref="${1:-origin/main}"
allowed='^(src/|tests/Architecture/|assets/(site-builder-runtime|interaction-runtime|ultimate-designer-admin|ultimate-designer-menu-admin|ultimate-designer-menu-pages|ultimate-designer-side-health|ultimate-designer-asset-admin|ultimate-designer-portability|ultimate-designer-permissions|ultimate-designer-ai|ultimate-designer-qa|ultimate-designer-conversion|ultimate-designer-layout-tools|ultimate-designer-box-tools|ultimate-designer-nesting-tools|ultimate-designer-box-content-layout|ultimate-designer-visual-composition|ultimate-designer-table-appearance|ultimate-designer-element-library|ultimate-designer-workspace-widgets|ultimate-designer-unsaved-preview|ultimate-designer-lego-spacing-v0830|ultimate-designer-lego-spacing-v0831|ultimate-designer-lego-design-v0832|ultimate-designer-lego-design-event-guard-v0832|ultimate-designer-history-v0817|ultimate-designer-history-v0818|ultimate-designer-history-preload-v0820|ultimate-designer-history-preload-v0821|ultimate-designer-history-post-restore-v0822|ultimate-designer-history-content-v0823)\.(js|css)$|docs/(architecture-|ud-|v085-|v0816-|v0817-|v0818-|v0830-|v0831-|v0832-|b2-)[^/]+\.md$|docs/ultimate-designer-onboarding\.md$|docs/integration-backlog-after-ud120\.md$|\.github/workflows/(architecture-foundation-qa|editor-runtime-fast-qa|event-auto-archive-qa|b1-backup-restore-qa|b2-site-backup-qa|lego-spacing-qa)\.yml$)'
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
