#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-workspace-widgets.js'
CSS='assets/ultimate-designer-workspace-widgets.css'
CTRL='src/Admin/EditorElementLibraryAdminController.php'

for file in "$JS" "$CSS" "$CTRL"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Both sides are independently collapsible and browser-local.
grep -F "const STORAGE_KEY = 'hangar18UltimateDesignerWorkspaceWidgetsV0814';" "$JS" >/dev/null
grep -F "const desktopQuery = window.matchMedia('(min-width: 1181px)');" "$JS" >/dev/null
grep -F "applyPanelState('left'" "$JS" >/dev/null
grep -F "applyPanelState('right'" "$JS" >/dev/null
grep -F 'window.localStorage.setItem' "$JS" >/dev/null
grep -F 'h18-workspace-left-collapsed' "$JS" >/dev/null
grep -F 'h18-workspace-right-collapsed' "$JS" >/dev/null
grep -F "'aria-expanded': 'true'" "$JS" >/dev/null
grep -F "'aria-expanded': 'false'" "$JS" >/dev/null

# Collapsed rails remain available and return width to the canvas.
grep -F 'data-h18-workspace-expand' "$JS" >/dev/null
grep -F 'h18-workspace-widget-rail' "$CSS" >/dev/null
grep -F '.h18-visual-builder.h18-workspace-left-collapsed{--h18-workspace-left:44px}' "$CSS" >/dev/null
grep -F '.h18-visual-builder.h18-workspace-right-collapsed{--h18-workspace-right:44px}' "$CSS" >/dev/null
grep -F 'grid-template-columns:var(--h18-workspace-left) var(--h18-workspace-center) var(--h18-workspace-right)!important' "$CSS" >/dev/null

# Tablet/mobile keeps the existing stacked editor rather than forcing rails.
grep -F '@media(max-width:1180px)' "$CSS" >/dev/null
grep -F '.h18-workspace-widget-rail{display:none!important}' "$CSS" >/dev/null
grep -F '@media(prefers-reduced-motion:reduce)' "$CSS" >/dev/null

# Admin-only enqueue; no page/public persistence primitive.
grep -F 'hangar18-ultimate-designer-workspace-widgets' "$CTRL" >/dev/null
grep -F "\$page !== 'hangar18-pages'" "$CTRL" >/dev/null
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: workspace widgets introduced page/public persistence primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.14 collapsible workspace widgets contract: PASS'
