<?php

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
        if ($source['html']==='') {
            throw new \RuntimeException('Den gamle Manager-Footer blev ikke fundet mellem HANGAR18-FOOTER-START/END på Hjem eller andre WordPress-sider. Ingen Footer er gættet eller oprettet automatisk.');
        }
        $model=self::buildModelFromLegacyFooter($source['html'],$design);
        $kind='legacy-manager-shell-footer';
        $note='Automatisk konvertering fra gammel Manager shell/Footer · v0.1.43';
        $counts=self::nodeCounts($model);
        if (($counts['section']??0)<1 || ($counts['container']??0)<1 || ($counts['text']??0)<1) throw new \RuntimeException('Footer-konverteringen gav ikke Sektion/Kasse/Tekst.');
        TemplateLayoutModel::ensureMigrated();
        $id=TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID,'footer')?self::TARGET_TEMPLATE_ID:TemplateLayoutModel::defaultId('footer');
        if ($id==='') $id=TemplateLayoutModel::create('footer','Footer – Standard');
        $version=TemplateLayoutModel::saveVersion($id,$model,['contentWidth'=>1728],get_current_user_id(),$note);
        TemplateLayoutModel::rename($id,'Footer – Standard'); TemplateLayoutModel::setActive($id,true); TemplateLayoutModel::setDefault('footer',$id);
        $result=['status'=>'success','convertedUtc'=>gmdate('c'),'templateId'=>$id,'templateVersion'=>$version,'source'=>$kind,'legacyFooterFound'=>$source['html']!=='','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>hash('sha256',$source['html']),'sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'nodeCounts'=>$counts,'digest'=>LayoutModel::structuralDigest($model)];
        update_option(self::STATUS_OPTION,$result,false); update_option(self::MIGRATION_OPTION,$result,false); return $result;
    }
    /** @return array<string,mixed> */
    public static function diagnosticStatus(): array {
        $source=self::legacyShellFooter(); $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];
        TemplateLayoutModel::ensureMigrated(); $id=TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID,'footer')?self::TARGET_TEMPLATE_ID:TemplateLayoutModel::defaultId('footer');
        $model=$id!==''?TemplateLayoutModel::model($id):LayoutModel::empty(); $last=get_option(self::STATUS_OPTION,[]); $last=is_array($last)?$last:[];
        return ['legacyFooterFound'=>$source['html']!=='','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>$source['html']!==''?hash('sha256',$source['html']):'','sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'targetTemplateId'=>$id,'targetVersion'=>$id!==''?TemplateLayoutModel::version($id):0,'targetNodeCounts'=>self::nodeCounts($model),'lastConversion'=>$last];
    }
    /** @param array<string,mixed> $design */
    public static function buildModelFromLegacyFooter(string $html,array $design=[]): array {
        $pct=self::footerWidth($design); [$x,$w]=self::centredUnits($pct); $rows=12;
        $primary=self::color($design['PrimaryColor']??'#30382a','#30382a');
        $light=self::color($design['LightTextColor']??'#f2f0e8','#f2f0e8');

        // The legacy block itself is authoritative. Use any explicit colors it
        // carries before falling back to the old HeaderDesign token values.
        if (preg_match('/background(?:-color)?\s*:\s*(#[0-9a-fA-F]{6})/i',$html,$m)) {
            $primary=strtolower((string)$m[1]);
        }
        if (preg_match('/(?:^|[;"\'])\s*color\s*:\s*(#[0-9a-fA-F]{6})/i',$html,$m)) {
            $light=strtolower((string)$m[1]);
        }

        $inner=$html;
        if (preg_match('/<footer\b[^>]*>(.*?)<\/footer>/is',$html,$m)) $inner=(string)$m[1];
        $inner=preg_replace('/<style\b[^>]*>.*?<\/style>/is','',$inner)??$inner;
        $inner=preg_replace('/<script\b[^>]*>.*?<\/script>/is','',$inner)??$inner;

        // Preserve the actual visible lines from the old Footer instead of a
        // hard-coded replacement string. Links retain their visible labels.
        $textHtml=preg_replace('/<\/?(?:p|div|section|li|ul|ol|nav|h[1-6])\b[^>]*>/i',"\n",$inner)??$inner;
        $textHtml=preg_replace('/<br\s*\/?>/i',"\n",$textHtml)??$textHtml;
        $text=html_entity_decode(strip_tags($textHtml),ENT_QUOTES|ENT_HTML5,'UTF-8');
        $lines=[];
        foreach (preg_split('/\R+/u',$text) ?: [] as $line) {
            $line=trim(preg_replace('/\s+/u',' ',$line)??'');
            if ($line!=='' && !in_array($line,$lines,true)) $lines[]=$line;
        }
        $text=implode("\n",$lines);
        if ($text==='') {
            throw new \RuntimeException('Legacy Footer-blokken blev fundet, men den indeholder ingen synlig tekst, som kan konverteres.');
        }

        $align=preg_match('/text-align\s*:\s*(left|right|center)/i',$html,$m)?strtolower((string)$m[1]):'center';
        $geometry=self::geometry([$x,0,$w,$rows],[$x,0,$w,$rows],[0,0,120,$rows]);
        $nodes=[
            self::node('section-footer-v0143','section','',10,$geometry,['background'=>$primary,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('container-footer-v0143','container','section-footer-v0143',10,self::geometry([0,0,120,$rows],[0,0,120,$rows],[0,0,120,$rows]),['background'=>$primary,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-v0143','text','container-footer-v0143',20,self::geometry([4,2,112,8],[4,2,112,8],[5,2,110,8]),['heading'=>'','headingLevel'=>'h2','text'=>$text,'align'=>$align,'background'=>$primary,'backgroundTransparent'=>true,'textColor'=>$light,'headingColor'=>$light,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>1.4,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
        ];

        // Preserve an actual image found in the legacy Footer as a canonical
        // Billede element. Media ID is resolved at runtime when WordPress can.
        if (preg_match('/<img\b[^>]*src=["\']([^"\']+)["\'][^>]*>/i',$inner,$m)) {
            $url=esc_url_raw((string)$m[1]);
            $mediaId=function_exists('attachment_url_to_postid')?absint(attachment_url_to_postid($url)):0;
            if ($url!=='') {
                $nodes[] = self::node('image-footer-v0143','image','container-footer-v0143',10,self::geometry([4,2,16,8],[4,2,16,8],[40,1,40,5]),['mediaId'=>$mediaId,'url'=>$url,'alt'=>'Footer logo','fit'=>'contain','imageAlignX'=>'center','imageAlignY'=>'center','boxBackground'=>$primary,'boxTransparent'=>true,'focalX'=>50,'focalY'=>50,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
            }
        }
        return LayoutModel::normalize(['schemaVersion'=>LayoutModel::SCHEMA,'units'=>LayoutModel::UNITS,'rowPx'=>LayoutModel::ROW_PX,'nodes'=>$nodes]);
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
    private static function sourcePreview(string $html): string {
        if ($html==='') return '';
        $text=html_entity_decode(strip_tags($html),ENT_QUOTES|ENT_HTML5,'UTF-8');
        $text=trim(preg_replace('/\s+/u',' ',$text)??'');
        return function_exists('mb_substr')?mb_substr($text,0,220):substr($text,0,220);
    }
    private static function footerWidth(array $design): int { $v=$design['FooterWidthPercent']??100; return is_numeric($v)?max(40,min(100,(int)$v)):100; }
    private static function color($v,string $fallback): string { $v=strtolower((string)$v); return preg_match('/^#[0-9a-f]{6}$/',$v)?$v:$fallback; }
    /** @return array{0:int,1:int} */ private static function centredUnits(int $pct): array { $w=max(1,min(120,(int)round(120*$pct/100))); return [(int)floor((120-$w)/2),$w]; }
    private static function geometry(array $d,array $l,array $m): array { return ['desktop'=>['x'=>$d[0],'y'=>$d[1],'w'=>$d[2],'h'=>$d[3]],'laptop'=>['x'=>$l[0],'y'=>$l[1],'w'=>$l[2],'h'=>$l[3],'inheritDesktop'=>false],'tablet'=>['x'=>$l[0],'y'=>$l[1],'w'=>$l[2],'h'=>$l[3],'inheritDesktop'=>false],'mobile'=>['x'=>$m[0],'y'=>$m[1],'w'=>$m[2],'h'=>$m[3],'inheritDesktop'=>false]]; }
    private static function node(string $id,string $type,string $parentId,int $order,array $geometry,array $props): array { return compact('id','type','parentId','order','geometry','props'); }
    private static function nodeCounts(array $model): array { $c=['section'=>0,'container'=>0,'text'=>0,'image'=>0,'menu'=>0,'button'=>0]; foreach (($model['nodes']??[]) as $n) { $t=(string)($n['type']??''); if (isset($c[$t])) $c[$t]++; } return $c; }
    private function __construct() {}
}
