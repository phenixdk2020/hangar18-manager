<?php

declare(strict_types=1);

namespace VisualDesignerManager\Modules;

final class ModuleStore
{
    public const POST_TYPE = 'h18_module_item';
    public const META_MODULE = '_h18_module_key';
    public const META_RECORD = '_h18_module_record_v1';
    public const META_RECORD_ID = '_h18_module_record_id';
    public const META_DIGEST = '_h18_module_digest';
    public const META_STATUS = '_h18_module_status';
    public const META_SORT = '_h18_module_sort_order';

    public static function register(): void
    {
        add_action('init', [self::class, 'registerPostType']);
    }

    public static function registerPostType(): void
    {
        if (post_type_exists(self::POST_TYPE)) {
            return;
        }
        register_post_type(self::POST_TYPE, [
            'labels' => [
                'name' => 'Visual Designer Data',
                'singular_name' => 'Visual Designer Datarecord',
            ],
            'public' => false,
            'publicly_queryable' => false,
            'exclude_from_search' => true,
            'show_ui' => false,
            'show_in_menu' => false,
            'show_in_rest' => false,
            'rewrite' => false,
            'query_var' => false,
            'supports' => ['title'],
            'map_meta_cap' => true,
            'capability_type' => 'page',
        ]);
    }

    /**
     * @param array<string,mixed> $raw
     * @return int|\WP_Error
     */
    public static function save(string $module, array $raw, int $postId = 0)
    {
        if (!current_user_can('edit_pages')) {
            return self::error('h18_module_forbidden', 'Du har ikke rettigheder til at ændre moduldata.');
        }

        $module = ModuleRegistry::key($module);
        if (!ModuleRegistry::supports($module)) {
            return self::error('h18_module_unknown', 'Ukendt modultype.');
        }

        $existing = $postId > 0 ? self::get($postId) : null;
        if ($postId > 0 && $existing === null) {
            return self::error('h18_module_missing', 'Modulrecorden findes ikke.');
        }
        if ($existing !== null && (string) ($existing['module'] ?? '') !== $module) {
            return self::error('h18_module_mismatch', 'Modulrecordens type kan ikke ændres.');
        }

        $now = gmdate('c');
        if ($existing !== null) {
            $raw['id'] = (string) ($existing['id'] ?? ($raw['id'] ?? ''));
            $raw['createdAt'] = (string) ($existing['createdAt'] ?? $now);
        } else {
            if (empty($raw['id'])) {
                $raw['id'] = function_exists('wp_generate_uuid4') ? wp_generate_uuid4() : uniqid($module . '-', true);
            }
            $raw['createdAt'] = $raw['createdAt'] ?? $now;
        }
        $raw['updatedAt'] = $now;

        $record = ModuleRecord::normalize($module, $raw);
        if ($record === [] || (string) ($record['id'] ?? '') === '') {
            return self::error('h18_module_invalid', 'Modulrecorden kunne ikke normaliseres.');
        }

        $definition = ModuleRegistry::definition($module);
        $fallbackTitle = is_array($definition) ? (string) ($definition['singular'] ?? 'Datarecord') : 'Datarecord';
        $title = (string) ($record['title'] ?? '');
        if ($title === '') {
            $title = $fallbackTitle;
        }

        $post = [
            'post_type' => self::POST_TYPE,
            'post_status' => 'publish',
            'post_title' => $title,
            'post_name' => (string) ($record['slug'] ?? ''),
        ];
        if ($postId > 0) {
            $post['ID'] = $postId;
            $result = wp_update_post($post, true);
        } else {
            $result = wp_insert_post($post, true);
        }
        if (is_wp_error($result)) {
            return $result;
        }

        $postId = (int) $result;
        $json = ModuleRecord::canonicalJson($record);
        update_post_meta($postId, self::META_MODULE, $module);
        update_post_meta($postId, self::META_RECORD, $json);
        update_post_meta($postId, self::META_RECORD_ID, (string) ($record['id'] ?? ''));
        update_post_meta($postId, self::META_DIGEST, hash('sha256', $json));
        update_post_meta($postId, self::META_STATUS, (string) ($record['status'] ?? 'draft'));
        update_post_meta($postId, self::META_SORT, (int) ($record['sortOrder'] ?? 0));
        clean_post_cache($postId);

        return $postId;
    }

    /** @return array<string,mixed>|null */
    public static function get(int $postId): ?array
    {
        if ($postId <= 0 || get_post_type($postId) !== self::POST_TYPE) {
            return null;
        }
        $module = ModuleRegistry::key((string) get_post_meta($postId, self::META_MODULE, true));
        if (!ModuleRegistry::supports($module)) {
            return null;
        }
        $json = (string) get_post_meta($postId, self::META_RECORD, true);
        if ($json === '') {
            return null;
        }
        $raw = json_decode($json, true);
        if (!is_array($raw)) {
            return null;
        }
        $record = ModuleRecord::normalize($module, $raw);
        return $record === [] ? null : $record;
    }

    /**
     * @param array<string,mixed> $args
     * @return array<int,array{postId:int,record:array<string,mixed>}>
     */
    public static function listRecords(string $module, array $args = []): array
    {
        $module = ModuleRegistry::key($module);
        if (!ModuleRegistry::supports($module)) {
            return [];
        }

        $status = strtolower((string) ($args['status'] ?? 'publish'));
        if (!in_array($status, ['draft', 'publish', 'archive', 'all'], true)) {
            $status = 'publish';
        }
        $limit = is_numeric($args['limit'] ?? null) ? (int) $args['limit'] : 50;
        $limit = max(1, min(100, $limit));
        $orderBy = (string) ($args['orderBy'] ?? 'sortOrder');
        if (!in_array($orderBy, ['sortOrder', 'title', 'updatedAt'], true)) {
            $orderBy = 'sortOrder';
        }
        $order = strtoupper((string) ($args['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';

        $metaQuery = [
            ['key' => self::META_MODULE, 'value' => $module, 'compare' => '='],
        ];
        if ($status !== 'all') {
            $metaQuery[] = ['key' => self::META_STATUS, 'value' => $status, 'compare' => '='];
        }

        $ids = get_posts([
            'post_type' => self::POST_TYPE,
            'post_status' => 'publish',
            'fields' => 'ids',
            'posts_per_page' => $limit,
            'no_found_rows' => true,
            'suppress_filters' => true,
            'meta_query' => $metaQuery,
        ]);
        $out = [];
        foreach ((array) $ids as $id) {
            $record = self::get((int) $id);
            if ($record !== null) {
                $out[] = ['postId' => (int) $id, 'record' => $record];
            }
        }

        usort($out, static function (array $a, array $b) use ($orderBy, $order): int {
            $left = $a['record'];
            $right = $b['record'];
            if ($orderBy === 'title') {
                $cmp = strnatcasecmp((string) ($left['title'] ?? ''), (string) ($right['title'] ?? ''));
            } elseif ($orderBy === 'updatedAt') {
                $cmp = strcmp((string) ($left['updatedAt'] ?? ''), (string) ($right['updatedAt'] ?? ''));
            } else {
                $cmp = ((int) ($left['sortOrder'] ?? 0)) <=> ((int) ($right['sortOrder'] ?? 0));
                if ($cmp === 0) {
                    $cmp = strnatcasecmp((string) ($left['title'] ?? ''), (string) ($right['title'] ?? ''));
                }
            }
            return $order === 'DESC' ? -$cmp : $cmp;
        });

        return array_slice($out, 0, $limit);
    }

    /** @return array{postId:int,record:array<string,mixed>}|null */
    public static function findByRecordId(string $module, string $recordId): ?array
    {
        $module = ModuleRegistry::key($module);
        $recordId = strtolower(trim($recordId));
        if (!ModuleRegistry::supports($module) || !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) {
            return null;
        }
        $ids = get_posts([
            'post_type' => self::POST_TYPE,
            'post_status' => 'publish',
            'fields' => 'ids',
            'posts_per_page' => 1,
            'no_found_rows' => true,
            'suppress_filters' => true,
            'meta_query' => [
                ['key' => self::META_MODULE, 'value' => $module, 'compare' => '='],
                ['key' => self::META_RECORD_ID, 'value' => $recordId, 'compare' => '='],
            ],
        ]);
        if (is_array($ids) && !empty($ids)) {
            $postId = (int) $ids[0];
            $record = self::get($postId);
            return $record !== null ? ['postId' => $postId, 'record' => $record] : null;
        }
        // Compatibility fallback for any records written by the v0.1.67 foundation
        // before META_RECORD_ID existed.
        foreach (self::listRecords($module, ['status' => 'all', 'limit' => 100]) as $item) {
            if ((string) ($item['record']['id'] ?? '') === $recordId) { return $item; }
        }
        return null;
    }

    /** @return bool|\WP_Error */
    public static function delete(int $postId)
    {
        if (!current_user_can('edit_pages')) {
            return self::error('h18_module_forbidden', 'Du har ikke rettigheder til at slette moduldata.');
        }
        if (self::get($postId) === null) {
            return self::error('h18_module_missing', 'Modulrecorden findes ikke.');
        }
        return wp_delete_post($postId, true) !== false;
    }

    /** @return \WP_Error */
    private static function error(string $code, string $message)
    {
        return new \WP_Error($code, $message);
    }

    private function __construct()
    {
    }
}
