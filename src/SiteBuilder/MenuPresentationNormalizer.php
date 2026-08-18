<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

/**
 * I3/UD-064..072 presentation settings for one generic menu tree.
 * Menu data remains independent from where/how it is rendered.
 */
final class MenuPresentationNormalizer
{
    /** @var list<string> */
    private const DESKTOP = ['classic','floating-pill','mega-menu','side-rail'];
    /** @var list<string> */
    private const MOBILE = ['classic','off-canvas-mobile','fullscreen-overlay','bottom-mobile'];
    /** @var list<string> */
    private const MOTION = ['none','motion-underline','motion-pill','motion-slide','motion-icon'];

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function normalize(array $raw): array
    {
        $desktop = strtolower(trim((string) ($raw['DesktopPreset'] ?? 'classic')));
        $mobile = strtolower(trim((string) ($raw['MobilePreset'] ?? 'off-canvas-mobile')));
        $motion = strtolower(trim((string) ($raw['MotionPreset'] ?? 'motion-underline')));
        if (!in_array($desktop,self::DESKTOP,true)) { $desktop='classic'; }
        if (!in_array($mobile,self::MOBILE,true)) { $mobile='off-canvas-mobile'; }
        if (!in_array($motion,self::MOTION,true)) { $motion='motion-underline'; }

        $normalized = [
            'SchemaVersion'=>'1.0',
            'DesktopPreset'=>$desktop,
            'MobilePreset'=>$mobile,
            'MotionPreset'=>$motion,
            'BreakpointPx'=>$this->clamp($raw['BreakpointPx'] ?? 900,480,1400),
            'MegaColumns'=>$this->clamp($raw['MegaColumns'] ?? 4,3,5),
            'MobileToggleLabel'=>$this->text($raw['MobileToggleLabel'] ?? 'Menu',40,'Menu'),
            'AriaLabel'=>$this->text($raw['AriaLabel'] ?? 'Hovedmenu',120,'Hovedmenu'),
            'ShowIcons'=>array_key_exists('ShowIcons',$raw) ? (bool) $raw['ShowIcons'] : true,
            'ShowBadges'=>array_key_exists('ShowBadges',$raw) ? (bool) $raw['ShowBadges'] : true,
        ];

        // Validate catalog-backed presets now so renamed/deleted preset keys cannot
        // silently enter stored menu presentation state.
        foreach ([$desktop,$mobile,$motion] as $preset) {
            if (in_array($preset,['classic','none'],true)) { continue; }
            SiteBuilderPresetCatalog::get($preset);
        }
        return $normalized;
    }

    /** @return array<string,array<string,mixed>> */
    public function options(): array
    {
        $catalog=SiteBuilderPresetCatalog::all();
        $make=static function(array $keys,string $fallbackLabel) use ($catalog): array {
            $out=[];
            foreach($keys as $key){
                $out[$key]=['Label'=>$key==='classic'?$fallbackLabel:(string)($catalog[$key]['Label']??$key),'Config'=>$key==='classic'?[]:(array)($catalog[$key]['Config']??[])];
            }
            return $out;
        };
        $motion=['none'=>['Label'=>'Ingen animation','Config'=>[]]];
        foreach(self::MOTION as $key){
            if($key==='none'){continue;}
            $motion[$key]=['Label'=>(string)($catalog[$key]['Label']??$key),'Config'=>(array)($catalog[$key]['Config']??[])];
        }
        return [
            'Desktop'=>$make(self::DESKTOP,'Klassisk menu'),
            'Mobile'=>$make(self::MOBILE,'Klassisk menu'),
            'Motion'=>$motion,
        ];
    }

    /** @param mixed $value */
    private function clamp($value,int $min,int $max): int
    {
        return max($min,min($max,(int)$value));
    }

    /** @param mixed $value */
    private function text($value,int $max,string $fallback): string
    {
        $text=trim((string)$value);
        if($text===''){return $fallback;}
        return mb_substr($text,0,$max);
    }
}
