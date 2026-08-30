<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Migration\ExternalPageSourceService;
use VisualDesignerManager\Migration\PageConversionService;
use VisualDesignerManager\Model\LayoutModel;

final class ConversionController
{
    private const PREPARE_ACTION = 'h18_vd_conversion_prepare_v0150';
    private const EXTERNAL_PREPARE_ACTION = 'h18_vd_conversion_external_prepare_v0151';
    private const BATCH_ACTION = 'h18_vd_conversion_batch_v0150';
    private const APPROVE_ACTION = 'h18_vd_conversion_approve_v0150';
    private const DISCARD_ACTION = 'h18_vd_conversion_discard_v0150';
    private const PREVIEW_ACTION = 'h18_vd_conversion_preview_v0150';
    private const NONCE = 'h18_vd_conversion_v0150';

    public static function register(): void
    {
        add_action('admin_post_' . self::PREPARE_ACTION, [self::class, 'prepare']);
        add_action('admin_post_' . self::EXTERNAL_PREPARE_ACTION, [self::class, 'externalPrepare']);
        add_action('admin_post_' . self::BATCH_ACTION, [self::class, 'batch']);
        add_action('admin_post_' . self::APPROVE_ACTION, [self::class, 'approve']);
        add_action('admin_post_' . self::DISCARD_ACTION, [self::class, 'discard']);
        add_action('admin_post_' . self::PREVIEW_ACTION, [self::class, 'preview']);
    }

    public static function render(): void
    {
        self::guard();
        $pages = self::pages();
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));
        $statusMessage = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $counts = ['active' => 0, 'review' => 0, 'not-converted' => 0];
        foreach ($pages as $page) {
            $row = PageConversionService::status((int) $page->ID);
            $key = (string) ($row['status'] ?? 'not-converted');
            if (isset($counts[$key])) { $counts[$key]++; }
        }

        echo '<div class="wrap h18-manager-admin">';
        echo '<h1>Konvertering af sider</h1>';
        echo '<p class="h18-manager-description">Forbered Visual Designer-versioner af lokale WordPress-sider eller hent en eksisterende side fra et andet offentligt HTTPS-site. Eksterne Gutenberg/page-frame-sider opdeles nu i rigtige Sektioner, Tekst, Billeder, Knapper og Kasser. Alt oprettes først som QA-kandidat; først <strong>Godkend og aktivér</strong> ændrer mål-sidens Visual Designer-model.</p>';
        if ($message !== '') {
            echo '<div class="notice ' . ($statusMessage === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>';
        }

        echo '<div class="h18-manager-stats">';
        self::stat('Sider', count($pages), 'WordPress-sider i alt');
        self::stat('Aktive VD', $counts['active'], 'Allerede aktive Visual Designer-sider');
        self::stat('Klar til QA', $counts['review'], 'Ikke aktiverede kandidater');
        self::stat('Ikke konverteret', $counts['not-converted'], 'Kan forberedes i batch');
        echo '</div>';

        echo '<section class="h18-manager-card"><h2>Sikker arbejdsgang</h2><ol class="h18-manager-list"><li><strong>Konvertér</strong> eller <strong>Hent ekstern side</strong> opretter kun en kandidat.</li><li><strong>Forhåndsvis</strong> viser kandidat + aktiv Header/Footer uden at ændre frontend.</li><li><strong>Godkend og aktivér</strong> opretter en ny Visual Designer-version. Lokal <code>post_content</code> overskrives ikke.</li></ol><p class="description">Første automatiske pass bevarer body-HTML i en canonical Text-blok. Komplekse layouts kræver fortsat visuel QA og kan bagefter opdeles i rigtige Text/Image/Button/Kasse-elementer.</p></section>';

        echo '<section class="h18-manager-card"><h2>Ekstern kilde</h2><p>Hent en eksisterende side fra et andet offentligt HTTPS-site som QA-kandidat. Kildesitet læses kun; det ændres aldrig.</p>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-manager-page-create-form">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::EXTERNAL_PREPARE_ACTION) . '">';
        echo '<label style="min-width:320px;flex:2"><strong>Kilde-URL</strong><input type="url" name="source_url" required value="https://test2.hangar18.dk/" placeholder="https://test2.hangar18.dk/"></label>';
        echo '<label style="min-width:260px"><strong>Målside</strong><select name="target_post_id"><option value="0">Opret ny WordPress-kladde</option>';
        foreach ($pages as $targetPage) {
            echo '<option value="' . esc_attr((string) $targetPage->ID) . '">' . esc_html((string) $targetPage->post_title) . ' · ' . esc_html((string) $targetPage->post_name) . '</option>';
        }
        echo '</select></label>';
        echo '<label style="min-width:220px"><strong>Titel ved ny side</strong><input type="text" name="new_title" placeholder="Automatisk fra kilden"></label>';
        echo '<button class="button button-primary" type="submit">Hent ekstern side til QA</button></form>';
        echo '<p class="description">Kilden læses kun. På det gamle Hangar18-layout vælges selve <code>h18-page-frame</code>, så gammel Header/Footer/Menu ikke importeres som sideindhold. Hero, baggrundsfarver, Gutenberg-sektioner, kolonner, tekst, billeder og knapper bliver canonical Visual Designer-elementer. Eksterne billeder er fortsat kilde-linkede og skal QA-godkendes.</p>';
echo '</section>';

        echo '<form id="h18-vd-conversion-batch" method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-manager-toolbar">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::BATCH_ACTION) . '">';
        echo '<button class="button button-primary" type="submit" name="scope" value="selected">Konvertér markerede</button>';
        echo '<button class="button" type="submit" name="scope" value="all">Konvertér alle ikke-konverterede</button>';
        echo '</form>';

        echo '<table class="widefat striped h18-manager-table"><thead><tr><th style="width:34px"><input type="checkbox" id="h18-vd-select-all"></th><th>Side</th><th>WordPress</th><th>Konvertering</th><th>Bemærkninger</th><th>Handlinger</th></tr></thead><tbody>';
        foreach ($pages as $page) {
            $postId = (int) $page->ID;
            $state = PageConversionService::status($postId);
            $key = (string) ($state['status'] ?? 'not-converted');
            $badge = $key === 'active'
                ? '<span class="h18-manager-badge is-ok">Aktiv Visual Designer</span>'
                : ($key === 'review' ? '<span class="h18-manager-badge is-progress">Klar til QA</span>' : '<span class="h18-manager-badge">Ikke konverteret</span>');
            $wpStatus = get_post_status_object((string) $page->post_status);
            $wpLabel = $wpStatus ? (string) $wpStatus->label : (string) $page->post_status;
            $warnings = isset($state['warnings']) && is_array($state['warnings']) ? $state['warnings'] : [];
            if (!empty($state['sourceChanged'])) { $warnings[] = 'Kildesiden er ændret siden kandidaten blev lavet'; }

            echo '<tr>';
            echo '<td><input class="h18-vd-page-check" form="h18-vd-conversion-batch" type="checkbox" name="post_ids[]" value="' . esc_attr((string) $postId) . '"></td>';
            echo '<td><strong>' . esc_html((string) $page->post_title) . '</strong><br><small>ID ' . esc_html((string) $postId) . ' · <code>' . esc_html((string) $page->post_name) . '</code></small></td>';
            echo '<td>' . esc_html($wpLabel) . ($page->post_status === 'publish' ? '<br><span class="h18-manager-badge is-ok">Live</span>' : '') . '</td>';
            echo '<td>' . $badge;
            if ((int) ($state['version'] ?? 0) > 0) { echo '<br><small>Designer v' . esc_html((string) $state['version']) . '</small>'; }
            echo '</td>';
            $sourceInfo = (string) ($state['sourceType'] ?? 'local') === 'external' && !empty($state['sourceUrl'])
                ? '<br><small>Kilde: <code>' . esc_html((string) $state['sourceUrl']) . '</code></small>'
                : '';
            echo '<td>' . ($warnings ? '<small>' . esc_html(implode(' · ', array_unique(array_map('strval', $warnings)))) . '</small>' : '<span class="description">—</span>') . $sourceInfo . '</td>';
            echo '<td class="h18-manager-actions">';
            self::postButton(self::PREPARE_ACTION, $postId, $key === 'review' ? 'Konvertér igen' : ($key === 'active' ? 'Lav ny kandidat' : 'Konvertér'), false);
            if ($key === 'review') {
                $preview = wp_nonce_url(admin_url('admin-post.php?action=' . self::PREVIEW_ACTION . '&post_id=' . $postId), self::NONCE);
                echo '<a class="button" target="_blank" rel="noopener" href="' . esc_url($preview) . '">Forhåndsvis kandidat</a>';
                self::postButton(self::APPROVE_ACTION, $postId, 'Godkend og aktivér', true);
                self::postButton(self::DISCARD_ACTION, $postId, 'Kassér kandidat', false);
            }
            if (!empty($state['active'])) {
                echo '<a class="button button-primary" href="' . esc_url(admin_url('admin.php?page=h18-clean-editor&post=' . $postId)) . '">Designer</a>';
            }
            echo '</td></tr>';
        }
        echo '</tbody></table>';
        echo '<script>document.addEventListener("DOMContentLoaded",function(){var all=document.getElementById("h18-vd-select-all");if(!all)return;all.addEventListener("change",function(){document.querySelectorAll(".h18-vd-page-check").forEach(function(box){box.checked=all.checked;});});});</script>';
        echo '</div>';
    }


    public static function externalPrepare(): void
    {
        self::guard();
        check_admin_referer(self::NONCE);
        $sourceUrl = esc_url_raw((string) wp_unslash($_POST['source_url'] ?? ''));
        $targetPostId = absint($_POST['target_post_id'] ?? 0);
        $newTitle = sanitize_text_field((string) wp_unslash($_POST['new_title'] ?? ''));
        $createdPostId = 0;

        try {
            $sourceData = ExternalPageSourceService::fetch($sourceUrl);
            if ($targetPostId <= 0) {
                if (!current_user_can('edit_pages')) {
                    throw new \RuntimeException('Du har ikke rettighed til at oprette en målside.');
                }
                $title = $newTitle !== '' ? $newTitle : sanitize_text_field((string) ($sourceData['title'] ?? ''));
                if ($title === '') {
                    $path = trim((string) wp_parse_url($sourceUrl, PHP_URL_PATH), '/');
                    $title = $path === '' ? 'Hjem – Visual Designer' : ucwords(str_replace(['-', '_'], ' ', basename($path)));
                }
                $slugBase = trim((string) wp_parse_url($sourceUrl, PHP_URL_PATH), '/');
                $slugBase = $slugBase === '' ? 'hjem-visual-designer' : sanitize_title(basename($slugBase));
                $created = wp_insert_post([
                    'post_type' => 'page',
                    'post_status' => 'draft',
                    'post_title' => $title,
                    'post_name' => $slugBase,
                    'post_content' => '',
                ], true);
                if (is_wp_error($created)) {
                    throw new \RuntimeException('Målsiden kunne ikke oprettes: ' . $created->get_error_message());
                }
                $targetPostId = (int) $created;
                $createdPostId = $targetPostId;
            } else {
                self::assertEditablePage($targetPostId);
            }

            PageConversionService::prepareExternalData($targetPostId, $sourceData, get_current_user_id());
            $target = get_post($targetPostId);
            $targetTitle = $target instanceof \WP_Post ? (string) $target->post_title : ('ID ' . $targetPostId);
            self::redirect('success', 'Ekstern kilde er hentet til QA på “' . $targetTitle . '”. Kildesitet og frontend er ikke ændret.');
        } catch (\Throwable $error) {
            if ($createdPostId > 0 && get_post_type($createdPostId) === 'page') {
                wp_delete_post($createdPostId, true);
            }
            self::redirect('error', 'Ekstern konvertering fejlede: ' . $error->getMessage());
        }
    }

    public static function prepare(): void
    {
        self::guard();
        check_admin_referer(self::NONCE);
        $postId = absint($_POST['post_id'] ?? 0);
        self::assertEditablePage($postId);
        try {
            PageConversionService::prepare($postId, get_current_user_id());
            self::redirect('success', 'Konverteringskandidaten er klar til QA. Frontend er ikke ændret.');
        } catch (\Throwable $error) {
            self::redirect('error', 'Konvertering fejlede: ' . $error->getMessage());
        }
    }

    public static function batch(): void
    {
        self::guard();
        check_admin_referer(self::NONCE);
        $scope = sanitize_key((string) ($_POST['scope'] ?? 'selected'));
        $ids = [];
        if ($scope === 'all') {
            foreach (self::pages() as $page) {
                $state = PageConversionService::status((int) $page->ID);
                if (empty($state['active'])) { $ids[] = (int) $page->ID; }
            }
        } else {
            foreach ((array) ($_POST['post_ids'] ?? []) as $raw) {
                $id = absint($raw);
                if ($id > 0) { $ids[] = $id; }
            }
        }
        $ids = array_values(array_unique($ids));
        if (!$ids) { self::redirect('error', 'Ingen sider blev valgt.'); }

        $ok = 0; $failed = 0;
        foreach ($ids as $postId) {
            if (get_post_type($postId) !== 'page' || !current_user_can('edit_post', $postId)) { $failed++; continue; }
            try { PageConversionService::prepare($postId, get_current_user_id()); $ok++; }
            catch (\Throwable $error) { $failed++; }
        }
        self::redirect($failed > 0 ? 'error' : 'success', $ok . ' kandidat(er) klar til QA' . ($failed > 0 ? ' · ' . $failed . ' fejlede' : '') . '. Ingen sider blev aktiveret automatisk.');
    }

    public static function approve(): void
    {
        self::guard();
        check_admin_referer(self::NONCE);
        $postId = absint($_POST['post_id'] ?? 0);
        self::assertEditablePage($postId);
        try {
            $version = PageConversionService::approve($postId, get_current_user_id());
            self::redirect('success', 'Siden er godkendt og aktiveret som Visual Designer v' . $version . '. Originalt WordPress-indhold er bevaret som fallback.');
        } catch (\Throwable $error) {
            self::redirect('error', 'Godkendelse fejlede: ' . $error->getMessage());
        }
    }

    public static function discard(): void
    {
        self::guard();
        check_admin_referer(self::NONCE);
        $postId = absint($_POST['post_id'] ?? 0);
        self::assertEditablePage($postId);
        PageConversionService::discard($postId);
        self::redirect('success', 'Konverteringskandidaten er kasseret. Den offentlige side er ikke ændret.');
    }

    public static function preview(): void
    {
        self::guard();
        check_admin_referer(self::NONCE);
        $postId = absint($_GET['post_id'] ?? 0);
        self::assertEditablePage($postId);
        try {
            nocache_headers();
            header('Content-Type: text/html; charset=' . get_option('blog_charset', 'UTF-8'));
            echo PageConversionService::previewDocument($postId); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
            exit;
        } catch (\Throwable $error) {
            wp_die(esc_html($error->getMessage()));
        }
    }

    private static function postButton(string $action, int $postId, string $label, bool $confirm): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr($action) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '">';
        echo '<button class="button' . ($action === self::APPROVE_ACTION ? ' button-primary' : '') . '" type="submit"' . ($confirm ? ' onclick="return confirm(\'Godkend kandidaten og aktivér Visual Designer på denne side?\');"' : '') . '>' . esc_html($label) . '</button></form>';
    }

    /** @return array<int,\WP_Post> */
    private static function pages(): array
    {
        $pages = get_pages([
            'sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC',
            'post_status' => ['publish', 'draft', 'pending', 'private', 'future'],
        ]);
        return array_values(array_filter($pages, static fn($page): bool => $page instanceof \WP_Post));
    }

    private static function assertEditablePage(int $postId): void
    {
        if ($postId <= 0 || get_post_type($postId) !== 'page' || !current_user_can('edit_post', $postId)) {
            wp_die(esc_html__('Ingen adgang til siden.', 'visual-designer-manager'));
        }
    }

    private static function redirect(string $status, string $message): void
    {
        wp_safe_redirect(add_query_arg([
            'page' => 'h18-clean-conversion', 'vd_status' => $status, 'vd_message' => $message,
        ], admin_url('admin.php')));
        exit;
    }

    private static function stat(string $label, int $value, string $hint): void
    {
        echo '<div class="h18-manager-stat"><span>' . esc_html($label) . '</span><strong>' . esc_html((string) $value) . '</strong><small>' . esc_html($hint) . '</small></div>';
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
    }

    private function __construct()
    {
    }
}
