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
$baseline = ['Version' => '1.22', 'PageSlug' => 'hjem', 'Sections' => [['Key' => 'one', 'Type' => 'text', 'LayoutParentKey' => '']]];
comparatorAssert($stateComparator->compare($baseline, $baseline)->equivalent(), 'Identical state must compare as equivalent.');
$changed = $baseline;
$changed['Sections'][0]['Type'] = 'image';
comparatorAssert(!$stateComparator->compare($baseline, $changed)->equivalent(), 'Changed state must not compare as equivalent.');

$markupComparator = new MarkupComparator();
$vehicleMarkup = '<div class="h18-vehicle-register"><article class="h18-vehicle-card"></article></div>';
comparatorAssert($markupComparator->compare($vehicleMarkup, $vehicleMarkup, ['h18-vehicle-register', 'h18-vehicle-card'])->equivalent(), 'Identical markup must pass.');
comparatorAssert(!$markupComparator->compare($vehicleMarkup, '<div class="new-register"></div>', ['h18-vehicle-register', 'h18-vehicle-card'])->equivalent(), 'Missing protected hooks must fail.');

comparatorAssert(ProtectedDomainContractCatalog::domains() === CompatibilityPolicy::PROTECTED_DOMAINS, 'Protected domain catalog and runtime policy must match.');
foreach (ProtectedDomainContractCatalog::domains() as $domain) {
    comparatorAssert(CompatibilityPolicy::mustUseLegacyRuntime($domain), "Catalog domain '{$domain}' is not protected.");
    comparatorAssert(ProtectedDomainContractCatalog::slug($domain) !== '', "Catalog domain '{$domain}' has no slug.");
    comparatorAssert(ProtectedDomainContractCatalog::marker($domain) !== '', "Catalog domain '{$domain}' has no marker.");
    comparatorAssert(ProtectedDomainContractCatalog::adminActions($domain) !== [], "Catalog domain '{$domain}' has no admin actions.");
    comparatorAssert(ProtectedDomainContractCatalog::markupHooks($domain) !== [], "Catalog domain '{$domain}' has no markup hooks.");
}

$vehicleContractMarkup = implode('', array_map(static fn(string $hook): string => '<div class="' . $hook . '"></div>', ProtectedDomainContractCatalog::markupHooks('vehicle')));
$domainAudit = new DomainMarkupAuditService();
comparatorAssert($domainAudit->audit('vehicle', $vehicleContractMarkup, $vehicleContractMarkup)->equivalent(), 'Identical Vehicle contract markup must pass.');
comparatorAssert(!$domainAudit->audit('vehicle', $vehicleContractMarkup, '<div class="h18-vehicle-register"></div>')->equivalent(), 'Vehicle markup missing hooks must fail.');

$pageState = [
    'Version' => '1.22', 'PageSlug' => 'hjem', 'PageTitle' => 'Hjem', 'ContentVersion' => 1,
    'DataContextType' => '', 'DataContextEntryId' => 0,
    'Sections' => [['Key' => 'one', 'Type' => 'text', 'LayoutParentKey' => '']],
];
$repository = new class($pageState) implements PageRepository {
    private array $store;
    public function __construct(array $state) { $this->store = ['hjem' => $state]; }
    public function load(string $pageKey): ?array { return $this->store[$pageKey] ?? null; }
    public function save(string $pageKey, array $state): void { $this->store[$pageKey] = $state; }
    public function exists(string $pageKey): bool { return array_key_exists($pageKey, $this->store); }
};
$stateAudit = new ShadowPageStateAuditor($repository, new PageSchemaValidator());
comparatorAssert($stateAudit->audit('hjem', $pageState)->equivalent(), 'Identical repository/legacy page state must pass shadow audit.');
$changedPageState = $pageState;
$changedPageState['PageTitle'] = 'Changed';
comparatorAssert(!$stateAudit->audit('hjem', $changedPageState)->equivalent(), 'Changed page state must fail shadow audit.');

fwrite(STDOUT, "Compatibility comparator smoke test: PASS\n");
