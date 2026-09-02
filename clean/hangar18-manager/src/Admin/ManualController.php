<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

final class ManualController
{
    public const PAGE_SLUG = 'visual-designer-brugermanual';
    public const SHORTCODE = 'visual_designer_manager_manual';

    private const PAGE_OPTION = 'h18_vd_user_manual_page_id_v0183';
    private const HTML_FILE = 'docs/user-manual.html';
    private const DOCX_FILE = 'docs/visual-designer-manager-brugermanual.docx';
    private const STYLE_HANDLE = 'h18-vd-user-manual-v0183';

    public static function register(): void
    {
        add_shortcode(self::SHORTCODE, [self::class, 'shortcode']);
        add_action('admin_init', [self::class, 'ensurePage'], 40);
        add_action('wp_enqueue_scripts', [self::class, 'enqueueFrontend']);
    }

    public static function ensurePage(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $storedId = absint(get_option(self::PAGE_OPTION, 0));
        if ($storedId > 0) {
            $stored = get_post($storedId);
            if ($stored instanceof \WP_Post && $stored->post_type === 'page' && $stored->post_status !== 'trash') {
                return;
            }
        }

        $existing = get_page_by_path(self::PAGE_SLUG, OBJECT, 'page');
        if ($existing instanceof \WP_Post && $existing->post_status !== 'trash') {
            if (!has_shortcode((string) $existing->post_content, self::SHORTCODE)) {
                wp_update_post([
                    'ID' => (int) $existing->ID,
                    'post_content' => '[' . self::SHORTCODE . ']',
                ]);
            }
            update_option(self::PAGE_OPTION, (int) $existing->ID, false);
            return;
        }

        $pageId = wp_insert_post([
            'post_type' => 'page',
            'post_status' => 'publish',
            'post_title' => 'Brugermanual',
            'post_name' => self::PAGE_SLUG,
            'post_content' => '[' . self::SHORTCODE . ']',
            'comment_status' => 'closed',
            'ping_status' => 'closed',
        ], true);

        if (!is_wp_error($pageId) && (int) $pageId > 0) {
            update_option(self::PAGE_OPTION, (int) $pageId, false);
        }
    }

    public static function enqueueFrontend(): void
    {
        if (!is_singular('page')) {
            return;
        }
        $post = get_post();
        if (!$post instanceof \WP_Post || !has_shortcode((string) $post->post_content, self::SHORTCODE)) {
            return;
        }
        self::enqueueAssets();
    }

    public static function shortcode(): string
    {
        self::enqueueAssets();
        return self::renderManual(false);
    }

    public static function adminPage(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke adgang til denne side.', 'visual-designer-manager'));
        }
        self::ensurePage();
        self::enqueueAssets();

        echo '<div class="wrap h18-vd-manual-admin">';
        echo '<h1>Brugermanual</h1>';
        echo '<p>Den samme kanoniske brugermanual vises på websitet og leveres som Word-fil i denne Visual Designer Manager-version.</p>';
        echo self::toolbar(true); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
        echo self::renderManual(true); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
        echo '</div>';
    }

    public static function websiteUrl(): string
    {
        $pageId = absint(get_option(self::PAGE_OPTION, 0));
        if ($pageId > 0) {
            $permalink = get_permalink($pageId);
            if (is_string($permalink) && $permalink !== '') {
                return $permalink;
            }
        }
        return home_url('/' . self::PAGE_SLUG . '/');
    }

    public static function downloadUrl(): string
    {
        return H18_CLEAN_URL . self::DOCX_FILE;
    }

    private static function renderManual(bool $admin): string
    {
        $path = H18_CLEAN_DIR . self::HTML_FILE;
        if (!is_file($path) || !is_readable($path)) {
            return '<div class="h18-vd-manual-notice"><strong>Brugermanualen mangler i denne installation.</strong><br>Installer eller opdatér Visual Designer Manager igen, så de genererede manualfiler kommer med.</div>';
        }

        $html = file_get_contents($path);
        if (!is_string($html) || trim($html) === '') {
            return '<div class="h18-vd-manual-notice"><strong>Brugermanualen kunne ikke læses.</strong></div>';
        }

        $assetBase = H18_CLEAN_URL . 'docs/user-manual-assets/';
        $html = str_replace('src="docs/user-manual-assets/', 'src="' . esc_url($assetBase), $html);
        $html = str_replace("src='docs/user-manual-assets/", "src='" . esc_url($assetBase), $html);

        $toolbar = $admin ? '' : self::toolbar(false);
        return '<div class="h18-vd-manual">' . $toolbar . '<article class="h18-vd-manual-content">' . $html . '</article></div>';
    }

    private static function toolbar(bool $admin): string
    {
        $managerUrl = admin_url('admin.php?page=' . AdminController::MENU);
        $websiteUrl = self::websiteUrl();
        $downloadUrl = self::downloadUrl();

        $html = '<div class="h18-vd-manual-toolbar">';
        if ($admin) {
            $html .= '<a class="button button-primary" href="' . esc_url($websiteUrl) . '" target="_blank" rel="noopener">Åbn på websitet</a>';
        } else {
            $html .= '<a class="h18-vd-manual-button is-primary" href="' . esc_url($managerUrl) . '">Åbn Visual Designer Manager</a>';
        }
        $html .= '<a class="' . ($admin ? 'button' : 'h18-vd-manual-button') . '" href="' . esc_url($downloadUrl) . '" download>Download som Word (.docx)</a>';
        $html .= '</div>';
        return $html;
    }

    private static function enqueueAssets(): void
    {
        wp_enqueue_style(self::STYLE_HANDLE, H18_CLEAN_URL . 'assets/manual-v0183.css', [], H18_CLEAN_VERSION);
    }

    private function __construct()
    {
    }
}
