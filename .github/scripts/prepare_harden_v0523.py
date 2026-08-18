from pathlib import Path

p=Path('.github/scripts/harden_v0523.py')
t=p.read_text()
old="""# Canvas status badge; actual frontend is server-resolved, while editor values remain explicit fallback controls.
js=once(js,
\"\"\"        const type = String($row.attr('data-section-type') || 'text');
        const $inner = $('<div>', { class: 'h18-canvas-preview-inner' });
\"\"\",
\"\"\"        const type = String($row.attr('data-section-type') || 'text');
        const $inner = $('<div>', { class: 'h18-canvas-preview-inner' });
        const dynamicBindingCountV0523=Object.keys(dataBindingsV0523($row)).length;const dynamicEntryV0523=String(pageSectionControls($row,'.h18-data-context-entry').val()||pageSectionControls($row,'.h18-data-context-entry').attr('data-selected')||'0');if(dynamicBindingCountV0523&&dynamicEntryV0523!=='0')$inner.append($('<div>',{class:'h18-canvas-dynamic-badge',text:'Dynamic · '+dynamicBindingCountV0523+' binding(er)'}));
\"\"\",'canvas binding badge')
"""
new="""# Canvas status badge; actual frontend is server-resolved, while editor values remain explicit fallback controls.
canvas_start=js.index('    function canvasBuildPreviewContent($row, $preview) {')
canvas_end=js.index('    function canvasMediaFocalSettings', canvas_start)
canvas_block=js[canvas_start:canvas_end]
canvas_block=once(canvas_block,
\"\"\"        const type = String($row.attr('data-section-type') || 'text');
        const title = String(canvasFieldValue($row, 'Title', ''));
        const content = String(canvasFieldValue($row, 'Content', ''));
        const $inner = $('<div>', { class: 'h18-canvas-preview-inner h18-canvas-type-' + type });
\"\"\",
\"\"\"        const type = String($row.attr('data-section-type') || 'text');
        const title = String(canvasFieldValue($row, 'Title', ''));
        const content = String(canvasFieldValue($row, 'Content', ''));
        const $inner = $('<div>', { class: 'h18-canvas-preview-inner h18-canvas-type-' + type });
        const dynamicBindingCountV0523=Object.keys(dataBindingsV0523($row)).length;
        const dynamicEntryV0523=String(pageSectionControls($row,'.h18-data-context-entry').val()||pageSectionControls($row,'.h18-data-context-entry').attr('data-selected')||'0');
        if(dynamicBindingCountV0523&&dynamicEntryV0523!=='0')$inner.append($('<div>',{class:'h18-canvas-dynamic-badge',text:'Dynamic · '+dynamicBindingCountV0523+' binding(er)'}));
\"\"\",'canvas binding badge')
js=js[:canvas_start]+canvas_block+js[canvas_end:]
"""
if old not in t:
    raise SystemExit('Original canvas badge patch definition missing')
p.write_text(t.replace(old,new,1))
print('v0.5.23 hardening anchors prepared')
