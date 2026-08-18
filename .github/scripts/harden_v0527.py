from pathlib import Path
p=Path('assets/admin.js')
t=p.read_text()
old="""        renderCanvasDirectControls($row, $preview, layout, colors);
    }

    function refreshAllCanvasPreviews() {
"""
new="""        renderCanvasDirectControls($row, $preview, layout, colors);
        evaluateConditionPreviewV0527($row);
    }

    function refreshAllCanvasPreviews() {
"""
if t.count(old)!=1:
    raise SystemExit(f'canvas condition hook: expected 1 anchor, found {t.count(old)}')
t=t.replace(old,new,1)
p.write_text(t)
print('v0.5.27 canvas condition preview hook hardened')
