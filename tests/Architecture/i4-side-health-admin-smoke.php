<?php

declare(strict_types=1);

$h18Actions=[];$h18Styles=[];$h18Scripts=[];$h18Localized=[];
class I4JsonResponse extends RuntimeException{public bool $success;public array $data;public int $status;public function __construct(bool $success,array $data,int $status){parent::__construct('json response');$this->success=$success;$this->data=$data;$this->status=$status;}}
function add_action(string $hook,$callback,int $priority=10): void{global $h18Actions;$h18Actions[]=[$hook,$callback,$priority];}
function current_user_can(string $capability): bool{return $capability==='edit_pages';}
function sanitize_key($value): string{return trim(preg_replace('/[^a-z0-9_-]+/','-',strtolower((string)$value))??'','-_');}
function sanitize_text_field($value): string{return trim(strip_tags((string)$value));}
function wp_unslash($value){return $value;}
function plugins_url(string $path='',string $plugin=''): string{return 'https://example.test/wp-content/plugins/hangar18-manager/'.ltrim($path,'/');}
function wp_enqueue_style($handle,$src,$deps=[],$ver=false,$media='all'): void{global $h18Styles;$h18Styles[$handle]=compact('src','deps','ver','media');}
function wp_enqueue_script($handle,$src,$deps=[],$ver=false,$inFooter=false): void{global $h18Scripts;$h18Scripts[$handle]=['src'=>$src,'deps'=>$deps,'ver'=>$ver,'in_footer'=>$inFooter];}
function wp_localize_script($handle,$object,$data): void{global $h18Localized;$h18Localized[$handle]=[$object,$data];}
function admin_url(string $path=''): string{return 'https://example.test/wp-admin/'.$path;}
function wp_create_nonce($action): string{return 'nonce-'.$action;}
function check_ajax_referer($action,$field): bool{return isset($_POST[$field])&&$_POST[$field]==='nonce-'.$action;}
function wp_send_json_success($data=null,$status=200): void{throw new I4JsonResponse(true,is_array($data)?$data:[],(int)$status);}
function wp_send_json_error($data=null,$status=400): void{throw new I4JsonResponse(false,is_array($data)?$data:[],(int)$status);}
final class Hangar18_Manager{public const VERSION='0.7.7-test';}

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
use Hangar18\UltimateDesigner\Admin\SideHealthAdminController;
function i4Assert(bool $condition,string $message): void{if(!$condition)throw new RuntimeException($message);}

SideHealthAdminController::register();
$hooks=array_map(static fn(array $row):string=>(string)$row[0],$h18Actions);
i4Assert(in_array('wp_ajax_h18_ud_side_health',$hooks,true),'I4 AJAX hook missing.');
i4Assert(in_array('admin_enqueue_scripts',$hooks,true),'I4 admin asset hook missing.');
foreach($hooks as $hook){i4Assert(!in_array($hook,['wp','init','wp_head','wp_footer','template_redirect'],true),'I4 registered frontend hook: '.$hook);}

$_GET['page']='other';SideHealthAdminController::enqueueAssets('other_page');i4Assert($h18Styles===[]&&$h18Scripts===[],'I4 assets loaded on unrelated admin page.');
$_GET['page']='hangar18-pages';SideHealthAdminController::enqueueAssets('hangar18_page_hangar18-pages');
i4Assert(isset($h18Styles['hangar18-ultimate-designer-side-health']),'I4 Side Health CSS not enqueued.');
i4Assert(isset($h18Scripts['hangar18-ultimate-designer-side-health']),'I4 Side Health JS not enqueued.');
i4Assert(($h18Scripts['hangar18-ultimate-designer-side-health']['in_footer']??false)===true,'I4 JS must load in footer.');
i4Assert(isset($h18Localized['hangar18-ultimate-designer-side-health']),'I4 nonce/ajax config not localized.');

$state=[
 'Version'=>'1.22','PageSlug'=>'health-test','PageTitle'=>'Health test','ContentVersion'=>1,'DataContextType'=>'','DataContextEntryId'=>0,
 'Sections'=>[
  ['Key'=>'h1','Type'=>'heading','HeadingTag'=>'h1','Title'=>'Health test','LayoutParentKey'=>''],
  ['Key'=>'photo','Type'=>'image','MediaId'=>15,'AltText'=>'','LayoutParentKey'=>''],
  ['Key'=>'button','Type'=>'button','Label'=>'','MobileWidthPx'=>600,'MobileHeightPx'=>30,'LayoutParentKey'=>''],
 ]
];
$seo=['Title'=>'Health test','MetaDescription'=>'','CanonicalUrl'=>'','Index'=>true,'Follow'=>true,'SocialTitle'=>'Health test','SocialDescription'=>'','SocialImageMediaId'=>0];
$_POST=['nonce'=>'nonce-h18_ud_side_health_v1','state_json'=>json_encode($state),'seo_json'=>json_encode($seo)];
try{SideHealthAdminController::analyze();throw new RuntimeException('I4 analyze did not return JSON.');}catch(I4JsonResponse $response){
 i4Assert($response->success===true&&$response->status===200,'I4 valid snapshot must succeed.');
 $report=$response->data['report']??null;i4Assert(is_array($report),'I4 report missing.');
 i4Assert((int)($report['HardFailureCount']??0)>0,'I4 fixture should expose hard failures.');
 $issues=$report['Issues']??[];$keys=array_map(static fn(array $issue):string=>(string)($issue['ElementKey']??''),$issues);
 i4Assert(in_array('photo',$keys,true),'I4 report must preserve concrete photo element reference.');
 i4Assert(in_array('button',$keys,true),'I4 report must preserve concrete button element reference.');
}

$_POST=['nonce'=>'nonce-h18_ud_side_health_v1','state_json'=>str_repeat('x',524289),'seo_json'=>'{}'];
try{SideHealthAdminController::analyze();throw new RuntimeException('I4 oversized snapshot unexpectedly succeeded.');}catch(I4JsonResponse $response){i4Assert($response->success===false&&$response->status===400,'I4 oversized snapshot must be rejected.');}

fwrite(STDOUT,"I4 Side Health existing page editor bridge: PASS\n");
