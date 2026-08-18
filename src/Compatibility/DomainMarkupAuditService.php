<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

/**
 * Runs old/new markup comparison using the machine-readable contract for a
 * protected Vehicle/Event/Gallery domain.
 */
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
