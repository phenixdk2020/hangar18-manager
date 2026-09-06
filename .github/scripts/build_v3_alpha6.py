from pathlib import Path
import hashlib
import subprocess

VERSION = '3.0.0-alpha.6'
DEST = Path('build/visual-designer-manager')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Alpha.6 layers a narrowly scoped admin-style parity repair on the verified
# Alpha.5 package. The V1 Updates page markup and CSS are reused unchanged.
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

admin = DEST / 'src/Admin/AdminController.php'
admin_text = admin.read_text(encoding='utf-8')
old_guard = "if (!current_user_can('edit_pages') || strpos($hook, 'h18-clean-') === false) {"
new_guard = "if (!current_user_can('edit_pages') || strpos($hook, 'vdm-') === false) {"
if admin_text.count(old_guard) != 1:
    raise SystemExit(f'Alpha.6 admin enqueue guard mismatch: count={admin_text.count(old_guard)}')
admin_text = admin_text.replace(old_guard, new_guard)
admin.write_text(admin_text, encoding='utf-8')

# The updater notice already points to the canonical vdm-updates route after
# Alpha.4. Remove the remaining old product label from the visible notice.
updater = DEST / 'src/Update/GitHubUpdater.php'
updater_text = updater.read_text(encoding='utf-8')
old_label = 'Hangar18 Manager → Opdateringer'
new_label = 'Visual Designer Manager → Opdateringer'
if updater_text.count(old_label) != 1:
    raise SystemExit(f'Alpha.6 updater notice label mismatch: count={updater_text.count(old_label)}')
updater_text = updater_text.replace(old_label, new_label)
updater.write_text(updater_text, encoding='utf-8')

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

# No visual CSS redesign is allowed in this fix. The V1 CSS and all layout,
# Designer, frontend shell and storage files remain byte-identical to Alpha.5.
for rel, before in protected_before.items():
    after = sha(DEST / rel)
    if before != after:
        raise SystemExit(f'Protected V1/V3 parity file changed during Alpha.6 admin UI repair: {rel}')

print('V3 Alpha.6 V1 Updates UI parity: PASS')
print('Canonical vdm-* admin pages now enqueue imported V1 Manager CSS: PASS')
print('V1 Updates markup and CSS preserved byte-for-byte: PASS')
print('Updater notice uses Visual Designer Manager identity: PASS')
print('Designer/frontend/storage behavior unchanged: PASS')
