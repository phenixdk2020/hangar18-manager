<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

/** UD-100 token/typography/spacing consistency checks. */
final class DesignConsistencyAnalyzer
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
        $spacingValues = [];
        $radiusValues = [];
        foreach ($this->inspector->sections($state) as $section) {
            $key = $this->inspector->key($section);
            foreach (['CustomBackgroundColor'=>'BackgroundToken','CustomTextColor'=>'TextColorToken','CustomHeadingColor'=>'HeadingColorToken','CustomBorderColor'=>'BorderColorToken'] as $custom => $token) {
                $color = trim((string) ($section[$custom] ?? ''));
                if ($color !== '' && trim((string) ($section[$token] ?? '')) === '') {
                    $issues[] = QualityIssue::make('design','off-token-color','warning','Lokal farve bruger ikke et design-token.',$key,['property'=>$custom,'value'=>$color]);
                }
            }
            foreach (['SectionBodyFontFamily','SectionHeadingFontFamily'] as $property) {
                $font = trim((string) ($section[$property] ?? 'Global'));
                if ($font !== '' && strcasecmp($font,'Global') !== 0) {
                    $issues[] = QualityIssue::make('design','local-font-override','info','Elementet bruger en lokal font i stedet for global typography token.',$key,['property'=>$property,'value'=>$font]);
                }
            }
            foreach (['TopSpacingPx','BottomSpacingPx','PaddingTopPx','PaddingRightPx','PaddingBottomPx','PaddingLeftPx','LayoutGapPx'] as $property) {
                if (isset($section[$property]) && is_numeric($section[$property])) { $spacingValues[(string) (float) $section[$property]] = true; }
            }
            foreach (['BorderRadiusPx','RadiusPx'] as $property) {
                if (isset($section[$property]) && is_numeric($section[$property])) { $radiusValues[(string) (float) $section[$property]] = true; }
            }
        }
        if (count($spacingValues) > 8) {
            $issues[] = QualityIssue::make('design','spacing-outliers','warning','Siden bruger mange forskellige spacing-værdier.','',['unique'=>count($spacingValues),'values'=>array_keys($spacingValues)]);
        }
        if (count($radiusValues) > 5) {
            $issues[] = QualityIssue::make('design','radius-outliers','warning','Siden bruger mange forskellige radius-værdier.','',['unique'=>count($radiusValues),'values'=>array_keys($radiusValues)]);
        }
        return $issues;
    }
}
