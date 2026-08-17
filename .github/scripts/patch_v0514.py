from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 anchor, found {count}")
    return text.replace(old, new, 1)

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')
readme_path = Path('readme.txt')

php = php_path.read_text(encoding='utf-8')
php = replace_once(php, ' * Version: 0.5.13', ' * Version: 0.5.14', 'plugin header version')
php = replace_once(php, "    const VERSION = '0.5.13';", "    const VERSION = '0.5.14';", 'class version')

hint_anchor = '''                        <span>Visningen gør arbejdsområdet smallere. Den offentlige side åbnes med knappen ovenfor.</span>\n                    </div>'''
hint_new = '''                        <button type="button" class="button h18-command-palette-open" id="h18-command-palette-open" aria-haspopup="dialog" aria-controls="h18-command-palette" aria-expanded="false" title="Åbn kommandopaletten (Ctrl/Cmd+K)">⌘K Kommandoer</button>\n                        <span>Visningen gør arbejdsområdet smallere. Den offentlige side åbnes med knappen ovenfor.</span>\n                    </div>\n\n                    <div id="h18-command-palette" class="h18-command-palette" hidden>\n                        <div class="h18-command-palette-backdrop" data-command-close="1"></div>\n                        <section class="h18-command-palette-dialog" role="dialog" aria-modal="true" aria-labelledby="h18-command-palette-title">\n                            <header class="h18-command-palette-header">\n                                <div><strong id="h18-command-palette-title">Kommandoer og hurtignavigation</strong><small>Søg efter handlinger eller elementer på siden.</small></div>\n                                <button type="button" class="button-link h18-command-palette-close" aria-label="Luk kommandopaletten">Esc</button>\n                            </header>\n                            <label class="screen-reader-text" for="h18-command-palette-search">Søg i kommandoer</label>\n                            <input id="h18-command-palette-search" class="h18-command-palette-search" type="search" autocomplete="off" spellcheck="false" placeholder="Søg: hero, mobil, fortryd, kontakt …" aria-controls="h18-command-palette-results" />\n                            <div id="h18-command-palette-results" class="h18-command-palette-results" role="listbox" aria-label="Kommandoresultater"></div>\n                            <div id="h18-command-palette-empty" class="h18-command-palette-empty" hidden>Ingen kommandoer matcher søgningen.</div>\n                            <footer class="h18-command-palette-footer"><span>↑↓ vælg</span><span>Enter udfør</span><span>Esc luk</span><span>Alt+↑/↓ skift element</span></footer>\n                        </section>\n                    </div>'''
php = replace_once(php, hint_anchor, hint_new, 'command palette markup')
php_path.write_text(php, encoding='utf-8')

js = js_path.read_text(encoding='utf-8')
insert_anchor = "    $(document).on('click', '#h18-editor-restore-draft', function (event) {"
command_js = r'''
    const commandPaletteSectionTypes = [
        ['text', 'Tekst'], ['hero', 'Topbanner / hero'], ['text_image', 'Tekst og billede'], ['image', 'Stort billede'],
        ['buttons', 'Handlingsknapper'], ['card', 'Indholdskort'], ['card_grid', 'Kort-række / kolonner'], ['highlight', 'Fremhævet tekst'],
        ['spacer', 'Afstand'], ['html', 'Importeret blok / HTML'], ['css', 'Side-CSS'], ['mail_form', 'Mailformular'], ['poll', 'Afstemning']
    ];
    let commandPaletteActiveIndex = 0;
    let commandPaletteVisibleCommands = [];
    let commandPalettePreviousFocus = null;

    function commandPaletteIsOpen() {
        return !$('#h18-command-palette').prop('hidden');
    }

    function commandPaletteIsEditableTarget(target) {
        const $target = $(target);
        return $target.is('input, textarea, select') || $target.closest('[contenteditable="true"]').length > 0;
    }

    function commandPaletteNormalize(value) {
        return String(value || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim();
    }

    function commandPaletteSectionLabel($row) {
        const type = String($row.attr('data-section-type') || 'text');
        const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim() || 'Uden overskrift';
        const key = String($row.find('.h18-page-section-key').val() || '').trim();
        return { type: type, title: title, key: key, typeLabel: inspectorTypeLabel(type) };
    }

    function commandPaletteScrollToRow($row) {
        if (!$row || !$row.length) { return; }
        inspectPageSection($row);
        const node = $row.get(0);
        if (node && typeof node.scrollIntoView === 'function') {
            node.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function commandPaletteBuildCommands() {
        const commands = [];
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function (index) {
            const $row = $(this);
            const meta = commandPaletteSectionLabel($row);
            commands.push({
                id: 'section-' + String($row.attr('data-section-index') || index),
                group: 'Gå til element',
                label: meta.title,
                detail: meta.typeLabel + (meta.key ? ' · ' + meta.key : ''),
                keywords: 'gå til element sektion lag navigator ' + meta.type + ' ' + meta.typeLabel + ' ' + meta.title + ' ' + meta.key,
                run: function () { commandPaletteScrollToRow($row); }
            });
        });

        commandPaletteSectionTypes.forEach(function (entry) {
            commands.push({
                id: 'add-' + entry[0], group: 'Tilføj element', label: 'Tilføj ' + entry[1], detail: entry[0],
                keywords: 'tilføj nyt element sektion ' + entry[0] + ' ' + entry[1],
                run: function () {
                    const $row = addPageSection(entry[0]);
                    if ($row.length) { commandPaletteScrollToRow($row); }
                }
            });
        });

        [['desktop','Desktop'],['tablet','Tablet'],['mobile','Mobil']].forEach(function (entry) {
            commands.push({
                id: 'device-' + entry[0], group: 'Visning', label: 'Vis ' + entry[1], detail: 'Responsive preview',
                keywords: 'visning preview responsive device ' + entry[0] + ' ' + entry[1],
                run: function () { $('.h18-preview-device[data-device="' + entry[0] + '"]').first().trigger('click'); }
            });
        });
        [['normal','Normal'],['hover','Hover']].forEach(function (entry) {
            commands.push({
                id: 'state-' + entry[0], group: 'Visning', label: 'State: ' + entry[1], detail: 'Design-state',
                keywords: 'state normal hover design ' + entry[0] + ' ' + entry[1],
                run: function () { ensureCanvasToolbar(); $('.h18-preview-state[data-state="' + entry[0] + '"]').first().trigger('click'); }
            });
        });

        commands.push(
            { id: 'undo', group: 'Redigering', label: 'Fortryd', detail: 'Ctrl/Cmd+Z', keywords: 'fortryd undo tilbage', disabled: function () { return editorHistoryIndex <= 0; }, run: editorHistoryUndo },
            { id: 'redo', group: 'Redigering', label: 'Gendan', detail: 'Ctrl/Cmd+Shift+Z', keywords: 'gendan redo frem', disabled: function () { return editorHistoryIndex < 0 || editorHistoryIndex >= editorHistoryEntries.length - 1; }, run: editorHistoryRedo },
            { id: 'previous-section', group: 'Navigation', label: 'Forrige element', detail: 'Alt+↑', keywords: 'forrige element op navigation', run: function () { commandPaletteMoveSection(-1); } },
            { id: 'next-section', group: 'Navigation', label: 'Næste element', detail: 'Alt+↓', keywords: 'næste element ned navigation', run: function () { commandPaletteMoveSection(1); } },
            { id: 'copy-design', group: 'Design', label: 'Kopiér design', detail: 'Valgt element', keywords: 'kopier kopiér design stil', disabled: function () { return !$('#h18-inspector-copy-design').length || $('#h18-inspector-copy-design').prop('disabled'); }, run: function () { $('#h18-inspector-copy-design').trigger('click'); } },
            { id: 'paste-design', group: 'Design', label: 'Indsæt design', detail: 'Valgt element', keywords: 'indsæt paste design stil', disabled: function () { return !$('#h18-inspector-paste-design').length || $('#h18-inspector-paste-design').prop('disabled'); }, run: function () { $('#h18-inspector-paste-design').trigger('click'); } },
            { id: 'save-component', group: 'Design', label: 'Gem som komponent', detail: 'Valgt element', keywords: 'gem komponent genbrugelig preset', disabled: function () { return !$('#h18-save-section-preset').length || $('#h18-save-section-preset').prop('disabled'); }, run: function () { $('#h18-save-section-preset').trigger('click'); } },
            { id: 'focus-save', group: 'Side', label: 'Gå til Gem / ændringsbeskrivelse', detail: 'Gemmer ikke automatisk', keywords: 'gem save ændring version note beskrivelse', run: function () {
                const $note = $('#h18-page-editor-form [name="page_change_note"]');
                if ($note.length) { $note.get(0).scrollIntoView({ behavior: 'smooth', block: 'center' }); $note.trigger('focus'); }
                else { $('#h18-page-editor-form .h18-form-actions').last().get(0)?.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
            } },
            { id: 'public-page', group: 'Side', label: 'Åbn offentlig side', detail: 'Ny fane', keywords: 'åbn offentlig side preview frontend', disabled: function () { return !$('.h18-toolbar a[target="_blank"]').first().attr('href'); }, run: function () {
                const href = String($('.h18-toolbar a[target="_blank"]').first().attr('href') || '');
                if (href) { window.open(href, '_blank', 'noopener'); }
            } }
        );
        return commands;
    }

    function commandPaletteFilteredCommands(query) {
        const normalized = commandPaletteNormalize(query);
        const terms = normalized ? normalized.split(' ').filter(Boolean) : [];
        return commandPaletteBuildCommands().filter(function (command) {
            if (!terms.length) { return true; }
            const haystack = commandPaletteNormalize([command.group, command.label, command.detail, command.keywords].join(' '));
            return terms.every(function (term) { return haystack.indexOf(term) !== -1; });
        }).slice(0, 60);
    }

    function commandPaletteUpdateActive() {
        const $items = $('#h18-command-palette-results .h18-command-result');
        if (!$items.length) {
            $('#h18-command-palette-search').removeAttr('aria-activedescendant');
            return;
        }
        commandPaletteActiveIndex = Math.max(0, Math.min(commandPaletteActiveIndex, $items.length - 1));
        $items.removeClass('is-active').attr('aria-selected', 'false');
        const $active = $items.eq(commandPaletteActiveIndex).addClass('is-active').attr('aria-selected', 'true');
        $('#h18-command-palette-search').attr('aria-activedescendant', String($active.attr('id') || ''));
        const node = $active.get(0);
        if (node && typeof node.scrollIntoView === 'function') { node.scrollIntoView({ block: 'nearest' }); }
    }

    function commandPaletteRender(query) {
        const $results = $('#h18-command-palette-results').empty();
        commandPaletteVisibleCommands = commandPaletteFilteredCommands(query);
        commandPaletteActiveIndex = 0;
        let lastGroup = '';
        commandPaletteVisibleCommands.forEach(function (command, index) {
            if (command.group !== lastGroup) {
                $results.append($('<div>', { class: 'h18-command-group-label', text: command.group }));
                lastGroup = command.group;
            }
            const disabled = typeof command.disabled === 'function' ? Boolean(command.disabled()) : Boolean(command.disabled);
            const $button = $('<button>', {
                type: 'button', id: 'h18-command-result-' + index, class: 'h18-command-result' + (disabled ? ' is-disabled' : ''),
                role: 'option', 'aria-selected': 'false', disabled: disabled, 'data-command-index': index
            });
            $button.append($('<span>', { class: 'h18-command-result-main', text: command.label }));
            if (command.detail) { $button.append($('<small>', { text: command.detail })); }
            $results.append($button);
        });
        $('#h18-command-palette-empty').prop('hidden', commandPaletteVisibleCommands.length > 0);
        commandPaletteUpdateActive();
    }

    function commandPaletteOpen() {
        if (!$pageSections.length) { return; }
        commandPalettePreviousFocus = document.activeElement;
        $('#h18-command-palette').prop('hidden', false);
        $('#h18-command-palette-open').attr('aria-expanded', 'true');
        $('body').addClass('h18-command-palette-visible');
        const $search = $('#h18-command-palette-search').val('');
        commandPaletteRender('');
        window.setTimeout(function () { $search.trigger('focus').trigger('select'); }, 0);
    }

    function commandPaletteClose(restoreFocus) {
        $('#h18-command-palette').prop('hidden', true);
        $('#h18-command-palette-open').attr('aria-expanded', 'false');
        $('body').removeClass('h18-command-palette-visible');
        commandPaletteVisibleCommands = [];
        if (restoreFocus !== false && commandPalettePreviousFocus && typeof commandPalettePreviousFocus.focus === 'function') {
            commandPalettePreviousFocus.focus();
        }
        commandPalettePreviousFocus = null;
    }

    function commandPaletteExecute(index) {
        const command = commandPaletteVisibleCommands[Number(index) || 0];
        if (!command) { return; }
        const disabled = typeof command.disabled === 'function' ? Boolean(command.disabled()) : Boolean(command.disabled);
        if (disabled) { return; }
        commandPaletteClose(false);
        try { command.run(); } finally {
            if ($inspectedSection.length) { window.setTimeout(function () { $inspectedSection.find('.h18-canvas-preview').first().trigger('focus'); }, 0); }
        }
    }

    function commandPaletteMoveSection(direction) {
        const $rows = $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)');
        if (!$rows.length) { return; }
        let current = $inspectedSection.length ? $rows.index($inspectedSection) : -1;
        if (current < 0) { current = direction > 0 ? -1 : 0; }
        let next = current + (direction > 0 ? 1 : -1);
        if (next < 0) { next = $rows.length - 1; }
        if (next >= $rows.length) { next = 0; }
        commandPaletteScrollToRow($rows.eq(next));
    }

    function commandPaletteFocusable() {
        return $('#h18-command-palette .h18-command-palette-dialog').find('input:not(:disabled),button:not(:disabled),[href],select:not(:disabled),textarea:not(:disabled),[tabindex]:not([tabindex="-1"])').filter(':visible');
    }

    $(document).on('click', '#h18-command-palette-open', function (event) { event.preventDefault(); commandPaletteOpen(); });
    $(document).on('click', '.h18-command-palette-close,[data-command-close="1"]', function (event) { event.preventDefault(); commandPaletteClose(true); });
    $(document).on('input', '#h18-command-palette-search', function () { commandPaletteRender($(this).val()); });
    $(document).on('mouseenter', '.h18-command-result:not(:disabled)', function () {
        commandPaletteActiveIndex = Number($(this).attr('data-command-index')) || 0;
        commandPaletteUpdateActive();
    });
    $(document).on('click', '.h18-command-result:not(:disabled)', function () { commandPaletteExecute($(this).attr('data-command-index')); });

    $(document).on('keydown.h18CommandPalette', function (event) {
        const key = String(event.key || '').toLowerCase();
        if ((event.ctrlKey || event.metaKey) && key === 'k') {
            if (commandPaletteIsOpen()) {
                event.preventDefault();
                $('#h18-command-palette-search').trigger('focus').trigger('select');
                return;
            }
            if (commandPaletteIsEditableTarget(event.target)) { return; }
            event.preventDefault();
            commandPaletteOpen();
            return;
        }
        if (!commandPaletteIsOpen()) {
            if (event.altKey && !event.ctrlKey && !event.metaKey && (event.key === 'ArrowUp' || event.key === 'ArrowDown') && !commandPaletteIsEditableTarget(event.target)) {
                event.preventDefault();
                commandPaletteMoveSection(event.key === 'ArrowDown' ? 1 : -1);
            }
            return;
        }
        if (event.key === 'Escape') { event.preventDefault(); commandPaletteClose(true); return; }
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            event.preventDefault();
            if (!commandPaletteVisibleCommands.length) { return; }
            const direction = event.key === 'ArrowDown' ? 1 : -1;
            let next = commandPaletteActiveIndex;
            do {
                next = (next + direction + commandPaletteVisibleCommands.length) % commandPaletteVisibleCommands.length;
            } while ($('#h18-command-result-' + next).prop('disabled') && next !== commandPaletteActiveIndex);
            commandPaletteActiveIndex = next;
            commandPaletteUpdateActive();
            return;
        }
        if (event.key === 'Enter' && $(event.target).is('#h18-command-palette-search')) {
            event.preventDefault(); commandPaletteExecute(commandPaletteActiveIndex); return;
        }
        if (event.key === 'Tab') {
            const $focusable = commandPaletteFocusable();
            if (!$focusable.length) { event.preventDefault(); return; }
            const first = $focusable.get(0), last = $focusable.get($focusable.length - 1);
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        }
    });

'''
if insert_anchor not in js:
    raise SystemExit('command palette JS insertion anchor not found')
js = js.replace(insert_anchor, command_js + insert_anchor, 1)
js_path.write_text(js, encoding='utf-8')

css = css_path.read_text(encoding='utf-8')
css_marker = '/* v0.5.14 command palette */'
if css_marker in css:
    raise SystemExit('v0.5.14 command palette CSS already present')
css_add = r'''

/* v0.5.14 command palette */
body.h18-command-palette-visible{overflow:hidden}
.h18-command-palette[hidden]{display:none!important}
.h18-command-palette{position:fixed;inset:0;z-index:100000;display:flex;align-items:flex-start;justify-content:center;padding:10vh 18px 24px}
.h18-command-palette-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.48);backdrop-filter:blur(2px)}
.h18-command-palette-dialog{position:relative;width:min(720px,100%);max-height:78vh;display:flex;flex-direction:column;background:#fff;border:1px solid #c3c4c7;border-radius:12px;box-shadow:0 24px 80px rgba(0,0,0,.28);overflow:hidden}
.h18-command-palette-header{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;padding:16px 18px 10px}
.h18-command-palette-header>div{display:flex;flex-direction:column;gap:3px}.h18-command-palette-header strong{font-size:16px}.h18-command-palette-header small{color:#646970}
.h18-command-palette-search{width:calc(100% - 36px);margin:0 18px 10px;padding:11px 13px!important;font-size:16px!important;border-radius:7px!important}
.h18-command-palette-results{overflow:auto;padding:0 10px 10px;min-height:80px}
.h18-command-group-label{padding:9px 8px 4px;color:#646970;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.h18-command-result{width:100%;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:12px;text-align:left;border:0;background:transparent;padding:9px 10px;border-radius:7px;cursor:pointer;color:#1d2327}
.h18-command-result:hover,.h18-command-result.is-active{background:#f0f0f1}.h18-command-result:focus-visible{outline:2px solid #2271b1;outline-offset:-2px}
.h18-command-result.is-disabled{opacity:.42;cursor:not-allowed}.h18-command-result-main{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.h18-command-result small{color:#646970;text-align:right}
.h18-command-palette-empty{padding:24px 18px;text-align:center;color:#646970}
.h18-command-palette-footer{display:flex;gap:14px;flex-wrap:wrap;padding:9px 18px;border-top:1px solid #dcdcde;background:#f6f7f7;color:#646970;font-size:11px}
.h18-command-palette-open{white-space:nowrap}
@media(max-width:782px){.h18-command-palette{padding:7vh 10px 16px}.h18-command-palette-dialog{max-height:84vh}.h18-command-result{grid-template-columns:1fr}.h18-command-result small{text-align:left}.h18-command-palette-footer{gap:8px 12px}}
'''
css_path.write_text(css.rstrip() + css_add + '\n', encoding='utf-8')

readme = readme_path.read_text(encoding='utf-8')
readme = replace_once(readme, 'Version: 0.5.13', 'Version: 0.5.14', 'readme top version')
release_anchor = '== Version 0.5.13 – Lokal autosave og crash recovery ==\n'
release_new = '''== Version 0.5.14 – Kommandopalette og hurtignavigation ==\n\nNyt:\n- Ctrl/Cmd+K åbner en søgbar kommandopalette uden for aktive tekstfelter\n- dynamiske Gå til element-kommandoer bygges fra sidens aktuelle sektioner, overskrifter og elementnøgler\n- tilføj alle centrale elementtyper direkte fra paletten\n- skift Desktop/Tablet/Mobil og Normal/Hover fra tastaturet\n- Fortryd/Gendan, Kopiér/Indsæt design og Gem som komponent er tilgængelige som kommandoer\n- Gem-kommandoen navigerer kun til ændringsbeskrivelsen og udfører aldrig en rigtig Gem automatisk\n- Alt+Pil op/ned skifter mellem sideelementer uden at overtage genveje inde i tekstfelter\n- Escape lukker, piletaster vælger, Enter udfører og Tab holdes inde i dialogen\n- page-editor schema forbliver 1.12; funktionen er editor-only og ændrer ikke frontend-data\n\n'''+release_anchor
readme = replace_once(readme, release_anchor, release_new, 'readme v0.5.14 section')
readme_path.write_text(readme, encoding='utf-8')

print('v0.5.14 command palette patch applied')
