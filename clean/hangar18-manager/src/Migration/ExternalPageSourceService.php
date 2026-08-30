<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

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
            'user-agent' => 'Visual-Designer-Manager/0.1.52; ' . home_url('/'),
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
            '//*[contains(concat(" ", normalize-space(@class), " "), " h18-page-frame ")][1]',
            '//*[contains(concat(" ", normalize-space(@class), " "), " entry-content ")][1]',
            '//main[1]',
            '//article[1]',
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
        // Header/Footer/Menu are global Visual Designer models. They must never
        // become page nodes, regardless of which content root was selected.
        foreach (['header', 'footer', 'nav'] as $tag) {
            $nodes = $xpath->query('.//' . $tag, $root);
            if (!$nodes) { continue; }
            $remove = [];
            foreach ($nodes as $node) { $remove[] = $node; }
            foreach ($remove as $node) {
                if ($node->parentNode) { $node->parentNode->removeChild($node); }
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
        if (preg_match('/<!--\s*HANGAR18-PAGE-FRAME-START\s*-->(.*?)<!--\s*HANGAR18-PAGE-FRAME-END\s*-->/is', $raw, $match)) {
            $body = (string) $match[1];
        } elseif (preg_match('/<main\b[^>]*>(.*?)<\/main>/is', $raw, $match)) {
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
