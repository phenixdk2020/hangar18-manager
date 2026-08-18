<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

/**
 * UD-064 server renderer for classic horizontal/dropdown navigation.
 * JavaScript is progressive enhancement only; links remain usable without it.
 */
final class ClassicMenuRenderer
{
    /** @param array<string,mixed> $menu */
    public function render(array $menu, string $currentUrl = ''): string
    {
        (new MenuTreeValidator())->assertValid($menu);
        $items = array_values($menu['Items'] ?? []);
        $children = [];
        foreach ($items as $item) {
            $parent = (string) ($item['ParentId'] ?? '');
            $children[$parent][] = $item;
        }
        foreach ($children as &$group) {
            usort($group, static fn(array $a, array $b): int => ((int) ($a['Order'] ?? 0)) <=> ((int) ($b['Order'] ?? 0)));
        }
        unset($group);

        $menuId = $this->esc((string) ($menu['Id'] ?? 'menu'));
        $name = $this->esc((string) ($menu['Name'] ?? 'Menu'));
        $html = '<div class="h18-menu-shell" data-h18-menu-shell="' . $menuId . '">';
        $html .= '<button type="button" class="h18-menu-mobile-toggle" aria-expanded="false" aria-controls="h18-menu-' . $menuId . '"><span class="h18-menu-toggle-label">Menu</span></button>';
        $html .= '<nav id="h18-menu-' . $menuId . '" class="h18-menu h18-menu--classic" aria-label="' . $name . '" data-h18-menu>';
        $html .= $this->renderLevel($children, '', $currentUrl, 0);
        $html .= '</nav></div>';
        return $html;
    }

    /** @param array<string,list<array<string,mixed>>> $children */
    private function renderLevel(array $children, string $parentId, string $currentUrl, int $depth): string
    {
        $items = $children[$parentId] ?? [];
        if ($items === []) {
            return '';
        }
        $class = $depth === 0 ? 'h18-menu-list h18-menu-list--root' : 'h18-menu-list h18-menu-list--submenu';
        $html = '<ul class="' . $class . '" data-menu-depth="' . $depth . '">';
        foreach ($items as $item) {
            $id = (string) ($item['Id'] ?? '');
            $label = (string) ($item['Label'] ?? '');
            $url = $this->urlFor($item);
            $hasChildren = !empty($children[$id]);
            $active = $currentUrl !== '' && $this->normalizeUrl($currentUrl) === $this->normalizeUrl($url);
            $liClass = 'h18-menu-item' . ($hasChildren ? ' has-children' : '') . ($active ? ' is-current' : '');
            $html .= '<li class="' . $liClass . '" data-menu-item="' . $this->esc($id) . '">';
            $html .= '<a class="h18-menu-link" href="' . $this->esc($url) . '"' . ($active ? ' aria-current="page"' : '') . (!empty($item['OpenNew']) ? ' target="_blank" rel="noopener noreferrer"' : '') . '>';
            if ((string) ($item['Icon'] ?? '') !== '') {
                $html .= '<span class="h18-menu-icon" aria-hidden="true">' . $this->esc((string) $item['Icon']) . '</span>';
            }
            $html .= '<span class="h18-menu-label">' . $this->esc($label) . '</span>';
            if ((string) ($item['Badge'] ?? '') !== '') {
                $html .= '<span class="h18-menu-badge">' . $this->esc((string) $item['Badge']) . '</span>';
            }
            $html .= '</a>';
            if ($hasChildren) {
                $html .= '<button type="button" class="h18-submenu-toggle" aria-expanded="false" aria-label="Vis undermenu for ' . $this->esc($label) . '"><span aria-hidden="true">▾</span></button>';
                $html .= $this->renderLevel($children, $id, $currentUrl, $depth + 1);
            }
            $html .= '</li>';
        }
        $html .= '</ul>';
        return $html;
    }

    /** @param array<string,mixed> $item */
    private function urlFor(array $item): string
    {
        $url = trim((string) ($item['Url'] ?? ''));
        if ($url !== '') {
            return $url;
        }
        $target = trim((string) ($item['Target'] ?? ''));
        if (($item['Type'] ?? '') === 'anchor' && $target !== '') {
            return '#' . ltrim($target, '#');
        }
        return $target !== '' ? $target : '#';
    }

    private function normalizeUrl(string $url): string
    {
        return rtrim(strtolower(trim($url)), '/');
    }

    private function esc(string $value): string
    {
        return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}
