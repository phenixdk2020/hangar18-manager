from pathlib import Path

path = Path('clean/hangar18-manager/src/Admin/ManualController.php')
text = path.read_text(encoding='utf-8')
old = "$html = str_replace('src=\\\"docs/user-manual-assets/', 'src=\\\"' . esc_url($assetBase), $html);"
new = "$html = str_replace('src=\"docs/user-manual-assets/', 'src=\"' . esc_url($assetBase), $html);"
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('ManualController image URL rewrite anchor not found')
path.write_text(text, encoding='utf-8')
print('Ensured generated manual image URLs are rewritten correctly at runtime.')
