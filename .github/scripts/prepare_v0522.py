from pathlib import Path

p=Path('.github/scripts/patch_v0522.py')
t=p.read_text()

# 1) The ComponentRevision/Overrides pair exists twice; patch only render-time key remap.
old="""# Clear internal component variant during render key remap.
php=once(php,\"\"\"            $section['ComponentRevision'] = 0;
            $section['ComponentOverrides'] = [];
\"\"\",\"\"\"            $section['ComponentRevision'] = 0;
            $section['ComponentVariant'] = '';
            $section['ComponentOverrides'] = [];
\"\"\",'clear nested variant')
"""
new="""# Clear internal component variant only inside render-time key remap.
resolve_start=php.index('    private function resolve_page_component_instance_sections')
resolve_end=php.index('    private function page_module_storage_key',resolve_start)
resolve_block=php[resolve_start:resolve_end]
resolve_block=once(resolve_block,\"\"\"            $section['ComponentRevision'] = 0;
            $section['ComponentOverrides'] = [];
\"\"\",\"\"\"            $section['ComponentRevision'] = 0;
            $section['ComponentVariant'] = '';
            $section['ComponentOverrides'] = [];
\"\"\",'clear nested variant')
php=php[:resolve_start]+resolve_block+php[resolve_end:]
"""
if old not in t:
    raise SystemExit('Original clear nested variant patch definition missing')
t=t.replace(old,new,1)

# 2) v0.5.21 Pattern handler already has legacy guard + Navigator summary default name.
old_pattern="""# Pattern save handler posts selected subtree.
old=\"\"\"        const data = sectionPresetData($inspectedSection);
        if (!data) {
            return;
        }
        const defaultName = String(pageSectionControls($inspectedSection, '.h18-section-title-input').val() || inspectorTypeLabel(data.Type));
\"\"\"
new=\"\"\"        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length) { return; }
        const data = sections[0];
        const defaultName = String(pageSectionControls($inspectedSection, '.h18-section-title-input').val() || inspectorTypeLabel(data.Type));
\"\"\"
js=once(js,old,new,'pattern subtree save data')
"""
new_pattern="""# Pattern save handler posts selected subtree.
old=\"\"\"        const data = sectionPresetData($inspectedSection);
        if (!data || data.Type === 'legacy') {
            window.alert('Denne sektion kan ikke gemmes som komponent.');
            return;
        }
        const defaultName = String($inspectedSection.find('.h18-page-section-title-summary').text() || inspectorTypeLabel(data.Type)).trim();
\"\"\"
new=\"\"\"        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length || sections.some(function(section){ return ['legacy','component'].includes(String(section.Type || '')); })) {
            window.alert('Legacy og linked components kan ikke gemmes inde i et pattern.');
            return;
        }
        const data = sections[0];
        const defaultName = String($inspectedSection.find('.h18-page-section-title-summary').text() || inspectorTypeLabel(data.Type)).trim();
\"\"\"
js=once(js,old,new,'pattern subtree save data')
"""
if old_pattern not in t:
    raise SystemExit('Original pattern subtree patch definition missing')
t=t.replace(old_pattern,new_pattern,1)

p.write_text(t)
print('v0.5.22 patch prepared')
