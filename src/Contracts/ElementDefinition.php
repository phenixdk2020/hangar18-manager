<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface ElementDefinition
{
    public function type(): string;

    public function label(): string;

    /** @return array<string,mixed> */
    public function defaults(): array;

    /** @return array<string,mixed> */
    public function schema(): array;

    /** @return list<string> */
    public function propertyKeys(): array;
}
