#!/usr/bin/env bash
set -euo pipefail

MODEL='src/Editor/LegoSpacingModel.php'
CTRL='src/Admin/EditorLegoSpacingAdminController.php'
COORD='src/Backup/SiteBackupRestoreCoordinator.php'
JS='assets/ultimate-designer-lego-spacing-v0831.js'
CSS='assets/ultimate-designer-lego-spacing-v0831.css'

for file in "$MODEL" "$CTRL" "$COORD" "$JS" "$CSS"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1" needle="$2" label="$3"
  if ! grep -F -- "$needle" "$file" >/dev/null; then
    echo "FAIL: $label"
    echo "  missing: $needle"
    exit 1
  fi
}

require_contains "$MODEL" 'public const SCHEMA_VERSION = 2;' 'responsive spacing schema version is not 2'
require_contains "$MODEL" 'public const TABLET_MAX' 'Tablet limit is missing from canonical model'
require_contains "$MODEL" "'InheritDesktop'" 'responsive inheritance flag is missing from canonical model'
require_contains "$MODEL" 'public static function effective' 'effective inherited device resolver is missing'
require_contains "$MODEL" "'LayoutGapPx'" 'legacy desktop gap migration is missing'
require_contains "$MODEL" "'MobileLayoutGapPx'" 'legacy mobile gap migration is missing'

require_contains "$CTRL" 'assets/ultimate-designer-lego-spacing-v0831.js' 'v0.8.31 runtime is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-spacing-v0831.css' 'v0.8.31 styles are not enqueued'
require_contains "$CTRL" "'H18LegoSpacingV0831'" 'v0.8.31 localized configuration is missing'
require_contains "$CTRL" "'tablet' => LegoSpacingModel::TABLET_MAX" 'Tablet limit is not exposed to runtime'
require_contains "$CTRL" "hangar18_ultimate_designer_lego_spacing_v2" 'canonical LEGO option unexpectedly changed'
require_contains "$CTRL" "hangar18-ultimate-designer-history-content-v0823" 'existing history owner is not an explicit dependency'

require_contains "$JS" "const STATE_CLASS = 'h18-lego-spacing-state-json';" 'canonical hidden row state is missing'
require_contains "$JS" 'SchemaVersion: 2' 'runtime does not normalize to schema 2'
require_contains "$JS" 'Tablet:' 'Tablet runtime state is missing'
require_contains "$JS" 'InheritDesktop: true' 'Tablet inheritance default is missing'
require_contains "$JS" 'InheritDesktop: false' 'Mobile backwards-compatible override default is missing'
require_contains "$JS" "data-h18-lego-inherit-device" 'Inspector inheritance toggle is missing'
require_contains "$JS" "Tablet.Margin.X" 'Tablet X/Y control path support is missing'
require_contains "$JS" "effectiveDevice(state, 'Tablet')" 'Tablet effective state is not applied to preview'
require_contains "$JS" "setDeviceVars(node, 'tablet-'" 'Tablet CSS variables are not materialized'
require_contains "$JS" "data-h18-lego-spacing-runtime', '0.8.31'" 'runtime identity is missing'
require_contains "$JS" "\$field.trigger('input');" 'Inspector edits are not sent through the existing history checkpoint'

require_contains "$CSS" 'data-canvas-device="tablet"' 'Tablet preview selector is missing'
require_contains "$CSS" '--h18-lego-tablet-margin-x' 'Tablet margin variable is missing'
require_contains "$CSS" '--h18-lego-tablet-gap-x' 'Tablet X gap variable is missing'
require_contains "$CSS" '--h18-lego-tablet-gap-y' 'Tablet Y gap variable is missing'

require_contains "$COORD" "LEGO_SPACING_OPTION = 'hangar18_ultimate_designer_lego_spacing_v2'" 'B2 coordinator does not know canonical LEGO option'
require_contains "$COORD" 'restoreSelectiveLegoSpacing' 'selective LEGO restore hook is missing'
require_contains "$COORD" "\$current[\$pageSlug] = \$source[\$pageSlug];" 'selective restore does not scope replacement to selected page slug'
require_contains "$COORD" "\$result['LegoSpacingRestored']" 'selective restore result does not report LEGO state handling'

# v0.8.31 must still use the existing history motor. No parallel history stack/Undo commands.
if grep -Ei 'editorHistoryEntries|historyEntries|undoStack|redoStack|addEventListener\([^,]*(undo|redo)|\.on\([^,]*(undo|redo)' "$JS" >/dev/null; then
  echo 'FAIL: responsive LEGO spacing introduced a second history/Undo runtime'
  exit 1
fi

# Editor foundation remains admin-only; no public renderer/post mutations in model/controller/runtime.
if grep -Ei 'wp_update_post|wp_insert_post|set_post_thumbnail|update_post_meta|delete_post_meta|template_redirect|wp_head|wp_footer|wp_nav_menu' "$MODEL" "$CTRL" "$JS" >/dev/null; then
  echo 'FAIL: responsive LEGO spacing introduced public/post mutation primitives'
  exit 1
fi

php tests/Architecture/v0831-lego-responsive-spacing-smoke.php
php -l "$MODEL" >/dev/null
php -l "$CTRL" >/dev/null
php -l "$COORD" >/dev/null
node --check "$JS"

echo 'v0.8.31 LEGO responsive spacing + selective B2 restore contract: PASS'
