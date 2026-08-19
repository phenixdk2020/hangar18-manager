<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Additive layout tools for the existing Sider editor.
 *
 * Kasse/Auto-kasser continue to reuse Container/Grid plus LayoutParentKey. The
 * v0.8.13 runtime deliberately has one authoritative Kasse placement path; the
 * superseded v0.8.10 inline composer is no longer enqueued.
 */
final class EditorLayoutToolsAdminController
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-layout-tools.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-layout-tools.css';
        $boxJsPath = $pluginDir . '/assets/ultimate-designer-box-tools.js';
        $boxCssPath = $pluginDir . '/assets/ultimate-designer-box-tools.css';
        $nestingJsPath = $pluginDir . '/assets/ultimate-designer-nesting-tools.js';
        $nestingCssPath = $pluginDir . '/assets/ultimate-designer-nesting-tools.css';
        $boxContentJsPath = $pluginDir . '/assets/ultimate-designer-box-content-layout.js';
        $boxContentCssPath = $pluginDir . '/assets/ultimate-designer-box-content-layout.css';
        $tableAppearanceJsPath = $pluginDir . '/assets/ultimate-designer-table-appearance.js';
        $tableAppearanceCssPath = $pluginDir . '/assets/ultimate-designer-table-appearance.css';

        self::enqueueEditorHistoryGuardV0813();

        wp_enqueue_script(
            'hangar18-ultimate-designer-layout-tools',
            $pluginUrl . 'assets/ultimate-designer-layout-tools.js',
            ['jquery', 'jquery-ui-sortable', 'hangar18-manager-admin'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.13',
            true
        );
        self::enqueueKasseDragAuthorityV0813();
        wp_enqueue_style(
            'hangar18-ultimate-designer-layout-tools',
            $pluginUrl . 'assets/ultimate-designer-layout-tools.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.13'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($boxJsPath) ? (string) filemtime($boxJsPath) : '0.8.13',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($boxCssPath) ? (string) filemtime($boxCssPath) : '0.8.13'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.js',
            ['jquery', 'jquery-ui-sortable', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools', 'hangar18-ultimate-designer-box-tools'],
            is_file($nestingJsPath) ? (string) filemtime($nestingJsPath) : '0.8.13',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.css',
            ['hangar18-ultimate-designer-box-tools'],
            is_file($nestingCssPath) ? (string) filemtime($nestingCssPath) : '0.8.13'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentJsPath) ? (string) filemtime($boxContentJsPath) : '0.8.13',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.css',
            ['hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentCssPath) ? (string) filemtime($boxContentCssPath) : '0.8.13'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceJsPath) ? (string) filemtime($tableAppearanceJsPath) : '0.8.13',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceCssPath) ? (string) filemtime($tableAppearanceCssPath) : '0.8.13'
        );
    }

    /**
     * admin.js records editor history with a MutationObserver on the full form.
     * Restoring a snapshot replaces the section rows synchronously, while the
     * observer callback runs afterwards. Without this guard that derived restore
     * mutation can be recorded as a brand-new edit, making Undo oscillate A/B.
     *
     * The wrapper only suppresses the observer whose target is the page-editor
     * form, and only for the short settle window immediately after Undo/Redo.
     * Other Kasse/UI observers remain untouched.
     */
    private static function enqueueEditorHistoryGuardV0813(): void
    {
        $before = <<<'JS'
(function () {
    'use strict';
    if (window.__h18HistoryObserverGuardV0813 || !window.MutationObserver) { return; }

    var NativeMutationObserver = window.MutationObserver;
    var suppressUntil = 0;
    var api = {
        suppress: function (milliseconds) {
            suppressUntil = Math.max(suppressUntil, Date.now() + Math.max(0, Number(milliseconds) || 0));
        },
        isSuppressed: function () {
            return Date.now() < suppressUntil;
        }
    };
    window.__h18HistoryObserverGuardV0813 = api;

    function GuardedMutationObserver(callback) {
        var meta = { target: null };
        var observer = new NativeMutationObserver(function (mutations, nativeObserver) {
            var guard = window.__h18HistoryObserverGuardV0813;
            var isEditorHistoryObserver = !!(meta.target && meta.target.id === 'h18-page-editor-form');
            if (isEditorHistoryObserver && guard && guard.isSuppressed()) {
                return;
            }
            callback(mutations, nativeObserver);
        });
        var nativeObserve = observer.observe.bind(observer);
        observer.observe = function (target, options) {
            meta.target = target || null;
            return nativeObserve(target, options);
        };
        return observer;
    }
    GuardedMutationObserver.prototype = NativeMutationObserver.prototype;
    window.MutationObserver = GuardedMutationObserver;
}());
JS;
        wp_add_inline_script('hangar18-manager-admin', $before, 'before');

        $after = <<<'JS'
(function () {
    'use strict';
    function suppressAfterHistoryStep() {
        if (window.__h18HistoryObserverGuardV0813) {
            window.__h18HistoryObserverGuardV0813.suppress(180);
        }
    }

    // Registered after admin.js: the built-in Undo/Redo handler restores first;
    // this listener then covers the MutationObserver microtask produced by it.
    document.addEventListener('click', function (event) {
        var target = event.target && event.target.closest ? event.target.closest('#h18-editor-undo,#h18-editor-redo') : null;
        if (target) { suppressAfterHistoryStep(); }
    }, false);

    document.addEventListener('keydown', function (event) {
        var key = String(event.key || '').toLowerCase();
        var editable = event.target && event.target.closest ? event.target.closest('input,textarea,select,[contenteditable="true"]') : null;
        if ((event.ctrlKey || event.metaKey) && key === 'z' && !editable) {
            suppressAfterHistoryStep();
        }
    }, false);
}());
JS;
        wp_add_inline_script('hangar18-manager-admin', $after, 'after');
    }

    /**
     * The historical layout-tools addon used to claim Kasse drag/drop before the
     * direct nesting runtime saw the event. During a Kasse drag we temporarily
     * expose it as an ordinary Container, so layout-tools does not start its old
     * pending placement flow while the v0.8.13 nesting runtime remains able to
     * recognise and own the drag through data-section-type="container".
     */
    private static function enqueueKasseDragAuthorityV0813(): void
    {
        $js = <<<'JS'
(function () {
    'use strict';
    document.documentElement.setAttribute('data-h18-v0813-kasse-authority', '1');

    document.addEventListener('dragstart', function (event) {
        var item = event.target && event.target.closest ? event.target.closest('.h18-builder-palette-item[data-h18-layout-tool="box"]') : null;
        if (!item) { return; }
        item.setAttribute('data-h18-v0813-drag-tool', 'box');
        item.removeAttribute('data-h18-layout-tool');
        setTimeout(function () { item.setAttribute('data-h18-layout-tool', 'box'); }, 0);
    }, true);
}());
JS;
        wp_add_inline_script('hangar18-ultimate-designer-layout-tools', $js, 'before');
    }
}
