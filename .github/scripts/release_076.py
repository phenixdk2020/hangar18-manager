from pathlib import Path
p=Path('hangar18-manager.php'); r=Path('readme.txt')
php=p.read_text(encoding='utf-8'); readme=r.read_text(encoding='utf-8')
for old,new in [(' * Version: 0.7.5',' * Version: 0.7.6'),("const VERSION = '0.7.5';","const VERSION = '0.7.6';")]:
    if php.count(old)!=1: raise SystemExit(f'version anchor mismatch: {old}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.7.5')!=1: raise SystemExit('readme version anchor mismatch')
readme=readme.replace('Version: 0.7.5','Version: 0.7.6',1)
entry='''\n\n== Version 0.7.6 – I3 Menu UI v2 ==\n\nNyt:\n- Shadow-only Menu UI v2 oven på den generiske MenuService.\n- Desktop presets: klassisk, floating pill, mega-menu og side rail.\n- Mobil presets: klassisk, off-canvas, fullscreen overlay og bottom navigation.\n- Hover/aktiv motion presets med reduced-motion hensyn i preview.\n- Nested menu-data med drag/drop, op/ned, indent/outdent, ikon, badge, beskrivelse og ComponentId mega-panel.\n- Keyboard-preview med top-level piletaster, submenu åbning og Escape.\n- Menu presentation gemmes separat fra menu-data og eksisterende gamle menu-records får sikre defaults.\n- Dangerous javascript/data/vbscript URL-schemes afvises, og controlleren kræver capability + nonce + sanitization.\n- Den offentlige legacy-menu og eksisterende sider/Vehicle/Event/Gallery er fortsat uændrede.\n'''
pos=readme.find('\n\n== Version 0.7.5')
if pos<0: raise SystemExit('changelog anchor missing')
readme=readme[:pos]+entry+readme[pos:]
p.write_text(php,encoding='utf-8'); r.write_text(readme,encoding='utf-8')
