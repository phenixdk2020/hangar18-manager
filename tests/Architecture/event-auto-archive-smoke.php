<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Event\EventArchiveRuntime;

if (!defined('OBJECT')) { define('OBJECT', 'OBJECT'); }

final class WP_Post
{
    public int $ID;
    public string $post_name;
    public string $post_title;
    public string $post_content;

    public function __construct(int $id, string $slug, string $title, string $content = '')
    {
        $this->ID = $id;
        $this->post_name = $slug;
        $this->post_title = $title;
        $this->post_content = $content;
    }
}

$GLOBALS['event_test_is_events'] = true;
$GLOBALS['event_test_filters'] = [];
$GLOBALS['event_test_pages'] = [];
$GLOBALS['event_test_parent'] = new WP_Post(12, 'events', 'Events');

function eventAssert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}
function add_filter(string $hook, $callback, int $priority = 10): void
{
    $GLOBALS['event_test_filters'][] = [$hook, $callback, $priority];
}
function is_admin(): bool { return false; }
function is_page($slug): bool { return $GLOBALS['event_test_is_events'] && $slug === 'events'; }
function current_time(string $format): string
{
    return $format === 'Y-m-d' ? '2026-08-20' : ($format === 'H:i' ? '18:43' : '');
}
function get_page_by_path(string $slug, string $output = OBJECT, string $postType = 'page'): ?WP_Post
{
    return $slug === 'events' ? $GLOBALS['event_test_parent'] : null;
}
function get_pages(array $args = []): array { return $GLOBALS['event_test_pages']; }
function get_permalink($post): string { return 'https://example.test/events/' . $post->post_name . '/'; }

function eventMarker(array $data): string
{
    return '<!-- HANGAR18-EVENT-DATA:' . base64_encode((string) json_encode($data, JSON_UNESCAPED_SLASHES)) . ' -->';
}
function eventCard(string $slug, string $title): string
{
    return '<article class="h18-event-card"><a href="https://example.test/events/' . $slug . '/"><div class="h18-event-card-body"><h3>' . $title . '</h3></div></a></article>';
}

require_once dirname(__DIR__, 2) . '/src/Event/EventArchiveRuntime.php';

$GLOBALS['event_test_pages'] = [
    new WP_Post(20, 'gammel', 'Gammel', eventMarker(['EventDate'=>'2026-08-15','StartTime'=>'10:00','EndTime'=>'12:00'])),
    new WP_Post(21, 'sluttet-i-dag', 'Sluttet i dag', eventMarker(['EventDate'=>'2026-08-20','StartTime'=>'16:00','EndTime'=>'18:00'])),
    new WP_Post(22, 'aktiv-i-dag', 'Aktiv i dag', eventMarker(['EventDate'=>'2026-08-20','StartTime'=>'18:00','EndTime'=>'19:30'])),
    new WP_Post(23, 'uden-sluttid', 'Uden sluttid', eventMarker(['EventDate'=>'2026-08-20','StartTime'=>'08:00','EndTime'=>''])),
    new WP_Post(24, 'fremtid', 'Fremtid', eventMarker(['EventDate'=>'2026-08-21','StartTime'=>'09:00','EndTime'=>'10:00'])),
    new WP_Post(25, 'eventskabelon', 'Skabelon', eventMarker(['EventDate'=>'2020-01-01','EndTime'=>'00:01'])),
];

$source = '<!-- wp:html -->'
    . '<div class="h18-event-section-heading"><h2>Kommende arrangementer</h2></div>'
    . '<div class="h18-event-register">'
    . eventCard('gammel', 'Gammel')
    . eventCard('sluttet-i-dag', 'Sluttet i dag')
    . eventCard('aktiv-i-dag', 'Aktiv i dag')
    . eventCard('uden-sluttid', 'Uden sluttid')
    . eventCard('fremtid', 'Fremtid')
    . '</div>'
    . '<div class="h18-event-section-heading"><h2>Tidligere arrangementer</h2></div>'
    . '<div class="h18-event-register"><p>Der er ingen tidligere arrangementer registreret.</p></div>'
    . '<!-- /wp:html -->';

EventArchiveRuntime::register();
EventArchiveRuntime::register();
eventAssert(count($GLOBALS['event_test_filters']) === 1, 'Runtime registration must be idempotent.');
eventAssert($GLOBALS['event_test_filters'][0][0] === 'the_content', 'Runtime must register only on the_content.');
eventAssert($GLOBALS['event_test_filters'][0][2] === 8, 'Runtime must execute before WordPress do_blocks priority 9.');

$result = EventArchiveRuntime::filterContent($source);
eventAssert($result !== $source, 'Events overview should be reclassified at render time.');

$pastHeading = strpos($result, 'Tidligere arrangementer');
eventAssert($pastHeading !== false, 'Past heading is missing after dynamic classification.');

$oldPos = strpos($result, '<h3>Gammel</h3>');
$endedPos = strpos($result, '<h3>Sluttet i dag</h3>');
$activePos = strpos($result, '<h3>Aktiv i dag</h3>');
$noEndPos = strpos($result, '<h3>Uden sluttid</h3>');
$futurePos = strpos($result, '<h3>Fremtid</h3>');

eventAssert($endedPos !== false && $endedPos > $pastHeading, 'Today event must archive once explicit EndTime has passed.');
eventAssert($oldPos !== false && $oldPos > $pastHeading, 'Past-date event must be archived automatically.');
eventAssert($activePos !== false && $activePos < $pastHeading, 'Event whose EndTime has not passed must remain upcoming.');
eventAssert($noEndPos !== false && $noEndPos < $pastHeading, 'Event without EndTime must stay upcoming for the rest of its date.');
eventAssert($futurePos !== false && $futurePos < $pastHeading, 'Future event must remain upcoming.');
eventAssert($endedPos < $oldPos, 'Archive must show newest past event first.');
eventAssert($activePos < $futurePos, 'Upcoming events must sort chronologically.');
eventAssert(strpos($result, 'Skabelon') === false, 'eventskabelon must never enter the public register.');

$GLOBALS['event_test_is_events'] = false;
eventAssert(EventArchiveRuntime::filterContent($source) === $source, 'Non-Events pages must remain untouched.');

fwrite(STDOUT, "EVENT-001 automatic date/time archive: PASS\n");
