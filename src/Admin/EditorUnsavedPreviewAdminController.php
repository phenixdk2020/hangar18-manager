<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Read-only live frontend preview for the page currently open in Sider.
 *
 * The current editor form is stored in a short-lived transient and rendered by
 * the real public shortcode/runtime in an iframe. Preview therefore reflects
 * unsaved changes without writing the WordPress page or the canonical page
 * option. The transient is available only to an authenticated page editor.
 */
final class EditorUnsavedPreviewAdminController
{
    private const PREVIEW_PREFIX = 'h18_live_preview_';
    private const PAGE_OPTION = 'hangar18_manager_pages_v1';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('wp_ajax_h18_prepare_live_page_preview', [self::class, 'prepareLivePreview']);
    }

    public static function enqueue(): void
    {
        $adminPage = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($adminPage !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-unsaved-preview.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-unsaved-preview.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-unsaved-preview',
            $pluginUrl . 'assets/ultimate-designer-unsaved-preview.js',
            ['jquery', 'hangar18-manager-admin'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.85',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-unsaved-preview',
            $pluginUrl . 'assets/ultimate-designer-unsaved-preview.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.82'
        );

        $slug = isset($_GET['page_slug']) ? sanitize_title((string) wp_unslash($_GET['page_slug'])) : '';
        $page = $slug !== '' ? get_page_by_path($slug, OBJECT, 'page') : null;
        $previewUrl = $page instanceof \WP_Post ? get_permalink($page) : '';

        wp_localize_script(
            'hangar18-ultimate-designer-unsaved-preview',
            'H18UnsavedPreview',
            [
                'mode'       => 'live-frontend',
                'pageSlug'   => $slug,
                'previewUrl' => $previewUrl ? esc_url_raw((string) $previewUrl) : '',
                'ajaxUrl'    => admin_url('admin-ajax.php'),
                'action'     => 'h18_prepare_live_page_preview',
                'nonce'      => wp_create_nonce('h18_live_page_preview'),
            ]
        );
    }

    public static function prepareLivePreview(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettighed til at forhåndsvise siden.'], 403);
        }
        check_ajax_referer('h18_live_page_preview', 'nonce');

        $slug = isset($_POST['page_slug']) ? sanitize_title((string) wp_unslash($_POST['page_slug'])) : '';
        if ($slug === '') {
            wp_send_json_error(['message' => 'Siden mangler et gyldigt slug.'], 400);
        }
        $page = get_page_by_path($slug, OBJECT, 'page');
        if (!$page instanceof \WP_Post) {
            wp_send_json_error(['message' => 'Den valgte WordPress-side blev ikke fundet.'], 404);
        }

        $rawForm = isset($_POST['form_data']) ? (string) wp_unslash($_POST['form_data']) : '';
        if ($rawForm === '' || strlen($rawForm) > 2 * 1024 * 1024) {
            wp_send_json_error(['message' => 'Editor-data mangler eller er for stor til forhåndsvisning.'], 400);
        }

        $formData = [];
        parse_str($rawForm, $formData);
        $rawSections = isset($formData['sections']) && is_array($formData['sections']) ? $formData['sections'] : [];
        $sections = [];
        foreach (array_slice($rawSections, 0, 150, true) as $section) {
            if (!is_array($section) || !empty($section['Remove'])) {
                continue;
            }
            $sections[] = $section;
        }

        $store = get_option(self::PAGE_OPTION, []);
        $savedPageData = is_array($store) && isset($store[$slug]) && is_array($store[$slug])
            ? $store[$slug]
            : [];
        $pageData = $savedPageData;
        $pageData['PageSlug'] = $slug;
        $pageData['PageTitle'] = (string) $page->post_title;
        $pageData['Sections'] = $sections;

        // Preserve current top-level context fields if the editor form exposes them.
        foreach (['DataContextType', 'DataContextEntryId'] as $field) {
            if (array_key_exists($field, $formData)) {
                $pageData[$field] = is_scalar($formData[$field]) ? (string) $formData[$field] : '';
            }
        }

        $spanSections = [];
        $rawSpans = isset($_POST['spans_json']) ? (string) wp_unslash($_POST['spans_json']) : '';
        if ($rawSpans !== '' && strlen($rawSpans) <= 512 * 1024) {
            $decoded = json_decode($rawSpans, true);
            if (is_array($decoded)) {
                foreach (array_slice($decoded, 0, 150, true) as $key => $state) {
                    $cleanKey = sanitize_key((string) $key);
                    if ($cleanKey !== '' && is_array($state)) {
                        $spanSections[$cleanKey] = $state;
                    }
                }
            }
        }

        try {
            $token = bin2hex(random_bytes(16));
        } catch (\Throwable $exception) {
            $token = str_replace('-', '', wp_generate_uuid4());
        }

        set_transient(
            self::PREVIEW_PREFIX . $token,
            [
                'PageSlug' => $slug,
                'PageData' => $pageData,
                'SpanSections' => $spanSections,
                'UserId' => get_current_user_id(),
                'CreatedUtc' => gmdate('c'),
            ],
            10 * MINUTE_IN_SECONDS
        );

        $url = add_query_arg(
            [
                'h18_live_preview' => $token,
                'h18_frontend_preview' => time(),
            ],
            (string) get_permalink($page)
        );

        wp_send_json_success([
            'previewUrl' => esc_url_raw($url),
            'sectionCount' => count($sections),
            'spanCount' => count($spanSections),
        ]);
    }
}
