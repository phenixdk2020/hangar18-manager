jQuery(function ($) {
    'use strict';

    const config = window.H18LegoSpacingV0831 || {};
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
    const tabletMax = Math.max(0, parseInt(config.limits && config.limits.tablet, 10) || 160);
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

    function boolValue(value, fallback) {
        if (typeof value === 'boolean') { return value; }
        if (value === null || typeof value === 'undefined' || value === '') { return fallback; }
        if (typeof value === 'number') { return value !== 0; }
        return ['1', 'true', 'yes', 'on'].indexOf(String(value).toLowerCase().trim()) !== -1;
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
            SchemaVersion: 2,
            Desktop: {
                Margin: { X: 0, Y: 0 },
                Gap: { X: desktopGap, Y: desktopGap }
            },
            Tablet: {
                InheritDesktop: true,
                Margin: { X: 0, Y: 0 },
                Gap: { X: desktopGap, Y: desktopGap }
            },
            Mobile: {
                InheritDesktop: false,
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
        const tablet = raw.Tablet && typeof raw.Tablet === 'object' ? raw.Tablet : {};
        const mobile = raw.Mobile && typeof raw.Mobile === 'object' ? raw.Mobile : {};
        const normalizedDesktop = {
            Margin: normalizePair(desktop.Margin, desktopMax, fallback.Desktop.Margin),
            Gap: normalizePair(desktop.Gap, desktopMax, fallback.Desktop.Gap)
        };

        return {
            SchemaVersion: 2,
            Desktop: normalizedDesktop,
            Tablet: {
                InheritDesktop: Object.prototype.hasOwnProperty.call(tablet, 'InheritDesktop')
                    ? boolValue(tablet.InheritDesktop, true)
                    : true,
                Margin: normalizePair(tablet.Margin, tabletMax, normalizedDesktop.Margin),
                Gap: normalizePair(tablet.Gap, tabletMax, normalizedDesktop.Gap)
            },
            // v0.8.30/schema-1 Mobile values were explicit. Missing inheritance
            // therefore means override, preserving the existing visual result.
            Mobile: {
                InheritDesktop: Object.prototype.hasOwnProperty.call(mobile, 'InheritDesktop')
                    ? boolValue(mobile.InheritDesktop, false)
                    : false,
                Margin: normalizePair(mobile.Margin, mobileMax, fallback.Mobile.Margin),
                Gap: normalizePair(mobile.Gap, mobileMax, fallback.Mobile.Gap)
            }
        };
    }

    function effectiveDevice(state, device) {
        if (device === 'Desktop') {
            return { Margin: state.Desktop.Margin, Gap: state.Desktop.Gap, Inherited: false };
        }
        const requested = state[device] || {};
        if (requested.InheritDesktop) {
            return { Margin: state.Desktop.Margin, Gap: state.Desktop.Gap, Inherited: true };
        }
        return { Margin: requested.Margin, Gap: requested.Gap, Inherited: false };
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

    function setDeviceVars(node, prefix, state) {
        node.style.setProperty('--h18-lego-' + prefix + 'margin-x', state.Margin.X + 'px');
        node.style.setProperty('--h18-lego-' + prefix + 'margin-y', state.Margin.Y + 'px');
        node.style.setProperty('--h18-lego-' + prefix + 'gap-x', state.Gap.X + 'px');
        node.style.setProperty('--h18-lego-' + prefix + 'gap-y', state.Gap.Y + 'px');
    }

    function writeState($row, state, captureHistory) {
        state = normalizeState($row, state);
        const $field = ensureCanonicalField($row, state);
        $field.val(JSON.stringify(state));

        const desktop = effectiveDevice(state, 'Desktop');
        const tablet = effectiveDevice(state, 'Tablet');
        const mobile = effectiveDevice(state, 'Mobile');
        const node = $row.get(0);
        if (node) {
            // Keep v0.8.30 desktop/mobile variable names stable for compatibility.
            setDeviceVars(node, '', desktop);
            setDeviceVars(node, 'tablet-', tablet);
            setDeviceVars(node, 'mobile-', mobile);
        }
        $row.attr('data-h18-lego-spacing', '1');
        $row.attr('data-h18-lego-tablet-inherit', state.Tablet.InheritDesktop ? '1' : '0');
        $row.attr('data-h18-lego-mobile-inherit', state.Mobile.InheritDesktop ? '1' : '0');

        if (captureHistory) {
            // Existing admin.js delegated form listener owns the checkpoint.
            // Exactly one canonical hidden-field input is emitted per control edit.
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

    function deviceDisplayValue(state, device, kind, axis) {
        const effective = effectiveDevice(state, device);
        return effective[kind] && typeof effective[kind][axis] !== 'undefined'
            ? effective[kind][axis]
            : 0;
    }

    function numberControl(label, path, value, max, help, disabled) {
        const $label = $('<label>', { class: 'h18-ud-lego-control' });
        $label.append($('<strong>', { text: label }));
        $label.append(
            $('<span>', { class: 'h18-ud-lego-number' }).append(
                $('<input>', {
                    type: 'number', min: 0, max: max, step: 1,
                    value: value,
                    disabled: Boolean(disabled),
                    'data-h18-lego-path': path
                }),
                $('<em>', { text: 'px' })
            )
        );
        if (help) { $label.append($('<small>', { text: help })); }
        return $label;
    }

    function inheritanceControl(device, inherited) {
        return $('<label>', { class: 'h18-ud-lego-inherit' }).append(
            $('<input>', {
                type: 'checkbox',
                checked: Boolean(inherited),
                'data-h18-lego-inherit-device': device
            }),
            $('<span>', { text: 'Arv fra Desktop' })
        );
    }

    function deviceGroup(title, device, state, layout) {
        const max = device === 'Mobile' ? mobileMax : (device === 'Tablet' ? tabletMax : desktopMax);
        const inherited = device !== 'Desktop' && Boolean(state[device].InheritDesktop);
        const $group = $('<fieldset>', {
            class: 'h18-ud-lego-device' + (inherited ? ' is-inherited' : ''),
            'data-h18-lego-device': device
        });
        $group.append($('<legend>', { text: title }));
        if (device !== 'Desktop') {
            $group.append(
                inheritanceControl(device, inherited),
                $('<p>', {
                    class: 'h18-ud-lego-inherit-status description',
                    text: inherited
                        ? 'Aktive værdier følger Desktop. De tidligere override-værdier bevares.'
                        : 'Egne værdier er aktive på ' + title.toLowerCase() + '.'
                })
            );
        }

        const $grid = $('<div>', { class: 'h18-ud-lego-grid' });
        $grid.append(
            numberControl(
                'Element X',
                device + '.Margin.X',
                deviceDisplayValue(state, device, 'Margin', 'X'),
                max,
                inherited ? 'Arvet fra Desktop' : 'Venstre + højre',
                inherited
            ),
            numberControl(
                'Element Y',
                device + '.Margin.Y',
                deviceDisplayValue(state, device, 'Margin', 'Y'),
                max,
                inherited ? 'Arvet fra Desktop' : 'Over + under',
                inherited
            )
        );
        if (layout) {
            $grid.append(
                numberControl(
                    'Indhold X',
                    device + '.Gap.X',
                    deviceDisplayValue(state, device, 'Gap', 'X'),
                    max,
                    inherited ? 'Arvet fra Desktop' : 'Mellem kolonner/klodser',
                    inherited
                ),
                numberControl(
                    'Indhold Y',
                    device + '.Gap.Y',
                    deviceDisplayValue(state, device, 'Gap', 'Y'),
                    max,
                    inherited ? 'Arvet fra Desktop' : 'Mellem rækker/klodser',
                    inherited
                )
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
                    $('<p>', {
                        class: 'description',
                        text: 'Desktop er basis. Tablet og Mobil kan arve Desktop eller bruge egne X/Y-overrides.'
                    })
                ),
                $('<span>', { class: 'h18-ud-lego-badge', text: '0.8.31' })
            ),
            deviceGroup('Desktop', 'Desktop', state, layout),
            deviceGroup('Tablet', 'Tablet', state, layout),
            deviceGroup('Mobil', 'Mobile', state, layout)
        );
        if (layout) {
            $panel.append($('<p>', {
                class: 'description h18-ud-lego-note',
                text: 'Indhold X/Y er Kasse/Grid/Flex-afstanden mellem klodser. v0.8.30 Mobile-overrides bevares ved opgradering; Tablet starter med arv fra Desktop.'
            }));
        }
        $inspector.append($panel);
    }

    function syncInheritedPanel(state) {
        ['Tablet', 'Mobile'].forEach(function (device) {
            if (!state[device] || !state[device].InheritDesktop) { return; }
            ['Margin', 'Gap'].forEach(function (kind) {
                ['X', 'Y'].forEach(function (axis) {
                    $('#' + PANEL_ID + ' [data-h18-lego-path="' + device + '.' + kind + '.' + axis + '"]')
                        .val(deviceDisplayValue(state, device, kind, axis));
                });
            });
        });
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

    $(document).on('input', '#' + PANEL_ID + ' [data-h18-lego-path]', function () {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const path = String($(this).attr('data-h18-lego-path') || '');
        if (!/^(Desktop|Tablet|Mobile)\.(Margin|Gap)\.(X|Y)$/.test(path)) { return; }
        const state = stateForRow($row);
        const device = path.split('.')[0];
        if (device !== 'Desktop' && state[device] && state[device].InheritDesktop) { return; }
        const max = device === 'Mobile' ? mobileMax : (device === 'Tablet' ? tabletMax : desktopMax);
        const current = parseInt(valueAt(state, path), 10) || 0;
        setAt(state, path, clamp($(this).val(), max, current));
        const written = writeState($row, state, true);
        if (device === 'Desktop') { syncInheritedPanel(written); }
    });

    $(document).on('change', '#' + PANEL_ID + ' [data-h18-lego-inherit-device]', function () {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const device = String($(this).attr('data-h18-lego-inherit-device') || '');
        if (device !== 'Tablet' && device !== 'Mobile') { return; }
        const state = stateForRow($row);
        state[device].InheritDesktop = $(this).is(':checked');
        writeState($row, state, true);
        renderPanel();
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

    $form.on('submit.h18LegoSpacingV0831', appendSavePayload);

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

    // Register/migrate canonical fields before legacy admin.js records its initial history entry.
    applyAll();
    scheduleRefresh(90);

    document.documentElement.setAttribute('data-h18-lego-spacing-runtime', '0.8.31');
    window.__h18LegoSpacingV0831 = {
        version: '0.8.31',
        stateForKey: function (key) {
            const $row = activeRows().filter(function () { return rowKey($(this)) === String(key || ''); }).first();
            return $row.length ? stateForRow($row) : null;
        },
        effectiveForKey: function (key, device) {
            const $row = activeRows().filter(function () { return rowKey($(this)) === String(key || ''); }).first();
            if (!$row.length) { return null; }
            const normalizedDevice = ['Desktop', 'Tablet', 'Mobile'].indexOf(String(device || '')) !== -1
                ? String(device)
                : 'Desktop';
            return effectiveDevice(stateForRow($row), normalizedDevice);
        },
        hasCanonicalField: function (key) {
            const $row = activeRows().filter(function () { return rowKey($(this)) === String(key || ''); }).first();
            return $row.length ? canonicalField($row).length === 1 : false;
        }
    };
});
