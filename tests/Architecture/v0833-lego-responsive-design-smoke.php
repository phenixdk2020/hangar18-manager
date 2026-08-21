<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Editor\LegoDesignModel;
use Hangar18\UltimateDesigner\Editor\LegoResponsiveDesignModel;

require_once dirname(__DIR__, 2) . '/src/Editor/LegoDesignModel.php';
require_once dirname(__DIR__, 2) . '/src/Editor/LegoResponsiveDesignModel.php';

function h18ResponsiveDesignAssert(bool $ok, string $message): void
{
    if (!$ok) {
        throw new RuntimeException($message);
    }
}

$desktopA = LegoDesignModel::fromLegacy([
    'DesignMode'=>'Custom',
    'CustomBackgroundColor'=>'#112233',
    'CustomTextColor'=>'#eeeeee',
    'RadiusPx'=>14,
    'HoverEffect'=>'Lift',
]);

$state = LegoResponsiveDesignModel::defaults($desktopA);
h18ResponsiveDesignAssert(($state['SchemaVersion'] ?? 0) === 1, 'Responsive design schema must be v1.');
h18ResponsiveDesignAssert(($state['Tablet']['InheritDesktop'] ?? false) === true, 'Tablet must inherit Desktop by default.');
h18ResponsiveDesignAssert(($state['Mobile']['InheritDesktop'] ?? false) === true, 'Mobile must inherit Desktop by default.');
h18ResponsiveDesignAssert(($state['Tablet']['HasOverride'] ?? true) === false, 'Tablet must not pretend to own an override before first edit.');
h18ResponsiveDesignAssert(($state['Mobile']['HasOverride'] ?? true) === false, 'Mobile must not pretend to own an override before first edit.');

$effective = LegoResponsiveDesignModel::effective($state, $desktopA, 'Tablet');
h18ResponsiveDesignAssert(($effective['Inherited'] ?? false) === true, 'Inherited Tablet must report inherited state.');
h18ResponsiveDesignAssert(($effective['Design']['Colors']['Background'] ?? '') === '#112233', 'Tablet must use current Desktop background while inherited.');

$desktopB = LegoDesignModel::fromLegacy([
    'DesignMode'=>'Custom',
    'CustomBackgroundColor'=>'#445566',
    'CustomTextColor'=>'#ffffff',
    'RadiusPx'=>22,
    'HoverEffect'=>'Shadow',
]);
$state = LegoResponsiveDesignModel::setInheritance($state, $desktopB, 'Tablet', false);
h18ResponsiveDesignAssert(($state['Tablet']['InheritDesktop'] ?? true) === false, 'Tablet inheritance must turn off.');
h18ResponsiveDesignAssert(($state['Tablet']['HasOverride'] ?? false) === true, 'First explicit Tablet state must become an override.');
h18ResponsiveDesignAssert(($state['Tablet']['Design']['Colors']['Background'] ?? '') === '#445566', 'First override must seed from CURRENT Desktop, not stale Desktop.');
h18ResponsiveDesignAssert(($state['Tablet']['Design']['Radius']['All'] ?? 0) === 22, 'First override must seed current Desktop radius.');

$state['Tablet']['Design']['Colors']['Background'] = '#abcdef';
$state['Tablet']['Design']['States']['Hover']['Effect'] = 'Scale';
$state = LegoResponsiveDesignModel::normalize($state, $desktopB);
$state = LegoResponsiveDesignModel::setInheritance($state, $desktopB, 'Tablet', true);
h18ResponsiveDesignAssert(($state['Tablet']['Design']['Colors']['Background'] ?? '') === '#abcdef', 'Turning inheritance on must not delete Tablet override.');
$desktopC = LegoDesignModel::fromLegacy(['DesignMode'=>'Custom','CustomBackgroundColor'=>'#010203']);
$effective = LegoResponsiveDesignModel::effective($state, $desktopC, 'Tablet');
h18ResponsiveDesignAssert(($effective['Design']['Colors']['Background'] ?? '') === '#010203', 'Inherited Tablet must remain a live view of changed Desktop.');

$state = LegoResponsiveDesignModel::setInheritance($state, $desktopC, 'Tablet', false);
$effective = LegoResponsiveDesignModel::effective($state, $desktopC, 'Tablet');
h18ResponsiveDesignAssert(($effective['Inherited'] ?? true) === false, 'Tablet override must reactivate.');
h18ResponsiveDesignAssert(($effective['Design']['Colors']['Background'] ?? '') === '#abcdef', 'Previous Tablet override must return after inheritance is disabled.');
h18ResponsiveDesignAssert(($effective['Design']['States']['Hover']['Effect'] ?? '') === 'Scale', 'Previous Tablet hover override must survive inheritance cycle.');

$mobile = [
    'SchemaVersion'=>1,
    'Mobile'=>[
        'InheritDesktop'=>false,
        'HasOverride'=>true,
        'Design'=>LegoDesignModel::fromLegacy(['DesignMode'=>'Custom','CustomBackgroundColor'=>'#fedcba','BodyFontSizePx'=>19]),
    ],
];
$mobile = LegoResponsiveDesignModel::normalize($mobile, $desktopC);
h18ResponsiveDesignAssert(($mobile['Mobile']['Design']['Colors']['Background'] ?? '') === '#fedcba', 'Existing Mobile override must normalize without visual drift.');
h18ResponsiveDesignAssert(($mobile['Mobile']['Design']['Typography']['BodySize'] ?? 0) === 19, 'Mobile typography override must be preserved.');

echo "v0.8.33 LEGO responsive design model smoke: PASS\n";
