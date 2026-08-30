from pathlib import Path
import json

ROOT = Path('.')
PLUGIN_ROOT = ROOT / 'clean/hangar18-manager'
TEMPLATES = PLUGIN_ROOT / 'src/Model/TemplateLayoutModel.php'
EDITOR_CONTROLLER = PLUGIN_ROOT / 'src/Admin/EditorController.php'
GLOBAL_CONTROLLER = PLUGIN_ROOT / 'src/Admin/GlobalDesignerController.php'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
NOTES = ROOT / 'clean-release-notes.html'
HISTORY = PLUGIN_ROOT / 'release-history.json'
HF_SPEC = ROOT / 'docs/HEADER-FOOTER-SPEC.md'
BACKLOG = ROOT / 'docs/clean-backlog-v0100.md'
STATUS = ROOT / 'docs/v0161-status.md'
RELEASE_WORKFLOW = ROOT / '.github/workflows/visual-designer-release.yml'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


def append_once(text: str, marker: str, block: str) -> str:
    return text if marker in text else text.rstrip() + '\n\n' + block.strip() + '\n'


# Shared, active-only resolver contract.
templates = TEMPLATES.read_text(encoding='utf-8')
default_old = """        if ($id !== '' && self::exists($id, $type)) {
            return $id;
        }
"""
default_new = """        if ($id !== '' && self::exists($id, $type)) {
            $meta = self::meta($id);
            if ($meta && !empty($meta['active'])) {
                return $id;
            }
        }
"""
templates = replace_once(templates, default_old, default_new, 'inactive default exclusion')
resolve_old = """    public static function resolveId(int $postId, string $type): string
    {
        $type = self::type($type);
        $choice = self::pageChoice($postId, $type);
        if ($choice === 'none') {
            return '';
        }
        if ($choice !== 'auto') {
            $meta = self::meta($choice);
            if ($meta && !empty($meta['active'])) {
                return $choice;
            }
        }
        $default = self::defaultId($type);
        $meta = $default !== '' ? self::meta($default) : null;
        return $meta && !empty($meta['active']) ? $default : '';
    }
"""
resolve_new = """    public static function resolveChoiceId(string $type, string $choice): string
    {
        $type = self::type($type);
        $choice = sanitize_key($choice);
        if ($choice === 'none') {
            return '';
        }
        if ($choice !== '' && $choice !== 'auto') {
            $meta = self::meta($choice);
            if ($meta && ($meta['type'] ?? '') === $type && !empty($meta['active'])) {
                return $choice;
            }
        }
        $default = self::defaultId($type);
        $meta = $default !== '' ? self::meta($default) : null;
        return $meta && !empty($meta['active']) ? $default : '';
    }

    public static function resolveId(int $postId, string $type): string
    {
        $type = self::type($type);
        return self::resolveChoiceId($type, self::pageChoice($postId, $type));
    }
"""
templates = replace_once(templates, resolve_old, resolve_new, 'shared Header Footer resolver')
TEMPLATES.write_text(templates, encoding='utf-8')


# Page Designer and composite Preview use the same Header/Footer resolver as frontend.
controller = EDITOR_CONTROLLER.read_text(encoding='utf-8')
controller = replace_once(
    controller,
    '<span class="description">Header og Footer vælges uafhængigt. Frontend-overtagelse aktiveres først med Theme-shell.</span>',
    '<span class="description">Header og Footer vælges uafhængigt. Theme-shell er aktiv på Visual Designer-sider; Automatisk bruger den aktive website-standard.</span>',
    'page Header Footer shell status text'
)
preview_old = """        if ($choice === 'none') { return null; }
        $id = $choice !== '' && $choice !== 'auto' && TemplateLayoutModel::exists($choice, $part)
            ? $choice
            : TemplateLayoutModel::defaultId($part);
        if ($id === '' || !TemplateLayoutModel::exists($id, $part)) { return null; }
        return TemplateLayoutModel::model($id);
"""
preview_new = """        $id = TemplateLayoutModel::resolveChoiceId($part, $choice);
        if ($id === '' || !TemplateLayoutModel::exists($id, $part)) { return null; }
        return TemplateLayoutModel::model($id);
"""
controller = replace_once(controller, preview_old, preview_new, 'preview shared Header Footer resolver')
EDITOR_CONTROLLER.write_text(controller, encoding='utf-8')


# Header/Footer Manager now reports the actual production state.
global_controller = GLOBAL_CONTROLLER.read_text(encoding='utf-8')
global_controller = replace_once(
    global_controller,
    '<span class="h18-manager-badge is-progress">Under udvikling</span>',
    '<span class="h18-manager-badge is-ok">Færdig</span>',
    'Header Footer completed badge'
)
global_controller = replace_once(
    global_controller,
    '<p class="description">Theme-shell overtager endnu ikke frontend automatisk. Først tester vi templates og resolver uden risiko for dobbelt Header/Footer.</p>',
    '<p class="description">Theme-shell er aktiv på Visual Designer-sider. Header/Footer resolveren bruger sidevalg → aktiv website-standard → sikker tom fallback og deles med Preview.</p>',
    'Header Footer shell completed text'
)
GLOBAL_CONTROLLER.write_text(global_controller, encoding='utf-8')


# Authoritative Header/Footer specification: close the baseline explicitly.
hf = HF_SPEC.read_text(encoding='utf-8')
hf = replace_once(
    hf,
    '**Statusdato:** 26. august 2026  \n**Status:** Godkendt målarkitektur under implementation  ',
    '**Statusdato:** 30. august 2026  \n**Status:** FÆRDIG baseline · v0.1.61  ',
    'Header Footer spec status'
)
hf_closure = r'''## 15. Baseline lukket i v0.1.61

Multi-template Header/Footer er markeret **FÆRDIG** som produktionsbaseline i v0.1.61.

Definition of Done i afsnit 14 er nu en permanent regression gate og verificeres af `.github/scripts/v0161_header_footer_qa.php` samt release-workflowen:

- flere samtidige Header- og Footer-templates;
- stabilt template-ID, omdøbning og duplikering;
- uafhængig versionshistorik;
- aktiv website-standard Header og Footer;
- uafhængigt sidevalg med `Automatisk`, konkret template og `Ingen`;
- én delt deterministisk resolver for frontend og composite Preview;
- inaktive templates vælges ikke automatisk;
- fase-1 Header/Footer migreres til `Header – Standard` / `Footer – Standard` uden model- eller versionstab.

Assignment-regler, Export/Import, anvendelsestællere og nye generelle elementtyper som Ikon/Divider/Spacer er fremtidige udvidelser og genåbner ikke den afsluttede Header/Footer-baseline. Fejl i ovenstående Definition of Done gør derimod milepælen rød igen.'''
hf = append_once(hf, '## 15. Baseline lukket i v0.1.61', hf_closure)
HF_SPEC.write_text(hf, encoding='utf-8')


# Canonical backlog gets a current status block instead of rewriting historical detail.
backlog = BACKLOG.read_text(encoding='utf-8')
backlog = replace_once(backlog, '**Statusdato:** 25. august 2026  ', '**Statusdato:** 30. august 2026  ', 'canonical backlog date')
current_status = r'''## Aktuel milepælsstatus · v0.1.61

- **HEADER/FOOTER — FÆRDIG:** multi-template baseline, side-overrides, `Ingen`, standardvalg, migration, versionshistorik og delt Preview/frontend-resolver er lukket som regression-gate.
- **VD-KEYBOARD-001 — IMPLEMENTERET:** markeret element kan finjusteres 1 px med piletaster og 10 px med `Shift + pil`; offset X/Y er canonical og kan nulstilles i Inspector.
- **VD-CLIPBOARD-001 — IMPLEMENTERET:** `Ctrl/Cmd+C`, `Ctrl/Cmd+V` og `Ctrl/Cmd+D`, subtree-kopi af Kasse/Sektion, nye IDs/parentId-remap og clipboard mellem Designer-sider.
- **Næste generelle elementpakke:** Spacer, Divider, Ikon og Tabel/Dataliste. Dynamiske Køretøjer/Events/Billedgalleri følger derefter den separate modularkitektur.
'''
if '## Aktuel milepælsstatus · v0.1.61' not in backlog:
    backlog = backlog.replace('## Formål\n', current_status + '\n## Formål\n', 1)
BACKLOG.write_text(backlog, encoding='utf-8')


# Technical contracts.
tech = TECH.read_text(encoding='utf-8')
tech_block = r'''## 0.1.61 – Keyboard, Clipboard og Header/Footer baseline

### VD-KEYBOARD-001
- Et markeret Designer-element kan finjusteres visuelt uden at ændre 120-unit-gridpositionen.
- `Pil` ændrer canonical `offsetX`/`offsetY` med 1 px; `Shift + pil` ændrer med 10 px.
- Offset er begrænset til ±2000 px og renderes identisk i Designer og frontend via `transform: translate(...)`.
- Gentagne piletastetryk indtil keyup grupperes som én Undo/Redo-transaktion.
- Tastaturgenveje må ikke overtage piletaster/Ctrl-genveje når fokus står i input, textarea, select eller contenteditable.

### VD-CLIPBOARD-001
- `Ctrl/Cmd+C` kopierer valgt element; `Ctrl/Cmd+V` indsætter; `Ctrl/Cmd+D` duplikerer uden at overskrive clipboard.
- Kasse/Sektion kopieres som komplet subtree med alle descendants.
- Ved indsættelse oprettes nye unikke element-ID'er, og interne `parentId`-referencer remappes til de nye IDs.
- Clipboard lagres bruger-specifikt i browserens localStorage og overlever navigation mellem Visual Designer-sider på samme website; der findes in-memory fallback.
- Root for en indsættelse placeres på næste frie Y-position i mål-parenten, mens subtree-intern geometri, props, billeder, links og styling bevares.
- Indsæt/Duplikér er én Undo/Redo-transaktion.

### VD-HEADER-FOOTER-COMPLETE-001
- Multi-template Header/Footer baseline er FÆRDIG fra v0.1.61.
- `TemplateLayoutModel::resolveChoiceId()` er fælles resolverkontrakt for frontend og composite Preview.
- Inaktiv stored default ignoreres; resolveren falder deterministisk tilbage til første aktive template eller tom fallback.
- `Ingen Header/Footer` stopper resolveren eksplicit.
- `.github/scripts/v0161_header_footer_qa.php` er permanent Definition-of-Done regression gate.'''
tech = append_once(tech, '### VD-KEYBOARD-001', tech_block)
TECH.write_text(tech, encoding='utf-8')


# Release notes/history/status.
notes = NOTES.read_text(encoding='utf-8')
release_notes = '<h4>0.1.61 – Keyboard, Clipboard og Header/Footer færdig</h4><ul><li><strong>VD-KEYBOARD-001:</strong> Markerede elementer kan flyttes 1 px med piletaster og 10 px med Shift + piletast uden at ændre grid-positionen.</li><li><strong>VD-CLIPBOARD-001:</strong> Ctrl/Cmd+C, Ctrl/Cmd+V og Ctrl/Cmd+D understøtter enkelt-elementer samt komplette Kasse/Sektion-subtrees og virker mellem Designer-sider.</li><li>Indsatte elementer får nye unikke IDs og remappede parentId-relationer; Undo/Redo bevares som én transaktion.</li><li><strong>Header/Footer: FÆRDIG baseline.</strong> Preview og frontend bruger nu samme resolver, og inaktive defaults/templates vælges ikke automatisk.</li><li>Header/Footer Definition of Done er lagt ind som permanent QA/release-gate.</li></ul>\n'
if not notes.startswith('<h4>0.1.61'):
    notes = release_notes + notes
NOTES.write_text(notes, encoding='utf-8')

history_data = json.loads(HISTORY.read_text(encoding='utf-8'))
if not isinstance(history_data, dict):
    raise SystemExit('release-history.json has unexpected top-level format')
versions = history_data.setdefault('versions', [])
if not versions or versions[0].get('version') != '0.1.61':
    versions.insert(0, {
        'version': '0.1.61',
        'date': '2026-08-30',
        'items': [
            'VD-KEYBOARD-001: Pil flytter valgt element 1 px visuelt; Shift+pil flytter 10 px via canonical offsetX/offsetY.',
            'VD-CLIPBOARD-001: Ctrl/Cmd+C, V og D understøtter subtree-kopi, cross-page clipboard, nye IDs og parentId-remap.',
            'Piletastsekvenser og Paste/Duplicate er grupperede Undo/Redo-transaktioner.',
            'Header/Footer multi-template baseline er markeret FÆRDIG.',
            'Preview og frontend deler resolveChoiceId; inaktive defaults/templates vælges ikke automatisk.',
            'Header/Footer Definition of Done er permanent release-regression gate.'
        ],
    })
HISTORY.write_text(json.dumps(history_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

STATUS.parent.mkdir(parents=True, exist_ok=True)
STATUS.write_text('''# Visual Designer Manager 0.1.61 status\n\n## Keyboard / pixel-finjustering\n- Pil = 1 px via canonical offsetX/offsetY.\n- Shift + pil = 10 px.\n- Offset kan redigeres/nulstilles i Inspector.\n- Grid x/y/w/h ændres ikke af pixel-finjustering.\n- Piletastsekvens grupperes til én Undo/Redo-transaktion.\n\n## Clipboard\n- Ctrl/Cmd+C = Kopiér.\n- Ctrl/Cmd+V = Indsæt.\n- Ctrl/Cmd+D = Duplikér.\n- Kasse/Sektion kopierer hele subtree.\n- Nye IDs genereres, parentId remappes, og indsætning virker mellem Designer-sider via bruger-specifikt browser-clipboard.\n\n## Header/Footer\n- Status: FÆRDIG baseline.\n- Definition of Done verificeres af `.github/scripts/v0161_header_footer_qa.php`.\n- Shared `resolveChoiceId()` bruges til frontend og composite Preview.\n- Inaktive defaults/templates vælges ikke automatisk.\n- `Ingen Header/Footer`, side override, standardvalg, multi-template og fase-1 migration er regressionsgates.\n\n## Uden for denne afsluttede baseline\n- Assignment-regler, Export/Import og nye generelle elementtyper er separate fremtidige udvidelser.\n''', encoding='utf-8')


# Make the completed Header/Footer contract and new productivity functions permanent release gates.
workflow = RELEASE_WORKFLOW.read_text(encoding='utf-8')
qa_old = """          php .github/scripts/hierarchy_normalizer_qa.php
          php .github/scripts/v0125_model_qa.php
"""
qa_new = """          php .github/scripts/hierarchy_normalizer_qa.php
          php .github/scripts/v0125_model_qa.php
          php .github/scripts/v0161_header_footer_qa.php
          grep -Fq 'VD-KEYBOARD-001' CLEAN-TECHNICAL-MANUAL.md
          grep -Fq 'VD-CLIPBOARD-001' CLEAN-TECHNICAL-MANUAL.md
          grep -Fq \"const CLIPBOARD_KEY = 'h18-vd-clipboard-v1-u'\" clean/hangar18-manager/assets/editor-v018-core.js
          grep -Fq 'function nudgeSelected' clean/hangar18-manager/assets/editor-v018-core.js
          grep -Fq 'function pastePayload' clean/hangar18-manager/assets/editor-v018-core.js
          grep -Fq \"'offsetX' => self::clamp\" clean/hangar18-manager/src/Model/LayoutModel.php
          grep -Fq 'transform:translate(' clean/hangar18-manager/src/Frontend/Renderer.php
          grep -Fq 'public static function resolveChoiceId' clean/hangar18-manager/src/Model/TemplateLayoutModel.php
          grep -Fq 'h18-manager-badge is-ok\">Færdig' clean/hangar18-manager/src/Admin/GlobalDesignerController.php
"""
workflow = replace_once(workflow, qa_old, qa_new, 'permanent v0161 regression gates')
RELEASE_WORKFLOW.write_text(workflow, encoding='utf-8')

print('Applied v0.1.61 Header/Footer completion, docs and release metadata patch.')
