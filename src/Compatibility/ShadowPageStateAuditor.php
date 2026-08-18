<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

use Hangar18\UltimateDesigner\Contracts\PageRepository;
use Hangar18\UltimateDesigner\Contracts\SchemaValidator;

/**
 * Read-only audit helper for comparing a legacy page state with the state seen
 * through an extracted repository/validator path. It never writes or migrates.
 */
final class ShadowPageStateAuditor
{
    private PageRepository $pages;
    private SchemaValidator $validator;
    private StateComparator $comparator;

    public function __construct(
        PageRepository $pages,
        SchemaValidator $validator,
        ?StateComparator $comparator = null
    ) {
        $this->pages = $pages;
        $this->validator = $validator;
        $this->comparator = $comparator ?? new StateComparator();
    }

    /** @param array<string,mixed> $legacyState */
    public function audit(string $pageKey, array $legacyState): CompatibilityResult
    {
        $differences = [];

        foreach ($this->validator->validate($legacyState) as $error) {
            $differences[] = 'Legacy state invalid: ' . $error;
        }

        $candidate = $this->pages->load($pageKey);
        if ($candidate === null) {
            $differences[] = "Candidate repository returned no state for '{$pageKey}'.";
            return new CompatibilityResult(false, $differences);
        }

        foreach ($this->validator->validate($candidate) as $error) {
            $differences[] = 'Candidate state invalid: ' . $error;
        }

        if ($differences !== []) {
            return new CompatibilityResult(false, $differences);
        }

        return $this->comparator->compare($legacyState, $candidate);
    }
}
