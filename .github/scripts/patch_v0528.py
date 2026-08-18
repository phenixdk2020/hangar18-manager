from pathlib import Path

php_path=Path('hangar18-manager.php'); js_path=Path('assets/admin.js'); css_path=Path('assets/admin.css'); readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

def once(text,old,new,label):
    count=text.count(old)
    if count!=1: raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old,new,1)

php=once(php,' * Version: 0.5.27',' * Version: 0.5.28','plugin header version')
php=once(php,"    const VERSION = '0.5.27';","    const VERSION = '0.5.28';",'plugin const version')

php=once(php,
"""            'date' => 'Dato',
            'media' => 'Medie / billede',
        ];
    }

    private function normalize_custom_data_type(array $raw, $existing_key = '') {
""",
"""            'date' => 'Dato',
            'media' => 'Medie / billede',
            'relation' => 'Relation',
            'group' => 'Gruppe',
            'repeater' => 'Repeater',
        ];
    }

    private function custom_data_nested_field_types() {
        return [
            'text' => 'Tekst',
            'number' => 'Tal',
            'bool' => 'Ja/nej',
            'date' => 'Dato',
            'media' => 'Medie / billede',
        ];
    }

    private function normalize_custom_data_nested_fields($raw) {
        if (is_string($raw)) {
            $lines = preg_split('/\\r\\n|\\r|\\n/', $raw);
            $parsed = [];
            foreach ((array) $lines as $line) {
                $line = trim((string) $line); if ($line === '') { continue; }
                $parts = array_map('trim', explode('|', $line));
                $parsed[] = [
                    'Key' => $parts[0] ?? '',
                    'Label' => $parts[1] ?? ($parts[0] ?? ''),
                    'Type' => $parts[2] ?? 'text',
                    'Required' => in_array(strtolower((string) ($parts[3] ?? '')), ['1','true','yes','ja','required'], true),
                ];
            }
            $raw = $parsed;
        }
        if (!is_array($raw)) { return []; }
        $allowed = $this->custom_data_nested_field_types();
        $fields = []; $used = [];
        foreach (array_slice(array_values($raw), 0, 12) as $item) {
            if (!is_array($item)) { continue; }
            $key = sanitize_key((string) ($item['Key'] ?? ''));
            $label = sanitize_text_field((string) ($item['Label'] ?? ''));
            $type = sanitize_key((string) ($item['Type'] ?? 'text'));
            if ($key === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{0,47}$/', $key)) { throw new RuntimeException('Underfelter skal have en gyldig nøgle på højst 48 tegn.'); }
            if (isset($used[$key])) { throw new RuntimeException("Underfelt-nøglen '{$key}' findes mere end én gang."); }
            if ($label === '') { throw new RuntimeException("Underfeltet '{$key}' mangler et navn."); }
            if (!isset($allowed[$type])) { throw new RuntimeException("Underfeltet '{$key}' bruger en ikke-tilladt nested felttype."); }
            $used[$key] = true;
            $fields[] = ['Key'=>$key,'Label'=>$label,'Type'=>$type,'Required'=>!empty($item['Required']),'Order'=>count($fields)+1];
        }
        return $fields;
    }

    private function custom_data_nested_schema_text(array $fields) {
        $lines = [];
        foreach ($fields as $field) {
            $lines[] = (string) $field['Key'] . '|' . (string) $field['Label'] . '|' . (string) $field['Type'] . '|' . (!empty($field['Required']) ? 'required' : '');
        }
        return implode("\\n", $lines);
    }

    private function normalize_custom_data_type(array $raw, $existing_key = '') {
""",'structured field helpers')

php=once(php,
"""            $used[$field_key] = true;
            $fields[] = [
                'Key' => $field_key,
                'Label' => $label,
                'Type' => $type,
                'Required' => !empty($field['Required']),
                'Order' => count($fields) + 1,
            ];
""",
"""            $used[$field_key] = true;
            $relation_target = $type === 'relation' ? sanitize_key((string) ($field['RelationTargetType'] ?? '')) : '';
            if ($type === 'relation' && $relation_target === '') { throw new RuntimeException("Relationsfeltet '{$field_key}' skal vælge en mål-datatype."); }
            $nested_raw = $field['NestedFields'] ?? ($field['NestedSchemaText'] ?? []);
            $nested_fields = in_array($type, ['group','repeater'], true) ? $this->normalize_custom_data_nested_fields($nested_raw) : [];
            if (in_array($type, ['group','repeater'], true) && !$nested_fields) { throw new RuntimeException("Feltet '{$field_key}' skal have mindst ét underfelt."); }
            $fields[] = [
                'Key' => $field_key,
                'Label' => $label,
                'Type' => $type,
                'Required' => !empty($field['Required']),
                'RelationTargetType' => $relation_target,
                'NestedFields' => $nested_fields,
                'RepeaterMaxItems' => $type === 'repeater' ? $this->clamp_int($field['RepeaterMaxItems'] ?? 10, 1, 20, 10) : 0,
                'Order' => count($fields) + 1,
            ];
""",'structured field schema config')

php=once(php,"""            'SchemaVersion' => 1,
""","""            'SchemaVersion' => 2,
""",'data schema version 2')

# Prevent deleting relation targets still referenced by schemas.
relation_usage=r'''

    private function custom_data_relation_schema_usage($target_key) {
        $target_key = sanitize_key((string) $target_key);
        if ($target_key === '') { return []; }
        $usage = [];
        foreach ($this->get_custom_data_types() as $type_key => $type) {
            foreach ((array) ($type['Fields'] ?? []) as $field) {
                if (($field['Type'] ?? '') !== 'relation' || sanitize_key((string) ($field['RelationTargetType'] ?? '')) !== $target_key) { continue; }
                $usage[] = ['TypeKey'=>$type_key,'TypeLabel'=>(string)$type['SingularLabel'],'FieldKey'=>(string)$field['Key'],'FieldLabel'=>(string)$field['Label']];
            }
        }
        return $usage;
    }
'''
php=once(php,
"""    private function custom_data_entry_query($type_key, $limit = 100) {
""",
relation_usage+"""

    private function custom_data_entry_query($type_key, $limit = 100) {
""",'relation schema usage helper')

# Structured sanitization before scalar coercion.
structured_sanitize=r'''

    private function custom_data_structured_has_content($value) {
        if (is_array($value)) {
            foreach ($value as $item) { if ($this->custom_data_structured_has_content($item)) { return true; } }
            return false;
        }
        if (is_bool($value)) { return true; }
        return $value !== null && trim((string) $value) !== '';
    }

    private function sanitize_custom_data_nested_values(array $fields, $raw, array &$errors, $path) {
        $raw = is_array($raw) ? $raw : [];
        $result = [];
        foreach ($fields as $nested) {
            $nested_errors = [];
            $nested_value = $this->sanitize_custom_data_value($nested, $raw[(string)$nested['Key']] ?? null, $nested_errors);
            foreach ($nested_errors as $error) { $errors[] = sanitize_text_field((string) $path) . ': ' . $error; }
            $result[(string)$nested['Key']] = $nested_value;
        }
        return $result;
    }
'''
php=once(php,
"""    private function sanitize_custom_data_value(array $field, $value, array &$errors) {
""",
structured_sanitize+"""

    private function sanitize_custom_data_value(array $field, $value, array &$errors) {
""",'structured value helpers')

php=once(php,
"""        $required = !empty($field['Required']);
        if ($type === 'bool') { return !empty($value); }
        $value = is_scalar($value) ? trim((string) $value) : '';
""",
"""        $required = !empty($field['Required']);
        if ($type === 'bool') { return !empty($value); }
        if ($type === 'relation') {
            $relation_id = absint(is_scalar($value) ? $value : 0);
            if ($required && $relation_id <= 0) { $errors[] = "Feltet '{$label}' er obligatorisk."; return 0; }
            if ($relation_id <= 0) { return 0; }
            $target = sanitize_key((string) ($field['RelationTargetType'] ?? ''));
            if ($target === '' || !$this->custom_data_entry_for_type($relation_id, $target)) { $errors[] = "Feltet '{$label}' peger ikke på en gyldig relation."; return 0; }
            return $relation_id;
        }
        if ($type === 'group') {
            $nested = $this->sanitize_custom_data_nested_values((array) ($field['NestedFields'] ?? []), is_array($value) ? $value : [], $errors, $label);
            if ($required && !$this->custom_data_structured_has_content($nested)) { $errors[] = "Feltet '{$label}' er obligatorisk."; }
            return $nested;
        }
        if ($type === 'repeater') {
            $source = is_array($value) && isset($value['items']) && is_array($value['items']) ? $value['items'] : (is_array($value) ? $value : []);
            $limit = $this->clamp_int($field['RepeaterMaxItems'] ?? 10, 1, 20, 10);
            $items = [];
            foreach (array_slice(array_values($source), 0, $limit) as $index => $item) {
                if (!is_array($item) || !empty($item['_remove'])) { continue; }
                $nested = $this->sanitize_custom_data_nested_values((array) ($field['NestedFields'] ?? []), $item, $errors, $label . ' #' . ($index + 1));
                if ($this->custom_data_structured_has_content($nested)) { $items[] = $nested; }
            }
            if ($required && !$items) { $errors[] = "Feltet '{$label}' skal have mindst én række."; }
            return array_slice($items, 0, $limit);
        }
        $value = is_scalar($value) ? trim((string) $value) : '';
""",'structured value sanitizer')

# Validate relation target schemas after the complete type catalog is available.
php=once(php,
"""            $type = $this->normalize_custom_data_type($raw, $existing_key);
            $types = $this->get_custom_data_types();
            if ($existing_key === '' && isset($types[$type['Key']])) { throw new RuntimeException('Der findes allerede en datatype med denne nøgle.'); }
""",
"""            $type = $this->normalize_custom_data_type($raw, $existing_key);
            $types = $this->get_custom_data_types();
            if ($existing_key === '' && isset($types[$type['Key']])) { throw new RuntimeException('Der findes allerede en datatype med denne nøgle.'); }
            $known_targets = $types; $known_targets[$type['Key']] = $type;
            foreach ($type['Fields'] as $field) {
                if (($field['Type'] ?? '') === 'relation' && !isset($known_targets[(string) ($field['RelationTargetType'] ?? '')])) {
                    throw new RuntimeException("Relationsfeltet '{$field['Label']}' peger på en datatype, der ikke findes.");
                }
            }
""",'relation target existence validation')

php=once(php,
"""        $count = $this->custom_data_entry_count($key);
        if ($count > 0) { $this->set_notice('error', "Datatypen kan ikke slettes, fordi den har {$count} entries."); $this->custom_data_redirect($key); }
        $name = (string) $types[$key]['SingularLabel'];
""",
"""        $count = $this->custom_data_entry_count($key);
        if ($count > 0) { $this->set_notice('error', "Datatypen kan ikke slettes, fordi den har {$count} entries."); $this->custom_data_redirect($key); }
        $relation_usage = $this->custom_data_relation_schema_usage($key);
        if ($relation_usage) { $this->set_notice('error', 'Datatypen kan ikke slettes, fordi ' . count($relation_usage) . ' relationsfelt(er) stadig peger på den.'); $this->custom_data_redirect($key); }
        $name = (string) $types[$key]['SingularLabel'];
""",'relation target delete protection')

# Entry renderer refactor for relation/group/repeater.
render_helpers=r'''

    private function render_custom_data_value_input(array $field, $value, $name) {
        $type = (string) $field['Type'];
        if ($type === 'bool') {
            echo '<input type="hidden" name="' . esc_attr($name) . '" value="0" /><label class="h18-data-bool"><input type="checkbox" name="' . esc_attr($name) . '" value="1" ' . checked(!empty($value), true, false) . ' /> Ja</label>'; return;
        }
        if ($type === 'number') { echo '<input type="number" step="any" name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '" />'; return; }
        if ($type === 'date') { echo '<input type="date" name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '" />'; return; }
        if ($type === 'media') {
            $media_id = absint($value); echo '<div class="h18-data-media-field"><input class="h18-data-media-id" type="hidden" name="' . esc_attr($name) . '" value="' . esc_attr($media_id) . '" /><div class="h18-data-media-preview">'; if ($media_id) { echo wp_get_attachment_image($media_id, 'thumbnail'); } echo '</div><button type="button" class="button h18-data-media-pick">Vælg medie</button> <button type="button" class="button-link-delete h18-data-media-clear">Fjern</button></div>'; return;
        }
        echo '<input type="text" name="' . esc_attr($name) . '" value="' . esc_attr(is_scalar($value) ? (string) $value : '') . '" />';
    }

    private function render_custom_data_nested_inputs(array $fields, $values, $name_prefix) {
        $values = is_array($values) ? $values : [];
        echo '<div class="h18-data-nested-fields">';
        foreach ($fields as $nested) {
            $key = (string) $nested['Key']; echo '<div class="h18-field"><label><strong>' . esc_html((string)$nested['Label']) . (!empty($nested['Required']) && $nested['Type'] !== 'bool' ? ' *' : '') . '</strong><small>' . esc_html($this->custom_data_nested_field_types()[$nested['Type']] ?? $nested['Type']) . '</small></label>';
            $this->render_custom_data_value_input($nested, $values[$key] ?? '', $name_prefix . '[' . $key . ']'); echo '</div>';
        }
        echo '</div>';
    }
'''
php=once(php,
"""    private function render_custom_data_field_input(array $field, $value) {
""",
render_helpers+"""

    private function render_custom_data_field_input(array $field, $value) {
""",'structured input render helpers')

old_render="""    private function render_custom_data_field_input(array $field, $value) {
        $key = (string) $field['Key'];
        $name = 'data_values[' . $key . ']';
        $type = (string) $field['Type'];
        if ($type === 'bool') {
            echo '<input type=\"hidden\" name=\"' . esc_attr($name) . '\" value=\"0\" /><label class=\"h18-data-bool\"><input type=\"checkbox\" name=\"' . esc_attr($name) . '\" value=\"1\" ' . checked(!empty($value), true, false) . ' /> Ja</label>';
            return;
        }
        if ($type === 'number') { echo '<input type=\"number\" step=\"any\" name=\"' . esc_attr($name) . '\" value=\"' . esc_attr((string) $value) . '\" />'; return; }
        if ($type === 'date') { echo '<input type=\"date\" name=\"' . esc_attr($name) . '\" value=\"' . esc_attr((string) $value) . '\" />'; return; }
        if ($type === 'media') {
            $media_id = absint($value);
            echo '<div class=\"h18-data-media-field\"><input class=\"h18-data-media-id\" type=\"hidden\" name=\"' . esc_attr($name) . '\" value=\"' . esc_attr($media_id) . '\" /><div class=\"h18-data-media-preview\">';
            if ($media_id) { echo wp_get_attachment_image($media_id, 'thumbnail'); }
            echo '</div><button type=\"button\" class=\"button h18-data-media-pick\">Vælg medie</button> <button type=\"button\" class=\"button-link-delete h18-data-media-clear\">Fjern</button></div>';
            return;
        }
        echo '<input type=\"text\" name=\"' . esc_attr($name) . '\" value=\"' . esc_attr((string) $value) . '\" />';
    }
"""
new_render=r'''    private function render_custom_data_field_input(array $field, $value) {
        $key = (string) $field['Key']; $name = 'data_values[' . $key . ']'; $type = (string) $field['Type'];
        if ($type === 'relation') {
            $target = sanitize_key((string) ($field['RelationTargetType'] ?? '')); $entries = $target !== '' ? $this->custom_data_entry_query($target, 200) : []; $current = absint($value);
            echo '<select name="' . esc_attr($name) . '"><option value="0">Ingen relation</option>'; foreach ($entries as $entry) { echo '<option value="' . (int)$entry->ID . '" ' . selected($current,(int)$entry->ID,false) . '>' . esc_html((string)$entry->post_title) . '</option>'; } echo '</select>'; return;
        }
        if ($type === 'group') { echo '<fieldset class="h18-data-group"><legend>' . esc_html((string)$field['Label']) . '</legend>'; $this->render_custom_data_nested_inputs((array)($field['NestedFields']??[]),is_array($value)?$value:[],$name); echo '</fieldset>'; return; }
        if ($type === 'repeater') {
            $items=is_array($value)?array_values($value):[]; if(!$items)$items=[[]]; $limit=$this->clamp_int($field['RepeaterMaxItems']??10,1,20,10); echo '<div class="h18-data-repeater" data-max-items="'.(int)$limit.'"><div class="h18-data-repeater-items">'; foreach(array_slice($items,0,$limit) as $i=>$item){echo '<fieldset class="h18-data-repeater-item" data-item-index="'.(int)$i.'"><legend>Række '.((int)$i+1).'</legend>'; $this->render_custom_data_nested_inputs((array)($field['NestedFields']??[]),is_array($item)?$item:[],$name.'[items]['.(int)$i.']'); echo '<button type="button" class="button-link-delete h18-data-repeater-remove">Fjern række</button></fieldset>';} echo '</div><template class="h18-data-repeater-template"><fieldset class="h18-data-repeater-item" data-item-index="__ITEM__"><legend>Række</legend>'; $this->render_custom_data_nested_inputs((array)($field['NestedFields']??[]),[],$name.'[items][__ITEM__]'); echo '<button type="button" class="button-link-delete h18-data-repeater-remove">Fjern række</button></fieldset></template><button type="button" class="button h18-data-repeater-add">+ Tilføj række</button></div>'; return;
        }
        $this->render_custom_data_value_input($field,$value,$name);
    }
'''
php=once(php,old_render,new_render,'replace field input renderer')

# Schema row configs; current type catalog is safe to read during rendering.
php=once(php,
"""            <div class=\"h18-field\"><label><strong>Type</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[Type]\"><?php foreach ($this->custom_data_field_types() as $type_key => $type_label) : ?><option value=\"<?php echo esc_attr($type_key); ?>\" <?php selected($field['Type'], $type_key); ?>><?php echo esc_html($type_label); ?></option><?php endforeach; ?></select></div>
            <label class=\"h18-data-required\"><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[Required]\" value=\"1\" <?php checked(!empty($field['Required'])); ?> /> Obligatorisk</label>
""",
"""            <div class=\"h18-field\"><label><strong>Type</strong></label><select class=\"h18-data-field-type\" name=\"<?php echo esc_attr($prefix); ?>[Type]\"><?php foreach ($this->custom_data_field_types() as $type_key => $type_label) : ?><option value=\"<?php echo esc_attr($type_key); ?>\" <?php selected($field['Type'], $type_key); ?>><?php echo esc_html($type_label); ?></option><?php endforeach; ?></select></div>
            <label class=\"h18-data-required\"><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[Required]\" value=\"1\" <?php checked(!empty($field['Required'])); ?> /> Obligatorisk</label>
            <div class=\"h18-field h18-data-relation-config\"><label><strong>Mål-datatype</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[RelationTargetType]\"><option value=\"\">Vælg datatype</option><?php foreach ($this->get_custom_data_types() as $target_key => $target_type) : ?><option value=\"<?php echo esc_attr($target_key); ?>\" <?php selected((string)($field['RelationTargetType']??''),$target_key); ?>><?php echo esc_html($target_type['PluralLabel']); ?></option><?php endforeach; ?></select></div>
            <div class=\"h18-field h18-data-nested-config\"><label><strong>Underfelter</strong></label><textarea name=\"<?php echo esc_attr($prefix); ?>[NestedSchemaText]\" rows=\"4\" placeholder=\"key|Navn|text|required\"><?php echo esc_textarea($this->custom_data_nested_schema_text((array)($field['NestedFields']??[]))); ?></textarea><small>Én linje pr. felt: key|Navn|text|required. Tilladt: text, number, bool, date, media.</small></div>
            <div class=\"h18-field h18-data-repeater-config\"><label><strong>Maks. rækker</strong></label><input type=\"number\" min=\"1\" max=\"20\" name=\"<?php echo esc_attr($prefix); ?>[RepeaterMaxItems]\" value=\"<?php echo esc_attr((int)($field['RepeaterMaxItems']??10)); ?>\" /></div>
""",'schema structured configs')

# Blank field carries config defaults and help text reflects v0.5.28.
php=once(php,
"""        $blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'Order'=>1];
""",
"""        $blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'RelationTargetType'=>'','NestedFields'=>[],'RepeaterMaxItems'=>10,'Order'=>1];
""",'blank structured field')
php=once(php,
"""            <div class=\"h18-help-box\"><strong>E5 Dynamic CMS:</strong> Datatyperne her er generiske schemas. v0.5.23 understøtter text, number, bool, date og media samt valideret CRUD. Senere binding/query-funktioner bygges direkte oven på samme datamodel.</div>
""",
"""            <div class=\"h18-help-box\"><strong>E5 Dynamic CMS:</strong> Datatyperne understøtter primitive felter samt Relation, Group og Repeater. Relationer peger på en konkret datatype; Group/Repeater bruger validerede typed underfelter.</div>
""",'data help text')

# Query Builder v1 deliberately only exposes primitive fields until UD-056.
php=once(php,
"""                            <div class=\"h18-field\"><label><strong>Filterfelt</strong></label><select id=\"h18-qb-field\" name=\"qb_field\"><option value=\"\">Intet filter</option><?php foreach ($selected['Fields'] as $field) : ?><option value=\"<?php echo esc_attr($field['Key']); ?>\" data-field-type=\"<?php echo esc_attr($field['Type']); ?>\" <?php selected((string) $qb_raw['Field'], (string) $field['Key']); ?>><?php echo esc_html($field['Label'] . ' · ' . $field['Type']); ?></option><?php endforeach; ?></select></div>
""",
"""                            <div class=\"h18-field\"><label><strong>Filterfelt</strong></label><select id=\"h18-qb-field\" name=\"qb_field\"><option value=\"\">Intet filter</option><?php foreach ($selected['Fields'] as $field) : if (!in_array($field['Type'], ['text','number','bool','date','media'], true)) continue; ?><option value=\"<?php echo esc_attr($field['Key']); ?>\" data-field-type=\"<?php echo esc_attr($field['Type']); ?>\" <?php selected((string) $qb_raw['Field'], (string) $field['Key']); ?>><?php echo esc_html($field['Label'] . ' · ' . $field['Type']); ?></option><?php endforeach; ?></select></div>
""",'QB primitive filter UI')
php=once(php,
"""<option value=\"field:<?php echo esc_attr($field['Key']); ?>\" <?php selected($qb_raw['Sort'],'field:' . $field['Key']); ?>><?php echo esc_html($field['Label']); ?></option><?php endforeach; ?></select></div>
""",
"""<?php if (!in_array($field['Type'], ['text','number','date','media'], true)) continue; ?><option value=\"field:<?php echo esc_attr($field['Key']); ?>\" <?php selected($qb_raw['Sort'],'field:' . $field['Key']); ?>><?php echo esc_html($field['Label']); ?></option><?php endforeach; ?></select></div>
""",'QB primitive sort UI')

# Query normalizer itself rejects structured sort fields in v1.
php=once(php,
"""            if ($sort_field !== '' && isset($field_map[$sort_field]) && !in_array((string) $field_map[$sort_field]['Type'], ['bool'], true)) {
                $sort = 'field:' . $sort_field;
            }
""",
"""            if ($sort_field !== '' && isset($field_map[$sort_field]) && in_array((string) $field_map[$sort_field]['Type'], ['text','number','date','media'], true)) {
                $sort = 'field:' . $sort_field;
            }
""",'QB structured sort rejection')

# Empty conditions understand arrays.
php=once(php,
"""        if ($value === null || $value === '') { return true; }
        if ($field_type === 'media' && absint($value) <= 0) { return true; }
""",
"""        if ($value === null || $value === '') { return true; }
        if (is_array($value) && !$value) { return true; }
        if ($field_type === 'media' && absint($value) <= 0) { return true; }
""",'structured condition empty')

# Admin JS for schema config + repeater CRUD.
js += r'''

    /* v0.5.28 – UD-054 Relation / Group / Repeater fields */
    function refreshStructuredDataFieldRowV0528($row){if(!$row||!$row.length)return;const type=String($row.find('.h18-data-field-type').val()||'text');$row.find('.h18-data-relation-config').toggle(type==='relation');$row.find('.h18-data-nested-config').toggle(type==='group'||type==='repeater');$row.find('.h18-data-repeater-config').toggle(type==='repeater');}
    $('.h18-data-field-row').each(function(){refreshStructuredDataFieldRowV0528($(this));});
    $(document).on('change','.h18-data-field-type',function(){refreshStructuredDataFieldRowV0528($(this).closest('.h18-data-field-row'));});
    $(document).on('click','#h18-data-add-field',function(){window.setTimeout(function(){$('.h18-data-field-row').each(function(){refreshStructuredDataFieldRowV0528($(this));});},0);});
    $(document).on('click','.h18-data-repeater-add',function(){const $rep=$(this).closest('.h18-data-repeater');const max=Math.max(1,Math.min(20,parseInt($rep.attr('data-max-items'),10)||10));const $items=$rep.find('>.h18-data-repeater-items');if($items.children('.h18-data-repeater-item').length>=max){window.alert('Repeateren har nået sin maksimumgrænse på '+max+' rækker.');return;}const tpl=$rep.find('>template.h18-data-repeater-template').get(0);if(!tpl)return;let next=0;$items.children('.h18-data-repeater-item').each(function(){next=Math.max(next,(parseInt($(this).attr('data-item-index'),10)||0)+1);});const html=tpl.innerHTML.replaceAll('__ITEM__',String(next));const $row=$(html.trim());$row.find('legend').first().text('Række '+(next+1));$items.append($row);});
    $(document).on('click','.h18-data-repeater-remove',function(){const $items=$(this).closest('.h18-data-repeater-items');$(this).closest('.h18-data-repeater-item').remove();$items.children('.h18-data-repeater-item').each(function(i){$(this).find('legend').first().text('Række '+(i+1));});});
'''

css += """

/* v0.5.28 – UD-054 Relation / Group / Repeater fields */
.h18-data-field-row{grid-template-columns:auto minmax(120px,1fr) minmax(160px,1fr) minmax(150px,.8fr) auto auto}.h18-data-relation-config,.h18-data-nested-config,.h18-data-repeater-config{grid-column:2/-1}.h18-data-nested-config textarea{width:100%;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.h18-data-group,.h18-data-repeater-item{margin:8px 0;padding:12px;border:1px solid #dcdcde;border-radius:7px}.h18-data-nested-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.h18-data-repeater-items{display:grid;gap:10px;margin-bottom:10px}@media(max-width:900px){.h18-data-nested-fields{grid-template-columns:1fr}}
"""

readme=once(readme,'Version: 0.5.27','Version: 0.5.28','readme version')
readme += """

## v0.5.28 – E5 UD-054 Relation / Group / Repeater fields
- Datatype schema builder understøtter nu Relation, Group og Repeater ud over de fem primitive felttyper.
- Relation kræver en eksisterende mål-datatype og gemmer et valideret entry-ID; mål-datatyper kan ikke slettes mens relationer peger på dem.
- Group og Repeater bruger op til 12 typed underfelter af text/number/bool/date/media.
- Repeater er bounded til 1–20 rækker pr. schemafelt og har add/remove UI i entry-editoren.
- Nested værdier bruger samme server-side sanitizer som primitive felter og Required-validering.
- Query Builder v1 skjuler/rejecter strukturerede felter; relation/advanced query udvides separat i UD-056.
- Data SchemaVersion løftes til 2; page-editor schema forbliver 1.21.
"""

php_path.write_text(php); js_path.write_text(js); css_path.write_text(css); readme_path.write_text(readme)
print('v0.5.28 UD-054 structured fields patch applied')
