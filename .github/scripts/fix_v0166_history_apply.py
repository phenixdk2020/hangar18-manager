from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / '.github/scripts/apply_v0166_foundation.py'
text = path.read_text(encoding='utf-8')
old = '''history = json.loads(read(history_path))
if not any(str(row.get('version')) == '0.1.66' for row in history if isinstance(row, dict)):
    history.insert(0, {
        'version': '0.1.66',
        'title': 'Icon Library, Tabelkanter og Menu-preview',
        'status': 'test',
        'contracts': ['VD-ICON-LIBRARY-001','VD-TABLE-BORDERS-001','VD-MENU-PREVIEW-001','VD-ADMIN-STATUS-002'],
    })
    write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\\n')
'''
new = '''history = json.loads(read(history_path))
if not isinstance(history, dict):
    raise SystemExit('release-history root must be an object')
versions = history.get('versions')
if not isinstance(versions, list):
    versions = []
    history['versions'] = versions
if not any(str(row.get('version')) == '0.1.66' for row in versions if isinstance(row, dict)):
    versions.insert(0, {
        'version': '0.1.66',
        'date': '2026-08-31',
        'items': [
            'VD-ICON-LIBRARY-001: Centralt SVG-ikonregister med Core, Module og reserveret Custom-niveau.',
            'VD-TABLE-BORDERS-001: Excel-lignende multi-cell selection og canonical kanter pr. side/celle.',
            'VD-MENU-PREVIEW-001: Bredere Desktop Struktur-preview med nowrap og vandret scroll.',
            'VD-ADMIN-STATUS-002: Log og Konvertering vises som Klar.',
        ],
    })
    write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\\n')
'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit('v0.1.66 release-history apply anchor missing')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('v0.1.66 apply release-history handling fixed.')
