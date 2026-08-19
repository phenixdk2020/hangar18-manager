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

# A drop on the visible Auto-kasser tile must map back to the hidden source Kasse.
grep -F "element.closest('.h18-v0811-auto-box[data-h18-v0811-box]')" "$JS" >/dev/null
grep -F "rowByKey(String(autoTile.getAttribute('data-h18-v0811-box') || ''))" "$JS" >/dev/null

# Existing-row sortable hit-testing must use the visible Auto-kasser tile/drop-zone,
# because the source Kasse row is intentionally hidden while nested in Auto-kasser.
grep -F "$('.h18-v0811-auto-box[data-h18-v0811-box]').each(function ()" "$JS" >/dev/null
grep -F "const zone = $tile.find('.h18-ud-box-drop-zone').get(0) || this;" "$JS" >/dev/null

# Visual target feedback must also be applied to the visible Auto-kasser tile.
grep -F "$('.h18-v0811-auto-box').removeClass('h18-ud-nesting-drop-target')" "$JS" >/dev/null
grep -F "$('.h18-v0811-auto-box[data-h18-v0811-box=\"' + key + '\"]')" "$JS" >/dev/null

# Existing hierarchy/persistence model remains unchanged.
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F 'function moveRowIntoBox($row, $box)' "$JS" >/dev/null
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" >/dev/null; then
  echo 'FAIL: Auto-kasse drop hotfix introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.12 Auto-kasse child preview/drop contract: PASS'
