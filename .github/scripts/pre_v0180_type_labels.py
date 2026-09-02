from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
s = p.read_text(encoding='utf-8')
old = "eventlist:'EVENTLISTE',eventdetail:'EVENTDETALJE',gallerylist:'GALLERIOVERSIGT'"
new = "eventlist:'EVENTLISTE',eventdetail:'EVENTDETALJE',eventvalue:'EVENTVÆRDI',eventimage:'EVENTBILLEDE',eventfield:'EVENTFELT',gallerylist:'GALLERIOVERSIGT'"
count = s.count(old)
if count not in (0, 2):
    raise SystemExit(f'Unexpected event type-label anchor count: {count}')
if count:
    s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')
print(f'Event type-label pre-fix complete; replaced {count} anchors.')
