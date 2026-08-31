from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / '.github/scripts/v0165_general_elements_qa.py'
text = path.read_text(encoding='utf-8')
old = '''    if not re.search(r'Version:\\s*0\\.1\\.65\\b', plugin):
        raise AssertionError('plugin header is not 0.1.65')
    if "define('H18_CLEAN_VERSION', '0.1.65');" not in plugin:
        raise AssertionError('H18_CLEAN_VERSION is not 0.1.65')
'''
new = '''    match = re.search(r'Version:\\s*([0-9]+)\\.([0-9]+)\\.([0-9]+)\\b', plugin)
    if not match or tuple(map(int, match.groups())) < (0, 1, 65):
        raise AssertionError('plugin version is older than 0.1.65')
    if not re.search(r"define\\('H18_CLEAN_VERSION', '[0-9]+\\.[0-9]+\\.[0-9]+'\\);", plugin):
        raise AssertionError('H18_CLEAN_VERSION is missing')
'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit('v0165 QA version lock anchor missing')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('v0.1.65 QA made forward-compatible.')
