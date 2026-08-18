<?php

declare(strict_types=1);

$h18Options = [
    'hangar18_manager_site_templates_v1' => [
        'header-test' => ['Id'=>'header-test','Kind'=>'header','Name'=>'Header test','Revision'=>1,'Sections'=>[]],
        'footer-test' => ['Id'=>'footer-test','Kind'=>'footer','Name'=>'Footer test','Revision'=>1,'Sections'=>[]],
    ],
    'hangar18_manager_site_template_assignments_v1' => ['header'=>'header-test'],
    'hangar18_manager_site_menus_v1' => [
        'main' => ['Id'=>'main','Name'=>'Main','Items'=>[]],
    ],
    'hangar18_ud_asset_metadata_v1' => [
        42 => ['MediaId'=>42,'Collections'=>['historisk']],
    ],
];
$h18Actions = [];
$h18Submenus = [];

function get_option(string $key, $default = false) { global $h18Options; return $h18Options[$key] ?? $default; }
function update_option(string $key, $value, $autoload = null): bool { global $h18Options; $h18Options[$key]=$value; return true; }
function add_action(string $hook, $callback, int $priority = 10): void { global $h18Actions; $h18Actions[] = [$hook,$callback,$priority]; }
function add_submenu_page($parent,$pageTitle,$menuTitle,$capability,$slug,$callback): string { global $h18Submenus; $h18Submenus[] = compact('parent','pageTitle','menuTitle','capability','slug','callback'); return $slug; }
function current_user_can(string $capability): bool { return $capability === 'edit_pages'; }
function is_admin(): bool { return true; }
function wp_die($message): void { throw new RuntimeException((string) $message); }
function esc_html__($text,$domain=null): string { return (string) $text; }
function esc_html($text): string { return htmlspecialchars((string) $text,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'); }

final class Hangar18_Manager { public const MENU_SLUG='hangar18-manager'; }

require_once dirname(__DIR__,2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Admin\IntegrationAdminBootstrap;

function integrationAssert(bool $condition, string $message): void {
    if (!$condition) { throw new RuntimeException($message); }
}

IntegrationAdminBootstrap::register();
integrationAssert(count($h18Actions) === 1, 'Integration bootstrap must register exactly one admin_menu hook.');
integrationAssert($h18Actions[0][0] === 'admin_menu' && $h18Actions[0][2] === 30, 'Integration menu hook must be admin-only at priority 30.');

IntegrationAdminBootstrap::register();
integrationAssert(count($h18Actions) === 1, 'Integration bootstrap must be idempotent.');

IntegrationAdminBootstrap::registerMenu();
integrationAssert(count($h18Submenus) === 1, 'Ultimate Designer submenu must be registered once.');
integrationAssert($h18Submenus[0]['slug'] === 'hangar18-ultimate-designer', 'Unexpected integration submenu slug.');
integrationAssert($h18Submenus[0]['capability'] === 'edit_pages', 'Migration phase must preserve edit_pages capability gate.');

ob_start();
IntegrationAdminBootstrap::render();
$html = (string) ob_get_clean();
foreach (['Ultimate Designer','Ingen sidekonvertering','Site Builder','Manual release gates','I1','I10','Kontrolleret konvertering'] as $needle) {
    integrationAssert(strpos($html,$needle) !== false, 'Integration dashboard missing: '.$needle);
}
integrationAssert(strpos($html,'1 Header · 1 Footer · 1 Menu') !== false, 'Repository-backed Site Builder counts are incorrect.');
integrationAssert(strpos($html,'1 registreret') !== false, 'Asset metadata count is incorrect.');
integrationAssert(strpos($html,'Header: header-test · Footer: ingen') !== false, 'Shadow assignment status is incorrect.');

fwrite(STDOUT,"Ultimate Designer integration admin I1: PASS\n");
