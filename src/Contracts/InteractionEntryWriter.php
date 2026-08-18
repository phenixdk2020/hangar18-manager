<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface InteractionEntryWriter
{
    /** @param array<string,mixed> $values @return array<string,mixed> */
    public function save(string $dataType, array $values): array;
}
