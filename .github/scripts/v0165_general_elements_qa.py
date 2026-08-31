from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]


def text(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        raise AssertionError(f'missing file: {rel}')
    return p.read_text(encoding='utf-8')


def require(rel: str, needle: str, label: str | None = None) -> None:
    value = text(rel)
    if needle not in value:
        raise AssertionError(label or f'{rel} missing {needle!r}')


def require_all(rel: str, needles: list[str]) -> None:
    value = text(rel)
    missing = [n for n in needles if n not in value]
    if missing:
        raise AssertionError(f'{rel} missing: {missing}')

try:
    plugin = text('clean/hangar18-manager/hangar18-manager.php')
    if not re.search(r'Version:\s*0\.1\.65\b', plugin):
        raise AssertionError('plugin header is not 0.1.65')
    if "define('H18_CLEAN_VERSION', '0.1.65');" not in plugin:
        raise AssertionError('H18_CLEAN_VERSION is not 0.1.65')
    require('clean/hangar18-manager/hangar18-manager.php', "assets/editor-v0165-elements.css", 'new element CSS is not enqueued by the shared Designer bootstrap')

    new_types = ['spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table']
    model = text('clean/hangar18-manager/src/Model/LayoutModel.php')
    for node_type in new_types:
        if f"'{node_type}'" not in model:
            raise AssertionError(f'LayoutModel missing canonical type {node_type}')
        if node_type != 'spacer' and f"if ($type === '{node_type}')" not in model:
            raise AssertionError(f'LayoutModel missing props branch for {node_type}')
    require_all('clean/hangar18-manager/src/Model/LayoutModel.php', [
        'private static function pairRows',
        'private static function stringList',
        'private static function matrixRows',
        'private static function iconToken',
        "'mobileMode' => $mobileMode",
        "'cellBorderWidth' => self::clamp",
    ])

    core = text('clean/hangar18-manager/assets/editor-v018-core.js')
    for node_type in new_types:
        if f"'{node_type}'" not in core:
            raise AssertionError(f'editor core missing type {node_type}')
    require_all('clean/hangar18-manager/assets/editor-v018-core.js', [
        "spacer:'Mellemrum'",
        "divider:'Skillelinje'",
        "datalist:'Data List'",
        "table:'Tabel'",
        'function normalizePairRows',
        'function normalizeHeaders',
        'function normalizeMatrixRows',
        'function iconSvgMarkup',
        "node.type === 'spacer'",
        "node.type === 'divider'",
        "node.type === 'icon'",
        "node.type === 'badge'",
        "node.type === 'link'",
        "node.type === 'datalist'",
        "node.type === 'table'",
        'Statisk Data List · test',
        'Statisk Tabel · test',
        "field === 'tableHeaders'",
        "field === 'tableRows'",
        "field === 'mobileTableMode'",
        "field === 'dataRows'",
        "cellBorderWidth: clamp(parseInt(raw.cellBorderWidth != null ? raw.cellBorderWidth : 1, 10) || 0, 0, 10)",
        "laptop: Object.assign({}, desktop, { inheritDesktop: true })",
        'window.H18VDProductivity = {',
    ])

    page = text('clean/hangar18-manager/src/Admin/EditorController.php')
    global_designer = text('clean/hangar18-manager/src/Admin/GlobalDesignerController.php')
    palette_labels = ['Mellemrum', 'Skillelinje', 'Ikon', 'Badge', 'Link', 'Data List', 'Tabel']
    for label in palette_labels:
        if label not in page:
            raise AssertionError(f'Page Designer palette missing {label}')
        if label not in global_designer:
            raise AssertionError(f'Header/Footer palette missing {label}')

    renderer = text('clean/hangar18-manager/src/Frontend/Renderer.php')
    require_all('clean/hangar18-manager/src/Frontend/Renderer.php', [
        "if ($type === 'spacer')",
        "if ($type === 'divider')",
        "if ($type === 'icon')",
        "if ($type === 'badge')",
        "if ($type === 'link')",
        "if ($type === 'datalist')",
        "if ($type === 'table')",
        'private static function iconSvg',
        'h18-clean-front-spacer',
        'h18-clean-front-divider',
        'h18-clean-front-datalist',
        'h18-clean-front-table-wrap',
        'data-mobile-mode',
        'data-label=',
    ])

    css = text('clean/hangar18-manager/assets/editor-v0165-elements.css')
    for cls in ['h18-clean-node--spacer', 'h18-vd-divider-line', 'h18-vd-icon-preview', 'h18-vd-badge-preview', 'h18-vd-datalist-preview', 'h18-vd-table-preview']:
        if cls not in css:
            raise AssertionError(f'v0.1.65 CSS missing {cls}')

    require('CLEAN-TECHNICAL-MANUAL.md', 'VD-ELEMENTS-001')
    require('docs/v0165-status.md', 'Status: TESTKANDIDAT')
    require('docs/v0165-status.md', 'Dynamisk datasource/binding')
    require('clean-release-notes.html', '0.1.65 – General Designer Elements · testversion')
    require('clean/hangar18-manager/release-history.json', '"version": "0.1.65"')

    # Explicit architectural boundary: this release must not introduce the Vehicle module.
    forbidden_paths = [
        ROOT / 'clean/hangar18-manager/src/Vehicle',
        ROOT / 'clean/hangar18-manager/src/Vehicles',
    ]
    if any(p.exists() for p in forbidden_paths):
        raise AssertionError('v0.1.65 unexpectedly introduced Vehicle module source')

except AssertionError as exc:
    print(f'V0165 GENERAL ELEMENTS QA FAIL: {exc}', file=sys.stderr)
    raise SystemExit(1)

print('V0165 GENERAL ELEMENTS QA OK')
