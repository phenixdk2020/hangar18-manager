from pathlib import Path
php=Path('hangar18-manager.php').read_text(); js=Path('assets/admin.js').read_text(); css=Path('assets/admin.css').read_text(); readme=Path('readme.txt').read_text()
checks={
'version':'Version: 0.5.27' in php and "const VERSION = '0.5.27';" in php,
'schema 1.21':"'Version'        => '1.21'" in php,
'normalizer':'private function normalize_page_conditions' in php,
'max 8':'array_slice(array_values($raw), 0, 8)' in php,
'type allowlist':all(x in php for x in ["'data' => ['empty','not_empty','eq','neq','gt','gte','lt','lte']","'user' => ['logged_in','logged_out','role','capability']","'date' => ['before','after','between']"]),
'datetime WP timezone':'wp_timezone()' in php and 'DateTimeImmutable::createFromFormat' in php,
'evaluate single':'private function evaluate_page_condition' in php,
'evaluate group':'private function evaluate_page_conditions' in php,
'all any':"['All','Any']" in php and "$mode === 'Any'" in php,
'data eval':'page_condition_value_is_empty' in php and "$type === 'data'" in php,
'user eval':'is_user_logged_in()' in php and 'wp_get_current_user()' in php and 'current_user_can($value)' in php,
'date eval':"$type === 'date'" in php and "$operator === 'between'" in php,
'runtime condition':'!$this->evaluate_page_conditions($section, $this->active_dynamic_data_context)' in php,
'condition before binding':php.index('!$this->evaluate_page_conditions($section, $this->active_dynamic_data_context)') < php.index('$section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context)', php.index('private function render_page_editor_section_front')),
'defaults':"'ConditionMode'         => 'All'" in php and "'Conditions'            => []" in php,
'json input':'ConditionsJson' in php,
'admin warning':'må ikke bruges som adgangskontrol eller sikkerhedsgrænse' in php,
'preview environment':"'conditionUser'" in php and "'conditionNow'" in php,
'JS evaluator':'evaluateOneConditionV0527' in js and 'evaluateConditionPreviewV0527' in js,
'JS all any':"mode==='Any'?results.some(Boolean):results.every(Boolean)" in js,
'JS current context':'conditionDataContextV0527' in js and 'dynamicContextEntryV0524()' in js,
'canvas hook':'renderCanvasDirectControls($row, $preview, layout, colors);\n        evaluateConditionPreviewV0527($row);' in js,
'preview badge':'Skjult af conditions' in js,
'CSS':'/* v0.5.27 – UD-058 Conditional Visibility */' in css,
'readme':'UD-058' in readme and 'Version: 0.5.27' in readme,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit('Failed v0.5.27 assertions: '+repr(failed))

# Conditions are visibility only: evaluator must not mutate auth/session/data or query storage.
s=php.index('private function normalize_page_conditions'); e=php.index('private function default_page_section',s); engine=php[s:e]
for forbidden in ['$wpdb','wp_set_current_user','wp_set_auth_cookie','update_option(','update_post_meta(','wp_delete_post(']:
    if forbidden in engine: raise SystemExit('Condition engine contains forbidden side effect: '+forbidden)

# Strict data/user/date condition type/operator validation.
norm_s=php.index('private function normalize_page_conditions'); norm_e=php.index('private function page_condition_datetime_timestamp',norm_s); norm=php[norm_s:norm_e]
for token in ["!isset($allowed[$type])","!in_array($operator, $allowed[$type], true)","$type === 'data' && $field === ''","['role','capability']"]:
    if token not in norm: raise SystemExit('Condition normalization missing '+token)

# Date engine must use WordPress site timezone and reject invalid parsed values.
date_s=php.index('private function page_condition_datetime_timestamp'); date_e=php.index('private function page_condition_value_is_empty',date_s); date=php[date_s:date_e]
if 'wp_timezone()' not in date or "['!Y-m-d\\TH:i', '!Y-m-d H:i', '!Y-m-d']" not in date:
    raise SystemExit('Date conditions are not site-timezone normalized')

# Runtime order is safety-critical: Active -> conditions -> bindings -> query/component renderer.
render_s=php.index('private function render_page_editor_section_front'); render_e=php.index('private function render_page_editor_front',render_s); render=php[render_s:render_e]
pos_active=render.index("empty($section['Active'])")
pos_condition=render.index('evaluate_page_conditions')
pos_binding=render.index('apply_dynamic_bindings_to_section')
if not (pos_active < pos_condition < pos_binding): raise SystemExit('Runtime condition/binding ordering is wrong')

# Query-list per-result context must be assigned before component tree render, making child conditions context-aware.
ql_s=php.index('private function render_page_editor_query_list'); ql_e=php.index('private function render_page_editor_section_front',ql_s); ql=php[ql_s:ql_e]
if ql.index('$this->active_dynamic_data_context = $context;') > ql.index('$this->render_page_editor_layout_tree($page_id, $component_sections)'):
    raise SystemExit('Query List context is assigned after component render')
if 'finally {' not in ql or '$this->active_dynamic_data_context = $previous_context;' not in ql:
    raise SystemExit('Query List no longer restores context')

# Editor must never hide/remove the actual editable row; it only applies preview class/badge.
if ".remove()" in js[js.index('function evaluateConditionPreviewV0527'):js.index("$(document).on('click','.h18-condition-add'",js.index('function evaluateConditionPreviewV0527'))]:
    raise SystemExit('Condition preview removes editor DOM')

# ConditionsJson is a named section field and sectionPresetData should not exclude it, preserving Patterns/Components/Templates.
preset_s=js.index('function sectionPresetData'); preset_e=js.index('function setSectionPresetField',preset_s); preset=js[preset_s:preset_e]
if 'ConditionsJson' in preset and 'includes(fieldName)' in preset:
    raise SystemExit('ConditionsJson appears to be excluded from section serialization')

# No eval/new Function for condition expressions: conditions are structured data only.
condition_js=js[js.index('/* v0.5.27 – UD-058 Conditional Visibility */'):]
if 'eval(' in condition_js or 'new Function' in condition_js:
    raise SystemExit('Condition editor uses executable expressions')

print('v0.5.27 UD-058 Conditional Visibility security/architecture QA passed')
