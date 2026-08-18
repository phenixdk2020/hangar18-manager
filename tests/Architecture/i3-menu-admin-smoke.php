<?php

declare(strict_types=1);

$h18Options = [
    'hangar18_manager_site_menus_v1' => [
        'main' => [
            'SchemaVersion'=>'1.0','Id'=>'main','Name'=>'Main','Revision'=>2,'UpdatedUtc'=>'2026-08-18T00:00:00Z',
            'Items'=>[
                ['Id'=>'home','ParentId'=>'','Order'=>10,'Type'=>'url','Label'=>'Hjem','Target'=>'','Url'=>'/','Icon'=>'⌂','Badge'=>'','Description'=>'','OpenNew'=>false,'ComponentId'=>''],
                ['Id'=>'about','ParentId'=>'','Order'=>20,'Type'=>'url','Label'=>'Om','Target'=>'','Url'=>'/om/','Icon'=>'','Badge'=>'Ny','Description'=>'Om os','OpenNew'=>false,'ComponentId'=>'about-panel'],
                ['Id'=>'contact','ParentId'=>'about','Order'=>30,'Type'=>'url','Label'=>'Kontakt','Target'=>'','Url'=>'/kontakt/','Icon'=>'','Badge'=>'','Description'=>'','OpenNew'=>false,'ComponentId'=>''],
            ],
            'Presentation'=>['DesktopPreset'=>'mega-menu','MobilePreset'=>'off-canvas-mobile','MotionPreset'=>'motion-pill','BreakpointPx'=>920,'MegaColumns'=>4,'MobileToggleLabel'=>'Menu','AriaLabel'=>'Hovedmenu','ShowIcons'=>true,'ShowBadges'=>true],
        ],
    ],
];
$h18Actions=[];$h18Styles=[];$h18Scripts=[];
function get_option(string $key,$default=false){global $h18Options;return $h18Options[$key]??$default;}
function update_option(string $key,$value,$autoload=null): bool{global $h18Options;$h18Options[$key]=$value;return true;}
function add_action(string $hook,$callback,int $priority=10): void{global $h18Actions;$h18Actions[]=[$hook,$callback,$priority];}
function current_user_can(string $capability): bool{return $capability==='edit_pages';}
function wp_die($message): void{throw new RuntimeException((string)$message);}
function sanitize_key($value): string{return trim(preg_replace('/[^a-z0-9_-]+/','-',strtolower((string)$value))??'','-_');}
function sanitize_text_field($value): string{return trim(strip_tags((string)$value));}
function wp_unslash($value){return $value;}
function esc_url_raw($value,$protocols=null): string{$value=trim((string)$value);return preg_match('#^(https?|mailto|tel):#i',$value)?$value:'';}
function esc_html__($text,$domain=null): string{return (string)$text;}
function esc_html($text): string{return htmlspecialchars((string)$text,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');}
function esc_attr($text): string{return esc_html($text);}
function esc_url($text): string{return (string)$text;}
function admin_url(string $path=''): string{return 'https://example.test/wp-admin/'.$path;}
function add_query_arg(array $args,string $url): string{return $url.'?'.http_build_query($args);}
function wp_nonce_field($action): void{echo '<input type="hidden" name="_wpnonce" value="test">';}
function selected($value,$current,$echo=true): string{$r=((string)$value===(string)$current)?' selected="selected"':'';if($echo)echo $r;return $r;}
function checked($value,$current=true,$echo=true): string{$r=((bool)$value===(bool)$current)?' checked="checked"':'';if($echo)echo $r;return $r;}
function plugins_url(string $path='',string $plugin=''): string{return 'https://example.test/wp-content/plugins/hangar18-manager/'.ltrim($path,'/');}
function wp_enqueue_style($handle,$src,$deps=[],$ver=false,$media='all'): void{global $h18Styles;$h18Styles[$handle]=compact('src','deps','ver','media');}
function wp_enqueue_script($handle,$src,$deps=[],$ver=false,$inFooter=false): void{global $h18Scripts;$h18Scripts[$handle]=['src'=>$src,'deps'=>$deps,'ver'=>$ver,'in_footer'=>$inFooter];}
final class Hangar18_Manager{public const VERSION='0.7.6-test';}

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Admin\IntegrationAdminBootstrap;
use Hangar18\UltimateDesigner\Admin\MenuAdminController;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionMenuRepository;
use Hangar18\UltimateDesigner\SiteBuilder\MenuPresentationNormalizer;
use Hangar18\UltimateDesigner\SiteBuilder\MenuService;
use Hangar18\UltimateDesigner\SiteBuilder\MenuTreeValidator;

function i3Assert(bool $condition,string $message): void{if(!$condition)throw new RuntimeException($message);}

MenuAdminController::register();
$hooks=array_map(static fn(array $row):string=>(string)$row[0],$h18Actions);
foreach(['admin_post_h18_ud_create_menu','admin_post_h18_ud_save_menu','admin_post_h18_ud_delete_menu','admin_enqueue_scripts'] as $hook){i3Assert(in_array($hook,$hooks,true),'I3 hook missing: '.$hook);}
foreach($hooks as $hook){i3Assert(!in_array($hook,['wp','init','wp_head','wp_footer','template_redirect'],true),'I3 registered frontend hook: '.$hook);}

$_GET['page']='other';
MenuAdminController::enqueueAssets('other_page');
i3Assert($h18Styles===[]&&$h18Scripts===[],'I3 assets loaded outside Ultimate Designer page.');
$_GET['page']=IntegrationAdminBootstrap::PAGE_SLUG;
MenuAdminController::enqueueAssets('hangar18_page_'.IntegrationAdminBootstrap::PAGE_SLUG);
i3Assert(isset($h18Styles['hangar18-ultimate-designer-menu-admin']),'I3 CSS not enqueued.');
i3Assert(isset($h18Scripts['hangar18-ultimate-designer-menu-admin']),'I3 JS not enqueued.');
i3Assert($h18Scripts['hangar18-ultimate-designer-menu-admin']['in_footer']===true,'I3 JS must load in footer.');

$normalizer=new MenuPresentationNormalizer();
$presentation=$normalizer->normalize(['DesktopPreset'=>'mega-menu','MobilePreset'=>'fullscreen-overlay','MotionPreset'=>'motion-slide','BreakpointPx'=>9999,'MegaColumns'=>99,'AriaLabel'=>'']);
i3Assert($presentation['DesktopPreset']==='mega-menu','Desktop preset lost.');
i3Assert($presentation['MobilePreset']==='fullscreen-overlay','Mobile preset lost.');
i3Assert($presentation['MotionPreset']==='motion-slide','Motion preset lost.');
i3Assert($presentation['BreakpointPx']===1400&&$presentation['MegaColumns']===5,'Presentation numeric clamps failed.');
i3Assert($presentation['AriaLabel']==='Hovedmenu','Empty aria label must get accessible fallback.');
$options=$normalizer->options();
foreach(['floating-pill','mega-menu','side-rail'] as $key)i3Assert(isset($options['Desktop'][$key]),'Desktop preset option missing: '.$key);
foreach(['off-canvas-mobile','fullscreen-overlay','bottom-mobile'] as $key)i3Assert(isset($options['Mobile'][$key]),'Mobile preset option missing: '.$key);

$service=new MenuService(new WordPressOptionMenuRepository(),new MenuTreeValidator(),$normalizer);
$loaded=$service->get('main');
i3Assert(is_array($loaded)&&($loaded['Presentation']['DesktopPreset']??'')==='mega-menu','MenuService did not normalize stored presentation.');
$updated=$service->update('main','Main updated',$loaded['Items'],['DesktopPreset'=>'floating-pill','MobilePreset'=>'bottom-mobile','MotionPreset'=>'motion-icon']);
i3Assert(($updated['Presentation']['DesktopPreset']??'')==='floating-pill','Presentation update not persisted.');
i3Assert(($updated['Presentation']['MobilePreset']??'')==='bottom-mobile','Mobile presentation update not persisted.');

$_POST['items']=[
 ['Id'=>'home','ParentId'=>'','Type'=>'url','Label'=>'Hjem','Url'=>'/','Target'=>'','Icon'=>'⌂','Badge'=>'','Description'=>'','OpenNew'=>'0','ComponentId'=>'','Remove'=>'0'],
 ['Id'=>'bad','ParentId'=>'home','Type'=>'url','Label'=>'Farlig','Url'=>'javascript:alert(1)','Target'=>'','Icon'=>'','Badge'=>'','Description'=>'','OpenNew'=>'1','ComponentId'=>'mega-panel','Remove'=>'0'],
];
$method=new ReflectionMethod(MenuAdminController::class,'postedItems');$method->setAccessible(true);$items=$method->invoke(null);
i3Assert(count($items)===2,'I3 item normalizer lost rows.');
i3Assert($items[0]['Order']===10&&$items[1]['Order']===20,'I3 order must be recomputed from editor order.');
i3Assert($items[1]['ParentId']==='home','Nested ParentId lost.');
i3Assert($items[1]['Url']==='','javascript: URL must be rejected.');
i3Assert($items[1]['OpenNew']===true,'OpenNew normalization failed.');
i3Assert($items[1]['ComponentId']==='mega-panel','Mega panel ComponentId lost.');

$_POST['presentation']=['DesktopPreset'=>'mega-menu','MobilePreset'=>'off-canvas-mobile','MotionPreset'=>'motion-pill','BreakpointPx'=>'880','MegaColumns'=>'3','MobileToggleLabel'=>'Navigation','AriaLabel'=>'Primær navigation','ShowIcons'=>'1','ShowBadges'=>'1'];
$pm=new ReflectionMethod(MenuAdminController::class,'postedPresentation');$pm->setAccessible(true);$posted=$pm->invoke(null);
i3Assert($posted['DesktopPreset']==='mega-menu'&&$posted['MobilePreset']==='off-canvas-mobile','Posted presets failed.');
i3Assert($posted['BreakpointPx']===880&&$posted['MegaColumns']===3,'Posted presentation numbers failed.');

$_GET['ud_menu']='main';
ob_start();MenuAdminController::renderPanel();$html=(string)ob_get_clean();
foreach(['I3 · Menu UI v2','SHADOW · legacy menu er aktiv','Desktop preset','Mobil preset','Hover/aktiv effekt','Mega-panel ComponentId','Keyboard-preview','Gem menu'] as $needle){i3Assert(strpos($html,$needle)!==false,'I3 UI missing: '.$needle);}
i3Assert(strpos($html,'assignGlobal')===false&&strpos($html,'activate')===false,'I3 UI must not expose public cutover.');

$cycle=['SchemaVersion'=>'1.0','Id'=>'cyclic','Name'=>'Cycle','Revision'=>1,'Items'=>[
 ['Id'=>'one','ParentId'=>'two','Order'=>10,'Type'=>'url','Label'=>'One','Url'=>'/one'],
 ['Id'=>'two','ParentId'=>'one','Order'=>20,'Type'=>'url','Label'=>'Two','Url'=>'/two'],
]];
i3Assert((new MenuTreeValidator())->validate($cycle)!==[],'Menu cycle must be rejected.');

fwrite(STDOUT,"I3 Menu UI v2 shadow admin: PASS\n");
