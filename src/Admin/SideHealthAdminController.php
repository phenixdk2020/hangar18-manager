<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Quality\SideHealthService;
use RuntimeException;

/**
 * I4 read-only bridge between the legacy page editor DOM state and Side Health.
 * It never writes page state and is available only to authenticated page editors.
 */
final class SideHealthAdminController
{
    private const NONCE_ACTION = 'h18_ud_side_health_v1';
    private const MAX_JSON_BYTES = 524288;

    public static function register(): void
    {
        add_action('wp_ajax_h18_ud_side_health', [self::class, 'analyze']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueueAssets']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' && strpos((string) $hook, 'hangar18-pages') === false) {
            return;
        }
        $pluginFile = dirname(__DIR__, 2) . '/hangar18-manager.php';
        $version = class_exists('Hangar18_Manager') ? (string) \Hangar18_Manager::VERSION : '0';
        $jsPath = dirname(__DIR__, 2) . '/assets/ultimate-designer-side-health.js';
        $cssPath = dirname(__DIR__, 2) . '/assets/ultimate-designer-side-health.css';
        wp_enqueue_style('hangar18-ultimate-designer-side-health', plugins_url('assets/ultimate-designer-side-health.css', $pluginFile), [], $version . '-' . (string) (@filemtime($cssPath) ?: 0));
        wp_enqueue_script('hangar18-ultimate-designer-side-health', plugins_url('assets/ultimate-designer-side-health.js', $pluginFile), ['jquery'], $version . '-' . (string) (@filemtime($jsPath) ?: 0), true);
        wp_localize_script('hangar18-ultimate-designer-side-health', 'Hangar18SideHealth', [
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce(self::NONCE_ACTION),
            'debounceMs' => 650,
        ]);
    }

    public static function analyze(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Manglende rettighed til Side Health.'], 403);
            return;
        }
        check_ajax_referer(self::NONCE_ACTION, 'nonce');

        try {
            $stateRaw = isset($_POST['state_json']) ? (string) wp_unslash($_POST['state_json']) : '';
            $seoRaw = isset($_POST['seo_json']) ? (string) wp_unslash($_POST['seo_json']) : '{}';
            if ($stateRaw === '' || strlen($stateRaw) > self::MAX_JSON_BYTES || strlen($seoRaw) > 65536) {
                throw new RuntimeException('Side Health snapshot er tomt eller for stort.');
            }
            $state = json_decode($stateRaw, true, 64, JSON_THROW_ON_ERROR);
            $seo = json_decode($seoRaw, true, 16, JSON_THROW_ON_ERROR);
            if (!is_array($state) || !is_array($seo)) {
                throw new RuntimeException('Side Health snapshot har ugyldigt format.');
            }
            $sections = isset($state['Sections']) && is_array($state['Sections']) ? array_values($state['Sections']) : [];
            if (count($sections) > 100) {
                throw new RuntimeException('Side Health snapshot indeholder for mange elementer.');
            }
            $normalized = [
                'Version' => is_string($state['Version'] ?? null) ? (string) $state['Version'] : '',
                'PageSlug' => sanitize_key((string) ($state['PageSlug'] ?? '')),
                'PageTitle' => sanitize_text_field((string) ($state['PageTitle'] ?? '')),
                'ContentVersion' => max(0, (int) ($state['ContentVersion'] ?? 0)),
                'DataContextType' => sanitize_key((string) ($state['DataContextType'] ?? '')),
                'DataContextEntryId' => max(0, (int) ($state['DataContextEntryId'] ?? 0)),
                'Sections' => $sections,
            ];
            $report = (new SideHealthService())->analyze($normalized, $seo, []);
        } catch (\Throwable $e) {
            wp_send_json_error(['message' => mb_substr($e->getMessage(), 0, 500)], 400);
            return;
        }

        // Keep the transport success response outside the analyzer try/catch.
        // WordPress exits here; tests can safely intercept the response without it
        // being misclassified as an analyzer exception.
        wp_send_json_success(['report' => $report]);
    }
}
