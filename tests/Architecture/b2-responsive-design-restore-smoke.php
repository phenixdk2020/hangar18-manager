<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Backup\SiteBackupPackageService;
use Hangar18\UltimateDesigner\Backup\SiteBackupRestoreCoordinator;

// Reuse the complete B2 WordPress/package/restore harness first. It leaves the
// mock WordPress state/functions available after cleaning its temporary files.
require_once __DIR__ . '/b2-package-restore-smoke.php';

wp_mkdir_p($GLOBALS['b2_tmp'] . '/uploads');

$option = 'hangar18_ultimate_designer_lego_design_responsive_v1';
$baselineResponsive = [
    'hjem'=>[
        'SchemaVersion'=>1,
        'Sections'=>[
            'text-1'=>[
                'SchemaVersion'=>1,
                'Tablet'=>['InheritDesktop'=>false,'HasOverride'=>true,'Design'=>['SchemaVersion'=>1,'Mode'=>'Custom','Colors'=>['Background'=>'#224466']]],
                'Mobile'=>['InheritDesktop'=>true,'HasOverride'=>false,'Design'=>['SchemaVersion'=>1,'Mode'=>'Global']],
            ],
        ],
    ],
    'kontakt'=>[
        'SchemaVersion'=>1,
        'Sections'=>[
            'contact-1'=>[
                'SchemaVersion'=>1,
                'Tablet'=>['InheritDesktop'=>true,'HasOverride'=>false,'Design'=>['SchemaVersion'=>1,'Mode'=>'Global']],
                'Mobile'=>['InheritDesktop'=>false,'HasOverride'=>true,'Design'=>['SchemaVersion'=>1,'Mode'=>'Custom','Colors'=>['Background'=>'#335577']]],
            ],
        ],
    ],
];
$GLOBALS['b2_options'][$option] = $baselineResponsive;

$packagesResponsive = new SiteBackupPackageService();
$createdResponsive = $packagesResponsive->create('v0.8.33 responsive design baseline');
$backupId = (string)($createdResponsive['BackupId'] ?? '');
b2Assert($backupId !== '', 'Responsive design backup must be created.');

$GLOBALS['b2_options'][$option]['hjem']['Sections']['text-1']['Tablet']['Design']['Colors']['Background'] = '#999999';
$GLOBALS['b2_options'][$option]['kontakt']['Sections']['contact-1']['Mobile']['Design']['Colors']['Background'] = '#abcdef';
$contactMustStay = $GLOBALS['b2_options'][$option]['kontakt'];

$coordinatorResponsive = new SiteBackupRestoreCoordinator($packagesResponsive);
$planResponsive = $coordinatorResponsive->plan($backupId, 'page', 'hjem');
b2Assert(($planResponsive['Executable'] ?? false) === true, 'Responsive selective restore dry-run must be executable.');
$resultResponsive = $coordinatorResponsive->restorePage((string)$planResponsive['Token']);

b2Assert(($resultResponsive['LegoResponsiveDesignRestored'] ?? false) === true, 'Selective restore must report responsive LEGO design restore.');
b2Assert(
    b2CanonicalEqual($GLOBALS['b2_options'][$option]['hjem'], $baselineResponsive['hjem']),
    'Selective restore must restore only the selected page responsive design state.'
);
b2Assert(
    b2CanonicalEqual($GLOBALS['b2_options'][$option]['kontakt'], $contactMustStay),
    'Selective restore must preserve another page responsive design state.'
);

fwrite(STDOUT, "B2 selective responsive LEGO design restore: PASS\n");
b2Cleanup($GLOBALS['b2_tmp']);
