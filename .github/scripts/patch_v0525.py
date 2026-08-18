from pathlib import Path

php_path=Path('hangar18-manager.php')
js_path=Path('assets/admin.js')
css_path=Path('assets/admin.css')
readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

def once(text,old,new,label):
    count=text.count(old)
    if count!=1: raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old,new,1)

php=once(php,' * Version: 0.5.24',' * Version: 0.5.25','plugin header version')
php=once(php,"    const VERSION = '0.5.24';","    const VERSION = '0.5.25';",'plugin const version')

# Same query core serves admin preview and frontend shortcode.
php=once(php,
"""        add_shortcode('hangar18_page_editor', [$this, 'shortcode_page_editor']);
        add_filter('wp_robots', [$this, 'filter_conversion_test_robots']);
""",
"""        add_shortcode('hangar18_page_editor', [$this, 'shortcode_page_editor']);
        add_shortcode('hangar18_data_query', [$this, 'shortcode_data_query']);
        add_filter('wp_robots', [$this, 'filter_conversion_test_robots']);
""",'query shortcode registration')

query_engine=r'''

    private function custom_data_query_operator_map($field_type) {
        $maps = [
            'text' => ['eq'=>'Er lig med','neq'=>'Er ikke lig med','contains'=>'Indeholder'],
            'number' => ['eq'=>'=','neq'=>'≠','gt'=>'>','gte'=>'≥','lt'=>'<','lte'=>'≤'],
            'bool' => ['eq'=>'Er lig med'],
            'date' => ['eq'=>'På dato','before'=>'Før','after'=>'Efter'],
            'media' => ['eq'=>'Er lig med','neq'=>'Er ikke lig med'],
        ];
        return $maps[(string) $field_type] ?? [];
    }

    private function normalize_custom_data_query(array $raw) {
        $types = $this->get_custom_data_types();
        $type_key = sanitize_key((string) ($raw['Type'] ?? $raw['type'] ?? ''));
        if ($type_key === '' || !isset($types[$type_key])) { throw new RuntimeException('Query Builder: vælg en gyldig datatype.'); }
        $schema = $types[$type_key];
        $field_map = [];
        foreach ($schema['Fields'] as $field) { $field_map[(string) $field['Key']] = $field; }

        $field_key = sanitize_key((string) ($raw['Field'] ?? $raw['field'] ?? ''));
        $operator = sanitize_key((string) ($raw['Operator'] ?? $raw['op'] ?? 'eq'));
        $value_raw = $raw['Value'] ?? $raw['value'] ?? '';
        $filter = null;
        if ($field_key !== '') {
            if (!isset($field_map[$field_key])) { throw new RuntimeException('Query Builder: filterfeltet findes ikke i datatypen.'); }
            $field = $field_map[$field_key];
            $field_type = (string) $field['Type'];
            $operators = $this->custom_data_query_operator_map($field_type);
            if (!isset($operators[$operator])) { throw new RuntimeException('Query Builder: operatoren er ikke tilladt for denne felttype.'); }
            if ($field_type === 'number') {
                if (!is_numeric($value_raw)) { throw new RuntimeException('Query Builder: filterværdien skal være et tal.'); }
                $value = (string) (0 + $value_raw);
            } elseif ($field_type === 'bool') {
                $value = $this->bool_value($value_raw, false) ? '1' : '0';
            } elseif ($field_type === 'date') {
                $value = sanitize_text_field((string) $value_raw);
                $date = DateTime::createFromFormat('!Y-m-d', $value);
                if (!$date || $date->format('Y-m-d') !== $value) { throw new RuntimeException('Query Builder: dato skal være ÅÅÅÅ-MM-DD.'); }
            } elseif ($field_type === 'media') {
                $value = (string) absint($value_raw);
            } else {
                $value = sanitize_text_field((string) $value_raw);
            }
            $filter = ['Field'=>$field_key,'FieldType'=>$field_type,'Operator'=>$operator,'Value'=>$value];
        }

        $sort_raw = (string) ($raw['Sort'] ?? $raw['sort'] ?? 'modified');
        $sort = in_array($sort_raw, ['title','modified','created'], true) ? $sort_raw : '';
        if ($sort === '' && strpos($sort_raw, 'field:') === 0) {
            $sort_field = sanitize_key(substr($sort_raw, 6));
            if ($sort_field !== '' && isset($field_map[$sort_field]) && !in_array((string) $field_map[$sort_field]['Type'], ['bool'], true)) {
                $sort = 'field:' . $sort_field;
            }
        }
        if ($sort === '') { $sort = 'modified'; }
        $order = strtoupper((string) ($raw['Order'] ?? $raw['order'] ?? 'DESC'));
        if (!in_array($order, ['ASC','DESC'], true)) { $order = 'DESC'; }
        $limit = $this->clamp_int($raw['Limit'] ?? $raw['limit'] ?? 10, 1, 100, 10);
        return [
            'Type' => $type_key,
            'Schema' => $schema,
            'Filter' => $filter,
            'Sort' => $sort,
            'Order' => $order,
            'Limit' => $limit,
        ];
    }

    private function custom_data_query_compare($operator) {
        $map = ['eq'=>'=','neq'=>'!=','contains'=>'LIKE','gt'=>'>','gte'=>'>=','lt'=>'<','lte'=>'<=','before'=>'<','after'=>'>'];
        return $map[(string) $operator] ?? '=';
    }

    private function run_custom_data_query(array $raw, &$normalized = null) {
        $query = $this->normalize_custom_data_query($raw);
        $normalized = $query;
        $meta_query = [[
            'key' => '_h18_data_type',
            'value' => $query['Type'],
            'compare' => '=',
        ]];
        if (is_array($query['Filter'])) {
            $filter = $query['Filter'];
            $meta_type = 'CHAR';
            if (in_array($filter['FieldType'], ['number','bool','media'], true)) { $meta_type = 'NUMERIC'; }
            elseif ($filter['FieldType'] === 'date') { $meta_type = 'DATE'; }
            $meta_query[] = [
                'key' => '_h18_field_' . $filter['Field'],
                'value' => $filter['Value'],
                'compare' => $this->custom_data_query_compare($filter['Operator']),
                'type' => $meta_type,
            ];
        }
        $args = [
            'post_type' => self::DATA_ENTRY_POST_TYPE,
            'post_status' => 'publish',
            'posts_per_page' => (int) $query['Limit'],
            'no_found_rows' => true,
            'meta_query' => $meta_query,
            'order' => $query['Order'],
        ];
        if ($query['Sort'] === 'title') { $args['orderby'] = 'title'; }
        elseif ($query['Sort'] === 'created') { $args['orderby'] = 'date'; }
        elseif ($query['Sort'] === 'modified') { $args['orderby'] = 'modified'; }
        else {
            $sort_field = sanitize_key(substr((string) $query['Sort'], 6));
            $field_map = [];
            foreach ($query['Schema']['Fields'] as $field) { $field_map[(string) $field['Key']] = $field; }
            $args['meta_key'] = '_h18_field_' . $sort_field;
            $args['orderby'] = isset($field_map[$sort_field]) && in_array((string) $field_map[$sort_field]['Type'], ['number','media'], true) ? 'meta_value_num' : 'meta_value';
        }
        return get_posts($args);
    }

    private function custom_data_query_shortcode_from_normalized(array $query) {
        $parts = ['type="' . esc_attr($query['Type']) . '"'];
        if (is_array($query['Filter'])) {
            $parts[] = 'field="' . esc_attr($query['Filter']['Field']) . '"';
            $parts[] = 'op="' . esc_attr($query['Filter']['Operator']) . '"';
            $parts[] = 'value="' . esc_attr($query['Filter']['Value']) . '"';
        }
        $parts[] = 'sort="' . esc_attr($query['Sort']) . '"';
        $parts[] = 'order="' . esc_attr($query['Order']) . '"';
        $parts[] = 'limit="' . (int) $query['Limit'] . '"';
        return '[hangar18_data_query ' . implode(' ', $parts) . ']';
    }

    public function shortcode_data_query($atts) {
        $atts = shortcode_atts(['type'=>'','field'=>'','op'=>'eq','value'=>'','sort'=>'modified','order'=>'DESC','limit'=>'10'], $atts, 'hangar18_data_query');
        try {
            $normalized = null;
            $posts = $this->run_custom_data_query($atts, $normalized);
        } catch (Throwable $e) {
            return current_user_can('edit_pages') ? '<p class="h18-data-query-error">' . esc_html($e->getMessage()) . '</p>' : '';
        }
        if (!$posts) { return '<div class="h18-data-query-results h18-data-query-results--empty">Ingen resultater.</div>'; }
        $hash = substr(hash('sha256', wp_json_encode($normalized)), 0, 16);
        $html = '<ul class="h18-data-query-results" data-query-hash="' . esc_attr($hash) . '">';
        foreach ($posts as $post) {
            if (!$post instanceof WP_Post) { continue; }
            $html .= '<li data-entry-id="' . (int) $post->ID . '">' . esc_html((string) $post->post_title) . '</li>';
        }
        return $html . '</ul>';
    }
'''
# Insert before render_data(), after data input helpers are available.
php=once(php,
"""    public function render_data() {
""",
query_engine+"""

    public function render_data() {
""",'insert query engine')

# Prepare preview state in Data admin.
php=once(php,
"""        $entries = $selected ? $this->custom_data_entry_query($selected['Key'], 100) : [];
        $can_schema = current_user_can('manage_options');
        $blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'Order'=>1];
        ?>
""",
"""        $entries = $selected ? $this->custom_data_entry_query($selected['Key'], 100) : [];
        $can_schema = current_user_can('manage_options');
        $blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'Order'=>1];
        $query_preview = !empty($_GET['query_preview']) && $selected;
        $qb_raw = [
            'Type' => $selected ? $selected['Key'] : '',
            'Field' => isset($_GET['qb_field']) ? wp_unslash($_GET['qb_field']) : '',
            'Operator' => isset($_GET['qb_operator']) ? wp_unslash($_GET['qb_operator']) : 'eq',
            'Value' => isset($_GET['qb_value']) ? wp_unslash($_GET['qb_value']) : '',
            'Sort' => isset($_GET['qb_sort']) ? wp_unslash($_GET['qb_sort']) : 'modified',
            'Order' => isset($_GET['qb_order']) ? wp_unslash($_GET['qb_order']) : 'DESC',
            'Limit' => isset($_GET['qb_limit']) ? wp_unslash($_GET['qb_limit']) : 10,
        ];
        $qb_results = []; $qb_normalized = null; $qb_error = '';
        if ($query_preview) {
            try { $qb_results = $this->run_custom_data_query($qb_raw, $qb_normalized); }
            catch (Throwable $e) { $qb_error = $e->getMessage(); }
        }
        ?>
""",'query preview state')

query_panel=r'''

                <section class="h18-panel h18-data-query-builder">
                    <div class="h18-panel-heading-row"><div><h3>Query Builder v1</h3><p>Type + ét filter + sortering + limit. Advanced AND/OR og pagination kommer i UD-056.</p></div><span>UD-055</span></div>
                    <form method="get" action="<?php echo esc_url(admin_url('admin.php')); ?>" class="h18-data-query-form">
                        <input type="hidden" name="page" value="hangar18-data" /><input type="hidden" name="type" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="query_preview" value="1" />
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <div class="h18-field"><label><strong>Filterfelt</strong></label><select id="h18-qb-field" name="qb_field"><option value="">Intet filter</option><?php foreach ($selected['Fields'] as $field) : ?><option value="<?php echo esc_attr($field['Key']); ?>" data-field-type="<?php echo esc_attr($field['Type']); ?>" <?php selected((string) $qb_raw['Field'], (string) $field['Key']); ?>><?php echo esc_html($field['Label'] . ' · ' . $field['Type']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Operator</strong></label><select id="h18-qb-operator" name="qb_operator" data-current="<?php echo esc_attr((string) $qb_raw['Operator']); ?>"></select></div>
                            <div class="h18-field"><label><strong>Værdi</strong></label><input id="h18-qb-value" type="text" name="qb_value" value="<?php echo esc_attr((string) $qb_raw['Value']); ?>" /><p class="description">Bool: ja/nej. Dato: ÅÅÅÅ-MM-DD. Media: attachment-ID.</p></div>
                            <div class="h18-field"><label><strong>Sortér</strong></label><select name="qb_sort"><option value="modified" <?php selected($qb_raw['Sort'],'modified'); ?>>Senest ændret</option><option value="created" <?php selected($qb_raw['Sort'],'created'); ?>>Oprettet</option><option value="title" <?php selected($qb_raw['Sort'],'title'); ?>>Titel</option><?php foreach ($selected['Fields'] as $field) : if ($field['Type'] === 'bool') continue; ?><option value="field:<?php echo esc_attr($field['Key']); ?>" <?php selected($qb_raw['Sort'],'field:' . $field['Key']); ?>><?php echo esc_html($field['Label']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Retning</strong></label><select name="qb_order"><option value="DESC" <?php selected(strtoupper((string)$qb_raw['Order']),'DESC'); ?>>Faldende</option><option value="ASC" <?php selected(strtoupper((string)$qb_raw['Order']),'ASC'); ?>>Stigende</option></select></div>
                            <div class="h18-field"><label><strong>Limit</strong></label><input type="number" name="qb_limit" min="1" max="100" value="<?php echo esc_attr((int) $qb_raw['Limit']); ?>" /></div>
                        </div>
                        <p><button type="submit" class="button button-primary">Kør preview</button></p>
                    </form>
                    <?php if ($query_preview) : ?>
                        <div class="h18-data-query-preview">
                            <?php if ($qb_error !== '') : ?><div class="notice notice-error inline"><p><?php echo esc_html($qb_error); ?></p></div>
                            <?php else : ?>
                                <p><strong><?php echo esc_html(count($qb_results)); ?> resultat(er)</strong> — samme server-query bruges af frontend-shortcode.</p>
                                <table class="widefat striped"><thead><tr><th>ID</th><th>Titel</th><th>Ændret</th></tr></thead><tbody><?php foreach ($qb_results as $qb_post) : ?><tr><td><?php echo esc_html((int)$qb_post->ID); ?></td><td><?php echo esc_html($qb_post->post_title); ?></td><td><?php echo esc_html(get_post_modified_time('Y-m-d H:i', false, $qb_post)); ?></td></tr><?php endforeach; ?></tbody></table>
                                <p><strong>Frontend:</strong> <code><?php echo esc_html($this->custom_data_query_shortcode_from_normalized($qb_normalized)); ?></code></p>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </section>
'''
# Insert after selected type summary, before schema editor.
php=once(php,
"""                <div class=\"h18-data-summary\"><div><h2><?php echo esc_html($selected['PluralLabel']); ?></h2><p><code><?php echo esc_html($selected['Key']); ?></code> · <?php echo esc_html(count($selected['Fields'])); ?> felter · <?php echo esc_html(count($entries)); ?> viste entries</p></div><a class=\"button button-primary\" href=\"<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($selected['Key']) . '&entry_id=0#h18-data-entry-form')); ?>\">+ Ny <?php echo esc_html($selected['SingularLabel']); ?></a></div>

                <?php if ($can_schema) : ?><details class=\"h18-panel h18-data-schema-details\"><summary><strong>Redigér datatype-schema</strong></summary>
""",
"""                <div class=\"h18-data-summary\"><div><h2><?php echo esc_html($selected['PluralLabel']); ?></h2><p><code><?php echo esc_html($selected['Key']); ?></code> · <?php echo esc_html(count($selected['Fields'])); ?> felter · <?php echo esc_html(count($entries)); ?> viste entries</p></div><a class=\"button button-primary\" href=\"<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($selected['Key']) . '&entry_id=0#h18-data-entry-form')); ?>\">+ Ny <?php echo esc_html($selected['SingularLabel']); ?></a></div>
"""+query_panel+"""

                <?php if ($can_schema) : ?><details class=\"h18-panel h18-data-schema-details\"><summary><strong>Redigér datatype-schema</strong></summary>
""",'query builder UI')

# Operator UI driven only by field type; server remains authority.
js_block=r'''

    /* v0.5.25 – Query Builder v1 */
    const $qbFieldV0525=$('#h18-qb-field');const $qbOperatorV0525=$('#h18-qb-operator');
    const qbOperatorsV0525={text:[['eq','Er lig med'],['neq','Er ikke lig med'],['contains','Indeholder']],number:[['eq','='],['neq','≠'],['gt','>'],['gte','≥'],['lt','<'],['lte','≤']],bool:[['eq','Er lig med']],date:[['eq','På dato'],['before','Før'],['after','Efter']],media:[['eq','Er lig med'],['neq','Er ikke lig med']]};
    function refreshQbOperatorsV0525(){if(!$qbOperatorV0525.length)return;const $option=$qbFieldV0525.find('option:selected');const type=String($option.attr('data-field-type')||'text');let current=String($qbOperatorV0525.attr('data-current')||$qbOperatorV0525.val()||'eq');const options=$qbFieldV0525.val()? (qbOperatorsV0525[type]||qbOperatorsV0525.text) : [['eq','—']];$qbOperatorV0525.empty();options.forEach(function(item){$qbOperatorV0525.append($('<option>',{value:item[0],text:item[1]}));});if(!$qbOperatorV0525.find('option[value="'+current.replace(/"/g,'\\"')+'"]').length)current=options[0][0];$qbOperatorV0525.val(current).attr('data-current',current);$('#h18-qb-value').prop('disabled',!$qbFieldV0525.val());}
    $qbFieldV0525.on('change',function(){$qbOperatorV0525.attr('data-current','eq');refreshQbOperatorsV0525();});$qbOperatorV0525.on('change',function(){$(this).attr('data-current',String($(this).val()||'eq'));});refreshQbOperatorsV0525();
'''
last=js.rfind('\n});')
if last<0: raise SystemExit('admin.js wrapper end not found')
if '/* v0.5.25 – Query Builder v1 */' in js: raise SystemExit('v0.5.25 JS already present')
js=js[:last]+js_block+js[last:]

css_block=r'''

/* v0.5.25 – Query Builder v1 */
.h18-data-query-builder{margin-bottom:18px;border-top:3px solid #2271b1}.h18-data-query-builder .h18-panel-heading-row h3{margin-bottom:4px}.h18-data-query-builder .h18-panel-heading-row p{margin:0}.h18-data-query-preview{margin-top:16px;padding-top:14px;border-top:1px solid #dcdcde}.h18-data-query-preview code{user-select:all}.h18-data-query-results{margin:1em 0;padding-left:1.25em}.h18-data-query-results--empty{opacity:.75}
'''
if '/* v0.5.25 – Query Builder v1 */' in css: raise SystemExit('v0.5.25 CSS already present')
css=css.rstrip()+css_block+'\n'

readme=once(readme,'Version: 0.5.24','Version: 0.5.25','readme version')
anchor='== Version 0.5.24 – E5 Dynamic binding ==\n'
notes="""== Version 0.5.25 – E5 Query Builder v1 ==

Nyt:
- UD-055: generisk Query Builder v1 for custom data med datatype, ét typevalideret filter, sortering, retning og limit
- text understøtter eq/neq/contains; number eq/neq/gt/gte/lt/lte; date eq/before/after; bool og media sikre equality-filtre
- sortering kan ske efter titel, oprettet, ændret eller kompatibelt schemafelt
- limit håndhæves server-side til 1–100 resultater
- admin-preview og frontend-shortcode bruger præcis samme run_custom_data_query()-motor
- frontend-shortcode [hangar18_data_query ...] viser kun publicerede data-entry-titler; drafts/private eksponeres ikke
- Query Builder bygger udelukkende WP_Query/get_posts-argumenter og query-klare _h18_field_<key> meta fra v0.5.23; ingen rå SQL
- generated shortcode vises efter preview, så samme query kan reproduceres på frontend
- page-editor schema forbliver 1.19
- advanced AND/OR, relation og pagination er fortsat UD-056; template-repeat pr. resultat er UD-057

"""+anchor
readme=once(readme,anchor,notes,'readme v0.5.25 anchor')

php_path.write_text(php);js_path.write_text(js);css_path.write_text(css);readme_path.write_text(readme)
print('v0.5.25 Query Builder v1 patch applied')
