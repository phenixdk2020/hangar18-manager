from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]


def text(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise AssertionError(f'missing file: {rel}')
    return path.read_text(encoding='utf-8')


def require(rel: str, needles: list[str]) -> None:
    value = text(rel)
    missing = [needle for needle in needles if needle not in value]
    if missing:
        raise AssertionError(f'{rel} missing {missing}')


def version_at_least(plugin: str, minimum: tuple[int, int, int]) -> bool:
    match = re.search(r'Version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)\b', plugin)
    return bool(match and tuple(map(int, match.groups())) >= minimum)


try:
    plugin = text('clean/hangar18-manager/hangar18-manager.php')
    if not version_at_least(plugin, (0, 1, 68)):
        raise AssertionError('plugin version is older than 0.1.68')

    require('clean/hangar18-manager/hangar18-manager.php', [
        "src/Migration/CanvasSectionMigration.php",
        "CanvasSectionMigration::register()",
    ])
    require('clean/hangar18-manager/src/Model/HierarchyNormalizer.php', [
        'public static function isCanonical(array $nodes): bool',
        "PAGE -> SECTION -> (CONTAINER|LEAF)",
        "'type' => 'section'",
        "node['type'] = 'container'",
    ])
    require('clean/hangar18-manager/src/Migration/CanvasSectionMigration.php', [
        "TARGET_VERSION = '0.1.68'",
        "BACKUP_META = '_h18_clean_layout_pre_section_v0168'",
        "Automatisk migrering til Section-struktur (v0.1.68)",
        "meta_key' => LayoutModel::META",
        'LayoutModel::saveVersion(',
        'HierarchyNormalizer::isCanonical(',
        'self::assertIdsPreserved(',
        'self::restoreMeta(',
        'clean_post_cache($postId)',
    ])
    require('clean/hangar18-manager/assets/editor-v018-core.js', [
        'function normalizeCanvasHierarchy(nodes)',
        'function hierarchyLocalGeometry(geometry)',
        'function hierarchyWrapperId(sourceId, map)',
        'normalizeCanvasHierarchy(nodes);',
        "if (type === 'section' && parentId) { parentId = ''; placement = null; }",
        "Sektioner kan kun ligge direkte på websiden",
        'state = normalizeModel(state);',
    ])
    css = text('clean/hangar18-manager/assets/editor.css')
    for needle in [
        ':has(.h18-clean-node.is-selected)',
        'z-index:9000!important',
        'z-index:10000!important',
        'z-index:11000!important',
        'z-index:12000!important',
    ]:
        if needle not in css:
            raise AssertionError(f'editor.css missing {needle}')

    renderer = text('clean/hangar18-manager/src/Frontend/Renderer.php')
    if 'z-index:10000' in renderer or 'z-index:11000' in renderer or 'z-index:12000' in renderer:
        raise AssertionError('editor-only active layer leaked into frontend Renderer')

    require('CLEAN-DESIGN-MANUAL.md', [
        '## 27. Canvas/Section-struktur',
        'Webside/Canvas → Sektion → Kasse eller indholdselement',
    ])
    require('CLEAN-TECHNICAL-MANUAL.md', [
        'VD-CANVAS-SECTION-001',
        'VD-SELECTION-LAYER-001',
    ])
    require('CLEAN-USER-MANUAL.md', ['Automatisk Section-struktur fra v0.1.68'])
    require('docs/v0168-status.md', ['Status: TESTKANDIDAT', 'Køretøjsmodulet er flyttet til v0.1.69'])
    require('docs/clean-backlog-v0100.md', ['Aktuel milepælsstatus · v0.1.68', 'v0.1.69 – Køretøjsmodul'])
    require('clean-release-notes.html', ['0.1.68 – Canvas/Section Structure'])
    require('clean/hangar18-manager/release-history.json', ['"version": "0.1.68"', 'VD-CANVAS-SECTION-001', 'VD-SELECTION-LAYER-001'])

except AssertionError as exc:
    print(f'V0168 CANVAS SECTION STATIC QA FAIL: {exc}', file=sys.stderr)
    raise SystemExit(1)

print('V0168 CANVAS SECTION STATIC QA OK')
