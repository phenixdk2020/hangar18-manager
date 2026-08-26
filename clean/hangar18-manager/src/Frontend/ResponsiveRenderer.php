<?php

declare(strict_types=1);

namespace Hangar18\Clean\Frontend;

use Hangar18\Clean\Model\LayoutModel;

/**
 * Responsive geometry layer for Clean Designer.
 *
 * The normal Renderer remains the single HTML renderer. This class only emits
 * breakpoint-specific geometry overrides from the same canonical model.
 */
final class ResponsiveRenderer
{
    public const LAPTOP_MAX = 1180;
    public const MOBILE_MAX = 782;

    public static function register(): void
    {
        add_action('wp_head', [self::class, 'css'], 1001);
    }

    public static function css(): void
    {
        if (!is_singular('page')) {
            return;
        }

        $postId = get_queried_object_id();
        if ($postId <= 0) {
            return;
        }

        $model = self::model($postId);
        if ($model === null || empty($model['nodes']) || !is_array($model['nodes'])) {
            return;
        }

        $byId = [];
        $byParent = [];
        foreach ($model['nodes'] as $node) {
            if (!is_array($node) || empty($node['id'])) {
                continue;
            }
            $id = (string) $node['id'];
            $byId[$id] = $node;
            $parent = (string) ($node['parentId'] ?? '');
            $byParent[$parent][] = $node;
        }

        $laptop = '';
        $mobile = '';
        foreach ($byId as $id => $node) {
            $lg = self::effectiveGeometry($node, 'laptop');
            $mg = self::effectiveGeometry($node, 'mobile');
            $laptopRows = self::effectiveRows($id, 'laptop', $byId, $byParent, []);
            $mobileRows = self::effectiveRows($id, 'mobile', $byId, $byParent, []);
            $selector = '#h18-clean-' . self::cssId($id);
            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $floating = (string) ($node['type'] ?? '') === 'button' && (string) ($node['parentId'] ?? '') !== '' && (string) ($props['placementMode'] ?? 'normal') === 'overlay';
            $zIndex = max(1, min(200, (int) ($props['zIndex'] ?? 20)));
            $laptop .= self::geometryCss($selector, $lg, $laptopRows, $floating, $zIndex);
            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);
        }

        echo '<style id="h18-clean-responsive-css">';
        echo '.h18-clean-page{max-width:100%;overflow-x:clip}';
        echo '@media(max-width:' . esc_attr((string) self::LAPTOP_MAX) . 'px){' . $laptop . '}';
        echo '@media(max-width:' . esc_attr((string) self::MOBILE_MAX) . 'px){' . $mobile . '}';
        echo '</style>';
    }

    /** @return array<string,mixed>|null */
    private static function model(int $postId): ?array
    {
        $preview = self::previewModel($postId);
        if ($preview !== null) {
            return $preview;
        }
        if (!metadata_exists('post', $postId, LayoutModel::META)) {
            return null;
        }
        return LayoutModel::get($postId);
    }

    /** @return array<string,mixed>|null */
    private static function previewModel(int $postId): ?array
    {
        if (!is_user_logged_in() || !current_user_can('edit_pages')) {
            return null;
        }
        $token = isset($_GET['h18_clean_preview']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_preview'])) : '';
        if ($token === '' || !preg_match('/^[a-z0-9]{12,64}$/', $token)) {
            return null;
        }
        $raw = get_transient(Renderer::previewKey(get_current_user_id(), $postId, $token));
        if (!is_array($raw)) {
            return null;
        }
        try {
            return LayoutModel::normalize($raw);
        } catch (\Throwable $error) {
            return null;
        }
    }

    /** @param array<string,mixed> $node @return array{x:int,y:int,w:int,h:int} */
    private static function effectiveGeometry(array $node, string $device): array
    {
        $geometry = is_array($node['geometry'] ?? null) ? $node['geometry'] : [];
        $desktop = self::geometry($geometry['desktop'] ?? null);
        if ($device === 'desktop') {
            return $desktop;
        }

        $laptopRaw = is_array($geometry['laptop'] ?? null) ? $geometry['laptop'] : [];
        $laptop = !empty($laptopRaw['inheritDesktop']) ? $desktop : self::geometry($laptopRaw, $desktop);
        if ($device === 'laptop') {
            return $laptop;
        }

        $mobileRaw = is_array($geometry['mobile'] ?? null) ? $geometry['mobile'] : [];
        // Responsive inheritance is cascading in the UI: Mobile inherits the
        // effective Laptop layout (which itself may inherit Desktop).
        return !empty($mobileRaw['inheritDesktop']) ? $laptop : self::geometry($mobileRaw, $laptop);
    }

    /** @param mixed $raw @param array{x:int,y:int,w:int,h:int}|null $fallback @return array{x:int,y:int,w:int,h:int} */
    private static function geometry(mixed $raw, ?array $fallback = null): array
    {
        $fallback ??= ['x' => 0, 'y' => 0, 'w' => LayoutModel::UNITS, 'h' => 0];
        if (!is_array($raw)) {
            return $fallback;
        }
        $x = max(0, min(LayoutModel::UNITS - 1, (int) ($raw['x'] ?? $fallback['x'])));
        $w = max(1, min(LayoutModel::UNITS - $x, (int) ($raw['w'] ?? $fallback['w'])));
        return [
            'x' => $x,
            'y' => max(0, min(10000, (int) ($raw['y'] ?? $fallback['y']))),
            'w' => $w,
            'h' => max(0, min(4000, (int) ($raw['h'] ?? $fallback['h']))),
        ];
    }

    /**
     * Runtime auto-grow for a breakpoint. This is deliberately derived from
     * canonical child geometry so responsive parents cannot visually overlap
     * following siblings merely because their children were stacked on Mobile.
     *
     * @param array<string,array<string,mixed>> $byId
     * @param array<string,array<int,array<string,mixed>>> $byParent
     * @param array<string,bool> $seen
     */
    private static function effectiveRows(string $id, string $device, array $byId, array $byParent, array $seen): int
    {
        if (!isset($byId[$id]) || isset($seen[$id])) {
            return 1;
        }
        $seen[$id] = true;
        $node = $byId[$id];
        $g = self::effectiveGeometry($node, $device);
        $type = (string) ($node['type'] ?? '');
        $base = $g['h'] > 0 ? $g['h'] : (in_array($type, ['text', 'image'], true) ? 10 : 8);

        if (!in_array($type, ['section', 'container'], true)) {
            return max(1, $base);
        }

        $required = 0;
        foreach ($byParent[$id] ?? [] as $child) {
            $childProps = is_array($child['props'] ?? null) ? $child['props'] : [];
            if ((string) ($child['type'] ?? '') === 'button' && (string) ($child['parentId'] ?? '') !== '' && (string) ($childProps['placementMode'] ?? 'normal') === 'overlay') { continue; }
            $childId = (string) ($child['id'] ?? '');
            if ($childId === '') {
                continue;
            }
            $cg = self::effectiveGeometry($child, $device);
            $required = max($required, $cg['y'] + self::effectiveRows($childId, $device, $byId, $byParent, $seen));
        }

        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $extraPx = (max(0, (int) ($props['padding'] ?? 0)) * 2) + (max(0, (int) ($props['borderWidth'] ?? 0)) * 2);
        $required += (int) ceil($extraPx / LayoutModel::ROW_PX);
        return max(1, $base, $required);
    }

    /** @param array{x:int,y:int,w:int,h:int} $g */
    private static function geometryCss(string $selector, array $g, int $rows, bool $floating = false, int $zIndex = 20): string
    {
        $rows = max(1, $rows);
        if ($floating) {
            $left = ($g['x'] / LayoutModel::UNITS) * 100;
            $width = ($g['w'] / LayoutModel::UNITS) * 100;
            return $selector . '{position:absolute!important;left:' . $left . '%!important;top:' . (max(0, $g['y']) * LayoutModel::ROW_PX) . 'px!important;'
                . 'width:' . $width . '%!important;height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;min-height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;'
                . 'z-index:' . max(1, min(200, $zIndex)) . '!important;grid-column:auto!important;grid-row:auto!important;margin-top:0!important;}';
        }
        $row = max(0, $g['y']) + 1;
        return $selector . '{grid-column:' . ($g['x'] + 1) . '/span ' . $g['w'] . '!important;'
            . 'grid-row:' . $row . '/span ' . $rows . '!important;'
            . 'min-height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;'
            . 'margin-top:0!important;}';
    }

    private static function cssId(string $id): string
    {
        // Clean IDs are already normalized to [a-z0-9._-]. CSS.escape is not
        // available server-side, so escape the only CSS-special punctuation.
        return str_replace(['.', ':'], ['\\.', '\\:'], $id);
    }
}
