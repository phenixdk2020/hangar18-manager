from pathlib import Path
import json

# Version and asset enqueue.
p = Path('clean/hangar18-manager/hangar18-manager.php')
s = p.read_text(encoding='utf-8')
s = s.replace(' * Version: 0.1.34', ' * Version: 0.1.35', 1)
s = s.replace("define('H18_CLEAN_VERSION', '0.1.34');", "define('H18_CLEAN_VERSION', '0.1.35');", 1)
style_marker = """    wp_enqueue_style(\n        'h18-clean-editor-v0134',\n        H18_CLEAN_URL . 'assets/editor-v0134.css',\n        ['h18-clean-editor-v0132'],\n        H18_CLEAN_VERSION\n    );\n"""
if "'h18-clean-editor-v0135'" not in s:
    s = s.replace(style_marker, style_marker + """    wp_enqueue_style(\n        'h18-clean-editor-v0135',\n        H18_CLEAN_URL . 'assets/editor-v0135.css',\n        ['h18-clean-editor-v0134'],\n        H18_CLEAN_VERSION\n    );\n""", 1)
script_marker = """    wp_enqueue_script(\n        'h18-clean-editor-v0132',\n        H18_CLEAN_URL . 'assets/editor-v0132.js',\n        ['h18-clean-editor-v0131'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"""
if "assets/editor-v0135.js" not in s:
    s = s.replace(script_marker, script_marker + """    wp_enqueue_script(\n        'h18-clean-editor-v0135',\n        H18_CLEAN_URL . 'assets/editor-v0135.js',\n        ['h18-clean-editor-v0132'],\n        H18_CLEAN_VERSION,\n        true\n    );\n""", 1)
p.write_text(s, encoding='utf-8')

# Release history.
p = Path('clean/hangar18-manager/release-history.json')
data = json.loads(p.read_text(encoding='utf-8'))
data = [x for x in data if x.get('version') != '0.1.35']
data.insert(0, {
    'version': '0.1.35', 'date': '2026-08-28', 'items': [
        'Fed, Kursiv og Understregning bruger deterministisk DOM-formatteringsmotor i stedet for browser execCommand for de tre inline-formater.',
        'Rich-text selection rekonstrueres fra logiske tekst-offsets efter formattering, og toolbar pointerdown forhindrer fokus-tab.',
        'Native Windows/browser type=color-dialog er erstattet af Visual Designers egen Inspector-farvevælger.',
        'Farvevælgeren har saturation/brightness-felt, hue-slider, HEX, preview og farvechips; canonical værdi forbliver #RRGGBB.',
        'Floating top-layer og Inspector-scroll er bevaret uændret.'
    ]
})
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Readme.
p = Path('clean/hangar18-manager/readme.txt')
s = p.read_text(encoding='utf-8').replace('Version: 0.1.34', 'Version: 0.1.35', 1)
if '== 0.1.35 ==' not in s:
    s = s.replace('== 0.1.34 ==\n', '''== 0.1.35 ==
* Fed, Kursiv og Understregning bruger deterministisk DOM-formatteringsmotor og bruger ikke længere browser execCommand for de tre inline-formater.
* Selection rekonstrueres fra logiske tekst-offsets, og toolbar pointerdown flytter ikke fokus før formattering.
* Native type=color/Windows-farvedialog er erstattet af Visual Designers egen farvevælger med saturation/brightness, hue, HEX, preview og farvechips.
* Farver gemmes fortsat canonical som #RRGGBB uden modelmigration.
* Floating top-layer og Inspector-scroll er bevaret uændret.

== 0.1.34 ==
''', 1)
p.write_text(s, encoding='utf-8')

Path('clean-release-notes.html').write_text('<h4>0.1.35</h4><ul><li><strong>Rich text:</strong> Fed, Kursiv og Understregning bruger deterministisk DOM-formatteringsmotor.</li><li><strong>Selection:</strong> logiske tekst-offsets rekonstruerer samme markering efter formattering.</li><li><strong>Farvevælger:</strong> native Windows/browser-dialog er erstattet af Visual Designers egen HSV/HEX-vælger.</li><li><strong>Farvemodel:</strong> canonical værdi er fortsat #RRGGBB.</li><li><strong>Regression:</strong> Floating top-layer og Inspector-scroll er bevaret.</li></ul>', encoding='utf-8')

# User manual.
p = Path('CLEAN-USER-MANUAL.md')
s = p.read_text(encoding='utf-8')
s = s.replace('Gælder for: Visual Designer Manager 0.1.34 og nyere;', 'Gælder for: Visual Designer Manager 0.1.35 og nyere;', 1)
heading = '## 8. Farverne i Designer\n\n'
if '### Farvevælger i Inspector' not in s:
    s = s.replace(heading, heading + '''### Farvevælger i Inspector

Fra **0.1.35** bruger Visual Designer sin egen farvevælger i stedet for Windows/browserens native farvedialog. Du kan vælge farve i saturation/brightness-feltet, flytte Hue-slideren, skrive en præcis HEX-værdi eller bruge en farvechip. Klik **Anvend** for at gemme valget eller **Annuller** for at beholde den tidligere farve. Canonical farve gemmes fortsat som `#RRGGBB`.

### Statusfarver i editoren

''', 1)
p.write_text(s, encoding='utf-8')

# Technical manual status.
p = Path('CLEAN-TECHNICAL-MANUAL.md')
s = p.read_text(encoding='utf-8')
s = s.replace('## 21. Kontraktstatus for 0.1.34', '## 21. Kontraktstatus for 0.1.35', 1)
old = '''### VD-TEXT-SEL-001 – Rich-text selection

**BUGFIX i 0.1.34 – afventer bruger-QA.** Bruger-QA af 0.1.33 viste Understregning stabil, Fed ustabil og Kursiv fortsat fejlbehæftet. Årsagen var tre samtidige selection-restore-lag (`v0125`, `v0131`, `v0132`). I 0.1.34 er `v0125` eneste autoritative selection-ejer; de to ældre restore-loops delegerer/returnerer. Selection fanges ved pointerdown som logiske tekst-offsets og bruges af én atomisk command-transaction for Fed, Kursiv og Understregning.

Godkendelsestest: mindst gentagne markeringer med Fed, Kursiv og Understregning samt kæden Fed → Kursiv → Understregning uden ny markering.
'''
new = '''### VD-TEXT-SEL-001 – Rich-text selection

**BUGFIX i 0.1.35 – afventer bruger-QA.** 0.1.34 løste ikke Fed/Kursiv stabilt. I 0.1.35 bruger Fed, Kursiv og Understregning ikke længere browserens `execCommand()` til selve inline-formatet. De tre udføres som deterministiske DOM-transaktioner, og selection rekonstrueres fra logiske tekst-offsets.

Godkendelsestest: 20/20 gentagelser for Fed, Kursiv og Understregning samt kæderne Fed → Kursiv → Understregning og Kursiv → Fed → Understregning uden ny markering.
'''
if old in s: s = s.replace(old, new, 1)
marker = '### VD-INSPECTOR-SCROLL-001 – Inspector bund-buffer\n'
if '### VD-COLOR-001 – Inspector farvevælger' not in s:
    s = s.replace(marker, '''### VD-COLOR-001 – Inspector farvevælger

**IMPLEMENTERET i 0.1.35 – afventer bruger-QA.** Inspector bruger sin egen farvevælger og må ikke afhænge af operativsystemets native `type=color`-dialog. UI har saturation/brightness-felt, hue-slider, HEX-input, preview og farvechips. Canonical værdi er fortsat `#RRGGBB`.

Godkendelsestest: vælg en tydelig grøn farve, klik **Anvend**, og verificér samme HEX i Inspector, canvas og efter Save/Reload uden at tidligere sort/lav luminans hænger ved.

''' + marker, 1)
s = s.replace('uændret i 0.1.34.', 'uændret i 0.1.35.', 1)
p.write_text(s, encoding='utf-8')

Path('docs/v0135-status.md').write_text('''# Visual Designer Manager 0.1.35 – status

Dato: 28. august 2026

## Scope
- VD-TEXT-SEL-001: deterministisk Fed/Kursiv/Understregning med bevaret selection.
- VD-COLOR-001: egen Inspector-farvevælger uden native Windows/browser-dialog.

## QA
PHP/JS syntax, hierarchy/model regression og source-contract checks køres før release. Endelig Firefox interaction-QA udføres af bruger efter release.
''', encoding='utf-8')

print('0.1.35 metadata applied')
