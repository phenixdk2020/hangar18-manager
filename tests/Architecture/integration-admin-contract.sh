#!/usr/bin/env bash
set -euo pipefail

grep -F "\$h18_ud_autoload = __DIR__ . '/src/Autoload.php';" hangar18-manager.php >/dev/null
grep -F 'if (is_admin()) {' hangar18-manager.php >/dev/null
grep -F '\Hangar18\UltimateDesigner\Admin\IntegrationAdminBootstrap::register();' hangar18-manager.php >/dev/null

grep -F "add_action('admin_menu'" src/Admin/IntegrationAdminBootstrap.php >/dev/null
if grep -E "add_action\('(wp|init|template_redirect|wp_head|wp_footer)" src/Admin/IntegrationAdminBootstrap.php >/dev/null; then
  echo 'FAIL: integration dashboard registers a frontend/runtime hook'
  exit 1
fi

grep -F 'Ingen sidekonvertering' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F "self::backlogRow('I10', 'Sidst'" src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'v0.7.4 – Ultimate Designer integration dashboard' assets/admin.css >/dev/null

echo 'Ultimate Designer integration admin safety contract: PASS'
