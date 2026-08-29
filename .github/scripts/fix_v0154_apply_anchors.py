from pathlib import Path

p = Path('.github/scripts/apply_v0154_menu_ux_publish.py')
s = p.read_text(encoding='utf-8')
old = '''model = replace_once(
    model,
    "                    'mobileMode' => in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger',\\n                    'menuId' => max(0, (int) ($props['menuId'] ?? 0)),",
    "                    'mobileMode' => in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger',\\n                    'mobilePresentation' => in_array((string) ($props['mobilePresentation'] ?? 'dropdown'), ['dropdown', 'panel-right', 'panel-left'], true) ? (string) $props['mobilePresentation'] : 'dropdown',\\n                    'mobileCloseOnSelect' => !array_key_exists('mobileCloseOnSelect', $props) || !empty($props['mobileCloseOnSelect']),\\n                    'mobileCloseOutside' => !array_key_exists('mobileCloseOutside', $props) || !empty($props['mobileCloseOutside']),\\n                    'menuId' => max(0, (int) ($props['menuId'] ?? 0)),",
    'php menu mobile props'
)
'''
new = '''model = replace_once(
    model,
    "            $mobileMode = strtolower((string) ($raw['mobileMode'] ?? 'hamburger'));\\n            if (!in_array($mobileMode, ['hamburger', 'vertical', 'wrap'], true)) { $mobileMode = 'hamburger'; }\\n            return array_merge([\\n                'menuId' => absint($raw['menuId'] ?? 0),\\n                'orientation' => $orientation,\\n                'align' => $align,\\n                'mobileMode' => $mobileMode,",
    "            $mobileMode = strtolower((string) ($raw['mobileMode'] ?? 'hamburger'));\\n            if (!in_array($mobileMode, ['hamburger', 'vertical', 'wrap'], true)) { $mobileMode = 'hamburger'; }\\n            $mobilePresentation = strtolower((string) ($raw['mobilePresentation'] ?? 'dropdown'));\\n            if (!in_array($mobilePresentation, ['dropdown', 'panel-right', 'panel-left'], true)) { $mobilePresentation = 'dropdown'; }\\n            return array_merge([\\n                'menuId' => absint($raw['menuId'] ?? 0),\\n                'orientation' => $orientation,\\n                'align' => $align,\\n                'mobileMode' => $mobileMode,\\n                'mobilePresentation' => $mobilePresentation,\\n                'mobileCloseOnSelect' => array_key_exists('mobileCloseOnSelect', $raw) ? (bool) $raw['mobileCloseOnSelect'] : true,\\n                'mobileCloseOutside' => array_key_exists('mobileCloseOutside', $raw) ? (bool) $raw['mobileCloseOutside'] : true,",
    'php menu mobile props'
)
'''
if old not in s:
    raise SystemExit('old model patch block not found')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('0.1.54 apply anchors repaired')
