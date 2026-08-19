<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\SiteBuilder\LegacyShellSnapshotService;

/**
 * Read-only bridge from the current legacy Header/Footer shell to the Designer.
 * It creates no options, post meta, templates or public renderer changes.
 */
final class LegacyShellShadowAdminController
{
    private const HEADER_OPTION = 'hangar18_manager_header_design_v25';

    public static function register(): void
    {
        // Intentionally no write/action handlers in this phase.
    }

    /** @return array<string,mixed> */
    public static function snapshot(): array
    {
        $design = get_option(self::HEADER_OPTION, []);
        if (!is_array($design)) {
            $design = [];
        }

        $source = self::shellSource();
        $version = class_exists('Hangar18_Manager') ? (string) \Hangar18_Manager::VERSION : '';
        $snapshot = (new LegacyShellSnapshotService())->build($design, (string) ($source['Content'] ?? ''), $version);
        $snapshot['SourcePostId'] = (int) ($source['PostId'] ?? 0);
        $snapshot['SourcePostTitle'] = (string) ($source['PostTitle'] ?? '');
        $snapshot['HeaderOption'] = self::HEADER_OPTION;
        return $snapshot;
    }

    public static function renderPanel(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $snapshot = self::snapshot();
        $ready = !empty($snapshot['ReadyForShadowImport']);
        $header = !empty($snapshot['HeaderMarkerComplete']);
        $footer = !empty($snapshot['FooterMarkerComplete']);
        $hash = (string) ($snapshot['SourceHash'] ?? '');

        echo '<section class="h18-ud-builder-panel">';
        echo '<div class="h18-ud-builder-panel-head"><div><h2>I2A · Nuværende Header/Footer baseline</h2><p>Read-only snapshot af den shell der er autoritativ på hjemmesiden nu. Den bruges som facit før Designer-import og senere visuel sammenligning.</p></div><span class="h18-ud-shadow-badge">READ ONLY · ingen writes</span></div>';
        echo '<div class="notice notice-info inline"><p><strong>Frontend er uændret:</strong> Baseline-adapteren læser kun <code>' . esc_html((string) ($snapshot['HeaderOption'] ?? self::HEADER_OPTION)) . '</code> og eksisterende Header/Footer-markører. Den opretter ikke templates og aktiverer ingen renderer.</p></div>';
        echo '<div class="h18-ud-status-grid">';
        self::card('Legacy shell source', ((int) ($snapshot['SourcePostId'] ?? 0)) > 0 ? 'Side #' . (int) $snapshot['SourcePostId'] : 'Ikke fundet', (string) ($snapshot['SourcePostTitle'] ?? ''));
        self::card('Header marker', $header ? 'Komplet' : 'Mangler', (int) ($snapshot['HeaderBytes'] ?? 0) . ' bytes');
        self::card('Footer marker', $footer ? 'Komplet' : 'Mangler', (int) ($snapshot['FooterBytes'] ?? 0) . ' bytes');
        self::card('Legacy design', (int) ($snapshot['DesignKeyCount'] ?? 0) . ' gemte felter', 'Runtime v' . esc_html((string) ($snapshot['RuntimeVersion'] ?? '')));
        echo '</div>';
        echo '<p><strong>Kilde-hash:</strong> <code>' . esc_html($hash) . '</code></p>';
        echo '<p class="description">' . esc_html($ready ? 'Baseline er komplet og kan bruges som kilde til næste trin: kontrolleret import til Header/Footer shadow-templates.' : 'Baseline er ikke komplet. Import til Designer skal forblive blokeret indtil både Header- og Footer-markør er fundet.') . '</p>';
        echo '</section>';
    }

    /** @return array{PostId:int,PostTitle:string,Content:string} */
    private static function shellSource(): array
    {
        $home = get_page_by_path('hjem', OBJECT, 'page');
        if ($home instanceof \WP_Post) {
            $content = (string) $home->post_content;
            if (self::hasShell($content)) {
                return ['PostId' => (int) $home->ID, 'PostTitle' => (string) $home->post_title, 'Content' => $content];
            }
        }

        $pages = get_posts([
            'post_type' => 'page',
            'post_status' => ['publish','draft','private','pending','future'],
            'posts_per_page' => -1,
            'orderby' => 'ID',
            'order' => 'ASC',
            'suppress_filters' => false,
        ]);
        foreach ($pages as $page) {
            if (!$page instanceof \WP_Post) {
                continue;
            }
            $content = (string) $page->post_content;
            if (self::hasShell($content)) {
                return ['PostId' => (int) $page->ID, 'PostTitle' => (string) $page->post_title, 'Content' => $content];
            }
        }
        return ['PostId' => 0, 'PostTitle' => '', 'Content' => ''];
    }

    private static function hasShell(string $content): bool
    {
        return strpos($content, LegacyShellSnapshotService::HEADER_START) !== false
            && strpos($content, LegacyShellSnapshotService::HEADER_END) !== false
            && strpos($content, LegacyShellSnapshotService::FOOTER_START) !== false
            && strpos($content, LegacyShellSnapshotService::FOOTER_END) !== false;
    }

    private static function card(string $title, string $value, string $description): void
    {
        echo '<section class="h18-ud-status-card"><h3>' . esc_html($title) . '</h3><strong>' . esc_html($value) . '</strong><p>' . esc_html($description) . '</p></section>';
    }
}
