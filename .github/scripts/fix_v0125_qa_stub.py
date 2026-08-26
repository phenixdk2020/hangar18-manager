from pathlib import Path

path = Path(__file__).resolve().parent / 'v0125_model_qa.php'
text = path.read_text(encoding='utf-8')
old = "return sprintf('00000000-0000-4000-8000-%012d', $GLOBALS['vd_uuid_counter']);"
new = "return sprintf('%08x-0000-4000-8000-%012x', $GLOBALS['vd_uuid_counter'], $GLOBALS['vd_uuid_counter']);"
if text.count(old) != 1:
    raise RuntimeError(f'Expected one QA UUID stub, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('0.1.25 QA UUID stub repaired.')
