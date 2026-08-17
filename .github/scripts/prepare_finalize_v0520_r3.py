from pathlib import Path

patch=Path('.github/scripts/patch_v0520.py')
t=patch.read_text()

# Correct actual Header/Footer spacing panel: radius fields follow spacing fields.
old_admin="""spacing_panel_tail=\"\"\"                        $this->field('SpacingLargePx', 'Afstand L (px)', $s['SpacingLargePx'], 'number');
                        $this->field('SpacingXlPx', 'Afstand XL (px)', $s['SpacingXlPx'], 'number');
                        ?>
                    </section>
\"\"\""""
new_admin="""spacing_panel_tail=\"\"\"                        $this->field('SpacingLargePx', 'Afstand L (px)', $s['SpacingLargePx'], 'number');
                        $this->field('SpacingXlPx', 'Afstand XL (px)', $s['SpacingXlPx'], 'number');
                        $this->field('RadiusSmallPx', 'Afrunding S (px)', $s['RadiusSmallPx'], 'number');
                        $this->field('RadiusMediumPx', 'Afrunding M (px)', $s['RadiusMediumPx'], 'number');
                        $this->field('RadiusLargePx', 'Afrunding L (px)', $s['RadiusLargePx'], 'number');
                        ?>
                    </section>
\"\"\""""
if old_admin not in t:
    raise SystemExit('Admin spacing panel patch-definition anchor missing')
t=t.replace(old_admin,new_admin,1)

# Correct CSS function boundary: section renderer follows page_editor_frontend_css in current source.
t=t.replace("end=php.index('    private function render_page_editor_imported_group', start)","end=php.index('    private function render_page_editor_section_front', start)")

# Correct current v0.5.19 canvasElementColors return order exactly.
old="""colors_return=\"\"\"        return { background: background, backgroundImage: backgroundImage, text: text, heading: heading, border: border, opacity: opacity };
\"\"\"
colors_return_new=\"\"\"        if (currentCanvasState === 'disabled') {
            opacity *= Math.max(10, Math.min(100, canvasNumber($row, 'DisabledOpacityPercent', 55))) / 100;
        }
        return { background: background, backgroundImage: backgroundImage, text: text, heading: heading, border: border, opacity: opacity };
\"\"\""""
new="""colors_return=\"\"\"        return { background: background, text: text, heading: heading, border: border, opacity: opacity, backgroundImage: backgroundImage };
\"\"\"
colors_return_new=\"\"\"        if (currentCanvasState === 'disabled') {
            opacity *= Math.max(10, Math.min(100, canvasNumber($row, 'DisabledOpacityPercent', 55))) / 100;
        }
        return { background: background, text: text, heading: heading, border: border, opacity: opacity, backgroundImage: backgroundImage };
\"\"\""""
if old not in t:
    raise SystemExit('Canvas return patch-definition anchor missing')
t=t.replace(old,new,1)
patch.write_text(t)

finalizer=Path('.github/scripts/finalize_v0520.py')
f=finalizer.read_text()
old_run="""def run(args):
    print('+', ' '.join(map(str,args)), flush=True)
    subprocess.run(args, check=True)
"""
new_run="""def run(args):
    print('+', ' '.join(map(str,args)), flush=True)
    proc=subprocess.run(args, text=True, capture_output=True)
    if proc.stdout: print(proc.stdout, end='')
    if proc.stderr: print(proc.stderr, end='', file=sys.stderr)
    if proc.returncode != 0:
        raise RuntimeError('command failed: ' + ' '.join(map(str,args)) + '\\nstdout:\\n' + proc.stdout + '\\nstderr:\\n' + proc.stderr)
"""
if old_run not in f:
    raise SystemExit('Finalizer run() anchor missing')
f=f.replace(old_run,new_run,1)

needle="""      '.github/workflows/diagnose-v0520-next.yml','.github/workflows/run-finalize-v0520.yml',
      '.github/diagnostics-v0520.txt','.github/diagnostics-v0520-next.txt','.github/finalize-v0520-error.txt']:
"""
replacement="""      '.github/workflows/diagnose-v0520-next.yml','.github/workflows/run-finalize-v0520.yml',
      '.github/workflows/run-finalize-v0520-r2.yml','.github/workflows/run-diagnose-patch-v0520.yml',
      '.github/workflows/run-diagnose-patch-v0520-r2.yml','.github/workflows/run-diagnose-patch-v0520-r3.yml',
      '.github/workflows/run-diagnose-patch-v0520-r4.yml','.github/workflows/run-finalize-v0520-r3.yml',
      '.github/scripts/diagnose_patch_v0520.py','.github/scripts/prepare_finalize_v0520_r3.py',
      '.github/diagnostics-v0520.txt','.github/diagnostics-v0520-next.txt','.github/diagnostics-v0520-patch.txt',
      '.github/finalize-v0520-error.txt']:
"""
if needle not in f:
    raise SystemExit('Finalizer cleanup anchor missing')
f=f.replace(needle,replacement,1)
finalizer.write_text(f)
print('v0.5.20 deterministic finalizer prepared')
