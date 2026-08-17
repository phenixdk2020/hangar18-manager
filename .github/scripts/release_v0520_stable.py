from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile
from datetime import datetime, timezone

ROOT = Path('.').resolve()
TARGET_BRANCH = 'qa/v0.5.20-release-check'
SYNC_WORKFLOW = '''name: Sync Hangar18 release source

on:
  push:
    branches:
      - main
    paths:
      - 'dist/hangar18-manager.zip'
      - 'update.json'
      - '.github/workflows/sync-release-source.yml'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  sync-source:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Validate package and extract source
        shell: bash
        run: |
          set -euo pipefail
          rm -rf .build
          mkdir -p .build
          unzip -t dist/hangar18-manager.zip
          unzip -q dist/hangar18-manager.zip -d .build
          VERSION=$(python3 -c "import json; print(json.load(open('update.json'))['version'])")
          grep -F "Version: ${VERSION}" .build/hangar18-manager/hangar18-manager.php
          grep -F "const VERSION = '${VERSION}';" .build/hangar18-manager/hangar18-manager.php
          php -l .build/hangar18-manager/hangar18-manager.php
          node --check .build/hangar18-manager/assets/admin.js

      - name: Synchronize repository source
        shell: bash
        run: |
          set -euo pipefail
          cp .build/hangar18-manager/hangar18-manager.php hangar18-manager.php
          cp .build/hangar18-manager/readme.txt readme.txt
          mkdir -p assets
          cp .build/hangar18-manager/assets/admin.css assets/admin.css
          cp .build/hangar18-manager/assets/admin.js assets/admin.js
          rm -rf .build
          git config user.name "hangar18-build"
          git config user.email "actions@users.noreply.github.com"
          git add hangar18-manager.php readme.txt assets/admin.css assets/admin.js
          if git diff --cached --quiet; then
            echo "Repository source is already synchronized."
            exit 0
          fi
          git commit -m "Sync Hangar18 Manager ${VERSION:-release} source"
          git push
'''

def run(args):
    print('+', ' '.join(map(str, args)), flush=True)
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout, end='')
    if proc.stderr:
        print(proc.stderr, end='', file=__import__('sys').stderr)
    if proc.returncode != 0:
        raise RuntimeError('command failed: ' + ' '.join(map(str,args)) + '\nstdout:\n' + proc.stdout + '\nstderr:\n' + proc.stderr)

# These exact corrections already passed check-v0520-r5.
run(['python3', '.github/scripts/prepare_finalize_v0520_r3.py'])
run(['python3', '.github/scripts/patch_v0520.py'])
run(['php', '-l', 'hangar18-manager.php'])
run(['node', '--check', 'assets/admin.js'])
run(['python3', '.github/scripts/qa_v0520.py'])

build = ROOT / '.build' / 'hangar18-manager'
shutil.rmtree(ROOT / '.build', ignore_errors=True)
(build / 'assets').mkdir(parents=True)
for name in ['hangar18-manager.php', 'readme.txt']:
    shutil.copy2(ROOT / name, build / name)
for name in ['admin.css', 'admin.js']:
    shutil.copy2(ROOT / 'assets' / name, build / 'assets' / name)

package = ROOT / 'dist' / 'hangar18-manager.zip'
if package.exists(): package.unlink()
with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in build.rglob('*'):
        if path.is_file():
            z.write(path, path.relative_to(build.parent))
with zipfile.ZipFile(package, 'r') as z:
    bad = z.testzip()
    if bad: raise RuntimeError('Corrupt ZIP member: ' + bad)
sha = hashlib.sha256(package.read_bytes()).hexdigest()
manifest = {
  'schema_version':'1.0','plugin':'hangar18-manager','version':'0.5.20','min_wp':'6.4','min_php':'8.0',
  'published_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),
  'package_path':'dist/hangar18-manager.zip','package_sha256':sha,
  'changelog':[
    'Afslutter E3 Design System med redigerbare builder-breakpoints og globale motion/focus-tokens.',
    'Tilføjer Focus, Active og Disabled states samt transition presets pr. element.',
    'Live canvas og kommandopalette kan forhåndsvise Normal, Hover, Focus, Aktiv og Disabled.',
    'Standard-breakpoints 782/1199 bevarer eksisterende responsive sider; Header legacy breakpoints ændres ikke.',
    'Løfter DesignerSchemaVersion kompatibelt til 1.1 og page-editor schema til 1.16.'
  ]}
(ROOT/'update.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

verify = ROOT / '.verify'
shutil.rmtree(verify, ignore_errors=True); verify.mkdir()
with zipfile.ZipFile(package,'r') as z: z.extractall(verify)
run(['php','-l',str(verify/'hangar18-manager/hangar18-manager.php')])
run(['node','--check',str(verify/'hangar18-manager/assets/admin.js')])
vp=(verify/'hangar18-manager/hangar18-manager.php').read_text()
vj=(verify/'hangar18-manager/assets/admin.js').read_text()
vr=(verify/'hangar18-manager/readme.txt').read_text()
assert 'Version: 0.5.20' in vp and "const VERSION = '0.5.20';" in vp
assert "'Version'        => '1.16'" in vp
assert "'data-state': 'focus'" in vj and "'data-state': 'disabled'" in vj
assert 'Version: 0.5.20' in vr
assert hashlib.sha256(package.read_bytes()).hexdigest() == sha
shutil.rmtree(ROOT/'.build',ignore_errors=True); shutil.rmtree(verify,ignore_errors=True)

# Remove all v0.5.20-only QA files. Restore the permanent workflow before commit.
for folder, patterns in [
    (ROOT/'.github/workflows',['*v0520*.yml']),
    (ROOT/'.github/scripts',['*v0520*.py']),
    (ROOT/'.github',['*v0520*.txt','*v0520*.log']),
]:
    if folder.exists():
        for pattern in patterns:
            for path in folder.glob(pattern):
                if path.is_file(): path.unlink()
(ROOT/'.github/workflows/sync-release-source.yml').write_text(SYNC_WORKFLOW,encoding='utf-8')

run(['git','config','user.name','hangar18-build'])
run(['git','config','user.email','actions@users.noreply.github.com'])
run(['git','add','-A'])
# Resulting tree must differ from origin/main only by the six release files.
changed = subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
allowed = {'hangar18-manager.php','assets/admin.js','assets/admin.css','readme.txt','update.json','dist/hangar18-manager.zip'}
extra = set(changed) - allowed
if extra: raise RuntimeError('Unexpected release scope: ' + repr(sorted(extra)))
missing = {'hangar18-manager.php','assets/admin.js','assets/admin.css','readme.txt','update.json','dist/hangar18-manager.zip'} - set(changed)
if missing: raise RuntimeError('Missing release files: ' + repr(sorted(missing)))
run(['git','commit','-m','Release Hangar18 Manager 0.5.20'])
run(['git','push','origin','HEAD:'+TARGET_BRANCH])
print('RELEASE_SHA256='+sha)
