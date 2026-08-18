from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone

ROOT=Path('.').resolve()
BRANCH='qa/v0.5.21-release'
ERROR=ROOT/'.github/v0521-release-error.txt'
SYNC_ORIGINAL='''name: Sync Hangar18 release source

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
    print('+',' '.join(map(str,args)),flush=True)
    p=subprocess.run(args,text=True,capture_output=True)
    if p.stdout: print(p.stdout,end='')
    if p.stderr: print(p.stderr,end='',file=sys.stderr)
    if p.returncode:
        raise RuntimeError('command failed: '+' '.join(map(str,args))+'\nstdout:\n'+p.stdout+'\nstderr:\n'+p.stderr)

def git_setup():
    run(['git','config','user.name','hangar18-build'])
    run(['git','config','user.email','actions@users.noreply.github.com'])

def persist_error(exc):
    try:
        ERROR.write_text(type(exc).__name__+': '+str(exc)+'\n',encoding='utf-8')
        git_setup(); run(['git','add',str(ERROR.relative_to(ROOT))])
        if subprocess.run(['git','diff','--cached','--quiet']).returncode:
            run(['git','commit','-m','QA: record v0.5.21 release error'])
            run(['git','push','origin','HEAD:'+BRANCH])
    except Exception as inner:
        print('Could not persist diagnostic:',inner,file=sys.stderr)

def build_package():
    build=ROOT/'.build/hangar18-manager'
    shutil.rmtree(ROOT/'.build',ignore_errors=True)
    (build/'assets').mkdir(parents=True)
    for f in ['hangar18-manager.php','readme.txt']: shutil.copy2(ROOT/f,build/f)
    for f in ['admin.css','admin.js']: shutil.copy2(ROOT/'assets'/f,build/'assets'/f)
    out=ROOT/'dist/hangar18-manager.zip'
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for path in build.rglob('*'):
            if path.is_file(): z.write(path,path.relative_to(build.parent))
    with zipfile.ZipFile(out,'r') as z:
        bad=z.testzip()
        if bad: raise RuntimeError('Corrupt ZIP member: '+bad)
    return out

def write_manifest(package):
    sha=hashlib.sha256(package.read_bytes()).hexdigest()
    manifest={
      'schema_version':'1.0','plugin':'hangar18-manager','version':'0.5.21','min_wp':'6.4','min_php':'8.0',
      'published_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),
      'package_path':'dist/hangar18-manager.zip','package_sha256':sha,
      'changelog':[
        'Tilføjer UD-043 Navigator rename/hide/lock/reorder med realtime canvas-synkronisering.',
        'Tilføjer UD-044 linked subtree components i separat global component-store.',
        'Tilføjer UD-045 atomisk propagation ved render-time resolution af den globale definition.',
        'Tilføjer UD-046 eksplicit frigivne Title/Content/Image/Button inputs med lokale overrides og låst layout/design.',
        'Tilføjer UD-050 usage inspector og blokeret delete når component stadig bruges.',
        'Eksisterende presets bevares som ikke-linked Patterns.',
        'Løfter page-editor schema bagudkompatibelt til 1.17.'
      ]}
    (ROOT/'update.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return sha

def verify_package(package,sha):
    verify=ROOT/'.verify'; shutil.rmtree(verify,ignore_errors=True); verify.mkdir()
    with zipfile.ZipFile(package,'r') as z: z.extractall(verify)
    run(['php','-l',str(verify/'hangar18-manager/hangar18-manager.php')])
    run(['node','--check',str(verify/'hangar18-manager/assets/admin.js')])
    php=(verify/'hangar18-manager/hangar18-manager.php').read_text()
    js=(verify/'hangar18-manager/assets/admin.js').read_text()
    readme=(verify/'hangar18-manager/readme.txt').read_text()
    assert 'Version: 0.5.21' in php and "const VERSION = '0.5.21';" in php
    assert "'Version'        => '1.17'" in php
    assert 'PAGE_COMPONENTS_OPTION' in php and 'resolve_page_component_instance_sections' in php
    assert 'renderLinkedComponentsV0521' in js and 'componentSubtreeDataV0521' in js
    assert 'Version: 0.5.21' in readme
    assert hashlib.sha256(package.read_bytes()).hexdigest()==sha
    shutil.rmtree(verify,ignore_errors=True)

def cleanup_success():
    shutil.rmtree(ROOT/'.build',ignore_errors=True); shutil.rmtree(ROOT/'.verify',ignore_errors=True)
    for path in [
      ROOT/'.github/scripts/patch_v0521.py',ROOT/'.github/scripts/prepare_v0521.py',ROOT/'.github/scripts/harden_v0521.py',ROOT/'.github/scripts/qa_v0521.py',ROOT/'.github/scripts/release_v0521.py',
      ROOT/'.github/workflows/build-v0521.yml',ROOT/'.github/workflows/inspect-v0521-context.yml',ROOT/'.github/v0521-context.txt',ROOT/'.github/v0521-release-error.txt']:
        if path.exists(): path.unlink()
    (ROOT/'.github/workflows/sync-release-source.yml').write_text(SYNC_ORIGINAL,encoding='utf-8')

def main():
    run(['python3','.github/scripts/prepare_v0521.py'])
    run(['python3','.github/scripts/patch_v0521.py'])
    run(['python3','.github/scripts/harden_v0521.py'])
    css=ROOT/'assets/admin.css'; t=css.read_text().replace('.h18-page-section-row:has(.h18-section-navigator-locked[value="1"]) .h18-page-section-drag','.h18-page-section-row.is-navigator-locked .h18-page-section-drag'); css.write_text(t)
    run(['php','-l','hangar18-manager.php']); run(['node','--check','assets/admin.js']); run(['python3','.github/scripts/qa_v0521.py'])
    if ':has(.h18-section-navigator-locked' in css.read_text(): raise RuntimeError('Unsupported lock :has selector remains')
    package=build_package(); sha=write_manifest(package); verify_package(package,sha); cleanup_success()
    git_setup(); run(['git','add','-A'])
    allowed={'hangar18-manager.php','assets/admin.js','assets/admin.css','readme.txt','update.json','dist/hangar18-manager.zip','.github/scripts/patch_v0521.py','.github/scripts/prepare_v0521.py','.github/scripts/harden_v0521.py','.github/scripts/qa_v0521.py','.github/scripts/release_v0521.py','.github/workflows/build-v0521.yml','.github/workflows/inspect-v0521-context.yml','.github/v0521-context.txt','.github/workflows/sync-release-source.yml'}
    changed=set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())
    extra=changed-allowed
    if extra: raise RuntimeError('Unexpected release scope: '+repr(sorted(extra)))
    run(['git','commit','-m','Release Hangar18 Manager 0.5.21'])
    run(['git','push','origin','HEAD:'+BRANCH])
    print('RELEASE_SHA256='+sha)

try:
    main()
except Exception as exc:
    persist_error(exc)
    raise
