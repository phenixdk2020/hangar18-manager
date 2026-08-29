from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'clean' / 'hangar18-manager'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Visual Designer Manager 0.1.49
# ---------------------------------------------------------------------------
plugin_path = PLUGIN / 'hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, ' * Version: 0.1.48', ' * Version: 0.1.49', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.48');", "define('H18_CLEAN_VERSION', '0.1.49');", 'plugin constant version')
write(plugin_path, plugin)


# ---------------------------------------------------------------------------
# Theme Shell: explicit user-approved cutover in 0.1.49.
# ---------------------------------------------------------------------------
shell_path = PLUGIN / 'src' / 'Frontend' / 'ThemeShell.php'
shell = read(shell_path)
shell = replace_once(
    shell,
    " * 0.1.31 deliberately prepares the cutover contract without replacing the\n * current Hangar18 Base Theme rendering. Header/Footer activation remains an\n * explicit later step after visual parity has passed on Desktop/Laptop/Mobile.\n",
    " * 0.1.49 activates the approved cutover for Visual Designer pages.\n * Non-Visual-Designer WordPress pages remain untouched as a safe fallback.\n",
    'ThemeShell class contract',
)
shell = replace_once(
    shell,
    "    public const CUTOVER_OPTION = 'h18_visual_designer_theme_shell_cutover_v1';\n",
    "    public const CUTOVER_OPTION = 'h18_visual_designer_theme_shell_cutover_v1';\n    private const V0149_ACTIVATED_OPTION = 'h18_visual_designer_theme_shell_cutover_v0149_activated';\n",
    'ThemeShell activation constant',
)
shell = replace_once(
    shell,
    "    public static function register(): void\n    {\n        add_filter('body_class', [self::class, 'bodyClasses'], 50);\n    }\n",
    "    public static function register(): void\n    {\n        add_action('init', [self::class, 'activateApprovedCutover'], 1);\n        add_filter('body_class', [self::class, 'bodyClasses'], 50);\n    }\n\n    /**\n     * 0.1.49 is the explicit, user-approved cutover point. This runs once.\n     * A rollback to an older plugin stays safe because older Renderers ignore\n     * the flag, while non-Visual-Designer pages are never wrapped by 0.1.49.\n     */\n    public static function activateApprovedCutover(): void\n    {\n        if (get_option(self::V0149_ACTIVATED_OPTION, false)) {\n            return;\n        }\n        update_option(self::CUTOVER_OPTION, '1', false);\n        update_option(self::V0149_ACTIVATED_OPTION, [\n            'activatedUtc' => gmdate('c'),\n            'version' => defined('H18_CLEAN_VERSION') ? H18_CLEAN_VERSION : '0.1.49',\n            'scope' => 'visual-designer-pages-only',\n        ], false);\n    }\n",
    'ThemeShell register/activation',
)
write(shell_path, shell)


# ---------------------------------------------------------------------------
# Live frontend composition: Header -> page model -> Footer.
# Only Visual Designer pages enter this path. Missing/inactive templates are
# omitted without hiding the page, providing the requested safe fallback.
# ---------------------------------------------------------------------------
renderer_path = PLUGIN / 'src' / 'Frontend' / 'Renderer.php'
renderer = read(renderer_path)
renderer = replace_once(
    renderer,
    "use Hangar18\\Clean\\Model\\LayoutModel;\n",
    "use Hangar18\\Clean\\Model\\LayoutModel;\nuse Hangar18\\Clean\\Model\\TemplateLayoutModel;\n",
    'Renderer TemplateLayoutModel import',
)
old_content = """    public static function content(string $content): string
    {
        if (is_admin() || !is_singular('page') || !in_the_loop() || !is_main_query()) {
            return $content;
        }
        $postId = get_the_ID();
        if ($postId <= 0) {
            return $content;
        }
        $preview = self::previewModel($postId);
        if ($preview !== null) {
            return self::renderModel($preview);
        }
        if (!metadata_exists('post', $postId, LayoutModel::META)) {
            return $content;
        }
        $model = LayoutModel::get($postId);
        if (empty($model['nodes'])) {
            return '';
        }
        return self::renderModel($model);
    }
"""
new_content = """    public static function content(string $content): string
    {
        if (is_admin() || !is_singular('page') || !in_the_loop() || !is_main_query()) {
            return $content;
        }
        $postId = get_the_ID();
        if ($postId <= 0) {
            return $content;
        }

        $preview = self::previewModel($postId);
        if ($preview !== null) {
            $pageHtml = empty($preview['nodes']) ? '' : self::renderModel($preview);
            return ThemeShell::enabled() ? self::renderLiveShell($postId, $pageHtml) : $pageHtml;
        }

        // Safe transition rule: legacy/non-Designer pages are untouched.
        if (!metadata_exists('post', $postId, LayoutModel::META)) {
            return $content;
        }

        $model = LayoutModel::get($postId);
        $pageHtml = empty($model['nodes']) ? '' : self::renderModel($model);
        return ThemeShell::enabled() ? self::renderLiveShell($postId, $pageHtml) : $pageHtml;
    }

    private static function renderLiveShell(int $postId, string $pageHtml): string
    {
        $headerId = ThemeShell::resolvedTemplateId($postId, 'header');
        $footerId = ThemeShell::resolvedTemplateId($postId, 'footer');
        $headerHtml = self::renderResolvedTemplate($headerId, 'header');
        $footerHtml = self::renderResolvedTemplate($footerId, 'footer');

        return '<div class="h18-vd-live-shell" data-h18-vd-shell="active" data-h18-vd-header="' . esc_attr($headerId) . '" data-h18-vd-footer="' . esc_attr($footerId) . '">'
            . '<div class="h18-vd-live-shell-part h18-vd-live-shell-header">' . $headerHtml . '</div>'
            . '<div class="h18-vd-live-shell-part h18-vd-live-shell-page">' . $pageHtml . '</div>'
            . '<div class="h18-vd-live-shell-part h18-vd-live-shell-footer">' . $footerHtml . '</div>'
            . '</div>';
    }

    private static function renderResolvedTemplate(string $templateId, string $type): string
    {
        if ($templateId === '') {
            return '';
        }
        try {
            if (!TemplateLayoutModel::exists($templateId, $type)) {
                return '';
            }
            $model = TemplateLayoutModel::model($templateId);
            return empty($model['nodes']) ? '' : self::renderModel($model);
        } catch (\\Throwable $error) {
            // Template failure must never suppress the page itself.
            return '';
        }
    }
"""
renderer = replace_once(renderer, old_content, new_content, 'Renderer content cutover')
renderer = replace_once(
    renderer,
    "        echo '.h18-clean-front-image img{display:block;max-width:none;margin:0;box-sizing:border-box}';\n        echo '</style>';\n",
    "        echo '.h18-clean-front-image img{display:block;max-width:none;margin:0;box-sizing:border-box}';\n        echo '.h18-vd-live-shell,.h18-vd-live-shell-part{display:block;width:100%;max-width:none;margin:0;padding:0;box-sizing:border-box}.h18-vd-live-shell{position:relative}';\n        echo '</style>';\n",
    'Renderer shell CSS',
)
renderer = replace_once(
    renderer,
    "     * Standalone canonical preview used by the Designer while Theme Shell is OFF.\n",
    "     * Standalone canonical preview used by the Designer. It remains isolated\n     * from the active public shell so unsaved work never changes frontend output.\n",
    'Renderer standalone preview comment',
)
write(renderer_path, renderer)


# ---------------------------------------------------------------------------
# Manager: direct WordPress front-page selection and active shell status.
# ---------------------------------------------------------------------------
admin_path = PLUGIN / 'src' / 'Admin' / 'AdminController.php'
admin = read(admin_path)
admin = replace_once(
    admin,
    "use Hangar18\\Clean\\Diagnostics\\DiagnosticStore;\n",
    "use Hangar18\\Clean\\Diagnostics\\DiagnosticStore;\nuse Hangar18\\Clean\\Frontend\\ThemeShell;\n",
    'Admin ThemeShell import',
)
admin = replace_once(
    admin,
    "    private const CREATE_PAGE_ACTION = 'h18_clean_create_page';\n",
    "    private const CREATE_PAGE_ACTION = 'h18_clean_create_page';\n    private const SET_HOME_PAGE_ACTION = 'h18_clean_set_home_page';\n",
    'set-home action constant',
)
admin = replace_once(
    admin,
    "    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';\n",
    "    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';\n    private const SET_HOME_PAGE_NONCE = 'h18_clean_set_home_page';\n",
    'set-home nonce constant',
)
admin = replace_once(
    admin,
    "        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);\n",
    "        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);\n        add_action('admin_post_' . self::SET_HOME_PAGE_ACTION, [self::class, 'setHomePage']);\n",
    'set-home action registration',
)

old_pages_intro = """        self::open('Sider', 'Alle WordPress-sider med Visual Designer-status');
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }
        $landingId = absint(get_option(self::LANDING_PAGE_OPTION, 0));
        if ($landingId > 0 && get_post_type($landingId) === 'page') {
            echo '<div class="h18-manager-card"><h2>Ny Visual Designer-landingsside</h2><p>Separat kladde til Header + indhold + Footer. Den gamle Hjem-side og WordPress-forsiden er ikke ændret.</p><p><a class="button button-primary" href="' . esc_url(self::designerUrl($landingId)) . '">Åbn Hjem – Visual Designer</a> <a class="button" href="' . esc_url(self::url('h18-clean-menu')) . '">Menu · næste arbejdsspor</a></p></div>';
        }
"""
new_pages_intro = """        self::open('Sider', 'Alle WordPress-sider med Visual Designer-status');
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }

        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        $frontPage = $frontId > 0 ? get_post($frontId) : null;
        echo '<div class="h18-manager-card"><h2>Hjemmeside</h2>';
        if ($frontPage instanceof \\WP_Post && $frontPage->post_type === 'page') {
            echo '<p>WordPress-forsiden er <strong>' . esc_html((string) $frontPage->post_title) . '</strong> <span class="h18-manager-badge is-ok">Hjemmeside</span></p>';
            if (metadata_exists('post', $frontId, LayoutModel::META)) {
                echo '<p><a class="button button-primary" href="' . esc_url(self::designerUrl($frontId)) . '">Åbn hjemmesiden i Designer</a></p>';
            } else {
                echo '<p class="description">Den aktuelle forside er endnu ikke en Visual Designer-side. Vælg “Sæt som Hjem” på en Visual Designer-side nedenfor for at skifte sikkert.</p>';
            }
        } else {
            echo '<p>WordPress viser aktuelt de seneste indlæg. Vælg <strong>Sæt som Hjem</strong> på en Visual Designer-side nedenfor.</p>';
        }
        echo '</div>';

        $landingId = absint(get_option(self::LANDING_PAGE_OPTION, 0));
        if ($landingId > 0 && get_post_type($landingId) === 'page') {
            echo '<div class="h18-manager-card"><h2>Hjem – Visual Designer</h2><p>Den separate Visual Designer-landingsside er klar til Header + indhold + Footer. Når du vælger den som Hjem, publiceres den automatisk hvis nødvendigt.</p><div class="h18-manager-toolbar"><a class="button button-primary" href="' . esc_url(self::designerUrl($landingId)) . '">Åbn Hjem – Visual Designer</a>';
            if ($frontId === $landingId) {
                echo '<span class="h18-manager-badge is-ok">Aktiv hjemmeside</span>';
            } elseif (metadata_exists('post', $landingId, LayoutModel::META)) {
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
                wp_nonce_field(self::SET_HOME_PAGE_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::SET_HOME_PAGE_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $landingId) . '"><button class="button" type="submit">Publicér og sæt som Hjem</button></form>';
            }
            echo '</div></div>';
        }
"""
admin = replace_once(admin, old_pages_intro, new_pages_intro, 'pages homepage intro')

admin = replace_once(
    admin,
    "            echo '<tr><td><strong>' . esc_html((string) $page->post_title) . '</strong><br><small>ID ' . esc_html((string) $page->ID) . '</small></td>';\n",
    "            $homeBadge = $frontId === (int) $page->ID ? ' <span class=\"h18-manager-badge is-ok\">Hjemmeside</span>' : '';\n            echo '<tr><td><strong>' . esc_html((string) $page->post_title) . '</strong>' . $homeBadge . '<br><small>ID ' . esc_html((string) $page->ID) . '</small></td>';\n",
    'pages homepage badge',
)
admin = replace_once(
    admin,
    "            if ($permalink) { echo '<a class=\"button\" target=\"_blank\" rel=\"noopener\" href=\"' . esc_url($permalink) . '\">Vis</a>'; }\n            echo '</td></tr>';\n",
    "            if ($permalink) { echo '<a class=\"button\" target=\"_blank\" rel=\"noopener\" href=\"' . esc_url($permalink) . '\">Vis</a>'; }\n            if ($frontId !== (int) $page->ID && metadata_exists('post', $page->ID, LayoutModel::META)) {\n                $homeLabel = (string) $page->post_status === 'publish' ? 'Sæt som Hjem' : 'Publicér og sæt som Hjem';\n                echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\" style=\"display:inline\">';\n                wp_nonce_field(self::SET_HOME_PAGE_NONCE);\n                echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::SET_HOME_PAGE_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $page->ID) . '\"><button class=\"button\" type=\"submit\">' . esc_html($homeLabel) . '</button></form>';\n            }\n            echo '</td></tr>';\n",
    'pages set-home action',
)

old_header_footer = """    public static function headerFooter(): void
    {
        self::guard();
        $theme = wp_get_theme();
        self::open('Header / Footer', 'Tema og global shell');
        echo '<div class="h18-manager-two-col"><div class="h18-manager-card"><h2>Aktivt tema</h2><dl class="h18-manager-dl">';
        echo '<dt>Navn</dt><dd>' . esc_html($theme->get('Name')) . '</dd><dt>Version</dt><dd>' . esc_html($theme->get('Version')) . '</dd><dt>Stylesheet</dt><dd><code>' . esc_html($theme->get_stylesheet()) . '</code></dd></dl>';
        echo '<p><a class="button" href="' . esc_url(admin_url('themes.php')) . '">Temaer</a>';
        if (current_user_can('edit_theme_options')) { echo ' <a class="button" href="' . esc_url(admin_url('customize.php')) . '">Tilpas</a>'; }
        echo '</p></div>';
        echo '<div class="h18-manager-card"><h2>Visual Designer-princip</h2><p>Visual Designer styrer sideindholdets canonical layout. Header, footer og global navigation holdes adskilt fra side-layoutet, så en sideversion ikke utilsigtet ændrer hele sitet.</p><p class="description">Når den globale design-editor porteres, placeres den her frem for at genaktivere den gamle 0.9.x shell-runtime.</p></div></div>';
        self::close();
    }
"""
new_header_footer = """    public static function headerFooter(): void
    {
        self::guard();
        $theme = wp_get_theme();
        TemplateLayoutModel::ensureMigrated();
        $headerId = TemplateLayoutModel::defaultId('header');
        $footerId = TemplateLayoutModel::defaultId('footer');
        $headerMeta = $headerId !== '' ? TemplateLayoutModel::meta($headerId) : null;
        $footerMeta = $footerId !== '' ? TemplateLayoutModel::meta($footerId) : null;

        self::open('Header / Footer', 'Tema og global shell');
        echo '<div class="h18-manager-two-col"><div class="h18-manager-card"><h2>Aktivt tema</h2><dl class="h18-manager-dl">';
        echo '<dt>Navn</dt><dd>' . esc_html($theme->get('Name')) . '</dd><dt>Version</dt><dd>' . esc_html($theme->get('Version')) . '</dd><dt>Stylesheet</dt><dd><code>' . esc_html($theme->get_stylesheet()) . '</code></dd></dl>';
        echo '<p><a class="button" href="' . esc_url(admin_url('themes.php')) . '">Temaer</a>';
        if (current_user_can('edit_theme_options')) { echo ' <a class="button" href="' . esc_url(admin_url('customize.php')) . '">Tilpas</a>'; }
        echo '</p></div>';

        echo '<div class="h18-manager-card"><h2>Shell integration</h2>';
        echo ThemeShell::enabled() ? '<p><span class="h18-manager-badge is-ok">Status: Aktiv</span></p>' : '<p><span class="h18-manager-badge">Status: Inaktiv</span></p>';
        echo '<p>På offentlige <strong>Visual Designer-sider</strong> renderer Manageren nu Header → sideindhold → Footer med den samme canonical renderer som Preview.</p>';
        echo '<dl class="h18-manager-dl"><dt>Standard Header</dt><dd>' . esc_html((string) ($headerMeta['name'] ?? 'Ingen aktiv')) . '</dd><dt>Standard Footer</dt><dd>' . esc_html((string) ($footerMeta['name'] ?? 'Ingen aktiv')) . '</dd></dl>';
        echo '<p class="description">Sider uden Visual Designer-model ændres ikke. Hvis en Header/Footer mangler eller er inaktiv, vises selve siden stadig uden den pågældende del.</p></div></div>';
        self::close();
    }
"""
admin = replace_once(admin, old_header_footer, new_header_footer, 'Header/Footer shell status')

set_home_method = r'''
    public static function setHomePage(): void
    {
        self::guard();
        check_admin_referer(self::SET_HOME_PAGE_NONCE);

        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page' || !current_user_can('edit_post', $postId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den valgte side er ikke gyldig.']));
            exit;
        }
        if (!metadata_exists('post', $postId, LayoutModel::META)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kun en side med Visual Designer-layout kan vælges som ny hjemmeside her.']));
            exit;
        }

        $page = get_post($postId);
        if (!$page instanceof \WP_Post) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke læses.']));
            exit;
        }

        if ((string) $page->post_status !== 'publish') {
            if (!current_user_can('publish_pages')) {
                wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden skal publiceres før den kan være hjemmeside.']));
                exit;
            }
            $published = wp_update_post(['ID' => $postId, 'post_status' => 'publish'], true);
            if (is_wp_error($published) || (int) $published <= 0) {
                $detail = is_wp_error($published) ? $published->get_error_message() : 'Ukendt WordPress-fejl';
                wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke publiceres: ' . $detail]));
                exit;
            }
        }

        if (absint(get_option('page_for_posts', 0)) === $postId) {
            update_option('page_for_posts', 0);
        }
        update_option('show_on_front', 'page');
        update_option('page_on_front', $postId);
        clean_post_cache($postId);

        wp_safe_redirect(self::url('h18-clean-pages', [
            'vd_status' => 'ok',
            'vd_message' => '“' . get_the_title($postId) . '” er nu publiceret og valgt som hjemmeside.',
        ]));
        exit;
    }

'''
admin = replace_once(
    admin,
    "    public static function ensureLandingPage(): void\n",
    set_home_method + "    public static function ensureLandingPage(): void\n",
    'setHomePage method insertion',
)
write(admin_path, admin)


# ---------------------------------------------------------------------------
# AKVPK theme 1.2.2: keep updater identity aligned with visible theme version.
# No layout change is required for 0.1.49 shell composition.
# ---------------------------------------------------------------------------
style_path = ROOT / 'theme' / 'legacy-v1.2.0' / 'style.css'
style = read(style_path)
style = replace_once(style, 'Version: 1.2.1', 'Version: 1.2.2', 'theme style version')
write(style_path, style)

functions_path = ROOT / 'theme' / 'legacy-v1.2.0' / 'functions.php'
functions = read(functions_path)
functions = replace_once(functions, "const H18_BASE_THEME_VERSION = '1.2.0';", "const H18_BASE_THEME_VERSION = '1.2.2';", 'theme runtime version')
functions = replace_once(functions, "        'name'          => 'Hangar18 Base Theme',", "        'name'          => 'AKVPK',", 'theme API visible name')
functions = replace_once(functions, "        'author'        => '<a href=\"https://hangar18.dk/\">Hangar18</a>',", "        'author'        => '<a href=\"https://hangar18.dk/\">AKVPK</a>',", 'theme API author')
write(functions_path, functions)

theme_manifest_path = ROOT / 'theme-update.json'
theme_manifest = json.loads(read(theme_manifest_path))
theme_manifest['version'] = '1.2.2'
theme_manifest['last_updated'] = '2026-08-29T08:52:00Z'
theme_manifest['package_sha256'] = ''
theme_manifest['changelog'] = '<h4>AKVPK 1.2.2</h4><ul><li>Theme runtime-versionen følger nu den synlige WordPress-version, så 1.2.1 ikke tilbydes igen efter installation.</li><li>Theme API viser konsekvent navnet AKVPK.</li><li>Ingen layoutændring; Visual Designer Manager 0.1.49 står for den aktive Header/Page/Footer-shell på Visual Designer-sider.</li></ul>'
write(theme_manifest_path, json.dumps(theme_manifest, ensure_ascii=False, indent=2) + '\n')


# ---------------------------------------------------------------------------
# Release documentation.
# ---------------------------------------------------------------------------
history_path = PLUGIN / 'release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not any(str(row.get('version', '')) == '0.1.49' for row in versions if isinstance(row, dict)):
    versions.insert(0, {
        'version': '0.1.49',
        'date': '2026-08-29',
        'items': [
            'Theme Shell-cutover er aktivt for Visual Designer-sider: Header → side → Footer rendres live med canonical Renderer.',
            'Legacy/non-Designer sider forbliver urørte under overgang; manglende Header/Footer skjuler aldrig siden.',
            'Visual Designer Manager → Sider viser aktuel hjemmeside og kan publicere/sætte en Visual Designer-side som Hjem.',
            'Hjem – Visual Designer kan vælges direkte via “Publicér og sæt som Hjem”.',
            'Header / Footer viser nu Shell integration = Aktiv og de valgte standardtemplates.',
            'AKVPK theme 1.2.2 retter runtime-version/updater-navn uden layoutændringer.',
            'Menu-redesign er fortsat næste separate arbejdsspor.'
        ]
    })
if isinstance(history, dict):
    history['versions'] = versions
else:
    history = {'versions': versions}
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes_path = ROOT / 'clean-release-notes.html'
notes = read(notes_path)
entry = '''<h4>0.1.49 – Aktiv shell og hjemmesidevalg</h4>
<ul>
<li>Visual Designer Header og Footer kan nu bruges live på Visual Designer-sider. Renderer-kæden er Header → side → Footer.</li>
<li>Ikke-konverterede WordPress-sider ændres ikke, og manglende/inaktiv Header eller Footer falder sikkert tilbage til selve siden.</li>
<li>Under <strong>Sider</strong> kan en Visual Designer-side publiceres og vælges som WordPress-hjemmeside direkte i Manageren.</li>
<li><strong>Hjem – Visual Designer</strong> er fortsat separat fra den gamle Hjem-side, indtil brugeren vælger den som Hjem.</li>
<li>Header/Footer-administrationen viser nu den aktive Shell-status samt standard Header/Footer.</li>
<li>AKVPK theme 1.2.2 synkroniserer synlig version og updater-runtime; ingen layoutændring.</li>
</ul>
'''
if '0.1.49 – Aktiv shell og hjemmesidevalg' not in notes:
    marker = '<body>'
    if marker in notes:
        notes = notes.replace(marker, marker + '\n' + entry, 1)
    else:
        notes = entry + notes
write(notes_path, notes)

status_path = ROOT / 'docs' / 'v0149-status.md'
write(status_path, '''# Visual Designer Manager 0.1.49 – status

## Scope
- Aktiv public Theme Shell på Visual Designer-sider.
- Canonical live-rækkefølge: Header → side → Footer.
- Safe fallback: ikke-Designer sider urørte; manglende template udelades uden at skjule siden.
- Manager-side til valg af WordPress-hjemmeside.
- Hjem – Visual Designer kan publiceres og sættes som Hjem direkte.
- AKVPK theme 1.2.2 updater/version identity fix.

## Cutover-kontrakt
0.1.49 er det eksplicit godkendte cutover-punkt. `ThemeShell::activateApprovedCutover()` sætter cutover-flaget én gang. `Renderer::content()` går kun ind i shell-kompositionen, når siden har Visual Designer metadata eller er et Designer-preview. Legacy/non-Designer `post_content` returneres uændret.

## Hjemmeside-kontrakt
Manageren skriver WordPress' standardindstillinger `show_on_front=page` og `page_on_front=<ID>`. Hvis den valgte Visual Designer-side er en kladde, publiceres den først efter capability-check. Den tidligere forside slettes eller ændres ikke.

## QA
Release-gates kontrollerer PHP/JS-syntaks, eksisterende hierarchy/model QA, aktiv cutover, safe fallback-grenen, Header/Footer resolution, set-home WordPress options, 0.1.48 Lag/Button/Fit/BUG-02 regression og AKVPK 1.2.2 updater-version.
''')

tech_path = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
tech = read(tech_path)
section = '''

## 0.1.49 – Aktiv Theme Shell og Hjemmeside

### VD-SHELL-LIVE-001
Når Theme Shell er aktiv på en side med canonical Visual Designer-model, er live-rendering: valgt/Auto Header → sidens canonical model → valgt/Auto Footer. Alle tre dele bruger samme `Renderer::renderModel()` som preview.

### VD-SHELL-FALLBACK-001
Theme Shell må ikke overtage legacy/non-Visual-Designer sider under overgang. Hvis en resolved Header/Footer mangler, er inaktiv, tom eller fejler, udelades kun den del; sideindholdet skal fortsat rendres.

### VD-HOME-001
Visual Designer Manager → Sider er autoritativ UX for at vælge hjemmesiden. Handlingen må kun vælge en Visual Designer-side, publicerer den ved behov efter capability-check og skriver WordPress-standarderne `show_on_front=page` + `page_on_front=<ID>`. Den gamle forside slettes ikke.

### VD-CUTOVER-0149
0.1.49 er det eksplicit godkendte Header/Footer cutover. Cutover aktiveres én gang ved runtime og markerer `h18_visual_designer_theme_shell_cutover_v1=1`. Menu-redesign er ikke en del af denne kontrakt.
'''
if '## 0.1.49 – Aktiv Theme Shell og Hjemmeside' not in tech:
    tech += section
write(tech_path, tech)

print('Visual Designer Manager 0.1.49 shell/home patch applied.')
