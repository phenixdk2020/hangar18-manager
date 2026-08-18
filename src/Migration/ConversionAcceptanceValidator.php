<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use RuntimeException;

/**
 * Human-only acceptance for an I10 shadow copy.
 * The caller cannot set AcceptedForSequence directly; it is derived from evidence.
 */
final class ConversionAcceptanceValidator
{
    private ConversionAcceptanceChecklist $checklist;

    public function __construct(?ConversionAcceptanceChecklist $checklist = null)
    {
        $this->checklist = $checklist ?? new ConversionAcceptanceChecklist();
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function normalize(string $slug, string $sourceHash, array $raw, int $userId): array
    {
        $slug = strtolower(trim($slug));
        $sourceHash = strtolower(trim($sourceHash));
        if ($slug === '' || strlen($slug) > 200) {
            throw new RuntimeException('Conversion acceptance slug is invalid.');
        }
        if (!preg_match('/^[a-f0-9]{64}$/', $sourceHash)) {
            throw new RuntimeException('Conversion acceptance requires the current 64-character source hash.');
        }

        $checks = $this->checklist->emptyStatus();
        $rawChecks = is_array($raw['Checks'] ?? null) ? $raw['Checks'] : [];
        foreach ($checks as $key => $unused) {
            $checks[$key] = !empty($rawChecks[$key]);
        }

        $environment = mb_substr(trim((string) ($raw['Environment'] ?? '')), 0, 240);
        $evidenceRef = mb_substr(trim((string) ($raw['EvidenceRef'] ?? '')), 0, 700);
        $notes = mb_substr(trim((string) ($raw['Notes'] ?? '')), 0, 4000);
        $confirmed = !empty($raw['ConfirmedManual']);
        $allChecksPassed = !in_array(false, array_values($checks), true);
        $accepted = $allChecksPassed && $confirmed && $environment !== '' && $evidenceRef !== '';

        return [
            'SchemaVersion' => '1.0',
            'Slug' => $slug,
            'SourceHash' => $sourceHash,
            'Checks' => $checks,
            'Environment' => $environment,
            'EvidenceRef' => $evidenceRef,
            'Notes' => $notes,
            'ConfirmedManual' => $confirmed,
            'AcceptedForSequence' => $accepted,
            'UserId' => max(0, $userId),
            'CapturedUtc' => gmdate('c'),
        ];
    }

    /** @param array<string,mixed>|null $record */
    public function isAccepted(?array $record, string $currentSourceHash): bool
    {
        if (!is_array($record)) {
            return false;
        }
        $currentSourceHash = strtolower(trim($currentSourceHash));
        if ($currentSourceHash === '' || !hash_equals((string) ($record['SourceHash'] ?? ''), $currentSourceHash)) {
            return false;
        }
        if (empty($record['ConfirmedManual']) || empty($record['AcceptedForSequence'])) {
            return false;
        }
        $checks = is_array($record['Checks'] ?? null) ? $record['Checks'] : [];
        foreach (array_keys($this->checklist->required()) as $key) {
            if (empty($checks[$key])) {
                return false;
            }
        }
        return trim((string) ($record['Environment'] ?? '')) !== '' && trim((string) ($record['EvidenceRef'] ?? '')) !== '';
    }

    /** @param array<string,mixed>|null $record @return list<string> */
    public function blockers(?array $record, string $currentSourceHash): array
    {
        if (!is_array($record)) {
            return ['acceptance-evidence-missing'];
        }
        $blockers = [];
        if (!hash_equals((string) ($record['SourceHash'] ?? ''), strtolower(trim($currentSourceHash)))) {
            $blockers[] = 'acceptance-source-hash-stale';
        }
        $checks = is_array($record['Checks'] ?? null) ? $record['Checks'] : [];
        foreach (array_keys($this->checklist->required()) as $key) {
            if (empty($checks[$key])) {
                $blockers[] = 'acceptance-check:' . $key;
            }
        }
        if (empty($record['ConfirmedManual'])) {
            $blockers[] = 'acceptance-manual-confirmation-missing';
        }
        if (trim((string) ($record['Environment'] ?? '')) === '') {
            $blockers[] = 'acceptance-environment-missing';
        }
        if (trim((string) ($record['EvidenceRef'] ?? '')) === '') {
            $blockers[] = 'acceptance-evidence-ref-missing';
        }
        $blockers = array_values(array_unique($blockers));
        sort($blockers, SORT_STRING);
        return $blockers;
    }
}
