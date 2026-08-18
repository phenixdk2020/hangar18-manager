<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Registry;

use Hangar18\UltimateDesigner\Contracts\PropertyDefinition;
use InvalidArgumentException;
use RuntimeException;

final class PropertyRegistry
{
    /** @var array<string,PropertyDefinition> */
    private array $definitions = [];

    public function register(PropertyDefinition $definition): void
    {
        $key = strtolower(trim($definition->key()));
        if ($key === '' || preg_match('/^[a-z][a-z0-9_.-]{0,95}$/', $key) !== 1) {
            throw new InvalidArgumentException('Property key must be a stable lowercase key.');
        }
        if (isset($this->definitions[$key])) {
            throw new RuntimeException("Property '{$key}' is already registered.");
        }

        $this->definitions[$key] = $definition;
    }

    public function has(string $key): bool
    {
        return isset($this->definitions[strtolower(trim($key))]);
    }

    public function get(string $key): PropertyDefinition
    {
        $normalized = strtolower(trim($key));
        if (!isset($this->definitions[$normalized])) {
            throw new RuntimeException("Unknown property '{$normalized}'.");
        }

        return $this->definitions[$normalized];
    }

    /** @return array<string,PropertyDefinition> */
    public function all(): array
    {
        return $this->definitions;
    }
}
