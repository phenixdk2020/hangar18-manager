<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

use RuntimeException;

/** All AI output remains a proposal until an explicit acceptance call creates a reversible change. */
final class SuggestionGuard
{
    /** @param mixed $before @param mixed $after @return array<string,mixed> */
    public function proposal(string $kind, string $elementKey, string $property, $before, $after, string $reason = ''): array
    {
        if ($after === $before) { throw new RuntimeException('AI proposal does not change the value.'); }
        return [
            'Id'=>'ai-' . substr(hash('sha256',$kind.'|'.$elementKey.'|'.$property.'|'.microtime(true)),0,16),
            'Kind'=>$kind,
            'ElementKey'=>$elementKey,
            'Property'=>$property,
            'Before'=>$before,
            'After'=>$after,
            'Reason'=>mb_substr(trim($reason),0,1000),
            'Status'=>'pending',
            'CreatedUtc'=>gmdate('c'),
        ];
    }

    /** @param array<string,mixed> $proposal @return array<string,mixed> */
    public function accept(array $proposal, bool $confirmed): array
    {
        if (!$confirmed) { throw new RuntimeException('AI suggestion requires explicit user acceptance.'); }
        if (($proposal['Status'] ?? '') !== 'pending') { throw new RuntimeException('Only pending AI suggestions may be accepted.'); }
        $accepted = $proposal;
        $accepted['Status'] = 'accepted';
        $accepted['AcceptedUtc'] = gmdate('c');
        $accepted['Undo'] = [
            'ElementKey'=>(string) ($proposal['ElementKey'] ?? ''),
            'Property'=>(string) ($proposal['Property'] ?? ''),
            'Value'=>$proposal['Before'] ?? null,
        ];
        $accepted['Apply'] = [
            'ElementKey'=>(string) ($proposal['ElementKey'] ?? ''),
            'Property'=>(string) ($proposal['Property'] ?? ''),
            'Value'=>$proposal['After'] ?? null,
        ];
        return $accepted;
    }

    /** @param array<string,mixed> $proposal @return array<string,mixed> */
    public function reject(array $proposal): array
    {
        $proposal['Status'] = 'rejected';
        $proposal['RejectedUtc'] = gmdate('c');
        return $proposal;
    }
}
