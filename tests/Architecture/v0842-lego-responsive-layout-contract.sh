#!/usr/bin/env bash
set -euo pipefail

BASE_JS='assets/ultimate-designer-lego-resize-v0841.js'
JS='assets/ultimate-designer-lego-responsive-layout-v0842.js'
CSS='assets/ultimate-designer-lego-responsive-layout-v0842.css'
CTRL='src/Admin/EditorLegoResizeAdminController.php'
MODEL='src/Editor/LegoLayoutSpanModel.php'
SPEC='tests/Architecture/browser/lego-responsive-layout-v0842.spec.cjs'
SMOKE='tests/Architecture/v0842-lego-responsive-layout-model-smoke.php'

for file in "$BASE_JS" "$JS" "$CSS" "$CTRL" "$MODEL" "$SPEC" "$SMOKE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

# Same canonical state/store and same placement/history owners.
require_contains "$MODEL" 'public const SCHEMA_VERSION = 2;' 'responsive span schema v2 missing'
require_contains "$MODEL" 'public static function setInheritance' 'reversible inheritance transition missing'
require_contains "$MODEL" 'public static function setSpan' 'responsive explicit span transition missing'
require_contains "$MODEL" "'HasOverride' => \$hasOverride" 'override snapshot marker missing'
require_contains "$CTRL" "hangar18_ultimate_designer_lego_layout_span_v1" 'same span option not reused'
require_contains "$CTRL" 'hangar18-ultimate-designer-lego-responsive-layout-v0842' 'responsive runtime not enqueued'
require_contains "$BASE_JS" 'writeStateForKey:' 'canonical span write API missing from base runtime'
require_contains "$BASE_JS" 'rowKeysForAuto:' 'canonical Auto-kasser child API missing from base runtime'

# Tablet/Mobile are overlays on the existing Auto-kasser 12-column visual grid.
require_contains "$JS" "if (raw === 'tablet') { return 'Tablet'; }" 'Tablet device bridge missing'
require_contains "$JS" "if (raw === 'mobile') { return 'Mobile'; }" 'Mobile device bridge missing'
require_contains "$JS" 'window.__h18LegoResizeV0841' 'v0.8.41 canonical runtime not reused'
require_contains "$JS" 'window.__h18HistoryAtomicV0840' 'existing atomic history owner not reused'
require_contains "$JS" 'responsiveWrite(current.leftKey, current.device, current.currentLeft, true);' 'responsive left neighbor write missing'
require_contains "$JS" 'responsiveWrite(current.rightKey, current.device, current.currentRight, true);' 'responsive right neighbor write missing'
require_contains "$JS" 'entry.InheritDesktop = true;' 'inherit Desktop toggle missing'
require_contains "$JS" 'entry.HasOverride = true;' 'override snapshot activation missing'
require_contains "$JS" 'data-h18-v0842-responsive-layout' 'responsive Auto-kasser decoration missing'
require_contains "$CSS" '[data-canvas-device="tablet"] .h18-v0841-resize-handle' 'Tablet resize handle enable missing'
require_contains "$CSS" '[data-canvas-device="mobile"] .h18-v0841-resize-handle' 'Mobile resize handle enable missing'
require_contains "$CSS" '.h18-v0842-inherit-toggle' 'inheritance control styling missing'

# Browser proof must cover inheritance, atomic responsive resize, device isolation and snapshots.
require_contains "$SPEC" 'initially inherit the Desktop 6/6 Auto layout' 'initial inheritance regression missing'
require_contains "$SPEC" 'Tablet resize creates only Tablet overrides as one Undo Redo checkpoint' 'Tablet atomic resize regression missing'
require_contains "$SPEC" 'Desktop Tablet and Mobile layouts remain independent' 'device isolation regression missing'
require_contains "$SPEC" 'Arv Desktop preserves and restores the responsive override snapshot' 'reversible snapshot regression missing'

# LEGO-033 must not create a second parent model, history stack or public renderer.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|admin_post_.*(activate|cutover|publish)|sortable\(|setParent\(|LayoutParentKey.*=' "$JS" "$CTRL" "$MODEL" >/dev/null; then
  echo 'FAIL: LEGO-033 introduced a public/placement mutation primitive'
  exit 1
fi
if grep -Ei 'undoStack|redoStack|historyEntries|editorHistoryEntries' "$JS" "$CTRL" "$MODEL" >/dev/null; then
  echo 'FAIL: LEGO-033 introduced a second history stack'
  exit 1
fi

node --check "$BASE_JS"
node --check "$JS"
node --check "$SPEC"
php -l "$CTRL" >/dev/null
php -l "$MODEL" >/dev/null
php "$SMOKE"

echo 'v0.8.42 LEGO responsive layout contract: PASS'
