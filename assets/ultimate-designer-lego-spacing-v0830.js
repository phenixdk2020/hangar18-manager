jQuery(function ($) {
    'use strict';

    const config = window.H18LegoSpacingV0830 || {};
    const $form = $('#h18-page-editor-form');
    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector');
    const $inspectorTarget = $('#h18-page-inspector-target');
    if (!$form.length || !$sections.length || !$inspector.length) {
        return;
    }

    const PANEL_ID = 'h18-ud-lego-spacing-panel';
    const STATE_CLASS = 'h18-lego-spacing-state-json';
    const SUBMIT_ATTR = 'data-h18-lego-submit';
    const desktopMax = Math.max(0, parseInt(config.limits && config.limits.desktop, 10) || 160);
    const mobileMax = Math.max(0, parseInt(config.limits && config.limits.mobile, 10) || 120);
    let refreshTimer = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function rowControls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($inspectorTarget.find(selector));
        }
        return $result;
    }

    function rowKey($row) {
        return String(rowControls($row, '.h18-page-section-key').first().val() || $row.attr('data-key') || '');
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || rowControls($row, '.h18-page-section-type').first().val() || '');
    }

    function isLayoutRow($row) {
        return ['container', 'flex', 'grid'].indexOf(rowType($row)) !== -1;
    }

    function pageSlug() {
        return String($form.find('[name="page_slug"]').first().val() || '').trim();
    }

    function clamp(value, max, fallback) {
        const parsed = parseInt(value, 10);
        if (!Number.isFinite(parsed)) { return fallback; }
        return Math.max(0, Math.min(max, parsed));
    }

    function legacyNumber($row, suffix, fallback) {
        const $field = rowControls($row, '[name$="[' + suffix + ']"]').first();
        if (!$field.length) { return fallback; }
        return clamp($field.val(), suffix.indexOf('Mobile') === 0 ? mobileMax : desktopMax, fallback);
    }

    function defaults($row) {
        const desktopGap = legacyNumber($row, 'LayoutGapPx', 16);
        const mobileGap = legacyNumber($row, 'MobileLayoutGapPx', 12);
        return {
            SchemaVersion: 1,
            Desktop: {
                Margin: { X: 0, Y: 0 },
                Gap: { X: desktopGap, Y: desktopGap }
            },
            Mobile: {
                Margin: { X: 0, Y: 0 },
                Gap: { X: mobileGap, Y: mobileGap }
            }
        };
    }

    function normalizePair(raw, max, fallback) {
        raw = raw && typeof raw === 'object' ? raw : {};
        return {
            X: clamp(raw.X, max, fallback.X),
            Y: clamp(raw.Y, max, fallback.Y)
        };
    }

    function normalizeState($row, raw) {
        const fallback = defaults($row);
        raw = raw && typeof raw === 'object' ? raw : {};
        const desktop = raw.Desktop && typeof raw.Desktop === 'object' ? raw.Desktop : {};
        const mobile = raw.Mobile && typeof raw.Mobile === 'object' ? raw.Mobile : {};
        return {
            SchemaVersion: 1,
            Desktop: {
                Margin: normalizePair(desktop.Margin, desktopMax, fallback.Desktop.Margin),
                Gap: normalizePair(desktop.Gap, desktopMax, fallback.Desktop.Gap)
            },
            Mobile: {
                Margin: normalizePair(mobile.Margin, mobileMax, fallback.Mobile.Margin),
                Gap: normalizePair(mobile.Gap, mobileMax, fallback.Mobile.Gap)
            }
        };
    }

    function storedSections() {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        return page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
    }

    function canonicalField($row) {
        return rowControls($row, '.' + STATE_CLASS).first();
    }

    function ensureCanonicalField($row, initialState) {
        let $field = canonicalField($row);
        if ($field.length) { return $field; }
        const state = normalizeState($row, initialState);
        $field = $('<input>', {
            type: 'hidden',
            class: STATE_CLASS,
            value: JSON.stringify(state),
            'data-h18-lego-canonical': '1'
        });
        let $body = rowControls($row, '.h18-page-section-body').first();
        if (!$body.length) { $body = $row; }
        $body.append($field);
        return $field;
    }

    function stateForRow($row) {
        const $field = canonicalField($row);
        if ($field.length) {
            try {
                return normalizeState($row, JSON.parse(String($field.val() || '{}')));
            } catch (error) {
                return defaults($row);
            }
        }
        const key = rowKey($row);
        const stored = storedSections();
        const raw = key && stored[key] && typeof stored[key] === 'object' ? stored[key] : {};
        return normalizeState($row, raw);
    }

    function writeState($row, state, captureHistory) {
        state = normalizeState($row, state);
        const $field = ensureCanonicalField($row, state);
        $field.val(JSON.stringify(state));

        const node = $row.get(0);
        if (node) {
            node.style.setProperty('--h18-lego-margin-x', state.Desktop.Margin.X + 'px');
            node.style.setProperty('--h18-lego-margin-y', state.Desktop.Margin.Y + 'px');
            node.style.setProperty('--h18-lego-gap-x', state.Desktop.Gap.X + 'px');
            node.style.setProperty('--h18-lego-gap-y', state.Desktop.Gap.Y + 'px');
            node.style.setProperty('--h18-lego-mobile-margin-x', state.Mobile.Margin.X + 'px');
            node.style.setProperty('--h18-lego-mobile-margin-y', state.Mobile.Margin.Y + 'px');
            node.style.setProperty('--h18-lego-mobile-gap-x', state.Mobile.Gap.X + 'px');
            node.style.setProperty('--h18-lego-mobile-gap-y', state.Mobile.Gap.Y + 'px');
        }
        $row.attr('data-h18-lego-spacing', '1');

        if (captureHistory) {
            // The existing admin.js form listener owns the checkpoint. This is
            // the only event emitted for one Inspector spacing edit.
            $field.trigger('input');
        }
        return state;
    }

    function hydrateRow($row) {
        const existing = canonicalField($row);
        if (existing.length) {
            writeState($row, stateForRow($row), false);
            return;
        }
        const key = rowKey($row);
        const stored = storedSections();
        const raw = key && stored[key] && typeof stored[key] === 'object' ? stored[key] : {};
        writeState($row, normalizeState($row, raw), false);
    }

    function selectedRow() {
        return activeRows().filter('.is-selected').first();
    }

    function valueAt(state, path) {
        return path.split('.').reduce(function (current, key) {
            return current && typeof current === 'object' ? current[key] : undefined;
        }, state);
    }

    function setAt(state, path, value) {
        const parts = path.split('.');
        let current = state;
        parts.slice(0, -1).forEach(function (key) {
            if (!current[key] || typeof current[key] !== 'object') { current[key] = {}; }
            current = current[key];
        });
        current[parts[parts.length - 1]] = value;
    }

    function numberControl(label, path, state, max, help) {
        const $label = $('<label>', { class: 'h18-ud-lego-control' });
        $label.append($('<strong>', { text: label }));
        $label.append(
            $('<span>', { class: 'h18-ud-lego-number' }).append(
                $('<input>', {
                    type: 'number', min: 0, max: max, step: 1,
                    value: valueAt(state, path),
                    'data-h18-lego-path': path
                }),
                $('<em>', { text: 'px' })
            )
        );
        if (help) { $label.append($('<small>', { text: help })); }
        return $label;
    }

    function deviceGroup(title, device, state, layout) {
        const max = device === 'Mobile' ? mobileMax : desktopMax;
        const $group = $('<fieldset>', { class: 'h18-ud-lego-device' });
        $group.append($('<legend>', { text: title }));
        const $grid = $('<div>', { class: 'h18-ud-lego-grid' });
        $grid.append(
            numberControl('Element X', device + '.Margin.X', state, max, 'Venstre + højre'),
            numberControl('Element Y', device + '.Margin.Y', state, max, 'Over + under')
        );
        if (layout) {
            $grid.append(
                numberControl('Indhold X', device + '.Gap.X', state, max, 'Mellem kolonner/klodser'),
                numberControl('Indhold Y', device + '.Gap.Y', state, max, 'Mellem rækker/klodser')
            );
        }
        $group.append($grid);
        return $group;
    }

    function renderPanel() {
        $('#' + PANEL_ID).remove();
        const $row = selectedRow();
        if (!$row.length) { return; }
        hydrateRow($row);

        const state = stateForRow($row);
        const layout = isLayoutRow($row);
        const $panel = $('<section>', {
            id: PANEL_ID,
            class: 'h18-section-module-box h18-canvas-direct-controls h18-ud-lego-spacing-panel',
            'data-h18-lego-key': rowKey($row)
        });
        $panel.append(
            $('<div>', { class: 'h18-ud-lego-heading' }).append(
                $('<div>').append(
                    $('<h4>', { text: 'LEGO-afstand X / Y' }),
                    $('<p>', { class: 'description', text: 'Styr vandret og lodret afstand separat. Samme element-model bruges af almindelige elementer og Kasser.' })
                ),
                $('<span>', { class: 'h18-ud-lego-badge', text: '0.8.30' })
            ),
            deviceGroup('Desktop', 'Desktop', state, layout),
            deviceGroup('Mobil', 'Mobile', state, layout)
        );
        if (layout) {
            $panel.append($('<p>', {
                class: 'description h18-ud-lego-note',
                text: 'Indhold X/Y er Kasse/Grid/Flex-afstanden mellem klodser. Hvis LEGO-state ikke fandtes før, starter begge akser fra eksisterende LayoutGap.'
            }));
        }
        $inspector.append($panel);
    }

    function applyAll() {
        activeRows().each(function () { hydrateRow($(this)); });
    }

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(function () {
            applyAll();
            renderPanel();
        }, typeof delay === 'number' ? delay : 40);
    }

    $(document).on('input change', '#' + PANEL_ID + ' [data-h18-lego-path]', function () {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const path = String($(this).attr('data-h18-lego-path') || '');
        if (!/^(Desktop|Mobile)\.(Margin|Gap)\.(X|Y)$/.test(path)) { return; }
        const state = stateForRow($row);
        const max = path.indexOf('Mobile.') === 0 ? mobileMax : desktopMax;
        const current = parseInt(valueAt(state, path), 10) || 0;
        setAt(state, path, clamp($(this).val(), max, current));
        writeState($row, state, true);
    });

    function appendSavePayload() {
        $form.find('[' + SUBMIT_ATTR + '="1"]').remove();
        let index = 0;
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (!key) { return; }
            hydrateRow($row);
            const values = {
                SectionKey: key,
                StateJson: JSON.stringify(stateForRow($row)),
                LegacyLayoutGapPx: legacyNumber($row, 'LayoutGapPx', 16),
                LegacyMobileLayoutGapPx: legacyNumber($row, 'MobileLayoutGapPx', 12)
            };
            Object.keys(values).forEach(function (name) {
                $('<input>', {
                    type: 'hidden',
                    name: 'h18_lego_spacing[' + index + '][' + name + ']',
                    value: values[name]
                }).attr(SUBMIT_ATTR, '1').appendTo($form);
            });
            index += 1;
        });
    }

    $form.on('submit.h18LegoSpacingV0830', appendSavePayload);

    $(document).on(
        'click',
        '.h18-page-section-header,.h18-page-section-edit,.h18-v0811-edit-child,.h18-ud-auto-box-tile,.h18-ud-box-child-chip,.h18-navigator-select',
        function () { scheduleRefresh(50); }
    );

    const observer = new MutationObserver(function (mutations) {
        const relevant = mutations.some(function (mutation) {
            return mutation.type === 'childList' || (mutation.type === 'attributes' && mutation.attributeName === 'class');
        });
        if (relevant) { scheduleRefresh(60); }
    });
    observer.observe($sections.get(0), { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    if ($inspectorTarget.length) {
        observer.observe($inspectorTarget.get(0), { childList: true, subtree: true });
    }

    // Register canonical fields before legacy admin.js records its initial history entry.
    applyAll();
    scheduleRefresh(90);

    document.documentElement.setAttribute('data-h18-lego-spacing-runtime', '0.8.30');
    window.__h18LegoSpacingV0830 = {
        version: '0.8.30',
        stateForKey: function (key) {
            const $row = activeRows().filter(function () { return rowKey($(this)) === String(key || ''); }).first();
            return $row.length ? stateForRow($row) : null;
        },
        hasCanonicalField: function (key) {
            const $row = activeRows().filter(function () { return rowKey($(this)) === String(key || ''); }).first();
            return $row.length ? canonicalField($row).length === 1 : false;
        }
    };
});
