jQuery(function ($) {
    'use strict';

    const config = window.H18UnsavedPreview || {};
    const $form = $('#h18-page-editor-form').first();
    if (!$form.length) { return; }

    const $header = $form.children('.h18-form-header').first();
    if (!$header.length || $('#h18-unsaved-preview-open').length) { return; }

    const basePreviewUrl = String(config.previewUrl || '').trim();
    const ajaxUrl = String(config.ajaxUrl || '').trim();
    const ajaxAction = String(config.action || 'h18_prepare_live_page_preview').trim();
    const nonce = String(config.nonce || '').trim();
    const pageSlug = String(config.pageSlug || '').trim();

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
    const $status = $('<div>', {
        class: 'h18-unsaved-preview-empty',
        text: 'Klargør live-forhåndsvisning…'
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
                    $('<span>', { text: 'Viser den aktuelle editor-tilstand med den rigtige frontend-renderer. Forhåndsvisning gemmer ikke siden.' })
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
                $('<div>', { class: 'h18-unsaved-preview-viewport is-desktop', 'data-h18-unsaved-preview-viewport': '1' }).append($status, $frame)
            )
        )
    );

    $('body').append($modal);

    const $viewport = $modal.find('[data-h18-unsaved-preview-viewport]');
    let opener = null;
    let request = null;

    function setStatus(message, isError) {
        $status.text(String(message || '')).toggleClass('is-error', Boolean(isError)).prop('hidden', !message);
        $frame.prop('hidden', Boolean(message));
    }

    function setDevice(device) {
        const normalized = ['desktop', 'tablet', 'mobile'].includes(device) ? device : 'desktop';
        $viewport.removeClass('is-desktop is-tablet is-mobile').addClass('is-' + normalized);
        $modal.find('[data-h18-preview-device]').each(function () {
            const active = String($(this).attr('data-h18-preview-device')) === normalized;
            $(this).toggleClass('is-active', active).attr('aria-pressed', active ? 'true' : 'false');
        });
    }

    function eachSectionKey(callback) {
        const seen = {};
        $form.find('.h18-page-section-key').each(function () {
            const key = String($(this).val() || '').trim();
            if (!key || seen[key]) { return; }
            seen[key] = true;
            callback(key);
        });
    }

    function collectSpanState() {
        const api = window.__h18LegoResizeV0841;
        const spans = {};
        if (!api || typeof api.stateForKey !== 'function') { return spans; }
        eachSectionKey(function (key) {
            try {
                const state = api.stateForKey(key);
                if (state && typeof state === 'object') { spans[key] = state; }
            } catch (ignore) {}
        });
        return spans;
    }

    function collectStackState() {
        const api = window.__h18LegoFixesV0851;
        const stacks = {};
        if (!api || typeof api.stackStateForKey !== 'function') { return stacks; }
        eachSectionKey(function (key) {
            try {
                const state = api.stackStateForKey(key);
                if (state && typeof state === 'object') { stacks[key] = state; }
            } catch (ignore) {}
        });
        return stacks;
    }

    function prepareLivePreview() {
        if (!basePreviewUrl || !ajaxUrl || !nonce || !pageSlug) {
            setStatus('Den valgte side kunne ikke klargøres til live-forhåndsvisning.', true);
            return;
        }

        if (request && typeof request.abort === 'function') { request.abort(); }
        setStatus('Klargør live-forhåndsvisning…', false);
        $frame.attr('src', 'about:blank');

        request = $.ajax({
            url: ajaxUrl,
            method: 'POST',
            dataType: 'json',
            data: {
                action: ajaxAction,
                nonce: nonce,
                page_slug: pageSlug,
                form_data: $form.serialize(),
                spans_json: JSON.stringify(collectSpanState()),
                stacks_json: JSON.stringify(collectStackState())
            }
        }).done(function (response) {
            const data = response && response.data ? response.data : {};
            const url = response && response.success ? String(data.previewUrl || '').trim() : '';
            if (!url) {
                setStatus(String(data.message || 'Live-forhåndsvisningen kunne ikke oprettes.'), true);
                return;
            }
            setStatus('', false);
            $frame.attr('src', url);
        }).fail(function (xhr, textStatus) {
            if (textStatus === 'abort') { return; }
            let message = 'Live-forhåndsvisningen kunne ikke oprettes.';
            if (xhr && xhr.responseJSON && xhr.responseJSON.data && xhr.responseJSON.data.message) {
                message = String(xhr.responseJSON.data.message);
            }
            setStatus(message, true);
        }).always(function () {
            request = null;
        });
    }

    function openPreview() {
        opener = document.activeElement;
        setDevice('desktop');
        $modal.prop('hidden', false).addClass('is-open');
        $('body').addClass('h18-unsaved-preview-open-body');
        $modal.find('.h18-unsaved-preview-close').trigger('focus');
        prepareLivePreview();
    }

    function closePreview() {
        if (request && typeof request.abort === 'function') { request.abort(); }
        request = null;
        $modal.removeClass('is-open').prop('hidden', true);
        $('body').removeClass('h18-unsaved-preview-open-body');
        $frame.attr('src', 'about:blank');
        setStatus('Klargør live-forhåndsvisning…', false);
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
