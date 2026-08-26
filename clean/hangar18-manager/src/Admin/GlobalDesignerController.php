<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

use Hangar18\Clean\Model\GlobalLayoutModel;
use Hangar18\Clean\Model\LayoutModel;

final class GlobalDesignerController
{
    private const PAGE = 'h18-clean-header-footer';
    private const SAVE_ACTION = 'h18_clean_global_layout_save';
    private const RESTORE_ACTION = 'h18_clean_global_layout_restore';
    private const NONCE_SAVE = 'h18_clean_global_layout_save';
    private const NONCE_RESTORE = 'h18_clean_global_layout_restore';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 8);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 9);
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);
        add_action('admin_post_' . self::RESTORE_ACTION, [self::class, 'restore']);
    }

    public static function menu(): void
    {
        remove_submenu_page(AdminController::MENU, self::PAGE);
        add_submenu_page(
            AdminController::MENU,
            'Header / Footer Designer',
            'Header / Footer',
            'edit_theme_options',
            self::PAGE,
            [self::class, 'render']
        );
    }

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_theme_options') || strpos($hook, self::PAGE) === false) {
            return;
        }
        wp_enqueue_media();
        wp_enqueue_style('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.css', [], H18_CLEAN_VERSION);
        wp_enqueue_style('h18-global-designer-v0123', H18_CLEAN_URL . 'assets/global-designer-v0123.css', ['h18-clean-editor-v0123-ux'], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-global-designer-v0123', H18_CLEAN_URL . 'assets/global-designer-v0123.js', ['h18-clean-editor-v0123-ux'], H18_CLEAN_VERSION, true);
    }

    public static function render(): void
    {
        self::guard();
        $part = self::part($_GET['part'] ?? 'header');
        $model = GlobalLayoutModel::get($part);
        $settings = GlobalLayoutModel::settings($part);
        $history = array_reverse(GlobalLayoutModel::history($part));
        $version = GlobalLayoutModel::version($part);
        $label = $part === 'header' ? 'Header' : 'Footer';
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));

        echo '<div class="wrap h18-clean-admin h18-global-designer">';
        echo '<h1>Visual Designer · Header / Footer</h1>';
        echo '<p class="description">Globale layouts med egen versionshistorik. Samme 120-unit / 8-px layoutmotor som almindelige sider.</p>';
        if ($message !== '') {
            echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>';
        }

        echo '<nav class="nav-tab-wrapper h18-global-tabs">';
        echo '<a class="nav-tab' . ($part === 'header' ? ' nav-tab-active' : '') . '" href="' . esc_url(self::url('header')) . '">Header</a>';
        echo '<a class="nav-tab' . ($part === 'footer' ? ' nav-tab-active' : '') . '" href="' . esc_url(self::url('footer')) . '">Footer</a>';
        echo '</nav>';

        echo '<div class="h18-global-statusbar"><strong>' . esc_html($label) . '</strong><span>Version v' . esc_html((string) $version) . '</span><span class="h18-manager-badge is-progress">Global Designer · fase 1</span></div>';

        echo '<form id="h18-clean-save-form" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::NONCE_SAVE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SAVE_ACTION) . '">';
        echo '<input type="hidden" name="part" value="' . esc_attr($part) . '">';
        echo '<input type="hidden" id="h18-clean-model-json" name="model_json" value="' . esc_attr((string) wp_json_encode($model)) . '">';
        echo '<input type="hidden" id="h18-clean-change-note" name="change_note" value="">';

        echo '<section class="h18-global-settings">';
        echo '<label class="h18-clean-checkbox"><input type="checkbox" name="global_enabled" value="1"' . checked(!empty($settings['enabled']), true, false) . '> Layout er klargjort til frontend</label>';
        if ($part === 'header') {
            echo '<label class="h18-clean-checkbox"><input type="checkbox" name="global_sticky" value="1"' . checked(!empty($settings['sticky']), true, false) . '> Sticky Header</label>';
            echo '<label class="h18-clean-checkbox"><input type="checkbox" name="global_overlay" value="1"' . checked(!empty($settings['overlay']), true, false) . '> Overlay første sektion</label>';
        }
        echo '<label>Indre max-bredde px <input type="number" name="global_content_width" min="320" max="2400" value="' . esc_attr((string) ($settings['contentWidth'] ?? 1440)) . '"></label>';
        echo '<p class="description">"Klargjort til frontend" gemmer indstillingen, men 0.1.23 overtager ikke endnu temaets Header/Footer automatisk. Det sker først gennem Theme-shell integration, så vi undgår dobbelt Header/Footer.</p>';
        echo '</section>';

        echo '<div class="h18-clean-toolbar">';
        echo '<button type="button" class="button" id="h18-clean-undo" disabled>↶ Fortryd</button>';
        echo '<button type="button" class="button" id="h18-clean-redo" disabled>↷ Gentag</button>';
        echo '<span class="h18-clean-grid-label">' . esc_html($label) . ' · 120 units · 8 px lodret snap</span>';
        echo '<button type="button" class="button" id="h18-global-local-preview">Forhåndsvis layout</button>';
        echo '<button type="submit" class="button button-primary h18-clean-save">Gem ' . esc_html($label) . ' som ny version</button>';
        echo '</div>';

        echo '<div class="h18-clean-workspace">';
        echo '<aside class="h18-clean-palette"><h2>Elementer</h2>';
        foreach (['section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede'] as $type => $elementLabel) {
            echo '<button type="button" draggable="true" class="button h18-clean-add" data-type="' . esc_attr($type) . '">+ ' . esc_html($elementLabel) . '</button>';
        }
        echo '<p class="description">Fase 1 bruger de samme grundelementer som Side Designer. Logo kan laves som Billede. Menu/Knap/Ikon kommer efter Header/Footer-layoutmotoren er testet.</p></aside>';
        echo '<main class="h18-clean-canvas-column"><div id="h18-clean-canvas" class="h18-clean-surface h18-clean-root" data-parent-id=""></div></main>';
        echo '<aside class="h18-clean-inspector"><h2>Inspector</h2><div id="h18-clean-inspector"><p class="description">Vælg et element på canvas.</p></div></aside>';
        echo '</div></form>';

        echo '<section class="h18-clean-history h18-global-history"><h2>' . esc_html($label) . ' · gemte versioner</h2>';
        if (!$history) {
            echo '<p>Ingen gemte versioner endnu.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Version</th><th>Gemt</th><th>Ændringer</th><th>Digest</th><th></th></tr></thead><tbody>';
            foreach (array_slice($history, 0, 20) as $entry) {
                $entryVersion = (int) ($entry['version'] ?? 0);
                echo '<tr><td><strong>v' . esc_html((string) $entryVersion) . '</strong></td><td>' . esc_html((string) ($entry['savedUtc'] ?? '')) . '</td><td>' . esc_html((string) ($entry['note'] ?? '')) . '</td><td><code>' . esc_html(substr((string) ($entry['digest'] ?? ''), 0, 14)) . '…</code></td><td>';
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" onsubmit="return confirm(\'Gendan denne ' . esc_js($label) . '-version? Den nuværende tilstand gemmes først som en ny version.\');">';
                wp_nonce_field(self::NONCE_RESTORE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::RESTORE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="version" value="' . esc_attr((string) $entryVersion) . '"><button type="submit" class="button">Gendan</button></form></td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</section></div>';
    }

    public static function save(): void
    {
        self::guard();
        check_admin_referer(self::NONCE_SAVE);
        $part = self::part($_POST['part'] ?? 'header');
        $rawJson = isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '';
        $decoded = json_decode($rawJson, true);
        if (!is_array($decoded)) {
            self::redirect($part, 'error', 'Layoutmodellen er ikke gyldig JSON.');
        }
        try {
            $normalized = LayoutModel::normalize($decoded);
            $settings = [
                'enabled' => !empty($_POST['global_enabled']),
                'sticky' => !empty($_POST['global_sticky']),
                'overlay' => !empty($_POST['global_overlay']),
                'contentWidth' => absint($_POST['global_content_width'] ?? 1440),
            ];
            $note = sanitize_text_field((string) wp_unslash($_POST['change_note'] ?? ''));
            if ($note === '') {
                $note = 'Opdateret global ' . ($part === 'header' ? 'Header' : 'Footer');
            }
            $version = GlobalLayoutModel::saveVersion($part, $normalized, $settings, get_current_user_id(), $note);
            $saved = GlobalLayoutModel::get($part);
            if (!hash_equals(LayoutModel::structuralDigest($normalized), LayoutModel::structuralDigest($saved))) {
                throw new \RuntimeException('Save-verifikation fejlede for globalt layout.');
            }
            self::redirect($part, 'success', ($part === 'header' ? 'Header' : 'Footer') . ' gemt og verificeret som v' . $version . '.');
        } catch (\Throwable $error) {
            self::redirect($part, 'error', 'Gem fejlede: ' . $error->getMessage());
        }
    }

    public static function restore(): void
    {
        self::guard();
        check_admin_referer(self::NONCE_RESTORE);
        $part = self::part($_POST['part'] ?? 'header');
        $version = absint($_POST['version'] ?? 0);
        $state = GlobalLayoutModel::historyState($part, $version);
        if ($state === null) {
            self::redirect($part, 'error', 'Den valgte version findes ikke længere.');
        }
        try {
            GlobalLayoutModel::saveVersion(
                $part,
                $state['model'],
                $state['settings'],
                get_current_user_id(),
                'Gendannet fra v' . $version
            );
            self::redirect($part, 'success', 'Version v' . $version . ' er gendannet som en ny version.');
        } catch (\Throwable $error) {
            self::redirect($part, 'error', 'Gendannelse fejlede: ' . $error->getMessage());
        }
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_theme_options')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
        }
    }

    private static function part($value): string
    {
        return sanitize_key((string) $value) === 'footer' ? 'footer' : 'header';
    }

    private static function url(string $part): string
    {
        return add_query_arg(['page' => self::PAGE, 'part' => self::part($part)], admin_url('admin.php'));
    }

    private static function redirect(string $part, string $status, string $message): void
    {
        wp_safe_redirect(add_query_arg([
            'page' => self::PAGE,
            'part' => self::part($part),
            'vd_status' => sanitize_key($status),
            'vd_message' => $message,
        ], admin_url('admin.php')));
        exit;
    }
}
