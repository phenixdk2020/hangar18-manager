from pathlib import Path
php=Path('hangar18-manager.php').read_text(); js=Path('assets/admin.js').read_text(); css=Path('assets/admin.css').read_text(); readme=Path('readme.txt').read_text()
checks={
'version':'Version: 0.5.26' in php and "const VERSION = '0.5.26';" in php,
'schema 1.20':"'Version'        => '1.20'" in php and "'1.19'" not in php,
'type label':"'query_list' => 'Repeater / Query list'" in php,
'default fields':all(x in php for x in ["'QueryListType'","'QueryListFilterField'","'QueryListComponentId'","'QueryListLimit'","'QueryListColumns'"]),
'normalized fields':all(x in php for x in ["'QueryListType'         => $query_list_type","'QueryListComponentVariant' => $query_list_component_variant","'QueryListLimit'        => $this->clamp_int"]),
'component containment block':"['legacy', 'component', 'query_list']" in php,
'usage includes query list':"['component','query_list']" in php and "QueryListComponentId" in php and "ReferenceType" in php,
'query adapter':'query_list_query_from_section' in php,
'renderer':'render_page_editor_query_list' in php,
'shared query core':'$posts = $this->run_custom_data_query($this->query_list_query_from_section($section), $normalized);' in php,
'context per result':"$context = $this->resolve_dynamic_data_context((string) $normalized['Type'], (int) $post->ID);" in php,
'context assigned':'$this->active_dynamic_data_context = $context;' in php,
'context restored':'$this->active_dynamic_data_context = $previous_context;' in php,
'finally restore':'finally {' in php,
'cycle guard':'active_query_list_stack' in php and 'count($this->active_query_list_stack) >= 3' in php,
'unique runtime key':"'-entry-' . (int) $post->ID" in php,
'component renderer reuse':'resolve_page_component_instance_sections($page_id, $instance)' in php and 'render_page_editor_layout_tree($page_id, $component_sections)' in php,
'variant':"QueryListComponentVariant" in php,
'admin controls':'h18-query-list-editor' in php and 'h18-query-list-filter-field' in php and 'h18-query-list-component' in php,
'JS controls':'refreshQueryListControlsV0526' in js and 'queryListOperatorMapV0526' in js,
'canvas preview':'h18-canvas-query-list' in js,
'CSS':'/* v0.5.26 – UD-057 Repeater / Query list */' in css,
'readme':'UD-057' in readme and 'Version: 0.5.26' in readme,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit('Failed v0.5.26 assertions: '+repr(failed))

# Query List must rely on the existing publish-only Query Builder core and must not implement a second DB query path.
s=php.index('private function query_list_query_from_section'); e=php.index('private function render_page_editor_section_front',s); ql=php[s:e]
if 'get_posts(' in ql or '$wpdb' in ql or 'WP_Query' in ql:
    raise SystemExit('Query List contains a parallel query implementation')
core_s=php.index('private function run_custom_data_query'); core_e=php.index('private function custom_data_query_shortcode_from_normalized',core_s); core=php[core_s:core_e]
if "'post_status' => 'publish'" not in core or 'return get_posts($args);' not in core:
    raise SystemExit('Shared Query Builder core is not publish-only/get_posts based')

# Context must be restored in finally even if component render fails.
render_s=php.index('private function render_page_editor_query_list'); render_e=php.index('private function render_page_editor_section_front',render_s); render=php[render_s:render_e]
if render.index('try {') > render.index('$this->active_query_list_stack[] = $component_id;'):
    pass
if 'finally {' not in render or render.index('finally {') > render.index('$this->active_dynamic_data_context = $previous_context;'):
    raise SystemExit('Dynamic context restore is not inside finally')
if 'array_pop($this->active_query_list_stack);' not in render:
    raise SystemExit('Query List stack is not popped')

# Component usage scan must map both component and query-list variants, so deletes remain safe.
usage_s=php.index('private function get_page_component_usage'); usage_e=php.index('private function get_page_components_for_editor',usage_s); usage=php[usage_s:usage_e]
for token in ['QueryListComponentId','QueryListComponentVariant','ReferenceType']:
    if token not in usage: raise SystemExit('Usage inspector missing '+token)

# Runtime IDs must differ for the same component repeated over multiple entries.
if "'Key' => sanitize_key((string) ($section['Key'] ?? 'query-list') . '-entry-' . (int) $post->ID)" not in render:
    raise SystemExit('Repeated component instance key is not entry-unique')

# The component definition validator must prevent a query-list hidden inside a linked component.
comp_s=php.index('private function normalize_page_component_definition'); comp_e=php.index('private function get_page_components',comp_s); comp=php[comp_s:comp_e]
if "['legacy', 'component', 'query_list']" not in comp:
    raise SystemExit('Linked component can recursively contain Query List')

# Query-list UI is driven by the same dynamic data catalog and component catalog already loaded by editor.
if 'pageDynamicDataCatalogV0524' not in js or 'pageLinkedComponents' not in js:
    raise SystemExit('Query List UI does not use canonical editor catalogs')

print('v0.5.26 UD-057 Repeater / Query list security/architecture QA passed')
