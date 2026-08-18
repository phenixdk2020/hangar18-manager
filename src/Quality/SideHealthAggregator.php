<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

/** UD-103 score aggregator that always exposes hard failures alongside scores. */
final class SideHealthAggregator
{
    /** @param list<array<string,mixed>> $issues @return array<string,mixed> */
    public function aggregate(array $issues): array
    {
        $areas = ['design'=>100,'responsive'=>100,'accessibility'=>100,'performance'=>100,'seo'=>100];
        $weights = ['critical'=>30,'error'=>12,'warning'=>5,'info'=>1];
        $hard = [];
        foreach ($issues as $issue) {
            if (!is_array($issue)) { continue; }
            $area = strtolower((string) ($issue['Area'] ?? ''));
            $severity = strtolower((string) ($issue['Severity'] ?? 'warning'));
            if (!isset($areas[$area])) { continue; }
            $areas[$area] = max(0, $areas[$area] - ($weights[$severity] ?? 5));
            if (in_array($severity,['critical','error'],true)) { $hard[] = $issue; }
        }
        $overall = (int) round(array_sum($areas) / count($areas));
        usort($issues, static function (array $a, array $b): int {
            $rank = ['critical'=>0,'error'=>1,'warning'=>2,'info'=>3];
            $sa = $rank[strtolower((string) ($a['Severity'] ?? 'warning'))] ?? 2;
            $sb = $rank[strtolower((string) ($b['Severity'] ?? 'warning'))] ?? 2;
            return [$sa,(string) ($a['Area'] ?? ''),(string) ($a['Code'] ?? '')] <=> [$sb,(string) ($b['Area'] ?? ''),(string) ($b['Code'] ?? '')];
        });
        return [
            'Score'=>$overall,
            'Areas'=>[
                'Design'=>$areas['design'],
                'Mobile'=>$areas['responsive'],
                'Accessibility'=>$areas['accessibility'],
                'Performance'=>$areas['performance'],
                'SEO'=>$areas['seo'],
            ],
            'IssueCount'=>count($issues),
            'HardFailureCount'=>count($hard),
            'HardFailures'=>$hard,
            'Issues'=>$issues,
        ];
    }
}
