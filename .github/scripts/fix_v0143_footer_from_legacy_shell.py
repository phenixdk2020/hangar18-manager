from pathlib import Path

ROOT = Path('.')

def read(path): return (ROOT / path).read_text(encoding='utf-8')
def write(path, text): (ROOT / path).write_text(text, encoding='utf-8')
def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)
def replace_span(text, start_marker, end_marker, new, label):
    start = text.find(start_marker)
    if start < 0: raise SystemExit(f'Missing start: {label}')
    end = text.find(end_marker, start)
    if end < 0: raise SystemExit(f'Missing end: {label}')
    return text[:start] + new + text[end:]

# Header: follow the legacy Manager contract exactly. Its saved ACTIVE_MENU_OPTION
# is authoritative when it still points at a real menu. Only discover/repair when
# that historical pointer is missing.
path='clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php'
s=read(path)
s=replace_once(
    s,
    "$saved = absint(get_option(self::LEGACY_ACTIVE_MENU_OPTION, 0));\n        $locations = get_nav_menu_locations();",
    "$saved = absint(get_option(self::LEGACY_ACTIVE_MENU_OPTION, 0));\n        if ($saved > 0 && wp_get_nav_menu_object($saved)) {\n            return $saved;\n        }\n        $locations = get_nav_menu_locations();",
    'legacy active menu authority'
)
s=s.replace("sanitize_title(wp_strip_all_tags((string)$item->title))","sanitize_title(strip_tags((string)$item->title))")
write(path,s)

# Footer: the old Manager did not own a separate FooterDesign. get_shell_source()
# copied the literal HANGAR18-FOOTER block from Hjem/another managed page. Make
# that exact stored block the only automatic conversion authority. No guessed
# content is silently substituted when the legacy block is gone.
path='clean/hangar18-manager/src/Migration/LegacyFooterConverter.php'
s=read(path)
s=replace_once(
    s,
    "        if ($source['html']!=='') { $model=self::buildModelFromLegacyFooter($source['html'],$design); $kind='legacy-footer-block'; $note='Automatisk konvertering fra fundet legacy Footer · v0.1.43'; }\n        else { $model=self::buildReferenceFooterModel($design); $kind='design-reference-fallback'; $note='Footer-reference fallback · v0.1.43'; }",
    "        if ($source['html']==='') {\n            throw new \\RuntimeException('Den gamle Manager-Footer blev ikke fundet mellem HANGAR18-FOOTER-START/END på Hjem eller andre WordPress-sider. Ingen Footer er gættet eller oprettet automatisk.');\n        }\n        $model=self::buildModelFromLegacyFooter($source['html'],$design);\n        $kind='legacy-manager-shell-footer';\n        $note='Automatisk konvertering fra gammel Manager shell/Footer · v0.1.43';",
    'footer conversion authority'
)

new_build=r'''    /** @param array<string,mixed> $design */
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

'''
s=replace_span(s,'    /** @param array<string,mixed> $design */\n    public static function buildModelFromLegacyFooter', '    /** @param array<string,mixed> $design */\n    public static function buildReferenceFooterModel',new_build,'legacy footer model')

# Add source evidence to diagnostics/result so the test tells us exactly which
# old page/block was used.
s=replace_once(
    s,
    "'sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'footerWidthPercent'=>self::footerWidth($design),'nodeCounts'=>$counts",
    "'sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>hash('sha256',$source['html']),'sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'nodeCounts'=>$counts",
    'footer result source evidence'
)
s=replace_once(
    s,
    "'sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'footerWidthPercent'=>self::footerWidth($design),'targetTemplateId'=>$id",
    "'sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>$source['html']!==''?hash('sha256',$source['html']):'','sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'targetTemplateId'=>$id",
    'footer diagnostic source evidence'
)
insert=r'''    private static function sourcePreview(string $html): string {
        if ($html==='') return '';
        $text=html_entity_decode(strip_tags($html),ENT_QUOTES|ENT_HTML5,'UTF-8');
        $text=trim(preg_replace('/\s+/u',' ',$text)??'');
        return function_exists('mb_substr')?mb_substr($text,0,220):substr($text,0,220);
    }
'''
s=replace_once(s,'    private static function footerWidth(array $design): int {',insert+'    private static function footerWidth(array $design): int {','source preview helper')
write(path,s)

# Footer Designer diagnostics must explicitly say that the old Manager shell is
# the source and display enough evidence to verify it.
path='clean/hangar18-manager/src/Admin/GlobalDesignerController.php'
s=read(path)
s=s.replace(
    'Footer læses fra den gamle HANGAR18-FOOTER-blok. Hvis den ikke længere findes, laves en tydeligt markeret design-fallback til første parity-test. Hver konvertering gemmes som ny Footer-version.',
    'Footer læses med den gamle Managers egen shell-metode fra den faktiske HANGAR18-FOOTER-blok på Hjem eller en anden gammel styret side. Hvis blokken mangler, stoppes konverteringen med en tydelig fejl; der gættes ikke på Footer-indhold. Hver konvertering gemmes som ny Footer-version.'
)
s=s.replace("(!empty($status['legacyFooterFound'])?'Fundet':'Ikke fundet · fallback bruges')","(!empty($status['legacyFooterFound'])?'Fundet':'Ikke fundet · konvertering stoppes')")
s=replace_once(
    s,
    "        echo '<tr><th>FooterWidthPercent</th><td>'.esc_html((string)($status['footerWidthPercent']??100)).'%</td></tr>';",
    "        echo '<tr><th>FooterWidthPercent</th><td>'.esc_html((string)($status['footerWidthPercent']??100)).'%</td></tr>';\n        echo '<tr><th>Kildeudsnit</th><td><code>'.esc_html((string)($status['sourcePreview']??'')).'</code></td></tr>';\n        echo '<tr><th>Kilde-digest</th><td><code>'.esc_html(substr((string)($status['sourceDigest']??''),0,20)).'</code></td></tr>';",
    'footer diagnostic evidence rows'
)
write(path,s)

# Update release-facing descriptions: no generic Footer fallback is part of the
# implementation anymore.
path='clean-release-notes.html'; s=read(path)
s=s.replace('første non-destruktive konvertering til Footer – Standard fra legacy Footer-blok, med diagnose og genkonverteringsknap.','første non-destruktive konvertering til Footer – Standard fra den faktiske gamle Manager-shells HANGAR18-FOOTER-blok, med kildeside, kildeudsnit, digest og genkonverteringsknap; ingen gættet Footer ved manglende blok.')
write(path,s)

path='docs/v0143-status.md'; s=read(path)
s=s.replace('- Footer – Standard first conversion added from HANGAR18-FOOTER block and FooterWidthPercent.','- Footer – Standard first conversion follows the old Manager get_shell_source contract: the literal HANGAR18-FOOTER block from Hjem/another managed page is authoritative, together with FooterWidthPercent.')
s=s.replace('- Footer conversion is observable and repeatable; missing legacy source uses a clearly labelled fallback.','- Footer conversion is observable and repeatable with source page, excerpt and SHA-256 evidence. Missing legacy source stops with an explicit error; no Footer content is guessed.')
write(path,s)

# QA now also asserts that the real legacy block text survives conversion.
path='.github/scripts/v0125_model_qa.php'; s=read(path)
s=s.replace("wp_strip_all_tags", "strip_tags")
write(path,s)

print('0.1.43 footer authority corrected to legacy Manager shell contract')
