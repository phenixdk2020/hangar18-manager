jQuery(function ($) {
    'use strict';

    const $form = $('#h18-page-editor-form').first();
    const $sections = $('#h18-page-sections-sortable').first();
    if (!$form.length || !$sections.length) {
        return;
    }

    const $header = $form.children('.h18-form-header').first();
    if (!$header.length || $('#h18-unsaved-preview-open').length) {
        return;
    }

    const $open = $('<button>', {
        type: 'button',
        id: 'h18-unsaved-preview-open',
        class: 'button button-secondary h18-unsaved-preview-open',
        text: 'Forhåndsvis side',
        'aria-haspopup': 'dialog',
        'aria-controls': 'h18-unsaved-preview-modal'
    });

    const $safeSwitch = $header.children('.h18-safe-switch').first();
    if ($safeSwitch.length) {
        $open.insertBefore($safeSwitch);
    } else {
        $header.append($open);
    }

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
                    $('<strong>', { id: 'h18-unsaved-preview-title', text: 'Ugemt forhåndsvisning' }),
                    $('<span>', { text: 'Viser den aktuelle editor-state uden at gemme siden.' })
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
                    $('<div>', { class: 'h18-unsaved-preview-stage h18-preview-desktop', 'data-h18-unsaved-preview-stage': '1' })
                )
            )
        )
    );

    $('body').append($modal);

    const $viewport = $modal.find('[data-h18-unsaved-preview-viewport]');
    const $stage = $modal.find('[data-h18-unsaved-preview-stage]');
    let opener = null;

    function topLevelRows() {
        return $sections.children('.h18-page-section-row').filter(function () {
            const parent = String($(this).find('.h18-layout-parent-key').first().val() || '').trim();
            return parent === '';
        });
    }

    function sanitizeClone($clone) {
        $clone.removeAttr('id tabindex role title');
        $clone.find('[id]').removeAttr('id');
        $clone.find('[contenteditable]').removeAttr('contenteditable');
        $clone.find('.ui-sortable-handle').removeClass('ui-sortable-handle');

        /*
         * Preview is cloned from the live editor canvas. The selected element can
         * therefore contain transient editor chrome at the exact moment the user
         * opens preview. Strip the chrome wrappers themselves before removing form
         * controls; otherwise labels such as "Billede", "Fokus X" and
         * "DIREKTE DESIGN" remain as empty floating panels in the preview.
         */
        $clone.find([
            '.h18-v0811-runtime-badge',
            '.h18-v0811-side-drop-zone',
            '.h18-v0811-kasse-drop-zone',
            '.h18-v0814-auto-drop-zone',
            '.h18-ud-box-child-actions',
            '.h18-page-section-actions',
            '.h18-section-toolbar',
            '.h18-builder-drop-hint',
            '.h18-canvas-direct-controls',
            '.h18-canvas-padding-handle',
            '.h18-canvas-margin-handle',
            '.h18-canvas-image-tools',
            '.h18-canvas-focal-dot',
            '.h18-canvas-box-model-overlay',
            '.h18-canvas-card-drag-handle',
            '.h18-condition-preview-badge',
            '[data-h18-v0811-edit-child]',
            '[data-h18-v0814-auto-drop]'
        ].join(',')).remove();

        /* Remove editor-only interaction/selection state from the cloned canvas. */
        $clone.removeClass('is-direct-dragging is-margin-dragging is-device-hidden');
        $clone.find('.is-card-selected').removeClass('is-card-selected');
        $clone.find('.is-editing').removeClass('is-editing');
        $clone.find('.h18-canvas-editable-media')
            .removeAttr('tabindex role title')
            .removeClass('is-focal-dragging');

        /* Canvas buttons are editor controls; page CTA previews are anchors. */
        $clone.find('button').remove();
        $clone.find('input,select,textarea').remove();
        return $clone;
    }

    function rebuildPreview() {
        $stage.empty();
        const $rows = topLevelRows();

        $rows.each(function () {
            const $row = $(this);
            const $preview = $row.children('.h18-canvas-preview').first();
            if (!$preview.length) {
                return;
            }
            const $clone = sanitizeClone($preview.clone(false, false));
            $clone.addClass('h18-unsaved-preview-section');
            $stage.append($clone);
        });

        if (!$stage.children().length) {
            $stage.append($('<p>', { class: 'h18-unsaved-preview-empty', text: 'Siden har ingen synlige sektioner endnu.' }));
        }
    }

    function setDevice(device) {
        const normalized = ['desktop', 'tablet', 'mobile'].includes(device) ? device : 'desktop';
        $viewport.removeClass('is-desktop is-tablet is-mobile').addClass('is-' + normalized);
        $stage.removeClass('h18-preview-desktop h18-preview-tablet h18-preview-mobile').addClass('h18-preview-' + normalized);
        $modal.find('[data-h18-preview-device]').each(function () {
            const active = String($(this).attr('data-h18-preview-device')) === normalized;
            $(this).toggleClass('is-active', active).attr('aria-pressed', active ? 'true' : 'false');
        });
    }

    function openPreview() {
        opener = document.activeElement;
        rebuildPreview();
        setDevice('desktop');
        $modal.prop('hidden', false).addClass('is-open');
        $('body').addClass('h18-unsaved-preview-open-body');
        $modal.find('.h18-unsaved-preview-close').trigger('focus');
    }

    function closePreview() {
        $modal.removeClass('is-open').prop('hidden', true);
        $('body').removeClass('h18-unsaved-preview-open-body');
        if (opener && typeof opener.focus === 'function') {
            opener.focus();
        }
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
        if (!$modal.hasClass('is-open')) {
            return;
        }
        if (event.key === 'Escape') {
            event.preventDefault();
            closePreview();
            return;
        }
        if (event.key !== 'Tab') {
            return;
        }
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
