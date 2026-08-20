<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;
use WP_Post;

/** Collects the Hangar18-owned application state for a portable B2 package. */
final class SiteBackupSnapshotCollector
{
    /** @return array{Payloads:array<string,mixed>,Media:array<int,array<string,mixed>>,MediaFiles:array<string,string>} */
    public function collect(): array
    {
        $pages = $this->managedPages();
        $options = $this->ownedOptions();
        $dataEntries = $this->dataEntries();

        $payloads = [
            'managed-site' => [
                'Pages' => $pages,
                'CapturedUtc' => gmdate('c'),
            ],
            'page-versions' => [
                'Options' => $this->selectOptions($options, static function (string $name): bool {
                    return str_contains($name, 'page_version') || str_contains($name, 'revision');
                }),
            ],
            'site-builder' => [
                'Options' => $this->selectOptions($options, static function (string $name): bool {
                    return (bool) preg_match('/(header|footer|menu|template|design|layout|pages_v1|component|preset)/', $name);
                }),
            ],
            'forms-polls-data' => [
                'Options' => $this->selectOptions($options, static function (string $name): bool {
                    return (bool) preg_match('/(form|poll|custom_data|data_type|submission)/', $name);
                }),
                'DataEntries' => $dataEntries,
            ],
            'plugin-metadata' => [
                'Options' => $options,
                'PluginVersion' => defined('Hangar18_Manager::VERSION') ? \Hangar18_Manager::VERSION : '0.0.0',
                'HomeUrl' => function_exists('home_url') ? (string) home_url('/') : '',
                'SiteUrl' => function_exists('site_url') ? (string) site_url('/') : '',
            ],
        ];

        $mediaIds = [];
        $this->collectAttachmentIds($payloads, $mediaIds, '');
        foreach ($pages as $page) {
            $featured = (int) ($page['FeaturedId'] ?? 0);
            if ($featured > 0) {
                $mediaIds[$featured] = true;
            }
        }

        [$media, $files, $mediaMap] = $this->mediaInventory(array_keys($mediaIds));
        $payloads['media-map'] = $mediaMap;

        return ['Payloads'=>$payloads, 'Media'=>$media, 'MediaFiles'=>$files];
    }

    /** @return array<int,array<string,mixed>> */
    private function managedPages(): array
    {
        if (!function_exists('get_posts')) {
            return [];
        }
        $posts = get_posts([
            'post_type'=>'page',
            'post_status'=>'any',
            'numberposts'=>-1,
            'orderby'=>'ID',
            'order'=>'ASC',
        ]);
        $fixed = ['hjem','om-foreningen','koeretoejer-og-materiel','events','billedgalleri','bliv-medlem','kontakt'];
        $result = [];
        foreach ($posts as $post) {
            if (!$post instanceof WP_Post) {
                continue;
            }
            $content = (string) $post->post_content;
            $slug = sanitize_title((string) $post->post_name);
            $managed = in_array($slug, $fixed, true)
                || strpos($content, 'HANGAR18-') !== false
                || stripos($content, '[hangar18_') !== false;
            if (!$managed) {
                continue;
            }
            $result[] = [
                'ID'=>(int)$post->ID,
                'Title'=>(string)$post->post_title,
                'Slug'=>$slug,
                'Status'=>(string)$post->post_status,
                'ParentId'=>(int)$post->post_parent,
                'Excerpt'=>(string)$post->post_excerpt,
                'Content'=>$content,
                'FeaturedId'=>function_exists('get_post_thumbnail_id') ? (int)get_post_thumbnail_id($post->ID) : 0,
                'Meta'=>$this->postMeta((int)$post->ID),
            ];
        }
        return $result;
    }

    /** @return array<string,mixed> */
    private function ownedOptions(): array
    {
        $names = [];
        global $wpdb;
        if (isset($wpdb) && is_object($wpdb) && isset($wpdb->options) && method_exists($wpdb, 'get_col')) {
            $likeA = method_exists($wpdb, 'esc_like') ? $wpdb->esc_like('hangar18_') . '%' : 'hangar18_%';
            $likeB = method_exists($wpdb, 'esc_like') ? $wpdb->esc_like('h18_') . '%' : 'h18_%';
            if (method_exists($wpdb, 'prepare')) {
                $query = $wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s", $likeA, $likeB);
                $rows = $wpdb->get_col($query);
                if (is_array($rows)) {
                    $names = array_map('strval', $rows);
                }
            }
        }

        $known = [
            'hangar18_manager_pages_v1','hangar18_manager_page_versions_v1','hangar18_manager_page_presets_v1',
            'hangar18_manager_page_components_v1','hangar18_manager_page_templates_v1','hangar18_manager_header_design_v25',
            'hangar18_manager_menu_order_v20','hangar18_manager_active_menu','hangar18_manager_form_submissions_v1',
            'hangar18_manager_poll_votes_v1','hangar18_manager_custom_data_types_v1','hangar18_manager_site_templates_v1',
            'hangar18_manager_site_template_assignments_v1','hangar18_manager_site_menus_v1','hangar18_ud_asset_metadata_v1',
        ];
        $names = array_values(array_unique(array_merge($names, $known)));
        sort($names, SORT_STRING);

        $result = [];
        foreach ($names as $name) {
            if (!$this->isPortableOption($name) || !function_exists('get_option')) {
                continue;
            }
            $missing = new \stdClass();
            $value = get_option($name, $missing);
            if ($value === $missing) {
                continue;
            }
            $result[$name] = $value;
        }
        return $result;
    }

    private function isPortableOption(string $name): bool
    {
        if (!(str_starts_with($name, 'hangar18_') || str_starts_with($name, 'h18_'))) {
            return false;
        }
        // Restore coordination/audit/catalog state is operational, not portable
        // application state. In particular, including a stale restore lock in
        // currentStateHash() would make its own recovery invalidate the dry-run.
        return !preg_match('/(_transient|update_lock|update_state|notice_|backup_restore_audit|site_backup_catalog|site_backup_restore)/', $name);
    }

    /** @param array<string,mixed> $options @return array<string,mixed> */
    private function selectOptions(array $options, callable $predicate): array
    {
        $result = [];
        foreach ($options as $name=>$value) {
            if ($predicate((string)$name)) {
                $result[(string)$name] = $value;
            }
        }
        return $result;
    }

    /** @return array<int,array<string,mixed>> */
    private function dataEntries(): array
    {
        if (!function_exists('get_posts')) {
            return [];
        }
        $posts = get_posts(['post_type'=>'h18_data_entry','post_status'=>'any','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC']);
        $result = [];
        foreach ($posts as $post) {
            if (!$post instanceof WP_Post) {
                continue;
            }
            $result[] = [
                'ID'=>(int)$post->ID,
                'Title'=>(string)$post->post_title,
                'Status'=>(string)$post->post_status,
                'Content'=>(string)$post->post_content,
                'Excerpt'=>(string)$post->post_excerpt,
                'Meta'=>$this->postMeta((int)$post->ID),
            ];
        }
        return $result;
    }

    /** @return array<string,mixed> */
    private function postMeta(int $postId): array
    {
        if (!function_exists('get_post_meta')) {
            return [];
        }
        $all = get_post_meta($postId);
        if (!is_array($all)) {
            return [];
        }
        $result = [];
        foreach ($all as $key=>$values) {
            $key = (string)$key;
            if (str_starts_with($key, '_edit_') || in_array($key, ['_wp_old_slug'], true)) {
                continue;
            }
            $decoded = [];
            foreach ((array)$values as $value) {
                // get_post_meta() already returns WordPress-decoded values.
                $decoded[] = $value;
            }
            $result[$key] = count($decoded) === 1 ? $decoded[0] : $decoded;
        }
        ksort($result, SORT_STRING);
        return $result;
    }

    /** @param mixed $value @param array<int,bool> $ids */
    private function collectAttachmentIds($value, array &$ids, string $key): void
    {
        if (is_array($value)) {
            foreach ($value as $childKey=>$child) {
                $this->collectAttachmentIds($child, $ids, (string)$childKey);
            }
            return;
        }
        if (!is_int($value) && !(is_string($value) && ctype_digit($value))) {
            return;
        }
        $id = (int)$value;
        if ($id <= 0 || isset($ids[$id])) {
            return;
        }
        $likely = (bool)preg_match('/(media|image|attachment|featured|logo|icon|background|thumbnail)/i', $key);
        if (!$likely || !function_exists('get_post')) {
            return;
        }
        $post = get_post($id);
        if ($post instanceof WP_Post && $post->post_type === 'attachment') {
            $ids[$id] = true;
        }
    }

    /** @param array<int,int|string> $ids @return array{0:array<int,array<string,mixed>>,1:array<string,string>,2:array<int,array<string,mixed>>} */
    private function mediaInventory(array $ids): array
    {
        $uploads = function_exists('wp_upload_dir') ? wp_upload_dir() : [];
        $baseDir = empty($uploads['basedir']) ? '' : rtrim((string)$uploads['basedir'], '/\\');
        $baseUrl = empty($uploads['baseurl']) ? '' : rtrim((string)$uploads['baseurl'], '/');
        $manifest = [];
        $files = [];
        $map = [];

        foreach ($ids as $rawId) {
            $id = (int)$rawId;
            if ($id <= 0 || !function_exists('get_attached_file')) {
                continue;
            }
            $path = (string)get_attached_file($id);
            if ($path === '' || !is_file($path) || $baseDir === '') {
                continue;
            }
            $realBase = realpath($baseDir);
            $realPath = realpath($path);
            if ($realBase === false || $realPath === false) {
                continue;
            }
            $prefix = rtrim($realBase, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR;
            if (strpos($realPath, $prefix) !== 0) {
                continue;
            }
            $relative = str_replace(DIRECTORY_SEPARATOR, '/', substr($realPath, strlen($prefix)));
            $sha = hash_file('sha256', $realPath);
            if (!is_string($sha)) {
                throw new RuntimeException('Kunne ikke beregne SHA-256 for media ID ' . $id . '.');
            }
            $mime = function_exists('get_post_mime_type') ? (string)get_post_mime_type($id) : '';
            $derivatives = $this->derivatives($id, $realBase, $relative);
            $manifest[] = [
                'MediaId'=>$id,
                'RelativePath'=>$relative,
                'Bytes'=>(int)filesize($realPath),
                'Sha256'=>$sha,
                'MimeType'=>$mime,
                'Role'=>'original',
                'Derivatives'=>array_map(static function (array $item): array {
                    return [
                        'RelativePath'=>$item['RelativePath'],
                        'Bytes'=>$item['Bytes'],
                        'Sha256'=>$item['Sha256'],
                        'MimeType'=>$item['MimeType'],
                    ];
                }, $derivatives),
            ];
            $files[$relative] = $realPath;
            foreach ($derivatives as $item) {
                $files[(string)$item['RelativePath']] = (string)$item['SourcePath'];
            }
            $url = $baseUrl !== '' ? $baseUrl . '/' . $relative : '';
            $map[$id] = ['MediaId'=>$id,'RelativePath'=>$relative,'Url'=>$url,'Sha256'=>$sha,'MimeType'=>$mime];
        }
        usort($manifest, static fn(array $a,array $b): int => ((int)$a['MediaId']) <=> ((int)$b['MediaId']));
        ksort($files, SORT_STRING);
        ksort($map, SORT_NUMERIC);
        return [$manifest,$files,$map];
    }

    /** @return array<int,array<string,mixed>> */
    private function derivatives(int $id, string $baseDir, string $relativeOriginal): array
    {
        $paths = [];
        if (function_exists('wp_get_attachment_metadata')) {
            $meta = wp_get_attachment_metadata($id);
            $dir = dirname($relativeOriginal);
            if (is_array($meta) && isset($meta['sizes']) && is_array($meta['sizes'])) {
                foreach ($meta['sizes'] as $size) {
                    if (is_array($size) && !empty($size['file'])) {
                        $paths[] = ($dir === '.' ? '' : $dir . '/') . basename((string)$size['file']);
                    }
                }
            }
        }
        $originalAbs = $baseDir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relativeOriginal);
        $root = preg_replace('/\.[^.]+$/', '', $originalAbs) ?: $originalAbs;
        foreach ([$root . '.h18.webp', $root . '.h18.avif'] as $candidate) {
            if (is_file($candidate)) {
                $paths[] = str_replace(DIRECTORY_SEPARATOR, '/', substr($candidate, strlen(rtrim($baseDir, DIRECTORY_SEPARATOR)) + 1));
            }
        }
        $paths = array_values(array_unique($paths));
        $result = [];
        foreach ($paths as $relative) {
            $abs = $baseDir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative);
            if (!is_file($abs)) {
                continue;
            }
            $sha = hash_file('sha256', $abs);
            if (!is_string($sha)) {
                continue;
            }
            $mime = function_exists('wp_check_filetype') ? (string)((wp_check_filetype($abs)['type'] ?? '')) : '';
            $result[] = ['RelativePath'=>$relative,'SourcePath'=>$abs,'Bytes'=>(int)filesize($abs),'Sha256'=>$sha,'MimeType'=>$mime];
        }
        return $result;
    }
}
