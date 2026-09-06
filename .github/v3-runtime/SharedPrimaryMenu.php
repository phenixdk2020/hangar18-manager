<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;

/**
 * Turns the historical Footer "Genveje" HTML text block into a real VDM menu
 * and keeps it bound to the menu used by the resolved Header.
 */
final class SharedPrimaryMenu
{
    private const LEGACY_FOOTER_NODE = 'text-footer-shortcuts-v0147';
    private const FOOTER_MENU_NODE = 'menu-footer-shortcuts-v3';
    private const DONE_OPTION = 'vdm_v3_alpha7_shared_primary_menu';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'syncFooterTemplates'], 55);
        add_filter('wp_nav_menu_args', [self::class, 'filterFooterMenuArgs'], 20);
    }

    /** @param array<string,mixed> $args @return array<string,mixed> */
    public static function filterFooterMenuArgs(array $args): array
    {
        $menuDomId = (string) ($args['menu_id'] ?? '');
        if ($menuDomId !== 'h18-clean-menu-list-' . self::FOOTER_MENU_NODE) {
            return $args;
        }
        $postId = is_singular('page') ? (int) get_queried_object_id() : 0;
        $menuId = self::headerMenuId($postId);
        if ($menuId > 0) {
            $args['menu'] = $menuId;
        }
        return $args;
    }

    public static function syncFooterTemplates(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        TemplateLayoutModel::ensureMigrated();
        $menuId = self::headerMenuId(0);
        if ($menuId <= 0) {
            return;
        }

        $updated = [];
        foreach (TemplateLayoutModel::all('footer') as $row) {
            $footerId = (string) ($row['id'] ?? '');
            if ($footerId === '') {
                continue;
            }
            $model = TemplateLayoutModel::model($footerId);
            [$model, $changed] = self::ensureMenuNode($model, $menuId);
            if (!$changed) {
                continue;
            }
            TemplateLayoutModel::saveVersion(
                $footerId,
                $model,
                TemplateLayoutModel::settings($footerId),
                get_current_user_id(),
                'V3 Alpha.7: Footer Genveje følger Headerens hovedmenu'
            );
            $updated[] = $footerId;
        }

        update_option(self::DONE_OPTION, [
            'version' => VDM_VERSION,
            'menuId' => $menuId,
            'updatedTemplates' => $updated,
            'checkedUtc' => gmdate('c'),
        ], false);
    }

    private static function headerMenuId(int $postId): int
    {
        TemplateLayoutModel::ensureMigrated();
        $headerId = $postId > 0
            ? TemplateLayoutModel::resolveId($postId, 'header')
            : TemplateLayoutModel::defaultId('header');
        if ($headerId === '' || !TemplateLayoutModel::exists($headerId, 'header')) {
            return 0;
        }
        $nodes = (array) (TemplateLayoutModel::model($headerId)['nodes'] ?? []);

        // Prefer the explicit primary menu when available, otherwise the first
        // valid Menu element in the resolved Header.
        foreach ([true, false] as $primaryOnly) {
            foreach ($nodes as $node) {
                if (!is_array($node) || (string) ($node['type'] ?? '') !== 'menu') {
                    continue;
                }
                $id = (string) ($node['id'] ?? '');
                if ($primaryOnly && stripos($id, 'primary') === false) {
                    continue;
                }
                $menuId = absint($node['props']['menuId'] ?? 0);
                if ($menuId > 0) {
                    return $menuId;
                }
            }
        }
        return 0;
    }

    /** @param array<string,mixed> $model @return array{0:array<string,mixed>,1:bool} */
    private static function ensureMenuNode(array $model, int $menuId): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        $changed = false;
        $foundMenu = false;

        foreach ($nodes as &$node) {
            if (!is_array($node)) {
                continue;
            }
            $id = (string) ($node['id'] ?? '');
            if ($id === self::FOOTER_MENU_NODE && (string) ($node['type'] ?? '') === 'menu') {
                $foundMenu = true;
                $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
                if (absint($props['menuId'] ?? 0) !== $menuId) {
                    $props['menuId'] = $menuId;
                    $node['props'] = $props;
                    $changed = true;
                }
                continue;
            }
            if ($id !== self::LEGACY_FOOTER_NODE || (string) ($node['type'] ?? '') !== 'text') {
                continue;
            }

            $old = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            $node['id'] = self::FOOTER_MENU_NODE;
            $node['type'] = 'menu';
            $node['props'] = [
                'menuId' => $menuId,
                'orientation' => 'vertical',
                'align' => 'left',
                'mobileMode' => 'vertical',
                'mobilePresentation' => 'dropdown',
                'mobileCloseOnSelect' => true,
                'mobileCloseOutside' => true,
                'textColor' => (string) ($old['textColor'] ?? '#f2f0e8'),
                'hoverTextColor' => '#c3ae83',
                'activeTextColor' => '#c3ae83',
                'background' => (string) ($old['background'] ?? '#30382a'),
                'backgroundTransparent' => array_key_exists('backgroundTransparent', $old) ? (bool) $old['backgroundTransparent'] : true,
                'fontSize' => (int) ($old['fontSize'] ?? 14),
                'fontWeight' => (int) ($old['fontWeight'] ?? 400),
                'menuGap' => 3,
                'paddingX' => 0,
                'paddingY' => 0,
                'radius' => (int) ($old['radius'] ?? 0),
                'borderWidth' => (int) ($old['borderWidth'] ?? 0),
                'borderColor' => (string) ($old['borderColor'] ?? '#000000'),
                'gapX' => (int) ($old['gapX'] ?? 0),
                'gapY' => (int) ($old['gapY'] ?? 0),
                'offsetX' => (int) ($old['offsetX'] ?? 0),
                'offsetY' => (int) ($old['offsetY'] ?? 0),
            ];
            $foundMenu = true;
            $changed = true;
        }
        unset($node);

        if (!$foundMenu) {
            return [$model, false];
        }
        $model['nodes'] = $nodes;
        return [LayoutModel::normalize($model), $changed];
    }

    private function __construct() {}
}
