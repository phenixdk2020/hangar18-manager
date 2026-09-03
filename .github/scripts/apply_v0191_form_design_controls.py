from pathlib import Path
import json

ROOT = Path('.')
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
MODEL = ROOT / 'clean/hangar18-manager/src/Model/LayoutModel.php'
FORM = ROOT / 'clean/hangar18-manager/src/Forms/FormService.php'
EDITOR = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
CSS = ROOT / 'clean/hangar18-manager/assets/editor-v0181.css'
HISTORY = ROOT / 'clean/hangar18-manager/release-history.json'
NOTES = ROOT / 'clean-release-notes.html'
STATUS = ROOT / 'docs/v0191-status.md'


def read(path): return path.read_text(encoding='utf-8')
def write(path, text): path.write_text(text, encoding='utf-8')
def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing marker for {label}')
    return text.replace(old, new, 1)

# Version bump.
plugin = read(PLUGIN)
plugin = replace_once(plugin, 'Version: 0.1.90', 'Version: 0.1.91', 'plugin header')
plugin = replace_once(plugin, "define('VDM_VERSION', '0.1.90');", "define('VDM_VERSION', '0.1.91');", 'VDM_VERSION')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.90');", "define('H18_CLEAN_VERSION', '0.1.91');", 'compat version')
write(PLUGIN, plugin)

# Canonical form props in server model.
model = read(MODEL)
old = """                'padding' => self::clamp($raw['padding'] ?? 24, 0, 80, 24),
                'radius' => self::clamp($raw['radius'] ?? 6, 0, 60, 6),
                'showPhone' => array_key_exists('showPhone', $raw) ? (bool) $raw['showPhone'] : true,
"""
new = """                'padding' => self::clamp($raw['padding'] ?? 24, 0, 80, 24),
                'radius' => self::clamp($raw['radius'] ?? 6, 0, 60, 6),
                'fieldGap' => self::clamp($raw['fieldGap'] ?? 16, 0, 80, 16),
                'textareaHeight' => self::clamp($raw['textareaHeight'] ?? 168, 80, 400, 168),
                'consentMargin' => self::clamp($raw['consentMargin'] ?? 18, 0, 80, 18),
                'buttonPaddingX' => self::clamp($raw['buttonPaddingX'] ?? 20, 0, 80, 20),
                'buttonPaddingY' => self::clamp($raw['buttonPaddingY'] ?? 11, 0, 60, 11),
                'showPhone' => array_key_exists('showPhone', $raw) ? (bool) $raw['showPhone'] : true,
"""
model = replace_once(model, old, new, 'LayoutModel form props')
write(MODEL, model)

# Frontend rendering: same props become CSS variables.
form = read(FORM)
old = """        $padding = max(0, min(80, (int) ($props['padding'] ?? 24)));
        $showPhone = !array_key_exists('showPhone', $props) || !empty($props['showPhone']);
"""
new = """        $padding = max(0, min(80, (int) ($props['padding'] ?? 24)));
        $fieldGap = max(0, min(80, (int) ($props['fieldGap'] ?? 16)));
        $textareaHeight = max(80, min(400, (int) ($props['textareaHeight'] ?? 168)));
        $consentMargin = max(0, min(80, (int) ($props['consentMargin'] ?? 18)));
        $buttonPaddingX = max(0, min(80, (int) ($props['buttonPaddingX'] ?? 20)));
        $buttonPaddingY = max(0, min(60, (int) ($props['buttonPaddingY'] ?? 11)));
        $showPhone = !array_key_exists('showPhone', $props) || !empty($props['showPhone']);
"""
form = replace_once(form, old, new, 'FormService prop reads')
old = """            . 'background:' . $background . ';color:' . $textColor . ';padding:' . $padding . 'px;'
            . '--h18-form-field-bg:' . $fieldBackground . ';--h18-form-accent:' . $accent . ';';
"""
new = """            . 'background:' . $background . ';color:' . $textColor . ';padding:' . $padding . 'px;'
            . '--h18-form-field-bg:' . $fieldBackground . ';--h18-form-accent:' . $accent . ';'
            . '--vdm-form-field-gap:' . $fieldGap . 'px;--vdm-form-textarea-height:' . $textareaHeight . 'px;'
            . '--vdm-form-consent-margin:' . $consentMargin . 'px;--vdm-form-button-padding-x:' . $buttonPaddingX . 'px;'
            . '--vdm-form-button-padding-y:' . $buttonPaddingY . 'px;';
"""
form = replace_once(form, old, new, 'FormService CSS variables')
form = replace_once(form,
    ".h18-vd-form-body{display:block}.h18-vd-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}",
    ".h18-vd-form-body{display:block}.h18-vd-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--vdm-form-field-gap,16px)}",
    'frontend field gap')
form = replace_once(form,
    ".h18-vd-form textarea{height:168px;min-height:168px;resize:vertical}",
    ".h18-vd-form textarea{height:var(--vdm-form-textarea-height,168px);min-height:var(--vdm-form-textarea-height,168px);resize:vertical}",
    'frontend textarea height')
form = replace_once(form,
    ".h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4;color:inherit}",
    ".h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:var(--vdm-form-consent-margin,18px) 0;font-size:14px;font-weight:400;line-height:1.4;color:inherit}",
    'frontend consent margin')
form = replace_once(form,
    ".h18-vd-form-submit{display:inline-block;border:0;border-radius:4px;background:var(--h18-form-accent);color:#fff;padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,\"Segoe UI\",sans-serif;cursor:pointer}",
    ".h18-vd-form-submit{display:inline-block;border:0;border-radius:4px;background:var(--h18-form-accent);color:#fff;padding:var(--vdm-form-button-padding-y,11px) var(--vdm-form-button-padding-x,20px);font:700 16px/1.35 system-ui,-apple-system,\"Segoe UI\",sans-serif;cursor:pointer}",
    'frontend button padding')
write(FORM, form)

# Editor model + preview + Inspector.
editor = read(EDITOR)
old = """                padding:clamp(parseInt(raw.padding || 24,10)||24,0,80), radius:clamp(parseInt(raw.radius || 6,10)||6,0,60),
                showPhone:raw.showPhone !== false, requireConsent:raw.requireConsent !== false
"""
new = """                padding:clamp(parseInt(raw.padding || 24,10)||24,0,80), radius:clamp(parseInt(raw.radius || 6,10)||6,0,60),
                fieldGap:clamp(parseInt(raw.fieldGap == null ? 16 : raw.fieldGap,10)||0,0,80),
                textareaHeight:clamp(parseInt(raw.textareaHeight || 168,10)||168,80,400),
                consentMargin:clamp(parseInt(raw.consentMargin == null ? 18 : raw.consentMargin,10)||0,0,80),
                buttonPaddingX:clamp(parseInt(raw.buttonPaddingX == null ? 20 : raw.buttonPaddingX,10)||0,0,80),
                buttonPaddingY:clamp(parseInt(raw.buttonPaddingY == null ? 11 : raw.buttonPaddingY,10)||0,0,60),
                showPhone:raw.showPhone !== false, requireConsent:raw.requireConsent !== false
"""
editor = replace_once(editor, old, new, 'editor normalize form props')
old = """            box.style.setProperty('--h18-form-preview-field-bg', node.props.fieldBackground || '#ffffff');
            box.style.setProperty('--h18-form-preview-accent', node.props.accentColor || '#30382a');
"""
new = """            box.style.setProperty('--h18-form-preview-field-bg', node.props.fieldBackground || '#ffffff');
            box.style.setProperty('--h18-form-preview-accent', node.props.accentColor || '#30382a');
            box.style.setProperty('--vdm-form-field-gap', String(node.props.fieldGap == null ? 16 : node.props.fieldGap) + 'px');
            box.style.setProperty('--vdm-form-textarea-height', String(node.props.textareaHeight || 168) + 'px');
            box.style.setProperty('--vdm-form-consent-margin', String(node.props.consentMargin == null ? 18 : node.props.consentMargin) + 'px');
            box.style.setProperty('--vdm-form-button-padding-x', String(node.props.buttonPaddingX == null ? 20 : node.props.buttonPaddingX) + 'px');
            box.style.setProperty('--vdm-form-button-padding-y', String(node.props.buttonPaddingY == null ? 11 : node.props.buttonPaddingY) + 'px');
"""
editor = replace_once(editor, old, new, 'editor preview form variables')
old = """            html += '<div class=\"h18-vd-menu-group\"><h3>Design</h3><div class=\"h18-clean-field-grid\"><label>Baggrund<input data-field=\"formBackground\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#f4f1e8') + '\"></label><label>Feltbaggrund<input data-field=\"formFieldBackground\" type=\"color\" value=\"' + escapeAttr(node.props.fieldBackground || '#ffffff') + '\"></label><label>Tekst<input data-field=\"formTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.textColor || '#30382a') + '\"></label><label>Knap/accent<input data-field=\"formAccentColor\" type=\"color\" value=\"' + escapeAttr(node.props.accentColor || '#30382a') + '\"></label><label>Padding<input data-field=\"formPadding\" type=\"number\" min=\"0\" max=\"80\" value=\"' + (node.props.padding || 24) + '\"></label><label>Hjørner<input data-field=\"formRadius\" type=\"number\" min=\"0\" max=\"60\" value=\"' + (node.props.radius || 6) + '\"></label></div></div>';
"""
new = """            html += '<div class=\"h18-vd-menu-group\"><h3>Design</h3><div class=\"h18-clean-field-grid\"><label>Baggrund<input data-field=\"formBackground\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#f4f1e8') + '\"></label><label>Feltbaggrund<input data-field=\"formFieldBackground\" type=\"color\" value=\"' + escapeAttr(node.props.fieldBackground || '#ffffff') + '\"></label><label>Tekst<input data-field=\"formTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.textColor || '#30382a') + '\"></label><label>Knap/accent<input data-field=\"formAccentColor\" type=\"color\" value=\"' + escapeAttr(node.props.accentColor || '#30382a') + '\"></label><label>Padding<input data-field=\"formPadding\" type=\"number\" min=\"0\" max=\"80\" value=\"' + (node.props.padding || 24) + '\"></label><label>Hjørner<input data-field=\"formRadius\" type=\"number\" min=\"0\" max=\"60\" value=\"' + (node.props.radius || 6) + '\"></label><label>Feltafstand px<input data-field=\"formFieldGap\" type=\"number\" min=\"0\" max=\"80\" value=\"' + (node.props.fieldGap == null ? 16 : node.props.fieldGap) + '\"></label><label>Kommentar/Besked højde px<input data-field=\"formTextareaHeight\" type=\"number\" min=\"80\" max=\"400\" value=\"' + (node.props.textareaHeight || 168) + '\"></label><label>Samtykkeafstand px<input data-field=\"formConsentMargin\" type=\"number\" min=\"0\" max=\"80\" value=\"' + (node.props.consentMargin == null ? 18 : node.props.consentMargin) + '\"></label><label>Knap padding X<input data-field=\"formButtonPaddingX\" type=\"number\" min=\"0\" max=\"80\" value=\"' + (node.props.buttonPaddingX == null ? 20 : node.props.buttonPaddingX) + '\"></label><label>Knap padding Y<input data-field=\"formButtonPaddingY\" type=\"number\" min=\"0\" max=\"60\" value=\"' + (node.props.buttonPaddingY == null ? 11 : node.props.buttonPaddingY) + '\"></label></div><p class=\"description\">Alle mål bruges identisk i Designer, forhåndsvisning og live. Formularboksen vokser automatisk, hvis indholdet kræver mere højde.</p></div>';
"""
editor = replace_once(editor, old, new, 'Inspector form design controls')
old = """                else if (field === 'formPadding') { current.props.padding=clamp(parseInt(control.value||24,10)||24,0,80); }
                else if (field === 'formRadius') { current.props.radius=clamp(parseInt(control.value||6,10)||6,0,60); }
"""
new = """                else if (field === 'formPadding') { current.props.padding=clamp(parseInt(control.value||24,10)||24,0,80); }
                else if (field === 'formRadius') { current.props.radius=clamp(parseInt(control.value||6,10)||6,0,60); }
                else if (field === 'formFieldGap') { current.props.fieldGap=clamp(parseInt(control.value||0,10)||0,0,80); }
                else if (field === 'formTextareaHeight') { current.props.textareaHeight=clamp(parseInt(control.value||168,10)||168,80,400); }
                else if (field === 'formConsentMargin') { current.props.consentMargin=clamp(parseInt(control.value||0,10)||0,0,80); }
                else if (field === 'formButtonPaddingX') { current.props.buttonPaddingX=clamp(parseInt(control.value||0,10)||0,0,80); }
                else if (field === 'formButtonPaddingY') { current.props.buttonPaddingY=clamp(parseInt(control.value||0,10)||0,0,60); }
"""
editor = replace_once(editor, old, new, 'form Inspector handlers')
# Auto-grow form nodes only when rendered content exceeds the current canonical box.
marker = """    function reconcileLayoutAfterRender(canvas) {
        const autoButtons = autoFitButtons();
        const materialized = materializeNaturalLeafHeights();
"""
replacement = """    function fitOverflowingForms() {
        let changed = false;
        document.querySelectorAll('.h18-clean-node[data-node-id]').forEach(function (card) {
            const node = nodeById(card.getAttribute('data-node-id') || '');
            if (!node || !['contactform','membershipform'].includes(node.type) || node.geometry.desktop.h <= 0) { return; }
            const preview = card.querySelector('.h18-vd-form-preview');
            if (!preview) { return; }
            const needed = Math.max(1, Math.ceil(preview.scrollHeight / ROW_PX));
            if (needed > node.geometry.desktop.h) {
                node.geometry.desktop.h = needed;
                ['laptop','tablet','mobile'].forEach(function (key) {
                    if (node.geometry[key] && node.geometry[key].inheritDesktop !== false) { node.geometry[key].h = needed; }
                });
                changed = true;
            }
        });
        return changed;
    }

    function reconcileLayoutAfterRender(canvas) {
        const autoButtons = autoFitButtons();
        const materialized = materializeNaturalLeafHeights();
"""
editor = replace_once(editor, marker, replacement, 'fitOverflowingForms insertion')
old = """        const collisionHealed = healMaterializationCollisions(materialized);
        const containersChanged = syncContainerHeights();
        const changed = materialized.size > 0 || collisionHealed || containersChanged;
"""
new = """        const collisionHealed = healMaterializationCollisions(materialized);
        const formsChanged = fitOverflowingForms();
        const containersChanged = syncContainerHeights();
        const changed = materialized.size > 0 || collisionHealed || formsChanged || containersChanged;
"""
editor = replace_once(editor, old, new, 'form auto-grow reconcile')
write(EDITOR, editor)

css = read(CSS)
css = replace_once(css, '.h18-vd-form-preview-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}', '.h18-vd-form-preview-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--vdm-form-field-gap,16px)}', 'preview field gap')
css = replace_once(css, '.h18-vd-form-preview-field textarea{height:168px;min-height:168px;resize:none}', '.h18-vd-form-preview-field textarea{height:var(--vdm-form-textarea-height,168px);min-height:var(--vdm-form-textarea-height,168px);resize:none}', 'preview textarea')
css = replace_once(css, '.h18-vd-form-preview-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4;color:inherit}', '.h18-vd-form-preview-consent{display:flex;gap:9px;align-items:flex-start;margin:var(--vdm-form-consent-margin,18px) 0;font-size:14px;font-weight:400;line-height:1.4;color:inherit}', 'preview consent')
css = replace_once(css, '.h18-vd-form-preview-submit{display:inline-block;border:0;border-radius:4px;background:var(--h18-form-preview-accent);color:#fff;padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif;opacity:1;cursor:default}', '.h18-vd-form-preview-submit{display:inline-block;border:0;border-radius:4px;background:var(--h18-form-preview-accent);color:#fff;padding:var(--vdm-form-button-padding-y,11px) var(--vdm-form-button-padding-x,20px);font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif;opacity:1;cursor:default}', 'preview button padding')
write(CSS, css)

history = json.loads(read(HISTORY))
history['versions'].insert(0, {
    'version': '0.1.91',
    'date': '2026-09-03',
    'items': [
        'VDM-FORM-DESIGN-002: Bliv medlem/Kontaktformular har nu canonical designkontroller for feltafstand, textarea-højde, samtykkeafstand og submit-padding.',
        'De nye formmål normaliseres identisk i PHP LayoutModel og JavaScript-editoren og bruges som CSS-variabler i både Designer-preview og frontend.',
        'Formularnoder auto-vokser kun ved overflow, så større indhold ikke kan flyde ud af formularens baggrund.',
        'Eksisterende 0.1.90-layouts beholder samme visuelle defaults: 16 px gap, 168 px textarea, 18 px samtykkeafstand og 20/11 px knap-padding.'
    ]
})
write(HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes = read(NOTES)
section = '<section data-version="0.1.91"><h2>0.1.91</h2><ul><li><strong>Formulardesign:</strong> justér feltafstand, Kommentar/Besked-højde, samtykkeafstand og knap-padding direkte i Inspector.</li><li>Samme værdier bruges i Designer, forhåndsvisning og live.</li><li>Formularer vokser automatisk ved overflow, så submit-knappen ikke kan ende uden for baggrunden.</li><li>0.1.90-standardudseendet bevares uændret, hvis de nye felter ikke justeres.</li></ul></section>\n'
anchor = '<section data-version="0.1.90">'
if anchor not in notes: raise SystemExit('Release notes v0.1.90 anchor missing')
notes = notes.replace(anchor, section + anchor, 1)
write(NOTES, notes)

write(STATUS, '''# Visual Designer Manager v0.1.91 status\n\n- Candidate: form design controls + overflow auto-growth.\n- Defaults preserve v0.1.90 geometry.\n- Release only after dedicated parity QA and historical regressions pass.\n''')
print('Applied v0.1.91 candidate')
