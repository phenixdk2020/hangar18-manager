(function () {
    'use strict';

    if (window.__h18HistoryRestoreLatchV0817) { return; }

    const state = {
        restoreLatched: false,
        selectionKey: '',
        preserveSelection: false,
        selectionToken: 0
    };

    document.documentElement.setAttribute('data-h18-v0817-history-latch', '1');

    function historyGuard() {
        return window.__h18HistoryTransactionV0814 || window.__h18HistoryObserverGuardV0813 || null;
    }

    function installRestoreLatchBridge() {
        const guard = historyGuard();
        if (!guard) { return null; }
        if (guard.__h18V0817RestoreLatchBridge) { return guard; }
        if (typeof guard.isSuppressed !== 'function') { return guard; }

        const baseIsSuppressed = guard.isSuppressed.bind(guard);
        const baseMarkTrustedEdit = typeof guard.markTrustedEdit === 'function'
            ? guard.markTrustedEdit.bind(guard)
            : null;

        guard.beginRestoreLatchV0817 = function (milliseconds) {
            state.restoreLatched = true;
            if (typeof guard.suppress === 'function') {
                guard.suppress(Math.max(1200, Number(milliseconds) || 0));
            }
        };

        guard.releaseRestoreLatchV0817 = function () {
            state.restoreLatched = false;
        };

        guard.isRestoreLatchedV0817 = function () {
            return state.restoreLatched === true;
        };

        guard.markTrustedEdit = function (milliseconds) {
            // A NEW trusted edit after Undo/Redo is the only thing that may
            // release the restore latch. Synthetic restore events never call
            // markTrustedEdit because the v0.8.16 bridge requires isTrusted.
            state.restoreLatched = false;
            if (baseMarkTrustedEdit) {
                baseMarkTrustedEdit(milliseconds);
            }
        };

        guard.isSuppressed = function () {
            // Important ordering: restore latch must win over the trusted-edit
            // window left behind by the action that is currently being undone.
            // v0.8.16 checked trusted first, which allowed 4 -> 3 -> 4.
            if (state.restoreLatched) { return true; }
            return baseIsSuppressed();
        };

        guard.__h18V0817RestoreLatchBridge = true;
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

    function currentSelectionKey() {
        const row = document.querySelector(
            '#h18-page-sections-sortable > .h18-page-section-row.is-selected:not(.h18-page-section-removed)'
        );
        return rowKey(row);
    }

    function rowByKey(key) {
        key = String(key || '');
        if (!key) { return null; }
        return activeRows().find(function (row) { return rowKey(row) === key; }) || null;
    }

    function restorePreservedSelection(token) {
        if (token !== state.selectionToken || !state.preserveSelection || !state.selectionKey) { return; }
        const row = rowByKey(state.selectionKey);
        if (!row || row.classList.contains('is-selected')) { return; }

        const header = row.querySelector(':scope > .h18-page-section-header') ||
            row.querySelector('.h18-page-section-header') ||
            row.querySelector('.h18-page-section-edit');
        if (header && typeof header.click === 'function') {
            header.click();
        }
    }

    function scheduleSelectionRestore(token) {
        // Base history restore is synchronous, while Inspector/runtime addons
        // rebuild immediately afterwards. Re-assert the user's CURRENT
        // selection after both phases without making selection part of history.
        [0, 40, 140].forEach(function (delay) {
            window.setTimeout(function () { restorePreservedSelection(token); }, delay);
        });
    }

    function beginRestoreTransaction(preserveSelection) {
        const guard = installRestoreLatchBridge();
        if (guard && typeof guard.beginRestoreLatchV0817 === 'function') {
            guard.beginRestoreLatchV0817(1200);
        } else if (guard && typeof guard.suppress === 'function') {
            guard.suppress(1200);
        }

        state.preserveSelection = preserveSelection === true;
        state.selectionKey = state.preserveSelection ? currentSelectionKey() : '';
        state.selectionToken += 1;
        const token = state.selectionToken;
        if (state.preserveSelection && state.selectionKey) {
            scheduleSelectionRestore(token);
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

    // Keyboard structural edits that do not necessarily emit input/change must
    // also be able to release the latch as genuine NEW user actions.
    document.addEventListener('keydown', function (event) {
        if (event.isTrusted !== true) { return; }
        const key = String(event.key || '');
        if (!event.altKey || (key !== 'ArrowUp' && key !== 'ArrowDown')) { return; }
        const guard = installRestoreLatchBridge();
        if (guard && typeof guard.markTrustedEdit === 'function') {
            guard.markTrustedEdit(900);
        }
    }, true);

    window.__h18HistoryRestoreLatchV0817 = {
        begin: beginRestoreTransaction,
        isLatched: function () { return state.restoreLatched === true; },
        selectionKey: function () { return state.selectionKey; },
        release: function () {
            const guard = installRestoreLatchBridge();
            if (guard && typeof guard.releaseRestoreLatchV0817 === 'function') {
                guard.releaseRestoreLatchV0817();
            } else {
                state.restoreLatched = false;
            }
        }
    };

    installRestoreLatchBridge();
}());
