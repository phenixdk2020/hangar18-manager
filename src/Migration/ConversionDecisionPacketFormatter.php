<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use JsonException;

/** Formats a decision packet for evidence/operator review without mutation. */
final class ConversionDecisionPacketFormatter
{
    /** @param array<string,mixed> $packet */
    public function json(array $packet): string
    {
        try {
            return json_encode($packet, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR) . "\n";
        } catch (JsonException $exception) {
            throw new \RuntimeException('Decision packet cannot be encoded as JSON.', 0, $exception);
        }
    }

    /** @param array<string,mixed> $packet */
    public function markdown(array $packet): string
    {
        $lines = [
            '# I10 Conversion Decision Packet',
            '',
            '- Mode: `' . $this->cell((string) ($packet['Mode'] ?? '')) . '`',
            '- Comparison: `' . $this->cell((string) ($packet['ComparisonSlug'] ?? '')) . '`',
            '- Manual evidence complete: **' . (!empty($packet['ManualEvidenceComplete']) ? 'YES' : 'NO') . '**',
            '- Executable: **' . (!empty($packet['Executable']) ? 'YES' : 'NO') . '**',
            '- Public mutation available: **' . (!empty($packet['PublicMutationAvailable']) ? 'YES' : 'NO') . '**',
            '',
            '| Stage | Kind | Slug | Plan | Preflight | Operator review | Blockers |',
            '|---:|---|---|---|---|---|---|',
        ];

        foreach ((array) ($packet['Stages'] ?? []) as $row) {
            if (!is_array($row)) {
                continue;
            }
            $blockers = array_values(array_filter(array_map('strval', (array) ($row['Blockers'] ?? [])), static fn(string $v): bool => $v !== ''));
            $lines[] = sprintf(
                '| %d | %s | `%s` | %s | %s | %s | %s |',
                (int) ($row['Stage'] ?? 0),
                $this->cell((string) ($row['Kind'] ?? '')),
                $this->cell((string) ($row['Slug'] ?? '')),
                !empty($row['PlanEligible']) ? 'eligible' : 'blocked',
                !empty($row['PreflightAvailable']) ? 'available' : 'missing',
                !empty($row['EligibleForOperatorReview']) ? '**YES**' : 'NO',
                $blockers === [] ? '-' : $this->cell(implode(', ', $blockers))
            );
        }

        $reviewable = array_values(array_filter(array_map('strval', (array) ($packet['ReviewableTargets'] ?? [])), static fn(string $v): bool => $v !== ''));
        $lines[] = '';
        $lines[] = '## Reviewable targets';
        $lines[] = '';
        if ($reviewable === []) {
            $lines[] = '- None.';
        } else {
            foreach ($reviewable as $slug) {
                $lines[] = '- `' . $this->cell($slug) . '`';
            }
        }

        $lines[] = '';
        $lines[] = '> This packet is review-only. It does not authorize or execute public cutover.';
        return implode("\n", $lines) . "\n";
    }

    private function cell(string $value): string
    {
        return str_replace(["\r", "\n", '|'], [' ', ' ', '\\|'], trim($value));
    }
}
