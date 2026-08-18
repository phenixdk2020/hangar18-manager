<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface RenderEngine
{
    /**
     * @param array<string,mixed> $state
     * @param array<string,mixed> $context
     */
    public function render(array $state, array $context = []): string;
}
