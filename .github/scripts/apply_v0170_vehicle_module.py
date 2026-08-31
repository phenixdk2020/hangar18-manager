from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f'{rel}: expected one marker, found {count}: {old[:140]!r}')
    write(rel, value.replace(old, new, 1))


def regex_once(rel: str, pattern: str, repl: str) -> None:
    value = read(rel)
    next_value, count = re.subn(pattern, repl, value, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'{rel}: regex marker not unique: {pattern[:140]!r}')
    write(rel, next_value)


def append_once(rel: str, marker: str, block: str) -> None:
    value = read(rel)
    if marker in value:
        return
    if value and not value.endswith('\n'):
        value += '\n'
    write(rel, value + '\n' + block.strip() + '\n')


# ---------------------------------------------------------------------------
# New module classes
# ---------------------------------------------------------------------------
vehicle_fields_php = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Modules;

final class VehicleFieldRegistry
{
    public const OPTION = 'h18_vehicle_fields_v1';
    public const SCHEMA = 1;
    private const MAX_FIELDS = 80;

    /** @return array<int,array<string,mixed>> */
    public static function all(): array
    {
        $raw = get_option(self::OPTION, null);
        if (!is_array($raw)) {
            return self::defaults();
        }
        return self::normalize($raw);
    }

    /** @param array<int,mixed> $rows @return array<int,array<string,mixed>> */
    public static function normalize(array $rows): array
    {
        $out = [];
        $used = [];
        foreach (array_slice(array_values($rows), 0, self::MAX_FIELDS) as $index => $row) {
            if (!is_array($row)) { continue; }
            $label = sanitize_text_field((string) ($row['label'] ?? ''));
            if ($label === '') { continue; }
            $id = sanitize_key((string) ($row['id'] ?? ''));
            if ($id === '') { $id = sanitize_key($label); }
            if ($id === '') { $id = 'field_' . ($index + 1); }
            $base = substr($id, 0, 54);
            $candidate = $base;
            $suffix = 2;
            while (isset($used[$candidate])) {
                $candidate = substr($base, 0, 48) . '_' . $suffix;
                $suffix++;
            }
            $used[$candidate] = true;
            $type = strtolower((string) ($row['type'] ?? 'text'));
            if (!in_array($type, ['text', 'textarea', 'richtext', 'number', 'integer', 'boolean', 'date'], true)) {
                $type = 'text';
            }
            $out[] = [
                'id' => $candidate,
                'label' => $label,
                'type' => $type,
                'unit' => sanitize_text_field((string) ($row['unit'] ?? '')),
                'enabled' => array_key_exists('enabled', $row) ? (bool) $row['enabled'] : true,
                'order' => max(0, min(100000, (int) ($row['order'] ?? (($index + 1) * 10))),
            ];
        }
        usort($out, static function (array $a, array $b): int {
            $cmp = ((int) $a['order']) <=> ((int) $b['order']);
            return $cmp !== 0 ? $cmp : strnatcasecmp((string) $a['label'], (string) $b['label']);
        });
        return array_values($out);
    }

    /** @param array<int,mixed> $rows */
    public static function save(array $rows): bool
    {
        return update_option(self::OPTION, self::normalize($rows), false);
    }

    /** @return array<int,array<string,mixed>> */
    private static function defaults(): array
    {
        return self::normalize([
            ['id' => 'manufacturer', 'label' => 'Producent', 'type' => 'text', 'unit' => '', 'enabled' => true, 'order' => 10],
            ['id' => 'model', 'label' => 'Model', 'type' => 'text', 'unit' => '', 'enabled' => true, 'order' => 20],
            ['id' => 'year', 'label' => 'Årgang', 'type' => 'integer', 'unit' => '', 'enabled' => true, 'order' => 30],
            ['id' => 'engine', 'label' => 'Motor', 'type' => 'text', 'unit' => '', 'enabled' => true, 'order' => 40],
            ['id' => 'weight', 'label' => 'Vægt', 'type' => 'text', 'unit' => '', 'enabled' => true, 'order' => 50],
            ['id' => 'crew', 'label' => 'Besætning', 'type' => 'text', 'unit' => '', 'enabled' => true, 'order' => 60],
        ]);
    }

    private function __construct()
    {
    }
}
'''
write('clean/hangar18-manager/src/Modules/VehicleFieldRegistry.php', vehicle_fields_php)

vehicle_admin_php = r'''<?php

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
'''
write('clean/hangar18-manager/src/Admin/VehicleAdminController.php', vehicle_admin_php)

vehicle_admin_js = r'''(function () {
    'use strict';

    function ids(value) {
        return String(value || '').split(/[^0-9]+/).map(function (v) { return parseInt(v || '0', 10) || 0; }).filter(Boolean);
    }

    function preview(target, attachments) {
        var box = document.querySelector('[data-media-preview="' + target.id + '"]');
        if (!box) { return; }
        box.replaceChildren();
        if (!attachments.length) {
            var empty = document.createElement('span'); empty.className = 'description'; empty.textContent = 'Ingen billeder valgt'; box.appendChild(empty); return;
        }
        attachments.slice(0,20).forEach(function (attachment) {
            var data = attachment.toJSON ? attachment.toJSON() : attachment;
            var img = document.createElement('img');
            img.src = (data.sizes && data.sizes.thumbnail && data.sizes.thumbnail.url) || data.url || '';
            img.alt = '';
            if (img.src) { box.appendChild(img); }
        });
    }

    document.addEventListener('click', function (event) {
        var pick = event.target && event.target.closest ? event.target.closest('.h18-vd-media-pick') : null;
        if (pick) {
            event.preventDefault();
            var target = document.getElementById(String(pick.getAttribute('data-target') || ''));
            if (!target || !window.wp || !wp.media) { return; }
            var multiple = pick.getAttribute('data-multiple') === '1';
            var frame = wp.media({title: multiple ? 'Vælg galleribilleder' : 'Vælg primært billede',button:{text:'Brug billeder'},multiple:multiple,library:{type:'image'}});
            frame.on('select', function () {
                var selection = frame.state().get('selection');
                var items = selection.toArray();
                target.value = items.map(function (item) { return String(item.id || (item.get && item.get('id')) || ''); }).filter(Boolean).join(',');
                preview(target, items);
            });
            frame.open();
            return;
        }
        var clear = event.target && event.target.closest ? event.target.closest('.h18-vd-media-clear') : null;
        if (clear) {
            event.preventDefault();
            var clearTarget = document.getElementById(String(clear.getAttribute('data-target') || ''));
            if (clearTarget) { clearTarget.value = ''; preview(clearTarget, []); }
            return;
        }
        var add = event.target && event.target.closest ? event.target.closest('#h18-vd-add-vehicle-field') : null;
        if (add) {
            event.preventDefault();
            var host = document.getElementById('h18-vd-vehicle-field-rows'); if (!host) { return; }
            var row = document.createElement('div'); row.className = 'h18-vd-field-row'; row.setAttribute('data-vehicle-field-row','');
            row.innerHTML = '<input type="hidden" name="field_id[]" value=""><label>Navn<input required type="text" name="field_label[]" value=""></label><label>Type<select name="field_type[]"><option value="text">Tekst</option><option value="textarea">Flere linjer</option><option value="number">Tal</option><option value="integer">Heltal</option><option value="boolean">Ja/nej</option><option value="date">Dato</option></select></label><label>Enhed<input type="text" name="field_unit[]" value="" placeholder="fx kg"></label><label>Rækkefølge<input type="number" name="field_order[]" value="' + String((host.children.length + 1) * 10) + '"></label><label class="h18-clean-checkbox"><input type="checkbox" name="field_enabled[]" value="1" checked> Aktiv</label><button type="button" class="button-link-delete h18-vd-remove-vehicle-field">Fjern</button>';
            host.appendChild(row); row.querySelector('input[name="field_label[]"]').focus();
            return;
        }
        var remove = event.target && event.target.closest ? event.target.closest('.h18-vd-remove-vehicle-field') : null;
        if (remove) { event.preventDefault(); var fieldRow = remove.closest('[data-vehicle-field-row]'); if (fieldRow) { fieldRow.remove(); } }
    });
}());
'''
write('clean/hangar18-manager/assets/admin-v0170-vehicles.js', vehicle_admin_js)

vehicle_admin_css = r'''.h18-vd-vehicle-layout{display:grid;grid-template-columns:minmax(520px,1.2fr) minmax(380px,.8fr);gap:18px;align-items:start}.h18-vd-vehicle-editor label,.h18-vd-technical-fields label,.h18-vd-field-row label{display:block;font-weight:600}.h18-vd-vehicle-editor input[type=text],.h18-vd-vehicle-editor input[type=number],.h18-vd-vehicle-editor input[type=date],.h18-vd-vehicle-editor textarea,.h18-vd-vehicle-editor select,.h18-vd-technical-fields input,.h18-vd-technical-fields textarea,.h18-vd-field-row input,.h18-vd-field-row select{width:100%;max-width:none;margin-top:4px}.h18-vd-technical-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.h18-vd-media-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}.h18-vd-media-preview{min-height:92px;border:1px dashed #c3c4c7;background:#f6f7f7;padding:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}.h18-vd-media-preview img{width:88px;height:72px;object-fit:cover;border-radius:3px}.h18-vd-field-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px}.h18-vd-field-row{display:grid;grid-template-columns:2fr 1.2fr 1fr .8fr auto auto;gap:10px;align-items:end;padding:10px 0;border-bottom:1px solid #dcdcde}.h18-vd-field-row .h18-clean-checkbox{padding-bottom:6px}.h18-vd-vehicle-list form{display:inline}.h18-vd-vehicle-list .h18-manager-actions{white-space:nowrap}@media(max-width:1100px){.h18-vd-vehicle-layout{grid-template-columns:1fr}.h18-vd-field-row{grid-template-columns:1fr 1fr}.h18-vd-technical-fields,.h18-vd-media-grid{grid-template-columns:1fr}}
'''
write('clean/hangar18-manager/assets/admin-v0170-vehicles.css', vehicle_admin_css)

# ---------------------------------------------------------------------------
# Plugin bootstrap and editor localization
# ---------------------------------------------------------------------------
replace_once('clean/hangar18-manager/hangar18-manager.php', ' * Version: 0.1.69', ' * Version: 0.1.70')
replace_once('clean/hangar18-manager/hangar18-manager.php', "define('H18_CLEAN_VERSION', '0.1.69');", "define('H18_CLEAN_VERSION', '0.1.70');")
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Modules/ModuleStore.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Modules/ModuleStore.php';\nrequire_once H18_CLEAN_DIR . 'src/Modules/VehicleFieldRegistry.php';\n",
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Admin/AdminController.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Admin/AdminController.php';\nrequire_once H18_CLEAN_DIR . 'src/Admin/VehicleAdminController.php';\n",
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "    \\VisualDesignerManager\\Admin\\AdminController::register();\n",
    "    \\VisualDesignerManager\\Admin\\AdminController::register();\n    \\VisualDesignerManager\\Admin\\VehicleAdminController::register();\n",
)
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "    }, wp_get_nav_menus()));\n\n    wp_enqueue_script(\n",
    r'''    }, wp_get_nav_menus()));

    $vehicleRecords = array_values(array_map(static function (array $item): array {
        $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
        $featuredId = absint($record['featuredMediaId'] ?? 0);
        $featuredUrl = $featuredId > 0 ? wp_get_attachment_image_url($featuredId, 'large') : false;
        return [
            'postId' => (int) ($item['postId'] ?? 0),
            'id' => (string) ($record['id'] ?? ''),
            'title' => (string) ($record['title'] ?? ''),
            'status' => (string) ($record['status'] ?? 'draft'),
            'sortOrder' => (int) ($record['sortOrder'] ?? 0),
            'summary' => (string) ($record['summary'] ?? ''),
            'featuredMediaId' => $featuredId,
            'featuredUrl' => is_string($featuredUrl) ? $featuredUrl : '',
            'fields' => isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [],
            'attributes' => isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [],
        ];
    }, \VisualDesignerManager\Modules\ModuleStore::listRecords('vehicles', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC'])));

    wp_enqueue_script(
''')
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "        'moduleCatalog' => \\VisualDesignerManager\\Modules\\ModuleRegistry::editorCatalog(),\n",
    "        'moduleCatalog' => \\VisualDesignerManager\\Modules\\ModuleRegistry::editorCatalog(),\n        'vehicleRecords' => $vehicleRecords,\n        'vehicleAdminUrl' => admin_url('admin.php?page=h18-clean-vehicles'),\n",
)

# ---------------------------------------------------------------------------
# Admin routing and status
# ---------------------------------------------------------------------------
replace_once(
    'clean/hangar18-manager/src/Admin/AdminController.php',
    "        add_submenu_page(self::MENU, 'Køretøjer', 'Køretøjer', $cap, 'h18-clean-vehicles', [self::class, 'vehicles']);\n        add_submenu_page(self::MENU, 'Køretøjsfelter', 'Køretøjsfelter', $cap, 'h18-clean-vehicle-fields', [self::class, 'vehicleFields']);\n",
    "        add_submenu_page(self::MENU, 'Køretøjer', 'Køretøjer', $cap, 'h18-clean-vehicles', [VehicleAdminController::class, 'render']);\n        add_submenu_page(self::MENU, 'Køretøjsfelter', 'Køretøjsfelter', $cap, 'h18-clean-vehicle-fields', [VehicleAdminController::class, 'renderFields']);\n",
)
replace_once('clean/hangar18-manager/assets/admin-v0123.js', "        'h18-clean-vehicles': ['Ikke færdig', 'planned'],\n        'h18-clean-vehicle-fields': ['Ikke færdig', 'planned'],", "        'h18-clean-vehicles': ['Klar', 'ready'],\n        'h18-clean-vehicle-fields': ['Klar', 'ready'],")

# ---------------------------------------------------------------------------
# Vehicle module schema and store lookup
# ---------------------------------------------------------------------------
replace_once(
    'clean/hangar18-manager/src/Modules/ModuleRegistry.php',
    "                    'category' => ['label' => 'Kategori', 'type' => 'text', 'required' => false],\n",
    "                    'category' => ['label' => 'Kategori', 'type' => 'text', 'required' => false],\n                    'imageIds' => ['label' => 'Galleri', 'type' => 'media_list', 'required' => false],\n",
)
replace_once(
    'clean/hangar18-manager/src/Modules/ModuleStore.php',
    "    public const META_RECORD = '_h18_module_record_v1';\n",
    "    public const META_RECORD = '_h18_module_record_v1';\n    public const META_RECORD_ID = '_h18_module_record_id';\n",
)
replace_once(
    'clean/hangar18-manager/src/Modules/ModuleStore.php',
    "        update_post_meta($postId, self::META_RECORD, $json);\n",
    "        update_post_meta($postId, self::META_RECORD, $json);\n        update_post_meta($postId, self::META_RECORD_ID, (string) ($record['id'] ?? ''));\n",
)
replace_once(
    'clean/hangar18-manager/src/Modules/ModuleStore.php',
    "    /** @return bool|\\WP_Error */\n    public static function delete(int $postId)\n",
    r'''    /** @return array{postId:int,record:array<string,mixed>}|null */
    public static function findByRecordId(string $module, string $recordId): ?array
    {
        $module = ModuleRegistry::key($module);
        $recordId = strtolower(trim($recordId));
        if (!ModuleRegistry::supports($module) || !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) {
            return null;
        }
        $ids = get_posts([
            'post_type' => self::POST_TYPE,
            'post_status' => 'publish',
            'fields' => 'ids',
            'posts_per_page' => 1,
            'no_found_rows' => true,
            'suppress_filters' => true,
            'meta_query' => [
                ['key' => self::META_MODULE, 'value' => $module, 'compare' => '='],
                ['key' => self::META_RECORD_ID, 'value' => $recordId, 'compare' => '='],
            ],
        ]);
        if (is_array($ids) && !empty($ids)) {
            $postId = (int) $ids[0];
            $record = self::get($postId);
            return $record !== null ? ['postId' => $postId, 'record' => $record] : null;
        }
        // Compatibility fallback for any records written by the v0.1.67 foundation
        // before META_RECORD_ID existed.
        foreach (self::listRecords($module, ['status' => 'all', 'limit' => 100]) as $item) {
            if ((string) ($item['record']['id'] ?? '') === $recordId) { return $item; }
        }
        return null;
    }

    /** @return bool|\WP_Error */
    public static function delete(int $postId)
''')

# ---------------------------------------------------------------------------
# Canonical Designer element model
# ---------------------------------------------------------------------------
replace_once('clean/hangar18-manager/src/Model/LayoutModel.php', "use VisualDesignerManager\\Icons\\IconRegistry;\n", "use VisualDesignerManager\\Icons\\IconRegistry;\nuse VisualDesignerManager\\Modules\\ModuleBinding;\n")
replace_once(
    'clean/hangar18-manager/src/Model/LayoutModel.php',
    "['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table']",
    "['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail']",
)
layout_vehicle_props = r'''        if ($type === 'vehiclelist') {
            $orderBy = in_array((string) ($raw['orderBy'] ?? 'sortOrder'), ['sortOrder', 'title', 'updatedAt'], true) ? (string) ($raw['orderBy'] ?? 'sortOrder') : 'sortOrder';
            $order = strtoupper((string) ($raw['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
            $limit = self::clamp($raw['limit'] ?? 50, 1, 100, 50);
            $binding = ModuleBinding::normalize([
                'mode' => 'module', 'module' => 'vehicles', 'view' => 'list',
                'query' => ['status' => 'publish', 'orderBy' => $orderBy, 'order' => $order, 'limit' => $limit],
            ]);
            return array_merge([
                'binding' => $binding,
                'limit' => $limit,
                'orderBy' => $orderBy,
                'order' => $order,
                'detailPageId' => absint($raw['detailPageId'] ?? 0),
                'columns' => self::clamp($raw['columns'] ?? 3, 1, 4, 3),
                'cardGap' => self::clamp($raw['cardGap'] ?? 18, 0, 80, 18),
                'cardPadding' => self::clamp($raw['cardPadding'] ?? 12, 0, 60, 12),
                'imageHeight' => self::clamp($raw['imageHeight'] ?? 180, 60, 600, 180),
                'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true,
                'showCategory' => array_key_exists('showCategory', $raw) ? (bool) $raw['showCategory'] : true,
                'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true,
                'linkCards' => array_key_exists('linkCards', $raw) ? (bool) $raw['linkCards'] : true,
                'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#ffffff')) ?: '#ffffff',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'cardRadius' => self::clamp($raw['cardRadius'] ?? 4, 0, 60, 4),
            ], $border);
        }
        if ($type === 'vehicledetail') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'vehicles', 'view' => 'detail', 'recordId' => $recordId]);
            return array_merge([
                'binding' => $binding,
                'recordId' => $recordId,
                'showGallery' => array_key_exists('showGallery', $raw) ? (bool) $raw['showGallery'] : true,
                'showCategory' => array_key_exists('showCategory', $raw) ? (bool) $raw['showCategory'] : true,
                'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true,
                'showDescription' => array_key_exists('showDescription', $raw) ? (bool) $raw['showDescription'] : true,
                'showAttributes' => array_key_exists('showAttributes', $raw) ? (bool) $raw['showAttributes'] : true,
                'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 900, 360),
                'labelWidth' => self::clamp($raw['labelWidth'] ?? 34, 20, 60, 34),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'padding' => self::clamp($raw['padding'] ?? 16, 0, 80, 16),
                'radius' => self::clamp($raw['radius'] ?? 4, 0, 60, 4),
            ], $border);
        }
'''
replace_once('clean/hangar18-manager/src/Model/LayoutModel.php', "        if ($type === 'image') {\n", layout_vehicle_props + "        if ($type === 'image') {\n")

# ---------------------------------------------------------------------------
# Page Designer palette and editor runtime
# ---------------------------------------------------------------------------
replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    "            'table' => 'Tabel',\n",
    "            'table' => 'Tabel',\n            'vehiclelist' => 'Køretøjsliste',\n            'vehicledetail' => 'Køretøjsdetalje',\n",
)
js_path = 'clean/hangar18-manager/assets/editor-v018-core.js'
replace_once(js_path,
    "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table'];",
    "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail'];")
replace_once(js_path,
    "datalist:'Data List',table:'Tabel'})",
    "datalist:'Data List',table:'Tabel',vehiclelist:'Køretøjsliste',vehicledetail:'Køretøjsdetalje'})")
# This uppercase map occurs twice: canvas card heading and Inspector heading.
value = read(js_path)
value = value.replace("datalist:'DATA LIST',table:'TABEL'}[", "datalist:'DATA LIST',table:'TABEL',vehiclelist:'KØRETØJSLISTE',vehicledetail:'KØRETØJSDETALJE'}[")
write(js_path, value)
replace_once(js_path,
    "    function iconLibrarySets() {\n",
    r'''    function vehicleRecords() {
        return Array.isArray(CFG.vehicleRecords) ? CFG.vehicleRecords.filter(function (record) { return record && record.id; }) : [];
    }
    function vehicleRecordById(recordId) {
        recordId = String(recordId || '');
        return vehicleRecords().find(function (record) { return String(record.id || '') === recordId; }) || null;
    }
    function vehicleCategory(record) {
        return record && record.fields && typeof record.fields === 'object' ? String(record.fields.category || '') : '';
    }

    function iconLibrarySets() {
''')
js_vehicle_props = r'''        if (type === 'vehiclelist') {
            const orderBy = ['sortOrder','title','updatedAt'].includes(String(raw.orderBy || 'sortOrder')) ? String(raw.orderBy || 'sortOrder') : 'sortOrder';
            const order = String(raw.order || 'ASC').toUpperCase() === 'DESC' ? 'DESC' : 'ASC';
            const limit = clamp(parseInt(raw.limit || 50,10) || 50,1,100);
            return Object.assign(common, {
                binding:{schema:1,mode:'module',module:'vehicles',view:'list',recordId:'',query:{status:'publish',orderBy:orderBy,order:order,limit:limit},fieldMap:{}},
                limit:limit, orderBy:orderBy, order:order,
                detailPageId:parseInt(raw.detailPageId || 0,10) || 0,
                columns:clamp(parseInt(raw.columns || 3,10) || 3,1,4),
                cardGap:clamp(parseInt(raw.cardGap || 18,10) || 18,0,80),
                cardPadding:clamp(parseInt(raw.cardPadding || 12,10) || 12,0,60),
                imageHeight:clamp(parseInt(raw.imageHeight || 180,10) || 180,60,600),
                showImage:raw.showImage !== false, showCategory:raw.showCategory !== false, showSummary:raw.showSummary !== false, linkCards:raw.linkCards !== false,
                cardBackground:/^#[0-9a-f]{6}$/i.test(String(raw.cardBackground || '')) ? String(raw.cardBackground).toLowerCase() : '#ffffff',
                textColor:/^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#30382a',
                accentColor:/^#[0-9a-f]{6}$/i.test(String(raw.accentColor || '')) ? String(raw.accentColor).toLowerCase() : '#c3ae83',
                cardRadius:clamp(parseInt(raw.cardRadius || 4,10) || 4,0,60)
            });
        }
        if (type === 'vehicledetail') {
            let recordId = String(raw.recordId || '').toLowerCase().trim();
            if (recordId && !/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(recordId)) { recordId = ''; }
            return Object.assign(common, {
                binding:{schema:1,mode:'module',module:'vehicles',view:'detail',recordId:recordId,query:{status:'publish',orderBy:'sortOrder',order:'ASC',limit:50},fieldMap:{}},
                recordId:recordId,
                showGallery:raw.showGallery !== false, showCategory:raw.showCategory !== false, showSummary:raw.showSummary !== false, showDescription:raw.showDescription !== false, showAttributes:raw.showAttributes !== false,
                imageHeight:clamp(parseInt(raw.imageHeight || 360,10) || 360,80,900), labelWidth:clamp(parseInt(raw.labelWidth || 34,10) || 34,20,60),
                background:/^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',
                textColor:/^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#30382a',
                accentColor:/^#[0-9a-f]{6}$/i.test(String(raw.accentColor || '')) ? String(raw.accentColor).toLowerCase() : '#c3ae83',
                padding:clamp(parseInt(raw.padding || 16,10) || 16,0,80), radius:clamp(parseInt(raw.radius || 4,10) || 4,0,60)
            });
        }
'''
# unique normalizeProps image marker follows table normalization.
replace_once(js_path, "        if (type === 'image') {\n            const fit = ['cover', 'contain', 'original', 'stretch', 'manual']", js_vehicle_props + "        if (type === 'image') {\n            const fit = ['cover', 'contain', 'original', 'stretch', 'manual']")
replace_once(js_path,
    "const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8, menu: 10, spacer: 4, divider: 6, icon: 10, badge: 8, link: 8, datalist: 18, table: 22 };",
    "const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8, menu: 10, spacer: 4, divider: 6, icon: 10, badge: 8, link: 8, datalist: 18, table: 22, vehiclelist: 42, vehicledetail: 54 };")

card_vehicle = r'''        } else if (node.type === 'vehiclelist') {
            wrap.classList.add('h18-clean-node-preview--vehiclelist');
            const records = vehicleRecords().filter(function (record) { return String(record.status || '') === 'publish'; }).slice(0, node.props.limit || 50);
            const grid = document.createElement('div'); grid.className = 'h18-vd-vehicle-list-preview'; grid.style.gridTemplateColumns = 'repeat(' + String(node.props.columns || 3) + ',minmax(0,1fr))'; grid.style.gap = String(node.props.cardGap || 18) + 'px';
            if (!records.length) { grid.textContent = 'Ingen publicerede køretøjer endnu · opret dem under Manager → Køretøjer'; }
            records.forEach(function (record) {
                const card = document.createElement('article'); card.className = 'h18-vd-vehicle-card-preview'; card.style.background = node.props.cardBackground || '#ffffff'; card.style.color = node.props.textColor || '#30382a'; card.style.padding = String(node.props.cardPadding || 12) + 'px'; card.style.borderRadius = String(node.props.cardRadius || 4) + 'px';
                if (node.props.showImage && record.featuredUrl) { const img = document.createElement('img'); img.src = String(record.featuredUrl); img.alt = ''; img.style.height = String(node.props.imageHeight || 180) + 'px'; card.appendChild(img); }
                const title = document.createElement('strong'); title.textContent = String(record.title || 'Køretøj'); card.appendChild(title);
                const category = vehicleCategory(record); if (node.props.showCategory && category) { const meta = document.createElement('small'); meta.textContent = category; meta.style.color = node.props.accentColor || '#c3ae83'; card.appendChild(meta); }
                if (node.props.showSummary && record.summary) { const summary = document.createElement('p'); summary.textContent = String(record.summary); card.appendChild(summary); }
                grid.appendChild(card);
            }); wrap.appendChild(grid);
        } else if (node.type === 'vehicledetail') {
            wrap.classList.add('h18-clean-node-preview--vehicledetail');
            const record = vehicleRecordById(node.props.recordId) || vehicleRecords().find(function (item) { return String(item.status || '') === 'publish'; }) || null;
            if (!record) { wrap.textContent = 'Ingen køretøjer at vise · opret data under Manager → Køretøjer'; }
            else {
                const detail = document.createElement('div'); detail.className = 'h18-vd-vehicle-detail-preview'; detail.style.background = node.props.background || '#ffffff'; detail.style.color = node.props.textColor || '#30382a'; detail.style.padding = String(node.props.padding || 16) + 'px'; detail.style.borderRadius = String(node.props.radius || 4) + 'px';
                if (record.featuredUrl) { const img = document.createElement('img'); img.src = String(record.featuredUrl); img.alt = ''; img.style.height = String(node.props.imageHeight || 360) + 'px'; detail.appendChild(img); }
                const title = document.createElement('h3'); title.textContent = String(record.title || 'Køretøj'); detail.appendChild(title);
                const category = vehicleCategory(record); if (node.props.showCategory && category) { const meta = document.createElement('strong'); meta.textContent = category; meta.style.color = node.props.accentColor || '#c3ae83'; detail.appendChild(meta); }
                if (node.props.showSummary && record.summary) { const summary = document.createElement('p'); summary.textContent = String(record.summary); detail.appendChild(summary); }
                if (node.props.showAttributes && Array.isArray(record.attributes)) { const dl = document.createElement('dl'); record.attributes.filter(function (a) { return a && a.enabled !== false && String(a.value == null ? '' : a.value) !== ''; }).slice(0,12).forEach(function (a) { const dt=document.createElement('dt');dt.textContent=String(a.label||a.key||'Felt');const dd=document.createElement('dd');dd.textContent=String(a.value);dl.appendChild(dt);dl.appendChild(dd); }); detail.appendChild(dl); }
                wrap.appendChild(detail);
            }
'''
replace_once(js_path, "        } else if (node.type === 'image') {\n            wrap.classList.add('h18-clean-node-preview--image');", card_vehicle + "        } else if (node.type === 'image') {\n            wrap.classList.add('h18-clean-node-preview--image');")

# Inspector: insert vehicle branches immediately before image controls using the unique image-pick marker.
inspector_vehicle = r'''        } else if (node.type === 'vehiclelist') {
            html += '<div class="h18-vd-menu-group"><h3>Køretøjsliste</h3><p class="description">Data kommer fra Manager → Køretøjer. Listen viser kun publicerede records.</p>';
            html += '<label>Detaljeside<select data-field="vehicleDetailPageId"><option value="0">Ingen link / vælg senere</option>' + (Array.isArray(CFG.pages) ? CFG.pages.map(function (page) { const id=parseInt(page.id||0,10)||0; return '<option value="'+id+'"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>'; }).join('') : '') + '</select></label>';
            html += '<div class="h18-clean-field-grid"><label>Kolonner<input data-field="vehicleColumns" type="number" min="1" max="4" value="'+(node.props.columns||3)+'"></label><label>Max. records<input data-field="vehicleLimit" type="number" min="1" max="100" value="'+(node.props.limit||50)+'"></label><label>Sortér efter<select data-field="vehicleOrderBy"><option value="sortOrder"'+(node.props.orderBy==='sortOrder'?' selected':'')+'>Sortering</option><option value="title"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value="updatedAt"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field="vehicleOrder"><option value="ASC"'+(node.props.order!=='DESC'?' selected':'')+'>Stigende</option><option value="DESC"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Kortafstand px<input data-field="vehicleCardGap" type="number" min="0" max="80" value="'+(node.props.cardGap||18)+'"></label><label>Kortpadding px<input data-field="vehicleCardPadding" type="number" min="0" max="60" value="'+(node.props.cardPadding||12)+'"></label><label>Billedhøjde px<input data-field="vehicleImageHeight" type="number" min="60" max="600" value="'+(node.props.imageHeight||180)+'"></label><label>Hjørner px<input data-field="vehicleCardRadius" type="number" min="0" max="60" value="'+(node.props.cardRadius||4)+'"></label></div>';
            html += '<label class="h18-clean-checkbox"><input data-field="vehicleShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class="h18-clean-checkbox"><input data-field="vehicleShowCategory" type="checkbox"'+(node.props.showCategory!==false?' checked':'')+'> Vis kategori</label><label class="h18-clean-checkbox"><input data-field="vehicleShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="vehicleLinkCards" type="checkbox"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside med ?h18_vehicle=record-id</label>';
            html += '<div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="vehicleCardBackground" type="color" value="'+escapeAttr(node.props.cardBackground||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="vehicleAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>';
            if (CFG.vehicleAdminUrl) { html += '<p><a class="button" href="'+escapeAttr(String(CFG.vehicleAdminUrl))+'">Administrér køretøjer</a></p>'; }
        } else if (node.type === 'vehicledetail') {
            html += '<div class="h18-vd-menu-group"><h3>Køretøjsdetalje</h3><label>Køretøj<select data-field="vehicleRecordId"><option value="">Fra URL · ?h18_vehicle=record-id</option>'+vehicleRecords().map(function (record) { return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Køretøj'))+' · '+escapeHtml(String(record.status||''))+'</option>'; }).join('')+'</select></label><p class="description">Lad feltet stå på “Fra URL”, når samme detaljeside skal bruges af alle kort i en Køretøjsliste.</p>';
            html += '<label class="h18-clean-checkbox"><input data-field="vehicleShowGallery" type="checkbox"'+(node.props.showGallery!==false?' checked':'')+'> Vis galleri</label><label class="h18-clean-checkbox"><input data-field="vehicleShowCategory" type="checkbox"'+(node.props.showCategory!==false?' checked':'')+'> Vis kategori</label><label class="h18-clean-checkbox"><input data-field="vehicleShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="vehicleShowDescription" type="checkbox"'+(node.props.showDescription!==false?' checked':'')+'> Vis beskrivelse</label><label class="h18-clean-checkbox"><input data-field="vehicleShowAttributes" type="checkbox"'+(node.props.showAttributes!==false?' checked':'')+'> Vis tekniske data</label>';
            html += '<div class="h18-clean-field-grid"><label>Billedhøjde px<input data-field="vehicleImageHeight" type="number" min="80" max="900" value="'+(node.props.imageHeight||360)+'"></label><label>Labelbredde %<input data-field="vehicleLabelWidth" type="number" min="20" max="60" value="'+(node.props.labelWidth||34)+'"></label><label>Padding px<input data-field="padding" type="number" min="0" max="80" value="'+(node.props.padding||16)+'"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="60" value="'+(node.props.radius||4)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="vehicleAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>';
            if (CFG.vehicleAdminUrl) { html += '<p><a class="button" href="'+escapeAttr(String(CFG.vehicleAdminUrl))+'">Administrér køretøjer</a></p>'; }
'''
# Find the inspector image branch specifically: it contains the media pick button in its first statement.
regex_once(js_path, r"(\n        \} else if \(node\.type === 'image'\) \{\n            html \+= '<button type=\\\"button\\\" class=\\\"button\\\" id=\\\"h18-clean-pick-image\\\")", "\n" + inspector_vehicle + r"        } else if (node.type === 'image') {
            html += '<button type=\"button\" class=\"button\" id=\"h18-clean-pick-image\"")

# Inspector field handlers.
handler_marker = "                else if (field === 'buttonText') { current.props.text = String(control.value || 'Knap'); }\n"
vehicle_handlers = r'''                else if (field === 'vehicleDetailPageId') { current.props.detailPageId = parseInt(control.value || 0,10) || 0; }
                else if (field === 'vehicleColumns') { current.props.columns = clamp(parseInt(control.value || 3,10) || 3,1,4); }
                else if (field === 'vehicleLimit') { current.props.limit = clamp(parseInt(control.value || 50,10) || 50,1,100); if (current.props.binding && current.props.binding.query) { current.props.binding.query.limit = current.props.limit; } }
                else if (field === 'vehicleOrderBy') { current.props.orderBy = ['sortOrder','title','updatedAt'].includes(control.value) ? control.value : 'sortOrder'; if (current.props.binding && current.props.binding.query) { current.props.binding.query.orderBy = current.props.orderBy; } }
                else if (field === 'vehicleOrder') { current.props.order = control.value === 'DESC' ? 'DESC' : 'ASC'; if (current.props.binding && current.props.binding.query) { current.props.binding.query.order = current.props.order; } }
                else if (field === 'vehicleCardGap') { current.props.cardGap = clamp(parseInt(control.value || 18,10) || 18,0,80); }
                else if (field === 'vehicleCardPadding') { current.props.cardPadding = clamp(parseInt(control.value || 12,10) || 12,0,60); }
                else if (field === 'vehicleImageHeight') { current.props.imageHeight = clamp(parseInt(control.value || 180,10) || 180,current.type === 'vehicledetail' ? 80 : 60,current.type === 'vehicledetail' ? 900 : 600); }
                else if (field === 'vehicleCardRadius') { current.props.cardRadius = clamp(parseInt(control.value || 4,10) || 4,0,60); }
                else if (field === 'vehicleShowImage') { current.props.showImage = !!control.checked; }
                else if (field === 'vehicleShowCategory') { current.props.showCategory = !!control.checked; }
                else if (field === 'vehicleShowSummary') { current.props.showSummary = !!control.checked; }
                else if (field === 'vehicleLinkCards') { current.props.linkCards = !!control.checked; }
                else if (field === 'vehicleCardBackground') { current.props.cardBackground = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'vehicleAccentColor') { current.props.accentColor = normalizeColor(control.value || '#c3ae83'); }
                else if (field === 'vehicleRecordId') { current.props.recordId = String(control.value || ''); if (current.props.binding) { current.props.binding.recordId = current.props.recordId; } }
                else if (field === 'vehicleShowGallery') { current.props.showGallery = !!control.checked; }
                else if (field === 'vehicleShowDescription') { current.props.showDescription = !!control.checked; }
                else if (field === 'vehicleShowAttributes') { current.props.showAttributes = !!control.checked; }
                else if (field === 'vehicleLabelWidth') { current.props.labelWidth = clamp(parseInt(control.value || 34,10) || 34,20,60); }
'''
replace_once(js_path, handler_marker, vehicle_handlers + handler_marker)

# Editor visuals for module previews.
append_once('clean/hangar18-manager/assets/editor-v0166-foundation.css', 'h18-vd-vehicle-list-preview', r'''
.h18-vd-vehicle-list-preview{display:grid;width:100%;box-sizing:border-box}.h18-vd-vehicle-card-preview{display:flex;flex-direction:column;gap:6px;min-width:0;border:1px solid #dcdcde;box-sizing:border-box;overflow:hidden}.h18-vd-vehicle-card-preview img,.h18-vd-vehicle-detail-preview>img{display:block;width:100%;object-fit:cover;max-width:none}.h18-vd-vehicle-card-preview p,.h18-vd-vehicle-detail-preview p,.h18-vd-vehicle-detail-preview h3{margin:0}.h18-vd-vehicle-detail-preview{display:flex;flex-direction:column;gap:10px;width:100%;box-sizing:border-box}.h18-vd-vehicle-detail-preview dl{display:grid;grid-template-columns:minmax(100px,34%) minmax(0,1fr);margin:0}.h18-vd-vehicle-detail-preview dt,.h18-vd-vehicle-detail-preview dd{margin:0;padding:5px 8px;border-bottom:1px solid #dcdcde}.h18-clean-node-preview--vehiclelist,.h18-clean-node-preview--vehicledetail{overflow:auto}
''')

# ---------------------------------------------------------------------------
# Frontend dynamic rendering
# ---------------------------------------------------------------------------
replace_once('clean/hangar18-manager/src/Frontend/Renderer.php', "use VisualDesignerManager\\Model\\TemplateLayoutModel;\n", "use VisualDesignerManager\\Model\\TemplateLayoutModel;\nuse VisualDesignerManager\\Modules\\ModuleStore;\n")
replace_once(
    'clean/hangar18-manager/src/Frontend/Renderer.php',
    "        echo '.h18-vd-live-shell,.h18-vd-live-shell-part{display:block;width:100%;max-width:none;margin:0;padding:0;box-sizing:border-box}.h18-vd-live-shell{position:relative}';\n",
    "        echo '.h18-clean-front-vehicle-list{display:grid;width:100%;box-sizing:border-box}.h18-clean-front-vehicle-card{display:flex;flex-direction:column;gap:8px;min-width:0;box-sizing:border-box;text-decoration:none;color:inherit;overflow:hidden}.h18-clean-front-vehicle-card img{display:block;width:100%;max-width:none;object-fit:cover}.h18-clean-front-vehicle-card h3,.h18-clean-front-vehicle-card p{margin:0}.h18-clean-front-vehicle-detail{box-sizing:border-box}.h18-clean-front-vehicle-hero{display:block;width:100%;max-width:none;object-fit:cover}.h18-clean-front-vehicle-gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}.h18-clean-front-vehicle-gallery img{display:block;width:100%;height:140px;object-fit:cover}.h18-clean-front-vehicle-specs{display:grid;margin:16px 0 0}.h18-clean-front-vehicle-specs dt,.h18-clean-front-vehicle-specs dd{margin:0;padding:7px 10px;border-bottom:1px solid #dcdcde}.h18-clean-front-vehicle-description{margin-top:16px}@media(max-width:782px){.h18-clean-front-vehicle-list{grid-template-columns:1fr!important}.h18-clean-front-vehicle-specs{grid-template-columns:1fr!important}.h18-clean-front-vehicle-specs dt{font-weight:700}.h18-clean-front-vehicle-specs dd{padding-top:0}}';\n        echo '.h18-vd-live-shell,.h18-vd-live-shell-part{display:block;width:100%;max-width:none;margin:0;padding:0;box-sizing:border-box}.h18-vd-live-shell{position:relative}';\n",
)
renderer_vehicle = r'''        if ($type === 'vehiclelist') {
            $binding = isset($props['binding']) && is_array($props['binding']) ? $props['binding'] : [];
            $query = isset($binding['query']) && is_array($binding['query']) ? $binding['query'] : [];
            $query['status'] = 'publish';
            $query['limit'] = max(1, min(100, (int) ($props['limit'] ?? ($query['limit'] ?? 50))));
            $query['orderBy'] = in_array((string) ($props['orderBy'] ?? ($query['orderBy'] ?? 'sortOrder')), ['sortOrder', 'title', 'updatedAt'], true) ? (string) ($props['orderBy'] ?? ($query['orderBy'] ?? 'sortOrder')) : 'sortOrder';
            $query['order'] = strtoupper((string) ($props['order'] ?? ($query['order'] ?? 'ASC'))) === 'DESC' ? 'DESC' : 'ASC';
            $records = ModuleStore::listRecords('vehicles', $query);
            $columns = max(1, min(4, (int) ($props['columns'] ?? 3)));
            $gap = max(0, min(80, (int) ($props['cardGap'] ?? 18)));
            $padding = max(0, min(60, (int) ($props['cardPadding'] ?? 12)));
            $imageHeight = max(60, min(600, (int) ($props['imageHeight'] ?? 180)));
            $cardBg = sanitize_hex_color((string) ($props['cardBackground'] ?? '#ffffff')) ?: '#ffffff';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
            $accent = sanitize_hex_color((string) ($props['accentColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $cardRadius = max(0, min(60, (int) ($props['cardRadius'] ?? 4)));
            $detailPageId = absint($props['detailPageId'] ?? 0);
            $detailBase = $detailPageId > 0 ? get_permalink($detailPageId) : false;
            $cards = '';
            foreach ($records as $item) {
                $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
                if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
                $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
                $recordId = (string) ($record['id'] ?? '');
                $href = is_string($detailBase) && $detailBase !== '' && !empty($props['linkCards']) ? add_query_arg('h18_vehicle', rawurlencode($recordId), $detailBase) : '';
                $tag = $href !== '' ? 'a' : 'article';
                $hrefAttr = $href !== '' ? ' href="' . esc_url($href) . '"' : '';
                $image = '';
                $featuredId = absint($record['featuredMediaId'] ?? 0);
                if (!empty($props['showImage']) && $featuredId > 0) {
                    $url = wp_get_attachment_image_url($featuredId, 'large');
                    if (is_string($url) && $url !== '') { $image = '<img src="' . esc_url($url) . '" alt="' . esc_attr((string) ($record['title'] ?? '')) . '" style="height:' . esc_attr((string) $imageHeight) . 'px">'; }
                }
                $category = !empty($props['showCategory']) && trim((string) ($fields['category'] ?? '')) !== '' ? '<small style="color:' . esc_attr($accent) . '">' . esc_html((string) $fields['category']) . '</small>' : '';
                $summary = !empty($props['showSummary']) && trim((string) ($record['summary'] ?? '')) !== '' ? '<p>' . esc_html((string) $record['summary']) . '</p>' : '';
                $cardStyle = 'background:' . $cardBg . ';color:' . $textColor . ';padding:' . $padding . 'px;border-radius:' . $cardRadius . 'px;';
                $cards .= '<' . $tag . ' class="h18-clean-front-vehicle-card"' . $hrefAttr . ' style="' . esc_attr($cardStyle) . '">' . $image . '<h3>' . esc_html((string) ($record['title'] ?? 'Køretøj')) . '</h3>' . $category . $summary . '</' . $tag . '>';
            }
            if ($cards === '' && self::$forceStandaloneCss) { $cards = '<p>Ingen publicerede køretøjer endnu.</p>'; }
            $listStyle = $style . $borderStyle . $spacingStyle . 'grid-template-columns:repeat(' . $columns . ',minmax(0,1fr));gap:' . $gap . 'px;';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-vehicle-list" style="' . esc_attr($listStyle) . '">' . $cards . '</div>';
        }

        if ($type === 'vehicledetail') {
            $recordId = strtolower(trim((string) ($props['recordId'] ?? '')));
            if ($recordId === '') { $recordId = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET['h18_vehicle'] ?? '')))); }
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            if ($recordId === '') {
                $message = self::$forceStandaloneCss ? 'Vælg et køretøj i Inspector eller brug ?h18_vehicle=record-id.' : 'Vælg et køretøj fra oversigten.';
                return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-vehicle-detail" style="' . esc_attr($style . $borderStyle . $spacingStyle) . '"><p>' . esc_html($message) . '</p></div>';
            }
            $found = ModuleStore::findByRecordId('vehicles', $recordId);
            $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
            $allowDraft = self::$forceStandaloneCss && current_user_can('edit_pages');
            if ($record === null || ((string) ($record['status'] ?? 'draft') !== 'publish' && !$allowDraft)) {
                return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-vehicle-detail" style="' . esc_attr($style . $borderStyle . $spacingStyle) . '"><p>Køretøjet findes ikke eller er ikke publiceret.</p></div>';
            }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $background = sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
            $accent = sanitize_hex_color((string) ($props['accentColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $padding = max(0, min(80, (int) ($props['padding'] ?? 16)));
            $imageHeight = max(80, min(900, (int) ($props['imageHeight'] ?? 360)));
            $labelWidth = max(20, min(60, (int) ($props['labelWidth'] ?? 34)));
            $featuredId = absint($record['featuredMediaId'] ?? 0);
            $hero = '';
            if ($featuredId > 0) { $url = wp_get_attachment_image_url($featuredId, 'large'); if (is_string($url) && $url !== '') { $hero = '<img class="h18-clean-front-vehicle-hero" src="' . esc_url($url) . '" alt="' . esc_attr((string) ($record['title'] ?? '')) . '" style="height:' . esc_attr((string) $imageHeight) . 'px">'; } }
            $category = !empty($props['showCategory']) && trim((string) ($fields['category'] ?? '')) !== '' ? '<p><strong style="color:' . esc_attr($accent) . '">' . esc_html((string) $fields['category']) . '</strong></p>' : '';
            $summary = !empty($props['showSummary']) && trim((string) ($record['summary'] ?? '')) !== '' ? '<p>' . esc_html((string) $record['summary']) . '</p>' : '';
            $description = !empty($props['showDescription']) && trim((string) ($fields['description'] ?? '')) !== '' ? '<div class="h18-clean-front-vehicle-description">' . wp_kses_post((string) $fields['description']) . '</div>' : '';
            $specs = '';
            if (!empty($props['showAttributes'])) {
                foreach ((array) ($record['attributes'] ?? []) as $attribute) {
                    if (!is_array($attribute) || empty($attribute['enabled'])) { continue; }
                    $value = $attribute['value'] ?? '';
                    if (is_bool($value)) { $value = $value ? 'Ja' : 'Nej'; }
                    if ($value === '' || $value === null) { continue; }
                    $specs .= '<dt>' . esc_html((string) ($attribute['label'] ?? $attribute['key'] ?? 'Felt')) . '</dt><dd>' . esc_html((string) $value) . '</dd>';
                }
                if ($specs !== '') { $specs = '<dl class="h18-clean-front-vehicle-specs" style="grid-template-columns:' . esc_attr((string) $labelWidth) . '% minmax(0,1fr)">' . $specs . '</dl>'; }
            }
            $gallery = '';
            if (!empty($props['showGallery'])) {
                $ids = array_values(array_unique(array_filter(array_merge([$featuredId], array_map('absint', is_array($fields['imageIds'] ?? null) ? $fields['imageIds'] : [])))));
                $images = '';
                foreach ($ids as $mediaId) { $url = wp_get_attachment_image_url($mediaId, 'large'); if (is_string($url) && $url !== '') { $images .= '<img src="' . esc_url($url) . '" alt="' . esc_attr((string) ($record['title'] ?? '')) . '">'; } }
                if ($images !== '') { $gallery = '<div class="h18-clean-front-vehicle-gallery">' . $images . '</div>'; }
            }
            $detailStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';color:' . $textColor . ';padding:' . $padding . 'px;';
            return '<article id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-vehicle-detail" style="' . esc_attr($detailStyle) . '">' . $hero . '<h2>' . esc_html((string) ($record['title'] ?? 'Køretøj')) . '</h2>' . $category . $summary . $description . $specs . $gallery . '</article>';
        }

'''
# Insert before image rendering branch after table/list branches.
replace_once('clean/hangar18-manager/src/Frontend/Renderer.php', "        if ($type === 'image') {\n", renderer_vehicle + "        if ($type === 'image') {\n")

# ---------------------------------------------------------------------------
# Release workflow gates
# ---------------------------------------------------------------------------
replace_once(
    '.github/workflows/visual-designer-release.yml',
    "          python3 .github/scripts/v0168_canvas_section_static_qa.py\n",
    "          python3 .github/scripts/v0168_canvas_section_static_qa.py\n          python3 .github/scripts/v0169_canvas_autoheight_qa.py\n          python3 .github/scripts/v0170_vehicle_module_qa.py\n",
)
replace_once(
    '.github/workflows/visual-designer-release.yml',
    "          grep -Fq 'VD-SELECTION-LAYER-001' CLEAN-TECHNICAL-MANUAL.md\n",
    "          grep -Fq 'VD-SELECTION-LAYER-001' CLEAN-TECHNICAL-MANUAL.md\n          grep -Fq 'VD-CANVAS-AUTOHEIGHT-001' CLEAN-TECHNICAL-MANUAL.md\n          grep -Fq 'VD-VEHICLE-MODULE-001' CLEAN-TECHNICAL-MANUAL.md\n",
)
replace_once(
    '.github/workflows/visual-designer-release.yml',
    "          test -s docs/v0168-status.md\n",
    "          test -s docs/v0168-status.md\n          test -s docs/v0169-status.md\n          test -s docs/v0170-status.md\n          test -s clean/hangar18-manager/src/Admin/VehicleAdminController.php\n          test -s clean/hangar18-manager/src/Modules/VehicleFieldRegistry.php\n",
)

# ---------------------------------------------------------------------------
# Manuals, release history and backlog sync
# ---------------------------------------------------------------------------
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', [])
if not any(str(item.get('version', '')) == '0.1.70' for item in versions if isinstance(item, dict)):
    versions.insert(0, {
        'version': '0.1.70',
        'date': '2026-08-31',
        'items': [
            'VD-VEHICLE-MODULE-001: Køretøjer er nu første fulde modul oven på Module/Data Foundation.',
            'Manager har CRUD, publiceringsstatus, sortering, primært billede, galleri og fælles fleksible tekniske felter.',
            'Designer har canonical Køretøjsliste og Køretøjsdetalje med dynamisk ModuleStore-binding.',
            'Listekort kan linke til én genbrugelig detaljeside via ?h18_vehicle=<record-id>.',
            'Designmanual, teknisk manual, brugermanual og backlog er synkroniseret til v0.1.70.'
        ],
    })
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

append_once('CLEAN-TECHNICAL-MANUAL.md', 'VD-VEHICLE-MODULE-001', r'''
## VD-VEHICLE-MODULE-001 – Køretøjsmodul v0.1.70

Køretøjer er første konkrete modul på `VD-MODULE-DATA-001`. Data gemmes som `h18_module_item` gennem `ModuleStore`, mens `VehicleFieldRegistry` ejer den fælles definition af fleksible tekniske felter. Et record består af stabilt record-ID, titel, status (`draft|publish|archive`), sortering, kort beskrivelse, kategori, beskrivelse, primært Media-ID, galleriets Media-IDer og canonical `attributes` for tekniske data. Felt-IDer er stabile ved omdøbning.

Visual Designer har to canonical leaf-typer: `vehiclelist` og `vehicledetail`. Begge normaliseres med `ModuleBinding` til modulet `vehicles`. `vehiclelist` forespørger kun publicerede records og kan linke til en valgt detaljeside med query-parameteren `h18_vehicle=<record-id>`. `vehicledetail` kan enten bindes til et fast record-ID eller, når `recordId` er tomt, resolve det samme ID fra query-parameteren. Offentlig rendering må aldrig vise `draft` eller `archive`; Designerens standalone preview må vise ikke-publicerede records for en bruger med `edit_pages`.

`ModuleStore::META_RECORD_ID` giver deterministisk detail-lookup. `findByRecordId()` har fallback til v0.1.67-records uden denne indeks-meta. Medier refereres kun som WordPress attachment IDs; frontend og Designer resolver URL ved rendering. Moduldata må ikke kopieres ind i side-layoutets JSON.
''')
append_once('CLEAN-DESIGN-MANUAL.md', 'Køretøjsmodul – designprincip', r'''
## Køretøjsmodul – designprincip

Køretøjsdata og sidedesign holdes adskilt. Et køretøj oprettes én gang under **Manager → Køretøjer** og kan derefter vises mange steder. **Køretøjsliste** er et layout-element til oversigter; det styrer kolonner, afstand, kortfarver, billede, kategori og kort beskrivelse. **Køretøjsdetalje** er et layout-element til den fulde visning og styrer hero-billede, galleri, beskrivelse og tekniske data.

Standardmønstret er én oversigtsside plus én genbrugelig detaljeside. Køretøjslisten peger på detaljesiden, og hvert kort sender sit stabile record-ID som `?h18_vehicle=...`. Detalje-elementet står i **Fra URL**-tilstand og viser dermed det valgte record uden at der skal oprettes en separat WordPress-side for hvert køretøj.

Tekniske felter defineres centralt. En ændring af feltets synlige navn må ikke ændre det stabile felt-ID. Billeder bliver i WordPress Media Library; modulrecords gemmer kun attachment IDs.
''')
append_once('CLEAN-USER-MANUAL.md', 'Sådan bruger du Køretøjsmodulet', r'''
## Sådan bruger du Køretøjsmodulet

Gå til **Visual Designer Manager → Køretøjer**. Vælg **Nyt køretøj**, skriv navn, kategori, status og sortering, tilføj en kort og en længere beskrivelse, vælg primært billede og eventuelle galleribilleder, og udfyld de tekniske data. **Publiceret** betyder, at recordet kan vises på den offentlige side; **Kladde** og **Arkiveret** vises ikke offentligt.

Under **Køretøjsfelter** kan du tilføje eller omdøbe de tekniske felter, vælge datatype, enhed og rækkefølge. Feltets interne ID bevares, så eksisterende data fortsat hører til det rigtige felt.

På en side i Visual Designer kan du tilføje **Køretøjsliste**. Her vælger du antal kolonner, sortering, hvilke oplysninger der vises, kortets udseende og den WordPress-side, som skal bruges til detaljer. Opret derefter en detaljeside med elementet **Køretøjsdetalje** og lad feltet **Køretøj** stå på **Fra URL**. Når en besøgende klikker et kort, åbnes detaljesiden med `?h18_vehicle=...`, og det rigtige køretøj vises automatisk. Du kan også vælge et fast køretøj i Inspector, hvis en side altid skal vise det samme record.
''')

# Rewrite backlog to current canonical status instead of keeping stale v0.1.68 roadmap.
backlog = r'''# Visual Designer Manager v0.1.x – canonical backlog

**Statusdato:** 31. august 2026  
**Aktuel release:** v0.1.70  
**Arkitekturgrænse:** `clean/hangar18-manager/`  
**Legacy-reference:** gammel Manager må bruges som read-only specifikation/migrationskilde; legacy editor-runtime må ikke blandes ind i Visual Designer Manager.

## Aktuel milepælsstatus · v0.1.70

- **HEADER/FOOTER — FÆRDIG:** multi-template, website-standarder, side-overrides, `Ingen`, migration, historik og fælles Preview/frontend-resolver er permanent regression-gate.
- **DESIGNER PRODUKTIVITET — IMPLEMENTERET:** keyboard nudge, clipboard/copy/paste/duplicate, sidekopi, Undo/Redo, versionshistorik og restore/kopi.
- **GENERELLE ELEMENTER — IMPLEMENTERET:** Tekst, Billede, Knap, Menu, Link, Mellemrum, Skillelinje, Ikon, Badge, Data List og Tabel inkl. tabelkanter.
- **VD-MODULE-DATA-001 — IMPLEMENTERET:** fælles ModuleRegistry, ModuleRecord, ModuleBinding og privat ModuleStore.
- **VD-CANVAS-SECTION-001 — IMPLEMENTERET:** Webside-root indeholder kun Sektioner; eksisterende Designer-sider migreres sikkert.
- **VD-SELECTION-LAYER-001 — IMPLEMENTERET:** selected/drag/resize løftes kun visuelt i editoren.
- **VD-CANVAS-AUTOHEIGHT-001 — IMPLEMENTERET I v0.1.69:** Webside/canvas vokser og krymper automatisk efter nederste root-Sektion.
- **VD-VEHICLE-MODULE-001 — IMPLEMENTERET I v0.1.70:** Køretøjer har Manager-CRUD, fleksible tekniske felter, billeder, sortering og Designer-list/detail-binding.

## Roadmap

1. **v0.1.69 – Canvas Auto Height — FÆRDIG.**
2. **v0.1.70 – Køretøjsmodul — FÆRDIG.**
3. **v0.1.71 – Events — NÆSTE:** CRUD på fælles ModuleStore, dato/tid, sted, status, automatisk kommende/afholdte visninger og Designer list/detail-elementer.
4. **v0.1.72 – Billedgalleri — PLANLAGT:** album, Media Library-referencer, sortering, cover og genbrugeligt Designer galleri/album-element.
5. **Efter modulerne:** samlet data-/module-migrering fra legacy, med side-by-side QA før cutover.

## Åben backlog

### VD-EVENT-MODULE-001 — NÆSTE
- Manager-CRUD på `events`-modulet.
- Start/slut, sted, kort/længere beskrivelse, status og billeder.
- Sortering samt kommende/afholdte regler uden at slette historiske events.
- Canonical Designer-elementer til Eventliste og Eventdetalje.
- Frontend må kun vise records efter den valgte status-/datoregel.

### VD-GALLERY-MODULE-001 — PLANLAGT
- Album-CRUD på `galleries`.
- Cover, beskrivelse og sorteret Media Library-liste.
- Designer-element til albumoversigt og albumvisning.
- Ingen billedbytes i layout-JSON eller module JSON; kun attachment IDs.

### CLEAN-RESPONSIVE-009 — DELVIST / MANUEL QA
- Canonical model har Desktop/Laptop/Tablet/Mobil geometri og arv.
- Desktop/Laptop/Mobil kan previewes i den nuværende viewport-runtime.
- Tablet skal have samme fulde, eksplicitte toolbar/preview-flow som de øvrige, før punktet lukkes.
- Breakpointændringer skal fortsat være Undo/Redo-sikre og må ikke mutere andre breakpoints.

### CLEAN-THEME-010 — IMPLEMENTERET BASELINE / REGRESSION FORTSÆTTER
- Theme shell og Header/Footer bruges på Visual Designer-sider.
- Banner, menu, farver, typografi og sitebredde skal fortsat regressionskontrolleres ved ændringer i fælles Designer/CSS.

### CLEAN-PREVIEW-013 — IMPLEMENTERET
- Ugemt canonical state kan previewes gennem samme PHP Renderer-kontrakt.
- Samlet preview kan vise Header + side + Footer uden at publicere.
- Admin-DOM klones ikke som frontend-kilde.

### CLEAN-MIGRATOR-014 — DELVIST / BLOKERET FOR MODULE-CUTOVER
- Eksisterende sidekonvertering er implementeret som ikke-destruktiv kandidat/QA-flow.
- Køretøjer, Events og Galleri migreres først, når de respektive nye moduler er færdige.
- Legacy-data læses read-only og originalen må ikke overskrives automatisk.

## v0.1.70 Køretøjsmodul – QA-gate

1. Opret et nyt køretøj som Kladde med primært billede, galleri og mindst tre tekniske felter.
2. Reload Manager og verificér identisk record, stabile field IDs og korrekt Media-ID-reference.
3. Redigér felt-navnet i Køretøjsfelter og verificér at recordets værdi stadig ligger under samme interne felt-ID.
4. Sæt record til Publiceret og opret mindst to yderligere publicerede records med forskellige sorteringsværdier.
5. Tilføj Køretøjsliste i Designer; test kolonner, sortering, vis/skjul billede/kategori/beskrivelse og kortdesign.
6. Opret en detaljeside med Køretøjsdetalje i “Fra URL”-tilstand og vælg den som detaljeside i listen.
7. Klik hvert listekort på frontend og verificér at `?h18_vehicle=<record-id>` viser korrekt record, billeder og tekniske data.
8. Sæt et record tilbage til Kladde/Arkiveret; det må ikke længere kunne vises offentligt via en direkte detail-URL.
9. Test et fast record-ID i Køretøjsdetalje Inspector.
10. Gem/reload/Undo/Redo Designer-sider med begge køretøjselementer og verificér canonical modelparitet.

## Global release-gate

- PHP/JavaScript syntax QA skal være grøn.
- Historiske regression-gates fra Header/Footer, clipboard, generelle elementer, Module Foundation, Canvas/Section og Canvas Auto Height skal forblive grønne.
- Release-ZIP bygges kun af central `visual-designer-release.yml`, SHA-256 skrives til `clean-update.json`, og versionen anses først for frigivet efter successful workflow + manifestkontrol.
'''
write('docs/clean-backlog-v0100.md', backlog)

write('clean-release-notes.html', '''<h4>0.1.70 – Køretøjsmodul</h4>\n<ul>\n<li>Manager → Køretøjer har CRUD, status, sortering, primært billede og galleri.</li>\n<li>Køretøjsfelter er fleksible og bruger stabile felt-IDer.</li>\n<li>Visual Designer har Køretøjsliste og Køretøjsdetalje med dynamisk ModuleStore-binding.</li>\n<li>Én detaljeside kan genbruges via <code>?h18_vehicle=&lt;record-id&gt;</code>.</li>\n<li>Designmanual, Brugermanual, Teknisk manual og backlog er opdateret til v0.1.70.</li>\n</ul>\n''')
write('docs/v0170-status.md', '''# Visual Designer Manager v0.1.70\n\nStatus: release candidate\n\n- VD-VEHICLE-MODULE-001 implementeret.\n- Manager CRUD + Køretøjsfelter + billeder + sortering.\n- Canonical vehiclelist / vehicledetail elementer med ModuleBinding.\n- Detailrouting via h18_vehicle query parameter.\n- Designmanual, brugermanual, teknisk manual, releasehistorik og backlog synkroniseret.\n- v0.1.69 Canvas Auto Height forbliver regression-gate.\n''')

print('Applied Visual Designer Manager v0.1.70 vehicle module')
