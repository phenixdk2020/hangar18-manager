from pathlib import Path

VERSION = '0.1.27'


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly 1 occurrence, found {count}: {old!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    print(f'patched {path}')

replace_once('clean/hangar18-manager/hangar18-manager.php', ' * Version: 0.1.26', f' * Version: {VERSION}')
replace_once('clean/hangar18-manager/hangar18-manager.php', "define('H18_CLEAN_VERSION', '0.1.26');", f"define('H18_CLEAN_VERSION', '{VERSION}');")

readme = Path('clean/hangar18-manager/readme.txt')
text = readme.read_text(encoding='utf-8')
if 'Version: 0.1.26' in text:
    text = text.replace('Version: 0.1.26', f'Version: {VERSION}', 1)
elif f'Version: {VERSION}' not in text:
    raise SystemExit('readme.txt: unexpected Version field')
section = """== 0.1.27 ==
* Canvas-recovery: en runtime-fejl i ét barn-element må ikke længere blanke hele Sektion/Kasse eller hele Designer-canvas.
* Rich-text sanitizer bruger en mere browser-/Firefox-robust unwrap-metode.
* Konkrete render-fejl vises på det berørte element eller root-canvas, mens canonical layoutdata bevares.
* Drag/drop og øvrige elementer kan fortsætte, selv hvis ét element ikke kan renderes.
* Alle 0.1.26 WYSIWYG-, typografi-, Inspector-, billed-persistence- og Knap-auto-size rettelser er bevaret.

"""
if '== 0.1.27 ==' not in text:
    marker = 'Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.\n\n'
    if marker not in text:
        raise SystemExit('readme.txt: insertion marker missing')
    text = text.replace(marker, marker + section, 1)
readme.write_text(text, encoding='utf-8')

notes = """<h4>0.1.27</h4><ul><li><strong>Canvas-recovery:</strong> en renderfejl i ét element kan ikke længere få hele den overordnede Sektion/Kasse eller hele Designer-canvas til at forsvinde.</li><li><strong>Browser-hardening:</strong> rich-text sanitizer bruger en mere Firefox-/browser-robust node-unwrapping.</li><li><strong>Synlig fejlhåndtering:</strong> hvis et konkret element stadig ikke kan renderes, vises en fejl-placeholder på det element, mens canonical layoutdata bevares.</li><li><strong>Redigering bevares:</strong> resten af canvas og drag/drop forbliver tilgængeligt, selv ved en lokal renderfejl.</li><li><strong>Regression:</strong> alle 0.1.26 WYSIWYG-, typografi-, Inspector-scroll-, billed-persistence- og Knap-auto-size rettelser er bevaret.</li></ul>"""
Path('clean-release-notes.html').write_text(notes, encoding='utf-8')

Path('clean-release-now.txt').write_text(
    'v0.1.27\n'
    'triggered_utc=2026-08-26T17:44:00Z\n'
    'reason=Release canvas recovery hotfix after blank Designer regression in 0.1.26.\n'
    'nonce=27-canvas-recovery\n',
    encoding='utf-8',
)
print('0.1.27 release preparation complete')
