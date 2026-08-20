<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestoreService;
use RuntimeException;

if (!defined('OBJECT')) { define('OBJECT', 'OBJECT'); }

final class WP_Post
{
    public int $ID;
    public string $post_type = 'page';
    public string $post_title = '';
    public string $post_name = '';
    public string $post_status = 'draft';
    public int $post_parent = 0;
    public string $post_excerpt = '';
    public string $post_content = '';

    public function __construct(array $data)
    {
        foreach ($data as $key => $value) {
            if (property_exists($this, (string) $key)) {
                $this->{$key} = $value;
            }
        }
    }
}

final class WP_Error
{
    public function __construct(private string $message) {}
    public function get_error_message(): string { return $this->message; }
}

final class Hangar18_Manager
{
    public const VERSION = '0.8.18-test';
    public const PAGE_EDITOR_OPTION = 'hangar18_manager_pages_v1';
}

$GLOBALS['b1_tmp'] = sys_get_temp_dir() . '/h18-b1-' . bin2hex(random_bytes(4));
$GLOBALS['b1_pages'] = [];
$GLOBALS['b1_options'] = [];
$GLOBALS['b1_thumbnails'] = [];
$GLOBALS['b1_next_id'] = 100;

function b1Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}
function trailingslashit(string $value): string { return rtrim($value, '/\\') . DIRECTORY_SEPARATOR; }
function sanitize_file_name(string $value): string { return basename(str_replace('..', '', $value)); }
function sanitize_text_field(string $value): string { return trim(strip_tags($value)); }
function sanitize_title(string $value): string
{
    $value = strtolower(trim($value));
    $value = preg_replace('/[^a-z0-9-]+/', '-', $value) ?? '';
    return trim($value, '-');
}
function sanitize_key(string $value): string { return preg_replace('/[^a-z0-9_\-]/', '', strtolower($value)) ?? ''; }
function absint($value): int { return abs((int) $value); }
function wp_upload_dir(): array { return ['basedir' => $GLOBALS['b1_tmp'], 'error' => '']; }
function wp_mkdir_p(string $dir): bool { return is_dir($dir) || mkdir($dir, 0777, true); }
function wp_json_encode($value, int $flags = 0): string|false { return json_encode($value, $flags); }
function get_option(string $name, $default = false) { return $GLOBALS['b1_options'][$name] ?? $default; }
function update_option(string $name, $value, bool $autoload = false): bool { $GLOBALS['b1_options'][$name] = $value; return true; }
function get_current_user_id(): int { return 7; }
function is_wp_error($value): bool { return $value instanceof WP_Error; }
function get_post(int $id): ?WP_Post { return $GLOBALS['b1_pages'][$id] ?? null; }
function get_page_by_path(string $slug, string $output = OBJECT, string $postType = 'page'): ?WP_Post
{
    foreach ($GLOBALS['b1_pages'] as $post) {
        if ($post instanceof WP_Post && $post->post_type === $postType && $post->post_name === $slug) { return $post; }
    }
    return null;
}
function get_post_thumbnail_id(int $id): int { return (int) ($GLOBALS['b1_thumbnails'][$id] ?? 0); }
function set_post_thumbnail(int $postId, int $attachmentId): bool { $GLOBALS['b1_thumbnails'][$postId] = $attachmentId; return true; }
function delete_post_thumbnail(int $postId): bool { unset($GLOBALS['b1_thumbnails'][$postId]); return true; }
function wp_update_post(array $data, bool $wpError = false)
{
    $id = (int) ($data['ID'] ?? 0);
    $post = $GLOBALS['b1_pages'][$id] ?? null;
    if (!$post instanceof WP_Post) { return $wpError ? new WP_Error('missing post') : 0; }
    foreach (['post_title','post_status','post_parent','post_excerpt','post_content'] as $field) {
        if (array_key_exists($field, $data)) { $post->{$field} = $data[$field]; }
    }
    return $id;
}
function wp_insert_post(array $data, bool $wpError = false)
{
    $id = $GLOBALS['b1_next_id']++;
    $post = new WP_Post([
        'ID' => $id,
        'post_type' => (string) ($data['post_type'] ?? 'post'),
        'post_title' => (string) ($data['post_title'] ?? ''),
        'post_name' => (string) ($data['post_name'] ?? ''),
        'post_status' => (string) ($data['post_status'] ?? 'draft'),
        'post_parent' => (int) ($data['post_parent'] ?? 0),
        'post_excerpt' => (string) ($data['post_excerpt'] ?? ''),
        'post_content' => (string) ($data['post_content'] ?? ''),
    ]);
    $GLOBALS['b1_pages'][$id] = $post;
    return $id;
}
function wp_delete_post(int $id, bool $force = false): ?WP_Post
{
    $post = $GLOBALS['b1_pages'][$id] ?? null;
    unset($GLOBALS['b1_pages'][$id]);
    return $post;
}

require_once dirname(__DIR__, 2) . '/src/Backup/ManagedPageBackupRestoreService.php';

wp_mkdir_p($GLOBALS['b1_tmp'] . '/hangar18-manager-backups');

$original = new WP_Post([
    'ID' => 9,
    'post_type' => 'page',
    'post_title' => 'Hjem nu',
    'post_name' => 'hjem',
    'post_status' => 'publish',
    'post_content' => '<!-- current -->[hangar18_page_editor slug="hjem"]',
]);
$GLOBALS['b1_pages'][9] = $original;
$GLOBALS['b1_options'][Hangar18_Manager::PAGE_EDITOR_OPTION] = [
    'hjem' => ['ContentVersion' => 9, 'Sections' => [['Key' => 'current']]],
];

$filename = 'Hangar18-Web-Full-Backup-20260819-120000.json';
$payload = [
    'created_utc' => '2026-08-19T12:00:00Z',
    'reason' => 'fixture',
    'plugin_version' => '0.8.15',
    'page_editor' => [
        'hjem' => ['ContentVersion' => 4, 'Sections' => [['Key' => 'backup']]],
    ],
    'posts' => [[
        'ID' => 9,
        'post_title' => 'Hjem backup',
        'post_name' => 'hjem',
        'post_status' => 'publish',
        'post_parent' => 0,
        'post_excerpt' => 'backup excerpt',
        'post_content' => '<!-- backup -->[hangar18_page_editor slug="hjem"]',
        'featured_id' => 0,
    ]],
];
file_put_contents(
    $GLOBALS['b1_tmp'] . '/hangar18-manager-backups/' . $filename,
    json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)
);

$service = new ManagedPageBackupRestoreService();
$list = $service->listBackups();
b1Assert(count($list) === 1, 'Managed backup should be discovered.');
b1Assert(($list[0]['Pages'][0]['Slug'] ?? '') === 'hjem', 'Backup page slug must be exposed.');
b1Assert(($list[0]['HasPageEditorStore'] ?? false) === true, 'Full backup must expose page editor availability.');

$beforeOriginalContent = $GLOBALS['b1_pages'][9]->post_content;
$copy = $service->createCopy($filename, '9');
$copyId = (int) ($copy['TargetPageId'] ?? 0);
b1Assert($copyId >= 100, 'Copy must create a new page ID.');
b1Assert(($copy['TargetSlug'] ?? '') === 'hjem-kopi', 'First copy slug must be hjem-kopi.');
b1Assert($GLOBALS['b1_pages'][$copyId]->post_status === 'draft', 'Copy must always be draft.');
b1Assert(str_contains($GLOBALS['b1_pages'][$copyId]->post_content, 'slug="hjem-kopi"'), 'Copy shortcode must be rebound to copy slug.');
b1Assert($GLOBALS['b1_pages'][9]->post_content === $beforeOriginalContent, 'Copy mode must not mutate original page.');
b1Assert(($GLOBALS['b1_options'][Hangar18_Manager::PAGE_EDITOR_OPTION]['hjem-kopi']['ContentVersion'] ?? 0) === 4, 'Page editor data must be rebound to copy store key.');

// A second copy proves collision-safe -kopi-N behavior.
$copy2 = $service->createCopy($filename, 'hjem');
b1Assert(($copy2['TargetSlug'] ?? '') === 'hjem-kopi-2', 'Second copy must use collision-safe -kopi-2 slug.');

// Make live original differ, then restore it from backup.
$GLOBALS['b1_pages'][9]->post_title = 'Changed live title';
$GLOBALS['b1_pages'][9]->post_content = '<!-- changed -->[hangar18_page_editor slug="hjem"]';
$GLOBALS['b1_options'][Hangar18_Manager::PAGE_EDITOR_OPTION]['hjem'] = ['ContentVersion' => 10, 'Sections' => [['Key' => 'changed']]];
$restore = $service->restoreOriginal($filename, '9');

b1Assert(($restore['TargetPageId'] ?? 0) === 9, 'Restore must preserve original page ID.');
b1Assert(($restore['TargetSlug'] ?? '') === 'hjem', 'Restore must preserve original slug.');
b1Assert($GLOBALS['b1_pages'][9]->post_name === 'hjem', 'wp_update restore must not rename original slug.');
b1Assert($GLOBALS['b1_pages'][9]->post_title === 'Hjem backup', 'Original title must be restored from backup.');
b1Assert(str_contains($GLOBALS['b1_pages'][9]->post_content, '<!-- backup -->'), 'Original content must be restored from backup.');
b1Assert(($GLOBALS['b1_options'][Hangar18_Manager::PAGE_EDITOR_OPTION]['hjem']['ContentVersion'] ?? 0) === 4, 'Original Page Editor store must be restored.');

$safety = (string) ($restore['SafetyBackup'] ?? '');
b1Assert($safety !== '', 'Replace-original must report safety backup.');
b1Assert(is_file($GLOBALS['b1_tmp'] . '/hangar18-manager-backups/' . $safety), 'Safety backup must physically exist after restore.');
$safetyPayload = json_decode((string) file_get_contents($GLOBALS['b1_tmp'] . '/hangar18-manager-backups/' . $safety), true);
b1Assert(($safetyPayload['post']['post_title'] ?? '') === 'Changed live title', 'Safety backup must contain the immediately pre-restore original.');
b1Assert(($safetyPayload['page_editor']['hjem']['ContentVersion'] ?? 0) === 10, 'Safety backup must include pre-restore Page Editor entry.');

$audit = $service->audit();
b1Assert(count($audit) === 3, 'Two copies plus one restore must be auditable.');
b1Assert(($audit[0]['Mode'] ?? '') === 'replace-original', 'Latest audit entry must be replace-original.');

$blocked = false;
try { $service->inspect('../etc/passwd'); } catch (RuntimeException $error) { $blocked = true; }
b1Assert($blocked, 'Path traversal / invalid backup filename must be rejected.');

fwrite(STDOUT, "B1 page backup restore/copy: PASS\n");

function b1Cleanup(string $path): void
{
    if (!is_dir($path)) { return; }
    foreach (array_diff(scandir($path) ?: [], ['.','..']) as $item) {
        $child = $path . DIRECTORY_SEPARATOR . $item;
        if (is_dir($child)) { b1Cleanup($child); } else { @unlink($child); }
    }
    @rmdir($path);
}
b1Cleanup($GLOBALS['b1_tmp']);
