<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionMenuRepository;
use Hangar18\UltimateDesigner\SiteBuilder\MenuPresentationNormalizer;
use Hangar18\UltimateDesigner\SiteBuilder\MenuService;
use Hangar18\UltimateDesigner\SiteBuilder\MenuTreeValidator;
use RuntimeException;

/** I3 shadow-only Menu UI v2. Never replaces the legacy/public WordPress menu. */
final class MenuAdminController
{
    private const NONCE_ACTION='h18_ud_menu_v2';
    /** @var list<string> */
    private const TYPES=['page','url','taxonomy','dynamic','anchor','action'];

    public static function register(): void
    {
        add_action('admin_post_h18_ud_create_menu',[self::class,'create']);
        add_action('admin_post_h18_ud_save_menu',[self::class,'save']);
        add_action('admin_post_h18_ud_delete_menu',[self::class,'delete']);
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG && strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';
        $jsPath=dirname(__DIR__,2).'/assets/ultimate-designer-menu-admin.js';
        $cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-menu-admin.css';
        $version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';
        wp_enqueue_style('hangar18-ultimate-designer-menu-admin',plugins_url('assets/ultimate-designer-menu-admin.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
        wp_enqueue_script('hangar18-ultimate-designer-menu-admin',plugins_url('assets/ultimate-designer-menu-admin.js',$pluginFile),[],$version.'-'.(string)(@filemtime($jsPath)?:0),true);
    }

    public static function renderPanel(): void
    {
        $service=self::service();
        $menus=$service->all();
        $selectedId=isset($_GET['ud_menu'])?sanitize_key((string)wp_unslash($_GET['ud_menu'])):'';
        $selected=$selectedId!==''?$service->get($selectedId):null;

        echo '<section class="h18-ud-menu-panel">';
        echo '<div class="h18-ud-builder-panel-head"><div><h2>I3 · Menu UI v2</h2><p>Redigér menu-data og præsentationspresets i shadow mode. Den offentlige menu ændres ikke.</p></div><span class="h18-ud-shadow-badge">SHADOW · legacy menu er aktiv</span></div>';
        self::renderCreate();
        self::renderList($menus,$selectedId);
        if(is_array($selected)){self::renderEditor($selected);}else{echo '<div class="h18-ud-empty-editor"><strong>Vælg eller opret en menu.</strong><p>Menuen kan bygges og keyboard-testes her uden frontend-cutover.</p></div>';}
        echo '</section>';
    }

    public static function create(): void
    {
        self::guard();
        $name=sanitize_text_field((string)($_POST['menu_name']??''));
        if($name===''){$name='Ny menu';}
        try{
            $menu=self::service()->create($name,self::starterItems(),null,[]);
            self::redirect((string)$menu['Id'],'created','Menu oprettet i shadow mode.');
        }catch(\Throwable $e){self::redirect('','error',$e->getMessage());}
    }

    public static function save(): void
    {
        self::guard();
        $id=sanitize_key((string)($_POST['menu_id']??''));
        $name=sanitize_text_field((string)($_POST['menu_name']??''));
        try{
            if($id===''){throw new RuntimeException('Menu-id mangler.');}
            if($name===''){$name=$id;}
            $menu=self::service()->update($id,$name,self::postedItems(),self::postedPresentation());
            self::redirect((string)$menu['Id'],'saved','Menu gemt i shadow mode. Den offentlige menu er uændret.');
        }catch(\Throwable $e){self::redirect($id,'error',$e->getMessage());}
    }

    public static function delete(): void
    {
        self::guard();
        $id=sanitize_key((string)($_POST['menu_id']??''));
        try{
            if($id===''){throw new RuntimeException('Menu-id mangler.');}
            self::service()->delete($id);
            self::redirect('','deleted','Shadow-menu slettet.');
        }catch(\Throwable $e){self::redirect($id,'error',$e->getMessage());}
    }

    /** @return list<array<string,mixed>> */
    private static function postedItems(): array
    {
        $raw=isset($_POST['items'])&&is_array($_POST['items'])?wp_unslash($_POST['items']):[];
        $items=[];$seen=[];$order=10;
        foreach(array_slice($raw,0,200) as $index=>$row){
            if(!is_array($row)||!empty($row['Remove'])){continue;}
            $id=sanitize_key((string)($row['Id']??''));
            if($id===''){$id='item-'.($index+1);}
            if(isset($seen[$id])){throw new RuntimeException("Menupunkt-id '{$id}' findes mere end én gang.");}
            $seen[$id]=true;
            $type=sanitize_key((string)($row['Type']??'url'));
            if(!in_array($type,self::TYPES,true)){$type='url';}
            $label=sanitize_text_field((string)($row['Label']??''));
            if($label===''){throw new RuntimeException("Menupunkt '{$id}' mangler tekst/label.");}
            $items[]=[
                'Id'=>$id,
                'ParentId'=>sanitize_key((string)($row['ParentId']??'')),
                'Order'=>$order,
                'Type'=>$type,
                'Label'=>$label,
                'Target'=>sanitize_text_field((string)($row['Target']??'')),
                'Url'=>self::safeUrl((string)($row['Url']??'')),
                'Icon'=>mb_substr(sanitize_text_field((string)($row['Icon']??'')),0,80),
                'Badge'=>mb_substr(sanitize_text_field((string)($row['Badge']??'')),0,40),
                'Description'=>mb_substr(sanitize_text_field((string)($row['Description']??'')),0,240),
                'OpenNew'=>!empty($row['OpenNew']),
                'ComponentId'=>sanitize_key((string)($row['ComponentId']??'')),
            ];
            $order+=10;
        }
        return $items;
    }

    /** @return array<string,mixed> */
    private static function postedPresentation(): array
    {
        $raw=isset($_POST['presentation'])&&is_array($_POST['presentation'])?wp_unslash($_POST['presentation']):[];
        return (new MenuPresentationNormalizer())->normalize([
            'DesktopPreset'=>sanitize_key((string)($raw['DesktopPreset']??'classic')),
            'MobilePreset'=>sanitize_key((string)($raw['MobilePreset']??'off-canvas-mobile')),
            'MotionPreset'=>sanitize_key((string)($raw['MotionPreset']??'motion-underline')),
            'BreakpointPx'=>(int)($raw['BreakpointPx']??900),
            'MegaColumns'=>(int)($raw['MegaColumns']??4),
            'MobileToggleLabel'=>sanitize_text_field((string)($raw['MobileToggleLabel']??'Menu')),
            'AriaLabel'=>sanitize_text_field((string)($raw['AriaLabel']??'Hovedmenu')),
            'ShowIcons'=>!empty($raw['ShowIcons']),
            'ShowBadges'=>!empty($raw['ShowBadges']),
        ]);
    }

    /** @return list<array<string,mixed>> */
    private static function starterItems(): array
    {
        return [
            ['Id'=>'home','ParentId'=>'','Order'=>10,'Type'=>'url','Label'=>'Hjem','Target'=>'','Url'=>'/','Icon'=>'','Badge'=>'','Description'=>'','OpenNew'=>false,'ComponentId'=>''],
            ['Id'=>'about','ParentId'=>'','Order'=>20,'Type'=>'url','Label'=>'Om','Target'=>'','Url'=>'/om-foreningen/','Icon'=>'','Badge'=>'','Description'=>'','OpenNew'=>false,'ComponentId'=>''],
            ['Id'=>'contact','ParentId'=>'','Order'=>30,'Type'=>'url','Label'=>'Kontakt','Target'=>'','Url'=>'/kontakt/','Icon'=>'','Badge'=>'','Description'=>'','OpenNew'=>false,'ComponentId'=>''],
        ];
    }

    /** @param array<string,array<string,mixed>> $menus */
    private static function renderList(array $menus,string $selectedId): void
    {
        echo '<div class="h18-ud-menu-list"><h3>Shadow-menuer</h3>';
        if($menus===[]){echo '<p class="description">Ingen menu-data endnu.</p>';}
        foreach($menus as $menu){
            $id=(string)($menu['Id']??'');
            $url=add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_menu'=>$id],admin_url('admin.php'));
            $presentation=(new MenuPresentationNormalizer())->normalize(is_array($menu['Presentation']??null)?$menu['Presentation']:[]);
            echo '<a class="h18-ud-menu-link'.($selectedId===$id?' is-active':'').'" href="'.esc_url($url).'"><span><strong>'.esc_html((string)($menu['Name']??$id)).'</strong><small>'.count((array)($menu['Items']??[])).' punkter · rev '.(int)($menu['Revision']??1).'</small></span><code>'.esc_html((string)$presentation['DesktopPreset']).' / '.esc_html((string)$presentation['MobilePreset']).'</code></a>';
        }
        echo '</div>';
    }

    private static function renderCreate(): void
    {
        echo '<form class="h18-ud-menu-create" method="post" action="'.esc_url(admin_url('admin-post.php')).'">';
        wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="h18_ud_create_menu"><input type="text" name="menu_name" placeholder="Navn på ny menu" aria-label="Menunavn"><button class="button" type="submit">+ Ny shadow-menu</button></form>';
    }

    /** @param array<string,mixed> $menu */
    private static function renderEditor(array $menu): void
    {
        $id=(string)$menu['Id'];
        $items=is_array($menu['Items']??null)?array_values($menu['Items']):[];
        $presentation=(new MenuPresentationNormalizer())->normalize(is_array($menu['Presentation']??null)?$menu['Presentation']:[]);
        $options=(new MenuPresentationNormalizer())->options();

        echo '<form class="h18-ud-menu-editor" method="post" action="'.esc_url(admin_url('admin-post.php')).'">';
        wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="h18_ud_save_menu"><input type="hidden" name="menu_id" value="'.esc_attr($id).'">';
        echo '<div class="h18-ud-menu-toolbar"><div><strong>MENU · '.esc_html($id).'</strong><small>Revision '.(int)($menu['Revision']??1).'</small></div><label>Navn<input type="text" name="menu_name" value="'.esc_attr((string)($menu['Name']??'')).'"></label><button class="button button-primary" type="submit">Gem menu</button></div>';

        echo '<div class="h18-ud-menu-presentation"><h3>Præsentation</h3><p class="description">Samme menu-data kan få forskellig desktop/mobile præsentation. Det er kun admin-preview i I3.</p><div class="h18-ud-menu-preset-grid">';
        self::presetSelect('DesktopPreset','Desktop preset',(string)$presentation['DesktopPreset'],$options['Desktop']);
        self::presetSelect('MobilePreset','Mobil preset',(string)$presentation['MobilePreset'],$options['Mobile']);
        self::presetSelect('MotionPreset','Hover/aktiv effekt',(string)$presentation['MotionPreset'],$options['Motion']);
        self::numberInput('BreakpointPx','Mobil breakpoint (px)',(int)$presentation['BreakpointPx'],480,1400);
        self::numberInput('MegaColumns','Mega-menu kolonner',(int)$presentation['MegaColumns'],3,5);
        self::textPresentation('MobileToggleLabel','Mobilknap',(string)$presentation['MobileToggleLabel']);
        self::textPresentation('AriaLabel','ARIA label',(string)$presentation['AriaLabel']);
        echo '<label class="h18-ud-check"><input type="hidden" name="presentation[ShowIcons]" value="0"><input type="checkbox" name="presentation[ShowIcons]" value="1"'.checked(!empty($presentation['ShowIcons']),true,false).'> Vis ikoner</label>';
        echo '<label class="h18-ud-check"><input type="hidden" name="presentation[ShowBadges]" value="0"><input type="checkbox" name="presentation[ShowBadges]" value="1"'.checked(!empty($presentation['ShowBadges']),true,false).'> Vis badges</label>';
        echo '</div><div id="h18-ud-menu-preset-info" class="h18-ud-menu-preset-info" aria-live="polite"></div></div>';

        echo '<div class="h18-ud-menu-workspace"><div><div class="h18-ud-element-list-head"><div><h3>Menupunkter</h3><p class="description">Træk for rækkefølge. Brug →/← til at gøre punktet til underpunkt eller flytte det ud.</p></div><button type="button" class="button" id="h18-ud-add-menu-item">+ Menupunkt</button></div>';
        echo '<div id="h18-ud-menu-item-list" data-next-index="'.count($items).'">';
        foreach($items as $index=>$item){self::renderItem($index,is_array($item)?$item:[]);}
        echo '</div></div><aside class="h18-ud-menu-preview"><h3>Keyboard-preview</h3><p class="description">Tab, ←/→, ↑/↓ og Escape kan testes her. Ikke offentlig frontend.</p><div id="h18-ud-menu-preview" tabindex="-1"></div></aside></div>';
        echo '</form>';

        echo '<form class="h18-ud-delete-menu" method="post" action="'.esc_url(admin_url('admin-post.php')).'" onsubmit="return confirm(\'Slet denne shadow-menu?\');">';
        wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="h18_ud_delete_menu"><input type="hidden" name="menu_id" value="'.esc_attr($id).'"><button class="button-link-delete" type="submit">Slet shadow-menu</button></form>';
    }

    /** @param array<string,mixed> $item */
    private static function renderItem(int $index,array $item): void
    {
        $id=(string)($item['Id']??('item-'.($index+1)));
        echo '<article class="h18-ud-menu-item-card" data-index="'.$index.'">';
        echo '<div class="h18-ud-template-element-head"><span class="dashicons dashicons-move h18-ud-menu-drag" aria-hidden="true"></span><strong class="h18-ud-menu-summary">'.esc_html((string)($item['Label']??$id)).'</strong><span class="h18-ud-move-controls"><button type="button" class="button-link h18-ud-menu-up" aria-label="Flyt op">↑</button><button type="button" class="button-link h18-ud-menu-down" aria-label="Flyt ned">↓</button><button type="button" class="button-link h18-ud-menu-outdent" aria-label="Flyt et niveau ud">←</button><button type="button" class="button-link h18-ud-menu-indent" aria-label="Gør til underpunkt">→</button></span><button type="button" class="button-link-delete h18-ud-remove-menu-item">Fjern</button></div>';
        echo '<div class="h18-ud-menu-item-grid">';
        self::itemText($index,'Id','Id',$id);
        self::itemText($index,'ParentId','Parent Id',(string)($item['ParentId']??''),'h18-ud-menu-parent');
        echo '<label>Type<select name="items['.$index.'][Type]" class="h18-ud-menu-type">';foreach(self::TYPES as $type){echo '<option value="'.esc_attr($type).'"'.selected((string)($item['Type']??'url'),$type,false).'>'.esc_html($type).'</option>';}echo '</select></label>';
        self::itemText($index,'Label','Tekst/label',(string)($item['Label']??''),'h18-ud-menu-label');
        self::itemText($index,'Url','URL',(string)($item['Url']??''));
        self::itemText($index,'Target','Target/anchor',(string)($item['Target']??''));
        self::itemText($index,'Icon','Ikon',(string)($item['Icon']??''));
        self::itemText($index,'Badge','Badge',(string)($item['Badge']??''));
        self::itemText($index,'Description','Beskrivelse',(string)($item['Description']??''),'','is-wide');
        self::itemText($index,'ComponentId','Mega-panel ComponentId',(string)($item['ComponentId']??''),'h18-ud-component-id','is-wide');
        echo '<label class="h18-ud-check"><input type="hidden" name="items['.$index.'][OpenNew]" value="0"><input type="checkbox" name="items['.$index.'][OpenNew]" value="1"'.checked(!empty($item['OpenNew']),true,false).'> Åbn i nyt vindue</label>';
        echo '<input type="hidden" name="items['.$index.'][Remove]" value="0" class="h18-ud-menu-remove">';
        echo '</div></article>';
    }

    /** @param array<string,array<string,mixed>> $options */
    private static function presetSelect(string $field,string $label,string $value,array $options): void
    {
        echo '<label>'.esc_html($label).'<select name="presentation['.esc_attr($field).']" data-menu-preset="'.esc_attr($field).'">';
        foreach($options as $key=>$option){echo '<option value="'.esc_attr((string)$key).'"'.selected($value,(string)$key,false).'>'.esc_html((string)($option['Label']??$key)).'</option>';}
        echo '</select></label>';
    }
    private static function numberInput(string $field,string $label,int $value,int $min,int $max): void{echo '<label>'.esc_html($label).'<input type="number" min="'.$min.'" max="'.$max.'" name="presentation['.esc_attr($field).']" value="'.$value.'"></label>';}
    private static function textPresentation(string $field,string $label,string $value): void{echo '<label>'.esc_html($label).'<input type="text" name="presentation['.esc_attr($field).']" value="'.esc_attr($value).'"></label>';}
    private static function itemText(int $index,string $field,string $label,string $value,string $class='',string $wrapper=''): void{echo '<label class="'.esc_attr($wrapper).'">'.esc_html($label).'<input type="text" name="items['.$index.']['.esc_attr($field).']" value="'.esc_attr($value).'" class="'.esc_attr($class).'"></label>';}

    private static function service(): MenuService{return new MenuService(new WordPressOptionMenuRepository(),new MenuTreeValidator(),new MenuPresentationNormalizer());}
    private static function guard(): void{if(!current_user_can('edit_pages')){wp_die(esc_html__('Du har ikke rettigheder til denne handling.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}

    private static function safeUrl(string $value): string
    {
        $value=trim($value);
        if($value===''||$value==='#'){return $value;}
        if(preg_match('/^(javascript|data|vbscript):/i',$value)){return '';}
        if($value[0]==='/'||$value[0]==='#'){return sanitize_text_field($value);}
        return (string)esc_url_raw($value,['http','https','mailto','tel']);
    }

    private static function redirect(string $menuId,string $status,string $message): void
    {
        $args=['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>$message];
        if($menuId!==''){$args['ud_menu']=$menuId;}
        wp_safe_redirect(add_query_arg($args,admin_url('admin.php')));exit;
    }
}
