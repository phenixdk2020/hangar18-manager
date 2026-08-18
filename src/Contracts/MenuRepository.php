<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface MenuRepository
{
    /** @return array<string,array<string,mixed>> */
    public function all(): array;

    /** @return array<string,mixed>|null */
    public function get(string $menuId): ?array;

    /** @param array<string,mixed> $menu @return array<string,mixed> */
    public function save(array $menu): array;

    public function delete(string $menuId): void;
}
