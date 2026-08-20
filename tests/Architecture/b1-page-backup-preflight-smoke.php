<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestorePreflightService;

$GLOBALS['b1pf_tmp'] = sys_get_temp_dir() . '/h18-b1pf-' . bin2hex(random_bytes(4));

function sanitize_file_name(string $value): string { return basename(str_replace('..', '', $value)); }
function sanitize_title(string $value): string
{
    $value = strtolower(trim($value));
    $value = preg_replace('/[^a-z0-9-]+/', '-', $value) ?? '';
    return trim($value, '-');
}
function absint($value): int { return abs((int) $value); }
function trailingslashit(string $value): string { return rtrim($value, '/\\') . DIRECTORY_SEPARATOR; }
function wp_upload_dir(): array { return ['basedir'=>$GLOBALS['b1pf_tmp'],'error'=>'']; }

function b1pfAssert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}
function b1pfWrite(string $filename, array $payload): void
{
    $dir = $GLOBALS['b1pf_tmp'] . '/hangar18-manager-backups';
    if (!is_dir($dir)) { mkdir($dir, 0777, true); }
    file_put_contents($dir . '/' . $filename, json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
}

require_once dirname(__DIR__, 2) . '/src/Backup/ManagedPageBackupRestorePreflightService.php';

$legacyEditor = 'Hangar18-Web-Backup-20260819-130000-Post-9.json';
b1pfWrite($legacyEditor, [
    'post'=>[
        'ID'=>9,
        'post_name'=>'hjem',
        'post_content'=>'<!-- HANGAR18-PAGE-EDITOR-DATA:YWJj -->[hangar18_page_editor slug="hjem"]',
    ],
]);

$legacyPlain = 'Hangar18-Web-Backup-20260819-130001-Post-10.json';
b1pfWrite($legacyPlain, [
    'post'=>[
        'ID'=>10,
        'post_name'=>'kontakt',
        'post_content'=>'<h1>Kontakt</h1><p>Legacy indhold uden Page Editor.</p>',
    ],
]);

$fullEditor = 'Hangar18-Web-Full-Backup-20260819-130002.json';
b1pfWrite($fullEditor, [
    'page_editor'=>[
        'hjem'=>['ContentVersion'=>4,'Sections'=>[['Key'=>'hero']]],
    ],
    'posts'=>[[
        'ID'=>9,
        'post_name'=>'hjem',
        'post_content'=>'<!-- HANGAR18-PAGE-EDITOR-DATA:YWJj -->[hangar18_page_editor slug="hjem"]',
    ]],
]);

$service = new ManagedPageBackupRestorePreflightService();
$blocked = $service->analyzeReplace($legacyEditor, '9');
b1pfAssert(($blocked['Allowed'] ?? true) === false, 'Editor backup without central store must be blocked for replace-original.');
b1pfAssert(($blocked['EditorDataSource'] ?? '') === 'embedded-marker-only', 'Blocked legacy editor source must be explicit.');

$plain = $service->analyzeReplace($legacyPlain, 'kontakt');
b1pfAssert(($plain['Allowed'] ?? false) === true, 'Plain legacy page does not require central Page Editor store.');
b1pfAssert(($plain['EditorDataSource'] ?? '') === 'not-required', 'Plain legacy page source must be explicit.');

$full = $service->analyzeReplace($fullEditor, 'hjem');
b1pfAssert(($full['Allowed'] ?? false) === true, 'Full backup with matching central editor store must be allowed.');
b1pfAssert(($full['HasPageEditorStoreEntry'] ?? false) === true, 'Full backup must detect exact slug editor store entry.');

$invalid = false;
try { $service->analyzeReplace('../wp-config.php', 'hjem'); } catch (RuntimeException $error) { $invalid = true; }
b1pfAssert($invalid, 'Invalid/path traversal backup filename must be rejected.');

fwrite(STDOUT, "B1 legacy editor restore preflight: PASS\n");

function b1pfCleanup(string $path): void
{
    if (!is_dir($path)) { return; }
    foreach (array_diff(scandir($path) ?: [], ['.','..']) as $item) {
        $child = $path . DIRECTORY_SEPARATOR . $item;
        if (is_dir($child)) { b1pfCleanup($child); } else { @unlink($child); }
    }
    @rmdir($path);
}
b1pfCleanup($GLOBALS['b1pf_tmp']);
