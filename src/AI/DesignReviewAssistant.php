<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

use Hangar18\UltimateDesigner\Contracts\AiProvider;
use Hangar18\UltimateDesigner\Quality\DesignConsistencyAnalyzer;

/** UD-106 AI review can suggest concrete element/property changes only. */
final class DesignReviewAssistant
{
    private AiProvider $provider;
    private DesignConsistencyAnalyzer $analyzer;
    private SuggestionGuard $guard;

    public function __construct(AiProvider $provider, ?DesignConsistencyAnalyzer $analyzer = null, ?SuggestionGuard $guard = null)
    {
        $this->provider = $provider;
        $this->analyzer = $analyzer ?? new DesignConsistencyAnalyzer();
        $this->guard = $guard ?? new SuggestionGuard();
    }

    /** @param array<string,mixed> $state @return list<array<string,mixed>> */
    public function review(array $state): array
    {
        $sections = [];
        foreach ((array) ($state['Sections'] ?? []) as $section) {
            if (!is_array($section)) { continue; }
            $key = trim((string) ($section['Key'] ?? ''));
            if ($key !== '') { $sections[$key] = $section; }
        }
        $issues = $this->analyzer->analyze($state);
        $response = $this->provider->complete([
            'Task'=>'design_review',
            'Issues'=>$issues,
            'Sections'=>array_values($sections),
            'OutputSchema'=>['Suggestions'=>[['ElementKey'=>'string','Property'=>'string','SuggestedValue'=>'mixed','Reason'=>'string']]],
        ]);
        $proposals = [];
        foreach ((array) ($response['Suggestions'] ?? []) as $suggestion) {
            if (!is_array($suggestion)) { continue; }
            $key = trim((string) ($suggestion['ElementKey'] ?? ''));
            $property = trim((string) ($suggestion['Property'] ?? ''));
            if ($key === '' || $property === '' || !isset($sections[$key]) || !array_key_exists($property,$sections[$key])) { continue; }
            $before = $sections[$key][$property];
            $after = $suggestion['SuggestedValue'] ?? null;
            if ($before === $after) { continue; }
            $proposals[] = $this->guard->proposal('design',$key,$property,$before,$after,(string) ($suggestion['Reason'] ?? ''));
        }
        return $proposals;
    }
}
