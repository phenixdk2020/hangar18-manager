<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Additive tools for the existing Sider editor.
 *
 * Auto Boxes reuses the existing Grid + Container storage/runtime. Table reuses
 * the existing sanitized HTML element so this slice does not create a new public
 * renderer, schema migration, URL change or cutover path. Generic nesting also
 * reuses LayoutParentKey so normal elements can be placed inside a Box without a
 * parallel storage model.
 */
final class EditorLayoutToolsAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-layout-tools.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-layout-tools.css';
        $boxJsPath = $pluginDir . '/assets/ultimate-designer-box-tools.js';
        $boxCssPath = $pluginDir . '/assets/ultimate-designer-box-tools.css';
        $nestingJsPath = $pluginDir . '/assets/ultimate-designer-nesting-tools.js';
        $nestingCssPath = $pluginDir . '/assets/ultimate-designer-nesting-tools.css';
        $boxContentJsPath = $pluginDir . '/assets/ultimate-designer-box-content-layout.js';
        $boxContentCssPath = $pluginDir . '/assets/ultimate-designer-box-content-layout.css';
        $tableAppearanceJsPath = $pluginDir . '/assets/ultimate-designer-table-appearance.js';
        $tableAppearanceCssPath = $pluginDir . '/assets/ultimate-designer-table-appearance.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-layout-tools',
            $pluginUrl . 'assets/ultimate-designer-layout-tools.js',
            ['jquery', 'jquery-ui-sortable', 'hangar18-manager-admin'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-layout-tools',
            $pluginUrl . 'assets/ultimate-designer-layout-tools.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($boxJsPath) ? (string) filemtime($boxJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($boxCssPath) ? (string) filemtime($boxCssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.js',
            ['jquery', 'jquery-ui-sortable', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools', 'hangar18-ultimate-designer-box-tools'],
            is_file($nestingJsPath) ? (string) filemtime($nestingJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.css',
            ['hangar18-ultimate-designer-box-tools'],
            is_file($nestingCssPath) ? (string) filemtime($nestingCssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentJsPath) ? (string) filemtime($boxContentJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.css',
            ['hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentCssPath) ? (string) filemtime($boxContentCssPath) : '0.8.7'
        );

        self::enqueueV0810KasseRuntime();

        wp_enqueue_script(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceJsPath) ? (string) filemtime($tableAppearanceJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceCssPath) ? (string) filemtime($tableAppearanceCssPath) : '0.8.7'
        );
    }

    /**
     * v0.8.10 deliberately binds the Kasse composition to a handle that is
     * already proven to execute in the legacy Sider editor. The separate v0.8.9
     * visual-composition asset is therefore no longer authoritative.
     */
    private static function enqueueV0810KasseRuntime(): void
    {
        $css = <<<'CSS'
#h18-page-sections-sortable[data-h18-v0810-kasse-runtime="1"] .h18-page-section-row[data-h18-v0810-child-source="1"]:not(.is-selected){display:none!important}
.h18-v0810-runtime-badge{font-size:10px;font-weight:700;color:#135e96;background:#f0f6fc;border:1px solid #72aee6;border-radius:999px;padding:2px 7px;margin-left:8px}
.h18-v0810-child-list{display:flex;flex-direction:column;gap:10px}
.h18-v0810-child-card{border:1px solid #c3c4c7;border-radius:7px;background:#fff;overflow:hidden}
.h18-v0810-child-bar{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;padding:7px 9px;background:#f6f7f7;border-bottom:1px solid #dcdcde}
.h18-v0810-child-bar strong{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}
.h18-v0810-child-preview{padding:8px;background:#fff}
.h18-v0810-child-preview>.h18-canvas-preview{margin:0!important;pointer-events:none!important;box-shadow:none!important}
.h18-v0810-child-preview input,.h18-v0810-child-preview select,.h18-v0810-child-preview textarea,.h18-v0810-child-preview button{pointer-events:none!important}
.h18-v0810-side-zones{display:none;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0 0}
#h18-page-sections-sortable.h18-v0810-box-drag .h18-page-section-row[data-h18-box="1"]>.h18-canvas-preview>.h18-v0810-side-zones{display:grid}
.h18-v0810-side-zone{padding:12px 8px;border:2px dashed #72aee6;border-radius:7px;background:#f0f6fc;color:#135e96;text-align:center;font-size:12px;font-weight:700}
.h18-v0810-side-zone.is-active{border-color:#2271b1;background:#dceeff;box-shadow:0 0 0 3px rgba(34,113,177,.12)}
.h18-v0810-auto-grid{display:grid;grid-template-columns:repeat(var(--h18-v0810-cols,1),minmax(0,1fr));gap:var(--h18-v0810-gap,16px);align-items:stretch}
.h18-v0810-auto-box{min-width:0;border:1px solid #c3c4c7;border-radius:8px;background:#fff;overflow:hidden}
.h18-v0810-auto-box>.h18-v0810-child-bar{border-bottom:1px solid #dcdcde}
.h18-v0810-auto-box-preview{padding:8px}
@media(max-width:1180px){.h18-v0810-auto-grid{grid-template-columns:1fr!important}}
CSS;
        wp_add_inline_style('hangar18-ultimate-designer-nesting-tools', $css);

        $js = <<<'JS'
jQuery(function($){
'use strict';
var $s=$('#h18-page-sections-sortable');
if(!$s.length){return;}
var $ins=$('#h18-page-inspector-target');
var BOX='Kasse',AUTO='Auto-kasser',timer=null,guard=false,boxDrag=null,containerClick=null,existingBoxDrag=null;
function rows(){return $s.children('.h18-page-section-row:not(.h18-page-section-removed)');}
function ctl($r,sel){var $x=$r.find(sel);if($r.hasClass('is-selected')){$x=$x.add($ins.find(sel));}return $x;}
function key($r){return String($r.find('.h18-page-section-key').first().val()||'');}
function type($r){return String($r.attr('data-section-type')||'');}
function label($r){return String(ctl($r,'.h18-section-navigator-label').first().val()||'').trim();}
function parent($r){return String(ctl($r,'.h18-layout-parent-key').first().val()||'');}
function byKey(k){k=String(k||'');return rows().filter(function(){return key($(this))===k;}).first();}
function isBox($r){return !!($r&&$r.length&&type($r)==='container'&&label($r).indexOf(BOX)===0);}
function isAuto($r){return !!($r&&$r.length&&type($r)==='grid'&&label($r)===AUTO);}
function children($r){var k=key($r);return rows().filter(function(){return parent($(this))===k;});}
function snapshot(){var x={};rows().each(function(){var k=key($(this));if(k){x[k]=1;}});return x;}
function findNew(before,t){var $n=$();rows().each(function(){var $r=$(this),k=key($r);if(k&&!before[k]&&(!t||type($r)===t)){$n=$r;}});return $n;}
function setParent($r,k){var $h=ctl($r,'.h18-layout-parent-key').first(),$q=ctl($r,'.h18-layout-parent-select').first();if(!$h.length){return false;}$h.val(String(k||'')).trigger('change');if($q.length){$q.val(String(k||'')).trigger('change');}$r.attr('data-h18-nested-in-box',String(k||''));return true;}
function setLabel($r,v){var $f=ctl($r,'.h18-section-navigator-label').first();if($f.length&&String($f.val()||'')!==String(v)){$f.val(v).trigger('input').trigger('change');}}
function setField($r,n,v){var $f=ctl($r,'[name$="['+n+']"]').first();if(!$f.length){return;}if($f.is(':checkbox')){var b=!!v;if($f.is(':checked')===b){return;}$f.prop('checked',b).trigger('change');}else{if(String($f.val()||'')===String(v)){return;}$f.val(String(v)).trigger('input').trigger('change');}}
function configBox($r){if(!$r.length||type($r)!=='container'){return;}setLabel($r,BOX);setField($r,'Title','');setField($r,'Content','');setField($r,'LayoutDirection','Column');setField($r,'LayoutWrap',true);setField($r,'LayoutAlign','Stretch');setField($r,'LayoutGapPx',12);setField($r,'MobileLayoutGapPx',10);setField($r,'MobileLayoutStack',true);$r.attr('data-h18-box','1');}
function configAuto($r){if(!$r.length||type($r)!=='grid'){return;}setLabel($r,AUTO);setField($r,'Title','');setField($r,'Content','');setField($r,'LayoutColumns',2);setField($r,'MobileLayoutColumns',1);setField($r,'LayoutGapPx',16);setField($r,'MobileLayoutGapPx',12);setField($r,'LayoutAlign','Stretch');setParent($r,'');}
function syncOrder(){var i=0;$s.children('.h18-page-section-row').each(function(){var $r=$(this);if($r.hasClass('h18-page-section-removed')){return;}i++;$r.find('.h18-page-section-order').val(i*10);});if($s.hasClass('ui-sortable')){$s.sortable('refresh');}}
function name($r){var n=label($r);if(n&&n!==BOX){return n;}var t=String($r.find('.h18-page-section-title-summary').first().text()||'').trim();if(t){return t;}var m={text:'Tekst',image:'Billede',buttons:'Knap',hero:'Hero',text_image:'Tekst + billede',container:'Kasse',grid:'Grid',flex:'Flex',html:'HTML',shortcode:'Shortcode',embed:'Embed',divider:'Skillelinje',spacer:'Spacer',list:'Liste',quote:'Citat'};return m[type($r)]||type($r)||'Element';}
function clonePreview($r){var $p=$r.children('.h18-canvas-preview').first();if(!$p.length){return $();}var $c=$p.clone(false,false);$c.removeAttr('id');$c.find('[id]').removeAttr('id');$c.find('[name]').removeAttr('name');$c.find('.h18-ud-box-contents-preview,.h18-ud-auto-box-canvas,.h18-v0810-side-zones').remove();$c.find('input,select,textarea,button').prop('disabled',true).attr('tabindex','-1');$c.find('a').attr('tabindex','-1');return $c;}
function ensureBoxUi($b){if(!isBox($b)){return;}var $p=$b.children('.h18-canvas-preview').first();if(!$p.length){return;}$b.attr('data-h18-box','1');var $wrap=$p.find('.h18-ud-box-contents-preview').first();if(!$wrap.length){$wrap=$('<div>',{'class':'h18-ud-box-contents-preview'}).append($('<div>',{'class':'h18-ud-box-contents-head'}),$('<div>',{'class':'h18-ud-box-contents-items'}),$('<div>',{'class':'h18-ud-box-drop-zone',text:'Træk et element hertil for at lægge det IND I kassen'}));$p.append($wrap);}var $kids=children($b),$head=$wrap.find('.h18-ud-box-contents-head').first(),$items=$wrap.find('.h18-ud-box-contents-items').first();$head.empty().append($('<strong>',{text:'Indhold i kassen'}),$('<span>',{text:$kids.length+' element'+($kids.length===1?'':'er')}),$('<em>',{'class':'h18-v0810-runtime-badge',text:'v0.8.10'}));$items.empty().addClass('h18-v0810-child-list');if(!$kids.length){$items.append($('<div>',{'class':'h18-ud-box-empty-drop',text:'Kassen er tom.'}));}else{$kids.each(function(){var $k=$(this),kk=key($k),$card=$('<section>',{'class':'h18-v0810-child-card','data-h18-v0810-child':kk}),$bar=$('<div>',{'class':'h18-v0810-child-bar'}).append($('<strong>',{text:name($k)}),$('<button>',{type:'button','class':'button button-small h18-v0810-edit','data-h18-v0810-edit':kk,text:'Rediger'})),$body=$('<div>',{'class':'h18-v0810-child-preview'}),$cl=clonePreview($k);if($cl.length){$body.append($cl);}else{$body.text(name($k));}$card.append($bar,$body);$items.append($card);});}
if(!parent($b)&&!$p.children('.h18-v0810-side-zones').length){$p.append($('<div>',{'class':'h18-v0810-side-zones'}).append($('<div>',{'class':'h18-v0810-side-zone','data-side':'left','data-box':key($b),text:'← Sæt Kasse ved siden af'}),$('<div>',{'class':'h18-v0810-side-zone','data-side':'right','data-box':key($b),text:'Sæt Kasse ved siden af →'})));}}
function ensureAutoUi($a){if(!isAuto($a)){return;}var $boxes=children($a).filter(function(){return isBox($(this));}),count=$boxes.length,cols=Math.max(1,Math.min(6,count||1)),gap=parseInt(String(ctl($a,'[name$="[LayoutGapPx]"]').first().val()||16),10)||16;$a.attr('data-h18-v0810-auto','1');setField($a,'LayoutColumns',cols);var $p=$a.children('.h18-canvas-preview').first();if(!$p.length){return;}var $grid=$p.find('.h18-ud-auto-box-grid').first();if(!$grid.length){$grid=$('<div>',{'class':'h18-ud-auto-box-grid'});$p.append($grid);}$grid.empty().addClass('h18-v0810-auto-grid').css({'--h18-v0810-cols':String(cols),'--h18-v0810-gap':gap+'px'});$boxes.each(function(i){var $b=$(this),bk=key($b),$tile=$('<section>',{'class':'h18-v0810-auto-box','data-h18-v0810-box':bk}),$bar=$('<div>',{'class':'h18-v0810-child-bar'}).append($('<strong>',{text:'Kasse '+(i+1)}),$('<button>',{type:'button','class':'button button-small h18-v0810-edit','data-h18-v0810-edit':bk,text:'Rediger Kasse'})),$body=$('<div>',{'class':'h18-v0810-auto-box-preview'}),$cl=clonePreview($b);if($cl.length){$body.append($cl);}$tile.append($bar,$body);$grid.append($tile);});}
function refresh(){if(guard){return;}guard=true;$s.attr('data-h18-v0810-kasse-runtime','1');rows().each(function(){var $r=$(this);if(isBox($r)){ensureBoxUi($r);}});rows().each(function(){var $r=$(this);if(isAuto($r)){ensureAutoUi($r);}});rows().each(function(){var $r=$(this),$p=byKey(parent($r)),hide=isBox($p)||isAuto($p);$r.attr('data-h18-v0810-child-source',hide?'1':'0');});guard=false;}
function schedule(ms){window.clearTimeout(timer);timer=window.setTimeout(refresh,typeof ms==='number'?ms:80);}
function createAutoForBoxes($source,$target,side){var beforeGrid=snapshot(),$gridBtn=$('.h18-builder-palette-item[data-section-type="grid"]').not('[data-h18-layout-tool]').first();if(!$gridBtn.length){schedule(40);return;}$gridBtn.trigger('click');window.setTimeout(function(){var $g=findNew(beforeGrid,'grid');if(!$g.length){schedule(40);return;}configAuto($g);var gk=key($g);setParent($source,gk);setParent($target,gk);$g.insertBefore($target);if(side==='left'){$source.insertAfter($g);$target.insertAfter($source);}else{$target.insertAfter($g);$source.insertAfter($target);}syncOrder();schedule(60);},100);}
function placeBoxBeside($source,$target,side){if(!$source.length||!$target.length||!isBox($source)||!isBox($target)||key($source)===key($target)){schedule(40);return;}var $targetAuto=byKey(parent($target));if(isAuto($targetAuto)){setParent($source,key($targetAuto));if(side==='left'){$source.insertBefore($target);}else{$source.insertAfter($target);}syncOrder();schedule(60);return;}createAutoForBoxes($source,$target,side);}
function finishContainer(before,target,side){window.setTimeout(function(){var $n=findNew(before,'container');if(!$n.length){schedule(50);return;}if(!isBox($n)){configBox($n);}if(!target){schedule(30);return;}placeBoxBeside($n,byKey(target),side);},120);}
function sideZoneAtPoint(pageX,pageY,sourceKey){var clientX=Number(pageX)-(window.pageXOffset||document.documentElement.scrollLeft||0),clientY=Number(pageY)-(window.pageYOffset||document.documentElement.scrollTop||0),hit=null;$('.h18-v0810-side-zone').each(function(){var z=this,target=String(z.getAttribute('data-box')||'');if(!target||target===sourceKey){return;}var rect=z.getBoundingClientRect();if(clientX>=rect.left&&clientX<=rect.right&&clientY>=rect.top&&clientY<=rect.bottom){hit={target:target,side:String(z.getAttribute('data-side')||'right'),node:z};}});return hit;}
$(document).on('click','.h18-v0810-edit',function(e){e.preventDefault();e.stopPropagation();var $r=byKey($(this).attr('data-h18-v0810-edit'));if(!$r.length){return;}var $h=$r.children('.h18-page-section-header').first();($h.length?$h:$r).trigger('click');schedule(150);});
document.addEventListener('click',function(e){var item=e.target.closest&&e.target.closest('.h18-builder-palette-item[data-section-type="container"]');if(!item||item.hasAttribute('data-h18-layout-tool')){return;}containerClick=snapshot();window.setTimeout(function(){var $n=findNew(containerClick,'container');if($n.length&&!isBox($n)){configBox($n);}containerClick=null;schedule(100);},80);},true);
document.addEventListener('dragstart',function(e){var item=e.target.closest&&e.target.closest('.h18-builder-palette-item');if(!item){return;}var tool=String(item.getAttribute('data-h18-layout-tool')||''),t=String(item.getAttribute('data-section-type')||'');if(tool!=='box'&&t!=='container'){return;}boxDrag={before:snapshot(),target:'',side:'right'};$s.addClass('h18-v0810-box-drag');schedule(0);},true);
document.addEventListener('dragover',function(e){if(!boxDrag){return;}var z=e.target.closest&&e.target.closest('.h18-v0810-side-zone');$('.h18-v0810-side-zone').removeClass('is-active');if(z){e.preventDefault();z.classList.add('is-active');boxDrag.target=String(z.getAttribute('data-box')||'');boxDrag.side=String(z.getAttribute('data-side')||'right');}},true);
document.addEventListener('drop',function(e){if(!boxDrag){return;}var z=e.target.closest&&e.target.closest('.h18-v0810-side-zone');if(z){e.preventDefault();boxDrag.target=String(z.getAttribute('data-box')||'');boxDrag.side=String(z.getAttribute('data-side')||'right');}var d=boxDrag;boxDrag=null;$s.removeClass('h18-v0810-box-drag');$('.h18-v0810-side-zone').removeClass('is-active');finishContainer(d.before,d.target,d.side);},true);
document.addEventListener('dragend',function(){if(!boxDrag){return;}var d=boxDrag;boxDrag=null;$s.removeClass('h18-v0810-box-drag');$('.h18-v0810-side-zone').removeClass('is-active');finishContainer(d.before,d.target,d.side);},true);
$s.on('sortstart.h18V0810BoxSide',function(event,ui){var $row=ui&&ui.item?ui.item:$();if(!isBox($row)){return;}existingBoxDrag={source:key($row),target:'',side:'right'};$s.addClass('h18-v0810-box-drag');schedule(0);});
$s.on('sort.h18V0810BoxSide',function(event){if(!existingBoxDrag){return;}var hit=sideZoneAtPoint(event.pageX,event.pageY,existingBoxDrag.source);$('.h18-v0810-side-zone').removeClass('is-active');if(hit){existingBoxDrag.target=hit.target;existingBoxDrag.side=hit.side;$(hit.node).addClass('is-active');}else{existingBoxDrag.target='';}});
$s.on('sortstop.h18V0810BoxSide',function(){if(!existingBoxDrag){return;}var d=existingBoxDrag;existingBoxDrag=null;$s.removeClass('h18-v0810-box-drag');$('.h18-v0810-side-zone').removeClass('is-active');if(d.target){placeBoxBeside(byKey(d.source),byKey(d.target),d.side);}else{schedule(60);}});
$(document).on('change input','.h18-layout-parent-key,.h18-layout-parent-select,.h18-section-navigator-label',function(){schedule(40);});
$(document).on('input change','#h18-page-inspector-target :input',function(){schedule(100);});
$(document).on('click','.h18-preview-device,.h18-preview-state',function(){schedule(140);});
$(document).on('click','.h18-builder-palette-item,.h18-page-section-delete,.h18-page-section-duplicate,.h18-page-section-header,.h18-page-section-edit',function(){schedule(140);});
var mo=new MutationObserver(function(){if(!guard){schedule(100);}});mo.observe($s.get(0),{childList:true,subtree:false});
schedule(220);
});
JS;
        wp_add_inline_script('hangar18-ultimate-designer-box-content-layout', $js, 'after');
    }
}
