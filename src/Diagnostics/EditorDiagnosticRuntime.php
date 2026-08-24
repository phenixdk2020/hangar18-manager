<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Diagnostics;

/**
 * Private structured diagnostic store for the Hangar18 page editor.
 *
 * Browser trace events are persisted server-side in bounded WordPress options.
 * A 256-bit read-only support token exposes only the sanitized diagnostic
 * payload through a dedicated REST route. No passwords, cookies, nonces,
 * credentials or raw editor content are intentionally persisted.
 */
final class EditorDiagnosticRuntime
{
    private const TOKEN_OPTION = 'hangar18_diag_support_token_v1';
    private const INDEX_OPTION = 'hangar18_diag_session_index_v1';
    private const SESSION_PREFIX = 'hangar18_diag_session_v1_';
    private const MAX_SESSIONS = 20;
    private const MAX_ENTRIES = 3000;
    private const MAX_BATCH = 120;
    private const ROUTE_NAMESPACE = 'hangar18/v1';
    private const ROUTE = '/diagnostics/(?P<token>[a-fA-F0-9]{64})';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        add_action('wp_ajax_h18_diag_append', [self::class, 'ajaxAppend']);
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureBeforeSave'], 1);
        add_action('rest_api_init', [self::class, 'registerRoute']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 120);
    }

    public static function enqueue(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages') {
            return;
        }
        if (!class_exists('Hangar18\\UltimateDesigner\\Admin\\UltimateDesignerTraceAdminController')) {
            return;
        }
        if (!\Hangar18\UltimateDesigner\Admin\UltimateDesignerTraceAdminController::enabled()) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $path = $pluginDir . '/assets/ultimate-designer-live-diagnostics-v0888.js';
        wp_enqueue_script(
            'hangar18-ultimate-designer-live-diagnostics-v0888',
            $pluginUrl . 'assets/ultimate-designer-live-diagnostics-v0888.js',
            ['hangar18-ultimate-designer-trace-tools-v0879'],
            is_file($path) ? (string) filemtime($path) : '0.8.88',
            true
        );

        $token = self::supportToken();
        wp_localize_script(
            'hangar18-ultimate-designer-live-diagnostics-v0888',
            'H18LiveDiagnosticsV0888',
            [
                'version' => '0.8.88',
                'ajaxUrl' => admin_url('admin-ajax.php'),
                'action' => 'h18_diag_append',
                'nonce' => wp_create_nonce('h18_diag_append'),
                'shareUrl' => rest_url(self::ROUTE_NAMESPACE . '/diagnostics/' . $token),
                'pageSlug' => isset($_GET['page_slug']) ? sanitize_title((string) wp_unslash($_GET['page_slug'])) : '',
                'maxBatch' => self::MAX_BATCH,
            ]
        );
    }

    public static function ajaxAppend(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Forbidden'], 403);
        }
        check_ajax_referer('h18_diag_append', 'nonce');

        $session = self::sessionId($_POST['session'] ?? '');
        if ($session === '') {
            wp_send_json_error(['message' => 'Missing diagnostic session'], 400);
        }

        $raw = isset($_POST['entries_json']) ? (string) wp_unslash($_POST['entries_json']) : '';
        if ($raw === '' || strlen($raw) > 1024 * 1024) {
            wp_send_json_error(['message' => 'Invalid diagnostic batch'], 400);
        }
        $decoded = json_decode($raw, true);
        if (!is_array($decoded)) {
            wp_send_json_error(['message' => 'Invalid diagnostic JSON'], 400);
        }

        $entries = [];
        foreach (array_slice($decoded, 0, self::MAX_BATCH) as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $entries[] = self::sanitizeEntry($entry);
        }
        if ($entries) {
            self::append($session, $entries, [
                'Source' => 'browser',
                'PageSlug' => isset($_POST['page_slug']) ? sanitize_title((string) wp_unslash($_POST['page_slug'])) : '',
                'PluginVersion' => class_exists('Hangar18_Manager') ? (string) \Hangar18_Manager::VERSION : '',
                'UserId' => get_current_user_id(),
            ]);
        }

        wp_send_json_success(['stored' => count($entries), 'session' => $session]);
    }

    public static function captureBeforeSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        $saveNonce = isset($_POST['_wpnonce']) ? sanitize_text_field((string) wp_unslash($_POST['_wpnonce'])) : '';
        if ($saveNonce === '' || !wp_verify_nonce($saveNonce, 'h18_save_page_editor')) {
            return;
        }
        $session = self::sessionId($_POST['h18_diag_session'] ?? '');
        if ($session === '') {
            return;
        }

        $sections = isset($_POST['sections']) && is_array($_POST['sections']) ? wp_unslash($_POST['sections']) : [];
        $summary = [];
        foreach (array_slice($sections, 0, 200, true) as $index => $section) {
            if (!is_array($section)) {
                continue;
            }
            $summary[] = self::sectionSummary($section, (int) $index);
        }

        self::append($session, [[
            'type' => 'SERVER_BEFORE_SAVE',
            'time' => gmdate('c'),
            'detail' => [
                'pageSlug' => isset($_POST['page_slug']) ? sanitize_title((string) wp_unslash($_POST['page_slug'])) : '',
                'sectionCount' => count($summary),
                'sections' => $summary,
                'hasSpanState' => isset($_POST['h18_lego_layout_span_v1']),
                'hasStackState' => isset($_POST['h18_lego_stack_v0851']),
            ],
        ]], [
            'Source' => 'server-save',
            'PageSlug' => isset($_POST['page_slug']) ? sanitize_title((string) wp_unslash($_POST['page_slug'])) : '',
            'PluginVersion' => class_exists('Hangar18_Manager') ? (string) \Hangar18_Manager::VERSION : '',
            'UserId' => get_current_user_id(),
        ]);
    }

    public static function registerRoute(): void
    {
        register_rest_route(
            self::ROUTE_NAMESPACE,
            self::ROUTE,
            [
                'methods' => 'GET',
                'callback' => [self::class, 'readDiagnostics'],
                'permission_callback' => '__return_true',
                'args' => [
                    'token' => ['required' => true],
                    'session' => ['required' => false],
                    'tail' => ['required' => false],
                ],
            ]
        );
    }

    public static function readDiagnostics(\WP_REST_Request $request): \WP_REST_Response
    {
        $provided = strtolower((string) $request->get_param('token'));
        $expected = self::supportToken(false);
        if ($expected === '' || strlen($provided) !== 64 || !hash_equals($expected, $provided)) {
            return new \WP_REST_Response(['error' => 'not_found'], 404);
        }

        $requested = self::sessionId($request->get_param('session') ?? '');
        $index = self::index();
        if ($requested === '') {
            $requested = isset($index[0]['Session']) ? self::sessionId($index[0]['Session']) : '';
        }
        if ($requested === '') {
            return self::noCacheResponse([
                'product' => 'Hangar18 Ultimate Designer diagnostics',
                'session' => '',
                'entries' => [],
                'message' => 'No diagnostic session has been stored yet.',
            ]);
        }

        $record = get_option(self::SESSION_PREFIX . md5($requested), []);
        $record = is_array($record) ? $record : [];
        $entries = isset($record['Entries']) && is_array($record['Entries']) ? $record['Entries'] : [];
        $tail = (int) $request->get_param('tail');
        $tail = max(1, min(2000, $tail > 0 ? $tail : 800));
        $entries = array_slice($entries, -$tail);

        return self::noCacheResponse([
            'product' => 'Hangar18 Ultimate Designer diagnostics',
            'schemaVersion' => 1,
            'session' => $requested,
            'updatedUtc' => (string) ($record['UpdatedUtc'] ?? ''),
            'meta' => isset($record['Meta']) && is_array($record['Meta']) ? $record['Meta'] : [],
            'entryCount' => isset($record['Entries']) && is_array($record['Entries']) ? count($record['Entries']) : 0,
            'returned' => count($entries),
            'entries' => $entries,
        ]);
    }

    private static function noCacheResponse(array $data): \WP_REST_Response
    {
        $response = new \WP_REST_Response($data, 200);
        $response->header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0');
        $response->header('Pragma', 'no-cache');
        $response->header('X-Robots-Tag', 'noindex, nofollow, noarchive');
        return $response;
    }

    private static function append(string $session, array $entries, array $meta): void
    {
        $option = self::SESSION_PREFIX . md5($session);
        $record = get_option($option, []);
        $record = is_array($record) ? $record : [];
        $existing = isset($record['Entries']) && is_array($record['Entries']) ? $record['Entries'] : [];
        foreach ($entries as $entry) {
            $existing[] = self::sanitizeEntry(is_array($entry) ? $entry : []);
        }
        if (count($existing) > self::MAX_ENTRIES) {
            $existing = array_slice($existing, -self::MAX_ENTRIES);
        }

        $cleanMeta = [
            'Source' => sanitize_key((string) ($meta['Source'] ?? '')),
            'PageSlug' => sanitize_title((string) ($meta['PageSlug'] ?? '')),
            'PluginVersion' => sanitize_text_field((string) ($meta['PluginVersion'] ?? '')),
            'UserId' => (int) ($meta['UserId'] ?? 0),
        ];
        update_option($option, [
            'SchemaVersion' => 1,
            'Session' => $session,
            'CreatedUtc' => (string) ($record['CreatedUtc'] ?? gmdate('c')),
            'UpdatedUtc' => gmdate('c'),
            'Meta' => array_filter(array_merge(isset($record['Meta']) && is_array($record['Meta']) ? $record['Meta'] : [], $cleanMeta), static fn($value): bool => $value !== '' && $value !== 0),
            'Entries' => $existing,
        ], false);

        self::touchIndex($session, $cleanMeta, count($existing));
    }

    private static function touchIndex(string $session, array $meta, int $count): void
    {
        $index = array_values(array_filter(self::index(), static fn(array $item): bool => (string) ($item['Session'] ?? '') !== $session));
        array_unshift($index, [
            'Session' => $session,
            'UpdatedUtc' => gmdate('c'),
            'PageSlug' => sanitize_title((string) ($meta['PageSlug'] ?? '')),
            'PluginVersion' => sanitize_text_field((string) ($meta['PluginVersion'] ?? '')),
            'EntryCount' => $count,
        ]);
        $removed = array_slice($index, self::MAX_SESSIONS);
        $index = array_slice($index, 0, self::MAX_SESSIONS);
        update_option(self::INDEX_OPTION, $index, false);
        foreach ($removed as $item) {
            $old = self::sessionId($item['Session'] ?? '');
            if ($old !== '') {
                delete_option(self::SESSION_PREFIX . md5($old));
            }
        }
    }

    private static function index(): array
    {
        $index = get_option(self::INDEX_OPTION, []);
        return is_array($index) ? array_values(array_filter($index, 'is_array')) : [];
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
        } catch (\Throwable $exception) {
            $token = hash('sha256', wp_generate_uuid4() . '|' . wp_salt('auth') . '|' . microtime(true));
        }
        update_option(self::TOKEN_OPTION, $token, false);
        return $token;
    }

    /** @param mixed $raw */
    private static function sessionId($raw): string
    {
        $value = strtolower((string) wp_unslash($raw));
        $value = preg_replace('/[^a-z0-9._-]/', '', $value);
        return is_string($value) ? substr($value, 0, 100) : '';
    }

    private static function sectionSummary(array $section, int $index): array
    {
        $safe = static function ($value, int $max = 120): string {
            return substr(sanitize_text_field(is_scalar($value) ? (string) $value : ''), 0, $max);
        };
        $number = static function ($value): int {
            return is_numeric($value) ? (int) $value : 0;
        };

        return [
            'index' => $index,
            'key' => sanitize_key((string) ($section['Key'] ?? '')),
            'type' => sanitize_key((string) ($section['Type'] ?? '')),
            'parentKey' => sanitize_key((string) ($section['LayoutParentKey'] ?? '')),
            'order' => $number($section['Order'] ?? 0),
            'remove' => !empty($section['Remove']),
            'elementWidth' => $number($section['ElementWidthPercent'] ?? 0),
            'tabletWidth' => $number($section['TabletWidthPercent'] ?? -1),
            'mobileWidth' => $number($section['MobileWidthPercent'] ?? -1),
            'elementMinHeight' => $number($section['ElementMinHeightPx'] ?? 0),
            'tabletMinHeight' => $number($section['TabletMinHeightPx'] ?? 0),
            'mobileMinHeight' => $number($section['MobileMinHeightPx'] ?? 0),
            'imageAspect' => $safe($section['ImageAspectRatio'] ?? '', 30),
            'imageFit' => $safe($section['ImageFit'] ?? '', 30),
            'imageHeight' => $number($section['ImageHeightPx'] ?? 0),
            'mobileImageHeight' => $number($section['MobileImageHeightPx'] ?? 0),
            'imageWidth' => $number($section['ImageWidthPercent'] ?? 0),
            'mobileImageWidth' => $number($section['MobileImageWidthPercent'] ?? 0),
            'mediaId' => $number($section['MediaId'] ?? 0),
            'titleLength' => strlen((string) ($section['Title'] ?? '')),
            'contentLength' => strlen((string) ($section['Content'] ?? '')),
        ];
    }

    private static function sanitizeEntry(array $entry): array
    {
        return self::sanitizeValue($entry, '', 0);
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
        if (preg_match('/^(value|text|content|html|markup|body)$/i', $key)) {
            $length = is_scalar($value) ? strlen((string) $value) : 0;
            return '[REDACTED_UI length=' . $length . ']';
        }
        if (is_array($value)) {
            $out = [];
            $limit = 0;
            foreach ($value as $name => $item) {
                if (++$limit > 250) {
                    $out['_truncated'] = true;
                    break;
                }
                $cleanKey = is_string($name) ? substr($name, 0, 120) : $name;
                $out[$cleanKey] = self::sanitizeValue($item, (string) $name, $depth + 1);
            }
            return $out;
        }
        if (is_bool($value) || is_int($value) || is_float($value) || $value === null) {
            return $value;
        }
        if (is_scalar($value)) {
            $string = (string) $value;
            if (preg_match('/content|html|markup|body|messagebody/i', $key)) {
                return '[REDACTED_CONTENT length=' . strlen($string) . ']';
            }
            $string = preg_replace('/(Bearer\s+)[A-Za-z0-9._~+\/-]+/i', '$1[REDACTED]', $string);
            $string = preg_replace('/((?:token|nonce|password|secret|cookie|authorization)\s*[=:]\s*)[^\s,;]+/i', '$1[REDACTED]', (string) $string);
            return substr(sanitize_text_field((string) $string), 0, 4000);
        }
        return '[unsupported]';
    }
}
