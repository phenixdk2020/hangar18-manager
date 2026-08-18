<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface AiProvider
{
    /**
     * Provider-neutral structured request/response boundary.
     * Providers must return data only; they never receive repository/write access.
     * @param array<string,mixed> $request
     * @return array<string,mixed>
     */
    public function complete(array $request): array;
}
