<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use Hangar18\UltimateDesigner\QA\ReleaseReadiness;

/**
 * Aggregates the existing plan/readiness/acceptance/preflight chain into one
 * operator-facing decision packet. This service is deliberately report-only:
 * it exposes no activation callback and never performs WordPress/public writes.
 */
final class ConversionDecisionPacketService
{
    private ConversionPlanService $plan;
    private ConversionCutoverPreflightService $preflight;
    private ReleaseReadiness $releaseReadiness;

    public function __construct(
        ?ConversionPlanService $plan = null,
        ?ConversionCutoverPreflightService $preflight = null,
        ?ReleaseReadiness $releaseReadiness = null
    ) {
        $this->plan = $plan ?? new ConversionPlanService();
        $this->preflight = $preflight ?? new ConversionCutoverPreflightService();
        $this->releaseReadiness = $releaseReadiness ?? new ReleaseReadiness();
    }

    /**
     * @param list<array<string,mixed>> $pages
     * @param array<string,bool> $manualEvidence
     * @param list<string> $acceptedSlugs
     * @param array<string,array<string,mixed>> $targetInputs keyed by slug
     * @return array<string,mixed>
     */
    public function build(
        array $pages,
        array $manualEvidence,
        array $acceptedSlugs,
        array $targetInputs
    ): array {
        $normalizedAccepted = array_values(array_unique(array_filter(
            array_map(static fn($v): string => strtolower(trim((string) $v)), $acceptedSlugs),
            static fn(string $v): bool => $v !== ''
        )));
        sort($normalizedAccepted, SORT_STRING);

        $normalizedInputs = [];
        foreach ($targetInputs as $inputSlug => $input) {
            if (!is_array($input)) {
                continue;
            }
            $inputSlug = strtolower(trim((string) $inputSlug));
            if ($inputSlug === '') {
                continue;
            }
            $normalizedInputs[$inputSlug] = $input;
        }
        ksort($normalizedInputs, SORT_STRING);

        $plan = $this->plan->plan($pages, $manualEvidence, $normalizedAccepted);
        $comparisonSlug = strtolower(trim((string) ($plan['ComparisonSlug'] ?? '')));
        $rows = [];
        $reviewable = [];
        $blocked = [];
        $requiredManualEvidence = array_keys($this->releaseReadiness->requiredManualEvidence());
        $manualEvidenceComplete = !array_filter(
            $requiredManualEvidence,
            static fn(string $gate): bool => empty($manualEvidence[$gate])
        );

        foreach ((array) ($plan['Stages'] ?? []) as $stage) {
            if (!is_array($stage)) {
                continue;
            }
            $slug = strtolower(trim((string) ($stage['Slug'] ?? '')));
            $kind = (string) ($stage['Kind'] ?? '');
            $stageBlockers = array_values(array_unique(array_map('strval', (array) ($stage['Blockers'] ?? []))));
            $input = $slug !== '' && isset($normalizedInputs[$slug])
                ? $normalizedInputs[$slug]
                : null;
            $preflight = null;

            if ($slug === '') {
                $stageBlockers[] = 'decision-target-missing';
            } elseif ($input === null) {
                $stageBlockers[] = 'decision-input-missing';
            } else {
                $preflight = $this->preflight->build(
                    $slug,
                    (int) ($input['PageId'] ?? 0),
                    (string) ($input['Permalink'] ?? ''),
                    is_array($input['CurrentLegacyState'] ?? null) ? $input['CurrentLegacyState'] : [],
                    is_array($input['Shadow'] ?? null) ? $input['Shadow'] : null,
                    is_array($input['AcceptanceRecord'] ?? null) ? $input['AcceptanceRecord'] : null,
                    $manualEvidence,
                    $normalizedAccepted,
                    $comparisonSlug
                );
                foreach ((array) ($preflight['Blockers'] ?? []) as $blocker) {
                    $stageBlockers[] = (string) $blocker;
                }
                if (!empty($preflight['Executable']) || !empty($preflight['PublicMutationAvailable'])) {
                    $stageBlockers[] = 'non-executable-invariant-violated';
                }
            }

            $stageBlockers = array_values(array_unique(array_filter($stageBlockers, static fn(string $v): bool => $v !== '')));
            sort($stageBlockers, SORT_STRING);
            $eligible = $stageBlockers === [] && is_array($preflight) && !empty($preflight['EligibleForFutureCutover']);

            $row = [
                'Stage' => (int) ($stage['Stage'] ?? 0),
                'Kind' => $kind,
                'Slug' => $slug,
                'Title' => (string) ($stage['Title'] ?? ''),
                'Exists' => !empty($stage['Exists']),
                'PlanEligible' => !empty($stage['EligibleForFutureCutover']),
                'PreflightAvailable' => is_array($preflight),
                'EligibleForOperatorReview' => $eligible,
                'Blockers' => $stageBlockers,
                'Preflight' => $preflight,
            ];
            if ($eligible) {
                $reviewable[] = $slug;
            } else {
                $blocked[$slug !== '' ? $slug : 'stage-' . (string) $row['Stage']] = $stageBlockers;
            }
            $rows[] = $row;
        }

        return [
            'SchemaVersion' => '1.0',
            'Mode' => 'decision-packet-only',
            'ComparisonSlug' => $comparisonSlug,
            'ManualEvidenceComplete' => $manualEvidenceComplete,
            'AcceptedSlugs' => $normalizedAccepted,
            'Stages' => $rows,
            'ReviewableTargets' => $reviewable,
            'BlockedTargets' => $blocked,
            'Executable' => false,
            'PublicMutationAvailable' => false,
        ];
    }
}
