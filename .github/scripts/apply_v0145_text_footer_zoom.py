from pathlib import Path
import json

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# Version
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/hangar18-manager.php'
s = read(path)
s = replace_once(s, ' * Version: 0.1.44', ' * Version: 0.1.45', 'plugin header version')
s = replace_once(s, "define('H18_CLEAN_VERSION', '0.1.44');", "define('H18_CLEAN_VERSION', '0.1.45');", 'version constant')
write(path, s)


# -----------------------------------------------------------------------------
# Canonical Text vertical alignment: Top / Center / Bottom.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Model/LayoutModel.php'
s = read(path)
old = """            $align = strtolower((string) ($raw['align'] ?? 'left'));
            if (!in_array($align, ['left', 'center', 'right'], true)) {
                $align = 'left';
            }
            return array_merge([
"""
new = """            $align = strtolower((string) ($raw['align'] ?? 'left'));
            if (!in_array($align, ['left', 'center', 'right'], true)) {
                $align = 'left';
            }
            $verticalAlign = strtolower((string) ($raw['verticalAlign'] ?? 'top'));
            if (!in_array($verticalAlign, ['top', 'center', 'bottom'], true)) {
                $verticalAlign = 'top';
            }
            return array_merge([
"""
s = replace_once(s, old, new, 'LayoutModel vertical align normalization')
s = replace_once(s, "                'align' => $align,\n", "                'align' => $align,\n                'verticalAlign' => $verticalAlign,\n", 'LayoutModel vertical align prop')
write(path, s)


# -----------------------------------------------------------------------------
# Editor: Text vertical alignment + explicit image MIME help.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v018-core.js'
s = read(path)
s = replace_once(
    s,
    "align:'tekstjustering',fontFamily:",
    "align:'tekstjustering',verticalAlign:'lodret justering',fontFamily:",
    'field label vertical align'
)
s = replace_once(
    s,
    "                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left',\n",
    "                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left',\n                verticalAlign: ['top', 'center', 'bottom'].includes(String(raw.verticalAlign || '').toLowerCase()) ? String(raw.verticalAlign).toLowerCase() : 'top',\n",
    'editor normalize vertical align'
)
s = replace_once(
    s,
    "            wrap.style.textAlign = node.props.align || 'left';\n",
    "            wrap.style.textAlign = node.props.align || 'left';\n            wrap.style.display = 'flex';\n            wrap.style.flexDirection = 'column';\n            wrap.style.justifyContent = ({ top: 'flex-start', center: 'center', bottom: 'flex-end' })[node.props.verticalAlign || 'top'] || 'flex-start';\n            wrap.style.height = '100%';\n            wrap.style.boxSizing = 'border-box';\n",
    'editor text flex vertical align'
)
old = """            html += '<label>Justering<select data-field=\"align\"><option value=\"left\"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value=\"center\"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value=\"right\"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label>';
"""
new = old + """            html += '<label>Lodret justering<select data-field=\"verticalAlign\"><option value=\"top\"' + (node.props.verticalAlign === 'top' ? ' selected' : '') + '>Top</option><option value=\"center\"' + (node.props.verticalAlign === 'center' ? ' selected' : '') + '>Midt</option><option value=\"bottom\"' + (node.props.verticalAlign === 'bottom' ? ' selected' : '') + '>Bund</option></select></label>';
"""
s = replace_once(s, old, new, 'Inspector vertical align')
s = replace_once(
    s,
    "                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }\n",
    "                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }\n                else if (field === 'verticalAlign') { current.props.verticalAlign = ['top', 'center', 'bottom'].includes(control.value) ? control.value : 'top'; }\n",
    'Inspector change vertical align'
)
s = replace_once(
    s,
    "            html += '<button type=\"button\" class=\"button\" id=\"h18-clean-pick-image\">Vælg / skift billede</button>';\n",
    "            html += '<button type=\"button\" class=\"button\" id=\"h18-clean-pick-image\">Vælg / skift billede</button><p class=\"description\">PNG, JPG/JPEG, WebP, GIF og andre image/*-formater som WordPress tillader. PNG-transparens bevares.</p>';\n",
    'Image MIME help'
)
write(path, s)


# -----------------------------------------------------------------------------
# Frontend renderer: same vertical alignment contract.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Frontend/Renderer.php'
s = read(path)
s = replace_once(
    s,
    "            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#000000')) ?: '#000000';\n",
    "            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#000000')) ?: '#000000';\n            $verticalAlign = in_array((string) ($props['verticalAlign'] ?? 'top'), ['top', 'center', 'bottom'], true) ? (string) $props['verticalAlign'] : 'top';\n            $verticalJustify = ['top' => 'flex-start', 'center' => 'center', 'bottom' => 'flex-end'][$verticalAlign];\n",
    'Renderer vertical align variables'
)
s = replace_once(
    s,
    "                . 'background:' . $background . ';padding:' . $padding . 'px;color:' . $textColor . ';text-align:' . (string) ($props['align'] ?? 'left') . ';font-family:' . $bodyFamily . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;';\n",
    "                . 'background:' . $background . ';padding:' . $padding . 'px;color:' . $textColor . ';text-align:' . (string) ($props['align'] ?? 'left') . ';font-family:' . $bodyFamily . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;display:flex;flex-direction:column;justify-content:' . $verticalJustify . ';';\n",
    'Renderer vertical align style'
)
write(path, s)


# -----------------------------------------------------------------------------
# Converted reference Header brand is vertically centred by the new canonical
# property instead of relying only on a hand-tuned Y offset.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php'
s = read(path)
s = s.replace("'text'=>$brand,'align'=>'left','background'", "'text'=>$brand,'align'=>'left','verticalAlign'=>'center','background'")
write(path, s)


# -----------------------------------------------------------------------------
# Footer source precedence:
# 1) historical Visual Header/Footer Builder options
# 2) historical HANGAR18-FOOTER shell block
# 3) explicitly labelled old-Manager standard fallback (not claimed as 1:1)
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Migration/LegacyFooterConverter.php'
s = read(path)
s = replace_once(
    s,
    "    private const LEGACY_DESIGN_OPTION='hangar18_manager_header_design_v25';\n",
    "    private const LEGACY_DESIGN_OPTION='hangar18_manager_header_design_v25';\n    private const LEGACY_SITE_TEMPLATES_OPTION='hangar18_manager_site_templates_v1';\n    private const LEGACY_SITE_ASSIGNMENTS_OPTION='hangar18_manager_site_template_assignments_v1';\n",
    'Footer legacy builder constants'
)
old = """        $source=self::legacyShellFooter();
        $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];
        if ($source['html']==='') {
            throw new \\RuntimeException('Den gamle Manager-Footer blev ikke fundet mellem HANGAR18-FOOTER-START/END på Hjem eller andre WordPress-sider. Ingen Footer er gættet eller oprettet automatisk.');
        }
        $model=self::buildModelFromLegacyFooter($source['html'],$design);
        $kind='legacy-manager-shell-footer';
        $note='Automatisk konvertering fra gammel Manager shell/Footer · v0.1.43';
"""
new = """        $source=self::resolveLegacyFooterSource();
        $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];
        $fallbackUsed=$source['html']==='';
        if ($fallbackUsed) {
            $model=self::buildReferenceFooterModel($design);
            $kind='legacy-manager-standard-fallback';
            $note='Standardfallback fra gammel Manager · v0.1.45 · ikke 1:1-kilde';
        } else {
            $model=self::buildModelFromLegacyFooter($source['html'],$design);
            $kind=(string)($source['sourceKind']??'legacy-manager-shell-footer');
            $note='Automatisk Footer-konvertering fra '.$kind.' · v0.1.45';
        }
"""
s = replace_once(s, old, new, 'Footer convert source precedence')
s = replace_once(
    s,
    "'source'=>$kind,'legacyFooterFound'=>$source['html']!=='','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>hash('sha256',$source['html']),'sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'nodeCounts'=>$counts,'digest'=>LayoutModel::structuralDigest($model)",
    "'source'=>$kind,'legacyFooterFound'=>$source['html']!=='','fallbackUsed'=>$fallbackUsed,'legacyBuilderFound'=>!empty($source['builderFound']),'legacyBuilderAmbiguous'=>!empty($source['builderAmbiguous']),'legacyBuilderCandidates'=>$source['builderCandidates']??[],'legacyBuilderTemplateId'=>$source['builderTemplateId']??'','legacyBuilderTemplateName'=>$source['builderTemplateName']??'','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>$source['html']!==''?hash('sha256',$source['html']):'','sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'nodeCounts'=>$counts,'digest'=>LayoutModel::structuralDigest($model)",
    'Footer conversion result diagnostics'
)
s = replace_once(
    s,
    "        $source=self::legacyShellFooter(); $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];\n",
    "        $source=self::resolveLegacyFooterSource(); $stored=get_option(self::LEGACY_DESIGN_OPTION,[]); $design=is_array($stored)?$stored:[];\n",
    'Footer diagnostic source precedence'
)
s = replace_once(
    s,
    "return ['legacyFooterFound'=>$source['html']!=='','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>$source['html']!==''?hash('sha256',$source['html']):'','sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'targetTemplateId'=>$id,'targetVersion'=>$id!==''?TemplateLayoutModel::version($id):0,'targetNodeCounts'=>self::nodeCounts($model),'lastConversion'=>$last];",
    "return ['legacyFooterFound'=>$source['html']!=='','fallbackAvailable'=>true,'legacyBuilderFound'=>!empty($source['builderFound']),'legacyBuilderAmbiguous'=>!empty($source['builderAmbiguous']),'legacyBuilderCandidates'=>$source['builderCandidates']??[],'legacyBuilderTemplateId'=>$source['builderTemplateId']??'','legacyBuilderTemplateName'=>$source['builderTemplateName']??'','sourceKind'=>$source['sourceKind']??'','sourcePageId'=>$source['pageId'],'sourcePageTitle'=>$source['pageTitle'],'sourceDigest'=>$source['html']!==''?hash('sha256',$source['html']):'','sourcePreview'=>self::sourcePreview($source['html']),'footerWidthPercent'=>self::footerWidth($design),'targetTemplateId'=>$id,'targetVersion'=>$id!==''?TemplateLayoutModel::version($id):0,'targetNodeCounts'=>self::nodeCounts($model),'lastConversion'=>$last];",
    'Footer diagnostic fields'
)
s = s.replace("'text'=>$text,'align'=>$align,'background'", "'text'=>$text,'align'=>$align,'verticalAlign'=>'center','background'")
s = s.replace("'text'=>$text,'align'=>'center','background'", "'text'=>$text,'align'=>'center','verticalAlign'=>'center','background'")

anchor = """    /** @return array{html:string,pageId:int,pageTitle:string} */
    private static function legacyShellFooter(): array {
"""
insert = r'''    /** @return array<string,mixed> */
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
            'html'=>'','pageId'=>0,'pageTitle'=>'','sourceKind'=>'legacy-manager-standard-fallback',
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

''' + anchor
s = replace_once(s, anchor, insert, 'Footer old visual builder resolver')
write(path, s)


# -----------------------------------------------------------------------------
# Footer diagnostics in Header/Footer UI.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Admin/GlobalDesignerController.php'
s = read(path)
old = """        echo '<p class=\"description\">Footer læses med den gamle Managers egen shell-metode fra den faktiske HANGAR18-FOOTER-blok på Hjem eller en anden gammel styret side. Hvis blokken mangler, stoppes konverteringen med en tydelig fejl; der gættes ikke på Footer-indhold. Hver konvertering gemmes som ny Footer-version.</p><table class=\"widefat striped\"><tbody>';
        echo '<tr><th>Legacy Footer-blok</th><td>'.(!empty($status['legacyFooterFound'])?'Fundet':'Ikke fundet · konvertering stoppes').'</td></tr>';
"""
new = """        echo '<p class=\"description\">Kildeprioritet: gammel Visual Header/Footer Builder → HANGAR18-FOOTER-blok → tydeligt mærket gammel Manager-standardfallback. En fallback betegnes aldrig som 1:1-konvertering. Hver kørsel gemmes som ny Footer-version.</p><table class=\"widefat striped\"><tbody>';
        echo '<tr><th>Gammel Visual Builder</th><td>'.(!empty($status['legacyBuilderFound'])?'Fundet':'Ikke fundet').(!empty($status['legacyBuilderAmbiguous'])?' · flere Footer-templates uden entydig global assignment':'').'</td></tr>';
        echo '<tr><th>Valgt gammel Builder-template</th><td>'.esc_html((string)($status['legacyBuilderTemplateName']??'')).(!empty($status['legacyBuilderTemplateId'])?' · '.esc_html((string)$status['legacyBuilderTemplateId']):'').'</td></tr>';
        echo '<tr><th>Legacy Footer-kilde</th><td>'.(!empty($status['legacyFooterFound'])?'Fundet · '.esc_html((string)($status['sourceKind']??'')):'Ikke fundet · gammel Manager-standardfallback er tilgængelig').'</td></tr>';
"""
s = replace_once(s, old, new, 'Footer UI diagnostics description')
write(path, s)


# -----------------------------------------------------------------------------
# WYSIWYG viewport + manual wheel zoom. Fit remains automatic; manual zoom stays
# fixed when side panels change. Device switch returns to Fit.
# -----------------------------------------------------------------------------
viewport_js = r'''(function () {
    'use strict';

    var WIDTHS = { desktop: 1920, laptop: 1180, mobile: 390 };
    var MIN_FIT_SCALE = 0.15;
    var MIN_MANUAL_SCALE = 0.25;
    var MAX_MANUAL_SCALE = 2.0;
    var STEP = 0.10;
    var root = null;
    var column = null;
    var stage = null;
    var currentScale = 1;
    var currentWidth = WIDTHS.desktop;
    var mode = 'fit';
    var scheduled = false;
    var rootObserver = null;
    var columnObserver = null;
    var bodyObserver = null;

    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function roundScale(value) { return Math.round(Number(value || 1) * 100) / 100; }
    function activeDevice() {
        if (window.H18CleanResponsive && typeof window.H18CleanResponsive.device === 'function') {
            var responsiveDevice = String(window.H18CleanResponsive.device() || '');
            if (WIDTHS[responsiveDevice]) { return responsiveDevice; }
        }
        var bodyDevice = document.body ? String(document.body.getAttribute('data-h18-clean-device') || '') : '';
        if (WIDTHS[bodyDevice]) { return bodyDevice; }
        var rootDevice = root ? String(root.getAttribute('data-h18-device') || '') : '';
        return WIDTHS[rootDevice] ? rootDevice : 'desktop';
    }
    function availableWidth() {
        if (!column) { return currentWidth; }
        var style = window.getComputedStyle(column);
        var left = parseFloat(style.paddingLeft || '0') || 0;
        var right = parseFloat(style.paddingRight || '0') || 0;
        return Math.max(80, column.clientWidth - left - right - 2);
    }
    function fitScale() {
        return clamp(Math.min(1, availableWidth() / Math.max(1, currentWidth)), MIN_FIT_SCALE, 1);
    }
    function ensureStage() {
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return false; }
        column = root.closest('.h18-clean-canvas-column') || root.parentElement;
        if (!column) { return false; }
        column.classList.add('h18-vd-zoom-scroll-host');
        if (root.parentElement && root.parentElement.classList.contains('h18-vd-viewport-stage')) {
            stage = root.parentElement;
            return true;
        }
        stage = document.createElement('div');
        stage.className = 'h18-vd-viewport-stage';
        column.insertBefore(stage, root);
        stage.appendChild(root);
        return true;
    }
    function syncStageHeight() {
        if (!root || !stage) { return; }
        var height = Math.max(1, root.offsetHeight || root.scrollHeight || 1);
        stage.style.height = Math.ceil(height * currentScale) + 'px';
    }
    function statusText() {
        var device = activeDevice();
        var label = ({ desktop: 'Desktop', laptop: 'Laptop', mobile: 'Mobil' })[device] || device;
        return label + ' · ' + currentWidth + ' px · ' + (mode === 'fit' ? 'Fit ' : 'Zoom ') + Math.round(currentScale * 100) + '%';
    }
    function ensureControls() {
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar) { return null; }
        var controls = document.getElementById('h18-vd-zoom-controls');
        if (controls) { return controls; }
        controls = document.createElement('span');
        controls.id = 'h18-vd-zoom-controls';
        controls.className = 'h18-vd-zoom-controls';
        controls.innerHTML = '<span id="h18-vd-viewport-status" class="h18-vd-viewport-status"></span>' +
            '<button type="button" class="button button-small" data-vd-zoom="out" title="Zoom ud">−</button>' +
            '<button type="button" class="button button-small" data-vd-zoom="fit" title="Tilpas automatisk til den ledige canvasbredde">Fit</button>' +
            '<button type="button" class="button button-small" data-vd-zoom="100" title="Vis 100 procent">100%</button>' +
            '<button type="button" class="button button-small" data-vd-zoom="in" title="Zoom ind">+</button>';
        var gridLabel = toolbar.querySelector('.h18-clean-grid-label');
        if (gridLabel) { gridLabel.insertAdjacentElement('afterend', controls); }
        else { toolbar.appendChild(controls); }
        controls.addEventListener('click', function (event) {
            var button = event.target && event.target.closest ? event.target.closest('[data-vd-zoom]') : null;
            if (!button) { return; }
            var action = String(button.getAttribute('data-vd-zoom') || '');
            if (action === 'fit') { setFit(); }
            else if (action === '100') { setManual(1, null); }
            else if (action === 'in') { setManual(currentScale + STEP, null); }
            else if (action === 'out') { setManual(currentScale - STEP, null); }
        });
        return controls;
    }
    function updateStatus() {
        ensureControls();
        var status = document.getElementById('h18-vd-viewport-status');
        if (status) {
            status.textContent = statusText();
            status.title = mode === 'fit'
                ? 'Virtuel frontendbredde. Fit følger automatisk den ledige editorbredde.'
                : 'Manuel canvas-zoom. Layoutets virtuelle geometri er uændret.';
        }
    }
    function applyScale(nextScale, nextMode) {
        if (!ensureStage()) { return; }
        currentWidth = WIDTHS[activeDevice()] || WIDTHS.desktop;
        currentScale = roundScale(clamp(nextScale, nextMode === 'fit' ? MIN_FIT_SCALE : MIN_MANUAL_SCALE, nextMode === 'fit' ? 1 : MAX_MANUAL_SCALE));
        mode = nextMode;
        root.setAttribute('data-h18-viewport-width', String(currentWidth));
        root.setAttribute('data-h18-viewport-scale', String(currentScale));
        root.setAttribute('data-h18-viewport-mode', mode);
        root.style.width = currentWidth + 'px';
        root.style.maxWidth = 'none';
        root.style.transformOrigin = '0 0';
        root.style.transform = 'scale(' + currentScale + ')';
        stage.style.width = Math.ceil(currentWidth * currentScale) + 'px';
        syncStageHeight();
        updateStatus();
        window.dispatchEvent(new CustomEvent('h18-vd-viewport-fit', { detail: { device: activeDevice(), width: currentWidth, scale: currentScale, mode: mode } }));
    }
    function setFit() {
        mode = 'fit';
        currentWidth = WIDTHS[activeDevice()] || WIDTHS.desktop;
        applyScale(fitScale(), 'fit');
        if (column) { column.scrollLeft = 0; }
    }
    function pointerAnchor(clientX, clientY) {
        if (!root || !column || clientX == null || clientY == null) { return null; }
        var rootRect = root.getBoundingClientRect();
        return {
            clientX: Number(clientX), clientY: Number(clientY),
            virtualX: (Number(clientX) - rootRect.left) / Math.max(0.01, currentScale),
            virtualY: (Number(clientY) - rootRect.top) / Math.max(0.01, currentScale)
        };
    }
    function restoreAnchor(anchor) {
        if (!anchor || !root || !column) { return; }
        window.requestAnimationFrame(function () {
            var rootRect = root.getBoundingClientRect();
            var dx = rootRect.left + anchor.virtualX * currentScale - anchor.clientX;
            var dy = rootRect.top + anchor.virtualY * currentScale - anchor.clientY;
            column.scrollLeft += dx;
            column.scrollTop += dy;
        });
    }
    function setManual(value, anchor) {
        var next = roundScale(clamp(value, MIN_MANUAL_SCALE, MAX_MANUAL_SCALE));
        applyScale(next, 'manual');
        restoreAnchor(anchor);
    }
    function refresh() {
        if (!ensureStage()) { return; }
        currentWidth = WIDTHS[activeDevice()] || WIDTHS.desktop;
        if (mode === 'fit') { applyScale(fitScale(), 'fit'); }
        else { applyScale(currentScale, 'manual'); }
    }
    function schedule() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(function () { scheduled = false; refresh(); });
    }
    function installWheel() {
        if (!column || column.getAttribute('data-vd-wheel-zoom') === '1') { return; }
        column.setAttribute('data-vd-wheel-zoom', '1');
        column.addEventListener('wheel', function (event) {
            if (!stage || !event.target || !(event.target === stage || stage.contains(event.target))) { return; }
            event.preventDefault();
            var anchor = pointerAnchor(event.clientX, event.clientY);
            var direction = event.deltaY < 0 ? 1 : -1;
            setManual(currentScale + direction * STEP, anchor);
        }, { passive: false });
    }
    function installObservers() {
        if (window.ResizeObserver && column && !columnObserver) {
            columnObserver = new ResizeObserver(function () { if (mode === 'fit') { schedule(); } else { syncStageHeight(); updateStatus(); } });
            columnObserver.observe(column);
        }
        if (window.ResizeObserver && root && !rootObserver) {
            rootObserver = new ResizeObserver(function () { syncStageHeight(); });
            rootObserver.observe(root);
        }
        if (window.MutationObserver && document.body && !bodyObserver) {
            bodyObserver = new MutationObserver(function (records) {
                var relevant = records.some(function (record) {
                    return record.type === 'attributes' && (record.attributeName === 'data-h18-clean-device' || record.attributeName === 'class');
                });
                if (relevant && mode === 'fit') { schedule(); }
            });
            bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['data-h18-clean-device', 'class'] });
        }
        window.addEventListener('resize', function () { if (mode === 'fit') { schedule(); } }, { passive: true });
        document.addEventListener('click', function (event) {
            if (!event.target || !event.target.closest) { return; }
            if (event.target.closest('.h18-clean-device-button')) {
                mode = 'fit';
                window.requestAnimationFrame(schedule);
                return;
            }
            if (event.target.closest('#h18-clean-wide-canvas,.h18-clean-panel-toggle') && mode === 'fit') {
                window.requestAnimationFrame(schedule);
            }
        }, true);
    }
    function install() {
        if (!ensureStage()) { return; }
        setFit();
        installWheel();
        installObservers();
    }

    window.H18VDViewport = {
        scale: function () { return currentScale || 1; },
        virtualWidth: function () { return currentWidth || WIDTHS.desktop; },
        unscalePx: function (pixels) { return Number(pixels || 0) / Math.max(MIN_FIT_SCALE, currentScale || 1); },
        scaledRowPx: function (rowPx) { return Number(rowPx || 0) * Math.max(MIN_FIT_SCALE, currentScale || 1); },
        refresh: schedule,
        fit: setFit,
        setZoom: function (value) { setManual(Number(value || 1), null); },
        mode: function () { return mode; },
        widths: Object.assign({}, WIDTHS)
    };

    if (document.getElementById('h18-clean-canvas')) { install(); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
'''
write('clean/hangar18-manager/assets/editor-v0144-viewport.js', viewport_js)

viewport_css = r'''/* Visual Designer Manager 0.1.45 · WYSIWYG + manual canvas zoom */
.h18-clean-canvas-column.h18-vd-zoom-scroll-host{
    overflow:auto!important;
    overscroll-behavior:contain;
    scrollbar-gutter:stable;
}
.h18-vd-viewport-stage{
    position:relative;
    display:block;
    margin:0 auto;
    min-height:1px;
    box-sizing:border-box;
}
.h18-vd-viewport-stage>.h18-clean-root{
    position:absolute!important;
    top:0!important;
    left:0!important;
    margin:0!important;
    max-width:none!important;
    transition:none!important;
    transform-origin:0 0!important;
}
.h18-vd-zoom-controls{
    display:inline-flex;
    align-items:center;
    gap:4px;
    white-space:nowrap;
}
.h18-vd-zoom-controls .button{
    min-width:34px;
    min-height:28px;
    padding:0 7px;
}
.h18-vd-viewport-status{
    display:inline-flex;
    align-items:center;
    min-height:28px;
    padding:0 8px;
    border:1px solid #c3c4c7;
    border-radius:5px;
    background:#fff;
    color:#50575e;
    font-size:12px;
    font-weight:700;
    white-space:nowrap;
}
.h18-vd-viewport-stage>.h18-clean-root[data-h18-device="desktop"],
.h18-vd-viewport-stage>.h18-clean-root[data-h18-device="laptop"],
.h18-vd-viewport-stage>.h18-clean-root[data-h18-device="mobile"]{
    max-width:none!important;
}
.h18-clean-node--section,.h18-clean-node--container{
    background-clip:border-box!important;
}
.h18-clean-node--section>.h18-clean-inner-surface,
.h18-clean-node--container>.h18-clean-inner-surface{
    position:absolute!important;
    inset:0!important;
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    margin:0!important;
    box-sizing:border-box!important;
    background:transparent!important;
    border-color:transparent!important;
    border-radius:inherit!important;
}
'''
write('clean/hangar18-manager/assets/editor-v0144.css', viewport_css)


# -----------------------------------------------------------------------------
# Model QA additions.
# -----------------------------------------------------------------------------
path = '.github/scripts/v0125_model_qa.php'
s = read(path)
qa = r'''

/* 0.1.45: Text vertical alignment is canonical and defaults safely. */
$verticalText = LayoutModel::normalize(['nodes'=>[[
    'id'=>'text-vertical','type'=>'text','parentId'=>'','order'=>10,
    'geometry'=>vdGeometry(0,0,60,12),
    'props'=>['text'=>'Midt','align'=>'left','verticalAlign'=>'center'],
]]]);
vdAssert(($verticalText['nodes'][0]['props']['verticalAlign']??'')==='center','Text verticalAlign was not retained canonically.');

$verticalTextDefault = LayoutModel::normalize(['nodes'=>[[
    'id'=>'text-vertical-default','type'=>'text','parentId'=>'','order'=>10,
    'geometry'=>vdGeometry(0,0,60,12),
    'props'=>['text'=>'Top'],
]]]);
vdAssert(($verticalTextDefault['nodes'][0]['props']['verticalAlign']??'')==='top','Existing Text must default to top vertical alignment.');

vdAssert(str_contains((string)$coreJs,'Lodret justering') && str_contains((string)$coreJs,"field === 'verticalAlign'"),'Text vertical alignment Inspector contract is missing.');
vdAssert(str_contains((string)$rendererPhp,'justify-content:') && str_contains((string)$rendererPhp,"['top', 'center', 'bottom']"),'Frontend vertical alignment contract is missing.');
vdAssert(str_contains((string)$coreJs,"library: { type: 'image' }") && !preg_match('/library[^\n]{0,100}\\.(?:jpe?g)/i',(string)$coreJs),'Image picker must use WordPress image/* filtering instead of JPG-only filtering.');
vdAssert(str_contains((string)$viewportJs,'MAX_MANUAL_SCALE = 2.0') && str_contains((string)$viewportJs,"addEventListener('wheel'") && str_contains((string)$viewportJs,'event.preventDefault()'),'Manual wheel zoom contract is missing.');
vdAssert(str_contains((string)$viewportJs,'scrollLeft') && str_contains((string)$viewportJs,'virtualX') && str_contains((string)$viewportJs,"data-vd-zoom=\"fit\""),'Pointer-anchored zoom / Fit controls are missing.');
$footerPhp=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/src/Migration/LegacyFooterConverter.php');
vdAssert(str_contains((string)$footerPhp,'hangar18_manager_site_templates_v1') && str_contains((string)$footerPhp,'hangar18_manager_site_template_assignments_v1'),'Legacy Visual Builder Footer source is missing.');
vdAssert(str_contains((string)$footerPhp,'legacy-manager-standard-fallback') && str_contains((string)$footerPhp,'ikke 1:1-kilde'),'Footer standard fallback is not explicitly labelled.');
'''
s = replace_once(s, "\necho \"Visual Designer Manager 0.1.44 model QA PASS\\n\";", qa + "\necho \"Visual Designer Manager 0.1.45 model QA PASS\\n\";", '0.1.45 QA footer')
write(path, s)


# -----------------------------------------------------------------------------
# Release notes/history/status/technical contracts.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(path))
history.insert(0, {
    'version': '0.1.45',
    'date': '2026-08-29',
    'items': [
        'Tekst får canonical lodret justering Top, Midt og Bund med samme resultat i Designer, Preview og frontend; eksisterende Tekst beholder Top som standard.',
        'Billedevælgerens WordPress image/*-kontrakt er eksplicit: PNG inkl. transparens, JPG/JPEG, WebP, GIF og øvrige billedformater som WordPress tillader.',
        'Footer-konvertering søger først i den gamle Visual Header/Footer Builders templates/global assignment, derefter i HANGAR18-FOOTER-blokke og bruger kun derefter en tydeligt mærket gammel Manager-standardfallback.',
        'Canvas kan zoomes 25-200% med musehjulet over designområdet; zoom forankres omkring musemarkøren, overflow giver scrollbars og Fit/100%/plus/minus ligger i toolbaren.',
        'Fit følger fortsat Mere canvas, panel-foldning og resize; manuel zoom forbliver fast. Device-skift går tilbage til Fit.',
        'Theme Shell forbliver OFF; Header/Footer afventer fortsat brugerens parity-QA.'
    ]
})
write(path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '''<h4>0.1.45</h4>
<ul>
<li>Tekst: lodret justering Top / Midt / Bund i canonical model, Designer og frontend.</li>
<li>Billede: eksplicit WordPress image/*-understøttelse, herunder PNG med transparens.</li>
<li>Footer: gammel Visual Header/Footer Builder er nu første migrationskilde; shell er fallback, og gammel Manager-standard er sidste tydeligt mærkede fallback.</li>
<li>Canvas: musehjulszoom 25-200 %, zoom omkring markøren, scrollbars ved overflow samt Fit/100%/−/+.</li>
<li>Theme Shell er fortsat deaktiveret.</li>
</ul>
''')

write('docs/v0145-status.md', '''# Visual Designer Manager 0.1.45 – status

Dato: 2026-08-29

## Implementeret

- VD-TEXT-VALIGN-001: Tekst har canonical `verticalAlign = top|center|bottom`; eksisterende modeller defaultes til `top`.
- VD-IMAGE-MIME-001: WordPress-mediavælgeren bruger `library.type = image`; PNG/JPG/WebP/GIF følger WordPress' billed-MIME-regler uden JPG-hardcoding.
- VD-FOOTER-LEGACY-SOURCE-001: Footer-kilder prioriteres old Visual Builder assignment/template → legacy shell → eksplicit standardfallback.
- VD-CANVAS-ZOOM-001: manuel 25-200% wheel-zoom, pointer-anchor, overflow-scrollbars og Fit/100%/−/+.
- Fit-mode følger editorbredden; manuel zoom ændres ikke af Inspector/Elementer/Mere canvas.
- Theme Shell cutover er fortsat OFF.

## QA-status

Kode-/modelkontrakter er dækket af release-gates. Bruger-QA af interaktion, Footer-kilde på testsite og browseradfærd afventer.
''')

path = 'CLEAN-TECHNICAL-MANUAL.md'
s = read(path)
marker = '## 22. Kontraktstatus for 0.1.45'
if marker not in s:
    s += r'''

---

## 22. Kontraktstatus for 0.1.45

### VD-TEXT-VALIGN-001 – IMPLEMENTERET, afventer bruger-QA

- Tekst har en canonical `verticalAlign` med værdierne `top`, `center`, `bottom`.
- Eksisterende Tekst uden property skal normaliseres til `top`, så gamle layouts ikke flytter sig.
- Inspector viser særskilt vandret og lodret justering.
- Designer, Preview og frontend skal bruge samme property.

### VD-IMAGE-MIME-001 – IMPLEMENTERET, afventer bruger-QA

- Billede-elementets medievælger filtrerer på WordPress `image/*`, ikke på en hårdkodet filendelse.
- PNG, inkl. alpha/transparens, må ikke konverteres eller flades ud af Visual Designer.
- JPG/JPEG, WebP, GIF og andre image-formater følger WordPress-installationens tilladte MIME-typer.
- SVG er kun tilgængelig hvis WordPress-installationen selv tillader SVG-upload.

### VD-FOOTER-LEGACY-SOURCE-001 – IMPLEMENTERET, afventer bruger-QA

Kildeprioritet ved gammel Footer-konvertering:

1. global Footer-assignment i den gamle Visual Header/Footer Builder;
2. præcis én gammel Footer-template hvis ingen global assignment findes;
3. gammel `HANGAR18-FOOTER-START/END` shell på Hjem eller anden side;
4. gammel Manager-standard som eksplicit fallback.

Hvis flere gamle Footer-templates findes uden entydig assignment, må systemet ikke gætte hvilken af dem der var aktiv. En standardfallback skal mærkes som fallback og må ikke beskrives som 1:1-konvertering.

### VD-CANVAS-ZOOM-001 – IMPLEMENTERET, afventer bruger-QA

- Virtuel viewport fra VD-WYSIWYG-VIEWPORT-001 ændres aldrig af zoom.
- Musehjul over canvas zoomer designet 25-200% i 10 procentpoint-trin.
- Zoom forankres omkring musemarkørens virtuelle punkt.
- Ved overflow viser canvas-host vandret/lodret scrollbar; Elementer, Inspector og toolbar zoomes ikke.
- `Fit` genberegnes ved ændret editorbredde, Mere canvas og panel-foldning.
- Manuel zoom forbliver fast ved de samme ændringer.
- Skift mellem Desktop/Laptop/Mobil går tilbage til `Fit` for den nye virtuelle viewport.
- Alle pointerbaserede layoutoperationer bruger fortsat den aktuelle viewport-scale til at oversætte skærmpixels til virtuelle layoutkoordinater.
'''
write(path, s)

print('Visual Designer Manager 0.1.45 patch prepared.')
