<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

/**
 * Builds an immutable-state cutover preflight. It never performs or exposes cutover.
 */
final class ConversionCutoverPreflightService
{
    private ConversionReadinessGate $gate;
    private ConversionAcceptanceValidator $acceptance;
    private ConversionSourceDriftService $drift;

    public function __construct(
        ?ConversionReadinessGate $gate = null,
        ?ConversionAcceptanceValidator $acceptance = null,
        ?ConversionSourceDriftService $drift = null
    ) {
        $this->gate = $gate ?? new ConversionReadinessGate();
        $this->acceptance = $acceptance ?? new ConversionAcceptanceValidator();
        $this->drift = $drift ?? new ConversionSourceDriftService();
    }

    /**
     * @param array<string,mixed> $currentLegacyState
     * @param array<string,mixed>|null $shadow
     * @param array<string,mixed>|null $acceptanceRecord
     * @param array<string,bool> $manualEvidence
     * @param list<string> $acceptedSlugs
     * @return array<string,mixed>
     */
    public function build(
        string $slug,
        int $pageId,
        string $permalink,
        array $currentLegacyState,
        ?array $shadow,
        ?array $acceptanceRecord,
        array $manualEvidence,
        array $acceptedSlugs,
        string $comparisonSlug
    ): array {
        $slug = strtolower(trim($slug));
        $permalink = trim($permalink);
        $decision = $this->gate->evaluate($slug, $manualEvidence, $acceptedSlugs, $comparisonSlug);
        $blockers = array_values((array) ($decision['Blockers'] ?? []));

        if ($pageId <= 0) {
            $blockers[] = 'wordpress-page-id-missing';
        }
        if ($permalink === '') {
            $blockers[] = 'wordpress-permalink-missing';
        }

        $sourceHash = '';
        $legacyHash = '';
        $acceptanceValid = false;
        $driftFree = false;
        if (!is_array($shadow)) {
            $blockers[] = 'shadow-copy-missing';
        } else {
            $sourceHash = strtolower(trim((string) ($shadow['SourceHash'] ?? ''));
            $drift = $this->drift->evaluate($shadow, $currentLegacyState);
            $legacyHash = (string) ($drift['CurrentLegacyHash'] ?? '');
            $driftFree = !empty($drift['Matches']);
            foreach ((array) ($drift['Blockers'] ?? []) as $blocker) {
                $blockers[] = (string) $blocker;
            }

            $acceptanceValid = $this->acceptance->isAccepted($acceptanceRecord, $sourceHash);
            if (!$acceptanceValid) {
                foreach ($this->acceptance->blockers($acceptanceRecord, $sourceHash) as $blocker) {
                    $blockers[] = $blocker;
                }
            }
        }

        $blockers = array_values(array_unique($blockers));
        sort($blockers, SORT_STRING);
        return [
            'SchemaVersion' => '1.0',
            'Mode' => 'cutover-preflight-only',
            'Slug' => $slug,
            'PageId' => max(0, $pageId),
            'Permalink' => $permalink,
            'ShadowSourceHash' => $sourceHash,
            'CurrentLegacyHash' => $legacyHash,
            'ManualEvidenceComplete' => !empty($decision['ManualEvidenceComplete']),
            'AcceptanceValid' => $acceptanceValid,
            'SourceDriftFree' => $driftFree,
            'EligibleForFutureCutover' => $blockers === [],
            'Blockers' => $blockers,
            'Executable' => false,
            'PublicMutationAvailable' => false,
        ];
    }
}
