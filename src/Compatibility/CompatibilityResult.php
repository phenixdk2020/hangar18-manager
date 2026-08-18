<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

final class CompatibilityResult
{
    private bool $equivalent;
    private array $differences;

    public function __construct(bool $equivalent, array $differences = [])
    {
        $this->equivalent = $equivalent;
        $this->differences = array_values($differences);
    }

    public function equivalent(): bool
    {
        return $this->equivalent;
    }

    public function differences(): array
    {
        return $this->differences;
    }

    public function assertEquivalent(): void
    {
        if (!$this->equivalent) {
            throw new \RuntimeException('Compatibility comparison failed: ' . implode(' ', $this->differences));
        }
    }
}
