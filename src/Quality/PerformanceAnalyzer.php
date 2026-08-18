<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

/** UD-102 static performance analyzer for assets, DOM depth and feature modules. */
final class PerformanceAnalyzer
{
    private StateInspector $inspector;

    public function __construct(?StateInspector $inspector = null)
    {
        $this->inspector = $inspector ?? new StateInspector();
    }

    /**
     * @param array<string,mixed> $state
     * @param array<int,int> $assetBytes native media ID => bytes
     * @return list<array<string,mixed>>
     */
    public function analyze(array $state, array $assetBytes = []): array
    {
        $issues = [];
        $sections = $this->inspector->sections($state);
        if (count($sections) > 150) {
            $issues[] = QualityIssue::make('performance','large-dom','warning','Siden har mange elementer og kan give en tung DOM.','',['elements'=>count($sections)]);
        }
        $depths = $this->inspector->depths($state);
        $maxDepth = $depths ? max($depths) : 0;
        if ($maxDepth > 8) {
            $issues[] = QualityIssue::make('performance','deep-dom','warning','Layout-hierarkiet er dybt og bør forenkles.','',['depth'=>$maxDepth]);
        }

        $usedMedia = [];
        $usedTypes = [];
        foreach ($sections as $section) {
            $type = $this->inspector->type($section);
            if ($type !== '') { $usedTypes[$type] = true; }
            foreach (['MediaId','ImageMediaId','BackgroundMediaId','MainMediaId'] as $property) {
                $mediaId = (int) ($section[$property] ?? 0);
                if ($mediaId > 0) { $usedMedia[$mediaId] = true; }
            }
        }
        foreach (array_keys($usedMedia) as $mediaId) {
            $bytes = max(0,(int) ($assetBytes[$mediaId] ?? 0));
            if ($bytes > 1500000) {
                $issues[] = QualityIssue::make('performance','oversized-image','warning','Et anvendt billede er større end 1,5 MB.','',['mediaId'=>$mediaId,'bytes'=>$bytes]);
            }
        }

        $moduleTypes = [
            'carousel'=>['carousel'],
            'tabs'=>['tabs'],
            'accordion'=>['accordion'],
            'forms'=>['form','mail_form'],
            'popup'=>['popup','modal'],
            'menu'=>['menu'],
        ];
        foreach ((array) ($state['LoadedModules'] ?? []) as $module) {
            $module = strtolower(trim((string) $module));
            if (!isset($moduleTypes[$module])) { continue; }
            $needed = false;
            foreach ($moduleTypes[$module] as $type) { if (isset($usedTypes[$type])) { $needed = true; break; } }
            if (!$needed) {
                $issues[] = QualityIssue::make('performance','unused-module','warning','Frontend-modul indlæses uden et tilsvarende element.','',['module'=>$module]);
            }
        }
        return $issues;
    }
}
