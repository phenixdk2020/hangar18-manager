from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import tempfile
import zipfile


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


php_path = Path("hangar18-manager.php")
php = php_path.read_text(encoding="utf-8")
php = replace_once(php, " * Version: 0.5.6", " * Version: 0.5.7", "plugin header version")
php = replace_once(php, "    const VERSION = '0.5.6';", "    const VERSION = '0.5.7';", "plugin const version")
php_path.write_text(php, encoding="utf-8")

js_path = Path("assets/admin.js")
js = js_path.read_text(encoding="utf-8")
js = replace_once(
    js,
    "    const pageUserPresets = {};\n",
    "    const pageUserPresets = {};\n    let currentCanvasDevice = 'desktop';\n    let currentCanvasState = 'normal';\n",
    "canvas state variables",
)

live_canvas = r'''    function canvasFieldValue($row, fieldName, fallback) {
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
        const text = canvasTextFromHtml(value, 260);
        if (text) {
            $target.append($('<p>', { class: 'h18-canvas-preview-text', text: text }));
        }
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
            const $media = $('<div>', { class: 'h18-canvas-preview-media' });
            if (url) { $media.append($('<img>', { src: url, alt: '' })); } else { $media.append($('<span>', { text: 'Vælg billede' })); }
            if (String(canvasFieldValue($row, 'ImagePosition', 'Right')) === 'Left' && currentCanvasDevice !== 'mobile') {
                $grid.append($media, $copy);
            } else {
                $grid.append($copy, $media);
            }
            $inner.append($grid);
        } else if (type === 'image') {
            addTitle('Billede');
            const url = String(canvasFieldValue($row, 'MediaUrl', '') || '');
            const $image = $('<div>', { class: 'h18-canvas-preview-image' });
            if (url) { $image.append($('<img>', { src: url, alt: '' })); } else { $image.append($('<span>', { text: 'Intet billede valgt' })); }
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
                const cardTitle = String($card.find('[name$="[Title]"]').val() || 'Kort');
                const cardContent = canvasTextFromHtml($card.find('[name$="[Content]"]').val() || '', 90);
                const cardBackground = canvasPaletteColor($card.find('[name$="[Background]"]').val() || 'OffWhite');
                const $cardPreview = $('<div>', { class: 'h18-canvas-card' }).css('background', cardBackground);
                $cardPreview.append($('<strong>', { text: cardTitle }));
                if (cardContent) { $cardPreview.append($('<small>', { text: cardContent })); }
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
            $preview.css('minHeight', Math.max(120, height) + 'px');
        } else {
            $preview.css('minHeight', '0');
        }
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

'''
js = replace_once(js, "    if ($pageSections.length) {\n", live_canvas + "    if ($pageSections.length) {\n", "live canvas helper insertion")

js = replace_once(
    js,
    "        renderUserPresets();\n        rebuildPageNavigator();\n    }\n",
    "        renderUserPresets();\n        rebuildPageNavigator();\n        ensureCanvasToolbar();\n        refreshAllCanvasPreviews();\n        $('.h18-builder-canvas').addClass('h18-live-canvas-ready');\n    }\n",
    "canvas initialization",
)

js = replace_once(
    js,
    "        refreshHoverStyleMode($row);\n        rebuildPageNavigator();\n    }\n",
    "        refreshHoverStyleMode($row);\n        rebuildPageNavigator();\n        renderCanvasPreview($row);\n    }\n",
    "section type live refresh",
)

click_handlers = r'''    $(document).on('click keydown', '.h18-canvas-preview', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-inline-edit.is-editing').length) { return; }
        event.preventDefault();
        inspectPageSection($(this).closest('.h18-page-section-row'));
    });

    $(document).on('dblclick', '.h18-canvas-inline-edit', function (event) {
        event.preventDefault();
        event.stopPropagation();
        inspectPageSection($(this).closest('.h18-page-section-row'));
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
            renderCanvasPreview($(this).closest('.h18-page-section-row'));
        }
    });

    $(document).on('input change', '#h18-page-inspector-target :input', function () {
        const $row = pageSectionForElement(this);
        window.requestAnimationFrame(function () { renderCanvasPreview($row); });
    });

    $(document).on('click', '.h18-page-card-remove, .h18-page-card-restore, .h18-add-page-card', function () {
        const $row = pageSectionForElement(this);
        window.setTimeout(function () { renderCanvasPreview($row); }, 0);
    });

'''
js = replace_once(js, "    $(document).on('click', '.h18-page-section-edit', function (event) {\n", click_handlers + "    $(document).on('click', '.h18-page-section-edit', function (event) {\n", "canvas interaction handlers")

js = replace_once(
    js,
    "        $container.append($card);\n        initializePageCardSortables($container);\n        return $card;\n",
    "        $container.append($card);\n        initializePageCardSortables($container);\n        renderCanvasPreview($row);\n        return $card;\n",
    "card live preview refresh",
)
js = replace_once(
    js,
    "                    update: function () { syncPageCardOrder($container); }\n",
    "                    update: function () { syncPageCardOrder($container); renderCanvasPreview(pageSectionForElement($container)); }\n",
    "card sortable live preview",
)
js = replace_once(
    js,
    "        inspectPageSection($row);\n        $('html, body').animate({ scrollTop: $row.offset().top - 60 }, 250);\n        return $row;\n",
    "        inspectPageSection($row);\n        renderCanvasPreview($row);\n        $('html, body').animate({ scrollTop: $row.offset().top - 60 }, 250);\n        return $row;\n",
    "new section live preview",
)

old_device = r'''    $('.h18-preview-device').on('click', function () {
        const device = String($(this).data('device') || 'desktop');
        $('.h18-preview-device').removeClass('is-active');
        $(this).addClass('is-active');
        $pageSections.removeClass('h18-preview-desktop h18-preview-tablet h18-preview-mobile').addClass('h18-preview-' + device);
    });
'''
new_device = r'''    $('.h18-preview-device').on('click', function () {
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
'''
js = replace_once(js, old_device, new_device, "device/state toolbar")

js = replace_once(
    js,
    "            pageSectionControls($row, '.h18-section-bg-media-preview').html($('<img>', { src: preview, alt: image.alt || '' }));\n",
    "            pageSectionControls($row, '.h18-section-bg-media-preview').html($('<img>', { src: preview, alt: image.alt || '' }));\n            renderCanvasPreview($row);\n",
    "background media live refresh",
)
js = replace_once(
    js,
    "        pageSectionControls($row, '.h18-section-bg-media-preview').empty();\n",
    "        pageSectionControls($row, '.h18-section-bg-media-preview').empty();\n        renderCanvasPreview($row);\n",
    "background media remove live refresh",
)
js_path.write_text(js, encoding="utf-8")

css_path = Path("assets/admin.css")
css = css_path.read_text(encoding="utf-8")
css += r'''

/* v0.5.7 – live visual canvas */
.h18-builder-canvas.h18-live-canvas-ready{background:#e9eaec;overflow:hidden}
.h18-builder-canvas.h18-live-canvas-ready .h18-builder-canvas-heading{position:sticky;top:0;z-index:5;margin:-14px -14px 14px;padding:12px 14px;background:rgba(246,247,247,.96);border-bottom:1px solid #dcdcde;backdrop-filter:blur(6px)}
#h18-canvas-runtime-status{display:inline-flex;align-items:center;padding:5px 9px;border-radius:999px;background:#1d2327;color:#fff!important;font-weight:700;letter-spacing:.02em}
.h18-preview-state-heading{margin-left:8px;padding-left:12px;border-left:1px solid #dcdcde}
.h18-page-preview-toolbar .h18-preview-state.is-active{border-color:#8b4a2b;background:#fff2e8;color:#7b3f22}
.h18-live-canvas-ready .h18-page-sections{gap:18px;padding:16px;margin-inline:auto;border-radius:12px;background:#d8dadd;box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)}
.h18-live-canvas-ready .h18-page-sections.h18-preview-desktop{max-width:100%}
.h18-live-canvas-ready .h18-page-sections.h18-preview-tablet{max-width:760px}
.h18-live-canvas-ready .h18-page-sections.h18-preview-mobile{max-width:390px}
.h18-live-canvas-ready .h18-page-section-row{overflow:visible;background:transparent;border:0;box-shadow:none;border-radius:0}
.h18-live-canvas-ready .h18-page-section-header{position:relative;z-index:3;margin:0 8px -1px;padding:7px 10px;border:1px solid #c3c4c7;border-bottom:0;border-radius:7px 7px 0 0;background:rgba(255,255,255,.94);opacity:.78;transition:opacity .15s ease,border-color .15s ease}
.h18-live-canvas-ready .h18-page-section-row:hover>.h18-page-section-header,.h18-live-canvas-ready .h18-page-section-row.is-selected>.h18-page-section-header{opacity:1;border-color:#3858e9}
.h18-live-canvas-ready .h18-page-section-header-actions label{font-size:11px}
.h18-live-canvas-ready .h18-page-section-edit{min-height:28px;line-height:26px;padding:0 8px;font-size:11px}
.h18-canvas-preview{position:relative;box-sizing:border-box;width:100%;overflow:hidden;cursor:pointer;outline:0;transition:box-shadow .18s ease,opacity .18s ease,transform .18s ease,background-color .18s ease,color .18s ease,border-color .18s ease;transform-origin:center center}
.h18-canvas-preview:hover{box-shadow:0 0 0 2px rgba(56,88,233,.28),0 10px 24px rgba(0,0,0,.08)!important}
.h18-page-section-row.is-selected>.h18-canvas-preview{box-shadow:0 0 0 3px #3858e9,0 12px 26px rgba(0,0,0,.12)!important}
.h18-canvas-preview:focus-visible{box-shadow:0 0 0 3px #3858e9!important}
.h18-canvas-preview-inner{box-sizing:border-box;width:100%;min-height:56px;display:flex;flex-direction:column;justify-content:center;gap:10px}
.h18-canvas-preview-title{margin:0!important;color:inherit;font-size:clamp(19px,3vw,30px);line-height:1.12}
.h18-canvas-preview-text{margin:0!important;max-width:78ch;line-height:1.5;color:inherit}
.h18-canvas-preview[style*="text-align: center"] .h18-canvas-preview-text{margin-inline:auto!important}
.h18-canvas-preview-actions{display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:flex-start;margin-top:5px}
.h18-canvas-preview[style*="text-align: center"] .h18-canvas-preview-actions{justify-content:center}
.h18-canvas-preview-button{display:inline-flex;align-items:center;justify-content:center;min-height:36px;padding:7px 15px;border-radius:999px;background:#c3ae83;color:#20261d;font-weight:700;line-height:1.2}
.h18-canvas-preview-button.is-secondary{background:transparent;border:1px solid currentColor;color:inherit}
.h18-canvas-inline-edit{cursor:text;border-radius:4px}
.h18-canvas-inline-edit:hover{outline:1px dashed rgba(56,88,233,.7);outline-offset:3px}
.h18-canvas-inline-edit.is-editing{outline:2px solid #3858e9!important;outline-offset:4px;background:rgba(255,255,255,.14)}
.h18-canvas-text-image{display:grid;grid-template-columns:minmax(0,1fr) minmax(130px,.72fr);gap:22px;align-items:center}
.h18-preview-mobile .h18-canvas-text-image{grid-template-columns:1fr}
.h18-canvas-text-image-copy{display:flex;flex-direction:column;gap:10px;min-width:0}
.h18-canvas-preview-media,.h18-canvas-preview-image{display:flex;align-items:center;justify-content:center;min-height:110px;border:1px dashed rgba(82,90,95,.45);border-radius:8px;background:rgba(255,255,255,.18);overflow:hidden;color:inherit}
.h18-canvas-preview-media img,.h18-canvas-preview-image img{display:block;width:100%;height:auto;max-height:330px;object-fit:cover}
.h18-canvas-card-grid{display:grid;margin-top:8px}
.h18-canvas-card{display:flex;min-width:0;min-height:92px;flex-direction:column;gap:6px;padding:14px;border-radius:7px;color:#30382a;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.h18-canvas-card small{line-height:1.35;color:inherit;opacity:.82}
.h18-canvas-fake-form{display:grid;grid-template-columns:1fr 1fr;gap:8px;max-width:640px;margin-top:8px}
.h18-canvas-fake-form span{min-height:34px;padding:8px 10px;border:1px solid rgba(82,90,95,.4);border-radius:5px;background:rgba(255,255,255,.72);color:#525a5f}
.h18-canvas-fake-form .is-wide{grid-column:1/-1;min-height:70px}
.h18-canvas-fake-form b,.h18-canvas-poll b{display:inline-flex;width:max-content;padding:7px 14px;border-radius:999px;background:#c3ae83;color:#20261d}
.h18-canvas-poll{display:flex;flex-direction:column;gap:8px;max-width:520px;margin-top:8px}
.h18-canvas-spacer{display:flex;align-items:center;justify-content:center;width:100%;border:1px dashed rgba(82,90,95,.55);background:repeating-linear-gradient(-45deg,rgba(82,90,95,.06),rgba(82,90,95,.06) 7px,transparent 7px,transparent 14px);font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.h18-canvas-code-block{display:flex;flex-direction:column;gap:5px;padding:16px;border-radius:7px;background:#1d2327;color:#f0f0f1;font-family:Consolas,Monaco,monospace}
.h18-canvas-code-block small{color:#c3c4c7}
.h18-canvas-preview.is-device-hidden{filter:grayscale(.65);opacity:.42!important}
.h18-canvas-device-hidden-label{position:absolute;inset:auto 10px 10px auto;z-index:4;padding:5px 8px;border-radius:999px;background:#b32d2e;color:#fff;font-size:11px;font-weight:700;pointer-events:none}
.h18-builder-canvas[data-canvas-state="hover"] .h18-canvas-preview:after{content:"Hover preview";position:absolute;top:9px;right:9px;z-index:3;padding:4px 7px;border-radius:999px;background:#8b4a2b;color:#fff;font-size:10px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;pointer-events:none}
.h18-preview-mobile .h18-canvas-fake-form{grid-template-columns:1fr}.h18-preview-mobile .h18-canvas-fake-form .is-wide{grid-column:auto}
@media(prefers-reduced-motion:reduce){.h18-canvas-preview{transition:none!important}}
@media(max-width:1100px){.h18-preview-state-heading{margin-left:0;padding-left:0;border-left:0}.h18-live-canvas-ready .h18-page-sections{padding:10px}}
'''
css_path.write_text(css, encoding="utf-8")

readme_path = Path("readme.txt")
readme = readme_path.read_text(encoding="utf-8")
readme = replace_once(readme, "Version: 0.5.6", "Version: 0.5.7", "readme version")
marker = "== Version 0.5.6 – Normal/Hover states ==\n"
section = """== Version 0.5.7 – Live visuel canvas ==\n\nNyt:\n- midterfeltet i sideeditoren viser nu en live visuel gengivelse af sektionerne\n- klik direkte på et element i canvas for at vælge det i Inspector\n- Desktop, Tablet og Mobil bruger de faktiske responsive værdier i live preview\n- Normal/Hover kan simuleres direkte i editorens toolbar\n- designændringer i Inspector opdaterer canvas uden at siden først skal gemmes\n- overskrifter og knaptekster kan redigeres direkte med dobbeltklik i canvas\n- skjulte elementer forbliver synlige som redigerbare, nedtonede placeholders på det valgte device\n- hero, tekst/billede, kort, formularer, afstemninger, spacer, HTML og øvrige sektionstyper har egne visuelle previews\n- page-editor schema forbliver 1.10; v0.5.7 ændrer kun editorens visuelle arbejdslag og er derfor bagudkompatibel\n\n\n"""
readme = replace_once(readme, marker, section + marker, "readme changelog insertion")
readme_path.write_text(readme, encoding="utf-8")

zip_path = Path("dist/hangar18-manager.zip")
fd, tmp_name = tempfile.mkstemp(prefix="hangar18-v057-", suffix=".zip")
os.close(fd)
replacements = {
    "hangar18-manager.php": php_path.read_bytes(),
    "readme.txt": readme_path.read_bytes(),
    "assets/admin.js": js_path.read_bytes(),
    "assets/admin.css": css_path.read_bytes(),
}
seen = set()
with zipfile.ZipFile(zip_path, "r") as zin, zipfile.ZipFile(tmp_name, "w") as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        normalized = item.filename.replace("\\", "/")
        for relative, replacement in replacements.items():
            if normalized.endswith("/" + relative) or normalized == relative:
                data = replacement
                seen.add(relative)
                break
        zout.writestr(item, data)
missing = set(replacements) - seen
if missing:
    raise SystemExit(f"package entries missing: {sorted(missing)}")
os.replace(tmp_name, zip_path)

with zipfile.ZipFile(zip_path, "r") as zf:
    plugin_entries = [n for n in zf.namelist() if n.endswith("/hangar18-manager.php") or n == "hangar18-manager.php"]
    js_entries = [n for n in zf.namelist() if n.endswith("/assets/admin.js") or n == "assets/admin.js"]
    if len(plugin_entries) != 1 or len(js_entries) != 1:
        raise SystemExit("package validation could not identify unique plugin/js entries")
    if b"Version: 0.5.7" not in zf.read(plugin_entries[0]):
        raise SystemExit("package plugin version mismatch")
    if b"function renderCanvasPreview" not in zf.read(js_entries[0]):
        raise SystemExit("package live canvas missing")

sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
manifest_path = Path("update.json")
data = json.loads(manifest_path.read_text(encoding="utf-8"))
data["version"] = "0.5.7"
data["published_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
data["package_sha256"] = sha
data["changelog"] = [
    "Tilføjer live visuel canvas i sideeditorens arbejdsområde.",
    "Desktop, tablet og mobil gengiver deres faktiske responsive elementværdier.",
    "Normal og Hover kan simuleres direkte i editoren.",
    "Inspector-ændringer opdaterer canvas live uden gemning.",
    "Overskrifter og knaptekster kan redigeres direkte med dobbeltklik.",
    "Skjulte device-elementer vises som redigerbare placeholders i canvas.",
    "Page-editor schema forbliver 1.10 og eksisterende sidedata ændres ikke.",
]
manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"v0.5.7 package sha256={sha}")
