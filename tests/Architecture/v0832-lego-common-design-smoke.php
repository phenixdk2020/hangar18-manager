<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Editor\LegoDesignModel;

require_once dirname(__DIR__, 2) . '/src/Editor/LegoDesignModel.php';

function h18DesignAssert(bool $ok, string $message): void
{
    if (!$ok) {
        throw new RuntimeException($message);
    }
}

$defaults = LegoDesignModel::defaults();
h18DesignAssert(LegoDesignModel::SCHEMA_VERSION >= 1, 'Design schema must remain additive from v1.');
h18DesignAssert(($defaults['SchemaVersion'] ?? 0) === LegoDesignModel::SCHEMA_VERSION, 'Default design state must advertise the current schema version.');
h18DesignAssert(($defaults['Mode'] ?? '') === 'Global', 'Default design mode must inherit Global.');
h18DesignAssert(($defaults['Colors']['Background'] ?? '') === '#ffffff', 'Default background mismatch.');
h18DesignAssert(($defaults['Radius']['TopLeft'] ?? 0) === -1, 'Per-corner radius must inherit with -1.');
h18DesignAssert(($defaults['Typography']['BodyFont'] ?? '') === 'Global', 'Body font must inherit global by default.');
h18DesignAssert(($defaults['States']['Hover']['Mode'] ?? '') === 'Inherit', 'Hover must inherit normal state by default.');

$legacy = [
    'DesignMode' => 'Custom',
    'CustomBackgroundColor' => '#112233',
    'CustomTextColor' => '#445566',
    'CustomHeadingColor' => '#778899',
    'BorderWidthPx' => 6,
    'CustomBorderColor' => '#aabbcc',
    'RadiusPx' => 18,
    'RadiusTopLeftPx' => 0,
    'RadiusTopRightPx' => 5,
    'RadiusBottomRightPx' => 9,
    'RadiusBottomLeftPx' => -1,
    'SectionBodyFontFamily' => 'Georgia',
    'SectionHeadingFontFamily' => 'Segoe UI',
    'BodyFontSizePx' => 21,
    'H1FontSizePx' => 54,
    'H2FontSizePx' => 42,
    'H3FontSizePx' => 31,
    'SectionOpacityPercent' => 87,
    'ShadowStyle' => 'Strong',
    'HoverStyleMode' => 'Custom',
    'HoverBackgroundColor' => '#010203',
    'HoverTextColor' => '#040506',
    'HoverHeadingColor' => '#070809',
    'HoverBorderColor' => '#0a0b0c',
    'HoverOpacityPercent' => 73,
    'HoverEffect' => 'Lift',
    'HoverTransitionMs' => 340,
];

$state = LegoDesignModel::fromLegacy($legacy);
h18DesignAssert(($state['Mode'] ?? '') === 'Custom', 'Custom mode must be preserved.');
h18DesignAssert(($state['Colors']['Background'] ?? '') === '#112233', 'Background color must map into canonical state.');
h18DesignAssert(($state['Border']['Width'] ?? 0) === 6, 'Border width mapping failed.');
h18DesignAssert(($state['Radius']['BottomLeft'] ?? 0) === -1, 'Inherited corner sentinel must be preserved.');
h18DesignAssert(($state['Typography']['BodyFont'] ?? '') === 'Georgia', 'Body font mapping failed.');
h18DesignAssert(($state['Effects']['Shadow'] ?? '') === 'Strong', 'Shadow mapping failed.');
h18DesignAssert(($state['States']['Hover']['Effect'] ?? '') === 'Lift', 'Hover effect mapping failed.');

$roundTrip = LegoDesignModel::toLegacy($state);
foreach (LegoDesignModel::legacyFieldMap() as $path => $field) {
    h18DesignAssert(array_key_exists($field, $roundTrip), 'Missing legacy roundtrip field: ' . $field . ' (' . $path . ')');
}
h18DesignAssert(($roundTrip['CustomBackgroundColor'] ?? '') === '#112233', 'Roundtrip background failed.');
h18DesignAssert(($roundTrip['HoverTransitionMs'] ?? 0) === 340, 'Roundtrip hover transition failed.');

$bad = LegoDesignModel::fromLegacy([
    'DesignMode' => 'Nope',
    'CustomBackgroundColor' => 'javascript:red',
    'BorderWidthPx' => 999,
    'RadiusTopLeftPx' => -9,
    'SectionBodyFontFamily' => 'Unknown Font',
    'BodyFontSizePx' => 999,
    'ShadowStyle' => 'Huge',
    'SectionOpacityPercent' => -5,
    'HoverEffect' => 'Spin',
    'HoverTransitionMs' => 99999,
]);
h18DesignAssert(($bad['Mode'] ?? '') === 'Global', 'Invalid mode must fall back.');
h18DesignAssert(($bad['Colors']['Background'] ?? '') === '#ffffff', 'Invalid color must fall back.');
h18DesignAssert(($bad['Border']['Width'] ?? 0) === 12, 'Border width must clamp to legacy maximum.');
h18DesignAssert(($bad['Radius']['TopLeft'] ?? 0) === -1, 'Corner radius must clamp to -1 minimum.');
h18DesignAssert(($bad['Typography']['BodyFont'] ?? '') === 'Global', 'Invalid font must fall back to Global.');
h18DesignAssert(($bad['Typography']['BodySize'] ?? 0) === 32, 'Body font size must clamp.');
h18DesignAssert(($bad['Effects']['Shadow'] ?? '') === 'None', 'Invalid shadow must fall back.');
h18DesignAssert(($bad['Effects']['Opacity'] ?? -1) === 0, 'Opacity must clamp.');
h18DesignAssert(($bad['States']['Hover']['Effect'] ?? '') === 'None', 'Invalid hover effect must fall back.');
h18DesignAssert(($bad['States']['Hover']['TransitionMs'] ?? 0) === 1000, 'Hover transition must clamp.');

echo "v0.8.32 LEGO common design model smoke: PASS\n";
