<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use Hangar18\UltimateDesigner\Contracts\SchemaMigration;
use RuntimeException;

final class MigrationRegistry
{
    /** @var array<string,SchemaMigration> */
    private array $migrations = [];

    public function register(SchemaMigration $migration): void
    {
        $from = trim($migration->fromVersion());
        $to = trim($migration->toVersion());
        if ($from === '' || $to === '' || $from === $to) {
            throw new RuntimeException('Schema migration must define two different non-empty versions.');
        }
        if (isset($this->migrations[$from])) {
            throw new RuntimeException("A migration from schema '{$from}' is already registered.");
        }

        $this->migrations[$from] = $migration;
    }

    /**
     * @param array<string,mixed> $state
     * @return array<string,mixed>
     */
    public function migrate(array $state, string $fromVersion, string $targetVersion): array
    {
        $current = trim($fromVersion);
        $target = trim($targetVersion);
        $seen = [];

        while ($current !== $target) {
            if (isset($seen[$current])) {
                throw new RuntimeException("Schema migration cycle detected at '{$current}'.");
            }
            $seen[$current] = true;

            if (!isset($this->migrations[$current])) {
                throw new RuntimeException("No schema migration path from '{$current}' to '{$target}'.");
            }

            $migration = $this->migrations[$current];
            $state = $migration->migrate($state);
            $current = $migration->toVersion();
        }

        return $state;
    }
}
