<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface SchemaMigration
{
    public function fromVersion(): string;

    public function toVersion(): string;

    /**
     * @param array<string,mixed> $state
     * @return array<string,mixed>
     */
    public function migrate(array $state): array;
}
