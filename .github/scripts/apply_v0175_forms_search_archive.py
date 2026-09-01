from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f'Missing required file: {rel}')
    return path.read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    if new in value:
        return
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one anchor, found {count}: {old[:120]!r}')
    write(rel, value.replace(old, new, 1))


def insert_before_once(rel: str, marker: str, addition: str, sentinel: str) -> None:
    value = read(rel)
    if sentinel in value:
        return
    pos = value.find(marker)
    if pos < 0:
        raise SystemExit(f'{rel}: missing marker: {marker[:120]!r}')
    write(rel, value[:pos] + addition + value[pos:])


PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
LAYOUT = 'clean/hangar18-manager/src/Model/LayoutModel.php'
RENDERER = 'clean/hangar18-manager/src/Frontend/Renderer.php'
EDITOR = 'clean/hangar18-manager/src/Admin/EditorController.php'
EDITOR_JS = 'clean/hangar18-manager/assets/editor-v018-core.js'
ADMIN = 'clean/hangar18-manager/src/Admin/AdminController.php'
ADMIN_CSS = 'clean/hangar18-manager/assets/admin-v0175.css'
REGISTRY = 'clean/hangar18-manager/src/Modules/ModuleRegistry.php'
EVENT_ADMIN = 'clean/hangar18-manager/src/Admin/EventAdminController.php'
FORMS = 'clean/hangar18-manager/src/Forms/FormService.php'
PROVISIONER = 'clean/hangar18-manager/src/Migration/FormPageProvisioner.php'
COLLECTION = 'clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php'
HISTORY = 'clean/hangar18-manager/release-history.json'
BACKLOG = 'docs/clean-backlog-v0100.md'
NOTES = 'clean-release-notes.html'
STATUS = 'docs/v0175-status.md'

# Version and runtime bootstrap.
replace_once(PLUGIN, ' * Version: 0.1.74', ' * Version: 0.1.75')
replace_once(PLUGIN, "define('H18_CLEAN_VERSION', '0.1.74');", "define('H18_CLEAN_VERSION', '0.1.75');")
replace_once(
    PLUGIN,
    "require_once H18_CLEAN_DIR . 'src/Modules/VehicleFieldRegistry.php';",
    "require_once H18_CLEAN_DIR . 'src/Modules/VehicleFieldRegistry.php';\nrequire_once H18_CLEAN_DIR . 'src/Forms/FormService.php';",
)
replace_once(
    PLUGIN,
    "require_once H18_CLEAN_DIR . 'src/Migration/SiteDesignHarmonizer.php';",
    "require_once H18_CLEAN_DIR . 'src/Migration/SiteDesignHarmonizer.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/FormPageProvisioner.php';",
)
replace_once(
    PLUGIN,
    "    \\VisualDesignerManager\\Modules\\ModuleStore::register();",
    "    \\VisualDesignerManager\\Modules\\ModuleStore::register();\n    \\VisualDesignerManager\\Forms\\FormService::register();",
)
replace_once(
    PLUGIN,
    "    \\VisualDesignerManager\\Migration\\SiteDesignHarmonizer::register();",
    "    \\VisualDesignerManager\\Migration\\SiteDesignHarmonizer::register();\n    \\VisualDesignerManager\\Migration\\FormPageProvisioner::register();",
)

# Manager actions column CSS.
replace_once(
    ADMIN,
    "        wp_enqueue_style('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.css', ['h18-clean-manager-admin'], H18_CLEAN_VERSION);",
    "        wp_enqueue_style('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.css', ['h18-clean-manager-admin'], H18_CLEAN_VERSION);\n        wp_enqueue_style('h18-clean-manager-v0175', H18_CLEAN_URL . 'assets/admin-v0175.css', ['h18-clean-manager-v0123'], H18_CLEAN_VERSION);",
)

# Canonical form node types and props.
replace_once(
    LAYOUT,
    "['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail']",
    "['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail', 'contactform', 'membershipform']",
)
form_props = r'''        if (in_array($type, ['contactform', 'membershipform'], true)) {
            $membership = $type === 'membershipform';
            return array_merge([
                'heading' => sanitize_text_field((string) ($raw['heading'] ?? ($membership ? 'Bliv medlem' : 'Kontakt os'))),
                'intro' => sanitize_textarea_field((string) ($raw['intro'] ?? ($membership ? 'Udfyld formularen, så kontakter vi dig om medlemskab.' : 'Har du spørgsmål, er du velkommen til at kontakte os.'))),
                'buttonText' => sanitize_text_field((string) ($raw['buttonText'] ?? ($membership ? 'Send indmeldelse' : 'Send besked'))),
                'recipient' => sanitize_email((string) ($raw['recipient'] ?? '')),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#f4f1e8')) ?: '#f4f1e8',
                'fieldBackground' => sanitize_hex_color((string) ($raw['fieldBackground'] ?? '#ffffff')) ?: '#ffffff',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#30382a')) ?: '#30382a',
                'padding' => self::clamp($raw['padding'] ?? 24, 0, 80, 24),
                'radius' => self::clamp($raw['radius'] ?? 6, 0, 60, 6),
                'showPhone' => array_key_exists('showPhone', $raw) ? (bool) $raw['showPhone'] : true,
                'requireConsent' => array_key_exists('requireConsent', $raw) ? (bool) $raw['requireConsent'] : true,
            ], $border);
        }
'''
insert_before_once(LAYOUT, "        if ($type === 'image') {", form_props, "['contactform', 'membershipform']")

# Frontend rendering delegates forms to FormService.
replace_once(
    RENDERER,
    "use VisualDesignerManager\\Icons\\IconRegistry;",
    "use VisualDesignerManager\\Forms\\FormService;\nuse VisualDesignerManager\\Icons\\IconRegistry;",
)
form_render = r'''        if (in_array($type, ['contactform', 'membershipform'], true)) {
            return FormService::renderNode($type, $id, $props, $style . $borderStyle . $spacingStyle . $radiusStyle);
        }

'''
insert_before_once(RENDERER, "        if ($type === 'image') {", form_render, 'FormService::renderNode')

# Form styling: responsive, accessible and compatible with wp_mail/Simply hosting.
forms = read(FORMS)
if 'h18-vd-form-style-v0175' not in forms:
    forms = forms.replace(
        "$html = '<section id=\"h18-clean-' . esc_attr($nodeId) . '\" class=\"h18-clean-front-node h18-vd-form h18-vd-form--' . esc_attr($kind) . '\" style=\"' . esc_attr($style) . '\">';",
        "$html = self::style() . '<section id=\"h18-clean-' . esc_attr($nodeId) . '\" class=\"h18-clean-front-node h18-vd-form h18-vd-form--' . esc_attr($kind) . '\" style=\"' . esc_attr($style) . '\">';",
        1,
    )
    marker = "    private function __construct()\n"
    style_method = r'''    private static function style(): string
    {
        static $done = false;
        if ($done) { return ''; }
        $done = true;
        return '<style id="h18-vd-form-style-v0175">'
            . '.h18-vd-form{box-sizing:border-box;width:100%;border-radius:6px}.h18-vd-form h2{margin:0 0 8px}.h18-vd-form-intro{margin:0 0 20px}'
            . '.h18-vd-form-body{display:block}.h18-vd-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}'
            . '.h18-vd-form-field{display:flex;flex-direction:column;gap:6px;font-weight:600}.h18-vd-form-field.is-wide{grid-column:1/-1}'
            . '.h18-vd-form input,.h18-vd-form textarea{box-sizing:border-box;width:100%;border:1px solid #b8b8b2;border-radius:4px;background:var(--h18-form-field-bg);color:inherit;padding:11px 12px;font:inherit}'
            . '.h18-vd-form input:focus,.h18-vd-form textarea:focus{outline:2px solid var(--h18-form-accent);outline-offset:1px}'
            . '.h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0}.h18-vd-form-consent input{width:auto;margin-top:3px}'
            . '.h18-vd-form-submit{border:0;border-radius:4px;background:var(--h18-form-accent);color:#fff;padding:11px 20px;font:inherit;font-weight:700;cursor:pointer}'
            . '.h18-vd-form-submit:hover{filter:brightness(1.12)}.h18-vd-form-message{padding:10px 12px;border-radius:4px;font-weight:600}.h18-vd-form-message.is-success{background:#e9f5e7}.h18-vd-form-message.is-error{background:#f9e4e2}'
            . '.h18-vd-form-hp{position:absolute!important;left:-10000px!important;width:1px!important;height:1px!important;overflow:hidden!important}'
            . '@media(max-width:782px){.h18-vd-form-grid{grid-template-columns:1fr}.h18-vd-form-field.is-wide{grid-column:auto}}'
            . '</style>';
    }

'''
    if marker not in forms:
        raise SystemExit(f'{FORMS}: constructor marker missing')
    forms = forms.replace(marker, style_method + marker, 1)
    write(FORMS, forms)

# Palette groups in the page Designer.
editor = read(EDITOR)
if 'h18-vd-palette-group' not in editor:
    start = "        echo '<div class=\"h18-clean-workspace\">';\n        echo '<aside class=\"h18-clean-palette\"><h2>Elementer</h2>';\n"
    end = "        echo '<p class=\"description\">Klik tilføjer på root. Træk et palette-element direkte til root, Sektion eller Kasse. Eksisterende elementer flyttes med ✥.</p></aside>';\n"
    a = editor.find(start)
    b = editor.find(end, a)
    if a < 0 or b < 0:
        raise SystemExit(f'{EDITOR}: palette anchors missing')
    b += len(end)
    replacement = r'''        echo '<div class="h18-clean-workspace">';
        echo '<aside class="h18-clean-palette"><h2>Elementer</h2>';
        $paletteGroups = [
            'Basic' => [
                'section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede',
                'button' => 'Knap', 'link' => 'Link', 'spacer' => 'Mellemrum', 'divider' => 'Skillelinje',
                'icon' => 'Ikon', 'badge' => 'Badge', 'datalist' => 'Data List', 'table' => 'Tabel',
            ],
            'Moduler' => [
                'vehiclelist' => 'Køretøjsliste', 'vehicledetail' => 'Køretøjsdetalje',
                'eventlist' => 'Eventliste', 'eventdetail' => 'Eventdetalje',
                'gallerylist' => 'Gallerioversigt', 'gallerydetail' => 'Albumvisning',
            ],
            'Formularer' => [
                'contactform' => 'Kontaktformular', 'membershipform' => 'Bliv medlem-formular',
            ],
        ];
        foreach ($paletteGroups as $groupLabel => $elements) {
            echo '<details class="h18-vd-palette-group" open><summary>' . esc_html($groupLabel) . '</summary><div class="h18-vd-palette-group-items">';
            foreach ($elements as $type => $label) {
                echo '<button type="button" draggable="true" class="button h18-clean-add" data-type="' . esc_attr($type) . '">+ ' . esc_html($label) . '</button>';
            }
            echo '</div></details>';
        }
        echo '<p class="description">Klik tilføjer på root. Træk et palette-element direkte til root, Sektion eller Kasse. Eksisterende elementer flyttes med ✥.</p></aside>';
'''
    editor = editor[:a] + replacement + editor[b:]
    write(EDITOR, editor)

# Editor runtime: form types, preview, inspector and event end-of-day archive semantics.
js = read(EDITOR_JS)
js = js.replace(
    "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail'];",
    "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail', 'contactform', 'membershipform'];",
)
js = js.replace(
    "gallerylist:'Gallerioversigt',gallerydetail:'Albumvisning'",
    "gallerylist:'Gallerioversigt',gallerydetail:'Albumvisning',contactform:'Kontaktformular',membershipform:'Bliv medlem-formular'",
)
js = js.replace(
    "function eventIsPast(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const edge=String(fields.end||fields.start||''); if(!edge){return false;} const timestamp=Date.parse(edge); return Number.isFinite(timestamp)&&timestamp<Date.now(); }",
    "function eventIsPast(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; let edge=String(fields.end||''); if(!edge){const start=String(fields.start||''); if(!start){return false;} edge=start.slice(0,10)+'T23:59:59';} const timestamp=Date.parse(edge); return Number.isFinite(timestamp)&&timestamp<Date.now(); }",
)
if "if (type === 'contactform' || type === 'membershipform')" not in js:
    marker = "        if (type === 'image') {"
    pos = js.find(marker, js.find('function normalizeProps'))
    if pos < 0:
        raise SystemExit(f'{EDITOR_JS}: normalize image marker missing')
    form_js_props = r'''        if (type === 'contactform' || type === 'membershipform') {
            const membership = type === 'membershipform';
            return Object.assign(common, {
                heading:String(raw.heading || (membership ? 'Bliv medlem' : 'Kontakt os')),
                intro:String(raw.intro || (membership ? 'Udfyld formularen, så kontakter vi dig om medlemskab.' : 'Har du spørgsmål, er du velkommen til at kontakte os.')),
                buttonText:String(raw.buttonText || (membership ? 'Send indmeldelse' : 'Send besked')),
                recipient:String(raw.recipient || ''),
                background:normalizeColor(raw.background || '#f4f1e8'), fieldBackground:normalizeColor(raw.fieldBackground || '#ffffff'),
                textColor:normalizeColor(raw.textColor || '#30382a'), accentColor:normalizeColor(raw.accentColor || '#30382a'),
                padding:clamp(parseInt(raw.padding || 24,10)||24,0,80), radius:clamp(parseInt(raw.radius || 6,10)||6,0,60),
                showPhone:raw.showPhone !== false, requireConsent:raw.requireConsent !== false
            });
        }
'''
    js = js[:pos] + form_js_props + js[pos:]
js = js.replace(
    "gallerylist: 40, gallerydetail: 52 }",
    "gallerylist: 40, gallerydetail: 52, contactform: 54, membershipform: 74 }",
)

# Insert form preview before the image branch inside cardContent.
if "h18-vd-form-preview" not in js:
    card_start = js.find('function cardContent(node)')
    image_marker = "        } else if (node.type === 'image') {"
    pos = js.find(image_marker, card_start)
    if pos < 0:
        raise SystemExit(f'{EDITOR_JS}: cardContent image marker missing')
    preview = r'''        } else if (node.type === 'contactform' || node.type === 'membershipform') {
            wrap.classList.add('h18-clean-node-preview--form');
            const membership = node.type === 'membershipform';
            const box = document.createElement('div'); box.className = 'h18-vd-form-preview';
            box.style.background = node.props.background || '#f4f1e8'; box.style.color = node.props.textColor || '#30382a'; box.style.padding = String(node.props.padding || 24) + 'px'; box.style.borderRadius = String(node.props.radius || 6) + 'px';
            const h = document.createElement('h3'); h.textContent = String(node.props.heading || (membership ? 'Bliv medlem' : 'Kontakt os')); box.appendChild(h);
            const intro = document.createElement('p'); intro.textContent = String(node.props.intro || ''); if (intro.textContent) { box.appendChild(intro); }
            const fields = membership ? ['Navn *','E-mail *','Telefon *','Adresse *','Postnr. *','By *','Kommentar'] : ['Navn *','E-mail *','Telefon','Emne *','Besked *'];
            const grid = document.createElement('div'); grid.className = 'h18-vd-form-preview-grid';
            fields.forEach(function(label){const f=document.createElement('span');f.textContent=label;f.style.background=node.props.fieldBackground||'#ffffff';grid.appendChild(f);}); box.appendChild(grid);
            if (node.props.requireConsent !== false) { const consent=document.createElement('small'); consent.textContent='☐ Samtykke'; box.appendChild(consent); }
            const submit=document.createElement('strong'); submit.className='h18-vd-form-preview-submit'; submit.textContent=String(node.props.buttonText || (membership?'Send indmeldelse':'Send besked')); submit.style.background=node.props.accentColor||'#30382a'; box.appendChild(submit);
            wrap.appendChild(box);
'''
    js = js[:pos] + preview + js[pos + len("        }"):]

# Inspector labels + form inspector.
js = js.replace(
    "vehiclelist:'KØRETØJSLISTE',vehicledetail:'KØRETØJSDETALJE'",
    "vehiclelist:'KØRETØJSLISTE',vehicledetail:'KØRETØJSDETALJE',eventlist:'EVENTLISTE',eventdetail:'EVENTDETALJE',gallerylist:'GALLERIOVERSIGT',gallerydetail:'ALBUMVISNING',contactform:'KONTAKTFORMULAR',membershipform:'BLIV MEDLEM-FORMULAR'",
)
if "data-field=\"formRecipient\"" not in js:
    inspector_start = js.find('function renderInspector()')
    image_marker = "        } else if (node.type === 'image') {"
    pos = js.find(image_marker, inspector_start)
    if pos < 0:
        raise SystemExit(f'{EDITOR_JS}: inspector image marker missing')
    inspector = r'''        } else if (node.type === 'contactform' || node.type === 'membershipform') {
            const membership = node.type === 'membershipform';
            html += '<div class="h18-vd-menu-group"><h3>Formular</h3><label>Overskrift<input data-field="formHeading" type="text" value="' + escapeAttr(node.props.heading || (membership ? 'Bliv medlem' : 'Kontakt os')) + '"></label><label>Intro<textarea data-field="formIntro" rows="4">' + escapeHtml(node.props.intro || '') + '</textarea></label><label>Knaptekst<input data-field="formButtonText" type="text" value="' + escapeAttr(node.props.buttonText || (membership ? 'Send indmeldelse' : 'Send besked')) + '"></label><label>Modtager-e-mail <span class="description">(tom = WordPress admin-e-mail)</span><input data-field="formRecipient" type="email" value="' + escapeAttr(node.props.recipient || '') + '"></label><label class="h18-clean-checkbox"><input data-field="formShowPhone" type="checkbox"' + (node.props.showPhone !== false ? ' checked' : '') + '> Vis telefonfelt</label><label class="h18-clean-checkbox"><input data-field="formRequireConsent" type="checkbox"' + (node.props.requireConsent !== false ? ' checked' : '') + '> Kræv samtykke</label></div>';
            html += '<div class="h18-vd-menu-group"><h3>Design</h3><div class="h18-clean-field-grid"><label>Baggrund<input data-field="formBackground" type="color" value="' + escapeAttr(node.props.background || '#f4f1e8') + '"></label><label>Feltbaggrund<input data-field="formFieldBackground" type="color" value="' + escapeAttr(node.props.fieldBackground || '#ffffff') + '"></label><label>Tekst<input data-field="formTextColor" type="color" value="' + escapeAttr(node.props.textColor || '#30382a') + '"></label><label>Knap/accent<input data-field="formAccentColor" type="color" value="' + escapeAttr(node.props.accentColor || '#30382a') + '"></label><label>Padding<input data-field="formPadding" type="number" min="0" max="80" value="' + (node.props.padding || 24) + '"></label><label>Hjørner<input data-field="formRadius" type="number" min="0" max="60" value="' + (node.props.radius || 6) + '"></label></div></div>';
'''
    js = js[:pos] + inspector + js[pos + len("        }"):]

change_anchor = "                else if (field === 'galleryShowDescription') { current.props.showDescription=!!control.checked; }"
if "field === 'formRecipient'" not in js:
    if change_anchor not in js:
        raise SystemExit(f'{EDITOR_JS}: field change anchor missing')
    changes = change_anchor + r'''
                else if (field === 'formHeading') { current.props.heading=String(control.value||''); }
                else if (field === 'formIntro') { current.props.intro=String(control.value||''); }
                else if (field === 'formButtonText') { current.props.buttonText=String(control.value||'Send'); }
                else if (field === 'formRecipient') { current.props.recipient=String(control.value||'').trim(); }
                else if (field === 'formShowPhone') { current.props.showPhone=!!control.checked; }
                else if (field === 'formRequireConsent') { current.props.requireConsent=!!control.checked; }
                else if (field === 'formBackground') { current.props.background=normalizeColor(control.value||'#f4f1e8'); }
                else if (field === 'formFieldBackground') { current.props.fieldBackground=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'formTextColor') { current.props.textColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'formAccentColor') { current.props.accentColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'formPadding') { current.props.padding=clamp(parseInt(control.value||24,10)||24,0,80); }
                else if (field === 'formRadius') { current.props.radius=clamp(parseInt(control.value||6,10)||6,0,60); }'''
    js = js.replace(change_anchor, changes, 1)
write(EDITOR_JS, js)

# Palette/form preview styles piggyback on v0.1.75 admin CSS.
css = read(ADMIN_CSS)
extra_css = r'''
.h18-vd-palette-group{margin:0 0 10px;border:1px solid #dcdcde;border-radius:5px;background:#fff}
.h18-vd-palette-group>summary{cursor:pointer;padding:8px 10px;font-weight:700;color:#30382a}
.h18-vd-palette-group-items{display:grid;gap:6px;padding:0 8px 8px}.h18-vd-palette-group-items .button{width:100%;text-align:left}
.h18-vd-form-preview{display:flex;flex-direction:column;gap:9px;width:100%;height:100%;box-sizing:border-box;overflow:hidden}.h18-vd-form-preview h3,.h18-vd-form-preview p{margin:0}.h18-vd-form-preview-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.h18-vd-form-preview-grid span{border:1px solid #c9c9c3;border-radius:3px;padding:7px;font-size:11px}.h18-vd-form-preview-submit{align-self:flex-start;color:#fff;border-radius:3px;padding:7px 12px}
'''
if 'h18-vd-palette-group' not in css:
    write(ADMIN_CSS, css.rstrip() + '\n' + extra_css.lstrip())

# Optional event -> gallery relation.
replace_once(
    REGISTRY,
    "                    'description' => ['label' => 'Beskrivelse', 'type' => 'richtext', 'required' => false],\n                ],\n            ],\n            'galleries' => [",
    "                    'description' => ['label' => 'Beskrivelse', 'type' => 'richtext', 'required' => false],\n                    'galleryRecordId' => ['label' => 'Tilknyttet album', 'type' => 'text', 'required' => false],\n                ],\n            ],\n            'galleries' => [",
)

event_admin = read(EVENT_ADMIN)
if 'gallery_record_id' not in event_admin:
    event_admin = event_admin.replace(
        "$start = self::dateTimeInput((string) ($fields['start'] ?? '')); $end = self::dateTimeInput((string) ($fields['end'] ?? '')); $location = (string) ($fields['location'] ?? ''); $description = (string) ($fields['description'] ?? '');",
        "$start = self::dateTimeInput((string) ($fields['start'] ?? '')); $end = self::dateTimeInput((string) ($fields['end'] ?? '')); $location = (string) ($fields['location'] ?? ''); $description = (string) ($fields['description'] ?? ''); $galleryRecordId = sanitize_text_field((string) ($fields['galleryRecordId'] ?? '')); $galleryItems = ModuleStore::listRecords('galleries', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'title', 'order' => 'ASC']);",
        1,
    )
    event_admin = event_admin.replace(
        "        echo '<label><strong>Status</strong><select class=\"widefat\" name=\"status\">",
        "        echo '<label><strong>Tilknyttet album</strong><select class=\"widefat\" name=\"gallery_record_id\"><option value=\"\">Intet album</option>'; foreach ($galleryItems as $galleryItem) { $gallery = isset($galleryItem['record']) && is_array($galleryItem['record']) ? $galleryItem['record'] : []; $galleryId = (string) ($gallery['id'] ?? ''); if ($galleryId === '') { continue; } echo '<option value=\"' . esc_attr($galleryId) . '\"' . selected($galleryRecordId, $galleryId, false) . '>' . esc_html((string) ($gallery['title'] ?? 'Album')) . '</option>'; } echo '</select><span class=\"description\">Kan tilføjes eller ændres også efter eventet er afholdt.</span></label>';\n        echo '<label><strong>Status</strong><select class=\"widefat\" name=\"status\">",
        1,
    )
    event_admin = event_admin.replace(
        "'description' => wp_kses_post((string) wp_unslash($_POST['description'] ?? ''))]];",
        "'description' => wp_kses_post((string) wp_unslash($_POST['description'] ?? '')), 'galleryRecordId' => sanitize_text_field((string) wp_unslash($_POST['gallery_record_id'] ?? ''))]];",
        1,
    )
    write(EVENT_ADMIN, event_admin)

# Collection pages: natural-flow parity, search/sort, end-of-day archive, gallery relation.
write(COLLECTION, r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Modules\ModuleStore;

final class CollectionPageRenderer
{
    /** @return string|null */
    public static function render(int $postId): ?string
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        if (!in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true)) { return null; }
        $title = trim((string) get_the_title($postId));
        if ($title === '') { $title = $slug === 'events' ? 'Events' : ($slug === 'billedgalleri' ? 'Billedgalleri' : 'Køretøjer og materiel'); }
        if ($slug === 'events') {
            $detail = self::requestRecordId('h18_event');
            $body = $detail !== '' ? self::eventDetail($postId, $detail, $title) : self::events($postId, $title);
        } elseif ($slug === 'billedgalleri') {
            $detail = self::requestRecordId('h18_gallery');
            $body = $detail !== '' ? self::galleryDetail($postId, $detail, $title) : self::galleries($postId, $title);
        } else {
            $detail = self::requestRecordId('h18_vehicle');
            $body = $detail !== '' ? self::vehicleDetail($postId, $detail, $title) : self::vehicles($postId, $title);
        }
        return self::style() . $body;
    }

    public static function supports(int $postId): bool
    {
        return in_array(sanitize_title((string) get_post_field('post_name', $postId)), ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true);
    }

    private static function events(int $postId, string $title): string
    {
        $items = ModuleStore::listRecords('events', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'start', 'order' => 'ASC']);
        $records = self::records($items);
        $query = self::query();
        if ($query !== '') { $records = self::searchTitle($records, $query); }
        $sort = self::sortMode('events');
        self::sortEvents($records, $sort);
        $upcoming = []; $past = []; $now = current_time('timestamp');
        foreach ($records as $record) {
            $edge = self::eventArchiveEdge($record);
            if ($edge > 0 && $edge < $now) { $past[] = $record; } else { $upcoming[] = $record; }
        }
        $html = self::openPage('events', $title) . self::controls('events', $query, $sort);
        $html .= '<section class="h18-module-section"><h2>Kommende arrangementer</h2>' . self::eventGrid($postId, $upcoming, false, 'Ingen kommende arrangementer matcher søgningen.') . '</section>';
        $html .= '<section class="h18-module-section"><h2>Tidligere arrangementer</h2>' . self::eventGrid($postId, $past, true, 'Ingen tidligere arrangementer matcher søgningen.') . '</section>';
        return $html . '</main>';
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function eventGrid(int $postId, array $records, bool $past, string $empty): string
    {
        if (!$records) { return '<p class="h18-module-empty">' . esc_html($empty) . '</p>'; }
        $html = '<div class="h18-module-card-grid h18-module-event-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_event', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-event-card">' . self::image($record, 'h18-module-card-image', 480, 285);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Event')) . '</h3>';
            $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? ''));
            $location = trim((string) ($fields['location'] ?? ''));
            if ($meta !== '' || $location !== '') { $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>'; }
            $summary = trim((string) ($record['summary'] ?? '')); if ($summary !== '') { $html .= '<p>' . esc_html($summary) . '</p>'; }
            $html .= '<div class="h18-module-card-actions"><a class="h18-module-more" href="' . esc_url($url) . '">Læs mere →</a>';
            if ($past) { $html .= self::eventGalleryLink($fields); }
            $html .= '</div></div></article>';
        }
        return $html . '</div>';
    }

    private static function galleries(int $postId, string $title): string
    {
        $records = self::records(ModuleStore::listRecords('galleries', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'title', 'order' => 'ASC']));
        $query = self::query(); if ($query !== '') { $records = self::searchTitle($records, $query); }
        $sort = self::sortMode('galleries'); self::sortByTitle($records, $sort === 'name-desc');
        $html = self::openPage('galleries', $title) . self::controls('galleries', $query, $sort) . '<section class="h18-module-section"><h2>Køretøjer</h2>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen album matcher søgningen.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-gallery-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
            $cover = absint($record['featuredMediaId'] ?? 0); if ($cover <= 0 && $imageIds) { $cover = (int) $imageIds[0]; }
            $url = add_query_arg('h18_gallery', rawurlencode((string) ($record['id'] ?? '')), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-gallery-card">' . self::imageId($cover, (string) ($record['title'] ?? ''), 'h18-module-card-image', 480, 285);
            $html .= '<div class="h18-module-card-body"><h3><a href="' . esc_url($url) . '">' . esc_html((string) ($record['title'] ?? 'Album')) . '</a></h3>';
            $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-description">' . wp_kses_post($description) . '</div>'; }
            $count = count($imageIds); $html .= '<p class="h18-module-count"><strong>' . esc_html((string) $count) . ' ' . ($count === 1 ? 'billede' : 'billeder') . '</strong></p></div></article>';
        }
        return $html . '</div></section></main>';
    }

    private static function vehicles(int $postId, string $title): string
    {
        $records = self::records(ModuleStore::listRecords('vehicles', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'title', 'order' => 'ASC']));
        $query = self::query(); if ($query !== '') { $records = self::searchTitle($records, $query); }
        $sort = self::sortMode('vehicles'); self::sortByTitle($records, $sort === 'name-desc');
        $html = self::openPage('vehicles', $title) . self::controls('vehicles', $query, $sort);
        $html .= '<section class="h18-module-section"><h2>Historisk materiel</h2><p class="h18-module-intro">Her finder du foreningens dokumenterede køretøjer og øvrige militærhistoriske materiel.</p>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen køretøjer matcher søgningen.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-vehicle-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $url = add_query_arg('h18_vehicle', rawurlencode((string) ($record['id'] ?? '')), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-vehicle-card">' . self::image($record, 'h18-module-card-image', 480, 285);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Køretøj')) . '</h3>';
            $rows = []; $category = trim((string) ($fields['category'] ?? '')); if ($category !== '') { $rows[] = ['Type', $category]; }
            foreach (isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [] as $attribute) {
                if (!is_array($attribute) || empty($attribute['enabled'])) { continue; }
                $value = self::attributeValue($attribute['value'] ?? ''); if ($value === '') { continue; }
                $label = trim((string) ($attribute['label'] ?? $attribute['key'] ?? '')); if ($label === '' || (strcasecmp($label, 'Type') === 0 && $category !== '')) { continue; }
                $rows[] = [$label, $value];
            }
            if ($rows) { $html .= '<table class="h18-module-spec-table"><tbody>'; foreach (array_slice($rows, 0, 10) as $row) { $html .= '<tr><th>' . esc_html($row[0]) . '</th><td>' . esc_html($row[1]) . '</td></tr>'; } $html .= '</tbody></table>'; }
            $html .= '<a class="h18-module-more" href="' . esc_url($url) . '">Se køretøjet →</a></div></article>';
        }
        return $html . '</div></section></main>';
    }

    private static function eventDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('events', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $html = self::openPage('events detail', (string) ($record['title'] ?? $pageTitle));
        $html .= '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Events</a></p>' . self::image($record, 'h18-module-detail-image', 1200, 620);
        $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? '')); $location = trim((string) ($fields['location'] ?? ''));
        if ($meta !== '' || $location !== '') { $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>'; }
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        $html .= self::eventGalleryLink($fields);
        return $html . '</main>';
    }

    private static function galleryDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('galleries', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : []; $ids = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        $html = self::openPage('galleries detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Billedgalleri</a></p>';
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        $html .= '<div class="h18-module-image-grid">'; foreach ($ids as $imageId) { $html .= self::imageId($imageId, (string) ($record['title'] ?? ''), 'h18-module-gallery-image', 420, 280); }
        return $html . '</div></main>';
    }

    private static function vehicleDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('vehicles', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $html = self::openPage('vehicles detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Køretøjer</a></p>' . self::image($record, 'h18-module-detail-image', 1200, 620);
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        return $html . '</main>';
    }

    /** @param array<string,mixed> $fields */
    private static function eventGalleryLink(array $fields): string
    {
        $galleryId = strtolower(trim((string) ($fields['galleryRecordId'] ?? '')));
        if ($galleryId === '') { return ''; }
        $found = ModuleStore::findByRecordId('galleries', $galleryId);
        $gallery = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($gallery === null || (string) ($gallery['status'] ?? '') !== 'publish') { return ''; }
        $page = get_page_by_path('billedgalleri', OBJECT, 'page'); if (!$page instanceof \WP_Post) { return ''; }
        $url = add_query_arg('h18_gallery', rawurlencode($galleryId), get_permalink((int) $page->ID));
        return '<a class="h18-module-more h18-module-gallery-link" href="' . esc_url($url) . '">Se billeder →</a>';
    }

    /** @param array<int,array{postId:int,record:array<string,mixed>}> $items @return array<int,array<string,mixed>> */
    private static function records(array $items): array
    {
        $out = []; foreach ($items as $item) { $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : []; if ((string) ($record['status'] ?? '') === 'publish') { $out[] = $record; } } return $out;
    }

    private static function query(): string { return trim(sanitize_text_field((string) wp_unslash($_GET['h18_q'] ?? ''))); }

    private static function sortMode(string $module): string
    {
        $raw = sanitize_key((string) wp_unslash($_GET['h18_sort'] ?? ''));
        if ($module === 'events') { return in_array($raw, ['date', 'name', 'name-desc'], true) ? $raw : 'date'; }
        return in_array($raw, ['name', 'name-desc'], true) ? $raw : 'name';
    }

    /** @param array<int,array<string,mixed>> $records @return array<int,array<string,mixed>> */
    private static function searchTitle(array $records, string $query): array
    {
        if ($query === '') { return $records; }
        return array_values(array_filter($records, static function (array $record) use ($query): bool {
            $title = (string) ($record['title'] ?? '');
            return function_exists('mb_stripos') ? mb_stripos($title, $query, 0, 'UTF-8') !== false : stripos($title, $query) !== false;
        }));
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function sortEvents(array &$records, string $sort): void
    {
        usort($records, static function (array $a, array $b) use ($sort): int {
            if ($sort === 'name' || $sort === 'name-desc') {
                $cmp = strnatcasecmp((string) ($a['title'] ?? ''), (string) ($b['title'] ?? ''));
                return $sort === 'name-desc' ? -$cmp : $cmp;
            }
            $left = self::eventStart($a); $right = self::eventStart($b);
            if ($left === $right) { return strnatcasecmp((string) ($a['title'] ?? ''), (string) ($b['title'] ?? '')); }
            if ($left <= 0) { return 1; } if ($right <= 0) { return -1; } return $left <=> $right;
        });
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function sortByTitle(array &$records, bool $desc): void
    {
        usort($records, static function (array $a, array $b) use ($desc): int { $cmp = strnatcasecmp((string) ($a['title'] ?? ''), (string) ($b['title'] ?? '')); return $desc ? -$cmp : $cmp; });
    }

    private static function controls(string $module, string $query, string $sort): string
    {
        $placeholder = $module === 'events' ? 'Søg i events' : ($module === 'vehicles' ? 'Søg i køretøjer' : 'Søg i billedgalleri');
        $html = '<form class="h18-module-controls" method="get"><label class="h18-module-search"><span class="screen-reader-text">' . esc_html($placeholder) . '</span><input type="search" name="h18_q" value="' . esc_attr($query) . '" placeholder="' . esc_attr($placeholder) . '"></label>';
        $html .= '<label><span>Sortér</span><select name="h18_sort">';
        if ($module === 'events') { $html .= '<option value="date"' . selected($sort, 'date', false) . '>Dato – tidligste først</option>'; }
        $html .= '<option value="name"' . selected($sort, 'name', false) . '>Navn A–Å</option><option value="name-desc"' . selected($sort, 'name-desc', false) . '>Navn Å–A</option></select></label>';
        $html .= '<button type="submit">Søg / sortér</button>' . ($query !== '' || ($module === 'events' ? $sort !== 'date' : $sort !== 'name') ? '<a class="h18-module-reset" href="' . esc_url(remove_query_arg(['h18_q', 'h18_sort'])) . '">Nulstil</a>' : '') . '</form>';
        return $html;
    }

    /** @param array<string,mixed> $record */
    private static function eventArchiveEdge(array $record): int
    {
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $end = trim((string) ($fields['end'] ?? '')); if ($end !== '') { return self::dateTimeTimestamp($end); }
        $start = trim((string) ($fields['start'] ?? '')); if ($start === '') { return 0; }
        $date = substr($start, 0, 10); return self::dateTimeTimestamp($date . 'T23:59:59');
    }

    /** @param array<string,mixed> $record */
    private static function eventStart(array $record): int
    {
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : []; return self::dateTimeTimestamp((string) ($fields['start'] ?? ''));
    }

    private static function dateTimeTimestamp(string $value): int
    {
        $value = trim($value); if ($value === '') { return 0; }
        $tz = wp_timezone(); $dt = \DateTimeImmutable::createFromFormat('!Y-m-d\\TH:i:s', $value, $tz);
        if (!$dt) { $dt = \DateTimeImmutable::createFromFormat('!Y-m-d\\TH:i', $value, $tz); }
        return $dt ? $dt->getTimestamp() : 0;
    }

    private static function eventDateLabel(string $start, string $end): string
    {
        $startTs = self::dateTimeTimestamp($start); $endTs = self::dateTimeTimestamp($end); if ($startTs <= 0) { return ''; }
        $startLabel = wp_date('j. F Y · H:i', $startTs); if ($endTs <= 0) { return $startLabel; }
        if (wp_date('Y-m-d', $startTs) === wp_date('Y-m-d', $endTs)) { return $startLabel . '–' . wp_date('H:i', $endTs); }
        return $startLabel . ' – ' . wp_date('j. F Y · H:i', $endTs);
    }

    private static function requestRecordId(string $key): string
    {
        $value = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET[$key] ?? '')))); return preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $value) ? $value : '';
    }

    /** @param array<string,mixed> $record */
    private static function image(array $record, string $class, int $width, int $height): string { return self::imageId(absint($record['featuredMediaId'] ?? 0), (string) ($record['title'] ?? ''), $class, $width, $height); }

    private static function imageId(int $id, string $alt, string $class, int $width, int $height): string
    {
        if ($id <= 0) { return ''; }
        $url = wp_get_attachment_image_url($id, 'large'); if (!is_string($url) || $url === '') { return ''; }
        return '<img class="' . esc_attr($class) . '" src="' . esc_url($url) . '" alt="' . esc_attr($alt) . '" loading="lazy" width="' . esc_attr((string) $width) . '" height="' . esc_attr((string) $height) . '">';
    }

    private static function attributeValue($value): string
    {
        if (is_bool($value)) { return $value ? 'Ja' : 'Nej'; } if (is_scalar($value)) { return trim((string) $value); } return '';
    }

    private static function notFound(int $postId, string $pageTitle): string { return self::openPage('detail', $pageTitle) . '<p>Indholdet findes ikke eller er ikke publiceret.</p><p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage</a></p></main>'; }
    private static function openPage(string $class, string $title): string { return '<main class="h18-module-page h18-module-page--' . esc_attr(sanitize_html_class($class)) . '"><h1>' . esc_html($title) . '</h1>'; }

    private static function style(): string
    {
        return '<style id="h18-module-page-style-v0175">'
            . '.h18-module-page{width:90%;max-width:1440px;margin:0 auto;padding:34px 0 54px;color:#30382a;box-sizing:border-box}.h18-module-page h1{margin:0 0 28px;font-size:clamp(30px,3vw,44px);line-height:1.08}.h18-module-section{margin:0 0 42px}.h18-module-section h2{margin:0 0 18px;font-size:clamp(23px,2vw,31px)}'
            . '.h18-module-intro{margin:-7px 0 20px;max-width:850px}.h18-module-card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:26px;align-items:start}.h18-module-card{background:#f4f1e8;border-radius:7px;overflow:hidden;box-shadow:0 1px 0 rgba(0,0,0,.06);min-width:0}.h18-module-card-image{display:block;width:100%;height:220px;object-fit:cover}.h18-module-card-body{padding:20px}.h18-module-card h3{font-size:22px;line-height:1.15;margin:0 0 10px}.h18-module-card h3 a{color:inherit;text-decoration:none}.h18-module-card p{margin:8px 0}.h18-module-meta{font-size:14px}.h18-module-more{font-weight:700;color:#536243;text-decoration:none}.h18-module-card-actions{display:flex;flex-wrap:wrap;gap:12px 20px;margin-top:14px}.h18-module-description>*:first-child{margin-top:0}.h18-module-description>*:last-child{margin-bottom:0}'
            . '.h18-module-spec-table{width:100%;border-collapse:collapse;margin:14px 0}.h18-module-spec-table th,.h18-module-spec-table td{padding:7px 8px;border-bottom:1px solid rgba(48,56,42,.16);text-align:left;vertical-align:top}.h18-module-spec-table th{width:45%;font-weight:700}.h18-module-count{font-size:14px}.h18-module-detail-image{display:block;width:min(100%,1100px);max-height:620px;object-fit:cover;border-radius:7px;margin:15px 0 20px}.h18-module-detail-text{max-width:950px;margin:18px 0}.h18-module-back{font-weight:700;text-decoration:none;color:#536243}.h18-module-image-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:24px}.h18-module-gallery-image{display:block;width:100%;height:260px;object-fit:cover;border-radius:5px}'
            . '.h18-module-controls{display:flex;align-items:end;gap:12px;flex-wrap:wrap;margin:-8px 0 30px;padding:14px 16px;background:#f4f1e8;border-radius:7px}.h18-module-controls label{display:flex;flex-direction:column;gap:5px;font-weight:700}.h18-module-search{flex:1 1 300px}.h18-module-controls input,.h18-module-controls select{min-height:40px;border:1px solid #aaa99f;border-radius:4px;background:#fff;padding:7px 10px;font:inherit}.h18-module-controls button{min-height:40px;border:0;border-radius:4px;padding:8px 16px;background:#30382a;color:#fff;font-weight:700;cursor:pointer}.h18-module-reset{padding:9px 4px;font-weight:700;color:#536243}.h18-module-empty{padding:18px;background:#f4f1e8;border-radius:6px}'
            . '@media(max-width:980px){.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.h18-module-page{width:92%;padding-top:24px}.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:1fr}.h18-module-card-image{height:auto;aspect-ratio:16/10}.h18-module-controls{align-items:stretch}.h18-module-controls label,.h18-module-controls button{width:100%}.h18-module-gallery-image{height:auto;aspect-ratio:4/3}}'
            . '</style>';
    }

    private function __construct() {}
}
''')

# Release history.
history = json.loads(read(HISTORY))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not versions or str(versions[0].get('version', '')) != '0.1.75':
    versions.insert(0, {
        'version': '0.1.75',
        'date': '2026-09-01',
        'items': [
            'FORM-001..006: fælles kontakt-/medlemsformularer, validering, spam-honeypot, wp_mail og kvitteringsmail.',
            'Kontakt og Bliv medlem klargøres automatisk som Visual Designer-sider med de relevante formularer.',
            'Events har tidligste dato først som standard, automatisk tidligere-event regel efter sluttid eller kl. 23:59:59 samt valgfri albumkobling.',
            'Events og Køretøjer kan søges på navn; Billedgalleri kan søges på albumnavn; køretøjer og album sorterer A–Å som standard.',
            'Designer-paletten er opdelt i Basic, Moduler og Formularer, og Sider/Handlinger har mere plads på desktop.',
            'Modulkort er visuelt harmoniseret tættere på _old-referencerne med ens spacing, billeder og tre-kolonne desktop-flow.'
        ],
    })
    history['versions'] = versions
    write(HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write(NOTES, '''<h2>0.1.75 – Formularer, søgning og eventarkiv</h2>
<ul>
<li><strong>Formularer:</strong> Kontaktformular og Bliv medlem-formular er canonical Visual Designer-elementer med validering, samtykke, spam-honeypot, <code>wp_mail()</code> og kvittering.</li>
<li>Siderne <strong>Kontakt</strong> (<code>kontakt</code>) og <strong>Bliv medlem</strong> (<code>bliv-medlem</code>) oprettes/klargøres automatisk uden at overskrive eksisterende Designer-elementer.</li>
<li><strong>Events:</strong> standard er tidligste dato først. Eventet flytter automatisk til Tidligere arrangementer efter sluttid; uden sluttid først ved dagens udløb.</li>
<li>Et event kan valgfrit kobles til et publiceret billedalbum og vise <strong>Se billeder →</strong>, også efter eventet er afholdt.</li>
<li><strong>Søgning:</strong> Events og Køretøjer kan søges på navn; Billedgalleri kan søges på albumnavn. Køretøjer og album sorterer A–Å som standard.</li>
<li>Elementpaletten er opdelt i <strong>Basic</strong>, <strong>Moduler</strong> og <strong>Formularer</strong>. Handlinger-kolonnen på Sider har mere desktop-plads.</li>
<li>Events, Billedgalleri og Køretøjer har et mere ensartet tre-kolonne kortlayout tættere på de originale <code>_old</code>-referencer.</li>
</ul>
''')

backlog = read(BACKLOG)
backlog = backlog.replace('**Aktuel release:** v0.1.74', '**Aktuel release:** v0.1.75')
if 'v0.1.75 – Formularer, søgning og eventarkiv' not in backlog:
    roadmap_anchor = '6. **v0.1.74 – Modul-cutover — FÆRDIG:** de tre dynamiske samlingssider følger `_old`-layoutet og har flow-højde; versionshistorik og Save-feedback er rettet.\n'
    roadmap_new = roadmap_anchor + '7. **v0.1.75 – Formularer, søgning og eventarkiv — FÆRDIG:** Kontakt/Bliv medlem-formularer, sideprovisionering, søgning/sortering, event→album og end-of-day arkivregel.\n'
    if roadmap_anchor in backlog:
        backlog = backlog.replace(roadmap_anchor, roadmap_new, 1)
    else:
        backlog += '\n\n## v0.1.75\n- Formularer, søgning/sortering og eventarkiv implementeret.\n'
write(BACKLOG, backlog)

write(STATUS, '''# Visual Designer Manager v0.1.75 – status

**Dato:** 1. september 2026  
**Status:** Implementation candidate; release kræver grøn v0.1.75 QA og central ZIP/manifest-build.

## Scope
- Kontaktformular og Bliv medlem-formular som canonical Designer-elementer.
- Automatisk klargøring af `kontakt` og `bliv-medlem`.
- Events: kronologisk standard, end-of-day fallback ved manglende sluttid og valgfri event→album relation.
- Søgning/sortering på Events, Køretøjer og Billedgalleri.
- Palettegrupper: Basic, Moduler, Formularer.
- Bredere Handlinger-kolonne og forbedret modul-kortparitet.

## Bevidst ikke i v0.1.75
- Event → deltagende køretøjer.
- Forside-teasers / Bliv medlem CTA.
- Billed-tags og søgning på tværs af album.
- Køretøjskategorifilter.

Disse ligger fortsat på `docs/clean-ideas.md`.
''')

print('Applied Visual Designer Manager v0.1.75 source candidate.')
