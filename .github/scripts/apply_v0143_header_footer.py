from pathlib import Path
import json

ROOT = Path('.')

def read(path): return (ROOT / path).read_text(encoding='utf-8')
def write(path, text): (ROOT / path).write_text(text, encoding='utf-8')
def replace_once(text, old, new, label):
    if old not in text: raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)
def replace_span(text, start_marker, end_marker, new, label):
    start = text.find(start_marker)
    if start < 0: raise SystemExit(f'Missing start: {label}')
    end = text.find(end_marker, start)
    if end < 0: raise SystemExit(f'Missing end: {label}')
    return text[:start] + new + text[end:]

# Version + Footer converter registration.
path='clean/hangar18-manager/hangar18-manager.php'; s=read(path)
s=replace_once(s,' * Version: 0.1.42',' * Version: 0.1.43','plugin version')
s=replace_once(s,"define('H18_CLEAN_VERSION', '0.1.42');","define('H18_CLEAN_VERSION', '0.1.43');",'version constant')
s=replace_once(s,"require_once H18_CLEAN_DIR . 'src/Migration/LegacyHeaderConverter.php';\n","require_once H18_CLEAN_DIR . 'src/Migration/LegacyHeaderConverter.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/LegacyFooterConverter.php';\n",'footer require')
s=replace_once(s,"    \\Hangar18\\Clean\\Migration\\LegacyHeaderConverter::register();\n","    \\Hangar18\\Clean\\Migration\\LegacyHeaderConverter::register();\n    \\Hangar18\\Clean\\Migration\\LegacyFooterConverter::register();\n",'footer register')
write(path,s)

# Header parity: rerun migration, deterministic reference geometry, validated menu, media-library logo discovery.
path='clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php'; s=read(path)
s=s.replace("h18_vd_legacy_header_converted_v0142","h18_vd_legacy_header_converted_v0143")
s=s.replace("h18_vd_legacy_header_status_v0142","h18_vd_legacy_header_status_v0143")
s=s.replace("v0.1.42","v0.1.43")
s=s.replace("['sticky' => false, 'overlay' => false, 'contentWidth' => 2400]","['sticky' => false, 'overlay' => false, 'contentWidth' => 1728]")

new_reference=r'''    public static function buildScreenshotReferenceModel(int $menuId, int $logoMediaId = 0, string $logoUrl = ''): array
    {
        $rowsDesktop = 15;
        $rowsMobile = 14;
        $brand = 'Aalborg Kaserners Veteran Panser- og Køretøjsforening';
        $nodes = [];
        $nodes[] = self::node('section-header-reference-v0143','section','',10,
            self::geometry([6,0,108,$rowsDesktop],[6,0,108,$rowsDesktop],[0,0,120,$rowsMobile]),
            ['background'=>'#30382a','radius'=>0,'padding'=>0,'minHeightRows'=>$rowsDesktop,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('container-header-reference-v0143','container','section-header-reference-v0143',10,
            self::geometry([0,0,120,$rowsDesktop],[0,0,120,$rowsDesktop],[0,0,120,$rowsMobile]),
            ['background'=>'#30382a','radius'=>0,'padding'=>0,'minHeightRows'=>$rowsDesktop,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('image-header-reference-logo-v0143','image','container-header-reference-v0143',10,
            self::geometry([0,1,7,13],[0,1,7,13],[0,1,20,12]),
            ['mediaId'=>max(0,$logoMediaId),'url'=>esc_url_raw($logoUrl),'alt'=>$brand,'fit'=>'contain','imageAlignX'=>'left','imageAlignY'=>'center','boxBackground'=>'#30382a','boxTransparent'=>true,'focalX'=>50,'focalY'=>50,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('text-header-reference-brand-v0143','text','container-header-reference-v0143',20,
            self::geometry([8,4,28,7],[8,4,30,7],[20,3,72,8]),
            ['heading'=>'','headingLevel'=>'h2','text'=>$brand,'align'=>'left','background'=>'#30382a','backgroundTransparent'=>true,'textColor'=>'#f2f0e8','headingColor'=>'#f2f0e8','padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>19,'fontWeight'=>700,'lineHeight'=>1.18,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('menu-header-reference-primary-v0143','menu','container-header-reference-v0143',30,
            self::geometry([72,4,48,7],[68,4,52,7],[95,3,25,8]),
            ['menuId'=>max(0,$menuId),'orientation'=>'horizontal','align'=>'right','mobileMode'=>'hamburger','textColor'=>'#f2f0e8','hoverTextColor'=>'#c3ae83','activeTextColor'=>'#c3ae83','background'=>'#30382a','backgroundTransparent'=>true,'fontSize'=>17,'fontWeight'=>600,'menuGap'=>22,'paddingX'=>6,'paddingY'=>8,'radius'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        return LayoutModel::normalize(['schemaVersion'=>LayoutModel::SCHEMA,'units'=>LayoutModel::UNITS,'rowPx'=>LayoutModel::ROW_PX,'nodes'=>$nodes]);
    }

'''
s=replace_span(s,'    public static function buildScreenshotReferenceModel(', '    /** @param array<string,mixed> $design @return array{mediaId:int,url:string,source:string} */',new_reference,'reference model')

new_logo=r'''    /** @param array<string,mixed> $design @return array{mediaId:int,url:string,source:string} */
    private static function resolveLogo(array $design): array
    {
        $url = esc_url_raw((string) ($design['LogoUrl'] ?? ''));
        $mediaId = max(0, (int) ($design['LogoMediaId'] ?? 0));
        if ($url !== '') { return ['mediaId'=>$mediaId,'url'=>$url,'source'=>'legacy-header']; }
        if (function_exists('get_theme_mod')) {
            $id=absint(get_theme_mod('custom_logo',0)); $u=$id>0?wp_get_attachment_url($id):false;
            if ($u) return ['mediaId'=>$id,'url'=>esc_url_raw((string)$u),'source'=>'wordpress-custom-logo'];
        }
        $siteIconId=absint(get_option('site_icon',0)); $siteIconUrl=$siteIconId>0?wp_get_attachment_url($siteIconId):false;
        if ($siteIconUrl) return ['mediaId'=>$siteIconId,'url'=>esc_url_raw((string)$siteIconUrl),'source'=>'wordpress-site-icon'];

        $best=['score'=>0,'mediaId'=>0,'url'=>''];
        $attachments=get_posts(['post_type'=>'attachment','post_status'=>'inherit','post_mime_type'=>'image','posts_per_page'=>200,'orderby'=>'date','order'=>'DESC','suppress_filters'=>true]);
        foreach ((array)$attachments as $attachment) {
            if (!$attachment instanceof \WP_Post) continue;
            $file=(string)get_post_meta($attachment->ID,'_wp_attached_file',true);
            $hay=sanitize_title((string)$attachment->post_title.' '.basename($file).' '.(string)$attachment->guid);
            $score=0;
            foreach (['logo'=>70,'emblem'=>55,'veteran'=>25,'kaserne'=>25,'aalborg'=>20,'panser'=>15] as $needle=>$points) if (str_contains($hay,$needle)) $score+=$points;
            foreach (['banner'=>80,'hero'=>70,'topbanner'=>90,'header-billede'=>60] as $needle=>$points) if (str_contains($hay,$needle)) $score-=$points;
            $meta=wp_get_attachment_metadata($attachment->ID);
            if (is_array($meta) && !empty($meta['width']) && !empty($meta['height'])) {
                $ratio=(float)$meta['width']/max(1,(float)$meta['height']);
                if ($ratio>=0.75 && $ratio<=1.25) $score+=25;
                elseif ($ratio>2.0) $score-=25;
            }
            $u=wp_get_attachment_url($attachment->ID);
            if ($u && $score>$best['score']) $best=['score'=>$score,'mediaId'=>(int)$attachment->ID,'url'=>esc_url_raw((string)$u)];
        }
        if ($best['score']>=40) return ['mediaId'=>$best['mediaId'],'url'=>$best['url'],'source'=>'media-library-match'];
        if (function_exists('get_site_icon_url')) {
            $u=(string)get_site_icon_url(512,''); if ($u!=='') return ['mediaId'=>0,'url'=>esc_url_raw($u),'source'=>'wordpress-site-icon-url'];
        }
        return ['mediaId'=>0,'url'=>'','source'=>'not-found'];
    }

'''
s=replace_span(s,'    /** @param array<string,mixed> $design @return array{mediaId:int,url:string,source:string} */\n    private static function resolveLogo', '    /** @param array<string,mixed> $model @return array<string,int> */',new_logo,'logo resolver')

new_menu=r'''    private static function legacyMenuId(): int
    {
        $defs = self::referenceMenuDefinitions();
        $saved = absint(get_option(self::LEGACY_ACTIVE_MENU_OPTION, 0));
        $locations = get_nav_menu_locations();
        $primary = is_array($locations) ? absint($locations['primary'] ?? 0) : 0;
        $bestId=0; $bestScore=-1;
        foreach ((array) wp_get_nav_menus() as $menu) {
            $id=(int)($menu->term_id ?? 0); if ($id<=0) continue;
            $items=wp_get_nav_menu_items($id); $items=is_array($items)?$items:[];
            $matched=[]; $score=0;
            foreach ($items as $item) {
                $titleSlug=sanitize_title(wp_strip_all_tags((string)$item->title));
                $pageSlug='';
                if (($item->object ?? '')==='page' && !empty($item->object_id)) { $p=get_post((int)$item->object_id); if ($p instanceof \WP_Post) $pageSlug=sanitize_title((string)$p->post_name); }
                foreach ($defs as $def) {
                    if (isset($matched[$def['slug']])) continue;
                    if ($pageSlug===$def['slug'] || $titleSlug===sanitize_title($def['title']) || in_array($titleSlug,$def['aliases'],true)) { $matched[$def['slug']]=true; $score+=10; }
                }
            }
            if (count($items)===7) $score+=10;
            $name=sanitize_title((string)($menu->name ?? ''));
            if (str_contains($name,'hangar18') || str_contains($name,'hoved') || str_contains($name,'main')) $score+=5;
            if ($id===$saved) $score+=2; if ($id===$primary) $score+=3;
            if ($score>$bestScore) { $bestScore=$score; $bestId=$id; }
        }
        if ($bestId>0 && $bestScore>=45) return $bestId;
        return self::ensureReferenceMenu($defs);
    }

    /** @return array<int,array{slug:string,title:string,aliases:array<int,string>}> */
    private static function referenceMenuDefinitions(): array
    {
        return [
            ['slug'=>'hjem','title'=>'Hjem','aliases'=>['hjem','home']],
            ['slug'=>'events','title'=>'Events','aliases'=>['events','event']],
            ['slug'=>'koeretoejer-og-materiel','title'=>'Køretøjer','aliases'=>['koeretoejer','koeretoejer-og-materiel','koretojer']],
            ['slug'=>'billedgalleri','title'=>'Billedgalleri','aliases'=>['billedgalleri','galleri']],
            ['slug'=>'om-foreningen','title'=>'Om','aliases'=>['om','om-foreningen']],
            ['slug'=>'bliv-medlem','title'=>'Bliv medlem','aliases'=>['bliv-medlem']],
            ['slug'=>'kontakt','title'=>'Kontakt','aliases'=>['kontakt']],
        ];
    }

    private static function ensureReferenceMenu(array $defs): int
    {
        $menu=wp_get_nav_menu_object('Visual Designer Hovedmenu');
        if (!$menu) {
            $created=wp_create_nav_menu('Visual Designer Hovedmenu');
            if (is_wp_error($created)) throw new \RuntimeException('Kunne ikke oprette Visual Designer Hovedmenu: '.$created->get_error_message());
            $menu=wp_get_nav_menu_object((int)$created);
        }
        $menuId=(int)($menu->term_id ?? 0); if ($menuId<=0) throw new \RuntimeException('Visual Designer Hovedmenu fik ikke et gyldigt ID.');
        $items=wp_get_nav_menu_items($menuId); if (!is_array($items) || count($items)<count($defs)) {
            foreach ((array)$items as $item) wp_delete_post((int)$item->ID,true);
            $position=1;
            foreach ($defs as $def) {
                $page=get_page_by_path($def['slug'],OBJECT,'page');
                $args=['menu-item-title'=>$def['title'],'menu-item-position'=>$position++,'menu-item-status'=>'publish'];
                if ($page instanceof \WP_Post) $args += ['menu-item-object-id'=>(int)$page->ID,'menu-item-object'=>'page','menu-item-type'=>'post_type'];
                else $args += ['menu-item-type'=>'custom','menu-item-url'=>home_url('/'.$def['slug'].'/')];
                $result=wp_update_nav_menu_item($menuId,0,$args);
                if (is_wp_error($result)) throw new \RuntimeException('Kunne ikke opbygge Visual Designer Hovedmenu: '.$result->get_error_message());
            }
        }
        return $menuId;
    }

'''
s=replace_span(s,'    private static function legacyMenuId(): int\n', '    private static function legacyShellHeader(): string\n',new_menu,'menu resolver')
write(path,s)

# Footer converter.
footer=r'''<?php

declare(strict_types=1);

namespace Hangar18\Clean\Migration;

use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Model\TemplateLayoutModel;

final class LegacyFooterConverter
{
    public const MIGRATION_OPTION='h18_vd_legacy_footer_converted_v0143';
    public const STATUS_OPTION='h18_vd_legacy_footer_status_v0143';
    private const LEGACY_DESIGN_OPTION='hangar18_manager_header_design_v25';
    private const TARGET_TEMPLATE_ID='footer-standard-v1';
    private const FOOTER_START='<!-- HANGAR18-FOOTER-START -->';
    private const FOOTER_END='<!-- HANGAR18-FOOTER-END -->';

    public static function register(): void { add_action('admin_init',[self::class,'maybeMigrate'],5); }
    public static function maybeMigrate(): void {
        if (!current_user_can('edit_theme_options') || get_option(self::MIGRATION_OPTION,false)) return;
        try { self::convert(false); } catch (\Throwable $e) { update_option(self::STATUS_OPTION,['status'=>'error','checkedUtc'=>gmdate('c'),'message'=>$e->getMessage()],false); }
    }
    /** @return array<string,mixed> */
    public static function convert(bool $force=true): array {
        if (!current_user_can('edit_theme_options')) throw new \RuntimeException('Ingen adgang til Footer-konvertering.');
        if (!$force && get_option(self::MIGRATION_OPTION,false)) return self::diagnosticStatus();
        $source=self::legacyShellFooter();
        $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];
        if ($source['html']!=='') { $model=self::buildModelFromLegacyFooter($source['html'],$design); $kind='legacy-footer-block'; $note='Automatisk konvertering fra fundet legacy Footer · v0.1.43'; }
        else { $model=self::buildReferenceFooterModel($design); $kind='design-reference-fallback'; $note='Footer-reference fallback · v0.1.43'; }
        $counts=self::nodeCounts($model);
        if (($counts['section']??0)<1 || ($counts['container']??0)<1 || ($counts['text']??0)<1) throw new \RuntimeException('Footer-konverteringen gav ikke Sektion/Kasse/Tekst.');
        TemplateLayoutModel::ensureMigrated();
        $id=TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID,'footer')?self::TARGET_TEMPLATE_ID:TemplateLayoutModel::defaultId('footer');
        if ($id==='') $id=TemplateLayoutModel::create('footer','Footer – Standard');
        $version=TemplateLayoutModel::saveVersion($id,$model,['contentWidth'=>1728],get_current_user_id(),$note);
        TemplateLayoutModel::rename($id,'Footer – Standard'); TemplateLayoutModel::setActive($id,true); TemplateLayoutModel::setDefault('footer',$id);
        $result=['status'=>'success','convertedUtc'=>gmdate('c'),'templateId'=>$id,'templateVersion'=>$version,'source'=>$kind,'legacyFooterFound'=>$source['html']!=='','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'footerWidthPercent'=>self::footerWidth($design),'nodeCounts'=>$counts,'digest'=>LayoutModel::structuralDigest($model)];
        update_option(self::STATUS_OPTION,$result,false); update_option(self::MIGRATION_OPTION,$result,false); return $result;
    }
    /** @return array<string,mixed> */
    public static function diagnosticStatus(): array {
        $source=self::legacyShellFooter(); $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];
        TemplateLayoutModel::ensureMigrated(); $id=TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID,'footer')?self::TARGET_TEMPLATE_ID:TemplateLayoutModel::defaultId('footer');
        $model=$id!==''?TemplateLayoutModel::model($id):LayoutModel::empty(); $last=get_option(self::STATUS_OPTION,[]); $last=is_array($last)?$last:[];
        return ['legacyFooterFound'=>$source['html']!=='','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'footerWidthPercent'=>self::footerWidth($design),'targetTemplateId'=>$id,'targetVersion'=>$id!==''?TemplateLayoutModel::version($id):0,'targetNodeCounts'=>self::nodeCounts($model),'lastConversion'=>$last];
    }
    /** @param array<string,mixed> $design */
    public static function buildModelFromLegacyFooter(string $html,array $design=[]): array {
        $pct=self::footerWidth($design); [$x,$w]=self::centredUnits($pct); $rows=12;
        $primary=self::color($design['PrimaryColor']??'#30382a','#30382a'); $light=self::color($design['LightTextColor']??'#f2f0e8','#f2f0e8');
        $inner=$html; if (preg_match('/<footer\b[^>]*>(.*?)<\/footer>/is',$html,$m)) $inner=(string)$m[1];
        $inner=preg_replace('/<style\b[^>]*>.*?<\/style>/is','',$inner)??$inner; $inner=preg_replace('/<script\b[^>]*>.*?<\/script>/is','',$inner)??$inner;
        $text=trim(preg_replace('/\s+/u',' ',wp_strip_all_tags($inner))??''); if ($text==='') $text='Aalborg Kaserners Veteran Panser- og Køretøjsforening';
        return self::model($x,$w,$rows,$primary,$light,$text);
    }
    /** @param array<string,mixed> $design */
    public static function buildReferenceFooterModel(array $design=[]): array {
        $pct=self::footerWidth($design); if ($pct>=100) $pct=90; [$x,$w]=self::centredUnits($pct);
        return self::model($x,$w,12,self::color($design['PrimaryColor']??'#30382a','#30382a'),self::color($design['LightTextColor']??'#f2f0e8','#f2f0e8'),'Aalborg Kaserners Veteran Panser- og Køretøjsforening');
    }
    private static function model(int $x,int $w,int $rows,string $bg,string $fg,string $text): array {
        $geometry=self::geometry([$x,0,$w,$rows],[$x,0,$w,$rows],[0,0,120,$rows]);
        $nodes=[
            self::node('section-footer-v0143','section','',10,$geometry,['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('container-footer-v0143','container','section-footer-v0143',10,self::geometry([0,0,120,$rows],[0,0,120,$rows],[0,0,120,$rows]),['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-v0143','text','container-footer-v0143',10,self::geometry([4,2,112,8],[4,2,112,8],[5,2,110,8]),['heading'=>'','headingLevel'=>'h2','text'=>$text,'align'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>1.4,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
        ];
        return LayoutModel::normalize(['schemaVersion'=>LayoutModel::SCHEMA,'units'=>LayoutModel::UNITS,'rowPx'=>LayoutModel::ROW_PX,'nodes'=>$nodes]);
    }
    /** @return array{html:string,pageId:int,pageTitle:string} */
    private static function legacyShellFooter(): array {
        $pages=[]; $home=get_page_by_path('hjem',OBJECT,'page'); if ($home instanceof \WP_Post) $pages[]=$home;
        foreach (get_pages(['sort_column'=>'menu_order,post_title','sort_order'=>'ASC','post_status'=>['publish','draft','pending','private','future']]) as $p) if ($p instanceof \WP_Post && (!$pages || (int)$pages[0]->ID!==(int)$p->ID)) $pages[]=$p;
        foreach ($pages as $p) { $c=(string)$p->post_content; $a=strpos($c,self::FOOTER_START); $b=strpos($c,self::FOOTER_END); if ($a===false||$b===false||$b<=$a) continue; $b+=strlen(self::FOOTER_END); return ['html'=>trim(substr($c,$a,$b-$a)),'pageId'=>(int)$p->ID,'pageTitle'=>(string)$p->post_title]; }
        return ['html'=>'','pageId'=>0,'pageTitle'=>''];
    }
    private static function footerWidth(array $design): int { $v=$design['FooterWidthPercent']??100; return is_numeric($v)?max(40,min(100,(int)$v)):100; }
    private static function color($v,string $fallback): string { $v=strtolower((string)$v); return preg_match('/^#[0-9a-f]{6}$/',$v)?$v:$fallback; }
    /** @return array{0:int,1:int} */ private static function centredUnits(int $pct): array { $w=max(1,min(120,(int)round(120*$pct/100))); return [(int)floor((120-$w)/2),$w]; }
    private static function geometry(array $d,array $l,array $m): array { return ['desktop'=>['x'=>$d[0],'y'=>$d[1],'w'=>$d[2],'h'=>$d[3]],'laptop'=>['x'=>$l[0],'y'=>$l[1],'w'=>$l[2],'h'=>$l[3],'inheritDesktop'=>false],'tablet'=>['x'=>$l[0],'y'=>$l[1],'w'=>$l[2],'h'=>$l[3],'inheritDesktop'=>false],'mobile'=>['x'=>$m[0],'y'=>$m[1],'w'=>$m[2],'h'=>$m[3],'inheritDesktop'=>false]]; }
    private static function node(string $id,string $type,string $parentId,int $order,array $geometry,array $props): array { return compact('id','type','parentId','order','geometry','props'); }
    private static function nodeCounts(array $model): array { $c=['section'=>0,'container'=>0,'text'=>0,'image'=>0,'menu'=>0,'button'=>0]; foreach (($model['nodes']??[]) as $n) { $t=(string)($n['type']??''); if (isset($c[$t])) $c[$t]++; } return $c; }
    private function __construct() {}
}
'''
write('clean/hangar18-manager/src/Migration/LegacyFooterConverter.php',footer)

# Global designer: Footer diagnostics and re-convert action.
path='clean/hangar18-manager/src/Admin/GlobalDesignerController.php'; s=read(path)
s=replace_once(s,'use Hangar18\\Clean\\Migration\\LegacyHeaderConverter;\n','use Hangar18\\Clean\\Migration\\LegacyHeaderConverter;\nuse Hangar18\\Clean\\Migration\\LegacyFooterConverter;\n','footer use')
s=replace_once(s,"    private const CONVERT_ACTION = 'h18_clean_legacy_header_convert';\n","    private const CONVERT_ACTION = 'h18_clean_legacy_header_convert';\n    private const FOOTER_CONVERT_ACTION = 'h18_clean_legacy_footer_convert';\n",'footer action const')
s=replace_once(s,"    private const NONCE_CONVERT = 'h18_clean_legacy_header_convert';\n","    private const NONCE_CONVERT = 'h18_clean_legacy_header_convert';\n    private const NONCE_FOOTER_CONVERT = 'h18_clean_legacy_footer_convert';\n",'footer nonce')
s=replace_once(s,"        add_action('admin_post_' . self::CONVERT_ACTION, [self::class, 'convertLegacyHeader']);\n","        add_action('admin_post_' . self::CONVERT_ACTION, [self::class, 'convertLegacyHeader']);\n        add_action('admin_post_' . self::FOOTER_CONVERT_ACTION, [self::class, 'convertLegacyFooter']);\n",'footer action hook')
s=replace_once(s,"        if ($part === 'header') { self::renderLegacyHeaderConversion(); }\n","        if ($part === 'header') { self::renderLegacyHeaderConversion(); }\n        if ($part === 'footer') { self::renderLegacyFooterConversion(); }\n",'footer diagnostic render')
anchor='    public static function convertLegacyHeader(): void\n'
footer_methods=r'''    private static function renderLegacyFooterConversion(): void
    {
        $status=LegacyFooterConverter::diagnosticStatus(); $counts=is_array($status['targetNodeCounts']??null)?$status['targetNodeCounts']:[]; $last=is_array($status['lastConversion']??null)?$status['lastConversion']:[];
        echo '<section class="h18-manager-card h18-global-conversion"><h2>Gammel Footer → Visual Designer</h2>';
        echo '<p class="description">Footer læses fra den gamle HANGAR18-FOOTER-blok. Hvis den ikke længere findes, laves en tydeligt markeret design-fallback til første parity-test. Hver konvertering gemmes som ny Footer-version.</p><table class="widefat striped"><tbody>';
        echo '<tr><th>Legacy Footer-blok</th><td>'.(!empty($status['legacyFooterFound'])?'Fundet':'Ikke fundet · fallback bruges').'</td></tr>';
        echo '<tr><th>Kildeside</th><td>'.esc_html((string)($status['sourcePageTitle']??'')).' · ID '.esc_html((string)($status['sourcePageId']??0)).'</td></tr>';
        echo '<tr><th>FooterWidthPercent</th><td>'.esc_html((string)($status['footerWidthPercent']??100)).'%</td></tr>';
        echo '<tr><th>Footer – Standard nu</th><td>v'.esc_html((string)($status['targetVersion']??0)).' · Sektion '.esc_html((string)($counts['section']??0)).' · Kasse '.esc_html((string)($counts['container']??0)).' · Tekst '.esc_html((string)($counts['text']??0)).'</td></tr>';
        if ($last) echo '<tr><th>Seneste konvertering</th><td>'.esc_html((string)($last['source']??$last['status']??'')).' · '.esc_html((string)($last['convertedUtc']??$last['checkedUtc']??'')).(!empty($last['message'])?' · '.esc_html((string)$last['message']):'').'</td></tr>';
        echo '</tbody></table><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">'; wp_nonce_field(self::NONCE_FOOTER_CONVERT); echo '<input type="hidden" name="action" value="'.esc_attr(self::FOOTER_CONVERT_ACTION).'"><button class="button button-primary" type="submit">Konvertér gammel Footer igen</button></form></section>';
    }

    public static function convertLegacyFooter(): void
    {
        self::guard(); check_admin_referer(self::NONCE_FOOTER_CONVERT);
        try { $r=LegacyFooterConverter::convert(true); $c=is_array($r['nodeCounts']??null)?$r['nodeCounts']:[]; $m='Footer konverteret som v'.(int)($r['templateVersion']??0).' fra '.(string)($r['source']??'ukendt kilde').'. Sektion '.(int)($c['section']??0).', Kasse '.(int)($c['container']??0).', Tekst '.(int)($c['text']??0).'.'; self::redirect('footer',(string)($r['templateId']??''),'success',$m); }
        catch (\Throwable $e) { self::redirect('footer',TemplateLayoutModel::defaultId('footer'),'error','Footer-konvertering fejlede: '.$e->getMessage()); }
    }

'''
s=replace_once(s,anchor,footer_methods+anchor,'footer methods')
write(path,s)

# Model QA.
path='.github/scripts/v0125_model_qa.php'; s=read(path)
s=replace_once(s,"require_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php';\n","require_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php';\nrequire_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/LegacyFooterConverter.php';\n",'footer qa require')
s=replace_once(s,"use Hangar18\\Clean\\Migration\\LegacyHeaderConverter;\n","use Hangar18\\Clean\\Migration\\LegacyHeaderConverter;\nuse Hangar18\\Clean\\Migration\\LegacyFooterConverter;\n",'footer qa use')
old='echo "Visual Designer Manager 0.1.42 model QA PASS\\n";'
qa=r'''$headerRef = LegacyHeaderConverter::buildScreenshotReferenceModel(77, 55, 'https://example.test/logo.png');
$hBy=[]; foreach ($headerRef['nodes'] as $n) { $hBy[$n['type']][]=$n; }
vdAssert(($hBy['section'][0]['props']['background']??'')==='#30382a','0.1.43 Header Section must be dark green.');
vdAssert(($hBy['container'][0]['props']['background']??'')==='#30382a','0.1.43 Header inner Container must be dark green.');
vdAssert((int)($hBy['text'][0]['geometry']['desktop']['y']??-1)===4,'Header brand must be vertically centred by explicit Y.');
vdAssert((int)($hBy['menu'][0]['geometry']['desktop']['y']??-1)===4,'Header menu must be vertically centred by explicit Y.');
$footerRef=LegacyFooterConverter::buildModelFromLegacyFooter('<!-- HANGAR18-FOOTER-START --><footer class="h18-site-footer">© Aalborg Kaserners Veteran Panser- og Køretøjsforening</footer><!-- HANGAR18-FOOTER-END -->',['FooterWidthPercent'=>90,'PrimaryColor'=>'#30382a','LightTextColor'=>'#f2f0e8']);
$fBy=[]; foreach ($footerRef['nodes'] as $n) { $fBy[$n['type']][]=$n; }
vdAssert(count($fBy['section']??[])===1,'Footer conversion must create Section.');
vdAssert(count($fBy['container']??[])===1,'Footer conversion must create Container.');
vdAssert(count($fBy['text']??[])===1,'Footer conversion must create Text.');
vdAssert((int)($fBy['section'][0]['geometry']['desktop']['x']??-1)===6,'90 percent Footer must center at X=6.');
vdAssert((int)($fBy['section'][0]['geometry']['desktop']['w']??-1)===108,'90 percent Footer must be 108/120 units.');
vdAssert(str_contains((string)($fBy['text'][0]['props']['text']??''),'Aalborg Kaserners'),'Footer text was not extracted from legacy block.');

echo "Visual Designer Manager 0.1.43 model QA PASS\\n";'''
s=replace_once(s,old,qa,'qa tail')
write(path,s)

# Release metadata.
path='clean/hangar18-manager/release-history.json'; hist=json.loads(read(path))
if not hist or hist[0].get('version')!='0.1.43':
    hist.insert(0,{'version':'0.1.43','date':'2026-08-29','items':['Header Desktop parity: mørkegrøn Section og Kasse, eksplicit vertikal placering af brand/menu og 1728 px max referencebredde.','Header menuvalidering matcher de syv kendte Hangar18-menupunkter; en dedikeret Visual Designer Hovedmenu oprettes kun hvis ingen eksisterende menu matcher.','Header logo-søgning udvidet til WordPress-mediebiblioteket med logo/emblem-kriterier og frasortering af banner/hero-billeder.','Footer-konvertering til Footer – Standard læser eksisterende HANGAR18-FOOTER-blok og FooterWidthPercent.','Footer har diagnose og Konvertér gammel Footer igen; fallback er tydeligt markeret hvis legacy Footer ikke findes.','Theme Shell forbliver OFF; Header og Footer afventer brugerens parity-QA.']})
write(path,json.dumps(hist,ensure_ascii=False,indent=2)+'\n')
write('clean-release-notes.html','<h4>0.1.43</h4><ul><li><strong>Header parity:</strong> mørkegrøn flade, vertikalt centreret brand/menu og 1728 px max referencebredde.</li><li><strong>Menu:</strong> validerer mod Hjem, Events, Køretøjer, Billedgalleri, Om, Bliv medlem og Kontakt; Sample Page-menu vælges ikke længere som fallback.</li><li><strong>Logo:</strong> søger også mediebiblioteket efter sandsynligt logo/emblem.</li><li><strong>Footer:</strong> første non-destruktive konvertering til Footer – Standard fra legacy Footer-blok, med diagnose og genkonverteringsknap.</li><li><strong>Sikkerhed:</strong> Theme Shell forbliver OFF indtil Header/Footer parity er QA PASS.</li></ul>')
write('docs/v0143-status.md','# Visual Designer Manager 0.1.43 – implementation status\n\n- Header Desktop parity pass 2: source implemented, awaiting user QA.\n- Header inner Container uses #30382A so editor preview no longer hides the dark bar.\n- Header brand/menu use explicit vertical geometry.\n- Header menu resolver validates the seven Hangar18 reference items and can create a dedicated Visual Designer Hovedmenu if necessary.\n- Header logo resolver scans the WordPress media library if legacy/custom-logo/site-icon sources are missing.\n- Footer – Standard first conversion added from HANGAR18-FOOTER block and FooterWidthPercent.\n- Footer conversion is observable and repeatable; missing legacy source uses a clearly labelled fallback.\n- Theme Shell remains OFF.\n')
print('Visual Designer Manager 0.1.43 patch applied')
