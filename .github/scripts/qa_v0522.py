from pathlib import Path

php=Path('hangar18-manager.php').read_text()
js=Path('assets/admin.js').read_text()
css=Path('assets/admin.css').read_text()
readme=Path('readme.txt').read_text()

checks={
    'version': 'Version: 0.5.22' in php and "const VERSION = '0.5.22';" in php,
    'schema': php.count("'Version'        => '1.18'")==3,
    'template store': "PAGE_TEMPLATES_OPTION       = 'hangar18_manager_page_templates_v1'" in php,
    'template nonce': "pageTemplateNonce" in php and 'h18_page_templates_v0522' in php,
    'variant field': "'ComponentVariant'" in php and '.h18-component-variant-select' in js,
    'variant normalize': 'normalize_page_component_variants' in php,
    'variant ajax': 'ajax_save_page_component_variant' in php and 'ajax_delete_page_component_variant' in php,
    'variant max': 'count($variants)>12' in php,
    'variant usage guard': 'get_page_component_variant_usage' in php and 'Varianten bruges stadig på' in php,
    'variant resolution order': 'array_replace($variant_values, $local_overrides)' in php,
    'preserve variants': "'Variants' => $existing ? ($existing['Variants'] ?? []) : []" in php,
    'pattern subtree normalize': 'normalize_page_pattern_sections' in php,
    'legacy pattern compatibility': "isset($entry['Section']) && is_array($entry['Section']) ? [$entry['Section']]" in php,
    'pattern new Sections': "'Sections'=>$sections" in php and 'applyPatternV0522' in js,
    'pattern fresh key map': 'const keyMap = {}' in js and 'newKey=String($row.find' in js,
    'pattern rejects shared content': "in_array($type, ['legacy','component'], true)" in php,
    'template normalize': 'normalize_page_template_sections' in php,
    'template store read': 'get_page_templates()' in php and 'get_page_templates_for_editor' in php,
    'template save': 'ajax_save_page_template' in php,
    'template create': 'ajax_create_page_from_template' in php,
    'template fresh keys': 'instantiate_page_template_sections' in php and "'sektion-'.substr(md5(wp_generate_uuid4()),0,12)" in php,
    'template draft': "'post_status'=>'draft'" in php,
    'template managed': "update_post_meta($post_id,'_h18_page_editor_managed','1')" in php,
    'template origin audit': "update_post_meta($post_id,'_h18_page_template_origin',$template_id)" in php,
    'template no component linkage': "Page Templates kan ikke indeholde legacy eller linked components" in php,
    'dynamic managed definitions': "'meta_key' => '_h18_page_editor_managed'" in php,
    'template UI': 'h18-page-templates-list' in php and 'renderPageTemplatesV0522' in js,
    'template create UI': 'h18-page-template-create' in js,
    'readme': 'page-editor schema løftes bagudkompatibelt til 1.18' in readme,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise SystemExit('Failed v0.5.22 assertions: '+repr(failed))

# Variants are only differences over already-exposed component inputs.
variant_start=php.index('private function normalize_page_component_variants')
variant_end=php.index('private function get_page_components()',variant_start)
variant_block=php[variant_start:variant_end]
if '$input_map' not in variant_block or '!isset($input_map[$input_id])' not in variant_block:
    raise SystemExit('Variant values are not restricted to exposed InputIds')
if 'sanitize_page_component_override' not in variant_block:
    raise SystemExit('Variant values bypass component override sanitizer')

# The render-time precedence must be Base -> Variant -> Local instance override.
resolve_start=php.index('private function resolve_page_component_instance_sections')
resolve_end=php.index('private function page_module_storage_key',resolve_start)
resolve_block=php[resolve_start:resolve_end]
sequence=[resolve_block.find("$sections = $component['Sections']"),resolve_block.find('$variant_values'),resolve_block.find('$local_overrides'),resolve_block.find('array_replace($variant_values, $local_overrides)')]
if any(x < 0 for x in sequence) or sequence != sorted(sequence):
    raise SystemExit('Component variant/local override precedence is wrong')

# Deleting a used variant must check usage before mutating definition.
del_start=php.index('public function ajax_delete_page_component_variant')
del_end=php.index('private function resolve_page_component_instance_sections',del_start)
del_block=php[del_start:del_end]
if del_block.find('get_page_component_variant_usage') < 0 or del_block.find('unset($components[$component_id]') < 0:
    raise SystemExit('Variant delete implementation incomplete')
if del_block.find('get_page_component_variant_usage') > del_block.find('unset($components[$component_id]'):
    raise SystemExit('Variant delete mutates before usage protection')

# Pattern storage must always detach shared component identity.
pattern_start=php.index('private function normalize_page_pattern_sections')
pattern_end=php.index('public function ajax_delete_page_preset',pattern_start)
pattern_block=php[pattern_start:pattern_end]
if "$section['ComponentId']='';" not in pattern_block or "$section['ComponentRevision']=0;" not in pattern_block or "$section['ComponentVariant']='';" not in pattern_block:
    raise SystemExit('Pattern does not explicitly detach linked component identity')

# Template creation must produce an independent page snapshot; origin meta is audit-only.
create_start=php.index('public function ajax_create_page_from_template')
create_end=php.index('private function page_component_allowed_input_fields',create_start)
create_block=php[create_start:create_end]
if "update_post_meta($post_id,'_h18_page_template_origin',$template_id)" not in create_block:
    raise SystemExit('Template origin audit metadata missing')
if 'save_page_editor_data($slug,$data)' not in create_block:
    raise SystemExit('Template-created page is not detached into normal page editor storage')
if 'instantiate_page_template_sections' not in create_block:
    raise SystemExit('Template page does not regenerate section keys')
# The template id may appear only in origin metadata/lookup; it must not be persisted as a page-editor linkage field.
for forbidden in ["'TemplateId'", "'PageTemplateId'", "'TemplateLink'"]:
    if forbidden in create_block:
        raise SystemExit('Template-created page contains shared template linkage field: '+forbidden)

# Deleting a Page Template must never delete or modify pages created from it.
tpl_del_start=php.index('public function ajax_delete_page_template')
tpl_del_end=php.index('private function instantiate_page_template_sections',tpl_del_start)
tpl_del=php[tpl_del_start:tpl_del_end]
if 'wp_delete_post' in tpl_del or 'wp_update_post' in tpl_del or 'save_page_editor_data' in tpl_del:
    raise SystemExit('Deleting Page Template mutates created pages')

# Dynamic page-definition expansion must only include explicitly managed pages.
defs_start=php.index('private function editable_page_definitions()')
defs_end=php.index('private function page_section_type_labels()',defs_start)
defs=php[defs_start:defs_end]
if "'_h18_page_editor_managed'" not in defs or "'meta_value' => '1'" not in defs:
    raise SystemExit('Dynamic page list is not restricted to Hangar18-managed pages')

print('v0.5.22 E4 completion/security QA passed')
