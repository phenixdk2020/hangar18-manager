from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.38'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha37.py'], check=True)


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
    (' * Version: 3.0.0-alpha.37', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.37');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.37');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.38 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# 1) Remove Header/Footer flash in embedded responsive Designer preview.
#
# Alpha.37 hid shell parts only after the iframe load event. Browsers can paint
# the frontend once before that bridge CSS is injected, producing a visible
# Header/Footer flash. Keep the iframe invisible during navigation and reveal it
# only after the page-only bridge has been installed.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    """                    '<iframe id="' + FRAME_ID + '" name="' + FRAME_NAME + '" title="Kanonisk frontend-preview" loading="eager"></iframe>' +
""",
    """                    '<iframe id="' + FRAME_ID + '" name="' + FRAME_NAME + '" title="Kanonisk frontend-preview" loading="eager" style="visibility:hidden"></iframe>' +
""",
    'Alpha.38 responsive iframe starts hidden'
)
replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    """        currentDevice = device;
        host.classList.add('is-loading');

        var form = document.createElement('form');
""",
    """        currentDevice = device;
        host.classList.add('is-loading');
        var frame = host.querySelector('#' + FRAME_ID);
        if (frame) { frame.style.visibility = 'hidden'; }

        var form = document.createElement('form');
""",
    'Alpha.38 hide responsive iframe before submit'
)
replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    """        if (host) { host.classList.remove('is-loading'); }
        installFrameBridge(frame);

        window.setTimeout(function () {
""",
    """        installFrameBridge(frame);
        window.requestAnimationFrame(function () {
            frame.style.visibility = 'visible';
            if (host) { host.classList.remove('is-loading'); }
        });

        window.setTimeout(function () {
""",
    'Alpha.38 reveal responsive iframe after bridge'
)

# ---------------------------------------------------------------------------
# 2) "Vis med Header + Footer" follows selected Designer device.
#
# The composite preview previously filled the overlay iframe at 100%, so every
# device was effectively a Desktop viewport. The srcdoc iframe itself now gets
# the exact selected CSS viewport width before the document is assigned. It is
# scaled only for presentation; media queries therefore evaluate at the real
# 1920/1100/850/390 px viewport.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0125.js',
    """    function ensureCompositeOverlay() {
""",
    """    var COMPOSITE_WIDTHS = { desktop: 1920, laptop: 1100, tablet: 850, mobile: 390 };
    var COMPOSITE_LABELS = { desktop: 'Desktop', laptop: 'Laptop', tablet: 'Tablet', mobile: 'Mobil' };

    function selectedCompositeDevice() {
        var device = document.body ? String(document.body.getAttribute('data-h18-clean-device') || 'desktop') : 'desktop';
        return COMPOSITE_WIDTHS[device] ? device : 'desktop';
    }

    function fitCompositePreview(overlay, device) {
        if (!overlay) { return; }
        var wrap = overlay.querySelector('.h18-vd-composite-frame-wrap');
        var stage = overlay.querySelector('.h18-vd-composite-stage');
        var frame = overlay.querySelector('.h18-vd-composite-frame');
        var status = overlay.querySelector('.h18-vd-composite-device');
        if (!wrap || !stage || !frame) { return; }
        device = COMPOSITE_WIDTHS[device] ? device : 'desktop';
        var width = COMPOSITE_WIDTHS[device];
        var availableWidth = Math.max(260, wrap.clientWidth - 24);
        var availableHeight = Math.max(420, wrap.clientHeight - 24);
        var scale = Math.max(0.15, Math.min(1, availableWidth / width));
        scale = Math.round(scale * 100) / 100;
        var cssHeight = Math.max(600, Math.floor(availableHeight / scale));
        frame.style.width = width + 'px';
        frame.style.height = cssHeight + 'px';
        frame.style.transformOrigin = '0 0';
        frame.style.transform = 'scale(' + scale + ')';
        stage.style.width = Math.ceil(width * scale) + 'px';
        stage.style.height = Math.ceil(cssHeight * scale) + 'px';
        if (status) { status.textContent = COMPOSITE_LABELS[device] + ' · ' + width + ' px · ' + Math.round(scale * 100) + '% visning'; }
    }

    function ensureCompositeOverlay() {
""",
    'Alpha.38 composite viewport helpers'
)
replace_once(
    'assets/editor-v0125.js',
    """        overlay.innerHTML = '<div class="h18-vd-composite-dialog" role="dialog" aria-modal="true"><div class="h18-vd-composite-bar"><strong>Visual Designer · Header + landingsside + Footer</strong><button type="button" class="button" data-vd-composite-close>Luk</button></div><div class="h18-vd-composite-frame-wrap"><div class="h18-vd-composite-loading">Renderer samlet preview…</div><iframe class="h18-vd-composite-frame" title="Samlet Visual Designer preview"></iframe></div></div>';
""",
    """        overlay.innerHTML = '<div class="h18-vd-composite-dialog" role="dialog" aria-modal="true"><div class="h18-vd-composite-bar"><strong>Visual Designer · Header + side + Footer</strong><span class="h18-vd-composite-device"></span><button type="button" class="button" data-vd-composite-close>Luk</button></div><div class="h18-vd-composite-frame-wrap"><div class="h18-vd-composite-loading">Renderer samlet preview…</div><div class="h18-vd-composite-stage"><iframe class="h18-vd-composite-frame" title="Samlet Visual Designer preview"></iframe></div></div></div>';
""",
    'Alpha.38 composite stage markup'
)
replace_once(
    'assets/editor-v0125.js',
    """        var loading = overlay.querySelector('.h18-vd-composite-loading');
        var frame = overlay.querySelector('.h18-vd-composite-frame');
        overlay.hidden = false;
        document.body.classList.add('h18-vd-composite-open');
        if (loading) { loading.hidden = false; loading.textContent = 'Renderer samlet preview…'; }
        if (frame) { frame.hidden = true; frame.removeAttribute('src'); }

        var body = new URLSearchParams();
""",
    """        var loading = overlay.querySelector('.h18-vd-composite-loading');
        var frame = overlay.querySelector('.h18-vd-composite-frame');
        var previewDevice = selectedCompositeDevice();
        overlay.hidden = false;
        overlay.setAttribute('data-vd-preview-device', previewDevice);
        document.body.classList.add('h18-vd-composite-open');
        if (loading) { loading.hidden = false; loading.textContent = 'Renderer samlet preview…'; }
        if (frame) {
            frame.hidden = false;
            frame.style.visibility = 'hidden';
            frame.removeAttribute('src');
        }
        fitCompositePreview(overlay, previewDevice);

        var body = new URLSearchParams();
""",
    'Alpha.38 selected composite device before render'
)
replace_once(
    'assets/editor-v0125.js',
    """        body.set('footer_template_choice', footer ? String(footer.value || 'auto') : 'auto');

        fetch(String(button.getAttribute('data-url') || ''), {
""",
    """        body.set('footer_template_choice', footer ? String(footer.value || 'auto') : 'auto');
        body.set('preview_device', previewDevice);
        body.set('preview_width', String(COMPOSITE_WIDTHS[previewDevice]));

        fetch(String(button.getAttribute('data-url') || ''), {
""",
    'Alpha.38 composite diagnostic device POST'
)
replace_once(
    'assets/editor-v0125.js',
    """            if (!frame) { return; }
            frame.srcdoc = result.html;
            frame.hidden = false;
            if (loading) { loading.hidden = true; }
""",
    """            if (!frame) { return; }
            frame.onload = function () {
                fitCompositePreview(overlay, previewDevice);
                frame.style.visibility = 'visible';
                if (loading) { loading.hidden = true; }
            };
            fitCompositePreview(overlay, previewDevice);
            frame.srcdoc = result.html;
""",
    'Alpha.38 composite reveal after selected viewport load'
)
replace_once(
    'assets/editor-v0125.js',
    """        var compositeButton = document.getElementById('h18-clean-composite-preview');
        if (compositeButton) { compositeButton.addEventListener('click', openCompositePreview); }
""",
    """        var compositeButton = document.getElementById('h18-clean-composite-preview');
        if (compositeButton) { compositeButton.addEventListener('click', openCompositePreview); }
        window.addEventListener('resize', function () {
            var overlay = document.getElementById('h18-vd-composite-overlay');
            if (!overlay || overlay.hidden) { return; }
            fitCompositePreview(overlay, String(overlay.getAttribute('data-vd-preview-device') || selectedCompositeDevice()));
        }, { passive: true });
""",
    'Alpha.38 composite resize refit'
)

replace_once(
    'assets/editor-v0125.css',
    ".h18-vd-composite-frame-wrap{position:relative;flex:1 1 auto;min-height:0;padding:12px;background:#dcdcde}.h18-vd-composite-frame{width:100%;height:100%;min-height:520px;border:0;background:#fff}.h18-vd-composite-loading{padding:30px;text-align:center;font-weight:600;color:#50575e}",
    ".h18-vd-composite-frame-wrap{position:relative;flex:1 1 auto;min-height:0;padding:12px;background:#dcdcde;overflow:auto}.h18-vd-composite-stage{margin:0 auto;transform-origin:top center}.h18-vd-composite-frame{display:block;border:0;background:#fff;box-shadow:0 3px 18px rgba(0,0,0,.18);transform-origin:0 0}.h18-vd-composite-device{margin-left:auto;font-weight:600;color:#50575e}.h18-vd-composite-bar strong{margin-right:12px}.h18-vd-composite-loading{position:absolute;inset:12px;z-index:2;padding:30px;text-align:center;font-weight:600;color:#50575e;background:#dcdcde}",
    'Alpha.38 composite selected viewport CSS'
)

# ---------------------------------------------------------------------------
# Diagnostics: record requested device in composite preview logs via document
# title only; server rendering remains canonical and device behavior is driven
# exclusively by the iframe CSS viewport.
# ---------------------------------------------------------------------------
replace_once(
    'src/Admin/EditorController.php',
    """            $footerModel = self::templateModelForPreview('footer', $footerChoice);
            nocache_headers();
            header('Content-Type: text/html; charset=utf-8');
            echo Renderer::standaloneDocument($pageModel, $headerModel, $footerModel, 'Visual Designer · samlet preview');
""",
    """            $footerModel = self::templateModelForPreview('footer', $footerChoice);
            $previewDevice = sanitize_key((string) wp_unslash($_POST['preview_device'] ?? 'desktop'));
            $previewWidths = ['desktop' => 1920, 'laptop' => 1100, 'tablet' => 850, 'mobile' => 390];
            if (!isset($previewWidths[$previewDevice])) { $previewDevice = 'desktop'; }
            $previewLabel = ['desktop' => 'Desktop', 'laptop' => 'Laptop', 'tablet' => 'Tablet', 'mobile' => 'Mobil'][$previewDevice];
            nocache_headers();
            header('Content-Type: text/html; charset=utf-8');
            echo Renderer::standaloneDocument($pageModel, $headerModel, $footerModel, 'Visual Designer · Header + Footer · ' . $previewLabel . ' · ' . $previewWidths[$previewDevice] . ' px');
""",
    'Alpha.38 composite server selected-device title'
)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.37':
    raise SystemExit('Expected Alpha.37 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-13',
    'items': [
        'Responsive Designer-preview skjuler iframe under navigation og viser det først efter page-only bridge-CSS er installeret; Header/Footer blinker derfor ikke længere kort ved skift eller første load.',
        'Vis med Header + Footer bruger nu den valgte Designer-enheds eksakte CSS-viewport: Desktop 1920 px, Laptop 1100 px, Tablet 850 px og Mobil 390 px.',
        'Samlet Header/Footer-preview skaleres kun visuelt til dialogen; iframe-layout og media queries beregnes fortsat på den valgte enheds rigtige pixelbredde.',
        'Preview-dialogen viser valgt enhed, pixelbredde og visningsskalering.',
        'Alpha.37 Laptop/Tablet CTA-knaprettelse og Alpha.36 responsive flow bevares.',
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
canonical = read('assets/editor-v0183-canonical-responsive-preview.js')
editor_js = read('assets/editor-v0125.js')
editor_css = read('assets/editor-v0125.css')
editor = read('src/Admin/EditorController.php')
history_text = read('release-history.json')

for token in [
    'Version: 3.0.0-alpha.38',
    "define('VDM_VERSION', '3.0.0-alpha.38');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.38');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.38 version token missing: {token}')

for token in [
    'style="visibility:hidden"',
    "frame.style.visibility = 'hidden';",
    "frame.style.visibility = 'visible';",
    '.h18-vd-live-shell-header,.h18-vd-live-shell-footer{display:none!important}',
]:
    if token not in canonical:
        raise SystemExit(f'Alpha.38 flash token missing: {token}')

for token in [
    "var COMPOSITE_WIDTHS = { desktop: 1920, laptop: 1100, tablet: 850, mobile: 390 };",
    'function selectedCompositeDevice()',
    'function fitCompositePreview(overlay, device)',
    "body.set('preview_device', previewDevice);",
    "body.set('preview_width', String(COMPOSITE_WIDTHS[previewDevice]));",
    "frame.style.visibility = 'hidden';",
    "frame.style.visibility = 'visible';",
]:
    if token not in editor_js:
        raise SystemExit(f'Alpha.38 composite JS token missing: {token}')

for token in [
    '.h18-vd-composite-stage{margin:0 auto',
    '.h18-vd-composite-device{margin-left:auto',
    'overflow:auto',
]:
    if token not in editor_css:
        raise SystemExit(f'Alpha.38 composite CSS token missing: {token}')

for token in [
    "$previewDevice = sanitize_key((string) wp_unslash($_POST['preview_device'] ?? 'desktop'));",
    "$previewWidths = ['desktop' => 1920, 'laptop' => 1100, 'tablet' => 850, 'mobile' => 390];",
    "'Visual Designer · Header + Footer · ' . $previewLabel . ' · ' . $previewWidths[$previewDevice] . ' px'",
]:
    if token not in editor:
        raise SystemExit(f'Alpha.38 composite server token missing: {token}')

if '3.0.0-alpha.38' not in history_text:
    raise SystemExit('Alpha.38 history token missing')

print('Alpha.38 selected-device composite preview: PASS')
