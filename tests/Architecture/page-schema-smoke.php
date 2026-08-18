<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';

\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;

function schemaAssert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new \RuntimeException($message);
    }
}

$validator = new PageSchemaValidator();

$valid = [
    'Version' => '1.22',
    'PageSlug' => 'hjem',
    'PageTitle' => 'Hjem',
    'ContentVersion' => 1,
    'DataContextType' => '',
    'DataContextEntryId' => 0,
    'Sections' => [
        ['Key' => 'root', 'Type' => 'container', 'LayoutParentKey' => ''],
        ['Key' => 'row', 'Type' => 'grid', 'LayoutParentKey' => 'root'],
        ['Key' => 'heading', 'Type' => 'text', 'LayoutParentKey' => 'row'],
    ],
];

schemaAssert($validator->validate($valid) === [], 'A normalized v0.5.30-compatible page must validate.');

$cycle = $valid;
$cycle['Sections'][0]['LayoutParentKey'] = 'row';
schemaAssert($validator->validate($cycle) !== [], 'Layout cycles must be rejected.');

$missingParent = $valid;
$missingParent['Sections'][2]['LayoutParentKey'] = 'missing';
schemaAssert($validator->validate($missingParent) !== [], 'Missing layout parents must be rejected.');

$wrongVersion = $valid;
$wrongVersion['Version'] = '9.99';
schemaAssert($validator->validate($wrongVersion) !== [], 'Unknown schema versions must be rejected.');

fwrite(STDOUT, "Page schema smoke test: PASS\n");
