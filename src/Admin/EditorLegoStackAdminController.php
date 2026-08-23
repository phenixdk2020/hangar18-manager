<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Persistence owner for LEGO-051 2D editor stack metadata.
 *
 * Existing page section persistence, LayoutParentKey and container/flex/grid
 * remain untouched. This option only stores the additive visual relation used
 * when multiple canonical Grid children share one column plus their responsive
 * height split.
 */
final class EditorLegoStackAdminController
{
    public const OPTION = 'hangar18_ultimate_designer_lego_stack_v0851';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 5);
    }

    /** @return array<string,mixed> */
    public static function store(): array
    {
        $store = get_option(self::OPTION, []);
        return is_array($store) ? $store : [];
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        check_admin_referer('h18_save_page_editor');
        if (!isset($_POST['h18_lego_stack_v0851']) || !is_array($_POST['h18_lego_stack_v0851'])) {
            return;
        }

        $slug = isset($_POST['page_slug']) ? sanitize_title((string) wp_unslash($_POST['page_slug'])) : '';
        if ($slug === '') {
            return;
        }

        $rawEntries = wp_unslash($_POST['h18_lego_stack_v0851']);
        $sections = [];
        foreach ($rawEntries as $rawEntry) {
            if (!is_array($rawEntry)) {
                continue;
            }
            $sectionKey = isset($rawEntry['SectionKey']) ? sanitize_key((string) $rawEntry['SectionKey']) : '';
            if ($sectionKey === '') {
                continue;
            }
            $decoded = json_decode(isset($rawEntry['StateJson']) ? (string) $rawEntry['StateJson'] : '', true);
            $decoded = is_array($decoded) ? $decoded : [];
            $root = sanitize_key((string) ($decoded['StackRootKey'] ?? ''));
            if ($root === $sectionKey) {
                $root = '';
            }
            $sections[$sectionKey] = [
                'SchemaVersion' => 1,
                'StackRootKey' => $root,
                'StackOrder' => max(0, (int) ($decoded['StackOrder'] ?? 0)),
                'DesktopPercent' => self::percent($decoded['DesktopPercent'] ?? 0),
                'TabletPercent' => self::percent($decoded['TabletPercent'] ?? 0),
                'MobilePercent' => self::percent($decoded['MobilePercent'] ?? 0),
            ];
        }

        $store = self::store();
        $store[$slug] = [
            'SchemaVersion' => 1,
            'SavedUtc' => gmdate('c'),
            'Sections' => $sections,
        ];
        update_option(self::OPTION, $store, false);
    }

    /** @param mixed $value */
    private static function percent($value): int
    {
        if (!is_numeric($value)) {
            return 0;
        }
        $percent = (int) $value;
        if ($percent <= 0) {
            return 0;
        }
        return max(10, min(90, $percent));
    }
}
