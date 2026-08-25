from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing patch anchor in {path}: {old[:100]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


core = 'clean/hangar18-manager/assets/editor-v018-core.js'
model = 'clean/hangar18-manager/src/Model/LayoutModel.php'
renderer = 'clean/hangar18-manager/src/Frontend/Renderer.php'
plugin = 'clean/hangar18-manager/hangar18-manager.php'
readme = 'clean/hangar18-manager/readme.txt'
workflow = '.github/workflows/clean-release.yml'

# 1) Parent manual minimum height survives auto-grow/shrink cycles.
replace_once(
    core,
    """        if (PARENT_TYPES.includes(type)) {\n            return Object.assign(common, {\n                background: String(raw.background || ''),\n                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),\n                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120)\n            });\n        }\n""",
    """        if (PARENT_TYPES.includes(type)) {\n            return Object.assign(common, {\n                background: String(raw.background || ''),\n                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),\n                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),\n                minHeightRows: clamp(parseInt(raw.minHeightRows || 0, 10) || 0, 0, 4000)\n            });\n        }\n"""
)

replace_once(
    core,
    """                props: normalizeProps(type, item.props)\n            });\n        });\n        const map = {};\n""",
    """                props: normalizeProps(type, item.props)\n            });\n            const added = nodes[nodes.length - 1];\n            if (PARENT_TYPES.includes(type) && (!item.props || !Object.prototype.hasOwnProperty.call(item.props, 'minHeightRows'))) {\n                added.props.minHeightRows = added.geometry.desktop.h;\n            }\n        });\n        const map = {};\n"""
)

# 2) Materialize natural leaf heights into canonical 8 px rows, heal only collisions
# caused by that materialization, recursively auto-grow containers, and mark remaining
# deliberate/manual overlaps without blocking them yet.
anchor = """    function nextFreeY(parentId) {\n        let bottom = 0;\n        children(parentId).forEach(function (node) {\n            const g = node.geometry.desktop;\n            bottom = Math.max(bottom, g.y + (g.h > 0 ? g.h : MIN_SPLIT_H));\n        });\n        return bottom;\n    }\n\n"""
insert = anchor + """    function nodeDepth(node) {\n        let depth = 0;\n        let cursor = node;\n        const seen = {};\n        while (cursor && cursor.parentId && !seen[cursor.id]) {\n            seen[cursor.id] = true;\n            depth += 1;\n            cursor = nodeById(cursor.parentId);\n        }\n        return depth;\n    }\n\n    function materializeNaturalLeafHeights() {\n        const changed = new Set();\n        document.querySelectorAll('.h18-clean-node[data-node-id]').forEach(function (card) {\n            const node = nodeById(card.getAttribute('data-node-id') || '');\n            if (!node || PARENT_TYPES.includes(node.type) || node.geometry.desktop.h > 0) { return; }\n            const rect = card.getBoundingClientRect();\n            const rows = Math.max(1, Math.ceil(Math.max(1, rect.height) / ROW_PX));\n            node.geometry.desktop.h = rows;\n            changed.add(node.id);\n        });\n        return changed;\n    }\n\n    function healMaterializationCollisions(materialized) {\n        if (!materialized || !materialized.size) { return false; }\n        let changed = false;\n        const parents = Array.from(new Set(state.nodes.map(function (node) { return node.parentId; })));\n        parents.forEach(function (parentId) {\n            const list = children(parentId).slice().sort(function (a, b) {\n                if (a.geometry.desktop.y !== b.geometry.desktop.y) { return a.geometry.desktop.y - b.geometry.desktop.y; }\n                return a.order - b.order;\n            });\n            const placed = [];\n            list.forEach(function (node) {\n                const g = node.geometry.desktop;\n                if (!materialized.has(node.id) && !placed.some(function (other) { return materialized.has(other.id); })) {\n                    placed.push(node);\n                    return;\n                }\n                let guard = 0;\n                while (guard++ < 100) {\n                    const current = { x: g.x, y: g.y, w: g.w, h: Math.max(1, g.h || MIN_SPLIT_H) };\n                    let nextY = current.y;\n                    placed.forEach(function (other) {\n                        const og = other.geometry.desktop;\n                        const otherRect = { x: og.x, y: og.y, w: og.w, h: Math.max(1, og.h || MIN_SPLIT_H) };\n                        if (rectsOverlap(current, otherRect)) { nextY = Math.max(nextY, otherRect.y + otherRect.h); }\n                    });\n                    if (nextY === current.y) { break; }\n                    g.y = nextY;\n                    changed = true;\n                }\n                placed.push(node);\n            });\n        });\n        return changed;\n    }\n\n    function syncContainerHeights() {\n        let changed = false;\n        const parents = state.nodes.filter(function (node) { return PARENT_TYPES.includes(node.type); });\n        parents.sort(function (a, b) { return nodeDepth(b) - nodeDepth(a); });\n        parents.forEach(function (parent) {\n            const kids = children(parent.id);\n            let required = kids.length ? 0 : MIN_SPLIT_H;\n            kids.forEach(function (child) {\n                const g = child.geometry.desktop;\n                required = Math.max(required, Math.max(0, g.y) + Math.max(1, g.h || MIN_SPLIT_H));\n            });\n            const p = parent.props || {};\n            const extraPx = (Math.max(0, parseInt(p.padding || 0, 10) || 0) * 2) + (Math.max(0, parseInt(p.borderWidth || 0, 10) || 0) * 2);\n            required += Math.ceil(extraPx / ROW_PX);\n            const manualMin = clamp(parseInt(p.minHeightRows || 0, 10) || 0, 0, 4000);\n            const next = clamp(Math.max(manualMin, required), 1, 4000);\n            if (parent.geometry.desktop.h !== next) {\n                parent.geometry.desktop.h = next;\n                changed = true;\n            }\n        });\n        return changed;\n    }\n\n    function markOverlapWarnings() {\n        document.querySelectorAll('.h18-clean-node.has-layout-overlap').forEach(function (card) { card.classList.remove('has-layout-overlap'); });\n        const parents = Array.from(new Set(state.nodes.map(function (node) { return node.parentId; })));\n        parents.forEach(function (parentId) {\n            const list = children(parentId);\n            for (let i = 0; i < list.length; i += 1) {\n                for (let j = i + 1; j < list.length; j += 1) {\n                    const a = list[i].geometry.desktop;\n                    const b = list[j].geometry.desktop;\n                    const ar = { x: a.x, y: a.y, w: a.w, h: Math.max(1, a.h || MIN_SPLIT_H) };\n                    const br = { x: b.x, y: b.y, w: b.w, h: Math.max(1, b.h || MIN_SPLIT_H) };\n                    if (!rectsOverlap(ar, br)) { continue; }\n                    [list[i].id, list[j].id].forEach(function (id) {\n                        document.querySelectorAll('.h18-clean-node[data-node-id=\"' + CSS.escape(id) + '\"]').forEach(function (card) {\n                            card.classList.add('has-layout-overlap');\n                        });\n                    });\n                }\n            }\n        });\n    }\n\n    function reconcileLayoutAfterRender(canvas) {\n        const materialized = materializeNaturalLeafHeights();\n        const collisionHealed = healMaterializationCollisions(materialized);\n        const containersChanged = syncContainerHeights();\n        const changed = materialized.size > 0 || collisionHealed || containersChanged;\n        if (changed && canvas) {\n            renderSurface('', canvas);\n            if (undoStack.length) { undoStack[undoStack.length - 1].after = clone(state); }\n        }\n        markOverlapWarnings();\n        return changed;\n    }\n\n"""
replace_once(core, anchor, insert)

# Parent resize height is a user-selected minimum, while content may force effective h larger.
replace_once(
    core,
    """        commit(current.before, 'Resize ' + current.id);\n        const node = nodeById(current.id);\n""",
    """        const resizedNode = nodeById(current.id);\n        if (resizedNode && PARENT_TYPES.includes(resizedNode.type)) {\n            resizedNode.props.minHeightRows = resizedNode.geometry.desktop.h;\n        }\n        commit(current.before, 'Resize ' + current.id);\n        const node = nodeById(current.id);\n"""
)

replace_once(
    core,
    """                else if (field === 'gh') { current.geometry.desktop.h = clamp(parseInt(control.value || 0, 10) || 0, 0, 4000); }\n""",
    """                else if (field === 'gh') {\n                    current.geometry.desktop.h = clamp(parseInt(control.value || 0, 10) || 0, 0, 4000);\n                    if (PARENT_TYPES.includes(current.type)) { current.props.minHeightRows = current.geometry.desktop.h; }\n                }\n"""
)

replace_once(
    core,
    """        if (canvas) { renderSurface('', canvas); }\n        renderInspector();\n        updateHidden();\n""",
    """        if (canvas) {\n            renderSurface('', canvas);\n            reconcileLayoutAfterRender(canvas);\n        }\n        renderInspector();\n        updateHidden();\n"""
)

# 3) Server model persists the explicit minimum and migrates old parent h into it.
replace_once(
    model,
    """            $nodes[$id] = [\n                'id' => $id,\n                'type' => $type,\n                'parentId' => self::cleanId($nodeRaw['parentId'] ?? ''),\n                'order' => self::clamp($nodeRaw['order'] ?? (($index + 1) * 10), 1, 100000, ($index + 1) * 10),\n                'geometry' => self::geometry(isset($nodeRaw['geometry']) && is_array($nodeRaw['geometry']) ? $nodeRaw['geometry'] : []),\n                'props' => self::props($type, isset($nodeRaw['props']) && is_array($nodeRaw['props']) ? $nodeRaw['props'] : []),\n            ];\n""",
    """            $nodes[$id] = [\n                'id' => $id,\n                'type' => $type,\n                'parentId' => self::cleanId($nodeRaw['parentId'] ?? ''),\n                'order' => self::clamp($nodeRaw['order'] ?? (($index + 1) * 10), 1, 100000, ($index + 1) * 10),\n                'geometry' => self::geometry(isset($nodeRaw['geometry']) && is_array($nodeRaw['geometry']) ? $nodeRaw['geometry'] : []),\n                'props' => self::props($type, isset($nodeRaw['props']) && is_array($nodeRaw['props']) ? $nodeRaw['props'] : []),\n            ];\n            if (in_array($type, ['section', 'container'], true) && (!isset($nodeRaw['props']) || !is_array($nodeRaw['props']) || !array_key_exists('minHeightRows', $nodeRaw['props']))) {\n                $nodes[$id]['props']['minHeightRows'] = (int) $nodes[$id]['geometry']['desktop']['h'];\n            }\n"""
)

replace_once(
    model,
    """                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),\n            ], $border);\n""",
    """                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),\n                'minHeightRows' => self::clamp($raw['minHeightRows'] ?? 0, 0, 4000, 0),\n            ], $border);\n"""
)

# 4) Frontend fallback for old h=0 layouts until they have been opened/saved in 0.1.10.
replace_once(
    renderer,
    """            $childHeight = $h * LayoutModel::ROW_PX;\n            if (in_array((string) ($child['type'] ?? ''), ['section', 'container'], true)) {\n                $childHeight = max($childHeight, self::requiredChildHeightPx((string) ($child['id'] ?? ''), $byParent));\n            }\n""",
    """            $type = (string) ($child['type'] ?? '');\n            if ($h > 0) {\n                $childHeight = $h * LayoutModel::ROW_PX;\n            } elseif ($type === 'image') {\n                $childHeight = 10 * LayoutModel::ROW_PX;\n            } elseif ($type === 'text') {\n                $childHeight = 6 * LayoutModel::ROW_PX;\n            } else {\n                $childHeight = 8 * LayoutModel::ROW_PX;\n            }\n            if (in_array($type, ['section', 'container'], true)) {\n                $childHeight = max($childHeight, self::requiredChildHeightPx((string) ($child['id'] ?? ''), $byParent));\n            }\n"""
)

# 5) Load the 0.1.10 CSS and bump package version.
replace_once(plugin, ' * Version: 0.1.9', ' * Version: 0.1.10')
replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.9');", "define('H18_CLEAN_VERSION', '0.1.10');")
replace_once(
    plugin,
    """     * 0.1.9 keeps the 0.1.8 cell-split editor runtime, now nested below the\n     * Clean Manager admin. Save/Restore and diagnostics contracts are unchanged.\n""",
    """     * 0.1.10 reconciles natural element height into canonical 8 px rows and\n     * auto-grows nested containers while keeping the 0.1.8 cell-split model.\n"""
)
replace_once(
    plugin,
    """    wp_enqueue_style(\n        'h18-clean-editor-v018',\n        H18_CLEAN_URL . 'assets/editor-v018.css',\n        ['h18-clean-editor-v016'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_script(\n""",
    """    wp_enqueue_style(\n        'h18-clean-editor-v018',\n        H18_CLEAN_URL . 'assets/editor-v018.css',\n        ['h18-clean-editor-v016'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0110',\n        H18_CLEAN_URL . 'assets/editor-v0110.css',\n        ['h18-clean-editor-v018'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_script(\n"""
)

# 6) Release documentation.
replace_once(readme, 'Version: 0.1.9', 'Version: 0.1.10')
replace_once(
    readme,
    '== 0.1.9 ==\n',
    """== 0.1.10 ==\n* Elementer med naturlig h=0 materialiseres nu til deres faktiske højde i hele 8-px-rækker, så gridet reserverer den plads der faktisk tegnes.\n* Kasse/Sektion beregner effektiv højde rekursivt ud fra alle direkte børn og vokser automatisk efter drop, reparent, resize, delete og reload.\n* Manuel højde på Kasse/Sektion gemmes separat som minHeightRows og fungerer som minimum; indhold kan gøre kassen højere, og den kan krympe tilbage til minimum når indhold fjernes.\n* Kollisions-heal flytter kun elementer der kolliderer som følge af automatisk materialisering af tidligere h=0-geometri.\n* Bevidst/manuelt overlap er foreløbig stadig tilladt, men markeres tydeligt med OVERLAP-advarsel i editoren, så vi kan beslutte den endelige policy efter test.\n* Frontend har fallback-højder for ældre h=0-layouts, indtil de er gemt igen med canonical 0.1.10-geometri.\n\n== 0.1.9 ==\n"""
)

Path('clean-release-notes.html').write_text(
    '<h4>0.1.10</h4><ul>'
    '<li>Naturlige h=0-elementer materialiseres til faktiske 8-px grid-rækker, så visuel højde og canonical geometri matcher.</li>'
    '<li>Kasse/Sektion auto-grow beregnes rekursivt fra børn; manuelt valgt højde bevares som minimum og kassen kan krympe tilbage til minimum.</li>'
    '<li>Automatiske h=0-kollisioner heales, mens manuelt overlap foreløbig stadig er muligt og markeres tydeligt med OVERLAP-advarsel.</li>'
    '<li>Frontend har kompatibilitetsfallback for ældre h=0-layouts.</li>'
    '</ul>\n',
    encoding='utf-8'
)

# 7) Release QA verifies the new style asset is actually packaged.
replace_once(
    workflow,
    """          test -s clean/hangar18-manager/assets/editor-v018.css\n""",
    """          test -s clean/hangar18-manager/assets/editor-v018.css\n          test -s clean/hangar18-manager/assets/editor-v0110.css\n"""
)

# Trigger normal SHA-verified Clean release pipeline from the patch commit.
Path('clean-release-now.txt').write_text(
    'v0.1.10\ntriggered_utc=2026-08-25T16:25:00Z\nreason=Canonical natural-height materialization, recursive container auto-grow and visible overlap diagnostics.\nnonce=10\n',
    encoding='utf-8'
)

print('Clean v0.1.10 patch applied successfully.')
