<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Modules\ModuleStore;

final class CollectionPageRenderer
{
    /** @return string|null */
    public static function render(int $postId): ?string
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        if (!in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true)) { return null; }
        $title = trim((string) get_the_title($postId));
        if ($title === '') { $title = $slug === 'events' ? 'Events' : ($slug === 'billedgalleri' ? 'Billedgalleri' : 'Køretøjer og materiel'); }
        if ($slug === 'events') {
            $detail = self::requestRecordId('h18_event');
            $body = $detail !== '' ? self::eventDetail($postId, $detail, $title) : self::events($postId, $title);
        } elseif ($slug === 'billedgalleri') {
            $detail = self::requestRecordId('h18_gallery');
            $body = $detail !== '' ? self::galleryDetail($postId, $detail, $title) : self::galleries($postId, $title);
        } else {
            $detail = self::requestRecordId('h18_vehicle');
            $body = $detail !== '' ? self::vehicleDetail($postId, $detail, $title) : self::vehicles($postId, $title);
        }
        return self::style() . $body;
    }

    public static function supports(int $postId): bool
    {
        return in_array(sanitize_title((string) get_post_field('post_name', $postId)), ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true);
    }

    private static function events(int $postId, string $title): string
    {
        $items = ModuleStore::listRecords('events', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'start', 'order' => 'ASC']);
        $records = self::records($items);
        $query = self::query();
        if ($query !== '') { $records = self::searchTitle($records, $query); }
        $sort = self::sortMode('events');
        self::sortEvents($records, $sort);
        $upcoming = []; $past = []; $now = current_time('timestamp');
        foreach ($records as $record) {
            $edge = self::eventArchiveEdge($record);
            if ($edge > 0 && $edge < $now) { $past[] = $record; } else { $upcoming[] = $record; }
        }
        $html = self::openPage('events', $title) . self::controls('events', $query, $sort);
        $html .= '<section class="h18-module-section"><h2>Kommende arrangementer</h2>' . self::eventGrid($postId, $upcoming, false, 'Ingen kommende arrangementer matcher søgningen.') . '</section>';
        $html .= '<section class="h18-module-section"><h2>Tidligere arrangementer</h2>' . self::eventGrid($postId, $past, true, 'Ingen tidligere arrangementer matcher søgningen.') . '</section>';
        return $html . '</main>';
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function eventGrid(int $postId, array $records, bool $past, string $empty): string
    {
        if (!$records) { return '<p class="h18-module-empty">' . esc_html($empty) . '</p>'; }
        $html = '<div class="h18-module-card-grid h18-module-event-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_event', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-event-card">' . self::image($record, 'h18-module-card-image', 480, 285);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Event')) . '</h3>';
            $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? ''));
            $location = trim((string) ($fields['location'] ?? ''));
            if ($meta !== '' || $location !== '') { $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>'; }
            $summary = trim((string) ($record['summary'] ?? '')); if ($summary !== '') { $html .= '<p>' . esc_html($summary) . '</p>'; }
            $html .= '<div class="h18-module-card-actions"><a class="h18-module-more" href="' . esc_url($url) . '">Læs mere →</a>';
            if ($past) { $html .= self::eventGalleryLink($fields); }
            $html .= '</div></div></article>';
        }
        return $html . '</div>';
    }

    private static function galleries(int $postId, string $title): string
    {
        $records = self::records(ModuleStore::listRecords('galleries', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'title', 'order' => 'ASC']));
        $query = self::query(); if ($query !== '') { $records = self::searchTitle($records, $query); }
        $sort = self::sortMode('galleries'); self::sortByTitle($records, $sort === 'name-desc');
        $html = self::openPage('galleries', $title) . self::controls('galleries', $query, $sort) . '<section class="h18-module-section"><h2>Køretøjer</h2>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen album matcher søgningen.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-gallery-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
            $cover = absint($record['featuredMediaId'] ?? 0); if ($cover <= 0 && $imageIds) { $cover = (int) $imageIds[0]; }
            $url = add_query_arg('h18_gallery', rawurlencode((string) ($record['id'] ?? '')), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-gallery-card">' . self::imageId($cover, (string) ($record['title'] ?? ''), 'h18-module-card-image', 480, 285);
            $html .= '<div class="h18-module-card-body"><h3><a href="' . esc_url($url) . '">' . esc_html((string) ($record['title'] ?? 'Album')) . '</a></h3>';
            $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-description">' . wp_kses_post($description) . '</div>'; }
            $count = count($imageIds); $html .= '<p class="h18-module-count"><strong>' . esc_html((string) $count) . ' ' . ($count === 1 ? 'billede' : 'billeder') . '</strong></p></div></article>';
        }
        return $html . '</div></section></main>';
    }

    private static function vehicles(int $postId, string $title): string
    {
        $records = self::records(ModuleStore::listRecords('vehicles', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'title', 'order' => 'ASC']));
        $query = self::query(); if ($query !== '') { $records = self::searchTitle($records, $query); }
        $sort = self::sortMode('vehicles'); self::sortByTitle($records, $sort === 'name-desc');
        $html = self::openPage('vehicles', $title) . self::controls('vehicles', $query, $sort);
        $html .= '<section class="h18-module-section"><h2>Historisk materiel</h2><p class="h18-module-intro">Her finder du foreningens dokumenterede køretøjer og øvrige militærhistoriske materiel.</p>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen køretøjer matcher søgningen.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-vehicle-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $url = add_query_arg('h18_vehicle', rawurlencode((string) ($record['id'] ?? '')), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-vehicle-card">' . self::image($record, 'h18-module-card-image', 480, 285);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Køretøj')) . '</h3>';
            $rows = []; $category = trim((string) ($fields['category'] ?? '')); if ($category !== '') { $rows[] = ['Type', $category]; }
            foreach (isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [] as $attribute) {
                if (!is_array($attribute) || empty($attribute['enabled'])) { continue; }
                $value = self::attributeValue($attribute['value'] ?? ''); if ($value === '') { continue; }
                $label = trim((string) ($attribute['label'] ?? $attribute['key'] ?? '')); if ($label === '' || (strcasecmp($label, 'Type') === 0 && $category !== '')) { continue; }
                $rows[] = [$label, $value];
            }
            if ($rows) { $html .= '<table class="h18-module-spec-table"><tbody>'; foreach (array_slice($rows, 0, 10) as $row) { $html .= '<tr><th>' . esc_html($row[0]) . '</th><td>' . esc_html($row[1]) . '</td></tr>'; } $html .= '</tbody></table>'; }
            $html .= '<a class="h18-module-more" href="' . esc_url($url) . '">Se køretøjet →</a></div></article>';
        }
        return $html . '</div></section></main>';
    }

    private static function eventDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('events', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $html = self::openPage('events detail', (string) ($record['title'] ?? $pageTitle));
        $html .= '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Events</a></p>' . self::image($record, 'h18-module-detail-image', 1200, 620);
        $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? '')); $location = trim((string) ($fields['location'] ?? ''));
        if ($meta !== '' || $location !== '') { $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>'; }
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        $html .= self::eventGalleryLink($fields);
        return $html . '</main>';
    }

    private static function galleryDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('galleries', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : []; $ids = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        $html = self::openPage('galleries detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Billedgalleri</a></p>';
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        $html .= '<div class="h18-module-image-grid">'; foreach ($ids as $imageId) { $html .= self::imageId($imageId, (string) ($record['title'] ?? ''), 'h18-module-gallery-image', 420, 280); }
        return $html . '</div></main>';
    }

    private static function vehicleDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('vehicles', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $html = self::openPage('vehicles detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Køretøjer</a></p>' . self::image($record, 'h18-module-detail-image', 1200, 620);
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        return $html . '</main>';
    }

    /** @param array<string,mixed> $fields */
    private static function eventGalleryLink(array $fields): string
    {
        $galleryId = strtolower(trim((string) ($fields['galleryRecordId'] ?? '')));
        if ($galleryId === '') { return ''; }
        $found = ModuleStore::findByRecordId('galleries', $galleryId);
        $gallery = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($gallery === null || (string) ($gallery['status'] ?? '') !== 'publish') { return ''; }
        $page = get_page_by_path('billedgalleri', OBJECT, 'page'); if (!$page instanceof \WP_Post) { return ''; }
        $url = add_query_arg('h18_gallery', rawurlencode($galleryId), get_permalink((int) $page->ID));
        return '<a class="h18-module-more h18-module-gallery-link" href="' . esc_url($url) . '">Se billeder →</a>';
    }

    /** @param array<int,array{postId:int,record:array<string,mixed>}> $items @return array<int,array<string,mixed>> */
    private static function records(array $items): array
    {
        $out = []; foreach ($items as $item) { $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : []; if ((string) ($record['status'] ?? '') === 'publish') { $out[] = $record; } } return $out;
    }

    private static function query(): string { return trim(sanitize_text_field((string) wp_unslash($_GET['h18_q'] ?? ''))); }

    private static function sortMode(string $module): string
    {
        $raw = sanitize_key((string) wp_unslash($_GET['h18_sort'] ?? ''));
        if ($module === 'events') { return in_array($raw, ['date', 'name', 'name-desc'], true) ? $raw : 'date'; }
        return in_array($raw, ['name', 'name-desc'], true) ? $raw : 'name';
    }

    /** @param array<int,array<string,mixed>> $records @return array<int,array<string,mixed>> */
    private static function searchTitle(array $records, string $query): array
    {
        if ($query === '') { return $records; }
        return array_values(array_filter($records, static function (array $record) use ($query): bool {
            $title = (string) ($record['title'] ?? '');
            return function_exists('mb_stripos') ? mb_stripos($title, $query, 0, 'UTF-8') !== false : stripos($title, $query) !== false;
        }));
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function sortEvents(array &$records, string $sort): void
    {
        usort($records, static function (array $a, array $b) use ($sort): int {
            if ($sort === 'name' || $sort === 'name-desc') {
                $cmp = strnatcasecmp((string) ($a['title'] ?? ''), (string) ($b['title'] ?? ''));
                return $sort === 'name-desc' ? -$cmp : $cmp;
            }
            $left = self::eventStart($a); $right = self::eventStart($b);
            if ($left === $right) { return strnatcasecmp((string) ($a['title'] ?? ''), (string) ($b['title'] ?? '')); }
            if ($left <= 0) { return 1; } if ($right <= 0) { return -1; } return $left <=> $right;
        });
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function sortByTitle(array &$records, bool $desc): void
    {
        usort($records, static function (array $a, array $b) use ($desc): int { $cmp = strnatcasecmp((string) ($a['title'] ?? ''), (string) ($b['title'] ?? '')); return $desc ? -$cmp : $cmp; });
    }

    private static function controls(string $module, string $query, string $sort): string
    {
        $placeholder = $module === 'events' ? 'Søg i events' : ($module === 'vehicles' ? 'Søg i køretøjer' : 'Søg i billedgalleri');
        $html = '<form class="h18-module-controls" method="get"><label class="h18-module-search"><span class="screen-reader-text">' . esc_html($placeholder) . '</span><input type="search" name="h18_q" value="' . esc_attr($query) . '" placeholder="' . esc_attr($placeholder) . '"></label>';
        $html .= '<label><span>Sortér</span><select name="h18_sort">';
        if ($module === 'events') { $html .= '<option value="date"' . selected($sort, 'date', false) . '>Dato – tidligste først</option>'; }
        $html .= '<option value="name"' . selected($sort, 'name', false) . '>Navn A–Å</option><option value="name-desc"' . selected($sort, 'name-desc', false) . '>Navn Å–A</option></select></label>';
        $html .= '<button type="submit">Søg / sortér</button>' . ($query !== '' || ($module === 'events' ? $sort !== 'date' : $sort !== 'name') ? '<a class="h18-module-reset" href="' . esc_url(remove_query_arg(['h18_q', 'h18_sort'])) . '">Nulstil</a>' : '') . '</form>';
        return $html;
    }

    /** @param array<string,mixed> $record */
    private static function eventArchiveEdge(array $record): int
    {
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $end = trim((string) ($fields['end'] ?? '')); if ($end !== '') { return self::dateTimeTimestamp($end); }
        $start = trim((string) ($fields['start'] ?? '')); if ($start === '') { return 0; }
        $date = substr($start, 0, 10); return self::dateTimeTimestamp($date . 'T23:59:59');
    }

    /** @param array<string,mixed> $record */
    private static function eventStart(array $record): int
    {
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : []; return self::dateTimeTimestamp((string) ($fields['start'] ?? ''));
    }

    private static function dateTimeTimestamp(string $value): int
    {
        $value = trim($value); if ($value === '') { return 0; }
        $tz = wp_timezone(); $dt = \DateTimeImmutable::createFromFormat('!Y-m-d\\TH:i:s', $value, $tz);
        if (!$dt) { $dt = \DateTimeImmutable::createFromFormat('!Y-m-d\\TH:i', $value, $tz); }
        return $dt ? $dt->getTimestamp() : 0;
    }

    private static function eventDateLabel(string $start, string $end): string
    {
        $startTs = self::dateTimeTimestamp($start); $endTs = self::dateTimeTimestamp($end); if ($startTs <= 0) { return ''; }
        $startLabel = wp_date('j. F Y · H:i', $startTs); if ($endTs <= 0) { return $startLabel; }
        if (wp_date('Y-m-d', $startTs) === wp_date('Y-m-d', $endTs)) { return $startLabel . '–' . wp_date('H:i', $endTs); }
        return $startLabel . ' – ' . wp_date('j. F Y · H:i', $endTs);
    }

    private static function requestRecordId(string $key): string
    {
        $value = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET[$key] ?? '')))); return preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $value) ? $value : '';
    }

    /** @param array<string,mixed> $record */
    private static function image(array $record, string $class, int $width, int $height): string { return self::imageId(absint($record['featuredMediaId'] ?? 0), (string) ($record['title'] ?? ''), $class, $width, $height); }

    private static function imageId(int $id, string $alt, string $class, int $width, int $height): string
    {
        if ($id <= 0) { return ''; }
        $url = wp_get_attachment_image_url($id, 'large'); if (!is_string($url) || $url === '') { return ''; }
        return '<img class="' . esc_attr($class) . '" src="' . esc_url($url) . '" alt="' . esc_attr($alt) . '" loading="lazy" width="' . esc_attr((string) $width) . '" height="' . esc_attr((string) $height) . '">';
    }

    private static function attributeValue($value): string
    {
        if (is_bool($value)) { return $value ? 'Ja' : 'Nej'; } if (is_scalar($value)) { return trim((string) $value); } return '';
    }

    private static function notFound(int $postId, string $pageTitle): string { return self::openPage('detail', $pageTitle) . '<p>Indholdet findes ikke eller er ikke publiceret.</p><p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage</a></p></main>'; }
    private static function openPage(string $class, string $title): string { return '<main class="h18-module-page h18-module-page--' . esc_attr(sanitize_html_class($class)) . '"><h1>' . esc_html($title) . '</h1>'; }

    private static function style(): string
    {
        return '<style id="h18-module-page-style-v0175">'
            . '.h18-module-page{width:90%;max-width:1440px;margin:0 auto;padding:34px 0 54px;color:#30382a;box-sizing:border-box}.h18-module-page h1{margin:0 0 28px;font-size:clamp(30px,3vw,44px);line-height:1.08}.h18-module-section{margin:0 0 42px}.h18-module-section h2{margin:0 0 18px;font-size:clamp(23px,2vw,31px)}'
            . '.h18-module-intro{margin:-7px 0 20px;max-width:850px}.h18-module-card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:26px;align-items:start}.h18-module-card{background:#f4f1e8;border-radius:7px;overflow:hidden;box-shadow:0 1px 0 rgba(0,0,0,.06);min-width:0}.h18-module-card-image{display:block;width:100%;height:220px;object-fit:cover}.h18-module-card-body{padding:20px}.h18-module-card h3{font-size:22px;line-height:1.15;margin:0 0 10px}.h18-module-card h3 a{color:inherit;text-decoration:none}.h18-module-card p{margin:8px 0}.h18-module-meta{font-size:14px}.h18-module-more{font-weight:700;color:#536243;text-decoration:none}.h18-module-card-actions{display:flex;flex-wrap:wrap;gap:12px 20px;margin-top:14px}.h18-module-description>*:first-child{margin-top:0}.h18-module-description>*:last-child{margin-bottom:0}'
            . '.h18-module-spec-table{width:100%;border-collapse:collapse;margin:14px 0}.h18-module-spec-table th,.h18-module-spec-table td{padding:7px 8px;border-bottom:1px solid rgba(48,56,42,.16);text-align:left;vertical-align:top}.h18-module-spec-table th{width:45%;font-weight:700}.h18-module-count{font-size:14px}.h18-module-detail-image{display:block;width:min(100%,1100px);max-height:620px;object-fit:cover;border-radius:7px;margin:15px 0 20px}.h18-module-detail-text{max-width:950px;margin:18px 0}.h18-module-back{font-weight:700;text-decoration:none;color:#536243}.h18-module-image-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:24px}.h18-module-gallery-image{display:block;width:100%;height:260px;object-fit:cover;border-radius:5px}'
            . '.h18-module-controls{display:flex;align-items:end;gap:12px;flex-wrap:wrap;margin:-8px 0 30px;padding:14px 16px;background:#f4f1e8;border-radius:7px}.h18-module-controls label{display:flex;flex-direction:column;gap:5px;font-weight:700}.h18-module-search{flex:1 1 300px}.h18-module-controls input,.h18-module-controls select{min-height:40px;border:1px solid #aaa99f;border-radius:4px;background:#fff;padding:7px 10px;font:inherit}.h18-module-controls button{min-height:40px;border:0;border-radius:4px;padding:8px 16px;background:#30382a;color:#fff;font-weight:700;cursor:pointer}.h18-module-reset{padding:9px 4px;font-weight:700;color:#536243}.h18-module-empty{padding:18px;background:#f4f1e8;border-radius:6px}'
            . '@media(max-width:980px){.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.h18-module-page{width:92%;padding-top:24px}.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:1fr}.h18-module-card-image{height:auto;aspect-ratio:16/10}.h18-module-controls{align-items:stretch}.h18-module-controls label,.h18-module-controls button{width:100%}.h18-module-gallery-image{height:auto;aspect-ratio:4/3}}'
            . '</style>';
    }

    private function __construct() {}
}
