from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.40'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha39.py'], check=True)


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.39', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.39');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.39');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.40 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Elementer collapse recovery.
#
# editor-v0121-panels.js upgrades the direct palette <h2> into the permanent
# panel header/toggle. editor-v0148-layers.js later wrapped ALL palette children
# into the "Elementer" tab, including that header. Once collapsed, CSS hides the
# tab panel and therefore also hides the only reopen button.
#
# Keep the direct h2 / enhanced panel head outside the Elementer/Lag tab panels.
# This works regardless of whether v0121 or v0148 initializes first.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0148-layers.js',
    """        const existing = Array.prototype.slice.call(palette.childNodes);
        const tabs = document.createElement('div');
""",
    """        // Keep the permanent Elementer panel heading/toggle as a direct child.
        // The collapse CSS intentionally leaves .h18-clean-panel-head visible, while
        // all tab content is hidden. Moving the heading into a tab made the palette
        // impossible to reopen after it had been collapsed.
        const directHead = Array.prototype.slice.call(palette.children).find(function (child) {
            return child.matches && child.matches('h2, .h18-clean-panel-head');
        }) || null;
        const existing = Array.prototype.slice.call(palette.childNodes).filter(function (node) {
            return node !== directHead;
        });
        const tabs = document.createElement('div');
""",
    'Alpha.40 preserve direct palette heading'
)

replace_once(
    'assets/editor-v0148-layers.js',
    """        palette.appendChild(tabs);
        palette.appendChild(elements);
        palette.appendChild(layers);
""",
    """        // directHead is deliberately left in place. Append only tab controls/content.
        palette.appendChild(tabs);
        palette.appendChild(elements);
        palette.appendChild(layers);
""",
    'Alpha.40 document direct palette heading placement'
)

# Defensive fallback: if another extension has already moved/removed the heading,
# panels.js must still create an always-visible rail toggle instead of silently
# leaving the user trapped in collapsed mode.
replace_once(
    'assets/editor-v0121-panels.js',
    """    function enhancePanel(panel, side) {
        if (!panel) { return; }
        var heading = panel.querySelector(':scope > h2');
        if (!heading || heading.dataset.h18Collapsible === '1') { return; }
""",
    """    function enhancePanel(panel, side) {
        if (!panel) { return; }
        var heading = panel.querySelector(':scope > h2, :scope > .h18-clean-panel-head');
        if (!heading) {
            heading = document.createElement('h2');
            heading.textContent = titleFor(side);
            panel.insertBefore(heading, panel.firstChild || null);
        }
        if (heading.dataset.h18Collapsible === '1') { return; }
""",
    'Alpha.40 panels fallback heading'
)

# Release history when available.
history_path = DEST / 'release-history.json'
if history_path.is_file():
    history = json.loads(history_path.read_text(encoding='utf-8'))
    rows = history.get('versions', []) if isinstance(history, dict) else []
    if isinstance(rows, list):
        rows.insert(0, {
            'version': VERSION,
            'date': '2026-10-21',
            'items': [
                'Elementer-panelets fold-ud-knap forbliver nu synlig, når panelet er sammenklappet.',
                'Lag-funktionen pakker ikke længere den permanente Elementer-header/toggle ind i et skjult tabpanel.',
                'Panelkoden opretter defensivt en direkte header/toggle, hvis en anden editorudvidelse har flyttet eller fjernet den.',
                'Alpha.39 tekst-, menu-, import- og PHP-fixes bevares uændret.'
            ],
        })
        history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic QA tokens.
main = read('visual-designer-manager.php')
layers = read('assets/editor-v0148-layers.js')
panels = read('assets/editor-v0121-panels.js')
for token in [
    'Version: 3.0.0-alpha.40',
    "define('VDM_VERSION', '3.0.0-alpha.40');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.40');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.40 main token missing: {token}')
for token in [
    'const directHead = Array.prototype.slice.call(palette.children).find',
    'return node !== directHead;',
    'directHead is deliberately left in place',
]:
    if token not in layers:
        raise SystemExit(f'Alpha.40 layers token missing: {token}')
for token in [
    "panel.querySelector(':scope > h2, :scope > .h18-clean-panel-head')",
    "heading = document.createElement('h2');",
    "panel.insertBefore(heading, panel.firstChild || null);",
]:
    if token not in panels:
        raise SystemExit(f'Alpha.40 panels token missing: {token}')

print('Visual Designer Manager V3 3.0.0-alpha.40 palette toggle recovery: PASS')
