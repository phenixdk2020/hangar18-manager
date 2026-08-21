#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-lego-resize-v0841.js'
CSS='assets/ultimate-designer-lego-resize-v0841.css'
CTRL='src/Admin/EditorLegoResizeAdminController.php'
MODEL='src/Editor/LegoLayoutSpanModel.php'
SPACING_CTRL='src/Admin/EditorLegoSpacingAdminController.php'
SPEC='tests/Architecture/browser/lego-resize-v0841.spec.cjs'
SMOKE='tests/Architecture/v0841-lego-resize-model-smoke.php'

for file in "$JS" "$CSS" "$CTRL" "$MODEL" "$SPACING_CTRL" "$SPEC" "$SMOKE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

# Canonical 12-column overlay: no parent/placement store.
require_contains "$MODEL" 'public const COLUMN_COUNT = 12;' '12-column model missing'
require_contains "$MODEL" "'Span' => \$desktopSpan" 'Desktop span state missing'
require_contains "$MODEL" "'InheritDesktop' => true" 'responsive inheritance missing'
require_contains "$CTRL" "hangar18_ultimate_designer_lego_layout_span_v1" 'admin-only span option missing'
require_contains "$CTRL" "admin_post_h18_save_page_editor" 'existing page-save bridge not reused'
require_contains "$SPACING_CTRL" 'EditorLegoResizeAdminController::register();' 'resize controller not registered'

# Visual resize must operate only on the existing Auto-kasser proxy and section keys.
require_contains "$JS" "const AUTO_LABEL = 'Auto-kasser';" 'Auto-kasser compatibility gate missing'
require_contains "$JS" 'parentKey($(this)) === key' 'LayoutParentKey child authority missing'
require_contains "$JS" 'h18-v0811-auto-grid' 'existing Auto-kasser grid proxy not reused'
require_contains "$JS" 'h18-v0841-resize-handle' 'resize handle missing'
require_contains "$JS" 'window.__h18HistoryAtomicV0840' 'existing atomic history transaction not reused'
require_contains "$JS" 'writeDesktopSpan(drag.$leftRow, drag.currentLeft, true);' 'left neighbor span commit missing'
require_contains "$JS" 'writeDesktopSpan(drag.$rightRow, drag.currentRight, true);' 'right neighbor span commit missing'
require_contains "$JS" 'h18_lego_layout_span[' 'save payload missing'
require_contains "$CSS" 'grid-template-columns:repeat(12,minmax(0,1fr))!important' '12-column visual grid missing'
require_contains "$CSS" 'grid-column:span var(--h18-v0841-span,12)!important' 'tile span CSS missing'

# Browser proof: Auto is non-mutating, resize is atomic, Undo/Redo and min-span work.
require_contains "$SPEC" 'default to 6/6 without persisted mutation' '6/6 Auto regression missing'
require_contains "$SPEC" 'changes 6/6 to 8/4 as one Undo Redo checkpoint' '8/4 history regression missing'
require_contains "$SPEC" 'clamps each neighbor to at least one of twelve columns' 'minimum span regression missing'

# LEGO-032 must not become a public renderer, drag/drop motor or second history stack.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|admin_post_.*(activate|cutover|publish)|sortable\(|setParent\(|LayoutParentKey.*=' "$JS" "$CTRL" "$MODEL" >/dev/null; then
  echo 'FAIL: LEGO-032 introduced a public/placement mutation primitive'
  exit 1
fi
if grep -Ei 'undoStack|redoStack|historyEntries|editorHistoryEntries' "$JS" "$CTRL" "$MODEL" >/dev/null; then
  echo 'FAIL: LEGO-032 introduced a second history stack'
  exit 1
fi

node --check "$JS"
node --check "$SPEC"
php -l "$CTRL" >/dev/null
php -l "$MODEL" >/dev/null
php "$SMOKE"

echo 'v0.8.41 LEGO visual resize contract: PASS'
