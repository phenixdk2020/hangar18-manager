<?php

declare(strict_types=1);

namespace Hangar18\Clean\Diagnostics;

use Hangar18\Clean\Model\LayoutModel;

final class DiagnosticStore
{
    private const META = '_h18_clean_diagnostics_v1';
    private const TOKEN_OPTION = 'h18_clean_diagnostics_token_v1';
    private const MAX_ENTRIES = 600;
    private const REST_NS = 'hangar18-clean/v1';
    private const REST_ROUTE = '/diagnostics/(?P<token>[a-fA-F0-9]{64})';

    public static function register(): void
    {
        add_action('rest_api_init', [self::class, 'registerRoute']);
        add_action('wp_ajax_h18_clean_diag_append', [self::class, 'ajaxAppend']);
    }

    /** @param array<string,mixed> $detail */
    public static function append(int $postId, string $type, array $detail): void
    {
        if ($postId <= 0) {
            return;
        }
        $entries = self::entries($postId);
        $entries[] = [
            'time' => gmdate('c'),
            'type' => sanitize_key($type),
            'userId' => get_current_user_id(),
            'detail' => self::sanitizeValue($detail, '', 0),
        ];
        if (count($entries) > self::MAX_ENTRIES) {
            $entries = array_slice($entries, -self::MAX_ENTRIES);
        }
        update_post_meta($postId, self::META, $entries);
    }

    /** @return array<int,array<string,mixed>> */
    public static function entries(int $postId): array
    {
        if ($postId <= 0) {
            return [];
        }
        $entries = get_post_meta($postId, self::META, true);
        return is_array($entries) ? array_values(array_filter($entries, 'is_array')) : [];
    }

    public static function clear(int $postId): void
    {
        if ($postId > 0) {
            delete_post_meta($postId, self::META);
        }
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    public static function modelSummary(array $model): array
    {
        $normalized = LayoutModel::normalize($model);
        $nodes = [];
        foreach ($normalized['nodes'] as $node) {
            $row = [
                'id' => $node['id'],
                'type' => $node['type'],
                'parentId' => $node['parentId'],
                'order' => $node['order'],
                'geometry' => $node['geometry'],
            ];
            if ($node['type'] === 'image') {
                $row['image'] = [
                    'mediaId' => (int) ($node['props']['mediaId'] ?? 0),
                    'fit' => (string) ($node['props']['fit'] ?? 'cover'),
                    'focalX' => (int) ($node['props']['focalX'] ?? 50),
                    'focalY' => (int) ($node['props']['focalY'] ?? 50),
                ];
            }
            $nodes[] = $row;
        }
        return [
            'digest' => LayoutModel::structuralDigest($normalized),
            'nodeCount' => count($nodes),
            'nodes' => $nodes,
        ];
    }

    public static function ajaxAppend(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Forbidden'], 403);
        }
        check_ajax_referer('h18_clean_diag_append', 'nonce');
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            wp_send_json_error(['message' => 'Invalid page'], 400);
        }
        $type = sanitize_key((string) wp_unslash($_POST['event_type'] ?? 'client'));
        $raw = isset($_POST['detail_json']) ? (string) wp_unslash($_POST['detail_json']) : '';
        $decoded = $raw !== '' ? json_decode($raw, true) : [];
        self::append($postId, $type, is_array($decoded) ? $decoded : []);
        wp_send_json_success(['stored' => true]);
    }

    public static function registerRoute(): void
    {
        register_rest_route(self::REST_NS, self::REST_ROUTE, [
            'methods' => 'GET',
            'callback' => [self::class, 'read'],
            'permission_callback' => '__return_true',
            'args' => [
                'token' => ['required' => true],
                'post' => ['required' => true],
                'tail' => ['required' => false],
            ],
        ]);
    }

    public static function read(\WP_REST_Request $request): \WP_REST_Response
    {
        $provided = strtolower((string) $request->get_param('token'));
        $expected = self::supportToken(false);
        if ($expected === '' || strlen($provided) !== 64 || !hash_equals($expected, $provided)) {
            return new \WP_REST_Response(['error' => 'not_found'], 404);
        }
        $postId = absint($request->get_param('post'));
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            return new \WP_REST_Response(['error' => 'not_found'], 404);
        }
        $tail = max(1, min(600, absint($request->get_param('tail')) ?: 300));
        $entries = self::entries($postId);
        $response = new \WP_REST_Response([
            'product' => 'Visual Designer Manager diagnostics',
            'schemaVersion' => 1,
            'postId' => $postId,
            'pageSlug' => (string) get_post_field('post_name', $postId),
            'entryCount' => count($entries),
            'entries' => array_slice($entries, -$tail),
        ], 200);
        $response->header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0');
        $response->header('X-Robots-Tag', 'noindex, nofollow, noarchive');
        return $response;
    }

    public static function supportUrl(int $postId): string
    {
        return rest_url(self::REST_NS . '/diagnostics/' . self::supportToken() . '?post=' . $postId);
    }

    private static function supportToken(bool $create = true): string
    {
        $token = strtolower((string) get_option(self::TOKEN_OPTION, ''));
        if (preg_match('/^[a-f0-9]{64}$/', $token)) {
            return $token;
        }
        if (!$create) {
            return '';
        }
        try {
            $token = bin2hex(random_bytes(32));
        } catch (\Throwable $error) {
            $token = hash('sha256', wp_generate_uuid4() . '|' . wp_salt('auth') . '|' . microtime(true));
        }
        update_option(self::TOKEN_OPTION, $token, false);
        return $token;
    }

    /** @return mixed */
    private static function sanitizeValue($value, string $key, int $depth)
    {
        if ($depth > 6) {
            return '[depth]';
        }
        if (preg_match('/pass(word)?|secret|token|nonce|authorization|api[-_ ]?key|cookie|bearer|credential|csrf/i', $key)) {
            return '[REDACTED]';
        }
        if (preg_match('/^(text|content|html|markup|body|value)$/i', $key)) {
            $length = is_scalar($value) ? strlen((string) $value) : 0;
            return '[REDACTED_CONTENT length=' . $length . ']';
        }
        if (is_array($value)) {
            $out = [];
            $count = 0;
            foreach ($value as $name => $item) {
                if (++$count > 350) {
                    $out['_truncated'] = true;
                    break;
                }
                $out[is_string($name) ? substr($name, 0, 120) : $name] = self::sanitizeValue($item, (string) $name, $depth + 1);
            }
            return $out;
        }
        if (is_bool($value) || is_int($value) || is_float($value) || $value === null) {
            return $value;
        }
        if (is_scalar($value)) {
            return substr(sanitize_text_field((string) $value), 0, 1000);
        }
        return '[unsupported]';
    }
}
