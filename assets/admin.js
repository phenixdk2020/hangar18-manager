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
        $('#h18-inspector-copy-key, #h18-inspector-duplicate, #h18-save-section-preset').prop('disabled', !hasRow || type === 'legacy');
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
        if (!skipNavigator) {
            rebuildPageNavigator();
        }
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
        rebuildPageNavigator();
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
                    update: function () { syncPageCardOrder($container); }
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
    }

    function pageSectionForElement(element) {
        const $closest = $(element).closest('.h18-page-section-row');
        return $closest.length ? $closest : $inspectedSection;
    }

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
            pageSectionControls($row, '.h18-section-media-id').val(image.id || '');
            pageSectionControls($row, '.h18-section-media-url').val(image.url || '');
            pageSectionControls($row, '.h18-section-media-preview').html($('<img>', { src: preview, alt: image.alt || '' }));
        });
        frame.open();
    });

    $(document).on('click', '.h18-page-remove-media', function (event) {
        event.preventDefault();
        const $row = pageSectionForElement(this);
        pageSectionControls($row, '.h18-section-media-id, .h18-section-media-url').val('');
        pageSectionControls($row, '.h18-section-media-preview').empty();
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
        $('.h18-preview-device').removeClass('is-active');
        $(this).addClass('is-active');
        $pageSections.removeClass('h18-preview-desktop h18-preview-tablet h18-preview-mobile').addClass('h18-preview-' + device);
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
    }

});
