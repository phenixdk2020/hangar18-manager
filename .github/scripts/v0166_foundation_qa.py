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
    if not version_at_least(plugin, (0, 1, 66)):
        raise AssertionError('plugin version is older than 0.1.66')
    require('clean/hangar18-manager/hangar18-manager.php', [
        "src/Icons/IconRegistry.php",
        "assets/editor-v0166-foundation.css",
        "IconRegistry::editorCatalog()",
    ])

    require('clean/hangar18-manager/src/Icons/IconRegistry.php', [
        'final class IconRegistry',
        "visual_designer_manager_module_icon_sets",
        "visual_designer_manager_custom_icon_sets",
        "'source' => 'core'",
        "'sources' => ['core', 'module', 'custom']",
        "'customUploadEnabled' => false",
        "self::category('general', 'Generelt'",
        "self::category('contact', 'Kontakt'",
        "self::category('events', 'Dato og events'",
        "self::category('media', 'Medier'",
        "self::category('technical', 'Tekniske data'",
        "self::icon('engine', 'Motor'",
        "self::icon('track', 'Bælte'",
    ])

    require('clean/hangar18-manager/src/Model/LayoutModel.php', [
        'use VisualDesignerManager\\Icons\\IconRegistry;',
        "'iconSet' => $selection['set']",
        "'cellBorderStyle' => self::lineStyle",
        "'borderMode' => self::tableBorderMode",
        "'cellBorders' => self::tableCellBorders",
        'private static function tableCellBorders',
    ])

    require('clean/hangar18-manager/assets/editor-v018-core.js', [
        'function iconLibrarySets()',
        'function openIconLibrary()',
        "registryIconSvgMarkup(node.props.iconSet || 'core'",
        'let tableCellSelection = null;',
        'function tableRangeKeys',
        'function applyTableBorderAction',
        "event.ctrlKey || event.metaKey",
        'event.shiftKey',
        'data-table-border-action="outer"',
        'data-table-border-action="inner"',
        'data-table-border-action="horizontal"',
        'data-table-border-action="vertical"',
        'data-table-border-action="none"',
        "field === 'cellBorderStyle'",
        "field === 'tableBorderMode'",
        'is-vd-table-cell-selected',
    ])

    require('clean/hangar18-manager/src/Frontend/Renderer.php', [
        'use VisualDesignerManager\\Icons\\IconRegistry;',
        'IconRegistry::svg(',
        'private static function tableCellBorderCss',
        "'cellBorders'",
        'border-top:',
        'border-right:',
        'border-bottom:',
        'border-left:',
    ])

    require('clean/hangar18-manager/assets/editor-v0166-foundation.css', [
        '.h18-vd-icon-library-dialog',
        '.h18-vd-icon-library-grid',
        '.is-vd-table-cell-selected',
        '.h18-vd-table-border-actions',
    ])

    require('clean/hangar18-manager/assets/admin-v0123.js', [
        "'h18-clean-log': ['Klar', 'ready']",
        "'h18-clean-conversion': ['Klar', 'ready']",
    ])
    require('clean/hangar18-manager/assets/admin-v0156-menu.css', [
        'max-width:1800px',
        'minmax(520px,580px)',
        'white-space:nowrap',
        'min-width:max-content',
        'overflow-x:auto',
        '@media(max-width:1250px)',
    ])

    require('CLEAN-DESIGN-MANUAL.md', [
        '## 25. Ikonbibliotek',
        '**Core icons**',
        '**Module icons**',
        '**Custom icons**',
        '## 26. Tabel – kantdesign',
    ])
    require('CLEAN-TECHNICAL-MANUAL.md', [
        'VD-ICON-LIBRARY-001',
        'VD-TABLE-BORDERS-001',
        'VD-MENU-PREVIEW-001',
        'VD-ADMIN-STATUS-002',
        '- solid/dashed/dotted.',
    ])
    require('docs/v0166-status.md', ['Status: TESTKANDIDAT', 'Custom icon upload', 'Køretøjsmodulet'])
    require('clean-release-notes.html', ['0.1.66 – Icon Library, Tabelkanter og Menu-preview'])
    require('clean/hangar18-manager/release-history.json', ['"version": "0.1.66"'])

except AssertionError as exc:
    print(f'V0166 FOUNDATION QA FAIL: {exc}', file=sys.stderr)
    raise SystemExit(1)

print('V0166 FOUNDATION QA OK')
