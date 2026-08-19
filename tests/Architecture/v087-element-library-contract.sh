#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-element-library.js'
CSS='assets/ultimate-designer-element-library.css'
CTRL='src/Admin/EditorElementLibraryAdminController.php'
BOOT='src/Admin/IntegrationAdminBootstrap.php'
ADMIN_JS='assets/admin.js'
ADMIN_CSS='assets/admin.css'
MAIN='hangar18-manager.php'

for file in "$JS" "$CSS" "$CTRL" "$BOOT" "$ADMIN_JS" "$ADMIN_CSS" "$MAIN"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# v0.8.7 element library: additive UI over the existing element palette.
grep -F '.h18-builder-sidebar-panel[data-builder-panel="elements"]' "$JS" >/dev/null
grep -F '.h18-builder-palette-item' "$JS" >/dev/null
grep -F 'h18-element-library-search' "$JS" >/dev/null
grep -F 'h18-library-filter' "$JS" >/dev/null
grep -F 'hangar18UltimateDesignerElementFavoritesV087' "$JS" >/dev/null
grep -F 'hangar18UltimateDesignerElementRecentV087' "$JS" >/dev/null
grep -F 'const recentLimit = 8;' "$JS" >/dev/null
grep -F 'window.localStorage' "$JS" >/dev/null
grep -F "['favorites', '★ Favoritter']" "$JS" >/dev/null
grep -F "['recent', '↻ Seneste']" "$JS" >/dev/null
grep -F 'h18-library-card-description' "$JS" >/dev/null
grep -F 'h18-library-card-category' "$JS" >/dev/null
grep -F 'h18-library-drag-ghost' "$JS" >/dev/null
grep -F 'transfer.setDragImage' "$JS" >/dev/null
grep -F 'markRecent($(this))' "$JS" >/dev/null
grep -F 'h18-library-item-shell' "$CSS" >/dev/null
grep -F 'h18-library-favorite' "$CSS" >/dev/null
grep -F 'h18-library-card-button' "$CSS" >/dev/null
grep -F 'h18-library-recent-badge' "$CSS" >/dev/null
grep -F 'h18-library-drag-ghost' "$CSS" >/dev/null

# The enhancer is admin-only and only loaded on the existing Sider editor.
grep -F "\$page !== 'hangar18-pages'" "$CTRL" >/dev/null
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null
grep -F "add_action('admin_enqueue_scripts'" "$CTRL" >/dev/null
grep -F 'hangar18-ultimate-designer-element-library' "$CTRL" >/dev/null
grep -F 'EditorElementLibraryAdminController::register();' "$BOOT" >/dev/null
if grep -E "add_action\('(wp|init|template_redirect|wp_head|wp_footer)'" "$CTRL" >/dev/null; then
  echo 'FAIL: element library controller registers a frontend hook'
  exit 1
fi
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$CTRL" "$JS" >/dev/null; then
  echo 'FAIL: element library contains a persistence/public-cutover primitive'
  exit 1
fi

# UD-020 command palette already lives in the characterized legacy editor and
# must remain present while architecture extraction continues.
grep -F 'function commandPaletteBuildCommands()' "$ADMIN_JS" >/dev/null
grep -F 'function commandPaletteFilteredCommands(query)' "$ADMIN_JS" >/dev/null
grep -F "key === 'k'" "$ADMIN_JS" >/dev/null
grep -F 'h18-command-palette-open' "$MAIN" >/dev/null
grep -F '.h18-command-palette-dialog' "$ADMIN_CSS" >/dev/null

# Vehicle/Event/Gallery public code is deliberately untouched by this slice.
if git diff --name-only origin/main...HEAD | grep -E '(^|/)(Vehicle|Event|Gallery)|vehicle|event|gallery' >/dev/null; then
  echo 'FAIL: v0.8.7 editor-library slice changed a protected domain path'
  exit 1
fi

echo 'v0.8.7 visual element library + recent items + drag preview contract: PASS'
