from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import zipfile


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


php_path = Path("hangar18-manager.php")
php = php_path.read_text(encoding="utf-8")
php = replace_once(php, " * Version: 0.5.7", " * Version: 0.5.8", "plugin header version")
php = replace_once(php, "    const VERSION = '0.5.7';", "    const VERSION = '0.5.8';", "plugin const version")
php_path.write_text(php, encoding="utf-8")

js_path = Path("assets/admin.js")
js = js_path.read_text(encoding="utf-8")

old_body = """    function canvasAddBodyText($target, value) {\n        const text = canvasTextFromHtml(value, 260);\n        if (text) {\n            $target.append($('<p>', { class: 'h18-canvas-preview-text', text: text }));\n        }\n    }\n"""
new_body = """    function canvasAddBodyText($target, value) {\n        const html = String(value || '').trim();\n        if (!html) {\n            return;\n        }\n        const $body = $('<div>', { class: 'h18-canvas-preview-text h18-canvas-rich-edit' });\n        $body.html(html);\n        $body.attr({\n            'data-canvas-edit-field': 'Content',\n            contenteditable: 'false',\n            spellcheck: 'true',\n            title: 'Dobbeltklik for at redigere brødtekst direkte'\n        });\n        $target.append($body);\n    }\n"""
js = replace_once(js, old_body, new_body, "rich body editor")

old_inspect = """        refreshInspectorMeta($row);\n        setInspectorPanel(currentInspectorPanel);\n        rebuildPageNavigator();\n    }\n\n    function pageSectionControls($row, selector) {\n"""
new_inspect = """        refreshInspectorMeta($row);\n        setInspectorPanel(currentInspectorPanel);\n        rebuildPageNavigator();\n        refreshAllCanvasPreviews();\n    }\n\n    function pageSectionControls($row, selector) {\n"""
js = replace_once(js, old_inspect, new_inspect, "selected canvas refresh")

toolbar_anchor = "    function ensureCanvasToolbar() {\n"
direct_controls = r'''    function canvasQuickFields() {
        if (currentCanvasDevice === 'tablet') {
            return { pad: 'TabletPaddingPx', padX: 'TabletHorizontalPaddingPx', top: 'TabletTopSpacingPx', bottom: 'TabletBottomSpacingPx' };
        }
        if (currentCanvasDevice === 'mobile') {
            return { pad: 'MobilePaddingPx', padX: 'MobileHorizontalPaddingPx', top: 'MobileTopSpacingPx', bottom: 'MobileBottomSpacingPx' };
        }
        return { pad: 'PaddingPx', padX: 'HorizontalPaddingPx', top: 'TopSpacingPx', bottom: 'BottomSpacingPx' };
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
        return $('<label>', { class: 'h18-canvas-quick-color' }).append(
            $('<span>', { text: label }),
            $('<input>', { type: 'color', value: value, 'data-canvas-color-role': role })
        );
    }

    function renderCanvasDirectControls($row, $preview, layout, colors) {
        $preview.children('.h18-canvas-direct-controls, .h18-canvas-padding-handle').remove();
        if (!$row.hasClass('is-selected')) { return; }

        const fields = canvasQuickFields();
        const hoverCustom = currentCanvasState === 'hover' && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom';
        const opacityField = hoverCustom ? 'HoverOpacityPercent' : 'SectionOpacityPercent';
        const opacityValue = hoverCustom ? canvasNumber($row, 'HoverOpacityPercent', 100) : canvasNumber($row, 'SectionOpacityPercent', 100);
        const radius = canvasNumber($row, 'RadiusPx', 7);
        const $bar = $('<div>', { class: 'h18-canvas-direct-controls', 'data-canvas-state': currentCanvasState });
        const $ranges = $('<div>', { class: 'h18-canvas-quick-ranges' }).append(
            canvasQuickRange('Indvendig', fields.pad, layout.pad, 0, 100, ' px'),
            canvasQuickRange('Vandret', fields.padX, layout.padX, 0, 100, ' px'),
            canvasQuickRange('Topafstand', fields.top, layout.top, 0, 160, ' px'),
            canvasQuickRange('Bundafstand', fields.bottom, layout.bottom, 0, 160, ' px'),
            canvasQuickRange('Radius', 'RadiusPx', radius, 0, 60, ' px'),
            canvasQuickRange('Opacity', opacityField, opacityValue, 0, 100, '%')
        );
        const $colors = $('<div>', { class: 'h18-canvas-quick-colors', 'data-canvas-color-state': currentCanvasState }).append(
            canvasQuickColor('Baggrund', 'background', colors.background),
            canvasQuickColor('Tekst', 'text', colors.text),
            canvasQuickColor('Overskrift', 'heading', colors.heading)
        );
        $bar.append($('<strong>', { class: 'h18-canvas-direct-title', text: 'Direkte design' }), $ranges, $colors);
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
    }

'''
js = replace_once(js, toolbar_anchor, direct_controls + toolbar_anchor, "direct controls functions")

old_render_tail = """        if (type === 'hero') {\n            const height = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileHeroHeightPx', 220) : canvasNumber($row, 'HeroHeightPx', 320);\n            $preview.css('minHeight', Math.max(120, height) + 'px');\n        } else {\n            $preview.css('minHeight', '0');\n        }\n    }\n\n    function refreshAllCanvasPreviews() {\n"""
new_render_tail = """        if (type === 'hero') {\n            const height = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileHeroHeightPx', 220) : canvasNumber($row, 'HeroHeightPx', 320);\n            $preview.css('minHeight', Math.max(120, height) + 'px');\n        } else {\n            $preview.css('minHeight', '0');\n        }\n        renderCanvasDirectControls($row, $preview, layout, colors);\n    }\n\n    function refreshAllCanvasPreviews() {\n"""
js = replace_once(js, old_render_tail, new_render_tail, "render direct controls")

old_inline_start = """        inspectPageSection($(this).closest('.h18-page-section-row'));\n        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');\n"""
new_inline_start = """        inspectPageSection($(this).closest('.h18-page-section-row'));\n        $(this).data('canvas-original-text', String($(this).text() || ''));\n        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');\n"""
js = replace_once(js, old_inline_start, new_inline_start, "inline original value")

old_inline_escape = """        if (event.key === 'Escape') {\n            event.preventDefault();\n            renderCanvasPreview($(this).closest('.h18-page-section-row'));\n        }\n    });\n\n    $(document).on('input change', '#h18-page-inspector-target :input', function () {\n"""
new_inline_escape = r'''        if (event.key === 'Escape') {
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

    $(document).on('click pointerdown', '.h18-canvas-direct-controls, .h18-canvas-padding-handle', function (event) {
        event.stopPropagation();
    });

    $(document).on('input', '.h18-canvas-quick-range input[type=range]', function () {
        const $input = $(this);
        const $row = $input.closest('.h18-page-section-row');
        const fieldName = String($input.data('canvas-quick-field') || '');
        const value = parseInt($input.val(), 10) || 0;
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
        if (state === 'hover') {
            canvasSetField($row, 'HoverStyleMode', 'Custom');
            canvasSetField($row, 'HoverBackgroundColor', background);
            canvasSetField($row, 'HoverTextColor', text);
            canvasSetField($row, 'HoverHeadingColor', heading);
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

    $(document).on('input change', '#h18-page-inspector-target :input', function () {
'''
js = replace_once(js, old_inline_escape, new_inline_escape, "direct edit handlers")
js_path.write_text(js, encoding="utf-8")

css_path = Path("assets/admin.css")
css = css_path.read_text(encoding="utf-8")
css += r'''

/* v0.5.8 – direkte canvas-redigering og grafiske hurtigkontroller */
.h18-page-section-row.is-selected{overflow:visible}
.h18-canvas-preview{position:relative}
.h18-canvas-rich-edit{min-height:1.4em;cursor:text}
.h18-canvas-rich-edit.is-editing,.h18-canvas-inline-edit.is-editing{outline:2px solid #3858e9;outline-offset:3px;border-radius:3px;background:rgba(255,255,255,.12)}
.h18-canvas-direct-controls{position:absolute;z-index:12;top:10px;right:10px;width:min(320px,calc(100% - 20px));padding:10px;border:1px solid #c3c4c7;border-radius:8px;background:rgba(255,255,255,.97);box-shadow:0 8px 24px rgba(0,0,0,.18);color:#1d2327;text-align:left;transform:none!important;opacity:1!important}
.h18-canvas-direct-title{display:block;margin-bottom:7px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#646970}
.h18-canvas-quick-ranges{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px 10px}
.h18-canvas-quick-range{display:grid;gap:3px;min-width:0}
.h18-canvas-quick-range-label{display:flex;justify-content:space-between;gap:6px;font-size:10px;color:#50575e}
.h18-canvas-quick-range output{font-variant-numeric:tabular-nums;color:#1d2327}
.h18-canvas-quick-range input[type=range]{width:100%;margin:0}
.h18-canvas-quick-colors{display:flex;align-items:center;gap:10px;margin-top:8px;padding-top:8px;border-top:1px solid #dcdcde}
.h18-canvas-quick-color{display:flex;align-items:center;gap:5px;font-size:10px;color:#50575e}
.h18-canvas-quick-color input[type=color]{width:30px;height:24px;padding:1px;border:1px solid #c3c4c7;border-radius:4px;background:#fff;cursor:pointer}
.h18-canvas-padding-handle{position:absolute;z-index:13;display:flex;align-items:center;justify-content:center;width:24px;height:24px;min-width:0;padding:0;border:1px solid #3858e9;border-radius:999px;background:#fff;color:#3858e9;box-shadow:0 2px 8px rgba(0,0,0,.18);cursor:grab}
.h18-canvas-padding-handle:active,.h18-canvas-preview.is-direct-dragging .h18-canvas-padding-handle{cursor:grabbing}
.h18-canvas-padding-handle .dashicons{width:14px;height:14px;font-size:14px;line-height:14px}
.h18-canvas-padding-handle.is-top{top:4px;left:50%;transform:translateX(-50%) rotate(90deg)}
.h18-canvas-padding-handle.is-bottom{bottom:4px;left:50%;transform:translateX(-50%) rotate(90deg)}
.h18-canvas-padding-handle.is-left{left:4px;top:50%;transform:translateY(-50%)}
.h18-canvas-padding-handle.is-right{right:4px;top:50%;transform:translateY(-50%)}
.h18-canvas-preview.is-direct-dragging{outline:2px dashed #3858e9;outline-offset:3px}
@media(max-width:782px){
  .h18-canvas-direct-controls{position:relative;top:auto;right:auto;width:auto;margin:12px 0 0}
  .h18-canvas-quick-ranges{grid-template-columns:1fr}
}
'''
css_path.write_text(css, encoding="utf-8")

readme_path = Path("readme.txt")
readme = readme_path.read_text(encoding="utf-8")
readme = replace_once(readme, "Version: 0.5.7", "Version: 0.5.8", "readme version")
marker = "Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.\n\n"
section = """== Version 0.5.8 – Direkte canvas-kontroller ==\n\nNyt:\n- brødtekst kan redigeres direkte som rich text i canvas med dobbeltklik\n- Escape annullerer inline-redigering af overskrift/knaptekst\n- valgt element får hurtigkontroller for padding, vandret padding, top/bundafstand, radius og opacity\n- baggrund, tekst og overskriftsfarve kan vælges direkte fra canvas\n- fire drag-handles ændrer indvendig lodret/vandret luft direkte på elementet\n- kontrollerne følger Desktop/Tablet/Mobil og Normal/Hover\n- page-editor schema forbliver 1.10; ingen eksisterende sidedata migreres\n\n\n"""
readme = replace_once(readme, marker, marker + section, "readme changelog insertion")
readme_path.write_text(readme, encoding="utf-8")

package = Path("dist/hangar18-manager.zip")
tmp = Path("/tmp/hangar18-manager-v058")
if tmp.exists():
    shutil.rmtree(tmp)
root = tmp / "hangar18-manager"
(root / "assets").mkdir(parents=True)
shutil.copy2("hangar18-manager.php", root / "hangar18-manager.php")
shutil.copy2("readme.txt", root / "readme.txt")
shutil.copy2("assets/admin.js", root / "assets/admin.js")
shutil.copy2("assets/admin.css", root / "assets/admin.css")
with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for p in sorted(root.rglob("*")):
        if p.is_file():
            zf.write(p, p.relative_to(tmp))

digest = hashlib.sha256(package.read_bytes()).hexdigest()
manifest = {
    "schema_version": "1.0",
    "plugin": "hangar18-manager",
    "version": "0.5.8",
    "min_wp": "6.4",
    "min_php": "8.0",
    "published_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "package_path": "dist/hangar18-manager.zip",
    "package_sha256": digest,
    "changelog": [
        "Tilføjer direkte rich-text redigering af brødtekst i live canvas.",
        "Tilføjer grafiske hurtigkontroller for padding, spacing, radius og opacity.",
        "Tilføjer direkte farvevalg for baggrund, tekst og overskrift.",
        "Tilføjer fire drag-handles til indvendig luft på det valgte element.",
        "Kontroller følger Desktop/Tablet/Mobil og Normal/Hover.",
        "Page-editor schema forbliver 1.10 og eksisterende sidedata migreres ikke."
    ]
}
Path("update.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("package_sha256=" + digest)
