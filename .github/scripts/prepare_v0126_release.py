from pathlib import Path

VERSION = '0.1.26'


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly 1 occurrence, found {count}: {old!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    print(f'patched {path}')


# Plugin runtime version.
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    ' * Version: 0.1.25',
    f' * Version: {VERSION}',
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "define('H18_CLEAN_VERSION', '0.1.25');",
    f"define('H18_CLEAN_VERSION', '{VERSION}');",
)

# WordPress readme version + concise release section.
readme = Path('clean/hangar18-manager/readme.txt')
text = readme.read_text(encoding='utf-8')
if 'Version: 0.1.23' in text:
    text = text.replace('Version: 0.1.23', f'Version: {VERSION}', 1)
elif f'Version: {VERSION}' not in text:
    raise SystemExit('readme.txt: unexpected Version field')

section = """== 0.1.26 ==
* WYSIWYG-hardening: editor-label/type/ID er ren editor-chrome og påvirker ikke længere elementets canonical geometri.
* Tekstlinjeskift og blanke linjer bevares ens i Designer, Forhåndsvisning og frontend.
* Rich-text selection bevares ved Fed/Kursiv/Understregning m.v., så markeringen ikke forsvinder under toolbar-opdatering.
* Brødtekst og overskrift har separate typografiindstillinger: skrifttype, størrelse, tykkelse, linjeafstand og bogstavafstand; overskrift kan arve brødtekstens skrifttype.
* Manuel billedstørrelse og -placering gemmes canonical med fit=manual samt X/Y/bredde/højde og overlever Gem + reload + frontend-rendering.
* Inspector har egen lodret scroll på desktop/laptop og bevarer scroll/fokus bedre ved re-render.
* Knap har Automatisk størrelse som standard, så tekst og Padding X/Y bestemmer minimumsstørrelsen; manuel resize kan fortsat bruges.
* Generiske synlige Clean-save-noter er fjernet fra den aktive editor-runtime; automatiske versionsnoter bruger konkrete ændringer.

"""
if '== 0.1.26 ==' not in text:
    marker = 'Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.\n\n'
    if marker not in text:
        raise SystemExit('readme.txt: insertion marker missing')
    text = text.replace(marker, marker + section, 1)
readme.write_text(text, encoding='utf-8')
print('patched clean/hangar18-manager/readme.txt')

# Release notes consumed by clean-release.yml.
notes = """<h4>0.1.26</h4><ul><li><strong>WYSIWYG-hardening:</strong> editor-label/type/ID er nu ren editor-chrome og påvirker ikke længere canonical elementgeometri.</li><li><strong>Linjeskift:</strong> almindelige linjeskift og blanke linjer bevares ens i Designer, Forhåndsvisning og frontend.</li><li><strong>Rich text:</strong> tekstmarkeringen bevares ved Fed, Kursiv, Understregning og øvrige toolbar-handlinger, så formatering kan udføres uden at selection forsvinder.</li><li><strong>Typografi:</strong> brødtekst og overskrift har separate indstillinger for skrifttype, skriftstørrelse, tykkelse, linjeafstand og bogstavafstand; overskrift kan arve brødtekstens skrifttype.</li><li><strong>Manuel billedredigering:</strong> billedets X/Y/bredde/højde og manuel tilstand gemmes i canonical modellen og overlever Gem, reload og frontend-rendering.</li><li><strong>Inspector:</strong> egen lodret scroll på desktop/laptop samt bedre bevarelse af scroll-position og fokus ved re-render.</li><li><strong>Knap auto-size:</strong> Automatisk størrelse følger som standard tekst og Padding X/Y; manuel resize kan fortsat gøre knappen større og slå auto-size fra.</li><li><strong>Regression:</strong> 0.1.25 multi-template Header/Footer, Knap-element, rich text, responsive layouts, hierarchy og versionshistorik er bevaret og køres gennem release-QA.</li></ul>"""
Path('clean-release-notes.html').write_text(notes, encoding='utf-8')
print('patched clean-release-notes.html')

# Make the 0.1.26 source gates permanent in the normal release workflow.
workflow = Path('.github/workflows/clean-release.yml')
w = workflow.read_text(encoding='utf-8')
needle = '          php .github/scripts/v0125_model_qa.php\n'
gates = """          # 0.1.26 WYSIWYG / typography / persistence release gates.
          grep -q "headingFontFamily" clean/hangar18-manager/src/Model/LayoutModel.php
          grep -q "headingFontSize" clean/hangar18-manager/assets/editor-v018-core.js
          grep -q "rememberSelection" clean/hangar18-manager/assets/editor-v0125.js
          grep -q "manualW" clean/hangar18-manager/assets/editor-v018-core.js
          grep -q "manualH" clean/hangar18-manager/assets/editor-v018-core.js
          grep -q "autoSize" clean/hangar18-manager/assets/editor-v018-core.js
          grep -q "autoFitButtons" clean/hangar18-manager/assets/editor-v018-core.js
          grep -q "nl2br" clean/hangar18-manager/src/Frontend/Renderer.php
          grep -q "editor labels are chrome" clean/hangar18-manager/assets/editor-v0123-ux.css
          grep -q "overscroll-behavior:contain" clean/hangar18-manager/assets/editor-v0123-ux.css
          if grep -n "Gem clean layout" clean/hangar18-manager/assets/editor-v018-core.js clean/hangar18-manager/assets/editor-v0123-ux.js clean/hangar18-manager/assets/editor-v0125.js; then
            echo 'Obsolete generic Clean save note remains in active editor runtime.' >&2
            exit 1
          fi
"""
if '# 0.1.26 WYSIWYG / typography / persistence release gates.' not in w:
    if w.count(needle) != 1:
        raise SystemExit('clean-release.yml: v0125 QA insertion point missing/ambiguous')
    w = w.replace(needle, needle + gates, 1)
workflow.write_text(w, encoding='utf-8')
print('patched .github/workflows/clean-release.yml')

# Trigger the normal package/manifest release only after this preparation commit passes QA.
Path('clean-release-now.txt').write_text(
    'v0.1.26\n'
    'triggered_utc=2026-08-26T13:42:00Z\n'
    'reason=Release WYSIWYG, typography, rich-text selection, image persistence, Inspector scroll and Button auto-size hotfix after source QA.\n'
    'nonce=26-v0126-release\n',
    encoding='utf-8',
)
print('patched clean-release-now.txt')
