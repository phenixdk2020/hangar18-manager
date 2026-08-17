from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile
from datetime import datetime, timezone

ROOT = Path('.').resolve()
TARGET_BRANCH = 'qa/v0.5.20-r3-check'

def run(args):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(args, check=True)

# Use the exact preparation that passed check-v0520-r5.
run(['python3', '.github/scripts/prepare_finalize_v0520_r3.py'])
run(['python3', '.github/scripts/patch_v0520.py'])
run(['php', '-l', 'hangar18-manager.php'])
run(['node', '--check', 'assets/admin.js'])
run(['python3', '.github/scripts/qa_v0520.py'])

build_root = ROOT / '.build'
package_root = build_root / 'hangar18-manager'
shutil.rmtree(build_root, ignore_errors=True)
(package_root / 'assets').mkdir(parents=True)
for name in ['hangar18-manager.php', 'readme.txt']:
    shutil.copy2(ROOT / name, package_root / name)
for name in ['admin.css', 'admin.js']:
    shutil.copy2(ROOT / 'assets' / name, package_root / 'assets' / name)

package = ROOT / 'dist' / 'hangar18-manager.zip'
package.parent.mkdir(exist_ok=True)
if package.exists():
    package.unlink()
with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in package_root.rglob('*'):
        if path.is_file():
            archive.write(path, path.relative_to(build_root))
with zipfile.ZipFile(package, 'r') as archive:
    bad = archive.testzip()
    if bad:
        raise RuntimeError('Corrupt ZIP member: ' + bad)

sha = hashlib.sha256(package.read_bytes()).hexdigest()
manifest = {
    'schema_version': '1.0',
    'plugin': 'hangar18-manager',
    'version': '0.5.20',
    'min_wp': '6.4',
    'min_php': '8.0',
    'published_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
    'package_path': 'dist/hangar18-manager.zip',
    'package_sha256': sha,
    'changelog': [
        'Afslutter E3 Design System med redigerbare builder-breakpoints og globale motion/focus-tokens.',
        'Tilføjer Focus, Active og Disabled states samt transition presets pr. element.',
        'Live canvas og kommandopalette kan forhåndsvise Normal, Hover, Focus, Aktiv og Disabled.',
        'Standard-breakpoints 782/1199 bevarer eksisterende responsive sider; Header legacy breakpoints ændres ikke.',
        'Løfter DesignerSchemaVersion kompatibelt til 1.1 og page-editor schema til 1.16.'
    ]
}
(ROOT / 'update.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

verify = ROOT / '.verify'
shutil.rmtree(verify, ignore_errors=True)
verify.mkdir()
with zipfile.ZipFile(package, 'r') as archive:
    archive.extractall(verify)
run(['php', '-l', str(verify / 'hangar18-manager' / 'hangar18-manager.php')])
run(['node', '--check', str(verify / 'hangar18-manager' / 'assets' / 'admin.js')])
verify_php = (verify / 'hangar18-manager' / 'hangar18-manager.php').read_text()
verify_js = (verify / 'hangar18-manager' / 'assets' / 'admin.js').read_text()
verify_readme = (verify / 'hangar18-manager' / 'readme.txt').read_text()
assert 'Version: 0.5.20' in verify_php
assert "const VERSION = '0.5.20';" in verify_php
assert "'Version'        => '1.16'" in verify_php
assert "'data-state': 'focus'" in verify_js and "'data-state': 'disabled'" in verify_js
assert 'Version: 0.5.20' in verify_readme
assert hashlib.sha256(package.read_bytes()).hexdigest() == sha

shutil.rmtree(build_root, ignore_errors=True)
shutil.rmtree(verify, ignore_errors=True)

# Self-clean every v0.5.20-only QA/build artifact on this release branch.
for folder, patterns in [
    (ROOT / '.github' / 'workflows', ['*v0520*.yml']),
    (ROOT / '.github' / 'scripts', ['*v0520*.py']),
    (ROOT / '.github', ['*v0520*.txt']),
]:
    if folder.exists():
        for pattern in patterns:
            for path in folder.glob(pattern):
                if path.is_file():
                    path.unlink()

run(['git', 'config', 'user.name', 'hangar18-build'])
run(['git', 'config', 'user.email', 'actions@users.noreply.github.com'])
run(['git', 'add', '-A'])
status = subprocess.run(['git', 'diff', '--cached', '--quiet'])
if status.returncode == 0:
    raise RuntimeError('No release changes staged')
run(['git', 'commit', '-m', 'Release Hangar18 Manager 0.5.20'])
run(['git', 'push', 'origin', 'HEAD:' + TARGET_BRANCH])
print('RELEASE_SHA256=' + sha)
