<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

final class ResponsiveAnalyzer
{
    private StateInspector $inspector;

    public function __construct(?StateInspector $inspector = null)
    {
        $this->inspector = $inspector ?? new StateInspector();
    }

    /** @param array<string,mixed> $state @return list<array<string,mixed>> */
    public function analyze(array $state): array
    {
        $issues = [];
        foreach ($this->inspector->sections($state) as $section) {
            $key = $this->inspector->key($section);
            $type = $this->inspector->type($section);
            foreach ([['MobileWidthPx',375,'mobile'],['TabletWidthPx',768,'tablet'],['WidthPx',1440,'desktop']] as $rule) {
                $width = (int) ($section[$rule[0]] ?? 0);
                if ($width > $rule[1]) {
                    $issues[] = QualityIssue::make('responsive','fixed-width-overflow','error','Fast bredde kan give horizontal overflow på '.$rule[2].'.',$key,['property'=>$rule[0],'width'=>$width,'viewport'=>$rule[1]]);
                }
            }
            if (in_array($type,['button','buttons','menu','tabs','accordion'],true)) {
                foreach ([['MobileHeightPx','mobile'],['HeightPx','base'],['MinHeightPx','base']] as $rule) {
                    $height = (int) ($section[$rule[0]] ?? 0);
                    if ($height > 0 && $height < 44) {
                        $issues[] = QualityIssue::make('responsive','small-touch-target','warning','Touch target er under 44 px.',$key,['property'=>$rule[0],'height'=>$height,'breakpoint'=>$rule[1]]);
                        break;
                    }
                }
            }
            foreach ([['MobileFontSizePx','mobile'],['TabletFontSizePx','tablet']] as $rule) {
                $font = (int) ($section[$rule[0]] ?? 0);
                if ($font > 0 && $font < 14) {
                    $issues[] = QualityIssue::make('responsive','small-text','warning','Tekststørrelsen er meget lille på '.$rule[1].'.',$key,['property'=>$rule[0],'fontSize'=>$font]);
                }
            }
            $mobileVisible = $section['MobileVisible'] ?? $section['MobileActive'] ?? null;
            if ($mobileVisible === false && in_array($type,['menu','form','mail_form'],true)) {
                $issues[] = QualityIssue::make('responsive','critical-content-hidden','error','Kritisk navigation/formular er skjult på mobil.',$key);
            }
        }
        return $issues;
    }
}
