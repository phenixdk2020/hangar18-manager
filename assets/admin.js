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
    let pageSectionNextIndex = 0;
    let pageCardSerial = 0;
    let $inspectedSection = $();
    let currentInspectorPanel = 'content';
    const pageUserPresets = {};
    let currentCanvasDevice = 'desktop';
    let currentCanvasState = 'normal';
    let selectedCanvasCardKey = '';
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
        window.console && console.warn('Hangar18: kunne ikke læse komponentbibliotek.', presetError);
    }

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
            spacer: 'Afstand', html: 'Importeret blok / HTML', css: 'Side-CSS', mail_form: 'Mailformular', poll: 'Afstemning', legacy: 'Eksisterende indhold'
        };
        return labels[String(type || '')] || 'Sektion';
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
            const active = $row.find('.h18-section-active').is(':checked');
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
            const $item = $('<div>', { class: 'h18-navigator-item' + (selected ? ' is-selected' : ''), 'data-section-index': index });
            $item.append($('<span>', { class: 'dashicons dashicons-menu h18-navigator-drag', title: 'Flyt lag' }));
            const $button = $('<button>', { type: 'button', class: 'h18-navigator-select' });
            $button.append($('<strong>', { text: inspectorTypeLabel(type) }));
            $button.append($('<small>', { text: title || 'Uden overskrift' }));
            $item.append($button);
            $item.append($('<span>', { class: 'h18-navigator-visibility ' + (active ? 'is-visible' : 'is-hidden'), title: active ? 'Synlig' : 'Skjult' }).append($('<span>', { class: 'dashicons ' + (active ? 'dashicons-visibility' : 'dashicons-hidden') })));
            $pageNavigatorList.append($item);
            count += 1;
        });
        $pageNavigatorCount.text(count);
        if (count > 1) {
            $pageNavigatorList.sortable({
                items: '> .h18-navigator-item', handle: '.h18-navigator-drag', axis: 'y', tolerance: 'pointer',
                update: function () {
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

    function renderUserPresets() {
        if (!$pageUserPresetsList.length) {
            return;
        }
        const presets = Object.values(pageUserPresets).sort(function (a, b) { return String(a.Name || '').localeCompare(String(b.Name || ''), 'da'); });
        $pageUserPresetsList.empty();
        if (!presets.length) {
            $pageUserPresetsList.html('<p class="description">Vælg en sektion og brug “Gem som komponent” i Inspector.</p>');
            return;
        }
        presets.forEach(function (preset) {
            const $row = $('<div>', { class: 'h18-user-preset-row', 'data-preset-id': String(preset.Id) });
            $row.append($('<button>', { type: 'button', class: 'h18-user-preset-insert' }).append($('<strong>', { text: String(preset.Name || 'Komponent') })).append($('<small>', { text: inspectorTypeLabel(preset.Section && preset.Section.Type) })));
            $row.append($('<button>', { type: 'button', class: 'h18-user-preset-delete', title: 'Slet komponent', 'aria-label': 'Slet komponent' }).append($('<span>', { class: 'dashicons dashicons-trash' })));
            $pageUserPresetsList.append($row);
        });
    }

    function sectionPresetData($row) {
        if (!$row || !$row.length) {
            return null;
        }
        const data = { Type: String($row.attr('data-section-type') || 'text') };
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
            if (['Key', 'Order', 'Remove', 'ResetVotes'].includes(fieldName)) {
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
            if (['Type', 'Cards', 'Key', 'Order', 'Remove'].includes(fieldName)) {
                return;
            }
            setSectionPresetField($row, fieldName, presetData[fieldName]);
        });
        $row.find('.h18-page-section-type').val(type);
        if (Array.isArray(presetData.Cards) && type === 'card_grid') {
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

    function inspectPageSection($row) {
        if (!$pageInspectorTarget.length || !$row.length || $row.hasClass('h18-page-section-removed')) {
            return;
        }
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
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
        rebuildPageNavigator();
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
        } else if (type === 'card') {
            setValue('Background', 'OffWhite');
            setValue('PaddingPx', 26);
            setValue('MobilePaddingPx', 20);
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
        } else if (type === 'buttons') {
            addTitle('Handling');
            canvasAddBodyText($inner, content);
            addButtons();
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
        const stateLabel = currentCanvasState === 'hover' ? 'Hover' : 'Normal';
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
            $label.insertBefore($hint); $normal.insertBefore($hint); $hover.insertBefore($hint);
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
        inspectPageSection($(this).closest('.h18-page-section-row'));
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
        const type = String($(this).val() || 'text');
        if (type === 'card_grid' && !pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length) {
            applyNewSectionDefaults($row, type);
        }
        refreshPageSectionType($row);
    });

    $(document).on('input', '.h18-section-title-input', function () {
        const $row = pageSectionForElement(this);
        $row.find('.h18-page-section-title-summary').text($(this).val());
        rebuildPageNavigator();
    });

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

    $(document).on('click', '.h18-navigator-select', function () {
        const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
        const $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
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
        if (preset && preset.Section) {
            applySectionPreset(preset.Section);
        }
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
        const data = sectionPresetData($inspectedSection);
        if (!data || data.Type === 'legacy') {
            window.alert('Denne sektion kan ikke gemmes som komponent.');
            return;
        }
        const defaultName = String($inspectedSection.find('.h18-page-section-title-summary').text() || inspectorTypeLabel(data.Type)).trim();
        const name = window.prompt('Navn på den genbrugelige komponent:', defaultName || 'Ny komponent');
        if (!name) {
            return;
        }
        const $button = $(this).prop('disabled', true).text('Gemmer…');
        $.post(Hangar18Manager.ajaxUrl || window.ajaxurl, {
            action: 'h18_save_page_preset', nonce: Hangar18Manager.pagePresetNonce, name: name, section: JSON.stringify(data)
        }).done(function (response) {
            if (!response || !response.success || !response.data || !response.data.preset) {
                window.alert((response && response.data && response.data.message) || 'Komponenten kunne ikke gemmes.');
                return;
            }
            const preset = response.data.preset;
            pageUserPresets[String(preset.Id)] = preset;
            renderUserPresets();
            $('.h18-builder-sidebar-tab[data-builder-tab="components"]').trigger('click');
        }).fail(function (xhr) {
            const message = xhr.responseJSON && xhr.responseJSON.data && xhr.responseJSON.data.message ? xhr.responseJSON.data.message : 'Komponenten kunne ikke gemmes.';
            window.alert(message);
        }).always(function () {
            $button.prop('disabled', false).text('Gem som komponent');
        });
    });

    $(document).on('click', '.h18-user-preset-delete', function () {
        const presetId = String($(this).closest('.h18-user-preset-row').attr('data-preset-id') || '');
        const preset = pageUserPresets[presetId];
        if (!preset || !window.confirm('Slet komponenten “' + String(preset.Name || 'Komponent') + '”?')) {
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
        addPageCard(pageSectionForElement(this), { Title: 'Ny kasse', Background: 'OffWhite', TextTone: 'Auto', Active: true });
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
        currentCanvasState = String($(this).data('state') || 'normal') === 'hover' ? 'hover' : 'normal';
        $('.h18-preview-state').removeClass('is-active');
        $(this).addClass('is-active');
        refreshAllCanvasPreviews();
    });

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
            currentCanvasState = String(entry.state) === 'hover' ? 'hover' : 'normal';
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

});
