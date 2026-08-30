<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

final class AdminMenuBridge
{
    public static function register(): void
    {
        // EditorController registers the historical standalone top-level entry.
        // Clean 0.1.9 keeps its editor implementation but nests it below Manager.
        remove_action('admin_menu', [EditorController::class, 'menu']);
        add_action('admin_menu', [self::class, 'menu'], 6);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 9);
    }

    public static function menu(): void
    {
        add_submenu_page(
            AdminController::MENU,
            'Visual Designer',
            'Visual Designer',
            'edit_pages',
            'h18-clean-editor',
            [EditorController::class, 'render']
        );
    }

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_pages') || strpos($hook, 'h18-clean-editor') === false) {
            return;
        }
        wp_enqueue_media();
        wp_enqueue_style('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.css', [], H18_CLEAN_VERSION);
    }
}
