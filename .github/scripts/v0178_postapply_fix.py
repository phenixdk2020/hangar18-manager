from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

# 1) Preserve moduleSlot through HierarchyNormalizer's historical
# nested-Section -> Kasse conversion. Only root Sections consume the value,
# but preserving it on containers keeps LayoutModel::normalize idempotent.
p=ROOT/'clean/hangar18-manager/src/Model/LayoutModel.php'
s=p.read_text(encoding='utf-8')
old="'moduleSlot' => $type === 'section' && in_array((string) ($raw['moduleSlot'] ?? 'before'), ['before','between','after'], true) ? (string) ($raw['moduleSlot'] ?? 'before') : 'before',"
new="'moduleSlot' => in_array((string) ($raw['moduleSlot'] ?? 'before'), ['before','between','after'], true) ? (string) ($raw['moduleSlot'] ?? 'before') : 'before',"
if new not in s:
    if old not in s: raise SystemExit('LayoutModel moduleSlot anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# 2) Eventdetail is the fixed/system event block. Flexible fields are separate
# Eventfelt nodes in the Designer detail template, so do not render the same
# values a second time from inside eventdetail.
p=ROOT/'clean/hangar18-manager/src/Frontend/Renderer.php'
s=p.read_text(encoding='utf-8')
old=".$summary.$description.$custom.'</article>';"
new=".$summary.$description.'</article>';"
if new not in s:
    if old not in s: raise SystemExit('Renderer Eventdetail custom return anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

print('v0.1.78 post-apply canonical fixes ready')
