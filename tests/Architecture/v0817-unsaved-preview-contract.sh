#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-unsaved-preview.js'
CSS='assets/ultimate-designer-unsaved-preview.css'
CTRL='src/Admin/EditorUnsavedPreviewAdminController.php'
BOOT='src/Admin/IntegrationAdminBootstrap.php'

for file in "$JS" "$CSS" "$CTRL" "$BOOT"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Preview is sourced from the current live editor DOM, not from the saved public page.
grep -F "const \$form = \$('#h18-page-editor-form').first();" "$JS" >/dev/null
grep -F "const \$sections = \$('#h18-page-sections-sortable').first();" "$JS" >/dev/null
grep -F 'topLevelRows()' "$JS" >/dev/null
grep -F "\$row.children('.h18-canvas-preview').first()" "$JS" >/dev/null
grep -F 'clone(false, false)' "$JS" >/dev/null

# Explicit unsaved preview action and device modes.
grep -F "text: 'Forhåndsvis side'" "$JS" >/dev/null
grep -F "text: 'Ugemt forhåndsvisning'" "$JS" >/dev/null
grep -F "'data-h18-preview-device': 'desktop'" "$JS" >/dev/null
grep -F "'data-h18-preview-device': 'tablet'" "$JS" >/dev/null
grep -F "'data-h18-preview-device': 'mobile'" "$JS" >/dev/null
grep -F '.h18-unsaved-preview-viewport.is-tablet{width:768px' "$CSS" >/dev/null
grep -F '.h18-unsaved-preview-viewport.is-mobile{width:390px' "$CSS" >/dev/null

# Editor chrome is stripped from the cloned preview.
grep -F '.h18-v0811-runtime-badge' "$JS" >/dev/null
grep -F '.h18-v0814-auto-drop-zone' "$JS" >/dev/null
grep -F '.h18-page-section-actions' "$JS" >/dev/null
grep -F "\$clone.find('button').remove();" "$JS" >/dev/null

# Accessibility and close/focus behavior.
grep -F "role: 'dialog'" "$JS" >/dev/null
grep -F "'aria-modal': 'true'" "$JS" >/dev/null
grep -F "event.key === 'Escape'" "$JS" >/dev/null
grep -F 'opener.focus();' "$JS" >/dev/null
grep -F '@media(prefers-reduced-motion:reduce)' "$CSS" >/dev/null

# Admin-only registration/enqueue.
grep -F 'EditorUnsavedPreviewAdminController::register();' "$BOOT" >/dev/null
grep -F "\$page !== 'hangar18-pages'" "$CTRL" >/dev/null
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null
grep -F 'hangar18-ultimate-designer-unsaved-preview' "$CTRL" >/dev/null

# This feature must have no executable persistence/network/public mutation path.
# Match call syntax/WordPress hook identifiers instead of prose in comments.
if grep -Ei '\$\.ajax\s*\(|jQuery\.ajax\s*\(|fetch\s*\(|new[[:space:]]+XMLHttpRequest|wp_update_post\s*\(|wp_insert_post\s*\(|update_post_meta\s*\(|delete_post_meta\s*\(|update_option\s*\(|delete_option\s*\(|admin_post_[a-z0-9_]+|wp_ajax_[a-z0-9_]+|\.submit\s*\(' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: unsaved preview introduced a network/persistence primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.17 unsaved preview contract: PASS'
