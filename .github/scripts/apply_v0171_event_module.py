from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f'Missing required file: {path}')
    return p.read_text(encoding='utf-8')


def write(path: str, value: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding='utf-8')


def replace_once(path: str, old: str, new: str) -> None:
    value = read(path)
    if new in value:
        return
    if old not in value:
        raise SystemExit(f'{path}: replacement anchor missing: {old[:90]}')
    write(path, value.replace(old, new, 1))


def append_once(path: str, marker: str, addition: str) -> None:
    value = read(path)
    if marker not in value:
        write(path, value.rstrip() + '\n\n' + addition.strip() + '\n')


PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
ADMIN = 'clean/hangar18-manager/src/Admin/AdminController.php'
EDITOR = 'clean/hangar18-manager/src/Admin/EditorController.php'
STATUS = 'clean/hangar18-manager/assets/admin-v0123.js'
STORE = 'clean/hangar18-manager/src/Modules/ModuleStore.php'
MODEL = 'clean/hangar18-manager/src/Model/LayoutModel.php'
CORE = 'clean/hangar18-manager/assets/editor-v018-core.js'
PREVIEW_CSS = 'clean/hangar18-manager/assets/editor-v0166-foundation.css'
RENDERER = 'clean/hangar18-manager/src/Frontend/Renderer.php'

# Version + bootstrap.
replace_once(PLUGIN, ' * Version: 0.1.70', ' * Version: 0.1.71')
replace_once(PLUGIN, "define('H18_CLEAN_VERSION', '0.1.70');", "define('H18_CLEAN_VERSION', '0.1.71');")
replace_once(PLUGIN, "require_once H18_CLEAN_DIR . 'src/Admin/VehicleAdminController.php';", "require_once H18_CLEAN_DIR . 'src/Admin/VehicleAdminController.php';\nrequire_once H18_CLEAN_DIR . 'src/Admin/EventAdminController.php';")
replace_once(PLUGIN, '    \\VisualDesignerManager\\Admin\\VehicleAdminController::register();', '    \\VisualDesignerManager\\Admin\\VehicleAdminController::register();\n    \\VisualDesignerManager\\Admin\\EventAdminController::register();')
replace_once(PLUGIN,
"    }, \\VisualDesignerManager\\Modules\\ModuleStore::listRecords('vehicles', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC'])));\n\n    wp_enqueue_script(",
"""    }, \\VisualDesignerManager\\Modules\\ModuleStore::listRecords('vehicles', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC'])));

    $eventRecords = array_values(array_map(static function (array $item): array {
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
        ];
    }, \\VisualDesignerManager\\Modules\\ModuleStore::listRecords('events', ['status' => 'all', 'limit' => 100, 'orderBy' => 'start', 'order' => 'ASC'])));

    wp_enqueue_script(""")
replace_once(PLUGIN, "        'vehicleAdminUrl' => admin_url('admin.php?page=h18-clean-vehicles'),", "        'vehicleAdminUrl' => admin_url('admin.php?page=h18-clean-vehicles'),\n        'eventRecords' => $eventRecords,\n        'eventAdminUrl' => admin_url('admin.php?page=h18-clean-events'),")

# Event Manager CRUD. Uses the existing generic media picker asset from v0.1.70.
write('clean/hangar18-manager/src/Admin/EventAdminController.php', r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Modules\ModuleStore;

final class EventAdminController
{
    public const PAGE = 'h18-clean-events';
    private const SAVE_ACTION = 'h18_clean_save_event';
    private const DELETE_ACTION = 'h18_clean_delete_event';
    private const NONCE_SAVE = 'h18_clean_save_event';
    private const NONCE_DELETE = 'h18_clean_delete_event';

    public static function register(): void
    {
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'saveEvent']);
        add_action('admin_post_' . self::DELETE_ACTION, [self::class, 'deleteEvent']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    public static function enqueue(string $hook): void
    {
        if (strpos($hook, self::PAGE) === false || !current_user_can('edit_pages')) { return; }
        wp_enqueue_media();
        wp_enqueue_script('h18-vd-module-media', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.js', [], H18_CLEAN_VERSION, true);
        wp_enqueue_style('h18-vd-event-admin', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.css', [], H18_CLEAN_VERSION);
    }

    public static function render(): void
    {
        if (!current_user_can('edit_pages')) { wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager')); }
        $editId = isset($_GET['edit']) ? absint($_GET['edit']) : 0;
        $record = $editId > 0 ? ModuleStore::get($editId) : null;
        if ($record !== null && (string) ($record['module'] ?? '') !== 'events') { $record = null; $editId = 0; }
        $state = isset($_GET['h18_status']) ? sanitize_key((string) wp_unslash($_GET['h18_status'])) : '';
        $message = isset($_GET['h18_message']) ? sanitize_text_field((string) wp_unslash($_GET['h18_message'])) : '';
        echo '<div class="wrap h18-clean-admin"><h1>Events</h1><p class="description">Canonical Event-data i fælles ModuleStore. Historiske events slettes ikke automatisk; de kan blive stående publiceret eller arkiveres.</p>';
        if ($message !== '') { echo '<div class="notice ' . ($state === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }
        self::renderList($editId); self::renderEditor($editId, $record); echo '</div>';
    }

    private static function renderList(int $editId): void
    {
        $items = ModuleStore::listRecords('events', ['status' => 'all', 'limit' => 100, 'orderBy' => 'start', 'order' => 'ASC']);
        echo '<h2>Eventoversigt</h2>';
        if (!$items) { echo '<p>Ingen events endnu.</p>'; return; }
        echo '<table class="widefat striped"><thead><tr><th>Titel</th><th>Start</th><th>Slut</th><th>Sted</th><th>Status</th><th>Record-ID</th><th>Handlinger</th></tr></thead><tbody>';
        foreach ($items as $item) {
            $postId = (int) ($item['postId'] ?? 0); $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : []; $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            echo '<tr' . ($editId === $postId ? ' class="is-active"' : '') . '><td><strong>' . esc_html((string) ($record['title'] ?? 'Event')) . '</strong></td><td>' . esc_html(self::dateTimeLabel((string) ($fields['start'] ?? ''))) . '</td><td>' . esc_html(self::dateTimeLabel((string) ($fields['end'] ?? ''))) . '</td><td>' . esc_html((string) ($fields['location'] ?? '')) . '</td><td>' . esc_html(self::statusLabel((string) ($record['status'] ?? 'draft'))) . '</td><td><code>' . esc_html((string) ($record['id'] ?? '')) . '</code></td><td>';
            echo '<a class="button button-small" href="' . esc_url(admin_url('admin.php?page=' . self::PAGE . '&edit=' . $postId)) . '">Redigér</a> <form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">'; wp_nonce_field(self::NONCE_DELETE);
            echo '<input type="hidden" name="action" value="' . esc_attr(self::DELETE_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '"><button type="submit" class="button button-small button-link-delete" onclick="return confirm(\'Slet eventet permanent? Historiske events bør normalt arkiveres i stedet.\');">Slet</button></form></td></tr>';
        }
        echo '</tbody></table>';
    }

    /** @param array<string,mixed>|null $record */
    private static function renderEditor(int $postId, ?array $record): void
    {
        $fields = $record !== null && is_array($record['fields'] ?? null) ? $record['fields'] : [];
        $title = (string) ($record['title'] ?? ''); $status = (string) ($record['status'] ?? 'draft'); $summary = (string) ($record['summary'] ?? ''); $sortOrder = (int) ($record['sortOrder'] ?? 0); $featuredId = absint($record['featuredMediaId'] ?? 0);
        $start = self::dateTimeInput((string) ($fields['start'] ?? '')); $end = self::dateTimeInput((string) ($fields['end'] ?? '')); $location = (string) ($fields['location'] ?? ''); $description = (string) ($fields['description'] ?? '');
        echo '<hr><h2>' . ($postId > 0 ? 'Redigér event' : 'Opret event') . '</h2><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'; wp_nonce_field(self::NONCE_SAVE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SAVE_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '"><div class="h18-vd-vehicle-layout"><div>';
        echo '<label><strong>Titel</strong><input class="widefat" required type="text" name="title" value="' . esc_attr($title) . '"></label><div class="h18-clean-field-grid"><label><strong>Start</strong><input required type="datetime-local" name="start" value="' . esc_attr($start) . '"></label><label><strong>Slut</strong><input type="datetime-local" name="end" value="' . esc_attr($end) . '"></label></div><label><strong>Sted</strong><input class="widefat" type="text" name="location" value="' . esc_attr($location) . '"></label><label><strong>Kort beskrivelse</strong><textarea class="widefat" rows="3" name="summary">' . esc_textarea($summary) . '</textarea></label><label><strong>Beskrivelse</strong>';
        wp_editor($description, 'h18_event_description', ['textarea_name' => 'description', 'textarea_rows' => 9, 'media_buttons' => false, 'teeny' => true]); echo '</label></div><aside>';
        echo '<label><strong>Status</strong><select class="widefat" name="status"><option value="draft"' . selected($status, 'draft', false) . '>Kladde</option><option value="publish"' . selected($status, 'publish', false) . '>Publiceret</option><option value="archive"' . selected($status, 'archive', false) . '>Arkiveret</option></select></label><label><strong>Sortering</strong><input class="widefat" type="number" name="sort_order" value="' . esc_attr((string) $sortOrder) . '"></label><label><strong>Primært billede</strong><input id="h18-event-featured" type="hidden" name="featured_media_id" value="' . esc_attr((string) $featuredId) . '"></label><p><button type="button" class="button h18-vd-media-pick" data-target="h18-event-featured">Vælg primært billede</button> <button type="button" class="button h18-vd-media-clear" data-target="h18-event-featured">Ryd</button></p><div class="h18-vd-media-preview" data-media-preview="h18-event-featured">';
        if ($featuredId > 0) { $url = wp_get_attachment_image_url($featuredId, 'thumbnail'); if (is_string($url) && $url !== '') { echo '<img src="' . esc_url($url) . '" alt="">'; } } else { echo '<span class="description">Intet billede valgt</span>'; }
        echo '</div><p><button type="submit" class="button button-primary">' . ($postId > 0 ? 'Gem event' : 'Opret event') . '</button>'; if ($postId > 0) { echo ' <a class="button" href="' . esc_url(admin_url('admin.php?page=' . self::PAGE)) . '">Annullér</a>'; } echo '</p></aside></div></form>';
    }

    public static function saveEvent(): void
    {
        if (!current_user_can('edit_pages')) { wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager')); } check_admin_referer(self::NONCE_SAVE);
        $postId = isset($_POST['post_id']) ? absint($_POST['post_id']) : 0; $title = sanitize_text_field((string) wp_unslash($_POST['title'] ?? '')); $status = sanitize_key((string) wp_unslash($_POST['status'] ?? 'draft')); $status = in_array($status, ['draft', 'publish', 'archive'], true) ? $status : 'draft';
        $start = self::dateTimeInput(sanitize_text_field((string) wp_unslash($_POST['start'] ?? ''))); $end = self::dateTimeInput(sanitize_text_field((string) wp_unslash($_POST['end'] ?? '')));
        if ($title === '') { self::redirect('error', 'Titel er påkrævet.', $postId); } if ($start === '') { self::redirect('error', 'Startdato og -tid er påkrævet.', $postId); } if ($end !== '' && strcmp($end, $start) < 0) { self::redirect('error', 'Sluttid må ikke ligge før starttid.', $postId); }
        $raw = ['title' => $title, 'status' => $status, 'summary' => sanitize_textarea_field((string) wp_unslash($_POST['summary'] ?? '')), 'sortOrder' => isset($_POST['sort_order']) ? (int) $_POST['sort_order'] : 0, 'featuredMediaId' => isset($_POST['featured_media_id']) ? absint($_POST['featured_media_id']) : 0, 'fields' => ['start' => $start, 'end' => $end, 'location' => sanitize_text_field((string) wp_unslash($_POST['location'] ?? '')), 'description' => wp_kses_post((string) wp_unslash($_POST['description'] ?? ''))]];
        $result = ModuleStore::save('events', $raw, $postId); if (is_wp_error($result)) { self::redirect('error', $result->get_error_message(), $postId); } self::redirect('ok', $postId > 0 ? 'Event opdateret.' : 'Event oprettet.', (int) $result);
    }

    public static function deleteEvent(): void
    {
        if (!current_user_can('edit_pages')) { wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager')); } check_admin_referer(self::NONCE_DELETE); $postId = isset($_POST['post_id']) ? absint($_POST['post_id']) : 0; $record = ModuleStore::get($postId);
        if ($record === null || (string) ($record['module'] ?? '') !== 'events') { self::redirect('error', 'Eventet findes ikke.', 0); }
        $result = ModuleStore::delete($postId); if (is_wp_error($result) || $result !== true) { self::redirect('error', is_wp_error($result) ? $result->get_error_message() : 'Eventet kunne ikke slettes.', 0); } self::redirect('ok', 'Event slettet.', 0);
    }

    private static function dateTimeInput(string $value): string { $value = trim($value); return preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/', $value) === 1 ? substr($value, 0, 16) : ''; }
    private static function dateTimeLabel(string $value): string { $value = self::dateTimeInput($value); return $value === '' ? '—' : str_replace('T', ' ', $value); }
    private static function statusLabel(string $status): string { return ['draft' => 'Kladde', 'publish' => 'Publiceret', 'archive' => 'Arkiveret'][$status] ?? 'Kladde'; }
    private static function redirect(string $status, string $message, int $editId): void { $args = ['page' => self::PAGE, 'h18_status' => $status, 'h18_message' => $message]; if ($editId > 0) { $args['edit'] = $editId; } wp_safe_redirect(add_query_arg($args, admin_url('admin.php'))); exit; }
    private function __construct() {}
}
''')

replace_once(ADMIN, "add_submenu_page(self::MENU, 'Events', 'Events', 'edit_pages', 'h18-clean-events', [self::class, 'events']);", "add_submenu_page(self::MENU, 'Events', 'Events', 'edit_pages', 'h18-clean-events', [EventAdminController::class, 'render']);")
replace_once(STATUS, "'h18-clean-events': ['Ikke færdig', 'planned']", "'h18-clean-events': ['Klar', 'ready']")
replace_once(EDITOR, "            'vehicledetail' => 'Køretøjsdetalje',", "            'vehicledetail' => 'Køretøjsdetalje',\n            'eventlist' => 'Eventliste',\n            'eventdetail' => 'Eventdetalje',")

# Shared chronological sorting.
replace_once(STORE, "if (!in_array($orderBy, ['sortOrder', 'title', 'updatedAt'], true)) {", "if (!in_array($orderBy, ['sortOrder', 'title', 'updatedAt', 'start'], true)) {")
replace_once(STORE, """            } elseif ($orderBy === 'updatedAt') {
                $cmp = strcmp((string) ($left['updatedAt'] ?? ''), (string) ($right['updatedAt'] ?? ''));
            } else {""", """            } elseif ($orderBy === 'updatedAt') {
                $cmp = strcmp((string) ($left['updatedAt'] ?? ''), (string) ($right['updatedAt'] ?? ''));
            } elseif ($orderBy === 'start') {
                $leftFields = isset($left['fields']) && is_array($left['fields']) ? $left['fields'] : [];
                $rightFields = isset($right['fields']) && is_array($right['fields']) ? $right['fields'] : [];
                $leftStart = (string) ($leftFields['start'] ?? ''); $rightStart = (string) ($rightFields['start'] ?? '');
                if ($leftStart === '' && $rightStart !== '') { $cmp = 1; } elseif ($leftStart !== '' && $rightStart === '') { $cmp = -1; } else { $cmp = strcmp($leftStart, $rightStart); }
                if ($cmp === 0) { $cmp = strnatcasecmp((string) ($left['title'] ?? ''), (string) ($right['title'] ?? '')); }
            } else {""")

# Canonical Event elements in PHP.
replace_once(MODEL, "'table', 'vehiclelist', 'vehicledetail'", "'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail'")
EVENT_MODEL = r'''        if ($type === 'eventlist') {
            $orderBy = in_array((string) ($raw['orderBy'] ?? 'start'), ['start', 'title', 'updatedAt'], true) ? (string) ($raw['orderBy'] ?? 'start') : 'start';
            $order = strtoupper((string) ($raw['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
            $limit = self::clamp($raw['limit'] ?? 50, 1, 100, 50);
            $dateFilter = in_array((string) ($raw['dateFilter'] ?? 'upcoming'), ['all', 'upcoming', 'past'], true) ? (string) ($raw['dateFilter'] ?? 'upcoming') : 'upcoming';
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'events', 'view' => 'list', 'query' => ['status' => 'publish', 'orderBy' => $orderBy, 'order' => $order, 'limit' => $limit]]);
            return array_merge(['binding' => $binding, 'limit' => $limit, 'orderBy' => $orderBy, 'order' => $order, 'dateFilter' => $dateFilter, 'detailPageId' => absint($raw['detailPageId'] ?? 0), 'columns' => self::clamp($raw['columns'] ?? 3, 1, 4, 3), 'cardGap' => self::clamp($raw['cardGap'] ?? 18, 0, 80, 18), 'cardPadding' => self::clamp($raw['cardPadding'] ?? 12, 0, 60, 12), 'imageHeight' => self::clamp($raw['imageHeight'] ?? 180, 60, 600, 180), 'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true, 'showDate' => array_key_exists('showDate', $raw) ? (bool) $raw['showDate'] : true, 'showLocation' => array_key_exists('showLocation', $raw) ? (bool) $raw['showLocation'] : true, 'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true, 'linkCards' => array_key_exists('linkCards', $raw) ? (bool) $raw['linkCards'] : true, 'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'cardRadius' => self::clamp($raw['cardRadius'] ?? 4, 0, 60, 4)], $border);
        }
        if ($type === 'eventdetail') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? ''))); if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'events', 'view' => 'detail', 'recordId' => $recordId]);
            return array_merge(['binding' => $binding, 'recordId' => $recordId, 'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true, 'showDate' => array_key_exists('showDate', $raw) ? (bool) $raw['showDate'] : true, 'showLocation' => array_key_exists('showLocation', $raw) ? (bool) $raw['showLocation'] : true, 'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true, 'showDescription' => array_key_exists('showDescription', $raw) ? (bool) $raw['showDescription'] : true, 'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 900, 360), 'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'padding' => self::clamp($raw['padding'] ?? 16, 0, 80, 16), 'radius' => self::clamp($raw['radius'] ?? 4, 0, 60, 4)], $border);
        }
'''
replace_once(MODEL, "        if ($type === 'image') {", EVENT_MODEL + "\n        if ($type === 'image') {")

# JavaScript model, preview and Inspector.
replace_once(CORE, "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail'];", "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail'];")
replace_once(CORE, "vehiclelist:'Køretøjsliste',vehicledetail:'Køretøjsdetalje'", "vehiclelist:'Køretøjsliste',vehicledetail:'Køretøjsdetalje',eventlist:'Eventliste',eventdetail:'Eventdetalje'")
replace_once(CORE, """    function vehicleCategory(record) {
        return record && record.fields && typeof record.fields === 'object' ? String(record.fields.category || '') : '';
    }

    function iconLibrarySets()""", """    function vehicleCategory(record) {
        return record && record.fields && typeof record.fields === 'object' ? String(record.fields.category || '') : '';
    }
    function eventRecords() { return Array.isArray(CFG.eventRecords) ? CFG.eventRecords.filter(function (record) { return record && record.id; }) : []; }
    function eventRecordById(recordId) { recordId = String(recordId || ''); return eventRecords().find(function (record) { return String(record.id || '') === recordId; }) || null; }
    function eventDateLabel(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const start=String(fields.start||'').replace('T',' '), end=String(fields.end||'').replace('T',' '); return start&&end?(start+' – '+end):start; }
    function eventIsPast(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const edge=String(fields.end||fields.start||''); if(!edge){return false;} const timestamp=Date.parse(edge); return Number.isFinite(timestamp)&&timestamp<Date.now(); }

    function iconLibrarySets()""")
EVENT_JS_MODEL = r'''        if (type === 'eventlist') {
            const orderBy=['start','title','updatedAt'].includes(String(raw.orderBy||'start'))?String(raw.orderBy||'start'):'start'; const order=String(raw.order||'ASC').toUpperCase()==='DESC'?'DESC':'ASC'; const limit=clamp(parseInt(raw.limit||50,10)||50,1,100); const dateFilter=['all','upcoming','past'].includes(String(raw.dateFilter||'upcoming'))?String(raw.dateFilter||'upcoming'):'upcoming';
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'events',view:'list',recordId:'',query:{status:'publish',orderBy:orderBy,order:order,limit:limit},fieldMap:{}},limit:limit,orderBy:orderBy,order:order,dateFilter:dateFilter,detailPageId:parseInt(raw.detailPageId||0,10)||0,columns:clamp(parseInt(raw.columns||3,10)||3,1,4),cardGap:clamp(parseInt(raw.cardGap||18,10)||18,0,80),cardPadding:clamp(parseInt(raw.cardPadding||12,10)||12,0,60),imageHeight:clamp(parseInt(raw.imageHeight||180,10)||180,60,600),showImage:raw.showImage!==false,showDate:raw.showDate!==false,showLocation:raw.showLocation!==false,showSummary:raw.showSummary!==false,linkCards:raw.linkCards!==false,cardBackground:normalizeColor(raw.cardBackground||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),cardRadius:clamp(parseInt(raw.cardRadius||4,10)||4,0,60)});
        }
        if (type === 'eventdetail') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'events',view:'detail',recordId:recordId,query:{status:'publish',orderBy:'start',order:'ASC',limit:50},fieldMap:{}},recordId:recordId,showImage:raw.showImage!==false,showDate:raw.showDate!==false,showLocation:raw.showLocation!==false,showSummary:raw.showSummary!==false,showDescription:raw.showDescription!==false,imageHeight:clamp(parseInt(raw.imageHeight||360,10)||360,80,900),background:normalizeColor(raw.background||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),padding:clamp(parseInt(raw.padding||16,10)||16,0,80),radius:clamp(parseInt(raw.radius||4,10)||4,0,60)});
        }
'''
core = read(CORE)
if "if (type === 'eventlist')" not in core:
    anchor = "        if (type === 'image') {"; pos = core.find(anchor)
    if pos < 0: raise SystemExit('editor core: normalize image anchor missing')
    write(CORE, core[:pos] + EVENT_JS_MODEL + '\n' + core[pos:])
replace_once(CORE, 'vehiclelist:42,vehicledetail:54', 'vehiclelist:42,vehicledetail:54,eventlist:38,eventdetail:46')
EVENT_PREVIEW = r'''        } else if (node.type === 'eventlist') {
            wrap.classList.add('h18-clean-node-preview--eventlist'); let records=eventRecords().filter(function(record){return String(record.status||'')==='publish';}); if(node.props.dateFilter==='upcoming'){records=records.filter(function(record){return !eventIsPast(record);});}else if(node.props.dateFilter==='past'){records=records.filter(eventIsPast);} records=records.slice(0,node.props.limit||50);
            const grid=document.createElement('div'); grid.className='h18-vd-event-list-preview'; grid.style.gridTemplateColumns='repeat('+String(node.props.columns||3)+',minmax(0,1fr))'; grid.style.gap=String(node.props.cardGap||18)+'px'; if(!records.length){grid.textContent='Ingen publicerede events matcher filteret · opret dem under Manager → Events';}
            records.forEach(function(record){const card=document.createElement('article'); card.className='h18-vd-event-card-preview'; card.style.padding=String(node.props.cardPadding||12)+'px'; card.style.borderRadius=String(node.props.cardRadius||4)+'px'; card.style.background=node.props.cardBackground||'#ffffff'; card.style.color=node.props.textColor||'#30382a'; if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';img.style.height=String(node.props.imageHeight||180)+'px';card.appendChild(img);} const title=document.createElement('strong');title.textContent=String(record.title||'Event');card.appendChild(title);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDate!==false&&eventDateLabel(record)){const meta=document.createElement('small');meta.textContent=eventDateLabel(record);meta.style.color=node.props.accentColor||'#c3ae83';card.appendChild(meta);}if(node.props.showLocation!==false&&fields.location){const loc=document.createElement('small');loc.textContent=String(fields.location);card.appendChild(loc);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);card.appendChild(p);}grid.appendChild(card);}); wrap.appendChild(grid);
        } else if (node.type === 'eventdetail') {
            wrap.classList.add('h18-clean-node-preview--eventdetail'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const box=document.createElement('article');box.className='h18-vd-event-detail-preview';box.style.background=node.props.background||'#ffffff';box.style.color=node.props.textColor||'#30382a';box.style.padding=String(node.props.padding||16)+'px';box.style.borderRadius=String(node.props.radius||4)+'px'; if(!record){box.textContent='Vælg et event i Inspector eller opret et under Manager → Events';wrap.appendChild(box);}else{if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';img.style.height=String(node.props.imageHeight||360)+'px';box.appendChild(img);}const h=document.createElement('h3');h.textContent=String(record.title||'Event');box.appendChild(h);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDate!==false&&eventDateLabel(record)){const meta=document.createElement('p');meta.textContent=eventDateLabel(record);meta.style.color=node.props.accentColor||'#c3ae83';box.appendChild(meta);}if(node.props.showLocation!==false&&fields.location){const loc=document.createElement('p');loc.textContent=String(fields.location);box.appendChild(loc);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);box.appendChild(p);}if(node.props.showDescription!==false&&fields.description){const desc=document.createElement('div');desc.innerHTML=richPreviewHtml(String(fields.description));box.appendChild(desc);}wrap.appendChild(box);}
'''
replace_once(CORE, "        } else if (node.type === 'image') {", EVENT_PREVIEW + "\n        } else if (node.type === 'image') {")
EVENT_INSPECTOR = r'''        } else if (node.type === 'eventlist') {
            html += '<div class="h18-vd-menu-group"><h3>Eventliste</h3><p class="description">Data kommer fra Manager → Events. Frontend viser kun publicerede records.</p><label>Detaljeside<select data-field="eventDetailPageId"><option value="0">Ingen link / vælg senere</option>'+(Array.isArray(CFG.pages)?CFG.pages.map(function(page){const id=parseInt(page.id||0,10)||0;return '<option value="'+id+'"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>';}).join(''):'')+'</select></label>';
            html += '<div class="h18-clean-field-grid"><label>Visning<select data-field="eventDateFilter"><option value="upcoming"'+(node.props.dateFilter==='upcoming'?' selected':'')+'>Kommende</option><option value="past"'+(node.props.dateFilter==='past'?' selected':'')+'>Afholdte</option><option value="all"'+(node.props.dateFilter==='all'?' selected':'')+'>Alle publicerede</option></select></label><label>Kolonner<input data-field="eventColumns" type="number" min="1" max="4" value="'+(node.props.columns||3)+'"></label><label>Max. records<input data-field="eventLimit" type="number" min="1" max="100" value="'+(node.props.limit||50)+'"></label><label>Sortér efter<select data-field="eventOrderBy"><option value="start"'+(node.props.orderBy==='start'?' selected':'')+'>Startdato</option><option value="title"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value="updatedAt"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field="eventOrder"><option value="ASC"'+(node.props.order!=='DESC'?' selected':'')+'>Stigende</option><option value="DESC"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Kortafstand px<input data-field="eventCardGap" type="number" min="0" max="80" value="'+(node.props.cardGap||18)+'"></label><label>Kortpadding px<input data-field="eventCardPadding" type="number" min="0" max="60" value="'+(node.props.cardPadding||12)+'"></label><label>Billedhøjde px<input data-field="eventImageHeight" type="number" min="60" max="600" value="'+(node.props.imageHeight||180)+'"></label><label>Hjørner px<input data-field="eventCardRadius" type="number" min="0" max="60" value="'+(node.props.cardRadius||4)+'"></label></div><label class="h18-clean-checkbox"><input data-field="eventShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class="h18-clean-checkbox"><input data-field="eventShowDate" type="checkbox"'+(node.props.showDate!==false?' checked':'')+'> Vis dato/tid</label><label class="h18-clean-checkbox"><input data-field="eventShowLocation" type="checkbox"'+(node.props.showLocation!==false?' checked':'')+'> Vis sted</label><label class="h18-clean-checkbox"><input data-field="eventShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="eventLinkCards" type="checkbox"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside med ?h18_event=record-id</label><div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="eventCardBackground" type="color" value="'+escapeAttr(node.props.cardBackground||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="eventAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>'; if(CFG.eventAdminUrl){html+='<p><a class="button" href="'+escapeAttr(String(CFG.eventAdminUrl))+'">Administrér events</a></p>';}
        } else if (node.type === 'eventdetail') {
            html += '<div class="h18-vd-menu-group"><h3>Eventdetalje</h3><label>Event<select data-field="eventRecordId"><option value="">Fra URL · ?h18_event=record-id</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+' · '+escapeHtml(String(record.status||''))+'</option>';}).join('')+'</select></label><p class="description">Lad feltet stå på “Fra URL”, når samme detaljeside bruges af alle kort.</p><label class="h18-clean-checkbox"><input data-field="eventShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class="h18-clean-checkbox"><input data-field="eventShowDate" type="checkbox"'+(node.props.showDate!==false?' checked':'')+'> Vis dato/tid</label><label class="h18-clean-checkbox"><input data-field="eventShowLocation" type="checkbox"'+(node.props.showLocation!==false?' checked':'')+'> Vis sted</label><label class="h18-clean-checkbox"><input data-field="eventShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="eventShowDescription" type="checkbox"'+(node.props.showDescription!==false?' checked':'')+'> Vis beskrivelse</label><div class="h18-clean-field-grid"><label>Billedhøjde px<input data-field="eventImageHeight" type="number" min="80" max="900" value="'+(node.props.imageHeight||360)+'"></label><label>Padding px<input data-field="padding" type="number" min="0" max="80" value="'+(node.props.padding||16)+'"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="60" value="'+(node.props.radius||4)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="eventAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>'; if(CFG.eventAdminUrl){html+='<p><a class="button" href="'+escapeAttr(String(CFG.eventAdminUrl))+'">Administrér events</a></p>';}
'''
replace_once(CORE, "            if (CFG.vehicleAdminUrl) { html += '<p><a class=\"button\" href=\"'+escapeAttr(String(CFG.vehicleAdminUrl))+'\">Administrér køretøjer</a></p>'; }\n        } else if (node.type === 'image') {", "            if (CFG.vehicleAdminUrl) { html += '<p><a class=\"button\" href=\"'+escapeAttr(String(CFG.vehicleAdminUrl))+'\">Administrér køretøjer</a></p>'; }\n" + EVENT_INSPECTOR + "\n        } else if (node.type === 'image') {")
EVENT_HANDLERS = r'''                else if (field === 'eventDetailPageId') { current.props.detailPageId=parseInt(control.value||0,10)||0; }
                else if (field === 'eventDateFilter') { current.props.dateFilter=['all','upcoming','past'].includes(control.value)?control.value:'upcoming'; }
                else if (field === 'eventColumns') { current.props.columns=clamp(parseInt(control.value||3,10)||3,1,4); }
                else if (field === 'eventLimit') { current.props.limit=clamp(parseInt(control.value||50,10)||50,1,100); if(current.props.binding&&current.props.binding.query){current.props.binding.query.limit=current.props.limit;} }
                else if (field === 'eventOrderBy') { current.props.orderBy=['start','title','updatedAt'].includes(control.value)?control.value:'start'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.orderBy=current.props.orderBy;} }
                else if (field === 'eventOrder') { current.props.order=control.value==='DESC'?'DESC':'ASC'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.order=current.props.order;} }
                else if (field === 'eventCardGap') { current.props.cardGap=clamp(parseInt(control.value||18,10)||18,0,80); }
                else if (field === 'eventCardPadding') { current.props.cardPadding=clamp(parseInt(control.value||12,10)||12,0,60); }
                else if (field === 'eventImageHeight') { current.props.imageHeight=current.type==='eventdetail'?clamp(parseInt(control.value||360,10)||360,80,900):clamp(parseInt(control.value||180,10)||180,60,600); }
                else if (field === 'eventCardRadius') { current.props.cardRadius=clamp(parseInt(control.value||4,10)||4,0,60); }
                else if (field === 'eventShowImage') { current.props.showImage=!!control.checked; }
                else if (field === 'eventShowDate') { current.props.showDate=!!control.checked; }
                else if (field === 'eventShowLocation') { current.props.showLocation=!!control.checked; }
                else if (field === 'eventShowSummary') { current.props.showSummary=!!control.checked; }
                else if (field === 'eventLinkCards') { current.props.linkCards=!!control.checked; }
                else if (field === 'eventCardBackground') { current.props.cardBackground=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'eventAccentColor') { current.props.accentColor=normalizeColor(control.value||'#c3ae83'); }
                else if (field === 'eventRecordId') { current.props.recordId=String(control.value||''); if(current.props.binding){current.props.binding.recordId=current.props.recordId;} }
                else if (field === 'eventShowDescription') { current.props.showDescription=!!control.checked; }
'''
replace_once(CORE, "                else if (field === 'vehicleLabelWidth') { current.props.labelWidth = clamp(parseInt(control.value || 34,10) || 34,20,60); }\n                else if (field === 'buttonText')", "                else if (field === 'vehicleLabelWidth') { current.props.labelWidth = clamp(parseInt(control.value || 34,10) || 34,20,60); }\n" + EVENT_HANDLERS + "                else if (field === 'buttonText')")

append_once(PREVIEW_CSS, '.h18-vd-event-list-preview', '.h18-vd-event-list-preview{display:grid;width:100%;box-sizing:border-box}.h18-vd-event-card-preview{display:flex;flex-direction:column;gap:6px;min-width:0;border:1px solid #dcdcde;box-sizing:border-box;overflow:hidden}.h18-vd-event-card-preview img,.h18-vd-event-detail-preview>img{display:block;width:100%;object-fit:cover;max-width:none}.h18-vd-event-card-preview p,.h18-vd-event-detail-preview p,.h18-vd-event-detail-preview h3{margin:0}.h18-vd-event-detail-preview{display:flex;flex-direction:column;gap:10px;width:100%;box-sizing:border-box}.h18-clean-node-preview--eventlist,.h18-clean-node-preview--eventdetail{overflow:auto}')

# Frontend Event list/detail.
replace_once(RENDERER, "        echo '.h18-vd-live-shell,.h18-vd-live-shell-part", "        echo '.h18-clean-front-event-list{display:grid;width:100%;box-sizing:border-box}.h18-clean-front-event-card{display:flex;flex-direction:column;gap:8px;min-width:0;box-sizing:border-box;text-decoration:none;color:inherit;overflow:hidden}.h18-clean-front-event-card img{display:block;width:100%;max-width:none;object-fit:cover}.h18-clean-front-event-card h3,.h18-clean-front-event-card p{margin:0}.h18-clean-front-event-meta{display:flex;flex-wrap:wrap;gap:6px 14px}.h18-clean-front-event-detail{box-sizing:border-box}.h18-clean-front-event-hero{display:block;width:100%;max-width:none;object-fit:cover;margin-bottom:14px}.h18-clean-front-event-description{margin-top:16px}@media(max-width:782px){.h18-clean-front-event-list{grid-template-columns:1fr!important}}';\n        echo '.h18-vd-live-shell,.h18-vd-live-shell-part")
EVENT_RENDERER = r'''        if ($type === 'eventlist') {
            $binding = isset($props['binding']) && is_array($props['binding']) ? $props['binding'] : []; $query = isset($binding['query']) && is_array($binding['query']) ? $binding['query'] : []; $query['status']='publish'; $query['limit']=max(1,min(100,(int)($props['limit']??($query['limit']??50)))); $query['orderBy']=in_array((string)($props['orderBy']??($query['orderBy']??'start')),['start','title','updatedAt'],true)?(string)($props['orderBy']??($query['orderBy']??'start')):'start'; $query['order']=strtoupper((string)($props['order']??($query['order']??'ASC')))==='DESC'?'DESC':'ASC';
            $records=ModuleStore::listRecords('events',$query); $dateFilter=in_array((string)($props['dateFilter']??'upcoming'),['all','upcoming','past'],true)?(string)($props['dateFilter']??'upcoming'):'upcoming'; $now=current_time('Y-m-d\\TH:i'); $columns=max(1,min(4,(int)($props['columns']??3))); $gap=max(0,min(80,(int)($props['cardGap']??18))); $padding=max(0,min(60,(int)($props['cardPadding']??12))); $imageHeight=max(60,min(600,(int)($props['imageHeight']??180))); $cardBg=sanitize_hex_color((string)($props['cardBackground']??'#ffffff'))?:'#ffffff'; $textColor=sanitize_hex_color((string)($props['textColor']??'#30382a'))?:'#30382a'; $accent=sanitize_hex_color((string)($props['accentColor']??'#c3ae83'))?:'#c3ae83'; $cardRadius=max(0,min(60,(int)($props['cardRadius']??4))); $detailPageId=absint($props['detailPageId']??0); $detailBase=$detailPageId>0?get_permalink($detailPageId):false; $cards='';
            foreach($records as $item){$record=isset($item['record'])&&is_array($item['record'])?$item['record']:[]; if((string)($record['status']??'')!=='publish'){continue;} $fields=isset($record['fields'])&&is_array($record['fields'])?$record['fields']:[]; $start=(string)($fields['start']??'');$end=(string)($fields['end']??'');$edge=$end!==''?$end:$start;$past=$edge!==''&&strcmp(substr($edge,0,16),$now)<0;if($dateFilter==='upcoming'&&$past){continue;}if($dateFilter==='past'&&!$past){continue;} $recordId=(string)($record['id']??'');$href=is_string($detailBase)&&$detailBase!==''&&!empty($props['linkCards'])?add_query_arg('h18_event',rawurlencode($recordId),$detailBase):'';$tag=$href!==''?'a':'article';$hrefAttr=$href!==''?' href="'.esc_url($href).'"':'';$image='';$featuredId=absint($record['featuredMediaId']??0);if(!empty($props['showImage'])&&$featuredId>0){$url=wp_get_attachment_image_url($featuredId,'large');if(is_string($url)&&$url!==''){$image='<img src="'.esc_url($url).'" alt="'.esc_attr((string)($record['title']??'')).'" style="height:'.esc_attr((string)$imageHeight).'px">';}} $meta='';if(!empty($props['showDate'])){$dateLabel=self::eventDateLabel($start,$end);if($dateLabel!==''){$meta.='<span style="color:'.esc_attr($accent).'">'.esc_html($dateLabel).'</span>';}}if(!empty($props['showLocation'])&&trim((string)($fields['location']??''))!==''){$meta.='<span>'.esc_html((string)$fields['location']).'</span>';}$meta=$meta!==''?'<div class="h18-clean-front-event-meta">'.$meta.'</div>':'';$summary=!empty($props['showSummary'])&&trim((string)($record['summary']??''))!==''?'<p>'.esc_html((string)$record['summary']).'</p>':'';$cardStyle='background:'.$cardBg.';color:'.$textColor.';padding:'.$padding.'px;border-radius:'.$cardRadius.'px;';$cards.='<'.$tag.' class="h18-clean-front-event-card"'.$hrefAttr.' style="'.esc_attr($cardStyle).'">'.$image.'<h3>'.esc_html((string)($record['title']??'Event')).'</h3>'.$meta.$summary.'</'.$tag.'>';}
            if($cards===''&&self::$forceStandaloneCss){$cards='<p>Ingen publicerede events matcher visningen.</p>';}$listStyle=$style.$borderStyle.$spacingStyle.'grid-template-columns:repeat('.$columns.',minmax(0,1fr));gap:'.$gap.'px;';return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-list" style="'.esc_attr($listStyle).'">'.$cards.'</div>';
        }
        if ($type === 'eventdetail') {
            $recordId=strtolower(trim((string)($props['recordId']??'')));if($recordId===''){$recordId=strtolower(trim(sanitize_text_field((string)wp_unslash($_GET['h18_event']??''))));}if($recordId!==''&&!preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/',$recordId)){$recordId='';}if($recordId===''){$message=self::$forceStandaloneCss?'Vælg et event i Inspector eller brug ?h18_event=record-id.':'Vælg et event fra oversigten.';return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-detail" style="'.esc_attr($style.$borderStyle.$spacingStyle).'"><p>'.esc_html($message).'</p></div>';}
            $found=ModuleStore::findByRecordId('events',$recordId);$record=is_array($found)&&isset($found['record'])&&is_array($found['record'])?$found['record']:null;$allowDraft=self::$forceStandaloneCss&&current_user_can('edit_pages');if($record===null||((string)($record['status']??'draft')!=='publish'&&!$allowDraft)){return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-detail" style="'.esc_attr($style.$borderStyle.$spacingStyle).'"><p>Eventet findes ikke eller er ikke publiceret.</p></div>';}$fields=isset($record['fields'])&&is_array($record['fields'])?$record['fields']:[];$background=sanitize_hex_color((string)($props['background']??'#ffffff'))?:'#ffffff';$textColor=sanitize_hex_color((string)($props['textColor']??'#30382a'))?:'#30382a';$accent=sanitize_hex_color((string)($props['accentColor']??'#c3ae83'))?:'#c3ae83';$padding=max(0,min(80,(int)($props['padding']??16)));$imageHeight=max(80,min(900,(int)($props['imageHeight']??360)));$featuredId=absint($record['featuredMediaId']??0);$hero='';if(!empty($props['showImage'])&&$featuredId>0){$url=wp_get_attachment_image_url($featuredId,'large');if(is_string($url)&&$url!==''){$hero='<img class="h18-clean-front-event-hero" src="'.esc_url($url).'" alt="'.esc_attr((string)($record['title']??'')).'" style="height:'.esc_attr((string)$imageHeight).'px">';}}$meta='';if(!empty($props['showDate'])){$dateLabel=self::eventDateLabel((string)($fields['start']??''),(string)($fields['end']??''));if($dateLabel!==''){$meta.='<span style="color:'.esc_attr($accent).'">'.esc_html($dateLabel).'</span>';}}if(!empty($props['showLocation'])&&trim((string)($fields['location']??''))!==''){$meta.='<span>'.esc_html((string)$fields['location']).'</span>';}$meta=$meta!==''?'<div class="h18-clean-front-event-meta">'.$meta.'</div>':'';$summary=!empty($props['showSummary'])&&trim((string)($record['summary']??''))!==''?'<p><strong>'.esc_html((string)$record['summary']).'</strong></p>':'';$description=!empty($props['showDescription'])&&trim((string)($fields['description']??''))!==''?'<div class="h18-clean-front-event-description">'.wp_kses_post((string)$fields['description']).'</div>':'';$detailStyle=$style.$borderStyle.$spacingStyle.$radiusStyle.'background:'.$background.';color:'.$textColor.';padding:'.$padding.'px;';return '<article id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-detail" style="'.esc_attr($detailStyle).'">'.$hero.'<h2>'.esc_html((string)($record['title']??'Event')).'</h2>'.$meta.$summary.$description.'</article>';
        }
'''
replace_once(RENDERER, "        if ($type === 'image') {", EVENT_RENDERER + "\n        if ($type === 'image') {")
EVENT_HELPER = r'''    private static function eventDateLabel(string $start, string $end = ''): string
    {
        $render = static function (string $value): string { $value=trim($value); if(preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/',$value)!==1){return '';} $date=\DateTimeImmutable::createFromFormat('!Y-m-d\\TH:i',substr($value,0,16)); if(!$date instanceof \DateTimeImmutable){return str_replace('T',' ',substr($value,0,16));} return $date->format((string)get_option('date_format','j. F Y').' '.(string)get_option('time_format','H:i')); };
        $startLabel=$render($start);$endLabel=$render($end);if($startLabel===''){return $endLabel;}return $endLabel!==''?($startLabel.' – '.$endLabel):$startLabel;
    }

'''
replace_once(RENDERER, "    /** @param array<string,mixed> $props */\n    private static function tableCellBorderCss", EVENT_HELPER + "    /** @param array<string,mixed> $props */\n    private static function tableCellBorderCss")

# Manuals, release traceability, backlog.
history_path='clean/hangar18-manager/release-history.json';history=json.loads(read(history_path));versions=history.get('versions',[])
if not any(isinstance(row,dict) and row.get('version')=='0.1.71' for row in versions):
    versions.insert(0,{'version':'0.1.71','date':'2026-08-31','items':['VD-EVENT-MODULE-001: Events er nu et fuldt modul oven på den fælles ModuleStore.','Manager har CRUD, publiceringsstatus, start/slut, sted, beskrivelse og primært billede.','Designer har canonical Eventliste og Eventdetalje med kommende/afholdte/alle publicerede visninger.','Eventkort kan linke til én genbrugelig detaljeside via ?h18_event=<record-id>.','Designmanual, teknisk manual, brugermanual og backlog er synkroniseret til v0.1.71.']});history['versions']=versions;write(history_path,json.dumps(history,ensure_ascii=False,indent=2)+'\n')
append_once('CLEAN-DESIGN-MANUAL.md','## Eventmodul – designprincip','''## Eventmodul – designprincip

**VD-EVENT-MODULE-001** gør Events til dynamiske data i den fælles ModuleStore. Eventliste og Eventdetalje gemmer kun binding/design, ikke kopier af eventdata. Eventliste kan vise kommende, afholdte eller alle publicerede events, så historiske events bevares.''')
append_once('CLEAN-USER-MANUAL.md','## Sådan bruger du Eventmodulet','''## Sådan bruger du Eventmodulet

1. Åbn **Manager → Events** og opret titel, start/slut, sted, beskrivelse og billede.
2. Kun **Publiceret** kan vises offentligt; Kladde og Arkiveret er skjult.
3. Tilføj **Eventliste** i Designer og vælg Kommende, Afholdte eller Alle publicerede samt en detaljeside.
4. Indsæt **Eventdetalje** på detaljesiden og behold *Fra URL* for routing via `?h18_event=<record-id>`.
5. Arkivér frem for at slette, når historikken skal bevares.''')
append_once('CLEAN-TECHNICAL-MANUAL.md','## VD-EVENT-MODULE-001','''## VD-EVENT-MODULE-001

Events bruger `ModuleRegistry`, `ModuleRecord` og `ModuleStore`; der findes ingen parallel event-datasilo. `EventAdminController` skriver start/slut/sted/beskrivelse i canonical `fields` og billede som attachment-ID. `ModuleStore::listRecords()` understøtter `orderBy=start`. Designer-elementerne `eventlist` og `eventdetail` binder til `module=events`, og frontend tvinger publiceret status samt bruger stabilt record-ID via `h18_event`.''')
write('clean-release-notes.html','''<h2>0.1.71 – Events</h2>\n<ul>\n<li><strong>VD-EVENT-MODULE-001:</strong> Events har nu Manager-CRUD på den fælles ModuleStore.</li>\n<li>Start/slut, sted, beskrivelser, status og primært billede understøttes.</li>\n<li>Designer har Eventliste og Eventdetalje med genbrugelig detailrouting via <code>?h18_event=&lt;record-id&gt;</code>.</li>\n<li>Eventliste kan vise kommende, afholdte eller alle publicerede events uden at slette historiske records.</li>\n<li>Næste modulrelease er v0.1.72 – Billedgalleri.</li>\n</ul>\n''')
backlog=read('docs/clean-backlog-v0100.md').replace('**Aktuel release:** v0.1.70','**Aktuel release:** v0.1.71').replace('## Aktuel milepælsstatus · v0.1.70','## Aktuel milepælsstatus · v0.1.71').replace('- **VD-VEHICLE-MODULE-001 — IMPLEMENTERET I v0.1.70:** Køretøjer har Manager-CRUD, fleksible tekniske felter, billeder, sortering og Designer-list/detail-binding.','- **VD-VEHICLE-MODULE-001 — IMPLEMENTERET I v0.1.70:** Køretøjer har Manager-CRUD, fleksible tekniske felter, billeder, sortering og Designer-list/detail-binding.\n- **VD-EVENT-MODULE-001 — IMPLEMENTERET I v0.1.71:** Events har Manager-CRUD, dato/tid, sted, billede, kommende/afholdte regler og Designer list/detail-binding.').replace('3. **v0.1.71 – Events — NÆSTE:**','3. **v0.1.71 – Events — FÆRDIG:**').replace('4. **v0.1.72 – Billedgalleri — PLANLAGT:**','4. **v0.1.72 – Billedgalleri — NÆSTE:**').replace('### VD-EVENT-MODULE-001 — NÆSTE','### VD-EVENT-MODULE-001 — FÆRDIG I v0.1.71').replace('### VD-GALLERY-MODULE-001 — PLANLAGT','### VD-GALLERY-MODULE-001 — NÆSTE')
append='''## v0.1.71 Eventmodul – QA-gate

1. Opret Kladde med start/slut, sted, beskrivelse og billede; reload og verificér stabilt record-ID.
2. Publicér events før og efter aktuel dato og test Kommende, Afholdte og Alle publicerede.
3. Test startdato-sortering, Eventliste-design og genbrugelig Eventdetalje via `?h18_event=<record-id>`.
4. Kladde/Arkiveret må ikke kunne vises offentligt via direkte detail-URL.
5. Gem/reload/Undo/Redo begge eventelementer; historiske events må ikke slettes automatisk.
'''
if '## v0.1.71 Eventmodul – QA-gate' not in backlog: backlog=backlog.replace('## Global release-gate',append+'\n## Global release-gate')
write('docs/clean-backlog-v0100.md',backlog)
write('docs/v0171-status.md','''# Visual Designer Manager v0.1.71\n\nStatus: release candidate\n\n- VD-EVENT-MODULE-001 implementeret.\n- Manager CRUD + start/slut + sted + beskrivelse + primært billede.\n- Canonical eventlist / eventdetail elementer med ModuleBinding.\n- Kommende/afholdte/alle publicerede datoregler uden automatisk sletning.\n- Detailrouting via h18_event query parameter.\n- v0.1.70 Køretøjsmodul forbliver regression-gate.\n''')

print('Applied Visual Designer Manager v0.1.71 Event module candidate.')
