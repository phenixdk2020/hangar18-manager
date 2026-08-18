<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

/** UD-098 static accessibility checks with element references. */
final class AccessibilityAnalyzer
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
        $previousHeading = 0;
        foreach ($this->inspector->sections($state) as $section) {
            $key = $this->inspector->key($section);
            $type = $this->inspector->type($section);
            $level = $this->inspector->headingLevel($section);
            if ($level > 0) {
                if ($previousHeading > 0 && $level > $previousHeading + 1) {
                    $issues[] = QualityIssue::make('accessibility','heading-order','error','Overskriftsniveau springer fra H'.$previousHeading.' til H'.$level.'.',$key,['from'=>$previousHeading,'to'=>$level]);
                }
                $previousHeading = $level;
            }

            if (in_array($type,['image','text_image'],true) && empty($section['Decorative'])) {
                $alt = trim((string) ($section['AltText'] ?? $section['ImageAlt'] ?? $section['Alt'] ?? ''));
                if ($alt === '') {
                    $issues[] = QualityIssue::make('accessibility','missing-alt','error','Billedet mangler alternativ tekst.',$key);
                }
            }

            if (in_array($type,['button','buttons'],true)) {
                $label = trim((string) ($section['Label'] ?? $section['Button1Label'] ?? $section['Title'] ?? ''));
                if ($label === '') {
                    $issues[] = QualityIssue::make('accessibility','missing-control-label','error','Interaktiv kontrol mangler synlig/tilgængelig tekst.',$key);
                }
            }

            if (($section['FocusVisible'] ?? null) === false || strtolower((string) ($section['FocusOutline'] ?? '')) === 'none') {
                if (in_array($type,['button','buttons','menu','tabs','accordion','form','mail_form'],true)) {
                    $issues[] = QualityIssue::make('accessibility','focus-disabled','critical','Fokusmarkering er eksplicit deaktiveret på en interaktiv kontrol.',$key);
                }
            }

            foreach ((array) ($section['Fields'] ?? []) as $index => $field) {
                if (!is_array($field)) { continue; }
                $fieldKey = $key . ':field:' . $index;
                $label = trim((string) ($field['Label'] ?? ''));
                $aria = trim((string) ($field['AriaLabel'] ?? ''));
                if ($label === '' && $aria === '') {
                    $issues[] = QualityIssue::make('accessibility','missing-field-label','error','Formularfelt mangler label/aria-label.',$fieldKey);
                }
            }

            $fg = (string) ($section['CustomTextColor'] ?? '');
            $bg = (string) ($section['CustomBackgroundColor'] ?? $section['BackgroundColor'] ?? '');
            $ratio = $this->inspector->contrastRatio($fg,$bg);
            if ($ratio !== null && $ratio < 4.5) {
                $issues[] = QualityIssue::make('accessibility','low-contrast','error','Tekstkontrast er under 4.5:1.',$key,['ratio'=>round($ratio,2),'foreground'=>$fg,'background'=>$bg]);
            }
        }
        return $issues;
    }
}
