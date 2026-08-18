jQuery(function ($) {
    'use strict';

    const config = window.Hangar18SideHealth || {};
    const $form = $('#h18-page-editor-form');
    const $inspector = $('#h18-page-inspector');
    const $sections = $('#h18-page-sections-sortable');
    if (!$form.length || !$inspector.length || !config.ajaxUrl || !config.nonce) { return; }

    let timer = null;
    let requestSerial = 0;
    let pendingXhr = null;

    const $panel = $(
        '<section id="h18-ud-side-health-panel" class="h18-ud-side-health-panel">' +
          '<div class="h18-ud-health-head"><div><strong>Side Health</strong><small>Live · ugemte ændringer medregnes</small></div><button type="button" class="button button-small h18-ud-health-refresh">Opdatér</button></div>' +
          '<div class="h18-ud-health-summary"><div class="h18-ud-health-score" aria-label="Side Health score"><span>–</span><small>/100</small></div><div class="h18-ud-health-areas"></div></div>' +
          '<div class="h18-ud-health-status" aria-live="polite">Klar til analyse</div>' +
          '<div class="h18-ud-health-filters" role="group" aria-label="Side Health filtre"><button type="button" class="is-active" data-filter="all">Alle</button><button type="button" data-filter="hard">Fejl</button><button type="button" data-filter="warning">Advarsler</button></div>' +
          '<div class="h18-ud-health-issues"></div>' +
        '</section>'
    );

    const $tabs = $inspector.find('.h18-inspector-tabs').first();
    if ($tabs.length) { $panel.insertAfter($tabs); }
    else { $inspector.prepend($panel); }

    function sanitizeKey(value) {
        return String(value || '').trim().toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '');
    }

    function directSectionFields($row) {
        const result = {};
        const checkboxNames = new Set();
        $row.find('[name]').each(function () {
            const name = String(this.name || '');
            const match = name.match(/^sections\[\d+\]\[([^\]]+)\]$/);
            if (!match) { return; }
            const field = match[1];
            if (this.type === 'checkbox') { checkboxNames.add(field); }
        });
        $row.find('[name]').each(function () {
            const name = String(this.name || '');
            const match = name.match(/^sections\[\d+\]\[([^\]]+)\]$/);
            if (!match) { return; }
            const field = match[1];
            if (checkboxNames.has(field) && this.type !== 'checkbox') { return; }
            if (this.type === 'checkbox') { result[field] = !!this.checked; return; }
            let value = $(this).val();
            if (Array.isArray(value)) { value = value.join(','); }
            if (this.type === 'number' || /(?:Id|Px|Percent|Columns|Limit|Order|Level)$/.test(field)) {
                const n = parseInt(String(value || ''), 10);
                result[field] = Number.isFinite(n) ? n : 0;
            } else {
                result[field] = String(value == null ? '' : value);
            }
        });
        result.Key = String($row.find('.h18-page-section-key').val() || result.Key || '');
        result.Type = String($row.attr('data-section-type') || result.Type || 'text');
        return result;
    }

    function buildState() {
        const sections = [];
        $sections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            sections.push(directSectionFields($(this)));
        });
        return {
            Version: String($form.find('[name="version"],[name="page_version"]').first().val() || '1.22'),
            PageSlug: sanitizeKey($form.find('[name="page_slug"]').val() || ''),
            PageTitle: String($form.find('[name="editor_page_title"]').val() || ''),
            ContentVersion: parseInt(String($form.find('[name="content_version"]').val() || '0'), 10) || 0,
            DataContextType: sanitizeKey($form.find('[name="data_context_type"]').val() || $('#h18-page-data-context-type').val() || ''),
            DataContextEntryId: parseInt(String($form.find('[name="data_context_entry_id"]').val() || $('#h18-page-data-context-entry').val() || '0'), 10) || 0,
            Sections: sections
        };
    }

    function buildSeo(state) {
        const explicitTitle = String($form.find('[name="seo_title"]').val() || '').trim();
        const title = explicitTitle || String(state.PageTitle || '').trim();
        return {
            Title: title,
            MetaDescription: String($form.find('[name="meta_description"],[name="seo_description"]').first().val() || ''),
            CanonicalUrl: String($form.find('[name="canonical_url"]').val() || ''),
            Index: true,
            Follow: true,
            SocialTitle: String($form.find('[name="social_title"]').val() || title),
            SocialDescription: String($form.find('[name="social_description"]').val() || ''),
            SocialImageMediaId: parseInt(String($form.find('[name="social_image_media_id"]').val() || '0'), 10) || 0
        };
    }

    function severityLabel(severity) {
        return ({critical:'Kritisk',error:'Fejl',warning:'Advarsel',info:'Info'})[severity] || severity;
    }

    function areaLabel(area) {
        return ({accessibility:'Tilgængelighed',responsive:'Mobil',design:'Design',seo:'SEO',performance:'Performance'})[area] || area;
    }

    function renderReport(report) {
        const score = Math.max(0, Math.min(100, parseInt(report.Score, 10) || 0));
        $panel.find('.h18-ud-health-score span').text(score);
        $panel.find('.h18-ud-health-score').css('--h18-health-score', score);
        const areas = report.Areas || {};
        const areaOrder = ['Design','Mobile','Accessibility','Performance','SEO'];
        $panel.find('.h18-ud-health-areas').html(areaOrder.map(function (name) {
            const value = Math.max(0, Math.min(100, parseInt(areas[name], 10) || 0));
            return '<div><span>' + $('<div>').text(name).html() + '</span><strong>' + value + '</strong></div>';
        }).join(''));

        const issues = Array.isArray(report.Issues) ? report.Issues : [];
        const $list = $panel.find('.h18-ud-health-issues').empty();
        if (!issues.length) {
            $list.html('<div class="h18-ud-health-clean"><span class="dashicons dashicons-yes-alt"></span><strong>Ingen fund</strong><small>Det aktuelle snapshot har ingen Side Health issues.</small></div>');
        } else {
            issues.forEach(function (issue) {
                const severity = String(issue.Severity || 'warning').toLowerCase();
                const elementKeyRaw = String(issue.ElementKey || '');
                const elementKey = elementKeyRaw.split(':')[0];
                const $item = $('<article>', { class: 'h18-ud-health-issue severity-' + severity, 'data-severity': severity });
                const $title = $('<div>', { class: 'h18-ud-health-issue-title' })
                    .append($('<span>', { class: 'h18-ud-health-severity', text: severityLabel(severity) }))
                    .append($('<strong>', { text: areaLabel(String(issue.Area || '')) }));
                $item.append($title, $('<p>', { text: String(issue.Message || issue.Code || 'Side Health issue') }));
                const $meta = $('<div>', { class: 'h18-ud-health-issue-meta' }).append($('<code>', { text: String(issue.Code || '') }));
                if (elementKey) {
                    $meta.append($('<button>', { type: 'button', class: 'button-link h18-ud-health-goto', 'data-element-key': elementKey, text: 'Gå til ' + elementKey }));
                }
                $item.append($meta);
                $list.append($item);
            });
        }
        $panel.attr('data-hard-failures', String(parseInt(report.HardFailureCount, 10) || 0));
        applyFilter();
    }

    function analyze() {
        const state = buildState();
        if (!state.Sections.length) {
            $panel.find('.h18-ud-health-status').text('Ingen elementer at analysere');
            return;
        }
        const serial = ++requestSerial;
        if (pendingXhr && pendingXhr.readyState !== 4) { pendingXhr.abort(); }
        $panel.addClass('is-loading');
        $panel.find('.h18-ud-health-status').text('Analyserer ' + state.Sections.length + ' elementer…');
        pendingXhr = $.post(config.ajaxUrl, {
            action: 'h18_ud_side_health',
            nonce: config.nonce,
            state_json: JSON.stringify(state),
            seo_json: JSON.stringify(buildSeo(state))
        }).done(function (response) {
            if (serial !== requestSerial) { return; }
            if (!response || !response.success || !response.data || !response.data.report) {
                throw new Error((response && response.data && response.data.message) || 'Ukendt Side Health-fejl');
            }
            renderReport(response.data.report);
            $panel.find('.h18-ud-health-status').text('Opdateret · ' + state.Sections.length + ' elementer');
        }).fail(function (xhr, status) {
            if (status === 'abort' || serial !== requestSerial) { return; }
            const message = xhr.responseJSON && xhr.responseJSON.data && xhr.responseJSON.data.message ? xhr.responseJSON.data.message : 'Side Health kunne ikke beregnes';
            $panel.find('.h18-ud-health-status').text(message);
        }).always(function () {
            if (serial === requestSerial) { $panel.removeClass('is-loading'); }
        });
    }

    function schedule() {
        window.clearTimeout(timer);
        timer = window.setTimeout(analyze, parseInt(config.debounceMs, 10) || 650);
    }

    function applyFilter() {
        const filter = String($panel.find('.h18-ud-health-filters button.is-active').data('filter') || 'all');
        $panel.find('.h18-ud-health-issue').each(function () {
            const severity = String($(this).data('severity') || 'warning');
            const visible = filter === 'all' || (filter === 'hard' && (severity === 'critical' || severity === 'error')) || (filter === 'warning' && severity === 'warning');
            $(this).toggle(visible);
        });
    }

    $panel.on('click', '.h18-ud-health-refresh', analyze);
    $panel.on('click', '.h18-ud-health-filters button', function () {
        $panel.find('.h18-ud-health-filters button').removeClass('is-active');
        $(this).addClass('is-active');
        applyFilter();
    });
    $panel.on('click', '.h18-ud-health-goto', function () {
        const key = String($(this).data('element-key') || '');
        if (!key) { return; }
        const $navigator = $('#h18-page-navigator-list .h18-navigator-item').filter(function () {
            return String($(this).attr('data-section-key') || '') === key;
        }).first();
        if ($navigator.length) {
            const $button = $navigator.find('.h18-navigator-select').first();
            if ($button.length) { $button.trigger('click'); }
            $navigator.get(0).scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            return;
        }
        const $row = $sections.children('.h18-page-section-row').filter(function () {
            return String($(this).find('.h18-page-section-key').val() || '') === key;
        }).first();
        if ($row.length) { $row.get(0).scrollIntoView({ block: 'center', behavior: 'smooth' }); }
    });

    $form.on('input change', 'input,select,textarea', schedule);
    if ($sections.length && window.MutationObserver) {
        new MutationObserver(schedule).observe($sections.get(0), { childList: true, subtree: false });
    }
    window.setTimeout(analyze, 250);
});
