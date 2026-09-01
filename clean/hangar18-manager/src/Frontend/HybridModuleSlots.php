<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Model\LayoutModel;

final class HybridModuleSlots
{
    /** @return string */
    public static function render(int $postId, string $slot): string
    {
        $slot = in_array($slot, ['before','between','after'], true) ? $slot : 'before';
        if (!metadata_exists('post', $postId, LayoutModel::META)) { return ''; }
        $model = LayoutModel::get($postId);
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? $model['nodes'] : [];
        $roots = [];
        foreach ($nodes as $node) {
            if (!is_array($node) || (string) ($node['parentId'] ?? '') !== '' || (string) ($node['type'] ?? '') !== 'section') { continue; }
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ((string) ($props['moduleSlot'] ?? 'before') !== $slot) { continue; }
            $roots[(string) $node['id']] = true;
        }
        if (!$roots) { return ''; }

        $keep = [];
        $changed = true;
        while ($changed) {
            $changed = false;
            foreach ($nodes as $node) {
                if (!is_array($node)) { continue; }
                $id = (string) ($node['id'] ?? ''); $parent = (string) ($node['parentId'] ?? '');
                if ($id === '' || isset($keep[$id])) { continue; }
                if (isset($roots[$id]) || ($parent !== '' && isset($keep[$parent]))) { $keep[$id] = true; $changed = true; }
            }
        }
        $filtered = array_values(array_filter($nodes, static fn($node): bool => is_array($node) && isset($keep[(string) ($node['id'] ?? '')])));
        $hasContent = false;
        foreach ($filtered as $node) { if ((string) ($node['type'] ?? '') !== 'section') { $hasContent = true; break; } }
        if (!$hasContent) { return ''; }
        $fragment = $model; $fragment['nodes'] = $filtered;
        return '<div class="h18-vd-hybrid-slot h18-vd-hybrid-slot-' . esc_attr($slot) . '">' . Renderer::renderFragment($fragment) . '</div>';
    }

    private function __construct() {}
}
