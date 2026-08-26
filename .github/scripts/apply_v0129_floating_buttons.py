from pathlib import Path

ROOT = Path('.')

def replace(path, old, new, expected=1):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    count = s.count(old)
    if count != expected:
        raise SystemExit(f'{path}: expected {expected} occurrence(s), found {count}: {old[:100]!r}')
    p.write_text(s.replace(old, new), encoding='utf-8')
    print(f'patched {path}: {count} replacement(s)')

core = 'clean/hangar18-manager/assets/editor-v018-core.js'
replace(core,
"function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap'})[String(type || '')] || String(type || 'Element'); }\n    function fieldLabel(field) { return ({gx:'X-position'",
"function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap'})[String(type || '')] || String(type || 'Element'); }\n    function isFloatingButton(node) { return !!(node && node.type === 'button' && node.parentId && node.props && node.props.placementMode === 'overlay'); }\n    function fieldLabel(field) { return ({gx:'X-position'")
replace(core,
"paddingY:'lodret padding',autoSize:'automatisk størrelse'})",
"paddingY:'lodret padding',autoSize:'automatisk størrelse',placementMode:'placering',zIndex:'lag'})")
replace(core,
"                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),\n                autoSize: raw.autoSize !== false\n",
"                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),\n                autoSize: raw.autoSize !== false,\n                placementMode: String(raw.placementMode || 'normal').toLowerCase() === 'overlay' ? 'overlay' : 'normal',\n                zIndex: clamp(parseInt(raw.zIndex || 20, 10) || 20, 1, 200)\n")
replace(core,
"        children(parentId).forEach(function (node) {\n            const g = node.geometry.desktop;\n            bottom = Math.max(bottom, g.y + (g.h > 0 ? g.h : MIN_SPLIT_H));\n        });",
"        children(parentId).forEach(function (node) {\n            if (isFloatingButton(node)) { return; }\n            const g = node.geometry.desktop;\n            bottom = Math.max(bottom, g.y + (g.h > 0 ? g.h : MIN_SPLIT_H));\n        });")
replace(core,
"            const list = children(parentId).slice().sort(function (a, b) {",
"            const list = children(parentId).filter(function (node) { return !isFloatingButton(node); }).slice().sort(function (a, b) {")
replace(core,
"            const kids = children(parent.id);\n            let required = kids.length ? 0 : MIN_SPLIT_H;",
"            const kids = children(parent.id).filter(function (child) { return !isFloatingButton(child); });\n            let required = kids.length ? 0 : MIN_SPLIT_H;")
replace(core,
"                    if (PARENT_TYPES.includes(list[i].type) || PARENT_TYPES.includes(list[j].type)) { continue; }\n                    const a = list[i].geometry.desktop;",
"                    if (PARENT_TYPES.includes(list[i].type) || PARENT_TYPES.includes(list[j].type)) { continue; }\n                    if (isFloatingButton(list[i]) || isFloatingButton(list[j])) { continue; }\n                    const a = list[i].geometry.desktop;")
replace(core,
"        autoButtons.forEach(function (id) { materialized.add(id); });",
"        autoButtons.forEach(function (id) { const node = nodeById(id); if (!isFloatingButton(node)) { materialized.add(id); } });")
replace(core,
"        const target = directDropTarget(event, parentId, movingId, surface);\n        if (!target) {",
"        const movingNode = movingId ? nodeById(movingId) : null;\n        if (isFloatingButton(movingNode)) {\n            const pointerRow = clamp(Math.round((event.clientY - rect.top) / ROW_PX), 0, 10000);\n            const movingH = Math.max(1, movingNode.geometry.desktop.h || MIN_SPLIT_H);\n            placement.y = Math.max(0, pointerRow - Math.floor(movingH / 2));\n            placement.targetId = '';\n            placement.zone = 'overlay';\n            placement.bandIds = [];\n            placement.targetGeometry = null;\n            return placement;\n        }\n        const target = directDropTarget(event, parentId, movingId, surface);\n        if (!target) {")
replace(core,
"return ({ above: '↑ DEL CELLEN OVER', below: '↓ DEL CELLEN UNDER', left: '← DEL CELLEN VENSTRE', right: 'DEL CELLEN HØJRE →', inside: 'IND I KASSEN', 'inside-empty': 'IND I KASSEN', free: 'FRI PLACERING' })[zone] || zone;",
"return ({ above: '↑ DEL CELLEN OVER', below: '↓ DEL CELLEN UNDER', left: '← DEL CELLEN VENSTRE', right: 'DEL CELLEN HØJRE →', inside: 'IND I KASSEN', 'inside-empty': 'IND I KASSEN', free: 'FRI PLACERING', overlay: 'FLYDENDE · FRI PLACERING' })[zone] || zone;")
replace(core,
"        if (sourceSnapshot) { healSourceCell(sourceSnapshot, id); }",
"        if (sourceSnapshot && !isFloatingButton(node)) { healSourceCell(sourceSnapshot, id); }")
old_apply = """    function applyCardGeometry(card, node, geometry) {
        card.style.gridColumn = String(geometry.x + 1) + ' / span ' + String(geometry.w);
        card.style.marginTop = '0px';
        if (geometry.h > 0) {
            card.style.gridRow = String(Math.max(0, geometry.y) + 1) + ' / span ' + String(geometry.h);
            card.style.height = 'auto';
            card.style.minHeight = String(geometry.h * ROW_PX) + 'px';
            card.setAttribute('data-h18-explicit-grid', '1');
        } else {
            card.style.gridRow = '';
            card.style.height = '';
            card.style.minHeight = '';
            card.removeAttribute('data-h18-explicit-grid');
        }
        card.setAttribute('data-geometry', [geometry.x, geometry.y, geometry.w, geometry.h].join(','));
    }
"""
new_apply = """    function applyCardGeometry(card, node, geometry) {
        if (isFloatingButton(node)) {
            card.style.position = 'absolute';
            card.style.gridColumn = 'auto';
            card.style.gridRow = 'auto';
            card.style.left = ((geometry.x / UNITS) * 100) + '%';
            card.style.top = String(Math.max(0, geometry.y) * ROW_PX) + 'px';
            card.style.width = ((geometry.w / UNITS) * 100) + '%';
            card.style.height = geometry.h > 0 ? String(geometry.h * ROW_PX) + 'px' : 'auto';
            card.style.minHeight = geometry.h > 0 ? String(geometry.h * ROW_PX) + 'px' : '';
            card.style.zIndex = String(clamp(parseInt(node.props.zIndex || 20, 10) || 20, 1, 200));
            card.style.marginTop = '0px';
            card.setAttribute('data-h18-floating', '1');
            card.setAttribute('data-h18-explicit-grid', '1');
            card.setAttribute('data-geometry', [geometry.x, geometry.y, geometry.w, geometry.h].join(','));
            return;
        }
        card.style.position = 'relative';
        card.style.left = '';
        card.style.top = '';
        card.style.width = '';
        card.style.zIndex = '';
        card.removeAttribute('data-h18-floating');
        card.style.gridColumn = String(geometry.x + 1) + ' / span ' + String(geometry.w);
        card.style.marginTop = '0px';
        if (geometry.h > 0) {
            card.style.gridRow = String(Math.max(0, geometry.y) + 1) + ' / span ' + String(geometry.h);
            card.style.height = 'auto';
            card.style.minHeight = String(geometry.h * ROW_PX) + 'px';
            card.setAttribute('data-h18-explicit-grid', '1');
        } else {
            card.style.gridRow = '';
            card.style.height = '';
            card.style.minHeight = '';
            card.removeAttribute('data-h18-explicit-grid');
        }
        card.setAttribute('data-geometry', [geometry.x, geometry.y, geometry.w, geometry.h].join(','));
    }
"""
replace(core, old_apply, new_apply)
replace(core,
"            card.className = 'h18-clean-node h18-clean-node--' + node.type + (selectedId === node.id ? ' is-selected' : '');",
"            card.className = 'h18-clean-node h18-clean-node--' + node.type + (isFloatingButton(node) ? ' is-floating' : '') + (selectedId === node.id ? ' is-selected' : '');")
replace(core,
"            html += '<label class=\"h18-clean-checkbox\"><input data-field=\"targetBlank\" type=\"checkbox\"' + (node.props.targetBlank ? ' checked' : '') + '> Åbn i ny fane</label>';",
"            html += '<label class=\"h18-clean-checkbox\"><input data-field=\"targetBlank\" type=\"checkbox\"' + (node.props.targetBlank ? ' checked' : '') + '> Åbn i ny fane</label>';\n            html += '<label>Placering<select data-field=\"placementMode\"><option value=\"normal\"' + (node.props.placementMode !== 'overlay' ? ' selected' : '') + '>Normal i layout</option><option value=\"overlay\"' + (node.props.placementMode === 'overlay' ? ' selected' : '') + '>Flydende i Sektion/Kasse</option></select></label>';\n            if (node.props.placementMode === 'overlay') { html += '<label>Lag<input data-field=\"zIndex\" type=\"number\" min=\"1\" max=\"200\" value=\"' + (node.props.zIndex || 20) + '\"><span class=\"description\">Højere lag ligger foran andre elementer. Flyt knappen med ✥ eller X/Y.</span></label>'; }")
replace(core,
"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\n                else if (field === 'textColor')",
"                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\n                else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' && current.parentId ? 'overlay' : 'normal'; }\n                else if (field === 'zIndex') { current.props.zIndex = clamp(parseInt(control.value || 20, 10) || 20, 1, 200); }\n                else if (field === 'textColor')")

# Responsive editor: floating geometry follows the active breakpoint.
respjs = 'clean/hangar18-manager/assets/editor-v0121.js'
replace(respjs,
"    function children(parentId, map) {\n        return Object.keys(map).map(function (id) { return map[id]; }).filter(function (node) {",
"    function isFloatingButton(node) { return !!(node && node.type === 'button' && node.parentId && node.props && node.props.placementMode === 'overlay'); }\n    function children(parentId, map) {\n        return Object.keys(map).map(function (id) { return map[id]; }).filter(function (node) {")
replace(respjs,
"        children(id, map).forEach(function (child) {\n            var cg = effective(child, device);",
"        children(id, map).forEach(function (child) {\n            if (isFloatingButton(child)) { return; }\n            var cg = effective(child, device);")
old_rg = """    function applyGeometry(card, g, rows) {
        card.style.gridColumn = String(g.x + 1) + ' / span ' + String(g.w);
        card.style.gridRow = String(Math.max(0, g.y) + 1) + ' / span ' + String(Math.max(1, rows));
        card.style.minHeight = String(Math.max(1, rows) * ROW_PX) + 'px';
        card.style.marginTop = '0px';
        card.setAttribute('data-h18-active-geometry', [g.x, g.y, g.w, g.h].join(','));
    }
"""
new_rg = """    function applyGeometry(card, g, rows, node) {
        if (isFloatingButton(node)) {
            card.style.position = 'absolute';
            card.style.gridColumn = 'auto';
            card.style.gridRow = 'auto';
            card.style.left = ((g.x / UNITS) * 100) + '%';
            card.style.top = String(Math.max(0, g.y) * ROW_PX) + 'px';
            card.style.width = ((g.w / UNITS) * 100) + '%';
            card.style.height = String(Math.max(1, rows) * ROW_PX) + 'px';
            card.style.minHeight = String(Math.max(1, rows) * ROW_PX) + 'px';
            card.style.zIndex = String(clamp(n(node.props && node.props.zIndex, 20), 1, 200));
        } else {
            card.style.position = 'relative';
            card.style.left = '';
            card.style.top = '';
            card.style.width = '';
            card.style.height = '';
            card.style.zIndex = '';
            card.style.gridColumn = String(g.x + 1) + ' / span ' + String(g.w);
            card.style.gridRow = String(Math.max(0, g.y) + 1) + ' / span ' + String(Math.max(1, rows));
            card.style.minHeight = String(Math.max(1, rows) * ROW_PX) + 'px';
        }
        card.style.marginTop = '0px';
        card.setAttribute('data-h18-active-geometry', [g.x, g.y, g.w, g.h].join(','));
    }
"""
replace(respjs, old_rg, new_rg)
replace(respjs,
"            applyGeometry(card, effective(node, activeDevice), rowsFor(id, activeDevice, map, {}));",
"            applyGeometry(card, effective(node, activeDevice), rowsFor(id, activeDevice, map, {}), node);")

# Canonical PHP model.
model = 'clean/hangar18-manager/src/Model/LayoutModel.php'
replace(model,
"                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\n            ], $border);",
"                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\n                'placementMode' => strtolower((string) ($raw['placementMode'] ?? 'normal')) === 'overlay' ? 'overlay' : 'normal',\n                'zIndex' => self::clamp($raw['zIndex'] ?? 20, 1, 200, 20),\n            ], $border);")

# Frontend renderer: position floating button relative to its Section/Kasse.
renderer = 'clean/hangar18-manager/src/Frontend/Renderer.php'
replace(renderer,
"            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 10)));\n            $buttonStyle = $style . $borderStyle . $spacingStyle . $radiusStyle\n                . '--h18-btn-bg:'",
"            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 10)));\n            $placementMode = (string) ($props['placementMode'] ?? 'normal');\n            $floating = $placementMode === 'overlay' && (string) ($node['parentId'] ?? '') !== '';\n            $layoutStyle = $style;\n            if ($floating) {\n                $leftPct = ($x / LayoutModel::UNITS) * 100;\n                $widthPct = ($w / LayoutModel::UNITS) * 100;\n                $zIndex = max(1, min(200, (int) ($props['zIndex'] ?? 20)));\n                $heightCss = $h > 0 ? 'height:' . ($h * LayoutModel::ROW_PX) . 'px;min-height:' . ($h * LayoutModel::ROW_PX) . 'px;' : '';\n                $layoutStyle = 'position:absolute;left:' . $leftPct . '%;top:' . ($y * LayoutModel::ROW_PX) . 'px;width:' . $widthPct . '%;' . $heightCss . 'z-index:' . $zIndex . ';grid-column:auto;grid-row:auto;margin-top:0;';\n            }\n            $buttonStyle = $layoutStyle . $borderStyle . $spacingStyle . $radiusStyle\n                . '--h18-btn-bg:'")
replace(renderer,
"            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-button\" style=\"' . esc_attr($buttonStyle) . '\"><a class=\"h18-clean-front-button-link\"",
"            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-button' . ($floating ? ' h18-clean-front-button--floating' : '') . '\" style=\"' . esc_attr($buttonStyle) . '\"><a class=\"h18-clean-front-button-link\"")

# Responsive frontend overrides use the responsive x/y/w/h for floating buttons.
rr = 'clean/hangar18-manager/src/Frontend/ResponsiveRenderer.php'
replace(rr,
"            $selector = '#h18-clean-' . self::cssId($id);\n            $laptop .= self::geometryCss($selector, $lg, $laptopRows);\n            $mobile .= self::geometryCss($selector, $mg, $mobileRows);",
"            $selector = '#h18-clean-' . self::cssId($id);\n            $props = is_array($node['props'] ?? null) ? $node['props'] : [];\n            $floating = (string) ($node['type'] ?? '') === 'button' && (string) ($node['parentId'] ?? '') !== '' && (string) ($props['placementMode'] ?? 'normal') === 'overlay';\n            $zIndex = max(1, min(200, (int) ($props['zIndex'] ?? 20)));\n            $laptop .= self::geometryCss($selector, $lg, $laptopRows, $floating, $zIndex);\n            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);")
replace(rr,
"        foreach ($byParent[$id] ?? [] as $child) {\n            $childId = (string) ($child['id'] ?? '');",
"        foreach ($byParent[$id] ?? [] as $child) {\n            $childProps = is_array($child['props'] ?? null) ? $child['props'] : [];\n            if ((string) ($child['type'] ?? '') === 'button' && (string) ($child['parentId'] ?? '') !== '' && (string) ($childProps['placementMode'] ?? 'normal') === 'overlay') { continue; }\n            $childId = (string) ($child['id'] ?? '');")
old_gcss = """    /** @param array{x:int,y:int,w:int,h:int} $g */
    private static function geometryCss(string $selector, array $g, int $rows): string
    {
        $row = max(0, $g['y']) + 1;
        $rows = max(1, $rows);
        return $selector . '{grid-column:' . ($g['x'] + 1) . '/span ' . $g['w'] . '!important;'
            . 'grid-row:' . $row . '/span ' . $rows . '!important;'
            . 'min-height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;'
            . 'margin-top:0!important;}';
    }
"""
new_gcss = """    /** @param array{x:int,y:int,w:int,h:int} $g */
    private static function geometryCss(string $selector, array $g, int $rows, bool $floating = false, int $zIndex = 20): string
    {
        $rows = max(1, $rows);
        if ($floating) {
            $left = ($g['x'] / LayoutModel::UNITS) * 100;
            $width = ($g['w'] / LayoutModel::UNITS) * 100;
            return $selector . '{position:absolute!important;left:' . $left . '%!important;top:' . (max(0, $g['y']) * LayoutModel::ROW_PX) . 'px!important;'
                . 'width:' . $width . '%!important;height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;min-height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;'
                . 'z-index:' . max(1, min(200, $zIndex)) . '!important;grid-column:auto!important;grid-row:auto!important;margin-top:0!important;}';
        }
        $row = max(0, $g['y']) + 1;
        return $selector . '{grid-column:' . ($g['x'] + 1) . '/span ' . $g['w'] . '!important;'
            . 'grid-row:' . $row . '/span ' . $rows . '!important;'
            . 'min-height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;'
            . 'margin-top:0!important;}';
    }
"""
replace(rr, old_gcss, new_gcss)

# Version bump and release-facing docs.
mainphp = 'clean/hangar18-manager/hangar18-manager.php'
replace(mainphp, ' * Version: 0.1.28', ' * Version: 0.1.29')
replace(mainphp, "define('H18_CLEAN_VERSION', '0.1.28');", "define('H18_CLEAN_VERSION', '0.1.29');")

readme = 'clean/hangar18-manager/readme.txt'
replace(readme,
"Version: 0.1.28\nModeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.\n\n== 0.1.28 ==",
"Version: 0.1.29\nModeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.\n\n== 0.1.29 ==\n* Knap kan vælges som Normal eller Flydende i sin egen Sektion/Kasse.\n* Flydende Knap bruger canonical X/Y/W/H og kan overlappe Tekst, Billede og andre elementer uden at ændre det normale grid-flow.\n* Flydende Knap kan flyttes med drag-håndtaget eller X/Y og har Lag (z-index) 1-200.\n* Desktop/Laptop/Mobil bruger samme responsive geometrimodel; floating er aldrig position:fixed og bindes ikke til browser-vinduet.\n* 0.1.28 canvas-fix samt alle 0.1.26 WYSIWYG-, typografi-, Inspector-, billed-persistence- og Knap-auto-size rettelser bevares.\n\n== 0.1.28 ==")

notes = Path('clean-release-notes.html')
notes.write_text('<h4>0.1.29</h4><ul><li><strong>Flydende Knap:</strong> Knap kan skifte mellem Normal og Flydende placering inde i sin egen Sektion/Kasse.</li><li><strong>Fri overlap:</strong> Flydende Knap bruger canonical X/Y/W/H og må ligge oven på Tekst/Billede uden at skubbe det normale grid-layout eller udløse utilsigtet overlap-healing.</li><li><strong>Lag:</strong> Inspector har Lag (z-index 1-200), og knappen kan flyttes med ✥ eller X/Y.</li><li><strong>Responsive:</strong> Desktop/Laptop/Mobil bruger eksisterende responsive geometri. Floating er relativt til parent og er aldrig position:fixed til browser-vinduet.</li><li><strong>Regression:</strong> 0.1.28 canvas-fix samt 0.1.26 WYSIWYG, linjeskift, typografi, Inspector-scroll, billed-persistence og Knap-auto-size bevares.</li></ul>', encoding='utf-8')

# Button design spec: explicitly define floating as parent-relative overlay, never viewport fixed.
spec = Path('docs/BUTTON-ELEMENT-SPEC.md')
s = spec.read_text(encoding='utf-8')
anchor = "### Placering\n\nTeksten skal som standard være centreret både vandret og lodret i knappen.\n\nDer skal senere kunne vælges venstre/center/højre, især hvis knappen kombineres med ikon.\n"
replacement = "### Placering\n\nTeksten skal som standard være centreret både vandret og lodret i knappen.\n\nDer skal kunne vælges mellem:\n\n- **Normal i layout** – Knap deltager i det almindelige grid/cellelayout.\n- **Flydende i Sektion/Kasse** – Knap bruger sin X/Y/W/H-geometri som fri, parent-relativ placering og må overlappe andre elementer i samme Sektion/Kasse.\n\nFlydende betyder **ikke** `position:fixed` til browser-vinduet. Knappen følger sin Sektion/Kasse og siden under scroll. Flydende Knap skal have et Lag/z-index, så rækkefølgen ved overlap er entydig.\n\nDer skal senere kunne vælges venstre/center/højre, især hvis knappen kombineres med ikon.\n"
if s.count(anchor) != 1:
    raise SystemExit('BUTTON-ELEMENT-SPEC.md placement anchor not found exactly once')
spec.write_text(s.replace(anchor, replacement), encoding='utf-8')

print('0.1.29 floating button patch complete')
