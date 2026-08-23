<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Opt-in trace controller for Ultimate Designer diagnostics.
 *
 * Full event tracing is disabled by default. The master switch lives on the
 * legacy Hangar18 Updates page; when enabled, the Designer gets its own
 * Start/Stop/Marker/Export toolbar. Trace data stays browser-local.
 */
final class UltimateDesignerTraceAdminController
{
    private const OPTION = 'hangar18_manager_trace_settings_v1';
    private const STORAGE_KEY = 'h18.ultimate-designer.trace.v0876';
    private const TRACE_VERSION = '0.8.76';
    private const TRACE_TOOLS_VERSION = '0.8.79';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        add_action('admin_post_h18_save_trace_settings', [self::class, 'handleSave']);
        add_action('admin_notices', [self::class, 'renderUpdatesPanel']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 99);
    }

    public static function enabled(): bool
    {
        $settings = get_option(self::OPTION, []);
        return is_array($settings) && !empty($settings['Enabled']);
    }

    public static function handleSave(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke rettigheder til denne handling.', 'hangar18-manager'));
        }

        check_admin_referer('h18_save_trace_settings');
        $enabled = isset($_POST['h18_trace_enabled']) && (string) wp_unslash($_POST['h18_trace_enabled']) === '1';

        update_option(
            self::OPTION,
            [
                'Version' => '1.0',
                'Enabled' => $enabled,
                'UpdatedUtc' => gmdate('c'),
                'UpdatedBy' => get_current_user_id(),
            ],
            false
        );

        $target = add_query_arg(
            [
                'page' => 'hangar18-updates',
                'h18_trace_saved' => '1',
            ],
            admin_url('admin.php')
        );
        wp_safe_redirect($target);
        exit;
    }

    public static function enqueue(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');

        if ($page === 'hangar18-updates') {
            $settingsPath = $pluginDir . '/assets/ultimate-designer-trace-settings-v0876.js';
            wp_enqueue_script(
                'hangar18-ultimate-designer-trace-settings-v0876',
                $pluginUrl . 'assets/ultimate-designer-trace-settings-v0876.js',
                [],
                is_file($settingsPath) ? (string) filemtime($settingsPath) : self::TRACE_VERSION,
                true
            );
            wp_localize_script(
                'hangar18-ultimate-designer-trace-settings-v0876',
                'H18UltimateDesignerTraceSettingsV0876',
                [
                    'storageKey' => self::STORAGE_KEY,
                    'enabled' => self::enabled(),
                    'version' => self::TRACE_VERSION,
                ]
            );
            return;
        }

        if ($page !== 'hangar18-pages' || !self::enabled()) {
            return;
        }

        $tracePath = $pluginDir . '/assets/ultimate-designer-trace-v0876.js';
        wp_enqueue_script(
            'hangar18-ultimate-designer-trace-v0876',
            $pluginUrl . 'assets/ultimate-designer-trace-v0876.js',
            [
                'jquery',
                'hangar18-ultimate-designer-lego-placement-stability-v0862',
            ],
            is_file($tracePath) ? (string) filemtime($tracePath) : self::TRACE_VERSION,
            true
        );

        $toolsPath = $pluginDir . '/assets/ultimate-designer-trace-tools-v0879.js';
        wp_enqueue_script(
            'hangar18-ultimate-designer-trace-tools-v0879',
            $pluginUrl . 'assets/ultimate-designer-trace-tools-v0879.js',
            ['hangar18-ultimate-designer-trace-v0876'],
            is_file($toolsPath) ? (string) filemtime($toolsPath) : self::TRACE_TOOLS_VERSION,
            true
        );
        wp_localize_script(
            'hangar18-ultimate-designer-trace-tools-v0879',
            'H18UltimateDesignerTraceToolsV0879',
            [
                'pluginVersion' => class_exists('Hangar18_Manager') ? (string) \Hangar18_Manager::VERSION : '',
                'traceVersion' => self::TRACE_VERSION,
                'toolsVersion' => self::TRACE_TOOLS_VERSION,
                'storageKey' => self::STORAGE_KEY,
            ]
        );
    }

    public static function renderUpdatesPanel(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-updates') {
            return;
        }

        $enabled = self::enabled();
        $saved = isset($_GET['h18_trace_saved']) && (string) wp_unslash($_GET['h18_trace_saved']) === '1';

        if ($saved) {
            echo '<div class="notice notice-success is-dismissible"><p><strong>Udvidet fejllogning er gemt.</strong></p></div>';
        }

        echo '<div class="notice notice-info" style="padding:14px 16px;margin-top:16px;">';
        echo '<h2 style="margin:0 0 8px;">Ultimate Designer — udvidet fejllogning</h2>';
        echo '<p style="max-width:1000px;">Master-indstillingen bestemmer, om trace-værktøjet indlæses i Designeren. Når den er slået til, starter den tunge event-log <strong>ikke automatisk</strong>; brug <strong>Start test</strong> eller <strong>Fortsæt log</strong> i Designerens tracebjælke. JavaScript-fejl kan fortsat registreres af trace-værktøjet, mens master er aktiv.</p>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:12px 0;">';
        echo '<input type="hidden" name="action" value="h18_save_trace_settings">';
        wp_nonce_field('h18_save_trace_settings');
        echo '<label style="display:flex;align-items:center;gap:7px;font-weight:600;">';
        echo '<input type="checkbox" name="h18_trace_enabled" value="1"' . checked($enabled, true, false) . '> Udvidet fejllogning TIL';
        echo '</label>';
        submit_button('Gem logindstilling', 'secondary', 'submit', false);
        echo '<span><strong>Master:</strong> ' . ($enabled ? '<span style="color:#008a20;">TIL</span>' : '<span style="color:#646970;">FRA</span>') . '</span>';
        echo '</form>';

        echo '<div id="h18-trace-browser-summary" data-storage-key="' . esc_attr(self::STORAGE_KEY) . '">Browser-log: kontrollerer…</div>';
        echo '<p style="margin-bottom:0;"><button type="button" class="button" id="h18-trace-export-json">Eksportér gemt JSON</button> ';
        echo '<button type="button" class="button" id="h18-trace-clear-browser">Nulstil browser-log</button></p>';
        echo '</div>';
    }
}
