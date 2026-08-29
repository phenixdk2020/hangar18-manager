from __future__ import annotations

import json
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
# Visual Designer Manager 0.1.51
# ---------------------------------------------------------------------------
plugin_path = PLUGIN / 'hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, ' * Version: 0.1.50', ' * Version: 0.1.51', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.50');", "define('H18_CLEAN_VERSION', '0.1.51');", 'plugin constant version')
plugin = replace_once(
    plugin,
    "require_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Migration/ExternalPageSourceService.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';\n",
    'external source service require',
)
write(plugin_path, plugin)


# ---------------------------------------------------------------------------
# External source fetch/extract service.
# ---------------------------------------------------------------------------
external_service = r'''<?php

declare(strict_types=1);

namespace Hangar18\Clean\Migration;

/**
 * Read-only importer for public HTTPS pages.
 *
 * The service never mutates the source site. It returns a sanitized body
 * snapshot that PageConversionService can stage as a QA candidate.
 */
final class ExternalPageSourceService
{
    private const MAX_RESPONSE_BYTES = 2097152;

    /** @return array<string,mixed> */
    public static function fetch(string $url): array
    {
        $requestedUrl = self::validatedUrl($url);
        $response = wp_safe_remote_get($requestedUrl, [
            'timeout' => 20,
            'redirection' => 3,
            'reject_unsafe_urls' => true,
            'limit_response_size' => self::MAX_RESPONSE_BYTES,
            'user-agent' => 'Visual-Designer-Manager/0.1.51; ' . home_url('/'),
            'headers' => [
                'Accept' => 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.1',
            ],
        ]);
        if (is_wp_error($response)) {
            throw new \RuntimeException('Kildesiden kunne ikke hentes: ' . $response->get_error_message());
        }

        $code = (int) wp_remote_retrieve_response_code($response);
        if ($code < 200 || $code >= 300) {
            throw new \RuntimeException('Kildesiden svarede med HTTP ' . $code . '.');
        }
        $contentType = strtolower((string) wp_remote_retrieve_header($response, 'content-type'));
        if ($contentType !== '' && strpos($contentType, 'text/html') === false && strpos($contentType, 'application/xhtml+xml') === false) {
            throw new \RuntimeException('Kilde-URL peger ikke på en HTML-side.');
        }

        $raw = (string) wp_remote_retrieve_body($response);
        if (trim($raw) === '') {
            throw new \RuntimeException('Kildesiden returnerede tom HTML.');
        }
        if (strlen($raw) >= self::MAX_RESPONSE_BYTES) {
            throw new \RuntimeException('Kildesiden er større end 2 MB og importen blev stoppet.');
        }

        $parsed = self::extract($raw, $requestedUrl);
        $html = trim(wp_kses_post((string) ($parsed['html'] ?? '')));
        if ($html === '') {
            throw new \RuntimeException('Der blev ikke fundet brugbart sideindhold på kildesiden.');
        }

        $warnings = isset($parsed['warnings']) && is_array($parsed['warnings']) ? $parsed['warnings'] : [];
        $warnings[] = 'external-source-read-only';
        $warnings[] = 'visual-parity-requires-qa';

        return [
            'sourceType' => 'external',
            'url' => $requestedUrl,
            'title' => sanitize_text_field((string) ($parsed['title'] ?? '')),
            'html' => $html,
            'hash' => hash('sha256', $html),
            'rawLength' => strlen($raw),
            'bodyLength' => strlen($html),
            'imageCount' => max(0, (int) ($parsed['imageCount'] ?? 0)),
            'linkCount' => max(0, (int) ($parsed['linkCount'] ?? 0)),
            'warnings' => array_values(array_unique(array_map('sanitize_text_field', $warnings))),
            'capturedUtc' => gmdate('c'),
        ];
    }

    private static function validatedUrl(string $url): string
    {
        $url = trim($url);
        $clean = esc_url_raw($url, ['https']);
        if ($clean === '' || strtolower((string) wp_parse_url($clean, PHP_URL_SCHEME)) !== 'https') {
            throw new \InvalidArgumentException('Kilde-URL skal være en gyldig HTTPS-adresse.');
        }
        $host = strtolower((string) wp_parse_url($clean, PHP_URL_HOST));
        if ($host === '' || $host === 'localhost' || filter_var($host, FILTER_VALIDATE_IP)) {
            throw new \InvalidArgumentException('Kilde-URL skal pege på et offentligt hostnavn.');
        }
        if (function_exists('wp_http_validate_url') && !wp_http_validate_url($clean)) {
            throw new \InvalidArgumentException('Kilde-URL blev afvist af WordPress sikkerhedsvalidering.');
        }
        return $clean;
    }

    /** @return array<string,mixed> */
    private static function extract(string $raw, string $baseUrl): array
    {
        if (!class_exists('DOMDocument')) {
            return self::extractFallback($raw, $baseUrl);
        }

        $previous = libxml_use_internal_errors(true);
        $dom = new \DOMDocument('1.0', 'UTF-8');
        $loaded = $dom->loadHTML('<?xml encoding="utf-8" ?>' . $raw, LIBXML_NONET | LIBXML_NOERROR | LIBXML_NOWARNING);
        libxml_clear_errors();
        libxml_use_internal_errors($previous);
        if (!$loaded) {
            return self::extractFallback($raw, $baseUrl);
        }

        $xpath = new \DOMXPath($dom);
        $title = '';
        foreach (['//main//h1[1]', '//article//h1[1]', '//h1[1]', '//title[1]'] as $query) {
            $nodes = $xpath->query($query);
            if ($nodes && $nodes->length > 0) {
                $title = trim((string) $nodes->item(0)->textContent);
                if ($title !== '') { break; }
            }
        }

        $root = null;
        foreach ([
            '//main[1]',
            '//article[1]',
            '//*[contains(concat(" ", normalize-space(@class), " "), " entry-content ")][1]',
            '//*[@id="content"][1]',
            '//body[1]',
        ] as $query) {
            $nodes = $xpath->query($query);
            if ($nodes && $nodes->length > 0) {
                $root = $nodes->item(0);
                break;
            }
        }
        if (!$root instanceof \DOMNode) {
            return self::extractFallback($raw, $baseUrl);
        }

        foreach (['script', 'style', 'noscript', 'template'] as $tag) {
            $nodes = $xpath->query('.//' . $tag, $root);
            if (!$nodes) { continue; }
            $remove = [];
            foreach ($nodes as $node) { $remove[] = $node; }
            foreach ($remove as $node) {
                if ($node->parentNode) { $node->parentNode->removeChild($node); }
            }
        }
        if (strtolower((string) $root->nodeName) === 'body') {
            foreach (['header', 'footer', 'nav'] as $tag) {
                $nodes = $xpath->query('.//' . $tag, $root);
                if (!$nodes) { continue; }
                $remove = [];
                foreach ($nodes as $node) { $remove[] = $node; }
                foreach ($remove as $node) {
                    if ($node->parentNode) { $node->parentNode->removeChild($node); }
                }
            }
        }

        $imageCount = 0;
        $linkCount = 0;
        $formCount = 0;
        $sourceHost = strtolower((string) wp_parse_url($baseUrl, PHP_URL_HOST));
        $internalSourceLinks = 0;

        $all = $xpath->query('.//*', $root);
        if ($all) {
            foreach ($all as $node) {
                if (!$node instanceof \DOMElement) { continue; }
                $tag = strtolower($node->tagName);
                if ($tag === 'img') { $imageCount++; }
                if ($tag === 'a') { $linkCount++; }
                if ($tag === 'form') { $formCount++; }

                foreach (['href', 'src', 'poster'] as $attribute) {
                    if (!$node->hasAttribute($attribute)) { continue; }
                    $value = trim($node->getAttribute($attribute));
                    $absolute = self::absoluteUrl($baseUrl, $value);
                    if ($absolute === '') {
                        $node->removeAttribute($attribute);
                    } else {
                        $node->setAttribute($attribute, $absolute);
                        if ($tag === 'a' && $attribute === 'href' && strtolower((string) wp_parse_url($absolute, PHP_URL_HOST)) === $sourceHost) {
                            $internalSourceLinks++;
                        }
                    }
                }
                if ($node->hasAttribute('srcset')) {
                    $node->setAttribute('srcset', self::absoluteSrcset($baseUrl, $node->getAttribute('srcset')));
                }
                foreach (['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus'] as $unsafeAttribute) {
                    if ($node->hasAttribute($unsafeAttribute)) { $node->removeAttribute($unsafeAttribute); }
                }
            }
        }

        $html = '';
        foreach ($root->childNodes as $child) {
            $part = $dom->saveHTML($child);
            if (is_string($part)) { $html .= $part; }
        }

        $warnings = [];
        if (stripos($raw, '<script') !== false) { $warnings[] = 'external-scripts-not-imported'; }
        if (stripos($raw, '<style') !== false || stripos($raw, 'rel="stylesheet"') !== false || stripos($raw, "rel='stylesheet'") !== false) {
            $warnings[] = 'external-stylesheets-not-imported';
        }
        if ($imageCount > 0) { $warnings[] = 'external-images-remain-source-linked'; }
        if ($internalSourceLinks > 0) { $warnings[] = 'external-internal-links-remain-source-linked'; }
        if ($formCount > 0) { $warnings[] = 'external-forms-require-manual-qa'; }

        return [
            'title' => $title,
            'html' => $html,
            'imageCount' => $imageCount,
            'linkCount' => $linkCount,
            'warnings' => $warnings,
        ];
    }

    /** @return array<string,mixed> */
    private static function extractFallback(string $raw, string $baseUrl): array
    {
        $body = $raw;
        if (preg_match('/<main\b[^>]*>(.*?)<\/main>/is', $raw, $match)) {
            $body = (string) $match[1];
        } elseif (preg_match('/<body\b[^>]*>(.*?)<\/body>/is', $raw, $match)) {
            $body = (string) $match[1];
        }
        $body = preg_replace('/<(script|style|noscript|template)\b[^>]*>.*?<\/\1>/is', '', $body) ?: $body;
        $title = '';
        if (preg_match('/<h1\b[^>]*>(.*?)<\/h1>/is', $body, $match)) {
            $title = trim(wp_strip_all_tags((string) $match[1]));
        } elseif (preg_match('/<title\b[^>]*>(.*?)<\/title>/is', $raw, $match)) {
            $title = trim(wp_strip_all_tags((string) $match[1]));
        }
        return [
            'title' => $title,
            'html' => $body,
            'imageCount' => substr_count(strtolower($body), '<img'),
            'linkCount' => substr_count(strtolower($body), '<a'),
            'warnings' => ['dom-extension-unavailable-relative-links-require-qa'],
        ];
    }

    private static function absoluteUrl(string $baseUrl, string $value): string
    {
        $value = trim(html_entity_decode($value, ENT_QUOTES | ENT_HTML5, 'UTF-8'));
        if ($value === '') { return ''; }
        $lower = strtolower($value);
        if (str_starts_with($lower, 'javascript:') || str_starts_with($lower, 'vbscript:')) { return ''; }
        if ($value[0] === '#' || str_starts_with($lower, 'mailto:') || str_starts_with($lower, 'tel:') || str_starts_with($lower, 'data:')) {
            return $value;
        }
        if (preg_match('#^https?://#i', $value)) { return esc_url_raw($value); }

        $scheme = strtolower((string) wp_parse_url($baseUrl, PHP_URL_SCHEME));
        $host = (string) wp_parse_url($baseUrl, PHP_URL_HOST);
        $port = wp_parse_url($baseUrl, PHP_URL_PORT);
        $origin = $scheme . '://' . $host . ($port ? ':' . (int) $port : '');
        if (str_starts_with($value, '//')) { return esc_url_raw($scheme . ':' . $value); }
        if (str_starts_with($value, '/')) { return esc_url_raw($origin . $value); }

        $path = (string) wp_parse_url($baseUrl, PHP_URL_PATH);
        $directory = preg_replace('#/[^/]*$#', '/', $path);
        if (!is_string($directory) || $directory === '') { $directory = '/'; }
        $combined = $directory . $value;
        $segments = [];
        foreach (explode('/', $combined) as $segment) {
            if ($segment === '' || $segment === '.') { continue; }
            if ($segment === '..') { array_pop($segments); continue; }
            $segments[] = $segment;
        }
        return esc_url_raw($origin . '/' . implode('/', $segments));
    }

    private static function absoluteSrcset(string $baseUrl, string $srcset): string
    {
        $result = [];
        foreach (explode(',', $srcset) as $candidate) {
            $candidate = trim($candidate);
            if ($candidate === '') { continue; }
            $parts = preg_split('/\s+/', $candidate, 2);
            $url = self::absoluteUrl($baseUrl, (string) ($parts[0] ?? ''));
            if ($url === '') { continue; }
            $descriptor = isset($parts[1]) ? trim((string) $parts[1]) : '';
            $result[] = $url . ($descriptor !== '' ? ' ' . $descriptor : '');
        }
        return implode(', ', $result);
    }

    private function __construct()
    {
    }
}
'''
write(PLUGIN / 'src' / 'Migration' / 'ExternalPageSourceService.php', external_service)


# ---------------------------------------------------------------------------
# PageConversionService: source type/URL, external staging and approval gate.
# ---------------------------------------------------------------------------
service_path = PLUGIN / 'src' / 'Migration' / 'PageConversionService.php'
service = read(service_path)
service = replace_once(
    service,
    "        $state = is_array($state) ? $state : [];\n        $post = get_post($postId);\n        $currentHash = $post instanceof \\WP_Post ? hash('sha256', (string) $post->post_content) : '';\n        $sourceHash = sanitize_text_field((string) ($state['sourceHash'] ?? ''));\n",
    "        $state = is_array($state) ? $state : [];\n        $sourceType = sanitize_key((string) ($state['sourceType'] ?? 'local'));\n        $sourceUrl = esc_url_raw((string) ($state['sourceUrl'] ?? ''));\n        $post = get_post($postId);\n        $currentHash = $post instanceof \\WP_Post ? hash('sha256', (string) $post->post_content) : '';\n        $sourceHash = sanitize_text_field((string) ($state['sourceHash'] ?? ''));\n        $sourceChanged = $sourceType !== 'external' && $sourceHash !== '' && $currentHash !== '' && !hash_equals($sourceHash, $currentHash);\n",
    'status source metadata',
)
service = replace_once(
    service,
    "            'sourceHash' => $sourceHash,\n            'sourceChanged' => $sourceHash !== '' && $currentHash !== '' && !hash_equals($sourceHash, $currentHash),\n",
    "            'sourceHash' => $sourceHash,\n            'sourceType' => $sourceType,\n            'sourceUrl' => $sourceUrl,\n            'sourceTitle' => sanitize_text_field((string) ($state['sourceTitle'] ?? '')),\n            'sourceChanged' => $sourceChanged,\n",
    'status return source metadata',
)
service = replace_once(
    service,
    "            'postContent' => $source,\n            ]);\n",
    "            'postContent' => $source,\n                'sourceType' => 'local',\n            ]);\n",
    'local source snapshot marker',
)
service = replace_once(
    service,
    "            'status' => 'review',\n            'preparedUtc' => gmdate('c'),\n            'preparedBy' => max(0, $userId),\n            'sourceHash' => $sourceHash,\n",
    "            'status' => 'review',\n            'preparedUtc' => gmdate('c'),\n            'preparedBy' => max(0, $userId),\n            'sourceType' => 'local',\n            'sourceUrl' => '',\n            'sourceTitle' => (string) $post->post_title,\n            'sourceHash' => $sourceHash,\n",
    'local candidate source state',
)
insert_after_prepare = r'''
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
        $model = self::modelFromHtml($postId, $html);
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
'''
needle = "        return self::status($postId);\n    }\n\n    /** @return array<string,mixed>|null */\n    public static function candidate(int $postId): ?array\n"
service = replace_once(
    service,
    needle,
    "        return self::status($postId);\n    }\n" + insert_after_prepare + "\n    /** @return array<string,mixed>|null */\n    public static function candidate(int $postId): ?array\n",
    'insert external prepare methods',
)
old_approval_guard = r'''        $state = get_post_meta($postId, self::STATE_META, true);
        $sourceHash = is_array($state) ? sanitize_text_field((string) ($state['sourceHash'] ?? '')) : '';
        $post = get_post($postId);
        if ($post instanceof \WP_Post && $sourceHash !== '' && !hash_equals($sourceHash, hash('sha256', (string) $post->post_content))) {
            throw new \RuntimeException('Kildesiden er ændret efter konverteringen. Konvertér siden igen før godkendelse.');
        }

        $version = LayoutModel::saveVersion($postId, $candidate, $userId, 'Godkendt sidekonvertering v0.1.50 · original post_content bevaret');
'''
new_approval_guard = r'''        $state = get_post_meta($postId, self::STATE_META, true);
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
            ? 'Godkendt ekstern sidekonvertering v0.1.51 · kilde ' . $sourceUrl
            : 'Godkendt lokal sidekonvertering v0.1.51 · original post_content bevaret';
        $version = LayoutModel::saveVersion($postId, $candidate, $userId, $note);
'''
service = replace_once(service, old_approval_guard, new_approval_guard, 'external approval gate')
service = replace_once(
    service,
    "            'approvedBy' => max(0, $userId),\n            'sourceHash' => $sourceHash,\n            'version' => $version,\n            'warnings' => is_array($state) && isset($state['warnings']) && is_array($state['warnings']) ? $state['warnings'] : [],\n",
    "            'approvedBy' => max(0, $userId),\n            'sourceType' => $sourceType,\n            'sourceUrl' => $sourceUrl,\n            'sourceTitle' => sanitize_text_field((string) ($state['sourceTitle'] ?? '')),\n            'sourceHash' => $sourceHash,\n            'version' => $version,\n            'warnings' => isset($state['warnings']) && is_array($state['warnings']) ? $state['warnings'] : [],\n",
    'approved external metadata',
)
write(service_path, service)


# ---------------------------------------------------------------------------
# ConversionController: external URL -> existing/new local target.
# ---------------------------------------------------------------------------
controller_path = PLUGIN / 'src' / 'Admin' / 'ConversionController.php'
controller = read(controller_path)
controller = replace_once(
    controller,
    "use Hangar18\\Clean\\Migration\\PageConversionService;\n",
    "use Hangar18\\Clean\\Migration\\ExternalPageSourceService;\nuse Hangar18\\Clean\\Migration\\PageConversionService;\n",
    'controller external import',
)
controller = replace_once(
    controller,
    "    private const PREPARE_ACTION = 'h18_vd_conversion_prepare_v0150';\n",
    "    private const PREPARE_ACTION = 'h18_vd_conversion_prepare_v0150';\n    private const EXTERNAL_PREPARE_ACTION = 'h18_vd_conversion_external_prepare_v0151';\n",
    'external action constant',
)
controller = replace_once(
    controller,
    "        add_action('admin_post_' . self::PREPARE_ACTION, [self::class, 'prepare']);\n",
    "        add_action('admin_post_' . self::PREPARE_ACTION, [self::class, 'prepare']);\n        add_action('admin_post_' . self::EXTERNAL_PREPARE_ACTION, [self::class, 'externalPrepare']);\n",
    'external action register',
)
external_card = r'''
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
        echo '<p class="description">Til forsiden: brug <code>https://test2.hangar18.dk/</code> og vælg <strong>Hjem – Visual Designer</strong> som målside. Relative billeder og links gøres absolutte mod kildesitet; eksterne assets flyttes ikke til det nye mediebibliotek i denne version.</p></section>';
'''
controller = replace_once(
    controller,
    "        echo '<section class=\"h18-manager-card\"><h2>Sikker arbejdsgang</h2><ol class=\"h18-manager-list\"><li><strong>Konvertér</strong> opretter en kandidat og gemmer et snapshot af den oprindelige side.</li><li><strong>Forhåndsvis</strong> viser kandidat + aktiv Header/Footer uden at ændre frontend.</li><li><strong>Godkend og aktivér</strong> opretter en ny Visual Designer-version. Original <code>post_content</code> overskrives ikke.</li></ol><p class=\"description\">Første automatiske pass bevarer eksisterende body-HTML i en canonical Text-blok. Det giver en sikker indholdsmigrering, men komplekse legacy-layouts kan stadig kræve visuel QA og efterfølgende opdeling i rigtige Text/Image/Button/Kasse-elementer.</p></section>';\n",
    "        echo '<section class=\"h18-manager-card\"><h2>Sikker arbejdsgang</h2><ol class=\"h18-manager-list\"><li><strong>Konvertér</strong> eller <strong>Hent ekstern side</strong> opretter kun en kandidat.</li><li><strong>Forhåndsvis</strong> viser kandidat + aktiv Header/Footer uden at ændre frontend.</li><li><strong>Godkend og aktivér</strong> opretter en ny Visual Designer-version. Lokal <code>post_content</code> overskrives ikke.</li></ol><p class=\"description\">Første automatiske pass bevarer body-HTML i en canonical Text-blok. Komplekse layouts kræver fortsat visuel QA og kan bagefter opdeles i rigtige Text/Image/Button/Kasse-elementer.</p></section>';\n" + external_card,
    'external source UI card',
)
controller = replace_once(
    controller,
    "            echo '<td>' . ($warnings ? '<small>' . esc_html(implode(' · ', array_unique(array_map('strval', $warnings)))) . '</small>' : '<span class=\"description\">—</span>') . '</td>';\n",
    "            $sourceInfo = (string) ($state['sourceType'] ?? 'local') === 'external' && !empty($state['sourceUrl'])\n                ? '<br><small>Kilde: <code>' . esc_html((string) $state['sourceUrl']) . '</code></small>'\n                : '';\n            echo '<td>' . ($warnings ? '<small>' . esc_html(implode(' · ', array_unique(array_map('strval', $warnings)))) . '</small>' : '<span class=\"description\">—</span>') . $sourceInfo . '</td>';\n",
    'row external source info',
)
external_handler = r'''
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

'''
controller = replace_once(
    controller,
    "    public static function prepare(): void\n    {\n",
    external_handler + "    public static function prepare(): void\n    {\n",
    'external prepare handler',
)
write(controller_path, controller)


# ---------------------------------------------------------------------------
# Theme migration timing repair: setup_theme already fired before plugins_loaded.
# ---------------------------------------------------------------------------
theme_controller_path = PLUGIN / 'src' / 'Admin' / 'ThemeController.php'
theme_controller = read(theme_controller_path)
theme_controller = replace_once(
    theme_controller,
    "        add_action('setup_theme', [self::class, 'maybeMigrateAkVpkTheme'], 0);\n        add_action('admin_menu', [self::class, 'menu'], 9);\n",
    "        add_action('admin_init', [self::class, 'maybeMigrateAkVpkTheme'], 1);\n        add_action('admin_menu', [self::class, 'menu'], 9);\n",
    'theme migration hook timing',
)
theme_controller = replace_once(
    theme_controller,
    "    public static function maybeMigrateAkVpkTheme(): void\n    {\n        if (get_stylesheet() !== 'hangar18-base' || get_option(self::THEME_MIGRATION_OPTION, false)) {\n",
    "    public static function maybeMigrateAkVpkTheme(): void\n    {\n        if (!current_user_can('switch_themes')) { return; }\n        if (get_stylesheet() !== 'hangar18-base' || get_option(self::THEME_MIGRATION_OPTION, false)) {\n",
    'theme migration capability gate',
)
write(theme_controller_path, theme_controller)


# ---------------------------------------------------------------------------
# Release history and status documentation.
# ---------------------------------------------------------------------------
history_path = PLUGIN / 'release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', [])
versions = [row for row in versions if str(row.get('version', '')) != '0.1.51']
versions.insert(0, {
    'version': '0.1.51',
    'date': '2026-08-29',
    'items': [
        'Konvertering kan nu hente en offentlig HTTPS-side som read-only ekstern kilde og stage den som QA-kandidat på en eksisterende eller ny WordPress-side.',
        'Hjem kan hentes fra https://test2.hangar18.dk/ og lægges på Hjem – Visual Designer uden at ændre test2 eller live frontend før godkendelse.',
        'Ekstern HTML renses for scripts/styles, relative links/billeder gøres absolutte, og kildehash kontrolleres igen ved Godkend og aktivér.',
        'Eksterne billeder forbliver kilde-linkede i denne version og markeres til QA; mediebiblioteks-lokalisering er et separat senere trin.',
        'Theme slug-migrationen hangar18-base → akvpk flyttes til admin_init, så den faktisk kan køre efter installation af AKVPK 1.3.0.',
    ],
})
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

status = '''# Visual Designer Manager 0.1.51 – status\n\n## Scope\n- CONV-02 ekstern sidekonvertering.\n- Første autoritative kilde: `https://test2.hangar18.dk/` for Hjem.\n- Eksisterende lokal konvertering fra 0.1.50 bevares.\n- AKVPK theme slug-migration timing repareres.\n\n## Kontrakter\n1. Ekstern kilde er read-only og skal være offentlig HTTPS.\n2. Import opretter kun en QA-kandidat; frontend ændres først ved eksplicit Godkend og aktivér.\n3. Lokal `post_content` overskrives aldrig af konverteringen.\n4. Scripts/styles fra ekstern side køres/importeres ikke. Relative links og billed-URL'er absolutgøres mod kilden.\n5. Ved godkendelse hentes kilden igen og source hash skal fortsat matche kandidaten.\n6. En ekstern URL kan målrettes en eksisterende side eller oprette en ny WordPress-kladde.\n7. Header/Footer-preview bruger fortsat de aktive canonical templates.\n\n## Begrænsning\n0.1.51 kopierer ikke eksterne billeder ind i målsiteets mediebibliotek. Kandidaten markerer dette som QA-warning. Første pass er fortsat HTML-bevarende og er ikke en automatisk semantisk opsplitning i alle Visual Designer-elementtyper.\n'''
write(ROOT / 'docs' / 'v0151-status.md', status)

print('Applied Visual Designer Manager 0.1.51 external conversion patch')
