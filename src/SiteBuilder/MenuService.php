<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use Hangar18\UltimateDesigner\Contracts\MenuRepository;
use RuntimeException;

/** UD-063 application service for version-safe menu trees. */
final class MenuService
{
    private MenuRepository $repository;
    private MenuTreeValidator $validator;
    private MenuPresentationNormalizer $presentation;

    public function __construct(MenuRepository $repository, MenuTreeValidator $validator, ?MenuPresentationNormalizer $presentation = null)
    {
        $this->repository = $repository;
        $this->validator = $validator;
        $this->presentation = $presentation ?? new MenuPresentationNormalizer();
    }

    /**
     * @param list<array<string,mixed>> $items
     * @param array<string,mixed> $presentation
     * @return array<string,mixed>
     */
    public function create(string $name, array $items = [], ?string $menuId = null, array $presentation = []): array
    {
        $id = $menuId !== null && trim($menuId) !== ''
            ? $this->normalizeId($menuId)
            : 'menu-' . substr(hash('sha256', $name . '|' . microtime(true)), 0, 16);
        if ($this->repository->get($id) !== null) {
            throw new RuntimeException("Menu '{$id}' already exists.");
        }
        $menu = [
            'SchemaVersion' => MenuTreeValidator::SCHEMA_VERSION,
            'Id' => $id,
            'Name' => trim($name),
            'Revision' => 1,
            'UpdatedUtc' => gmdate('c'),
            'Items' => $this->normalizeItems($items),
            'Presentation' => $this->presentation->normalize($presentation),
        ];
        $this->validator->assertValid($menu);
        return $this->repository->save($menu);
    }

    /**
     * @param list<array<string,mixed>> $items
     * @param array<string,mixed>|null $presentation null keeps existing presentation/default
     * @return array<string,mixed>
     */
    public function update(string $menuId, string $name, array $items, ?array $presentation = null): array
    {
        $id = $this->normalizeId($menuId);
        $existing = $this->repository->get($id);
        if ($existing === null) {
            throw new RuntimeException("Menu '{$id}' was not found.");
        }
        $menu = $existing;
        $menu['Name'] = trim($name);
        $menu['Revision'] = ((int) ($existing['Revision'] ?? 0)) + 1;
        $menu['UpdatedUtc'] = gmdate('c');
        $menu['Items'] = $this->normalizeItems($items);
        $sourcePresentation = $presentation ?? (is_array($existing['Presentation'] ?? null) ? $existing['Presentation'] : []);
        $menu['Presentation'] = $this->presentation->normalize($sourcePresentation);
        $this->validator->assertValid($menu);
        return $this->repository->save($menu);
    }

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        return $this->repository->all();
    }

    /** @return array<string,mixed>|null */
    public function get(string $menuId): ?array
    {
        $menu=$this->repository->get($this->normalizeId($menuId));
        if($menu!==null){
            $menu['Presentation']=$this->presentation->normalize(is_array($menu['Presentation']??null)?$menu['Presentation']:[]);
        }
        return $menu;
    }

    public function delete(string $menuId): void
    {
        $this->repository->delete($this->normalizeId($menuId));
    }

    /** @param list<array<string,mixed>> $items @return list<array<string,mixed>> */
    private function normalizeItems(array $items): array
    {
        $result = [];
        foreach (array_values($items) as $index => $item) {
            if (!is_array($item)) {
                continue;
            }
            $id = $this->normalizeId((string) ($item['Id'] ?? ('item-' . ($index + 1))));
            $result[] = [
                'Id' => $id,
                'ParentId' => $this->normalizeId((string) ($item['ParentId'] ?? '')),
                'Order' => isset($item['Order']) ? max(0, (int) $item['Order']) : (($index + 1) * 10),
                'Type' => strtolower(trim((string) ($item['Type'] ?? 'url'))),
                'Label' => trim((string) ($item['Label'] ?? '')),
                'Target' => trim((string) ($item['Target'] ?? '')),
                'Url' => trim((string) ($item['Url'] ?? '')),
                'Icon' => trim((string) ($item['Icon'] ?? '')),
                'Badge' => trim((string) ($item['Badge'] ?? '')),
                'Description' => trim((string) ($item['Description'] ?? '')),
                'OpenNew' => !empty($item['OpenNew']),
                'ComponentId' => trim((string) ($item['ComponentId'] ?? '')),
            ];
        }
        usort($result, static fn(array $a, array $b): int => ((int) $a['Order']) <=> ((int) $b['Order']));
        return $result;
    }

    private function normalizeId(string $id): string
    {
        $id = strtolower(trim($id));
        if ($id === '') {
            return '';
        }
        $id = preg_replace('/[^a-z0-9_-]+/', '-', $id) ?? '';
        return trim($id, '-_');
    }
}
