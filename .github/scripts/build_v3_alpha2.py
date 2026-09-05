from pathlib import Path
import hashlib
import shutil

VERSION = '3.0.0-alpha.2'
SOURCE = Path('clean/hangar18-manager')
DEST = Path('build/visual-designer-manager')

TOKEN_MAP = {
    'H18_CLEAN_VERSION': 'VDM_VERSION',
    'H18_CLEAN_FILE': 'VDM_FILE',
    'H18_CLEAN_DIR': 'VDM_DIR',
    'H18_CLEAN_URL': 'VDM_URL',
}

UPDATER_REPLACEMENTS = {
    "private const MANIFEST_URL = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/main/clean-update.json';":
        "private const MANIFEST_URL = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/v3-clean-refactor/v3-update.json';",
    "private const SLUG = 'hangar18-manager';":
        "private const SLUG = 'visual-designer-manager';",
    "private const PLUGIN_FILE = 'hangar18-manager/hangar18-manager.php';":
        "private const PLUGIN_FILE = 'visual-designer-manager/visual-designer-manager.php';",
    "'User-Agent' => 'Hangar18-Manager-Clean/' . VDM_VERSION,":
        "'User-Agent' => 'Visual-Designer-Manager-V3/' . VDM_VERSION,",
    "'hangar18-manager/' . str_replace('\\\\', '/', $relative)":
        "'visual-designer-manager/' . str_replace('\\\\', '/', $relative)",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_php(text: str) -> str:
    for old, new in TOKEN_MAP.items():
        text = text.replace(old, new)
    return text


if DEST.parent.exists():
    shutil.rmtree(DEST.parent)
DEST.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(SOURCE, DEST)

old_main = DEST / 'hangar18-manager.php'
main = DEST / 'visual-designer-manager.php'
old_main.rename(main)

main_text = main.read_text(encoding='utf-8')
main_replacements = {
    ' * Version: 0.1.93': f' * Version: {VERSION}',
    "define('VDM_VERSION', '0.1.93');": f"define('VDM_VERSION', '{VERSION}');",
    "define('H18_CLEAN_VERSION', '0.1.93');": f"define('H18_CLEAN_VERSION', '{VERSION}');",
}
for old, new in main_replacements.items():
    if main_text.count(old) != 1:
        raise SystemExit(f'Main bootstrap token mismatch: {old!r} count={main_text.count(old)}')
    main_text = main_text.replace(old, new)
main.write_text(main_text, encoding='utf-8')

for path in sorted(DEST.rglob('*.php')):
    if path == main:
        continue
    text = path.read_text(encoding='utf-8')
    transformed = transform_php(text)
    if path.relative_to(DEST).as_posix() == 'src/Update/GitHubUpdater.php':
        for old, new in UPDATER_REPLACEMENTS.items():
            if transformed.count(old) != 1:
                raise SystemExit(f'Updater token mismatch: {old!r} count={transformed.count(old)}')
            transformed = transformed.replace(old, new)
    path.write_text(transformed, encoding='utf-8')

# Prove every non-bootstrap runtime change is limited to the approved constant-token map,
# plus the updater's V3 package identity substitutions.
failures = []
for src in sorted(p for p in SOURCE.rglob('*') if p.is_file()):
    rel = src.relative_to(SOURCE).as_posix()
    if rel == 'hangar18-manager.php':
        continue
    dst = DEST / rel
    if not dst.is_file():
        failures.append(f'missing: {rel}')
        continue
    if src.suffix.lower() == '.php':
        expected = transform_php(src.read_text(encoding='utf-8'))
        if rel == 'src/Update/GitHubUpdater.php':
            for old, new in UPDATER_REPLACEMENTS.items():
                expected = expected.replace(old, new)
        actual = dst.read_text(encoding='utf-8')
        if actual != expected:
            failures.append(f'non-approved PHP mutation: {rel}')
    elif sha(src) != sha(dst):
        failures.append(f'non-PHP runtime changed: {rel}')

source_files = {
    p.relative_to(SOURCE).as_posix()
    for p in SOURCE.rglob('*') if p.is_file() and p.relative_to(SOURCE).as_posix() != 'hangar18-manager.php'
}
dest_files = {
    p.relative_to(DEST).as_posix()
    for p in DEST.rglob('*') if p.is_file() and p.relative_to(DEST).as_posix() != 'visual-designer-manager.php'
}
for rel in sorted(source_files - dest_files):
    failures.append(f'missing expected runtime file: {rel}')
for rel in sorted(dest_files - source_files):
    failures.append(f'extra runtime file: {rel}')

if failures:
    print('V3 Alpha.2 deterministic transform: FAIL')
    for failure in failures:
        print(' -', failure)
    raise SystemExit(1)

# V3 runtime code must now use the canonical constants. Compatibility aliases remain only
# in the bootstrap so old integrations do not break during the staged migration.
legacy_constant_hits = []
for path in sorted(DEST.rglob('*.php')):
    if path == main:
        continue
    text = path.read_text(encoding='utf-8')
    for token in TOKEN_MAP:
        if token in text:
            legacy_constant_hits.append(f'{path.relative_to(DEST)}: {token}')
if legacy_constant_hits:
    print('Legacy runtime constants remain outside bootstrap:')
    for hit in legacy_constant_hits:
        print(' -', hit)
    raise SystemExit(1)

for token in TOKEN_MAP:
    if token not in main_text:
        raise SystemExit(f'Compatibility alias missing from bootstrap: {token}')

print('V3 Alpha.2 deterministic transform: PASS')
print('Canonical VDM_* runtime constants: PASS')
print('V1 compatibility aliases retained only in bootstrap: PASS')
