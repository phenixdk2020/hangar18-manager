#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLegoPrimaryViewAdminController.php'
DESIGN_CTRL='src/Admin/EditorLegoDesignAdminController.php'
JS='assets/ultimate-designer-lego-primary-view-v0836.js'
CSS='assets/ultimate-designer-lego-primary-view-v0836.css'
SPEC='tests/Architecture/browser/lego-primary-view-v0836.spec.cjs'

for file in "$CTRL" "$DESIGN_CTRL" "$JS" "$CSS" "$SPEC"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

need() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

need "$DESIGN_CTRL" 'EditorLegoPrimaryViewAdminController::register();' 'primary view is not registered after LEGO design stack'
need "$CTRL" 'hangar18-ultimate-designer-lego-primary-view-v0836' 'primary view asset handle missing'
need "$CTRL" 'hangar18-ultimate-designer-lego-interaction-snapshot-v0834' 'primary view does not load after interaction snapshot layer'
need "$CTRL" 'ultimate-designer-lego-primary-view-v0836.js' 'primary view JS not enqueued'
need "$CTRL" 'ultimate-designer-lego-primary-view-v0836.css' 'primary view CSS not enqueued'

need "$JS" "const DESIGN_PANEL = '#h18-ud-lego-responsive-design-panel';" 'direct design is not routed through responsive LEGO panel'
need "$JS" "const INTERACTION_PANEL = '#h18-ud-lego-interaction-states-panel';" 'disabled state is not routed through interaction LEGO panel'
need "$JS" "event.stopImmediatePropagation();" 'legacy direct duplicate handler is not blocked for canonical controls'
need "$JS" "state[requested].InheritDesktop = false;" 'responsive direct edit cannot atomically leave inheritance'
need "$JS" "state[requested].HasOverride = true;" 'responsive direct edit does not mark canonical override'
need "$JS" "data-h18-interaction-' + requested.toLowerCase() + '-snapshot'" 'interaction snapshot preservation marker missing'
need "$JS" "field === 'RadiusPx'" 'legacy radius is not mapped to canonical radius'
need "$JS" "field === 'SectionOpacityPercent'" 'legacy opacity is not mapped to canonical design/state'
need "$JS" "canvasState() === 'disabled'" 'Disabled opacity is not separated from normal opacity'
need "$JS" "layoutFieldPattern.test(field)" 'unique layout controls are not explicitly preserved'
need "$JS" "data-h18-v0836-layout-control" 'layout ownership marker missing'
need "$JS" "data-h18-v0836-primary-view" 'primary view runtime marker missing'
need "$JS" "data-h18-lego-primary-view-runtime', '0.8.36'" 'runtime identity marker missing'

need "$SPEC" 'Desktop direct background is a canonical LEGO proxy with no legacy duplicate event' 'Desktop proxy regression missing'
need "$SPEC" 'Tablet inherited Radius becomes one responsive override checkpoint from Direct Design' 'Tablet atomic override regression missing'
need "$SPEC" 'Mobile inherited Hover background routes to responsive Hover custom as one checkpoint' 'Mobile Hover proxy regression missing'
need "$SPEC" 'Tablet Disabled opacity routes to interaction state instead of normal design opacity' 'Disabled interaction regression missing'
need "$SPEC" 'unique layout quick control remains legacy-owned and is not swallowed by LEGO bridge' 'layout preservation regression missing'
need "$SPEC" 'legacyDirect:0,responsive:1,interaction:0,legacyField:0' 'single responsive checkpoint assertion missing'
need "$SPEC" 'legacyDirect:0,responsive:0,interaction:1,legacyField:0' 'single interaction checkpoint assertion missing'

# v0.8.36 is a view/proxy only: no WordPress persistence, page mutation,
# public renderer, placement motor or second history implementation.
if grep -Ei 'update_option|add_option|delete_option|wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|admin_post_|wp_ajax_|template_redirect|wp_head|wp_footer|wp_nav_menu' "$CTRL" "$JS" >/dev/null; then
  echo 'FAIL: primary view introduced persistence/public mutation primitives'
  exit 1
fi
if grep -Ei 'undoStack|redoStack|historyEntries|editorHistoryEntries|sortable\(|LayoutParentKey|setParent\(|moveRowIntoBox|moveBoxIntoAuto' "$JS" >/dev/null; then
  echo 'FAIL: primary view introduced a history or placement motor'
  exit 1
fi

php -l "$CTRL" >/dev/null
php -l "$DESIGN_CTRL" >/dev/null
node --check "$JS"
node --check "$SPEC"
echo 'v0.8.36 LEGO primary editor view contract: PASS'
