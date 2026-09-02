from pathlib import Path
import json

ROOT = Path('.')


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# Version + ManualController bootstrap
# -----------------------------------------------------------------------------
plugin_path = 'clean/hangar18-manager/hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, ' * Version: 0.1.82', ' * Version: 0.1.83', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.82');", "define('H18_CLEAN_VERSION', '0.1.83');", 'runtime version')

require_anchor = "require_once H18_CLEAN_DIR . 'src/Admin/AdminController.php';\n"
require_line = "require_once H18_CLEAN_DIR . 'src/Admin/ManualController.php';\n"
if require_line not in plugin:
    plugin = replace_once(plugin, require_anchor, require_anchor + require_line, 'manual controller require')

register_anchor = "    \\VisualDesignerManager\\Admin\\AdminController::register();\n"
register_line = "    \\VisualDesignerManager\\Admin\\ManualController::register();\n"
if register_line not in plugin:
    plugin = replace_once(plugin, register_anchor, register_anchor + register_line, 'manual controller register')
write(plugin_path, plugin)


# -----------------------------------------------------------------------------
# Public/manual controller. One canonical Markdown source is converted at release
# time to HTML for the website and DOCX for download.
# -----------------------------------------------------------------------------
manual_controller = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

final class ManualController
{
    public const PAGE_SLUG = 'visual-designer-brugermanual';
    public const SHORTCODE = 'visual_designer_manager_manual';

    private const PAGE_OPTION = 'h18_vd_user_manual_page_id_v0183';
    private const HTML_FILE = 'docs/user-manual.html';
    private const DOCX_FILE = 'docs/visual-designer-manager-brugermanual.docx';
    private const STYLE_HANDLE = 'h18-vd-user-manual-v0183';

    public static function register(): void
    {
        add_shortcode(self::SHORTCODE, [self::class, 'shortcode']);
        add_action('admin_init', [self::class, 'ensurePage'], 40);
        add_action('wp_enqueue_scripts', [self::class, 'enqueueFrontend']);
    }

    public static function ensurePage(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $storedId = absint(get_option(self::PAGE_OPTION, 0));
        if ($storedId > 0) {
            $stored = get_post($storedId);
            if ($stored instanceof \WP_Post && $stored->post_type === 'page' && $stored->post_status !== 'trash') {
                return;
            }
        }

        $existing = get_page_by_path(self::PAGE_SLUG, OBJECT, 'page');
        if ($existing instanceof \WP_Post && $existing->post_status !== 'trash') {
            if (!has_shortcode((string) $existing->post_content, self::SHORTCODE)) {
                wp_update_post([
                    'ID' => (int) $existing->ID,
                    'post_content' => '[' . self::SHORTCODE . ']',
                ]);
            }
            update_option(self::PAGE_OPTION, (int) $existing->ID, false);
            return;
        }

        $pageId = wp_insert_post([
            'post_type' => 'page',
            'post_status' => 'publish',
            'post_title' => 'Brugermanual',
            'post_name' => self::PAGE_SLUG,
            'post_content' => '[' . self::SHORTCODE . ']',
            'comment_status' => 'closed',
            'ping_status' => 'closed',
        ], true);

        if (!is_wp_error($pageId) && (int) $pageId > 0) {
            update_option(self::PAGE_OPTION, (int) $pageId, false);
        }
    }

    public static function enqueueFrontend(): void
    {
        if (!is_singular('page')) {
            return;
        }
        $post = get_post();
        if (!$post instanceof \WP_Post || !has_shortcode((string) $post->post_content, self::SHORTCODE)) {
            return;
        }
        self::enqueueAssets();
    }

    public static function shortcode(): string
    {
        self::enqueueAssets();
        return self::renderManual(false);
    }

    public static function adminPage(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke adgang til denne side.', 'visual-designer-manager'));
        }
        self::ensurePage();
        self::enqueueAssets();

        echo '<div class="wrap h18-vd-manual-admin">';
        echo '<h1>Brugermanual</h1>';
        echo '<p>Den samme kanoniske brugermanual vises på websitet og leveres som Word-fil i denne Visual Designer Manager-version.</p>';
        echo self::toolbar(true); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
        echo self::renderManual(true); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
        echo '</div>';
    }

    public static function websiteUrl(): string
    {
        $pageId = absint(get_option(self::PAGE_OPTION, 0));
        if ($pageId > 0) {
            $permalink = get_permalink($pageId);
            if (is_string($permalink) && $permalink !== '') {
                return $permalink;
            }
        }
        return home_url('/' . self::PAGE_SLUG . '/');
    }

    public static function downloadUrl(): string
    {
        return H18_CLEAN_URL . self::DOCX_FILE;
    }

    private static function renderManual(bool $admin): string
    {
        $path = H18_CLEAN_DIR . self::HTML_FILE;
        if (!is_file($path) || !is_readable($path)) {
            return '<div class="h18-vd-manual-notice"><strong>Brugermanualen mangler i denne installation.</strong><br>Installer eller opdatér Visual Designer Manager igen, så de genererede manualfiler kommer med.</div>';
        }

        $html = file_get_contents($path);
        if (!is_string($html) || trim($html) === '') {
            return '<div class="h18-vd-manual-notice"><strong>Brugermanualen kunne ikke læses.</strong></div>';
        }

        $assetBase = H18_CLEAN_URL . 'docs/user-manual-assets/';
        $html = str_replace('src="docs/user-manual-assets/', 'src="' . esc_url($assetBase), $html);
        $html = str_replace("src='docs/user-manual-assets/", "src='" . esc_url($assetBase), $html);

        $toolbar = $admin ? '' : self::toolbar(false);
        return '<div class="h18-vd-manual">' . $toolbar . '<article class="h18-vd-manual-content">' . $html . '</article></div>';
    }

    private static function toolbar(bool $admin): string
    {
        $managerUrl = admin_url('admin.php?page=' . AdminController::MENU);
        $websiteUrl = self::websiteUrl();
        $downloadUrl = self::downloadUrl();

        $html = '<div class="h18-vd-manual-toolbar">';
        if ($admin) {
            $html .= '<a class="button button-primary" href="' . esc_url($websiteUrl) . '" target="_blank" rel="noopener">Åbn på websitet</a>';
        } else {
            $html .= '<a class="h18-vd-manual-button is-primary" href="' . esc_url($managerUrl) . '">Åbn Visual Designer Manager</a>';
        }
        $html .= '<a class="' . ($admin ? 'button' : 'h18-vd-manual-button') . '" href="' . esc_url($downloadUrl) . '" download>Download som Word (.docx)</a>';
        $html .= '</div>';
        return $html;
    }

    private static function enqueueAssets(): void
    {
        wp_enqueue_style(self::STYLE_HANDLE, H18_CLEAN_URL . 'assets/manual-v0183.css', [], H18_CLEAN_VERSION);
    }

    private function __construct()
    {
    }
}
'''
write('clean/hangar18-manager/src/Admin/ManualController.php', manual_controller)

manual_css = r'''.h18-vd-manual{max-width:1180px;margin:0 auto;padding:24px clamp(16px,3vw,42px) 56px;box-sizing:border-box;color:#1d2327;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.h18-vd-manual-toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 28px}.h18-vd-manual-button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 16px;border:1px solid #2271b1;border-radius:6px;background:#fff;color:#135e96;text-decoration:none;font-weight:600;box-sizing:border-box}.h18-vd-manual-button:hover,.h18-vd-manual-button:focus{background:#f0f6fc;color:#0a4b78}.h18-vd-manual-button.is-primary{background:#2271b1;color:#fff}.h18-vd-manual-button.is-primary:hover,.h18-vd-manual-button.is-primary:focus{background:#135e96;color:#fff}.h18-vd-manual-content{font-size:16px;line-height:1.65}.h18-vd-manual-content h1{font-size:clamp(30px,4vw,46px);line-height:1.12;margin:0 0 18px}.h18-vd-manual-content h2{font-size:clamp(24px,3vw,32px);line-height:1.2;margin:42px 0 16px;padding-top:8px;border-top:1px solid #dcdcde}.h18-vd-manual-content h3{font-size:21px;line-height:1.3;margin:30px 0 12px}.h18-vd-manual-content h4{font-size:18px;margin:24px 0 10px}.h18-vd-manual-content p,.h18-vd-manual-content ul,.h18-vd-manual-content ol{max-width:900px}.h18-vd-manual-content img{display:block;max-width:100%;height:auto;margin:22px auto;border:1px solid #dcdcde;border-radius:8px;background:#fff}.h18-vd-manual-content table{width:100%;border-collapse:collapse;margin:20px 0 30px;background:#fff}.h18-vd-manual-content th,.h18-vd-manual-content td{padding:10px 12px;border:1px solid #c3c4c7;vertical-align:top;text-align:left}.h18-vd-manual-content th{background:#f0f0f1}.h18-vd-manual-content pre{overflow:auto;padding:16px;border-radius:7px;background:#1d2327;color:#f6f7f7;line-height:1.45}.h18-vd-manual-content code{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}.h18-vd-manual-content blockquote{margin:20px 0;padding:4px 18px;border-left:4px solid #72aee6;background:#f6f7f7}.h18-vd-manual-notice{padding:16px 18px;border-left:4px solid #dba617;background:#fcf9e8}.h18-vd-manual-admin .h18-vd-manual{max-width:none;padding-left:0;padding-right:0}.h18-vd-manual-admin>.h18-vd-manual-toolbar{margin:18px 0 24px}@media(max-width:782px){.h18-vd-manual{padding-top:18px}.h18-vd-manual-toolbar{align-items:stretch}.h18-vd-manual-button,.h18-vd-manual-toolbar .button{width:100%;text-align:center}.h18-vd-manual-content{font-size:15px}.h18-vd-manual-content table{display:block;overflow-x:auto;white-space:normal}}
'''
write('clean/hangar18-manager/assets/manual-v0183.css', manual_css)


# -----------------------------------------------------------------------------
# Manager menu + dashboard entry
# -----------------------------------------------------------------------------
admin_path = 'clean/hangar18-manager/src/Admin/AdminController.php'
admin = read(admin_path)
menu_anchor = "        add_submenu_page(self::MENU, 'Log', 'Log', $cap, 'h18-clean-log', [self::class, 'log']);\n"
menu_line = "        add_submenu_page(self::MENU, 'Brugermanual', 'Brugermanual', $cap, 'h18-clean-manual', [ManualController::class, 'adminPage']);\n"
if menu_line not in admin:
    admin = replace_once(admin, menu_anchor, menu_anchor + menu_line, 'manual submenu')

card_anchor = "        self::card('Menu', 'Redigér WordPress-menuens punkter og rækkefølge i en brugervenlig VDM-visning. Samme menu bruges direkte af Visual Designer.', self::url('h18-clean-menu'), 'Redigér Menu');\n"
card_line = "        self::card('Brugermanual', 'Læs den komplette brugermanual på websitet eller download den som Word-fil.', ManualController::websiteUrl(), 'Åbn brugermanual');\n"
if card_line not in admin:
    admin = replace_once(admin, card_anchor, card_anchor + card_line, 'manual dashboard card')
write(admin_path, admin)

admin_js_path = 'clean/hangar18-manager/assets/admin-v0123.js'
admin_js = read(admin_js_path)
status_anchor = "        'h18-clean-gallery': ['Klar', 'ready'],\n"
status_line = "        'h18-clean-manual': ['Klar', 'ready'],\n"
if status_line not in admin_js:
    admin_js = replace_once(admin_js, status_anchor, status_anchor + status_line, 'manual status')
write(admin_js_path, admin_js)


# -----------------------------------------------------------------------------
# Canonical user manual documents its new access paths.
# -----------------------------------------------------------------------------
manual_path = 'CLEAN-USER-MANUAL.md'
manual = read(manual_path)
manual = manual.replace('Senest opdateret: 28. august 2026', 'Senest opdateret: 2. september 2026', 1)
manual = manual.replace('Gælder for: Visual Designer Manager 0.1.39 og nyere; planlagte funktioner er mærket **Planlagt**', 'Gælder for: Visual Designer Manager 0.1.83 og nyere; planlagte funktioner er mærket **Planlagt**', 1)
manual_anchor = '> Denne manual beskriver **hvordan Visual Designer Manager bruges i praksis**. Den tekniske arkitektur er beskrevet separat i `CLEAN-DESIGN-MANUAL.md`.\n\n---\n\n'
manual_section = '''> Denne manual beskriver **hvordan Visual Designer Manager bruges i praksis**. Den tekniske arkitektur er beskrevet separat i `CLEAN-DESIGN-MANUAL.md`.\n\n---\n\n## Brugermanualen på websitet\n\nFra Visual Designer Manager 0.1.83 findes brugermanualen også som en almindelig side på websitet med adressen **`/visual-designer-brugermanual/`**. Siden oprettes automatisk, når en administrator åbner WordPress efter opdateringen.\n\nDu kan åbne den fra **Visual Designer Manager → Brugermanual** eller fra kortet **Brugermanual** på Managerens Dashboard. På websiden kan du vælge **Åbn Visual Designer Manager** for at gå tilbage til administrationen.\n\nKnappen **Download som Word (.docx)** henter den samme manual som en rigtig Word-fil. Webvisningen og Word-filen genereres begge fra den kanoniske kilde **`CLEAN-USER-MANUAL.md`** ved release, så de ikke vedligeholdes som to forskellige manualer.\n\n---\n\n'''
if '## Brugermanualen på websitet' not in manual:
    manual = replace_once(manual, manual_anchor, manual_section, 'manual web access section')
write(manual_path, manual)


# -----------------------------------------------------------------------------
# Release metadata
# -----------------------------------------------------------------------------
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', [])
if not isinstance(versions, list):
    raise SystemExit('release history versions is not a list')
if not any(isinstance(row, dict) and row.get('version') == '0.1.83' for row in versions):
    versions.insert(0, {
        'version': '0.1.83',
        'date': '2026-09-02',
        'items': [
            'VD-USER-MANUAL-WEB-001: brugermanualen provisioneres automatisk som offentlig WordPress-side og kan åbnes fra Visual Designer Manager.',
            'Webvisning og Word-download genereres fra samme kanoniske CLEAN-USER-MANUAL.md ved release.',
            'Brugermanual-siden linker tilbage til Visual Designer Manager og tilbyder direkte download som .docx.',
            'Manualens SVG-illustrationer pakkes sammen med pluginet og vises responsivt på websitet.'
        ]
    })
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes_path = 'clean-release-notes.html'
notes = read(notes_path)
section = '<section data-version="0.1.83"><h2>0.1.83</h2><ul><li>Brugermanual er nu en side i Visual Designer Manager og provisioneres automatisk på websitet.</li><li>Webmanualen har direkte link tilbage til Visual Designer Manager.</li><li>Manualen kan downloades som en rigtig Word-fil (.docx).</li><li>Web- og Word-versionen genereres fra samme kanoniske manual ved release.</li></ul></section>\n'
if 'data-version="0.1.83"' not in notes:
    notes = section + notes
write(notes_path, notes)

status = '''# Visual Designer Manager v0.1.83 – status\n\nDato: 2. september 2026\n\n## VD-USER-MANUAL-WEB-001\n\nStatus: **Klar til release**\n\n- Brugermanual findes som Manager-menupunkt og dashboardkort.\n- WordPress-siden `/visual-designer-brugermanual/` provisioneres automatisk.\n- Websiden kan åbne Visual Designer Manager igen.\n- Word-download leveres som `.docx`.\n- HTML, DOCX og illustrationer genereres/pakkes fra `CLEAN-USER-MANUAL.md` i den centrale release-workflow.\n- Web- og Word-manualen har derfor samme kanoniske indholdskilde.\n'''
write('docs/v0183-status.md', status)


# -----------------------------------------------------------------------------
# Central release builds HTML + DOCX from the canonical Markdown before ZIP.
# -----------------------------------------------------------------------------
workflow_path = '.github/workflows/visual-designer-release.yml'
workflow = read(workflow_path)
qa_anchor = "          python3 .github/scripts/v0172_gallery_design_qa.py\n"
qa_line = "          python3 .github/scripts/v0183_user_manual_qa.py\n"
if qa_line not in workflow:
    workflow = replace_once(workflow, qa_anchor, qa_anchor + qa_line, 'v0183 release QA')

build_anchor = "      - name: Build package and manifest\n"
manual_build = '''      - name: Build user manual artifacts\n        shell: bash\n        run: |\n          set -euo pipefail\n          sudo apt-get update -qq\n          sudo apt-get install -y --no-install-recommends pandoc\n          rm -rf clean/hangar18-manager/docs\n          mkdir -p clean/hangar18-manager/docs/user-manual-assets\n          cp CLEAN-USER-MANUAL.md clean/hangar18-manager/docs/user-manual.md\n          cp -R docs/user-manual-assets/. clean/hangar18-manager/docs/user-manual-assets/\n          pandoc CLEAN-USER-MANUAL.md --from=gfm --to=html5 --resource-path=. -o clean/hangar18-manager/docs/user-manual.html\n          pandoc CLEAN-USER-MANUAL.md --from=gfm --resource-path=. -o clean/hangar18-manager/docs/visual-designer-manager-brugermanual.docx\n          test -s clean/hangar18-manager/docs/user-manual.html\n          test -s clean/hangar18-manager/docs/visual-designer-manager-brugermanual.docx\n          test -s clean/hangar18-manager/docs/user-manual-assets/page-anatomy.svg\n\n'''
if '      - name: Build user manual artifacts\n' not in workflow:
    workflow = replace_once(workflow, build_anchor, manual_build + build_anchor, 'manual artifact build step')

package_anchor = "          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/src/Admin/GalleryAdminController.php$')\" = '1'\n"
package_tests = package_anchor + "          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/src/Admin/ManualController.php$')\" = '1'\n          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/docs/user-manual.html$')\" = '1'\n          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/docs/visual-designer-manager-brugermanual.docx$')\" = '1'\n          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/docs/user-manual-assets/page-anatomy.svg$')\" = '1'\n"
if "hangar18-manager/docs/visual-designer-manager-brugermanual.docx" not in workflow:
    workflow = replace_once(workflow, package_anchor, package_tests, 'manual package verification')
write(workflow_path, workflow)

print('Applied Visual Designer Manager v0.1.83 user manual web/Word feature.')
