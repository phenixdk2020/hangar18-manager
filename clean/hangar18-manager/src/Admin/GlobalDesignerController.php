<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Model\TemplateLayoutModel;

final class GlobalDesignerController
{
    private const PAGE = 'h18-clean-header-footer';
    private const SAVE_ACTION = 'h18_clean_global_layout_save';
    private const RESTORE_ACTION = 'h18_clean_global_layout_restore';
    private const TEMPLATE_ACTION = 'h18_clean_global_template_action';
    private const NONCE_SAVE = 'h18_clean_global_layout_save';
    private const NONCE_RESTORE = 'h18_clean_global_layout_restore';
    private const NONCE_TEMPLATE = 'h18_clean_global_template_action';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 8);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 9);
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);
        add_action('admin_post_' . self::RESTORE_ACTION, [self::class, 'restore']);
        add_action('admin_post_' . self::TEMPLATE_ACTION, [self::class, 'templateAction']);
    }

    public static function menu(): void
    {
        remove_submenu_page(AdminController::MENU, self::PAGE);
        add_submenu_page(AdminController::MENU, 'Header / Footer Designer', 'Header / Footer', 'edit_theme_options', self::PAGE, [self::class, 'render']);
    }

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_theme_options') || strpos($hook, self::PAGE) === false) { return; }
        wp_enqueue_media();
        wp_enqueue_style('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.css', [], H18_CLEAN_VERSION);
        wp_enqueue_style('h18-global-designer-v0123', H18_CLEAN_URL . 'assets/global-designer-v0123.css', ['h18-clean-editor-v0125'], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-global-designer-v0123', H18_CLEAN_URL . 'assets/global-designer-v0123.js', ['h18-clean-editor-v0125'], H18_CLEAN_VERSION, true);
    }

    public static function render(): void
    {
        self::guard();
        TemplateLayoutModel::ensureMigrated();
        $part = self::part($_GET['part'] ?? 'header');
        $templates = TemplateLayoutModel::all($part);
        $templateId = sanitize_key((string) ($_GET['template'] ?? ''));
        if ($templateId === '' || !TemplateLayoutModel::exists($templateId, $part)) {
            $templateId = TemplateLayoutModel::defaultId($part);
        }
        if ($templateId === '' && $templates) { $templateId = (string) $templates[0]['id']; }
        if ($templateId === '') { $templateId = TemplateLayoutModel::create($part, $part === 'header' ? 'Header – Standard' : 'Footer – Standard'); }

        $meta = TemplateLayoutModel::meta($templateId) ?? [];
        $model = TemplateLayoutModel::model($templateId);
        $settings = TemplateLayoutModel::settings($templateId);
        $history = array_reverse(TemplateLayoutModel::history($templateId));
        $version = TemplateLayoutModel::version($templateId);
        $label = $part === 'header' ? 'Header' : 'Footer';
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));

        echo '<div class="wrap h18-clean-admin h18-global-designer">';
        echo '<h1>Visual Designer · Header / Footer</h1>';
        echo '<p class="description">Navngivne globale templates med egne modeller og versionshistorik. Header og Footer kan vælges uafhængigt pr. side.</p>';
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }

        echo '<nav class="nav-tab-wrapper h18-global-tabs"><a class="nav-tab' . ($part === 'header' ? ' nav-tab-active' : '') . '" href="' . esc_url(self::url('header')) . '">Headers</a><a class="nav-tab' . ($part === 'footer' ? ' nav-tab-active' : '') . '" href="' . esc_url(self::url('footer')) . '">Footers</a></nav>';

        echo '<section class="h18-global-template-manager"><div class="h18-global-template-list"><h2>' . esc_html($label) . '-templates</h2><table class="widefat striped"><thead><tr><th>Navn</th><th>Status</th><th>Version</th><th>Handling</th></tr></thead><tbody>';
        foreach ($templates as $row) {
            $id = (string) $row['id'];
            echo '<tr><td><strong>' . esc_html((string) $row['name']) . '</strong>' . (!empty($row['isDefault']) ? ' <span class="h18-manager-badge is-ok">Standard</span>' : '') . '</td><td>' . (!empty($row['active']) ? 'Aktiv' : 'Inaktiv') . '</td><td>v' . esc_html((string) ($row['version'] ?? 0)) . '</td><td><a class="button' . ($id === $templateId ? ' button-primary' : '') . '" href="' . esc_url(self::url($part, $id)) . '">Redigér</a> ';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($id) . '"><input type="hidden" name="operation" value="duplicate"><button class="button" type="submit">Duplikér</button></form> ';
            if (empty($row['isDefault'])) { echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($id) . '"><input type="hidden" name="operation" value="default"><button class="button" type="submit">Sæt standard</button></form>'; }
            echo '</td></tr>';
        }
        echo '</tbody></table></div><div class="h18-global-template-create"><h2>Ny ' . esc_html($label) . '</h2><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="operation" value="create"><input type="text" name="template_name" placeholder="Navn" required><button class="button button-primary" type="submit">Opret template</button></form></div></section>';

        echo '<div class="h18-global-statusbar"><strong>' . esc_html((string) ($meta['name'] ?? $label)) . '</strong><span>Version v' . esc_html((string) $version) . '</span><span class="h18-manager-badge is-progress">Under udvikling</span></div>';
        echo '<form class="h18-global-rename" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($templateId) . '"><input type="hidden" name="operation" value="rename"><label>Templatenavn <input type="text" name="template_name" value="' . esc_attr((string) ($meta['name'] ?? '')) . '"></label><button class="button" type="submit">Omdøb</button></form>';

        echo '<form id="h18-clean-save-form" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::NONCE_SAVE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SAVE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($templateId) . '"><input type="hidden" id="h18-clean-model-json" name="model_json" value="' . esc_attr((string) wp_json_encode($model)) . '"><input type="hidden" id="h18-clean-change-note" name="change_note" value="">';

        echo '<section class="h18-global-settings"><label class="h18-clean-checkbox"><input type="checkbox" name="template_active" value="1"' . checked(!empty($meta['active']), true, false) . '> Template aktiv</label>';
        if ($part === 'header') { echo '<label class="h18-clean-checkbox"><input type="checkbox" name="global_sticky" value="1"' . checked(!empty($settings['sticky']), true, false) . '> Sticky Header</label><label class="h18-clean-checkbox"><input type="checkbox" name="global_overlay" value="1"' . checked(!empty($settings['overlay']), true, false) . '> Overlay første sektion</label>'; }
        echo '<label>Indre max-bredde px <input type="number" name="global_content_width" min="320" max="2400" value="' . esc_attr((string) ($settings['contentWidth'] ?? 1440)) . '"></label><p class="description">Theme-shell overtager endnu ikke frontend automatisk. Først tester vi templates og resolver uden risiko for dobbelt Header/Footer.</p></section>';

        echo '<div class="h18-clean-toolbar"><button type="button" class="button" id="h18-clean-undo" disabled>↶ Fortryd</button><button type="button" class="button" id="h18-clean-redo" disabled>↷ Gentag</button><span class="h18-clean-grid-label">' . esc_html($label) . ' · 120 units · 8 px lodret snap</span><button type="button" class="button" id="h18-global-local-preview">Forhåndsvis layout</button><button type="submit" class="button button-primary h18-clean-save">Gem ' . esc_html($label) . ' som ny version</button></div>';
        echo '<div class="h18-clean-workspace"><aside class="h18-clean-palette"><h2>Elementer</h2>';
        foreach (['section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede', 'button' => 'Knap', 'menu' => 'Menu'] as $type => $elementLabel) { echo '<button type="button" draggable="true" class="button h18-clean-add" data-type="' . esc_attr($type) . '">+ ' . esc_html($elementLabel) . '</button>'; }
        echo '<p class="description">Logo laves som Billede. Menu-elementet henter en eksisterende WordPress-menu som datakilde; Visual Designer styrer placering, farver, afstand og mobilvisning.</p></aside><main class="h18-clean-canvas-column"><div id="h18-clean-canvas" class="h18-clean-surface h18-clean-root" data-parent-id=""></div></main><aside class="h18-clean-inspector"><h2>Inspector</h2><div id="h18-clean-inspector"><p class="description">Vælg et element på canvas.</p></div></aside></div></form>';

        echo '<section class="h18-clean-history h18-global-history"><h2>' . esc_html((string) ($meta['name'] ?? $label)) . ' · gemte versioner</h2>';
        if (!$history) { echo '<p>Ingen gemte versioner endnu.</p>'; }
        else { echo '<table class="widefat striped"><thead><tr><th>Version</th><th>Gemt</th><th>Ændringer</th><th>Digest</th><th></th></tr></thead><tbody>'; foreach (array_slice($history, 0, 20) as $entry) { $entryVersion = (int) ($entry['version'] ?? 0); echo '<tr><td><strong>v' . esc_html((string) $entryVersion) . '</strong></td><td>' . esc_html((string) ($entry['savedUtc'] ?? '')) . '</td><td>' . esc_html((string) ($entry['note'] ?? '')) . '</td><td><code>' . esc_html(substr((string) ($entry['digest'] ?? ''), 0, 14)) . '…</code></td><td><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'; wp_nonce_field(self::NONCE_RESTORE); echo '<input type="hidden" name="action" value="' . esc_attr(self::RESTORE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($templateId) . '"><input type="hidden" name="version" value="' . esc_attr((string) $entryVersion) . '"><button type="submit" class="button">Gendan</button></form></td></tr>'; } echo '</tbody></table>'; }
        echo '</section></div>';
    }

    public static function save(): void
    {
        self::guard(); check_admin_referer(self::NONCE_SAVE); TemplateLayoutModel::ensureMigrated();
        $part = self::part($_POST['part'] ?? 'header'); $id = sanitize_key((string) ($_POST['template_id'] ?? ''));
        if (!TemplateLayoutModel::exists($id, $part)) { self::redirect($part, '', 'error', 'Template findes ikke.'); }
        $decoded = json_decode(isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '', true);
        if (!is_array($decoded)) { self::redirect($part, $id, 'error', 'Layoutmodellen er ikke gyldig JSON.'); }
        try {
            $normalized = LayoutModel::normalize($decoded);
            $settings = ['sticky' => !empty($_POST['global_sticky']), 'overlay' => !empty($_POST['global_overlay']), 'contentWidth' => absint($_POST['global_content_width'] ?? 1440)];
            $note = sanitize_text_field((string) wp_unslash($_POST['change_note'] ?? '')); if ($note === '') { $note = 'Opdateret ' . ($part === 'header' ? 'Header' : 'Footer') . '-template'; }
            TemplateLayoutModel::setActive($id, !empty($_POST['template_active']));
            $version = TemplateLayoutModel::saveVersion($id, $normalized, $settings, get_current_user_id(), $note);
            if (!hash_equals(LayoutModel::structuralDigest($normalized), LayoutModel::structuralDigest(TemplateLayoutModel::model($id)))) { throw new \RuntimeException('Save-verifikation fejlede.'); }
            self::redirect($part, $id, 'success', 'Template gemt og verificeret som v' . $version . '.');
        } catch (\Throwable $error) { self::redirect($part, $id, 'error', 'Gem fejlede: ' . $error->getMessage()); }
    }

    public static function restore(): void
    {
        self::guard(); check_admin_referer(self::NONCE_RESTORE); TemplateLayoutModel::ensureMigrated();
        $part = self::part($_POST['part'] ?? 'header'); $id = sanitize_key((string) ($_POST['template_id'] ?? '')); $version = absint($_POST['version'] ?? 0);
        $state = TemplateLayoutModel::exists($id, $part) ? TemplateLayoutModel::historyState($id, $version) : null;
        if ($state === null) { self::redirect($part, $id, 'error', 'Den valgte version findes ikke længere.'); }
        try { TemplateLayoutModel::saveVersion($id, $state['model'], $state['settings'], get_current_user_id(), 'Gendannet fra v' . $version); self::redirect($part, $id, 'success', 'Version v' . $version . ' er gendannet som en ny version.'); }
        catch (\Throwable $error) { self::redirect($part, $id, 'error', 'Gendannelse fejlede: ' . $error->getMessage()); }
    }

    public static function templateAction(): void
    {
        self::guard(); check_admin_referer(self::NONCE_TEMPLATE); TemplateLayoutModel::ensureMigrated();
        $part = self::part($_POST['part'] ?? 'header'); $operation = sanitize_key((string) ($_POST['operation'] ?? '')); $id = sanitize_key((string) ($_POST['template_id'] ?? ''));
        try {
            if ($operation === 'create') { $id = TemplateLayoutModel::create($part, (string) wp_unslash($_POST['template_name'] ?? '')); }
            elseif ($operation === 'duplicate') { $id = TemplateLayoutModel::duplicate($id); }
            elseif ($operation === 'rename') { TemplateLayoutModel::rename($id, (string) wp_unslash($_POST['template_name'] ?? '')); }
            elseif ($operation === 'default') { TemplateLayoutModel::setDefault($part, $id); }
            else { throw new \InvalidArgumentException('Ukendt template-handling.'); }
            self::redirect($part, $id, 'success', 'Template-handlingen er gennemført.');
        } catch (\Throwable $error) { self::redirect($part, $id, 'error', 'Template-handling fejlede: ' . $error->getMessage()); }
    }

    private static function guard(): void { if (!current_user_can('edit_theme_options')) { wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean')); } }
    private static function part($value): string { return sanitize_key((string) $value) === 'footer' ? 'footer' : 'header'; }
    private static function url(string $part, string $template = ''): string { $args = ['page' => self::PAGE, 'part' => self::part($part)]; if ($template !== '') { $args['template'] = sanitize_key($template); } return add_query_arg($args, admin_url('admin.php')); }
    private static function redirect(string $part, string $template, string $status, string $message): void { $args = ['page' => self::PAGE, 'part' => self::part($part), 'vd_status' => sanitize_key($status), 'vd_message' => $message]; if ($template !== '') { $args['template'] = sanitize_key($template); } wp_safe_redirect(add_query_arg($args, admin_url('admin.php'))); exit; }
}
