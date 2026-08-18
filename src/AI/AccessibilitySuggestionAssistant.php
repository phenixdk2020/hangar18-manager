<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

use Hangar18\UltimateDesigner\Contracts\AiProvider;
use Hangar18\UltimateDesigner\Quality\AccessibilityAnalyzer;

/** UD-107 proposes alt/label text only and leaves every suggestion pending for user approval. */
final class AccessibilitySuggestionAssistant
{
    private AiProvider $provider;
    private AccessibilityAnalyzer $analyzer;
    private SuggestionGuard $guard;

    public function __construct(AiProvider $provider, ?AccessibilityAnalyzer $analyzer = null, ?SuggestionGuard $guard = null)
    {
        $this->provider = $provider;
        $this->analyzer = $analyzer ?? new AccessibilityAnalyzer();
        $this->guard = $guard ?? new SuggestionGuard();
    }

    /** @param array<string,mixed> $state @return list<array<string,mixed>> */
    public function suggest(array $state): array
    {
        $sections = [];
        foreach ((array) ($state['Sections'] ?? []) as $section) {
            if (!is_array($section)) { continue; }
            $key = trim((string) ($section['Key'] ?? ''));
            if ($key !== '') { $sections[$key] = $section; }
        }
        $issues = array_values(array_filter($this->analyzer->analyze($state), static function (array $issue): bool {
            return in_array((string) ($issue['Code'] ?? ''), ['missing-alt','missing-control-label','missing-field-label'], true);
        }));
        if ($issues === []) { return []; }
        $response = $this->provider->complete([
            'Task'=>'accessibility_text_suggestions',
            'Issues'=>$issues,
            'Sections'=>array_values($sections),
            'OutputSchema'=>['Suggestions'=>[['ElementKey'=>'string','Property'=>'AltText|Label','SuggestedValue'=>'string','Reason'=>'string']]],
        ]);
        $proposals = [];
        foreach ((array) ($response['Suggestions'] ?? []) as $suggestion) {
            if (!is_array($suggestion)) { continue; }
            $key = trim((string) ($suggestion['ElementKey'] ?? ''));
            $property = trim((string) ($suggestion['Property'] ?? ''));
            if (!isset($sections[$key]) || !in_array($property,['AltText','Label'],true)) { continue; }
            $after = trim((string) ($suggestion['SuggestedValue'] ?? ''));
            if ($after === '') { continue; }
            $before = (string) ($sections[$key][$property] ?? '');
            if ($before === $after) { continue; }
            $proposals[] = $this->guard->proposal('accessibility',$key,$property,$before,$after,(string) ($suggestion['Reason'] ?? ''));
        }
        return $proposals;
    }
}
