<?php

declare(strict_types=1);

$h18Options = [
    'hangar18_manager_site_templates_v1' => [
        'header-test' => [
            'SchemaVersion'=>'1.0','Id'=>'header-test','Kind'=>'header','Name'=>'Header test','Revision'=>1,'UpdatedUtc'=>'2026-08-18T00:00:00Z',
            'Sections'=>[
                ['Key'=>'header-root','Type'=>'flex','LayoutParentKey'=>'','Title'=>'','Content'=>''],
                ['Key'=>'brand','Type'=>'text','LayoutParentKey'=>'header-root','Title'=>'','Content'=>'Hangar18'],
            ],
        ],
        'footer-test' => [
            'SchemaVersion'=>'1.0','Id'=>'footer-test','Kind'=>'footer','Name'=>'Footer test','Revision'=>1,'UpdatedUtc'=>'2026-08-18T00:00:00Z',
            'Sections'=>[['Key'=>'footer-text','Type'=>'text','LayoutParentKey'=>'','Title'=>'','Content'=>'Footer']],
        ],
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
$h18Styles = [];
$h18Scripts = [];

function get_option(string $key, $default = false) { global $h18Options; return $h18Options[$key] ?? $default; }
function update_option(string $key, $value, $autoload = null): bool { global $h18Options; $h18Options[$key]=$value; return true; }
function add_action(string $hook, $callback, int $priority = 10): void { global $h18Actions; $h18Actions[] = [$hook,$callback,$priority]; }
function add_submenu_page($parent,$pageTitle,$menuTitle,$capability,$slug,$callback): string { global $h18Submenus; $h18Submenus[] = compact('parent','pageTitle','menuTitle','capability','slug','callback'); return $slug; }
function current_user_can(string $capability): bool { return $capability === 'edit_pages'; }
function is_admin(): bool { return true; }
function wp_die($message): void { throw new RuntimeException((string) $message); }
function esc_html__($text,$domain=null): string { return (string) $text; }
function esc_html($text): string { return htmlspecialchars((string) $text,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'); }
function esc_attr($text): string { return esc_html($text); }
function esc_url($text): string { return (string) $text; }
function esc_textarea($text): string { return esc_html($text); }
function sanitize_key($value): string { return preg_replace('/[^a-z0-9_-]/','',strtolower((string)$value)) ?? ''; }
function sanitize_text_field($value): string { return trim(strip_tags((string)$value)); }
function wp_unslash($value) { return $value; }
function admin_url(string $path=''): string { return 'https://example.test/wp-admin/'.$path; }
function add_query_arg(array $args, string $url): string { return $url.'?'.http_build_query($args); }
function wp_nonce_field($action): void { echo '<input type="hidden" name="_wpnonce" value="test">'; }
function selected($value,$current,$echo=true): string { $result=((string)$value===(string)$current)?' selected="selected"':''; if($echo){echo $result;} return $result; }
function wp_json_encode($value): string { return json_encode($value,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES) ?: 'null'; }
function plugins_url(string $path='', string $plugin=''): string { return 'https://example.test/wp-content/plugins/hangar18-manager/'.ltrim($path,'/'); }
function wp_enqueue_style($handle,$src,$deps=[],$ver=false,$media='all'): void { global $h18Styles; $h18Styles[$handle]=compact('src','deps','ver','media'); }
function wp_enqueue_script($handle,$src,$deps=[],$ver=false,$inFooter=false): void { global $h18Scripts; $h18Scripts[$handle]=['src'=>$src,'deps'=>$deps,'ver'=>$ver,'in_footer'=>$inFooter]; }

final class Hangar18_Manager { public const MENU_SLUG='hangar18-manager'; public const VERSION='0.7.5-test'; }

require_once dirname(__DIR__,2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Admin\IntegrationAdminBootstrap;
use Hangar18\UltimateDesigner\Admin\SiteTemplateAdminController;

function integrationAssert(bool $condition, string $message): void {
    if (!$condition) { throw new RuntimeException($message); }
}

IntegrationAdminBootstrap::register();
$hooks = array_map(static fn(array $row): string => (string)$row[0], $h18Actions);
foreach (['admin_menu','admin_post_h18_ud_create_site_template','admin_post_h18_ud_save_site_template','admin_post_h18_ud_delete_site_template','admin_enqueue_scripts'] as $hook) {
    integrationAssert(in_array($hook,$hooks,true), 'Integration bootstrap missing admin-only hook: '.$hook);
}
foreach ($hooks as $hook) {
    integrationAssert(!in_array($hook,['wp','init','wp_head','wp_footer','template_redirect'],true), 'Integration bootstrap unexpectedly registered frontend hook: '.$hook);
}
$actionCount = count($h18Actions);
IntegrationAdminBootstrap::register();
integrationAssert(count($h18Actions) === $actionCount, 'Integration bootstrap must be idempotent.');

IntegrationAdminBootstrap::registerMenu();
integrationAssert(count($h18Submenus) === 1, 'Ultimate Designer submenu must be registered once.');
integrationAssert($h18Submenus[0]['slug'] === 'hangar18-ultimate-designer', 'Unexpected integration submenu slug.');
integrationAssert($h18Submenus[0]['capability'] === 'edit_pages', 'Migration phase must preserve edit_pages capability gate.');

$_GET['page']='hangar18-ultimate-designer';
SiteTemplateAdminController::enqueueAssets('hangar18_page_hangar18-ultimate-designer');
integrationAssert(isset($h18Styles['hangar18-ultimate-designer-admin']), 'I2 CSS must be enqueued on Ultimate Designer page.');
integrationAssert(isset($h18Scripts['hangar18-ultimate-designer-admin']), 'I2 JavaScript must be enqueued on Ultimate Designer page.');
integrationAssert($h18Scripts['hangar18-ultimate-designer-admin']['in_footer'] === true, 'I2 JavaScript must load in footer after editor markup.');

$_GET['ud_template']='header-test';
ob_start();
IntegrationAdminBootstrap::render();
$html = (string) ob_get_clean();
foreach (['Ultimate Designer','Ingen sidekonvertering','Site Builder','Manual release gates','I1','I2','I10','Visual Header/Footer Builder','SHADOW · ingen cutover','Gem template','Live preview','header-root','brand'] as $needle) {
    integrationAssert(strpos($html,$needle) !== false, 'Integration dashboard missing: '.$needle);
}
integrationAssert(strpos($html,'1 Header · 1 Footer · 1 Menu') !== false, 'Repository-backed Site Builder counts are incorrect.');
integrationAssert(strpos($html,'1 registreret') !== false, 'Asset metadata count is incorrect.');
integrationAssert(strpos($html,'Header: header-test · Footer: ingen') !== false, 'Shadow assignment status is incorrect.');
integrationAssert(strpos($html,'name="action" value="h18_ud_save_site_template"') !== false, 'Visual builder save action missing.');
integrationAssert(strpos($html,'assignGlobal') === false, 'Visual builder must not expose public/global cutover action in I2.');

fwrite(STDOUT,"Ultimate Designer integration admin I1/I2: PASS\n");
