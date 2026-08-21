#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-canvas-panel-collapse-v0839.js'
CSS='assets/ultimate-designer-canvas-panel-collapse-v0839.css'
CTRL='src/Admin/EditorCanvasPanelCollapseAdminController.php'
SPACING_CTRL='src/Admin/EditorLegoSpacingAdminController.php'
SPEC='tests/Architecture/browser/collapsible-canvas-panels-v0839.spec.cjs'

for file in "$JS" "$CSS" "$CTRL" "$SPACING_CTRL" "$SPEC"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

grep -F "hangar18CanvasPanelCollapseV0839" "$JS" >/dev/null
grep -F ".h18-canvas-image-tools" "$JS" >/dev/null
grep -F ".h18-canvas-direct-controls" "$JS" >/dev/null
grep -F "h18-canvas-panel-collapse-toggle" "$JS" >/dev/null
grep -F "MutationObserver" "$JS" >/dev/null
grep -F "data-h18-canvas-panel-collapsed" "$JS" >/dev/null
grep -F "h18-canvas-panel-collapsed" "$CSS" >/dev/null
grep -F "EditorCanvasPanelCollapseAdminController::register();" "$SPACING_CTRL" >/dev/null
grep -F "ultimate-designer-canvas-panel-collapse-v0839.js" "$CTRL" >/dev/null
grep -F "ultimate-designer-canvas-panel-collapse-v0839.css" "$CTRL" >/dev/null
grep -F "\$page !== 'hangar18-pages'" "$CTRL" >/dev/null
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null

# Browser-local UI state is allowed, but no page/save/history/placement/public mutation motor may be added.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_|wp_ajax_|setParent\(|sortable\(|undoStack|redoStack|editorHistory' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.39 collapse UX introduced a page/history/placement mutation primitive'
  exit 1
fi

node --check "$JS"
node --check "$SPEC"
php -l "$CTRL" >/dev/null

echo 'v0.8.39 collapsible canvas panels contract: PASS'
