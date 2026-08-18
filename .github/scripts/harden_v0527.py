from pathlib import Path

# Canvas preview must restore the hidden-condition marker after every re-render.
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

# PHP DateTime format needs exactly one source backslash before literal T.
p=Path('hangar18-manager.php')
t=p.read_text()
old="$formats = ['!Y-m-d\\\\TH:i', '!Y-m-d H:i', '!Y-m-d'];"
new="$formats = ['!Y-m-d\\TH:i', '!Y-m-d H:i', '!Y-m-d'];"
if t.count(old)!=1:
    raise SystemExit(f'datetime format escaping: expected 1 anchor, found {t.count(old)}')
t=t.replace(old,new,1)
p.write_text(t)
print('v0.5.27 canvas/date condition hardening applied')
