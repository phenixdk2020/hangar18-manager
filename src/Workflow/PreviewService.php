<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Workflow;

use Hangar18\UltimateDesigner\Contracts\StagingRepository;

/** UD-085 read-only preview resolver for working state. */
final class PreviewService
{
    private PreviewTokenService $tokens;
    private StagingRepository $staging;

    public function __construct(PreviewTokenService $tokens, StagingRepository $staging)
    {
        $this->tokens = $tokens;
        $this->staging = $staging;
    }

    /** @return array{resource:string,device:string,expires:int,state:array<string,mixed>}|null */
    public function resolve(string $token): ?array
    {
        $claims = $this->tokens->validate($token);
        if ($claims === null) {
            return null;
        }
        $state = $this->staging->working($claims['resource']);
        if ($state === null) {
            return null;
        }
        return [
            'resource' => $claims['resource'],
            'device' => $claims['device'],
            'expires' => $claims['expires'],
            'state' => $state,
        ];
    }
}
