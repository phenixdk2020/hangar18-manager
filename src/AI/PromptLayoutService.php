<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

use Hangar18\UltimateDesigner\Contracts\AiProvider;
use Hangar18\UltimateDesigner\Contracts\SchemaValidator;
use Hangar18\UltimateDesigner\Core\Version;

/** UD-105 AI layout output must pass the normal page schema before preview/insert. */
final class PromptLayoutService
{
    private AiProvider $provider;
    private SchemaValidator $validator;

    public function __construct(AiProvider $provider, SchemaValidator $validator)
    {
        $this->provider = $provider;
        $this->validator = $validator;
    }

    /** @return array{Valid:bool,Errors:list<string>,State:array<string,mixed>,PreviewAllowed:bool,InsertAllowed:bool} */
    public function propose(string $prompt, array $context = []): array
    {
        $response = $this->provider->complete([
            'Task'=>'layout_proposal',
            'Prompt'=>trim($prompt),
            'Context'=>$context,
            'PageSchemaVersion'=>Version::PAGE_SCHEMA,
            'Rule'=>'Return a complete candidate state only; no writes or side effects.',
        ]);
        $state = is_array($response['State'] ?? null) ? $response['State'] : [];
        $errors = $this->validator->validate($state);
        $valid = $errors === [];
        return ['Valid'=>$valid,'Errors'=>$errors,'State'=>$state,'PreviewAllowed'=>$valid,'InsertAllowed'=>$valid];
    }
}
