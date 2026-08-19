<?php

declare(strict_types=1);

require_once __DIR__ . '/../../src/SiteBuilder/LegacyShellSnapshotService.php';

use Hangar18\UltimateDesigner\SiteBuilder\LegacyShellSnapshotService;

function h18_assert(bool $condition, string $message): void
{
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$service = new LegacyShellSnapshotService();
$content = '<p>before</p>'
    . LegacyShellSnapshotService::HEADER_START . '<header>Legacy header</header>' . LegacyShellSnapshotService::HEADER_END
    . '<main>page</main>'
    . LegacyShellSnapshotService::FOOTER_START . '<footer>Legacy footer</footer>' . LegacyShellSnapshotService::FOOTER_END
    . '<p>after</p>';

$first = $service->build(['SecondaryColor' => '#525a5f', 'PrimaryColor' => '#30382a'], $content, '0.8.7');
$second = $service->build(['PrimaryColor' => '#30382a', 'SecondaryColor' => '#525a5f'], $content, '0.8.7');

h18_assert($first['HeaderMarkerComplete'] === true, 'Header marker should be complete.');
h18_assert($first['FooterMarkerComplete'] === true, 'Footer marker should be complete.');
h18_assert($first['ReadyForShadowImport'] === true, 'Complete shell should be eligible as a shadow import source.');
h18_assert($first['DesignKeyCount'] === 2, 'Design key count should reflect legacy option payload.');
h18_assert($first['SourceHash'] === $second['SourceHash'], 'Source hash must be deterministic regardless of associative key order.');
h18_assert(strpos((string) $first['HeaderHtml'], 'Legacy header') !== false, 'Header block must be preserved.');
h18_assert(strpos((string) $first['FooterHtml'], 'Legacy footer') !== false, 'Footer block must be preserved.');

$missingFooter = $service->build(['PrimaryColor' => '#30382a'], LegacyShellSnapshotService::HEADER_START . '<header>x</header>' . LegacyShellSnapshotService::HEADER_END, '0.8.7');
h18_assert($missingFooter['HeaderMarkerComplete'] === true, 'Header-only source should still identify its header.');
h18_assert($missingFooter['FooterMarkerComplete'] === false, 'Missing footer must be detected.');
h18_assert($missingFooter['ReadyForShadowImport'] === false, 'Incomplete shell must block shadow import.');

$changed = $service->build(['PrimaryColor' => '#000000', 'SecondaryColor' => '#525a5f'], $content, '0.8.7');
h18_assert($changed['SourceHash'] !== $first['SourceHash'], 'A legacy design change must change SourceHash.');

echo "v0.8.8 legacy shell shadow smoke: PASS\n";
