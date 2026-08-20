#!/usr/bin/env bash
set -euo pipefail

SERVICE='src/SiteBuilder/LegacyShellShadowImportService.php'
CTRL='src/Admin/LegacyShellShadowAdminController.php'

for file in "$SERVICE" "$CTRL"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Immutable/hash-bound shadow identity and explicit no-public-mutation plan.
grep -F "'legacy-header-' . \$suffix" "$SERVICE" >/dev/null
grep -F "'legacy-footer-' . \$suffix" "$SERVICE" >/dev/null
grep -F "'PublicMutationAvailable' => false" "$SERVICE" >/dev/null
grep -F "'LegacyImportMode' => 'shadow-only'" "$SERVICE" >/dev/null
grep -F "'LegacySourceHash'" "$SERVICE" >/dev/null

# Import must verify global assignment is unchanged and roll back its own created templates on drift.
grep -F "globalAssignment('header') !==" "$SERVICE" >/dev/null
grep -F "globalAssignment('footer') !==" "$SERVICE" >/dev/null
grep -F "array_reverse(\$created)" "$SERVICE" >/dev/null
grep -F "\$this->repository->delete(\$templateId)" "$SERVICE" >/dev/null

# Explicit admin-only action, nonce and source-hash drift check.
grep -F "admin_post_h18_ud_import_legacy_shell_shadow" "$CTRL" >/dev/null
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null
grep -F "check_admin_referer(self::NONCE_ACTION)" "$CTRL" >/dev/null
grep -F "hash_equals(\$expectedHash, \$currentHash)" "$CTRL" >/dev/null
grep -F "wp_kses_post" "$CTRL" >/dev/null

# This slice may write shadow templates only through the repository. It must expose no public assignment/render/cutover primitive.
if grep -Ei 'assignGlobal\s*\(|template_redirect|wp_head|wp_footer|wp_nav_menu|switch_theme|set_theme_mod|wp_update_post\s*\(|wp_insert_post\s*\(|update_post_meta\s*\(|delete_post_meta\s*\(' "$SERVICE" "$CTRL" >/dev/null; then
  echo 'FAIL: I2A introduced a public assignment, frontend hook or page mutation primitive'
  exit 1
fi

echo 'I2A controlled Header/Footer shadow import contract: PASS'
