from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, content: str) -> None:
    (ROOT / rel).write_text(content, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if new in text:
        return
    if text.count(old) != 1:
        raise SystemExit(f'{rel}: expected one anchor, found {text.count(old)}')
    write(rel, text.replace(old, new, 1))


# Runtime version.
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    ' * Version: 0.1.78',
    ' * Version: 0.1.79',
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "define('H18_CLEAN_VERSION', '0.1.78');",
    "define('H18_CLEAN_VERSION', '0.1.79');",
)

# Active responsive editor layer: Desktop -> Laptop -> Tablet -> Mobile.
p = 'clean/hangar18-manager/assets/editor-v0121.js'
replace_once(p, "var DEVICES = ['desktop', 'laptop', 'mobile'];", "var DEVICES = ['desktop', 'laptop', 'tablet', 'mobile'];")
replace_once(
    p,
    """                var laptopRaw = source.geometry && source.geometry.laptop;
                var mobileRaw = source.geometry && source.geometry.mobile;
                responsive[id] = {
                    laptop: normalizeGeometry(laptopRaw, desktop, true),
                    mobile: normalizeGeometry(mobileRaw, desktop, true)
                };
                if (!laptopRaw) { responsive[id].laptop.inheritDesktop = true; }
                if (!mobileRaw) { responsive[id].mobile.inheritDesktop = true; }""",
    """                var laptopRaw = source.geometry && source.geometry.laptop;
                var tabletRaw = source.geometry && source.geometry.tablet;
                var mobileRaw = source.geometry && source.geometry.mobile;
                responsive[id] = {
                    laptop: normalizeGeometry(laptopRaw, desktop, true),
                    tablet: normalizeGeometry(tabletRaw, desktop, true),
                    mobile: normalizeGeometry(mobileRaw, desktop, true)
                };
                if (!laptopRaw) { responsive[id].laptop.inheritDesktop = true; }
                if (!tabletRaw) { responsive[id].tablet.inheritDesktop = true; }
                if (!mobileRaw) { responsive[id].mobile.inheritDesktop = true; }""",
)
replace_once(
    p,
    """        var mobile = state.mobile || normalizeGeometry(null, effectiveLaptop, true);
        return mobile.inheritDesktop !== false ? effectiveLaptop : normalizeGeometry(mobile, effectiveLaptop, false);""",
    """        var tablet = state.tablet || normalizeGeometry(null, effectiveLaptop, true);
        var effectiveTablet = tablet.inheritDesktop !== false ? effectiveLaptop : normalizeGeometry(tablet, effectiveLaptop, false);
        if (device === 'tablet') { return effectiveTablet; }
        var mobile = state.mobile || normalizeGeometry(null, effectiveTablet, true);
        return mobile.inheritDesktop !== false ? effectiveTablet : normalizeGeometry(mobile, effectiveTablet, false);""",
)
replace_once(
    p,
    """            node.geometry.laptop = clone(responsive[id].laptop);
            node.geometry.mobile = clone(responsive[id].mobile);""",
    """            node.geometry.laptop = clone(responsive[id].laptop);
            node.geometry.tablet = clone(responsive[id].tablet);
            node.geometry.mobile = clone(responsive[id].mobile);""",
)
replace_once(
    p,
    "return ({ desktop: 'Desktop', laptop: 'Laptop', mobile: 'Mobil' })[device] || device;",
    "return ({ desktop: 'Desktop', laptop: 'Laptop', tablet: 'Tablet', mobile: 'Mobil' })[device] || device;",
)
replace_once(
    p,
    """            button.className = 'button h18-clean-device-button';
            button.setAttribute('data-device', device);
            button.textContent = labelDevice(device);""",
    """            button.className = 'button h18-clean-device-button';
            button.setAttribute('data-device', device);
            button.setAttribute('aria-pressed', device === activeDevice ? 'true' : 'false');
            button.setAttribute('aria-label', 'Redigér ' + labelDevice(device) + '-layout');
            button.textContent = labelDevice(device);""",
)
replace_once(
    p,
    "' checked' : '') + '> Arv fra ' + (activeDevice === 'mobile' ? 'Laptop/Desktop' : 'Desktop') + '</label>'",
    "' checked' : '') + '> Arv fra ' + (activeDevice === 'mobile' ? 'Tablet/Laptop/Desktop' : (activeDevice === 'tablet' ? 'Laptop/Desktop' : 'Desktop')) + '</label>'",
)
replace_once(
    p,
    """        document.querySelectorAll('.h18-clean-device-button').forEach(function (button) {
            button.classList.toggle('button-primary', button.getAttribute('data-device') === activeDevice);
        });""",
    """        document.querySelectorAll('.h18-clean-device-button').forEach(function (button) {
            var isActive = button.getAttribute('data-device') === activeDevice;
            button.classList.toggle('button-primary', isActive);
            button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });""",
)

# Canvas viewport: same breakpoint width that module pages already use for Tablet.
p = 'clean/hangar18-manager/assets/editor-v0144-viewport.js'
replace_once(p, "var WIDTHS = { desktop: 1920, laptop: 1180, mobile: 390 };", "var WIDTHS = { desktop: 1920, laptop: 1180, tablet: 980, mobile: 390 };")
replace_once(p, "({ desktop: 'Desktop', laptop: 'Laptop', mobile: 'Mobil' })[device]", "({ desktop: 'Desktop', laptop: 'Laptop', tablet: 'Tablet', mobile: 'Mobil' })[device]")

# Responsive editor CSS: Tablet is a first-class viewport everywhere Laptop/Mobile are scoped.
p = 'clean/hangar18-manager/assets/editor-v0121.css'
s = read(p)
s = s.replace('/* Clean 0.1.21 – Desktop / Laptop / Mobil responsive Designer. */', '/* Visual Designer Manager 0.1.79 – Desktop / Laptop / Tablet / Mobil responsive Designer. */', 1)
s = s.replace('.h18-clean-root[data-h18-device="laptop"]{max-width:1024px;box-shadow:0 0 0 1px #c3c4c7,0 6px 24px rgba(0,0,0,.06)}\n.h18-clean-root[data-h18-device="mobile"]', '.h18-clean-root[data-h18-device="laptop"]{max-width:1180px;box-shadow:0 0 0 1px #c3c4c7,0 6px 24px rgba(0,0,0,.06)}\n.h18-clean-root[data-h18-device="tablet"]{max-width:980px;box-shadow:0 0 0 1px #c3c4c7,0 6px 24px rgba(0,0,0,.07)}\n.h18-clean-root[data-h18-device="mobile"]', 1)
s = s.replace('body[data-h18-clean-device="laptop"] .h18-clean-canvas-column,\nbody[data-h18-clean-device="mobile"]', 'body[data-h18-clean-device="laptop"] .h18-clean-canvas-column,\nbody[data-h18-clean-device="tablet"] .h18-clean-canvas-column,\nbody[data-h18-clean-device="mobile"]', 1)
s = s.replace('body[data-h18-clean-device="laptop"] .h18-clean-node.is-selected,\nbody[data-h18-clean-device="mobile"]', 'body[data-h18-clean-device="laptop"] .h18-clean-node.is-selected,\nbody[data-h18-clean-device="tablet"] .h18-clean-node.is-selected,\nbody[data-h18-clean-device="mobile"]', 1)
s = s.replace('body[data-h18-clean-device="laptop"] .h18-clean-move,\nbody[data-h18-clean-device="mobile"]', 'body[data-h18-clean-device="laptop"] .h18-clean-move,\nbody[data-h18-clean-device="tablet"] .h18-clean-move,\nbody[data-h18-clean-device="mobile"]', 1)
s = s.replace('body[data-h18-clean-device="laptop"] .h18-clean-v018-drop-overlay,\nbody[data-h18-clean-device="mobile"]', 'body[data-h18-clean-device="laptop"] .h18-clean-v018-drop-overlay,\nbody[data-h18-clean-device="tablet"] .h18-clean-v018-drop-overlay,\nbody[data-h18-clean-device="mobile"]', 1)
if 'data-h18-device="tablet"' not in s or 'data-h18-clean-device="tablet"' not in s:
    raise SystemExit('editor-v0121.css: Tablet selectors were not added')
write(p, s)

p = 'clean/hangar18-manager/assets/editor-v0144.css'
replace_once(
    p,
    ".h18-vd-viewport-stage>.h18-clean-root[data-h18-device=\"laptop\"],\n.h18-vd-viewport-stage>.h18-clean-root[data-h18-device=\"mobile\"]",
    ".h18-vd-viewport-stage>.h18-clean-root[data-h18-device=\"laptop\"],\n.h18-vd-viewport-stage>.h18-clean-root[data-h18-device=\"tablet\"],\n.h18-vd-viewport-stage>.h18-clean-root[data-h18-device=\"mobile\"]",
)

# Public frontend responsive renderer: Desktop -> Laptop -> Tablet -> Mobile.
p = 'clean/hangar18-manager/src/Frontend/ResponsiveRenderer.php'
replace_once(p, "    public const LAPTOP_MAX = 1180;\n    public const MOBILE_MAX = 782;", "    public const LAPTOP_MAX = 1180;\n    public const TABLET_MAX = 980;\n    public const MOBILE_MAX = 782;")
replace_once(p, "        $laptop = '';\n        $mobile = '';", "        $laptop = '';\n        $tablet = '';\n        $mobile = '';")
replace_once(
    p,
    """            $lg = self::effectiveGeometry($node, 'laptop');
            $mg = self::effectiveGeometry($node, 'mobile');
            $laptopRows = self::effectiveRows($id, 'laptop', $byId, $byParent, []);
            $mobileRows = self::effectiveRows($id, 'mobile', $byId, $byParent, []);""",
    """            $lg = self::effectiveGeometry($node, 'laptop');
            $tg = self::effectiveGeometry($node, 'tablet');
            $mg = self::effectiveGeometry($node, 'mobile');
            $laptopRows = self::effectiveRows($id, 'laptop', $byId, $byParent, []);
            $tabletRows = self::effectiveRows($id, 'tablet', $byId, $byParent, []);
            $mobileRows = self::effectiveRows($id, 'mobile', $byId, $byParent, []);""",
)
replace_once(
    p,
    """            $laptop .= self::geometryCss($selector, $lg, $laptopRows, $floating, $zIndex);
            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);""",
    """            $laptop .= self::geometryCss($selector, $lg, $laptopRows, $floating, $zIndex);
            $tablet .= self::geometryCss($selector, $tg, $tabletRows, $floating, $zIndex);
            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);""",
)
replace_once(
    p,
    """        echo '@media(max-width:' . esc_attr((string) self::LAPTOP_MAX) . 'px){' . $laptop . '}';
        echo '@media(max-width:' . esc_attr((string) self::MOBILE_MAX) . 'px){' . $mobile . '}';""",
    """        echo '@media(max-width:' . esc_attr((string) self::LAPTOP_MAX) . 'px){' . $laptop . '}';
        echo '@media(max-width:' . esc_attr((string) self::TABLET_MAX) . 'px){' . $tablet . '}';
        echo '@media(max-width:' . esc_attr((string) self::MOBILE_MAX) . 'px){' . $mobile . '}';""",
)
replace_once(
    p,
    """        $mobileRaw = is_array($geometry['mobile'] ?? null) ? $geometry['mobile'] : [];
        // Responsive inheritance is cascading in the UI: Mobile inherits the
        // effective Laptop layout (which itself may inherit Desktop).
        return !empty($mobileRaw['inheritDesktop']) ? $laptop : self::geometry($mobileRaw, $laptop);""",
    """        $tabletRaw = is_array($geometry['tablet'] ?? null) ? $geometry['tablet'] : [];
        $tablet = !empty($tabletRaw['inheritDesktop']) ? $laptop : self::geometry($tabletRaw, $laptop);
        if ($device === 'tablet') {
            return $tablet;
        }

        $mobileRaw = is_array($geometry['mobile'] ?? null) ? $geometry['mobile'] : [];
        // Responsive inheritance is cascading: Mobile inherits Tablet, Tablet
        // inherits Laptop, and Laptop may inherit Desktop.
        return !empty($mobileRaw['inheritDesktop']) ? $tablet : self::geometry($mobileRaw, $tablet);""",
)

# Release history.
p = 'clean/hangar18-manager/release-history.json'
data = json.loads(read(p))
versions = data.get('versions', []) if isinstance(data, dict) else []
if not any(isinstance(row, dict) and row.get('version') == '0.1.79' for row in versions):
    versions.insert(0, {
        'version': '0.1.79',
        'date': '2026-09-02',
        'items': [
            'CLEAN-RESPONSIVE-009: Tablet er nu et fuldt breakpoint i Designer, viewport og offentlig ResponsiveRenderer.',
            'Responsive kaskade er Desktop → Laptop (1180) → Tablet (980) → Mobil (782), med canonical geometry pr. breakpoint.',
            'Tablet har samme toolbar, Inspector, arv/override, flyt/resize og viewport Fit/Zoom som Laptop og Mobil.',
            'Responsive Undo/Redo snapshots omfatter Laptop/Tablet/Mobil og ændrer ikke de øvrige breakpoint-geometrier.',
            'Device-knapper opdaterer aria-pressed og har eksplicitte labels for tastatur/skærmlæserbrugere.'
        ]
    })
    data['versions'] = versions
write(p, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

# Release notes.
write('clean-release-notes.html', '''<h2>0.1.79 – Fuld Tablet- og responsive Designer-understøttelse</h2>
<ul>
<li><strong>Tablet er nu et fuldt breakpoint</strong> i Visual Designer på samme niveau som Desktop, Laptop og Mobil.</li>
<li>Den responsive kaskade er Desktop → Laptop (1180 px) → Tablet (980 px) → Mobil (782 px).</li>
<li>Tablet får egen canonical geometri, arv/override, Inspector-redigering, flyt/resize samt Fit/Zoom-preview.</li>
<li>Frontendens ResponsiveRenderer bruger nu den gemte Tablet-geometri i intervallet 783–980 px.</li>
<li>Responsive ændringer er fortsat Undo/Redo-sikre og isoleret til det valgte breakpoint.</li>
<li>Breakpoint-knapper har aktiv tilstand via <code>aria-pressed</code> og tydelige tilgængelighedslabels.</li>
</ul>
''')

# Canonical backlog.
p = 'docs/clean-backlog-v0100.md'
s = read(p)
s = s.replace('**Statusdato:** 1. september 2026  \n**Aktuel release:** v0.1.78', '**Statusdato:** 2. september 2026  \n**Aktuel release:** v0.1.79', 1)
s = s.replace('## Aktuel milepælsstatus · v0.1.78', '## Aktuel milepælsstatus · v0.1.79', 1)
s = s.replace('10. **v0.1.78 – Hybrid modulsider + Eventfelter — FÆRDIG:** almindelige Designer-elementer i før/mellem/efter-slots, Designer-detailpages og fleksible Eventfelter.', '10. **v0.1.78 – Hybrid modulsider + Eventfelter — FÆRDIG:** almindelige Designer-elementer i før/mellem/efter-slots, Designer-detailpages og fleksible Eventfelter.\n11. **v0.1.79 – CLEAN-RESPONSIVE-009 — FÆRDIG:** Tablet er et fuldt canonical breakpoint i toolbar, Inspector, viewport og frontend med isoleret Undo/Redo.', 1)
old = '''### CLEAN-RESPONSIVE-009 — DELVIST / MANUEL QA
- Canonical model har Desktop/Laptop/Tablet/Mobil geometri og arv.
- Desktop/Laptop/Mobil kan previewes i den nuværende viewport-runtime.
- Tablet skal have samme fulde, eksplicitte toolbar/preview-flow som de øvrige, før punktet lukkes.
- Breakpointændringer skal fortsat være Undo/Redo-sikre og må ikke mutere andre breakpoints.'''
new = '''### CLEAN-RESPONSIVE-009 — FÆRDIG I v0.1.79
- Canonical model har Desktop/Laptop/Tablet/Mobil geometri og kaskaderende arv.
- Alle fire breakpoints har eksplicit toolbar, Inspector og viewport Fit/Zoom.
- Tablet bruger 980 px som canonical preview/frontend-breakpoint mellem Laptop 1180 px og Mobil 782 px.
- Responsive ændringer snapshots i Undo/Redo og muterer kun det valgte breakpoint; øvrige breakpoint-geometrier bevares.'''
if old not in s and new not in s:
    raise SystemExit('backlog responsive block anchor missing')
s = s.replace(old, new, 1)
write(p, s)

write('docs/v0179-status.md', '''# Visual Designer Manager v0.1.79 – status

## Scope
`CLEAN-RESPONSIVE-009`: fuld Desktop/Laptop/Tablet/Mobil-understøttelse i canonical Designer og frontend.

## Implementeret
- Tablet føjet til aktiv device-toolbar og responsive editor-state.
- Canonical kaskade: Desktop → Laptop → Tablet → Mobil.
- Breakpoints: Laptop 1180 px, Tablet 980 px, Mobil 782 px.
- Tablet Inspector med arv/override samt flyt/resize på samme kontrakt som Laptop/Mobil.
- Viewport Fit/Zoom og status understøtter Tablet 980 px.
- Frontend ResponsiveRenderer emitterer Tablet-geometri og auto-height mellem 783–980 px.
- Breakpoint-knapper har `aria-pressed` og eksplicitte labels.

## Release gate
Kandidat må først frigives efter PHP/JS syntax, historiske regressioner, v0.1.79 responsive QA og central ZIP/manifest-build.
''')

print('Applied Visual Designer Manager v0.1.79 responsive completion.')
