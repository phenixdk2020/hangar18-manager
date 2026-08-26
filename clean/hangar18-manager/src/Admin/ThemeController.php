<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

final class ThemeController
{
    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 9);
    }

    public static function menu(): void
    {
        add_submenu_page(
            AdminController::MENU,
            'Tema / Shell',
            'Tema',
            'edit_theme_options',
            'h18-clean-theme',
            [self::class, 'render']
        );
    }

    public static function render(): void
    {
        self::guard();
        $theme = wp_get_theme();
        $parent = $theme->parent();
        $registered = get_registered_nav_menus();
        $locations = get_nav_menu_locations();

        echo '<div class="wrap h18-manager-admin">';
        echo '<h1>Tema / Shell</h1>';
        echo '<p class="h18-manager-description">Temaet leverer WordPress-runtime og fallback. Visual Designer Manager skal gradvist overtage den visuelle sandhed for globalt design, Header, Footer og Menu-præsentation uden at gøre temaet til en parallel Designer.</p>';

        echo '<div class="h18-manager-two-col">';
        echo '<section class="h18-manager-card"><h2>Aktivt tema</h2><dl class="h18-manager-dl">';
        self::row('Navn', (string) $theme->get('Name'));
        self::row('Version', (string) $theme->get('Version'));
        self::row('Stylesheet', $theme->get_stylesheet(), true);
        self::row('Template', $theme->get_template(), true);
        self::row('Theme URI', (string) $theme->get('ThemeURI'));
        echo '</dl>';
        echo '<p class="h18-manager-actions"><a class="button" href="' . esc_url(admin_url('themes.php')) . '">WordPress Temaer</a>';
        if (current_user_can('customize')) {
            echo '<a class="button" href="' . esc_url(admin_url('customize.php')) . '">Tilpas</a>';
        }
        echo '<a class="button button-primary" href="' . esc_url(admin_url('admin.php?page=h18-clean-export')) . '">Export Tema</a></p></section>';

        echo '<section class="h18-manager-card"><h2>Parent theme</h2>';
        if ($parent instanceof \WP_Theme) {
            echo '<dl class="h18-manager-dl">';
            self::row('Navn', (string) $parent->get('Name'));
            self::row('Version', (string) $parent->get('Version'));
            self::row('Template', $parent->get_template(), true);
            echo '</dl><p class="description">Ved en senere fuld Theme-export skal parent theme kunne medtages sammen med child theme, så pakken er transportabel.</p>';
        } else {
            echo '<p>Det aktive tema har ikke et parent theme.</p>';
        }
        echo '</section></div>';

        echo '<div class="h18-manager-two-col">';
        echo '<section class="h18-manager-card"><h2>Theme supports</h2><table class="widefat striped"><thead><tr><th>Funktion</th><th>Status</th></tr></thead><tbody>';
        foreach ([
            'title-tag' => 'Title tag',
            'custom-logo' => 'Custom logo',
            'menus' => 'Klassiske menuer',
            'post-thumbnails' => 'Featured images',
            'html5' => 'HTML5',
            'align-wide' => 'Wide alignment',
        ] as $feature => $label) {
            $supported = current_theme_supports($feature);
            echo '<tr><td>' . esc_html($label) . '<br><code>' . esc_html($feature) . '</code></td><td><span class="h18-manager-badge ' . ($supported ? 'is-ok' : '') . '">' . ($supported ? 'Ja' : 'Nej') . '</span></td></tr>';
        }
        echo '</tbody></table></section>';

        echo '<section class="h18-manager-card"><h2>Menu-locations fra temaet</h2>';
        if (!$registered) {
            echo '<p>Temaet registrerer ingen klassiske menu-locations.</p><p class="description">Det er ikke en blokering for Visual Designer: et fremtidigt Menu-element kan vælge navigation direkte uden at være bundet til en theme-location.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Location</th><th>Tildelt navigation</th></tr></thead><tbody>';
            foreach ($registered as $key => $label) {
                $menuId = (int) ($locations[$key] ?? 0);
                $menu = $menuId > 0 ? wp_get_nav_menu_object($menuId) : false;
                echo '<tr><td><strong>' . esc_html((string) $label) . '</strong><br><code>' . esc_html((string) $key) . '</code></td><td>' . esc_html($menu ? (string) $menu->name : 'Ikke tildelt') . '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '<p><a class="button" href="' . esc_url(admin_url('admin.php?page=h18-clean-menu')) . '">Administrér Menu-data</a></p></section></div>';

        echo '<section class="h18-manager-card"><h2>Ansvarsgrænse</h2><table class="widefat striped"><thead><tr><th>Område</th><th>Ansvar</th></tr></thead><tbody>';
        echo '<tr><td>WordPress templates/hooks/fallback</td><td><strong>Tema</strong></td></tr>';
        echo '<tr><td>Navigationens punkter/hierarki/links</td><td><strong>Menu-data i WordPress / Visual Designer Manager</strong></td></tr>';
        echo '<tr><td>Menuens farver, typografi, spacing, hamburger/drawer</td><td><strong>Visual Designer Menu-element</strong> – senere</td></tr>';
        echo '<tr><td>Header/Footer layout</td><td><strong>Global Header/Footer Designer</strong> – senere</td></tr>';
        echo '<tr><td>Global palette, typografi og sidebredder</td><td><strong>Globalt design</strong> – senere</td></tr>';
        echo '</tbody></table></section>';

        echo '<section class="h18-manager-card h18-manager-module"><h2>Shell integration</h2><p><strong>Status:</strong> Ikke overtaget endnu.</p><p>Den aktive offentlige theme-runtime ændres ikke af denne administrationsside. Først når Globalt design og Header/Footer-modellerne er QA-godkendt, kan temaet reduceres til en tynd shell med sikker fallback.</p></section>';
        echo '</div>';
    }

    private static function row(string $label, string $value, bool $code = false): void
    {
        echo '<dt>' . esc_html($label) . '</dt><dd>' . ($code ? '<code>' . esc_html($value) . '</code>' : esc_html($value !== '' ? $value : '—')) . '</dd>';
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_theme_options')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
        }
    }
}
