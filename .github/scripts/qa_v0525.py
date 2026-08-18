from pathlib import Path
php=Path('hangar18-manager.php').read_text(); js=Path('assets/admin.js').read_text(); css=Path('assets/admin.css').read_text(); readme=Path('readme.txt').read_text()
checks={
'version':'Version: 0.5.25' in php and "const VERSION = '0.5.25';" in php,
'schema unchanged':"'Version'        => '1.19'" in php and "'Version'        => '1.20'" not in php,
'shortcode registration':"add_shortcode('hangar18_data_query'" in php,
'operator map':'custom_data_query_operator_map' in php,
'normalizer':'normalize_custom_data_query' in php,
'core':'run_custom_data_query' in php,
'publish only':"'post_status' => 'publish'" in php,
'limit':"$this->clamp_int($raw['Limit']" in php,
'meta type':"'_h18_data_type'" in php and "'_h18_field_' . $filter['Field']" in php,
'no raw sql':'$wpdb->' not in php[php.index('private function custom_data_query_operator_map'):php.index('public function render_data()',php.index('private function custom_data_query_operator_map'))],
'admin preview':'query_preview' in php and '$this->run_custom_data_query($qb_raw, $qb_normalized)' in php,
'frontend same core':'public function shortcode_data_query' in php and '$this->run_custom_data_query($atts, $normalized)' in php,
'escaped output':"esc_html((string) $post->post_title)" in php,
'JS':'/* v0.5.25 – Query Builder v1 */' in js,
'CSS':'/* v0.5.25 – Query Builder v1 */' in css,
'readme':'UD-055' in readme and 'Version: 0.5.25' in readme,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit('Failed v0.5.25 assertions: '+repr(failed))

# Operators are strict per type.
s=php.index('private function custom_data_query_operator_map');e=php.index('private function normalize_custom_data_query',s);op=php[s:e]
expected={
"'text'":"['eq'=>'Er lig med','neq'=>'Er ikke lig med','contains'=>'Indeholder']",
"'number'":"['eq'=>'=','neq'=>'≠','gt'=>'>','gte'=>'≥','lt'=>'<','lte'=>'≤']",
"'bool'":"['eq'=>'Er lig med']",
"'date'":"['eq'=>'På dato','before'=>'Før','after'=>'Efter']",
"'media'":"['eq'=>'Er lig med','neq'=>'Er ikke lig med']",
}
for t,token in expected.items():
    if token not in op: raise SystemExit('Operator map mismatch for '+t)

# Filter field must exist in schema before meta key construction.
s=php.index('private function normalize_custom_data_query');e=php.index('private function custom_data_query_compare',s);norm=php[s:e]
if '!isset($field_map[$field_key])' not in norm: raise SystemExit('Unknown filter fields are not rejected')
if '!isset($operators[$operator])' not in norm: raise SystemExit('Operator is not checked against field type')
if "DateTime::createFromFormat('!Y-m-d'" not in norm or '!is_numeric($value_raw)' not in norm: raise SystemExit('Type-specific query values are not validated')
if "strpos($sort_raw, 'field:') === 0" not in norm or '!isset($field_map[$sort_field])' not in norm: raise SystemExit('Sort field is not schema-validated')

# Query core must use WordPress query args, publish-only, bounded rows, and sanitized meta keys from normalized schema.
s=php.index('private function run_custom_data_query');e=php.index('private function custom_data_query_shortcode_from_normalized',s);core=php[s:e]
for token in ["'post_type' => self::DATA_ENTRY_POST_TYPE","'post_status' => 'publish'","'posts_per_page' => (int) $query['Limit']","'no_found_rows' => true",'return get_posts($args);']:
    if token not in core: raise SystemExit('Query core missing: '+token)
if '$wpdb' in core or 'prepare(' in core: raise SystemExit('Query core contains raw SQL path')
if "'_h18_field_' . $filter['Field']" not in core: raise SystemExit('Filter meta key does not use normalized field')

# Meta compare type must be numeric/date where appropriate.
if "['number','bool','media']" not in core or "$meta_type = 'DATE'" not in core: raise SystemExit('Typed meta comparison missing')

# Frontend must not disclose errors to anonymous users and must escape title output.
s=php.index('public function shortcode_data_query');e=php.index('public function render_data()',s);short=php[s:e]
if "current_user_can('edit_pages') ?" not in short: raise SystemExit('Anonymous query errors may leak schema details')
if "esc_html((string) $post->post_title)" not in short: raise SystemExit('Frontend query title is not escaped')

# Admin and frontend both call same core exactly; no second query implementation.
if php.count('run_custom_data_query(') < 3: raise SystemExit('Shared query core is not used by both consumers')

print('v0.5.25 UD-055 Query Builder security/architecture QA passed')
