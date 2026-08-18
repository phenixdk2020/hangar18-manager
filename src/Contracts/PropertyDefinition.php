<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface PropertyDefinition
{
    public function key(): string;

    public function label(): string;

    public function control(): string;

    /** @return array<string,mixed> */
    public function schema(): array;

    /** @return mixed */
    public function defaultValue();
}
