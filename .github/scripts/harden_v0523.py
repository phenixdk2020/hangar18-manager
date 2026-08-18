from pathlib import Path


def once(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old,new,1)

php_path=Path('hangar18-manager.php'); js_path=Path('assets/admin.js'); css_path=Path('assets/admin.css'); readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

# Schema field preset/default support.
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
"""            $default_raw = $field['Default'] ?? '';
            $default_errors = [];
            $default_field = ['Key'=>$field_key,'Label'=>$label,'Type'=>$type,'Required'=>false];
            $default_value = $this->sanitize_custom_data_value($default_field, $default_raw, $default_errors);
            if ($default_errors) { throw new RuntimeException('Standardværdi for “' . $label . '” er ugyldig: ' . implode(' ', $default_errors)); }
            $used[$field_key] = true;
            $fields[] = [
                'Key' => $field_key,
                'Label' => $label,
                'Type' => $type,
                'Required' => !empty($field['Required']),
                'Default' => $default_value,
                'Order' => count($fields) + 1,
            ];
""",'schema field default')

# Add default input to schema row.
php=once(php,
"""            <div class="h18-field"><label><strong>Type</strong></label><select name="<?php echo esc_attr($prefix); ?>[Type]"><?php foreach ($this->custom_data_field_types() as $type_key => $type_label) : ?><option value="<?php echo esc_attr($type_key); ?>" <?php selected($field['Type'], $type_key); ?>><?php echo esc_html($type_label); ?></option><?php endforeach; ?></select></div>
            <label class="h18-data-required"><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[Required]" value="1" <?php checked(!empty($field['Required'])); ?> /> Obligatorisk</label>
""",
"""            <div class="h18-field"><label><strong>Type</strong></label><select name="<?php echo esc_attr($prefix); ?>[Type]"><?php foreach ($this->custom_data_field_types() as $type_key => $type_label) : ?><option value="<?php echo esc_attr($type_key); ?>" <?php selected($field['Type'], $type_key); ?>><?php echo esc_html($type_label); ?></option><?php endforeach; ?></select></div>
            <div class="h18-field"><label><strong>Standard / preset</strong></label><input class="h18-data-field-default" type="text" name="<?php echo esc_attr($prefix); ?>[Default]" value="<?php echo esc_attr((string) ($field['Default'] ?? '')); ?>" /></div>
            <label class="h18-data-required"><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[Required]" value="1" <?php checked(!empty($field['Required'])); ?> /> Obligatorisk</label>
""",'schema default input')
php=php.replace("$blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'Order'=>1];","$blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'Default'=>'','Order'=>1];")
php=once(php,
"""<?php foreach ($selected['Fields'] as $field) : $value = $entry ? ($entry_values[$field['Key']] ?? '') : ''; ?><div class="h18-field">""",
"""<?php foreach ($selected['Fields'] as $field) : $value = $entry ? ($entry_values[$field['Key']] ?? '') : ($field['Default'] ?? ''); ?><div class="h18-field">""",'new entry defaults')

# Dynamic binding metadata in page sections.
php=once(php,
"""            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
            'Order'                 => (int) $order,
""",
"""            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
            'DataContextTypeKey'    => '',
            'DataContextEntryId'    => 0,
            'DynamicBindings'       => [],
            'Order'                 => (int) $order,
""",'binding section defaults')

php=once(php,
"""        $component_variant = sanitize_key((string) ($raw['ComponentVariant'] ?? ''));
        $component_overrides_raw = $raw['ComponentOverrides'] ?? [];
""",
"""        $component_variant = sanitize_key((string) ($raw['ComponentVariant'] ?? ''));
        $data_context_type_key = sanitize_key((string) ($raw['DataContextTypeKey'] ?? ''));
        $data_context_entry_id = absint($raw['DataContextEntryId'] ?? 0);
        $dynamic_bindings_raw = $raw['DynamicBindings'] ?? [];
        if ((!is_array($dynamic_bindings_raw) || !$dynamic_bindings_raw) && isset($raw['DynamicBindingsJson']) && is_string($raw['DynamicBindingsJson'])) {
            $decoded_dynamic_bindings = json_decode((string) $raw['DynamicBindingsJson'], true);
            if (is_array($decoded_dynamic_bindings)) { $dynamic_bindings_raw = $decoded_dynamic_bindings; }
        }
        $dynamic_bindings = [];
        $allowed_dynamic_targets = array_keys($this->page_dynamic_binding_targets());
        if (is_array($dynamic_bindings_raw)) {
            foreach ($dynamic_bindings_raw as $target => $field_key) {
                $target = sanitize_key((string) $target);
                $field_key = sanitize_key((string) $field_key);
                if ($target !== '' && $field_key !== '' && in_array($target, $allowed_dynamic_targets, true)) { $dynamic_bindings[$target] = $field_key; }
            }
        }
        $component_overrides_raw = $raw['ComponentOverrides'] ?? [];
""",'binding normalize prelude')

php=once(php,
"""            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
            'Order'                 => $this->clamp_int($raw['Order'] ?? $section['Order'], 1, 10000, $section['Order']),
""",
"""            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
            'DataContextTypeKey'    => $data_context_type_key,
            'DataContextEntryId'    => $data_context_entry_id,
            'DynamicBindings'       => $dynamic_bindings,
            'Order'                 => $this->clamp_int($raw['Order'] ?? $section['Order'], 1, 10000, $section['Order']),
""",'binding normalized fields')

# Persisted page JSON changed: bump page editor schema to 1.19.
if php.count("'Version'        => '1.18'") != 3:
    raise SystemExit('Expected 3 active page schema 1.18 payloads after base patch')
php=php.replace("'Version'        => '1.18'","'Version'        => '1.19'")
php=php.replace("'Version' => '1.18',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,","'Version' => '1.19',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,")
php=php.replace("'Version' => '1.18',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,","'Version' => '1.19',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,")

binding_methods=r'''

    /* ================================================================
       DYNAMIC BINDING ENGINE — v0.5.23 / E5 UD-053
       ================================================================ */

    private function page_dynamic_binding_targets() {
        return [
            'title' => ['Field'=>'Title','Label'=>'Overskrift','Types'=>['text','number','bool','date']],
            'content' => ['Field'=>'Content','Label'=>'Tekst','Types'=>['text','number','bool','date']],
            'mediaid' => ['Field'=>'MediaId','Label'=>'Billede / medie','Types'=>['media']],
            'button1label' => ['Field'=>'Button1Label','Label'=>'Knap 1 tekst','Types'=>['text','number','bool','date']],
            'button1url' => ['Field'=>'Button1Url','Label'=>'Knap 1 link','Types'=>['text']],
            'button2label' => ['Field'=>'Button2Label','Label'=>'Knap 2 tekst','Types'=>['text','number','bool','date']],
            'button2url' => ['Field'=>'Button2Url','Label'=>'Knap 2 link','Types'=>['text']],
        ];
    }

    private function custom_data_field_map(array $schema) {
        $map=[]; foreach((array)($schema['Fields']??[]) as $field){ if(is_array($field)&&!empty($field['Key']))$map[(string)$field['Key']]=$field; } return $map;
    }

    private function custom_data_context($type_key,$entry_id) {
        $type_key=sanitize_key((string)$type_key);$entry_id=absint($entry_id);if($type_key===''||$entry_id<=0)return null;$types=$this->get_custom_data_types();if(!isset($types[$type_key]))return null;$entry=$this->custom_data_entry_for_type($entry_id,$type_key);if(!$entry)return null;return['TypeKey'=>$type_key,'EntryId'=>$entry_id,'Schema'=>$types[$type_key],'Values'=>$this->custom_data_entry_values($entry_id,$types[$type_key])];
    }

    private function custom_data_display_value($type,$value) {
        if($type==='bool')return !empty($value)?'Ja':'Nej';return is_scalar($value)?(string)$value:'';
    }

    private function resolve_page_section_dynamic_bindings(array $section,$data_context=null) {
        $bindings=isset($section['DynamicBindings'])&&is_array($section['DynamicBindings'])?$section['DynamicBindings']:[];if(!$bindings)return$section;
        $explicit_type=sanitize_key((string)($section['DataContextTypeKey']??''));$explicit_entry=absint($section['DataContextEntryId']??0);$context=null;
        if($explicit_type!==''&&$explicit_entry>0)$context=$this->custom_data_context($explicit_type,$explicit_entry);elseif(is_array($data_context)&&!empty($data_context['Schema'])&&isset($data_context['Values'])&&is_array($data_context['Values']))$context=$data_context;
        if(!$context||empty($context['Schema']))return$section;$field_map=$this->custom_data_field_map($context['Schema']);$targets=$this->page_dynamic_binding_targets();$values=$context['Values'];
        foreach($bindings as $target_key=>$field_key){$target_key=sanitize_key((string)$target_key);$field_key=sanitize_key((string)$field_key);if(!isset($targets[$target_key],$field_map[$field_key])||!array_key_exists($field_key,$values))continue;$field=$field_map[$field_key];if(!in_array((string)$field['Type'],$targets[$target_key]['Types'],true))continue;$raw=$values[$field_key];if($raw===''||$raw===null)continue;$property=$targets[$target_key]['Field'];
            if($target_key==='mediaid'){$id=absint($raw);if($id<=0||get_post_type($id)!=='attachment')continue;$section[$property]=$id;$section['MediaUrl']='';continue;}
            $value=$this->custom_data_display_value((string)$field['Type'],$raw);if(in_array($target_key,['button1url','button2url'],true)){$url=esc_url_raw($value);if($url==='')continue;$section[$property]=$url;continue;}
            if($target_key==='content'){$section[$property]=sanitize_textarea_field($value);continue;}$section[$property]=sanitize_text_field($value);
        }
        return$section;
    }

    private function custom_data_binding_usage($type_key,$entry_id=0,$field_key='') {
        $type_key=sanitize_key((string)$type_key);$entry_id=absint($entry_id);$field_key=sanitize_key((string)$field_key);$usage=[];
        $scan=function($source,$source_id,$title,$sections)use(&$usage,$type_key,$entry_id,$field_key){foreach((array)$sections as $section){if(!is_array($section)||sanitize_key((string)($section['DataContextTypeKey']??''))!==$type_key)continue;if($entry_id>0&&absint($section['DataContextEntryId']??0)!==$entry_id)continue;if($field_key!==''){ $bindings=isset($section['DynamicBindings'])&&is_array($section['DynamicBindings'])?$section['DynamicBindings']:[];if(!in_array($field_key,array_map('sanitize_key',array_values($bindings)),true))continue; }$usage[]=['Source'=>$source,'SourceId'=>(string)$source_id,'Title'=>(string)$title,'SectionKey'=>sanitize_key((string)($section['Key']??''))];}};
        foreach($this->get_page_editor_store() as $slug=>$data){if(is_array($data))$scan('page',$slug,$data['PageTitle']??$slug,$data['Sections']??[]);}
        foreach($this->get_page_components() as $id=>$component)$scan('component',$id,$component['Name']??$id,$component['Sections']??[]);
        foreach($this->get_page_presets() as $id=>$pattern)$scan('pattern',$id,$pattern['Name']??$id,$pattern['Sections']??[]);
        foreach($this->get_page_templates() as $id=>$template)$scan('template',$id,$template['Name']??$id,$template['Sections']??[]);
        return$usage;
    }

    private function custom_data_types_for_editor() {
        $types=$this->get_custom_data_types();$payload=[];foreach($types as $key=>$type){$entries=[];foreach($this->custom_data_entry_query($key,200) as $entry){$entries[]=['Id'=>(int)$entry->ID,'Title'=>(string)$entry->post_title,'Values'=>$this->custom_data_entry_values($entry->ID,$type)];}$payload[]=['Key'=>$key,'SingularLabel'=>$type['SingularLabel'],'PluralLabel'=>$type['PluralLabel'],'Fields'=>$type['Fields'],'Entries'=>$entries];}return$payload;
    }
'''
php=once(php,"\n    private function default_page_section($type = 'text', $order = 10) {",binding_methods+"\n\n    private function default_page_section($type = 'text', $order = 10) {",'binding methods')

# Block deleting datatype or entry while saved bindings reference them.
php=once(php,
"""        $count = $this->custom_data_entry_count($key);
        if ($count > 0) { $this->set_notice('error', "Datatypen kan ikke slettes, fordi den har {$count} entries."); $this->custom_data_redirect($key); }
        $name = (string) $types[$key]['SingularLabel'];
""",
"""        $count = $this->custom_data_entry_count($key);
        if ($count > 0) { $this->set_notice('error', "Datatypen kan ikke slettes, fordi den har {$count} entries."); $this->custom_data_redirect($key); }
        $binding_usage = $this->custom_data_binding_usage($key);
        if ($binding_usage) { $this->set_notice('error', 'Datatypen kan ikke slettes, fordi den bruges i ' . count($binding_usage) . ' dynamiske binding(er).'); $this->custom_data_redirect($key); }
        $name = (string) $types[$key]['SingularLabel'];
""",'datatype binding delete guard')
php=once(php,
"""        if (!$entry) { $this->set_notice('error', 'Data-entry blev ikke fundet.'); $this->custom_data_redirect($type_key); }
        $title = (string) $entry->post_title;
        wp_delete_post($entry_id, true);
""",
"""        if (!$entry) { $this->set_notice('error', 'Data-entry blev ikke fundet.'); $this->custom_data_redirect($type_key); }
        $binding_usage = $this->custom_data_binding_usage($type_key, $entry_id);
        if ($binding_usage) { $this->set_notice('error', 'Data-entry kan ikke slettes, fordi den bruges i ' . count($binding_usage) . ' dynamiske sektion(er).'); $this->custom_data_redirect($type_key, ['entry_id'=>$entry_id]); }
        $title = (string) $entry->post_title;
        wp_delete_post($entry_id, true);
""",'entry binding delete guard')

# Field removals/type changes are blocked if existing entries or bindings could be broken.
php=once(php,
"""            if ($existing_key === '' && isset($types[$type['Key']])) { throw new RuntimeException('Der findes allerede en datatype med denne nøgle.'); }
            $now = gmdate('c');
""",
"""            if ($existing_key === '' && isset($types[$type['Key']])) { throw new RuntimeException('Der findes allerede en datatype med denne nøgle.'); }
            if ($existing_key !== '' && isset($types[$existing_key])) {
                $old_fields=$this->custom_data_field_map($types[$existing_key]);$new_fields=$this->custom_data_field_map($type);$has_entries=$this->custom_data_entry_count($existing_key)>0;
                foreach($old_fields as $field_key=>$old_field){$breaking=!isset($new_fields[$field_key])||$new_fields[$field_key]['Type']!==$old_field['Type'];if($breaking&&($has_entries||$this->custom_data_binding_usage($existing_key,0,$field_key)))throw new RuntimeException('Feltet “'.$old_field['Label'].'” er i brug og kan derfor ikke fjernes eller skifte type.');}
            }
            $now = gmdate('c');
""",'schema breaking change guard')

# Future-ready data context parameter through renderer/layout/component tree.
php=once(php,
"""    private function render_page_editor_section_front($page_id, array $section, $layout_children = '') {
        if (empty($section['Active'])) {
""",
"""    private function render_page_editor_section_front($page_id, array $section, $layout_children = '', $data_context = null) {
        $section = $this->resolve_page_section_dynamic_bindings($section, $data_context);
        if (empty($section['Active'])) {
""",'section renderer data context')
php=once(php,
"""            return '<div id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" data-h18-component="' . esc_attr($component['Id']) . '" data-h18-component-revision="' . esc_attr($component['Revision']) . '">' . $this->render_page_editor_layout_tree($page_id, $component_sections) . '</div>';
""",
"""            return '<div id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" data-h18-component="' . esc_attr($component['Id']) . '" data-h18-component-revision="' . esc_attr($component['Revision']) . '">' . $this->render_page_editor_layout_tree($page_id, $component_sections, '', 0, $data_context) . '</div>';
""",'component data context forwarding')
layout_start=php.index('    private function render_page_editor_layout_tree(');layout_end=php.index('    private function render_page_editor_front(',layout_start);block=php[layout_start:layout_end]
block=once(block,"    private function render_page_editor_layout_tree($page_id, array $sections, $parent_key = '', $depth = 0) {\n","    private function render_page_editor_layout_tree($page_id, array $sections, $parent_key = '', $depth = 0, $data_context = null) {\n",'layout signature')
block=block.replace("$this->render_page_editor_layout_tree($page_id, $sections, (string) $section['Key'], $depth + 1)","$this->render_page_editor_layout_tree($page_id, $sections, (string) $section['Key'], $depth + 1, $data_context)")
block=block.replace("$this->render_page_editor_section_front($page_id, $section, $children)","$this->render_page_editor_section_front($page_id, $section, $children, $data_context)")
php=php[:layout_start]+block+php[layout_end:]

# Binding controls in section admin.
admin_anchor='''                    <div class="h18-section-type-field h18-section-module-box h18-component-instance-editor" data-types="component">\n'''
binding_box=r'''                    <div class="h18-section-type-field h18-section-module-box h18-dynamic-binding-box" data-types="hero text text_image image buttons card card_grid tabs accordion carousel container flex grid highlight icon list badge quote mail_form poll">
                        <h4>Dynamiske data</h4>
                        <p class="description">Vælg en datatype + entry og bind enkelte egenskaber. Manglende data falder automatisk tilbage til den statiske værdi.</p>
                        <div class="h18-module-fields-grid"><div class="h18-field"><label><strong>Datatype</strong></label><select class="h18-data-context-type" data-selected="<?php echo esc_attr($section['DataContextTypeKey']); ?>" name="<?php echo esc_attr($prefix); ?>[DataContextTypeKey]"><option value="">Statisk</option></select></div><div class="h18-field"><label><strong>Entry</strong></label><select class="h18-data-context-entry" data-selected="<?php echo esc_attr($section['DataContextEntryId']); ?>" name="<?php echo esc_attr($prefix); ?>[DataContextEntryId]"><option value="0">Vælg entry</option></select></div></div>
                        <input class="h18-dynamic-bindings-json" type="hidden" name="<?php echo esc_attr($prefix); ?>[DynamicBindingsJson]" value="<?php echo esc_attr(wp_json_encode($section['DynamicBindings'])); ?>" />
                        <div class="h18-dynamic-binding-status"></div><div class="h18-dynamic-binding-rows"></div>
                    </div>

'''+admin_anchor
php=once(php,admin_anchor,binding_box,'binding admin box')

# Expose data catalog to the page editor.
php=once(php,
"""        $page_templates = $this->get_page_templates_for_editor();
""",
"""        $page_templates = $this->get_page_templates_for_editor();
        $custom_data_catalog = $this->custom_data_types_for_editor();
""",'binding catalog render data')
php=once(php,
"""                <script id="h18-page-templates-data" type="application/json"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <template id="h18-page-section-template"><?php $this->render_page_editor_section_admin($page, $this->default_page_section('text', 10), '__INDEX__', true); ?></template>
""",
"""                <script id="h18-page-templates-data" type="application/json"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <script id="h18-custom-data-catalog" type="application/json"><?php echo wp_json_encode($custom_data_catalog, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <template id="h18-page-section-template"><?php $this->render_page_editor_section_admin($page, $this->default_page_section('text', 10), '__INDEX__', true); ?></template>
""",'binding catalog JSON')

# JavaScript catalog + binding UI.
js=once(js,
"""    const pageTemplatesV0522 = {};
    let navigatorLockedOrderSnapshotV0521 = null;
""",
"""    const pageTemplatesV0522 = {};
    const customDataCatalogV0523 = {};
    let navigatorLockedOrderSnapshotV0521 = null;
""",'binding catalog state')
parse_anchor="""    } catch(templateError){ window.console&&console.warn('Hangar18: kunne ikke læse Page Templates.',templateError); }

    const builtInSectionPresets = {
"""
parse_new="""    } catch(templateError){ window.console&&console.warn('Hangar18: kunne ikke læse Page Templates.',templateError); }
    try { const node=document.getElementById('h18-custom-data-catalog');const rows=node?JSON.parse(node.textContent||'[]'):[];(Array.isArray(rows)?rows:[]).forEach(function(type){if(type&&type.Key)customDataCatalogV0523[String(type.Key)]=type;}); } catch(dataCatalogError){window.console&&console.warn('Hangar18: kunne ikke læse Dynamic Data katalog.',dataCatalogError);}

    const builtInSectionPresets = {
"""
js=once(js,parse_anchor,parse_new,'binding catalog parse')

binding_js=r'''

    const dynamicBindingTargetsV0523={title:{label:'Overskrift',types:['text','number','bool','date']},content:{label:'Tekst',types:['text','number','bool','date']},mediaid:{label:'Billede / medie',types:['media']},button1label:{label:'Knap 1 tekst',types:['text','number','bool','date']},button1url:{label:'Knap 1 link',types:['text']},button2label:{label:'Knap 2 tekst',types:['text','number','bool','date']},button2url:{label:'Knap 2 link',types:['text']}};
    function dataTypeV0523(key){return customDataCatalogV0523[String(key||'')]||null;}
    function dataEntriesV0523(key){const type=dataTypeV0523(key);return type&&Array.isArray(type.Entries)?type.Entries:[];}
    function dataBindingsV0523($row){try{const raw=String(pageSectionControls($row,'.h18-dynamic-bindings-json').val()||'{}');const data=JSON.parse(raw);return data&&typeof data==='object'&&!Array.isArray(data)?data:{};}catch(e){return{};}}
    function writeDataBindingsV0523($row,data){pageSectionControls($row,'.h18-dynamic-bindings-json').val(JSON.stringify(data||{})).trigger('change');}
    function bindingTargetsForRowV0523($row){const type=String($row.attr('data-section-type')||'text');if(['spacer','divider','css','html','shortcode','embed','legacy','component'].includes(type))return[];const result=['title','content'];if(['hero','text_image','image'].includes(type))result.push('mediaid');if(['hero','buttons'].includes(type))result.push('button1label','button1url','button2label','button2url');return result;}
    function refreshDynamicBindingsV0523($row){if(!$row||!$row.length)return;const $type=pageSectionControls($row,'.h18-data-context-type').first();if(!$type.length)return;const $entry=pageSectionControls($row,'.h18-data-context-entry').first();const $rows=pageSectionControls($row,'.h18-dynamic-binding-rows').first();const $status=pageSectionControls($row,'.h18-dynamic-binding-status').first();let selectedType=String($type.val()||$type.attr('data-selected')||'');$type.empty().append($('<option>',{value:'',text:'Statisk'}));Object.values(customDataCatalogV0523).sort(function(a,b){return String(a.SingularLabel||a.Key).localeCompare(String(b.SingularLabel||b.Key),'da');}).forEach(function(item){$type.append($('<option>',{value:String(item.Key),text:String(item.SingularLabel||item.Key)}));});if(selectedType&&!dataTypeV0523(selectedType))selectedType='';$type.val(selectedType).attr('data-selected',selectedType);let selectedEntry=String($entry.val()||$entry.attr('data-selected')||'0');const entries=dataEntriesV0523(selectedType);$entry.empty().append($('<option>',{value:'0',text:selectedType?'Vælg entry':'Vælg datatype først'}));entries.forEach(function(item){$entry.append($('<option>',{value:String(item.Id),text:String(item.Title||('Entry '+item.Id))}));});if(selectedEntry!=='0'&&!entries.some(function(item){return String(item.Id)===selectedEntry;}))selectedEntry='0';$entry.val(selectedEntry).attr('data-selected',selectedEntry);const bindings=dataBindingsV0523($row);const schema=dataTypeV0523(selectedType);const fields=schema&&Array.isArray(schema.Fields)?schema.Fields:[];$rows.empty();let count=0;bindingTargetsForRowV0523($row).forEach(function(targetKey){const target=dynamicBindingTargetsV0523[targetKey];const $line=$('<label>',{class:'h18-dynamic-binding-row'}).append($('<span>',{text:target.label}));const $select=$('<select>',{class:'h18-dynamic-binding-target','data-target':targetKey}).append($('<option>',{value:'',text:'Statisk'}));fields.filter(function(field){return target.types.includes(String(field.Type||'text'));}).forEach(function(field){$select.append($('<option>',{value:String(field.Key),text:'Dynamisk · '+String(field.Label||field.Key)}));});const current=String(bindings[targetKey]||'');if(current&&$select.find('option[value="'+current.replace(/"/g,'\\"')+'"]').length){$select.val(current);count+=1;}else if(current)delete bindings[targetKey];$line.append($select);$rows.append($line);});writeDataBindingsV0523($row,bindings);$status.empty().append($('<span>',{class:'h18-dynamic-status-chip '+(count&&selectedEntry!=='0'?'is-dynamic':'is-static'),text:count&&selectedEntry!=='0'?count+' dynamiske binding(er)':'Statisk / fallback'}));}
    function refreshAllDynamicBindingsV0523(){$pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function(){refreshDynamicBindingsV0523($(this));});}
    $(document).on('change','.h18-data-context-type',function(){const $row=pageSectionForElement(this);$(this).attr('data-selected',String($(this).val()||''));pageSectionControls($row,'.h18-data-context-entry').val('0').attr('data-selected','0');writeDataBindingsV0523($row,{});refreshDynamicBindingsV0523($row);renderCanvasPreview($row);scheduleEditorHistoryCapture(0);});
    $(document).on('change','.h18-data-context-entry',function(){const $row=pageSectionForElement(this);$(this).attr('data-selected',String($(this).val()||'0'));refreshDynamicBindingsV0523($row);renderCanvasPreview($row);scheduleEditorHistoryCapture(0);});
    $(document).on('change','.h18-dynamic-binding-target',function(){const $row=pageSectionForElement(this);const bindings=dataBindingsV0523($row);const target=String($(this).attr('data-target')||'');const field=String($(this).val()||'');if(target){if(field)bindings[target]=field;else delete bindings[target];writeDataBindingsV0523($row,bindings);}refreshDynamicBindingsV0523($row);renderCanvasPreview($row);scheduleEditorHistoryCapture(0);});
'''
js=once(js,"\n    const builtInSectionPresets = {",binding_js+"\n\n    const builtInSectionPresets = {",'binding JS')

js=once(js,
"""        if (type === 'component') { renderComponentInstanceEditorV0521($row); }
        rebuildPageNavigator();
""",
"""        if (type === 'component') { renderComponentInstanceEditorV0521($row); }
        refreshDynamicBindingsV0523($row);
        rebuildPageNavigator();
""",'binding refresh on type')
js=once(js,
"""        renderPageTemplatesV0522();
        refreshAllComponentEditorsV0521();
        rebuildPageNavigator();
""",
"""        renderPageTemplatesV0522();
        refreshAllDynamicBindingsV0523();
        refreshAllComponentEditorsV0521();
        rebuildPageNavigator();
""",'initial binding render')

# Canvas status badge; actual frontend is server-resolved, while editor values remain explicit fallback controls.
js=once(js,
"""        const type = String($row.attr('data-section-type') || 'text');
        const $inner = $('<div>', { class: 'h18-canvas-preview-inner' });
""",
"""        const type = String($row.attr('data-section-type') || 'text');
        const $inner = $('<div>', { class: 'h18-canvas-preview-inner' });
        const dynamicBindingCountV0523=Object.keys(dataBindingsV0523($row)).length;const dynamicEntryV0523=String(pageSectionControls($row,'.h18-data-context-entry').val()||pageSectionControls($row,'.h18-data-context-entry').attr('data-selected')||'0');if(dynamicBindingCountV0523&&dynamicEntryV0523!=='0')$inner.append($('<div>',{class:'h18-canvas-dynamic-badge',text:'Dynamic · '+dynamicBindingCountV0523+' binding(er)'}));
""",'canvas binding badge')

# Data schema UI CSS now has one more column; binding controls styling.
css=css.replace('grid-template-columns:auto minmax(120px,.8fr) minmax(180px,1.2fr) minmax(120px,.7fr) auto auto','grid-template-columns:auto minmax(110px,.8fr) minmax(150px,1.1fr) minmax(110px,.7fr) minmax(130px,.8fr) auto auto')
css_block=r'''

/* v0.5.23 – Dynamic bindings */
.h18-dynamic-binding-box{border-color:#b9d7ed;background:#f7fbfe}.h18-dynamic-binding-status{margin:9px 0}.h18-dynamic-status-chip{display:inline-flex;padding:4px 8px;border-radius:999px;background:#f0f0f1;color:#50575e;font-size:12px;font-weight:700}.h18-dynamic-status-chip.is-dynamic{background:#dff3e4;color:#0a5c2b}.h18-dynamic-binding-rows{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.h18-dynamic-binding-row{display:grid;gap:4px}.h18-dynamic-binding-row>span{font-size:12px;font-weight:600}.h18-canvas-dynamic-badge{display:inline-flex;margin-bottom:8px;padding:3px 7px;border-radius:999px;background:#dff3e4;color:#0a5c2b;font-size:11px;font-weight:700}@media(max-width:1000px){.h18-dynamic-binding-rows{grid-template-columns:1fr}}
'''
if '/* v0.5.23 – Dynamic bindings */' in css:raise SystemExit('binding CSS already present')
css=css.rstrip()+css_block+'\n'

# Existing base-patch release notes become the complete UD-051/052/053 notes.
readme=readme.replace('- schemas understøtter text, number, bool, date og media fields med stabile keys, labels, required-flag og validering','- schemas understøtter text, number, bool, date og media fields med stabile keys, labels, required-flag, standard/preset-værdi og validering')
readme=readme.replace('- datamotoren er foundation for UD-053 dynamic binding og UD-055 Query Builder; Vehicle/Event/Gallery migreres senere via UD-060 presets, ikke via endnu en specialmotor','- UD-053: elementer kan binde Overskrift, Tekst, Media og knaptekst/links til en valgt datatype + entry med tydelig Dynamic/Static-status og statisk fallback\n- datatype/entry-delete og breaking schema-ændringer blokeres, mens gemte pages/components/patterns/templates bruger dem\n- binding-rendereren har allerede en generisk data_context parameter, så UD-057 Query/Repeater kan genbruge samme motor i næste release')
readme=readme.replace('- page-editor schema forbliver 1.18; denne release ændrer ikke eksisterende side-JSON','- page-editor schema løftes bagudkompatibelt til 1.19 for eksplicit data-context og DynamicBindings')

php_path.write_text(php);js_path.write_text(js);css_path.write_text(css);readme_path.write_text(readme)
print('v0.5.23 hardening and UD-053 binding applied')
