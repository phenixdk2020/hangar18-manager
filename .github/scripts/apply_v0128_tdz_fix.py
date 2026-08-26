from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
README = ROOT / 'clean/hangar18-manager/readme.txt'
NOTES = ROOT / 'clean-release-notes.html'

core = CORE.read_text(encoding='utf-8')
font_line = "    const FONT_TOKENS = ['system','arial','verdana','tahoma','trebuchet','georgia','times','courier'];\n"
anchor = "    const MIN_SPLIT_H = 8;\n"
state_line = "    let state = normalizeModel(CFG.initialModel || {});\n"

if core.count(font_line) != 1:
    raise SystemExit(f'Expected exactly one FONT_TOKENS declaration, found {core.count(font_line)}')
if core.count(anchor) != 1 or core.count(state_line) != 1:
    raise SystemExit('Expected initialization anchors not found exactly once')

core = core.replace(font_line, '', 1)
core = core.replace(anchor, anchor + font_line, 1)

if core.index(font_line) > core.index(state_line):
    raise SystemExit('FONT_TOKENS still initializes after state normalization')
CORE.write_text(core, encoding='utf-8')

plugin = PLUGIN.read_text(encoding='utf-8')
plugin = plugin.replace(' * Version: 0.1.27', ' * Version: 0.1.28', 1)
plugin = plugin.replace("define('H18_CLEAN_VERSION', '0.1.27');", "define('H18_CLEAN_VERSION', '0.1.28');", 1)
if ' * Version: 0.1.28' not in plugin or "H18_CLEAN_VERSION', '0.1.28'" not in plugin:
    raise SystemExit('Plugin version bump failed')
PLUGIN.write_text(plugin, encoding='utf-8')

readme = README.read_text(encoding='utf-8')
if 'Version: 0.1.27' in readme:
    readme = readme.replace('Version: 0.1.27', 'Version: 0.1.28', 1)
elif 'Version: 0.1.28' not in readme:
    raise SystemExit('Unexpected readme Version field')
section = """== 0.1.28 ==
* Kritisk canvas-fix: typografi-konstanten FONT_TOKENS initialiseres nu før den første canonical model-normalisering.
* Eksisterende sider med Tekst-elementer kan derfor starte editor-runtime uden JavaScript TDZ/ReferenceError.
* 0.1.27 canvas-recovery og alle 0.1.26 WYSIWYG-, typografi-, Inspector-, billed- og Knap-rettelser bevares.
* Release-QA kontrollerer eksplicit initialiseringsrækkefølgen, så denne regression ikke kan pakkes igen.

"""
if '== 0.1.28 ==' not in readme:
    marker = 'Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.\n\n'
    if marker not in readme:
        raise SystemExit('Readme insertion marker missing')
    readme = readme.replace(marker, marker + section, 1)
README.write_text(readme, encoding='utf-8')

NOTES.write_text("""<h4>0.1.28</h4><ul><li><strong>Kritisk canvas-fix:</strong> <code>FONT_TOKENS</code> initialiseres før <code>normalizeModel()</code> kaldes første gang. Sider med eksisterende Tekst-elementer stopper derfor ikke længere editor-runtime med en TDZ/ReferenceError.</li><li><strong>Data bevares:</strong> rettelsen ændrer ikke canonical layoutdata eller versionshistorik.</li><li><strong>Regression:</strong> 0.1.27 canvas-recovery samt 0.1.26 WYSIWYG, typografi, Inspector-scroll, billed-persistence og Knap-auto-size bevares.</li><li><strong>QA:</strong> releaseforløbet validerer eksplicit, at typografi-konstanter initialiseres før første modelnormalisering.</li></ul>""", encoding='utf-8')

(ROOT / 'clean-release-now.txt').write_text(
    'v0.1.28\n'
    'triggered_utc=2026-08-26T17:55:00Z\n'
    'reason=Release critical Designer startup TDZ fix for existing Text elements.\n'
    'nonce=28-tdz-fix-action\n',
    encoding='utf-8'
)

print('0.1.28 TDZ fix applied')
