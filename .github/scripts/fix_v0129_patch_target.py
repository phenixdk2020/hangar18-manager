from pathlib import Path

p = Path('.github/scripts/apply_v0129_floating_buttons.py')
s = p.read_text(encoding='utf-8')
old = """replace(core,\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'textColor')\",\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' && current.parentId ? 'overlay' : 'normal'; }\\n                else if (field === 'zIndex') { current.props.zIndex = clamp(parseInt(control.value || 20, 10) || 20, 1, 200); }\\n                else if (field === 'textColor')\")"""
new = """replace(core,\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'autoSize') { current.props.autoSize = !!control.checked; }\\n                else if (field === 'textColor')\",\n\"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\\n                else if (field === 'autoSize') { current.props.autoSize = !!control.checked; }\\n                else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' && current.parentId ? 'overlay' : 'normal'; }\\n                else if (field === 'zIndex') { current.props.zIndex = clamp(parseInt(control.value || 20, 10) || 20, 1, 200); }\\n                else if (field === 'textColor')\")"""
if s.count(old) != 1:
    raise SystemExit(f'Expected old v0.1.29 target once, found {s.count(old)}')
p.write_text(s.replace(old, new), encoding='utf-8')
print('0.1.29 patch target repaired for autoSize-aware handler')
