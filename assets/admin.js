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
    let pageSectionNextIndex = 0;

    $pageSections.children('.h18-page-section-row').each(function () {
        const value = parseInt($(this).attr('data-section-index'), 10);
        if (!Number.isNaN(value)) {
            pageSectionNextIndex = Math.max(pageSectionNextIndex, value + 1);
        }
    });

    function newSectionKey() {
        return 'sektion-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 9);
    }

    function syncPageSectionOrder() {
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
    }

    function refreshPageSectionType($row) {
        const type = String($row.find('.h18-page-section-type').val() || $row.find('input[name$="[Type]"]').val() || 'text');
        $row.find('.h18-section-type-field').each(function () {
            const types = String($(this).attr('data-types') || '').split(/\s+/);
            $(this).toggle(types.includes(type));
        });
        const labels = {
            text: 'Tekst',
            text_image: 'Tekst og billede',
            image: 'Stort billede',
            buttons: 'Handlingsknapper',
            card: 'Indholdskort',
            highlight: 'Fremhævet tekst',
            spacer: 'Afstand',
            mail_form: 'Mailformular',
            poll: 'Afstemning',
            legacy: 'Eksisterende indhold'
        };
        $row.find('.h18-page-section-summary').text(labels[type] || 'Sektion');
        $row.find('.h18-section-title-label').text(type === 'poll' ? 'Spørgsmål' : 'Overskrift');
    }

    function reindexPageSection($row, index) {
        $row.attr('data-section-index', index);
        $row.find('[name]').each(function () {
            const name = String($(this).attr('name') || '');
            $(this).attr('name', name.replace(/sections\[(?:\d+|__INDEX__)\]/, 'sections[' + index + ']'));
        });
        $row.find('.h18-page-section-key').val(newSectionKey());
        $row.find('.h18-page-section-remove').val('0');
        $row.removeClass('h18-page-section-removed');
        $row.find('input[name$="[ResetVotes]"]').prop('checked', false);
        $row.find('.h18-module-status').html('<em>Gem siden for at oprette modulet.</em>');
    }

    function applyNewSectionDefaults($row, type) {
        const setValue = function (field, value) {
            $row.find('[name$="[' + field + ']"]').val(value);
        };
        if (type === 'card') {
            setValue('Background', 'OffWhite');
            setValue('PaddingPx', 26);
            setValue('MobilePaddingPx', 20);
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
        }
    }

    if ($pageSections.length) {
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
        syncPageSectionOrder();
    }

    $(document).on('change', '.h18-page-section-type', function () {
        refreshPageSectionType($(this).closest('.h18-page-section-row'));
    });

    $(document).on('input', '.h18-section-title-input', function () {
        $(this).closest('.h18-page-section-row').find('.h18-page-section-title-summary').text($(this).val());
    });

    $('#h18-add-page-section').on('click', function (event) {
        event.preventDefault();
        if (!pageSectionTemplate || !$pageSections.length) {
            return;
        }
        if ($pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').length >= 25) {
            window.alert('En side kan højst have 25 aktive editorsektioner. Fjern en sektion, før du tilføjer en ny.');
            return;
        }
        const index = pageSectionNextIndex++;
        const html = pageSectionTemplate.innerHTML.replaceAll('__INDEX__', String(index));
        const $row = $(html.trim());
        reindexPageSection($row, index);
        const type = String($('#h18-new-section-type').val() || 'text');
        $row.find('.h18-page-section-type').val(type);
        applyNewSectionDefaults($row, type);
        refreshPageSectionType($row);
        $pageSections.append($row);
        syncPageSectionOrder();
        $('html, body').animate({ scrollTop: $row.offset().top - 60 }, 250);
    });

    $(document).on('click', '.h18-page-section-duplicate', function (event) {
        event.preventDefault();
        const $source = $(this).closest('.h18-page-section-row');
        const $copy = $source.clone(false, false);
        const index = pageSectionNextIndex++;
        reindexPageSection($copy, index);
        $copy.find('.h18-page-section-title-summary').text($copy.find('.h18-section-title-input').val() || '');
        refreshPageSectionType($copy);
        $source.after($copy);
        syncPageSectionOrder();
    });

    $(document).on('click', '.h18-page-section-delete', function (event) {
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        const removing = !$row.hasClass('h18-page-section-removed');
        $row.toggleClass('h18-page-section-removed', removing);
        $row.find('.h18-page-section-remove').val(removing ? '1' : '0');
        $(this).text(removing ? 'Fortryd fjernelse' : 'Fjern');
        syncPageSectionOrder();
    });

    $(document).on('click', '.h18-page-select-media', function (event) {
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        const frame = wp.media({
            title: Hangar18Manager.chooseImage,
            button: { text: Hangar18Manager.useImage },
            multiple: false,
            library: { type: 'image' }
        });
        frame.on('select', function () {
            const image = frame.state().get('selection').first().toJSON();
            const preview = image.sizes && image.sizes.thumbnail ? image.sizes.thumbnail.url : image.url;
            $row.find('.h18-section-media-id').val(image.id || '');
            $row.find('.h18-section-media-url').val(image.url || '');
            $row.find('.h18-section-media-preview').html($('<img>', { src: preview, alt: image.alt || '' }));
        });
        frame.open();
    });

    $(document).on('click', '.h18-page-remove-media', function (event) {
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        $row.find('.h18-section-media-id, .h18-section-media-url').val('');
        $row.find('.h18-section-media-preview').empty();
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

});
