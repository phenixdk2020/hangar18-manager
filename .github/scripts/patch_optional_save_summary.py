from pathlib import Path

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor, found {count}')
    return text.replace(old, new, 1)

# --- PHP UI: optional user comment + automatic summary preview/hidden value ---
old_ui = '''                        <div class="h18-field"><label><strong>Hvad er ændret?</strong></label><textarea name="page_change_note" rows="3" maxlength="500" placeholder="Fx Rettet overskrift, ændret luft mellem kort og udskiftet kontaktknappen."></textarea><p class="description">Skal udfyldes ved en rigtig gemning. Teksten gemmes sammen med versionsnummer, tidspunkt, bruger og backup. Ved WhatIf er feltet valgfrit.</p></div>'''
new_ui = '''                        <div class="h18-field">
                            <label><strong>Egen kommentar (valgfri)</strong></label>
                            <textarea name="page_change_note" rows="3" maxlength="500" placeholder="Valgfrit: skriv evt. hvorfor du lavede ændringen eller noget systemet ikke selv kan se."></textarea>
                            <input type="hidden" name="page_auto_change_summary" id="h18-page-auto-change-summary" value="" />
                            <p class="description">Du behøver ikke skrive noget for at gemme. Systemet laver automatisk et kort resumé af ændringerne og gemmer det i versionshistorikken. Din egen kommentar tilføjes kun, hvis du skriver en.</p>
                            <p class="description"><strong>Automatisk resumé:</strong> <span id="h18-page-auto-change-summary-preview">Beregnes ud fra ændringerne på siden…</span></p>
                        </div>'''
php = replace_once(php, old_ui, new_ui, 'page change note UI')

# --- PHP server-side fallback summary helpers ---
handler_anchor = '''    public function handle_save_page_editor() {'''
helper_code = '''    private function page_change_summary_section_label_v071($section, $fallback = '') {
        if (!is_array($section)) {
            return $fallback !== '' ? $fallback : 'element';
        }
        foreach (['NavigatorLabel', 'Title', 'Heading', 'Name', 'Key'] as $field) {
            $value = trim((string) ($section[$field] ?? ''));
            if ($value !== '') {
                return mb_substr(wp_strip_all_tags($value), 0, 80);
            }
        }
        return $fallback !== '' ? $fallback : 'element';
    }

    private function summarize_page_editor_changes_v071($before, $after) {
        $before = is_array($before) ? $before : [];
        $after = is_array($after) ? $after : [];
        $parts = [];

        if (trim((string) ($before['PageTitle'] ?? '')) !== trim((string) ($after['PageTitle'] ?? ''))) {
            $parts[] = 'Sidetitel ændret';
        }

        $before_sections = is_array($before['Sections'] ?? null) ? array_values($before['Sections']) : [];
        $after_sections = is_array($after['Sections'] ?? null) ? array_values($after['Sections']) : [];
        $before_map = [];
        $after_map = [];
        $before_order = [];
        $after_order = [];

        foreach ($before_sections as $index => $section) {
            if (!is_array($section)) { continue; }
            $key = trim((string) ($section['Key'] ?? ''));
            if ($key === '') { $key = '__before_' . $index; }
            $before_map[$key] = $section;
            $before_order[] = $key;
        }
        foreach ($after_sections as $index => $section) {
            if (!is_array($section)) { continue; }
            $key = trim((string) ($section['Key'] ?? ''));
            if ($key === '') { $key = '__after_' . $index; }
            $after_map[$key] = $section;
            $after_order[] = $key;
        }

        $added = array_values(array_diff(array_keys($after_map), array_keys($before_map)));
        $removed = array_values(array_diff(array_keys($before_map), array_keys($after_map)));
        if ($added) {
            $labels = array_map(function ($key) use ($after_map) {
                return '“' . $this->page_change_summary_section_label_v071($after_map[$key], $key) . '”';
            }, array_slice($added, 0, 3));
            $parts[] = count($added) . ' element' . (count($added) === 1 ? '' : 'er') . ' tilføjet' . ($labels ? ': ' . implode(', ', $labels) : '');
        }
        if ($removed) {
            $labels = array_map(function ($key) use ($before_map) {
                return '“' . $this->page_change_summary_section_label_v071($before_map[$key], $key) . '”';
            }, array_slice($removed, 0, 3));
            $parts[] = count($removed) . ' element' . (count($removed) === 1 ? '' : 'er') . ' fjernet' . ($labels ? ': ' . implode(', ', $labels) : '');
        }

        $before_common_order = array_values(array_filter($before_order, function ($key) use ($after_map) { return isset($after_map[$key]); }));
        $after_common_order = array_values(array_filter($after_order, function ($key) use ($before_map) { return isset($before_map[$key]); }));
        if ($before_common_order !== $after_common_order) {
            $parts[] = 'Elementrækkefølge ændret';
        }

        $changed = [];
        foreach (array_intersect(array_keys($before_map), array_keys($after_map)) as $key) {
            $left = $before_map[$key];
            $right = $after_map[$key];
            unset($left['Order'], $left['ResetVotes'], $right['Order'], $right['ResetVotes']);
            if (wp_json_encode($left) !== wp_json_encode($right)) {
                $changed[] = $this->page_change_summary_section_label_v071($after_map[$key], $key);
            }
        }
        if ($changed) {
            $shown = array_slice(array_values(array_unique($changed)), 0, 3);
            $quoted = array_map(function ($label) { return '“' . $label . '”'; }, $shown);
            $parts[] = 'Indhold/design ændret på ' . implode(', ', $quoted) . (count($changed) > count($shown) ? ' +' . (count($changed) - count($shown)) . ' mere' : '');
        }

        if (!$parts) {
            $parts[] = 'Ingen synlige ændringer registreret; ny version gemt';
        }
        return mb_substr(implode(' · ', $parts), 0, 420);
    }

'''
php = replace_once(php, handler_anchor, helper_code + handler_anchor, 'save summary helper insertion')

# --- PHP request values: user note is optional; automatic summary is separate ---
old_read = '''        $current = $this->get_page_editor_data($slug, $page);
        $change_note = sanitize_textarea_field((string) wp_unslash($_POST['page_change_note'] ?? ''));'''
new_read = '''        $current = $this->get_page_editor_data($slug, $page);
        $user_change_note = sanitize_textarea_field((string) wp_unslash($_POST['page_change_note'] ?? ''));
        $auto_change_summary = sanitize_text_field((string) wp_unslash($_POST['page_auto_change_summary'] ?? ''));'''
php = replace_once(php, old_read, new_read, 'save note request values')

old_required = '''        if (trim($change_note) === '') {
            $this->set_notice('error', 'Skriv kort, hvad du har ændret, før siden gemmes som en ny version.');
            $this->redirect_page_editor($slug);
        }

        try {'''
new_required = '''        if (trim($auto_change_summary) === '') {
            $auto_change_summary = $this->summarize_page_editor_changes_v071($current, $data);
        }
        if (trim($auto_change_summary) === '') {
            $auto_change_summary = 'Siden er gemt med ændringer.';
        }
        $change_note = 'Automatisk: ' . $auto_change_summary;
        if (trim($user_change_note) !== '') {
            $change_note .= "\nEgen kommentar: " . $user_change_note;
        }
        $change_note = mb_substr($change_note, 0, 1000);

        try {'''
php = replace_once(php, old_required, new_required, 'remove mandatory note server gate')

old_history = '''                'ChangeNote'     => $change_note,'''
new_history = '''                'ChangeNote'       => $change_note,
                'AutoChangeSummary' => $auto_change_summary,
                'UserChangeNote'   => $user_change_note,'''
php = replace_once(php, old_history, new_history, 'version history summary fields')

php = php.replace(
    'Ændringsbeskrivelse, fuld backup, sidekopi og WordPress-revision er oprettet.',
    'Automatisk ændringsresumé, fuld backup, sidekopi og WordPress-revision er oprettet.',
    1,
)

# --- JavaScript: deterministic editor-state summary ---
js_decl_anchor = '''    let h18EditorDirtyV064 = false;
    let h18EditorSubmittingV064 = false;'''
js_summary_code = r'''    let h18EditorDirtyV064 = false;
    let h18EditorSubmittingV064 = false;

    // v0.7.1: deterministic automatic change summary; manual note remains optional.
    const $h18AutoSummaryInputV071 = $('#h18-page-auto-change-summary');
    const $h18AutoSummaryPreviewV071 = $('#h18-page-auto-change-summary-preview');
    let h18AutoSummaryBaselineV071 = null;
    let h18AutoSummaryTimerV071 = null;

    function h18SummaryFieldPathV071(name) {
        const raw = String(name || '');
        const tokens = [];
        const re = /\[([^\]]*)\]/g;
        let match;
        while ((match = re.exec(raw)) !== null) { tokens.push(String(match[1] || '')); }
        let cut = -1;
        for (let i = 0; i < tokens.length; i += 1) {
            if (/^\d+$/.test(tokens[i])) { cut = i; break; }
        }
        const remaining = cut >= 0 ? tokens.slice(cut + 1) : tokens;
        return remaining.length ? remaining.join('.') : raw;
    }

    function h18SummaryInputValueV071($input) {
        const type = String($input.attr('type') || '').toLowerCase();
        if (type === 'radio') { return $input.is(':checked') ? String($input.val() || '') : '__h18_skip__'; }
        if (type === 'checkbox') { return $input.is(':checked') ? '1' : '0'; }
        if ($input.is('select[multiple]')) {
            const value = $input.val();
            return Array.isArray(value) ? value.map(String).sort().join('|') : '';
        }
        return String($input.val() == null ? '' : $input.val());
    }

    function h18SummarySectionLabelV071($row, key, type) {
        const candidates = [
            String(pageSectionControls($row, '.h18-section-navigator-label').val() || ''),
            String($row.find('.h18-page-section-title-summary').first().text() || ''),
            String(pageSectionControls($row, '[name$="[Title]"]').first().val() || ''),
            inspectorTypeLabel(type || String($row.attr('data-section-type') || '')),
            key
        ];
        for (let i = 0; i < candidates.length; i += 1) {
            const value = String(candidates[i] || '').trim();
            if (value) { return value.replace(/\s+/g, ' ').slice(0, 80); }
        }
        return 'Element';
    }

    function h18CollectChangeSummaryModelV071() {
        const sections = [];
        $pageSections.children('.h18-page-section-row').each(function (index) {
            const $row = $(this);
            if ($row.hasClass('h18-page-section-removed')) { return; }
            const type = String($row.attr('data-section-type') || 'text');
            const key = String($row.find('.h18-page-section-key').first().val() || ('section-' + index));
            const fields = {};
            $row.find(':input[name]').each(function () {
                const $input = $(this);
                const inputType = String($input.attr('type') || '').toLowerCase();
                if (['button','submit','reset','file'].includes(inputType)) { return; }
                const path = h18SummaryFieldPathV071($input.attr('name'));
                if (!path || /(^|\.)(Order|ResetVotes)$/.test(path)) { return; }
                const value = h18SummaryInputValueV071($input);
                if (value === '__h18_skip__') { return; }
                fields[path] = Object.prototype.hasOwnProperty.call(fields, path) ? (String(fields[path]) + '|' + value) : value;
            });
            sections.push({ key: key, type: type, label: h18SummarySectionLabelV071($row, key, type), fields: fields });
        });
        return {
            title: String($h18PageEditorFormV064.find('[name="editor_page_title"]').val() || '').trim(),
            order: sections.map(function (section) { return section.key; }),
            sections: sections
        };
    }

    function h18SummaryCategoryV071(path) {
        const value = String(path || '').toLowerCase();
        if (/(mobile|tablet|responsive|breakpoint)/.test(value)) { return 'Mobil/responsive'; }
        if (/(binding|query|relation|repeater|condition|datacontext|dynamic)/.test(value)) { return 'Dynamisk indhold'; }
        if (/(font|typograph|lineheight|letterspacing|textalign|headingtag|headinglevel)/.test(value)) { return 'Typografi'; }
        if (/(background|color|border|radius|shadow|padding|margin|spacing|gap|width|height|opacity|transform)/.test(value)) { return 'Design'; }
        if (/(layout|parent|grid|flex|align|justify|position|columns|rows|direction|wrap)/.test(value)) { return 'Layout'; }
        return 'Indhold';
    }

    function h18SummaryNamesV071(items) {
        const names = Array.from(new Set((items || []).filter(Boolean)));
        const shown = names.slice(0, 3).map(function (name) { return '“' + String(name).replace(/[“”]/g, '') + '”'; });
        return shown.join(', ') + (names.length > shown.length ? ' +' + (names.length - shown.length) + ' mere' : '');
    }

    function h18BuildAutomaticSummaryV071() {
        const before = h18AutoSummaryBaselineV071;
        const after = h18CollectChangeSummaryModelV071();
        if (!before) { return 'Siden er ændret.'; }
        const parts = [];
        if (before.title !== after.title) { parts.push('Sidetitel ændret'); }

        const beforeMap = {};
        const afterMap = {};
        before.sections.forEach(function (section) { beforeMap[section.key] = section; });
        after.sections.forEach(function (section) { afterMap[section.key] = section; });
        const added = after.sections.filter(function (section) { return !beforeMap[section.key]; });
        const removed = before.sections.filter(function (section) { return !afterMap[section.key]; });
        if (added.length) { parts.push(added.length + ' element' + (added.length === 1 ? '' : 'er') + ' tilføjet: ' + h18SummaryNamesV071(added.map(function (section) { return section.label; }))); }
        if (removed.length) { parts.push(removed.length + ' element' + (removed.length === 1 ? '' : 'er') + ' fjernet: ' + h18SummaryNamesV071(removed.map(function (section) { return section.label; }))); }

        const beforeCommonOrder = before.order.filter(function (key) { return Boolean(afterMap[key]); });
        const afterCommonOrder = after.order.filter(function (key) { return Boolean(beforeMap[key]); });
        if (JSON.stringify(beforeCommonOrder) !== JSON.stringify(afterCommonOrder)) { parts.push('Elementrækkefølge ændret'); }

        const categoryTargets = {};
        Object.keys(beforeMap).forEach(function (key) {
            if (!afterMap[key]) { return; }
            const left = beforeMap[key].fields || {};
            const right = afterMap[key].fields || {};
            const paths = Array.from(new Set(Object.keys(left).concat(Object.keys(right))));
            paths.forEach(function (path) {
                if (String(left[path] == null ? '' : left[path]) === String(right[path] == null ? '' : right[path])) { return; }
                const category = h18SummaryCategoryV071(path);
                categoryTargets[category] = categoryTargets[category] || [];
                categoryTargets[category].push(afterMap[key].label || key);
            });
        });

        ['Indhold','Typografi','Design','Layout','Mobil/responsive','Dynamisk indhold'].forEach(function (category) {
            if (!categoryTargets[category] || !categoryTargets[category].length) { return; }
            parts.push(category + ' ændret på ' + h18SummaryNamesV071(categoryTargets[category]));
        });

        let summary = parts.length ? parts.slice(0, 8).join(' · ') : 'Ingen synlige ændringer registreret; ny version gemmes';
        if (summary.length > 420) { summary = summary.slice(0, 417).replace(/[\s,;:.]+$/, '') + '…'; }
        return summary;
    }

    function h18RefreshAutomaticSummaryV071() {
        if (!$h18AutoSummaryInputV071.length) { return ''; }
        const summary = h18BuildAutomaticSummaryV071();
        $h18AutoSummaryInputV071.val(summary);
        if ($h18AutoSummaryPreviewV071.length) { $h18AutoSummaryPreviewV071.text(summary); }
        return summary;
    }

    function h18ScheduleAutomaticSummaryV071() {
        window.clearTimeout(h18AutoSummaryTimerV071);
        h18AutoSummaryTimerV071 = window.setTimeout(h18RefreshAutomaticSummaryV071, 120);
    }
'''
js = replace_once(js, js_decl_anchor, js_summary_code, 'automatic summary declarations/functions')

old_input_handler = '''        $h18PageEditorFormV064.on('input change', ':input', function () {
            h18EditorMarkDirtyV064();
        });'''
new_input_handler = '''        $h18PageEditorFormV064.on('input change', ':input', function () {
            h18EditorMarkDirtyV064();
            h18ScheduleAutomaticSummaryV071();
        });'''
js = replace_once(js, old_input_handler, new_input_handler, 'summary refresh input handler')

old_submit_gate = '''        $h18PageEditorFormV064.on('submit', function (event) {
            const whatIf = $h18PageEditorFormV064.find('[name="whatif"]').is(':checked');
            const $note = $h18PageEditorFormV064.find('[name="page_change_note"]');
            if (!whatIf && $note.length && !String($note.val() || '').trim()) {
                event.preventDefault();
                h18EditorSetSaveStatusV064('Beskriv ændringen før Gem', 'error');
                $note.trigger('focus');
                return;
            }
            h18EditorSubmittingV064 = true;'''
new_submit_gate = '''        $h18PageEditorFormV064.on('submit', function (event) {
            h18RefreshAutomaticSummaryV071();
            const whatIf = $h18PageEditorFormV064.find('[name="whatif"]').is(':checked');
            h18EditorSubmittingV064 = true;'''
js = replace_once(js, old_submit_gate, new_submit_gate, 'remove mandatory note client gate')

# Establish the comparison baseline after the editor DOM has been initialized.
init_anchor = '''    if ($h18PageEditorFormV064.length) {
        $h18PageEditorFormV064.on('input change', ':input', function () {'''
init_replacement = '''    if ($h18PageEditorFormV064.length) {
        h18AutoSummaryBaselineV071 = h18CollectChangeSummaryModelV071();
        h18RefreshAutomaticSummaryV071();
        $h18PageEditorFormV064.on('input change', ':input', function () {'''
js = replace_once(js, init_anchor, init_replacement, 'automatic summary baseline initialization')

# Guard against accidental reintroduction of mandatory note behavior.
if 'Beskriv ændringen før Gem' in js:
    raise SystemExit('old mandatory client note gate still present')
if 'Skriv kort, hvad du har ændret, før siden gemmes som en ny version.' in php:
    raise SystemExit('old mandatory server note gate still present')

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
