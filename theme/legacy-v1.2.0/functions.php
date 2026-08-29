<?php
/**
 * Hangar18 Base Theme functions.
 *
 * @package Hangar18_Base
 */

if (!defined('ABSPATH')) {
    exit;
}

const H18_BASE_THEME_VERSION = '1.2.2';

const H18_BASE_TRANSITION_CSS_OPTION = 'hangar18_base_transition_css';

const H18_BASE_UPDATE_MANIFEST_URL = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/main/theme-update.json';

const H18_BASE_UPDATE_CACHE_KEY = 'hangar18_base_update_manifest';

function h18_base_theme_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('responsive-embeds');
    add_theme_support('align-wide');

    add_theme_support(
        'html5',
        [
            'search-form',
            'comment-form',
            'comment-list',
            'gallery',
            'caption',
            'style',
            'script',
        ]
    );

    register_nav_menus(
        [
            'primary' => __('Hangar18 primærmenu', 'hangar18-base'),
        ]
    );
}
add_action('after_setup_theme', 'h18_base_theme_setup');

function h18_base_content_width() {
    $GLOBALS['content_width'] = 2400;
}
add_action('after_setup_theme', 'h18_base_content_width', 0);

function h18_base_enqueue_assets() {
    wp_enqueue_style(
        'hangar18-base',
        get_stylesheet_uri(),
        [],
        H18_BASE_THEME_VERSION
    );

    $transition_css = h18_base_get_transition_css();

    if ($transition_css !== '') {
        wp_add_inline_style(
            'hangar18-base',
            "/* Hangar18: bevaret Custom CSS fra det tidligere tema */\n" .
            $transition_css
        );
    }
}
add_action('wp_enqueue_scripts', 'h18_base_enqueue_assets', 20);

/**
 * Henter og validerer temaets GitHub-manifest.
 */
function h18_base_get_update_manifest($force = false) {
    if (!$force) {
        $cached = get_site_transient(H18_BASE_UPDATE_CACHE_KEY);
        if (is_array($cached)) {
            return $cached;
        }
    }

    $response = wp_safe_remote_get(
        H18_BASE_UPDATE_MANIFEST_URL,
        [
            'timeout'    => 15,
            'sslverify'  => true,
            'user-agent' => 'Hangar18-Base-Theme/' . H18_BASE_THEME_VERSION . '; ' . home_url('/'),
            'headers'    => [
                'Accept' => 'application/json',
            ],
        ]
    );

    if (is_wp_error($response)) {
        return [];
    }

    if ((int) wp_remote_retrieve_response_code($response) !== 200) {
        return [];
    }

    $manifest = json_decode((string) wp_remote_retrieve_body($response), true);

    if (!is_array($manifest)) {
        return [];
    }

    $theme          = sanitize_key((string) ($manifest['theme'] ?? ''));
    $version        = sanitize_text_field((string) ($manifest['version'] ?? ''));
    $package_url    = esc_url_raw((string) ($manifest['package_url'] ?? ''));
    $package_host   = strtolower((string) wp_parse_url($package_url, PHP_URL_HOST));
    $package_path   = (string) wp_parse_url($package_url, PHP_URL_PATH);
    $package_sha256 = strtolower(sanitize_text_field((string) ($manifest['package_sha256'] ?? '')));

    $valid = (
        $theme === 'hangar18-base' &&
        preg_match('/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/', $version) &&
        $package_host === 'raw.githubusercontent.com' &&
        str_starts_with($package_path, '/phenixdk2020/hangar18-manager/') &&
        preg_match('/^[a-f0-9]{64}$/', $package_sha256)
    );

    if (!$valid) {
        return [];
    }

    $clean = [
        'theme'            => $theme,
        'version'          => $version,
        'package_url'      => $package_url,
        'package_encoding' => sanitize_key((string) ($manifest['package_encoding'] ?? '')),
        'package_sha256'   => $package_sha256,
        'details_url'      => esc_url_raw((string) ($manifest['details_url'] ?? '')),
        'requires'         => sanitize_text_field((string) ($manifest['requires'] ?? '6.4')),
        'requires_php'     => sanitize_text_field((string) ($manifest['requires_php'] ?? '8.0')),
        'tested'           => sanitize_text_field((string) ($manifest['tested'] ?? '')),
        'last_updated'     => sanitize_text_field((string) ($manifest['last_updated'] ?? '')),
        'changelog'        => wp_kses_post((string) ($manifest['changelog'] ?? '')),
    ];

    set_site_transient(H18_BASE_UPDATE_CACHE_KEY, $clean, 15 * MINUTE_IN_SECONDS);

    return $clean;
}

/**
 * Tilføjer GitHub-versionen til WordPress' normale temaopdateringer.
 */
function h18_base_check_for_update($transient) {
    if (!is_object($transient)) {
        return $transient;
    }

    $manifest = h18_base_get_update_manifest();
    if (empty($manifest)) {
        return $transient;
    }

    $slug = get_stylesheet();
    if ($slug !== 'hangar18-base') {
        return $transient;
    }

    $update = [
        'theme'        => $slug,
        'new_version'  => $manifest['version'],
        'url'          => $manifest['details_url'],
        'package'      => $manifest['package_url'],
        'requires'     => $manifest['requires'],
        'requires_php' => $manifest['requires_php'],
    ];

    if (version_compare(H18_BASE_THEME_VERSION, $manifest['version'], '<')) {
        $transient->response[$slug] = $update;
        unset($transient->no_update[$slug]);
    } else {
        $transient->no_update[$slug] = $update;
        unset($transient->response[$slug]);
    }

    return $transient;
}
add_filter('pre_set_site_transient_update_themes', 'h18_base_check_for_update');

/**
 * Viser versionsdetaljer i WordPress' tema-dialog.
 */
function h18_base_theme_information($result, $action, $args) {
    if ($action !== 'theme_information' || !is_object($args)) {
        return $result;
    }

    if (($args->slug ?? '') !== 'hangar18-base') {
        return $result;
    }

    $manifest = h18_base_get_update_manifest();
    if (empty($manifest)) {
        return $result;
    }

    return (object) [
        'name'          => 'AKVPK',
        'slug'          => 'hangar18-base',
        'version'       => $manifest['version'],
        'author'        => '<a href="https://hangar18.dk/">AKVPK</a>',
        'homepage'      => $manifest['details_url'],
        'requires'      => $manifest['requires'],
        'requires_php'  => $manifest['requires_php'],
        'tested'        => $manifest['tested'],
        'last_updated'  => $manifest['last_updated'],
        'download_link' => $manifest['package_url'],
        'sections'      => [
            'description' => 'Det officielle basistema til Aalborg Kaserners Veteran Panser- og Køretøjsforening.',
            'changelog'   => $manifest['changelog'],
        ],
    ];
}
add_filter('themes_api', 'h18_base_theme_information', 20, 3);

/**
 * GitHub gemmer tema-ZIP'en som Base64-tekst, så den kan publiceres sikkert
 * gennem repositoryets tekstbaserede indholds-API. Her downloades teksten,
 * afkodes til en midlertidig ZIP og kontrolleres mod SHA-256 i manifestet.
 */
function h18_base_pre_download_package($reply, $package, $upgrader, $hook_extra = []) {
    if ($reply !== false) {
        return $reply;
    }

    $manifest = h18_base_get_update_manifest();
    if (empty($manifest) || $package !== $manifest['package_url']) {
        return $reply;
    }

    if ($manifest['package_encoding'] !== 'base64') {
        return new WP_Error(
            'hangar18_invalid_package_encoding',
            __('Hangar18-temapakken har et ukendt format.', 'hangar18-base')
        );
    }

    if (!function_exists('download_url')) {
        require_once ABSPATH . 'wp-admin/includes/file.php';
    }

    $encoded_file = download_url($package, 300, false);
    if (is_wp_error($encoded_file)) {
        return $encoded_file;
    }

    $encoded = file_get_contents($encoded_file);
    @unlink($encoded_file);

    if ($encoded === false) {
        return new WP_Error(
            'hangar18_package_read_failed',
            __('Hangar18-temapakken kunne ikke læses.', 'hangar18-base')
        );
    }

    $decoded = base64_decode(preg_replace('/\s+/', '', $encoded), true);
    if ($decoded === false) {
        return new WP_Error(
            'hangar18_package_decode_failed',
            __('Hangar18-temapakken kunne ikke afkodes.', 'hangar18-base')
        );
    }

    if (!hash_equals($manifest['package_sha256'], hash('sha256', $decoded))) {
        return new WP_Error(
            'hangar18_package_checksum_failed',
            __('Hangar18-temapakkens kontrolsum passer ikke. Opdateringen er stoppet.', 'hangar18-base')
        );
    }

    $zip_file = wp_tempnam('hangar18-base-theme.zip');
    if (!$zip_file || file_put_contents($zip_file, $decoded) === false) {
        return new WP_Error(
            'hangar18_package_write_failed',
            __('Hangar18-temapakken kunne ikke gemmes midlertidigt.', 'hangar18-base')
        );
    }

    return $zip_file;
}
add_filter('upgrader_pre_download', 'h18_base_pre_download_package', 10, 4);

/**
 * Tøm updater-cachen efter en temaupdatering.
 */
function h18_base_clear_update_cache($upgrader, $hook_extra) {
    if (($hook_extra['type'] ?? '') !== 'theme') {
        return;
    }

    delete_site_transient(H18_BASE_UPDATE_CACHE_KEY);
}
add_action('upgrader_process_complete', 'h18_base_clear_update_cache', 10, 2);

/**
 * Returnerer en permanent kopi af Custom CSS fra temaet, der blev afløst.
 *
 * Ved en opgradering fra Base Theme 1.0.0 findes der muligvis endnu ikke et
 * snapshot. I det tilfælde indlæses kendte tidligere stylesheets én gang og
 * gemmes i Base Themes egen option. Dette ændrer eller sletter ikke data hos
 * de tidligere temaer.
 */
function h18_base_get_transition_css() {
    $snapshot = get_option(H18_BASE_TRANSITION_CSS_OPTION, []);

    if (is_array($snapshot) && !empty($snapshot['css'])) {
        return trim((string) $snapshot['css']);
    }

    if (!function_exists('wp_get_custom_css')) {
        return '';
    }

    $stylesheets = [];

    if (is_array($snapshot) && !empty($snapshot['stylesheet'])) {
        $stylesheets[] = sanitize_key((string) $snapshot['stylesheet']);
    }

    /* Kendte temaer fra Hangar18-projektets overgangshistorik. */
    $stylesheets[] = 'astra';
    $stylesheets[] = 'extendable';
    $stylesheets   = array_values(array_unique(array_filter($stylesheets)));

    $css_parts = [];
    $seen      = [];

    foreach ($stylesheets as $stylesheet) {
        $css = trim((string) wp_get_custom_css($stylesheet));

        if ($css === '') {
            continue;
        }

        $hash = hash('sha256', $css);
        if (isset($seen[$hash])) {
            continue;
        }

        $seen[$hash] = true;
        $css_parts[] = "/* Kilde: {$stylesheet} */\n{$css}";
    }

    $combined_css = trim(implode("\n\n", $css_parts));

    if ($combined_css !== '') {
        update_option(
            H18_BASE_TRANSITION_CSS_OPTION,
            [
                'stylesheet'  => 'legacy-fallback',
                'captured_utc'=> gmdate('c'),
                'css'         => $combined_css,
                'sha256'      => hash('sha256', $combined_css),
            ],
            false
        );
    }

    return $combined_css;
}

/**
 * Ingen theme-header/footer/menu skal indsættes automatisk.
 * Hangar18 Manager leverer disse elementer inde i sideindholdet.
 */
function h18_base_body_classes($classes) {
    $classes[] = 'h18-base-theme';

    if (class_exists('Hangar18_Manager')) {
        $classes[] = 'h18-manager-active';
    } else {
        $classes[] = 'h18-manager-missing';
    }

    return $classes;
}
add_filter('body_class', 'h18_base_body_classes');

/**
 * Lille sikkerhedsadvarsel i wp-admin hvis pluginet mangler.
 */
function h18_base_admin_notice() {
    if (!current_user_can('manage_options')) {
        return;
    }

    if (class_exists('Hangar18_Manager')) {
        return;
    }

    echo '<div class="notice notice-warning"><p><strong>Hangar18 Base Theme:</strong> ' .
        esc_html__('Hangar18 Manager er ikke aktiv. Temaet virker stadig, men den administrerede Hangar18-header/footer og specialfunktioner kan mangle.', 'hangar18-base') .
        '</p></div>';
}
add_action('admin_notices', 'h18_base_admin_notice');

/**
 * Når temaet aktiveres, gemmes overgangs-CSS og diagnostik.
 * Vi ændrer ikke sider, menuer, Astra-indstillinger eller plugin-data.
 */
function h18_base_after_switch_theme($old_name = '', $old_theme = null) {
    $old_stylesheet = '';
    $old_css        = '';

    if ($old_theme instanceof WP_Theme) {
        $old_stylesheet = sanitize_key((string) $old_theme->get_stylesheet());
    }

    if ($old_stylesheet !== '' && function_exists('wp_get_custom_css')) {
        $old_css = trim((string) wp_get_custom_css($old_stylesheet));
    }

    update_option(
        H18_BASE_TRANSITION_CSS_OPTION,
        [
            'stylesheet'   => $old_stylesheet,
            'theme_name'   => sanitize_text_field((string) $old_name),
            'captured_utc' => gmdate('c'),
            'css'          => $old_css,
            'sha256'       => $old_css !== '' ? hash('sha256', $old_css) : '',
        ],
        false
    );

    update_option(
        'hangar18_base_theme_activated',
        [
            'version'       => H18_BASE_THEME_VERSION,
            'activated_utc' => gmdate('c'),
            'old_theme_css_preserved' => true,
            'old_theme_stylesheet'     => $old_stylesheet,
        ],
        false
    );
}
add_action('after_switch_theme', 'h18_base_after_switch_theme', 10, 2);
