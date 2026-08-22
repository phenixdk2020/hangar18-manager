<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only visual target layer for LEGO placement.
 *
 * Existing LayoutParentKey/nesting remains authoritative. LEGO-051 stores only
 * the new editor 2D stack/height relation in a separate option so old pages and
 * the existing container/flex/grid schema remain unchanged.
 */
final class EditorLegoDropZonesAdminController
{
    public const STACK_OPTION_V0851 = 'hangar18_ultimate_designer_lego_stack_v0851';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) { return; }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureStackSaveV0851'], 5);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) { return; }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $historyAtomicPath = $pluginDir . '/assets/ultimate-designer-history-atomic-v0840.js';
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-drop-zones-v0838.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-drop-zones-v0838.css';
        $paletteSideDropBridgePath = $pluginDir . '/assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js';
        $parentKeyGuardPath = $pluginDir . '/assets/ultimate-designer-lego-parent-key-guard-v0845.js';
        $inspectorOnlyJsPath = $pluginDir . '/assets/ultimate-designer-lego-inspector-only-v0847.js';
        $inspectorOnlyCssPath = $pluginDir . '/assets/ultimate-designer-lego-inspector-only-v0847.css';
        $selectionInspectorJsPath = $pluginDir . '/assets/ultimate-designer-lego-selection-inspector-v0849.js';
        $selectionInspectorCssPath = $pluginDir . '/assets/ultimate-designer-lego-selection-inspector-v0849.css';
        $liveHistoryInspectorJsPath = $pluginDir . '/assets/ultimate-designer-lego-live-history-inspector-v0850.js';
        $liveHistoryInspectorCssPath = $pluginDir . '/assets/ultimate-designer-lego-live-history-inspector-v0850.css';
        $kasseTerminologyJsPath = $pluginDir . '/assets/ultimate-designer-lego-kasse-terminology-v0850.js';
        $fixesJsPath = $pluginDir . '/assets/ultimate-designer-lego-fixes-v0851.js';
        $fixesCssPath = $pluginDir . '/assets/ultimate-designer-lego-fixes-v0851.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-history-atomic-v0840',
            $pluginUrl . 'assets/ultimate-designer-history-atomic-v0840.js',
            ['jquery', 'hangar18-ultimate-designer-nesting-tools'],
            is_file($historyAtomicPath) ? (string) filemtime($historyAtomicPath) : '0.8.40',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-drop-zones-v0838',
            $pluginUrl . 'assets/ultimate-designer-lego-drop-zones-v0838.js',
            ['jquery', 'hangar18-ultimate-designer-nesting-tools', 'hangar18-ultimate-designer-lego-layout-primary-v0837', 'hangar18-ultimate-designer-history-atomic-v0840'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.38',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-parent-key-guard-v0845',
            $pluginUrl . 'assets/ultimate-designer-lego-parent-key-guard-v0845.js',
            ['jquery', 'hangar18-ultimate-designer-nesting-tools'],
            is_file($parentKeyGuardPath) ? (string) filemtime($parentKeyGuardPath) : '0.8.45',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-palette-side-drop-bridge-v0843',
            $pluginUrl . 'assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js',
            ['jquery', 'hangar18-ultimate-designer-nesting-tools', 'hangar18-ultimate-designer-lego-drop-zones-v0838', 'hangar18-ultimate-designer-lego-parent-key-guard-v0845'],
            is_file($paletteSideDropBridgePath) ? (string) filemtime($paletteSideDropBridgePath) : '0.8.43',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-inspector-only-v0847',
            $pluginUrl . 'assets/ultimate-designer-lego-inspector-only-v0847.js',
            ['jquery', 'hangar18-ultimate-designer-nesting-tools', 'hangar18-ultimate-designer-lego-parent-key-guard-v0845'],
            is_file($inspectorOnlyJsPath) ? (string) filemtime($inspectorOnlyJsPath) : '0.8.47',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-selection-inspector-v0849',
            $pluginUrl . 'assets/ultimate-designer-lego-selection-inspector-v0849.js',
            ['hangar18-ultimate-designer-lego-inspector-only-v0847', 'hangar18-ultimate-designer-nesting-tools'],
            is_file($selectionInspectorJsPath) ? (string) filemtime($selectionInspectorJsPath) : '0.8.49',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-live-history-inspector-v0850',
            $pluginUrl . 'assets/ultimate-designer-lego-live-history-inspector-v0850.js',
            ['jquery', 'hangar18-ultimate-designer-history-atomic-v0840', 'hangar18-ultimate-designer-nesting-tools', 'hangar18-ultimate-designer-lego-selection-inspector-v0849'],
            is_file($liveHistoryInspectorJsPath) ? (string) filemtime($liveHistoryInspectorJsPath) : '0.8.50',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-kasse-terminology-v0850',
            $pluginUrl . 'assets/ultimate-designer-lego-kasse-terminology-v0850.js',
            ['hangar18-ultimate-designer-lego-live-history-inspector-v0850'],
            is_file($kasseTerminologyJsPath) ? (string) filemtime($kasseTerminologyJsPath) : '0.8.50',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-fixes-v0851',
            $pluginUrl . 'assets/ultimate-designer-lego-fixes-v0851.js',
            ['jquery', 'hangar18-ultimate-designer-lego-kasse-terminology-v0850', 'hangar18-ultimate-designer-lego-palette-side-drop-bridge-v0843', 'hangar18-ultimate-designer-lego-live-history-inspector-v0850', 'hangar18-ultimate-designer-lego-resize-v0841'],
            is_file($fixesJsPath) ? (string) filemtime($fixesJsPath) : '0.8.51',
            false
        );

        $stackStore = get_option(self::STACK_OPTION_V0851, []);
        wp_localize_script(
            'hangar18-ultimate-designer-lego-fixes-v0851',
            'H18LegoFixesV0851',
            ['version' => '0.8.51', 'schemaVersion' => 1, 'pages' => is_array($stackStore) ? $stackStore : []]
        );

        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-drop-zones-v0838',
            $pluginUrl . 'assets/ultimate-designer-lego-drop-zones-v0838.css',
            ['hangar18-ultimate-designer-nesting-tools'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.38'
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-inspector-only-v0847',
            $pluginUrl . 'assets/ultimate-designer-lego-inspector-only-v0847.css',
            ['hangar18-ultimate-designer-lego-drop-zones-v0838'],
            is_file($inspectorOnlyCssPath) ? (string) filemtime($inspectorOnlyCssPath) : '0.8.47'
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-selection-inspector-v0849',
            $pluginUrl . 'assets/ultimate-designer-lego-selection-inspector-v0849.css',
            ['hangar18-ultimate-designer-lego-inspector-only-v0847'],
            is_file($selectionInspectorCssPath) ? (string) filemtime($selectionInspectorCssPath) : '0.8.49'
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-live-history-inspector-v0850',
            $pluginUrl . 'assets/ultimate-designer-lego-live-history-inspector-v0850.css',
            ['hangar18-ultimate-designer-lego-selection-inspector-v0849'],
            is_file($liveHistoryInspectorCssPath) ? (string) filemtime($liveHistoryInspectorCssPath) : '0.8.50'
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-fixes-v0851',
            $pluginUrl . 'assets/ultimate-designer-lego-fixes-v0851.css',
            ['hangar18-ultimate-designer-lego-live-history-inspector-v0850', 'hangar18-ultimate-designer-lego-resize-v0841'],
            is_file($fixesCssPath) ? (string) filemtime($fixesCssPath) : '0.8.51'
        );
    }

    public static function captureStackSaveV0851(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        check_admin_referer('h18_save_page_editor');
        if (!isset($_POST['h18_lego_stack_v0851']) || !is_array($_POST['h18_lego_stack_v0851'])) { return; }

        $slug = isset($_POST['page_slug']) ? sanitize_title((string) wp_unslash($_POST['page_slug'])) : '';
        if ($slug === '') { return; }
        $rawEntries = wp_unslash($_POST['h18_lego_stack_v0851']);
        $sections = [];
        foreach ($rawEntries as $rawEntry) {
            if (!is_array($rawEntry)) { continue; }
            $sectionKey = isset($rawEntry['SectionKey']) ? sanitize_key((string) $rawEntry['SectionKey']) : '';
            if ($sectionKey === '') { continue; }
            $decoded = json_decode(isset($rawEntry['StateJson']) ? (string) $rawEntry['StateJson'] : '', true);
            $decoded = is_array($decoded) ? $decoded : [];
            $root = sanitize_key((string) ($decoded['StackRootKey'] ?? ''));
            if ($root === $sectionKey) { $root = ''; }
            $sections[$sectionKey] = [
                'SchemaVersion' => 1,
                'StackRootKey' => $root,
                'StackOrder' => max(0, (int) ($decoded['StackOrder'] ?? 0)),
                'DesktopPercent' => self::percentV0851($decoded['DesktopPercent'] ?? 0),
                'TabletPercent' => self::percentV0851($decoded['TabletPercent'] ?? 0),
                'MobilePercent' => self::percentV0851($decoded['MobilePercent'] ?? 0),
            ];
        }
        $store = get_option(self::STACK_OPTION_V0851, []);
        $store = is_array($store) ? $store : [];
        $store[$slug] = ['SchemaVersion' => 1, 'SavedUtc' => gmdate('c'), 'Sections' => $sections];
        update_option(self::STACK_OPTION_V0851, $store, false);
    }

    /** @param mixed $value */
    private static function percentV0851($value): int
    {
        if (!is_numeric($value)) { return 0; }
        $percent = (int) $value;
        if ($percent <= 0) { return 0; }
        return max(10, min(90, $percent));
    }
}
