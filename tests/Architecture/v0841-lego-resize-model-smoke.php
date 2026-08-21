<?php

declare(strict_types=1);

require_once __DIR__ . '/../../src/Editor/LegoLayoutSpanModel.php';

use Hangar18\UltimateDesigner\Editor\LegoLayoutSpanModel;

$defaults = LegoLayoutSpanModel::defaults();
if (($defaults['SchemaVersion'] ?? null) !== 2) {
    throw new RuntimeException('Unexpected LEGO span schema version.');
}
if (($defaults['Desktop']['Span'] ?? null) !== 0) {
    throw new RuntimeException('Desktop default must remain Auto span 0.');
}
if (($defaults['Tablet']['InheritDesktop'] ?? null) !== true || ($defaults['Mobile']['InheritDesktop'] ?? null) !== true) {
    throw new RuntimeException('Tablet/Mobile defaults must continue to inherit Desktop.');
}
if (($defaults['Tablet']['HasOverride'] ?? null) !== false || ($defaults['Mobile']['HasOverride'] ?? null) !== false) {
    throw new RuntimeException('Responsive defaults must not invent overrides.');
}

$normalized = LegoLayoutSpanModel::normalize([
    'Desktop' => ['Span' => 8],
    'Tablet' => ['InheritDesktop' => false, 'HasOverride' => true, 'Span' => 4],
    'Mobile' => ['InheritDesktop' => false, 'HasOverride' => true, 'Span' => 2],
]);
if (($normalized['Desktop']['Span'] ?? null) !== 8) {
    throw new RuntimeException('Desktop explicit span was not preserved.');
}
if (LegoLayoutSpanModel::effectiveSpan($normalized, 'Tablet') !== 4 || LegoLayoutSpanModel::effectiveSpan($normalized, 'Mobile') !== 2) {
    throw new RuntimeException('Responsive explicit spans were not preserved.');
}

$inherit = LegoLayoutSpanModel::setInheritance($normalized, 'Tablet', true);
if (LegoLayoutSpanModel::effectiveSpan($inherit, 'Tablet') !== 8) {
    throw new RuntimeException('Tablet inheritance must resolve to Desktop.');
}
if (($inherit['Tablet']['Span'] ?? null) !== 4 || ($inherit['Tablet']['HasOverride'] ?? null) !== true) {
    throw new RuntimeException('Tablet inheritance must preserve the stored override snapshot.');
}

$clamped = LegoLayoutSpanModel::normalize(['Desktop' => ['Span' => 99]]);
if (($clamped['Desktop']['Span'] ?? null) !== 12) {
    throw new RuntimeException('Span must clamp to 12.');
}
$auto = LegoLayoutSpanModel::normalize(['Desktop' => ['Span' => -5]]);
if (($auto['Desktop']['Span'] ?? null) !== 0) {
    throw new RuntimeException('Non-positive span must normalize to Auto 0.');
}

echo "v0.8.41 LEGO resize model smoke on schema 2: PASS\n";
