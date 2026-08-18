from pathlib import Path

php=Path('hangar18-manager.php').read_text()
js=Path('assets/admin.js').read_text()
css=Path('assets/admin.css').read_text()
readme=Path('readme.txt').read_text()

checks={
    'version': 'Version: 0.5.24' in php and "const VERSION = '0.5.24';" in php,
    'schema 1.19': "'Version'        => '1.19'" in php and "'1.18'" not in php,
    'runtime property': 'private $active_dynamic_data_context = null;' in php,
    'binding allowlist': 'private function dynamic_binding_property_types()' in php,
    'binding normalize': 'private function normalize_dynamic_bindings($raw)' in php,
    'catalog': 'dynamic_data_context_catalog_for_editor' in php and 'posts_per_page' in php,
    'context resolve': 'resolve_dynamic_data_context' in php and 'custom_data_entry_for_type($entry_id, $type_key)' in php,
    'static fallback architecture': 'apply_dynamic_bindings_to_section' in php,
    'media sanitizer': "$section[$property] = absint($value);" in php,
    'url sanitizer': "$section[$property] = esc_url_raw($text);" in php,
    'content sanitizer': "$section[$property] = wp_kses_post($text);" in php,
    'page context fields': "'DataContextType'" in php and "'DataContextEntryId'" in php,
    'section bindings': "'Bindings'" in php,
    'runtime apply': '$section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context);' in php,
    'runtime context set': '$this->active_dynamic_data_context = $this->resolve_dynamic_data_context(' in php,
    'admin catalog JSON': 'h18-dynamic-data-catalog' in php,
    'admin page context': 'h18-page-data-context-type' in php and 'h18-page-data-context-entry' in php,
    'binding controls': 'h18-dynamic-binding-select' in php,
    'JS catalog': 'pageDynamicDataCatalogV0524' in js,
    'JS preview': 'dynamicPreviewBindingV0524' in js,
    'JS media preview': "fieldName === 'MediaUrl'" in js and 'mediaBinding.mediaUrl' in js,
    'nested serialization': 'const bindings = {};' in js and 'data.Bindings = bindings;' in js,
    'preset restore': 'presetData.Bindings' in js,
    'CSS': '/* v0.5.24 – Dynamic data context + bindings */' in css,
    'readme': 'UD-053' in readme and 'Version: 0.5.24' in readme and '1.19' in readme,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise SystemExit('Failed v0.5.24 assertions: '+repr(failed))

# Only explicitly approved element properties may bind dynamically.
start=php.index('private function dynamic_binding_property_types()')
end=php.index('private function normalize_dynamic_bindings',start)
allow=php[start:end]
expected=['Title','Content','MediaId','Button1Label','Button1Url','Button2Label','Button2Url']
for prop in expected:
    if "'"+prop+"'" not in allow: raise SystemExit('Missing binding property '+prop)
for forbidden in ['LegacyHtml','RecipientEmail','CustomBackgroundColor','ContentVersion','AdvancedContentAuthorized','ComponentId','Type']:
    if "'"+forbidden+"'" in allow: raise SystemExit('Unsafe binding property allowed: '+forbidden)

# URL properties must only accept text fields; MediaId only media.
if "'MediaId' => ['media']" not in allow:
    raise SystemExit('MediaId binding accepts non-media values')
for url_prop in ['Button1Url','Button2Url']:
    if f"'{url_prop}' => ['text']" not in allow:
        raise SystemExit(url_prop+' binding accepts non-text values')

# Normalizer must discard unknown properties and empty keys.
start=php.index('private function normalize_dynamic_bindings')
end=php.index('private function dynamic_data_context_catalog_for_editor',start)
normalize=php[start:end]
if '!isset($allowed[$property])' not in normalize or "$field_key === ''" not in normalize:
    raise SystemExit('Binding normalizer is not allowlist-based')

# Server runtime must verify field presence AND field type before mutation.
start=php.index('private function apply_dynamic_bindings_to_section')
end=php.index('PAGE EDITOR AND FUNCTION MODULES',start)
apply=php[start:end]
required_runtime=[
    '!isset($fields[$field_key])',
    '!array_key_exists($field_key, $values)',
    '!in_array($field_type, $property_types[$property] ?? [], true)',
    "if ($property === 'MediaId')",
    "in_array($property, ['Button1Url','Button2Url'], true)",
]
for token in required_runtime:
    if token not in apply: raise SystemExit('Runtime binding safety missing: '+token)

# Static values are fallback: method starts from supplied section and skips invalid/missing bindings.
if 'return $section;' not in apply or apply.count('continue;') < 3:
    raise SystemExit('Static fallback behavior is not explicit')

# Data context must be both schema-valid and entry/type-valid before persisting or rendering.
start=php.index('private function normalize_page_editor_data')
end=php.index('private function get_page_editor_store',start)
page_norm=php[start:end]
if 'resolve_dynamic_data_context($data_context_type, $data_context_entry_id)' not in page_norm:
    raise SystemExit('Page context not revalidated during normalization')
if "$data_context_type = '';" not in page_norm or '$data_context_entry_id = 0;' not in page_norm:
    raise SystemExit('Invalid page context is not cleared')

# Context resolver uses cross-type guarded entry lookup, never raw arbitrary post meta.
start=php.index('private function resolve_dynamic_data_context')
end=php.index('private function dynamic_binding_text_value',start)
resolver=php[start:end]
if 'custom_data_entry_for_type($entry_id, $type_key)' not in resolver:
    raise SystemExit('Context resolver bypasses datatype/entry isolation')
if 'custom_data_entry_values($entry_id, $types[$type_key])' not in resolver:
    raise SystemExit('Context resolver bypasses normalized values layer')

# Frontend current context must be set before section rendering and applied before component handling.
front_start=php.index('private function render_page_editor_front')
front_end=php.index('private function build_page_editor_core',front_start)
front=php[front_start:front_end]
if front.find('active_dynamic_data_context') < 0:
    raise SystemExit('Frontend page does not establish current context')
sec_start=php.index('private function render_page_editor_section_front')
sec_end=php.index('private function render_page_editor_layout_tree',sec_start)
sec=php[sec_start:sec_end]
if sec.find('apply_dynamic_bindings_to_section') < 0 or sec.find("if ($section['Type'] === 'component')") < 0:
    raise SystemExit('Section render binding/component order missing')
if sec.find('apply_dynamic_bindings_to_section') > sec.find("if ($section['Type'] === 'component')"):
    raise SystemExit('Bindings are applied too late for consistent render semantics')

# Binding metadata must serialize independently from static fields.
if "name.match(/^sections\\[[^\\]]+\\]\\[Bindings\\]" not in js:
    raise SystemExit('Inspector binding metadata is not serialized')
if "['Type', 'Cards', 'Bindings', 'Key'" not in js:
    raise SystemExit('Nested Bindings would be treated as a scalar preset field')

# Current context is page-level only; patterns/components/templates may carry binding expressions, not entry identity.
section_start=php.index('private function default_page_section')
section_end=php.index('private function default_page_card',section_start)
default_section=php[section_start:section_end]
for forbidden in ['DataContextType','DataContextEntryId']:
    if forbidden in default_section: raise SystemExit('Entry identity leaked into section model: '+forbidden)

print('v0.5.24 UD-053 dynamic binding security/architecture QA passed')
