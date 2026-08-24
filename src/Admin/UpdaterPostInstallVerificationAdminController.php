<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Post-install verifier for the legacy updater.
 *
 * The legacy Hangar18_Manager remains the only installation owner. The release
 * hardening step writes a short-lived pending transition after the new plugin
 * files have been installed. On the next WordPress request this controller runs
 * from the newly loaded code, verifies the active runtime/main file and records
 * a compact audit result.
 */
final class UpdaterPostInstallVerificationAdminController
{
    private const PAGE_SLUG = 'hangar18-updates';
    private const STATE_OPTION = 'hangar18_manager_update_state_v1';
    private const PENDING_OPTION = 'hangar18_manager_update_post_install_pending_v1';
    private const AUDIT_OPTION = 'hangar18_manager_update_post_install_verification_v1';

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        // Legacy auto-check runs at priority 20 and the atomic state controller at
        // priority 40. Verify/clear the pending transition in between so priority
        // 40 writes one fresh state after cache invalidation.
        add_action('admin_init', [self::class, 'verifyPendingTransition'], 35);
        add_action('admin_notices', [self::class, 'renderVerificationNotice'], 29);
    }

    public static function verifyPendingTransition(): void
    {
        if (!is_admin() || !current_user_can('update_plugins')) {
            return;
        }

        $pending = get_option(self::PENDING_OPTION, []);
        if (!is_array($pending) || $pending === []) {
            return;
        }

        $from = trim((string) ($pending['from_version'] ?? ''));
        $expected = trim((string) ($pending['expected_version'] ?? ''));
        $packageSha = strtolower(trim((string) ($pending['package_sha256'] ?? '')));
        $runtime = self::runtimeVersion();
        $pluginFile = dirname(__DIR__, 2) . '/hangar18-manager.php';

        $audit = [
            'schema_version' => '1.0',
            'from_version' => $from,
            'expected_version' => $expected,
            'runtime_version' => $runtime,
            'package_sha256' => $packageSha,
            'verified_at_utc' => gmdate('c'),
            'success' => false,
            'error' => '',
            'cache_invalidated' => [],
        ];

        try {
            if (!preg_match('/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/', $expected)) {
                throw new \RuntimeException('Pending updater transition mangler gyldig expected_version.');
            }
            if ($runtime !== $expected) {
                throw new \RuntimeException(
                    'Aktiv runtime-version er ' . $runtime . ', forventet ' . $expected . '.'
                );
            }
            if (!is_file($pluginFile) || !is_readable($pluginFile)) {
                throw new \RuntimeException('Installeret plugin-hovedfil kan ikke læses.');
            }

            $source = file_get_contents($pluginFile);
            if ($source === false) {
                throw new \RuntimeException('Installeret plugin-hovedfil kunne ikke indlæses.');
            }

            $expectedQuoted = preg_quote($expected, '/');
            if (!preg_match('/\*\s+Version:\s*' . $expectedQuoted . '\s*$/m', $source)) {
                throw new \RuntimeException('Plugin-header matcher ikke aktiv runtime-version.');
            }
            if (!preg_match("/const\\s+VERSION\\s*=\\s*'" . $expectedQuoted . "';/", $source)) {
                throw new \RuntimeException('Hangar18_Manager::VERSION-kilden matcher ikke aktiv runtime-version.');
            }

            $mainSha = strtolower((string) hash_file('sha256', $pluginFile));
            if (!preg_match('/^[a-f0-9]{64}$/', $mainSha)) {
                throw new \RuntimeException('SHA-256 af installeret hovedfil kunne ikke beregnes.');
            }
            $audit['installed_main_sha256'] = $mainSha;

            // One cache/state invalidation transaction. The atomic state controller
            // at priority 40 will immediately repopulate STATE_OPTION from the now
            // active runtime and current manifest on the Updates page.
            delete_option(self::STATE_OPTION);
            $audit['cache_invalidated'][] = self::STATE_OPTION;

            if (function_exists('delete_site_transient')) {
                delete_site_transient('update_plugins');
                $audit['cache_invalidated'][] = 'site_transient:update_plugins';
            }
            if (function_exists('wp_clean_plugins_cache')) {
                wp_clean_plugins_cache(true);
                $audit['cache_invalidated'][] = 'wp_clean_plugins_cache:true';
            }

            $audit['success'] = true;
            update_option(self::AUDIT_OPTION, $audit, false);
            delete_option(self::PENDING_OPTION);
        } catch (\Throwable $error) {
            $audit['error'] = $error->getMessage();
            update_option(self::AUDIT_OPTION, $audit, false);
            // Keep pending state for diagnosis; do not silently claim completion.
        }
    }

    public static function renderVerificationNotice(): void
    {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== self::PAGE_SLUG) {
            return;
        }

        $audit = get_option(self::AUDIT_OPTION, []);
        if (!is_array($audit) || $audit === []) {
            return;
        }

        $success = !empty($audit['success']);
        $class = $success ? 'notice notice-success' : 'notice notice-error';
        $from = trim((string) ($audit['from_version'] ?? ''));
        $to = trim((string) ($audit['expected_version'] ?? ''));
        $runtime = trim((string) ($audit['runtime_version'] ?? ''));
        $verified = trim((string) ($audit['verified_at_utc'] ?? ''));
        $error = trim((string) ($audit['error'] ?? ''));

        echo '<div class="' . esc_attr($class) . '"><p><strong>Updater runtime-verifikation:</strong> ';
        if ($success) {
            echo esc_html(($from !== '' ? $from : '?') . ' → ' . ($to !== '' ? $to : '?') . ' · aktiv runtime ' . ($runtime !== '' ? $runtime : '?'));
            if ($verified !== '') {
                echo ' · ' . esc_html($verified);
            }
            echo '. Cache/state er invalidated og genopbygges fra aktiv kode.';
        } else {
            echo esc_html($error !== '' ? $error : 'Verifikation er ikke gennemført.');
        }
        echo '</p></div>';
    }

    private static function runtimeVersion(): string
    {
        if (class_exists('Hangar18_Manager')) {
            try {
                $version = trim((string) \Hangar18_Manager::VERSION);
                if ($version !== '') {
                    return $version;
                }
            } catch (\Throwable $ignore) {
            }
        }
        return '0.0.0';
    }
}
