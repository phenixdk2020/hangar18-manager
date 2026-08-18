#!/usr/bin/env bash
set -euo pipefail

grep -F "\$h18_ud_autoload = __DIR__ . '/src/Autoload.php';" hangar18-manager.php >/dev/null
grep -F 'if (is_admin()) {' hangar18-manager.php >/dev/null
grep -F '\Hangar18\UltimateDesigner\Admin\IntegrationAdminBootstrap::register();' hangar18-manager.php >/dev/null

# Only the exact public/runtime hooks are forbidden here. WordPress admin/AJAX hooks
# such as wp_ajax_* are legitimate controller boundaries and must not be mistaken
# for the exact frontend hook "wp".
frontend_hook_pattern="add_action\\('(wp|init|template_redirect|wp_head|wp_footer)'([,)]|[[:space:]])"

grep -F "add_action('admin_menu'" src/Admin/IntegrationAdminBootstrap.php >/dev/null
if grep -E "$frontend_hook_pattern" src/Admin/IntegrationAdminBootstrap.php >/dev/null; then
  echo 'FAIL: integration dashboard registers a frontend/runtime hook'; exit 1
fi
for controller in src/Admin/SiteTemplateAdminController.php src/Admin/MenuAdminController.php src/Admin/SideHealthAdminController.php; do
  if grep -E "$frontend_hook_pattern" "$controller" >/dev/null; then
    echo "FAIL: admin controller registers frontend/runtime hook: $controller"; exit 1
  fi
done

grep -F 'Ingen sidekonvertering' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -E "backlogRow\('I10',[[:space:]]*'Sidst'" src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Menu UI v2' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Side Health' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'wp_ajax_h18_ud_side_health' src/Admin/SideHealthAdminController.php >/dev/null
grep -F 'v0.7.4 – Ultimate Designer integration dashboard' assets/admin.css >/dev/null

if grep -RInE 'ultimate-designer-(admin|menu-admin|side-health)\.(js|css)' src --include='*.php' | grep -vE '^src/Admin/' >/dev/null; then
  echo 'FAIL: Ultimate Designer admin asset referenced outside Admin namespace'; exit 1
fi

echo 'Ultimate Designer integration admin safety contract I1-I4: PASS'
