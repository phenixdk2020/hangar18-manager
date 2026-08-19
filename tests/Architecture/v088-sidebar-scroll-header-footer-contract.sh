#!/usr/bin/env bash
set -euo pipefail

CSS="assets/ultimate-designer-element-library.css"
MAIN="hangar18-manager.php"
DOC="docs/ud-global-header-footer-migration-v088.md"

# Left builder sidebar must scroll independently on desktop while keeping tabs outside the scroller.
grep -F '@media(min-width:1181px)' "$CSS" >/dev/null
grep -F '.h18-pages-admin .h18-builder-palette{display:flex;flex-direction:column;max-height:calc(100vh - 70px);overflow:hidden;overscroll-behavior:contain}' "$CSS" >/dev/null
grep -F '.h18-pages-admin .h18-builder-sidebar-tabs{flex:0 0 auto}' "$CSS" >/dev/null
grep -F '.h18-pages-admin .h18-builder-sidebar-panel.is-active' "$CSS" >/dev/null
grep -F 'overflow-y:auto' "$CSS" >/dev/null
grep -F 'scrollbar-gutter:stable' "$CSS" >/dev/null

# Responsive behavior follows Inspector: no forced viewport scroller on narrower layouts.
grep -F '@media(max-width:1180px)' "$CSS" >/dev/null
grep -F '.h18-pages-admin .h18-builder-palette{display:block;max-height:none;overflow:visible}' "$CSS" >/dev/null

# Header/Footer migration remains planning/shadow work; existing runtime is still source of truth.
grep -F "const HEADER_DESIGN_OPTION" "$MAIN" >/dev/null
grep -F "const HEADER_START" "$MAIN" >/dev/null
grep -F "const FOOTER_START" "$MAIN" >/dev/null
grep -F 'Planned architecture work only' "$DOC" >/dev/null
grep -F 'No frontend hook or renderer switch.' "$DOC" >/dev/null
grep -F 'Vehicle/Event/Gallery stay on the protected legacy runtime.' "$DOC" >/dev/null
grep -F 'public cutover only after explicit approval' "$DOC" >/dev/null

echo 'v0.8.8 sidebar scroll/Header-Footer contract: PASS'
