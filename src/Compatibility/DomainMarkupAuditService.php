<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

final class DomainMarkupAuditService
{
    private MarkupComparator $comparator;

    public function __construct(?MarkupComparator $comparator = null)
    {
        $this->comparator = $comparator ?? new MarkupComparator();
    }

    public function audit(string $domain, string $legacyMarkup, string $candidateMarkup): CompatibilityResult
    {
        return $this->comparator->compare(
            $legacyMarkup,
            $candidateMarkup,
            ProtectedDomainContractCatalog::markupHooks($domain)
        );
    }
}
