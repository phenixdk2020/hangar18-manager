from pathlib import Path

php=Path('hangar18-manager.php').read_text()
js=Path('assets/admin.js').read_text()
css=Path('assets/admin.css').read_text()
readme=Path('readme.txt').read_text()

checks={
    'version':'Version: 0.5.23' in php and "const VERSION = '0.5.23';" in php,
    'page schema':php.count("'Version'        => '1.19'")==3,
    'stores':"CUSTOM_DATA_TYPES_OPTION    = 'hangar18_manager_custom_data_types_v1'" in php and "DATA_ENTRY_POST_TYPE        = 'h18_data_entry'" in php,
    'post type init':"add_action('init', [$this, 'register_dynamic_data_post_type'], 5);" in php,
    'private post type':"'public' => false" in php and "'show_ui' => false" in php and "'show_in_rest' => false" in php,
    'field types':all(x in php for x in ["'text' => 'Tekst'","'number' => 'Tal'","'bool' => 'Ja/nej'","'date' => 'Dato'","'media' => 'Medie / billede'"]),
    'schema normalize':'normalize_custom_data_type' in php,
    'schema key immutable':'Datatype-nøglen er permanent' in php,
    'field default':"'Default' => $default_value" in php and 'h18-data-field-default' in php,
    'field uniqueness':"Felt-nøglen '{$field_key}' findes mere end én gang." in php,
    'schema cap':"current_user_can('manage_options')" in php,
    'entry cap':'public function handle_save_data_entry()' in php and '$this->require_capability();' in php,
    'entry cross type':'custom_data_entry_for_type' in php and '_h18_data_type' in php,
    'query ready meta':"'_h18_field_' . sanitize_key" in php,
    'values map':"update_post_meta($entry_id, '_h18_data_values', $values);" in php,
    'number validation':"if (!is_numeric($value))" in php,
    'date validation':"DateTime::createFromFormat('!Y-m-d', $value)" in php,
    'media validation':"$attachment->post_type !== 'attachment'" in php,
    'data menu':"'hangar18-data', [$this, 'render_data']" in php,
    'schema UI':'h18-data-schema-fields' in php and 'h18-data-add-field' in js,
    'media UI':'h18-data-media-pick' in js and 'wp.media' in js,
    'binding metadata':all(x in php for x in ["'DataContextTypeKey'    => ''","'DataContextEntryId'    => 0","'DynamicBindings'       => []"]),
    'binding target map':'page_dynamic_binding_targets' in php,
    'binding resolver':'resolve_page_section_dynamic_bindings' in php,
    'binding usage':'custom_data_binding_usage' in php,
    'datatype binding guard':'Datatypen kan ikke slettes, fordi den bruges i' in php,
    'entry binding guard':'Data-entry kan ikke slettes, fordi den bruges i' in php,
    'schema breaking guard':'kan derfor ikke fjernes eller skifte type' in php,
    'context section signature':"render_page_editor_section_front($page_id, array $section, $layout_children = '', $data_context = null)" in php,
    'context tree signature':"render_page_editor_layout_tree($page_id, array $sections, $parent_key = '', $depth = 0, $data_context = null)" in php,
    'editor catalog':'h18-custom-data-catalog' in php and 'customDataCatalogV0523' in js,
    'binding UI':'h18-dynamic-binding-box' in php and 'refreshDynamicBindingsV0523' in js,
    'binding status':'h18-dynamic-status-chip' in css and 'h18-canvas-dynamic-badge' in js,
    'readme':'UD-051' in readme and 'UD-052' in readme and 'UD-053' in readme and 'page-editor schema løftes bagudkompatibelt til 1.19' in readme,
}
failed=[name for name,ok in checks.items() if not ok]
if failed: raise SystemExit('Failed v0.5.23 assertions: '+repr(failed))

# Capability and nonce gates.
for method in ['handle_save_data_type','handle_delete_data_type']:
    start=php.index('public function '+method+'()');end=php.find('\n    public function ',start+20);block=php[start:end if end!=-1 else len(php)]
    if "current_user_can('manage_options')" not in block or 'check_admin_referer' not in block: raise SystemExit(method+' lacks manage_options/nonce gate')
for method in ['handle_save_data_entry','handle_delete_data_entry']:
    start=php.index('public function '+method+'()');end=php.find('\n    public function ',start+20);block=php[start:end if end!=-1 else len(php)]
    if '$this->require_capability();' not in block or 'check_admin_referer' not in block: raise SystemExit(method+' lacks edit_pages/nonce gate')

# Persistence boundary: posted binding targets are fixed allowlist keys only.
start=php.index("$dynamic_bindings_raw = $raw['DynamicBindings']");end=php.index('$component_overrides_raw',start);block=php[start:end]
for marker in ['allowed_dynamic_targets','array_keys($this->page_dynamic_binding_targets())','in_array($target, $allowed_dynamic_targets, true)']:
    if marker not in block: raise SystemExit('Dynamic binding persistence allowlist incomplete: '+marker)

# Runtime: target and field types must match; dynamic values cannot execute code.
start=php.index('private function resolve_page_section_dynamic_bindings');end=php.index('private function custom_data_binding_usage',start);resolver=php[start:end]
for marker in ['page_dynamic_binding_targets','custom_data_field_map',"in_array((string)$field['Type'],$targets[$target_key]['Types'],true)",'esc_url_raw($value)',"get_post_type($id)!=='attachment'"]:
    if marker not in resolver: raise SystemExit('Dynamic binding runtime validation missing: '+marker)
for forbidden in ['do_shortcode','eval(','wp_kses_post($value)']:
    if forbidden in resolver: raise SystemExit('Dynamic entry value can execute rich/custom code: '+forbidden)
if "if($raw===''||$raw===null)continue;" not in resolver: raise SystemExit('Missing dynamic value does not retain static fallback')

# Delete guards must happen before mutation.
start=php.index('public function handle_delete_data_type()');end=php.index('public function handle_save_data_entry()',start);block=php[start:end]
if block.find('custom_data_binding_usage')<0 or block.find('unset($types[$key])')<0 or block.find('custom_data_binding_usage')>block.find('unset($types[$key])'): raise SystemExit('Datatype delete binding guard occurs too late')
start=php.index('public function handle_delete_data_entry()');end=php.index('private function render_data_schema_field_row',start);block=php[start:end]
if block.find('custom_data_binding_usage')<0 or block.find('wp_delete_post')<0 or block.find('custom_data_binding_usage')>block.find('wp_delete_post'): raise SystemExit('Entry delete binding guard occurs too late')

# Usage scanner covers saved pages and all reusable content stores.
start=php.index('private function custom_data_binding_usage');end=php.index('private function custom_data_types_for_editor',start);usage=php[start:end]
for marker in ['get_page_editor_store','get_page_components','get_page_presets','get_page_templates']:
    if marker not in usage: raise SystemExit('Binding usage scan misses '+marker)

# Context survives recursive layout and linked components, ready for Query/Repeater.
start=php.index('private function render_page_editor_layout_tree');end=php.index('private function render_page_editor_front',start);tree=php[start:end]
if tree.count('$data_context')<4: raise SystemExit('Nested layout does not forward data_context consistently')
component_start=php.index("if ($section['Type'] === 'component')");component_end=php.index("if ($section['Type'] === 'legacy')",component_start)
if '$data_context' not in php[component_start:component_end]: raise SystemExit('Linked component loses data_context')

# Generic engine remains domain-agnostic and query-ready.
engine_start=php.index('GENERIC DYNAMIC DATA ENGINE');engine_end=php.index('PAGE EDITOR AND FUNCTION MODULES',engine_start);engine=php[engine_start:engine_end]
for forbidden in ['VEHICLE_PARENT_SLUG','EVENT_PARENT_SLUG','GALLERY_PARENT_SLUG','vehicle_register','gallery_album']:
    if forbidden in engine: raise SystemExit('Generic data engine contains domain coupling: '+forbidden)
if "update_post_meta($entry_id, '_h18_data_values', $values);" not in engine or "update_post_meta($entry_id, $meta_key" not in engine: raise SystemExit('Entry persistence is not query-ready')

print('v0.5.23 UD-051/052/053 security and architecture QA passed')
