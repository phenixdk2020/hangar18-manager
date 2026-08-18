<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';

\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Contracts\Logger;
use Hangar18\UltimateDesigner\Contracts\PageRepository;
use Hangar18\UltimateDesigner\Contracts\SecurityGate;
use Hangar18\UltimateDesigner\Core\Architecture;
use Hangar18\UltimateDesigner\Core\RuntimeBridge;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;

function bridgeAssert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new \RuntimeException($message);
    }
}

$pages = new class implements PageRepository {
    private array $store = [];

    public function load(string $pageKey): ?array
    {
        return $this->store[$pageKey] ?? null;
    }

    public function save(string $pageKey, array $state): void
    {
        $this->store[$pageKey] = $state;
    }

    public function exists(string $pageKey): bool
    {
        return array_key_exists($pageKey, $this->store);
    }
};

$security = new class implements SecurityGate {
    public function can(string $capability): bool
    {
        return $capability === 'edit_pages';
    }

    public function validateWriteToken(string $action, string $token): bool
    {
        return $action === 'test-action' && $token === 'valid-token';
    }
};

$logger = new class implements Logger {
    /** @var list<array{0:string,1:string,2:string}> */
    public array $entries = [];

    public function log(string $level, string $checkpoint, string $message): void
    {
        $this->entries[] = [$level, $checkpoint, $message];
    }
};

$bridge = new RuntimeBridge(
    new Architecture(),
    $pages,
    $security,
    $logger,
    new PageSchemaValidator()
);

bridgeAssert($bridge->mode() === RuntimeBridge::MODE_SHADOW, 'Runtime bridge must boot in shadow mode.');

foreach (['vehicle', 'event', 'gallery'] as $domain) {
    bridgeAssert(
        $bridge->routeDomain($domain) === RuntimeBridge::ROUTE_LEGACY,
        "Protected domain '{$domain}' must remain on legacy runtime."
    );
    bridgeAssert(!$bridge->mayReplaceLegacyHandler($domain), "Protected domain '{$domain}' cannot replace legacy handlers.");
}

bridgeAssert(
    $bridge->routeDomain('generic') === RuntimeBridge::ROUTE_ARCHITECTURE_SHADOW,
    'Generic domain should be available only as architecture shadow.'
);
bridgeAssert(!$bridge->mayReplaceLegacyHandler('generic'), 'Shadow mode must not replace any legacy handler.');
bridgeAssert($bridge->security()->can('edit_pages'), 'Security adapter boundary was not exposed.');

$state = [
    'Version' => '1.22',
    'PageSlug' => 'hjem',
    'PageTitle' => 'Hjem',
    'ContentVersion' => 1,
    'DataContextType' => '',
    'DataContextEntryId' => 0,
    'Sections' => [],
];

bridgeAssert($bridge->pageSchema()->validate($state) === [], 'Compatible v0.5.30 page state must validate.');
$bridge->pages()->save('hjem', $state);
bridgeAssert($bridge->pages()->exists('hjem'), 'Page repository bridge failed.');
bridgeAssert($bridge->pages()->load('hjem') === $state, 'Page repository roundtrip changed state.');

$bridge->logger()->log('INFO', 'RUNTIME_BRIDGE_TEST', 'Shadow bridge test.');
bridgeAssert(count($logger->entries) === 1, 'Logger bridge was not exposed.');

fwrite(STDOUT, "Runtime bridge smoke test: PASS\n");
