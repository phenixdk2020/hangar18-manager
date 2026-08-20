<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Event;

/**
 * Keeps the public Events overview classified against the current WordPress
 * local date/time without rewriting the Events page on every request.
 *
 * The legacy Events builder still owns card markup and persistence. This
 * runtime only redistributes the already-rendered event cards between
 * "Kommende arrangementer" and "Tidligere arrangementer" at render time.
 */
final class EventArchiveRuntime
{
    private const EVENT_PARENT_SLUG = 'events';
    private const EVENT_MARKER = 'HANGAR18-EVENT-DATA';

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered || !function_exists('add_filter')) {
            return;
        }
        self::$registered = true;

        // WordPress attaches do_blocks() to the_content at priority 9.
        // EVENT-001 must classify the raw managed wp:html register first so
        // its reliable closing block boundary is still present.
        add_filter('the_content', [self::class, 'filterContent'], 8);
    }

    /** @param mixed $content @return mixed */
    public static function filterContent($content)
    {
        if (!is_string($content) || $content === '') {
            return $content;
        }
        if (function_exists('is_admin') && is_admin()) {
            return $content;
        }
        if (!function_exists('is_page') || !is_page(self::EVENT_PARENT_SLUG)) {
            return $content;
        }
        if (
            strpos($content, 'Kommende arrangementer') === false ||
            strpos($content, 'Tidligere arrangementer') === false ||
            strpos($content, 'h18-event-register') === false
        ) {
            return $content;
        }

        $events = self::eventStateByPermalink();
        if ($events === []) {
            return $content;
        }

        $cardPattern = '#<article\b[^>]*class=(["\'])[^"\']*\bh18-event-card\b[^"\']*\1[^>]*>.*?</article>#si';
        if (!preg_match_all($cardPattern, $content, $cardMatches) || empty($cardMatches[0])) {
            return $content;
        }

        $upcomingCards = [];
        $pastCards = [];
        foreach ($cardMatches[0] as $card) {
            if (!preg_match('#<a\b[^>]*href=(["\'])(.*?)\1#si', $card, $hrefMatch)) {
                // Never risk dropping a card if the legacy markup cannot be mapped safely.
                return $content;
            }
            $key = self::normalizeUrl(html_entity_decode((string) $hrefMatch[2], ENT_QUOTES | ENT_HTML5, 'UTF-8'));
            if ($key === '' || !isset($events[$key])) {
                return $content;
            }

            $record = $events[$key];
            $entry = [
                'card' => $card,
                'sort' => (string) ($record['SortKey'] ?? ''),
            ];
            if (!empty($record['Past'])) {
                $pastCards[] = $entry;
            } else {
                $upcomingCards[] = $entry;
            }
        }

        usort($upcomingCards, static fn(array $a, array $b): int => strcmp($a['sort'], $b['sort']));
        usort($pastCards, static fn(array $a, array $b): int => strcmp($b['sort'], $a['sort']));

        $upcoming = $upcomingCards
            ? implode('', array_column($upcomingCards, 'card'))
            : '<p>Der er ingen kommende arrangementer registreret.</p>';
        $past = $pastCards
            ? implode('', array_column($pastCards, 'card'))
            : '<p>Der er ingen tidligere arrangementer registreret.</p>';

        $registerPattern = '#'
            . '(<div\s+class=["\']h18-event-section-heading["\'][^>]*>\s*<h2>\s*Kommende arrangementer\s*</h2>\s*</div>\s*'
            . '<div\s+class=["\']h18-event-register["\'][^>]*>)'
            . '(.*?)'
            . '(</div>\s*<div\s+class=["\']h18-event-section-heading["\'][^>]*>\s*<h2>\s*Tidligere arrangementer\s*</h2>\s*</div>\s*'
            . '<div\s+class=["\']h18-event-register["\'][^>]*>)'
            . '(.*?)'
            . '(</div>\s*<!--\s*/wp:html\s*-->)#si';

        $updated = preg_replace_callback(
            $registerPattern,
            static function (array $match) use ($upcoming, $past): string {
                return $match[1] . $upcoming . $match[3] . $past . $match[5];
            },
            $content,
            1,
            $replacements
        );

        return is_string($updated) && $replacements === 1 ? $updated : $content;
    }

    /** @return array<string,array{Past:bool,SortKey:string}> */
    private static function eventStateByPermalink(): array
    {
        if (!function_exists('get_page_by_path') || !function_exists('get_pages')) {
            return [];
        }
        $parent = get_page_by_path(self::EVENT_PARENT_SLUG, OBJECT, 'page');
        if (!$parent instanceof \WP_Post) {
            return [];
        }

        $pages = get_pages([
            'parent' => (int) $parent->ID,
            'post_type' => 'page',
            'post_status' => 'publish',
            'sort_column' => 'menu_order,post_title',
        ]);
        if (!is_array($pages)) {
            return [];
        }

        $result = [];
        foreach ($pages as $page) {
            if (!$page instanceof \WP_Post || (string) $page->post_name === 'eventskabelon') {
                continue;
            }
            $data = self::decodeEventMarker((string) $page->post_content);
            if ($data === null) {
                continue;
            }
            $permalink = function_exists('get_permalink') ? get_permalink($page) : '';
            $key = self::normalizeUrl(is_string($permalink) ? $permalink : '');
            if ($key === '') {
                continue;
            }
            $date = trim((string) ($data['EventDate'] ?? ''));
            $start = self::normalizeTime((string) ($data['StartTime'] ?? ''));
            $end = self::normalizeTime((string) ($data['EndTime'] ?? ''));
            $result[$key] = [
                'Past' => self::isPastEvent($date, $end),
                'SortKey' => $date . ' ' . ($start !== '' ? $start : ($end !== '' ? $end : '23:59')),
            ];
        }
        return $result;
    }

    /** @return array<string,mixed>|null */
    private static function decodeEventMarker(string $content): ?array
    {
        if (!preg_match('/<!--\s*' . preg_quote(self::EVENT_MARKER, '/') . ':([A-Za-z0-9+\/=]+)\s*-->/', $content, $matches)) {
            return null;
        }
        $json = base64_decode((string) $matches[1], true);
        if (!is_string($json)) {
            return null;
        }
        $data = json_decode($json, true);
        return is_array($data) ? $data : null;
    }

    private static function isPastEvent(string $date, string $endTime): bool
    {
        if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date) || !function_exists('current_time')) {
            return false;
        }
        $today = (string) current_time('Y-m-d');
        if ($date < $today) {
            return true;
        }
        if ($date > $today) {
            return false;
        }

        // On the event date we keep it upcoming until its explicit end time.
        // Without an end time it remains upcoming for the rest of that day and
        // moves to the archive automatically after midnight.
        if ($endTime === '') {
            return false;
        }
        return $endTime <= (string) current_time('H:i');
    }

    private static function normalizeTime(string $value): string
    {
        $value = trim($value);
        if (!preg_match('/^([01]\d|2[0-3]):([0-5]\d)/', $value, $match)) {
            return '';
        }
        return $match[1] . ':' . $match[2];
    }

    private static function normalizeUrl(string $url): string
    {
        $url = trim($url);
        if ($url === '') {
            return '';
        }
        return rtrim($url, '/');
    }
}
