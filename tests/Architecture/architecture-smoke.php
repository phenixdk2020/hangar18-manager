<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';

\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Compatibility\CompatibilityPolicy;
use Hangar18\UltimateDesigner\Contracts\ElementDefinition;
use Hangar18\UltimateDesigner\Contracts\PropertyDefinition;
use Hangar18\UltimateDesigner\Contracts\SchemaMigration;
use Hangar18\UltimateDesigner\Core\Architecture;
use Hangar18\UltimateDesigner\Core\Version;
use Hangar18\UltimateDesigner\Migration\MigrationRegistry;

function assertTrue(bool $condition, string $message): void
{
    if (!$condition) {
        throw new \RuntimeException($message);
    }
}

$architecture = new Architecture();

$element = new class implements ElementDefinition {
    public function type(): string { return 'test_element'; }
    public function label(): string { return 'Test element'; }
    public function defaults(): array { return ['title' => '']; }
    public function schema(): array { return ['type' => 'object']; }
    public function propertyKeys(): array { return ['layout.width']; }
};

$property = new class implements PropertyDefinition {
    public function key(): string { return 'layout.width'; }
    public function label(): string { return 'Width'; }
    public function control(): string { return 'dimension'; }
    public function schema(): array { return ['type' => ['string', 'number']]; }
    public function defaultValue() { return 'auto'; }
};

$architecture->elements()->register($element);
$architecture->properties()->register($property);

assertTrue($architecture->elements()->has('test_element'), 'Element registry lookup failed.');
assertTrue($architecture->properties()->has('layout.width'), 'Property registry lookup failed.');
assertTrue(Version::RUNTIME === '0.5.30', 'Legacy runtime version guard changed unexpectedly.');
assertTrue(Version::PAGE_SCHEMA === '1.22', 'Page schema guard changed unexpectedly.');

foreach (['vehicle', 'event', 'gallery'] as $domain) {
    assertTrue(CompatibilityPolicy::mustUseLegacyRuntime($domain), "Protected domain '{$domain}' lost its legacy-runtime guard.");
}
assertTrue(!CompatibilityPolicy::mustUseLegacyRuntime('generic'), 'Generic domains must not be forced onto the legacy runtime.');

$duplicateRejected = false;
try {
    $architecture->elements()->register($element);
} catch (\RuntimeException $exception) {
    $duplicateRejected = true;
}
assertTrue($duplicateRejected, 'Element registry must reject duplicate element types.');

$migrations = new MigrationRegistry();
$migrations->register(new class implements SchemaMigration {
    public function fromVersion(): string { return '1.20'; }
    public function toVersion(): string { return '1.21'; }
    public function migrate(array $state): array { $state['migration'][] = '1.21'; return $state; }
});
$migrations->register(new class implements SchemaMigration {
    public function fromVersion(): string { return '1.21'; }
    public function toVersion(): string { return '1.22'; }
    public function migrate(array $state): array { $state['migration'][] = '1.22'; return $state; }
});

$migrated = $migrations->migrate(['migration' => []], '1.20', '1.22');
assertTrue($migrated['migration'] === ['1.21', '1.22'], 'Schema migrations must execute deterministically in sequence.');

$missingPathRejected = false;
try {
    $migrations->migrate([], '1.19', '1.22');
} catch (\RuntimeException $exception) {
    $missingPathRejected = true;
}
assertTrue($missingPathRejected, 'Migration registry must reject an incomplete migration path.');

require __DIR__ . '/i10-decision-packet-smoke.php';
require __DIR__ . '/i10-decision-packet-fingerprint-smoke.php';

fwrite(STDOUT, "Architecture foundation smoke test: PASS\n");
