from pathlib import Path

p=Path('.github/scripts/qa_v0523.py')
t=p.read_text()
old="""# Context survives recursive layout and linked components, ready for Query/Repeater.
start=php.index('private function render_page_editor_layout_tree');end=php.index('private function render_page_editor_front',start);tree=php[start:end]
if tree.count('$data_context')<4: raise SystemExit('Nested layout does not forward data_context consistently')
component_start=php.index(\"if ($section['Type'] === 'component')\");component_end=php.index(\"if ($section['Type'] === 'legacy')\",component_start)
if '$data_context' not in php[component_start:component_end]: raise SystemExit('Linked component loses data_context')
"""
new="""# Context survives recursive layout and linked components, ready for Query/Repeater.
start=php.index('private function render_page_editor_layout_tree');end=php.index('private function render_page_editor_front',start);tree=php[start:end]
required_tree_context=[
    \"render_page_editor_layout_tree($page_id, array $sections, $parent_key = '', $depth = 0, $data_context = null)\",
    \"render_page_editor_layout_tree($page_id, $sections, (string) $section['Key'], $depth + 1, $data_context)\",
    \"render_page_editor_section_front($page_id, $section, $children, $data_context)\",
]
for marker in required_tree_context:
    if marker not in tree: raise SystemExit('Nested layout does not forward data_context: '+marker)
component_start=php.index(\"if ($section['Type'] === 'component')\");component_end=php.index(\"if ($section['Type'] === 'legacy')\",component_start)
if '$data_context' not in php[component_start:component_end]: raise SystemExit('Linked component loses data_context')
"""
if old not in t:
    raise SystemExit('Original context propagation QA block missing')
p.write_text(t.replace(old,new,1))
print('v0.5.23 QA assertions prepared')
