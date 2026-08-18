<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';

\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Compatibility\MarkupComparator;
use Hangar18\UltimateDesigner\Compatibility\StateComparator;

function comparatorAssert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new \RuntimeException($message);
    }
}

$stateComparator = new StateComparator();
$baseline = [
    'Version' => '1.22',
    'PageSlug' => 'hjem',
    'Sections' => [
        ['Key' => 'one', 'Type' => 'text', 'LayoutParentKey' => ''],
    ],
];

$equal = $stateComparator->compare($baseline, $baseline);
comparatorAssert($equal->equivalent(), 'Identical state must compare as equivalent.');
comparatorAssert($equal->differences() === [], 'Equivalent state must have no differences.');

$changed = $baseline;
$changed['Sections'][0]['Type'] = 'image';
$notEqual = $stateComparator->compare($baseline, $changed);
comparatorAssert(!$notEqual->equivalent(), 'Changed state must not compare as equivalent.');
comparatorAssert($notEqual->differences() !== [], 'Changed state must report differences.');

$markupComparator = new MarkupComparator();
$vehicleMarkup = '<div class="h18-vehicle-register"><article class="h18-vehicle-card"></article></div>';
$markupEqual = $markupComparator->compare(
    $vehicleMarkup,
    str_replace("\n", "\r\n", $vehicleMarkup),
    ['h18-vehicle-register', 'h18-vehicle-card']
);
comparatorAssert($markupEqual->equivalent(), 'Line-ending-only differences must normalize away.');

$markupChanged = $markupComparator->compare(
    $vehicleMarkup,
    '<div class="new-register"></div>',
    ['h18-vehicle-register', 'h18-vehicle-card']
);
comparatorAssert(!$markupChanged->equivalent(), 'Missing protected hooks must fail compatibility.');
comparatorAssert(count($markupChanged->differences()) >= 2, 'Missing protected hooks must be reported.');

fwrite(STDOUT, "Compatibility comparator smoke test: PASS\n");
