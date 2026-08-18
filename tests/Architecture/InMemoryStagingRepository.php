<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Contracts\StagingRepository;

final class InMemoryStagingRepository implements StagingRepository
{
    /** @var array<string,array<string,mixed>> */
    private array $workingStates = [];
    /** @var array<string,array<string,mixed>> */
    private array $publishedStates = [];

    public function working(string $resourceKey): ?array
    {
        return $this->workingStates[$resourceKey] ?? null;
    }

    public function published(string $resourceKey): ?array
    {
        return $this->publishedStates[$resourceKey] ?? null;
    }

    public function saveWorking(string $resourceKey, array $state): void
    {
        $this->workingStates[$resourceKey] = $state;
    }

    public function savePublished(string $resourceKey, array $state): void
    {
        $this->publishedStates[$resourceKey] = $state;
    }

    public function transaction(callable $callback)
    {
        $workingBefore = $this->workingStates;
        $publishedBefore = $this->publishedStates;
        try {
            return $callback();
        } catch (Throwable $e) {
            $this->workingStates = $workingBefore;
            $this->publishedStates = $publishedBefore;
            throw $e;
        }
    }
}
