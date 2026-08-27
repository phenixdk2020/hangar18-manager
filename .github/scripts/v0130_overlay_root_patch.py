from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly 1 match, got {count}: {old[:100]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

core = 'clean/hangar18-manager/assets/editor-v018-core.js'
renderer = 'clean/hangar18-manager/src/Frontend/Renderer.php'
richcss = 'clean/hangar18-manager/assets/editor-v0125.css'

replace_once(
    core,
    "function isFloatingButton(node) { return !!(node && node.type === 'button' && node.parentId && node.props && node.props.placementMode === 'overlay'); }",
    "function isFloatingButton(node) { return !!(node && node.type === 'button' && node.props && node.props.placementMode === 'overlay'); }",
)
replace_once(
    core,
    "else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' && current.parentId ? 'overlay' : 'normal'; }",
    "else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' ? 'overlay' : 'normal'; }",
)
replace_once(
    core,
    '>Flydende i Sektion/Kasse</option>',
    '>Flydende i område</option>',
)
replace_once(
    core,
    'Højere lag ligger foran andre elementer. Flyt knappen med ✥ eller X/Y.',
    'Højere lag ligger foran andre elementer. Knappen flyder frit i sin aktuelle Side/Sektion/Kasse og flyttes med ✥ eller X/Y.',
)

replace_once(
    renderer,
    "$floating = $placementMode === 'overlay' && (string) ($node['parentId'] ?? '') !== '';",
    "$floating = $placementMode === 'overlay';",
)
replace_once(
    renderer,
    "echo '.h18-clean-page,.h18-clean-front-surface{display:grid;",
    "echo '.h18-clean-page,.h18-clean-front-surface{display:grid;position:relative;",
)

replace_once(
    richcss,
    '.h18-vd-rich-shell{display:block;margin-top:4px}',
    '.h18-vd-rich-shell{display:block;margin-top:4px;font-weight:400}',
)
replace_once(
    richcss,
    'background:#fff;color:#1d2327;line-height:1.45;',
    'background:#fff;color:#1d2327;font-weight:400;line-height:1.45;',
)

print('0.1.30 overlay-root + rich-text inheritance patch applied')
