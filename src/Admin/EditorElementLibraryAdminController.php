<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only UX enhancer for the existing Sider element palette.
 *
 * Search, categories and favorites operate entirely on the rendered palette.
 * Favorites are browser-local and this controller introduces no page storage,
 * public renderer, schema migration or cutover path.
 */
final class EditorElementLibraryAdminController
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-element-library.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-element-library.css';

        // v0.8.19 must run before assets/admin.js. The existing history engine
        // stores the return value from window.setTimeout in editorHistoryTimer;
        // installing this bridge afterwards leaves a timing window where the
        // legacy 120 ms structural debounce can collapse separate element adds.
        self::enqueueEditorHistoryCoreBridgeV0819();

        wp_enqueue_script(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.js',
            ['jquery', 'hangar18-manager-admin'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.7'
        );

        // v0.8.18 remains in the package solely as rollback archaeology. It is
        // deliberately NOT enqueued together with the preloaded v0.8.19 owner.
    }

    /**
     * Own editorHistoryRecordNow scheduling before the legacy editor initializes.
     *
     * Structural/explicit checkpoints (0..120 ms in the legacy engine) are
     * committed immediately instead of sharing the normal input debounce queue.
     * Text/input edits keep one debounced pending callback. Undo/Redo flushes that
     * callback once in capture phase while the legacy timer handle always stays 0,
     * so editorHistoryFlushPending() cannot replay an already-fired callback.
     */
    private static function enqueueEditorHistoryCoreBridgeV0819(): void
    {
        $js = <<<'JS'
(function () {
    'use strict';

    if (window.__h18HistoryCoreBridgeV0819) { return; }

    const state = {
        pending: null,
        pendingSerial: 0,
        restoreLatched: false,
        trustedReleaseBlockedUntil: 0,
        clearSelectionToken: 0
    };

    const inheritedSetTimeout = window.setTimeout.bind(window);
    const inheritedClearTimeout = window.clearTimeout.bind(window);

    document.documentElement.setAttribute('data-h18-v0819-history-runtime', '1');

    function historyGuard() {
        return window.__h18HistoryTransactionV0814 || window.__h18HistoryObserverGuardV0813 || null;
    }

    function isCoreHistoryCallback(callback) {
        return typeof callback === 'function' && callback.name === 'editorHistoryRecordNow';
    }

    function cancelPendingHistory() {
        const pending = state.pending;
        state.pending = null;
        if (pending && pending.nativeId) {
            inheritedClearTimeout(pending.nativeId);
        }
        return pending;
    }

    function runPendingHistory() {
        const pending = cancelPendingHistory();
        if (!pending || typeof pending.callback !== 'function') { return false; }
        pending.callback.apply(window, pending.args || []);
        return true;
    }

    function guardSuppressed() {
        const guard = historyGuard();
        return Boolean(guard && typeof guard.isSuppressed === 'function' && guard.isSuppressed());
    }

    // Authoritative history scheduler. This executes before assets/admin.js has
    // initialized its closure, so every later scheduleEditorHistoryCapture call
    // necessarily passes through this owner.
    window.setTimeout = function (callback, delay) {
        const args = Array.prototype.slice.call(arguments, 2);
        if (!isCoreHistoryCallback(callback)) {
            return inheritedSetTimeout.apply(window, [callback, delay].concat(args));
        }

        const milliseconds = Math.max(0, Number(delay) || 0);

        if (state.restoreLatched || guardSuppressed()) {
            cancelPendingHistory();
            return 0;
        }

        // Legacy structure capture uses 120 ms and explicit structural actions
        // use 0 ms. They are USER checkpoints, not typing debounce. Flush any
        // older text edit first, then commit the structural state immediately.
        if (milliseconds <= 120) {
            runPendingHistory();
            callback.apply(window, args);
            return 0;
        }

        // Normal field/text editing remains debounced, but its native timer id is
        // never exposed to legacy editorHistoryTimer. That variable always gets 0.
        cancelPendingHistory();
        state.pendingSerial += 1;
        const serial = state.pendingSerial;
        const pending = {
            serial: serial,
            nativeId: 0,
            callback: callback,
            args: args
        };
        state.pending = pending;
        pending.nativeId = inheritedSetTimeout(function () {
            if (!state.pending || state.pending.serial !== serial) { return; }
            state.pending = null;
            if (state.restoreLatched || guardSuppressed()) { return; }
            callback.apply(window, args);
        }, milliseconds);
        return 0;
    };

    function installGuardBridge() {
        const guard = historyGuard();
        if (!guard || typeof guard.isSuppressed !== 'function') { return guard; }
        if (guard.__h18V0819HistoryBridge) { return guard; }

        // v0.8.16 installs these functions from its ready callback. Wait until
        // that bridge exists so this runtime wraps it instead of being overwritten.
        if (typeof guard.hasTrustedEdit !== 'function' || typeof guard.markTrustedEdit !== 'function') {
            return guard;
        }

        const baseIsSuppressed = guard.isSuppressed.bind(guard);
        const baseHasTrustedEdit = guard.hasTrustedEdit.bind(guard);
        const baseMarkTrustedEdit = guard.markTrustedEdit.bind(guard);

        guard.hasTrustedEdit = function () {
            if (state.restoreLatched) { return false; }
            return baseHasTrustedEdit();
        };

        guard.markTrustedEdit = function (milliseconds) {
            if (state.restoreLatched && Date.now() < state.trustedReleaseBlockedUntil) {
                return;
            }
            state.restoreLatched = false;
            state.trustedReleaseBlockedUntil = 0;
            baseMarkTrustedEdit(milliseconds);
        };

        guard.isSuppressed = function () {
            if (state.restoreLatched) { return true; }
            return baseIsSuppressed();
        };

        guard.__h18V0819HistoryBridge = true;
        return guard;
    }

    function clearDirectDesignArtifacts() {
        document.querySelectorAll(
            '.h18-canvas-direct-controls,' +
            '.h18-canvas-padding-handle,' +
            '.h18-canvas-margin-handle,' +
            '.h18-canvas-box-model-overlay,' +
            '.h18-canvas-image-tools,' +
            '.h18-canvas-focal-dot'
        ).forEach(function (node) { node.remove(); });
    }

    function clearEditorSelection() {
        const selectedRows = Array.from(document.querySelectorAll(
            '#h18-page-sections-sortable > .h18-page-section-row.is-selected'
        ));
        const target = document.getElementById('h18-page-inspector-target');
        const body = target ? target.querySelector(':scope > .h18-page-section-body') : null;

        if (body && selectedRows.length) {
            selectedRows[0].appendChild(body);
        }

        selectedRows.forEach(function (row) { row.classList.remove('is-selected'); });
        document.querySelectorAll('.h18-navigator-item.is-selected').forEach(function (item) {
            item.classList.remove('is-selected');
        });
        document.querySelectorAll('.is-card-selected,.is-canvas-selected-card').forEach(function (node) {
            node.classList.remove('is-card-selected', 'is-canvas-selected-card');
        });

        if (target) {
            target.innerHTML = '<p class="description">Klik på <strong>Rediger</strong> ved en sektion for at ændre indhold, design og responsive indstillinger.</p>';
        }
        const heading = document.querySelector('#h18-page-inspector .h18-builder-inspector-heading span');
        if (heading) { heading.textContent = 'Vælg en sektion i sideopbygningen'; }
        const type = document.getElementById('h18-inspector-type');
        const key = document.getElementById('h18-inspector-key');
        if (type) { type.textContent = '–'; }
        if (key) { key.textContent = '–'; }
        [
            'h18-inspector-copy-key',
            'h18-inspector-duplicate',
            'h18-inspector-copy-design',
            'h18-inspector-paste-design',
            'h18-save-section-preset'
        ].forEach(function (id) {
            const button = document.getElementById(id);
            if (button) { button.disabled = true; }
        });
        clearDirectDesignArtifacts();
    }

    function scheduleSelectionClear(token) {
        [0, 40, 160, 420].forEach(function (delay) {
            inheritedSetTimeout(function () {
                if (token === state.clearSelectionToken) { clearEditorSelection(); }
            }, delay);
        });
    }

    function beginRestoreTransaction(clearSelection) {
        // A pending text/input edit belongs before Undo. Commit it exactly once.
        runPendingHistory();

        const guard = installGuardBridge();
        state.restoreLatched = true;
        state.trustedReleaseBlockedUntil = Date.now() + 100;
        if (guard && typeof guard.suppress === 'function') {
            guard.suppress(1600);
        }

        state.clearSelectionToken += 1;
        if (clearSelection === true) {
            scheduleSelectionClear(state.clearSelectionToken);
        }
    }

    function resultLabel(node) {
        if (!node || !node.querySelector) { return ''; }
        const label = node.querySelector('.h18-command-result-main');
        return String(label ? label.textContent : '').trim();
    }

    function isHistoryCommand(node) {
        const label = resultLabel(node);
        return label === 'Fortryd' || label === 'Gendan';
    }

    function activeCommandResult() {
        return document.querySelector('#h18-command-palette-results .h18-command-result.is-active');
    }

    function isEditableTarget(target) {
        return Boolean(target && target.closest && target.closest('input,textarea,select,[contenteditable="true"]'));
    }

    document.addEventListener('click', function (event) {
        const target = event.target && event.target.closest ? event.target : null;
        if (!target) { return; }

        if (target.closest('#h18-editor-undo,#h18-editor-redo')) {
            beginRestoreTransaction(true);
            return;
        }
        if (target.closest('#h18-editor-restore-draft')) {
            beginRestoreTransaction(false);
            return;
        }
        const command = target.closest('#h18-command-palette-results .h18-command-result');
        if (command && isHistoryCommand(command)) {
            beginRestoreTransaction(true);
        }
    }, true);

    document.addEventListener('keydown', function (event) {
        const key = String(event.key || '');
        const lower = key.toLowerCase();
        const target = event.target;
        if (!target || !target.closest) { return; }

        if ((event.ctrlKey || event.metaKey) && lower === 'z' && !isEditableTarget(target)) {
            beginRestoreTransaction(true);
            return;
        }
        if ((key === 'Enter' || key === ' ') && target.closest('#h18-editor-undo,#h18-editor-redo')) {
            beginRestoreTransaction(true);
            return;
        }
        if ((key === 'Enter' || key === ' ') && target.closest('#h18-editor-restore-draft')) {
            beginRestoreTransaction(false);
            return;
        }
        if ((key === 'Enter' || key === ' ') && target.closest('#h18-command-palette')) {
            const command = activeCommandResult();
            if (command && isHistoryCommand(command)) {
                beginRestoreTransaction(true);
            }
        }
    }, true);

    // Alt+arrow is a genuine structural user edit that may not emit input/change.
    document.addEventListener('keydown', function (event) {
        if (event.isTrusted !== true || !event.altKey) { return; }
        if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') { return; }
        const guard = installGuardBridge();
        if (guard && typeof guard.markTrustedEdit === 'function') {
            guard.markTrustedEdit(900);
        }
    }, true);

    // The v0.8.16 trusted-edit bridge is installed from a later jQuery ready
    // callback. Install our wrapper one macrotask after ready so it is final.
    if (window.jQuery) {
        window.jQuery(function () {
            inheritedSetTimeout(function () {
                installGuardBridge();
                const status = document.getElementById('h18-editor-history-status');
                if (status) {
                    status.setAttribute('data-h18-history-runtime', '0.8.19');
                    status.setAttribute('title', 'History runtime 0.8.19');
                }
            }, 0);
        });
    }

    window.__h18HistoryCoreBridgeV0819 = {
        flushPending: runPendingHistory,
        hasPending: function () { return Boolean(state.pending); },
        isLatched: function () { return state.restoreLatched === true; },
        clearSelection: clearEditorSelection,
        version: '0.8.19'
    };
}());
JS;

        wp_add_inline_script('hangar18-manager-admin', $js, 'before');
    }
}
