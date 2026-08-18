<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Contracts\MenuRepository;
use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;

final class InMemoryMenuRepository implements MenuRepository
{
    /** @var array<string,array<string,mixed>> */
    private array $items=[];
    public function all(): array { return $this->items; }
    public function get(string $menuId): ?array { return $this->items[$menuId] ?? null; }
    public function save(array $menu): array { $this->items[(string) $menu['Id']]=$menu; ksort($this->items); return $menu; }
    public function delete(string $menuId): void { unset($this->items[$menuId]); }
}

final class InMemorySiteTemplateRepository implements SiteTemplateRepository
{
    /** @var array<string,array<string,mixed>> */
    private array $items=[];
    /** @var array<string,string|null> */
    private array $global=['header'=>null,'footer'=>null];
    public function all(): array { return $this->items; }
    public function get(string $templateId): ?array { return $this->items[$templateId] ?? null; }
    public function save(array $template): array { $this->items[(string) $template['Id']]=$template; ksort($this->items); return $template; }
    public function delete(string $templateId): void { unset($this->items[$templateId]); foreach($this->global as $kind=>$id){if($id===$templateId)$this->global[$kind]=null;} }
    public function assignGlobal(string $kind, ?string $templateId): void { $this->global[$kind]=$templateId; }
    public function globalAssignment(string $kind): ?string { return $this->global[$kind] ?? null; }
}
