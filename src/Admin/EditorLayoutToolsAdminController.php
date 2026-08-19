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
        wp_add_inline_style(
            'hangar18-ultimate-designer-nesting-tools',
            '.h18-v0814-auto-kasse-drop{display:flex;align-items:center;justify-content:center;min-height:58px;margin-top:10px;padding:10px 12px;border:2px dashed #8c8f94;border-radius:7px;background:#fff;color:#50575e;font-size:12px;font-weight:700;text-align:center}.h18-v0814-auto-kasse-drop.is-active{border-color:#2271b1;background:#eaf4fb;color:#135e96;box-shadow:inset 0 0 0 1px rgba(34,113,177,.12)}'
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

    window.setTimeout = function (callback, delay) {
        var args = Array.prototype.slice.call(arguments, 2);
        var guard = window.__h18HistoryTransactionV0814;
        if (guard && guard.isSuppressed() && typeof callback === 'function' && callback.name === 'editorHistoryRecordNow') {
            return NativeSetTimeout(function () {}, 0);
        }
        return NativeSetTimeout.apply(window, [callback, delay].concat(args));
    };

    document.addEventListener('click', function (event) {
        var target = event.target && event.target.closest
            ? event.target.closest('#h18-editor-undo,#h18-editor-redo')
            : null;
        if (target) { api.suppress(520); }
    }, true);

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
     * During Kasse drag, hide the historical layout-tool marker from the old
     * layout-tools capture handler. The direct nesting runtime still recognises
     * the drag through data-h18-v0813-drag-tool="box".
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

    /**
     * Historical v0.8.14 Auto-kasse adapter retained only as dead reference for
     * rollback archaeology. It is deliberately NOT enqueued. The direct nesting
     * runtime owns all Kasse/Auto-kasser placement, while layout-tools only
     * configures the Grid created by the Auto-kasser palette item.
     */
    private static function enqueueAutoKasseAuthorityV0814(): void
    {
        $js = <<<'JS'
jQuery(function ($) {
    'use strict';

    var $sections = $('#h18-page-sections-sortable');
    var $inspector = $('#h18-page-inspector-target');
    if (!$sections.length) { return; }

    var AUTO_LABEL = 'Auto-kasser';
    var BOX_LABEL = 'Kasse';
    var autoCreate = null;
    var boxDragActive = false;
    var zoneTimer = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }
    function controls($row, selector) {
        var $result = $row.find(selector);
        if ($row.hasClass('is-selected')) { $result = $result.add($inspector.find(selector)); }
        return $result;
    }
    function rowKey($row) { return String($row.find('.h18-page-section-key').first().val() || ''); }
    function rowType($row) { return String($row.attr('data-section-type') || ''); }
    function rowLabel($row) { return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim(); }
    function parentKey($row) { return String(controls($row, '.h18-layout-parent-key').first().val() || ''); }
    function isAuto($row) { return !!($row.length && rowType($row) === 'grid' && rowLabel($row) === AUTO_LABEL); }
    function isBox($row) { return !!($row.length && rowType($row) === 'container' && rowLabel($row).indexOf(BOX_LABEL) === 0); }
    function snapshotKeys() {
        var keys = new Set();
        activeRows().each(function () { var key = rowKey($(this)); if (key) { keys.add(key); } });
        return keys;
    }
    function findNewRow(before, type) {
        var $match = $();
        activeRows().each(function () {
            var $row = $(this), key = rowKey($row);
            if (key && !before.has(key) && (!type || rowType($row) === type)) { $match = $row; }
        });
        return $match;
    }
    function setField($row, name, value) {
        var $field = controls($row, '[name$="[' + name + ']"]').first();
        if (!$field.length) { return; }
        if ($field.is(':checkbox')) {
            if ($field.is(':checked') !== !!value) { $field.prop('checked', !!value).trigger('change'); }
        } else if (String($field.val() || '') !== String(value)) {
            $field.val(String(value)).trigger('input').trigger('change');
        }
    }
    function setLabel($row, label) {
        var $field = controls($row, '.h18-section-navigator-label').first();
        if ($field.length && String($field.val() || '') !== label) {
            $field.val(label).trigger('input').trigger('change');
        }
    }
    function setParent($row, key) {
        var value = String(key || '');
        var $hidden = controls($row, '.h18-layout-parent-key').first();
        var $select = controls($row, '.h18-layout-parent-select').first();
        if ($hidden.length && String($hidden.val() || '') !== value) { $hidden.val(value).trigger('change'); }
        if ($select.length && String($select.val() || '') !== value) { $select.val(value).trigger('change'); }
    }
    function syncFlatOrder() {
        var index = 0;
        $sections.children('.h18-page-section-row').each(function () {
            var $row = $(this);
            if ($row.hasClass('h18-page-section-removed')) { return; }
            index += 1;
            $row.find('.h18-page-section-order').val(index * 10);
        });
        if ($sections.hasClass('ui-sortable')) { $sections.sortable('refresh'); }
    }
    function configureAuto($row) {
        if (!$row.length || rowType($row) !== 'grid') { return; }
        setLabel($row, AUTO_LABEL);
        setField($row, 'Title', '');
        setField($row, 'Content', '');
        setField($row, 'LayoutColumns', 1);
        setField($row, 'MobileLayoutColumns', 1);
        setField($row, 'LayoutGapPx', 16);
        setField($row, 'MobileLayoutGapPx', 12);
        setField($row, 'LayoutAlign', 'Stretch');
        setParent($row, '');
        $row.attr('data-h18-auto-box-row', '1').attr('data-h18-v0814-grid-only', '1');
    }
    function configureBox($row) {
        if (!$row.length || rowType($row) !== 'container') { return; }
        setLabel($row, BOX_LABEL);
        setField($row, 'Title', '');
        setField($row, 'Content', '');
        setField($row, 'LayoutDirection', 'Column');
        setField($row, 'LayoutWrap', true);
        setField($row, 'LayoutAlign', 'Stretch');
        setField($row, 'LayoutGapPx', 12);
        setField($row, 'MobileLayoutGapPx', 10);
        setField($row, 'MobileLayoutStack', true);
        $row.attr('data-h18-box', '1');
    }

    function installAutoTool() {
        var $tool = $('.h18-builder-palette-item[data-h18-layout-tool="auto-row"]').first();
        if (!$tool.length) { return; }
        $tool.attr('data-h18-v0814-auto-tool', '1')
            .attr('data-h18-v0813-drag-tool', 'auto-row')
            .removeAttr('data-h18-layout-tool');
    }

    function neutralizeAutoToolForEvent(item) {
        item.setAttribute('data-h18-layout-tool', 'v0814-auto-native');
        window.setTimeout(function () {
            if (item && item.getAttribute('data-h18-v0814-auto-tool') === '1') {
                item.removeAttribute('data-h18-layout-tool');
            }
        }, 0);
    }

    function finalizeAutoCreation(attempt) {
        if (!autoCreate) { return; }
        var $row = findNewRow(autoCreate.before, 'grid');
        if (!$row.length && attempt < 6) {
            window.setTimeout(function () { finalizeAutoCreation(attempt + 1); }, 30);
            return;
        }
        if ($row.length) {
            configureAuto($row);
            syncFlatOrder();
            scheduleZones(40);
        }
        autoCreate = null;
    }

    document.addEventListener('click', function (event) {
        var item = event.target && event.target.closest
            ? event.target.closest('.h18-builder-palette-item[data-h18-v0814-auto-tool="1"]')
            : null;
        if (!item) { return; }
        autoCreate = { before: snapshotKeys(), mode: 'click' };
        neutralizeAutoToolForEvent(item);
        window.setTimeout(function () { finalizeAutoCreation(0); }, 20);
    }, true);

    document.addEventListener('dragstart', function (event) {
        var autoItem = event.target && event.target.closest
            ? event.target.closest('.h18-builder-palette-item[data-h18-v0814-auto-tool="1"]')
            : null;
        if (autoItem) {
            autoCreate = { before: snapshotKeys(), mode: 'drag' };
            neutralizeAutoToolForEvent(autoItem);
            return;
        }
        var boxItem = event.target && event.target.closest ? event.target.closest('.h18-builder-palette-item') : null;
        if (!boxItem) { return; }
        var tool = String(boxItem.getAttribute('data-h18-layout-tool') || boxItem.getAttribute('data-h18-v0813-drag-tool') || '');
        boxDragActive = tool === 'box';
        if (boxDragActive) { $sections.attr('data-h18-v0814-box-drag', '1'); scheduleZones(0); }
    }, true);

    document.addEventListener('drop', function () {
        if (autoCreate && autoCreate.mode === 'drag') {
            window.setTimeout(function () { finalizeAutoCreation(0); }, 30);
        }
    }, true);

    function directBoxChildren($auto) {
        var key = rowKey($auto);
        return activeRows().filter(function () {
            var $row = $(this);
            return parentKey($row) === key && isBox($row);
        });
    }

    function ensureAutoDropZones() {
        activeRows().each(function () {
            var $auto = $(this);
            if (!isAuto($auto)) { return; }
            var key = rowKey($auto);
            var $preview = $auto.children('.h18-canvas-preview').first();
            if (!$preview.length) { return; }
            var $zone = $preview.children('.h18-v0814-auto-kasse-drop[data-h18-v0814-auto-key="' + key + '"]').first();
            var count = directBoxChildren($auto).length;
            if (!$zone.length) {
                $zone = $('<div>', {
                    class: 'h18-v0814-auto-kasse-drop',
                    'data-h18-v0814-auto-key': key
                });
                $preview.append($zone);
            }
            $zone.text(count
                ? 'Slip en Kasse her for at tilføje endnu en Kasse til Auto-kasser'
                : 'Slip en Kasse her for at oprette den første Kasse i Auto-kasser');
        });
    }
    function scheduleZones(delay) {
        window.clearTimeout(zoneTimer);
        zoneTimer = window.setTimeout(ensureAutoDropZones, typeof delay === 'number' ? delay : 60);
    }

    function createBoxInAuto(autoKey) {
        var $auto = activeRows().filter(function () { return rowKey($(this)) === String(autoKey); }).first();
        if (!isAuto($auto)) { return; }
        var before = snapshotKeys();
        var $tool = $('.h18-builder-palette-item[data-h18-layout-tool="box"],.h18-builder-palette-item[data-h18-v0813-drag-tool="box"]').first();
        if (!$tool.length) { return; }
        if (!$tool.attr('data-h18-layout-tool')) { $tool.attr('data-h18-layout-tool', 'box'); }
        var node = $tool.get(0);
        if (node && typeof node.click === 'function') { node.click(); } else { $tool.trigger('click'); }

        var finish = function (attempt) {
            var $box = findNewRow(before, 'container');
            if (!$box.length && attempt < 7) {
                window.setTimeout(function () { finish(attempt + 1); }, 30);
                return;
            }
            if (!$box.length) { return; }
            configureBox($box);
            var $boxes = directBoxChildren($auto).not($box);
            var $anchor = $boxes.length ? $boxes.last() : $auto;
            $box.insertAfter($anchor);
            setParent($box, rowKey($auto));
            syncFlatOrder();
            $box.attr('data-h18-v0811-child-source', '1');
            $(document).trigger('h18:v0814-auto-kasse-added', [rowKey($box), rowKey($auto)]);
            scheduleZones(80);
        };
        window.setTimeout(function () { finish(0); }, 70);
    }

    document.addEventListener('dragover', function (event) {
        if (!boxDragActive) { return; }
        var zone = event.target && event.target.closest ? event.target.closest('.h18-v0814-auto-kasse-drop') : null;
        if (!zone) { return; }
        event.preventDefault();
        if (typeof event.stopImmediatePropagation === 'function') { event.stopImmediatePropagation(); }
        $('.h18-v0814-auto-kasse-drop').removeClass('is-active');
        $(zone).addClass('is-active');
    }, true);

    document.addEventListener('drop', function (event) {
        if (!boxDragActive) { return; }
        var zone = event.target && event.target.closest ? event.target.closest('.h18-v0814-auto-kasse-drop') : null;
        if (!zone) { return; }
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') { event.stopImmediatePropagation(); }
        var autoKey = String(zone.getAttribute('data-h18-v0814-auto-key') || '');
        boxDragActive = false;
        $sections.removeAttr('data-h18-v0814-box-drag');
        $('.h18-v0814-auto-kasse-drop').removeClass('is-active');
        if (autoKey) { createBoxInAuto(autoKey); }
    }, true);

    document.addEventListener('dragend', function () {
        boxDragActive = false;
        $sections.removeAttr('data-h18-v0814-box-drag');
        $('.h18-v0814-auto-kasse-drop').removeClass('is-active');
        scheduleZones(100);
    }, true);

    var observer = new MutationObserver(function () { scheduleZones(60); });
    observer.observe($sections.get(0), { childList: true, subtree: true });

    installAutoTool();
    scheduleZones(80);
});
JS;
        wp_add_inline_script('hangar18-ultimate-designer-layout-tools', $js, 'after');
    }
}
