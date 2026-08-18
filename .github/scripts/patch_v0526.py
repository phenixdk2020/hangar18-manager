from pathlib import Path

php_path=Path('hangar18-manager.php')
js_path=Path('assets/admin.js')
css_path=Path('assets/admin.css')
readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

def once(text,old,new,label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old,new,1)

# ------------------------------------------------------------------
# Version + page-editor schema 1.20
# ------------------------------------------------------------------
php=once(php,' * Version: 0.5.25',' * Version: 0.5.26','plugin header version')
php=once(php,"    const VERSION = '0.5.25';","    const VERSION = '0.5.26';",'plugin const version')
php=php.replace("'1.19'", "'1.20'")

# Prevent recursive query-list/component loops at runtime.
php=once(php,
"""    private static $instance = null;
    private $active_dynamic_data_context = null;

    public static function instance() {
""",
"""    private static $instance = null;
    private $active_dynamic_data_context = null;
    private $active_query_list_stack = [];

    public static function instance() {
""",'query list runtime stack')

# ------------------------------------------------------------------
# Element type + persistent model
# ------------------------------------------------------------------
php=once(php,
"""            'grid'       => 'Grid container',
            'component'  => 'Linked component',
""",
"""            'grid'       => 'Grid container',
            'query_list' => 'Repeater / Query list',
            'component'  => 'Linked component',
""",'query list type label')

php=once(php,
"""            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
            'Bindings'              => [],
            'Order'                 => (int) $order,
""",
"""            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
            'Bindings'              => [],
            'QueryListType'         => '',
            'QueryListFilterField'  => '',
            'QueryListFilterOperator' => 'eq',
            'QueryListFilterValue'  => '',
            'QueryListSort'         => 'modified',
            'QueryListOrder'        => 'DESC',
            'QueryListLimit'        => 10,
            'QueryListComponentId'  => '',
            'QueryListComponentVariant' => '',
            'QueryListColumns'      => 1,
            'QueryListMobileColumns'=> 1,
            'QueryListGapPx'        => 18,
            'QueryListMobileGapPx'  => 14,
            'QueryListEmptyText'    => 'Ingen resultater.',
            'Order'                 => (int) $order,
""",'query list default fields')

php=once(php,
"""        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);

        $alignment = (string) ($raw['DesktopAlignment'] ?? 'Left');
""",
"""        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);
        $query_list_type = sanitize_key((string) ($raw['QueryListType'] ?? ''));
        $query_list_filter_field = sanitize_key((string) ($raw['QueryListFilterField'] ?? ''));
        $query_list_filter_operator = sanitize_key((string) ($raw['QueryListFilterOperator'] ?? 'eq'));
        if (!in_array($query_list_filter_operator, ['eq','neq','contains','gt','gte','lt','lte','before','after'], true)) { $query_list_filter_operator = 'eq'; }
        $query_list_filter_value = sanitize_text_field((string) ($raw['QueryListFilterValue'] ?? ''));
        if (strlen($query_list_filter_value) > 500) { $query_list_filter_value = substr($query_list_filter_value, 0, 500); }
        $query_list_sort_raw = (string) ($raw['QueryListSort'] ?? 'modified');
        if (in_array($query_list_sort_raw, ['title','modified','created'], true)) { $query_list_sort = $query_list_sort_raw; }
        elseif (strpos($query_list_sort_raw, 'field:') === 0) { $query_list_sort = 'field:' . sanitize_key(substr($query_list_sort_raw, 6)); }
        else { $query_list_sort = 'modified'; }
        $query_list_order = strtoupper((string) ($raw['QueryListOrder'] ?? 'DESC'));
        if (!in_array($query_list_order, ['ASC','DESC'], true)) { $query_list_order = 'DESC'; }
        $query_list_component_id = sanitize_key((string) ($raw['QueryListComponentId'] ?? ''));
        $query_list_component_variant = sanitize_key((string) ($raw['QueryListComponentVariant'] ?? ''));
        $query_list_empty_text = sanitize_text_field((string) ($raw['QueryListEmptyText'] ?? 'Ingen resultater.'));
        if ($query_list_empty_text === '') { $query_list_empty_text = 'Ingen resultater.'; }

        $alignment = (string) ($raw['DesktopAlignment'] ?? 'Left');
""",'query list normalize fields')

php=once(php,
"""            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
            'Bindings'              => $bindings,
            'Order'                 => $this->clamp_int($raw['Order'] ?? $section['Order'], 1, 10000, $section['Order']),
""",
"""            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
            'Bindings'              => $bindings,
            'QueryListType'         => $query_list_type,
            'QueryListFilterField'  => $query_list_filter_field,
            'QueryListFilterOperator' => $query_list_filter_operator,
            'QueryListFilterValue'  => $query_list_filter_value,
            'QueryListSort'         => $query_list_sort,
            'QueryListOrder'        => $query_list_order,
            'QueryListLimit'        => $this->clamp_int($raw['QueryListLimit'] ?? 10, 1, 100, 10),
            'QueryListComponentId'  => $query_list_component_id,
            'QueryListComponentVariant' => $query_list_component_variant,
            'QueryListColumns'      => $this->clamp_int($raw['QueryListColumns'] ?? 1, 1, 6, 1),
            'QueryListMobileColumns'=> $this->clamp_int($raw['QueryListMobileColumns'] ?? 1, 1, 2, 1),
            'QueryListGapPx'        => $this->clamp_int($raw['QueryListGapPx'] ?? 18, 0, 80, 18),
            'QueryListMobileGapPx'  => $this->clamp_int($raw['QueryListMobileGapPx'] ?? 14, 0, 60, 14),
            'QueryListEmptyText'    => $query_list_empty_text,
            'Order'                 => $this->clamp_int($raw['Order'] ?? $section['Order'], 1, 10000, $section['Order']),
""",'query list normalized return')

# A linked component definition may not itself contain Query List references to linked components.
php=once(php,
"""            if (in_array($raw_type, ['legacy', 'component'], true)) {
                throw new RuntimeException('Linked components kan ikke indeholde legacy-indhold eller andre linked components.');
            }
""",
"""            if (in_array($raw_type, ['legacy', 'component', 'query_list'], true)) {
                throw new RuntimeException('Linked components kan ikke indeholde legacy-indhold, linked components eller Query List-elementer.');
            }
""",'component nested query list protection')

# Usage inspector/deletion protection also counts components referenced by Query Lists.
php=once(php,
"""                if (!is_array($section) || sanitize_key((string) ($section['Type'] ?? '')) !== 'component') { continue; }
                if (sanitize_key((string) ($section['ComponentId'] ?? '')) !== $component_id) { continue; }
                $usage[] = [
                    'PageSlug' => sanitize_title((string) $slug),
                    'PageTitle' => sanitize_text_field((string) ($page_data['PageTitle'] ?? ($definitions[$slug] ?? $slug))),
                    'SectionKey' => sanitize_key((string) ($section['Key'] ?? '')),
                    'Variant' => sanitize_key((string) ($section['ComponentVariant'] ?? '')),
                ];
""",
"""                if (!is_array($section)) { continue; }
                $reference_type = sanitize_key((string) ($section['Type'] ?? ''));
                if (!in_array($reference_type, ['component','query_list'], true)) { continue; }
                $referenced_component_id = $reference_type === 'query_list'
                    ? sanitize_key((string) ($section['QueryListComponentId'] ?? ''))
                    : sanitize_key((string) ($section['ComponentId'] ?? ''));
                if ($referenced_component_id !== $component_id) { continue; }
                $usage[] = [
                    'PageSlug' => sanitize_title((string) $slug),
                    'PageTitle' => sanitize_text_field((string) ($page_data['PageTitle'] ?? ($definitions[$slug] ?? $slug))),
                    'SectionKey' => sanitize_key((string) ($section['Key'] ?? '')),
                    'Variant' => sanitize_key((string) ($reference_type === 'query_list' ? ($section['QueryListComponentVariant'] ?? '') : ($section['ComponentVariant'] ?? ''))),
                    'ReferenceType' => $reference_type,
                ];
""",'query list component usage')

# ------------------------------------------------------------------
# Runtime renderer: same Query Builder core, one component render per result.
# ------------------------------------------------------------------
query_runtime=r'''

    private function query_list_query_from_section(array $section) {
        return [
            'Type' => (string) ($section['QueryListType'] ?? ''),
            'Field' => (string) ($section['QueryListFilterField'] ?? ''),
            'Operator' => (string) ($section['QueryListFilterOperator'] ?? 'eq'),
            'Value' => (string) ($section['QueryListFilterValue'] ?? ''),
            'Sort' => (string) ($section['QueryListSort'] ?? 'modified'),
            'Order' => (string) ($section['QueryListOrder'] ?? 'DESC'),
            'Limit' => (int) ($section['QueryListLimit'] ?? 10),
        ];
    }

    private function render_page_editor_query_list($page_id, array $section) {
        $component_id = sanitize_key((string) ($section['QueryListComponentId'] ?? ''));
        if ($component_id === '') {
            return current_user_can('edit_pages') ? '<div class="h18-query-list-error">Query List mangler en template-komponent.</div>' : '';
        }
        if (in_array($component_id, $this->active_query_list_stack, true) || count($this->active_query_list_stack) >= 3) {
            return current_user_can('edit_pages') ? '<div class="h18-query-list-error">Query List-loop blev blokeret.</div>' : '';
        }

        try {
            $normalized = null;
            $posts = $this->run_custom_data_query($this->query_list_query_from_section($section), $normalized);
        } catch (Throwable $e) {
            return current_user_can('edit_pages') ? '<div class="h18-query-list-error">' . esc_html($e->getMessage()) . '</div>' : '';
        }

        $background_class = strtolower((string) ($section['Background'] ?? 'White'));
        $classes = trim('h18-editor-section h18-editor-query-list h18-editor-section--' . sanitize_html_class($background_class) . ' ' . $this->page_editor_visibility_classes($section));
        $id = 'h18-section-' . sanitize_html_class((string) ($section['Key'] ?? 'query-list'));
        $style = $this->page_editor_section_style($section);
        $columns = $this->clamp_int($section['QueryListColumns'] ?? 1, 1, 6, 1);
        $mobile_columns = $this->clamp_int($section['QueryListMobileColumns'] ?? 1, 1, 2, 1);
        $gap = $this->clamp_int($section['QueryListGapPx'] ?? 18, 0, 80, 18);
        $mobile_gap = $this->clamp_int($section['QueryListMobileGapPx'] ?? 14, 0, 60, 14);
        $design = $this->get_header_design_settings();
        $mobile_breakpoint = (int) ($design['BreakpointMobileMaxPx'] ?? 782);
        $title_html = trim((string) ($section['Title'] ?? '')) !== '' ? '<h2>' . esc_html((string) $section['Title']) . '</h2>' : '';
        $empty_text = sanitize_text_field((string) ($section['QueryListEmptyText'] ?? 'Ingen resultater.'));
        $query_hash = substr(hash('sha256', wp_json_encode($normalized) . '|' . $component_id . '|' . sanitize_key((string) ($section['QueryListComponentVariant'] ?? ''))), 0, 16);
        $responsive_css = '<style>@media(max-width:' . $mobile_breakpoint . 'px){#' . esc_attr($id) . '>.h18-query-list-items{grid-template-columns:repeat(' . $mobile_columns . ',minmax(0,1fr));gap:' . $mobile_gap . 'px}}</style>';

        if (!$posts) {
            return $responsive_css . '<section id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" style="' . esc_attr($style) . '" data-query-hash="' . esc_attr($query_hash) . '">' . $title_html . '<p class="h18-query-list-empty">' . esc_html($empty_text) . '</p></section>';
        }

        $previous_context = $this->active_dynamic_data_context;
        $this->active_query_list_stack[] = $component_id;
        $items = '';
        try {
            foreach ($posts as $post) {
                if (!$post instanceof WP_Post) { continue; }
                $context = $this->resolve_dynamic_data_context((string) $normalized['Type'], (int) $post->ID);
                if (!is_array($context)) { continue; }
                $instance = [
                    'Key' => sanitize_key((string) ($section['Key'] ?? 'query-list') . '-entry-' . (int) $post->ID),
                    'ComponentId' => $component_id,
                    'ComponentRevision' => 0,
                    'ComponentVariant' => sanitize_key((string) ($section['QueryListComponentVariant'] ?? '')),
                    'ComponentOverrides' => [],
                ];
                [$component_sections, $component] = $this->resolve_page_component_instance_sections($page_id, $instance);
                if (!$component || !$component_sections) { continue; }
                $this->active_dynamic_data_context = $context;
                $items .= '<div class="h18-query-list-item" data-entry-id="' . (int) $post->ID . '" data-component-id="' . esc_attr($component_id) . '">' . $this->render_page_editor_layout_tree($page_id, $component_sections) . '</div>';
            }
        } finally {
            $this->active_dynamic_data_context = $previous_context;
            array_pop($this->active_query_list_stack);
        }

        if ($items === '') {
            $items = '<p class="h18-query-list-empty">' . esc_html($empty_text) . '</p>';
        } else {
            $items = '<div class="h18-query-list-items" style="display:grid;grid-template-columns:repeat(' . $columns . ',minmax(0,1fr));gap:' . $gap . 'px">' . $items . '</div>';
        }
        return $responsive_css . '<section id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" style="' . esc_attr($style) . '" data-query-hash="' . esc_attr($query_hash) . '">' . $title_html . $items . '</section>';
    }
'''
php=once(php,
"""    private function render_page_editor_section_front($page_id, array $section, $layout_children = '') {
""",
query_runtime+"""

    private function render_page_editor_section_front($page_id, array $section, $layout_children = '') {
""",'query list runtime functions')

php=once(php,
"""        if (is_array($this->active_dynamic_data_context)) {
            $section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context);
        }
        if ($section['Type'] === 'component') {
""",
"""        if (is_array($this->active_dynamic_data_context)) {
            $section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context);
        }
        if ($section['Type'] === 'query_list') {
            return $this->render_page_editor_query_list($page_id, $section);
        }
        if ($section['Type'] === 'component') {
""",'query list render dispatch')

# ------------------------------------------------------------------
# Inspector controls
# ------------------------------------------------------------------
query_admin=r'''

                    <div class="h18-section-type-field h18-section-module-box h18-query-list-editor" data-types="query_list">
                        <h4>Repeater / Query list</h4>
                        <p class="description">Kører Query Builder v1 og renderer den valgte linked component én gang pr. resultat. Hvert resultat bliver current data context inde i templaten.</p>
                        <?php
                        $h18_query_types = $this->get_custom_data_types();
                        $h18_query_components = $this->get_page_components();
                        $h18_query_schema = isset($h18_query_types[$section['QueryListType']]) ? $h18_query_types[$section['QueryListType']] : null;
                        $h18_query_fields = $h18_query_schema ? (array) $h18_query_schema['Fields'] : [];
                        $h18_query_component = isset($h18_query_components[$section['QueryListComponentId']]) ? $h18_query_components[$section['QueryListComponentId']] : null;
                        ?>
                        <div class="h18-module-fields-grid h18-module-fields-grid--two">
                            <div class="h18-field"><label><strong>Datatype</strong></label><select class="h18-query-list-type" name="<?php echo esc_attr($prefix); ?>[QueryListType]"><option value="">Vælg datatype</option><?php foreach ($h18_query_types as $h18_type_key => $h18_type) : ?><option value="<?php echo esc_attr($h18_type_key); ?>" <?php selected($section['QueryListType'], $h18_type_key); ?>><?php echo esc_html($h18_type['PluralLabel']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Template-komponent</strong></label><select class="h18-query-list-component" name="<?php echo esc_attr($prefix); ?>[QueryListComponentId]"><option value="">Vælg linked component</option><?php foreach ($h18_query_components as $h18_component_id => $h18_component) : ?><option value="<?php echo esc_attr($h18_component_id); ?>" <?php selected($section['QueryListComponentId'], $h18_component_id); ?>><?php echo esc_html($h18_component['Name']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Variant</strong></label><select class="h18-query-list-component-variant" data-current="<?php echo esc_attr($section['QueryListComponentVariant']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListComponentVariant]"><option value="">Base</option><?php if ($h18_query_component) : foreach ((array) ($h18_query_component['Variants'] ?? []) as $h18_variant_id => $h18_variant) : ?><option value="<?php echo esc_attr($h18_variant_id); ?>" <?php selected($section['QueryListComponentVariant'], $h18_variant_id); ?>><?php echo esc_html($h18_variant['Name']); ?></option><?php endforeach; endif; ?></select></div>
                            <div class="h18-field"><label><strong>Filterfelt</strong></label><select class="h18-query-list-filter-field" data-current="<?php echo esc_attr($section['QueryListFilterField']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListFilterField]"><option value="">Intet filter</option><?php foreach ($h18_query_fields as $h18_field) : ?><option value="<?php echo esc_attr($h18_field['Key']); ?>" data-field-type="<?php echo esc_attr($h18_field['Type']); ?>" <?php selected($section['QueryListFilterField'], $h18_field['Key']); ?>><?php echo esc_html($h18_field['Label']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Operator</strong></label><select class="h18-query-list-filter-operator" data-current="<?php echo esc_attr($section['QueryListFilterOperator']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListFilterOperator]"><option value="eq">Er lig med</option></select></div>
                            <div class="h18-field"><label><strong>Filterværdi</strong></label><input class="h18-query-list-filter-value" type="text" name="<?php echo esc_attr($prefix); ?>[QueryListFilterValue]" value="<?php echo esc_attr($section['QueryListFilterValue']); ?>" /></div>
                            <div class="h18-field"><label><strong>Sortering</strong></label><select class="h18-query-list-sort" data-current="<?php echo esc_attr($section['QueryListSort']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListSort]"><option value="modified">Senest ændret</option><option value="created">Oprettet</option><option value="title">Titel</option><?php foreach ($h18_query_fields as $h18_field) : if (($h18_field['Type'] ?? '') === 'bool') continue; ?><option value="field:<?php echo esc_attr($h18_field['Key']); ?>" <?php selected($section['QueryListSort'], 'field:' . $h18_field['Key']); ?>><?php echo esc_html($h18_field['Label']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Retning</strong></label><select name="<?php echo esc_attr($prefix); ?>[QueryListOrder]"><option value="DESC" <?php selected($section['QueryListOrder'],'DESC'); ?>>Faldende</option><option value="ASC" <?php selected($section['QueryListOrder'],'ASC'); ?>>Stigende</option></select></div>
                            <div class="h18-field"><label><strong>Maks. resultater</strong></label><input type="number" min="1" max="100" name="<?php echo esc_attr($prefix); ?>[QueryListLimit]" value="<?php echo esc_attr($section['QueryListLimit']); ?>" /></div>
                            <div class="h18-field"><label><strong>Kolonner desktop</strong></label><input type="number" min="1" max="6" name="<?php echo esc_attr($prefix); ?>[QueryListColumns]" value="<?php echo esc_attr($section['QueryListColumns']); ?>" /></div>
                            <div class="h18-field"><label><strong>Kolonner mobil</strong></label><input type="number" min="1" max="2" name="<?php echo esc_attr($prefix); ?>[QueryListMobileColumns]" value="<?php echo esc_attr($section['QueryListMobileColumns']); ?>" /></div>
                            <div class="h18-field"><label><strong>Gap desktop (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[QueryListGapPx]" value="<?php echo esc_attr($section['QueryListGapPx']); ?>" /></div>
                            <div class="h18-field"><label><strong>Gap mobil (px)</strong></label><input type="number" min="0" max="60" name="<?php echo esc_attr($prefix); ?>[QueryListMobileGapPx]" value="<?php echo esc_attr($section['QueryListMobileGapPx']); ?>" /></div>
                            <div class="h18-field h18-field--full"><label><strong>Tomt resultat</strong></label><input type="text" maxlength="160" name="<?php echo esc_attr($prefix); ?>[QueryListEmptyText]" value="<?php echo esc_attr($section['QueryListEmptyText']); ?>" /></div>
                        </div>
                    </div>
'''
php=once(php,
"""                    <div class=\"h18-section-type-field h18-section-module-box h18-component-instance-editor\" data-types=\"component\">
""",
query_admin+"""

                    <div class=\"h18-section-type-field h18-section-module-box h18-component-instance-editor\" data-types=\"component\">
""",'query list inspector')

# ------------------------------------------------------------------
# JS editor behavior + canvas preview
# ------------------------------------------------------------------
js=once(js,
"""            container: 'Container', flex: 'Flex container', grid: 'Grid container', component: 'Linked component',
""",
"""            container: 'Container', flex: 'Flex container', grid: 'Grid container', query_list: 'Repeater / Query list', component: 'Linked component',
""",'JS query list type label')

query_js=r'''

    /* v0.5.26 – UD-057 Repeater / Query list */
    function queryListOperatorMapV0526(type) {
        const maps = {
            text: [['eq','Er lig med'],['neq','Er ikke lig med'],['contains','Indeholder']],
            number: [['eq','='],['neq','≠'],['gt','>'],['gte','≥'],['lt','<'],['lte','≤']],
            bool: [['eq','Er lig med']],
            date: [['eq','På dato'],['before','Før'],['after','Efter']],
            media: [['eq','Er lig med'],['neq','Er ikke lig med']]
        };
        return maps[String(type || '')] || [['eq','Er lig med']];
    }
    function refreshQueryListControlsV0526($row) {
        if (!$row || !$row.length || String($row.attr('data-section-type') || '') !== 'query_list') { return; }
        const typeKey = String(canvasFieldValue($row,'QueryListType','') || '');
        const definition = pageDynamicDataCatalogV0524[typeKey] || null;
        const fields = definition && Array.isArray(definition.Fields) ? definition.Fields : [];
        const $field = pageSectionControls($row,'.h18-query-list-filter-field').first();
        let currentField = String($field.val() || $field.attr('data-current') || '');
        $field.empty().append($('<option>',{value:'',text:'Intet filter'}));
        fields.forEach(function(field){ $field.append($('<option>',{value:String(field.Key),text:String(field.Label || field.Key),'data-field-type':String(field.Type || 'text')})); });
        if (!$field.find('option[value="'+currentField.replace(/"/g,'\\"')+'"]').length) { currentField=''; }
        $field.val(currentField).attr('data-current',currentField);

        const selectedField = fields.find(function(field){ return String(field.Key)===currentField; }) || null;
        const $operator = pageSectionControls($row,'.h18-query-list-filter-operator').first();
        let currentOperator = String($operator.val() || $operator.attr('data-current') || 'eq');
        $operator.empty();
        queryListOperatorMapV0526(selectedField ? selectedField.Type : 'text').forEach(function(item){ $operator.append($('<option>',{value:item[0],text:item[1]})); });
        if (!$operator.find('option[value="'+currentOperator.replace(/"/g,'\\"')+'"]').length) { currentOperator='eq'; }
        $operator.val(currentOperator).attr('data-current',currentOperator);

        const $sort = pageSectionControls($row,'.h18-query-list-sort').first();
        let currentSort = String($sort.val() || $sort.attr('data-current') || 'modified');
        $sort.empty().append($('<option>',{value:'modified',text:'Senest ændret'}),$('<option>',{value:'created',text:'Oprettet'}),$('<option>',{value:'title',text:'Titel'}));
        fields.forEach(function(field){ if(String(field.Type)!=='bool') $sort.append($('<option>',{value:'field:'+String(field.Key),text:String(field.Label || field.Key)})); });
        if (!$sort.find('option').filter(function(){return String($(this).val())===currentSort;}).length) { currentSort='modified'; }
        $sort.val(currentSort).attr('data-current',currentSort);

        const componentId = String(canvasFieldValue($row,'QueryListComponentId','') || '');
        const component = pageLinkedComponents[componentId] || null;
        const $variant = pageSectionControls($row,'.h18-query-list-component-variant').first();
        let currentVariant = String($variant.val() || $variant.attr('data-current') || '');
        $variant.empty().append($('<option>',{value:'',text:'Base'}));
        const variants = component && component.Variants && typeof component.Variants === 'object' ? Object.values(component.Variants) : [];
        variants.forEach(function(variant){ if(variant&&variant.Id)$variant.append($('<option>',{value:String(variant.Id),text:String(variant.Name || 'Variant')})); });
        if (!$variant.find('option').filter(function(){return String($(this).val())===currentVariant;}).length) { currentVariant=''; }
        $variant.val(currentVariant).attr('data-current',currentVariant);
    }
    $(document).on('change','.h18-query-list-type,.h18-query-list-filter-field,.h18-query-list-filter-operator,.h18-query-list-component',function(){
        const $row=pageSectionForElement($(this)); refreshQueryListControlsV0526($row); renderCanvasPreview($row); scheduleEditorHistoryCapture(0);
    });
    $(document).on('input change','.h18-query-list-filter-value,[name$="[QueryListLimit]"],[name$="[QueryListColumns]"],[name$="[QueryListMobileColumns]"],[name$="[QueryListGapPx]"],[name$="[QueryListMobileGapPx]"],[name$="[QueryListEmptyText]"],[name$="[QueryListOrder]"]',function(){ const $row=pageSectionForElement($(this)); if($row.length)renderCanvasPreview($row); });
'''
# Insert before the main refreshPageSectionType function so the function is hoisted and reusable.
js=once(js,
"""    function refreshPageSectionType($row) {
""",
query_js+"""

    function refreshPageSectionType($row) {
""",'query list JS controls')

js=once(js,
"""        $row.attr('data-section-type', type);
        pageSectionControls($row, '.h18-section-type-field').each(function () {
""",
"""        $row.attr('data-section-type', type);
        refreshQueryListControlsV0526($row);
        pageSectionControls($row, '.h18-section-type-field').each(function () {
""",'refresh query list on type')

js=once(js,
"""        } else if (type === 'component') {
            const componentId = String(canvasFieldValue($row, 'ComponentId', ''));
""",
"""        } else if (type === 'query_list') {
            const typeKey = String(canvasFieldValue($row,'QueryListType','') || '');
            const definition = pageDynamicDataCatalogV0524[typeKey] || null;
            const componentId = String(canvasFieldValue($row,'QueryListComponentId','') || '');
            const component = pageLinkedComponents[componentId] || null;
            const limit = Math.max(1,Math.min(100,parseInt(canvasFieldValue($row,'QueryListLimit',10),10)||10));
            const sampleEntries = definition && Array.isArray(definition.Entries) ? definition.Entries.slice(0,Math.min(limit,3)) : [];
            const $preview = $('<div>',{class:'h18-canvas-query-list'});
            $preview.append($('<strong>',{text:'Query List · '+(definition ? String(definition.PluralLabel || definition.Key) : 'vælg datatype')}));
            $preview.append($('<small>',{text:(component ? 'Template: '+String(component.Name || 'Linked component') : 'Vælg template-komponent')+' · op til '+limit+' resultater'}));
            const $samples=$('<div>',{class:'h18-canvas-query-list-samples'});
            if(sampleEntries.length){ sampleEntries.forEach(function(entry){$samples.append($('<span>',{text:String(entry.Title || ('Entry '+entry.Id))}));}); }
            else {$samples.append($('<span>',{text:'Ingen preview entries i valgt datatype'}));}
            $preview.append($samples); $inner.append($preview);
        } else if (type === 'component') {
            const componentId = String(canvasFieldValue($row, 'ComponentId', ''));
""",'canvas query list preview')

# ------------------------------------------------------------------
# CSS + readme
# ------------------------------------------------------------------
css += """

/* v0.5.26 – UD-057 Repeater / Query list */
.h18-query-list-editor .h18-module-fields-grid{align-items:start}.h18-canvas-query-list{display:grid;gap:8px;padding:14px;border:1px dashed #8c8f94;border-radius:7px;background:#f6f7f7}.h18-canvas-query-list strong,.h18-canvas-query-list small{display:block}.h18-canvas-query-list-samples{display:flex;gap:6px;flex-wrap:wrap}.h18-canvas-query-list-samples span{padding:4px 7px;border-radius:999px;background:#fff;border:1px solid #dcdcde;font-size:12px}
"""

readme=once(readme,'Version: 0.5.25','Version: 0.5.26','readme version')
readme += """

## v0.5.26 – E5 UD-057 Repeater / Query list
- Nyt `Repeater / Query list`-element i den visuelle sidebygger.
- Genbruger Query Builder v1 til datatype, filter, sortering og limit.
- En linked component fungerer som template og renderes én gang pr. query-resultat.
- Hvert resultat bliver current data context under render, så eksisterende dynamic bindings virker uden en særskilt template-motor.
- Understøtter component variant, desktop/mobil-kolonner, gap og tom-resultattekst.
- Query List-komponentreferencer indgår i Usage Inspector og blokerer sikker sletning af komponent/variant.
- Runtime beskytter mod rekursive Query List/component-loops og gendanner altid det tidligere data context.
- Page-editor schema: 1.20.
"""

php_path.write_text(php); js_path.write_text(js); css_path.write_text(css); readme_path.write_text(readme)
print('v0.5.26 UD-057 Repeater / Query list patch applied')
