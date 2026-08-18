<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface SchemaValidator
{
    /**
     * @param array<string,mixed> $state
     * @return list<string> Validation errors. Empty means valid.
     */
    public function validate(array $state): array;

    /** @param array<string,mixed> $state */
    public function assertValid(array $state): void;
}
