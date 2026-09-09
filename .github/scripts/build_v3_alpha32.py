from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.32'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha31.py'], check=True)


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
# Version cutover. Alpha.32 is deliberately a release-channel fix; the
# Alpha.31 frontend/runtime behavior is retained byte-for-byte apart from the
# plugin version and release history.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.31', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.31');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.31');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.32 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.31':
    raise SystemExit('Expected Alpha.31 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Retter V3 GitHub-opdateringskanalen, som var blevet stående på 3.0.0-alpha.29.',
        'Release-workflow publicerer fremover installations-ZIP og v3-update.json samlet til den stabile v3-clean-refactor-kanal efter bestået QA.',
        'Updaterens stabile manifest-URL bevares, så allerede installerede V3-versioner kan opdage den nye version uden lokal konfigurationsændring.',
        'Alpha.31 Moduldesign → Afstand til Footer og øvrig frontend-adfærd er bevaret uændret.',
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts + regression locks.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
updater = read('src/Update/GitHubUpdater.php')
module_design = read('src/Model/ModuleDesignModel.php')
editor = read('src/Admin/EditorController.php')
collection = read('src/Frontend/CollectionPageRenderer.php')
responsive = read('src/Frontend/ResponsiveRenderer.php')
history_text = read('release-history.json')

for token in [
    'Version: 3.0.0-alpha.32',
    "define('VDM_VERSION', '3.0.0-alpha.32');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.32');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.32 main token missing: {token}')

stable_manifest = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/v3-clean-refactor/v3-update.json'
if stable_manifest not in updater:
    raise SystemExit('Alpha.32 stable updater manifest URL missing')

# Alpha.31 Footer-gap contracts must survive unchanged.
for token in ["'footerGap' => 64", "'footerGap' => self::clamp("]:
    if token not in module_design:
        raise SystemExit(f'Alpha.32 retained ModuleDesign token missing: {token}')
for token in ['Afstand til Footer (px)', 'gælder både moduloversigten og modulets detaljesider']:
    if token not in editor:
        raise SystemExit(f'Alpha.32 retained Editor token missing: {token}')
for token in ['--h18-module-footer-gap:', 'padding:36px 0 var(--h18-module-footer-gap)']:
    if token not in collection:
        raise SystemExit(f'Alpha.32 retained Collection token missing: {token}')
for token in [
    '$moduleFooterGap = self::detailModuleFooterGap($postId);',
    "'event-detalje' => 'events'",
    "'album-detalje' => 'billedgalleri'",
    "'koeretoej-detalje' => 'koeretoejer-og-materiel'",
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.32 retained Responsive token missing: {token}')

if '3.0.0-alpha.32' not in history_text:
    raise SystemExit('Alpha.32 history token missing')

print('PASS')
