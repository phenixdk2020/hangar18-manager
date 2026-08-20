(function () {
    'use strict';

    if (window.__h18HistoryCoreBridgeV0821) { return; }

    const state = {
        pending: null,
        pendingSerial: 0,
        restoreLatched: false,
        trustedReleaseBlockedUntil: 0,
        clearSelectionToken: 0,
        cloneBridgeInstalled: false
    };

    const inheritedSetTimeout = window.setTimeout.bind(window);
    const inheritedClearTimeout = window.clearTimeout.bind(window);

    document.documentElement.setAttribute('data-h18-v0821-history-runtime', '1');

    function historyGuard() {
        return window.__h18HistoryTransactionV0814 || window.__h18HistoryObserverGuardV0813 || null;
    }

    function isCoreHistoryCallback(callback) {
        return typeof callback === 'function' && callback.name === 'editorHistoryRecordNow';
    }

    function isHistoryCloneSource(node) {
        if (!node || node.nodeType !== 1) { return false; }
        if (node.id === 'h18-page-sections-sortable') { return true; }
        return Boolean(
            node.classList &&
            node.classList.contains('h18-page-section-body') &&
            node.closest &&
            node.closest('#h18-page-inspector-target')
        );
    }

    function copyFormControlState(sourceRoot, cloneRoot) {
        if (!sourceRoot || !cloneRoot || !sourceRoot.querySelectorAll || !cloneRoot.querySelectorAll) { return; }

        const sourceControls = Array.from(sourceRoot.querySelectorAll('input,textarea,select'));
        const cloneControls = Array.from(cloneRoot.querySelectorAll('input,textarea,select'));

        sourceControls.forEach(function (source, index) {
            const clone = cloneControls[index];
            if (!clone || String(source.tagName || '') !== String(clone.tagName || '')) { return; }

            if (source.tagName === 'SELECT') {
                const selectedValues = Array.from(source.options || [])
                    .filter(function (option) { return option.selected; })
                    .map(function (option) { return String(option.value); });

                Array.from(clone.options || []).forEach(function (option) {
                    const selected = selectedValues.includes(String(option.value));
                    option.selected = selected;
                    if (selected) { option.setAttribute('selected', 'selected'); }
                    else { option.removeAttribute('selected'); }
                });
                return;
            }

            if (source.tagName === 'TEXTAREA') {
                clone.value = String(source.value == null ? '' : source.value);
                clone.textContent = clone.value;
                return;
            }

            clone.value = String(source.value == null ? '' : source.value);
            clone.setAttribute('value', clone.value);
            if (source.type === 'checkbox' || source.type === 'radio') {
                clone.checked = Boolean(source.checked);
                if (clone.checked) { clone.setAttribute('checked', 'checked'); }
                else { clone.removeAttribute('checked'); }
            }
        });
    }

    function installHistoryCloneBridge() {
        const jq = window.jQuery;
        if (!jq || !jq.fn || typeof jq.fn.clone !== 'function') { return false; }
        if (jq.fn.clone.__h18V0821HistoryCloneBridge) {
            state.cloneBridgeInstalled = true;
            return true;
        }

        const baseClone = jq.fn.clone;
        const bridgedClone = function () {
            const clonedSet = baseClone.apply(this, arguments);
            this.each(function (index) {
                const source = this;
                const clone = clonedSet.get(index);
                if (!isHistoryCloneSource(source) || !clone) { return; }
                copyFormControlState(source, clone);
            });
            return clonedSet;
        };
        bridgedClone.__h18V0821HistoryCloneBridge = true;
        bridgedClone.__h18BaseClone = baseClone;
        jq.fn.clone = bridgedClone;
        state.cloneBridgeInstalled = true;
        return true;
    }

    // jQuery is a dependency of this header asset. Install before assets/admin.js
    // can create the history closure. The bridge is narrowly scoped to the two
    // clone sources used by editorHistorySnapshot(): the section collection and
    // the inspected section body temporarily moved into the Inspector.
    installHistoryCloneBridge();

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

    // This file is loaded in wp-admin's header. assets/admin.js is loaded in the
    // footer, so every editorHistoryRecordNow schedule is intercepted from the
    // first history tick regardless of PHP enqueue callback registration order.
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
        // use 0 ms. They are separate document checkpoints, not typing debounce.
        if (milliseconds <= 120) {
            runPendingHistory();
            callback.apply(window, args);
            return 0;
        }

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
        if (guard.__h18V0821HistoryBridge) { return guard; }

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

        guard.__h18V0821HistoryBridge = true;
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

    document.addEventListener('keydown', function (event) {
        if (event.isTrusted !== true || !event.altKey) { return; }
        if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') { return; }
        const guard = installGuardBridge();
        if (guard && typeof guard.markTrustedEdit === 'function') {
            guard.markTrustedEdit(900);
        }
    }, true);

    function installRuntimeIdentity() {
        installHistoryCloneBridge();
        installGuardBridge();
        const status = document.getElementById('h18-editor-history-status');
        if (!status) { return; }
        status.setAttribute('data-h18-history-runtime', '0.8.21');
        status.setAttribute('title', 'History runtime 0.8.21');
        const oldBadge = document.getElementById('h18-history-runtime-badge');
        if (oldBadge) { oldBadge.remove(); }
        const badge = document.createElement('small');
        badge.id = 'h18-history-runtime-badge';
        badge.textContent = 'H0.8.21';
        badge.title = 'Aktiv historikmotor 0.8.21';
        badge.style.cssText = 'margin-left:6px;opacity:.55;font-size:10px;white-space:nowrap';
        status.insertAdjacentElement('afterend', badge);
    }

    if (window.jQuery) {
        window.jQuery(function () {
            inheritedSetTimeout(installRuntimeIdentity, 0);
        });
    } else if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', installRuntimeIdentity, { once: true });
    } else {
        installRuntimeIdentity();
    }

    window.__h18HistoryCoreBridgeV0821 = {
        flushPending: runPendingHistory,
        hasPending: function () { return Boolean(state.pending); },
        isLatched: function () { return state.restoreLatched === true; },
        cloneBridgeInstalled: function () { return state.cloneBridgeInstalled === true; },
        copyFormControlState: copyFormControlState,
        clearSelection: clearEditorSelection,
        version: '0.8.21'
    };
}());
