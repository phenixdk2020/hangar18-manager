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

# Version + page-editor schema.
php=once(php,' * Version: 0.5.26',' * Version: 0.5.27','plugin header version')
php=once(php,"    const VERSION = '0.5.26';","    const VERSION = '0.5.27';",'plugin const version')
php=php.replace("'1.20'", "'1.21'")

# Localized editor environment for user/date preview. Capabilities are read-only editor hints,
# not an authorization boundary; frontend is always evaluated server-side.
php=once(php,
"""            'pagePresetNonce'      => wp_create_nonce('h18_page_presets_v051'),
            'pageComponentNonce'   => wp_create_nonce('h18_page_components_v0521'),
            'pageTemplateNonce'    => wp_create_nonce('h18_page_templates_v0522'),
        ]);
""",
"""            'pagePresetNonce'      => wp_create_nonce('h18_page_presets_v051'),
            'pageComponentNonce'   => wp_create_nonce('h18_page_components_v0521'),
            'pageTemplateNonce'    => wp_create_nonce('h18_page_templates_v0522'),
            'conditionUser'        => (function () {
                $user = wp_get_current_user();
                $caps = [];
                foreach ((array) $user->allcaps as $capability => $granted) {
                    if ($granted) { $caps[] = sanitize_key((string) $capability); }
                }
                sort($caps, SORT_STRING);
                return [
                    'LoggedIn' => is_user_logged_in(),
                    'Roles' => array_values(array_map('sanitize_key', (array) $user->roles)),
                    'Capabilities' => array_values(array_unique($caps)),
                ];
            })(),
            'conditionNow'         => wp_date('Y-m-d\\TH:i:sP', time(), wp_timezone()),
        ]);
""",'condition preview environment')

# Generic condition engine lives next to dynamic binding engine.
condition_engine=r'''

    /* ================================================================
       CONDITIONAL VISIBILITY ENGINE — v0.5.27 / E5 UD-058
       ================================================================ */

    private function normalize_page_conditions($raw) {
        if (is_string($raw) && $raw !== '') {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) { $raw = $decoded; }
        }
        if (!is_array($raw)) { return []; }
        $allowed = [
            'data' => ['empty','not_empty','eq','neq','gt','gte','lt','lte'],
            'user' => ['logged_in','logged_out','role','capability'],
            'date' => ['before','after','between'],
        ];
        $conditions = [];
        foreach (array_slice(array_values($raw), 0, 8) as $index => $item) {
            if (!is_array($item)) { continue; }
            $type = sanitize_key((string) ($item['Type'] ?? ''));
            $operator = sanitize_key((string) ($item['Operator'] ?? ''));
            if (!isset($allowed[$type]) || !in_array($operator, $allowed[$type], true)) { continue; }
            $field = sanitize_key((string) ($item['Field'] ?? ''));
            $value = sanitize_text_field((string) ($item['Value'] ?? ''));
            $value2 = sanitize_text_field((string) ($item['Value2'] ?? ''));
            if (strlen($value) > 300) { $value = substr($value, 0, 300); }
            if (strlen($value2) > 300) { $value2 = substr($value2, 0, 300); }
            if ($type === 'data' && $field === '') { continue; }
            if ($type === 'user' && in_array($operator, ['role','capability'], true)) {
                $value = sanitize_key($value);
                if ($value === '') { continue; }
            }
            if ($type === 'date') {
                if (!$this->page_condition_datetime_timestamp($value)) { continue; }
                if ($operator === 'between' && !$this->page_condition_datetime_timestamp($value2)) { continue; }
            }
            $id = sanitize_key((string) ($item['Id'] ?? ''));
            if ($id === '') { $id = 'condition-' . ($index + 1); }
            $conditions[] = [
                'Id' => $id,
                'Type' => $type,
                'Operator' => $operator,
                'Field' => $field,
                'Value' => $value,
                'Value2' => $value2,
            ];
        }
        return $conditions;
    }

    private function page_condition_datetime_timestamp($value) {
        $value = trim((string) $value);
        if ($value === '') { return 0; }
        $timezone = wp_timezone();
        $formats = ['!Y-m-d\\TH:i', '!Y-m-d H:i', '!Y-m-d'];
        foreach ($formats as $format) {
            $date = DateTimeImmutable::createFromFormat($format, $value, $timezone);
            if ($date instanceof DateTimeImmutable) {
                $errors = DateTimeImmutable::getLastErrors();
                if ($errors === false || (((int) ($errors['warning_count'] ?? 0)) === 0 && ((int) ($errors['error_count'] ?? 0)) === 0)) {
                    $roundtrip = $date->format(str_replace('!', '', $format));
                    if ($roundtrip === $value) { return $date->getTimestamp(); }
                }
            }
        }
        return 0;
    }

    private function page_condition_value_is_empty($value, $field_type = '') {
        if ($value === null || $value === '') { return true; }
        if ($field_type === 'media' && absint($value) <= 0) { return true; }
        return false;
    }

    private function evaluate_page_condition(array $condition, $context = null, $timestamp = null) {
        $type = (string) ($condition['Type'] ?? '');
        $operator = (string) ($condition['Operator'] ?? '');
        if ($type === 'data') {
            $field_key = sanitize_key((string) ($condition['Field'] ?? ''));
            $fields = is_array($context) && isset($context['Fields']) && is_array($context['Fields']) ? $context['Fields'] : [];
            $values = is_array($context) && isset($context['Values']) && is_array($context['Values']) ? $context['Values'] : [];
            $field_type = isset($fields[$field_key]) ? (string) ($fields[$field_key]['Type'] ?? '') : '';
            $exists = $field_key !== '' && isset($fields[$field_key]) && array_key_exists($field_key, $values);
            $actual = $exists ? $values[$field_key] : null;
            $empty = !$exists || $this->page_condition_value_is_empty($actual, $field_type);
            if ($operator === 'empty') { return $empty; }
            if ($operator === 'not_empty') { return !$empty; }
            if (!$exists) { return false; }
            $expected = (string) ($condition['Value'] ?? '');
            if ($field_type === 'bool') {
                $actual = $this->bool_value($actual, false) ? 1 : 0;
                $expected = $this->bool_value($expected, false) ? 1 : 0;
            } elseif ($field_type === 'number' || (is_numeric($actual) && is_numeric($expected))) {
                $actual = (float) $actual;
                $expected = (float) $expected;
            } elseif ($field_type === 'date') {
                $actual_ts = $this->page_condition_datetime_timestamp((string) $actual);
                $expected_ts = $this->page_condition_datetime_timestamp((string) $expected);
                if (!$actual_ts || !$expected_ts) { return false; }
                $actual = $actual_ts;
                $expected = $expected_ts;
            } else {
                $actual = (string) $actual;
                $expected = (string) $expected;
            }
            if ($operator === 'eq') { return $actual == $expected; }
            if ($operator === 'neq') { return $actual != $expected; }
            if ($operator === 'gt') { return $actual > $expected; }
            if ($operator === 'gte') { return $actual >= $expected; }
            if ($operator === 'lt') { return $actual < $expected; }
            if ($operator === 'lte') { return $actual <= $expected; }
            return false;
        }
        if ($type === 'user') {
            if ($operator === 'logged_in') { return is_user_logged_in(); }
            if ($operator === 'logged_out') { return !is_user_logged_in(); }
            $value = sanitize_key((string) ($condition['Value'] ?? ''));
            if ($operator === 'role') {
                $user = wp_get_current_user();
                return $value !== '' && in_array($value, array_map('sanitize_key', (array) $user->roles), true);
            }
            if ($operator === 'capability') { return $value !== '' && current_user_can($value); }
            return false;
        }
        if ($type === 'date') {
            $now = $timestamp === null ? time() : (int) $timestamp;
            $first = $this->page_condition_datetime_timestamp((string) ($condition['Value'] ?? ''));
            if (!$first) { return false; }
            if ($operator === 'before') { return $now < $first; }
            if ($operator === 'after') { return $now > $first; }
            if ($operator === 'between') {
                $second = $this->page_condition_datetime_timestamp((string) ($condition['Value2'] ?? ''));
                if (!$second) { return false; }
                $min = min($first, $second); $max = max($first, $second);
                return $now >= $min && $now <= $max;
            }
        }
        return false;
    }

    private function evaluate_page_conditions(array $section, $context = null, $timestamp = null) {
        $conditions = $this->normalize_page_conditions($section['Conditions'] ?? []);
        if (!$conditions) { return true; }
        $mode = (string) ($section['ConditionMode'] ?? 'All');
        if (!in_array($mode, ['All','Any'], true)) { $mode = 'All'; }
        if ($mode === 'Any') {
            foreach ($conditions as $condition) {
                if ($this->evaluate_page_condition($condition, $context, $timestamp)) { return true; }
            }
            return false;
        }
        foreach ($conditions as $condition) {
            if (!$this->evaluate_page_condition($condition, $context, $timestamp)) { return false; }
        }
        return true;
    }
'''
php=once(php,
"""    /* ================================================================
       PAGE EDITOR AND FUNCTION MODULES
       ================================================================ */
""",
condition_engine+"""

    /* ================================================================
       PAGE EDITOR AND FUNCTION MODULES
       ================================================================ */
""",'insert condition engine')

# Section model.
php=once(php,
"""            'Bindings'              => [],
            'QueryListType'         => '',
""",
"""            'Bindings'              => [],
            'ConditionMode'         => 'All',
            'Conditions'            => [],
            'QueryListType'         => '',
""",'default conditions')

php=once(php,
"""        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);
        $query_list_type = sanitize_key((string) ($raw['QueryListType'] ?? ''));
""",
"""        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);
        $condition_mode = (string) ($raw['ConditionMode'] ?? 'All');
        if (!in_array($condition_mode, ['All','Any'], true)) { $condition_mode = 'All'; }
        $conditions_raw = $raw['Conditions'] ?? [];
        if ((!is_array($conditions_raw) || !$conditions_raw) && isset($raw['ConditionsJson']) && is_string($raw['ConditionsJson'])) {
            $decoded_conditions = json_decode((string) $raw['ConditionsJson'], true);
            if (is_array($decoded_conditions)) { $conditions_raw = $decoded_conditions; }
        }
        $conditions = $this->normalize_page_conditions($conditions_raw);
        $query_list_type = sanitize_key((string) ($raw['QueryListType'] ?? ''));
""",'normalize conditions')

php=once(php,
"""            'Bindings'              => $bindings,
            'QueryListType'         => $query_list_type,
""",
"""            'Bindings'              => $bindings,
            'ConditionMode'         => $condition_mode,
            'Conditions'            => $conditions,
            'QueryListType'         => $query_list_type,
""",'normalized conditions return')

# Runtime conditions happen before bindings and before special renderers.
php=once(php,
"""        if (empty($section['Active'])) {
            return '';
        }
        if (is_array($this->active_dynamic_data_context)) {
            $section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context);
        }
""",
"""        if (empty($section['Active'])) {
            return '';
        }
        if (!$this->evaluate_page_conditions($section, $this->active_dynamic_data_context)) {
            return '';
        }
        if (is_array($this->active_dynamic_data_context)) {
            $section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context);
        }
""",'runtime conditional visibility')

# Admin condition editor after dynamic bindings, before Query List panel.
condition_admin=r'''

                    <div class="h18-section-module-box h18-condition-editor" data-condition-editor>
                        <h4>Conditions / synlighed</h4>
                        <p class="description">Vis eller skjul elementet ud fra data, bruger eller dato/tid. Conditions er præsentationslogik og må ikke bruges som adgangskontrol eller sikkerhedsgrænse.</p>
                        <div class="h18-module-fields-grid h18-module-fields-grid--two">
                            <div class="h18-field"><label><strong>Kombinér betingelser</strong></label><select class="h18-condition-mode" name="<?php echo esc_attr($prefix); ?>[ConditionMode]"><option value="All" <?php selected($section['ConditionMode'],'All'); ?>>Alle skal være opfyldt (AND)</option><option value="Any" <?php selected($section['ConditionMode'],'Any'); ?>>Mindst én skal være opfyldt (OR)</option></select></div>
                        </div>
                        <input class="h18-conditions-json" type="hidden" name="<?php echo esc_attr($prefix); ?>[ConditionsJson]" value="<?php echo esc_attr(wp_json_encode(array_values((array) $section['Conditions']))); ?>" />
                        <div class="h18-condition-list"></div>
                        <p><button type="button" class="button h18-condition-add">Tilføj condition</button> <span class="description">Maks. 8 pr. element.</span></p>
                    </div>
'''
php=once(php,
"""                        <?php endforeach; ?>
                    </div>



                    <div class=\"h18-section-type-field h18-section-module-box h18-query-list-editor\" data-types=\"query_list\">
""",
"""                        <?php endforeach; ?>
                    </div>
"""+condition_admin+"""

                    <div class=\"h18-section-type-field h18-section-module-box h18-query-list-editor\" data-types=\"query_list\">
""",'condition editor UI')

# JS condition engine before refreshPageSectionType; preview keeps hidden items editable.
condition_js=r'''

    /* v0.5.27 – UD-058 Conditional Visibility */
    function conditionEnvironmentV0527() {
        const user = Hangar18Manager.conditionUser && typeof Hangar18Manager.conditionUser === 'object' ? Hangar18Manager.conditionUser : {LoggedIn:false,Roles:[],Capabilities:[]};
        const nowRaw = String(Hangar18Manager.conditionNow || '');
        const parsed = Date.parse(nowRaw);
        return {user:user, now:Number.isFinite(parsed)?parsed:Date.now()};
    }
    function conditionDataContextV0527() {
        const definition = dynamicContextDefinitionV0524();
        const entry = dynamicContextEntryV0524();
        if (!definition || !entry) return null;
        const fields={}; (Array.isArray(definition.Fields)?definition.Fields:[]).forEach(function(field){if(field&&field.Key)fields[String(field.Key)]=field;});
        return {Fields:fields,Values:(entry.Values&&typeof entry.Values==='object')?entry.Values:{}};
    }
    function parseConditionsV0527($row) {
        const $hidden=pageSectionControls($row,'.h18-conditions-json').first();
        try { const parsed=JSON.parse(String($hidden.val()||'[]')); return Array.isArray(parsed)?parsed.slice(0,8):[]; } catch(e){ return []; }
    }
    function conditionOperatorsV0527(type) {
        const map={data:[['empty','Er tomt'],['not_empty','Er udfyldt'],['eq','Er lig med'],['neq','Er ikke lig med'],['gt','Større end'],['gte','Større/lig'],['lt','Mindre end'],['lte','Mindre/lig']],user:[['logged_in','Bruger er logget ind'],['logged_out','Bruger er logget ud'],['role','Bruger har rolle'],['capability','Bruger har capability']],date:[['before','Nu er før'],['after','Nu er efter'],['between','Nu er mellem']]};
        return map[String(type||'')]||map.data;
    }
    function conditionNewIdV0527(){return 'condition-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7);}
    function conditionEditorFieldOptionsV0527() {
        const definition=dynamicContextDefinitionV0524(); return definition&&Array.isArray(definition.Fields)?definition.Fields:[];
    }
    function syncConditionsFromEditorV0527($row) {
        const items=[];
        pageSectionControls($row,'.h18-condition-row').each(function(){
            const $item=$(this); if(items.length>=8)return false;
            items.push({Id:String($item.attr('data-condition-id')||conditionNewIdV0527()),Type:String($item.find('.h18-condition-type').val()||'data'),Operator:String($item.find('.h18-condition-operator').val()||'empty'),Field:String($item.find('.h18-condition-field').val()||''),Value:String($item.find('.h18-condition-value').val()||''),Value2:String($item.find('.h18-condition-value2').val()||'')});
        });
        pageSectionControls($row,'.h18-conditions-json').val(JSON.stringify(items));
        return items;
    }
    function refreshConditionRowV0527($item, condition) {
        condition=condition||{}; const type=String(condition.Type||$item.find('.h18-condition-type').val()||'data');
        $item.find('.h18-condition-type').val(type);
        const $operator=$item.find('.h18-condition-operator'); let op=String(condition.Operator||$operator.val()||conditionOperatorsV0527(type)[0][0]); $operator.empty(); conditionOperatorsV0527(type).forEach(function(pair){$operator.append($('<option>',{value:pair[0],text:pair[1]}));}); if(!$operator.find('option').filter(function(){return String($(this).val())===op;}).length)op=conditionOperatorsV0527(type)[0][0]; $operator.val(op);
        const $field=$item.find('.h18-condition-field'); let field=String(condition.Field||$field.val()||''); $field.empty().append($('<option>',{value:'',text:'Vælg datafelt'})); conditionEditorFieldOptionsV0527().forEach(function(f){$field.append($('<option>',{value:String(f.Key),text:String(f.Label||f.Key)+' · '+String(f.Type||'text')}));}); if(!$field.find('option').filter(function(){return String($(this).val())===field;}).length)field=''; $field.val(field);
        const needsField=type==='data'; const needsValue=(type==='data'&&!['empty','not_empty'].includes(op))||(type==='user'&&['role','capability'].includes(op))||type==='date'; const needsValue2=type==='date'&&op==='between';
        $item.find('.h18-condition-field-wrap').toggle(needsField); $item.find('.h18-condition-value-wrap').toggle(needsValue); $item.find('.h18-condition-value2-wrap').toggle(needsValue2);
        const $value=$item.find('.h18-condition-value'); const $value2=$item.find('.h18-condition-value2');
        $value.attr('type',type==='date'?'datetime-local':'text'); $value2.attr('type','datetime-local');
        if(Object.prototype.hasOwnProperty.call(condition,'Value'))$value.val(String(condition.Value||'')); if(Object.prototype.hasOwnProperty.call(condition,'Value2'))$value2.val(String(condition.Value2||''));
        if(type==='user'&&op==='role')$value.attr('placeholder','fx administrator'); else if(type==='user'&&op==='capability')$value.attr('placeholder','fx edit_pages'); else $value.attr('placeholder','Værdi');
    }
    function conditionRowV0527(condition) {
        condition=condition||{}; const id=String(condition.Id||conditionNewIdV0527()); const $item=$('<div>',{class:'h18-condition-row','data-condition-id':id});
        const $type=$('<select>',{class:'h18-condition-type'}).append('<option value="data">Data</option><option value="user">Bruger</option><option value="date">Dato/tid</option>');
        const $op=$('<select>',{class:'h18-condition-operator'}); const $field=$('<select>',{class:'h18-condition-field'}); const $value=$('<input>',{class:'h18-condition-value',type:'text'}); const $value2=$('<input>',{class:'h18-condition-value2',type:'datetime-local'});
        $item.append($('<div>',{class:'h18-field'}).append($('<label><strong>Type</strong></label>'),$type),$('<div>',{class:'h18-field'}).append($('<label><strong>Operator</strong></label>'),$op),$('<div>',{class:'h18-field h18-condition-field-wrap'}).append($('<label><strong>Felt</strong></label>'),$field),$('<div>',{class:'h18-field h18-condition-value-wrap'}).append($('<label><strong>Værdi</strong></label>'),$value),$('<div>',{class:'h18-field h18-condition-value2-wrap'}).append($('<label><strong>Slut</strong></label>'),$value2),$('<button>',{type:'button',class:'button-link-delete h18-condition-remove',text:'Fjern'}));
        refreshConditionRowV0527($item,condition); return $item;
    }
    function refreshConditionEditorV0527($row) {
        if(!$row||!$row.length)return; const $list=pageSectionControls($row,'.h18-condition-list').first(); if(!$list.length)return;
        const conditions=parseConditionsV0527($row); $list.empty(); conditions.forEach(function(condition){$list.append(conditionRowV0527(condition));}); evaluateConditionPreviewV0527($row);
    }
    function conditionEmptyV0527(value,fieldType){return value===null||value===undefined||value===''||(fieldType==='media'&&(parseInt(value,10)||0)<=0);}
    function conditionDateV0527(value){const text=String(value||''); if(!text)return NaN; const normalized=/^\d{4}-\d{2}-\d{2}$/.test(text)?text+'T00:00':text; return Date.parse(normalized);}
    function evaluateOneConditionV0527(condition,context,env) {
        const type=String(condition.Type||''); const op=String(condition.Operator||'');
        if(type==='data'){
            const key=String(condition.Field||''); const field=context&&context.Fields?context.Fields[key]:null; const has=Boolean(field)&&context&&context.Values&&Object.prototype.hasOwnProperty.call(context.Values,key); const actual=has?context.Values[key]:null; const fieldType=field?String(field.Type||''):''; const empty=!has||conditionEmptyV0527(actual,fieldType); if(op==='empty')return empty;if(op==='not_empty')return !empty;if(!has)return false; let expected=String(condition.Value||''); let a=actual,b=expected;
            if(fieldType==='bool'){a=Boolean(actual===true||actual===1||String(actual).toLowerCase()==='1'||String(actual).toLowerCase()==='true'||String(actual).toLowerCase()==='yes'||String(actual).toLowerCase()==='ja')?1:0;b=Boolean(['1','true','yes','ja','on'].includes(String(expected).toLowerCase()))?1:0;} else if(fieldType==='number'||(!Number.isNaN(Number(a))&&!Number.isNaN(Number(b))&&String(a).trim()!==''&&String(b).trim()!=='')){a=Number(a);b=Number(b);} else if(fieldType==='date'){a=conditionDateV0527(a);b=conditionDateV0527(b);if(!Number.isFinite(a)||!Number.isFinite(b))return false;} else {a=String(a);b=String(b);}
            if(op==='eq')return a==b;if(op==='neq')return a!=b;if(op==='gt')return a>b;if(op==='gte')return a>=b;if(op==='lt')return a<b;if(op==='lte')return a<=b;return false;
        }
        if(type==='user'){const user=env.user||{};if(op==='logged_in')return Boolean(user.LoggedIn);if(op==='logged_out')return !Boolean(user.LoggedIn);const value=String(condition.Value||'');if(op==='role')return Array.isArray(user.Roles)&&user.Roles.includes(value);if(op==='capability')return Array.isArray(user.Capabilities)&&user.Capabilities.includes(value);return false;}
        if(type==='date'){const first=conditionDateV0527(condition.Value);if(!Number.isFinite(first))return false;if(op==='before')return env.now<first;if(op==='after')return env.now>first;if(op==='between'){const second=conditionDateV0527(condition.Value2);if(!Number.isFinite(second))return false;return env.now>=Math.min(first,second)&&env.now<=Math.max(first,second);}return false;}
        return false;
    }
    function evaluateConditionPreviewV0527($row) {
        if(!$row||!$row.length)return true; const conditions=parseConditionsV0527($row); let visible=true; if(conditions.length){const mode=String(pageSectionControls($row,'.h18-condition-mode').val()||'All');const context=conditionDataContextV0527();const env=conditionEnvironmentV0527();const results=conditions.map(function(c){return evaluateOneConditionV0527(c,context,env);});visible=mode==='Any'?results.some(Boolean):results.every(Boolean);} $row.toggleClass('h18-condition-preview-hidden',!visible); const $preview=ensureCanvasPreview($row); if($preview.length){$preview.toggleClass('h18-condition-preview-hidden',!visible);$preview.find('.h18-condition-preview-badge').remove();if(!visible)$preview.append($('<span>',{class:'h18-condition-preview-badge',text:'Skjult af conditions'}));} return visible;
    }
    $(document).on('click','.h18-condition-add',function(){const $row=pageSectionForElement($(this));const current=parseConditionsV0527($row);if(current.length>=8){window.alert('Et element kan højst have 8 conditions.');return;}current.push({Id:conditionNewIdV0527(),Type:'data',Operator:'empty',Field:'',Value:'',Value2:''});pageSectionControls($row,'.h18-conditions-json').val(JSON.stringify(current));refreshConditionEditorV0527($row);scheduleEditorHistoryCapture(0);});
    $(document).on('click','.h18-condition-remove',function(){const $row=pageSectionForElement($(this));$(this).closest('.h18-condition-row').remove();syncConditionsFromEditorV0527($row);evaluateConditionPreviewV0527($row);scheduleEditorHistoryCapture(0);});
    $(document).on('change input','.h18-condition-type,.h18-condition-operator,.h18-condition-field,.h18-condition-value,.h18-condition-value2,.h18-condition-mode',function(){const $row=pageSectionForElement($(this));const $item=$(this).closest('.h18-condition-row');if($item.length)refreshConditionRowV0527($item,{});syncConditionsFromEditorV0527($row);evaluateConditionPreviewV0527($row);scheduleEditorHistoryCapture(250);});
'''
js=once(js,
"""    function refreshPageSectionType($row) {
""",
condition_js+"""

    function refreshPageSectionType($row) {
""",'condition JS engine')

js=once(js,
"""        $row.attr('data-section-type', type);
        refreshQueryListControlsV0526($row);
        pageSectionControls($row, '.h18-section-type-field').each(function () {
""",
"""        $row.attr('data-section-type', type);
        refreshQueryListControlsV0526($row);
        refreshConditionEditorV0527($row);
        pageSectionControls($row, '.h18-section-type-field').each(function () {
""",'refresh conditions on type')

# Re-evaluate visibility after each canvas render and when page context changes.
js=once(js,
"""    function renderCanvasPreview($row) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return; }
        const $preview = ensureCanvasPreview($row);
""",
"""    function renderCanvasPreview($row) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return; }
        const $preview = ensureCanvasPreview($row);
""",'canvas function stable anchor')
# Hook at every global canvas refresh through existing context change handler.
js=once(js,
"""    $pageDataContextTypeV0524.on('change', function () { refreshPageDataContextEntriesV0524(false); refreshDynamicBindingsV0524($('.h18-pages-admin')); refreshAllCanvasPreviews(); });
    $pageDataContextEntryV0524.on('change', function () { $(this).attr('data-current-entry', String($(this).val() || '0')); refreshAllCanvasPreviews(); });
""",
"""    $pageDataContextTypeV0524.on('change', function () { refreshPageDataContextEntriesV0524(false); refreshDynamicBindingsV0524($('.h18-pages-admin')); refreshAllCanvasPreviews(); $pageSections.children('.h18-page-section-row').each(function(){evaluateConditionPreviewV0527($(this));}); });
    $pageDataContextEntryV0524.on('change', function () { $(this).attr('data-current-entry', String($(this).val() || '0')); refreshAllCanvasPreviews(); $pageSections.children('.h18-page-section-row').each(function(){evaluateConditionPreviewV0527($(this));}); });
""",'context condition preview refresh')

# ConditionsJson is structural metadata and should survive Pattern/Component/Template serialization automatically.
# sectionPresetData already serializes unexcluded section-level named controls; no special JS fork required.

css += """

/* v0.5.27 – UD-058 Conditional Visibility */
.h18-condition-editor{border-left:3px solid #8b4a2b}.h18-condition-list{display:grid;gap:10px;margin:12px 0}.h18-condition-row{display:grid;grid-template-columns:repeat(5,minmax(0,1fr)) auto;gap:8px;align-items:end;padding:10px;border:1px solid #dcdcde;border-radius:7px;background:#fff}.h18-condition-row .h18-field{margin:0}.h18-condition-preview-hidden{opacity:.52}.h18-canvas-section-preview.h18-condition-preview-hidden{position:relative;outline:2px dashed #b32d2e;outline-offset:-2px}.h18-condition-preview-badge{position:absolute;top:8px;right:8px;z-index:4;padding:4px 8px;border-radius:999px;background:#b32d2e;color:#fff;font-size:11px;font-weight:700;pointer-events:none}@media(max-width:1100px){.h18-condition-row{grid-template-columns:repeat(2,minmax(0,1fr))}.h18-condition-row>.h18-condition-remove{grid-column:1/-1;justify-self:start}}
"""

readme=once(readme,'Version: 0.5.26','Version: 0.5.27','readme version')
readme += """

## v0.5.27 – E5 UD-058 Conditional Visibility
- Alle page-builder elementer får generiske Conditions med AND/OR mode.
- Data conditions: empty/not-empty/equality/comparison mod current data context.
- User conditions: logged in/out, rolle og capability.
- Date/time conditions: før, efter og mellem i WordPress-site timezone.
- Conditions evalueres server-side før dynamic binding og virker derfor også pr. resultat inde i Query Lists.
- Editor-preview evaluerer samme condition-model og markerer skjulte elementer uden at fjerne dem fra canvas.
- Conditions er præsentationslogik og er eksplicit ikke en authorization/security boundary.
- Maks. 8 conditions pr. element; ukendte typer/operatorer droppes under normalisering.
- Page-editor schema: 1.21.
"""

php_path.write_text(php); js_path.write_text(js); css_path.write_text(css); readme_path.write_text(readme)
print('v0.5.27 UD-058 Conditional Visibility patch applied')
