from pathlib import Path

php_path=Path('hangar18-manager.php'); js_path=Path('assets/admin.js'); css_path=Path('assets/admin.css'); readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

def once(text,old,new,label):
    count=text.count(old)
    if count!=1: raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old,new,1)

php=once(php,' * Version: 0.5.29',' * Version: 0.5.30','plugin version')
php=once(php,"    const VERSION = '0.5.29';","    const VERSION = '0.5.30';",'const version')
php=php.replace("'1.21'", "'1.22'")

# Persistent section options layer; Bindings map itself remains unchanged.
php=once(php,"""            'Bindings'              => [],
            'ConditionMode'         => 'All',
""","""            'Bindings'              => [],
            'BindingOptions'        => [],
            'ConditionMode'         => 'All',
""",'binding options default')
php=once(php,"""        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);
        $condition_mode = (string) ($raw['ConditionMode'] ?? 'All');
""","""        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);
        $binding_options = $this->normalize_dynamic_binding_options($raw['BindingOptions'] ?? []);
        $condition_mode = (string) ($raw['ConditionMode'] ?? 'All');
""",'binding options normalize call')
php=once(php,"""            'Bindings'              => $bindings,
            'ConditionMode'         => $condition_mode,
""","""            'Bindings'              => $bindings,
            'BindingOptions'        => $binding_options,
            'ConditionMode'         => $condition_mode,
""",'binding options normalized return')

# Add formatter/options helpers immediately after normalize_dynamic_bindings().
needle="""        return $bindings;
    }

    private function dynamic_data_context_catalog_for_editor() {
"""
helpers=r'''        return $bindings;
    }

    private function dynamic_binding_formatters() {
        return [
            'Auto'=>'Automatisk',
            'Text'=>'Tekst',
            'Upper'=>'STORE BOGSTAVER',
            'Lower'=>'små bogstaver',
            'Number0'=>'Tal · 0 decimaler',
            'Number1'=>'Tal · 1 decimal',
            'Number2'=>'Tal · 2 decimaler',
            'DateShort'=>'Dato · 31.12.2026',
            'DateIso'=>'Dato · 2026-12-31',
            'DateLong'=>'Dato · 31. december 2026',
            'BoolYesNo'=>'Ja / Nej',
        ];
    }

    private function normalize_dynamic_binding_options($raw) {
        if (is_string($raw) && $raw !== '') {
            $decoded=json_decode($raw,true); if(is_array($decoded))$raw=$decoded;
        }
        if(!is_array($raw))return[];
        $properties=$this->dynamic_binding_property_types();$formatters=$this->dynamic_binding_formatters();$out=[];
        foreach($raw as $property=>$option){
            $property=(string)$property;if(!isset($properties[$property])||!is_array($option))continue;
            $formatter=(string)($option['Formatter']??'Auto');if(!isset($formatters[$formatter]))$formatter='Auto';
            $fallback_mode=(string)($option['FallbackMode']??'Static');if(!in_array($fallback_mode,['Static','Custom','Empty'],true))$fallback_mode='Static';
            $fallback=sanitize_text_field((string)($option['Fallback']??''));if(strlen($fallback)>2000)$fallback=substr($fallback,0,2000);
            $prefix=sanitize_text_field((string)($option['Prefix']??''));if(strlen($prefix)>100)$prefix=substr($prefix,0,100);
            $suffix=sanitize_text_field((string)($option['Suffix']??''));if(strlen($suffix)>100)$suffix=substr($suffix,0,100);
            $out[$property]=['Formatter'=>$formatter,'FallbackMode'=>$fallback_mode,'Fallback'=>$fallback,'FallbackWhenEmpty'=>!empty($option['FallbackWhenEmpty']),'Prefix'=>$prefix,'Suffix'=>$suffix];
        }
        return$out;
    }

    private function dynamic_binding_option_for_property(array $options,$property) {
        return isset($options[$property])&&is_array($options[$property])?$options[$property]:['Formatter'=>'Auto','FallbackMode'=>'Static','Fallback'=>'','FallbackWhenEmpty'=>false,'Prefix'=>'','Suffix'=>''];
    }

    private function dynamic_binding_value_is_empty($value,$field_type='') {
        if($value===null||$value==='')return true;
        if(is_array($value)&&!$value)return true;
        if($field_type==='media'&&absint($value)<=0)return true;
        return false;
    }

    private function dynamic_binding_format_value($value,$field_type,$formatter) {
        $formatter=(string)$formatter;$field_type=(string)$field_type;
        if($formatter==='Auto')return $this->dynamic_binding_text_value($value);
        if($formatter==='Text')return $this->dynamic_binding_text_value($value);
        if($formatter==='Upper'||$formatter==='Lower'){
            if(!in_array($field_type,['text','number','bool','date'],true))return null;$text=$this->dynamic_binding_text_value($value);
            if($formatter==='Upper')return function_exists('mb_strtoupper')?mb_strtoupper($text,'UTF-8'):strtoupper($text);
            return function_exists('mb_strtolower')?mb_strtolower($text,'UTF-8'):strtolower($text);
        }
        if(in_array($formatter,['Number0','Number1','Number2'],true)){
            if(!is_numeric($value))return null;$decimals=(int)substr($formatter,-1);return number_format_i18n((float)$value,$decimals);
        }
        if(in_array($formatter,['DateShort','DateIso','DateLong'],true)){
            $raw=trim((string)$value);$date=DateTimeImmutable::createFromFormat('!Y-m-d',$raw,wp_timezone());$errors=DateTimeImmutable::getLastErrors();
            if(!$date||($errors!==false&&(((int)($errors['warning_count']??0))>0||((int)($errors['error_count']??0))>0))||$date->format('Y-m-d')!==$raw)return null;
            $format=$formatter==='DateShort'?'d.m.Y':($formatter==='DateIso'?'Y-m-d':'j. F Y');return wp_date($format,$date->getTimestamp(),wp_timezone());
        }
        if($formatter==='BoolYesNo')return $this->bool_value($value,false)?'Ja':'Nej';
        return null;
    }

    private function apply_dynamic_binding_output(array &$section,$property,$value) {
        if($property==='MediaId'){$section[$property]=absint($value);return;}
        $text=is_scalar($value)?(string)$value:'';
        if(in_array($property,['Button1Url','Button2Url'],true))$section[$property]=esc_url_raw($text);
        elseif($property==='Content')$section[$property]=wp_kses_post($text);
        else $section[$property]=sanitize_text_field($text);
    }

    private function apply_dynamic_binding_fallback(array &$section,$property,array $option) {
        $mode=(string)($option['FallbackMode']??'Static');if($mode==='Static')return;
        if($mode==='Empty'){$this->apply_dynamic_binding_output($section,$property,$property==='MediaId'?0:'');return;}
        $fallback=(string)($option['Fallback']??'');$this->apply_dynamic_binding_output($section,$property,$fallback);
    }

    private function dynamic_data_context_catalog_for_editor() {
'''
php=once(php,needle,helpers,'binding formatter helpers')

# Replace runtime binding function as one contiguous unit.
start=php.index('    private function apply_dynamic_bindings_to_section(array $section, array $context) {')
end=php.index('    /* ================================================================\n       CONDITIONAL VISIBILITY ENGINE',start)
new_apply=r'''    private function apply_dynamic_bindings_to_section(array $section, array $context) {
        $bindings=$this->normalize_dynamic_bindings($section['Bindings']??[]);if(!$bindings)return$section;
        $options=$this->normalize_dynamic_binding_options($section['BindingOptions']??[]);$property_types=$this->dynamic_binding_property_types();$fields=isset($context['Fields'])&&is_array($context['Fields'])?$context['Fields']:[];$values=isset($context['Values'])&&is_array($context['Values'])?$context['Values']:[];
        foreach($bindings as $property=>$field_key){
            $option=$this->dynamic_binding_option_for_property($options,$property);$resolved=false;
            if(isset($fields[$field_key])&&array_key_exists($field_key,$values)){
                $field_type=(string)($fields[$field_key]['Type']??'');
                if(in_array($field_type,$property_types[$property]??[],true)){
                    $value=$values[$field_key];$empty=$this->dynamic_binding_value_is_empty($value,$field_type);
                    if(!$empty||empty($option['FallbackWhenEmpty'])){
                        if($property==='MediaId'){$formatted=absint($value);$resolved=true;}
                        else{$formatted=$this->dynamic_binding_format_value($value,$field_type,(string)$option['Formatter']);if($formatted!==null){if(!in_array($property,['Button1Url','Button2Url'],true))$formatted=(string)$option['Prefix'].$formatted.(string)$option['Suffix'];$resolved=true;}}
                        if($resolved)$this->apply_dynamic_binding_output($section,$property,$formatted);
                    }
                }
            }
            if(!$resolved)$this->apply_dynamic_binding_fallback($section,$property,$option);
        }
        return$section;
    }



'''
php=php[:start]+new_apply+php[end:]

# Extend admin binding UI. Binding options names are separate from the legacy Bindings map.
old="""                        foreach ($binding_rows as $binding_property => $binding_config) :
                            $binding_value = (string) (($section['Bindings'][$binding_property] ?? ''));
                        ?>
                            <div class=\"h18-field h18-dynamic-binding-row\" data-types=\"<?php echo esc_attr($binding_config[1]); ?>\">
                                <label><strong><?php echo esc_html($binding_config[0]); ?></strong></label>
                                <select class=\"h18-dynamic-binding-select\" name=\"<?php echo esc_attr($prefix); ?>[Bindings][<?php echo esc_attr($binding_property); ?>]\" data-binding-property=\"<?php echo esc_attr($binding_property); ?>\" data-allowed-types=\"<?php echo esc_attr($binding_config[2]); ?>\" data-binding-value=\"<?php echo esc_attr($binding_value); ?>\"><option value=\"\">Statisk værdi</option></select>
                            </div>
                        <?php endforeach; ?>
"""
new="""                        foreach ($binding_rows as $binding_property => $binding_config) :
                            $binding_value = (string) (($section['Bindings'][$binding_property] ?? ''));
                            $binding_option = $this->dynamic_binding_option_for_property((array)($section['BindingOptions'] ?? []), $binding_property);
                        ?>
                            <div class=\"h18-field h18-dynamic-binding-row\" data-types=\"<?php echo esc_attr($binding_config[1]); ?>\">
                                <label><strong><?php echo esc_html($binding_config[0]); ?></strong></label>
                                <select class=\"h18-dynamic-binding-select\" name=\"<?php echo esc_attr($prefix); ?>[Bindings][<?php echo esc_attr($binding_property); ?>]\" data-binding-property=\"<?php echo esc_attr($binding_property); ?>\" data-allowed-types=\"<?php echo esc_attr($binding_config[2]); ?>\" data-binding-value=\"<?php echo esc_attr($binding_value); ?>\"><option value=\"\">Statisk værdi</option></select>
                                <div class=\"h18-binding-options\" data-binding-property=\"<?php echo esc_attr($binding_property); ?>\">
                                    <select class=\"h18-binding-formatter\" name=\"<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Formatter]\"><?php foreach($this->dynamic_binding_formatters() as $formatter_key=>$formatter_label):?><option value=\"<?php echo esc_attr($formatter_key); ?>\" <?php selected($binding_option['Formatter'],$formatter_key); ?>><?php echo esc_html($formatter_label); ?></option><?php endforeach;?></select>
                                    <select class=\"h18-binding-fallback-mode\" name=\"<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][FallbackMode]\"><option value=\"Static\" <?php selected($binding_option['FallbackMode'],'Static'); ?>>Fallback: statisk elementværdi</option><option value=\"Custom\" <?php selected($binding_option['FallbackMode'],'Custom'); ?>>Fallback: egen værdi</option><option value=\"Empty\" <?php selected($binding_option['FallbackMode'],'Empty'); ?>>Fallback: tom</option></select>
                                    <input class=\"h18-binding-fallback\" type=\"text\" maxlength=\"2000\" name=\"<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Fallback]\" value=\"<?php echo esc_attr($binding_option['Fallback']); ?>\" placeholder=\"Egen fallback\" />
                                    <label class=\"h18-binding-empty-toggle\"><input class=\"h18-binding-fallback-empty\" type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][FallbackWhenEmpty]\" value=\"1\" <?php checked(!empty($binding_option['FallbackWhenEmpty'])); ?> /> Brug fallback når feltet er tomt</label>
                                    <input class=\"h18-binding-prefix\" type=\"text\" maxlength=\"100\" name=\"<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Prefix]\" value=\"<?php echo esc_attr($binding_option['Prefix']); ?>\" placeholder=\"Prefix\" />
                                    <input class=\"h18-binding-suffix\" type=\"text\" maxlength=\"100\" name=\"<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Suffix]\" value=\"<?php echo esc_attr($binding_option['Suffix']); ?>\" placeholder=\"Suffix\" />
                                </div>
                            </div>
                        <?php endforeach; ?>
"""
php=once(php,old,new,'binding options admin UI')

# JS preset serialization/restoration for BindingOptions.
js=once(js,"""        const cards = {};
        const bindings = {};
        pageSectionControls($row, '[name]').each(function () {
""","""        const cards = {};
        const bindings = {};
        const bindingOptions = {};
        pageSectionControls($row, '[name]').each(function () {
""",'preset binding options init')
js=once(js,"""            let match = name.match(/^sections\\[[^\\]]+\\]\\[Bindings\\]\\[([^\\]]+)\\]$/);
            const value = $field.is(':checkbox') ? $field.is(':checked') : $field.val();
            if (match) {
                if (value) { bindings[String(match[1])] = String(value); }
                return;
            }
            match = name.match(/^sections\\[[^\\]]+\\]\\[Cards\\]\\[([^\\]]+)\\]\\[([^\\]]+)\\]$/);
""","""            let match = name.match(/^sections\\[[^\\]]+\\]\\[Bindings\\]\\[([^\\]]+)\\]$/);
            const value = $field.is(':checkbox') ? $field.is(':checked') : $field.val();
            if (match) {
                if (value) { bindings[String(match[1])] = String(value); }
                return;
            }
            match = name.match(/^sections\\[[^\\]]+\\]\\[BindingOptions\\]\\[([^\\]]+)\\]\\[([^\\]]+)\\]$/);
            if (match) {
                const property=String(match[1]), optionKey=String(match[2]); bindingOptions[property]=bindingOptions[property]||{}; bindingOptions[property][optionKey]=value; return;
            }
            match = name.match(/^sections\\[[^\\]]+\\]\\[Cards\\]\\[([^\\]]+)\\]\\[([^\\]]+)\\]$/);
""",'preset binding options collect')
js=once(js,"""        data.Cards = Object.keys(cards).sort(function (a, b) { return Number(a) - Number(b); }).map(function (index) { return cards[index]; });
        data.Bindings = bindings;
        return data;
""","""        data.Cards = Object.keys(cards).sort(function (a, b) { return Number(a) - Number(b); }).map(function (index) { return cards[index]; });
        data.Bindings = bindings;
        data.BindingOptions = bindingOptions;
        return data;
""",'preset binding options output')
js=once(js,"""            if (['Type', 'Cards', 'Bindings', 'Key', 'Order', 'Remove', 'LayoutParentKey'].includes(fieldName)) {
""","""            if (['Type', 'Cards', 'Bindings', 'BindingOptions', 'Key', 'Order', 'Remove', 'LayoutParentKey'].includes(fieldName)) {
""",'preset skip binding options')
js=once(js,"""        if (presetData.Bindings && typeof presetData.Bindings === 'object') {
            Object.keys(presetData.Bindings).forEach(function (property) {
                pageSectionControls($row, '.h18-dynamic-binding-select[data-binding-property=\"' + property + '\"]').attr('data-binding-value', String(presetData.Bindings[property] || ''));
            });
        }
""","""        if (presetData.Bindings && typeof presetData.Bindings === 'object') {
            Object.keys(presetData.Bindings).forEach(function (property) {
                pageSectionControls($row, '.h18-dynamic-binding-select[data-binding-property=\"' + property + '\"]').attr('data-binding-value', String(presetData.Bindings[property] || ''));
            });
        }
        if (presetData.BindingOptions && typeof presetData.BindingOptions === 'object') {
            Object.keys(presetData.BindingOptions).forEach(function(property){const option=presetData.BindingOptions[property]||{};const $box=pageSectionControls($row,'.h18-binding-options[data-binding-property=\"'+property+'\"]');Object.keys(option).forEach(function(key){const $control=$box.find('[name$=\"['+key+']\"]');if($control.is(':checkbox'))$control.prop('checked',Boolean(option[key]));else $control.val(option[key]==null?'':String(option[key]));});});
        }
""",'preset restore binding options')

# JS formatter/fallback preview helpers and enhanced dynamicPreviewBinding.
preview_helpers=r'''

    /* v0.5.30 – UD-059 Binding formatters + fallback */
    function bindingOptionsV0530($row, property) {
        const $box=pageSectionControls($row,'.h18-binding-options[data-binding-property="'+property+'"]').first();
        return {Formatter:String($box.find('.h18-binding-formatter').val()||'Auto'),FallbackMode:String($box.find('.h18-binding-fallback-mode').val()||'Static'),Fallback:String($box.find('.h18-binding-fallback').val()||''),FallbackWhenEmpty:$box.find('.h18-binding-fallback-empty').is(':checked'),Prefix:String($box.find('.h18-binding-prefix').val()||''),Suffix:String($box.find('.h18-binding-suffix').val()||'')};
    }
    function bindingPreviewEmptyV0530(value, fieldType){return value===null||value===undefined||value===''||(Array.isArray(value)&&!value.length)||(fieldType==='media'&&(parseInt(value,10)||0)<=0);}
    function bindingPreviewFormatV0530(value, fieldType, formatter){formatter=String(formatter||'Auto');if(formatter==='Auto'||formatter==='Text'){if(typeof value==='boolean')return value?'Ja':'Nej';return (value==null||typeof value==='object')?null:String(value);}if(formatter==='Upper'||formatter==='Lower'){if(value==null||typeof value==='object')return null;const text=String(value);return formatter==='Upper'?text.toLocaleUpperCase('da-DK'):text.toLocaleLowerCase('da-DK');}if(['Number0','Number1','Number2'].includes(formatter)){const number=Number(value);if(!Number.isFinite(number))return null;const decimals=parseInt(formatter.slice(-1),10)||0;return new Intl.NumberFormat('da-DK',{minimumFractionDigits:decimals,maximumFractionDigits:decimals}).format(number);}if(['DateShort','DateIso','DateLong'].includes(formatter)){const raw=String(value||'');if(!/^\d{4}-\d{2}-\d{2}$/.test(raw))return null;const parts=raw.split('-').map(Number),date=new Date(Date.UTC(parts[0],parts[1]-1,parts[2]));if(formatter==='DateIso')return raw;if(formatter==='DateShort')return String(parts[2]).padStart(2,'0')+'.'+String(parts[1]).padStart(2,'0')+'.'+parts[0];return new Intl.DateTimeFormat('da-DK',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(date);}if(formatter==='BoolYesNo')return (value===true||value===1||['1','true','yes','ja','on'].includes(String(value).toLowerCase()))?'Ja':'Nej';return null;}
    function bindingPreviewFallbackV0530($row,property,option){if(option.FallbackMode==='Static')return{bound:false};if(option.FallbackMode==='Empty')return{bound:true,value:property==='MediaId'?0:'',mediaUrl:''};return{bound:true,value:property==='MediaId'?(parseInt(option.Fallback,10)||0):option.Fallback,mediaUrl:''};}
'''
js=once(js,"""    function dynamicPreviewBindingV0524($row, property) {
""",preview_helpers+"""
    function dynamicPreviewBindingV0524($row, property) {
""",'preview formatter helpers')
start=js.index('    function dynamicPreviewBindingV0524($row, property) {')
end=js.index('    $pageDataContextTypeV0524.on',start)
new_preview=r'''    function dynamicPreviewBindingV0524($row, property) {
        const $select=pageSectionControls($row,'.h18-dynamic-binding-select[data-binding-property="'+property+'"]').first();const fieldKey=String($select.val()||$select.attr('data-binding-value')||'');if(!$select.length||!fieldKey)return{bound:false};
        const option=bindingOptionsV0530($row,property),definition=dynamicContextDefinitionV0524(),entry=dynamicContextEntryV0524();if(!definition||!entry)return bindingPreviewFallbackV0530($row,property,option);
        const field=(Array.isArray(definition.Fields)?definition.Fields:[]).find(function(item){return String(item.Key)===fieldKey;});const values=entry.Values&&typeof entry.Values==='object'?entry.Values:{};if(!field||!Object.prototype.hasOwnProperty.call(values,fieldKey))return bindingPreviewFallbackV0530($row,property,option);
        const raw=values[fieldKey],fieldType=String(field.Type||'');if(bindingPreviewEmptyV0530(raw,fieldType)&&option.FallbackWhenEmpty)return bindingPreviewFallbackV0530($row,property,option);
        if(property==='MediaId'){const mediaUrls=entry.MediaUrls&&typeof entry.MediaUrls==='object'?entry.MediaUrls:{};return{bound:true,value:parseInt(raw,10)||0,mediaUrl:String(mediaUrls[fieldKey]||'')};}
        let value=bindingPreviewFormatV0530(raw,fieldType,option.Formatter);if(value===null)return bindingPreviewFallbackV0530($row,property,option);if(!['Button1Url','Button2Url'].includes(property))value=option.Prefix+value+option.Suffix;return{bound:true,value:value,mediaUrl:''};
    }
'''
js=js[:start]+new_preview+js[end:]

# Binding options visibility / canvas refresh.
js += r'''

    $(document).on('change input','.h18-binding-formatter,.h18-binding-fallback-mode,.h18-binding-fallback,.h18-binding-fallback-empty,.h18-binding-prefix,.h18-binding-suffix',function(){const $row=pageSectionForElement($(this));const $box=$(this).closest('.h18-binding-options');$box.find('.h18-binding-fallback').toggle(String($box.find('.h18-binding-fallback-mode').val()||'Static')==='Custom');if($row.length)renderCanvasPreview($row);scheduleEditorHistoryCapture(250);});
    function refreshBindingOptionUiV0530($scope){($scope&&$scope.length?$scope:$(document)).find('.h18-binding-options').each(function(){const $box=$(this),property=String($box.attr('data-binding-property')||'');$box.toggleClass('is-url-or-media',['Button1Url','Button2Url','MediaId'].includes(property));$box.find('.h18-binding-fallback').toggle(String($box.find('.h18-binding-fallback-mode').val()||'Static')==='Custom');});}
    refreshBindingOptionUiV0530($('.h18-pages-admin'));
'''

css += """

/* v0.5.30 – UD-059 Binding formatters + fallback */
.h18-binding-options{display:grid;grid-template-columns:minmax(150px,1fr) minmax(190px,1.2fr) minmax(130px,1fr);gap:7px;margin-top:7px;padding:9px;border:1px solid #dcdcde;border-radius:6px;background:#f6f7f7}.h18-binding-options .h18-binding-empty-toggle{grid-column:1/-1;font-size:12px}.h18-binding-options.is-url-or-media .h18-binding-prefix,.h18-binding-options.is-url-or-media .h18-binding-suffix{display:none}@media(max-width:900px){.h18-binding-options{grid-template-columns:1fr}}
"""

readme=once(readme,'Version: 0.5.29','Version: 0.5.30','readme version')
readme += """

## v0.5.30 – E5 UD-059 Field formatters + fallback
- Dynamic bindings får et separat, bagudkompatibelt `BindingOptions`-lag; den eksisterende `Bindings[property]=field` model ændres ikke.
- Formatters: Auto/Text, upper/lower, tal med 0/1/2 decimaler, kort/ISO/lang dato samt Ja/Nej.
- Fallback modes: behold statisk elementværdi, custom fallback eller tom værdi.
- `FallbackWhenEmpty` er opt-in og default false, så eksisterende bindinger beholder tidligere empty-value adfærd.
- Prefix/suffix kan anvendes på tekstoutput; URL/media springer prefix/suffix over og saniteres fortsat typespecifikt.
- Runtime og canvas-preview anvender samme formatter/fallback-model.
- BindingOptions følger med i Patterns, linked component definitions og Page Templates.
- Page-editor schema løftes bagudkompatibelt til 1.22.
"""

php_path.write_text(php);js_path.write_text(js);css_path.write_text(css);readme_path.write_text(readme)
print('v0.5.30 UD-059 binding formatters/fallback patch applied')
