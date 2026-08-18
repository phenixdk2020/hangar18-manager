<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';

\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Compatibility\CompatibilityPolicy;
use Hangar18\UltimateDesigner\Compatibility\DomainMarkupAuditService;
use Hangar18\UltimateDesigner\Compatibility\MarkupComparator;
use Hangar18\UltimateDesigner\Compatibility\ProtectedDomainContractCatalog;
use Hangar18\UltimateDesigner\Compatibility\ShadowPageStateAuditor;
use Hangar18\UltimateDesigner\Compatibility\StateComparator;
use Hangar18\UltimateDesigner\Contracts\PageRepository;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;

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

comparatorAssert(
    ProtectedDomainContractCatalog::domains() === CompatibilityPolicy::PROTECTED_DOMAINS,
    'Protected domain catalog and runtime policy must contain exactly the same domains.'
);

foreach (ProtectedDomainContractCatalog::domains() as $domain) {
    comparatorAssert(CompatibilityPolicy::mustUseLegacyRuntime($domain), "Catalog domain '{$domain}' is not protected by runtime policy.");
    comparatorAssert(ProtectedDomainContractCatalog::slug($domain) !== '', "Catalog domain '{$domain}' has no legacy slug.");
    comparatorAssert(ProtectedDomainContractCatalog::marker($domain) !== '', "Catalog domain '{$domain}' has no legacy marker.");
    comparatorAssert(ProtectedDomainContractCatalog::adminActions($domain) !== [], "Catalog domain '{$domain}' has no admin actions.");
    comparatorAssert(ProtectedDomainContractCatalog::markupHooks($domain) !== [], "Catalog domain '{$domain}' has no markup hooks.");
}

$vehicleContractMarkup = implode('', array_map(
    static fn(string $hook): string => '<div class="' . $hook . '"></div>',
    ProtectedDomainContractCatalog::markupHooks('vehicle')
));
$domainAudit = new DomainMarkupAuditService();
comparatorAssert(
    $domainAudit->audit('vehicle', $vehicleContractMarkup, $vehicleContractMarkup)->equivalent(),
    'Identical Vehicle markup satisfying the protected contract must pass.'
);
comparatorAssert(
    !$domainAudit->audit('vehicle', $vehicleContractMarkup, '<div class="h18-vehicle-register"></div>')->equivalent(),
    'Vehicle candidate missing protected hooks must fail domain audit.'
);

$pageState = [
    'Version' => '1.22',
    'PageSlug' => 'hjem',
    'PageTitle' => 'Hjem',
    'ContentVersion' => 1,
    'DataContextType' => '',
    'DataContextEntryId' => 0,
    'Sections' => [
        ['Key' => 'one', 'Type' => 'text', 'LayoutParentKey' => ''],
    ],
];
$repository = new class($pageState) implements PageRepository {
    /** @var array<string,array<string,mixed>> */
    private array $store;

    /** @param array<string,mixed> $state */
    public function __construct(array $state)
    {
        $this->store = ['hjem' => $state];
    }

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

$stateAudit = new ShadowPageStateAuditor($repository, new PageSchemaValidator());
comparatorAssert($stateAudit->audit('hjem', $pageState)->equivalent(), 'Identical repository/legacy page state must pass shadow audit.');
$changedPageState = $pageState;
$changedPageState['PageTitle'] = 'Changed';
comparatorAssert(!$stateAudit->audit('hjem', $changedPageState)->equivalent(), 'Changed legacy/repository state must fail shadow audit.');

fwrite(STDOUT, "Compatibility comparator smoke test: PASS\n");
