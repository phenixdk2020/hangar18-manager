#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-visual-composition.js'
CSS='assets/ultimate-designer-visual-composition.css'
CTRL='src/Admin/EditorLayoutToolsAdminController.php'
NEST='assets/ultimate-designer-nesting-tools.js'

for file in "$JS" "$CSS" "$CTRL" "$NEST"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Keep the historical v0.8.9 addon syntactically valid/documented.
grep -F "const AUTO_LABEL = 'Auto-kasser';" "$JS" >/dev/null
grep -F "const BOX_LABEL = 'Kasse';" "$JS" >/dev/null
grep -F 'function parentKey($row)' "$JS" >/dev/null
grep -F 'function setParent($row, key)' "$JS" >/dev/null
grep -F 'h18-ud-vc-source-hidden' "$JS" >/dev/null
grep -F 'function renderBoxComposition($box)' "$JS" >/dev/null
grep -F 'function renderAutoComposition($autoRow)' "$JS" >/dev/null
grep -F 'h18-ud-vc-side-drop-zone' "$JS" >/dev/null
grep -F '.h18-page-section-row.h18-ud-vc-source-hidden{display:none!important}' "$CSS" >/dev/null

# It is no longer an executable placement authority in the editor.
if grep -F "'hangar18-ultimate-designer-visual-composition'" "$CTRL" >/dev/null || grep -F 'ultimate-designer-visual-composition.js' "$CTRL" >/dev/null; then
  echo 'FAIL: historical v0.8.9 visual composition is still enqueued'
  exit 1
fi
grep -F 'data-h18-v0813-kasse-runtime' "$NEST" >/dev/null
grep -F 'function moveRowIntoBox($row, $box)' "$NEST" >/dev/null

if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: visual composition introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
node --check "$NEST"
echo 'v0.8.9 visual box composition historical contract: PASS'
