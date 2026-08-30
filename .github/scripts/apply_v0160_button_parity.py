from pathlib import Path
import json

ROOT = Path('.')
PLUGIN_ROOT = ROOT / 'clean/hangar18-manager'
PLUGIN = PLUGIN_ROOT / 'hangar18-manager.php'
MODEL = PLUGIN_ROOT / 'src/Model/LayoutModel.php'
RENDERER = PLUGIN_ROOT / 'src/Frontend/Renderer.php'
EDITOR_JS = PLUGIN_ROOT / 'assets/editor-v018-core.js'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
NOTES = ROOT / 'clean-release-notes.html'
HISTORY = PLUGIN_ROOT / 'release-history.json'
STATUS = ROOT / 'docs/v0160-status.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# BUG-22 / VD-BUTTON-PARITY-001
# Button typography must be canonical instead of inherited independently from
# wp-admin in Designer and the active theme on frontend.
model = MODEL.read_text(encoding='utf-8')
model_old = """                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#ffffff')) ?: '#ffffff',
                'hoverBackground' => sanitize_hex_color((string) ($raw['hoverBackground'] ?? '#525a5f')) ?: '#525a5f',
"""
model_new = """                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#ffffff')) ?: '#ffffff',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 400, 100, 900, 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.2, 0.8, 3.0, 1.2),
                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),
                'hoverBackground' => sanitize_hex_color((string) ($raw['hoverBackground'] ?? '#525a5f')) ?: '#525a5f',
"""
model = replace_once(model, model_old, model_new, 'canonical button typography')
MODEL.write_text(model, encoding='utf-8')

editor = EDITOR_JS.read_text(encoding='utf-8')
normalize_old = """                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#ffffff',
                hoverBackground: /^#[0-9a-f]{6}$/i.test(String(raw.hoverBackground || '')) ? String(raw.hoverBackground).toLowerCase() : '#525a5f',
"""
normalize_new = """                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#ffffff',
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 120),
                fontWeight: clamp(parseInt(raw.fontWeight || 400, 10) || 400, 100, 900),
                lineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.lineHeight || 1.2) || 1.2)),
                letterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.letterSpacing || 0) || 0)),
                hoverBackground: /^#[0-9a-f]{6}$/i.test(String(raw.hoverBackground || '')) ? String(raw.hoverBackground).toLowerCase() : '#525a5f',
"""
editor = replace_once(editor, normalize_old, normalize_new, 'Designer button typography normalization')

preview_old = """            button.style.background = node.props.background || '#30382a';
            button.style.color = node.props.textColor || '#ffffff';
            button.style.borderRadius = String(node.props.radius || 0) + 'px';
            button.style.padding = String(node.props.paddingY || 10) + 'px ' + String(node.props.paddingX || 20) + 'px';
"""
preview_new = """            button.style.background = node.props.background || '#30382a';
            button.style.color = node.props.textColor || '#ffffff';
            button.style.fontFamily = fontCss(node.props.fontFamily || 'system', 'system');
            button.style.fontSize = String(node.props.fontSize || 16) + 'px';
            button.style.fontWeight = String(node.props.fontWeight || 400);
            button.style.lineHeight = String(node.props.lineHeight || 1.2);
            button.style.letterSpacing = String(node.props.letterSpacing || 0) + 'px';
            button.style.whiteSpace = node.props.autoSize === false ? 'normal' : 'nowrap';
            button.style.borderRadius = String(node.props.radius || 0) + 'px';
            button.style.padding = String(node.props.paddingY || 10) + 'px ' + String(node.props.paddingX || 20) + 'px';
"""
editor = replace_once(editor, preview_old, preview_new, 'Designer button preview typography')

inspector_marker = """            html += '<label class=\"h18-clean-checkbox\"><input data-field=\"autoSize\" type=\"checkbox\"' + (node.props.autoSize !== false ? ' checked' : '') + '> Automatisk størrelse efter tekst og padding</label>';
            html += '<div class=\"h18-clean-field-grid\"><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#30382a') + '\"></label><label>Tekstfarve<input data-field=\"textColor\" type=\"color\" value=\"' + escapeAttr(node.props.textColor || '#ffffff') + '\"></label><label>Hover baggrund<input data-field=\"hoverBackground\" type=\"color\" value=\"' + escapeAttr(node.props.hoverBackground || '#525a5f') + '\"></label><label>Hover tekst<input data-field=\"hoverTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.hoverTextColor || '#ffffff') + '\"></label><label>Focus-farve<input data-field=\"focusColor\" type=\"color\" value=\"' + escapeAttr(node.props.focusColor || '#c3ae83') + '\"></label><label>Hjørner px<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"100\" value=\"' + (node.props.radius || 0) + '\"></label><label>Padding X<input data-field=\"paddingX\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingX || 20) + '\"></label><label>Padding Y<input data-field=\"paddingY\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingY || 10) + '\"></label></div>';
"""
inspector_new = """            html += '<label class=\"h18-clean-checkbox\"><input data-field=\"autoSize\" type=\"checkbox\"' + (node.props.autoSize !== false ? ' checked' : '') + '> Automatisk størrelse efter tekst og padding</label>';
            html += '<div class=\"h18-vd-typography\"><strong>Typografi · knap</strong><div class=\"h18-clean-field-grid\"><label>Skrifttype<select data-field=\"fontFamily\">' + fontOptions(node.props.fontFamily || 'system', false) + '</select></label><label>Størrelse px<input data-field=\"fontSize\" type=\"number\" min=\"8\" max=\"120\" value=\"' + (node.props.fontSize || 16) + '\"></label><label>Tykkelse<select data-field=\"fontWeight\">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value=\"' + v + '\"' + (parseInt(node.props.fontWeight || 400, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label><label>Linjeafstand<input data-field=\"lineHeight\" type=\"number\" step=\"0.1\" min=\"0.8\" max=\"3\" value=\"' + (node.props.lineHeight || 1.2) + '\"></label><label>Bogstavafstand px<input data-field=\"letterSpacing\" type=\"number\" step=\"0.1\" min=\"-10\" max=\"30\" value=\"' + (node.props.letterSpacing || 0) + '\"></label></div></div>';
            html += '<div class=\"h18-clean-field-grid\"><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#30382a') + '\"></label><label>Tekstfarve<input data-field=\"textColor\" type=\"color\" value=\"' + escapeAttr(node.props.textColor || '#ffffff') + '\"></label><label>Hover baggrund<input data-field=\"hoverBackground\" type=\"color\" value=\"' + escapeAttr(node.props.hoverBackground || '#525a5f') + '\"></label><label>Hover tekst<input data-field=\"hoverTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.hoverTextColor || '#ffffff') + '\"></label><label>Focus-farve<input data-field=\"focusColor\" type=\"color\" value=\"' + escapeAttr(node.props.focusColor || '#c3ae83') + '\"></label><label>Hjørner px<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"100\" value=\"' + (node.props.radius || 0) + '\"></label><label>Padding X<input data-field=\"paddingX\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingX || 20) + '\"></label><label>Padding Y<input data-field=\"paddingY\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingY || 10) + '\"></label></div>';
"""
editor = replace_once(editor, inspector_marker, inspector_new, 'Button Inspector typography controls')
EDITOR_JS.write_text(editor, encoding='utf-8')

renderer = RENDERER.read_text(encoding='utf-8')
renderer_color_old = """            $background = sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#ffffff')) ?: '#ffffff';
            $hoverBackground = sanitize_hex_color((string) ($props['hoverBackground'] ?? '#525a5f')) ?: '#525a5f';
"""
renderer_color_new = """            $background = sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#ffffff')) ?: '#ffffff';
            $fontFamily = self::fontCss((string) ($props['fontFamily'] ?? 'system'));
            $fontSize = max(8, min(120, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 400)));
            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.2)));
            $letterSpacing = max(-10.0, min(30.0, (float) ($props['letterSpacing'] ?? 0)));
            $hoverBackground = sanitize_hex_color((string) ($props['hoverBackground'] ?? '#525a5f')) ?: '#525a5f';
"""
renderer = replace_once(renderer, renderer_color_old, renderer_color_new, 'Frontend button typography variables')

renderer_padding_old = """            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 20)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 10)));
            $placementMode = (string) ($props['placementMode'] ?? 'normal');
"""
renderer_padding_new = """            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 20)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 10)));
            $autoSize = !array_key_exists('autoSize', $props) || !empty($props['autoSize']);
            $whiteSpace = $autoSize ? 'nowrap' : 'normal';
            $placementMode = (string) ($props['placementMode'] ?? 'normal');
"""
renderer = replace_once(renderer, renderer_padding_old, renderer_padding_new, 'Frontend button autosize wrap contract')

renderer_link_old = """            $linkStyle = $borderStyle . $radiusStyle . 'padding:' . $paddingY . 'px ' . $paddingX . 'px;';
"""
renderer_link_new = """            $linkStyle = $borderStyle . $radiusStyle . 'padding:' . $paddingY . 'px ' . $paddingX . 'px;'
                . 'font-family:' . $fontFamily . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;white-space:' . $whiteSpace . ';';
"""
renderer = replace_once(renderer, renderer_link_old, renderer_link_new, 'Frontend button canonical typography style')
RENDERER.write_text(renderer, encoding='utf-8')

# Version bump.
plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, ' * Version: 0.1.59', ' * Version: 0.1.60', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.59');", "define('H18_CLEAN_VERSION', '0.1.60');", 'runtime version')
PLUGIN.write_text(plugin, encoding='utf-8')

# Technical contract and release documentation.
tech = TECH.read_text(encoding='utf-8')
contract = r'''

## 0.1.60 – Button Designer/frontend parity

### VD-BUTTON-PARITY-001
- Knap-elementets typografi er canonical data: skrifttype, størrelse, tykkelse, linjeafstand og bogstavafstand.
- Designer-preview og PHP Renderer bruger de samme Button-properties og samme system-font fallback.
- `autoSize=true` betyder, at knapteksten holdes på én linje (`nowrap`) og Designerens målte tekst/padding materialiserer elementets grid-geometri.
- `autoSize=false` bevarer manuel bredde/højde og tillader normal tekstombrydning.
- Temaets link-/button-typografi må ikke ændre den synlige størrelse på et Visual Designer Button-element.
- Sektion/Kasse-geometri, Menu, Billede og Tekst ændres ikke af denne kontrakt.
'''
if '## 0.1.60 – Button Designer/frontend parity' not in tech:
    tech += contract
TECH.write_text(tech, encoding='utf-8')

notes = NOTES.read_text(encoding='utf-8')
release_notes = '''<h4>0.1.60 – Button Designer/frontend parity</h4><ul><li><strong>BUG-22:</strong> Knapper bruger nu samme canonical typografi i Designer og på frontend.</li><li>Knap Inspector har skrifttype, skriftstørrelse, skrifttykkelse, linjeafstand og bogstavafstand.</li><li>Automatisk størrelse holder knapteksten på én linje og måles ud fra samme font og padding som frontend.</li><li>Manuel størrelse tillader fortsat normal tekstombrydning.</li><li>Temaets globale link-/button-typografi kan ikke længere ændre Visual Designer-knappens størrelse.</li></ul>\n'''
if not notes.startswith('<h4>0.1.60'):
    notes = release_notes + notes
NOTES.write_text(notes, encoding='utf-8')

history_data = json.loads(HISTORY.read_text(encoding='utf-8'))
if not isinstance(history_data, dict):
    raise SystemExit('release-history.json has unexpected top-level format')
versions = history_data.setdefault('versions', [])
if not versions or versions[0].get('version') != '0.1.60':
    versions.insert(0, {
        'version': '0.1.60',
        'date': '2026-08-30',
        'items': [
            'BUG-22: Button Designer/frontend parity er rettet.',
            'Button har nu canonical fontFamily, fontSize, fontWeight, lineHeight og letterSpacing.',
            'Designer-preview og frontend Renderer bruger samme typografidata.',
            'Auto størrelse bruger nowrap; manuel størrelse tillader wrap.',
            'Sektion/Kasse, Menu, Billede og Tekst er uændret.'
        ],
    })
HISTORY.write_text(json.dumps(history_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

STATUS.parent.mkdir(parents=True, exist_ok=True)
STATUS.write_text('''# Visual Designer Manager 0.1.60 status\n\n- BUG-22 / VD-BUTTON-PARITY-001 implementeret.\n- Button-typografi er canonical i LayoutModel.\n- Designer-preview og frontend Renderer bruger samme font, størrelse, tykkelse, linjeafstand og bogstavafstand.\n- Auto størrelse holder teksten på én linje og bruger den samme målte typografi som frontend.\n- Manuel størrelse kan fortsat ombryde tekst.\n- Button Inspector har de nye typografifelter.\n- Ingen ændring i Sektion/Kasse, Menu, Billede eller Tekst.\n''', encoding='utf-8')

print('Applied Visual Designer Manager 0.1.60 Button Designer/frontend parity patch.')
