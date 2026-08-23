<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Keeps the legacy Hangar18 updater status aligned with the plugin version
 * actually installed on disk.
 *
 * The legacy installer runs inside the old plugin PHP request, so
 * Hangar18_Manager::VERSION still contains the pre-update version until the
 * redirect loads the new code. This controller reconciles the persisted
 * updater state immediately after Plugin_Upgrader completes and again on the
 * next admin request as a bounded safety net.
 */
final class UpdaterPostInstallStateAdminController
{
    private const UPDATE_STATE_OPTION = 'hangar18_manager_update_state_v1';
    private const PLUGIN_FILE = 'hangar18-manager/hangar18-manager.php';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }

        self::$registered = true;
        add_action('upgrader_process_complete', [self::class, 'afterUpgrade'], 99, 2);
        add_action('admin_init', [self::class, 'reconcile'], 25);
    }

    public static function afterUpgrade($upgrader, $hookExtra): void
    {
        if (is_array($hookExtra) && isset($hookExtra['type']) && $hookExtra['type'] !== 'plugin') {
            return;
        }

        self::reconcile();
    }

    public static function reconcile(): void
    {
        $state = get_option(self::UPDATE_STATE_OPTION, []);
        if (!is_array($state) || !$state) {
            return;
        }

        $manifest = isset($state['manifest']) && is_array($state['manifest'])
            ? $state['manifest']
            : [];
        $manifestVersion = trim((string) ($manifest['version'] ?? ''));
        if ($manifestVersion === '') {
            return;
        }

        $installedVersion = self::installedVersion();
        if ($installedVersion === '') {
            return;
        }

        $updateAvailable = version_compare($manifestVersion, $installedVersion, '>');
        $storedCurrent = trim((string) ($state['current_version'] ?? ''));
        $storedAvailable = !empty($state['update_available']);
        $storedError = trim((string) ($state['error'] ?? ''));

        if (
            $storedCurrent === $installedVersion &&
            $storedAvailable === $updateAvailable &&
            $storedError === ''
        ) {
            return;
        }

        $state['checked_at_utc'] = gmdate('c');
        $state['success'] = true;
        $state['current_version'] = $installedVersion;
        $state['update_available'] = $updateAvailable;
        $state['compatible_wp'] = version_compare(
            get_bloginfo('version'),
            (string) ($manifest['min_wp'] ?? '6.4'),
            '>='
        );
        $state['compatible_php'] = version_compare(
            PHP_VERSION,
            (string) ($manifest['min_php'] ?? '8.0'),
            '>='
        );
        $state['error'] = '';

        update_option(self::UPDATE_STATE_OPTION, $state, false);

        // WordPress can otherwise keep the previous plugin update result in
        // the site transient until another manual update check is performed.
        delete_site_transient('update_plugins');
        if (function_exists('wp_clean_plugins_cache')) {
            wp_clean_plugins_cache(true);
        }
    }

    private static function installedVersion(): string
    {
        if (!defined('WP_PLUGIN_DIR')) {
            return '';
        }

        $file = trailingslashit(WP_PLUGIN_DIR) . self::PLUGIN_FILE;
        if (!is_file($file) || !is_readable($file)) {
            return '';
        }

        clearstatcache(true, $file);
        $data = get_file_data($file, ['Version' => 'Version'], 'plugin');
        return trim((string) ($data['Version'] ?? ''));
    }
}
