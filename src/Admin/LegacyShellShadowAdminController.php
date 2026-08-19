<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionSiteTemplateRepository;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use Hangar18\UltimateDesigner\SiteBuilder\LegacyShellShadowImportService;
use Hangar18\UltimateDesigner\SiteBuilder\LegacyShellSnapshotService;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateValidator;

/**
 * I2A bridge from the currently authoritative legacy Header/Footer shell to
 * isolated Designer shadow templates.
 *
 * Snapshot reads remain read-only. The only write path in this controller is an
 * explicit, nonce-protected, source-hash-bound import into Site Builder shadow
 * template storage. No global assignment or frontend renderer is exposed here.
 */
final class LegacyShellShadowAdminController
{
    private const HEADER_OPTION = 'hangar18_manager_header_design_v25';
    private const NONCE_ACTION = 'h18_ud_import_legacy_shell_shadow';

    public static function register(): void
    {
        add_action('admin_post_h18_ud_import_legacy_shell_shadow', [self::class, 'importShadow']);
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
        $plan = null;
        $planError = '';
        try {
            $plan = self::importService()->plan($snapshot);
        } catch (\Throwable $error) {
            $planError = $error->getMessage();
        }

        echo '<section class="h18-ud-builder-panel">';
        echo '<div class="h18-ud-builder-panel-head"><div><h2>I2A · Nuværende Header/Footer baseline</h2><p>Snapshot af den shell der er autoritativ på hjemmesiden nu. Baseline kan importeres kontrolleret til isolerede Designer shadow-templates til visuel sammenligning.</p></div><span class="h18-ud-shadow-badge">SHADOW IMPORT · ingen cutover</span></div>';
        echo '<div class="notice notice-info inline"><p><strong>Frontend er uændret:</strong> Baseline-adapteren læser <code>' . esc_html((string) ($snapshot['HeaderOption'] ?? self::HEADER_OPTION)) . '</code> og eksisterende Header/Footer-markører. Import skriver kun til Site Builder shadow-template storage og laver ingen global assignment.</p></div>';
        echo '<div class="h18-ud-status-grid">';
        self::card('Legacy shell source', ((int) ($snapshot['SourcePostId'] ?? 0)) > 0 ? 'Side #' . (int) $snapshot['SourcePostId'] : 'Ikke fundet', (string) ($snapshot['SourcePostTitle'] ?? ''));
        self::card('Header marker', $header ? 'Komplet' : 'Mangler', (int) ($snapshot['HeaderBytes'] ?? 0) . ' bytes');
        self::card('Footer marker', $footer ? 'Komplet' : 'Mangler', (int) ($snapshot['FooterBytes'] ?? 0) . ' bytes');
        self::card('Legacy design', (int) ($snapshot['DesignKeyCount'] ?? 0) . ' gemte felter', 'Runtime v' . (string) ($snapshot['RuntimeVersion'] ?? ''));
        if (is_array($plan)) {
            self::card(
                'Shadow import',
                !empty($plan['AlreadyImported']) ? 'Importeret' : ($ready ? 'Klar' : 'Blokeret'),
                'Hash-bundet · ingen global assignment'
            );
        }
        echo '</div>';
        echo '<p><strong>Kilde-hash:</strong> <code>' . esc_html($hash) . '</code></p>';

        if ($planError !== '') {
            echo '<div class="notice notice-error inline"><p><strong>Importplan kunne ikke bygges:</strong> ' . esc_html($planError) . '</p></div>';
        } elseif (!$ready) {
            echo '<p class="description">Baseline er ikke komplet. Shadow-import forbliver blokeret indtil både Header- og Footer-markør er fundet.</p>';
        } elseif (is_array($plan) && !empty($plan['Conflicts'])) {
            echo '<div class="notice notice-error inline"><p><strong>Importkonflikt:</strong> ' . esc_html(implode(' ', (array) $plan['Conflicts'])) . '</p></div>';
        } elseif (is_array($plan) && !empty($plan['AlreadyImported'])) {
            echo '<div class="notice notice-success inline"><p><strong>Denne baseline er allerede importeret.</strong> Den eksisterende legacy Header/Footer er fortsat autoritativ på frontend.</p></div>';
            self::renderImportedLinks($plan);
        } elseif (is_array($plan)) {
            echo '<p class="description">Baseline er komplet. Importen opretter et hash-bundet Header/Footer-par i shadow storage. Hvis legacy-kilden ændrer sig inden klik, afvises importen automatisk.</p>';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" onsubmit="return confirm(\'Importer den aktuelle legacy Header/Footer baseline til shadow templates? Frontend ændres ikke.\');">';
            wp_nonce_field(self::NONCE_ACTION);
            echo '<input type="hidden" name="action" value="h18_ud_import_legacy_shell_shadow">';
            echo '<input type="hidden" name="source_hash" value="' . esc_attr($hash) . '">';
            echo '<button type="submit" class="button button-primary">Importer baseline til shadow templates</button>';
            echo ' <span class="description"><code>' . esc_html((string) ($plan['HeaderTemplateId'] ?? '')) . '</code> + <code>' . esc_html((string) ($plan['FooterTemplateId'] ?? '')) . '</code></span>';
            echo '</form>';
        }

        echo '</section>';
    }

    public static function importShadow(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke rettigheder til denne handling.', 'hangar18-manager'));
        }
        check_admin_referer(self::NONCE_ACTION);

        $expectedHash = strtolower((string) preg_replace('/[^a-f0-9]/i', '', (string) wp_unslash($_POST['source_hash'] ?? '')));
        if (strlen($expectedHash) !== 64) {
            self::redirect('error', 'Importplanen mangler en gyldig SourceHash. Genindlæs Designer-overblikket.');
        }

        try {
            $snapshot = self::snapshot();
            $currentHash = strtolower((string) ($snapshot['SourceHash'] ?? ''));
            if (!hash_equals($expectedHash, $currentHash)) {
                throw new \RuntimeException('Legacy Header/Footer har ændret sig siden importplanen blev vist. Genindlæs siden og gennemgå den nye baseline først.');
            }
            if (empty($snapshot['ReadyForShadowImport'])) {
                throw new \RuntimeException('Legacy Header/Footer baseline er ikke komplet.');
            }

            // Only the editable shadow copy is sanitized. SourceHash remains bound
            // to the exact authoritative legacy snapshot used to approve import.
            $snapshot['HeaderHtml'] = wp_kses_post((string) ($snapshot['HeaderHtml'] ?? ''));
            $snapshot['FooterHtml'] = wp_kses_post((string) ($snapshot['FooterHtml'] ?? ''));

            $result = self::importService()->import($snapshot);
            $headerId = (string) ($result['HeaderTemplateId'] ?? '');
            $footerId = (string) ($result['FooterTemplateId'] ?? '');
            $message = !empty($result['Idempotent'])
                ? 'Baseline var allerede importeret. Ingen nye shadow-templates blev skrevet.'
                : 'Legacy Header/Footer er importeret til shadow templates. Frontend og global assignment er uændret.';
            self::redirect('success', $message, $headerId !== '' ? $headerId : $footerId);
        } catch (\Throwable $error) {
            self::redirect('error', $error->getMessage());
        }
    }

    /** @param array<string,mixed> $plan */
    private static function renderImportedLinks(array $plan): void
    {
        $links = [];
        foreach (['HeaderTemplateId' => 'Åbn importeret Header', 'FooterTemplateId' => 'Åbn importeret Footer'] as $field => $label) {
            $id = sanitize_key((string) ($plan[$field] ?? ''));
            if ($id === '') {
                continue;
            }
            $url = add_query_arg(
                ['page' => IntegrationAdminBootstrap::PAGE_SLUG, 'ud_template' => $id],
                admin_url('admin.php')
            );
            $links[] = '<a class="button" href="' . esc_url($url) . '">' . esc_html($label) . '</a>';
        }
        if ($links !== []) {
            echo '<p>' . implode(' ', $links) . '</p>';
        }
    }

    private static function importService(): LegacyShellShadowImportService
    {
        return new LegacyShellShadowImportService(
            new WordPressOptionSiteTemplateRepository(),
            new SiteTemplateValidator(new PageSchemaValidator())
        );
    }

    private static function redirect(string $status, string $message, string $templateId = ''): void
    {
        $args = [
            'page' => IntegrationAdminBootstrap::PAGE_SLUG,
            'ud_status' => $status === 'error' ? 'error' : 'success',
            'ud_message' => $message,
        ];
        if ($templateId !== '') {
            $args['ud_template'] = sanitize_key($templateId);
        }
        wp_safe_redirect(add_query_arg($args, admin_url('admin.php')));
        exit;
    }

    /** @return array{PostId:int,PostTitle:string,Content:string} */
    private static function shellSource(): array
    {
        if (function_exists('get_page_by_path')) {
            $output = defined('OBJECT') ? OBJECT : 'OBJECT';
            $home = get_page_by_path('hjem', $output, 'page');
            if ($home instanceof \WP_Post) {
                $content = (string) $home->post_content;
                if (self::hasShell($content)) {
                    return ['PostId' => (int) $home->ID, 'PostTitle' => (string) $home->post_title, 'Content' => $content];
                }
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
