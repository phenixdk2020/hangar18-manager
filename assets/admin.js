jQuery(function ($) {
    'use strict';

    function openSingleMedia(prefix) {
        const frame = wp.media({
            title: Hangar18Manager.chooseImage,
            button: { text: Hangar18Manager.useImage },
            multiple: false,
            library: { type: 'image' }
        });

        frame.on('select', function () {
            const a = frame.state().get('selection').first().toJSON();
            const preview = a.sizes && a.sizes.medium ? a.sizes.medium.url : a.url;

            $('#h18-' + prefix + '-media-id').val(a.id || '');
            $('#h18-' + prefix + '-media-url').val(a.url || '');
            $('#h18-' + prefix + '-media-preview').html(
                $('<img>', { src: preview, alt: a.alt || '' })
            );
        });

        frame.open();
    }

    $('.h18-select-media').on('click', function (event) {
        event.preventDefault();
        openSingleMedia($(this).data('media-prefix') || 'main');
    });

    $('.h18-remove-media').on('click', function (event) {
        event.preventDefault();
        const prefix = $(this).data('media-prefix') || 'main';
        $('#h18-' + prefix + '-media-id').val('');
        $('#h18-' + prefix + '-media-url').val('');
        $('#h18-' + prefix + '-media-preview').html('<span>Intet hovedbillede valgt</span>');
    });

    function slugify(value) {
        return String(value || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/æ/g, 'ae')
            .replace(/ø/g, 'oe')
            .replace(/å/g, 'aa')
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }

    $('#h18-name, #h18-event_name, #h18-album_name').on('blur', function () {
        const $slug = $('#h18-slug');
        if ($slug.length && !$slug.val().trim()) {
            $slug.val(slugify($(this).val()));
        }
    });

    const $sortable = $('#h18-gallery-sortable');
    const $json = $('#h18-gallery-items-json');
    const $count = $('#h18-gallery-count');
    const $empty = $('#h18-gallery-empty');

    function galleryItemsFromDom() {
        const items = [];

        $sortable.children('.h18-gallery-admin-item').each(function (index) {
            const $item = $(this);
            items.push({
                MediaId: parseInt($item.data('id'), 10) || 0,
                Url: String($item.data('url') || ''),
                Title: String($item.data('title') || ''),
                Description: '',
                Order: index + 1
            });
        });

        $json.val(JSON.stringify(items));
        $count.text(items.length);
        $empty.toggle(items.length === 0);
    }

    if ($sortable.length) {
        $sortable.sortable({
            handle: '.h18-drag-handle',
            tolerance: 'pointer',
            update: galleryItemsFromDom
        });

        galleryItemsFromDom();
    }

    $('#h18-gallery-add').on('click', function (event) {
        event.preventDefault();

        const frame = wp.media({
            title: Hangar18Manager.chooseGallery,
            button: { text: Hangar18Manager.useGallery },
            multiple: true,
            library: { type: 'image' }
        });

        frame.on('select', function () {
            frame.state().get('selection').each(function (attachmentModel) {
                const a = attachmentModel.toJSON();
                const exists = $sortable.children('[data-id="' + a.id + '"]').length > 0;

                if (exists) {
                    return;
                }

                const thumb = a.sizes && a.sizes.thumbnail ? a.sizes.thumbnail.url : a.url;

                const $item = $('<div>', {
                    class: 'h18-gallery-admin-item',
                    'data-id': a.id,
                    'data-url': a.url,
                    'data-title': a.title || ''
                });

                $item.append($('<span>', { class: 'dashicons dashicons-move h18-drag-handle' }));
                $item.append($('<img>', { src: thumb, alt: a.alt || '' }));
                $item.append($('<div>', { class: 'h18-gallery-admin-title', text: a.title || ('Billede ' + a.id) }));
                $item.append($('<button>', {
                    type: 'button',
                    class: 'button-link-delete h18-gallery-remove',
                    text: Hangar18Manager.removeImage
                }));

                $sortable.append($item);
            });

            galleryItemsFromDom();
        });

        frame.open();
    });

    $(document).on('click', '.h18-gallery-remove', function (event) {
        event.preventDefault();
        $(this).closest('.h18-gallery-admin-item').remove();
        galleryItemsFromDom();
    });

    const $menuSortable = $('#h18-menu-sortable');
    const $menuJson = $('#h18-menu-items-json');

    function syncMenuJson() {
        if (!$menuSortable.length || !$menuJson.length) {
            return;
        }

        const rows = [];

        $menuSortable.children('.h18-menu-admin-item').each(function () {
            const $row = $(this);

            rows.push({
                id: parseInt($row.data('id'), 10) || 0,
                title: String($row.find('.h18-menu-title-input').val() || ''),
                parent: parseInt($row.find('.h18-menu-parent-select').val(), 10) || 0,
                remove: String($row.attr('data-remove') || '0') === '1'
            });
        });

        $menuJson.val(JSON.stringify(rows));
    }

    if ($menuSortable.length) {
        $menuSortable.sortable({
            handle: '.h18-menu-drag-handle',
            tolerance: 'pointer',
            update: syncMenuJson
        });

        syncMenuJson();
    }

    $(document).on(
        'input change',
        '.h18-menu-title-input, .h18-menu-parent-select',
        syncMenuJson
    );

    $(document).on('click', '.h18-menu-remove', function (event) {
        event.preventDefault();

        const $row = $(this).closest('.h18-menu-admin-item');
        const removing = String($row.attr('data-remove') || '0') !== '1';

        $row.attr('data-remove', removing ? '1' : '0');
        $row.toggleClass('h18-menu-admin-item-removed', removing);
        $(this).text(removing ? 'Fortryd fjernelse' : 'Fjern');

        syncMenuJson();
    });



    const $vehicleFieldSortable = $('#h18-vehicle-fields-sortable');

    function syncVehicleFieldOrder() {
        if (!$vehicleFieldSortable.length) {
            return;
        }

        $vehicleFieldSortable.children('.h18-vehicle-field-row').each(function (index) {
            $(this).find('.h18-vehicle-field-order').val((index + 1) * 10);
        });
    }

    if ($vehicleFieldSortable.length) {
        $vehicleFieldSortable.sortable({
            items: '> tr.h18-vehicle-field-row',
            handle: '.h18-vehicle-field-drag-handle',
            axis: 'y',
            tolerance: 'pointer',
            helper: function (event, row) {
                const originals = row.children();
                const helper = row.clone();
                helper.children().each(function (index) {
                    $(this).width(originals.eq(index).width());
                });
                return helper;
            },
            update: syncVehicleFieldOrder
        });
        syncVehicleFieldOrder();
    }

    $('#h18-new-vehicle-field-label').on('blur', function () {
        const $key = $('#h18-new-vehicle-field-key');
        if ($key.length && !$key.val().trim()) {
            $key.val(slugify($(this).val()).replace(/-/g, '_'));
        }
    });

    const $staticSections = $('#h18-static-sections-sortable');

    function syncStaticSectionOrder() {
        if (!$staticSections.length) {
            return;
        }

        $staticSections.children('.h18-static-section-row').each(function (index) {
            $(this).find('.h18-static-section-order').val((index + 1) * 10);
        });
    }

    if ($staticSections.length) {
        $staticSections.sortable({
            items: '> .h18-static-section-row',
            handle: '.h18-static-section-drag',
            axis: 'y',
            tolerance: 'pointer',
            update: syncStaticSectionOrder
        });
        syncStaticSectionOrder();
    }

    const $pageSections = $('#h18-page-sections-sortable');
    const pageSectionTemplate = document.getElementById('h18-page-section-template');
    const pageCardTemplate = document.getElementById('h18-page-card-template');
    const $pageInspector = $('#h18-page-inspector');
    const $pageInspectorTarget = $('#h18-page-inspector-target');
    const $pageInspectorAdvanced = $('#h18-inspector-advanced-panel');
    const $pageNavigatorList = $('#h18-page-navigator-list');
    const $pageNavigatorCount = $('#h18-page-navigator-count');
    const $pageUserPresetsList = $('#h18-user-presets-list');
    const $pageLinkedComponentsList = $('#h18-linked-components-list');
    const $pageTemplatesList = $('#h18-page-templates-list');
    let pageSectionNextIndex = 0;
    let pageCardSerial = 0;
    let $inspectedSection = $();
    let currentInspectorPanel = 'content';
    const pageUserPresets = {};
    const pageLinkedComponents = {};
    const pageTemplatesV0522 = {};
    let navigatorLockedOrderSnapshotV0521 = null;
    let currentCanvasDevice = 'desktop';
    let currentCanvasState = 'normal';
    let selectedCanvasCardKey = '';
    const multiSelectedSectionKeys = new Set();
    let canvasZoomPercentV0515 = 100;
    let canvasOutlineModeV0515 = false;
    let canvasGuideModeV0515 = false;
    const canvasWorkspaceStorageKeyV0515 = 'hangar18CanvasWorkspaceV0515';
    let contextMenuRowV0515 = $();
    let contextMenuReturnFocusV0515 = null;
    const sectionDesignClipboardStorageKey = 'hangar18SectionDesignClipboardV0511';
    let sectionDesignClipboard = null;
    try {
        const storedDesignClipboard = window.localStorage ? window.localStorage.getItem(sectionDesignClipboardStorageKey) : '';
        const parsedDesignClipboard = storedDesignClipboard ? JSON.parse(storedDesignClipboard) : null;
        if (parsedDesignClipboard && parsedDesignClipboard.Fields && typeof parsedDesignClipboard.Fields === 'object') { sectionDesignClipboard = parsedDesignClipboard; }
    } catch (designClipboardError) {
        sectionDesignClipboard = null;
    }

    try {
        const presetNode = document.getElementById('h18-page-presets-data');
        const parsedPresets = presetNode ? JSON.parse(presetNode.textContent || '[]') : [];
        (Array.isArray(parsedPresets) ? parsedPresets : []).forEach(function (preset) {
            if (preset && preset.Id) {
                pageUserPresets[String(preset.Id)] = preset;
            }
        });
    } catch (presetError) {
        window.console && console.warn('Hangar18: kunne ikke læse pattern-bibliotek.', presetError);
    }
    try {
        const componentNode = document.getElementById('h18-page-components-data');
        const parsedComponents = componentNode ? JSON.parse(componentNode.textContent || '[]') : [];
        (Array.isArray(parsedComponents) ? parsedComponents : []).forEach(function (component) {
            if (component && component.Id) { pageLinkedComponents[String(component.Id)] = component; }
        });
    } catch (componentError) {
        window.console && console.warn('Hangar18: kunne ikke læse linked component-bibliotek.', componentError);
    }
    try {
        const templateNode = document.getElementById('h18-page-templates-data');
        const parsedTemplates = templateNode ? JSON.parse(templateNode.textContent || '[]') : [];
        (Array.isArray(parsedTemplates) ? parsedTemplates : []).forEach(function(template){ if(template&&template.Id) pageTemplatesV0522[String(template.Id)]=template; });
    } catch(templateError){ window.console&&console.warn('Hangar18: kunne ikke læse Page Templates.',templateError); }

    const builtInSectionPresets = {
        'hero-cta': { Type: 'hero', Title: 'Velkommen', Content: '<p>Skriv en kort introduktion, der fortæller hvad siden handler om.</p>', Background: 'Olive', DesktopAlignment: 'Center', MobileAlignment: 'Center', PaddingPx: 36, MobilePaddingPx: 22, HeroHeightPx: 320, MobileHeroHeightPx: 220, OverlayOpacityPercent: 35, Button1Label: 'Læs mere', Button1Url: '#', Active: true },
        'text-image': { Type: 'text_image', Title: 'Overskrift', Content: '<p>Fortæl historien her. Vælg derefter et billede i Inspector.</p>', Background: 'White', ImagePosition: 'Right', DesktopAlignment: 'Left', MobileAlignment: 'Left', Active: true },
        'info-cards': { Type: 'card_grid', Title: 'Kort fortalt', Content: '', Background: 'White', Columns: 3, MobileColumns: 1, ColumnGapPx: 16, MobileColumnGapPx: 14, Active: true, Cards: [ { Title: 'Punkt 1', Content: '<p>Beskrivelse af det første punkt.</p>', Background: 'OffWhite', TextTone: 'Auto', Active: true }, { Title: 'Punkt 2', Content: '<p>Beskrivelse af det andet punkt.</p>', Background: 'Sand', TextTone: 'Auto', Active: true }, { Title: 'Punkt 3', Content: '<p>Beskrivelse af det tredje punkt.</p>', Background: 'Steel', TextTone: 'Auto', Active: true } ] },
        'cta-band': { Type: 'buttons', Title: 'Klar til næste skridt?', Content: '<p>Brug sektionen til en tydelig handling.</p>', Background: 'OffWhite', DesktopAlignment: 'Center', MobileAlignment: 'Center', PaddingPx: 24, MobilePaddingPx: 18, Button1Label: 'Læs mere', Button1Url: '#', Active: true },
        'contact-form': { Type: 'mail_form', Title: 'Kontakt os', Content: '<p>Send os en besked, så vender vi tilbage hurtigst muligt.</p>', Background: 'OffWhite', PaddingPx: 26, MobilePaddingPx: 20, Active: true }
    };

    $pageSections.children('.h18-page-section-row').each(function () {
        const value = parseInt($(this).attr('data-section-index'), 10);
        if (!Number.isNaN(value)) {
            pageSectionNextIndex = Math.max(pageSectionNextIndex, value + 1);
        }
    });

    function newSectionKey() {
        return 'sektion-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 9);
    }

    function newCardKey() {
        pageCardSerial += 1;
        return 'kort-' + Date.now().toString(36) + '-' + pageCardSerial.toString(36) + '-' + Math.random().toString(36).slice(2, 7);
    }


    function inspectorTypeLabel(type) {
        const labels = {
            hero: 'Topbanner / hero', text: 'Tekst', text_image: 'Tekst og billede', image: 'Stort billede',
            buttons: 'Handlingsknapper', card: 'Indholdskort', card_grid: 'Kort-række / kolonner', highlight: 'Fremhævet tekst',
            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', container: 'Container', flex: 'Flex container', grid: 'Grid container', component: 'Linked component', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',
            spacer: 'Afstand', html: 'Importeret blok / HTML', css: 'Side-CSS', mail_form: 'Mailformular', poll: 'Afstemning', legacy: 'Eksisterende indhold'
        };
        return labels[String(type || '')] || 'Sektion';
    }

    const primitiveVariantOptionsV0516 = {
        icon: { check: 'Flueben', star: 'Stjerne', info: 'Info', location: 'Placering', calendar: 'Kalender', phone: 'Telefon', mail: 'E-mail', wrench: 'Værktøj', shield: 'Skjold', arrow: 'Pil' },
        divider: { solid: 'Hel linje', dashed: 'Stiplet', dotted: 'Prikket', double: 'Dobbelt' },
        list: { bullets: 'Punkter', numbers: 'Numre', checks: 'Flueben' },
        badge: { solid: 'Fyldt', outline: 'Outline' },
        quote: { standard: 'Standard', large: 'Stort citat' }
    };

    function refreshPrimitiveVariantV0516($row) {
        if (!$row || !$row.length) { return; }
        const type = String($row.attr('data-section-type') || 'text');
        const options = primitiveVariantOptionsV0516[type];
        const $select = pageSectionControls($row, '.h18-primitive-variant').first();
        if (!$select.length || !options) { return; }
        const current = String($select.val() || '');
        $select.empty();
        Object.keys(options).forEach(function (value) {
            $select.append($('<option>', { value: value, text: options[value] }));
        });
        $select.val(Object.prototype.hasOwnProperty.call(options, current) ? current : Object.keys(options)[0]);
    }

    function setInspectorPanel(panel) {
        panel = ['content', 'design', 'advanced'].includes(String(panel)) ? String(panel) : 'content';
        currentInspectorPanel = panel;
        $pageInspector.attr('data-inspector-panel', panel);
        $pageInspector.find('.h18-inspector-tab').removeClass('is-active').filter('[data-inspector-tab="' + panel + '"]').addClass('is-active');
    }

    function refreshInspectorMeta($row) {
        const hasRow = $row && $row.length && !$row.hasClass('h18-page-section-removed');
        const type = hasRow ? String($row.attr('data-section-type') || 'text') : '';
        const key = hasRow ? String($row.find('.h18-page-section-key').val() || '') : '';
        $('#h18-inspector-type').text(hasRow ? inspectorTypeLabel(type) : '–');
        $('#h18-inspector-key').text(key || '–');
        $('#h18-inspector-copy-key, #h18-inspector-duplicate, #h18-inspector-copy-design, #h18-save-section-preset').prop('disabled', !hasRow || type === 'legacy');
        $('#h18-inspector-paste-design').prop('disabled', !hasRow || type === 'legacy' || !sectionDesignClipboard);
        if (hasRow && type === 'legacy') {
            $('#h18-inspector-copy-key').prop('disabled', false);
        }
    }

    function rebuildPageNavigator() {
        if (!$pageNavigatorList.length || !$pageSections.length) {
            return;
        }
        if ($pageNavigatorList.hasClass('ui-sortable')) {
            $pageNavigatorList.sortable('destroy');
        }
        $pageNavigatorList.empty();
        let count = 0;
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const $row = $(this);
            const index = String($row.attr('data-section-index') || '');
            const type = String($row.attr('data-section-type') || 'text');
            const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim();
            const navigatorLabel = String(pageSectionControls($row, '.h18-section-navigator-label').val() || '').trim();
            const active = $row.find('.h18-section-active').is(':checked');
            const locked = String(pageSectionControls($row, '.h18-section-navigator-locked').val() || '0') === '1';
            $row.toggleClass('is-navigator-locked', locked);
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
            const sectionKeyV0515 = String($row.find('.h18-page-section-key').val() || '');
            const multiSelectedV0515 = sectionKeyV0515 && multiSelectedSectionKeys.has(sectionKeyV0515);
            const $item = $('<div>', { class: 'h18-navigator-item' + (selected ? ' is-selected' : '') + (multiSelectedV0515 ? ' is-multi-selected' : '') + (locked ? ' is-locked' : ''), 'data-section-index': index, 'data-section-key': sectionKeyV0515 });
            $item.append($('<span>', { class: 'dashicons ' + (locked ? 'dashicons-lock' : 'dashicons-menu') + ' h18-navigator-drag', title: locked ? 'Låst lag' : 'Flyt lag' }));
            const $button = $('<button>', { type: 'button', class: 'h18-navigator-select' });
            $button.append($('<strong>', { text: navigatorLabel || inspectorTypeLabel(type) }));
            $button.append($('<small>', { text: title || inspectorTypeLabel(type) }));
            $item.append($button);
            $item.append($('<button>', { type: 'button', class: 'h18-navigator-tool h18-navigator-rename', title: 'Omdøb lag', 'aria-label': 'Omdøb lag' }).append($('<span>', { class: 'dashicons dashicons-edit' })));
            $item.append($('<button>', { type: 'button', class: 'h18-navigator-tool h18-navigator-toggle-lock', title: locked ? 'Lås op' : 'Lås', 'aria-label': locked ? 'Lås op' : 'Lås' }).append($('<span>', { class: 'dashicons ' + (locked ? 'dashicons-lock' : 'dashicons-unlock') })));
            $item.append($('<button>', { type: 'button', class: 'h18-navigator-tool h18-navigator-toggle-visibility ' + (active ? 'is-visible' : 'is-hidden'), title: active ? 'Skjul' : 'Vis', 'aria-label': active ? 'Skjul' : 'Vis' }).append($('<span>', { class: 'dashicons ' + (active ? 'dashicons-visibility' : 'dashicons-hidden') })));
            $pageNavigatorList.append($item);
            count += 1;
        });
        $pageNavigatorCount.text(count);
        if (count > 1) {
            $pageNavigatorList.sortable({
                items: '> .h18-navigator-item', handle: '.h18-navigator-drag', axis: 'y', tolerance: 'pointer',
                start: function (event, ui) {
                    if (ui.item.hasClass('is-locked')) { $(this).sortable('cancel'); return false; }
                    navigatorLockedOrderSnapshotV0521 = {};
                    $pageNavigatorList.children('.h18-navigator-item.is-locked').each(function (lockedIndex) { navigatorLockedOrderSnapshotV0521[String($(this).attr('data-section-key') || '')] = $(this).index(); });
                },
                update: function () {
                    let lockedMoved = false;
                    if (navigatorLockedOrderSnapshotV0521) {
                        $pageNavigatorList.children('.h18-navigator-item.is-locked').each(function () {
                            const key = String($(this).attr('data-section-key') || '');
                            if (Object.prototype.hasOwnProperty.call(navigatorLockedOrderSnapshotV0521, key) && navigatorLockedOrderSnapshotV0521[key] !== $(this).index()) { lockedMoved = true; }
                        });
                    }
                    if (lockedMoved) { $(this).sortable('cancel'); navigatorLockedOrderSnapshotV0521 = null; return; }
                    navigatorLockedOrderSnapshotV0521 = null;
                    const orderedRows = [];
                    $pageNavigatorList.children('.h18-navigator-item').each(function () {
                        const index = String($(this).attr('data-section-index') || '');
                        const $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
                        if ($row.length) {
                            orderedRows.push($row);
                        }
                    });
                    orderedRows.forEach(function ($row) { $pageSections.append($row); });
                    $pageSections.children('.h18-page-section-row.h18-page-section-removed').appendTo($pageSections);
                    syncPageSectionOrder(true);
                    window.setTimeout(rebuildPageNavigator, 0);
                }
            });
        }
    }


    function navigatorRowV0521($item) {
        const index = String($item.attr('data-section-index') || '');
        return $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
    }

    function rowLockedV0521($row) {
        return String(pageSectionControls($row, '.h18-section-navigator-locked').val() || '0') === '1';
    }

    $(document).on('click', '.h18-navigator-rename', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = navigatorRowV0521($(this).closest('.h18-navigator-item'));
        if (!$row.length) { return; }
        const current = String(pageSectionControls($row, '.h18-section-navigator-label').val() || '');
        const value = window.prompt('Navn i Navigator (tomt = brug elementtype):', current);
        if (value === null) { return; }
        pageSectionControls($row, '.h18-section-navigator-label').val(String(value).trim().slice(0,80)).trigger('change');
        rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });

    $(document).on('click', '.h18-navigator-toggle-lock', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = navigatorRowV0521($(this).closest('.h18-navigator-item'));
        if (!$row.length) { return; }
        const $field = pageSectionControls($row, '.h18-section-navigator-locked').first();
        $field.val(String($field.val() || '0') === '1' ? '0' : '1').trigger('change');
        rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });

    $(document).on('click', '.h18-navigator-toggle-visibility', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = navigatorRowV0521($(this).closest('.h18-navigator-item'));
        if (!$row.length || rowLockedV0521($row)) { return; }
        const $active = pageSectionControls($row, '.h18-section-active').first();
        $active.prop('checked', !$active.is(':checked')).trigger('change');
        renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });

    function renderUserPresets() {
        if (!$pageUserPresetsList.length) {
            return;
        }
        const presets = Object.values(pageUserPresets).sort(function (a, b) { return String(a.Name || '').localeCompare(String(b.Name || ''), 'da'); });
        $pageUserPresetsList.empty();
        if (!presets.length) {
            $pageUserPresetsList.html('<p class="description">Vælg en sektion og brug “Gem som pattern” i Inspector.</p>');
            return;
        }
        presets.forEach(function (preset) {
            const patternSections = Array.isArray(preset.Sections) ? preset.Sections : (preset.Section ? [preset.Section] : []);
            const firstSection = patternSections.length ? patternSections[0] : null;
            const $row = $('<div>', { class: 'h18-user-preset-row', 'data-preset-id': String(preset.Id) });
            $row.append($('<button>', { type: 'button', class: 'h18-user-preset-insert' }).append($('<strong>', { text: String(preset.Name || 'Pattern') })).append($('<small>', { text: (firstSection ? inspectorTypeLabel(firstSection.Type) : 'Pattern') + ' · ' + patternSections.length + ' element(er)' })));
            $row.append($('<button>', { type: 'button', class: 'h18-user-preset-delete', title: 'Slet komponent', 'aria-label': 'Slet komponent' }).append($('<span>', { class: 'dashicons dashicons-trash' })));
            $pageUserPresetsList.append($row);
        });
    }

    function sectionPresetData($row) {
        if (!$row || !$row.length) {
            return null;
        }
        const data = { Type: String($row.attr('data-section-type') || 'text') };
        if (data.Type === 'component') { return null; }
        const cards = {};
        pageSectionControls($row, '[name]').each(function () {
            const $field = $(this);
            const name = String($field.attr('name') || '');
            let match = name.match(/^sections\[[^\]]+\]\[Cards\]\[([^\]]+)\]\[([^\]]+)\]$/);
            const value = $field.is(':checkbox') ? $field.is(':checked') : $field.val();
            if (match) {
                const cardIndex = String(match[1]);
                const fieldName = String(match[2]);
                if (['Key', 'Order', 'Remove'].includes(fieldName)) {
                    return;
                }
                cards[cardIndex] = cards[cardIndex] || {};
                cards[cardIndex][fieldName] = value;
                return;
            }
            match = name.match(/^sections\[[^\]]+\]\[([^\]]+)\]$/);
            if (!match) {
                return;
            }
            const fieldName = String(match[1]);
            if (['Key', 'Order', 'Remove', 'ResetVotes', 'LayoutParentKey', 'NavigatorLabel', 'NavigatorLocked', 'ComponentId', 'ComponentRevision', 'ComponentOverridesJson'].includes(fieldName)) {
                return;
            }
            data[fieldName] = value;
        });
        data.Cards = Object.keys(cards).sort(function (a, b) { return Number(a) - Number(b); }).map(function (index) { return cards[index]; });
        return data;
    }

    function setSectionPresetField($row, fieldName, value) {
        const sectionIndex = String($row.attr('data-section-index') || '');
        pageSectionControls($row, '[name]').filter(function () {
            return String($(this).attr('name') || '') === 'sections[' + sectionIndex + '][' + fieldName + ']';
        }).each(function () {
            const $field = $(this);
            if ($field.is(':checkbox')) {
                $field.prop('checked', Boolean(value));
            } else {
                $field.val(value == null ? '' : value);
            }
        });
    }

    function setSectionTitleSummary($row) {
        const title = String(pageSectionControls($row, '.h18-section-title-input').val() || '');
        $row.find('.h18-page-section-title-summary').text(title);
        return title;
    }

    function applySectionPreset(presetData) {
        if (!presetData || typeof presetData !== 'object') {
            return $();
        }
        const type = String(presetData.Type || 'text');
        const $row = addPageSection(type);
        if (!$row.length) {
            return $row;
        }
        Object.keys(presetData).forEach(function (fieldName) {
            if (['Type', 'Cards', 'Key', 'Order', 'Remove', 'LayoutParentKey'].includes(fieldName)) {
                return;
            }
            setSectionPresetField($row, fieldName, presetData[fieldName]);
        });
        $row.find('.h18-page-section-type').val(type);
        if (Array.isArray(presetData.Cards) && ['card_grid', 'tabs', 'accordion', 'carousel'].includes(type)) {
            const $container = pageSectionControls($row, '.h18-page-cards-sortable');
            $container.children('.h18-page-card-row').remove();
            presetData.Cards.slice(0, 12).forEach(function (card) { addPageCard($row, card || {}); });
        }
        refreshPageSectionType($row);
        setSectionTitleSummary($row);
        syncPageSectionOrder();
        inspectPageSection($row);
        return $row;
    }



    function applyPatternV0522(preset) {
        const sections = Array.isArray(preset && preset.Sections) ? preset.Sections : (preset && preset.Section ? [preset.Section] : []);
        if (!sections.length) { return $(); }
        const keyMap = {}; const rows = [];
        sections.forEach(function(section){
            const copy=Object.assign({},section); delete copy.LayoutParentKey; delete copy.Key; delete copy.Order;
            const $row=applySectionPreset(copy); if(!$row.length)return;
            const oldKey=String(section.Key||''); const newKey=String($row.find('.h18-page-section-key').val()||''); if(oldKey)keyMap[oldKey]=newKey; rows.push({row:$row,source:section});
        });
        rows.forEach(function(item){ const oldParent=String(item.source.LayoutParentKey||''); pageSectionControls(item.row,'.h18-layout-parent-key').val(oldParent&&keyMap[oldParent]?keyMap[oldParent]:''); });
        syncPageSectionOrder(); rebuildPageNavigator(); refreshLayoutHierarchyV0519(); refreshAllCanvasPreviews(); if(rows.length)inspectPageSection(rows[0].row); scheduleEditorHistoryCapture(0); return rows.length?rows[0].row:$();
    }

    function componentDefinitionSectionV0521(component, sectionKey) {
        if (!component || !Array.isArray(component.Sections)) { return null; }
        return component.Sections.find(function (section) { return String(section.Key || '') === String(sectionKey || ''); }) || null;
    }

    function componentInputDefaultV0521(component, input, variantId) {
        const section = componentDefinitionSectionV0521(component, input && input.SectionKey);
        if (!section) { return ''; }
        const field = String(input.Field || '');
        let value = section[field] == null ? '' : section[field];
        const variants = component && component.Variants && typeof component.Variants === 'object' ? component.Variants : {};
        const variant = variantId && variants[variantId] ? variants[variantId] : null;
        if (variant && variant.Values && Object.prototype.hasOwnProperty.call(variant.Values, String(input.InputId || ''))) value = variant.Values[String(input.InputId || '')];
        return value;
    }

    function parseComponentOverridesV0521($row) {
        try {
            const raw = String(pageSectionControls($row, '.h18-component-overrides-json').val() || '{}');
            const parsed = JSON.parse(raw);
            return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
        } catch (error) { return {}; }
    }

    function writeComponentOverridesV0521($row, overrides) {
        pageSectionControls($row, '.h18-component-overrides-json').val(JSON.stringify(overrides || {})).trigger('change');
    }

    function renderComponentInstanceEditorV0521($row) {
        if (!$row || !$row.length || String($row.attr('data-section-type') || '') !== 'component') { return; }
        const componentId = String(pageSectionControls($row, '.h18-component-select').val() || '');
        const component = pageLinkedComponents[componentId];
        const $status = pageSectionControls($row, '.h18-component-instance-status').first();
        const $editor = pageSectionControls($row, '.h18-component-overrides-editor').first();
        $editor.empty();
        if (!component) {
            $status.html('<p class="description">Vælg en linked component. Hvis definitionen er slettet, renderes instansen ikke på frontend.</p>');
            return;
        }
        pageSectionControls($row, '.h18-component-revision').val(parseInt(component.Revision,10)||1);
        const $variantSelect = pageSectionControls($row, '.h18-component-variant-select').first();
        const currentVariant = String($variantSelect.val() || '');
        const variants = component.Variants && typeof component.Variants === 'object' ? Object.values(component.Variants) : [];
        $variantSelect.empty().append($('<option>',{value:'',text:'Base'})); variants.forEach(function(variant){$variantSelect.append($('<option>',{value:String(variant.Id),text:String(variant.Name||'Variant')}));});
        $variantSelect.val(variants.some(function(v){return String(v.Id)===currentVariant;})?currentVariant:'');
        const activeVariant = String($variantSelect.val() || '');
        const usage = parseInt(component.UsageCount,10)||0;
        $status.empty().append($('<p>', { class: 'h18-component-status-line' }).append($('<strong>', { text: String(component.Name || 'Linked component') }), $('<span>', { text: 'Revision ' + String(component.Revision || 1) + ' · bruges ' + usage + ' sted(er)' })));
        const overrides = parseComponentOverridesV0521($row);
        const inputs = Array.isArray(component.Inputs) ? component.Inputs : [];
        const $variantActions = $('<div>',{class:'h18-component-variant-actions'});
        if(inputs.length){$variantActions.append($('<button>',{type:'button',class:'button h18-component-save-variant',text:activeVariant?'Opdater valgt variant':'Gem aktuelle værdier som variant'}));if(activeVariant)$variantActions.append($('<button>',{type:'button',class:'button-link-delete h18-component-delete-variant',text:'Slet variant'}));$editor.append($variantActions);}
        if (!inputs.length) {
            $editor.append($('<p>', { class: 'description', text: 'Denne komponent har ingen frigivne lokale inputs. Layout og indhold følger den globale definition.' }));
            return;
        }
        inputs.forEach(function (input) {
            const inputId = String(input.InputId || '');
            const field = String(input.Field || '');
            const defaultValue = componentInputDefaultV0521(component, input, activeVariant);
            const effective = Object.prototype.hasOwnProperty.call(overrides, inputId) ? overrides[inputId] : defaultValue;
            const $field = $('<label>', { class: 'h18-component-override-field' }).append($('<span>', { text: String(input.Label || field) }));
            let $control;
            if (field === 'Content') {
                $control = $('<textarea>', { rows: 4, class: 'h18-component-override-control', 'data-input-id': inputId, 'data-default-value': String(defaultValue == null ? '' : defaultValue), 'data-input-field': field }).val(String(effective == null ? '' : effective));
            } else if (field === 'MediaId') {
                $control = $('<div>', { class: 'h18-component-media-override' });
                const $value = $('<input>', { type: 'hidden', class: 'h18-component-override-control', 'data-input-id': inputId, 'data-default-value': String(defaultValue || 0), 'data-input-field': field }).val(String(effective || 0));
                const $label = $('<span>', { class: 'h18-component-media-id', text: effective ? 'Medie-ID ' + String(effective) : 'Bruger komponentens standardbillede' });
                const $pick = $('<button>', { type: 'button', class: 'button h18-component-override-media', text: 'Vælg billede' });
                const $reset = $('<button>', { type: 'button', class: 'button-link h18-component-override-reset', text: 'Brug global standard' });
                $control.append($value, $label, $pick, $reset);
            } else {
                $control = $('<input>', { type: field.indexOf('Url') !== -1 ? 'url' : 'text', class: 'h18-component-override-control', 'data-input-id': inputId, 'data-default-value': String(defaultValue == null ? '' : defaultValue), 'data-input-field': field }).val(String(effective == null ? '' : effective));
                $field.append($('<button>', { type: 'button', class: 'button-link h18-component-override-reset', text: 'Brug global standard' }));
            }
            $field.prepend($control);
            $editor.append($field);
        });
    }

    function syncComponentOverrideControlV0521($control) {
        const $row = pageSectionForElement($control);
        if (!$row.length) { return; }
        const inputId = String($control.attr('data-input-id') || '');
        const defaultValue = String($control.attr('data-default-value') || '');
        let value = String($control.val() == null ? '' : $control.val());
        const overrides = parseComponentOverridesV0521($row);
        if (value === defaultValue) { delete overrides[inputId]; }
        else { overrides[inputId] = value; }
        writeComponentOverridesV0521($row, overrides);
        renderCanvasPreview($row); scheduleEditorHistoryCapture(250);
    }

    $(document).on('input change', '.h18-component-override-control', function () { syncComponentOverrideControlV0521($(this)); });
    $(document).on('click', '.h18-component-override-reset', function (event) {
        event.preventDefault();
        const $field = $(this).closest('.h18-component-override-field');
        const $control = $field.find('.h18-component-override-control').first();
        $control.val(String($control.attr('data-default-value') || '')).trigger('change');
        const field = String($control.attr('data-input-field') || '');
        if (field === 'MediaId') { $field.find('.h18-component-media-id').text('Bruger komponentens standardbillede'); }
    });
    $(document).on('click', '.h18-component-override-media', function (event) {
        event.preventDefault();
        const $field = $(this).closest('.h18-component-override-field');
        const $control = $field.find('.h18-component-override-control').first();
        const frame = wp.media({ title: 'Vælg komponentbillede', button: { text: 'Brug billede' }, multiple: false, library: { type: 'image' } });
        frame.on('select', function () {
            const media = frame.state().get('selection').first().toJSON();
            $control.val(String(media.id || 0)).trigger('change');
            $field.find('.h18-component-media-id').text(media.id ? 'Medie-ID ' + media.id : 'Bruger komponentens standardbillede');
        });
        frame.open();
    });
    $(document).on('change', '.h18-component-select', function () {
        const $row = pageSectionForElement(this);
        pageSectionControls($row,'.h18-component-variant-select').val('');
        writeComponentOverridesV0521($row, {});
        renderComponentInstanceEditorV0521($row); renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });


    $(document).on('change','.h18-component-variant-select',function(){const $row=pageSectionForElement(this);writeComponentOverridesV0521($row,{});renderComponentInstanceEditorV0521($row);renderCanvasPreview($row);scheduleEditorHistoryCapture(0);});

    function componentVariantValuesV0522($row){const values={};pageSectionControls($row,'.h18-component-override-control').each(function(){const id=String($(this).attr('data-input-id')||'');if(id)values[id]=String($(this).val()==null?'':$(this).val());});return values;}

    $(document).on('click','.h18-component-save-variant',function(event){event.preventDefault();const $row=pageSectionForElement(this);const componentId=String(pageSectionControls($row,'.h18-component-select').val()||'');const component=pageLinkedComponents[componentId];if(!component)return;const variantId=String(pageSectionControls($row,'.h18-component-variant-select').val()||'');let currentName='';if(variantId&&component.Variants&&component.Variants[variantId])currentName=String(component.Variants[variantId].Name||'');const name=window.prompt(variantId?'Variantnavn:':'Navn til ny variant:',currentName||'Ny variant');if(!name)return;const $button=$(this).prop('disabled',true).text('Gemmer…');$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_save_page_component_variant',nonce:Hangar18Manager.pageComponentNonce,component_id:componentId,variant_id:variantId,name:String(name).trim(),values:JSON.stringify(componentVariantValuesV0522($row))}).done(function(response){if(!response||!response.success||!response.data||!response.data.component){window.alert((response&&response.data&&response.data.message)||'Varianten kunne ikke gemmes.');return;}pageLinkedComponents[componentId]=response.data.component;pageSectionControls($row,'.h18-component-variant-select').val(String(response.data.variant_id||''));writeComponentOverridesV0521($row,{});renderLinkedComponentsV0521();refreshAllComponentEditorsV0521();}).fail(function(xhr){window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Varianten kunne ikke gemmes.');}).always(function(){$button.prop('disabled',false);renderComponentInstanceEditorV0521($row);});});

    $(document).on('click','.h18-component-delete-variant',function(event){event.preventDefault();const $row=pageSectionForElement(this);const componentId=String(pageSectionControls($row,'.h18-component-select').val()||'');const variantId=String(pageSectionControls($row,'.h18-component-variant-select').val()||'');if(!componentId||!variantId||!window.confirm('Slet denne variant? Instanser der bruger den skal fjernes/skiftes først.'))return;$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_delete_page_component_variant',nonce:Hangar18Manager.pageComponentNonce,component_id:componentId,variant_id:variantId}).done(function(response){if(!response||!response.success){window.alert((response&&response.data&&response.data.message)||'Varianten kunne ikke slettes.');return;}const component=pageLinkedComponents[componentId];if(component&&component.Variants)delete component.Variants[variantId];pageSectionControls($row,'.h18-component-variant-select').val('');writeComponentOverridesV0521($row,{});renderComponentInstanceEditorV0521($row);renderCanvasPreview($row);});});

    function componentSubtreeRowsV0521($root) {
        if (!$root || !$root.length) { return []; }
        const rootKey = String($root.find('.h18-page-section-key').val() || '');
        if (!rootKey) { return []; }
        const ordered = [];
        const wanted = new Set([rootKey]);
        let changed = true;
        while (changed && wanted.size < 25) {
            changed = false;
            $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
                const $row = $(this);
                const key = String($row.find('.h18-page-section-key').val() || '');
                const parent = String(pageSectionControls($row, '.h18-layout-parent-key').val() || '');
                if (key && parent && wanted.has(parent) && !wanted.has(key)) { wanted.add(key); changed = true; }
            });
        }
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const key = String($(this).find('.h18-page-section-key').val() || '');
            if (wanted.has(key)) { ordered.push($(this)); }
        });
        return ordered;
    }

    function componentSubtreeDataV0521($root) {
        const rows = componentSubtreeRowsV0521($root);
        if (!rows.length) { return []; }
        const rootKey = String($root.find('.h18-page-section-key').val() || '');
        const keys = new Set(rows.map(function ($row) { return String($row.find('.h18-page-section-key').val() || ''); }));
        return rows.map(function ($row, index) {
            const data = sectionPresetData($row);
            if (!data) { return null; }
            const key = String($row.find('.h18-page-section-key').val() || '');
            const parent = String(pageSectionControls($row, '.h18-layout-parent-key').val() || '');
            data.Key = key;
            data.Order = (index + 1) * 10;
            data.LayoutParentKey = key === rootKey ? '' : (keys.has(parent) ? parent : '');
            delete data.NavigatorLabel; delete data.NavigatorLocked; delete data.ComponentId; delete data.ComponentRevision; delete data.ComponentOverridesJson;
            return data;
        }).filter(Boolean);
    }

    function componentCandidateInputsV0521(sections) {
        const inputs = [];
        (sections || []).forEach(function (section) {
            const key = String(section.Key || '');
            const type = String(section.Type || 'text');
            const sectionName = String(section.Title || inspectorTypeLabel(type));
            function add(field, label) { inputs.push({ SectionKey: key, Field: field, Label: sectionName + ' · ' + label }); }
            if (!['css','html','shortcode','embed','legacy','component','spacer','divider'].includes(type)) {
                add('Title','Overskrift');
            }
            if (!['css','html','shortcode','embed','legacy','component','spacer','divider','image','badge','icon'].includes(type)) {
                add('Content','Tekst');
            }
            if (['hero','text_image','image'].includes(type)) { add('MediaId','Billede'); }
            if (['hero','buttons'].includes(type)) {
                add('Button1Label','Knap 1 tekst'); add('Button1Url','Knap 1 link'); add('Button2Label','Knap 2 tekst'); add('Button2Url','Knap 2 link');
            }
        });
        return inputs.slice(0,40);
    }

    function openSaveLinkedComponentDialogV0521(componentId) {
        if (!$inspectedSection.length) { return; }
        if (rowLockedV0521($inspectedSection)) { window.alert('Laget er låst. Lås det op før det gemmes som en linked component.'); return; }
        const type = String($inspectedSection.attr('data-section-type') || '');
        if (['legacy','component'].includes(type)) { window.alert('Vælg et almindeligt element eller layout-subtree.'); return; }
        const subtreeRows = componentSubtreeRowsV0521($inspectedSection);
        if (subtreeRows.some(function($row){ return ['legacy','component'].includes(String($row.attr('data-section-type') || '')); })) {
            window.alert('Subtreeet indeholder legacy eller en linked component. Nested linked components er ikke tilladt i denne version.');
            return;
        }
        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length) { return; }
        const existing = componentId ? pageLinkedComponents[String(componentId)] : null;
        const candidates = componentCandidateInputsV0521(sections);
        const selectedIds = new Set((existing && Array.isArray(existing.Inputs) ? existing.Inputs : []).map(function (input) { return String(input.SectionKey) + '|' + String(input.Field); }));
        const $overlay = $('<div>', { class: 'h18-component-dialog-overlay' });
        const $dialog = $('<div>', { class: 'h18-component-dialog', role: 'dialog', 'aria-modal': 'true', 'aria-label': existing ? 'Opdater linked component' : 'Gem linked component' });
        $dialog.append($('<h3>', { text: existing ? 'Opdater linked component' : 'Gem subtree som linked component' }));
        const $name = $('<input>', { type: 'text', class: 'regular-text h18-component-dialog-name', maxlength: 80, placeholder: 'Komponentnavn' }).val(existing ? String(existing.Name || '') : String(pageSectionControls($inspectedSection,'.h18-section-navigator-label').val() || setSectionTitleSummary($inspectedSection) || inspectorTypeLabel(type)));
        $dialog.append($('<label>').append($('<strong>', { text: 'Navn' }), $name));
        $dialog.append($('<p>', { class: 'description', text: 'Vælg hvilke indholdsfelter instanser må overskrive lokalt. Layout/design er altid låst til den globale definition.' }));
        const $choices = $('<div>', { class: 'h18-component-input-choices' });
        candidates.forEach(function (candidate) {
            const token = String(candidate.SectionKey) + '|' + String(candidate.Field);
            const checked = existing ? selectedIds.has(token) : ['Title','Content','MediaId','Button1Label','Button1Url'].includes(String(candidate.Field));
            const $check = $('<input>', { type: 'checkbox', value: token }).prop('checked', checked).data('input', candidate);
            $choices.append($('<label>', { class: 'h18-component-input-choice' }).append($check, $('<span>', { text: String(candidate.Label) })));
        });
        if (!candidates.length) { $choices.append($('<p>', { class: 'description', text: 'Subtreeet har ingen sikre felter, der kan frigives. Det kan stadig gemmes med helt låst indhold.' })); }
        $dialog.append($choices);
        const $actions = $('<div>', { class: 'h18-component-dialog-actions' });
        const $cancel = $('<button>', { type: 'button', class: 'button', text: 'Annuller' });
        const $save = $('<button>', { type: 'button', class: 'button button-primary', text: existing ? 'Opdater global definition' : 'Gem linked component' });
        $actions.append($cancel,$save); $dialog.append($actions); $overlay.append($dialog); $('body').append($overlay); $name.trigger('focus');
        function close(){ $overlay.remove(); }
        $cancel.on('click',close); $overlay.on('click',function(e){ if(e.target === $overlay.get(0)) close(); });
        $save.on('click',function(){
            const name = String($name.val() || '').trim(); if(!name){ $name.trigger('focus'); return; }
            const inputs=[]; $choices.find('input:checked').each(function(){ const input=$(this).data('input'); if(input) inputs.push(input); });
            $save.prop('disabled',true).text('Gemmer…');
            $.post(Hangar18Manager.ajaxUrl || window.ajaxurl, { action:'h18_save_page_component', nonce:Hangar18Manager.pageComponentNonce, name:name, component_id:existing ? String(existing.Id) : '', sections:JSON.stringify(sections), inputs:JSON.stringify(inputs) })
                .done(function(response){
                    if(!response || !response.success || !response.data || !response.data.component){ window.alert((response&&response.data&&response.data.message)||'Linked component kunne ikke gemmes.'); return; }
                    const component=response.data.component; pageLinkedComponents[String(component.Id)]=component; renderLinkedComponentsV0521(); refreshAllComponentEditorsV0521(); close();
                }).fail(function(xhr){ window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Linked component kunne ikke gemmes.'); })
                .always(function(){ $save.prop('disabled',false).text(existing ? 'Opdater global definition' : 'Gem linked component'); });
        });
    }

    function renderLinkedComponentsV0521() {
        if (!$pageLinkedComponentsList.length) { return; }
        const components = Object.values(pageLinkedComponents).sort(function(a,b){ return String(a.Name||'').localeCompare(String(b.Name||''),'da'); });
        $pageLinkedComponentsList.empty();
        if(!components.length){ $pageLinkedComponentsList.html('<p class="description">Ingen linked components endnu.</p>'); return; }
        components.forEach(function(component){
            const usage=parseInt(component.UsageCount,10)||0;
            const $row=$('<div>',{class:'h18-user-preset-row h18-linked-component-row','data-component-id':String(component.Id)});
            $row.append($('<button>',{type:'button',class:'h18-linked-component-insert'}).append($('<strong>',{text:String(component.Name||'Linked component')}),$('<small>',{text:'r'+String(component.Revision||1)+' · '+usage+' brug'})));
            $row.append($('<button>',{type:'button',class:'h18-linked-component-usage',title:'Vis brug','aria-label':'Vis brug'}).append($('<span>',{class:'dashicons dashicons-admin-links'})));
            $row.append($('<button>',{type:'button',class:'h18-linked-component-update',title:'Opdater fra valgt subtree','aria-label':'Opdater fra valgt subtree'}).append($('<span>',{class:'dashicons dashicons-update'})));
            $row.append($('<button>',{type:'button',class:'h18-linked-component-delete',title:'Slet linked component','aria-label':'Slet linked component'}).append($('<span>',{class:'dashicons dashicons-trash'})));
            $pageLinkedComponentsList.append($row);
        });
    }

    function applyLinkedComponentV0521(component) {
        if(!component || !component.Id){ return $(); }
        const $row=addPageSection('component');
        if(!$row.length){ return $row; }
        pageSectionControls($row,'.h18-component-select').val(String(component.Id));
        pageSectionControls($row,'.h18-component-revision').val(parseInt(component.Revision,10)||1);
        pageSectionControls($row,'.h18-component-overrides-json').val('{}');
        pageSectionControls($row,'.h18-section-navigator-label').val(String(component.Name||'Linked component'));
        refreshPageSectionType($row); renderComponentInstanceEditorV0521($row); setSectionTitleSummary($row); syncPageSectionOrder(); inspectPageSection($row); scheduleEditorHistoryCapture(0); return $row;
    }

    function refreshAllComponentEditorsV0521(){ $pageSections.children('.h18-page-section-row[data-section-type="component"]').each(function(){ renderComponentInstanceEditorV0521($(this)); renderCanvasPreview($(this)); }); }

    $(document).on('click','.h18-linked-component-insert',function(){ const component=pageLinkedComponents[String($(this).closest('.h18-linked-component-row').attr('data-component-id')||'')]; applyLinkedComponentV0521(component); });
    $(document).on('click','.h18-linked-component-usage',function(){
        const component=pageLinkedComponents[String($(this).closest('.h18-linked-component-row').attr('data-component-id')||'')]; if(!component)return;
        const usage=Array.isArray(component.Usage)?component.Usage:[];
        window.alert(usage.length ? 'Brug af “'+String(component.Name||'Component')+'”:\n\n'+usage.map(function(item){return '• '+String(item.PageTitle||item.PageSlug)+' / '+String(item.SectionKey||'');}).join('\n') : 'Komponenten bruges ikke på gemte sider endnu.');
    });
    $(document).on('click','.h18-linked-component-update',function(){
        const id=String($(this).closest('.h18-linked-component-row').attr('data-component-id')||'');
        if(!$inspectedSection.length){window.alert('Vælg først det subtree, der skal være den nye globale definition.');return;}
        openSaveLinkedComponentDialogV0521(id);
    });
    $(document).on('click','.h18-linked-component-delete',function(){
        const id=String($(this).closest('.h18-linked-component-row').attr('data-component-id')||''); const component=pageLinkedComponents[id]; if(!component)return;
        const usage=parseInt(component.UsageCount,10)||0; if(usage>0){window.alert('Komponenten bruges '+usage+' sted(er). Vis brug og fjern instanserne først.');return;}
        if(!window.confirm('Slet linked component “'+String(component.Name||'Component')+'”?'))return;
        $.post(Hangar18Manager.ajaxUrl || window.ajaxurl,{action:'h18_delete_page_component',nonce:Hangar18Manager.pageComponentNonce,component_id:id}).done(function(response){if(response&&response.success){delete pageLinkedComponents[id];renderLinkedComponentsV0521();}else{window.alert((response&&response.data&&response.data.message)||'Komponenten kunne ikke slettes.');}});
    });
    $('#h18-save-linked-component').on('click',function(){ if($inspectedSection.length)openSaveLinkedComponentDialogV0521(''); });


    function pageTemplateSectionsV0522(){const rows=[];let invalid='';$pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function(index){const $row=$(this);const type=String($row.attr('data-section-type')||'text');if(['legacy','component'].includes(type)){invalid=type;return false;}const data=sectionPresetData($row);if(!data){invalid=type;return false;}data.Key=String($row.find('.h18-page-section-key').val()||'');data.Order=(index+1)*10;data.LayoutParentKey=String(pageSectionControls($row,'.h18-layout-parent-key').val()||'');rows.push(data);});return invalid?{error:invalid,sections:[]}:{error:'',sections:rows};}

    function renderPageTemplatesV0522(){if(!$pageTemplatesList.length)return;const templates=Object.values(pageTemplatesV0522).sort(function(a,b){return String(a.Name||'').localeCompare(String(b.Name||''),'da');});$pageTemplatesList.empty();if(!templates.length){$pageTemplatesList.html('<p class="description">Ingen Page Templates endnu.</p>');return;}templates.forEach(function(template){const usage=parseInt(template.UsageCount,10)||0;const $row=$('<div>',{class:'h18-user-preset-row h18-page-template-row','data-template-id':String(template.Id)});$row.append($('<button>',{type:'button',class:'h18-page-template-create'}).append($('<strong>',{text:String(template.Name||'Page Template')}),$('<small>',{text:(Array.isArray(template.Sections)?template.Sections.length:0)+' elementer · '+usage+' oprettede sider'})));$row.append($('<button>',{type:'button',class:'h18-page-template-usage',title:'Vis oprettede sider','aria-label':'Vis oprettede sider'}).append($('<span>',{class:'dashicons dashicons-admin-page'})));$row.append($('<button>',{type:'button',class:'h18-page-template-delete',title:'Slet template','aria-label':'Slet template'}).append($('<span>',{class:'dashicons dashicons-trash'})));$pageTemplatesList.append($row);});}

    $('#h18-save-page-template').on('click',function(){const collected=pageTemplateSectionsV0522();if(collected.error){window.alert('Page Template kan ikke gemmes, mens siden indeholder legacy eller linked component-instanser. Konvertér/detach dem først.');return;}if(!collected.sections.length){window.alert('Siden har ingen elementer at gemme.');return;}const currentTitle=String($('[name="editor_page_title"]').val()||'Side');const name=window.prompt('Navn til Page Template:',currentTitle);if(!name)return;const $button=$(this).prop('disabled',true).text('Gemmer…');$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_save_page_template',nonce:Hangar18Manager.pageTemplateNonce,name:String(name).trim(),page_title:currentTitle,sections:JSON.stringify(collected.sections)}).done(function(response){if(!response||!response.success||!response.data||!response.data.template){window.alert((response&&response.data&&response.data.message)||'Page Template kunne ikke gemmes.');return;}pageTemplatesV0522[String(response.data.template.Id)]=response.data.template;renderPageTemplatesV0522();}).fail(function(xhr){window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Page Template kunne ikke gemmes.');}).always(function(){$button.prop('disabled',false).text('Gem denne side som template');});});

    $(document).on('click','.h18-page-template-create',function(){const id=String($(this).closest('.h18-page-template-row').attr('data-template-id')||'');const template=pageTemplatesV0522[id];if(!template)return;const title=window.prompt('Titel på den nye WordPress-side:',String(template.PageTitle||template.Name||'Ny side'));if(!title)return;const suggested=String(title).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');const slug=window.prompt('Slug til den nye side:',suggested);if(!slug)return;$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_create_page_from_template',nonce:Hangar18Manager.pageTemplateNonce,template_id:id,page_title:String(title).trim(),page_slug:String(slug).trim()}).done(function(response){if(!response||!response.success){window.alert((response&&response.data&&response.data.message)||'Siden kunne ikke oprettes.');return;}if(response.data.manager_url)window.location.href=response.data.manager_url;}).fail(function(xhr){window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Siden kunne ikke oprettes.');});});

    $(document).on('click','.h18-page-template-usage',function(){const id=String($(this).closest('.h18-page-template-row').attr('data-template-id')||'');const template=pageTemplatesV0522[id];if(!template)return;const usage=Array.isArray(template.Usage)?template.Usage:[];window.alert(usage.length?'Sider oprettet fra “'+String(template.Name||'Template')+'”:\n\n'+usage.map(function(item){return '• '+String(item.PageTitle||item.PageSlug)+' / '+String(item.PageSlug||'');}).join('\n'):'Ingen sider er oprettet fra denne template endnu.');});

    $(document).on('click','.h18-page-template-delete',function(){const id=String($(this).closest('.h18-page-template-row').attr('data-template-id')||'');const template=pageTemplatesV0522[id];if(!template)return;if(!window.confirm('Slet Page Template “'+String(template.Name||'Template')+'”? Allerede oprettede sider påvirkes ikke.'))return;$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_delete_page_template',nonce:Hangar18Manager.pageTemplateNonce,template_id:id}).done(function(response){if(response&&response.success){delete pageTemplatesV0522[id];renderPageTemplatesV0522();}else window.alert((response&&response.data&&response.data.message)||'Template kunne ikke slettes.');});});

    function restoreInspectedSection() {
        if (!$inspectedSection.length) {
            return;
        }
        const $body = $pageInspectorTarget.children('.h18-page-section-body');
        if ($body.length) {
            $inspectedSection.append($body);
        }
        $inspectedSection.removeClass('is-selected');
        $inspectedSection = $();
        $pageInspector.find('.h18-builder-inspector-heading span').text('Vælg en sektion i sideopbygningen');
        $pageInspectorTarget.html('<p class="description">Klik på <strong>Rediger</strong> ved en sektion for at ændre indhold, design og responsive indstillinger.</p>');
        refreshInspectorMeta($());
        setInspectorPanel('content');
        rebuildPageNavigator();
    }

    function inspectPageSection($row, preserveMultiSelection) {
        if (!$pageInspectorTarget.length || !$row.length || $row.hasClass('h18-page-section-removed')) {
            return;
        }
        if (preserveMultiSelection !== true) {
            multiSelectClearV0515(false);
        }
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
            syncMultiSelectUiV0515();
            return;
        }
        restoreInspectedSection();
        $inspectedSection = $row;
        $row.addClass('is-selected');
        const label = String($row.find('.h18-page-section-summary').first().text() || 'Sektion');
        $pageInspector.find('.h18-builder-inspector-heading span').text(label);
        $pageInspectorTarget.empty().append($row.children('.h18-page-section-body'));
        refreshInspectorMeta($row);
        setInspectorPanel(currentInspectorPanel);
        rebuildPageNavigator();
        refreshAllCanvasPreviews();
    }

    function pageSectionControls($row, selector) {
        let $controls = $row.find(selector);
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
            $controls = $controls.add($pageInspectorTarget.find(selector));
        }
        return $controls;
    }

    function syncPageSectionOrder(skipNavigator) {
        if (!$pageSections.length) {
            return;
        }
        let visibleIndex = 0;
        $pageSections.children('.h18-page-section-row').each(function () {
            if (!$(this).hasClass('h18-page-section-removed')) {
                visibleIndex += 1;
                $(this).find('.h18-page-section-order').val(visibleIndex * 10);
            }
        });
        if (skipNavigator !== true) {
            rebuildPageNavigator();
        }
    }

    function refreshSectionDesignMode($row) {
        if (!$row || !$row.length) { return; }
        const custom = String(pageSectionControls($row, '.h18-section-design-mode').val() || 'Global') === 'Custom';
        pageSectionControls($row, '.h18-custom-design-fields').toggle(custom);
    }

    function refreshSectionBackgroundEffect($row) {
        if (!$row || !$row.length) { return; }
        const effect = String(pageSectionControls($row, '.h18-section-background-effect').val() || 'None');
        pageSectionControls($row, '.h18-bg-gradient-fields').toggle(effect === 'Gradient');
        pageSectionControls($row, '.h18-bg-image-fields').toggle(effect === 'Image');
    }

    function refreshHoverStyleMode($row) {
        if (!$row || !$row.length) { return; }
        const custom = String(pageSectionControls($row, '.h18-hover-style-mode').val() || 'Inherit') === 'Custom';
        pageSectionControls($row, '.h18-hover-style-fields').toggle(custom);
    }

    function refreshCollectionEditorV0517($row) {
        if (!$row || !$row.length) { return; }
        const type = String($row.attr('data-section-type') || 'text');
        const $box = pageSectionControls($row, '.h18-collection-editor');
        if (!$box.length) { return; }
        const isCards = type === 'card_grid';
        const isTabs = type === 'tabs';
        const isAccordion = type === 'accordion';
        const isCarousel = type === 'carousel';
        $box.find('.h18-card-grid-layout-fields').toggle(isCards);
        $box.find('.h18-collection-editor-title').text(isTabs ? 'Faner / tabs' : (isAccordion ? 'Accordion' : (isCarousel ? 'Carousel / slider' : 'Kort-række / kolonner')));
        $box.find('.h18-collection-editor-description').text(isTabs
            ? 'Hvert panel bliver en fane. Titel er fanetekst; indhold er fanens panel.'
            : (isAccordion ? 'Hvert panel bliver et fold-ud punkt med titel og indhold.' : (isCarousel ? 'Hvert panel bliver et slide. Titel, indhold og Card-design følger slidet.' : 'Hver kasse kan flyttes, farves og tilpasses separat.')));
        $box.find('.h18-add-page-card-label').text(isCards ? 'Tilføj kasse' : 'Tilføj panel');
    }

    function initializeCollectionPanelsV0517($row, type) {
        if (!['tabs', 'accordion', 'carousel'].includes(type)) { return; }
        if (pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length) { return; }
        const prefix = type === 'tabs' ? 'Fane' : (type === 'carousel' ? 'Slide' : 'Punkt');
        addPageCard($row, { Title: prefix + ' 1', Content: '<p>Indhold til ' + prefix.toLowerCase() + ' 1.</p>', Background: 'White', TextTone: 'Auto', Active: true });
        addPageCard($row, { Title: prefix + ' 2', Content: '<p>Indhold til ' + prefix.toLowerCase() + ' 2.</p>', Background: 'OffWhite', TextTone: 'Auto', Active: true });
    }

    function layoutParentCapableV0519($row) {
        return $row && $row.length && ['container','flex','grid'].includes(String($row.attr('data-section-type') || ''));
    }

    function layoutWouldCycleV0519($row, candidateKey) {
        const selfKey = String($row.find('.h18-page-section-key').val() || '');
        let cursor = String(candidateKey || '');
        const seen = new Set([selfKey]);
        let depth = 0;
        while (cursor) {
            depth += 1;
            if (depth > 2 || seen.has(cursor)) { return true; }
            seen.add(cursor);
            const $candidate = $pageSections.children('.h18-page-section-row').filter(function () { return String($(this).find('.h18-page-section-key').val() || '') === cursor; }).first();
            if (!$candidate.length || !layoutParentCapableV0519($candidate)) { return true; }
            cursor = String(pageSectionControls($candidate, '.h18-layout-parent-key').val() || '');
        }
        return false;
    }

    function refreshLayoutHierarchyV0519() {
        if (!$pageSections.length) { return; }
        const parents = [];
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const $candidate = $(this);
            if (layoutParentCapableV0519($candidate)) {
                parents.push({ key: String($candidate.find('.h18-page-section-key').val() || ''), title: String($candidate.find('.h18-page-section-title-summary').first().text() || inspectorTypeLabel($candidate.attr('data-section-type'))), type: String($candidate.attr('data-section-type') || '') });
            }
        });
        $pageSections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            const selfKey = String($row.find('.h18-page-section-key').val() || '');
            const $hidden = pageSectionControls($row, '.h18-layout-parent-key').first();
            const $select = pageSectionControls($row, '.h18-layout-parent-select').first();
            if (!$select.length || !$hidden.length) { return; }
            let current = String($hidden.val() || '');
            $select.empty().append($('<option>', { value: '', text: 'Topniveau på siden' }));
            parents.forEach(function (parent) {
                if (!parent.key || parent.key === selfKey) { return; }
                const disabled = layoutWouldCycleV0519($row, parent.key);
                $select.append($('<option>', { value: parent.key, text: inspectorTypeLabel(parent.type) + ' · ' + (parent.title || parent.key), disabled: disabled }));
            });
            if (current && !$select.find('option[value="' + current.replace(/"/g,'\\"') + '"]:not(:disabled)').length) { current = ''; $hidden.val(''); }
            $select.val(current);
            $row.toggleClass('h18-layout-child-row', Boolean(current)).attr('data-layout-parent', current);
            const index = String($row.attr('data-section-index') || '');
            $pageNavigatorList.children('.h18-navigator-item[data-section-index="' + index + '"]').toggleClass('h18-layout-child-item', Boolean(current)).attr('data-layout-parent', current);
            $row.find('.h18-layout-parent-box').toggle(String($row.attr('data-section-type') || '') !== 'legacy');
        });
    }

    function refreshPageSectionType($row) {
        const type = String(pageSectionControls($row, '.h18-page-section-type').val() || pageSectionControls($row, 'input[name$="[Type]"]').val() || 'text');
        $row.attr('data-section-type', type);
        pageSectionControls($row, '.h18-section-type-field').each(function () {
            const types = String($(this).attr('data-types') || '').split(/\s+/);
            $(this).toggle(types.includes(type));
        });
        const labels = {
            hero: 'Topbanner / hero',
            text: 'Tekst',
            text_image: 'Tekst og billede',
            image: 'Stort billede',
            buttons: 'Handlingsknapper',
            card: 'Indholdskort',
            card_grid: 'Kort-række / kolonner',
            tabs: 'Faner / tabs',
            accordion: 'Accordion',
            carousel: 'Carousel / slider',
            container: 'Container',
            flex: 'Flex container',
            grid: 'Grid container',
            highlight: 'Fremhævet tekst',
            spacer: 'Afstand',
            html: 'Importeret blok / HTML',
            css: 'Side-CSS (avanceret)',
            mail_form: 'Mailformular',
            poll: 'Afstemning',
            legacy: 'Eksisterende indhold'
        };
        $row.find('.h18-page-section-summary').text(labels[type] || 'Sektion');
        pageSectionControls($row, '.h18-section-title-label').text(type === 'poll' ? 'Spørgsmål' : 'Overskrift');
        refreshInspectorMeta($row);
        refreshSectionDesignMode($row);
        refreshSectionBackgroundEffect($row);
        refreshHoverStyleMode($row);
        refreshPrimitiveVariantV0516($row);
        refreshCollectionEditorV0517($row);
        if (type === 'component') { renderComponentInstanceEditorV0521($row); }
        rebuildPageNavigator();
        refreshLayoutHierarchyV0519();
        renderCanvasPreview($row);
    }

    function syncPageCardOrder($container) {
        let visibleIndex = 0;
        $container.children('.h18-page-card-row').each(function () {
            if (!$(this).hasClass('h18-page-card-removed')) {
                visibleIndex += 1;
                $(this).find('.h18-page-card-order').val(visibleIndex * 10);
            }
        });
    }

    function renamePageCard($card, sectionIndex, cardIndex, regenerateKey) {
        $card.attr('data-card-index', cardIndex);
        $card.find('[name]').each(function () {
            const name = String($(this).attr('name') || '');
            $(this).attr('name', name.replace(/sections\[(?:\d+|__SECTION_INDEX__)\]\[Cards\]\[(?:\d+|__CARD_INDEX__)\]/, 'sections[' + sectionIndex + '][Cards][' + cardIndex + ']'));
        });
        if (regenerateKey) {
            $card.find('.h18-page-card-key').val(newCardKey());
        }
        $card.find('.h18-page-card-remove').val('0');
        $card.removeClass('h18-page-card-removed');
    }

    function initializePageCardSortables($scope) {
        $scope.find('.h18-page-cards-sortable').addBack('.h18-page-cards-sortable').each(function () {
            const $container = $(this);
            if (!$container.hasClass('ui-sortable')) {
                $container.sortable({
                    items: '> .h18-page-card-row:not(.h18-page-card-removed)',
                    handle: '.h18-page-card-drag',
                    axis: 'y',
                    tolerance: 'pointer',
                    update: function () { syncPageCardOrder($container); renderCanvasPreview(pageSectionForElement($container)); }
                });
            }
            syncPageCardOrder($container);
        });
    }

    function addPageCard($row, values) {
        if (!pageCardTemplate || !$row.length) {
            return $();
        }
        const $container = pageSectionControls($row, '.h18-page-cards-sortable');
        if ($container.children('.h18-page-card-row:not(.h18-page-card-removed)').length >= 12) {
            window.alert('En kort-række kan højst indeholde 12 kasser.');
            return $();
        }
        const sectionIndex = String($row.attr('data-section-index'));
        let cardIndex = 0;
        $container.children('.h18-page-card-row').each(function () {
            const current = parseInt($(this).attr('data-card-index'), 10);
            if (!Number.isNaN(current)) {
                cardIndex = Math.max(cardIndex, current + 1);
            }
        });
        const html = pageCardTemplate.innerHTML
            .replaceAll('__SECTION_INDEX__', sectionIndex)
            .replaceAll('__CARD_INDEX__', String(cardIndex));
        const $card = $(html.trim());
        renamePageCard($card, sectionIndex, cardIndex, true);
        Object.entries(values || {}).forEach(function (entry) {
            $card.find('[name$="[' + entry[0] + ']"]').val(entry[1]);
        });
        if (values && Object.prototype.hasOwnProperty.call(values, 'Active')) {
            $card.find('[name$="[Active]"]').prop('checked', Boolean(values.Active));
        }
        const title = String((values && values.Title) || 'Uden overskrift');
        $card.find('.h18-page-card-title-summary').text(title);
        $container.append($card);
        initializePageCardSortables($container);
        renderCanvasPreview($row);
        return $card;
    }

    function reindexPageSection($row, index) {
        $row.attr('data-section-index', index);
        $row.find('[name]').each(function () {
            const name = String($(this).attr('name') || '');
            $(this).attr('name', name.replace(/sections\[(?:\d+|__INDEX__)\]/, 'sections[' + index + ']'));
        });
        $row.find('.h18-page-section-key').val(newSectionKey());
        $row.find('.h18-page-section-remove').val('0');
        $row.find('.h18-page-card-row').each(function (cardIndex) {
            renamePageCard($(this), index, cardIndex, true);
        });
        $row.removeClass('h18-page-section-removed');
        $row.find('input[name$="[ResetVotes]"]').prop('checked', false);
        $row.find('.h18-module-status').html('<em>Gem siden for at oprette modulet.</em>');
    }

    function applyNewSectionDefaults($row, type) {
        const setValue = function (field, value) {
            pageSectionControls($row, '[name$="[' + field + ']"]').val(value);
        };
        if (type === 'hero') {
            setValue('Background', 'Olive');
            setValue('DesktopAlignment', 'Center');
            setValue('MobileAlignment', 'Center');
            setValue('PaddingPx', 36);
            setValue('MobilePaddingPx', 22);
            setValue('HeroHeightPx', 320);
            setValue('MobileHeroHeightPx', 220);
            setValue('OverlayOpacityPercent', 35);
        } else if (type === 'icon') {
            setValue('PrimitiveVariant', 'check');
            setValue('DesktopAlignment', 'Center');
            setValue('MobileAlignment', 'Center');
        } else if (type === 'divider') {
            setValue('PrimitiveVariant', 'solid');
            setValue('BorderWidthPx', 2);
            setValue('BottomSpacingPx', 24);
        } else if (type === 'list') {
            setValue('PrimitiveVariant', 'bullets');
        } else if (type === 'badge') {
            setValue('PrimitiveVariant', 'solid');
            setValue('DesktopAlignment', 'Left');
        } else if (type === 'quote') {
            setValue('PrimitiveVariant', 'standard');
            setValue('BorderWidthPx', 4);
        } else if (type === 'card') {
            setValue('Background', 'OffWhite');
            setValue('PaddingPx', 26);
            setValue('MobilePaddingPx', 20);
        } else if (['container','flex','grid'].includes(type)) {
            setValue('Background', 'White');
            setValue('PaddingPx', 12);
            setValue('HorizontalPaddingPx', 12);
            setValue('MobilePaddingPx', 8);
            setValue('MobileHorizontalPaddingPx', 8);
            setValue('LayoutGapPx', 16);
            setValue('MobileLayoutGapPx', 12);
            setValue('LayoutColumns', 2);
            setValue('MobileLayoutColumns', 1);
            pageSectionControls($row, '[name$="[LayoutWrap]"]').prop('checked', true);
            pageSectionControls($row, '[name$="[MobileLayoutStack]"]').prop('checked', true);
        } else if (type === 'carousel') {
            setValue('Background', 'White');
            setValue('PaddingPx', 0);
            setValue('HorizontalPaddingPx', 0);
            setValue('MobilePaddingPx', 0);
            setValue('MobileHorizontalPaddingPx', 0);
            setValue('CarouselIntervalMs', 5000);
            pageSectionControls($row, '[name$="[CarouselAutoplay]"]').prop('checked', false);
            pageSectionControls($row, '[name$="[CarouselLoop]"]').prop('checked', true);
            pageSectionControls($row, '[name$="[CarouselShowArrows]"]').prop('checked', true);
            pageSectionControls($row, '[name$="[CarouselShowDots]"]').prop('checked', true);
            initializeCollectionPanelsV0517($row, type);
        } else if (type === 'tabs' || type === 'accordion') {
            setValue('Background', 'White');
            setValue('PaddingPx', 0);
            setValue('HorizontalPaddingPx', 0);
            setValue('MobilePaddingPx', 0);
            setValue('MobileHorizontalPaddingPx', 0);
            initializeCollectionPanelsV0517($row, type);
        } else if (type === 'card_grid') {
            setValue('Background', 'White');
            setValue('PaddingPx', 0);
            setValue('HorizontalPaddingPx', 0);
            setValue('MobilePaddingPx', 0);
            setValue('MobileHorizontalPaddingPx', 0);
            setValue('Columns', 3);
            setValue('MobileColumns', 1);
            setValue('ColumnGapPx', 16);
            setValue('MobileColumnGapPx', 14);
            if (!pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length) {
                addPageCard($row, { Title: 'Kasse 1', Background: 'OffWhite', TextTone: 'Auto', Active: true });
                addPageCard($row, { Title: 'Kasse 2', Background: 'Sand', TextTone: 'Auto', Active: true });
                addPageCard($row, { Title: 'Kasse 3', Background: 'Steel', TextTone: 'Auto', Active: true });
            }
        } else if (type === 'highlight') {
            setValue('Background', 'OffWhite');
            setValue('PaddingPx', 22);
            setValue('MobilePaddingPx', 18);
        } else if (type === 'mail_form' || type === 'poll') {
            setValue('Background', 'OffWhite');
            setValue('PaddingPx', 26);
            setValue('MobilePaddingPx', 20);
        } else if (type === 'spacer') {
            setValue('BottomSpacingPx', 0);
            setValue('MobileBottomSpacingPx', 0);
        } else if (type === 'css') {
            setValue('BottomSpacingPx', 0);
            setValue('MobileBottomSpacingPx', 0);
        }
    }

    function canvasFieldValue($row, fieldName, fallback) {
        const $field = pageSectionControls($row, '[name$="[' + fieldName + ']"]').first();
        if (!$field.length) {
            return fallback;
        }
        if ($field.is(':checkbox')) {
            return $field.is(':checked');
        }
        const value = $field.val();
        return value == null || value === '' ? fallback : value;
    }

    function canvasNumber($row, fieldName, fallback) {
        const value = parseFloat(canvasFieldValue($row, fieldName, fallback));
        return Number.isFinite(value) ? value : fallback;
    }

    function canvasTextFromHtml(value, maxLength) {
        const node = document.createElement('div');
        node.innerHTML = String(value || '');
        let text = String(node.textContent || node.innerText || '').replace(/\s+/g, ' ').trim();
        const limit = parseInt(maxLength, 10) || 220;
        if (text.length > limit) {
            text = text.slice(0, limit - 1).trimEnd() + '…';
        }
        return text;
    }

    function canvasPaletteColor(value) {
        const colors = {
            White: '#ffffff', OffWhite: '#f2f0e8', Sand: '#c3ae83',
            Olive: '#30382a', Steel: '#525a5f', Transparent: 'transparent'
        };
        return colors[String(value || 'White')] || '#ffffff';
    }

    function canvasShadow(value) {
        const shadows = {
            None: 'none', Soft: '0 4px 14px rgba(0,0,0,.10)',
            Medium: '0 9px 24px rgba(0,0,0,.16)', Strong: '0 15px 38px rgba(0,0,0,.24)'
        };
        return shadows[String(value || 'None')] || 'none';
    }

    function canvasDeviceLayout($row) {
        const desktop = {
            align: String(canvasFieldValue($row, 'DesktopAlignment', 'Left')).toLowerCase(),
            top: canvasNumber($row, 'TopSpacingPx', 0), bottom: canvasNumber($row, 'BottomSpacingPx', 24),
            pad: canvasNumber($row, 'PaddingPx', 0), padX: canvasNumber($row, 'HorizontalPaddingPx', canvasNumber($row, 'PaddingPx', 0)),
            x: canvasNumber($row, 'DesktopTranslateXPx', 0), y: canvasNumber($row, 'DesktopTranslateYPx', 0),
            scale: canvasNumber($row, 'DesktopScalePercent', 100), rotate: canvasNumber($row, 'DesktopRotateDeg', 0),
            width: canvasNumber($row, 'ElementWidthPercent', 100), minHeight: canvasNumber($row, 'ElementMinHeightPx', 0),
            visible: Boolean(canvasFieldValue($row, 'ShowDesktop', true))
        };
        if (currentCanvasDevice === 'tablet') {
            const align = String(canvasFieldValue($row, 'TabletAlignment', 'Inherit'));
            const inherit = function (field, desktopValue) {
                const value = canvasNumber($row, field, -1);
                return value < 0 ? desktopValue : value;
            };
            return {
                align: align === 'Inherit' ? desktop.align : align.toLowerCase(),
                top: inherit('TabletTopSpacingPx', desktop.top), bottom: inherit('TabletBottomSpacingPx', desktop.bottom),
                pad: inherit('TabletPaddingPx', desktop.pad), padX: inherit('TabletHorizontalPaddingPx', desktop.padX),
                x: canvasNumber($row, 'TabletTranslateXPx', 0), y: canvasNumber($row, 'TabletTranslateYPx', 0),
                scale: canvasNumber($row, 'TabletScalePercent', 100), rotate: canvasNumber($row, 'TabletRotateDeg', 0),
                width: canvasNumber($row, 'TabletWidthPercent', -1) >= 20 ? canvasNumber($row, 'TabletWidthPercent', desktop.width) : desktop.width,
                minHeight: inherit('TabletMinHeightPx', desktop.minHeight),
                visible: Boolean(canvasFieldValue($row, 'ShowTablet', true))
            };
        }
        if (currentCanvasDevice === 'mobile') {
            return {
                align: String(canvasFieldValue($row, 'MobileAlignment', 'Center')).toLowerCase(),
                top: canvasNumber($row, 'MobileTopSpacingPx', 0), bottom: canvasNumber($row, 'MobileBottomSpacingPx', 18),
                pad: canvasNumber($row, 'MobilePaddingPx', 0), padX: canvasNumber($row, 'MobileHorizontalPaddingPx', canvasNumber($row, 'MobilePaddingPx', 0)),
                x: canvasNumber($row, 'MobileTranslateXPx', 0), y: canvasNumber($row, 'MobileTranslateYPx', 0),
                scale: canvasNumber($row, 'MobileScalePercent', 100), rotate: canvasNumber($row, 'MobileRotateDeg', 0),
                width: canvasNumber($row, 'MobileWidthPercent', -1) >= 20 ? canvasNumber($row, 'MobileWidthPercent', desktop.width) : desktop.width,
                minHeight: canvasNumber($row, 'MobileMinHeightPx', -1) < 0 ? desktop.minHeight : canvasNumber($row, 'MobileMinHeightPx', desktop.minHeight),
                visible: Boolean(canvasFieldValue($row, 'ShowMobile', true))
            };
        }
        return desktop;
    }

    function canvasElementColors($row) {
        const preset = String(canvasFieldValue($row, 'Background', 'White'));
        const dark = ['Olive', 'Steel'].includes(preset);
        let background = canvasPaletteColor(preset);
        let text = dark ? '#ffffff' : '#30382a';
        let heading = text;
        let border = String(canvasFieldValue($row, 'CustomBorderColor', '#c3ae83'));
        let opacity = Math.max(0, Math.min(100, canvasNumber($row, 'SectionOpacityPercent', 100))) / 100;
        let backgroundImage = 'none';

        if (String(canvasFieldValue($row, 'DesignMode', 'Global')) === 'Custom') {
            background = String(canvasFieldValue($row, 'CustomBackgroundColor', '#ffffff'));
            text = String(canvasFieldValue($row, 'CustomTextColor', '#30382a'));
            heading = String(canvasFieldValue($row, 'CustomHeadingColor', text));
        }

        const backgroundEffect = String(canvasFieldValue($row, 'BackgroundEffect', 'None'));
        if (backgroundEffect === 'Gradient') {
            const angle = canvasNumber($row, 'GradientAngleDeg', 135);
            const start = String(canvasFieldValue($row, 'GradientStartColor', '#30382a'));
            const end = String(canvasFieldValue($row, 'GradientEndColor', '#c3ae83'));
            backgroundImage = 'linear-gradient(' + angle + 'deg,' + start + ',' + end + ')';
        } else if (backgroundEffect === 'Image') {
            const url = String(canvasFieldValue($row, 'BackgroundImageUrl', '') || '');
            if (url) {
                backgroundImage = 'url("' + url.replace(/"/g, '%22') + '")';
            }
        }

        if (String($row.attr('data-section-type') || '') === 'hero' && backgroundEffect === 'None') {
            const heroUrl = String(canvasFieldValue($row, 'MediaUrl', '') || '');
            if (heroUrl) {
                backgroundImage = 'url("' + heroUrl.replace(/"/g, '%22') + '")';
            }
        }

        if (currentCanvasState === 'hover' && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom') {
            background = String(canvasFieldValue($row, 'HoverBackgroundColor', background));
            text = String(canvasFieldValue($row, 'HoverTextColor', text));
            heading = String(canvasFieldValue($row, 'HoverHeadingColor', heading));
            border = String(canvasFieldValue($row, 'HoverBorderColor', border));
            opacity = Math.max(0, Math.min(100, canvasNumber($row, 'HoverOpacityPercent', 100))) / 100;
            backgroundImage = 'none';
        }

        if (currentCanvasState === 'disabled') {
            opacity *= Math.max(10, Math.min(100, canvasNumber($row, 'DisabledOpacityPercent', 55))) / 100;
        }
        return { background: background, text: text, heading: heading, border: border, opacity: opacity, backgroundImage: backgroundImage };
    }

    function canvasEditableNode(tagName, className, fieldName, value, fallback) {
        const $node = $('<' + tagName + '>', { class: className + ' h18-canvas-inline-edit', text: String(value || fallback || '') });
        $node.attr({ 'data-canvas-edit-field': fieldName, contenteditable: 'false', spellcheck: 'true', title: 'Dobbeltklik for at redigere direkte' });
        return $node;
    }

    function canvasAddBodyText($target, value) {
        const html = String(value || '').trim();
        if (!html) {
            return;
        }
        const $body = $('<div>', { class: 'h18-canvas-preview-text h18-canvas-rich-edit' });
        $body.html(html);
        $body.attr({
            'data-canvas-edit-field': 'Content',
            contenteditable: 'false',
            spellcheck: 'true',
            title: 'Dobbeltklik for at redigere brødtekst direkte'
        });
        $target.append($body);
    }

    function canvasImageSettings($row) {
        const aspectValue = String(canvasFieldValue($row, 'ImageAspectRatio', 'Auto'));
        const aspectMap = { Auto: 'auto', '1:1': '1 / 1', '4:3': '4 / 3', '3:2': '3 / 2', '16:9': '16 / 9' };
        const heightField = currentCanvasDevice === 'mobile' ? 'MobileImageHeightPx' : 'ImageHeightPx';
        const widthField = currentCanvasDevice === 'mobile' ? 'MobileImageWidthPercent' : 'ImageWidthPercent';
        const locked = Boolean(canvasFieldValue($row, 'ImageAspectLocked', false));
        return {
            aspect: aspectMap[aspectValue] || 'auto',
            aspectValue: aspectValue,
            fit: String(canvasFieldValue($row, 'ImageFit', 'Cover')).toLowerCase(),
            x: Math.max(0, Math.min(100, canvasNumber($row, 'ImageFocalXPercent', 50))),
            y: Math.max(0, Math.min(100, canvasNumber($row, 'ImageFocalYPercent', 50))),
            heightField: heightField,
            height: Math.max(0, canvasNumber($row, heightField, 0)),
            widthField: widthField,
            width: Math.max(20, Math.min(100, canvasNumber($row, widthField, 100))),
            maxWidth: Math.max(0, canvasNumber($row, 'ImageMaxWidthPx', 0)),
            locked: locked
        };
    }

    function canvasApplySectionImageStyle($row, $scope) {
        if (!$row || !$row.length || !$scope || !$scope.length) { return; }
        const settings = canvasImageSettings($row);
        $scope.find('img').css({
            width: settings.width + '%',
            maxWidth: settings.maxWidth > 0 ? settings.maxWidth + 'px' : 'none',
            marginInline: 'auto',
            height: settings.locked && settings.aspectValue !== 'Auto' ? 'auto' : (settings.height > 0 ? settings.height + 'px' : 'auto'),
            aspectRatio: settings.aspect,
            objectFit: settings.fit,
            objectPosition: settings.x + '% ' + settings.y + '%'
        });
    }

    function canvasOpenSectionMedia($row) {
        if (!$row || !$row.length || typeof wp === 'undefined' || !wp.media) { return; }
        const frame = wp.media({
            title: Hangar18Manager.chooseImage,
            button: { text: Hangar18Manager.useImage },
            multiple: false,
            library: { type: 'image' }
        });
        frame.on('select', function () {
            const image = frame.state().get('selection').first().toJSON();
            const preview = image.sizes && image.sizes.thumbnail ? image.sizes.thumbnail.url : image.url;
            canvasSetField($row, 'MediaId', image.id || '');
            canvasSetField($row, 'MediaUrl', image.url || '');
            pageSectionControls($row, '.h18-section-media-preview').html($('<img>', { src: preview, alt: image.alt || '' }));
            renderCanvasPreview($row);
        });
        frame.open();
    }

    function canvasImageSelect(label, fieldName, value, options) {
        const $select = $('<select>', { class: 'h18-canvas-image-control', 'data-image-control-field': fieldName });
        options.forEach(function (item) {
            $select.append($('<option>', { value: item[0], text: item[1], selected: String(value) === String(item[0]) }));
        });
        return $('<label>', { class: 'h18-canvas-image-select' }).append($('<span>', { text: label }), $select);
    }

    function canvasImageRange(label, fieldName, value, min, max, suffix) {
        return $('<label>', { class: 'h18-canvas-image-range' }).append(
            $('<span>', { text: label }),
            $('<input>', { type: 'range', min: min, max: max, step: 1, value: Math.round(value), 'data-image-control-field': fieldName }),
            $('<output>', { text: Math.round(value) + (suffix || '') })
        );
    }

    function renderCanvasImageTools($row, $preview) {
        if (!$row.hasClass('is-selected')) { return; }
        const type = String($row.attr('data-section-type') || '');
        if (!['image', 'text_image'].includes(type)) { return; }
        const $media = $preview.find('.h18-canvas-editable-media').first();
        if (!$media.length) { return; }
        const settings = canvasImageSettings($row);
        const $tools = $('<div>', { class: 'h18-canvas-image-tools' }).append(
            $('<strong>', { text: 'Billede' }),
            $('<div>', { class: 'h18-canvas-image-actions' }).append(
                $('<button>', { type: 'button', class: 'button button-small h18-canvas-image-change', text: 'Skift billede' }),
                $('<button>', { type: 'button', class: 'button-link-delete h18-canvas-image-remove', text: 'Fjern' })
            ),
            canvasImageSelect('Format', 'ImageAspectRatio', settings.aspectValue, [['Auto','Auto'],['1:1','1:1'],['4:3','4:3'],['3:2','3:2'],['16:9','16:9']]),
            canvasImageSelect('Tilpas', 'ImageFit', String(canvasFieldValue($row, 'ImageFit', 'Cover')), [['Cover','Fyld'],['Contain','Hele billedet']]),
            canvasImageRange('Fokus X', 'ImageFocalXPercent', settings.x, 0, 100, '%'),
            canvasImageRange('Fokus Y', 'ImageFocalYPercent', settings.y, 0, 100, '%'),
            canvasImageRange(currentCanvasDevice === 'mobile' ? 'Bredde mobil' : 'Bredde', settings.widthField, settings.width, 20, 100, '%'),
            canvasImageRange('Maks. bredde', 'ImageMaxWidthPx', settings.maxWidth, 0, 2000, ' px'),
            canvasImageRange(currentCanvasDevice === 'mobile' ? 'Højde mobil' : 'Højde', settings.heightField, settings.height, 0, currentCanvasDevice === 'mobile' ? 900 : 1200, ' px'),
            $('<button>', { type: 'button', class: 'button button-small h18-canvas-aspect-lock', text: settings.locked ? '🔒 Format låst' : '🔓 Format frit', title: settings.locked ? 'Klik for at frigive billedformatet' : 'Klik for at låse det valgte billedformat' })
        );
        if (settings.locked && settings.aspectValue !== 'Auto') {
            $tools.find('[data-image-control-field="' + settings.heightField + '"]').prop('disabled', true).closest('.h18-canvas-image-range').attr('title', 'Højden styres af det låste billedformat.');
        }
        const $dot = $('<button>', {
            type: 'button', class: 'h18-canvas-focal-dot',
            'aria-label': 'Træk fokuspunkt', title: 'Træk for at flytte fokuspunkt'
        }).css({ left: settings.x + '%', top: settings.y + '%' });
        $media.append($tools, $dot);
    }

    function canvasBuildPreviewContent($row, $preview) {
        const type = String($row.attr('data-section-type') || 'text');
        const title = String(canvasFieldValue($row, 'Title', ''));
        const content = String(canvasFieldValue($row, 'Content', ''));
        const $inner = $('<div>', { class: 'h18-canvas-preview-inner h18-canvas-type-' + type });
        const addTitle = function (fallback) {
            if (title || fallback) {
                $inner.append(canvasEditableNode('h2', 'h18-canvas-preview-title', 'Title', title, fallback));
            }
        };
        const addButtons = function () {
            const labels = [
                ['Button1Label', canvasFieldValue($row, 'Button1Label', '')],
                ['Button2Label', canvasFieldValue($row, 'Button2Label', '')]
            ];
            const $actions = $('<div>', { class: 'h18-canvas-preview-actions' });
            labels.forEach(function (item, index) {
                if (!String(item[1] || '')) { return; }
                const $button = canvasEditableNode('span', 'h18-canvas-preview-button' + (index ? ' is-secondary' : ''), item[0], item[1], 'Knap');
                $button.attr('role', 'button');
                $actions.append($button);
            });
            if ($actions.children().length) { $inner.append($actions); }
        };

        if (type === 'hero') {
            addTitle('Hero-overskrift');
            canvasAddBodyText($inner, content);
            addButtons();
        } else if (type === 'text_image') {
            const $grid = $('<div>', { class: 'h18-canvas-text-image' });
            const $copy = $('<div>', { class: 'h18-canvas-text-image-copy' });
            if (title) { $copy.append(canvasEditableNode('h2', 'h18-canvas-preview-title', 'Title', title, 'Overskrift')); }
            canvasAddBodyText($copy, content);
            const url = String(canvasFieldValue($row, 'MediaUrl', '') || '');
            const $media = $('<div>', { class: 'h18-canvas-preview-media h18-canvas-editable-media', tabindex: '0', role: 'button', title: 'Klik for billedkontroller · dobbeltklik for at skifte billede' });
            if (url) { $media.append($('<img>', { src: url, alt: '' })); } else { $media.append($('<span>', { class: 'h18-canvas-image-placeholder', text: 'Vælg billede' })); }
            canvasApplySectionImageStyle($row, $media);
            if (String(canvasFieldValue($row, 'ImagePosition', 'Right')) === 'Left' && currentCanvasDevice !== 'mobile') {
                $grid.append($media, $copy);
            } else {
                $grid.append($copy, $media);
            }
            $inner.append($grid);
        } else if (type === 'image') {
            addTitle('Billede');
            const url = String(canvasFieldValue($row, 'MediaUrl', '') || '');
            const $image = $('<div>', { class: 'h18-canvas-preview-image h18-canvas-editable-media', tabindex: '0', role: 'button', title: 'Klik for billedkontroller · dobbeltklik for at skifte billede' });
            if (url) { $image.append($('<img>', { src: url, alt: '' })); } else { $image.append($('<span>', { class: 'h18-canvas-image-placeholder', text: 'Intet billede valgt' })); }
            canvasApplySectionImageStyle($row, $image);
            $inner.append($image);
        } else if (type === 'icon') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'check'));
            const symbols = { check: '✓', star: '★', info: 'ⓘ', location: '⌖', calendar: '▣', phone: '☎', mail: '✉', wrench: '⌕', shield: '◆', arrow: '→' };
            $inner.append($('<div>', { class: 'h18-canvas-primitive-icon', text: symbols[variant] || '✓', title: title || inspectorTypeLabel(type) }));
            if (content) { canvasAddBodyText($inner, content); }
        } else if (type === 'divider') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'solid'));
            $inner.append($('<hr>', { class: 'h18-canvas-primitive-divider h18-canvas-primitive-divider--' + variant }));
        } else if (type === 'list') {
            addTitle('Liste');
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'bullets'));
            const text = $('<div>').html(content).text();
            const items = text.split(/\r?\n|•/).map(function (item) { return item.trim(); }).filter(Boolean).slice(0, 8);
            const $list = $(variant === 'numbers' ? '<ol>' : '<ul>', { class: variant === 'checks' ? 'h18-canvas-list-checks' : '' });
            (items.length ? items : ['Listepunkt']).forEach(function (item) { $list.append($('<li>', { text: item })); });
            $inner.append($list);
        } else if (type === 'badge') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'solid'));
            $inner.append($('<span>', { class: 'h18-canvas-primitive-badge h18-canvas-primitive-badge--' + variant, text: title || $('<div>').html(content).text() || 'Badge' }));
        } else if (type === 'quote') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'standard'));
            const $quote = $('<figure>', { class: 'h18-canvas-primitive-quote h18-canvas-primitive-quote--' + variant });
            $quote.append($('<blockquote>', { text: $('<div>').html(content).text() || 'Citat' }));
            if (title) { $quote.append($('<figcaption>', { text: '— ' + title })); }
            $inner.append($quote);
        } else if (type === 'embed') {
            addTitle('Embed');
            $inner.append($('<div>', { class: 'h18-canvas-embed-placeholder' }).append($('<span>', { class: 'dashicons dashicons-video-alt3' }), $('<code>', { text: content || 'Indsæt en medie-URL' })));
        } else if (type === 'shortcode') {
            addTitle('Shortcode');
            $inner.append($('<pre>', { class: 'h18-canvas-shortcode-placeholder' }).append($('<code>', { text: content || '[shortcode]' })));
        } else if (type === 'buttons') {
            addTitle('Handling');
            canvasAddBodyText($inner, content);
            addButtons();
        } else if (['container','flex','grid'].includes(type)) {
            addTitle(type === 'grid' ? 'Grid container' : (type === 'flex' ? 'Flex container' : 'Container'));
            canvasAddBodyText($inner, content);
            const selfKey = String($row.find('.h18-page-section-key').val() || '');
            const childCount = $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').filter(function () { return String(pageSectionControls($(this), '.h18-layout-parent-key').val() || '') === selfKey; }).length;
            const detail = type === 'grid' ? String(canvasFieldValue($row,'LayoutColumns',2)) + ' kolonner' : (type === 'flex' ? String(canvasFieldValue($row,'LayoutDirection','Row')) + ' · gap ' + String(canvasFieldValue($row,'LayoutGapPx',16)) + ' px' : 'blok-container');
            $inner.append($('<div>', { class: 'h18-canvas-layout-shell h18-canvas-layout-shell--' + type }).append($('<strong>', { text: childCount + ' under-element' + (childCount === 1 ? '' : 'er') }), $('<small>', { text: detail })));
        } else if (type === 'component') {
            const componentId = String(canvasFieldValue($row, 'ComponentId', ''));
            const component = pageLinkedComponents[componentId];
            const overrides = parseComponentOverridesV0521($row);
            $inner.append($('<div>', { class: 'h18-canvas-linked-component' }).append(
                $('<span>', { class: 'dashicons dashicons-admin-links' }),
                $('<div>').append($('<strong>', { text: component ? String(component.Name || 'Linked component') : 'Vælg linked component' }), $('<small>', { text: component ? 'Global revision ' + String(component.Revision || 1) + (String(canvasFieldValue($row,'ComponentVariant','')) ? ' · variant' : ' · base') + ' · ' + Object.keys(overrides).length + ' lokal(e) override(s)' : 'Ingen definition valgt' }))
            ));
        } else if (type === 'carousel') {
            addTitle('Carousel');
            canvasAddBodyText($inner, content);
            const $slides = pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').filter(function () { return $(this).find('[name$="[Active]"]').is(':checked'); });
            const $carousel = $('<div>', { class: 'h18-canvas-carousel' });
            const $stage = $('<div>', { class: 'h18-canvas-carousel-stage' });
            if ($slides.length) {
                const $card = $slides.first();
                const cardTitle = String($card.find('.h18-page-card-title').val() || 'Slide 1');
                $stage.append($('<strong>', { text: cardTitle }), $('<div>', { class: 'h18-canvas-carousel-body' }).html(String($card.find('[name$="[Content]"]').val() || '')));
            } else {
                $stage.text('Tilføj mindst ét slide.');
            }
            const showArrows = Boolean(canvasFieldValue($row, 'CarouselShowArrows', true));
            const showDots = Boolean(canvasFieldValue($row, 'CarouselShowDots', true));
            if (showArrows && $slides.length > 1) { $carousel.append($('<span>', { class: 'h18-canvas-carousel-arrow is-prev', text: '‹' })); }
            $carousel.append($stage);
            if (showArrows && $slides.length > 1) { $carousel.append($('<span>', { class: 'h18-canvas-carousel-arrow is-next', text: '›' })); }
            if (showDots && $slides.length > 1) {
                const $dots = $('<div>', { class: 'h18-canvas-carousel-dots' });
                $slides.each(function (i) { $dots.append($('<span>', { class: 'h18-canvas-carousel-dot' + (i === 0 ? ' is-active' : '') })); });
                $carousel.append($dots);
            }
            $inner.append($carousel);
        } else if (type === 'tabs') {
            addTitle('Faner');
            canvasAddBodyText($inner, content);
            const $cards = pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').filter(function () { return $(this).find('[name$="[Active]"]').is(':checked'); });
            const $tabs = $('<div>', { class: 'h18-canvas-tabs-nav' });
            const $panel = $('<div>', { class: 'h18-canvas-tabs-panel' });
            if (!$cards.length) { $panel.text('Tilføj mindst ét panel.'); }
            $cards.each(function (index) {
                const $card = $(this);
                const cardTitle = String($card.find('.h18-page-card-title').val() || ('Fane ' + (index + 1)));
                $tabs.append($('<button>', { type: 'button', class: 'h18-canvas-tab' + (index === 0 ? ' is-active' : ''), text: cardTitle, tabindex: -1 }));
                if (index === 0) { $panel.html(String($card.find('[name$="[Content]"]').val() || '')); }
            });
            $inner.append($tabs, $panel);
        } else if (type === 'accordion') {
            addTitle('Accordion');
            canvasAddBodyText($inner, content);
            const $accordion = $('<div>', { class: 'h18-canvas-accordion' });
            pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').filter(function () { return $(this).find('[name$="[Active]"]').is(':checked'); }).each(function (index) {
                const $card = $(this);
                const cardTitle = String($card.find('.h18-page-card-title').val() || ('Punkt ' + (index + 1)));
                const $item = $('<div>', { class: 'h18-canvas-accordion-item' });
                $item.append($('<strong>', { text: cardTitle }), $('<span>', { text: index === 0 ? '−' : '+' }));
                if (index === 0) { $item.append($('<div>', { class: 'h18-canvas-accordion-body' }).html(String($card.find('[name$="[Content]"]').val() || ''))); }
                $accordion.append($item);
            });
            $inner.append($accordion);
        } else if (type === 'card_grid') {
            addTitle('Kort-række');
            canvasAddBodyText($inner, content);
            const columns = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileColumns', 1) : canvasNumber($row, 'Columns', 3);
            const gap = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileColumnGapPx', 14) : canvasNumber($row, 'ColumnGapPx', 16);
            const $grid = $('<div>', { class: 'h18-canvas-card-grid' }).css({ gridTemplateColumns: 'repeat(' + Math.max(1, Math.min(6, columns)) + ',minmax(0,1fr))', gap: gap + 'px' });
            pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').each(function () {
                const $card = $(this);
                const key = canvasCardKey($card);
                const active = $card.find('[name$="[Active]"]').is(':checked');
                const $cardPreview = $('<article>', {
                    class: 'h18-canvas-card' + (selectedCanvasCardKey === key ? ' is-card-selected' : '') + (active ? '' : ' is-card-inactive'),
                    'data-card-key': key, tabindex: '0', role: 'button'
                });
                $cardPreview.append($('<button>', { type: 'button', class: 'h18-canvas-card-drag-handle', title: 'Træk for at flytte kort', 'aria-label': 'Flyt kort' }).append($('<span>', { class: 'dashicons dashicons-move' })));
                const titleValue = String(canvasCardFieldValue($card, 'Title', ''));
                $cardPreview.append($('<strong>', {
                    class: 'h18-canvas-card-title h18-canvas-card-inline-edit', text: titleValue || 'Kort uden overskrift',
                    'data-card-edit-field': 'Title', contenteditable: 'false', spellcheck: 'true', title: 'Dobbeltklik for at redigere kortets overskrift'
                }));
                const contentHtml = String(canvasCardFieldValue($card, 'Content', '') || '').trim();
                const $content = $('<div>', {
                    class: 'h18-canvas-card-content h18-canvas-card-rich-edit' + (contentHtml ? '' : ' is-empty'),
                    'data-card-edit-field': 'Content', contenteditable: 'false', spellcheck: 'true', title: 'Dobbeltklik for at redigere kortets tekst'
                });
                if (contentHtml) { $content.html(contentHtml); } else { $content.text('Dobbeltklik for at tilføje tekst'); }
                $cardPreview.append($content);
                if (!active) { $cardPreview.append($('<span>', { class: 'h18-canvas-card-inactive-label', text: 'Skjult på siden' })); }
                canvasApplyCardPreviewStyle($card, $cardPreview);
                if (selectedCanvasCardKey === key) { canvasBuildCardTools($card, $cardPreview); }
                $grid.append($cardPreview);
            });
            if (!$grid.children().length) { $grid.append($('<div>', { class: 'h18-canvas-card', text: 'Tilføj et kort i Inspector' })); }
            $inner.append($grid);
        } else if (type === 'mail_form') {
            addTitle('Kontaktformular');
            canvasAddBodyText($inner, content);
            $inner.append($('<div>', { class: 'h18-canvas-fake-form' }).append(
                $('<span>', { text: 'Navn' }), $('<span>', { text: 'E-mail' }), $('<span>', { class: 'is-wide', text: 'Besked' }), $('<b>', { text: 'Send besked' })
            ));
        } else if (type === 'poll') {
            addTitle('Afstemning');
            canvasAddBodyText($inner, content);
            $inner.append($('<div>', { class: 'h18-canvas-poll' }).append(
                $('<span>', { text: '○ Svarmulighed 1' }), $('<span>', { text: '○ Svarmulighed 2' }), $('<b>', { text: 'Stem' })
            ));
        } else if (type === 'spacer') {
            const height = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileSpacerPx', 24) : canvasNumber($row, 'SpacerPx', 32);
            $inner.append($('<div>', { class: 'h18-canvas-spacer', text: 'Afstand · ' + height + ' px' }).css('minHeight', Math.max(24, height) + 'px'));
        } else if (type === 'css') {
            $inner.append($('<div>', { class: 'h18-canvas-code-block' }).append($('<strong>', { text: 'Side-CSS' }), $('<small>', { text: 'CSS påvirker siden efter gemning og vises ikke som rå kode i canvas.' })));
        } else if (type === 'html' || type === 'legacy') {
            addTitle(type === 'legacy' ? 'Eksisterende indhold' : 'HTML-blok');
            canvasAddBodyText($inner, type === 'legacy' ? canvasFieldValue($row, 'LegacyHtml', content) : content);
        } else {
            addTitle(type === 'highlight' ? 'Fremhævet tekst' : (type === 'card' ? 'Indholdskort' : 'Overskrift'));
            canvasAddBodyText($inner, content);
            addButtons();
        }

        $preview.empty().append($inner);
        renderCanvasImageTools($row, $preview);
    }


    function canvasCardKey($card) {
        return String($card.find('.h18-page-card-key').val() || $card.attr('data-card-index') || '');
    }

    function canvasCardFieldValue($card, fieldName, fallback) {
        const $field = $card.find('[name$="[' + fieldName + ']"]').first();
        if (!$field.length) { return fallback; }
        if ($field.is(':checkbox')) { return $field.is(':checked'); }
        const value = $field.val();
        return value == null || value === '' ? fallback : value;
    }

    function canvasCardSetField($card, fieldName, value) {
        const $field = $card.find('[name$="[' + fieldName + ']"]').first();
        if (!$field.length) { return false; }
        if ($field.is(':checkbox')) { $field.prop('checked', Boolean(value)); } else { $field.val(value); }
        return true;
    }

    function canvasCardNumber($card, fieldName, fallback) {
        const value = parseFloat(canvasCardFieldValue($card, fieldName, fallback));
        return Number.isFinite(value) ? value : fallback;
    }

    function canvasCardBorderColor(value) {
        const borders = { None: 'transparent', Sand: '#c3ae83', Olive: '#30382a', Steel: '#525a5f' };
        return borders[String(value || 'Sand')] || '#c3ae83';
    }

    function canvasCardTextColor($card) {
        const background = String(canvasCardFieldValue($card, 'Background', 'OffWhite'));
        const tone = String(canvasCardFieldValue($card, 'TextTone', 'Auto'));
        return tone === 'Light' || (tone === 'Auto' && ['Olive', 'Steel'].includes(background)) ? '#ffffff' : '#30382a';
    }

    function canvasFindCardRow($row, cardKey) {
        let $match = $();
        pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').each(function () {
            const $card = $(this);
            if (canvasCardKey($card) === String(cardKey || '')) { $match = $card; return false; }
        });
        return $match;
    }

    function canvasApplyCardPreviewStyle($card, $cardPreview) {
        if (!$card.length || !$cardPreview.length) { return; }
        const mobile = currentCanvasDevice === 'mobile';
        const paddingField = mobile ? 'MobilePaddingPx' : 'PaddingPx';
        const alignField = mobile ? 'MobileAlignment' : 'DesktopAlignment';
        const padding = Math.max(0, Math.min(mobile ? 60 : 80, canvasCardNumber($card, paddingField, mobile ? 20 : 26)));
        const radius = Math.max(0, Math.min(30, canvasCardNumber($card, 'RadiusPx', 7)));
        const borderWidth = Math.max(0, Math.min(8, canvasCardNumber($card, 'BorderWidthPx', 0)));
        $cardPreview.css({
            background: canvasPaletteColor(canvasCardFieldValue($card, 'Background', 'OffWhite')),
            color: canvasCardTextColor($card),
            borderStyle: 'solid', borderWidth: borderWidth + 'px', borderColor: canvasCardBorderColor(canvasCardFieldValue($card, 'BorderColor', 'Sand')),
            padding: padding + 'px', borderRadius: radius + 'px',
            textAlign: String(canvasCardFieldValue($card, alignField, 'Left')) === 'Center' ? 'center' : 'left'
        });
    }

    function canvasCardRange(label, fieldName, value, min, max) {
        return $('<label>', { class: 'h18-canvas-card-range' }).append(
            $('<span>', { text: label }),
            $('<input>', { type: 'range', min: min, max: max, step: 1, value: Math.round(value), 'data-card-control-field': fieldName }),
            $('<output>', { text: Math.round(value) + ' px' })
        );
    }

    function canvasCardSelect(label, fieldName, value, options) {
        const $select = $('<select>', { class: 'h18-canvas-card-control', 'data-card-control-field': fieldName });
        options.forEach(function (option) { $select.append($('<option>', { value: option[0], text: option[1], selected: String(value) === String(option[0]) })); });
        return $('<label>', { class: 'h18-canvas-card-select' }).append($('<span>', { text: label }), $select);
    }

    function canvasBuildCardTools($card, $cardPreview) {
        const mobile = currentCanvasDevice === 'mobile';
        const paddingField = mobile ? 'MobilePaddingPx' : 'PaddingPx';
        const alignField = mobile ? 'MobileAlignment' : 'DesktopAlignment';
        $cardPreview.append($('<div>', { class: 'h18-canvas-card-tools' }).append(
            $('<strong>', { text: 'Kortdesign' }),
            canvasCardSelect('Baggrund', 'Background', canvasCardFieldValue($card, 'Background', 'OffWhite'), [['White','Hvid'],['OffWhite','Knækket hvid'],['Sand','Sand'],['Olive','Oliven'],['Steel','Stål']]),
            canvasCardSelect('Tekst', 'TextTone', canvasCardFieldValue($card, 'TextTone', 'Auto'), [['Auto','Auto'],['Dark','Mørk'],['Light','Lys']]),
            canvasCardSelect('Placering', alignField, canvasCardFieldValue($card, alignField, 'Left'), [['Left','Venstre'],['Center','Midt']]),
            canvasCardRange('Padding', paddingField, canvasCardNumber($card, paddingField, mobile ? 20 : 26), 0, mobile ? 60 : 80),
            canvasCardRange('Radius', 'RadiusPx', canvasCardNumber($card, 'RadiusPx', 7), 0, 30),
            canvasCardRange('Kant', 'BorderWidthPx', canvasCardNumber($card, 'BorderWidthPx', 0), 0, 8),
            $('<label>', { class: 'h18-canvas-card-active' }).append($('<input>', { type: 'checkbox', class: 'h18-canvas-card-control', 'data-card-control-field': 'Active', checked: Boolean(canvasCardFieldValue($card, 'Active', true)) }), $('<span>', { text: 'Aktiv' }))
        ));
    }

    function canvasFocusCardEditor($row, cardKey) {
        pageSectionControls($row, '.h18-page-card-row').removeClass('is-canvas-selected-card');
        const $card = canvasFindCardRow($row, cardKey);
        if ($card.length) {
            $card.addClass('is-canvas-selected-card');
            $pageInspector.find('.h18-builder-inspector-heading span').text('Kort-række · ' + String(canvasCardFieldValue($card, 'Title', '') || 'Kort uden overskrift'));
        }
        return $card;
    }

    function initializeCanvasCardGridPreview($row, $preview) {
        const $grid = $preview.find('.h18-canvas-card-grid');
        if (!$grid.length || $grid.hasClass('ui-sortable')) { return; }
        $grid.sortable({
            items: '> .h18-canvas-card[data-card-key]', handle: '.h18-canvas-card-drag-handle', tolerance: 'pointer', placeholder: 'h18-canvas-card-sort-placeholder',
            update: function () {
                const keys = $grid.children('.h18-canvas-card[data-card-key]').map(function () { return String($(this).data('card-key') || ''); }).get();
                const $container = pageSectionControls($row, '.h18-page-cards-sortable').first();
                keys.forEach(function (key) { const $card = canvasFindCardRow($row, key); if ($card.length) { $container.append($card); } });
                syncPageCardOrder($container);
                renderCanvasPreview($row);
            }
        });
    }

    function ensureCanvasPreview($row) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return $(); }
        let $preview = $row.children('.h18-canvas-preview');
        if (!$preview.length) {
            $preview = $('<div>', { class: 'h18-canvas-preview', tabindex: '0', role: 'button' });
            $row.children('.h18-page-section-header').after($preview);
        }
        return $preview;
    }

    function renderCanvasPreview($row) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return; }
        const $preview = ensureCanvasPreview($row);
        if (!$preview.length) { return; }
        const type = String($row.attr('data-section-type') || 'text');
        const layout = canvasDeviceLayout($row);
        const colors = canvasElementColors($row);
        const radius = canvasNumber($row, 'RadiusPx', 7);
        const tl = canvasNumber($row, 'RadiusTopLeftPx', -1);
        const tr = canvasNumber($row, 'RadiusTopRightPx', -1);
        const br = canvasNumber($row, 'RadiusBottomRightPx', -1);
        const bl = canvasNumber($row, 'RadiusBottomLeftPx', -1);
        let scale = layout.scale / 100;
        let translateY = layout.y;
        let shadow = canvasShadow(canvasFieldValue($row, 'ShadowStyle', 'None'));
        if (currentCanvasState === 'hover') {
            const effect = String(canvasFieldValue($row, 'HoverEffect', 'None'));
            if (effect === 'Lift') { translateY -= 6; }
            if (effect === 'Scale') { scale *= 1.025; }
            if (effect === 'Shadow') { shadow = '0 16px 38px rgba(0,0,0,.24)'; }
        }
        if (currentCanvasState === 'active') {
            const activeEffect = String(canvasFieldValue($row, 'ActiveEffect', 'None'));
            if (activeEffect === 'Press') { translateY += 1; }
            if (activeEffect === 'ScaleDown') { scale *= 0.97; }
        }
        const focusPreview = currentCanvasState === 'focus' && String(canvasFieldValue($row, 'FocusRingStyle', 'Global')) !== 'None';
        const focusColor = String(canvasFieldValue($row, 'FocusRingColor', '#8b4a2b'));
        const focusWidth = Math.max(1, Math.min(8, canvasNumber($row, 'FocusRingWidthPx', 3)));
        const focusOffset = Math.max(0, Math.min(12, canvasNumber($row, 'FocusRingOffsetPx', 2)));
        if (focusPreview) { shadow = '0 0 0 ' + focusOffset + 'px transparent,0 0 0 ' + (focusOffset + focusWidth) + 'px ' + focusColor; }
        const effectPosition = String(canvasFieldValue($row, 'BackgroundImagePosition', 'Center')).toLowerCase();
        const effectSize = String(canvasFieldValue($row, 'BackgroundImageSize', 'Cover')).toLowerCase();
        const borderWidth = canvasNumber($row, 'BorderWidthPx', 0);
        const bodySize = canvasNumber($row, 'BodyFontSizePx', 0);
        const h2Size = canvasNumber($row, 'H2FontSizePx', 0);

        canvasBuildPreviewContent($row, $preview);
        initializeCanvasCardGridPreview($row, $preview);
        $preview.removeAttr('style').css({
            backgroundColor: colors.background,
            backgroundImage: colors.backgroundImage,
            backgroundPosition: effectPosition,
            backgroundSize: effectSize,
            backgroundRepeat: 'no-repeat',
            color: colors.text,
            opacity: colors.opacity,
            borderStyle: 'solid', borderWidth: borderWidth + 'px', borderColor: colors.border,
            borderRadius: (tl < 0 ? radius : tl) + 'px ' + (tr < 0 ? radius : tr) + 'px ' + (br < 0 ? radius : br) + 'px ' + (bl < 0 ? radius : bl) + 'px',
            boxShadow: shadow,
            textAlign: layout.align,
            padding: layout.pad + 'px ' + layout.padX + 'px',
            marginTop: Math.max(0, layout.top) + 'px', marginBottom: Math.max(0, layout.bottom) + 'px',
            width: Math.max(20, Math.min(100, layout.width)) + '%',
            maxWidth: canvasNumber($row, 'ElementMaxWidthPx', 0) > 0 ? canvasNumber($row, 'ElementMaxWidthPx', 0) + 'px' : 'none',
            marginLeft: 'auto', marginRight: 'auto',
            transform: 'translate(' + layout.x + 'px,' + translateY + 'px) scale(' + scale + ') rotate(' + layout.rotate + 'deg)'
        });
        if (bodySize > 0) { $preview.css('fontSize', bodySize + 'px'); }
        if (h2Size > 0) { $preview.find('.h18-canvas-preview-title').css('fontSize', h2Size + 'px'); }
        $preview.find('.h18-canvas-preview-title').css('color', colors.heading);
        $preview.toggleClass('is-device-hidden', !layout.visible);
        $preview.attr('aria-label', inspectorTypeLabel(type) + ' – klik for at redigere');
        $preview.attr('data-canvas-device', currentCanvasDevice).attr('data-canvas-state', currentCanvasState);
        $preview.find('.h18-canvas-device-hidden-label').remove();
        if (!layout.visible) {
            $preview.append($('<span>', { class: 'h18-canvas-device-hidden-label', text: 'Skjult på ' + (currentCanvasDevice === 'mobile' ? 'mobil' : currentCanvasDevice) }));
        }
        if (type === 'hero') {
            const height = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileHeroHeightPx', 220) : canvasNumber($row, 'HeroHeightPx', 320);
            $preview.css('minHeight', Math.max(120, height, Math.max(0, layout.minHeight)) + 'px');
        } else {
            $preview.css('minHeight', Math.max(0, layout.minHeight) + 'px');
        }
        renderCanvasDirectControls($row, $preview, layout, colors);
    }

    function refreshAllCanvasPreviews() {
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            renderCanvasPreview($(this));
        });
        updateCanvasToolbarStatus();
    }

    function updateCanvasToolbarStatus() {
        const deviceLabel = currentCanvasDevice === 'mobile' ? 'Mobil' : currentCanvasDevice.charAt(0).toUpperCase() + currentCanvasDevice.slice(1);
        const stateLabels = { normal: 'Normal', hover: 'Hover', focus: 'Focus', active: 'Aktiv', disabled: 'Disabled' };
        const stateLabel = stateLabels[currentCanvasState] || 'Normal';
        $('.h18-builder-canvas').attr('data-canvas-device', currentCanvasDevice).attr('data-canvas-state', currentCanvasState);
        $('#h18-canvas-runtime-status').text(deviceLabel + ' · ' + stateLabel + ' · Live');
    }

    function canvasQuickFields() {
        if (currentCanvasDevice === 'tablet') {
            return { pad: 'TabletPaddingPx', padX: 'TabletHorizontalPaddingPx', top: 'TabletTopSpacingPx', bottom: 'TabletBottomSpacingPx', width: 'TabletWidthPercent', minHeight: 'TabletMinHeightPx' };
        }
        if (currentCanvasDevice === 'mobile') {
            return { pad: 'MobilePaddingPx', padX: 'MobileHorizontalPaddingPx', top: 'MobileTopSpacingPx', bottom: 'MobileBottomSpacingPx', width: 'MobileWidthPercent', minHeight: 'MobileMinHeightPx' };
        }
        return { pad: 'PaddingPx', padX: 'HorizontalPaddingPx', top: 'TopSpacingPx', bottom: 'BottomSpacingPx', width: 'ElementWidthPercent', minHeight: 'ElementMinHeightPx' };
    }

    function canvasSetField($row, fieldName, value) {
        const $field = pageSectionControls($row, '[name$="[' + fieldName + ']"]').first();
        if (!$field.length) { return false; }
        if ($field.is(':checkbox')) {
            $field.prop('checked', Boolean(value));
        } else {
            $field.val(value);
        }
        return true;
    }


    const sectionDesignFields = [
        'Background','DesktopAlignment','TabletAlignment','MobileAlignment','TopSpacingPx','BottomSpacingPx','MobileTopSpacingPx','MobileBottomSpacingPx',
        'TabletTopSpacingPx','TabletBottomSpacingPx','PaddingPx','HorizontalPaddingPx','MobilePaddingPx','MobileHorizontalPaddingPx','TabletPaddingPx','TabletHorizontalPaddingPx',
        'RadiusPx','RadiusTopLeftPx','RadiusTopRightPx','RadiusBottomRightPx','RadiusBottomLeftPx','DesignMode','CustomBackgroundColor','CustomTextColor','CustomHeadingColor',
        'BorderWidthPx','CustomBorderColor','ShadowStyle','SectionBodyFontFamily','SectionHeadingFontFamily','BodyFontSizePx','H1FontSizePx','H2FontSizePx','H3FontSizePx',
        'SectionOpacityPercent','GradientStartColor','GradientEndColor','GradientAngleDeg','HoverEffect','HoverTransitionMs','HoverStyleMode','HoverBackgroundColor','HoverTextColor',
        'HoverHeadingColor','HoverBorderColor','HoverOpacityPercent','DesktopTranslateXPx','DesktopTranslateYPx','DesktopScalePercent','DesktopRotateDeg','TabletTranslateXPx',
        'TabletTranslateYPx','TabletScalePercent','TabletRotateDeg','MobileTranslateXPx','MobileTranslateYPx','MobileScalePercent','MobileRotateDeg','ElementWidthPercent',
        'TabletWidthPercent','MobileWidthPercent','ElementMaxWidthPx','ElementMinHeightPx','TabletMinHeightPx','MobileMinHeightPx'
    ];
    const sectionImageDesignFields = ['ImagePosition','ImageAspectRatio','ImageFit','ImageFocalXPercent','ImageFocalYPercent','ImageHeightPx','MobileImageHeightPx','ImageWidthPercent','MobileImageWidthPercent','ImageMaxWidthPx','ImageAspectLocked'];

    function sectionDesignSnapshot($row) {
        if (!$row || !$row.length || String($row.attr('data-section-type') || '') === 'legacy') { return null; }
        const type = String($row.attr('data-section-type') || 'text');
        const fields = {};
        sectionDesignFields.concat(['image','text_image'].includes(type) ? sectionImageDesignFields : []).forEach(function (fieldName) {
            const $field = pageSectionControls($row, '[name$="[' + fieldName + ']"]').first();
            if (!$field.length) { return; }
            fields[fieldName] = $field.is(':checkbox') ? $field.is(':checked') : $field.val();
        });
        return { Version: '1.0', SourceType: type, Fields: fields };
    }

    function applySectionDesignSnapshot($row, snapshot) {
        if (!$row || !$row.length || !snapshot || !snapshot.Fields) { return 0; }
        const targetType = String($row.attr('data-section-type') || 'text');
        let changed = 0;
        Object.keys(snapshot.Fields).forEach(function (fieldName) {
            if (sectionImageDesignFields.includes(fieldName) && !['image','text_image'].includes(targetType)) { return; }
            if (canvasSetField($row, fieldName, snapshot.Fields[fieldName])) { changed += 1; }
        });
        refreshSectionDesignMode($row);
        refreshHoverStyleMode($row);
        renderCanvasPreview($row);
        return changed;
    }

    function canvasQuickRange(label, fieldName, value, min, max, suffix) {
        const $wrap = $('<label>', { class: 'h18-canvas-quick-range' });
        const $top = $('<span>', { class: 'h18-canvas-quick-range-label' }).append(
            $('<span>', { text: label }),
            $('<output>', { text: String(Math.round(value)) + (suffix || '') })
        );
        const $input = $('<input>', {
            type: 'range', min: min, max: max, step: 1, value: Math.round(value),
            'data-canvas-quick-field': fieldName, 'data-canvas-quick-suffix': suffix || ''
        });
        return $wrap.append($top, $input);
    }

    function canvasQuickColor(label, role, value) {
        const raw = String(value || '');
        const normalized = /^#[0-9a-fA-F]{6}$/.test(raw) ? raw : '#ffffff';
        return $('<label>', { class: 'h18-canvas-quick-color' }).append(
            $('<span>', { text: label }),
            $('<input>', { type: 'color', value: normalized, 'data-canvas-color-role': role })
        );
    }

    function renderCanvasDirectControls($row, $preview, layout, colors) {
        $preview.children('.h18-canvas-direct-controls, .h18-canvas-padding-handle').remove();
        if (!$row.hasClass('is-selected')) { return; }

        const fields = canvasQuickFields();
        const hoverState = currentCanvasState === 'hover';
        const hoverCustom = hoverState && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom';
        const opacityField = hoverState ? 'HoverOpacityPercent' : 'SectionOpacityPercent';
        const opacityValue = hoverCustom ? canvasNumber($row, 'HoverOpacityPercent', 100) : Math.round(colors.opacity * 100);
        const radius = canvasNumber($row, 'RadiusPx', 7);
        const $bar = $('<div>', { class: 'h18-canvas-direct-controls', 'data-canvas-state': currentCanvasState });
        const $ranges = $('<div>', { class: 'h18-canvas-quick-ranges' }).append(
            canvasQuickRange('Indvendig', fields.pad, layout.pad, 0, 100, ' px'),
            canvasQuickRange('Vandret', fields.padX, layout.padX, 0, 100, ' px'),
            canvasQuickRange('Topafstand', fields.top, layout.top, 0, 160, ' px'),
            canvasQuickRange('Bundafstand', fields.bottom, layout.bottom, 0, 160, ' px'),
            canvasQuickRange('Radius', 'RadiusPx', radius, 0, 60, ' px'),
            canvasQuickRange('Opacity', opacityField, opacityValue, 0, 100, '%'),
            canvasQuickRange('Bredde', fields.width, layout.width, 20, 100, '%'),
            canvasQuickRange('Min. højde', fields.minHeight, Math.max(0, layout.minHeight), 0, currentCanvasDevice === 'mobile' ? 1200 : 1600, ' px')
        );
        const $colors = $('<div>', {
            class: 'h18-canvas-quick-colors',
            'data-canvas-color-state': currentCanvasState,
            'data-canvas-border': colors.border,
            'data-canvas-opacity': Math.round(colors.opacity * 100)
        }).append(
            canvasQuickColor('Baggrund', 'background', colors.background),
            canvasQuickColor('Tekst', 'text', colors.text),
            canvasQuickColor('Overskrift', 'heading', colors.heading)
        );
        $bar.append($('<strong>', { class: 'h18-canvas-direct-title', text: 'Direkte design' }), $ranges, $colors);
        if (String($row.attr('data-section-type') || '') === 'card_grid') {
            const columnField = currentCanvasDevice === 'mobile' ? 'MobileColumns' : 'Columns';
            const gapField = currentCanvasDevice === 'mobile' ? 'MobileColumnGapPx' : 'ColumnGapPx';
            $bar.append($('<div>', { class: 'h18-canvas-card-grid-controls' }).append(
                $('<strong>', { text: 'Kort-række' }),
                canvasQuickRange('Kolonner', columnField, canvasNumber($row, columnField, currentCanvasDevice === 'mobile' ? 1 : 3), 1, 6, ''),
                canvasQuickRange('Mellemrum', gapField, canvasNumber($row, gapField, currentCanvasDevice === 'mobile' ? 14 : 16), 0, 60, ' px')
            ));
        }
        $preview.append($bar);

        [
            ['top', fields.pad, 'y', 1, layout.pad],
            ['bottom', fields.pad, 'y', -1, layout.pad],
            ['left', fields.padX, 'x', 1, layout.padX],
            ['right', fields.padX, 'x', -1, layout.padX]
        ].forEach(function (item) {
            $preview.append($('<button>', {
                type: 'button', class: 'h18-canvas-padding-handle is-' + item[0],
                'data-canvas-handle-field': item[1], 'data-canvas-handle-axis': item[2],
                'data-canvas-handle-sign': item[3], 'data-canvas-handle-value': item[4],
                title: 'Træk for at ændre indvendig luft'
            }).append($('<span>', { class: 'dashicons dashicons-move' })));
        });

        $preview.append($('<div>', { class: 'h18-canvas-box-model-overlay', 'aria-hidden': 'true' }).append(
            $('<span>', { class: 'is-margin-top', text: 'M ' + Math.round(layout.top) }),
            $('<span>', { class: 'is-padding', text: 'P ' + Math.round(layout.pad) + ' / ' + Math.round(layout.padX) }),
            $('<span>', { class: 'is-margin-bottom', text: 'M ' + Math.round(layout.bottom) })
        ));
        [
            ['top', fields.top, 'y', 1, layout.top],
            ['bottom', fields.bottom, 'y', -1, layout.bottom]
        ].forEach(function (item) {
            $preview.append($('<button>', {
                type: 'button', class: 'h18-canvas-margin-handle is-' + item[0],
                'data-canvas-margin-field': item[1], 'data-canvas-margin-axis': item[2],
                'data-canvas-margin-sign': item[3], 'data-canvas-margin-value': item[4],
                title: 'Træk for at ændre ydre afstand'
            }).append($('<span>', { text: 'M' })));
        });
    }

    function ensureCanvasToolbar() {
        const $toolbar = $('.h18-page-preview-toolbar');
        if (!$toolbar.length) { return; }
        if (!$toolbar.find('.h18-preview-state').length) {
            const $hint = $toolbar.children('span').last();
            const $label = $('<strong>', { class: 'h18-preview-state-heading', text: 'State:' });
            const $normal = $('<button>', { type: 'button', class: 'button h18-preview-state is-active', 'data-state': 'normal', text: 'Normal' });
            const $hover = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'hover', text: 'Hover' });
            const $focus = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'focus', text: 'Focus' });
            const $active = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'active', text: 'Aktiv' });
            const $disabled = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'disabled', text: 'Disabled' });
            $label.insertBefore($hint); $normal.insertBefore($hint); $hover.insertBefore($hint); $focus.insertBefore($hint); $active.insertBefore($hint); $disabled.insertBefore($hint);
            $hint.text('Klik direkte i canvas for at vælge et element. Dobbeltklik på overskrifter og knaptekster for hurtig tekstredigering.');
        }
        const $heading = $('.h18-builder-canvas-heading');
        if ($heading.length && !$('#h18-canvas-runtime-status').length) {
            $heading.children('span').first().attr('title', 'Live visning af den valgte breakpoint og state').attr('id', 'h18-canvas-runtime-status');
        }
        updateCanvasToolbarStatus();
    }

    if ($pageSections.length) {
        $('.h18-visual-builder').addClass('is-ready');
        $pageSections.sortable({
            items: '> .h18-page-section-row:not(.h18-page-section-removed)',
            handle: '.h18-page-section-drag',
            axis: 'y',
            tolerance: 'pointer',
            start: function(event,ui){ if(rowLockedV0521(ui.item)){ $(this).sortable('cancel'); return false; } },
            update: syncPageSectionOrder
        });
        $pageSections.children('.h18-page-section-row').each(function () {
            refreshPageSectionType($(this));
        });
        initializePageCardSortables($pageSections);
        syncPageSectionOrder();
        const $firstEditable = $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').first();
        if ($firstEditable.length) {
            inspectPageSection($firstEditable);
        }
        renderUserPresets();
        renderLinkedComponentsV0521();
        renderPageTemplatesV0522();
        refreshAllComponentEditorsV0521();
        rebuildPageNavigator();
        ensureCanvasToolbar();
        refreshAllCanvasPreviews();
        $('.h18-builder-canvas').addClass('h18-live-canvas-ready');
    }

    function pageSectionForElement(element) {
        const $closest = $(element).closest('.h18-page-section-row');
        return $closest.length ? $closest : $inspectedSection;
    }

    $(document).on('click keydown', '.h18-canvas-preview', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-inline-edit.is-editing').length) { return; }
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        if (event.type === 'click' && (event.ctrlKey || event.metaKey || event.shiftKey)) {
            toggleMultiSelectRowV0515($row);
            return;
        }
        inspectPageSection($row);
    });


    $(document).on('click keydown', '.h18-canvas-card[data-card-key]', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-card-tools, .h18-canvas-card-drag-handle, .h18-canvas-card-inline-edit.is-editing, .h18-canvas-card-rich-edit.is-editing').length) { return; }
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        inspectPageSection($row);
        selectedCanvasCardKey = String($(this).data('card-key') || '');
        canvasFocusCardEditor($row, selectedCanvasCardKey);
        renderCanvasPreview($row);
    });

    $(document).on('click pointerdown', '.h18-canvas-card-tools, .h18-canvas-card-drag-handle', function (event) { event.stopPropagation(); });

    $(document).on('dblclick', '.h18-canvas-card-inline-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $source = $(this);
        const $row = $source.closest('.h18-page-section-row');
        const key = String($source.closest('.h18-canvas-card').data('card-key') || '');
        const original = String($source.text() || '');
        selectedCanvasCardKey = key;
        inspectPageSection($row);
        canvasFocusCardEditor($row, key);
        renderCanvasPreview($row);
        const $fresh = $row.children('.h18-canvas-preview').find('.h18-canvas-card[data-card-key="' + key + '"] .h18-canvas-card-inline-edit').first();
        $fresh.data('canvas-original-card-text', original).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });

    $(document).on('input', '.h18-canvas-card-inline-edit.is-editing', function () {
        const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
        if (!$card.length) { return; }
        const value = String($editable.text() || '').replace(/\s+/g, ' ').trim();
        canvasCardSetField($card, 'Title', value); $card.find('.h18-page-card-title-summary').text(value || 'Uden overskrift');
    });

    $(document).on('blur', '.h18-canvas-card-inline-edit.is-editing', function () { const $row = $(this).closest('.h18-page-section-row'); $(this).attr('contenteditable', 'false').removeClass('is-editing'); renderCanvasPreview($row); });

    $(document).on('keydown', '.h18-canvas-card-inline-edit.is-editing', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); $(this).trigger('blur'); }
        else if (event.key === 'Escape') {
            event.preventDefault();
            const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
            const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
            const original = String($editable.data('canvas-original-card-text') || '');
            if ($card.length) { canvasCardSetField($card, 'Title', original); $card.find('.h18-page-card-title-summary').text(original || 'Uden overskrift'); }
            renderCanvasPreview($row);
        }
    });

    $(document).on('dblclick', '.h18-canvas-card-rich-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $source = $(this);
        const $row = $source.closest('.h18-page-section-row');
        const key = String($source.closest('.h18-canvas-card').data('card-key') || '');
        const original = String($source.hasClass('is-empty') ? '' : ($source.html() || ''));
        selectedCanvasCardKey = key;
        inspectPageSection($row);
        canvasFocusCardEditor($row, key);
        renderCanvasPreview($row);
        const $fresh = $row.children('.h18-canvas-preview').find('.h18-canvas-card[data-card-key="' + key + '"] .h18-canvas-card-rich-edit').first();
        $fresh.data('canvas-original-card-html', original);
        if ($fresh.hasClass('is-empty')) { $fresh.empty().removeClass('is-empty'); }
        $fresh.attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });

    $(document).on('input', '.h18-canvas-card-rich-edit.is-editing', function () {
        const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
        if ($card.length) { canvasCardSetField($card, 'Content', String($editable.html() || '')); }
    });

    $(document).on('blur', '.h18-canvas-card-rich-edit.is-editing', function () { const $row = $(this).closest('.h18-page-section-row'); $(this).attr('contenteditable', 'false').removeClass('is-editing'); renderCanvasPreview($row); });

    $(document).on('keydown', '.h18-canvas-card-rich-edit.is-editing', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); $(this).trigger('blur'); }
        else if (event.key === 'Escape') {
            event.preventDefault();
            const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
            const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
            if ($card.length) { canvasCardSetField($card, 'Content', String($editable.data('canvas-original-card-html') || '')); }
            renderCanvasPreview($row);
        }
    });

    $(document).on('input', '.h18-canvas-card-range input[type=range]', function (event) {
        event.stopPropagation();
        const $input = $(this), $previewCard = $input.closest('.h18-canvas-card'), $row = $previewCard.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($previewCard.data('card-key') || ''));
        if (!$card.length) { return; }
        const value = parseInt($input.val(), 10) || 0;
        canvasCardSetField($card, String($input.data('card-control-field') || ''), value);
        $input.closest('.h18-canvas-card-range').find('output').text(value + ' px');
        canvasApplyCardPreviewStyle($card, $previewCard);
    });

    $(document).on('change', '.h18-canvas-card-control', function (event) {
        event.stopPropagation();
        const $control = $(this), $previewCard = $control.closest('.h18-canvas-card'), $row = $previewCard.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($previewCard.data('card-key') || ''));
        if (!$card.length) { return; }
        canvasCardSetField($card, String($control.data('card-control-field') || ''), $control.is(':checkbox') ? $control.is(':checked') : $control.val());
        renderCanvasPreview($row); canvasFocusCardEditor($row, selectedCanvasCardKey);
    });

    $(document).on('change', '.h18-canvas-card-range input[type=range]', function () { renderCanvasPreview($(this).closest('.h18-page-section-row')); });

    $(document).on('click keydown', '.h18-canvas-editable-media', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-image-tools, .h18-canvas-focal-dot').length) { return; }
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        inspectPageSection($row);
        renderCanvasPreview($row);
    });

    $(document).on('dblclick', '.h18-canvas-editable-media', function (event) {
        if ($(event.target).closest('.h18-canvas-image-tools, .h18-canvas-focal-dot').length) { return; }
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        inspectPageSection($row);
        canvasOpenSectionMedia($row);
    });

    $(document).on('click', '.h18-canvas-image-change', function (event) {
        event.preventDefault(); event.stopPropagation();
        canvasOpenSectionMedia($(this).closest('.h18-page-section-row'));
    });

    $(document).on('click', '.h18-canvas-aspect-lock', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        canvasSetField($row, 'ImageAspectLocked', !Boolean(canvasFieldValue($row, 'ImageAspectLocked', false)));
        renderCanvasPreview($row);
    });

    $(document).on('click', '.h18-canvas-image-remove', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        canvasSetField($row, 'MediaId', ''); canvasSetField($row, 'MediaUrl', '');
        pageSectionControls($row, '.h18-section-media-preview').empty();
        renderCanvasPreview($row);
    });

    $(document).on('input change', '.h18-canvas-image-control, .h18-canvas-image-range input[type=range]', function (event) {
        event.stopPropagation();
        const $control = $(this), $row = $control.closest('.h18-page-section-row');
        const field = String($control.data('image-control-field') || '');
        if (!field) { return; }
        const value = $control.is('[type=range]') ? (parseInt($control.val(), 10) || 0) : $control.val();
        canvasSetField($row, field, value);
        if ($control.is('[type=range]')) { $control.closest('.h18-canvas-image-range').find('output').text(value + (field.includes('Percent') ? '%' : ' px')); }
        const $media = $row.children('.h18-canvas-preview').find('.h18-canvas-editable-media').first();
        canvasApplySectionImageStyle($row, $media);
        if (event.type === 'change' || ['ImageAspectRatio','ImageFit'].includes(field)) { renderCanvasPreview($row); }
    });

    let canvasFocalDrag = null;
    $(document).on('pointerdown', '.h18-canvas-focal-dot', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $media = $(this).closest('.h18-canvas-editable-media');
        canvasFocalDrag = { $row: $(this).closest('.h18-page-section-row'), $media: $media, rect: $media.get(0).getBoundingClientRect() };
        $media.addClass('is-focal-dragging');
    });

    $(document).on('pointermove', function (event) {
        if (!canvasFocalDrag) { return; }
        const rect = canvasFocalDrag.rect;
        const x = Math.max(0, Math.min(100, Math.round(((event.clientX - rect.left) / Math.max(1, rect.width)) * 100)));
        const y = Math.max(0, Math.min(100, Math.round(((event.clientY - rect.top) / Math.max(1, rect.height)) * 100)));
        canvasSetField(canvasFocalDrag.$row, 'ImageFocalXPercent', x);
        canvasSetField(canvasFocalDrag.$row, 'ImageFocalYPercent', y);
        canvasFocalDrag.$media.find('img').css('objectPosition', x + '% ' + y + '%');
        canvasFocalDrag.$media.find('.h18-canvas-focal-dot').css({ left: x + '%', top: y + '%' });
        canvasFocalDrag.$media.find('[data-image-control-field="ImageFocalXPercent"]').val(x).closest('.h18-canvas-image-range').find('output').text(x + '%');
        canvasFocalDrag.$media.find('[data-image-control-field="ImageFocalYPercent"]').val(y).closest('.h18-canvas-image-range').find('output').text(y + '%');
    });

    $(document).on('pointerup pointercancel', function () {
        if (!canvasFocalDrag) { return; }
        const $row = canvasFocalDrag.$row;
        canvasFocalDrag.$media.removeClass('is-focal-dragging');
        canvasFocalDrag = null;
        renderCanvasPreview($row);
    });

    $(document).on('dblclick', '.h18-canvas-inline-edit', function (event) {
        event.preventDefault();
        event.stopPropagation();
        inspectPageSection($(this).closest('.h18-page-section-row'));
        $(this).data('canvas-original-text', String($(this).text() || ''));
        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
        const selection = window.getSelection && window.getSelection();
        if (selection && document.createRange) {
            const range = document.createRange();
            range.selectNodeContents(this); range.collapse(false); selection.removeAllRanges(); selection.addRange(range);
        }
    });

    $(document).on('input', '.h18-canvas-inline-edit.is-editing', function () {
        const $editable = $(this);
        const $row = $editable.closest('.h18-page-section-row');
        const fieldName = String($editable.data('canvas-edit-field') || '');
        if (!fieldName || !$row.length) { return; }
        const value = String($editable.text() || '').replace(/\s+/g, ' ').trim();
        pageSectionControls($row, '[name$="[' + fieldName + ']"]').first().val(value);
        if (fieldName === 'Title') {
            $row.find('.h18-page-section-title-summary').text(value);
            rebuildPageNavigator();
        }
    });

    $(document).on('blur', '.h18-canvas-inline-edit.is-editing', function () {
        const $editable = $(this);
        const $row = $editable.closest('.h18-page-section-row');
        $editable.attr('contenteditable', 'false').removeClass('is-editing');
        renderCanvasPreview($row);
    });

    $(document).on('keydown', '.h18-canvas-inline-edit.is-editing', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            $(this).trigger('blur');
        }
        if (event.key === 'Escape') {
            event.preventDefault();
            const $editable = $(this);
            const $row = $editable.closest('.h18-page-section-row');
            const fieldName = String($editable.data('canvas-edit-field') || '');
            const original = String($editable.data('canvas-original-text') || '');
            if (fieldName && $row.length) {
                canvasSetField($row, fieldName, original);
                if (fieldName === 'Title') {
                    $row.find('.h18-page-section-title-summary').text(original);
                    rebuildPageNavigator();
                }
            }
            renderCanvasPreview($row);
        }
    });

    $(document).on('dblclick', '.h18-canvas-rich-edit', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        inspectPageSection($row);
        $(this).data('canvas-original-html', String($(this).html() || ''));
        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });

    $(document).on('input', '.h18-canvas-rich-edit.is-editing', function () {
        const $row = $(this).closest('.h18-page-section-row');
        canvasSetField($row, 'Content', String($(this).html() || ''));
    });

    $(document).on('blur', '.h18-canvas-rich-edit.is-editing', function () {
        const $row = $(this).closest('.h18-page-section-row');
        $(this).attr('contenteditable', 'false').removeClass('is-editing');
        renderCanvasPreview($row);
    });

    $(document).on('keydown', '.h18-canvas-rich-edit.is-editing', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            $(this).trigger('blur');
        } else if (event.key === 'Escape') {
            event.preventDefault();
            const $row = $(this).closest('.h18-page-section-row');
            const original = String($(this).data('canvas-original-html') || '');
            canvasSetField($row, 'Content', original);
            renderCanvasPreview($row);
        }
    });

    $(document).on('click pointerdown', '.h18-canvas-direct-controls, .h18-canvas-padding-handle, .h18-canvas-margin-handle, .h18-canvas-image-tools, .h18-canvas-focal-dot', function (event) {
        event.stopPropagation();
    });

    $(document).on('input', '.h18-canvas-quick-range input[type=range]', function () {
        const $input = $(this);
        const $row = $input.closest('.h18-page-section-row');
        const fieldName = String($input.data('canvas-quick-field') || '');
        const value = parseInt($input.val(), 10) || 0;
        if (fieldName === 'HoverOpacityPercent' && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) !== 'Custom') {
            const $group = $input.closest('.h18-canvas-direct-controls').find('.h18-canvas-quick-colors');
            canvasSetField($row, 'HoverStyleMode', 'Custom');
            canvasSetField($row, 'HoverBackgroundColor', String($group.find('[data-canvas-color-role="background"]').val() || '#ffffff'));
            canvasSetField($row, 'HoverTextColor', String($group.find('[data-canvas-color-role="text"]').val() || '#30382a'));
            canvasSetField($row, 'HoverHeadingColor', String($group.find('[data-canvas-color-role="heading"]').val() || '#30382a'));
            canvasSetField($row, 'HoverBorderColor', String($group.attr('data-canvas-border') || '#c3ae83'));
            refreshHoverStyleMode($row);
        }
        canvasSetField($row, fieldName, value);
        $input.closest('.h18-canvas-quick-range').find('output').text(String(value) + String($input.data('canvas-quick-suffix') || ''));
    });

    $(document).on('change', '.h18-canvas-quick-range input[type=range]', function () {
        renderCanvasPreview($(this).closest('.h18-page-section-row'));
    });

    $(document).on('input', '.h18-canvas-quick-color input[type=color]', function () {
        const $input = $(this);
        const $row = $input.closest('.h18-page-section-row');
        const $preview = $row.children('.h18-canvas-preview');
        const role = String($input.data('canvas-color-role') || 'background');
        const value = String($input.val() || '#ffffff');
        const $group = $input.closest('.h18-canvas-quick-colors');
        const state = String($group.data('canvas-color-state') || 'normal');
        const background = String($group.find('[data-canvas-color-role="background"]').val() || '#ffffff');
        const text = String($group.find('[data-canvas-color-role="text"]').val() || '#30382a');
        const heading = String($group.find('[data-canvas-color-role="heading"]').val() || text);
        const seedBorder = String($group.attr('data-canvas-border') || '#c3ae83');
        const seedOpacity = parseInt($group.attr('data-canvas-opacity'), 10);
        if (state === 'hover') {
            const wasCustom = String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom';
            canvasSetField($row, 'HoverStyleMode', 'Custom');
            canvasSetField($row, 'HoverBackgroundColor', background);
            canvasSetField($row, 'HoverTextColor', text);
            canvasSetField($row, 'HoverHeadingColor', heading);
            if (!wasCustom) {
                canvasSetField($row, 'HoverBorderColor', seedBorder);
                canvasSetField($row, 'HoverOpacityPercent', Number.isFinite(seedOpacity) ? seedOpacity : 100);
            }
            refreshHoverStyleMode($row);
        } else {
            canvasSetField($row, 'DesignMode', 'Custom');
            canvasSetField($row, 'CustomBackgroundColor', background);
            canvasSetField($row, 'CustomTextColor', text);
            canvasSetField($row, 'CustomHeadingColor', heading);
            refreshSectionDesignMode($row);
        }
        if (role === 'background') { $preview.css('backgroundColor', value); }
        if (role === 'text') { $preview.css('color', value); }
        if (role === 'heading') { $preview.find('.h18-canvas-preview-title').css('color', value); }
    });

    $(document).on('change', '.h18-canvas-quick-color input[type=color]', function () {
        renderCanvasPreview($(this).closest('.h18-page-section-row'));
    });

    let canvasHandleDrag = null;
    $(document).on('pointerdown', '.h18-canvas-padding-handle', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $handle = $(this);
        const $row = $handle.closest('.h18-page-section-row');
        const $preview = $row.children('.h18-canvas-preview');
        canvasHandleDrag = {
            $row: $row,
            $preview: $preview,
            field: String($handle.data('canvas-handle-field') || ''),
            axis: String($handle.data('canvas-handle-axis') || 'x'),
            sign: parseFloat($handle.data('canvas-handle-sign')) || 1,
            startValue: parseFloat($handle.data('canvas-handle-value')) || 0,
            startX: event.clientX,
            startY: event.clientY
        };
        $preview.addClass('is-direct-dragging');
    });

    $(document).on('pointermove', function (event) {
        if (!canvasHandleDrag) { return; }
        const delta = canvasHandleDrag.axis === 'x' ? event.clientX - canvasHandleDrag.startX : event.clientY - canvasHandleDrag.startY;
        const value = Math.max(0, Math.min(100, Math.round(canvasHandleDrag.startValue + (delta * canvasHandleDrag.sign))));
        canvasSetField(canvasHandleDrag.$row, canvasHandleDrag.field, value);
        if (canvasHandleDrag.axis === 'x') {
            canvasHandleDrag.$preview.css({ paddingLeft: value + 'px', paddingRight: value + 'px' });
        } else {
            canvasHandleDrag.$preview.css({ paddingTop: value + 'px', paddingBottom: value + 'px' });
        }
        canvasHandleDrag.$preview.find('[data-canvas-quick-field="' + canvasHandleDrag.field + '"]').val(value).closest('.h18-canvas-quick-range').find('output').text(value + ' px');
    });

    $(document).on('pointerup pointercancel', function () {
        if (!canvasHandleDrag) { return; }
        const $row = canvasHandleDrag.$row;
        canvasHandleDrag.$preview.removeClass('is-direct-dragging');
        canvasHandleDrag = null;
        renderCanvasPreview($row);
    });

    let canvasMarginDrag = null;
    $(document).on('pointerdown', '.h18-canvas-margin-handle', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $handle = $(this), $row = $handle.closest('.h18-page-section-row');
        canvasMarginDrag = {
            $row: $row, $preview: $row.children('.h18-canvas-preview'),
            field: String($handle.data('canvas-margin-field') || ''),
            sign: parseFloat($handle.data('canvas-margin-sign')) || 1,
            startValue: parseFloat($handle.data('canvas-margin-value')) || 0,
            startY: event.clientY,
            edge: $handle.hasClass('is-top') ? 'top' : 'bottom'
        };
        canvasMarginDrag.$preview.addClass('is-margin-dragging');
    });

    $(document).on('pointermove', function (event) {
        if (!canvasMarginDrag) { return; }
        const value = Math.max(0, Math.min(160, Math.round(canvasMarginDrag.startValue + ((event.clientY - canvasMarginDrag.startY) * canvasMarginDrag.sign))));
        canvasSetField(canvasMarginDrag.$row, canvasMarginDrag.field, value);
        if (canvasMarginDrag.edge === 'top') { canvasMarginDrag.$preview.css('marginTop', value + 'px'); }
        else { canvasMarginDrag.$preview.css('marginBottom', value + 'px'); }
        canvasMarginDrag.$preview.find('[data-canvas-quick-field="' + canvasMarginDrag.field + '"]').val(value).closest('.h18-canvas-quick-range').find('output').text(value + ' px');
        canvasMarginDrag.$preview.find('.h18-canvas-box-model-overlay .' + (canvasMarginDrag.edge === 'top' ? 'is-margin-top' : 'is-margin-bottom')).text('M ' + value);
    });

    $(document).on('pointerup pointercancel', function () {
        if (!canvasMarginDrag) { return; }
        const $row = canvasMarginDrag.$row;
        canvasMarginDrag.$preview.removeClass('is-margin-dragging');
        canvasMarginDrag = null;
        renderCanvasPreview($row);
    });

    $(document).on('input change', '#h18-page-inspector-target :input', function () {
        const $row = pageSectionForElement(this);
        window.requestAnimationFrame(function () { renderCanvasPreview($row); });
    });

    $(document).on('click', '.h18-page-card-remove, .h18-page-card-restore, .h18-add-page-card', function () {
        const $row = pageSectionForElement(this);
        window.setTimeout(function () { renderCanvasPreview($row); }, 0);
    });

    $(document).on('click', '.h18-page-section-edit', function (event) {
        event.preventDefault();
        inspectPageSection($(this).closest('.h18-page-section-row'));
    });

    $(document).on('click', '.h18-page-section-header', function (event) {
        if ($(event.target).closest('button,a,input,label').length) {
            return;
        }
        inspectPageSection($(this).closest('.h18-page-section-row'));
    });

    $(document).on('change', '.h18-page-section-type', function () {
        const $row = pageSectionForElement(this);
        if (rowLockedV0521($row)) {
            const previousType = String($row.attr('data-section-type') || 'text');
            $(this).val(previousType);
            window.alert('Laget er låst. Lås det op før du ændrer elementtype.');
            return;
        }
        const type = String($(this).val() || 'text');
        if (['card_grid', 'tabs', 'accordion', 'carousel'].includes(type) && !pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length) {
            applyNewSectionDefaults($row, type);
        }
        refreshPageSectionType($row);
    });

    $(document).on('input', '.h18-section-title-input', function () {
        const $row = pageSectionForElement(this);
        $row.find('.h18-page-section-title-summary').text($(this).val());
        rebuildPageNavigator();
    });

    $(document).on('change', '.h18-layout-parent-select', function () {
        const $row = pageSectionForElement(this);
        pageSectionControls($row, '.h18-layout-parent-key').val(String($(this).val() || '')).trigger('change');
        refreshLayoutHierarchyV0519();
        rebuildPageNavigator();
        refreshLayoutHierarchyV0519();
        scheduleEditorHistoryCapture(0);
    });
    $(document).on('click', '.h18-page-section-delete', function () { window.setTimeout(refreshLayoutHierarchyV0519, 0); });

    $(document).on('change', '.h18-section-active', rebuildPageNavigator);
    $(document).on('change', '.h18-section-design-mode', function () { refreshSectionDesignMode(pageSectionForElement(this)); });
    $(document).on('change', '.h18-section-background-effect', function () { refreshSectionBackgroundEffect(pageSectionForElement(this)); });
    $(document).on('change', '.h18-hover-style-mode', function () { refreshHoverStyleMode(pageSectionForElement(this)); });

    function addPageSection(type, $before) {
        if (!pageSectionTemplate || !$pageSections.length) {
            return $();
        }
        if ($pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').length >= 25) {
            window.alert('En side kan højst have 25 aktive editorsektioner. Fjern en sektion, før du tilføjer en ny.');
            return $();
        }
        restoreInspectedSection();
        const index = pageSectionNextIndex++;
        const html = pageSectionTemplate.innerHTML.replaceAll('__INDEX__', String(index));
        const $row = $(html.trim());
        reindexPageSection($row, index);
        type = String(type || 'text');
        $row.find('.h18-page-section-type').val(type);
        applyNewSectionDefaults($row, type);
        refreshPageSectionType($row);
        if ($before && $before.length) {
            $before.before($row);
        } else {
            $pageSections.append($row);
        }
        initializePageCardSortables($row);
        syncPageSectionOrder();
        inspectPageSection($row);
        renderCanvasPreview($row);
        $('html, body').animate({ scrollTop: $row.offset().top - 60 }, 250);
        return $row;
    }

    $('#h18-add-page-section').on('click', function (event) {
        event.preventDefault();
        addPageSection(String($('#h18-new-section-type').val() || 'text'));
    });

    $(document).on('click', '.h18-builder-palette-item', function (event) {
        event.preventDefault();
        addPageSection(String($(this).data('section-type') || 'text'));
    });


    $(document).on('click', '.h18-builder-sidebar-tab', function () {
        const tab = String($(this).data('builder-tab') || 'elements');
        $('.h18-builder-sidebar-tab').removeClass('is-active');
        $(this).addClass('is-active');
        $('.h18-builder-sidebar-panel').removeClass('is-active').filter('[data-builder-panel="' + tab + '"]').addClass('is-active');
        if (tab === 'layers') {
            rebuildPageNavigator();
        } else if (tab === 'components') {
            renderUserPresets();
        }
    });

    $(document).on('click', '.h18-navigator-select', function (event) {
        const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
        const $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
        if (event.ctrlKey || event.metaKey || event.shiftKey) {
            event.preventDefault();
            toggleMultiSelectRowV0515($row);
            return;
        }
        inspectPageSection($row);
    });

    $(document).on('click', '.h18-inspector-tab', function () {
        setInspectorPanel(String($(this).data('inspector-tab') || 'content'));
    });

    $(document).on('click', '.h18-builder-component-item', function () {
        const presetId = String($(this).data('section-preset') || '');
        if (builtInSectionPresets[presetId]) {
            applySectionPreset(builtInSectionPresets[presetId]);
        }
    });

    $(document).on('click', '.h18-user-preset-insert', function () {
        const presetId = String($(this).closest('.h18-user-preset-row').attr('data-preset-id') || '');
        const preset = pageUserPresets[presetId];
        if (preset) { applyPatternV0522(preset); }
    });

    $('#h18-inspector-copy-key').on('click', function () {
        if (!$inspectedSection.length) { return; }
        const key = String($inspectedSection.find('.h18-page-section-key').val() || '');
        if (!key) { return; }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(key);
        } else {
            window.prompt('Kopiér elementnøglen:', key);
        }
    });

    $('#h18-inspector-duplicate').on('click', function () {
        if ($inspectedSection.length) {
            $inspectedSection.find('.h18-page-section-duplicate').first().trigger('click');
        }
    });

    $('#h18-inspector-copy-design').on('click', function () {
        if (!$inspectedSection.length) { return; }
        const snapshot = sectionDesignSnapshot($inspectedSection);
        if (!snapshot) { return; }
        sectionDesignClipboard = snapshot;
        try { if (window.localStorage) { window.localStorage.setItem(sectionDesignClipboardStorageKey, JSON.stringify(snapshot)); } } catch (error) {}
        refreshInspectorMeta($inspectedSection);
        const $button = $(this).text('Design kopieret ✓');
        window.setTimeout(function () { $button.text('Kopiér design'); }, 1200);
    });

    $('#h18-inspector-paste-design').on('click', function () {
        if (!$inspectedSection.length || !sectionDesignClipboard) { return; }
        const changed = applySectionDesignSnapshot($inspectedSection, sectionDesignClipboard);
        if (!changed) { window.alert('Der var ingen kompatible designfelter at indsætte på dette element.'); return; }
        const $button = $(this).text('Design indsat ✓');
        window.setTimeout(function () { $button.text('Indsæt design'); }, 1200);
    });

    $('#h18-save-section-preset').on('click', function () {
        if (!$inspectedSection.length) {
            return;
        }
        if (String($inspectedSection.attr('data-section-type') || '') === 'component') { window.alert('Linked component-instanser gemmes ikke som patterns.'); return; }
        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length || sections.some(function(section){ return ['legacy','component'].includes(String(section.Type || '')); })) {
            window.alert('Legacy og linked components kan ikke gemmes inde i et pattern.');
            return;
        }
        const data = sections[0];
        const defaultName = String($inspectedSection.find('.h18-page-section-title-summary').text() || inspectorTypeLabel(data.Type)).trim();
        const name = window.prompt('Navn på den genbrugelige komponent:', defaultName || 'Ny komponent');
        if (!name) {
            return;
        }
        const $button = $(this).prop('disabled', true).text('Gemmer…');
        $.post(Hangar18Manager.ajaxUrl || window.ajaxurl, {
            action: 'h18_save_page_preset', nonce: Hangar18Manager.pagePresetNonce, name: name, sections: JSON.stringify(sections)
        }).done(function (response) {
            if (!response || !response.success || !response.data || !response.data.preset) {
                window.alert((response && response.data && response.data.message) || 'Pattern kunne ikke gemmes.');
                return;
            }
            const preset = response.data.preset;
            pageUserPresets[String(preset.Id)] = preset;
            renderUserPresets();
            $('.h18-builder-sidebar-tab[data-builder-tab="components"]').trigger('click');
        }).fail(function (xhr) {
            const message = xhr.responseJSON && xhr.responseJSON.data && xhr.responseJSON.data.message ? xhr.responseJSON.data.message : 'Pattern kunne ikke gemmes.';
            window.alert(message);
        }).always(function () {
            $button.prop('disabled', false).text('Gem som pattern');
        });
    });

    $(document).on('click', '.h18-user-preset-delete', function () {
        const presetId = String($(this).closest('.h18-user-preset-row').attr('data-preset-id') || '');
        const preset = pageUserPresets[presetId];
        if (!preset || !window.confirm('Slet pattern “' + String(preset.Name || 'Komponent') + '”?')) {
            return;
        }
        $.post(Hangar18Manager.ajaxUrl || window.ajaxurl, {
            action: 'h18_delete_page_preset', nonce: Hangar18Manager.pagePresetNonce, preset_id: presetId
        }).done(function (response) {
            if (!response || !response.success) {
                window.alert((response && response.data && response.data.message) || 'Komponenten kunne ikke slettes.');
                return;
            }
            delete pageUserPresets[presetId];
            renderUserPresets();
        }).fail(function () {
            window.alert('Komponenten kunne ikke slettes.');
        });
    });

    let draggedPaletteType = '';
    $(document).on('dragstart', '.h18-builder-palette-item', function (event) {
        draggedPaletteType = String($(this).data('section-type') || 'text');
        const transfer = event.originalEvent && event.originalEvent.dataTransfer;
        if (transfer) {
            transfer.effectAllowed = 'copy';
            transfer.setData('text/plain', draggedPaletteType);
        }
        $('.h18-builder-canvas').addClass('is-drop-active');
    });
    $(document).on('dragend', '.h18-builder-palette-item', function () {
        draggedPaletteType = '';
        $('.h18-builder-canvas').removeClass('is-drop-active');
    });
    $('.h18-builder-canvas').on('dragover', function (event) {
        if (draggedPaletteType) {
            event.preventDefault();
        }
    }).on('drop', function (event) {
        if (!draggedPaletteType) {
            return;
        }
        event.preventDefault();
        const $before = $(event.target).closest('.h18-page-section-row');
        addPageSection(draggedPaletteType, $before);
        draggedPaletteType = '';
        $(this).removeClass('is-drop-active');
    });

    $(document).on('click', '.h18-page-section-duplicate', function (event) {
        event.preventDefault();
        const $source = $(this).closest('.h18-page-section-row');
        if (rowLockedV0521($source)) { window.alert('Laget er låst. Lås det op før du duplikerer det.'); return; }
        if ($inspectedSection.length && $inspectedSection.get(0) === $source.get(0)) {
            restoreInspectedSection();
        }
        const $copy = $source.clone(false, false);
        const index = pageSectionNextIndex++;
        reindexPageSection($copy, index);
        $copy.find('.h18-page-section-title-summary').text($copy.find('.h18-section-title-input').val() || '');
        refreshPageSectionType($copy);
        $source.after($copy);
        initializePageCardSortables($copy);
        syncPageSectionOrder();
        inspectPageSection($copy);
    });

    $(document).on('click', '.h18-page-section-delete', function (event) {
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        if (rowLockedV0521($row)) { window.alert('Laget er låst. Lås det op før du fjerner det.'); return; }
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
            restoreInspectedSection();
        }
        const removing = !$row.hasClass('h18-page-section-removed');
        $row.toggleClass('h18-page-section-removed', removing);
        $row.find('.h18-page-section-remove').val(removing ? '1' : '0');
        $(this).text(removing ? 'Fortryd fjernelse' : 'Fjern');
        syncPageSectionOrder();
    });

    $(document).on('click', '.h18-add-page-card', function (event) {
        event.preventDefault();
        const $row = pageSectionForElement(this);
        const type = String($row.attr('data-section-type') || 'card_grid');
        const current = pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length + 1;
        const title = type === 'tabs' ? 'Fane ' + current : (type === 'accordion' ? 'Punkt ' + current : (type === 'carousel' ? 'Slide ' + current : 'Ny kasse'));
        addPageCard($row, { Title: title, Background: 'OffWhite', TextTone: 'Auto', Active: true });
    });

    $(document).on('input', '.h18-page-card-title', function () {
        const title = String($(this).val() || 'Uden overskrift');
        $(this).closest('.h18-page-card-row').find('.h18-page-card-title-summary').text(title);
    });

    $(document).on('click', '.h18-page-card-duplicate', function (event) {
        event.preventDefault();
        const $source = $(this).closest('.h18-page-card-row');
        const $row = pageSectionForElement(this);
        const $container = $source.parent();
        if ($container.children('.h18-page-card-row:not(.h18-page-card-removed)').length >= 12) {
            window.alert('En kort-række kan højst indeholde 12 kasser.');
            return;
        }
        let cardIndex = 0;
        $container.children('.h18-page-card-row').each(function () {
            const current = parseInt($(this).attr('data-card-index'), 10);
            if (!Number.isNaN(current)) {
                cardIndex = Math.max(cardIndex, current + 1);
            }
        });
        const $copy = $source.clone(false, false);
        renamePageCard($copy, String($row.attr('data-section-index')), cardIndex, true);
        $source.after($copy);
        initializePageCardSortables($container);
    });

    $(document).on('click', '.h18-page-card-delete', function (event) {
        event.preventDefault();
        const $card = $(this).closest('.h18-page-card-row');
        const removing = !$card.hasClass('h18-page-card-removed');
        $card.toggleClass('h18-page-card-removed', removing);
        $card.find('.h18-page-card-remove').val(removing ? '1' : '0');
        $(this).text(removing ? 'Fortryd fjernelse' : 'Fjern');
        syncPageCardOrder($card.parent());
    });

    $(document).on('click', '.h18-split-imported-cards', function (event) {
        event.preventDefault();
        const $source = pageSectionForElement(this);
        const textarea = pageSectionControls($source, '.h18-page-section-content textarea').get(0);
        if (!textarea) {
            return;
        }
        const documentCopy = new DOMParser().parseFromString('<div id="h18-import-root">' + textarea.value + '</div>', 'text/html');
        const root = documentCopy.getElementById('h18-import-root');
        const columns = root ? root.querySelector('.wp-block-columns') : null;
        if (!columns) {
            window.alert('Der blev ikke fundet en importeret WordPress-kolonneblok i denne sektion.');
            return;
        }
        const columnNodes = Array.from(columns.children).filter(function (node) {
            return node.classList && node.classList.contains('wp-block-column');
        }).slice(0, 4);
        if (!columnNodes.length) {
            window.alert('Kolonneblokken indeholder ingen kasser, som kan udskilles.');
            return;
        }
        const extracted = columnNodes.map(function (column) {
            const contentRoot = column.querySelector('.avpf-info-card') || column;
            const copy = contentRoot.cloneNode(true);
            const heading = copy.querySelector('h1,h2,h3,h4,h5,h6');
            const title = heading ? String(heading.textContent || '').trim() : 'Kasse';
            if (heading) {
                heading.remove();
            }
            return { Title: title || 'Kasse', Content: copy.innerHTML.trim() };
        });
        columns.remove();
        textarea.value = root.innerHTML.trim();
        pageSectionControls($source, '.h18-page-section-imported-group').val('columns');
        pageSectionControls($source, '[name$="[BottomSpacingPx]"]').val(0);
        pageSectionControls($source, '[name$="[MobileBottomSpacingPx]"]').val(0);
        const $next = $source.next('.h18-page-section-row');
        const $grid = addPageSection('card_grid', $next);
        if (!$grid.length) {
            return;
        }
        const colors = ['OffWhite', 'Sand', 'Steel', 'Olive'];
        const $container = pageSectionControls($grid, '.h18-page-cards-sortable');
        $container.children('.h18-page-card-row').remove();
        extracted.forEach(function (card, index) {
            addPageCard($grid, { Title: card.Title, Content: card.Content, Background: colors[index] || 'OffWhite', TextTone: 'Auto', Active: true });
        });
        pageSectionControls($grid, '[name$="[Columns]"]').val(Math.min(extracted.length, 4));
        $grid.find('.h18-page-section-title-summary').text('Importerede kasser');
        window.alert(extracted.length + ' importerede kasser er gjort redigerbare. Skriv en ændringsbeskrivelse og gem som ny version, når resultatet er godkendt.');
    });

    $(document).on('click', '.h18-page-select-media', function (event) {
        event.preventDefault();
        canvasOpenSectionMedia(pageSectionForElement(this));
    });

    $(document).on('click', '.h18-page-remove-media', function (event) {
        event.preventDefault();
        const $row = pageSectionForElement(this);
        pageSectionControls($row, '.h18-section-media-id, .h18-section-media-url').val('');
        pageSectionControls($row, '.h18-section-media-preview').empty();
        renderCanvasPreview($row);
    });

    $(document).on('click', '.h18-page-select-bg-media', function (event) {
        event.preventDefault();
        const $row = pageSectionForElement(this);
        const frame = wp.media({
            title: Hangar18Manager.chooseImage,
            button: { text: Hangar18Manager.useImage },
            multiple: false,
            library: { type: 'image' }
        });
        frame.on('select', function () {
            const image = frame.state().get('selection').first().toJSON();
            const preview = image.sizes && image.sizes.thumbnail ? image.sizes.thumbnail.url : image.url;
            pageSectionControls($row, '.h18-section-bg-media-id').val(image.id || '');
            pageSectionControls($row, '.h18-section-bg-media-url').val(image.url || '');
            pageSectionControls($row, '.h18-section-bg-media-preview').html($('<img>', { src: preview, alt: image.alt || '' }));
            renderCanvasPreview($row);
        });
        frame.open();
    });

    $(document).on('click', '.h18-page-remove-bg-media', function (event) {
        event.preventDefault();
        const $row = pageSectionForElement(this);
        pageSectionControls($row, '.h18-section-bg-media-id, .h18-section-bg-media-url').val('');
        pageSectionControls($row, '.h18-section-bg-media-preview').empty();
        renderCanvasPreview($row);
    });

    $(document).on('click', '.h18-mini-format', function (event) {
        event.preventDefault();
        const textarea = $(this).closest('.h18-page-section-content').find('textarea').get(0);
        if (!textarea) {
            return;
        }
        const start = textarea.selectionStart || 0;
        const end = textarea.selectionEnd || start;
        const selected = textarea.value.slice(start, end);
        const format = String($(this).data('format') || '');
        let replacement = selected;
        if (format === 'bold') {
            replacement = '<strong>' + (selected || 'fed tekst') + '</strong>';
        } else if (format === 'italic') {
            replacement = '<em>' + (selected || 'kursiv tekst') + '</em>';
        } else if (format === 'link') {
            const url = window.prompt('Indtast linkadresse', 'https://');
            if (!url) {
                return;
            }
            replacement = '<a href="' + url.replace(/"/g, '&quot;') + '">' + (selected || 'linktekst') + '</a>';
        } else if (format === 'list') {
            const lines = (selected || 'Punkt 1\nPunkt 2').split(/\r?\n/).filter(Boolean);
            replacement = '<ul>\n' + lines.map(function (line) { return '<li>' + line + '</li>'; }).join('\n') + '\n</ul>';
        }
        textarea.setRangeText(replacement, start, end, 'end');
        $(textarea).trigger('input');
        textarea.focus();
    });

    $('.h18-preview-device').on('click', function () {
        const device = String($(this).data('device') || 'desktop');
        currentCanvasDevice = ['desktop', 'tablet', 'mobile'].includes(device) ? device : 'desktop';
        $('.h18-preview-device').removeClass('is-active');
        $(this).addClass('is-active');
        $pageSections.removeClass('h18-preview-desktop h18-preview-tablet h18-preview-mobile').addClass('h18-preview-' + currentCanvasDevice);
        refreshAllCanvasPreviews();
    });

    $(document).on('click', '.h18-preview-state', function () {
        const requestedState = String($(this).data('state') || 'normal');
        currentCanvasState = ['normal','hover','focus','active','disabled'].includes(requestedState) ? requestedState : 'normal';
        $('.h18-preview-state').removeClass('is-active');
        $(this).addClass('is-active');
        refreshAllCanvasPreviews();
    });


    /* ================================================================
       v0.5.15 – E1 Editor Shell completion
       UD-017 multi-select/common properties
       UD-018 zoom/guides/outline workspace
       UD-019 accessible context menu
       ================================================================ */

    function sectionKeyV0515($row) {
        return $row && $row.length ? String($row.find('.h18-page-section-key').val() || '') : '';
    }

    function multiSelectRowsV0515() {
        const rows = [];
        const validKeys = new Set();
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const $row = $(this);
            const key = sectionKeyV0515($row);
            if (key && multiSelectedSectionKeys.has(key)) {
                rows.push($row);
                validKeys.add(key);
            }
        });
        Array.from(multiSelectedSectionKeys).forEach(function (key) {
            if (!validKeys.has(key)) { multiSelectedSectionKeys.delete(key); }
        });
        return rows;
    }

    function ensureMultiEditPanelV0515() {
        if (!$pageInspector.length || $('#h18-multi-edit-panel').length) { return; }
        const $panel = $('<section>', {
            id: 'h18-multi-edit-panel',
            class: 'h18-multi-edit-panel',
            'aria-live': 'polite',
            hidden: true
        });
        $panel.append(
            $('<div>', { class: 'h18-multi-edit-heading' }).append(
                $('<div>').append(
                    $('<strong>', { text: 'Flere elementer valgt' }),
                    $('<small>', { id: 'h18-multi-edit-count', text: '0 elementer' })
                ),
                $('<button>', { type: 'button', class: 'button-link', id: 'h18-multi-clear', text: 'Ryd markering' })
            )
        );
        const $grid = $('<div>', { class: 'h18-multi-edit-grid' });
        $grid.append(
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'Background' }).append(
                $('<span>', { text: 'Baggrund' }),
                $('<select>', { id: 'h18-multi-background' }).append(
                    $('<option>', { value: '', text: 'Behold hver værdi' }),
                    $('<option>', { value: 'White', text: 'Hvid' }),
                    $('<option>', { value: 'OffWhite', text: 'Off-white' }),
                    $('<option>', { value: 'Sand', text: 'Sand' }),
                    $('<option>', { value: 'Steel', text: 'Stål' }),
                    $('<option>', { value: 'Olive', text: 'Oliven' })
                )
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'DesktopAlignment' }).append(
                $('<span>', { text: 'Desktop-placering' }),
                $('<select>', { id: 'h18-multi-alignment' }).append(
                    $('<option>', { value: '', text: 'Behold hver værdi' }),
                    $('<option>', { value: 'Left', text: 'Venstre' }),
                    $('<option>', { value: 'Center', text: 'Midt' })
                )
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'PaddingPx' }).append(
                $('<span>', { text: 'Indvendig luft' }),
                $('<input>', { id: 'h18-multi-padding', type: 'number', min: 0, max: 160, step: 1, placeholder: 'Behold' })
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'RadiusPx' }).append(
                $('<span>', { text: 'Radius' }),
                $('<input>', { id: 'h18-multi-radius', type: 'number', min: 0, max: 160, step: 1, placeholder: 'Behold' })
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'SectionOpacityPercent' }).append(
                $('<span>', { text: 'Opacity %' }),
                $('<input>', { id: 'h18-multi-opacity', type: 'number', min: 0, max: 100, step: 1, placeholder: 'Behold' })
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'Active' }).append(
                $('<span>', { text: 'Synlighed' }),
                $('<select>', { id: 'h18-multi-active' }).append(
                    $('<option>', { value: '', text: 'Behold hver værdi' }),
                    $('<option>', { value: '1', text: 'Synlig' }),
                    $('<option>', { value: '0', text: 'Skjult' })
                )
            )
        );
        $panel.append($grid);
        $panel.append(
            $('<div>', { class: 'h18-multi-edit-actions' }).append(
                $('<button>', { type: 'button', class: 'button button-primary', id: 'h18-multi-apply', text: 'Anvend på valgte' }),
                $('<span>', { class: 'description', text: 'Kun felter, som alle valgte elementer understøtter, bliver vist.' })
            )
        );
        $panel.insertBefore($pageInspectorTarget);
    }

    function multiSelectCommonFieldV0515(rows, fieldName) {
        if (!rows.length) { return false; }
        return rows.every(function ($row) {
            return pageSectionControls($row, '[name$="[' + fieldName + ']"]').length > 0;
        });
    }

    function syncMultiSelectUiV0515() {
        const rows = multiSelectRowsV0515();
        $pageSections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            $row.toggleClass('is-multi-selected', multiSelectedSectionKeys.has(sectionKeyV0515($row)));
        });
        $pageNavigatorList.children('.h18-navigator-item').each(function () {
            const index = String($(this).attr('data-section-index') || '');
            const $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
            $(this).toggleClass('is-multi-selected', multiSelectedSectionKeys.has(sectionKeyV0515($row)));
        });
        ensureMultiEditPanelV0515();
        const visible = rows.length > 1;
        const $panel = $('#h18-multi-edit-panel');
        $panel.prop('hidden', !visible);
        $('#h18-multi-edit-count').text(rows.length + ' elementer');
        if (visible) {
            $panel.find('[data-common-field]').each(function () {
                const fieldName = String($(this).attr('data-common-field') || '');
                $(this).prop('hidden', !multiSelectCommonFieldV0515(rows, fieldName));
            });
        }
    }

    function multiSelectClearV0515(updateInspector) {
        if (!multiSelectedSectionKeys.size) {
            syncMultiSelectUiV0515();
            return;
        }
        multiSelectedSectionKeys.clear();
        syncMultiSelectUiV0515();
        if (updateInspector === true && $inspectedSection.length) {
            refreshInspectorMeta($inspectedSection);
        }
    }

    function toggleMultiSelectRowV0515($row) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return; }
        const key = sectionKeyV0515($row);
        if (!key) { return; }
        if (!multiSelectedSectionKeys.size && $inspectedSection.length) {
            const inspectedKey = sectionKeyV0515($inspectedSection);
            if (inspectedKey) { multiSelectedSectionKeys.add(inspectedKey); }
        }
        if (multiSelectedSectionKeys.has(key)) { multiSelectedSectionKeys.delete(key); }
        else { multiSelectedSectionKeys.add(key); }

        const rows = multiSelectRowsV0515();
        if (rows.length < 2) {
            const remaining = rows.length ? rows[0] : null;
            multiSelectedSectionKeys.clear();
            syncMultiSelectUiV0515();
            if (remaining && remaining.length) { inspectPageSection(remaining, true); }
            return;
        }
        inspectPageSection($row, true);
        syncMultiSelectUiV0515();
    }

    function multiSelectSetFieldV0515($row, fieldName, value) {
        const $control = pageSectionControls($row, '[name$="[' + fieldName + ']"]').first();
        if (!$control.length) { return false; }
        if ($control.is(':checkbox')) {
            $control.prop('checked', String(value) === '1' || value === true).trigger('change');
        } else {
            $control.val(value).trigger('input').trigger('change');
        }
        renderCanvasPreview($row);
        return true;
    }

    function multiSelectApplyV0515() {
        const rows = multiSelectRowsV0515();
        if (rows.length < 2) { return; }
        const changes = [
            ['Background', $('#h18-multi-background').val()],
            ['DesktopAlignment', $('#h18-multi-alignment').val()],
            ['PaddingPx', $('#h18-multi-padding').val()],
            ['RadiusPx', $('#h18-multi-radius').val()],
            ['SectionOpacityPercent', $('#h18-multi-opacity').val()],
            ['Active', $('#h18-multi-active').val()]
        ].filter(function (item) { return String(item[1] ?? '') !== ''; });
        if (!changes.length) {
            window.alert('Vælg mindst én fælles værdi, der skal ændres.');
            return;
        }
        rows.forEach(function ($row) {
            changes.forEach(function (item) {
                if (multiSelectCommonFieldV0515(rows, item[0])) {
                    multiSelectSetFieldV0515($row, item[0], item[1]);
                }
            });
        });
        syncPageSectionOrder(true);
        rebuildPageNavigator();
        refreshAllCanvasPreviews();
        syncMultiSelectUiV0515();
        scheduleEditorHistoryCapture(0);
        $('#h18-multi-edit-panel input').val('');
        $('#h18-multi-edit-panel select').val('');
        const $button = $('#h18-multi-apply').text('Anvendt ✓');
        window.setTimeout(function () { $button.text('Anvend på valgte'); }, 1000);
    }

    $(document).on('click', '#h18-multi-clear', function () { multiSelectClearV0515(true); });
    $(document).on('click', '#h18-multi-apply', multiSelectApplyV0515);
    $(document).on('click', '.h18-page-section-delete', function () {
        window.setTimeout(syncMultiSelectUiV0515, 0);
    });

    function loadCanvasWorkspaceV0515() {
        try {
            const raw = window.localStorage ? window.localStorage.getItem(canvasWorkspaceStorageKeyV0515) : '';
            const saved = raw ? JSON.parse(raw) : null;
            if (saved && typeof saved === 'object') {
                canvasZoomPercentV0515 = Math.max(50, Math.min(150, parseInt(saved.zoom, 10) || 100));
                canvasOutlineModeV0515 = saved.outline === true;
                canvasGuideModeV0515 = saved.guides === true;
            }
        } catch (error) {}
    }

    function saveCanvasWorkspaceV0515() {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(canvasWorkspaceStorageKeyV0515, JSON.stringify({
                    zoom: canvasZoomPercentV0515,
                    outline: canvasOutlineModeV0515,
                    guides: canvasGuideModeV0515
                }));
            }
        } catch (error) {}
    }

    function applyCanvasWorkspaceV0515() {
        if (!$pageSections.length) { return; }
        const scale = Math.max(0.5, Math.min(1.5, canvasZoomPercentV0515 / 100));
        const supportsZoom = Boolean(window.CSS && CSS.supports && CSS.supports('zoom', '1'));
        if (supportsZoom) {
            $pageSections.css({ zoom: String(scale), transform: '', transformOrigin: '', width: '' });
        } else {
            $pageSections.css({
                zoom: '',
                transform: 'scale(' + scale + ')',
                transformOrigin: 'top center',
                width: (100 / scale) + '%'
            });
        }
        $pageSections.toggleClass('h18-canvas-outline-mode', canvasOutlineModeV0515);
        $pageSections.toggleClass('h18-canvas-guide-mode', canvasGuideModeV0515);
        $('#h18-canvas-zoom').val(canvasZoomPercentV0515);
        $('#h18-canvas-zoom-output').text(canvasZoomPercentV0515 + '%');
        $('#h18-canvas-outline-toggle').attr('aria-pressed', canvasOutlineModeV0515 ? 'true' : 'false').toggleClass('is-active', canvasOutlineModeV0515);
        $('#h18-canvas-guide-toggle').attr('aria-pressed', canvasGuideModeV0515 ? 'true' : 'false').toggleClass('is-active', canvasGuideModeV0515);
        saveCanvasWorkspaceV0515();
    }

    function ensureCanvasWorkspaceControlsV0515() {
        const $heading = $('.h18-builder-canvas-heading');
        if (!$heading.length || $('#h18-canvas-workspace-controls').length) { return; }
        const $controls = $('<div>', { id: 'h18-canvas-workspace-controls', class: 'h18-canvas-workspace-controls' });
        $controls.append(
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-zoom-out', text: '−', title: 'Zoom ud', 'aria-label': 'Zoom ud' }),
            $('<label>', { class: 'h18-canvas-zoom-label' }).append(
                $('<span>', { class: 'screen-reader-text', text: 'Canvas zoom' }),
                $('<input>', { id: 'h18-canvas-zoom', type: 'range', min: 50, max: 150, step: 5, value: canvasZoomPercentV0515 }),
                $('<output>', { id: 'h18-canvas-zoom-output', for: 'h18-canvas-zoom', text: canvasZoomPercentV0515 + '%' })
            ),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-zoom-in', text: '+', title: 'Zoom ind', 'aria-label': 'Zoom ind' }),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-zoom-reset', text: '100%', title: 'Nulstil zoom' }),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-outline-toggle', text: 'Outline', 'aria-pressed': 'false' }),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-guide-toggle', text: 'Guides', 'aria-pressed': 'false' })
        );
        $heading.append($controls);
        applyCanvasWorkspaceV0515();
    }

    $(document).on('input change', '#h18-canvas-zoom', function () {
        canvasZoomPercentV0515 = Math.max(50, Math.min(150, parseInt($(this).val(), 10) || 100));
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-zoom-out', function () {
        canvasZoomPercentV0515 = Math.max(50, canvasZoomPercentV0515 - 5);
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-zoom-in', function () {
        canvasZoomPercentV0515 = Math.min(150, canvasZoomPercentV0515 + 5);
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-zoom-reset', function () {
        canvasZoomPercentV0515 = 100;
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-outline-toggle', function () {
        canvasOutlineModeV0515 = !canvasOutlineModeV0515;
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-guide-toggle', function () {
        canvasGuideModeV0515 = !canvasGuideModeV0515;
        applyCanvasWorkspaceV0515();
    });

    function contextMenuEnsureV0515() {
        if ($('#h18-editor-context-menu').length) { return; }
        const $menu = $('<div>', {
            id: 'h18-editor-context-menu',
            class: 'h18-editor-context-menu',
            role: 'menu',
            'aria-label': 'Elementhandlinger',
            hidden: true
        });
        $('body').append($menu);
    }

    function contextMenuItemsV0515($row) {
        const type = String($row.attr('data-section-type') || 'text');
        const active = pageSectionControls($row, '.h18-section-active').is(':checked');
        const key = sectionKeyV0515($row);
        const lockedV0521 = rowLockedV0521($row);
        return [
            { action: 'edit', label: 'Redigér element', hint: 'Enter' },
            { action: 'multi', label: multiSelectedSectionKeys.has(key) ? 'Fjern fra multivalg' : 'Tilføj til multivalg', hint: 'Ctrl/⌘/Shift+klik' },
            { separator: true },
            { action: 'duplicate', label: 'Duplikér element', disabled: type === 'legacy' || lockedV0521 },
            { action: 'copy-design', label: 'Kopiér design', disabled: type === 'legacy' },
            { action: 'paste-design', label: 'Indsæt design', disabled: type === 'legacy' || !sectionDesignClipboard },
            { action: 'component', label: 'Gem som pattern', disabled: type === 'legacy' || type === 'component' || lockedV0521 },
            { separator: true },
            { action: 'toggle-active', label: active ? 'Skjul element' : 'Vis element', disabled: lockedV0521 },
            { action: 'move-up', label: 'Flyt op', disabled: lockedV0521 },
            { action: 'move-down', label: 'Flyt ned', disabled: lockedV0521 },
            { separator: true },
            { action: 'delete', label: 'Fjern element', danger: true, disabled: type === 'legacy' || lockedV0521 }
        ];
    }

    function contextMenuCloseV0515(returnFocus) {
        const $menu = $('#h18-editor-context-menu');
        if (!$menu.length || $menu.prop('hidden')) { return; }
        $menu.prop('hidden', true).empty();
        contextMenuRowV0515 = $();
        if (returnFocus !== false && contextMenuReturnFocusV0515 && document.contains(contextMenuReturnFocusV0515)) {
            $(contextMenuReturnFocusV0515).trigger('focus');
        }
        contextMenuReturnFocusV0515 = null;
    }

    function contextMenuOpenV0515($row, x, y, focusSource) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return; }
        contextMenuEnsureV0515();
        const key = sectionKeyV0515($row);
        inspectPageSection($row, key && multiSelectedSectionKeys.has(key));
        contextMenuRowV0515 = $row;
        contextMenuReturnFocusV0515 = focusSource || document.activeElement;
        const $menu = $('#h18-editor-context-menu').empty();
        contextMenuItemsV0515($row).forEach(function (item) {
            if (item.separator) {
                $menu.append($('<div>', { class: 'h18-context-separator', role: 'separator' }));
                return;
            }
            const $button = $('<button>', {
                type: 'button',
                role: 'menuitem',
                class: 'h18-context-item' + (item.danger ? ' is-danger' : ''),
                'data-context-action': item.action,
                disabled: item.disabled === true
            });
            $button.append($('<span>', { text: item.label }));
            if (item.hint) { $button.append($('<small>', { text: item.hint })); }
            $menu.append($button);
        });
        $menu.prop('hidden', false).css({ left: 0, top: 0 });
        const node = $menu.get(0);
        const width = node ? node.offsetWidth : 240;
        const height = node ? node.offsetHeight : 300;
        const left = Math.max(8, Math.min(Number(x) || 8, window.innerWidth - width - 8));
        const top = Math.max(8, Math.min(Number(y) || 8, window.innerHeight - height - 8));
        $menu.css({ left: left + 'px', top: top + 'px' });
        $menu.find('.h18-context-item:not(:disabled)').first().trigger('focus');
    }

    function contextMenuMoveRowV0515($row, direction) {
        if (!$row || !$row.length) { return; }
        restoreInspectedSection();
        const $target = direction < 0
            ? $row.prevAll('.h18-page-section-row:not(.h18-page-section-removed)').first()
            : $row.nextAll('.h18-page-section-row:not(.h18-page-section-removed)').first();
        if (!$target.length) { inspectPageSection($row, true); return; }
        if (direction < 0) { $row.insertBefore($target); }
        else { $row.insertAfter($target); }
        syncPageSectionOrder(true);
        rebuildPageNavigator();
        inspectPageSection($row, multiSelectedSectionKeys.has(sectionKeyV0515($row)));
        scheduleEditorHistoryCapture(0);
    }

    function contextMenuExecuteV0515(action) {
        const $row = contextMenuRowV0515;
        if (!$row || !$row.length) { contextMenuCloseV0515(); return; }
        contextMenuCloseV0515(false);
        if (action === 'edit') { inspectPageSection($row, multiSelectedSectionKeys.has(sectionKeyV0515($row))); }
        else if (action === 'multi') { toggleMultiSelectRowV0515($row); }
        else if (action === 'duplicate') { inspectPageSection($row); $row.find('.h18-page-section-duplicate').first().trigger('click'); }
        else if (action === 'copy-design') { inspectPageSection($row); $('#h18-inspector-copy-design').trigger('click'); }
        else if (action === 'paste-design') { inspectPageSection($row); $('#h18-inspector-paste-design').trigger('click'); }
        else if (action === 'component') { inspectPageSection($row); $('#h18-save-section-preset').trigger('click'); }
        else if (action === 'toggle-active') {
            const $active = pageSectionControls($row, '.h18-section-active').first();
            if ($active.length) { $active.prop('checked', !$active.is(':checked')).trigger('change'); renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0); }
        }
        else if (action === 'move-up') { contextMenuMoveRowV0515($row, -1); }
        else if (action === 'move-down') { contextMenuMoveRowV0515($row, 1); }
        else if (action === 'delete') { inspectPageSection($row); $row.find('.h18-page-section-delete').first().trigger('click'); }
    }

    $(document).on('contextmenu', '.h18-canvas-preview, .h18-navigator-item', function (event) {
        if ($(event.target).closest('input,textarea,select,[contenteditable="true"]').length) { return; }
        event.preventDefault();
        let $row = $(this).closest('.h18-page-section-row');
        if (!$row.length) {
            const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
            $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
        }
        contextMenuOpenV0515($row, event.clientX, event.clientY, this);
    });

    $(document).on('keydown', '.h18-canvas-preview, .h18-navigator-select', function (event) {
        if (!(event.shiftKey && event.key === 'F10')) { return; }
        event.preventDefault();
        let $row = $(this).closest('.h18-page-section-row');
        if (!$row.length) {
            const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
            $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
        }
        const rect = this.getBoundingClientRect();
        contextMenuOpenV0515($row, rect.left + Math.min(rect.width / 2, 180), rect.top + Math.min(rect.height / 2, 120), this);
    });

    $(document).on('click', '.h18-context-item:not(:disabled)', function () {
        contextMenuExecuteV0515(String($(this).attr('data-context-action') || ''));
    });

    $(document).on('keydown', '#h18-editor-context-menu', function (event) {
        const $items = $(this).find('.h18-context-item:not(:disabled)');
        if (!$items.length) { return; }
        const index = Math.max(0, $items.index(document.activeElement));
        if (event.key === 'Escape') { event.preventDefault(); contextMenuCloseV0515(); }
        else if (event.key === 'ArrowDown') { event.preventDefault(); $items.eq((index + 1) % $items.length).trigger('focus'); }
        else if (event.key === 'ArrowUp') { event.preventDefault(); $items.eq((index - 1 + $items.length) % $items.length).trigger('focus'); }
        else if (event.key === 'Home') { event.preventDefault(); $items.first().trigger('focus'); }
        else if (event.key === 'End') { event.preventDefault(); $items.last().trigger('focus'); }
        else if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); $(document.activeElement).trigger('click'); }
        else if (event.key === 'Tab') { event.preventDefault(); $items.eq((index + (event.shiftKey ? -1 : 1) + $items.length) % $items.length).trigger('focus'); }
    });

    $(document).on('mousedown', function (event) {
        if (!$(event.target).closest('#h18-editor-context-menu').length) { contextMenuCloseV0515(false); }
    });
    $(window).on('blur scroll resize', function () { contextMenuCloseV0515(false); });

    loadCanvasWorkspaceV0515();
    if ($pageSections.length) {
        window.setTimeout(function () {
            ensureCanvasWorkspaceControlsV0515();
            syncMultiSelectUiV0515();
        }, 0);
    }


    const editorHistoryLimit = 50;
    const editorHistoryEntries = [];
    let editorHistoryIndex = -1;
    let editorHistoryTimer = null;
    let editorHistoryReady = false;
    let editorHistoryApplying = false;
    let editorHistorySubmitting = false;
    let editorHistorySavedSignature = '';
    const editorDraftVersion = '1.0';
    const editorDraftStoragePrefix = 'hangar18PageDraftV0513:';
    const editorDraftMaxChars = 4000000;
    const editorDraftSubmitSuccessWindowMs = 10 * 60 * 1000;
    let editorDraftTimer = null;
    let editorDraftCandidate = null;
    let editorDraftServerSignature = '';
    let editorDraftRecoveryPending = false;

    function editorDraftPageSlug() {
        const raw = String($('#h18-page-editor-form [name="page_slug"]').val() || '').trim().toLowerCase();
        return raw.replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '') || 'unknown';
    }

    function editorDraftStorageKey() {
        return editorDraftStoragePrefix + editorDraftPageSlug();
    }

    function editorDraftSetStatus(text, state) {
        const $status = $('#h18-editor-autosave-status');
        if (!$status.length) { return; }
        $status.removeClass('is-saved is-warning is-error');
        if (state) { $status.addClass('is-' + state); }
        $status.text(String(text || 'Lokal kladde: klar'));
    }

    function editorDraftFormatTime(iso) {
        if (!iso) { return ''; }
        const value = new Date(iso);
        if (Number.isNaN(value.getTime())) { return ''; }
        return value.toLocaleTimeString('da-DK', { hour: '2-digit', minute: '2-digit' });
    }

    function editorDraftHideRecovery() {
        $('#h18-editor-recovery-actions').prop('hidden', true);
    }

    function editorDraftShowRecovery() {
        $('#h18-editor-recovery-actions').prop('hidden', false);
    }

    function editorDraftRead() {
        try {
            if (!window.localStorage) { return null; }
            const raw = window.localStorage.getItem(editorDraftStorageKey());
            if (!raw) { return null; }
            const value = JSON.parse(raw);
            if (!value || value.Version !== editorDraftVersion || value.PageSlug !== editorDraftPageSlug()) { return null; }
            if (!value.Snapshot || typeof value.Snapshot !== 'object' || !value.Snapshot.html || !value.Snapshot.signature) { return null; }
            return value;
        } catch (error) {
            editorDraftSetStatus('Lokal kladde kunne ikke læses', 'error');
            return null;
        }
    }

    function editorDraftRemove(updateStatus) {
        try {
            if (window.localStorage) { window.localStorage.removeItem(editorDraftStorageKey()); }
            if (updateStatus !== false) { editorDraftSetStatus('Lokal kladde: ingen ændringer', ''); }
            return true;
        } catch (error) {
            editorDraftSetStatus('Lokal kladde kunne ikke slettes', 'error');
            return false;
        }
    }

    function editorDraftSaveNow(markSubmitted) {
        window.clearTimeout(editorDraftTimer);
        editorDraftTimer = null;
        if (!editorHistoryReady || editorHistoryApplying) { return false; }
        if (editorDraftRecoveryPending && !markSubmitted) { return false; }
        const snapshot = editorHistorySnapshot();
        if (!snapshot) { return false; }
        if (snapshot.signature === editorDraftServerSignature) {
            editorDraftRemove(false);
            editorDraftSetStatus('Lokal kladde: ingen ændringer', '');
            return true;
        }
        const now = new Date().toISOString();
        const payload = {
            Version: editorDraftVersion,
            PluginVersion: '0.5.13',
            PageSlug: editorDraftPageSlug(),
            BaseSignature: editorDraftServerSignature,
            SavedAtUtc: now,
            SubmittedAtUtc: markSubmitted ? now : '',
            Snapshot: snapshot
        };
        let raw = '';
        try {
            raw = JSON.stringify(payload);
            if (raw.length > editorDraftMaxChars) {
                editorDraftSetStatus('Lokal kladde er for stor til browserlager', 'error');
                return false;
            }
            if (!window.localStorage) { throw new Error('localStorage unavailable'); }
            window.localStorage.setItem(editorDraftStorageKey(), raw);
            editorDraftSetStatus('Lokal kladde gemt ' + editorDraftFormatTime(now), 'saved');
            return true;
        } catch (error) {
            editorDraftSetStatus('Lokal kladde kunne ikke gemmes', 'error');
            return false;
        }
    }

    function editorDraftScheduleSave(delay) {
        if (!editorHistoryReady || editorHistoryApplying || editorDraftRecoveryPending) { return; }
        window.clearTimeout(editorDraftTimer);
        editorDraftTimer = window.setTimeout(function () { editorDraftSaveNow(false); }, Math.max(150, Number(delay) || 1200));
    }

    function editorDraftInitializeRecovery(initial) {
        if (!initial) { return; }
        editorDraftServerSignature = initial.signature;
        editorDraftHideRecovery();
        const draft = editorDraftRead();
        if (!draft) {
            editorDraftSetStatus('Lokal kladde: klar', '');
            return;
        }
        if (draft.Snapshot.signature === initial.signature) {
            editorDraftRemove(false);
            editorDraftSetStatus('Lokal kladde er allerede gemt', 'saved');
            return;
        }
        const submittedAt = draft.SubmittedAtUtc ? new Date(draft.SubmittedAtUtc).getTime() : 0;
        const recentlySubmitted = submittedAt > 0 && (Date.now() - submittedAt) >= 0 && (Date.now() - submittedAt) <= editorDraftSubmitSuccessWindowMs;
        if (recentlySubmitted && draft.BaseSignature && draft.BaseSignature !== initial.signature) {
            editorDraftRemove(false);
            editorDraftSetStatus('Sidste lokale kladde er gemt i WordPress', 'saved');
            return;
        }
        editorDraftCandidate = draft;
        editorDraftRecoveryPending = true;
        editorDraftShowRecovery();
        const time = editorDraftFormatTime(draft.SavedAtUtc);
        const stale = Boolean(draft.BaseSignature && draft.BaseSignature !== initial.signature);
        editorDraftSetStatus(
            'Kladde fundet' + (time ? ' ' + time : '') + (stale ? ' · ældre sideversion' : ' · kan gendannes'),
            'warning'
        );
    }

    function editorDraftRestoreCandidate() {
        if (!editorDraftCandidate || !editorDraftCandidate.Snapshot || !editorHistoryReady) { return; }
        const draft = editorDraftCandidate;
        const serverEntry = editorHistoryEntries.find(function (entry) { return entry.signature === editorDraftServerSignature; }) || editorHistoryEntries[0];
        editorDraftRecoveryPending = false;
        editorDraftCandidate = null;
        editorDraftHideRecovery();
        editorHistoryEntries.splice(0, editorHistoryEntries.length);
        if (serverEntry) { editorHistoryEntries.push(serverEntry); }
        if (!serverEntry || draft.Snapshot.signature !== serverEntry.signature) { editorHistoryEntries.push(draft.Snapshot); }
        editorHistoryIndex = editorHistoryEntries.length - 1;
        editorHistoryRestore(draft.Snapshot);
        editorDraftSaveNow(false);
        editorHistoryUpdateUi();
    }

    function editorDraftDiscardCandidate() {
        editorDraftRecoveryPending = false;
        editorDraftCandidate = null;
        editorDraftHideRecovery();
        editorDraftRemove(false);
        editorDraftSetStatus('Lokal kladde kasseret', '');
        editorDraftScheduleSave(250);
    }

    function editorHistoryNormalizeClone($root) {
        $root.find('.h18-canvas-preview, .ui-sortable-placeholder, .ui-sortable-helper').remove();
        $root.find('.is-selected, .is-card-selected, .is-direct-dragging, .is-focal-dragging').removeClass('is-selected is-card-selected is-direct-dragging is-focal-dragging');
        $root.find('.ui-sortable').removeClass('ui-sortable');
        $root.find('input').each(function () {
            const $input = $(this);
            if ($input.is(':checkbox, :radio')) {
                if ($input.prop('checked')) { $input.attr('checked', 'checked'); }
                else { $input.removeAttr('checked'); }
            } else {
                $input.attr('value', String($input.val() == null ? '' : $input.val()));
            }
        });
        $root.find('textarea').each(function () { $(this).text(String($(this).val() == null ? '' : $(this).val())); });
        $root.find('select').each(function () {
            const $select = $(this);
            const values = Array.isArray($select.val()) ? $select.val().map(String) : [String($select.val() == null ? '' : $select.val())];
            $select.find('option').each(function () {
                if (values.includes(String($(this).val()))) { $(this).attr('selected', 'selected'); }
                else { $(this).removeAttr('selected'); }
            });
        });
    }

    function editorHistorySnapshot() {
        if (!$pageSections.length) { return null; }
        const selectedKey = $inspectedSection.length ? String($inspectedSection.find('.h18-page-section-key').val() || '') : '';
        const inspectedIndex = $inspectedSection.length ? String($inspectedSection.attr('data-section-index') || '') : '';
        const $clone = $pageSections.clone(false, false);
        if (inspectedIndex) {
            const $body = $pageInspectorTarget.children('.h18-page-section-body').first();
            if ($body.length) {
                const $cloneRow = $clone.children('.h18-page-section-row[data-section-index="' + inspectedIndex + '"]').first();
                if ($cloneRow.length) {
                    $cloneRow.children('.h18-page-section-body').remove();
                    $cloneRow.children('.h18-page-section-header').after($body.clone(false, false));
                }
            }
        }
        editorHistoryNormalizeClone($clone);
        const html = String($clone.html() || '');
        return {
            html: html,
            signature: html,
            selectedKey: selectedKey,
            selectedCardKey: String(selectedCanvasCardKey || ''),
            device: String(currentCanvasDevice || 'desktop'),
            state: String(currentCanvasState || 'normal')
        };
    }

    function editorHistoryUpdateUi() {
        const canUndo = editorHistoryIndex > 0;
        const canRedo = editorHistoryIndex >= 0 && editorHistoryIndex < editorHistoryEntries.length - 1;
        $('#h18-editor-undo').prop('disabled', !canUndo);
        $('#h18-editor-redo').prop('disabled', !canRedo);
        const current = editorHistoryIndex >= 0 ? editorHistoryEntries[editorHistoryIndex] : null;
        const dirty = Boolean(current && current.signature !== editorHistorySavedSignature);
        $('#h18-editor-history-status')
            .toggleClass('is-dirty', dirty)
            .text(dirty ? 'Ugemte ændringer · trin ' + editorHistoryIndex : 'Ingen ugemte ændringer');
    }

    function editorHistoryRecordNow() {
        if (!editorHistoryReady || editorHistoryApplying) { return; }
        const snapshot = editorHistorySnapshot();
        if (!snapshot) { return; }
        const current = editorHistoryIndex >= 0 ? editorHistoryEntries[editorHistoryIndex] : null;
        if (current && current.signature === snapshot.signature) { editorHistoryUpdateUi(); return; }
        if (editorHistoryIndex < editorHistoryEntries.length - 1) { editorHistoryEntries.splice(editorHistoryIndex + 1); }
        editorHistoryEntries.push(snapshot);
        if (editorHistoryEntries.length > editorHistoryLimit) {
            editorHistoryEntries.shift();
            if (editorHistorySavedSignature && !editorHistoryEntries.some(entry => entry.signature === editorHistorySavedSignature)) {
                editorHistorySavedSignature = '__saved_state_outside_history__';
            }
        }
        editorHistoryIndex = editorHistoryEntries.length - 1;
        editorHistoryUpdateUi();
        editorDraftScheduleSave();
    }

    function scheduleEditorHistoryCapture(delay) {
        if (!editorHistoryReady || editorHistoryApplying) { return; }
        window.clearTimeout(editorHistoryTimer);
        editorHistoryTimer = window.setTimeout(editorHistoryRecordNow, typeof delay === 'number' ? delay : 280);
    }

    function editorHistoryFindRowByKey(key) {
        let $match = $();
        if (!key) { return $match; }
        $pageSections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            if (String($row.find('.h18-page-section-key').val() || '') === String(key)) { $match = $row; return false; }
        });
        return $match;
    }

    function editorHistoryRestore(entry) {
        if (!entry || !entry.html || !$pageSections.length) { return; }
        editorHistoryApplying = true;
        window.clearTimeout(editorHistoryTimer);
        try {
            restoreInspectedSection();
            selectedCanvasCardKey = String(entry.selectedCardKey || '');
            $pageSections.html(entry.html);
            $pageSections.children('.h18-page-section-row').each(function () {
                const $row = $(this);
                refreshPageSectionType($row);
                initializePageCardSortables($row);
            });
            syncPageSectionOrder(true);
            rebuildPageNavigator();
            currentCanvasDevice = ['desktop','tablet','mobile'].includes(String(entry.device)) ? String(entry.device) : 'desktop';
            currentCanvasState = ['normal','hover','focus','active','disabled'].includes(String(entry.state)) ? String(entry.state) : 'normal';
            $('.h18-preview-device').removeClass('is-active').filter('[data-device="' + currentCanvasDevice + '"]').addClass('is-active');
            $('.h18-preview-state').removeClass('is-active').filter('[data-state="' + currentCanvasState + '"]').addClass('is-active');
            $pageSections.removeClass('h18-preview-desktop h18-preview-tablet h18-preview-mobile').addClass('h18-preview-' + currentCanvasDevice);
            const $target = editorHistoryFindRowByKey(entry.selectedKey);
            if ($target.length && !$target.hasClass('h18-page-section-removed')) { inspectPageSection($target); }
            refreshAllCanvasPreviews();
        } finally {
            editorHistoryApplying = false;
            editorHistoryUpdateUi();
            if (editorHistoryReady) { editorDraftScheduleSave(250); }
        }
    }

    function editorHistoryFlushPending() {
        if (!editorHistoryTimer) { return; }
        window.clearTimeout(editorHistoryTimer);
        editorHistoryTimer = null;
        editorHistoryRecordNow();
    }

    function editorHistoryUndo() {
        editorHistoryFlushPending();
        if (editorHistoryIndex <= 0) { return; }
        editorHistoryIndex -= 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }

    function editorHistoryRedo() {
        editorHistoryFlushPending();
        if (editorHistoryIndex < 0 || editorHistoryIndex >= editorHistoryEntries.length - 1) { return; }
        editorHistoryIndex += 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }

    function initializeEditorHistory() {
        if (!$pageSections.length || editorHistoryReady) { return; }
        const initial = editorHistorySnapshot();
        if (!initial) { return; }
        editorHistoryEntries.push(initial);
        editorHistoryIndex = 0;
        editorHistorySavedSignature = initial.signature;
        editorDraftServerSignature = initial.signature;
        editorHistoryReady = true;
        editorHistoryUpdateUi();
        editorDraftInitializeRecovery(initial);

        const originalCanvasSetField = canvasSetField;
        canvasSetField = function ($row, fieldName, value) {
            const result = originalCanvasSetField($row, fieldName, value);
            if (result) { scheduleEditorHistoryCapture(); }
            return result;
        };
        const originalCanvasCardSetField = canvasCardSetField;
        canvasCardSetField = function ($card, fieldName, value) {
            const result = originalCanvasCardSetField($card, fieldName, value);
            if (result) { scheduleEditorHistoryCapture(); }
            return result;
        };

        $('#h18-page-editor-form').on('input change', '.h18-page-section-body :input, .h18-page-card-row :input', function () {
            scheduleEditorHistoryCapture();
        });

        if (window.MutationObserver && $pageEditorForm.get(0)) {
            const observer = new MutationObserver(function (mutations) {
                if (editorHistoryApplying) { return; }
                let meaningful = false;
                mutations.forEach(function (mutation) {
                    if (meaningful) { return; }
                    if (mutation.type === 'childList') {
                        const nodes = Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || []));
                        meaningful = nodes.some(function (node) {
                            return node && node.nodeType === 1 && ($(node).is('.h18-page-section-row, .h18-page-card-row') || $(node).find('.h18-page-section-row, .h18-page-card-row').length);
                        });
                    } else if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        const $target = $(mutation.target);
                        if ($target.is('.h18-page-section-row, .h18-page-card-row')) {
                            const before = String(mutation.oldValue || '').includes('h18-page-section-removed') || String(mutation.oldValue || '').includes('h18-page-card-removed');
                            const after = $target.hasClass('h18-page-section-removed') || $target.hasClass('h18-page-card-removed');
                            meaningful = before !== after;
                        }
                    }
                });
                if (meaningful) { scheduleEditorHistoryCapture(120); }
            });
            observer.observe($pageEditorForm.get(0), { childList: true, subtree: true, attributes: true, attributeOldValue: true, attributeFilter: ['class'] });
        }
    }

    $(document).on('click', '#h18-editor-undo', function (event) { event.preventDefault(); editorHistoryUndo(); });
    $(document).on('click', '#h18-editor-redo', function (event) { event.preventDefault(); editorHistoryRedo(); });
    $(document).on('keydown.h18EditorHistory', function (event) {
        if (!(event.ctrlKey || event.metaKey) || String(event.key || '').toLowerCase() !== 'z') { return; }
        const $target = $(event.target);
        if ($target.is('input, textarea, select') || $target.closest('[contenteditable="true"]').length) { return; }
        event.preventDefault();
        if (event.shiftKey) { editorHistoryRedo(); } else { editorHistoryUndo(); }
    });

    const $pageEditorForm = $('#h18-page-editor-form');
    const $pageChangeNote = $pageEditorForm.find('[name="page_change_note"]');
    const $pageWhatIf = $pageEditorForm.find('[name="whatif"]');

    function syncPageChangeNoteRequirement() {
        if (!$pageChangeNote.length) {
            return;
        }
        const required = !$pageWhatIf.is(':checked');
        $pageChangeNote.prop('required', required).attr('aria-required', required ? 'true' : 'false');
    }

    if ($pageEditorForm.length) {
        $pageWhatIf.on('change', syncPageChangeNoteRequirement);
        syncPageChangeNoteRequirement();
        $pageEditorForm.on('submit', function () {
            editorHistoryFlushPending();
            window.clearTimeout(editorDraftTimer);
            editorDraftTimer = null;
            editorDraftSaveNow(!$pageWhatIf.is(':checked'));
            editorHistorySubmitting = true;
        });
        window.setTimeout(initializeEditorHistory, 0);
        window.setTimeout(refreshLayoutHierarchyV0519, 0);
    }

    $(window).on('beforeunload.h18EditorHistory', function (event) {
        if (!editorHistoryReady || editorHistorySubmitting || editorHistoryIndex < 0) { return; }
        editorHistoryFlushPending();
        editorDraftSaveNow(false);
        const live = editorHistorySnapshot();
        if (!live || live.signature === editorHistorySavedSignature) { return; }
        event.preventDefault();
        event.returnValue = '';
        return '';
    });



    const commandPaletteSectionTypes = [
        ['text', 'Tekst'], ['hero', 'Topbanner / hero'], ['text_image', 'Tekst og billede'], ['image', 'Stort billede'],
        ['buttons', 'Handlingsknapper'], ['card', 'Indholdskort'], ['card_grid', 'Kort-række / kolonner'], ['container', 'Container'], ['flex', 'Flex container'], ['grid', 'Grid container'], ['highlight', 'Fremhævet tekst'],
        ['spacer', 'Afstand'], ['html', 'Importeret blok / HTML'], ['css', 'Side-CSS'], ['mail_form', 'Mailformular'], ['poll', 'Afstemning']
    ];
    let commandPaletteActiveIndex = 0;
    let commandPaletteVisibleCommands = [];
    let commandPalettePreviousFocus = null;

    function commandPaletteIsOpen() {
        return !$('#h18-command-palette').prop('hidden');
    }

    function commandPaletteIsEditableTarget(target) {
        const $target = $(target);
        return $target.is('input, textarea, select') || $target.closest('[contenteditable="true"]').length > 0;
    }

    function commandPaletteNormalize(value) {
        return String(value || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim();
    }

    function commandPaletteSectionLabel($row) {
        const type = String($row.attr('data-section-type') || 'text');
        const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim() || 'Uden overskrift';
        const key = String($row.find('.h18-page-section-key').val() || '').trim();
        return { type: type, title: title, key: key, typeLabel: inspectorTypeLabel(type) };
    }

    function commandPaletteScrollToRow($row) {
        if (!$row || !$row.length) { return; }
        inspectPageSection($row);
        const node = $row.get(0);
        if (node && typeof node.scrollIntoView === 'function') {
            node.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function commandPaletteBuildCommands() {
        const commands = [];
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function (index) {
            const $row = $(this);
            const meta = commandPaletteSectionLabel($row);
            commands.push({
                id: 'section-' + String($row.attr('data-section-index') || index),
                group: 'Gå til element',
                label: meta.title,
                detail: meta.typeLabel + (meta.key ? ' · ' + meta.key : ''),
                keywords: 'gå til element sektion lag navigator ' + meta.type + ' ' + meta.typeLabel + ' ' + meta.title + ' ' + meta.key,
                run: function () { commandPaletteScrollToRow($row); }
            });
        });

        commandPaletteSectionTypes.forEach(function (entry) {
            commands.push({
                id: 'add-' + entry[0], group: 'Tilføj element', label: 'Tilføj ' + entry[1], detail: entry[0],
                keywords: 'tilføj nyt element sektion ' + entry[0] + ' ' + entry[1],
                run: function () {
                    const $row = addPageSection(entry[0]);
                    if ($row.length) { commandPaletteScrollToRow($row); }
                }
            });
        });

        [['desktop','Desktop'],['tablet','Tablet'],['mobile','Mobil']].forEach(function (entry) {
            commands.push({
                id: 'device-' + entry[0], group: 'Visning', label: 'Vis ' + entry[1], detail: 'Responsive preview',
                keywords: 'visning preview responsive device ' + entry[0] + ' ' + entry[1],
                run: function () { $('.h18-preview-device[data-device="' + entry[0] + '"]').first().trigger('click'); }
            });
        });
        [['normal','Normal'],['hover','Hover'],['focus','Focus'],['active','Aktiv'],['disabled','Disabled']].forEach(function (entry) {
            commands.push({
                id: 'state-' + entry[0], group: 'Visning', label: 'State: ' + entry[1], detail: 'Design-state',
                keywords: 'state normal hover design ' + entry[0] + ' ' + entry[1],
                run: function () { ensureCanvasToolbar(); $('.h18-preview-state[data-state="' + entry[0] + '"]').first().trigger('click'); }
            });
        });

        commands.push(
            { id: 'undo', group: 'Redigering', label: 'Fortryd', detail: 'Ctrl/Cmd+Z', keywords: 'fortryd undo tilbage', disabled: function () { return editorHistoryIndex <= 0; }, run: editorHistoryUndo },
            { id: 'redo', group: 'Redigering', label: 'Gendan', detail: 'Ctrl/Cmd+Shift+Z', keywords: 'gendan redo frem', disabled: function () { return editorHistoryIndex < 0 || editorHistoryIndex >= editorHistoryEntries.length - 1; }, run: editorHistoryRedo },
            { id: 'previous-section', group: 'Navigation', label: 'Forrige element', detail: 'Alt+↑', keywords: 'forrige element op navigation', run: function () { commandPaletteMoveSection(-1); } },
            { id: 'next-section', group: 'Navigation', label: 'Næste element', detail: 'Alt+↓', keywords: 'næste element ned navigation', run: function () { commandPaletteMoveSection(1); } },
            { id: 'copy-design', group: 'Design', label: 'Kopiér design', detail: 'Valgt element', keywords: 'kopier kopiér design stil', disabled: function () { return !$('#h18-inspector-copy-design').length || $('#h18-inspector-copy-design').prop('disabled'); }, run: function () { $('#h18-inspector-copy-design').trigger('click'); } },
            { id: 'paste-design', group: 'Design', label: 'Indsæt design', detail: 'Valgt element', keywords: 'indsæt paste design stil', disabled: function () { return !$('#h18-inspector-paste-design').length || $('#h18-inspector-paste-design').prop('disabled'); }, run: function () { $('#h18-inspector-paste-design').trigger('click'); } },
            { id: 'save-component', group: 'Design', label: 'Gem som pattern', detail: 'Valgt element', keywords: 'gem komponent genbrugelig preset', disabled: function () { return !$('#h18-save-section-preset').length || $('#h18-save-section-preset').prop('disabled'); }, run: function () { $('#h18-save-section-preset').trigger('click'); } },
            { id: 'focus-save', group: 'Side', label: 'Gå til Gem / ændringsbeskrivelse', detail: 'Gemmer ikke automatisk', keywords: 'gem save ændring version note beskrivelse', run: function () {
                const $note = $('#h18-page-editor-form [name="page_change_note"]');
                if ($note.length) { $note.get(0).scrollIntoView({ behavior: 'smooth', block: 'center' }); $note.trigger('focus'); }
                else { $('#h18-page-editor-form .h18-form-actions').last().get(0)?.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
            } },
            { id: 'public-page', group: 'Side', label: 'Åbn offentlig side', detail: 'Ny fane', keywords: 'åbn offentlig side preview frontend', disabled: function () { return !$('.h18-toolbar a[target="_blank"]').first().attr('href'); }, run: function () {
                const href = String($('.h18-toolbar a[target="_blank"]').first().attr('href') || '');
                if (href) { window.open(href, '_blank', 'noopener'); }
            } }
        );
        return commands;
    }

    function commandPaletteFilteredCommands(query) {
        const normalized = commandPaletteNormalize(query);
        const terms = normalized ? normalized.split(' ').filter(Boolean) : [];
        return commandPaletteBuildCommands().filter(function (command) {
            if (!terms.length) { return true; }
            const haystack = commandPaletteNormalize([command.group, command.label, command.detail, command.keywords].join(' '));
            return terms.every(function (term) { return haystack.indexOf(term) !== -1; });
        }).slice(0, 60);
    }

    function commandPaletteUpdateActive() {
        const $items = $('#h18-command-palette-results .h18-command-result');
        if (!$items.length) {
            $('#h18-command-palette-search').removeAttr('aria-activedescendant');
            return;
        }
        commandPaletteActiveIndex = Math.max(0, Math.min(commandPaletteActiveIndex, $items.length - 1));
        $items.removeClass('is-active').attr('aria-selected', 'false');
        const $active = $items.eq(commandPaletteActiveIndex).addClass('is-active').attr('aria-selected', 'true');
        $('#h18-command-palette-search').attr('aria-activedescendant', String($active.attr('id') || ''));
        const node = $active.get(0);
        if (node && typeof node.scrollIntoView === 'function') { node.scrollIntoView({ block: 'nearest' }); }
    }

    function commandPaletteRender(query) {
        const $results = $('#h18-command-palette-results').empty();
        commandPaletteVisibleCommands = commandPaletteFilteredCommands(query);
        commandPaletteActiveIndex = 0;
        let lastGroup = '';
        commandPaletteVisibleCommands.forEach(function (command, index) {
            if (command.group !== lastGroup) {
                $results.append($('<div>', { class: 'h18-command-group-label', text: command.group }));
                lastGroup = command.group;
            }
            const disabled = typeof command.disabled === 'function' ? Boolean(command.disabled()) : Boolean(command.disabled);
            const $button = $('<button>', {
                type: 'button', id: 'h18-command-result-' + index, class: 'h18-command-result' + (disabled ? ' is-disabled' : ''),
                role: 'option', 'aria-selected': 'false', disabled: disabled, 'data-command-index': index
            });
            $button.append($('<span>', { class: 'h18-command-result-main', text: command.label }));
            if (command.detail) { $button.append($('<small>', { text: command.detail })); }
            $results.append($button);
        });
        $('#h18-command-palette-empty').prop('hidden', commandPaletteVisibleCommands.length > 0);
        commandPaletteUpdateActive();
    }

    function commandPaletteOpen() {
        if (!$pageSections.length) { return; }
        commandPalettePreviousFocus = document.activeElement;
        $('#h18-command-palette').prop('hidden', false);
        $('#h18-command-palette-open').attr('aria-expanded', 'true');
        $('body').addClass('h18-command-palette-visible');
        const $search = $('#h18-command-palette-search').val('');
        commandPaletteRender('');
        window.setTimeout(function () { $search.trigger('focus').trigger('select'); }, 0);
    }

    function commandPaletteClose(restoreFocus) {
        $('#h18-command-palette').prop('hidden', true);
        $('#h18-command-palette-open').attr('aria-expanded', 'false');
        $('body').removeClass('h18-command-palette-visible');
        commandPaletteVisibleCommands = [];
        if (restoreFocus !== false && commandPalettePreviousFocus && typeof commandPalettePreviousFocus.focus === 'function') {
            commandPalettePreviousFocus.focus();
        }
        commandPalettePreviousFocus = null;
    }

    function commandPaletteExecute(index) {
        const command = commandPaletteVisibleCommands[Number(index) || 0];
        if (!command) { return; }
        const disabled = typeof command.disabled === 'function' ? Boolean(command.disabled()) : Boolean(command.disabled);
        if (disabled) { return; }
        commandPaletteClose(false);
        try { command.run(); } finally {
            if ($inspectedSection.length) { window.setTimeout(function () { $inspectedSection.find('.h18-canvas-preview').first().trigger('focus'); }, 0); }
        }
    }

    function commandPaletteMoveSection(direction) {
        const $rows = $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)');
        if (!$rows.length) { return; }
        let current = $inspectedSection.length ? $rows.index($inspectedSection) : -1;
        if (current < 0) { current = direction > 0 ? -1 : 0; }
        let next = current + (direction > 0 ? 1 : -1);
        if (next < 0) { next = $rows.length - 1; }
        if (next >= $rows.length) { next = 0; }
        commandPaletteScrollToRow($rows.eq(next));
    }

    function commandPaletteFocusable() {
        return $('#h18-command-palette .h18-command-palette-dialog').find('input:not(:disabled),button:not(:disabled),[href],select:not(:disabled),textarea:not(:disabled),[tabindex]:not([tabindex="-1"])').filter(':visible');
    }

    $(document).on('click', '#h18-command-palette-open', function (event) { event.preventDefault(); commandPaletteOpen(); });
    $(document).on('click', '.h18-command-palette-close,[data-command-close="1"]', function (event) { event.preventDefault(); commandPaletteClose(true); });
    $(document).on('input', '#h18-command-palette-search', function () { commandPaletteRender($(this).val()); });
    $(document).on('mouseenter', '.h18-command-result:not(:disabled)', function () {
        commandPaletteActiveIndex = Number($(this).attr('data-command-index')) || 0;
        commandPaletteUpdateActive();
    });
    $(document).on('click', '.h18-command-result:not(:disabled)', function () { commandPaletteExecute($(this).attr('data-command-index')); });

    $(document).on('keydown.h18CommandPalette', function (event) {
        const key = String(event.key || '').toLowerCase();
        if ((event.ctrlKey || event.metaKey) && key === 'k') {
            if (commandPaletteIsOpen()) {
                event.preventDefault();
                $('#h18-command-palette-search').trigger('focus').trigger('select');
                return;
            }
            if (commandPaletteIsEditableTarget(event.target)) { return; }
            event.preventDefault();
            commandPaletteOpen();
            return;
        }
        if (!commandPaletteIsOpen()) {
            if (event.altKey && !event.ctrlKey && !event.metaKey && (event.key === 'ArrowUp' || event.key === 'ArrowDown') && !commandPaletteIsEditableTarget(event.target)) {
                event.preventDefault();
                commandPaletteMoveSection(event.key === 'ArrowDown' ? 1 : -1);
            }
            return;
        }
        if (event.key === 'Escape') { event.preventDefault(); commandPaletteClose(true); return; }
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            event.preventDefault();
            if (!commandPaletteVisibleCommands.length) { return; }
            const direction = event.key === 'ArrowDown' ? 1 : -1;
            let next = commandPaletteActiveIndex;
            do {
                next = (next + direction + commandPaletteVisibleCommands.length) % commandPaletteVisibleCommands.length;
            } while ($('#h18-command-result-' + next).prop('disabled') && next !== commandPaletteActiveIndex);
            commandPaletteActiveIndex = next;
            commandPaletteUpdateActive();
            return;
        }
        if (event.key === 'Enter' && $(event.target).is('#h18-command-palette-search')) {
            event.preventDefault(); commandPaletteExecute(commandPaletteActiveIndex); return;
        }
        if (event.key === 'Tab') {
            const $focusable = commandPaletteFocusable();
            if (!$focusable.length) { event.preventDefault(); return; }
            const first = $focusable.get(0), last = $focusable.get($focusable.length - 1);
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        }
    });

    $(document).on('click', '#h18-editor-restore-draft', function (event) {
        event.preventDefault();
        editorHistoryFlushPending();
        editorDraftRestoreCandidate();
    });

    $(document).on('click', '#h18-editor-discard-draft', function (event) {
        event.preventDefault();
        editorDraftDiscardCandidate();
    });

    $(window).on('pagehide.h18EditorDraft', function () {
        if (!editorHistoryReady || editorHistorySubmitting) { return; }
        editorHistoryFlushPending();
        editorDraftSaveNow(false);
    });

    if (document && document.addEventListener) {
        document.addEventListener('visibilitychange', function () {
            if (document.visibilityState !== 'hidden' || !editorHistoryReady || editorHistorySubmitting) { return; }
            editorHistoryFlushPending();
            editorDraftSaveNow(false);
        });
    }


    /* v0.5.23 – Generic Dynamic Data schema + entry editor */
    const $dataSchemaFields = $('#h18-data-schema-fields');
    const dataFieldTemplate = document.getElementById('h18-data-field-template');
    let dataFieldSerialV0523 = 1000;
    function syncDataFieldRowsV0523(){
        if(!$dataSchemaFields.length)return;
        $dataSchemaFields.children('.h18-data-field-row:not(.is-removed)').each(function(index){$(this).find('.h18-data-field-drag').attr('title','Felt '+(index+1));});
    }
    if($dataSchemaFields.length){$dataSchemaFields.sortable({items:'> .h18-data-field-row:not(.is-removed)',handle:'.h18-data-field-drag',axis:'y',tolerance:'pointer',update:syncDataFieldRowsV0523});syncDataFieldRowsV0523();}
    $('#h18-data-add-field').on('click',function(){
        if(!dataFieldTemplate||!$dataSchemaFields.length)return;
        if($dataSchemaFields.children('.h18-data-field-row:not(.is-removed)').length>=30){window.alert('En datatype kan højst have 30 felter.');return;}
        dataFieldSerialV0523+=1;
        const html=dataFieldTemplate.innerHTML.replaceAll('__INDEX__',String(dataFieldSerialV0523));
        const $row=$(html.trim());$row.find('.h18-data-field-key').val('');$row.find('.h18-data-field-label').val('');$dataSchemaFields.append($row);syncDataFieldRowsV0523();
    });
    $(document).on('click','.h18-data-remove-field',function(){const $row=$(this).closest('.h18-data-field-row');$row.find('.h18-data-field-remove').val('1');$row.addClass('is-removed').hide();syncDataFieldRowsV0523();});
    $(document).on('blur','.h18-data-field-label',function(){const $row=$(this).closest('.h18-data-field-row');const $key=$row.find('.h18-data-field-key');if(!$key.val().trim())$key.val(slugify($(this).val()).replace(/-/g,'_'));});
    $('#h18-data-type-singular').on('blur',function(){const $key=$('#h18-data-type-key');if($key.length&&!$key.val().trim())$key.val(slugify($(this).val()).replace(/-/g,'_'));});
    $(document).on('click','.h18-data-media-pick',function(event){event.preventDefault();const $field=$(this).closest('.h18-data-media-field');const frame=wp.media({title:'Vælg medie',button:{text:'Brug medie'},multiple:false});frame.on('select',function(){const media=frame.state().get('selection').first().toJSON();const thumb=media.sizes&&media.sizes.thumbnail?media.sizes.thumbnail.url:media.url;$field.find('.h18-data-media-id').val(media.id||0);$field.find('.h18-data-media-preview').html($('<img>',{src:thumb,alt:media.alt||''}));});frame.open();});
    $(document).on('click','.h18-data-media-clear',function(event){event.preventDefault();const $field=$(this).closest('.h18-data-media-field');$field.find('.h18-data-media-id').val('0');$field.find('.h18-data-media-preview').empty();});

});
