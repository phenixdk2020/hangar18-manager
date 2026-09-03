from pathlib import Path
import json,re

ROOT=Path('.')
plugin=(ROOT/'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
export=(ROOT/'clean/hangar18-manager/src/Admin/ExportController.php').read_text(encoding='utf-8')
release=(ROOT/'.github/workflows/visual-designer-release.yml').read_text(encoding='utf-8')
backlog=(ROOT/'docs/BACKLOG-CANONICAL.md').read_text(encoding='utf-8')
history=json.loads((ROOT/'clean/hangar18-manager/release-history.json').read_text(encoding='utf-8'))
notes=(ROOT/'clean-release-notes.html').read_text(encoding='utf-8')

m=re.search(r"define\('VDM_VERSION',\s*'([^']+)'\);",plugin)
assert m and tuple(map(int,m.group(1).split('.'))) >= (0,1,93)
# User-facing export terminology.
assert "            'Eksport',\n            'Eksport'," in export
assert "echo '<h1>Eksport</h1>'" in export
for label in ['Eksporter plugin','Eksporter tema','Eksporter websider','Eksporter navigation','Eksporter billeder','Eksporter dokumenter','Eksporter videoer','Eksporter alle medier']:
    assert label in export,label
assert "'>Eksporter ' . esc_html(self::LABELS[$kind])" in export
assert "'pages' => 'Websider'" in export
assert "'videos' => 'Videoer'" in export
assert 'Ukendt eksporttype.' in export
assert 'midlertidig eksportfil.' in export
assert 'Eksportpakken blev ikke oprettet korrekt.' in export
# Central release gate must contain current maintenance QA before packaging.
assert '- name: Verify current VDM release gates' in release
for script in [
 'v0192_export_integrity_qa.py','v0191_form_design_controls_qa.py','v0190_form_wysiwyg_parity_qa.py',
 'v0189_manager_cleanup_export_all_qa.py','v0186_site_settings_qa.py','v0185_editor_live_box_qa.py',
 'v0185_event_facts_typography_qa.py','v0185_semantic_qa.py','v0184_portable_transfer_qa.py','v0181_complete_qa.py']:
    assert script in release,script
assert release.index('- name: Verify current VDM release gates') < release.index('- name: Build package and manifest')
# Backlog pointer is current and keeps v0.2.0 migration isolated.
assert '# Visual Designer Manager — canonical backlog pointer' in backlog
assert '**Aktuel vedligeholdelsesbaseline:** `v0.1.93`' in backlog
assert '**Næste planlagte hovedmilepæl:** `v0.2.0`' in backlog
assert 'plugin-basename-migration' in backlog or 'plugin-basename' in backlog
assert any(str(row.get('version'))=='0.1.93' for row in history.get('versions',[]))
assert 'data-version="0.1.93"' in notes
assert (ROOT/'docs/v0193-status.md').is_file()
print('v0.1.93 release/UX hardening QA: PASS on runtime '+m.group(1))
