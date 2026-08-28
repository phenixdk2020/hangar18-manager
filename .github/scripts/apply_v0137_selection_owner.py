from pathlib import Path
import json
import re

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(path, old, new):
    text = read(path)
    if old not in text:
        raise SystemExit(f'Missing expected text in {path}: {old[:140]!r}')
    write(path, text.replace(old, new, 1))


# Version
replace_once('clean/hangar18-manager/hangar18-manager.php', 'Version: 0.1.36', 'Version: 0.1.37')
replace_once("clean/hangar18-manager/hangar18-manager.php", "define('H18_CLEAN_VERSION', '0.1.36');", "define('H18_CLEAN_VERSION', '0.1.37');")

# ---------------------------------------------------------------------------
# VD-TEXT-SEL-001 root cause: legacy handlers were accidentally re-enabled.
# v0131/v0132 must delegate whenever v0125 declares any authoritative owner;
# the delegation contract must never depend on a release-version string.
# ---------------------------------------------------------------------------
v0125 = 'clean/hangar18-manager/assets/editor-v0125.js'
replace_once(v0125, "selectionOwner: 'v0135',", "selectionOwner: 'v0125-authoritative',")
replace_once(v0125, "selectionMode: 'boundary-markers-v0136',", "selectionMode: 'boundary-markers-v0137-single-owner',")

v0131 = 'clean/hangar18-manager/assets/editor-v0131.js'
text = read(v0131)
old = "if (window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner === 'v0134') { return; }"
count = text.count(old)
if count != 2:
    raise SystemExit(f'Expected exactly 2 version-bound v0131 owner guards, found {count}')
text = text.replace(old, "if (window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner) { return; }")
write(v0131, text)

v0132 = 'clean/hangar18-manager/assets/editor-v0132.js'
replace_once(
    v0132,
    "return !!(window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner === 'v0134');",
    "return !!(window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner);"
)

# Permanent release-gate so a future owner label/version cannot reactivate legacy loops.
workflow = '.github/workflows/visual-designer-release.yml'
text = read(workflow)
anchor = "          grep -q \"boundary-markers-v0136\" clean/hangar18-manager/assets/editor-v0125.js\n"
if anchor not in text:
    # 0.1.37 may be rerun after this file was already partly updated.
    anchor = "          grep -q \"boundary-markers-v0137-single-owner\" clean/hangar18-manager/assets/editor-v0125.js\n"
    if anchor not in text:
        raise SystemExit('Release workflow rich-selection anchor missing')
    replacement = anchor
else:
    replacement = "          grep -q \"boundary-markers-v0137-single-owner\" clean/hangar18-manager/assets/editor-v0125.js\n"
replacement += "          grep -q \"selectionOwner: 'v0125-authoritative'\" clean/hangar18-manager/assets/editor-v0125.js\n"
replacement += "          grep -q \"window.H18RichTextV0125.selectionOwner) { return; }\" clean/hangar18-manager/assets/editor-v0131.js\n"
replacement += "          grep -q \"window.H18RichTextV0125.selectionOwner);\" clean/hangar18-manager/assets/editor-v0132.js\n"
replacement += "          if grep -n -E \"selectionOwner[[:space:]]*===?[[:space:]]*['\\\"]v[0-9]+\" clean/hangar18-manager/assets/editor-v0131.js clean/hangar18-manager/assets/editor-v0132.js; then\n"
replacement += "            echo 'Legacy rich-text owner guard is tied to a release version.' >&2\n"
replacement += "            exit 1\n"
replacement += "          fi\n"
text = text.replace(anchor, replacement, 1)
write(workflow, text)

# Release history
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
if not any(str(row.get('version')) == '0.1.37' for row in history if isinstance(row, dict)):
    history.insert(0, {
        'version': '0.1.37',
        'date': '2026-08-28',
        'items': [
            'BUG-02 root cause rettet: v0131/v0132 selection-restore loops blev ved en versionsstrengsændring utilsigtet aktiveret igen.',
            'v0125 er nu permanent autoritativ rich-text selection-ejer; legacy handlers delegerer ved enhver gyldig owner-værdi.',
            'Owner-kontrakten er ikke længere bundet til et bestemt release-nummer og har en release-gate mod regression.',
            '0.1.36 boundary-marker formatteringsmotoren bevares og får nu lov at køre uden konkurrerende restore-handlers.',
            'Ingen ændringer til Billede-adfærd i denne release.'
        ]
    })
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

# Technical manual
tech_path = 'CLEAN-TECHNICAL-MANUAL.md'
tech = read(tech_path)
tech = tech.replace('## 21. Kontraktstatus for 0.1.36', '## 21. Kontraktstatus for 0.1.37', 1)
old_para = "**BUGFIX i 0.1.36 – afventer bruger-QA.** Bruger-QA af 0.1.35 viste fortsat, at Understregning bevarer selection, mens Fed/Kursiv kan miste den. 0.1.36 gør derfor selection uafhængig af Firefox' genopbygning af `STRONG`/`EM`: to vedvarende, tomme editor-boundary-markører placeres omkring den valgte tekst ved toolbar-pointerdown. Fed, Kursiv og Understregning formatterer mellem de samme markører, og Range rekonstrueres fra markørerne efter hver kommando. Logiske tekst-offsets er kun fallback."
new_para = "**BUGFIX i 0.1.37 – afventer bruger-QA.** Bruger-QA af 0.1.36 viste fortsat tab af selection ved Fed/Kursiv. Den konkrete regressionsårsag er identificeret: `v0131` og `v0132` deaktiverede kun deres gamle restore-loops, når `v0125.selectionOwner === 'v0134'`. Da den aktive owner-label senere blev ændret, blev legacy-loopene utilsigtet aktiveret igen og konkurrerede med den autoritative formatteringsmotor. I 0.1.37 er `v0125` permanent autoritativ ejer, og legacy-lag delegerer ved enhver truthy `selectionOwner`; kontrakten er dermed ikke versionsbundet. Boundary-marker motoren fra 0.1.36 bevares uændret som den eneste aktive selection-motor."
if old_para not in tech:
    raise SystemExit('Technical manual 0.1.36 rich-text paragraph missing')
tech = tech.replace(old_para, new_para, 1)
needle = "Godkendelsestest: 20/20 gentagelser for Fed, Kursiv og Understregning samt kæderne Fed → Kursiv → Understregning og Kursiv → Fed → Understregning uden ny markering."
rule = needle + "\n\n**FAST owner-regel:** Legacy rich-text-filer må aldrig afgøre delegation ud fra et konkret release-nummer. Hvis `H18RichTextV0125.selectionOwner` er sat, er v0125 den eneste selection-ejer, og ældre capture/restore-loops skal returnere uden handling."
if needle not in tech:
    raise SystemExit('Technical manual rich-text QA anchor missing')
tech = tech.replace(needle, rule, 1)
write(tech_path, tech)

# Status + release notes
write('docs/v0137-status.md', """# Visual Designer Manager 0.1.37 – status

Dato: 28. august 2026

## Scope
- VD-TEXT-SEL-001 / BUG-02 only.
- Ingen Billede-rettelse i denne release; billedobservationen er fortsat ikke erklæret som bug.

## Root cause
0.1.34 gjorde `editor-v0125.js` til eneste selection-ejer, men delegation i `editor-v0131.js` og `editor-v0132.js` var fejlagtigt hardcoded til owner-strengen `v0134`. Da owner-label senere blev `v0135`, blev de gamle selection restore-loops aktive igen og kunne overskrive Range efter toolbar-kommandoen.

## Fix
- `editor-v0125.js`: `selectionOwner = v0125-authoritative`.
- `editor-v0131.js`: gamle handlers returnerer ved enhver truthy v0125 owner.
- `editor-v0132.js`: samme permanente delegation.
- 0.1.36 boundary-marker formatteringsmotor beholdes som eneste aktive selection-motor.
- Release-QA fejler, hvis legacy owner guards igen bindes til et versionsnummer.

## QA
PHP/JS syntax, hierarchy/model regression og source-contract gates køres før release. Endelig Firefox interaction-QA udføres af bruger.
""")

write('clean-release-notes.html', """<h4>0.1.37</h4><ul><li><strong>BUG-02 root cause:</strong> gamle rich-text restore-loops blev utilsigtet genaktiveret, fordi deres delegation var hardcoded til owner-navnet v0134.</li><li><strong>Single owner:</strong> v0125 er nu permanent autoritativ selection-ejer; v0131/v0132 delegerer uanset versionslabel.</li><li><strong>Regression gate:</strong> release-QA afviser fremover versionsbundne selection-owner guards.</li><li><strong>Formattering:</strong> boundary-marker motoren fra 0.1.36 kører nu uden konkurrerende selection-handlers.</li><li><strong>Scope:</strong> ingen ændring til Billede-adfærd i denne release.</li></ul>""")

print('0.1.37 selection-owner patch applied')
