from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone

ROOT=Path('.').resolve()
DIAG=ROOT/'.github/finalize-v0520-error.txt'

def run(args):
    print('+', ' '.join(map(str,args)), flush=True)
    subprocess.run(args, check=True)

def git_commit(message, paths=None):
    run(['git','config','user.name','hangar18-build'])
    run(['git','config','user.email','actions@users.noreply.github.com'])
    if paths:
        run(['git','add',*paths])
    else:
        run(['git','add','-A'])
    proc=subprocess.run(['git','diff','--cached','--quiet'])
    if proc.returncode != 0:
        run(['git','commit','-m',message])
        run(['git','push','origin','HEAD:qa/v0.5.20-diagnose'])

def correct_patch_anchor():
    p=ROOT/'.github/scripts/patch_v0520.py'
    t=p.read_text()
    old="""spacing_panel_tail=\"\"\"                        $this->field('SpacingLargePx', 'Afstand L (px)', $s['SpacingLargePx'], 'number');
                        $this->field('SpacingXlPx', 'Afstand XL (px)', $s['SpacingXlPx'], 'number');
                        ?>
                    </section>
\"\"\""""
    new="""spacing_panel_tail=\"\"\"                        $this->field('SpacingLargePx', 'Afstand L (px)', $s['SpacingLargePx'], 'number');
                        $this->field('SpacingXlPx', 'Afstand XL (px)', $s['SpacingXlPx'], 'number');
                        $this->field('RadiusSmallPx', 'Afrunding S (px)', $s['RadiusSmallPx'], 'number');
                        $this->field('RadiusMediumPx', 'Afrunding M (px)', $s['RadiusMediumPx'], 'number');
                        $this->field('RadiusLargePx', 'Afrunding L (px)', $s['RadiusLargePx'], 'number');
                        ?>
                    </section>
\"\"\""""
    if old not in t:
        raise RuntimeError('admin anchor definition missing')
    p.write_text(t.replace(old,new,1))

def build_zip():
    build=ROOT/'.build/hangar18-manager'
    if build.parent.exists(): shutil.rmtree(build.parent)
    (build/'assets').mkdir(parents=True)
    for f in ['hangar18-manager.php','readme.txt']:
        shutil.copy2(ROOT/f, build/f)
    for f in ['admin.css','admin.js']:
        shutil.copy2(ROOT/'assets'/f, build/'assets'/f)
    out=ROOT/'dist/hangar18-manager.zip'
    out.parent.mkdir(exist_ok=True)
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for f in build.parent.rglob('*'):
            if f.is_file(): z.write(f, f.relative_to(build.parent))
    with zipfile.ZipFile(out,'r') as z:
        bad=z.testzip()
        if bad: raise RuntimeError('bad ZIP member: '+bad)
    return out

def write_manifest(package):
    sha=hashlib.sha256(package.read_bytes()).hexdigest()
    manifest={
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
    (ROOT/'update.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return sha

def clean_temp():
    shutil.rmtree(ROOT/'.build',ignore_errors=True)
    for rel in [
      '.github/scripts/patch_v0520.py','.github/scripts/qa_v0520.py','.github/scripts/finalize_v0520.py',
      '.github/workflows/build-v0520.yml','.github/workflows/diagnose-v0520.yml','.github/workflows/finalize-v0520.yml',
      '.github/workflows/diagnose-v0520-next.yml','.github/workflows/run-finalize-v0520.yml',
      '.github/diagnostics-v0520.txt','.github/diagnostics-v0520-next.txt','.github/finalize-v0520-error.txt']:
        p=ROOT/rel
        if p.exists(): p.unlink()

def main():
    correct_patch_anchor()
    run(['python3','.github/scripts/patch_v0520.py'])
    run(['php','-l','hangar18-manager.php'])
    run(['node','--check','assets/admin.js'])
    run(['python3','.github/scripts/qa_v0520.py'])
    package=build_zip()
    sha=write_manifest(package)
    verify=ROOT/'.verify'
    shutil.rmtree(verify,ignore_errors=True); verify.mkdir()
    with zipfile.ZipFile(package,'r') as z: z.extractall(verify)
    run(['php','-l',str(verify/'hangar18-manager/hangar18-manager.php')])
    run(['node','--check',str(verify/'hangar18-manager/assets/admin.js')])
    m=json.loads((ROOT/'update.json').read_text())
    assert m['version']=='0.5.20' and m['package_sha256']==sha
    shutil.rmtree(verify,ignore_errors=True)
    clean_temp()
    git_commit('Release Hangar18 Manager 0.5.20')
    print('RELEASE_SHA256='+sha)

try:
    main()
except Exception as exc:
    DIAG.parent.mkdir(parents=True,exist_ok=True)
    DIAG.write_text(type(exc).__name__+': '+str(exc)+'\n')
    try:
        git_commit('QA: record v0.5.20 finalizer error',[str(DIAG.relative_to(ROOT))])
    except Exception as git_exc:
        print('Could not persist diagnostic:',git_exc,file=sys.stderr)
    raise
