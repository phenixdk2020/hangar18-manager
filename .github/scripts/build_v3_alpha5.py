from pathlib import Path
import hashlib
import subprocess

VERSION = '3.0.0-alpha.5'
DEST = Path('build/visual-designer-manager')

SITE_TEMPLATE = r'''<?php

declare(strict_types=1);

defined('ABSPATH') || exit;
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
<style id="vdm-site-shell-reset">
body.vdm-site-shell{margin:0;padding:0;width:100%;min-width:0;max-width:none;overflow-x:hidden}
body.vdm-site-shell #vdm-site-shell-root{display:block;width:100%;max-width:none;margin:0;padding:0;box-sizing:border-box}
body.vdm-site-shell .h18-vd-live-shell,body.vdm-site-shell .h18-vd-live-shell-part{display:block;width:100%;max-width:none;margin:0;padding:0;box-sizing:border-box}
body.vdm-site-shell .h18-vd-live-shell-page{min-width:0}
</style>
</head>
<body <?php body_class('vdm-site-shell'); ?>>
<?php wp_body_open(); ?>
<div id="vdm-site-shell-root" data-vdm-site-shell="active">
<?php
if (have_posts()) {
    while (have_posts()) {
        the_post();
        the_content();
    }
}
?>
</div>
<?php wp_footer(); ?>
</body>
</html>
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Alpha.5 layers only the true frontend shell on the verified Alpha.4 package.
subprocess.run(['python3', '.github/scripts/build_v3_alpha4.py'], check=True)

# The imported V1 Designer, viewport, storage and layout model are protected.
protected = [
    'assets/editor-v018-core.js',
    'assets/editor-v0144-viewport.js',
    'assets/editor-v0169-canvas-height.js',
    'assets/editor.css',
    'src/Frontend/Renderer.php',
    'src/Frontend/ResponsiveRenderer.php',
    'src/Model/LayoutModel.php',
    'src/Migration/V3StorageMigration.php',
]
protected_before = {rel: sha(DEST / rel) for rel in protected}

main = DEST / 'visual-designer-manager.php'
main_text = main.read_text(encoding='utf-8')
for old, new in [
    (' * Version: 3.0.0-alpha.4', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.4');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.4');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main_text.count(old) != 1:
        raise SystemExit(f'Alpha.5 version token mismatch: {old!r} count={main_text.count(old)}')
    main_text = main_text.replace(old, new)
main.write_text(main_text, encoding='utf-8')

# Convert ThemeShell from an in-content wrapper coordinator into the owner of
# the WordPress template only for pages that actually carry a VDM layout.
theme = DEST / 'src/Frontend/ThemeShell.php'
theme_text = theme.read_text(encoding='utf-8')

import_anchor = 'use VisualDesignerManager\\Model\\TemplateLayoutModel;'
if theme_text.count(import_anchor) != 1:
    raise SystemExit('ThemeShell import anchor mismatch')
theme_text = theme_text.replace(
    import_anchor,
    'use VisualDesignerManager\\Model\\LayoutModel;\n' + import_anchor,
)

register_old = """    public static function register(): void
    {
        add_action('init', [self::class, 'activateApprovedCutover'], 1);
        add_filter('body_class', [self::class, 'bodyClasses'], 50);
    }
"""
register_new = """    public static function register(): void
    {
        add_action('init', [self::class, 'activateApprovedCutover'], 1);
        add_filter('body_class', [self::class, 'bodyClasses'], 50);
        add_filter('template_include', [self::class, 'templateInclude'], 999);
    }
"""
if theme_text.count(register_old) != 1:
    raise SystemExit('ThemeShell register anchor mismatch')
theme_text = theme_text.replace(register_old, register_new)

body_old = """    public static function bodyClasses(array $classes): array
    {
        $classes[] = 'h18-vd-theme-shell-ready';
        if (self::enabled()) {
            $classes[] = 'h18-vd-theme-shell-active';
        }
        return array_values(array_unique($classes));
    }
"""
body_new = """    public static function bodyClasses(array $classes): array
    {
        $classes[] = 'h18-vd-theme-shell-ready';
        if (self::enabled()) {
            $classes[] = 'h18-vd-theme-shell-active';
        }
        if (self::ownsCurrentRequest()) {
            $classes[] = 'vdm-site-shell';
        }
        return array_values(array_unique($classes));
    }

    /**
     * True shell ownership is deliberately narrow: only singular WordPress
     * pages carrying canonical VDM layout data can bypass the active theme's
     * page template. Ordinary WordPress pages remain theme-owned.
     */
    public static function ownsCurrentRequest(): bool
    {
        if (is_admin() || !self::enabled() || !is_singular('page')) {
            return false;
        }
        $postId = (int) get_queried_object_id();
        return $postId > 0 && metadata_exists('post', $postId, LayoutModel::META);
    }

    /**
     * Replace the theme template, not its styles or WordPress lifecycle hooks.
     * The standalone VDM template still calls wp_head(), wp_body_open() and
     * wp_footer(), but never get_header()/get_footer()/the_title().
     */
    public static function templateInclude(string $template): string
    {
        if (!self::ownsCurrentRequest()) {
            return $template;
        }
        $standalone = VDM_DIR . 'templates/vdm-site-shell.php';
        return is_readable($standalone) ? $standalone : $template;
    }
"""
if theme_text.count(body_old) != 1:
    raise SystemExit('ThemeShell bodyClasses anchor mismatch')
theme_text = theme_text.replace(body_old, body_new)
theme.write_text(theme_text, encoding='utf-8')

template = DEST / 'templates/vdm-site-shell.php'
template.parent.mkdir(parents=True, exist_ok=True)
template.write_text(SITE_TEMPLATE, encoding='utf-8')

# Contract checks inside the deterministic build.
if "add_filter('template_include', [self::class, 'templateInclude'], 999);" not in theme_text:
    raise SystemExit('True template ownership filter missing')
if "metadata_exists('post', $postId, LayoutModel::META)" not in theme_text:
    raise SystemExit('VDM page ownership guard missing')
if "VDM_DIR . 'templates/vdm-site-shell.php'" not in theme_text:
    raise SystemExit('Standalone shell path missing')

template_text = template.read_text(encoding='utf-8')
for required in ('wp_head();', 'wp_body_open();', 'the_content();', 'wp_footer();', 'data-vdm-site-shell="active"'):
    if required not in template_text:
        raise SystemExit(f'Standalone shell lifecycle token missing: {required}')
for forbidden in ('get_header(', 'get_footer(', 'the_title('):
    if forbidden in template_text:
        raise SystemExit(f'Theme-owned output leaked into standalone shell: {forbidden}')

# Alpha.5 must not mutate the already imported layout/storage or the V1
# Designer/viewport. The fixed 1920px virtual desktop and Fit-as-transform
# behavior are deliberately retained byte-for-byte.
for rel, before in protected_before.items():
    after = sha(DEST / rel)
    if before != after:
        raise SystemExit(f'Protected V1/V3 runtime changed during Alpha.5 shell cutover: {rel}')

viewport_text = (DEST / 'assets/editor-v0144-viewport.js').read_text(encoding='utf-8')
for required in (
    'desktop: 1920',
    "mode = 'fit'",
    "root.style.transform = 'scale(' + currentScale + ')'",
    "root.style.width = currentWidth + 'px'",
):
    if required not in viewport_text:
        raise SystemExit(f'Designer viewport parity contract missing: {required}')

print('V3 Alpha.5 true site shell: PASS')
print('Theme header/footer/page-title bypass for VDM layout pages: PASS')
print('WordPress wp_head/wp_body_open/wp_footer lifecycle retained: PASS')
print('V1 Designer 1920px virtual viewport + Fit zoom preserved byte-for-byte: PASS')
print('Alpha.3 storage and imported layout data preserved: PASS')
