<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Frontend;

/**
 * Keeps pure Image elements inside their own box without default Cover crop.
 *
 * Auto/original aspect images use contain semantics. Explicit aspect-ratio
 * choices keep the configured ImageFit value from the canonical renderer.
 */
final class ImageElementFrontendRuntime
{
    public static function register(): void
    {
        add_action('wp_head', [self::class, 'render'], 1003);
    }

    public static function render(): void
    {
        if (!is_singular('page')) {
            return;
        }

        echo <<<'HTML'
<style id="h18-image-element-parity-v0887">
.h18-editor-image{
    box-sizing:border-box;
    width:100%;
    max-width:100%;
    margin:0;
    min-width:0;
}
.h18-editor-image img{
    box-sizing:border-box;
    max-width:100%!important;
}
</style>
<script id="h18-image-element-parity-runtime-v0887">
(function(){
    'use strict';
    function apply(){
        document.querySelectorAll('.h18-editor-section').forEach(function(section){
            var figure=null;
            Array.prototype.some.call(section.children||[],function(child){
                if(child.classList&&child.classList.contains('h18-editor-image')){figure=child;return true;}
                return false;
            });
            if(!figure){return;}
            var image=figure.querySelector('img');
            if(!image){return;}
            var style=window.getComputedStyle(section);
            var aspect=String(style.getPropertyValue('--h18-image-aspect')||'auto').trim().toLowerCase();
            figure.style.boxSizing='border-box';
            figure.style.width='100%';
            figure.style.maxWidth='100%';
            figure.style.margin='0';
            image.style.boxSizing='border-box';
            image.style.maxWidth='100%';
            if(!aspect||aspect==='auto'){
                section.setAttribute('data-h18-v0887-image-fit','auto-contain');
                image.style.objectFit='contain';
            }else{
                section.removeAttribute('data-h18-v0887-image-fit');
            }
        });
        document.documentElement.setAttribute('data-h18-image-element-parity','0.8.87');
    }
    if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',apply,{once:true});}
    else{apply();}
})();
</script>
HTML;
    }
}
