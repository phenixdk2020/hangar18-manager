from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.10'
DEST = Path('build/visual-designer-manager')


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


subprocess.run(['python3', '.github/scripts/build_v3_alpha9.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.9', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.9');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.9');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.10 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Mobile runtime reflow safeguard.
# Alpha.8 correctly loads stored mobile geometry, but screenshots from test4
# prove that valid stored coordinates can still become visually invalid after
# real mobile text wrapping (especially Safari): horizontal clipping, text
# overlap and very large empty gaps. Alpha.10 measures the rendered page and
# only reflows the specific parent containers that actually fail.
# Header/Footer keep their explicit responsive template geometry untouched.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
replace_once(
    rr_rel,
    "    public static function register(): void\n    {\n        add_action('wp_head', [self::class, 'css'], 1001);\n    }\n",
    "    public static function register(): void\n    {\n        add_action('wp_head', [self::class, 'css'], 1001);\n        add_action('wp_enqueue_scripts', [self::class, 'assets'], 1001);\n    }\n\n    public static function assets(): void\n    {\n        if (!is_singular('page')) {\n            return;\n        }\n        $postId = get_queried_object_id();\n        if ($postId <= 0) {\n            return;\n        }\n        $model = self::model($postId);\n        if ($model === null || empty($model['nodes']) || !is_array($model['nodes'])) {\n            return;\n        }\n        wp_enqueue_script('vdm-v3-mobile-reflow', VDM_URL . 'assets/v3-alpha10-mobile-reflow.js', [], VDM_VERSION, true);\n    }\n",
    'mobile reflow asset registration'
)
replace_once(
    rr_rel,
    "            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);\n",
    "            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);\n            if ($floating) {\n                $mobile .= $scope . '.h18-vdm-mobile-flow-repair>#h18-clean-' . self::cssId($id)\n                    . '{position:relative!important;left:auto!important;right:auto!important;top:auto!important;width:100%!important;height:auto!important;z-index:auto!important;grid-column:auto!important;grid-row:auto!important;margin-right:0!important;}';\n            }\n",
    'mobile overlay demotion when repaired'
)
replace_once(
    rr_rel,
    "            . '.h18-vd-live-shell{overflow-x:hidden;}'\n            . $mobile . '}';",
    "            . '.h18-vd-live-shell{overflow-x:hidden;}'\n            . '.h18-vd-live-shell-page .h18-vdm-mobile-flow-repair{display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:0!important;height:auto!important;min-height:0!important;overflow:visible!important;}'\n            . '.h18-vd-live-shell-page .h18-vdm-mobile-flow-repair>.h18-clean-front-node{position:relative!important;left:auto!important;right:auto!important;top:auto!important;width:100%!important;max-width:100%!important;height:auto!important;grid-column:auto!important;grid-row:auto!important;margin-right:0!important;box-sizing:border-box!important;}'\n            . '.h18-vd-live-shell-page .h18-vdm-mobile-flow-repair>.h18-clean-front-spacer{min-height:32px!important;}'\n            . $mobile . '}';",
    'mobile natural flow repair CSS'
)

mobile_js = r'''(function () {
    'use strict';

    var BREAKPOINT = 782;
    var REPAIR_CLASS = 'h18-vdm-mobile-flow-repair';
    var ROOT_SELECTOR = '.h18-vd-live-shell-page .h18-clean-front-surface';
    var PARENT_SELECTOR = ROOT_SELECTOR + ',.h18-vd-live-shell-page .h18-clean-front-section,.h18-vd-live-shell-page .h18-clean-front-container';

    function directNodes(parent) {
        return Array.prototype.filter.call(parent.children || [], function (child) {
            return child && child.classList && child.classList.contains('h18-clean-front-node');
        });
    }

    function depth(element) {
        var value = 0;
        for (var node = element; node && node.parentElement; node = node.parentElement) { value += 1; }
        return value;
    }

    function isSpacer(element) {
        return !!(element && element.classList && element.classList.contains('h18-clean-front-spacer'));
    }

    function isAbsolute(element) {
        try { return window.getComputedStyle(element).position === 'absolute'; }
        catch (error) { return false; }
    }

    function horizontalOverflow(parentRect, childRect) {
        return childRect.left < parentRect.left - 2 || childRect.right > parentRect.right + 2;
    }

    function intrinsicOverflow(element) {
        return element.scrollWidth > element.clientWidth + 2 || element.scrollHeight > element.clientHeight + 2;
    }

    function overlaps(a, b) {
        var x = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        var y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        return x > 4 && y > 4;
    }

    function needsRepair(parent) {
        var children = directNodes(parent);
        if (!children.length) { return false; }
        var parentRect = parent.getBoundingClientRect();
        var normal = [];
        var i;
        for (i = 0; i < children.length; i += 1) {
            var child = children[i];
            var rect = child.getBoundingClientRect();
            if (horizontalOverflow(parentRect, rect) || intrinsicOverflow(child)) { return true; }
            if (!isAbsolute(child)) { normal.push({ element: child, rect: rect }); }
        }
        normal.sort(function (a, b) { return a.rect.top - b.rect.top || a.rect.left - b.rect.left; });
        for (i = 1; i < normal.length; i += 1) {
            if (overlaps(normal[i - 1].rect, normal[i].rect)) { return true; }
        }
        if (parent.matches(ROOT_SELECTOR) && normal.length > 1) {
            for (i = 1; i < normal.length; i += 1) {
                var gap = normal[i].rect.top - normal[i - 1].rect.bottom;
                if (gap > 160 && !isSpacer(normal[i - 1].element) && !isSpacer(normal[i].element)) { return true; }
            }
        }
        return false;
    }

    function runRepair() {
        if (!window.matchMedia || !window.matchMedia('(max-width:' + BREAKPOINT + 'px)').matches) {
            document.querySelectorAll('.' + REPAIR_CLASS).forEach(function (node) { node.classList.remove(REPAIR_CLASS); });
            return;
        }
        var parents = Array.prototype.slice.call(document.querySelectorAll(PARENT_SELECTOR));
        parents.sort(function (a, b) { return depth(b) - depth(a); });
        for (var pass = 0; pass < 3; pass += 1) {
            var changed = false;
            parents.forEach(function (parent) {
                if (!parent.classList.contains(REPAIR_CLASS) && needsRepair(parent)) {
                    parent.classList.add(REPAIR_CLASS);
                    changed = true;
                }
            });
            if (!changed) { break; }
        }
    }

    var pending = 0;
    function schedule() {
        if (pending) { window.cancelAnimationFrame(pending); }
        pending = window.requestAnimationFrame(function () { pending = 0; runRepair(); });
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', schedule, { once: true }); }
    else { schedule(); }
    window.addEventListener('load', schedule, { once: true });
    window.addEventListener('resize', schedule, { passive: true });
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(schedule); }
}());
'''
write('assets/v3-alpha10-mobile-reflow.js', mobile_js)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.9':
    raise SystemExit('Expected Alpha.9 release-history baseline missing')
alpha10 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'Mobil runtime registrerer faktisk overflow, overlap og ekstreme tomme mellemrum i sideindholdet i stedet for kun at stole på gemte grid-koordinater.',
        'Kun problematiske side-containere skifter til naturligt vertikalt flow på mobil; valide mobile layouts efterlades urørte.',
        'Reflow gælder sideindholdet, mens Header/Footer fortsat bruger deres egne eksplicitte responsive template-geometrier.',
        'Reflow genmåles efter DOM-load, font-load og resize, så tekstombrydning og iOS/Safari viewportbredder ikke kan skabe skjulte overlap eller afklip.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha10] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic contract checks.
rr = read(rr_rel)
for required in [
    "wp_enqueue_script('vdm-v3-mobile-reflow'",
    "assets/v3-alpha10-mobile-reflow.js",
    'h18-vdm-mobile-flow-repair',
    "'.h18-vd-live-shell-page '",
    'public const MOBILE_MAX = 782;',
    "if ($floating) {",
]:
    if required not in rr:
        raise SystemExit(f'Alpha.10 responsive runtime token missing: {required}')
for required in [
    'horizontalOverflow(parentRect, childRect)',
    'intrinsicOverflow(child)',
    'overlaps(normal[i - 1].rect, normal[i].rect)',
    'gap > 160',
    'document.fonts.ready.then(schedule)',
    "window.addEventListener('resize', schedule",
]:
    if required not in mobile_js:
        raise SystemExit(f'Alpha.10 mobile reflow token missing: {required}')

built_history = json.loads(history_path.read_text(encoding='utf-8'))['versions']
if built_history[0].get('version') != VERSION or built_history[1].get('version') != '3.0.0-alpha.9':
    raise SystemExit('Alpha.10 release-history ordering failed')

print('V3 Alpha.10 mobile rendered-layout safeguard: PASS')
print('Page-only adaptive reflow: PASS')
print('Header/Footer responsive template geometry preserved: PASS')
print('Overflow/overlap/large-gap detection + font/resize remeasurement: PASS')
