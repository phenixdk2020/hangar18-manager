jQuery(function ($) {
    'use strict';

    const config = window.H18UnsavedPreview || {};
    const $form = $('#h18-page-editor-form').first();
    if (!$form.length) { return; }

    const $header = $form.children('.h18-form-header').first();
    if (!$header.length || $('#h18-unsaved-preview-open').length) { return; }

    const previewUrl = String(config.previewUrl || '').trim();
    const $open = $('<button>', {
        type: 'button',
        id: 'h18-unsaved-preview-open',
        class: 'button button-secondary h18-unsaved-preview-open',
        text: 'Forhåndsvis side',
        'aria-haspopup': 'dialog',
        'aria-controls': 'h18-unsaved-preview-modal'
    });

    const $safeSwitch = $header.children('.h18-safe-switch').first();
    if ($safeSwitch.length) { $open.insertBefore($safeSwitch); }
    else { $header.append($open); }

    const $frame = $('<iframe>', {
        class: 'h18-unsaved-preview-frame',
        title: 'Frontend-forhåndsvisning af siden',
        loading: 'eager'
    });

    const $modal = $('<div>', {
        id: 'h18-unsaved-preview-modal',
        class: 'h18-unsaved-preview-modal',
        hidden: true
    }).append(
        $('<div>', { class: 'h18-unsaved-preview-backdrop', 'data-h18-unsaved-preview-close': '1' }),
        $('<section>', {
            class: 'h18-unsaved-preview-dialog',
            role: 'dialog',
            'aria-modal': 'true',
            'aria-labelledby': 'h18-unsaved-preview-title'
        }).append(
            $('<header>', { class: 'h18-unsaved-preview-toolbar' }).append(
                $('<div>', { class: 'h18-unsaved-preview-heading' }).append(
                    $('<strong>', { id: 'h18-unsaved-preview-title', text: 'Frontend-forhåndsvisning' }),
                    $('<span>', { text: 'Viser den senest gemte side med den rigtige frontend-renderer. Gem først for at medtage nye ændringer.' })
                ),
                $('<div>', { class: 'h18-unsaved-preview-devices', role: 'group', 'aria-label': 'Preview-størrelse' }).append(
                    $('<button>', { type: 'button', class: 'button is-active', text: 'Desktop', 'data-h18-preview-device': 'desktop', 'aria-pressed': 'true' }),
                    $('<button>', { type: 'button', class: 'button', text: 'Tablet', 'data-h18-preview-device': 'tablet', 'aria-pressed': 'false' }),
                    $('<button>', { type: 'button', class: 'button', text: 'Mobil', 'data-h18-preview-device': 'mobile', 'aria-pressed': 'false' })
                ),
                $('<button>', {
                    type: 'button',
                    class: 'button h18-unsaved-preview-close',
                    text: 'Luk',
                    'data-h18-unsaved-preview-close': '1',
                    'aria-label': 'Luk forhåndsvisning'
                })
            ),
            $('<div>', { class: 'h18-unsaved-preview-shell' }).append(
                $('<div>', { class: 'h18-unsaved-preview-viewport is-desktop', 'data-h18-unsaved-preview-viewport': '1' }).append(
                    previewUrl
                        ? $frame
                        : $('<p>', { class: 'h18-unsaved-preview-empty', text: 'Den valgte side kunne ikke findes som offentlig WordPress-side.' })
                )
            )
        )
    );

    $('body').append($modal);

    const $viewport = $modal.find('[data-h18-unsaved-preview-viewport]');
    let opener = null;

    function cacheBustedUrl() {
        if (!previewUrl) { return ''; }
        const separator = previewUrl.indexOf('?') === -1 ? '?' : '&';
        return previewUrl + separator + 'h18_frontend_preview=' + Date.now();
    }

    function setDevice(device) {
        const normalized = ['desktop', 'tablet', 'mobile'].includes(device) ? device : 'desktop';
        $viewport.removeClass('is-desktop is-tablet is-mobile').addClass('is-' + normalized);
        $modal.find('[data-h18-preview-device]').each(function () {
            const active = String($(this).attr('data-h18-preview-device')) === normalized;
            $(this).toggleClass('is-active', active).attr('aria-pressed', active ? 'true' : 'false');
        });
    }

    function openPreview() {
        opener = document.activeElement;
        setDevice('desktop');
        if (previewUrl) { $frame.attr('src', cacheBustedUrl()); }
        $modal.prop('hidden', false).addClass('is-open');
        $('body').addClass('h18-unsaved-preview-open-body');
        $modal.find('.h18-unsaved-preview-close').trigger('focus');
    }

    function closePreview() {
        $modal.removeClass('is-open').prop('hidden', true);
        $('body').removeClass('h18-unsaved-preview-open-body');
        if (previewUrl) { $frame.attr('src', 'about:blank'); }
        if (opener && typeof opener.focus === 'function') { opener.focus(); }
        opener = null;
    }

    $open.on('click', function (event) {
        event.preventDefault();
        openPreview();
    });

    $modal.on('click', '[data-h18-preview-device]', function () {
        setDevice(String($(this).attr('data-h18-preview-device') || 'desktop'));
    });

    $modal.on('click', '[data-h18-unsaved-preview-close]', function (event) {
        event.preventDefault();
        closePreview();
    });

    $(document).on('keydown.h18UnsavedPreview', function (event) {
        if (!$modal.hasClass('is-open')) { return; }
        if (event.key === 'Escape') {
            event.preventDefault();
            closePreview();
            return;
        }
        if (event.key !== 'Tab') { return; }
        const $focusable = $modal.find('button:visible,[href]:visible,[tabindex]:visible').filter('[tabindex!="-1"]');
        if (!$focusable.length) {
            event.preventDefault();
            return;
        }
        const first = $focusable.get(0);
        const last = $focusable.get($focusable.length - 1);
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    });
});
