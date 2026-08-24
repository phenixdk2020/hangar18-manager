(function () {
    'use strict';

    if (window.__h18SaveIntegrityGuardV0891) { return; }

    const VERSION = '0.8.91';
    const FORM_ID = 'h18-page-editor-form';
    const ROW_SELECTOR = '#h18-page-sections-sortable > .h18-page-section-row[data-index]';
    const CAPTURE_MAX_AGE_MS = 15000;

    let saveIntent = null;
    let lastPointerCaptureAt = 0;

    function form() {
        return document.getElementById(FORM_ID);
    }

    function cleanKey(value) {
        return String(value == null ? '' : value).trim().toLowerCase().replace(/[^a-z0-9._-]/g, '');
    }

    function rowKey(row) {
        if (!row) { return ''; }
        const input = row.querySelector('.h18-page-section-key,[name$="[Key]"]');
        return cleanKey(input && input.value);
    }

    function controlsForRow(row, selector) {
        const result = [];
        if (!row) { return result; }

        Array.from(row.querySelectorAll(selector)).forEach(function (node) {
            if (result.indexOf(node) === -1) { result.push(node); }
        });

        if (row.classList.contains('is-selected')) {
            const inspector = document.getElementById('h18-page-inspector-target');
            if (inspector) {
                Array.from(inspector.querySelectorAll(selector)).forEach(function (node) {
                    if (result.indexOf(node) === -1) { result.push(node); }
                });
            }
        }

        return result;
    }

    function firstControlValue(row, selector, fallback) {
        const controls = controlsForRow(row, selector);
        if (!controls.length) { return fallback; }
        return String(controls[0].value == null ? fallback : controls[0].value);
    }

    function removeValue(row) {
        return firstControlValue(row, '.h18-page-section-remove,[name$="[Remove]"]', '0');
    }

    function parentKey(row) {
        return cleanKey(firstControlValue(
            row,
            '.h18-page-section-layout-parent,.h18-layout-parent-key,[name$="[LayoutParentKey]"]',
            ''
        ));
    }

    function rowType(row) {
        return String(
            (row && row.getAttribute('data-section-type')) ||
            firstControlValue(row, '[name$="[Type]"]', '')
        ).trim().toLowerCase();
    }

    function removed(row) {
        return Boolean(
            row && (
                row.classList.contains('h18-page-section-removed') ||
                removeValue(row) === '1'
            )
        );
    }

    function snapshot(reason) {
        const rows = Array.from(document.querySelectorAll(ROW_SELECTOR));
        const sections = rows.map(function (row) {
            return {
                index: String(row.getAttribute('data-index') || ''),
                key: rowKey(row),
                type: rowType(row),
                removed: removed(row),
                removeValue: removeValue(row),
                parentKey: parentKey(row)
            };
        });

        return {
            version: VERSION,
            reason: String(reason || ''),
            time: Date.now(),
            sectionCount: sections.length,
            activeCount: sections.filter(function (item) { return !item.removed; }).length,
            sections: sections
        };
    }

    function trace(type, detail) {
        const api = window.__h18UltimateDesignerTraceV0876;
        if (api && typeof api.record === 'function') {
            try {
                api.record(type, document.activeElement, detail || {}, { force: true });
            } catch (ignore) {}
        }
    }

    function flushDiagnosticsSoon() {
        window.setTimeout(function () {
            const diagnostics = window.__h18LiveDiagnosticsV0888;
            if (diagnostics && typeof diagnostics.flush === 'function') {
                try { diagnostics.flush(); } catch (ignore) {}
            }
        }, 0);
    }

    function isSubmitControl(node) {
        const editorForm = form();
        if (!editorForm || !node || !node.closest) { return false; }
        const submitter = node.closest('button[type="submit"],input[type="submit"],button:not([type])');
        return Boolean(submitter && editorForm.contains(submitter));
    }

    function captureSaveIntent(reason) {
        const current = snapshot(reason || 'save-intent');
        saveIntent = current;
        trace('DIAG_SAVE_GUARD_CAPTURE_V0891', current);
    }

    function setControls(row, selector, value) {
        controlsForRow(row, selector).forEach(function (node) {
            if ('value' in node) { node.value = String(value); }
        });
    }

    function findRow(section) {
        const rows = Array.from(document.querySelectorAll(ROW_SELECTOR));
        if (section && section.key) {
            const byKey = rows.find(function (row) { return rowKey(row) === section.key; });
            if (byKey) { return byKey; }
        }
        if (section) {
            return rows.find(function (row) {
                return String(row.getAttribute('data-index') || '') === String(section.index || '');
            }) || null;
        }
        return null;
    }

    function restoreSection(section) {
        const row = findRow(section);
        if (!row) { return false; }

        row.classList.remove('h18-page-section-removed');
        setControls(row, '.h18-page-section-remove,[name$="[Remove]"]', '0');
        setControls(
            row,
            '.h18-page-section-layout-parent,.h18-layout-parent-key,[name$="[LayoutParentKey]"]',
            section.parentKey || ''
        );
        return true;
    }

    function recoverIfCatastrophic(event) {
        const editorForm = form();
        if (!editorForm || !event || event.target !== editorForm) { return; }

        const before = snapshot('submit-capture-before-guard');
        const intent = saveIntent;
        const age = intent ? Date.now() - Number(intent.time || 0) : Number.MAX_SAFE_INTEGER;
        const activeAtIntent = intent ? intent.sections.filter(function (item) { return !item.removed; }) : [];
        const allIntentRowsStillExist = activeAtIntent.length > 0 && activeAtIntent.every(function (item) {
            return Boolean(findRow(item));
        });
        const catastrophic = Boolean(
            intent &&
            age >= 0 && age <= CAPTURE_MAX_AGE_MS &&
            intent.activeCount > 0 &&
            before.activeCount === 0 &&
            allIntentRowsStillExist
        );

        if (!catastrophic) {
            if (intent && intent.activeCount !== before.activeCount) {
                trace('DIAG_SAVE_GUARD_CHECK_V0891', {
                    version: VERSION,
                    recovered: false,
                    intentAgeMs: age,
                    intentActiveCount: intent.activeCount,
                    submitActiveCount: before.activeCount,
                    reason: 'not-catastrophic'
                });
            }
            return;
        }

        let restored = 0;
        activeAtIntent.forEach(function (section) {
            if (restoreSection(section)) { restored += 1; }
        });

        const after = snapshot('submit-capture-after-guard');
        trace('DIAG_SAVE_GUARD_RECOVER_V0891', {
            version: VERSION,
            recovered: true,
            intentAgeMs: age,
            restored: restored,
            intent: intent,
            before: before,
            after: after
        });
        flushDiagnosticsSoon();
    }

    document.addEventListener('pointerdown', function (event) {
        if (!isSubmitControl(event.target)) { return; }
        lastPointerCaptureAt = Date.now();
        captureSaveIntent('submit-pointerdown');
    }, true);

    document.addEventListener('mousedown', function (event) {
        if (!isSubmitControl(event.target)) { return; }
        if (Date.now() - lastPointerCaptureAt < 80) { return; }
        captureSaveIntent('submit-mousedown');
    }, true);

    document.addEventListener('keydown', function (event) {
        if (!isSubmitControl(event.target)) { return; }
        const key = String(event.key || '').toLowerCase();
        if (key === 'enter' || key === ' ') {
            captureSaveIntent('submit-keydown');
        }
    }, true);

    window.addEventListener('submit', recoverIfCatastrophic, true);

    window.__h18SaveIntegrityGuardV0891 = {
        version: VERSION,
        snapshot: function () { return snapshot('api'); },
        capture: function () { captureSaveIntent('api'); return saveIntent; },
        lastCapture: function () { return saveIntent; }
    };
}());
