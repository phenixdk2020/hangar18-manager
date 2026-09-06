from pathlib import Path
import hashlib
import json
import subprocess

VERSION = '3.0.0-alpha.6'
DEST = Path('build/visual-designer-manager')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Alpha.6 layers a narrowly scoped admin-style/history parity repair on the
# verified Alpha.5 package. The V1 Updates page markup and CSS are reused.
subprocess.run(['python3', '.github/scripts/build_v3_alpha5.py'], check=True)

protected = [
    'assets/admin-v019.css',
    'assets/admin-v0123.css',
    'assets/admin-v0175.css',
    'assets/editor-v018-core.js',
    'assets/editor-v0144-viewport.js',
    'assets/editor-v0169-canvas-height.js',
    'assets/editor.css',
    'src/Frontend/Renderer.php',
    'src/Frontend/ResponsiveRenderer.php',
    'src/Frontend/ThemeShell.php',
    'src/Model/LayoutModel.php',
    'src/Migration/V3StorageMigration.php',
    'templates/vdm-site-shell.php',
]
protected_before = {rel: sha(DEST / rel) for rel in protected}

main = DEST / 'visual-designer-manager.php'
main_text = main.read_text(encoding='utf-8')
for old, new in [
    (' * Version: 3.0.0-alpha.5', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.5');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.5');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main_text.count(old) != 1:
        raise SystemExit(f'Alpha.6 version token mismatch: {old!r} count={main_text.count(old)}')
    main_text = main_text.replace(old, new)
main.write_text(main_text, encoding='utf-8')

# Alpha.4 moved the Manager routes to vdm-* but the V1 enqueue guard still
# looked for the old route prefix. This is why the Updates page lost V1 CSS.
admin = DEST / 'src/Admin/AdminController.php'
admin_text = admin.read_text(encoding='utf-8')
old_guard = "if (!current_user_can('edit_pages') || strpos($hook, 'h18-clean-') === false) {"
new_guard = "if (!current_user_can('edit_pages') || strpos($hook, 'vdm-') === false) {"
if admin_text.count(old_guard) != 1:
    raise SystemExit(f'Alpha.6 admin enqueue guard mismatch: count={admin_text.count(old_guard)}')
admin_text = admin_text.replace(old_guard, new_guard)
admin.write_text(admin_text, encoding='utf-8')

# V1 releaseHistory() only accepted x.y.z and therefore silently rejected V3
# prerelease versions such as 3.0.0-alpha.6. Extend only the version parser.
updater = DEST / 'src/Update/GitHubUpdater.php'
updater_text = updater.read_text(encoding='utf-8')
old_pattern = "if (!preg_match('/^\\d+\\.\\d+\\.\\d+$/', $version)) {"
new_pattern = "if (!preg_match('/^\\d+\\.\\d+\\.\\d+(?:-[0-9A-Za-z.-]+)?$/', $version)) {"
if updater_text.count(old_pattern) != 1:
    raise SystemExit(f'Alpha.6 release-history version parser mismatch: count={updater_text.count(old_pattern)}')
updater_text = updater_text.replace(old_pattern, new_pattern)

# Remove the remaining old visible product label from the updater notice.
old_label = 'Hangar18 Manager → Opdateringer'
new_label = 'Visual Designer Manager → Opdateringer'
if updater_text.count(old_label) != 1:
    raise SystemExit(f'Alpha.6 updater notice label mismatch: count={updater_text.count(old_label)}')
updater_text = updater_text.replace(old_label, new_label)
updater.write_text(updater_text, encoding='utf-8')

# Prepend the V3 clean-refactor history to the retained V1 history. V1 rows are
# preserved verbatim below so test3 remains the historical product baseline.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
v1_rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(v1_rows, list) or not v1_rows or v1_rows[0].get('version') != '0.1.93':
    raise SystemExit('Expected V1 0.1.93 release-history baseline missing')

v3_rows = [
    {
        'version': '3.0.0-alpha.6',
        'date': '2026-09-06',
        'items': [
            'Opdateringer-siden indlæser igen den originale V1 Manager-styling på canonical vdm-* adminruter.',
            'Versionshistorikken viser nu V3 prerelease-versioner og markerer den installerede V3-version korrekt.',
            'V3 3.0.0-alpha.1 til alpha.6 vises før den bevarede V1 0.1.93-historik.',
            'Updater-noticen bruger nu navnet Visual Designer Manager i stedet for det historiske produktnavn.'
        ]
    },
    {
        'version': '3.0.0-alpha.5',
        'date': '2026-09-06',
        'items': [
            'True Site Shell: VDM-layouts overtager WordPress-template på VDM-sider.',
            'Temaets egen header, footer og sidetitel renderes ikke omkring VDM-indholdet.',
            'WordPress lifecycle hooks wp_head, wp_body_open og wp_footer bevares.',
            'V1 Designerens 1920/1180/980/390 virtuelle viewport og Fit-zoom er bevaret.'
        ]
    },
    {
        'version': '3.0.0-alpha.4',
        'date': '2026-09-06',
        'items': [
            'Bruger-synlige WordPress adminruter er flyttet fra historiske h18-clean-* slugs til canonical vdm-* slugs.',
            'Gamle admin-URLer bevares via et isoleret kompatibilitets-redirect.',
            'Designer, renderer, layout og Alpha.3 storage-migrering blev ikke ændret.'
        ]
    },
    {
        'version': '3.0.0-alpha.3',
        'date': '2026-09-05',
        'items': [
            'Kontrolleret V1 → V3 storage-migrering for layouts, historik, Header/Footer, moduldesign, felter, menuhistorik og modulrecords.',
            'Migreringen er copy-and-verify og sletter ikke V1-data.',
            'Portable V1-siteimport kan herefter bruges som permanent V3 acceptance-baseline.'
        ]
    },
    {
        'version': '3.0.0-alpha.2',
        'date': '2026-09-05',
        'items': [
            'Aktiv PHP-runtime bruger canonical VDM_VERSION, VDM_FILE, VDM_DIR og VDM_URL.',
            'Historiske runtime-konstanter blev reduceret til compatibility-aliaser i bootstrap.',
            'Designer, renderer og storage-adfærd blev ikke ændret.'
        ]
    },
    {
        'version': '3.0.0-alpha.1',
        'date': '2026-09-05',
        'items': [
            'V3 Clean Identity Baseline bygget direkte fra den gennemtestede V1 0.1.93 runtime.',
            'Pluginmappe og main-fil blev ændret til visual-designer-manager uden at omskrive Designer/renderer.',
            'Release-gaten verificerer V1-runtime og centrale Designer-interaktioner før pakning.'
        ]
    },
]

history_path.write_text(
    json.dumps({'versions': v3_rows + v1_rows}, ensure_ascii=False, indent=2) + '\n',
    encoding='utf-8',
)

# The actual V1 Updates page structure must still be present. Alpha.6 fixes the
# canonical admin hook so the already imported V1 styles are finally enqueued.
admin_text = admin.read_text(encoding='utf-8')
for required in (
    "self::open('Opdateringer', 'Tjek, installer og se update-checkpoints for Visual Designer Manager');",
    '<div class=\"h18-manager-card\"><h2>Version</h2><p class=\"h18-manager-big-version\">',
    'h18-manager-badge is-progress',
    'h18-manager-badge is-ok',
    '<div class=\"h18-manager-toolbar\">',
    '<div class=\"h18-manager-card\"><h2>Update-checkpoints</h2>',
    '<table class=\"widefat striped\">',
):
    if required not in admin_text:
        raise SystemExit(f'V1 Updates page parity token missing: {required}')

if new_guard not in admin_text:
    raise SystemExit('Canonical vdm-* admin style enqueue guard missing')
if old_guard in admin_text:
    raise SystemExit('Legacy admin style enqueue guard still active')

updater_text = updater.read_text(encoding='utf-8')
if 'admin.php?page=vdm-updates' not in updater_text:
    raise SystemExit('Canonical Updates notice route missing')
if old_label in updater_text or new_label not in updater_text:
    raise SystemExit('Updater notice product label cutover failed')
if new_pattern not in updater_text:
    raise SystemExit('SemVer prerelease release-history parser missing')

built_history = json.loads(history_path.read_text(encoding='utf-8'))['versions']
expected_v3 = [f'3.0.0-alpha.{n}' for n in range(6, 0, -1)]
actual_v3 = [row.get('version') for row in built_history[:6]]
if actual_v3 != expected_v3:
    raise SystemExit(f'V3 release-history order mismatch: {actual_v3!r}')
if built_history[6].get('version') != '0.1.93':
    raise SystemExit('V1 history was not retained immediately after V3 history')

# No visual CSS redesign is allowed in this fix. The V1 CSS and all layout,
# Designer, frontend shell and storage files remain byte-identical to Alpha.5.
for rel, before in protected_before.items():
    after = sha(DEST / rel)
    if before != after:
        raise SystemExit(f'Protected V1/V3 parity file changed during Alpha.6 admin UI/history repair: {rel}')

print('V3 Alpha.6 V1 Updates UI parity: PASS')
print('Canonical vdm-* admin pages now enqueue imported V1 Manager CSS: PASS')
print('V3 prerelease versions are accepted by releaseHistory(): PASS')
print('V3 alpha.1-alpha.6 history prepended; V1 history retained: PASS')
print('Updater notice uses Visual Designer Manager identity: PASS')
print('Designer/frontend/storage behavior unchanged: PASS')
