from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, zipfile


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


path = Path('assets/admin.js')
js = path.read_text(encoding='utf-8')

old = """    function canvasQuickColor(label, role, value) {\n        return $('<label>', { class: 'h18-canvas-quick-color' }).append(\n            $('<span>', { text: label }),\n            $('<input>', { type: 'color', value: value, 'data-canvas-color-role': role })\n        );\n    }\n"""
new = """    function canvasQuickColor(label, role, value) {\n        const raw = String(value || '');\n        const normalized = /^#[0-9a-fA-F]{6}$/.test(raw) ? raw : '#ffffff';\n        return $('<label>', { class: 'h18-canvas-quick-color' }).append(\n            $('<span>', { text: label }),\n            $('<input>', { type: 'color', value: normalized, 'data-canvas-color-role': role })\n        );\n    }\n"""
js = replace_once(js, old, new, 'color input normalization')

old = """        const hoverCustom = currentCanvasState === 'hover' && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom';\n        const opacityField = hoverCustom ? 'HoverOpacityPercent' : 'SectionOpacityPercent';\n        const opacityValue = hoverCustom ? canvasNumber($row, 'HoverOpacityPercent', 100) : canvasNumber($row, 'SectionOpacityPercent', 100);\n"""
new = """        const hoverState = currentCanvasState === 'hover';\n        const hoverCustom = hoverState && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom';\n        const opacityField = hoverState ? 'HoverOpacityPercent' : 'SectionOpacityPercent';\n        const opacityValue = hoverCustom ? canvasNumber($row, 'HoverOpacityPercent', 100) : Math.round(colors.opacity * 100);\n"""
js = replace_once(js, old, new, 'hover opacity target')

old = """        const $colors = $('<div>', { class: 'h18-canvas-quick-colors', 'data-canvas-color-state': currentCanvasState }).append(\n"""
new = """        const $colors = $('<div>', {\n            class: 'h18-canvas-quick-colors',\n            'data-canvas-color-state': currentCanvasState,\n            'data-canvas-border': colors.border,\n            'data-canvas-opacity': Math.round(colors.opacity * 100)\n        }).append(\n"""
js = replace_once(js, old, new, 'color state seed data')

old = """        const fieldName = String($input.data('canvas-quick-field') || '');\n        const value = parseInt($input.val(), 10) || 0;\n        canvasSetField($row, fieldName, value);\n"""
new = """        const fieldName = String($input.data('canvas-quick-field') || '');\n        const value = parseInt($input.val(), 10) || 0;\n        if (fieldName === 'HoverOpacityPercent' && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) !== 'Custom') {\n            const $group = $input.closest('.h18-canvas-direct-controls').find('.h18-canvas-quick-colors');\n            canvasSetField($row, 'HoverStyleMode', 'Custom');\n            canvasSetField($row, 'HoverBackgroundColor', String($group.find('[data-canvas-color-role=\"background\"]').val() || '#ffffff'));\n            canvasSetField($row, 'HoverTextColor', String($group.find('[data-canvas-color-role=\"text\"]').val() || '#30382a'));\n            canvasSetField($row, 'HoverHeadingColor', String($group.find('[data-canvas-color-role=\"heading\"]').val() || '#30382a'));\n            canvasSetField($row, 'HoverBorderColor', String($group.attr('data-canvas-border') || '#c3ae83'));\n            refreshHoverStyleMode($row);\n        }\n        canvasSetField($row, fieldName, value);\n"""
js = replace_once(js, old, new, 'hover opacity state initialization')

old = """        const heading = String($group.find('[data-canvas-color-role=\"heading\"]').val() || text);\n        if (state === 'hover') {\n            canvasSetField($row, 'HoverStyleMode', 'Custom');\n            canvasSetField($row, 'HoverBackgroundColor', background);\n            canvasSetField($row, 'HoverTextColor', text);\n            canvasSetField($row, 'HoverHeadingColor', heading);\n            refreshHoverStyleMode($row);\n"""
new = """        const heading = String($group.find('[data-canvas-color-role=\"heading\"]').val() || text);\n        const seedBorder = String($group.attr('data-canvas-border') || '#c3ae83');\n        const seedOpacity = parseInt($group.attr('data-canvas-opacity'), 10);\n        if (state === 'hover') {\n            const wasCustom = String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom';\n            canvasSetField($row, 'HoverStyleMode', 'Custom');\n            canvasSetField($row, 'HoverBackgroundColor', background);\n            canvasSetField($row, 'HoverTextColor', text);\n            canvasSetField($row, 'HoverHeadingColor', heading);\n            if (!wasCustom) {\n                canvasSetField($row, 'HoverBorderColor', seedBorder);\n                canvasSetField($row, 'HoverOpacityPercent', Number.isFinite(seedOpacity) ? seedOpacity : 100);\n            }\n            refreshHoverStyleMode($row);\n"""
js = replace_once(js, old, new, 'hover color state initialization')
path.write_text(js, encoding='utf-8')

# Rebuild the exact plugin package after QA fix.
package = Path('dist/hangar18-manager.zip')
tmp = Path('/tmp/hangar18-manager-v058-qa')
if tmp.exists(): shutil.rmtree(tmp)
root = tmp / 'hangar18-manager'
(root / 'assets').mkdir(parents=True)
for src, dst in [
    ('hangar18-manager.php', root / 'hangar18-manager.php'),
    ('readme.txt', root / 'readme.txt'),
    ('assets/admin.js', root / 'assets/admin.js'),
    ('assets/admin.css', root / 'assets/admin.css'),
]:
    shutil.copy2(src, dst)
with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for p in sorted(root.rglob('*')):
        if p.is_file(): zf.write(p, p.relative_to(tmp))

digest = hashlib.sha256(package.read_bytes()).hexdigest()
manifest_path = Path('update.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['published_utc'] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
manifest['package_sha256'] = digest
manifest['changelog'].append('Hover-direktekontroller seedes nu fra Normal-design, så Hover-ændringer ikke påvirker Normal eller nulstiller kant/opacity.')
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('package_sha256=' + digest)
