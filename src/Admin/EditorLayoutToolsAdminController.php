<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Additive layout tools for the existing Sider editor.
 *
 * Kasse/Auto-kasser continue to reuse Container/Grid plus LayoutParentKey. The
 * direct nesting runtime is the authoritative Kasse placement path; historical
 * layout helpers are prevented from competing with drag/drop ownership.
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
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.14',
            true
        );
        self::enqueueKasseDragAuthorityV0813();
        wp_enqueue_style(
            'hangar18-ultimate-designer-layout-tools',
            $pluginUrl . 'assets/ultimate-designer-layout-tools.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.14'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($boxJsPath) ? (string) filemtime($boxJsPath) : '0.8.14',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($boxCssPath) ? (string) filemtime($boxCssPath) : '0.8.14'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.js',
            ['jquery', 'jquery-ui-sortable', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools', 'hangar18-ultimate-designer-box-tools'],
            is_file($nestingJsPath) ? (string) filemtime($nestingJsPath) : '0.8.14',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.css',
            ['hangar18-ultimate-designer-box-tools'],
            is_file($nestingCssPath) ? (string) filemtime($nestingCssPath) : '0.8.14'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentJsPath) ? (string) filemtime($boxContentJsPath) : '0.8.14',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.css',
            ['hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentCssPath) ? (string) filemtime($boxContentCssPath) : '0.8.14'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceJsPath) ? (string) filemtime($tableAppearanceJsPath) : '0.8.14',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceCssPath) ? (string) filemtime($tableAppearanceCssPath) : '0.8.14'
        );
    }

    /**
     * admin.js keeps editor history in its existing closure. A restore replaces
     * section rows synchronously, but MutationObserver and helper runtimes settle
     * afterwards. Those derived callbacks must never become a new user edit.
     *
     * v0.8.14 starts the guard in capture phase BEFORE Undo/Redo executes,
     * suppresses the editor-history MutationObserver through the settle window,
     * and defers any editorHistoryRecordNow timer that is scheduled by derived
     * input/change events until the guard has expired. The deferred recorder then
     * sees the restored signature and becomes a no-op; if the user genuinely edits
     * meanwhile, it records that real new state instead.
     */
    private static function enqueueEditorHistoryGuardV0813(): void
    {
        $before = <<<'JS'
(function () {
    'use strict';
    if (window.__h18HistoryObserverGuardV0813 || !window.MutationObserver) { return; }

    var NativeMutationObserver = window.MutationObserver;
    var NativeSetTimeout = window.setTimeout.bind(window);
    var suppressUntil = 0;
    var api = {
        suppress: function (milliseconds) {
            suppressUntil = Math.max(suppressUntil, Date.now() + Math.max(0, Number(milliseconds) || 0));
            document.documentElement.setAttribute('data-h18-v0814-history-restore', '1');
            NativeSetTimeout(function () {
                if (Date.now() >= suppressUntil) {
                    document.documentElement.removeAttribute('data-h18-v0814-history-restore');
                }
            }, Math.max(0, Number(milliseconds) || 0) + 20);
        },
        isSuppressed: function () {
            return Date.now() < suppressUntil;
        },
        remaining: function () {
            return Math.max(0, suppressUntil - Date.now());
        }
    };
    window.__h18HistoryObserverGuardV0813 = api;
    window.__h18HistoryTransactionV0814 = api;

    function GuardedMutationObserver(callback) {
        var meta = { target: null };
        var observer = new NativeMutationObserver(function (mutations, nativeObserver) {
            var guard = window.__h18HistoryTransactionV0814;
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

    // scheduleEditorHistoryCapture() passes the declared function directly to
    // setTimeout. If a derived Kasse/input event schedules it while a restore is
    // settling, run it only after the restore transaction. It will then compare
    // equal to the current history signature and not append a duplicate step.
    window.setTimeout = function (callback, delay) {
        var args = Array.prototype.slice.call(arguments, 2);
        var guard = window.__h18HistoryTransactionV0814;
        if (guard && guard.isSuppressed() && typeof callback === 'function' && callback.name === 'editorHistoryRecordNow') {
            var wait = Math.max(Number(delay) || 0, guard.remaining() + 30);
            return NativeSetTimeout(function () { callback.apply(window, args); }, wait);
        }
        return NativeSetTimeout.apply(window, [callback, delay].concat(args));
    };

    function beginHistoryRestore(event) {
        var target = event.target && event.target.closest
            ? event.target.closest('#h18-editor-undo,#h18-editor-redo')
            : null;
        if (target) { api.suppress(520); }
    }
    document.addEventListener('click', beginHistoryRestore, true);

    document.addEventListener('keydown', function (event) {
        var key = String(event.key || '').toLowerCase();
        var editable = event.target && event.target.closest
            ? event.target.closest('input,textarea,select,[contenteditable="true"]')
            : null;
        if ((event.ctrlKey || event.metaKey) && key === 'z' && !editable) {
            api.suppress(520);
        }
    }, true);
}());
JS;
        wp_add_inline_script('hangar18-manager-admin', $before, 'before');
    }

    /**
     * The historical layout-tools addon used to claim Kasse drag/drop before the
     * direct nesting runtime saw the event. During a Kasse drag we temporarily
     * expose it as an ordinary Container, so layout-tools does not start its old
     * pending placement flow while the direct nesting runtime remains able to
     * recognise and own the drag through data-section-type="container".
     */
    private static function enqueueKasseDragAuthorityV0813(): void
    {
        $js = <<<'JS'
(function () {
    'use strict';
    document.documentElement.setAttribute('data-h18-v0813-kasse-authority', '1');
    document.documentElement.setAttribute('data-h18-v0814-kasse-authority', '1');

    document.addEventListener('dragstart', function (event) {
        var item = event.target && event.target.closest
            ? event.target.closest('.h18-builder-palette-item[data-h18-layout-tool="box"]')
            : null;
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
