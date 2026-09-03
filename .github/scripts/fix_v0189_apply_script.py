from pathlib import Path

path = Path('.github/scripts/apply_v0189_manager_cleanup_export_all.py')
text = path.read_text(encoding='utf-8')
old = 'transfer, count = export_block.subn(replacement, transfer, count=1)'
new = 'transfer, count = export_block.subn(lambda _match: replacement, transfer, count=1)'
if old not in text and new not in text:
    raise SystemExit('v0.1.89 apply substitution marker not found')
if old in text:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')
print('v0.1.89 apply script literal replacement: OK')
