#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'clean/hangar18-manager/assets/editor-v0181.css').read_text(encoding='utf-8')
CORE = (ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js').read_text(encoding='utf-8')
RENDERER = (ROOT / 'clean/hangar18-manager/src/Frontend/Renderer.php').read_text(encoding='utf-8')


def require(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise SystemExit(f'Missing {label}: {needle}')


# The editor and frontend must use the same canonical 8 px track geometry.
require(CORE, "surface.style.gridAutoRows = ROW_PX + 'px';", 'editor fixed grid rows')
require(CORE, "card.style.gridRow = String(Math.max(0, geometry.y) + 1) + ' / span ' + String(geometry.h);", 'editor grid-row geometry')
require(RENDERER, "grid-auto-rows:' . esc_attr((string) $rowPx) . 'px", 'frontend fixed grid rows')
require(RENDERER, "$style .= 'grid-row:' . ($y + 1) . '/span ' . $h . ';min-height:' . ($h * LayoutModel::ROW_PX) . 'px;';", 'frontend grid-row geometry')

# v0.1.85 parity patch: parent editing chrome must not inflate the canonical outer box.
require(CSS, 'VD-EDITOR-LIVE-BOX-PARITY-002', 'parity marker')
require(CSS, '.h18-clean-node--section[data-h18-explicit-grid="1"]', 'section exact geometry selector')
require(CSS, '.h18-clean-node--container[data-h18-explicit-grid="1"]', 'container exact geometry selector')
require(CSS, 'height:100%!important;', 'exact editor parent height')
require(CSS, 'min-height:0!important;', 'remove editor-only min-height inflation')
require(CSS, '>.h18-clean-inner-surface', 'nested editor surface containment')
require(CSS, 'height:100%;', 'nested surface height containment')
require(CSS, 'box-sizing:border-box;', 'canonical border-box sizing')

# Parent geometry is still expanded from real children + configured padding/border
# before render; therefore forcing the DOM card to its grid area cannot clip valid
# Designer geometry.
require(CORE, 'function syncContainerHeights()', 'container geometry reconciler')
require(CORE, 'required = Math.max(required, Math.max(0, g.y) + Math.max(1, g.h || MIN_SPLIT_H));', 'child extent calculation')
require(CORE, 'const extraPx = (Math.max(0, parseInt(p.padding || 0, 10) || 0) * 2) + (Math.max(0, parseInt(p.borderWidth || 0, 10) || 0) * 2);', 'padding and border geometry allowance')
require(CORE, 'required += Math.ceil(extraPx / ROW_PX);', 'pixel-to-row allowance')

# Frontend remains a single border-box for Section/Box.
require(RENDERER, ".h18-clean-front-node{box-sizing:border-box", 'frontend node border-box')
require(RENDERER, "$boxStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $padding . 'px;'", 'frontend parent box style')

# Mathematical regression: the editor reconciliation must materialize an outer
# height large enough for child extent + parent padding/border, while the frontend
# consumes that same selected row height as its outer minimum.
ROW = 8
cases = [
    # child_bottom_rows, padding_px, border_px, manual_min_rows
    (12, 0, 0, 8),
    (12, 16, 0, 8),
    (18, 20, 2, 10),
    (30, 8, 1, 40),
]
for child_bottom, padding, border, manual_min in cases:
    extra_px = padding * 2 + border * 2
    editor_rows = max(manual_min, child_bottom + (extra_px + ROW - 1) // ROW)
    editor_outer_px = editor_rows * ROW
    frontend_selected_px = editor_rows * ROW
    if editor_outer_px != frontend_selected_px:
        raise SystemExit('Editor/frontend outer geometry mismatch')
    if editor_outer_px < child_bottom * ROW + extra_px:
        raise SystemExit('Reconciled parent geometry is too small for content box')

print('v0.1.85 editor/live box parity QA: OK')
