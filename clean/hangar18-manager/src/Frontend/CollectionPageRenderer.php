<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Modules\ModuleStore;

/**
 * v0.1.74 collection-page cutover.
 *
 * The three historical Hangar18 collection pages are data modules, not fixed
 * 8px Designer canvases. Their main content therefore flows naturally with
 * record count while Header/Footer remain owned by ThemeShell.
 */
final class CollectionPageRenderer
{
    /** @return string|null */
    public static function render(int $postId): ?string
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        if (!in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true)) {
            return null;
        }

        $title = trim((string) get_the_title($postId));
        if ($title === '') {
            $title = $slug === 'events' ? 'Events' : ($slug === 'billedgalleri' ? 'Billedgalleri' : 'Køretøjer og materiel');
        }

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
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        return in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true);
    }

    private static function events(int $postId, string $title): string
    {
        $records = ModuleStore::listRecords('events', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'start', 'order' => 'ASC']);
        $upcoming = [];
        $past = [];
        $now = current_time('timestamp');
        foreach ($records as $item) {
            $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
            if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $start = self::dateTimeTimestamp((string) ($fields['start'] ?? ''));
            $end = self::dateTimeTimestamp((string) ($fields['end'] ?? ''));
            $edge = $end > 0 ? $end : $start;
            if ($edge > 0 && $edge < $now) { $past[] = $record; } else { $upcoming[] = $record; }
        }
        usort($upcoming, static fn(array $a, array $b): int => self::eventStart($a) <=> self::eventStart($b));
        usort($past, static fn(array $a, array $b): int => self::eventStart($b) <=> self::eventStart($a));

        $html = self::openPage('events', $title);
        $html .= '<section class="h18-module-section"><h2>Kommende arrangementer</h2>' . self::eventGrid($postId, $upcoming, 'Ingen kommende arrangementer.') . '</section>';
        $html .= '<section class="h18-module-section"><h2>Tidligere arrangementer</h2>' . self::eventGrid($postId, $past, 'Ingen tidligere arrangementer.') . '</section>';
        return $html . '</main>';
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function eventGrid(int $postId, array $records, string $empty): string
    {
        if (!$records) { return '<p class="h18-module-empty">' . esc_html($empty) . '</p>'; }
        $html = '<div class="h18-module-card-grid h18-module-event-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_event', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-event-card">' . self::image($record, 'h18-module-card-image', 220, 140);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Event')) . '</h3>';
            $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? ''));
            $location = trim((string) ($fields['location'] ?? ''));
            if ($meta !== '' || $location !== '') {
                $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>';
            }
            $summary = trim((string) ($record['summary'] ?? ''));
            if ($summary !== '') { $html .= '<p>' . esc_html($summary) . '</p>'; }
            $html .= '<a class="h18-module-more" href="' . esc_url($url) . '">Læs mere →</a></div></article>';
        }
        return $html . '</div>';
    }

    private static function galleries(int $postId, string $title): string
    {
        $records = ModuleStore::listRecords('galleries', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC']);
        $html = self::openPage('galleries', $title) . '<section class="h18-module-section"><h2>Køretøjer</h2>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen publicerede album endnu.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-gallery-grid">';
        foreach ($records as $item) {
            $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
            if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
            $cover = absint($record['featuredMediaId'] ?? 0); if ($cover <= 0 && $imageIds) { $cover = (int) $imageIds[0]; }
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_gallery', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-gallery-card">' . self::imageId($cover, (string) ($record['title'] ?? ''), 'h18-module-card-image', 245, 150);
            $html .= '<div class="h18-module-card-body"><h3><a href="' . esc_url($url) . '">' . esc_html((string) ($record['title'] ?? 'Album')) . '</a></h3>';
            $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<p>' . wp_kses_post($description) . '</p>'; }
            $count = count($imageIds); $html .= '<p class="h18-module-count"><strong>' . esc_html((string) $count) . ' ' . ($count === 1 ? 'billede' : 'billeder') . '</strong></p></div></article>';
        }
        return $html . '</div></section></main>';
    }

    private static function vehicles(int $postId, string $title): string
    {
        $records = ModuleStore::listRecords('vehicles', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC']);
        $html = self::openPage('vehicles', $title);
        $html .= '<section class="h18-module-section"><h2>Historisk materiel</h2><p class="h18-module-intro">Her finder du foreningens dokumenterede køretøjer og øvrige militærhistoriske materiel.</p>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen publicerede køretøjer endnu.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-vehicle-grid">';
        foreach ($records as $item) {
            $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
            if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_vehicle', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-vehicle-card">' . self::image($record, 'h18-module-card-image', 235, 150);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Køretøj')) . '</h3>';
            $rows = [];
            $category = trim((string) ($fields['category'] ?? '')); if ($category !== '') { $rows[] = ['Type', $category]; }
            foreach (isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [] as $attribute) {
                if (!is_array($attribute) || empty($attribute['enabled'])) { continue; }
                $value = self::attributeValue($attribute['value'] ?? ''); if ($value === '') { continue; }
                $label = trim((string) ($attribute['label'] ?? $attribute['key'] ?? '')); if ($label === '') { continue; }
                if (strcasecmp($label, 'Type') === 0 && $category !== '') { continue; }
                $rows[] = [$label, $value];
            }
            if ($rows) {
                $html .= '<table class="h18-module-spec-table"><tbody>';
                foreach (array_slice($rows, 0, 10) as $row) { $html .= '<tr><th>' . esc_html($row[0]) . '</th><td>' . esc_html($row[1]) . '</td></tr>'; }
                $html .= '</tbody></table>';
            }
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
        $html .= '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Events</a></p>' . self::image($record, 'h18-module-detail-image', 900, 420);
        $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? '')); $location = trim((string) ($fields['location'] ?? ''));
        if ($meta !== '' || $location !== '') { $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>'; }
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        return $html . '</main>';
    }

    private static function galleryDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('galleries', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : []; $ids = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        $html = self::openPage('galleries detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Billedgalleri</a></p>';
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        $html .= '<div class="h18-module-image-grid">'; foreach ($ids as $imageId) { $html .= self::imageId($imageId, (string) ($record['title'] ?? ''), 'h18-module-gallery-image', 320, 220); } return $html . '</div></main>';
    }

    private static function vehicleDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('vehicles', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $html = self::openPage('vehicles detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Køretøjer</a></p>' . self::image($record, 'h18-module-detail-image', 900, 420);
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        return $html . '</main>';
    }

    private static function notFound(int $postId, string $pageTitle): string
    {
        return self::openPage('detail', $pageTitle) . '<p>Indholdet findes ikke eller er ikke publiceret.</p><p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage</a></p></main>';
    }

    private static function openPage(string $class, string $title): string
    {
        return '<main class="h18-module-page h18-module-page-' . esc_attr(sanitize_html_class($class)) . '"><h1>' . esc_html($title) . '</h1>';
    }

    /** @param array<string,mixed> $record */
    private static function image(array $record, string $class, int $width, int $height): string
    {
        return self::imageId(absint($record['featuredMediaId'] ?? 0), (string) ($record['title'] ?? ''), $class, $width, $height);
    }

    private static function imageId(int $id, string $alt, string $class, int $width, int $height): string
    {
        if ($id <= 0) { return ''; }
        $url = wp_get_attachment_image_url($id, 'large'); if (!is_string($url) || $url === '') { return ''; }
        return '<img class="' . esc_attr($class) . '" src="' . esc_url($url) . '" alt="' . esc_attr($alt) . '" width="' . esc_attr((string) $width) . '" height="' . esc_attr((string) $height) . '">';
    }

    private static function requestRecordId(string $key): string
    {
        $value = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET[$key] ?? ''))));
        return preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $value) ? $value : '';
    }

    /** @param array<string,mixed> $record */
    private static function eventStart(array $record): int
    {
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $time = self::dateTimeTimestamp((string) ($fields['start'] ?? '')); return $time > 0 ? $time : PHP_INT_MAX;
    }

    private static function dateTimeTimestamp(string $value): int
    {
        $value = trim($value); if ($value === '') { return 0; }
        try { return (new \DateTimeImmutable($value, wp_timezone()))->getTimestamp(); } catch (\Throwable $error) { return 0; }
    }

    private static function eventDateLabel(string $start, string $end): string
    {
        $startTs = self::dateTimeTimestamp($start); if ($startTs <= 0) { return ''; }
        $label = wp_date('d-m-Y', $startTs, wp_timezone()); $endTs = self::dateTimeTimestamp($end);
        if ($endTs > 0 && wp_date('Y-m-d', $endTs, wp_timezone()) !== wp_date('Y-m-d', $startTs, wp_timezone())) { $label .= ' – ' . wp_date('d-m-Y', $endTs, wp_timezone()); }
        return $label;
    }

    private static function attributeValue($value): string
    {
        if (is_bool($value)) { return $value ? 'Ja' : 'Nej'; }
        if (is_array($value) || is_object($value)) { return ''; }
        return trim(wp_strip_all_tags((string) $value));
    }

    private static function style(): string
    {
        return '<style id="h18-module-page-v0174">'
            . '.h18-module-page{width:90%;max-width:none;margin:0 auto;padding:42px 0 32px;box-sizing:border-box;color:#30382a;font-family:Arial,Helvetica,sans-serif}'
            . '.h18-module-page h1{margin:0 0 28px;font-size:32px;line-height:1.15;color:#30382a}.h18-module-section{margin:0}.h18-module-section+.h18-module-section{margin-top:30px}.h18-module-section h2{margin:0 0 18px;font-size:28px;line-height:1.2;color:#151329}.h18-module-intro{margin:-10px 0 22px;font-size:14px}'
            . '.h18-module-card-grid{display:grid;justify-content:start;align-items:start;gap:12px}.h18-module-event-grid{grid-template-columns:repeat(auto-fill,220px)}.h18-module-gallery-grid{grid-template-columns:repeat(auto-fill,245px)}.h18-module-vehicle-grid{grid-template-columns:repeat(auto-fill,235px)}'
            . '.h18-module-card{overflow:hidden;border:1px solid #d9d6ca;border-radius:5px;background:#f2f0e7;color:#30382a;box-sizing:border-box;box-shadow:0 1px 2px rgba(0,0,0,.04)}.h18-module-card-image{display:block;width:100%;height:150px;max-width:none;object-fit:cover;margin:0}.h18-module-event-card .h18-module-card-image{height:140px}.h18-module-card-body{padding:12px}.h18-module-card h3{margin:0 0 5px;font-size:18px;line-height:1.15;color:#30382a}.h18-module-card h3 a{color:inherit;text-decoration:none}.h18-module-card p{margin:5px 0;font-size:13px;line-height:1.35}.h18-module-meta{font-size:12px!important}.h18-module-count{margin-top:7px!important}.h18-module-more,.h18-module-back{display:inline-block;margin-top:7px;color:#843d19;font-weight:700;font-size:12px;text-decoration:none}.h18-module-more:hover,.h18-module-more:focus,.h18-module-back:hover,.h18-module-back:focus{text-decoration:underline}'
            . '.h18-module-spec-table{width:100%;margin:7px 0 4px;border-collapse:collapse;font-size:12px;line-height:1.35}.h18-module-spec-table th,.h18-module-spec-table td{padding:6px 5px;border-bottom:1px solid #d9d6ca;text-align:left;vertical-align:top}.h18-module-spec-table th{width:42%;background:#e7e1d2;font-weight:700}.h18-module-empty{margin:0 0 20px}.h18-module-detail-image{display:block;width:min(900px,100%);height:auto;max-height:520px;object-fit:cover;margin:16px 0}.h18-module-detail-text{max-width:900px;line-height:1.55}.h18-module-image-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-top:18px}.h18-module-gallery-image{display:block;width:100%;height:220px;object-fit:cover}'
            . '@media(max-width:782px){.h18-module-page{width:calc(100% - 32px);padding:28px 0 24px}.h18-module-page h1{font-size:28px;margin-bottom:22px}.h18-module-section h2{font-size:24px}.h18-module-card-grid{grid-template-columns:1fr!important}.h18-module-card{width:100%}.h18-module-card-image{height:auto;aspect-ratio:16/10}.h18-module-spec-table{font-size:13px}}'
            . '</style>';
    }

    private function __construct() {}
}
