from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'clean' / 'hangar18-manager'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Visual Designer Manager 0.1.50
# ---------------------------------------------------------------------------
plugin_path = PLUGIN / 'hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, ' * Version: 0.1.49', ' * Version: 0.1.50', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.49');", "define('H18_CLEAN_VERSION', '0.1.50');", 'plugin constant version')
plugin = replace_once(
    plugin,
    "require_once H18_CLEAN_DIR . 'src/Migration/LegacyFooterConverter.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Migration/LegacyFooterConverter.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';\n",
    'PageConversionService require',
)
plugin = replace_once(
    plugin,
    "require_once H18_CLEAN_DIR . 'src/Admin/AdminMenuBridge.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Admin/AdminMenuBridge.php';\nrequire_once H18_CLEAN_DIR . 'src/Admin/ConversionController.php';\n",
    'ConversionController require',
)
plugin = replace_once(
    plugin,
    "    \\Hangar18\\Clean\\Admin\\AdminMenuBridge::register();\n",
    "    \\Hangar18\\Clean\\Admin\\AdminMenuBridge::register();\n    \\Hangar18\\Clean\\Admin\\ConversionController::register();\n",
    'ConversionController register',
)
write(plugin_path, plugin)


# ---------------------------------------------------------------------------
# Non-destructive page conversion candidate service.
# ---------------------------------------------------------------------------
service = r'''<?php

declare(strict_types=1);

namespace Hangar18\Clean\Migration;

use Hangar18\Clean\Frontend\Renderer;
use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Model\TemplateLayoutModel;

/**
 * Creates a staged Visual Designer candidate without changing public output.
 * The original WordPress post_content is never overwritten by conversion.
 */
final class PageConversionService
{
    public const CANDIDATE_META = '_h18_vd_conversion_candidate_v0150';
    public const STATE_META = '_h18_vd_conversion_state_v0150';
    public const SOURCE_META = '_h18_vd_conversion_source_v0150';

    /** @return array<string,mixed> */
    public static function status(int $postId): array
    {
        $active = metadata_exists('post', $postId, LayoutModel::META);
        $version = max(0, (int) get_post_meta($postId, LayoutModel::VERSION_META, true));
        $candidate = self::candidate($postId);
        $state = get_post_meta($postId, self::STATE_META, true);
        $state = is_array($state) ? $state : [];
        $post = get_post($postId);
        $currentHash = $post instanceof \WP_Post ? hash('sha256', (string) $post->post_content) : '';
        $sourceHash = sanitize_text_field((string) ($state['sourceHash'] ?? ''));

        if ($candidate !== null) {
            $key = 'review';
        } elseif ($active) {
            $key = 'active';
        } else {
            $key = 'not-converted';
        }

        return [
            'status' => $key,
            'active' => $active,
            'version' => $version,
            'candidate' => $candidate !== null,
            'candidateDigest' => $candidate !== null ? LayoutModel::structuralDigest($candidate) : '',
            'preparedUtc' => sanitize_text_field((string) ($state['preparedUtc'] ?? '')),
            'sourceHash' => $sourceHash,
            'sourceChanged' => $sourceHash !== '' && $currentHash !== '' && !hash_equals($sourceHash, $currentHash),
            'warnings' => isset($state['warnings']) && is_array($state['warnings']) ? array_values(array_map('sanitize_text_field', $state['warnings'])) : [],
        ];
    }

    /** @return array<string,mixed> */
    public static function prepare(int $postId, int $userId): array
    {
        $post = get_post($postId);
        if (!$post instanceof \WP_Post || $post->post_type !== 'page') {
            throw new \InvalidArgumentException('Kun WordPress-sider kan konverteres.');
        }

        $source = (string) $post->post_content;
        $sourceHash = hash('sha256', $source);
        $snapshot = get_post_meta($postId, self::SOURCE_META, true);
        if (!is_array($snapshot) || !isset($snapshot['postContent'])) {
            update_post_meta($postId, self::SOURCE_META, [
                'capturedUtc' => gmdate('c'),
                'sourceHash' => $sourceHash,
                'postTitle' => (string) $post->post_title,
                'postName' => (string) $post->post_name,
                'postStatus' => (string) $post->post_status,
                'postContent' => $source,
            ]);
        }

        [$body, $warnings] = self::extractBody($source);
        $html = self::renderBlocksOnly($body, $warnings);
        $model = self::modelFromHtml($postId, $html);
        $digest = LayoutModel::structuralDigest($model);

        update_post_meta($postId, self::CANDIDATE_META, $model);
        update_post_meta($postId, self::STATE_META, [
            'status' => 'review',
            'preparedUtc' => gmdate('c'),
            'preparedBy' => max(0, $userId),
            'sourceHash' => $sourceHash,
            'sourceLength' => strlen($source),
            'bodyLength' => strlen($body),
            'candidateDigest' => $digest,
            'warnings' => $warnings,
        ]);

        return self::status($postId);
    }

    /** @return array<string,mixed>|null */
    public static function candidate(int $postId): ?array
    {
        $raw = get_post_meta($postId, self::CANDIDATE_META, true);
        if (!is_array($raw)) {
            return null;
        }
        try {
            return LayoutModel::normalize($raw);
        } catch (\Throwable $error) {
            return null;
        }
    }

    public static function approve(int $postId, int $userId): int
    {
        $candidate = self::candidate($postId);
        if ($candidate === null) {
            throw new \RuntimeException('Der findes ingen konverteringskandidat at godkende.');
        }
        $state = get_post_meta($postId, self::STATE_META, true);
        $sourceHash = is_array($state) ? sanitize_text_field((string) ($state['sourceHash'] ?? '')) : '';
        $post = get_post($postId);
        if ($post instanceof \WP_Post && $sourceHash !== '' && !hash_equals($sourceHash, hash('sha256', (string) $post->post_content))) {
            throw new \RuntimeException('Kildesiden er ændret efter konverteringen. Konvertér siden igen før godkendelse.');
        }

        $version = LayoutModel::saveVersion($postId, $candidate, $userId, 'Godkendt sidekonvertering v0.1.50 · original post_content bevaret');
        TemplateLayoutModel::ensureMigrated();
        TemplateLayoutModel::setPageChoice($postId, 'header', 'auto');
        TemplateLayoutModel::setPageChoice($postId, 'footer', 'auto');
        delete_post_meta($postId, self::CANDIDATE_META);
        update_post_meta($postId, self::STATE_META, [
            'status' => 'active',
            'approvedUtc' => gmdate('c'),
            'approvedBy' => max(0, $userId),
            'sourceHash' => $sourceHash,
            'version' => $version,
            'warnings' => is_array($state) && isset($state['warnings']) && is_array($state['warnings']) ? $state['warnings'] : [],
        ]);
        return $version;
    }

    public static function discard(int $postId): void
    {
        delete_post_meta($postId, self::CANDIDATE_META);
        if (metadata_exists('post', $postId, LayoutModel::META)) {
            $state = get_post_meta($postId, self::STATE_META, true);
            $state = is_array($state) ? $state : [];
            $state['status'] = 'active';
            $state['discardedUtc'] = gmdate('c');
            update_post_meta($postId, self::STATE_META, $state);
        } else {
            delete_post_meta($postId, self::STATE_META);
        }
    }

    public static function previewDocument(int $postId): string
    {
        $candidate = self::candidate($postId);
        $post = get_post($postId);
        if ($candidate === null || !$post instanceof \WP_Post) {
            throw new \RuntimeException('Konverteringskandidaten blev ikke fundet.');
        }

        TemplateLayoutModel::ensureMigrated();
        $headerId = TemplateLayoutModel::resolveId($postId, 'header');
        $footerId = TemplateLayoutModel::resolveId($postId, 'footer');
        $header = $headerId !== '' && TemplateLayoutModel::exists($headerId, 'header') ? TemplateLayoutModel::model($headerId) : null;
        $footer = $footerId !== '' && TemplateLayoutModel::exists($footerId, 'footer') ? TemplateLayoutModel::model($footerId) : null;
        return Renderer::standaloneDocument($candidate, $header, $footer, 'Konvertering · ' . (string) $post->post_title);
    }

    /** @return array{0:string,1:array<int,string>} */
    private static function extractBody(string $source): array
    {
        $warnings = [];
        $body = $source;
        $patterns = [
            'header' => '/<!--\s*HANGAR18-HEADER-START\s*-->.*?<!--\s*HANGAR18-HEADER-END\s*-->/is',
            'footer' => '/<!--\s*HANGAR18-FOOTER-START\s*-->.*?<!--\s*HANGAR18-FOOTER-END\s*-->/is',
        ];
        foreach ($patterns as $name => $pattern) {
            $next = preg_replace($pattern, '', $body, -1, $count);
            if (is_string($next)) {
                $body = $next;
            }
            if ($count > 0) {
                $warnings[] = 'legacy-' . $name . '-removed-global-shell-used';
            }
        }
        if (preg_match('/\[[A-Za-z0-9_-]+(?:\s[^\]]*)?\]/', $body)) {
            $warnings[] = 'shortcode-preserved-for-manual-qa';
        }
        if (stripos($body, '<script') !== false) {
            $warnings[] = 'script-markup-filtered-by-canonical-text';
        }
        if (trim(wp_strip_all_tags($body)) === '' && stripos($body, '<img') === false) {
            $warnings[] = 'source-body-empty';
        }
        return [$body, array_values(array_unique($warnings))];
    }

    /** @param array<int,string> $warnings */
    private static function renderBlocksOnly(string $body, array &$warnings): string
    {
        if (function_exists('has_blocks') && function_exists('do_blocks') && has_blocks($body)) {
            $body = do_blocks($body);
            $warnings[] = 'wordpress-blocks-rendered-to-html';
        }
        // Shortcodes are deliberately not executed during conversion; the source
        // stays immutable and QA can decide how dynamic content should be modeled.
        return trim($body);
    }

    /** @return array<string,mixed> */
    private static function modelFromHtml(int $postId, string $html): array
    {
        $plain = trim(wp_strip_all_tags($html, true));
        $blockCount = max(1, substr_count(strtolower($html), '<p') + substr_count(strtolower($html), '<div') + substr_count(strtolower($html), '<h'));
        $estimatedRows = 24 + ((int) ceil(max(1, strlen($plain)) / 80) * 4) + ($blockCount * 2);
        $rows = max(32, min(900, $estimatedRows));
        $g = static function (int $x, int $y, int $w, int $h): array {
            return [
                'desktop' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h],
                'laptop' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h, 'inheritDesktop' => true],
                'tablet' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h, 'inheritDesktop' => true],
                'mobile' => ['x' => 0, 'y' => $y, 'w' => 120, 'h' => $h, 'inheritDesktop' => false],
            ];
        };
        $suffix = substr(hash('sha256', (string) $postId), 0, 8);
        return LayoutModel::normalize(['nodes' => [
            [
                'id' => 'section-convert-' . $suffix,
                'type' => 'section',
                'parentId' => '',
                'order' => 10,
                'geometry' => $g(6, 0, 108, $rows),
                'props' => [
                    'background' => '#ffffff', 'padding' => 0, 'minHeightRows' => $rows,
                    'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
                ],
            ],
            [
                'id' => 'container-convert-' . $suffix,
                'type' => 'container',
                'parentId' => 'section-convert-' . $suffix,
                'order' => 10,
                'geometry' => $g(0, 0, 120, $rows),
                'props' => [
                    'background' => '#ffffff', 'padding' => 0, 'minHeightRows' => $rows,
                    'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
                ],
            ],
            [
                'id' => 'text-convert-' . $suffix,
                'type' => 'text',
                'parentId' => 'container-convert-' . $suffix,
                'order' => 10,
                'geometry' => $g(0, 0, 120, $rows),
                'props' => [
                    'heading' => '', 'headingLevel' => 'h2', 'text' => $html,
                    'align' => 'left', 'verticalAlign' => 'top', 'background' => '#ffffff',
                    'backgroundTransparent' => true, 'textColor' => '#30382a', 'headingColor' => '#30382a',
                    'fontFamily' => 'system', 'fontSize' => 16, 'fontWeight' => 400,
                    'lineHeight' => 1.5, 'letterSpacing' => 0, 'headingFontFamily' => 'body',
                    'headingFontSize' => 0, 'headingFontWeight' => 700, 'headingLineHeight' => 1.2,
                    'headingLetterSpacing' => 0, 'padding' => 0, 'radius' => 0,
                    'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
                ],
            ],
        ]]);
    }

    private function __construct()
    {
    }
}
'''
write(PLUGIN / 'src' / 'Migration' / 'PageConversionService.php', service)


# ---------------------------------------------------------------------------
# Conversion UI/controller. Batch conversion only prepares candidates.
# Approval is deliberately per-page because approval activates the VD model on
# published pages while preserving the original post_content as fallback.
# ---------------------------------------------------------------------------
controller = r'''<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

use Hangar18\Clean\Migration\PageConversionService;
use Hangar18\Clean\Model\LayoutModel;

final class ConversionController
{
    private const PREPARE_ACTION = 'h18_vd_conversion_prepare_v0150';
    private const BATCH_ACTION = 'h18_vd_conversion_batch_v0150';
    private const APPROVE_ACTION = 'h18_vd_conversion_approve_v0150';
    private const DISCARD_ACTION = 'h18_vd_conversion_discard_v0150';
    private const PREVIEW_ACTION = 'h18_vd_conversion_preview_v0150';
    private const NONCE = 'h18_vd_conversion_v0150';

    public static function register(): void
    {
        add_action('admin_post_' . self::PREPARE_ACTION, [self::class, 'prepare']);
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
        echo '<p class="h18-manager-description">Forbered Visual Designer-versioner af eksisterende WordPress-sider uden at ændre den offentlige side. Konvertering opretter først en QA-kandidat; først <strong>Godkend og aktivér</strong> gemmer kandidaten som en rigtig Visual Designer-version.</p>';
        if ($message !== '') {
            echo '<div class="notice ' . ($statusMessage === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>';
        }

        echo '<div class="h18-manager-stats">';
        self::stat('Sider', count($pages), 'WordPress-sider i alt');
        self::stat('Aktive VD', $counts['active'], 'Allerede aktive Visual Designer-sider');
        self::stat('Klar til QA', $counts['review'], 'Ikke aktiverede kandidater');
        self::stat('Ikke konverteret', $counts['not-converted'], 'Kan forberedes i batch');
        echo '</div>';

        echo '<section class="h18-manager-card"><h2>Sikker arbejdsgang</h2><ol class="h18-manager-list"><li><strong>Konvertér</strong> opretter en kandidat og gemmer et snapshot af den oprindelige side.</li><li><strong>Forhåndsvis</strong> viser kandidat + aktiv Header/Footer uden at ændre frontend.</li><li><strong>Godkend og aktivér</strong> opretter en ny Visual Designer-version. Original <code>post_content</code> overskrives ikke.</li></ol><p class="description">Første automatiske pass bevarer eksisterende body-HTML i en canonical Text-blok. Det giver en sikker indholdsmigrering, men komplekse legacy-layouts kan stadig kræve visuel QA og efterfølgende opdeling i rigtige Text/Image/Button/Kasse-elementer.</p></section>';

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
            echo '<td>' . ($warnings ? '<small>' . esc_html(implode(' · ', array_unique(array_map('strval', $warnings)))) . '</small>' : '<span class="description">—</span>') . '</td>';
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
            wp_die(esc_html__('Ingen adgang til siden.', 'hangar18-manager-clean'));
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
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
        }
    }

    private function __construct()
    {
    }
}
'''
write(PLUGIN / 'src' / 'Admin' / 'ConversionController.php', controller)


# ---------------------------------------------------------------------------
# Add Conversion to main navigation and dashboard.
# ---------------------------------------------------------------------------
admin_path = PLUGIN / 'src' / 'Admin' / 'AdminController.php'
admin = read(admin_path)
admin = replace_once(
    admin,
    "        add_submenu_page(self::MENU, 'Sider', 'Sider', $cap, 'h18-clean-pages', [self::class, 'pages']);\n",
    "        add_submenu_page(self::MENU, 'Sider', 'Sider', $cap, 'h18-clean-pages', [self::class, 'pages']);\n        add_submenu_page(self::MENU, 'Konvertering af sider', 'Konvertering', $cap, 'h18-clean-conversion', [ConversionController::class, 'render']);\n",
    'conversion submenu',
)
admin = replace_once(
    admin,
    "        self::card('Sider', 'Se Visual Designer-status, nodeantal og seneste version for alle WordPress-sider.', self::url('h18-clean-pages'), 'Vis sider');\n",
    "        self::card('Sider', 'Se Visual Designer-status, nodeantal og seneste version for alle WordPress-sider.', self::url('h18-clean-pages'), 'Vis sider');\n        self::card('Konvertering', 'Forbered eksisterende WordPress-sider som ikke-destruktive Visual Designer-kandidater, QA dem og aktivér én side ad gangen.', self::url('h18-clean-conversion'), 'Konvertér sider');\n",
    'conversion dashboard card',
)
write(admin_path, admin)


# ---------------------------------------------------------------------------
# Theme controller: stale shell copy is retired and safe technical AKVPK slug
# migration is performed once the new akvpk theme package is installed.
# ---------------------------------------------------------------------------
theme_controller_path = PLUGIN / 'src' / 'Admin' / 'ThemeController.php'
theme_controller = read(theme_controller_path)
theme_controller = replace_once(
    theme_controller,
    "namespace Hangar18\\Clean\\Admin;\n\nfinal class ThemeController\n{\n",
    "namespace Hangar18\\Clean\\Admin;\n\nuse Hangar18\\Clean\\Frontend\\ThemeShell;\n\nfinal class ThemeController\n{\n    private const THEME_MIGRATION_OPTION = 'h18_vd_theme_slug_migration_v0150';\n",
    'ThemeController import/constant',
)
theme_controller = replace_once(
    theme_controller,
    "    public static function register(): void\n    {\n        add_action('admin_menu', [self::class, 'menu'], 9);\n    }\n",
    "    public static function register(): void\n    {\n        add_action('setup_theme', [self::class, 'maybeMigrateAkVpkTheme'], 0);\n        add_action('admin_menu', [self::class, 'menu'], 9);\n    }\n\n    public static function maybeMigrateAkVpkTheme(): void\n    {\n        if (get_stylesheet() !== 'hangar18-base' || get_option(self::THEME_MIGRATION_OPTION, false)) {\n            return;\n        }\n        $target = wp_get_theme('akvpk');\n        if (!$target->exists()) {\n            return;\n        }\n\n        $oldMods = get_option('theme_mods_hangar18-base', null);\n        if (is_array($oldMods) && get_option('theme_mods_akvpk', null) === null) {\n            update_option('theme_mods_akvpk', $oldMods, false);\n        }\n        if (function_exists('wp_get_custom_css') && function_exists('wp_update_custom_css_post')) {\n            $css = trim((string) wp_get_custom_css('hangar18-base'));\n            if ($css !== '' && trim((string) wp_get_custom_css('akvpk')) === '') {\n                wp_update_custom_css_post($css, ['stylesheet' => 'akvpk']);\n            }\n        }\n        if (!function_exists('switch_theme')) {\n            return;\n        }\n        switch_theme('akvpk');\n        update_option(self::THEME_MIGRATION_OPTION, [\n            'migratedUtc' => gmdate('c'),\n            'from' => 'hangar18-base',\n            'to' => 'akvpk',\n            'themeModsCopied' => is_array($oldMods),\n        ], false);\n    }\n",
    'ThemeController migration hook',
)
old_shell = """        echo '<section class=\"h18-manager-card h18-manager-module\"><h2>Shell integration</h2><p><strong>Status:</strong> Ikke overtaget endnu.</p><p>Den aktive offentlige theme-runtime ændres ikke af denne administrationsside. Først når Globalt design og Header/Footer-modellerne er QA-godkendt, kan temaet reduceres til en tynd shell med sikker fallback.</p></section>';
"""
new_shell = """        $shellActive = ThemeShell::enabled();
        echo '<section class=\"h18-manager-card h18-manager-module\"><h2>Shell integration</h2><p><strong>Status:</strong> <span class=\"h18-manager-badge ' . ($shellActive ? 'is-ok' : '') . '\">' . ($shellActive ? 'Aktiv' : 'Deaktiveret') . '</span></p>';
        echo '<p>Visual Designer Manager leverer live Header → side → Footer på Visual Designer-sider. Ikke-konverterede WordPress-sider beholder deres eksisterende indhold som sikker fallback.</p><p class=\"description\">AKVPK-temaet er den tynde WordPress-shell; global Header/Footer og side-layout kommer fra de canonical Visual Designer-modeller.</p></section>';
"""
theme_controller = replace_once(theme_controller, old_shell, new_shell, 'ThemeController shell status')
write(theme_controller_path, theme_controller)


# ---------------------------------------------------------------------------
# AKVPK theme 1.3.0. Keep legacy source as a rollback/reference; create a new
# technical theme root named akvpk, so WordPress Stylesheet/Template become akvpk.
# The manifest intentionally keeps theme=hangar18-base for this one migration
# release so existing 1.2.2 installations can discover the update.
# ---------------------------------------------------------------------------
legacy_theme = ROOT / 'theme' / 'legacy-v1.2.0'
akvpk_theme = ROOT / 'theme' / 'akvpk'
if akvpk_theme.exists():
    shutil.rmtree(akvpk_theme)
shutil.copytree(legacy_theme, akvpk_theme)

style_path = akvpk_theme / 'style.css'
style = read(style_path)
style = replace_once(style, 'Theme URI: https://hangar18.dk/', 'Theme URI: https://akvpk.dk/', 'AKVPK Theme URI')
style = replace_once(style, 'Author: AKVPK\n', 'Author: AKVPK\nAuthor URI: https://akvpk.dk/\n', 'AKVPK Author URI')
style = replace_once(style, 'Version: 1.2.2', 'Version: 1.3.0', 'AKVPK theme version')
style = replace_once(style, 'Text Domain: hangar18-base', 'Text Domain: akvpk', 'AKVPK text domain')
write(style_path, style)

functions_path = akvpk_theme / 'functions.php'
functions = read(functions_path)
functions = replace_once(functions, "const H18_BASE_THEME_VERSION = '1.2.2';", "const H18_BASE_THEME_VERSION = '1.3.0';", 'AKVPK runtime version')
functions = replace_once(functions, "'primary' => __('Hangar18 primærmenu', 'hangar18-base'),", "'primary' => __('AKVPK primærmenu', 'akvpk'),", 'AKVPK menu label')
functions = replace_once(functions, "'user-agent' => 'Hangar18-Base-Theme/' . H18_BASE_THEME_VERSION . '; ' . home_url('/'),", "'user-agent' => 'AKVPK-Theme/' . H18_BASE_THEME_VERSION . '; ' . home_url('/'),", 'AKVPK user agent')
functions = replace_once(functions, "$theme === 'hangar18-base' &&", "in_array($theme, ['hangar18-base', 'akvpk'], true) &&", 'AKVPK manifest legacy/current themes')
functions = replace_once(functions, "    if ($slug !== 'hangar18-base') {\n        return $transient;\n    }", "    if (!in_array($slug, ['hangar18-base', 'akvpk'], true)) {\n        return $transient;\n    }", 'AKVPK update slug')
functions = replace_once(functions, "    if (($args->slug ?? '') !== 'hangar18-base') {\n        return $result;\n    }", "    if (!in_array((string) ($args->slug ?? ''), ['hangar18-base', 'akvpk'], true)) {\n        return $result;\n    }", 'AKVPK theme information slug gate')
functions = replace_once(functions, "        'slug'          => 'hangar18-base',", "        'slug'          => 'akvpk',", 'AKVPK theme info slug')
functions = replace_once(functions, "        'author'        => '<a href=\"https://hangar18.dk/\">AKVPK</a>',", "        'author'        => '<a href=\"https://akvpk.dk/\">AKVPK</a>',", 'AKVPK author URL')
functions = functions.replace("__('Hangar18-temapakken", "__('AKVPK-temapakken")
functions = functions.replace("'hangar18-base'\n        )", "'akvpk'\n        )")
functions = functions.replace("wp_tempnam('hangar18-base-theme.zip')", "wp_tempnam('akvpk-theme.zip')")
functions = functions.replace('<strong>Hangar18 Base Theme:</strong>', '<strong>AKVPK:</strong>')
functions = functions.replace('Hangar18 Manager er ikke aktiv.', 'Visual Designer Manager er ikke aktiv.')
write(functions_path, functions)

manifest_path = ROOT / 'theme-update.json'
manifest = json.loads(read(manifest_path))
manifest.update({
    'schema_version': '1.1',
    'theme': 'hangar18-base',
    'target_theme': 'akvpk',
    'version': '1.3.0',
    'last_updated': '2026-08-29T12:20:00Z',
    'details_url': 'https://akvpk.dk/',
    'package_url': 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/main/dist/akvpk-theme.zip.b64',
    'package_encoding': 'base64',
    'package_sha256': '',
    'changelog': '<h4>AKVPK 1.3.0</h4><ul><li>Teknisk theme-slug/mappe ændres fra <code>hangar18-base</code> til <code>akvpk</code>.</li><li>Theme URI er <code>https://akvpk.dk/</code> og Text Domain er <code>akvpk</code>.</li><li>Visual Designer Manager 0.1.50 migrerer theme_mods, menu-locations og Custom CSS og skifter sikkert til den nye AKVPK-theme-slug, når temaet er installeret.</li><li>Det gamle theme kan blive liggende som rollback; det slettes ikke automatisk.</li></ul>',
})
write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


# ---------------------------------------------------------------------------
# Release metadata/docs.
# ---------------------------------------------------------------------------
history_path = PLUGIN / 'release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', [])
versions.insert(0, {
    'version': '0.1.50',
    'date': '2026-08-29',
    'items': [
        'Nyt hovedpunkt “Konvertering” viser alle WordPress-sider og deres migrationsstatus.',
        'Konvertér én, markerede eller alle ikke-konverterede sider til ikke-destruktive QA-kandidater.',
        'Kandidat-preview bruger canonical Renderer med aktiv Header/Footer; frontend ændres først ved “Godkend og aktivér”.',
        'Original post_content gemmes urørt og første snapshot bevares som konverteringskilde/fallback.',
        'Legacy Header/Footer-markører fjernes fra kandidatens body, fordi global Visual Designer-shell allerede er live.',
        'Tema/Shell-status er rettet til Aktiv.',
        'AKVPK 1.3.0 introducerer teknisk theme-slug akvpk og Theme URI https://akvpk.dk/ med sikker migration fra hangar18-base.',
    ],
})
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes_path = ROOT / 'clean-release-notes.html'
notes = read(notes_path)
notes = '<h4>0.1.50 – Sidekonvertering og AKVPK theme-migration</h4><ul><li>Nyt <strong>Konvertering</strong>-punkt med enkelt/batch forberedelse, QA-preview og separat godkendelse.</li><li>Konvertering er ikke-destruktiv: original post_content overskrives ikke, og batch aktiverer aldrig sider automatisk.</li><li>AKVPK theme 1.3.0 flytter den tekniske theme-identitet til <code>akvpk</code> og bruger <code>https://akvpk.dk/</code>.</li><li>Tema/Shell viser nu korrekt aktiv Visual Designer Header/Page/Footer-runtime.</li></ul>\n' + notes
write(notes_path, notes)

status_doc = '''# Visual Designer Manager 0.1.50 – status\n\n## Leveret\n- Nyt hovedpunkt **Konvertering**.\n- Enkelt, markeret og alle-ikke-konverterede kan forberedes som QA-kandidater.\n- Batch er staging-only; ingen automatisk live-cutover.\n- Preview bruger Header + kandidat + Footer via canonical Renderer.\n- Godkendelse opretter en ny LayoutModel-version og sætter Header/Footer til Auto.\n- Original WordPress `post_content` ændres ikke.\n- Legacy Header/Footer shell-markører fjernes fra kandidatens body.\n- Theme/Shell-admin viser aktiv shell korrekt.\n- AKVPK theme 1.3.0: Theme URI `https://akvpk.dk/`, teknisk slug `akvpk`, Text Domain `akvpk`.\n- Visual Designer Manager migrerer `theme_mods`, menu-locations og Custom CSS før switch fra `hangar18-base` til `akvpk`, når det nye theme er installeret.\n\n## QA-kontrakt\nDen automatiske converter er bevidst konservativ: eksisterende body-HTML bevares i første pass i en canonical Text-blok. Komplekse sider kan derfor kræve visuel efterbearbejdning/dekomponering i native Text/Image/Button/Kasse-elementer før de godkendes. Kandidaten må ikke ændre public frontend før eksplicit godkendelse.\n'''
write(ROOT / 'docs' / 'v0150-status.md', status_doc)

manual_path = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
manual = read(manual_path)
manual += '''\n\n## 0.1.50 – Sidekonvertering og AKVPK teknisk theme-identitet\n\n### VD-CONVERSION-STAGE-001\nKonvertering af en eksisterende WordPress-side skal være staging-only indtil eksplicit godkendelse. Original `post_content` overskrives ikke. Batch-konvertering må oprette kandidater, men må ikke aktivere dem.\n\n### VD-CONVERSION-SHELL-001\nLegacy Header/Footer-markører fjernes fra kandidatens body, fordi Visual Designer Header/Footer allerede leveres af den aktive globale shell. Kandidat-preview skal bruge samme canonical Renderer.\n\n### VD-THEME-AKVPK-001\nDet officielle WordPress-theme hedder og installeres teknisk som `akvpk`. Migration fra historisk `hangar18-base` skal bevare theme_mods/menu-locations og Custom CSS før theme-switch. Theme URI er `https://akvpk.dk/`.\n'''
write(manual_path, manual)

print('Visual Designer Manager 0.1.50 conversion/theme patch applied.')
