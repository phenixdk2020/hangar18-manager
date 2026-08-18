from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone

ROOT=Path('.').resolve()
BRANCH='qa/v0.5.22-release'
ERROR=ROOT/'.github/v0522-release-error.txt'

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
            run(['git','commit','-m','QA: record v0.5.22 release error'])
            run(['git','push','origin','HEAD:'+BRANCH])
    except Exception as inner:
        print('Could not persist v0.5.22 diagnostic:',inner,file=sys.stderr)

def build_package():
    build=ROOT/'.build/hangar18-manager'
    shutil.rmtree(ROOT/'.build',ignore_errors=True)
    (build/'assets').mkdir(parents=True)
    for f in ['hangar18-manager.php','readme.txt']: shutil.copy2(ROOT/f,build/f)
    for f in ['admin.css','admin.js']: shutil.copy2(ROOT/'assets'/f,build/'assets'/f)
    package=ROOT/'dist/hangar18-manager.zip'
    if package.exists(): package.unlink()
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for path in build.rglob('*'):
            if path.is_file(): z.write(path,path.relative_to(build.parent))
    with zipfile.ZipFile(package,'r') as z:
        bad=z.testzip()
        if bad: raise RuntimeError('Corrupt ZIP member: '+bad)
    return package

def write_manifest(package):
    sha=hashlib.sha256(package.read_bytes()).hexdigest()
    manifest={
      'schema_version':'1.0','plugin':'hangar18-manager','version':'0.5.22','min_wp':'6.4','min_php':'8.0',
      'published_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),
      'package_path':'dist/hangar18-manager.zip','package_sha256':sha,
      'changelog':[
        'Tilføjer UD-047 Component Variants oven på samme linked definition og eksponerede inputmodel.',
        'Variant anvendes før lokale instance-overrides; lokale overrides har dermed højeste prioritet.',
        'Tilføjer UD-048 nested subtree Patterns med friske keys og transparent kompatibilitet med gamle enkeltsektion-presets.',
        'Tilføjer UD-049 Page Templates, der opretter frie draft WordPress/Hangar18-sider med friske section keys og audit-origin.',
        'Template-oprettede sider bliver automatisk Hangar18-managed og redigerbare i sideeditoren.',
        'Løfter page-editor schema bagudkompatibelt til 1.18.'
      ]}
    (ROOT/'update.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return sha

def verify(package,sha):
    verify=ROOT/'.verify'; shutil.rmtree(verify,ignore_errors=True); verify.mkdir()
    with zipfile.ZipFile(package,'r') as z: z.extractall(verify)
    run(['php','-l',str(verify/'hangar18-manager/hangar18-manager.php')])
    run(['node','--check',str(verify/'hangar18-manager/assets/admin.js')])
    php=(verify/'hangar18-manager/hangar18-manager.php').read_text()
    js=(verify/'hangar18-manager/assets/admin.js').read_text()
    readme=(verify/'hangar18-manager/readme.txt').read_text()
    assert 'Version: 0.5.22' in php and "const VERSION = '0.5.22';" in php
    assert "'Version'        => '1.18'" in php
    assert 'normalize_page_component_variants' in php and 'normalize_page_template_sections' in php
    assert 'applyPatternV0522' in js and 'renderPageTemplatesV0522' in js
    assert 'Version: 0.5.22' in readme
    assert hashlib.sha256(package.read_bytes()).hexdigest()==sha
    shutil.rmtree(verify,ignore_errors=True); shutil.rmtree(ROOT/'.build',ignore_errors=True)

def main():
    run(['python3','.github/scripts/patch_v0522.py'])
    run(['php','-l','hangar18-manager.php'])
    run(['node','--check','assets/admin.js'])
    run(['python3','.github/scripts/qa_v0522.py'])
    package=build_package(); sha=write_manifest(package); verify(package,sha)
    git_setup()
    run(['git','add','hangar18-manager.php','assets/admin.js','assets/admin.css','readme.txt','update.json','dist/hangar18-manager.zip'])
    if subprocess.run(['git','diff','--cached','--quiet']).returncode==0:
        raise RuntimeError('No v0.5.22 product changes staged')
    run(['git','commit','-m','Release Hangar18 Manager 0.5.22 candidate'])
    run(['git','push','origin','HEAD:'+BRANCH])
    print('RELEASE_SHA256='+sha)

try:
    main()
except Exception as exc:
    persist_error(exc)
    raise
