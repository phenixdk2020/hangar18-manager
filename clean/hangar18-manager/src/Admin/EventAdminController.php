<?php

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
