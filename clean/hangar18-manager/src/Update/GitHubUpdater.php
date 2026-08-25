<?php

declare(strict_types=1);

namespace Hangar18\Clean\Update;

final class GitHubUpdater
{
    private const MANIFEST_URL = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/main/clean-update.json';
    private const CACHE_KEY = 'h18_clean_github_update_manifest_v1';
    private const CHECK_ACTION = 'h18_clean_check_update';
    private const CHECK_NONCE = 'h18_clean_check_update';
    private const INSTALL_ACTION = 'h18_clean_install_update';
    private const INSTALL_NONCE = 'h18_clean_install_update';
    private const SLUG = 'hangar18-manager';
    private const PLUGIN_FILE = 'hangar18-manager/hangar18-manager.php';

    public static function register(): void
    {
        add_filter('pre_set_site_transient_update_plugins', [self::class, 'injectUpdate']);
        add_filter('plugins_api', [self::class, 'pluginInfo'], 20, 3);
        add_filter('upgrader_pre_download', [self::class, 'verifyDownload'], 20, 4);
        add_action('admin_post_' . self::CHECK_ACTION, [self::class, 'manualCheck']);
        add_action('admin_post_' . self::INSTALL_ACTION, [self::class, 'installNow']);
        add_action('upgrader_process_complete', [self::class, 'clearCache'], 10, 2);
        add_action('admin_notices', [self::class, 'adminNotice']);
    }

    public static function injectUpdate(mixed $transient): mixed
    {
        if (!is_object($transient) || !isset($transient->checked) || !is_array($transient->checked)) {
            return $transient;
        }

        $manifest = self::manifest();
        if ($manifest === null) {
            return $transient;
        }

        $item = self::updateObject($manifest);
        if (version_compare((string) $manifest['version'], H18_CLEAN_VERSION, '>')) {
            $transient->response[self::PLUGIN_FILE] = $item;
            if (isset($transient->no_update[self::PLUGIN_FILE])) {
                unset($transient->no_update[self::PLUGIN_FILE]);
            }
        } else {
            $transient->no_update[self::PLUGIN_FILE] = $item;
            if (isset($transient->response[self::PLUGIN_FILE])) {
                unset($transient->response[self::PLUGIN_FILE]);
            }
        }

        return $transient;
    }

    public static function pluginInfo(mixed $result, string $action, mixed $args): mixed
    {
        if ($action !== 'plugin_information' || !is_object($args) || (string) ($args->slug ?? '') !== self::SLUG) {
            return $result;
        }

        $manifest = self::manifest();
        if ($manifest === null) {
            return $result;
        }

        $info = new \stdClass();
        $info->name = (string) ($manifest['name'] ?? 'Hangar18 Manager Clean');
        $info->slug = self::SLUG;
        $info->version = (string) $manifest['version'];
        $info->author = '<a href="https://hangar18.dk/">Hangar18</a>';
        $info->homepage = (string) ($manifest['homepage'] ?? 'https://hangar18.dk/');
        $info->requires = (string) ($manifest['requires'] ?? '6.4');
        $info->requires_php = (string) ($manifest['requires_php'] ?? '8.0');
        $info->tested = (string) ($manifest['tested'] ?? '');
        $info->download_link = (string) $manifest['package'];
        $info->sections = is_array($manifest['sections'] ?? null) ? $manifest['sections'] : [
            'description' => 'Hangar18 Clean Designer.',
            'changelog' => '',
        ];
        return $info;
    }

    public static function verifyDownload(mixed $reply, string $package, mixed $upgrader, array $hookExtra = []): mixed
    {
        if ($reply !== false) {
            return $reply;
        }
        if (($hookExtra['plugin'] ?? '') !== self::PLUGIN_FILE) {
            return false;
        }

        $manifest = self::manifest(true);
        if ($manifest === null || $package !== (string) $manifest['package']) {
            return false;
        }

        $expected = strtolower((string) ($manifest['sha256'] ?? ''));
        if (!preg_match('/^[a-f0-9]{64}$/', $expected)) {
            return new \WP_Error('h18_clean_update_hash_missing', 'GitHub-manifestet mangler en gyldig SHA-256 for update-pakken.');
        }

        require_once ABSPATH . 'wp-admin/includes/file.php';
        $file = download_url($package, 300, false);
        if (is_wp_error($file)) {
            return $file;
        }
        $actual = strtolower((string) hash_file('sha256', $file));
        if (!hash_equals($expected, $actual)) {
            @unlink($file);
            return new \WP_Error('h18_clean_update_hash_mismatch', 'Hangar18 update-pakken blev afvist: SHA-256 matcher ikke GitHub-manifestet.');
        }
        return $file;
    }

    public static function manualCheck(): void
    {
        if (!current_user_can('update_plugins')) {
            wp_die(esc_html__('Ingen adgang til plugin-opdateringer.', 'hangar18-manager-clean'));
        }
        check_admin_referer(self::CHECK_NONCE);

        self::clearCache();
        delete_site_transient('update_plugins');
        wp_clean_plugins_cache(true);
        require_once ABSPATH . 'wp-admin/includes/update.php';
        wp_update_plugins();

        $manifest = self::manifest(true);
        $status = 'error';
        $version = '';
        if ($manifest !== null) {
            $version = (string) $manifest['version'];
            $status = version_compare($version, H18_CLEAN_VERSION, '>') ? 'available' : 'current';
        }

        self::redirectToUpdates([
            'h18_clean_update_check' => $status,
            'h18_clean_update_version' => $version,
        ]);
    }

    public static function checkButtonHtml(): string
    {
        if (!current_user_can('update_plugins')) {
            return '';
        }
        return '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-clean-update-check">'
            . '<input type="hidden" name="action" value="' . esc_attr(self::CHECK_ACTION) . '">'
            . '<input type="hidden" name="_wpnonce" value="' . esc_attr(wp_create_nonce(self::CHECK_NONCE)) . '">'
            . '<button type="submit" class="button">↻ Tjek GitHub-opdatering</button>'
            . '</form>';
    }

    /** @return array{ok:bool,current:string,latest:string,available:bool} */
    public static function status(bool $force = false): array
    {
        $manifest = self::manifest($force);
        if ($manifest === null) {
            return ['ok' => false, 'current' => H18_CLEAN_VERSION, 'latest' => '', 'available' => false];
        }
        $latest = (string) $manifest['version'];
        return [
            'ok' => true,
            'current' => H18_CLEAN_VERSION,
            'latest' => $latest,
            'available' => version_compare($latest, H18_CLEAN_VERSION, '>'),
        ];
    }

    public static function installButtonHtml(): string
    {
        if (!current_user_can('update_plugins')) {
            return '';
        }
        $status = self::status();
        if (!$status['ok'] || !$status['available']) {
            return '';
        }
        return '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-clean-update-install">'
            . '<input type="hidden" name="action" value="' . esc_attr(self::INSTALL_ACTION) . '">'
            . '<input type="hidden" name="_wpnonce" value="' . esc_attr(wp_create_nonce(self::INSTALL_NONCE)) . '">'
            . '<button type="submit" class="button button-primary" onclick="return confirm(\'Installer Hangar18 Manager Clean ' . esc_attr($status['latest']) . ' nu?\');">Opdater nu til ' . esc_html($status['latest']) . '</button>'
            . '</form>';
    }

    public static function installNow(): void
    {
        if (!current_user_can('update_plugins')) {
            wp_die(esc_html__('Ingen adgang til plugin-opdateringer.', 'hangar18-manager-clean'));
        }
        check_admin_referer(self::INSTALL_NONCE);

        $manifest = self::manifest(true);
        if ($manifest === null) {
            self::redirectToUpdates(['h18_clean_update_install' => 'error']);
        }
        $latest = (string) $manifest['version'];
        if (!version_compare($latest, H18_CLEAN_VERSION, '>')) {
            self::redirectToUpdates(['h18_clean_update_install' => 'current']);
        }

        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        $wasNetworkActive = is_multisite() && is_plugin_active_for_network(self::PLUGIN_FILE);
        $wasActive = $wasNetworkActive || is_plugin_active(self::PLUGIN_FILE);

        self::clearCache();
        delete_site_transient('update_plugins');
        wp_clean_plugins_cache(true);
        require_once ABSPATH . 'wp-admin/includes/update.php';
        require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
        wp_update_plugins();

        $skin = new \Automatic_Upgrader_Skin();
        $upgrader = new \Plugin_Upgrader($skin);
        $result = $upgrader->upgrade(self::PLUGIN_FILE, ['clear_update_cache' => true]);
        if (is_wp_error($result) || $result === false) {
            self::redirectToUpdates([
                'h18_clean_update_install' => 'error',
                'h18_clean_update_version' => $latest,
            ]);
        }

        // Never execute the freshly replaced plugin again inside this request.
        // Plugin_Upgrader may temporarily remove the active flag while replacing files.
        // Restore the pre-update activation state directly, then let the redirect start
        // a clean WordPress request that loads the new plugin normally.
        wp_clean_plugins_cache(true);
        $validation = validate_plugin(self::PLUGIN_FILE);
        if (is_wp_error($validation)) {
            wp_safe_redirect(add_query_arg([
                'h18_clean_update_install' => 'plugin_invalid',
                'h18_clean_update_version' => $latest,
            ], admin_url('plugins.php')));
            exit;
        }

        if ($wasNetworkActive) {
            $networkPlugins = get_site_option('active_sitewide_plugins', []);
            $networkPlugins = is_array($networkPlugins) ? $networkPlugins : [];
            if (!isset($networkPlugins[self::PLUGIN_FILE])) {
                $networkPlugins[self::PLUGIN_FILE] = time();
                update_site_option('active_sitewide_plugins', $networkPlugins);
            }
        } elseif ($wasActive) {
            $activePlugins = get_option('active_plugins', []);
            $activePlugins = is_array($activePlugins) ? array_values($activePlugins) : [];
            if (!in_array(self::PLUGIN_FILE, $activePlugins, true)) {
                $activePlugins[] = self::PLUGIN_FILE;
                sort($activePlugins, SORT_STRING);
                update_option('active_plugins', $activePlugins);
            }
        }

        wp_clean_plugins_cache(true);
        if ($wasActive) {
            $stillActive = $wasNetworkActive
                ? is_plugin_active_for_network(self::PLUGIN_FILE)
                : is_plugin_active(self::PLUGIN_FILE);
            if (!$stillActive) {
                wp_safe_redirect(add_query_arg([
                    'h18_clean_update_install' => 'activation_error',
                    'h18_clean_update_version' => $latest,
                ], admin_url('plugins.php')));
                exit;
            }
        }

        self::redirectToUpdates([
            'h18_clean_update_install' => 'success',
            'h18_clean_update_version' => $latest,
        ]);
    }

    public static function adminNotice(): void
    {
        if (!current_user_can('update_plugins')) {
            return;
        }
        $status = isset($_GET['h18_clean_update_check']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_update_check'])) : '';
        if ($status === '') {
            return;
        }
        $version = isset($_GET['h18_clean_update_version']) ? sanitize_text_field((string) wp_unslash($_GET['h18_clean_update_version'])) : '';

        $install = isset($_GET['h18_clean_update_install']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_update_install'])) : '';
        if ($install === 'success') {
            echo '<div class="notice notice-success is-dismissible"><p><strong>Hangar18 Manager Clean blev opdateret til ' . esc_html($version !== '' ? $version : H18_CLEAN_VERSION) . '.</strong></p></div>';
            return;
        }
        if ($install === 'error') {
            echo '<div class="notice notice-error is-dismissible"><p>Opdateringen kunne ikke installeres. Den eksisterende plugin-version er bevaret.</p></div>';
            return;
        }
        if ($install === 'current') {
            echo '<div class="notice notice-success is-dismissible"><p>Hangar18 Manager Clean er allerede opdateret.</p></div>';
            return;
        }
        if ($status === 'available' && $version !== '') {
            echo '<div class="notice notice-info is-dismissible"><p><strong>Hangar18 Manager Clean ' . esc_html($version) . ' er tilgængelig.</strong> Den kan installeres direkte under <a href="' . esc_url(admin_url('admin.php?page=h18-clean-updates')) . '">Hangar18 Manager → Opdateringer</a>.</p></div>';
        } elseif ($status === 'current') {
            echo '<div class="notice notice-success is-dismissible"><p>Hangar18 Manager Clean ' . esc_html(H18_CLEAN_VERSION) . ' er den nyeste GitHub-version.</p></div>';
        } elseif ($status !== '') {
            echo '<div class="notice notice-error is-dismissible"><p>GitHub update-manifestet kunne ikke læses. Den installerede plugin-version er ikke ændret.</p></div>';
        }
    }

    public static function clearCache(mixed $upgrader = null, mixed $hookExtra = null): void
    {
        delete_site_transient(self::CACHE_KEY);
    }

    /** @param array<string,string> $args */
    private static function redirectToUpdates(array $args = []): void
    {
        $url = add_query_arg(array_merge(['page' => 'h18-clean-updates'], $args), admin_url('admin.php'));
        wp_safe_redirect($url);
        exit;
    }

    private static function manifest(bool $force = false): ?array
    {
        if (!$force) {
            $cached = get_site_transient(self::CACHE_KEY);
            if (is_array($cached) && self::validManifest($cached)) {
                return $cached;
            }
        }

        $response = wp_remote_get(self::MANIFEST_URL, [
            'timeout' => 12,
            'redirection' => 3,
            'headers' => [
                'Accept' => 'application/json',
                'User-Agent' => 'Hangar18-Manager-Clean/' . H18_CLEAN_VERSION,
            ],
        ]);
        if (is_wp_error($response) || (int) wp_remote_retrieve_response_code($response) !== 200) {
            return null;
        }

        $decoded = json_decode((string) wp_remote_retrieve_body($response), true);
        if (!is_array($decoded) || !self::validManifest($decoded)) {
            return null;
        }
        set_site_transient(self::CACHE_KEY, $decoded, 15 * MINUTE_IN_SECONDS);
        return $decoded;
    }

    private static function validManifest(array $manifest): bool
    {
        $version = (string) ($manifest['version'] ?? '');
        $package = (string) ($manifest['package'] ?? '');
        $sha256 = strtolower((string) ($manifest['sha256'] ?? ''));
        if ($version === '' || $package === '' || !preg_match('/^[a-f0-9]{64}$/', $sha256)) {
            return false;
        }
        return str_starts_with($package, 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/');
    }

    private static function updateObject(array $manifest): \stdClass
    {
        $item = new \stdClass();
        $item->id = 'github.com/phenixdk2020/hangar18-manager';
        $item->slug = self::SLUG;
        $item->plugin = self::PLUGIN_FILE;
        $item->new_version = (string) $manifest['version'];
        $item->url = (string) ($manifest['homepage'] ?? 'https://hangar18.dk/');
        $item->package = (string) $manifest['package'];
        $item->tested = (string) ($manifest['tested'] ?? '');
        $item->requires_php = (string) ($manifest['requires_php'] ?? '8.0');
        $item->requires = (string) ($manifest['requires'] ?? '6.4');
        return $item;
    }
}
