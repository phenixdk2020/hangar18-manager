from pathlib import Path
p=Path('hangar18-manager.php').read_text();j=Path('assets/admin.js').read_text();c=Path('assets/admin.css').read_text();r=Path('readme.txt').read_text()
checks={'version':'Version: 0.5.30' in p and "const VERSION = '0.5.30';" in p,'schema':"'Version'        => '1.22'" in p,'default options':"'BindingOptions'        => []" in p,'normalizer':'normalize_dynamic_binding_options' in p,'formatters':'dynamic_binding_formatters' in p,'runtime formatter':'dynamic_binding_format_value' in p,'fallback':'apply_dynamic_binding_fallback' in p,'empty opt in':'FallbackWhenEmpty' in p,'prefix suffix':"['Prefix']" in p and "['Suffix']" in p,'sanitization':'apply_dynamic_binding_output' in p,'admin':'h18-binding-options' in p and 'h18-binding-formatter' in p,'preset serialize':'bindingOptions' in j and 'data.BindingOptions = bindingOptions' in j,'preset restore':'presetData.BindingOptions' in j,'preview':'bindingPreviewFormatV0530' in j and 'bindingPreviewFallbackV0530' in j,'CSS':'/* v0.5.30 – UD-059 Binding formatters + fallback */' in c,'readme':'UD-059' in r and 'Version: 0.5.30' in r}
bad=[k for k,v in checks.items() if not v]
if bad:raise SystemExit('Failed v0.5.30 assertions: '+repr(bad))
# Existing Bindings map remains field-key scalar and is not migrated to nested structure.
s=p.index('private function normalize_dynamic_bindings');e=p.index('private function dynamic_binding_formatters',s);legacy=p[s:e]
if "$bindings[$property] = $field_key;" not in legacy:raise SystemExit('Legacy Bindings map changed shape')
# Default options reproduce old behavior: static missing fallback, no fallback-on-empty, no prefix/suffix, Auto formatter.
s=p.index('private function dynamic_binding_option_for_property');e=p.index('private function dynamic_binding_value_is_empty',s);defaults=p[s:e]
for token in ["'Formatter'=>'Auto'","'FallbackMode'=>'Static'","'FallbackWhenEmpty'=>false","'Prefix'=>'','Suffix'=>''"]:
    if token not in defaults:raise SystemExit('Backward-compatible option default missing '+token)
# Formatter allowlist is fixed and cannot execute arbitrary functions/templates.
s=p.index('private function dynamic_binding_formatters');e=p.index('private function normalize_dynamic_binding_options',s);fm=p[s:e]
for token in ['Auto','Text','Upper','Lower','Number0','Number1','Number2','DateShort','DateIso','DateLong','BoolYesNo']:
    if token not in fm:raise SystemExit('Formatter missing '+token)
engine=p[p.index('private function normalize_dynamic_binding_options'):p.index('private function dynamic_data_context_catalog_for_editor')]
for forbidden in ['eval(','call_user_func(','preg_replace_callback(']:
    if forbidden in engine:raise SystemExit('Binding option engine contains executable/dynamic formatter path: '+forbidden)
# Empty values only invoke fallback when explicitly opted in.
s=p.index('private function apply_dynamic_bindings_to_section');e=p.index('CONDITIONAL VISIBILITY ENGINE',s);apply=p[s:e]
if "if(!$empty||empty($option['FallbackWhenEmpty']))" not in apply:raise SystemExit('Empty fallback is not opt-in')
if 'if(!$resolved)$this->apply_dynamic_binding_fallback' not in apply:raise SystemExit('Invalid/missing formatter path does not fall back')
# Output still has property-specific final sanitization.
s=p.index('private function apply_dynamic_binding_output');e=p.index('private function apply_dynamic_binding_fallback',s);out=p[s:e]
for token in ['absint($value)','esc_url_raw($text)','wp_kses_post($text)','sanitize_text_field($text)']:
    if token not in out:raise SystemExit('Binding output sanitizer missing '+token)
# URL/media don't get prefix/suffix on server or editor.
if "!in_array($property,['Button1Url','Button2Url'],true)" not in apply:raise SystemExit('URL prefix/suffix exclusion missing')
if "['Button1Url','Button2Url','MediaId'].includes(property)" not in j:raise SystemExit('Editor URL/media option UI restriction missing')
# Binding options are serialized through Patterns/components/templates.
s=j.index('function sectionPresetData');e=j.index('function setSectionPresetField',s);preset=j[s:e]
for token in ['BindingOptions','bindingOptions[property]','data.BindingOptions = bindingOptions']:
    if token not in preset:raise SystemExit('BindingOptions preset serialization missing '+token)
# Preview default and fallback behavior mirrors server model.
for token in ['Formatter:String','FallbackMode:String','FallbackWhenEmpty','bindingPreviewFormatV0530','bindingPreviewFallbackV0530']:
    if token not in j:raise SystemExit('Preview binding options missing '+token)
print('v0.5.30 UD-059 binding formatter/fallback security/architecture QA passed')
