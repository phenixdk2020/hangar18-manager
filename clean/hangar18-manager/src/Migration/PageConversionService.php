<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Frontend\Renderer;
use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;

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
        $sourceType = sanitize_key((string) ($state['sourceType'] ?? 'local'));
        $sourceUrl = esc_url_raw((string) ($state['sourceUrl'] ?? ''));
        $post = get_post($postId);
        $currentHash = $post instanceof \WP_Post ? hash('sha256', (string) $post->post_content) : '';
        $sourceHash = sanitize_text_field((string) ($state['sourceHash'] ?? ''));
        $sourceChanged = $sourceType !== 'external' && $sourceHash !== '' && $currentHash !== '' && !hash_equals($sourceHash, $currentHash);

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
            'sourceType' => $sourceType,
            'sourceUrl' => $sourceUrl,
            'sourceTitle' => sanitize_text_field((string) ($state['sourceTitle'] ?? '')),
            'sourceChanged' => $sourceChanged,
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
                'sourceType' => 'local',
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
            'sourceType' => 'local',
            'sourceUrl' => '',
            'sourceTitle' => (string) $post->post_title,
            'sourceHash' => $sourceHash,
            'sourceLength' => strlen($source),
            'bodyLength' => strlen($body),
            'candidateDigest' => $digest,
            'warnings' => $warnings,
        ]);

        return self::status($postId);
    }

    /** @return array<string,mixed> */
    public static function prepareExternal(int $postId, string $url, int $userId): array
    {
        return self::prepareExternalData($postId, ExternalPageSourceService::fetch($url), $userId);
    }

    /**
     * @param array<string,mixed> $sourceData
     * @return array<string,mixed>
     */
    public static function prepareExternalData(int $postId, array $sourceData, int $userId): array
    {
        $post = get_post($postId);
        if (!$post instanceof \WP_Post || $post->post_type !== 'page') {
            throw new \InvalidArgumentException('Kun WordPress-sider kan bruges som mål for ekstern konvertering.');
        }

        $sourceUrl = esc_url_raw((string) ($sourceData['url'] ?? ''));
        $html = trim((string) ($sourceData['html'] ?? ''));
        $sourceHash = sanitize_text_field((string) ($sourceData['hash'] ?? ''));
        if ($sourceUrl === '' || $html === '' || !preg_match('/^[a-f0-9]{64}$/', $sourceHash)) {
            throw new \RuntimeException('Den eksterne kildesnapshot er ugyldig.');
        }
        if (!hash_equals($sourceHash, hash('sha256', $html))) {
            throw new \RuntimeException('Kildesnapshotets kontrolsum passer ikke.');
        }

        $warnings = isset($sourceData['warnings']) && is_array($sourceData['warnings'])
            ? array_values(array_unique(array_map('sanitize_text_field', $sourceData['warnings'])))
            : [];
        $sourceTitle = sanitize_text_field((string) ($sourceData['title'] ?? ''));
        $model = VisualBlockConversionService::build($postId, $html, $warnings);
        if ($model === null) {
            $warnings[] = 'visual-block-conversion-fallback-to-single-text';
            $model = self::modelFromHtml($postId, $html);
        }
        $warnings = array_values(array_unique(array_map('sanitize_text_field', $warnings)));
        $digest = LayoutModel::structuralDigest($model);

        update_post_meta($postId, self::SOURCE_META, [
            'capturedUtc' => sanitize_text_field((string) ($sourceData['capturedUtc'] ?? gmdate('c'))),
            'sourceType' => 'external',
            'sourceUrl' => $sourceUrl,
            'sourceHash' => $sourceHash,
            'sourceTitle' => $sourceTitle,
            'sourceHtml' => $html,
            'rawLength' => max(0, (int) ($sourceData['rawLength'] ?? 0)),
            'bodyLength' => strlen($html),
        ]);
        update_post_meta($postId, self::CANDIDATE_META, $model);
        update_post_meta($postId, self::STATE_META, [
            'status' => 'review',
            'preparedUtc' => gmdate('c'),
            'preparedBy' => max(0, $userId),
            'sourceType' => 'external',
            'sourceUrl' => $sourceUrl,
            'sourceTitle' => $sourceTitle,
            'sourceHash' => $sourceHash,
            'sourceLength' => max(0, (int) ($sourceData['rawLength'] ?? 0)),
            'bodyLength' => strlen($html),
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
        $state = is_array($state) ? $state : [];
        $sourceHash = sanitize_text_field((string) ($state['sourceHash'] ?? ''));
        $sourceType = sanitize_key((string) ($state['sourceType'] ?? 'local'));
        $sourceUrl = esc_url_raw((string) ($state['sourceUrl'] ?? ''));
        $post = get_post($postId);
        if ($sourceType === 'external') {
            if ($sourceUrl === '' || $sourceHash === '') {
                throw new \RuntimeException('Ekstern kildeinformation mangler. Konvertér siden igen.');
            }
            $latest = ExternalPageSourceService::fetch($sourceUrl);
            $latestHash = sanitize_text_field((string) ($latest['hash'] ?? ''));
            if ($latestHash === '' || !hash_equals($sourceHash, $latestHash)) {
                throw new \RuntimeException('Den eksterne kildeside er ændret siden kandidaten blev lavet. Hent kilden igen før godkendelse.');
            }
        } elseif ($post instanceof \WP_Post && $sourceHash !== '' && !hash_equals($sourceHash, hash('sha256', (string) $post->post_content))) {
            throw new \RuntimeException('Kildesiden er ændret efter konverteringen. Konvertér siden igen før godkendelse.');
        }

        $note = $sourceType === 'external'
            ? 'Godkendt ekstern visuel sidekonvertering v0.1.52 · kilde ' . $sourceUrl
            : 'Godkendt lokal sidekonvertering v0.1.52 · original post_content bevaret';
        $version = LayoutModel::saveVersion($postId, $candidate, $userId, $note);
        TemplateLayoutModel::ensureMigrated();
        TemplateLayoutModel::setPageChoice($postId, 'header', 'auto');
        TemplateLayoutModel::setPageChoice($postId, 'footer', 'auto');
        delete_post_meta($postId, self::CANDIDATE_META);
        update_post_meta($postId, self::STATE_META, [
            'status' => 'active',
            'approvedUtc' => gmdate('c'),
            'approvedBy' => max(0, $userId),
            'sourceType' => $sourceType,
            'sourceUrl' => $sourceUrl,
            'sourceTitle' => sanitize_text_field((string) ($state['sourceTitle'] ?? '')),
            'sourceHash' => $sourceHash,
            'version' => $version,
            'warnings' => isset($state['warnings']) && is_array($state['warnings']) ? $state['warnings'] : [],
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
