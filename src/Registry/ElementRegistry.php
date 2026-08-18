<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Registry;

use Hangar18\UltimateDesigner\Contracts\ElementDefinition;
use InvalidArgumentException;
use RuntimeException;

final class ElementRegistry
{
    /** @var array<string,ElementDefinition> */
    private array $definitions = [];

    public function register(ElementDefinition $definition): void
    {
        $type = strtolower(trim($definition->type()));
        if ($type === '' || preg_match('/^[a-z][a-z0-9_-]{0,63}$/', $type) !== 1) {
            throw new InvalidArgumentException('Element type must be a stable lowercase key.');
        }
        if (isset($this->definitions[$type])) {
            throw new RuntimeException("Element type '{$type}' is already registered.");
        }

        $this->definitions[$type] = $definition;
    }

    public function has(string $type): bool
    {
        return isset($this->definitions[strtolower(trim($type))]);
    }

    public function get(string $type): ElementDefinition
    {
        $key = strtolower(trim($type));
        if (!isset($this->definitions[$key])) {
            throw new RuntimeException("Unknown element type '{$key}'.");
        }

        return $this->definitions[$key];
    }

    /** @return array<string,ElementDefinition> */
    public function all(): array
    {
        return $this->definitions;
    }
}
