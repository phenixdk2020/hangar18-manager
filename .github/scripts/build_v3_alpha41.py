from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.41'
DEST = Path('build/visual-designer-manager')

# Alpha.40 contains the corrected Elementer-panel recovery implementation.
subprocess.run(['python3', '.github/scripts/build_v3_alpha40.py'], check=True)


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.40', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.40');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.40');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.41 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

history_path = DEST / 'release-history.json'
if history_path.is_file():
    history = json.loads(history_path.read_text(encoding='utf-8'))
    rows = history.get('versions', []) if isinstance(history, dict) else []
    if isinstance(rows, list):
        rows.insert(0, {
            'version': VERSION,
            'date': '2026-10-21',
            'items': [
                'Endelig udgave af Elementer-panel recovery: fold-ud-knappen forbliver synlig på den smalle venstre rail.',
                'Elementer/Lag wrapperen bevarer den permanente panel-header som direkte barn af palette-panelet.',
                'Defensiv fallback opretter header/toggle, hvis den mangler.',
                'Alle Alpha.39-fixes bevares.'
            ],
        })
        history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

layers = read('assets/editor-v0148-layers.js')
panels = read('assets/editor-v0121-panels.js')
for token in [
    "child.matches('h2, .h18-clean-panel-head')",
    'return node !== directHead;',
]:
    if token not in layers:
        raise SystemExit(f'Alpha.41 corrected layer token missing: {token}')
for token in [
    "panel.querySelector(':scope > h2, :scope > .h18-clean-panel-head')",
    "heading = document.createElement('h2');",
]:
    if token not in panels:
        raise SystemExit(f'Alpha.41 panel fallback token missing: {token}')
if 'Version: 3.0.0-alpha.41' not in main:
    raise SystemExit('Alpha.41 version token missing')

print('Visual Designer Manager V3 3.0.0-alpha.41 palette toggle final: PASS')
