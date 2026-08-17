from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 anchor, found {count}')
    return text.replace(old, new, 1)

php_path=Path('hangar18-manager.php'); js_path=Path('assets/admin.js'); css_path=Path('assets/admin.css'); readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

php=replace_once(php,' * Version: 0.5.18',' * Version: 0.5.19','plugin header')
php=replace_once(php,"    const VERSION = '0.5.18';","    const VERSION = '0.5.19';",'plugin const')

labels_old="""            'accordion'  => 'Accordion',
            'carousel'   => 'Carousel / slider',
            'embed'      => 'Embed / medie-URL',
"""
labels_new="""            'accordion'  => 'Accordion',
            'carousel'   => 'Carousel / slider',
            'container'  => 'Container',
            'flex'       => 'Flex container',
            'grid'       => 'Grid container',
            'embed'      => 'Embed / medie-URL',
"""
php=replace_once(php,labels_old,labels_new,'layout type labels')

# Flat parent-key hierarchy remains diff/revision friendly while rendering as a real DOM tree.
default_anchor="""            'Cards'                 => [],
            'CarouselAutoplay'      => false,
"""
default_new="""            'Cards'                 => [],
            'LayoutParentKey'       => '',
            'LayoutDirection'       => 'Row',
            'LayoutWrap'            => true,
            'LayoutJustify'         => 'Start',
            'LayoutAlign'           => 'Stretch',
            'LayoutGapPx'           => 16,
            'MobileLayoutGapPx'     => 12,
            'LayoutColumns'         => 2,
            'MobileLayoutColumns'   => 1,
            'MobileLayoutStack'     => true,
            'CarouselAutoplay'      => false,
"""
php=replace_once(php,default_anchor,default_new,'layout defaults')

# Normalize enums before Cards normalization.
enum_anchor="""        $cards = [];
        $used_card_keys = [];
"""
enum_new="""        $layout_parent_key = sanitize_key((string) ($raw['LayoutParentKey'] ?? ''));
        $layout_direction = (string) ($raw['LayoutDirection'] ?? 'Row');
        if (!in_array($layout_direction, ['Row', 'Column'], true)) { $layout_direction = 'Row'; }
        $layout_justify = (string) ($raw['LayoutJustify'] ?? 'Start');
        if (!in_array($layout_justify, ['Start', 'Center', 'End', 'SpaceBetween'], true)) { $layout_justify = 'Start'; }
        $layout_align = (string) ($raw['LayoutAlign'] ?? 'Stretch');
        if (!in_array($layout_align, ['Start', 'Center', 'End', 'Stretch'], true)) { $layout_align = 'Stretch'; }

        $cards = [];
        $used_card_keys = [];
"""
php=replace_once(php,enum_anchor,enum_new,'layout enums')

return_anchor="""            'Cards'                  => $cards,
            'CarouselAutoplay'       => array_key_exists('CarouselAutoplay', $raw) ? $this->bool_value($raw['CarouselAutoplay'], false) : false,
"""
return_new="""            'Cards'                  => $cards,
            'LayoutParentKey'        => $layout_parent_key,
            'LayoutDirection'        => $layout_direction,
            'LayoutWrap'             => array_key_exists('LayoutWrap', $raw) ? $this->bool_value($raw['LayoutWrap'], true) : true,
            'LayoutJustify'          => $layout_justify,
            'LayoutAlign'            => $layout_align,
            'LayoutGapPx'            => $this->clamp_int($raw['LayoutGapPx'] ?? 16, 0, 120, 16),
            'MobileLayoutGapPx'      => $this->clamp_int($raw['MobileLayoutGapPx'] ?? 12, 0, 80, 12),
            'LayoutColumns'          => $this->clamp_int($raw['LayoutColumns'] ?? 2, 1, 6, 2),
            'MobileLayoutColumns'    => $this->clamp_int($raw['MobileLayoutColumns'] ?? 1, 1, 3, 1),
            'MobileLayoutStack'      => array_key_exists('MobileLayoutStack', $raw) ? $this->bool_value($raw['MobileLayoutStack'], true) : true,
            'CarouselAutoplay'       => array_key_exists('CarouselAutoplay', $raw) ? $this->bool_value($raw['CarouselAutoplay'], false) : false,
"""
php=replace_once(php,return_anchor,return_new,'layout normalized fields')

# Validate hierarchy after unique keys and sort: parent must be layout-capable, no cycles, max depth 3.
normalize_sort_anchor="""        usort($sections, static function($a, $b) {
            return ((int) $a['Order']) <=> ((int) $b['Order']);
        });

        $title = sanitize_text_field((string) ($raw['PageTitle'] ?? ($page ? $page->post_title : $definitions[$slug])));
"""
normalize_sort_new="""        usort($sections, static function($a, $b) {
            return ((int) $a['Order']) <=> ((int) $b['Order']);
        });

        $layout_parent_types = ['container', 'flex', 'grid'];
        $sections_by_key = [];
        foreach ($sections as $section_index => $candidate) {
            $sections_by_key[(string) $candidate['Key']] = $section_index;
        }
        foreach ($sections as $section_index => &$candidate) {
            $parent_key = sanitize_key((string) ($candidate['LayoutParentKey'] ?? ''));
            if ($parent_key === '') { continue; }
            $self_key = (string) $candidate['Key'];
            $seen = [$self_key => true];
            $cursor = $parent_key;
            $depth = 0;
            $valid_parent = true;
            while ($cursor !== '') {
                $depth++;
                if ($depth > 3 || isset($seen[$cursor]) || !isset($sections_by_key[$cursor])) {
                    $valid_parent = false;
                    break;
                }
                $seen[$cursor] = true;
                $parent_section = $sections[$sections_by_key[$cursor]];
                if (!in_array((string) ($parent_section['Type'] ?? ''), $layout_parent_types, true)) {
                    $valid_parent = false;
                    break;
                }
                $cursor = sanitize_key((string) ($parent_section['LayoutParentKey'] ?? ''));
            }
            if (!$valid_parent) {
                $candidate['LayoutParentKey'] = '';
            }
        }
        unset($candidate);

        $title = sanitize_text_field((string) ($raw['PageTitle'] ?? ($page ? $page->post_title : $definitions[$slug])));
"""
php=replace_once(php,normalize_sort_anchor,normalize_sort_new,'hierarchy validation')

# Schema bump.
if php.count("'Version'        => '1.14'") != 3: raise SystemExit('Expected 3 active schema 1.14 payloads')
php=php.replace("'Version'        => '1.14'","'Version'        => '1.15'")
php=php.replace("'Version' => '1.14',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,","'Version' => '1.15',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,")
php=php.replace("'Version' => '1.14',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,","'Version' => '1.15',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,")

# Render optional child tree inside layout-capable sections.
sig_old="""    private function render_page_editor_section_front($page_id, array $section) {
"""
sig_new="""    private function render_page_editor_section_front($page_id, array $section, $layout_children = '') {
"""
php=replace_once(php,sig_old,sig_new,'renderer signature')

branch_anchor="""        if ($section['Type'] === 'icon') {
"""
layout_branch="""        if (in_array($section['Type'], ['container', 'flex', 'grid'], true)) {
            $justify_map = ['Start'=>'flex-start','Center'=>'center','End'=>'flex-end','SpaceBetween'=>'space-between'];
            $align_map = ['Start'=>'flex-start','Center'=>'center','End'=>'flex-end','Stretch'=>'stretch'];
            $style .= '--h18-layout-gap:' . (int) $section['LayoutGapPx'] . 'px;' .
                '--h18-layout-mobile-gap:' . (int) $section['MobileLayoutGapPx'] . 'px;' .
                '--h18-layout-columns:' . (int) $section['LayoutColumns'] . ';' .
                '--h18-layout-mobile-columns:' . (int) $section['MobileLayoutColumns'] . ';' .
                '--h18-layout-direction:' . strtolower((string) $section['LayoutDirection']) . ';' .
                '--h18-layout-wrap:' . (!empty($section['LayoutWrap']) ? 'wrap' : 'nowrap') . ';' .
                '--h18-layout-justify:' . ($justify_map[$section['LayoutJustify']] ?? 'flex-start') . ';' .
                '--h18-layout-align:' . ($align_map[$section['LayoutAlign']] ?? 'stretch') . ';' .
                '--h18-layout-mobile-direction:' . (!empty($section['MobileLayoutStack']) ? 'column' : strtolower((string) $section['LayoutDirection'])) . ';';
            $layout_class = 'h18-layout-' . sanitize_html_class((string) $section['Type']) . '-children';
            $inner = $title . $content . '<div class="h18-layout-children ' . esc_attr($layout_class) . '">' . (string) $layout_children . '</div>';
        } elseif ($section['Type'] === 'icon') {
"""
php=replace_once(php,branch_anchor,layout_branch,'layout renderer branch')

# Recursive tree helper and early tree path only when parent links exist, preserving legacy imported grouping otherwise.
front_anchor="""    private function render_page_editor_front($page_id, array $data) {
        $html = $this->page_editor_frontend_css($page_id) . '<div class=\"h18-editor-page\">';
        $sections = array_values((array) $data['Sections']);
"""
tree_helper="""    private function render_page_editor_layout_tree($page_id, array $sections, $parent_key = '', $depth = 0) {
        if ($depth > 3) { return ''; }
        $html = '';
        foreach ($sections as $section) {
            if (sanitize_key((string) ($section['LayoutParentKey'] ?? '')) !== sanitize_key((string) $parent_key)) { continue; }
            $children = '';
            if (in_array((string) ($section['Type'] ?? ''), ['container','flex','grid'], true)) {
                $children = $this->render_page_editor_layout_tree($page_id, $sections, (string) $section['Key'], $depth + 1);
            }
            $html .= $this->render_page_editor_section_front($page_id, $section, $children);
        }
        return $html;
    }

    private function render_page_editor_front($page_id, array $data) {
        $html = $this->page_editor_frontend_css($page_id) . '<div class=\"h18-editor-page\">';
        $sections = array_values((array) $data['Sections']);
        $has_layout_hierarchy = false;
        foreach ($sections as $layout_candidate) {
            if (sanitize_key((string) ($layout_candidate['LayoutParentKey'] ?? '')) !== '') { $has_layout_hierarchy = true; break; }
        }
        if ($has_layout_hierarchy) {
            return $html . $this->render_page_editor_layout_tree($page_id, $sections) . '</div>';
        }
"""
php=replace_once(php,front_anchor,tree_helper,'layout tree renderer')

# Existing direct-child editor styling also applies to nested layout children, but not arbitrary imported wrappers.
php=php.replace('body.page .h18-editor-page>.h18-editor-section', ':is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section)')
php=php.replace('body.page .h18-editor-page>.h18-hide-desktop','body.page .h18-editor-page .h18-hide-desktop')
php=php.replace('body.page .h18-editor-page>.h18-hide-tablet','body.page .h18-editor-page .h18-hide-tablet')
php=php.replace('body.page .h18-editor-page>.h18-hide-mobile','body.page .h18-editor-page .h18-hide-mobile')
php=php.replace('body.page .h18-editor-page>.h18-hover-style-custom','body.page .h18-editor-page .h18-hover-style-custom')

# Add layout CSS before form CSS.
layout_css_anchor="""            '.h18-page-form,.h18-page-poll{max-width:760px;margin-inline:auto;text-align:left}' .
"""
if layout_css_anchor not in php:
    short="            '.h18-page-form,.h18-page-poll{max-width:760px;margin-inline:auto;text-align:left}"
    if short not in php: raise SystemExit('layout css anchor missing')
    layout_css="            '.h18-layout-children{box-sizing:border-box;min-width:0;gap:var(--h18-layout-gap,16px)}.h18-layout-container-children{display:grid;grid-template-columns:minmax(0,1fr)}.h18-layout-flex-children{display:flex;flex-direction:var(--h18-layout-direction,row);flex-wrap:var(--h18-layout-wrap,wrap);justify-content:var(--h18-layout-justify,flex-start);align-items:var(--h18-layout-align,stretch)}.h18-layout-grid-children{display:grid;grid-template-columns:repeat(var(--h18-layout-columns,2),minmax(0,1fr));align-items:var(--h18-layout-align,stretch)}.h18-layout-children>.h18-editor-section{min-width:0;margin-top:var(--h18-top,0);margin-bottom:var(--h18-bottom,24px);padding:var(--h18-pad,0) var(--h18-pad-x,var(--h18-pad,0));text-align:var(--h18-align,left)}@media(max-width:782px){.h18-layout-children{gap:var(--h18-layout-mobile-gap,12px)}.h18-layout-flex-children{flex-direction:var(--h18-layout-mobile-direction,column)}.h18-layout-grid-children{grid-template-columns:repeat(var(--h18-layout-mobile-columns,1),minmax(0,1fr))}}' .\n"+short
    php=php.replace(short,layout_css,1)
else:
    layout_css="            '.h18-layout-children{box-sizing:border-box;min-width:0;gap:var(--h18-layout-gap,16px)}.h18-layout-container-children{display:grid;grid-template-columns:minmax(0,1fr)}.h18-layout-flex-children{display:flex;flex-direction:var(--h18-layout-direction,row);flex-wrap:var(--h18-layout-wrap,wrap);justify-content:var(--h18-layout-justify,flex-start);align-items:var(--h18-layout-align,stretch)}.h18-layout-grid-children{display:grid;grid-template-columns:repeat(var(--h18-layout-columns,2),minmax(0,1fr));align-items:var(--h18-layout-align,stretch)}.h18-layout-children>.h18-editor-section{min-width:0;margin-top:var(--h18-top,0);margin-bottom:var(--h18-bottom,24px);padding:var(--h18-pad,0) var(--h18-pad-x,var(--h18-pad,0));text-align:var(--h18-align,left)}@media(max-width:782px){.h18-layout-children{gap:var(--h18-layout-mobile-gap,12px)}.h18-layout-flex-children{flex-direction:var(--h18-layout-mobile-direction,column)}.h18-layout-grid-children{grid-template-columns:repeat(var(--h18-layout-mobile-columns,1),minmax(0,1fr))}}' .\n"+layout_css_anchor
    php=php.replace(layout_css_anchor,layout_css,1)

# Admin title/content can be used on layout containers too.
php=replace_once(php,
 'data-types="hero text text_image image buttons card card_grid tabs accordion carousel highlight icon list badge quote html mail_form poll"',
 'data-types="hero text text_image image buttons card card_grid tabs accordion carousel container flex grid highlight icon list badge quote html mail_form poll"',
 'admin layout title types')
php=replace_once(php,
 'data-types="hero text text_image image buttons card card_grid tabs accordion carousel highlight icon list quote embed shortcode html css mail_form poll"',
 'data-types="hero text text_image image buttons card card_grid tabs accordion carousel container flex grid highlight icon list quote embed shortcode html css mail_form poll"',
 'admin layout content types')

# Parent and layout controls before carousel controls.
admin_anchor="""                    <div class=\"h18-section-type-field h18-section-module-box\" data-types=\"carousel\">
"""
admin_layout="""                    <div class=\"h18-section-module-box h18-layout-parent-box\">
                        <h4>Layout-hierarki</h4>
                        <input class=\"h18-layout-parent-key\" type=\"hidden\" name=\"<?php echo esc_attr($prefix); ?>[LayoutParentKey]\" value=\"<?php echo esc_attr($section['LayoutParentKey']); ?>\" />
                        <div class=\"h18-field\"><label><strong>Placér element i</strong></label><select class=\"h18-layout-parent-select\"><option value=\"\">Topniveau på siden</option></select></div>
                        <p class=\"description\">Kun Container, Flex container og Grid container kan være parent. Cyklusser og mere end tre niveauer afvises også server-side.</p>
                    </div>
                    <div class=\"h18-section-type-field h18-section-module-box\" data-types=\"container flex grid\">
                        <h4>Container-layout</h4>
                        <div class=\"h18-module-fields-grid h18-module-fields-grid--four\">
                            <div class=\"h18-field h18-section-type-field\" data-types=\"flex\"><label><strong>Retning</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[LayoutDirection]\"><option value=\"Row\" <?php selected($section['LayoutDirection'],'Row'); ?>>Vandret</option><option value=\"Column\" <?php selected($section['LayoutDirection'],'Column'); ?>>Lodret</option></select></div>
                            <label class=\"h18-section-type-field\" data-types=\"flex\"><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[LayoutWrap]\" value=\"1\" <?php checked(!empty($section['LayoutWrap'])); ?> /> <strong>Tillad wrap</strong></label>
                            <div class=\"h18-field h18-section-type-field\" data-types=\"flex\"><label><strong>Fordeling</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[LayoutJustify]\"><option value=\"Start\" <?php selected($section['LayoutJustify'],'Start'); ?>>Start</option><option value=\"Center\" <?php selected($section['LayoutJustify'],'Center'); ?>>Center</option><option value=\"End\" <?php selected($section['LayoutJustify'],'End'); ?>>Slut</option><option value=\"SpaceBetween\" <?php selected($section['LayoutJustify'],'SpaceBetween'); ?>>Space between</option></select></div>
                            <div class=\"h18-field h18-section-type-field\" data-types=\"flex grid\"><label><strong>Vertikal/track placering</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[LayoutAlign]\"><option value=\"Start\" <?php selected($section['LayoutAlign'],'Start'); ?>>Start</option><option value=\"Center\" <?php selected($section['LayoutAlign'],'Center'); ?>>Center</option><option value=\"End\" <?php selected($section['LayoutAlign'],'End'); ?>>Slut</option><option value=\"Stretch\" <?php selected($section['LayoutAlign'],'Stretch'); ?>>Stretch</option></select></div>
                            <div class=\"h18-field\"><label><strong>Gap desktop (px)</strong></label><input type=\"number\" min=\"0\" max=\"120\" name=\"<?php echo esc_attr($prefix); ?>[LayoutGapPx]\" value=\"<?php echo esc_attr($section['LayoutGapPx']); ?>\" /></div>
                            <div class=\"h18-field\"><label><strong>Gap mobil (px)</strong></label><input type=\"number\" min=\"0\" max=\"80\" name=\"<?php echo esc_attr($prefix); ?>[MobileLayoutGapPx]\" value=\"<?php echo esc_attr($section['MobileLayoutGapPx']); ?>\" /></div>
                            <div class=\"h18-field h18-section-type-field\" data-types=\"grid\"><label><strong>Grid kolonner</strong></label><input type=\"number\" min=\"1\" max=\"6\" name=\"<?php echo esc_attr($prefix); ?>[LayoutColumns]\" value=\"<?php echo esc_attr($section['LayoutColumns']); ?>\" /></div>
                            <div class=\"h18-field h18-section-type-field\" data-types=\"grid\"><label><strong>Grid kolonner mobil</strong></label><input type=\"number\" min=\"1\" max=\"3\" name=\"<?php echo esc_attr($prefix); ?>[MobileLayoutColumns]\" value=\"<?php echo esc_attr($section['MobileLayoutColumns']); ?>\" /></div>
                            <label class=\"h18-section-type-field\" data-types=\"flex\"><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[MobileLayoutStack]\" value=\"1\" <?php checked(!empty($section['MobileLayoutStack'])); ?> /> <strong>Stack lodret på mobil</strong></label>
                        </div>
                    </div>

"""+admin_anchor
php=replace_once(php,admin_anchor,admin_layout,'layout admin controls')

# Fix v0.5.18 checkbox semantics and add layout booleans at save time.
save_bool_old="""            $raw['ShowDesktop'] = !empty($raw['ShowDesktop']);
            $raw['ShowTablet'] = !empty($raw['ShowTablet']);
            $raw['ShowMobile'] = !empty($raw['ShowMobile']);
            $key = sanitize_key((string) ($raw['Key'] ?? ''));
"""
save_bool_new="""            $raw['ShowDesktop'] = !empty($raw['ShowDesktop']);
            $raw['ShowTablet'] = !empty($raw['ShowTablet']);
            $raw['ShowMobile'] = !empty($raw['ShowMobile']);
            $raw['CarouselAutoplay'] = !empty($raw['CarouselAutoplay']);
            $raw['CarouselLoop'] = !empty($raw['CarouselLoop']);
            $raw['CarouselShowArrows'] = !empty($raw['CarouselShowArrows']);
            $raw['CarouselShowDots'] = !empty($raw['CarouselShowDots']);
            $raw['LayoutWrap'] = !empty($raw['LayoutWrap']);
            $raw['MobileLayoutStack'] = !empty($raw['MobileLayoutStack']);
            $key = sanitize_key((string) ($raw['Key'] ?? ''));
"""
php=replace_once(php,save_bool_old,save_bool_new,'checkbox save semantics')

# JS type labels.
js=replace_once(js,
 "tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', embed: 'Embed / medie-URL'",
 "tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', container: 'Container', flex: 'Flex container', grid: 'Grid container', embed: 'Embed / medie-URL'",
 'inspector layout labels')
js=replace_once(js,
 "            carousel: 'Carousel / slider',\n            highlight: 'Fremhævet tekst',",
 "            carousel: 'Carousel / slider',\n            container: 'Container',\n            flex: 'Flex container',\n            grid: 'Grid container',\n            highlight: 'Fremhævet tekst',",
 'refresh layout labels')

# Layout hierarchy UI helpers before refreshPageSectionType.
js_anchor="""    function refreshPageSectionType($row) {
"""
js_helpers=r'''    function layoutParentCapableV0519($row) {
        return $row && $row.length && ['container','flex','grid'].includes(String($row.attr('data-section-type') || ''));
    }

    function layoutWouldCycleV0519($row, candidateKey) {
        const selfKey = String($row.find('.h18-page-section-key').val() || '');
        let cursor = String(candidateKey || '');
        const seen = new Set([selfKey]);
        let depth = 0;
        while (cursor) {
            depth += 1;
            if (depth > 3 || seen.has(cursor)) { return true; }
            seen.add(cursor);
            const $candidate = $pageSections.children('.h18-page-section-row').filter(function () { return String($(this).find('.h18-page-section-key').val() || '') === cursor; }).first();
            if (!$candidate.length || !layoutParentCapableV0519($candidate)) { return true; }
            cursor = String(pageSectionControls($candidate, '.h18-layout-parent-key').val() || '');
        }
        return false;
    }

    function refreshLayoutHierarchyV0519() {
        if (!$pageSections.length) { return; }
        const parents = [];
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const $candidate = $(this);
            if (layoutParentCapableV0519($candidate)) {
                parents.push({ key: String($candidate.find('.h18-page-section-key').val() || ''), title: String($candidate.find('.h18-page-section-title-summary').first().text() || inspectorTypeLabel($candidate.attr('data-section-type'))), type: String($candidate.attr('data-section-type') || '') });
            }
        });
        $pageSections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            const selfKey = String($row.find('.h18-page-section-key').val() || '');
            const $hidden = pageSectionControls($row, '.h18-layout-parent-key').first();
            const $select = pageSectionControls($row, '.h18-layout-parent-select').first();
            if (!$select.length || !$hidden.length) { return; }
            let current = String($hidden.val() || '');
            $select.empty().append($('<option>', { value: '', text: 'Topniveau på siden' }));
            parents.forEach(function (parent) {
                if (!parent.key || parent.key === selfKey) { return; }
                const disabled = layoutWouldCycleV0519($row, parent.key);
                $select.append($('<option>', { value: parent.key, text: inspectorTypeLabel(parent.type) + ' · ' + (parent.title || parent.key), disabled: disabled }));
            });
            if (current && !$select.find('option[value="' + current.replace(/"/g,'\\"') + '"]:not(:disabled)').length) { current = ''; $hidden.val(''); }
            $select.val(current);
            $row.toggleClass('h18-layout-child-row', Boolean(current)).attr('data-layout-parent', current);
            const index = String($row.attr('data-section-index') || '');
            $pageNavigatorList.children('.h18-navigator-item[data-section-index="' + index + '"]').toggleClass('h18-layout-child-item', Boolean(current)).attr('data-layout-parent', current);
            $row.find('.h18-layout-parent-box').toggle(String($row.attr('data-section-type') || '') !== 'legacy');
        });
    }

'''
js=replace_once(js,js_anchor,js_helpers+js_anchor,'layout js helpers')

# Hook hierarchy refresh into type refresh tail.
refresh_tail="""        refreshPrimitiveVariantV0516($row);
        refreshCollectionEditorV0517($row);
        rebuildPageNavigator();
"""
refresh_new="""        refreshPrimitiveVariantV0516($row);
        refreshCollectionEditorV0517($row);
        rebuildPageNavigator();
        refreshLayoutHierarchyV0519();
"""
js=replace_once(js,refresh_tail,refresh_new,'layout refresh hook')

# Parent change and deletion refresh.
js_events_anchor="""    $(document).on('change', '.h18-section-active', rebuildPageNavigator);
"""
js_events="""    $(document).on('change', '.h18-layout-parent-select', function () {
        const $row = pageSectionForElement(this);
        pageSectionControls($row, '.h18-layout-parent-key').val(String($(this).val() || '')).trigger('change');
        refreshLayoutHierarchyV0519();
        rebuildPageNavigator();
        refreshLayoutHierarchyV0519();
        scheduleEditorHistoryCapture(0);
    });
    $(document).on('click', '.h18-page-section-delete', function () { window.setTimeout(refreshLayoutHierarchyV0519, 0); });

    $(document).on('change', '.h18-section-active', rebuildPageNavigator);
"""
js=replace_once(js,js_events_anchor,js_events,'layout events')

# New section layout defaults.
default_anchor_js="""        } else if (type === 'carousel') {
            setValue('Background', 'White');
"""
default_layout_js="""        } else if (['container','flex','grid'].includes(type)) {
            setValue('Background', 'White');
            setValue('PaddingPx', 12);
            setValue('HorizontalPaddingPx', 12);
            setValue('MobilePaddingPx', 8);
            setValue('MobileHorizontalPaddingPx', 8);
            setValue('LayoutGapPx', 16);
            setValue('MobileLayoutGapPx', 12);
            setValue('LayoutColumns', 2);
            setValue('MobileLayoutColumns', 1);
            pageSectionControls($row, '[name$=\"[LayoutWrap]\"]').prop('checked', true);
            pageSectionControls($row, '[name$=\"[MobileLayoutStack]\"]').prop('checked', true);
        } else if (type === 'carousel') {
            setValue('Background', 'White');
"""
js=replace_once(js,default_anchor_js,default_layout_js,'layout defaults js')

# Canvas preview before carousel.
canvas_anchor="""        } else if (type === 'carousel') {
            addTitle('Carousel');
"""
canvas_layout=r'''        } else if (['container','flex','grid'].includes(type)) {
            addTitle(type === 'grid' ? 'Grid container' : (type === 'flex' ? 'Flex container' : 'Container'));
            canvasAddBodyText($inner, content);
            const selfKey = String($row.find('.h18-page-section-key').val() || '');
            const childCount = $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').filter(function () { return String(pageSectionControls($(this), '.h18-layout-parent-key').val() || '') === selfKey; }).length;
            const detail = type === 'grid' ? String(canvasFieldValue($row,'LayoutColumns',2)) + ' kolonner' : (type === 'flex' ? String(canvasFieldValue($row,'LayoutDirection','Row')) + ' · gap ' + String(canvasFieldValue($row,'LayoutGapPx',16)) + ' px' : 'blok-container');
            $inner.append($('<div>', { class: 'h18-canvas-layout-shell h18-canvas-layout-shell--' + type }).append($('<strong>', { text: childCount + ' under-element' + (childCount === 1 ? '' : 'er') }), $('<small>', { text: detail })));
        } else if (type === 'carousel') {
            addTitle('Carousel');
'''
js=replace_once(js,canvas_anchor,canvas_layout,'canvas layout preview')

# Initial hierarchy refresh after editor setup anchor.
init_anchor="""        window.setTimeout(initializeEditorHistory, 0);
"""
init_new="""        window.setTimeout(initializeEditorHistory, 0);
        window.setTimeout(refreshLayoutHierarchyV0519, 0);
"""
js=replace_once(js,init_anchor,init_new,'layout initial refresh')

css_block=r'''

/* v0.5.19 – nested layout hierarchy */
.h18-page-section-row.h18-layout-child-row{margin-left:28px;width:calc(100% - 28px);position:relative}
.h18-page-section-row.h18-layout-child-row:before{content:'↳';position:absolute;left:-24px;top:18px;color:#2271b1;font-weight:700}
.h18-navigator-item.h18-layout-child-item{margin-left:18px;width:calc(100% - 18px);border-left:2px solid #b9d7ed}
.h18-layout-parent-box{border-color:#b9d7ed;background:#f7fbfe}.h18-canvas-layout-shell{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px;padding:12px;border:2px dashed rgba(34,113,177,.35);border-radius:6px;background:rgba(240,246,252,.58)}.h18-canvas-layout-shell small{color:#50575e}
@media(max-width:900px){.h18-page-section-row.h18-layout-child-row{margin-left:14px;width:calc(100% - 14px)}}
'''
if '/* v0.5.19 – nested layout hierarchy */' in css: raise SystemExit('v0.5.19 CSS already present')
css=css.rstrip()+css_block+'\n'

readme=replace_once(readme,'Version: 0.5.18','Version: 0.5.19','readme version')
readme_anchor='== Version 0.5.18 – Carousel / Slider ==\n'
readme_new="""== Version 0.5.19 – Section/Container/Flex/Grid layout foundation ==

Nyt:
- UD-021–023 layoutfundament: Container, Flex container og Grid container som native builder-elementer
- elementer kan placeres inde i en layout-parent via LayoutParentKey, mens storage fortsat er en flad revisionsvenlig sektionsliste
- frontend omdanner den flade model til et ægte DOM-træ med op til tre niveauer
- server-side validering af parent-type, manglende parent, selvreference, cykler og maksimal dybde
- Flex: row/column, wrap, justify, align, desktop/mobile gap og valgfri mobil-stack
- Grid: 1-6 desktopkolonner, 1-3 mobilkolonner, align og separate gaps
- Canvas og Navigator indrykker children og viser antal under-elementer i layout-containere
- responsive section styling, hover, visibility og typografi virker også for nested children
- retter samtidig checkbox-semantik for Carousel loop/pile/prikker samt nye layout-checkboxes
- page-editor schema løftes bagudkompatibelt til 1.15

"""+readme_anchor
readme=replace_once(readme,readme_anchor,readme_new,'readme v0.5.18 anchor')

php_path.write_text(php);js_path.write_text(js);css_path.write_text(css);readme_path.write_text(readme)
print('v0.5.19 patch applied')
