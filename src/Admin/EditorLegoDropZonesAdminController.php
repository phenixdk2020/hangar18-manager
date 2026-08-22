<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only visual target layer for LEGO placement.
 *
 * The visual asset does not own placement. Over/Under stay passive over jQuery
 * sortable, while Venstre/Højre reuse the existing nesting motor's
 * .h18-v0811-side-zone data contract. LEGO-031 also loads a thin atomic history
 * adapter which batches one drag/drop action into the existing history owner;
 * it does not create a second Undo/Redo stack or persistence model.
 *
 * LEGO-041 adds a browser-event bridge for palette drops whose pointer is inside
 * a visible side zone while the native HTML5 drop target remains the preview.
 * The bridge only retargets that event to the existing side-zone contract;
 * nesting-tools remains the sole placement/LayoutParentKey/Auto-kasser owner.
 *
 * LEGO-042 guards only the LayoutParentKey hidden/select handoff. It ensures a
 * freshly created canonical parent already exists as a select option before the
 * normal WordPress select change handler can mirror an empty value back into the
 * hidden key. It does not choose placement or create a second parent model.
 *
 * LEGO-047 makes Inspector the sole owner of content/design/media settings.
 * Canvas keeps direct layout manipulation (drag/drop and resize), while legacy
 * inline edit/media controls are redirected to Inspector. Selecting a nested
 * child also re-arms the existing visual reconciliation so Auto-kasse/Grid stays
 * visually stable while the authoritative settings body lives in Inspector.
 *
 * LEGO-049 keeps the selected element marker stable across transient Grid/Auto-
 * kasse rerenders and moves Dynamic data binding + Conditions/synlighed to the
 * bottom of Inspector as advanced controls without changing their data model.
 */
final class EditorLegoDropZonesAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

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

        wp_enqueue_script(
            'hangar18-ultimate-designer-history-atomic-v0840',
            $pluginUrl . 'assets/ultimate-designer-history-atomic-v0840.js',
            [
                'jquery',
                'hangar18-ultimate-designer-nesting-tools',
            ],
            is_file($historyAtomicPath) ? (string) filemtime($historyAtomicPath) : '0.8.40',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-drop-zones-v0838',
            $pluginUrl . 'assets/ultimate-designer-lego-drop-zones-v0838.js',
            [
                'jquery',
                'hangar18-ultimate-designer-nesting-tools',
                'hangar18-ultimate-designer-lego-layout-primary-v0837',
                'hangar18-ultimate-designer-history-atomic-v0840',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.38',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-parent-key-guard-v0845',
            $pluginUrl . 'assets/ultimate-designer-lego-parent-key-guard-v0845.js',
            [
                'jquery',
                'hangar18-ultimate-designer-nesting-tools',
            ],
            is_file($parentKeyGuardPath) ? (string) filemtime($parentKeyGuardPath) : '0.8.45',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-palette-side-drop-bridge-v0843',
            $pluginUrl . 'assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js',
            [
                'jquery',
                'hangar18-ultimate-designer-nesting-tools',
                'hangar18-ultimate-designer-lego-drop-zones-v0838',
                'hangar18-ultimate-designer-lego-parent-key-guard-v0845',
            ],
            is_file($paletteSideDropBridgePath) ? (string) filemtime($paletteSideDropBridgePath) : '0.8.43',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-inspector-only-v0847',
            $pluginUrl . 'assets/ultimate-designer-lego-inspector-only-v0847.js',
            [
                'jquery',
                'hangar18-ultimate-designer-nesting-tools',
                'hangar18-ultimate-designer-lego-parent-key-guard-v0845',
            ],
            is_file($inspectorOnlyJsPath) ? (string) filemtime($inspectorOnlyJsPath) : '0.8.47',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-selection-inspector-v0849',
            $pluginUrl . 'assets/ultimate-designer-lego-selection-inspector-v0849.js',
            [
                'hangar18-ultimate-designer-lego-inspector-only-v0847',
                'hangar18-ultimate-designer-nesting-tools',
            ],
            is_file($selectionInspectorJsPath) ? (string) filemtime($selectionInspectorJsPath) : '0.8.49',
            false
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
    }
}
