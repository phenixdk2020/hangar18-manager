<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

/** Compares two decision-packet snapshots without mutating either snapshot. */
final class ConversionDecisionPacketDiffService
{
    /** @param array<string,mixed> $before @param array<string,mixed> $after @return array<string,mixed> */
    public function compare(array $before, array $after): array
    {
        $beforeStages = $this->indexStages($before);
        $afterStages = $this->indexStages($after);
        $slugs = array_values(array_unique(array_merge(array_keys($beforeStages), array_keys($afterStages))));
        sort($slugs, SORT_STRING);

        $changes = [];
        foreach ($slugs as $slug) {
            $left = $beforeStages[$slug] ?? null;
            $right = $afterStages[$slug] ?? null;
            if ($left === null) {
                $changes[] = ['Slug'=>$slug,'Change'=>'stage-added','Before'=>null,'After'=>$this->summary($right)];
                continue;
            }
            if ($right === null) {
                $changes[] = ['Slug'=>$slug,'Change'=>'stage-removed','Before'=>$this->summary($left),'After'=>null];
                continue;
            }
            $leftSummary = $this->summary($left);
            $rightSummary = $this->summary($right);
            if ($leftSummary !== $rightSummary) {
                $changes[] = ['Slug'=>$slug,'Change'=>'stage-changed','Before'=>$leftSummary,'After'=>$rightSummary];
            }
        }

        $comparisonChanged = (string)($before['ComparisonSlug']??'') !== (string)($after['ComparisonSlug']??'');
        $manualChanged = !empty($before['ManualEvidenceComplete']) !== !empty($after['ManualEvidenceComplete']);
        $acceptedBefore = $this->normalizeList((array)($before['AcceptedSlugs']??[]));
        $acceptedAfter = $this->normalizeList((array)($after['AcceptedSlugs']??[]));

        return [
            'SchemaVersion'=>'1.0',
            'Mode'=>'decision-packet-diff-only',
            'Changed'=>$comparisonChanged || $manualChanged || $acceptedBefore !== $acceptedAfter || $changes !== [],
            'ComparisonChanged'=>$comparisonChanged,
            'ManualEvidenceChanged'=>$manualChanged,
            'AcceptedSlugsChanged'=>$acceptedBefore !== $acceptedAfter,
            'BeforeAcceptedSlugs'=>$acceptedBefore,
            'AfterAcceptedSlugs'=>$acceptedAfter,
            'StageChanges'=>$changes,
            'ChangedStageCount'=>count($changes),
            'Executable'=>false,
            'PublicMutationAvailable'=>false,
        ];
    }

    /** @param array<string,mixed> $packet @return array<string,array<string,mixed>> */
    private function indexStages(array $packet): array
    {
        $out=[];
        foreach((array)($packet['Stages']??[]) as $row){
            if(!is_array($row)){continue;}
            $slug=strtolower(trim((string)($row['Slug']??'')));
            if($slug===''){$slug='stage-'.(string)((int)($row['Stage']??0));}
            $out[$slug]=$row;
        }
        ksort($out,SORT_STRING);
        return $out;
    }

    /** @param array<string,mixed> $row @return array<string,mixed> */
    private function summary(array $row): array
    {
        $blockers=$this->normalizeList((array)($row['Blockers']??[]));
        return [
            'Stage'=>(int)($row['Stage']??0),
            'Kind'=>(string)($row['Kind']??''),
            'Exists'=>!empty($row['Exists']),
            'PlanEligible'=>!empty($row['PlanEligible']),
            'PreflightAvailable'=>!empty($row['PreflightAvailable']),
            'EligibleForOperatorReview'=>!empty($row['EligibleForOperatorReview']),
            'Blockers'=>$blockers,
        ];
    }

    /** @param list<mixed> $values @return list<string> */
    private function normalizeList(array $values): array
    {
        $values=array_values(array_unique(array_filter(array_map(static fn($v): string=>strtolower(trim((string)$v)),$values),static fn(string $v): bool=>$v!=='')));
        sort($values,SORT_STRING);
        return $values;
    }
}
