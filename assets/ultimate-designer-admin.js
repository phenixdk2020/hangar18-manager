(function () {
    'use strict';

    const list = document.getElementById('h18-ud-template-element-list');
    const preview = document.getElementById('h18-ud-site-template-preview');
    const addButton = document.getElementById('h18-ud-add-template-element');
    if (!list || !preview) {
        return;
    }

    const fonts = ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'];
    let types = ['container','flex','grid','text','image','menu','buttons','spacer'];
    try {
        const parsed = JSON.parse(list.dataset.supportedTypes || '[]');
        if (Array.isArray(parsed) && parsed.length) { types = parsed; }
    } catch (error) {
        // Keep the safe built-in list.
    }
    let nextIndex = parseInt(list.dataset.nextIndex || '0', 10);
    if (!Number.isFinite(nextIndex)) { nextIndex = list.children.length; }
    let dragged = null;

    function esc(value) {
        const node = document.createElement('div');
        node.textContent = String(value == null ? '' : value);
        return node.innerHTML;
    }

    function activeRows() {
        return Array.from(list.querySelectorAll('.h18-ud-template-element')).filter(function (row) {
            return !row.classList.contains('is-removed');
        });
    }

    function field(row, suffix) {
        return row.querySelector('[name$="[' + suffix + ']"]');
    }

    function value(row, suffix, fallback) {
        const control = field(row, suffix);
        return control && control.value != null ? control.value : (fallback == null ? '' : fallback);
    }

    function number(row, suffix, fallback) {
        const parsed = parseInt(value(row, suffix, fallback), 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function fontOptions() {
        return fonts.map(function (font) {
            return '<option value="' + esc(font) + '">' + esc(font === 'Global' ? 'Global font' : font) + '</option>';
        }).join('');
    }

    function typeOptions() {
        return types.map(function (type) {
            return '<option value="' + esc(type) + '">' + esc(type) + '</option>';
        }).join('');
    }

    function newRowHtml(index) {
        const key = 'element-' + (index + 1);
        return [
            '<article class="h18-ud-template-element" data-index="' + index + '">',
            '<div class="h18-ud-template-element-head">',
            '<span class="dashicons dashicons-move h18-ud-drag-handle" aria-hidden="true"></span>',
            '<strong class="h18-ud-element-summary">' + key + ' · text</strong>',
            '<span class="h18-ud-move-controls"><button type="button" class="button-link h18-ud-move-up" aria-label="Flyt element op">↑</button><button type="button" class="button-link h18-ud-move-down" aria-label="Flyt element ned">↓</button></span>',
            '<button type="button" class="button-link-delete h18-ud-remove-template-element">Fjern</button></div>',
            '<div class="h18-ud-template-element-grid">',
            '<label>Key<input type="text" name="sections[' + index + '][Key]" value="' + key + '"></label>',
            '<label>Type<select name="sections[' + index + '][Type]" class="h18-ud-section-type">' + typeOptions() + '</select></label>',
            '<label>Parent key<input type="text" name="sections[' + index + '][LayoutParentKey]"></label>',
            '<label>Overskrift (valgfri)<input type="text" name="sections[' + index + '][Title]"></label>',
            '<label class="is-wide">Tekst/indhold<textarea rows="4" name="sections[' + index + '][Content]" class="h18-ud-section-content"></textarea></label>',
            '<div class="h18-ud-element-style-controls is-wide"><h4>Typografi og design</h4><div class="h18-ud-style-grid">',
            '<label>Design<select data-style-field="DesignMode" name="sections[' + index + '][DesignMode]"><option value="Global">Global</option><option value="Custom">Custom</option></select></label>',
            '<label>Brødtekst-font<select data-style-field="SectionBodyFontFamily" name="sections[' + index + '][SectionBodyFontFamily]">' + fontOptions() + '</select></label>',
            '<label>Overskrift-font<select data-style-field="SectionHeadingFontFamily" name="sections[' + index + '][SectionHeadingFontFamily]">' + fontOptions() + '</select></label>',
            '<label>Brødtekst (px)<input data-style-field="BodyFontSizePx" type="number" min="0" max="32" name="sections[' + index + '][BodyFontSizePx]" value="0"><small>0 = global</small></label>',
            '<label>H1 (px)<input data-style-field="H1FontSizePx" type="number" min="0" max="96" name="sections[' + index + '][H1FontSizePx]" value="0"><small>0 = global</small></label>',
            '<label>H2 (px)<input data-style-field="H2FontSizePx" type="number" min="0" max="80" name="sections[' + index + '][H2FontSizePx]" value="0"><small>0 = global</small></label>',
            '<label>H3 (px)<input data-style-field="H3FontSizePx" type="number" min="0" max="64" name="sections[' + index + '][H3FontSizePx]" value="0"><small>0 = global</small></label>',
            '<label>Justering<select data-style-field="DesktopAlignment" name="sections[' + index + '][DesktopAlignment]"><option>Left</option><option>Center</option><option>Right</option></select></label>',
            '<label>Baggrund<input data-style-field="CustomBackgroundColor" type="color" name="sections[' + index + '][CustomBackgroundColor]" value="#ffffff"></label>',
            '<label>Tekst<input data-style-field="CustomTextColor" type="color" name="sections[' + index + '][CustomTextColor]" value="#30382a"></label>',
            '<label>Overskrift<input data-style-field="CustomHeadingColor" type="color" name="sections[' + index + '][CustomHeadingColor]" value="#30382a"></label>',
            '<label>Indvendig afstand (px)<input data-style-field="PaddingPx" type="number" min="0" max="120" name="sections[' + index + '][PaddingPx]" value="0"></label>',
            '</div></div>',
            '<input type="hidden" name="sections[' + index + '][Remove]" value="0" class="h18-ud-section-remove">',
            '</div></article>'
        ].join('');
    }

    function renumber() {
        Array.from(list.querySelectorAll('.h18-ud-template-element')).forEach(function (row, index) {
            row.dataset.index = String(index);
            row.querySelectorAll('[name]').forEach(function (control) {
                control.name = control.name.replace(/sections\[\d+\]/, 'sections[' + index + ']');
            });
        });
    }

    function fontCss(font) {
        if (!font || font === 'Global') { return ''; }
        if (font === 'System') { return 'system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'; }
        return '"' + String(font).replace(/"/g, '') + '",sans-serif';
    }

    function buildPreviewNode(row) {
        const type = String(value(row, 'Type', 'text'));
        const title = String(value(row, 'Title', ''));
        const content = String(value(row, 'Content', ''));
        const node = document.createElement(['container','flex','grid'].includes(type) ? 'section' : 'div');
        node.className = 'h18-ud-preview-node h18-ud-preview-' + type;
        node.dataset.key = String(value(row, 'Key', 'element'));

        const bodySize = Math.max(0, Math.min(32, number(row, 'BodyFontSizePx', 0)));
        const padding = Math.max(0, Math.min(120, number(row, 'PaddingPx', 0)));
        const bodyFont = fontCss(value(row, 'SectionBodyFontFamily', 'Global'));
        const headingFont = fontCss(value(row, 'SectionHeadingFontFamily', 'Global'));
        const align = String(value(row, 'DesktopAlignment', 'Left')).toLowerCase();
        const designMode = String(value(row, 'DesignMode', 'Global'));

        node.style.textAlign = ['left','center','right'].includes(align) ? align : 'left';
        if (bodySize > 0) { node.style.fontSize = bodySize + 'px'; }
        if (padding > 0) { node.style.padding = padding + 'px'; }
        if (bodyFont) { node.style.fontFamily = bodyFont; }
        if (designMode === 'Custom') {
            node.style.backgroundColor = String(value(row, 'CustomBackgroundColor', '#ffffff'));
            node.style.color = String(value(row, 'CustomTextColor', '#30382a'));
        }

        if (title) {
            const heading = document.createElement('strong');
            heading.className = 'h18-ud-preview-heading';
            heading.textContent = title;
            if (designMode === 'Custom') { heading.style.color = String(value(row, 'CustomHeadingColor', '#30382a')); }
            if (headingFont) { heading.style.fontFamily = headingFont; }
            node.appendChild(heading);
        }
        if (content) {
            const body = document.createElement('div');
            body.className = 'h18-ud-preview-body';
            body.innerHTML = esc(content).replace(/\r?\n/g, '<br>');
            node.appendChild(body);
        }
        if (type === 'menu') {
            const menu = document.createElement('div');
            menu.className = 'h18-ud-preview-menu';
            menu.textContent = 'Hjem · Om · Kontakt';
            node.appendChild(menu);
        } else if (type === 'image') {
            const image = document.createElement('div');
            image.className = 'h18-ud-preview-image';
            image.textContent = 'Billede';
            node.appendChild(image);
        } else if (type === 'buttons') {
            const button = document.createElement('span');
            button.className = 'button';
            button.textContent = content || 'Knap';
            node.appendChild(button);
        } else if (type === 'spacer') {
            node.style.minHeight = '32px';
            node.textContent = 'Afstand';
        }
        return node;
    }

    function render() {
        preview.innerHTML = '';
        const nodes = new Map();
        const rows = activeRows();
        rows.forEach(function (row) {
            const key = String(value(row, 'Key', 'element'));
            nodes.set(key, buildPreviewNode(row));
            const summary = row.querySelector('.h18-ud-element-summary');
            if (summary) { summary.textContent = key + ' · ' + String(value(row, 'Type', 'text')); }
        });
        rows.forEach(function (row) {
            const key = String(value(row, 'Key', 'element'));
            const parent = String(value(row, 'LayoutParentKey', ''));
            const node = nodes.get(key);
            const parentNode = parent ? nodes.get(parent) : null;
            if (parentNode && parentNode !== node) { parentNode.appendChild(node); }
            else { preview.appendChild(node); }
        });
        if (!preview.children.length) {
            preview.innerHTML = '<p class="description">Ingen aktive elementer.</p>';
        }
    }

    function move(row, delta) {
        const rows = activeRows();
        const index = rows.indexOf(row);
        const target = rows[index + delta];
        if (!target) { return; }
        if (delta < 0) { list.insertBefore(row, target); }
        else { list.insertBefore(target, row); }
        renumber();
        render();
        row.scrollIntoView({ block: 'nearest' });
    }

    if (addButton) {
        addButton.addEventListener('click', function () {
            list.insertAdjacentHTML('beforeend', newRowHtml(nextIndex++));
            renumber();
            render();
            const rows = activeRows();
            const last = rows[rows.length - 1];
            if (last) { last.scrollIntoView({ block: 'nearest' }); }
        });
    }

    list.addEventListener('click', function (event) {
        const remove = event.target.closest('.h18-ud-remove-template-element');
        if (remove) {
            event.preventDefault();
            const row = remove.closest('.h18-ud-template-element');
            const removeField = row && field(row, 'Remove');
            if (row && removeField) {
                removeField.value = '1';
                row.classList.add('is-removed');
                render();
            }
            return;
        }
        const up = event.target.closest('.h18-ud-move-up');
        const down = event.target.closest('.h18-ud-move-down');
        if (up || down) {
            event.preventDefault();
            move((up || down).closest('.h18-ud-template-element'), up ? -1 : 1);
        }
    });

    list.addEventListener('dragstart', function (event) {
        const handle = event.target.closest('.h18-ud-drag-handle');
        const row = event.target.closest('.h18-ud-template-element');
        if (!row || !handle || row.classList.contains('is-removed')) {
            event.preventDefault();
            return;
        }
        dragged = row;
        row.classList.add('is-dragging');
        if (event.dataTransfer) {
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', row.dataset.index || '');
        }
    });

    list.querySelectorAll('.h18-ud-template-element').forEach(function (row) { row.draggable = true; });

    list.addEventListener('dragover', function (event) {
        if (!dragged) { return; }
        event.preventDefault();
        const target = event.target.closest('.h18-ud-template-element');
        if (!target || target === dragged || target.classList.contains('is-removed')) { return; }
        const rect = target.getBoundingClientRect();
        const after = event.clientY > rect.top + rect.height / 2;
        list.insertBefore(dragged, after ? target.nextSibling : target);
    });
    list.addEventListener('drop', function (event) {
        if (!dragged) { return; }
        event.preventDefault();
        dragged.classList.remove('is-dragging');
        dragged = null;
        renumber();
        render();
    });
    list.addEventListener('dragend', function () {
        if (dragged) { dragged.classList.remove('is-dragging'); }
        dragged = null;
        renumber();
        render();
    });

    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1 && node.classList.contains('h18-ud-template-element')) { node.draggable = true; }
            });
        });
    });
    observer.observe(list, { childList: true });

    list.addEventListener('input', render);
    list.addEventListener('change', render);
    const form = list.closest('form');
    if (form) { form.addEventListener('submit', renumber); }

    renumber();
    render();
})();
