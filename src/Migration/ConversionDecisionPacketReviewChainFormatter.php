<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use JsonException;

/** Formats review-chain reports without changing or authorizing them. */
final class ConversionDecisionPacketReviewChainFormatter
{
    /** @param array<string,mixed> $report */
    public function json(array $report): string
    {
        try {
            return json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR) . "\n";
        } catch (JsonException $exception) {
            throw new \RuntimeException('Review-chain report cannot be encoded as JSON.', 0, $exception);
        }
    }

    /** @param array<string,mixed> $report */
    public function markdown(array $report): string
    {
        $lines = [
            '# I10 Review Chain',
            '',
            '- Mode: `' . $this->text((string)($report['Mode'] ?? '')) . '`',
            '- Review chain valid: **' . (!empty($report['ReviewChainValid']) ? 'YES' : 'NO') . '**',
            '- Fresh human review required: **' . (!empty($report['FreshHumanReviewRequired']) ? 'YES' : 'NO') . '**',
            '- Packet mode valid: **' . (!empty($report['PacketModeValid']) ? 'YES' : 'NO') . '**',
            '- Packet safety invariant valid: **' . (!empty($report['PacketSafetyInvariantValid']) ? 'YES' : 'NO') . '**',
            '- Fingerprint valid: **' . (!empty($report['FingerprintValid']) ? 'YES' : 'NO') . '**',
            '- Human review receipt valid: **' . (!empty($report['HumanReviewReceiptValid']) ? 'YES' : 'NO') . '**',
            '- Authorizes cutover: **' . (!empty($report['AuthorizesCutover']) ? 'YES' : 'NO') . '**',
            '- Executable: **' . (!empty($report['Executable']) ? 'YES' : 'NO') . '**',
            '- Public mutation available: **' . (!empty($report['PublicMutationAvailable']) ? 'YES' : 'NO') . '**',
            '',
            '## Blockers',
            '',
        ];

        $blockers = array_values(array_filter(array_map('strval', (array)($report['Blockers'] ?? [])), static fn(string $v): bool => trim($v) !== ''));
        if ($blockers === []) {
            $lines[] = '- None.';
        } else {
            foreach ($blockers as $blocker) {
                $lines[] = '- `' . $this->text($blocker) . '`';
            }
        }

        $lines[] = '';
        $lines[] = '## Reviewable targets';
        $lines[] = '';
        $targets = array_values(array_filter(array_map('strval', (array)($report['ReviewableTargets'] ?? [])), static fn(string $v): bool => trim($v) !== ''));
        if ($targets === []) {
            $lines[] = '- None.';
        } else {
            foreach ($targets as $target) {
                $lines[] = '- `' . $this->text($target) . '`';
            }
        }

        $lines[] = '';
        $lines[] = '> A valid review chain only proves evidence freshness for the reviewed packet. It does not authorize cutover.';
        return implode("\n", $lines) . "\n";
    }

    private function text(string $value): string
    {
        return str_replace(["\r", "\n", '`'], [' ', ' ', "'"], trim($value));
    }
}
