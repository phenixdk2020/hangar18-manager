from pathlib import Path
import json, re

ROOT = Path('.')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


def sub_once(text, pattern, repl, label, flags=0):
    text2, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text2

php_path = ROOT / 'hangar18-manager.php'
js_path = ROOT / 'assets/admin.js'
css_path = ROOT / 'assets/admin.css'
readme_path = ROOT / 'readme.txt'
manifest_path = ROOT / 'update.json'

php = php_path.read_text()
js = js_path.read_text()
css = css_path.read_text()
readme = readme_path.read_text()
manifest = json.loads(manifest_path.read_text())

# Version.
php = replace_once(php, ' * Version: 0.5.9', ' * Version: 0.5.10', 'plugin header')
php = replace_once(php, "    const VERSION = '0.5.9';", "    const VERSION = '0.5.10';", 'version constant')
php, schema_count = re.subn(r"('Version'\s*=>\s*)'1\.10'", r"\1'1.11'", php)
if schema_count != 7:
    raise SystemExit(f'page schema: expected 7 replacements, found {schema_count}')

# Section defaults: foreground image controls.
default_anchor = """            'MediaId'               => 0,\n            'MediaUrl'              => '',\n            'ImagePosition'         => 'Right',\n"""
default_repl = """            'MediaId'               => 0,\n            'MediaUrl'              => '',\n            'ImagePosition'         => 'Right',\n            'ImageAspectRatio'      => 'Auto',\n            'ImageFit'              => 'Cover',\n            'ImageFocalXPercent'    => 50,\n            'ImageFocalYPercent'    => 50,\n            'ImageHeightPx'         => 0,\n            'MobileImageHeightPx'   => 0,\n"""
php = replace_once(php, default_anchor, default_repl, 'image defaults')

# Normalization rules.
norm_anchor = """        $image_position = (string) ($raw['ImagePosition'] ?? 'Right');\n        if (!in_array($image_position, ['Left', 'Right'], true)) {\n            $image_position = 'Right';\n        }\n"""
norm_repl = norm_anchor + """        $image_aspect = (string) ($raw['ImageAspectRatio'] ?? 'Auto');\n        if (!in_array($image_aspect, ['Auto', '1:1', '4:3', '3:2', '16:9'], true)) {\n            $image_aspect = 'Auto';\n        }\n        $image_fit = (string) ($raw['ImageFit'] ?? 'Cover');\n        if (!in_array($image_fit, ['Cover', 'Contain'], true)) {\n            $image_fit = 'Cover';\n        }\n"""
php = replace_once(php, norm_anchor, norm_repl, 'image normalization rules')

return_anchor = """            'MediaId'               => absint($raw['MediaId'] ?? 0),\n            'MediaUrl'              => esc_url_raw((string) ($raw['MediaUrl'] ?? '')),\n            'ImagePosition'         => $image_position,\n"""
return_repl = return_anchor + """            'ImageAspectRatio'      => $image_aspect,\n            'ImageFit'              => $image_fit,\n            'ImageFocalXPercent'    => $this->clamp_int($raw['ImageFocalXPercent'] ?? 50, 0, 100, 50),\n            'ImageFocalYPercent'    => $this->clamp_int($raw['ImageFocalYPercent'] ?? 50, 0, 100, 50),\n            'ImageHeightPx'         => $this->clamp_int($raw['ImageHeightPx'] ?? 0, 0, 1200, 0),\n            'MobileImageHeightPx'   => $this->clamp_int($raw['MobileImageHeightPx'] ?? 0, 0, 900, 0),\n"""
php = replace_once(php, return_anchor, return_repl, 'normalized image fields')

# Add inspector controls after the existing desktop image-position field.
image_pos_pattern = r'''(\s*<div class="h18-field h18-section-type-field" data-types="text_image">\s*<label><strong>Billedplacering på desktop</strong></label>\s*<select name="<\?php echo esc_attr\(\$prefix\); \?>\[ImagePosition\]">.*?</select>\s*</div>)'''
image_controls = r'''\1
                            <div class="h18-section-type-field h18-field-wide h18-image-design-fields" data-types="text_image image">
                                <h4>Billedudsnit og fokus</h4>
                                <p class="description">Auto bevarer den nuværende billedhøjde. Vælg et format eller en højde for at aktivere beskæring. Fokuspunktet styrer, hvilken del af billedet der prioriteres.</p>
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Format</strong></label><select name="<?php echo esc_attr($prefix); ?>[ImageAspectRatio]"><option value="Auto" <?php selected($section['ImageAspectRatio'], 'Auto'); ?>>Auto / original</option><option value="1:1" <?php selected($section['ImageAspectRatio'], '1:1'); ?>>1:1</option><option value="4:3" <?php selected($section['ImageAspectRatio'], '4:3'); ?>>4:3</option><option value="3:2" <?php selected($section['ImageAspectRatio'], '3:2'); ?>>3:2</option><option value="16:9" <?php selected($section['ImageAspectRatio'], '16:9'); ?>>16:9</option></select></div>
                                    <div class="h18-field"><label><strong>Tilpasning</strong></label><select name="<?php echo esc_attr($prefix); ?>[ImageFit]"><option value="Cover" <?php selected($section['ImageFit'], 'Cover'); ?>>Fyld / beskær</option><option value="Contain" <?php selected($section['ImageFit'], 'Contain'); ?>>Vis hele billedet</option></select></div>
                                    <div class="h18-field"><label><strong>Fokus vandret (%)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[ImageFocalXPercent]" value="<?php echo esc_attr($section['ImageFocalXPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Fokus lodret (%)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[ImageFocalYPercent]" value="<?php echo esc_attr($section['ImageFocalYPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Højde desktop/tablet (px)</strong></label><input type="number" min="0" max="1200" name="<?php echo esc_attr($prefix); ?>[ImageHeightPx]" value="<?php echo esc_attr($section['ImageHeightPx']); ?>" /><p class="description">0 = automatisk.</p></div>
                                    <div class="h18-field"><label><strong>Højde mobil (px)</strong></label><input type="number" min="0" max="900" name="<?php echo esc_attr($prefix); ?>[MobileImageHeightPx]" value="<?php echo esc_attr($section['MobileImageHeightPx']); ?>" /><p class="description">0 = automatisk.</p></div>
                                </div>
                            </div>'''
php = sub_once(php, image_pos_pattern, image_controls, 'image inspector controls', flags=re.S)

# Frontend CSS variables for image presentation.
style_anchor = """            '--h18-section-bg-position:' . strtolower((string) ($section['BackgroundImagePosition'] ?? 'Center')) . ';' .\n            '--h18-section-bg-size:' . strtolower((string) ($section['BackgroundImageSize'] ?? 'Cover')) . ';' .\n            '--h18-radius-tl:' . $radius_tl . 'px;' .\n"""
style_repl = """            '--h18-section-bg-position:' . strtolower((string) ($section['BackgroundImagePosition'] ?? 'Center')) . ';' .\n            '--h18-section-bg-size:' . strtolower((string) ($section['BackgroundImageSize'] ?? 'Cover')) . ';' .\n            '--h18-image-aspect:' . (($section['ImageAspectRatio'] ?? 'Auto') === 'Auto' ? 'auto' : str_replace(':', ' / ', (string) $section['ImageAspectRatio'])) . ';' .\n            '--h18-image-fit:' . strtolower((string) ($section['ImageFit'] ?? 'Cover')) . ';' .\n            '--h18-image-position:' . (int) ($section['ImageFocalXPercent'] ?? 50) . '% ' . (int) ($section['ImageFocalYPercent'] ?? 50) . '%;' .\n            '--h18-image-height:' . ((int) ($section['ImageHeightPx'] ?? 0) > 0 ? (int) $section['ImageHeightPx'] . 'px' : 'auto') . ';' .\n            '--h18-mobile-image-height:' . ((int) ($section['MobileImageHeightPx'] ?? 0) > 0 ? (int) $section['MobileImageHeightPx'] . 'px' : 'auto') . ';' .\n            '--h18-radius-tl:' . $radius_tl . 'px;' .\n"""
php = replace_once(php, style_anchor, style_repl, 'frontend image variables')

old_img_css = "'.h18-editor-media img,.h18-editor-image img{display:block;width:100%;height:auto;border-radius:inherit}.h18-editor-actions{display:flex;gap:12px;flex-wrap:wrap;justify-content:var(--h18-justify,flex-start)}' ."
new_img_css = "'.h18-editor-media img,.h18-editor-image img{display:block;width:100%;height:var(--h18-image-height,auto);aspect-ratio:var(--h18-image-aspect,auto);object-fit:var(--h18-image-fit,cover);object-position:var(--h18-image-position,50% 50%);border-radius:inherit}.h18-editor-actions{display:flex;gap:12px;flex-wrap:wrap;justify-content:var(--h18-justify,flex-start)}' ."
php = replace_once(php, old_img_css, new_img_css, 'frontend image css')

mobile_anchor = '.h18-editor-text-image{grid-template-columns:1fr}.h18-editor-text-image .h18-editor-media{order:-1}.h18-page-form-grid{grid-template-columns:1fr}'
mobile_repl = '.h18-editor-text-image{grid-template-columns:1fr}.h18-editor-text-image .h18-editor-media{order:-1}.h18-editor-media img,.h18-editor-image img{height:var(--h18-mobile-image-height,var(--h18-image-height,auto))}.h18-page-form-grid{grid-template-columns:1fr}'
php = replace_once(php, mobile_anchor, mobile_repl, 'mobile image height css')

# ---- Admin canvas JavaScript ----
helper_anchor = "    function canvasBuildPreviewContent($row, $preview) {"
image_helpers = r'''    function canvasImageSettings($row) {
        const aspectValue = String(canvasFieldValue($row, 'ImageAspectRatio', 'Auto'));
        const aspectMap = { Auto: 'auto', '1:1': '1 / 1', '4:3': '4 / 3', '3:2': '3 / 2', '16:9': '16 / 9' };
        const heightField = currentCanvasDevice === 'mobile' ? 'MobileImageHeightPx' : 'ImageHeightPx';
        return {
            aspect: aspectMap[aspectValue] || 'auto',
            aspectValue: aspectValue,
            fit: String(canvasFieldValue($row, 'ImageFit', 'Cover')).toLowerCase(),
            x: Math.max(0, Math.min(100, canvasNumber($row, 'ImageFocalXPercent', 50))),
            y: Math.max(0, Math.min(100, canvasNumber($row, 'ImageFocalYPercent', 50))),
            heightField: heightField,
            height: Math.max(0, canvasNumber($row, heightField, 0))
        };
    }

    function canvasApplySectionImageStyle($row, $scope) {
        if (!$row || !$row.length || !$scope || !$scope.length) { return; }
        const settings = canvasImageSettings($row);
        $scope.find('img').css({
            width: '100%',
            height: settings.height > 0 ? settings.height + 'px' : 'auto',
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
            canvasImageRange(currentCanvasDevice === 'mobile' ? 'Højde mobil' : 'Højde', settings.heightField, settings.height, 0, currentCanvasDevice === 'mobile' ? 900 : 1200, ' px')
        );
        const $dot = $('<button>', {
            type: 'button', class: 'h18-canvas-focal-dot',
            'aria-label': 'Træk fokuspunkt', title: 'Træk for at flytte fokuspunkt'
        }).css({ left: settings.x + '%', top: settings.y + '%' });
        $media.append($tools, $dot);
    }

''' + helper_anchor
js = replace_once(js, helper_anchor, image_helpers, 'canvas image helpers')

# Make canvas foreground images interactive and style-aware.
text_image_old = """            const $media = $('<div>', { class: 'h18-canvas-preview-media' });\n            if (url) { $media.append($('<img>', { src: url, alt: '' })); } else { $media.append($('<span>', { text: 'Vælg billede' })); }\n"""
text_image_new = """            const $media = $('<div>', { class: 'h18-canvas-preview-media h18-canvas-editable-media', tabindex: '0', role: 'button', title: 'Klik for billedkontroller · dobbeltklik for at skifte billede' });\n            if (url) { $media.append($('<img>', { src: url, alt: '' })); } else { $media.append($('<span>', { class: 'h18-canvas-image-placeholder', text: 'Vælg billede' })); }\n            canvasApplySectionImageStyle($row, $media);\n"""
js = replace_once(js, text_image_old, text_image_new, 'text_image canvas media')

image_old = """            const $image = $('<div>', { class: 'h18-canvas-preview-image' });\n            if (url) { $image.append($('<img>', { src: url, alt: '' })); } else { $image.append($('<span>', { text: 'Intet billede valgt' })); }\n"""
image_new = """            const $image = $('<div>', { class: 'h18-canvas-preview-image h18-canvas-editable-media', tabindex: '0', role: 'button', title: 'Klik for billedkontroller · dobbeltklik for at skifte billede' });\n            if (url) { $image.append($('<img>', { src: url, alt: '' })); } else { $image.append($('<span>', { class: 'h18-canvas-image-placeholder', text: 'Intet billede valgt' })); }\n            canvasApplySectionImageStyle($row, $image);\n"""
js = replace_once(js, image_old, image_new, 'image canvas media')

js = replace_once(js, "        $preview.empty().append($inner);\n    }\n\n\n    function canvasCardKey", "        $preview.empty().append($inner);\n        renderCanvasImageTools($row, $preview);\n    }\n\n\n    function canvasCardKey", 'render image tools')

# Reuse the new picker from the old Inspector button and keep canvas live.
picker_pattern = r"    \$\(document\)\.on\('click', '\.h18-page-select-media', function \(event\) \{.*?\n    \}\);\n\n    \$\(document\)\.on\('click', '\.h18-page-remove-media', function \(event\) \{"
picker_repl = """    $(document).on('click', '.h18-page-select-media', function (event) {\n        event.preventDefault();\n        canvasOpenSectionMedia(pageSectionForElement(this));\n    });\n\n    $(document).on('click', '.h18-page-remove-media', function (event) {"""
js = sub_once(js, picker_pattern, picker_repl, 'media picker refactor', flags=re.S)

remove_old = """        pageSectionControls($row, '.h18-section-media-id, .h18-section-media-url').val('');\n        pageSectionControls($row, '.h18-section-media-preview').empty();\n    });\n"""
remove_new = """        pageSectionControls($row, '.h18-section-media-id, .h18-section-media-url').val('');\n        pageSectionControls($row, '.h18-section-media-preview').empty();\n        renderCanvasPreview($row);\n    });\n"""
js = replace_once(js, remove_old, remove_new, 'media remove live refresh')

# Image interactions before generic inline editing.
inline_anchor = "    $(document).on('dblclick', '.h18-canvas-inline-edit', function (event) {"
image_events = r'''    $(document).on('click keydown', '.h18-canvas-editable-media', function (event) {
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

''' + inline_anchor
js = replace_once(js, inline_anchor, image_events, 'canvas image events')

# Box-model overlay and margin handles added after existing padding handles.
box_anchor = """        ].forEach(function (item) {\n            $preview.append($('<button>', {\n                type: 'button', class: 'h18-canvas-padding-handle is-' + item[0],\n                'data-canvas-handle-field': item[1], 'data-canvas-handle-axis': item[2],\n                'data-canvas-handle-sign': item[3], 'data-canvas-handle-value': item[4],\n                title: 'Træk for at ændre indvendig luft'\n            }).append($('<span>', { class: 'dashicons dashicons-move' })));\n        });\n    }\n\n    function ensureCanvasToolbar() {\n"""
box_repl = """        ].forEach(function (item) {\n            $preview.append($('<button>', {\n                type: 'button', class: 'h18-canvas-padding-handle is-' + item[0],\n                'data-canvas-handle-field': item[1], 'data-canvas-handle-axis': item[2],\n                'data-canvas-handle-sign': item[3], 'data-canvas-handle-value': item[4],\n                title: 'Træk for at ændre indvendig luft'\n            }).append($('<span>', { class: 'dashicons dashicons-move' })));\n        });\n\n        $preview.append($('<div>', { class: 'h18-canvas-box-model-overlay', 'aria-hidden': 'true' }).append(\n            $('<span>', { class: 'is-margin-top', text: 'M ' + Math.round(layout.top) }),\n            $('<span>', { class: 'is-padding', text: 'P ' + Math.round(layout.pad) + ' / ' + Math.round(layout.padX) }),\n            $('<span>', { class: 'is-margin-bottom', text: 'M ' + Math.round(layout.bottom) })\n        ));\n        [\n            ['top', fields.top, 'y', 1, layout.top],\n            ['bottom', fields.bottom, 'y', -1, layout.bottom]\n        ].forEach(function (item) {\n            $preview.append($('<button>', {\n                type: 'button', class: 'h18-canvas-margin-handle is-' + item[0],\n                'data-canvas-margin-field': item[1], 'data-canvas-margin-axis': item[2],\n                'data-canvas-margin-sign': item[3], 'data-canvas-margin-value': item[4],\n                title: 'Træk for at ændre ydre afstand'\n            }).append($('<span>', { text: 'M' })));\n        });\n    }\n\n    function ensureCanvasToolbar() {\n"""
js = replace_once(js, box_anchor, box_repl, 'box model controls')

# Margin dragging: separate from padding dragging to avoid changing legacy direct-control behavior.
inspector_input_anchor = "    $(document).on('input change', '#h18-page-inspector-target :input', function () {"
margin_events = r'''    let canvasMarginDrag = null;
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

''' + inspector_input_anchor
js = replace_once(js, inspector_input_anchor, margin_events, 'margin drag events')

# Prevent canvas parent click handling while operating image or margin controls.
old_stop = "$(document).on('click pointerdown', '.h18-canvas-direct-controls, .h18-canvas-padding-handle', function (event) {"
new_stop = "$(document).on('click pointerdown', '.h18-canvas-direct-controls, .h18-canvas-padding-handle, .h18-canvas-margin-handle, .h18-canvas-image-tools, .h18-canvas-focal-dot', function (event) {"
js = replace_once(js, old_stop, new_stop, 'canvas control event isolation')

# Admin CSS: append isolated v0.5.10 rules.
css += r'''

/* v0.5.10 – direkte billedredigering og box-model */
.h18-canvas-editable-media{position:relative;min-height:86px;overflow:hidden;border-radius:8px;outline:1px dashed rgba(34,113,177,.28);cursor:pointer}
.h18-canvas-editable-media>img{display:block;width:100%;max-width:none}
.h18-canvas-image-placeholder{display:flex;min-height:120px;align-items:center;justify-content:center;padding:20px;background:#f6f7f7;border:1px dashed #8c8f94;color:#646970}
.h18-canvas-image-tools{position:absolute;z-index:25;top:10px;right:10px;display:grid;grid-template-columns:repeat(2,minmax(112px,1fr));gap:7px;width:min(430px,calc(100% - 20px));padding:10px;background:rgba(255,255,255,.96);border:1px solid #8c8f94;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.16);color:#1d2327;text-align:left;cursor:default}
.h18-canvas-image-tools>strong,.h18-canvas-image-actions{grid-column:1/-1}.h18-canvas-image-actions{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.h18-canvas-image-select,.h18-canvas-image-range{display:grid;gap:3px;font-size:11px}.h18-canvas-image-select select{width:100%;min-height:30px}.h18-canvas-image-range{grid-template-columns:1fr auto}.h18-canvas-image-range input{grid-column:1/-1;width:100%}.h18-canvas-image-range output{font-weight:700}
.h18-canvas-focal-dot{position:absolute;z-index:24;width:24px;height:24px;margin:-12px 0 0 -12px;padding:0;border:2px solid #fff;border-radius:50%;background:#2271b1;box-shadow:0 0 0 2px rgba(0,0,0,.35);cursor:move}.h18-canvas-focal-dot:after{position:absolute;inset:7px;content:"";border-radius:50%;background:#fff}.h18-canvas-editable-media.is-focal-dragging{cursor:crosshair}
.h18-canvas-box-model-overlay{position:absolute;z-index:18;inset:0;pointer-events:none;border:1px dashed rgba(219,166,23,.75)}.h18-canvas-box-model-overlay span{position:absolute;padding:2px 5px;border-radius:4px;background:rgba(48,56,42,.88);color:#fff;font-size:10px;font-weight:700;line-height:1.2}.h18-canvas-box-model-overlay .is-margin-top{top:-18px;left:50%;transform:translateX(-50%)}.h18-canvas-box-model-overlay .is-padding{top:6px;left:6px}.h18-canvas-box-model-overlay .is-margin-bottom{bottom:-18px;left:50%;transform:translateX(-50%)}
.h18-canvas-margin-handle{position:absolute;z-index:27;left:50%;display:flex;align-items:center;justify-content:center;width:28px;height:18px;margin-left:-14px;padding:0;border:1px solid #2271b1;border-radius:999px;background:#fff;color:#2271b1;font-size:10px;font-weight:800;cursor:ns-resize;box-shadow:0 2px 8px rgba(0,0,0,.14)}.h18-canvas-margin-handle.is-top{top:-24px}.h18-canvas-margin-handle.is-bottom{bottom:-24px}.h18-canvas-preview.is-margin-dragging{outline:2px solid #2271b1}
@media(max-width:900px){.h18-canvas-image-tools{grid-template-columns:1fr;width:min(300px,calc(100% - 16px));top:8px;right:8px}.h18-canvas-image-tools>strong,.h18-canvas-image-actions{grid-column:auto}}
'''

# Readme and manifest.
readme = replace_once(readme, 'Version: 0.5.8', 'Version: 0.5.10', 'readme version') if 'Version: 0.5.8' in readme else replace_once(readme, 'Version: 0.5.9', 'Version: 0.5.10', 'readme version')
entry = """\n== Version 0.5.10 – Billeder og box-model i live canvas ==\n\nNyt:\n- klik på image/text_image direkte i canvas for billedkontroller; dobbeltklik åbner WordPress Media Library\n- focal point kan trækkes direkte på billedet og gemmes som X/Y-procenter\n- billedformat: Auto, 1:1, 4:3, 3:2 og 16:9\n- object-fit kan vælges som Fyld/beskær eller Vis hele billedet\n- separat billedhøjde for desktop/tablet og mobil; 0 bevarer automatisk højde\n- margin top/bund får egne drag-handles, mens eksisterende padding-handles bevares\n- valgt element viser en kompakt box-model overlay med margin- og padding-værdier\n- page-editor schema 1.11 med bagudkompatible standarder: Auto, Cover, fokus 50/50 og 0 px højde\n\n"""
marker = '== Version 0.5.9'
if marker not in readme:
    raise SystemExit('readme: v0.5.9 marker missing')
readme = readme.replace(marker, entry + marker, 1)

manifest['version'] = '0.5.10'
manifest['published_utc'] = 'BUILD_TIME_UTC'
manifest['package_sha256'] = 'BUILD_SHA256'
manifest['changelog'] = [
    'Tilføjer direkte Media Library-redigering af image/text_image fra live canvas.',
    'Tilføjer draggable focal point med X/Y-procenter.',
    'Tilføjer aspect ratio, object-fit og separat billedhøjde for desktop/tablet og mobil.',
    'Tilføjer box-model overlay samt margin top/bund drag-handles.',
    'Page-editor schema 1.11 med bagudkompatible standarder.'
]

php_path.write_text(php)
js_path.write_text(js)
css_path.write_text(css)
readme_path.write_text(readme)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

print('v0.5.10 patch applied')
