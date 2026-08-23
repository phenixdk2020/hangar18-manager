<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Keeps the legacy updater UI on one atomic version/manifest snapshot.
 *
 * The legacy updater remains the installation owner (backup, SHA verification,
 * code backup and rollback). This controller refreshes/normalizes the read-only
 * state and adds a support/status layer on the Updates page.
 */
final class UpdaterStateConsistencyAdminController
{
    private const PAGE_SLUG = 'hangar18-updates';
    private const SETTINGS_OPTION = 'hangar18_manager_update_settings_v1';
    private const STATE_OPTION = 'hangar18_manager_update_state_v1';
    private const SUPPORT_VERSION = '0.8.79';

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        // Legacy maybe_check_for_updates runs at priority 20. Normalize afterwards
        // so render_updates() always receives one coherent snapshot.
        add_action('admin_init', [self::class, 'refreshUpdatePageState'], 40);
        add_action('admin_notices', [self::class, 'renderStatusCard'], 30);
        add_action('admin_enqueue_scripts', [self::class, 'enqueueSupport'], 80);
    }

    public static function refreshUpdatePageState(): void
    {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== self::PAGE_SLUG) {
            return;
        }

        $currentVersion = self::currentPluginVersion();
        $settings = self::settings();
        $previous = get_option(self::STATE_OPTION, []);
        $previous = is_array($previous) ? $previous : [];

        try {
            $manifest = self::fetchManifest($settings);
            $state = self::buildState($currentVersion, $settings, $manifest, true, '');
        } catch (\Throwable $error) {
            // A temporary GitHub failure must not resurrect a stale JA or blank
            // the previously known version. Keep the last manifest, but recompute
            // availability from the currently active plugin version.
            $manifest = is_array($previous['manifest'] ?? null) ? $previous['manifest'] : [];
            $state = self::buildState(
                $currentVersion,
                $settings,
                $manifest,
                false,
                $error->getMessage()
            );
        }

        update_option(self::STATE_OPTION, $state, false);
    }

    public static function enqueueSupport(): void
    {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== self::PAGE_SLUG) {
            return;
        }

        $state = get_option(self::STATE_OPTION, []);
        $state = is_array($state) ? $state : [];
        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $path = $pluginDir . '/assets/updater-support-v0879.js';
        wp_enqueue_script(
            'hangar18-updater-support-v0879',
            $pluginUrl . 'assets/updater-support-v0879.js',
            [],
            is_file($path) ? (string) filemtime($path) : self::SUPPORT_VERSION,
            true
        );

        wp_localize_script(
            'hangar18-updater-support-v0879',
            'H18UpdaterSupportV0879',
            [
                'updateAvailable' => !empty($state['update_available']),
                'diagnosis' => self::diagnosis($state),
            ]
        );
    }

    public static function renderStatusCard(): void
    {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== self::PAGE_SLUG) {
            return;
        }

        $state = get_option(self::STATE_OPTION, []);
        $state = is_array($state) ? $state : [];
        $manifest = is_array($state['manifest'] ?? null) ? $state['manifest'] : [];
        $checked = trim((string) ($state['checked_at_utc'] ?? ''));
        $checkedTs = $checked !== '' ? strtotime($checked) : false;
        $age = $checkedTs !== false ? max(0, time() - $checkedTs) : null;
        $fresh = !empty($state['success']) && $age !== null && $age <= 1800;
        $error = trim((string) ($state['error'] ?? ''));
        $current = trim((string) ($state['current_version'] ?? self::currentPluginVersion()));
        $latest = trim((string) ($manifest['version'] ?? ''));
        $sha = trim((string) ($manifest['package_sha256'] ?? ''));
        $published = trim((string) ($manifest['published_utc'] ?? ''));
        $wpOk = !empty($state['compatible_wp']);
        $phpOk = !empty($state['compatible_php']);
        $available = !empty($state['update_available']);

        echo '<div class="notice notice-info" style="padding:14px 16px;margin-top:16px;">';
        echo '<h2 style="margin:0 0 10px;">Updater status · atomisk snapshot</h2>';
        echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;max-width:1100px;">';
        self::statusCell('Installeret', $current !== '' ? $current : 'ukendt');
        self::statusCell('Seneste GitHub-version', $latest !== '' ? $latest : 'ukendt');
        self::statusCell('Opdatering', $available ? 'JA' : 'NEJ');
        self::statusCell('State', $fresh ? 'FRESH' : 'STALE / FEJL');
        self::statusCell('Seneste check', $checked !== '' ? $checked : 'ikke registreret');
        self::statusCell('Published', $published !== '' ? $published : 'ukendt');
        self::statusCell('WP / PHP', ($wpOk ? 'WP OK' : 'WP IKKE OK') . ' · ' . ($phpOk ? 'PHP OK' : 'PHP IKKE OK'));
        self::statusCell('Package SHA-256', $sha !== '' ? $sha : 'ukendt', true);
        echo '</div>';

        if ($error !== '') {
            echo '<div class="notice notice-error inline" style="margin:12px 0 0;"><p><strong>GitHub/netværksfejl:</strong> ' . esc_html($error) . '<br><small>Senest kendte manifest kan vises, men JA/NEJ er genberegnet mod den aktive pluginversion.</small></p></div>';
        } elseif (!$fresh) {
            echo '<div class="notice notice-warning inline" style="margin:12px 0 0;"><p>Updater-state er ældre end 30 minutter eller mangler et succesfuldt check.</p></div>';
        }

        $changelog = is_array($manifest['changelog'] ?? null) ? $manifest['changelog'] : [];
        if ($changelog) {
            echo '<details style="margin-top:12px;"><summary><strong>Changelog for seneste version</strong></summary><ul style="list-style:disc;padding-left:22px;">';
            foreach ($changelog as $line) {
                if (!is_scalar($line) || trim((string) $line) === '') {
                    continue;
                }
                echo '<li>' . esc_html(trim((string) $line)) . '</li>';
            }
            echo '</ul></details>';
        }

        echo '<p style="margin:12px 0 0;"><button type="button" class="button" id="h18-copy-updater-diagnosis">Kopiér updater diagnose</button> <span id="h18-updater-copy-status" aria-live="polite"></span></p>';
        echo '</div>';
    }

    private static function statusCell(string $label, string $value, bool $code = false): void
    {
        echo '<div style="border:1px solid #dcdcde;border-radius:4px;padding:8px 10px;background:#fff;">';
        echo '<small style="display:block;color:#646970;">' . esc_html($label) . '</small>';
        echo $code ? '<code style="overflow-wrap:anywhere;">' . esc_html($value) . '</code>' : '<strong>' . esc_html($value) . '</strong>';
        echo '</div>';
    }

    /** @return array<string,mixed> */
    private static function diagnosis(array $state): array
    {
        $manifest = is_array($state['manifest'] ?? null) ? $state['manifest'] : [];
        return [
            'support_version' => self::SUPPORT_VERSION,
            'checked_at_utc' => (string) ($state['checked_at_utc'] ?? ''),
            'success' => !empty($state['success']),
            'repository' => (string) ($state['repository'] ?? ''),
            'branch' => (string) ($state['branch'] ?? ''),
            'current_version' => (string) ($state['current_version'] ?? ''),
            'latest_version' => (string) ($manifest['version'] ?? ''),
            'update_available' => !empty($state['update_available']),
            'compatible_wp' => !empty($state['compatible_wp']),
            'compatible_php' => !empty($state['compatible_php']),
            'published_utc' => (string) ($manifest['published_utc'] ?? ''),
            'package_path' => (string) ($manifest['package_path'] ?? ''),
            'package_sha256' => (string) ($manifest['package_sha256'] ?? ''),
            'state_contract' => (string) ($state['state_contract'] ?? ''),
            'error' => (string) ($state['error'] ?? ''),
        ];
    }

    private static function currentPluginVersion(): string
    {
        if (class_exists('Hangar18_Manager')) {
            try {
                $version = trim((string) \Hangar18_Manager::VERSION);
                if ($version !== '') {
                    return $version;
                }
            } catch (\Throwable $ignore) {
                // Fall through to plugin header.
            }
        }

        $pluginFile = dirname(__DIR__, 2) . '/hangar18-manager.php';
        if (is_file($pluginFile) && function_exists('get_file_data')) {
            $data = get_file_data($pluginFile, ['Version' => 'Version'], 'plugin');
            $version = trim((string) ($data['Version'] ?? ''));
            if ($version !== '') {
                return $version;
            }
        }

        return '0.0.0';
    }

    /** @return array<string,mixed> */
    private static function settings(): array
    {
        $stored = get_option(self::SETTINGS_OPTION, []);
        $stored = is_array($stored) ? $stored : [];

        $repository = trim((string) ($stored['Repository'] ?? 'phenixdk2020/hangar18-manager'));
        $branch = trim((string) ($stored['Branch'] ?? 'main'));
        $manifestPath = trim((string) ($stored['ManifestPath'] ?? 'update.json'));
        $packagePath = trim((string) ($stored['PackagePath'] ?? 'dist/hangar18-manager.zip'));

        return [
            'Repository' => $repository !== '' ? $repository : 'phenixdk2020/hangar18-manager',
            'Branch' => $branch !== '' ? $branch : 'main',
            'ManifestPath' => $manifestPath !== '' ? $manifestPath : 'update.json',
            'PackagePath' => $packagePath !== '' ? $packagePath : 'dist/hangar18-manager.zip',
        ];
    }

    /** @return array<string,mixed> */
    private static function fetchManifest(array $settings): array
    {
        $repository = (string) $settings['Repository'];
        $branch = (string) $settings['Branch'];
        $path = ltrim((string) $settings['ManifestPath'], '/');

        if (!preg_match('~^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$~', $repository)) {
            throw new \RuntimeException('Updater repository-format er ugyldigt.');
        }
        if ($path === '' || str_contains($path, '..')) {
            throw new \RuntimeException('Updater manifest-stien er ugyldig.');
        }

        $encodedPath = implode('/', array_map('rawurlencode', explode('/', $path)));
        $url = 'https://api.github.com/repos/' . $repository . '/contents/' . $encodedPath . '?ref=' . rawurlencode($branch);
        $headers = [
            'Accept' => 'application/vnd.github+json',
            'User-Agent' => 'Hangar18-Manager-Updater-State',
            'X-GitHub-Api-Version' => '2022-11-28',
            'Cache-Control' => 'no-cache',
        ];

        if (defined('HANGAR18_GITHUB_TOKEN')) {
            $token = trim((string) constant('HANGAR18_GITHUB_TOKEN'));
            if ($token !== '') {
                $headers['Authorization'] = 'Bearer ' . $token;
            }
        }

        $response = wp_remote_get($url, [
            'timeout' => 20,
            'redirection' => 3,
            'headers' => $headers,
        ]);

        if (is_wp_error($response)) {
            throw new \RuntimeException('GitHub manifest-check fejlede: ' . $response->get_error_message());
        }

        $status = (int) wp_remote_retrieve_response_code($response);
        if ($status < 200 || $status >= 300) {
            throw new \RuntimeException('GitHub manifest-check returnerede HTTP ' . $status . '.');
        }

        $payload = json_decode((string) wp_remote_retrieve_body($response), true);
        if (!is_array($payload)) {
            throw new \RuntimeException('GitHub manifest-svaret kunne ikke læses.');
        }

        $encoded = (string) ($payload['content'] ?? '');
        $decoded = base64_decode(str_replace(["\r", "\n"], '', $encoded), true);
        if ($decoded === false || $decoded === '') {
            throw new \RuntimeException('GitHub manifest-indholdet kunne ikke afkodes.');
        }

        $manifest = json_decode($decoded, true);
        if (!is_array($manifest)) {
            throw new \RuntimeException('update.json indeholder ikke gyldig JSON.');
        }

        $version = trim((string) ($manifest['version'] ?? ''));
        if ($version === '') {
            throw new \RuntimeException('update.json mangler version.');
        }

        return [
            'schema_version' => trim((string) ($manifest['schema_version'] ?? '1.0')),
            'plugin' => trim((string) ($manifest['plugin'] ?? 'hangar18-manager')),
            'version' => $version,
            'channel' => trim((string) ($manifest['channel'] ?? '')),
            'backlog_ids' => array_values(array_filter(
                is_array($manifest['backlog_ids'] ?? null) ? $manifest['backlog_ids'] : [],
                static fn($id): bool => is_scalar($id) && trim((string) $id) !== ''
            )),
            'min_wp' => trim((string) ($manifest['min_wp'] ?? '6.4')),
            'min_php' => trim((string) ($manifest['min_php'] ?? '8.0')),
            'published_utc' => trim((string) ($manifest['published_utc'] ?? '')),
            'package_path' => trim((string) ($manifest['package_path'] ?? $settings['PackagePath'])),
            'package_sha256' => strtolower(trim((string) ($manifest['package_sha256'] ?? ''))),
            'changelog' => array_values(array_filter(
                is_array($manifest['changelog'] ?? null) ? $manifest['changelog'] : [],
                static fn($line): bool => is_scalar($line) && trim((string) $line) !== ''
            )),
        ];
    }

    /** @return array<string,mixed> */
    private static function buildState(
        string $currentVersion,
        array $settings,
        array $manifest,
        bool $success,
        string $error
    ): array {
        $latestVersion = trim((string) ($manifest['version'] ?? ''));
        $updateAvailable = $latestVersion !== '' && version_compare($latestVersion, $currentVersion, '>');
        $minWp = trim((string) ($manifest['min_wp'] ?? ''));
        $minPhp = trim((string) ($manifest['min_php'] ?? ''));

        return [
            'checked_at_utc' => gmdate('c'),
            'success' => $success,
            'repository' => (string) $settings['Repository'],
            'branch' => (string) $settings['Branch'],
            'current_version' => $currentVersion,
            'manifest' => $manifest,
            'update_available' => $updateAvailable,
            'compatible_wp' => $minWp === '' || version_compare((string) get_bloginfo('version'), $minWp, '>='),
            'compatible_php' => $minPhp === '' || version_compare(PHP_VERSION, $minPhp, '>='),
            'error' => $error,
            'state_contract' => 'atomic-v0.8.77',
        ];
    }
}
