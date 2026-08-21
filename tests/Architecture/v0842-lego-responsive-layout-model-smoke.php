<?php

declare(strict_types=1);

require_once __DIR__ . '/../../src/Editor/LegoLayoutSpanModel.php';

use Hangar18\UltimateDesigner\Editor\LegoLayoutSpanModel;

$state = LegoLayoutSpanModel::normalize([
    'Desktop' => ['Span' => 8],
]);
if (LegoLayoutSpanModel::effectiveSpan($state, 'Tablet') !== 8 || LegoLayoutSpanModel::effectiveSpan($state, 'Mobile') !== 8) {
    throw new RuntimeException('Responsive defaults must inherit Desktop span.');
}

$tablet = LegoLayoutSpanModel::setSpan($state, 'Tablet', 5);
if (($tablet['Tablet']['InheritDesktop'] ?? null) !== false || ($tablet['Tablet']['HasOverride'] ?? null) !== true) {
    throw new RuntimeException('Tablet span write must activate an override.');
}
if (LegoLayoutSpanModel::effectiveSpan($tablet, 'Tablet') !== 5 || LegoLayoutSpanModel::effectiveSpan($tablet, 'Desktop') !== 8) {
    throw new RuntimeException('Tablet override must not mutate Desktop.');
}

$tabletInherited = LegoLayoutSpanModel::setInheritance($tablet, 'Tablet', true);
if (LegoLayoutSpanModel::effectiveSpan($tabletInherited, 'Tablet') !== 8) {
    throw new RuntimeException('Inherited Tablet must return to Desktop span.');
}
if (($tabletInherited['Tablet']['Span'] ?? null) !== 5 || ($tabletInherited['Tablet']['HasOverride'] ?? null) !== true) {
    throw new RuntimeException('Enabling inheritance must preserve Tablet snapshot.');
}

$tabletRestored = LegoLayoutSpanModel::setInheritance($tabletInherited, 'Tablet', false, 7);
if (LegoLayoutSpanModel::effectiveSpan($tabletRestored, 'Tablet') !== 5) {
    throw new RuntimeException('Disabling inheritance must restore the existing Tablet snapshot.');
}

$firstMobile = LegoLayoutSpanModel::setInheritance($state, 'Mobile', false, 6);
if (($firstMobile['Mobile']['Span'] ?? null) !== 6 || ($firstMobile['Mobile']['HasOverride'] ?? null) !== true) {
    throw new RuntimeException('First Mobile override must seed from the supplied effective Desktop span.');
}
if (LegoLayoutSpanModel::effectiveSpan($firstMobile, 'Mobile') !== 6) {
    throw new RuntimeException('Seeded Mobile override was not effective.');
}

$clamped = LegoLayoutSpanModel::setSpan($state, 'Mobile', 99);
if (LegoLayoutSpanModel::effectiveSpan($clamped, 'Mobile') !== 12) {
    throw new RuntimeException('Responsive span must clamp to 12.');
}

echo "v0.8.42 LEGO responsive layout model smoke: PASS\n";
