from pathlib import Path

php=Path('hangar18-manager.php').read_text()
js=Path('assets/admin.js').read_text()
css=Path('assets/admin.css').read_text()
readme=Path('readme.txt').read_text()

checks={
 'version': 'Version: 0.5.21' in php and "const VERSION = '0.5.21';" in php,
 'schema': php.count("'Version'        => '1.17'")==3,
 'separate store': "PAGE_COMPONENTS_OPTION      = 'hangar18_manager_page_components_v1'" in php and 'PAGE_PRESETS_OPTION' in php,
 'component type': "'component'  => 'Linked component'" in php and "component: 'Linked component'" in js,
 'component fields': all(x in php for x in ["'NavigatorLabel'", "'NavigatorLocked'", "'ComponentId'", "'ComponentRevision'", "'ComponentOverrides'"]),
 'component ajax': all(x in php for x in ['ajax_save_page_component','ajax_delete_page_component','h18_page_components_v0521']),
 'definition normalize': 'normalize_page_component_definition' in php,
 'nested component guard': "in_array($raw_type, ['legacy', 'component'], true)" in php,
 'one root': "count($roots) !== 1" in php,
 'input allowlist': "['Title', 'Content', 'MediaId', 'Button1Label', 'Button1Url', 'Button2Label', 'Button2Url']" in php,
 'risky content gate': "['css','html','shortcode','embed']" in php,
 'atomic store': 'update_option(self::PAGE_COMPONENTS_OPTION, $components, false);' in php,
 'usage scanner': 'get_page_component_usage' in php and "sanitize_key((string) ($section['Type'] ?? '')) !== 'component'" in php,
 'delete usage block': "Komponenten bruges stadig på" in php,
 'input identity guard': 'Frigivne input-ID’er skal bevares ved global opdatering' in php,
 'render propagation': 'resolve_page_component_instance_sections' in php and 'data-h18-component-revision' in php,
 'unique render keys': "hash('sha256', (int) $page_id" in php and '$key_map' in php,
 'component data embed': 'h18-page-components-data' in php,
 'linked library': 'h18-linked-components-list' in php and 'renderLinkedComponentsV0521' in js,
 'pattern compatibility': 'PAGE_PRESETS_OPTION' in php and 'Gem som pattern' in php and 'sectionPresetData' in js,
 'subtree': 'componentSubtreeRowsV0521' in js and 'componentSubtreeDataV0521' in js,
 'designer inputs': 'componentCandidateInputsV0521' in js and 'h18-component-input-choice' in js,
 'local overrides': 'h18-component-overrides-json' in php and 'parseComponentOverridesV0521' in js,
 'media override': 'h18-component-override-media' in js,
 'navigator rename': 'h18-navigator-rename' in js and 'NavigatorLabel' in php,
 'navigator lock': 'h18-navigator-toggle-lock' in js and 'rowLockedV0521' in js,
 'locked delete': "Laget er låst. Lås det op før du fjerner det." in js,
 'locked type': "Laget er låst. Lås det op før du ændrer elementtype." in js,
 'usage UI': 'h18-linked-component-usage' in js,
 'readme': 'page-editor schema løftes bagudkompatibelt til 1.17' in readme,
}
failed=[k for k,v in checks.items() if not v]
if failed:
    raise SystemExit('Failed v0.5.21 assertions: '+repr(failed))

# Old presets must remain non-linked: applying a pattern creates a fresh ordinary section.
preset_start=js.index('function applySectionPreset')
preset_end=js.index('function componentDefinitionSectionV0521', preset_start)
preset_block=js[preset_start:preset_end]
if 'ComponentId' in preset_block or 'applyLinkedComponentV0521' in preset_block:
    raise SystemExit('Legacy pattern insertion became linked unexpectedly')

# Component definitions must never recursively resolve another component.
normalize_start=php.index('private function normalize_page_component_definition')
normalize_end=php.index('private function get_page_components()', normalize_start)
if "['legacy', 'component']" not in php[normalize_start:normalize_end]:
    raise SystemExit('Recursive linked component rejection missing')

# Global update must be a single option write, not per-page mutation.
save_start=php.index('public function ajax_save_page_component')
save_end=php.index('public function ajax_delete_page_component', save_start)
save_block=php[save_start:save_end]
if 'wp_update_post(' in save_block or 'save_page_editor_data(' in save_block:
    raise SystemExit('Component propagation mutates pages instead of linked definition')
if save_block.count('update_option(self::PAGE_COMPONENTS_OPTION') != 1:
    raise SystemExit('Component definition update is not one atomic option write')

# Usage-protected delete must check before mutation.
del_start=php.index('public function ajax_delete_page_component')
del_end=php.index('private function resolve_page_component_instance_sections', del_start)
del_block=php[del_start:del_end]
if del_block.index('get_page_component_usage') > del_block.index('unset($components[$component_id])'):
    raise SystemExit('Delete mutates before usage check')

# Linked definitions are not allowed to expose risky custom-code content.
if "if ($field === 'Content' && in_array($target_type, ['css','html','shortcode','embed'], true))" not in php:
    raise SystemExit('Risky component content could be locally overridden')

print('v0.5.21 component/security QA passed')
