<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\MenuRepository;
use RuntimeException;

final class WordPressOptionMenuRepository implements MenuRepository
{
    public const OPTION = 'hangar18_manager_site_menus_v1';
    private const MAX_MENUS = 50;

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        $stored = get_option(self::OPTION, []);
        if (!is_array($stored)) {
            return [];
        }
        $result = [];
        foreach ($stored as $id => $menu) {
            if (!is_array($menu)) {
                continue;
            }
            $key = (string) ($menu['Id'] ?? $id);
            if ($key !== '') {
                $result[$key] = $menu;
            }
        }
        return $result;
    }

    /** @return array<string,mixed>|null */
    public function get(string $menuId): ?array
    {
        $all = $this->all();
        return $all[$menuId] ?? null;
    }

    /** @param array<string,mixed> $menu @return array<string,mixed> */
    public function save(array $menu): array
    {
        $id = (string) ($menu['Id'] ?? '');
        if ($id === '') {
            throw new RuntimeException('Menu Id is required.');
        }
        $all = $this->all();
        if (!isset($all[$id]) && count($all) >= self::MAX_MENUS) {
            throw new RuntimeException('Maximum number of Site Builder menus reached.');
        }
        $all[$id] = $menu;
        update_option(self::OPTION, $all, false);
        return $menu;
    }

    public function delete(string $menuId): void
    {
        $all = $this->all();
        if (!isset($all[$menuId])) {
            return;
        }
        unset($all[$menuId]);
        update_option(self::OPTION, $all, false);
    }
}
