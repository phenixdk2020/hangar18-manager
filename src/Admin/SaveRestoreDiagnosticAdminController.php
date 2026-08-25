<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * v0.9.2 structural diagnostics around Page Editor Save and Restore.
 *
 * This class is deliberately observational. It never mutates editor content,
 * canonical layout state, geometry, backup files or restore decisions. Events
 * are appended to the existing bounded private diagnostic store so the same
 * read-only support link can be used for interaction, Save and Restore traces.
 */
final class SaveRestoreDiagnosticAdminController
{
    public const VERSION = '0.9.2';

    private const INDEX_OPTION = 'hangar18_diag_session_index_v1';
    private const SESSION_PREFIX = 'hangar18_diag_session_v1_';
    private const LAYOUT_OPTION = 'hangar18_ultimate_designer_layout_model_v0900';
    private const HISTORY_OPTION = 'hangar18_manager_page_versions_v1';
    private const MAX_SESSIONS = 20;
    private const MAX_ENTRIES = 3000;
    private const SAVE_NONCE_ACTION = 'h18_save_page_editor';
    private const RESTORE_NONCE_ACTION = 'h18_ud_page_version_restore';

    private static bool $registered = false;
    /** @var array<string,mixed> */
    private static array $pendingSave = [];
    /** @var array<string,mixed> */
    private static array $pendingRestore = [];
    private static bool $saveShutdownRegistered = false;
    private static bool $restoreShutdownRegistered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        // Existing diagnostic request snapshot runs at priority 1. We capture
        // the baseline at 2, then the canonical v0.9.0 model is written at 4
        // and physical geometry is merged at 5. Priority 6 therefore sees the
        // exact structural state handed to the legacy content saver at 10.
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSaveIntent'], 2);
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSaveProjected'], 6);

        // Restore controller owns mutation at the default priority. These
        // priority-1 observers only capture before-state and register shutdown.
        add_action('admin_post_h18_ud_restore_page_version_original', [self::class, 'captureRestoreOriginal'], 1);
        add_action('admin_post_h18_ud_restore_page_version_copy', [self::class, 'captureRestoreCopy'], 1);

        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 150);
    }

    public static function enqueue(): void
    {
        if (!current_user_can('edit_pages') || !self::loggingEnabled()) {
            return;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages') {
            return;
        }

        $dir = dirname(__DIR__, 2);
        $url = plugin_dir_url($dir . '/hangar18-manager.php');
        $path = $dir . '/assets/ultimate-designer-save-restore-diagnostics-v0902.js';
        $deps = ['hangar18-ultimate-designer-physical-canvas-v0901'];
        if (wp_script_is('hangar18-ultimate-designer-live-diagnostics-v0888', 'enqueued')) {
            $deps[] = 'hangar18-ultimate-designer-live-diagnostics-v0888';
        }

        wp_enqueue_script(
            'hangar18-ultimate-designer-save-restore-diagnostics-v0902',
            $url . 'assets/ultimate-designer-save-restore-diagnostics-v0902.js',
            $deps,
            is_file($path) ? (string) filemtime($path) : self::VERSION,
            true
        );
        wp_localize_script(
            'hangar18-ultimate-designer-save-restore-diagnostics-v0902',
            'H18SaveRestoreDiagnosticsV0902',
            [
                'version' => self::VERSION,
                'pageSlug' => isset($_GET['page_slug']) ? sanitize_title((string) wp_unslash($_GET['page_slug'])) : '',
            ]
        );
    }

    public static function captureSaveIntent(): void
    {
        if (!self::authorizedSave() || !self::loggingEnabled()) {
            return;
        }
        $slug = self::postedSlug();
        if ($slug === '') {
            return;
        }
        $session = self::sessionId($_POST['h18_diag_session'] ?? '');
        if ($session === '') {
            $session = self::latestSessionForPage($slug);
        }
        if ($session === '') {
            return;
        }

        $before = self::persistedState($slug);
        self::$pendingSave = [
            'session' => $session,
            'slug' => $slug,
            'startedUtc' => gmdate('c'),
            'before' => $before,
        ];

        self::appendEvent($session, 'SERVER_SAVE_INTENT_V0902', [
            'pageSlug' => $slug,
            'postedSectionCount' => self::postedSectionCount(),
            'hasCanonicalPayload' => isset($_POST['h18_layout_model_v0900']) && is_string($_POST['h18_layout_model_v0900']),
            'hasGeometryPayload' => isset($_POST['h18_layout_geometry_v0901']) && is_string($_POST['h18_layout_geometry_v0901']),
            'before' => $before,
        ], 'server-save', $slug);
    }

    public static function captureSaveProjected(): void
    {
        if (!self::authorizedSave() || !self::loggingEnabled()) {
            return;
        }
        $slug = self::postedSlug();
        if ($slug === '') {
            return;
        }
        $session = self::sessionId(self::$pendingSave['session'] ?? ($_POST['h18_diag_session'] ?? ''));
        if ($session === '') {
            $session = self::latestSessionForPage($slug);
        }
        if ($session === '') {
            return;
        }

        if (!self::$pendingSave) {
            self::$pendingSave = [
                'session' => $session,
                'slug' => $slug,
                'startedUtc' => gmdate('c'),
                'before' => self::persistedState($slug),
            ];
        }

        self::appendEvent($session, 'SERVER_SAVE_PROJECTED_V0902', [
            'pageSlug' => $slug,
            'postedSectionCount' => self::postedSectionCount(),
            'postedSections' => self::postedSectionsSummary(),
            'hasSpanState' => isset($_POST['h18_lego_layout_span']),
            'hasStackState' => isset($_POST['h18_lego_stack_v0851']),
            'hasGeometryState' => isset($_POST['h18_layout_geometry_v0901']),
            'projectedPersistedState' => self::persistedState($slug),
        ], 'server-save', $slug);

        if (!self::$saveShutdownRegistered) {
            self::$saveShutdownRegistered = true;
            register_shutdown_function([self::class, 'captureSaveShutdown']);
        }
    }

    public static function captureSaveShutdown(): void
    {
        if (!self::$pendingSave) {
            return;
        }
        $pending = self::$pendingSave;
        self::$pendingSave = [];
        $session = self::sessionId($pending['session'] ?? '');
        $slug = sanitize_title((string) ($pending['slug'] ?? ''));
        if ($session === '' || $slug === '') {
            return;
        }

        $before = is_array($pending['before'] ?? null) ? $pending['before'] : [];
        $after = self::persistedState($slug);
        $beforeVersion = (int) ($before['version']['version'] ?? 0);
        $afterVersion = (int) ($after['version']['version'] ?? 0);
        $beforeHash = (string) ($before['wordpress']['contentHash'] ?? '');
        $afterHash = (string) ($after['wordpress']['contentHash'] ?? '');
        $beforeLayout = (string) ($before['layout']['digest'] ?? '');
        $afterLayout = (string) ($after['layout']['digest'] ?? '');

        self::appendEvent($session, 'SERVER_SAVE_RESULT_V0902', [
            'pageSlug' => $slug,
            'startedUtc' => (string) ($pending['startedUtc'] ?? ''),
            'finishedUtc' => gmdate('c'),
            'versionBefore' => $beforeVersion,
            'versionAfter' => $afterVersion,
            'versionDelta' => $afterVersion - $beforeVersion,
            'wordpressHashChanged' => $beforeHash !== '' && $afterHash !== '' && !hash_equals($beforeHash, $afterHash),
            'layoutDigestChanged' => $beforeLayout !== '' && $afterLayout !== '' && !hash_equals($beforeLayout, $afterLayout),
            'fatal' => self::fatalSummary(),
            'after' => $after,
        ], 'server-save-result', $slug);
    }

    public static function captureRestoreOriginal(): void
    {
        self::captureRestoreBegin('original');
    }

    public static function captureRestoreCopy(): void
    {
        self::captureRestoreBegin('copy');
    }

    private static function captureRestoreBegin(string $mode): void
    {
        if (!current_user_can('edit_pages') || !self::validRestoreNonce() || !self::loggingEnabled()) {
            return;
        }
        $slug = self::postedSlug();
        $version = absint($_POST['version'] ?? 0);
        if ($slug === '' || $version <= 0) {
            return;
        }

        $session = self::sessionId($_POST['h18_diag_session'] ?? '');
        if ($session === '') {
            $session = self::latestSessionForPage($slug);
        }
        if ($session === '') {
            $session = self::newServerSession('restore');
        }
        if ($session === '') {
            return;
        }

        $before = self::persistedState($slug);
        self::$pendingRestore = [
            'session' => $session,
            'slug' => $slug,
            'mode' => $mode,
            'version' => $version,
            'startedUtc' => gmdate('c'),
            'before' => $before,
            'redirect' => [],
        ];

        self::appendEvent($session, 'SERVER_RESTORE_BEGIN_V0902', [
            'mode' => $mode,
            'pageSlug' => $slug,
            'targetVersion' => $version,
            'sourceFilePosted' => sanitize_file_name((string) wp_unslash($_POST['source_file'] ?? '')),
            'before' => $before,
        ], 'server-restore', $slug);

        add_filter('wp_redirect', [self::class, 'captureRestoreRedirect'], 999, 2);
        if (!self::$restoreShutdownRegistered) {
            self::$restoreShutdownRegistered = true;
            register_shutdown_function([self::class, 'captureRestoreShutdown']);
        }
    }

    /** @param mixed $location @param mixed $status @return mixed */
    public static function captureRestoreRedirect($location, $status)
    {
        if (!self::$pendingRestore || !is_string($location)) {
            return $location;
        }
        $query = (string) wp_parse_url($location, PHP_URL_QUERY);
        $params = [];
        if ($query !== '') {
            parse_str($query, $params);
        }
        self::$pendingRestore['redirect'] = [
            'httpStatus' => is_numeric($status) ? (int) $status : 0,
            'restoreStatus' => sanitize_key((string) ($params['h18_version_restore_status'] ?? '')),
            'pageSlug' => sanitize_title((string) ($params['page_slug'] ?? '')),
            'messageLength' => strlen((string) ($params['h18_version_restore_message'] ?? '')),
        ];
        return $location;
    }

    public static function captureRestoreShutdown(): void
    {
        if (!self::$pendingRestore) {
            return;
        }
        $pending = self::$pendingRestore;
        self::$pendingRestore = [];
        $session = self::sessionId($pending['session'] ?? '');
        $slug = sanitize_title((string) ($pending['slug'] ?? ''));
        if ($session === '' || $slug === '') {
            return;
        }

        $before = is_array($pending['before'] ?? null) ? $pending['before'] : [];
        $after = self::persistedState($slug);
        $beforeHash = (string) ($before['wordpress']['contentHash'] ?? '');
        $afterHash = (string) ($after['wordpress']['contentHash'] ?? '');
        $beforeLayout = (string) ($before['layout']['digest'] ?? '');
        $afterLayout = (string) ($after['layout']['digest'] ?? '');

        self::appendEvent($session, 'SERVER_RESTORE_RESULT_V0902', [
            'mode' => sanitize_key((string) ($pending['mode'] ?? '')),
            'pageSlug' => $slug,
            'targetVersion' => (int) ($pending['version'] ?? 0),
            'startedUtc' => (string) ($pending['startedUtc'] ?? ''),
            'finishedUtc' => gmdate('c'),
            'redirect' => is_array($pending['redirect'] ?? null) ? $pending['redirect'] : [],
            'originalWordpressHashChanged' => $beforeHash !== '' && $afterHash !== '' && !hash_equals($beforeHash, $afterHash),
            'canonicalLayoutDigestChanged' => $beforeLayout !== '' && $afterLayout !== '' && !hash_equals($beforeLayout, $afterLayout),
            'fatal' => self::fatalSummary(),
            'after' => $after,
        ], 'server-restore-result', $slug);
    }

    private static function authorizedSave(): bool
    {
        if (!current_user_can('edit_pages')) {
            return false;
        }
        $nonce = isset($_POST['_wpnonce']) ? sanitize_text_field((string) wp_unslash($_POST['_wpnonce'])) : '';
        return $nonce !== '' && wp_verify_nonce($nonce, self::SAVE_NONCE_ACTION) !== false;
    }

    private static function validRestoreNonce(): bool
    {
        $nonce = isset($_POST['_wpnonce']) ? sanitize_text_field((string) wp_unslash($_POST['_wpnonce'])) : '';
        return $nonce !== '' && wp_verify_nonce($nonce, self::RESTORE_NONCE_ACTION) !== false;
    }

    private static function loggingEnabled(): bool
    {
        return class_exists('Hangar18\\UltimateDesigner\\Admin\\UltimateDesignerTraceAdminController')
            && UltimateDesignerTraceAdminController::enabled();
    }

    private static function postedSlug(): string
    {
        return isset($_POST['page_slug'])
            ? sanitize_title((string) wp_unslash($_POST['page_slug']))
            : '';
    }

    private static function postedSectionCount(): int
    {
        return isset($_POST['sections']) && is_array($_POST['sections']) ? count($_POST['sections']) : 0;
    }

    /** @return array<int,array<string,mixed>> */
    private static function postedSectionsSummary(): array
    {
        $sections = isset($_POST['sections']) && is_array($_POST['sections']) ? wp_unslash($_POST['sections']) : [];
        $out = [];
        foreach (array_slice($sections, 0, 150, true) as $index => $section) {
            if (!is_array($section)) {
                continue;
            }
            $out[] = [
                'index' => (int) $index,
                'key' => sanitize_key((string) ($section['Key'] ?? '')),
                'type' => sanitize_key((string) ($section['Type'] ?? '')),
                'parentKey' => sanitize_key((string) ($section['LayoutParentKey'] ?? '')),
                'order' => is_numeric($section['Order'] ?? null) ? (int) $section['Order'] : 0,
                'removed' => !empty($section['Remove']),
            ];
        }
        return $out;
    }

    /** @return array<string,mixed> */
    private static function persistedState(string $slug): array
    {
        return [
            'wordpress' => self::wordpressState($slug),
            'version' => self::versionState($slug),
            'layout' => self::layoutState($slug),
        ];
    }

    /** @return array<string,mixed> */
    private static function wordpressState(string $slug): array
    {
        $page = get_page_by_path($slug, OBJECT, 'page');
        if (!$page instanceof \WP_Post) {
            return ['exists' => false, 'pageId' => 0, 'contentHash' => '', 'status' => ''];
        }
        return [
            'exists' => true,
            'pageId' => (int) $page->ID,
            'contentHash' => hash('sha256', (string) $page->post_content),
            'status' => sanitize_key((string) $page->post_status),
            'modifiedGmt' => sanitize_text_field((string) $page->post_modified_gmt),
        ];
    }

    /** @return array<string,mixed> */
    private static function versionState(string $slug): array
    {
        $all = get_option(self::HISTORY_OPTION, []);
        $entries = is_array($all) && isset($all[$slug]) && is_array($all[$slug]) ? $all[$slug] : [];
        $latest = [];
        foreach ($entries as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            if ((int) ($entry['Version'] ?? 0) > (int) ($latest['Version'] ?? 0)) {
                $latest = $entry;
            }
        }
        return [
            'count' => count($entries),
            'version' => (int) ($latest['Version'] ?? 0),
            'savedUtc' => sanitize_text_field((string) ($latest['SavedUtc'] ?? '')),
            'activeSections' => (int) ($latest['ActiveSections'] ?? 0),
            'contentHash' => substr(preg_replace('/[^a-f0-9]/i', '', (string) ($latest['ContentHash'] ?? '')) ?: '', 0, 64),
            'hasFullBackup' => sanitize_file_name((string) ($latest['FullBackupFile'] ?? '')) !== '',
            'hasSnapshot' => sanitize_file_name((string) ($latest['SnapshotFile'] ?? '')) !== '',
        ];
    }

    /** @return array<string,mixed> */
    private static function layoutState(string $slug): array
    {
        $store = get_option(self::LAYOUT_OPTION, []);
        $page = is_array($store) && isset($store[$slug]) && is_array($store[$slug]) ? $store[$slug] : [];
        $sections = isset($page['Sections']) && is_array($page['Sections']) ? $page['Sections'] : [];
        $out = [];
        $active = 0;
        $removed = 0;
        foreach (array_slice($sections, 0, 150, true) as $rawKey => $section) {
            if (!is_array($section)) {
                continue;
            }
            $key = sanitize_key((string) ($section['Key'] ?? $rawKey));
            if ($key === '') {
                continue;
            }
            $isRemoved = !empty($section['Removed']);
            $isRemoved ? $removed++ : $active++;
            $out[$key] = [
                'key' => $key,
                'type' => sanitize_key((string) ($section['Type'] ?? '')),
                'parentKey' => sanitize_key((string) ($section['ParentKey'] ?? $section['LayoutParentKey'] ?? '')),
                'order' => is_numeric($section['Order'] ?? null) ? (int) $section['Order'] : 0,
                'removed' => $isRemoved,
                'span' => self::spanSummary($section['Span'] ?? []),
                'stack' => self::stackSummary($section['Stack'] ?? []),
                'geometry' => self::geometrySummary($section['Geometry'] ?? []),
            ];
        }
        ksort($out);
        $json = wp_json_encode($out, JSON_UNESCAPED_SLASHES);
        return [
            'schemaVersion' => (int) ($page['SchemaVersion'] ?? 0),
            'engineVersion' => sanitize_text_field((string) ($page['EngineVersion'] ?? '')),
            'savedUtc' => sanitize_text_field((string) ($page['SavedUtc'] ?? $page['GeometrySavedUtc'] ?? '')),
            'sectionCount' => count($out),
            'activeCount' => $active,
            'removedCount' => $removed,
            'digest' => hash('sha256', is_string($json) ? $json : ''),
            'sections' => $out,
        ];
    }

    /** @param mixed $raw @return array<string,mixed> */
    private static function spanSummary($raw): array
    {
        if (!is_array($raw)) {
            return [];
        }
        $device = static function ($branch): array {
            if (!is_array($branch)) {
                return [];
            }
            return [
                'span' => is_numeric($branch['Span'] ?? null) ? (int) $branch['Span'] : 0,
                'inheritDesktop' => array_key_exists('InheritDesktop', $branch) ? (bool) $branch['InheritDesktop'] : null,
                'hasOverride' => array_key_exists('HasOverride', $branch) ? (bool) $branch['HasOverride'] : null,
            ];
        };
        return [
            'desktop' => $device($raw['Desktop'] ?? []),
            'tablet' => $device($raw['Tablet'] ?? []),
            'mobile' => $device($raw['Mobile'] ?? []),
        ];
    }

    /** @param mixed $raw @return array<string,mixed> */
    private static function stackSummary($raw): array
    {
        if (!is_array($raw)) {
            return [];
        }
        return [
            'rootKey' => sanitize_key((string) ($raw['StackRootKey'] ?? '')),
            'order' => is_numeric($raw['StackOrder'] ?? null) ? (int) $raw['StackOrder'] : 0,
            'desktopPercent' => is_numeric($raw['DesktopPercent'] ?? null) ? (int) $raw['DesktopPercent'] : 0,
            'tabletPercent' => is_numeric($raw['TabletPercent'] ?? null) ? (int) $raw['TabletPercent'] : 0,
            'mobilePercent' => is_numeric($raw['MobilePercent'] ?? null) ? (int) $raw['MobilePercent'] : 0,
        ];
    }

    /** @param mixed $raw @return array<string,mixed> */
    private static function geometrySummary($raw): array
    {
        if (!is_array($raw)) {
            return [];
        }
        $device = static function ($branch): array {
            if (!is_array($branch)) {
                return [];
            }
            return [
                'explicit' => !empty($branch['Explicit']),
                'x' => is_numeric($branch['X'] ?? null) ? (int) $branch['X'] : 0,
                'y' => is_numeric($branch['Y'] ?? null) ? (int) $branch['Y'] : 0,
                'w' => is_numeric($branch['W'] ?? null) ? (int) $branch['W'] : 0,
                'h' => is_numeric($branch['H'] ?? null) ? (int) $branch['H'] : 0,
                'inheritDesktop' => array_key_exists('InheritDesktop', $branch) ? (bool) $branch['InheritDesktop'] : null,
                'hasOverride' => array_key_exists('HasOverride', $branch) ? (bool) $branch['HasOverride'] : null,
            ];
        };
        return [
            'desktop' => $device($raw['Desktop'] ?? []),
            'tablet' => $device($raw['Tablet'] ?? []),
            'mobile' => $device($raw['Mobile'] ?? []),
        ];
    }

    /** @return array<string,mixed> */
    private static function fatalSummary(): array
    {
        $error = error_get_last();
        if (!is_array($error)) {
            return [];
        }
        $type = (int) ($error['type'] ?? 0);
        if (!in_array($type, [E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR, E_USER_ERROR, E_RECOVERABLE_ERROR], true)) {
            return [];
        }
        return [
            'type' => $type,
            'file' => sanitize_file_name(basename((string) ($error['file'] ?? ''))),
            'line' => (int) ($error['line'] ?? 0),
            'message' => substr(sanitize_text_field((string) ($error['message'] ?? '')), 0, 500),
        ];
    }

    private static function latestSessionForPage(string $slug): string
    {
        $index = get_option(self::INDEX_OPTION, []);
        if (!is_array($index)) {
            return '';
        }
        $userId = get_current_user_id();
        foreach (array_slice($index, 0, self::MAX_SESSIONS) as $item) {
            if (!is_array($item) || sanitize_title((string) ($item['PageSlug'] ?? '')) !== $slug) {
                continue;
            }
            $session = self::sessionId($item['Session'] ?? '');
            if ($session === '') {
                continue;
            }
            $record = get_option(self::SESSION_PREFIX . md5($session), []);
            $meta = is_array($record) && isset($record['Meta']) && is_array($record['Meta']) ? $record['Meta'] : [];
            if ((int) ($meta['UserId'] ?? 0) === $userId) {
                return $session;
            }
        }
        return '';
    }

    private static function newServerSession(string $kind): string
    {
        $uuid = strtolower(preg_replace('/[^a-z0-9]/', '', wp_generate_uuid4()) ?: '');
        return self::sessionId('diag-srv-' . sanitize_key($kind) . '-' . get_current_user_id() . '-' . time() . '-' . substr($uuid, 0, 10));
    }

    private static function appendEvent(string $session, string $type, array $detail, string $source, string $slug): void
    {
        $session = self::sessionId($session);
        if ($session === '') {
            return;
        }
        $option = self::SESSION_PREFIX . md5($session);
        $record = get_option($option, []);
        $record = is_array($record) ? $record : [];
        $entries = isset($record['Entries']) && is_array($record['Entries']) ? $record['Entries'] : [];
        $entries[] = self::sanitizeValue([
            'type' => sanitize_key($type),
            'time' => gmdate('c'),
            'detail' => $detail,
        ], '', 0);
        if (count($entries) > self::MAX_ENTRIES) {
            $entries = array_slice($entries, -self::MAX_ENTRIES);
        }

        $meta = [
            'Source' => sanitize_key($source),
            'PageSlug' => sanitize_title($slug),
            'PluginVersion' => class_exists('Hangar18_Manager') ? sanitize_text_field((string) \Hangar18_Manager::VERSION) : '',
            'UserId' => get_current_user_id(),
        ];
        update_option($option, [
            'SchemaVersion' => 1,
            'Session' => $session,
            'CreatedUtc' => (string) ($record['CreatedUtc'] ?? gmdate('c')),
            'UpdatedUtc' => gmdate('c'),
            'Meta' => array_filter(array_merge(isset($record['Meta']) && is_array($record['Meta']) ? $record['Meta'] : [], $meta), static fn($value): bool => $value !== '' && $value !== 0),
            'Entries' => $entries,
        ], false);
        self::touchIndex($session, $meta, count($entries));
    }

    private static function touchIndex(string $session, array $meta, int $count): void
    {
        $raw = get_option(self::INDEX_OPTION, []);
        $index = is_array($raw) ? array_values(array_filter($raw, 'is_array')) : [];
        $index = array_values(array_filter($index, static fn(array $item): bool => (string) ($item['Session'] ?? '') !== $session));
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

    /** @param mixed $raw */
    private static function sessionId($raw): string
    {
        $value = strtolower((string) wp_unslash($raw));
        $value = preg_replace('/[^a-z0-9._-]/', '', $value);
        return is_string($value) ? substr($value, 0, 100) : '';
    }

    /** @return mixed */
    private static function sanitizeValue($value, string $key, int $depth)
    {
        if ($depth > 7) {
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
                if (++$limit > 300) {
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
            $string = preg_replace('/(Bearer\s+)[A-Za-z0-9._~+\/-]+/i', '$1[REDACTED]', $string);
            $string = preg_replace('/((?:token|nonce|password|secret|cookie|authorization)\s*[=:]\s*)[^\s,;]+/i', '$1[REDACTED]', (string) $string);
            return substr(sanitize_text_field((string) $string), 0, 4000);
        }
        return '[unsupported]';
    }
}
