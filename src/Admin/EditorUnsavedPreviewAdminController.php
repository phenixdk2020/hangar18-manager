<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Exact frontend preview for the page currently open in the Sider editor.
 *
 * The old implementation cloned the admin canvas and tried to remove editor
 * chrome afterwards. That could never be 1:1 with the public renderer and was
 * fragile whenever LEGO/Inspector markup changed. The preview now loads the
 * real saved public page in an iframe. It remains read-only and performs no
 * option/post mutation. Unsaved editor changes must be saved before they can be
 * represented by this exact frontend preview.
 */
final class EditorUnsavedPreviewAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
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
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.82',
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
                'mode'       => 'saved-frontend',
                'pageSlug'   => $slug,
                'previewUrl' => $previewUrl ? esc_url_raw((string) $previewUrl) : '',
            ]
        );
    }
}
