<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

use Hangar18\UltimateDesigner\Contracts\AiProvider;
use RuntimeException;

/** UD-104 proposes text changes but cannot mutate content. */
final class TextAssistant
{
    private AiProvider $provider;
    private SuggestionGuard $guard;

    public function __construct(AiProvider $provider, ?SuggestionGuard $guard = null)
    {
        $this->provider = $provider;
        $this->guard = $guard ?? new SuggestionGuard();
    }

    /** @return array<string,mixed> */
    public function suggest(string $elementKey, string $property, string $currentText, string $instruction, array $context = []): array
    {
        $instruction = trim($instruction);
        if ($instruction === '') { throw new RuntimeException('AI text instruction is required.'); }
        $response = $this->provider->complete([
            'Task'=>'text_suggestion',
            'Instruction'=>$instruction,
            'CurrentText'=>$currentText,
            'Context'=>$context,
            'OutputSchema'=>['SuggestedText'=>'string','Reason'=>'string'],
        ]);
        $text = trim((string) ($response['SuggestedText'] ?? ''));
        if ($text === '') { throw new RuntimeException('AI provider did not return SuggestedText.'); }
        return $this->guard->proposal('text',$elementKey,$property,$currentText,$text,(string) ($response['Reason'] ?? ''));
    }
}
