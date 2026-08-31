from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f'{rel}: expected exactly one marker, found {count}: {old[:100]!r}')
    write(rel, value.replace(old, new, 1))


def append_once(rel: str, marker: str, block: str) -> None:
    value = read(rel)
    if marker in value:
        return
    if value and not value.endswith('\n'):
        value += '\n'
    write(rel, value + '\n' + block.strip() + '\n')


# ---------------------------------------------------------------------------
# Runtime version + bootstrap
# ---------------------------------------------------------------------------
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    ' * Version: 0.1.67',
    ' * Version: 0.1.68',
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "define('H18_CLEAN_VERSION', '0.1.67');",
    "define('H18_CLEAN_VERSION', '0.1.68');",
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/CanvasSectionMigration.php';\n",
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "    \\VisualDesignerManager\\Modules\\ModuleStore::register();\n",
    "    \\VisualDesignerManager\\Modules\\ModuleStore::register();\n    \\VisualDesignerManager\\Migration\\CanvasSectionMigration::register();\n",
)


# ---------------------------------------------------------------------------
# Canonical hierarchy validator shared by migration + QA
# ---------------------------------------------------------------------------
normalizer_method = r'''
    /**
     * Returns true only when the node graph obeys the canonical page contract:
     * PAGE -> SECTION -> (CONTAINER|LEAF), with nested CONTAINER allowed.
     *
     * @param array<int|string,array<string,mixed>> $nodes
     */
    public static function isCanonical(array $nodes): bool
    {
        $map = [];
        foreach ($nodes as $key => $node) {
            if (!is_array($node)) {
                return false;
            }
            $id = (string) ($node['id'] ?? (is_string($key) ? $key : ''));
            if ($id === '' || isset($map[$id])) {
                return false;
            }
            $map[$id] = $node;
        }

        foreach ($map as $id => $node) {
            $type = (string) ($node['type'] ?? '');
            $parent = (string) ($node['parentId'] ?? '');

            if ($type === 'section') {
                if ($parent !== '') {
                    return false;
                }
                continue;
            }
            if ($parent === '') {
                return false;
            }

            $seen = [];
            $cursor = $id;
            while (isset($map[$cursor])) {
                if (isset($seen[$cursor])) {
                    return false;
                }
                $seen[$cursor] = true;
                $current = $map[$cursor];
                $currentType = (string) ($current['type'] ?? '');
                $currentParent = (string) ($current['parentId'] ?? '');
                if ($currentParent === '') {
                    if ($currentType !== 'section') {
                        return false;
                    }
                    break;
                }
                if (!isset($map[$currentParent])) {
                    return false;
                }
                $parentType = (string) ($map[$currentParent]['type'] ?? '');
                if (!in_array($parentType, ['section', 'container'], true)) {
                    return false;
                }
                $cursor = $currentParent;
            }
        }

        return true;
    }

'''
replace_once(
    'clean/hangar18-manager/src/Model/HierarchyNormalizer.php',
    "    /** @param array<string,array<string,mixed>> $nodes */\n    private static function uniqueWrapperId",
    normalizer_method + "    /** @param array<string,array<string,mixed>> $nodes */\n    private static function uniqueWrapperId",
)


# ---------------------------------------------------------------------------
# One-time, rollback-safe persistent migration of existing Designer pages.
# ---------------------------------------------------------------------------
migration_php = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\HierarchyNormalizer;
use VisualDesignerManager\Model\LayoutModel;

/**
 * v0.1.68 persistent migration for existing Visual Designer pages.
 *
 * LayoutModel::get() has long normalized legacy root elements in memory. This
 * migration makes that hierarchy permanent in post meta without asking the
 * editor to open and save every page manually.
 */
final class CanvasSectionMigration
{
    public const TARGET_VERSION = '0.1.68';
    public const OPTION = 'h18_vd_canvas_section_migration_v0168';
    public const BACKUP_META = '_h18_clean_layout_pre_section_v0168';
    public const NOTE = 'Automatisk migrering til Section-struktur (v0.1.68)';

    public static function register(): void
    {
        if (is_admin()) {
            add_action('admin_init', [self::class, 'maybeRun'], 5);
        }
    }

    public static function maybeRun(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        if (function_exists('wp_doing_ajax') && wp_doing_ajax()) {
            return;
        }

        $previous = get_option(self::OPTION, []);
        if (is_array($previous)
            && (string) ($previous['version'] ?? '') === self::TARGET_VERSION
            && empty($previous['failed'])) {
            return;
        }

        $postIds = get_posts([
            'post_type' => 'page',
            'post_status' => ['publish', 'draft', 'pending', 'private', 'future'],
            'posts_per_page' => -1,
            'fields' => 'ids',
            'orderby' => 'ID',
            'order' => 'ASC',
            'meta_key' => LayoutModel::META,
            'no_found_rows' => true,
            'suppress_filters' => false,
        ]);
        $postIds = is_array($postIds) ? array_values(array_map('absint', $postIds)) : [];

        $result = [
            'version' => self::TARGET_VERSION,
            'ranUtc' => gmdate('c'),
            'migrated' => 0,
            'skipped' => 0,
            'failed' => [],
        ];

        foreach ($postIds as $postId) {
            $raw = get_post_meta($postId, LayoutModel::META, true);
            if (!is_array($raw) || !self::needsMigration($raw)) {
                $result['skipped']++;
                continue;
            }

            $historyExists = metadata_exists('post', $postId, LayoutModel::HISTORY_META);
            $versionExists = metadata_exists('post', $postId, LayoutModel::VERSION_META);
            $historyBefore = get_post_meta($postId, LayoutModel::HISTORY_META, true);
            $versionBefore = get_post_meta($postId, LayoutModel::VERSION_META, true);
            $mutated = false;

            try {
                self::writeRawBackupOnce($postId, $raw);
                $originalIds = self::nodeIds($raw);
                $normalized = LayoutModel::normalize($raw);
                if (!HierarchyNormalizer::isCanonical((array) ($normalized['nodes'] ?? []))) {
                    throw new \RuntimeException('Canonical Section-struktur kunne ikke verificeres.');
                }
                self::assertIdsPreserved($originalIds, $normalized);

                $mutated = true;
                LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), self::NOTE);

                $saved = get_post_meta($postId, LayoutModel::META, true);
                if (!is_array($saved) || !HierarchyNormalizer::isCanonical((array) ($saved['nodes'] ?? []))) {
                    throw new \RuntimeException('Gemte layoutdata bestod ikke Section-verifikation.');
                }
                self::assertIdsPreserved($originalIds, $saved);
                clean_post_cache($postId);
                $result['migrated']++;
            } catch (\Throwable $error) {
                if ($mutated) {
                    update_post_meta($postId, LayoutModel::META, $raw);
                    self::restoreMeta($postId, LayoutModel::HISTORY_META, $historyExists, $historyBefore);
                    self::restoreMeta($postId, LayoutModel::VERSION_META, $versionExists, $versionBefore);
                    clean_post_cache($postId);
                }
                $result['failed'][] = [
                    'postId' => $postId,
                    'message' => sanitize_text_field($error->getMessage()),
                ];
            }
        }

        update_option(self::OPTION, $result, false);
    }

    /** @param array<string,mixed> $model */
    public static function needsMigration(array $model): bool
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        if (!$nodes) {
            return false;
        }

        $map = [];
        foreach ($nodes as $node) {
            if (!is_array($node)) {
                return true;
            }
            $id = self::cleanId($node['id'] ?? '');
            if ($id === '' || isset($map[$id])) {
                return true;
            }
            $map[$id] = [
                'type' => sanitize_key((string) ($node['type'] ?? '')),
                'parentId' => self::cleanId($node['parentId'] ?? ''),
            ];
        }

        foreach ($map as $id => $node) {
            $type = (string) $node['type'];
            $parent = (string) $node['parentId'];
            if ($type === 'section') {
                if ($parent !== '') {
                    return true;
                }
                continue;
            }
            if ($parent === '') {
                return true;
            }
            if (!isset($map[$parent]) || !in_array((string) $map[$parent]['type'], ['section', 'container'], true)) {
                return true;
            }

            $seen = [];
            $cursor = $id;
            while ($cursor !== '') {
                if (isset($seen[$cursor]) || !isset($map[$cursor])) {
                    return true;
                }
                $seen[$cursor] = true;
                $cursor = (string) $map[$cursor]['parentId'];
            }
        }

        return false;
    }

    /** @param array<string,mixed> $raw */
    private static function writeRawBackupOnce(int $postId, array $raw): void
    {
        if (metadata_exists('post', $postId, self::BACKUP_META)) {
            return;
        }
        $json = wp_json_encode($raw, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        update_post_meta($postId, self::BACKUP_META, [
            'version' => self::TARGET_VERSION,
            'savedUtc' => gmdate('c'),
            'digest' => hash('sha256', is_string($json) ? $json : ''),
            'model' => $raw,
        ]);
    }

    /** @param array<string,mixed> $model @return array<int,string> */
    private static function nodeIds(array $model): array
    {
        $ids = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) {
                continue;
            }
            $id = self::cleanId($node['id'] ?? '');
            if ($id !== '') {
                $ids[$id] = true;
            }
        }
        return array_keys($ids);
    }

    /** @param array<int,string> $originalIds @param array<string,mixed> $model */
    private static function assertIdsPreserved(array $originalIds, array $model): void
    {
        $saved = array_fill_keys(self::nodeIds($model), true);
        foreach ($originalIds as $id) {
            if (!isset($saved[$id])) {
                throw new \RuntimeException('Migreringen ville miste element-ID: ' . $id);
            }
        }
    }

    /** @param mixed $value */
    private static function restoreMeta(int $postId, string $key, bool $existed, $value): void
    {
        if ($existed) {
            update_post_meta($postId, $key, $value);
        } else {
            delete_post_meta($postId, $key);
        }
    }

    /** @param mixed $value */
    private static function cleanId($value): string
    {
        return substr(strtolower((string) preg_replace('/[^a-z0-9._-]/i', '', (string) $value)), 0, 100);
    }
}
'''
write('clean/hangar18-manager/src/Migration/CanvasSectionMigration.php', migration_php)


# ---------------------------------------------------------------------------
# Editor runtime: canonical hierarchy at all times, not only on server save.
# ---------------------------------------------------------------------------
js_helpers = r'''
    function hierarchyLocalGeometry(geometry) {
        geometry = geometry && typeof geometry === 'object' ? geometry : {};
        const desktopSource = normalizeDevice(geometry.desktop, false);
        const result = {
            desktop: { x: 0, y: 0, w: UNITS, h: desktopSource.h }
        };
        ['laptop', 'tablet', 'mobile'].forEach(function (key) {
            const source = normalizeDevice(geometry[key], true);
            const inherit = source.inheritDesktop !== false;
            result[key] = { x: 0, y: 0, w: UNITS, h: inherit ? desktopSource.h : source.h, inheritDesktop: inherit };
        });
        return result;
    }

    function hierarchyWrapperId(sourceId, map) {
        const tail = cleanId(sourceId).slice(-70) || 'element';
        const base = cleanId('section-migrated-' + tail) || 'section-migrated';
        let candidate = base;
        let suffix = 2;
        while (map[candidate]) {
            candidate = cleanId(base.slice(0, 92) + '-' + String(suffix));
            suffix += 1;
        }
        return candidate;
    }

    function normalizeCanvasHierarchy(nodes) {
        const map = {};
        nodes.forEach(function (node) { map[node.id] = node; });

        // Sektion is page-level only. Historical nested sections are losslessly
        // treated as Kasser, matching the server HierarchyNormalizer contract.
        nodes.forEach(function (node) {
            if (node.type === 'section' && node.parentId) {
                node.type = 'container';
                node.props = normalizeProps('container', node.props || {});
            }
        });

        const roots = nodes.filter(function (node) { return !node.parentId && node.type !== 'section'; });
        roots.forEach(function (node) {
            const oldGeometry = clone(node.geometry || {});
            const wrapperId = hierarchyWrapperId(node.id, map);
            const gapX = clamp(parseInt(node.props && node.props.gapX || 0, 10) || 0, 0, 200);
            const gapY = clamp(parseInt(node.props && node.props.gapY || 0, 10) || 0, 0, 200);
            const wrapper = {
                id: wrapperId,
                type: 'section',
                parentId: '',
                order: Math.max(1, parseInt(node.order || 10, 10) || 10),
                geometry: clone(oldGeometry),
                props: normalizeProps('section', { gapX: gapX, gapY: gapY, minHeightRows: 0 })
            };
            map[wrapperId] = wrapper;
            nodes.push(wrapper);
            if (node.props) { node.props.gapX = 0; node.props.gapY = 0; }
            node.parentId = wrapperId;
            node.order = 10;
            node.geometry = hierarchyLocalGeometry(oldGeometry);
        });

        return nodes;
    }

'''
replace_once(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    '    function normalizeModel(raw) {\n',
    js_helpers + '    function normalizeModel(raw) {\n',
)
replace_once(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "        return { schemaVersion: 1, units: UNITS, rowPx: ROW_PX, nodes: nodes };\n    }\n\n    function mapById()",
    "        normalizeCanvasHierarchy(nodes);\n        return { schemaVersion: 1, units: UNITS, rowPx: ROW_PX, nodes: nodes };\n    }\n\n    function mapById()",
)
replace_once(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "        const placement = dropGeometry && typeof dropGeometry === 'object' ? dropGeometry : null;\n        parentId = cleanId(placement && placement.parentId != null ? placement.parentId : parentId || '');\n        const parent = parentId ? nodeById(parentId) : null;",
    "        let placement = dropGeometry && typeof dropGeometry === 'object' ? dropGeometry : null;\n        parentId = cleanId(placement && placement.parentId != null ? placement.parentId : parentId || '');\n        if (type === 'section' && parentId) { parentId = ''; placement = null; }\n        const parent = parentId ? nodeById(parentId) : null;",
)
replace_once(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "        applyDestinationGeometry(id, p);\n        selectedId = id;",
    "        applyDestinationGeometry(id, p);\n        state = normalizeModel(state);\n        selectedId = id;",
)
replace_once(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "        if (parentId === id || descendants(id).includes(parentId)) { return; }\n\n        const before = clone(state);",
    "        if (parentId === id || descendants(id).includes(parentId)) { return; }\n        if (node.type === 'section' && parentId) { productivityNotice('Sektioner kan kun ligge direkte på websiden'); return; }\n\n        const before = clone(state);",
)
replace_once(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "        node.geometry.desktop.w = Math.min(UNITS, Math.max(1, node.geometry.desktop.w));\n        commit(before, 'Flyt ' + typeLabel(node.type) + ' · ' + placement.zone);",
    "        node.geometry.desktop.w = Math.min(UNITS, Math.max(1, node.geometry.desktop.w));\n        state = normalizeModel(state);\n        commit(before, 'Flyt ' + typeLabel(node.type) + ' · ' + placement.zone);",
)


# ---------------------------------------------------------------------------
# Editor-only layer policy: selected/dragged/resized node and its stacking
# ancestors are lifted without mutating canonical/frontend zIndex.
# ---------------------------------------------------------------------------
replace_once(
    'clean/hangar18-manager/assets/editor.css',
    ".h18-clean-node.is-selected{outline:2px solid #2271b1;outline-offset:1px;z-index:5}\n.h18-clean-node.is-dragging{opacity:.45}\n.h18-clean-node.is-resizing{z-index:20;box-shadow:0 0 0 2px #2271b1}",
    ".h18-clean-node:has(.h18-clean-node.is-selected),.h18-clean-node:has(.h18-clean-node.is-dragging),.h18-clean-node:has(.h18-clean-node.is-resizing){z-index:9000!important}\n.h18-clean-node.is-selected{outline:2px solid #2271b1;outline-offset:1px;z-index:10000!important}\n.h18-clean-node.is-dragging{opacity:.55;z-index:11000!important}\n.h18-clean-node.is-resizing{z-index:12000!important;box-shadow:0 0 0 2px #2271b1}",
)


# ---------------------------------------------------------------------------
# Release history, manuals and backlog
# ---------------------------------------------------------------------------
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions') if isinstance(history, dict) else None
if not isinstance(versions, list):
    raise RuntimeError('release-history.json: missing versions list')
if not any(isinstance(row, dict) and row.get('version') == '0.1.68' for row in versions):
    versions.insert(0, {
        'version': '0.1.68',
        'date': '2026-08-31',
        'items': [
            'VD-CANVAS-SECTION-001: Webside-root må kun indeholde Sektioner; Kasser og leaf-elementer ligger altid under en Sektion.',
            'Eksisterende Designer-sider migreres automatisk og rollback-sikkert med rå v0.1.68-backup samt ny Designer-version.',
            'Editor-runtime normaliserer samme hierarki ved add, paste, undo/redo og re-parent, så nye løse root-elementer ikke kan opstå.',
            'VD-SELECTION-LAYER-001: markeret, trukket eller resized element løftes midlertidigt øverst i Designeren uden at ændre frontend z-index.'
        ]
    })
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '''<h4>0.1.68 – Canvas/Section Structure</h4>
<ul>
<li>Alle Designer-sider følger nu canonical Webside → Sektion → Kasse/Element.</li>
<li>Eksisterende sider migreres automatisk med rå backup, ID-bevarelse, rollback og ny Designer-version.</li>
<li>Nye root-elementer pakkes automatisk i en Sektion; Sektioner kan kun ligge direkte på websiden.</li>
<li>Markerede, trukne og resized elementer ligger midlertidigt øverst i Designeren uden at ændre frontendens z-index.</li>
<li>Køretøjsmodulet flyttes til næste version oven på den færdige Canvas/Section-kontrakt.</li>
</ul>
''')

append_once('CLEAN-DESIGN-MANUAL.md', '## 27. Canvas/Section-struktur', r'''
## 27. Canvas/Section-struktur

Den canonical sideanatomi er **Webside/Canvas → Sektion → Kasse eller indholdselement**. Kun Sektion må ligge direkte på Webside/Canvas. Kasser, Tekst, Billede, Knap, Menu, Tabel, Data List og andre leaf-elementer skal derfor altid have en Sektion som øverste layoutforælder. Kasser kan fortsat nestes i Sektion/Kasse.

Når et eksisterende legacy-layout har et element direkte på root, opretter normalizeren en neutral Sektion omkring elementet og flytter root-geometri og ekstern spacing til Sektionen. Elementets ID og synlige placering bevares. En historisk nested Sektion konverteres tabsfrit til Kasse.

Fra v0.1.68 bliver denne normalisering også persisteret automatisk for eksisterende Designer-sider. Hver berørt side får en rå pre-migration-backup og en ny Designer-version. Migreringen må kun committe, hvis alle oprindelige element-ID'er stadig findes og den nye model består canonical hierarchy-validering.

I editoren er lagløft under redigering en **ren UI-egenskab**: markeret element, drag og resize må midlertidigt ligge foran andre elementer og løfte nødvendige ancestor stacking contexts. Det må aldrig ændre elementets canonical `zIndex` eller frontendens lagrækkefølge.
''')

append_once('CLEAN-TECHNICAL-MANUAL.md', 'VD-CANVAS-SECTION-001', r'''
## VD-CANVAS-SECTION-001 – Canonical Canvas/Section hierarchy

- Root på en almindelig Designer-side må kun indeholde `section`.
- `container` og alle leaf-typer skal have ancestry, der ender i en root-`section`.
- `HierarchyNormalizer::normalize()` wrapper legacy root-noder i en neutral Sektion og konverterer nested Sektion til Kasse.
- `HierarchyNormalizer::isCanonical()` er den fælles verifieringskontrakt for migration/QA.
- `CanvasSectionMigration` kører én gang i Admin for sider med `_h18_clean_layout_v1`, gemmer `_h18_clean_layout_pre_section_v0168`, bevarer alle oprindelige node-ID'er og gemmer migrationen som en ny Designer-version.
- Ved validerings- eller save-fejl gendannes current model, history og version-meta til før migreringen.
- Editorens JavaScript-normalizer håndhæver samme root-kontrakt ved runtime, så add/paste/re-parent ikke kan efterlade løse root-elementer.

## VD-SELECTION-LAYER-001 – Editor-only active layer

Markeret element og element under drag/resize skal ligge øverst i Designerens stacking context. Ancestor wrappers løftes samtidig, så et markeret child ikke kan skjules bag en sibling-Kasse/Sektion. Lagløftet implementeres kun i editor-CSS og må ikke persistére eller ændre frontendens canonical `zIndex`.
''')

append_once('CLEAN-USER-MANUAL.md', '### Automatisk Section-struktur fra v0.1.68', r'''
### Automatisk Section-struktur fra v0.1.68

Visual Designer sørger automatisk for, at en side er bygget som **Webside → Sektion → Kasse/Element**. Du behøver ikke selv åbne gamle sider og flytte løse elementer ind i Sektioner. Ved opdatering konverteres berørte Designer-sider automatisk med backup og en ny sideversion.

Hvis du trækker et almindeligt element ud på selve websiden, opretter Designer den nødvendige Sektion automatisk. En Sektion kan kun ligge direkte på websiden. Når et element er markeret, flyttes det visuelt øverst under redigering/drag/resize; dette ændrer ikke den publicerede sides lagrækkefølge.
''')

backlog = read('docs/clean-backlog-v0100.md')
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.67', '## Aktuel milepælsstatus · v0.1.68', 1)
backlog = backlog.replace(
    '- **VD-MODULE-DATA-001 — IMPLEMENTERET I v0.1.67:** fælles ModuleRegistry, ModuleRecord, ModuleBinding og privat ModuleStore er fundamentet for Køretøjer, Events og Billedgalleri.\n- **Næste modul:** Køretøjer bygges først oven på den fælles modularkitektur; derefter Events og Billedgalleri.',
    '- **VD-MODULE-DATA-001 — IMPLEMENTERET I v0.1.67:** fælles ModuleRegistry, ModuleRecord, ModuleBinding og privat ModuleStore er fundamentet for Køretøjer, Events og Billedgalleri.\n- **VD-CANVAS-SECTION-001 / VD-SELECTION-LAYER-001 — IMPLEMENTERET I v0.1.68:** root er kun Sektioner, eksisterende sider migreres automatisk, og markeret/drag/resize løftes kun i editorlaget.\n- **Næste modul:** Køretøjer bygges i v0.1.69 oven på den fælles modularkitektur og den låste Canvas/Section-kontrakt; derefter Events og Billedgalleri.',
    1,
)
backlog = backlog.replace(
    '- Elementet kan trækkes ud til root igen.\n',
    '- Elementet kan trækkes ud mod root; Designer opretter automatisk en neutral Sektion, så root fortsat kun indeholder Sektioner.\n',
    1,
)
backlog = backlog.replace(
    '- Fra v0.1.1 kan nye palette-elementer trækkes direkte til root, Sektion eller Kasse.\n',
    '- Nye palette-elementer kan slippes på websiden, Sektion eller Kasse; drop på websiden auto-wrapper ikke-Sektioner i en neutral Sektion.\n',
    1,
)
backlog = backlog.replace('## Roadmap fra v0.1.67', '## Roadmap fra v0.1.68', 1)
backlog = backlog.replace(
    '1. **v0.1.67 – Module/Data Foundation:** registry, canonical recordmodel, private datastore og binding-kontrakt.\n2. **Næste – Køretøjsmodul:** Manager-CRUD, fleksible tekniske datafelter, billeder, sortering og Designer-modul-elementer til liste/detail.\n3. **Derefter – Events:** samme data-/bindingarkitektur med dato, sted, status og eventvisninger.\n4. **Derefter – Billedgalleri:** album/medier på samme modulstore og genbrugelige Designer-visninger.\n5. Dynamisk binding aktiveres først i de konkrete modulelementer; v0.1.67 ændrer ikke eksisterende statiske Data List/Tabel-renderinger.',
    '1. **v0.1.67 – Module/Data Foundation:** registry, canonical recordmodel, private datastore og binding-kontrakt.\n2. **v0.1.68 – Canvas/Section Structure:** root kun Sektioner, automatisk persist-migration og editor-only active layer.\n3. **v0.1.69 – Køretøjsmodul:** Manager-CRUD, fleksible tekniske datafelter, billeder, sortering og Designer-modul-elementer til liste/detail.\n4. **Derefter – Events:** samme data-/bindingarkitektur med dato, sted, status og eventvisninger.\n5. **Derefter – Billedgalleri:** album/medier på samme modulstore og genbrugelige Designer-visninger.\n6. Dynamisk binding aktiveres først i de konkrete modulelementer; v0.1.67 ændrede ikke eksisterende statiske Data List/Tabel-renderinger.',
    1,
)
backlog = backlog.replace('5. Træk eksisterende Tekst ind i Kasse og ud til root igen.', '5. Træk eksisterende Tekst ind i Kasse og ud mod websiden igen; verificér at Designer automatisk opretter en Sektion omkring elementet.', 1)
write('docs/clean-backlog-v0100.md', backlog)

write('docs/v0168-status.md', '''# Visual Designer Manager v0.1.68 – Canvas/Section Structure\n\nStatus: TESTKANDIDAT\n\n## Scope\n- VD-CANVAS-SECTION-001: root kun Sektioner.\n- Automatisk persistent migration af eksisterende Designer-sider med rå backup, ID-verifikation og rollback.\n- JavaScript runtime-normalisering af add/paste/re-parent.\n- VD-SELECTION-LAYER-001: valgt/drag/resize øverst kun i editoren.\n- Køretøjsmodulet er flyttet til v0.1.69 og er ikke del af denne release.\n\n## Migration\nFørste admin-request efter opdatering gennemgår sider med `_h18_clean_layout_v1`. Kun sider der bryder hierarchy-kontrakten gemmes på ny. Hver berørt side får `_h18_clean_layout_pre_section_v0168` samt en ny Designer-version med note `Automatisk migrering til Section-struktur (v0.1.68)`.\n\n## QA\n- Alle eksisterende regressionstests skal være grønne.\n- Hierarchy-normalisering skal være idempotent.\n- Alle oprindelige node-ID'er skal overleve migreringen.\n- Root må efter normalisering kun indeholde `section`.\n- Nested `section` må ikke overleve som `section`; den bliver `container`.\n- Selected/drag/resize layer må ikke ændre Renderer eller canonical `zIndex`.\n''')

print('Applied Visual Designer Manager v0.1.68 Canvas/Section Structure source changes.')
