(function () {
    'use strict';

    const list = document.getElementById('h18-ud-template-element-list');
    const preview = document.getElementById('h18-ud-site-template-preview');
    if (!list || !preview) {
        return;
    }

    const fonts = ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'];
    let dragged = null;

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
        if (!control) {
            return fallback == null ? '' : fallback;
        }
        return control.value == null ? (fallback == null ? '' : fallback) : control.value;
    }

    function number(row, suffix, fallback) {
        const parsed = parseInt(value(row, suffix, fallback), 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function esc(value) {
        const node = document.createElement('div');
        node.textContent = String(value == null ? '' : value);
        return node.innerHTML;
    }

    function ensureStyleControls(row) {
        if (row.querySelector('.h18-ud-element-style-controls')) {
            return;
        }
        const grid = row.querySelector('.h18-ud-template-element-grid');
        if (!grid) {
            return;
        }
        const box = document.createElement('div');
        box.className = 'h18-ud-element-style-controls is-wide';
        box.innerHTML = [
            '<h4>Typografi og design</h4>',
            '<div class="h18-ud-style-grid">',
            '<label>Brødtekst-font<select data-style-field="SectionBodyFontFamily">' + fonts.map(function (f) { return '<option value="' + esc(f) + '">' + esc(f === 'Global' ? 'Global font' : f) + '</option>'; }).join('') + '</select></label>',
            '<label>Overskrift-font<select data-style-field="SectionHeadingFontFamily">' + fonts.map(function (f) { return '<option value="' + esc(f) + '">' + esc(f === 'Global' ? 'Global font' : f) + '</option>'; }).join('') + '</select></label>',
            '<label>Brødtekst (px)<input data-style-field="BodyFontSizePx" type="number" min="0" max="32" value="0"><small>0 = global</small></label>',
            '<label>Justering<select data-style-field="DesktopAlignment"><option>Left</option><option>Center</option><option>Right</option></select></label>',
            '<label>Baggrund<input data-style-field="CustomBackgroundColor" type="color" value="#ffffff"></label>',
            '<label>Tekst<input data-style-field="CustomTextColor" type="color" value="#30382a"></label>',
            '<label>Overskrift<input data-style-field="CustomHeadingColor" type="color" value="#30382a"></label>',
            '<label>Indvendig afstand (px)<input data-style-field="PaddingPx" type="number" min="0" max="120" value="0"></label>',
            '</div>'
        ].join('');
        grid.appendChild(box);

        box.querySelectorAll('[data-style-field]').forEach(function (control) {
            const key = control.getAttribute('data-style-field');
            const existing = field(row, key);
            if (existing) {
                control.value = existing.value;
                existing.remove();
            }
        });
        renumber();
    }

    function ensureMoveControls(row) {
        const head = row.querySelector('.h18-ud-template-element-head');
        if (!head || head.querySelector('.h18-ud-move-up')) {
            return;
        }
        const group = document.createElement('span');
        group.className = 'h18-ud-move-controls';
        group.innerHTML = '<button type="button" class="button-link h18-ud-move-up" aria-label="Flyt element op">↑</button><button type="button" class="button-link h18-ud-move-down" aria-label="Flyt element ned">↓</button>';
        const remove = head.querySelector('.h18-ud-remove-template-element');
        head.insertBefore(group, remove || null);
    }

    function enhanceRow(row) {
        row.draggable = true;
        ensureStyleControls(row);
        ensureMoveControls(row);
    }

    function renumber() {
        Array.from(list.querySelectorAll('.h18-ud-template-element')).forEach(function (row, index) {
            row.dataset.index = String(index);
            row.querySelectorAll('[name]').forEach(function (control) {
                control.name = control.name.replace(/sections\[\d+\]/, 'sections[' + index + ']');
            });
            row.querySelectorAll('[data-style-field]').forEach(function (control) {
                const styleField = control.getAttribute('data-style-field');
                control.name = 'sections[' + index + '][' + styleField + ']';
            });
        });
    }

    function fontCss(value) {
        if (!value || value === 'Global') {
            return '';
        }
        if (value === 'System') {
            return 'system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif';
        }
        return '"' + String(value).replace(/"/g, '') + '",sans-serif';
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
        const background = String(value(row, 'CustomBackgroundColor', '#ffffff'));
        const textColor = String(value(row, 'CustomTextColor', '#30382a'));
        const headingColor = String(value(row, 'CustomHeadingColor', '#30382a'));

        node.style.backgroundColor = background;
        node.style.color = textColor;
        node.style.textAlign = ['left','center','right'].includes(align) ? align : 'left';
        if (bodySize > 0) { node.style.fontSize = bodySize + 'px'; }
        if (padding > 0) { node.style.padding = padding + 'px'; }
        if (bodyFont) { node.style.fontFamily = bodyFont; }

        if (title) {
            const heading = document.createElement('strong');
            heading.className = 'h18-ud-preview-heading';
            heading.textContent = title;
            heading.style.color = headingColor;
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
            if (summary) {
                summary.textContent = key + ' · ' + String(value(row, 'Type', 'text'));
            }
        });
        rows.forEach(function (row) {
            const key = String(value(row, 'Key', 'element'));
            const parent = String(value(row, 'LayoutParentKey', ''));
            const node = nodes.get(key);
            const parentNode = parent ? nodes.get(parent) : null;
            if (parentNode && parentNode !== node) {
                parentNode.appendChild(node);
            } else {
                preview.appendChild(node);
            }
        });
        if (!preview.children.length) {
            preview.innerHTML = '<p class="description">Ingen aktive elementer.</p>';
        }
    }

    function move(row, delta) {
        const rows = activeRows();
        const index = rows.indexOf(row);
        const target = rows[index + delta];
        if (!target) {
            return;
        }
        if (delta < 0) {
            list.insertBefore(row, target);
        } else {
            list.insertBefore(target, row);
        }
        renumber();
        render();
        row.scrollIntoView({ block: 'nearest' });
    }

    list.addEventListener('click', function (event) {
        const up = event.target.closest('.h18-ud-move-up');
        const down = event.target.closest('.h18-ud-move-down');
        if (up || down) {
            event.preventDefault();
            move((up || down).closest('.h18-ud-template-element'), up ? -1 : 1);
            return;
        }
        window.setTimeout(function () {
            Array.from(list.querySelectorAll('.h18-ud-template-element')).forEach(enhanceRow);
            renumber();
            render();
        }, 0);
    });

    list.addEventListener('dragstart', function (event) {
        const row = event.target.closest('.h18-ud-template-element');
        if (!row || row.classList.contains('is-removed')) { return; }
        dragged = row;
        row.classList.add('is-dragging');
        if (event.dataTransfer) {
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', row.dataset.index || '');
        }
    });
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

    list.addEventListener('input', render);
    list.addEventListener('change', render);

    const observer = new MutationObserver(function () {
        Array.from(list.querySelectorAll('.h18-ud-template-element')).forEach(enhanceRow);
        renumber();
        render();
    });
    observer.observe(list, { childList: true });

    Array.from(list.querySelectorAll('.h18-ud-template-element')).forEach(enhanceRow);
    renumber();
    render();
})();
