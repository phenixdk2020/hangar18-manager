from pathlib import Path

p = Path('.github/scripts/apply_v0129_floating_buttons.py')
s = p.read_text(encoding='utf-8')

old = """replace(core,\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'textColor')\",\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' && current.parentId ? 'overlay' : 'normal'; }\\n                else if (field === 'zIndex') { current.props.zIndex = clamp(parseInt(control.value || 20, 10) || 20, 1, 200); }\\n                else if (field === 'textColor')\")"""
new = """replace(core,\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'autoSize') { current.props.autoSize = !!control.checked; }\\n                else if (field === 'textColor')\",\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'autoSize') { current.props.autoSize = !!control.checked; }\\n                else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' && current.parentId ? 'overlay' : 'normal'; }\\n                else if (field === 'zIndex') { current.props.zIndex = clamp(parseInt(control.value || 20, 10) || 20, 1, 200); }\\n                else if (field === 'textColor')\")"""
if s.count(old) != 1:
    raise SystemExit(f'Expected old event-handler v0.1.29 target once, found {s.count(old)}')
s = s.replace(old, new)

old = """replace(model,\n\"                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\\n            ], $border);\",\n\"                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\\n                'placementMode' => strtolower((string) ($raw['placementMode'] ?? 'normal')) === 'overlay' ? 'overlay' : 'normal',\\n                'zIndex' => self::clamp($raw['zIndex'] ?? 20, 1, 200, 20),\\n            ], $border);\")"""
new = """replace(model,\n\"                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\\n                'autoSize' => array_key_exists('autoSize', $raw) ? (bool) $raw['autoSize'] : true,\\n            ], $border);\",\n\"                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\\n                'autoSize' => array_key_exists('autoSize', $raw) ? (bool) $raw['autoSize'] : true,\\n                'placementMode' => strtolower((string) ($raw['placementMode'] ?? 'normal')) === 'overlay' ? 'overlay' : 'normal',\\n                'zIndex' => self::clamp($raw['zIndex'] ?? 20, 1, 200, 20),\\n            ], $border);\")"""
if s.count(old) != 1:
    raise SystemExit(f'Expected old LayoutModel v0.1.29 target once, found {s.count(old)}')
s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print('0.1.29 patch targets repaired for current 0.1.28 source')
