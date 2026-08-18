<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Contracts\AiProvider;

final class FakeAiProvider implements AiProvider
{
    /** @var array<string,array<string,mixed>> */
    private array $responses;
    /** @var list<array<string,mixed>> */
    public array $requests = [];

    /** @param array<string,array<string,mixed>> $responses */
    public function __construct(array $responses)
    {
        $this->responses = $responses;
    }

    public function complete(array $request): array
    {
        $this->requests[] = $request;
        return $this->responses[(string) ($request['Task'] ?? '')] ?? [];
    }
}
