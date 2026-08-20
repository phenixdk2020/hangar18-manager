<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Backup/SiteBackupManifestService.php';
require_once dirname(__DIR__, 2) . '/src/Backup/SiteBackupManifestValidator.php';

use Hangar18\UltimateDesigner\Backup\SiteBackupManifestService;
use Hangar18\UltimateDesigner\Backup\SiteBackupManifestValidator;

function b2aAssert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$service = new SiteBackupManifestService();
b2aAssert($service->nextBackupId([]) === 'H18-BACKUP-000001', 'First backup ID must start at 000001.');
b2aAssert($service->nextBackupId(['H18-BACKUP-000001','junk','H18-BACKUP-000009']) === 'H18-BACKUP-000010', 'Backup ID must advance past highest valid numeric ID.');

$payloadsA = [
    'managed-site' => ['pages' => [['slug'=>'hjem','id'=>9]], 'design' => ['width'=>90]],
    'page-versions' => ['hjem' => [['Version'=>4,'Hash'=>'abc']]],
    'site-builder' => ['header'=>'legacy-header-a','footer'=>'legacy-footer-a','menus'=>[]],
    'forms-polls-data' => ['forms'=>[],'polls'=>['demo'=>3]],
    'plugin-metadata' => ['plugin'=>'hangar18-manager','runtime'=>'shadow'],
];
// Same semantics, deliberately different associative key order.
$payloadsB = [
    'plugin-metadata' => ['runtime'=>'shadow','plugin'=>'hangar18-manager'],
    'forms-polls-data' => ['polls'=>['demo'=>3],'forms'=>[]],
    'site-builder' => ['menus'=>[],'footer'=>'legacy-footer-a','header'=>'legacy-header-a'],
    'page-versions' => ['hjem' => [['Hash'=>'abc','Version'=>4]]],
    'managed-site' => ['design'=>['width'=>90],'pages'=>[['id'=>9,'slug'=>'hjem']]],
];
$media = [[
    'MediaId'=>44,
    'RelativePath'=>'2026/08/banner.jpg',
    'Bytes'=>123456,
    'Sha256'=>str_repeat('a',64),
    'MimeType'=>'image/jpeg',
    'Role'=>'original',
    'Derivatives'=>[[
        'RelativePath'=>'2026/08/banner.jpg.h18.webp',
        'Bytes'=>54321,
        'Sha256'=>str_repeat('b',64),
        'MimeType'=>'image/webp',
    ]],
]];

$manifestA = $service->build(
    'H18-BACKUP-000010',
    '2026-08-19T19:30:00Z',
    '0.8.15',
    ['HomeUrl'=>'https://hangar18.dk/','SiteUrl'=>'https://hangar18.dk'],
    $payloadsA,
    $media
);
$manifestB = $service->build(
    'H18-BACKUP-000010',
    '2026-08-19T19:30:00Z',
    '0.8.15',
    ['SiteUrl'=>'https://hangar18.dk/','HomeUrl'=>'https://hangar18.dk'],
    $payloadsB,
    $media
);

b2aAssert(($manifestA['SchemaVersion'] ?? '') === '1.0', 'Manifest schema must be explicit.');
b2aAssert(($manifestA['BackupId'] ?? '') === 'H18-BACKUP-000010', 'Manifest backup ID must be immutable input ID.');
b2aAssert(preg_match('/^[a-f0-9]{64}$/', (string) ($manifestA['ManifestSha256'] ?? '')) === 1, 'Manifest must carry SHA-256.');
b2aAssert(($manifestA['SourceSite']['Host'] ?? '') === 'hangar18.dk', 'Source host must be included.');
b2aAssert(($manifestA['SourceSite']['IdentitySha256'] ?? '') === ($manifestB['SourceSite']['IdentitySha256'] ?? ''), 'Site identity must be canonical/order-independent.');
b2aAssert(($manifestA['ManifestSha256'] ?? '') === ($manifestB['ManifestSha256'] ?? ''), 'Canonical manifest hash must not depend on associative input order.');
b2aAssert(($manifestA['Capabilities']['FullRestore'] ?? true) === false, 'B2-A must not advertise full restore.');
b2aAssert(($manifestA['Capabilities']['ZipExport'] ?? true) === false, 'B2-A must not advertise ZIP export.');

$validator = new SiteBackupManifestValidator();
$report = $validator->validate($manifestA, $payloadsA);
b2aAssert(($report['Valid'] ?? false) === true, 'Fresh manifest must validate.');
b2aAssert(($report['Warnings'] ?? []) === [], 'Complete B2-A logical payload scope should have no missing-payload warnings.');
b2aAssert(($report['DryRunOnly'] ?? false) === true, 'Validator must explicitly be dry-run only.');

$tamperedPayloads = $payloadsA;
$tamperedPayloads['managed-site']['pages'][0]['slug'] = 'tampered';
$tampered = $validator->validate($manifestA, $tamperedPayloads);
b2aAssert(($tampered['Valid'] ?? true) === false, 'Payload checksum drift must fail validation.');
b2aAssert((bool) array_filter($tampered['Errors'] ?? [], static fn(string $e): bool => str_contains($e, 'SHA-256 mismatch')), 'Checksum mismatch must be explicit.');

$tamperedManifest = $manifestA;
$tamperedManifest['PluginVersion'] = '0.8.99';
$tamperedManifestReport = $validator->validate($tamperedManifest, $payloadsA);
b2aAssert(($tamperedManifestReport['Valid'] ?? true) === false, 'Manifest mutation must invalidate ManifestSha256.');

$blockedPath = false;
try {
    $service->build(
        'H18-BACKUP-000011',
        '2026-08-19T19:31:00Z',
        '0.8.15',
        ['HomeUrl'=>'https://hangar18.dk','SiteUrl'=>'https://hangar18.dk'],
        $payloadsA,
        [['RelativePath'=>'../wp-config.php','Sha256'=>str_repeat('c',64)]]
    );
} catch (RuntimeException $error) {
    $blockedPath = true;
}
b2aAssert($blockedPath, 'Unsafe media path must be rejected during manifest build.');

$duplicatePath = false;
try {
    $service->build(
        'H18-BACKUP-000012',
        '2026-08-19T19:32:00Z',
        '0.8.15',
        ['HomeUrl'=>'https://hangar18.dk','SiteUrl'=>'https://hangar18.dk'],
        $payloadsA,
        [
            ['RelativePath'=>'2026/08/a.jpg','Sha256'=>str_repeat('d',64)],
            ['RelativePath'=>'2026/08/A.JPG','Sha256'=>str_repeat('e',64)],
        ]
    );
} catch (RuntimeException $error) {
    $duplicatePath = true;
}
b2aAssert($duplicatePath, 'Case-insensitive duplicate media paths must be rejected.');

fwrite(STDOUT, "B2-A versioned backup manifest/checksum dry-run: PASS\n");
