from pathlib import Path
import json

ROOT = Path('.')
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
EDITOR = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
EDITOR_CSS = ROOT / 'clean/hangar18-manager/assets/editor-v0181.css'
FORMS = ROOT / 'clean/hangar18-manager/src/Forms/FormService.php'
LAYOUT = ROOT / 'clean/hangar18-manager/src/Model/LayoutModel.php'
HISTORY = ROOT / 'clean/hangar18-manager/release-history.json'
NOTES = ROOT / 'clean-release-notes.html'
STATUS = ROOT / 'docs/v0190-status.md'


def read(path):
    return path.read_text(encoding='utf-8')


def write(path, text):
    path.write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing {label}')
    return text.replace(old, new, 1)

# Runtime version.
plugin = read(PLUGIN)
plugin = replace_once(plugin, 'Version: 0.1.89', 'Version: 0.1.90', 'plugin header version')
plugin = replace_once(plugin, "define('VDM_VERSION', '0.1.89');", "define('VDM_VERSION', '0.1.90');", 'VDM_VERSION')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.89');", "define('H18_CLEAN_VERSION', '0.1.90');", 'compatibility version')
write(PLUGIN, plugin)

# Designer: form defaults must reserve enough rows for the same real controls as frontend.
editor = read(EDITOR)
editor = replace_once(
    editor,
    'eventfacts: 12, eventfield: 18, contactform: 54, membershipform: 74',
    'eventfacts: 12, eventfield: 18, contactform: 76, membershipform: 87',
    'form default rows',
)
write(EDITOR, editor)

# Designer CSS: textarea must use the same canonical 168px geometry as live.
css = read(EDITOR_CSS)
css = replace_once(
    css,
    '.h18-vd-form-preview-field textarea{height:112px;resize:none}',
    '.h18-vd-form-preview-field textarea{height:168px;min-height:168px;resize:none}',
    'Designer textarea height',
)
write(EDITOR_CSS, css)

# Frontend: remove theme-dependent typography/textarea geometry and match Designer exactly.
forms = read(FORMS)
forms = replace_once(
    forms,
    ".h18-vd-form{box-sizing:border-box;width:100%;border-radius:6px}.h18-vd-form h2{margin:0 0 8px}.h18-vd-form-intro{margin:0 0 20px}",
    ".h18-vd-form{box-sizing:border-box;width:100%;border-radius:6px;font-family:system-ui,-apple-system,\"Segoe UI\",sans-serif;font-size:16px;line-height:1.35;text-align:left}.h18-vd-form h2{margin:0 0 8px;padding:0;color:inherit;font:700 32px/1.2 system-ui,-apple-system,\"Segoe UI\",sans-serif}.h18-vd-form-intro{margin:0 0 20px;padding:0;color:inherit;font:400 16px/1.5 system-ui,-apple-system,\"Segoe UI\",sans-serif}",
    'frontend canonical form typography',
)
forms = replace_once(
    forms,
    ".h18-vd-form-field{display:flex;flex-direction:column;gap:6px;font-weight:600}.h18-vd-form-field.is-wide{grid-column:1/-1}",
    ".h18-vd-form-field{display:flex;flex-direction:column;gap:6px;min-width:0;font-size:14px;font-weight:600;line-height:1.35;color:inherit}.h18-vd-form-field.is-wide{grid-column:1/-1}",
    'frontend canonical field labels',
)
forms = replace_once(
    forms,
    ".h18-vd-form input,.h18-vd-form textarea{box-sizing:border-box;width:100%;border:1px solid #b8b8b2;border-radius:4px;background:var(--h18-form-field-bg);color:inherit;padding:11px 12px;font:inherit}",
    ".h18-vd-form input,.h18-vd-form textarea{box-sizing:border-box;width:100%;min-height:42px;border:1px solid #b8b8b2;border-radius:4px;background:var(--h18-form-field-bg);color:inherit;padding:11px 12px;font:400 16px/1.35 system-ui,-apple-system,\"Segoe UI\",sans-serif}.h18-vd-form textarea{height:168px;min-height:168px;resize:vertical}",
    'frontend canonical controls and textarea',
)
forms = replace_once(
    forms,
    ".h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0}.h18-vd-form-consent input{width:auto;margin-top:3px}",
    ".h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4;color:inherit}.h18-vd-form-consent input{width:auto;min-height:0;margin-top:3px}",
    'frontend canonical consent',
)
forms = replace_once(
    forms,
    ".h18-vd-form-submit{border:0;border-radius:4px;background:var(--h18-form-accent);color:#fff;padding:11px 20px;font:inherit;font-weight:700;cursor:pointer}",
    ".h18-vd-form-submit{display:inline-block;border:0;border-radius:4px;background:var(--h18-form-accent);color:#fff;padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,\"Segoe UI\",sans-serif;cursor:pointer}",
    'frontend canonical submit',
)
write(FORMS, forms)

# Existing saved form nodes also need enough desktop rows, otherwise frontend content can overflow the background.
layout = read(LAYOUT)
needle = """            if (in_array($type, ['section', 'container'], true) && (!isset($nodeRaw['props']) || !is_array($nodeRaw['props']) || !array_key_exists('minHeightRows', $nodeRaw['props']))) {
                $nodes[$id]['props']['minHeightRows'] = (int) $nodes[$id]['geometry']['desktop']['h'];
            }
"""
replacement = needle + """            if (in_array($type, ['contactform', 'membershipform'], true)) {
                // v0.1.90 FORM-WYSIWYG-002: form controls have canonical intrinsic geometry.
                // Existing layouts created with the old 112px Designer textarea must not keep a too-short grid span.
                $formMinRows = $type === 'membershipform' ? 87 : 76;
                $currentRows = (int) ($nodes[$id]['geometry']['desktop']['h'] ?? 0);
                if ($currentRows > 0 && $currentRows < $formMinRows) {
                    $nodes[$id]['geometry']['desktop']['h'] = $formMinRows;
                }
            }
"""
layout = replace_once(layout, needle, replacement, 'LayoutModel form minimum height normalization')
write(LAYOUT, layout)

# Release history.
history = json.loads(read(HISTORY))
entry = {
    'version': '0.1.90',
    'date': '2026-09-03',
    'items': [
        'FORM-WYSIWYG-002: Designer og frontend bruger nu samme canonical formulargeometri.',
        'Kommentar/Besked textarea er 168 px i både Designer og live i stedet for 112 px kun i Designer.',
        'Formularfelter, labels, samtykke og submit-knap bruger samme eksplicitte typografi og spacing i Editor og frontend.',
        'Eksisterende Kontaktformularer under 76 grid-rækker og Bliv medlem-formularer under 87 grid-rækker normaliseres til en sikker minimumshøjde, så submit-knappen ikke flyder uden for formularbaggrunden.',
        'Nye formularer oprettes med de samme minimumshøjder, så Editor → Forhåndsvisning → Live starter med samme geometri.'
    ]
}
versions = history.get('versions', []) if isinstance(history, dict) else []
if not versions or versions[0].get('version') != '0.1.90':
    history['versions'] = [entry] + versions
write(HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes = read(NOTES)
section = '''<section data-version="0.1.90"><h2>0.1.90</h2><ul><li><strong>Formular-paritet:</strong> Kontakt- og Bliv medlem-formularer bruger samme mål i Designer og live.</li><li>Kommentar/Besked-feltet er nu canonical 168 px i begge visninger; den gamle 112 px Designer-højde er fjernet.</li><li>Labels, felter, samtykke og submit-knap bruger samme typografi, line-height, padding og spacing.</li><li>Eksisterende formularer med for lav grid-højde normaliseres sikkert, så <strong>Send indmeldelse</strong>/<strong>Send besked</strong> ikke flyder uden for formularens baggrund.</li><li>Nye formularer reserverer korrekt minimumshøjde fra start.</li></ul></section>\n'''
if 'data-version="0.1.90"' not in notes:
    notes = section + notes
write(NOTES, notes)

write(STATUS, '''# Visual Designer Manager v0.1.90 – formular WYSIWYG-paritet\n\nStatus: kandidat.\n\n- FORM-WYSIWYG-002: canonical formulargeometri i Editor og frontend.\n- Textarea: 168 px begge steder.\n- Kontaktformular: minimum 76 rækker på desktop.\n- Bliv medlem-formular: minimum 87 rækker på desktop.\n- Eksisterende for lave formulargeometrier normaliseres read-time/save-time gennem LayoutModel.\n- Frontend-typografi og spacing er eksplicit og matcher Designer-previewet.\n''')

print('Applied Visual Designer Manager v0.1.90 form WYSIWYG parity candidate')
