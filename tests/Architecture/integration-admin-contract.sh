#!/usr/bin/env bash
set -euo pipefail

grep -F "\$h18_ud_autoload = __DIR__ . '/src/Autoload.php';" hangar18-manager.php >/dev/null
grep -F 'if (is_admin()) {' hangar18-manager.php >/dev/null
grep -F '\Hangar18\UltimateDesigner\Admin\IntegrationAdminBootstrap::register();' hangar18-manager.php >/dev/null

frontend_hook_pattern="add_action\\('(wp|init|template_redirect|wp_head|wp_footer)'([,)]|[[:space:]])"
grep -F "add_action('admin_menu'" src/Admin/IntegrationAdminBootstrap.php >/dev/null
if grep -E "$frontend_hook_pattern" src/Admin/IntegrationAdminBootstrap.php >/dev/null; then echo 'FAIL: integration dashboard registers a frontend/runtime hook'; exit 1; fi
for controller in \
  src/Admin/SiteTemplateAdminController.php \
  src/Admin/MenuAdminController.php \
  src/Admin/MenuPageChooserAdminController.php \
  src/Admin/SideHealthAdminController.php \
  src/Admin/EditorLayoutToolsAdminController.php \
  src/Admin/AssetManagerAdminController.php \
  src/Admin/PortabilityAdminController.php \
  src/Admin/PermissionsAdminController.php \
  src/Admin/AiAdminController.php \
  src/Admin/QaDashboardAdminController.php \
  src/Admin/ConversionAdminController.php \
  src/Admin/CutoverPreflightAdminController.php; do
  if grep -E "$frontend_hook_pattern" "$controller" >/dev/null; then echo "FAIL: admin controller registers frontend/runtime hook: $controller"; exit 1; fi
done

grep -F 'Ingen sidekonvertering' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Tilvalg/fravalg pr. side' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Editor layout+' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Side Health' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Asset Manager' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Portability Workspace' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Design Lock' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'AI forslag' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'Manual QA' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'I10 conversion' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'I10 signed preflight' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F "backlogRow('I9','Færdig'" src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F "backlogRow('I10','Aktiv · signed preflight'" src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'wp_ajax_h18_ud_side_health' src/Admin/SideHealthAdminController.php >/dev/null
grep -F 'wp_ajax_h18_ud_asset_duplicates' src/Admin/AssetManagerAdminController.php >/dev/null
grep -F 'wp_ajax_h18_ud_plan_artifact_import' src/Admin/PortabilityAdminController.php >/dev/null
grep -F 'PermissionsAdminController::register();' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'AiAdminController::register();' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'QaDashboardAdminController::register();' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'ConversionAdminController::register();' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'CutoverPreflightAdminController::register();' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'WordPressOptionConversionAcceptanceRepository' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'WordPressOptionCutoverPreflightRepository' src/Admin/IntegrationAdminBootstrap.php >/dev/null
grep -F 'v0.7.4 – Ultimate Designer integration dashboard' assets/admin.css >/dev/null

if grep -RInE 'ultimate-designer-(admin|menu-admin|menu-pages|side-health|asset-admin|portability|permissions|ai|qa|conversion|layout-tools)\.(js|css)' src --include='*.php' | grep -vE '^src/Admin/' >/dev/null; then
  echo 'FAIL: Ultimate Designer admin asset referenced outside Admin namespace'; exit 1
fi

echo 'Ultimate Designer integration admin safety contract I1-I10 signed preflight: PASS'
