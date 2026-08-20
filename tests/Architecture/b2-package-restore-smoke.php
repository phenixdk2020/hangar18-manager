<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Backup\SiteBackupManifestService;
use Hangar18\UltimateDesigner\Backup\SiteBackupPackageService;
use Hangar18\UltimateDesigner\Backup\SiteBackupRestoreCoordinator;
use Hangar18\UltimateDesigner\Backup\SiteBackupSecurityPolicy;

if (!defined('OBJECT')) { define('OBJECT', 'OBJECT'); }
if (!defined('AUTH_SALT')) { define('AUTH_SALT', 'b2-test-auth-salt'); }

final class WP_Post
{
    public int $ID;
    public string $post_type='page';
    public string $post_title='';
    public string $post_name='';
    public string $post_status='draft';
    public int $post_parent=0;
    public string $post_excerpt='';
    public string $post_content='';
    public function __construct(array $data){ foreach($data as $k=>$v){ if(property_exists($this,(string)$k)){$this->{$k}=$v;} } }
}
final class WP_Error
{
    public function __construct(private string $message){}
    public function get_error_message(): string { return $this->message; }
}
final class Hangar18_Manager { public const VERSION='0.8.31'; }
final class B2Wpdb
{
    public string $options='wp_options';
    public function esc_like(string $value): string { return $value; }
    public function prepare(string $query, ...$args): string { return $query; }
    public function get_col(string $query): array
    {
        return array_values(array_filter(array_keys($GLOBALS['b2_options']), static function(string $name): bool {
            return str_starts_with($name,'hangar18_') || str_starts_with($name,'h18_');
        }));
    }
}

$GLOBALS['b2_tmp']=sys_get_temp_dir().'/h18-b2-'.bin2hex(random_bytes(4));
$GLOBALS['b2_options']=[];
$GLOBALS['b2_posts']=[];
$GLOBALS['b2_meta']=[];
$GLOBALS['b2_thumbs']=[];
$GLOBALS['b2_next_id']=100;
$GLOBALS['wpdb']=new B2Wpdb();

function b2Assert(bool $ok,string $message): void { if(!$ok){throw new RuntimeException($message);} }
function b2CanonicalEqual($left,$right): bool
{
    $canonical=new SiteBackupManifestService();
    return hash_equals($canonical->canonicalJson($left),$canonical->canonicalJson($right));
}
function sanitize_title(string $v): string { $v=strtolower(trim($v));$v=preg_replace('/[^a-z0-9-]+/','-',$v)??'';return trim($v,'-'); }
function sanitize_text_field(string $v): string { return trim(strip_tags($v)); }
function wp_upload_dir(): array { return ['basedir'=>$GLOBALS['b2_tmp'].'/uploads','baseurl'=>'https://example.test/wp-content/uploads','error'=>'']; }
function wp_mkdir_p(string $dir): bool { return is_dir($dir)||mkdir($dir,0777,true); }
function home_url(string $path=''): string { return 'https://example.test'.($path===''?'':'/'.ltrim($path,'/')); }
function site_url(string $path=''): string { return 'https://example.test'.($path===''?'':'/'.ltrim($path,'/')); }
function get_option(string $name,$default=false){return $GLOBALS['b2_options'][$name]??$default;}
function update_option(string $name,$value,$autoload=false): bool {$GLOBALS['b2_options'][$name]=$value;return true;}
function add_option(string $name,$value,$deprecated='',$autoload=true): bool {if(array_key_exists($name,$GLOBALS['b2_options']))return false;$GLOBALS['b2_options'][$name]=$value;return true;}
function delete_option(string $name): bool {unset($GLOBALS['b2_options'][$name]);return true;}
function get_current_user_id(): int { return 7; }
function wp_salt(string $scheme='auth'): string { return 'b2-test-salt-'.$scheme; }
function maybe_unserialize($value){return $value;}
function get_posts(array $args=[]): array {
    $type=(string)($args['post_type']??'post');
    return array_values(array_filter($GLOBALS['b2_posts'],static fn($p)=>$p instanceof WP_Post&&$p->post_type===$type));
}
function get_post(int $id): ?WP_Post {return $GLOBALS['b2_posts'][$id]??null;}
function get_page_by_path(string $slug,string $output=OBJECT,string $type='page'): ?WP_Post {foreach($GLOBALS['b2_posts'] as $p){if($p instanceof WP_Post&&$p->post_type===$type&&$p->post_name===$slug)return $p;}return null;}
function get_post_meta(int $id,$key='',$single=false){if($key!==''){return $GLOBALS['b2_meta'][$id][$key]??($single?'':[]);} $out=[];foreach(($GLOBALS['b2_meta'][$id]??[]) as $k=>$v){$out[$k]=is_array($v)?$v:[$v];}return $out;}
function update_post_meta(int $id,string $key,$value): bool {$GLOBALS['b2_meta'][$id][$key]=$value;return true;}
function get_post_thumbnail_id(int $id): int {return (int)($GLOBALS['b2_thumbs'][$id]??0);}
function set_post_thumbnail(int $id,int $media): bool {$GLOBALS['b2_thumbs'][$id]=$media;return true;}
function delete_post_thumbnail(int $id): bool {unset($GLOBALS['b2_thumbs'][$id]);return true;}
function is_wp_error($v): bool {return $v instanceof WP_Error;}
function wp_update_post(array $data,bool $wpError=false){$id=(int)($data['ID']??0);$p=$GLOBALS['b2_posts'][$id]??null;if(!$p instanceof WP_Post)return $wpError?new WP_Error('missing'):0;foreach(['post_title','post_status','post_parent','post_excerpt','post_content','post_name'] as $f){if(array_key_exists($f,$data)){$p->{$f}=$data[$f];}}return $id;}
function wp_insert_post(array $data,bool $wpError=false){$id=$GLOBALS['b2_next_id']++;$GLOBALS['b2_posts'][$id]=new WP_Post(['ID'=>$id,'post_type'=>(string)($data['post_type']??'post'),'post_title'=>(string)($data['post_title']??''),'post_name'=>(string)($data['post_name']??''),'post_status'=>(string)($data['post_status']??'draft'),'post_parent'=>(int)($data['post_parent']??0),'post_excerpt'=>(string)($data['post_excerpt']??''),'post_content'=>(string)($data['post_content']??'')]);return $id;}
function attachment_url_to_postid(string $url): int {return 0;}
function wp_check_filetype(string $file): array {return ['type'=>'image/jpeg'];}

require_once dirname(__DIR__,2).'/src/Backup/SiteBackupManifestService.php';
require_once dirname(__DIR__,2).'/src/Backup/SiteBackupManifestValidator.php';
require_once dirname(__DIR__,2).'/src/Backup/SiteBackupSnapshotCollector.php';
require_once dirname(__DIR__,2).'/src/Backup/SiteBackupPackageService.php';
require_once dirname(__DIR__,2).'/src/Backup/SiteBackupRestoreService.php';
require_once dirname(__DIR__,2).'/src/Backup/SiteBackupSecurityPolicy.php';
require_once dirname(__DIR__,2).'/src/Backup/SiteBackupRestoreCoordinator.php';

wp_mkdir_p($GLOBALS['b2_tmp'].'/uploads');
$GLOBALS['b2_posts'][9]=new WP_Post(['ID'=>9,'post_type'=>'page','post_title'=>'Hjem','post_name'=>'hjem','post_status'=>'publish','post_content'=>'<!-- ORIGINAL -->[hangar18_page_editor slug="hjem"]']);
$GLOBALS['b2_posts'][10]=new WP_Post(['ID'=>10,'post_type'=>'page','post_title'=>'Kontakt','post_name'=>'kontakt','post_status'=>'publish','post_content'=>'<p>KONTAKT ORIGINAL</p>']);
$GLOBALS['b2_options']['hangar18_manager_pages_v1']=['hjem'=>['ContentVersion'=>1,'Sections'=>[['Key'=>'original']]],'kontakt'=>['ContentVersion'=>1,'Sections'=>[['Key'=>'kontakt-original']]]];
$GLOBALS['b2_options']['hangar18_manager_page_versions_v1']=['hjem'=>[['Version'=>1]],'kontakt'=>[['Version'=>1]]];
$GLOBALS['b2_options']['hangar18_manager_active_menu']='main-original';
$GLOBALS['b2_options']['hangar18_manager_site_menus_v1']=['main'=>['Items'=>[['slug'=>'hjem'],['slug'=>'kontakt']]]];
$GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']=[
    'hjem'=>['SchemaVersion'=>2,'Sections'=>['grid-1'=>['SchemaVersion'=>2,'Desktop'=>['Margin'=>['X'=>4,'Y'=>6],'Gap'=>['X'=>18,'Y'=>20]],'Tablet'=>['InheritDesktop'=>true,'Margin'=>['X'=>4,'Y'=>6],'Gap'=>['X'=>18,'Y'=>20]],'Mobile'=>['InheritDesktop'=>false,'Margin'=>['X'=>2,'Y'=>3],'Gap'=>['X'=>10,'Y'=>11]]]]],
    'kontakt'=>['SchemaVersion'=>2,'Sections'=>['contact-1'=>['SchemaVersion'=>2,'Desktop'=>['Margin'=>['X'=>1,'Y'=>1],'Gap'=>['X'=>12,'Y'=>12]],'Tablet'=>['InheritDesktop'=>true,'Margin'=>['X'=>1,'Y'=>1],'Gap'=>['X'=>12,'Y'=>12]],'Mobile'=>['InheritDesktop'=>false,'Margin'=>['X'=>0,'Y'=>0],'Gap'=>['X'=>8,'Y'=>8]]]]],
];
$baselineLego=$GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2'];

SiteBackupSecurityPolicy::hardenStorage();
$packages=new SiteBackupPackageService();
$created=$packages->create('Baseline før ændring');
b2Assert(($created['BackupId']??'')==='H18-BACKUP-000001','First package must be H18-BACKUP-000001.');
$report=$packages->validate('H18-BACKUP-000001');
b2Assert(($report['Valid']??false)===true,'Fresh B2 package must validate.');
b2Assert(($report['Warnings']??[])===[],'Complete package should not have capability/payload warnings.');
if(class_exists(ZipArchive::class)){
    $zip=$packages->zipPath('H18-BACKUP-000001');
    b2Assert(is_file($zip),'ZIP export must exist when ZipArchive is available.');
    $zipReport=SiteBackupSecurityPolicy::inspectZip($zip);
    b2Assert(($zipReport['Entries']??0)>0,'Exported ZIP must pass security inspection.');
}

// Full restore roundtrip, including the complete LEGO option.
$GLOBALS['b2_posts'][9]->post_content='<!-- CHANGED -->';
$GLOBALS['b2_options']['hangar18_manager_pages_v1']['hjem']=['ContentVersion'=>99,'Sections'=>[['Key'=>'changed']]];
$GLOBALS['b2_options']['hangar18_manager_active_menu']='main-changed';
$GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']['hjem']['Sections']['grid-1']['Desktop']['Gap']['X']=99;
$GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']['kontakt']['Sections']['contact-1']['Desktop']['Gap']['X']=77;
$coordinator=new SiteBackupRestoreCoordinator($packages);
$plan=$coordinator->plan('H18-BACKUP-000001','full');
b2Assert(($plan['Executable']??false)===true,'Full restore dry-run must be executable.');
$result=$coordinator->restoreFull((string)$plan['Token']);
b2Assert(($result['SafetyBackupId']??'')==='H18-BACKUP-000002','Full restore must create safety backup before mutation.');
b2Assert(str_contains($GLOBALS['b2_posts'][9]->post_content,'ORIGINAL'),'Full restore must restore page content.');
b2Assert(($GLOBALS['b2_options']['hangar18_manager_pages_v1']['hjem']['ContentVersion']??0)===1,'Full restore must restore page editor state.');
b2Assert($GLOBALS['b2_options']['hangar18_manager_active_menu']==='main-original','Full restore must restore Hangar18 owned options.');
b2Assert(b2CanonicalEqual($GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2'],$baselineLego),'Full restore must restore the complete LEGO spacing option.');

// Selective restore only touches selected page/editor/version/LEGO ledger, not another page/menu.
$GLOBALS['b2_posts'][9]->post_content='<!-- HOME NEW -->';
$GLOBALS['b2_posts'][10]->post_content='<p>CONTACT MUST STAY NEW</p>';
$GLOBALS['b2_options']['hangar18_manager_pages_v1']['hjem']=['ContentVersion'=>55,'Sections'=>[['Key'=>'home-new']]];
$GLOBALS['b2_options']['hangar18_manager_pages_v1']['kontakt']=['ContentVersion'=>77,'Sections'=>[['Key'=>'contact-new']]];
$GLOBALS['b2_options']['hangar18_manager_active_menu']='menu-must-stay';
$GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']['hjem']['Sections']['grid-1']['Desktop']['Gap']['X']=55;
$GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']['kontakt']['Sections']['contact-1']['Desktop']['Gap']['X']=88;
$contactLegoMustStay=$GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']['kontakt'];
$planPage=$coordinator->plan('H18-BACKUP-000001','page','hjem');
b2Assert(($planPage['Executable']??false)===true,'Selective page dry-run must be executable.');
$pageResult=$coordinator->restorePage((string)$planPage['Token']);
b2Assert(($pageResult['SafetyBackupId']??'')==='H18-BACKUP-000003','Selective restore must create its own safety backup.');
b2Assert(($pageResult['LegoSpacingRestored']??false)===true,'Selective restore must report selected-page LEGO spacing restore.');
b2Assert(str_contains($GLOBALS['b2_posts'][9]->post_content,'ORIGINAL'),'Selective restore must restore selected page.');
b2Assert(str_contains($GLOBALS['b2_posts'][10]->post_content,'CONTACT MUST STAY NEW'),'Selective restore must not overwrite another page.');
b2Assert(($GLOBALS['b2_options']['hangar18_manager_pages_v1']['hjem']['ContentVersion']??0)===1,'Selective restore must restore selected page editor state.');
b2Assert(($GLOBALS['b2_options']['hangar18_manager_pages_v1']['kontakt']['ContentVersion']??0)===77,'Selective restore must preserve another page editor state.');
b2Assert($GLOBALS['b2_options']['hangar18_manager_active_menu']==='menu-must-stay','Selective restore must preserve menu option state.');
b2Assert(b2CanonicalEqual($GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']['hjem'],$baselineLego['hjem']),'Selective restore must restore only selected page LEGO state from package.');
b2Assert(b2CanonicalEqual($GLOBALS['b2_options']['hangar18_ultimate_designer_lego_spacing_v2']['kontakt'],$contactLegoMustStay),'Selective restore must preserve another page LEGO state.');

// Signed dry-run is state-bound; drift blocks execution before a new safety package/write.
$driftPlan=$coordinator->plan('H18-BACKUP-000001','page','hjem');
$GLOBALS['b2_posts'][9]->post_content='<!-- DRIFT AFTER PLAN -->';
$blocked=false;
try{$coordinator->restorePage((string)$driftPlan['Token']);}catch(RuntimeException $error){$blocked=str_contains($error->getMessage(),'ændret sig siden dry-run');}
b2Assert($blocked,'State drift after dry-run must block restore.');
$audit=$coordinator->audit(10);
b2Assert(str_contains((string)($audit[0]['Mode']??''),'failed'),'Failed restore must be audit logged.');

// Stale restore lock is recoverable, fresh lock remains authoritative in core engine.
$GLOBALS['b2_options']['hangar18_manager_site_backup_restore_lock_v1']=['Utc'=>'2020-01-01T00:00:00Z'];
$freshPlan=$coordinator->plan('H18-BACKUP-000001','page','hjem');
$staleResult=$coordinator->restorePage((string)$freshPlan['Token']);
b2Assert(!isset($GLOBALS['b2_options']['hangar18_manager_site_backup_restore_lock_v1']),'Stale lock must be cleared and final lock released.');
b2Assert(!empty($staleResult['SafetyBackupId']),'Restore after stale lock recovery must still safety-backup.');

$unsafe=false;
try{SiteBackupSecurityPolicy::assertManifestSafe(['Media'=>[['RelativePath'=>'2026/08/shell.php']]]);}catch(RuntimeException $error){$unsafe=true;}
b2Assert($unsafe,'Executable media path must be rejected.');

if(class_exists(ZipArchive::class)){
    $bad=$GLOBALS['b2_tmp'].'/bad.zip';
    $z=new ZipArchive();
    $z->open($bad,ZipArchive::CREATE|ZipArchive::OVERWRITE);
    $z->addFromString('media/2026/shell.php','<?php echo 1;');
    $z->close();
    $zipBlocked=false;
    try{SiteBackupSecurityPolicy::inspectZip($bad);}catch(RuntimeException $error){$zipBlocked=true;}
    b2Assert($zipBlocked,'Executable ZIP entry must be rejected before extraction.');
}

fwrite(STDOUT,"B2 package/export/full+selective restore roundtrip incl LEGO spacing: PASS\n");

function b2Cleanup(string $path): void
{
    if(!is_dir($path))return;
    foreach(array_diff(scandir($path)?:[],['.','..']) as $item){
        $child=$path.DIRECTORY_SEPARATOR.$item;
        if(is_dir($child)){b2Cleanup($child);}else{@unlink($child);}
    }
    @rmdir($path);
}
b2Cleanup($GLOBALS['b2_tmp']);
