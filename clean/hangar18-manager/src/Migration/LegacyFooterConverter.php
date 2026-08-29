<?php

declare(strict_types=1);

namespace Hangar18\Clean\Migration;

use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Model\TemplateLayoutModel;

final class LegacyFooterConverter
{
    public const MIGRATION_OPTION='h18_vd_legacy_footer_converted_v0147';
    public const STATUS_OPTION='h18_vd_legacy_footer_status_v0147';
    private const LEGACY_DESIGN_OPTION='hangar18_manager_header_design_v25';
    private const LEGACY_SITE_TEMPLATES_OPTION='hangar18_manager_site_templates_v1';
    private const LEGACY_SITE_ASSIGNMENTS_OPTION='hangar18_manager_site_template_assignments_v1';
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
        $source=self::resolveLegacyFooterSource();
        $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];
        $fallbackUsed=$source['html']==='';
        if ($fallbackUsed) {
            $model=self::buildDesktopReferenceFooterModel($design,self::referenceFooterLinks());
            $kind='desktop-reference-2026-08-29';
            $note='Footer-reference fra godkendt Desktop-screenshot · v0.1.47';
        } else {
            $model=self::buildModelFromLegacyFooter($source['html'],$design);
            $kind=(string)($source['sourceKind']??'legacy-manager-shell-footer');
            $note='Automatisk Footer-konvertering fra '.$kind.' · v0.1.45';
        }
        $counts=self::nodeCounts($model);
        if (($counts['section']??0)<1 || ($counts['container']??0)<1 || ($counts['text']??0)<1) throw new \RuntimeException('Footer-konverteringen gav ikke Sektion/Kasse/Tekst.');
        TemplateLayoutModel::ensureMigrated();
        $id=TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID,'footer')?self::TARGET_TEMPLATE_ID:TemplateLayoutModel::defaultId('footer');
        if ($id==='') $id=TemplateLayoutModel::create('footer','Footer – Standard');
        $version=TemplateLayoutModel::saveVersion($id,$model,['contentWidth'=>1728],get_current_user_id(),$note);
        TemplateLayoutModel::rename($id,'Footer – Standard'); TemplateLayoutModel::setActive($id,true); TemplateLayoutModel::setDefault('footer',$id);
        $result=['status'=>'success','convertedUtc'=>gmdate('c'),'templateId'=>$id,'templateVersion'=>$version,'source'=>$kind,'legacyFooterFound'=>$source['html']!=='','fallbackUsed'=>$fallbackUsed,'legacyBuilderFound'=>!empty($source['builderFound']),'legacyBuilderAmbiguous'=>!empty($source['builderAmbiguous']),'legacyBuilderCandidates'=>$source['builderCandidates']??[],'legacyBuilderTemplateId'=>$source['builderTemplateId']??'','legacyBuilderTemplateName'=>$source['builderTemplateName']??'','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>$source['html']!==''?hash('sha256',$source['html']):'','sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'nodeCounts'=>$counts,'digest'=>LayoutModel::structuralDigest($model)];
        update_option(self::STATUS_OPTION,$result,false); update_option(self::MIGRATION_OPTION,$result,false); return $result;
    }
    /** @return array<string,mixed> */
    public static function diagnosticStatus(): array {
        $source=self::resolveLegacyFooterSource(); $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];
        TemplateLayoutModel::ensureMigrated(); $id=TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID,'footer')?self::TARGET_TEMPLATE_ID:TemplateLayoutModel::defaultId('footer');
        $model=$id!==''?TemplateLayoutModel::model($id):LayoutModel::empty(); $last=get_option(self::STATUS_OPTION,[]); $last=is_array($last)?$last:[];
        return ['legacyFooterFound'=>$source['html']!=='','fallbackAvailable'=>true,'legacyBuilderFound'=>!empty($source['builderFound']),'legacyBuilderAmbiguous'=>!empty($source['builderAmbiguous']),'legacyBuilderCandidates'=>$source['builderCandidates']??[],'legacyBuilderTemplateId'=>$source['builderTemplateId']??'','legacyBuilderTemplateName'=>$source['builderTemplateName']??'','sourceKind'=>$source['sourceKind']??'','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>$source['html']!==''?hash('sha256',$source['html']):'','sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'targetTemplateId'=>$id,'targetVersion'=>$id!==''?TemplateLayoutModel::version($id):0,'targetNodeCounts'=>self::nodeCounts($model),'lastConversion'=>$last];
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
            self::node('text-footer-v0143','text','container-footer-v0143',20,self::geometry([4,2,112,8],[4,2,112,8],[5,2,110,8]),['heading'=>'','headingLevel'=>'h2','text'=>$text,'align'=>$align,'verticalAlign'=>'center','background'=>$primary,'backgroundTransparent'=>true,'textColor'=>$light,'headingColor'=>$light,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>1.4,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
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

    /**
     * Deterministic no-legacy fallback based on the real Desktop Footer
     * reference supplied 2026-08-29. It is a visual reconstruction, not a
     * claim that the historical source was recovered.
     *
     * @param array<string,mixed> $design
     * @param array<string,string> $links
     */
    public static function buildDesktopReferenceFooterModel(array $design=[],array $links=[]): array {
        $pct=self::footerWidth($design); if ($pct>=100) $pct=90; [$x,$w]=self::centredUnits($pct);
        $bg=self::color($design['PrimaryColor']??'#30382a','#30382a');
        $fg=self::color($design['LightTextColor']??'#f2f0e8','#f2f0e8');
        $accent=self::color($design['AccentColor']??'#c3ae83','#c3ae83');
        $rows=40;
        $nodes=[
            self::node('section-footer-reference-v0147','section','',10,self::geometry([$x,0,$w,$rows],[3,0,114,44],[0,0,120,82]),['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('container-footer-reference-v0147','container','section-footer-reference-v0147',10,self::geometry([0,0,120,$rows],[0,0,120,44],[0,0,120,82]),['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-brand-v0147','text','container-footer-reference-v0147',20,self::geometry([2,5,42,4],[2,5,42,5],[4,4,112,5]),['heading'=>'','headingLevel'=>'h2','text'=>'Aalborg Kaserners Veteran Panser- og Køretøjsforening','align'=>'left','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>18,'fontWeight'=>700,'lineHeight'=>1.25,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-description-v0147','text','container-footer-reference-v0147',30,self::geometry([2,10,36,7],[2,11,40,8],[4,10,112,10]),['heading'=>'','headingLevel'=>'h2','text'=>'Bevaring, restaurering og levende formidling af militærhistorisk materiel med særlig tilknytning til Aalborg Kaserner.','align'=>'left','verticalAlign'=>'top','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>1.45,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-shortcuts-heading-v0147','text','container-footer-reference-v0147',40,self::geometry([49,5,18,3],[47,5,20,3],[4,23,112,3]),['heading'=>'','headingLevel'=>'h2','text'=>'Genveje','align'=>'left','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$accent,'headingColor'=>$accent,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>600,'lineHeight'=>1.2,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-shortcuts-v0147','text','container-footer-reference-v0147',50,self::geometry([49,9,20,18],[47,9,22,19],[4,27,112,18]),['heading'=>'','headingLevel'=>'h2','text'=>self::referenceShortcutHtml($links),'align'=>'left','verticalAlign'=>'top','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>1.75,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-association-heading-v0147','text','container-footer-reference-v0147',60,self::geometry([84,5,32,3],[80,5,38,3],[4,48,112,3]),['heading'=>'','headingLevel'=>'h2','text'=>'Foreningen','align'=>'left','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$accent,'headingColor'=>$accent,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>600,'lineHeight'=>1.2,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('button-footer-join-v0147','button','container-footer-reference-v0147',70,self::geometry([84,8,32,6],[80,8,38,6],[4,52,112,6]),['text'=>'Bliv medlem','linkType'=>'url','url'=>self::referenceLink($links,'join','/bliv-medlem/'),'targetBlank'=>false,'autoSize'=>false,'placementMode'=>'normal','zIndex'=>20,'background'=>$accent,'textColor'=>'#1d2327','hoverBackground'=>$accent,'hoverTextColor'=>'#1d2327','focusColor'=>$fg,'paddingX'=>12,'paddingY'=>8,'radius'=>5,'borderWidth'=>0,'borderColor'=>$accent,'gapX'=>0,'gapY'=>0]),
            self::node('button-footer-contact-v0147','button','container-footer-reference-v0147',80,self::geometry([84,16,32,6],[80,16,38,6],[4,60,112,6]),['text'=>'Kontakt','linkType'=>'url','url'=>self::referenceLink($links,'contact','/kontakt/'),'targetBlank'=>false,'autoSize'=>false,'placementMode'=>'normal','zIndex'=>20,'background'=>$bg,'textColor'=>$fg,'hoverBackground'=>$bg,'hoverTextColor'=>$fg,'focusColor'=>$accent,'paddingX'=>12,'paddingY'=>8,'radius'=>5,'borderWidth'=>1,'borderColor'=>$accent,'gapX'=>0,'gapY'=>0]),
            self::node('container-footer-divider-v0147','container','container-footer-reference-v0147',90,self::geometry([2,31,116,1],[2,34,116,1],[4,70,112,1]),['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>1,'borderWidth'=>1,'borderColor'=>'#596052','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-copyright-v0147','text','container-footer-reference-v0147',100,self::geometry([35,34,50,4],[30,37,60,4],[4,74,112,5]),['heading'=>'','headingLevel'=>'h2','text'=>'© 2026 Aalborg Kaserners Veteran Panser- og Køretøjsforening','align'=>'center','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>11,'fontWeight'=>400,'lineHeight'=>1.3,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
        ];
        return LayoutModel::normalize(['schemaVersion'=>LayoutModel::SCHEMA,'units'=>LayoutModel::UNITS,'rowPx'=>LayoutModel::ROW_PX,'nodes'=>$nodes]);
    }

    /** @param array<string,mixed> $design */
    public static function buildReferenceFooterModel(array $design=[]): array {
        return self::buildDesktopReferenceFooterModel($design,[]);
    }

    /** @param array<string,string> $links */
    private static function referenceShortcutHtml(array $links): string {
        $items=[['home','Hjem','/'],['about','Om','/om-foreningen/'],['vehicles','Køretøjer','/koeretoejer-og-materiel/'],['events','Events','/events/'],['gallery','Billedgalleri','/billedgalleri/']];
        $rows=[];
        foreach ($items as $item) {
            [$key,$label,$fallback]=$item; $url=self::referenceLink($links,$key,$fallback);
            $rows[]='<a href="'.htmlspecialchars($url,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8').'">'.htmlspecialchars($label,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8').'</a>';
        }
        return implode("<br>\n",$rows);
    }

    /** @param array<string,string> $links */
    private static function referenceLink(array $links,string $key,string $fallback): string {
        $url=esc_url_raw((string)($links[$key]??'')); return $url!==''?$url:$fallback;
    }

    /** @return array<string,string> */
    private static function referenceFooterLinks(): array {
        return [
            'home'=>self::referencePageUrl([], '/'),
            'about'=>self::referencePageUrl(['om-foreningen','om'], '/om-foreningen/'),
            'vehicles'=>self::referencePageUrl(['koeretoejer-og-materiel','koretojer-og-materiel','koeretoejer'], '/koeretoejer-og-materiel/'),
            'events'=>self::referencePageUrl(['events'], '/events/'),
            'gallery'=>self::referencePageUrl(['billedgalleri'], '/billedgalleri/'),
            'join'=>self::referencePageUrl(['bliv-medlem'], '/bliv-medlem/'),
            'contact'=>self::referencePageUrl(['kontakt'], '/kontakt/'),
        ];
    }

    /** @param array<int,string> $slugs */
    private static function referencePageUrl(array $slugs,string $fallbackPath): string {
        if (function_exists('get_page_by_path') && function_exists('get_permalink')) {
            foreach ($slugs as $slug) {
                $page=get_page_by_path($slug,OBJECT,'page');
                if ($page instanceof \WP_Post) { $url=get_permalink($page); if (is_string($url) && $url!=='') return esc_url_raw($url); }
            }
        }
        if (function_exists('home_url')) return esc_url_raw((string)home_url($fallbackPath));
        return $fallbackPath;
    }
    private static function model(int $x,int $w,int $rows,string $bg,string $fg,string $text): array {
        $geometry=self::geometry([$x,0,$w,$rows],[$x,0,$w,$rows],[0,0,120,$rows]);
        $nodes=[
            self::node('section-footer-v0143','section','',10,$geometry,['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('container-footer-v0143','container','section-footer-v0143',10,self::geometry([0,0,120,$rows],[0,0,120,$rows],[0,0,120,$rows]),['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-v0143','text','container-footer-v0143',10,self::geometry([4,2,112,8],[4,2,112,8],[5,2,110,8]),['heading'=>'','headingLevel'=>'h2','text'=>$text,'align'=>'center','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>1.4,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
        ];
        return LayoutModel::normalize(['schemaVersion'=>LayoutModel::SCHEMA,'units'=>LayoutModel::UNITS,'rowPx'=>LayoutModel::ROW_PX,'nodes'=>$nodes]);
    }
    /** @return array<string,mixed> */
    private static function resolveLegacyFooterSource(): array {
        $builder=self::legacyVisualBuilderFooter();
        if (($builder['html']??'')!=='') return $builder;
        $shell=self::legacyShellFooter();
        if (($shell['html']??'')!=='') {
            return array_merge($shell,[
                'sourceKind'=>'legacy-manager-shell-footer',
                'builderFound'=>!empty($builder['builderFound']),
                'builderAmbiguous'=>!empty($builder['builderAmbiguous']),
                'builderCandidates'=>$builder['builderCandidates']??[],
                'builderTemplateId'=>'',
                'builderTemplateName'=>'',
            ]);
        }
        return [
            'html'=>'','pageId'=>0,'pageTitle'=>'','sourceKind'=>'desktop-reference-2026-08-29',
            'builderFound'=>!empty($builder['builderFound']),
            'builderAmbiguous'=>!empty($builder['builderAmbiguous']),
            'builderCandidates'=>$builder['builderCandidates']??[],
            'builderTemplateId'=>'','builderTemplateName'=>'',
        ];
    }

    /** @return array<string,mixed> */
    private static function legacyVisualBuilderFooter(): array {
        $stored=get_option(self::LEGACY_SITE_TEMPLATES_OPTION,[]);
        $templates=is_array($stored)?$stored:[];
        $footers=[];
        foreach ($templates as $key=>$template) {
            if (!is_array($template) || strtolower((string)($template['Kind']??''))!=='footer') continue;
            $id=sanitize_key((string)($template['Id']??$key));
            if ($id==='') continue;
            $footers[$id]=$template;
        }
        $candidates=[];
        foreach ($footers as $id=>$template) {
            $candidates[]=[
                'id'=>$id,
                'name'=>(string)($template['Name']??$id),
                'revision'=>(int)($template['Revision']??0),
            ];
        }
        $assignments=get_option(self::LEGACY_SITE_ASSIGNMENTS_OPTION,[]);
        $assignments=is_array($assignments)?$assignments:[];
        $assigned=sanitize_key((string)($assignments['footer']??''));
        $selected=null; $sourceKind='';
        if ($assigned!=='' && isset($footers[$assigned])) {
            $selected=$footers[$assigned]; $sourceKind='legacy-visual-builder-assigned';
        } elseif (count($footers)===1) {
            $assigned=(string)array_key_first($footers); $selected=$footers[$assigned]; $sourceKind='legacy-visual-builder-single';
        }
        if (!is_array($selected)) {
            return [
                'html'=>'','pageId'=>0,'pageTitle'=>'','sourceKind'=>'',
                'builderFound'=>count($footers)>0,
                'builderAmbiguous'=>count($footers)>1,
                'builderCandidates'=>$candidates,
                'builderTemplateId'=>'','builderTemplateName'=>'',
            ];
        }
        $html=self::legacyVisualBuilderTemplateHtml($selected);
        return [
            'html'=>$html,'pageId'=>0,'pageTitle'=>'Gammel Visual Header/Footer Builder','sourceKind'=>$sourceKind,
            'builderFound'=>true,'builderAmbiguous'=>false,'builderCandidates'=>$candidates,
            'builderTemplateId'=>$assigned,'builderTemplateName'=>(string)($selected['Name']??$assigned),
        ];
    }

    /** @param array<string,mixed> $template */
    private static function legacyVisualBuilderTemplateHtml(array $template): string {
        $sections=is_array($template['Sections']??null)?array_values($template['Sections']):[];
        $lines=[]; $background='#30382a'; $color='#f2f0e8'; $align='center';
        foreach ($sections as $section) {
            if (!is_array($section)) continue;
            $bg=sanitize_hex_color((string)($section['CustomBackgroundColor']??''));
            if ($bg) $background=strtolower($bg);
            $fg=sanitize_hex_color((string)($section['CustomTextColor']??''));
            if ($fg) $color=strtolower($fg);
            $a=strtolower((string)($section['DesktopAlignment']??''));
            if (in_array($a,['left','center','right'],true)) $align=$a;
            foreach (['Title','Content'] as $field) {
                $value=html_entity_decode(wp_strip_all_tags((string)($section[$field]??'')),ENT_QUOTES|ENT_HTML5,'UTF-8');
                $value=trim(preg_replace('/\s+/u',' ',$value)??'');
                if ($value!=='' && !in_array($value,$lines,true)) $lines[]=$value;
            }
        }
        if (!$lines) return '';
        $visible=implode('<br>',array_map('esc_html',$lines));
        return '<!-- HANGAR18-FOOTER-START --><footer class="h18-site-footer h18-legacy-builder-footer" style="background:'.esc_attr($background).';color:'.esc_attr($color).';text-align:'.esc_attr($align).'">'.$visible.'</footer><!-- HANGAR18-FOOTER-END -->';
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
