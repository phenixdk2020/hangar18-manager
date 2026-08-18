#!/usr/bin/env bash
set -euo pipefail

# v0.7.3 final regression contract.
# Ordinary section heading is explicitly optional.
grep -F "Overskrift (valgfri)" hangar18-manager.php >/dev/null
if grep -E 'class="h18-section-title-input"[^>]*required' hangar18-manager.php >/dev/null; then
  echo 'FAIL: ordinary section heading is still required'
  exit 1
fi

# Natural Enter/newline is preserved in editor preview and frontend uses wpautop.
grep -F 'Enter = linjeskift.' hangar18-manager.php >/dev/null
grep -F '.h18-pages-admin .h18-canvas-preview-text{white-space:pre-line}' assets/admin.css >/dev/null
grep -F 'return wpautop(wp_kses_post((string) $content));' hangar18-manager.php >/dev/null

# Manual save note must never be toggled back to required by the old WhatIf handler.
if grep -F 'const required = !$pageWhatIf.is('"'"':checked'"'"');' assets/admin.js >/dev/null; then
  echo 'FAIL: legacy save-note required toggle still exists'
  exit 1
fi
grep -F ".prop('required', false).removeAttr('required').attr('aria-required', 'false')" assets/admin.js >/dev/null

echo 'v0.7.3 heading/line-break contract: PASS'
