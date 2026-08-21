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
                'Tablet'=>[
                    'InheritDesktop'=>false,
                    'HasOverride'=>true,
                    'InteractionHasOverride'=>true,
                    'InteractionHasSnapshot'=>true,
                    'Design'=>[
                        'SchemaVersion'=>2,
                        'Mode'=>'Custom',
                        'Colors'=>['Background'=>'#224466'],
                        'Motion'=>['Transition'=>'Fast'],
                        'States'=>[
                            'Focus'=>['Style'=>'Custom','Color'=>'#654321','Width'=>6,'Offset'=>3],
                            'Active'=>['Effect'=>'Press'],
                            'Disabled'=>['Opacity'=>37],
                        ],
                    ],
                ],
                'Mobile'=>[
                    'InheritDesktop'=>true,
                    'HasOverride'=>false,
                    'InteractionHasOverride'=>false,
                    'InteractionHasSnapshot'=>true,
                    'Design'=>[
                        'SchemaVersion'=>2,
                        'Mode'=>'Global',
                        'Motion'=>['Transition'=>'Slow'],
                        'States'=>[
                            'Focus'=>['Style'=>'Custom','Color'=>'#123456','Width'=>4,'Offset'=>2],
                            'Active'=>['Effect'=>'ScaleDown'],
                            'Disabled'=>['Opacity'=>44],
                        ],
                    ],
                ],
            ],
        ],
    ],
    'kontakt'=>[
        'SchemaVersion'=>1,
        'Sections'=>[
            'contact-1'=>[
                'SchemaVersion'=>1,
                'Tablet'=>['InheritDesktop'=>true,'HasOverride'=>false,'InteractionHasOverride'=>false,'InteractionHasSnapshot'=>false,'Design'=>['SchemaVersion'=>2,'Mode'=>'Global']],
                'Mobile'=>[
                    'InheritDesktop'=>false,
                    'HasOverride'=>true,
                    'InteractionHasOverride'=>true,
                    'InteractionHasSnapshot'=>true,
                    'Design'=>[
                        'SchemaVersion'=>2,
                        'Mode'=>'Custom',
                        'Colors'=>['Background'=>'#335577'],
                        'Motion'=>['Transition'=>'Normal'],
                        'States'=>[
                            'Focus'=>['Style'=>'None','Color'=>'#8b4a2b','Width'=>3,'Offset'=>2],
                            'Active'=>['Effect'=>'Press'],
                            'Disabled'=>['Opacity'=>52],
                        ],
                    ],
                ],
            ],
        ],
    ],
];
$GLOBALS['b2_options'][$option] = $baselineResponsive;

$packagesResponsive = new SiteBackupPackageService();
$createdResponsive = $packagesResponsive->create('v0.8.34 responsive design + interaction baseline');
$backupId = (string)($createdResponsive['BackupId'] ?? '');
b2Assert($backupId !== '', 'Responsive design backup must be created.');

$GLOBALS['b2_options'][$option]['hjem']['Sections']['text-1']['Tablet']['Design']['Colors']['Background'] = '#999999';
$GLOBALS['b2_options'][$option]['hjem']['Sections']['text-1']['Tablet']['Design']['States']['Focus']['Color'] = '#ffffff';
$GLOBALS['b2_options'][$option]['hjem']['Sections']['text-1']['Mobile']['InteractionHasSnapshot'] = false;
$GLOBALS['b2_options'][$option]['kontakt']['Sections']['contact-1']['Mobile']['Design']['Colors']['Background'] = '#abcdef';
$GLOBALS['b2_options'][$option]['kontakt']['Sections']['contact-1']['Mobile']['Design']['States']['Disabled']['Opacity'] = 88;
$contactMustStay = $GLOBALS['b2_options'][$option]['kontakt'];

$coordinatorResponsive = new SiteBackupRestoreCoordinator($packagesResponsive);
$planResponsive = $coordinatorResponsive->plan($backupId, 'page', 'hjem');
b2Assert(($planResponsive['Executable'] ?? false) === true, 'Responsive selective restore dry-run must be executable.');
$resultResponsive = $coordinatorResponsive->restorePage((string)$planResponsive['Token']);

b2Assert(($resultResponsive['LegoResponsiveDesignRestored'] ?? false) === true, 'Selective restore must report responsive LEGO design restore.');
b2Assert(
    b2CanonicalEqual($GLOBALS['b2_options'][$option]['hjem'], $baselineResponsive['hjem']),
    'Selective restore must restore selected page responsive design + interaction snapshots.'
);
b2Assert(
    b2CanonicalEqual($GLOBALS['b2_options'][$option]['kontakt'], $contactMustStay),
    'Selective restore must preserve another page responsive design + interaction state.'
);

fwrite(STDOUT, "B2 selective responsive LEGO design + interaction restore: PASS\n");
b2Cleanup($GLOBALS['b2_tmp']);
