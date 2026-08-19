#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-nesting-tools.js'
test -f "$JS" || { echo "FAIL: missing $JS"; exit 1; }

# Auto-kasser must render the Kasse composition, including its inside drop-zone,
# instead of stripping the Kasse contents from the visible tile.
grep -F 'function clonePreview($row, preserveBoxContents)' "$JS" >/dev/null
grep -F 'if (preserveBoxContents)' "$JS" >/dev/null
grep -F 'const $clone = clonePreview($box, true);' "$JS" >/dev/null
grep -F "'data-h18-v0812-auto-kasse-drop': '1'" "$JS" >/dev/null

# A drop on a visible Auto-kasse or nested-Kasse proxy maps back to its hidden source Kasse.
grep -F '.h18-v0811-auto-box[data-h18-v0811-box],.h18-v0813-nested-box[data-h18-v0811-box]' "$JS" >/dev/null
grep -F "rowByKey(String(proxy.getAttribute('data-h18-v0811-box') || ''))" "$JS" >/dev/null

# Existing-row sortable hit-testing uses visible proxy/drop-zones because nested source rows stay hidden.
grep -F 'const $proxy = $(this);' "$JS" >/dev/null
grep -F 'const zone = $proxy.find' "$JS" >/dev/null
grep -F 'h18-ud-box-drop-zone[data-h18-v0813-box-drop]' "$JS" >/dev/null

# Visual target feedback is applied to visible proxies.
grep -F '.h18-v0811-auto-box,.h18-v0813-nested-box' "$JS" >/dev/null
grep -F "removeClass('h18-ud-nesting-drop-target')" "$JS" >/dev/null
grep -F 'h18-v0813-nested-box[data-h18-v0811-box=' "$JS" >/dev/null

# Existing hierarchy/persistence model remains unchanged.
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F 'function moveRowIntoBox($row, $box)' "$JS" >/dev/null
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" >/dev/null; then
  echo 'FAIL: Auto-kasse drop hotfix introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.12+ Auto-kasse child preview/drop contract: PASS'
