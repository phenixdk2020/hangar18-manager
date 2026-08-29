<?php

declare(strict_types=1);

if (!function_exists('sanitize_key')) {
    function sanitize_key($value): string { return strtolower((string) preg_replace('/[^a-z0-9_\-]/i', '', (string) $value)); }
}
if (!function_exists('sanitize_text_field')) {
    function sanitize_text_field($value): string { return trim(strip_tags((string) $value)); }
}
if (!function_exists('wp_kses_post')) {
    function wp_kses_post($value): string { return (string) $value; }
}
if (!function_exists('sanitize_hex_color')) {
    function sanitize_hex_color($value) { $value=(string)$value; return preg_match('/^#[0-9a-f]{6}$/i',$value) ? strtolower($value) : null; }
}
if (!function_exists('absint')) {
    function absint($value): int { return abs((int) $value); }
}
if (!function_exists('esc_url_raw')) {
    function esc_url_raw($value): string { return (string) $value; }
}
if (!function_exists('wp_json_encode')) {
    function wp_json_encode($value, int $flags=0, int $depth=512) { return json_encode($value,$flags,$depth); }
}

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/LayoutModel.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/VisualBlockConversionService.php';

use Hangar18\Clean\Migration\VisualBlockConversionService;

function v152Fail(string $message): void { fwrite(STDERR, "V0152 VISUAL QA FAIL: {$message}\n"); exit(1); }
function v152Assert(bool $condition, string $message): void { if (!$condition) { v152Fail($message); } }

$fixture = <<<'HTML'
<div class="h18-page-frame">
  <div class="wp-block-cover alignfull avpf-home-hero" style="min-height:260px">
    <img class="wp-block-cover__image-background" src="https://test2.hangar18.dk/wp-content/uploads/2026/08/Banner-6.jpg" alt="Historiske militærkøretøjer">
  </div>
  <div class="wp-block-group alignfull avpf-home-tagline" style="color:#30382a;background-color:#c3ae83">
    <p class="has-text-align-center">Bevaring, restaurering og levende formidling af dansk militærhistorie.</p>
  </div>
  <div class="wp-block-group alignfull avpf-section" style="color:#30382a;background-color:#f2f0e8">
    <h2 class="has-text-align-center">Om foreningen</h2>
    <p class="has-text-align-center">Aalborg Kaserners Veteran Panser- og Køretøjsforening arbejder med at indsamle, restaurere, vedligeholde og bevare militærhistorisk materiel samt formidle dets historie.</p>
    <p class="has-text-align-center">Der lægges særlig vægt på bælte-, hjul- og hestekøretøjer.</p>
    <div class="wp-block-buttons"><div class="wp-block-button"><a href="https://test2.hangar18.dk/om-foreningen/">Læs om foreningen</a></div></div>
  </div>
  <div class="wp-block-group alignfull avpf-section" style="color:#30382a;background-color:#f2f0e8">
    <div class="wp-block-columns">
      <div class="wp-block-column"><div class="wp-block-group avpf-card" style="background-color:#ffffff"><h3>Køretøjer</h3><p>Se foreningens materiel.</p><div class="wp-block-buttons"><div class="wp-block-button"><a href="https://test2.hangar18.dk/koeretoejer/">Se køretøjer</a></div></div></div></div>
      <div class="wp-block-column"><div class="wp-block-group avpf-card" style="background-color:#ffffff"><h3>Events</h3><p>Se kommende arrangementer.</p></div></div>
    </div>
  </div>
</div>
HTML;

$warnings=[];
$model=VisualBlockConversionService::build(9,$fixture,$warnings);
v152Assert(is_array($model),'No model returned.');
$nodes=$model['nodes'] ?? [];
v152Assert(count($nodes)>=10,'Too few canonical nodes.');
$roots=array_values(array_filter($nodes,static fn(array $n): bool => (string)($n['parentId']??'')===''));
v152Assert(count($roots)===4,'Expected four top-level sections.');
foreach($roots as $root){v152Assert(($root['type']??'')==='section','Non-Section node remains at page root.');}
v152Assert((int)$roots[0]['geometry']['desktop']['x']===6 && (int)$roots[0]['geometry']['desktop']['w']===108,'Desktop frame is not 90%.');
v152Assert((int)$roots[0]['geometry']['mobile']['x']===0 && (int)$roots[0]['geometry']['mobile']['w']===120,'Mobile frame is not 100%.');
v152Assert((int)$roots[0]['geometry']['desktop']['y']===4,'Desktop top spacing is not 32px/4 rows.');
v152Assert((int)$roots[1]['geometry']['desktop']['y']===41,'Desktop 32px gap after 33-row hero is wrong.');

$hero=array_values(array_filter($nodes,static fn(array $n): bool => ($n['type']??'')==='image' && str_contains((string)($n['props']['url']??''),'Banner-6.jpg')));
v152Assert(count($hero)===1,'Hero did not become canonical Image.');
$tagline=array_values(array_filter($nodes,static fn(array $n): bool => ($n['type']??'')==='text' && str_contains((string)($n['props']['text']??''),'Bevaring, restaurering')));
v152Assert(count($tagline)===1,'Tagline did not become canonical Text.');
v152Assert(($tagline[0]['props']['align']??'')==='center','Tagline is not centered.');
$buttons=array_values(array_filter($nodes,static fn(array $n): bool => ($n['type']??'')==='button'));
v152Assert(count($buttons)>=2,'Gutenberg buttons did not become canonical Button nodes.');
$containers=array_values(array_filter($nodes,static fn(array $n): bool => ($n['type']??'')==='container'));
v152Assert(count($containers)>=2,'Columns/cards did not become Kasse/container nodes.');
foreach($containers as $container){v152Assert((string)($container['parentId']??'')!=='','A converted Kasse was incorrectly placed at page root.');}
v152Assert(in_array('visual-block-conversion-v0152',$warnings,true),'Visual conversion warning/marker missing.');
v152Assert(in_array('visual-hero-image-converted',$warnings,true),'Hero conversion marker missing.');

echo "VisualBlockConversionService v0.1.52 QA PASS\n";
