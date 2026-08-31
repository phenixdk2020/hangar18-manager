<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Modules\ModuleStore;
use VisualDesignerManager\Modules\VehicleFieldRegistry;

final class VehicleAdminController
{
    public const PAGE = 'h18-clean-vehicles';
    public const FIELDS_PAGE = 'h18-clean-vehicle-fields';
    private const SAVE_ACTION = 'h18_vd_vehicle_save';
    private const DELETE_ACTION = 'h18_vd_vehicle_delete';
    private const FIELD_SAVE_ACTION = 'h18_vd_vehicle_fields_save';
    private const SAVE_NONCE = 'h18_vd_vehicle_save';
    private const DELETE_NONCE = 'h18_vd_vehicle_delete';
    private const FIELD_SAVE_NONCE = 'h18_vd_vehicle_fields_save';

    public static function register(): void
    {
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'saveVehicle']);
        add_action('admin_post_' . self::DELETE_ACTION, [self::class, 'deleteVehicle']);
        add_action('admin_post_' . self::FIELD_SAVE_ACTION, [self::class, 'saveFields']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_pages') || (strpos($hook, self::PAGE) === false && strpos($hook, self::FIELDS_PAGE) === false)) {
            return;
        }
        wp_enqueue_media();
        wp_enqueue_style('h18-vd-vehicles-v0170', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.css', ['h18-clean-manager-admin'], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-vd-vehicles-v0170', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.js', [], H18_CLEAN_VERSION, true);
    }

    public static function render(): void
    {
        self::guard();
        $editId = absint($_GET['record'] ?? 0);
        $editing = $editId > 0 ? ModuleStore::get($editId) : null;
        if ($editId > 0 && ($editing === null || (string) ($editing['module'] ?? '') !== 'vehicles')) {
            $editing = null;
            $editId = 0;
        }
        $records = ModuleStore::listRecords('vehicles', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC']);
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));

        echo '<div class="wrap h18-manager-admin h18-vd-vehicles"><h1>Køretøjer</h1><p class="description">Canonical Køretøjsmodul · data gemmes i den fælles Visual Designer ModuleStore.</p>';
        if ($message !== '') {
            echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>';
        }
        echo '<div class="h18-manager-toolbar"><a class="button button-primary" href="' . esc_url(self::url()) . '">+ Nyt køretøj</a><a class="button" href="' . esc_url(self::fieldsUrl()) . '">Køretøjsfelter</a></div>';

        echo '<div class="h18-vd-vehicle-layout"><section class="h18-manager-card h18-vd-vehicle-list"><h2>Registrerede køretøjer</h2>';
        echo '<table class="widefat striped"><thead><tr><th>Sort.</th><th>Køretøj</th><th>Kategori</th><th>Status</th><th>Billeder</th><th>Handlinger</th></tr></thead><tbody>';
        if (!$records) { echo '<tr><td colspan="6">Ingen køretøjer oprettet endnu.</td></tr>'; }
        foreach ($records as $item) {
            $postId = (int) ($item['postId'] ?? 0);
            $record = is_array($item['record'] ?? null) ? $item['record'] : [];
            $fields = is_array($record['fields'] ?? null) ? $record['fields'] : [];
            $images = is_array($fields['imageIds'] ?? null) ? $fields['imageIds'] : [];
            $imageCount = count(array_unique(array_filter(array_merge([(int) ($record['featuredMediaId'] ?? 0)], array_map('absint', $images)))));
            echo '<tr><td>' . esc_html((string) ((int) ($record['sortOrder'] ?? 0))) . '</td><td><strong>' . esc_html((string) ($record['title'] ?? 'Køretøj')) . '</strong><br><code>' . esc_html((string) ($record['id'] ?? '')) . '</code></td><td>' . esc_html((string) ($fields['category'] ?? '')) . '</td><td><span class="h18-manager-badge ' . ((string) ($record['status'] ?? '') === 'publish' ? 'is-ok' : '') . '">' . esc_html(self::statusLabel((string) ($record['status'] ?? 'draft'))) . '</span></td><td>' . esc_html((string) $imageCount) . '</td><td class="h18-manager-actions"><a class="button" href="' . esc_url(self::url(['record' => $postId])) . '">Redigér</a>';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" onsubmit="return confirm(\'Slet køretøjet permanent?\');">';
            wp_nonce_field(self::DELETE_NONCE);
            echo '<input type="hidden" name="action" value="' . esc_attr(self::DELETE_ACTION) . '"><input type="hidden" name="record_post_id" value="' . esc_attr((string) $postId) . '"><button class="button button-link-delete" type="submit">Slet</button></form></td></tr>';
        }
        echo '</tbody></table></section>';

        self::renderForm($editId, $editing);
        echo '</div></div>';
    }

    /** @param array<string,mixed>|null $record */
    private static function renderForm(int $postId, ?array $record): void
    {
        $record = is_array($record) ? $record : [];
        $fields = is_array($record['fields'] ?? null) ? $record['fields'] : [];
        $attributes = [];
        foreach ((array) ($record['attributes'] ?? []) as $attribute) {
            if (is_array($attribute) && !empty($attribute['key'])) { $attributes[(string) $attribute['key']] = $attribute; }
        }
        $gallery = is_array($fields['imageIds'] ?? null) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        $featured = absint($record['featuredMediaId'] ?? 0);
        echo '<section class="h18-manager-card h18-vd-vehicle-editor"><h2>' . esc_html($postId > 0 ? 'Redigér køretøj' : 'Nyt køretøj') . '</h2><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::SAVE_NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SAVE_ACTION) . '"><input type="hidden" name="record_post_id" value="' . esc_attr((string) $postId) . '">';
        echo '<label>Navn / titel<input required type="text" name="title" value="' . esc_attr((string) ($record['title'] ?? '')) . '"></label>';
        echo '<div class="h18-clean-field-grid"><label>Kategori<input type="text" name="category" value="' . esc_attr((string) ($fields['category'] ?? '')) . '"></label><label>Status<select name="status"><option value="draft"' . selected((string) ($record['status'] ?? 'draft'), 'draft', false) . '>Kladde</option><option value="publish"' . selected((string) ($record['status'] ?? 'draft'), 'publish', false) . '>Publiceret</option><option value="archive"' . selected((string) ($record['status'] ?? 'draft'), 'archive', false) . '>Arkiveret</option></select></label><label>Sortering<input type="number" name="sort_order" value="' . esc_attr((string) ((int) ($record['sortOrder'] ?? 0))) . '"></label></div>';
        echo '<label>Kort beskrivelse<textarea name="summary" rows="3">' . esc_textarea((string) ($record['summary'] ?? '')) . '</textarea></label>';
        echo '<label>Beskrivelse<textarea name="description" rows="7">' . esc_textarea(wp_strip_all_tags((string) ($fields['description'] ?? ''))) . '</textarea></label>';

        echo '<div class="h18-vd-media-grid"><div><h3>Primært billede</h3><input id="h18-vd-featured-media" type="hidden" name="featured_media_id" value="' . esc_attr((string) $featured) . '"><div class="h18-vd-media-preview" data-media-preview="h18-vd-featured-media">' . self::imagePreview([$featured]) . '</div><button type="button" class="button h18-vd-media-pick" data-target="h18-vd-featured-media" data-multiple="0">Vælg primært billede</button><button type="button" class="button-link h18-vd-media-clear" data-target="h18-vd-featured-media">Ryd</button></div>';
        echo '<div><h3>Galleri</h3><input id="h18-vd-gallery-media" type="hidden" name="image_ids" value="' . esc_attr(implode(',', $gallery)) . '"><div class="h18-vd-media-preview is-gallery" data-media-preview="h18-vd-gallery-media">' . self::imagePreview($gallery) . '</div><button type="button" class="button h18-vd-media-pick" data-target="h18-vd-gallery-media" data-multiple="1">Vælg galleribilleder</button><button type="button" class="button-link h18-vd-media-clear" data-target="h18-vd-gallery-media">Ryd</button></div></div>';

        echo '<h3>Tekniske data</h3><p class="description">Felterne styres centralt under Køretøjsfelter. Tomme felter kan gemmes og udfyldes senere.</p><div class="h18-vd-technical-fields">';
        foreach (VehicleFieldRegistry::all() as $definition) {
            if (empty($definition['enabled'])) { continue; }
            $key = (string) $definition['id'];
            $value = $attributes[$key]['value'] ?? '';
            $label = (string) $definition['label'] . ((string) $definition['unit'] !== '' ? ' (' . (string) $definition['unit'] . ')' : '');
            $name = 'technical[' . $key . ']';
            $type = (string) $definition['type'];
            if ($type === 'boolean') {
                echo '<label class="h18-clean-checkbox"><input type="checkbox" name="' . esc_attr($name) . '" value="1"' . checked((bool) $value, true, false) . '> ' . esc_html($label) . '</label>';
            } elseif (in_array($type, ['textarea', 'richtext'], true)) {
                echo '<label>' . esc_html($label) . '<textarea name="' . esc_attr($name) . '" rows="3">' . esc_textarea((string) $value) . '</textarea></label>';
            } else {
                $inputType = in_array($type, ['number', 'integer'], true) ? 'number' : ($type === 'date' ? 'date' : 'text');
                $step = $type === 'number' ? ' step="any"' : '';
                echo '<label>' . esc_html($label) . '<input type="' . esc_attr($inputType) . '"' . $step . ' name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '"></label>';
            }
        }
        echo '</div><p><button class="button button-primary" type="submit">' . esc_html($postId > 0 ? 'Gem køretøj' : 'Opret køretøj') . '</button>';
        if ($postId > 0) { echo ' <a class="button" href="' . esc_url(self::url()) . '">Annullér</a>'; }
        echo '</p></form></section>';
    }

    public static function renderFields(): void
    {
        self::guard();
        $rows = VehicleFieldRegistry::all();
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));
        echo '<div class="wrap h18-manager-admin h18-vd-vehicles"><h1>Køretøjsfelter</h1><p class="description">Definér de genbrugelige tekniske datafelter. Felt-ID bevares stabilt, så eksisterende køretøjsdata ikke flytter sig ved omdøbning.</p>';
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }
        echo '<p><a class="button" href="' . esc_url(self::url()) . '">← Køretøjer</a></p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::FIELD_SAVE_NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::FIELD_SAVE_ACTION) . '"><div class="h18-manager-card"><div class="h18-vd-field-toolbar"><h2>Tekniske felter</h2><button type="button" class="button" id="h18-vd-add-vehicle-field">+ Tilføj felt</button></div><div id="h18-vd-vehicle-field-rows">';
        foreach ($rows as $row) { self::fieldRow($row); }
        echo '</div><p><button class="button button-primary" type="submit">Gem feltopsætning</button></p></div></form></div>';
    }

    /** @param array<string,mixed> $row */
    private static function fieldRow(array $row): void
    {
        echo '<div class="h18-vd-field-row" data-vehicle-field-row><input type="hidden" name="field_id[]" value="' . esc_attr((string) ($row['id'] ?? '')) . '"><label>Navn<input required type="text" name="field_label[]" value="' . esc_attr((string) ($row['label'] ?? '')) . '"></label><label>Type<select name="field_type[]">';
        foreach (['text' => 'Tekst', 'textarea' => 'Flere linjer', 'number' => 'Tal', 'integer' => 'Heltal', 'boolean' => 'Ja/nej', 'date' => 'Dato'] as $type => $label) {
            echo '<option value="' . esc_attr($type) . '"' . selected((string) ($row['type'] ?? 'text'), $type, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select></label><label>Enhed<input type="text" name="field_unit[]" value="' . esc_attr((string) ($row['unit'] ?? '')) . '" placeholder="fx kg"></label><label>Rækkefølge<input type="number" name="field_order[]" value="' . esc_attr((string) ((int) ($row['order'] ?? 0))) . '"></label><label class="h18-clean-checkbox"><input type="checkbox" name="field_enabled[]" value="1" checked> Aktiv</label><button type="button" class="button-link-delete h18-vd-remove-vehicle-field">Fjern</button></div>';
    }

    public static function saveVehicle(): void
    {
        self::guard();
        check_admin_referer(self::SAVE_NONCE);
        $postId = absint($_POST['record_post_id'] ?? 0);
        $title = sanitize_text_field((string) wp_unslash($_POST['title'] ?? ''));
        if ($title === '') { self::redirect(self::PAGE, 'error', 'Køretøjet skal have et navn.'); }
        $technical = isset($_POST['technical']) && is_array($_POST['technical']) ? wp_unslash($_POST['technical']) : [];
        $attributes = [];
        foreach (VehicleFieldRegistry::all() as $definition) {
            if (empty($definition['enabled'])) { continue; }
            $key = (string) $definition['id'];
            $raw = $technical[$key] ?? ($definition['type'] === 'boolean' ? false : '');
            $label = (string) $definition['label'] . ((string) $definition['unit'] !== '' ? ' (' . (string) $definition['unit'] . ')' : '');
            $attributes[] = [
                'key' => $key,
                'label' => $label,
                'type' => (string) $definition['type'],
                'value' => $raw,
                'enabled' => true,
                'order' => (int) $definition['order'],
            ];
        }
        $raw = [
            'title' => $title,
            'status' => sanitize_key((string) ($_POST['status'] ?? 'draft')),
            'sortOrder' => (int) ($_POST['sort_order'] ?? 0),
            'featuredMediaId' => absint($_POST['featured_media_id'] ?? 0),
            'summary' => sanitize_textarea_field((string) wp_unslash($_POST['summary'] ?? '')),
            'fields' => [
                'category' => sanitize_text_field((string) wp_unslash($_POST['category'] ?? '')),
                'description' => wp_kses_post(nl2br(esc_html((string) wp_unslash($_POST['description'] ?? '')), false)),
                'imageIds' => self::mediaIds((string) wp_unslash($_POST['image_ids'] ?? '')),
            ],
            'attributes' => $attributes,
        ];
        $result = ModuleStore::save('vehicles', $raw, $postId);
        if (is_wp_error($result)) { self::redirect(self::PAGE, 'error', $result->get_error_message()); }
        self::redirect(self::PAGE, 'ok', $postId > 0 ? 'Køretøjet er gemt.' : 'Køretøjet er oprettet.');
    }

    public static function deleteVehicle(): void
    {
        self::guard();
        check_admin_referer(self::DELETE_NONCE);
        $postId = absint($_POST['record_post_id'] ?? 0);
        $result = ModuleStore::delete($postId);
        if (is_wp_error($result) || !$result) { self::redirect(self::PAGE, 'error', is_wp_error($result) ? $result->get_error_message() : 'Køretøjet kunne ikke slettes.'); }
        self::redirect(self::PAGE, 'ok', 'Køretøjet er slettet.');
    }

    public static function saveFields(): void
    {
        self::guard();
        check_admin_referer(self::FIELD_SAVE_NONCE);
        $ids = isset($_POST['field_id']) && is_array($_POST['field_id']) ? wp_unslash($_POST['field_id']) : [];
        $labels = isset($_POST['field_label']) && is_array($_POST['field_label']) ? wp_unslash($_POST['field_label']) : [];
        $types = isset($_POST['field_type']) && is_array($_POST['field_type']) ? wp_unslash($_POST['field_type']) : [];
        $units = isset($_POST['field_unit']) && is_array($_POST['field_unit']) ? wp_unslash($_POST['field_unit']) : [];
        $orders = isset($_POST['field_order']) && is_array($_POST['field_order']) ? wp_unslash($_POST['field_order']) : [];
        $rows = [];
        foreach ($labels as $index => $label) {
            $rows[] = [
                'id' => (string) ($ids[$index] ?? ''),
                'label' => (string) $label,
                'type' => (string) ($types[$index] ?? 'text'),
                'unit' => (string) ($units[$index] ?? ''),
                'order' => (int) ($orders[$index] ?? (($index + 1) * 10)),
                'enabled' => true,
            ];
        }
        VehicleFieldRegistry::save($rows);
        self::redirect(self::FIELDS_PAGE, 'ok', 'Køretøjsfelterne er gemt. Eksisterende data bevarer deres stabile felt-IDer.');
    }

    /** @param array<int,int> $ids */
    private static function imagePreview(array $ids): string
    {
        $html = '';
        foreach (array_slice(array_values(array_unique(array_filter(array_map('absint', $ids)))), 0, 20) as $id) {
            $src = wp_get_attachment_image_url($id, 'thumbnail');
            if (is_string($src) && $src !== '') { $html .= '<img src="' . esc_url($src) . '" alt="">'; }
        }
        return $html !== '' ? $html : '<span class="description">Ingen billeder valgt</span>';
    }

    /** @return array<int,int> */
    private static function mediaIds(string $value): array
    {
        $out = [];
        foreach (preg_split('/[^0-9]+/', $value) ?: [] as $part) {
            $id = absint($part);
            if ($id > 0) { $out[$id] = $id; }
            if (count($out) >= 100) { break; }
        }
        return array_values($out);
    }

    private static function statusLabel(string $status): string
    {
        return ['publish' => 'Publiceret', 'archive' => 'Arkiveret', 'draft' => 'Kladde'][$status] ?? 'Kladde';
    }

    /** @param array<string,mixed> $args */
    private static function url(array $args = []): string
    {
        return add_query_arg($args, admin_url('admin.php?page=' . self::PAGE));
    }

    private static function fieldsUrl(): string
    {
        return admin_url('admin.php?page=' . self::FIELDS_PAGE);
    }

    private static function redirect(string $page, string $status, string $message): void
    {
        wp_safe_redirect(add_query_arg(['page' => $page, 'vd_status' => $status, 'vd_message' => $message], admin_url('admin.php')));
        exit;
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_pages')) { wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager')); }
    }

    private function __construct()
    {
    }
}
