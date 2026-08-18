from pathlib import Path
php=Path('hangar18-manager.php').read_text();js=Path('assets/admin.js').read_text();css=Path('assets/admin.css').read_text();readme=Path('readme.txt').read_text()
checks={
'version':'Version: 0.5.28' in php and "const VERSION = '0.5.28';" in php,
'page schema unchanged':"'Version'        => '1.21'" in php,
'field types':all(("'%s'"%x) in php for x in ['relation','group','repeater']),
'nested primitive allowlist':'private function custom_data_nested_field_types' in php and all(("'%s'"%x) in php for x in ['text','number','bool','date','media']),
'nested max 12':'array_slice(array_values($raw), 0, 12)' in php,
'relation target':'RelationTargetType' in php,
'repeater max':'RepeaterMaxItems' in php and "1, 20, 10" in php,
'schema version 2':"'SchemaVersion' => 2" in php,
'relation usage':'custom_data_relation_schema_usage' in php,
'target delete protection':'relationsfelt(er) stadig peger på den' in php,
'structured sanitizer':'sanitize_custom_data_nested_values' in php and 'custom_data_structured_has_content' in php,
'relation value validation':'custom_data_entry_for_type($relation_id, $target)' in php,
'group render':'h18-data-group' in php,
'repeater render':'h18-data-repeater-template' in php,
'schema config UI':'h18-data-relation-config' in php and 'h18-data-nested-config' in php and 'h18-data-repeater-config' in php,
'JS config':'refreshStructuredDataFieldRowV0528' in js,
'JS repeater':'h18-data-repeater-add' in js and 'h18-data-repeater-remove' in js,
'condition arrays empty':'is_array($value) && !$value' in php,
'CSS':'/* v0.5.28 – UD-054 Relation / Group / Repeater fields */' in css,
'readme':'UD-054' in readme and 'Version: 0.5.28' in readme,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit('Failed v0.5.28 assertions: '+repr(failed))

# Nested structural recursion is forbidden by allowlist: only five primitive nested types.
s=php.index('private function custom_data_nested_field_types');e=php.index('private function normalize_custom_data_nested_fields',s);nested_types=php[s:e]
for forbidden in ["'relation'","'group'","'repeater'"]:
    if forbidden in nested_types: raise SystemExit('Nested structural recursion allowed: '+forbidden)

# Schema normalization must persist target/nested/max settings but not accept more than 30 top-level fields.
s=php.index('private function normalize_custom_data_type');e=php.index('private function get_custom_data_types',s);norm=php[s:e]
for token in ["array_slice($raw['Fields'], 0, 30)",'RelationTargetType','NestedFields','RepeaterMaxItems']:
    if token not in norm: raise SystemExit('Structured schema normalization missing '+token)

# Relation target existence is verified in save handler after catalog is available.
s=php.index('public function handle_save_data_type');e=php.index('public function handle_delete_data_type',s);save=php[s:e]
if '$known_targets = $types' not in save or "!isset($known_targets[(string) ($field['RelationTargetType'] ?? '')])" not in save:
    raise SystemExit('Relation target datatype is not existence-validated')

# Delete safety: target datatype cannot be deleted while a relation schema points at it.
s=php.index('public function handle_delete_data_type');e=php.index('public function handle_save_data_entry',s);delete=php[s:e]
if 'custom_data_relation_schema_usage($key)' not in delete or 'if ($relation_usage)' not in delete:
    raise SystemExit('Relation target delete protection missing')

# Structured values are sanitized before scalar coercion; relation is target-type isolated.
s=php.index('private function sanitize_custom_data_value');e=php.index('private function custom_data_redirect',s);san=php[s:e]
for token in ["$type === 'relation'","$type === 'group'","$type === 'repeater'",'array_slice(array_values($source), 0, $limit)']:
    if token not in san: raise SystemExit('Structured sanitizer missing '+token)
if san.index("$type === 'relation'") > san.index('$value = is_scalar($value)'):
    raise SystemExit('Relation is scalar-coerced before validation')

# Query Builder v1 must reject structured sort and have no operators for relation/group/repeater until UD-056.
s=php.index('private function custom_data_query_operator_map');e=php.index('private function normalize_custom_data_query',s);ops=php[s:e]
for forbidden in ["'relation'","'group'","'repeater'"]:
    if forbidden in ops: raise SystemExit('Query Builder v1 unexpectedly exposes '+forbidden)
s=php.index('private function normalize_custom_data_query');e=php.index('private function custom_data_query_compare',s);qb=php[s:e]
if "['text','number','date','media']" not in qb:
    raise SystemExit('Structured fields are not rejected for Query Builder v1 sorting')

# Relation remains scalar query-ready meta; group/repeater may be serialized only in general values/meta storage.
if "update_post_meta($entry_id, $meta_key" not in php:
    raise SystemExit('Per-field query meta storage missing')

# Entry renderer must bound repeater UI by server schema max and use nested field sanitizer renderer.
s=php.index('private function render_custom_data_field_input');e=php.index('private function custom_data_query_operator_map',s);render=php[s:e]
for token in ['data-max-items','array_slice($items,0,$limit)','render_custom_data_nested_inputs']:
    if token not in render: raise SystemExit('Structured renderer missing '+token)

print('v0.5.28 UD-054 Relation / Group / Repeater security/architecture QA passed')
