<?php
/**
 * Plugin Name: Visual Designer Manager
 * Plugin URI: https://github.com/phenixdk2020/hangar18-manager
 * Update URI: https://github.com/phenixdk2020/hangar18-manager
 * Description: Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.
 * Version: 0.1.92
 * Author: Visual Designer Manager
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Text Domain: visual-designer-manager
 */

if (!defined('ABSPATH')) {
    exit;
}

define('VDM_VERSION', '0.1.92');
define('VDM_FILE', __FILE__);
define('VDM_DIR', plugin_dir_path(__FILE__));
define('VDM_URL', plugin_dir_url(__FILE__));

/* Deprecated compatibility aliases. New code must use VDM_* constants. */
define('H18_CLEAN_VERSION', '0.1.92');
define('H18_CLEAN_FILE', VDM_FILE);
define('H18_CLEAN_DIR', VDM_DIR);
define('H18_CLEAN_URL', VDM_URL);

/**
 * Compatibility marker for Hangar18 Base Theme 1.2.x.
 *
 * The theme only checks whether the historical Hangar18_Manager class exists
 * to decide if a Manager is active. Visual Designer Manager deliberately does not load the
 * legacy manager runtime, but exposing this empty marker keeps the theme's
 * status detection correct while the current architecture remains isolated.
 */
if (!class_exists('Hangar18_Manager', false)) {
    final class Hangar18_Manager
    {
        public const CLEAN_COMPATIBILITY_MARKER = true;

        private function __construct()
        {
        }
    }
}

require_once VDM_DIR . 'src/Compatibility/LegacyStorageBridge.php';
require_once H18_CLEAN_DIR . 'src/Icons/IconRegistry.php';
require_once H18_CLEAN_DIR . 'src/Modules/ModuleRegistry.php';
require_once H18_CLEAN_DIR . 'src/Modules/ModuleRecord.php';
require_once H18_CLEAN_DIR . 'src/Modules/ModuleBinding.php';
require_once H18_CLEAN_DIR . 'src/Modules/ModuleStore.php';
require_once H18_CLEAN_DIR . 'src/Modules/VehicleFieldRegistry.php';
require_once H18_CLEAN_DIR . 'src/Modules/EventFieldRegistry.php';
require_once H18_CLEAN_DIR . 'src/Forms/FormService.php';
require_once H18_CLEAN_DIR . 'src/Model/HierarchyNormalizer.php';
require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';
require_once H18_CLEAN_DIR . 'src/Model/ModuleDesignModel.php';
require_once H18_CLEAN_DIR . 'src/Migration/CanvasSectionMigration.php';
require_once H18_CLEAN_DIR . 'src/Migration/SiteDesignHarmonizer.php';
require_once H18_CLEAN_DIR . 'src/Migration/FormPageProvisioner.php';
require_once H18_CLEAN_DIR . 'src/Migration/HybridModulePageMigration.php';
require_once H18_CLEAN_DIR . 'src/Migration/EventDetailFactsMigration.php';
require_once H18_CLEAN_DIR . 'src/Model/GlobalLayoutModel.php';
require_once H18_CLEAN_DIR . 'src/Model/TemplateLayoutModel.php';
require_once H18_CLEAN_DIR . 'src/Migration/LegacyHeaderConverter.php';
require_once H18_CLEAN_DIR . 'src/Migration/LegacyFooterConverter.php';
require_once H18_CLEAN_DIR . 'src/Migration/ExternalPageSourceService.php';
require_once H18_CLEAN_DIR . 'src/Migration/VisualBlockConversionService.php';
require_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';
require_once H18_CLEAN_DIR . 'src/Migration/ConvertedButtonOverlayMigration.php';
require_once H18_CLEAN_DIR . 'src/Diagnostics/DiagnosticStore.php';
require_once H18_CLEAN_DIR . 'src/Admin/EditorController.php';
require_once H18_CLEAN_DIR . 'src/Admin/AdminController.php';
require_once H18_CLEAN_DIR . 'src/Admin/ManualController.php';
require_once H18_CLEAN_DIR . 'src/Admin/VehicleAdminController.php';
require_once H18_CLEAN_DIR . 'src/Admin/EventAdminController.php';
require_once H18_CLEAN_DIR . 'src/Admin/GalleryAdminController.php';
require_once H18_CLEAN_DIR . 'src/Admin/AdminMenuBridge.php';
require_once H18_CLEAN_DIR . 'src/Admin/ConversionController.php';
require_once H18_CLEAN_DIR . 'src/Admin/ExportController.php';
require_once VDM_DIR . 'src/Admin/PortableTransferController.php';
require_once VDM_DIR . 'src/Admin/SiteSettingsController.php';
require_once H18_CLEAN_DIR . 'src/Admin/NavigationController.php';
require_once H18_CLEAN_DIR . 'src/Admin/ThemeController.php';
require_once H18_CLEAN_DIR . 'src/Admin/GlobalDesignerController.php';
require_once H18_CLEAN_DIR . 'src/Frontend/HybridModuleSlots.php';
require_once H18_CLEAN_DIR . 'src/Frontend/CollectionPageRenderer.php';
require_once H18_CLEAN_DIR . 'src/Frontend/Renderer.php';
require_once H18_CLEAN_DIR . 'src/Frontend/ResponsiveRenderer.php';
require_once H18_CLEAN_DIR . 'src/Frontend/ThemeShell.php';
require_once H18_CLEAN_DIR . 'src/Update/GitHubUpdater.php';

add_action('plugins_loaded', static function (): void {
    \VisualDesignerManager\Modules\ModuleStore::register();
    \VisualDesignerManager\Forms\FormService::register();
    \VisualDesignerManager\Migration\CanvasSectionMigration::register();
    \VisualDesignerManager\Migration\SiteDesignHarmonizer::register();
    \VisualDesignerManager\Migration\FormPageProvisioner::register();
    \VisualDesignerManager\Migration\HybridModulePageMigration::register();
    \VisualDesignerManager\Migration\EventDetailFactsMigration::register();
    \VisualDesignerManager\Migration\ConvertedButtonOverlayMigration::register();
    \VisualDesignerManager\Diagnostics\DiagnosticStore::register();
    \VisualDesignerManager\Admin\EditorController::register();
    \VisualDesignerManager\Admin\AdminController::register();
    \VisualDesignerManager\Admin\ManualController::register();
    \VisualDesignerManager\Admin\VehicleAdminController::register();
    \VisualDesignerManager\Admin\EventAdminController::register();
    \VisualDesignerManager\Admin\GalleryAdminController::register();
    \VisualDesignerManager\Admin\AdminMenuBridge::register();
    \VisualDesignerManager\Admin\ConversionController::register();
    \VisualDesignerManager\Admin\ExportController::register();
    \VisualDesignerManager\Admin\PortableTransferController::register();
    \VisualDesignerManager\Admin\SiteSettingsController::register();
    \VisualDesignerManager\Admin\NavigationController::register();
    \VisualDesignerManager\Admin\ThemeController::register();
    \VisualDesignerManager\Admin\GlobalDesignerController::register();
    \VisualDesignerManager\Frontend\Renderer::register();
    \VisualDesignerManager\Frontend\ResponsiveRenderer::register();
    \VisualDesignerManager\Frontend\ThemeShell::register();
    \VisualDesignerManager\Update\GitHubUpdater::register();
});

add_action('admin_enqueue_scripts', static function (string $hook): void {
    $isPageDesigner = strpos($hook, 'h18-clean-editor') !== false;
    $isGlobalDesigner = strpos($hook, 'h18-clean-header-footer') !== false;
    if ((!$isPageDesigner && !$isGlobalDesigner) || !current_user_can('edit_pages')) {
        return;
    }

    /*
     * Current Visual Designer Manager core provides theme-accurate preview, canonical grid layout,
     * verified Save, independent image-box rendering and responsive layout editing.
     */
    wp_dequeue_script('h18-clean-editor');

    $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;
    if ($isGlobalDesigner) {
        $part = isset($_GET['part']) && sanitize_key((string) $_GET['part']) === 'footer' ? 'footer' : 'header';
        $postId = 0;
        \VisualDesignerManager\Model\TemplateLayoutModel::ensureMigrated();
        $templateId = isset($_GET['template']) ? sanitize_key((string) $_GET['template']) : '';
        if ($templateId === '' || !\VisualDesignerManager\Model\TemplateLayoutModel::exists($templateId, $part)) { $templateId = \VisualDesignerManager\Model\TemplateLayoutModel::defaultId($part); }
        $model = $templateId !== '' ? \VisualDesignerManager\Model\TemplateLayoutModel::model($templateId) : \VisualDesignerManager\Model\LayoutModel::empty();
        $templateMeta = $templateId !== '' ? \VisualDesignerManager\Model\TemplateLayoutModel::meta($templateId) : null;
        $contextLabel = is_array($templateMeta) ? (string) ($templateMeta['name'] ?? ($part === 'header' ? 'Header' : 'Footer')) : ($part === 'header' ? 'Header' : 'Footer');
    } else {
        $model = $postId > 0 && get_post_type($postId) === 'page'
            ? \VisualDesignerManager\Model\LayoutModel::get($postId)
            : \VisualDesignerManager\Model\LayoutModel::empty();
        $contextLabel = $postId > 0 ? (string) get_the_title($postId) : 'Visual Designer';
    }

    $menuPayload = array_values(array_map(static function ($menu): array {
        $items = wp_get_nav_menu_items((int) $menu->term_id);
        $items = is_array($items) ? $items : [];
        return [
            'id' => (int) $menu->term_id,
            'name' => (string) $menu->name,
            'items' => array_values(array_map(static function ($item): array {
                return [
                    'id' => (int) $item->ID,
                    'title' => wp_strip_all_tags((string) $item->title),
                    'url' => esc_url_raw((string) $item->url),
                    'parent' => (int) $item->menu_item_parent,
                ];
            }, $items)),
        ];
    }, wp_get_nav_menus()));

    $vehicleRecords = array_values(array_map(static function (array $item): array {
        $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
        $featuredId = absint($record['featuredMediaId'] ?? 0);
        $featuredUrl = $featuredId > 0 ? wp_get_attachment_image_url($featuredId, 'large') : false;
        return [
            'postId' => (int) ($item['postId'] ?? 0),
            'id' => (string) ($record['id'] ?? ''),
            'title' => (string) ($record['title'] ?? ''),
            'status' => (string) ($record['status'] ?? 'draft'),
            'sortOrder' => (int) ($record['sortOrder'] ?? 0),
            'summary' => (string) ($record['summary'] ?? ''),
            'featuredMediaId' => $featuredId,
            'featuredUrl' => is_string($featuredUrl) ? $featuredUrl : '',
            'fields' => isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [],
            'attributes' => isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [],
        ];
    }, \VisualDesignerManager\Modules\ModuleStore::listRecords('vehicles', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC'])));

    $eventRecords = array_values(array_map(static function (array $item): array {
        $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
        $featuredId = absint($record['featuredMediaId'] ?? 0);
        $featuredUrl = $featuredId > 0 ? wp_get_attachment_image_url($featuredId, 'large') : false;
        return [
            'postId' => (int) ($item['postId'] ?? 0),
            'id' => (string) ($record['id'] ?? ''),
            'title' => (string) ($record['title'] ?? ''),
            'status' => (string) ($record['status'] ?? 'draft'),
            'sortOrder' => (int) ($record['sortOrder'] ?? 0),
            'summary' => (string) ($record['summary'] ?? ''),
            'featuredMediaId' => $featuredId,
            'featuredUrl' => is_string($featuredUrl) ? $featuredUrl : '',
            'fields' => isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [],
            'attributes' => isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [],
        ];
    }, \VisualDesignerManager\Modules\ModuleStore::listRecords('events', ['status' => 'all', 'limit' => 100, 'orderBy' => 'start', 'order' => 'ASC'])));

    $galleryRecords = array_values(array_map(static function (array $item): array {
        $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
        $featuredId = absint($record['featuredMediaId'] ?? 0);
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        if ($featuredId <= 0 && $imageIds) { $featuredId = (int) $imageIds[0]; }
        $featuredUrl = $featuredId > 0 ? wp_get_attachment_image_url($featuredId, 'large') : false;
        $imageUrls = [];
        foreach (array_slice($imageIds, 0, 100) as $imageId) {
            $url = wp_get_attachment_image_url($imageId, 'large');
            if (is_string($url) && $url !== '') { $imageUrls[] = ['id' => $imageId, 'url' => $url]; }
        }
        return [
            'postId' => (int) ($item['postId'] ?? 0),
            'id' => (string) ($record['id'] ?? ''),
            'title' => (string) ($record['title'] ?? ''),
            'status' => (string) ($record['status'] ?? 'draft'),
            'sortOrder' => (int) ($record['sortOrder'] ?? 0),
            'summary' => (string) ($record['summary'] ?? ''),
            'featuredMediaId' => $featuredId,
            'featuredUrl' => is_string($featuredUrl) ? $featuredUrl : '',
            'fields' => $fields,
            'imageUrls' => $imageUrls,
        ];
    }, \VisualDesignerManager\Modules\ModuleStore::listRecords('galleries', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC'])));

    /* v0.1.81: collect an active theme/Designer palette without restricting free color choice. */
    $themePalette = [];
    $collectPaletteColor = static function ($value) use (&$themePalette): void {
        if (!is_scalar($value)) { return; }
        $hex = sanitize_hex_color((string) $value);
        if (!is_string($hex) || $hex === '') { return; }
        $hex = strtolower($hex);
        if (strlen($hex) === 4) {
            $hex = '#' . $hex[1] . $hex[1] . $hex[2] . $hex[2] . $hex[3] . $hex[3];
        }
        if (!in_array($hex, $themePalette, true)) { $themePalette[] = $hex; }
    };
    $collectPaletteTree = null;
    $collectPaletteTree = static function ($value) use (&$collectPaletteTree, $collectPaletteColor): void {
        if (is_array($value)) {
            if (isset($value['color'])) { $collectPaletteColor($value['color']); }
            foreach ($value as $child) { $collectPaletteTree($child); }
            return;
        }
        $collectPaletteColor($value);
    };
    if (function_exists('wp_get_global_settings')) {
        foreach (['theme', 'custom', 'default'] as $origin) {
            $candidate = wp_get_global_settings(['color', 'palette', $origin]);
            if (is_array($candidate)) { $collectPaletteTree($candidate); }
        }
    }
    $themeMods = get_theme_mods();
    if (is_array($themeMods)) { $collectPaletteTree($themeMods); }
    $collectPaletteTree($model);
    $themePalette = array_slice(array_values(array_unique($themePalette)), 0, 24);

    wp_enqueue_script(
        'h18-clean-editor-v0144-viewport',
        H18_CLEAN_URL . 'assets/editor-v0144-viewport.js',
        ['jquery'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v018-core',
        H18_CLEAN_URL . 'assets/editor-v018-core.js',
        ['jquery', 'h18-clean-editor-v0144-viewport'],
        H18_CLEAN_VERSION,
        true
    );
    wp_localize_script('h18-clean-editor-v018-core', 'H18CleanEditor', [
        'version' => H18_CLEAN_VERSION,
        'schemaVersion' => \VisualDesignerManager\Model\LayoutModel::SCHEMA,
        'units' => \VisualDesignerManager\Model\LayoutModel::UNITS,
        'rowPx' => \VisualDesignerManager\Model\LayoutModel::ROW_PX,
        'postId' => $postId,
        'userId' => get_current_user_id(),
        'contextLabel' => $contextLabel,
        'themePalette' => $themePalette,
        'iconLibrary' => \VisualDesignerManager\Icons\IconRegistry::editorCatalog(),
        'moduleCatalog' => \VisualDesignerManager\Modules\ModuleRegistry::editorCatalog(),
        'vehicleRecords' => $vehicleRecords,
        'vehicleAdminUrl' => admin_url('admin.php?page=h18-clean-vehicles'),
        'eventRecords' => $eventRecords,
        'eventAdminUrl' => admin_url('admin.php?page=h18-clean-events'),
        'eventFieldDefinitions' => \VisualDesignerManager\Modules\EventFieldRegistry::all(),
        'galleryRecords' => $galleryRecords,
        'galleryAdminUrl' => admin_url('admin.php?page=h18-clean-gallery'),
        'initialModel' => $model,
        'pages' => array_values(array_map(static function ($page): array { return ['id' => (int) $page->ID, 'title' => (string) $page->post_title]; }, get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC', 'post_status' => ['publish', 'draft', 'pending', 'private', 'future']]))),
        'menus' => $menuPayload,
        'menuAdminUrl' => admin_url('admin.php?page=h18-clean-menu'),
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'diagAction' => 'h18_clean_diag_append',
        'diagNonce' => wp_create_nonce('h18_clean_diag_append'),
    ]);

    wp_enqueue_style(
        'h18-clean-editor-v016',
        H18_CLEAN_URL . 'assets/editor-v016.css',
        ['h18-clean-editor'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v018',
        H18_CLEAN_URL . 'assets/editor-v018.css',
        ['h18-clean-editor-v016'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0110',
        H18_CLEAN_URL . 'assets/editor-v0110.css',
        ['h18-clean-editor-v018'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0112',
        H18_CLEAN_URL . 'assets/editor-v0112.css',
        ['h18-clean-editor-v0110'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0114',
        H18_CLEAN_URL . 'assets/editor-v0114.css',
        ['h18-clean-editor-v0112'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0117',
        H18_CLEAN_URL . 'assets/editor-v0117.css',
        ['h18-clean-editor-v0114'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0118',
        H18_CLEAN_URL . 'assets/editor-v0118.css',
        ['h18-clean-editor-v0117'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0120',
        H18_CLEAN_URL . 'assets/editor-v0120.css',
        ['h18-clean-editor-v0118'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0121',
        H18_CLEAN_URL . 'assets/editor-v0121.css',
        ['h18-clean-editor-v0120'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0122-hierarchy',
        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.css',
        ['h18-clean-editor-v0121'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0123-ux',
        H18_CLEAN_URL . 'assets/editor-v0123-ux.css',
        ['h18-clean-editor-v0122-hierarchy'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0125',
        H18_CLEAN_URL . 'assets/editor-v0125.css',
        ['h18-clean-editor-v0123-ux'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0131',
        H18_CLEAN_URL . 'assets/editor-v0131.css',
        ['h18-clean-editor-v0125'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0132',
        H18_CLEAN_URL . 'assets/editor-v0132.css',
        ['h18-clean-editor-v0131'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0134',
        H18_CLEAN_URL . 'assets/editor-v0134.css',
        ['h18-clean-editor-v0132'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0144',
        H18_CLEAN_URL . 'assets/editor-v0144.css',
        ['h18-clean-editor-v0134'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0148-layers',
        H18_CLEAN_URL . 'assets/editor-v0148-layers.css',
        ['h18-clean-editor-v0144'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0153-transparent',
        H18_CLEAN_URL . 'assets/editor-v0153-transparent.css',
        ['h18-clean-editor-v0148-layers'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0154-menu',
        H18_CLEAN_URL . 'assets/editor-v0154-menu.css',
        ['h18-clean-editor-v0153-transparent'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0165-elements',
        H18_CLEAN_URL . 'assets/editor-v0165-elements.css',
        ['h18-clean-editor-v0154-menu'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0166-foundation',
        H18_CLEAN_URL . 'assets/editor-v0166-foundation.css',
        ['h18-clean-editor-v0165-elements'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0181',
        H18_CLEAN_URL . 'assets/editor-v0181.css',
        ['h18-clean-editor-v0166-foundation'],
        H18_CLEAN_VERSION
    );

    wp_enqueue_script(
        'h18-clean-editor-v0114',
        H18_CLEAN_URL . 'assets/editor-v0114.js',
        ['h18-clean-editor-v018-core'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0120',
        H18_CLEAN_URL . 'assets/editor-v0120.js',
        ['h18-clean-editor-v0114'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0121',
        H18_CLEAN_URL . 'assets/editor-v0121.js',
        ['h18-clean-editor-v0120'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0121-panels',
        H18_CLEAN_URL . 'assets/editor-v0121-panels.js',
        ['h18-clean-editor-v0121'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0122-hierarchy',
        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.js',
        ['h18-clean-editor-v0121-panels'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0123-ux',
        H18_CLEAN_URL . 'assets/editor-v0123-ux.js',
        ['h18-clean-editor-v0122-hierarchy'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0125',
        H18_CLEAN_URL . 'assets/editor-v0125.js',
        ['h18-clean-editor-v0123-ux'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0131',
        H18_CLEAN_URL . 'assets/editor-v0131.js',
        ['h18-clean-editor-v0125'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0132',
        H18_CLEAN_URL . 'assets/editor-v0132.js',
        ['h18-clean-editor-v0131'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0148-layers',
        H18_CLEAN_URL . 'assets/editor-v0148-layers.js',
        ['h18-clean-editor-v0132'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0169-canvas-height',
        H18_CLEAN_URL . 'assets/editor-v0169-canvas-height.js',
        ['h18-clean-editor-v0148-layers'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0181-color-picker',
        H18_CLEAN_URL . 'assets/editor-v0181-color-picker.js',
        ['h18-clean-editor-v0169-canvas-height'],
        H18_CLEAN_VERSION,
        true
    );
    /* v0.1.6 border/autogrow JS is retired; current Clean core handles these natively. */
}, 20);
