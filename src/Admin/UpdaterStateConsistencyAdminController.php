<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Keeps the legacy updater UI on one atomic version/manifest snapshot.
 *
 * The legacy updater remains the installation owner (backup, SHA verification,
 * code backup and rollback). This controller only refreshes/normalizes the
 * read-only state consumed by Hangar18_Manager::render_updates().
 */
final class UpdaterStateConsistencyAdminController
{
    private const PAGE_SLUG = 'hangar18-updates';
    private const SETTINGS_OPTION = 'hangar18_manager_update_settings_v1';
    private const STATE_OPTION = 'hangar18_manager_update_state_v1';

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
