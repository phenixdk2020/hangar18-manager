from pathlib import Path

p = Path('assets/admin.js')
s = p.read_text(encoding='utf-8')

old_title = r'''    $(document).on('dblclick', '.h18-canvas-card-inline-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        selectedCanvasCardKey = String($(this).closest('.h18-canvas-card').data('card-key') || '');
        inspectPageSection($row); canvasFocusCardEditor($row, selectedCanvasCardKey);
        $(this).data('canvas-original-card-text', String($(this).text() || '')).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });
'''
new_title = r'''    $(document).on('dblclick', '.h18-canvas-card-inline-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $source = $(this);
        const $row = $source.closest('.h18-page-section-row');
        const key = String($source.closest('.h18-canvas-card').data('card-key') || '');
        const original = String($source.text() || '');
        selectedCanvasCardKey = key;
        inspectPageSection($row);
        canvasFocusCardEditor($row, key);
        renderCanvasPreview($row);
        const $fresh = $row.children('.h18-canvas-preview').find('.h18-canvas-card[data-card-key="' + key + '"] .h18-canvas-card-inline-edit').first();
        $fresh.data('canvas-original-card-text', original).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });
'''

old_rich = r'''    $(document).on('dblclick', '.h18-canvas-card-rich-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        selectedCanvasCardKey = String($(this).closest('.h18-canvas-card').data('card-key') || '');
        inspectPageSection($row); canvasFocusCardEditor($row, selectedCanvasCardKey);
        $(this).data('canvas-original-card-html', String($(this).hasClass('is-empty') ? '' : ($(this).html() || '')));
        if ($(this).hasClass('is-empty')) { $(this).empty().removeClass('is-empty'); }
        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });
'''
new_rich = r'''    $(document).on('dblclick', '.h18-canvas-card-rich-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $source = $(this);
        const $row = $source.closest('.h18-page-section-row');
        const key = String($source.closest('.h18-canvas-card').data('card-key') || '');
        const original = String($source.hasClass('is-empty') ? '' : ($source.html() || ''));
        selectedCanvasCardKey = key;
        inspectPageSection($row);
        canvasFocusCardEditor($row, key);
        renderCanvasPreview($row);
        const $fresh = $row.children('.h18-canvas-preview').find('.h18-canvas-card[data-card-key="' + key + '"] .h18-canvas-card-rich-edit').first();
        $fresh.data('canvas-original-card-html', original);
        if ($fresh.hasClass('is-empty')) { $fresh.empty().removeClass('is-empty'); }
        $fresh.attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });
'''

for label, old, new in [('title direct edit', old_title, new_title), ('rich direct edit', old_rich, new_rich)]:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
