<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\QA;

/** UD-113..120 proof gate: automated evidence never impersonates required manual/live acceptance. */
final class ReleaseReadiness
{
    /**
     * @param array<string,bool> $automated
     * @param array<string,bool> $manual
     * @return array<string,mixed>
     */
    public function evaluate(array $automated, array $manual): array
    {
        $failedAutomated = [];
        foreach ($automated as $name => $passed) { if (!$passed) { $failedAutomated[] = (string) $name; } }
        $pendingManual = [];
        foreach ($manual as $name => $passed) { if (!$passed) { $pendingManual[] = (string) $name; } }
        sort($failedAutomated,SORT_STRING);
        sort($pendingManual,SORT_STRING);
        return [
            'Ready'=>$failedAutomated === [] && $pendingManual === [],
            'AutomatedPassed'=>count($automated)-count($failedAutomated),
            'AutomatedTotal'=>count($automated),
            'ManualPassed'=>count($manual)-count($pendingManual),
            'ManualTotal'=>count($manual),
            'FailedAutomated'=>$failedAutomated,
            'PendingManual'=>$pendingManual,
        ];
    }

    /** @return array<string,bool> */
    public function requiredManualEvidence(): array
    {
        return [
            'latest-chrome-brand'=>false,
            'latest-edge-brand'=>false,
            'latest-firefox-brand'=>false,
            'latest-safari-brand'=>false,
            'screen-reader-core-flow'=>false,
            'test2-live-site-e2e'=>false,
            'vehicle-event-gallery-visual-regression'=>false,
            'migration-rollback-live-copy'=>false,
        ];
    }
}
