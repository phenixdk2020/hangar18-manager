from pathlib import Path
p=Path('hangar18-manager.php').read_text();j=Path('assets/admin.js').read_text();c=Path('assets/admin.css').read_text();r=Path('readme.txt').read_text()
checks={'version':'Version: 0.5.29' in p and "const VERSION = '0.5.29';" in p,'taxonomy constant':'DATA_TAG_TAXONOMY' in p,'taxonomy register':'register_taxonomy(self::DATA_TAG_TAXONOMY' in p,'shortcode':"add_shortcode('hangar18_data_query_advanced'" in p,'normalizer':'normalize_advanced_data_query' in p,'runner':'run_advanced_data_query' in p,'groups':'GroupRelation' in p and "array_slice(array_values($groups_raw),0,4)" in p and "array_slice(array_values((array)($group['Filters']??[])),0,6)" in p,'relation':"$field_type==='relation'?['eq','neq']" in p,'taxonomy filter':"$kind==='taxonomy'" in p and "['in','not_in']" in p,'publish only':"'post_status'=>'publish'" in p,'candidate bound':'$candidate_limit=2000' in p,'pagination':'TotalPages' in p and 'PerPage' in p,'config bound':'strlen($config)>12000' in p,'tag save':'wp_set_object_terms($entry_id, $tags, self::DATA_TAG_TAXONOMY, false)' in p,'tag input':'name=\"data_tags\"' in p,'admin':'h18-advanced-query-form' in p,'JS':'/* v0.5.29 – UD-056 Advanced Query */' in j,'CSS':'/* v0.5.29 – UD-056 Advanced Query */' in c,'readme':'UD-056' in r and 'Version: 0.5.29' in r}
bad=[k for k,v in checks.items() if not v]
if bad:raise SystemExit('Failed v0.5.29 assertions: '+repr(bad))
# Private taxonomy only.
s=p.index('register_taxonomy(self::DATA_TAG_TAXONOMY');e=p.index('private function custom_data_field_types',s);tax=p[s:e]
if "'public' => false" not in tax or "'show_ui' => false" not in tax or "'show_in_rest' => false" not in tax: raise SystemExit('Data Tags taxonomy is not private')
# Normalizer bounded and excludes group/repeater field filters.
s=p.index('private function normalize_advanced_data_query');e=p.index('private function advanced_data_query_compare_value',s);norm=p[s:e]
for token in ["in_array($field_type,['group','repeater'],true)","$field_type==='relation'?['eq','neq']",'PerPage']:
    if token not in norm:raise SystemExit('Advanced normalizer missing '+token)
# Runner no raw SQL and only publish candidates.
s=p.index('private function run_advanced_data_query');e=p.index('private function advanced_data_query_public_config',s);run=p[s:e]
if '$wpdb' in run or 'SELECT ' in run.upper():raise SystemExit('Advanced query introduced raw SQL')
for token in ["'post_status'=>'publish'","$candidate_limit=2000",'array_slice($matches,$offset,$query[\'PerPage\'])']:
    if token not in run:raise SystemExit('Advanced runner missing '+token)
# Both preview and frontend use same runner.
if p.count('run_advanced_data_query(')<3:raise SystemExit('Preview/frontend do not share advanced runner')
# Frontend config decode is strict and page parameter is derived from query hash.
s=p.index('public function shortcode_data_query_advanced');e=p.index('public function render_data()',s);short=p[s:e]
for token in ["$page_param='h18q_'.$hash",'absint($_GET[$page_param])','esc_url($url)']:
    if token not in short:raise SystemExit('Frontend pagination/config safety missing '+token)
# Tag input capped to 20 and sanitized.
s=p.index('$raw_tags =');e=p.index("CUSTOM_DATA_ENTRY_SAVED",s);tags=p[s:e]
if "array_slice(preg_split('/\\s*,\\s*/', $raw_tags), 0, 20)" not in tags or 'sanitize_text_field' not in tags:raise SystemExit('Tag save is not bounded/sanitized')
# JS builder bounded 4x6 and does not offer group/repeater fields.
if "length>=4" not in j or "length>=6" not in j or "!['group','repeater'].includes" not in j:raise SystemExit('Advanced builder UI bounds/type exclusions missing')
print('v0.5.29 UD-056 Advanced Query security/architecture QA passed')
