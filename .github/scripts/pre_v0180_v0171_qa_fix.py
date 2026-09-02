from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / '.github/scripts/v0171_event_module_qa.py'
s = p.read_text(encoding='utf-8')
old = '''require('clean/hangar18-manager/src/Admin/EditorController.php',
        "'eventlist' => 'Eventliste'", "'eventdetail' => 'Eventdetalje'")'''
new = '''if current < (0, 1, 80):
    require('clean/hangar18-manager/src/Admin/EditorController.php',
            "'eventlist' => 'Eventliste'", "'eventdetail' => 'Eventdetalje'")
else:
    # v0.1.80 keeps eventdetail canonical/runtime compatibility but replaces the
    # old all-in-one palette entry with composable Eventværdi/Eventbillede pieces.
    require('clean/hangar18-manager/src/Admin/EditorController.php',
            "'eventlist' => 'Eventliste'", "'eventvalue' => 'Eventværdi'", "'eventimage' => 'Eventbillede'")'''
if new in s:
    print('v0.1.71 QA already forward-compatible.')
elif old in s:
    p.write_text(s.replace(old, new, 1), encoding='utf-8')
    print('v0.1.71 event QA updated for v0.1.80 composable palette.')
else:
    raise SystemExit('v0.1.71 palette contract block not found')
