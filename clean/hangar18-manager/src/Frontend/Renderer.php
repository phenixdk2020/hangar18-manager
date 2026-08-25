<?php

declare(strict_types=1);

namespace Hangar18\Clean\Frontend;

use Hangar18\Clean\Model\LayoutModel;

final class Renderer
{
    public static function register(): void
    {
        add_filter('the_content', [self::class, 'content'], 20);
        add_action('wp_head', [self::class, 'css'], 1000);
    }

    public static function content(string $content): string
    {
        if (is_admin() || !is_singular('page') || !in_the_loop() || !is_main_query()) {
            return $content;
        }
        $postId = get_the_ID();
        if ($postId <= 0 || !metadata_exists('post', $postId, LayoutModel::META)) {
            return $content;
        }
        $model = LayoutModel::get($postId);
        if (empty($model['nodes'])) {
            return '';
        }
        return self::renderModel($model);
    }

    public static function css(): void
    {
        if (!is_singular('page')) {
            return;
        }
        $postId = get_queried_object_id();
        if ($postId <= 0 || !metadata_exists('post', $postId, LayoutModel::META)) {
            return;
        }
        echo <<<'CSS'
<style id="h18-clean-frontend-css">
.h18-clean-page,.h18-clean-front-surface{display:grid;grid-template-columns:repeat(120,minmax(0,1fr));align-items:start;width:100%;box-sizing:border-box;min-width:0}
.h18-clean-front-node{box-sizing:border-box;min-width:0;position:relative}
.h18-clean-front-container,.h18-clean-front-section{display:grid;grid-template-columns:repeat(120,minmax(0,1fr));align-items:start;min-width:0;box-sizing:border-box;height:auto!important}
.h18-clean-front-text{overflow-wrap:anywhere}
.h18-clean-front-image{margin:0;width:100%;max-width:none;overflow:hidden;box-sizing:border-box}
.h18-clean-front-image img{display:block;width:100%;max-width:none;margin:0;box-sizing:border-box}
</style>
CSS;
    }

    /** @param array<string,mixed> $model */
    private static function renderModel(array $model): string
    {
        $byParent = [];
        $byId = [];
        foreach ($model['nodes'] as $node) {
            $byId[$node['id']] = $node;
            $byParent[$node['parentId']][] = $node;
        }
        foreach ($byParent as &$children) {
            usort($children, static fn(array $a, array $b): int => (int) $a['order'] <=> (int) $b['order']);
        }
        unset($children);

        return '<div class="h18-clean-page h18-clean-front-surface">' . self::children('', $byParent, $byId) . '</div>';
    }

    /** @param array<string,array<int,array<string,mixed>>> $byParent @param array<string,array<string,mixed>> $byId */
    private static function children(string $parentId, array $byParent, array $byId): string
    {
        $html = '';
        foreach ($byParent[$parentId] ?? [] as $node) {
            $html .= self::node($node, $byParent, $byId);
        }
        return $html;
    }

    /** @param array<string,mixed> $node @param array<string,array<int,array<string,mixed>>> $byParent @param array<string,array<string,mixed>> $byId */
    private static function node(array $node, array $byParent, array $byId): string
    {
        $g = isset($node['geometry']['desktop']) && is_array($node['geometry']['desktop']) ? $node['geometry']['desktop'] : ['x' => 0, 'y' => 0, 'w' => 120, 'h' => 0];
        $x = max(0, min(119, (int) ($g['x'] ?? 0)));
        $w = max(1, min(120 - $x, (int) ($g['w'] ?? 120)));
        $y = (int) ($g['y'] ?? 0);
        $h = max(0, (int) ($g['h'] ?? 0));
        $style = 'grid-column:' . ($x + 1) . '/span ' . $w . ';';
        if ($y !== 0) {
            $style .= 'margin-top:' . ($y * LayoutModel::ROW_PX) . 'px;';
        }
        if ($h > 0) {
            $style .= 'height:' . ($h * LayoutModel::ROW_PX) . 'px;min-height:' . ($h * LayoutModel::ROW_PX) . 'px;';
        }

        $id = esc_attr((string) $node['id']);
        $type = (string) $node['type'];
        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $borderStyle = self::borderStyle($props);

        if ($type === 'text') {
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-text" style="' . esc_attr($style . $borderStyle . 'text-align:' . (string) ($props['align'] ?? 'left') . ';') . '">' . wpautop(wp_kses_post((string) ($props['text'] ?? ''))) . '</div>';
        }
        if ($type === 'image') {
            $url = esc_url((string) ($props['url'] ?? ''));
            if ($url === '' && !empty($props['mediaId'])) {
                $url = esc_url((string) wp_get_attachment_image_url((int) $props['mediaId'], 'full'));
            }
            $fit = (string) ($props['fit'] ?? 'cover');
            $fitCss = $fit === 'contain' ? 'contain' : ($fit === 'stretch' ? 'fill' : 'cover');
            $imageStyle = 'object-fit:' . $fitCss . ';object-position:' . (int) ($props['focalX'] ?? 50) . '% ' . (int) ($props['focalY'] ?? 50) . '%;';
            if ($h > 0) {
                $imageStyle .= 'height:100%;';
            } else {
                $imageStyle .= 'height:auto;';
            }
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($style . $borderStyle) . '"><figure class="h18-clean-front-image"' . ($h > 0 ? ' style="height:100%"' : '') . '>' . ($url !== '' ? '<img src="' . $url . '" alt="' . esc_attr((string) ($props['alt'] ?? '')) . '" style="' . esc_attr($imageStyle) . '">' : '') . '</figure></div>';
        }

        $background = sanitize_hex_color((string) ($props['background'] ?? '')) ?: 'transparent';
        $radius = max(0, min(100, (int) ($props['radius'] ?? 0)));
        $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
        $classes = $type === 'section' ? 'h18-clean-front-section' : 'h18-clean-front-container';
        $requiredHeight = self::requiredChildHeightPx((string) $node['id'], $byParent);
        $selectedHeight = $h * LayoutModel::ROW_PX;
        $minimumHeight = max($selectedHeight, $requiredHeight);
        if ($minimumHeight > 0) {
            $style .= 'min-height:' . $minimumHeight . 'px;';
        }
        $boxStyle = $style . $borderStyle . 'background:' . $background . ';border-radius:' . $radius . 'px;padding:' . $padding . 'px;';
        return '<section id="h18-clean-' . $id . '" class="h18-clean-front-node ' . esc_attr($classes) . '" style="' . esc_attr($boxStyle) . '">' . self::children((string) $node['id'], $byParent, $byId) . '</section>';
    }

    /** @param array<string,mixed> $props */
    private static function borderStyle(array $props): string
    {
        $width = max(0, min(20, (int) ($props['borderWidth'] ?? 0)));
        if ($width === 0) {
            return 'border:0 solid transparent;';
        }
        $color = sanitize_hex_color((string) ($props['borderColor'] ?? '#000000')) ?: '#000000';
        return 'border:' . $width . 'px solid ' . $color . ';';
    }

    /** @param array<string,array<int,array<string,mixed>>> $byParent */
    private static function requiredChildHeightPx(string $parentId, array $byParent): int
    {
        $required = 0;
        foreach ($byParent[$parentId] ?? [] as $child) {
            $g = isset($child['geometry']['desktop']) && is_array($child['geometry']['desktop']) ? $child['geometry']['desktop'] : [];
            $y = max(0, (int) ($g['y'] ?? 0));
            $h = max(0, (int) ($g['h'] ?? 0));
            $childHeight = $h * LayoutModel::ROW_PX;
            if (in_array((string) ($child['type'] ?? ''), ['section', 'container'], true)) {
                $childHeight = max($childHeight, self::requiredChildHeightPx((string) ($child['id'] ?? ''), $byParent));
            }
            $required = max($required, ($y * LayoutModel::ROW_PX) + $childHeight);
        }
        return $required;
    }
}
