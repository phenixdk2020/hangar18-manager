from pathlib import Path
import re
import subprocess

VERSION = '3.0.0-alpha.39'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha38.py'], check=True)


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Version cutover.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.38', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.38');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.38');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.39 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# 1) Rich text lost everything after the first typed letter.
#
# The Inspector scroll/focus preservation (v0114) re-focused the hidden text
# field after every Inspector rebuild, even while the rich text editor still
# had focus. That blur committed the field, rebuilt the Inspector and the
# editor lost all but the first character. Only restore focus when the field
# the user worked in was actually replaced and nothing else is focused.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0114.js',
    """        function capture(event) {
            var target = event && event.target;
            if (!target || !host.contains(target) || !target.matches('input,select,textarea,button')) { return; }
            pending = {
                scrollTop: panel.scrollTop,
                key: fieldKey(target)
            };
        }
""",
    """        function currentSelection() {
            var api = window.H18VDDesigner;
            return api && typeof api.selectedId === 'function' ? String(api.selectedId() || '') : '';
        }

        // A pointer press on the canvas means the user moved on to the canvas: forget the field and ignore
        // the change event its blur fires, so focus stays out of the Inspector and arrow keys nudge.
        var canvasSuppressUntil = 0;
        document.addEventListener('pointerdown', function (event) {
            if (event.target && event.target.closest && event.target.closest('#h18-clean-canvas')) {
                pending = null;
                canvasSuppressUntil = Date.now() + 600;
            }
        }, true);

        function capture(event) {
            if (Date.now() < canvasSuppressUntil) { return; }
            var target = event && event.target;
            if (!target || !host.contains(target) || !target.matches('input,select,textarea,button')) { return; }
            pending = {
                scrollTop: panel.scrollTop,
                key: fieldKey(target),
                selected: currentSelection()
            };
        }
""",
    'Alpha.39 Inspector capture ignores canvas clicks'
)
replace_once(
    'assets/editor-v0114.js',
    """                    if (replacement && typeof replacement.focus === 'function') {
""",
    """                    // Only restore focus when the field the user worked in was replaced. Never pull focus
                    // away from a control that is still connected (e.g. the rich text editor while typing).
                    var current = document.activeElement;
                    var stillFocused = current && current !== document.body && current.isConnected && host.contains(current);
                    // A different element was selected on the canvas: leave focus there so arrow keys nudge it.
                    var selectionChanged = state.selected !== currentSelection();
                    if (replacement && !stillFocused && !selectionChanged && typeof replacement.focus === 'function') {
""",
    'Alpha.39 Inspector focus restore does not steal focus'
)

# The rich text editor primes its selection one tick later. If the user has
# already typed (or moved the caret) by then, re-applying the stale range
# selected the new text and the next keystroke overwrote it.
replace_once(
    'assets/editor-v0125.js',
    """        active.savedLogical = logical;
        window.setTimeout(function () {
            if (!active || active.editor !== editor || active.formatting || !editor.isConnected) { return; }
            primeSelectionSession(logical);
""",
    """        active.savedLogical = logical;
        // The deferred prime must not re-apply a stale selection: if the user already typed (text or
        // selection generation changed), restoring the old range would select and overwrite new text.
        var generation = selectionGeneration;
        var htmlAtSchedule = editor.innerHTML;
        window.setTimeout(function () {
            if (!active || active.editor !== editor || active.formatting || !editor.isConnected) { return; }
            if (generation !== selectionGeneration || editor.innerHTML !== htmlAtSchedule) { return; }
            primeSelectionSession(logical);
""",
    'Alpha.39 rich text deferred selection prime is skipped after typing'
)

# ---------------------------------------------------------------------------
# 2) Arrow keys did not move the element after editing an Inspector field.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v018-core.js',
    """                event.stopPropagation();
                selectedId = node.id;
                render();
            });
""",
    """                event.stopPropagation();
                // Release focus from an Inspector field (committing its value) so arrow keys move the element.
                const focused = document.activeElement;
                if (focused && focused !== document.body && focused.closest && focused.closest('#h18-clean-inspector')) { focused.blur(); }
                selectedId = node.id;
                render();
            });
""",
    'Alpha.39 canvas click releases Inspector focus'
)

# ---------------------------------------------------------------------------
# 3) A new Menu was invisible on a light section (white text on white, and
#    the mobile hamburger used the same colour).
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v018-core.js',
    """    function addNode(type, parentId, source, dropGeometry) {
""",
    """    function effectiveBackground(parentId) {
        let current = parentId ? nodeById(parentId) : null;
        while (current) {
            const props = current.props || {};
            const bg = String(props.background || '');
            if (!props.backgroundTransparent && /^#[0-9a-f]{6}$/i.test(bg)) { return bg; }
            current = current.parentId ? nodeById(current.parentId) : null;
        }
        return '#ffffff';
    }

    function readableMenuText(parentId) {
        const hex = effectiveBackground(parentId).slice(1);
        const channel = function (i) { const c = parseInt(hex.slice(i, i + 2), 16) / 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
        const luminance = 0.2126 * channel(0) + 0.7152 * channel(2) + 0.0722 * channel(4);
        return luminance > 0.4 ? '#30382a' : '#ffffff';
    }

    function addNode(type, parentId, source, dropGeometry) {
""",
    'Alpha.39 readable menu colour helpers'
)
replace_once(
    'assets/editor-v018-core.js',
    """        if (type === 'text') { newProps.padding = 12; }
""",
    """        if (type === 'text') { newProps.padding = 12; }
        // A new menu defaults to white text (made for the dark V1 header); on a light background that is
        // invisible on desktop and hides the mobile hamburger. Pick a readable colour for where it is placed.
        if (type === 'menu') { newProps.textColor = readableMenuText(parentId); }
""",
    'Alpha.39 new menu gets readable text colour'
)

# ---------------------------------------------------------------------------
# 4) Import turned an existing image into a page.
#
# get_page_by_path(..., 'page') also returns attachments. A portable import of
# page "aktiviteter" therefore overwrote the image aktiviteter.jpg. Route every
# page lookup through a wrapper that only returns real pages.
# ---------------------------------------------------------------------------
write('src/Compatibility/PageLookup.php', """<?php

declare(strict_types=1);

/**
 * get_page_by_path() also searches attachments, so a page lookup could return an
 * image with the same slug (e.g. an import then turned that image into a page).
 * This wrapper only ever returns a real page.
 */
if (!function_exists('vdm_page_by_path')) {
    function vdm_page_by_path($path): ?\\WP_Post
    {
        $post = get_page_by_path((string) $path, OBJECT, 'page');
        return $post instanceof \\WP_Post && $post->post_type === 'page' ? $post : null;
    }
}
""")
replace_once(
    'visual-designer-manager.php',
    """require_once VDM_DIR . 'src/Compatibility/LegacyStorageBridge.php';
""",
    """require_once VDM_DIR . 'src/Compatibility/PageLookup.php';
require_once VDM_DIR . 'src/Compatibility/LegacyStorageBridge.php';
""",
    'Alpha.39 load page lookup wrapper'
)
LOOKUP = re.compile(r"get_page_by_path\(\s*([^;]*?)\s*,\s*OBJECT\s*,\s*'page'\s*\)")
replaced = 0
for path in sorted((DEST / 'src').rglob('*.php')):
    rel = path.relative_to(DEST).as_posix()
    if rel == 'src/Compatibility/PageLookup.php':
        continue
    value = path.read_text(encoding='utf-8')
    value, count = LOOKUP.subn(r'vdm_page_by_path(\1)', value)
    if count:
        replaced += count
        path.write_text(value, encoding='utf-8')
if replaced != 20:
    raise SystemExit(f'Alpha.39 page lookup: expected 20 get_page_by_path page lookups, replaced {replaced}')

# ---------------------------------------------------------------------------
# 5) PHP 8.1 deprecations from add_submenu_page(null, ...) on every admin page.
# ---------------------------------------------------------------------------
replace_once(
    'src/Admin/AdminController.php',
    "add_submenu_page(null, 'Data (intern)',",
    "add_submenu_page('', 'Data (intern)',",
    'Alpha.39 hidden Data route without null parent'
)
replace_once(
    'src/Admin/AdminController.php',
    "add_submenu_page(null, 'Konvertering (intern)',",
    "add_submenu_page('', 'Konvertering (intern)',",
    'Alpha.39 hidden Konvertering route without null parent'
)
replace_once(
    'src/Admin/PortableTransferController.php',
    """        add_submenu_page(
            null,
            'Import / recovery',
""",
    """        add_submenu_page(
            '',
            'Import / recovery',
""",
    'Alpha.39 hidden import route without null parent'
)

# Hidden routes have no menu title, so WordPress' admin header calls
# strip_tags(null) on them (a PHP 8.1 deprecation). Give them their title.
write('src/Compatibility/HiddenAdminTitles.php', """<?php

declare(strict_types=1);

/**
 * Hidden admin routes (registered with an empty parent) have no menu title, and
 * wp-admin/admin-header.php then passes null to strip_tags(). Provide the title.
 */
add_action('current_screen', static function (): void {
    global $title, $plugin_page;
    $hidden = [
        'vdm-data' => 'Data (intern)',
        'vdm-conversion' => 'Konvertering (intern)',
        'vdm-transfer' => 'Import / recovery',
    ];
    if (empty($title) && is_string($plugin_page) && isset($hidden[$plugin_page])) {
        $title = $hidden[$plugin_page];
    }
});
""")
replace_once(
    'visual-designer-manager.php',
    """require_once VDM_DIR . 'src/Compatibility/PageLookup.php';
""",
    """require_once VDM_DIR . 'src/Compatibility/PageLookup.php';
require_once VDM_DIR . 'src/Compatibility/HiddenAdminTitles.php';
""",
    'Alpha.39 load hidden admin titles'
)

# ---------------------------------------------------------------------------
# 6) Import / restore was unreachable: the route is hidden and nothing linked
#    to it. Link it from Backup and Eksport.
# ---------------------------------------------------------------------------
replace_once(
    'src/Admin/AdminController.php',
    """        echo '<div class="h18-manager-card"><h2>Hvad backupen indeholder</h2>""",
    """        echo '<div class="h18-manager-card"><h2>Gendan / importér</h2><p>Gendan et site fra en portabel VDM-sitepakke (fra <strong>Eksport</strong>). Pakken kontrolleres først med en forhåndskontrol, før noget ændres.</p><p><a class="button" href="' . esc_url(admin_url('admin.php?page=vdm-transfer')) . '">Åbn Gendan / importér</a></p></div>';
        echo '<div class="h18-manager-card"><h2>Hvad backupen indeholder</h2>""",
    'Alpha.39 Backup links to import / restore'
)
replace_once(
    'src/Admin/ExportController.php',
    """        echo '<h1>Eksport</h1>';
""",
    """        echo '<h1>Eksport</h1>';
        echo '<p>Skal du gendanne eller flytte et site? <a href="' . esc_url(admin_url('admin.php?page=vdm-transfer')) . '">Åbn Gendan / importér</a>.</p>';
""",
    'Alpha.39 Eksport links to import / restore'
)

print(f'Visual Designer Manager V3 {VERSION} build: PASS')
