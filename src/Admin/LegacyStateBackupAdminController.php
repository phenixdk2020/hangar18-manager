<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Creates a rollback snapshot of legacy/migration options before cleanup.
 *
 * This controller never deletes or mutates the source options. It only stores
 * bounded snapshots in a dedicated option so later cleanup can require evidence
 * that a rollback point exists first.
 */
final class LegacyStateBackupAdminController
{
    private const PAGE_SLUG = 'hangar18-updates';
    private const BACKUP_OPTION = 'hangar18_manager_legacy_cleanup_backups_v1';
    private const ACTION = 'h18_create_legacy_cleanup_backup';
    private const NONCE = 'h18_create_legacy_cleanup_backup';
    private const MAX_BACKUPS = 10;

    private static bool $registered = false;

    /** @var array<int,string> */
    private const CANDIDATE_OPTIONS = [
        'hangar18_manager_config_import_meta',
        'hangar18_manager_config_bootstrap_v032',
        'hangar18_manager_authoritative_baseline_20260813',
        'hangar18_manager_frontend_repair_046',
        'hangar18_manager_astra_banner_repair_047',
        'hangar18_manager_vehicle_layout_repair_049',
        'hangar18_manager_legacy_page_template_repair_0411',
        'hangar18_manager_mobile_content_layout_repair_0414',
        'hangar18_manager_legacy_startup_cleanup_0415',
        'hangar18_manager_home_editor_design_repair_0423',
    ];

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_post_' . self::ACTION, [self::class, 'handleCreate']);
        add_action('admin_notices', [self::class, 'render'], 85);
    }

    public static function handleCreate(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Du har ikke rettigheder til denne handling.', 'hangar18-manager'));
        }
        check_admin_referer(self::NONCE);

        $options = [];
        $existingCount = 0;
        foreach (self::CANDIDATE_OPTIONS as $name) {
            $sentinel = new \stdClass();
            $value = get_option($name, $sentinel);
            $exists = $value !== $sentinel;
            if ($exists) {
                $existingCount++;
            }
            $options[$name] = [
                'exists' => $exists,
                'value' => $exists ? $value : null,
            ];
        }

        $snapshot = [
            'schema_version' => '1.0',
            'created_utc' => gmdate('c'),
            'user_id' => get_current_user_id(),
            'plugin_version' => self::pluginVersion(),
            'candidate_count' => count(self::CANDIDATE_OPTIONS),
            'existing_count' => $existingCount,
            'options' => $options,
        ];
        $canonical = wp_json_encode($snapshot, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        $snapshot['sha256'] = hash('sha256', is_string($canonical) ? $canonical : serialize($snapshot));

        $history = get_option(self::BACKUP_OPTION, []);
        $history = is_array($history) ? array_values($history) : [];
        array_unshift($history, $snapshot);
        $history = array_slice($history, 0, self::MAX_BACKUPS);
        update_option(self::BACKUP_OPTION, $history, false);

        $url = add_query_arg(
            [
                'page' => self::PAGE_SLUG,
                'h18_legacy_backup' => 'created',
                'h18_legacy_backup_sha' => substr((string) $snapshot['sha256'], 0, 12),
            ],
            admin_url('admin.php')
        );
        wp_safe_redirect($url);
        exit;
    }

    public static function render(): void
    {
        if (!current_user_can('manage_options')) {
            return;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== self::PAGE_SLUG) {
            return;
        }

        $history = get_option(self::BACKUP_OPTION, []);
        $history = is_array($history) ? array_values($history) : [];
        $latest = isset($history[0]) && is_array($history[0]) ? $history[0] : null;

        if (isset($_GET['h18_legacy_backup']) && sanitize_key((string) wp_unslash($_GET['h18_legacy_backup'])) === 'created') {
            echo '<div class="notice notice-success is-dismissible"><p><strong>Legacy cleanup-backup oprettet.</strong> Ingen legacy-option blev slettet eller ændret.</p></div>';
        }

        echo '<div class="notice notice-info" style="padding:14px 16px;margin-top:16px">';
        echo '<h2 style="margin:0 0 8px">Legacy cleanup rollback-punkt</h2>';
        echo '<p>Opretter et snapshot af de kendte migration/repair-options før senere oprydning. Handlingen er <strong>kun backup</strong> og sletter intet.</p>';

        if ($latest) {
            echo '<p><strong>Seneste backup:</strong> ' . esc_html((string) ($latest['created_utc'] ?? 'ukendt'));
            echo ' · plugin ' . esc_html((string) ($latest['plugin_version'] ?? 'ukendt'));
            echo ' · eksisterende options ' . esc_html((string) ($latest['existing_count'] ?? '0')) . '/' . esc_html((string) ($latest['candidate_count'] ?? count(self::CANDIDATE_OPTIONS)));
            echo ' · SHA <code>' . esc_html(substr((string) ($latest['sha256'] ?? ''), 0, 16)) . '…</code></p>';
        } else {
            echo '<p><strong>Status:</strong> Der er endnu ikke oprettet et legacy cleanup rollback-punkt.</p>';
        }

        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION) . '">';
        echo '<button type="submit" class="button button-secondary">Opret legacy cleanup-backup</button>';
        echo '</form>';
        echo '<p><small>Der beholdes maksimalt ' . esc_html((string) self::MAX_BACKUPS) . ' snapshots. Senere destructive cleanup skal kontrollere, at et rollback-punkt findes først.</small></p>';
        echo '</div>';
    }

    public static function hasBackup(): bool
    {
        $history = get_option(self::BACKUP_OPTION, []);
        return is_array($history) && !empty($history) && is_array($history[0] ?? null) && !empty($history[0]['sha256']);
    }

    private static function pluginVersion(): string
    {
        if (class_exists('Hangar18_Manager')) {
            try {
                return trim((string) \Hangar18_Manager::VERSION);
            } catch (\Throwable $ignore) {
                // Fall through.
            }
        }
        return '0.0.0';
    }
}
