<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestoreService;
use Hangar18\UltimateDesigner\Backup\ManagedPageTrashService;
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
    public const VERSION = '0.8.41-test';
    public const PAGE_EDITOR_OPTION = 'hangar18_manager_pages_v1';
}

$GLOBALS['pd_tmp'] = sys_get_temp_dir() . '/h18-page-delete-' . bin2hex(random_bytes(4));
$GLOBALS['pd_pages'] = [];
$GLOBALS['pd_options'] = [];
$GLOBALS['pd_thumbnails'] = [];

function pdAssert(bool $condition, string $message): void
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
function wp_upload_dir(): array { return ['basedir' => $GLOBALS['pd_tmp'], 'error' => '']; }
function wp_mkdir_p(string $dir): bool { return is_dir($dir) || mkdir($dir, 0777, true); }
function wp_json_encode($value, int $flags = 0): string|false { return json_encode($value, $flags); }
function get_option(string $name, $default = false) { return $GLOBALS['pd_options'][$name] ?? $default; }
function update_option(string $name, $value, bool $autoload = false): bool { $GLOBALS['pd_options'][$name] = $value; return true; }
function get_current_user_id(): int { return 42; }
function is_wp_error($value): bool { return $value instanceof WP_Error; }
function get_post(int $id): ?WP_Post { return $GLOBALS['pd_pages'][$id] ?? null; }
function get_page_by_path(string $slug, string $output = OBJECT, string $postType = 'page'): ?WP_Post
{
    foreach ($GLOBALS['pd_pages'] as $post) {
        if ($post instanceof WP_Post && $post->post_type === $postType && $post->post_name === $slug) {
            return $post;
        }
    }
    return null;
}
function get_post_thumbnail_id(int $id): int { return (int) ($GLOBALS['pd_thumbnails'][$id] ?? 0); }
function set_post_thumbnail(int $postId, int $attachmentId): bool { $GLOBALS['pd_thumbnails'][$postId] = $attachmentId; return true; }
function delete_post_thumbnail(int $postId): bool { unset($GLOBALS['pd_thumbnails'][$postId]); return true; }
function wp_update_post(array $data, bool $wpError = false)
{
    $id = (int) ($data['ID'] ?? 0);
    $post = $GLOBALS['pd_pages'][$id] ?? null;
    if (!$post instanceof WP_Post) { return $wpError ? new WP_Error('missing post') : 0; }
    foreach (['post_title','post_status','post_parent','post_excerpt','post_content'] as $field) {
        if (array_key_exists($field, $data)) { $post->{$field} = $data[$field]; }
    }
    return $id;
}
function wp_insert_post(array $data, bool $wpError = false)
{
    return $wpError ? new WP_Error('not used') : 0;
}
function wp_delete_post(int $id, bool $force = false): ?WP_Post
{
    throw new RuntimeException('PAGE-DELETE-001 must never permanently delete a page.');
}
function wp_trash_post(int $id): ?WP_Post
{
    $post = $GLOBALS['pd_pages'][$id] ?? null;
    if (!$post instanceof WP_Post) { return null; }
    $post->post_status = 'trash';
    return $post;
}

require_once dirname(__DIR__, 2) . '/src/Backup/ManagedPageTrashService.php';
require_once dirname(__DIR__, 2) . '/src/Backup/ManagedPageBackupRestoreService.php';

wp_mkdir_p($GLOBALS['pd_tmp'] . '/hangar18-manager-backups');

$page = new WP_Post([
    'ID' => 55,
    'post_type' => 'page',
    'post_title' => 'Midlertidig testside',
    'post_name' => 'midlertidig-testside',
    'post_status' => 'publish',
    'post_excerpt' => 'før trash',
    'post_content' => '<!-- current -->[hangar18_page_editor slug="midlertidig-testside"]',
]);
$GLOBALS['pd_pages'][55] = $page;
$GLOBALS['pd_options'][Hangar18_Manager::PAGE_EDITOR_OPTION] = [
    'midlertidig-testside' => ['ContentVersion' => 12, 'Sections' => [['Key' => 'keep-me']]],
];

$service = new ManagedPageTrashService();

// Wrong title must reject before backup or mutation.
$blocked = false;
try {
    $service->trashBySlug('midlertidig-testside', 'Forkert titel', 42);
} catch (RuntimeException $error) {
    $blocked = true;
}
pdAssert($blocked, 'Wrong confirmation title must be rejected.');
pdAssert($GLOBALS['pd_pages'][55]->post_status === 'publish', 'Rejected confirmation must not trash page.');
pdAssert(count(glob($GLOBALS['pd_tmp'] . '/hangar18-manager-backups/*.json') ?: []) === 0, 'Rejected confirmation must not create a backup.');

// Protected core routes must reject regardless of title.
$GLOBALS['pd_pages'][9] = new WP_Post([
    'ID' => 9,
    'post_title' => 'Hjem',
    'post_name' => 'hjem',
    'post_status' => 'publish',
]);
$protectedBlocked = false;
try {
    $service->trashBySlug('hjem', 'Hjem', 42);
} catch (RuntimeException $error) {
    $protectedBlocked = true;
}
pdAssert($protectedBlocked, 'Protected core page must be blocked.');
pdAssert($GLOBALS['pd_pages'][9]->post_status === 'publish', 'Protected core page must remain published.');

// Successful deletion means WordPress Trash, never permanent deletion.
$result = $service->trashBySlug('midlertidig-testside', 'Midlertidig testside', 42);
pdAssert(($result['PageId'] ?? 0) === 55, 'Audit result must bind page ID.');
pdAssert(($result['Title'] ?? '') === 'Midlertidig testside', 'Audit result must bind page title.');
pdAssert(($result['UserId'] ?? 0) === 42, 'Audit result must bind user ID.');
pdAssert(($result['PreviousStatus'] ?? '') === 'publish', 'Audit must record previous status.');
pdAssert($GLOBALS['pd_pages'][55]->post_status === 'trash', 'Successful delete must move page to WordPress Trash.');
pdAssert(isset($GLOBALS['pd_options'][Hangar18_Manager::PAGE_EDITOR_OPTION]['midlertidig-testside']), 'Trash must not erase editor state.');

$safety = (string) ($result['SafetyBackup'] ?? '');
pdAssert($safety !== '', 'Trash must report a safety backup.');
$safetyPath = $GLOBALS['pd_tmp'] . '/hangar18-manager-backups/' . $safety;
pdAssert(is_file($safetyPath), 'Safety backup must physically exist before/after Trash.');
$payload = json_decode((string) file_get_contents($safetyPath), true);
pdAssert(($payload['post']['ID'] ?? 0) === 55, 'Safety backup must contain page ID.');
pdAssert(($payload['post']['post_status'] ?? '') === 'publish', 'Safety backup must contain pre-trash status.');
pdAssert(($payload['page_editor']['midlertidig-testside']['ContentVersion'] ?? 0) === 12, 'Safety backup must contain page editor state.');
pdAssert(str_contains((string) ($payload['reason'] ?? ''), 'PAGE-DELETE-001'), 'Safety backup must identify page-delete reason.');

$audit = $service->audit();
pdAssert(count($audit) === 1, 'Only successful Trash action must be audited.');
pdAssert(($audit[0]['Mode'] ?? '') === 'trash-page', 'Audit mode must be trash-page.');
pdAssert(($audit[0]['SafetyBackup'] ?? '') === $safety, 'Audit must bind safety backup filename.');
pdAssert((string) ($audit[0]['Utc'] ?? '') !== '', 'Audit must include UTC timestamp.');

// Existing B1 restore must be able to reactivate the same trashed page safely.
$GLOBALS['pd_pages'][55]->post_title = 'Trashed title changed';
$GLOBALS['pd_pages'][55]->post_content = '<!-- trashed changed -->';
$GLOBALS['pd_options'][Hangar18_Manager::PAGE_EDITOR_OPTION]['midlertidig-testside'] = [
    'ContentVersion' => 99,
    'Sections' => [['Key' => 'changed-after-trash']],
];
$restore = (new ManagedPageBackupRestoreService())->restoreOriginal($safety, '55');
pdAssert(($restore['TargetPageId'] ?? 0) === 55, 'B1 restore must target original trashed page ID.');
pdAssert($GLOBALS['pd_pages'][55]->post_status === 'publish', 'B1 restore must restore pre-trash publish status.');
pdAssert($GLOBALS['pd_pages'][55]->post_title === 'Midlertidig testside', 'B1 restore must restore original title.');
pdAssert(str_contains($GLOBALS['pd_pages'][55]->post_content, '<!-- current -->'), 'B1 restore must restore original content.');
pdAssert(($GLOBALS['pd_options'][Hangar18_Manager::PAGE_EDITOR_OPTION]['midlertidig-testside']['ContentVersion'] ?? 0) === 12, 'B1 restore must restore original editor state.');

fwrite(STDOUT, "PAGE-DELETE-001 trash + backup + B1 restore: PASS\n");

function pdCleanup(string $path): void
{
    if (!is_dir($path)) { return; }
    foreach (array_diff(scandir($path) ?: [], ['.','..']) as $item) {
        $child = $path . DIRECTORY_SEPARATOR . $item;
        if (is_dir($child)) { pdCleanup($child); } else { @unlink($child); }
    }
    @rmdir($path);
}
pdCleanup($GLOBALS['pd_tmp']);
