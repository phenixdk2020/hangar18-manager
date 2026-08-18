<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * I3.1 page chooser: pages exist independently from menu membership.
 * Read-only WordPress page discovery; menu mutations still go through MenuAdminController save.
 */
final class MenuPageChooserAdminController
{
    public static function register(): void
    {
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG && strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';
        $version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';
        $jsPath=dirname(__DIR__,2).'/assets/ultimate-designer-menu-pages.js';
        $cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-menu-pages.css';
        wp_enqueue_style('hangar18-ultimate-designer-menu-pages',plugins_url('assets/ultimate-designer-menu-pages.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
        wp_enqueue_script('hangar18-ultimate-designer-menu-pages',plugins_url('assets/ultimate-designer-menu-pages.js',$pluginFile),['hangar18-ultimate-designer-menu-admin'],$version.'-'.(string)(@filemtime($jsPath)?:0),true);
        wp_localize_script('hangar18-ultimate-designer-menu-pages','Hangar18MenuPages',['pages'=>self::pages()]);
    }

    /** @return list<array{Id:int,Title:string,Url:string,Status:string}> */
    private static function pages(): array
    {
        $posts=get_posts([
            'post_type'=>'page',
            'post_status'=>['publish','draft','private'],
            'posts_per_page'=>500,
            'orderby'=>['menu_order'=>'ASC','title'=>'ASC'],
            'order'=>'ASC',
        ]);
        if(!is_array($posts)){return [];}
        $out=[];
        foreach($posts as $post){
            if(!($post instanceof \WP_Post)){continue;}
            $id=(int)$post->ID;
            if($id<=0){continue;}
            $title=trim((string)get_the_title($id));
            if($title===''){$title='Side #'.$id;}
            $url=(string)get_permalink($id);
            $out[]=['Id'=>$id,'Title'=>$title,'Url'=>$url,'Status'=>(string)$post->post_status];
        }
        return $out;
    }
}
