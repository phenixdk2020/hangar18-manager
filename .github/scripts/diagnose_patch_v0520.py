from pathlib import Path
import subprocess

p=Path('.github/scripts/patch_v0520.py')
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
if old in t:
    p.write_text(t.replace(old,new,1))
proc=subprocess.run(['python3','.github/scripts/patch_v0520.py'],text=True,capture_output=True)
out=Path('.github/diagnostics-v0520-patch.txt')
out.write_text('returncode='+str(proc.returncode)+'\n--- stdout ---\n'+proc.stdout+'\n--- stderr ---\n'+proc.stderr)
subprocess.run(['git','config','user.name','hangar18-build'],check=True)
subprocess.run(['git','config','user.email','actions@users.noreply.github.com'],check=True)
subprocess.run(['git','add',str(out)],check=True)
subprocess.run(['git','commit','-m','QA: record detailed v0.5.20 patch failure'],check=True)
subprocess.run(['git','push','origin','HEAD:qa/v0.5.20-diagnose'],check=True)
