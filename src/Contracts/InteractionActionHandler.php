<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface InteractionActionHandler
{
    public function type(): string;

    /**
     * @param array<string,mixed> $config
     * @param array<string,mixed> $context
     * @return array{success:bool,message:string,data?:array<string,mixed>}
     */
    public function execute(array $config, array $context): array;
}
