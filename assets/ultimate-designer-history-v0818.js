(function () {
    'use strict';

    if (window.__h18HistoryRuntimeV0818) { return; }

    const state = {
        pending: null,
        pendingSerial: 0,
        restoreLatched: false,
        trustedReleaseBlockedUntil: 0,
        selectionKey: '',
        preserveSelection: false,
        selectionToken: 0
    };

    const inheritedSetTimeout = window.setTimeout.bind(window);
    const inheritedClearTimeout = window.clearTimeout.bind(window);

    document.documentElement.setAttribute('data-h18-v0818-history-runtime', '1');

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

    function installHistoryTimerOwner() {
        if (window.__h18HistoryTimerOwnerV0818) { return; }

        window.setTimeout = function (callback, delay) {
            const args = Array.prototype.slice.call(arguments, 2);
            if (!isCoreHistoryCallback(callback)) {
                return inheritedSetTimeout.apply(window, [callback, delay].concat(args));
            }

            cancelPendingHistory();

            // admin.js stores the return value in editorHistoryTimer. Returning 0
            // is intentional: once our native timer has executed there must not
            // be a stale truthy timer id for editorHistoryFlushPending() to replay.
            if (state.restoreLatched) {
                return 0;
            }

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
                if (state.restoreLatched) { return; }
                callback.apply(window, args);
            }, Math.max(0, Number(delay) || 0));
            return 0;
        };

        window.__h18HistoryTimerOwnerV0818 = true;
    }

    function installGuardBridge() {
        const guard = historyGuard();
        if (!guard || typeof guard.isSuppressed !== 'function') { return guard; }
        if (guard.__h18V0818HistoryBridge) { return guard; }

        const baseIsSuppressed = guard.isSuppressed.bind(guard);
        const baseHasTrustedEdit = typeof guard.hasTrustedEdit === 'function'
            ? guard.hasTrustedEdit.bind(guard)
            : null;
        const baseMarkTrustedEdit = typeof guard.markTrustedEdit === 'function'
            ? guard.markTrustedEdit.bind(guard)
            : null;

        guard.hasTrustedEdit = function () {
            if (state.restoreLatched) { return false; }
            return baseHasTrustedEdit ? baseHasTrustedEdit() : false;
        };

        guard.markTrustedEdit = function (milliseconds) {
            // beforeinput/historyUndo from the same Ctrl/Cmd+Z gesture is trusted
            // by the browser, but it is not a new edit and may not reopen history.
            if (state.restoreLatched && Date.now() < state.trustedReleaseBlockedUntil) {
                return;
            }
            state.restoreLatched = false;
            state.trustedReleaseBlockedUntil = 0;
            if (baseMarkTrustedEdit) {
                baseMarkTrustedEdit(milliseconds);
            }
        };

        guard.isSuppressed = function () {
            if (state.restoreLatched) { return true; }
            return baseIsSuppressed();
        };

        guard.__h18V0818HistoryBridge = true;
        return guard;
    }

    function activeRows() {
        return Array.from(document.querySelectorAll(
            '#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)'
        ));
    }

    function rowKey(row) {
        if (!row || !row.querySelector) { return ''; }
        const input = row.querySelector('.h18-page-section-key');
        return String(input ? input.value : '').trim();
    }

    function rowByKey(key) {
        key = String(key || '');
        if (!key) { return null; }
        return activeRows().find(function (row) { return rowKey(row) === key; }) || null;
    }

    function currentSelectionKey() {
        const selected = document.querySelector(
            '#h18-page-sections-sortable > .h18-page-section-row.is-selected:not(.h18-page-section-removed)'
        );
        return rowKey(selected);
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

    function selectRow(row) {
        if (!row || row.classList.contains('is-selected')) { return; }
        const header = row.querySelector(':scope > .h18-page-section-header') ||
            row.querySelector('.h18-page-section-edit');
        if (header && typeof header.click === 'function') {
            header.click();
        }
    }

    function reconcileSelection(token) {
        if (token !== state.selectionToken || !state.preserveSelection) { return; }
        const wanted = rowByKey(state.selectionKey);
        if (wanted) {
            selectRow(wanted);
            return;
        }

        // The element selected before Undo no longer exists. Selection is UI
        // state, not page history: do not fall back to entry.selectedKey.
        clearEditorSelection();
    }

    function scheduleSelectionReconcile(token) {
        [0, 40, 160, 420].forEach(function (delay) {
            inheritedSetTimeout(function () { reconcileSelection(token); }, delay);
        });
    }

    function beginRestoreTransaction(preserveSelection) {
        // This is the authoritative flush. It executes a genuinely pending user
        // edit exactly once before Undo/Redo. The core flush sees timer id 0 and
        // therefore cannot replay an already-fired timer afterwards.
        runPendingHistory();

        const guard = installGuardBridge();
        state.restoreLatched = true;
        state.trustedReleaseBlockedUntil = Date.now() + 100;
        if (guard && typeof guard.suppress === 'function') {
            guard.suppress(1600);
        }

        state.preserveSelection = preserveSelection === true;
        state.selectionKey = state.preserveSelection ? currentSelectionKey() : '';
        state.selectionToken += 1;
        const token = state.selectionToken;
        if (state.preserveSelection) {
            scheduleSelectionReconcile(token);
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
        return !!(target && target.closest && target.closest('input,textarea,select,[contenteditable="true"]'));
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

    // Alt+arrow is a real structural edit that may not emit input/change.
    document.addEventListener('keydown', function (event) {
        if (event.isTrusted !== true || !event.altKey) { return; }
        if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') { return; }
        const guard = installGuardBridge();
        if (guard && typeof guard.markTrustedEdit === 'function') {
            guard.markTrustedEdit(900);
        }
    }, true);

    installHistoryTimerOwner();
    installGuardBridge();

    window.__h18HistoryRuntimeV0818 = {
        flushPending: runPendingHistory,
        hasPending: function () { return Boolean(state.pending); },
        isLatched: function () { return state.restoreLatched === true; },
        selectionKey: function () { return state.selectionKey; },
        clearSelection: clearEditorSelection
    };
}());
