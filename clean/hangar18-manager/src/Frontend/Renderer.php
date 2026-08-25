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
        add_action('wp_footer', [self::class, 'previewBadge'], 1000);
    }

    public static function content(string $content): string
    {
        if (is_admin() || !is_singular('page') || !in_the_loop() || !is_main_query()) {
            return $content;
        }
        $postId = get_the_ID();
        if ($postId <= 0) {
            return $content;
        }
        $preview = self::previewModel($postId);
        if ($preview !== null) {
            return self::renderModel($preview);
        }
        if (!metadata_exists('post', $postId, LayoutModel::META)) {
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
        if ($postId <= 0 || (!metadata_exists('post', $postId, LayoutModel::META) && self::previewModel($postId) === null)) {
            return;
        }
        $rowPx = LayoutModel::ROW_PX;
        echo '<style id="h18-clean-frontend-css">';
        echo '.h18-clean-page,.h18-clean-front-surface{display:grid;grid-template-columns:repeat(120,minmax(0,1fr));grid-auto-rows:' . esc_attr((string) $rowPx) . 'px;align-items:stretch;width:100%;box-sizing:border-box;min-width:0}';
        echo '.h18-clean-front-node{box-sizing:border-box;min-width:0;position:relative}';
        echo '.h18-clean-front-container,.h18-clean-front-section{display:grid;grid-template-columns:repeat(120,minmax(0,1fr));grid-auto-rows:' . esc_attr((string) $rowPx) . 'px;align-items:stretch;min-width:0;box-sizing:border-box;height:auto!important}';
        echo '.h18-clean-front-text{overflow-wrap:anywhere}';
        echo '.h18-clean-front-text-heading{margin:0 0 8px;line-height:1.2}';
        echo '.h18-clean-front-image{margin:0;width:100%;max-width:none;overflow:hidden;box-sizing:border-box;height:100%}';
        echo '.h18-clean-front-image img{display:block;max-width:none;margin:0;box-sizing:border-box}';
        echo '</style>';
    }

    public static function previewKey(int $userId, int $postId, string $token): string
    {
        return 'h18_clean_preview_' . max(0, $userId) . '_' . max(0, $postId) . '_' . sanitize_key($token);
    }

    public static function previewBadge(): void
    {
        if (!is_singular('page')) {
            return;
        }
        $postId = get_queried_object_id();
        if ($postId <= 0 || self::previewModel($postId) === null) {
            return;
        }
        $version = isset($_GET['h18_clean_preview_version']) ? absint($_GET['h18_clean_preview_version']) : 0;
        $label = $version > 0 ? 'Historisk version v' . $version . ' · ikke aktiv' : 'Forhåndsvisning · ikke gemt';
        echo '<div style="position:fixed;right:16px;bottom:16px;z-index:2147483647;padding:8px 12px;border:1px solid #2271b1;border-radius:6px;background:#fff;color:#1d2327;box-shadow:0 4px 18px rgba(0,0,0,.2);font:600 13px/1.3 system-ui,sans-serif;pointer-events:none">' . esc_html($label) . '</div>';
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
        $raw = get_transient(self::previewKey(get_current_user_id(), $postId, $token));
        if (!is_array($raw)) {
            return null;
        }
        try {
            return LayoutModel::normalize($raw);
        } catch (\Throwable $error) {
            return null;
        }
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
        $y = max(0, (int) ($g['y'] ?? 0));
        $h = max(0, (int) ($g['h'] ?? 0));
        $style = 'grid-column:' . ($x + 1) . '/span ' . $w . ';';
        if ($h > 0) {
            $style .= 'grid-row:' . ($y + 1) . '/span ' . $h . ';min-height:' . ($h * LayoutModel::ROW_PX) . 'px;';
        } elseif ($y !== 0) {
            $style .= 'margin-top:' . ($y * LayoutModel::ROW_PX) . 'px;';
        }

        $id = esc_attr((string) $node['id']);
        $type = (string) $node['type'];
        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $borderStyle = self::borderStyle($props);
        $spacingStyle = self::spacingStyle($props);
        $radius = max(0, min(100, (int) ($props['radius'] ?? 0)));
        $radiusStyle = 'border-radius:' . $radius . 'px;';

        if ($type === 'text') {
            $heading = trim((string) ($props['heading'] ?? ''));
            $headingLevel = in_array((string) ($props['headingLevel'] ?? 'h2'), ['h2', 'h3', 'h4', 'h5', 'h6'], true) ? (string) $props['headingLevel'] : 'h2';
            $headingColor = sanitize_hex_color((string) ($props['headingColor'] ?? '#000000')) ?: '#000000';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#000000')) ?: '#000000';
            $background = !empty($props['backgroundTransparent'])
                ? 'transparent'
                : (sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff');
            $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
            $headingHtml = $heading !== ''
                ? '<' . $headingLevel . ' class="h18-clean-front-text-heading" style="color:' . esc_attr($headingColor) . '">' . esc_html($heading) . '</' . $headingLevel . '>'
                : '';
            $textStyle = $style . $borderStyle . $spacingStyle . $radiusStyle
                . 'background:' . $background . ';padding:' . $padding . 'px;color:' . $textColor . ';text-align:' . (string) ($props['align'] ?? 'left') . ';';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-text" style="' . esc_attr($textStyle) . '">' . $headingHtml . wpautop(wp_kses_post((string) ($props['text'] ?? ''))) . '</div>';
        }

        if ($type === 'image') {
            $url = esc_url((string) ($props['url'] ?? ''));
            if ($url === '' && !empty($props['mediaId'])) {
                $url = esc_url((string) wp_get_attachment_image_url((int) $props['mediaId'], 'full'));
            }
            $fit = (string) ($props['fit'] ?? 'contain');
            if (!in_array($fit, ['cover', 'contain', 'original', 'stretch', 'manual'], true)) {
                $fit = 'contain';
            }
            $alignX = in_array((string) ($props['imageAlignX'] ?? 'center'), ['left', 'center', 'right'], true) ? (string) $props['imageAlignX'] : 'center';
            $alignY = in_array((string) ($props['imageAlignY'] ?? 'center'), ['top', 'center', 'bottom'], true) ? (string) $props['imageAlignY'] : 'center';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$alignX];
            $alignItems = ['top' => 'flex-start', 'center' => 'center', 'bottom' => 'flex-end'][$alignY];
            $posX = ['left' => '0%', 'center' => '50%', 'right' => '100%'][$alignX];
            $posY = ['top' => '0%', 'center' => '50%', 'bottom' => '100%'][$alignY];
            $background = !empty($props['boxTransparent']) ? 'transparent' : (sanitize_hex_color((string) ($props['boxBackground'] ?? '#ffffff')) ?: '#ffffff');
            $figureStyle = 'height:100%;background:' . $background . ';border-radius:inherit;overflow:hidden;';

            if ($fit === 'manual') {
                $manualX = max(-4000, min(4000, (int) ($props['manualX'] ?? 0)));
                $manualY = max(-4000, min(4000, (int) ($props['manualY'] ?? 0)));
                $manualW = max(1, min(4000, (int) ($props['manualW'] ?? 320)));
                $manualH = max(1, min(4000, (int) ($props['manualH'] ?? 240)));
                $figureStyle .= 'position:relative;display:block;';
                $imageStyle = 'position:absolute;left:' . $manualX . 'px;top:' . $manualY . 'px;width:' . $manualW . 'px;height:' . $manualH . 'px;max-width:none;max-height:none;object-fit:fill;object-position:50% 50%;';
            } else {
                $figureStyle .= 'display:flex;justify-content:' . $justify . ';align-items:' . $alignItems . ';';
                if ($fit === 'original') {
                    $imageStyle = 'display:block;width:auto;height:auto;max-width:100%;max-height:100%;object-fit:contain;object-position:' . $posX . ' ' . $posY . ';';
                } else {
                    $fitCss = $fit === 'stretch' ? 'fill' : $fit;
                    $objectPosition = $fit === 'cover'
                        ? ((int) ($props['focalX'] ?? 50) . '% ' . (int) ($props['focalY'] ?? 50) . '%')
                        : ($posX . ' ' . $posY);
                    $imageStyle = 'display:block;width:100%;height:100%;max-width:none;max-height:none;object-fit:' . $fitCss . ';object-position:' . $objectPosition . ';';
                }
            }

            $outerStyle = $style . $borderStyle . $spacingStyle . $radiusStyle;
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($outerStyle) . '"><figure class="h18-clean-front-image" style="' . esc_attr($figureStyle) . '">' . ($url !== '' ? '<img src="' . $url . '" alt="' . esc_attr((string) ($props['alt'] ?? '')) . '" style="' . esc_attr($imageStyle) . '">' : '') . '</figure></div>';
        }

        $background = sanitize_hex_color((string) ($props['background'] ?? '')) ?: 'transparent';
        $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
        $classes = $type === 'section' ? 'h18-clean-front-section' : 'h18-clean-front-container';
        $requiredHeight = self::requiredChildHeightPx((string) $node['id'], $byParent);
        $selectedHeight = $h * LayoutModel::ROW_PX;
        $minimumHeight = max($selectedHeight, $requiredHeight);
        if ($minimumHeight > 0) {
            $style .= 'min-height:' . $minimumHeight . 'px;';
        }
        $boxStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $padding . 'px;';
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

    /** @param array<string,mixed> $props */
    private static function spacingStyle(array $props): string
    {
        $gapX = max(0, min(200, (int) ($props['gapX'] ?? 0)));
        $gapY = max(0, min(200, (int) ($props['gapY'] ?? 0)));
        return 'margin-right:' . $gapX . 'px;margin-bottom:' . $gapY . 'px;';
    }

    /** @param array<string,array<int,array<string,mixed>>> $byParent */
    private static function requiredChildHeightPx(string $parentId, array $byParent): int
    {
        $required = 0;
        foreach ($byParent[$parentId] ?? [] as $child) {
            $g = isset($child['geometry']['desktop']) && is_array($child['geometry']['desktop']) ? $child['geometry']['desktop'] : [];
            $y = max(0, (int) ($g['y'] ?? 0));
            $h = max(0, (int) ($g['h'] ?? 0));
            $type = (string) ($child['type'] ?? '');
            if ($h > 0) {
                $childHeight = $h * LayoutModel::ROW_PX;
            } elseif ($type === 'image') {
                $childHeight = 10 * LayoutModel::ROW_PX;
            } elseif ($type === 'text') {
                $childHeight = 10 * LayoutModel::ROW_PX;
            } else {
                $childHeight = 8 * LayoutModel::ROW_PX;
            }
            if (in_array($type, ['section', 'container'], true)) {
                $childHeight = max($childHeight, self::requiredChildHeightPx((string) ($child['id'] ?? ''), $byParent));
            }
            $required = max($required, ($y * LayoutModel::ROW_PX) + $childHeight);
        }
        return $required;
    }
}
