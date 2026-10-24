from pathlib import Path
import json
import shutil
import subprocess

VERSION = '3.0.0-alpha.42'
DEST = Path('build/visual-designer-manager')
ASSET_ROOT = Path('.github/release-assets/alpha42')

subprocess.run(['python3', '.github/scripts/build_v3_alpha41.py'], check=True)


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Version cutover.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.41', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.41');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.41');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.42 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Canonical metadata fields used only by Designer productivity features.
# They are harmless to the frontend renderer, but persistence is required for
# labels, lock/hide, linked components and Design Token references.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v018-core.js',
    """            offsetX: clamp(parseInt(raw.offsetX || 0, 10) || 0, -2000, 2000),
            offsetY: clamp(parseInt(raw.offsetY || 0, 10) || 0, -2000, 2000)
        };
""",
    """            offsetX: clamp(parseInt(raw.offsetX || 0, 10) || 0, -2000, 2000),
            offsetY: clamp(parseInt(raw.offsetY || 0, 10) || 0, -2000, 2000),
            suiteLabel: String(raw.suiteLabel || '').slice(0, 120),
            suiteHidden: !!raw.suiteHidden,
            suiteLocked: !!raw.suiteLocked,
            suiteComponentId: String(raw.suiteComponentId || '').replace(/[^a-z0-9_-]/gi, '').slice(0, 80).toLowerCase(),
            suiteComponentVersion: clamp(parseInt(raw.suiteComponentVersion || 0, 10) || 0, 0, 100000),
            suiteTokenBackground: String(raw.suiteTokenBackground || '').replace(/[^a-z0-9_-]/gi, '').slice(0, 60).toLowerCase(),
            suiteTokenText: String(raw.suiteTokenText || '').replace(/[^a-z0-9_-]/gi, '').slice(0, 60).toLowerCase(),
            suiteTokenRadius: String(raw.suiteTokenRadius || '').replace(/[^a-z0-9_-]/gi, '').slice(0, 60).toLowerCase(),
            suiteTokenSpacing: String(raw.suiteTokenSpacing || '').replace(/[^a-z0-9_-]/gi, '').slice(0, 60).toLowerCase(),
            suiteTokenFont: String(raw.suiteTokenFont || '').replace(/[^a-z0-9_-]/gi, '').slice(0, 60).toLowerCase()
        };
""",
    'Alpha.42 JS suite metadata persistence'
)

replace_once(
    'src/Model/LayoutModel.php',
    """            'offsetX' => self::clamp($raw['offsetX'] ?? 0, -2000, 2000, 0),
            'offsetY' => self::clamp($raw['offsetY'] ?? 0, -2000, 2000, 0),
        ];
""",
    """            'offsetX' => self::clamp($raw['offsetX'] ?? 0, -2000, 2000, 0),
            'offsetY' => self::clamp($raw['offsetY'] ?? 0, -2000, 2000, 0),
            'suiteLabel' => sanitize_text_field((string) ($raw['suiteLabel'] ?? '')),
            'suiteHidden' => !empty($raw['suiteHidden']),
            'suiteLocked' => !empty($raw['suiteLocked']),
            'suiteComponentId' => sanitize_key((string) ($raw['suiteComponentId'] ?? '')),
            'suiteComponentVersion' => self::clamp($raw['suiteComponentVersion'] ?? 0, 0, 100000, 0),
            'suiteTokenBackground' => sanitize_key((string) ($raw['suiteTokenBackground'] ?? '')),
            'suiteTokenText' => sanitize_key((string) ($raw['suiteTokenText'] ?? '')),
            'suiteTokenRadius' => sanitize_key((string) ($raw['suiteTokenRadius'] ?? '')),
            'suiteTokenSpacing' => sanitize_key((string) ($raw['suiteTokenSpacing'] ?? '')),
            'suiteTokenFont' => sanitize_key((string) ($raw['suiteTokenFont'] ?? '')),
        ];
""",
    'Alpha.42 PHP suite metadata persistence'
)

# ---------------------------------------------------------------------------
# Extend the canonical editor bridge. Every Suite mutation therefore uses the
# same normalize/commit/render/Undo path as ordinary Designer operations.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v018-core.js',
    """    window.H18VDDesigner = Object.assign(window.H18VDDesigner || {}, {
        selectNode: function (id) {
            var node = nodeById(cleanId(id));
            if (!node) { return false; }
            selectedId = node.id;
            render();
            return true;
        },
        selectedId: function () { return selectedId || ''; }
    });
""",
    """    window.H18VDDesigner = Object.assign(window.H18VDDesigner || {}, {
        selectNode: function (id) {
            var node = nodeById(cleanId(id));
            if (!node) { return false; }
            selectedId = node.id;
            render();
            return true;
        },
        selectedId: function () { return selectedId || ''; },
        getModel: function () { return clone(state); },
        node: function (id) { var node = nodeById(cleanId(id)); return node ? clone(node) : null; },
        descendants: function (id) { return descendants(cleanId(id)).slice(); },
        history: function () { return undoStack.map(function (entry) { return entry.label; }); },
        undo: function () { undo(); return clone(state); },
        redo: function () { redo(); return clone(state); },
        applyModel: function (raw, label, nextSelectedId) {
            var before = clone(state);
            state = normalizeModel(clone(raw || {}));
            selectedId = cleanId(nextSelectedId || '');
            if (selectedId && !nodeById(selectedId)) { selectedId = ''; }
            commit(before, String(label || 'Designer+ ændring'));
            render();
            return clone(state);
        },
        mutate: function (mutator, label) {
            if (typeof mutator !== 'function') { return clone(state); }
            var before = clone(state);
            mutator(state);
            state = normalizeModel(state);
            if (selectedId && !nodeById(selectedId)) { selectedId = ''; }
            commit(before, String(label || 'Designer+ ændring'));
            render();
            return clone(state);
        }
    });
""",
    'Alpha.42 canonical Designer bridge'
)

# ---------------------------------------------------------------------------
# Layer tree: expose canonical node IDs to the Suite. Alpha.40 keeps the panel
# heading outside the Elementer/Lag wrapper, so collapse recovery stays intact.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0148-layers.js',
    """                item.className = 'h18-vd-layer-item' + (card.classList.contains('is-selected') ? ' is-selected' : '');
                item.style.setProperty('--h18-layer-depth', String(depth));
""",
    """                item.className = 'h18-vd-layer-item' + (card.classList.contains('is-selected') ? ' is-selected' : '');
                item.setAttribute('data-node-id', id);
                item.style.setProperty('--h18-layer-depth', String(depth));
""",
    'Alpha.42 layer node id bridge'
)

# Canonical delete warning owns nested deletion, avoiding duplicate Suite dialogs.
replace_once(
    'assets/editor-v018-core.js',
    """        const del = document.getElementById('h18-clean-delete');
        if (del) { del.addEventListener('click', function () { if (window.confirm('Slet det valgte element?')) { deleteSelected(); } }); }
""",
    """        const del = document.getElementById('h18-clean-delete');
        if (del) {
            del.addEventListener('click', function () {
                const node = nodeById(selectedId);
                const childCount = node ? descendants(node.id).length : 0;
                const message = childCount > 0
                    ? 'Dette element indeholder ' + childCount + ' under-element' + (childCount === 1 ? '' : 'er') + '.\\n\\nSlet element + alle under-elementer?'
                    : 'Slet det valgte element?';
                if (window.confirm(message)) { deleteSelected(); }
            });
        }
""",
    'Alpha.42 nested delete protection'
)

# ---------------------------------------------------------------------------
# Responsive preview API: keep canonical frontend renderer, but allow named
# device presets and rotation to change only the iframe CSS viewport width.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    "var WIDTHS = { laptop: 1100, tablet: 850, mobile: 390 };",
    "var WIDTHS = { laptop: 1100, tablet: 850, mobile: 390 };\n    var DEFAULT_WIDTHS = { laptop: 1100, tablet: 850, mobile: 390 };",
    'Alpha.42 mutable preview widths'
)
replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    """    function install() {
        ensureHost();
""",
    """    window.H18VDResponsivePreview = Object.assign(window.H18VDResponsivePreview || {}, {
        setWidth: function (device, width) {
            device = String(device || '');
            width = Math.max(280, Math.min(2400, parseInt(width || 0, 10) || 0));
            if (!WIDTHS[device] || !width) { return false; }
            WIDTHS[device] = width;
            currentDevice = device;
            lastSubmitted = '';
            fitFrame();
            submitPreview(true);
            return true;
        },
        reset: function () {
            Object.keys(DEFAULT_WIDTHS).forEach(function (device) { WIDTHS[device] = DEFAULT_WIDTHS[device]; });
            lastSubmitted = '';
            fitFrame();
            if (WIDTHS[activeDevice()]) { submitPreview(true); }
        },
        width: function () {
            var device = activeDevice();
            return WIDTHS[device] || 1920;
        },
        widths: function () { return Object.assign({}, WIDTHS); },
        refresh: function () { lastSubmitted = ''; submitPreview(true); }
    });

    function install() {
        ensureHost();
""",
    'Alpha.42 responsive preview public API'
)

# ---------------------------------------------------------------------------
# Server-backed Suite library/controller + editor assets.
# ---------------------------------------------------------------------------
controller_source = ASSET_ROOT / 'DesignerSuiteController.php'
js_source = ASSET_ROOT / 'editor-v0200-designer-suite.js'
css_source = ASSET_ROOT / 'editor-v0200-designer-suite.css'
for source in [controller_source, js_source, css_source]:
    if not source.is_file():
        raise SystemExit(f'Alpha.42 release asset missing: {source}')

write('src/Admin/DesignerSuiteController.php', controller_source.read_text(encoding='utf-8'))
write('assets/editor-v0200-designer-suite.js', js_source.read_text(encoding='utf-8'))
write('assets/editor-v0200-designer-suite.css', css_source.read_text(encoding='utf-8'))

replace_once(
    'visual-designer-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Admin/EditorController.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Admin/EditorController.php';\nrequire_once VDM_DIR . 'src/Admin/DesignerSuiteController.php';\n",
    'Alpha.42 controller require'
)
replace_once(
    'visual-designer-manager.php',
    "    \\VisualDesignerManager\\Admin\\EditorController::register();\n",
    "    \\VisualDesignerManager\\Admin\\EditorController::register();\n    \\VisualDesignerManager\\Admin\\DesignerSuiteController::register();\n",
    'Alpha.42 controller register'
)

replace_once(
    'visual-designer-manager.php',
    """        'diagAction' => 'h18_clean_diag_append',
        'diagNonce' => wp_create_nonce('h18_clean_diag_append'),
    ]);
""",
    """        'diagAction' => 'h18_clean_diag_append',
        'diagNonce' => wp_create_nonce('h18_clean_diag_append'),
        'suiteNonce' => \\VisualDesignerManager\\Admin\\DesignerSuiteController::nonce(),
        'pageUrl' => $postId > 0 ? (string) get_permalink($postId) : '',
    ]);
""",
    'Alpha.42 Suite localization'
)

replace_once(
    'visual-designer-manager.php',
    """    wp_enqueue_style(
        'h18-clean-editor-v0183-canonical-responsive-preview',
        H18_CLEAN_URL . 'assets/editor-v0183-canonical-responsive-preview.css',
        ['h18-clean-editor-v0181'],
        H18_CLEAN_VERSION
    );
""",
    """    wp_enqueue_style(
        'h18-clean-editor-v0183-canonical-responsive-preview',
        H18_CLEAN_URL . 'assets/editor-v0183-canonical-responsive-preview.css',
        ['h18-clean-editor-v0181'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0200-designer-suite',
        H18_CLEAN_URL . 'assets/editor-v0200-designer-suite.css',
        ['h18-clean-editor-v0183-canonical-responsive-preview'],
        H18_CLEAN_VERSION
    );
""",
    'Alpha.42 Suite stylesheet enqueue'
)

replace_once(
    'visual-designer-manager.php',
    """    wp_enqueue_script(
        'h18-clean-editor-v0183-canonical-responsive-preview',
        H18_CLEAN_URL . 'assets/editor-v0183-canonical-responsive-preview.js',
        ['h18-clean-editor-v0181-color-picker', 'h18-clean-editor-v0121'],
        H18_CLEAN_VERSION,
        true
    );
""",
    """    wp_enqueue_script(
        'h18-clean-editor-v0183-canonical-responsive-preview',
        H18_CLEAN_URL . 'assets/editor-v0183-canonical-responsive-preview.js',
        ['h18-clean-editor-v0181-color-picker', 'h18-clean-editor-v0121'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0200-designer-suite',
        H18_CLEAN_URL . 'assets/editor-v0200-designer-suite.js',
        ['h18-clean-editor-v0183-canonical-responsive-preview', 'h18-clean-editor-v0148-layers'],
        H18_CLEAN_VERSION,
        true
    );
""",
    'Alpha.42 Suite script enqueue'
)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if isinstance(rows, list):
    rows.insert(0, {
        'version': VERSION,
        'date': '2026-10-24',
        'items': [
            'Designer+ samler multi-select, alignment, ens bredde/højde og vandret/lodret fordeling i samme canonical Undo/Redo-model.',
            'Lag+ får omdøbning, editor-only skjul, lås og drag-rækkefølge; Elementer-panelets Alpha.41 fold-ud-fix bevares.',
            'Lokal crash-recovery/autosave gemmer usavede layoutmodeller og tilbyder Gendan/Kassér efter browser- eller sessionsafbrydelse.',
            'Responsive værktøjer viser inheritance/override, kan nulstille til Desktop, filtrere kun overrides, vise safe-area og bruge device presets/rotation.',
            'Komponentbibliotek understøtter lokale kopier og globale Sektion-komponenter; globale opdateringer synkroniserer gemte instanser og opretter sideversioner.',
            'Design Tokens for farver, radius, spacing og fonts kan linkes til elementer og synkroniseres på tværs af gemte sider.',
            'Designer+ tilføjer visuel box-model/spacing-editor, hurtige billedværktøjer med klikbart fokuspunkt og otte Sektionspresets.',
            'Gemte versioner kan sammenlignes side-by-side gennem den canonical frontend-preview-renderer; live-siden kan sammenlignes mod den usavede Designer-model.',
            'QA/Test siden analyserer alt-tekst, billedkilder, tomme links, smalle knapper, overflow og overlap; workflow-badge markerer Publiceret/Kladde/Ikke gemt.',
            'Inspector får søgning/favoritter, Ctrl+K Command Palette og nested delete-beskyttelse.',
        ],
    })
    history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
core = read('assets/editor-v018-core.js')
layers = read('assets/editor-v0148-layers.js')
responsive_preview = read('assets/editor-v0183-canonical-responsive-preview.js')
suite_js = read('assets/editor-v0200-designer-suite.js')
suite_css = read('assets/editor-v0200-designer-suite.css')
layout = read('src/Model/LayoutModel.php')
controller = read('src/Admin/DesignerSuiteController.php')

for token in [
    'Version: 3.0.0-alpha.42',
    "define('VDM_VERSION', '3.0.0-alpha.42');",
    "'h18-clean-editor-v0200-designer-suite'",
    'DesignerSuiteController::nonce()',
]:
    if token not in main:
        raise SystemExit(f'Alpha.42 main token missing: {token}')
for token in [
    'suiteComponentId', 'suiteTokenBackground', 'getModel: function ()',
    'applyModel: function (raw, label, nextSelectedId)', 'mutate: function (mutator, label)',
    "childCount = node ? descendants(node.id).length : 0",
]:
    if token not in core:
        raise SystemExit(f'Alpha.42 core token missing: {token}')
for token in ['suiteComponentId', 'suiteTokenBackground', 'suiteLocked', 'suiteHidden']:
    if token not in layout:
        raise SystemExit(f'Alpha.42 LayoutModel token missing: {token}')
if "item.setAttribute('data-node-id', id);" not in layers:
    raise SystemExit('Alpha.42 Layer bridge missing')
for token in ['window.H18VDResponsivePreview', 'setWidth: function (device, width)', 'DEFAULT_WIDTHS']:
    if token not in responsive_preview:
        raise SystemExit(f'Alpha.42 responsive API token missing: {token}')
for token in [
    'DesignerSuiteController', 'syncComponentAcrossPages', 'syncTokensAcrossPages',
    'LayoutModel::saveVersion', 'vdm_designer_suite_components_v1',
]:
    if token not in controller:
        raise SystemExit(f'Alpha.42 controller token missing: {token}')
for token in [
    'installMultiSelect()', 'function align(action)', 'installAutosave()',
    'function addSectionPreset(kind)', 'function runQa()', 'openLiveCompare',
    'openModelCompare', 'saveGlobalComponent', 'saveTokens', 'openCommandPalette',
]:
    if token not in suite_js:
        raise SystemExit(f'Alpha.42 suite JS token missing: {token}')
for token in ['.h18-suite-drawer', '.h18-suite-selected', '.h18-suite-command', '.h18-suite-safe-top']:
    if token not in suite_css:
        raise SystemExit(f'Alpha.42 suite CSS token missing: {token}')

print('Visual Designer Manager V3 3.0.0-alpha.42 Designer Productivity Suite: PASS')
