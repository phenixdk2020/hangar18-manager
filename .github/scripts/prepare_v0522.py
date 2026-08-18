from pathlib import Path

p=Path('.github/scripts/patch_v0522.py')
t=p.read_text()
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
p.write_text(t.replace(old,new,1))
print('v0.5.22 patch prepared')
