from pathlib import Path

php=Path('hangar18-manager.php').read_text()
js=Path('assets/admin.js').read_text()
css=Path('assets/admin.css').read_text()
readme=Path('readme.txt').read_text()

checks={
    'version': 'Version: 0.5.23' in php and "const VERSION = '0.5.23';" in php,
    'page schema unchanged': "'Version'        => '1.18'" in php and "'Version'        => '1.19'" not in php,
    'stores': "CUSTOM_DATA_TYPES_OPTION    = 'hangar18_manager_custom_data_types_v1'" in php and "DATA_ENTRY_POST_TYPE        = 'h18_data_entry'" in php,
    'post type init': "add_action('init', [$this, 'register_dynamic_data_post_type'], 5);" in php,
    'private post type': "'public' => false" in php and "'show_ui' => false" in php and "'capability_type' => 'page'" in php,
    'field types': all(x in php for x in ["'text' => 'Tekst'","'number' => 'Tal'","'bool' => 'Ja/nej'","'date' => 'Dato'","'media' => 'Medie / billede'"]),
    'schema normalize': 'normalize_custom_data_type' in php,
    'schema key immutable': 'Datatype-nøglen er permanent' in php,
    'field uniqueness': "Felt-nøglen '{$field_key}' findes mere end én gang." in php,
    'field max': 'array_slice($raw[\'Fields\'], 0, 30)' in php,
    'schema cap': "current_user_can('manage_options')" in php,
    'entry cap': 'public function handle_save_data_entry()' in php and '$this->require_capability();' in php,
    'entry cross type': 'custom_data_entry_for_type' in php and "_h18_data_type" in php,
    'query ready meta': "'_h18_field_' . sanitize_key" in php,
    'values map': "update_post_meta($entry_id, '_h18_data_values', $values);" in php,
    'number validation': "if (!is_numeric($value))" in php,
    'date validation': "DateTime::createFromFormat('!Y-m-d', $value)" in php,
    'media validation': "$attachment->post_type !== 'attachment'" in php,
    'type delete usage guard': 'custom_data_entry_count($key)' in php and 'Datatypen kan ikke slettes' in php,
    'data menu': "'hangar18-data', [$this, 'render_data']" in php,
    'schema UI': 'h18-data-schema-fields' in php and 'h18-data-add-field' in js,
    'media UI': 'h18-data-media-pick' in js and 'wp.media' in js,
    'css': '/* v0.5.23 – Generic Dynamic Data */' in css,
    'readme': 'UD-051' in readme and 'UD-052' in readme and 'Version: 0.5.23' in readme,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise SystemExit('Failed v0.5.23 assertions: '+repr(failed))

# Structural capability gates: schema mutation must be admin-only; entry mutation edit_pages.
for method in ['handle_save_data_type','handle_delete_data_type']:
    start=php.index('public function '+method+'()')
    end=php.find('\n    public function ',start+20)
    block=php[start:end if end!=-1 else len(php)]
    if "current_user_can('manage_options')" not in block or 'check_admin_referer' not in block:
        raise SystemExit(method+' lacks manage_options/nonce gate')
for method in ['handle_save_data_entry','handle_delete_data_entry']:
    start=php.index('public function '+method+'()')
    end=php.find('\n    public function ',start+20)
    block=php[start:end if end!=-1 else len(php)]
    if '$this->require_capability();' not in block or 'check_admin_referer' not in block:
        raise SystemExit(method+' lacks edit_pages/nonce gate')

# Type deletion must inspect usage before removing schema.
start=php.index('public function handle_delete_data_type()')
end=php.index('public function handle_save_data_entry()',start)
block=php[start:end]
usage_pos=block.find('custom_data_entry_count($key)')
unset_pos=block.find('unset($types[$key])')
if usage_pos<0 or unset_pos<0 or usage_pos>unset_pos:
    raise SystemExit('Datatype delete mutates schema before usage protection')

# Entry update must verify ID belongs to the selected datatype before wp_update_post.
start=php.index('public function handle_save_data_entry()')
end=php.index('public function handle_delete_data_entry()',start)
block=php[start:end]
verify_pos=block.find('custom_data_entry_for_type($entry_id, $type_key)')
update_pos=block.find('wp_update_post')
if verify_pos<0 or update_pos<0 or verify_pos>update_pos:
    raise SystemExit('Cross-type entry isolation check occurs too late')

# Generic engine must not special-case the current domains in storage/validation logic.
engine_start=php.index('GENERIC DYNAMIC DATA ENGINE')
engine_end=php.index('PAGE EDITOR AND FUNCTION MODULES',engine_start)
engine=php[engine_start:engine_end]
for forbidden in ['VEHICLE_PARENT_SLUG','EVENT_PARENT_SLUG','GALLERY_PARENT_SLUG','vehicle_register','gallery_album']:
    if forbidden in engine:
        raise SystemExit('Generic data engine contains domain-specific coupling: '+forbidden)

# Query builder foundation: values must be both normalized map and individual meta keys.
if "update_post_meta($entry_id, '_h18_data_values', $values);" not in engine or "update_post_meta($entry_id, $meta_key" not in engine:
    raise SystemExit('Entry persistence is not query-ready')

print('v0.5.23 UD-051/UD-052 security and architecture QA passed')
