<?php

declare(strict_types=1);

require_once __DIR__ . '/../../src/Editor/LegoLayoutSpanModel.php';

use Hangar18\UltimateDesigner\Editor\LegoLayoutSpanModel;

$defaults = LegoLayoutSpanModel::defaults();
if (($defaults['SchemaVersion'] ?? null) !== 1) {
    throw new RuntimeException('Unexpected LEGO span schema version.');
}
if (($defaults['Desktop']['Span'] ?? null) !== 0) {
    throw new RuntimeException('Desktop default must remain Auto span 0.');
}
if (($defaults['Tablet']['InheritDesktop'] ?? null) !== true || ($defaults['Mobile']['InheritDesktop'] ?? null) !== true) {
    throw new RuntimeException('Tablet/Mobile must inherit Desktop in LEGO-032.');
}

$normalized = LegoLayoutSpanModel::normalize([
    'Desktop' => ['Span' => 8],
    'Tablet' => ['InheritDesktop' => false, 'Span' => 4],
    'Mobile' => ['InheritDesktop' => false, 'Span' => 2],
]);
if (($normalized['Desktop']['Span'] ?? null) !== 8) {
    throw new RuntimeException('Desktop explicit span was not preserved.');
}
if (($normalized['Tablet']['InheritDesktop'] ?? null) !== true || ($normalized['Mobile']['InheritDesktop'] ?? null) !== true) {
    throw new RuntimeException('LEGO-032 must force responsive inheritance until LEGO-033.');
}
if (LegoLayoutSpanModel::effectiveSpan($normalized, 'Tablet') !== 8 || LegoLayoutSpanModel::effectiveSpan($normalized, 'Mobile') !== 8) {
    throw new RuntimeException('Responsive effective span must inherit Desktop.');
}

$clamped = LegoLayoutSpanModel::normalize(['Desktop' => ['Span' => 99]]);
if (($clamped['Desktop']['Span'] ?? null) !== 12) {
    throw new RuntimeException('Span must clamp to 12.');
}
$auto = LegoLayoutSpanModel::normalize(['Desktop' => ['Span' => -5]]);
if (($auto['Desktop']['Span'] ?? null) !== 0) {
    throw new RuntimeException('Non-positive span must normalize to Auto 0.');
}

echo "v0.8.41 LEGO resize model smoke: PASS\n";
