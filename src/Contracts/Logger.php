<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface Logger
{
    public function log(string $level, string $checkpoint, string $message): void;
}
